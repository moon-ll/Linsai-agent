---
title: "奇宇称交变磁的自旋群判据（The odd-parity altermagnetism: A spin group study）"
type: "papers"
created: "2026-11-12T10:59:27Z"
updated: "2026-11-15T15:09:20Z"
tags: ["交变磁", "反铁磁", "自旋群", "自旋劈裂", "对称性分析", "deepxiv-论文库"]
related: ["2507.09906", "A", "B", "Berry相位", "Haldane-Hubbard模型", "MnPS3", "PLAN", "Rashba效应", "general-berry-mnps3-rashba-20260816", "反常霍尔效应", "强场超快", "强场超快光学", "强场高次谐波", "自旋劈裂", "自旋群（spin group）对称性分析", "非线性光学", "非线性光学探测"]
source_raw: "2025-2507.09906-the-odd-parity-altermagnetism-a-spin-group-study.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
updated_at: "2026-11-15T01:14:38Z"
merged_from: ["wiki/papers/2507.09906.md"]
---

# 奇宇称交变磁的自旋群判据（The odd-parity altermagnetism: A spin group study）

## 林赛的理解

作为做强场超快光学的 PI，我看到这篇工作的第一反应是：它把“零净磁矩却有自旋劈裂”这件事从材料个案上升到了**可操作的对称性判据**层面。在自旋群框架（即近似忽略自旋轨道耦合的对称性描述）下，共线反铁磁体中出现奇宇称自旋劈裂的充分条件被归结为三条：破缺非磁时间反演、长程共线补偿磁序、以及存在 [C2||Ē] 或 [C2||M] 这类自旋群操作。

这个结论对我有两层价值。第一，“奇宇称”意味着空间反演破缺——这在我熟悉的光学语言里直接对应二阶非线性响应（如 SHG）原则上可探测，等于给了一套“对称性判据 → 光学指纹 → 超快时间分辨实验”的筛选逻辑。第二，判据中的每一条对称性（时间反演、特定 C2 操作）在强场激光下都是可以在飞秒尺度被动态打破或恢复的自由度——这提示了光场瞬时调制交变磁自旋劈裂的可能性，正是我 NSFC 强场超快方向关心的操控维度。

与我手头的 MnPS3/Rashba/Berry 相位提案（general-berry-mnps3-rashba-20260816）直接相关：MnPS3 正是共线补偿反铁磁体系，本文的判据可以作为提案中对称性分析部分的分类工具。但要警惕层次差异：自旋群判据在 SOC→0 极限下成立，而 Rashba 是 SOC 效应，二者的衔接需要在提案里明确交代。

## 核心要点

- **研究对象**：共线反铁磁体系中的“奇宇称交变磁”（odd-parity altermagnetism），即具有奇宇称性质的自旋劈裂。
- **核心方法**：自旋群（spin group）对称性分析，在弱自旋轨道耦合近似下操作。
- **充分判据（三条）**：
  1. 破缺非磁时间反演对称性；
  2. 存在长程共线的补偿磁序（净磁矩为零）；
  3. 体系具有 [C2||Ē] 或 [C2||M] 自旋群对称性。
- **理论验证**：在 Haldane-Hubbard 模型上验证了判据的有效性。
- **发表信息**：arXiv:2507.09906（2025），作者 Zeng, Qin, Qin, Feng, Wu, Xu, Wang 等；对应发表 PRB 113, L220412（Letter）。
- **定位**：这是判据/分类型工作，而非材料计算或实验工作（基于现有摘要级信息判断）。

## 实验/研究关联

- **NSFC-强场超快项目**：零净磁矩 + 自旋劈裂的体系是超快自旋流操控的理想候选（无杂散场、抗磁干扰）；本文判据可用于系统筛选候选材料。
- **提案 general-berry-mnps3-rashba-20260816**：MnPS3 为共线反铁磁范德华磁体，可直接用三条判据检验其（或其衍生结构）是否落入奇宇称交变磁类；同时注意本文的 SOC-free 框架与提案中 Rashba（SOC 主导）议题的互补关系——一个管交换尺度的大劈裂，一个管 SOC 尺度的劈裂，不宜混为一谈。
- **光学探测（我的推演，原文摘要级信息未涉及）**：奇宇称 → 反演破缺 → 原则上可用 SHG 等二阶非线性光学手段做对称性指纹识别和时间分辨探测，需读全文核实作者是否讨论了光学判据。
- **强场操控（我的推演）**：判据依赖的对称性元素（时间反演、C2 操作）恰是光场可以瞬时打破的对象，为飞秒尺度开关自旋劈裂提供了思路，但这是我的延伸，非本文内容。

