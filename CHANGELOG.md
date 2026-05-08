# 变更记录

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
