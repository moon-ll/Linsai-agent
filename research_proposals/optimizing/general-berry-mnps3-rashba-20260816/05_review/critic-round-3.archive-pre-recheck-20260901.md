# 对抗评审报告（第 3 轮 · 聚焦：立项依据 rationale.md 段落级深审）

项目：general-berry-mnps3-rashba-20260816（面上）｜评审日期 2026-08-31
核验：四文件通读、编号-主题比对、Crossref+doi.org+arXiv 反查；round-3 新建无覆盖；标准实读于 CoPilot 根 memory/nsfc-standards.json。

## 0. 核心判断

R2 文献专项后 writer 于 08-27 20:13 重写 references.md（40→28 条，arXiv 伪冒全清、Šmejkal/Werner 修正），文献表质量回升；**但三章正文引用编号完全未同步**——rationale 27 个唯一编号约 17 个错位，另有 5 处空引用槽、3 个悬空编号；18 条 DOI 不过门。语体是范本级，证据链是断的。

## 1. 执行清单对照

- 模块完整性：通过（1.1→1.5 五层齐全）｜读取文件+标准：通过（全文实读）
- 逐条对照：不通过项均落 C1-C5/H1-H5｜锚点对比：完成，"差距明显"（§5）
- 程序化 AI 检测引用：完成（§4）｜红队/风格/建议/分级：完成（critical 5 / high 5 / medium 6 / low 2）

## 2. 修复确认表（R2→R3 实测）

| R2 问题 | 状态 |
|---|---|
| 六条 arXiv 伪冒 | **已解决**（arXiv API 实测五条 ID 标题作者逐字真实） |
| [3] Šmejkal 伪装 Science | **已解决**（现 PRX 12:040501 正确） |
| [19] Werner 页码克隆+缩写 | **已解决**（[15] PRB 110:235101，Crossref 实测） |
| [10] FeCuP₂S₆ 撞车 | 部分解决（条目已删，L13 论断残留，见 C2） |
| [20] García-Gaitán 错配 | 部分解决（条目已删，论述残留错位，见 C1） |
| 21 条期刊待硬门 | **未解决**（本轮实测 18 条不过门，见 C4） |
| R2 首见 content 超长句 13.6% | 改善未解决（句号口径 5/73=6.8%；程序口径仍偏高，再列 H2） |

## 3. 问题清单

### P0（必改）

**C1 [critical] citation_misalignment — 文献表重写后正文编号系统性未同步（本轮最重）**
- 位置：rationale 42 实例/27 编号约 17 错位；content L15 [31,33]、scheme L15 [33,35] 悬空
- 实测样本（论述→列表实为）：L21 Ruiz-Tijerina [17]→Basnet；L23 Ghorashi-Rappe [18]→Yarmohammadi；L23 Werner [19]→Ogawa；L23/45 García-Gaitán [20]→Ezawa；L25 Rajpurohit [21]→López-Alcalá；L25 Yarmohammadi [22]→Basnet；L11 VSe₂ [14]→Yang-Liang；L11 [15]、L21 [16]、L41 [12]/[24][25][26]、L53 [30] 同类；scheme L49/51/65 可行性段引用全失效
- 危害：三条承重证据（Ruiz-Tijerina/Ghorashi-Rappe/García-Gaitán）在列表已不存在而正文仍引用，反查即穿帮
- 违反：section_standards.references"正文有[N]角标与参考文献对应""无张冠李戴"；indicator_red_lines.consistency_check
- 建议：以 28 条列表为真值源对三章约 70 处引用逐一重锚；仍需文献（Ruiz-Tijerina、Ghorashi-Rappe、García-Gaitán 真身、插层三篇）检索真实条目重录；无支撑论断删；改后跑编号-主题比对自检
- action：rewrite + research

**C2 [critical] fabrication_residue — 已删伪文献的论断残留**
- 位置：rationale L13"FeCuP₂S₆ 的研究证明，FEAFM…AFEAFM 相…层间滑移可反转自旋劈裂符号而不翻转 Néel 矢量 [10]"
- 问题：R2 已实锤该证据源不存在并删除；现 [10] 为 Wang h-BN 类双层滑移极化开关，主题全异，论断失去支撑但原文保留
- 违反：indicator_red_lines.no_exaggeration；ai_policy_2026"不得使用未经核实的内容"
- 建议：或检索到 P₂S₆ 族多铁真实文献（含 DOI）重录，或整句删除仅保留 [34] Sheng 真实论述
- action：research + rewrite

