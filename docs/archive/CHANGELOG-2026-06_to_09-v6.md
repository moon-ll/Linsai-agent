# 变更记录（历史归档：v6.x 及更早，2026-09-27 从主文件移出）

> 完整历史仍在 git log 中；本文件为 v6.x 时代（2026-06 至 2026-09-26）的工作日志。

## v6.10.55 - 2026-09-26 链路任务形态优化第一批：机械步骤单发化 + lit_read 分诊 + 全链调用计量

- **计量账本 `step_usage.py`（新）**：管线 LLM 调用统一入账，补齐计量盲区
  （usage_tracker 仅覆盖聊天会话，管线侧此前零记录）。JSONL 月分片
  （memory/usage/step-usage-YYYY-MM.jsonl，file_lock 多进程安全，180 天滚动
  清理）；两条通道挂接——`llm_router.call_llm`（包装层计时，含 provider 级
  失败行：429/超时/错误均落账，为配额熔断做数据面）与
  `hermes_memory._run_hermes_agent`（profile + 主模型归因，主模型从
  config.yaml 解析缓存）。token 口径：API usage 优先，缺失按 chars/2 粗估
  并标 `tokens_estimated`。CLI：`--summary [--days N]` / `--tail N` /
  `--self-check`。
- **gap_identify 单发化**：直调快路径前置（输出必须可解析出 gaps JSON 才
  算成功）→ agent loop 兜底（原方案 A 保留，行为不变）；降级标记反转为
  `direct_failed→agent_loop`。解析链收敛为纯函数 `_extract_gaps_json`
  （围栏剥离/花括号配平/引号修复）；顺带修复配平提取的旧早停 bug
  （break 位于首个内层 `}`，嵌套 JSON 场景形同虚设）。
- **update_vision 单发化**：直调 + 程序写盘 + 结构校验（`_valid_brief_text`：
  markdown 标题/frontmatter + ≥200 字符），校验不过回退 writer agent loop；
  `update_method_manual` 保留 agent 形态——读大文件改写属 agent 任务，
  单发会把 40-60KB 压进一次 completion（M3 reasoning token 吃配额的长输出
  陷阱）。lit_note 经核实本就是零 LLM（纯程序化关联），无需改造。
- **lit_read 分诊（零 LLM）**：解析 lit-gap 报告条目（id|标题|tldr），按
  检索关键词命中数排序，深读上限 5→3（`_LIT_READ_CAP`）；报告格式漂移时
  回退原序全量正则（保留旧上限，不因解析失败降低覆盖）。
- **回归**：新增 `test_step_usage_triage` 42 条（账本读写/汇总聚合/gaps
  提取六态/分诊排序/brief 校验/模型归因/包装结构），纳入 `--module` 清单；
  全量 `--module` 1939/1939 通过。
- **入库说明**：executor.py 的单发化/分诊改动因与 v7.0.0 skill 工作流
  共享工作区，已随提交 7b284add 入库（该提交信息未单列）；本提交补入
  计量账本、挂接层、回归测试与文档。

## v7.0.0 - 2026-09-25 skill 架构迭代：项目从 prompt 驱动迁移为 skill 驱动

用户裁决（2026-09-25）：将基于 prompt 运转/优化 prompt 的思路更新为以
skill 为核心（项目内 skill，所有 agent 可用）；人工处理只作兜底，根因
修复沉淀进 skill；核心目标是产出高质量课题。直接触发：研究方案叙事
重构后仍不具可操作性——缺"实验学家常识层"（装置/序列/数据形式/时间
预算），此类质量标准必须进入自动链路而非依赖人工评审兜底。

**架构（三层分工，见 docs/SKILL-ARCHITECTURE.md）**：
- skill 层（单一真相源）：.hermes/skills/<name>/SKILL.md——hermes 项目
  本地 trusted 目录（优先级最高），agent 会话自动进 skills index，零改造
- 数据层：nsfc-standards.json 保留量化参数，skill 引用不搬家
- 代码层：流程编排 + 输出契约 + 运行时数据注入

**新增 5 个管线 skill**（.hermes/skills/）：
- research-proposal：**操作性五问**（拿什么做/测什么/怎么测/多久/怎么从
  数据到结论）+ 方案六要素模板 + 课题设想六模块 + 质量递进链——直接
  响应"方案不具可操作性"反馈，含正反对照样例
- nsfc-writing v2（十节）：收编 optimize.py 三处硬编码真相源
  （critic narrative_rules 29 条 / writer narrative_requirement /
  purity 红线 + 质量纪律）
- literature-reading：三链路同构的结构化阅读法（五维笔记/五要素/深读五字段）
- method-manual：手册维护纪律（唯一真相源/禁追加/判据口径表/参数溯源）
- quality-review：四维锚点评审 + 串通检测 + idea_review 四维门槛

**统一加载器 scripts/skill_loader.py**：节提取/静态绑定/fail-open/缓存/
注入预算 4KB，含 _self_check。

**代码接入（~120 行硬编码知识收敛为 skill 注入）**：
- optimize.py：_load_nsfc_writing_skill_text 重构为 skill_loader 通道
  （writer/critic/purity 三路）；narrative_rules 缩减为评分锚点契约；
  narrative_requirement 缩减为范本指引；_purity_rules+质量纪律 → skill 六/七节
- executor.py：lit_read 五维笔记/idea_review 四维/method_manual 纪律三处接 skill
- hermes_pipeline.py：STAGE_PROMPTS 六阶段追加 skill 引用行（STAGE_SKILLS 映射）
- idea_generator.py：六模块模板 → research-proposal skill 三节
- 旧 skills/nsfc-writing/SKILL.md 改为迁移指针（防会话链路过时内容）

**测试**：test_nsfc_writing_skill.py 升级 v2（十节结构/三路裁剪/fail-open/
挂接防误删/收敛验证/预算）；test_skill_integration + test_mechanism_hardening
适配（字符串断言 → skill 注入调用断言）；全量回归 1897/1897 通过。

遗留（下轮）：weekend_pipeline _llm_json 通道的知识注入改造；nsfc-
standards.json 文字规范条目继续迁出；P2 方案按操作性五问补实体内容
（装置/序列/时算）待执行。

## v6.10.54 - 2026-09-25 知识库四维体检治理（数据面）：双世代重复 514 组清零 + 概念家族归并 + 别名归一链路 + title 污染修复

**接 v6.10.52（代码面，同日）：用户授权"按优先级动手修"体检报告。本批为
数据治理与持续化挂链，全部经官方门面写入，stub 保检索可达。**

- 双世代论文页去重累计 521 对（514+7 churn）全部成功，504 stub，289 页
  引用改写；wiki/papers 存活 1491 篇（治理前 ~2070 live，重复率 54%→0）。
- 概念家族归并 14 对全 LLM 融合成功（CEP门控×4/固体高次谐波×3/相对论
  等离子体镜面×3/CEP sub-1.5-cycle×2/跨类型 hhg+波形控制×2），314 页
  引用改写，"高次谐波产生（HHG）"564 入链分裂终结。
- 枢纽概念页补建 5 页（强场超快/交变磁体/Berry曲率/MnPS3/量子几何反演，
  红链 Top5 目标；量子几何反演正文以课题文档为准，不编造）。
- proposal 镜像页 title 污染修复 10 页（正文片段当标题→proposal id，
  389 条 proposal 引用红链的根源）+ stub 标题全局改写 53 页 106 处。
- 别名表 25→41 规范名：删悬空互指键"高次谐波"，补中英/课题中文/方法
  中文名映射；图谱别名归一救回边 43→522 条。
- 空占位"深度解析"小节清理 629 处；裸 id 页 title 回填真名 119 页；
  has_fulltext 失配修复 26 篇；标签中英归并+#前缀清洗 228 页 330 处；
  .bak/.DS_Store 清入隔离区；Home.md 统计刷新；论文库 MOC 生成
  （1491 篇/38 年份桶，浏览动线补缺）。
- 周日反思 job 挂接确定性去重（merge_paper_generations 前置，零 LLM）
  ——蒸馏管线持续产出新页，不挂链则重复重新积累（手术当日 churn +7 实证）。
- 新增 manual_ops 三件：kb_merge_concept_families（人工审定映射，可
  复跑）/kb_seed_core_concepts（幂等补建）/kb_build_papers_moc（重生成）。

**终态指标**：连通性 1.68(失真)→0.84 真实口径；幽灵边 3848→0；related
红链 47.1%→38.3%（剩余为未来概念/长尾论文标题，图谱侧安全丢弃）；
双世代重复 561→0。**勘误**：初版体检"索引 318 幽灵条目"系误报——
hermes-briefings/hermes-wiki 为外部工作区设计内索引（5134=3926 md+
890 txt+318 hermes 精确对账）。**验证**：全量回归 1896/1896，图谱/索引
多轮重建幂等，kb_merger self-check 6 项通过。

## v6.10.53 - 2026-09-25 nsfc-writing 写作纪律 skill 化：叙事主线修复进入自动链路（根因）

用户验收反馈（new-idea/attosecond 两课题）：信息量足够但三类问题——
风格偏离范本（审计腔）、研究内容/方案读完不知"做什么/怎么做"（防御性
装甲淹没主线）、机械罗列。诊断：8 轮 writer-critic 对抗循环中 critic
只按"防御完备性"扣分，writer 逐轮累积边界条件/降级预案/交叉引用锚点
（new-idea 实测：交叉引用 31 处、审计词 61 处、R1/R2/R3 代号 59 处），
风格标准从未进入对抗循环。用户裁决：根因修复走 skill 化而非 prompt
硬编码，人工处理（评审团/用户指令）只作兜底。

**新增 skills/nsfc-writing/SKILL.md**（风格纪律单一真相源，七节）：读者
视角总纲（读完知道做什么/怎么做）、叙事主线纪律（顺叙为主/防御性内容
降权——每段≤1 条件分支、预案集中方案末节/交叉引用预算每千字≤1 处/
量化指标嵌入叙述）、审计语言替换映射（交付物/硬门控/入门阈值/口径/
锚定/R1R2R3 代号等 13 条）、语言结构规范（范本对标）、正反对照样例
（样品段两版对比）、writer 自检清单 6 项、critic 检查项 5 条（含
"科学正确性优先级高于风格检查"护栏）。

**optimize.py 接入**：`_load_nsfc_writing_skill_text(role)` 按角色裁剪
注入（writer 拿纪律+映射 ~1.1KB，critic 拿检查项+黑名单 ~1.05KB，
完整 skill 给路径按需读），挂接 writer/critic prompt 构造处，fail-open，
模块级缓存。后续修订风格规则只需改 SKILL.md 一处，全链路生效。

**new-idea 课题叙事重构（skill 首个应用案例，用户过目样例）**：
content+scheme 重构——交叉引用 31→0、审计词 61+代号 59 处归零、
§2.7 失败模式节迁入 scheme §9 集中风险应对、四环节标签段改顺叙；
数值对账零损失（40+ 关键参数逐项 ✓）、评审团修复防回退（空间群
P6₃/mmc/Γ-K 分方向表/[21] 属性）全存活；full_review 骨架同步新结构，
rationale 残留代号清理。

**测试**：新增 test_nsfc_writing_skill.py（S1 结构完整/S2 角色裁剪/
S3 fail-open/S4 挂接防误删/S5 token 预算≤3KB）；全量回归 1896/1896 通过。

遗留：attosecond 课题同类重构待用户确认 new-idea 样例方向后执行；
skills/README.md 已登记 nsfc-writing。

# 变更记录

## v6.10.44 - 2026-09-25 深度检查：备份隔天回归修复 + 对账盲区补录 + 文档基线刷新

对近一个月（v6.9.75→v6.10.42，120 提交）的全面深度检查（功能实测/文档
一致性/工作流健康/架构冗余四层），修复 5 项：

**P0 备份隔天自持回归（v6.9.70 幂等修复的边界漏洞）**：13:00 cron 在
13:01 完成后，次日 13:00 age=23h58m<24h 必跳过 → 永远隔天一份（实证
09-11 起缺 12/14/16/18/20/21/23 共 7 天）。改为按自然日判定：今日 UTC
已有全量备份才跳过。修复后手动验证立即产出当日备份。

**对账盲区补录**：lc-kb-distill-pm（18:50 第二档，曾撤出 manifest）与
lc-daily-sync（09-02 重建版——sync_engine __main__ 已改真 sync_all，非
当年 self_check 冒充）补入 CRON_MANIFEST（19→21 项），对账 0 问题；
manifest 顶部加对账范围注释（林赛简报 5 条/prompt-optimize/worker 为
有意排除，防误判）。

**深度阅读管线激活**：deep_read_pipeline --process 此前无任何自动调用方
（has_fulltext→五要素蒸馏层休眠），挂入 kb_auto_sync 尾部（每日 12:40
随 kb-sync 链执行，fail-open limit=10）。

**文档基线刷新**：AGENTS.md 测试基线 1146→1896（实测）、cron 清单
10→19 描述、蒸馏时段补周日档与 digest_level 分层说明、最后更新日期。
PROJECT-STRUCTURE/ARCHITECTURE 停留在 v6.9.29（标注遗留）。

**测试基线同步**：monitor_cron_stale/ghost_write 两套件的模拟 cron 清单
补 lc-kb-distill-pm 与 lc-daily-sync。

**检查确认无问题项**：gate2 双门筛选实际效果良好（池 254 篇已打分 251，
拒绝 33 篇=13%，9-10 分核心档 101 篇）；知识库重构终态（wiki 2050 =
fulltext 596 + abstract 1454，PDF 库 750）；30 个 cron 全部 last_status=ok；
两套深读系统（CoPilot ≥8 全文库 / hermes ≥9 简报池日 2 篇）为分层设计
非重叠；housekeeping（v6.10.42）与 backup/kb_maintenance 边界清晰；归档
模块无引用回流；执行历史最近 50 条零失败。

**遗留观察**：磁盘 knowledge 4.5G/backups 27G/.git 3.3G（一个月 ×5/×17/
×7，housekeeping 已上线观察效果）；human_queue 5 项待验收（1 项超 72h
已催办）；PROJECT-STRUCTURE/ARCHITECTURE 两文档待系统性重写（工程量大，
建议专项做）。

## v6.10.42 - 2026-09-24 数据域滚动治理：housekeeping 守护（分割+滚动释放，用户审计诉求落地）

