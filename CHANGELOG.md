# 变更记录

## v2.0.0 - 2026-05-12 林赛自主学习引擎（5 阶段完整实施）

### 新增（自主学习引擎）

- `scripts/research_profiler.py` — 研究方向感知器：从用户画像/任务/会话动态提取研究关键词
- `scripts/external_fetcher.py` — 统一信息获取接口：deepxiv(arXiv) + Wikipedia API + raw/ 扫描 + 优先级排序
- `scripts/learning_engine.py` — 自主学习核心编排器：蒸馏/精读/概念提取/知识整合/图谱扩展/成本追踪/一键回滚
- `scripts/quality_evaluator.py` — 质量评估引擎：规则评估 + LLM 评估 + 对抗性多轮蒸馏 + 用户反馈闭环
- `memory/learning-config.json` — 学习策略与配额配置（自动开关/策略/来源/成本上限）
- `memory/research-profile.json` — 研究方向关键词（动态更新）
- `memory/learning-cost.json` — 学习成本追踪（日/月/按来源/按 Provider）
- `memory/learning-quality-log.json` — 质量评分历史
- `memory/learning-pending-queue.json` — 待审队列
- `memory/learning-user-edits.json` — 用户编辑追踪
- `knowledge/.cache/` — 网络获取结果缓存（arXiv 24h / Wikipedia 7d）
- `knowledge/.backup/auto-grown/` — 生长前自动备份

### 新增（Web 前端）

- 侧边栏工具栏新增 🌱 学习管理器入口
- 学习管理器模态框：3 标签页（📜 学习日志 / 📝 待审内容 / 📊 统计）
- 设置面板新增学习策略配置：自动开关、保守/平衡/激进策略、来源勾选、日配额、成本上限
- 手动触发学习按钮（带进度反馈）

### 新增（API 端点）

- `GET /api/learning/config` — 获取学习配置
- `POST /api/learning/config` — 更新学习配置
- `GET /api/learning/status` — 学习状态（成本/配额/调用次数）
- `GET /api/learning/queue` — 待审队列
- `GET /api/learning/log` — 质量评估日志
- `POST /api/learning/trigger` — 手动触发学习周期
- `POST /api/learning/review` — 审批/拒绝待审内容

### 新增（配套文档）

- `docs/CLAUDE-CLI-ADMIN.md` — Claude CLI 人工管理指南
- `docs/prompts/quality-audit.txt` — 质量审查 prompt 模板
- `docs/prompts/maintenance-audit.txt` — 维护审查 prompt 模板
- `docs/prompts/concept-merge.txt` — 概念合并 prompt 模板
- `docs/prompts/paper-deep-read.txt` — 论文精读 prompt 模板

### 改造

- `scripts/proactive_engine.py` — heartbeat() 新增第 5 类信号 `learning_opportunity`
- `scripts/knowledge_base.py` — 扩展图谱边类型（`supported_by`/`supports`/`extends`/`contradicts`）
- `scripts/web_server.py` — 新增 `/api/learning/*` 端点
- `web/index.html` — 新增学习管理器 DOM
- `web/js/app.js` — 新增学习管理器渲染逻辑

### 验证

- 5 个新模块自检全部通过
- **全量自测 88/88 通过** ✅
- 零破坏性：所有现有功能不受影响

---

## v2.1.0 - 2026-05-15 工具协作者 + 知识库三工作流

### Phase 0 — 工具协作者（v2.1.0）
- `scripts/tool_engine.py` — 新增 `tool_run_command()` + `tool_hermes_chat()`
  - run_command: subprocess 调用 CLI（kimi/claude/hermes/python/git），cwd 限制 + 危险命令黑名单
  - hermes_chat: 调用 `hermes --profile linsai -z`，获得 LinSai 完整人格 + 记忆的深度回答
  - 权限模型：禁止逃离项目目录的命令组合

### Phase 1 — 子代理工具（v2.1.0）
- `scripts/tool_engine.py` — 新增 `tool_agent()`，通过 `claude --agent explore/coder/plan` 调用子代理
- 8 个工具完整注册：calc / file_read / file_write / task_create / knowledge_query / run_command / hermes_chat / agent

### Phase 2 — 记忆加载自动化（v2.1.0）
- `scripts/context_builder.py` — `_read_lt_mem()` 返回实际内容（最近 10 条），`_read_work_ctx()` 过滤已逾期项目

### 知识库三工作流（v2.1.0）
- `tool_knowledge_research` — 工作流1-自动增加：Hermes调研 → 编译 → 写入wiki → 建双向链接
- `tool_knowledge_ingest` — 工作流2-手动增加：编译raw文件夹 → 建立双向链接 → 健康检查
- `tool_knowledge_create` — 工作流3-对话生长：创建概念存根 → 记录上下文
- 外部导入规范：raw/ 三级分类（papers/notes/webclips），林赛负责所有后续编译管理

