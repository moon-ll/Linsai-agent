# 评审团深度修改报告
执行者：engine亲审 ｜ 课题：general-ssh-weyl-20260920 ｜ 时间：2026-10-03

> 方法：零外部 LLM/CLI。定点核查基于通读五章 + 知识库逐篇核对（按 arxiv_id 检索 `knowledge/wiki/papers/`，覆盖 [8][9][11][12][13][14][15][16][20][23][24][25][26][29][30] 共 15 处关键断言）+ 评审链追溯（critic-round-3/4、05_review/.archive-targeted）。三视角 findings 见同目录 panel-researcher/critic/reviewer-findings.md。

## 处置总表

### A. 历史遗留问题（O1–O16，全部清账）

| # | 问题 | 处置 | 修改位置 | 说明 |
|---|------|------|----------|------|
| O1 [critical] | "TaP 的 2–3 个数量级增强（[16]）"归属失实 | 已修（历史轮） | rationale §2.3 | 现文"TaP 严格立方律（[16]）"，KB 2508.16166 证实 [16] 无量级表述；本轮复核通过 |
| O2 [critical] | Kagome"两到三个数量级"失实 | 已修（历史轮）+ 本轮补正 R2 | rationale/content/scheme 全链 | 正文全链已为"上限两个数量级"；本轮进一步修正归属对象（见 R2） |
| O3 [high] | [9]"数个数量级"矮化"最高 14 个数量级" | 已修（历史轮）+ 本轮补残尾 V2 | rationale L21、content L27；references [9] 注 | 正文已达标；refs[9] 注"数个数量级"残留本轮同步为"最高增强达 14 个数量级" |
| O4 [high] | 禁用词（锚点/锚定/口径/落地）9 处 | 已修（历史轮）+ 本轮清残尾 | rationale L7"锚文"→"两篇原始文献"；references [30] 注"锚点"→"基准值" | 五词终态 grep 清零 |
| O5 [high] | 超长句 4 处 + 元话语"需要特别说明" | 已修（历史轮） | rationale §2.2/§2.3 | 本轮全文复扫 prose 超长句 0 残留 |
| O6 [critical] | content 10 处 + scheme 3 处"2-3 个数量级/100-1000 倍" | 已修（历史轮）+ 本轮清最后残留 | references [20] 注（原残留"2–3 个数量级"） | grep "2-3/2–3/两到三/100-1000" 五文件清零 |
| O7 [critical] | R≥2 依据"取下界 100 倍"方向词错向 | 已修（历史轮） | content L53/L67 等 | 现文"取该量级增强上限 100 倍对应的对数尺度比值"，方向已正 |
| O8 [high] | "比普通绝缘体高 2-3 个数量级已复现"无引孤儿断言 | 已修（历史轮） | content §2.4 | 断言已删，本轮复核通过 |
| O9 [high] | content 禁用词 7 处（门控/闭环/口径/锚点） | 已修（历史轮） | content 全文 | grep 清零 |
| O10 [high] | content 自引用 18 次超阈 | 已修（历史轮） | content 全文 | 本轮实测 0 次（阈 15） |
| O11 [critical] | X+Y+Z"≥95%"与"=100%"两套判据互斥 | 已修（历史轮）+ 本轮补 rationale 侧残尾 V1 | content L43/L65/L81、scheme L51/L123/L125/L253；rationale L79 | 五章链路统一"≥95%（σ₀/σ_full<0.05）"；rationale L79 残留"= 100%"本轮改齐（V1） |
| O12 [critical] | scheme 与 refs[20] "2-3 个数量级（100-1000 倍）/取下界"残留 | 部分修改（历史轮改 scheme）→ 本轮收尾 | references [20] 注、scheme L41 | refs 注残留本轮修；连带发现归属错置（R2）一并修正 |
| O13 [high] | "三条备选路径"实为两条；"如 §3.1 所述"死指针 | 已修（历史轮） | scheme L33、L203 | 本轮复核通过 |
| O14 [high] | 年度计划 2026.01 起于建档前 | 已修（历史轮） | scheme §6 | 现为 2027.01–2030.12，论文撰写分流第 3–4 年 |
| O15 [high] | scheme 自引用 16 次超阈 | 已修（历史轮） | scheme 全文 | 本轮实测 4 次（阈 15） |
| O16 [high] | §3.2.2 判据句同段重复两次 | 已修（历史轮） | scheme §3.2.2 | 本轮复核通过 |

**历史遗留结论：16 条全部清账。6 条 critical（O1/O2/O6/O7/O11/O12）零残留（grep 复核），10 条 high 全部已修或本轮收尾。**

### B. 本轮新发现（researcher R / critic C / reviewer V）

