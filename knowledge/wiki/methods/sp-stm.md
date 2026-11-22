---
title: "自旋极化扫描隧道显微镜（SP-STM）准粒子干涉成像"
type: "methods"
created: "2026-10-11T06:41:42Z"
updated: "2026-11-01T04:55:12Z"
tags: ["方法学", "#type/method"]
related: ["1406.5137", "2107.05014", "2510.00605", "arXivID", "拓扑绝缘体", "量子几何", "量子几何张量", "量子度规"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-11T06:41:42Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

自旋极化扫描隧道显微镜（SP-STM）准粒子干涉成像以磁化针尖实现自旋分辨的局域态密度（LDOS）成像，通过读取实空间LDOS振荡（Friedel振荡）的几何振幅，将其转换为动量空间的量子几何信息（如量子度规），是拓扑绝缘体等体系全量子几何张量测量的核心实验载体与探测手段。

## 参数表

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 价带偏移 VBO（实验） | 0.83 eV | 主要发现与核心结论 
| 导带偏移 CBO（实验） | 0.76 eV | 主要发现与核心结论 
| VBO（DFT 计算） | 0.94 eV | 主要发现与核心结论 
| 能带模型 | Bistritzer-MacDonald 连续模型：v_F=2.34a eV、w₀/w₁=0.78、θ_mag≈1.12°；8 轨道 Wannier 拟合（跃迁截断 10 个莫尔晶格常数半径）；位置算符对角近似；未掺杂（化学势随温度设置）；两谷假设去耦（各谷满足 C₃/C₂T/镜面 M） | 研究方法·能带模型 
| 激光与数值 | E₀=1×10⁵ V/m；ω=1 meV（微波段，光子能量<平带带宽排除上导带跃迁）；高斯包络 FWHM 23.5 ps；100×100 Monkhorst-Pack k 网格；时间步长 2.41 fs；T₂=1000 fs≈Ω/4（已验证不影响结论）；扫描：转角 1.00–1.35°、温度 20–300 K、Γ-M 与 Γ-K 两方向 | 研究方法·时间演化与 HHG 计算/合并页 Methods 
| 核心结果 | 魔角处 H3/H5/H7 降数个量级（两方向一致）；1.06° vs 1.12° 产额差数个量级；<100 K 凹陷集中于 1.12°、高温后消失偏移；偶次谐波两谷相消 | 主要发现1-2/4/6 
| THz峰值电场 | 约 500 kV/cm | 2510.00605 
| THz光斑尺寸 | 约 380 μm (FWHM) | 2510.00605 
| THz产生方案 | 800 nm 抽运 + 1.3 μm 光在 DSTMS 晶体中差频产生宽带 THz | 2510.00605 
| 探测光/信号波长 | 800 nm 探测，400 nm SHG（PMT+lock-in 检测） | 2510.00605 
<!-- src:1406.5137 -->
<!-- src:2024-2302_04127-high-harmonic-generation-with-a-twist-all-optical-char -->
<!-- src:2107.05014 -->

## 适用边界

依赖磁化针尖提供稳定自旋极化、且样品表面存在可成像的准粒子干涉（LDOS/Friedel振荡）；实空间到动量空间几何信息的转换建立在干涉图谱的映射近似之上，需低温超高真空与原子级洁净表面，自旋分辨逐点采集耗时长、成本高。

## 代表作

- arXiv:2501.13588
- paper:2025-2501.13588-stm-based-full-qgt-measurement-topological-insulator
- paper:2025-2501.13588-spin-polarized-scanning-tunneling-microscopy-measurement-sch

## 证据日志

- 2026-10-11｜r71｜仅简报｜[paper:2025-2501.13588-stm-based-full-qgt-measurement-topological-insulator] 自旋极化扫描隧道显微镜（SP-STM）准粒子干涉成像：将实空间LDOS振荡的自旋分辨成像转换为动量空间的量子几何信息，是本方案的核心实验载体。
- 2026-10-11｜r71｜仅简报｜[paper:2025-2501.13588-spin-polarized-scanning-tunneling-microscopy-measurement-sch] 自旋极化扫描隧道显微（SP-STM）：以磁化针尖实现自旋分辨的局域态密度成像，是读取Friedel振荡几何振幅的核心探测手段。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[1406.5137]]
- [[2107.05014]]
- [[2510.00605]]
- [[arXivID]]
- [[拓扑绝缘体]]
- [[量子几何]]
- [[量子几何张量]]
- [[量子度规]]
<!-- /linsai-wikilinks -->
