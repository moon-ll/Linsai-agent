---
title: "Lewenstein模型"
type: "concept"
created: "2026-06-17T12:39:10Z"
updated: "2026-06-23T02:42:18Z"
tags: ["HHG", "理论模型", "SFA", "量子", "#type/concept", "#topic/HHG", "#status/mature", "#status/growing"]
related: ["RABBITT", "三步模型", "截止定律", "高次谐波产生"]
source_raw: ""
growth_stage: "mature"
confidence: 0.9
aliases: ["Lewenstein-model", "SFA", "strong field approximation", "强场近似"]
---

# Lewenstein 模型（SFA 强场近似）

## 林赛的理解

Lewenstein 模型（1994）是三步模型的量子力学精确化。它用强场近似（Strong Field Approximation, SFA）求解含时薛定谔方程，给出了 HHG 谱的量子振幅表达式，并自然包含了量子扩散和干涉效应。当经典三步模型不够用时（如讨论量子轨道、相位锁定），我会回到 Lewenstein 框架。

## 核心要点

**核心近似**：忽略束缚态-连续态耦合，只考虑 |0⟩（基态）↔ |p⟩（连续态 Volkov 态）。

**跃迁振幅**：x(t) = i∫dt' ∫dp [电子从基态隧穿 → 在 Volkov 态传播 → 复合到基态]
- 这个积分可以平稳相位近似，分解成经典轨道的量子版本

**关键物理**：
- 量子轨道：多条返回路径（短轨道、长轨道）相干叠加
- 电离时间 vs 复合时间的相位关系 → RABBITT 测的就是这个
- 高于阈值的电离（ATI）和 HHG 共享同一套量子轨道图像

**局限**：
- 忽略库仑效应（对低能谐波不准）
- 不含多电子效应

## 来源

- Lewenstein et al., "Theory of high-harmonic generation by low-frequency laser fields", PRA 49, 2117 (1994)
- arXiv: 0707.4192（改进 Lewenstein 模型）

<!-- linsai-wikilinks -->
## 关联概念

- [[RABBITT]]
- [[三步模型]]
- [[截止定律]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
