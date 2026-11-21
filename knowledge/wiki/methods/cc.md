---
title: "渐近库仑相/连续态-连续态（cc）延迟解析近似"
type: "methods"
created: "2026-10-24T10:45:59Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "#type/method"]
related: ["2024-2407_14160-angular-momentum-dependence-in-multiphoton-ionization-and-at", "2407.14160", "2610.15251", "arXivID"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.6
updated_at: "2026-10-24T10:45:59Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

RABITT 边带延迟可分解为内禀 Wigner 延迟加红外缀饰场与剩余长程库仑势共同产生的普适连续态-连续态延迟（τR ≈ τW + τcc）；吸收新证据后：仅由库仑相 σ_l 的能量导数即可按分波（角向）分别构造 cc/IR 修正，该几何相位项的角依赖可解析处理，从而在比传统高能极限更低、更宽的能量范围重现分波延迟差，并与二阶微扰 ab initio（分子 above-threshold R-matrix、RMT）及双谐波 RABITT 实验相符。

## 参数表

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| warping 耦合 λ | 0–1（λ=0 各向同性 Dirac 锥，λ=1 最近邻紧束缚真实石墨烯） | [[2610.15251]] |
| EFT 展开参数 x=λa_cc·A_0 | H4 一阶描述有效至 x≈0.5 | [[2610.15251]] |
| H4 验证场强上限 | ≤10¹¹ W/cm² | [[2610.15251]] |
| H4 谷对比解释精度 | 真实石墨烯能谷对比 10% 以内 | [[2610.15251]] |
| H5 对高阶晶格项敏感起始场强 | 10¹⁰ W/cm² | [[2610.15251]] |
| 驱动场构型 | ω-2ω 反向旋转圆极化场 | [[2610.15251]] |
| DFT 设置 | ELK LAPW；PBE-GGA；U=4.0/J=0.97 eV（FLL）；26×26×16；a=4.134 Å、c=6.652 Å；±4.447 µB | §电子基态 
| 脉冲参数 | τ_FWHM=40 fs；Γ=100 meV；ρ_E=4 mJ/cm²；RPA 32×32×20/0.003 Ha | §介电函数与脉冲参数 
| 材料与样品 | bulk BP：直接带隙 0.3 eV（Z 点）、D₂h 点群；Scotch-tape 剥离约 30 nm 薄层于熔融石英（薄于波长、忽略传播效应）；氮气手套箱制备保存 | 研究方法·材料体系/样品制备 
| MIR 驱动 | 4.8 µm（0.26 eV，覆盖 0.3 eV 带隙共振）；60 fs；0.05–0.37 TW/cm²；焦斑 60 µm FWHM；OPA+AgGaSe₂ 差频产生（Ti:sa 35 fs/7 mJ/800 nm/1 kHz 泵浦） | 研究方法·实验技术 
<!-- src:2610.15251 -->
<!-- src:2026-2505_13415-optical-signatures-of-bulk-g-wave-altermagnetism-in-mn -->
<!-- src:2020-2006_09376-visualization-of-two-dimensional-transition-dipole-mom -->

## 适用边界

传统普适 τcc（以及 τcoupl、τdLC 等附加项）仅在光电子与剩余离子弱相互作用的高动能极限下严格定义，低能区电子关联使各渐近贡献相互纠缠而失效；新的分波-库仑相 σ_l 能量导数近似将适用下限扩展至更低能量（对弱关联分子成立）并给出明确失效条件，但仍需注意低能/低强下分子电子态密集造成的谱拥挤，需双谐波配置分离高阶多光子通道。

## 代表作

- arXiv:2407.14160
- arXiv:2005.12654

## 证据日志

- 2026-10-24｜r91｜回原文｜[paper:2024-2407.14160-angular-momentum-dependence-in-multiphoton-ionization-and-at] 渐近库仑相/连续态-连续态（cc）延迟解析近似：证明仅由库仑相 σ_l 的能量导数即可在更宽（更低）能量范围重现分波延迟差，扩展了该近似的适用下限并给出失效条件。
- 2026-10-24｜r91｜仅简报｜[paper:2020-2005.12654-angle-resolved-time-delays-for-shake-up-ionization-of-helium] 连续态-连续态（cc）延迟/长程库仑修正：分离 IR 与剩余库仑势作用产生的普适几何相位项，确认其角依赖可解析处理。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2024-2407_14160-angular-momentum-dependence-in-multiphoton-ionization-and-at]]
- [[2407.14160]]
- [[2610.15251]]
- [[arXivID]]
<!-- /linsai-wikilinks -->
