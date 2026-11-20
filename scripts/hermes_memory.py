#!/usr/bin/env python3
"""Hermes Profile 记忆回写工具。

提供：
- _run_hermes_agent(profile, prompt, timeout) → 调用 hermes agent loop（oneshot）
- _write_memory(profile, content) → 追加记忆条目到 profile 的 MEMORY.md
- _write_memory_batch(profile, entries) → 批量追加多条记忆

记忆格式（MEMORY.md）：
    条目1内容
    §
    条目2内容
    §
    ...

用法示例：
    from hermes_memory import _run_hermes_agent, _write_memory
    result = _run_hermes_agent("researcher", "调研XX方向", timeout=300)
    _write_memory("researcher", "已完成XX调研，关键发现：...")

约束：
    - 仅使用 Python 3 标准库
    - 路径使用 pathlib.Path
    - 记忆写入使用原子写入（避免并发写冲突）
"""

from __future__ import annotations

import os
import re
import signal
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

# hermes profile 记忆目录
_HERMES_HOME = Path.home() / ".hermes"
_PROFILES_DIR = _HERMES_HOME / "profiles"

# 日志
try:
    from logger import get_logger
    _log = get_logger("hermes_memory")
except Exception:
    _log = None

# v6.10.52: profile 主模型缓存（供 step_usage 账本归因）
_PROFILE_MODEL_CACHE: Dict[str, str] = {}


def _profile_primary_model(profile: str) -> str:
    """读取 profile 主模型（config.yaml 的 model.default），带进程内缓存。

    用于 step_usage 账本的模型归因；解析失败返回空串（不影响调用）。
    """
    if profile in _PROFILE_MODEL_CACHE:
        return _PROFILE_MODEL_CACHE[profile]
    model = ""
    try:
        cfg = _PROFILES_DIR / profile / "config.yaml"
        text = cfg.read_text(encoding="utf-8", errors="ignore")[:4096] if cfg.exists() else ""
        m = re.search(r"^model:\s*\n\s+default:\s*([^\s#]+)", text, re.M)
        if m:
            model = m.group(1)
    except Exception:
        model = ""
    _PROFILE_MODEL_CACHE[profile] = model
    return model


def _profile_memory_path(profile: str) -> Optional[Path]:
    """获取指定 profile 的 MEMORY.md 路径。"""
    mem_path = _PROFILES_DIR / profile / "memories" / "MEMORY.md"
    if not mem_path.exists():
        if _log:
            _log.warning(f"[hermes_memory] profile {profile} 的 MEMORY.md 不存在")
        return None
    return mem_path


def _run_hermes_agent(
    profile: str,
    prompt: str,
    timeout: int = 300,
) -> Dict[str, Any]:
    """调用 hermes agent loop（v6.10.52 起带计量），委托 _impl 并入账。

    记录 profile / 主模型 / 提示与输出字符数 / 时长 / 成败到
    memory/usage/step-usage-*.jsonl；记账失败静默，不影响调用本身。
    """
    import time as _time
    _t0 = _time.time()
    result = _run_hermes_agent_impl(profile, prompt, timeout=timeout)
    try:
        import step_usage
        step_usage.record_call(
            "hermes_agent", profile,
            model=_profile_primary_model(profile),
            elapsed_s=_time.time() - _t0,
            success=bool(result.get("success")),
            prompt_chars=len(prompt or ""),
            output_chars=len(result.get("output") or ""),
            error=str(result.get("error") or "")[:200],
        )
    except Exception:
        pass
    return result


def _run_hermes_agent_impl(
    profile: str,
    prompt: str,
    timeout: int = 300,
) -> Dict[str, Any]:
    """调用 hermes agent loop（oneshot 模式）。

    通过 hermes CLI 的 -z 参数派发一次性任务给指定 profile，
    由 agent 自主执行（多轮 tool use）直到完成。

    Args:
        profile: hermes profile 名称（如 "researcher"）
        prompt: 任务描述
        timeout: 超时秒数（agent loop 通常较慢，默认 300s）

    Returns:
        {"success": bool, "output": str, "error": str, "elapsed_s": float}
    """
    import time
    from common import hermes_subprocess_env

    env = hermes_subprocess_env()
    cmd = ["hermes", "--profile", profile, "-z", prompt]

    # 从 llm_router 或项目 .env 中读取 MiniMax 配置，透传给 hermes
    # 确保 hermes researcher 也能使用相同的 API Key
    _inject_minimax_env(env)

    t0 = time.time()
    proc = None
    try:
        # v6.8.40: 使用 Popen + 进程组杀死替代 subprocess.run，与
        # proposal_lifecycle/optimize.py v6.8.3-fix9 修复策略一致。
        # subprocess.run(timeout=N) 在 macOS 上只 kill 直接子进程，
        # 若 hermes CLI fork 了额外进程（如 gateway worker），这些进程会
        # 继续运行导致 CLI 端口/管道不释放，孤儿进程累积消耗资源
        # （2026-07-26 机器冻结事故同类风险）。start_new_session=True 使
        # 子进程成为新进程组 leader，timeout 后用 os.killpg 清理整个进程组。
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            start_new_session=True,
        )
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            # 杀死整个进程组（hermes CLI + 所有子进程）
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                    proc.wait(timeout=3)
            except (ProcessLookupError, PermissionError):
                pass
            elapsed = round(time.time() - t0, 2)
            if _log:
                _log.warning(
                    f"[hermes_memory] agent loop 超时 profile={profile} "
                    f"timeout={timeout}s（进程组已清理）"
                )
            return {
                "success": False,
                "output": "",
                "error": f"hermes agent 超时（{timeout}s）",
                "elapsed_s": elapsed,
            }
        elapsed = round(time.time() - t0, 2)
        if proc.returncode == 0:
            output = stdout.strip()
            if len(output) > 8000:
                output = output[:8000] + f"\n\n... (已截断，共 {len(output)} 字符)"
            if _log:
                _log.info(
                    f"[hermes_memory] agent loop 成功 profile={profile} "
                    f"elapsed={elapsed}s"
                )
            return {"success": True, "output": output, "error": "", "elapsed_s": elapsed}
        return {
            "success": False,
            "output": stdout.strip()[:2000],
            "error": stderr.strip()[:500] or f"退出码 {proc.returncode}",
            "elapsed_s": elapsed,
        }
    except FileNotFoundError:
        return {"success": False, "output": "", "error": "未找到 hermes 命令", "elapsed_s": 0}
    except Exception as e:
        # 兜底：确保进程被清理
        if proc and proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except Exception:
                pass
        return {"success": False, "output": "", "error": str(e), "elapsed_s": 0}


