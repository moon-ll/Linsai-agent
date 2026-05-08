# scripts/ — 工具脚本

本目录存放 LinSai-CoPilot 的所有 Python 工具脚本。

## 开发规范

- **仅使用 Python 标准库**，禁止引入第三方依赖
- 头部必须包含中文 docstring，说明用途和用法示例
- 路径处理使用 `pathlib.Path`
- `PROJECT_ROOT` 统一通过 `Path(__file__).parent.parent` 推导
- 输出使用中文，状态图标统一：`✓` 成功、`✗` 失败、`⚠` 警告、`○` 待处理、`◐` 进行中
- JSON 文件必须 `ensure_ascii=False, indent=2`
- 时间戳统一使用 UTC ISO 格式：`%Y-%m-%dT%H:%M:%SZ`
- 单个脚本代码量 ≤ 500 行

## 脚本清单

| 脚本 | 状态 | 行数 | 说明 |
|------|------|------|------|
| `session_manager.py` | ✅ 已完成 | 382 | 会话创建、存档、加载、列出、归档 |
| `context_builder.py` | ✅ 已完成 | 337 | 上下文组装：人格注入 + 记忆 + 会话历史 + 预算控制 |
| `copilot_engine.py` | ✅ 已完成 | 584 | 核心引擎：LLM调用（Claude/Kimi CLI）、交互式对话循环、CLI参数解析 |
| `memory_manager.py` | ✅ 已完成 | 465 | 用户画像提取、工作上下文、长期记忆索引、记忆片段、会话摘要 |
| `task_manager.py` | ✅ 已完成 | 380 | 任务 CRUD、状态流转、截止日期追踪、逾期检测 |
| `proactive_engine.py` | ✅ 已完成 | 465 | 心跳扫描、主动提醒、压力信号检测、三级自主控制、模式识别 |
| `document_handler.py` | ✅ 已完成 | 486 | Markdown/TXT读取、PDF基础提取、代码分析、文档摘要、参考文献索引 |
| `agora_bridge.py` | ✅ 已完成 | 208 | Agora群聊系统桥接：上下文导出/导入、历史人物召唤 |

**总计：8 个脚本，3307 行 Python，零第三方依赖。**

---

*版本：1.0*  
*日期：2026-05-08*
