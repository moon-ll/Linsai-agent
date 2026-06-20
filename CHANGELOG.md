# 变更记录

## v3.1.1 - 2026-06-20 灵活分类系统（迭代 2）

### 新功能
- **自定义分类系统**：用户可创建基于关键词规则的虚拟分类
  - 支持任一匹配（any）和全部匹配（all）两种逻辑
  - 自动扫描全库，匹配 wiki 页面
  - 分类是虚拟的：不移动文件，删除分类不影响文件
  - 存储在 `knowledge/categories.json`
- **分类管理弹窗**：前端 🏷️ 分类按钮，支持创建/删除/重新扫描
- **搜索筛选器**：4 个下拉筛选器（类型/阶段/子库/标签）
  - 实时过滤文件树
  - 一键清除筛选
- **标签内联编辑**：文件预览区显示标签 chip
  - 点击 ✕ 移除标签/子库归属
  - 点击"+ 标签"添加新标签
  - 通过 `/api/knowledge/wiki` POST meta-only 更新

### 新增 API 端点
- `GET /api/knowledge/categories` — 列出全部分类
- `GET /api/knowledge/filters` — 获取筛选器选项
- `POST /api/knowledge/categories/create` — 创建分类
- `POST /api/knowledge/categories/update` — 更新分类
- `POST /api/knowledge/categories/delete` — 删除分类
- `POST /api/knowledge/categories/scan` — 重新扫描全部分类
- `POST /api/knowledge/filter` — 按条件过滤 wiki 页面

### 改进
- `POST /api/knowledge/wiki` 支持 meta-only 更新（无需 content）
- 新增 `scripts/kb_categories.py` 模块（CRUD + 匹配 + 筛选）
- 前端新增分类管理、筛选器、标签编辑器 JS 函数

### 验证
- self_test 88/88 全绿
- Web API 测试 26/26 全绿
- 浏览器验证：创建"固体HHG"分类，自动匹配 74 篇 wiki 页面

## v3.1.0 - 2026-06-20 知识库自维护闭环（迭代 1）

### 新功能
- **`sync_all()` 自动重建**：同步完成后自动触发 reindex + rebuild_graph，无需手动重建
- **`kb_auto_sync.py` 定时同步脚本**：支持 macOS LaunchAgent 每日 09:00 自动同步
  - `--install`：安装 LaunchAgent
  - `--uninstall`：卸载 LaunchAgent
  - `--status`：查看自动同步状态和历史
  - 失败自动记录到 `sync-state.json` 的 `auto_sync_history`
- **`/api/sync/auto-status` API**：返回 LaunchAgent 安装状态和自动同步历史
- **前端管理工具栏**：知识库文件树顶部新增
  - 🔄 同步按钮：一键触发 sync_all（含自动重建）
  - 📊 健康按钮：快速查看知识库健康度
  - 同步状态指示器：显示自动同步是否开启

### 改进
- `sync_engine.py` 新增 `_import_kb_helper()` 辅助函数
- `web_server.py` 新增 `/api/sync/auto-status` GET 端点
- `web/index.html` 新增 `.kb-toolbar` 管理工具栏
- `web/css/style.css` 新增工具栏和指示器样式
- `web/js/app.js` 新增 `handleKbSync`、`handleKbHealth`、`loadSyncIndicator` 函数

### 验证
- self_test 88/88 全绿
- Web API 测试 26/26 全绿
- 浏览器验证：工具栏渲染正常，同步按钮功能正常，指示器正确显示"手动同步"

## v3.0.2 - 2026-06-20 BUG-A 修复 + 知识库维护增强

### BUG 修复
- **BUG-A（Web 端聊天功能异常）**：修复 v3.0.0 布局重构引入的聊天侧栏问题
  - `.upload-zone` 默认隐藏（此前始终可见，占用输入区 64px 空间）
  - `.chat-sidebar` 添加 `align-self: stretch` + `overflow: hidden` 高度保护
  - `.chat-sidebar-inner` 添加 `min-height: 0` 防止 flex 子元素高度塌陷
  - 上传按钮改为切换上传区域显示/隐藏（此前直接弹文件选择器）
- **Web API 测试超时**：`_wait_for_server` 超时从 20s 增至 30s，轮询超时从 2s 增至 3s

### 知识库维护增强
- **`kb_importer.py`**：补全 `import_all_candidates()` 函数定义（此前 def 行缺失，函数体悬空）
- **`kb_maintenance.py`**：新增 `cmd_rebuild_graph()` 子命令（`--rebuild-graph`）
  - 从所有 wiki frontmatter 的 related/project 字段反向重建知识图谱
  - 解决 import_candidate/import_deep_analysis 绕过 save_wiki_page 导致的图谱断层
  - 已集成到 `--weekly` 周维护流程

### 验证
- self_test 88/88 全绿
- Web API 测试 26/26 全绿
- 浏览器验证：消息区从 377px 增至 441px，输入区从 212px 降至 148px
- 图谱重建：88 节点成功导入

## v3.0.1 - 2026-06-19 每日简报+NSFC项目正式纳入知识库管理

### 导入内容（47 篇）
- **23 份每日简报** → wiki/papers/briefing-*.md（带 frontmatter，可检索可浏览）
- **15 份深度解析** → wiki/projects/deepxiv-论文库/（结构化：核心发现/林赛理解/开放问题）
- **5 个 NSFC 课题报告** → wiki/projects/NSFC-强场超快/（T1-T5 立项依据镜像）
- **5 份 NSFC 决策记录** → wiki/projects/NSFC-强场超快/decisions/

### 成果
- wiki 从 33 → 89 篇，raw 从 61 → 106 篇
- 搜索"每日简报"/"NSFC"/"带动力学"全部可检索命中
- 知识库主区文件树现在显示全部内容（简报/深分析/课题/决策）
- 所有导入内容带 project 标签 + source 标记，纳入子库分类

