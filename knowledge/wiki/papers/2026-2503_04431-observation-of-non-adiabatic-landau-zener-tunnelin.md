---
title: "Observation of non-adiabatic Landau-Zener tunneling among Floquet states"
type: "papers"
created: "2026-08-17T09:52:16Z"
updated: "2026-08-23T01:01:18Z"
tags: ["Floquet工程", "Landau-Zener隧穿", "光波电子学", "多光子光电子能谱", "强场超快光学", "固体HHG", "非绝热动力学"]
related: ["Cu(111)", "Floquet states", "Landau-Zener transition", "general-order-parameter-ultrafast-readout-20260727", "high-harmonic generation in solids", "instantaneous Floquet theory", "lightwave electronics", "multi-photon photoemission", "non-perturbative light-matter coupling", "固体高次谐波", "固体高次谐波产生", "高次谐波产生"]
source_raw: "2026-2503.04431-observation-of-non-adiabatic-landau-zener-tunnelin.md"
growth_stage: "growing"
confidence: 0.7
auto_grown: true
review_status: "pending"
updated_at: "2026-08-23T01:01:18Z"
merged_from: ["wiki/papers/2503.04431.md"]
---

# Observation of non-adiabatic Landau-Zener tunneling among Floquet states

## 概述

Yen 等人在 Cu(111) 表面态上做了一项将 Floquet 工程边界从「弱场微扰」推进到「非微扰、强场、非绝热」的工作。长期以来，Floquet 物理在固体中一直被视为周期驱动下的「稳态修饰」，默认处于两种理想化假设之一：微扰极限（小场强，态可由小参数展开）或绝热极限（场强变化足够慢，系统沿瞬时 Floquet 态演化）。在真实的强场光波电子学场景里，这两个假设往往同时失效——场强大到微扰论彻底崩溃，而光场瞬态包络不可避免地存在开启/关闭的非绝热区域。

选择 Cu(111) 体系的优势在于：sp 金属表面态的色散和带结构理论与实验（ARPES/2PPE）都成熟，便于把信号解释的「理论负担」压到最低，使关注点集中在 Floquet 态本身的非绝热演化上。

## 核心要点

1. **实验现象**：在 Cu(111) 表面态上，随着入射光场强度增大，体系从「微扰 Floquet 修饰」平滑过渡到「Floquet 态之间的非绝热 Landau-Zener 隧穿」区。场强继续增大时，绝热 Floquet 演化图像彻底失效。

2. **关键转变**：识别出一个明确的场强阈值，跨越之后 Floquet 态不再是「被动的态」，而是会主动通过免交叉（avoided crossing）发生隧穿——这是 Landau-Zener 物理在 Floquet 态之间的直接体现。

3. **结论的普适意义**：作者明确把这一非绝热 Floquet 隧穿 regime 与三个宏观现象挂钩：
   - 光致态修饰（light-dressing）的真正起点
   - 非微扰光波电子学
   - 固体高次谐波产生（HHG）

   即**固体 HHG 在强场下很可能就是一系列非绝热 Landau-Zener 跳跃的级联结果**。

## 机制：非绝热 Landau-Zener 隧穿

Floquet 态之间通过免交叉（avoided crossing）发生隧穿，是 Landau-Zener 物理在 Floquet 态之间的直接体现。隧穿概率表达式包含与 Berry 相相关的几何相位项。

传统稳态 Floquet 理论在强场、非绝热条件下失效，原因在于：稳态 Floquet 理论基于固定的周期场，而真实脉冲具有瞬态包络，必须用每一时刻的瞬时场幅去构造瞬时 Floquet 哈密顿量，这样非绝热耦合才能自然出现。

## 实验方法

- **干涉式多光子光电子能谱（interferometric TR-2PPE）**：用一对相位锁定的脉冲干涉，直接读出 Floquet 态的瞬态布居以及相位信息。关键意义在于：只有相位敏感的测量才能区分「绝热跟随」与「非绝热隧穿」——后者会留下可识别的相位印记。

- **瞬时 Floquet 态理论（instantaneous Floquet states）**：不是用稳态 Floquet 理论拟合，而是用每一时刻的瞬时场幅构造瞬时 Floquet 哈密顿量，使非绝热耦合自然出现。

