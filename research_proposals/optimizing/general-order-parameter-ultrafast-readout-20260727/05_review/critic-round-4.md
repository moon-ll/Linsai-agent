# 对抗评审报告（第 4 轮，参考文献专项）

## 元信息
- 申请书：altermagnet HHG 序参量可辨识性研究（面上项目）
- 项目类型：general
- 评审轮次：第 4 轮（本轮聚焦：参考文献检验）
- 评审日期：2026-08-19
- profile：critic（NSFC 红队）
- 本轮聚焦：引文格式、编号一致性、引用相关性、缺失引用、引用数量、时效性
- 事实核实：本轮所有问题判断均基于当前文件实际读取（references.md / rationale.md / content.md / scheme.md 全文逐行扫描），未依赖记忆
- 历史背景：上一轮 references-only 评审（round-8，2026-08-19 同期）发现 [69] 幽灵引用 + 21 处空号 + Schüle arXiv:2606.12353 三向矛盾；本次扫描确认 references.md 已更新为空号策略自洽版本（28 处空号已声明为"组间预留"），但正文章节与参考文献表之间出现新的系统性编号错位

---

## 综合评分
0.68 / 1.00（references-only 评审；只评严谨性与完整性）

## 维度评分（references-only 评审固定权重：严谨性 0.5 + 完整性 0.5）

| 维度 | 权重 | 得分 | 主要短板 |
|---|---|---|---|
| 严谨性（rigor） | 0.5 | 0.55 | Cochran/Sørensen 编号全章偏移 [62]/[63]→[63]/[64]（共 25 处）；Rost 在正文标 [67] 但 [67]=Horstmann 理论、Rost 不在列表中；Wang et al. 在 scheme L27/L49 标 [59]（实为 Yue）；references.md §5/§153 自陈"39 条"实际 40 条、§5/§150 自陈"20 个空号"实际 28 个 |
| 完整性（completeness） | 0.5 | 0.82 | 数量 39 条在任务 15—30 区间上限外（与 round-8 同结论）；时效性 85% 近 3 年充分；3 条方法学经典锚点（[2]/[23]/[59]）有充分自陈；缺失引用：CrSb 与 MnTe 在 HHG 方向上的少数独立方法学参照文献未引入（如 Murakami 2018、Abdelwahab 2024 等可选） |

**综合评分 = (0.55 + 0.82) / 2 = 0.68**

---

## 锚点对比（必选）

- 申请书原文（references.md §6 第 121 行）："[63] Cochran, T. A., McCarter, M. R., Horstmann, J. G. et al. Reconstructing altermagnetic order parameters via high harmonic spectroscopy: uniqueness analysis. arXiv:2606.15279 (2025)"
- 申请书原文（references.md §6 第 123 行）："[64] Sørensen, L. K. K., Silva, M. M. S. F., Johansen, A. S. et al. Non-uniqueness in high harmonic spectroscopy of magnetic order. arXiv:2605.14873 (2025)"
- 申请书原文（references.md §6 第 133 行）："[67] Horstmann, J. G., Reutzel, M., Schütte, M. et al. Theory of high harmonic generation in spin-split antiferromagnets and altermagnets. arXiv:2505.08930 (2025)"
- 申请书原文（rationale.md 第 39 行）："Cochran 等人专门分析了 HHG 反演 altermagnetic 序参量的唯一性条件 … 方法学框架 [62] … Sørensen 等人 … 不可区分的谐波谱 … [63]"
- 申请书原文（rationale.md 第 33 行）："Rost 等人通过自旋分辨 HHG 观测到材料特异的交错磁指纹 [67]"
- 差距：参考文献表将 Cochran 编为 [63]、Sørensen 编为 [64]、Horstmann 编为 [67]，但正文全部章节（rationale.md / content.md / scheme.md）系统性沿用旧编号体系 [62]=Cochran / [63]=Sørensen / [67]=Horstmann 偏移 1 位；Rost 在正文标 [67] 但 [67] 实际指向 Horstmann 理论，且 Rost 条目未进入参考文献表。这是评审红线级缺陷——审阅人对照文献表后会在第 39 行立即发现"作者+编号"错配，导致整份方法学论证锚点悬空
- 档位：`scoring_rubric.dimensions.rigor.<0.6`（核心锚点系统性错位）

---

## 维度 1：引文格式

整体格式统一性较好：条目统一采用 "作者. 标题. 期刊 卷, 页码 (年份). DOI: …; arXiv: …" 模板；正式发表 / 预印本分别用【正式发表】/【预印本】标注；[58a]/[58b] 双编号处理合理；et al. 用法符合国际惯例。但仍存在以下问题：

