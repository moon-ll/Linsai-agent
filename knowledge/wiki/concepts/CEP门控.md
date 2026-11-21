---
title: "CEP门控"
type: "concepts"
created: "2026-10-06T18:54:32Z"
updated: "2026-11-03T15:40:17Z"
tags: ["type/concept", "topic/阿秒科学", "topic/强场超快", "topic/HHG"]
related: ["光波电子学", "相对论等离子体镜面", "载波包络相位", "孤立阿秒脉冲"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
aliases: ["CEP gating", "CEP 效应", "CEP门控__CEP_gating", "carrier-envelope phase gating", "载波包络相位门控"]
updated_at: "2026-11-03T15:40:17Z"
merged_from: ["wiki/methods/CEP门控.md"]
---

# CEP门控（Carrier-Envelope Phase Gating）

## 定义

载波-包络相位（CEP，Carrier-Envelope Phase）门控，是一种通过控制少周期激光脉冲的载波-包络相位，实现亚周期激光脉冲相位稳定与波形精准控制的技术，也是光波电子学的关键手段。

CEP门控可进一步用于相对论等离子体镜面上的 XUV 连续谱产生，以及相对论电子束的 attosecond（阿秒）精准控制。

## 一句话直觉

CEP 决定"载波振荡的波峰落在脉冲包络的哪个位置"——对多周期脉冲这只是波形内部的无害平移，对少周期脉冲则直接决定最强的那个半周出现在脉冲头部还是尾部，从而决定电离与发射发生的瞬时时刻。

## 数学表述

线偏振少周期脉冲电场的标准写法：

\[
E(t) = E_0 \cdot f(t) \cdot \cos(\omega t + \varphi_{\mathrm{CEP}})
\]

其中 \(f(t)\) 为慢变包络，\(\varphi_{\mathrm{CEP}}\) 即载波-包络相位。周期数 \(N \gg 1\) 时改变 \(\varphi_{\mathrm{CEP}}\) 只是波形平移，物理效应可忽略；\(N \lesssim 2\) 时 \(\varphi_{\mathrm{CEP}}\) 改变电场峰值位置与波形不对称性，隧穿电离时刻、发射窗口等强场过程随之显著变化——这正是"门控"的物理来源。

## 机制

通过 CEP 门控获得相位稳定、可重复的 sub-1.5-cycle（亚 1.5 个光学周期）激光脉冲波形，从而对强场物理过程实现 attosecond 级时间控制。

## 实验表现

- 实现亚周期激光脉冲的相位稳定控制。
- 首次实现通过 CEP 门控的 sub-1.5-cycle 激光脉冲，在相对论等离子体镜面上可靠产生 XUV 连续谱，并实现对相对论电子束的 attosecond 精准控制。
- CEP 稳定度达到约 **380 mrad rms**，可持续约 **1 小时**。
- 运行在 **kHz 重频**下，并实现稳定输出。

## 常见误用

- **CEP 稳定 ≠ CEP 门控**：CEP 稳定只是锁定 \(\varphi_{\mathrm{CEP}}\) 使其不逐发漂移，是前置条件；CEP 门控是利用 \(\varphi_{\mathrm{CEP}}\) 的取值把发射限制在单个光学半周期内、输出孤立阿秒脉冲——二者不是同义词。
- **长脉冲语境下谈 CEP 门控**：CEP 敏感性随周期数增大迅速消失，多周期脉冲的光谱对 \(\varphi_{\mathrm{CEP}}\) 基本不敏感；仅在少周期（sub-2-cycle 量级）语境下讨论门控才有意义。

## 来源

- arXiv:2406.06396（简报评级：4.5/5）

## 关联概念

- [[光波电子学]]
- [[相对论等离子体镜面]]
- [[载波包络相位]]
- [[孤立阿秒脉冲]]

<!-- linsai-wikilinks -->
## 关联概念

- [[光波电子学]]
- [[相对论等离子体镜面]]
- [[载波包络相位]]
- [[孤立阿秒脉冲]]
<!-- /linsai-wikilinks -->