- 背景：用户提出"持续膨胀文档需要适当分割+滚动释放（如日志）"。全库审计确认已有机制覆盖 linsai.log（TimedRotatingFileHandler 30 天轮转）、method-manual（v6.10.41 软上限 60KB+压缩任务）、kanban execution_history（200 条）、error_history（10 条）、processed_sources（28 天滚动）——但五类文件持续膨胀无治理：weekend-input 周快照 32.7MB（sources-*.json 每周 2-4.5MB 累积无清理）、hermes researcher MEMORY.md 196KB/859 条（纯追加，430+ 条 job 日志噪音）、proposal-draft-rN.md 轮次备份无上限（44 个积压）、knowledge/*.bak* 手工备份累积、reading-notes.md 27-51KB 持续追加
- 新增 `scripts/housekeeping.py`（零依赖标准库，dry-run/apply/status/self-check 四模式，治理原则：可再生数据超限删除，资产类只归档分割不删内容）：① weekend-input 周快照 >8 周 gzip 压缩、压缩档 >24 周删除（活注册表 clusters.json 等白名单永不触碰）② profile MEMORY.md >120KB 或 >900 条滚动，保留"尾部累计 ≥40KB 且 ≥200 条"，旧条目移入 MEMORY-archive-{date}.md（首版按条数切实测 859→500 条仅 196KB→192KB 无效，改为按字节切后 196KB→78KB）③ proposal-draft-rN.md 保留最近 3 版（git 历史兜底）④ knowledge 同前缀 bak 保留最近 2 个 ⑤ reading-notes >60KB 按 `## ` 条目边界分割，旧段入 reading-notes-archive-{date}.md
- 修复（测试实测捕获）：周快照首版 glob(SNAPSHOT_PATTERNS) 匹配不到 `.json.gz` 压缩档（后缀不符），压缩档永远进不了超龄删除分支——改为 iterdir + fnmatch（去 .gz 后缀统一匹配）
- 挂接：`kb_auto_sync.run_sync()` 尾部每日调用（12:40 cron lc-kb-sync），fail-open 不阻塞同步；无需新增 cron（不触碰 v6.8.54 cron 拓扑清单）
- 首次执行（--apply）：MEMORY.md 196KB→78KB（659 条归档至 MEMORY-archive-20260924.md，§ 分隔格式与最新条目完好）；draft 轮次备份删除 44 个释放 3.7MB；knowledge bak 删除 3 个释放 259KB；research_proposals 39.0MB→35.3MB。周快照压缩窗口下周陆续开启（当前最老 54 天 < 56 天阈值）
- 测试：新增 `tests/test_housekeeping.py`（30 断言：快照压缩/超龄删/活文件豁免、MEMORY 按字节滚动+归档不丢内容+未超限不动、draft 保留 3 版、bak 同前缀留 2、笔记按 ## 边界分割）；`self_test.py --module` 固定清单补入 `test_token_redundancy_fix` + `test_housekeeping`（此前新套件仅全量自动发现模式覆盖，--module 健康检查不含）；`self_test.py --module` **1896/1896** 全量通过（v6.10.41 后 1835 + token 冗余 31 + housekeeping 30）
- 更新 `VERSION` 文件 6.10.41 → 6.10.42

## v6.10.41 - 2026-09-23 token 冗余设计六项修复（工作日 agent loop 调用 230-270 次/天 → 预期 ~1/3）

- 背景：用户反馈"token 消耗特别严重"。审计确认工作日 agent loop 调用从 8 月底 80-170 次/天涨到 230-270 次/天（09-23 当天 272 次/137 job），根因是 v6.9.87 不间断轮转（19h 连续派发）× 7-8 个优化中课题 × 每轮 34 个 LLM 会话模板。逐调用点审查确认六处冗余设计，按浪费量排序修复（已排除嫌疑：lit_read 跨轮重读实测 0%、MEMORY.md 注入有 2200 字符截断兜底、多源检索 HTTP 层零 LLM token）
- 修复①（最大头，`lifecycle/controller.py::_build_full_round_jobs`）：**已通过章节跳过**——旧实现每轮无条件构建 25 job（3 章节 × critic+gap+search+read+note+writer + full_review/references/monitor/derived），`section_passes` 只用于完成判定从不用于跳过，后期轮次已达标章节照样重跑完整对抗链。现常规轮跳过 passed 章节（依赖链自动重接：后续 critic 依赖最近未跳过章节的 writer，全跳过时回落 idea_review/空依赖），每 3 轮（round_num % 3 == 0）强制复检轮全量构建防跨章影响长期失检；跳过章节 section_passes 保持 True，completion 语义不变。晚段轮次省 30-60% 会话
- 修复②（`lifecycle/executor.py::_run_lit_read_step`）：**5 篇合并单会话**——旧实现逐篇各开一次 hermes oneshot 会话（5 篇 = 5 个完整 agent 会话，约占轮内会话量 45%）。现一次会话带 5 篇按 `## <arXiv ID>` 分节输出（每维度 2-3 句、总输出 ≤6500 字），regex 解析分节，有效门槛 120 字符；截断/缺失篇目降级 `LiteratureService.read` 单篇兜底（与旧降级路径同源）；timeout 240→600。wiki 笔记写入副作用保持（仅会话产出的有效篇目）
- 修复③（`_run_lit_search_step`）：**空缺口短路**——gap_identify 产出 0 缺口/0 关键词时（09-23 实测 quantum-geometry R8 scheme 轮），旧链路照样派发：agent loop 白跑回答"关键词为空"（浪费 1 会话），多源回退用默认词 "high harmonic generation" 捞回 2010/2011 泛域老文，lit_read 再烧 5 会话深读低价值文献——单次空缺口 ≈6 会话纯浪费（当天 2 次）。现短路返回 `method=short_circuit` 并落盘带章节标记的空 lit-gap 文件（lit_read 按 v6.10.6 章节匹配读到它 → 无 arxiv_id → 跳过），零 LLM 消耗
- 修复④（同函数）：**排除清单截断**——旧实现把全部本地论文 ID（实测 1408 个 ≈16.5K 字符/4-8K token）注入每次 lit_search prompt，随 KB 增长线性膨胀，且与解析后程序化去重（is_new 标记 + 多源 existing_keys）职责重叠。现仅提示总量 + 采样 80 个 ID 示例并说明完整去重由系统程序化执行
- 修复⑤（`proposal_lifecycle/optimize.py::_run_writer_optimize`）：**writer 指令栈按章节裁剪**——"文件纯净性红线"块从 v6.8-v6.10 十几层版本累积的无条件注入改为：通用规则（正文纯净/白名单/内容边界）始终注入，references 工作日志迁移规则仅 references 轮注入，full_review 骨架规则仅 full_review 轮注入（`_purity_rules` + `_eff_section`），rationale/content 轮不再背负无关指令
- 修复⑥（`_run_update_method_manual_step`）：**手册膨胀治理**——手册每轮重写已涨到 60-186KB（quantum-geometry 186KB ≈ 单会话 5 万 token 读写量，v6.9.60 纪律指令未能阻止）。三层防御：超软上限 60KB 注入压缩任务（目标 ≤40KB）；正常轮指令"只读目录与相关小节，无关章节不重读"；步骤后检测本轮膨胀 >10% 记 warning 供观测
- 附带修复（`_run_writer_step` 的 `lit_supplement`）：从盲取最新 lit 文件改为章节感知匹配 + 空报告过滤（v6.10.41 短路落盘的空报告/其他章节报告不再误导 writer 找不存在的文献）
- 测试：新增 `tests/test_token_redundancy_fix.py`（31 断言：空缺口短路零会话+空报告章节标记、排除清单 ≤80 采样+prompt <6000 字符、常规轮跳过 passed 章节+依赖重接+复检轮 25 job 全量、lit_read 合并单会话+截断降级补齐+wiki 写入副作用）；`test_mechanism_hardening.py` 纯净性守卫按章节裁剪语义更新（"full_review.md 同样适用"无条件注入 → `_eff_section == "full_review"` 条件注入）；`self_test.py --module` 1835/1835 全量通过（v6.10.40 基线 1804 + 新增 31）
- 更新 `VERSION` 文件 6.10.40 → 6.10.41

## v6.10.40 - 2026-09-23 健康检查根因修复：kb_graph 污染闭环（MOC.md 脏 frontmatter + _update_moc/_inject_wikilinks 自我强化）

- 根因追查：v6.10.39 只清了 graph.json 数据 + kb_graph 防御，但"污染来源未明"。深挖确认**污染闭环**：`knowledge/wiki/projects/NSFC-强场超快/MOC.md` 的 `project`/`tags`/`related` 三字段被三层 json.dumps + build_frontmatter 字符串化写成 `[\\\\\\\\"...\\\\"]` 双重转义字符串（含 100+ 反斜杠）。`kb_proposal_reorg._update_moc`（lc-kb-sync cron 每日触发）读回污染串（字符串）→ `build_frontmatter` 对 str 再包引号 → 反斜杠翻倍逐轮自我强化；`_inject_wikilinks` 用字符串 related 生成 `- [[["2503.08052]]` 畸形链接。下游读 MOC 污染 project → `kb_wiki.update_graph_node` 写污染 title 进 graph.json → `_count_graph_orphans` 拼超长路径 Errno 63
- 修复 1（`scripts/kb_proposal_reorg.py::_update_moc`）：**重建干净 frontmatter 数组字段**——`project=["NSFC-强场超快"]`、`tags=["MOC",...]`、`related=_extract_moc_related(all_proposals)`（从 lifecycle 派生课题标签，去重保序），彻底切断污染闭环而不是复用旧污染值
- 修复 2（`_strip_polluted_wikilinks`）：剥离 body 中被污染的 `<!-- linsai-wikilinks -->` 畸形链接区块，由后续 kb 流程重建
- 修复 3（`_coerce_frontmatter_value` + `parse_frontmatter`）：解析 frontmatter 时对数组字段尝试折叠反斜杠并 json.loads 还原，防御性质兜底（失败原样返回不抛异常）
- 数据清理：应用 `--apply` 修复 MOC.md——frontmatter 三字段恢复干净数组、body 畸形 wikilinks 剥离；保留手工概念/方法/团队/论文/外部链接 sections
- 验证：`kb_proposal_reorg.py` dry-run + --apply 均成功；修复后 MOC.md frontmatter `project: ["NSFC-强场超快"]` 干净数组；`get_kb_health()` graph_nodes=2247 / graph_orphans=0 / kb_health OK；`self_test.py --module` 1835/1835 全量通过
- 更新 `VERSION` 文件 6.10.39 → 6.10.40

## v6.10.39 - 2026-09-23 健康检查发现：kb_graph 污染 title 写入图谱导致 kb_health 测试失败 + 防御性检查

- 背景：09-23 20h 健康检查发现 `self_test.py --module` 实测 1832/1833（vs CHANGELOG 基线 1833/1833 全过）— `_test_kb_health` 抛 `OSError: [Errno 63] File name too long`。定位根因：`knowledge/graph.json` 内有 2 条污染节点（type=projects，path 含 100+ 个反斜杠的转义串 `wiki/projects/[\\\\\\\\...NSFC-强场超快\\\\\\\\...]`），调用 `_count_graph_orphans` 时 `(KNOWLEDGE_DIR / path).exists()` 把整段 path 拼接到路径下，超出 macOS 文件名 255 字节上限。污染来源未明（疑似某次 raw 文献 / YAML 解析错误经 `update_graph_node` 写入图谱）
- 修复 1（数据层）：手动清理 graph.json 2 条污染节点 + 2 条相关边（备份 `knowledge/graph.json.bak-kbhealth-20260923`），原子写回；清理后 `_count_graph_orphans` 实测 0 孤儿（vs 修复前 Errno 63），`graph_nodes` 2249 → 2247
- 修复 2（代码层 `scripts/kb_graph.py::update_graph_node`）：增加防御性检查——title 含连续 ≥3 个反斜杠视为污染数据，拒绝写入（返回前不抛异常，保持现有调用兼容）；同步检查非字符串 / 空字符串
- 测试：`test_core.py` 新增 `_test_kb_graph_defensive`（正常 title 通过 + 连续 50×3 反斜杠污染 title 被拒绝，2 断言）；`self_test.py --module` 1835/1835 全量通过（v6.10.38 基线 1833 + 新增 2）
- 更新 `VERSION` 文件 6.10.38 → 6.10.39

## v6.10.38 - 2026-09-21 簇持续积累结构性修复：linked 簇影子吸收（连续 4 周 assigned=0 根治）

- 背景：用户问"已有簇的持续积累效果如何"。实测数据揭示结构性空转——**连续 4 周（09-05/09-12/09-19/09-20）assigned 全部为 0**，注册表 62 簇中 open=0（59 linked + 3 closed），孤儿池 583 条（334 条处于 29-42 天濒清理窗口）。根因是簇生命周期结构性循环：成簇 → 当周被 topic_match 路由 → linked → 不再吸收 → open 清零；assign_summaries 只往 open 簇融入、recycle_orphans 只回收进 open 簇、form_new_clusters 的开簇查重又与全部簇（含 linked）比对——同主题新文献"无簇可归 + 开新簇被防换皮查重挡回"双路皆堵，只能滞留孤儿池等 42 天清理 = 系统性知识流失。上周末 R18-R31 共 14 轮约百篇深读文献全部落孤儿
- 修复（`weekend_pipeline/clusters.py`）：新增 `absorbable_clusters(registry)`——可吸收簇 = open 簇 + 未超 `MAX_ABSORB_MEMBERS=30` 上限的 linked 簇（closed 仍排除）；`assign_summaries` 与 `recycle_orphans` 的候选集从 open 扩展为可吸收簇（"影子吸收"：linked 簇吸收的新成员不触发重新路由，assigned 条目带 `cluster_status=linked` 标记）
- 课题挂载通道（`weekend_pipeline/input_jobs.py::run_input_cluster_assign`）：linked 簇影子吸收的新成员直接调用 `_write_supplementary_sources` 挂载为目标课题补充信息源（expansion 语义：文献进入课题 references 校验与 writer 视野，不重新路由不注入知识卡——簇已路由过）；job 结果与 `clusters-week-*.json` 新增 `linked_absorbed`/`linked_mounted` 计数
- 测试：`test_input_clustering.py` 新增 `_test_linked_cluster_shadow_absorb`（7 断言：linked 吸收带标记/closed 排除/成员上限/孤儿回收扩展），2 个旧用例改为孤儿直接预置（聚焦 form_new_clusters 开簇查重语义——影子吸收已由新用例覆盖，原"assign→orphan→查重挡回"路径已变）；聚类套件 151/151；`self_test.py --module` 1833/1833 全量通过（v6.10.37 基线 1827 + 新增 6）
- 预期效果（下周末实测验证）：open 清零状态下新料沿 59 个 linked 簇融入并直挂课题；孤儿池的 334 条濒清理存量将由 recycle 二次匹配批量回收（同口径 0.22）；`linked_absorbed` 周计数应从 0 变为数十量级
- 更新 `VERSION` 文件 6.10.37 → 6.10.38

## v6.10.37 - 2026-09-21 用户裁决落地 + new 门槛主线三防线（6 退 1 接受根因修复）

- 用户裁决执行：接受 `general-ssh-weyl-20260920`（固态 HHG 探测拓扑物态，drafts→optimizing 激活）；退回其余 6 课题（h-wn6/lifshitz-td-wte2/mott/mc3d/new-idea-20260919/new-idea-20260919-02，drafts→archived，理由"用户裁决 09-21：相关度差"），知识库提案索引自动同步
- 根因分析（对比接受簇 vs 退回簇的实测数据）：① **范式词表只约束手段不约束研究对象**——CORE_THEME_TERMS 命中"阿秒/强场/HHG"即放行，"少阿秒电子脉冲串""孤立阿秒时空光学涡旋"两簇研究对象是自由电子束/气体介质光源，字面命中但完全主线外；② **4 个退回簇 research_gap 为空**（被接受的 ssh-weyl 簇 gap 完整 100+ 字）——v6.10.28 加的字段没用作门槛，知识卡不完整照样开题；③ **5 个退回簇"3 篇成员"含同题双版本**（arXiv 预印本+期刊发表版未去重，独立文献仅 2 篇）——"3 篇起簇"的多源佐证要求被虚增满足；④ 附带发现：compare_with_existing 的 Jaccard 相似度对"簇 idea vs 课题 brief"口径全面偏低（接受课题仅 0.017、全部 <0.1），主线锚定不能靠相似度阈值（实测校准后弃用该方案）
- new 门槛三防线（`weekend_pipeline/input_jobs.py::_new_gates`，四重门槛 → 七道关）：**关 1 升级**——成员计数从 source_ids 改为 member_summaries 归一化标题去重（同题双版本算一篇，空 summaries 回退旧口径）；**关 6 主线体系关**——新增 `MATERIAL_SYSTEM_TERMS` 体系词表（固体/二维/拓扑/磁性/铁电/莫尔/激子/Weyl/Mott 等中英 50+ 词），簇文本须命中（范式词+体系词双命中=手段与对象都对齐主线；10 个 optimizing 课题全部满足）；**关 7 知识卡完整关**——research_gap 非空才可开题
- 防线效果（对 09-21 六个退回簇回放）：电子束串/阿秒涡旋栽体系关（主线外）、mc3d/mott/hWN6 栽成员关（凑数）、4 个栽缺口关——六退簇中 5 个可被程序拦截；WTe2 滑移簇（3 篇独立+gap 完整+体系命中）属"主题同源但词袋测不出"的语义层判断，保留给 idea_review 前置评审与人工立项裁决把关（宁缺毋滥原则下宁可多拦）
- 测试：`test_input_clustering.py` 新增 `_test_new_gates_mainline_guards`（体系关/缺口关/成员去重关/合格簇放行，8 断言），更新 3 处旧夹具适配新门槛（cl_d/quota 三簇/sf_cluster 补体系词与 research_gap）；聚类套件 145/145；`self_test.py --module` 1827/1827 全量通过（v6.10.36 基线 1820 + 新增 7）
- 更新 `VERSION` 文件 6.10.36 → 6.10.37

## v6.10.36 - 2026-09-21 新课题标题可读性修复：注册 title 落 state + brief 占位回退 + 存量 7 课题回填

- 背景：用户问"最近有新增课题吗"，巡检发现上周末输入端注册了 7 个新课题（09-18 批 4 个：双束反向传播少阿秒脉冲串/孤立阿秒时空涡旋/稀土镍酸盐莫特相变 THz 三次谐波/线偏振超快磁化；09-20 批 3 个：结构压缩调控 HHG 截止能量/SSH-Weyl 拓扑物态 HHG 探测/WTe2 层间滑移 HHG），全部在 drafts 待人工激活（09-18 批已在待人工队列等 67h，接近 72h 催办线）——但 brief 的课题名称全部是"（待生成）"，待人工队列只显示 proposal_id，用户无法判断课题内容
- 根因：`register()` 的 state_data 不存 title；drafts 阶段无申请书，`update_proposal_brief` 的 `_extract_proposal_title` 只能从旧 brief 提到"（待生成）"占位串（非空，挡住回退）
- 修复（`proposal_lifecycle/registration.py` + `metadata.py`）：① `register()` 新增 `title` 参数写入 state；② `register_from_idea` 传递 `idea.title`；③ `update_proposal_brief` 在提取值为空或等于"（待生成）"占位时回退 `state.title`
- 存量回填：从各课题立项决策包首行（"# 立项决策包 · {title}"）提取标题写入 state（加 `file_lock`，备份 `_lifecycle.json.bak-title-backfill-20260921`），重建 7 个 brief——课题名称全部可读
- 测试：`test_skill_integration.py` 新增 `_test_register_title_fallback`（register 显式传 title / register_from_idea 路径 / brief 渲染非占位，6 断言）；`self_test.py --module` 1820/1820 全量通过（v6.10.35 基线 1815 + 新增 5）
- 更新 `VERSION` 文件 6.10.35 → 6.10.36

## v6.10.35 - 2026-09-21 检索更新落位修复：多源补充移植到真实 job 路径（lit_search 实际 handler）

- 背景：用户问"更新的检索方式有没有按预期起效"。实测验证未生效——今日 BSV R5 / moire R4 共 7 次 lit_search 产出的检索报告均无"多源学术检索补充"章节、无 candidates-*.bib 副产物、无补充日志。排查根因：job 链 lit_search step 的真实 handler 是 `lifecycle/executor.py::_run_lit_search_step`（hermes researcher agent loop 优先 + LiteratureService 降级），而 v6.10.32 把三源并发/year_from/BibTeX 加在了 `proposal_lifecycle/optimize.py::_run_literature_searcher`——该函数只被旧版单 job 兼容路径（`_run_researcher_step`，"向后兼容"注释）调用，改动落在了死路径上。教训：改代码前未核实函数在 job 链中的真实调用关系
- 移植（`lifecycle/executor.py::_run_lit_search_step`）：agent loop 检索结果之后、写报告之前插入多源补充块——① `search_academic` 三源并发叠加（与 agent loop 结果按 arxiv_id/doi/title 去重，失败静默降级不阻塞）；② candidates-{ts}.bib 副产物 + 报告新增"多源学术检索补充"章节（附 .bib 路径）；③ 日志带源清单与年份口径
- 时效过滤口径修正（`_multi_source_search_config`）：references 分支扩展为 references/full_review 都限近 3 年——job 链中 references 轮本身无 lit_search job（仅 critic+writer 两步），full_review 轮的检索才是 references 时效补充的实际载体；经典文献由不限年的 hermes agent loop 检索层提供，多源层专注补新。executor 调用侧按 `section_key` 构造传参（full_review 轮 focus_section 为 None 的坑）
- `optimize.py` 旧路径的同款代码保留（无害，向后兼容路径触发时仍有增益），`_run_literature_searcher` 注释标注
- 测试：`test_skill_integration.py` 补 full_review 限年断言；`self_test.py --module` 1815/1815 全量通过（v6.10.34 基线 1814 + 新增 1）
- 更新 `VERSION` 文件 6.10.34 → 6.10.35

## v6.10.34 - 2026-09-21 整合调用巡检收尾：compose new 路由接入六模块补全 + route 短步骤误滤修复

- 背景：用户要求检查当前链路是否已包含对两个桌面技能的调用。巡检结论——检索能力（academic-literature-search）已完整接入（优化链路 `optimize.py:1614` researcher 定向检索三源并发+年份过滤+BibTeX 副产物；`learning_engine.py:732` 自主学习自动享受并发）；六模块模板（research-proposal）存在缺口：v6.10.31 只注入了 idea_generator 的 prompt，但 `--auto` 早已不在 cron 链路（v6.9.12 知识簇链路取代），全自动设想主路径是 topic_match → compose new → register_from_idea，构建的 idea 只有基础字段——dossier 新章节（技术路线/验证方案/与参考工作的区别）永远为空，模板只在 Web 手动入口（`web_routes_system.py` → `expand_manual_idea`）生效
- compose new 六模块补全（`weekend_pipeline/input_jobs.py`）：新增 `_enrich_idea_six_modules(idea, cluster)`——new 路由落地前按模板补全 route/validation/comparison 三字段（输入：簇标题/知识卡/research_gap/开放问题/成员文献；prompt 约束"增量贡献必须说清新在哪里，只换材料不换科学问题不算贡献"）；只取三字段防 LLM 越权重写 title（防漂移）；LLM 不可用/失败/垃圾输出一律原样返回降级不阻塞；清洗复用 `idea_generator._coerce_idea_fields`；JSON 解析复用 `_llm_json`（v6.10.9 三层健壮解析）。成本：每个 new 课题 1 次 LLM 调用（周配额 ≤2 可控），merge/expansion 不补全（注入现有课题无需）
- route 短步骤误滤修复（`idea_generator.py`）：`_coerce_idea_fields` 拆分过滤最小长度 6→4——"对比验证""数值模拟"等 4 字合法步骤被整步丢弃（新测试用例实测"步骤三：对比验证"丢失）。同时修复 `test_skill_integration.py` 的 `__main__` 块读取不存在的 summary key 掩盖失败（单跑假绿，全量回归才暴露）
- 测试：`test_skill_integration.py` 新增 `_test_enrich_idea_six_modules`（LLM 正常补全+清洗/失败降级/垃圾输出/不可用四态，7 断言）+ 4 字短步骤回归断言，setup 补 weekend_pipeline 模块隔离；套件 62/62；`self_test.py --module` 1814/1814 全量通过（v6.10.33 基线 1805 + 新增 9）
- 更新 `VERSION` 文件 6.10.33 → 6.10.34

## v6.10.33 - 2026-09-21 测试写穿生产 lifecycle 修复：test-proposal-clear-nfa 残留清理 + 套件隔离补齐

- 背景：09-21 00:00/00:05 微调度器两次聚焦 `test-proposal-clear-nfa` 并派发 job——该课题是 `test_negative_feedback_global_recovery.py` 第 10 节写入生产 `research_proposals/_lifecycle.json` 的测试残留（status=optimizing，无 title/created_at，26 个 job），09-16 首次写入起持续污染轮转队列（挤占真实课题窗口 + 浪费 LLM 配额），09-18 与 09-21 多次被派发。根因：套件 `setup()` 调 `create_isolated_env()` 未接收返回值、未重定向 `proposal_lifecycle` 根路径，第 10 节 `ProposalLifecycle()._load_state()/_save_state()` 直写真实 state——v6.9.54 的跨套件模块卫生防护不覆盖这种"套件自身直写"路径
- 测试修复（`test_negative_feedback_global_recovery.py`）：setup 补齐标准隔离（tmp_root 接收 + `paths.PROJECT_ROOT` 重定向 + `proposal_lifecycle.constants.PROPOSALS_ROOT` 重定向 + `patch_module_root`），teardown 恢复真实根路径并清理临时目录（防后续套件沿用隔离值）；验证：单跑 16/16 通过，跑套件前后真实 `_lifecycle.json` 的测试课题条目逐字节一致（写入全部落在隔离目录）
- 生产数据清理：加 `file_lock("proposal-lifecycle")` 删除 `test-proposal-clear-nfa`（备份 `_lifecycle.json.bak-test-pollution-20260921`），无文件目录残留（微调度器执行过的 job 均因"proposal 目录不存在"失败，未产生产物），剩余 9 个真实 optimizing 课题
- 顺带确认（本次巡检）：链路周一 00:00 窗口正常开启（focus-slots 00:00-13:00/18:00-23:59），微调度器每 5 分钟运行，09-20 stuck 的两个课题 job 已被 repair 重置 pending（attempts=0），00:10 起聚焦 `general-mos2-20260905`（R5 rationale critic 正在执行，hermes 进程活跃）
- 测试：`self_test.py --module` 1805/1805 全量通过
- 更新 `VERSION` 文件 6.10.32 → 6.10.33

## v6.10.32 - 2026-09-21 优化链路检索环节对齐整合能力：references 时效过滤 + 三源并发 + BibTeX 副产物

- 背景：v6.10.31 把 academic-literature-search 技能的检索能力整合进 `external_fetcher`（并发/year_from/BibTeX-RIS），但全自动优化链路的检索消费方（`proposal_lifecycle/optimize.py` 的 `_run_literature_searcher`，researcher 定向检索）仍停在旧口径（双源顺序、无年份过滤、无引用格式输出），用户指示相应更新
- 源扩展：多源补充检索 `sources` 由 `("arxiv","openalex")` 扩为 `("arxiv","openalex","semantic_scholar")`——`search_academic` 已并发化，加源不增墙钟，S2 匿名 429 由单源容错兜底（实测自检 S2 无 key 常空返回，空结果即静默降级）
- 时效对齐：新增纯函数 `_multi_source_search_config(focus_section)`——references 聚焦轮返回 `year_from = 当前年-3`（呼应 references critic 检查项"总数 20-40 篇 + 是否包含近 3 年文献"，时效性缺口直接消解在检索源头）；其余章节/整篇轮不限年（立项依据与机制溯源常需经典高引文献如 Berry 1984，一刀切限年会误杀奠基性引用）
- BibTeX 副产物：多源候选去重后落 `02_literature/targeted-research/candidates-{ts}.bib`（`format_bibtex` 标准格式），检索报告"多源学术检索补充"章节附副产物路径——writer 修订 references.md 时直接取标准条目，不再手编引文格式（引文格式错误是 critic 严谨性维度的高频扣分项）
- 报告增强：多源章节标题按实际源动态生成；检索日志带源清单与年份口径
- 测试：`test_skill_integration.py` 新增 `_test_multi_source_search_config`（6 断言：references 轮限近 3 年/其余章节不限年/源清单一致性），setup 补 proposal_lifecycle 模块隔离；`self_test.py --module` 1805/1805 全量通过（v6.10.31 基线 1799 + 新增 6）
- 更新 `VERSION` 文件 6.10.31 → 6.10.32

## v6.10.31 - 2026-09-21 桌面技能整合：research-proposal 六模块模板 + academic-literature-search 检索能力

- 背景：用户提供桌面两个 OpenClaw 技能包（`~/Desktop/research-proposal/` 六模块研究设想模板、`~/Desktop/academic-literature-search/` 多源文献检索 v2.0.0），指示按"模板注入 idea_generator prompt、检索能力并入 external_fetcher"方案整合进本项目。两者定位互补：前者提升设想生成质量（强制说清增量贡献，防"换皮课题"），后者提升检索吞吐与引用格式输出
- 整合点 1 · 六模块模板（`idea_generator.py`）：`_build_idea_prompt`（自动生成）与 `expand_manual_idea`（手动扩展）注入新字段要求——`route`（技术路线分步）、`validation`（验证方案，含替代解释排除）、`comparison`（与参考工作的区别：core_refs 核心对比文献 + table 对比表 + increment 增量贡献 + boundary 边界界定 + depends 依赖关系）；content 强制方法具体化（"禁止'利用超快测量技术'类模糊表述，必须'基于时间分辨HHG光谱，测量…'"）；system prompt 增加"只换材料不换科学问题的不算新课题"红线。新增 `_coerce_idea_fields` 形状防御（route 整段字符串拆条目、comparison 垃圾输入兜底空结构、截断上限防 prompt 爆炸）；`generate_idea_dossier` 渲染技术路线/验证方案/与参考工作的区别三个新章节（对比表 Markdown 表格）
- 整合点 2 · 检索能力（`external_fetcher.py`）：`search_academic` 由顺序查询改为 `ThreadPoolExecutor` 并发（标准库零依赖，3-4 源墙钟时间从串行叠加降为最慢单源）+ `year_from` 年份过滤（year 字段缺失从 date 前 4 位回退）；新增 `format_bibtex`/`format_ris` 引用格式输出（BibTeX key=首作者姓+年+序号，支持"Given Family"与"Family, Given"两种作者格式，无作者兜底 Unknown）；自检补 12 断言（离线夹具）
- 设计决策保持：Crossref 仍仅作 DOI 元数据补全、不作关键词发现源（相关性差，v6.8.42 实测决策，见 `fetch_crossref_doi` 注释）；技能包的 aiohttp/pandas 第三方依赖不引入（本项目零依赖约束）
- 测试：新建 `tests/test_skill_integration.py`（7 用例 47 断言：prompt 六模块要素注入、route/comparison 形状防御、dossier 新章节渲染、BibTeX/RIS 输出、search_academic 离线打桩验证去重合并/单源失败容错/year_from 过滤/引用数降序），注册进 `self_test.py --module` 清单；`self_test.py --module` 1799/1799 全量通过（v6.10.30 基线 1752 + 新增 47）；`external_fetcher.py` 自检全项通过（网络路径实测聚合 3 篇）
- 更新 `VERSION` 文件 6.10.30 → 6.10.31

## v6.10.30 - 2026-09-20 输入端跨 UTC 午夜路由错位修复：compose 按 state 路径读 routes

- 背景：用户报"输入端连续 2 次周末运行零研究设想（ideas-09-19/09-20 actions=0）"。排查 `routes-2026-09-19.json`（1 条 CrSb expansion 路由，07:41 写入）与 `ideas-2026-09-19.json`（04:20）时间线发现错位：R27 topic_match 在 UTC 09-19 23:41 写 `routes-2026-09-19.json`，compose 在 UTC 09-20 00:00:54 执行（20 分钟 worker 间隔跨过午夜），按 `now_utc()[:10]` 猜文件名读不存在的 `routes-2026-09-20.json` → 空路由 → ideas actions=0，CrSb expansion 路由滞留未消费、簇未标 linked
- 根因：compose 与 topic_match 用各自执行时刻的 UTC 日期拼接 routes 文件名，跨午夜时两 job 日期不一致——与 v6.9.98 为 summaries 修的跨天错位（`last_summaries_path`）同类问题，routes 漏了同样处理
- 修复（`weekend_pipeline/input_jobs.py`）：① `run_input_topic_match` 写 routes 后把实际路径记录到 `state.input_round.last_routes_path`（相对 PROJECT_ROOT）；② 新增纯函数 `_routes_path_for_compose`——compose 优先按 state 记录路径读取，无记录回退当日文件名（兼容旧 state）；③ `weekend_pipeline/rounds.py` 的 `reset_input_for_new_round` 同步清空 `last_routes_path`（与 last_summaries_path 对称），自检补断言
- 测试：`test_input_clustering.py` 新增跨午夜用例（state 记录路径优先读取 + 无记录回退当日），聚类套件 134/134；`self_test.py --module` 1752/1752 全量通过（v6.10.29 基线 1747 + 新增 5 断言）
- 更新 `VERSION` 文件 6.10.29 → 6.10.30

## v6.10.29 - 2026-09-20 孤儿回收链路：领袖聚团 + 回收二次匹配 + 强场散料清理豁免

- 背景：v6.10.28 三通道相似度修复归簇失配后，孤儿池仍膨胀至 567 条——348 条处于 28-42 天濒临清理窗口、其中 267 条命中强场/超快核心范式（HHG 光源、阿秒路径量子比特、Floquet 光控、超快 Berry 门等），下周末即触发 42 天清理=知识流失。定位两处结构性缺口：① 聚团算法"首种子贪心"对弥散簇失配（链式相关 A~B~C 而 A≁C 永远聚不起来）；② 旧孤儿从不参与增量归簇（assign 只处理当轮摘要），跨轮孤儿与已有/新簇之间没有匹配通道；③ 42 天清理一刀切，核心范式散料被当垃圾删
- 领袖优先聚团（`weekend_pipeline/clusters.py`）：`form_new_clusters` 改为每轮取度数（与其余 orphan 相似 ≥0.30 的数量）最高者当种子 + 组内生长（吸收与组内任一成员相似 ≥0.30 的 orphan 直至收敛），链式/弥散簇也能成团且与顺序无关；孤儿池 > `MAX_LEADER_SEARCH=800` 时退回首种子模式防 O(n²) 失控；修复收尾分支孤儿池重复计数 bug（567→1096 双算）。实测救回 19 条聚成 5 簇（HHG/强场/量子光学主题），耗时 144s 可接受
- 孤儿回收（`recycle_orphans`）：聚团后剩余孤儿与全部 open 簇（含本轮新簇）按 `ASSIGN_SIM_THRESHOLD=0.22` 取最高分二次匹配，零 LLM 确定性；成员吸收抽取 `_absorb_member` 与 `assign_summaries` 共用。机制为未来簇覆盖积累后持续生效（当前 6 簇覆盖窄，0 条属真实不匹配）
- 清理豁免（`prune_orphans` 新增 `keep_fn`）：`run_input_cluster_assign` 传入 `_is_core_theme_orphan`（`core_theme_hit` 口径，与 new 路由硬门槛一致）——超龄强场相关孤儿保留并标记 `theme_protected`，其余超龄散料照常清理（防无限堆积初衷不变）；job 结果与 `clusters-week-*.json` 新增 `orphan_recycled`/`orphan_theme_protected` 计数
- 测试：`test_input_clustering.py` 新增 3 用例（链式簇领袖聚团、孤儿回收沿簇融入、强场孤儿清理豁免），聚类套件 133/133；`self_test.py --module` 1747/1747 全量通过（v6.10.28 基线 1736 + 新增 11 断言）
- 更新 `VERSION` 文件 6.10.28 → 6.10.29

## v6.10.28 - 2026-09-20 聚类提炼工作流优化：三通道相似度 + 防换皮查重阈值独立 + 提炼闭环

- 背景：输入端连续 2 次周末零研究设想（ideas-09-19/09-20 actions=0）排查定位聚类链路三处瓶颈——① 归簇失配：09-19 R27 十条新料（超快光谱/二维材料/非线性光学）`assigned=0` 全落 orphans，相似度仅用 keywords+title，关键词抽取不全即失配；② 孤儿积压：orphans 膨胀至 567 条（320 条超 28 天逼近 42 天清理线=知识流失），防换皮查重与聚团共用 0.30 阈值过严，部分重叠但研究问题不同的合法新方向被已有簇挡下永远无法成簇；③ 提炼闭环缺失：LLM 提炼失败降级 fallback 后 `distilled_by` 永久非 llm，new 门槛（要求 LLM 知识卡）永不通过
- 归簇算法升级（`weekend_pipeline/clusters.py`）：`summary_similarity`/`item_similarity` 由双通道（kw 0.7 + title 0.3）改为三通道（kw 0.5 + title 0.25 + 摘要正文 0.25，新增 `cluster_summary_text` 簇侧成员摘要拼接与 `SUMMARY_TEXT_LIMIT` 截断），正文 2-gram 作关键词漏提时的兜底信号，把失配分数抬进 borderline 区间供 LLM 仲裁救回
- 防换皮查重阈值独立：`form_new_clusters` 新增 `FORM_CLUSTER_DEDUP_THRESHOLD=0.45`（原与聚团共用 0.30），仅"与已有簇主题高度重合"拒开新簇，共享泛词但方向合法的团可成簇，缓解孤儿积压
- 提炼闭环（`weekend_pipeline/input_jobs.py`）：新增 `open_clusters_needing_distill`（本周有新成员 或 `pending_redistill` 的 open 簇，不受周窗口限制）；知识卡质量门槛 `DISTILL_MIN_SUMMARY_CHARS=50` + `DISTILL_MIN_QUESTIONS=1`——不合格/失败卡标记 `pending_redistill=True` 下轮自动重试，不再一次 fallback 永久定格；知识卡新增 `research_gap`（研究缺口）字段辅助 new 决策；distill 产物增加 `pending_redistill` 计数
- 测试：`test_input_clustering.py` 新增 3 用例（摘要正文通道抬升得分、查重 0.45 放行部分重叠团、提炼质量门槛与重试闭环），并更新中文标题 2-gram 断言阈值（标题分量 0.3→0.25）；`self_test.py --module` 1736/1736 全量通过（基线 1723 + 新增 13 断言）
- 更新 `VERSION` 文件 6.10.27 → 6.10.28

## v6.10.27 - 2026-09-18 评分口径统一：references 2 维收尾分不再被当整篇分读（全链路 caliber 分型）

- 背景：得分波动排查（09-18 周报）定位三根因——① references 轮（2 维：rigor/completeness）与章节轮（4 维加权）口径不同，每轮步骤序固定 references 收尾，导致 `last_score`/`round_scores[-1]` 系统性等于 2 维收尾分；② 不同 section 评审报告共用裸名 `critic-round-{n}.md`，后写覆盖先写，章节轮误读 references 2 维报告（实测 attosecond r5 rationale=0.66 恰为 references 2 维均值，真实章节分 0.80）；③ 维度提取不完整（dims_partial）无口径标注。修复后 key-transient/moire 看板读数由 0.59/0.56 修正为章节均值 0.775/0.802（0.59/0.56 实为 references 2 维收尾分）
- 根因修复（v6.10.26）：`proposal_lifecycle/optimize.py` 新增 `_critic_report_path` 按 section 分文件（`critic-round-{n}-{section}.md`，兼容裸名旧约定回退）；`_run_critic`/`_run_writer_optimize` 写盘与 `executor._read_critic_report` 读盘同口径（section 感知），同轮多 section 不再互覆
- 口径标记入史：optimize.py 与 executor.py 的 score_history 写入统一加 `caliber` 字段（`references_2d`/`section_4d`），全库 211 条历史回填（refs_2d 40 / section_4d 169 / legacy 2）；attosecond r5 rationale 伪分 0.66→0.80 修正
- 看板/报告/总览口径统一（`lifecycle/micro_scheduler.py`）：新增 `_section_mean_score` 辅助函数（按 caliber 过滤取章节 4 维均值）；`_generate_round_report` 轮次总分由 `round_scores[-1]`（references 收尾 2 维分）改为章节 4 维均值、references 分单独成行展示；`_update_kanban` 看板得分同口径（当前轮无章节分时回退最近完成轮次均值，再兜底 last_score）
- 审核/预审/API 口径统一：`web_routes_system.py` 审核会话"最新评分"与 stages 总览 `last_score` 取最近一条章节 4 维口径分（排除 references）；`review_dossier.py` 预审回退逻辑同口径（旧逻辑取 history[-1]，references 收尾时拿到 2 维分做门槛判定）
- Web 服务器启动修复（v6.10.27）：`web_server.py` 新增 `LocalHTTPServer` 重写 `server_bind` 跳过 `socket.getfqdn` 反向 DNS 查询（实测 127.0.0.1 反查挂起 35s，击穿 WebApiSuite 30s 启动超时），启动时间 35s+→0.32s
- 周报口径修正（outputs/weekly-review-20260918/）：图1 条形图改用章节均值口径并重排（order-parameter 0.810 居首）；图2 趋势图按 caliber 分型绘制（章节 4 维均值实线 / references 2 维虚线，消除混口径伪波动）；表格"最新得分"列改章节均值口径、references 分单独标注；叙述段落（两档分化、order-parameter 0.86 过线等误导性结论）全部修正
- 验证：`self_test.py --module` 全量通过；test_kanban_round_stats 22/22、test_micro_scheduler_rotation 28/28、test_heartbeat_kanban_merge、test_auto_acceptance 67/67 通过；`_section_mean_score` 对全库 9 课题逐轮均值与周报 sec 系列完全一致
- 更新 `VERSION` 文件 6.10.25 → 6.10.27

## v6.10.25 - 2026-09-17 负反馈告警时间戳同步清理（nfa_at 字段语义修复，方向 A）

- 背景：健康检查 25+ 轮持续观察（TTL 阈值达成 🔴 待裁决）——负反馈告警复位/清除时只清 `negative_feedback_reasons`，漏清 `negative_feedback_at` 时间戳，导致 nfa_at 残留历史首次触发时刻（实测 moire nfa_at=08-20 残 27 天 → human_queue waiting 虚高 667h；berry nfa_at=09-10 残 6 天 → waiting 虚高 148h），24h 冷却永远按旧时刻判定、无法从真实触发时刻重新起算
- 修复（方向 A 复位/清除同步清 nfa_at，冷却可重新起算）：
  - `scripts/adversarial/scoring.py` `record_monitor_history`：alert 复位（check_negative_feedback 返回 False）时同步 `pop("negative_feedback_at")`（原 v6.10.5 只清 reasons）
  - `scripts/proposal_lifecycle/cron.py` `clear_negative_feedback`：人工/自动清除告警时同步 `pop("negative_feedback_at")`
  - trim 分支（全局回升裁剪保留自身原因时告警仍挂）不处理——nfa_at 为真实首次触发时刻，清空会重置冷却延迟自愈，语义上保留（方向 A 笼统含 trim 但执行语义上保留更正确）
- 新增测试（`test_negative_feedback_global_recovery.py`）：
  - 用例 9 扩展：scoring 复位后断言 `negative_feedback_at` 已 pop
  - 用例 10 新增：`clear_negative_feedback` 清除告警后 持久化 state 中无 `negative_feedback_at`
- 验证：负反馈全局回升测试 16/16 通过；`self_test.py --module` 1723/1723 全量通过（此前基线 1720/1720 + 新增 3 断言用例，零回退）
- 更新 `VERSION` 文件 6.10.24 → 6.10.25

## v6.10.24 - 2026-09-16 MnPS₃ 评审团深度修改 M1：R1 对称性硬错修复 + R2 术语统一 + R3 引用核实 + HHG 产额论证

- 课题：general-berry-mnps3-rashba-20260816（平台期转评审团模式，M1 第一轮深度修改；输入 _manual-review-20260916-mnps3/ 三份评审报告 R1 科学性 / R2 语言表达 / R3 引用审校）
- R1 科学性 critical 全清：i-wave Hamiltonian 对称性改写（Δ_i(k)∝cos6θ，C₃/C₆ 旋转不变、镜面反射不变、C₄ 旋转变号，全篇删除 C4 口径）；三劈裂类型表重写（i-wave→六光子、d-wave→双光子、g-wave→四光子）；NiCl₂ 磁点群改正为三方 CdCl₂ 型（R-3m，点群 D3d）；VS₂ 统一为 VSe₂；τ_m 寿命统一 1–4 ns（对齐 Sahu [22] 实测）；THz 周期 333 as→333 fs
- R1 high/medium 落地：产额可测性论证（§3.4 补 0.01–0.1 MV/cm 场强下 (F/F₀)^(2n) 标度分析、归一化比值反演量对绝对产额不敏感、谷手性背景 σ⁺/σ⁻ 差分扣除）；d′ 换算修正（90%→d′<2.56）；带隙放宽 1.5→1.5–2 eV（type-II 界面电荷转移对齐，跨带 2–5 光子）；静态磁场维度取舍声明（§1.5：i-wave 判定依赖螺旋度指纹、T_N≈78 K 磁场窗口窄）；光应力机制修正（电子极化/虚激发响应非实载流子）；Δ 定义同口径化；Ezawa [14] 口径收敛；Rashba 阈值降级平台一实测标定
- R2 语言整改：波型术语统一 d-wave/g-wave/i-wave/p-wave/s-wave（16 处）；"磁序层"统一、"堆垛"→"堆叠"、"基线值"→"基准值"；同构排比差异化、口语化修正（背书→佐证、支点路线→单点路线）；jerk 电流括注、双主语修正
- R3 引用核实：[35] 虚构署名修正为 Horstmann 等（arXiv:2508.16422）；幽灵编号 [36]–[40] 补录并程序化重排；[36] 事实挂靠方向修正；[25] 作者链修正；[22] 补录 DOI 与卷期
- 修改文件：03_method/method-manual.md + 04_proposal/sections/ 五文件 + 05_review/（R8 产物归档与 _archive-targeted 迁移）+ 新建 _manual-review-20260916-mnps3/（三份评审报告 + manual-revision-20260916.md 逐项确认表）
- 清除评审团旗标（panel_review_requested=False，panel_review_clear_reason=评审团 M1 深度修改完成，退回轮转队列等待 R9 critic 独立评分检验）
- 遗留观察项：产额可测性最终定论依赖 R2 归一化产额谱数值；i-wave 载体成立与否依赖 R1 劈裂波型判定；[25] 预印本单锚点待增设第二独立校验源

## v6.10.22 - 2026-09-16 序参量评审团深度修改第二批：medium 清偿 + 四组文献检索核实 + 判据复述压缩

- 课题：general-order-parameter-ultrafast-readout-20260727（M1 修改 agent 第二批，处置第一批遗留：R1 medium 11 条 + R3 medium 5 条 + R4 medium 4 条全部裁决执行，R2 medium 71 条逐条复核关闭 69/补充处置 2，驳回 0；逐项确认表 05_review/manual-revision-20260916.md 追加第二批章节）
- 四组文献联网检索核实（零编造）：**补回 4 条**——[36] Long et al. 3D bulk-resolved g-wave altermagnetic order parameter in CrSb（Nature 656, 854—860 (2026), arXiv:2601.14526，𝒴₄⁻³=zy(3x²−y²) 摘要逐字核实，手册 §1.4"编号不预设"临时态解除+正文波型争议有据）；[39] Woodgate et al. CrSb/MnTe DLM 温度演化（arXiv:2603.15035，CrSb 远低于 T_N 自旋简并平滑恢复+MnTe 近 T_N 才恢复，逐句吻合后挂引 scheme/manual/rationale）；[37] Krempaský Nature 626, 517 (2024) + [38] Osumi PRB 109, 115102 (2024) MnTe ARPES 自旋分裂直接观测（0.8 eV @非高对称动量点，R3-14 补引+R3-13 先验实测锚点）；**未果维持去引用化 2 项**——Schwierz/Hou/Ren 三条候选 arXiv（2503.04431=Floquet Landau-Zener/2602.09738=[19]Ly 泵浦/2507.02673=近场阿秒）全部张冠李戴、Schüle 2606.12353 实测为 WSe₂ 无关论文，手册 §2.5 改记核实结果不作"内置对照"声明
- R3 medium 5 条：TiSe₂ 相变温度 205 K→约 200 K 全量 16 处统一（[7] 摘要级核实"CDW transition at T_c ≈ 200 K"，手册 §2.2 加密区间重划 198—202 K+判据 200 K±5 K，"Tyulnev 报道的 205 K 锚点"更正为"文献报道的相变温度（约 200 K [7]）"）；带隙分歧改挂 [39] 金属态情景证据（窄隙端检索未果维持标定初值定位）；先验上限锚点改 [38] 实测（六处）+Sb SOC 改"原子物理标准值+启动期 DFT 标定"（四处）；MnTe ARPES 补引 rationale 两处（只用可逐字核实结论，不引入 MnTe 波型争议）
- R1 medium 11 条：κ 阈值标定协议（θ̃=θ/σ_prior 归一化+≥100 组合成注入—MCMC 恢复+κ-成功率分档标定+验收归档，R1-22）；附录 B 热效应三通道判据（重频对照+瞬时反射率逐脉冲相关+脉宽依赖，闭合单脉冲内热化缺口，R1-33）；装置表/附录 A.3 补磁场方向行（R1-38 指代闭环）；σ 定义补奇次/总强度代理量+群论初判前置（R1-41，rationale/manual/full_review 三方同步）；"亚周期"空白宣称补发射过程 vs 测量能力限定（R1-30）；R1-24/25/34/37 复核关闭（第一批已消解）
- R4 medium：content 碎片化收敛（段合并 8 处+句合并 16 处：段落数 40→32、短段 19→14、句长中位数 38→46 字、>80 字句占比 9.5%→15.3% 进入范本区间）；scheme 判据复述指针化（σ×1.5—2.0 从 11→2 次、κ 18→10 次、"（即 0.75%—1.6%）"括号清零联动 R2-59、装置工程参数改"见方法手册装置表"，判据复述压缩约 520 字、被 R3/R1 新增引证内容 690 字部分抵消）；G2/G3/R3 前向代号补称谓定义（R4-10）；full_review 索引句断句（>120 字句归零，R4-14）；scheme 内部编号 §3/§4 漏网 2 处清理（R2-79 补漏）
- 全文超长句归零：四文件 >120 字句 21 处拆分（rationale 5/content 3/scheme 11/full_review 2），程序实测 0 处
- 程序化对账终态：references 39 条连续无跳号（新增 §9 组 [36]—[39]）；正文行内引用 57 处（rationale 42/content 12/scheme 19，40—60 区间）；零死条目/零超界/零一号两用/同章 ≤3 次；防回退 grep 21 项全过（[62]/[63]、±8%、27(2) meV、0.4 meV、205 K 等仅存手册版本日志合法存档；破折号/时间戳/自旋劈裂/altermagnetic/d 波形/交错磁交换/Yes-Go/本文全部归零）；新口径正向锚点（约 200 K 14 处、[36]—[39] 挂引、κ 标定协议、场向行、σ 代理量、热效应三通道）grep 全部在位
- 修改文件：04_proposal/sections/ 五文件 + 03_method/method-manual.md（v2.5→v2.6，版本日志含 v2.6 行）+ 05_review/manual-revision-20260916.md（追加第二批章节：核实记录 7 项/裁决表 20 条/复核结论/防回退/对账终态/遗留项终清单）；遗留项仅剩第 1 年实测标定回填与预研期检索事项（见确认表第八节）

## v6.10.21 - 2026-09-16 序参量评审团深度修改第一批：19 critical 全清 + 引用挂靠修复 + 波型口径统一

- 课题：general-order-parameter-ultrafast-readout-20260727（M1 修改 agent 裁决执行，输入 _manual-review-20260916 四份评审报告 R1 42/R2 102/R3 16/R4 14 条；critical 19 + high 45 共 64 条逐条裁决：采纳 47 / 改后采纳 13 / 更强方案消解 4（R3-1/2+R2-85/86 随 §9 删除）/ 驳回 0；另顺手修复联动 medium 22 条；逐项确认表 05_review/manual-revision-20260916.md）
- R1 科学性 7 critical 全清：CrSb 波型 d/g 跨模块互斥→d 波主口径（[17] 对称性分类为唯一可核实锚点）+ 手册 Long dHvA g 波证认降级开放争议记录（文献未入表、编号不预设、禁止编造）+ 基函数 d（E₂g）/g（𝒴₄⁻³）两套化经 dHvA 校准；Δ_d 基函数 cosk_xcosk_y 四方 B₁g 硬错→六角 D₆h E₂g + σ_z 自旋结构；TiSe₂ CDW 波矢 (0,0,1/2)→(1/2,1/2,1/2) 2×2×2；σ 噪声三套口径合一（σ_drift=0.5%—0.8% 实测为唯一口径、合格线 σ×1.5—2.0、SNR 公式自洽化 N_rep=25→≥7.5、单谱噪声另记 σ_spec）；FIM 450×450 概念错误→参数空间 N×N（7—9 维）+ 雅可比 14 次演化 + 算力对齐 1260 次合成演化降采样 4—6 GPU 月；先验 100—500 meV/0.1—1.0 eV 两套→统一 0.1—1.0 eV 五处同步；手册编号一号两用全清（[25]→[17]、[24]→[16] 等 20+ 处）+ 疑似虚构 [62] Cochran/[63] Sørensen 整段删除零编造 + Schwierz/Hou/Ren/Schüle 去引用化
- R1 14 high：Zeeman 0.4→0.8 meV（g≈2）+ B_SF≈√(2B_E·B_K) 判据；γ 三处统一 0.1—1.0（复算 3 μm 0.21—0.95/5 μm 0.12—0.57）；MnTe"跨相变"全部改近相变温度依赖扫描（290—310 K）+有序相内基线；Γ=ħ/T₂* 统一（T₂*=1—10 fs）；规范标签互换修正+生产改长度规范；电流/发射谱公式修正（P(t)/dP/dt/|ωFT[P]|²/能量分母）；能量—重频—焦斑两档联动（1 kHz×1—2 mJ / 10—100 kHz×10—30 μJ）；磁场切换<10 s 矛盾删除统一 30—60 分钟；损伤阈值三处统一（<0.8 下调/<0.5 降场强/<0.3 或预案不可达切 MnTe）；MSHG 区隔段新增（HHG 高阶三点增量）；带隙半金属情景分析前置第 1 年；θ₅ 改 c 轴倾角 0°±10°；No-Go κ>10⁴ 单条件触发；full_review 口径表新增方法手册列
- R2 10 critical + 21 high：范围声明自毁 2 处（CDW=对照体系/磁序=唯一主线）；检索时间戳 4 处删除；超长句 7 处拆分；altermagnet 磁序术语修复；Q2 补问题句；σ 一符两义拆分（FIM 记 δ）；"唯一受控差分维度"→主差分维度；序参量术语 8 种变体统一（d 波自旋分裂/d 波分裂幅度/删"形"）；altermagnet/交错磁/altermagnetic 统一+首现括注；自旋劈裂→自旋分裂归零；缩写首现全称（SOC/SBE/FIM/SNR/DFT/dHvA/OPA/OPCPA）
- R4 2 critical + 5 high：引用密度 121→59 处（[6]16→6、[7]11→5、[12]9→1、[27]8→4 等，35 条全嵌入零死条目）；references 元叙述 34.3%→约 1%（8 个分组导览段+§9 整节删除，QA 自检口吻归零，141→105 行）；破折号插入语 12 处清零；超 300 字长段重点拆分（scheme 742 字段→4 段）；文献堆砌句 2 处群组化；异常角标 6 处统一"（中子衍射实测 733(4) K [27]）"式；条目格式统一（半角括号/版本注置尾/[24] 作者计数与 [27] 变更史删除）
- R3 5 high：[35] 孤儿按方案一补引（content §2.4，守恒律表述以 [2601.12743] 摘要核实为据）；[7] 方法错记 SBE→含时薛定谔方程+现象学平均场（4 处统一含 SBE→TDSE 迁移说明）；[20] 亚周期→相干声子皮秒级（2 处）；R3-1/2 计数与边界声明随 §9 删除消解；联动 medium：[21] Kerr=Berry 曲率/Voigt=Néel 序各向异性、[25] 三细节弱化（多条频率分支/删电阻式磁体与四带细节）、[1] 体系归属、判据合成 ±8% 降级设计值（第 1 年实测校准，4 处同步）、27(2) meV 与 10⁻⁵ Ω⁻¹ 无出处数值删除
- 程序化对账终态：正文 59 处/35 条全嵌入/零跳号/零超界/零一号两用/零附注角标；references 35 条连续；防回退 grep 14 项全过（[17] arXiv:2105.05820、[24] 完整作者列表、损伤阈值口径、C₄ 语言、95% 压制等零回退；L139 计数自述随 §9 删除属裁决性状态变更，新实态已记入确认表）
- 修改文件：04_proposal/sections/ 五文件（rationale/content/scheme/full_review/references，其中四文件整体重写）+ 03_method/method-manual.md（31 处修改，v2.4→v2.5，版本日志含 v2.5 行）+ 05_review/manual-revision-20260916.md（新增）；遗留项（R1 medium 11 条/R3 medium 5 条/R4 medium 3 条/四组待检索文献）见确认表第九节，留第二批

## v6.10.19 - 2026-09-15 阿秒条纹评审团深度修改第二批：R1/R2 medium 清偿 + 风格节奏 + 冲突项统一

- 课题：general-attosecond-streaking-20260822（M1 修改 agent 第二批，第一批遗留 23 项处置：采纳 20 / 改后采纳 1 / 消解 1 / 驳回 0）
- R1 medium 物理核实 11 条全清：模拟总时长 5–10 ps→100–500 fs（谱分辨 h/T≈0.01–0.04 eV 自洽）；布鲁斯特角 70% 错误→镀膜平板 80° 高入射角分束（附 55.4°/13% 勘误）；Mo/Si（92 eV）→Cr/Sc 膜系 284–400 eV；动态范围概念拆分（计数比 ≥10³:1 与能量标定 ΔE/E≈1% 分列）；SNR 5–30→10–40 dB（10·log₁₀N）；G3 补 50 eV 选限依据；M6 六实测点→模拟端扩充 ≥12 点+覆盖域外禁外推；G5a α<0.05 独立阈值删除→修正项贡献范数 <1%；G1 补时间域指标（等效时间抖动 <25 as）；scheme §3.3+M6 新增束线时间预算（6 组纯采集 2–4 周、总占用 6–8 周）；R1-42 Cousin"误差超过 20%"经 arXiv:1710.02208 全文检索无出处→去归属改定性警示，判据改"第一步实测基准+目标降幅 ≥4 倍"（7 处同步）
- R2 剩余 medium：创新点同构模板删除（R2-58）；[21][24] 预印本补 [physics.atom-ph]（R2-66）；[11] 止页四源核实补 4799-4807（R2-67）；R2-68 随 [35] 删除消解；连接号 en dash 归一、manual 英文单位中文化（mJ/pulse 等）
- R4 风格节奏：括号插入语 142→6 处（rationale 29→2/content 27→1/scheme 86→3，单文件 ≤8 达标）；超 300 字段 21→0；scheme 碎段 43.9%→25%；rationale 60 字内句 48.0%→60.5%、超 120 字句三章归零；创新点 233/265/260→206/206/203 字
- 冲突裁决 R4-11 vs R2-34：符号体例统一 Unicode 上下标+行内文字表述，sections 三章 LaTeX 源码（$$ 块 2+行内 22）全部转写归零；跨章 § 指代维持第一批"研究内容/研究方案 §X.X"完整形式，文内自指改"本章 X.X 节"
- 程序化总验收：references 33 条连续、三章引用 41 次、单编号 ≤2、零死条目/零越界/零占位符；头部自述"16 条 48.5%"与实测一致；第一批 35 项已修项 grep 零回退（manual 内 5–10 ps 等命中均为"已废弃"勘误注记）；正向锚点（Cr/Sc、10–40 dB、≥12 点、束线预算、25 as 抖动、降幅 4 倍）全部在位
- 修改文件：04_proposal/sections/ 五文件 + 03_method/method-manual.md（13 处）+ 05_review/manual-revision-20260915.md（追加第二批裁决表/冲突裁决/核实记录/终态验收/遗留项）

## v6.10.18 - 2026-09-15 阿秒条纹评审团深度修改第一批：16 critical 全清 + R3 引用核实修复 + 口径统一

- 课题：general-attosecond-streaking-20260822（M1 修改 agent 裁决执行，输入 _manual-review-20260915 四份评审报告；critical 16 + high 47 共 63 条逐条裁决：采纳 49 / 改后采纳 12 / 驳回 2）
- R1 科学性 7 条 critical 全落地：水窗改学界惯例 284–543 eV 分低段/高段（删"符合分类惯例"句）；三层口径可行性论证层统一 8%–15%；IR 条纹场强 10¹⁴⁻¹⁵→10⁹⁻¹⁰ W/cm²（含 M3 条纹臂弱聚焦核算）；M6 图谱判据 ε 改对真值基准（TDSE 注入相位/人工相位调制回注，消除"修正越有效偏差越大"自毁）；2% 改设计阈值并补分波物理论证；TOF 窗 10–20 ns→≈500 ns（飞行时间 145–477 ns 自洽）；TDSE 步长 10 as→≤0.2 as（每光场周期≥50 步）
- R3 引用 5 critical + 6 high：[31]氦→氪张冠李戴、[6]虚构作者 Makabe→Li J,Yin Y（逐字取 Crossref 核实）、[1]瞬态吸收错挂改写、[10] 100 eV 凭空依据降级设计值、[15]Villeneuve 论证方向改写（角动量分量解纠缠）；死条目 [23][35] 删除 + 24–34→23–33 程序化重排（两阶段占位替换）；[32] 更新为 Ultrafast Science 2026 正式发表；M6 外部参照 Silva/Nat Photonics 误挂勘误为 Ardana-Lamas 再分析
- R2 语言 3 critical + R4 风格 1 critical：删检索时间戳/编辑元指令/13 行校验报告残留；引用密度 89→41 次（复述处撤编号、单编号≤2、33 条零死条目——"25 次内"子目标与零死条目+30-40 条区间数学上不可同时满足，按 R3>R4 优先级驳回数值子目标并记录在案）
- high 级口径统一：能量分辨率单一口径 4 eV@400 eV；靶材体系改氦单通道基准/氖氩线性响应（Ne 2s 阈 48.5 eV 修正）；备选 A 触发统一 40%（η=30%）；δφ_RMS 以 2π 归一、δ_cross 相位归一；Up[1−cos2ωt] 因子 2；延迟扫描 ±2–5 fs/≤100 as；防御性注记 42→9 处；主语统一"本项目"；主语/术语/能区叫法全文一致
- 程序化对账全部通过：references 33 条连续无跳号无一号两用、零超界、零死条目、零占位符；grep 防回退复核上轮 35 条文献真实性/时间线未回退，本轮旧口径（8%–10%/氦探测/Makabe/瞬态吸收挂条纹/Silva 等）残留归零
- 修改文件：04_proposal/sections/ 五文件 + 03_method/method-manual.md（22 处，仅 critical 口径相关节）+ 05_review/manual-revision-20260915.md（逐项裁决表与遗留项清单，medium 130 条转第二批）

## v6.10.17 - 2026-09-14 评审团执行推动环节补齐：panel_request 催办链 + 反思端周计划

- 检查结论：v6.10.14 分层策略已有"检测→调度止损→人工队列→clear 恢复"四环，但缺执行推动——队列条目无 waiting_hours（置标志时未记时间戳）→ 不参与 72h escalate 催办，评审团请求会永远静默挂着；且链路无周期性执行计划生成
- 修复 1（时间戳）：completion 置 panel_review_requested 时同步记 panel_requested_at；human_queue 的 panel_request 条目补 waiting_hours（旧数据回退 updated_at）→ 自动进入 escalate 排序与 72h 催办链
- 修复 2（催办标签）：lifecycle_monitor 的 type_names 补齐 panel_request=评审团 / cluster_stale=簇裁决 / strategy=策略（原 fallback 显英文）
- 修复 3（周计划）：反思端新增第 11 个任务 reflection_panel_plan（零 LLM）——每周生成 panel-review-plan-{date}.md（待评审课题按分数降序 + 等待时长 + 执行指引：跑评审团→clear_panel_request→恢复轮转→仍无起色则 redirect）；注册于 constants/jobs/pipeline 三层
- 链路终态闭环：平台检测 → 调度止损 → 人工队列 → 72h 催办 → 周计划盘点 → 人工运行评审团 → 清标志恢复自动循环
- 适配：test_weekend_pipeline_hardening artifact 锚点 9→10；test_panel_review_request 增至 22 用例（waiting_hours/escalate/任务注册/催办标签）
- 备注：与并行会话的 v6.10.15（停滞用例锚点）/v6.10.16（编排器 dry-run）无冲突，版本顺延
- 验证：--module 全量 1720/1720 通过；panel_plan handler 实弹落盘计划文件

## v6.10.16 - 2026-09-14 周末编排器 dry-run 零落盘修复：预览不再污染真实状态

- 问题（09-14 实证）：`weekend_orchestrator` 三个 `run_*_task` 声称透传 dry_run，但 `_update_job_status`（写 weekend-jobs.json 的 RUNNING/FAILED/DONE 终态与 attempts 计数）和 `pipeline.sync_stage_jobs`（含产物缺失级联重置、stage_status 推进，均落盘）不受 dry_run 保护——`--output --dry-run` 把 weekend_output 误标 failed（attempts 2→4），并因 `proposals-index.md` 产物缺失触发级联重置把 output/sync、weekly_report 落盘回 pending、stage_status 改 pending
- 处置：污染状态已从 09-13 auto.zip 精准恢复（保留 09-13 13:00 后 input 链 r17 正常更新，output/sync、weekly_report 含 result 完整还原）
- 修复：`run_input_task` / `run_output_task` / `run_reflection_task` 统一 dry_run 保护——预览跳过 `_update_job_status` 与 `sync_stage_jobs`；阶段未完成时 dry-run 返回 `note` 提示（不再误报 `success=False` + error，那是磁盘状态而非预览结论）；异常路径返回体标注 `dry_run` 字段
- 新增 `tests/test_weekend_orchestrator_dryrun.py`（19 断言：全 done 阶段双状态文件零写入 / 未完成阶段不误标 failed / sync 触发类级计数 dry-run=0 且真实执行=1 / 真实执行 weekend-jobs.json 正常推进 done / 异常路径 dry-run 零写入而真实执行照写 failed+attempts，wrapper 注入不触 LLM）；注册进 `--module` 静态清单
- 验证：单跑 19/19；test_weekend_pipeline_hardening 35/35；`--module` 全量 1716/1716（=1697 基线+19）；真实环境 `--output --dry-run` 前后 weekend-jobs.json 与 weekend-pipeline.json 字节级零变更

## v6.10.15 - 2026-09-14 停滞检测用例锚点修正：净工时口径下 87h 不触发

- 问题：v6.10.13 引入净工时口径后（扣周末小时），`test_stalled_clock_job_activity` 用例 1 的 fixture 锚点（job finished_at=87h 前 + updated_at=26h 前）实际净工时仅 ≈47h < 48h 阈值，按 v6.10.13 逻辑正确返回 0（不告警），但用例期望 1（应触发）→ 本轮 4h 窗口跑测试 1695/1696 失败 1 个
- 根因：v6.10.13 修改用例 3（净工时口径）时漏改用例 1——用例 1 描述的"87h 锚点"在新净工时口径下不触发告警（实际应触发的是 effective_h ≈ 47h），与用例语义"job 实际停滞 87h"已偏离
- 修复：把用例 1 fixture 锚点从 87h 调到 110h（净工时 ≈70h > 48h，任一运行日均稳定触发）；同步更新断言消息文本与用例 4 fixture
- 新断言：hours >= 80（仍按"job 真实活动小时数"口径，非有效工时；语义：旧 updated_at=26h 漏报 → 新口径读 110h job 时间戳触发）
- 验证：单跑 6/6 通过；--module 全量 1697/1697 通过
- 教训：净工时口径下任何时间锚点需重算——纯小时差已不能描述触发性，必须用 effective_h 反推 fixture

## v6.10.14 - 2026-09-13 平台期转评审团分层策略：0.70-0.85 主平台带止损

- 背景（09-13 链路效率复盘）：近 3 周 ~1500 job/110h LLM 机时只换来 3 次模块通过（2.3%）与 0 次质量晋级；3 次晋级全靠"最大轮数 8"逃生阀且决策包全 reject_lean、全被人工退回——"逃生阀晋级→退回→再爬 8 轮"是无效循环，主体是 0.70-0.85 主平台带课题（qgi/moire/new-idea 等，每课题末端空转 30-40h）。对比：评审团人工模式两轮单轮闭环 13 个 critical，效率远高于平台期自动循环
- 分层策略落地：爬坡期（<0.70 或持续提升）全自动；平台期（连续 4 轮评分 ∈[0.70,0.85) 且每轮 |Δ|<2%）转评审团
- 修复 1（检测）：completion.py 新增 PANEL_FLOOR=0.70 平台带检测（与 0.80+ 次优平台检测互补）→ 置 panel_review_requested + reason
- 修复 2（调度止损）：micro_scheduler._focus_proposal_for_slot 候选预过滤——平台期课题不再参与自动轮转（机时让给爬坡型课题）；list_by_status 携带标志字段
- 修复 3（人工可见）：human_queue 第六类 panel_request（建议动作"运行评审团模式深度修改"）
- 修复 4（恢复通道）：ProposalLifecycle.clear_panel_request（评审团完成后清除标志恢复自动循环，幂等，记录清除时间与理由）
- 新增 tests/test_panel_review_request.py（18 用例：平台带判定正反例/爬坡不误伤/高位平台不越界/调度过滤源码锚点/队列聚合/清除幂等）
- 验证：单跑 18/18；--module 全量 1697/1697 通过

## v6.10.13 - 2026-09-13 优化批次：周末停滞宽限 + kb_merge 实体过滤（含两轮误合并事故恢复）+ 引用降噪链路验证 + 保护簇补检索

- P0-1 周末停滞告警宽限：停滞检测抽为 `_check_proposal_stall` + `_weekend_hours_between`——停滞时钟扣除窗口内周末小时（本地时区周六/周日，净工时口径），周一恢复后真实停滞仍触发。实测 09-13：8 条未解决告警中 5 条为周末设计性"停滞"批量误报
- P0-2 kb_merge 同名不同实体误合并（事故级）：`_detect_duplicate_concepts` 纯 title 分组把模板标题下不同实体判为重复——**两轮事故**（09-06 与 09-13 反思 kb_merge）：moire 课题报告/版本页被并入 qgi（LLM 融合模式也被同名骗过）、6 个不同日期的讨论页被并成 stub。处置：①8+3 个受害文件从 git 历史恢复（02d65573 基线）②`detect_merge_pairs` 加 `_entity_key` 实体一致性过滤（文件名首段含数字=arXiv ID 同实体；纯字母首段拼第二段区分 general-moire vs general-quantum、讨论-20260619 vs 讨论-20260702）③修复后候选组归零验证（真重复 arXiv 组 09-06 已正确合并为 stub，模板组全部排除）
- P1-3 引用降噪链路验证：`load_review_feedback_for_optimization` 确认评审团"引用降噪"策略文本已在注入链（qgi/key-transient 抽样注入 188-248 字符含策略）——周一 writer prompt 自动携带，无需改动
- P1-5 保护簇定向补检索（4/4 成功）：少阿秒脉冲串/超快磁化/太赫兹谐波/时空涡旋各补 1 篇对口论文（Einstein-de Haas 超快磁化、Mott THG 等高相关）入库+挂簇，成员 2→3、保护状态自动解除、人工队列清零——下轮 topic_match 成员 ≥3 门槛已过，进入 new 评估（LLM 知识卡+方向相关+相似度三关）
- 适配：test_stalled_clock_job_activity 用例 3 改净工时口径（140h 锚点，附"净工时"消息断言）
- 验证：--module 全量 1679/1679 通过；受害文件恢复后 grep 无 merged_into/merged_from 残留

## v6.10.12 - 2026-09-13 周末输入/输出双向优化：borderline LLM 语义归簇 + 输出萃取链路加固

- 背景（09-12/13 周末实测）：输入端三天 assigned=0——50 条摘要与 55 簇的纯 Jaccard（阈值 0.22）全失配，orphan 池膨胀至 471（42 天清理=知识流失），4 个保护簇等不到第 3 篇；输出端 daily 萃取 53 来源 0 概念 0 方法（output_jobs._llm_json 是弱版本地副本：无 prefer 标签→16384 放宽不生效、无围栏剥离降级、无截断报因，glm 空输出时段静默归零）
- 输入修复（borderline 语义仲裁）：assign_summaries 加 llm_arbiter 可选回调——最佳候选分 ∈ [0.12, 0.22) 的摘要交 LLM 做概念级归属判断（"量子度规反演"摘要 vs "Berry 曲率谱学"簇这类跨术语同源场景），True 归入（method="llm"）、False/异常/不可用保守 orphan（零成本兜底）；仲裁回调由 input_jobs._llm_assign_arbiter 注入（clusters.py 保持纯函数可测）；保护簇直接受益（borderline 相关的第 3 篇可入簇）；高相似/低相似两端不调 LLM（成本控制）
- 输出修复：①output_jobs._llm_json 改委托 input_jobs 加固版（prefer="weekend_output"）②TASK_MAX_TOKENS 补 weekend_output: 16384 ③萃取来源 6→8 条 ④萃取全空时 WARNING（区分"LLM 失败"与"确实无可萃取"，不再静默 0）
- 实弹验证：borderline 仲裁对 3 个简报类候选正确拒绝（保守性 ✓，简报不属研究簇）；下次 cluster_assign 运行即生效
- 新增 tests/test_weekend_io_enhance.py（18 用例：Jaccard 路径不调 LLM/仲裁 True-False-异常三态/低相似不浪费调用/无 arbiter 回归兼容/_overlap 分母簇侧口径校准/委托 prefer 传递/来源 8 条）
- 验证：单跑 18/18；--module 全量 1694/1694 通过

## v6.10.11 - 2026-09-13 auto 路由分支补传任务级 max_tokens（v6.10.9 修复未完全生效）

- 问题：v6.10.9 的 TASK_MAX_TOKENS 放宽（weekend_input: 16384）只接到模式 A（强制指定）分支，模式 B（auto 自动路由，weekend 全部调用走此路径）漏传 max_tokens → 长摘要仍按默认 4096 截断。v6.10.9 部署后实测（09-13 09:03-20:41）：空响应形态已归零（27 次空 content 被拦截降级 ✓）但截断仍 11 次（"疑似截断" 6 + Unterminated 5，输出 800-1600 字符即断）
- 修复：模式 B 的 provider.call 补传 `max_tokens=TASK_MAX_TOKENS.get(prefer or "")`
- 验证：源码断言 auto 分支含传递 ✓；实弹长文任务 glm 89.7s 输出 667 字符 core 完整 ✓；--module 全量 1676/1676
- 教训：router 双分支（强制/auto）的参数传递需对称检查——同款"改一处漏一处"已第三次出现（v6.9.75 max_tokens 表、v6.9.77 coverage、本例分支漏传），建议后续在 call_llm 出口加统一参数日志


## v6.10.10 - 2026-09-13 human_queue cluster_stale proposal_id 字段补齐：监控/控制台/自检不再 KeyError

- 问题：v6.10.7 新增的第五类 cluster_stale 条目 dict 缺 `proposal_id` 字段（仅含 `cluster_id`），但生产端任何以 id 维度遍历 items 的消费者（human_queue 自检 L331 / test_auto_acceptance HumanQueueTests L672 / `--module` 全量回归）都会抛 KeyError。触发条件：production clusters.json 中存在 `pending_human_review=True` 的 open 簇——09-12 lc-weekend-weekend-reflection 起累积至今已 4 簇（cl_20260815_82c665/282c86/31d4a2/cb5278），致 09-13 20h `--module` 1659/1660（失败 1：HumanQueueTests KeyError）+ human_queue 自检崩溃 + 控制台 `/api/console/human-queue` 实际不可用（前端 `escapeHtml(item.title || item.proposal_id)` 兜底不崩溃但显示 `undefined` 标题）。09-12 16h 报告 1638/1638 通过是因为当时 dbaa9a2a 部署后尚未累积 pending_human_review 簇
- 根因：`v6.10.7 _pending_cluster_reviews` 设计偏差——以 cluster_id 作为唯一标识键，未考虑 production consumers 普遍依赖 proposal_id 的语义槽位一致性
- 修复 1（生产）：`_pending_cluster_reviews` 返回 dict 补 `proposal_id=cluster_id`（共享 proposal_id 语义槽位 + 保留 cluster_id 供专门消费者区分），与 review/activate/negative_feedback/strategy 四类同一字段命名
- 修复 2（自检）：`_self_check` 由严格相等改子集断言（`_pending_cluster_reviews/_pending_strategy_suggestions/_pending_feedback_review` 三处外部读生产文件，self_check 无法 mock；只要测试项必含 + escalated>=1 即可）
- 修复 3（测试）：test_auto_acceptance.HumanQueueTests L672-676 由严格相等改子集断言（_pending_cluster_reviews 同上原因）
- 修复 4（回归）：test_cluster_stale_protection 用例 7 增 cluster_stale 条目 `proposal_id in it and it["proposal_id"]` 与 `proposal_id == cluster_id` 双断言，防回退
- 验证：单跑 + 8 新增；--module 全量 1668→1676 通过（human_queue 自检 ✓；待人工队列聚合 ✓；簇 stale 清理保护 ✓）
- 防回退：v6.10.7 同款"测试与生产文件未隔离"病根——后续 human_queue 类回归须显式 mock 三处外部读源或采用子集断言

## v6.10.9 - 2026-09-13 LLM 解析失败三层修复：空响应拦截 + weekend_input 截断放宽 + 未闭合围栏剥离

- 问题：周末输入端 deep_digest/summarize LLM 解析失败频发且三形态（09-12/13 实测 >12 次）：①空响应——glm 200-OK 但 content 空串（间歇性/疑似 reasoning-only），②Unterminated string 截断——长中文摘要超 max_tokens 被切，③```json 开头围栏无闭合——截断的另一表现，尾部 ``` 被切掉。每轮 30 篇深读部分摘要静默丢失（r13 仅产出 4 条），输入端转化率受损
- 根因 1（空响应穿透三层）：`_call_api` 取 content 不校验空 → router 无异常返回 → gateway `result or ""` 报 ok=True → 调用方解析必败且**不触发 provider 降级**（空响应被当成功）
- 根因 2（截断）：TASK_MAX_TOKENS 表（v6.9.75）只放宽了 kb_distill_deep: 16384，weekend_input 标签漏配 → 默认 4096 → 推理模型 reasoning+长正文超限——与 v6.9.77/v6.10.8 同款"修一处漏一处"模式（本表内注释当时已记载该病根）
- 根因 3（围栏）：v6.10.1 降级链的围栏正则要求闭合 ```，截断响应只剩开头围栏时不匹配；大括号降级也因截断无闭合 } 失败
- 修复 1（router）：`_call_api` 空 content 显式抛 RuntimeError（含 finish_reason 诊断信息）→ 进入 except 分支 → failure_count+1 → 自动降级到下一 provider，空响应从"静默成功"变"可重试失败"
- 修复 2（router）：TASK_MAX_TOKENS 补 `weekend_input: 16384`（与 kb_distill_deep 同档，根治长摘要截断）
- 修复 3（gateway）：`llm_complete` 空 content 兜底拦截返回 ok=False（CLI 类 provider/漏网路径双保险）
- 修复 4（解析层）：`_llm_json` 前置剥离"开头围栏无闭合"形态（```json 前缀 sub 后再走原降级链）；有 { 无闭合 } 时明确报"响应疑似截断"（可观测性，区分空响应/截断/格式三类）
- 新增 tests/test_llm_parse_hardening.py（12 用例：三形态解析/TASK_MAX_TOKENS/router 空 content 抛错/gateway 兜底/v6.10.1 前言尾注降级不回归）
- 验证：单跑 12/12；--module 全量 1661/1661 通过

## v6.10.8 - 2026-09-12 覆盖率统计口径修复：看板 4.9% 假象 → 真实 81.8%

- 问题：sync_engine 每日看板的 `coverage_pct` 用文件名 stem 精确匹配 raw/papers 与 wiki/papers，而蒸馏页命名把 arXiv ID 点号改为下划线（`2604.03983`→`2604_03983`），1485 篇 wiki 蒸馏页仅 56 篇恰好同名——真实覆盖 80.7% 被报为 4.9%，且"走低"（5.1%→4.9%）实为分母增长快于同名条目的假象，误导出"深读断流"诊断（09-12 复核推翻）
- 根因溯源：同一个坑 v6.9.77 已在 reflection_jobs._calculate_kb_health 修过（当时真实 98.7% 被报为 43%，注释在案），但修复未同步到 sync_engine 的每日看板统计——两处覆盖率代码各自演化
- 修复：新增 `compute_kb_coverage(raw_dir, wiki_dir, used_sources=None)`——统一 source_raw 口径（蒸馏页 frontmatter 的 source_raw 纯文件名 vs raw 文件名，与 reflection v6.9.77 / kb_distill / kb_health 告警三处同源），used_sources 可注入（可测），读取失败或为空回退旧 stem 匹配（防御性）；[3.6/5] 同步段改调此函数
- 对账验证：修复后真实缺失 208 篇 ≈ 蒸馏积压清单（今晨 218，当日 cron 又消化 12，自洽）；归一化匹配独立口径 80.7% 交叉印证
- 运维：看板 kb_metrics 立即刷新（coverage 4.9%→81.8%，missing 1085→208）
- 新增 tests/test_kb_coverage_source_raw.py（11 用例：source_raw 计数/命名差异下旧口径零命中锚点/空目录不除零/回退分支/前缀注入防虚高）
- 验证：单跑 11/11；--module 全量 1649/1649 通过

## v6.10.7 - 2026-09-12 簇 stale 清理保护：高相关待积累簇转人工裁决

- 问题：`close_stale_clusters` 对超 4 周无更新的 open 簇一律自动 closed，"2 成员 + 高相关"簇（topic_match 判"成员 <3 继续积累"，差 1 篇过 new 门槛）的跨周积累会被静默作废（实测 09-12：4 个高相关簇卡 2/3 成员 26 天，距 stale 线仅 2 天；cluster_distill 知识卡因此连续零产出，新课题孵化管道实质空转）
- 修复 1（信号回写）：`run_input_topic_match` defer 时回写 `route_signal` 到簇注册表——`_defer_signal` 用"成员 N < 3"正则精确判定 accumulate（off_topic 理由常含"继续积累"字样如"主题不对齐，应继续积累等待范式嫁接"，关键词判定会把不对齐簇误标，实测今晨 3 例）；信号随 routes 落盘并在 topic_match 末尾统一回写
- 修复 2（保护分支）：`close_stale_clusters` 返回值改 dict `{closed, protected, protected_ids}`——accumulate 簇超期不关闭，标记 `pending_human_review` + `stale_notified_at`（幂等不覆盖时间戳），保持 open 可继续吸收；off_topic/无信号簇照旧关闭（不确定不保护，防僵尸簇逃逸）
- 修复 3（人工可见）：①`cluster_assign` job 对 protected 簇落盘 `stale-protected-{date}.json` + WARNING 日志；②`human_queue` 新增第五类 `cluster_stale`（`_pending_cluster_reviews` 读 pending_human_review 的 open 簇，建议动作"定向补检索凑第 3 篇或关闭"），控制台队列展示 + monitor 催办
- 运维：存量 7 个 open 簇按今晨路由结果一次性迁移信号（4 accumulate 高相关簇将获保护 / 3 off_topic 簇周一正常关闭——维格纳晶体、无线能量、量子点主题不对齐，积累无意义）
- 适配：`test_input_clustering` stale 用例改 dict 返回值断言；新增 `tests/test_cluster_stale_protection.py`（25 用例：保护/关闭/未超期/幂等/linked 豁免/信号判定正反例/人工队列聚合）
- 验证：单跑 25/25；--module 全量 1638/1638 通过；真实数据干跑确认周一 cluster_assign 运行时保护分支自动生效（当前 26 天 < 28 天阈值未触发）

## v6.10.6 - 2026-09-10 api_idle_spin 根治：gap JSON 引号修复 + 跨章节串读修复 + writer 挣得式恢复

- 问题 1（api_idle_spin 根因）：LLM 在 gap_identify 的中文 claim 中嵌套 ASCII 引号（如 `论证"光源—样品—谱学—理论—反演"五环`，应为全角），使整段 JSON 解析失败，前两级解析全挂后掉入空 gaps 兜底——真实缺口被静默丢弃，下游 lit_search/lit_read/lit_note 拿空关键词反复跑 API，触发空转告警（实测 09-10 bsv r2 scheme：2859 字有效输出仅因引号全灭，3 个 job 被标记 api_idle_spin）
- 修复 1：executor 新增 `_repair_json_inner_quotes` 启发式状态机（字符串内的 `"` 若其后首个非空白字符非 `:,}]` 则转义），修复后含花括号深度扫描二级兜底；挽救成功记录日志（含缺口条数），失败才走空 gaps 兜底
- 修复 2（跨章节串读）：gap 文件写入时 `data.setdefault("section", section_key)`，lit-gap 报告头部写入 `## 章节` 标记；lit_search/lit_read/lit_note 优先读本章节文件，旧文件无标记时回退最新（向后兼容）——此前 rationale 章节的 lit 链会串读 scheme 章节的 gap，检索方向错位
- 修复 3（空转误报）：health_sensor 新增 `LOCAL_FAST_STEPS = {"lit_note"}`——纯本地步骤（regex 抽取 + 本地关联，实测 ~1s）秒级完成是正常行为，计入空转检测只会制造误报；done 扫描时跳过
- 修复 4（writer 分数恢复）：对抗系统存在结构性负漂移——惩罚为固定值（质量门 -2/-5、违规 -5/-8）而奖励按比例（20×monitor 增量、3×问题修复），critic 有 RECOVERY_BONUS 对冲自身漂移，writer 无对称机制（实测全局分 100→42.9，近 10 轮累计 -32.8，且拖累多课题负反馈连坐）。新增挣得式恢复：全局分 <50 且本轮 delta>0（实质改进才给，与 critic 版"低位不恶化即奖励"语义区分——writer 典型病症正是表面修改持续扣分）、近 48h 无严重违规（severe/critical 或单条 ≤-8）时追加 +5 分，`WRITER_RECOVERY_MAX_SCORE=50` 自限防滥用
- 运维：人工清除 order-parameter 负反馈告警（连坐课题，v6.10.5 回升感知的前置验证）并刷新人工队列；重置 bsv scheme 链 3 个空转 job 交 worker 重推
- 新增 tests/test_gap_json_repair.py（9 用例：内嵌引号/转义保留/结构字符边界/自然语言兜底/花括号扫描等）、tests/test_writer_recovery_bonus.py（13 用例：加成触发/48h 窗内外/严重违规阻断/自限边界 50/无违规记录/对称场景等）
- 验证：--module 全量 1612/1612 通过（新增 26 用例全绿）

## v6.10.5 - 2026-09-10 负反馈连坐修复：全局 agent 分回升感知解除

- 问题：负反馈条件"writer/critic 全局分数低于 50"使用跨课题共享的全局分（agent-scores.json 单一实体），任一课题惨烈对抗拖破全局分会连锁触发健康课题告警并冻结流转（实测 09-09：qgi 把 writer 拖到 45.6，mos2/order-parameter/key-transient 被连坐，4/8 课题挂警；自动清除额度每课题仅 1 次且早已耗尽，只能等人工）
- 修复 1：lifecycle/utils 新增 global_recovery_clear_plan——告警原因含全局类条目且对应 agent 全局分回升 ≥50 时：无剩余原因则整条解除（clear），有课题自身原因则裁剪保留（trim）；读不到分数保守视为未恢复
- 修复 2：lifecycle_monitor._auto_heal_negative_feedback 在 24h 冷却路径前接入回升解除——不占 negative_feedback_auto_clear_count 额度、不降级 idea_review_required（被连坐非课题自身问题，不应惩罚性退回设想评审）； healed 记录带 kind 区分
- 修复 3：adversarial/scoring record_monitor_history 在 alert 复位时同步清空 negative_feedback_reasons——旧实现只在 alert=True 写入，复位后历史原因残留误导 monitor 自愈/human_queue/前端
- 新增 tests/test_negative_feedback_global_recovery.py（13 用例：clear/trim/未恢复/纯自身/无告警/critic 对称/缺分数/边界 50/复位清理）
- 验证：单跑 13/13；--module 全量 1577/1577 通过；无参数全量 1731/1734→1744/1747（3 个失败为 v6.9.56 已记载的跨套件模块污染预存问题，移除新测试后失败数不变，与本次改动无关）
- 生效路径：monitor 每小时跑 _auto_heal，writer 分回升过 50 后 mos2/order-parameter 自动解除、key-transient 裁剪保留 monitor 原因；moire 为纯自身原因不受影响

## v6.10.4 - 2026-09-09 writer prompt 人工优化：引用纪律强化 + 三态响应 + 验证性自述红线

- 背景：writer-critic 分差 97+（45.6 vs 148.6），writer 20 条违规集中三族——引用杜撰（虚构作者串/DOI 错构/死链遮盖）、表面修改（批注清理替代实质响应）、统计自述失真（自称 grep 实测不可复现）；prompt_optimizer auto 按 v6.9.70 设计暂停，走人工路径
- 修复规则冲突：原"文献不足用占位标注"与"禁止占位符"打架（writer 被逼杜撰），统一为文献纪律四步——检索核实/去引用化/标注待补/禁止凭记忆生成任何引用字段；禁止以 Erratum/脚注/模糊化作者遮盖被指认的杜撰条目
- 运行纪律升级：实质修改改三态响应（已修改+原句/部分修改+障碍/驳回+依据，禁止沉默跳过）；新增验证性自述红线（统计数字当场重算，禁止声称未执行的验证）
- 清理过期 auto 段 2 个（08-21 empty-draft 段系调度器指令错位入 writer、表面修改段与运行纪律 1 重复），保留 09-02 模板句式段（有独立阈值）；净增 319 字节（12.9KB→13.2KB，规避 v6.9.70 膨胀教训）
- 备份：~/.hermes/profiles/writer/SOUL.md.bak-20260909-manual-opt；critic 侧不动（148 分为 monitor 核实的真实表现，分差根因在 writer 失分）
- 验证：AUTO_TAG 正则配对 1/1 完整；四条新规则 grep 在位

## v6.10.3 - 2026-09-09 晋级机制口径修复：逃生阀有效分判定 + 晋级方式打标 + 收敛自动晋级降级

- F1 last_score 口径修复（P0）：references 为 2 维专用口径且每轮固定收尾，顶层 last_score 系统性等于其单模块分（实测 9 课题中 7 个末条=references），逃生阀质量警告此前用它比较会豁免（attosecond 1/5 模块以"无警告 0.85"达标观感进队）。新增 `_effective_score()`（monitor 独立分 > 最近 4 维章节分 > last_score 兜底），条件2/条件3 警告改用整篇有效分并标注口径；score_history 条目新增 caliber 字段（references_2d/section_4d）
- F2 晋级方式打标：done 结果与 prop_state 新增 promotion_kind（all_sections_passed / escape_max_rounds / escape_no_improvement / quality_declining），executor 晋级时落盘，review_dossier 决策包输出并在 reasons 首位标注"晋级方式：逃生阀…"（不改 verdict 规则）
- F3 收敛自动晋级降级为人工信号（用户裁决 09-09：晋级条件偏松）：连续 3 轮 ≥0.85 收敛分支不再 done=True，改为与次优平台同款 quality_warning 落盘（"建议人工评估是否晋级验收"）；该分支与天花板体系冲突（32 轮实测 max 0.81 零触发），防御性保留检测逻辑
- F5 prompt_optimizer 停摆定性：非故障——v6.9.70 有意暂停（auto 只增不减/审计失真/writer SOUL 膨胀分数净-27），v6.9.87 加入口守卫默认关闭。analyze 链路健康（数据源+10 prompt 文件），本次产出 1 条 HIGH 建议（writer 禁止占位符残留）待人工确认；恢复 auto 需显式 PROMPT_OPTIMIZER_ENABLED=1，建议维持人工确认模式
- 验证：py_compile 通过；test_quality_ceiling_convergence 16/16（收敛断言更新为降级语义）；全量 --module 回归 1577/1577 通过

## v6.10.2 - 2026-09-09 评审团 20260909：attosecond M1 修订 24 处 + qgi 退回 pass5

- attosecond（0.85 达标待验收）：R1 重复段删除 + R2 自指/称谓清理 19 处 + R4 长句拆分 4 处；程序化验收长句=0/自指=0/编号对账 30-30 干净；遗留 5 项转 feedback-2（human_feedback_count 1→2）
- qgi（0.575 未达标）：修正引用红线——references[9] 题名失实（真名 "Quantum metric in step response", PRL 134,106403）+ scheme 创新点 7.1/7.2 两处引用语境同步修正；submit_feedback(major_revision) 退回 optimizing（rounds 归零，pass 4→5，8 条结构化意见注入下轮）
- 引用核实方法论沉淀：WebSearch 对 arXiv 编号不可靠（26 条误报），应走 arxiv.org/doi.org/Crossref 直查；APS 2025+ DOI 为短码注册形式，构造式 DOI 不存在，勿机械改写（见 memory/agent-feedback-20260909.md）
- 产出：research_proposals/_manual-review-20260909/（总报告+四维 panel+执行报告）
- 验证：编号对账两课题 0 越界/0 死条目；grep 复核关键修复无回退

## v6.10.1 - 2026-09-06 深读解析健壮化：JSON 降级提取 + 超时 90→120s

**背景**：新周末编排首日实测 r1/r2 深读各 5/10 篇失败（50%），根因定位——
LLM 调用本身成功（glm 42-63s）但返回 JSON 外带前言/尾注或空响应，旧解析
直接 json.loads 整段失败且不记录原始输出（"Expecting value: line 1 column 1"）。

**修复**（input_jobs.py _llm_json）：降级提取链（markdown 围栏 → 首个 { 至
末个 } 子串）；解析失败记录原始响应前 200 字符；deep_digest 单篇超时 90→120s
（10 篇×120s=1200s，stale 阈值 3600s 内安全）。

**验证**：复测此前失败源（2506.19286）43s 解析成功；定向回归
weekend_input_rounds / input_summarize_shapes / weekend_pipeline 全过。

## v6.10.0

## v6.10.0 - 2026-09-06 T3 方法学专题：methods_settle 轮内沉淀+按需回原文定点融合+方法页反哺 writer/critic

**范围**：T3（方法学专题模块）。T1（ae38be66 输入链多轮化）、T2（16cd6173 维护链）
已提交。功能合入构成 MINOR。

**methods_settle job（weekend_pipeline/methods_jobs.py 新模块）**：
- job `input_methods_settle`（step=`methods_settle`，job_id 同名），插入位置
  cluster_distill 之后、topic_match 之前；topic_match 依赖相应改为
  methods_settle（input 轮次结构六步→七步，rounds 判定与 docstring 同步，
  旧 state 依赖由 sync_stage_jobs 的依赖刷新机制自动迁移）；
- artifact `methods-settle-{date}-r{round}.json`（轮次号与 deep_digest 同格式，
  {round} 按 job 自身 round 字段格式化参与产物校验）；空 leads 也落空产物
  （"done 必有产物"不变式）；dry-run 零落盘（词表生成 persist=False 同口径）；
- handler 逻辑（消费 T1 deep_digest 的 method_leads，文献消化以简报为主源、
  方法学整合为附加产品）：
  1) 读本轮 summaries（state.input_round.last_summaries_path，多轮/跨天不错位）
     全部 method_leads；
  2) 按方法词表（memory/config/methods-lexicon.json，文件优先可手工编辑；
     初始 28 词条从 18 个现有方法页映射 + 常见强场超快方法词新页候选生成，
     每词条 {slug, page, aliases:[], zh:[]}）归组到方法页；无匹配页时同类
     宽松合并（SequenceMatcher ≥0.6，"海森堡不确定"与"…原理"同义不同形可聚）
     ≥2 条且跨 ≥2 源新建页（英文 slug 优先提取名中最长英文段，纯中文名
     hash 短码兜底；title 用中文 display 名）；散条 unmatched 仅计数不建页；
  3) 按需回原文：source_id 提取 arxiv id（兼容 `paper:2007-0707.4192-slug`
     长 stem 与 hermes 短 stem）→ `_text_cache/{点号换下划线}.txt` 定位
     方法段落——方法名/别名/参数符号 + Methods|方法|实验装置 章节标题启发式
     找命中行，取前后共 ~3KB 窗口（行对齐限 200 字符回溯，PDF txt 无换行
     巨行不吞窗口；最多两窗）；无 txt（DOI 入库期刊等）仅用简报文本；
  4) LLM 融合（复用 input_jobs._llm_json 通道，weekend_input 优先 GLM）：
     输出结构化 JSON（principle/params/boundary/works），程序格式化进页面
     结构化专区（`<!-- methods-settle:v1 -->` 标记包裹，置顶；专区外既有
     正文原样保留不删改）；LLM 不可用或失败降级"附录式追加"（专区最小
     结构 + 证据日志标 fallback，链路不失败）；数值必须来自证据文本；
  5) frontmatter：updated_at、settled_count+1、growth_stage 按次数晋升
     （seedling→growing≥2 次→mature≥4 次或正文 >1500 字；需求原文的
     sprout 对齐 growth_engine 现有 growing 阶段名，避免第四阶段值分裂
     晋升链；mature/自定义值不降级）、confidence 随一手原文证据 +0.1
     （上限 0.9）、词条别名并入 frontmatter aliases；
  6) 页面写入优先 kb_wiki 统一门面（防双 frontmatter + 图谱同步），
     门面异常降级 kb_text frontmatter + tempfile+os.replace 原子写；
     每轮融合页上限 8（控 LLM 成本），证据日志保留最近 30 条防膨胀；
  7) 产物 json 记录每页融合条数/回原文次数/fallback 标记/晋升后
     growth_stage 与 settled_count，overflow_groups 记录超限组数。

**方法页反哺 optimizing 课题（proposal_lifecycle/optimize.py 消费端）**：
- `_load_methods_reference_block`：writer 派活 scheme 聚焦轮时按当前课题
  关键词（title + 00 号研究设想前 2000 字）词表反向匹配方法页（命中词数
  降序），以【方法学专题参考】块注入 prompt（每课题最多 max_pages 页、
  每页摘要 ≤max_chars 字：结构化专区优先，无专区回退正文并剥离
  frontmatter），说明"研究内容与可行性论证可直接引用这些已验证方法与
  参数，引用时标注来源文献"；
- `_methods_critic_hint`：critic scheme 聚焦轮加一行提示（不注入全文，
  只提示方法页存在与 knowledge/wiki/methods/ 路径，可依据参数表核对
  申请书数值）；
- 注入量控制与开关：memory/config/methods-inject.json
  （{enabled:true, max_pages:3, max_chars:400}，默认开）；开关关/零命中
  返回空串不注入；rationale/content 等其他章节轮不注入；
- 不导入 weekend_pipeline（研究管线保持 weekend_pipeline →
  proposal_lifecycle 单向依赖，词表 json 两端同源读取）。

**词表与配置初始化**：
- memory/config/methods-lexicon.json（28 词条；文件存在即以此为准，
  种子不再覆盖——scope-terms.json 同语义）；
- memory/config/methods-inject.json（注入开关，研究管线消费端同源读取）。

**真实工作区验证**：
- settle dry-run：今日 r1 产物 5 篇 21 条 method_leads → 归组 3 页
  （floquet-engineering 词条组 2 条 / RABBITT 1 条 / 同类新页候选 1 组），
  散条 16（Berry-Maxwell/RMT/Wilson 圈等单条不达门槛），零落盘；
  arxiv 源（2602.22137）可回原文定位，DOI 源（s41567）正确降级仅简报；
- 注入端：9 个 optimizing 课题实测——key-transient-quantum-phase 命中
  3 页（瞬态吸收光谱/波形控制/阿秒条纹相机，语义高度相关、frontmatter
  零泄漏），quantum-geometry-inversion 与 moire-strong-field-probe 零
  命中不硬塞。

**测试**：
- 新增 scripts/tests/test_weekend_methods.py（82 断言）：七步链注册与
  依赖、词表归组（同义合并建页/严格门槛）、假 txt 定位窗口（命中/边界
  对齐/连续子串/无命中空串/arxiv 点号→下划线映射）、settle 端到端
  （LLM 融合专区+frontmatter 晋升+confidence、二轮 growing 晋升与专区
  替换不叠加、LLM 失败降级 fallback 标记、空 leads 空产物、dry-run
  零落盘）、注入端（块构造/开关/截断/零命中/writer scheme 轮含块
  rationale 轮不含/critic scheme 轮提示行）——隔离目录 + stub LLM/hermes；
- self_test --module 登记新套件；结构断言随七步链同步
  （test_weekend_pipeline 6→7、test_input_clustering expected 列表、
  test_weekend_input_rounds 七步 done_state 与跨周 pending 7、
  hardening 预览/锁粒度 job 数 6→7、产物齐全用例补 methods-settle 产物）；
- 回归：--module 1575/1575（基线 1492+82+1 结构同步）、--scenario 16/16、
  --persona 38/38；定向复跑 T1 input_rounds 66/66、T2 maintenance 81/81、
  weekend_pipeline 45/45、hardening 35/35、input_clustering 108/108；
- py_compile 全量通过；methods_jobs/rounds --self-check 通过。

**遗留风险**：
- 词表归组依赖方法名的可匹配性——LLM 生成的中文长名（"半经典动力学方程
  （贝里曲率反常速度项）"）多数进 unmatched 等待同类凑对或人工补词条；
  散条积累观察一两周后按高频补词表；
- _text_cache 覆盖 852 篇，DOI 入库的期刊论文（Nature Physics 等）无
  txt 只用简报线索，融合证据薄（confidence 不加成），待 PDF 补采；
- 方法页专区与既有正文并存（专区置顶、旧正文保留）——growth_engine 的
  内容字数口径含旧正文，>1500 字门槛对既有长页（RABBITT 等 mature）
  无副作用（不降级），但 seedling 短页首轮即可能因正文增长过快晋升，
  属可接受语义；
- LLM 融合每轮上限 8 页 × 120s，stale 阈值 3600s 内安全；连续多轮同页
  融合的 token 成本由 settled_count 晋升自然抑制（mature 后仍会融合，
  如需静默 mature 页可在后续版本加跳过规则）。

## v6.9.99 - 2026-09-06 T2 周末维护链：课题校准+复盘移周日+分类执行+收尾汇总

**范围**：T2（周末反思链尾三个新 job + 收尾汇总 + cron 变更）。T1 已提交（ae38be66），
T3（methods 相关、optimize 反哺）不在本次提交。

**proposal_calibration job（weekend_pipeline/maintenance_jobs.py 新模块，零 LLM）**：
- job `reflection_proposal_calibration`（step=`proposal_calibration`，依赖
  `reflection_kb_merge_duplicates`，反思链尾平行分支不阻塞 recommend 主链）；
- 对全部 optimizing 课题逐个程序化校准：
  1) 引用对账：扫描 04_proposal/sections/ 四正文模块的 [N] 引用（支持
     [5,6,16] 逗号组与 [3-5] 连字符区间，跨度 >20 的区间视为数值范围跳过），
     统计次数/最大编号/唯一编号 vs references.md 条数；报超界（high）/
     死条目（>3 条 high、≤3 条 medium）/编号缺口（low）；
  2) 范本指标：立项依据中文字数（目标 5000-8000，越界 medium）、正文引用
     总次数（目标 10-20，越界 low）、主语混用（"本课题/我们"同现 low）、
     占位符扫描（[CITE: 等 12 种特征，high）；
  3) 噪声豁免（T1 评审教训落地）：frontmatter / ```代码围栏``` / $$数学块$$ /
     $行内数学$ 先剥离再扫引用——`$T\in[50,300]$` 不再误判为引用编号；
     **frontmatter 剥离逐文件执行**（合并拼接后只有首文件命中 "^---" 锚点，
     后续文件的元数据编号会泄漏，测试捕获后修复）；
  4) 产物：每课题 `06_feedback/calibration-{date}.md`（问题清单含位置与修法，
     尾部机器可读 marker 行供收尾汇总回退解析）+ job artifact 聚合报告
     `memory/weekend-reflection/proposal-calibration-{date}.md`（无 optimizing
     课题也落盘，"done 必有产物"不变式）；
  5) 反馈注入：仅 high（超界/占位符/死条目>3）时追加写
     `06_feedback/feedback-{N+1}-raw.md` 并在 file_lock("lifecycle") 内
     递增 _lifecycle.json 的 human_feedback_count（先落文件后加计数，杜绝
     "计数指向不存在文件"的空注入窗口）——下轮 critic/writer prompt 经
     load_review_feedback_for_optimization 自动携带；无 high 只落报告不动
     count（防反馈通胀）；
- 真实工作区 dry-run 验证：9 个 optimizing 课题全扫，high 合计 3（3 个课题
  各 1），其余 6 个零 high；bsv 课题 124 处引用零误报（数学区间豁免生效）。

**link_deep_review job（复用 retrospective，报告移周末）**：
- job `reflection_link_deep_review`（依赖 calibration）；import 调用
  `retrospective.run_retrospective("7d", output_path=…)`（勿复制逻辑），
  retrospective 新增可选 `output_path` 参数（缺省旧行为不变）；
- 报告落 `memory/weekend-reflection/link-deep-review-{date}.md`（与既有反思
  产物同目录），含五源复盘 7 章节 + 行动建议 + 低风险策略自动应用审计行；
- dry-run 零落盘（run_retrospective 恒写盘并可能触发策略 apply，预览直接跳过）。

**kb_taxonomy_apply job（零 LLM）**：
- job `reflection_kb_taxonomy_apply`（依赖 deep_review）；调
  `propose_categories()` → `apply_categories()`（内部先备份 categories.json
  为 .json.bak.{date} 再原子写入，同名跳过幂等）→ `scan_all_categories()`
  刷新 matched_paths → `coverage_after()` 验证；
- 无候选时写空产物文件（明确标注"保持不变式，非执行失败"）；
  v6.9.6"周日只提示不写入"哲学由 T2 显式推进为执行（纯规则筛选 + 备份 + 幂等）；
- 真实工作区 dry-run：候选 12 个（deepxiv-论文库/交变磁体/贝里曲率/强场超快光学…）。

**周末收尾汇总（scripts/weekend_summary.py 新脚本，零 LLM）**：
- 数据源：weekend-pipeline.json（calibration job result 权威口径）+
  weekend-input/ 轮次产物（summaries-{date}-r{N}.json，旧名快照不重复计数）+
  clusters-week/routes 路由分布 + optimizing/*/06_feedback/calibration-{date}.md
  marker 回退源 + knowledge/wiki/methods/ 周末窗口 mtime；