### 验证
- self_test 88/88 全绿
- 检索验证通过

## v3.0.0 - 2026-06-19 知识库升为主舞台：独立界面 + 聊天降为侧栏

### 架构重构（核心）
知识库从"聊天框的弹窗附属"升级为**主舞台**，聊天降为**右侧可折叠侧栏**。
符合 Obsidian/Notion 的科研知识库体验。

### 新布局
```
左:会话栏 │ 中:知识库主区(文件树+内容预览双栏) │ 右:聊天侧栏(可折叠)
```

### 知识库主区（中间双栏）
- 左半文件树（280px）：🗺️MOC / 📐概念 / 🛠️方法 / 👤人物 / 📚综述 / 📁项目 / 📄论文库
- 右半内容预览：复用 openWikiDetail（[[]]双链/related chip/反向关联均可点击）
- 搜索框实时搜索，结果替换树

### 聊天侧栏（右侧可折叠）
- 聊天功能全部移入，收起时变 40px 细条，状态存 localStorage
- 聊天逻辑不退化（sendMessage/SSE/@注入不变）

### 验证：self_test 88/88 全绿，三栏布局正确

## v2.9.5 - 2026-06-19 知识库交互修复：双链可点击+搜索+raw预览+7个bug

### 核心修复：让知识网络真正连通
之前数据层建好了（MOC/双链/related/图谱），但展示层把所有关联渲染成纯文本，
知识网络在 UI 里是断的。本次让所有关联都可点击跳转。

### 7 个 Bug 修复
- **BUG-1** 打开文件夹 404：openLocalFile 裸 'knowledge' 被错加前缀 → 修复判断
- **BUG-2** MOC 详情 [[]] 双链不可点击（最严重）→ 渲染成可点击链接，点击跳转
- **BUG-3** related 字段纯文本 → 渲染成可点击 chip
- **BUG-4** raw 列表点击无反应 → 新增 openRawDetail 预览弹窗
- **BUG-5** .kb-tab 选择器跨面板冲突（污染学习面板）→ scope 到 #kb-manager-overlay
- **BUG-6** confidence NaN → 兜底 `?? 0`
- **BUG-7** onclick 路径未转义 → 统一转义单引号

### 新功能
- **知识库搜索框**：wiki tab 顶部加搜索框，接已有 /api/knowledge/search，支持跨类型按关键词找概念
- **按标题跳转 openWikiByTitle**：[[wikilink]] 和 related chip 共用，模糊匹配 title/path
- **反向关联展示**：wiki 详情底部显示"被哪些笔记关联"（调 /api/knowledge/related）
- **CSS 双链样式**：.kb-wikilink 虚线下划线 + .kb-related-chip 圆角标签

### 验证
- self_test 88/88 全绿
- 搜索 API 返回正确结果（三步模型 3 条）
- MOC 双链、related chip、raw 预览均可点击

## v2.9.4 - 2026-06-19 知识库专项优化：修bug+分层结构+MOC+标签体系

### 第一层：修 Bug
- **打开文件 404 修复**：openLocalFile 补 knowledge/ 路径前缀
  - 根因：wiki/raw 列表传的路径相对 knowledge/，后端按项目根拼接（缺前缀）
  - 修复后点知识库面板里的文件能正常打开

### 第二层：数据治理（一致性）
- **6 篇综述补 frontmatter**：hhg-methods/principles/comprehensive/systems/technology/teams
  - 全部补全 type/tags/related/growth_stage/confidence（之前完全无或残缺）
- **图谱治理**：
  - 26 条边补 type 字段（related/pioneered/same_as）
  - 9 个节点 type 统一为复数（concept→concepts, method→methods, person→people）
  - 连接孤立节点 attosecond → 高次谐波产生
- 结果：27 节点 27 边 0 孤立，33 篇 wiki 全有 frontmatter

### 第三层：分层结构（让知识库"好用"）
- **MOC 索引页（Map of Content）**：
  - `wiki/concepts/MOC-HHG.md` — HHG 知识地图（理论/材料/方法/人物/应用/综述）
  - `wiki/projects/NSFC-强场超快/MOC.md` — NSFC 课题入口（T1-T5/概念/方法/论文）
  - `wiki/projects/deepxiv-论文库/MOC.md` — 论文库索引（61篇/归档说明）
- **标签体系规范化**：33 篇 wiki 追加分类维度标签
  - `#type/concept` `#type/method` `#type/person` `#type/report` `#type/MOC`
  - `#topic/HHG` `#topic/固体HHG`
  - `#status/mature` `#status/growing`
- **前端分层浏览**：loadKbWiki 重写
  - 顶部 MOC 知识地图入口（主题漫游起点）
  - 按 type 折叠分组（概念/方法/人物/综述/项目）
  - 每组按 growth_stage 排序（mature 优先）
  - 显示 project 子库标签

### 成果
- 知识库从"平铺列表"升级为"分层结构 + MOC 主题入口"
- 符合好知识库标准：原子化笔记 + 双向链接 + MOC + 标签体系
- 94 文档（61 raw + 33 wiki），27 节点 27 边 0 孤立

### 验证
- self_test 88/88 全绿
- 33 篇 wiki 全有 frontmatter，图谱 0 孤立
- 打开文件不再 404

## v2.9.3 - 2026-06-18 知识库整理 + 文献流程修正（感兴趣≠归档）

### 知识库整理（确保 hermes 工作连贯性）
- **清理**：删除 1 篇无深度解析的 hermes 简报、移动 1 篇边缘量子光学笔记到 _archive/
- **图谱清理**：删除 16 个悬空 paper_2026 节点 + 5 个孤立英文冗余节点（48→27 节点）
- **标签重命名**：raw/papers 的 project 从"文献简报"→"deepxiv-论文库"（消除命名误导）
  - 这 55 篇是 deepxiv 真实论文元数据，不是简报
