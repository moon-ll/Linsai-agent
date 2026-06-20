#!/usr/bin/env python3
"""知识库自动同步守护脚本 —— 定时触发 sync_all + 重建索引/图谱。

设计为 macOS LaunchAgent 调用（每日 09:00），也可手动执行。

用法:
    python scripts/kb_auto_sync.py                    # 立即执行一次同步
    python scripts/kb_auto_sync.py --install          # 安装 LaunchAgent（每日 09:00）
    python scripts/kb_auto_sync.py --uninstall        # 卸载 LaunchAgent
    python scripts/kb_auto_sync.py --status           # 查看自动同步状态

规范:
    - 仅使用 Python 3 标准库
    - 幂等：重复运行不会重复导入
    - 失败不崩溃：记录错误到 sync-state.json 的 history
    - 输出中文，状态图标统一
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
MEMORY_DIR = PROJECT_ROOT / "memory"
SYNC_STATE_PATH = MEMORY_DIR / "sync-state.json"

# LaunchAgent 配置
LAUNCH_AGENT_ID = "com.linsai.kb-auto-sync"
LAUNCH_AGENT_PATH = Path.home() / "Library" / "LaunchAgents" / f"{LAUNCH_AGENT_ID}.plist"


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_local() -> str:
    """本地时间，用于日志输出。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run_sync() -> dict:
    """执行一次完整同步（sync_all 已内含 reindex + rebuild_graph）。

    Returns:
        同步结果摘要
    """
    print(f"[{_now_local()}] ▶ 知识库自动同步开始")
    print("=" * 50)

    # 动态导入 sync_engine
    sys.path.insert(0, str(SCRIPTS_DIR))
    from sync_engine import sync_all, _load_sync_state, _save_sync_state

    try:
        result = sync_all()
        print(f"[{_now_local()}] ✓ 自动同步完成")
        print(f"  新增会话: {result['new_sessions']}")
        print(f"  新增文献: {result['new_papers']}")
        print(f"  错误数:   {result['errors']}")

        # 记录到 sync-state 的 auto_sync_history
        state = _load_sync_state()
        if "auto_sync_history" not in state:
            state["auto_sync_history"] = []
        state["auto_sync_history"].append({
            "timestamp": _now_utc(),
            "new_sessions": result["new_sessions"],
            "new_papers": result["new_papers"],
            "errors": result["errors"],
            "status": "success",
        })
        state["auto_sync_history"] = state["auto_sync_history"][-30:]  # 保留 30 次
        _save_sync_state(state)

        return result

    except Exception as e:
        print(f"[{_now_local()}] ✗ 自动同步失败: {e}")

        # 记录失败
        try:
            state = _load_sync_state()
            if "auto_sync_history" not in state:
                state["auto_sync_history"] = []
            state["auto_sync_history"].append({
                "timestamp": _now_utc(),
                "status": "failed",
                "error": str(e),
            })
            state["auto_sync_history"] = state["auto_sync_history"][-30:]
            _save_sync_state(state)
        except Exception:
            pass

        return {"new_sessions": 0, "new_papers": 0, "errors": 1, "error": str(e)}


def install_launch_agent() -> None:
    """安装 macOS LaunchAgent，每日 09:00 自动同步。"""
    LAUNCH_AGENT_PATH.parent.mkdir(parents=True, exist_ok=True)

    python_path = sys.executable
    script_path = str(SCRIPTS_DIR / "kb_auto_sync.py")

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{LAUNCH_AGENT_ID}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{PROJECT_ROOT}/logs/kb-auto-sync.log</string>
    <key>StandardErrorPath</key>
    <string>{PROJECT_ROOT}/logs/kb-auto-sync-error.log</string>
    <key>WorkingDirectory</key>
    <string>{PROJECT_ROOT}</string>
</dict>
</plist>
"""

    LAUNCH_AGENT_PATH.write_text(plist_content, encoding="utf-8")
    print(f"✓ LaunchAgent 已安装: {LAUNCH_AGENT_PATH}")
    print(f"  每日 09:00 自动执行同步")

    # 尝试加载
    try:
        subprocess.run(
            ["launchctl", "load", str(LAUNCH_AGENT_PATH)],
            check=True,
            capture_output=True,
        )
        print("✓ LaunchAgent 已加载（立即生效）")
    except subprocess.CalledProcessError as e:
        print(f"⚠ LaunchAgent 加载失败（可能已加载）: {e}")


def uninstall_launch_agent() -> None:
    """卸载 macOS LaunchAgent。"""
    if LAUNCH_AGENT_PATH.exists():
        try:
            subprocess.run(
                ["launchctl", "unload", str(LAUNCH_AGENT_PATH)],
                capture_output=True,
            )
        except Exception:
            pass
        LAUNCH_AGENT_PATH.unlink()
        print(f"✓ LaunchAgent 已卸载: {LAUNCH_AGENT_PATH}")
    else:
        print("○ LaunchAgent 不存在，无需卸载")


def show_status() -> None:
    """显示自动同步状态。"""
    print("=" * 50)
    print("  知识库自动同步状态")
    print("=" * 50)

    # LaunchAgent 状态
    installed = LAUNCH_AGENT_PATH.exists()
    print(f"\n  LaunchAgent: {'✓ 已安装' if installed else '✗ 未安装'}")
    if installed:
        print(f"  路径: {LAUNCH_AGENT_PATH}")

    # 同步历史
    if SYNC_STATE_PATH.exists():
        state = json.loads(SYNC_STATE_PATH.read_text(encoding="utf-8"))
        auto_history = state.get("auto_sync_history", [])
        print(f"\n  自动同步历史（最近 {len(auto_history)} 次）:")
        if auto_history:
            for record in auto_history[-5:]:
                ts = record.get("timestamp", "")[:19]
                status = record.get("status", "unknown")
                if status == "success":
                    ns = record.get("new_sessions", 0)
                    np = record.get("new_papers", 0)
                    print(f"    {ts}  ✓ 新增 {ns} 会话 + {np} 文献")
                else:
                    err = record.get("error", "")[:60]
                    print(f"    {ts}  ✗ 失败: {err}")
        else:
            print("    ○ 无自动同步记录")

        last_sync = state.get("last_sync", "")
        print(f"\n  上次同步: {last_sync[:19] if last_sync else '从未'}")
    else:
        print("\n  ○ 同步状态文件不存在")

    print("\n" + "=" * 50)


def main() -> None:
    parser = argparse.ArgumentParser(description="知识库自动同步守护脚本")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--install", action="store_true", help="安装 LaunchAgent（每日 09:00）")
    group.add_argument("--uninstall", action="store_true", help="卸载 LaunchAgent")
    group.add_argument("--status", action="store_true", help="查看自动同步状态")
    args = parser.parse_args()

    if args.install:
        install_launch_agent()
    elif args.uninstall:
        uninstall_launch_agent()
    elif args.status:
        show_status()
    else:
        run_sync()


if __name__ == "__main__":
    main()
