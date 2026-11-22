# 评审团深度修改报告（第二轮）
执行者：engine亲审 ｜ 课题：general-attosecond-streaking-20260822 ｜ 时间：2026-10-05

本轮为评审团"亲审模式"第二轮：在 r1（2026-10-03，已修 24 项、复核通过）文本上做新鲜定点核查（三视角 findings 见 06_panel/panel-{researcher,critic,reviewer}-findings.md）→ 一次性外科手术式修改 → 本报告。全部判断基于本地文本、knowledge/wiki 与 knowledge/raw 反查、本课题 02_literature 检索记录与 05_review 历史评审，未调用任何外部 LLM/CLI。r1 遗留靶子用 R# 编号。

## 处置总表

| # | 问题 | 处置 | 修改位置 | 说明 |
|---|------|------|----------|------|
| RES2-1 | [high] content §2.4「Ar/Kr/Xe……无内壳层参与电离……低于 5%，归入单通道极限档」与 scheme §3.2（Ar 2p/Kr 3d 芯态通道在水窗低段开放、须叠加多通道修正处理本底）、§3.3（氪/氙芯态通道随能量演化）直接矛盾；物理上"K 边远高于上限"推不出"无内壳层参与"（Ar 2p 250.78 eV、Kr 3d 93.8、Xe 4d 67.5 均低于 284 eV） | 已修 | content.md §2.4 | 收窄为氦/氖（与 scheme L53/L63/L84 单通道档口径闭合）；新增指针句「氩、氪、氙的芯态通道（Ar 2p、Kr 3d、Xe 4d）在本能区开放，相应处置见研究方案 §3.2 与 §3.3」 |
| REV2-5 | [high] 同上，一致性视角登记（破坏统一定义表"靶材体系"行跨章口径） | 已修（合并于 RES2-1） | content.md §2.4 | 同一处修改，不重复计数 |
| RES2-2 | [medium] Hutcheson[10] 断言错挂「偶极相移随光电子动能的可解析演化」——KB 全文页（2502.19010）证实该 ATAS 工作相移按延迟/失谐/泵浦强度提取，全程不测光电子 | 已修 | content.md §2.1 | 改「其偶极相移随延迟与探测失谐的可解析提取，为偶极相位的独立量化提供方法学支撑」；rationale L55 对同文表述经核无误、不动 |
| RES2-3 | [medium] "Keller 组"归属与 KB 冲突（KB 页 s41566-025-01802 两处作"Wörner 组，ETH Zürich"；raw 无作者名单，PI 归属本地不可终裁） | 部分修改 | scheme.md §3.1 | 改中性归属「苏黎世联邦理工学院团队」（双方证据共同承载的最强断言）；2.5 fs 经 KB 证实保留；1800 nm 波长 KB 明示摘要未给——保留正文原值、待核 |
| RES2-4 | [low] 「800 nm、5×10¹⁴ W/cm² 条件下 He 电离截止约 119–176 eV」单场强对区间不自洽（复算 5×10¹⁴→119.3 eV、8×10¹⁴→176.0 eV；05_review/critic-round-2-full_review.md L47 同口径在案） | 已修 | scheme.md §3.1 | 改「800 nm、(5–8)×10¹⁴ W/cm² 条件下」；同句 531 eV/约 400 eV 按区间下端复算吻合、不动 |
| RES2-5 | [low] 矢势二次项「2U_p·sin²(ωt)」缺 φ_CEP，与同句含 φ_CEP 表达式的"等价"仅在 φ_CEP=0 成立 | 已修 | scheme.md §2.1 | sin² 内补 φ_CEP，等价性严格成立 |
| CRI2-1 | [low] 「该判据的物理依据」指代略松（回指对象是中红外驱动选型而非判据；r1 复核非阻塞观察的残余） | 已修 | scheme.md §3.1 | 改「该选型的物理依据」；scheme L114 与 rationale L99 另两处"该判据"回指正确、经复核不属此病，不动 |
| REV2-1 | [medium] scheme §2.2「适用参数区间……超出此区间启用备选路径 A」口径错挂：A 的规范触发是通道能量差 <0.5 eV／混合度 >30%（§2.1、§6），贡献 >50% 是失效上界、无接管，<8% 是修正项不激活 | 已修 | scheme.md §2.2 | 改「多通道贡献 8%–50%，通道间能量差小于 0.5 eV 时启用备选路径 A」，与 §2.1/§6 闭合 |
| REV2-2 | [low] full_review 统一定义表 R1 工作区间行内「（rACE 基准点约 10%，§2.2）」指针过期（两个 §2.2 均无该数值）；出现章节「scheme §2.2/§4.2」欠准（§4.2 无分档数值） | 已修 | full_review.md §三表 | 删行内「，§2.2」；出现章节改「scheme §2.2/§3.3」（四档表为权威出现处） |
| REV2-3 | [low] full_review「>409.7 eV 或多通道贡献 >50% 启用备选路径 C」与 scheme §6（C 触发=偏差 >10% 且重标定无改善）、§3.3「对应备选路径 C」不齐 | 已修 | full_review.md §三表 | 「启用」→「对应」 |
| REV2-4 | [low] full_review「降幅 ≥4 倍（定义见 content §2.2 与 scheme §2.2）」度量定义不全（实验端包络峰值归一在 content G1） | 已修 | full_review.md §一 | 改「content §2.2/G1 与 scheme §2.2」 |
| RES2-6 | [待核] R#靶子：Driver[37] "高达 700 as"及「shape 共振瞬态俘获与 Auger-Meitner 碰撞为主贡献」 | 待核 | （不改动） | 本轮新获 KB 全文精读页（2402.12764）：NO 分子 O/N K 壳层相对时延、540–580 eV O K 边 NEXAFS 区、LCLS ESASE 角向条纹、七通道 MCSCI 吻合——正文主体表述获佐证；但 700 as 数值与机理归因该页未载。原文保留，继续标待核 |
| RES2-7 | [待核] R#靶子：Villeneuve[15] s/f 分波组成（m=0 f 波、近纯 f/s 干涉参考） | 待核 | （不改动） | 本轮复查 KB 仍无 Science 2017,356,1150 原文页（"villeneuve"命中均为其合作者其他论文），原文保留合规 |
| RES2-8 | [待核，新增] Kheifets[18]「氩 Cooper 极小与氙巨 shape 共振区连续宽带相位恢复」 | 待核 | （不改动） | KB 无该 PRA 2026,113,043103 页；KB 既有 rainbow 页为 He/H₂ crRABBITT 体系。标题相符、细节不可本地复核，原文保留 |
| RES2-9 | [待核] R#关联：scheme §3.1「Fu 与 Takahashi 2025」nJ 级水窗/通量约 100 倍 | 待核 | （不改动） | r1 遗留台账冲突已裁决：KB 全文页证实 arXiv:2512.19965 = Hasan[39]，02_literature lit-gap L30 对该号挂 Fu & Takahashi 系错挂；Fu & Takahashi 水窗工作（Communications Physics 2025）本身 KB 无页。正文（未挂编号）保留，台账订正留文献治理（02_literature/ 不在本轮允许改动范围） |
| RES2-10 | [待核，新增] scheme §3.2「Zhu 等[9]以含偶极相位残差的条纹迹作为训练集的一部分」 | 待核 | （不改动） | KB 三个 [9] 相关页均摘要级且明示"训练数据/噪声模型细节未给出"；断言无本地依据亦无反证。原文保留（03_method/method-manual.md L638 同文，不在本轮允许改动范围，一并记录） |

