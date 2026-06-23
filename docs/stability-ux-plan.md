# 稳定性与用户体验优化计划（v3.3 设计稿）

> 状态：**已设计，待执行**
> 日期：2026-06-19
> 目标：主攻功能稳定性 + 功能间融洽性 + 用户友好性 + 结构清晰度

## 一、问题全景

全面体检发现 30 个问题，按严重度分 4 级：

| 级别 | 数量 | 含义 |
|------|------|------|
| P0 | 8 | 功能直接损坏（DOM id 错位/事件未绑定/选择器失效） |
| P1 | 14 | 隐患/边界情况/布局结构问题 |
| P2 | 8 | 体验不佳/文案不一致/缺引导 |
| P3 | 4 | 视觉细节/样式协调 |

## 二、P0 功能损坏（必须修，成本极低收益极大）

这些全是重构时 DOM 改名但 JS 没跟上的"断头线"，修复就是**对齐 id/选择器**。

### P0-1：任务看板 DOM id/状态值全错位（功能完全坏）
- **位置**：`index.html:184-195` 用 `task-backlog/active/completed` + `data-status=backlog/active/completed`；`web/js/task.js:23-27` 用 `task-todo/doing/done` + key `todo/doing/done`
- **影响**：任务看板三列永远空，新建任务无反馈
- **修复**：统一为 `backlog/active/completed`（与 HTML 的中文标签"待办/进行中/已完成"一致），task.js 改 id 和 status 枚举

### P0-2：设置抽屉学习配置全部失效
- **位置**：`settings.js:145-161` 读写 `learning-enabled/auto-review/interval`，但 HTML 用 `learning-auto-enabled/strategy/source-*/daily-quota/cost-limit`；`save-learning-config` 按钮未绑定事件
- **影响**：学习配置保存无反应
- **修复**：重写 `load/saveLearningConfig` 对接 HTML 现有 id，补 click 绑定

### P0-3：NSFC 讨论工具栏插入失败
- **位置**：`projects.js:193` 用 `.chat-messages` 选择器，但 HTML 里是 `.messages`
- **影响**：讨论总结→提交→反馈 hermes 闭环断裂
- **修复**：选择器改为 `.messages`

### P0-4：LLM Provider 状态从不更新
- **位置**：`settings.js:44-45` 写 `llm-provider/llm-model`（不存在），顶栏 `provider-badge` 初始 "auto" 从不更新
- **影响**：用户看不到当前用的哪个模型
- **修复**：loadLLMStatus 同时写入 `provider-badge` 和设置面板

### P0-5：用量统计两套实现冲突
- **位置**：`app.js:316` vs `settings.js:89` 对 `/api/usage` 期望不同结构；`usage-status` 永远"加载中"
- **影响**：用量数据显示不出来
- **修复**：统一 API 契约和渲染

### P0-6：心跳状态指示器是死的
- **位置**：`settings.js:8` 操作 `status-dot`（不存在）
- **修复**：用 `status-text` 或在 statusbar 加状态圆点

### P0-7：模式徽章缺 deep-talk/quick-check 映射
- **位置**：`settings.js:24-30` 只有 `co-working/autonomous/review`
- **修复**：补全 `deep-talk→深度对话` `quick-check→快速验证`

### P0-8：工具栏任务按钮窄屏失效 + 无效 flash
- **位置**：`app.js:307-315`，`panel.style.flash='1'` 是无效属性
- **修复**：窄屏弹提示，移除 flash，加滚动高亮

## 三、P1 布局与稳定性

### P1-1：五栏布局挤压知识库预览
- **问题**：实际五栏（会话260+文件树280+预览flex+聊天400+任务260），1440px 屏留给预览仅~240px
- **方案**：right-sidebar（任务面板）默认折叠/隐藏，任务改为工具栏弹窗。给知识库预览让出空间

### P1-2：init 不自动选会话 + welcome 不显示
- **问题**：首屏聊天区完全空白
- **方案**：无会话时显示 welcome-screen（含快速引导），有会话自动选最新