- 产出 `memory/weekend-summary-{date}.md`：消化轮次/篇数、新成簇/蒸馏簇、
  路由动作分布（new/merge/expansion/defer）、校准 high 数、反馈注入数、
  方法页变动数、反思链产物索引；--dry-run 零落盘；--self-check 临时目录
  全构造验证（10 项断言全过）；时间窗口与跨周锚点同口径（周六 00:00 本地）。

**cron 变更（lifecycle/constants.py + cron_manifest.py + framework.py + controller.py，已安装）**：
| 变更 | cron | 调度 | 说明 |
|------|------|------|------|
| 撤除 | lc-retrospective | ~~0 15 * * 1~~ | hermes 实例已删（残留 0）；CRON_MANIFEST 移除；framework 安装块与 wrapper 清理，安装路径主动删残留；DEFAULT_RETROSPECTIVE_SCHEDULE 常量移除 |
| 新增 | lc-weekend-summary | 0 22 * * 0 | 周日 22:00 收尾汇总；登记 manifest；由 setup_weekend_crontab 统一重建（lc-weekend- 前缀组，teardown 后不丢失） |
| 新增 | lc-kb-distill-sunday | 0 20 * * 0 | 周日 20:00 蒸馏小批 kb_distill --batch 8 + kb_linker --apply；独立于每日 12:50 主档（--auto 自适应档）互不干扰 |
- 实机拓扑对账 validate_cron_topology 返回 []（缺失/重复/漂移零问题）。