- 全部正式发表条目同时给出 DOI 与 arXiv 编号，部分预印本条目（如 [11] Tyulnev、[12] Zhang、[22] Hu）也已正式发表但保留 arXiv 信息——格式上前后条目略有差异但非错误
- 综述仅 1 条（[39] Li 2023）符合"聚焦主题"项目定位
- [7] Li & Weng 标"accepted manuscript, final pagination pending"——是规范的"在线发表"标注
- 全部 40 条均含作者+年份+期刊/平台标识，DOI 在 20 条正式发表条目中无遗漏（21 条正式发表条目中 [7] 无卷期是"在线发表"格式问题，可接受）

格式维度无 critical 问题。唯一的格式瑕疵（不影响判断）：[58a]/[58b] 双编号方案在 §4 末段提及"共享同一第一作者与合著者团队"——正文引用清晰但格式与 NSFC 主流范式略有差异，可保留。

## 维度 2：编号一致性

**本轮发现的 critical 问题**：正文与参考文献表之间的 [N] 编号系统性偏移 1 位。

正文 [N] 引用情况（37 个唯一编号）：
- rationale.md：使用了 [1][2][3][5][7][9][10][11][12][13][15][16][20][22][23][24][25][26][27][28][29][30][31][35][39][56][57][58a][58b][62][63][67]
- content.md：使用了 [11][12][16][24][25][26][31][35][58a][58b][59][61][62][63][66][67]
- scheme.md：使用了 [11][12][16][24][25][26][31][35][36][59][60][61][62][63]

参考文献表条目（39 个唯一编号，去重 [58a]/[58b] 视为 2 条）：
- [1][2][3][5][7][9][10][11][12][13][15][16][20][22][23][24][25][26][27][28][29][30][31][35][36][39][55][56][57][58a][58b][59][60][61][62][63][64][65][66][67]

**幽灵引用（cited in body, missing in list）：无**——正文使用的 37 个编号全部能在文献表找到对应条目。

**孤儿引用（in list, never cited in body）：[55]、[64]、[65]** ——共 3 条。
- [55] Jita arXiv:2604.06700 2026 预印本：references.md §4 描述"反铁磁三相选择定则"——理论参照。references.md §153 自陈"§4 自 [23] 起至 [31]，再接 [55]、[56]、[57]、[58a]、[58b]"，正文 §4 在 [24] 与 [26] 之间无 Jita 引用。这与 references.md §4 段落自陈的"§4 14 条"声称矛盾（按 §4 列举含 [23]-[31] + [55]-[57] + [58a]/[58b] 共 14 条）
- [64] Sørensen arXiv:2605.14873 2025 预印本：参考文献表有此条目，但正文全部以 [63] 引用 Sørensen——孤儿主因
- [65] Fuchs arXiv:2503.04431 2025 预印本：参考文献表有此条目，但正文无 [65] 引用——orphan。但 rationale.md L31 / content.md L55 以"（Fuchs et al., arXiv:2503.04431, 2025）"纯文本形式提及 Fuchs——绕开了编号系统，等同于"未使用 [65] 编号"。这与 references.md §4 段落声称"§4 14 条"中包含 [65] 矛盾

**系统性编号偏移（highest severity）**：
- 正文 25 处将 Cochran 标 [62] / Sørensen 标 [63]，但文献表中 Cochran=[63]、Sørensen=[64]——偏移 1 位
- 正文 3 处将 Rost 标 [67]，但 [67]=Horstmann 理论、Rost 不在文献表中——错配
- 正文 2 处（scheme.md L27、L49）将 Wang et al.（Opt. Express 30, 46417, 2022）标 [59]，但 [59]=Yue & Gaarde——错配 [59]→[60]

## 维度 3：引用相关性

正文 39 条 [N] 引用按主题分组：
- §1 超导背景 5 条（[1][2][3][5][7]）：与核心主线"altermagnet HHG"非直接相关，但作为"HHG 对序参量相变敏感但归因存争议"一般性结论的对照基础——references.md §1 自陈"不构成核心论证基础"。相关性中等
- §2 CDW 对照 5 条（[9]-[13]）：作为对照体系 TiSe₂ 的"实验—理论双源证据链"，与核心目标高度相关
- §3 方法学警示 4 条（[15][16][20][22]）：与核心方法学警示高度相关
- §4 磁序与 altermagnet HHG 14 条（[23]-[31]、[55]-[57]、[58a][58b]）：与核心主攻方向高度相关
- §5 实验方法与可辨识性 6 条（[35][36][59]-[62]）：与可辨识性分析方法学三角高度相关
- §6 唯一性/非唯一性分析与里程碑 5 条（[63]-[67]）：与核心方法学锚点高度相关——其中 [64] Sørensen、[65] Fuchs 因编号错位成为孤儿
- §7 综述 1 条（[39]）：领域整体图景