R#待核项销案记录：[13] 325 eV —— 本轮在 KB raw/papers/2013-1310.7008（[13] 预印本）摘要行查得「光子能量覆盖水窗(最高325 eV)并跨越碳K边」，现值获原文级本地证实，rationale L73 与 scheme L43 两处同值合规，**销案、无需改文**；[15]、[37] 数值仍无据，保留待核（见 RES2-7/RES2-6）。

不适用项：无（本轮所有 findings 均有明确处置，无空条目）。

计数：立案问题 15（high 1 / medium 3 / low 6 / 待核 5；REV2-5 合并于 RES2-1 不另计）。处置：已修 9 ｜ 部分修改 1 ｜ 待核 5 ｜ 不适用 0。

## 修改后校验
- 残留 grep：Keller／超出此区间启用／光电子动能的可解析演化／该判据的物理依据（指代略松处）均归零；rationale L99、scheme L114 两处"该判据"经复核为有效回指、保留。
- [N] 双向核对（程序化）：正文 [N] 并集恰为 1–40、连续无跳号；references 40/40 条目均被引用、无孤儿；references.md 本轮零改动。
- full_review 字数 2987 ≤ 3000（本轮净 −2 字）；长句（散文口径）rationale/content/full_review 0、scheme 仅存 r1 记录保留的双源互证句 1 处（121 字）；长段 0；跨章 ≥18 字逐字重复 0；模板腔 0。
- 本轮新增句无超长句（content 改写初稿曾现 122 字句，已按"。 "切分后复测清零）。
- 修改范围：仅 04_proposal/sections/{content,scheme,full_review}.md 共 9 处（content 2、scheme 4、full_review 3）与 06_panel/ 四个新文件；未触碰 rationale.md、references.md、05_review/、_lifecycle.json、previous-20261003-r1/、其他课题；未建备份副本；未执行任何 git 操作。

## 遗留与风险
- 待核 5 项（RES2-6..10）：Driver[37] 700 as 与机理归因、Villeneuve[15] s/f 分波、Kheifets[18] 共振区细节、Fu & Takahashi（Comm. Phys. 2025）nJ/100 倍、Zhu[9] 训练集构成——均属 KB 覆盖外正式刊物细节，建议投稿前原文终核；r1 遗留三项靶子中 [13] 325 eV 已销案，[15][37] 降为"主体已获 KB 佐证、仅存数值/分波细节待核"。
- 台账治理移交：02_literature/targeted-research/lit-gap-1790890315.md L30 将 arXiv:2512.19965 挂 Fu & Takahashi 已证为错挂（该号=Hasan[39]），需文献治理订正（本轮无权改动）；同时建议为 Fu & Takahashi 水窗工作补建正确条目与 KB 页，以消除 scheme §3.1「约 100 倍」的唯一外部依据风险。
- 归属终裁：2.5 fs 自压缩论文（Nature Photonics 2025 / arXiv:2411.12372）的 PI 归属（Keller vs Wörner，均 ETH Zürich）与 1800 nm 驱动波长，正文已中性化为"苏黎世联邦理工学院团队"，波长保留待原文终核。
