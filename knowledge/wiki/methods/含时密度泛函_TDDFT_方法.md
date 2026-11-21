---
title: "含时密度泛函（TDDFT）方法"
type: "methods"
created: "2026-10-31T11:38:09Z"
updated: "2026-11-15T05:32:54Z"
tags: []
related: ["DFT计算", "Impact of the electronic band structure in high-harmonic generation spectra of solids", "TDDFT", "固体HHG", "固体HHG数值计算方法体系", "层间耦合"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
source_reliability: "reliable"
sources: ""
- title: "general-mos2-20260905"
source_type: "archived_proposal"
---

TDDFT 直接计算晶体在强场下的含时电流，可从头算给出谐波产额及角分布，并能描述层间耦合和莫尔势而无需经验参数；其计算成本随莫尔原胞原子数急剧上升，当前只适合莫尔周期较小、扭转角较大的构型。

## 参数表

**canonical 升级**（2026-11-01，教科书级方法要素，引用已核实）：
见 [[DFT计算]] 的 TDDFT 段：Runge–Gross 定理（1984）保证含时密度-外势一一对应，TDKS 方程实时传播给出强场响应。本页为其方法卡：两种模式（线性响应 Casida / 实时 RT-TDDFT）、绝热近似误差源、传播子选择（Magnus/CN/时间反演对称）。

| 要素 | 内容 | 出处 |
| --- | --- | --- |
| 理论基石 | Runge–Gross 定理（1984） | [[TDDFT]] |
| 主要误差源 | 绝热 xc 近似（ALDA/AGGA） | [[TDDFT]] |
| 传播子 | Magnus / Crank–Nicolson / 强制时间反演对称 | [[TDDFT]] |

## 代表作

- N. Tancogne-Dejean, A. Rubio, "Impact of the electronic band structure in high-harmonic generation spectra of solids," Phys. Rev. Lett. 118, 087403 (2017). https://doi.org/10.1103/PhysRevLett.118.087403

## 适用边界

✅ 强场非微扰响应的第一性原理主力引擎（[[固体HHG数值计算方法体系]] §1.4）。
❌ 双激发/长时电荷转移失效；GPU 实现见 2603.21835 方向。

- N. Tancogne-Dejean, A. Rubio, "Impact of the electronic band structure in high-harmonic generation spectra of solids," Phys. Rev. Lett. 118, 087403 (2017). https://doi.org/10.1103/PhysRevLett.118.087403

<!-- linsai-wikilinks -->
## 关联概念

- [[DFT计算]]
- [[Impact of the electronic band structure in high-harmonic generation spectra of solids]]
- [[TDDFT]]
- [[固体HHG]]
- [[固体HHG数值计算方法体系]]
- [[层间耦合]]
<!-- /linsai-wikilinks -->
