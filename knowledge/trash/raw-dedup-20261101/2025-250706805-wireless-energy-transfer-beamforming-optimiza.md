---
has_fulltext: true
title: "Wireless Energy Transfer Beamforming Optimization for Intelligent Transmitting Surface"
arxiv_id: "2507.06805"
authors: "Osmel Martínez Rosabal, Onel Alcaraz López, Victoria Dala Pegorara Souto, Richard Demo Souza, Samuel Montejo-Sánchez, Robert Schober, Hirley Alves"
year: 2025
tags: ["deepxiv-论文库"]
project: ["NSFC-强场超快"]
direction: "光波电子学"
source: "hermes-briefing"
imported_at: "2026-08-12T11:25:02Z"
score_deepxiv: 0.2
status: "unseen"
read_status: "unread"
has_pdf: false
---
# Wireless Energy Transfer Beamforming Optimization for Intelligent Transmitting Surface

## 摘要
Radio frequency (RF) wireless energy transfer (WET) is a promising technology for powering the growing ecosystem of Internet of Things (IoT) using power beacons (PBs). Recent research focuses on efficient PB architectures that can support numerous antennas. In this context, PBs equipped with intelligent surfaces present a promising approach, enabling physically large, reconfigurable arrays. Motivated by these advantages, this work aims to minimize the power consumption of a PB equipped with a passive intelligent transmitting surface (ITS) and a collocated digital beamforming-based feeder to charge multiple single-antenna devices. To model the PB's power consumption accurately, we consider power amplifiers nonlinearities, ITS control power, and feeder-to-ITS air interface losses. The resulting optimization problem is highly nonlinear and nonconvex due to the high-power amplifier (HPA), the received power constraints at the devices, and the unit-modulus constraint imposed by the phase shifter configuration of the ITS. To tackle this issue, we apply successive convex approximation (SCA) to iteratively solve convex subproblems that jointly optimize the digital precoder and phase configuration. Given SCA's sensitivity to initialization, we propose an algorithm that ensures initialization feasibility while balancing convergence speed and solution quality. We compare the proposed ITS-equipped PB's power consumption against benchmark architectures featuring digital and hybrid analog-digital beamforming. Results demonstrate that the proposed architecture efficiently scales with the number of RF chains and ITS elements. We also show that nonuniform ITS power distribution influences beamforming and can shift a device between near- and far-field regions, even with a constant aperture.

## 背景概述与问题引入
射频无线能量传输 (WET) 是物联网供电的关键方案。能量发射机 (PB) 配备智能发射面 (ITS) 可形成大可重构阵列；但联合优化数字预编码 + ITS 相位 · 建模功放非线性 + ITS 控制功耗 + 馈线空口损耗 是强非凸问题。本文针对“ITS 辅助 PB 架构下最小化总功耗”展开。

## 关键发现及核心讨论
- **发现 1 (联合建模)**: HPA 非线性 + ITS 控制功耗 + 馈线-ITS 空口损耗 同时入模。
- **发现 2 (SCA + 初始化)**: SCA 联合求解预编码 + ITS 相位；初始化算法保证可行性 + 平衡收敛/质量。
- **发现 3 (可扩展性)**: 较全数字/混合架构 → 能耗优势随阵列规模放大。
- **发现 4 (非均匀功率分布的新效应)**: 固定孔径下使设备在近场与远场之间切换。

## 主要方法
- 优化模型: 最小化 PB 总功耗 · 受接收功率约束 + ITS 单位模约束。
- 算法: SCA + 可行初始化 · 迭代求解凸子问题。
- 对照: 全数字、混合模数波束成型。
- 指标: 能耗随 RF 链路 / ITS 单元数的扩展 · 近远场切换。

## 创新性
ITS 辅助 WET 架构中同时建模 HPA 非线性 + ITS 控制 + 馈线空口损耗，提出带可行性保证的 SCA 初始化。

## 结论与展望
ITS 辅助 PB 在大阵列下显著优于传统架构，且提供近-远场调控新自由度。后续：多用户多设备 · 自适应 ITS 拓扑 · 近场波束成型协议。