---
title: "dmft"
type: "methods"
created: "2026-09-25T19:44:29Z"
updated: "2026-11-21T11:18:41Z"
tags: ["方法学", "#type/method"]
related: ["2410.01424", "Mott转变", "强关联体系", "精确对角化", "非线性光学"]
source_raw: ""
growth_stage: "mature"
confidence: 0.8
updated_at: "2026-11-21T07:35:37Z"
settled_count: 5
aliases: ["DMFT", "dynamical mean-field theory", "dynamical mean field theory", "动力学平均场"]
---

<!-- methods-settle:v1 -->

## 原理

DMFT 将晶格强关联电子模型以局域自能自洽映射为 Anderson 杂质模型（量子杂质问题），是揭示单轨道 Hubbard 模型中隐藏 Kondo 晶格结构的核心工具，既可在模型层面解析 U 驱动的金属–绝缘体相变与轨道选择性 Mott 转变全相图，也可经非平衡/含时扩展计算 Mott 体系强场非线性光学响应（AFM 绝缘相谐波由自旋-电荷/轨道-电荷耦合主导、金属相来自重整化带内电流等相区依赖机制仍然成立）；结合 cRPA 的 DFT+DMFT 可从第一性原理建立晶格畸变与关联的定量联系（如单层 1T-TaS2 的 CDW 振幅调制有效 U 驱动 Mott–金属转变）；新证据进一步表明，对单带 Hubbard 模型的非平衡多体演化可定性再现准一维与准二维关联绝缘体高次谐波生成的维度依赖差异：一维体系中自旋-电荷分离使电荷动力学受自旋背景约束较弱，HHG 非线性更强（出现跨能隙的类气体平台结构）且对热涨落稳健，二维体系则谐波产额随阶数单调衰减且被温度强抑制，说明自旋-电荷耦合的维度敏感性可在强驱动体系中被 HHG 直接探测。

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
| SrCuO2 电荷转移能隙 | 1.4 eV | paper:2026-2609.02466-prominent-dimensional-effects-on-high-order-harmon |
| SrCuO2 自旋链交换常数 J | 约 0.2 eV | paper:2026-2609.02466-prominent-dimensional-effects-on-high-order-harmon |
| Pr2CuO4 光学能隙 | 1.2 eV | paper:2026-2609.02466-prominent-dimensional-effects-on-high-order-harmon |

## 适用边界

沿用局域（动量无关）自能近似，不含非局域关联与空间涨落（含 U 驱动相图、轨道选择性 Mott 转变与隐藏 Kondo 晶格结构的解析均在此框架内）；第一性原理应用（DFT+DMFT+cRPA）依赖窄半满带（meV 带宽）的 Wannier 降维建模，大超胞内屏蔽库仑相互作用的定量评估困难；THz 谐波建模限于光子能量远低于 Mott 能隙的强关联体系，谐波强度随阶数衰减，需 ~100 阶才能匹配 Mott 能隙尺度的响应实际不可探测；新增维度效应研究表明，一维自旋-电荷分离物理本质上是局域自能近似（及单杂质映射）难以完全刻画的非局域/维度敏感现象，相关 HHG 维度依赖分析需借助非平衡多体演化（DMFT 类/精确对角化）并在一维链与二维方格上分别模拟，且实验 HHG 需在强场非微扰区（>0.4 TW/cm2）以反射几何抑制非线性传播效应方可解读为本征响应。

## 代表作

- arXiv:2410.01424
- arXiv:2510.26584
- arXiv:2410.14583
- arXiv:2609.02466

## 证据日志

- 2026-09-25｜r33｜回原文｜[paper:2024-2410.01424-terahertz-harmonic-generation-across-the-mott-insulator-meta] 非平衡 DMFT / 含时 Gutzwiller 类理论建模：从强关联模型层面确认自旋-电荷与轨道-电荷耦合对三阶非线性（THG 增强）的贡献机制。
- 2026-09-26｜r38｜回原文｜[paper:2025-2510.26584-dynamical-control-of-coulomb-interactions-and-hubbard-bands] DFT+DMFT：获得不同CDW振幅下的谱函数与上下Hubbard带演化，定位Mott-金属相变边界（3%阈值）。
- 2026-10-03｜r52｜仅简报｜[paper:2024-2410.14583-hidden-kondo-lattice-physics-in-single-orbital-hubbard-model] DMFT（动力学平均场理论）：以局域自能自洽映射到杂质模型，解析U驱动的轨道选择性Mott转变与金属-绝缘体相变的全相图。
- 2026-11-01｜r111｜仅简报｜[paper:2024-2410.14583-hidden-kondo-lattice-physics-in-single-orbital-hubbard-model] 动力学平均场理论 (DMFT)：把单带 Hubbard 模型自洽映射为 Anderson 杂质模型，是揭示隐藏 Kondo 晶格结构的核心工具。
- 2026-11-21｜r1｜回原文｜[paper:2026-2609.02466-prominent-dimensional-effects-on-high-order-harmon] 强关联多体模型非平衡演化（DMFT类/精确对角化）：提供维度依赖的关联谱与谐波响应的直接联系

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2410.01424]]
- [[Mott转变]]
- [[强关联体系]]
- [[精确对角化]]
- [[非线性光学]]
<!-- /linsai-wikilinks -->