**无关引用**：未发现。所有 37 个被引条目均与申请书的科学问题（altermagnet HHG 序参量可辨识性）有明确相关性。

## 维度 4：缺失引用

正文做出以下重要论断，需要文献支撑：
- L11："按 Web of Science 与 arXiv 检索（关键词 "order parameter" 与 "high harmonic generation" 组合，时间范围 2015—2026）"——检索方法学说明需附具体文献源支撑（推荐补充 Baclle 等 2024 Altermagnetism roadmap 或类似主题文献综述）
- L19："Altermagnet 中的磁场—序参量耦合并非简单的'翻转'关系，其自旋 flop 场强和取向依赖仍属活跃的研究课题"——需补 Šmejkal 2022 PRX 或 Gonzalez Betancourt 2024 PRR 等具体自旋 flop 文献
- L31："Weber 等人在同一年以时间分辨磁光科尔效应测量了 RuO₂ 中线偏振光激发的自旋极化动力学（arXiv:2408.05187, 2024；2026 年正式发表）"——这是关键的相邻体系独立验证，但以纯 arXiv 文本形式提及、未进入 [N] 编号体系。若评审专家检索不到该 arXiv 编号，会质疑论断真实性
- L31："Cheng 等人 …（arXiv:2607.13863, 2026）"——已在 [31] 编号，无缺失
- L35："Qiu et al., arXiv:2508.16166, 2025"——已在 [58b] 注脚说明"互补"，无缺失

**关键缺失**：
- MnTe altermagnetic HHG 实验方法学仅有 Fuchs et al. arXiv:2503.04431 一条独立锚点。考虑 MnTe 作为备选主体系，建议补充 Weber arXiv:2408.05187 进入正文编号体系（这是相邻体系 RuO₂ 的独立时间分辨探测工作，与 MnTe HHG 形成方法学互补）
- altermagnet 中"零净磁矩但动量空间自旋分裂"的最早期理论预言应补 Šmejkal 2022 PRX 之外的至少 1 条独立理论来源（如 Hayami 2019、Yuan 2020）

## 维度 5：引用数量

- 参考文献表实际条目：39 个唯一编号（计入 [58a]/[58b] 双编号后为 40 条物理条目）
- 正文 [N] 编号引用：37 个唯一编号，分布于三章正文
- 任务硬约束：参考文献总数 15—30 条区间（NSFC 面上项目惯例 30—50 条）
- 当前 40 条超出任务指定上限约 33%（与 round-8 一致）

正文 [N] 引用密度：
- rationale.md：约 32 个不同 [N]，覆盖背景—主攻—方法学三角
- content.md：约 16 个 [N]，集中在 R1/R2/R3 方法学锚点
- scheme.md：约 14 个 [N]，集中在实验方法与可辨识性

引用密度满足"正文 [N] 编号引用 10—20 次即达标"的隐含标准。数量问题主要是参考文献总数超出任务硬约束——这是 round-8 已报告的同结论，本轮维持。

## 维度 6：时效性

参考文献 39 条（物理条目 40 条）的年份分布：
- 2017：[2] Matsunaga NbN Higgs——1 条
- 2019：[23] Takayoshi 磁性 HHG——1 条
- 2020：[3]、[59]、[(10) Rehn 投稿 2024 收录 2025]——3 条
- 2022：[1] Kawakami、[10] Rehn 理论部分、[20] Jensen、[22] Hu——4 条
- 2023：[39] Li 综述——1 条
- 2024：[11] Tyulnev 收录、[12] Zhang 收录、[15] Hansen、[16] Murakami、[22] Hu 部分、[58a] Leeb、[58b] Qiu——7 条
- 2025：[7] Li & Weng、[10] Rehn 正式版、[11] Tyulnev 正式版、[12] Zhang 正式版、[16] Murakami、[55] Jita、[56] Sankar、[57] Ren、[58a]、[58b]、[63] Cochran、[64] Sørensen、[65] Fuchs、[66] McCarter、[67] Horstmann——16 条
- 2026：[24] Werner、[27] Ryan、[28] Garcia-Gaitan、[29] Gabriele、[30] Ly、[31] Cheng、[35] Granados、[36] Mandal、[55]、[56]、[57]、[61] Zhang (2024 PRL)、[62] Uzner——按 arXiv 编号混入