- **子库目录**：wiki/projects/文献简报 → wiki/projects/deepxiv-论文库
- **文档更新**：knowledge/README.md 重写，明确 project 字段与子库分类规范
- 图谱：27 节点 26 边，仅 1 孤立节点

### 文献流程修正（核心逻辑修复）
**之前（错误）**：👍感兴趣 → 立即归档（归档了不充分理解的内容）
**现在（正确）**：
```
未看 → [👍感兴趣] → 已看未讨论 → [💬讨论完成] → 归档（深度沉淀）
```
- 👍 感兴趣：仅记录偏好 + 移入"已看未讨论"池，**不归档**
- 💬 讨论：注入知识库 → 林赛讨论（充分理解论文）
- 📥 归档沉淀：讨论完成后的最终动作，归档+深分析+wiki建议
- 归档 = 对论文有足够了解后的知识沉淀，不是瞬间的感兴趣

### 候选池状态机重构
- `interested` → viewed（不再 archived）
- 新增 `discuss_done` 动作 → archived（讨论完成后归档）
- 已看未讨论区：💬讨论 + 📥归档沉淀 两个操作
- 状态标签优化：🔔未看 / 📖已看未讨论 / ✅已归档（深度沉淀）

### 验证
- self_test 88/88 全绿
- hermes 连贯性：SOUL.md 软链接正常、4 cron 活跃、45 篇候选可读

## v2.9.2 - 2026-06-18 NSFC 面板重构 + 异步协作框架（hermes干活↔知识库↔林赛讨论）

### NSFC 面板三区重构
- **区域1 课题产物**：T1-T5 + 共性顶层，卡片网格展示（进度/版本/大小/参考数），点击展开文档
- **区域2 调研资料**：references(16篇) + knowledge_base(concepts/methods) + daily_brief(7份)，折叠列表
- **区域3 待决策项**：从 state.md 提取，每项可 ✓通过/✗否决/💬讨论
- 替换了原来照搬 state.md 区块的混乱展示

### 通用异步协作框架
**hermes 干活 → 知识库 → 林赛讨论 → 反馈 → hermes 再干活**
- 待决策项「💬 讨论」：注入该课题知识库到聊天框 → 林赛基于知识库讨论 → 总结写 discussions/ → 异步反馈 hermes
- 通过/否决：持久化到 memory/nsfc-decisions.json + 异步反馈 hermes
- 林赛和 hermes 不直接交互，通过知识库（discussions 文件）异步通信

### 讨论→反馈闭环
- `POST /api/projects/nsfc/pending/<id>` — 决策（approve/reject/discuss）
- `POST /api/projects/nsfc/discuss-summary` — 总结讨论 → 写 discussions/ + 反馈 hermes
- 讨论工具栏：显示"📝总结讨论"按钮 → 林赛生成总结 → "✓提交总结到discussions"
- 决策状态持久化：memory/nsfc-decisions.json（approved/rejected 不再显示）

### 新增后端数据
- `get_nsfc_topics()` — 6 课题卡片（T1-T4 mature 100KB+，T5 seedling）
- `get_nsfc_references()` — 16 references + 7 概念/方法 + 7 简报
- `get_nsfc_pending()` — 结构化待决策项（合并持久化状态）
- 新增 API：/nsfc/topics /nsfc/references /nsfc/pending /nsfc/pending/<id> /nsfc/discuss-summary

### 验证
- self_test 88/88 全绿
- 6 课题卡片渲染、23 调研资料、待决策项通过/讨论闭环

## v2.9.1 - 2026-06-18 候选池三状态 + @知识库文件讨论 + 智能分类回填

### 候选池三状态持久化
- **新增 `scripts/paper_pool.py`**：候选论文生命周期管理（unseen→viewed→archived）
- 未看的候选**累积保留**在池中，不因新一天而清空——你随时回来继续
- 新增「⏰ 稍后」操作：标记为 viewed（已看未讨论），留待后续
- 前端按三状态分组渲染（🔔未看 / ⏰已看未讨论 / ✅已归档）
- 新增 API：`GET /api/projects/papers/pool`（支持 status 过滤）

### @知识库文件讨论
- **🗂️ 按钮**：点击弹出知识库文件树（按类型分组），勾选 1-N 个文件注入讨论上下文
- **@补全**：输入框打 @ 触发文件名补全，选中后用 `[文件名]` 标记
- 发送消息时自动读取选中文件内容（截断 2000 字）拼接到消息后
- 新增 API：`GET /api/knowledge/files`（文件列表）、`GET /api/knowledge/file-content`（读内容）
- 文献卡的「💬 讨论」按钮：一键把文献信息填入聊天框 + 注入知识库上下文

### 智能分类回填
- 给现有 61 篇 raw 论文批量补 `project` frontmatter 字段
- 按方向自动分类：55 篇→文献简报子库，6 篇→NSFC-强场超快子库
- 知识库检索现在支持按子库过滤（search 的 project 参数）

### feedback 端点增强
- 新增 `later` 动作（稍后讨论）
- 所有动作联动候选池状态流转
- skip/later 均标记为 viewed（保留可追溯）

### 验证
- self_test 88/88 全绿
- 候选池 45 篇入池，三状态正确
- 知识库文件 API + 内容读取正常

## v2.9.0 - 2026-06-18 以知识库为核心的科研协作工作流

### 用户需求重构
界面是基本需求（文献卡+进度展开），知识库是核心（反馈→深读→归档→分类→生长），讨论是轻量的。