### P1-3：移动端未处理 kb/chat
- **问题**：<900px 知识库和聊天互相挤压
- **方案**：底部 tab 切换（📚知识库 / 💬聊天），单栏全屏

### P1-4：聊天折叠无新消息提示
- **方案**：折叠态 toggle 加未读角标，SSE done 时若折叠则闪烁

### P1-5：hermes run 后知识库不刷新
- **方案**：oneshot done 后调 `renderKbTree()` + toast "知识库已更新"

### P1-6：筛选器死锁
- **问题**：filter-bar 隐藏时 select 也隐藏，无法点开筛选
- **方案**：改为"筛选"按钮触发展开

### P1-7：SSE 流式重复渲染卡顿
- **方案**：增量渲染/节流；检测用户是否在底部，不在底部不自动滚

### P1-8：escapeHtml 重复定义 + onclick 字符串拼接
- **方案**：统一用 core.js 的；改事件委托避免拼接

## 四、P2 功能融洽与用户友好

### P2-1：知识库与项目面板"文献"内容重叠
- **方案**：明确职责——知识库=沉淀后浏览，项目面板=待决策候选流；加跳转互链

### P2-2：文献反馈流程跨面板，难理解
- **方案**：文献生命周期进度条（未看→感兴趣→讨论中→已沉淀）

### P2-3：@知识库注入不透明
- **方案**：输入框上方常驻 chip 列表显示已注入文件，可移除

### P2-4：缺引导/空状态
- **方案**：首屏 3 步引导卡（建会话/看知识库/试发消息）

### P2-5：文案不一致（归档按钮名实不符、搜索入口重复、/mode 命令无用）
- **方案**：统一命名，移除/改造无功能按钮

### P2-6：错误处理混杂（静默/toast/alert 三种）
- **方案**：统一 toast，关键错误加重试按钮

### P2-7：操作反馈/loading 不一致
- **方案**：统一 loading 规范，工具栏按钮加 active 态

## 五、P3 视觉协调

### P3-1：内联 style 在深色模式刺眼
- **方案**：抽 class + CSS 变量，补 task-priority 深色适配

### P3-2：工具栏 7 emoji 密度高
- **方案**：加文字 label 或分组（知识库/协作/工具）

### P3-3：details 双重接管（原生 marker + JS preventDefault）
- **方案**：统一为原生或全接管

### P3-4：字号层级过碎（10+ 种 rem 值）
- **方案**：定义 4-5 级 type scale token

## 六、实施路线（4 个迭代）

### 迭代 1：P0 功能修复（最高优先，预计半天）
修 8 个功能损坏——全部是 id/选择器对齐，改动极小但收益极大：
1. 任务看板 id/状态统一
2. 学习配置对接 + 按钮绑定
3. NSFC 讨论选择器修复
4. Provider 状态显示
5. 用量统计统一
6. 心跳状态指示
7. 模式徽章补全
8. 任务按钮窄屏

### 迭代 2：布局优化（预计 1 天）
1. right-sidebar 默认折叠（让知识库预览有空间）
2. welcome-screen 首屏显示 + 自动选会话
3. 移动端 tab 切换
4. 聊天折叠未读角标

### 迭代 3：功能融洽（预计 1 天）
1. 文献生命周期进度条
2. @知识库注入透明化（chip 列表）
3. hermes run 后自动刷新知识库
4. 筛选器改按钮触发展开
5. 知识库与项目面板职责划分

### 迭代 4：体验打磨（预计半天）
1. 首屏引导卡
2. 文案统一（归档/搜索/命令）
3. 错误处理统一 toast
4. 工具栏分组 + label
5. CSS 变量统一 + 深色适配
6. type scale 规范

## 七、验证标准

- 所有 P0 修复后手动验证功能可用（任务看板/学习配置/讨论闭环/Provider显示/用量）
- self_test 88/88 + web_api 26/26 不回归
- 首屏不再是空白/拥挤，新用户能理解布局
- 文献反馈流程能走通完整链路
- 移动端基本可用（知识库/聊天可切换）