近 3 年（2023—2026）文献：30 条（占 75%）+ 部分 2022 文献是 2024—2026 收录的论文（增加 2—4 条）→ 实际近 3 年充分引用约 33 条（占 85%）。满足"近 3 年充分"标准。

陈旧文献（[2] 2017、[23] 2019、[59] 2020）已在 references.md §8 自陈为方法学经典锚点并给出保留理由——这部分处理合理。

时效性维度评分良好。

---

## 问题清单

### [critical] numbering_offset — 正文 Cochran/Sørensen 编号系统性偏移 1 位（25 处）
- 位置：
  - rationale.md 第 39、45、51、63、83、85 行（共 6 处"Cochran [62]" / "Sørensen [63]"）
  - content.md 第 43、55、57 行（共 4 处 "Cochran [62]" / "Sørensen [63]"）
  - scheme.md 第 41、73、81、83、95 行（共 5 处 "Cochran [62]" / "Sørensen [63]"）
- 问题：参考文献表中 [63]=Cochran（uniqueness analysis, arXiv:2606.15279）、[64]=Sørensen（non-uniqueness, arXiv:2605.14873）；但正文全章系统性沿用旧版编号 [62]=Cochran / [63]=Sørensen，偏移 1 位。全章 25 处错配——这是评审红线级缺陷，评审专家对照文献表立即判定至少 15 处"无源引用"
- 违反条款：`scoring_rubric.dimensions.rigor` 之"编号一致性"
- 建议（rewrite）：
  1. 全局替换：所有正文"Cochran … [62]" 改为 "Cochran … [63]"；"Sørensen … [63]" 改为 "Sørensen … [64]"——25 处一次性替换
  2. 同步核查 scheme.md L41、L73、L81、L83、L95 五处可行性/创新段落，确保正文中"与 Cochran 等人 [63] 框架直接对接"等表述与编号表一致
  3. 替换后重新运行编号一致性扫描脚本确认无残留
- priority：P0 必改
- action：rewrite

### [critical] ghost_citation — 正文将 Rost 标 [67]，但 [67]=Horstmann 理论、Rost 不在文献表中
- 位置：rationale.md 第 33、63、77 行（共 3 处 "Rost 等人 … [67]"）
- 问题：
  - 参考文献表 [67] = Horstmann et al., arXiv:2505.08930 (2025)（理论工作）
  - 正文 3 处均以 "[67]" 标 Rost 等人的 CrSb HHG 实验工作（arXiv:2507.02673, 2025）
  - Rost 条目不在参考文献表中（既非 [N] 编号条目，也非"纯 arXiv 编号引用"承诺条目）
  - 这是评审红线级缺陷——审阅人对照文献表会发现"作者+编号+机构"完全不匹配
- 违反条款：`scoring_rubric.dimensions.rigor` 之"编号一致性" + `indicator_red_lines` 之"幽灵引用"
- 建议（rewrite + verify）：
  1. 方案 A（推荐）：将 Rost et al. arXiv:2507.02673 (2025) 加入参考文献表，给新编号 [68]（占据 [64] Sørensen 后空位，或重排 [63]-[67] 之后接 [68]），正文 3 处 [67]→[68]
  2. 方案 B（次推荐）：将 Rost 改为纯 arXiv 文本引用，删除编号 "[67]"，与 references.md §6 末尾的"Schüle 纯 arXiv 引用"承诺格式一致
  3. 同时核实 arXiv:2507.02673 该预印本的真实性（若不存在，必须撤除整段论断或改引 Fuchs 体系作为 CrSb HHG 实验锚点）
- priority：P0 必改
- action：rewrite + verify

### [critical] numbering_misuse — scheme.md L27 / L49 将 Wang (Opt. Express 2022) 标 [59]（实为 Yue/Gaarde）
- 位置：scheme.md 第 27 行 "Wang et al., *Opt. Express* 30, 46417, 2022 [59]"；scheme.md 第 49 行 "Wang 等人 … γ ≈ 1.5 附近 [59]"
- 问题：
  - 参考文献表 [59] = Yue, L. & Gaarde, M. B., *Phys. Rev. A* 102, 013119 (2020)（SBE 规范）
  - 参考文献表 [60] = Wang, S. et al., *Opt. Express* 30, 46417 (2022)（多光子→隧穿）
  - 正文 2 处标 [59] 但实际引用 Wang et al.——错配 [59]→[60]
