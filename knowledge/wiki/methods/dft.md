---
title: "第一性原理DFT能带计算（含磁序薄膜体系）"
type: "methods"
created: "2026-10-09T23:42:33Z"
updated: "2026-11-08T05:06:52Z"
tags: ["方法学", "#type/method"]
related: ["2024-2408.08835-altermagnetism-in-the-layered-intercalated-transition-metal", "2408.08835", "2503.16670", "Altermagnetism in the layered intercalated transition metal dichalcogenide CoNb4Se8", "CoNb4Se8 层状交变磁性化合物的电子结构（ARPES+DFT）", "DFT计算", "arpes", "dmft", "交变磁体", "自旋劈裂", "量子度规"]
source_raw: ""
growth_stage: "mature"
confidence: 0.5
updated_at: "2026-10-31T03:01:12Z"
settled_count: 3
---

<!-- methods-settle:v1 -->

## 原理

基于自洽求解Kohn-Sham方程的（自旋极化）DFT能带计算获取含磁序体系能带结构：在偶数层EuSn2As2薄膜中确认II型倾斜表面Dirac态及其倾斜参数，在偶数层MnBi2Te4中给出隐藏贝里曲率偶极与量子度规偶极的真实量级及带边热点的能带位置，为非线性霍尔/层霍尔输运提供第一性原理依据；对层状插层过渡金属化合物可揭示动量依赖、符号交变（k与-k反号）的自旋劈裂能带作为交变磁性的能带指纹，确定反铁磁基态与对称性主导的自旋劈裂并与实验费米面/能带定量对照；新证据表明该方法可进一步扩展为高通量DFT材料筛选——以逆Lieb几何等结构判据在晶体数据库中系统检索候选家族（'从几何motif到真实材料'的可复用范式），并对四方Heusler化合物批量计算磁性序与能带自旋劈裂，快速锁定大自旋劈裂的金属交变磁体候选。

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

结果依赖交换关联泛函近似与磁结构建模——薄膜情形需设定slab层厚、层宇称及层间磁序（表面Dirac态与几何偶极量级对磁构型敏感），交变磁体的动量自旋劈裂由磁对称性主导且对磁序设定敏感，大超胞计算成本高且属基态近似需与ARPES/输运实验交叉验证；高通量筛选还受几何结构判据完备性与批量计算精度的限制，命中的候选材料仍需逐体系精细DFT计算与实验验证方可确认。

## 代表作

- arXiv:2502.16463
- arXiv:2510.23971
- arXiv:2408.08835
- arXiv:2503.16670
- arXiv:2508.04839
- arXiv:2609.14051

## 证据日志

- 2026-10-09｜r62｜仅简报｜[paper:2025-2502.16463-quantum-metric-non-linear-hall-effect-in-an-antiferromagneti] 第一性原理DFT能带计算（含磁序薄膜体系）：确认EuSn2As2偶数层薄膜中II型表面Dirac态的存在及其倾斜参数。
- 2026-10-09｜r62｜仅简报｜[paper:2025-2510.23971-nonlinear-layer-hall-effect-and-detection-of-the-hidden-berr] 第一性原理能带计算：在偶数层MnBi2Te4上给出隐藏贝里曲率偶极与量子度规偶极的真实量级及带边热点的能带位置。
- 2026-10-24｜r89｜仅简报｜[paper:2024-2408.08835-altermagnetism-in-the-layered-intercalated-transition-metal] 自旋极化 DFT 能带计算：揭示动量依赖、符号交变（k 与 -k 反号）的自旋劈裂能带，给出交变磁性的能带指纹。
- 2026-10-24｜r89｜仅简报｜[paper:2025-2503.16670-electronic-structure-of-a-layered-altermagnetic-compound-con] 自旋极化DFT计算：确定反铁磁基态与对称性主导的动量依赖自旋劈裂，并与实验费米面/能带定量对照。
- 2026-10-31｜r103｜仅简报｜[paper:2025-2508.04839-inverse-lieb-materials-altermagnetism-and-more] 高通量DFT几何判据材料筛选：以逆Lieb几何为结构判据在晶体数据库中系统检索候选家族，是'从几何 motif 到真实材料'的可复用筛选范式。
- 2026-10-31｜r103｜仅简报｜[paper:2026-2609.14051-large-spin-splitting-metallic-altermagnets-from-machine-lear] 高通量DFT筛选：对四方Heusler化合物批量计算磁性序与能带自旋劈裂，快速锁定金属变磁体候选

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2024-2408.08835-altermagnetism-in-the-layered-intercalated-transition-metal]]
- [[2408.08835]]
- [[2503.16670]]
- [[Altermagnetism in the layered intercalated transition metal dichalcogenide CoNb4Se8]]
- [[CoNb4Se8 层状交变磁性化合物的电子结构（ARPES+DFT）]]
- [[DFT计算]]
- [[arpes]]
- [[dmft]]
- [[交变磁体]]
- [[自旋劈裂]]
- [[量子度规]]
<!-- /linsai-wikilinks -->
