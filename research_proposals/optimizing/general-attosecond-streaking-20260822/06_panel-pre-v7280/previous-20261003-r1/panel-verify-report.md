# 评审团复核报告

复核员：独立复核（fresh context）｜ 课题：general-attosecond-streaking-20260822 ｜ 时间：2026-10-03

复核方式：只验三视角 findings 清单，不做全量评审。一切以磁盘当前文本重新取证（grep + 读原文 + 与修改前快照 `04_proposal/proposal-draft.md`（2026-10-02 07:04）及 `05_review/.monitor-view-r2.md` 做全量 diff 穷举本轮改动），不采信修改报告自我声明。程序化复测：残留 grep 13 项、[N] 双向核对、字数、长句长段。

## 逐条判定

| # | 问题（短） | 判定 | 证据 |
|---|-----------|------|------|
| RES-1 [high] | R1 修正项启用阈值 15% 与四档表矛盾 | 已解决 | content.md L49「R1 修正项在多通道贡献大于 8% 时启用」；旧值「大于 15% 时启用」全库 grep=0；与同段四档表（5%–8% 过渡带不激活）、scheme §2.2（适用 8%–50%）、§3.3 表（线性响应档 8%–15% 修正项生效）闭合 |
| RES-2 [high] | 1.6 μm 截止 375 eV 与自用公式不自洽、覆盖子句错挂 | 已解决 | scheme.md L41「1850 nm 同场强条件下截止升至 531 eV 以上，覆盖水窗低段与高段全区间；1.6 μm 同场强截止约 400 eV，可覆盖水窗低段大部分能区」；「375 eV」全库 grep=0；复算 I_p+3.17U_p≈403 eV 与 400 吻合；覆盖子句已挂 1850 nm |
| RES-3 [medium] | VPGTA 应为 VTGPA（三处） | 已解决 | content.md L13「以 Volkov 变换广义投影算法（VTGPA）」、scheme.md L96「以 VTGPA（Volkov 变换广义投影算法）重新分析」、rationale.md L37「VTGPA 重分析」；「VPGTA／变分相位梯度」全库 grep=0；依据在盘：knowledge/wiki/papers/2510.04086.md「用 VTGPA (Volkov变换广义投影算法…)」 |
| RES-4 [medium] | Ishii[13] 谱截止两章两值（300 vs 325 eV） | 已解决 | rationale.md L73「其谱截止约 325 eV」，与 scheme.md L43 一致；依据在盘：02_literature/targeted-research/lit-gap-1790890315.md L21「光子能量覆盖水窗(最高325 eV)」；rationale「300 eV」grep=0 |
| RES-5 [medium] | "误差量级在 15%–30% 区间"量纲混读 | 已解决 | rationale.md L11「多通道贡献 15%–30% 区间内的条纹重构误差标定尚未见公开报道」；diff 确认旧句「该误差量级在…」已替换 |
| RES-6 [medium] | "约 165 as"归 Han[31] 自测属归属过强 | 已解决 | content.md L13「Han 等[31]指出，同源数据的自相关检索给出约 165 as，与 19.2 as 相差约八倍」；依据在盘：knowledge/wiki/papers/2025-2510_17949-*.md L43「2020 年 ~165 as 自相关检索结果」（Comment 引用对比，非自测） |
| RES-7 [medium] | Zhu[34] 年份 2025 与条目 AAAI 2026 错位 | 已解决 | content.md L17「Zhu 等[34]2026 年以 SinBasis 网络」、scheme.md L140「Zhu 等[34]2026 年系统比较」；「Zhu 等[34]2025」grep=0；references.md [34] 2026, 40(16) 对齐 |
| RES-8 [medium] | "第一排原子"误称 | 已解决 | rationale.md L17「以氖等稀有气体原子为靶」、content.md L43「Ne 与 Ar/Kr/Xe 等稀有气体原子的 K 边阈值」；「第一排」全库 grep=0 |
| RES-9 [medium] | Hasan 结论句"水窗"泛化自缠 | 已解决 | scheme.md L98「表明 Auger 通道由多通道条纹表征中的隐性分量变为可测量分量」；紧随句「能区中心光子能量约 130 eV，落在极紫外段」不再自缠 |
| RES-10 [待核] | Villeneuve[15] s/f 分波细节 | 豁免 | 原文保留即合规：content.md L9「证实角分布选择 m=0 f 波分量的可行性」、rationale.md L47「以近纯 f 波与 s 波的干涉作为全息参考」逐字在盘（diff 零改动）；KB 无 Science 2017,356,1150 原文页，待核标注合理 |
| RES-11 [待核] | Driver[37] "700 as" | 豁免 | 原文保留：rationale.md L31「测得高达 700 as 的相对延迟及其随光子能量的振荡调制」逐字在盘（diff 零改动）；KB 无 Nature 632,762 原文页 |
| CRI-1 [medium] | scheme 7 处 >120 字分号复句 | 已解决 | diff 穷举证实全部按"；→。"拆分（119–176 eV 句、531 eV 句、325 eV 句、Keller 句、通量句、氖气句、对照句等）；散文口径复测 >120 字长句 0；保留 2 处（γ 估算句 101 字、Cousin/Peschel 双源句 120 字，去空白口径；报告口径 121/129）——均在红线附近、保留理由已随报告记录 |
| CRI-2 [medium] | scheme 3 段 >400 字 | 已解决 | 三处自然边界分段在盘：「TDSE 能在单电子近似」（§2.1）、「该方案在文献中已有完整先例」（§3.1）、「多通道靶材选用甲烷与氮气」（§3.1）前均插入段落断点；复测长段 0/0/0/0 |
| CRI-3 [medium] | "正式 Reply"表述复发（[38] 为预印本†） | 已解决 | rationale.md L37、content.md L13 均「以预印本形式 Reply 逐条答辩」；「正式 Reply」全库 grep=0；references.md [38]† 标记未动 |
| CRI-4 [low] | "串行衔接"句跨章逐字重复 | 已解决 | scheme 处该句已删（diff 证实整句删除；「串行衔接」scheme grep=0）；rationale.md L85 出处句「三者在执行节点上呈串行衔接…」逐字保留 |
| CRI-5 [low] | Meier[23] 句 §3.2/§5 逐字双现 | 已解决 | scheme.md L128「如 §3.2 所引 Meier 等[23]的机器学习重构研究，个别探测通道失效与高噪声可由通道间冗余信息补偿」；§3.2 L65 全句保留 |
| CRI-6/REV-11 [low] | 检索库范围子集与 canonical 不齐 | 已解决 | content.md L39、scheme.md L160 均「Web of Science、arXiv、IEEE Xplore、Scopus 与 CrossRef」，与 references.md L97 canonical 一致；rationale.md L71 CNKI/IOPscience 按 findings 自身理由（国内专项检索面）保留，属清单预设范围 |
| REV-1 [high] | 截面库 ASD 误称复发（scheme 三处） | 已解决 | scheme.md L88「NIST 光电离截面库（XCOM）与 FFAST 等截面数据库的 Xe 4d 与 Kr 3d 光电离曲线」、L106「NIST 光电离截面库（XCOM）、FFAST 等独立截面数据库」、L136「NIST 光电离截面库（XCOM）、FFAST 等截面数据库」；「ASD／Atomic Spectra」全库 grep=0；病句「光电离子表」已除；与 rationale/content/scheme L53 既有 XCOM 口径统一 |
| REV-2 [high] | 备选路径 A 启用口径 rationale 数值错挂 | 已解决 | rationale.md L97「备选路径 A 的启用判据为通道混合度大于 30%（对应多通道贡献约 40%，映射见研究方案 §6）」；与 scheme §6 L136「通道混合度大于 30%，对应多通道贡献约 40%」、§3.3 表、full_review L23「40% 启用备选路径 A，40%–50% 降级运行」四方一致 |
| REV-3 [medium] | "通道重叠度"同量异名残留 | 已解决 | diff 证实 scheme §3.3 分组变量/阈值划分/表头/失效条件、§4.3、§7 创新点三共 7 处改「多通道贡献」，§5 两处 eV 量改「重叠宽度」；「通道重叠度」全库 grep=0；full_review.md L7「以能区与多通道贡献为双变量」、L29 表行同步 |
| REV-4 [low] | rationale L85 指针复核 | 豁免 | 复核更正成立：rationale.md L85「在研究内容 §2.3 与研究方案 §4.1 分项给出」逐字在盘（diff 零改动）；content §2.3 L35 实含「残余大于 2% 时即启用第二级」判据，指针有效，不改合规 |
| REV-5 [medium] | scheme §1 三层与 R1/R2/R3 错置对应 | 已解决 | scheme.md L7「三层的划分以研究内容 §2.2 中 R1 工作区间（8%–50% 三亚区）为坐标」+ 实验验证层（主检验区）/可行性论证层（线性响应区）两处括注；content §2.2 L27 实为三亚区定义，指针有效；rationale 连带将「三层定义」改「三个子区间」（diff 在案，与 REV-5 术语统一同向、语义无损） |
| REV-6 [medium] | full_review 三层定义指针错误 | 已解决 | full_review.md L11「三层定义由 scheme §1 给出（对应 content §2.2 三亚区）」；统一定义表「多通道贡献百分比」行出现章节改「scheme §1/§2.2」（diff 在案） |
| REV-7 [medium] | full_review R2 兑现句靶材挂错 | 已解决 | full_review.md L13「（氩/氪主靶与氦/氖对照靶、16 通道 TOF 角积分）」；与 scheme §3.2 L63（氩气与氪气主靶、氦气与氖气对照）一致 |
| REV-8 [medium] | full_review 100 eV 物理依据出处过宽 | 已解决 | full_review.md L13「100 eV 二级修正启用阈值由 content K2 给出，物理依据（IR 半周期内光电子累积偶极相移约 1 rad 动能上限）见 scheme §3.2」；「时间节点」→「所属研究阶段」；content K2（L73 阈值）、scheme §3.2（L67 约 1 rad）均实有对应内容 |
| REV-9 [low] | "≥5pp/≤2pp"与正文中文表述混用 | 已解决 | full_review.md L7/L29 均「差值不小于 5 个百分点／差值不大于 2 个百分点」；「pp」全库 grep=0 |
| REV-10 [low] | 统一定义表两处出现章节过期、"时域门控"不一 | 已解决 | N₂ 行「15.58 eV | scheme §3.2/§4.2」（N₂ 115.6 eV 实在 scheme L69/L116）且删「（两处一致）」；Auger 行出现章节改「scheme §3.3」、「时域门控」→「时间门控」；scheme L100 用词同步「时间门控窗口」 |