**C3 [critical] dangling_citation — 空引用槽 5 处，§1.4 连续三处**
- 位置：rationale L45"高次谐波产生 、反铁磁超快动力学  与强场 Floquet 谷操控 [23]"（两空槽+[23] 错位）；L47"选择定则 与…谷工程 [23]"；content L71"（见文献 ）"；scheme L95"HHG 实验平台 "（悬挂）
- 问题：文献删除后未回填，§1.4 论证链断裂；content L71 空槽位于可证伪表述内（P1"占位符未清"）
- 建议：回填真实国内文献或改写；课题组自引空槽改文字或删
- action：rewrite

**C4 [critical] doi_mismatch — 18 条 DOI 不过门**
- 位置：references.md 全表（Crossref+doi.org 双源实测）
- 404 八条：[4][5][7][8][9][12][14][21]；解析到无关论文十条：[6]→Fabrizio 自旋液体、[11]→Morales-Durán、[13]→Patel（页码亦不符）、[17]→Zhou、[18]→Preimesberger、[19]→Ansari、[20]→Sahoo、[23]→Li、[25]→Luo（页码不符）、[26]→Šipr。可确认真实仅 [1][2][3][10][15]+arXiv 五条（9/28）
- 重点：[8]（平台二地基，三章共引）与 [5][7][9]（§1.1-1.2 承重）均 404
- 违反：section_standards.references"无张冠李戴"
- 建议：18 条逐条硬门三步（Crossref 元数据→doi.org 解析→官网比对文号），查无此文按伪造作废；不符者以真实元数据整条重写
- action：verify + research

**C5 [critical] duplicate_entry — [24] 与 [30] 同文重录且作者拼写不一致**
- 位置：references.md L49/L55 均为 Haque arXiv:2510.00605；实测第三作者 Rajpurohit，[30] 写"Rajpurkar"。附带 content L19"在 MnPS₃ 中观测到"——arXiv 标题仅"a van der Waals antiferromagnet"，材料归属须核实
- 建议：删 [30] 统一锚 [24]，作者名按 arXiv 订正，正文补材料名
- action：remove + rewrite

### P1（强烈建议）

**H1 [high] anti_ai — "为…提供…"全文 27 次（rationale 单章 16），超 15 上限，范本 0 次**
- 位置：rationale L9/L13(3)/L31/L33/L45(3)/L57-L75 等；程序检测 template_phrases 9（窄口径）
- 违反：anti_ai_patterns 模板句式上限 15；style_benchmark.anti_pattern_in_benchmarks
- 建议：保留≤10 处信息实足者，余改具体动词收束（例："…提供了材料基础"→"由此获得零净磁化下多态存储的材料设计原理"）
- action：rewrite

**H2 [high] anti_ai — 超长句 >120 字：程序口径 26 处（免赔 5）；独立复核正文 11-18 处**
- 位置：rationale L9（约 160 字）/L19/L21 为程序点名三例；另 content L19/L41/L49、scheme L11/L31。历史项：content 本轮 5/73 句（vs R2 13.6%）改善未达标，按跨轮纪律再列，severity 维持 [high]
- 违反：anti_ai_patterns"超 120 字属严重超长句"；style_benchmark.sentence_rhythm
- 建议：每句拆 2-3 句，物理数据保留句式重组
- action：rewrite

**H3 [high] red_line — "在国内尚属空白"无国内检索支撑**
- 位置：rationale L47。§1.5 L63 优先权声明合规（有检索范围+截止日期），本句无支撑，属红线漏网
- 违反：indicator_red_lines.novelty_claim_cautious
- 建议：改"据目前检索（CNKI/WoS 国内机构，截止 2026-08），国内尚无将 HHG 指纹反演引入交变磁体的系统工作"
- action：rewrite

**H4 [high] broken_reference — "如上节所析"指向不存在的论证**
- 位置：rationale L35"如上节所析，Rashba 效应与 Berry 曲率响应同属电子时标…"——§1.2 无 Rashba/Berry 时标分层分析，而该判断是研究内容三地基
- 违反：writing_style_rules"各章之间必须逻辑呼应"
- 建议：§1.2 第三阶段末补 2-3 句电子时标 vs 磁序 ps-ns 时标分层论证（引时间分辨实验文献）
- action：rewrite

**H5 [high] verification_gap — 16–40 meV/unitcell 势垒数据归属未核实**
- 位置：五章句均引 [11]——现 [11] 为 Gonzalez-Hernandez 电控自旋劈裂（DOI 亦错配），非势垒源；[34] Sheng 是否逐体系给出 NiCl₂/VS₂/CrSe₂ 势垒未核实；"滑移二维方晶格"概念原文献（Hu 伪冒）已删成无源
- 建议：逐体系核实出处并标注表号；概念补真实定义文献或改写为"层间滑移可调的 T 族多层体系"
- action：verify

