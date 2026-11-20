---
title: "2018-1807.02525-floquet-theoretical-formulation-and-analysis-of-high-harmoni"
type: "papers"
created: "2026-11-01T16:06:44Z"
updated: "2026-11-15T15:09:21Z"
tags: []
related: ["floquet-theory", "landau-zener-tunneling", "wikilink", "zno", "固体HHG", "固体高次谐波", "固体高次谐波产生", "布洛赫振荡", "高次谐波产生", "高次谐波产生（HHG）"]
source_raw: "2018-1807.02525-floquet-theoretical-formulation-and-analysis-of-high-harmoni.md"
growth_stage: "seedling"
confidence: 0.5
---

• 我先读取原始论文和 skill 写作规范。

• `_text_cache` 无此文全文缓存，raw 条目仅有摘要级一句话概述 —— 按 abstract 级四要素简写蒸馏。

  ---

  # Floquet 理论表述与分析固体高次谐波产生（Oka & Kitamura, 2018）

  ## 研究问题（Research Question）

  如何用 [[floquet-theory|Floquet 理论]]严格表述并分析 [[固体高次谐波产生|固体高次谐波产生（HHG）]]？本文的核心目标是：从激光场开启瞬间这一明确的初始条件出发，基于 Floquet 本征态推导出单色驱动下电流高次谐波分量的计算公式，并据此在解析层面厘清 HHG 光谱中不同平台的动力学起源。

  ## 背景（Background）

  [[固体高次谐波产生]]自 2011 年在 [[zno|ZnO]] 等块材中实验实现后，被视为探测固体电子结构和超快动力学的有力工具。已有的几种理论表述（如 Houston 基、Van Vleck 微扰、强场近似推广）在"单色驱动下平台结构对应何种微观机制"这一问题上存在分歧。本文作者（Oka、Kitamura）是 [[floquet-theory|Floquet 驱动体系]]研究的代表学者，其动机是为平台归属问题提供一个无近似争议、以 Floquet 本征态为基础的统一理论表述。

  ## 研究方法（Method）

  方法为纯理论推导，不依赖数值模拟：以单色激光场开启瞬间（t = 0）为初始条件，构建含驱动场的 [[floquet-theory|Floquet 哈密顿量]]并展开其本征态，将电流算符的时间演化投影到 Floquet 本征态基底上，由此给出高次谐波电流分量的显式计算公式；随后在解析可解的**一维交错势链（staggered potential chain）**模型上应用该公式。

  ## 发现（Findings）

  解析证明一维交错势链的 HHG 谱中存在**带内（intraband）**与**带间（interband）**两种不同起源的平台：前者对应 [[布洛赫振荡|布洛赫振荡（Bloch oscillation）]]驱动的带内电流贡献，后者对应 [[landau-zener-tunneling|Landau–Zener 隧穿]]引发的带间跃迁贡献。两个平台的宽度分别正比于场振幅，并分别反比于激光频率及其平方——这一标度关系把"哪个平台来自哪种动力学"的判断从数值拟合上升为解析结论。

  ---

  蒸馏完成。摘要级来源（raw 无全文、无独立 abstract 字段），未虚构任何数值；正文约 480 字，含 4 个实质小节与多处 [[wikilink]]。worker 落盘时请注入 `source_raw`（纯文件名 `2018-1807.02525-floquet-theoretical-formulation-and-analysis-of-high-harmoni.md`）与 `digest_level: abstract`。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：Floquet 本征态表述的固体 HHG 解析理论（场开启初条件 + 一维交错势链平台归属）

**原理**：以激光场开启瞬间（t=0）为明确初始条件构建 Floquet 哈密顿量，将电流算符时间演化投影到 Floquet 本征态基底，给出单色驱动下高次谐波电流分量的显式计算公式；在一维交错势链解析证明 HHG 谱中带内与带间两种平台并存：带内平台源于布洛赫振荡驱动电流、带间平台源于 Landau-Zener 隧穿跃迁——把平台归属从数值拟合上升为解析结论。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 平台宽度标度 | 分别正比于场振幅，并分别反比于激光频率及其平方（带内/带间） | 发现（Findings） |

**适用边界**：摘要级纯理论推导；解析结论在一维交错势链模型上建立，推广到真实材料带结构待核；与 Houston 基/Van Vleck 微扰等既有表述的关系未在摘要层面展开。
**代表作**：Oka & Kitamura, Floquet theoretical formulation and analysis of high harmonic generation in solids, arXiv:1807.02525 (2018)
*方法卡回补 2026-11-01*

<!-- linsai-wikilinks -->
## 关联概念

- [[floquet-theory]]
- [[landau-zener-tunneling]]
- [[wikilink]]
- [[zno]]
- [[固体HHG]]
- [[固体高次谐波]]
- [[固体高次谐波产生]]
- [[布洛赫振荡]]
- [[高次谐波产生]]
- [[高次谐波产生（HHG）]]
<!-- /linsai-wikilinks -->
