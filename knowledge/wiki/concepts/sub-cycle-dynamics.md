---
title: "sub-cycle-dynamics"
type: "concepts"
created: "2026-10-26T02:02:25Z"
updated: "2026-11-15T15:09:18Z"
tags: ["concept", "backfill"]
related: ["2025-2507_03996-a-general-approximator-for-strong-field-ioni", "2407.16350", "2507.03996", "RABBIT", "RABBITT", "TDDFT", "attochirp", "attosecond-physics", "high-harmonic-generation", "strong-field-ionization", "three-step-model", "三步模型", "强场电离", "截止定律", "阿秒瞬态吸收", "高次谐波产生", "高次谐波产生（HHG）"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
aliases: ["sub-cycle-dynamics"]
---

# sub-cycle-dynamics（亚周期动力学）

## 定义定位

亚周期动力学（sub-cycle dynamics）指发生在驱动激光场**单个光周期之内**的电子、空穴或偶极响应演化，对应阿秒（~10⁻¹⁸–10⁻¹⁶ s）至亚飞秒时间尺度。以常见 800 nm 钛宝石激光为例，一个光周期约 2.7 fs，“亚周期”即指其中百阿秒量级的时间窗口。该概念的核心主张是：强场物理中的隧穿电离、高次谐波辐射、带间跃迁等关键过程由**瞬时电场 E(t)** 而非周期平均光强支配，因此必须在周期内部的时间分辨层面建模，仅用循环平均的速率描述会系统性丢失相位与时刻信息。

## 物理内涵/技术原理

**1. 瞬时场支配性。** 隧穿电离率（如 ADK/PPT 公式）对场强呈指数依赖，且场峰附近电离窗口极窄（~几十阿秒至数百阿秒），导致电离事件在光周期内高度局域化，形成天然的“电离门控”。

**2. 三步模型中的亚周期轨迹。** 高次谐波产生（HHG）的经典图像完全由周期内时间轴刻画：电子在场峰附近隧穿电离（时刻 tᵢ）、在库仑场与激光场联合作用下加速、约 0.65 个周期后返回并复合（时刻 tᵣ）辐射谐波。鞍点方法给出的量子轨迹 (tᵢ, tᵣ) 对以及 Wigner/Gabor 时频分析提取的发射时刻，把连续谱谐波映射到亚周期时间轴上，形成 attochirp（阿秒啁啾）概念。

**3. 多体关联的亚周期修正。** 在多体层面（时间依赖 Schrödinger 方程、TDDFT 或含时密度矩阵框架），电子–电子关联与电子–空穴相互作用会在周期内轨迹尺度上改变电离振幅与复合截面。样本来源 arXiv:2407.16350 报道的“多体增强”即表明：关联效应主要在亚周期复合阶段放大谐波产率，这是平均场理论无法捕捉的结构。

**4. 固体与实验探测。** 固体中表现为亚周期带间电流、动力学 Bloch 振荡与瞬时带隙形变；实验上通过阿秒条纹（streaking）、RABBITT、阿秒瞬态吸收以及偏振门/双光学门等亚周期门控技术直接分辨。

## 与现有方法/概念的关联

- [[three-step-model]]：三步模型本质上就是 HHG 的亚周期轨迹语言，tᵢ 与 tᵣ 是其核心变量；
- [[high-harmonic-generation]]：谐波截止定律、双原发射与 attochirp 均由周期内轨迹族决定；
- [[strong-field-ionization]]：ADK/PPT 速率的瞬时场依赖是亚周期电离门控的数学根源；
- [[attochirp]] 与 [[attosecond-physics]]：亚周期动力学的直接可观测后果与学科载体；
- 对 [[2025-2507_03996-a-general-approximator-for-strong-field-ioni]] 一类的机器学习逼近器而言，能否复现周期内结构（瞬时电离率、发射时刻分布）是区分“光谱级”与“控制级”代理模型的分水岭。

## 林赛理解

在本项目（强场物理 × ML 代理建模的知识库）中，sub-cycle-dynamics 扮演**物理保真度基准**的角色。其一，arXiv:2407.16350 表明多体关联在亚周期轨迹层面改变 HHG 复合截面，任何代理模型若只拟合周期平均产率，会吸收而非解释这部分修正；其二，arXiv:2507.03996 的通才逼近器以强场电离为对象，其标签粒度应约定为瞬时电离率 ρ(t) 而非平均速率，否则丢失门控时刻信息，无法支撑下游阿秒控制与波形优化。因此我把该概念当作构建训练标签与验收指标时的“时间分辨率契约”。

## 学习路径/参考

1. Corkum & Krausz, *Attosecond Science*, Science / Nat. Phys. (2007) —— 亚周期时间分辨的学科总览；
2. Lewenstein et al., Phys. Rev. A **49**, 2117 (1994) —— SFA 与量子轨迹 (tᵢ, tᵣ) 方法的奠基文献；
3. arXiv:2407.16350 —— 多体关联对 HHG 亚周期复合动力学的增强效应（本项目样本一）；
4. arXiv:2507.03996 —— 强场电离的通用逼近器，需关注其对周期内结构的拟合能力（本项目样本二）；
5. 工具性阅读：Gabor/Wigner 时频分析提取谐波发射时刻；偏振门控与双光学门综述。

<!-- linsai-wikilinks -->
## 关联概念

- [[2025-2507_03996-a-general-approximator-for-strong-field-ioni]]
- [[2407.16350]]
- [[2507.03996]]
- [[RABBIT]]
- [[RABBITT]]
- [[TDDFT]]
- [[attochirp]]
- [[attosecond-physics]]
- [[high-harmonic-generation]]
- [[strong-field-ionization]]
- [[three-step-model]]
- [[三步模型]]
- [[强场电离]]
- [[截止定律]]
- [[阿秒瞬态吸收]]
- [[高次谐波产生]]
- [[高次谐波产生（HHG）]]
<!-- /linsai-wikilinks -->
