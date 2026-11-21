# 对抗评审报告（第 7 轮 · 参考文献专项）

## 综合评分
0.65 / 1.00（references-only 双维均值）

## 维度评分
| 维度 | 权重 | 得分 | 问题数 |
| 严谨性 rigor | 0.5 | 0.55 | 7 |
| 完整性 completeness | 0.5 | 0.75 | 4 |
| 创新性 | — | N/A | — |
| 可行性 | — | N/A | — |

## 锚点对比
申请书写法："*Multidimensional inversion of HHG spectra for material property extraction*. **Proceedings of the National Academy of Sciences 121, e2301234121 (2024)**. DOI: 10.1073/pnas.2301234121"。申请书自评表述（[14] 条目末"国内（中科院物理研究所）可对标团队"）依赖此条。
benchmark 锚点：同领域 NSFC 面上参考文献通常①DOI 经 CrossRef 命中（DOI 与题名同年卷期匹配）②一作与作者链就位。申请书 [14] DOI 10.1073/pnas.2301234121 经 web 核查实际指向 USC 牙学院 "The Oncogene-Addicted Fate of Oral Squamous Cell Carcinoma Depends on Methionine Availability"（口腔癌蛋氨酸代谢），与 HHG/物探完全无关。
差距明显：申请人把同一 e-locator 编号借壳贴到 PNAS 2024 的伪造题名上，又在条目末挂"国内可对标"暗示其"真实存在"，属于典型凭记忆伪造 DOI。需立即重写。
锚点对比结论：差距明显——三条作者链错位 / 一条 DOI 错指无关文献 / 一条 DOI 单字符错位，已构成 critical 级别的元数据失真，参考文献不可采信原状。

## 问题清单

- [critical]｜references.md [14]｜DOI 10.1073/pnas.2301234121 真实指向 USC 口腔癌蛋氨酸代谢论文，与 HHG 完全无关｜丢弃该 DOI，改用题名"Multidimensional inversion of HHG spectra"在 PNAS/PRC 站重检真实文献；核实作者链后再补 DOI
- [critical]｜references.md [10]｜申请书一作"Xu Y., Zhou T."与 CrossRef 真实一作 Haijun Cao（Meng Sheng 组）不一致，文章号 90 一致｜改作者链为 Cao H., Sun J.-T., Meng S. (npj Quantum Materials 9, 90, 2024)
- [critical]｜references.md [21]｜申请书一作"Xu Y., Watanabe K., Taniguchi T."与真实一作 Richen Xiong（Cenke Xu / Chenhao Jin 组）不一致，且文章号 4758 错位（真实 4254）｜改作者链为 Xiong R., Brantly S. L., Su K., ..., Xu C., Jin C. (Nat Commun 15, 4254, 2024)
- [critical]｜references.md [3]｜DOI 10.1038/s41567-024-02540-7 在 CrossRef 404；同题名真实 DOI 为 10.1038/s41567-024-02640-8（末四位差一位 407→408）｜改 DOI 为 10.1038/s41567-024-02640-8
- [high]｜references.md [12]｜arXiv 2508.00296 未标注发表状态追踪日期；CrossRef 与期刊数据库均无对应正式发表条目，仅依赖预印本｜增补"截至 2026-09 检索尚无期刊发表记录"，正文如有依赖正式版的论断须迁移至已发表文献
- [high]｜references.md 引用分布与时效性节｜申请书自评"2024–2026 最新成果 13 篇 50.0%"与按出版年分箱不符（2023–2025 实为 18 篇 69.2%），时窗口径混乱｜统一以"近 3 年=出版年≥2023"为口径重计
- [medium]｜references.md [7]｜同时给 DOI 10.1103/PhysRevResearch.2.032015 与 arXiv:2005.01718 双 ID 但未注"亦见"关系，与 [11]/[17] 三 ID 风格不统一｜统一"DOI 优先；亦见 arXiv:XXXX.YYYYY"格式
- [medium]｜references.md [16]｜"Erratum: Nature 602, E19 (2022)"已注但卷期（7895）漏写｜补卷 602, 期 7895
- [medium]｜references.md 全文｜4 处条目以"等."结尾但对应作者数 ≤6（[2][3][9][18]），NSFC 写作规范通常要求列出全部作者或前 3+et al.，"等."为非标用法｜统一为"+et al."或列全前 3 作者
- [low]｜references.md [22]｜Photonics Research 13(5), 1235 (2025) 无 article number 与期号交叉验证；Yao/Lou 国内代表作唯一未挂 arXiv 预印本｜补 arXiv 编号（如有）并复核期号
- [low]｜references.md [4]｜Wang L. 一作首字母缩写"L."与同申请人 [14] Hu Y. 一作首字母缩写"Y."混用，大小写与姓名格式不统一｜统一为"姓 + 名首字母"或全名格式

## 对抗结论
- 本轮发现 11 个问题（critical:4, high:2, medium:4, low:2）
- 相比上轮 R6（[21][41] 错配 + 94处改 + g波归零）：本轮新增 4 条 critical（[14] DOI 错指口腔癌文献最严重），其余为格式一致性扫尾
- 4 条 critical 中 [3][10][21] 属"凭记忆克隆一作/页码"（R7 实锤教训命中），[14] 属"借壳伪造 DOI"（最重）
- 严谨性降至 0.55：作者链与 DOI 双重失真，足以让 NSFC 评审对全部 26 条的可信度产生连带怀疑，须当轮落地修复
- 是否达到输出标准：否（4 条 critical 待修复，二次验收需全量 CrossRef + 1 条 web 反查 [14] 真实文献是否存在）
- 建议把本报告作为工作日志草稿留 05_review 目录，R8 在 references.md 修复完成后再做核验

## 评分
创新性：N/A
可行性：N/A
严谨性：0.55
完整性：0.75
综合评分：0.65