---
title: "材料体系 HHG 方法（Weyl 半金属 / 交变磁体 / moiré / 高阶拓扑）"
type: "method-topics"
created: "2026-11-01T06:00:00Z"
updated: "2026-11-01T12:40:00Z"
tags: ["方法专题", "材料体系", "Weyl", "altermagnet", "moiré", "HOTI", "材料专题", "外尔半金属", "交变磁体", "莫尔", "高阶拓扑"]
related: ["固体HHG数值计算方法体系", "多变量光场设计", "HHG反演方法学", "量子几何张量分析"]
source_raw: "T2/T3 Q3 + 库内方法卡(2508.15631) + 已核实外部文献(Werner PRB 2024/Bauer&Hansen PRL 2018) + ssh-weyl rationale"
growth_stage: "growing"
confidence: 0.9
---

# 材料体系 HHG 方法（Weyl 半金属 / 交变磁体 / moiré / 高阶拓扑）

> **专题定位**：四类量子材料的 HHG 指纹、模型栈与判据——每类材料「用什么模型、
> 扫什么变量、读什么签名、阈值取多少」。对称性层的通用规则见 [[对称性与群论选择定则]]。

## 一、基本理论原理

**1.1 拓扑相与边态。** Bauer & Hansen 系统研究了有/无拓扑边态固体的 HHG 差异[3]，确立「拓扑量子数在谐波谱中留下印记」的理论基础。低阶（Chern/TI）与高阶拓扑绝缘体（HOTI）的 CD 指纹差异被 Lorenzo 等的三紧束缚模型对比系统化[2]：Haldane→Chern、Kane-Mele→TI、breathing Kagome→HOTI，体态/边态/角态贡献逐一分轨；拓扑相相对平庸相产额增强上限两个数量级（第二版收敛值）成为保守阈值 10² 的锚点。SSH 边界态的特殊机制：带隙频率谐波压缩，拓扑相与平庸相压缩度不同（Bera 等的填充调控可区分 0/2/4 个边缘模式[4]）。

**1.2 Weyl 半金属。** TaP 中 Weyl 费米子驱动的太赫兹三次谐波呈**严格立方功率律** I₃f ∝ I_f³（Pilch 等，库内 rationale[4]）——立方律是「散射贡献 Z」的标度律约束；Duan 等在 Cd₃As₂ Dirac 半金属微腔中报告三个数量级增强（不同物理根源，库内 rationale[4]）。增强的微观归属（Weyl 节点 X / Berry 曲率 Y / 散射 Z）是反演问题（[[HHG反演方法学]] 的闭合归一化判据）。

**1.3 交变磁体（altermagnet）。** Werner 等预言交磁体 HHG[1]：d 波自旋劈裂表现为谐波谱的磁场依赖各向异性（3ω ~15%、5ω ~30% 量级）——偶次/低阶谐波对自旋-轨道与磁序的敏感通道；后续工作扩展到自旋-电荷泵浦分离。g 波/kagome 变体与国内首例（Liu & Si PRB 112, L081105, 2025，见库内 NSFC-T1 Q6[4]）构成竞争格局。

**1.4 moiré 体系。** 扭转角是莫尔超晶格的新自由度：twist-angle 扫描把「堆叠/平移对称破缺」映射到谐波各向异性与选择定则——库内 2508.15631 的 breathing Kagome 模型即 twist-class 问题的紧束缚代理（滑移铁电/层间堆叠的极化-Berry 关联见 [[量子几何张量分析]]）。

## 二、核心算法实现（可参照复现）

**2.1 分材料模型栈**：

| 材料类 | 模型栈 | 扫描变量 | 读出判据 |
|---|---|---|---|
| HOTI/SSH | 四带 BHZ 推广 + 多带 TDSE/SBE 引擎 | 取向 + ε + 双基线波长 | 高阶 CD 角度谱 × 对称破缺边带（双变量） |
| Weyl 半金属 | 多带 TB（含节点倾斜项）+ SBE | 强度（立方律检验）+ 温度/磁场 | 立方律偏离点 = 散射通道开启；X/Y/Z 闭合分解 |
| 交变磁体 | kagome/偶子格 TB + SBE（含 SOC 开关） | 磁场方向 + 偏振 | 3ω/5ω 各向异性比率；自旋-电荷通道分离 |
| moiré | twist-angle 参数化 TB | 扭角 θ + 椭圆度 | 各向异性轴随 θ 的旋转 |

**2.2 通用流程。** ① 对称性识别（[[对称性与群论选择定则]] 的工作流）→ ② 最小 TB 构建（参数第一性锚定，[[固体HHG数值计算方法体系]] §2.3 纪律）→ ③ 引擎选择（SBE 主力/tdDMFT 多体，按关联强度）→ ④ 扫描协议（[[多变量光场设计]] §2.1）→ ⑤ 判据读出（阈值取保守下界，双基线验证）。

**2.3 验证清单。** ① 对称性空检验（λ=0 或等价对称极限下指纹严格为零[5]）；② 与实验基准对标（TaP 立方律、ZnO 各向异性图样[1]）；③ 模型阶数收敛（H4 领头阶解释真实体系 ≤10% 精度的经验线[5]）；④ 厚度/尺寸稳健性。

