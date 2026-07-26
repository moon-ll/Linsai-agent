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

## 公共基础

| 脚本 | 行数 | 说明 |
|------|------|------|
| `__init__.py` | 7 | 包初始化 |
| `common.py` | 66 | 公共工具：now_utc / load_json / save_json / safe_filename / lazy_load |
| `paths.py` | 42 | 路径工具：PROJECT_ROOT 与各子目录路径常量 |
| `logger.py` | 139 | 统一日志：彩色控制台输出 + 文件按日期轮转 |
| `backup_manager.py` | 254 | 数据备份与恢复 |
| `upgrade.py` | 316 | 安全升级标准流程（检查 / 模拟 / 执行） |

## 核心引擎

| 脚本 | 行数 | 说明 |
|------|------|------|
| `copilot_engine.py` | 661 | 核心引擎：LLM调用、交互式对话、CLI参数解析、斜杠命令拦截 |
| `slash_commands.py` | 686 | 斜杠命令系统：/research /ingest /check /skill 等 9 个命令 |
| `tool_engine.py` | 966 | 工具引擎：11个工具注册、权限模型、工具循环 |
| `context_builder.py` | 608 | 上下文组装：人格 + 记忆 + 知识库 + 技能 + 会话历史 + 预算控制 |
| `web_server.py` | 321 | Web 服务器聚合器（Mixin 架构，10 路由 Mixin，160 路由） |

## 数据管理

| 脚本 | 行数 | 说明 |
|------|------|------|
| `session_manager.py` | 377 | 会话创建、存档、加载、列出、归档 |
| `memory_manager.py` | 459 | 用户画像提取、工作上下文、长期记忆索引、记忆片段 |
| `task_manager.py` | 499 | 任务 CRUD、状态流转、截止日期追踪 |
| `chat_archive.py` | 479 | 对话存档管理 |
| `project_dispatch.py` | 369 | 项目总控：意见持久化 + 执行追踪（v3.3.0） |

## 知识库

| 脚本 | 行数 | 说明 |
|------|------|------|
| `knowledge_base.py` | 534 | 知识库引擎门面（re-export 5 子模块：kb_text/kb_graph/kb_index/kb_wiki/kb_health） |
| `kb_capture.py` | 316 | 对话自动捕获：技术参数检测、零LLM开销 |
| `kb_maintenance.py` | 286 | 批处理维护：索引重建、孤儿清理、候选报告、周维护 |
| `kb_auto_sync.py` | 227 | 知识库自动同步 |
| `kb_categories.py` | 348 | 知识库分类管理 |
| `kb_importer.py` | 658 | 知识库批量导入 |
| `kb_linker.py` | 221 | 知识库关联链接 |
| `alias_learner.py` | 274 | 别名学习器：从对话学习同义词候选 |
| `growth_engine.py` | 243 | 知识生长引擎：growth_stage 流转与置信度提升 |
| `paper_pool.py` | 196 | 论文池管理 |

## 课题指导模块（v3.5）

| 脚本 | 行数 | 说明 |
|------|------|------|
| `project_manager.py` | 450 | 课题 CRUD、状态机、PROJECT-MEMORY.md 自动维护与压缩（≤100行） |
| `unit_manager.py` | 699 | 单元 CRUD、验收标准结构化数组、风险追踪、状态机 |
| `project_kb.py` | 890 | 课题分层知识库：raw/parsed/summary、TF-IDF 倒排索引、标签 |
| `project_memory.py` | 761 | 课题三级记忆：对话全文 / 片段 / 核心记忆、决策与风险记录 |
| `project_context.py` | 328 | @语法解析、跨课题检索、课题上下文构建 |
| `project_workflow.py` | 423 | 工作流编排：规划→执行→验收→完成→总结 |

## 学习与认知闭环