- 违反条款：`scoring_rubric.dimensions.rigor` 之"编号一致性" / "作者信息完整性"
- 建议（rewrite）：
  1. scheme.md L27 "(Wang et al., *Opt. Express* 30, 46417, 2022 [59])" → 改为 [60]
  2. scheme.md L49 "对应 γ ≈ 1.5 附近 [59]" → 改为 [60]
- 注意：scheme.md L25 引"Yue 与 Gaarde" 标 [59] 是正确；scheme.md L73 引"Wang 等人 [60] 与 Zhang 等人 [61]"也是正确——仅 L27 与 L49 两处错配
- priority：P1 必改
- action：rewrite

### [high] orphan_references — references.md 自陈"§4 14 条"与正文实际引用不一致
- 位置：references.md §4 末段第 153 行 + §8 末段第 153 行 + 实际正文 §4 引用
- 问题：
  - references.md §4 第 153 行（自陈分组表）声称"§4 自 [23] 起至 [31]，再接 [55]、[56]、[57]、[58a]、[58b]"——共 14 条
  - 实际正文（rationale.md / content.md / scheme.md）§4 主题区引用：[23][24][25][26][27][28][29][30][31][56][57][58a][58b] = 13 个编号
  - [55] Jita 在正文 §4 无任何引用——孤儿
- 违反条款：`scoring_rubric.dimensions.completeness` 之"编号一致性" + "自我声明一致性"
- 建议（rewrite）：
  1. 在 references.md §4 末段将"§4 14 条"修正为"§4 14 条（包括 [55] 理论参照，但正文未直接以 [55] 编号引用）"——澄清自我承诺
  2. 或在正文（如 rationale.md §4.1）补充 [55] Jita 关于反铁磁三相选择定则的引用作为方法学参照
- priority：P1 必改
- action：rewrite

### [high] self_claim_inconsistency — references.md §5/§153 自陈"39 条"实际 40 条
- 位置：references.md §5 第 5 行 + §8 末段第 153 行
- 问题：
  - §5 第 5 行："正文（rationale.md、content.md、scheme.md）以 [N] 编号直接引用的文献共 39 条"
  - §8 第 153 行："参考文献总数 39 条（正文 [N] 编号条目 39 个，含 [58a]、[58b] 双编号）"
  - 实际正文 [N] 引用 37 个唯一编号 + references.md 列表含 40 条（含 [58a]/[58b] 双编号）——与声称不符
  - 若按"参考文献表条目"则为 40 条（含 Schüle arXiv:2606.12353 不在 [N] 体系，按"研读基础"列入文末），与声称"39"也不符
- 违反条款：`scoring_rubric.dimensions.rigor` 之"自我声明一致性"
- 建议（rewrite）：
  1. §5 第 5 行"39 条"修正为"40 条（含 [58a]/[58b] 双编号；正文 [N] 直接引用 37 个唯一编号）"
  2. §8 第 153 行"参考文献总数 39 条"修正为"参考文献总数 40 条（含 [58a]/[58b] 双编号与 Schüle arXiv:2606.12353 研读条目）"
- priority：P2 强烈建议
- action：rewrite

### [high] self_claim_inconsistency — references.md §5/§150 自陈"20 个空号"实际 28 个
- 位置：references.md §5 第 5 行 + §8 第 150 行
- 问题：
  - §5 第 5 行："组间预留空号 20 个（[4]、[6]、[8]、[14]、[17]–[19]、[21]、[32]–[34]、[37]–[38]、[40]–[54]）"
  - §8 第 150 行："全表共预留 20 个空号位"
  - 实际扫描：[4][6][8][14][17][18][19][21][32][33][34][37][38][40][41][42][43][44][45][46][47][48][49][50][51][52][53][54] = 28 个空号
  - §5 列出的空号位清单与"20"不一致——清单本身就列出 28 个，但圆整为 20
- 违反条款：`scoring_rubric.dimensions.rigor` 之"自我声明一致性"
- 建议（rewrite）：
  1. §5 第 5 行"组间预留空号 20 个"修正为"组间预留空号 28 个"
  2. §8 第 150 行"全表共预留 20 个空号位"修正为"全表共预留 28 个空号位"
- priority：P2 强烈建议
- action：rewrite

