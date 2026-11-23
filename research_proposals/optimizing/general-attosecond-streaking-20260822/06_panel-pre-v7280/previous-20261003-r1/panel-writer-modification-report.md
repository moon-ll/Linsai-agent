# 评审团深度修改报告
执行者：engine亲审 ｜ 课题：general-attosecond-streaking-20260822 ｜ 时间：2026-10-03

本轮为评审团"亲审模式"：定点核查（三视角 findings 见 06_panel/panel-{researcher,critic,reviewer}-findings.md）→ 一次性外科手术式修改 → 本报告。全部判断基于本地文本、knowledge/wiki/papers/ 反查、本课题 02_literature/（reading-notes、targeted-research）检索记录与 05_review/_r1_verify_cache_v2.json 核查缓存，未调用任何外部 LLM/CLI。

## 处置总表

| # | 问题 | 处置 | 修改位置 | 说明 |
|---|------|------|----------|------|
| RES-1 | R1 修正项启用阈值"大于 15%"与四档表/scheme §2.2（8%–50% 适用、8%–15% 生效）矛盾 | 已修 | content.md §2.4 | 改"大于 8% 时启用"，与 5%–8% 过渡带不激活口径闭合 |
| RES-2 | 1.6 μm"截止约 375 eV"与文中自用公式（I_p+3.17U_p，He、5×10¹⁴ W/cm²）复算值 ≈403 eV 不自洽（同句 119/531 eV 均吻合公式）；覆盖子句错挂 | 已修 | scheme.md §3.1 | 改"约 400 eV，可覆盖水窗低段大部分能区"；"覆盖水窗低段与高段全区间"改挂 1850 nm（"531 eV 以上"） |
| RES-3 | 条纹反演算法名"VPGTA（变分相位梯度时域分析）"有误，[30] 原文（KB 页 2510.04086）为 VTGPA（Volkov 变换广义投影算法） | 已修 | content.md §2.1、scheme.md §3.3、rationale.md §2.3 | 三处统一 VTGPA |
| RES-4 | Ishii[13] 谱截止 rationale"约 300 eV" vs scheme"约 325 eV"两章两值 | 已修 | rationale.md §3.1 | 统一为 325 eV（课题文献池 lit-gap-1790890315.md 记录"最高 325 eV"） |
| RES-5 | "该误差量级在 15%–30% 区间内的标定"量纲混读（15%–30% 是贡献区间非误差区间） | 已修 | rationale.md §1 | 改"多通道贡献 15%–30% 区间内的条纹重构误差标定" |
| RES-6 | "Han 等[31]以自相关方法对同源数据得到约 165 as"归属过强（~165 as 自相关检索出自 Zhao 2020，Han Comment 引用对比） | 已修 | content.md §2.1 | 改"Han 等[31]指出，同源数据的自相关检索给出约 165 as，与 19.2 as 相差约八倍"（与 KB Comment 页"相差约 8 倍"一致） |
| RES-7 | Zhu[34] 正文"2025 年"与条目 AAAI 2026 错位（同 Hasan 案例类别） | 已修 | content.md §2.1、scheme.md §6 | 两处改 2026 年 |
| RES-8 | "第一排原子"误称（Ar/Kr/Xe 为第三至第五周期） | 已修 | rationale.md §2.1、content.md §2.4 | 改"稀有气体原子" |
| RES-9 | Hasan 结论句"水窗多通道贡献中的隐性分量"与同段"能区约 130 eV 属极紫外段"自缠 | 已修 | scheme.md §3.3 | 删"水窗"，改"多通道条纹表征中的隐性分量" |
| RES-10 | Villeneuve[15]"f 波与 s 波干涉/m=0 f 波"细节 KB 无原文页可核 | 待核 | （不改动） | 标题与"相干电子波包成像"相符，分波组成待原文终核 |
| RES-11 | Driver[37]"高达 700 as"KB 无原文页可核 | 待核 | （不改动） | 机理表述与该 LCLS 工作一致，数值待原文终核 |
| CRI-1 | scheme 7 处 >120 字分号复句 | 已修 | scheme.md §1/§3.1/§3.2 | 拆分至仅剩 2 处保留项：γ 估算句（121 字，公式主体）、Cousin/Peschel 双源互证句（129 字，full_review 衔接点设计性并列） |
| CRI-2 | scheme 3 段 >400 字可拆（530/405/404 字） | 已修 | scheme.md §2.1、§3.1×2 | 在"建模层级分两级/该方案在文献中已有完整先例/多通道靶材选用甲烷与氮气"自然边界分段，段内文字不动；复测长段 0 |
| CRI-3 | "正式 Reply"×2（[38] 为预印本†，scheme 侧已修、此两处复发） | 已修 | rationale.md §2.3、content.md §2.1 | 改"以预印本形式 Reply" |
| CRI-4 | "串行衔接"句 scheme 与 rationale 逐字重复且与段首"递进依赖"义重 | 已修 | scheme.md §1 | 删 scheme 处，保留 rationale 出处 |
| CRI-5 | Meier[23] 句 scheme §3.2 与 §5 逐字双现 | 已修 | scheme.md §5 | §5 改短引"如 §3.2 所引" |
| CRI-6 / REV-11 | 检索库范围三处子集表述与 references 表尾 canonical 不齐 | 部分修改 | content.md §2.4、scheme.md §7 | content/scheme 两处对齐 canonical 五库（补 IEEE Xplore、CrossRef）；rationale §3.1 的 CNKI/IOPscience 为"国内未见报道"专项检索面，保留不改（理由：检索对象与范围不同，非同一声明的异名） |
| REV-1 | 截面库口径：scheme 三处"NIST（电子）电离数据库 ASD/光电离子表"误称（ASD 系能级库），与 XCOM/FFAST 并存——历史 critical 复发 | 已修 | scheme.md §3.3、§4.1、§6 | 三处统一"NIST 光电离截面库（XCOM）、FFAST 等截面数据库"，删除病句"光电离子表" |
| REV-2 | 备选路径 A 启用口径：rationale"多通道贡献（截面占比）约 30% 的通道混合度判据"与 scheme §6（混合度 30%↔贡献约 40%）、full_review（40% 启用 A）冲突 | 已修 | rationale.md §4 | 改"备选路径 A 的启用判据为通道混合度大于 30%（对应多通道贡献约 40%，映射见研究方案 §6）" |
| REV-3 | "通道重叠度"与"多通道贡献"同量异名残留（eV 量"重叠宽度"不受影响） | 已修 | scheme.md §3.3×3、§4.3、§5×2（改"重叠宽度"）、§7 创新点三；full_review.md×2 | 百分比量统一"多通道贡献"，eV 量统一"（通道）重叠宽度" |
| REV-4 | rationale L85 指针"研究内容 §2.3"复核 | 不适用 | — | 初查误录为 §2.2；现行 §2.3 指针有效（该节含 2% 启用判据并经"见目标 G2"链至量化来源），不改 |
| REV-5 | scheme §1"三层的划分与研究内容三个研究方向 R1/R2/R3 对应"归类错误（三层是 R1 参数空间内分层），且 content 无"三层"术语 | 已修 | scheme.md §1 | 改"以研究内容 §2.2 中 R1 工作区间（8%–50% 三亚区）为坐标"，各层括注主检验区/线性响应区 |
| REV-6 | full_review"三层定义由 content §2.2 给出"指针错误；统一定义表"多通道贡献百分比"行出现章节过期 | 已修 | full_review.md §二、§三表 | 改"由 scheme §1 给出（对应 content §2.2 三亚区）"；表行出现章节改"方案 §1/§2.2" |
| REV-7 | full_review R2 兑现句靶材挂错（氦/氖/甲烷/氮气——甲烷/氮气属 R1） | 已修 | full_review.md §二 | 改"氩/氪主靶与氦/氖对照靶" |
| REV-8 | full_review"100 eV 物理依据由 content K2 与 scheme §3.2 分别给出"过宽（K2 无 1 rad 细节）；"时间节点"无对应 | 已修 | full_review.md §二 | 改"阈值由 content K2 给出，物理依据……见 scheme §3.2"；"时间节点"→"所属研究阶段" |
| REV-9 | full_review"≥5pp/≤2pp"与正文"不小于/不大于 N 个百分点"混用（历史 medium 复发） | 已修 | full_review.md §一、§三表 | 两处镜像正文中文表述 |
| REV-10 | full_review 统一定义表 N₂ 行（content K2 已无 N₂）、Auger 行（content §2.1 无处置表述）出现章节过期；"时域门控"与 scheme"时间门控"不一 | 已修 | full_review.md §三表 | N₂ 行改"scheme §3.2/§4.2"并删"（两处一致）"；Auger 行改"scheme §3.3"、"时域门控"→"时间门控" |
| CRI-N1 | R1/R2/R3、G/K 代号（历史轮"改实义名"建议） | 不适用 | — | 属结构编号体系且处处带实义名并注，题面纪律要求保持既有编号体系，不立案 |
| CRI-N2 | 设计值/待实测标定注记密度（防御句） | 不适用 | — | 系 4 项设计值诚实披露与降级路径收口（scheme §4.1 集中列出），删注记伤严谨性，不立案 |
| CRI-N3 | [N] 角标合计 89 次（36/23/30）超题面 10–20 提示线 | 不适用 | — | 项目校准标准 rationale 35–47（历史两轮判达标）；本轮双向核对 40/40 无孤儿无缺号，不立案 |
| CRI-N4 | 模板腔/口号式开头（"在此基础上""本项目拟""综上所述"） | 不适用 | — | 实测均为 0；"为…提供"6 处低于"为…提供…支撑">5 红线且为实义用法，不立案 |
| CRI-N5 | full_review 4 处 >120 字句 | 已修 | full_review.md §一、§二 | 随 REV-8/9 修改顺带按"；→。"拆分；复测长句 0、字数 2989≤3000 |
| RES-N1 | rationale"内壳层贡献 5% 以下"与 XUV 双壳层 8%–15% 表面张力 | 不适用 | — | content §2.4 已有调和句（5% 基线对应阈未开放 deeper 内壳层），物理成立 |
| RES-N2 | Ar 2p 阈 250.78 eV 系 2p₁/₂ 分量（2p₃/₂ 248.6 eV） | 不适用 | — | 正文动能区间按 250.78 eV 自洽且在"≈"容差内 |

