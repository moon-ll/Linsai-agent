---
title: "Shape of Wigner Crystals and Hole Self-Doping in a Mexican-Hat Dispersion"
arxiv_id: "2608.00170"
authors: "Minho Luke Kim, Xiao-Gang Wen"
year: 2026
tags: ["deepxiv-论文库"]
project: ["NSFC-强场超快"]
direction: "能谷电子学"
source: "hermes-briefing"
imported_at: "2026-08-04T13:05:07Z"
score_deepxiv: 0.5
status: "unseen"
read_status: "unread"
has_pdf: false
---
# Shape of Wigner Crystals and Hole Self-Doping in a Mexican-Hat Dispersion

## 摘要

We study Wigner crystals (WCs) induced by a strong Coulomb interaction from the ring-like Fermi surface of a Mexican-hat dispersion $ε_k= c_2k^2+c_4k^4$. We design orbital shape in order to minimize the energy of the WC, and find that a low ground-state energy requires an orbital shape with a depletion of electrons near $k=0$. To capture the Coulomb-induced correlations, we include a Jastrow factor as well as a factor describing the correlation between electrons and doped vacancies. Using variational Monte Carlo calculations, we calibrate the effective band parameters $c_2$ and $c_4$ to reproduce the two transitions observed experimentally as the electron density is lowered: from a spin-valley-polarized Fermi liquid with a disk-like Fermi surface, to one with a ring-like Fermi surface, and finally to a WC. We find that, even with an optimized orbital shape that depletes electrons near $k=0$, a WC with hole self-doping near $k=0$ can still be energetically favorable near the WC transition, provided that the electron-vacancy correlation is included. We also estimate the dispersion of the doped hole.

## 背景概述与问题引入

Wigner 晶体是电子在强库仑抵拒下自发形成的位置有序相，常见于低密度二维电子气。但当能带本身不是简单抛物线、而是 Mexican-hat 形（在 Gamma 点有局部极大值）时，环状费米面带来的嵌套与能量曲率反转给 WC 的形成带来新自由度：晶体是否仍然稳定？其轨道形状如何适应环状费米面？空穴能否在 k=0 附近共存？这正是本文要回答的核心问题。

## 关键发现及核心讨论

- **轨道形状设计原则**：通过变分设计轨道形状来最小化 Wigner 晶体（WC）的基态能量，发现低能态要求轨道在 k=0 附近电子密度有耗尽（depletion）。
- **变分蒙特卡洛 + Jastrow 因子**：用 Jastrow 因子刻画电子-电子关联，并额外引入描述电子-掺杂空穴之间关联的因子，从而完整捕捞 Mexican-hat 形能带 c2 k^2 + c4 k^4 带来的环状费米面关联效应。
- **重整有效能带参数，匹配实验两阶段相变**：在 transition metal dichalcogenide 等具有 Mexican-hat 色散的材料中，电子密度降低时会经历"自旋-谷极化费米液体（盘状费米面）-> 环状费米面 -> Wigner 晶体"两个相变；作者把 c2、c4 与之校准，实现与实验的定量对应。
- **空穴自掺杂（hole self-doping）作为能量上更优的 WC 形态**：即使在 k=0 附近对电子轨道做了耗尽优化，仍然存在一种携带 k=0 附近空穴自掺杂的 WC 在 WC 转变点附近能量更低，前提是引入电子-空穴关联项；这是论文最反直觉的新结果。
- **掺杂空穴色散的估计**：作者进一步给出该掺杂空穴的有效色散，为实验探测（如 STM 准粒子干涉或谱学测量）提供预测。

## 主要方法

理论框架：Mexican-hat 色散紧束缚模型；变分蒙特卡洛（VMC）求解 WC 基态；Jastrow + 电子-空穴关联因子；将 c2、c4 与实验观测的两阶段相变校准。

## 创新性

不同于以往假设均匀轨道形状的 Wigner 晶体研究，本文把"轨道形状优化 + 空穴自掺杂"同时纳入 WC 描述，发现 k=0 附近的电子耗尽和空穴掺杂会在能量上共同降低 WC 态，并给出可与 STM 谱学对照的空穴色散。

## 结论与展望

为具有环状/Mexican-hat 色散的半导体（如部分 TMD、双层石墨烯、转角 TMD）中的关联绝缘态提供微观图像；空穴自掺杂机制可推广到其他具有局部极大值色散的系统，并指导后续实验区分 WC 与电荷密度波等竞争序。