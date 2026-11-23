---
title: "salmon-williams-lax"
type: "methods"
created: "2026-10-24T14:26:40Z"
updated: "2026-11-07T20:26:03Z"
tags: ["方法学", "#type/method"]
related: ["2026-2607_17109-microscopic-origin-of-dephasing-in-solids-from-fir", "2505.09387", "2607.17109", "TDDFT", "arXivID", "时变密度泛函理论", "面向阿秒物理的时变密度泛函理论技术综述：从气相到固体"]
source_raw: ""
growth_stage: "mature"
confidence: 0.6
updated_at: "2026-11-07T20:26:03Z"
settled_count: 2
aliases: ["SALMON", "Williams-Lax", "Williams-Lax method"]
---

<!-- methods-settle:v1 -->

## 原理

威廉斯–拉克斯（Williams–Lax）均匀半经典近似给出强场带间跃迁/弗朗兹–凯尔迪什吸收的解析速率；新证据确立其时间域推广（Yamada & Yabana，基于 SALMON 实时 TDDFT）——把电子–声子退相化为冻结的热+零点核构型响应的统计平均（实践上单发构型即可、无需系综平均），金属中自然涌现 ~10 fs Drude 阻尼、介质中不引入经验 T2 即得干净高次谐波谱，且超胞动力学映射回原胞密度矩阵表明退相主要由对角布居动力学而非非对角相干衰减主导，可作为该半经典方法移植与第一性原理基准检验的现成平台。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 金属(Al) Drude 弛豫时间 τ | ~10 fs | 2607.17109 |
| 热无序温度（含热运动与零点运动） | 300 K | 2607.17109 |
| 超胞尺寸（收敛值） | 4×4×4 | 2607.17109 |
| Al 超胞原子/轨道数（2×2×2→3×3×3→4×4×4 序贯收敛） | 32/108/256 原子，64/216/512 轨道 | 2607.17109 |
| k 网格（Bloch 态总数守恒） | 原胞 48³ → 对应超胞 24³/16³/12³ | 2607.17109 |
| Al 原胞晶格常数/k 网格 | 4.0494 Å，48³ k（含 Γ） | 2607.17109 |
| Si 4×4×4 超胞规模 | 512 原子，4³ k（原胞 3.567 Å/8 原子/16³ k） | 2607.17109 |
| 金刚石 4×4×4 超胞规模 | 512 原子，9³ k（原胞 5.429 Å/8 原子/36³ k） | 2607.17109 |
| 热无序采样构型数 | 单发 1 个（10 个独立随机构型 σ(t) 几乎一致，无需系综平均） | 2607.17109 |
| 声子振幅设置 | 等于其标准差 | 2607.17109 |
| 非对角相干衰减时标 | ~1 fs（快衰减后近恒定，对角项主导 ~10 fs Drude 衰减） | 2607.17109 |
| 金刚石 HHG 干净谐波阶数（无需经验 T2） | >20 阶 | 2607.17109 |

## 适用边界

原式依赖抛物带、偶极近似与准静态均匀场假设（非抛物带、强散射或超短脉冲非偶极效应显著时失效）；时间域 Williams–Lax 框架依赖冻结核近似（飞秒电子动力学内离子位移冻结，仅显含电子–声子静无序通道，未含电子–电子与杂质散射）与 ALDA 泛函精度，且需 4×4×4 超胞/512 轨道量级的大体系长时间实传播，成本随体系尺度与脉冲时长增长，适合作对照基准而非大规模替代。

## 代表作

- 2026-2607.17109-microscopic-origin-of-dephasing-in-solids-from-fir
- 2025-2505.09387-technical-review-time-dependent-density-functional-theory-fo

## 证据日志

- 2026-10-24｜r92｜仅简报｜[paper:2025-2505.09387-technical-review-time-dependent-density-functional-theory-fo] 开源实时TDDFT软件（SALMON系，Yabana组生态）：提供可复现的固体强场光电耦合计算流程与气相-固相对比算例，是方法移植的现成平台。
- 2026-11-07｜r122｜回原文｜[paper:2026-2607.17109-microscopic-origin-of-dephasing-in-solids-from-fir] 时间域Williams-Lax方法：把电子-声子退相化为冻结核构型响应的统计平均，绕开微扰论与唯象耗散项。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2026-2607_17109-microscopic-origin-of-dephasing-in-solids-from-fir]]
- [[2505.09387]]
- [[2607.17109]]
- [[TDDFT]]
- [[arXivID]]
- [[时变密度泛函理论]]
- [[面向阿秒物理的时变密度泛函理论技术综述：从气相到固体]]
<!-- /linsai-wikilinks -->
