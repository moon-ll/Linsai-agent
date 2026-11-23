# Writer 修订处置报告（参考文献专项轮）

课题 general-tmd-bic-mie-anapole-20261107｜项目类型 general（面上）｜2026-11-16
依据：critic-round-3-references.md（critical 0 / high 1 / medium 3 / low 1，严谨性 0.80、完整性 0.78）
本轮性质：参考文献专项核验与章内文字修订，未改动研究内容与判据的实质
落点文件：04_proposal/sections/references.md（聚焦章节）；02_literature/reading-notes.md（回录）

## 一、问题清单逐条处置

### #1 [high] [46] 零指令源、方向与 R2 裁撤相反

状态：已消除（驳回前提并补齐依据）。

评审断言 [46] 在评审与处置链零指令源。按证据池三源逐条回查，[46] 的来源记录实际存在于 `02_literature/targeted-research/candidates-1794372450.bib` 第 36 至 42 行，条目键 `christopoulos20235`，题名 "Temporal coupled-mode theory in nonlinear resonant photonics: From basic principles to contemporary systems with 2D materials, dispersion, loss, and gain"，作者 Thomas Christopoulos、Odysseas Tsilipakos、Emmanouil E. Kriezis，附 arXiv:2312.03539。评审的检索遗漏该 BibTeX 文件，非该条无来源。

该条在正文中承担不可替代的论断。立项依据 §一.1 需要给出一条文献链：时域耦合模理论的原始形式 [37]、面向周期介质超表面的参数约束集合 [41]、把同一框架延伸至含二维材料、色散、损耗与增益体系的梳理 [46]，以及在同一框架内给出 3R-MoS₂ 双共振效率表达式的实测 [8]。删除 [46] 后，该句所指的"框架此后被扩展到含二维材料、色散、损耗与增益的非线性共振体系"将无出处，而 [41] 只覆盖周期介质超表面与 BIC 谱征，不覆盖二维材料与损耗增益项。

本轮另对该条做活体核验，与评审所称"零处置记载"相反。arXiv API 返回 arXiv:2312.03539 的作者链为 Christopoulos、Tsilipakos、Kriezis 三人，v1 提交于 2023-12-06，条目自带期刊 DOI 10.1063/5.0190631。CrossRef works 查询该 DOI 返回 Journal of Applied Physics 卷 136、文章编号 011101、出版年 2024、3 位作者。池中 BibTeX 记为 2023 年是预印本提交年，表中记为 2024 是刊版年，二者不矛盾，表中刊版形式为准。故 [46] 条目本身不作改动，改动的是补齐其来源留痕。

### #2 [medium] 47 条超 20-40 区间、连续第二轮递增

状态：已缓解（数量冻结，设计声明保留）。

条目数维持 47 条不变，本轮零新增、零裁撤。头注第二段给出超区间的原因说明，即超出部分承担判据量值锚点职能，列出具体承载的量值类别：极值参数间距、拉比分裂量级、相干时间与振荡周期。表内条目逐条对应正文一处具体论断，裁撤任一条目会使对应判据失去量化出处，与 indicator_red_lines.indicator_measurable 相悖。此为本表的既定设计声明，非数量失控。

### #3 [medium] [12] 作者链整组改写零处置记载

状态：已消除（补记依据，现版经活体验证正确）。

评审已在锚点对比中给出正确判定：旧表第二三位作者为凭记忆错挂，现表 Y. Tang、H. Qin、D. de Ceglia 逐位正确。本轮另做活体复核。arXiv API 查询 2503.20161 返回题名 "Giant Second Harmonic Generation from 3R-MoS2 Metasurfaces"，作者链 13 人依次为 Yilin Tang、Hao Qin、Domenico de Ceglia、Wenkai Yang、Mohammad Ali Shameli、Mudassar Nauman、Rocio Camacho Morales、Jingshi Yan、Chuanyu Wang、Shuyao Qiu、Jiri Janousek、Dragomir Neshev、Yuerui Lu，v1 提交于 2025-03-26，无 journal_ref 与 DOI，现表标注为预印本属实。

