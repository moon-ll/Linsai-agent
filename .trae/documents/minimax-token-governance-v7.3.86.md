# MiniMax Token 系统性治理（v7.3.86）

## Context

现象：11-16 凌晨 MiniMax 额度恢复后 5 小时烧 142k token，用户要求系统性解决"消耗比之前严重"。

账本实证（step-usage-2026-11.jsonl，代码探查交叉验证）：

1. **双烧通道（占 11-16 可见消耗 38%）**：`literature_service` 在 hermes researcher 超时（480s，内部已烧多轮）后，把同一份 ~29k 字符文档**无标签全文直灌 MiniMax-M3**（无联网能力，只回 ~200 字符，近乎纯烧）。10-29 以来累计 40 对，11-16 两对即 61.4k。
2. **v7.3.82（11-15）停用 kimi 的副作用**：全局链变 minimax→minimax-fallback→glm→…，14 处无 prefer 标签的直调此前烧 kimi 池、现在全部先打 M3——这是"之前没这么严重"的结构性原因。v7.3.83/84 的降耗治理只覆盖带标签任务，无标签族没吃到红利。
3. **M3 思考不可关**（项目内实证仅 GLM 支持 thinking:disabled）：直调单次成本 2.27k→3.23k→4.57k token/次；v7.3.81 think-only 升预算重试（16384）11-16 首次真实生效 2 对（4096 白烧 + 重试侧 7.7k/10.7k completion）。
4. 消耗拐点其实在 10-29~11-11（活跃日均 356~514k），11-16 折算 ~326k/天未创新高；体感严重主因是 11-14/15 两天配额尽零消耗后的积压在恢复后头 5 小时集中释放。

**不在本次范围**（另行裁决，不改）：hermes profiles 默认模型（~/.hermes 域）；micro-scheduler 夜间降频（吞吐策略）；hermes 内部 loop 逐条入账（~/.hermes 域）；researcher 超时 480s 不回退（v7.3.81 按 p99=441s 锚定依据充分）。

## 改动项（按优先级，各自独立可回滚）

### P0 删除 literature_service 双烧降级直调（最高单点收益）

文件：`scripts/literature_service.py`

- `:909-921` `_dispatch_researcher` 方案B（`llm_complete` 全文直调）整体删除：hermes 失败/超时直接返回空 results。
- `:1500-1506` `_dispatch_deep_read` 方案B 删除：失败走 `:1508` 占位符 `"> 深度阅读未执行"`。
- 安全性已验证：`search()` 返回空列表时 executor 按"无新论文"成功放行（executor.py:973-994，仅异常才 success:False 触发 attempts<3 重试，无死循环）；deep_read 占位符被 `_fallback_read` 视为有效 content，不污染 KB。
- **用户裁决①**：deep_read 方案B 直接删（推荐：无联网 → 近年小众论文参数化知识不可靠，幻觉笔记污染 KB，v7.3.85 刚清完噪音）还是保留但加 `prefer="governance"` 走 glm？

### P1a 注册 weekend_output → glm-first（补漏，一行）

文件：`scripts/llm_router.py` `TASK_PROVIDER_PREFS`（:167-190）

- 加 `"weekend_output": ("glm", "glm-fallback")`。`TASK_MAX_TOKENS` 已有 16384 预算、output_jobs.py:66 已传标签，但偏好未注册 → 落全局 minimax 链，纯遗漏。
- **用户裁决②**：是否并入 `TASKS_DISABLE_THINKING`。推荐**不并入**——weekend_output 是长文生成类（周末课题撰写），关思考伤质量；关思考只留给结构化抽取/格式化类（weekend_input、kb_distill*）。

### P1b 机械/判断类无标签直调补 governance 标签（→ glm-first）

逐文件加 `prefer="governance"`（`llm_gateway.llm_complete` 已支持透传；`router.call_llm` 第 4 参）：

| 文件:行 | 任务 |
|---|---|
| scripts/chat_archive.py:187 | 关键词提取（机械） |
| scripts/kb_merger.py:227 | 双页融合（格式化） |
| scripts/web_routes_system.py:955 | 对话审核判定（判断 JSON） |
| scripts/web_routes_tasks.py:168 | 任务拆解（结构化判断） |
| scripts/project_workflow.py:202 | 任务拆解（结构化判断） |
| scripts/lifecycle/executor.py:704 | gap_identify gaps JSON（结构化判断） |

保留 M3 不动（既有"执行/生成类走 M3"分工）：copilot_engine.py:215-287、idea_generator.py:391/929、executor.py:2156 update_vision、proposal_writer/topic_generator/question_architect。`learning_engine.py:134` 为共享 wrapper，形态未逐个核实 → **待观测**，下轮账本看分布再裁决。

- **用户裁决③**：以上名单确认或增删。

### P2 think-only 升预算重试观测字段（不改行为，证据先行）

文件：`scripts/llm_router.py:251` `_record_llm_call` / `scripts/step_usage.py:106` `record_call` 增可选 `note` 字段（加性，聚合按固定键不受扰）；升预算重试行记 `note="think_only_retry:16384"`。部署 24-48h 后按 completion 分布再裁决是否下调 8192 或按 prompt 尺寸缩放（当前仅 2 对样本，证据不足不硬调）。

## 测试

- 新建 `scripts/tests/test_literature_no_dual_burn.py`：monkeypatch `hermes_memory._run_hermes_agent` 返回 `{"success": False}` + 假 `llm_gateway.llm_complete` 计数（手法参照 `test_llm_router_no_think.py` 的 fake 注入），断言：llm_complete 零调用、`search()` 返回 `[]`、deep_read 返回占位符。
- 扩展 llm_router 测试：`TASK_PROVIDER_PREFS` 含 weekend_output 且链序为 (glm, glm-fallback)。
- P1b 各文件：fake router/gateway 捕获 prefer 参数，断言 = "governance"。
- 跑法：`python3 -m unittest discover scripts/tests`（或按 tests 目录既有单文件跑法）。

## 回滚

每项独立 commit，可单独 revert；P1a 删一行即回滚；P0 恢复两段 try/except。

## 验证（部署后 24-48h，step_usage 账本前后对照，以部署时间戳为界）

| 指标 | 当前基线 | 目标 |
|---|---|---|
| 双烧对数（hermes researcher 超时后 10min 内同尺寸 minimax 直调） | 2 对/日（11-16） | → 0 |
| 无标签 minimax 直调次数/日 | ~20 次（11-16） | 降幅 ≥80% |
| minimax 直调单次均值 | 4.57k token | 持平或降 |

对照命令：`python3 scripts/step_usage.py --summary` + 内联 python3 -c 按上述口径聚合。

## CHANGELOG

按 v7.3.84/85 既有格式新增 v7.3.86 条目（背景账本数字 → 改动 → 测试 → 验证计划）。
