---
title: "PSIS-LOO（Pareto 平滑重要性抽样留一交叉验证）"
type: "methods"
created: "2026-10-18T03:25:55Z"
updated: "2026-10-25T18:56:35Z"
tags: ["方法学", "#type/method"]
related: ["2402.08151", "Perturbative adaptive importance sampling for Bayesian LOO cross-validation"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-18T03:25:55Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

PSIS-LOO 用 Pareto 平滑重要性抽样从单次后验拟合中估计留一交叉验证得分，并以 k-hat（Pareto-k）诊断重要性权重尾部；吸收新证据：其在弱先验与层次（部分池化）数据下重要性比呈重尾，k-hat 超阈即估计失效、需对相应观测重拟合。

## 参数表

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 动力学反应模型 | η_true = [k1,k2,k3,k4] = [1.5, 0.5, 1, 0.1]（10 时间点）；vs Nelder-Mead 平均改进 370 倍；β vs PINN 提升 3.8 倍；µ_ODE 提升 88 倍；DE 收敛指数 a = 1.5255±0.0009 | 主要发现（动力学反应模型） 
| FitzHugh-Nagumo | η_true = [0.7, 0.8, 12.5]（仅 7 数据点稀疏挑战）；γ_rel 改进 4.7 倍；β 改进 3.5 倍；ξ=500% 时 NM 失败 PINNverse 胜出 221 倍 | 主要发现（FitzHugh-Nagumo） 
| Fisher-KPP | η_true = [0.5, 1]（18 时空扰动点）；γ_rel 平均改进 12 倍；β 平均改进 48 倍；PINN 特有失效——NN 解过拟合噪声且数值正演不能复现数据 | 主要发现（Fisher-KPP） 
| Burgers（激波区） | ν_true = 0.01；β 改进 33 倍（vs PINN）、2 倍（vs NM）；PINNverse 噪声下仍准确捕捉激波 | 主要发现（Burgers） 
| 训练配置 | ODE 500,000 epochs、Fisher-KPP 300,000、Burgers 150,000；噪声 ζ 与初始偏差 ξ 双维扫描（10%–500%）；Burgers 用 Fourier 特征映射；与 PINN 完全相同架构/优化器（Adan）/调度/初始化 | 研究方法（实验设计） 
<!-- src:2025-2504_05248-pinnverse-accurate-parameter-estimation-in-differentia -->

## 适用边界

近似有效的前提是重要性权重尾部受控：弱先验或层次数据会使重要性比呈重尾，Pareto-k（k-hat）超阈时 PSIS-LOO 失效，须对超标观测重拟合，带来额外计算成本。

## 代表作

- arXiv:2402.08151
- arXiv:2607.18836

## 证据日志

- 2026-10-18｜r82｜仅简报｜[paper:2024-2402.08151-perturbative-adaptive-importance-sampling-for-bayesian-loo-c] PSIS-LOO（Pareto 平滑重要性抽样留一交叉验证）：作为被改进的基线，暴露出其在弱先验下重要性权重重尾、k-hat 超标需重拟合的失效模式。
- 2026-10-18｜r82｜仅简报｜[paper:2026-2607.18836-partial-pooling-predicts-cross-validation-reliability-a-clos] PSIS-LOO（Pareto 平滑重要性采样留一交叉验证）：被诊断对象：层次数据下其重要性比呈重尾，Pareto-k 超阈即失效。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2402.08151]]
- [[Perturbative adaptive importance sampling for Bayesian LOO cross-validation]]
<!-- /linsai-wikilinks -->
