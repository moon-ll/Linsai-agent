# 变更记录

## v6.9.40 - 2026-08-23 软卡死误判导致课题轮次中途切换（job 级推进信号缺失）

背景：用户实测课题优化总在一轮未完成时被切换，轮次推进不连贯。运行时
实证两例误切：quantum-geometry r1 26/29（90% 进度）连续 2 个时段后被判
"轮次无推进"让出；berry r2 12/25 连续 3 个时段后被让出——两者 job 每时
段都在实质推进。

根因：软卡死检测（v6.8.10）的"推进"信号只有 `optimization_rounds`（整轮
完成才 +1），而一轮 25-30 job 在 critic/writer 超时上限升至 1200s 后需
2-4 个时段完成。MAX_SOFT_STUCK_SLOTS=2 下，任何一轮超过 2 个时段，第 3
时段必然因"rounds 未变"误判软卡死强制让出——与"未完成则下一时段继续
直至完成"的设计意图直接冲突（设计于一轮 1-2 时段可完成的时代，信号与
阈值随 job 变慢脱节）。

- `lifecycle/micro_scheduler.py`：
  - 新增 `_current_round_done_count()`——job 级进展信号（当前轮 done 计数）。
  - 软卡死判定细化为"rounds 变化 OR 当前轮 done 数增加"：done 增加即视
    为实质推进，继续聚焦直至轮次完成；仅 rounds 与 done 双停滞达阈值才
    让出（防单课题饿死队列的语义保留）。
  - `_round_when_focused` 记录格式 `{pid: int}` → `{pid: {"round": N,
    "done": M}}`，读取时自动迁移旧 int（done 基线缺失视为有推进以建立
    基线，最多少切一次，后续时段兜底）。
  - 让出判定 `except Exception: pass` 改为保守"继续聚焦当前课题"——旧
    实现任何 IO/解析异常都静默落入 `_move_to_queue_end` 变成误切换课题。
  - 让出日志补充 done 计数，便于区分真停滞与推进中。
- `tests/test_micro_scheduler_rotation.py` 新增测试 10（4 断言）：
  - 10a: done 24→26→28 跨 3 个时段持续聚焦（修复主场景）
  - 10b: done 连续 2 时段不变仍软卡死让出（防饿死保留）
  - 10c: 旧 int 基线迁移安全
  - 测试构造对齐真实 tick 节奏（每时段 2 次 tick，切换分支提前 return
    不追加 focus_history，靠时段内第二次 tick 补记）。
- 验证：`self_test --module` 1019/1019 全绿；轮转回归 21/21 通过
  （17 旧 + 4 新，旧用例语义不变）。
- 预期效果：一轮优化连贯推进直至完成（跨 3-4 个时段），仅在真停滞
  （连续 2 时段零 job 进展）或卡死时让出。8 个课题轮转周期变长但每轮
  完整，符合"每时段聚焦一个 proposal 直至完成完整一轮"的设计。

## v6.9.39 - 2026-08-23 注册命名守卫：课题名称段数字开头必被校验拒绝

背景：00h 健康检查第三层抽查时回溯 bc190e1（08-22 周六输入端命名失败）根因。
`register_from_idea` 从簇标题 ASCII 过滤提取 name 后，未保证命名规则要求的
"课题名称段以字母开头"（`[a-z][a-z0-9-]{1,40}`）。标题含数字编号/波长时
（实测 `322-frogcrab`）拼出的 `general-322-frogcrab-20260822` 必被
`validate_proposal_id` 拒绝——注册静默失败，且 `run_input_compose` 对单条
路由失败不阻断 job 整体 success，本周 new 配额空转需人工兜底（bc190e1
手动补注册「阿秒条纹技术」课题）。

- `proposal_lifecycle/registration.py`：`register_from_idea` name 定型前
  剥离前导数字段（`re.sub(r"^[0-9-]+", "", name)`），空则回退占位名
  `new-idea`（与 v6.9.16 中文标题回退链衔接）；覆盖 title 直取与
  keywords 回退两条路径
- `idea_generator.py`：`_generate_proposal_id` 与 `register_new_idea`
  dry_run 分支同模式加固（防未来调用方踩坑；当前 `_generate_proposal_id`
  无调用方属遗留代码）
- 测试：`test_mechanism_hardening.py` 新增 NamingGuardTests（9 断言）——
  数字开头主场景 / 中文标题 keywords 数字开头回退 / 纯数字标题占位名 /
  正常标题不受影响 / idea_generator 两处源码级守卫
- 验证：`self_test --module` 1015/1015 全绿（+9）

## v6.9.38 - 2026-08-22 周六复盘三修复：跨周重置空转 / 任务状态不回退 / KB 蒸馏积压不收敛

背景：08-22 周六全天复盘发现三项机制缺陷。输入端入口 cron 09:00 触发后
空转 3 小时（靠 6h repair 兜底救回）；key-transient 课题 job 6/25 进行中
但任务面板显示 completed（审核退回重开后状态不回退）；KB 待蒸馏积压 347
连续 46 次告警不收敛（日蒸馏 5 篇 vs 日增 40+），且告警口径（347）与蒸馏
器实际清单（229）不一致，积压治理无法对账。

- `weekend_pipeline/pipeline.py`（P1a）：`_reset_stage_for_new_week` 跨周
  判定从滚动 144h 时差（`delta_days < 6`）改为自然周锚点（最近过去的周六
  00:00 本地）。旧口径下上周完成时刻晚于本周入口 cron 时刻时（08-16 11:51
  完成 vs 08-22 09:00 入口，时差 5 天 21 小时），入口 cron 必然差不满 6 天
  而 no-op 却标记成功。新口径与 `lifecycle.orchestrator._weekend_catchup_
  decisions` 锚点一致，入口 cron 即时生效，不再依赖 repair 兜底。
- `lifecycle/micro_scheduler.py`（P1b）：任务同步补 `completed→active`
  回退分支。审核退回归零轮次重开时，映射命中的旧任务已标 completed 并移
  入 completed/ 目录，旧代码只处理 backlog→active，任务面板与实际 job
  进度永久脱节。task_manager 状态机本就允许该转换并自动搬移文件。存量
  脱节任务 key-transient r1 已手动修正回 active。
- `kb_distill.py`（P2）：新增 `--auto` 自适应批量——积压 >300 → 20 篇/天
  （追赶档），>150 → 10 篇/天（消化档），否则 5 篇/天（维持档），积压回
  落后自动降档避免常态多耗 token。cron wrapper `lc_kb_distill.sh` 由固定
  `--batch 5` 改 `--auto`（旧 wrapper 已重生成）。
- `kb_health.py`（P2）：`pending_distill` 口径统一——改调
  `kb_distill.pending_distill_list()` 同一函数（延迟导入防循环），旧实现
  未排除 `_text_cache/`、`_pdf-library.md` 等中间产物导致 347 vs 229 长期
  不一致。失败时降级回旧口径保底。
- 测试更新：`test_mechanism_hardening.py` 新增 3 套件 20 断言（自然周锚点
  修复主场景/同周末幂等/异常安全 + 回退分支源码守卫 + 自适应档位边界/
  wrapper 接线/口径统一）；`test_weekend_pipeline.py` 两用例注入固定时钟
  消除星期依赖（旧"2 天前/昨日"构造与新锚点口径冲突且周六跑必失败）；
  `test_weekend_pipeline_hardening.py` 产物日期定位用例同步改固定时钟。
- 验证：`self_test --module` 1006/1006 全绿（基线 +3 为新增断言）；
  机制加固测试 68/68 通过；`kb_distill --self-check` 通过；口径统一实测
  kb_health=229 与蒸馏器一致。

## v6.9.37 - 2026-08-22 P0 跨轮记忆被跨章节 critic 调用误标已解决（同轮入库同轮被杀）

背景：08-22 16h 健康检查第四轮设计抽查 #6（P0 跨轮持久化）静态三项
（critic/writer 注入、writer 跨章节修复授权、持久化）全部在位，但运行时
数据异常：6 个 optimizing 课题全部条目 `round_resolved ==
first_seen_round`（order-param 7/7、moire 8/8、bsv 8/8、key-transient
4/4），quantum-geometry 更出现 first_seen=8 / resolved=1 的时间倒挂。

根因：`optimize._update_open_critical_issues` 的"标记解决"分支不比较
章节——每轮含 3 个章节 critic + full_review + references 共 5 次调用共享
同一 open_critical_issues，`current_sigs` 只含本章节问题签名，其余章节
条目一律落入"本轮未复现→已解决"分支。一轮内后续章节的 critic 调用会把
先前章节刚入库的 P0 全部误标已解决，跨轮记忆实际只存活到下一个 critic
job；writer 跨章节修复与 completion 的 P0 清零检查因此系统性失真。

- `proposal_lifecycle/optimize.py`：标记解决增加
  `entry.section == section_key` 前置条件——仅当条目所属章节正是本轮
  评审章节且未复现时才标记解决；其他章节条目保持原状（不解决、不刷新
  last_seen）。同章节自然生命周期（下一轮同章节评审未复现→解决）不变。
