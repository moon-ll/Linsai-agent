---
title: "第一性原理DFT计算（含vdW修正的滑移势垒与能带计算）"
type: "methods"
created: "2026-09-19T14:00:42Z"
updated: "2026-11-01T04:55:12Z"
tags: ["方法学", "type/method"]
related: ["DFT计算", "dmft", "层间耦合", "自旋劈裂"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-09-27T02:13:42Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

基于第一性原理DFT并引入vdW色散修正，可定量计算层状材料的滑移势垒（如铁电翻转势垒）与堆叠依赖的电子结构（能带、滑移铁电极化、层间磁基态及自旋劈裂），既能刻画S→Te等电子替换系列中势垒与电子结构随堆叠演化的系统趋势，也能确定特定堆叠（如R堆叠2H-VX2双层）的滑移铁电极化、层间反铁磁基态与自旋劈裂能带。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| S→Te等电子替换系列滑移势垒范围 | 5.47→0.18 meV/f.u. | paper:2025-acs.jpcc.5c04939-low-ferroelectric-switching-barriers-and-stacking-insensitiv |

**联网检索升级**（2026-11-01，引用已核实）：第一性原理计算方法链——**DFT**（Kohn–Sham 1965）基态电子结构；**PBE** 泛函（GGA 标准，~25 万引）作半局域基线（系统性低估带隙，不含 vdW 色散）；**DFT+U**（Dudarev 简化方案 U_eff=U−J）修正强关联 d/f 壳层；**DFT-D3** 色散修正补层间结合；**约束 RPA（cRPA）**从全电子筛选出低能模型相互作用参数。

| 要素 | 数值/要点 | 出处 |
| --- | --- | --- |
| PBE 泛函 | GGA 标准，带隙低估 30-50%（3d 氧化物典型） | [1] |
| DFT+U | U_eff = U − J（Dudarev 简化方案） | [2] |
| D3 色散 | C6 系数 + BJ 阻尼；层间结合定量必需 | [3] |
| cRPA | 从 W 全谱筛 W_C 低能模型 U | [4]（库内 2510.26584 应用实例） |

- [1] J. P. Perdew, K. Burke, M. Ernzerhof, "Generalized Gradient Approximation Made Simple," Phys. Rev. Lett. 77, 3865 (1996). https://doi.org/10.1103/PhysRevLett.77.3865
- [2] S. L. Dudarev et al., "Electron-energy-loss spectra and the structural stability of nickel oxide: An LSDA+U study," Phys. Rev. B 57, 1505 (1998). https://doi.org/10.1103/PhysRevB.57.1505
- [3] S. Grimme et al., "A consistent and accurate ab initio parametrization of density functional dispersion correction (DFT-D) for the 94 elements H–Pu," J. Comput. Chem. 32, 1456 (2011, D3-BJ). https://doi.org/10.1002/jcc.21759；D3 原始：J. Chem. Phys. 132, 154104 (2010) https://doi.org/10.1063/1.3382344
- [4] 库内应用：`knowledge/wiki/papers/2510.26584.md`（1T-TaS₂ U_eff=0.4 eV、CDW 振幅 +3% 阈值；本地可验证路径）

✅ 基态结构/带对齐基线/模型参数锚定（Wannier 化、TB 参数）。
❌ PBE 带隙绝对值不可定量外推（同泛函内部横向比较用）；激子/强关联激发需 GW+BSE 或 tdDMFT；磁性体系必须开自旋极化。

## 适用边界

适用于以vdW层间耦合为主的二维层状体系，meV/f.u.量级的极低势垒对交换关联泛函与vdW修正方案的选择较敏感，且结论依赖具体堆叠构型，计算成本随体系尺寸增大。

## 代表作

- paper:2025-acs.jpcc.5c04939-low-ferroelectric-switching-barriers-and-stacking-insensitiv
- paper:2024-s41524-024-01288-5-strain-engineering-the-spin-valley-coupling-of-the-r-stackin

## 证据日志

- 2026-09-19｜r24｜仅简报｜[paper:2025-acs.jpcc.5c04939-low-ferroelectric-switching-barriers-and-stacking-insensitiv] 第一性原理DFT计算（含vdW修正的滑移势垒与能带计算）：定量给出S→Te等电子替换系列中滑移势垒（5.47→0.18 meV/f.u.）与电子结构随堆叠演化的系统趋势。
- 2026-09-19｜r24｜仅简报｜[paper:2024-s41524-024-01288-5-strain-engineering-the-spin-valley-coupling-of-the-r-stackin] 第一性原理DFT计算：确定R堆叠2H-VX2双层的滑移铁电极化、层间反铁磁基态与自旋劈裂能带。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[DFT计算]]
- [[dmft]]
- [[层间耦合]]
- [[自旋劈裂]]
<!-- /linsai-wikilinks -->