### 文献卡小红书式卡片流
- 每篇候选文献一张卡片（标题/作者/方向/评分/TL;DR），纵向滚动流
- 三个操作按钮：👍感兴趣 / 👎跳过 / 📥归档，操作后卡片淡出移除
- 👍 触发：归档 raw + 导入深分析 + 生成 wiki 笔记建议 + 异步反馈 hermes 偏好

### 申请书进度层次展开
- 新增 `parse_nsfc_state_hierarchical()`：state.md → 三层结构（区块→表格行→文件路径）
- 前端渲染为可折叠 `<details>` 树，关键区块默认展开（当前Phase/待决策/风险）
- 表格行/列表项提取文件路径，点击 📄 按钮加载文档内容（第3层）

### 知识库智能生长（归档自动 + wiki 确认）
- `suggest_wiki_notes(arxiv_id)`：从深分析的 core_findings/linsai_connection 提取概念和关联建议
- 👍 处理后弹出确认弹窗：勾选要生成的概念笔记和图谱关联，确认后生成
- 生成的笔记标记 seedling（confidence 0.4），邀请用户补充
- `grow_from_suggestion()`：按确认结果生成 wiki 笔记 + 连图谱边

### 子库自动分类
- `infer_project(direction)`：按方向关键词自动归入对应子库
  - "固体HHG"/"2D材料"/"拓扑" → NSFC-强场超快 子库
  - 默认 → 文献简报 子库
- import_candidate/import_deep_analysis 自动使用

### hermes 偏好反馈闭环
- 👍/👎 时异步调 `hermes_bridge.oneshot()` 反馈用户偏好（fire-and-forget，不阻塞 UI）
- 本地 `memory/paper-feedback.json` 累积偏好数据

### 新增 API
- `GET /api/projects/nsfc/tree` — 层次结构树（12 区块）
- `POST /api/projects/papers/feedback` — 文献反馈（interested/skip/archive）
- `POST /api/knowledge/suggest` — 查询 wiki 建议
- `POST /api/knowledge/grow` — 按确认生成 wiki 笔记

### 验证
- self_test 88/88 + web_api 26/26 全绿
- 实测：tree 返回 12 区块、feedback(skip/archive) 正常、suggest 返回 8 概念

## v2.8.0 - 2026-06-17 虚拟用户测试 + 前端 bug 修复 + 知识库全套整理

### 第一块：Web API 虚拟用户测试框架
- **新增 `scripts/tests/test_web_api.py`**：基于 test_runner 框架的 HTTP 虚拟用户测试套件
  - ApiClient（urllib 零依赖）：GET/POST/PUT/DELETE + JSON 编解码 + 状态码断言
  - WebApiSuite：启动 web_server 子进程（隔离环境），26 个测试用例覆盖所有 API
  - 接入 self_test：`python3 scripts/self_test.py --web`（26/26 通过）
  - web_server.py 加 `--root` 参数支持隔离测试环境

### 第二块：前端 bug 修复
- **P0 崩溃修复**：补全 learning manager 4 个缺失函数（openLearningManager/closeLearningManager/renderLearningManager/switchLearningTab），点击🌱自主学习按钮不再报错
- **P1 任务按钮**：修复 `.task-panel`/`.right-panel` 选择器 → `getElementById`
- **P1 任务新建/删除**：task-panel 加「+新建」表单 + createNewTask/deleteTask 函数 + 后端 POST/DELETE /api/tasks 路由
- **P2 导出会话**：实现 export-btn 真导出（生成 .md 下载，不再是"开发中"）
- **P2 死代码**：删除 #back-to-current 遗留绑定

### 第三块：知识库数据修复
- **methods-report 重复 bug**：截断 hhg-methods-report.md（1510→735 行，删除 775 行重复）
- **graph 悬空边**：清理 16 条全空 source/target 的坏边
- **principles 标题 bug**：修复 Python list 字面量未解包的标题

### 第四块：知识库全套整理（补 HHG 核心原子笔记）
- **concepts 新增 8 篇**：三步模型/截止定律/相位匹配/水窗口/Lewenstein模型/固体高次谐波/液体高次谐波/高次谐波产生（HHG总论）
- **methods 新增 8 篇**：RABBITT/FROG/瞬态吸收光谱/VMI/COLTRIMS/阿秒条纹相机/协方差映射/TDSE求解器
- **people 新增 5 篇**：Corkum/Krausz/LHuillier/Ghimare-Reis/北大HHG团队
- **拓扑绝缘体补完**：seedling(0.3) → growing(0.7)，补充实质内容
- **aliases.json**：从空 → 25 组中英/缩写对照（HHG=高次谐波产生、三步模型=three-step-model 等）
- **图谱重建**：48 节点 26 边（原 32 节点 0 边），0 孤儿，核心概念/方法/人物互联
- **growth-log**：补充 8 条整理事件记录

### 成果数据
- wiki 条目：9 → 30（mature 12 / growing 5 / seedling 1）
- 知识库检索：别名扩展生效（"HHG"→高次谐波产生、"RABBITT"→重建阿秒拍频干涉）
- 测试：self_test 88/88 + web_api 26/26，全绿不回归

## v2.7.0 - 2026-06-17 hermes 协作中枢：林赛 Web 作为双 hermes 工作流的指挥台

### 架构定位
hermes（+ profile linsai）是"大脑和手脚"——自主执行论文简报 cron、NSFC 工作流 cron。
林赛 CoPilot Web 升级为"指挥台和档案室"——可视化产出、控制 cron、沉淀知识、多端汇聚。

### 新增 5 个核心脚本
- `scripts/project_reader.py`：解析 NSFC state.md（进度/待决策/路线图）、discussions（决策卡）、topics（申请书章节）、文献候选/简报
- `scripts/kb_importer.py`：把 hermes 产出（daily_candidates/deep_analysis JSON）转换为林赛知识库 markdown，沉淀到「文献简报」子库
- `scripts/hermes_bridge.py`：控制 hermes cron（list/pause/resume/run）+ 手动派活（oneshot agent loop）
- `scripts/sync_engine.py`：多端同步层，扫描 hermes 248 个会话/文献产出 → 导入林赛（幂等去重）
- 知识库子库改造：`knowledge_base.py` 支持 projects/ 子目录、project 字段过滤检索、图谱 belongs_to 边