- `tests/test_cross_round_p0_memory.py` 新增 3.5 回归（3 断言）：
  content 章节 critic 调用不得误标 rationale 章节未解决 high 条目。
- `self_test.py` mapping["module"] 补注册 `test_cross_round_p0_memory`
  （此前未注册被静默跳过，本次修复的回归保护因此缺位）。
- 数据不回滚：历史误标条目无法区分真解决/误标，维持现状；berry 现存
  12 条未解决 P0 已受修复保护（周一恢复时段后 writer 跨章节修复应激活）。
- 验证：`self_test --module` 986/986 全绿（基线 965→986，+21 为 P0
  套件补注册）。

## v6.9.36 - 2026-08-22 auto-heal 降级标志被比较路径消费修复（idea_review 前置失效）

背景：08-22 12h 健康检查第四轮设计抽查 #3（研究设想质量门槛）运行时
实证断裂：order-param 负反馈告警 08-21 10:00 auto-heal 清除时按设计设置
`idea_review_required=True`（降级退回研究设想评审，理由已落盘），但其后
创建的 round 7 job 链以 critic 开头、无 idea_review 前置，且标志已变 False。

根因：`orchestrator._compute_actual_round` 把 `_build_full_round_jobs` 当
纯"预期 vs 实际"比较函数调用，但后者在 `idea_review_required=True` 时会
顺手清除该标志（controller L285-287 副作用）。时间线：auto-heal 置标志 →
下一 tick 扫描时标志被比较调用烧掉（顺带 26 vs 25 不匹配延误一轮推进）→
再下一 tick 真正建轮时标志已为 False → 降级链在最后一环无声断裂。

- `lifecycle/orchestrator.py` `_compute_actual_round`：比较前快照
  `idea_review_required`、finally 中恢复；标志只允许被"真正建轮并落盘
  job"的调用方（sync_checkpoint）消费。签名不变，测试 monkeypatch 兼容。
- 修复后语义：降级标志在场时，已闭环轮次会回补 idea_review job（比较
  26 vs 25 不匹配），下一轮建链继续前置 idea_review——降级真正生效。
- `tests/test_auto_acceptance.py` 新增 `DemoteFlagSurvivalTests`（R2b）：
  用例 1 断言比较路径不消费标志；用例 2 断言 sync_checkpoint 回补
  idea_review job 且仅在落盘后消费标志。
- 数据修复：order-param 被烧掉的标志已恢复为 True（按已记录的降级理由
  还原设计意图，round 8 建链时前置 idea_review）。
- 验证：`self_test --module` 965/965 全绿（基线 961 → 965，+4 项断言）。

## v6.9.35 - 2026-08-22 人工审核反馈闭环第三处断裂修复（proposal_id 缺失）

背景：08-22 00h 健康检查第三轮设计抽查 #10（人工审核反馈闭环）运行时实证
断裂：bsv human_feedback_count=3、feedback-3-raw.md 存在，但
`load_review_feedback_for_optimization` 恒返回空串。根因：`_lifecycle.json`
的 prop_state 中**没有** proposal_id 键（state.py `_get_proposal_state`
原样返回 proposals[pid] dict），旧实现 `prop_state.get("proposal_id")`
恒 None → feedback_dir 拼成 `optimizing//06_feedback` 永不存在。这是该
闭环自 v6.8.17 引入以来的第三处断裂（v6.9.26 已修门闩与长度判断两处），
意味着历史人工审核意见从未注入过 critic/writer prompt，用户审核反馈
学习完全失效。

- feedback_archive.py `load_review_feedback_for_optimization` 新增显式
  `proposal_id` 参数（空串时回退 prop_state 内字段，兼容旧式调用）
- optimize.py `_load_human_feedback_block` 传入自身已有的 proposal_id
- test_optimize_v6817_prompt_vars.py 新增端到端用例：真实结构 prop_state
  （无 proposal_id 键）+ feedback 文件 → 走真实加载链路断言注入
- 验证：bsv 实数据修复后返回 114 字符反馈内容；`self_test --module`
  961/961 全量通过；py_compile 通过

## v6.9.34 - 2026-08-22 周末补跑接线测试时钟依赖修复

背景：08-22 00h 健康检查发现 `self_test --module` 959/961（v6.9.33 提交时
961/961 全绿），失败集中在 `周末任务流水线测试` 两个接线用例。根因：
`_test_weekend_stage_catchup` 的决策用例固定了时钟（08-16 周日中午），但
接线用例调用 `_weekend_stage_catchup()` 时无法注入时钟，走真实
`datetime.now()`——周六凌晨 00:00-09:30 窗口内三阶段入口 cron 窗口均未过，
`_weekend_catchup_decisions` 全部返回 False，`fake.synced` 为空导致断言
必然失败。产品行为本身正确（窗口未过本就不该补跑），纯测试时钟依赖缺陷。

- orchestrator.py `_weekend_stage_catchup` 新增可选参数 `now_local`
  （默认 None 时保持 `datetime.now()`，产品路径不变）
- test_weekend_pipeline.py 接线/dry-run 两处调用注入固定时钟
  `datetime(2026, 8, 16, 12, 0)`，与决策用例口径对齐；dry-run 用例从
  "碰巧无超期阶段"变为真正验证"有超期但不落盘"
- 验证：`self_test --module` 961/961 全量通过；py_compile 通过

## v6.9.33 - 2026-08-21 writer 后程序化复检闭环（防表面修改）

背景：v6.9.30 的 AI 天花板机制生效后，writer prompt 已注入 top_issues 明细，
但历史执行不力（moire 案例只修 1/7 问题，r2/r3 连续大额扣分）。复检用
确定性检测验证 writer 是否实质修复表达问题，与顽固升级机制形成闭环。

- **writer 后二次 AI 检测**（`executor.py` `_run_writer_step`）：writer 执行
  成功后重新运行 `_detect_ai_patterns`，比较 writer 前后天花板
- **提升判定**：未达标（天花板 <0.85）必须严格提升（`>` 前值）；已达标只
  要求不显著倒退（允许 ±0.02）；references 轮跳过（不涉及正文表达）
- **未提升即判未通过**：`expression_improved` 并入 `section_passed` 判定，
  未提升时记录原因"writer 未实质修复表达问题（AI 天花板 X→Y）"，下一轮
  继续优化，杜绝表面修改蒙混过关
- **可观测性**：score_history 新增 `ai_ceiling_after` / `expression_improved`
  / `expression_not_improved_reason`；writer 返回携带复检结果供 monitor 综合
  评估（monitor 经 section_passes 读取未通过信号）
- **回归守护**：`test_mechanism_hardening.py` ExecutorPathTests 新增 5 用例
  （复检二次检测 / 提升判定 / section_passed 条件 / ai_ceiling_after 入史 /
  references 跳过）
- **验证**：`test_mechanism_hardening.py` 48/48 通过；`self_test.py --module`
  961/961 通过；`py_compile` 通过

## v6.9.32 - 2026-08-21 references 评审超时放宽 + order-parameter 卡死解锁

背景：v6.9.30 修复生效后暴露真问题——order-parameter r7 references-critic
连续 3 次 600s 超时失败卡死（阻塞 references-writer → monitor → derived
整条 r7 收尾链）。根因：references 评审输入含 references.md + 三个正文
章节（约 106KB），而 MiniMax 慢 API 下主 critic 单章都要 1155s 才能完成，
600s cap 对 references 评审过紧。

- **references 评审超时 600s→1200s**（`optimize.py`）：`min(timeout, 600)`
  改为 `min(timeout, 1200)`，对齐主 critic 大模块超时。v6.8.37 的 600s
  假设"references 较主 critic 轻"已不成立（输入含全部正文）
- **order-parameter r7 references-critic 手动解锁**：`--reset-stuck` 强制
  重置 failed→pending（attempts 清零），依赖链恢复可推进
- **回归守护**：`test_mechanism_hardening.py` ExecutorPathTests 新增
  references 超时 cap 守护（必须 ≥1200s，禁止回退 600s）
- **验证**：`test_mechanism_hardening.py` 43/43 通过；`self_test.py --module`
  954/954 通过；`py_compile` 通过

## v6.9.31 - 2026-08-21 修复 slot_done 轮转信号"先删后读"缺陷（焦点无限持有、队列饥饿）

背景：20h 健康检查发现 4/6 课题无进展 2-4 天（bsv 87.7h、berry 46.9h、
quantum-geometry 40.5h、key-transient 39.4h），近 3 天全部时段被 moire 与
order-param 垄断；bsv 的 scheme-critic 已被修复链路重置为可执行却始终轮不到
调度，且 48h 停滞告警从未触发。定位到两个已确认缺陷 + 一项防线加固：

- **slot_done 先删后读（主因）**：`_focus_proposal_for_slot` 时段切换时先
  `state.pop(slot_{i}_done)` 再在下方对同一内存 dict `state.get()` 该键，
  "轮次中途完成→下一时段轮转"信号（v6.8.20 设计）永远读不到。聚焦课题每
  推进一轮即重置软卡死计数，可无限持有焦点（生产实证：order-param r6 于
  slot 2 中途完成后 slot 3 仍持有）。修复：pop 前捕获 flag，消费点读捕获值
