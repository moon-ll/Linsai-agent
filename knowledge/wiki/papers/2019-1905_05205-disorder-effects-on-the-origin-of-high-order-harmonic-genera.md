---
title: "2019-1905.05205-disorder-effects-on-the-origin-of-high-order-harmonic-genera"
type: "papers"
created: "2026-11-01T16:09:56Z"
updated: "2026-11-15T15:09:25Z"
tags: []
related: ["Floquet-Keldysh-Green函数", "high-order-harmonic-generation", "固体HHG", "布洛赫电子", "高次谐波产生"]
source_raw: "2019-1905.05205-disorder-effects-on-the-origin-of-high-order-harmonic-genera.md"
growth_stage: "seedling"
confidence: 0.5
digest_level: "abstract"
---

• # Disorder Effects on the Origin of High-Order Harmonic Generation in Solids

  ## 研究问题（Research Question）

  固体[[高次谐波产生]]（[[high-order-harmonic-generation]]）的微观起源是什么？具体地，晶体周期性（布洛赫态与带间相干）在其中扮演何种角色——无序（disorder）对谐波电流的影响能否作为区分"相干机制"与"非相干机制"的判据？这是 Chen、Taucer、Yu（2019）要解决的核心问题。

  ## 研究背景（Background）

  固体 HHG 自 2010 年代初在实验上被系统观测以来，其起源存在两种竞争性图像：一是继承原子 HHG 的"非相干"图像（局域散射、含时隧穿等非周期性过程），二是依赖晶格周期性的"相干"图像（带间极化与[[布洛赫电子]]加速）。此前大量工作集中于完美晶体，无序对谐波谱的系统影响缺乏严格的多体理论处理，这正是本文切入的缺口。

  ## 研究方法（Data & Method）

  作者采用 [[Floquet-Keldysh-Green函数]] 方法，在含无序的固体模型中严格计算谐波电流。关键理论结果是：每个谐波电流分量都可分解为**相干部分**与**非相干部分**之和，两者对无序的响应行为不同，从而可以把无序强度当作"探针"来分离两种贡献。（摘要级来源，具体模型参数与无序实现方式未在 raw 笔记中给出，不虚构。）

  ## 主要发现与核心结论（Main Results & Findings）

  - 每个谐波电流分量同时含有相干与非相干两部分贡献，二者可随无序强度变化发生权重转移。
  - 随无序增强，体系发生从**相干散射主导**到**非相干散射主导**的交叉（crossover）。
  - 由此反证：在弱无序（近完美晶体）极限下，固体 HHG 主要由依赖晶体周期性的相干过程贡献，**晶体周期性是固体 HHG 起源的关键**。
  （以上均为定性结论；摘要级来源不含具体数值，不做定量转述。）

  ## 潜在研究方向（Limitations & Open Questions）

  - 无序诱导的相干→非相干交叉是否具有可观测的谱学指纹（如谐波阶次依赖的相对权重变化），可在实验上用于机制判别？
  - 本文结论与具体无序模型（对角/非对角无序、关联长度）的依赖关系值得在后续工作中推广验证。
  - 对课题的意义：为"HHG 起源判据"提供了一条理论工具链——把无序当作机制探针，可服务于本课题对 HHG 机制表述的校准；同时该方法（Floquet-Keldysh + 无序分解）可作为方案中理论支撑节的引用锚点。

  **来源**：arXiv:1905.05205（Chen, Taucer, Yu, 2019），摘要级蒸馏（digest_level=abstract），无全文定量数据。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：Floquet-Keldysh 格林函数的谐波电流相干/非相干分解（无序作为机制探针）

**原理**：在含无序固体模型中用 Floquet-Keldysh 格林函数严格计算谐波电流：每个谐波分量可分解为相干与非相干两部分，二者对无序的响应不同——随无序增强发生从相干散射主导到非相干散射主导的交叉；反证弱无序（近完美晶体）极限下固体 HHG 主要由依赖晶体周期性的相干过程贡献。

**适用边界**：摘要级定性结论（无定量数值）：无序诱导 crossover 的可观测谱学指纹（阶次依赖权重变化）待实验检验；与具体无序模型（对角/非对角、关联长度）的依赖关系待推广验证。
**代表作**：Chen, Taucer, Yu, Disorder Effects on the Origin of High-Order Harmonic Generation in Solids, arXiv:1905.05205 (2019)
*方法卡回补 2026-11-01*

<!-- linsai-wikilinks -->
## 关联概念

- [[Floquet-Keldysh-Green函数]]
- [[high-order-harmonic-generation]]
- [[固体HHG]]
- [[布洛赫电子]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