## 开放问题

- 有哪些**真实材料**满足三条判据？是否覆盖范德华磁体（如 MnPS3 家族及其异质结/应变调控变体）？摘要级信息未给出候选清单，需查全文。
- 判据是**充分而非必要**：不满足三条的体系是否仍可能存在奇宇称自旋劈裂？
- SOC 不可忽略时（重元素体系、Rashba 情形）判据如何修正？与 Rashba/Dresselhaus 劈裂的竞争与共存？
- 奇宇称自旋劈裂的**光学指纹**是什么（SHG？圆偏振光电流？），时间分辨探测方案如何设计？
- **非平衡态**下判据是否成立：强场激发、磁序受扰后，自旋劈裂的动力学演化与退简并时间尺度？
- [C2||Ē] 与 [C2||M] 的记号细节（自旋空间与实空间操作的具体搭配）需对照全文确认，当前仅来自一行式总结。

## 来源


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：奇宇称交变磁的自旋群判据（弱 SOC 极限三条充分条件：破缺非磁时间反演 + 长程共线补偿磁序 + [C2‖Ē] 或 [C2‖M] 自旋群操作；Haldane-Hubbard 模型验证）

**原理**：在自旋群框架（近似忽略自旋轨道耦合的对称性描述）下，把「零净磁矩却有自旋劈裂」从材料个案上升为可操作的对称性判据：共线反铁磁体中出现奇宇称自旋劈裂的充分条件归结为三条——(1) 破缺非磁时间反演对称性；(2) 存在长程共线的补偿磁序（净磁矩为零）；(3) 体系具有 [C2‖Ē] 或 [C2‖M] 自旋群对称性；在 Haldane-Hubbard 模型上验证判据有效性；「奇宇称」意味着空间反演破缺——原则上可用 SHG 等二阶非线性响应探测（对称性判据→光学指纹→超快时间分辨实验的筛选逻辑）。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 三条充分判据 | (1) 破缺非磁时间反演；(2) 长程共线补偿磁序（净磁矩为零）；(3) [C2‖Ē] 或 [C2‖M] 自旋群对称性 | 核心要点 |
| 理论验证与发表 | Haldane-Hubbard 模型验证；arXiv:2507.09906（2025），发表 PRB 113, L220412（Letter）；作者 Zeng, Qin, Qin, Feng, Wu, Xu, Wang 等 | 核心要点 |

**适用边界**：判据为充分而非必要（不满足三条的体系可能仍存在奇宇称自旋劈裂）；SOC→0 极限下成立——重元素/Rashba 情形判据修正及与 Rashba/Dresselhaus 劈裂竞争共存待研究；真实材料候选清单未给出（含范德华磁体 MnPS3 家族与否需查全文）；奇宇称自旋劈裂的光学指纹（SHG/圆偏光电流）与时间分辨探测方案待设计；非平衡态（强场激发/磁序受扰）下判据是否成立未验证；[C2‖Ē]/[C2‖M] 记号细节需对照全文。
**代表作**：arXiv:2507.09906（Zeng, Qin, Qin, Feng, Wu, Xu, Wang 等，2025，PRB 113, L220412），The odd-parity altermagnetism: A spin group study（交变磁对称性判据工具）
*方法卡回补 2026-11-12*

## 合并自「2507.09906」

## 阅读笔记

### general-berry-mnps3-rashba-20260816

I now have comprehensive content from the paper. Let me synthesize the structured research notes.

