---
title: "时间/角度分辨光电子能谱（trARPES）"
type: "methods"
created: "2026-10-30T23:24:31Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "#type/method"]
related: ["1310.7563", "2026-2605_03663-enhanced-valley-polarization-via-nonlinear-cascade", "2026-2610.17984-direct-view-of-exciton-and-carrier-dynamics-in-twisted-bilay", "2302.00604", "Floquet边带", "arXivID", "arpes", "时间分辨ARPES"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-30T23:24:31Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

以泵浦-探测光电子发射在角度（动量）分辨的能带测量上叠加飞秒时间维度，直接成像泵浦诱导的能带重整化、Floquet边带与动态能隙及其超快时间演化，并可实现层分辨，直接区分不同层（如扭转双层石墨烯两层）的载流子布居与激子谱特征动力学。

## 参数表

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 泵浦 | 515 nm；通量 1.5–2.5 mJ/cm² | §泵浦条件 
| 电声耦合 | dE_g/dL=1.1 eV/nm；dE_c/dL=0.2 eV/nm | §第一性原理计算 
| trARPES 对照 | K 点电子 0.6 ps；空穴双指数快 ~2 ps/慢 >5 ps | §互补表征 
| 泵浦 | IR 1.2 eV/135 fs/2.7 mJ/cm²；LCP/RCP | §研究方法 
| XUV 探针 | 21.6 eV（H9）；65° 入射/Γ-M | §研究方法 
| 泵浦 | MIR 4–17 µm 可调，~1 μJ/脉冲，250 fs FWHM，45° 斜入射，光斑 300 μm；表面场 E₀=2.5±1×10⁷ V/m（Fresnel 校正） | 研究方法·泵浦-探测构型 
| MIR 光子能量 | ℏω=120 meV（低于 Bi₂Se₃ 体带隙 <300 meV，仅表面 Dirac 电子耦合） | 研究方法·泵浦-探测构型 
| 动态能隙（线偏） | k_y 方向 0.1 eV 与 0.22 eV 处 kink，2Δ=62 meV；anti-crossing k≈±0.03 Å⁻¹（理论 ω/2v=0.02 Å⁻¹，偏差归因 Dirac 点以下速度减小） | 主要发现·关键结果 2 
| Dirac 点能隙（圆偏） | 2κ=53 meV（全方向 anti-crossing，与 Haldane 模型一致）；n=+1/−1 间能隙 ~26 meV 接近装置分辨率 20 meV 未可靠分辨 | 主要发现·关键结果 3 
| 差分谱系数 | 线性 α=0.25、圆偏 α=0.37（I(0)−α·I(−500 fs)） | 研究方法·数据处理方法 
<!-- src:2025-2502_11452-photoinduced-twist-and-untwist-of-moiré-superlattices- -->
<!-- src:2026-2605_03663-enhanced-valley-polarization-via-nonlinear-cascade -->
<!-- src:1310.7563 -->

## 适用边界

属表面敏感的泵浦-探测技术，依赖超高真空、仅探测近表面电子结构，激子须经其对谱函数的特征间接表征；时间与能量分辨率受空间电荷效应及激光重复频率的权衡制约。

## 代表作

- paper:2026-2610.17984-direct-view-of-exciton-and-carrier-dynamics-in-twisted-bilay
- paper:2023-2302.00604-pseudospin-selective-floquet-band-engineering-in-black-phosp

## 证据日志

- 2026-10-30｜r102｜仅简报｜[paper:2026-2610.17984-direct-view-of-exciton-and-carrier-dynamics-in-twisted-bilay] 时间/角度分辨光电子能谱（trARPES）：提供层分辨、动量分辨的载流子布居与激子谱特征的飞秒时间演化，直接区分两层石墨烯的动力学。
- 2026-10-30｜r102｜仅简报｜[paper:2023-2302.00604-pseudospin-selective-floquet-band-engineering-in-black-phosp] 时间分辨ARPES（trARPES）：直接成像泵浦诱导的能带重整化、Floquet边带与动态能隙及其超快时间演化

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[1310.7563]]
- [[2026-2605_03663-enhanced-valley-polarization-via-nonlinear-cascade]]
- [[2026-2610.17984-direct-view-of-exciton-and-carrier-dynamics-in-twisted-bilay]]
- [[2302.00604]]
- [[Floquet边带]]
- [[arXivID]]
- [[arpes]]
- [[时间分辨ARPES]]
<!-- /linsai-wikilinks -->