### 斜杠命令系统（v2.1.0）
- `scripts/slash_commands.py` — 统一命令入口（719行）
  - 解析器支持 `/research` 和 `/research:topic:depth` 两种格式
  - 44 个思维视角动态加载（~/.claude/skills/）
  - `/skill:<name>` 激活视角，session state 注入 prompt
  - `/research` / `/ingest` / `/check` / `/session` / `/mode` / `/read` / `/help` / `/list`
- `scripts/copilot_engine.py` — chat_loop 统一拦截 `/` 前缀

### 修复
- `knowledge_base.py` — `_load_graph()` 处理 graph.json 为空对象 `{}` 的情况
- `.gitignore` — 补充 `knowledge/captures`

---

## v1.7.3 - 2026-05-12 Obsidian 前端兼容性改造

### 新增（Obsidian 兼容）

- `knowledge/.obsidian/` — 开箱即用的 Obsidian Vault 配置
  - `app.json`：新建文件默认放入 `wiki/concepts/`，附件放入 `assets/`
  - `appearance.json`：强调色 `#2563eb`（林赛品牌蓝）
  - `core-plugins.json`：启用图谱、反向链接、标签面板、页面预览等核心插件
- `knowledge/templates/概念笔记.md` — Obsidian 模板，frontmatter 结构完整
- `knowledge/README.md` — 知识库使用指南（含 Obsidian 使用说明）
- `scripts/upgrade_wiki_for_obsidian.py` — 一次性升级脚本，为现有 wiki 文件注入双向链接

### 改造（知识库引擎）

- `scripts/knowledge_base.py` — 全面支持 Obsidian 双向链接 `[[WikiLink]]`
  - 新增 `_extract_wikilinks()` — 从正文提取 `[[链接]]`
  - 新增 `_get_aliases_for_concept()` — 从 `aliases.json` 反向查找别名
  - 新增 `_inject_wikilinks()` — 自动在正文末尾注入 `<!-- linsai-wikilinks -->` 区域，同步 frontmatter `related` 与正文 `[[链接]]`
  - `build_frontmatter()` — 优化 YAML 输出格式，字符串转义更安全，空数组正确输出 `[]`
  - `save_wiki_page()` — 保存后自动注入 wikilinks 并同步图谱
  - `save_distilled_wiki()` — 蒸馏后自动注入 wikilinks
  - `apply_growth()` — 生长后自动注入 wikilinks
  - `build_index()` / `list_raw_files()` — 新增 `_should_index()` 过滤器，排除 `.obsidian/`、`.git/`、`__pycache__/` 等隐藏目录

### 影响

- 现有 2 个 wiki 页面已通过升级脚本注入 wikilinks 区域
- 新建/更新的 wiki 页面自动获得 `[[双向链接]]`，Obsidian 图谱可正确显示概念间连接
- frontmatter 新增 `aliases` 字段（来自 `aliases.json` 映射），Obsidian 别名搜索可用
- 全量自测 88/88 通过 ✅

## v1.7.2 - 2026-05-11 内测系统 — 影子用户自动化回归测试

### 新增

- `scripts/self_test.py` — 内测统一入口，支持命令行与程序化双接口
  - 命令行：`--module` / `--scenario` / `--persona` / `--json`
  - 程序化：`from self_test import run_tests; result = run_tests(["module"])`
- `scripts/tests/test_runner.py` — 零依赖轻量级测试框架，支持隔离环境、Monkey-patch、中文报告
- `scripts/tests/test_core.py` — 核心模块单元测试（会话 / 知识库 / 技能 / 任务 / 记忆 / 上下文）
- `scripts/tests/test_scenarios.py` — 场景剧本测试（5 类影子用户：并肩工作 / 深度对话 / 快速验证 / 任务驱动 / 主动感知）
- `scripts/tests/test_persona.py` — 人格一致性静态抽检（锚点 / 结构 / 表达 DNA / 反模式）
- `skills/self-test/SKILL.md` — 内测技能封装，触发词：内测/测试/回归测试/影子用户/健康检查

### 新增（深度评估与功能测试）

- `scripts/deep_audit.py` — 9维度深度评估脚本（代码质量 / 架构拓扑 / 数据完整性 / 边界条件 / 前端资产 / LLM引擎 / 安全审查 / 文档一致性 / 性能基线）
- `docs/DEEP-AUDIT-REPORT.md` — 深度评估报告（风险评分 150/1000，0 严重 0 高 0 中）
- `docs/FUNCTIONAL-TEST-REPORT.md` — 子代理模拟用户功能测试报告（65 个检查点，Web API 15/15 通过）

### 修复

