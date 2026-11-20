---
title: "Real-space perspective on dephasing in solid-state high harmonic generation"
type: "papers"
created: "2026-10-08T10:54:08Z"
updated: "2026-11-15T15:09:22Z"
tags: ["solid-state-HHG", "dephasing", "real-space-method", "Wannier-Stark", "ultrafast-dynamics", "strong-field"]
related: ["2109.07693", "2401.12929", "Berry 曲率", "Floss et al. 2021: Si与金刚石在近/中红外驱动下的高次谐波产生（TDDFT研究）", "TDDFT", "TDSE", "Unveiling the Role of Electron-Phonon Scattering in Dephasing High-Order Harmonics in Solids", "Wannier-Stark localization", "dephasing time in HHG", "quantum geometry inversion", "real-space semiclassical model", "solid-state high harmonic generation", "固态高次谐波", "层间耦合", "强场超快", "范德华异质结", "量子几何", "高次谐波产生"]
source_raw: "2024-2410.04512-real-space-perspective-on-dephasing-in-solid-state-high-harm.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Real-space perspective on dephasing in solid-state high harmonic generation

## 林赛的理解

这篇 Brown–Jiménez-Galán–Silva–Ivanov 的工作 (arXiv:2410.04512, 2024) 一直放在我案头，是我做固态高次谐波退相干机制时绕不开的一篇。它从一个我很在意的角度切入：**完全在实空间**重写固态 HHG 的退相干模型，并把这个退相干长度明确地与 **Wannier-Stark 局域距离**绑在一起。在我之前看的多数文献里，退相干时间是被当作一个可调参数往里塞的——为了复现实验上观察到的谐波截止、平台结构、亚周期动力学，人们不得不假设一个"极短"的退相干时间（通常是亚飞秒量级），但这个数字从哪来、为什么这么短，很少有人给出微观层面的论证。这篇论文的核心吸引力，就是它给出了一个空间局域化的图像：电子波包在强场下被 Wannier-Stark 态钉在实空间的某个范围里，退相干的长度标度因此天然是"局域距离"本身，而不是某个抽象的动量空间关联时间。

## 核心要点

- **完全实空间的固态 HHG 建模**：区别于主流动量空间（含 Bloch 加速定理 + Berry 曲率）的处理方式，作者把整个产生过程放到实空间里来做。这对于描述 **局域化、退局域化、再干涉** 这类现象是更自然的语言。
- **退相干由 Wannier-Stark 局域距离决定**：在强直流电场下，Wannier 中心沿场方向被局域化到有限的 Stark 距离内。论文把退相干的有效长度/时间与这个局域距离耦合起来——而不是作为一个自由参数。
- **解释了实验上"超短退相干时间"为何必须**：以往拟合 HHG 实验谱时总要假设一个非常短的相干时间。这篇工作给出了这个短时间的物理起源：它就是 Stark 局域尺度对应的时间，从而把一个"凑参数"变成了一个"可计算量"。
- **作者阵容**：Brown（实空间方法）、Jiménez-Galán（HHG 微观模型）、Silva（强场理论）、Ivanov（阿秒+强场老牌组）。这是 Ivanov 组在固态 HHG 退相干方向上的延续性工作。

## 实验/研究关联

- **与 NSFC 强场超快项目的连接**：我们项目里的 "general-quantum-geometry-inversion" 提案正是要把 HHG 中观测到的反常（如反常偏振、ellipticity response、Berry 曲率痕迹）反演回 **量子几何**。这一步的关键前提是：**退相干已经"清洗"了部分纯几何信息**。Brown 等给出的实空间图像告诉我，在反演的时候应该用什么尺度来量化退相干对几何量的"擦除"程度——即 Wannier-Stark 局域长度，而非随意一个 decoherence constant。
- **与 Silva 之前工作的衔接**：Silva 2023 那篇将 Wannier-Stark 局域与椭圆依赖联系起来的文章，我需要回头交叉看，确认这篇 2410.04512 是把 **dephasing time** 明确化成 **Stark-localization length / drift velocity** 的版本。如果是，那么椭圆响应曲线在长退相干极限下的标度律就应该被改写——这是我下一步要在 group meeting 上推的。
- **对我组 TDSE/RMT 代码的启示**：我们用紧束缚 + 含时薛定谔做 HHG 的代码目前还是动量空间的"双带 + 退相干时间常数"框架。要么 (i) 在动量空间里把 dephasing 项写成依赖于动量-实空间映射的算符，要么 (ii) 直接迁一套实空间基组（如 Wannier 基 + 有限格点）。前者改动小、物理图像模糊；后者改动大、但和这篇工作的语言直接对接。值得让博士后做一次 benchmark。
- **对多轨道/层状材料的推广**：在范德华异质结、扭转双层等体系里，Wannier 中心的层间耦合会让局域距离变成一个张量。这给我一个新的自由度：能不能用 HHG 偏振依赖**反推** Stark 局域的各向异性？这可以写进下一轮 NSFC 续期的"科学问题"段落。