- **数值模拟**：与实验直接比对的 real-time 模拟，追踪实际的激发路径（excitation pathways），而非只给能谱。

- **方法学特点**：干涉式 TR-2PPE 对光场相位稳定性要求极高，需要飞秒级相位锁定，对机械振动、光路稳定性的要求远高于普通 TR-2PPE。

## 研究方向关联

- **光波电子学方向**：attosecond-scale electron control 的核心瓶颈是缺乏对瞬态 Floquet 演化的直接测量。Yen 等人的干涉式 2PPE 技术原则上可移植，用来追踪 sub-cycle 电子动力学，从而把「光场相位 → 电子终态」的映射从半经典的 three-step model 升级到量子相干版本。

- **固体 HHG 方向**：若 HHG 微观机制确实涉及非绝热 Landau-Zener 隧穿，则 HHG 谱对 order parameter 的灵敏度需重新评估——隧穿概率本身对能带结构（特别是 gap 大小）的依赖是非线性的，而非简单依赖光电流或振幅。

- **量子几何 / 拓扑方向**：Landau-Zener 隧穿概率的表达式里有 Berry 相关的几何相位项。将 Cu(111) 替换为拓扑材料（如 Bi₂Se₃ 表面态或 twisted bilayer），非绝热 Floquet 隧穿本身可能成为探测量子几何（quantum metric / Berry curvature）的工具。

- **方法学借鉴**：已有的 HHG 干涉实验具备相位锁定能力，理论上可扩展到干涉式 TR-2PPE 框架。

## 开放问题

1. **非绝热阈值的可预测性**：从弱场到强场的过渡阈值由什么物理量决定？是光场频率与能带特征长度的乘积？电子-电子散射时间？还是 Floquet 态间的最小免交叉 gap？文章中似乎没有给出明确的标度律（scaling law），这是一个理论缺口。

2. **与 HHG 的定量对应**：声称「固体 HHG = 非绝热 LZ 隧穿级联」，但未给出直接实验关联——例如同一场强区间内的 HHG 谱与 2PPE 测得的 LZ 隧穿概率之间的定量对应。cross-validation 实验值得开展。

3. **多体效应**：Cu(111) 的表面态虽然相对干净，但电子-电子散射、电子-声子散射在强场下不可避免。瞬时 Floquet 理论是单粒子图像，多体修正是否会破坏 LZ 隧穿的清晰信号？特别是在 1 eV 以上的强场区，电子的二次激发和加热效应可能使 Floquet 描述本身失效。

4. **体系拓展性**：从 sp 金属到 d 电子金属、到拓扑半金属、到莫尔系统，LZ 隧穿概率的几何相位贡献将越来越重要，实验难度也急剧上升。是否有可能在所给方法框架下，做出「量子几何 + 非绝热 Floquet」的统一表，是领域中可能的实质性进展。

5. **实验方法的可推广性**：干涉式 2PPE 要求飞秒级相位锁定，对机械振动、光路稳定性要求远高于普通 TR-2PPE。作者未详细给出误差预算和时间分辨率的限制，这会影响该方法在其他体系（如低温、强磁场下的拓扑材料）上的适用性。

## 关联概念

- [[Cu(111)]]
- [[Floquet states]]
- [[Landau-Zener transition]]
- [[general-order-parameter-ultrafast-readout-20260727]]
- [[high-harmonic generation in solids]]
- [[instantaneous Floquet theory]]
- [[lightwave electronics]]
- [[multi-photon photoemission]]
- [[non-perturbative light-matter coupling]]
- [[固体高次谐波]]
- [[固体高次谐波产生]]
- [[高次谐波产生]]

## 来源

- 原始材料：2026-2503.04431-observation-of-non-adiabatic-landau-zener-tunnelin.md
- 蒸馏时间：2026-08-17T09:52:16Z

<!-- linsai-wikilinks -->
## 关联概念

- [[Cu(111)]]
- [[Floquet states]]
- [[Landau-Zener transition]]
- [[general-order-parameter-ultrafast-readout-20260727]]
- [[high-harmonic generation in solids]]
- [[instantaneous Floquet theory]]
- [[lightwave electronics]]
- [[multi-photon photoemission]]
- [[non-perturbative light-matter coupling]]
- [[固体高次谐波]]
- [[固体高次谐波产生]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