- **停滞检测时钟盲区**：monitor 停滞时钟读 proposal 级 `updated_at`，会被
  repair 重置 / cron 失败记录 / stale 清理等非执行写入刷新（bsv 实证：
  updated_at 距 26.1h、job 实际停滞 87.7h，告警永不触发）。修复：时钟改取
  任一 job 的 `finished_at/started_at` 最大值，无 job 时间戳回退 updated_at
- **focus_history 去重（加固）**：旧实现每 5 分钟 tick 追加一条，50 条上限
  仅覆盖约一个时段，`_count_consecutive_slots` 在时段切换时几乎恒为 1，
  `MAX_SOFT_STUCK_SLOTS=2` 软卡死防线对满时段失效。改为同一 (slot,
  proposal) 只记一条，计数语义不变
- **测试**：`test_micro_scheduler_rotation.py` 新增测试 8（slot_done 轮转
  守护）+ 测试 9（历史去重守护），套件 10→16 断言；新增
  `test_stalled_clock_job_activity.py`（4 用例，含 bsv 场景复刻）并注册进
  `self_test.py --module` 硬编码清单
- **验证**：两套件独立运行全绿；`self_test.py --module` 954/954 通过
  （基线 944 + 新增 10）；`py_compile` 通过；修复前缺陷均已在隔离环境
  动态复现确认

## v6.9.30 - 2026-08-21 锚点绑定/AI 检测机制移植到线上执行路径（executor.py）
背景：v6.9.28 的机制修复只落在 `optimize.py`（微调度器未调用的死代码），
线上实际执行路径 `lifecycle/executor.py` 缺失，导致"template=score anchor"
机制整体失效。本次将核心机制移植到 executor.py 的 `_run_critic_step` /
`_run_writer_step`，并新增源码级回归守护。

- **程序化 AI 写作模式检测**：critic 步骤之前运行 `_detect_ai_patterns`，
  产出表达质量天花板；结果传入 critic（`ai_check_result`）与 writer
  （writer 必须修复检测到的 AI 模式问题）
- **程序化天花板强制执行**：表达质量分 > AI 天花板时强制 cap；综合分按
  AI 天花板分级 cap（<0.7→0.75 / <0.8→0.80 / <0.9→0.85），与 optimize.py
  对齐
- **references 评审专用计分**：N/A 维度不纳入加权，且先于锚点绑定执行
  （防覆盖回归）；references 轮跳过锚点绑定（口径不适用）
- **锚点结论绑定**：`_extract_anchor_conclusion` + `_apply_anchor_conclusion_binding`
  三档结论强制绑定评分档位，范本锚点成为分数锚
- **评审报告完整性验证**：缺少"锚点对比"/"写作风格评估"段落时置
  `report_invalid_reason`，section 判定为未通过
- **score_history 新字段**：`ai_ceiling` / `ai_top_issues` / `anchor_conclusion`
  随轮次入史，prompt_optimizer 可聚合全局 top_issues 生成针对性修复指令
- **回归守护**：`test_mechanism_hardening.py` 新增 `ExecutorPathTests`
  （14 用例）做源码级守卫，防止机制再次只修死代码
- **验证**：`test_mechanism_hardening.py` 41/41 通过；`self_test.py --module`
  944/944 通过；`py_compile` 通过

## v6.9.29 - 2026-08-20 项目文档瘦身（归档 4 份过期/冗余文档 + 权威文档补全）

背景：用户要求对项目结构说明/规则等相关文档瘦身，清理明显过期或冗余内容，避免文档堆积。

- **归档 4 份过期/冗余文档**（移入 `docs/archive/`，保留历史）：
  - `FRAMEWORK-ARCHITECTURE.md`（650 行）：v6.8.9 快照，与 `ARCHITECTURE.md` 大量重复，达标线/测试基线/目录结构全部过期
  - `SCORING-STANDARDS.md`（191 行）：达标线写 0.90 统一，与当前 0.85/0.90/0.95（v6.9.27 上调）矛盾，权威源为 `nsfc-standards.json`
  - `FEATURE-PLAN.md`：P1 研究设想质量门槛已完成（v6.8.26），无待办内容
  - `linsai-orchestrator-design.md`：v6.7 总控设计稿，已实现
- **`PROJECT-STRUCTURE.md` 瘦身重写**（280→99 行）：只保留顶层结构 + 数据域 + 关键目录，脚本细节指向 `scripts/README.md`（已维护逐脚本清单），修正版本号与 docs/ 目录错误
- **`DATA-FLOW-MAP.md` 清理**：移除会腐烂的硬编码数据量（PDF/简报/论文/课题数），只维护结构流向，更新验证日期
- **`ARCHITECTURE.md` 补全**：达标线（0.85/0.90/0.95）、逃生阀、agent 奖惩门槛等评分规则并入质量标准一节，避免归档 SCORING-STANDARDS 后规则丢失
- **索引同步**：`docs/README.md` 与根 `README.md` 更新文件清单，移除对已归档文档的引用
- **验证**：全库 grep 无对已归档文档的代码/前端残留引用（仅 docs/README 归档说明与历史日志）

## v6.9.28 - 2026-08-20 对抗自优化机制完整修复（锚点绑定顺序 bug + 顽固升级 + 语义去重）

背景：用户要求完整修复 writer/critic 自优化与对抗机制（申请书质量的核心支撑），
并核查范本是否按设计起正向引导作用。全链路体检发现四个机制断点/缺陷。

- **① 锚点绑定顺序 bug（optimize.py）**：v6.9.25 引入的"范本锚点结论
  强制绑定评分档位"被排在前者赋值的 references 专用计分之前——references
  轮的绑定结果被覆盖、形同虚设。修复：绑定段移至 references 专用计分
  之后，且 references 轮跳过绑定（其口径为文献元数据准确性，写作语体
  锚点不适用，"差距明显"不应 cap 元数据评审分）。源码级顺序守卫防回归。
- **② 锚点结论可观测性**：三档结论（差距明显/基本接近/达标）记入
  lifecycle 状态（`anchor_conclusion` 字段），范本引导效果从"黑盒分数"
  变为可追踪信号——续轮可见结论是否随优化收敛至"达标"。
- **③ writer 顽固升级机制（optimize.py）**：实测 writer 连续两轮负分
  （-16.9/-8.5）却仅做表面修改（diff 5 行、P0 不修），奖惩扣分不足以
  改变行为。新增 `_build_writer_escalation_block`：连续两轮负分且
  critic 评价含表面修改特征时，writer prompt 注入"顽固升级"块——
  强制对问题清单逐条响应（改了什么/为什么这样改），禁止沉默式微调。
- **④ prompt_optimizer 语义去重**：v6.9.25 将历史 auto-opt 规则手工
  合并进 SOUL 正文后，fingerprint 窗口（7 天）过期，同义建议以不同
  措辞再生成、被重复追加。新增 `_semantic_overlap_ratio` 双口径取 max：
  特征词覆盖率（CJK ≥3 字/ASCII ≥2 字词元命中比，≥6 字长词按内部
  3-gram ≥40% 判部分命中）+ 字符 4-gram 包含度；≥0.6 判"正文已覆盖"
  跳过写入（不备份、记 `apply_note=semantically_present:N%`）。
  两个泛化缺陷在回归中修正：整句 token 无法子串命中同义改写（改双
  口径）、2 字泛用词（内容/需要）造成短建议误拦截（改词元长度门槛）。
- **配套运维**：writer SOUL 残留 auto-opt 段回收（标记清零）；`memory/
  prompt-interventions.json` 旧干预记录标记 `superseded_merged`；
  `nsfc-standards.json` benchmark_anchors 增加主从声明（该文件为唯一
  真相源，防双处维护漂移）。
- **范本核查结论**：设计意图（锚点=分数锚、结论=档位 cap）在①修复前
  仅部分生效（references 轮失效），②使引导路径全链路可见；修复后范本
  对比从"格式门槛"实际升格为"分数锚"。
- **回归**：新增 `scripts/tests/test_mechanism_hardening.py`（27 用例：
  锚点顺序 7 / 顽固升级 12 / 语义去重 8），注册入 `--module` 硬编码清单；
  `--module` 930/930 全绿（含 test_prompt_optimizer 35/35 备份上限用例
  兼容验证）。

## v6.9.27 - 2026-08-20 质量达标线整体上调（面上 0.85 / 重点 0.90 / 重大 0.95）

背景：用户要求提高质量标准，将三类项目达标线按比例上调一档，收敛逃生阀同步上移，
防止低分课题绕过新标准。

- **nsfc-standards.json**：面上项目 `min_overall_score` 0.80→0.85、重点项目 0.85→0.90、
  重大项目 0.90→0.95（该文件为全局标准唯一真相源，monitor/critic/writer prompt 动态读取自动生效）