- `scripts/copilot_engine.py:461` — `call_llm()` 返回值从单值改为 3 元组解包，修复 `AttributeError`
- `scripts/copilot_engine.py:108` — `detect_llm_cli()` 遍历 `status["providers"]` 而非字典键，修复 CLI 入口崩溃
- `scripts/web_server.py` — 新增 `PUT /api/tasks/{id}/subtasks` 和 `/progress` 路由，修复前端 API 调用失败
- `scripts/web_server.py` — `os.system` 替换为 `subprocess.run`，消除命令注入风险
- `web/index.html` — 版本标签 `v1.1.0` → `v1.7.2`
- `tasks/` — 修复 8 个任务文件状态与目录不一致
- `sessions/agora_exports/` — 修复 `invited_personas` 数据类型（字符串 `"t"` → 列表 `["费曼"]`）

### 验证

- 全量测试 88/88 通过（核心 34 + 人格 38 + 场景 16），总耗时 ~0.06s
- 深度评估：0 严重 / 0 高 / 0 中 / 150 低，风险评分 150/1000
- 子代理功能测试：Web API 15/15 通过，CLI 入口恢复正常
- 测试隔离：所有写入操作在临时目录进行，零污染真实数据
- 零第三方依赖，仅使用 Python 3 标准库

---

## v1.7.1 - 2026-05-09 知识库精细化 — 从"建库"到"浮现"

### 核心改进
- **对话自动捕获** — `scripts/kb_capture.py`
  - 检测技术参数（3个以上数字+单位）、用户明确请求（"记下来"）、工作模式长消息
  - 零 LLM 开销，保存到 `knowledge/captures/`
- **智能检索触发器** — `scripts/knowledge_base.py` 的 `should_search_knowledge()`
  - 闲聊/问候自动跳过，技术讨论才检索知识库
  - 节省 40-100% 的每轮对话知识库上下文开销
- **分级上下文注入** — `scripts/context_builder.py`
  - 高相关（score≥0.8）：注入全文摘要 300 字
  - 中相关（0.4≤score<0.8）：只注入标题 + 一句话 + 路径链接
  - 低相关（score<0.4）：不注入
- **紧凑注入格式** — `[KB] 标题 [source:stage]: 摘要`（节省 ~30% prompt 空间）
- **别名映射系统** — `knowledge/aliases.json`
  - 查询时自动展开同义词（如 HHG → 高次谐波产生）
- **相似概念检测** — 创建 wiki stub 前检测 score>0.9 的相似条目，防膨胀
- **批处理维护窗口** — `scripts/kb_maintenance.py`
  - `--weekly` 一键维护：重建索引 + 清理孤儿 + 候选报告 + 健康度
  - `--reindex` / `--orphans` / `--candidates` / `--health` / `--captures`
- **知识库健康仪表盘** — Web 界面新增"健康度"和"别名"标签页
  - 健康度：总条目、生长分布、图谱状态、本周新增、待处理项
  - 别名管理：增删改别名映射，实时保存
- **移除 auto_distill 默认触发** — 蒸馏/生长改为用户控制，节省 80%+ LLM 调用

### 文件变更
- 新增：`scripts/kb_capture.py`（317 行，自检通过）
- 新增：`scripts/kb_maintenance.py`（260 行，自检通过）
- 新增：`knowledge/aliases.json`
- 修改：`scripts/knowledge_base.py`（+216 行：别名、相似检测、健康度、智能触发）
- 修改：`scripts/context_builder.py`（分级注入、紧凑格式、预算 2000→1200）
- 修改：`scripts/copilot_engine.py`（对话后自动调用 capture）
- 修改：`scripts/web_server.py`（+94 行：aliases/captures/health/maintenance API）
- 修改：`web/js/app.js`（+158 行：健康度/别名标签页、维护按钮、相似概念提示）
- 修改：`web/css/style.css`（+69 行：仪表盘和别名样式）
- 修改：`web/index.html`（新增 2 个标签页和面板）

---

## v1.7.0 - 2026-05-08 知识库系统重构（raw/wiki 分层 + 知识图谱 + 生长机制）

### 架构重构（借鉴 Karpathy 笔记系统）
- **目录结构重组**：`knowledge/` 分为 `raw/`（用户原始材料）和 `wiki/`（林赛研究笔记）
  - `raw/papers/` — 论文 PDF/笔记
  - `raw/notes/` — 用户手写笔记
  - `raw/webclips/` — 网页剪藏
  - `wiki/concepts/` — 核心概念
  - `wiki/methods/` — 实验方法
  - `wiki/people/` — 学者评价
  - `wiki/papers/` — 论文精读
  - `wiki/projects/` — 项目聚合

### 新增核心模块
- **Wiki 页面管理**（`scripts/knowledge_base.py`）
  - `parse_frontmatter()` / `build_frontmatter()` — YAML frontmatter 解析与生成
  - `get_wiki_page()` / `list_wiki_pages()` / `save_wiki_page()` / `delete_wiki_page()` — CRUD
  - 标准 wiki 格式：YAML frontmatter + Markdown，林赛第一人称视角
  - 关键字段：`growth_stage`（seedling/growing/mature/archived）、`confidence`（0-1）、`related`（关联概念）