## 开放问题

- **实验能不能直接测量这个 Wannier-Stark 局域长度？** 当前实验给出的是谐波谱，截止、平台、对齐依赖。我不确信有任何现有实验能区分"退相干时间 = τ" 和"退相干长度 = L_Stark"。两条路径在谱上是否完全简并？需要仔细看论文的数值例子。
- **温度/声子的角色**：Wannier-Stark 是纯静电场图像。真实材料里晶格振动会给 Stark 距离一个额外的展宽。论文是否包含？摘要未提，我读全文时要重点检查。
- **强场破坏 Wannier-Stark 局域的临界条件**：当场强高到 Zener 隧穿开启，局域会被破坏（这本来也是 HHG 的核心机制）。这意味着 L_Stark 本身是 **场强依赖的**，退相干长度因此不是常数。这一点如果论文处理了，是这篇工作真正的亮点；如果没处理，是个明显的 open gap。
- **与 quantum geometry inversion 的兼容性**：我组目前的反演算法假设 dephasing 是 i.i.d. 的、均匀的。如果 dephasing 是 **Wannier-Stark 距离决定的、非均匀的**，那反演的 regularization 矩阵要不要重写？这是我必须想清楚的事。

## 来源
- 原始材料：2024-2410.04512-real-space-perspective-on-dephasing-in-solid-state-high-harm.md
- 蒸馏时间：2026-10-08T10:54:08Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：实空间固态 HHG 退相干模型：退相干长度 = Wannier-Stark 局域距离

**原理**：完全在实空间重构固态 HHG 退相干模型（区别于主流动量空间 Bloch 加速+Berry 曲率处理）。核心机制：强直流场下 Wannier 中心沿场方向被局域化到有限 Stark 距离，退相干的有效长度/时间与该局域距离耦合而非自由参数——给出实验拟合中长期必需的'超短退相干时间'的物理起源（Stark 局域尺度对应的时间），把'凑参数'变为'可计算量'。对局域化、退局域化、再干涉类现象是更自然的语言。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 理论框架 | 完全实空间固态 HHG 建模（Wannier 基） | 核心要点 |
| 核心等式 | 退相干长度/时间 ↔ Wannier-Stark 局域距离（非自由参数） | 核心要点 |

**适用边界**：摘要级：温度/声子对 Stark 距离的展宽是否包含未提；强场 Zener 隧穿开启后局域被破坏（L_Stark 场强依赖、非常数）是否处理为关键 open gap；'退相干时间 τ vs 退相干长度 L_Stark'两条路径在谱上是否简并（实验可区分性）待数值例子检验；与 quantum-geometry-inversion 兼容性——若退相干为 Stark 距离决定的非均匀过程，反演 regularization 矩阵需重写。与 Korolev 2401.12929（动量依赖退相干）及 Freeman 2109.07693（MD 退相干）构成退相干机制三视角。
**代表作**：Brown, Jiménez-Galán, Silva, Ivanov, Real-space perspective on dephasing in solid-state high harmonic generation, arXiv:2410.04512 (2024)
*方法卡回补 2026-10-08*

<!-- linsai-wikilinks -->
## 关联概念

- [[2109.07693]]
- [[2401.12929]]
- [[Berry 曲率]]
- [[Floss et al. 2021: Si与金刚石在近/中红外驱动下的高次谐波产生（TDDFT研究）]]
- [[TDDFT]]
- [[TDSE]]
- [[Unveiling the Role of Electron-Phonon Scattering in Dephasing High-Order Harmonics in Solids]]
- [[Wannier-Stark localization]]
- [[dephasing time in HHG]]
- [[quantum geometry inversion]]
- [[real-space semiclassical model]]
- [[solid-state high harmonic generation]]
- [[固态高次谐波]]
- [[层间耦合]]
- [[强场超快]]
- [[范德华异质结]]
- [[量子几何]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