### 新增 12 个 API 端点
- **项目数据**：`/api/projects`、`/api/projects/nsfc/{dashboard,decisions,chapters,proposal}`、`/api/projects/papers/{candidates,briefings}`
- **hermes 控制**：`/api/hermes/cron`、`/api/hermes/cron/<id>/{pause,resume,run}`、`/api/hermes/run`（SSE 流式）
- **导入沉淀**：`/api/import/paper`、`/api/sync/{status,run}`

### 新增前端
- 工具栏加 📂 项目面板 + ⚡ hermes 控制台两个按钮
- `web/js/projects.js`：NSFC 仪表盘（阶段/待决策/风险/路线图/决策时间轴）+ 文献候选表格（勾选导入）+ 多端同步
- `web/js/hermes_console.js`：cron 列表（启停/触发）+ 手动派活（hermes agent loop 流式输出）

### 知识库子库架构
- `knowledge/wiki/projects/文献简报/` 和 `NSFC-强场超快/` 两个子库
- frontmatter 新增 `project` 字段，search() 支持 `project=` 过滤
- 图谱自动连接 项目节点→子内容（belongs_to 边）
- 文献简报子库可作为 NSFC 项目的知识来源（跨子库互联）

### 写回策略（安全）
- 林赛讨论结论只写 hermes 的 `discussions/`（BRAIN 必读输入），不直接改申请书内容
- 文献讨论沉淀写林赛自己的 `knowledge/wiki/projects/文献简报/`

### 验证
- `py_compile` 全量通过 + `self_test` 88/88 全绿
- 5 个新脚本自检全部通过
- web_server 实测：12 个 API 返回 200，前端面板渲染正常
- NSFC 仪表盘：3 BRAIN 区块 / 5 待决策 / 20 路线图行 / 5 条决策
- 文献候选：55 篇可导入，子库检索验证通过
- hermes cron：6 个 job 正确读取，网关 running

## v2.6.2 - 2026-06-17 代码瑕疵修复 + 知识库索引重建 + 会话摘要链路接通

### 修复 3 处代码瑕疵
- `tool_engine.py`：删除 `tool_run_command` 的死代码（return/except 后重复的整段函数体 L709-766，永不执行）
- `learning_engine.py`：自检 `[4/5]` 调用未定义的 `_build_wikipedia_distill_prompt` → 改用运行时实际使用的 `_build_web_search_distill_prompt`（之前手动自检会 NameError）
- `research_profiler.py`：漂移分支调用未定义的 `_import_kb()` → 改用 `import knowledge_base as kb`（之前被 try/except 静默吞掉，导致生长日志少记）

### 重建知识库索引（修复严重脱节）
- `knowledge/index.json`：死链 74 → **0**（74 条引用不存在文件的陈旧索引已清除），doc_count 8 → 739，built_at 更新至今日
- `knowledge/graph.json` + `index.json` 的 `graph_summary`：**完全同步**（节点 32 / 边 16，之前 index 缓存的 summary 停在 2 节点/3 边）
- 清理 17 个指向不存在论文的孤儿图谱节点
- 检索功能恢复可信：`search("三步模型")` → principles-report score=0.44（TF-IDF 真实打分）

### 接通会话摘要链路（CoPilot 记忆能力起点）
- `session_manager.archive_session()`：归档时自动调用 `memory_manager.generate_session_summary()`，替代创建时的占位符 `"> 会话摘要预留位置"`
- 摘要生成失败不阻塞归档（降级保留占位）
- 端到端验证通过：创建→加消息→归档→摘要含真实内容 + 长期记忆索引同步更新

### 验证
- `py_compile` 全量通过 + `self_test` 88/88 全绿
- `learning_engine` 自检 5/5 通过（之前 [4/5] NameError）

## v2.6.1 - 2026-06-17 项目健康度清理：补回幽灵脚本 + 恢复 Web + 修包 import

### 补回缺失脚本（被 4d3969e 误删或从未实现）
- **新增 `scripts/version.py`**：集中读取 VERSION 文件，提供 `get_version()` / `__version__` / `parse_version()` / `is_newer()`，消除三处人工版本号同步点
- **补回 `scripts/backup_manager.py`**：数据备份/恢复（zip 打包 + `auto_backup()` 24h 跳过 + `--list/--restore/--only` + 恢复前应急备份），修复 `copilot_engine.py` 的 `from backup_manager import auto_backup` 静默失效
- **补回 `scripts/upgrade.py`**：安全升级流程（备份→语法验证→迁移→自测→可回滚），支持 `--check/--simulate/--self-check`，修复 README/AGENTS 的 SOP 命令照抄报错
- **从 git 历史（30b12d7）恢复** 4d3969e 误删的脚本：
  - `scripts/web_server.py`（1165 行）+ `web/` 前端三件套（index.html/css/js，4533 行）—— Web 界面能力恢复
  - `scripts/deep_audit.py`（622 行）：9 维度架构稳定性审查
  - `scripts/learning_quality_tracker.py`（501 行）：交互质量追踪
  - `scripts/test_e2e_learning.py` / `test_e2e_learning_full.py`（共 578 行）：端到端测试

### 修复包 import 模式（可被作为 Python 包 import）
- `scripts/deepxiv_knowledge/{paper_writer,pdf_enricher,run}.py`：绝对 import → `try/except` 双模式（包模式优先，脚本模式回退），修复 `import deepxiv_knowledge` 崩溃
- `scripts/wiki_regenerator/{report_writer,run}.py`：同上处理

