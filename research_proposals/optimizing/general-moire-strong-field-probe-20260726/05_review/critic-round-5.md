# 对抗评审报告（第 5 轮 · 参考文献专项）

评审对象：04_proposal/sections/references.md（26 条，2026-09-05 修订版，本轮实际读取）
审查日期：2026-09-08；方法：Crossref DOI 全量（24 条）+ arXiv API（6 个编号）+ OpenAlex 三源反查
编号一致性采信程序化预检，不重复；相关性按条目自附用途标注+解析记录主题比对，26 条全部切题，无关引用 0。

文件处理：原 critic-round-5.md（09-05 整体一致性审查）先归档为 .archive-critic-round-5-overall-20260905-pre-overwrite-references-r5-20260908.md 再写入本报告。

## 核查结果总览
26 条中 14 条五件套（题/作者/刊/卷页/年）全对；12 条有缺陷：无法证实 1、DOI 错构 1、死链 1、作者串错位 4、标题失真 6、统计自述不实 2（类别有交叉）。预检风险名单 10 条中 5 条实锤（[9][10][17][21][25]），[2][11][18][24] 本轮通过；池内条目 [3][8][12][14] 同样中弹——再次印证"全量反查、不可抽查"。

## 问题清单
[critical]｜[14]｜DOI Crossref/OpenAlex 双 404，Meng 组 HHG 论文清单亦无此文，疑虚构｜检索真身后重录，可换 10.1073/pnas.2316775121
[critical]｜[17]｜DOI 110.064428 解析为 Nakane 金刚石 NV 声子自旋文，非 Amato 光致反铁磁｜改 DOI 10.1103/PhysRevB.109.054424
[critical]｜[3]｜DOI …-02540-7 死链；真身 Heide 2024 Nat. Phys. 为 …-02640-8｜末段 02540 改 02640
[critical]｜[9]｜DOI 命中 Du 等 8 人，Zhang/Su/Wang 作者串虚构，页码 1179-1192｜按 Crossref 重录全作者与卷期页
[critical]｜[21]｜DOI 命中 Xiong 等，条目 Xu Y./Kang K. 虚构，页 4758→4254｜按 Crossref 重录作者串与页码
[high]｜[10]｜DOI 命中 Cao/Sun/Meng，条目 Xu Y./Zhou T. 虚构，文号 109→90，题脱 band｜按 Crossref 重录
[high]｜[12]｜二作 Murakami A. 应为 Yuta Murakami；正式发表状态待核｜改 Murakami Y. 并复查期刊版
[high]｜[8]｜PRB 110,115415 实为 Mrudul 独作，Tancogne-Dejean/Rubio 无出处｜删虚构合著者
[medium]｜[25]｜题尾 internal magnetic field 虚构，真题为 Group-VI Dichalcogenides｜按 PRL 正式题重录
[medium]｜[4][5][13][23]｜标题与正式记录不符：[4][5][23]脱词、[13]缩略｜按 Crossref 正式题逐字著录
[medium]｜L67/L71 统计｜2024-26 实 16 篇 61.5% 非 13 篇 50%；DOI 24/26 非 23/26｜按实测重算三段分布
[low]｜[7]｜arXiv 真题含冠词 a（of a twisted…），条目脱词｜补全标题
[low]｜L65｜总引用自述 108（content 33）实测 104（content 31）｜按 grep 复核计数

共 13 项：critical 5 / high 3 / medium 3 / low 2。

## 锚点对比
条目 [9] vs Crossref 10.1038/s41563-024-01951-8：标题"Nonlinear physics of moiré superlattices"逐字一致，但正式作者为 Du, Huang, Zhang J., Ye, Dai, Deng, Zhang G., Sun（8 人），条目所写 Zhang Y./Su Y./Wang L. 前三作者无一命中；正式页码 1179–1192，条目写 844–855。
锚点对比结论：差距明显——"题同名异"式半真实条目比纯虚构更隐蔽，标题可过抽查、作者串一查即穿，正是 R7 教训的池内变体。

## 评分依据
严谨性 0.40：8/26 条（30.8%）作者/DOI/卷期页实质错误（虚构 1+错构 2+死链 1+作者错位 4）；文件自述"R3 约 100 次反查逐条对账"与实测直接矛盾。
完整性 0.88：26 条数量达标（20–40）；2024–26 文献 16 篇（61.5%）时效达标；预检零缺失零死链；扣统计自述失真与凭记忆新条目未回录检索池。

## 对抗结论
是否达标：否。返工优先级：先换 [17][3] 的 DOI（一处更正即修复），再裁决 [14] 存废，随后按 Crossref 重录 [9][21][10][8][12] 作者串。下一轮验收：26 条全量复扫 + 修复须全条目落地（同判据残留他行须全章 grep，09-07 教训）。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.40
完整性：0.88
综合评分：0.64