**测试**：
- 新增 `scripts/tests/test_weekend_maintenance.py`（81 断言，隔离目录 + 时钟注入）：
  job 模板/依赖/artifact/handler 注册、引用对账（数学区间+frontmatter+代码块豁免、
  超界/死条目/占位符分级、主语混用计数）、注入闭环（high→feedback-{N+1}+count 递增、
  无 high 不动 count、dry-run 零落盘）、deep_review 接线（stub 验证 output_path）、
  taxonomy 空候选/有候选/dry-run、cron 清单变更、收尾汇总采集与回退源；
- 适配既有测试：test_weekend_pipeline_hardening（reflection artifact 计数 6→9）、
  test_alert_circuits（清单覆盖断言换新 cron）、test_monitor_cron_stale 与
  test_ghost_write_guard（fixtures 补两个新 cron；ghost 的 micro-scheduler 调度改
  按当天动态构造——固定 `1-5` 在周末被 v6.9.2 免检分支跳过属星期依赖既有隐患）；
- `--self-check`：weekend_summary / cron_manifest / retrospective 全过；
- `--module` 全量：**1492/1492 通过**（v6.9.98 基线 1411 + 本次 81）。

## v6.9.98 - 2026-09-06 周末输入链多轮化（T1/3，T2 T3 另行提交）