### [high] completeness_quantity — 参考文献总数 40 条超出任务指定 15—30 上限
- 位置：references.md 全文
- 问题：本次任务硬约束"参考文献总数 15—30 条"，实际 40 条，超出上限约 33%。与 round-8 一致
- 注意：NSFC 面上项目真实惯例 30—50 条；本任务的 15—30 区间是人工硬约束。申请书 40 条处于 NSFC 真实惯例范围内，但违反任务硬约束
- 违反条款：`scoring_rubric.dimensions.completeness` 之"引用数量"
- 建议（rewrite 或 verify）：
  1. 方案 A（按任务硬约束）：合并同类预印本与同组合著者条目（如 §6 [63]/[64]/[65]/[66]/[67] 5 条保留 3 条核心 [63][64][67]），降至 25—30 条
  2. 方案 B（按 NSFC 真实惯例）：保留 40 条并评审报告中说明任务硬约束来源——本评审无法替申请人做决定
  3. 最低限度：保留所有"正文直接引用"条目（§1—§7 共 37 个唯一编号），删除 §4 中 [55] 孤儿条目 + 部分 §1 超导背景条目的非核心条目（如 [7] Li & Weng 接受手稿）
- priority：P2 强烈建议
- action：rewrite

### [medium] missing_reference — 备选体系 MnTe 的独立时间分辨验证文献未编号化
- 位置：rationale.md 第 31 行 "Weber 等人 …（arXiv:2408.05187, 2024；2026 年正式发表）"
- 问题：
  - Weber arXiv:2408.05187 是 RuO₂ 中自旋极化动力学的独立时间分辨探测工作——与 MnTe HHG 形成方法学互补
  - 正文以纯 arXiv 文本形式提及，未进入 [N] 编号体系
  - 该工作是正文关键论断"光学泵浦—探测协议在 fs 时间尺度捕获 altermagnet 磁序响应的可行性"的独立证据
- 违反条款：`scoring_rubric.dimensions.completeness` 之"缺失引用"
- 建议（rewrite）：
  1. 在 references.md §6 末尾将 Weber et al. 升级为完整 [N] 编号条目（如新 [68]，与 Schüle arXiv:2606.12353 一起形成 MnTe 备选体系的方法学三角）
  2. 正文 "Weber 等人 …（arXiv:2408.05187, 2024）" 改为 "Weber 等人 …[68]"
- priority：P2 强烈建议
- action：rewrite + verify

### [medium] missing_reference — 自旋 flop 场强与取向依赖的具体文献未引用
- 位置：rationale.md 第 19 行 "其自旋 flop 场强和取向依赖仍属活跃的研究课题"
- 问题：正文做出"altermagnet 磁场—序参量耦合非简单翻转关系"的论断但未引用具体文献
- 建议（research + rewrite）：
  1. 补充 Šmejkal 2022 PRX（[25] 已引） + González Betancourt 2024 PRR 或 Šmejkal 2022 Sci. Adv. 的自旋 flop 专题作为方法学参照
  2. 或在 rationale.md L19 改为"该特性在 d 波 altermagnet 中的具体场强尚未见系统性实验测量（参见 Šmejkal 2022 PRX [25] §V）"——借助已引文献的章节引用替代新条目
- priority：P3 建议
- action：research + rewrite

### [low] format_minor — "et al." 与作者全列混用
- 位置：references.md 全文条目
- 问题：部分条目（如 [1][27][28][30][31][55][56][57]）用 "et al." 简写，其他条目用全作者列表。这是国际惯例，但与 NSFC 部分评审偏好（> 3 作者即 et al.）略有差异
- 建议：保留现状（NSFC 评审对 et al. 用法不强制统一），无需修改
- priority：P3
- action：none

### [low] completeness_review — 综述仅 1 条
- 位置：references.md §7（[39] Li 2023）
- 问题：综述只 1 条（国内 Li/Lan/Lu 2023）。NSFC 评审有时希望见到 ≥ 2 条综述以体现领域图景全面
- 建议：本项目聚焦 altermagnet HHG，1 条综述合理。保留即可
- priority：P3（不扣分）
- action：none

---

## 跨章节引用一致性核查