- **知识图谱**（`knowledge/graph.json`）
  - `update_graph_node()` / `add_graph_edge()` — 节点/边管理
  - `get_related_concepts()` — 通过图谱拉取关联知识（支持深度遍历）
  - `get_graph_summary()` — 图谱概览（节点数、边数、生长阶段分布）

- **生长日志**（`knowledge/growth-log.json`）
  - `log_growth()` — 记录每次创建/更新/关联/提炼/纳入事件
  - `get_growth_log()` — 按目标或时间范围查询
  - `get_growth_candidates()` — 获取待生长概念列表（seedling 阶段）

- **raw → wiki 提炼流程**
  - `ingest_raw()` — 将 raw 文件纳入系统，记录日志，可选自动触发提炼
  - `distill_raw_to_wiki()` — 生成提炼 prompt（供 LLM 使用）
  - `save_distilled_wiki()` — 保存 LLM 提炼结果，自动更新图谱和日志
  - 五种 wiki 类型的提炼模板：concepts / methods / people / papers / projects

- **交互触发生长机制**
  - `create_wiki_stub()` — 对话中遇到新概念时自动创建 seedling stub
  - `grow_wiki_prompt()` — 生成 wiki 丰满 prompt（供 LLM 使用）
  - `apply_growth()` — 应用 LLM 生成的丰满内容，更新生长阶段

### 索引系统增强
- `build_index()` — 统一索引 raw + wiki 目录
- `search()` — 支持 `source="all"|"raw"|"wiki"` 过滤，wiki 结果加权（×1.2），mature 再加权（×1.1）
- `get_enriched_context()` — 增强上下文：搜索结果 + 图谱关联知识 + 缺失概念检测
- `get_index_status()` — 返回 raw_count / wiki_count / chunks / graph 概览

### 上下文构建增强
- `context_builder.py` — `_read_knowledge_context()` 使用 `get_enriched_context()`
  - 搜索结果标注来源（📚 raw / 📝 wiki）和生长阶段
  - 通过图谱拉取关联知识（轻量注入）
  - **缺失概念检测**：如果用户提到知识库中没有的概念，林赛会标注"认知边界"，邀请一起记录
  - 体现"知识库是林赛的可靠知识来源，而非额外记忆负担"

### API 端点（大量新增）
- `GET /api/knowledge/raw` — 列出 raw 文件
- `GET /api/knowledge/wiki` — 列出 wiki 页面（支持 `?type=` 过滤）
- `GET /api/knowledge/wiki/{path}` — 获取单个 wiki 页面（含 frontmatter + body）
- `DELETE /api/knowledge/wiki/{path}` — 删除 wiki 页面（清理图谱关联）
- `GET /api/knowledge/graph` — 知识图谱概览
- `GET /api/knowledge/related?q=...` — 关联概念查询
- `GET /api/knowledge/growth-log?limit=N` — 生长日志
- `GET /api/knowledge/growth-candidates` — 待生长概念
- `GET /api/knowledge/enriched?q=...` — 增强上下文（搜索+关联+缺失检测）
- `POST /api/knowledge/ingest` — 纳入 raw 文件
- `POST /api/knowledge/wiki` — 创建/更新 wiki 页面
- `POST /api/knowledge/stub` — 创建概念 stub
- `GET /api/knowledge/search` — 增强：支持 `?source=` 和 `?top_k=` 参数

### Web 前端增强
- 设置面板新增"📚 知识库管理器"按钮
- 知识库管理器模态框：5 个标签页
  - 📊 **概览**：统计卡片（raw/wiki/段落/节点/边/待生长）+ 生长阶段分布
  - 📄 **Raw**：按分类（论文/笔记/剪藏）浏览 raw 文件
  - 📝 **Wiki**：按类型过滤浏览 wiki 页面，点击打开详情
  - 🔗 **图谱**：节点/边统计 + 生长阶段分布
  - 🌱 **生长**：待生长概念列表 + 最近生长日志
- Wiki 详情模态框：frontmatter 元信息 + Markdown 渲染（标题/列表/引用/代码）
- 支持"➕ 新建概念 Stub"交互

### 文档
- `knowledge/README.md` — 完整知识库使用指南（设计理念、目录结构、wiki 格式、使用方式）

## v1.6.0-M3 - 2026-05-08 子代理调用系统

