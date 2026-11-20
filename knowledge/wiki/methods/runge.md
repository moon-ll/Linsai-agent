---
title: "离散时间 Runge-Kutta 神经网络步进器"
type: "methods"
created: "2026-10-31T20:02:01Z"
updated: "2026-11-01T04:55:12Z"
tags: ["方法学", "#type/method"]
related: ["2026-2607_16477-measuring-the-dipole-phase-of-bloch-trajectory-har", "2411.02379", "arXivID"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-31T20:02:01Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

以 q 级隐式 Runge-Kutta 格式将时间演化离散化并作为神经网络的时间演化约束，使仅凭相隔大 Δt 的两个时刻快照对即可做大时间步长外推求解（Part I 数据驱动求解），并可在同一框架下发现动力学方程（Part II 数据驱动发现）。

## 参数表

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 激光系统 | ELI-ALPS 中红外：λ1 = 3.2 µm；42 fs 经 BaF2/Si 自相位调制展宽 + CaF2/BaF2 啁啾补偿压缩至 24 fs；焦斑 ~100 µm（M² = 1.6）；脉冲能量 ~10 µJ；峰值强度 ~6 TW/cm² | 研究方法·激光系统 / 深度解析 
| 样品 | 蓝宝石 500 µm 两侧 ALD ZnO 各 47 nm（实测）/50 nm（设计）；谐波吸收长度（λ<380 nm）约 40 nm 与膜厚相当——膜内传播可忽略；双面样品产生至 H13 | 研究方法 / 深度解析 
| 偶极相位斜率 | 实验拟合 η ≈ 3 rad·cm²/TW（n2 = 2×10⁻²⁰ m²/W 时计算低估斜率约 15%）；半经典模型 Bloch 轨迹在 4 TW/cm² 附近给出 ~3.5 rad·cm²/TW——高度一致 | 主要发现与核心结论 
| Bloch 轨迹判据 | H9 能量 3.6 eV 仅比禁带 3.2 eV 高 0.4 eV（复合能极低）：短轨迹激发幅值低、长轨迹被超快退相干压制，均不能重现斜率；Bloch 轨迹（−0.1T 激发、0.1T 复合、能带边缘反向、位置空间反向而晶体动量不反向）幅值大、渡越时间短——主导机制 | 主要发现与核心结论 
| 前/背不对称 | 背侧 ZnO-真空界面相长干涉场增强、前侧空气界面相消——后表面信号更强；Hn≥7 蓝移（群速度低于基频、下降沿 XPM）、H5 红移（上升沿） | 主要发现与核心结论 
| 模拟设置 | FME 移动参考帧四阶 Runge-Kutta；唯象发射 Eq = |E_local|N_eff exp(i(qφ − φ_HHG))，有效非线性 N_eff = 2.5 单一经验值拟合所有谐波阶；正弦能带近似（禁带 3.2 eV、带宽 5.0 eV） | 研究方法·脉冲传播模拟 
| 质量场带隙 Δ（h-BN 封装石墨烯） | 40 meV | [[2411.02379]] |
| 退相干时间 T_D | 20 fs | [[2411.02379]] |
| 脉冲宽度 | 5–30 fs（亚 cycle 至 few cycle） | [[2411.02379]] |
| 脉冲振幅 A₀ | 0.01–0.1 a.u.（10¹⁰–10¹¹ W/cm²） | [[2411.02379]] |
<!-- src:2026-2607_16477-measuring-the-dipole-phase-of-bloch-trajectory-har -->
<!-- src:2411.02379 -->

## 适用边界

适用于数据稀疏、仅在离散未来时刻可观测且动力学可被隐式 RK 大步长离散良好近似的演化问题；中间时刻状态不受直接约束，且 q 级隐式格式需逐级网络求值，计算与训练成本随级数上升，精度依赖 RK 离散的有效性。

## 代表作

- arXiv:1711.10561
- arXiv:1711.10566

## 证据日志

- 2026-10-31｜r108｜仅简报｜[paper:2017-1711.10566-physics-informed-deep-learning-part-ii-data-driven-discovery] 离散时间 Runge-Kutta 神经网络步进器：用 q 级隐式RK格式作为时间演化约束，使仅凭相隔大 Δt 的快照对即可发现动力学方程。
- 2026-10-31｜r108｜仅简报｜[paper:2017-1711.10561-physics-informed-deep-learning-part-i-data-driven-solutions] 离散时间PINN（Runge-Kutta格式）：用q阶隐式Runge-Kutta把时间演化离散化，只需两个时刻的快照数据即可做大时间步长外推，适合数据稀疏且只在未来时刻可观测的演化问题。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2026-2607_16477-measuring-the-dipole-phase-of-bloch-trajectory-har]]
- [[2411.02379]]
- [[arXivID]]
<!-- /linsai-wikilinks -->
