#!/usr/bin/env python3
"""LLM 路由管理器 — 多模型支持与自动降级。

支持:
    - CLI 后端: claude, kimi
    - HTTP API 后端: OpenAI 兼容格式 (MiniMax, DeepSeek, Groq, Azure 等)

配置优先级（高优先覆盖低优先）:
    1. 环境变量（os.environ）
    2. 项目根目录 .env 文件
    3. memory/llm-config.json
    4. 自动检测本地 CLI

用法:
    from llm_router import router
    response = router.call_llm(system_prompt, messages)

    # 查看状态
    status = router.get_status()
"""

import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()
_CONFIG_PATH = _PROJECT_ROOT / "memory" / "llm-config.json"
_ENV_PATH = _PROJECT_ROOT / ".env"


# ---------------------------------------------------------------------------
# 配置加载
# ---------------------------------------------------------------------------

def _load_env_file(path: Path) -> Dict[str, str]:
    """简单解析 .env 文件（不需要 python-dotenv）。"""
    result: Dict[str, str] = {}
    if not path.exists():
        return result
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                result[k.strip()] = v.strip().strip('"').strip("'")
    return result


def _detect_cli_providers() -> List[Dict[str, Any]]:
    """检测本地可用的 CLI 工具。"""
    providers: List[Dict[str, Any]] = []
    for name, cmd in [("kimi", "kimi"), ("claude", "claude")]:
        if shutil.which(cmd):
            providers.append({
                "name": name,
                "type": "cli",
                "priority": 1 if name == "kimi" else 2,
            })
    return providers


def _build_config() -> Dict[str, Any]:
    """构建运行时配置。"""
    config: Dict[str, Any] = {
        "providers": [],
        "strategy": "priority",
        "timeout": 60,
        "retry": 1,
    }

    # 1. 读取配置文件
    if _CONFIG_PATH.exists():
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                file_cfg = json.load(f)
            config.update(file_cfg)
        except Exception:
            pass

    # 2. 读取 .env 文件
    env_vars = _load_env_file(_ENV_PATH)
    env_vars.update(os.environ)

    # 3. 如果环境变量中有 MiniMax 配置，自动添加
    if env_vars.get("MINIMAX_API_KEY"):
        # 避免重复添加
        has_minimax = any(p.get("name") == "minimax" for p in config["providers"])
        if not has_minimax:
            config["providers"].append({
                "name": "minimax",
                "type": "api",
                "base_url": env_vars.get("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1"),
                "api_key": env_vars["MINIMAX_API_KEY"],
                "model": env_vars.get("MINIMAX_MODEL", "MiniMax-M2.7"),
                "priority": 1,
            })

    # 4. 如果环境变量中有其他 OpenAI 兼容配置，自动添加
    for prefix in ["OPENAI", "DEEPSEEK", "GROQ", "AZURE"]:
        key = env_vars.get(f"{prefix}_API_KEY")
        if key:
            name = prefix.lower()
            has_it = any(p.get("name") == name for p in config["providers"])
            if not has_it:
                config["providers"].append({
                    "name": name,
                    "type": "api",
                    "base_url": env_vars.get(f"{prefix}_BASE_URL", ""),
                    "api_key": key,
                    "model": env_vars.get(f"{prefix}_MODEL", ""),
                    "priority": env_vars.get(f"{prefix}_PRIORITY", "2"),
                })

    # 5. 如果没有配置任何 API provider，自动检测 CLI
    api_providers = [p for p in config["providers"] if p.get("type") == "api"]
    if not api_providers:
        cli_detected = _detect_cli_providers()
        # 合并，避免重复
        existing_names = {p["name"] for p in config["providers"]}
        for p in cli_detected:
            if p["name"] not in existing_names:
                config["providers"].append(p)

    return config


# ---------------------------------------------------------------------------
# Provider 实现
# ---------------------------------------------------------------------------

