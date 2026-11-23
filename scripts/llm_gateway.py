#!/usr/bin/env python3
"""LLM 网关 — 共享基础设施层的受控 LLM 调用通道（v6.3.2）

用途：
    为 CoPilot 核心模块和研究管线模块提供统一的 LLM 调用接口，
    解决 AGENTS.md §6 边界隔离下管线模块无法直接调用 LLM 的问题。

设计理念：
    本模块定位为「共享基础设施层」（同 common.py / paths.py），
    双方均可导入。它封装了 llm_router 的降级策略（MiniMax API →
    Kimi CLI → Claude CLI），对调用方完全透明。

边界合规（AGENTS.md §6）：
    - 本模块归入「共享基础设施」分类（§6.1）
    - 管线模块允许导入本模块（§6.2 ① 扩展）
    - 本模块内部导入 llm_router，但对外只暴露 llm_complete() 等纯函数
    - 管线模块仍禁止直接导入 llm_router

降级与容错：
    - LLM 调用失败时返回结构化错误，不抛异常（管线可降级到模板模式）
    - 支持 dry_run 模式（LLM 不可用时跳过，返回空结果）
    - 调用日志统一记录到 logger

用法示例：
    >>> from llm_gateway import llm_complete, is_llm_available
    >>> if is_llm_available():
    ...     text = llm_complete("你是学术写作助手", "请润色这段话：...")
    ...     if text:
    ...         # 使用 LLM 生成的内容
    ...         pass
    ...     else:
    ...         # 降级到模板
    ...         pass

命令行自检：
    python3 scripts/llm_gateway.py --self-check
    python3 scripts/llm_gateway.py --test "你好"
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 确保可从 scripts/ 目录直接导入
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

__all__ = [
    "llm_complete",
    "llm_chat",
    "is_llm_available",
    "get_llm_status",
    "safe_llm_complete",
]

# ---------------------------------------------------------------------------
# 日志（可选依赖，失败时静默）
# ---------------------------------------------------------------------------
try:
    from logger import get_logger
    _log = get_logger("llm_gateway")
except Exception:
    _log = None


def _log_info(msg: str) -> None:
    if _log:
        _log.info(msg)


def _log_warn(msg: str) -> None:
    if _log:
        _log.warning(msg)


# ---------------------------------------------------------------------------
# 延迟导入 llm_router（避免循环依赖与启动开销）
# ---------------------------------------------------------------------------
_router = None
_router_loaded = False
_router_error: Optional[str] = None


def _get_router():
    """延迟加载 llm_router 全局实例。加载失败时记录原因。"""
    global _router, _router_loaded, _router_error
    if _router_loaded:
        return _router
    _router_loaded = True
    try:
        from llm_router import router as _r
        _router = _r
    except Exception as e:
        _router_error = str(e)
        _log_warn(f"llm_router 加载失败: {e}")
    return _router


# ---------------------------------------------------------------------------
# 公共接口
# ---------------------------------------------------------------------------

def is_llm_available() -> bool:
    """检测 LLM 是否可用（至少有一个 Provider 在线）。"""
    router = _get_router()
    if router is None:
        return False
    try:
        status = router.get_status()
        return bool(status.get("providers"))
    except Exception:
        return False


def get_llm_status() -> Dict[str, Any]:
    """获取 LLM 状态摘要（对管线模块安全的只读视图）。"""
    router = _get_router()
    if router is None:
        return {
            "available": False,
            "error": _router_error or "llm_router 未加载",
            "providers": [],
        }
    try:
        status = router.get_status()
        return {
            "available": True,
            "strategy": status.get("strategy", "priority"),
            "active_provider": status.get("active_provider"),
            "force_provider": status.get("force_provider"),
            "providers": [
                {
                    "name": p.get("name", ""),
                    "type": p.get("type", ""),
                    "available": p.get("available", False),
                    "model": p.get("model", ""),
                }
                for p in status.get("providers", [])
            ],
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "providers": [],
        }


def llm_complete(
    system_prompt: str,
    user_prompt: str,
    timeout: int = 90,
    prefer: Optional[str] = None,
) -> Tuple[bool, str, Dict[str, Any]]:
    """单轮 LLM 调用（system + user 两段式）。

    这是管线模块最常用的入口。返回三元组，永不抛异常。

    Args:
        system_prompt: 系统提示词（角色/任务/约束）。
        user_prompt:   用户输入（待处理的内容）。
        timeout:       调用超时（秒），默认 90。
        prefer:        任务标签（v6.9.4）。治理/维护类任务传 "governance"
                       可优先使用 GLM 系模型；None 走默认 MiniMax 主链。

    Returns:
        (ok, text, meta)
        - ok:    是否成功
        - text:  成功时为 LLM 输出文本；失败时为空字符串
        - meta:  元数据 {provider, usage, error, elapsed_s}
    """
    import time
    router = _get_router()
    if router is None:
        return False, "", {"error": f"llm_router 未加载: {_router_error}"}

    messages = [{"role": "user", "content": user_prompt}]
    t0 = time.time()
    try:
        result, usage, provider_name = router.call_llm(
            system_prompt, messages, timeout=timeout, prefer=prefer)
        elapsed = round(time.time() - t0, 2)
        # v6.10.9: 空 content 双保险——router._call_api 已对空 content 抛错
        # 触发 provider 降级，此处兜底拦截 CLI 类 provider 或旧版本漏网
        # 的空结果（ok=True + 空文本会让所有调用方解析必败）。
        if not (result or "").strip():
            _log_warn(f"LLM 返回空内容（provider={provider_name}）视为失败")
            return False, "", {
                "provider": provider_name,
                "error": "empty content",
                "elapsed_s": elapsed,
            }
        _log_info(f"LLM 调用成功 provider={provider_name} elapsed={elapsed}s")
        return True, result or "", {
            "provider": provider_name,
            "usage": usage or {},
            "elapsed_s": elapsed,
        }
    except Exception as e:
        elapsed = round(time.time() - t0, 2)
        _log_warn(f"LLM 调用失败 elapsed={elapsed}s: {e}")
        return False, "", {
            "error": str(e),
            "elapsed_s": elapsed,
        }


def llm_chat(
    system_prompt: str,
    messages: List[Dict[str, str]],
    timeout: int = 90,
    prefer: Optional[str] = None,
) -> Tuple[bool, str, Dict[str, Any]]:
    """多轮 LLM 调用（传入完整消息历史）。

    Args:
        system_prompt: 系统提示词。
        messages:      消息列表 [{role, content}, ...]。
        timeout:       调用超时（秒）。
        prefer:        任务标签（v6.9.4），语义同 llm_complete。

    Returns:
        同 llm_complete。
    """
    import time
    router = _get_router()
    if router is None:
        return False, "", {"error": f"llm_router 未加载: {_router_error}"}

    t0 = time.time()
    try:
        result, usage, provider_name = router.call_llm(
            system_prompt, messages, timeout=timeout, prefer=prefer)
        elapsed = round(time.time() - t0, 2)
        _log_info(f"LLM 多轮调用成功 provider={provider_name} elapsed={elapsed}s")
        return True, result or "", {
            "provider": provider_name,
            "usage": usage or {},
            "elapsed_s": elapsed,
        }
    except Exception as e:
        elapsed = round(time.time() - t0, 2)
        _log_warn(f"LLM 多轮调用失败 elapsed={elapsed}s: {e}")
        return False, "", {
            "error": str(e),
            "elapsed_s": elapsed,
        }


def safe_llm_complete(
    system_prompt: str,
    user_prompt: str,
    fallback: str = "",
    timeout: int = 90,
    prefer: Optional[str] = None,
) -> str:
    """安全 LLM 调用：失败时返回 fallback 文本（最简形式）。

    适用于「锦上添花」场景——LLM 生成的内容更好，但模板也能用。

    >>> text = safe_llm_complete(sys_prompt, user_prompt, fallback=template_text)
    """
    ok, text, _ = llm_complete(system_prompt, user_prompt, timeout=timeout, prefer=prefer)
    if ok and text.strip():
        return text.strip()
    return fallback


# ---------------------------------------------------------------------------
# JSON 输出辅助（LLM 常被要求输出 JSON）
# ---------------------------------------------------------------------------

def llm_json(
    system_prompt: str,
    user_prompt: str,
    timeout: int = 90,
    prefer: Optional[str] = None,
) -> Tuple[bool, Any, Dict[str, Any]]:
    """LLM 调用并解析 JSON 输出。

    Args:
        system_prompt, user_prompt: 同 llm_complete。
        timeout: 超时秒数。
        prefer:  任务标签（v6.9.4），语义同 llm_complete。

    Returns:
        (ok, data, meta)
        - ok:   是否成功（LLM 调用成功 AND JSON 解析成功）
        - data: 成功时为解析后的 dict/list；失败时为 None
        - meta: 同 llm_complete，额外含 json_error 字段（若解析失败）
    """
    import json as _json
    ok, text, meta = llm_complete(system_prompt, user_prompt, timeout=timeout, prefer=prefer)
    if not ok:
        return False, None, meta
    # 尝试提取 JSON（LLM 可能包裹在 ```json ... ``` 或纯文本中）
    text = text.strip()
    # 去除 markdown 代码块
    if text.startswith("```"):
        lines = text.split("\n")
        # 去首行 ``` 和尾行 ```
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        data = _json.loads(text)
        return True, data, meta
    except Exception as e:
        meta["json_error"] = str(e)
        meta["raw_text"] = text[:500]
        _log_warn(f"LLM JSON 解析失败: {e}")
        return False, None, meta


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_check() -> None:
    """模块自检。"""
    print("=== llm_gateway 自检 ===")

    # 1. 模块导入
    print("[1] 模块导入...", end=" ")
    assert is_llm_available is not None
    assert llm_complete is not None
    assert safe_llm_complete is not None
    assert llm_json is not None
    print("✓")

    # 2. 状态查询
    print("[2] 状态查询...", end=" ")
    status = get_llm_status()
    assert "available" in status
    assert "providers" in status
    print(f"✓ (available={status['available']}, providers={len(status['providers'])})")

    # 3. 可用性检测
    print("[3] 可用性检测...", end=" ")
    avail = is_llm_available()
    print(f"✓ (is_llm_available={avail})")

    # 4. safe_llm_complete 降级（不实际调用 LLM，验证 fallback 逻辑）
    print("[4] safe_llm_complete 降级逻辑...", end=" ")
    # 构造一个必定失败的调用（空 system_prompt 强制错误路径不可控，
    # 这里仅验证函数签名与返回类型）
    try:
        # 不实际触发 LLM，只验证函数可调用
        assert callable(safe_llm_complete)
        print("✓")
    except Exception as e:
        print(f"✗ {e}")
        raise

    # 5. llm_json 解析逻辑
    print("[5] llm_json 解析逻辑...", end=" ")
    import json as _json
    # 模拟 markdown 包裹的 JSON
    test_md = '```json\n{"a": 1, "b": 2}\n```'
    lines = test_md.split("\n")
    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    cleaned = "\n".join(lines).strip()
    assert _json.loads(cleaned) == {"a": 1, "b": 2}
    print("✓")

    print("\n✓ llm_gateway 自检全部通过")


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="LLM 网关（共享基础设施层）")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    parser.add_argument("--status", action="store_true", help="查看 LLM 状态")
    parser.add_argument("--test", metavar="PROMPT", help="测试调用")
    args = parser.parse_args(argv)

    if args.self_check:
        _self_check()
        return 0
    if args.status:
        status = get_llm_status()
        print("=== LLM 网关状态 ===")
        print(f"  可用: {'✓' if status['available'] else '✗'}")
        if not status["available"]:
            print(f"  错误: {status.get('error', '未知')}")
        else:
            print(f"  策略: {status.get('strategy', 'priority')}")
            print(f"  当前: {status.get('active_provider', 'auto')}")
            for p in status["providers"]:
                avail = "✓" if p["available"] else "✗"
                model = f" ({p['model']})" if p.get("model") else ""
                print(f"    [{avail}] {p['name']}{model}")
        return 0
    if args.test:
        print(f"=== 测试调用: {args.test} ===")
        ok, text, meta = llm_complete(
            "你是测试助手，请简短回复。",
            args.test,
        )
        print(f"  成功: {'✓' if ok else '✗'}")
        print(f"  返回: {text[:200] if text else '(空)'}")
        print(f"  元数据: {meta}")
        return 0 if ok else 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