- **completion.py**：质量收敛逃生阀 `CONVERGENCE_SCORE` 0.80→0.85（连续 3 轮 ≥0.85 且提升 <2% 才自动晋级待审）
- **executor.py / rebuild_lifecycle.py**：未知项目类型 fallback 达标线 0.80→0.85 保持一致
- **test_quality_ceiling_convergence.py**：收敛回归测试数据同步上移（4×0.86 平台收敛、骤降防误晋级、0.84 跌破、连续下降分支）
- **验证**：`--module` 903/903 通过（含收敛 7/7、审核反馈闭环 8/8、AI 检测数据源 19/19）

## v6.9.26 - 2026-08-18 审核反馈闭环复活（双断点修复）+ 三课题带反馈退回

背景：v6.9.25 落地后执行三课题（moire/key-transient/quantum-geometry）
审核退回，验证注入时发现"审核反馈闭环"（v6.8.17 引入）从未生效——
`load_review_feedback_for_optimization` 存在两个叠加断点，所有路径
（Web 与 CLI）恒返回空串，人工审核意见从未进入 critic/writer prompt。

- **断点 1（门闩错误）**：函数以 `review_history` 为门闩提前返回，但该
  字段仅在带 `session_id` 的 Web 审核提交时写入——CLI/脚本提交不写，
  反馈永远不注入。函数体实际只依赖 `human_feedback_count` 与 raw 文件，
  门闩改为 `feedback_count`。
- **断点 2（长度判断永假）**：旧判断 `len(lines) > 2` 恒为 False
  （lines 最多含 header + 1 个反馈共 2 个元素），即使 Web 路径过门闩
  也返回空串。改为 `len(lines) > 1`。
- **附带修复**：`_structure_feedback` 派 writer 的 timeout=120s 必超时
  （writer 实测平均 350s+），结构化 JSON 永远写不出、每次反馈提交白派
  一次 writer。timeout 提至 480s。
- **验证**：三个退回课题注入块 725-782 字符，反馈正文（新语言规范红
  线/参考文献修复要求/P0 清单）实际进入 prompt。
- **回归**：新增 `scripts/tests/test_feedback_injection.py`（8 用例：
  无 review_history 注入/空态/文件缺失/摘要提取路径/超时参数），注册
  入 `--module` 硬编码清单。
- **运维执行**：prompt_optimizer auto 即时跑（应用 1 条 writer 禁占位
  符遗留建议）；三课题 major_revision 退回（moire 携 5 高危 P0+语言
  红线要求、key-transient 携参考文献 0.81→0.53 崩落修复要求、
  quantum-geometry 携一致性 0.77+参考文献 0.70 补短板要求），退回后
  rounds=0/jobs=0 干净链（v6.9.24 归档清理生效）。

## v6.9.25 - 2026-08-18 破解 0.9 分数学死锁（AI 检测闭环 + 锚点档位绑定 + 语言红线）

背景：review_dossier 预审发现三个 pending_review 课题均不可采纳，且
存在数学死锁——AI 写作模式检测在 `ai_ceiling < 0.7` 时把综合分 cap 至
0.75，叠加 writer prompt 残留"总字数≥4000"低标准污染（人为拉长句、堆
积修饰词，直接触发 AI 模式扣分），0.9+ 分在机制上不可达。本轮按
A→D 四方案打通闭环。

- **A：writer SOUL 字数污染清除**（`apply_prompt_upgrades.py` 已执行）：
  移除"总字数≥4000字/每章节≥1200字"低标准段，替换为范本实测篇幅口径
  （面上正文约 2.9 万字符：立项依据 5000-8000 字、研究内容 3000-5000
  字、研究方案 5000-8000 字）；`failure_analyzer.py` 的
  low-content-after-rewrite 模式 suggested_prompt_change 同步改为
  篇幅对标口径，杜绝"总字数≥4000"经失败分析再注入 prompt。
- **B：AI 检测扣分项接入 prompt_optimizer 数据源**
  （`prompt_optimizer.py`）：新增 `AI_PATTERN_RULES`（9 类 AI 写作
  模式→定向修复指令）与 `_collect_ai_pattern_hints`（从 lifecycle
  score_history 的 `ai_top_issues` 聚合，证据 ≥2 才生成建议，按证据数
  排序取 top），接入 `_generate_suggestions`——此前优化器对程序化检测
  的重扣分项（超长句/自引用/冗余修饰）完全盲视，只盯次要问题。
- **C：critic 锚点对比结论与 rubric 档位强制绑定**
  （`proposal_lifecycle/optimize.py`）：critic prompt 强制要求输出
  "锚点对比结论：达标/基本接近/差距明显"行；新增
  `_extract_anchor_conclusion`（程序解析，无结论行不做绑定）与
  `_apply_anchor_conclusion_binding`——差距明显→表达质量 cap 0.69、
  综合 cap 0.84；基本接近→0.79/0.89；达标不设限。锚点对比从格式
  要求变为分数锚，"与范本差距明显却给 0.85+"被机制阻断。
- **D：writer SOUL 增补语言规范三条红线**（程序化检测口径）：① 句长
  红线（单句≤120 字，80-120 字技术长句每段≤2 句，拆分后以动词开头）；
  ② 自引用红线（正文禁"详§X"替代论证，>10 处扣分、>15 处固定扣
  0.10）；③ 修饰词红线（10 个空泛修饰词全文合计≤12 次）；关联项
  （列表替代论述/关联词/句首"本项目拟"/元话语/加粗密度）一并自检。
- **回归**：新增 `scripts/tests/test_ai_pattern_anchor_binding.py`
  （32 用例：B 数据源聚合 19 + C 锚点解析与档位绑定 13），注册入
  `self_test --module` 硬编码清单（v6.9.24 教训：不注册会被静默跳过）。
  `--module` 895/895 全绿。

## v6.9.24 - 2026-08-18 审核退回清理旧轮次残留 job（防跳轮/防提前触顶）

- **缺陷**（08-18 04h 健康检查发现）：pending_review → optimizing 审核
  退回仅归零 `optimization_rounds`，不清理 `pipeline_jobs`——退回前生命周
  期的 done/pending job 全部残留（bsv 实证：r7 done×29 + r8 done×23 +
  derived pending×2）。后果链：`_compute_actual_round` 整轮全 done 向上扫
  描会消耗旧 done 轮次跳轮（新 r6 完成后一次性跳至 r8=DEFAULT_MAX_ROUNDS，
  真实 r7/r8 两轮被吞）；`sync_checkpoint` 按 job_id 去重导致新 r7/r8 链
  永不创建；r8-derived 残留在轮末空窗被误调度。标准人工审核退回流程即触
  发，直接影响申请书优化轮次预算。
- **修复**（`proposal_lifecycle/transitions.py`）：审核退回分支归零轮次时
  将 `pipeline_jobs` 全量经 `append_archive_jobs` 归档后清空（兼容 legacy
  dict 形态；归档失败降级 warning 不阻断）。
- **存量数据修复**：bsv 54 个 r7/r8 残留 job 归档至 `_lifecycle_archive.json`，
  保留 r1 活跃链 26 个（修复前备份；r8-derived attempts=0 确认无误调度产物）。
- **回归**：新增 `scripts/tests/test_transition_reset_jobs.py`（14 用例：
  退回清空+归档/退回后不跳轮/普通流转不清 job/dict 兼容），注册入
  `self_test --module` 清单——`--module` 为硬编码清单非自动发现，新套件
  不注册会被静默跳过（本轮实证）。--module 863/863、--scenario 16/16、
  --persona 38/38 全绿。
- 仅报告项（待人工裁决）：`test_idea_review` 无 `run_tests` 在 --module
  静默跳过（35 用例未计入基线）；AGENTS"自动发现"表述与 --module 实现偏差。

## v6.9.22 - 2026-08-17 课题方向纠偏 + 周末输入核心主题对齐门

背景（用户指示）：08-16 注册的 berry-mnps3 课题跑偏——纯准静态凝聚
态理论（第一性原理 + 滑移工程器件化），无强场/超快维度。课题组核
心范式应为：**强场操控**（强场/THz 光场驱动物性切换）或 **HHG/超快
光谱测量**（高次谐波谱学/泵浦-探测超快读出），两者居其一。

- **课题方向修正**（`research_proposals/drafts/general-berry-mnps3-rashba-20260816/`）：
  direction-calibration 追加"人工方向修正"章节，保留原知识簇资产
  （耦合准交变磁性/滑移工程/MnPS3|WS2 三元耦合），重定向为双范式
  四问（强场驱动滑移动力学、Floquet 增强弱交变磁、交变磁自旋劈裂
  HHG 螺旋度指纹、Rashba-Berry-交变磁时域分离）；proposal-brief 核
  心问题/创新点同步；lifecycle state 记录 direction_correction 事件。
  知识库弹药：2408.08955/2408.16926（交变磁体 HHG）、2410.08910
  （强场 Floquet 谷操控）。
