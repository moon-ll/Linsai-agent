---
title: "Floquet诱导的二维d波交磁体各向异性磁阻与反常霍尔效应（Rashba自旋轨道耦合）精读笔记"
type: "concepts"
created: "2026-10-25T20:05:24Z"
updated: "2026-10-26T10:59:52Z"
tags: ["concept", "backfill"]
related: ["反常霍尔效应", "自旋劈裂"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
aliases: ["Floquet诱导的二维d波交磁体各向异性磁阻与反常霍尔效应（Rashba自旋轨道耦合）精读笔记"]
---

# Floquet诱导的二维d波交磁体各向异性磁阻与反常霍尔效应（Rashba自旋轨道耦合）精读笔记

## 定义定位

本页是对“周期（Floquet）驱动下二维 d 波交磁体输运响应”这一工作的精读笔记式概念页。研究对象是同时具备 d 波交替磁自旋劈裂（形如 Δ(cos kx − cos ky)σz，符号随奈尔矢量取向翻转）与 Rashba 自旋轨道耦合 λ(kyσx − kxσy) 的二维晶格，在线偏振周期场驱动下，通过 Floquet 高频展开得到的有效哈密顿量中同时诱导出各向异性磁阻（AMR）与反常霍尔效应（AHE）。其定位在于：把“外场作为对称性旋钮”的思想施加于零净磁化的共线磁体，证明无需铁磁序也能获得可调的磁阻与霍尔响应；在知识库中，它连接 Floquet 工程、交磁体物理与自旋电子学输运三条主线。

## 物理内涵/技术原理

**模型与驱动。** 母体哈密顿量取 H0(k) = ε(k)σ0 + Δ(cos kx − cos ky)σz，其中 Δ 为交磁交换劈裂；Rashba 项 HR = λ(kyσx − kxσy) 来自面外反演破缺。线偏振光经 Peierls 代换 k → k − A0cos(ωt)û 进入跳跃项，û 为面内偏振方向。

**Floquet 有效理论。** 在 ℏω 远超带宽的高频区，对含时跳跃做 Bessel 平均（van Vleck 展开零阶项）：跳跃 t 与劈裂 Δ 被 J0(A0) 重整。关键机制在于线偏振**选择性**重整化沿 û 方向的跳跃（如 cos kx 的系数变为 J0(A0)cos kx，而 cos ky 保持不变），显式破坏 C4 旋转对称；Rashba 系数 λ 亦被偏振相关的贝塞尔因子压低。

**AMR

<!-- linsai-wikilinks -->
## 关联概念

- [[反常霍尔效应]]
- [[自旋劈裂]]
<!-- /linsai-wikilinks -->