### 扩展 A：各材料签名数值表（联网检索整合）

| 材料 | 关键参数 | HHG 签名 | 出处 |
|---|---|---|---|
| ZnO | Eg 3.4 eV；激子结合 ~60 meV | 首次块体观测（2011）；激子-HHG 通道竞争 | [2][1] |
| MgO | Eg 7.8 eV | 各向异性六重图样（2017） | [1] |
| WSe₂ | 单层；T₂ = 24±1 fs（反演下限） | SBE 反演谷对比 | 库内 scheme |
| TaP | Weyl 节点 | THz 三次谐波严格立方律 I₃f∝I_f³ | 库内 rationale |
| MnTe 类交磁体 | d-wave 劈裂 | 3ω ~15%、5ω ~30% 磁场依赖 | [3] |
| Sr₂CuO₃ | Mott；J ~0.1 eV 量级 | doublon-holon 亚周期追踪 | [4] |

### 扩展 B：模型栈选型流程（文字版流程图）

对称性识别（[[对称性与群论选择定则]]）→ 关联强度判断（U/W 比：弱→SBE，强→tdDMFT）→激子显著性（Eb vs ℏω 驱动量子：显著→激子模型）→ 核量子效应（液体/软晶格→PIMD 耦合）→引擎确定 + T₂/参数锚定（[[固体HHG数值计算方法体系]] §2.2-2.3）→ 判据阈值（保守下界）。

- Y. S. You, D. A. Reis, S. Ghimire, Nat. Phys. 13, 345 (2017). https://doi.org/10.1038/nphys3955
- S. Ghimire et al., Nat. Phys. 7, 138 (2011). https://doi.org/10.1038/nphys1847
- P. Werner, M. Lysne, Y. Murakami, PRB 110, 235101 (2024). https://doi.org/10.1103/PhysRevB.110.235101
- arXiv:2508.00296（Sr₂CuO₃ doublon-holon）. https://arxiv.org/abs/2508.00296
## 三、典型应用案例

**案例 1（三模型家族对比）**：Lorenzo 等的三紧束缚模型 LOTI/HOTI 对比[2]——材料族筛选范式，其「HOTI 无清晰 CD 指纹」结论直接定义了 ssh-weyl 课题的方法学缺口（高阶量子数印记需要超越 CD 的双变量探针）。

**案例 2（交磁体理论预言）**：Werner 等的 altermagnet HHG[1]——磁场依赖谐波各向异性的定量预言（3ω ~15%、5ω ~30%），含/无 SOC 双设定，是 d-wave 劈裂探针设计的直接模板。

**案例 3（拓扑边态谱学）**：Bauer & Hansen[3]——边态有无对谐波谱影响的系统对比，SSH 链边界态压缩机制的先驱理论（实验端 Bera 填充调控[4]闭环）。

**案例 4（Weyl 立方律基准）**：TaP 严格立方律（库内 rationale[4]）——所有 Weyl 体系 HHG 反演的实验校核点：偏离立方即非散射通道开启，这使「立方律检验」成为 X/Y/Z 分解的第一道工序。

## 参考文献

[1] P. Werner, M. Lysne, Y. Murakami, "High harmonic generation in altermagnets," Phys. Rev. B 110, 235101 (2024). https://doi.org/10.1103/PhysRevB.110.235101
[2] B. Lorenzo et al., "High harmonic spectroscopy from lower-order to higher-order topological insulators," arXiv:2508.15631 (2025; 已刊 DOI: 10.1103/7zjc-4b4r). https://arxiv.org/abs/2508.15631
[3] D. Bauer, K. K. Hansen, "High-harmonic generation in solids with and without topological edge states," Phys. Rev. Lett. 120, 177401 (2018). https://doi.org/10.1103/PhysRevLett.120.177401
[4] 库内综合：`/Users/ll/Desktop/LinSai-CoPilot/research_proposals/pending_review/general-ssh-weyl-20260920/04_proposal/sections/rationale.md`（Bera PRB 108, 214104、TaP 立方律、Duan 微腔表述与引文）与 `/Users/ll/Desktop/hermes_workspace/research_proposals/2026_NSFG_strongfield_ultrafast/topics/T1_quantum_geometry/notes/Q6_3d_gap_analysis.md`（Liu & Si PRB 112, L081105 等；本地可验证路径）
[5] Pais, Iorio, Ciappina, "EFT 分层 Hamilton 族（λ=0 空检验与 H4 精度线）," arXiv:2610.15251 (2026). https://arxiv.org/abs/2610.15251

<!-- linsai-wikilinks -->
## 关联概念

- [[量子几何张量分析]]
- [[固体HHG数值计算方法体系]]
- [[多变量光场设计]]
- [[HHG反演方法学]]
- [[对称性与群论选择定则]]
- [[Kubo公式线性响应输运计算]]
- [[bistritzer]]
- [[c-TEPL测量]]
- [[lswt]]
- [[stack]]
- [[层间滑移势能面与极化路径计算]]
- [[Lifshitz-Kosevich分析与有效质量提取]]
- [[扭转角扫描与标定]]
- [[莫尔势首阶_Fourier_跃迁矩阵元模型]]
<!-- /linsai-wikilinks -->