class LLMProvider:
    """单个 LLM 提供者。"""

    def __init__(self, config: Dict[str, Any]):
        self.name = config["name"]
        self.type = config["type"]  # "cli" or "api"
        self.priority = int(config.get("priority", 99))
        self.config = config
        self.failure_count = 0
        self.last_error = ""

    def __repr__(self) -> str:
        return f"LLMProvider({self.name}/{self.type})"

    def call(self, system_prompt: str, messages: List[Dict[str, str]], timeout: int = 60) -> str:
        """调用 LLM 获取回复。"""
        if self.type == "cli":
            return self._call_cli(system_prompt, messages, timeout)
        elif self.type == "api":
            return self._call_api(system_prompt, messages, timeout)
        raise ValueError(f"Unknown provider type: {self.type}")

    # ---- CLI 调用 ----

    def _call_cli(self, system_prompt: str, messages: List[Dict[str, str]], timeout: int) -> str:
        if self.name == "kimi":
            return self._call_kimi(system_prompt, messages, timeout)
        elif self.name == "claude":
            return self._call_claude(system_prompt, messages, timeout)
        raise ValueError(f"Unknown CLI provider: {self.name}")

    def _call_kimi(self, system_prompt: str, messages: List[Dict[str, str]], timeout: int) -> str:
        """调用 kimi CLI。"""
        # 构建 kimi 需要的输入格式
        prompt_parts = [system_prompt]
        for m in messages:
            role_label = "用户" if m["role"] == "user" else "助手"
            prompt_parts.append(f"{role_label}: {m['content']}")
        prompt_text = "\n\n".join(prompt_parts)

        result = subprocess.run(
            ["kimi", "-c", prompt_text],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(f"kimi CLI 错误: {result.stderr}")
        # 清理 kimi 的输出（转义序列等）
        return self._clean_kimi_output(result.stdout)

    def _call_claude(self, system_prompt: str, messages: List[Dict[str, str]], timeout: int) -> str:
        """调用 claude CLI。"""
        # claude CLI 支持多轮对话格式
        cmd = ["claude", "-p", "--no-stream"]
        # 构建对话文本
        prompt_parts = [f"System: {system_prompt}"]
        for m in messages:
            role_label = "Human" if m["role"] == "user" else "Assistant"
            prompt_parts.append(f"{role_label}: {m['content']}")
        prompt_parts.append("Assistant:")
        prompt_text = "\n\n".join(prompt_parts)

        result = subprocess.run(
            cmd + [prompt_text],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(f"claude CLI 错误: {result.stderr}")
        return result.stdout.strip()

    @staticmethod
    def _clean_kimi_output(text: str) -> str:
        """清理 kimi CLI 输出中的转义序列。"""
        import re
        text = re.sub(r"\x1b\[[0-9;]*m", "", text)
        text = re.sub(r"\x1b\]0;.*?\x07", "", text)
        return text.strip()

    # ---- API 调用 ----

    def _call_api(self, system_prompt: str, messages: List[Dict[str, str]], timeout: int) -> str:
        """调用 OpenAI 兼容 API。"""
        base_url = self.config.get("base_url", "").rstrip("/")
        api_key = self.config.get("api_key", "")
        model = self.config.get("model", "")

        if not all([base_url, api_key, model]):
            raise ValueError(f"Provider {self.name} 缺少必要配置 (base_url/api_key/model)")

        url = f"{base_url}/chat/completions"

        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "temperature": 0.7,
            "max_tokens": 4096,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            raise RuntimeError(f"API HTTP {e.code}: {body}")


# ---------------------------------------------------------------------------
# 路由管理器
# ---------------------------------------------------------------------------

class LLMRouter:
    """LLM 路由管理器 — 按策略选择 Provider，自动降级。"""

    def __init__(self):
        self.config = _build_config()
        self.providers = [LLMProvider(p) for p in self.config.get("providers", [])]
        self._round_robin_idx = 0

    def call_llm(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        """调用 LLM，按策略自动选择 Provider，失败时自动降级。

        Args:
            system_prompt: 系统提示词
            messages: 消息列表 [{role, content}, ...]

        Returns:
            LLM 生成的文本

        Raises:
            RuntimeError: 所有 Provider 均失败
        """
        strategy = self.config.get("strategy", "priority")
        timeout = int(self.config.get("timeout", 60))
        retry = int(self.config.get("retry", 1))

        available = [p for p in self.providers if self._is_available(p)]
        if not available:
            raise RuntimeError("✗ 没有可用的 LLM Provider。请检查配置或安装 CLI 工具。")

        if strategy == "priority":
            available.sort(key=lambda p: p.priority)
        elif strategy == "round_robin":
            idx = self._round_robin_idx % len(available)
            available = available[idx:] + available[:idx]
            self._round_robin_idx = (self._round_robin_idx + 1) % len(available)

        last_error = ""
        for provider in available:
            for attempt in range(retry + 1):
                try:
                    result = provider.call(system_prompt, messages, timeout)
                    provider.failure_count = 0
                    return result
                except urllib.error.HTTPError as e:
                    provider.failure_count += 1
                    if e.code == 429:
                        last_error = f"⚠ {provider.name} 限流 (429)，尝试下一个…"
                        print(last_error, file=sys.stderr)
                    elif e.code >= 500:
                        last_error = f"⚠ {provider.name} 服务端错误 ({e.code})，尝试下一个…"
                        print(last_error, file=sys.stderr)
                    else:
                        last_error = f"✗ {provider.name} HTTP {e.code}"
                except subprocess.TimeoutExpired:
                    provider.failure_count += 1
                    last_error = f"⚠ {provider.name} 超时，尝试下一个…"
                    print(last_error, file=sys.stderr)
                except Exception as e:
                    provider.failure_count += 1
                    last_error = f"✗ {provider.name}: {e}"

        raise RuntimeError(f"所有 Provider 均失败。最后错误: {last_error}")

    def _is_available(self, provider: LLMProvider) -> bool:
        """检查 Provider 是否可用。"""
        if provider.type == "cli":
            return shutil.which(provider.name) is not None
        elif provider.type == "api":
            return bool(provider.config.get("api_key") and provider.config.get("base_url"))
        return False

    def get_status(self) -> List[Dict[str, Any]]:
        """返回所有 Provider 的状态。"""
        return [
            {
                "name": p.name,
                "type": p.type,
                "priority": p.priority,
                "available": self._is_available(p),
                "failure_count": p.failure_count,
                "model": p.config.get("model", "") if p.type == "api" else "",
            }
            for p in self.providers
        ]

    def reload_config(self) -> None:
        """重新加载配置（用于动态更新）。"""
        self.config = _build_config()
        self.providers = [LLMProvider(p) for p in self.config.get("providers", [])]


# ---------------------------------------------------------------------------
# 全局实例
# ---------------------------------------------------------------------------
router = LLMRouter()

# 便捷的模块级函数
call_llm = router.call_llm
get_status = router.get_status


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="LLM 路由管理器")
    parser.add_argument("--status", action="store_true", help="显示 Provider 状态")
    parser.add_argument("--test", metavar="PROVIDER", help="测试指定 Provider")
    args = parser.parse_args(argv)

    if args.status:
        print("=== LLM Provider 状态 ===")
        for s in router.get_status():
            avail = "✓" if s["available"] else "✗"
            print(f"  {avail} {s['name']:12} {s['type']:6} 优先:{s['priority']:2}  失败:{s['failure_count']}")
        return 0

    if args.test:
        for p in router.providers:
            if p.name == args.test:
                print(f"◐ 测试 {p.name} …")
                try:
                    result = p.call("你是一个测试助手，只回复'测试成功'。", [{"role": "user", "content": "开始测试"}], timeout=30)
                    print(f"✓ 测试通过: {result[:50]}…")
                except Exception as e:
                    print(f"✗ 测试失败: {e}")
                return 0
        print(f"✗ 未找到 Provider: {args.test}")
        return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
