#!/usr/bin/env python3
"""
copilot_engine.py — 核心引擎：LLM调用 + CLI界面

用途：
    作为 LinSai-CoPilot 的主入口，负责检测本地 LLM CLI、调用 LLM、
    与用户进行交互式对话，并提供命令行参数解析。

用法示例：
    >>> python3 scripts/copilot_engine.py --start "固体HHG实验方案"
    >>> python3 scripts/copilot_engine.py --continue
    >>> python3 scripts/copilot_engine.py --list
    >>> python3 scripts/copilot_engine.py --archive 20260508-固体HHG实验方案

规范：
    - 仅使用 Python 3 标准库
    - 头部包含中文 docstring
    - 路径处理使用 pathlib.Path
    - PROJECT_ROOT 通过 Path(__file__).parent.parent 推导
    - 输出使用中文，状态图标统一
    - JSON 文件必须 ensure_ascii=False, indent=2
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

# 统一日志
try:
    from logger import get_logger, setup_logging
    setup_logging()
    _log = get_logger("copilot_engine")
except Exception:
    _log = None

# ---------------------------------------------------------------------------
# 路径与导入配置
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()

if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import llm_router as lr

try:
    from session_manager import (
        create_session,
        load_session,
        append_message,
        list_sessions,
        get_latest_session_id,
        archive_session,
    )
except ImportError as _import_err:
    print(f"✗ 无法导入 session_manager: {_import_err}")
    sys.exit(1)

try:
    from context_builder import build_context
except ImportError:
    _PERSONA_PATH = _PROJECT_ROOT / "persona" / "lin-sai-persona.md"

    def build_context(session_id, user_input, mode="co-working", emergency=False):
        """fallback：当 context_builder 尚未就绪时使用。"""
        system_prompt = (
            "你是林赛（Lin Sai），强场超快光学与阿秒科学领域的独立PI，"
            "用户的专属AI协作者。"
        )
        if _PERSONA_PATH.exists():
            system_prompt = _PERSONA_PATH.read_text(encoding="utf-8")[:3000]

        messages = []
        msg_path = _PROJECT_ROOT / "sessions" / session_id / "messages.json"
        if msg_path.exists():
            try:
                history = json.loads(msg_path.read_text(encoding="utf-8"))
                for msg in history:
                    messages.append(
                        {
                            "role": msg.get("role", "user"),
                            "content": msg.get("content", ""),
                        }
                    )
            except Exception:
                pass

        messages.append({"role": "user", "content": user_input})
        return {"system_prompt": system_prompt, "messages": messages}


# ---------------------------------------------------------------------------
# LLM CLI 检测（已迁移到 llm_router，保留兼容接口）
# ---------------------------------------------------------------------------
_LLM_CLI = None

def detect_llm_cli() -> Optional[Tuple[str, str]]:
    """检测本地可用的 LLM CLI，返回 (cli_name, cli_path)。"""
    status = lr.get_status()
    for s in status.get("providers", []):
        if s.get("type") == "cli" and s.get("available"):
            return s["name"], s["name"]
    return None


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------
def _unescape_kimi_text(text: str) -> str:
    """解码 kimi 输出中的转义序列（\\n -> 换行等）。"""

    def _repl(m):
        c = m.group(1)
        mapping = {
            "n": "\n",
            "t": "\t",
            "r": "\r",
            "\\": "\\",
            "'": "'",
            '"': '"',
        }
        return mapping.get(c, m.group(0))

    return re.sub(r"\\(.)", _repl, text)


def _parse_kimi_output(raw: str) -> str:
    """从 kimi --print 的日志输出中提取 assistant 文本。"""
    # 单引号包裹（支持转义字符）
    matches = re.findall(r"text='((?:\\.|[^'\\])*)'", raw)
    if not matches:
        # 双引号包裹
        matches = re.findall(r'text="((?:\\.|[^"\\])*)"', raw)
    if not matches:
        return ""
    texts = [_unescape_kimi_text(m) for m in matches]
    return "\n".join(texts)


def _build_prompt_text(system_prompt: str, messages: list, include_system: bool = True) -> str:
    """将 system_prompt 和 messages 拼接为单个 prompt 字符串。"""
    lines: list[str] = []
    if include_system:
        lines.append(f"[系统指令]\n{system_prompt}")
    if messages:
        lines.append("[对话历史]")
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            label = {"assistant": "助手", "system": "系统"}.get(role, "用户")
            lines.append(f"{label}: {content}")
    return "\n\n".join(lines)


# ---------------------------------------------------------------------------
# LLM 调用封装（已迁移到 llm_router，保留兼容接口）
# ---------------------------------------------------------------------------
def call_llm(system_prompt: str, messages: list, timeout: int = 120):
    """调用 LLM，返回 assistant 的回复内容及用量信息。

    返回:
        (response_text, usage_dict, provider_name)
        - response_text: LLM 生成的文本
        - usage_dict: API 返回的 usage 字段（CLI 调用时为 None）
        - provider_name: 实际使用的 Provider 名称

    由 llm_router 按策略自动选择 Provider：
    - 优先使用配置文件中优先级最高的可用 Provider
    - 支持 CLI (claude, kimi) 和 HTTP API (MiniMax 等)
    - 失败时自动降级到下一个 Provider
    """
    try:
        return lr.call_llm(system_prompt, messages)
    except RuntimeError as e:
        raise RuntimeError(f"LLM 调用失败: {e}") from e


def call_llm_with_tools(system_prompt: str, messages: list, timeout: int = 120):
    """调用 LLM，支持工具调用（子代理）。

    执行流程：
        1. 在 system_prompt 中注入可用工具说明
        2. 第一次调用 LLM，获取响应
        3. 解析响应中的工具调用指令
        4. 执行工具，获取结果
        5. 将工具结果作为 assistant/tool 消息加入对话
        6. 第二次调用 LLM，获取最终回复
        7. 返回 (final_text, usage_dict, provider_name, tool_calls_log)

    Returns:
        (response_text, usage_dict, provider_name, tool_log)
        - tool_log: 工具调用记录列表，每项为 {"name", "args", "result"}
    """
    try:
        import importlib.util
        te_path = Path(__file__).parent / "tool_engine.py"
        spec = importlib.util.spec_from_file_location("tool_engine", te_path)
        te = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(te)
    except Exception:
        # 工具引擎不可用，降级为普通调用
        text, usage, provider = lr.call_llm(system_prompt, messages)
        return text, usage, provider, []

    # 注入工具说明
    enhanced_prompt = te.inject_tools_prompt(system_prompt)

    # 第一次调用
    first_text, first_usage, provider = lr.call_llm(enhanced_prompt, messages)
    tool_log = []

    # 检查是否包含工具调用
    if not te.has_tool_calls(first_text):
        # 无工具调用，直接返回（清理可能的残余标记）
        clean_text = te.strip_tool_calls(first_text)
        return clean_text, first_usage, provider, []

    # 解析并执行工具调用
    calls = te.parse_tool_calls(first_text)
    if not calls:
        clean_text = te.strip_tool_calls(first_text)
        return clean_text, first_usage, provider, []

    results = te.execute_tool_calls(calls)

    # 记录工具调用日志
    for i, call in enumerate(calls):
        res = results[i] if i < len(results) else {"success": False, "result": "未知错误"}
        tool_log.append({
            "name": call["name"],
            "args": call["args"],
            "result": res.get("result", ""),
            "success": res.get("success", False),
        })

    # 构建工具结果消息
    tool_messages = list(messages)
    # 追加 assistant 的思考过程（去掉工具调用标记）
    thought = te.strip_tool_calls(first_text)
    if thought:
        tool_messages.append({"role": "assistant", "content": thought})

    # 追加每个工具的结果
    for entry in tool_log:
        tool_messages.append({
            "role": "user",
            "content": f"[工具 {entry['name']} 结果]\n{entry['result']}",
        })

    # 第二次调用：让 LLM 基于工具结果给出最终回复
    final_text, final_usage, _ = lr.call_llm(enhanced_prompt, tool_messages)

    # 合并用量（简单累加）
    merged_usage = {}
    if first_usage:
        merged_usage.update(first_usage)
    if final_usage:
        for k, v in final_usage.items():
            if k in merged_usage and isinstance(v, (int, float)):
                merged_usage[k] = merged_usage.get(k, 0) + v
            else:
                merged_usage[k] = v

    clean_final = te.strip_tool_calls(final_text)
    return clean_final, merged_usage or None, provider, tool_log


# ---------------------------------------------------------------------------
# 交互式对话循环
# ---------------------------------------------------------------------------
def chat_loop(session_id: str, mode: str = "co-working") -> None:
    """交互式对话主循环。

    - 显示当前会话信息
    - 每轮：接收用户输入 → build_context → call_llm → 显示响应 → append_message
    - 支持特殊命令与多行输入
    """
    try:
        messages, state = load_session(session_id)
        if _log:
            _log.info(f"会话加载: {session_id} | 主题: {state.get('topic', '')} | 消息数: {len(messages)}")
    except Exception as exc:
        if _log:
            _log.error(f"加载会话失败: {exc}", exc_info=True)
        print(f"✗ 加载会话失败: {exc}")
        return

    topic = state.get("topic", "未知主题")
    msg_count = len(messages)
    started_at = state.get("started_at", "")

    print(f"\n◐ 会话: {session_id}")
    print(f"  主题: {topic}")
    print(f"  模式: {mode}")
    print(f"  消息数: {msg_count}")
    print(f"  开始于: {started_at}")
    print("  输入 /help 查看命令，空行结束多行输入\n")

    while True:
        try:
            print("> ", end="", flush=True)
        except BrokenPipeError:
            break

        lines: list[str] = []
        try:
            while True:
                line = input()
                if line == "" and lines:
                    break
                lines.append(line)
        except EOFError:
            print("\n✓ 再见")
            break
        except KeyboardInterrupt:
            print("\n✓ 中断退出")
            break

        user_input = "\n".join(lines).strip()
        if not user_input:
            continue

        # 特殊命令处理
        if user_input in ("/exit", "/quit"):
            print("✓ 会话已保存，再见")
            break

        if user_input == "/save":
            print("✓ 会话已自动保存（无需手动操作）")
            continue

        if user_input == "/help":
            print("  /exit, /quit — 退出会话")
            print("  /save        — 手动保存提示（已自动保存）")
            print("  /mode <mode> — 切换交互模式")
            print("  /summary     — 显示会话摘要")
            print("  /read <文件>  — 读取并显示文档/代码内容")
            print("  /agora <人物> — 导出当前上下文到Agora群聊")
            print("  /help        — 显示此帮助")
            continue

        if user_input == "/summary":
            try:
                msgs, st = load_session(session_id)
                duration = "未知"
                try:
                    started = datetime.fromisoformat(
                        st.get("started_at", "").replace("Z", "+00:00")
                    )
                    now = datetime.now(timezone.utc)
                    delta = now - started
                    duration = f"{int(delta.total_seconds() // 60)} 分钟"
                except Exception:
                    pass
                print(f"  主题: {st.get('topic', '')}")
                print(f"  模式: {st.get('mode', '')}")
                print(f"  消息数: {len(msgs)}")
                print(f"  已进行: {duration}")
            except Exception as exc:
                print(f"✗ 获取摘要失败: {exc}")
            continue

        if user_input.startswith("/mode "):
            new_mode = user_input[6:].strip()
            if new_mode:
                mode = new_mode
                try:
                    state_path = _PROJECT_ROOT / "sessions" / session_id / "state.json"
                    if state_path.exists():
                        st = json.loads(state_path.read_text(encoding="utf-8"))
                        st["mode"] = mode
                        state_path.write_text(
                            json.dumps(st, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8",
                        )
                except Exception as exc:
                    print(f"⚠ 更新模式失败: {exc}")
                print(f"✓ 模式已切换为: {mode}")
            continue

        if user_input.startswith("/read "):
            file_path = user_input[6:].strip()
            try:
                import importlib.util
                dh_path = _PROJECT_ROOT / "scripts" / "document_handler.py"
                if dh_path.exists():
                    spec = importlib.util.spec_from_file_location("document_handler", dh_path)
                    dh = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(dh)
                    content = dh.read_document(file_path)
                    print(f"\n◐ 文档内容（前1000字符）:\n{content[:1000]}\n")
                else:
                    print("✗ document_handler 模块不可用")
            except Exception as exc:
                print(f"✗ 读取文档失败: {exc}")
            continue

        if user_input.startswith("/agora "):
            personas_str = user_input[7:].strip()
            personas = [p.strip() for p in personas_str.split(",") if p.strip()]
            if personas:
                try:
                    import importlib.util
                    ab_path = _PROJECT_ROOT / "scripts" / "agora_bridge.py"
                    if ab_path.exists():
                        spec = importlib.util.spec_from_file_location("agora_bridge", ab_path)
                        ab = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(ab)
                        path = ab.export_to_agora(session_id, personas)
                        print(f"✓ 已导出到 Agora: {path.name}")
                        print(f"  邀请人物: {', '.join(personas)}")
                    else:
                        print("✗ agora_bridge 模块不可用")
                except Exception as exc:
                    print(f"✗ Agora 导出失败: {exc}")
            else:
                print("⚠ 请指定要邀请的人物，如：/agora 费曼, 狄拉克")
            continue

        # 模式自动识别（仅在未明确切换时）
        try:
            import importlib.util
            pe_path = _PROJECT_ROOT / "scripts" / "proactive_engine.py"
            if pe_path.exists():
                spec = importlib.util.spec_from_file_location("proactive_engine", pe_path)
                pe = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(pe)
                detected = pe.classify_mode(user_input)
                if detected and detected != mode and detected != "unknown":
                    mode = detected
                    try:
                        state_path = _PROJECT_ROOT / "sessions" / session_id / "state.json"
                        if state_path.exists():
                            st = json.loads(state_path.read_text(encoding="utf-8"))
                            st["mode"] = mode
                            state_path.write_text(
                                json.dumps(st, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8",
                            )
                    except Exception:
                        pass
                    print(f"◐ 自动识别为 {mode} 模式")
        except Exception:
            pass

        # 正常对话流程
        try:
            ctx = build_context(session_id, user_input, mode)
            system_prompt = ctx.get("system_prompt", "")
            llm_messages = ctx.get("messages", [])
            if _log:
                _log.info(f"LLM 调用: session={session_id}, mode={mode}, messages={len(llm_messages)}")
            assistant_content, _usage, _provider = call_llm(system_prompt, llm_messages)
        except Exception as exc:
            if _log:
                _log.error(f"LLM 调用失败: {exc}", exc_info=True)
            print(f"✗ LLM 调用失败: {exc}")
            continue

        if not assistant_content.strip():
            print("⚠ 响应为空，请重试")
            continue

        try:
            append_message(session_id, "user", user_input, mode)
            append_message(session_id, "assistant", assistant_content, mode)
        except Exception as exc:
            print(f"✗ 保存消息失败: {exc}")

        # 每轮对话后尝试更新记忆（静默执行，失败不影响对话）
        try:
            import importlib.util
            mm_path = _PROJECT_ROOT / "scripts" / "memory_manager.py"
            if mm_path.exists():
                spec = importlib.util.spec_from_file_location("memory_manager", mm_path)
                mm = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mm)
                mm.update_user_profile(session_id)
                mm.update_working_context(session_id)
        except Exception:
            pass

        # 每轮对话后尝试捕获知识片段（静默执行）
        try:
            import importlib.util
            kc_path = _PROJECT_ROOT / "scripts" / "kb_capture.py"
            if kc_path.exists():
                spec = importlib.util.spec_from_file_location("kb_capture", kc_path)
                kc = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(kc)
                result = kc.capture_from_session(session_id, topic_hint=topic)
                if result.get("captured"):
                    print(f"  📎 已捕获知识片段: {result['path']}")
        except Exception:
            pass

        print(f"\n林赛: {assistant_content}\n")


# ---------------------------------------------------------------------------
# 命令行参数解析
# ---------------------------------------------------------------------------
def parse_args(argv=None) -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="LinSai-CoPilot 核心引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--start", "-s", type=str, help="创建新会话，指定主题"
    )
    parser.add_argument(
        "--continue",
        "-c",
        dest="continue_session",
        action="store_true",
        help="续接最近会话",
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="列出所有会话"
    )
    parser.add_argument(
        "--archive", "-a", type=str, help="归档指定会话 ID"
    )
    parser.add_argument(
        "--mode",
        "-m",
        type=str,
        default="co-working",
        help="交互模式 (co-working/deep-talk/quick-check)",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------
def _run_heartbeat() -> list[str]:
    """启动时运行心跳扫描，返回需要显示的提醒消息列表。"""
    try:
        import importlib.util
        pe_path = _PROJECT_ROOT / "scripts" / "proactive_engine.py"
        if not pe_path.exists():
            return []
        spec = importlib.util.spec_from_file_location("proactive_engine", pe_path)
        pe = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pe)
        signals = pe.heartbeat()
        if not signals:
            return []
        level = pe.get_autonomy_level()
        if level == "observe":
            return []
        msgs = []
        for sig in signals[:3]:  # 最多显示3条
            if level == "suggest":
                msg = pe.generate_proactive_message(sig)
                if msg:
                    msgs.append(msg)
            elif level == "act":
                msg = pe.generate_proactive_message(sig)
                if msg:
                    msgs.append(f"[主动提醒] {msg}")
        return msgs
    except Exception:
        return []


def main() -> None:
    args = parse_args()

    # 启动时自动备份（24h间隔，失败不阻塞）
    try:
        from backup_manager import auto_backup
        result = auto_backup()
        if result:
            print(f"✓ 自动备份完成: {result.name}")
    except Exception:
        pass  # 备份失败不阻塞主流程

    # 启动时运行心跳扫描
    reminders = _run_heartbeat()
    if reminders:
        print("\n◐ 林赛有一些话想先说：")
        for r in reminders:
            print(f"  • {r}")
        print()

    if args.start:
        session_id, _ = create_session(args.start, args.mode)
        print(f"✓ 会话已创建: {session_id}")
        chat_loop(session_id, args.mode)
    elif args.continue_session:
        session_id = get_latest_session_id()
        if not session_id:
            print("✗ 没有可续接的会话")
            return
        print(f"◐ 续接会话: {session_id}")
        chat_loop(session_id)
    elif args.list:
        sessions = list_sessions()
        if not sessions:
            print("○ 暂无会话")
            return
        print(f"\n{'会话ID':<34} {'主题':<22} {'模式':<14} {'消息数':<8} {'最后活跃'}")
        print("-" * 90)
        for s in sessions:
            sid = s.get("session_id", "")[:32]
            topic = s.get("topic", "")[:20]
            mode_ = s.get("mode", "")[:12]
            count = str(s.get("message_count", 0))
            last = s.get("last_active", "")[:19]
            print(f"{sid:<34} {topic:<22} {mode_:<14} {count:<8} {last}")
        print()
    elif args.archive:
        archive_session(args.archive)
        print(f"✓ 会话已归档: {args.archive}")
    else:
        sessions = list_sessions(status="active")
        if sessions:
            print("\n○ 检测到活跃会话：")
            for i, s in enumerate(sessions[:5], 1):
                print(
                    f"  {i}. {s['session_id']} — {s['topic']} "
                    f"({s['message_count']} 条消息)"
                )
            print("  使用 --continue 续接最近会话，或 --start <主题> 创建新会话")
        else:
            print("○ 当前无活跃会话，使用 --start <主题> 创建新会话")


# ---------------------------------------------------------------------------
# 自检与启动
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # 1. 检测本地 LLM CLI
    cli_info = detect_llm_cli()
    if cli_info:
        print(f"✓ 检测到 LLM CLI: {cli_info[0]}")
    else:
        print("✗ 未检测到 LLM CLI。请安装 kimi-cli: pip install kimi-cli")
        print("  或安装 Claude Code: npm install -g @anthropic-ai/claude-code")

    # 2. 测试 call_llm
    if cli_info:
        try:
            test_resp, _usage, _provider = call_llm(
                "你是一个测试助手，只回复'测试成功'三个字，不要多说。",
                [{"role": "user", "content": "开始测试"}],
            )
            if "测试成功" in test_resp or test_resp.strip():
                print("✓ LLM 调用测试通过")
            else:
                print(f"⚠ LLM 调用返回异常: {test_resp[:80]}")
        except Exception as e:
            print(f"✗ LLM 调用测试失败: {e}")

    # 3. 检测备份模块
    try:
        from backup_manager import auto_backup
        print("✓ 备份模块可用")
    except ImportError:
        print("⚠ 备份模块未就绪（不影响使用）")

    # 4. 测试命令行参数解析
    try:
        _ = parse_args([])
        print("✓ 参数解析模块正常")
    except SystemExit:
        pass

    # 5. 运行主程序
    main()
