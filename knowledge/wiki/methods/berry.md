---
title: "Berry 曲率偶极（BCD）分析"
type: "methods"
created: "2026-10-04T10:21:49Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "#type/method"]
related: ["2024-2411.16675-fully-nonequilibrium-hall-response-from-berry-curvature", "2026-2607.01519-nonperturbative-nonlinear-hall-effect-in-nonequilibrium-stea", "2026-2607_13863-ultrafast-altermagnetophononics", "2505.16999", "2510.01727", "2510.16672", "2603.29106", "Berry 曲率", "Berry曲率", "Berry曲率偶极", "Chern数", "arXivID", "arpes"]
source_raw: ""
growth_stage: "mature"
confidence: 0.5
updated_at: "2026-11-15T01:11:38Z"
settled_count: 3
---

<!-- methods-settle:v1 -->

## 原理

Berry 曲率偶极（BCD）分析以动量空间中 Berry 曲率分布的一阶矩描述非中心对称体系的二阶响应，解析框架可推广至温度梯度驱动的横向非线性能斯特/热输运并与电学非线性霍尔形成互补读出通道，光驱动体系亦存在 Berry 曲率闭式公式可定位能隙处曲率热点，且作为弱场半经典基准其在强场完全非平衡区被非微扰理论对照检验并证明失效；本轮新证据进一步把 Berry 曲率类分析拓展为拓扑量读出窗口——轨道磁矩算符与 Berry 曲率/Chern 数的关联使逆法拉第（IFE）二阶光响应张量与能带 Chern 数建立解析联系，Berry 曲率/Chern 数计算亦可直接表征光致能隙拓扑、证明螺旋度可控 Chern 数符号的 Chern 绝缘体相。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| hBN 五次谐波（5ω）转换效率 | ~4×10⁻⁵ | 2025-2510_16672 |
| 菱方石墨 DSS 弯曲深度（L=18 平板, PBE） | 20 meV | 2026-2607_28491 |
| 菱方石墨 DSS 弯曲深度（L=60 平板, PBE） | 34 meV | 2026-2607_28491 |
| 菱方石墨 DSS 弯曲深度（L=60 平板, r2SCAN+rVV10） | 36 meV | 2026-2607_28491 |
| 菱方石墨 DSS 弯曲深度（半无限 (001) 表面） | 38 meV | 2026-2607_28491 |
| ARPES 实验弯曲深度（对照） | 32 meV | 2026-2607_28491（转引 Zhang et al., PNAS 121, e2410714121） |
| |Ω|/TrG 于 K̄ 中心 | ≈0.96（r2SCAN+rVV10 下 0.958） | 2026-2607_28491 |
| 菱方石墨含 SOC 节线带隙 | 0.03 meV | 2026-2607_28491 |
| 侧表面狄拉克点能量 | E_F − 1.5 eV | 2026-2607_28491 |
| 菱方石墨晶格常数 a / c | 2.461 Å / 10.061 Å（实验值） | 2026-2607_28491 |
| 层间 vdW 距离 | 3.354 Å（比石墨 3.473 Å 小 3.5%） | 2026-2607_28491 |
| 平面波截断能 | 400 eV | 2026-2607_28491 |

## 适用边界

BCD 仅在空间反演破缺（时间反演可保持）体系中非零；其电场与温度梯度驱动的解析表达均基于半经典小扰动弱场展开，在强场完全非平衡区、Berry 曲率热点附近以及弛豫时间动量依赖情形下失效（需非微扰/完全非平衡处理替代）；光驱动闭式曲率结果依赖特定能带模型近似，本轮新增的 IFE–Chern 数解析联系与光致能隙拓扑表征亦仅限相应二阶光响应与光致能带（如二聚化晶格）近似框架内成立，且光致 Chern 数符号由泵浦螺旋度决定。

## 代表作

- paper:2025-2505.16999-nonlinear-thermal-and-thermoelectric-transport-from-quantum
- paper:2026-2603.29106-exploring-non-trivial-band-structure-and-spin-polarizations
- paper:2024-2411.16675-fully-nonequilibrium-hall-response-from-berry-curvature
- paper:2026-2607.01519-nonperturbative-nonlinear-hall-effect-in-nonequilibrium-stea
- paper:2022-2201.06243-low-frequency-divergence-of-circular-photomagnetic-effect-in
- paper:2025-2508.18360-light-induced-odd-parity-altermagnets-on-dimerized-lattices

## 证据日志

- 2026-10-04｜r58｜仅简报｜[paper:2025-2505.16999-nonlinear-thermal-and-thermoelectric-transport-from-quantum] Berry 曲率偶极（BCD）分析：给出温度梯度驱动下横向非线性能斯特/热输运信号的解析表达，与电学非线性霍尔形成互补读出通道。
- 2026-10-04｜r58｜仅简报｜[paper:2026-2603.29106-exploring-non-trivial-band-structure-and-spin-polarizations] Berry 曲率解析计算：给出光驱动体系 Berry 曲率的闭式公式，定位能隙处的曲率热点及其随光场演化。
- 2026-10-30｜r101｜仅简报｜[paper:2024-2411.16675-fully-nonequilibrium-hall-response-from-berry-curvature] Berry曲率偶极（BCD）二阶响应框架：作为弱场基准被对照检验，并被证明在强场完全非平衡区失效。
- 2026-10-30｜r101｜仅简报｜[paper:2026-2607.01519-nonperturbative-nonlinear-hall-effect-in-nonequilibrium-stea] Berry 曲率偶极（BCD）半经典理论：作为本文对照与超越的基准，其失效边界（强场、热点附近、弛豫时间动量依赖）被明确定位。
- 2026-11-15｜r137｜仅简报｜[paper:2022-2201.06243-low-frequency-divergence-of-circular-photomagnetic-effect-in] 轨道磁矩算符与Berry曲率/Chern数的关联分析：将IFE响应张量与能带Chern数建立解析联系，使二阶光响应成为拓扑量的读出窗口。
- 2026-11-15｜r137｜仅简报｜[paper:2025-2508.18360-light-induced-odd-parity-altermagnets-on-dimerized-lattices] Berry曲率与Chern数计算：表征光致能隙的拓扑性，证明Chern绝缘体相及螺旋度可控的Chern数符号。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2024-2411.16675-fully-nonequilibrium-hall-response-from-berry-curvature]]
- [[2026-2607.01519-nonperturbative-nonlinear-hall-effect-in-nonequilibrium-stea]]
- [[2026-2607_13863-ultrafast-altermagnetophononics]]
- [[2505.16999]]
- [[2510.01727]]
- [[2510.16672]]
- [[2603.29106]]
- [[Berry 曲率]]
- [[Berry曲率]]
- [[Berry曲率偶极]]
- [[Chern数]]
- [[arXivID]]
- [[arpes]]
<!-- /linsai-wikilinks -->