| 脚本 | 行数 | 说明 |
|------|------|------|
| `research_profiler.py` | 396 | 研究方向感知器：TF-IDF关键词、7天自动重建、漂移检测 |
| `external_fetcher.py` | 738 | 统一信息获取：deepxiv arXiv + 联网检索 + raw扫描 |
| `learning_engine.py` | 1007 | 自主学习核心：蒸馏/精读/概念整合/图谱扩展/成本追踪 |
| `quality_evaluator.py` | 785 | 质量评估：规则+LLM评估、对抗蒸馏、三级决策 |
| `memory_reflow.py` | 569 | 认知回流引擎：hermes→记忆提炼、冷启动、增量回流（v3.4） |
| `sync_engine.py` | 328 | 多端同步：hermes 会话/文献 → 知识库 + 认知回流 |

## LLM 路由

| 脚本 | 行数 | 说明 |
|------|------|------|
| `llm_router.py` | 611 | 多模型路由：MiniMax API + Kimi CLI + Claude CLI，自动降级 |
| `usage_tracker.py` | 208 | Token 用量追踪：多维度查询 |

## 辅助工具

| 脚本 | 行数 | 说明 |
|------|------|------|
| `document_handler.py` | 486 | Markdown/TXT读取、PDF基础提取、代码分析 |
| `project_reader.py` | 923 | 项目文件读取器：跨课题/跨目录文件聚合读取 |
| `agora_bridge.py` | 206 | Agora群聊桥接：上下文导出/导入 |
| `hermes_bridge.py` | 340 | Hermes 桥接器：cron控制/oneshot派活/团队profile状态（v6.6） |
| `hermes_pipeline.py` | 1050+ | NSFC 研究管线：六阶段全链路→7个hermes profile协作 |
| `proposal_lifecycle.py` | 1700+ | 提案生命周期：四阶段流转+对抗优化引擎+文献驱动筛选 |
| `skill_manager.py` | 299 | 项目级技能系统：skills/ 目录、关键词匹配 |
| `proactive_engine.py` | 553 | 主动感知：心跳扫描、压力信号检测、主动提醒 |
| `self_test.py` | 247 | 统一自检入口：137+207 项全量回归 |

## deepxiv 知识库流水线

| 脚本 | 行数 | 说明 |
|------|------|------|
| `deepxiv_knowledge/fetch_core.py` | ~295 | deepxiv 封装 + section TLDR 解析 |
| `deepxiv_knowledge/paper_writer.py` | ~71 | 写入 raw paper Markdown |
| `deepxiv_knowledge/checkpoint.py` | ~65 | 断点持久化 |
| `deepxiv_knowledge/schema.py` | ~46 | 论文标准结构（PAPER_SCHEMA）|
| `deepxiv_knowledge/pdf_extractor.py` | ~350 | PDF 全文提取（PyPDF2）|
| `deepxiv_knowledge/pdf_enricher.py` | ~180 | PDF 增强流水线（追加/替换 content sections）|
| `deepxiv_knowledge/run.py` | ~240 | 主入口（v6，--rebuild 支持）|
| `wiki_regenerator/paper_reader.py` | ~85 | 读取所有 raw papers |
| `wiki_regenerator/report_writer.py` | ~420 | 6 篇报告生成器 |
| `wiki_regenerator/run.py` | ~69 | wiki 重建主入口 |

## 测试套件（`tests/`）

| 脚本 | 说明 |
|------|------|
| `test_runner.py` | 轻量测试框架：隔离环境、中文报告 |
| `test_core.py` | 核心模块单元测试（137个检查点） |
| `test_scenarios.py` | 场景剧本测试（16个检查点） |
| `test_persona.py` | 人格一致性静态抽检（38个检查点） |
| `test_web_api.py` | Web API 端到端测试 |

根目录另有 `test_e2e_learning_full.py`（292 行）——三来源端到端完整链路验证脚本。

**总计：scripts/ 根目录 49 个 .py 文件（含 `__init__.py`）+ tests/ 目录 6 个 .py 文件 + deepxiv_knowledge（8 模块）/ wiki_regenerator（4 模块）两个流水线包。**

---
*版本：6.1.0*
*日期：2026-07-25*