### 文档与版本号同步
- **版本号统一到 2.6.0**：`VERSION`（2.1.0→2.6.0）、`README.md`（2.0.0→2.6.0）、`AGENTS.md`（2.0.0→2.6.0）、`scripts/README.md`（2.2.0→2.6.0）
- **修文档失实**：
  - `README.md` / `AGENTS.md` 目录树按磁盘真实情况重写（补 slash_commands/version/deepxiv_knowledge/wiki_regenerator，删不存在的 upgrade_wiki_for_obsidian）
  - `docs/README.md`：取消 v2.1.0 计划"当前有效"声明（改为"已实现，归档"），补齐 4 份 HHG 调研报告清单
  - `scripts/README.md`：脚本统计口径更新（23 主脚本 + 两个流水线包）
- **修代码注释**：`tool_engine.py:14` 残留的 `v2.1.0 Phase 0` 注释修正

### 第一代草稿脚本清理（v2.6.0 已由第二代流水线取代）
- 删除 6 个第一代 HHG 脚本：`hhg_paper_fetcher.py` / `fetch_hhg_new_papers.py` / `ss_search_hhg.py` / `extend_papers.py`（含语法错误 + 编造数据）/ `hhg_batch_writer.py` / `update_graph.py`

### 验证
- `py_compile` 全量通过（含恢复的 web_server/deep_audit 等 + 两个子包）
- `import deepxiv_knowledge` / `import wiki_regenerator.paper_reader` 包模式 import 成功
- `backup_manager --self-check` / `upgrade --self-check` / `version` 自检通过

## v2.6.0 - 2026-05-22 方法完备性评估（按方法逐一要素级审查）

### 完备性评估集成
- 替换通用检查清单（第 785-796 行）为 **12 个方法的逐一要素级完备性评估**（来自 `solid-HHG-completeness-by-method.md`）
- 每个方法含：动力学方程、观测量计算、近似、参数 → ✅/❌ 状态 + 原文内容 + 复现障碍说明
- 关键缺失项（影响复现）：
  - 双层石墨烯 SBE：k 点网格密度、时间步长
  - Na₃Bi TDDFT：时间步长
  - Cd₃As₂ Boltzmann：数值积分格式、动量采样密度
  - Rashba SOC TDSE：系统格点数、时间步长
  - 莫特 Hubbard DMFT：DMFT solver 类型、晶格大小
  - YBCO 准 Hubbard：基态求解格式、EOM 积分格式、U_eff
  - 扭转 h-BN：χ 系数（唯象理论，无从头算参数）
- 新增 **完备性总表**（第 980-995 行）：12 方法 × 4 要素矩阵

### 文件变更
- `docs/solid-HHG-by-material-system.md`：831 → 1029 行（+198 行）

## v2.5.0 - 2026-05-21 凝聚态 HHG 计算方法调研（按材料体系分类，v3，全文原文提取）

### 调研报告重建（v3）

- `docs/solid-HHG-by-material-system.md`（**31 KB，831 行**）：按材料体系分类的凝聚态 HHG 计算与分析方法调研
- **全面联网检索**（arXiv API）确认凝聚态 HHG 已覆盖的 9 个材料体系类别
- **全部内容严格来自已获取论文原文**，无任何生成内容，每节末尾标注来源 arXiv ID

### 调研覆盖的 9 个材料体系

**体系一：宽禁带介电体/绝缘体**
- `1807.02961` — Le Breton et al. (2018)：h-BN，Octopus TDDFT，Δx=0.28 Bohr，k: 32²–54³
- `1607.00747` — Otobe (2016)：α-石英，mBJ，Δt=0.02 a.u.，HH19(30 eV)
- `2508.15076` — Kuzkova et al. (2025)：MgO，XUV 干涉偶极子相位测量，三层次 SBE/Wannier

**体系二：传统半导体**
- `1805.10453` — Klemke et al. (2018)：Si，TDDFT，偏振分辨，HH5 纯带内，HH7 耦合，HH9 主要带内
- `2004.04492` — (2020)：GaAs，Luttinger-Kohn 模型，非扰动 HHG

**体系三：2D 材料**
- `2011.12252` — (2020)：石墨烯，SBE 紧束缚，t₀=2.7 eV，t⊥=0.48 eV，双层石墨烯
- `2111.10986` — Lee et al. (2021)：MoS₂，Berry 曲率公式，伪自旋谷选择定则
- `1807.02961` — 单层 h-BN 原子样 HHG，E_c = E_w + 3.17U_p

**体系四：拓扑材料**
- `1806.11232` — Silva et al. (2018)：Haldane 模型，Chern 数控制谐波螺旋度
- `2103.09322` — Tancogne-Dejean et al. (2021)：Na₃Bi，Octopus SOC TDDFT，Δr=0.36 Bohr
- `2405.16125` — Zhang et al. (2024)：TaAs，Jones 矩阵形式，晶体对称性 vs 拓扑
- `1911.01476` — Kovalev et al. (2019)：Cd₃As₂，Boltzmann 输运，τ=10 fs，THz HHG

**体系五：扭转/双层材料**
- `2503.08052` — Ma et al. (2025)：扭转 h-BN，相位匹配，效率 ~1.5×10⁻⁵
- `2011.12252` — AA/AB 堆垛双层石墨烯（已在上方体系三中）

**体系六：磁性/SOC 材料**
- `1906.10224` — Mrudul S. et al. (2019)：自旋极化缺陷，TDDFT
- `2104.04001` — Ly & Manchon (2021)：Rashba SOC，紧束缚 TDSE，谐振条件 α_R k_F/J ≈ 1

