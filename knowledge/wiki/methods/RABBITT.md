---
title: "RABBITT"
type: "methods"
created: "2026-06-17T12:40:33Z"
updated: "2026-08-23T01:00:46Z"
tags: ["表征方法", "阿秒", "干涉", "#type/method", "#topic/HHG", "#status/mature"]
related: ["FROG", "Lewenstein模型", "三步模型"]
source_raw: ""
growth_stage: "mature"
confidence: 0.9
aliases: ["reconstruction-of-attosecond-beating", "重建阿秒拍频干涉"]
updated_at: "2026-08-23T01:00:46Z"
merged_from: ["wiki/concepts/RABBITT.md"]
---

# RABBITT

## 定义

RABBITT（Reconstruction of Attosecond Beating By Interference of Two-photon Transitions）是测量阿秒时间延迟的"金标准"方法。

## 原理

用一个孤立阿秒脉冲串（odd harmonics）加上弱红外（IR）驱动场，通过双光子跃迁的边带振荡，反推出电离时间延迟：

- XUV（odd harmonics）+ IR（fundamental）→ 产生 sideband（even harmonics）
- Sideband 振荡相位 ∝ 电离-连续态相位差 → 阿秒时间延迟 τ = Δφ/(2ω)
- 扫描 IR-XUV 延时，测 sideband 振荡

## 测量的是什么

电子从某能级电离后在连续态中积累的相位（Wigner-like delay）。

## 与其他方法对比

- **vs FROG**：RABBITT 需要阿秒脉冲串（频率梳），FROG-CRAB 用孤立阿秒脉冲。
- 简报标签中明确提到的相位匹配/高次谐波产生相关技术。

## 来源

- arXiv: 0707.4228（RABBITT vs FROG 对比）
- `hhg-methods-report.md`

## 关联概念

- [[FROG]]
- [[Lewenstein模型]]
- [[三步模型]]

<!-- linsai-wikilinks -->
## 关联概念

- [[FROG]]
- [[Lewenstein模型]]
- [[三步模型]]
<!-- /linsai-wikilinks -->
