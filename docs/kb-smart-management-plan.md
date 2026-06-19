# 知识库智能管理计划（v3.1 设计稿）

> 状态：**已设计，待执行**（2026-06-19）
> 目标：知识库从"手动整理"升级为"自维护+灵活分类"

## 一、核心理念

知识库不能靠每次手动整理。它应该能：
1. **自动捕获新增**（hermes 每天产出 → 自动同步进知识库）
2. **自动健康维护**（索引/图谱/孤儿/一致性，一键或定时）
3. **灵活分类**（智能分类 + 自定义分类 + 临时分类搜索）
4. **渐进生长**（理解深入时自动升级阶段，不丢失旧理解）

原则：**raw 层不轻易动**（论文元数据是事实），wiki 层可自由生长（理解会变化）。

## 二、现有基础设施（已完成）

调研确认以下能力已存在：

| 能力 | 状态 | 位置 |
|------|------|------|
| 索引重建/孤儿清理/健康报告 | ✅ 已接入前端（健康面板4按钮） | kb_maintenance.py |
| 单篇导入+深分析 | ✅ 文献反馈链路 | kb_importer.py |
| 多端同步 | ✅ 项目面板同步tab | sync_engine.py |
| 智能生长建议+确认 | ✅ suggest/grow API | kb_importer.py |
| 手动创建 stub | ✅ Wiki tab | knowledge_base.py |
| hermes cron 控制 | ✅ hermes控制台 | hermes_bridge.py |
| 别名编辑器 | ✅ 别名tab | aliases.json |
| 生长日志 | ✅ 自动记录 | growth-log.json |

## 三、需要补的 7 个缺口

### 缺口 1：自动定时同步（最关键）
**问题**：hermes 每天 08:23 产出简报，但林赛侧只能手动点"立即同步"。
**方案**：新增 `scripts/kb_auto_sync.py`，作为 LaunchAgent 每天定时跑：
- 09:00 触发 `sync_engine.sync_all()`（同步新增会话+候选论文）
- 同步后自动 `kb_maintenance.cmd_reindex()`（重建索引）
- 同步后自动更新图谱（补缺口2）
- 结果写入 `memory/sync-state.json` 的 history
- **前端**：知识库面板加"自动同步状态"指示器（上次同步时间/新增数）

### 缺口 2：批量导入不更新图谱
**问题**：import_candidate/import_deep_analysis 直接 write_text，绕过 save_wiki_page，图谱不更新。
**方案**：
- 方案A（推荐）：在 `kb_maintenance` 新增 `cmd_rebuild_graph` 子命令，从所有 wiki frontmatter 的 related/project 字段反向重建图谱（reindex 时顺便做）
- 方案B：改 import_* 函数，导入后调 update_graph_node/add_graph_edge
- 选 A：更稳健，一次性修复所有历史导入的图谱断层

### 缺口 3：import_all_candidates 死代码
**问题**：kb_importer.py 的 def 行缺失，函数不可调用。
**方案**：修复 def 行，接入前端"批量导入当日简报"按钮。

### 缺口 4：同步后不自动 reindex
**问题**：sync_all 完成后只 print 提示，需手动点重建。
**方案**：sync_all 末尾自动调 `kb.build_index(force=True)`。

### 缺口 5：别名无自动学习
**问题**：25 组别名全手写，无法从使用中学习。
**方案**：新增 `scripts/alias_learner.py`：
- 从图谱 same_as 边提取已声明的同义关系
- 从 [[]] wikilink 的别名用法提取（如 `[[三步模型|半经典模型]]`）
- 从检索 miss 日志提取（用户搜了 X 但命中的是 Y → X 可能是 Y 的别名）
- 生成候选列表，用户在别名 tab 一键确认
- **前端**：别名 tab 加"🔍 发现新别名候选"按钮

### 缺口 6：growth_stage 无自动晋升
**问题**：seedling→growing→mature 全靠人改 frontmatter。
**方案**：新增规则引擎（轻量）：
- 被 ≥3 篇 raw 论文引用 → seedling→growing
- 被 ≥5 篇引用 + 被检索命中 ≥10 次 → growing→mature
- 内容字数 >2000 且有 related → 自动 mature
- **前端**：wiki 详情加"阶段"徽章 + 手动晋升按钮（覆盖自动规则）

### 缺口 7：前端缺少一键操作按钮
**问题**：现有按钮分散在多个 tab，核心操作没有快捷入口。
**方案**：知识库主区文件树顶部加"管理工具栏"：
```
[🔄 一键同步+重建] [📊 健康检查] [🏷️ 分类管理] [🔍 别名发现]
```
- 一键同步+重建 = sync_all + reindex + rebuild_graph（串联）
- 健康检查 = 现有 cmd_health
- 分类管理 = 打开分类面板（见下）
- 别名发现 = 调 alias_learner

## 四、灵活分类系统（你的核心需求）

### 分类三层设计

#### 第1层：智能分类（自动，基于内容）
- 导入时根据 direction/tags/title 关键词自动归入子库（已有 infer_project）
- 扩展：从论文摘要提取主题关键词，匹配已有概念，自动连 related 边
- 一个文件可属于多个分类（project 字段是数组）

#### 第2层：自定义分类（你添加，自动关联）
- 你可以创建自定义分类（如"水窗成像"、"拓扑材料HHG"）
- 创建分类时指定关键词规则（如"水窗 AND 成像"）
- 系统自动扫描全库，把匹配的文件关联到该分类
- 分类本身是一个 wiki/projects/ 下的 MOC 页（带 [[]] 链接）
- **前端**：文件树加"📁 分类"区，可新建/编辑/删除分类