**范围**：仅 T1（deep_digest 深读 + 轮次接力 + 周末输入 cron 扩编）。T2/T3 不在本次提交。

**deep_digest 取代 summarize（input_jobs.py / jobs.py）**：
- `input_summarize_new_papers` 废弃（加入 `DEPRECATED_INPUT_JOBS`，sync 清残留），
  新 job `input_deep_digest_papers`（step=`deep_digest`，handler 二元组注册）；
- 输入改简报卡全文（去掉旧 `[:1200]` 截断），单轮批量 30→10 篇
  （`DIGEST_BATCH_LIMIT`，收集层 papers 2000/briefings 6000 字符上限不动）；
- prompt 升级结构化深读 JSON：core（2-3 句核心贡献）/ mechanism（物理机制要点）/
  method_leads（方法线索：方法名 + 一句话新信息）/ proposal_links（在跑课题
  关联点：方向词 + 关联说明）/ keywords（10-15 个，保留 2-4 领域级标签要求）；
  `_coerce_digest_data` 收敛形状（数组防御沿用 v6.9.13、关键词归一化沿用
  v6.9.14），summary 由 core 回填保持下游聚类/挂载零改动兼容；
- 产物带轮次号 `summaries-{date}-r{round}.json`（round 从 1 起）；**首轮同时写
  旧名 `summaries-{date}.json`**（外部工具/人工兼容快照——影响最小方案：链内
  下游 cluster_assign/compose 改读 state 记录的 `input_round.last_summaries_path`
  （跨天轮次不错位），不再按当日文件名猜测；