### 新增
- **子代理调用系统**
  - `scripts/tool_engine.py` — 新建模块（300行）
    - 工具注册表：`file_read`, `file_write`, `calc`, `task_create`, `knowledge_query`
    - 严格安全边界：
      - `file_read`: 只能读项目目录内文件
      - `file_write`: 只能写 `memory/`, `sessions/`, `tasks/`, `knowledge/`
      - `calc`: `ast.parse` 白名单机制，仅允许数学运算节点，禁止导入/系统调用
    - 工具调用协议：`@@tool:name@@\n{json}\n@@end@@`
    - `parse_tool_calls()` / `execute_tool_calls()` / `strip_tool_calls()`
  - `scripts/copilot_engine.py` — 新增 `call_llm_with_tools()`
    - 执行流程：注入工具说明 → 第一次 LLM 调用 → 解析工具调用 → 执行工具 → 结果回传 → 第二次 LLM 调用 → 最终回复
    - 无工具调用时只消耗一次 LLM 调用（性能无损）
  - `scripts/web_server.py` — SSE 流式支持工具事件
    - 前端收到 `{"type": "tools", "calls": [...]}` 事件时显示工具调用提示
  - `persona/lin-sai-persona.md` — 追加"子代理调用"角色说明
    - 教会林赛何时使用工具、如何分解任务、调用格式
  - Web 界面：消息气泡旁显示 `🔧 调用工具: calc, knowledge_query` 提示
  - API：`GET /api/tools` — 列出可用工具

### 新增
- **本地知识库**
  - `scripts/knowledge_base.py` — 新建模块（300行）
    - 纯标准库实现：中文分词（单字+双字+四字窗口）、英文单词提取
    - 文档分块：按段落切分，每块 ≤500 字符
    - 倒排索引 + TF-IDF 检索
    - 增量索引：只更新修改过的文档
    - 数据存储：`knowledge/index.json`
  - `knowledge/` 目录：用户放入 .md/.txt/.rst 文件即可被索引
  - 示例文档：`knowledge/solid_hhg_basics.md`（固体HHG基础）
  - `context_builder.py` 自动检索：用户输入自动匹配 Top-2 相关知识段落注入 system_prompt
  - Web 界面：设置面板显示索引状态，支持一键重建索引
- **任务进度跟踪增强**
  - `scripts/task_manager.py` 增强：
    - 任务 JSON 新增 `progress` (0-100)、`subtasks`、 `milestones` 字段
    - `update_progress()` — 更新进度，自动检测完成（progress=100 → status=completed）
    - `add_subtask()` / `toggle_subtask()` — 子任务 CRUD
    - `_recalc_progress()` — 根据子任务完成数自动计算父任务进度
  - Web 界面：
    - 右侧任务面板改为**三列看板**（待办 / 进行中 / 已完成）
    - 任务卡片显示进度条 + 子任务完成数（如 `2/5`）
    - 点击任务展开详情模态框：进度滑块、子任务勾选、里程碑列表
  - API 端点：
    - `GET /api/tasks/{id}` — 任务详情
    - `PUT /api/tasks/{id}/progress` — 更新进度
    - `PUT /api/tasks/{id}/subtasks` — 添加/切换子任务
- **知识库 API**
  - `GET /api/knowledge` — 索引状态
  - `GET /api/knowledge/search?q=...` — TF-IDF 检索
  - `POST /api/knowledge/reindex` — 重建索引

### 修改
- `scripts/context_builder.py` — 新增 `knowledge` 预算项（2000字符），知识检索结果参与预算分配
- `scripts/web_server.py` — 新增知识库和任务管理 API

## v1.6.0-M1 - 2026-05-08 Token 统计 + 技能系统

### 新增
- **Token 用量统计**
  - `scripts/usage_tracker.py` — 新建模块（200行）
    - API Provider 精确统计（从 HTTP 响应解析 usage 字段）
    - CLI Provider 字符估算（utf-8 字节数 // 3）
    - 五维统计：daily / monthly / by_session / by_provider / total
    - 数据存储：`memory/usage/usage.json`
  - Web 界面：设置面板显示今日用量、总用量、各 Provider 分布
  - 顶部栏不显示（避免干扰），在设置面板中展示详细统计
- **技能系统**
  - `scripts/skill_manager.py` — 新建模块（150行）
    - 扫描 `skills/` 目录下的 SKILL.md 文件
    - 关键词触发匹配：根据用户输入自动激活相关技能
    - 技能上下文注入到 system_prompt，参与预算分配
  - `skills/` 目录结构：
    - `math-derivation/` — 数学推导辅助（量纲检查、标注假设、极限验证）
    - `code-review/` — 代码审查（可读性、边界情况、性能）
    - `experiment-design/` — 实验方案设计（先画框图、风险预判、备用方案）
  - Web 界面：
    - 设置面板显示所有可用技能及触发条件
    - 输入框实时检测：顶部栏显示 `🎯 math-derivation` 等激活技能
    - 300ms 防抖，避免频繁请求
