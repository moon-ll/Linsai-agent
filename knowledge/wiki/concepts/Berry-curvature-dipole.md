---
title: "Berry curvature dipole"
type: "concepts"
created: "2026-10-25T18:05:11Z"
updated: "2026-11-15T15:09:18Z"
tags: ["concept", "backfill"]
related: ["2025-2505_16999-nonlinear-thermal-and-thermoelectric-transpo", "2026-260929226-valley-berry-curvature-dipole-induced-nonline", "2505.16999", "Berry curvature", "Berry 曲率", "半经典输运理论", "反常速度", "反常霍尔效应", "谷极化", "谷电子学", "非线性热电输运", "非线性霍尔效应"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
aliases: ["Berry curvature dipole"]
---

# Berry curvature dipole（贝里曲率偶极子）

## 定义定位

Berry curvature dipole（BCD，贝里曲率偶极子）是动量空间中贝里曲率分布的一阶不对称矩，由 Sodemann 与 Fu 于 2015 年提出，用于描述**时间反演对称但反演对称破缺**晶体中贝里曲率的“隐藏不对称性”。其数学定义为费米分布加权下贝里曲率（作为赝矢量 $\Omega_b = \frac{1}{2}\epsilon_{bac}\Omega_{ac}$）与群速度 $v_a$ 在布里渊区上的积分：$D_{ab} = -\int \frac{d\mathbf{k}}{(2\pi)^d} \frac{\partial f_0}{\partial \varepsilon}\, v_a(\mathbf{k})\, \Omega_b(\mathbf{k})$。虽然此类体系中贝里曲率在全布里渊区的积分（陈数类量）为零，但其局域分布可非零且在动量空间中分布不对称，BCD 正是量化这一不对称的内禀几何量，也是无磁场下二阶霍尔响应的核心来源。

## 物理内涵/技术原理

**对称性约束**：贝里曲率 $\Omega$ 是轴矢量（时间反演下奇、空间反演下偶），速度 $v$ 是极矢量（反演下奇），二者乘积构成的 BCD 是二阶赝张量。因此：(1) 反演对称存在时 BCD 严格为零，即反演破缺是其存在的必要条件；(2) 时间反演对称可以保留，这正是 BCD 区别于反常霍尔效应的关键。具体非零分量由点群对称性决定：二维体系中倾斜的 gapped Dirac 锥（如应变石墨烯、gapped honeycomb 体系）、倾斜 Weyl 锥等是产生大 BCD 的典型能带结构。

**输运机制**：在含 Berry 相修正与波包轨道磁矩的半经典玻尔兹曼方程框架下，电场不仅产生反常速度 $-\frac{e}{\hbar}\mathbf{E}\times\mathbf{\Omega}$，还通过相空间修正使分布函数产生正比于 $\mathbf{E}\cdot\mathbf{v}$ 的非平衡项。二阶展开后，贝里曲率对非平衡分布加权求和即产生横向二阶电流：$j_a^{(2)} = \frac{e^3\tau}{2(1+i\omega\tau)\hbar}\, \epsilon_{abc}\, E_b D_{cd} E_d$，表现为量子非线性霍尔效应（二次谐波横向电压），且该响应本质上是内禀的（仅弱依赖于弛豫时间 $\tau$ 的线性因子，不受杂质斜散射主导）。

**拓展方向**：(1) **非线性热/热电输运**——BCD 同样进入对温度梯度 $\nabla T$ 的二阶响应（非线性 Nernst、非线性热导），构成无量纲热输运系数中的几何项，对应样本 [[2025-2505_16999-nonlinear-thermal-and-thermoelectric-transpo]] 的核心框架；(2) **谷分辨 BCD**——在 2H 过渡金属硫族化合物等 valley 体系中，不同谷的贝里曲率矩符号相反，谷极化或层极化可使谷分辨 BCD 主导非线性响应，对应样本 [[2026-260929226-valley-berry-curvature-dipole-induced-nonline]]；(3) 作为纯费米面量，BCD 可通过栅压、能带倾斜与层间滑移（如 WTe₂）高效调控。

## 与现有方法/概念的关联

- **[[Berry curvature]]**：BCD 是贝里曲率在费米面附近的一阶矩，是贝里曲率“总积分为零但局域非零”这一情形下的下一阶可观测修正；
- **[[非线性霍尔效应]]**：BCD 是时间反演对称体系中量子非线性霍尔效应的主导内禀机制；
- **[[反常霍尔效应]]**：线性对应物，需要磁有序或时间反演破缺；BCD 将横向霍尔响应推广到非磁性、反演破缺体系；
- **[[半经典输运理论]]**：BCD 的输运表现完全在含 Berry 曲率修正的波包动力学框架内导出；
- **[[谷电子学]]** 与 [[非线性热电输运]]：谷分辨 BCD 与 BCD 型非线性热响应是本项目两篇样本论文的直接主题延伸。

## 林赛理解

在本项目的非线性输运理论研究中，BCD 扮演“几何引擎”的角色：它把能带的贝里几何结构转化为可测量的二阶横向响应，使我们在无外磁场、无磁序的条件下也能分离出内禀输运通道。对样本论文而言，一篇（2505.16999）将 BCD 机制从电学响应推广到温度梯度驱动的非线性热电与热流响应，检验 BCD 在 Onsager 关系下的热-电对应；另一篇（2609.29226）则聚焦谷分辨层面，讨论谷/层自由度如何与 BCD 耦合产生新的非线性信号。引用频次仅 2、优先级 low，说明 BCD 在本项目中是**支撑性背景概念**而非核心研究对象——理解它的目的在于读懂非线性热输运与谷非线性两篇文献的理论骨架，并在实验解释中区分内禀几何贡献与无序散射贡献。

## 学习路径/参考

1. **奠基文献**：Sodemann & Fu, *Phys. Rev. Lett.* **115**, 216601 (2015) —— BCD 与量子非线性霍尔效应的原始提出；
2. **实验验证**：Ma et al., *Nature* **565**, 337 (2019)；Tang et al., *Phys. Rev. X* **9**, 021024 (2019) —— 少层 WTe₂ 中二阶霍尔电压的观测；
3. **项目样本**：[[2025-2505_16999-nonlinear-thermal-and-thermoelectric-transpo]]（BCD 型非线性热/热电输运）；[[2026-260929226-valley-berry-curvature-dipole-induced-nonline]]（谷 BCD 诱导的非线性响应）；
4. **背景补充**：Xiao, Chang & Nagaosa, *Rev. Mod. Phys.* **82**, 1959 (2010)（Berry 相修正的半经典动力学）；建议先掌握 [[Berry curvature]] 与 [[反常霍尔效应]]，再进入 BCD 的二阶响应推导。

<!-- linsai-wikilinks -->
## 关联概念

- [[2025-2505_16999-nonlinear-thermal-and-thermoelectric-transpo]]
- [[2026-260929226-valley-berry-curvature-dipole-induced-nonline]]
- [[2505.16999]]
- [[Berry curvature]]
- [[Berry 曲率]]
- [[半经典输运理论]]
- [[反常速度]]
- [[反常霍尔效应]]
- [[谷极化]]
- [[谷电子学]]
- [[非线性热电输运]]
- [[非线性霍尔效应]]
<!-- /linsai-wikilinks -->
