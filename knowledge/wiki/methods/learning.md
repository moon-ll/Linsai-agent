---
title: "闭环学习控制（closed-loop learning control）"
type: "methods"
created: "2026-10-17T06:41:58Z"
updated: "2026-10-17T06:41:58Z"
tags: ["方法学", "#type/method"]
related: []
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-17T06:41:58Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

闭环学习控制是源自飞秒化学脉冲整形传统的"教会激光器"式实验反馈优化范式：以实测目标信号为适应度迭代更新整形脉冲波形，从而在哈密顿量建模不准、无需精确系统模型的情况下仍能逼近最优控制场，被综述评价为最具实用价值的量子控制方法。

## 参数表

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 库内评分 | deepxiv 0.83 | 实验/研究关联 
| 相变阈值 | Poisson/Helmholtz λ≥5、波动方程 b≥3、Sine–Gordon k≥8、NLS n≥4（低复杂度区经典领先 1.4–4.3 倍） | 主要发现 1（相位复杂度相变） 
| 高复杂区优势 | 对最强经典基线领先 1.5×（波动）至 12×（Helmholtz 与 NLS 振幅恢复）；可训练参数约为经典基线 1/4 | 主要发现 1/4 
| 代表精度（relative L²） | Poisson λ=5：PI-HPQNN (6.11±1.73)×10⁻³ vs PINN 1.66；Helmholtz λ=4：(2.72±1.34)×10⁻²；NLS n=6 |ψ|：(3.12±2.04)×10⁻² | 主要发现 1 
| 反问题 | 反 Burgers 粘度误差无噪 (6.04±4.11)×10⁻³（PINN (2.60±1.96)×10⁻²）；反 Euler k̂ = 0.9996±0.0010、ρ 误差 (1.35±0.47)×10⁻³ | 主要发现 3 
| 机制证据 | Fock 图谱：主导光子波数 |k| ≈ 4.48（训练全程无谱标签，对齐 PDE 自然模方向）、最大耦合 7.10；消融 frozen-random 使耦合场误差 1.95%→3.90%、frozen-shuffled →3.47% | 主要发现 5/6 
| 噪声鲁棒 | 严重复合扰动（η=0.90, V=0.90, N=10³）：PI-HPQNN 0.2741 vs HQNN 0.3794（干净设定 HQNN 更优 0.0169 vs 0.0281，联合扰动下排序反转） | 主要发现 7 
| 范例式生成（Approach 2）有效率 | 70%（无需人工调试） | [[2608.16422]] |
| 仅提示式生成有效率 | 55% | [[2608.16422]] |
| 模板式生成（Approach 1）有效率 | 40% | [[2608.16422]] |
<!-- src:2024-2402_18830-training-set-free-two-stage-deep-learning-for-spectros -->
<!-- src:2026-2606_18713-trainable-photonic-measurement-for-physics-informed-pd -->
<!-- src:2025-2608_16422-coherent-phonon-control-beyond-amplitude-saturation-in -->

## 适用边界

其优势边界恰恰在系统模型不精确或缺失时仍可用，但前提是目标量可重复实验测量且反馈回路稳定；由于每轮迭代均为真实实验、且所得最优解往往是"黑箱"波形，实验成本与噪声敏感度高于基于模型的优化，物理解释性有限。

## 代表作

- arXiv:0912.5121
- arXiv:2205.12110

## 证据日志

- 2026-10-17｜r76｜仅简报｜[paper:2010-0912.5121-control-of-quantum-phenomena-past-present-and-future] 闭环学习控制（closed-loop learning control）：'教会激光器'式实验反馈优化范式，不依赖精确模型即可逼近最优波形，是本文总结的最具实用价值的方法。
- 2026-10-17｜r76｜仅简报｜[paper:2022-2205.12110-quantum-optimal-control-in-quantum-technologies-strategic-re] 闭环学习控制：以实验测量反馈迭代优化波形，可在哈密顿量建模不准时仍逼近最优，源自飞秒化学脉冲整形传统。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

_暂无关联概念_
<!-- /linsai-wikilinks -->
