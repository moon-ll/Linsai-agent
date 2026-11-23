# 评审团复核报告（第二轮）

复核员：独立复核（fresh context）｜ 课题：key-transient-quantum-phase-optical-20260726 ｜ 时间：2026-10-05

复核纪律：只验清单，不做全量评审；一切以磁盘当前文本为准重新取证（grep/读原文/程序化复测），不采信修改报告自我声明，不凭记忆放行。文献溯源仅用 knowledge/wiki/papers/ 在档页与 knowledge/raw/pdfs/_text_cache/ 全文缓存。

## 逐条判定

### researcher 视角（R2-1 至 R2-9，9 条）

| # | 问题（短） | 判定 | 证据 |
|---|-----------|------|------|
| R2-1 | Mokhtari "15–30 倍实验标定"误标（HIGH） | 已解决 | grep "实验标定" 五章 0 命中（旧表述清零）。rationale.md L55 现文："Mokhtari 等[27]于 2026 年实验测量 77–500 K 温区 HHG 产额随温度的显著变化（随降温显著上升），其一维链模型外推液氦温区预测产率增强 15–30 倍"。KB 页 wiki/papers/2026-2604_07543-*.md 亲证：L37"温度范围 77 K 至 500 K"、L61"所有产额均随温度降低而显著增加"、L64"由于实验最低温限制在 77 K，模型外推到液氦温度时预测高次谐波谱将有 15–30 倍的增强"——实验量/外推量改写与 KB 逐句相符 |
| R2-2 | McIver 2020 具名无编号、表内无条目（HIGH） | 已解决 | references.md [17]："McIver J.W., Schulte B., Stein F.-U., et al. Light-induced anomalous Hall effect in graphene. Nat. Phys., 2020, 16: 38-41. DOI: 10.1038/s41567-019-0698-y"；KB 页 1811.03522.md L36"正式发表于 Nature Physics 16, 38–41 (2020)；DOI: 10.1038/s41567-019-0698-y"、L32 作者三人（McIver/Schulte/Stein）逐项相符；rationale.md L35 正文挂点"McIver 等[17]于 2020 年在石墨烯中观测到光致反常霍尔效应" |
| R2-3 | [7] 实验验证论文未入表、"并获实验证实"悬空（HIGH） | 已解决 | references.md [8]："Baykusheva D., Chacón A., Lu J., et al. All-optical probe…Nano Lett., 2021, 21: 8970-8978. DOI: 10.1021/acs.nanolett.1c02145"；KB 主页 2021-2109_15291-*.md L156"Nano Letters 21, 8970-8978 (2021) — DOI: 10.1021/acs.nanolett.1c02145"、L157 前三作者（Baykusheva/Chacón/Lu）相符；rationale.md L21"由强场理论预言[7]并获实验证实[8]"。一手原文：raw/pdfs/_text_cache/2109_15291.txt L68-70"In a recent theoretical work, we predicted a unique enhancement…Bi2Se3 [30]. Here, we report experimental results."；该文其 [30]（L531-532）＝"Strong-field physics in three-dimensional topological insulators, Phys. Rev. A 103, 23101 (2021)"＝本表 [7]——[7] 理论预言定性一手定案无误 |
| R2-4 | Kiselev 定性断言无一手复核（LOW→待核） | 豁免（待核合规维持） | scheme.md L83 原文逐字保留："Kiselev[38]在 2026 年用参数不稳定性机制给出：反转对称中心晶体的 IR-active 声子在 Mathieu 共振条件下被驱动进入稳定的非平衡破缺态，可在原本被禁戒的二阶非线性通道产生强 SHG"（仅角标 36→38 随重排）；未凭记忆改写，符合待核纪律 |
| R2-5 | de la Torre 数值（~120 K/s、210 K）无在档佐证（LOW→待核） | 豁免（待核合规维持） | content.md L29 原文逐字保留："de la Torre 等[37]于 2025 年在热淬火 1T-TaS₂ 中证明 H-CDW 相可由 ~120 K/s 中等速率热淬火稳定到 210 K，且 C-CDW 与 H-CDW 共存于同一块体"（仅角标 31→37）；表 [37] 条目 Nat. Phys. 21: 1267-1274 与 Kim[36] KB 页侧面佐证身份相符 |
| R2-6 | r1 [21]（现[25]）Batista 理论/数值定性复核定案 | 豁免（复核通过） | raw/pdfs/_text_cache/2604_27750.txt 亲证：L119/L600 "time-dependent density matrix (TDDM) formalism"、L73 "spectra are simulated for each time delay"——数值模拟方法学成立；rationale.md L55 现文"Batista 等[25]于 2026 年从理论上证明"定性正确，无需改动 |
| R2-7 | 其余 r1 修正项 KB 抽查（6 项）＋Lesko 待核 | 豁免（复核通过＋1 项维持待核） | 6 项断言的 KB 源页均在档且主题相符（2606_02238 Faeyrman、2604_20388 Ilin、2608_02456 Kim、2511_13114 Zhao、2602_22578 Watanabe、Ono PRB 110）。Lesko[18]（rationale.md L37）SHG 探测/电流调制/TDDFT 细节原文逐字保留（仅角标 14→18），维持待核，未凭记忆改写 |
| R2-8 | rationale L21 材料类指略宽（LOW） | 豁免（合理） | [7] 标题即"Strong-field physics in three-dimensional topological insulators"（三维 TI 类指成立）；[8] 实测体系为 Bi₂Se₃（2109_15291.txt L68-69 "prototypical topological insulator system Bi2Se3"）。理论类指＋Bi₂Se₃ 实验证实语义自洽，材料列举不构成错误，不改正确 |
| R2-9 | 创新增量与边界归属复核 | 豁免（复核通过） | 抽验 rationale L37/L55、scheme L207/L209、content L39：Lesko/Jacobsen[42]"观测"层、Uzan/Faeyrman[13][12]"相位层"、Zhao[20]"模拟参考点"边界句在位；con L53 读出归属句未动。无误归迹象 |

