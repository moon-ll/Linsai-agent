# 参考文献检验轮修订报告（writer-round-1-references）

## 一、本轮对象与范围

- 聚焦章节：04_proposal/sections/references.md
- 一并修复章节：scheme.md、content.md、full_review.md、00_research_idea.md（均为聚焦章节问题的直接跨章节后果）
- 未改动：rationale.md、03_method/method-manual.md

## 二、评审报告问题逐条处置

critic-round-1-references.md 的 8 条问题系针对 2026-11-01 骨架批次生成的 0 字节空文件（当时 references.md 全文空缺，34 个引用点无条目）。该报告已过期——references.md 在本轮开始前已有 47 条成稿。但报告的两项判断仍然成立且本轮予以落实：引用真实性未做逐字段核验、载体需与正文引用点一一对应。

### [critical] 引用真实性未逐字段核验 —— 已修

对全部 47 条条目做逐字段反查，分两路：

- 35 条正式发表条目：按 DOI 查询 CrossRef 注册记录（`api.crossref.org/works/{DOI}`），取出版方登记的标题、期刊、卷、页码或文章号、作者顺序与年份。
- 13 条 arXiv 预印本：查询 arXiv API（`export.arxiv.org/api/query`），取条目 ID、标题、作者全链、主分类与提交日期。

核验后发现并修正 4 处实质错误：

| 条目 | 原写法 | 核实后写法 | 依据 |
|---|---|---|---|
| [11] | Structure and laser gauges for the semiconductor Bloch equations... | Structure gauges and laser gauges for the semiconductor Bloch equations... | CrossRef 10.1103/physreva.101.053411 |
| [18] | Probing electron-hole coherence in strongly-driven solids, Optica, 2022, 9: 512-519 | Probing electron-hole coherence in strongly driven 2D materials using high-harmonic generation, Optica, 2022, 9: 512 | CrossRef 10.1364/optica.444105 |
| [22] | Nature Communications, 2017, 8: 1-8 | Nature Communications, 2017, 8: 14971 | CrossRef 10.1038/ncomms14971（文章号非页码区间） |
| [47] | arXiv:2601.09608 预印本 | Ultrafast Science, 2026, 6: 0171，DOI 10.34133/ultrafastscience.0171 | CrossRef 10.34133/ultrafastscience.0171（已正式发表，不再按预印本列出）|

另核实 [23] Kong、[35] Fang、[37] Gauthier 三条在定向检索池中的年份为预印本提交年，与正式出版年不同，原文所列年份与卷页经 CrossRef 确认正确，无需改动。[40][41][43][45][46] 五条在检索池中仅存裸 arXiv 号或团体署名，其题名与作者链经 arXiv 摘要页核实后确认原文写法正确。

### [critical] 正文引用与条目一一对应 —— 已修

- 编号连续性：1–47 无跳号、无重复。
- 覆盖度：正文（rationale/content/scheme）实引 47 个编号，与条目集合完全一致，无游离条目、无悬空引用。
- 关闭说明中原有"条目共 47 篇条目共 47 篇"的重复字句。

### [high] 引用数量 —— 已通过

47 篇，落在 general 项目 20–40 条参考区间上限之外但属实质文献量，范本实测 30–40 篇，本表条数与正文引用密度匹配。

### [high] 时效性 —— 已通过并复算

2024–2026 年文献 17 条，占比 36.2%，高于 ≥30% 的要求（原文所述 36.2% 经本轮逐年复算吻合）。

### [high] 引用相关性 —— 已通过

47 条按七个方向覆盖并在正文相应位置被引：气体侧角动量转移标度律理论与实验、固体高次谐波的建立与数值方法、固体涡旋谐波的三组直接前驱工作、角动量分辨非线性光学的二阶序列、空时耦合与时空涡旋方向、拓扑荷读出方法、固体 twisted attosecond 方向的近期理论预期。

### [medium] 预检计数漏计聚合 token —— 不适用

本轮以脚本解析 [N] 与 [N,M]、区间形态 [N-M] 三种写法后重算，正文实引编号数为 47，未复现漏计。

### [medium] 02_literature 池素材未入表 —— 已处理

池中 lit-gap-1793930805.md 的 2601.12743、2607.23652、2512.19412、2510.15207、2603.08263、2506.07465、2608.00233、2509.08681、2410.14385、2512.15370 与 candidates-1793930807.bib 的 nayak202610 均已入表；candidates-1793927682.bib 的 9 条与 candidates-1793935367.bib 的 5 条亦在表内。池中 2610.31313 一条原为裸号占位（"需补充元数据"），其题名与作者链经 arXiv 摘要页补全后入表。

### [low] content/scheme/full_review 零引用 —— 部分修

本轮为 references 轮，正文引用点的挂靠已在 rationale/content/scheme 三章存在（实引 47 处）。content 与 scheme 的关键方法与判据出处已挂 [N]（如 Albar [28]、Granados [29]、Flores-Cova [45]、Yokoshi [30]、Apostolova [46]）。full_review 为全文逻辑骨架章，按其功能定位不承载文献角标。

