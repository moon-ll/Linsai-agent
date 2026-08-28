# 变更记录

## v6.9.69 - 2026-08-28 模型逃生机制：主模型静默挂起时备用模型接管而非停摆

**根因（08-27/28 危机复盘）**：zai 限额期失败形态是"静默挂起"（连接建立后
无字节返回、无 429 文本）。hermes 内部降级只认明确报错（error_classifier
的 rate_limit/billing 分支），普通 TimeoutError 归为同供应商重试；唯一能从
挂起走到降级的 stale-giveup 需 5 次连续静默而重试上限 3 次结构性达不到，
且 3×300s(大上下文 stale)=900s 恰好等于 CoPilot 击杀线——9 个终态 job
全部死在重试循环中途（超时+零输出+零 429），备用链 3 条一条都没轮到。

**三层修复**：
1. 编排层模型逃生（circuit_breaker.py + optimize.py `_run_hermes`）：
   长输出 job 连续超时达 LONG_TIMEOUT_THRESHOLD(3) 时激活逃生——调度
   照常不停摆，hermes 调用经 `escape_override_target()` 注入
   `--provider minimax-cn -m MiniMax-M3` 强制备用模型；每 30min 放行一次
   主模型试探（成功即解除）；备用连续失败达 ESCAPE_FAILURE_LIMIT(3)
   → open 真停摆（主备全挂）。api_error（明确 429）路径保持原停摆语义。
2. 提前 hermes 自身 stale 放弃（`HERMES_STREAM_STALE_GIVEUP=2` 环境注入）：
   give-up 触发 error_classifier 7b 分支 should_fallback=True，hermes
   得以在击杀前按自身 fallback 链降级（与编排层逃生双保险）。
3. profile 链首跨供应商（hermes 侧配置，已备份）：critic/reviewer 的
   fallback 链首 zai/glm-5.2（同账户兜不住账户级限额）调整为
   minimax-cn/MiniMax-M3 优先。

**验证**：circuit_breaker 自检 14 路径全过（逃生激活/注入/试探解除/主备
全挂停摆/probing 长超时转逃生）；test_mechanism_hardening 新增 16.x 套件
12 用例（源码守卫+功能闭环）；全量模块回归 1227/1227；端到端实弹验证
（mock Popen 走真实代码路径）四场景全过，日志确认
`[model-escape] critic 强制备用模型: minimax-cn/MiniMax-M3`。
生产熔断器已复位 closed（主模型实测恢复 19.6s），今晚 18:30 时段起
201 个积压 job 恢复推进。

## v6.9.68 - 2026-08-28 优化环节运转评估：critic 超时根因治理（报告解析噪声闭环）+ 测试隔离补桩

按用户指令评估申请书优化环节近期运转。数据结论：**质量机制本身在生效
（范围校准已被 critic 实际采用：新报告零研究基础/团队要求，qg R3 按新
四维评分且明确认可"不将合作意向作为可行性前提"；AI 检测器修复后 qg/kt
天花板 0.87/0.90），但协作链路出现恶性循环——critic 24h 成功率崩至
7%（28/30 全超时，全课题全时段）**。

根因链（数据实证）：

1. `_extract_issues` 解析器逐行扫描"含 [critical]/[high] 字样即收"——
   critic 报告中的 Markdown 表格行、评分说明、交叉引用全部被误收为
   issue，一行多标记还重复收集。实测 R8 报告产出 28 条表格行垃圾。
2. 垃圾经 open_critical_issues 全量注入下一轮 critic prompt（attosecond
   29 条未解决 6.4KB，要求"逐条核对"）→ 评审输入膨胀 + 注意力稀释。
3. critic 被迫写巨型报告（R8 达 37KB——输出 token 是超时主因之一）→
   新报告又被吸成更多垃圾条目 → 恶性循环。

修复（四层）：

- **解析器源头**：噪声行过滤（表格/标题/代码块/评分说明/执行清单/
  锚点结论行）+ 每行只收最高严重级 + 20 字实质下限 + 去重。R8 报告
  实测 28 垃圾 → 3 条真 issue。
- **注入侧限量**：P0 记忆块过滤噪声 + critical 优先 + 上限 12 条
  （原全量 40 条）；writer 侧同函数自动受益。
- **存量清洗**：3 课题 57 条垃圾条目标 stale（berry 11/new-idea 21/
  attosecond 25），保留有效 P0 24 条。
- **报告体量纪律**：critic prompt 注入"报告 ≤6000 字，逐条对照用简短
  结论行"——直接压缩输出 token。
- **测试隔离补桩**：monitor lark 去重测试因真实 human_queue 的 bsv
  催办（>72h）泄漏而 notified_count 期望 1 实际 2——补桩健康信号/
  负反馈自愈/human_queue 三处真实数据源。

观察指标（24h）：critic 成功率应从 7% 回升至 >50%；若仍 <20%，
下一步是 critic 输入的进一步瘦身（standards 按需分片加载）。
与并行会话 v6.9.66/67 的熔断器（连续超时止损）形成输入/运营两侧互补。

- 验证：四层回归 1215/16/38/1466 全绿；R8 报告解析对比实证；
  存量清洗前后 open_critical_issues 统计。

## v6.9.67 - 2026-08-28 熔断器 probing 活性保证：试探放行无回报卡死闭环修复 - 2026-08-28 熔断器 probing 活性保证：试探放行无回报卡死的闭环修复

背景：v6.9.66 人工熔断后复查发现系统未按预期自愈——熔断器 10:30 冷却
结束转 probing 并放行试探，但执行记录 0 条（放行的试探 job 因调用方
后续逻辑未实际执行），而状态机只有 record_job_result 回报才能推进，
probing 从此卡死：后续每 5 分钟 tick 全部被拒，201 个已就绪 pending
job（repair 00:00/06:00 已重置大部分 failed）一个都没跑。

根因：allow_dispatch() 的 probing 语义"只放行一次试探、其余拒绝"缺
活性保证——试探 job 丢失时无任何机制推动状态机（v6.8.50 原始设计
缺陷，8/19 两次自愈纯属试探 job 恰好执行并回报，今天首次触发）。

修复：probing 态超过 PROBE_TIMEOUT_S（30min，覆盖 tick 5min + 长 job
上限 1200s 的正常试探回收窗口）无回报 → 重新放行一次试探并刷新
时间戳。每 30 分钟至多消耗一个试探窗口：配额未恢复时试探失败回
open 冷却循环（v6.9.66 长超时/probing 失败回 open 路径），恢复后
30 分钟内必有一次试探成功 → closed → 恢复全量派发。

- 自检新增路径 8（probing 单次放行/超时重新放行/窗口内不重复/
  重新试探失败回 open），覆盖 08-28 卡死场景闭环。
- 卡死现场无需人工干预：last_transition_at 已超阈值，下个 tick
  自动触发 reprobe。
- 验证：circuit_breaker --self-check 全过；--module 1215/1215 全绿。

## v6.9.66 - 2026-08-28 熔断器补盲：长输出 job 连续超时熔断（配额限流"空输出触顶"特征）+ 人工止血

背景：观察项复查发现 8/27 晚至 8/28 晨超时率 74%（28/38）——短输出
job（lit_search/gap_identify/lit_note）全部成功，critic/writer/monitor
长输出全部"空输出+恰好触顶"失败，微调度器单实例连续 3h 串行碾磨超时
job，7 课题重试次数烧尽全部 stuck（08h 健康检查实录）。v6.9.62 手动
重置的 3 个 job 在配额期全部再超时烧尽——证实根因是配额限流而非输入
问题。既有熔断器只识别 429 文本（api_error:* 前缀），对本次失败模式
完全失明，原注释明确"超时不触发熔断"。

修复：

- **熔断器补盲（circuit_breaker.py）**：`record_job_result` 增加
  `job_kind` 参数（long/short，默认 long）——长输出主链
  （critic/writer/monitor/idea_review/update_vision/update_method_manual）
  的超时类失败单独计数 `consecutive_long_timeouts`，达阈值 3 触发
  open；短输出 job 的成功/失败均不影响该计数（配额限流期短输出间歇
  成功不该清零长链计数）；长输出 job 成功才清零。probing 态试探超时
  同样回 open。非超时失败（解析错误等）仍走原路径不触发。
- **人工熔断入口**：`--open REASON` CLI + `force_open()`——本次配额
  期立即止血（09:27 熔断），冷却 1h 循环试探，配额恢复（预计 17:32）
  后试探成功自动 closed，无需人工复位（状态历史可见 8/19 该机制两次
  正确自愈的前例）。
- **微调度器回报口**：按 job 的 step 映射 job_kind 传入熔断器，熔断
  日志同时输出两类计数。

- 自检新增路径 6/7（长链连续超时熔断/短超时不计/短成功不清零/
  2 次未达阈值不误熔断/跨短成功达阈值仍熔断）与路径 8（force_open
  →冷却→probing→自愈全链路）；--module 1215/1215 全绿。
- 附注：monitor 900s 上调在配额间歇窗口已验证有效（berry 16:38
  monitor 成功，此前四连超时）；quality_gate_passed 收敛观察因配额期
  writer 几乎未执行暂无新数据，待配额恢复后观察。

## v6.9.65 - 2026-08-27 遗留事项处置收口：维度完整性防线 + monitor 超时上调 + R1/R2/R4 + R3 测试调度迁移

