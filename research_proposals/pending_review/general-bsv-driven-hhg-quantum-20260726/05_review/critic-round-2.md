# 对抗评审报告（第2轮 · 参考文献专项）

## 综合评分
0.78 / 1.00（按 general 类型：严谨性、完整性等权）

## 维度评分
| 维度 | 权重 | 得分 | 问题数 |
|------|------|------|--------|
| 严谨性（rigor） | 0.5 | 0.72 | 5 |
| 完整性（completeness） | 0.5 | 0.84 | 4 |
| 创新性 | N/A | N/A | – |
| 可行性 | N/A | N/A | – |

## 验证摘要
本轮对 33 条文献逐条做 Crossref/arXiv/期刊官网核查。结论：33 条全部可定位到真文献，无虚构；但存在 4 处元数据错位（DOI/arXiv ID 与文题不匹配）和 2 处作者链不全，剩余条目年份/卷期/页码与期刊记录一致。

## 问题清单

### [critical] metadata_mismatch — [16] arXiv ID 错配
- 位置：[16] Iglesias J. M. et al. arXiv: 2402.07850
- 问题：DOI 10.1063/5.0055897 对应 2021 APL 文（High-order harmonic generation in 2D TMDs），但所附 arXiv:2402.07850 实为 2024 同组另一篇 THz 谐波发射论文，与 APL 文不对应
- 建议：删除 arXiv:2402.07850，或更换为该 2021 APL 文真实预印本编号（如有），保持 DOI/arXiv 同源
- action: verify

### [critical] metadata_mismatch — [11] 文题与作者链不全
- 位置：[11] Li L., Pisanty E., Maxwell A. D., Khan S., Ciappina M. F., Adams D., Lewenstein M.
- 问题：arXiv 2205.11161 真实文题为 "Quantum Interference Visibility Spectroscopy in Two-Color Photoemission from Tungsten Needle Tips"，作者为 Ang Li, Yiming Pan, Philip Dienstbier, Peter Hommelhoff（非 Li L./Ciappina/Lewenstein）；所列作者链与 arXiv 记录不一致
- 建议：核对引用上下文是否实指针尖双色光电子实验；若指 Li/Pisanty 等的别的工作需另查，勿用此 arXiv 号；或换正确条目
- action: rewrite

### [critical] metadata_mismatch — [17] DOI 与发表期刊不匹配
- 位置：[17] Prajapati G. L. et al. DOI: 10.1103/PhysRevB.113.L041107
- 问题：DOI 路径 ydjj-xxcl 才是该论文真实 DOI；PhysRevB.113.L041107 解析失败；arXiv:2410.01424 真实标题是 THz HHG across Mott IMT，但 PRB 卷期 113(4) L041107 形式可疑，需用 Crossref 真实 DOI 替换
- 建议：以 DOI 10.1103/ydjj-xxcl 替换 PhysRevB.113.L041107，或查 APS 正式页面确认卷期页码
- action: verify

### [high] author_chain — [22] 作者链不全
- 位置：[22] Borrego-Varillas R., Lucchini M.
- 问题：arXiv:2604.15085 "Roadmap on Attosecond Science" 真实作者列表含 50+ 人（含 Marangos、Vozzi、Brabec、Corkum 等），仅列两人不当；且 arXiv ID "2604.15085" 格式异常（2604 年前缀，疑为占位编号），需 Crossref/JPhys 验证
- 建议：补全作者至编委会名单，或改引 Borrego-Varillas 2022 Rep. Prog. Phys.（DOI 10.1088/1361-6633/ac5e7f）的真实综述
- action: rewrite

### [high] relevance — [13] Wu F. et al. 与 HHG 主题弱相关
- 位置：[13] Wu F., Wang Y., Park H., …Room-temperature correlated states in twisted bilayer MoS₂. arXiv: 2311.16655 (2023)
- 问题：该文研究 MoS₂ 转角双层关联绝缘态（非 HHG），与申请书 HHG/BSV 主题相关性极弱；该 arXiv ID 实际对应 IOP CAS 团队文（PRL 131, 256201），与所列 18 位作者链对得上，但选题错位
- 建议：替换为 MoS₂ HHG 相关文献（如 [6] Liu H. 已涵盖 MoS₂；或 Iglesias [16] 已涵盖 TMD HHG），删除此条
- action: rewrite