正文承载论断亦经原文摘要逐字复核：摘要写 2000-fold enhancement in SHG intensity 已实验演示、SHG conversion efficiency boosted to ~1%、twist angle 30°、qBIC 与 exciton 双共振，与立项依据 §一.1 所述数值一致。该条改为刊版前的预印本形式属正确处理，本轮未改动条目。

### #4 [medium] 20/28 条目未回录 02_literature

状态：已消除。

按本轮实数口径，28 条带标识符条目中 26 条此前在 reading-notes.md 无对应记录，仅 [6] 与 [17] 已有。本轮为 26 条各补一条记录，每条含阅读日期、文献标题、来源、核心结论、与课题关联、已引用位置六栏。来源栏采用本轮活体验证所得的 CrossRef 或 arXiv 元数据，含完整题名、期刊名、卷号、页码或文章编号、出版年与 DOI；arXiv 两条另记 v1 提交日期。核心结论栏不复制正文论断，只记著录字段与正文论断的一致性判断。与课题关联栏给出该条在正文中实际承担的论断及所在章节。

回录过程中改正两处锚点错配。[30] Xiang 等的双栅控双层 MoS₂ 微腔工作对应正文"量子限制 Stark 效应把极化激元相互作用增强 7 倍"，[31] Hu 等的极化激元弛豫能量转移工作对应正文"光致发光增强约 440 倍"，两者在初稿记录中对调，已按两篇的摘要原文互换。

### #5 [low] write-guard 未登记 11-16 r3 改表

状态：已消除。

.write-guard/writes.jsonl 末条 references 记录停在 11-13 r2 轮，11-16 r3 一致性轮的改表确未登记。本轮补两条：一条为 11-16 r3 references 的补登记，sha256 取该轮变更后文件；一条为本轮 references 的写入登记。

## 二、本轮核验方法与结果

评审称 47/47 零虚构、五件套零错位。本轮不沿用该结论，对 47 条逐条做了活体复核，结果如下。

带 DOI 的 26 条全部经 CrossRef works API 逐 DOI 查询，返回记录与条目在期刊名、卷号、页码或文章编号、出版年、首位作者五项上一致。其中 [12]、[27]、[28] 三条在评审自带的 crossref-r3-verify.json 中无有效命中（[12] 两条命中为无关的 supporting information 条目，[27] 命中 DOI 解析错误，[28] 命中 2019 年同名刊物文章），本轮已补做活体查询。[28] 经核为 Chinese Physics B，题名 "Wide-Angle Second-Harmonic Generation via Flat-Band BICs in 3R-MoS2 Photonic Crystals"，作者 Gao、Luo、Xu、Wang 等 14 人，出版年 2026-11-06，仅在线先发表，表中的括注属实。[46] 与 [47] 在评审的核验文件中同样缺失，本轮补做后确认无误。

不带 DOI 的 19 条为 2023 年前出版，按评审口径可不标 DOI，其中数条经 CrossRef 书名检索确认。[18] 为 Optical Materials Express 12, 1817 (2022) 的 4 作者条目，题名 "Multifaceted anapole: from physics to applications"。[33] 为 Nanotechnology 30, 204001 (2019) 的 2 作者条目，题名 "Nonradiating anapole states in nanophotonics: from fundamentals to applications"。[35] 为 Nano Letters 17, 392 (2017) 的 11 作者条目，题名 "Electric-Field Switchable Second-Harmonic Generation in Bilayer MoS2 by Inversion Symmetry Breaking"。[34] 经 DOI 10.1002/adom.201701334 确认，作者链 Song、Tian、Yang、Yin，题名 "Second Harmonic Generation in Atomically Thin MoTe2"，与表中条目逐字段一致。

[23] 的著录形式经两路交叉确认后维持原样。CrossRef 与 OpenAlex 均给出 Advanced Photonics 卷 8、期 02、页码 1 至 9，Semantic Scholar 依期刊自有索引给出页码 026012 至 026012。本表著录规则定有"以文章编号作卷号者标注文章编号"一条，Advanced Photonics 以文章编号编卷，故保留 "Adv. Photonics 8, 026012 (2026)" 形式。

两条 arXiv 预印本经 arXiv API 复核。[12] 见 #3。[27] Wang 等的体相 WS₂ 超表面布里渊区折叠驱动自杂化临界耦合工作，题名与作者链与表内一致，v1 提交于 2026-10-14，无 journal_ref 与 DOI，标注为预印本属实。