| # | 问题 | 处置 | 修改位置 | 说明 |
|---|------|------|----------|------|
| V1 [critical] | rationale L79"X + Y + Z = 100%"与统一判据"≥95%"互斥（O11 残尾） | 已修 | rationale L79 | 改"三者之和在弱耦合近似下趋于 100%，验收判据为 X + Y + Z ≥ 95%（闭合条件 σ₀/σ_full < 0.05，定义见研究方案 §2.2）" |
| R1 [high] | [26] 幂律"由 2.3 渐降至 0.3"误并裸膜（2.3）与微腔样品（0.9→0.3）两条曲线；KB 2510.01760 主页实测 | 已修（5 处） | rationale L39/L59、content L41/L81、references [26] 注 | 统一改"裸膜幂律指数约 2.3（近微扰），微腔样品随驱动增强幂指数由 0.9 渐降至 0.3，进入近饱和区"；方向三"识别 Boltzmann 失效边界"用途不变 |
| R2 [high] | refs[20] 注残留"2–3 个数量级"；且"上限两个数量级"被错置到"拓扑半金属相"名下（KB 2508.15631 fulltext：该相恰报约 3 个数量级/7 次谐波/Fig.6；摘要口径才是 up to two orders——critic-round-4 引证摘要原文） | 已修（12 处） | rationale L25/L39/L55/L59；content L5/L17/L21/L53/L67；scheme L41/L59；references [20] 注 | 两级表述：拓扑相增强上限两个数量级（摘要口径）+ 正文计算中拓扑半金属相 7 次谐波最高约 3 个数量级（预印本）；R≥2 依据链（上限 100 倍→对数比值 2）不受影响 |
| R3 [high→待核] | Δκ≥20% 依据"[24] 报告统计涨落约 10-15%"在 KB [24] 页（解析理论文，2005.09449）无任何记载，与该文性质不符 | 待核（保留原文） | content L33、scheme L45 | 无法核实不下结论；建议后续以自研引擎参数扫描涨落自检重建该阈值依据 |
| V2 [high] | refs[9] 注"数个数量级"与正文"最高达 14 个数量级"不同步 | 已修 | references [9] 注 | 同步为"最高增强达 14 个数量级" |
| R4 [medium] | scheme L137"激子束缚能 ~60 meV 与光子能量 ~3 eV 跨三个数量级"算术失实（实为 50 倍） | 已修 | scheme §3.3.1 | 改"相差约 50 倍，激发时间尺度横跨激子动力学与带间电子动力学两个区间" |
| R5 [medium→待核] | ① Δt≤10 fs 依据"[14] 30 fs 有效寿命窗口"KB 无载（摘要级笔记）；② refs[14] arXiv:2304.06697 与 KB 元数据 2305.02025 冲突 | 待核（保留原文） | scheme L49、content L33、references [14] | 两处均无法单方裁决，保留并标注；建议以 arXiv 原文页核编号与 30 fs 出处 |
| R6 [medium] | [29] 方法误标"rtTDDFT"（该文标题即 via real-space trajectories，KB 证实实空间轨迹替代 TDDFT） | 已修（2 处） | rationale L45、references [29] 注 | 改"实空间轨迹模型"；MoS₂ 双峰/hBN 单调等结论断言经核对相符 |
| C1 [medium] | rationale L25 超长段 591 字 | 已修 | rationale §2.2 | 在"Bi₂Se₃ 类三维拓扑绝缘体…"句前拆两段（概念与模型进展 / 三维材料平台） |
| C2 [medium] | rationale L39 超长段 466 字 | 已修 | rationale §2.3 | 在"该结果给出三条独立的实验标定基准"句前拆段（与 R1 同点） |
| C3 [medium] | content L43 单句 126 字（>120 必拆） | 已修 | content §2.4 | 冒号列举后断句 |
| C4 [medium] | 内部文件名"content §2.6"泄漏进申请书正文 | 已修（2 处） | scheme L37/L63 | 改"研究内容 §2.6" |
| V3 [medium] | refs L77"共 172 处编号引用"与实测不符 | 已修 | references 编号映射说明 | 实测 rationale 54 + content 45 + scheme 61 = 160 处，改"160 处"；"35 条全部被引"复核属实 |
| V4 [medium] | scheme L59"依据见 §5.3"↔ L231"同 §2.2"循环指针，两处均无实文 | 已修 | scheme §2.2 ΔI_gap 条目 | 依据句（[20] 上限两个数量级→100 倍对数比值）落位 §2.2，§5.3 指针自此有效 |
| R7 [low] | rationale L79"非平衡散射贡献明显超过拓扑通道"超出 [26] 支持范围 | 已修（随 V1 同句） | rationale L79 | 改"微腔近饱和区响应由场驱动非平衡动理学主导"（KB 证实） |
| R8 [low] | rationale L7"（亦即 Lewenstein 小组）"用语不当 | 已修 | rationale §1 | 改"（Lewenstein 小组的工作）" |
| R9 [low] | scheme L29 Crank-Nicolson（隐式）与 CFL 条件并列表述张力 | 已修 | scheme §2.1 | 改"显式格式的时间步长 Δt 须满足稳定性（CFL）条件" |
| C5 [low] | 其余 >400 字段 9 处（rationale L59/L79；content L21/L33/L39/L41/L49/L53/L67） | 不适用 | — | 逐段核查句长全部 ≤120 字、80–120 字句每段 ≤3；均为"总起句+三指标"列举块或科学问题承接段，机械拆段破坏列举结构 |
| C6 [low] | 引用角标密度 rationale 54 / content 45 / scheme 61，超出 10–20 次区间 | 不适用 | — | 文献综述型立项依据+指标体系章的体裁密度；rigor 0.66 为最弱项，删引直接损伤严谨性；阈值按短文档校准不适用整章 |
| C7 [low] | 禁用词残尾：rationale L7"锚文"、refs[30] 注"锚点" | 已修（2 处） | rationale L7、references [30] 注 | 见 O4 行 |
| C8 [low] | content G4（L67）与 §2.5（L53）"R≥2 数值依据"整句级重复 | 已修 | content L67 | 改短指针"R ≥ 2 的数值依据见 §2.5（…）"，阈值与判定语句保留 |