- **核心范式强制关**（`sources.py` + `input_jobs.py`）：新增
  `CORE_THEME_TERMS`（49 词，按"强场操控/超快测量"两范式分层）与
  `core_theme_hit()`；`_new_gates` 方向关升级为六重门槛——开新课题
  必须命中核心范式词，仅命中材料/物态语境词（自旋/能谷/激子/交变
  磁）不够格，只能 merge/expansion 注入或 defer 积累。
- **LLM 仲裁 prompt 注入核心主题约束**：纯静态凝聚态簇不得判 new。
- **移除同义反复漂移引擎**（`load_scope_terms`）：不再从活跃课题标
  题自动补词（课题词进词表→新簇命中→注册课题→标题再扩词表的不可
  逆漂移），方向扩张仅经人工编辑词表或升级种子词。
- **回归测试**：`_test_new_gate_requires_core_theme`（静态簇拒 new/
  嫁接强场维度放行/core_theme_hit 正反例/词表不吸课题标题词）；
  self_test --module 849/849 全绿。
- 教训记录：同一文件多处修改禁止并行编辑（本轮两处 SearchReplace
  并行导致第一处被覆盖，测试抓出后补回）。

## v6.9.21 - 2026-08-17 gateway 挂死排查收尾：看板空档期刷新 + bak 清理

背景：08-16 07:36 → 08-17 13:13 linsai 网关挂死 29.6h 后自愈（根因
仍定位在启动导入链 open() 阻塞，hermes-agent 侧问题，降级观察明晨
07:37 daily-reload 复发）。排查中发现两个 CoPilot 侧可修复缺陷。

- **看板 current 冻结**（`micro_scheduler.py`）：空档期（非聚焦时段）
  直接 return，不刷新看板 `current` 字段；挂死期间该字段冻结在
  08-14 22:30 的 `in_slot=true / slot=18:30-22:30`，恢复后空档期
  也不刷新，看板/控制台误读为"时段内"。修复：空档期跳过路径同样
  合并写看板，置 `in_slot=false/slot=null` 并刷新时间戳。实测
  16:56 微调度器空档执行后 current 正确归零。
- **.bak 误入版本库**（`.gitignore`）：16h 健康检查发现
  `categories.json.bak.*`、`wiki/papers/.backup/*.bak` 随批次提交。
  新增 `knowledge/**/*.bak(.*)`、`.backup/` 忽略规则，并从索引移除
  已跟踪的备份文件（本地保留）。
- **验证**：self_test --module 840/840 全绿。

## v6.9.20 - 2026-08-16 蒸馏残留清零行动：索引文件排除 + 惯犯批次消化

背景：08-15 批量蒸馏消化 348 篇存量后剩 78 篇"惯犯"。08-16 排查
发现两个事实：① 惯犯全部是小文件（≤5KB），此前失败根因是 MiniMax
429 限额期而非内容超长——切 GLM 后试批 5/5 全成；② 其中混入
`raw/pdfs/_pdf-library.md`（自动生成的 PDF 汇总表），蒸馏无意义且
永久占用 pending 计数。

- **排除规则**（`kb_distill.py`）：新增 `EXCLUDE_FILES` 精确排除
  索引/清单类文件（首批收录 `_pdf-library.md`），`_is_excluded`
  先查精确清单再查前缀；自检新增排除规则断言。
- **存量消化**：`--batch 80` 一次性蒸馏剩余 77 篇论文（GLM 主链，
  单篇约 60s），惯犯批次试跑 5/5 成功验证链路可用。
- **周维护同步执行**：kb_merger 合并 1 对重复页（deepxiv 分析页 →
  wiki/papers 主页，本周额度 4+1 用满，余 8 组下周日续）；
  kb_maintenance 周维护报告健康（图谱 579 节点/2132 边/0 孤儿）。
- **验证**：`kb_distill.py --self-check` 6 项断言全过。

## v6.9.19 - 2026-08-16 周末阶段超期补跑：入口 cron 错过不再整周空缺

背景：周末三阶段的跨周重置只发生在入口 cron 的 sync_stage_jobs 里
（input 周六 09:00 / output 周六 14:00 / reflection 周日 09:00）——
08-16 实测反思入口 cron 撞上系统卡死窗口失败后，20 分钟 worker 只
推进 pending job 不触发重置，本周反思整段空缺且无人补位（需人工
手动补跑才恢复）；v6.9.6 的 KB 深度维护 job 也因反思阶段从未 sync
而长期未注册进 state。

- **补跑逻辑**（`lifecycle/orchestrator.py`）：`lc-repair`（每 6 小时）
  周末分支新增 `_weekend_stage_catchup`——入口窗口（本地时间，对齐
  controller 安装的时刻 +30 分钟宽限）已过且该阶段本周末（最近周六
  00:00 起）零活动（无任何 job 的 started/finished 落入窗口）时，
  补调 `sync_stage_jobs`（触发跨周重置 + 补建缺失 job 模板），执行
  交给 20 分钟 worker 自然推进；repair 自身不跑 LLM 不长阻塞。
- **决策与执行分离**：`_weekend_catchup_decisions` 纯函数（state +
  now → {stage: 超期}）便于回归测试与时区锚点验证（UTC 时间戳 vs
  本地窗口经 astimezone 对齐，周六 09:30 CST 活动正确判定为"本周末
  已跑"）。
- **验证**：test_weekend_pipeline 新增 7 断言（周日中午全零活动 →
  三阶段全超期 / 周六中午仅 input / 本周末已跑不重复触发 / 接线
  sync 实际调用 / dry-run 零落盘）；真实 state 复核无误报（本周末
  三阶段均已有活动 → 全 False）；`--module` 全量 **840/840** 全绿。

## v6.9.18 - 2026-08-16 输入链路重构：信息整合 → 课题融合/新增全链治理

08-16 凌晨知识簇链路全链首跑的实测暴露四层缺陷：乱聚类（簇 ID
碰撞最多 10 簇同名、中文标题分词失效、两篇凑数簇占 143 簇绝大
多数）、路由泛滥（141 簇 → 72 new，54 个弱簇课题注册 drafts）、
落地断裂（expansion 跨周挂载成功率 12/58，BSV 课题被 6 个变体簇
重复注入）、源头杂音（运维简报聚成 8 成员簇、跨领域论文成簇）。
本次按"源头过滤 → 聚类修复 → 路由门槛 → 落地归并"四层重构：

- **源头治理（sources.py）**：① 方向词表 `scope-terms.json`
  （约 70 个中英种子词 + 活跃课题标题词，首跑自动生成、可手工
  编辑、文件优先）过滤跨领域论文——08-16 真实数据回放标定：连
  字符归一（high-harmonic ≡ high harmonic）+ 英文单词左词界允许
  后缀延展（altermagnet 命中 altermagnetism），最终仅滤 3 篇
  真跨领域（6G 波束成形等），453 篇领域内全保留；② 运维简报
  识别（<300 字 / 命中"空记录/cron 运维"且无论文条目）跳过，
  实测滤 19 条。
- **聚类修复（clusters.py）**：① 簇 ID 改 uuid4 + 注册表查重
  （旧 id(object()) seed 因 CPython id 复用高频碰撞）；② 分词
  改中文 2-gram 滑窗（旧 {2,8} 贪婪切分对无空格中文恒近 0，与
  kb_text 索引同口径）；③ MIN_CLUSTER_MEMBERS 2→3；④ 簇标题
  改团内共享关键词拼接（旧用种子论文标题）；⑤ member_summaries/
  orphans 补存 path 供跨周挂载。真实簇数据回放：143 簇全部满足
  阈值可达性，现有 0.22/0.30 阈值无需调整。
- **路由门槛（input_jobs.py）**：new 动作四重门槛——成员 ≥3、
  知识卡为 LLM 提炼（distill 新增 distilled_by 标记）、方向词表
  有交集、与现有课题相似度 <0.50（对齐 idea_generator hold 线）
  ——+ 周配额 2（成员数降序先到先得）；不达标路由 defer（簇保持
  open 继续积累，不丢失）。
- **落地修复（input_jobs.py + registration.py）**：① 信息源挂载
  改用簇内 member_summaries（跨周可用），修复旧实现依赖当天
  summaries 索引导致跨周成员必失败；② 同目标课题的 merge 簇
  连通分组（按目标分组 + 簇间相似度），组内主簇注入知识卡、
  其余只挂信息源；③ 注入标题带簇 ID 且带标记标题不参与句级去重
  （根治多簇注入标题裸奔），无标记标题仍走去重保持同 idea 幂等；
  ④ register_from_idea 注册前先算课题对比、注册后生成立项决策包
  00_idea-dossier.md——新课题自动进 human_queue activate 待人工
  队列（控制台已有渲染与 72h 催办，零前端改动），drafts→optimizing
  激活保留为法定人工节点。
- **数据修复（fix_input_chain_data.py，一次性）**：54 个垃圾
  drafts 课题归档至 backups/input-chain-fix-20260816/ + 清
  _lifecycle.json 状态；KB 垃圾镜像 108 页（reports/versions）
  归档 + proposals-index/MOC 重建；簇注册表重置（乱聚 open/closed
  簇 267 条成员摘要退回 orphan 池保留 LLM 成本，linked 簇 35 个
  保留防重复注入与查重屏障）。processed_sources 772 条原样保留。
