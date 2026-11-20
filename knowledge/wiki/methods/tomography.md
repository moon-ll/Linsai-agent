---
title: "平衡零差层析（homodyne tomography）"
type: "methods"
created: "2026-10-02T23:21:14Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "#type/method"]
related: ["1805.03806", "arXivID"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-02T23:21:14Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

平衡零差层析通过扫描本底振荡（LO）相位测得各相位下正交分量的边缘分布，再经反演重构 Wigner 函数/密度矩阵，常作为与外差层析逐点对比的基准方案；但新证据表明该重构流程脆弱——即使对不含非经典性的经典模型数据，也可能反演出带 Wigner 负值的密度矩阵。

## 参数表

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 发表 | Shen, Zhou, Wang & Wang (2026), arXiv:2609.28680 | 标题行 |
| 1D 模型参数 | 周期边界直接带隙半导体：软化参数 s = 25 a.u.、介电常数 ε = 5 a.u.、杂质电离势 E_g − ε₀ = 106.4 meV；激光 F₀ = 10⁻⁴ a.u.（I₀ = 3.5×10⁸ W/cm²）、λ₀ = 50 µm、12 cycle 高斯包络；相干时间 T₂ = 50 fs | 研究方法（数值实现） 
| 谱特征 | 谐波强度 |j̃|² 与偶极矩 |d₀(ω)|² 形态高度吻合；双轨迹结构（短轨迹主导、长轨迹集中于高次谐波高端）；强度在 ~71 次谐波附近截止（与 d₀(ω)² 衰减一致） | 主要发现 
| 截止律 | E_cut = Ip + 3.17 Up，其中 Up ∝ I ∝ E²drive——cutoff 对驱动场振幅涨落呈平方放大 | 核心要点 
| 超快 TEM | PHAROS→SHG 514 nm/2.4 eV/25 kHz/0.33 mJ/cm²；光斑 160 µm；总时间分辨 4 ps（最佳 750 fs） | §研究方法 
| 驱动 | 2.1 µm / 27 fs / 10 kHz / 28 W；He 靶 ~2.2 bar | §HHG 源参数 
| 通量标定 | O 边 ~532 eV 处 ≈5×10⁵ ph/eV/s（PTB 绝对标定） | §HHG 源参数 
| 样品 | Al₂O₃ ~70 nm（ALD 225 °C 500 cycles）+ 埋藏 Pt ~20 nm（溅射 2×10⁻¹ mbar/0.14 nm/s） | §样品体系 
<!-- src:2026-2609_28680-altermagnetic-kondo-logic-via-floquet-symmetry-convers -->
<!-- src:1805.03806 -->
<!-- src:2026-2605_21925-nonclassical-cutoff-fluctuations-in-squeezed-light-dri -->
<!-- src:2026-2601_13620-photo-and-thermally-induced-huge-layer-decoupling-in-t -->
<!-- src:2025-2503_04276-soft-x-ray-imaging-with-coherence-tomography-in-the-wa -->

## 适用边界

在有限相位采样与反演流程下，Wigner 负值并非非经典性的可靠判据（经典模型数据经同一层析流程仍可产生虚假负值），且需逐相位扫描 LO，测量成本随重构维度增长。

## 代表作

- arXiv:2512.17031
- arXiv:2512.13462

## 证据日志

- 2026-10-02｜r48｜仅简报｜[paper:2025-2512.17031-comparing-homodyne-and-heterodyne-tomography-of-quantum-stat] 平衡零差层析（homodyne tomography）：作为基准方案，通过 LO 相位扫描测正交分量边缘分布重构 Wigner 函数，用于逐点对比外差性能。
- 2026-10-02｜r48｜仅简报｜[paper:2025-2512.13462-wigner-function-negativity-in-a-classical-model-of-quantum-l] 平衡零差层析：本文用它对经典模型数据执行与实验相同的态重构，反演出带Wigner负值的密度矩阵，暴露层析流程的脆弱点。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[1805.03806]]
- [[arXivID]]
<!-- /linsai-wikilinks -->