### P2/P3（简列）
- M1 [medium] typo："Bery 曲率"2 处（rationale L35、content L47）应 Berry｜M2 [medium] SST-4B、LKSD 缩写未定义
- M3 [medium] anti_ai：破折号插入语 6 对（范本 0；sentence_rhythm 禁用）｜M4 [medium] L5"THz 乃至亚-THz"量级顺序颠倒
- M5 [medium] §1.4 链断裂+4590 字低于下限：须以真实国内文献回填实质论证（与 C3 合并处置）
- M6 [medium] L31"响应时间受限于 MHz"无引文（滑移铁电器件可达 ns 级），需文献或弱化
- L1 [low] [13] 在列未被引用；L2 [low] L61 主谓不谐，"同时"15 次偏密

## 4. 写作风格评估（程序化检测引用）

全文 20505 字符，天花板 0.55——**程序化检测发现AI写作模式，表达质量被强制限制**。template_phrases 9 处超标（阈 8，扣 0.03）；long_sentences severe 26 处（免赔 5，扣 0.42）；transition_words 20 处未越阈（"同时"15 次）；其余四项合规。独立复核：句号切分 >120 字句 18 处（6/5/7），仍显著高于范本（~0）。叙述式骨架良好：五层递进完整、嵌入式引用到位、段间内容衔接、无 bullet 替代论证。anti_ai 已列 H1/H2。表达 0.55=天花板。

## 5. 锚点对比（rationale_example）

① 原文（L21）："Ruiz-Tijerina 等人 [17] 在 Fe₂CoGaTe₂ 中证明，21.79° 扭转可破坏 PT 联合对称性但保留层间反铁磁耦合，实现 i-wave 交变磁性，最大劈裂约 138 meV…"
② 锚点："2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生。"——"作者[N]+手段+对象+结果"四要素齐全且 [9] 反查即真，证据闭环。
③ 差距：(a) 语体同构（达标）；(b) 论证密度——单句塞入扭转角+对称性+机制+数值+能位五层，超范本负荷（与 H2 互为表里）；(c) 数据驱动达标；(d) **引用嵌入——形式嵌入、验证链断裂：[17] 反查为 Basnet NiPS₃（Crossref 实测），"作者↔编号"对应不成立，范本最核心的可验证性缺失**。另 §1.4 L45 三连空槽段证据密度为零，无法支撑"逐步收窄到核心挑战"功能。

锚点对比结论：差距明显
（依据：引用嵌入项崩坏为决定性证据——17/27 编号错位+5 空槽+3 悬空，叠加 anti_ai 超标与 §1.4 残缺，四项无法逐项举证不低于范本。v6.9.25 绑定：表达 ≤0.69、综合 ≤0.84。）

## 6. 评分依据（scoring_rubric 档位）

- 创新性 0.82（0.80-0.89 档：三项创新区隔清晰、检索声明规范；未上 0.90 因属范式组合创新，两个创新点文献地基本轮失守）
- 可行性 0.74（0.70-0.79 档：THz 场强与商用源匹配、Go/No-Go 与降级路径齐备；风险在 [8] 文献 404、H5、Floquet 增强 ≥5 倍无先例）
- 严谨性 0.60（0.60-0.69 档"存在事实错误、关键论证环节缺失"：C1-C5 均落证据链；指标口径本身已一致（10%/50%、d′≥3、D_sep≥0.80、0.3–0.7 MV/cm 四章互洽）；red_line（H3）压至区间下沿）
- 表达质量 0.55（=天花板，与锚点上限取小；叙述式结构本身 0.75 档，被 anti_ai 限档）

## 7. 对抗结论

- 本轮 18 个问题（critical 5, high 5, medium 6, low 2）
- 相比 R2：改善 3（arXiv 伪冒全清、Šmejkal/Werner 修正、content 超长句减半）；新增 5（编号错位系、FeCuP₂S₆ 残留、空引用槽、DOI 不过门、[24]/[30] 重录——均为文献表重写的伴生损伤）；未解决 1（期刊条目硬门）
- 是否达到输出标准：**否**（min_overall 0.85 未达；max_high_issues=0 未达）
- 返工优先级：P0 全部——先 C1 编号重锚（机械操作即消除最大伤害面），同步 C2/C3 处置，再走 C4 硬门
- 下一轮建议聚焦：references.md 复审（验证 C1-C5）+ rationale 复核；文献修复前内容层精修性价比靠后

## 评分
创新性：0.82
可行性：0.74
严谨性：0.60
表达质量：0.55
综合评分：0.68