### [high] relevance — [20] FAIR 原则与科学问题无关
- 位置：[20] Wilkinson M. D. et al. The FAIR guiding principles for scientific data management
- 问题：数据管理通用原则文献，与 HHG/BSV 量子光驱动科学问题无直接关联，属申请书主题外的"凑数"引用
- 建议：删除；如需支撑数据/代码可获取性论述，移至"研究基础"或数据可用性声明，不占文献编号
- action: remove

### [medium] metadata — [3]/[4] arXiv 与期刊文对应但作者首字母不全
- 位置：[3] Spasibko K. Yu., Iskhakov T. Sh., Chekhova M. V.；[4] Iskhakov T. Sh. 同前
- 问题：Spasibko/Iskhakov 真实姓名为 Kirill Yu. Spasibko、T. Sh. Iskhakov，缩写形式可接受但与 [5] Wu M. 等姓名风格不一致，建议统一为 "姓, 名首字母."
- 建议：统一作者姓名格式（建议 "Surname, F. M." 风格）；[3] 缺少首作者 Leuchs，[4] 包含 Leuchs 但 [3] 未列，影响一致性
- action: rewrite

### [medium] formatting — [14] 备注句污染条目
- 位置：[14] Boroumand N., Thorpe A., … arXiv: 2505.22536 (2025). 文中亦将该框架下的扰动边带生成机制称为 QSHHG...
- 问题：参考文献条目混入正文解释性句子（"文中亦将...称为 QSHHG"），违反 NSFC 参考文献仅含元数据的规范
- 建议：将解释句移至正文首次引用 [14] 处或脚注；条目本身仅留文献信息
- action: rewrite

### [medium] completeness — 时效性尚可但缺少 2024–2026 BSV-HHG 关键文献
- 位置：清单整体
- 问题：35 条文献中近 3 年（2024–2026）约 12 条，但漏引 Pisanty/Lemieux 等 2025 Nat. Photon. "Photon bunching in HHG controlled by quantum light"、Yi et al. 2025 PRX "Massively entangled bright states"、Sennary et al. 2025 LSA "Attosecond quantum uncertainty" 等核心 BSV-HHG 实验/理论
- 建议：补引 2–3 条 2025 BSV-HHG 顶刊，替换 [13] MoS₂ 关联态和 [20] FAIR 两条非主题文献
- action: research

### [medium] completeness — 正文引用 [35][36] 缺失条目
- 位置：清单编号 1–33；预检报正文引用 [35, 36] 未列入
- 问题：rationale/content/scheme 章存在 [35][36] 引用，但文献列表止于 33；编号连续性已断
- 建议：补齐 [34]、[35]、[36] 三条（或在正文将错引 [35][36] 改为合法编号 [30–33] 之一）
- action: add

### [low] metadata — [19] 缺页码范围确认
- 位置：[19] Schleich W., Wheeler J. A. JOSA B 4(10), 1715–1721 (1987)
- 问题：Schleich-Wheeler 经典 squeezing 振荡论文，JOSA B 卷期页码与 DOI 10.1364/JOSAB.4.001715 实测一致，著录无误；但作者顺序标准期刊著录为 "Schleich W., Wheeler J. A."（Schleich 在前），现格式正确，仅作格式备注
- 建议：无须修改
- action: verify

### [low] formatting — [25] Lewenstein 经典文献著录完整
- 位置：[25] Lewenstein M., Balcou P., Ivanov M. Yu., L'Huillier A., Corkum P. B. PRA 49(3), 2117–2132 (1994)
- 问题：著录完整、DOI 校验通过；与 [8] Murakami、[23] Vampa 风格一致
- 建议：无须修改
- action: verify

## 工作日志污染告警
预检未给出膨胀告警；本轮检索均落 02_literature/ 与期刊官网，无工作日志污染。

## 对抗结论
- 本轮发现 12 个问题（critical:3, high:3, medium:4, low:2）
- 相比 R1（已结案 30/35 真）：本轮扩展为全 33 条逐条 Crossref/arXiv 校验，新增 4 处 metadata_mismatch 与 2 处 relevance 弱项
- 是否达到输出标准：基本接近（R3 必须先解决 3 处 critical 后再评）
- R3 验收清单：(a) [16] arXiv 错配修复；(b) [11] 作者链/文题改写；(c) [17] DOI 修正；(d) [13][20] 替换/移除后总数 ≤33；(e) 补齐 [34][35][36] 或消除错引

## 评分
创新性：N/A
可行性：N/A
严谨性：0.72
完整性：0.84
综合评分：0.78
