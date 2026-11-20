---
title: "2025-2503_09877-two-dimensional-antiferromagnets-with-non-relativistic-spin"
type: "papers"
created: "2026-09-25T20:22:08Z"
updated: "2026-11-16T05:30:14Z"
tags: []
related: ["2503.09877", "Berry 曲率", "CrSb", "MnPS3", "general-berry-mnps3-rashba-20260816", "层间耦合", "强场超快", "强场驱动", "泵浦探测", "滑动铁电", "自旋劈裂", "莫尔超晶格", "量子几何", "量子度规"]
source_raw: "2025-2503.09877-two-dimensional-antiferromagnets-with-non-relativistic-spin.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
---

• # Two-dimensional antiferromagnets with non-relativistic spin splitting switchable by electric polarization

  ## 林赛的理解

  这篇工作对我们组的价值很直接：它把"铁电极化"作为非相对论自旋劈裂（NRSS）的开关，而且明确落在 MnPSe₃ / MnPS₃ 这类 MPX₃ 家族和 1T-CrTe₂ 这类 vdW 磁性异质体系上——这正是我们 Berry-MnPS₃-Rashba 课题库里的核心材料类。对我们的意义有两层：

  1. **材料与器件接口**：它给"如何用电压而非电流控制 AFM 序参量"提供了一个对称性分类框架（Type I/II/III），Type-II（MnPS₃ + ≥4% 双轴拉应变）实现"保 Néel 矢量、翻转 NRSS 符号"的非易失切换——这正是低功耗自旋电子学器件的卖点。
  2. **强场视角的挪用**：NRSS 本质是动量依赖的自旋极化带结构，而我们关心的是**强场驱动下这类自旋劈裂带的超快动力学**。极化可控的 d 波交替磁体 + 130 meV 量级的自旋劈裂，是强场 HHG/阿秒泵浦探测中"自旋选择性激发"的现成平台——劈裂尺度（32–130 meV）落在太赫兹-中红外泵浦可达范围，值得做定性估算。

  我打算把这篇列入 MnPS₃ 方向的支撑文献，重点引用其对称性判据和 Type-II 切换机制。

  ## 研究问题

  论文要回答的核心问题是：**在二维反铁磁 vdW 双层中，极性层堆叠（polar-layer stacking，即滑动铁电性）能否产生非相对论自旋劈裂（NRSS），并且这种 NRSS 能否通过铁电极化的翻转来实现可逆、非易失的开关？**

  具体分解为三个子问题：

  1. 极性堆叠的 AFM 双层中，NRSS 的对称性来源是什么？哪些情况下是交替磁性（altermagnetic）起源，哪些是非交替磁性起源？
  2. NRSS 可被电极化翻转开关的**对称性充要条件**是什么？
  3. 哪些代表性 2D AFM 材料（MPX₃、1T-CrTe₂）能实现上述情景，且切换是否比电流驱动 Néel 矢量翻转更实用？

  中心论点：电极化切换 NRSS（而非电流反转 Néel 矢量）是 AFM 自旋电子学更节能、非易失的器件路径。

  ## 研究背景

  - **AFM 自旋电子学**：反铁磁体抗磁扰动、无杂散场、自旋动力学超快，是理想的态变量材料（Baltz et al., Rev. Mod. Phys. 90, 015005 (2018)；Jungwirth et al., Nat. Phys. 14, 200 (2018)）。
  - **NRSS 的兴起**：传统共线 AFM 因 PT 或 UT 对称性强制能带自旋简并；NRSS AFM 打破这些对称性，在无 SOC 时就产生动量依赖自旋极化（Hayami et al. 2019；Yuan et al., PRB 102, 014422 (2020)）。其中两个反磁亚晶格由（真/假）转动连接的称为**交替磁体**（Šmejkal et al., PRX 12, 031042 (2022)），无对称性连接的则是 Yuan et al. (PRL 133, 216701 (2024)) 讨论的 BZ 中心 NRSS。
  - **Néel 矢量翻转的瓶颈**：自旋转移矩/自旋轨道矩可以反转 Néel 矢量（Manchon et al., RMP 91, 035004 (2019)），但所需大电流密度导致能效差（Han et al., Sci. Adv. 10, eadn0479 (2024)）。
  - **电场诱导 NRSS 的局限**：已有 proposal（Wang et al., Nano Lett. 25, 498 (2024)；Peng et al., arXiv:2408.12504）用电场破缺反演对称性产生 NRSS，但劈裂小、无非易失性。
  - **滑动铁电性的成熟**：vdW 组装技术（Geim & Grigorieva, Nature 499, 419 (2013)）使两个非极性层堆成非中心对称结构产生面外极化成为可能，BN 双层滑动铁电已实现（Yasuda et al., Science 372, 1458 (2021)；Vizner Stern et al., Science 372, 1462 (2021)）。已有若干理论工作提出在 AFM vdW 双层中实现 NRSS（Cao et al., Nano Lett. 23, 3781 (2023)；Sun et al., Nano Lett. 24, 11179 (2024) 等），但缺少系统的对称性分类。
  - **本文定位**：用自旋空间群方法对极性堆叠 AFM 双层的 NRSS 做统一分类，并给出可切换性的对称性判据。

  ## 研究方法

  - **第一性原理计算**：VASP，PAW 方法，PBE 泛函；平面波截断能 **500 eV**，不可约布里渊区 **16×16×1** k 点网格；原子弛豫至每个原子受力 < **2×10⁻³ eV/Å**，电子自洽容差 **10⁻⁷ eV**；层间真空层 > **20 Å**；范德华作用采用半经验 **DFT-D3**；极化用偶极修正法计算。
  - **DFT+U**（旋转不变形式）：MnPSe₃ 和 MnPS₃ 的 Mn d 轨道 **U = 4 eV**；1T-CrTe₂ 的 Cr d 轨道 **U = 2 eV**。
  - **对称性分析**：自旋空间群方法（自旋与空间自由度解耦），对称操作记为 [R_s || R_l]；辅助工具：Bilbao Crystallographic Server、FINDSYM、Pymatgen、PyProcar。
  - **材料体系**：
    - Type-I 代表：MnPSe₃ 双层（MPX₃ 家族，M = Mn, Fe, Co, Ni；X = S, Se），层间 Néel AFM 序，单层层群 No. 162 (P3̄1m)，原生双层 No. 147 (P3̄)。
    - Type-II 代表：**5% 双轴拉应变**的 MnPS₃ 双层（≥4% 应变强制 Type-II 基态）。
    - Type-III 代表：1T-CrTe₂ 双层（A-AFM 序，即层内 FM + 层间 AFM 耦合，此类序亦见于 CrSBr、MnBi₂Te₄ 等）。
  - **结构构造**：AA̅ 堆叠（顶层为底层 xy 面镜像）不稳定，沿高对称方向滑移 ±a/3 弛豫到极性基态 AB̄ 或 B̄A，破缺反演对称性并产生面外极化。

  ## 主要发现与核心结论

  1. **对称性判据**：2D 共线磁体的自旋简并由 [C₂||Ē]、[C₂||U]、[C₂||M_z] 或 [C₂||C₂z] 保护；要产生 NRSS，两个磁亚晶格不能被平移 U、反演 Ē、镜面 M_z 或二重转动 C₂z 连接。亚晶格若被其他晶体转动交换 → 交替磁性 NRSS；完全无对称性连接 → 非交替磁性 NRSS。

  2. **三种极性堆叠类型**（按 AB̄ 与 B̄A 态的 AFM 序关系分类）：
     - **Type-I**：两层 AFM 序相同；AB̄ 与 B̄A 由 [E||M_z] 联系 → **NRSS 不变**（电极化翻转不改变 NRSS 符号），层内 AFM 序保证零净磁矩。
     - **Type-II**：顶层 AFM 序磁反；AB̄ 与 B̄A 由 [C₂||M_z] 联系 → **NRSS 反号**，保 Néel 矢量实现非易失可逆切换。
     - **Type-III**：FM 单层 + 层间 AFM 耦合（A-AFM）；无亚晶格交换对称性 → **非交替磁性 NRSS**；极化翻转同时翻转 NRSS 符号与未补偿净磁矩（磁电效应）。

  3. **MnPSe₃ 双层（Type-I）**：
     - 基态 AB̄/B̄A 沿 [100] 方向滑移 **+a/3 / −a/3**，空间群 No. 8 (Cm)，极化 **0.031 pC/m**（沿 +z / −z）。
     - Type-I 比 Type-II 基态能量低 **0.1 meV**（含 SOC 不变）。
     - 自旋空间群含 [E||E] 和 [C₂||M_y]，两个亚晶格由 M_y 镜面交换 → **d 波交替磁体**，k_x = 0 与 k_y = 0 线为自旋简并节线。
     - 最高价带 NRSS 最大约 **32 meV**，最低导带约 **13 meV**——大于此前报道的 MnPSe₃ 插层（ref. 39）或扭转（ref. 65）情形。
     - 电极化翻转**不改变** NRSS 符号。

  4. **MnPS₃ 双层（Type-II，5% 双轴拉应变）**：
     - Type-I 与 Type-II 能量几乎简并；**≥4%** 双轴拉应变强制 Type-II 基态。
     - 偶极矩约 **0.27 pC/m**，远大于 MnPSe₃。
     - AB̄ 与 B̄A 由 [C₂||M_z] 联系 → **NRSS 反号**：反转电极化翻转 NRSS 符号而**保持 Néel 矢量不变**。

  5. **1T-CrTe₂ 双层（Type-III）**：
     - AA̅ 堆叠沿 [11̄0] 方向 ±a/3 滑移弛豫到极性基态；偶极矩约 **0.20 pC/m**；极性基态属空间群 No. 156 (P3m1)，无亚晶格交换对称性 → 非交替磁性 NRSS。
     - 层间耦合为 AFM（FM 与 AFM 序能量差计算确认）；基态含 [E||C₃z]，与 [C̄₂||P] 组合成 [E||C₆z] → 自旋极化能带呈**六重转动对称**。
     - 顶/底层 Cr 磁矩分别为 **3.19 μB 和 −3.17 μB**，双层净磁矩约 **0.03 μB/Cr 原子**，位于面内（面外磁各向异性能 **6.24 meV**），AB̄ 与 B̄A 指向相反。
     - 费米能处可逆 NRSS 最大值约 **130 meV**。
     - 电极化翻转翻转 NRSS 符号并翻转未补偿净磁矩。

  6. **结论**：极性堆叠 AFM 双层的 NRSS 可具有交替磁（Type I/II）或非交替磁（Type III）起源；Type II 与 III 支持电极化驱动的可逆 NRSS 切换，结果对 SOC 稳健。电压而非电流切换避免 Néel 矢量反转，提供非易失性且更节能；实验可行性有支撑——极性堆叠 vdW 3R-MoS₂ 与 BN 双层已实现超快、无疲劳的铁电翻转，超过 **10¹¹ 周期**（refs. 76–78）。

  ## 潜在研究方向

  - **全部为理论预测，无实验验证**：极化切换 NRSS 在 AFM 双层中尚无实验演示；材料制备（应变 MnPS₃、极性 1T-CrTe₂ 双层）与畴控制是主要障碍。
  - **Type-I 情景的"死路"性质**：MnPSe₃ 天然基态是 Type-I（能量差仅 0.1 meV），极化翻转不切换 NRSS，器件意义上需刻意选用 Type-II/III 体系。
  - **应变依赖性问题**：MnPS₃ 的 Type-II 需 ≥4% 双轴拉应变，实际器件中应变维持与均匀性存疑；应变弛豫可能退回 Type-I。
  - **净磁矩泄漏**：Type-III（1T-CrTe₂）的 0.03 μB/Cr 净磁矩虽显示磁电耦合，但也意味着非完全补偿，对纯 AFM 逻辑的"零杂散场"优势有折损。
  - **未讨论动力学**：切换路径的势垒高度、翻转动力学时间尺度、以及太赫兹/超快脉冲驱动切换的可能性均未涉及——这恰是我们强场方向可以补的空白。
  - **温度稳定性**：DFT 基态讨论未涉及有限温度下磁序与铁电极化的稳定性（MnPS₃ 单层层内 Néel 序、CrTe₂ 居里/奈尔温度的堆叠依赖）。
  - **SOC 效应仅作稳健性说明**（补充材料）， Rashba 型自旋纹理与 NRSS 的交叉调控未展开——对我们 Berry-MnPS₃ 课题是机会点。

  ## 与林赛研究的关联

  - **MnPS₃ / MnPSe₃ 材料重叠**：本组 `general-berry-mnps3-rashba-20260816` 课题以 MnPS₃ 为核心材料。本文给出 MnPS₃ 在 ≥4% 双轴拉应变下进入 Type-II 极性堆叠、d 波交替磁性、NRSS 符号随极化翻转——这是"Berry 相位工程 + 可控自旋劈裂"的结合点：NRSS 动量依赖自旋纹理直接调制 Berry 曲率分布，应变-极化两个外参量提供调控旋钮。
  - **强场驱动 / HHG / 阿秒**：NRSS 带劈裂 32 meV（MnPSe₃ 价带）到 130 meV（CrTe₂ 费米面）对应约 7.7–31 THz 能量尺度，强场中红外/太赫兹泵浦可分辨自旋分辨带间跃迁；极化可切换的 NRSS 意味着 HHG 或光电流中的自旋选择性可由电压门控——这是"交变磁 + 强场超快"器件构想的具体落点。
  - **莫尔 / 转角接口**：本文对比了扭转双层路线（ref. 65）与极性堆叠路线的 NRSS 增强，两者可在莫尔超晶格中叠加；莫尔势 + 铁电极化 + d 波交替磁性的联合对称性分析是开放方向。
  - **量子几何**：d 波交替磁体的节线（k_x = 0、k_y = 0）与六重对称自旋纹理（1T-CrTe₂）约束 Berry 曲率与量子度规的分布形态，可作为我们量子几何-强场响应框架的模型体系。
  - **实验接口**：滑动铁电的成熟实验（10¹¹ 周期无疲劳翻转）意味着"电压写入自旋纹理"在 vdW 器件上可行，可作为我们超快泵浦-探测样品设计的器件化参照。

  ## 来源
  - 蒸馏自全文（deep-read）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：二维反铁磁体非相对论自旋劈裂的对称性分类（自旋空间群 Type-I/II/III 三类 + MPX₃/CrTe₂ 代表）

