#!/usr/bin/env python3
"""LLM 路由管理器 — 多模型支持与自动降级。

支持:
    - CLI 后端: claude, kimi
    - HTTP API 后端: OpenAI 兼容格式 (MiniMax, Kimi coding plan, DeepSeek, Groq, Azure, GLM 等)

配置优先级（高优先覆盖低优先）:
    1. 环境变量（os.environ）
    2. 项目根目录 .env 文件
    3. memory/llm-config.json
    4. 自动检测本地 CLI

provider 停用（v7.3.82）: .env 设 LLM_DISABLED_PROVIDERS（逗号分隔
    provider 名，如 "kimi,kimi-coding"），命中的 provider 统一不进候选链
    （CLI 检测与 HTTP API 注入一并过滤）。恢复即删该行。

用法:
    from llm_router import router
    response = router.call_llm(system_prompt, messages)

    # 查看状态
    status = router.get_status()
"""

import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import common as _cms

# 统一日志
try:
    from logger import get_logger
    _log = get_logger("llm_router")
except Exception:
    _log = None


# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()
_CONFIG_PATH = _PROJECT_ROOT / "memory" / "llm-config.json"
_ENV_PATH = _PROJECT_ROOT / ".env"
_HERMES_ENV_PATH = Path.home() / ".hermes" / ".env"


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


def _load_hermes_env_key(key: str) -> Optional[str]:
    """从 hermes 的 .env 读取指定 key（作为项目 .env 的兜底）。"""
    hermes_env = _load_env_file(_HERMES_ENV_PATH)
    return hermes_env.get(key)


class RateLimitError(RuntimeError):
    """v7.3.66: API 429 限流专用异常。

    背景：`_call_api` 把 urllib 的 HTTPError 统一包成 RuntimeError，路由层
    的 `except HTTPError` 分支实际取不到 429，只能落入通用异常分支并对同
    provider 重试 retry 次——11-07 18:51 实测同一调用连发两条 429（不同
    request_id）后才降级 kimi。429 是明确的退避信号，同 prompt 立即重试
    不会成功，只会放大限流计数与失败账本。路由层捕获本类型后跳过同
    provider 重试，直接切换下一 provider。
    """

    def __init__(self, message: str, code: int = 429):
        super().__init__(message)
        self.code = code