- **API 端点**
  - `GET /api/usage` — 用量摘要（daily + total + by_provider）
  - `GET /api/usage/daily` — 今日用量
  - `GET /api/skills` — 列出所有技能
  - `GET /api/skills/active?q=...` — 查询输入激活的技能

### 修改
- `scripts/llm_router.py` — `call_llm()` 返回 `(text, usage_dict, provider_name)`，支持用量追踪
- `scripts/copilot_engine.py` — 适配新返回值格式
- `scripts/context_builder.py` — 新增 `skills` 预算项（2000字符），技能上下文参与分配与截断
- `scripts/web_server.py` — 对话后自动记录 token 用量；新增 usage/skills API

## v1.5.2 - 2026-05-08 think 过滤 + CLI/API 切换 + 聊天记录查看

### 新增
- **过滤 LLM 推理标签 `<think>`**
  - `scripts/llm_router.py` 新增 `_strip_think_tags()` 函数，使用栈算法处理嵌套标签
  - 所有 Provider（CLI + API）返回的内容自动过滤 think 标签，对话更干净
- **Provider 选择持久化**
  - 手动切换的 Provider 保存到 `memory/llm-config.json`，服务器重启后保留
  - 新增 `💻 CLI 自动` 选项：强制使用第一个可用的 CLI Provider（claude/kimi）
  - 设置面板同时显示所有 Provider（包括不可用的），灰色标记，让用户知道有哪些选择
- **聊天记录查看优化**
  - 修复遗漏的 `chat-archive-header` HTML 元素（v1.4.1 引入的 `viewArchiveSession` 功能）
  - 点击会话加载后，消息数 > 3 时显示提示条：`↑ 已加载 X 条消息，向上滚动查看历史`（8 秒后自动消失）
  - 归档浏览头部显示会话主题、消息数、模式，提供 `✕ 关闭浏览` 按钮返回对话

### 修复
- `scripts/copilot_engine.py` / `scripts/web_server.py` — 补全遗漏的 `import llm_router as lr`
- `scripts/copilot_engine.py` — `detect_llm_cli()` 延迟初始化，避免模块导入时循环依赖
- `scripts/web_server.py` — `POST /api/switch-provider` 支持 `cli_auto` 特殊值
- **`scripts/llm_router.py` — 修复 CLI 检测被 API 配置阻塞的 bug**：原逻辑"没有 API 时才检测 CLI"改为"始终检测 CLI"，确保同时配置了 API 和安装了 CLI 时，两者都能被识别

## v1.5.1 - 2026-05-08 手动 Provider 切换

### 新增
- **Web 界面手动切换 Provider**
  - 顶部栏新增 `provider-badge`，实时显示当前使用的模型/CLI（点击打开设置面板）
  - 设置面板中 LLM Provider 区域改为 radio 按钮列表，支持选择：
    - `🔄 自动选择`（默认）
    - 每个可用 Provider（显示 ✓/✗ 可用状态、API/CLI 类型、模型名）
  - 切换后即时生效，下次对话使用新 Provider
- **新 API 端点**
  - `GET /api/providers` — 返回所有 Provider 状态列表
  - `GET /api/providers/current` — 返回当前选中的 Provider（`auto` 或具体名称）
  - `POST /api/switch-provider` — 手动切换 Provider（与 `/api/llm-provider` 兼容）

### 修复
- `scripts/web_server.py` / `scripts/copilot_engine.py` — 补全遗漏的 `import llm_router as lr`
- `scripts/copilot_engine.py` — `detect_llm_cli()` 改为延迟初始化，避免模块导入时循环依赖

## v1.5.0 - 2026-05-08 多模型路由 + MiniMax API 支持

### 新增
- `scripts/llm_router.py` — 多模型路由管理器（350行）
  - 支持 CLI 后端：claude, kimi
  - 支持 HTTP API 后端：OpenAI 兼容格式（MiniMax, DeepSeek, Groq 等）
  - 自动检测 `.env` 文件中的 API Key，自动注册 Provider
  - **策略系统**：priority（优先级）/ round_robin（轮询）/ 自动降级
  - **限流自动降级**：HTTP 429 触发自动切换到下一个 Provider
  - 健康检查与失败计数
- **零第三方依赖**：HTTP API 调用使用 Python 标准库 `urllib.request`
- **安全配置**：
  - `.env` 和 `memory/llm-config.json` 已加入 `.gitignore`，API Key 永不进入 Git
  - 环境变量优先于配置文件

### 接入修改
- `copilot_engine.py` — `call_llm()` 迁移到 llm_router，保留兼容接口
- `chat_archive.py` — 关键词提炼改用 llm_router
- `web_server.py` — 新增 `GET /api/llm-status` 接口
- Web 界面 — 设置面板显示当前 LLM Provider 状态

