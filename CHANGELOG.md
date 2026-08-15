# 变更记录

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
