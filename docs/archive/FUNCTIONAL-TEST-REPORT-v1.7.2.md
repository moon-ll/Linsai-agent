# LinSai-CoPilot 功能测试报告（模拟用户）

**版本**: v1.7.2
**时间**: 2026-05-11 22:25:06
**测试代理**: 子代理模拟真实用户

---

## 执行摘要

| 指标 | 数值 |
|------|------|
| 测试场景 | 4 个 |
| 总检查点 | 65 |
| 通过 | 61 |
| 失败 | 4 |
| 阻塞问题 | **有 1 个**（copilot_engine CLI 入口崩溃） |

**总体评价**：核心模块、Web API、上下文构建、任务与会话管理均正常工作。存在 1 个明确的代码缺陷导致 CLI 主入口完全不可用，需优先修复。

---

## 场景 1：模块级功能测试

在真实项目目录中执行，使用隔离的测试标识符，测试后全部清理。

| 模块 | 测试项 | 结果 | 备注 |
|------|--------|------|------|
| session_manager | 创建会话 | ✓ | session_id=20260511-功能测试会话-模块测试 |
| session_manager | 追加消息 | ✓ | msg_id=msg_001 |
| session_manager | 加载会话 | ✓ | 消息内容与状态一致 |
| session_manager | 列出会话 | ✓ | 在 all 列表中正确出现 |
| session_manager | 归档会话 | ✓ | 成功移入 archived/ |
| task_manager | 创建任务 | ✓ | task_id=TASK-20260511-功能测试任务 |
| task_manager | 读取任务 | ✓ | 标题正确 |
| task_manager | 状态流转 backlog→active | ✓ | 成功 |
| task_manager | 验证active状态 | ✓ | status==active |
| task_manager | 更新进度 | ✓ | progress=30 |
| task_manager | 添加子任务 | ✓ | 子任务数=1 |
| task_manager | 切换子任务 | ✓ | done=True，自动触发 completed（符合预期） |
| task_manager | 列出active任务 | ✓ | 正确处理自动完成状态 |
| task_manager | 状态流转 active→completed | ✓ | 因自动完成跳过，行为符合设计 |
| task_manager | 删除任务 | ✓ | 成功删除 |
| context_builder | 返回system_prompt | ✓ | 长度=5869 |
| context_builder | 返回messages | ✓ | 条数=3（历史2+当前1） |
| context_builder | 返回_budget | ✓ | 包含 allocations/total_budget |
| context_builder | 人格锚点注入 | ✓ | 包含"林赛"或"Lin Sai" |
| knowledge_base | 索引状态 | ✓ | 返回 indexed/raw_count/wiki_count 等 |
| knowledge_base | 搜索固体 | ✓ | 返回列表 |
| knowledge_base | should_search_knowledge(技术) | ✗ | 返回 False。原因：测试查询长度42字符，未超过 co-working 模式阈值50字符，符合设计预期 |
| knowledge_base | should_search_knowledge(闲聊) | ✓ | 返回 False，正确过滤 |
| skill_manager | 列出技能 | ✓ | 数量=8 |
| skill_manager | self-test技能存在 | ✓ | 在列表中 |
| skill_manager | 关键词搜索 | ✓ | 返回列表 |
| skill_manager | 技能匹配激活 | ✓ | 返回列表（当前配置下为空，见下方说明） |
| proactive_engine | classify co-working | ✓ | 返回 co-working |
| proactive_engine | classify quick-check | ✓ | 返回 quick-check |
| proactive_engine | classify deep-talk | ✓ | 返回 deep-talk |
| proactive_engine | 自主级别设置/读取 | ✓ | suggest/suggest |
| proactive_engine | 压力信号检测 | ✓ | 检测到 high 风险 |
| proactive_engine | heartbeat | ✓ | 返回列表，信号数=1 |
| llm_router | 状态结构 | ✓ | 包含 providers/strategy/active_provider |

**场景1小结**：33/34 通过。唯一"失败"项为 `should_search_knowledge` 对短查询的判定，系测试查询未满足长度阈值（>50字符），属预期行为，非功能缺陷。

---

## 场景 2：Web API 测试

Web 服务器启动在 **127.0.0.1:18080**（非默认端口，避免冲突），测试后停止并清理会话数据。

| 端点 | 方法 | 状态码 | 关键字段验证 | 结果 |
|------|------|--------|-------------|------|
| /api/version | GET | 200 | version=1.7.2 | ✓ |
| /api/sessions | GET | 200 | 返回会话列表数组 | ✓ |
| /api/tasks | GET | 200 | 返回任务列表数组 | ✓ |
| /api/skills | GET | 200 | 包含 self-test 技能 | ✓ |
| /api/knowledge | GET | 200 | 返回索引状态（indexed/raw_count/wiki_count） | ✓ |
| /api/llm-status | GET | 200 | 返回 providers/strategy/active_provider | ✓ |
| /api/heartbeat | GET | 200 | 返回 reminders 数组 | ✓ |
| /api/sessions | POST | 200 | 创建成功，返回 session_id | ✓ |
| /api/sessions/{id}/messages | GET | 200 | 返回消息数组 | ✓ |
| /api/sessions/{id}/keywords | GET | 200 | 返回关键词数组 | ✓ |
| /api/sessions/{id}/messages | POST | 400 | 空内容返回 400（验证路由存在） | ✓ |
| /api/tasks/{task_id} | GET | 200 | 返回单个任务详情 | ✓ |
| /api/tasks/{task_id}/progress | PUT | 200 | 更新进度成功 success=true | ✓ |
| /api/references | GET | 200 | 返回参考文献列表 | ✓ |
| /api/usage | GET | 200 | 返回用量统计（daily/total/by_provider） | ✓ |