### C. 复检通过项（无需修改，记录备查）

- **创新增量**（R-评估）：三创新点相对 [14][20][8][6][9]-[13] 的增量边界成立，无越界宣称。
- **V5 指标口径对表**：14 项关键指标（R_HOTI/S_edge/δ_FP/G1 成功率/Δκ/η_SF/Δt/X+Y+Z/σ_dec/R²/R/T/ΔI_rev/双基线 <10%）跨章逐点一致（V1 修复后）。
- **V6 章节衔接**：三方向递进链三章一致；rationale→content→scheme 全部跨章指针有效；scheme TaP 校核窗与 KB 2508.16166 实验参数对齐。
- **V7 引用编号**：1–35 连续无跳号、无孤儿条目、预印本 10 条清单与正文标注一致、格式统一。
- **V8 full_review**：仍为 ≤3000 字"全文骨架"语义（标题索引+程序维护声明+过程材料排除声明），无处置记录混入，未改动。

## 修改统计

- 发现问题合计 **21**（critical 1 / high 4 / medium 9 / low 7）；另有复检通过项 5、历史遗留 16 条核对。
- 处置：**已修 17 ｜ 部分修改 0（O12 以"历史轮部分+本轮收尾"入 A 表）｜ 不适用 2（C5/C6）｜ 待核 2（R3/R5）**。

## 改动文件（8 个，全部位于本课题目录内）

- `/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-ssh-weyl-20260920/04_proposal/sections/rationale.md`（7 处）
- `/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-ssh-weyl-20260920/04_proposal/sections/content.md`（10 处）
- `/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-ssh-weyl-20260920/04_proposal/sections/scheme.md`（6 处）
- `/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-ssh-weyl-20260920/04_proposal/sections/references.md`（7 处）
- `/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-ssh-weyl-20260920/06_panel/panel-researcher-findings.md`（新建）
- `/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-ssh-weyl-20260920/06_panel/panel-critic-findings.md`（新建）
- `/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-ssh-weyl-20260920/06_panel/panel-reviewer-findings.md`（新建）
- `/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-ssh-weyl-20260920/06_panel/panel-writer-modification-report.md`（本文件）

未触碰：`_lifecycle.json`、`05_review/`、其他课题目录；未建备份副本；未执行任何 git 操作。`04_proposal/full_review.md` 经 V8 核查语义合规，未改动。修改后复核：历史 P0 词串 grep 清零、禁用词清零、prose 超长句清零、X+Y+Z 判据五章统一、引用编号 1–35 完整且计数注明一致。

## 遗留与风险

1. **R3 待核**：Δκ ≥ 20% 阈值所引 [24]"统计涨落约 10-15%"在知识库 [24] 页（2005.09449，解析理论）无载、与该文性质不符——若后续核实为无据，需以自研引擎参数扫描涨落自检重建该阈值依据（content L33、scheme L45 两处联动）。
2. **R5 待核**：refs[14] arXiv 编号（2304.06697 vs KB 元数据 2305.02025）与"[14] 30 fs 寿命窗口"（scheme L49）均需以 arXiv/PRB 原文页最终裁决。
3. **R2 双源张力**：[20] 摘要口径（up to two orders）与知识库全文级深读（拓扑半金属相约 3 个数量级，Fig.6）已用两级表述兼容并注明预印本属性；刊本出版后建议以正文 Fig.6 复核一次，S_edge=0.2 与 R≥2 两条阈值链预留了"刊本核实后修正余量"（scheme L41）。
4. **C6 密度豁免**：三章引用角标 160 处系体裁性密度，本轮未删引；若后续轮次仍被程序罚分，建议以"复核性引用改指针"方式收敛 scheme §4 可行性分析中的重复引证，而非动立项依据。