**体系七：关联电子材料**
- `2203.01029` — Murakami et al. (2022)：莫特绝缘体，DMFT + Hubbard，U
- `2409.04216` — Tyulnev et al. (2024)：TiSe₂ CDW，HH5 异常各向异性，Tc=205 K
- `2201.09515` — Alcalà et al. (2022)：YBCO，两带准 Hubbard + BCS，Tc=88 K，T*=173 K

**体系八：手性 HHG**
- `2306.02313` — (2023)：石墨烯，ω+2ω co-rotating，产生同螺旋度圆谐波

**体系九：气体相位匹配**
- `2404.01325` — Popmintchev et al. (2024)：Δk 方程，η_CR ∝ λ_L⁻²，He ~330 eV（水窗）

### 方法论改进

- 增加体系分类（9 大类）而非理论模型分类
- 每个体系均包含计算方法、软件、关键参数（数值）
- 增加跨体系方法对比树：拿到一个材料 → 确定体系 → 选择方法
- 增加方法完备性检查清单（k 点、网格、时间步长、带数、CAP、SOC、关联）

## v2.4.0 - 2026-05-19 固体 HHG 计算方法调研（按材料体系分类，v2）

### 调研报告重建（v2）

- `docs/solid-HHG-computation-by-material.md` → **完全重写**（28.7 KB，850 行）
- **全部内容严格来自已获取论文原文**，无任何生成内容
- 每节末尾标注来源 arXiv ID

### 本次重新获取的论文（共 8 篇）

**体系一：h-BN**
- `1807.02961` — Le Breton, Rubio, Tancogne-Dejean (2018)：Octopus TDDFT 参数（Δx=0.28 Bohr，k: 32²–54³），激光 1600 nm，面内/层方向 HHG，带隙 4.50–4.87 eV

**体系二：α-石英**
- `1607.00747` — Otobe (2016)：实时 TDDFT，mBJ 交换势，网格 26×44×38，k: 8³，Δt=0.02 a.u.，HH19（30 eV），主导机制：电子-空穴复合

**体系三：Si / 石英偏振分辨**
- `1805.10453` — Klemke, Tancogne-Dejean et al. (2018)：实验参数（Si: 2 μm，(100)，2.1 μm，120 fs，0.6 TW/cm²；石英: 50 μm，z-cut，40 TW/cm²），HH5 纯带内，HH7 耦合，HH9 主要带内

**体系四：拓扑材料**
- `1806.11232` — Silva, Jiménez-Galán, Smirnova, Ivanov (2018)：Haldane 模型参数，Chern 数 ν 控制谐波螺旋度，λ=3 μm，E₀=4×10⁹ V/m

**体系五：2D 材料与谷电子学**
- `2203.10253` — Luu (2022)：SBE vs TDDFT 对比，有隙/无隙石墨烯，谷极化
- `1906.10224` — Mrudul S., Tancogne-Dejean, Rubio, Dixit (2019)：h-BN 自旋极化空位缺陷，TDDFT，电子-电子相互作用必须包含

**体系六：气体 HHG 相位匹配**
- `2404.01325` — Popmintchev et al. (2024)：Δk 方程，η_CR 公式（∝λ_L⁻²），相位匹配截止 ∝ λ_L^1.6-1.7，He: ~330 eV，λ→3 μm: ~1 keV

**体系七：量子光学**
- `1910.13791` — Gorlach, Lewenstein et al. (2019)：SFQED 框架，三步方案，组合波函数（纠缠态），每个 HHG 光子是整个频谱的叠加

**体系八：分子自探测**
- `2103.16228` — Haessler, Caillat, Salières (2021)：自探测范式，ADK + Lewenstein，轨道断层成像，多电子动力学

### 方法论改进

- 明确区分哪些内容来自哪些具体论文
- 每个体系的参数均为原文提取（如 h-BN 的 Δx=0.28 Bohr，α-石英的网格 26×44×38）
- 删除了所有凭记忆补充的内容（ZnO SBE 参数、MoS₂ Berry 曲率具体公式等）

## v2.3.0 - 2026-05-19 固体 HHG 计算方法调研（按材料体系分类）

### 调研报告新增

- `docs/solid-HHG-computation-by-material.md`（**20.3 KB**）：按 6 大材料体系组织的 HHG 计算与分析方法调研

### 体系一：宽禁带介电体

- h-BN（单层→体材料层数演化，TDDFT 参数，Octopus 设置，Le Breton 2018）
- α-石英（Otobe 2016）：mBJ 赝势，TDDFT 设置，HH19（30 eV）

### 体系三：传统半导体

- Si（Klemke et al. 2018）：(100)取向，2 μm 厚度，2.1 μm 驱动，TDDFT 参数，偏振分辨

### 体系四：拓扑材料

- Haldane 模型（Silva et al. 2018）：Haldane Hamiltonian，拓扑相变条件，Chern 数→谐波椭圆率切换

## v2.2.0 - 2026-05-19 固体 HHG 理论调研报告重建（正确检索流程）

### 调研报告重建

- 重写 `docs/solid-HHG-theory-methods-survey.md`：从 285 KB 原始文件提炼为 **23.5 KB** 结构化报告
- **全部内容均直接来自论文原文**，通过 arXiv API 检索 → deepxiv CLI 逐篇获取，无任何生成内容
- 纠正前期 ID 漂移问题：所有 13 篇论文均经检索验证 arXiv ID 正确性

### 新增核心文献（SBE 理论方向）

- `2102.11964` — Yue & Gaarde (2021)：全 BZ 隧穿 + 不完美回碰，SBE 鞍点方程
- `2003.02961` — Yue & Gaarde (2020)：速度/长度规范系统比较，h-BN 实例，Berry 联络规范依赖
- `2508.07869` — Thümmler & Lettau (2025)：Wannier 规范 SBE + 平滑退相干算符（SDO），FFT 加速
- `1904.00283` — Silva, Martín, Ivanov (2019)：MLWF 构造平滑偶极矩阵元，h-BN 2 带收敛性