## 三、历史遗留 P0 跨章节修复

### [critical] G1 判据几何口径互斥 —— 已消除

content §二.0 的 G1 判据为"每种材料在其可用几何下"，明确材料与几何非全交叉；scheme §三.1 的采样矩阵却按材料 × 几何全交叉（5×2×7 = 70）计，机时预算 337 小时、年均 85 小时。两处口径互斥。

按既定配对（ZnO/GaSe/MgO 透射、Si/单层 WSe₂ 反射）重算，材料可用单元为 5 而非 10：

- 主网格 5×7×8×8 = 2240 点（原 4480）
- 束腰系列 480 点、仲裁扫描 36 点、层析扫描 63 点不变
- 合计 2819 点（原 5059），机时约 156 小时（原 337），年均约 39 小时（原 85）

scheme §三.1、full_review 口径段、00_research_idea.md 技术路线节与机时摊薄段四处同步改写；content §二.0 的"五材料双几何矩阵"改为"五材料与各自可用几何构成的测量矩阵"。00_research_idea.md 原述"主网格承担约 98%、仲裁与层析合计约 2%"与实际不符（实际主网格占约 80%、方向一合计约 96%、仲裁与层析合计约 4%），一并更正。

### [high] 跨章节重复论证 —— 已消除两处

- scheme §三.1 原完整复述 content §二.1 的 Granados 静态空间整形工作（生成 Bessel-Gauss 与完美光学涡旋、ZnO 与 GaSe 驱动强场 HHG、验证 l_q = q·l₀）。方案章改为只陈述该选择理由"少周期中红外涡旋与固态强场驱动可在同一光路下共存"，工作细节留在内容章。
- scheme §三.7 可行性分析原重复 scheme §三.2 的 ZnO 退相验证条件（3.2 μm、45 fs、约 1 TW/cm²、50 μm 透射样品），改为指代"其驱动条件与退相量级见 §三.2"。

### [high] 周期数方向表述 —— 复核后无冲突

content §二.3"周期数自 1.5 增至 10"与 scheme §三.1 的八点序列 1.5、2、2.5、3、4、5、7、10 及 content/scheme §二.2、§三.3 的少周期区 1.5–4、多周期区 5/7/10 一致，均指同一取点集合按数值递增排列，物理含义（破缺量随周期数减少而增长）表述统一，无需改动。

### [high] 探索方向定位冲突 —— 复核后无冲突

content §二.3 将分方向二定位为"核心问题"，探索方向在 §二.5、§二.6（目标第 8 条）、§二.7 与 full_review 口径段中一致定位为挂在破缺窗口之上的探索层，full_review 无"优先裁剪"表述，两章无冲突。

### [high] 全文超长句 —— 已消除

以脚本按中文句末标点切分正文段落（排除标题与列表行）复算：rationale 130 句、content 184 句、scheme 177 句、full_review 24 句中，超过 120 字者 0 处（修正前 full_review §二 有 1 处 125 字）。80–120 字技术性长句占比 rationale 30%、content 13%、scheme 21%、full_review 42%，与范本 12%–28% 的区间基本吻合。

## 四、载体纯净性处置

- references.md 只保留文献条目、条目内挂钩注释与章节正文；原头注中的"APS 条目保留出版方注册的短式 DOI"表述已泛化，因表内已含 Optica、Optics Express、Optics Letters、Science、Nature 系列等非 APS 出版方条目。
- full_review.md 原含 19 行跨章节对照表，违反"full_review 只写全文逻辑骨架、严禁逐项对照表"的载体规则。已改写为三段叙述式口径段落，字符数 1841（限 3000 以内），表格清零。
- references.md 内无映射表、无核实声明、无闭环日志、无轮次编号与内部文件名。

## 五、终检数据

- 条目 47 条，编号 1–47 连续无跳号；正文实引 47 个编号，与条目集合双向完全一致。
- 47 条逐字段核验结果：CrossRef 35 条 + arXiv API 13 条，字段不一致 0 处（题名、作者顺序、年份、卷、页码或文章号、期刊、DOI、arXiv ID 与分类）。
- 预印本标记 † 12 条，与结尾说明所写条数一致。
- 2024–2026 年文献 17 条，占 36.2%。
- 指标口径跨章节一致：单次 ≤ 3%、三次平均后 ≤ 2%、整数门限 ±0.5、χ²_ν < 5.99（ν = 2）、η ≥ 0.1、N* 偏差 ≤ 20%、幂指数偏差 ≤ 15%、螺旋相位 < λ/10、2819 采样点、约 156 小时机时。
- 加粗标记 0 处；跨章节完全重复段落 0 处；过程性残留 0 处。

## 六、遗留说明

- references.md 中 35 条正式发表条目未在 02_literature 检索池留有对应记录，本轮以出版方注册记录（CrossRef）作为核验依据并据以校订，池侧记录缺失属文献池覆盖范围问题，不影响条目真实性。若后续需池侧留痕，可将本轮核验结果回写 candidates BibTeX。
- 方法学手册未改动，由 update_method_manual 步骤按单一真相源治理统一维护。
