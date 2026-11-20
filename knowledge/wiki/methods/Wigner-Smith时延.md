---
title: "Wigner-Smith（Eisenbud-Wigner-Smith）时延"
type: "methods"
created: "2026-09-18T16:44:34Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "type/method"]
related: ["1407.6613", "2312.14174", "2403.13650", "RABBIT", "RABBITT", "TDDFT", "TDSE"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-09-27T02:13:42Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

Eisenbud-Wigner-Smith（Wigner-Smith）时延将通道分辨的光电离时间延迟定义为散射（振幅）相位对能量的微商（τ = ℏ ∂φ/∂E），作为单通道散射的内在参考延迟，用于把阿秒条纹等测得的表观延迟按通道分解，并充当多通道多光子理论的基准物理量。

## 参数表

**canonical 升级**（2026-11-01，教科书级方法要素，引用已核实）：
Wigner-Smith 时延 τ_W = ℏ ∂δ/∂E 定义为散射相位对能量的导数，是光发射时间延迟的单粒子定义；RABBITT/条纹测到的表观时延还叠加连续-连续交扰（cc）项，比较时必须扣除。

| 要素 | 内容 | 出处 |
| --- | --- | --- |
| 定义 | τ_W = ℏ ∂arg(D_k)/∂ε | [1] |
| 实测量 | 表观延迟 = τ_W + τ_cc（cc 由软库仑或 TDSE 标定） | [2] |
| Ne 基准 | 2p-2s 实验 ±21±5 as；理论 4.82/8.19 as（SAE/RPAE） | [2] |

✅ 原子分子光发射时延的理论量与实验解释。
❌ 凝聚态需重定义（输运+退相干混叠）；多电子体系需 RPAE/TDDFT 修正。

- F. T. Smith, "Lifetime matrix in collision theory," Phys. Rev. 118, 349 (1960). https://doi.org/10.1103/PhysRev.118.349
- "角分辨阿秒条纹光发射时间延迟," arXiv:1407.6613. https://arxiv.org/abs/1407.6613

## 适用边界

该定义严格对应单通道散射相位可明确定义的情形（弱场/单光子散射近似），仅作参考基准而非可观测量——条纹法测得的表观延迟与多光子多通道过程需结合通道分解及探测场修正项方能与之比较。

## 代表作

- arXiv:2312.14174
- arXiv:2403.13650

## 证据日志

- 2026-09-18｜r18｜仅简报｜[paper:2023-2312.14174-evaluating-the-accuracy-of-attosecond-streaking-time-delay-m] Wigner-Smith（Eisenbud-Wigner-Smith）时延：作为单通道散射相位能微商的参考延迟定义，用于分解表观延迟的构成。
- 2026-09-18｜r18｜仅简报｜[paper:2024-2403.13650-theory-of-attosecond-time-delays-in-multiphoton-multichannel] Eisenbud-Wigner-Smith 时间延迟理论：将通道分辨的光电离时间延迟定义为散射振幅相位对能量的导数，作为多通道分解的基准物理量。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[1407.6613]]
- [[2312.14174]]
- [[2403.13650]]
- [[RABBIT]]
- [[RABBITT]]
- [[TDDFT]]
- [[TDSE]]
<!-- /linsai-wikilinks -->