- 故障防线保留：全失败 success=False 不标 done（v6.9.12）；无新料写空产物
  （v6.9.7 不变式）。

**轮次接力（weekend_pipeline/rounds.py 新模块 + pipeline.py）**：
- 每轮六步全 done 后，weekend worker（*/20 tick，`run_next` 路径，持锁内判定）
  满足四门槛即重置 input 阶段开新轮（round+1）：剩余源 ≥1（本轮 deep_digest
  result 的 remaining_sources）+ 冷却 90 分钟（`INPUT_ROUND_COOLDOWN_SECONDS`，
  距本轮最后 finished_at）+ 周末窗口未闭合（北京时间周日 23:59 后不开）+
  非工作日；源尽或窗口闭合则 stage 保持终态 done；
- 重置语义：job 全部 pending、**attempts 保留**、记录 `prev_round_finished_at`、
  清上轮产物指针、各 job 打 round 标（`_verify_artifacts` 新增 `{round}` 占位符
  支持，按 job.round 格式化）；
- 跨周重置（自然周锚点）中 round 归 1；
- 判定全为纯函数 + now 时钟注入（对齐 `_is_weekend` 注入式设计），dry-run
  零落盘不执行接力；
- cluster_distill 每轮簇上限 8→3（原"周限 8 簇"语义改为"每轮 ≤3 簇"，
  多轮下周末总吞吐约 21 簇）。

**cron 变更（lifecycle/constants.py + cron_manifest.py + framework.py，已安装）**：
- 周六 input 首轮 09:00 → **09:30**（`DEFAULT_WEEKEND_INPUT_SCHEDULE`，两处常量同步）；
- 新增锚点轮（保底触发，轮次接力由 worker 完成）：`lc-weekend-input-r2`（六 15:30）
  / r3（六 19:30）/ r4（日 11:30）/ r5（日 15:30）/ r6（日 19:30）；
- 新增夜间轮：`lc-weekend-input-n1`（六 00:30）/ n2（六 05:30）/ n3（日 00:30）/
  n4（日 05:30）——凌晨时段覆盖，全部同 `lc_weekend_input.sh` 入口幂等触发；
- 首轮 cron 名统一 `lc-weekend-input`（旧通用映射生成冗余的
  `lc-weekend-weekend-input`，与清单登记名不一致致对账 missing；旧实例已随
  teardown 重建清除，output/reflection 双前缀名不在本次范围保持不变）；
- 全部 10 条新 cron 登记进 `CRON_MANIFEST`（缺失/重复/漂移对账），安装由
  `setup_weekend_crontab` 统一重建；实测 `validate_cron_topology` 对账零问题。

**测试**：
- 新增 `tests/test_weekend_input_rounds.py`（66 断言）：deep_digest 产物轮次命名/
  首轮旧名兼容/批量上限/全文输入/全失败防线；接力四门槛与周日 23:59/工作日
  窗口；重置保留 attempts；run_next 端到端开轮挑中 collect；dry-run 不开轮；
  跨周 round 归 1；distill 每轮 3 簇；`{round}` 产物校验；
- `test_input_summarize_shapes.py` 迁移至 `_coerce_digest_data`（v6.9.13 形状
  防线语义保留）并补入 `--module` 清单（此前该套件不在清单，12 断言从未计入
  日常回归）；`test_weekend_input_rounds` 同步入清单；
- 同步更新 5 个既有测试的构造数据/断言（job 改名、manifest 扩容）：
  test_weekend_pipeline / test_weekend_pipeline_hardening / test_input_clustering /
  test_cron_stale_weekend_grace / test_alert_circuits / test_monitor_cron_stale /
  test_ghost_write_guard。