背景：治理总结报告的五项遗留事项经用户裁决处置（事项 1 裁决为"申请
书不涉及平台条件类内容——聚焦研究思路与内容"；事项 2-5 按建议执行）。
时序说明：本批代码修改与 16h/20h 健康检查及人工对标优化（v6.9.62-64）
在同一工作区并行推进，代码已随上述提交入库（v6.9.64 报告的
1215/16/38/1466 全绿已包含本批 15.x 断言），本条目为完整补记 +
R3 新增。其中事项 4 在核实中确诊根因：

- **维度完整性防线（事项 4，确诊为解析丢失而非质量回落）**：attosecond
  r7 rationale 轮 dim_scores 只解析出 rigor/completeness 两维
  （innovation/feasibility 缺失），0.58 实为残缺口径均值。残缺分数进
  score_history 会污染天花板收敛/次优平台/质量下降三类检测与 agent
  奖惩。修复：① executor 解析后校验维度完整性（正文章节轮期望
  DIMENSION_FLOOR 全维），dims_partial/dims_present 入史可观测；
  ② completion.py 三个检测窗口全部过滤 partial 轮；③ monitor 收尾时
  残缺轮跳过 agent 奖惩（零增量而非 None，对齐 v6.8.48 模式）。
- **monitor 超时 600→900（事项 3）**：600s 在 MiniMax 慢速期连续触顶；
  v6.9.61 输入瘦身后 900s 余量充足。同事项手动重置 3 个解锁配额耗尽
  的终态 failed job（moire r5-content / order-param r7-references /
  kt r1-content，manual_reset_at 审计），其余由 24h 自动解锁与依赖链
  重试兜底。
- **R1 可信池两步降噪（事项 2）**：删除"head 需含 doi:/arxiv 字样"
  gate（266/741 页整页丢弃根因），head 提取为空回退全文（消除 187 个
  截断漏检）——只影响"有没有提取到"，不影响"ID 是否可信"，灵敏度
  不降。实测池 484→650 ID，order-param 未命中降至 5/44（原误报
  20-96%）。
- **R2 cron 安装闭环（事项 2）**：framework.py 补 lc-daily-backup/
  lc-daily-sync 安装器（原仅 manifest 登记，teardown+setup 后永久
  消失且监控端不可自愈）；controller.py 补 wrapper 生成；cleanup
  默认清单纳入；调度常量入 lifecycle/constants.py。
- **R4 备份窗口 + 测试零污染（事项 2）**：lc-daily-backup 03:17→13:00
  （避开 worker 时段 860MB zip 并发写风险）；test_leak_guard 学习缓存
  用例改 patch 临时文件（原直读真实 memory/.cache）。
- **R3 测试调度迁移（本轮新增）**：self_test._run_selected（--module/
  --scenario/--persona/--web 入口）从裸调迁移到 execute_suite——旧
  实现套件中途崩溃时 teardown 跳过且失败不计数，"--module 全绿"存在
  假阳性面（12h 健康检查 R3；v6.9.54 同类修复只覆盖全量路径）。
- **内容边界红线（事项 1 用户裁决，与 v6.9.64 撰写范围校准互补）**：
  writer prompt 明示"申请书聚焦研究思路与研究内容，严禁撰写研究基础/
  实验平台条件/设备参数/合作声明——系统不掌握申请人真实信息，写入必
  是虚构，必须由申请人本人补充"。孤儿章节内容维持 05_review 存档。

- 验证：--module 1215/1215；--scenario 16/16；--persona 38/38 全绿
  （R3 迁移后复跑确认三个入口调度行为一致）。

## v6.9.64 - 2026-08-27 撰写范围校准：聚焦研究思路，剥离研究基础/工作条件类个性化内容

背景（用户校准）：范本申请书是完整真实申请书，含研究基础/研究条件等个性化
内容——这些不是本项目的撰写与优化目标，本项目聚焦研究思路与内容。排查确认
偏差真实存在且有三层：

- **标准层自相矛盾**：proposal_templates._note 已写"不撰写研究基础与团队"，
  但 project_types 的 evaluation_focus 仍含"研究基础权重 0.15"（面上）/
  "团队实力 0.15 + 研究基础 0.10"（重点），structure 仍写"三段式含研究
  基础"，review_checklist 有"研究基础是否厚重（高水平论文+预研数据）"——
  critic 按这些权重评审（实测 kt critic-round-6 引用权重表并按"团队实力
  0.55 权重在产出维度"做心理效应分析）。
- **申请书层存量**：qg 写入了整段"三条能力线"（实验平台运维指标/代码复现
  细节/多体模拟预研）+ 合作矩阵协议状态与共同发表清单 + 经费论证三段
  （60 万明细/人员费分层）+ 人力配置段——21 处命中，全属个性化内容。
- **权重归一**：面上（创新 .35/可行 .30/意义 .25/表达 .10）、重点/青年
  同步清理，review_checklist 删除研究基础/团队两项。

修正（三层）：

1. **standards 源头**：nsf_context.structural_reform_2026 加本项目口径注记
   （改革事实保留，范围仅研究思路部分）；三类项目 structure/权重/checklist
   清理；新增 general_principles.scope_exclusion 全局规则（研究基础/工作
   条件/团队/经费不撰写、不评审、不扣分，可行性仅保留"原理+方法对照+降级
   路径"，已有内容压缩至最简）。
2. **prompt 注入**：critic（optimize.py:1046）与 writer（:1816）的重点读取
   清单加入 scope_exclusion，确保 agent 实际读到新规则。
3. **qg 申请书清理**（21 处 → 3 处合理保留）："三条能力线"压缩为三句最简
   可行性（复现事实保留一句+手册引用）；合作矩阵压缩为两句（外部依赖+降级
   路径，删协议状态/发表清单/单位人名）；算力两段压缩为一句；删除经费论证
   三段与人力配置段（-611 字，scheme 10119 中文字回落至预算线）；人才
   培养段压缩（去 ICFO 个性化细节）。kt/order-param 剩余命中为他方文献
   基线引用与最简可行性声明，属合理内容保留。
4. **运维对齐**：发现并行会话已将 lc-daily-backup 清单调度改为 13:00 但
   实际 cron 未同步（对账漂移）——重新注册对齐，测试基线同步。

- 验证：四层回归 1215/16/38/1466 全绿；cron 对账 0 问题；qg draft 刷新。

## v6.9.63 - 2026-08-27 人工对标范本优化全量申请书 + 检测器口径修复 + 备份盲区补录 - 2026-08-27 人工对标范本优化全量申请书 + 检测器口径修复 + 备份盲区补录

按用户指令对标范本（benchmark_anchors：嵌入式引用/数据驱动/段间逻辑衔接）
人工优化全部 7 个 optimizing 课题。**改前发现并修复备份盲区：BACKUP_TARGETS
不含 research_proposals——申请书正文此前不在备份范围**（已补录，改前先做
research_proposals 专项备份）。

**中文字口径基线体检**（修正了此前按文件字符数的误判——ASCII 公式/图表
占大量字符，真实分布是"两个老课题超长、四个新课题偏短"）：

- **kt-transient（0.76）重灾区深度治理**：rationale 从 24286 字符（约 9500
  中文字，超预算 19%）对标重写为 4765 中文字——消除"定义-实现-测量"因果
  链 7 处重复陈述、Lesko[64]/Zhao[65]/Zhang[66] 等核心文献各 3-4 次的重复
  详述、§2.3 四级控制过度铺陈；72 条文献引用点全保留（ghost/orphan 零），
  嵌入式引用与全部量化指标原样织入压缩版。17 处超长句程序化拆分。
- **qg（0.81）结构修复**：发现 content 与 scheme 双份维护同样的任务细节
  与年度计划（两章均超预算的根源，亦即 quality_gate 的跨章节重复病灶）。
  删除 content 内嵌的 §2.6 年度计划（scheme 已含完整时序，NSFC 结构年度
  计划本属研究方案域）+ 元叙述修剪：10412→8566 中文字。
- **attosecond（0.72）P0 文献闭环**：R8 报告 5 项 P0 中 4 项已被自动管线
  后续轮消化（验证 [29] 页码已正/[34] 已删/Schultze 氛氖已正/区间四口径
  已统一），人工补刀 2 处残留：[19][20] 国际文献（Ishii-日本UEC/
  Popmintchev-JILA）从上海光机所归属中剥离（张冠李戴 critical）；
  "[（需补引）]"占位符清除。
- **berry（0.51）文献修复**：Yarmohammadi [20]→[18]、Yang-Liang [17]→[14]
  编号错配改正；6 个孤儿引用编号处置——2 条从检索产物池反查回填真实条目
  （[30] Haque THz 对称调制/[34] Sheng 滑移铁控，arXiv ID 可溯）、Basnet
  重复编号归并 [17]、3 个无源角标删除（绝不凭空补造元数据）。孤儿引用
  归零；[1-4,13] 存量 ghost 留待 critic 提示补引。
- **全课题程序化卫生**：berry/new-idea 的 full_review 骨架补齐（615/542
  字符）；7 课题 draft 汇总视图刷新。

**产品级修复（优化过程中发现）**：
- **AI 检测器口径 bug**：章节内嵌参考文献表（kt/qg 的 ### 参考文献）
  被计入写作检测，文献条目的长行被判为"超长句"（实测 kt 一篇 72 条
  文献表贡献 11 处假超长句，天花板被错压至 0.50）。检测前剥离文献表，
  kt 真实天花板恢复 0.66→拆句后 0.90。
