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
| `context_builder.py` | ✅ 已完成 | 425 | 上下文组装：人格 + 记忆 + 知识库 + 技能 + 会话历史 + 预算控制 |
| `copilot_engine.py` | ✅ 已完成 | 650 | 核心引擎：LLM调用（多Provider）、交互式对话、CLI参数解析、工具调用 |
| `memory_manager.py` | ✅ 已完成 | 465 | 用户画像提取、工作上下文、长期记忆索引、记忆片段、会话摘要 |
| `task_manager.py` | ✅ 已完成 | 448 | 任务 CRUD、状态流转、进度/子任务/里程碑、截止日期追踪 |
| `proactive_engine.py` | ✅ 已完成 | 465 | 心跳扫描、主动提醒、压力信号检测、三级自主控制、模式识别 |
| `document_handler.py` | ✅ 已完成 | 486 | Markdown/TXT读取、PDF基础提取、代码分析、文档摘要、参考文献索引 |
| `agora_bridge.py` | ✅ 已完成 | 208 | Agora群聊系统桥接：上下文导出/导入、历史人物召唤 |
| `llm_router.py` | ✅ 已完成 | 565 | 多模型路由：MiniMax API + Kimi CLI + Claude CLI，自动降级 |
| `usage_tracker.py` | ✅ 已完成 | 210 | Token 用量追踪：API精确统计 + CLI字符估算，多维度查询 |
| `skill_manager.py` | ✅ 已完成 | ~330 | 技能系统：扫描 skills/ 目录，关键词匹配，上下文注入，自动/手动模式，配置管理，模糊搜索 |
| `knowledge_base.py` | ✅ 已完成 | ~1380 | 知识库引擎：raw/wiki分层、frontmatter、知识图谱、生长机制、别名、健康度 |
| `kb_capture.py` | ✅ 已完成 | ~317 | 对话自动捕获：技术参数检测、零LLM开销 |
| `kb_maintenance.py` | ✅ 已完成 | ~260 | 批处理维护：索引重建、孤儿清理、候选报告、周维护 |
| `research_profiler.py` | ✅ 已完成 | ~250 | 研究方向感知器：TF-IDF关键词提取、7天自动重建、漂移检测 |
| `external_fetcher.py` | ✅ 已完成 | ~380 | 统一信息获取：deepxiv(arXiv) + 联网检索 + raw扫描 + 四级评分 |
| `learning_engine.py` | ✅ 已完成 | ~980 | 自主学习核心：蒸馏/精读/概念整合/图谱扩展/成本追踪/回滚 |
| `quality_evaluator.py` | ✅ 已完成 | ~520 | 质量评估引擎：规则+LLM评估、三级决策、对抗蒸馏、待审队列 |
| `tool_engine.py` | ✅ 已完成 | 322 | 子代理调用：5工具注册、安全白名单、解析-执行-回传 |
| `logger.py` | ✅ 已完成 | ~140 | 统一日志：控制台彩色输出 + 文件按日期轮转，DEBUG/INFO/WARNING/ERROR |
| `web_server.py` | ✅ 已完成 | ~940 | Web 服务器：HTTP + SSE + API路由 + 文件上传 + 知识库API |
| `backup_manager.py` | ✅ 已完成 | — | 数据备份/恢复/清理 |
| `upgrade.py` | ✅ 已完成 | — | 安全升级标准流程 |
| `self_test.py` | ✅ 已完成 | ~200 | 内测统一入口：全量回归测试 / 分维度 / JSON 输出 / 程序化调用 |
| `deep_audit.py` | ✅ 已完成 | ~500 | 深度评估脚本：9维度架构稳定性审查 |
| `learning_quality_tracker.py` | ✅ 已完成 | ~500 | 交互质量追踪器：质量评估/记忆召回率测试/人格漂移检测 |

**测试套件（`scripts/tests/`）**

| 脚本 | 说明 |
|------|------|
| `test_runner.py` | 轻量测试框架：隔离环境、Monkey-patch、中文报告 |
| `test_core.py` | 核心模块单元测试（34 个检查点） |
| `test_scenarios.py` | 场景剧本测试 — 5 类影子用户（16 个检查点） |
| `test_persona.py` | 人格一致性静态抽检（38 个检查点） |
| `test_e2e_learning.py` | 端到端 arXiv 链路验证（来源链接注入检查） |
| `test_e2e_learning_full.py` | 三来源（arXiv/web/raw）端到端完整链路验证 |
| `upgrade_wiki_for_obsidian.py` | 一次性升级脚本：为现有 wiki 注入双向链接 |

**总计：29 个主脚本 + 6 个测试脚本，约 11000+ 行 Python，零第三方依赖。**

---

*版本：2.0.0*  
*日期：2026-05-14*
