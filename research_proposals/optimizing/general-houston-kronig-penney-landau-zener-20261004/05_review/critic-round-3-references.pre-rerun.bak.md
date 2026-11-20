# 对抗评审报告（第 3 轮 · references 专项）

- 项目类型：general（面上）；课题：houston-kronig-penney-landau-zener
- 审查日期：2026-10-23；范围：04_proposal/sections/references.md 全 34 条（编号 1–36，缺口 [10][16]）
- 方法：28 条 DOI 逐条 CrossRef works/ 反查七字段（题名/首作/二作/刊/年/卷/页），6 条 arXiv 批量 API 反查（题名/首作/见刊信号）；编号一致性采信预检未复核。

## 核查结果概览

- 真实性：34/34 全量反查零虚构、零错挂。R2 全部 critical/high（[12] 虚构重写、[24] 作者链、[16]=[29] 去重、[21][23] 补刊版、[34] 补标识、乱序）已修复并经本轮 CrossRef/arXiv 实测确认。
- 预检点名 20 条"凭知识引用"风险条目全部实测通过。[12] 相似度 0.96 系 CR 题名内嵌 <sub>2</sub> 标记的下标伪影，按首作 Liu+卷期页 22(7):073046 定案通过。
- [28] DOI 10.1038/s41467-026-78716-1 新注册：works/ 端点暂 404，但 doi.org handle 可解析，且 CrossRef 文献库检索命中 Korolev/Lettau/Krishna, Nat. Commun. 17:10954——真实，不立案（新注册 DOI 的 API 索引滞后）。
- 预检修正："[18][19] 未被正文引用"系区间聚合 [18-19]、[18-19,29] 未展开的解析假象——两条在 rationale/content/scheme 均实引；聚合展开后并集 34/34，零孤儿、零幽灵。勿删 [18][19]。
- 相关性：34 条均属固体 HHG/拓扑超快/门控方法学域（[18][19] 为双色场波形门控读取时序的方法学先例，挂靠成立），无不相关条目。
- 数量 34 篇（20–40 达标）；2023+ 文献 15/34 = 44.1%（≥30% 达标）。

## 维度评分
严谨性：0.86（2 med + 4 low：题名单词失真、见刊滞后 2 条、体例 3 处）
完整性：0.88（1 med + 1 low：跳号、时效贴校准线）

## 问题清单

[medium]｜[25] L53｜题名失真：多插"order"，真身为 Imperfect Recollisions in High-Harmonic Generation｜题名逐字改"High-Harmonic Generation"，全串复核
[medium]｜[35][36] L73/L75｜已见刊仍引 arXiv：真身 PRResearch 8,033302(2026)、PRA 109,063109(2024)｜改引刊版卷页，DOI 以 CrossRef 实注为准
[medium]｜全表｜编号跳号 [10][16]，违"连续无跳号"标准（头注自认沿用旧号）｜定稿前连续重编号并全量同步正文 [N]
[low]｜[32] L67｜唯一 et al. 折著条目，与全表全列作者规则互斥｜补全作者链，或头注声明统一折著规则
[low]｜[28][30] L59/L63｜DOI 与 arXiv 并标，违"DOI/arXiv 二选一"体例｜删 arXiv 括注，或头注声明并标规则
[low]｜[28] L59｜挂钩注释"§2.2 与 §2.2"章节号重复笔误｜更正为实际双落点章节（其一疑为方案章）
[low]｜头注 L7｜残留"不得互换/不得作为证据"指令式防错记录｜迁 05_review 处置文件，头注只留体例说明
[low]｜全表｜2023+ 占 44.1%，过 30% 线但低于 50% 校准线｜增补 2–3 篇 2025–2026 固体 HHG 新文献并回录检索池

## 锚点对比

申请书 [25]：`Yue L, Gaarde M B. Imperfect recollisions in high-order harmonic generation in solids. Physical Review Letters, 2020, 124(15): 153204.`
CrossRef 10.1103/PhysRevLett.124.153204：`Imperfect Recollisions in High-Harmonic Generation in Solids`（Yue/Gaarde，PRL 2020, v124, p153204）
锚点结论：作者、刊、卷期页、DOI 全对，唯题名插入"order"一词，属单词级失真而非换文错挂；修复时须整串逐字替换，禁局部改写。

## 对抗结论

- 本轮发现 8 个问题（critical:0, high:0, medium:3, low:5）
- 相比 R2（11 个：critical 2 / high 2 / medium 6 / low 1）：9 项修复经实测确认，时效性 33.3%→44.1% 改善，头注过程记录缩为残留句；无已修复问题回潮
- 是否达到输出标准：是（综合 0.87 ≥ 0.85，high 0，medium 3 恰为上限；三项 medium 清零前不得定稿）
- 返工优先级：[25] 题名 → [35][36] 刊版化 → 跳号重编（置于最后统一执行，避免与正文 [N] 同步冲突）
- 下一轮建议：writer 修复后对本轮三点定向复查；[18][19] 保留勿删；新增文献先回录 02_literature 再入表

## 评分
创新性：N/A
可行性：N/A
严谨性：0.86
完整性：0.88
综合评分：0.87