- **备份盲区**：BACKUP_TARGETS + research_proposals。

**偏短课题（berry/new-idea/attosecond/moire 共 9 篇章节低于预算下限）
不人工扩写**——注水扩写违背"字数是症状质量是根本"理念，交由自动
writer 轮次按聚焦章节逐步补强。

- 验证：四层回归 1202/16/38/1453 全绿；改后统一自验（AI 天花板/字数
  预算/编号一致性/来源校验）通过；research_proposals 专项备份先行。

## v6.9.62 - 2026-08-27 16h 健康检查：孤儿章节守卫同日再生成丢内容修复

背景：第十二轮设计抽查（#7 质量天花板 / #8 停滞检测 / #9 输入端熔断，
全部正常）中对 v6.9.61 新增守卫做边界审查时实锤一处数据丢失：

- **孤儿章节守卫同日再生成静默丢内容**（`section_hygiene.py`
  `handle_orphan_sections`）：writer 同日在不同 job 两次违反章节白名单
  红线时（既有实证：new-idea 曾自创 `research-foundation.md`），首次
  孤儿被存档至 `orphan-section-{key}-{date}.md`；第二份含新内容的孤儿
  命中 `dest.exists()` 分支被直接 `unlink()` 不存档——违反"产出即
  资产"原则。修复：改序号后缀（`-{date}-2/-3…`）追加存档后再移除，
  以同内容冗余存档代价换零丢失，幂等语义不变。
- 回归：`test_mechanism_hardening.py` 新增 14.3b（再生成 → 两份存档且
  新内容完整保留）；`section_hygiene --self-check` 通过；全量
  `--module` 1202/1202 全绿（1198 + 4 新断言）。
- 报告不修复（设计缺口待人工确认）：quality_warning 只写不清，课题
  分数回升后残留历史下降警告（qg 实证）可能误导 dossier 预审。
- 运行时最高优先发现（不属代码缺陷）：超时链致 kt r1 / moire r5 /
  order-param r7 的 critic job 永久闭死（attempts=3 + repair_attempts=4
  + auto_unlock_count=1 三路全拒）；qg/new-idea/attosecond 待 08-28
  各自 24h 线首次解锁重跑，再失败将扩至 6/7 课题——"critic 超时档
  与 writer 分离"人工裁决紧迫度显著上升。
- 完整报告：`logs/healthchecks/healthcheck-2026-08-27-16h.md`。

## v6.9.61 - 2026-08-27 第二轮全环节审计：monitor 输入瘦身 + 笔记去重 + 检索产物裁剪 + 孤儿章节守卫

背景：继续按"结构不变量靠约定、写入/读取边界信任 agent 行为"的病灶
模式审计剩余环节，实锤四处（其中 monitor 是正在发生的超时现案）：

- **D. monitor 输入从未瘦身（现案根因）**：monitor 同时读组装全文
  `proposal-draft.md`（40-140KB，含 references 列表与 full_review 骨架）
  + 上一轮组装全文（再一份）+ critic 报告 + standards，合计 120KB+。
  08-27 new-idea monitor 4 连空输出 600s 触顶的直接输入侧根因——
  critic 侧同类问题 v6.9.46/53 已排除，monitor 是最后一个未瘦身的
  读取方。修复（`adversarial/monitor.py`）：① 评审视图
  `_build_monitor_review_view`（正文三章节拼接，排除 references/骨架）
  替代组装全文；② `_build_monitor_diff_summary`（difflib 程序 diff，
  限 400 行）替代 prev 全文——monitor 只需"改了什么"，不需读第二份
  全文；③ critic 报告接 v6.9.60 digest。规则检测
  （detect_*_prohibitions）仍读全文（本地零成本不受影响）。
- **E. 阅读笔记同文献重复条目**：writer 步骤 9b"追加一条记录"无查重，
  attosecond 同一 arXiv 文献两条笔记（2608.18905）。修复：
  `dedupe_reading_notes` 按 `## {arxiv-id}` 标题或条目内 arXiv ID 字段
  分组，同 ID 保留最新（追加序=时间序），零 LLM。