class ThinkOnlyResponseError(RuntimeError):
    """v7.2.55: 剥离 think 标签后为空的专用异常（v7.2.54 修复的副作用治理）。

    背景：v7.2.54 把该形态从「静默成功」改为显式可降级失败后，路由层
    仍按普通错误在同 provider 上重试 retry 次——同 prompt 同预算必然
    重演，单次调用被放大为 N×(retry+1) 次，且消耗的 token 在失败
    记账中不可见（10 月实测：97 条空成功全部 completion_tokens=4096）。
    路由层捕获本类型后：
      ① 不在同 provider 上重试（直接切换下一 provider）；
      ② 把 usage 并入失败记账，token 消耗可见。
    """

    def __init__(self, message: str, usage: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.usage = usage


def _strip_think_tags(text: str) -> str:
    """过滤掉 LLM 推理标签 <think>...</think> 及其内容。"""
    if not text:
        return text

    # 使用栈处理可能嵌套的 think 标签
    result = []
    i = 0
    depth = 0
    while i < len(text):
        if text[i:].lower().startswith("<think") and (i + 6 >= len(text) or text[i + 6] in " >"):
            # 找到 think 开始标签
            depth += 1
            # 跳过整个开始标签
            end = text.find(">", i)
            i = end + 1 if end != -1 else len(text)
        elif text[i:].lower().startswith("</think>") and depth > 0:
            depth -= 1
            i += 8
        elif depth == 0:
            result.append(text[i])
            i += 1
        else:
            # 在 think 标签内部，跳过
            i += 1

    cleaned = "".join(result)
    # 清理因移除标签产生的多余空行
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


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


# v6.9.4: 任务级 provider 偏好。
# 背景：监管/维护类任务（品味评分、知识萃取、提案检查）与执行类任务
# （撰写、文献调研）对模型的诉求不同——前者重判断与规范遵循，后者重生成
# 与长文产出。通过任务标签让治理类调用优先走 GLM（当前 glm-5.3），
# 执行类维持 MiniMax 主链，实现"一链两用"而不破坏全局降级策略。
# 偏好仅在自动策略（模式 B）下生效：偏好 provider 不可用或调用失败时，
# 照常回落到原优先级链，不会因偏好引入新的失败面。
TASK_PROVIDER_PREFS: Dict[str, Tuple[str, ...]] = {
    # 任务标签 → 优先尝试的 provider 名（按序）
    "governance": ("glm", "glm-fallback"),
    # v6.9.14: 周末输入端知识簇链路（summarize/cluster_distill/
    # topic_match 仲裁）主模型改走 GLM 最新（glm-5.3）。该任务重
    # 判断与结构化输出（知识卡/路由决策），GLM 5.3 规范遵循更稳；
    # 且 MiniMax Token Plan 月末限额期（429）不再阻塞输入端整链。
    # 失败仍回落全局链（minimax → kimi-coding …），无新增失败面。
    "weekend_input": ("glm", "glm-fallback"),
    # v6.9.15: raw→wiki 蒸馏主模型改走 GLM。08-15 实测 MiniMax Token
    # Plan 429 限额期，蒸馏走默认 MiniMax 主链需 429 重试（实测单篇
    # 最长 369s）再降级 glm，350 篇积压按此链路约 26 小时不可行；
    # glm 直连单篇 30-60s。蒸馏为治理类长文生成任务，与 governance
    # 同级。失败仍回落全局链，无新增失败面。
    # v7.3.83: glm-first——用户裁决 2026-11-15（MiniMax 额度掉得快，蒸馏
    # 挪出 M3）。v6.9.73 minimax-first 的依据（glm 蒸馏长 prompt 104s 失败）
    # 已被 glm-5.3 稳定性取代；且 ① 号改造后 glm 跑 kb_distill 请求级关思考
    # （思考 token 不产生），单篇成本低于开推理的 M3。glm 故障仍回落 minimax。
    "kb_distill": ("glm", "minimax"),
    # v7.3.83: 低价值源轻量蒸馏（简报 tier 2 / 剪藏笔记 tier 3）——降档
    # 口径与 kb_distill 一致（kb_distill._is_lite_source 判定），仅输出
    # 预算减半（见 TASK_MAX_TOKENS）。链序随 kb_distill。
    "kb_distill_lite": ("glm", "minimax"),
    # v7.3.86: weekend_output 补注册 glm-first——TASK_MAX_TOKENS 早已给该
    # 标签配了 16384 输出预算，但偏好漏注册，周末输出端任务一直落全局
    # minimax 链（v7.3.82 停 kimi 后 M3 回到链首，整链烧 MiniMax 池）。
    # 不并入 TASKS_DISABLE_THINKING：长文生成类，关思考伤质量（关思考
    # 只留给结构化抽取/格式化类，见上）。
    "weekend_output": ("glm", "glm-fallback"),
}

# v6.9.75: 任务级输出预算——推理模型（reasoning tokens 计入 completion
# 上限）写长文时 4096 不够，按 prefer 标签放宽
# v6.10.9: 补 weekend_input——与 kb_distill_deep 同病：deep_digest 摘要
# core/mechanism 长中文正文 + 推理 token 计入 4096 上限被截断（实测
# 09-13 02:41 "Unterminated string"、06:24 ```json 围栏开头无闭合——
# 尾部截断的两种表现），v6.9.75 只修了 kb_distill_deep 漏了本标签。
TASK_MAX_TOKENS = {
    "kb_distill_deep": 16384,
    "kb_distill_lite": 2048,
    "weekend_input": 16384,
    "weekend_output": 16384,
}
# 评审团（v6.10.46）：hermes MiniMax 每周配额 429 时的降级链。
# v7.3.80: 链序按近 7 天 step_usage 账本实证重排——kimi CLI 对 panel
# 尺寸 prompt（50k+ 字符）14/15 次超时（每次成对白等 2×timeout），
# 摘出 panel 链（见 TASK_PROVIDER_EXCLUDE）；claude 3/3 成功、唯一在
# panel 尺寸稳定产出，提为首选；minimax-fallback（M2.7）3/6 居次；
# glm 0/2（think-only）。minimax（M3）panel 尺寸 12/12 think-only，
# 由 THINK_ONLY 大 prompt 守卫统一规避（见下），不再单独列序。
TASK_PROVIDER_PREFS["panel"] = ("claude", "minimax-fallback", "glm")

# v7.3.80: 任务级 provider 排除清单——对特定任务形态系统性失效（非瞬态
# 故障）的 provider，重排救不了，直接摘出该任务的候选链。仅在自动策略
# （模式 B）下生效；过滤后为空则放弃排除（防御）。
TASK_PROVIDER_EXCLUDE: Dict[str, Tuple[str, ...]] = {
    # kimi CLI（编码 agent）对 panel 尺寸 prompt 近乎必超时（近 7 天
    # panel 14/15 超时，每轮白等 2×PANEL_TIMEOUT）；其它任务不受影响
    # （kb_distill 27/27 成功）。
    "panel": ("kimi",),
}

# v7.3.80: M3 大 prompt think-only 守卫——MiniMax-M3 把生成预算全部耗在
# <think> 思考块、正文为空（ThinkOnlyResponseError）的概率随 prompt 尺寸
# 陡增：近 7 天账本，成功调用 prompt 尺寸 p99=27k 字符、≥40k 字符仅 7 次
# 成功，而 panel 尺寸（50k+ 字符）think-only 12/12。超阈值时在自动策略
# 链中直接跳过下列 provider（仍有后续候选时），免得每次全价烧完 prompt
# 再降级。强制指定（模式 A）不拦——用户显式点名时不剥夺尝试权。
THINK_ONLY_PRONE_PROVIDERS = ("minimax",)
THINK_ONLY_PRONE_MIN_CHARS = 40000

# v7.3.81: think-only 就地升预算重试——首次 think-only 后同 provider 以
# 抬高后的 max_tokens 重试一次（不消耗 retry 额度）。全库证据：214 次
# think-only 失败的 completion_tokens 全部恰为 4096（默认预算被思考
# token 打满、正文为空）。升到 16384 起步（或当前值 ×4 取大者），给
# 思考留出正文空间；上限 32768 防预算失控。
THINK_ONLY_RETRY_MAX_TOKENS = 16384
THINK_ONLY_RETRY_MAX_CAP = 32768

# v7.3.83: 机械任务请求级关思考（用户裁决 2026-11-15 token 治理①）。
# GLM 系（bigmodel）支持请求级 thinking 参数；kb_distill（五要素蒸馏）与
# weekend_input（深读摘要/知识卡）为结构化抽取/格式化任务，关思考后思考
# token 直接不产生（输出预算全给正文），同时根除这两类任务上的 think-only
# 空烧（本周账本：think-only 57 次烧 622k tokens 零产出）。判断类任务
# （governance 评分 / panel 评审 / hermes 优化轮）不动。端点不认该参数时
# 以 HTTP 400 拒绝，_call_api 剥离后重发一次（宁可少省不可断链）。
THINKING_DISABLE_PROVIDERS = ("glm", "glm-fallback")
TASKS_DISABLE_THINKING = ("kb_distill", "kb_distill_lite", "weekend_input")


def _record_llm_call(
    name: str,
    *,
    provider: str = "",
    model: str = "",
    prefer: str = "",
    elapsed_s: float = 0.0,
    success: bool = True,
    prompt_chars: int = 0,
    output_chars: int = 0,
    usage: Optional[Dict[str, Any]] = None,
    error: str = "",
    note: str = "",
) -> None:
    """v6.10.52: 调用计量——把每次路由结果（含 provider 级失败）写入
    step_usage 账本。延迟导入避免循环依赖；记账失败静默（不影响主链路）。
    """
    try:
        import step_usage
        step_usage.record_call(
            "llm_router", name, provider=provider, model=model, prefer=prefer,
            elapsed_s=elapsed_s, success=success, prompt_chars=prompt_chars,
            output_chars=output_chars, usage=usage, error=error, note=note)
    except Exception:
        pass


def _apply_task_preference(
    ordered: List["LLMProvider"], prefer: Optional[str]
) -> List["LLMProvider"]:
    """按任务标签把偏好 provider 按声明顺序全部提到队首（稳定，其余不变）。

    v7.3.80 修复：旧实现循环内首次命中即 return，声明的第 2 个及以后
    偏好永远不会生效（panel 声明 ("kimi","claude","glm")，实际链序是
    kimi → 全局序，claude/glm 的提升被吞掉；账本实测 panel 链为
    kimi → minimax → minimax-fallback → claude）。新语义：全部偏好按
    声明顺序整体提前，其余 provider 保持全局相对顺序。

    Args:
        ordered: 已按全局策略排好序的可用 provider 列表。
        prefer:  任务标签（如 "governance"）；None 或未注册标签原样返回。

    Returns:
        重排后的列表；偏好 provider 均不在列表中时原样返回。
    """
    pref_names = TASK_PROVIDER_PREFS.get(prefer or "")
    if not pref_names:
        return ordered
    pref_set = set(pref_names)
    head = [p for name in pref_names for p in ordered if p.name == name]
    if not head:
        return ordered
    tail = [p for p in ordered if p.name not in pref_set]
    return head + tail


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
                "model": env_vars.get("MINIMAX_MODEL", "MiniMax-M3"),
                "priority": 1,
            })
        # MiniMax 降级模型（M2.7 等），与主力共用同一 API Key / base_url
        fallback_model = env_vars.get("MINIMAX_FALLBACK_MODEL")
        has_fallback = any(p.get("name") == "minimax-fallback" for p in config["providers"])
        if fallback_model and not has_fallback:
            config["providers"].append({
                "name": "minimax-fallback",
                "type": "api",
                "base_url": env_vars.get("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1"),
                "api_key": env_vars["MINIMAX_API_KEY"],
                "model": fallback_model,
                "priority": 2,
            })

    # 4. 如果环境变量中有其他 OpenAI 兼容配置，自动添加
    # GLM 默认 priority=3（与 kimi-coding 同级，排在 minimax 之后）
    for prefix in ["OPENAI", "DEEPSEEK", "GROQ", "AZURE", "GLM"]:
        key = env_vars.get(f"{prefix}_API_KEY")
        if key:
            name = prefix.lower()
            has_it = any(p.get("name") == name for p in config["providers"])
            if not has_it:
                default_prio = "3" if prefix == "GLM" else "2"
                config["providers"].append({
                    "name": name,
                    "type": "api",
                    "base_url": env_vars.get(f"{prefix}_BASE_URL", ""),
                    "api_key": key,
                    "model": env_vars.get(f"{prefix}_MODEL", ""),
                    "priority": env_vars.get(f"{prefix}_PRIORITY", default_prio),
                })

    # 4.5 GLM 降级模型（例如 GLM-5.1 作为 GLM-5.2 fallback），与主力共用同一 API Key / base_url
    glm_key = env_vars.get("GLM_API_KEY")
    glm_fallback_model = env_vars.get("GLM_FALLBACK_MODEL")
    has_glm_fallback = any(p.get("name") == "glm-fallback" for p in config["providers"])
    if glm_key and glm_fallback_model and not has_glm_fallback:
        config["providers"].append({
            "name": "glm-fallback",
            "type": "api",
            "base_url": env_vars.get("GLM_BASE_URL", "https://open.bigmodel.cn/api/coding/paas/v4"),
            "api_key": glm_key,
            "model": glm_fallback_model,
            "priority": env_vars.get("GLM_FALLBACK_PRIORITY", "4"),
        })

    # 5. 如果环境变量中有 Kimi coding plan 配置，自动添加
    #    hermes 中 provider 名为 kimi-coding，base_url=https://api.kimi.com/coding
    #    优先读项目 .env/os.environ 的 KIMI_API_KEY，找不到则兜底读 ~/.hermes/.env
    kimi_api_key = env_vars.get("KIMI_API_KEY") or _load_hermes_env_key("KIMI_API_KEY")
    if kimi_api_key:
        has_kimi_coding = any(p.get("name") == "kimi-coding" for p in config["providers"])
        if not has_kimi_coding:
            config["providers"].append({
                "name": "kimi-coding",
                "type": "api",
                "base_url": env_vars.get("KIMI_BASE_URL", "https://api.kimi.com/coding"),
                "api_key": kimi_api_key,
                "model": env_vars.get("KIMI_MODEL", "kimi-k2.7-code"),
                "priority": env_vars.get("KIMI_PRIORITY", "3"),
            })

    # 6. 自动检测本地 CLI（始终执行，与 API provider 无关）
    cli_detected = _detect_cli_providers()
    existing_names = {p["name"] for p in config["providers"]}
    for p in cli_detected:
        if p["name"] not in existing_names:
            config["providers"].append(p)

    # 7. v7.3.82: provider 级停用开关（用户裁决 2026-11-15：kimi 摘出全链，
    #    不再消耗 Kimi 套餐 token）。LLM_DISABLED_PROVIDERS 逗号分隔 provider
    #    名，命中的统一不进候选链——kimi CLI（priority=1 全局排最前）与
    #    kimi-coding API 注入（兜底读 ~/.hermes/.env）都在本处一并过滤；
    #    任务级偏好（TASK_PROVIDER_PREFS）无候选可提升自然失效。
    #    恢复：删除 .env 中该行即可。
    disabled_names = {
        n.strip()
        for n in (env_vars.get("LLM_DISABLED_PROVIDERS") or "").split(",")
        if n.strip()
    }
    if disabled_names:
        dropped = [p.get("name") for p in config["providers"]
                   if p.get("name") in disabled_names]
        if dropped and _log:
            _log.info("[llm_router] 停用 provider: %s", ",".join(dropped))
        config["providers"] = [
            p for p in config["providers"] if p.get("name") not in disabled_names
        ]

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

    def call(self, system_prompt: str, messages: List[Dict[str, str]], timeout: int = 60,
             max_tokens: Optional[int] = None, prefer: Optional[str] = None):
        """调用 LLM 获取回复。

        返回: (response_text, usage_dict)
            - response_text: LLM 生成的文本（已过滤 think 标签）
            - usage_dict: API 返回的 usage 字段，如 {"prompt_tokens": 100, "completion_tokens": 50}
                         CLI 调用时为 None
        """
        # v6.9.80: 输入 NUL 字节净化——raw 文献正文偶含 \x00（PDF 抽取
        # 残留，2026-08-29 实测 6 篇）。CLI 路径 subprocess 参数遇 NUL 抛
        # ValueError("embedded null byte")，API 降级期（429/限流）全降级链
        # 仅剩 CLI 时 7 provider 全灭、蒸馏整批失败。统一在入口净化，
        # API/CLI 双路径一致防御（JSON 载荷虽容忍 \u0000，服务端可能拒收）。
        if "\x00" in system_prompt or any(
            "\x00" in str(m.get("content") or "") for m in messages
        ):
            system_prompt = system_prompt.replace("\x00", "")
            messages = [
                {
                    "role": m.get("role", "user"),
                    "content": str(m.get("content") or "").replace("\x00", ""),
                }
                for m in messages
            ]

        if self.type == "cli":
            raw = self._call_cli(system_prompt, messages, timeout)
            usage = None
        elif self.type == "api":
            # v6.9.79: 传递 max_tokens——旧版 call() 收下该参数却不传，
            # _call_api 内引用未定义名，API 类型 provider（minimax 等）
            # 每次调用必抛 NameError，只能靠 CLI 降级链兜底
            raw, usage = self._call_api(system_prompt, messages, timeout, max_tokens,
                                        prefer=prefer)
        else:
            raise ValueError(f"Unknown provider type: {self.type}")
        # v7.2.54: 剥离 think 标签后为空 → 显式失败（可降级）。
        # 背景：空 content 判定（v6.10.9）只覆盖「原始 content 为空」，发生在
        # 剥离**之前**。推理型模型（MiniMax-M3 等）把全部 max_tokens 预算
        # 耗在 <think> 思考块、content 剥离后为空串的形态被当成成功：
        # 既不触发 provider 降级，又在 step_usage 账本记 success=True 而
        # output_chars=0（10 月全库 97 条、全部 completion_tokens=4096，
        # 7 天 success_rate 虚高 6.70pp）。此处抛错进入 router 的 except
        # 分支 → failure_count+1 → 自动降级到下一 provider，与 v6.10.9
        # 「空响应从静默成功变可重试失败」的设计意图一致。
        cleaned = _strip_think_tags(raw)
        if not (cleaned or "").strip():
            # v7.2.55: 改抛专用异常并携带 usage（同 provider 重试无意义，
            # token 消耗须入失败账本可见）
            raise ThinkOnlyResponseError(
                "响应剥离 think 标签后为空（疑似 reasoning-only / 预算耗尽于思考阶段）",
                usage=usage,
            )
        return cleaned, usage

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
            ["kimi", "-p", prompt_text, "--output-format", "text"],
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
        cmd = ["claude", "-p", "--output-format", "text"]
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

    def _call_api(self, system_prompt: str, messages: List[Dict[str, str]], timeout: int,
                  max_tokens: Optional[int] = None, prefer: Optional[str] = None,
                  _strip_no_think: bool = False) -> str:
        """调用 OpenAI 兼容 API。

        v6.9.79: 签名补 max_tokens 参数——原实现 L398 引用该名但签名
        未声明（call() 也未传递），API 类型 provider 必抛
        NameError("name 'max_tokens' is not defined")。
        v7.3.83: 签名补 prefer——机械任务（TASKS_DISABLE_THINKING）对
        GLM 系注入请求级 thinking:disabled；_strip_no_think 供 400 回退
        时剥离参数重发（内部用，不进对外签名语义）。
        """
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
            "max_tokens": max_tokens or 4096,
        }

        # v7.3.83: 机械任务关思考——GLM 系请求级 thinking 参数。
        no_think = (
            not _strip_no_think
            and prefer in TASKS_DISABLE_THINKING
            and self.name in THINKING_DISABLE_PROVIDERS
        )
        if no_think:
            payload["thinking"] = {"type": "disabled"}


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
            # P3-7: SSL 证书验证降级 — 企业网络/代理自签证书环境下允许跳过
            import ssl as _ssl
            ctx = _ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = _ssl.CERT_NONE
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                msg = (data.get("choices") or [{}])[0].get("message") or {}
                text = msg.get("content")
                # v7.2.66: usage 提前取——空响应的 token 消耗也必须入失败账本
                usage = data.get("usage")
                # v6.10.9: 空 content 显式失败——思考型模型可能把内容放
                # reasoning_content 而 content 为空、或服务端间歇性空输出。
                # v7.2.66: 升级为 ThinkOnlyResponseError 专用通道——10 月
                # 实测 glm 空响应 218 次/7 天（finish_reason=length，推理
                # 吃光预算），旧版抛普通 RuntimeError 被同 provider 无脑
                # 重试放大（同 prompt 同预算必然重演）。接入 v7.2.55 通道：
                # ① 跳过同 provider 重试直接降级；② usage 入失败记账。
                if not (text or "").strip():
                    finish = (data.get("choices") or [{}])[0].get("finish_reason", "")
                    raise ThinkOnlyResponseError(
                        f"API 返回空 content（finish_reason={finish or 'unknown'}，"
                        f"疑似 reasoning-only/服务端空输出）",
                        usage=usage,
                    )
                return text, usage
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            # v7.3.83: thinking 参数不被端点/模型接受（HTTP 400 拒绝整个
            # 请求）→ 剥离该参数重发一次，宁可少省不可断链（仅回退一次，
            # _strip_no_think 防递归）。
            if no_think and e.code == 400:
                if _log:
                    _log.warning(f"[{self.name}] thinking 参数被拒 (400)，剥离后重发")
                return self._call_api(system_prompt, messages, timeout, max_tokens,
                                      prefer=prefer, _strip_no_think=True)
            # v7.3.66: 429 专用异常——路由层据此跳过同 provider 重试
            if e.code == 429:
                raise RateLimitError(f"API HTTP {e.code}: {body}", code=e.code)
            raise RuntimeError(f"API HTTP {e.code}: {body}")
        except urllib.error.URLError as e:
            # P3-7: SSL/网络错误明确提示
            if "SSL" in str(e) or "CERTIFICATE" in str(e):
                raise RuntimeError(f"SSL 证书验证失败: {e}")
            raise RuntimeError(f"网络错误: {e}")


