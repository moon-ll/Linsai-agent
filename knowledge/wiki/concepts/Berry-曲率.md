---
title: "Berry 曲率"
type: "concepts"
created: "2026-10-24T06:01:49Z"
updated: "2026-11-15T15:09:18Z"
tags: ["concept", "backfill"]
related: ["arpes", "半经典运动方程", "反常速度", "反常霍尔效应", "圆二色性", "外尔半金属", "角分辨光电子能谱", "谷电子学", "贝里相位", "赝磁场", "陈数", "陈绝缘体"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
aliases: ["Berry 曲率"]
---

# Berry 曲率

## 定义定位

Berry 曲率（Berry curvature，贝里曲率）是布洛赫波函数在动量空间中随晶体动量 $\mathbf{k}$ 绝热变化时几何相位的局域密度，通常记作 $\boldsymbol{\Omega}_n(\mathbf{k})$。对第 $n$ 条能带，它定义为 Berry 联络 $\mathbf{A}_n(\mathbf{k}) = i\langle u_{n\mathbf{k}}|\nabla_{\mathbf{k}}|u_{n\mathbf{k}}\rangle$ 的旋度。直观上，它是一个分布在**动量空间**的赝磁场：电子的“回旋运动”不在实空间而在 $\mathbf{k}$ 空间发生，其几何响应由 $\boldsymbol{\Omega}$ 度量。作为连接能带波函数微观结构与宏观输运、光学及拓扑性质的核心物理量，它在反常霍尔效应、谷电子学与拓扑能带理论中处于枢纽地位。

## 物理内涵/技术原理

**数学结构**：$\boldsymbol{\Omega}_n(\mathbf{k}) = \nabla_{\mathbf{k}} \times \mathbf{A}_n(\mathbf{k})$ 本身是规范不变的（联络 $\mathbf{A}_n$ 依赖波函数规范选取，但其旋度不依赖）。在二维材料中退化为标量 $\Omega_{n,z}$；二带模型下可写成 $\Omega \propto \hat{d}\cdot(\partial_{k_x}\hat{d}\times\partial_{k_y}\hat{d})$，仅当带间杂化（$\hat{d}$ 方向缠绕）时才非零——即 Berry 曲率集中在带隙附近与简并点周围。

**半经典动力学**：修正的电子运动方程
$$\dot{\mathbf{r}} = \frac{1}{\hbar}\nabla_{\mathbf{k}}\varepsilon_n - \dot{\mathbf{k}}\times\boldsymbol{\Omega}_n, \qquad \hbar\dot{\mathbf{k}} = -e(\mathbf{E} + \dot{\mathbf{r}}\times\mathbf{B})$$
中第二项给出反常速度 $\mathbf{E}\times\boldsymbol{\Omega}/\hbar$：即使无外磁场， Berry 曲率也驱动横向电流，这是本征反常霍尔效应的来源，$\sigma_{xy} = -\frac{e^2}{\hbar}\int_{\text{BZ}}\Omega_z\, f_0\, d^3k/(2\pi)^3$。

**对称性约束**：时间反演要求 $\Omega(\mathbf{k}) = -\Omega(-\mathbf{k})$，空间反演要求 $\Omega(\mathbf{k}) = \Omega(-\mathbf{k})$；二者同时存在时净 Berry 曲率处处为零，破缺其一（如六角晶格 $K/K'$ 谷、破缺反演的异质双层）才允许局域非零 $\Omega$。

**拓扑与测量**：$\boldsymbol{\Omega}$ 在布里渊区内的通量给出陈数 $C = \frac{1}{2\pi}\int_{\text{BZ}}\Omega\, d^2k$；带简并点（如 Weyl 点）是 $\boldsymbol{\Omega}$ 的单极子源/汇。实验上除输运外，圆二色性 ARPES 可利用左右旋光在带边附近矩阵元的巨大差异，直接对 $\Omega(\mathbf{k})$ 做动量分辨成像（Science 2018, WSe₂）。

## 与现有方法/概念的关联

- 概念上游：$\boldsymbol{\Omega}$ 是 [[贝里相位]] 沿闭合回路的环路积分密度，$\gamma = \oint \mathbf{A}\cdot d\mathbf{k} = \int \Omega\, dS$。
- 输运表现：[[反常霍尔效应]]（本征项）与 [[半经典运动方程]] 中的反常速度项。
- 拓扑角色：BZ 积分给出 [[陈数]]，联系 [[陈绝缘体]] 与 [[外尔半金属]]（单极子图像）。
- 器件方向：$K/K'$ 谷相反号的 $\Omega$ 支撑 [[谷电子学]] 与谷依赖电子光学（贝里曲率透镜/分束）。
- 实验手段：[[角分辨光电子能谱]]（尤其 CD-ARPES）是动量分辨测 $\Omega$ 的直接工具。

## 林赛理解

在本项目的文献图谱中，Berry 曲率是“动量空间能带几何 ↔ 实空间输运/光学响应”的双向桥梁：三个样本恰好覆盖了它的三个面向——(i) CD-ARPES 直接测量 $\Omega(\mathbf{k})$（arXiv:1804.07565）对应“可测量的拓扑”；(ii) 谷依赖电子光学（arXiv:2607.00271）展示 $\Omega$ 驱动的反常折射与谷分束，对应“可设计的器件物理”；(iii) 动量分辨电子结构（arXiv:2511

<!-- linsai-wikilinks -->
## 关联概念

- [[arpes]]
- [[半经典运动方程]]
- [[反常速度]]
- [[反常霍尔效应]]
- [[圆二色性]]
- [[外尔半金属]]
- [[角分辨光电子能谱]]
- [[谷电子学]]
- [[贝里相位]]
- [[赝磁场]]
- [[陈数]]
- [[陈绝缘体]]
<!-- /linsai-wikilinks -->