计数：立案问题 27（high 4 / medium 15 / low 6 / 待核 2）+ 不立案记录 7。处置：已修 24 ｜ 部分修改 1 ｜ 不适用 8（含 REV-4 复核更正）｜ 待核 2。另修复：scheme 长段 3→0、长句 9→2（保留项）、rationale/content/full_review 长句长段清零；full_review 2989 字 ≤3000。

## 修改后校验
- 残留 grep：VPGTA／正式 Reply／第一排／ASD 误称／通道重叠度／375 eV／Zhu[34]2025／≥5pp 全部为 0。
- [N] 双向核对：正文引用编号 1–40 连续，40/40 条目均被引用、无孤儿；references.md 本轮未改动。
- 数值口径复算抽查通过：γ≈108（>100）、U_p≈6×10⁻⁴ eV、Ar/Kr/N₂ 动能区间、G3 换算 84/134/116 eV、中点能量 100/346.85/476.35 eV、降幅 ≥4 倍。
- 修改范围：仅 04_proposal/sections/{rationale,content,scheme,full_review}.md 与 06_panel/*（新建）；未触碰 references.md、05_review/、_lifecycle.json及其他课题，未建备份副本。

## 遗留与风险
- 待核 2 项：Villeneuve[15] s/f 分波组成、Driver[37] "700 as"——本地知识库无原文页，正式投稿前建议原文终核；同期建议对 [13]（Ishii 325 eV）一并做原文终核（现值以课题文献池检索记录为据）。
- 数值修订依据说明：375→400 eV 以正文自用公式与同句双锚点自洽为据（非外部新源）；165 as 归属、VTGPA、325 eV 以 02_literature 与 knowledge/wiki 原文记录为据——均已按"核实过的来源"纪律执行，但 [13][15][37] 三条属 KB 覆盖外的正式刊物文献。
- 内部记录冲突（不影响正文）：05_review 与 02_literature 对 arXiv:2512.19965 分别挂 Hasan[39] 与 Fu & Takahashi，两者必有一误；正文未引用该 arXiv 号，建议下轮文献治理时订正台账。