### 新增核心文献（量子光学+Berry 方向）

- `2312.08942` — Lange, Hansen, Madsen (2023)：Fermi-Hubbard 模型，电子关联→非经典光（压缩态/纠缠）
- `2111.10986` — Lee, Kim (2021)：MoS₂ 单层/双层 Berry 曲率公式，伪自旋 HHG 选择定则
- `1902.03421` — Yoshikawa et al. (2019)：谷极化 e-h 对，带间共振，MoSe₂/WSe₂/MoS₂/WS₂ 实验参数

### 新增核心文献（相位匹配+隧穿方向）

- `2404.01325` — Popmintchev et al. (2024)：相位失配公式，临界电离度，水窗（~330 eV），3 μm 驱动→多 keV
- `2104.06144` — Wang et al. (2021)：attoclock 隧穿时间，TCCSFA（Feynman 路径积分），24–58 as 隧穿延迟

### 检索方法规范化

- 确立正确流程：**arXiv 检索 → 人工验证 → deepxiv 获取**，摒弃凭记忆猜 arXiv ID 的做法（ID 复用导致漂移）
- 检索关键词：solid high harmonic generation theory Berry curvature semiconductor Bloch / high harmonic phase matching / high harmonic quantum optics
- deepxiv reader.py 编码 bug 修复（latin-1 → utf-8）已在本轮调研前完成

## v2.1.0 - 2026-05-19 deepxiv 知识库 v6 + PDF 全文增强

### 新增（deepxiv 流水线）

- `scripts/deepxiv_knowledge/pdf_extractor.py` — PDF 全文提取模块（PyPDF2）：碎片化检测、affiliation 过滤、章节解析、要点提取
- `scripts/deepxiv_knowledge/pdf_enricher.py` — PDF 增强流水线：`--all`（top 20）/ `--rebuild`（全量 61 篇）
- 扩展调研：新增 20 篇论文（实验方法 8 篇 + 光谱学原理 12 篇），总数 41 → **61 篇**

### 改进（fetch_core.py）

- 新增 `_extract_sections_from_head()`：优先使用 deepxiv 官方 section TLDR 解析（46 篇已用）
- 节名过滤：排除 Acknowledgment / References / Appendix 等非实质节
- 降级策略：head sections → preview → tldr 兜底
- `paper_reader.py` YAML 列表解析：修复 `"a, b, c"` 被逐字拆分的 bug

### 改进（run.py）

- v5 → **v6**：新增 `--rebuild` 强制重建标志
- 新增分支：sections 存在但无匹配节 → 回退 preview（无需重新获取 head）

### 内容质量（61 篇平均）

| 指标 | 增强前 | + PDF 增强后 |
|------|---------|---------------|
| 关键科学问题 | 1.0 条/篇 | **3.0 条/篇** |
| 核心发现 | 2.6 条/篇 | **6.0 条/篇** |
| 完全为空 | >0 篇 | **0 篇** |
| raw papers 大小 | ~40 KB | **285 KB** |

### 文档更新

- `docs/deepxiv-knowledge-workflow.md`：v5 → v6，新增 PDF 增强章节、数据源优先级 v6
- `scripts/README.md`：新增 deepxiv_knowledge / wiki_regenerator 模块清单

### 配置

- `~/.kimi/config.toml`：`max_steps_per_turn` 100 → **200**

### 已知问题

- `physics/9906053`（1999 年）无 PDF 存档，仅保留 abstract + tldr

---

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

## v2.2.0 - 2026-05-08 固体 HHG 理论方法文献调研

### 新增（knowledge base）

- `docs/solid-HHG-theory-methods-survey.md` — **34 KB 调研报告**，覆盖 10 个理论方向（A/B/C/D/E/F/G/H/I/J），所有内容直接来自 arXiv 论文真实文本

### 调研方向（10 个）

| 方向 | 主题 | 主要文献 |
|------|------|----------|
| A | Berry 相位/联络/结构规范 | 2111.08669 |
| B | SFQED 量子光学框架 | 1910.13791 |
| C | 半导体布洛赫方程（SBE）| 2304.12547 |
| D | 倒空间轨迹方法（RST）| 1809.08109 |
| E | 拓扑 HHG（Berry 曲率/陈数）| 1806.11232 |
| F | 阿秒条纹/隧穿时间测量 | 1707.05445 |
| G | 自旋/谷电子学 HHG | 1906.10224 |
| H | SFA 强场近似完整理论 | 1812.11447 |
| I | 偏振分辨 HHG 光谱（固体）| 1805.10453 |
| J | 分子自探测/轨道断层成像 | 2103.16228 |

### 关键方程提取（可复现性）

- Berry 曲率数值公式（Eq. 11）
- SFQED 三步量子化方案（分解 $A_c(t)$ + $A_q$）
- SBE 方程（密度矩阵形式，含退相干 $T_2$ 项）
- RST 四步模型（新增 pre-acceleration 步骤）
- Berry 曲率反常速度（$\dot{r} = \nabla_k\varepsilon + eE\times\Omega$）
- ADK 隧穿率公式
- Keldysh 参数 $\gamma = \omega\sqrt{2I_p/E_0}$

### 数值参数汇总

- ZnO SBE 计算：$\omega=0.014$ a.u., $F_{x0}=0.004$ a.u., 2D ($k_z=0$)
- Si HHG：2 μm 厚，2.1 μm，120 fs，0.6 TW/cm²，TDDFT 验证
- H 原子 attoclock：770 nm，6 fs，$0.84$ 椭圆率，$1.65$–$3.9\times10^{14}$ W/cm²

### 技术修复

- deepxiv SDK (`reader.py`) encoding bug：response.content.decode("utf-8", errors="replace") + json.loads() 替换 response.json()

