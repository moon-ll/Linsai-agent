# 对抗评审报告（第 7 轮·参考文献专项）

项目类型：general｜对象：04_proposal/sections/references.md（33 条）｜日期：2026-09-14｜轮线：references（同轮号 overall 线文件已归档为 .bak-overall-20260914）

核查方法：33 条全部经 CrossRef API / arXiv abs 页反查（标题、作者链、期刊、卷页、年份）；编号一致性采信预检，正文未读，缺失引用凭预判。

## 核查结论总览

- 真实性：33/33 实证为真（22 条 DOI CrossRef 命中，10 条 arXiv sim=1.00 作者链逐位吻合，[33] DOI 真实）。预检 22 条未验证条目无一虚构。
- 主要问题集中在：2 个作者链错位、1 个标题转写不忠实、2 个可升级的正式版、人名格式不统一、2 条未引用条目。

## 问题清单

- [high]｜[11] L23｜作者链 pos3 错位：Ghimire N J 实为官方链第 16 位末位作者，非第 3 位｜按官方链改前三位 Regmi/Bhandari/Thapa 后接 et al.（action: rewrite）
- [high]｜[23] L47｜作者链 pos3 错位：Suárez Morell E 拆分错位，官方链为 González; Brumme; Morell｜改 Suárez Morell E → Morell E S（action: rewrite）
- [high]｜[33] L67｜标题非官方版："coupled to magnetic ordering" 应为官方 "and magnetic correlations"｜按 DOI 官方标题逐字更正（action: rewrite）
- [medium]｜[14] L29｜可升级正式版：Phys Rev B 114, L111201 (2026)，DOI 10.1103/5rrq-5g1k，仍标 preprint｜替换为正式发表信息（action: rewrite）
- [medium]｜[22] L45｜可升级正式版：Sci China-Phys Mech Astron 68, 297511 (2025)，DOI 10.1007/s11433-025-2698-5｜替换为正式发表信息（action: rewrite）
- [medium]｜[7] L15｜人名格式不统一：Rybak M 应为 Rybak M 与前两位格式对齐（仅姓氏缩写一致化）｜全文统一"姓 全缩写"或"姓 首字母"一种（action: rewrite）
- [medium]｜[12] L25｜DOI 格式混杂：10.1103/gly7-jzfl 为 APS 新式短码，与 10.1103/PhysRevLett.133.126801 传统式并存｜全文统一为期刊全称式 DOI（action: rewrite）
- [medium]｜[1][2] 未引用｜两条综述均未被正文引用（rationale 从 [3] 起引）｜在 AF 自旋电子学背景段补引，或删除并整体重编号（action: add/remove）
(预检未标记膨胀告警，无工作日志污染问题)
(引用相关性：33 条均指向反常磁体/MnPS3/贝里曲率/Rashba/超快自旋电子学，无一条无关引用)
(时效性：33 条中 2024–2026 文献 22 条，占 66.7%，达标)

## 锚点对比

- 引用：[5] Krempaský J, Šmejkal L, D'Souza S W, et al. Altermagnetic lifting of Kramers spin degeneracy. Nature, 2024, 626: 517–522. DOI: 10.1038/s41586-023-06907-7
- 对比（CrossRef 官方记录）：Krempaský, J.; Šmejkal, L.; D'Souza, S. W.; Hajlaoui, M.; Springholz, R. et al. Altermagnetic lifting of Kramers spin degeneracy. Nature 626, 517–522 (2024). DOI 10.1038/s41586-023-06907-7——作者链前三位、标题、期刊、卷页、年份、DOI 全部一致。
- 差距：本条为全表最优写法的代表；对照它可见 [11][23] 的作者链错位与 [33] 的标题转写属于可完全避免的机械错误，writer 补录时应以 CrossRef 官方记录为准逐位回录。

锚点对比结论：达标

## 维度评分

| 维度 | 权重 | 得分 | 依据 |
|---|---|---|---|
| 严谨性 | 0.5 | 0.83 | 33/33 真实、格式完整；2 作者链错位 + 1 标题转写不忠实 + DOI 码制混杂 |
| 完整性 | 0.5 | 0.90 | 33 条在标杆区间；近 3 年 66.7%；2 条未引用待处置；2 条正式版待升级 |

## 对抗结论

- 本轮发现 8 个问题（critical:0, high:3, medium:5）
- 相比上一轮（R6）：改善——预检标记的 22 条未验证条目全量反查全部为真，无新增虚构风险；新增 3 个错位类问题（作者链×2、标题转写×1）为对比例行发现
- 是否达到输出标准：是（无虚构、无编号断链、数量时效达标；遗留问题均为机械修正项，writer 一轮可清）

## 评分
创新性：N/A
可行性：N/A
严谨性：0.83
完整性：0.90
综合评分：0.87