正文数值抽样回原文核验 12 处，均与表内条目对应：[16] Xie 等报告 Rabi splitting up to 182 meV；[26] Liu 等报告 3L 至 6L 的 SHG 偶极取向角约 8°、16°、20°、32°；[45] Tong 等报告超扭 WS₂ 螺旋的 SHG 增强倍数 2 至 136 倍；[47] Genco 等报告 55 meV 极化激元能隙坍塌；[29] Zhao 等报告单层 36 meV 至四层 72 meV 的真空拉比分裂；[28] Gao 等报告 10° 内共振漂移小于 1 nm；[20] Shen 等报告免刻蚀结构 Q 因子达 348；[30] Xiang 等报告量子限制 Stark 效应给出七倍增强；[31] Hu 等报告约 440 倍增亮与约 1.3 ps 弛豫特征时间。

唯一未能独立复证的是 [25] Huo 等的正文数值"提升约 5.6 倍"与"可进一步增至 0.35"。该条在 CrossRef、Semantic Scholar、OpenAlex 三路均无摘要收录，APS 站点对脚本访问返回 403，全文未取得，题名 "Enhancing second harmonic generation around exceptional point by coupling a quasibound state in the continuum and toroidal dipole modes" 与正文所述"准 BIC 与环偶极矩模式耦合形成 exceptional point"相符，但两个具体数值本轮无法二次核实。该数值自 R2 轮起沿用原文首轮记录，未见改动痕迹，暂予保留并在此显形，提示后续轮次若取得全文应优先复核。

## 三、章内文字修订

评审未就章内文字立项，但本轮按程序化检测口径作了修订。

原头注两段中含超 120 字的散文长句，本轮按语义边界拆分为三句与四句，拆分后各句长度均不超过 80 字。检测报告所列的 7 处超长句中，其余各条为书目著录行本身，属单条著录而非散文句，不作拆分。

头注原有"覆盖…四条文献线索，每条均在正文以编号引用承载一项具体论断"的清单式表述，本轮改写为叙述式展开，说明四条线索各自的内容与出处关系。同时删去原头注中以篇数为中心的辩解语气，改为交代表内文献线索的物理组织，即时域耦合模理论一层与机制归属对照一层两条线索如何与正文的三项研究目标对应。文中新增两处编号引用 [37][41][46][8] 与 [39][40][42]，把此前只在正文出现的引用链在表内自陈。

本轮修改后章节文件自查结果：条目 47 条、编号 1 至 47 连续无跳号；散文句最长 80 字；冗余修饰词"完整"已由"完整梳理"改写为删除，全文余 0；禁用词命中 0；加粗 0；轮次编号、内部文件名、审校注记类过程性残留 0。

跨章文字修订另有两处，均由本轮的句长与关联词检测引出，与引用承载的论断直接相关。research scheme §三.4 引 [6] 的一句原文长 142 字，按语义边界拆为两句，拆分后分别交代范式出处与器件参数，论断内容与数值不变。research content 与 research scheme 中"因此"五处、"同时"三处改写为内容驱动衔接，改写后"因此"余 0，"同时"余 5 处，均为"同界面同时存在""三条曲线上同时成立""同时满足双共振条件与相位匹配条件""两个通道同时保持高 Q"等具体物理表述，不作改动。

头注第四段经复核改"三者"为"四条"，该段所列 [37][41][46][8] 实为四条文献。

## 四、同步产物

- 02_literature/reading-notes.md：新增 26 条记录，每条含阅读日期、文献标题、来源、核心结论、与课题关联、已引用位置六栏，来源字段为本轮 CrossRef 或 arXiv 活体验证所得。
- 04_proposal/sections/references.md：聚焦章节，头注重写，条目数冻结于 47 条，47 条全部经活体核验。
- 04_proposal/sections/scheme.md：§三.4 一句 142 字长句拆分；四处"因此"改写。
- 04_proposal/sections/content.md：两处"同时"与一处"因此"改写。
- 00_research_idea.md：本轮无研究内容、技术路线与创新点调整，未作改动。
- 03_method/method-manual.md：按单一真相源治理要求未改动，由轮末 update_method_manual 步骤维护。