- **验证**：test_input_clustering 扩至 94 断言（新增簇 ID 唯一性/
  中文 2-gram/scope 与运维过滤/new 配额/distilled_by/跨周挂载/
  归并分组/标题标记/dossier 九组），test_input_pipeline_repair
  夹具适配新过滤；`--module` 全量 **829/829** 全绿；真实数据
  dry-run 零落盘；修复后真实 input 链路全链重跑验证通过。

## v6.9.17 - 2026-08-16 体检修复：补提交 v6.9.16 遗漏的命名修复

08h 三层诊断发现 v6.9.16 存在提交完整性缺陷：commit 29d33c9 收录了
引用"修复后"行为的两条命名回归（test_input_clustering），但修复本体
（naming.py 的 LIFECYCLE_STAGES 导入 + registration.py 的中文标题
keywords 英文词回退）滞留工作区未入库。HEAD 上该套件一崩一败：

- `_test_register_generates_valid_id`：HEAD naming.py 引用未导入的
  LIFECYCLE_STAGES → NameError，被 self_test ⚠ 静默吞（恰为 v6.9.16
  刚收口的静默吞模式，发布说明"796/796 全绿"仅对工作区成立）
- `_test_register_cn_title_falls_back_to_keywords`：无回退逻辑 →
  占位名 "new-idea-N" 硬断言失败

本补提交将两个修复文件入库，git 快照与工作区恢复一致，796/796 复验
通过。触发链回溯：08-16 01:49 周日输入运行注册 54 个新课题（46 个
纯中文标题落占位名）→ 04h 会话修复命名 → 04:17 提交测试但漏提修复。

## v6.9.16 - 2026-08-16 体检修复：收敛窗口约束当前轮 + 测试门禁静默吞恢复

04h 三层诊断（运行时健康 / 代码缺陷 / 设计一致性抽查 #7 #10）产出
两项修复，`--module` 门禁 721→796 全绿：

- **质量天花板收敛窗口缺陷（#7 复核发现，P1）**：
  `completion._check_done` 收敛分支 `recent_scores[:-1]` 只约束窗口前
  3 轮 ≥0.80，"3 轮高位平台后当前轮骤降"（含伪分数污染，如历史实测
  0.81→0.18）会被误判为质量收敛而自动晋级 pending_review，掩盖质量
  回退。运行时近触发实证：quantum-geometry 尾部 [0.84,0.86,0.85,0.77]
  仅因浮点 0.86-0.84=0.02000…不满足 <0.02 而幸免；key-transient 尾部
  4×0.81 已满足条件、待 r4 critic 终态 job 解锁后轮末即触发。修复为
  窗口内全部轮次（含当前轮）≥0.80，骤降序列正确落入下降分支（暂停）
  或继续优化。
- **新增 test_quality_ceiling_convergence（7 用例）**：稳定收敛晋级 /
  骤降防误晋级 / 小幅跌破不触发 / 连续 3 轮下降走暂停分支，登记入
  `self_test._run_selected` module 精选清单（--module 不走 glob 发现，
  新套件不登记则不进日常门禁）。
- **测试门禁静默吞恢复（68 条断言归位）**：`--module` 运行期异常仅打
  ⚠ 不计数，两个套件自落地起从未真正运行且被"全绿"掩盖——
  test_kb_distill_created_ts（v6.9.15 prefer 透传回归，stub 路径
  /tmp/fake/raw/x.md 不在隔离 KNOWLEDGE_DIR 下 relative_to 必然
  ValueError，+7）与 test_input_clustering（08-15 enrich 用例，夹具
  只建 01_direction 而 enrich_from_idea 还写 02_topic/03_question/
  04_proposal，open("a") FileNotFoundError，+61）。修 stub 路径与
  夹具目录后 796/796 全绿、零 ⚠。全量发现模式（--web-ci）仍有
  ghost_write_guard 等静默吞，维持测试基建改进项不扩科。

## v6.9.15 - 2026-08-15 知识库积压批量处理：蒸馏主模型切 GLM

用户指令"把知识库累积的内容都处理一下"——盘点存量：输入链未摘要
文献 508 篇 + raw→wiki 待蒸馏 348 篇。输入链批处理直调 handler
（绕过 job 状态机，job 全 done 无冲突），蒸馏因链路瓶颈先行改造：

- **蒸馏主模型切 GLM（P0，实测数据驱动）**：kb_distill 默认走
  MiniMax 主链，429 限额期单篇需重试+降级（实测最长 369s），
  348 篇按此链路约 26 小时不可行。`TASK_PROVIDER_PREFS` 注册
  `kb_distill` 标签（glm/glm-fallback 队首），`distill_one` 传
  `prefer="kb_distill"`。实测 GLM 直连 ~65s/篇（成功篇 71s），
  提速 4 倍，且与 governance/weekend_input 同模式无新增失败面。
- **测试**：test_kb_distill_created_ts.py 新增 prefer 透传回归
  （stub llm_gateway 捕获参数），721/721 全绿。
- **批处理驱动**（临时脚本，不入仓）：输入链循环 summarize+
  cluster_assign 每批 30 篇至清零 → 全量簇蒸馏（跳过已有知识卡，
  一次性追平语义不受周限 8 束缚）→ topic_match+compose 路由落地；
  蒸馏 watcher 等输入链结束后全量跑（串行避免双进程抢 GLM 配额）。

## v6.9.14 - 2026-08-15 输入链端到端实测收尾：GLM 主模型 + 知识簇聚类校准

手动完整跑通输入链（collect→summarize→cluster_assign→cluster_distill
→topic_match→compose 6 job），实测暴露并修复两处设计/实现问题，726/726
全绿（周末时段工作日分支用例自动跳过，总数较工作日少）：

- **GLM 主模型路由（用户指令）**：`llm_router.TASK_PROVIDER_PREFS` 新增
  `weekend_input` 标签（glm, glm-fallback 队首），`input_jobs._llm_json`
  默认 `prefer="weekend_input"`——summarize/cluster_distill/topic_match
  三个 LLM 调用点统一走 glm-5.3。实测：30 篇摘要全量 `主模型=glm`
  直连（单篇 10-25s），对比旧链 minimax 429→claude 超时→glm 兜底
  单篇 130s+，全程零降级噪音。
- **聚类相似度校准（P0，实测数据驱动）**：首轮 30/30 摘要全部挂
  orphans、零簇形成——5 词论文特定关键词的集合太稀疏（435 对最高
  Jaccard 0.161 < 成簇阈值 0.30），簇永远聚不成、输入链空转。三处
  修复：① 摘要 prompt 关键词 5 个 → 10-15 个且强制含 2-4 个领域级
  标签（固态高次谐波/强场物理/阿秒动力学等，制造共享词表）②
  `clusters.py` 关键词分量 Jaccard → overlap 系数（|∩|/min，短集合
  语义"核心词是否落入簇核心"），标题分量保持 Jaccard ③ 关键词
  归一化 `norm_keyword`（"高次谐波产生 (HHG)" ≡ "高次谐波产生"，
  实测 4/181 关键词带括注后缀），摄取（`_coerce_summary_data`）与
  合并（`_merge_keywords`）双侧生效。实测重跑：30 篇 → 2 个真实
  主题簇（偶次谐波×Weyl 节点对称性破缺 / HHG 全量子描述，2+5
  成员）→ 2 条路由（expansion 补充信息源挂载 + merge 课题内容
  句级去重注入）→ 双簇 linked，剩余 40 orphans 留待跨周积累。
- **registration.py 缺 `import re`（P1）**：compose 的 merge 路由在
  `_sentence_similarity` 处 NameError 中断；既有测试目标课题文件为
  空、早退于去重路径之前未覆盖。补导入 + 新增带已有内容课题的
  enrich 回归（重复注入去重为一次）。
- **测试**：test_input_clustering.py 新增 4 用例（关键词归一化/稀疏
  overlap 成簇/enrich 崩溃回归/GLM 路由透传——后者随 v6.9.13 GLM
  改动并入本版提交），套件 55/55。

## v6.9.13 - 2026-08-15 体检修复：输入端知识簇链路四处阻断点 + 熔断口径

20h 例行体检发现 v6.9.12 知识簇链路重构后四处阻断（其中两处
直接导致整链断流），全部定向修复并补测试，770/770 全绿：

- **compose 永久死锁（P0）**：旧 state 里
  `input_compose_ideas.depends_on=["input_deep_read"]` 指向
  v6.9.12 已废弃 job，而 `sync_stage_jobs` 只刷新 artifact 不刷新
  depends_on，`dependencies_satisfied` 要求依赖在 done 集合 →
  compose 永久不可调度、input 阶段永无终态。修复：sync 时
  depends_on 随模板刷新（diff 落 INFO）；生产 state 已随本次
  sync 落盘自愈。`dependencies_satisfied` 保持严格语义（缺失依赖
  不放行），防"代码已更新、state 未 sync"窗口期空路由落地。