# ---------------------------------------------------------------------------
# 路由管理器
# ---------------------------------------------------------------------------

class LLMRouter:
    """LLM 路由管理器 — 按策略选择 Provider，自动降级。"""

    def __init__(self):
        self.config = _build_config()
        self.providers = [LLMProvider(p) for p in self.config.get("providers", [])]
        self._round_robin_idx = 0
        self.force_provider: Optional[str] = None  # 手动强制指定
        self._last_used: Optional[str] = None       # 记录上次实际使用的 Provider
        self.load_force_provider()

    def call_llm(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        timeout: Optional[int] = None,
        prefer: Optional[str] = None,
    ):
        """调用 LLM（v6.10.52 起带计量），委托 _call_llm_impl。

        计时并写入 step_usage 账本（provider/model/usage/成败），失败时
        同样入账后原样抛出。返回契约与 impl 一致：`(text, usage, provider)`。
        """
        import time as _time
        _t0 = _time.time()
        _prompt_chars = len(system_prompt or "") + sum(
            len(m.get("content") or "") for m in (messages or []))
        try:
            result, usage, provider_name = self._call_llm_impl(
                system_prompt, messages, timeout=timeout, prefer=prefer)
        except Exception as e:
            _record_llm_call(
                "(all-failed)", prefer=prefer or "",
                elapsed_s=_time.time() - _t0, success=False,
                prompt_chars=_prompt_chars, error=str(e)[:200])
            raise
        _model = ""
        for _p in self.providers:
            if _p.name == provider_name:
                _model = _p.config.get("model", "") if _p.type == "api" else _p.name
                break
        _record_llm_call(
            provider_name, provider=provider_name, model=_model,
            prefer=prefer or "", elapsed_s=_time.time() - _t0, success=True,
            prompt_chars=_prompt_chars,
            output_chars=len(result) if isinstance(result, str) else 0,
            usage=usage if isinstance(usage, dict) else None)
        return result, usage, provider_name

    def _call_llm_impl(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        timeout: Optional[int] = None,
        prefer: Optional[str] = None,
    ):
        """调用 LLM。若 force_provider 已设置则直接使用；否则按策略自动选择。

        Args:
            system_prompt: 系统提示词
            messages: 消息列表 [{role, content}, ...]
            timeout: 单次调用超时（秒），None 则使用配置默认值。
            prefer: 任务标签（v6.9.4，如 "governance"）。自动策略下把
                TASK_PROVIDER_PREFS 中注册的 provider 提到队首；偏好
                不可用或失败时回落全局链。force_provider 存在时忽略。

        Returns:
            LLM 生成的文本

        Raises:
            RuntimeError: 所有 Provider 均失败
        """
        timeout = int(timeout or self.config.get("timeout", 60))
        retry = int(self.config.get("retry", 1))
        used_provider_name = ""

        if _log:
            _log.info(f"LLM 路由: strategy={self.config.get('strategy', 'priority')}, force={self.force_provider or 'auto'}")

        # 模式 A：手动强制指定
        if self.force_provider:
            target_name = self.force_provider
            # 特殊值 cli_auto：动态选择第一个可用 CLI
            if target_name == "cli_auto":
                provider = None
                for p in self.providers:
                    if p.type == "cli" and self._is_available(p):
                        provider = p
                        target_name = p.name
                        break
                if not provider:
                    raise RuntimeError("强制 CLI 模式：没有可用的 CLI Provider")
            else:
                provider = self._get_provider(target_name)
            if provider and self._is_available(provider):
                if _log:
                    _log.info(f"LLM 路由: 强制使用 provider={provider.name}")
                for attempt in range(retry + 1):
                    try:
                        result, usage = provider.call(
                            system_prompt, messages, timeout,
                            max_tokens=TASK_MAX_TOKENS.get(prefer or ""),
                            prefer=prefer,
                        )
                        provider.failure_count = 0
                        self._last_used = provider.name
                        if _log:
                            _log.info(f"LLM 路由成功: provider={provider.name} (强制指定)")
                        return result, usage, provider.name
                    except Exception as e:
                        provider.failure_count += 1
                        # v7.2.55: think-only 失败同 provider 重试必然重演，
                        # 跳过重试直接失败（强制指定模式无降级目标）
                        if isinstance(e, ThinkOnlyResponseError):
                            _record_llm_call(
                                provider.name, prefer=prefer or "",
                                success=False, usage=e.usage,
                                error=f"think-only: {e}")
                            raise RuntimeError(
                                f"强制指定 Provider {provider.name} 失败: {e}")
                        if attempt < retry and not isinstance(e, RateLimitError):
                            continue
                        raise RuntimeError(f"强制指定 Provider {provider.name} 失败: {e}")
            else:
                raise RuntimeError(f"强制指定 Provider {target_name} 不可用")

        # 模式 B：自动策略
        strategy = self.config.get("strategy", "priority")
        available = [p for p in self.providers if self._is_available(p)]
        if not available:
            raise RuntimeError("✗ 没有可用的 LLM Provider。请检查配置或安装 CLI 工具。")

        if strategy == "priority":
            available.sort(key=lambda p: p.priority)
        elif strategy == "round_robin":
            idx = self._round_robin_idx % len(available)
            available = available[idx:] + available[:idx]
            self._round_robin_idx = (self._round_robin_idx + 1) % len(available)

        # v7.3.80: 任务级排除——对特定任务形态系统性失效的 provider 直接
        # 摘出候选链（如 kimi CLI 之于 panel 尺寸 prompt）。全被排除则
        # 放弃过滤（防御：宁可让系统性失效的 provider 试一次也别断链）。
        exclude_names = TASK_PROVIDER_EXCLUDE.get(prefer or "") if prefer else None
        if exclude_names:
            exclude_set = set(exclude_names)
            filtered = [p for p in available if p.name not in exclude_set]
            if filtered:
                if _log and len(filtered) != len(available):
                    dropped = [p.name for p in available if p.name in exclude_set]
                    _log.info(
                        f"LLM 路由: prefer={prefer} 排除系统性失效 provider "
                        f"{dropped}（账本实证，见 TASK_PROVIDER_EXCLUDE）")
                available = filtered

        # v6.9.4: 任务级偏好——治理/维护类标签优先 GLM，失败仍回落整链
        if prefer:
            available = _apply_task_preference(available, prefer)

        ordered_names = ", ".join([p.name for p in available])
        primary_name = available[0].name
        if _log:
            _log.info(f"LLM 路由: 可用 providers=[{ordered_names}]，主模型={primary_name}")

        # v7.3.80: 大 prompt think-only 守卫需要 prompt 尺寸（与 call_llm
        # 包装层的记账口径一致：system + 全部 message 内容字符数）。
        prompt_chars_total = len(system_prompt or "") + sum(
            len(m.get("content") or "") for m in (messages or []))

        last_error = ""
        for idx, provider in enumerate(available):
            is_fallback = idx > 0
            # v7.3.80: M3 大 prompt think-only 守卫——超阈值且仍有后续
            # 候选时直接跳过，避免全价烧完 prompt 才降级（实测成功调用
            # p99=27k 字符，panel 尺寸 50k+ think-only 12/12）。末位不跳
            # （有尝试总比整体失败强）；强制指定（模式 A）不拦。
            if (provider.name in THINK_ONLY_PRONE_PROVIDERS
                    and prompt_chars_total >= THINK_ONLY_PRONE_MIN_CHARS
                    and idx < len(available) - 1):
                last_error = (
                    f"⚠ {provider.name} prompt {prompt_chars_total} 字符 "
                    f"≥{THINK_ONLY_PRONE_MIN_CHARS}，跳过（防 think-only），"
                    f"尝试下一个…")
                if _log:
                    _log.warning(last_error)
                print(last_error, file=sys.stderr)
                _record_llm_call(provider.name, prefer=prefer or "",
                                 success=False,
                                 error="skip: 大 prompt 防 think-only")
                continue
            # v7.3.81: for→while 改造——think-only 升预算重试不消耗 attempt
            # 额度（预算变化打破了 v7.2.55「同预算必然重演」的前提，值得
            # 一次就地机会，免得整链 fallback 重复全价 prompt）。
            attempt = 0
            effective_max_tokens = TASK_MAX_TOKENS.get(prefer or "")
            think_only_bumped = False
            while attempt < retry + 1:
                try:
                    # v6.10.10: auto 分支补传任务级 max_tokens——v6.10.9 的
                    # TASK_MAX_TOKENS 放宽只接到了模式 A（强制指定）分支，
                    # 模式 B 漏传导致 weekend_input 的 16384 未生效，长摘要
                    # 在默认 4096 下照旧截断（实测 09-13 17:13 仍 5 次
                    # "疑似截断"，输出 800-1600 字符即断）。
                    # v7.3.81: max_tokens 改经 effective_max_tokens——
                    # think-only 升预算重试时就地抬高。
                    # v7.3.83: 透传 prefer——机械任务对 GLM 系关思考。
                    result, usage = provider.call(
                        system_prompt, messages, timeout,
                        max_tokens=effective_max_tokens, prefer=prefer)
                    provider.failure_count = 0
                    self._last_used = provider.name
                    if _log:
                        if is_fallback:
                            _log.info(f"LLM 路由成功: provider={provider.name} (从 {primary_name} 降级/fallback)")
                        else:
                            _log.info(f"LLM 路由成功: provider={provider.name} (主模型)")
                    return result, usage, provider.name
                except urllib.error.HTTPError as e:
                    provider.failure_count += 1
                    if e.code == 429:
                        last_error = f"⚠ {provider.name} 限流 (429)，尝试下一个…"
                        if _log:
                            _log.warning(f"Provider {provider.name} 限流 (429)")
                        print(last_error, file=sys.stderr)
                    elif e.code >= 500:
                        last_error = f"⚠ {provider.name} 服务端错误 ({e.code})，尝试下一个…"
                        if _log:
                            _log.warning(f"Provider {provider.name} 服务端错误 ({e.code})")
                        print(last_error, file=sys.stderr)
                    else:
                        last_error = f"✗ {provider.name} HTTP {e.code}"
                        if _log:
                            _log.error(f"Provider {provider.name} HTTP {e.code}")
                    _record_llm_call(provider.name, prefer=prefer or "",
                                     success=False, error=last_error)
                    attempt += 1  # v7.3.81: while 改造后需手动推进
                except subprocess.TimeoutExpired:
                    provider.failure_count += 1
                    last_error = f"⚠ {provider.name} 超时，尝试下一个…"
                    if _log:
                        _log.warning(f"Provider {provider.name} 超时")
                    print(last_error, file=sys.stderr)
                    _record_llm_call(provider.name, prefer=prefer or "",
                                     success=False, error=last_error)
                    # v7.3.80: 超时不在同 provider 上重试——CLI 同命令同
                    # prompt 重跑大概率重演（实测 kimi panel 超时全部成对
                    # 出现，每对白等 2×timeout=20 分钟），直接切下一
                    # provider（与 v7.2.55 think-only、v7.3.66 限流同纪律）。
                    break
                except Exception as e:
                    provider.failure_count += 1
                    # v7.3.66: 429 限流同样不在同 provider 上重试——限流窗口内
                    # 同 prompt 立即重试必然再次 429（11-07 实测每调用双发），
                    # 直接切换下一 provider，减少失败账本噪声与限流计数。
                    if isinstance(e, RateLimitError):
                        last_error = f"⚠ {provider.name} 限流 (429)，跳过重试切下一 provider"
                        if _log:
                            _log.warning(
                                f"Provider {provider.name} 限流 (429)，"
                                f"跳过同 provider 重试")
                        print(last_error, file=sys.stderr)
                        _record_llm_call(
                            provider.name, prefer=prefer or "",
                            success=False, error=str(e))
                        break
                    # v7.2.55（BUG-21 副作用治理）：think-only 失败不在同
                    # provider 上重试——同 prompt 同预算必然重演，重试只会
                    # 把单次调用放大为 N×(retry+1) 次空烧 token；直接切换
                    # 下一 provider（不同模型可能非推理型）。usage 随失败
                    # 记账入账本，token 消耗可见。
                    # v7.3.81: 修订——账本全库 214 次回溯证明 think-only
                    # 全部是预算型（completion_tokens 恰为 4096 默认上限，
                    # 思考 token 计入预算打满、正文为空）。首次 think-only
                    # 就地升 max_tokens 重试一次（不消耗 retry 额度）：预算
                    # 变化打破确定性重演，思考有了空间即可能产出正文，省去
                    # 整链 fallback 重复全价 prompt；升预算后仍空才认定
                    # 非预算问题，切下一 provider。
                    if isinstance(e, ThinkOnlyResponseError):
                        if not think_only_bumped:
                            think_only_bumped = True
                            effective_max_tokens = min(
                                max(THINK_ONLY_RETRY_MAX_TOKENS,
                                    (effective_max_tokens or 4096) * 4),
                                THINK_ONLY_RETRY_MAX_CAP)
                            last_error = (
                                f"⚠ {provider.name} think-only（生成预算耗尽），"
                                f"就地升 max_tokens={effective_max_tokens} 重试")
                            if _log:
                                _log.warning(last_error)
                            print(last_error, file=sys.stderr)
                            _record_llm_call(
                                provider.name, prefer=prefer or "",
                                success=False, usage=e.usage,
                                error=f"think-only: {e}（升预算重试）",
                                note=f"think_only_retry:{effective_max_tokens}")
                            continue
                        last_error = (
                            f"✗ {provider.name}: think-only（升预算重试仍空，"
                            f"切下一 provider）")
                        if _log:
                            _log.warning(
                                f"Provider {provider.name} 升预算重试仍 "
                                f"think-only，切下一 provider")
                        print(last_error, file=sys.stderr)
                        _record_llm_call(
                            provider.name, prefer=prefer or "",
                            success=False, usage=e.usage,
                            error=f"think-only: {e}")
                        break
                    last_error = f"✗ {provider.name}: {e}"
                    if _log:
                        _log.error(f"Provider {provider.name} 错误: {e}")
                    _record_llm_call(provider.name, prefer=prefer or "",
                                     success=False, error=last_error)
                    attempt += 1  # v7.3.81: while 改造后需手动推进

        if _log:
            _log.error(f"所有 Provider 均失败。最后错误: {last_error}")
        raise RuntimeError(f"所有 Provider 均失败。最后错误: {last_error}")

    def _get_provider(self, name: str) -> Optional[LLMProvider]:
        """按名称查找 Provider。"""
        for p in self.providers:
            if p.name == name:
                return p
        return None

    def _is_available(self, provider: LLMProvider) -> bool:
        """检查 Provider 是否可用。"""
        if provider.type == "cli":
            return shutil.which(provider.name) is not None
        elif provider.type == "api":
            return bool(provider.config.get("api_key") and provider.config.get("base_url"))
        return False

    def get_status(self) -> Dict[str, Any]:
        """返回所有 Provider 的状态和当前配置。"""
        providers = [
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
        active = self.force_provider or self._last_used or ""
        if not active and providers:
            avail = [p for p in providers if p["available"]]
            if avail:
                avail.sort(key=lambda p: p["priority"])
                active = avail[0]["name"]
        return {
            "providers": providers,
            "strategy": self.config.get("strategy", "priority"),
            "force_provider": self.force_provider,
            "active_provider": active,
        }

    def set_provider(self, name: str) -> bool:
        """手动强制指定 Provider。支持特殊值 'cli_auto'（第一个可用 CLI）。"""
        if name == "cli_auto":
            for p in self.providers:
                if p.type == "cli" and self._is_available(p):
                    self.force_provider = "cli_auto"
                    self.save_force_provider()
                    return True
            return False
        provider = self._get_provider(name)
        if provider and self._is_available(provider):
            self.force_provider = name
            self.save_force_provider()
            return True
        return False

    def set_auto(self) -> None:
        """恢复自动策略。"""
        self.force_provider = None
        self.save_force_provider()

    def save_force_provider(self) -> None:
        """将当前强制选择持久化到 llm-config.json。"""
        config: Dict[str, Any] = {}
        if _CONFIG_PATH.exists():
            try:
                with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception:
                pass
        config["force_provider"] = self.force_provider
        _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        _cms.save_json(_CONFIG_PATH, config)

    def load_force_provider(self) -> None:
        """从 llm-config.json 读取持久化的强制选择。"""
        if not _CONFIG_PATH.exists():
            return
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            saved = config.get("force_provider")
            if saved == "cli_auto":
                # 验证是否仍有可用 CLI
                for p in self.providers:
                    if p.type == "cli" and self._is_available(p):
                        self.force_provider = "cli_auto"
                        return
            elif saved:
                provider = self._get_provider(saved)
                if provider and self._is_available(provider):
                    self.force_provider = saved
        except Exception:
            pass

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
        status = router.get_status()
        print("=== LLM Provider 状态 ===")
        print(f"  策略: {status['strategy']}  |  当前: {status['active_provider'] or 'auto'}")
        if status['force_provider']:
            print(f"  [强制指定: {status['force_provider']}]")
        for s in status["providers"]:
            avail = "✓" if s["available"] else "✗"
            model = f" ({s['model']})" if s.get("model") else ""
            print(f"  {avail} {s['name']:12} {s['type']:6} 优先:{s['priority']:2}  失败:{s['failure_count']}{model}")
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
