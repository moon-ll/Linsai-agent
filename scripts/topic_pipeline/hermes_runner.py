# -*- coding: utf-8 -*-
"""课题启动包管线（v8）——hermes oneshot 执行器（含 API 错误特征检测）。

继承 v6.8.46 防线：hermes CLI 配额耗尽/限流时以 returncode=0 退出且 stdout
为错误文本，必须识别为失败，防止错误文本被当产物落盘。
每次调用经 step_usage 入账（v6.10.55 全链计量，kind=hermes_agent）。

用法示例：
    from topic_pipeline.hermes_runner import run_hermes
    res = run_hermes("researcher", "请调研……", timeout=900)
"""
from __future__ import annotations

import subprocess
import time
from typing import Any, Dict, List

from common import hermes_subprocess_env

from .constants import PROJECT_ROOT

# v6.8.46 特征清单（照抄 proposal_lifecycle/optimize.py，单一语义两处实现
# 各自独立演进；>2000 字符输出不判错，防长文引用错误信息误判）
_API_ERROR_SIGNATURES = (
    "API call failed",
    "已达到 Token Plan 用量上限",
    "购买积分补充用量",
    "HTTP 429",
    "rate limit exceeded",
    "quota exceeded",
    "insufficient_quota",
    "API 调用失败",
    "余额不足",
    "账户已欠费",
)


def detect_api_error(output: str) -> str:
    if not output:
        return ""
    if len(output) > 2000:
        return ""
    for sig in _API_ERROR_SIGNATURES:
        if sig in output:
            return sig
    return ""


def run_hermes(profile: str, prompt: str, timeout: int = 900) -> Dict[str, Any]:
    """执行一次 hermes oneshot（agent loop 自主执行），入账 step_usage。"""
    cmd: List[str] = ["hermes", "--profile", profile, "-z", prompt]
    env = hermes_subprocess_env()
    t0 = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            env=env, cwd=str(PROJECT_ROOT),
        )
        elapsed = round(time.time() - t0, 2)
    except subprocess.TimeoutExpired:
        _record(profile, 0.0, False, 0, len(prompt), f"超时 {timeout}s")
        return {"success": False, "output": "", "error": f"hermes agent 超时（{timeout}s）",
                "elapsed_s": round(time.time() - t0, 2)}
    except FileNotFoundError:
        return {"success": False, "output": "", "error": "未找到 hermes 命令", "elapsed_s": 0.0}
    except Exception as e:  # noqa: BLE001
        return {"success": False, "output": "", "error": str(e), "elapsed_s": round(time.time() - t0, 2)}

    output = (result.stdout or "").strip()
    if result.returncode == 0:
        sig = detect_api_error(output)
        if sig:
            _record(profile, elapsed, False, len(output), len(prompt), f"API 错误特征: {sig}")
            return {"success": False, "output": output[:2000], "error": f"API 错误特征命中: {sig}",
                    "elapsed_s": elapsed}
        _record(profile, elapsed, True, len(output), len(prompt), "")
        return {"success": True, "output": output, "error": "", "elapsed_s": elapsed}
    _record(profile, elapsed, False, 0, len(prompt),
            (result.stderr or "").strip()[:200] or f"退出码 {result.returncode}")
    return {
        "success": False,
        "output": output[:2000],
        "error": (result.stderr or "").strip()[:500] or f"退出码 {result.returncode}",
        "elapsed_s": elapsed,
    }


def _record(profile: str, elapsed: float, success: bool, out_chars: int, in_chars: int, error: str) -> None:
    try:
        import step_usage
        step_usage.record_call(
            "hermes_agent", profile,
            elapsed_s=elapsed, success=success,
            prompt_chars=in_chars, output_chars=out_chars, error=error,
        )
    except Exception:
        pass  # 记账失败不阻塞主流程