def _inject_minimax_env(env: dict) -> None:
    """从环境变量或 llm_router 配置中注入 MiniMax API Key 到 hermes 子进程环境。"""
    # 如果已经设置了 MINIMAX_CN_API_KEY（hermes 的 minimax-cn provider 需要），跳过
    if env.get("MINIMAX_CN_API_KEY"):
        return

    # 从项目 .env 读取
    try:
        from paths import PROJECT_ROOT
        from common import load_env_file
        project_env = load_env_file(PROJECT_ROOT / ".env")
        minimax_key = project_env.get("MINIMAX_API_KEY") or project_env.get("MINIMAX_CN_API_KEY")
        if minimax_key:
            env["MINIMAX_CN_API_KEY"] = minimax_key
            if _log:
                _log.debug("[hermes_memory] 已注入 MINIMAX_CN_API_KEY")
    except Exception:
        pass


def _write_memory(profile: str, content: str) -> bool:
    """向指定 profile 的 MEMORY.md 追加一条记忆。

    使用 § 分隔符，格式与 hermes 原生记忆格式一致。
    使用原子写入避免并发冲突。

    Args:
        profile: hermes profile 名称
        content: 记忆内容（纯文本，将在写入时自动追加 § 分隔符）

    Returns:
        True 表示写入成功，False 表示失败
    """
    mem_path = _profile_memory_path(profile)
    if not mem_path:
        return False

    try:
        current = mem_path.read_text(encoding="utf-8").rstrip()
        # 确保以 § 结尾
        if current.endswith("§"):
            new_content = f"\n{content}\n§"
        else:
            new_content = f"\n§\n{content}\n§"

        # 原子写入
        _atomic_write(mem_path, current + new_content)

        if _log:
            preview = content[:100].replace("\n", " ")
            _log.info(f"[hermes_memory] 已写入记忆 profile={profile} 前100字: {preview}")
        return True
    except Exception as e:
        if _log:
            _log.error(f"[hermes_memory] 写入记忆失败 profile={profile}: {e}")
        return False


def _write_memory_batch(profile: str, entries: List[str]) -> int:
    """批量追加多条记忆。

    Args:
        profile: hermes profile 名称
        entries: 记忆内容列表

    Returns:
        成功写入的条目数
    """
    count = 0
    for entry in entries:
        if _write_memory(profile, entry):
            count += 1
    return count


def _atomic_write(path: Path, content: str) -> None:
    """原子写入文件（tempfile + fsync + os.replace）。"""
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.tmp.",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, str(path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        raise


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_check() -> List[str]:
    """运行自检，返回错误列表。"""
    errors: List[str] = []

    # 检查 hermes 命令是否可用
    hermes_ok = False
    import shutil
    if shutil.which("hermes"):
        hermes_ok = True
    if not hermes_ok:
        errors.append("hermes 命令不可用")

    # 检查 researcher profile 记忆文件
    mem_path = _profile_memory_path("researcher")
    if not mem_path:
        errors.append("researcher MEMORY.md 不存在")
    else:
        content = mem_path.read_text(encoding="utf-8")
        if "§" not in content:
            errors.append("researcher MEMORY.md 缺少 § 分隔符")

    # 检查 llm_router 是否可导入
    try:
        from llm_router import router as _r
        _r.get_status()
    except Exception:
        errors.append("llm_router 不可用")

    if not errors:
        if _log:
            _log.info("[hermes_memory] 自检通过")
    return errors


if __name__ == "__main__":
    errors = _self_check()
    if errors:
        print("自检失败:")
        for e in errors:
            print(f"  ✗ {e}")
    else:
        print("✓ 自检通过")