### 使用方式
```bash
# 方式 1：项目根目录创建 .env 文件
cat > .env << 'EOF'
MINIMAX_API_KEY=your_key_here
MINIMAX_MODEL=MiniMax-M2.7
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
EOF

# 方式 2：环境变量
export MINIMAX_API_KEY=your_key_here

# 启动后自动检测并优先使用 API
python3 scripts/web_server.py
```

---

## v1.4.0 - 2026-05-08 聊天记录浏览器 + 智能归档

### 新增
- `scripts/chat_archive.py` — 聊天记录智能归档系统（400行，4项自检通过）
  - **关键词提炼**：本地词频统计 + LLM 语义提炼，双阶段合并去重
  - **跨会话搜索**：遍历所有 sessions/ 全文匹配，按匹配度排序
  - **全局索引**：`memory/chat-archive-index.json` 汇总所有会话元信息
  - 每个会话目录下自动生成 `keywords.json` 缓存
- **Web 界面聊天记录浏览器**
  - 左侧会话列表显示关键词标签（hover 可点击搜索）
  - 点击任意历史会话 → 进入只读模式查看完整聊天记录
  - "返回当前会话"按钮，一键切回活跃对话
  - 新增"聊天记录"侧边栏：跨会话全文搜索，结果点击跳转
- **后端 API 扩展**
  - `GET /api/sessions/<id>/keywords` — 获取会话关键词
  - `GET /api/history?q=...` — 跨会话全文搜索
  - `GET /api/archive-index` — 获取归档索引

### 设计决策
- **存档与记忆分离**：聊天记录 = 微信历史（完整保留，随时翻阅）；林赛记忆 = 人脑提炼（精简、会遗忘）
- 中文分词采用简单正则（英文术语 + 中文2-8字词组），零第三方依赖
- LLM 关键词提炼仅在首次访问时触发，后续读缓存

---

## v1.3.0 - 2026-05-08 Web 界面第二批 + 启动快捷方式

### 新增
- **文件上传图形化**
  - 拖拽上传区域 + 点击选择按钮
  - 支持文本文件（.md/.txt）直接读取，二进制文件 Base64 传输
  - 上传进度条，完成后自动在对话中插入文件引用卡片
  - 上传后自动更新文献索引和右侧栏引用列表
- **Agora 集成按钮**
  - 点击 `/agora` 弹出 20 位历史人物选择面板（费曼、狄拉克、爱因斯坦等）
  - 多选人物，一键导出到 Agora 群聊格式
- **消息编辑/删除**
  - 用户消息 hover 显示编辑/删除按钮
  - 编辑后实时更新 DOM 和持久化存储
  - 删除前确认，避免误操作
- **启动快捷方式**
  - `scripts/launch.sh` — 一键启动脚本，检测端口占用，自动打开浏览器
  - `scripts/LinSai-CoPilot.command` — macOS 双击启动（可放桌面）
- **文献列表 API** — `/api/references` 实时显示已上传文档

### 后端增强
- `web_server.py` 新增 API：
  - `POST /api/upload` — 文件上传（JSON base64 方式）
  - `POST /api/agora` — Agora 上下文导出
  - `PUT /api/sessions/<id>/messages/<msg_id>` — 消息编辑
  - `DELETE /api/sessions/<id>/messages/<msg_id>` — 消息删除
  - `GET /api/references` — 文献列表
- 新增辅助函数：`_handle_upload`、`_edit_message`、`_delete_message`、`_list_references`

---

## v1.2.0 - 2026-05-08 Web 界面与浏览器交互

### 新增
- `scripts/web_server.py` — Web 服务器（HTTP + SSE + API路由，330行，4项自检通过）
  - ThreadingHTTPServer 并发处理，零第三方依赖
  - REST API：会话 CRUD、消息历史、任务列表、主动提醒、版本信息
  - SSE 流式输出：LLM 回复逐句切分模拟打字效果
  - 复用现有引擎：context_builder + copilot_engine.call_llm()
- `web/index.html` — 单页应用入口（6大功能区块）
- `web/css/style.css` — 双主题样式系统（深色/浅色/自动跟随系统）
  - CSS 变量驱动，切换无闪烁
  - 消息气泡、代码块、Markdown 渲染、滚动条美化
  - 响应式布局：移动端侧边栏折叠、触摸优化
- `web/js/app.js` — 原生 JavaScript 前端逻辑（450行）
  - 会话管理：搜索、新建、切换、侧边栏渲染
  - 聊天界面：消息气泡、Markdown 轻量渲染器、流式 SSE 接收
  - 主题管理：localStorage 持久化、系统主题监听
  - 快捷命令：/mode /read /agora /summary 按钮触发
  - 主动提醒：Toast 弹窗通知

### 设计决策
- 前端零框架：不引入 React/Vue/Angular，保持项目极简哲学
- SSE 替代 WebSocket：Python 标准库原生支持，无需额外依赖
- 模拟流式输出：现有 call_llm() 为同步调用，先获取完整回复再逐句推送