- **summarize 30/30 malformed（P1）**：system prompt 要求"JSON
  数组"与 user 模板（对象）自相矛盾，LLM 全返回数组形状；旧代码
  只回填 dict 形状 → 条目无 source_id/path/tier，
  cluster_assign 取 `.get()` 崩溃且来源已标 processed 失去重跑
  资格。修复：`_coerce_summary_data()` 归一化（数组取首 dict、
  回填溯源、不可收敛计 failed_llm 不标 processed）+ prompt 统一
  "JSON 对象" + 离线数据修复 30/30（按归一化标题回连，含备份
  `*.bak-malformed-2026-08-15`）。
- **熔断幻影键（P1）**：monitor 输入端熔断读
  `data.get("ideas", [])`，但 compose 新旧版本从未写过 "ideas"
  键（真实 schema `{"generated_at","actions":[...]}`），测试夹具
  与实现共享幻影契约 → 告警恒触发永不解除。修复：actions 主口径
  （ideas 仅历史兼容），夹具改真实 schema。
- **sync 并发覆盖（P2）**：sync 加载快照后等锁期间 worker 完成
  job，获锁写 stale 快照冲掉 done 状态（08-15 实测 summarize
  重跑一次）。修复：`sync_stage_jobs` 全程持
  `file_lock("weekend-pipeline")` + 锁内重载 state；内部子保存改
  `_save_unlocked()`（file_lock 每次开新 fd，同进程嵌套自死锁）。
- **测试**：新增 `test_input_summarize_shapes.py`（14 断言）；
  test_weekend_pipeline 增依赖刷新/严格语义 2 用例；
  test_input_breaker 增真实 schema 用例 5/6。770/770 全绿。
- **仅报告不修**：知识簇零成簇——阈值 0.22/0.30 vs 08-15 实测
  30 篇 435 对最高相似度 0.161（仅 19 对关键词有交集），当前
  LLM 关键词风格下永远不成簇，后三环空转；标定需人工确认。

## v6.9.12 - 2026-08-15 输入端架构重构：知识簇链路（用户设计四点全落地）

背景：用户提出理想输入端设计——①信息提取（对未被提炼过的知识聚类
提炼）②课题判断（提炼内容 vs 全阶段课题，重合则融合、不重合则注册）
③融入机制（补充 proposal/信息源，进下周工作流）④聚类防冗余（新知识
沿已有类融入，不开新类）；并补充⑤源甄别设计（哪些知识可作聚类源）。
对照现状逐项评估：①伪聚类（每周无状态重猜）、③expansion 空转、
④⑤缺失、②存在 kb_concepts 恒空 bug。本次整体重构：

- **源甄别（⑤）**：`distilled_paper_ids()` 以 wiki/papers 页的
  arxiv_id/stem 为判据，已提炼论文不再作为聚类源（collect 层排除，
  不耗 summarize LLM 名额）；tier 分层 paper=1/briefing=2/capture=3/
  note=3，tier≤2 进聚类主源。实测首轮排除后仍有 500+ 未提炼积压。
- **知识簇注册表（①④）**：新增 `clusters.py`——簇状态机
  open→linked/closed；增量归簇 `assign_summaries`（关键词 Jaccard
  0.7+标题 0.3 加权，零 LLM 确定性），新摘要优先融入已有 open 簇；
  `form_new_clusters` 单篇不成簇（≥2 篇）、新簇与全部已有簇（含
  linked/closed）查重防换皮重开；orphan 42 天超龄清理、open 簇 4 周
  无更新自动 closed 防僵尸簇。注册表持久化
  `memory/weekend-input/clusters.json`。
- **课题判断（②）**：`topic_match` 取代旧 direction_select——
  `_load_all_stage_proposals` 直读 research_proposals/ 全阶段（旧版只
  读 KB 静态页 3000 字截断）；两级判断：Jaccard ≥0.35 高置信直判
  （archived→expansion，活跃→merge），中低置信 LLM 仲裁 top-3 候选
  （概念级重合，词袋测不出的场景）；LLM 不可用回退纯 Jaccard。
  顺手修复 kb_concepts 恒空 bug（processed_sources value 无 source_id
  键，旧 gap_analysis 的知识库概念输入从未生效）。
- **融入机制（③）**：compose 三路由全部落地——new→register_from_idea；
  merge→enrich_from_idea+信息源挂载；expansion→
  `_write_supplementary_sources` 把簇成员文献写入课题
  `02_literature/supplementary-sources-{date}.json`（references 校验
  与下周 writer 以课题目录为输入域，即进下一轮优化可见范围；旧版
  expansion 仅写建议 JSON 空转）。路由成功后簇标 linked 不再吸收。
- **job 链重构**：input 7 job → 6 job（collect→summarize→
  cluster_assign→cluster_distill→topic_match→compose）；旧 4 job
  （gap/select/retrieve/deep_read）由 `DEPRECATED_INPUT_JOBS` 清单
  在 sync 时清理 state 残留；summarize 摘要条目回填 source_id/path/
  tier 供归簇与挂载回溯。
- **验证**：新增 `tests/test_input_clustering.py`（36 断言：已提炼
  排除/tier 分层/增量归簇/单篇不成簇/两篇成簇/新簇查重/stale 关闭/
  全阶段路由 merge-expansion-new/6 job 链完整性+废弃清理）；旧套件
  同步新链口径（7 job→6 job、产物名清单）；修复 source_counts 对
  int 键 len() 崩溃；基线 717 → **753/753** 全绿。真实环境已切换
  （清理 4 废弃 job、新增 3 job）并重置 input 阶段用新链重跑。

## v6.9.11 - 2026-08-15 输入端积压治理：虚假标记清理 + 补课语义

背景：v6.9.10 修复"收集即标记"缺陷后，用户指出存量问题——306 条
processed_sources 里 93 条文献类标记是 bug 时期打上的虚假记录（文献
从未被真正摘要），仅删代码不清理数据，"恢复未处理"仍轮不到消费。

- **数据修正（一次性）**：清理 `weekend-pipeline.json` 中 93 条文献类
  虚假标记（briefing 52 + paper 40 + capture 1），保留 kb 类 213 条
  （gap_analysis 数据通路）。备份留存于
  `memory/weekend-pipeline.json.bak-vacuum-*`。
- **补课语义（窗口/上限豁免）**：清理后发现第二层结构性浪费——
  `collect_briefings` 按 mtime 7 天窗口过滤，积压文献 mtime 已老化，
  下周重跑即被窗口挡住；`collect_paper_pool` 按 mtime 前 20 截断，
  池中较旧的一半永远排不进。修复：新增 `_backlog_exempt`——来源
  从未被处理过（无标记）时豁免时间窗口与数量上限；已处理的维持
  原过滤。待处理语义由标记决定，而非文件新鲜度。state=None 时
  保持旧语义（向后兼容）。
- **summarize 单次容量 10 → 30**：每篇 LLM timeout 60s，最坏 1800s
  在 weekend job stale 阈值（3600s）内安全。旧值 10/周 < 稳态新料
  增速，消化能力不足。
- **实测规模**：补课语义生效后真实积压显现——577 条文献
  （502 篇论文 + 75 份简报）从未被处理过，此前被"前 20 上限 +
  虚假标记"双重掩盖。按 30 条/周转化，约 19 周清完；gap_analysis
  每周消费 8 条摘要，下周六（08-22）起 ideas 产出恢复正常。
- **验证**：test_input_pipeline_repair 新增 2 用例 7 断言（窗口豁免
  三场景/上限豁免三场景，含 state=None 旧语义回归），修复 stub
  用例间污染（_patch_collectors 增加 _restore_collectors）；
  基线 710 → **717/717** 全绿。

## v6.9.10 - 2026-08-15 周末输入端三项修复："成功空转"根治

背景：用户报告 input 任务失败。排查发现 7 个 input job 全部 done、
无 failed，但产物全空（directions=[]、ideas=0）——输入端自 v6.7.7
上线起从未真正产生过研究设想（08-01/08-14/08-15 连续全零），熔断
防线从未告警，stage_status 卡 pending。三项修复：

- **修复 1（核心）：收集即标记饿死摘要**——`collect_all_sources` 在
  收集时顺手把 papers/briefings/captures/reference_notes 全部
  `mark_source_processed`，随后 `summarize` 的 `new_paper_sources`
  过滤"未处理新料"恒为空，整条链空转。v6.7.7 原生缺陷，存在 9 天。
  修复：删除四类文献来源的预标记，标记职责归还消费方（summarize
  摘要成功后才标记，该逻辑已存在）；kb 类来源保留标记——
  gap_analysis 依赖 processed_sources 中的 kb:concept 记录作为知识库
  概念输入，且 collect_kb_concepts_and_methods 靠它去重。
- **修复 2：熔断防线被空跑刷新**——旧口径"最近一次 ideas=0 且距今
  ≥7 天"，但每周空跑一次 compose_ideas 就刷新 finished_at，
  days_since 永远到不了 7，防线形同虚设（全零 15 天零告警）。
  修复：改扫 `weekend-input/ideas-*.json` 产物文件族，最近 2 个文件
  ideas 均空即告警；损坏文件按 0 计（宁误报不漏报）。注意：修复
  部署后当期 monitor 会如实报一次 input_pipeline_broken（历史断流
  的真实反映），待 08-22 新料产出非零后自愈。
