---
title: "rabi-oscillation"
type: "methods"
created: "2026-10-17T10:27:02Z"
updated: "2026-11-01T10:30:19Z"
tags: ["方法学", "#type/method"]
related: ["2603.19875", "DFT计算", "sbe-bloch-equations", "库仑关联对单层TMDC高次谐波生成的影响", "量子拍读出", "高次谐波产生", "高次谐波产生（HHG）"]
source_raw: ""
growth_stage: "growing"
confidence: 0.5
updated_at: "2026-11-01T10:30:19Z"
settled_count: 2
aliases: ["Rabi oscillation", "Rabi frequency", "Rabi", "拉比振荡", "喇比振荡", "拉比频率"]
---

<!-- methods-settle:v1 -->

## 原理

拉比振荡指近共振驱动下两能级/带间布居的相干周期性往返（Ω_R = |d_cv·E|/ℏ，缀饰态图像中表现为准能级劈裂与谱线展宽，用于解释共振 HHG 宽谱谐波结构）；新证据在时域检验了该缀饰态/Rabi 相干图像——Floquet-Bloch 带的成带时间对应缀饰态相干积累、失相由 T₂ 型退相干支配，从而为拉比/Floquet 相干操控设定了明确的时间窗口。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| Rabi 频率 | Ω_R = |d_cv·E|/ℏ | sbe-bloch-equations |
| 脉冲面积（π 脉冲翻转条件） | ∫Ω_R dt = π | DFT计算 |
| 退相干时间 T₁/T₂（阻尼拉比振荡；T₂ 型退相干同时设定 Floquet 带成带-失相时间窗口） | T₁/T₂ 进入后为阻尼拉比振荡 | sbe-bloch-equations; paper:2024-2501.03798-build-up-and-dephasing-of-floquet-bloch-bands-on-subcycle-ti |

## 适用边界

仅当强共振耦合且缀饰态相干积累能在 T₂ 型退相干发生前的有限时间窗口内完成时适用（该窗口同时约束 Floquet 工程的有效脉冲时长）；少能级缀饰态近似在微扰区、多体库仑关联或退相干主导时失效，且全时域含时模拟成本高。

## 代表作

- 2026-2603.19875-influence-of-coulomb-correlations-on-high-harmonic-generatio
- 2024-2501.03798-build-up-and-dephasing-of-floquet-bloch-bands-on-subcycle-ti

## 证据日志

- 2026-10-17｜r77｜仅简报｜[paper:2026-2603.19875-influence-of-coulomb-correlations-on-high-harmonic-generatio] 共振驱动的缀饰态/拉比振荡谱分析：用dressed-state图像解释共振HHG的谱线展宽与劈裂，将宽谱谐波归因于场-激子强耦合。
- 2026-11-01｜r112｜仅简报｜[paper:2024-2501.03798-build-up-and-dephasing-of-floquet-bloch-bands-on-subcycle-ti] 缀饰态/Rabi 相干图像的时域检验：把成带时间与缀饰态相干积累、失相与 T2 型退相干时间直接联系起来，给出 Floquet 工程的时间窗口约束。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2603.19875]]
- [[DFT计算]]
- [[sbe-bloch-equations]]
- [[库仑关联对单层TMDC高次谐波生成的影响]]
- [[量子拍读出]]
- [[高次谐波产生]]
- [[高次谐波产生（HHG）]]
<!-- /linsai-wikilinks -->
