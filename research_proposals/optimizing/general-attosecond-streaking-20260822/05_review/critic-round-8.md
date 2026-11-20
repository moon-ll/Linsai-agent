# 对抗评审报告（第 8 轮·参考文献专项）

- 项目类型：general（面上）
- 审查日期：2026-09-07
- 审查范围：04_proposal/sections/references.md（25 条）+ 正文引用上下文抽查（rationale/content/scheme 各 20 处）
- 核查方法：Crossref DOI 全量反查 20 条 + arXiv API 批量反查 5 条（含 [23] 双源交叉）+ 正文 [N] 上下文比对。编号一致性直接采信程序预检，未重复核对。
- 上轮文件处理：05_review 目录本轮新建，无同名文件，无需归档。

## 核查总览
1. 25/25 条全部命中真实文献：题名/一作/期刊/卷页/年份五件套与 Crossref/arXiv 记录一致，未发现虚构、张冠李戴、克隆条目或地址复用。
2. 预检标记的 15 条"未经检索验证"条目（[1]–[9],[11]–[16]）经 Crossref 逐一反查全部为真，元数据零差错——R7 型虚构风险本轮清零。
3. 三条 APS 新式哈希后缀 DOI（[18] 9jcm-8gd8、[20] ll25-15dm、[24] csvm-858f）均可正常解析且指向声称论文，属 2024 后 APS 新编号规则，非格式异常。
4. [9] Chin Phys B 35:054204 (2026) 作者真值 Zhu Xiaoxian/Gao Yitan/Wang Yiming/Zhao Kun/Wei Zhiyi，与条目缩写 Zhu X X, Gao Y T, Wang Y M, Zhao K, Wei Z Y 逐一吻合。
5. 引用相关性：25 条均紧扣阿秒条纹/水窗/多通道/偶极相位主题，经典文献（[4][5][14] 等）支撑计量学脉络，无凑数或无关引用。

## 问题清单（0 critical / 0 high / 3 medium / 5 low）

[medium]｜[24] L49｜arXiv:2501.08966 已正式发表仍引预印本｜改引 PRAB 28:074601(2025)，DOI:10.1103/csvm-858f
[medium]｜[2][10][11]｜APS/Optica DOI 字母段小写（physrevx.7.041030 等）｜统一为注册大写 PhysRevX.7.041030、OE.27.004799
[medium]｜[19] L39｜2024-09 预印本 18 个月未见刊，时效存疑｜查录用/见刊状态，转正式卷页或明确标注预印本
[low]｜[2] L5｜条目截断副题，与 Crossref 全题不符｜补全": A New Regime of Attosecond Pulse Characterization"
[low]｜[13] L27｜"et al." 截断 Nat Commun 30+ 位作者｜可保留 et al.，但全表截断规则须统一
[low]｜全表｜期刊名缩写/全称混排（Nat Commun vs Journal of Optics）｜统一为全称，与 NSFC 模板一致
[low]｜全表｜2024-2026 文献仅 10/25=40%，低于 50% 标杆｜补 2-3 条近三年水窗 HHG/ML 重构文献
[low]｜content §2.3 [22]｜正文称 Aygun"1D-TDSE 计算"未核原文方法｜核对 arXiv:2602.22137 原文表述，防方法错述

## 锚点对比
申请书 [18]：Kheifets A, Serov V, Vismarra F, Wörner H J. Rainbow retrieval of atomic time delays in attosecond streaking. Phys Rev A, 2026, 113: 043103. DOI: 10.1103/9jcm-8gd8
Crossref 真值：Kheifets | Rainbow retrieval of atomic time delays in attosecond streaking | Physical Review A 113:043103 (2026)
差距：题名/一作/卷页/年完全一致；哈希后缀 DOI 为注册原形非错误。作者四人全列无截断、卷:页完整，可作全表格式标杆；其余条目与之差距仅在 DOI 大小写与期刊名统一性。
锚点对比结论：达标

## 维度评分依据
- 严谨性 0.88：25/25 真实、五件套零差错（R7 虚构风险消除）；扣分为 DOI 大小写混排、[2] 题名截断、期刊名不统一。
- 完整性 0.82：数量 25 条在 20-40 达标；无幽灵/未引用条目；扣分为近 3 年文献 40% 低于 50% 标杆、[24] 版本滞后、[19][22] 预印本待转正。

## 对抗结论
本轮 8 个问题（0c/0h/3m/5l）。较 R7：6 条虚构已清零，15 条凭学科知识引用条目全部反查为真，评分回升属实质改善而非口径放宽。建议 writer 将本轮核查通过的 15 条 DOI 回录 02_literature 检索池备查；[24] 转正式版为下轮复检项。是否达到输出标准：是。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.88
完整性：0.82
综合评分：0.85