- **修复 3：stage_status 卡 pending**——worker cron 用 run_next 逐
  job 推进，旧版只有 run_stage 做阶段终态汇总，worker 推完整阶段后
  stage_status 永远停在 pending（控制台显示阶段未完成，实际 job 已
  全 done）。修复：抽 `_finalize_stage_status` 公共方法，run_next
  执行 job 后同样汇总。已对真实环境执行一次汇总修正（input→done）。
- **验证**：新增 `tests/test_input_pipeline_repair.py`（15 用例：预
  标记删除/新料过滤恢复/kb 通路保留/熔断触发-静默-单文件-损坏文件/
  run_next 终态汇总/中途不提前翻 done），重写 `test_input_breaker.py`
  适配新口径（4 用例）；基线 695 → **710/710** 全绿。

## v6.9.9 - 2026-08-15 writer/critic 提示词范本对齐 + 自优化架构加固

背景：对照申请书范本（references/nsfc-templates/）审查 writer/critic
提示词与 prompt_optimizer 自优化架构，发现两类问题——①标准层失真
（nsfc-standards.json 有 3 处描述与范本实测不符，优化器以失真标准为
锚点只会越优化越偏）；②自优化架构存在污染与单向膨胀（历史自动追加
的"总字数 ≥ 4000 字"等低标准指令与范本 2.5-3 万字体量冲突，且只增
不减）。本次逐项修复。

- **标准层校准（nsfc-standards.json）**：3 处失真描述按范本实测修正——
  ① `citation_style`"正文引用 35-47 次"系误将文献列表条数计入正文引用，
  校准为"[N] 编号引用 10-20 次即可（范本实测 10-17 次）"；②
  `sentence_rhythm`"单句一般不超过 60 字"与范本实测不符（38%-50% 句子
  超 60 字），校准为"超 120 字必拆、80-120 字技术性长句属正常"；
  ③ `anti_pattern_in_benchmarks`"完全不见'在此基础上'"实测面上范本
  出现 3 次，校准为"密度判定：模板化表达全文超 5 次为超标"。
- **范本守门机制（prompt_optimizer）**：新增 `BENCHMARK_GUARD_RULES`
  正则规则集，自动应用前拦截与范本实测口径冲突的量化指令——总字数
  下限 <10000 字、参考文献篇数区间偏离 20-40、评分魔法数（0.10 兜底
  等）三类历史污染形态全部拦截并记录原因，杜绝失真建议写入 SOUL.md。
- **指令化模板**：`_analyze_reasons_for_prompt_hints` 重构——原输出
  "需在 prompt 中要求 XXX"元描述（agent 无法直接执行），改为逐条
  可执行指令（如"逐条核对评审报告每个问题并逐一修改，输出末尾给出
  '问题→修改对照'清单"），并以严重度分级（high 触发即时约束追加）。
- **自动段回收**：自动追加段以 `<!--auto-opt:start:{sid}:{ts}:{pattern}-->`
  标记包裹；超过 14 天且对应失败模式近期未复现的段自动回收，实现提示词
  "有增有减"动态平衡，防止 SOUL.md 无限膨胀；问题复现时保留对应段。
- **运行时口径修正（proposal_lifecycle/optimize.py）**：运行时 prompt
  与校准后标准同步——参考文献篇数"15-30 篇"→"20-40 篇（范本 30-40 篇
  为标杆）"；句长">80 字应拆分"→">120 字必须拆分，80-120 字技术性
  长句属正常"，消除标准文件与运行时指令的口径分裂。
- **SOUL.md 手动修复工具（apply_prompt_upgrades.py）**：writer/critic
  SOUL.md 的历史污染段（总字数 ≥4000 字、每章节 ≥1200 字）替换为
  "篇幅对标"与"运行纪律"段；句长口径同步校准。沙箱内无 ~/.hermes
  写权限，需手动执行 `python3 scripts/apply_prompt_upgrades.py`
  （自动备份至 memory/prompt-backups/）。
- **验证**：新增回归 `tests/test_prompt_benchmark_guard.py`（38 用例，
  覆盖守门拦截/误拦豁免/指令化生成/标记解析/段龄计算/回收时机/问题
  复现保留），注册进 `--module` 基线 657 → **695/695** 全绿。

## v6.9.8 - 2026-08-15 周末流水线架构加固（评估五项改进全部落地）

架构评审结论："好架构欠了三笔小债"——核心决策（checkpoint 化/四层自愈/
模板幂等）正确，扣分集中在语义一致性层面。本次逐项落地全部改进。

- **P0 dry-run 零落盘**：`run_next`/`run_stage` 在 dry_run 时不持久化
  状态（此前预览会把假 done 写入状态文件，input/reflection 无自愈兜底，
  要等 6 天跨周重置才能恢复）。配套修复 dry-run 循环终止条件（零落盘
  下每轮磁盘 reload 会无限重复 pick 同一 pending job——dry-run 改为仅
  首轮 reload、复用内存状态推进）。
- **P1a 声明式产物校验**：job 模板新增 `artifact` 字段（PROJECT_ROOT
  相对路径 + `{date}` 占位符），`_verify_artifacts` 从 output 专用硬编码
  map 通用化为三阶段统一读取声明；`{date}` 以 job 自身 `finished_at`
  格式化（旧实现取检查当日，cron 晚一天跑就误重置）。`sync_stage_jobs`
  增加字段级合并：旧 state 已有 job 自动补齐 artifact 声明（零迁移）。
  顺手修复级联重置同一下游被重复遍历（日志重复 3 次）。
- **P1b handler 二元组注册**：注册 key 统一为 `(stage, step)`，消灭
  "job_id 优先、step 回退"双命名空间（同名 step 静默错绑风险）。原
  `STEP_KB_MAINTAIN` 拆分为 `STEP_KB_DEEP_HEALTH` + `STEP_KB_MERGE`
  （现 state 未含 v6.9.6 新 job，周日 reflection cron 尚未首跑，零迁移
  成本）。
- **P2a processed_sources 滚动裁剪**：`trim_processed_sources` 保留 28 天
  （实测 291 条只增不减），与 error_history 策略对齐；旧格式（纯字符串
  无时间戳）与缺 processed_at 记录保留不误删，sync 时自动触发。
- **P2b 锁粒度细化**：① `common.file_lock` 新增 `blocking=False` 参数
  （非阻塞抢锁失败抛 TimeoutError）；② `run_stage` 从整阶段一次持锁
  （LLM 慢时段可达数小时）细化为每 job 一持一放，worker 可在间隙抢锁
  协作推进；③ `run_next` 非阻塞抢锁，锁忙温和退出（skipped=lock_busy），
  杜绝 worker cron 每 20 分钟 spawn 的进程在 flock 上堆积。
- **潜伏 bug 顺手修复 2 个**：① `JOB_STATUS_FAILED` 从未进入 pipeline
  import，run_stage 汇总段在"部分失败"路径必抛 NameError（此前因
  all()/any() 短路从未触发）；② `input_summarize` 无新论文时提前
  return 不写产物文件——实测 08-14 周六该路径真实发生，产物缺失被
  新校验正确捕获并重置，修复后无条件写空 summaries 防重置空转。
- **验证**：新增回归 `tests/test_weekend_pipeline_hardening.py`（11 用例
  35 断言，覆盖 dry-run 落盘/产物校验三阶段/finished_at 防错位/字段级
  合并/二元组完整性/裁剪/非阻塞锁/温和退出/per-job 锁等价性），注册进
  `--module` 基线 622 → **657/657** 全绿；真实环境 `--input --dry-run`
  实测：input 7 job 补齐 artifact、假 done 自愈重置、processed_sources
  裁剪无副作用。

## v6.9.7 - 2026-08-15 体检修复：kb_distill 蒸馏页 created 时间戳冻结

- **缺陷**：`kb_distill._ensure_source_raw` 硬编码 `now = "2026-08-15T00:00:00Z"`。
  蒸馏系统提示要求 LLM"直接输出 Markdown 正文（frontmatter 由系统补写）"，
  即"无 frontmatter → 构造合规头"是**主路径**而非边缘分支——lc-kb-distill
  cron（每日 12:50，5 篇/天）产出的新页 `created` 将全部冻结在 2026-08-15，
  系统性污染 KB 新鲜度指标（kb_health）与 growth_engine 晋升时序。
- **修复**：改为 `common.now_utc()` 取真实当前时间（最小化定向修复，
  `save_distilled_wiki` 门面确认不覆盖 created/updated，冻结值会原样落盘）。
- **验证**：`kb_distill.py --self-check` 新增第 5 项断言（created 与当前
  时间差 <24h）5/5 通过；新增回归测试
  `tests/test_kb_distill_created_ts.py`（5 断言）注册进 `--module` 基线，
  617 → **622/622** 全绿。
