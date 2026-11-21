---
title: "strong-field-ultrafast"
type: "concepts"
created: "2026-10-24T18:06:51Z"
updated: "2026-11-15T15:09:18Z"
tags: ["concept", "backfill"]
related: ["RABBIT", "RABBITT", "attosecond-streaking", "high-harmonic-generation", "keldysh-parameter", "phase-matching", "photoemission-time-delay", "three-step-model", "tunnel-ionization", "三步模型", "孤立阿秒脉冲", "强场超快", "强场驱动", "截止定律", "相位匹配", "阿秒脉冲串", "高次谐波产生", "高次谐波产生（HHG）"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
aliases: ["strong-field-ultrafast"]
---

# 强场超快物理（strong-field-ultrafast）

## 定义定位

强场超快物理研究当激光电场强度与原子/分子内部库仑场可比拟（典型光强 10¹³–10¹⁵ W/cm²）时，物质在飞秒（10⁻¹⁵ s）乃至阿秒（10⁻¹⁸ s）时间尺度上的电子与结构动力学。“强场”意味着相互作用进入高度非线性区：隧穿电离、多光子电离、高次谐波产生（HHG）、非次序双电离等过程主导系统响应；“超快”则强调用超短脉冲作为驱动源或探针，对电子运动进行时间分辨的测量与操控。二者结合构成了从阿秒光脉冲产生到电子动力学测绘的核心物理平台。

## 物理内涵/技术原理

核心判据是 Keldysh 参数 γ = √(Iₚ/2Uₚ)：γ ≫ 1 对应多光子电离区，γ ≪ 1 对应隧穿电离区，其中 Iₚ 为电离势，Uₚ 为有质动力能（正比于光强 I 与波长平方 λ²）。在隧穿区，Corkum 的“三步模型”给出最简洁的物理图像：电子先隧穿电离，随后在激光场中被加速并获得动能，最后在场反向时回到母离子附近复合（或再散射）；复合将动能以高能光子形式释放，形成 HHG 平台及 Iₚ + 3.17Uₚ 的截止定律。同一图像也解释了高阈值电离（ATI）与非次序双电离（NSDI）中的再散射特征。

宏观上，单原子响应必须经由相位匹配才能转化为可观测的 HHG 信号：相干长度受基频—谐波相位失配、Gouy 相位、等离子体色散与中性色散共同制约，并与吸收长度竞争，决定最优聚焦几何与气压窗口——这正是样本 2025-2510_16672 所系统讨论的传播物理。时间维度上，HHG 的奇次谐波梳在频域锁相，可合成为阿秒脉冲串或孤立阿秒脉冲，进而支撑阿秒条纹（streaking）、RABBITT 等计时技术，实现对光发射延迟（Wigner 时延）的测量。样本 2025-2507_11497 对碘代烷烃的光发射计时即属这一脉络：用强场驱动与阿秒探测，把不同价壳层电离的时间差转化为可测的谱相位偏移。

## 与现有方法/概念的关联

- 作为上位概念统摄 [[high-harmonic-generation]]（强场最典型的相干辐射输出）与 [[tunnel-ionization]]（三步模型第一步的微观机制）。
- 定量骨架由 [[keldysh-parameter]] 与 [[three-step-model]] 给出；HHG 的宏观增强依赖 [[phase-matching]] 的传播优化。
- 时间测量端衔接 [[attosecond-streaking]] 与 [[photoemission-time-delay]]，是阿秒计时学（chronoscopy）的物理基础。
- 与弱场超快技术（如泵浦–探测光谱）形成对照：强场中光场本身直接驱动电子轨迹，而非仅作被动标记。

## 林赛理解

在本项目文献图谱中，strong-field-ultrafast 是一个“伞状”枢纽概念：它把两篇样本——HHG 相位匹配（宏观传播视角）与碘代烷烃光发射计时（单分子电子动力学视角）——统一到同一物理框架下。前者回答“强场信号如何相干地从介质中长出来”，后者回答“电离电子何时离开分子”，二者恰好覆盖强场超快物理的宏观与微观两端。鉴于该概念目前仅被引用 2 次、优先级为 low，本页定位为轻量枢纽节点：不追求穷尽综述，只给出 Keldysh 参数、三步模型、相位匹配、阿秒计时四条主线的最短路径，供后续任一支深入时由此跳转；若 liquid-phase HHG 或阿秒分子动力学文献增多，可在此节点下派生子页。

## 学习路径/参考

1. 建议入门顺序：Keldysh 参数与电离区划分 → 三步模型与 HHG 截止定律 → 相位匹配与宏观传播 → 阿秒脉冲与条纹计时。
2. 样本文献（项目内 id）：
   - 2025-2510_16672-phase-matching-of-high-harmonic-generation-i
   - 2025-2507_11497-photoemission-chronoscopy-of-the-iodoalkanes
3. 经典文献：Keldysh, *Sov. Phys. JETP* 20, 1307 (1965)；Corkum, *Phys. Rev. Lett.* 71, 1994 (1993)；Agostini & DiMauro, *Rep. Prog. Phys.* 67, 813 (2004)；Krausz & Ivanov, *Rev. Mod. Phys.* 81, 163 (2009)。

<!-- linsai-wikilinks -->
## 关联概念

- [[RABBIT]]
- [[RABBITT]]
- [[attosecond-streaking]]
- [[high-harmonic-generation]]
- [[keldysh-parameter]]
- [[phase-matching]]
- [[photoemission-time-delay]]
- [[three-step-model]]
- [[tunnel-ionization]]
- [[三步模型]]
- [[孤立阿秒脉冲]]
- [[强场超快]]
- [[强场驱动]]
- [[截止定律]]
- [[相位匹配]]
- [[阿秒脉冲串]]
- [[高次谐波产生]]
- [[高次谐波产生（HHG）]]
<!-- /linsai-wikilinks -->
