---
title: "dmft"
type: "methods"
created: "2026-09-25T19:44:29Z"
updated: "2026-11-01T06:41:19Z"
tags: ["方法学", "#type/method"]
related: ["2410.01424", "Mott转变", "强关联体系", "非线性光学"]
source_raw: ""
growth_stage: "mature"
confidence: 0.7
updated_at: "2026-11-01T06:41:19Z"
settled_count: 4
aliases: ["DMFT", "dynamical mean-field theory", "dynamical mean field theory", "动力学平均场"]
---

<!-- methods-settle:v1 -->

## 原理

DMFT 将晶格强关联电子模型以局域自能自洽映射为 Anderson 杂质模型（量子杂质问题），是揭示单轨道 Hubbard 模型中隐藏 Kondo 晶格结构的核心工具，既可在模型层面解析 U 驱动的金属–绝缘体相变与轨道选择性 Mott 转变全相图，也可经非平衡/含时扩展计算 Mott 体系 THz 非线性光学响应（AFM 绝缘相谐波由自旋-电荷/轨道-电荷耦合主导、金属相来自重整化带内电流等相区依赖机制仍然成立）；结合 cRPA 的 DFT+DMFT 可进一步从第一性原理建立晶格畸变与关联的定量联系：CDW 振幅通过改变轨道局域化与电子屏蔽调制有效 Hubbard U，使 Hubbard 带随 CDW 振幅协同移动，减小畸变可驱动 Mott 绝缘体向关联金属转变（如单层 1T-TaS2），为光控二维关联相提供微观机制。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| Mott 能隙典型尺度 | ~1 eV（数量级） | paper:2024-2410.01424-terahertz-harmonic-generation-across-the-mott-insulator-meta |
| THz 光子能量 | 数 meV（比 Mott 能隙小约三个数量级） | paper:2024-2410.01424-terahertz-harmonic-generation-across-the-mott-insulator-meta |
| THz 驱动频率（实验） | 0.3 THz | paper:2024-2410.01424-terahertz-harmonic-generation-across-the-mott-insulator-meta |
| 三次谐波频率（实验） | 0.9 THz | paper:2024-2410.01424-terahertz-harmonic-generation-across-the-mott-insulator-meta |
| 单层 1T-TaS2 平衡态有效 Hubbard U | 0.4 eV | paper:2025-2510.26584-dynamical-control-of-coulomb-interactions-and-hubbard-bands |
| CDW 振幅 1% 变化引起的屏蔽致 U 降低幅度 | 至多 0.1 eV | paper:2025-2510.26584-dynamical-control-of-coulomb-interactions-and-hubbard-bands |
| Mott 绝缘体–关联金属相变的 CDW 振幅阈值 | +3%（振幅增大） | paper:2025-2510.26584-dynamical-control-of-coulomb-interactions-and-hubbard-bands |
| 1T-TaS2 相干 CDW 振幅模式频率 | 2.4 THz | paper:2025-2510.26584-dynamical-control-of-coulomb-interactions-and-hubbard-bands |
| 费米能级半满分子轨道带宽（Ta d 3z2−r2） | meV 量级 | paper:2025-2510.26584-dynamical-control-of-coulomb-interactions-and-hubbard-bands |

## 适用边界

沿用局域（动量无关）自能近似，不含非局域关联与空间涨落（含 U 驱动相图、轨道选择性 Mott 转变与隐藏 Kondo 晶格结构的解析均在此框架内）；第一性原理应用（DFT+DMFT+cRPA）依赖窄半满带（meV 带宽）的 Wannier 降维建模，且大超胞（如 SoD 13 原子星形结构）内屏蔽库仑相互作用的定量评估困难；THz 谐波建模限于光子能量（数 meV）远低于 Mott 能隙（~1 eV）的强关联体系，谐波强度随阶数衰减，需 ~100 阶才能匹配 Mott 能隙尺度的响应实际不可探测。

## 代表作

- arXiv:2410.01424
- arXiv:2510.26584
- arXiv:2410.14583

## 证据日志

- 2026-09-25｜r33｜回原文｜[paper:2024-2410.01424-terahertz-harmonic-generation-across-the-mott-insulator-meta] 非平衡 DMFT / 含时 Gutzwiller 类理论建模：从强关联模型层面确认自旋-电荷与轨道-电荷耦合对三阶非线性（THG 增强）的贡献机制。
- 2026-09-26｜r38｜回原文｜[paper:2025-2510.26584-dynamical-control-of-coulomb-interactions-and-hubbard-bands] DFT+DMFT：获得不同CDW振幅下的谱函数与上下Hubbard带演化，定位Mott-金属相变边界（3%阈值）。
- 2026-10-03｜r52｜仅简报｜[paper:2024-2410.14583-hidden-kondo-lattice-physics-in-single-orbital-hubbard-model] DMFT（动力学平均场理论）：以局域自能自洽映射到杂质模型，解析U驱动的轨道选择性Mott转变与金属-绝缘体相变的全相图。
- 2026-11-01｜r111｜仅简报｜[paper:2024-2410.14583-hidden-kondo-lattice-physics-in-single-orbital-hubbard-model] 动力学平均场理论 (DMFT)：把单带 Hubbard 模型自洽映射为 Anderson 杂质模型，是揭示隐藏 Kondo 晶格结构的核心工具。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2410.01424]]
- [[Mott转变]]
- [[强关联体系]]
- [[非线性光学]]
<!-- /linsai-wikilinks -->