### critic 视角（C2-1 至 C2-4，4 条）

| # | 问题（短） | 判定 | 证据 |
|---|-----------|------|------|
| C2-1 | scheme §2.2(a) 噪声预算段 523 字超长可拆（MEDIUM） | 已解决 | 现 scheme.md L101（333 字，止于"分项噪声预算…时序抖动"）/ L103（124 字，起于"两项按方和根合成"）/ L105（68 字，起于"该裕度差由压缩 CEP 噪声至 ≤75 mrad"）三段，拆分点与建议完全一致；三段合计 ≈525 ≈ 原 523（+2 为角标重排位宽变化），句子内部零改动 |
| C2-2 | 补角标后 [N] 密度（LOW，记录） | 豁免（合理） | 程序化实测：rationale 41 / content 9 / scheme 19，合计 69，与预测一致；rat 为综述章在 35-47 带内，con/sch 在 10-20 区间，不超标 |
| C2-3 | 量化基线复测全绿 | 豁免（复核通过） | 独立复测：>120 字句三章 0/0/0（剔行内 $…$ 剔 [N]）；自引用 8（rat 6/con 0/sch 2）≤10；禁用词（触发/口径/锚定/固化/交付/首例）＋回归词（"实验证据"等 5 个）grep 全章 0 命中 |
| C2-4 | 超长段豁免（3 段记录） | 豁免（合理） | 独立复测 scheme >400 字段恰 3 处：L75（419 字，分区矩阵四靶材分述）、L81（527 字，写脉冲三档）、L233（450 字，第 4 年）——与既录豁免清单一一对应；C2-1 拆分后无新增超长段 |

### reviewer 视角（V2-1 至 V2-5，5 条）