## 调研主题
**论文标题**：The odd-parity altermagnetism: A spin group study（奇宇称交变磁性的自旋群研究）
来源：[arXiv:2507.09906v5](https://arxiv.org/abs/2507.09906v5)（v5, 2026-04-01；v1, 2025-07-14）
作者：Minghuan Zeng, Zheng Qin, Ling Qin, Shiping Feng, Lin Wu, Dong-Hui Xu, Rui Wang
发表期刊（相关 DOI）：[Phys. Rev. B（via DOI 10.1103/7kmk-yl2t）](https://doi.org/10.1103/7kmk-yl2t)
研究领域：强关联电子系统（cond-mat.str-el），奇宇称交变磁性、自旋群对称性分析、Haldane-Hubbard 模型

---

## 研究问题（Research Question）

论文的核心问题是：**如何系统地识别和定义"奇宇称交变磁性（odd-parity altermagnetism, odd-parity ALM）"——即在共线反铁磁体系中产生 Rashba/Dresselhaus 型奇宇称自旋劈裂的充分条件**。论文明确指出既有 ALM 研究局限于"偶宇称"自旋劈裂（依赖非磁性时间反演对称性 TRS），而奇宇称自旋-动量锁定虽然具备类 Rashba/Dresselhaus SOC 形式，对自旋电子学更有应用潜力，但此前只能通过打破非磁性 TRS（如光辐照[32,33]、子格电流[38]、轨道序[43]）零散实现，缺乏系统的自旋群对称性理论基础。论文的中心论点是：通过自旋群方法可以推导出奇宇称 ALM 出现的三条充分条件（打破非磁性 TRS、长程共线补偿磁性、连接相反自旋子格的对称算符），并以 Haldane-Hubbard 模型作为最小实现范例验证这些判据。

## 研究背景（Background）

偶宇称 ALM 自 Šmejkal 等人 2020 年提出以来[7,15,25,29]已成为凝聚态物理热点，其特征是共线反铁磁序在动量空间产生 d-wave、g-wave、i-wave 等对称性的偶宇称自旋劈裂，并导致反常霍尔效应[7,26]、自旋-电荷转换[13]、隧道磁电阻[15,14]等新效应。然而近期研究发现，通过**打破非磁性时间反演对称（nonmagnetic TRS）**可以产生"非相对论性奇宇称磁性"——具有 Rashba/Dresselhaus 形式（p-wave）自旋-动量锁定[31-38]。但已观察到的奇宇称磁性多局限于共面（coplanar）自旋构型[31,34,37]，而共线（collinear）体系中的奇宇称 ALM 是该领域的核心难题，且实验区分和操控共面磁态较为困难。同时，已知能够诱导奇宇称 ALM 的途径包括：光场[32,33]、子格电流[38]和轨道序[43]，但三者之间的统一对称性框架尚未建立。论文在自旋群理论框架下填补了这一空白。

## 研究方法（Methods）

论文采用**理论+数值**两阶段方法：(1) **自旋群对称性分析（spin-group analysis）**——利用 spin-only group $\overline{C}_{\infty} \times \overline{C}_{\infty}$ 与 nontrivial spin group 的余类分解（coset decomposition），推导出三种共线磁性态（FM、AFM、even-parity ALM）对应的自旋群结构，再分析当非磁性 TRS 被打破后，原本保证偶宇称 ALM 的 $[C_2 \| E]$ 算符（E 为反演）失效，取而代之的是 $[C_2 \| \bar{E}]$ 或 $[C_2 \| M]$（$\bar{E}$ 为 Bravais 格子反演，M 为连接相反自旋子格的镜面），从而推导出奇宇称 ALM 的三条充分条件。(2) **Haldane-Hubbard 模型 + cluster slave spin 方法**——以方格（square lattice，对应 p-wave）与六角格（hexagon/honeycomb lattice，对应 f-wave）两种 HH 模型为具体范例（图 2a、2b），通过 cluster slave spin 方法（已成功用于 Hubbard 模型弱-强相互作用渡越[45-47]）自洽求解交错磁化强度 $m_s$、TKNN 数与单粒子能隙，绘制 Haldane 跳跃 $M$ 与在位库仑排斥 $U$ 之间的相图（Fig.3c）。具体计算指标包括：通过谱函数 $A(\mathbf{k},\omega)$ 绘制的等能曲线（CCE）、TKNN 拓扑数、以及沿锯齿形方向的能隙分布（Fig.3d）。

## 主要发现与核心结论（Main Results）

论文给出三组核心定量发现：(1) **对称性充分条件**——奇宇称 ALM 由"打破非磁性 TRS + 长程共线补偿磁序 + 对称算符 $[C_2\|\bar{E}]$（高阶谐波 $l\geq3$ ALM）或 $[C_2\|M]$（p-wave，$l=1$ ALM）连接相反自旋子格"三条件共同保证（Eq.(1)）。(2) **Haldane-Hubbard 模型中的奇宇称 ALM 实现**——在方格 HH 模型中反向子格电流产生反 chirality，建立 $[C_2\|M]$ 对称，对应 p-wave ALM；在六角格 HH 模型中子格电流保持相同手性但被 $[C_2\|C_6]$ 连接，对应 f-wave ALM；两者自旋群分别表达为 $[E\|G] \cup [C_2\|\bar{E} G]$ 与 $[E\|G] \cup [C_2\|C_6 G]$。(3) **四区相图**（Fig.3c，$M$ vs $U$，半填充）——包含 AFMI 区（$m_s\neq0$, Chern=0）、普通 CI 区（$m_s=0$, Chern=1）、奇宇称 ALM-CI 混合区（$m_s\neq0$, Chern=1）以及奇宇称 ALMI 区（$m_s\neq0$, Chern=0）；拓扑相变点（CI→ALMI）的临界 $U$ 随 Haldane 跳跃 $M$ 单调增长，反映 AFM 能隙与拓扑能隙之间的竞争（Fig.3d）。无相互作用的临界 $U_c\approx 4.3t$，与大规模 QMC 模拟值 $[62-67]$ 在合理范围内一致。在 $\langle n\rangle=1$ 时，低能等能曲线（Fig.3a,b）显示自旋向上/向下电子的 CCE 分别围绕 Dirac 点 $\mathbf{K}$ 与 $\mathbf{K}'$ 分离而无交叉，提出可通过准粒子散射干涉（QSI）实验识别奇宇称 ALM。

## 潜在研究方向（Future Directions）

论文指出三个层面的开放方向：(1) **实验验证路径**——利用冷原子平台与 shaking lattice 技术（已实现 Haldane 模型[68-70]）灵活调节 $U/t$ 比，可在受控环境中系统性探索奇宇称 ALM 的相图；同时作者指出其自旋群分析不局限于 HH 模型，可推广至轨道序诱导体系[43]和其他拓扑关联系统[71,72]。(2) **方法学局限**——cluster slave spin 方法未包含规范涨落（gauge fluctuations），且临界 $U_c$ 精度可通过增大 cluster size 引入更多空间涨落进一步改进；此外，论文聚焦共线补偿磁序，对共面（coplanar）奇宇称磁性体系尚未展开讨论。(3) **未解决的开放问题**——奇宇称 ALM 与 spin-splitter torque、charge-to-spin conversion、anomalous Hall 效应等自旋电子学响应的定量关系尚未建立；odd-parity ALM-CI 混合相的具体输运特征、QSI 实验谱学特征以及在真实材料（而非 HH 模型）中的实现可能性是后续重要课题；此外，光场诱导、轨道序诱导与子格电流诱导的奇宇称 ALM 三者之间是否可在统一框架内相互转换仍是开放问题。

---
**笔记元信息**：
- 课题：general-berry-mnps3-rashba-20260816（与 MnPS3/Rashba/交变磁性主题直接相关——奇宇称 ALM 是 Rashba 型自旋劈裂在共线磁体中的对应物）
- 论文定位：理论方法论论文（自旋群对称性分析）+ 数值验证（Haldane-Hubbard 模型）
- 与课题关联：①Rashba/Dresselhaus 型奇宇称自旋劈裂为 MnPS3 中 NRSS 研究提供对称性基础；②p-wave/f-wave ALM 选择定则可应用于强场高次谐波光谱的通道选择；③cluster slave spin + QSI 思路可借鉴用于锰磷硫族材料的电子关联表征。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：自旋群余类分解 + Haldane-Hubbard 模型 + cluster slave spin——奇宇称交变磁性（odd-parity ALM）的对称性充分条件与 p/f-wave 实现（Zeng, Qin, Feng, Wu, Xu, Wang，PRB）

**原理**：系统定义共线反铁磁体系中产生 Rashba/Dresselhaus 型奇宇称自旋劈裂（p-wave）的充分条件：①打破非磁性时间反演对称（nonmagnetic TRS）+ ②长程共线补偿磁序 + ③对称算符 [C₂‖Ē]（高阶 l≥3 ALM）或 [C₂‖M]（p-wave，l=1，M 为连接相反自旋子格的镜面）——通过 spin-only group C̄∞×C̄∞ 与 nontrivial spin group 的余类分解推导；既有偶宇称 ALM 依赖非磁性 TRS 保持，奇宇称此前只能靠光辐照/子格电流/轨道序零散实现。最小实现：方格 Haldane-Hubbard 模型中反向子格电流产生反手性建立 [C₂‖M]（p-wave ALM）、六角格中同手性子格电流被 [C₂‖C₆] 连接（f-wave ALM）；cluster slave spin 方法（不含规范涨落）自洽求解，得 M-U 四区相图：AFMI（m_s≠0, Chern=0）/普通 CI（m_s=0, Chern=1）/奇宇称 ALM-CI 混合区（m_s≠0, Chern=1）/奇宇称 ALMI（m_s≠0, Chern=0）；⟨n⟩=1 时自旋上下电子的等能曲线分别围绕 K/K′ 分离无交叉——提出准粒子散射干涉（QSI）实验识别奇宇称 ALM。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 对称性条件 | 三条件：打破非磁性 TRS + 长程共线补偿磁序 + [C₂‖Ē]（l≥3）或 [C₂‖M]（p-wave）对称算符（Eq. 1）；自旋群 [E‖G] ∪ [C₂‖ĒG]（方格 p-wave）与 [E‖G] ∪ [C₂‖C₆G]（六角 f-wave） | 研究方法/主要发现 |
| 相图与临界值 | M-U 四区相图（半填充）：AFMI/CI/ALM-CI 混合/ALMI；CI→ALMI 拓扑相变临界 U 随 Haldane 跳跃 M 单调增长（AFM 能隙 vs 拓扑能隙竞争）；无相互作用临界 U_c ≈ 4.3t（与大规模 QMC 模拟值一致） | 主要发现 |
| 文献信息 | arXiv:2507.09906v5（2026-04-01；v1 2025-07-14），PRB（DOI 10.1103/7kmk-yl2t），cond-mat.str-el | 调研主题 |

**适用边界**：cluster slave spin 方法未含规范涨落（临界 U_c 精度可通过增大 cluster size 改进）；聚焦共线补偿磁序，共面奇宇称磁性体系未展开；奇宇称 ALM 与 spin-splitter torque/charge-to-spin conversion/anomalous Hall 的定量关系未建立；ALM-CI 混合相的具体输运特征、QSI 实验谱学特征、真实材料（非 HH 模型）实现可能性均为后续课题；光场诱导/轨道序诱导/子格电流诱导三种途径能否在统一框架内相互转换仍是开放问题。
**代表作**：Minghuan Zeng, Zheng Qin, Ling Qin, Shiping Feng, Lin Wu, Dong-Hui Xu, Rui Wang, The odd-parity altermagnetism: A spin group study（arXiv:2507.09906v5，PRB，hermes 深度解析入库）
*方法卡回补 2026-10-03*

<!-- linsai-wikilinks -->
## 关联概念

- [[2507.09906]]
- [[A]]
- [[B]]
- [[Berry相位]]
- [[Haldane-Hubbard模型]]
- [[MnPS3]]
- [[PLAN]]
- [[Rashba效应]]
- [[general-berry-mnps3-rashba-20260816]]
- [[反常霍尔效应]]
- [[强场超快]]
- [[强场超快光学]]
- [[强场高次谐波]]
- [[自旋劈裂]]
- [[自旋群（spin group）对称性分析]]
- [[非线性光学]]
- [[非线性光学探测]]
<!-- /linsai-wikilinks -->
