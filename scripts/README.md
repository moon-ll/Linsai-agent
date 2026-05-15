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

## 核心引擎

| 脚本 | 行数 | 说明 |
|------|------|------|
| `copilot_engine.py` | 661 | 核心引擎：LLM调用、交互式对话、CLI参数解析、斜杠命令拦截 |
| `slash_commands.py` | 686 | 斜杠命令系统：/research /ingest /check /skill 等 9 个命令 |
| `tool_engine.py` | 1024 | 工具引擎：11个工具注册、权限模型、工具循环 |
| `context_builder.py` | 473 | 上下文组装：人格 + 记忆 + 知识库 + 技能 + 会话历史 + 预算控制 |

## 数据管理

| 脚本 | 行数 | 说明 |
|------|------|------|
| `session_manager.py` | 382 | 会话创建、存档、加载、列出、归档 |
| `memory_manager.py` | 465 | 用户画像提取、工作上下文、长期记忆索引、记忆片段 |
| `task_manager.py` | 448 | 任务 CRUD、状态流转、截止日期追踪 |
| `chat_archive.py` | 479 | 对话存档管理 |

## 知识库

| 脚本 | 行数 | 说明 |
|------|------|------|
| `knowledge_base.py` | 1623 | 知识库引擎：raw/wiki分层、frontmatter、知识图谱、搜索、生长机制 |
| `kb_capture.py` | 318 | 对话自动捕获：技术参数检测、零LLM开销 |
| `kb_maintenance.py` | 213 | 批处理维护：索引重建、孤儿清理 |

## LLM 路由

| 脚本 | 行数 | 说明 |
|------|------|------|
| `llm_router.py` | 587 | 多模型路由：MiniMax API + Kimi CLI + Claude CLI，自动降级 |
| `usage_tracker.py` | 210 | Token 用量追踪：多维度查询 |

## 辅助工具

| 脚本 | 行数 | 说明 |
|------|------|------|
| `document_handler.py` | 486 | Markdown/TXT读取、PDF基础提取、代码分析 |
| `agora_bridge.py` | 208 | Agora群聊桥接：上下文导出/导入 |
| `skill_manager.py` | 299 | 项目级技能系统：skills/ 目录、关键词匹配 |
| `proactive_engine.py` | 568 | 主动感知：心跳扫描、压力信号检测、主动提醒 |
| `research_profiler.py` | 398 | 研究方向感知器：TF-IDF关键词、漂移检测 |
| `external_fetcher.py` | 740 | 统一信息获取：arXiv + Wikipedia + raw扫描 |
| `learning_engine.py` | 1010 | 自主学习核心：蒸馏/精读/概念整合/图谱扩展 |
| `quality_evaluator.py` | 787 | 质量评估：规则+LLM评估、对抗蒸馏 |
| `logger.py` | 139 | 统一日志：彩色控制台 + 文件轮转 |
| `self_test.py` | 240 | 统一自检入口：88项全量回归 |

## 测试套件（`tests/`）

| 脚本 | 说明 |
|------|------|
| `test_runner.py` | 轻量测试框架：隔离环境、中文报告 |
| `test_core.py` | 核心模块单元测试（34个检查点） |
| `test_scenarios.py` | 场景剧本测试（16个检查点） |
| `test_persona.py` | 人格一致性静态抽检（38个检查点） |

**总计：23 个主脚本 + 4 个测试脚本。**

---
*版本：2.1.0*
*日期：2026-05-15*
