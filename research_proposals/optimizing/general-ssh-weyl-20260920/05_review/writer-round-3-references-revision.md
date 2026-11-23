# 参考文献轮处置记录（references 轮）

本文件记录本轮对 04_proposal/sections/references.md 的修订处置与核验证据。过程性材料归 05_review/，章节文件只保留申请书正文。

## 一、逐条问题处置

| 编号 | 严重度 | 问题 | 处置 | 状态 |
|---|---|---|---|---|
| R3-01 | high | 全表 45 条，第 5 轮仍超 section_standards 规定的 30–40 条上限 | 裁撤 5 条冗余条目，表收敛至 40 条 | 已解决 |
| R3-02 | high | [16][17][34][35][40][44] 条目尾中文长评注回潮（82–106 字） | 6 条压回一句定位语；另发现 5 条 58–79 字条目同样超标，一并压缩。40 条评注最长 50 中文字 | 已解决 |
| R3-03 | medium | 头注 "全部 43 条" 计数滞后，实为 45 条 | 头注重写为 40 条，并同步复算 2024—2026 年占比 65%、纯预印本占比 35% | 已解决 |
| R3-04 | medium | [6] Bauer、[41] Haldane 未回录 02_literature 检索池 | 两条回录 reading-notes.md，含题名、来源、核心结论、与课题关联、已引用位置 | 已解决 |
| R3-05 | medium | 15 条纯预印本占 33% | 裁撤后为 14 条纯预印本（35%）。逐条经 arXiv API 确认 abs 页无 journal_ref/doi 字段，即尚无刊版可回录，非漏标 | 已消除（性质澄清） |
| R3-06 | low | [43]-[44] 之间缺空行分隔 | 40 条条目统一为条间空行，体例一致 | 已解决 |
| R3-07 | low | 预检来源校验模块 5 条名单 3 条过期 | 本轮改以 DOI + arXiv + 题名三形态对池复核，池外条目一律不写入 | 已解决 |

## 二、裁撤清单与论证覆盖对照

裁撤的 5 条均为被保留条目已覆盖的冗余条目，裁后无任何独有论断丢失：

| 原编号 | 新编号 | 条目 | 裁撤理由 |
|---|---|---|---|
| [8] | — | Pooyan 与 Bauer，SSH 电子-电子关联稳健性 | 由 refs [6][7] 的边界态增强源覆盖；SSH 方法学链条保留 [6][7][8→原9][9→原10][10→原11] |
| [14] | — | de las Heras 等，RhSi 阿秒局部手性光合成 | 其"手性映射与拓扑无关"的警示由 refs [11][13][29] 的对称性归因与宇称依赖方向性规则覆盖 |
| [23] | — | Fan 等，二维半导体双圆偏振产额曲线 | 其 Berry 曲率—速度竞争结论由 refs [11][17][29][30] 覆盖 |
| [27] | — | 白亚等，Bi₂Se₃ 带间 Berry 相位读出 | 由 refs [23][30][37] 的 Berry 相位读出链覆盖 |
| [32] | — | 马辰俊等，转角 hBN 谐波相位匹配 | 属转换效率工程化，与拓扑探针主线不同；且在 content 与 scheme 两章均无引用 |

国内现状段落（rationale §2.4）裁后保留三条国内锚点：彭良友团队 β-WP₂ 理论分析 [20]、Faeyrman 团队 MgO 动态复 Berry 相 [23]、吕扬洋团队 β-WP₂ 实验 [38]。

## 三、编号迁移

45 → 40 条为全量迁移，四章正文角标同步重映射。全部角标经程序复核：

- 角标总数 186 处（rationale 39、content 42、scheme 72、full_review 33）
- 孤儿（正文引用但表中无对应）0 条
- 幽灵（表中列出但正文未引用）0 条
- 表内编号连续 1–40，无跳号
- 裁撤条目对应的叙述段落一并删除或改写（如 rationale §2.2 的 Pooyan 句、§2.3 的 de las Heras 段、§2.4 的半导体所/白亚/转角 hBN 三段；content §2.1 的 Pooyan 句、§2.4 的 de las Heras 句；full_review 统一表述表的"国内现状条目"行与"转角 hBN 相位匹配"行）

## 四、字段级核验证据

引用真实性红线（零容忍）逐字段核对：