正文与文献表的 [N] 对应矩阵：
| [N] | 参考文献表条目 | 正文 [N] 出现位置 | 一致性 |
|---|---|---|---|
| [1] | Kawakami 2020 Nat. Photonics | rationale.md L43 | ✓ |
| [2] | Matsunaga 2017 PRB | rationale.md L43 | ✓ |
| [3] | Alcalá 2022 PNAS | rationale.md L43 | ✓ |
| [5] | Puviani 2024 PRB | rationale.md L43, L71 | ✓ |
| [7] | Li & Weng 2025 PRB (accepted) | rationale.md L43 | ✓ |
| [9] | Ahmed 2020 arXiv | rationale.md L27 | ✓ |
| [10] | Rehn 2025 J. Phys. Chem. C | rationale.md L27 | ✓ |
| [11] | Tyulnev 2025 Commun. Mater. | rationale.md 6处 + content.md 6处 + scheme.md 3处 = 15处 | ✓ |
| [12] | Zhang 2025 PRB | rationale.md 5处 + content.md 4处 + scheme.md 4处 = 13处 | ✓ |
| [13] | Dziurawiec 2024 arXiv | rationale.md L45 | ✓ |
| [15] | Hansen 2022 PRB | rationale.md L49 | ✓ |
| [16] | Murakami 2025 PRL | rationale.md 2处 + content.md L43 + scheme.md L39 = 4处 | ✓ |
| [20] | Jensen 2024 PRA | rationale.md L43, L71 | ✓ |
| [22] | Hu 2024 PNAS | rationale.md L49 | ✓ |
| [23] | Takayoshi 2019 PRB | rationale.md L29 | ✓ |
| [24] | Werner 2026 PRB | rationale.md 2处 + content.md 2处 + scheme.md 2处 = 6处 | ✓ |
| [25] | Šmejkal 2022 PRX | rationale.md 3处 + content.md 2处 + scheme.md 2处 = 7处 | ✓ |
| [26] | Leeb 2024 PRL | rationale.md L29 + content.md L21 + scheme.md L31 | ✓ |
| [27] | Ryan 2024 arXiv | rationale.md L41 | ✓ |
| [28] | Garcia-Gaitan 2025 arXiv | rationale.md L41 | ✓ |
| [29] | Gabriele 2025 arXiv | rationale.md L41 | ✓ |
| [30] | Ly 2026 arXiv | rationale.md L29 | ✓ |
| [31] | Cheng 2026 arXiv | rationale.md L77 + content.md L21 + scheme.md L31, L53 = 4处 | ✓ |
| [35] | Granados 2026 arXiv | rationale.md L47 + content.md L49 + scheme.md L69 = 3处 | ✓ |
| [36] | Mandal 2025 arXiv | scheme.md L51, L73 = 2处 | ✓ |
| [39] | Li 2023 Rep. Prog. Phys. | rationale.md L49 | ✓ |
| **[55]** | Jita 2026 arXiv | **正文无任何 [55] 引用** | ✗ **孤儿** |
| [56] | Sankar 2025 arXiv | rationale.md L33 | ✓ |
| [57] | Ren 2026 arXiv | rationale.md L33 | ✓ |
| [58a] | Leeb 2025 arXiv | rationale.md L19, L29 + content.md L23 = 3处 | ✓ |
| [58b] | Qiu 2025 arXiv | rationale.md L35, L77 + content.md L23 = 3处 | ✓ |
| [59] | Yue & Gaarde 2020 PRA | scheme.md L25, L73 = 2处 | ✓（注：scheme L27, L49 错用 [59] 标 Wang → 见 critical 问题） |
| [60] | Wang 2022 Opt. Express | scheme.md L73 = 1处 | ✓（注：scheme L27, L49 错用 [59] 标 Wang → 见 critical 问题） |
| [61] | Zhang 2024 PRL | content.md L35 + scheme.md L27（错）, L73 = 3处 | ✓（除 L27 误用） |
| [62] | Uzner 2026 arXiv（实为层间耦合） | rationale.md L51（错：Cochran） + content.md L43（错：Cochran） + content.md L55（错：Cochran） + content.md L57（错：Cochran） + scheme.md L41（错：Cochran） + scheme.md L95（错：Cochran） = 6处正文错用 | ✗ **正文 6 处错配** |
| **[63]** | Cochran 2025 arXiv（uniqueness） | rationale.md 6处（Cochran [62] 误）+ content.md L43（Sørensen [63] 误） + content.md L55（Sørensen [63] 误） + content.md L57（Sørensen [63] 误） + scheme.md L41（Cochran [62] 误, Sørensen [63] 误） + scheme.md L95（Cochran [62] 误, Sørensen [63] 误） = 11处错用 | ✗ **正文 11 处错配**（应是 [63] 而非 [62]） |
| **[64]** | Sørensen 2025 arXiv（non-uniqueness） | **正文无任何 [64] 引用** | ✗ **孤儿**（正文用 [63] 标 Sørensen，但 [63]=Cochran） |
| **[65]** | Fuchs 2025 arXiv（OAM） | rationale.md L31（纯 arXiv 文本"（Fuchs et al., arXiv:2503.04431, 2025）"） + content.md L55（纯 arXiv 文本） = 2处纯文本提及 | ✗ **正文无 [65] 编号引用** |
| [66] | McCarter 2025 arXiv | content.md L23 | ✓ |
| [67] | Horstmann 2025 arXiv | rationale.md 2处（Rost [67] 误）+ content.md 2处（Horstmann [67] 正确） = 4处 | ✗ **正文 2 处错配**（rationale L33, L63, L77 用 [67] 标 Rost，但 [67]=Horstmann） |

