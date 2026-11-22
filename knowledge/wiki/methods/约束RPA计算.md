---
title: "约束RPA（cRPA）"
type: "methods"
created: "2026-09-20T10:01:06Z"
updated: "2026-11-01T04:55:12Z"
tags: ["方法学", "type/method"]
related: ["2023-PMC10214477-first-principles-investigation-of-screened-coulomb-interacti", "2510.26584", "dmft"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-09-27T02:13:42Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

约束RPA（cRPA）在计算屏蔽库仑相互作用时，从总屏蔽极化中剔除目标关联子空间（如窄带/Z2子空间）内部的电子-空穴跃迁，从而在不重复计数关联的前提下定量给出有效Hubbard U（以及Hund耦合J、团簇间V）；该框架还可沿序参量（如CDW振幅）扫描，追踪U、J随结构演化的动态行为（如U随振幅压缩显著下降）。

## 参数表

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

结果依赖目标子空间与环境能带之间的清晰划分（划分不当或能带交叠会引入误差），且仅剔除子空间内跃迁、其余屏蔽以常规RPA处理，无法包含关联子空间自身的动态屏蔽效应。

## 代表作

- paper:2025-2510.26584-dynamical-control-of-coulomb-interactions-and-hubbard-bands
- paper:2023-PMC10214477-first-principles-investigation-of-screened-coulomb-interacti

## 证据日志

- 2026-09-20｜r30｜仅简报｜[paper:2025-2510.26584-dynamical-control-of-coulomb-interactions-and-hubbard-bands] 约束RPA（cRPA）：定量给出CDW振幅扫描下屏蔽后的Hubbard U与Hund耦合J的演化，证明U随振幅压缩显著下降。
- 2026-09-20｜r30｜仅简报｜[paper:2023-PMC10214477-first-principles-investigation-of-screened-coulomb-interacti] 约束RPA（cRPA）：从总屏蔽中剔除目标Z2子空间内跃迁，定量给出窄带上的有效Hubbard U与团簇间V，避免关联双重计数。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2023-PMC10214477-first-principles-investigation-of-screened-coulomb-interacti]]
- [[2510.26584]]
- [[dmft]]
<!-- /linsai-wikilinks -->
