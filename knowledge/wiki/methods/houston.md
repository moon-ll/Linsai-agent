---
title: "Houston 基/加速布洛赫态图像"
type: "methods"
created: "2026-10-31T06:43:55Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "#type/method"]
related: ["2511.13114", "Berry 曲率", "TDDFT", "arXivID", "反常速度", "量子几何"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.6
updated_at: "2026-10-31T06:43:55Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

Houston 基（加速布洛赫态）图像将固体强场动力学刻画为沿 k(t)=k0+A(t) 被激光场加速的 k 空间波包演化：带内通道由加速度轨迹描述（含 Berry 曲率驱动的反常速度项）、带间通道由 Landau–Zener 型跃迁描述，从而用实空间/动量空间轨迹图像解析两通道对波形与量子几何量依赖的差异——新证据（单层 WS2 双色场 rt-TDDFT）进一步表明张应力通过重塑能带色散增强带内电流、通过显著重塑 Berry 曲率放大反常速度对垂直偏振谐波的贡献（增至近两倍），而双色场相对相位可作为电子–空穴对量子相干的亚飞秒开关。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 单层WS2张应力下垂直偏振谐波分量放大倍数 | ≈2倍（nearly a factor of two） | arXiv:2511.13114 |
| 验证模拟（rt-TDDFT, Octopus）实空间网格间距 | 0.21 Å（有效截断约850 eV） | arXiv:2511.13114 |
| 验证模拟布里渊区采样网格 | 36×36×1 Monkhorst-Pack | arXiv:2511.13114 |

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 模型哈密顿量 | H(k) = d(k)·σ，d1 = tx{cos(kx a) − cos(k0 a)} + ty{cos(ky b) − 1} + tz{cos(kz c) − 1}，d2 = ty sin(ky b)，d3 = tz sin(kz c) | 理论模型节 
| 外尔点位置 | (±k0, 0, 0) | 理论模型节 
| 晶格常数 a、b | 3.437 Å | 材料参数（四方晶格铁磁外尔半金属） 
| 晶格常数 c | 11.646 Å | 材料参数 
| 跃迁参数 tx | 1.88 eV | 材料参数 
| 跃迁参数 ty | 0.49 eV | 材料参数 
| 跃迁参数 tz | 0.16 eV | 材料参数 
| 外尔点间距 k0 | 0.2 rad/au（另取 0.3 rad/au 对比反常谐波产额） | 材料参数节 / 主要发现 6（Figs. S4、S5） 
| 激光脉宽 | ≈ 100 fs | 激光参数节 
| 激光强度 | 1 × 10^11 W/cm^2 | 激光参数节 
<!-- src:2021-2112_01745-high-harmonic-spectroscopy-of-light-driven-nonlinear-a -->

## 适用边界

该解析图像依赖偶极近似与 Houston 态随场绝热平移的近似、通常忽略退相干与多体关联；当动力学由全布里渊区非局域效应主导（如 TMD 中 Γ 与 M 点贡献及其量子干涉控制的平行偏振带间通道）时须以全 BZ 的 rt-TDDFT 数值为准，图像对 Berry 曲率高度集中的 K/K′ 谷反常速度通道最可靠，且其预测的应变/相位调制的定量验证成本受强场含时模拟的计算代价限制。

## 代表作

- arXiv:2511.13114
- arXiv:2022.01010

## 证据日志

- 2026-10-31｜r104｜回原文｜[paper:2025-2511.13114-orthogonal-attosecond-control-of-solid-state-harmonics-by-op] Houston 基/加速布洛赫态图像：以带内加速轨迹和带间跃迁的实空间/动量空间图像解释两通道对波形与几何量依赖的差异。
- 2026-10-31｜r104｜仅简报｜[paper:2022-2022.01010-observation-of-light-driven-band-structure-via-multi-band-hi] Houston基/加速度规范波包演化：以场加速k空间波包+Landau-Zener型带间跃迁描述多带强场动力学，是可迁移的解析框架。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2511.13114]]
- [[Berry 曲率]]
- [[TDDFT]]
- [[arXivID]]
- [[反常速度]]
- [[量子几何]]
<!-- /linsai-wikilinks -->