- **F. 定向检索产物无界累积**：gap-analysis/*.json 与 targeted-research/
  lit-gap-*.md 每轮新增从不清（order-param 单课题 59+58 个文件），
  writer 只读最新一份。修复：`prune_targeted_research` 滚动裁剪至最近
  12 个/目录（覆盖约 4 轮），旧件移 `05_review/.archive-targeted/`
  （移动不删除，数据安全）。
- **G. 孤儿章节（schema 盲区，资产静默丢失）**：writer 按 NSFC 2026
  三段式自创 `research-foundation.md`（2.4KB 研究基础），但组装按
  PROPOSAL_SECTIONS 五模块白名单 → 内容不进申请书、评审不读。修复：
  `handle_orphan_sections` 非白名单章节迁 `05_review/orphan-section-
  {key}-{date}.md` 存档（内容不丢，提示人工并入正文）；writer prompt
  加"章节文件白名单"红线（研究基础等内容并入 scheme.md 相应小节）。

- 守卫挂载：E/F/G 全部并入 `guard_written_artifacts`（writer 落盘后
  当轮执行，幂等）与 `apply_all`（一次性存量清理，已执行：去重 4 课题
  6 条、裁剪 5 课题 234 旧件归档、孤儿章节 1 课题迁出）。
- 测试：SectionHygieneTests 扩展 14.1-14.6（去重保最新/幂等、裁剪
  保留数/归档不删、孤儿迁出/内容存档/幂等、monitor 三项瘦身源码守卫、
  白名单红线、守卫注册）。
- 验证：209/209；--module 1198/1198；--scenario 16/16 全绿。

## v6.9.60 - 2026-08-27 同构问题治理：手册单一真相源 + critic 报告 digest + 晋级完整性门

背景：用户要求排查"其他环节是否有同类问题"。按"结构不变量只靠
prompt 约定、写入边界信任 agent 输出"的病灶模式全环节审计，发现
三处同构问题（研究设想/阅读笔记/手稿纯净性经查干净）：

- **A. 方法学手册双真相源分裂（最严重）**：`03_method/method-manual.md`
  （update_method_manual derived job 维护，实测 47KB 含成片重复）与
  `04_proposal/methodology-manual.md`（writer prompt 第 9b 步 + 配套
  同步路径两处写者维护，10KB）并存——同一资产两个文件、三个写者、
  读者（weekend output/kb_sync vs writer prompt）各指一处，互不同步。
  修复：单一真相源 = `03_method/method-manual.md`；writer prompt 第
  9c 步改为"不由本步骤更新"（消除双写根源）；配套同步路径改指
  03_method；derived 步骤 prompt 增手册质量纪律（先读后改、禁文末
  追加重复段、禁过程记录）。存量一次性迁移：7 课题旧手册归档
  `05_review/methodology-manual-legacy-{date}.md` + 原位 stub 指针
  （canonical 缺失时先落位防悬空，幂等）。
- **B. critic 报告无篇幅约束（16-37KB）**：writer 每轮必读全文，
  是超时输入大头（章节瘦身后的最大残留输入）。新增
  `build_critic_digest()`：报告 >25KB 时程序化提取问题结构
  （severity 行/标题/表格/评分块，纯叙述丢弃），按字节截断至 ≤8KB
  （中文 3 字节/字，字符截断会放大约 3 倍——首版实测 13KB 已修），
  digest 头注明完整报告路径。实测 37KB→8KB、30KB→8KB。
- **C. 晋级边界信任状态**：`_check_and_transition` 只看分数不查本轮
  job 完整性——08-26 实证 bsv 带 2 个 pending derived job 晋级
  pending_review。新增晋级完整性门：本轮存在非 done job（含 derived）
  则暂缓晋级（记日志），下个 tick 自然重试；failed 由 repair/自动
  解锁兜底后仍可晋级，不死锁。

- 测试：SectionHygieneTests 扩展 13.1-13.4（digest 触发/限额/保留
  结构/丢叙述、手册迁移幂等/stub/防悬空、optimize/executor/micro_
  scheduler 三处源码守卫）。
- 验证：189/189；self_test --module 1178/1178 全绿。

## v6.9.59 - 2026-08-27 12h 健康检查：v6.9.53-57 六缺陷定向修复（晋级主路径解封 + 预检误杀 + 丢写/丢记录）

三层诊断（运行时健康 + 代码缺陷 + 设计一致性 #4/#5/#6）发现并修复：

- **质量门误伤非正文章节（严重，引爆前拦截）**：v6.9.55 把预算门重构
  为质量门时丢失 v6.9.54"无预算章节恒通过"出口，且 cross 判据全局
  化——7/7 课题正文存在跨章节重复（cross_exact 1~20）时，
  references/full_review 轮 writer（指令约束只改聚焦章节，物理上
  无法消除正文冗余）永远 passed=False，晋级主路径（5 模块全通过）
  被系统性封死，且静默空转无告警；_lifecycle 中 quality_gate_passed
  零次出现 = 新代码路径尚无真实 writer job 执行，未引爆即修复。
  修复：非正文章节零信息通过；设计边界固化为显式语义——
  detect_redundancy 只扫三正文章节，references/full_review 结构卫生
  由写入门卫（guard_written_artifacts）专职负责（测试 12.5b/12.5c
  防回归）。真实数据验证：moire/attosecond 的 references/full_review
  恢复通过，rationale 保持拦截（3 exact + 17 similar）。
- **section_hygiene --self-check 断言过时（复现失败）**：v6.9.55 将
  budget_report_text 重构为纯信息性体量参考后，_self_check 仍断言
  "净删/削减至"字样 → 自检必然失败；断言同步新语义。
- **次优平台 quality_warning 生产端丢写（v6.9.57 功能死到达）**：
  _get_proposal_state 每次磁盘新读无缓存，completion.py 次优平台分支
  只写内存副本、not-done 路径无落盘调用 → 警告即写即丢，
  review_dossier 永远读不到；单测 mock 返回同一 dict 引用恰好掩盖。
  修复：写入后 _set_proposal_state 落盘；测试 mock 升级为磁盘新读
  语义（deepcopy + set_calls 断言），此类丢写从此可被测出。
- **references 预检 ID 归一化全角标点污染（7 课题实测 9 条合法文献
  误杀）**：DOI 正则排除集不含全角"；，、"，"DOI: 10.1364/...；arXiv:
  ..."吞成复合污染 ID 无法命中可信池 → 误报"虚构风险"；同类还有
  markdown ** 尾缀；arXiv 分支行尾句点整条漏提取。修复：排除集补
  全角标点 + DOI/arXiv 双分支统一 rstrip + arXiv lookahead 放宽尾部
  句点（测试 8.6b 三组真实形态）。
- **guard 迁移产物同日覆盖丢首次记录**：full-review-record-{date}.md
  固定日期文件名 + write_text 覆盖写，writer 污染同日复发时首次记录
  丢失（违反"产出即资产"）；references-worklog 同构。修复：文件已
  存在改追加（带时间戳分隔注释）。
- **prune_backups 误删应急备份**：按 mtime 保留 backups/ 顶层全部
  zip 最近 7 份，含 *-manual.zip / *-pre-restore.zip（restore 撤销
  安全网）——daily 连跑 7 天后应急备份被静默 unlink；排除出轮转候选。
- **报告不修（待人工裁决 R1-R4）**：R1 可信池 gate 比提取器严
  （head 预筛丢 266/741 页 + 2KB 截断 + 池不含学科经典 → unmatched
  误报率 20%-96%，真实经典文献被标"虚构风险集中区"）；R2
  lc-daily-backup/lc-daily-sync 入 cron_manifest 但 framework 安装器
  /controller wrapper 不含（teardown+setup 后备份 cron 消失且不可
  自愈）；R3 self_test _run_selected 仍旧调度（v6.9.56 teardown 修复
  只覆盖全量入口）；R4 03:17 备份与 00:30-03:30 worker 时段重叠。
- **设计一致性抽查（第十一轮 #4/#5/#6）**：Agent 分数奖惩闭环正常
  （writer 73.1/critic 125.775 有界 + 跨课题 round_ref 闭环）；Prompt
  优化器正常（库存 12 条新鲜，TARGET_PROFILES 5/7 偏差维持）；P0 跨
  轮持久化正常（注入链经大改后完好）。下一批 #7/#8/#9。
- **调度链路澄清**：lc-* cron 由 hermes gateway 内置调度器承载
  （~/.hermes/profiles/linsai/），系统 crontab 为空属正常部署形态。
- 验证：py_compile 4 文件通过；section_hygiene --self-check 通过；
  归一化/质量门真实数据端到端通过；self_test --module **1164/1164
  全绿**（基线 1155 + 新增 9 断言）。

## v6.9.58 - 2026-08-27 架构审计落地：前端断层修复 + 输入链路查重 + 死代码激活 + 对账盲区消除

按架构级审计清单逐项处置（前端 13 天未更新/295 条后端路由活 UI 仅触达 30%）：

- **前端断层修复（P1，四子项）**：
  ① pipeline.js 9 条坏链修复（gap-analysis→gaps 系改名对齐、
  write-all→write、单条 citation CRUD 后端缺失改为列表内取数/明确提示）；
  ② 侧栏恢复"申请书工作台⚗️/Hermes 中枢🤖"工具入口（v6.8.0 移除入口
  后两模块 55 端点不可达——复用其既有的 #toolbar-* 绑定路径，零 JS
  侵入；app.js 导航绑定跳过无 data-view 的工具按钮）；
  ③ 全链路页新增**想法收件箱面板**（incoming 列表/激活/拒绝/展开，5
  条端点首次有 UI）与**周末任务面板**（input/output/reflection 三 job
  状态+错误+手动执行）；④ 控制台新增**调度策略面板**（当前值 vs 建议
  diff + 单项确认应用 + tuning-log 历史，strategy_optimizer 3 周 0
  采纳的人工通道补齐）与总控面板入口；script 版本参数 6.8.0→6.9.58；
  app.js 33 行 learning 死引用清理（learning.js 未加载靠 ?. 掩盖）。
- **输入链路查重（P2）**：08-22 追查确认立项闭环完好（两 new 路由均
  落地，attosecond 有一次 ID 不合规人工补救记录），但发现真问题——
  交变磁体簇的语义相关课题（berry-mnps3）被 Jaccard 预筛 top-3 截断
  排除在 LLM 仲裁视野外，致与 idea_generator 路径重复立项
  （new-idea-20260822 vs berry 同方向并存）。修复：仲裁候选 top-3→
  top-8（每候选一行成本可忽略，截断漏检代价是整个重复课题）。
- **维度轮换死代码激活（P2）**：v6.8.24 的 [-12:] 窗口仍是算术错误
  ——section 周期 6 轮下 12 窗口同 section 最多 2 次，>=3 永不可达
  （实测 0 触发）。窗口改 [-18:]（3 个完整周期），r12 起可达。
- **strategy_optimizer 接入 human_queue（P2）**：新增第四类
  "strategy" 聚合（非白名单键的待确认建议进队列，1h 文件缓存防重算）
  ——中高风险策略建议此前只活在 dashboard JSON 无人消费。
- **对账盲区消除（P1）**：lc-daily-sync（23:00 日终同步）补录
  CRON_MANIFEST（第 10 项）——此前游离清单外违反"单一真相源"自述，
  monitor 对账实测 0 问题。
- **运行环境治理（P3）**：/api/version 附进程启动时间（修"版本号新
  但代码旧"的显示失真，实测 8/3 实例曾显示 6.9.57）；三个旧代码常驻
  web 实例收敛为 8080 单实例（最新代码）；5 个遗留 lc_worker_*.sh
  清理（保留在用的 lc_weekend_worker.sh）。
- **quality_gate 双投评估（P2，结论不动代码）**：critic 侧注入实测
  仅 1.3KB（最大课题），与 writer 侧拦截各有时序职责，token 成本可
  忽略——保留分层设计，不与质量门工作（并行会话）冲突。

- 验证：四层全绿 `--module` 1155/1155、`--scenario` 16/16、
  `--persona` 38/38、`--web-ci` 1406/1406；前端 5 个改动 JS 经
  JavaScriptCore 语法验证全过；浏览器快照确认新入口渲染、无 JS
  崩溃；4 个新面板依赖 API 全 200；遗留死文件（learning/projects/
  research.js 共 96 端点）保留待后续迭代决定去留。

## v6.9.57 - 2026-08-27 风险清单收尾：文献来源前置校验 + 次优平台信号 + 状态校准

按全项目评估风险清单逐项处置（P1 泄漏/备份已于 v6.9.56 修复）：

- **lifecycle 状态校准（P3）**：`rebuild_lifecycle.py` 非 dry-run 执行，
  6 个课题的 round/score 状态漂移归零（如 qg r1/0.77→r2/0.81、
  attosecond r7→r8），执行前自动备份至 `backups/_lifecycle.json.*`。
- **蒸馏积压（P2）确认已被覆盖**：v6.9.38 已将 cron 改为 `--auto`
  自适应档位（>300 → 20 篇/天追赶档），当前积压 354 触发追赶档，
  今日 12:50 起执行；AGENTS.md 的"5 篇/天"过时描述同步更正。
- **references 来源前置校验（P3，防文献幻觉）**：`_references_preflight`
  新增第 ④ 段——参考文献条目的 DOI/arXiv ID 与可信池比对（池 =
  02_literature 全部轮次检索产物 + 知识库 wiki/papers frontmatter，
  头部 2KB 限读控 IO）。未命中条目列入"优先核查清单"附入 critic
  prompt（R7 实测：writer 凭记忆虚构 6 条元数据被 CrossRef 下游
  打回致评分暴跌——防线前移到评审输入）；无标识符条目单独归类
  提示补齐。attosecond 实测：27 条中 23 条未命中/1 条无 ID，即该
  课题 references 的元数据可信度当前约 11%，为 critic 聚焦核查
  提供了量化依据。
- **次优平台检测（P2，分数天花板死代码激活）**：数据实证收敛线
  0.85 与程序化天花板体系结构性冲突——AI 写作检测 ceiling<0.9 档
  把综合分 cap 在 0.85、锚点"差距明显"档 cap 在 0.84，全量 32 轮
  分数样本 max 0.81（≥0.85 零次），收敛分支零触发。处置：① 代码
  注记固化结构性不可达证据；② 新增 0.80-0.85 连续平台检测——
  不自动晋级（晋级语义不变），置 quality_warning 建议人工评估
  （与"人工验收为主"定位一致，把死代码转为有效人工信号）。
- **critic 超时率（P1）测量**：v6.9.53-55 治理上线后最近 6h 窗口
  critic 4/7（样本小），失败仍全部为 900s/600s 硬超时——留 24h
  观察窗口验证，避免与质量门工作（并行会话）重复干预。
- **kb_sync 写穿加固**：module 模式（多套件顺序）实测仍写穿真实
  knowledge/——ORDERED_FULL 标记扩大到所有 self_test 多套件模式
  （kb_sync/optimize 端到端仅单跑完整执行）。

- 测试：ReferencesPreflightTests +2（来源校验命中/未命中/无 ID/
  池空跳过）；QualityCeilingConvergenceTests +2（次优平台标记/
  爬升通道不误伤）。
- 验证：四层全绿 `--module` 1155/1155、`--scenario` 16/16、
  `--persona` 38/38、`--web-ci` 1406/1406；真实 knowledge/ 零写穿；
  零进程泄漏；cron 对账 0 问题。

## v6.9.56 - 2026-08-27 测试进程泄漏修复 + 备份链路补全（P1 双修）

背景：全项目评估发现两个 P1 工程缺陷——① `--web-ci` 每次运行泄漏
1 个 web_server 孤儿进程（7 月底以来累计 57 个）；② 备份断档 18 天
（最后备份 08-09，无定期 cron，与"备份优先"原则冲突）。

**修复①（进程泄漏，三层根因）**：

- **根因链**：`/api/heartbeat` 的学习机会检测内含 arXiv/Wikipedia
  同步外呼（实测 52s）→ ApiClient 15s 超时抛 `socket.timeout` 炸穿
  run_tests → self_test 全量分支的复制调度 `except Exception: pass`
  静默吞掉 → teardown 被跳过（进程泄漏）+ 崩溃套件从报告蒸发
  （**WebApiSuite 的 44 个断言长期从未被计数，"全量通过"是假绿**）。
- **调度层**：`test_runner.execute_suite()` 公共函数——teardown 放
  finally、崩溃套件计入报告并追加"套件完整执行"失败结果；self_test
  复制调度改为复用（消除双份漂移）；套件发现加 `__module__` 过滤
  （from-import 的套件类此前被重复执行）；套件间模块卫生（弹出
  proposal_lifecycle/lifecycle 系，阻止旧根绑定跨套件泄漏）。
- **客户端层**：ApiClient 捕获 socket.timeout/URLError 返回 code=0
  （断言失败不炸套件）；timeout 15→30s；Popen start_new_session +
  进程组 SIGTERM→SIGKILL 回收；setup/teardown 孤儿自愈清扫
  （按 `--root linsai_test_*` 匹配，正式实例无 --root 不误伤）——
  **57 个存量泄漏进程已全部清零，后续每次运行自动自愈**。
- **服务端层**：学习机会检测加 6h TTL 缓存 + daemon 线程 15s 超时
  护栏（超时写 10 分钟降级缓存，heartbeat 不再被外网拖死）；测试
  隔离环境关闭 auto_enabled（CI 不依赖外网）。

**修复②（备份链路）**：`backup_manager` 新增 `prune_backups(keep=7)`
轮转（仅顶层 zip，keep<=0 防误配清空）与 `daily_backup()` 幂等入口
（24h 内跳过 + 轮转）；注册 hermes cron `lc-daily-backup`（每日
03:17，`--daily` 模式），`cron_manifest` 清单同步为 9 固定项（monitor
对账自动覆盖）；**立即补跑一次备份（837MB/2358 文件）填 18 天断档**。

**附带显形修复（静默吞异常揭露的历史崩溃套件）**：

- `proposal_sections.assemble_draft` **幽灵写入防护落地**（v6.8.10
  时代防护从未实现）：拼接 <500B 且将覆盖显著更大已有草稿时抛
  ValueError（initialization 传 allow_shrink=True 豁免重置语义；
  optimize 的 writer 重组路径已有 try/except 优雅处理）；
  test_ghost_write_guard 修复 import 方式/传参错位/cron 样本补全。
- test_idea_review **补写 run_tests**（12 个 _test_* 方法写完未接
  调度，从未运行）+ 浮点容差 + teardown 模块还原。
- patch_module_root **可重入化**（注册表还原原始值，修复二次 patch
  对已隔离路径替换失效）。
- 两个顺序敏感套件（test_proposal_kb_sync 全量跳过、
  test_optimize_v6817 跳过端到端方法）：全量顺序下 KB 写入链/
  feedback_archive 的 from-import 值绑定绕过 patch（曾把测试课题
  写穿真实 knowledge/，已清理），单跑 11/11 正常，待写入链改造为
  显式传参后恢复全量。

- 测试：新增 `test_leak_guard.py` 19 断言（execute_suite 三态保护/
  孤儿识别纯函数/网络容错/prune 语义/缓存 TTL）；backup_manager
  self-check 扩展 prune 用例。
- 验证：四层全绿 `--module` 1146/1146、`--scenario` 16/16、
  `--persona` 38/38、`--web-ci` 1398/1398（基线 1237→1398：+44
  WebApiSuite 蒸发断言回归计数 + 新增守卫）；零进程泄漏；真实
  knowledge/ 无写穿。

## v6.9.55 - 2026-08-27 质量核心重构：字数门升级为质量门（冗余/无关为病因，字数为症状）

背景：用户校准设计理念——"章节字数不是死板的限制，关键在于质量；
过于冗余/掺杂无关内容本身就是影响质量的因素"。v6.9.54 的预算门把
字数当判据存在概念错误：论证密集的 8500 字章节是优质品，充满重复的
5500 字章节才是劣质品——字数门误伤前者、放过后者。字数是症状，
冗余/无关才是病因。

重构（budget_gate → quality_gate）：

- **程序化拦截（字面确凿，零误伤）**：
  ① 跨章节归一化完全相同句 ≥1 处，或高相似句（中文 2-gram + 英文词
  containment > 0.85，长度分桶控复杂度）≥2 处——直接对应 NSFC 评审
  红线"无跨章节内容重复"；
  ② 章节内任一句重复 ≥3 次或 ≥3 组句子各自重复（成片复制信号）。
- **语义判断交还 LLM**：无关内容检测（段落级核心术语命中）是启发式，
  真实数据实测误伤严重（attosecond 40 段核心论证被误标——中文密集
  段落与英文术语表天然低重叠）。降级为线索注入 critic/writer prompt
  （"相关性复核线索"，附具体段落位置），由 LLM 语义裁决；核心术语
  提取自 research_idea + proposal_id（空集时跳过检测，fail-safe）。
- **字数降级为上下文**：超参考体量不独立拦截——冗余/无关零命中的
  超限章节按"实质性长文"放行（reason 明示"密度合格，字数不作为
  扣分项"）；有冗余命中时字数并入放大理由。standards 措辞同步从
  "预算"改为"参考体量（字数非门限）"；writer 纪律段重写为
  "内容质量纪律"（质量以密度论，不以字数论）。
- **质量指令（quality_directives_text）**：writer/critic 收到的指令
  从"净删 N 字"改为具体缺陷位置——重复句原文 + 所在章节 + 处置方式
  （保留一份/改写为指代式引用），无关段附"程序初筛存在误报，请逐段
  语义裁决"。critic full_review 分支同步注入跨章节冗余初筛线索。

真实数据实测（7 个 optimizing 课题）：全部检出真实跨章节重复句
（1-20 处/课题），如 berry 的"平台二的 MnPS₃/WS₂ 异质结三元耦合体系"
句在 content/ rationale 双章节原样重复——正是 writer 逐轮追加响应
累积的复制冗余；全部课题三章节被正确拦截，质量指令直接命中缺陷位置。

- 测试：SectionHygieneTests 43 断言（12.1-12.8：实质性长文放行/
  跨章节重复拦截/章节内成片复制拦截/无关不拦截但产线索/干净章节
  通过/门卫零存活/executor 源码守卫含"字数门不得残留"/optimize
  质量指令守卫）。
- 验证：163/163；self_test --module 1157/1157 全绿。

## v6.9.54 - 2026-08-27 写入门卫 + 预算门：结构不变量从"prompt 约定"升级为"确定性强制"

背景：用户提出"从根源上杜绝，而不是修修补补"。回溯 v6.9.28 以来的
全部修复（锚点绑定/超时治理/AI 天花板公平性/章节卫生），反复出现的
问题共享同一架构缺陷——**结构不变量（文件纯净性/章节体量/语义定位）
只靠 prompt 红线约定，写入边界完全信任 agent 输出**。违规内容进入
数据域后跨轮存续，只能靠 critic 事后发现或人工一次性清洗补救，于是
同类问题反复复发（references §D-F 污染 → full_review 变审计日志 →
章节无上限膨胀，三代同构问题）。

根治：不变量的执行点从"LLM 自觉 + 事后评审"前移到"写入边界 + 通过
判定"，全部确定性代码，零 LLM 参与：

- **写入门卫（guard_written_artifacts）**：executor 在 writer 落盘后、
  job 判定继续之前运行——references 工作日志段落当场剥离迁 05_review/，
  full_review 核查记录当场迁出并重生骨架。污染在数据域的存活时间为
  零，从此不再依赖下一轮评审发现；v6.9.53 的 apply_all 退化为历史
  存量工具。守卫自身异常 fail-open（记录日志不阻塞主管线）。
- **预算门（budget_gate）**：写入前记录聚焦章节中文字数基线，写入后
  判定——通过条件为"预算内"或"本轮净删 ≥10%"（超限章节渐进压缩，
  收敛速率保证单调收敛不死锁：至多 log₁.₁(N/max) 轮）。未收敛则
  section_passed=False，膨胀章节无法"通过"、无法晋级 pending_review。
  判定结果（budget_gate_passed/reason）入 score_history 可观测。
- **无预算章节**（references）恒通过；新建即超限（无基线）拦截；
  预算门异常 fail-open。

- 接入点：executor._run_writer_step——before_chars 基线捕获 →
  writer 成功 → guard_written_artifacts → budget_gate →
  section_passed 纳入 budget_ok。
- 测试：SectionHygieneTests 扩展至 33 断言（12.1-12.4：预算门四象限
  判定/新建超限拦截/门卫当场修复零存活/文献无损/executor 源码守卫）。
- 验证：138/138 → 152/152；self_test --module 1146/1146 全绿。

## v6.9.53 - 2026-08-27 章节卫生治理：full_review 骨架化 + references 存量清洗 + 章节字数预算

背景：分章节评审只限制了"单次评审读哪些章节"，没有限制章节本身的
体量。08-27 超时率回升至 44%（11/25，全部空输出+恰好触顶型），排查
确认三类性质不同的膨胀叠加（章节 22-48KB + critic 报告 22-42KB +
standards 36KB = 60-90KB prompt × API 慢速 = 超时）：

1. full_review.md 定位错位——writer 把"一致性核查记录"（round-N 修复
   确认表、逐项对照）当正文写入章节文件（qg 33KB / moire 25KB /
   order-param 23KB / kt 14KB）。真实 NSFC 申请书没有"整体一致性
   审查"章节，该文件是派生索引；且 full_review critic 的评审输入包含
   它自身，形成"记录越写越大→评审越来越慢"的正反馈。
2. references.md 存量污染回归——moire 28KB 内含 [CITE:xxx] 独立映射
   表（v6.9.46 红线之前的存量，writer 后续轮次聚焦别的章节无人清理）。
3. 正文章节无长度预算——writer 逐条响应 critic 问题只追加不删减，
   kt-rationale 11364 字 / qg-scheme 10900 字 / qg-content 10412 字，
   远超 NSFC 各章节正常体量（增量累积无上限）。

修复（三层）：

- **P0 full_review.md 语义重定义**：新增 `section_hygiene.py` 模块。
  一次性清洗（已执行）：4 个课题的核查记录迁至
  `05_review/full-review-record-{date}.md`，原位重生"全文逻辑骨架"
  （标题索引 + 衔接点 + 口径表，≤3000 字，25-33KB→1-2KB）。运行时
  防线：full_review critic 输入同时排除 references.md 与 full_review.md
  自身（骨架纯净性由程序化预检把关）；writer prompt 增加 full_review
  写法指令（三部分/≤3000 字/过程性材料只进 05_review）；纯净性红线
  扩展覆盖 full_review.md。
- **P0 references.md 存量清洗**：`strip_references_worklog()` 按标题
  特征（映射表/核实声明/闭环/§D-F）与 CITE 表格行剥离工作日志段落，
  文献条目与条目内挂钩注释完整保留（moire 已执行，34 条无损）。
  order-param 的 28KB 为分类文献列表（8 类 42 条带注释），非污染，
  检测正确未误伤。
- **P1 章节字数预算**：SECTION_BUDGETS（rationale 5000-8000 /
  content 4000-7000 / scheme 6000-10000 中文字）写入 standards 的
  section_standards；critic 附程序化预算预检（超限按 critical"压缩
  重写"处置）；writer 附量化指令（"当前 N 字，净删 ≥M 字"）+ 字数
  纪律（超限章节禁追加响应，改写优先于新增，细节下沉方法学手册）。

- 测试：`test_mechanism_hardening.py` 新增 SectionHygieneTests
  19 断言（预算判定/量化指令/迁移幂等/骨架纯净/条目无损/源码守卫/
  standards 守卫）；v6.9.46 旧守卫同步更新为成员检查写法（语义不放松）。
- 验证：`--module` 138/138 → 1132/1132 全绿；清洗后 4 课题 sections
  总量 447KB→435KB，full_review 输入规模立减 22-32KB/次。

## v6.9.52 - 2026-08-27 lark-cli 路径版本自适应：修复插件升级后飞书告警通道静默失效

背景：04h 健康检查发现 monitor 连续数十次报"lark-cli 不存在：
`~/.trae-cn/plugins/trae-remote-official/lark/1.0.3/bin/lark-cli`，跳过飞书通知"。
根因：`lifecycle_monitor.py` 用 `Path.home()/.../lark/1.0.3/bin/lark-cli`
硬编码插件版本目录，而 TRAE lark 插件已升级到 1.0.4（新路径在 PATH 中）。
插件升级后固定路径指向不存在的二进制 → `_send_feishu` 每次返回 False →
monitor 检测到异常但全部静默旁路，告警防线数据出口完全失效。

修复：`LARK_CLI` 改为运行时解析——扫 `~/.trae-cn/plugins/trae-remote-official/lark/*/`
取最高已安装版本目录下的 `bin/lark-cli`，路径不存在则回退 `shutil.which`；
无任何可用实现在时返回空串（`_send_feishu` 既有 empty 检查兜底）。不再绑定
固定版本号，后续插件升级自动适配最高版本。

- 行为变化：飞书告警通道在插件升级（1.0.3→1.0.4，实测解析到 1.0.4 且 exists）
  后恢复可用。
- 测试：`test_monitor_lark_failure.py` 新增"插件升级后解析最高已安装版本"
  断言（当前 7/7 通过）。
- 验证：`self_test --module` 全量通过（见本轮回归基线）。

## v6.9.51 - 2026-08-26 每完成一轮强制切换：修复单课题无限持有焦点饿死队列

背景：08-25/26 实证 attosecond 连续 2 天持焦点（r3→r6 一天 4 轮），
饿死 qg/kt/moire/order-param/berry 5 课题（healthcheck 标记 stalled ×5）。
根因：`_focus_proposal_for_slot` 的让出判定只看"进行中轮次
（completed_rounds+1）是否完成"——课题完成一轮后立即创建下一轮 job，
`_is_round_complete` 对下一轮恒返回 False，导致永远判定"未完成"、
焦点被单课题无限持有。slot_done 标记本应兜底，但仅覆盖"轮次中途完成"
场景，未覆盖"整轮完成后继续开下一轮"场景。

修复：新增 `_last_round_seen` 快照（`lifecycle-focus.json`），记录各
课题上次被检查时的 `optimization_rounds`。时段切换时若发现轮次增加
（上一时段完成了一轮）→ 强制让出焦点，切换到队列下一个课题；未完成
新轮次则回退到原有"进行中轮次完成"判定。首次聚焦课题自动记录基线，
无基线时不误切。

- 行为变化：每课题每完成一轮即让出，队列内课题均衡轮转，不再出现
  单课题连续多轮独占焦点。
- 测试：`test_micro_scheduler_rotation.py` 新增 11a-11d 共 5 断言
  （完成一轮强制让出 / rounds 未变继续聚焦 / 首次聚焦记基线 /
  让出后新课题快照初始化）。
- 验证：28/28 通过；`self_test --module` 1113/1113 全绿。

## v6.9.50 - 2026-08-25 AI 白名单长词优先替换：消除短词遮蔽长词导致的计数泄漏

背景：v6.9.48 引入的 `AI_TERM_WHITELIST` 中"同时电离"（4 字）排在
"同时或近同时电离"（8 字）之前，逐词 `str.replace` 时短词先命中并把
长词截成"同时或近同时电离"→"□□□□或近同时电离"，残余部分中的
"同时"脱离白名单保护，每出现一次泄漏 1 次冗余计数——08-24 20h 健康
检查已标记低优先级，00h 复核确认属于确定性缺陷（触发场景：正文本就
写着"同时或近同时电离"，writer 按此措辞修复反而被多扣分）。

修复：计数前对白名单按词长降序排序
（`sorted(..., key=len, reverse=True)`），长词先替换为等长占位符，
短词不再截断长词。对白名单未来新增任何重叠词条同样稳健。

- 测试：`test_mechanism_hardening.py` 新增 10.2b 长词遮蔽回归
  （"一个以上电子被同时或近同时电离。"修复前泄漏 1 次"同时"，
  修复后 0 泄漏）。
- 验证：泄漏 1→0；`self_test --module` 1106/1106 全绿。

## v6.9.49 - 2026-08-25 should_auto_unlock 死角修复：修复系统放弃后单次失败即永久卡死

背景：00h 健康检查发现 order-param r7-references-critic 陷入
attempts=1 / repair_attempts=3 死角态，三条恢复路径全部失效：

- `run_repair` 拒绝：repair_attempts >= 3（修复系统已放弃）；
- 依赖链重试被跳过：`_is_proposal_stuck` 以 `attempts >= 3 or
  repair_attempts >= 3` 判 stuck，ready 列表构建时整课题被 skip；
- `should_auto_unlock` 拒绝：旧逻辑要求 attempts 与 repair_attempts
  **同时**达上限。

死角成因（系统性）：repair 对 failed job 的重置语义是 attempts→0 +
repair_attempts+1（utils 备忘 #27）。当 repair_attempts 从 2→3 时
attempts 被清零，此后该 job 只要再失败一次即落入 attempts=1 /
repair_attempts=3 死角——不是偶发，是每个走到修复上限的 job 的
必经状态。实证：berry r2-scheme-critic 若下次重跑失败也将同样卡死。

修复：`should_auto_unlock` 移除 `attempts >= MAX_JOB_ATTEMPTS` 门槛，
仅保留 `repair_attempts >= MAX_JOB_ATTEMPTS`（修复系统放弃即充分），
维持 24h 冷却与终生 1 次两道护栏。次品 job 仍会被双上限拦住
（repair 不再重置、依赖链重试被 stuck skip），不会无限重跑。

- 测试：`test_alert_circuits.py` AutoUnlockPolicyTests 用例 5 期望
  翻转（死角态 → 解锁），新增 5b 两子用例（死角态冷却期拒绝、
  死角态终生次数耗尽拒绝）。
- 验证：unlock 套件 10/10；`self_test --module` 1106/1106 全绿。

## v6.9.48 - 2026-08-24 AI 天花板公平性修复：白名单/千字归一/raw 复检/章节归因

背景：attosecond 课题 AI 天花板连续 5 轮卡死 0.50，writer 每轮被
复检判"未实质修复表达问题"。逐项核查 13992 字真实文本发现四层叠加
缺陷——修复指令物理上不可执行，writer 被系统性误判。

- 缺陷①领域术语误伤（最重）：`_detect_ai_patterns` 裸词计数把
  '关键科学问题'×5（NSFC 法定章节名）、'系统误差'（物理术语）、
  '有效性'（=validity，技术必需）、'同时电离'（simultaneous
  ionization，物理概念）等不可删词全算冗余——writer 无法在不破坏
  科学含义与模板合规的前提下修复。修复：新增 `AI_TERM_WHITELIST`
  （9 项复合词），计数前替换为占位符，只统计真实冗余用法。
- 缺陷②绝对阈值不随篇幅归一：阈值 12 次对 14K 字长文意味着
  0.86 次/千字，中文科研写作正常密度 2-4 次/千字，达标不可能。
  修复：冗余修饰词阈值 `max(12, 2.0/千字)`、死板关联词
  `max(8, 1.0/千字)`、超长句免赔额 `2+0.15/千字`——短文本仍严格。
- 缺陷③floor 掩埋真实进步：复检比较 floor(0.5) 后的值，惩罚从
  0.6 实质降到 0.5 仍显示 0.50→0.50（5 连误判根因）。修复：返回
  `raw_ceiling`（floor 前原始值），复检与日志均用 raw 比较。
- 缺陷④复检口径与修改范围错配：writer 每轮只修聚焦章节，复检却用
  三章节合并口径，单章节完美修复被其余两章稀释。修复：正文章节 job
  writer 前建立 `section_baseline`，复检以聚焦章节自身 raw 变化为准
  （full_review/references 维持全局/跳过口径）。
- writer prompt 量化清单：逐词列出"当前 N 次 → 削减至 ≤M 次"，
  并明确告知白名单术语无需修改——修复指令从不可执行变为可量化达成。
- 实测（8 个 optimizing 课题全量）：attosecond 0.50→0.94（白名单
  +归一化后仅剩 3 处真实超长句）；berry raw=0.43、quantum-geometry
  raw=-0.54 等仍有大量真实超长句/自引用问题（该扣的照扣，检测未废）。
- 测试：`test_mechanism_hardening.py` 新增 AICeilingFairnessTests
  （20 断言：白名单四类术语剔除、13K 长文正常密度不扣、2K 短文高
  密度照扣、raw_ceiling 保留、章节级检测隔离、长句免赔额、executor
  raw 比较与 section_baseline 源码守卫、writer 量化清单守卫）。
- 验证：`self_test --module` 1103/1103 全绿。

## v6.9.47 - 2026-08-24 DOI 塞进 arxiv_id 字段归一化：修复文献入库 ENOENT

背景：12 时段例行健康检查发现 attosecond r2 课题 lit_search 解析出
10 篇论文（全部中文/国际期刊，含 DOI 无 arXiv ID），入库失败 8 篇。

- 根因：researcher agent 对无 arXiv 预印本的期刊论文常把 DOI 直接
  塞进 `arxiv_id` 字段（如 `10.1088/1674-1056/ae3474`）。该形态
  绕过 arXiv 校验（`_extract_arxiv_id` 兜底原样返回）与 DOI 清洗，
  `identifier` 保留 `/` 使 `raw/papers/{identifier}.md` 的
  `write_text` 抛 `[Errno 2]`——实测 10 篇丢 8 篇（failed=8）。
- 修复：`_ingest_new_papers` 在 identifier 决策前归一化——非
  arXiv 形态（`NNNN.NNNNN(vN)` / 旧式 7-8 位数字）且匹配 DOI 模式
  （`10.\d{4,9}/...`）时移入 `doi_clean`，走既有 doi-{slug} 清洗
  路径（点/斜杠转连字符）。
- 测试：`test_literature_service.py` 新增
  `_test_ingest_doi_stuffed_in_arxiv_id_field`（套件 41→42）：
  断言 ingested=1 / failed=0 / 产物文件名
  `*doi-10-1088-1674-1056-ae3474*.md` / 正文含原始 DOI。
- 验证：`py_compile` 通过；`self_test --module` 1083/1083 全绿。
- 已知缺口（仅报告待人工裁决，不在本次修复范围）：lit_read/
  lit_note 对 DOI 论文无处理路径（`executor.py` 仅 arXiv 正则，
  `link_to_proposal` 以 wiki/papers/{arxiv_id}.md 为键），DOI 论文
  入库后两步骤无法消费。

## v6.9.46 - 2026-08-24 超时任务全景排查：full_review/writer 同构问题批量修复

背景：用户要求排查易超时任务是否与 references 评审同构。两样本统计
（活跃 error_history 17 次 + 归档 20 次 = 37 次）：critic 系列 14 次
（content 5、references 6 已修、full_review 4、rationale/scheme 各 3）、
writer 系列 10 次（full_review 4、references 2）、lit_read 2 次。确认
full_review/critic 与 writer 存在与 references 完全同构的三类问题。

- full_review/critic 输入超载：旧版读全部 5 章节（实测最大 ~180KB：
  48+46+47+33+39KB）+ standards 36KB。修复：① 排除 references.md——
  39KB 纯文献列表与"逻辑衔接/术语一致性/冗余矛盾"审查无关，输入立减
  ~40KB；② 新增 `_cross_section_metrics_preflight()`——"指标红线 P0：
  同一指标跨章节一致"的数字比对程序化完成（12 类物理量纲正则提取，
  按数值+单位聚类，标出跨章节数值集差异），预检表附入 prompt。
- 实测预检（真实数据）：attosecond 课题立即检出 content `285 eV` vs
  scheme `284 eV` 数值矛盾——正是指标红线要抓的目标；bsv 检出 5 项
  差异指标（fs/nm/μm/%/eV）。
- writer 输入与目标对齐：旧版无条件列出全部 5 章节文件供"可读"，但
  章节级修订指令又说"只修改聚焦章节"。修复：focus_section 存在且无
  跨章节 P0 时只列聚焦章节（references.md 全场景排除——引用修订走
  专轮）；跨章节修复场景保留多章节列表。
- writer 文件纯净性红线（references.md 污染源头治理）：prompt 明确
  禁止向章节文件写入工作过程记录（核校日志/闭环证据/修复声明），
  要求过程性内容写 05_review/，既有 §D-F 污染内容下轮修订时迁移。
- lit_read（2 次）属必要长任务（读多篇文献全文），不动。
- 测试：`test_mechanism_hardening.py` 新增 MetricsPreflightTests
  （10 断言：一致/差异指标识别、不误报、references 排除守卫、writer
  对齐守卫、纯净性红线守卫）。
- 验证：`self_test --module` 1079/1079 全绿。

## v6.9.45 - 2026-08-24 references 评审任务重排（程序化预检）+ 交变磁体设想人工改写

背景：references critic 连续超时卡死 bsv/order-param 两个临门课题。诊断
发现任务安排三处结构性缺陷：① 输入超载——critic 被要求读 references.md
（40KB，其中 60% 是 writer 每轮追加的核校工作日志 §D-F）+ 三个正文章节
（62KB）≈ 106KB，超时上限怎么调都跑不完；② 程序化任务交给 LLM——"编号
一致性"（正文 [N] ↔ 列表编号比对）正则可完成，却让 critic 通读全文；
③ 核校日志污染文献文件——35 条文献本应 8-11KB 被撑到 40KB。

- `proposal_lifecycle/optimize.py`：
  - 新增 `_references_preflight()`：程序化预检（零 LLM）——正文引用
    标记全集（排除 [critical] 类英文标签）× 列表编号全集（兼容
    `**[N]**` 粗体与行首两种体例）→ 缺失/未引用/连续性/数量对标 +
    膨胀告警（>25KB 提示工作日志迁 05_review）。
  - references 分支 prompt 重构：只读 references.md + 预检表（输入
    106KB → ~45KB），编号一致性声明"已由程序完成"，critic 聚焦
    格式规范/时效性/相关性判断；删除正文文件列表构建。
- 实测预检（真实数据）：bsv 秒级输出"33 引用 vs 35 条、[27,28] 未引用"；
  order-param 额外发现编号缺口 [4,6,8,...] 与 42 篇超区间——这些正是
  旧超时路径要查的全部内容。
- 交变磁体课题（general-new-idea-20260822）设想人工改写（v2）：按三份
  idea_review 意见逐条修正——① 材料体系 MnPS₃/FePS₃/CrI₃（均非交变
  磁体）→ MnTe（d 波自旋劈裂获 ARPES 证实）+ CrSb/RuO₂ 对照；② 删除
  v1 全部不可考引文（Crossref 零命中），重建 DOI 可查文献；③ "首次"
  降级并与 MnTe 既有 HHG 工作显式对账；④ 修正量纲错误（温度灵敏度
  → 时间分辨 ≤100 fs）；⑤ 补量级论证（d 波劈裂 ~0.4 eV 与光子 0.41 eV
  同量级，替代错用的层间交换 1.5 meV）；⑥ 重构内容/路线切分（v1 两节
  逐字重复）；⑦ 三个创新点补可证伪判据（45°/90° 偏振周期二元判据）
  与预设失败出口。idea_review job 已重置重评。
- bsv 卡住的 references-critic 已重置（新 prompt 下重跑）。
- 测试：`test_mechanism_hardening.py` 新增 ReferencesPreflightTests
  （11 断言：粗体/行首双体例、缺失/未引用识别、英文标签排除、膨胀
  告警、数量对标、prompt 源码守卫——不再构建正文列表）。
- 验证：`self_test --module` 1069/1069 全绿。

## v6.9.44 - 2026-08-24 修复扫描周末误判（UTC→北京时间，周一凌晨自愈延迟根因）

背景：08h 健康检查发现 4 个 attempts=3 failed job（moire/order-param/
bsv 的 critic 900s 超时 + new-idea idea_review 600s 超时）在周一
06:03 BJ lc-repair 后零重试。根因：`_is_weekend()`
（scripts/lifecycle/utils.py）用 UTC weekday 判定周末，与业务时区
北京时间偏差 8 小时——BJ 周一 00:00-08:00（UTC 仍处周日）被误判
为周末，`run_repair` 走 `_run_weekend_repair` 分支，完全跳过工作日
failed job 重试与 stale 清理；而微调度器 cron（`*/5 * * * 1-5`，
本地求值）同一时刻已在正常派活，两套口径分裂。反向 BJ 周六
00:00-08:00（UTC 周五）被误判为工作日，周末阶段补跑窗口错失。

- 修复：`_is_weekend()` 锚定显式 `BUSINESS_TZ`（Asia/Shanghai，
  UTC+8）求 weekday；新增可选 `now` 参数供测试注入带时区固定时钟，
  任意时区 aware 表达先归一北京时间再判定，宿主机时区漂移不影响
  业务语义。与 `_weekend_stage_catchup` 的本地时间口径对齐。
- 新增回归：`scripts/tests/test_weekend_local_timezone.py`（11 项
  断言，覆盖事故时刻 00:00:59/06:03:24、周六反向窗口、边界
  07:59:59、双时区表达一致性），已注册 `self_test.py --module`
  硬编码清单（规避未注册套件被静默跳过的坑）。
- 验证：`--module` 1058/1058 全绿（基线 1047 + 新增 11）；修复后
  当前时刻（周一 08:1x）判定 False 正确；4 个 failed job 由
  12:00 repair 自然重试（UTC 04:00 周一，新旧口径均工作日）。
- 关联观察（未修复，仅报告）：`weekend_orchestrator.py` L180
  `run_weekly_mode` 同用 UTC weekday，但其入口 cron（周六 09:00/
  14:00、周日 09:00 BJ）触发时刻 UTC 与 BJ 同日，cron 路径不可达
  误判窗口，仅手动 CLI 在 BJ 周末凌晨调用会误判，低风险。

## v6.9.43 - 2026-08-24 04h 健康检查（第七轮设计抽查 #1-#3，无缺陷无修复）

- 运行时：周一调度恢复正常（08-24 为周一非周日，经 weekend cron
  last_run 交叉验证；微调度器 #0/#1 时段正常轮转，moire 卡住按设计
  跳过切 order-parameter）；cron 17/17；回归 1047/1047 全绿；
  看板自愈 6→8 兑现。
- 设计抽查：#1 范例注入正常（02:15 moire←order-param 注入实证）；
  #2 维度轮换维持潜在死代码（moire rationale deltas[-0.028,-0.04]
  超阈再证不可达，待人工裁决）；#3 idea_review 正常（03:05
  order-param r7 required 回补建链 0.78 通过，退回重触发首次闭环）。
- 观察项：moire r5-content-critic 2×900s 超时 attempts=3 failed，
  06:00 repair 自愈在位；writer.score=36.3 结算闭环验证正常
  （44.3−8.0 精确吻合 moire r4 delta）。
- 随附提交周一 00:07 后调度器产物（moire 轮 5 章节/评审文件、
  order-param idea-review-r7、wiki 同步时间戳）与 pointer 更新。

## v6.9.42 - 2026-08-23 审核反馈注入零信息修复（兜底文本回退结构化意见）

背景：20h 健康检查第三层 #10 抽查发现 bsv 课题反馈闭环实际失效——
`human_feedback_count=3` 指向的 `feedback-3-raw.md` 仅 155 字节通用兜底
话术（Web 审核路由 reason 为空时写入），实质意见全在 8.6KB 的
`feedback-3-structured.json` 中，但注入器只读 raw 文件——critic/writer
prompt 收到零信息。与 v6.9.41 对比报告"bsv 审核意见注入未产生边际效果
（0.86→0.86）"互证：不是注入无效果，而是从未注入过实质内容。其余 4 个
有反馈课题（moire/key-transient/qg/order-parameter）raw 文件恰含完整
意见文本，故仅 bsv 受影响。

- `proposal_lifecycle/feedback_archive.py`：
  - 新增 `_is_contentless_feedback`：识别提取后正文是否为空/仅通用兜底
    话术（精确匹配"用户审核不通过，请根据审核意见修改。"，允许前后
    ≤10 字符冗余；不做短文本一刀切，简短实质意见不受影响）。
  - 新增 `_render_structured_feedback`：将 `feedback-{N}-structured.json`
    渲染为可注入意见文本（结论 + 总体评价 + 最多 8 条 issue 的
    严重度/章节/描述/指令）。
  - `load_review_feedback_for_optimization`：raw 为无信息兜底且同编号
    structured 存在时改注入结构化渲染；raw 有实质内容时行为不变；
    raw 缺失或无 structured 时维持旧行为（空串/兜底注入）。
- 实测：bsv 注入块 155B→2391 字符（7 条带严重度/章节/指令的实质
  issue）；其余 4 课题注入内容与此前完全一致（raw 正文路径）。
- 测试：`test_feedback_injection.py` 新增 3 场景 7 断言（兜底 raw +
  structured → 结构化渲染 / 实质 raw 优先不被抢位 / 兜底 raw 无
  structured → 维持旧行为）。
- 验证：`self_test --module` 1047/1047 全绿（+7）。


## v6.9.41 - 2026-08-23 score_history 遍次隔离 + 退回对比报告（全路径学习 P0/P1）

背景：审核退回清零 rounds/job 但从不清理 score_history，多遍数据混叠在
同一数组（08-23 实测 5 个课题混叠）。迁移后真相：课题实为第 3-5 遍重跑
（非"第一轮卡 27 天"），四课题均触顶 0.84-0.86 被人工否决，且多课题
第 2/3 遍天花板完全相同（bsv 0.86→0.86、quantum-geometry 0.86→0.86）
——审核意见注入未产生边际效果。任何轨迹分析、毕业报告、跨课题学习
此前均建立在污染数据上。

- `proposal_lifecycle/pass_history.py`（新模块）：
  - `archive_pass_history`：退回时把 score_history 归档到
    `score_history_archive`（[{pass, returned_at, reason, entries}]，
    FIFO 保留 10 遍），当前清空，`pass_number` 推进。
  - `generate_return_comparison`：退回对比报告（本遍 vs 上遍）——分数
    轨迹、天花板移动、模块对抗通过变化、弱维度卡点（是否响应）、综合
    诊断（"天花板未动+通过无增长+卡点未变 → 反馈注入未产生边际效果"
    直接指向 writer 执行力或门槛拦截问题）。
  - `migrate_overlaid_history`：存量迁移——按 transition_history 的退回
    时间戳把混叠条目切分成遍（幂等）。
- `transitions.py`：退回分支接线归档 + 对比报告（异常不阻断退回）。
- 存量迁移已执行：5 个课题切出 2-4 个历史遍，pass_number 补齐（备份
  `/tmp/_lifecycle_backup_v6.9.41.json`）。
- 附带修复：遍次隔离消除了跨遍分数比较污染——旧数据下第二遍 r1 的
  分数会与第一遍 r8 比较，"连续下降→暂停"判定曾被跨遍噪声误触发。
- 测试：`test_pass_history.py` 21 断言（归档隔离/对比报告/迁移切分/
  transitions 集成守卫——归档须在状态落盘前）；注册进 `--module` 清单。
- 验证：`self_test --module` 1040/1040 全绿；真实数据演示报告
  （bsv pass3）输出正确的天花板/通过/卡点三段诊断。
- 后续（P2，defer）：跨课题成功模式提炼等真 approve 样本 ≥3 后接入。

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
