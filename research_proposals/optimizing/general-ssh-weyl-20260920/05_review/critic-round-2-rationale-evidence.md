# R2 评审证据：rationale [N] 编号 ↔ 文献表条目错位矩阵（程序比对 + arXiv 反查）

判定法：对 rationale 每个被引 [N]，取其正文上下文（±60 字）的人名/体系锚，与 references.md 同号条目首作者比对。共 34 个去重编号被引。

## 分类结果

**A. 编号错位坐实（29 个）**：正文以人名 X 锚定 [N]，但条目 [N] 是另一篇论文（真身为他人条目或缺失）。

| 正文锚（叙事人名/体系） | 错用编号 | 条目该号实为 | 真身所在条目 |
|---|---|---|---|
| Lewenstein 小组 Wannier-Bloch | [14] | Z. Guan SFA | 缺（列表外） |
| TDSE / SBE / TDDFT 计算范式 | [15][16][17] | Yu 分子 / Tancogne 椭圆率 / Luu&Wörner Berry 测量 | 体系不符 |
| Luu 2018 MgO Berry 反演 | [18] | R.E.F. Silva 拓扑强场 | [17]（沦为孤儿） |
| Silva 磁化轨道 | [19] | M. Garg 拍赫兹 | [18] |
| Garg WSe₂ 亚周期 | [20] | J. Freudenstein | [19] |
| Freudenstein 拍赫兹电流 | [21] | C. Liu ZnO Berry | [20] |
| Liu ZnO SBE 验证 | [22] | C. Heide | [21] |
| Bai Na₃Bi Dirac 锥 | [23] | O. Neufeld PRX | 无真身（全表无 Na₃Bi 文） |
| Heide 拓扑相变 | [24] | O. Sufyan DCD | [22] |
| Neufeld PRX 质疑 | [25] | S. Li Bi₂Se₃ | [23] |
| Sufyan DCD Haldane | [26] | Bauer&Hansen PRL | [24] |
| Li Bi₂Se₃ 双色场 | [27] | C. Jürß | [25] |
| Bauer&Hansen 2018 PRL | [28] | S. Pooyan | [26] |
| Jürß 2019 | [29] | C.-T. Liu ESSH | [27] |
| Pooyan 2024 | [30] | C.S. Lange | [28] |
| Liu 2026 ESSH arXiv:2608.22136 | [31] | M.L. Bera | [29] |
| Saugbjerg Lange 压缩度 | [32] | X. Zhang TaAs | [30] |
| Bera 2023 扩展 SSH | [33] | L. Yue 反常 HHG | [31]（[33]真身无叙事） |
| Jiang 2024 Jones 矩阵 | [34] | D. Schmitt（作者虚构，见下） | [32] |
| Schmitt TaP THG | [36] | R.K. Thakur | [34] |
| de las Heras RhSi | [37] | N. Rana 节线 | [35]（沦为孤儿） |
| Bharti 螺旋性 | [38] | Y.S. You ZnO 声子 | [36] |
| Rana NbSiₓTe₂ | [39] | B. Lorenzo HOTI | [37] |
| 绝缘体/石墨烯/量子阱量子点 | [10][11][12] | Yoshikawa 石墨烯 / Kim / Vampa 理论 | 体系-条目互相错位 |
| Vampa 三步模型 | [13] | E.N. Osika | [12] |

**B. 对位正确（2 个）**：[6] Ghimire 2011（人名+体系+年份全符）；[47] Medic。

**C. 区间引用未独立核（8 个）**：[1,2][3-5][7-9] 属气相/阿秒通用文献，低风险。

**D. 全文零引用孤儿（4 个）**：[35]（恰为 de las Heras 真身）、[42][43]（Avetissian 系填充）、[45]（Venkat）。

## 关键结论

1. 漂移非均匀（−1/−2/−3 混合，[6] 又对位）→ 系两套编号体系错误合并，非简单平移；不可用"整体 ±N"修复，必须逐叙事锚重排。
2. 正文引用 token 44 次，去重 34 个编号。

## arXiv API 反查（2026-09-24，https export）

- arXiv:2508.16166v2（=Nano Lett. 25,16637 TaP THG）作者链：P. Pilch, C. Zhu, S. Kovalev, R.M.A. Dantas, A. Bedoya-Pinto, S.S.P. Parkin, Zhe Wang。**无 D. Schmitt** → 条目[34]"D. Schmitt et al."系作者链虚构（题名/卷页/DOI 为真）。
- 2405.16125：X. Zhang, J. van den Brink, J. Li（条目[32]自洽 ✓）
- 2508.15631：B. Lorenzo 等 10 人（条目[39]自洽 ✓）；2609.06119：R.K. Thakur 等（条目[36]自洽 ✓）
- 2608.22136：C.-T. Liu, J.-S. You, H.-C. Hsu（条目[29]自洽 ✓）；2603.05346：A. de las Heras, O. Neufeld, A. Rubio（条目[35]自恪 ✓）

## 外部核验（web）

- Heide 2022（Nat. Photon. 16,620）：实验体系为 Bi₂Se₃/(Bi₁₋ₓInₓ)₂Se₃ 化学掺杂相变，**无"异质结"表述**（rationale L17"拓扑绝缘体异质结中探测到拓扑相变"系表述失准）。
- Garg 2016（Nature 538,359）：晶体 WSe₂ ✓。