**验证**：`py_compile` weekend_pipeline/*.py lifecycle/*.py 通过；cron_manifest 与
weekend_pipeline.rounds `--self-check` 通过；定向回归（weekend_pipeline 45/45、
hardening 35/35、cron_stale_weekend_grace 19/19、input_clustering 107/107、
input_rounds 66/66、input_summarize_shapes 17/17）全过；`--module` 全量
**1411/1411** 通过（基线 1328 + 新套件 66 + 形状收敛入册 17）。

## v6.9.97 - 2026-09-06 健康检查遗留偏差处置：state_sync 原子写 + kb_health 三维看板化

**背景**：09-06 08h 健康检查报告遗留两项"仅报告待人工裁决"偏差（v6.9.96 规则），
用户裁决处置。

**修复 1（04h 报告 §2.2，state_sync.py）**：`_save_item_status` 非原子写 →
改走 `common.save_json`（tempfile+fsync+os.replace），消除 SIGKILL/磁盘满
半写窗口；`_load_item_status` 静默吞损坏 → 损坏副本备份 `.corrupt-{ts}` +
ERROR 输出后再空重启，杜绝"空数据覆盖全量论文状态"的不可恢复丢失链；
`save_project_sync` 顺手同批原子写。

**修复 2（#11 KB 健康评分偏离）**：`_calculate_kb_health` 三维度
（freshness/isolated/score）此前只留周日反思报告，看板 kb_metrics 仅
sync_engine 写 coverage 一维（1/3 维）——`run_reflection_analyze_patterns`
拿到 kb_health 后全量合并写入 system-kanban.json，前端 /api/console/flow
可见（实测基线：coverage 88.4 / freshness 100.0 / isolated 22.2 / score 88.7）。

**顺手修复**：test_weekend_kb_maintain / test_weekend_pipeline_hardening
直接单跑入口滞后（v6.9.56 起 `print_summary`→`print_report`、`suite.failed`
→`suite.summary()["failed"]`），单跑恢复 exit 0。

**裁决维持（不动代码）**：#2 对抗评审维度轮换（69 轮未触发属评分流动性
正常，逻辑在位非死代码）、#7 质量天花板收敛线（结构性死代码·设计内维持，
晋级主路径为全模块对抗+dossier）。

**验证**：py_compile 通过；state_sync --self-check 通过（35 篇真实状态读写）；
全量回归 1328/1328。

## v6.9.96 - 2026-09-06

## v6.9.96 - 2026-09-05 健康检查反惰性改造：pointer v2 防回退格式 + 定时任务模板五项优化

**背景**：20h 轮惰性区域评估确认健康检查产出不可累积——#11 KB 健康评分在 08h 轮
判"偏离"后被 20h 轮误判"正常"（结论回退）、6 个双上限终态异常连续 8 天用"既有
观察族"豁免、检查模板三处参数与实现漂移（--check 不存在 / 基线 392/395 过时 /
11 类 cron 与实际 8 类清单不符）、第二层连续多轮零对象空转。

**修改**：
- `logs/healthchecks/design-check-pointer.txt` 升级 v2：15 项 history 记录
  last_verdict+date（#4/#5/#6 因历史记账漂移标"待查证"）、deep_scan_rotation
  5 项存量路径轮换、green_streak 元检查计数（当前 0，#11 偏离归零）
- 定时任务"全链路健康检查与设计诊断"内容更新：① 命令修正（--dry-run /
  hermes cron list 对照 cron_manifest / 基线动态化 1328）② 空窗深扫规则
  ③ 抽查防回退强制规则（无对照禁判正常 / 偏离改判需双证据）④ 异常 TTL
  升级（≥6 轮未消解标🔴待裁决并给处置建议，禁"既有观察族"豁免）⑤ 元检查
  （green_streak≥12 触发检查面复盘段）+ 数据逐字核对规则
- `healthcheck-2026-09-05-20h.md` 两处勘误：done=420→414（414 与 16h 持平，
  周末 worker 暂停设计内）、#11 判定"正常"→"偏离维持"（与 08h 轮结论一致）

**验证**：pointer v2 结构完整可解析；定时任务 update 后 list 确认；无代码
逻辑改动，self_test 基线不受影响。

## v6.9.95 - 2026-09-05 moire（莫尔强场探针）评审团 4 份意见人工修订：引用重灾区修复 + I_c 口径重算

**输入**：R1/R2/R3/R4 四份评审意见本课题章节共 49 条（R1×11、R2×14、R3×13、R4×11），
按 R1>R3>R2>R4 裁决逐项执行，处置报告见
`optimizing/general-moire-strong-field-probe-20260726/05_review/manual-revision-20260905.md`。
（注：sections/ 下 rationale/content/scheme/full_review 四文件改动被并行进程随 v6.9.94
一并带入提交，本条目补记归属并提交 references.md 与处置报告。）

**关键修改**（sections/ 下 5 文件）：
- **R3 高危×5 引用修复**：12 处 [CITE:…] 占位符清零（2 处换核实条目 Silva 2018 /
  Ikeda R 2025 arXiv:2508.00296 真实标题，10 处按"无法核实即删"处置）；[12] 一号两用
  拆分（Cao 页码更正 80–84；Kozák 条独立为 [23] 且一作更正 Peterka，正文 5 处同步）；
  [9] Hohenleutner 乱码条目按核实文本更正后因 R1-37 失引用点移除；[15] 占位 DOI 北大条
  删除；[32][33] DOI 全错更正（nphys1847）。全表程序化重排 35→26 条（脚本 renumber_mo.py），
  对账终态 108 处/26 唯一编号/零占位/零死条目/零一号两用/零超界。
- **R1-32（critical）I_c 差 45 倍**：参数代入表重算（δW ∝ I 线性标度更正原"平方"错误），
  三档 I_c = 1.8/3.6/7.1×10⁹ W/cm²；随之重划双模式窗口（探针 ≤2×10⁸ ≪ I_c 保证读出
  不扰动关联态、调控 5×10⁸–2×10¹⁰ 覆盖 I_c），并补充探针 SNR 应对与靶标 B 强度窗口
  重标定；R2-08 的 10¹¹ 量级窗口文本因与修正后 I_c 矛盾按裁决规则驳回。
- **R1 其余 high/medium**：石墨烯 K 点偶极矩为零论断删（改带隙保护论证）；谐波阶次/
  数据维度三说统一 3–11 阶 ≤22 点；扭转角精度统一 ±0.05°（删 ±0.02°）；Hohenleutner
  张冠李戴实验链删（改"尚无直接实验验证"）；ATAS→TA（12 处）；O(N³)→带数×k 点×时间步
  + 核时分层分解 + 降阶量级 4→约 3–4 个数量级；"必达"与 30% 失败率并置矛盾消除。
- **R4 P1×5**：新增 §1.3 国内研究现状（约 420 字，仅用核实条目 [14][15][22]，后续小节
  顺延 §1.4–§1.7 并同步全部跨章引用）；"末尾补足 NSFC…"等元话语删除；scheme §3.5 年度
  计划/§3.7 预期成果整节删（唯一归属 content）；arXiv 编号主语句降级为主项目设计表述；
  主语统一"本项目"（19 处）。
- **R2×14**：检索时间戳/起草痕迹/量纲混乱句逐条改；误差口径统一 <12%（合成）/<15%
  （考核）；两处 600–700 字堆砌段切分。

**验证**：verify_mo.py 复验——零占位符/零临时令牌/零超界/零死条目/零一号两用，29 项旧
错误口径残留模式清零，修正后 7 条关键 DOI 抽检全部命中；正文引用 108 处（rationale 49/
content 33/scheme 26）。遗留：[12] preprint 发表状态待核；探针强度下移后 SNR 定量预算
建议下轮 critic 关注。


## v6.9.94 - 2026-09-05 order-parameter（CrSb 序参量读出）pass 4 引用专项收尾 + 评审团 4 份意见人工修订

**输入**：R1/R2/R3/R4 四份评审意见本课题章节共 42 条（R1×10、R2×13、R3×10、R4×9）
+ feedback-2/3 待修清单 8 项，按 R1>R3>R2>R4 裁决，逐项确认并执行，处置报告见
`optimizing/general-order-parameter-ultrafast-readout-20260727/05_review/manual-revision-20260905.md`。

**关键修改**（sections/ 下 5 文件，约 60 处）：
- **R1-53（critical）对易断言**：scheme §2 "[H_SOC,H_Z]=0" 删除，改显式不对易表述
  （[L·S, B·(L+2S)]≠0 为磁晶各向异性根源），参数可分性降级为 FIM 条件数数值检验
  命题；关联同步 scheme §3 雅可比句、content §2.4 正交化断言、full_review 口径表
  新增"磁场与 SOC 可分性"行。
- **R3 元数据八连修正**：[7] 编造作者串经本轮 arXiv API 实时反查（id_list=2412.13329）
  回填真实作者 Zhang/Tyulnev/Vamos 等 + 真实短 DOI 10.1103/812z-nl4m；[31] PRL→
  PNAS 122, e2426253122；[5] 卷 112→113；[9] 补全 130: 1551-1561 并删编造作者；
  [29] 卷期/DOI/标题三重更正；[30] 期刊信息不可核实撤除改 arXiv 引用；[3] 按原题
  更正；[33] 作者按 v2 更正。R3-09 补引带隙/SOC 文献驳回（零虚构红线，改标定初值
  +启动后复核表述）。对账终态 34 条/124 处/34 编号，零死条目零超界，满分保持、
  未重排编号。
- **feedback-3 口径表虚报**：rationale §一.4 补写"驱动场强 0.3—0.8 V/Å、外磁场
  0—7 T（本方案标定区间）"句使口径表互证成立；主动修正 2 处错位出处（§一.1→§一.4），
  口径表 14→17 行（新增 TiSe₂ 对称性/晶系语言/磁场-SOC 可分性三行）。
- **损伤阈值可行性（high）**：scheme §3 新增同类参照（ZnO/TiSe₂ 约 0.1—0.5 V/Å vs
  本项目 8×10¹²—2×10¹³ W/cm²）与降场强预案（下探 0.1—0.3 V/Å + 双通道监测 + 判据
  复核 + MnTe 备选兜底）；R1-55 长波长断言改两效应竞争表述。
- **R4-48 引用收敛**：rationale 编号引用 66→35 处（-47%，超额完成本轮先降 1/3），
  §2 三连堆砌段（约 900 字）按对称性分类/理论预言/实验佐证重组 3 段，[19][20][23]
  三轮复述收敛一轮，复述轮次去编号改回指。
- **R2×13 + 用户附加项**：丹麦理论组痕迹句自然化、"可辨识性"逐字重复 4 处收敛 1 处、
  L61 行号残留删、判据四段并为两段、SOC 100—200 meV 改原子值 0.3—0.4 eV（四处同步）、
  C₄ 语言清零（TiSe₂→D₃d 三重 / CrSb→六方 C₆→C₂）、超导磁体分钟级切换 + 场向几何、
  95% 压制比删数值、"Tyulnev ±8%" 6 处补挂 [6] 出处并注明合成规则。

**验证**：对账脚本复算——34 条编号连续，正文 124 处引用（rationale 35/content 30/
scheme 40/full_review 19），零死条目/零超界/零占位符；grep 复核 14 类旧表述归零；
三模块中文字数 5928/4982/9683 均在参考区间；上轮 [17] Šmejkal 真实标题未回退。
引用专项验收三门槛（citation critical 清零 / references 校验与 critic 一致 /
口径表出处全部可定位）逐条达成，详见处置报告第五节。

## v6.9.93 - 2026-09-05 new-idea（MnTe g 波 HHG）评审团 4 份意见人工修订

**输入**：R1/R2/R3/R4 四份评审意见本课题章节共 45 条（R1×10、R2×12、R3×14、R4×9），
按 R1>R3>R2>R4 裁决，逐项确认并执行，处置报告见
`optimizing/general-new-idea-20260822/05_review/manual-revision-20260905.md`。

**关键修改**（sections/ 下 5 文件）：
- **R1-43（critical）波型统一**：全文统一 g 波主线，rationale §2 新增 g/d 波型争议
  专段（ARPES[2] vs 磁化对称光学实验[17→新17]），d 波降为对照通道，实验可裁决。
- **R3 高危引用五连**：[16] CrSb 被当 MoS₂ 依据 5 处全部改挂 [6]；[8] Langer/[12] Luu
  DOI 指向无关论文（[12] 按 R3 核实文本替换为 PRB 94, 115164 (2016)，[8] 删除）；
  [13] 假 arXiv 号 2412.00000 删除；[18] Hancock 错配 2 处删除；scheme TDDFT 处
  [17]→[8]。共删 10 条、换 2 条、新增 Silva 2018 与 Hohenleutner 2015（均 R3 核实
  条目），references 29→21 条，脚本化重编号，对账零死条目/零超界/零占位符。
- **R4 P1×3**：新增 scheme §7 年度研究计划（四年含年度终止判据，全部复用既有口径）；
  立项依据 2994→5124 中文字（扩写仅用现有文献）；scheme 15 处粗体标签全部转自然段
  /小节标题，"目标 N 对应产出"四段并为两段。
- **R1-44/46/49/50**：SOC 10–100 meV 改为 Te 5p 原子值 0.4–0.5 eV 并阈值化；磁场
  反转差分补物理前提（Néel 矢量晶格钉扎 + B-线性偶次通道正演预计算，≥1% 降为
  工作假设）；超导磁体 7 T 改分钟级切换 + 双态驻留；产额"单发计数率"改计数率 +
  单脉冲换算 + 缩放依据待实测。
- **R2×12 逐条落地**：Nature 英文句中文转述、"counts/s"单位冲突、检索时间戳 5 处
  清理（保留 2 处带范围限定）、"拟首次"三连改增量定位（对齐 Lin 2024 已有观测）、
  交叉引用统一"见研究方案 §N"、"本研究"→"本项目"。

**验证**：对账脚本复算——21 条文献编号连续，正文 64 处引用（rationale 39/content
10/scheme 15），rationale 中文字数 5124 ≥ 5000；[6] Liu 2017 上轮修正未回退。

## v6.9.92 - 2026-09-05 order-parameter 人工退回 + per-proposal 轮次上限覆盖

**用户裁决（09-05）**：order-parameter（面上，pass 3/r8 晋级 pending_review）验收
决策包预审 reject_lean——1/5 模块通过（仅 references 0.85），18 未解决（12 高危）。
R8 critic 高危核心为引用真实性四连：`citation_fabrication`（12/44 错配+虚构卷期
页码）、`phantom_reference`（承重层双源不可证实）、`citation_mismatch`（内联错配
+未来编号+scheme 残留）、`red_line`（损伤阈值口径两说）。按"退回 + 引用专项"处置。

**退回执行**：`submit_feedback(verdict="major_revision")` 一次完成——流转
pending_review→optimizing、**轮次自动归零（8→0）**、pass 3 归档开 pass 4、
84 个旧 job 清理、`return-comparison-pass3.md` 对比报告生成。7 点反馈文本
（引用真实性专项 4 条逐条指令 + 表达质量 3 high + 验收标准：citation 类
critical 清零、references 校验与 critic 结论一致）经负反馈闭环注入 critic prompt。

**代码变更**（completion.py，治本项）：新增 per-proposal `max_rounds_override`——
人工退回后课题轮次已到上限，若不加宽，下一轮完成度检测立即再触发"达到最大轮数"
逃生阀空转晋级（r8 退回 + 引用专项需 r9+ 空间）。`_check_done` 条件 3 逃生阀与
`auto_optimize_and_advance` 循环上限同步读取该字段（正整数生效，缺省/非法值回落
`DEFAULT_MAX_ROUNDS=8`）。order-param 已写 `max_rounds_override=12` 作深度防御
（轮次已归零，覆盖保证未来 12 轮内不再撞顶空转）。

**验证**：隔离验证 8/8（缺省回落 8 / override=12 时 rounds=8 不触发 /
rounds=12 触发且文案带 12 / 三种非法值回落 / auto 循环同步尊重 override 与缺省）；
`py_compile` 通过；相关回归 5 套件（quality_ceiling_convergence 14、
cross_round_p0_memory 21、auto_acceptance 16、transition_reset_jobs 14、
lifecycle_cron）全过；生产落盘复核 status=optimizing、rounds=0、override=12。

## v6.9.91 - 2026-09-04 api_error 纳入模型逃生：只要有一个模型能跑就不停摆

**根因（用户质询 09-04）**："我们的模型都是互为备选的，只要有一个还能跑就应该正常推进。"
09-04 实证 51 job 中 41 成功（minimax 存活）却因 zai 的 9 次 429 触发全局熔断，
把 minimax 产能一并压死。查 hermes 源码（conversation_loop.py:6813-6827）确认：
hermes 把 429 文案分类为 `FailoverReason.billing`（账户套餐问题），而 billing 语义
= "换模型也解决不了套餐额度"，**不触发其内部 fallback**。该设计对单供应商多模型场景
正确，但本项目 fallback 链**跨账户**（zai 限额 ≠ minimax 限额），billing 恰恰应切换
——hermes 无法改（第三方），在 CoPilot 编排层补上。

**修复**（circuit_breaker.py）：明确 429（api_error）路径不再 open 停摆——
- 连续 `API_FAILURE_THRESHOLD` 次 api_error → `_activate_escape` 切备用（minimax），调度照常；
- probing 试探遇 api_error → 同样激活逃生（原先重新 open 等 1h 冷却）；
- 唯一停摆路径收敛为"逃生中备用也连续失败达 `ESCAPE_FAILURE_LIMIT`"（主备双挂）。
docstring 与自检/测试套件同步（路径 2/4/5/6 用例 2/4/6 改断言）。

**验证**：熔断器自检 18 路径全过（新增"api_error→逃生→双挂→open"链路）；
`--module` 全量 1328/1328 通过；生产状态复位为干净 closed，新逻辑即时生效。

## v6.9.90 - 2026-09-03 聚焦切换适配不间断调度（窗口内轮完成即切换）

**用户发现的缺陷（09-03）**：v6.9.87 切换到不间断长窗调度后，"每完成
一轮强制切换"（v6.9.51）的判定整个嵌在 `if slot_index != last_slot_index`
（时段边界）分支内——工作日 00:00-13:00 同一 slot 内该代码一次都不执行。
实证：qg 连续霸占焦点 9 小时连跑 r3-r6 三轮而零切换，其余 7 课题零执行。

**修复**：同时段延续路径（else 分支）新增窗口内轮完成检查——每次 tick
对比聚焦课题 optimization_rounds 与 _last_round_seen 快照，落后即让出
（move_to_queue_end + 队列头切入），让出时快照对齐防下次切入误切。
不更新 last_slot_index（保持时段切换检测语义）。

**验证**：隔离行为测试两场景（轮完成让出+快照对齐 / 轮进行中不误切）；
test_micro_scheduler_rotation 全过；生产即时验证——补丁上线后真实 cron
tick 于 09:15:55/09:16:02 两次触发 qg 让出，焦点切换到 transient，
被饿 9 小时的其余课题恢复轮转。

## v6.9.89 - 2026-09-03 内容卫生三修：full_review 结构性守卫 + qg 经费节剥离 + CITE 挂钩程序化解析

**审计发现（09-03 全池扫描）**：① attosecond full_review.md 被写回整份
"整体一致性自评报告"（1807 中文字符 < 3000 上限、措辞绕开全部
WORKLOG_PATTERNS——"评审轮次：R5"不匹配"第N轮"），旧判据双双漏过；
② qg scheme.md 含 §9 经费概算整节（60 万元分配/劳务费/合作方配套/
知识产权分割协议），违反 08-28 用户裁决的内容边界红线；③ moire 累计
107 处 [CITE:xxx] 挂钩未解析——CITE→[N] 替换此前完全依赖 writer LLM
行为，无程序化兜底。

**修复**：
1. full_review 守卫升级为结构性判据（最强）：合法文件必以程序生成的
   "# 全文逻辑骨架"头开头，非骨架头一律迁移 05_review/ 并重写骨架。
   attosecond 污染已迁移（full-review-record-20260903.md），其余 7 课题
   干净。
2. qg scheme §9 经费节 + §8.5 知识产权/合作句程序化剥离，存档
   05_review/removed-boundary-content-20260903.md；writer 边界红线
   扩展覆盖"经费概算/劳务与人员费/知识产权分割协议"。
3. 新增 resolve_cite_hooks()：从 references 条目尾注提取 CITE→N 映射，
   程序化替换正文挂钩并清理条目标记，挂入写盘守卫族（第 6 项）。
   moire 执行：正文替换 77 处、尾注清理 36 处、5 处未映射保留
   （对应文献不在列表，留下轮 references 轮补齐）。

**验证**：17.9 新增 3 用例（结构性判据/守卫族挂载/边界红线扩展）；
机制测试 261/261；全量回归 1328/1328。

## v6.9.88 - 2026-09-03 不间断轮转落地（补记，随 v6.9.87 一并提交 19e43ad7）：工作日仅 13:00-18:00 高峰空闲

**用户裁决（09-03）**：4 时段制（15h/天）的 3.5h 时段边界必然把 4-6h 的
完整优化轮切成"中间状态"课题；改为不间断轮转，仅保留工作日下午高峰
空闲窗。吞吐 15h→19h（+27%），轮次可一气呵成、完成即切换——中间状态
课题趋近零。

**实施（零代码改动）**：新增 `memory/config/schedules/focus-slots.json`
（slots: 00:00-13:00 + 18:00-23:59），走微调度器既有的配置覆盖路径
（DEFAULT_FOCUS_SLOTS 保留为回退，删除配置即恢复 4 时段制）。

**边界与交互（已评估）**：跨窗边界（13:00/18:00）各触发一次队列轮换；
窗内依靠"轮完成强制切换"（v6.9.51）轮转课题；软卡死让出语义从
"2 个时段(≈8h)"变为"2 个窗(≈1 天)"——v6.9.39 的 job 级推进信号是
主要保护，可接受；备份 cron 13:00 恰落空闲窗首；kb_sync/kb_distill
（12:40/12:50）与 job 并发（不同配额池）；周末模式不变。

**验证**：`_current_focus_slot` 六点边界判定（12:59/13:01/17:59/18:01/
23:58/当前）全部正确；全量回归 1325/1325；AGENTS.md 时段描述同步。

## v6.9.87 - 2026-09-02 lc-prompt-optimize 二次保险：脚本侧守卫拦截 auto 通道

**背景（09-02 健康检查 20h 发现）**：v6.9.70 (commit 3df575cb) 明确
说明"lc-prompt-optimize 暂停（只增不减/审计虚标 verified/writer
SOUL 12.5KB 而分数净-27）"，但修复仅停留在清单层面——
scripts/lifecycle/cron_manifest.py 注释说明 lc-prompt-optimize 已移出
期望拓扑，**未触及 hermes cron 实际配置**。2026-09-02T06:00:43Z（北京时间
14:00）实际触发 9 条 suggestions auto-applied（writer/SOUL.md ×8 +
critic/SOUL.md ×1），writer SOUL.md 167 行含 3 个 auto-opt 段，与
v6.9.70 设计意图偏离。monitor 不告警（被移出清单的 cron 不属
stale 范围）。

**根因**：v6.9.70 只删清单项不动 cron 配置，"暂停"是清单语义而非
运行时状态。

**修复（最小化、定向）**：
1. `scripts/prompt_optimizer.py` 顶部新增 `PROMPT_OPTIMIZER_ENABLED` 常量
   （默认 `False`，由 env `PROMPT_OPTIMIZER_ENABLED=1` 显式启用）。
2. `cmd_auto()` 函数首部守卫：`not PROMPT_OPTIMIZER_ENABLED` 立即返回
   + 写明 INFO 日志 `prompt_optimizer_gate`，**0 LLM 调用、0 SOUL.md
   写入**。
3. `analyze / list / apply` 三个子命令不受守卫影响——只挡 `auto` 通道，
   人工审查路径保留。
4. hermes cron 实际配置保持不变（恢复时无需重新创建 cron）。
5. `scripts/lifecycle/cron_manifest.py` L53-67 注释同步更新，含两种
   恢复方法。
6. `scripts/tests/test_prompt_optimizer.py` 新增 4 用例（共 8 断言）：
   - `_test_cmd_auto_gated_by_default`：默认 False + SOUL.md 未被修改
   - `_test_cmd_auto_enabled_by_env`：env=1 启用
   - `_test_analyze_list_apply_unaffected`：子命令路径不受影响
   - `_test_cron_manifest_no_lc_prompt_optimize`：清单侧不含此 cron

**验证**：4h 窗口 + 整个回归 1325/1325 全绿（基线 1317/1317 + 新增 8 断言）。
实测 `python3 scripts/prompt_optimizer.py auto` 立即输出暂停说明并
exit 0；`PROMPT_OPTIMIZER_ENABLED=1 python3 scripts/prompt_optimizer.py auto`
恢复正常流程。

**预期**：14:00 cron 触发后守卫拦截 → 0 写入 SOUL.md → 与 v6.9.70 设计意图一致。

## v6.9.86 - 2026-09-01 critic 输出契约模板化：从生成量上治本评审超时（不抬超时）

**背景（09-01 实证）**：v6.9.85 回退后 critic 在备用 MiniMax 上仍 1200s
精确触顶（10:30 派出 → 10:50:45 触顶，非误杀的干净数据）。量化定位：
critic 报告实测 17-22KB（moire r6 达 21,993 字符），而下游只消费评分块/
问题清单/修复指令（digest 后 8KB 足够）；prompt 中既有的"≤6000 字"软
约束实测完全无效。推理模型生成 20KB 报告的耗时（writer 同等输入 387s，
critic >1200s，3 倍差在生成端）是超时根源——抬超时只是给过量生成买单。

**修复（proposal_lifecycle/optimize.py）**：
1. 输出契约模板化（硬性）：报告全文 ≤4000 字，逐段落模板——执行清单
   对照每条一行、锚点对比限量 2 对（每对三行）、写作风格 ≤150 字、
   问题清单 ≤8 条（每条一行式 `[severity]｜位置｜问题≤40字｜建议≤40字`，
   仅 critical 可追加 ≤100 字论证）、评分块附一行档位依据。
2. references 轻量分支同步加 ≤2500 字契约。
3. 旧软字数约束（实测无效）移除。

**兼容性**：下游解析完全不变——评分块行格式（创新性：0.85）、锚点
结论行（锚点对比结论：…）、issues 提取（行内 [sev] 标记）均保留。

**验证**：prompt 构建端到端（真实课题重演）：3,857 字符、契约全要素
在位、评分块保留；17.8 新增 3 用例；全量回归 1317/1317。

**预期**：生成量降约 70%，critic 在 1200s 内从容完成；报告存储同步
瘦身（22KB→4KB），monitor 输入随之变小。生效后观察首个批次成功率。

## v6.9.85 - 2026-09-01 紧急回退：stall 击杀默认禁用（v6.9.84 前提错误致 critic 12 连误杀）

**事故**：v6.9.84 的活性感知通信上线后（08-31 19:10），critic 12 连挂、
0 成功——全部为"超时(挂起360s零输出)"，含备用模型上的正常任务，比
修复前（24% 成功率）更糟。熔断/逃生状态机被误杀事件反复推入
escape→open 循环。

**根因**：活性检测的前提假设错误。实测（真实调用 55.1s 全程监测）：
hermes CLI -z 模式工作期间**完全静默**——stdout/stderr 零字节流出，
仅在完成时一次性输出（1496 bytes@t+55s）。"持续产出=在干活"不成立，
360s 零输出击杀把所有超过 6 分钟的正常任务全部误杀。短任务（writer
387s 均值边缘、lit_*）侥幸存活造成"部分成功"的假象。

**处置**：
1. `HERMES_STALL_TIMEOUT_S` 360→0（默认禁用）；框架保留，仅显式传
   正值时生效——待 hermes 提供心跳/进度输出后再评估启用。
2. 复位熔断器（closed）清除误杀污染的计数与逃生状态。
3. 重置 11 个被烧到双上限终态的 critic job（attempts/repair 清零 →
   pending，备份 `_lifecycle.json.bak-v6985-miskill-reset`），解锁
   全部下游链路。

**教训**：对不可观测的子系统（CLI 静默工作），"无信号"≠"无进展"；
引入新击杀机制前必须先实测目标进程的真实输出模式。四形态测试用的
是模拟进程（持续 print），与 hermes 真实行为不符——端到端验证必须
覆盖真实执行形态。

**验证**：17.1/17.7 断言更新（默认禁用 + 零输出进程由硬上限击杀）；
机制测试 255/255；全量回归 1314/1314；真实 hermes 调用 16.8s 成功。

## v6.9.84 - 2026-08-31 活性感知通信：超时判断从"猜时间"改为"看产出"（治本）

**用户裁决**：不通过无限制提升超时时间解决问题。v6.9.83 的 900/1200→
1200/1500 是线性外推——模型再变慢又要 1800、2100。08-31 的 15 次 critic
失败实为两种不同形态被同一手段处理：zai 限流挂起（接受请求后零字节
输出，干等上限纯浪费）与慢而在跑（真实需要 840-1140s，被上限随机砍掉）。

**修复（proposal_lifecycle/optimize.py）**：
- 新增 `_communicate_with_stall()`：selectors 非阻塞监测子进程 stdout/
  stderr 活性。持续有产出 → 等到硬上限（慢任务不被砍）；零输出超过
  `HERMES_STALL_TIMEOUT_S=360s` → 立即击杀，error 标记
  `超时(挂起Ns零输出)`（文案计入熔断 is_timeout_error → 分桶/逃生
  更快接管：挂起从 900s 白烧缩短到 6 分钟内）。360s 对齐 hermes 内部
  stale 周期（300s，其自救重试会在 stderr 留输出不计为零输出）。
- `_run_hermes` 弃用 `communicate(timeout)` 改用上述函数；进程组
  击杀语义（SIGTERM→5s→SIGKILL）与管道吸干保持不变。
- 超时上限维持 v6.9.83 的 1200/1500 不再上調——硬上限仅兜底死循环，
  不再承担"猜一个足够大的时间"的职责。

**验证**：真子进程四形态（正常完成/零输出挂起 2.01s 击杀/慢而在跑触
硬上限且输出完整捕获/持续输出按时完成）全部符合设计；新增 17 套件
7 用例固化；全量回归 1313/1313；真实 hermes 调用端到端 17.4s 成功。

## v6.9.83 - 2026-08-31 critic 超时基准实测校准 900/1200→1200/1500 + worker 入口熔断闭环

**根因调查（纠正 08-31 傍晚的误诊）**：此前判断"凌晨 10 连超时未触发分桶
是 worker 路径无回报所致"——复核完整熔断历史（修正 UTC/CST 查询窗口
错误）后确认：凌晨 job 全部走微调度器路径，**分桶逃生 01:10 即正常触发**，
全天两轮完整闭环（激活→备用注入→试探→自动解除），机制无缺陷。

**真实根因：critic 超时基准失效**。成功案例实测耗时 840–1140s（18:49
成功案例约 19 分钟），普通模块 900s 上限随机砍掉大量本可完成的 job——
全天 critic 成功率 24%，15 次失败全部触顶超时（非解析/输出问题）；
凌晨备用模型（minimax）上 critic 同样 >900s，3 连败正确触发
escape->open 停摆 1h15m。zai 挂起由逃生机制兜底，超时上限才是瓶颈。

**修复**：
1. `CRITIC_WRITER_TIMEOUT_DEFAULT_S` 900→1200、`LARGE` 1200→1500
   （v6.8.52 分级框架不变，仅上调数值）；optimize.py 章节评审路径
   `min(timeout, 1200)` → `min(timeout, 1500)` 对齐。writer 平均 387s
   不受影响仅慢尾受益；1500s 仍 < STALE_RUNNING_SECONDS(1800s) 安全。
2. worker 入口（execute_next_job）补熔断闭环：派发前检查 allow_dispatch
   （open/probing 停摆不绕过，此前仅微调度器有此检查）+ 执行后回报
   record_job_result 四元组（失败计入分桶/长链计数；幂等无害——job
   终态后另一入口 pick 不到同一 job）。今日非根因，但为真实防御盲区。

**验证**：test_mechanism_hardening 4.6 断言更新 + 16.9 新增 4 用例
（worker 检查/回报/超时分档守卫）；全量回归 1306/1306 通过。

## v6.9.82 - 2026-08-31 monitor 夜间静默拦截补全：静默窗口内飞书照发的门控缺口

**缺陷（00h 健康检查发现，5 次运行时实证）**

- `lifecycle_monitor.py` v6.9.68 引入夜间静默（22:00-08:00 只入缓存
  不发送、次日工作时段补发），但实现只把 `quiet` 用于拦截
  `notified` 计数，L992 `_send_feishu(title, content)` 的实际发送
  未被拦截——静默窗口内只要某告警 key 通过 `_should_notify` 去重
  （新异常或 24h 冷却到期），飞书照常送达，且发送成功后
  `_mark_notified` 消耗冷却，次日也不会补发，"夜间不扰+次日补发"
  双语义同时失效。
- 实证（logs/linsai.log.2026-08-30 / linsai.log）：08-30 22:00:37、
  23:00:47、08-31 00:00:56、03:00:26、07:00:04 共 5 次静默窗口内
  "飞书通知发送成功"，均紧跟"只入缓存不发送通知"日志行。

**修复**

- 发送门控改为 `not quiet and _send_feishu(...)`：静默窗口内不发送
  也不标记，次日首个非静默运行经 `_should_notify` 自然补发同批异常。

**测试**

- 新增 `scripts/tests/test_monitor_quiet_hours.py`（13 断言）：静默
  不调用 _send_feishu / 不标记冷却 / _should_notify 保持 True /
  次日非静默补发并标记 / 非静默基线不变 / dry_run 永不发送。
- `test_monitor_lark_failure.py` setup 桩化 `_in_quiet_hours=False`：
  该套件聚焦 lark 失败去重语义，不桩化会在真实夜间（22:00-08:00）
  运行时随时钟漂移（v6.9.68 起 notified_count 断言已是时间炸弹，
  本次修复会进一步波及"发送成功后标记"断言）。
- 两套件注册进 self_test `mapping["module"]`（原 8 个未注册套件中
  的 test_monitor_lark_failure 一并注册——两者守护同一通知路径）。
  基线 1283 → 1303 全绿。

## v6.9.81 - 2026-08-30 周末状态双修 + 覆盖率口径纠偏：笔记覆盖 43%→100%（真实值）

**修 1：周末状态瑕疵（两处）**
- 周报自指（weekend_pipeline/output_jobs.py）：weekly_report job 生成报告
  快照时自身必处 running，旧实现如实呈现"◐ 进行中"（08-29 实证产物已
  落盘却误导读者以为卡死）。报告视角下该 job 一律按完成态呈现。
- 兼容层状态漂移（weekend_orchestrator.py + lifecycle/orchestrator.py）：
  stage job 由 pipeline 侧推进（repair 补跑/worker）而不经编排器入口时，
  weekend-jobs.json 停留陈旧状态（08-30 实证：pipeline output 全 done、
  兼容层仍 pending——上周六 FAILED → repair 重置 pending 后无人推进）。
  新增 reconcile_weekend_jobs() 以权威 pipeline 状态对齐兼容层，挂入
  repair 周末分支自动防复发，CLI --reconcile 可手动执行。已执行：
  weekend_output pending→done（finished 与权威一致）。

**修 2：KB 笔记覆盖率口径 bug（反思误报根因）**
08-30 反思建议"覆盖率仅 43%（336/780）批量补齐深度阅读笔记"——实为
统计口径 bug：旧算法从文件名正则提 arxiv_id，但 wiki 蒸馏页文件名把
"2603.07490" 改写为 "2603_07490"（点→下划线路径安全），正则失配后
fallback 用整名当 id，raw（arxiv id）与 wiki（文件名）几乎不相交。
按 source_raw 口径（与 kb_distill/kb_health 告警同源）重算真实覆盖
774/784=98.7%。修正 _calculate_kb_health 改用 source_raw 口径，并
蒸馏补齐真实缺口 10 篇（kb_distill --batch 10 全部成功）。

**验证**：待蒸馏归零，覆盖率 784/784=100%，KB 健康分 92.0；全量模块
回归 1283/1283 通过。

## v6.9.80 - 2026-08-29 llm_router CLI 路径 NUL 字节净化 + 16h 遗留误诊纠正

**20h 健康检查发现：v6.9.79 修复后 `name 'max_tokens' is not defined`
并未如 16h 报告预期"自然消解"，17h-20h 每小时仍产生 200-500 条
NameError。溯源定性为 16h 遗留提示误诊**：

1. **误诊纠正（v6.9.79 第 6 条）**：持有旧版 llm_router 的并非
   "hermes gateway 常驻进程"（gateway 跑 hermes-agent venv，不导入
   本项目 llm_router），而是 `/tmp/rebuild_kb.sh`（今晨 09:26 BJ
   手工启动的知识库存量重构总控）阶段 3 的 Python 子进程（PID 40206，
   10:04 启动，stdin 注入脚本）。该进程全生命周期持有修复前模块，
   API provider 全灭 NameError、每次调用降级 CLI（60-184s）。
2. **NUL 字节缺陷（本轮修复）**：raw 论文正文偶含 `\x00`（PDF
   抽取残留，当日实测 6 篇）。CLI 路径 `subprocess.run` 参数遇 NUL
   抛 `ValueError("embedded null byte")`——API 降级期全降级链仅剩
   CLI 时 7 provider 全灭、该篇蒸馏终态失败（重构批次 ✗115 中的
   确认成因之一；kimi 另有内容审查 400 拒答）。修复：`call()` 入口
   统一净化（system_prompt + messages content 剥离 `\x00`，快速
   路径零改写），API/CLI 双路径一致防御。
3. **重构脚本运行态（仅报告，未干预）**：阶段 3 进度 460/784
   （✓345 ✗115），速率约 1 篇/分钟，预计今夜 ~01:30 跑完。失败的
   115 篇无数据丢失（旧摘要级 wiki 页保留；无 wiki 页的留在
   pending_distill 由明日 12:50 lc-kb-distill 以修复版代码重试，
   新进程自动加载 v6.9.79/80 修复，API 路径恢复后 JSON 载荷本就
   容忍 NUL）。脚本产物（760 raw has_fulltext 标记 + 534 wiki 页）
   待跑完后由下一轮健康检查随附提交。
4. **回归**：新增 `test_llm_router_nul_sanitize`（7 断言：CLI 参数
   无 NUL / API 载荷无 \u0000 / 干净输入零改写，subprocess 与
   urlopen 双打桩零真实调用），已注册；`--module` 全量全绿。

## v6.9.79 - 2026-08-29 周末输出链三连缺陷修复：萃取缺键 KeyError + llm_router max_tokens NameError + sources 拼接 TypeError

**2026-08-29 14:40 BJ output_extract_daily_knowledge 终态失败（运行
22s 即崩，非超时），weekly_report 依赖链阻塞，本周周末输出报告无法
生成；16:35 BJ 手动补跑再暴露两层隐藏缺陷——三个 Bug 叠加把知识
出口链完全锁死，全部修复后 16:47-16:48 BJ 端到端恢复（extract done
→ weekly_report done → weekend-output-report-2026-08-29.md 落盘）**：

1. **KeyError('title')（表层）**：LLM 返回的萃取 JSON 中有条目缺
   `title` 键（people 缺 `name` 同型），
   `weekend_pipeline/output_jobs.py` 裸取 `item["title"]`，单条缺键
   拖垮整批萃取。该 job `repair_attempts=3` 已耗尽、`attempts=1`
   不满足解锁条件，当周恢复仅剩 24h 冷却后 auto_unlock 一条路。
   修复：`_item_title` 守卫（缺键/非 dict/空串/纯空白 → 跳过并计数
   `skipped_invalid`），覆盖 output_jobs 两函数 +
   knowledge_output CLI 两路径。
2. **llm_router NameError（中层，影响面最大）**：`LLMProvider.call()`
   收下 `max_tokens` 参数却不传给 `_call_api`，而 `_call_api` 的
   payload 构造引用 `max_tokens or 4096`（未定义名）——**API 类型
   provider（minimax 主链 + minimax-fallback）每次调用必抛
   NameError**，14:40 起全靠 claude/kimi CLI 降级兜底（14:41 日志
   实证"从 minimax 降级/fallback"），kimi 又间歇拒绝高风险请求
   （400），降级链一旦全断则所有 LLM 调用失败。修复：`_call_api`
   签名补 `max_tokens` 并由 `call()` 传递；16:47:43 日志实证
   `provider=minimax (主模型)` 直接成功（33.57s）。
3. **sources 拼接 TypeError（深层）**：`_write_wiki_page` 的
   `existing_fm.get("sources", []) + sources`——`_extract_frontmatter`
   为朴素行解析（非 YAML），多行 list 形态的 sources 解析为空串、
   单行标量解析为 str，**同一概念页第二次被萃取命中即抛
   `TypeError: can only concatenate str (not "list") to str`**
   （16:35 BJ 实证）。修复：读侧归一（非 list → [str] 或 []），
   output_jobs 与 knowledge_output 同型双修。
4. **运行时补救**：extract job 经 `reset_failed_job` 两次重置后由
   系统自身 `--run-next` 入口补跑成功；output 阶段 5 job 全 done、
   `stage_status.output=done`，本周产物零丢失。
5. **回归**：新增 `test_weekend_extract_guard`（18 断言：cron 路径 +
   CLI 路径 + 助手边界 + sources 归一，零 LLM/隔离目录零污染）与
   `test_llm_router_max_tokens`（4 断言：NameError 消除），均已注册；
   `--module` 全量 **1276/1276 全绿**（1254+22）；
   `knowledge_output.py --self-check` 通过。
6. **遗留提示**：hermes gateway 常驻进程在重启前仍持有旧版
   llm_router 模块（16:46:58 仍有两条 NameError 日志），新进程已
   全部走修复版；建议下次 gateway 重启窗口自然消解，无需处置。

## v6.9.78 - 2026-08-29 申请书质量下降根因修复：critic 粗体得分误读为权重列 + references 异口径混判 + 回退按 round 号失效

**用户报告"申请书质量下降"，全链路排查定位出三层叠加缺陷（数据实锤：
8 课题全部曾从最佳 0.79-0.86 退化至 0.5-0.7，4 课题触发自动回退；
bsv pass4 五连降 0.75→0.67→0.66→0.50 被误判"连续3轮质量下降"暂停）**：

1. **解析缺陷（核心根因）**：critic 报告实测把维度得分写成粗体
   `**0.70**`（bsv R1 references 报告 `| 严谨性（rigor） | 0.50 | **0.70** |`），
   `_extract_dimension_scores` 的 `fullmatch(0\.\d+)` 匹配不上粗体单元格，
   误取前一列权重 0.50 当得分——references 真实综合分 0.78 被记 0.50。
   全量扫描 74 份历史 critic 报告，7 份（9.5%）受污染（bsv R1/R5/R10、
   attosecond-streaking R1/R3/R4/R5，最重者 bsv R10 完整性 0.82 被记 0.20）。
   修复：单元格先剥离 markdown 强调（`**` `__` `` ` `` `*`）再判纯数字。
   该解析器为 optimize/executor 双路径共用（LifecycleCronController 继承），
   一处修复两链路同时生效。
2. **口径混判**：references 轮为 2 维专用口径（rigor/completeness 均值），
   与章节 4 维加权分（含锚点绑定/AI 天花板 cap）不可比，但 `_check_done`
   的收敛/下降/平台/无提升窗口与 `should_auto_rollback` 均混用同一分数
   序列——口径切换本身即制造虚假下降。修复：references 条目不参与连续性
   判定（与 v6.9.62 dims_partial 防线同构）。
3. **回退失效**：`should_auto_rollback` 按 round 号判"最佳轮=最新轮"，
   而微调度器一轮内 5 个 section job 共用同一 round 号（审核退回后 pass
   重置全遍归 1），条件恒成立，回退在微调度器路径永不触发（bsv 连续
   4 轮下滑至 0.5 无回退的直因）。修复：改按条目位置判定最佳。

**配套**：references critic prompt 评分块格式契约加固（明确禁止加粗/
表格包裹评分数字）；bsv 已按官方 transition API 退回 optimizing
（原因写入 transition_history，遍次归档正常），人工队列刷新清空其
108h 残留待办。历史 score_history 不重写（报告文件按遍覆盖，无法
忠实重建，保留审计原貌）。

**验证**：真实 bsv R1 报告端到端复现（修复前 rigor=0.50/completeness=0.50
→ 修复后 0.70/0.85，references 计分 0.50→0.775）；新增回归 8 组用例
（维度解析粗体表 4 组 / 收敛检测口径隔离 2 组 / 回退同轮号与口径过滤 2 组）；
全量回归 1254/1254 通过（--scenario 16/16、--persona 38/38、py_compile 通过）。

## v6.9.77 - 2026-08-29 deep_read_pipeline 头读窗口同类修复（1200B→8192B）+ backfill 冗余读清理

**00h 健康检查发现（v6.9.75 同类缺陷）**：v6.9.75 修复了 kb_distill gate2
的 500B 头读窗口（agent_rejected 位于 title/authors 之后，30+ 作者论文
偏移 660B+ 溢出），但同日新增的 `deep_read_pipeline._raw_frontmatter`
仍用 1200B 窗口——kb_importer 字段序中 `score_agent` 同样位于
title/authors 之后，35+ 作者大协作组论文（物理领域百人作者常见）偏移
可超 1200B，score_agent≥8 的高分论文会被误判为摘要级、漏出深度阅读
队列。当前生产暂未触发（R1 数据流断点致 score_agent 字段尚未到达
raw .md），属 R1 修复后必然引爆的潜伏缺陷。

**修复**：
1. `_raw_frontmatter` 头读窗口 1200→8192（与 gate2 修复口径一致，
   覆盖 100+ 作者），并改用 `with` 上下文管理器（修文件句柄泄漏）。
2. `backfill_pdfs` 删除冗余的二次 1200B 头读（既重复又泄漏句柄），
   复用 `_raw_frontmatter` 的解析结果。
3. `kb_distill._deep_wiki_rel` 移除未使用的 `distill_raw_to_wiki as _d`
   死导入。

**验证**：新增 `scripts/tests/test_deep_read_long_authors.py`（4 用例：
40 作者偏移 ~1800B 命中 / 100 作者偏移 ~3400B 命中 / 短作者低分仍摘要级
/ 超窗口 agent_rejected 可见性），已注册 self_test --module 清单；
`deep_read_pipeline --self-check` 增加大作者回归用例；全量回归通过。

## v6.9.76 - 2026-08-28 逃生分桶触发：critic/monitor 超时独立计数，异供应商成功不再抹掉挂起证据

**08-28 晚运转暴露的盲点**：模型逃生机制（v6.9.69）上线当晚，critic/monitor
（profile 主模型 glm-5.3@zai）三连 900s 触顶（20:50/21:45/22:50），但逃生
未触发——全局长超时计数被 writer（主模型 MiniMax，健康）的成功清零，zai
挂起的证据被异供应商的成功抹掉。实测确认故障形态：critic 短请求 7.6s
正常、zai 只对"大上下文长输出"请求挂起（与 08-27/28 危机同模式）；且
600s（hermes stale giveup 切换）+ 700s（minimax 实际生成，writer 实测
约 12 分钟）> 900s 击杀线，hermes 内部降级即使成功也来不及完成。

**修复**：
1. circuit_breaker 分桶计数（`consecutive_escape_step_timeouts`）：
   ESCAPE_TRIGGER_STEPS={critic, monitor}（zai 主模型步骤）的长超时独立
   累积，阈值 2 次（ESCAPE_STEP_THRESHOLD）即激活逃生；writer 等异供应商
   步骤的成功只清零全局计数、不清桶；桶内步骤成功才清桶。
2. record_job_result 增加 step 参数；微调度器回报时透传 job step。
3. 新增 CLI `--escape-open REASON`：人工确认主模型对长输出挂起但计数
   未达阈值时直接切换备用（今晚 21:18 已手动激活，21:48 起第一次
   主模型试探）。

**验证**：circuit_breaker 自检 17 路径全过（新增分桶触发/桶清零/手动激活
3 条）；test_mechanism_hardening 16.7-16.8 新增 6 用例；全量回归
1237/1237；生产实测 escape_override_target() 返回 minimax-cn/MiniMax-M3。

## v6.9.75 - 2026-08-28 蒸馏 gate2 过滤窗口修复 + kb_distill 测试净环境加固

**修复①：pending_distill_list 头读窗口 500B→8192B**。v6.9.73 落地的
gate2 过滤器（agent_rejected: true 不进蒸馏队列）只读 raw 文件前 500
字节，而 kb_importer 的 frontmatter 字段序中 agent_rejected 位于
title/authors/agent_note **之后**——大协作组论文（30+ 作者）该行偏移
实测 660B+，溢出 500B 窗口致被拒论文漏检、仍消耗蒸馏配额。字节算术
实证：40 作者构造用例偏移约 850B。8192B 可覆盖 100+ 作者（title 300B +
authors 3000B + 摘要前置字段），附带把裸 open().read() 改为 with 语句。

**修复②：test_kb_distill_created_ts v6.9.15 用例净环境加固**。该用例
依赖 /tmp/fake/raw/x.md 残留文件，distill_one 读取 raw 全文（分层蒸馏
判定 has_fulltext）后净环境（新沙箱 / 清理后）必挂 FileNotFoundError
——改为用例自建自清（finally unlink），前后向兼容（无 read_text 的
旧代码路径同样通过）。

**回归**：self_test --module 1231/1231 全绿（1228 基线 + 本轮 3 条新
断言：偏移>500 前置校验 / 被拒过滤 / 未拒保留）。

**附带对账**：v6.9.74（蒸馏路由+并发锁）提交时未带 VERSION（文件停留
6.9.73），本次一并推进至 6.9.75。并行会话在途的"分层蒸馏"特性
（DEEP_DISTILL_PROMPT / distill_one 五要素）不属本提交，保留工作区。

## v6.9.74 - 2026-08-28 蒸馏路由修复+并发锁（补记，原提交 f119fec 未记 CHANGELOG）

- kb_distill 偏好链 glm→minimax 优先（glm 对蒸馏长 prompt 实测 104s
  失败/篇，minimax 48s 成功/篇）
- run_batch 加 file_lock 进程互斥（防双时段 cron 与批量并发重复蒸馏，
  抢不到锁温和退出 lock_busy）
- 20h 健康检查运行时实证：批量蒸馏 1.5h 内积压 365→137，minimax
  17-48s/篇稳定

## v6.9.73 - 2026-08-28 入池双门筛选：agent 相关性打分第二道门落地

**评分分布审计的延伸决策**（用户提供分布图后拍板）：DeepXiv hybrid 模式
score 自 2026-07 起退化为占位值（0.5/0.33，无区分度，实测时间线：5 月
98% 真分→7 月 100% 固定值），gate1 单独已不足以筛质量。用户拍板方案：
保留低分 gate 做第一道；新增 agent 相关性打分做第二道；入池频率 4 次/天
保持。

**双门结构**：

- **Gate 1（脚本内，已有）**：MIN_DEEPXIV_SCORE=0.5——挡 DeepXiv 低分
  档（0.33）；arXiv 直抓（固定 0.5）与缺分条目放行。
- **Gate 2（agent 打分，本轮新增）**：简报 cron 新增 Step 1.5——agent
  按研究方向词表（scope-terms.json 85 词，覆盖研究主题而非仅 optimizing
  课题）逐篇判断相关性，1-10 打分写回池 json（score_agent/agent_note），
  <4 分标 agent_rejected=true 且不生成知识库简报。判断要求以物理内涵为
  准（禁字面匹配、禁套话）。

**下游贯通**：

- kb_importer：池 json → CoPilot frontmatter 透传 score_agent/agent_note/
  agent_rejected 三字段。
- kb_distill.pending_distill_list：agent_rejected=true 的条目不进蒸馏
  队列（raw 保留作记录，不消耗配额）。
- 简报 cron prompt 重建（Step 1.5 + 输出格式加 GATE-2 行）；重建过程中
  发现 hermes CLI create 不接受位置 prompt（版本差异），走 create
  no-agent 占位 → cron edit --agent --prompt 两步路径完成。

- 验证：编译通过；pending 判定过滤逻辑回归通过；四层 1228/16/38/1455
  全绿。观察点：下轮 18:23 cron 的 GATE-2 输出（打分数/通过数/拒绝数）。

## v6.9.72 - 2026-08-28 知识库正向作用审计 + 蒸馏双时段 + 入池 gate - 2026-08-28 知识库正向作用审计 + 蒸馏双时段 + 入池 gate

**知识库→申请书优化正向作用审计**（数据实证，详见会话记录）：

- **lit_search 联网检索链（强正向）**：申请书 references 的实际主要来源——
  每次 gap 驱动检索 10 篇直接进 02_literature 供 writer 引用；qg references
  与 KB 重合 18%（11/60）、berry 11%、attosecond 3%。
- **KB context 注入（运转中，中等强度）**：executor KB-first 预检索实测
  返回 1571 字符/10 篇命中注入 writer prompt（去重 + 背景）。
- **课题凝练链（间接但真实）**：周末 input→cluster→topic_match→
  idea_generator 已产出 berry/attosecond 两课题（source=auto_idea）。
- **蒸馏 wiki（弱正向，覆盖不足）**：笔记覆盖率仅 3.6%（756 篇缺笔记），
  限制 KB context 命中强度——蒸馏加速正是做实此渠道。

**蒸馏端加速**：新增 lc-kb-distill-pm cron（每日 18:50，--auto + kb_linker
补边），与 12:50 主时段合计日蒸馏 40 篇（FIFO 取天然不重复，时段错开无
并发），350 篇积压约 9 天清完（不计新进）。

**入池端 gate**：generate_briefing_v3.py phase1 新增 MIN_DEEPXIV_SCORE=0.5
（2026-07 规划项落地）——DeepXiv score <0.5 不入池；arXiv 直抓（固定
0.5 分）与缺分条目默认放行。实测池中 score 中位 0.5、<0.5 占 21%，
gate 后日进量约 12→9 篇。入池频率保持 4 次/天不变。

注：gate 脚本与 cron 位于 hermes 侧（~/Desktop/hermes_workspace 与
~/.hermes），不在本仓库 git 内，本条目为变更留档。

## v6.9.71 - 2026-08-28 蒸馏积压画像 + research/projects 域下线（精炼第四阶段之一） - 2026-08-28 蒸馏积压画像 + research/projects 域下线（精炼第四阶段之一）

**积压画像（用户问询答复）**：待蒸馏 350 篇全部来自 knowledge/raw/papers
（arXiv 论文全文缓存），由简报检索 cron（00/06/12/18:23 每天 4 次）+ 周末
input collect 写入，全部为 2026 年 8 月单月入池（birth time 证实无更早
存量）。宽口径主题分类：磁性与交变磁 23%、HHG 12%、阿秒/超快 12%、
二维/莫尔 9%、拓扑 3%、强场 3%，其余 31% 经三轮抽样确认仍是领域相关
（RABBITT、光电子谱、Wannier 动力学、激子等）——**没有垃圾、无删减
空间，纯消化速度问题**。

**research/projects 域下线**（用户决策）：

- 前端三文件已于 v6.9.70 归档；本轮下线后端：两路由模块
  （web_routes_research/projects.py，38+35 条路由）归档至
  docs/archive/refactored-20260828/。
- **解耦**：web_server 移除两 Mixin/路由表/research 独立分派器及
  self-check 断言；tasks 路由依赖的两个 hermes 派活函数抽离为新模块
  hermes_dispatch.py（写 plans/ 契约 + 异步派活回写），tasks 调用点
  全部切换。
- 测试基线：test_web_api 移除两域 13 条路由断言与 1 个扩展测试方法。
- 实测：活路由 /api/tasks 200、下线路由 404；web_server self-check 通过。

**影响面**：路由面 -73 条（295→222）；归档文件可随时 git 还原恢复。

- 验证：四层回归 1228/16/38/1455 全绿；实测路由下线与活路由无扰。

## v6.9.70 - 2026-08-28 全项目精炼：三阶段落地（修假动作/删死资产/降低价值运行） - 2026-08-28 全项目精炼：三阶段落地（修假动作/删死资产/降低价值运行）

按四线排查（后端调用图/cron 实效/前端触达/数据域健康）产出的精炼方案，
三阶段执行完毕。

**第一阶段：修"假动作"（账实相符）**

- **备份幂等判断 bug（数据安全级）**：list_backups 按文件名排序取"最新"，
  8/27 晚 6.8MB 的 research_proposals 专项备份（--only）在字典序上压过
  837MB 全量包，使 auto_backup 的 24h 幂等判断持续被"喂饱"而跳过——
  lc-daily-backup 自注册起 0 次真实全量执行。修复：--only 专项包文件名
  加 partial 标记 + 幂等判断排除 partial + 存量专项包重命名。修复后
  手动触发立即产出 865MB 全量包（含 research_proposals 3418 文件）。
- **lc-daily-sync 删除**：wrapper 实际跑 _self_check() 冒充同步（每晚
  自检即退出、14 天零 23:00 同步记录），且 12:40 kb-sync 已覆盖全部
  真实增量（日均 0-4 篇）。cron+manifest+wrapper+测试基线四处清除；
  sync_engine __main__ 默认行为改为真 sync_all（--self-check 显式自检），
  消除"调错入口"陷阱。
- **lc-prompt-optimize 暂停**：只增不减（41/41 append）、审计虚标
  verified（与文件 mtime 矛盾）、writer SOUL 724B→12.5KB 而分数净 -27。
  cron 删除 + 移出期望拓扑（含恢复命令注释）+ 测试基线同步。整改项
  （hash 校验/reap 配额/体量上限）留待恢复前完成。
- **monitor 告警降噪**：去重窗口 4h→24h + 夜间静默（22:00-08:00 只入
  缓存不发送，次日工作时段补发）——此前 7 天 90 条通知 90% 是同批
  卡死 job 复读。

**第二阶段：删死资产（11 项归档/删除）**

- 归档至 docs/archive/refactored-20260828/：citation_manager / taste_engine
  / quality_evaluator / lineage_tracker（4 个零 import 遗迹模块）+
  web/js/learning|projects|research.js（3 个死前端文件，96 端点零触达）。
- 移入 scripts/manual_ops/（手动运维工具与主代码隔离）：daily_health_check
  / kb_repair_papers / kb_fill_wiki_notes / regenerate_optimization_reports
  / check_boundary / alias_learner。
- 删除 memory/proposal-initial-scores.json（全项目零读写）。

**第三阶段：降低价值运行**

- lc-repair 降频 6h→12h（28 次扫描/7d 有效动作近零；stale 阈值随间隔
  自适应 24h，宽限测试同步更新为 13h 正常/26h 告警两档）。
- logs/healthchecks 滚动清理（保留 7 天，39 份过期清除；守护逻辑挂入
  lc_daily_backup.sh 每日执行）。

**明确不动（价值核心确认）**：微调度器（85% 有效派发）、kb-sync/kb-distill
（唯一同步与消化口）、周末四任务、三子包（零死文件）、4 个高频模块
（零死函数）、备份轮转。

- 验证：四层回归 1228/16/38/1479 全绿；cron 拓扑对账 0 问题；全量
  备份修复后实测落盘。

## v6.9.69 - 2026-08-28 模型逃生机制：主模型静默挂起时备用模型接管而非停摆 - 2026-08-28 模型逃生机制：主模型静默挂起时备用模型接管而非停摆

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
failed job 重试与 stale 清理；而微调度器 cron（`*/15 * * * 1-5`，
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