#### 第3层：临时分类搜索（即时，不持久化）
- 搜索框支持高级语法：`tag:HHG stage:mature project:NSFC`
- 搜索结果可临时分组（按 type/stage/project/tag 分组显示）
- 不创建永久分类，只影响当前视图
- **前端**：搜索框下方加"筛选器"栏（type/stage/project/tag 下拉）

### 分类管理 UI（文件树顶部）
```
📁 分类管理
  智能分类（自动）:
    📐 deepxiv-论文库 (106篇)
    📁 NSFC-强场超快 (16篇)
  自定义分类（你创建）:
    ➕ 新建分类...
    📂 水窗成像 (3篇) [编辑] [删除]
    📂 拓扑HHG (5篇) [编辑] [删除]
  筛选器:
    [类型▼] [阶段▼] [子库▼] [标签▼]
```

## 五、前端改动总览

### 知识库主区文件树顶部：管理工具栏
```
┌─────────────────────────────────────┐
│ 🔍 [搜索框]                          │
│ [🔄同步] [📊健康] [🏷️分类] [🔍别名]  │  ← 管理工具栏
├─────────────────────────────────────┤
│ 🗺️ 知识地图                          │
│ 📐 概念 (11)                         │
│ 🛠️ 方法 (8)                          │
│ ...                                  │
│ 📁 分类                              │  ← 新增分类区
│   📂 水窗成像 (3)                     │
│   ➕ 新建分类                         │
│ 📄 论文库 (106)                      │
└─────────────────────────────────────┘
```

### 每个文件项：分类标签可编辑
- 文件预览区显示该文件的分类标签（project + tags）
- 可点击标签快速筛选
- 可添加/移除标签（内联编辑）

## 六、实施路线（分 3 个迭代）

### 迭代 1：自维护闭环（最高优先）
1. 修复 import_all_candidates 死代码
2. kb_maintenance 新增 cmd_rebuild_graph（反向重建图谱）
3. sync_all 末尾自动 reindex
4. 新增 kb_auto_sync.py LaunchAgent（每日定时同步+重建）
5. 前端文件树顶部加"🔄一键同步+重建"按钮
6. 前端加自动同步状态指示器

### 迭代 2：灵活分类
7. 自定义分类系统（新建分类+关键词规则+自动关联）
8. 前端分类管理 UI（文件树的分类区）
9. 搜索筛选器（type/stage/project/tag）
10. 文件预览区的标签内联编辑

### 迭代 3：智能增强
11. alias_learner.py（别名自动发现）
12. growth_stage 自动晋升规则引擎
13. 导入时自动提取主题关键词连 related 边
14. 健康检查增强（分类覆盖率/图谱连通性/别名命中率）

## 七、数据安全约束

- **raw 层只增不改**：论文元数据是事实，导入后不修改（除非显式删除）
- **wiki 层可生长**：笔记内容可更新，但保留 growth-log 追溯
- **图谱可重建**：graph.json 是程序生成的，随时可从 frontmatter 反向重建
- **分类可撤销**：自定义分类删除时只移除关联，不删文件
- **别名需确认**：自动发现的别名候选需用户确认才生效

## 八、技术约束

- 仅 Python 标准库（LaunchAgent 用 plist）
- 前端零框架（原生 JS）
- 复用现有 kb_maintenance/sync_engine/kb_importer/knowledge_base 函数
- 不破坏现有功能（增量改进，不重写）

## 九、已知 Bug（待修复）

> 以下 bug 在 v3.0.0/v3.0.1 重构后发现，待执行迭代计划时一并修复。

### 🔴 BUG-A：聊天功能异常（v3.0.0 布局重构引入）
- **症状**：用户反馈"聊天也出问题了"（2026-06-19）
- **可能根因**：v3.0.0 把 chat-area 拆为 kb-main + chat-sidebar，聊天相关 DOM 元素（messages/typing-indicator/welcome-screen/input-area）被移动到新容器，但以下可能断裂：
  - `sendMessage` / `appendMessage` / SSE 流式引用的元素 ID 可能找不到（如 `#messages`、`#message-input`、`#typing-indicator`）
  - 事件绑定（send-btn click、message-input keydown、upload）可能在 `bindEvents()` 执行时元素还未渲染（如果 chat-sidebar 的 inner 被异步加载）
  - `State.currentSessionId` / `loadMessages` 等引用 `#messages` 容器可能失效
  - 欢迎屏（`#welcome-screen`）的快速启动按钮（quick-starts）在迁移时被删除了（新 HTML 里 welcome-screen display:none 且无 quick-starts 内容）
  - CSS：`.messages` / `.input-area` / `.typing-indicator` 的 flex 布局可能在新的 `.chat-sidebar-inner` 容器里高度塌陷（聊天区没有撑满侧栏高度）
- **排查方向**：
  1. 浏览器 F12 控制台看有无 JS 报错（元素找不到/函数未定义）
  2. 检查 `document.getElementById('messages')` 等是否返回 null
  3. 检查 `.chat-sidebar-inner` 的 flex 布局是否让 `.messages` 正确撑满
  4. 确认 send-btn/message-input/upload-btn 的事件绑定在 DOM 就绪后执行
  5. 确认 SSE 流式的 `data: ` 事件仍能正确推送到侧栏内的消息容器
- **修复优先级**：🔴 最高（聊天是核心功能，不能退化）
- **修复约束**：不能回退 v3.0.0 的知识库主区布局，需在侧栏容器内修复

---

*这份计划完善了用户的思路：自维护闭环 + 三层灵活分类 + 智能增强。待 token 充裕时按迭代执行。*