**原理**：自旋空间群方法（自旋-空间解耦，操作记 [R_s||R_l]）把二维 AFM 的 NRSS 分为三类：Type-I（MnPSe₃ 双层，层间 Néel AFM，原生双层 P3̄）、Type-II（5% 双轴拉应变的 MnPS₃ 双层，≥4% 应变强制该基态）、Type-III（1T-CrTe₂ 双层 A-AFM 序=层内 FM+层间 AFM，亦见 CrSBr/MnBi₂Te₄）；结构上 AA̅ 堆叠不稳定、沿高对称方向滑移 ±a/3 弛豫到极性基态 AB̄/B̄A 破缺反演对称产生面外极化；Bilbao/FINDSYM/Pymatgen/PyProcar 辅助分析。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| DFT 设置 | VASP PAW/PBE；500 eV；16×16×1；力 <2×10⁻³ eV/Å；自洽 10⁻⁷ eV；真空 >20 Å；DFT-D3；偶极修正极化 | §第一性原理计算 |
| U 取值 | MnPSe₃/MnPS₃：U(Mn-d)=4 eV；1T-CrTe₂：U(Cr-d)=2 eV（旋转不变 DFT+U） | §DFT+U |

**适用边界**：半经验 DFT-D3；U 值经验取值；Type-II 需 ≥4% 应变（实验可实现性受限）。
**代表作**：本文（arXiv:2503.09877）；工具：Bilbao + FINDSYM + Pymatgen + PyProcar
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[2503.09877]]
- [[Berry 曲率]]
- [[CrSb]]
- [[MnPS3]]
- [[general-berry-mnps3-rashba-20260816]]
- [[层间耦合]]
- [[强场超快]]
- [[强场驱动]]
- [[泵浦探测]]
- [[滑动铁电]]
- [[自旋劈裂]]
- [[莫尔超晶格]]
- [[量子几何]]
- [[量子度规]]
<!-- /linsai-wikilinks -->