- **26 条含 DOI 条目**：CrossRef works API 全量反查，题名、刊名、卷、页/文章号、年份五件套逐条一致，零错挂。
- **14 条纯预印本条目**：arXiv API 批量取 id/title/authors/category/published，题名、作者链、分类、年份逐条一致。
- **题名版本选择**：凡有刊版的条目一律采用刊版题名而非 arXiv 预印本题名，包括 [27] Klimmer（刊版 "Probing Ultrafast Coherent Bandgap Modulation in Monolayer WSe₂ by Nonlinear Optics"，arXiv 版题名不同）、[39] Yue–Gaarde（刊版 "Structure gauges and laser gauges for…"，arXiv 版为 "Structure- and laser-gauges for…"）、[22] Jessen（刊版无冠词 "Interplay between…"，arXiv 版有冠词 "The interplay between…"）。
- **在线发表条目**：[30] Tornow 为 Nat. Photon. 在线发表，CrossRef 尚无卷页，条目按在线发表体例著录。
- **年份口径**：以刊版年为准，[1] Nat. Phys. 7, 138–141 (2011) 与 [15] Nat. Phys. 13, 345–349 (2017) 的 CrossRef issued 字段为在线首发年（2010/2016），条目采用卷期归属年，与 CrossRef published-print 一致。
- **[8] 题名更正**：arXiv abs 页题名为 "...Su-Schrieffer-Heeger models"（复数），本轮据 arXiv API 原样采用，未作改写。
- **作者链**：40 条全列作者，无 et al. 截断。

## 五、历史遗留 P0 状态

| P0 | 归属 | 状态 | 结论 |
|---|---|---|---|
| 布居方程虚数项（scheme §2.1） | full_review | 待解决 | **已消除**。程序化复核四章，旧式 "−(i/ħ)E·[dρ−ρd]" 形式命中 0 处；scheme §2.1 现为 $\dot{\rho}_{nn}=\frac{2}{\hbar}\mathbf{E}\cdot\sum_{m\neq n}\mathrm{Im}[\mathbf{d}_{nm}\rho_{mn}]$，右端为实数，与 $\rho_{nn}$ 实数性自洽；full_review 统一表述表"SBE 引擎构成"行载有同一规范形式，与 reading-notes 记录的 Yue–Gaarde 依据一致。相干电流带间项已取 $\sum\mathrm{Im}[\rho_{nm}\mathbf{d}_{mn}]$，不含二次乘积。本轮未作改动即已达标。 |

## 六、本轮一并同步的跨章改动

| 文件 | 改动 | 原因 |
|---|---|---|
| rationale.md | 删 Pooyan 句、de las Heras 段、半导体所段、白亚段及后续段、转角 hBN 段；"这组工作"改"这两项工作"；"五组结果"改"四组结果"；"两条拓展线索"改单线索 | 裁撤条目对应叙述删除/改写 |
| content.md | 删 Pooyan 句、de las Heras 句；"三条线索"改"两条线索"；"这五组结果"改"这四组结果" | 同上 |
| full_review.md | "国内现状条目"行改为 refs [20][23][38]；删"转角 hBN 相位匹配"整行 | 同上；全文骨架仍为 2267 中文字，在 3000 字上限内 |
| 00_research_idea.md | "参考文献 43 条"改"40 条" | 该处计数自 R1 起即滞后（表实际 45 条），本轮按收敛后实际值修正 |
| 04_proposal/params.json | 7 组口径键与 canonical 内的引用编号全部重映射：Lorenzo [20]→[14]、Bera [14]→[10]、Pilch [16]→[12]、Duan [26]→[19]、Neufeld [6]→[3]；对应 note 内的 "refs [20]"→"refs [14]"、"[20] 摘要"→"[14] 摘要"、"[14]（arXiv:2305.02025）"→"[10]（arXiv:2305.02025）"同步更正 | 编号全量迁移后 params.json 的编号锚点全部成为死锚；口径表为跨章单一真相源，须同步。逐条复核后 7 处锚点均指向正确条目（[14]=Lorenzo、[10]=Bera、[12]=Pilch、[19]=Duan、[3]=Neufeld），stale_patterns 26 条正则仍全部可编译且对章节文件零命中 |
| 02_literature/reading-notes.md | 追加本轮引用记录：Bauer [6] 与 Haldane [36] 的池回录 + 裁撤与编号迁移说明 | R3-04 |

方法学手册未由本步骤改动，按 v6.9.60 单一真相源治理归轮末专职 update_method_manual 步骤维护。

## 七、程序化复核结果

| 检查项 | 结果 |
|---|---|
| 表内条目数 / 编号连续性 | 40 / 1–40 连续无跳号 |
| 孤儿角标 / 幽灵条目 | 0 / 0 |
| 条目体例（作者全列、题名、刊、卷页、年、DOI 或 arXiv 至少其一） | 40/40 合规 |
| 评注最长长度 | 50 中文字（上限 50） |
| 条目间空行 | 40/40 一致 |
| 文件纯净性（映射表/核实声明/闭环日志/轮次字样） | 0 命中 |
| 跨章口径表 stale_patterns 扫描（7 组 26 条正则） | 0 命中 |
| 单句 >120 字 | 0（rationale/content/scheme/full_review/references 各章均为 0） |
| 冗余修饰词（显著/重要/系统/良好/成熟/完整/关键/精准/一系列/有效/高效） | 申请书三章合计 12，正处红线 12；本轮增删对计数零影响 |
| 模板句式"为…提供…基础/支撑/途径" | 0 命中 |
| 加粗标记 | references 0；正文三章 0 |
| references.md 越界内容 | 无表格、无过程性记录、无轮次字样 |