## 八、盲区补充（第二轮审计发现）

> 第一轮体检聚焦 DOM 断头线/布局/流程，第二轮审计发现 8 个被忽略的维度。

### 数据安全（最高优先，用户数据无价）

**P0-9：删除操作零保护** `web_server.py:1495`
- DELETE wiki/消息/任务直接 unlink/覆写，无回收站、无备份前置、前端无二次确认
- **修复**：DELETE 前调 `backup_manager.create_backup()`；前端删除统一二次确认；wiki 改软删除（移到 `.trash/`）

**P0-10：备份按钮是死的** `app.js:70`
- "备份"只弹 toast 让用户去终端跑，Web 从未真正触发备份
- **修复**：新增 `/api/backup`（list/create/restore），设置面板的备份按钮真正可用

### 并发安全（索引/消息损坏风险）

**P1-9：文件写入无锁** `knowledge_base.py:1300`
- index.json(44MB)/messages.json/graph.json 的 read-modify-write 无任何锁，多线程并发会互相覆盖
- **修复**：统一 `threading.Lock` 包裹关键文件写入

**P1-10：SSE 流式切换会话不中断** `session.js:62`
- 流式中切会话，旧 stream 继续向已清空的 DOM 写入，切回来看到半截消息
- **修复**：switchSession 开头判断 isStreaming，cancel reader + reset 状态

**P1-11：同步/重建无防重入** `kb.js:387`
- 同时点"同步"+"重建"会并发读写同一 index.json
- **修复**：服务端 `_busy` 标志，重复请求返回 409

### 性能瓶颈

**P1-12：索引重建同步阻塞** `web_server.py:866`
- 44MB index.json 全量重建同步返回，请求 hang 数秒到数十秒
- **修复**：改后台线程 + 前端进度提示；或用增量 build_index(force=False)

### 安全性（XSS）

**P1-13：renderMarkdown 链接协议未校验** `core.js:88`
- `[x](javascript:alert(1))` 会生成可执行链接
- **修复**：href 协议白名单（只允许 http/https/mailto）

**P1-14：raw 文件预览未 sanitize** `kb.js:154`
- raw 里的 HTML/SVG 经简单正则后 innerHTML，潜在 XSS
- **修复**：渲染前 escapeHtml 或白名单标签

### 状态一致性

**P1-15：标签编辑后跨面板不刷新** `kb.js:674`
- 知识库改标签后，文件树计数/项目面板/搜索索引都不会更新
- **修复**：写成功后 renderKbTree() + 事件广播；save_wiki_page 触发增量索引

### 离线/断网体验

**P2-14：无全局断网提示** `core.js`
- API 失败只零散 toast"加载失败"，无"服务已断开"全局横幅
- **修复**：online/offline 监听 + fetch 失败计数 + 顶部横幅

**P2-16：长任务无前端超时** `apiPost`
- 同步/重建/学习触发无超时，fetch 无限等
- **修复**：apiPost 加可选 timeout，长任务默认 60s

### 无障碍

**P2-10：零 aria-label** `index.html:14-78`
- 全仓无 aria-label/role/tabindex，屏幕阅读器不可用
- **修复**：图标按钮补 aria-label，emoji 包 aria-hidden

**P2-11：键盘不可达** `core.js:170`
- 模态框无 ESC 关闭、无 focus trap，文件树无方向键
- **修复**：ESC 关模态 + focus trap + 关键容器加 role

### 新用户上手成本

**P2-18：术语门槛极高**
- "林赛/hermes/Agora/BRAIN/seedling/蒸馏"等大量自造术语，新用户 5 分钟无法理解
- **修复**：welcome-screen 内置术语词典 + 3 步引导；工具栏按钮加 `?` 帮助气泡

---

*基于 v3.2.0 全面体检制定。第一轮聚焦 DOM 断头线/布局/流程；第二轮审计补充数据安全/并发/安全/一致性/可达性/上手成本 8 个盲区。两轮共发现 48 个改进点。*
