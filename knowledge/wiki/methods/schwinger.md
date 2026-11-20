---
title: "含量子几何修正的半经典玻尔兹曼输运（波包/Lippmann-Schwinger框架）"
type: "methods"
created: "2026-10-09T20:02:10Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "#type/method"]
related: ["2506.17386", "Intrinsic Nonlinear Hall Effect 的量子几何分解：三贡献拆解与 PT 对称反铁磁中的新主导项", "PLAN", "arXivID", "反常速度", "量子几何", "量子度规"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-09T20:02:10Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

在波包动力学/Lippmann-Schwinger框架的半经典玻尔兹曼输运中显式纳入量子带几何修正：量子度规经明确的微观通道进入电导与分布修正、构成面内磁阻响应的定量来源；二阶霍尔电导则可严格分解为三类几何偶极，各几何源的产生通道（反常速度 vs 带间相干）已被分别识别。

## 参数表

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 模型 | H = J₁Σ⟨i,j⟩Sᵢ·Sⱼ + J₂Σ⟨⟨i,j⟩⟩Sᵢ·Sⱼ + KΣ□[(Sᵢ·Sⱼ)(Sₖ·Sₗ)+(Sᵢ·Sₗ)(Sₖ·Sⱼ)]；J₁>0，K 四环交换解除简并 | 研究方法 
| 轨道 AM 特征 | 标量自旋手性交错排列 χ_EP ∝ (−1,1,−1,1)，保持 C4zΘ 与 σvΘ，M=0；从共线 AM 经二级相变演化 | 主要发现 
| 自旋液体对应表 | A1 共线 AM→U(1) SL；A2/A3→Z₂ SL；C 轨道 AM→交变磁自旋液体（Z₂，保持 C4zΘ,σvΘ 对称）——自旋旋转不变但标量自旋手性呈交变磁空间排列 | 主要发现 
| 谱函数参数 | t₂/t₁=0.3，μ/t₁=−1.2，H₀/t₁=1，T/t₁=0.1，展宽 η/t₁=0.05；谱函数由 chargon 与 spinon 格林函数卷积 | 研究方法 
| R-matrix 球半径 | 120 bohr | 研究方法（计算细节） 
| 连续电子基组 | 240 条九阶 B-spline | 研究方法（计算细节） 
| 最大角动量 | H⁻ ℓ_max = 5；Cl⁻ ℓ_max = 6 | 研究方法（计算细节） 
| IR 光子能量 | ω = 0.517 eV | 研究方法（计算细节） 
| H⁻ 基准延迟 | 峰值 ~21 as @6 eV（static-exchange）；计极化阈值处 46 as | 主要发现 
| NO₃⁻ 价层共振延迟 | 5.5 eV 共振达 1 fs；23 eV 共振 100 as | 主要发现 
<!-- src:2024-2410_10949-fractionalized-altermagnets-from-neighboring-and-alter -->
<!-- src:2026-2607_10397-on-the-measurability-of-wigner-time-delays-at-shape-re -->

## 适用边界

成立前提是波包半经典近似（外场缓变、能带间绝热可分）以及杂质散射的微扰式处理（LS 散射算符/弛豫时间类）；在能带简并点附近、强场带间隧穿或强关联等需全量子处理的情形失效，且定量结果依赖量子度规与贝里曲率等能带几何量的可靠计算。

## 代表作

- arXiv:2512.03814
- arXiv:2506.17386

## 证据日志

- 2026-10-09｜r61｜仅简报｜[paper:2025-2512.03814-quantum-geometric-planar-magnetotransport-a-probe-for-magnet] 含量子几何修正的半经典玻尔兹曼输运（波包/Lippmann-Schwinger框架）：给出量子度规进入电导与分布修正的显式微观通道，是面内磁阻响应的定量来源。
- 2026-10-09｜r61｜仅简报｜[paper:2025-2506.17386-quantum-geometric-origin-of-the-intrinsic-nonlinear-hall-eff] 含量子几何修正的半经典玻尔兹曼输运（波包动力学）：给出二阶霍尔电导按三类几何偶极的严格分解，并揭示各几何源的产生通道（反常速度 vs 带间相干）。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2506.17386]]
- [[Intrinsic Nonlinear Hall Effect 的量子几何分解：三贡献拆解与 PT 对称反铁磁中的新主导项]]
- [[PLAN]]
- [[arXivID]]
- [[反常速度]]
- [[量子几何]]
- [[量子度规]]
<!-- /linsai-wikilinks -->