## 抽查与新问题

**程序化复测修改报告三项声明（全部复现通过）：**
1. [N] 编号 1–40 双向无缺口：正文引用 rationale 36 / content 23 / scheme 30 / full_review 0，合计 89 次（与报告声明及 critic 基线逐章一致，无引用丢失）；编号 1–40 无缺号、无越界；references 40/40 条目均被引用、无孤儿。
2. 残留 grep 全零：VPGTA／变分相位梯度／正式 Reply／第一排／ASD／Atomic Spectra／通道重叠度／375 eV／Zhu 等[34]2025／≥5pp／≤2pp／5pp／时域门控共 13 项，五章全文全部为 0。
3. full_review 2989 字 ≤3000：实测（含换行口径，与报告计数法一致）恰为 2989；长句（散文口径）0、长段 0；rationale/content 长句长段亦为 0。

**修改面穷举核对（与修改前快照全量 diff）：** rationale 6 处、content 6 处、scheme 20 处、full_review 12 处改动全部映射到清单条目，无越权改动、无清单外数值变更；references.md 本轮零改动（mtime 10-02 07:03，diff 仅末尾换行符差异）；05_review/ 无 10-03 改动文件——与报告"修改范围"声明一致。

**上下文衔接抽查（每章 2–3 处修改点）：**
- rationale：RES-4（325 eV）与 scheme L43 同值；REV-2 新句「映射见研究方案 §6」指针有效。
- content：RES-1 改 8% 后与同段四档表、§2.2 终止判据（15%–50% 主检验 + 8%–15% 辅助判据）自洽；RES-6 新句与后文「[38] 以预印本形式 Reply」衔接通顺。
- scheme：RES-2 拆句后 1850/1.6 μm 两锚点各自承载覆盖论断，物理口径正确；「该平台的单脉冲能量…对应光子通量较常规方案提升约 100 倍」与 §3.1 通量句一致；REV-1 三处新库名与 rationale L9/L81、content L43 既有 XCOM/FFAST 口径统一。
- full_review：REV-6/7/8/9/10 改后各表行与正文实况一一对应（逐行回查 content/scheme 原文证实）。

**非阻塞观察（不立案，仅记录）：**
1. 修改报告计数行「不适用 8」实为 7（REV-4 + CRI-N1..N4 + RES-N1..2），系报告自身台账口径小误差，不影响正文。
2. scheme §3.1「该判据」指代略松与「约 119–176 eV」区间：经 proposal-draft.md 快照与 05_review/.monitor-view-r2.md 比对均为既有文本、非本轮引入，且 119–176 eV 有 05_review/critic-round-2-full_review.md L47 的 (5–8)×10¹⁴ W/cm² 复算依据。
3. 待核 2 项（[15] s/f 分波、[37] 700 as）与 [13] 原文终核建议已由报告记录，属 KB 覆盖外正式刊物文献，留待投稿前终核，不构成硬伤。

## 总结

- 原问题 28 条（RES 11 + CRI 6 + REV 11，其中 CRI-6≡REV-11 同项）：已解决 25 / 部分 0 / 未解决 0 / 豁免 3（RES-10、RES-11 待核原文保留合规，REV-4 复核更正不改合规）。4 条 high 全部解决。
- 新引入问题：无（3 条非阻塞观察见上，均经快照比对证实为既有文本或台账口径误差）。
- 遗留 critical：无。

复核结论: 通过