---

## v1.1.0 - 2026-05-08 版本管理与数据安全体系

### 新增
- `VERSION` 文件 — 单一版本号真相源（SemVer 规范）
- `scripts/backup_manager.py` — 用户数据备份/恢复/自动清理（243行，6项自检通过）
  - 支持手动备份、自动备份（24h间隔）、备份列表、恢复指定备份
  - 恢复前自动创建应急备份，可一键回滚
  - 自动清理旧备份（默认保留最近10个）
- `scripts/upgrade.py` — 安全升级标准流程（234行，4项自检通过）
  - 升级前强制备份 → git pull → 脚本语法验证 → 迁移检查
  - 支持 `--check` 查看版本、`--simulate` 模拟升级、`--verify` 验证完整性
- `.gitignore` — 隔离用户数据（sessions/、memory/、tasks/、references/）与代码
- `copilot_engine.py` 启动时集成自动备份（失败不阻塞主流程）

### 规范
- 版本号统一为 `1.0.0`，`source-manifest.json` 同步更新
- 用户数据与代码分离原则：所有用户生成数据永不进入版本控制

---

## v1.0.0 - 2026-05-08 Phase 1-4 全部完成

### 新增
- 项目基础目录结构（`persona/`、`sessions/`、`memory/`、`tasks/`、`references/`、`scripts/`）
- `AGENTS.md`：AI 代理开发指南，定义项目定位、架构、开发规范
- `README.md`：人类可读的项目说明
- `persona/lin-sai-persona.md`：整合版人格注入文件，从 virtu-LinSai v2.7 的 5 个源文件提炼
- `persona/source-manifest.json`：来源追踪与版本锁定
- 各目录 `README.md`：说明用途和格式规范

### 设计决策
- 定位为"专属合作者"（CoPilot），区别于 Agora 的"群聊会议室"
- 采用 1v1 持续对话 + 长期记忆 + 主动感知的交互模型
- 人格资产单向引用 virtu-LinSai，禁止反向修改
- 技术栈：Python 3 标准库 + Markdown + JSON，零第三方依赖

### Phase 1 启明 — 2026-05-08
- `scripts/session_manager.py` — 会话创建、加载、追加、列出、归档（382行，自检通过）
- `scripts/context_builder.py` — Prompt组装、动态预算分配（30000字符）、分层截断（304行，自检通过）
- `scripts/copilot_engine.py` — LLM调用封装（Claude/Kimi CLI）、交互式对话循环、CLI参数解析（465行，自检通过）
- 端到端集成测试通过：创建会话 → 构建上下文 → 调用LLM → 林赛回复 → 消息持久化

### Phase 2 长河 — 2026-05-08
- `scripts/memory_manager.py` — 用户画像提取、工作上下文、长期记忆索引、记忆片段、会话摘要（439行，自检通过）
- `scripts/task_manager.py` — 任务CRUD、状态流转、截止日期追踪、逾期检测（380行，自检通过）
- 集成：context_builder 自动加载相关记忆，copilot_engine 对话后自动更新画像/上下文
- Phase 2 集成测试通过：6轮对话 → 自动提取技能/偏好/待决策事项

### Phase 3 觉醒 — 2026-05-08
- `scripts/proactive_engine.py` — 心跳扫描、主动提醒、压力信号检测、三级自主、模式识别（465行，自检通过）
- 集成：copilot_engine 启动时运行 heartbeat 显示提醒，对话中自动识别交互模式
- Phase 3 集成测试通过：截止日期提醒 + 压力信号关怀均符合林赛人格

### Phase 4 灵犀 — 2026-05-08
- `scripts/document_handler.py` — Markdown/TXT读取、PDF基础提取、代码分析、文档摘要、参考文献索引（486行，自检通过）
- `scripts/agora_bridge.py` — Agora群聊系统桥接，支持上下文导出/导入（208行，自检通过）
- 集成：copilot_engine 新增 `/read` 和 `/agora` 命令
- Phase 4 集成测试通过：文档读取 → LLM摘要 → 代码分析 → Agora导出

### 修复
- `memory_manager.py` 用户画像提取规则调优
  - 移除宽泛关键词 `"实验"`（避免误匹配"实验室"→"室最安静"）
  - 新增6条精确模式：支持"我是做"、"从事...的"、"在...领域"等变体
  - 添加后缀边界（"的"、"方向"、"领域"）确保正确截断
  - 技能去重：子串重复自动合并（"MATLAB"+"MATLAB编程"→"MATLAB编程"），长度差>3保留（"Java"/"JavaScript"共存）

### 项目状态
- ✅ Phase 0-4 全部完成
- ✅ 8个核心脚本，总计3307行，全部语法正确
- ✅ 零第三方依赖，仅使用Python标准库
- ✅ 全部通过自检与集成测试

---
