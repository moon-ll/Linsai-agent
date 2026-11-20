---
title: "BSE 贝特-萨尔皮特方程"
type: "methods"
created: "2026-11-15T16:30:33Z"
updated: "2026-11-16T05:30:14Z"
tags: ["方法学", "#type/method"]
related: ["Bethe-Salpeter方程", "GW近似", "MoS₂_单层_A_B_激子共振", "TDDFT", "固体HHG", "强场驱动"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.7
settled_count: 0
---

# BSE 贝特-萨尔皮特方程（激子光学响应）

<!-- methods-settle:v1 -->

## 原理

Bethe-Salpeter 方程（BSE）在 GW 准粒子能级上求解电子-空穴两体关联：以 Γ 点/动量空间构建电子-空穴对态基，求解含直接吸引项（激子束缚）与交换项（局域场效应）的两体本征问题，得到含激子的介电函数与光学谱。它是"GW+BSE"第一性原理光学方法链的标准后段——[[GW近似]]给单粒子准粒子能级（修正 DFT 带隙低估），BSE 在其上叠加电子-空穴吸引，给出激子结合能与正确的光学线形。

## 参数表

| 要素 | 数值/要点 | 出处 |
| --- | --- | --- |
| 方法链 | DFT（PBE）→ GW（准粒子能量）→ BSE（两体关联光学谱） | [1] |
| 两体哈密顿 | H^BSE = (E_c − E_v)δ + 直接项（吸引，Keldysh 屏蔽库仑）+ 交换项（局域场） | [1] |
| 近似口径 | Tamm–Dancoff 近似（TDA，常用于固体）；单谐振子截断（nv × nc 组合数控制规模） | [1] |
| 激子结合能 | 二维 TMD 典型 0.1–0.5 eV（体相 ~0.01–0.1 eV）；MoS₂ 单层 A 激子 1.88 eV 处结合能数百 meV 量级 | [2] |
| k 网格 | 激子锐度对 Γ 点采样敏感（激子半径小 → 需密网格） | [1] |

- [1] G. Strinati, "Application of the Green's functions method to the study of the optical properties of semiconductors," Riv. Nuovo Cimento 11, 1 (1988)；M. S. Hybertsen, S. G. Louie, PRL 55, 1541 (1985)（GW+BSE 开创链）
- [2] 库内概念页：`knowledge/wiki/concepts/Bethe-Salpeter方程.md`、`knowledge/wiki/concepts/GW近似.md`、`knowledge/wiki/concepts/MoS₂_单层_A_B_激子共振.md`

## 适用边界

BSE 是线性响应/激子谱方法：不给含时动力学（强场驱动下的激子演化需 TDDFT）；计算成本远高于 GW 本身（两体本征问题 O(N⁴) 量级）；声子旁路、双激子与激子-激子相互作用超出标准 BSE。固体 HHG 的带间判读若涉及激子近共振（如 MoS₂ A/B 激子窗），产额线形的定量参照应取 BSE 而非独立粒子近似。

## 代表作

- Hybertsen–Louie 与 Strinati 方法链原始文献
- 库内：`Bethe-Salpeter方程.md` / `GW近似.md` / `MoS₂_单层_A_B_激子共振.md`

<!-- linsai-wikilinks -->
## 关联概念

- [[Bethe-Salpeter方程]]
- [[GW近似]]
- [[MoS₂_单层_A_B_激子共振]]
- [[TDDFT]]
- [[固体HHG]]
- [[强场驱动]]
<!-- /linsai-wikilinks -->