| # | 问题（短） | 判定 | 证据 |
|---|-----------|------|------|
| V2-1 | 参考文献编号非首现序＋扩表重排专项（HIGH） | 已解决 | 程序化复测（独立脚本，非采信报告）：正文 69 角标（rat 41/con 9/sch 19，full_review 0）；首现顺序严格 1..42；references.md 42 条连续无重复无跳号；正文-表一一对应（1..42 全部被引、无越界、无孤儿无悬挂）。[8]/[17] 落位与首现位置一致（rat L21、rat L35）。书目溯源见 R2-2/R2-3（KB 两页逐项相符） |
| V2-2 | 残差档一"无 Berry 曲率符号反转"口径冲突（MEDIUM） | 已解决 | scheme.md L31 现文："$\|\Delta C\| \leq 0.20$ 且无预测外 Berry 曲率符号反转则验证循环成立"；与 scheme L157"若 $C(t)$ 的整数跃变与 A 预测的瞬态相变窗口吻合，则验证循环成立"、rationale L125"陈数整数跃变吻合、Berry 曲率符号对应则该组验证通过"三处闭环（预测处必须出现、预测外不得出现） |
| V2-3 | full_review 指标表"1-40"过期（LOW） | 已解决 | full_review.md L48 现文："唯一（编号 1-42 连续无跳号）…正文 [N] 挂点与列表一一对应，按首现顺序编号" |
| V2-4 | 跨章关键指标对表（11 项） | 豁免（复核通过） | 抽验：full_review 承接句"MoS₂ 体带隙 1.6 eV 已统一为多层体相取值""SNR 6.5–8.7"与 content L21/scheme 数值一致；content L21 Bi₂Se₃ ≈0.3 eV 与 scheme 判据同口径；本轮修改未触碰数值区 |
| V2-5 | full_review 骨架与章节衔接 | 豁免（复核通过） | 独立实测剔空白 2924 字 ≤3000（报告称 2916，+8 为 V2-3 备注格"按首现顺序编号"添入，口径内）；三段式骨架保持；指针目标在位（scheme §1.3=L21、§2.2=L93、§2.2(a)/(b) 分节存在；full L17-L21 承接句与实况相符） |

## 抽查与新问题

本轮大改（67 处旧号映射＋2 处新增＋全表重建）为高风险区，每章抽查重排点上下文衔接：

- **rationale（抽 6 处）**：L21 [6]→[7]→[8] 链（Ghimire 观测→理论预言→实验证实，叙事与编号同步成立）；L31 [12][13][14] 连续三挂点（Faeyrman MgO/Uzan Nature 2024/Rivera-Dean 量子光学，语义逐条对位）；L35 [15]→[16]→[17]（Floquet 理论→Rudner 综述→McIver 输运签名，McIver 句通顺入列）；L55 [25][26][27][28] 四连（Batista 理论/Lorenzo 指纹/Mokhtari 退相干/Hu 电声耦合，改写句融入段内无断裂）；L113 [34] Watanabe、L125 判据句——均衔接正常。
- **content（抽 5 处）**：L21 [36] Kim（MLFF-MD 两步相变，与 KB 2608_02456 相符）；L29 [37] de la Torre（原文保留）；L39 [5] Ciappina＋[26] Lorenzo（后者"后者针对静态拓扑相"自限句在位）；L59 [29] Ilin＋[34] Watanabe（机制判断与偏差数值来源分离表述完好）。编号密度 9 处在带内。
- **scheme（抽 5 处）**：L65/L209 [13][12] 双指针句（"详见 §一 §2.1 与 §三 §5(1)"指向一致）；L83 [38] Kiselev；L147 [29] Ilin（仅机制判断、偏差数值归 BEEF-vdW 的来源分离句完好）；L207 [18][42] Lesko/Jacobsen 对举。指针与挂点无错位。
- **残留扫描**：四章＋references grep "1-40"/"[43]"/"[0]"/"旧["，0 命中；full_review 无角标（0 处，无需重排）；禁用词/回归词 0。
- **段长微差说明**：豁免段实测 419/527/450 与修前记录 418/525/441 有 1-9 字差，来源为角标重排位宽变化（如旧[9]→[11] 类进位），不改变豁免状态与段落数。
- 未发现重排引入的编号错挂、语义断链或新红线。references.md 重建说明行（L3）与 [1] 前空行（L4）终态在位。

## 总结

- 原问题 18 条（R2-1…R2-9 / C2-1…C2-4 / V2-1…V2-5）：**已解决 7 / 部分 0 / 未解决 0 / 豁免 11**（豁免含复核通过 7 项、合理不改 2 项、待核合规维持 2 项 R2-4/R2-5；R2-7 内含 Lesko 1 个待核子项）。
- r1 靶子消化情况：**2 项已消化**（R13 两处引用缺口——McIver 入表为 [17]、[7] 实验验证论文入表为 [8]，均经 KB 在档页＋一手缓存原文双证）/ **3 项维持待核**（Kiselev[38] 定性断言、de la Torre[37] 两个数值、Lesko[18] 实验细节——三处原文逐字保留，未凭记忆改写，符合"待核原文保留即合规"纪律；均不影响论证结构）。
- 新引入问题：**无**（69 角标程序化复测全绿；重排抽查 16 处衔接正常；口径闭环三处成立；禁用/回归词 0）。
- 遗留 critical：**无**（3 项待核均为 low 风险且已有明确后续定案路径：论文入库或联网核查）。

复核结论: 通过