**场景2小结**：15/15 全部通过。所有 API 路由响应正常，JSON 格式正确，CORS 头正常。

---

## 场景 3：CLI 测试

| 命令 | 结果 | 输出摘要 |
|------|------|---------|
| `python3 scripts/copilot_engine.py --list` | ✗ | 模块级 `detect_llm_cli()` 崩溃：`TypeError: string indices must be integers`。根因：`for s in status:` 遍历的是字典键而非 `status["providers"]` 列表 |
| `python3 scripts/copilot_engine.py --start "功能测试会话" --mode co-working` | ✗ | 同上，`__main__` 中首行调用 `detect_llm_cli()` 即崩溃，无法进入交互模式 |
| `python3 scripts/llm_router.py --status` | ✓ | 正确显示 minimax(api)/kimi(cli)/claude(cli) 状态，active_provider=minimax |
| `python3 scripts/web_server.py --self-check` | ✓ | WEB_DIR/流式切分/代码块保留/空文本处理 全部通过 |
| `python3 scripts/self_test.py --json` | ✓ | 85/85 全部通过，耗时 0.045s，三套件（核心模块/人格一致性/场景剧本）零失败 |

**场景3小结**：3/5 通过。`copilot_engine.py` 的 CLI 入口因 `detect_llm_cli()` 的 bug 完全不可用，**这是阻塞级缺陷**。

---

## 场景 4：集成场景（固体HHG研究者链路）

模拟一个固体 HHG 研究者的完整使用链路，测试后全部清理。

| 步骤 | 操作 | 结果 | 备注 |
|------|------|------|------|
| 1 | 创建会话 "固体HHG相位匹配问题" | ✓ | session_id=20260511-固体HHG相位匹配问题 |
| 2 | 追加3条消息（用户→林赛，林赛→用户，用户→林赛） | ✓ | msg_001~003 成功写入 |
| 3 | 调用 build_context 验证人格锚点 | ✓ | system_prompt 包含"林赛"，长度=6721 |
| 4 | 创建关联任务 "优化固体HHG相位匹配" | ✓ | task_id=TASK-20260511-优化固体HHG相位匹 |
| 5 | 任务流转到 active | ✓ | 成功，且自动同步到 working-context |
| 6 | 更新任务进度为 30 | ✓ | progress=30 |
| 7 | 搜索知识库 "相位匹配" | ✓ | 返回2条结果 |
| 8 | 列出技能，确认 experiment-design 被激活 | ✗ | 返回空列表。原因：`memory/skills-state.json` 当前为 manual 模式，仅激活 math-derivation 和 code-review。功能本身正常，是配置状态导致 |
| 9 | 检测压力信号（会话不含压力词） | ✓ | has_stress=False，risk=none |
| 10 | 归档会话 | ✓ | 成功移入 archived/ |
| 11 | 删除任务 | ✓ | 成功删除 |

**场景4小结**：10/11 通过。步骤8因手动技能配置未激活 experiment-design 而返回空列表，非功能缺陷。

---

## 发现的问题

### 问题1：copilot_engine.py CLI 入口崩溃（阻塞级）
- **位置**：`scripts/copilot_engine.py:108-109`
- **现象**：运行任何 `python3 scripts/copilot_engine.py <args>` 都会崩溃
- **根因**：`detect_llm_cli()` 中 `for s in status:` 直接遍历 `lr.get_status()` 返回的字典，得到的是字符串键（如 `"providers"`），而非 `status["providers"]` 列表。随后 `s["type"]` 触发 `TypeError: string indices must be integer`
- **修复建议**：将 `for s in status:` 改为 `for s in status.get("providers", []):`
- **影响**：CLI 主入口完全不可用，用户无法通过终端创建/续接/列出会话

### 问题2：知识库短查询未触发检索（预期行为，但可优化测试）
- **位置**：`scripts/knowledge_base.py:143-167`
- **现象**：`should_search_knowledge("帮我看看固体HHG光路设计...", "co-working")` 对 42 字符的查询返回 False
- **根因**：`co-working` 模式要求 `len(text) > 50` 才配合 `_has_tech_terms` 触发检索
- **判定**：非缺陷，但测试用例应使用更长查询以覆盖该分支

### 问题3：技能配置为 manual 模式导致 experiment-design 未激活（配置状态）
- **位置**：`memory/skills-state.json`
- **现象**：`mode: manual`，`active_skills: ["math-derivation", "code-review"]`
- **根因**：项目当前配置为手动模式，仅开启两个技能
- **判定**：非缺陷，功能正常。建议在测试前重置为 auto 模式或标注为环境状态

---

## 结论

**整体评价：v1.7.2 核心功能稳固，但 CLI 主入口存在阻塞级缺陷。**

- **Web 界面与 API**：全部正常，15 个端点零失败，可作为主要交互入口使用。
- **模块功能**：会话/任务/上下文/知识库/主动感知/LLM 路由等核心模块均通过测试。
- **自测系统**：`self_test.py` 85/85 通过，内测覆盖完整。
- **CLI 入口**：`copilot_engine.py` 因 `detect_llm_cli()` 的遍历逻辑错误完全崩溃，需立即修复。

**建议优先级**：
1. **P0**：修复 `copilot_engine.py:108` 的 `for s in status:` → `for s in status.get("providers", []):`
2. **P1**：在 `skills-state.json` 被手动修改后，文档中提醒用户可能的影响
3. **P2**：考虑适当降低 `should_search_knowledge` 在 co-working 模式下的长度阈值，或增加字符数/词数双维度判断

---

*报告生成时间：2026-05-11 22:25:06*
*测试环境：macOS，Python 3.9.6，零第三方依赖*