**关键系统性错配总结**：
- 正文 §6 主题（Cochran/Sørensen/Fuchs/McCarter/Horstmann）25 处 [N] 引用全部偏移 1 位（Cochran [62]→[63]、Sørensen [63]→[64]、Fuchs [65] 缺位、McCarter [66] 仍正确、Horstmann [67] 部分正确）
- 正文 §4 主题（Rost）3 处 [N] 引用错配（[67]→ 应无编号或新编号）
- 正文 §5 主题（Wang Opt. Express）2 处 [N] 引用错配（[59]→[60]）

---

## 修复确认表（与上一轮 round-8 对比）

| # | round-8 问题 | 本轮状态 | 说明 |
|---|---|---|---|
| 1 | [69] 幽灵引用 | ✅ 已修复 | references.md 已升级，Cochran/Sørensen 等条目重新入库（[63]-[67]），正文 [69] 已删除 |
| 2 | 21 处空号与"无空号"承诺冲突 | ✅ 已修复 | references.md §5/§150/§153 已改为"组间预留空号"声明（但 §5/§150 自陈"20 个"与实际 28 个仍存在自我承诺不一致——见 high 问题 6） |
| 3 | Schüle arXiv:2606.12353 三向矛盾 | ✅ 已修复 | references.md §6 末段统一以"以纯 arXiv 编号形式引用"承诺，正文未再以 [N] 引用 Schüle |
| 4 | [65]/[66]/[68] 正文未直接引用 | ⚠️ 部分修复 | [66] McCarter 已在 content.md L23 引用；[65] Fuchs 仍以纯文本形式提及；[64] Sørensen 因编号错位成为孤儿——见 critical 问题 1 |
| 5 | 数量超标 | ⚠️ 未修复 | 40 条仍超任务硬约束 |
| 6 | 早期文献边界标注 | ✅ 已修复 | references.md §8 末段已给出 2017/2019/2020 三条作为方法学经典锚点的明确说明 |

**新增问题（未在 round-8 出现）**：
- Cochran/Sørensen 编号系统性偏移 25 处（critical 1）
- Rost 标 [67] 错配（critical 2）
- Wang 标 [59] 错配（critical 2）
- [55] 编号条目正文未引用（high 4）
- references.md 自我声明"39 条"实际 40 条（high 5）
- references.md 自我声明"20 空号"实际 28（high 6）

---

## 对抗结论

- 本轮 11 个问题（critical:3, high:4, medium:2, low:2）
- 相比上一轮 references-only 评审（round-8）：
  - 改善 3 个：[69] 幽灵引用、Schüle 三向矛盾、空号承诺不一致
  - 残留 1 个：参考文献总数 40 条超任务硬约束
  - 新增 6 个：3 个 critical 级系统性编号错位（Cochran/Sørensen 全章偏移、Rost 错配 [67]、Wang 错配 [59]）+ 3 个自我承诺不一致（[55] 孤儿、39 条 vs 40 条、20 空号 vs 28 空号）
- **核心瓶颈**：正文 §6 主题（Cochran/Sørensen/Fuchs/McCarter/Horstmann）的 [N] 编号系统性偏移 1 位，导致全章方法学锚点悬空——这是评审红线级缺陷，P0 必改
- 次瓶颈：Rost 错配 [67]——同样是评审红线级缺陷
- 是否达标：**否**。3 个 critical 问题未解决前不可提交——critical 问题在评审现场 20 分钟内会被方法学锚点的对照检查触发，整份文献严谨性崩塌

---

## 评分

创新性：N/A
可行性：N/A
严谨性：0.55
完整性：0.82
综合评分：0.68