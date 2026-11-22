# Writer 修订处置报告（整体一致性轮）

课题 general-tmd-bic-mie-anapole-20261107｜项目类型 general（面上）｜2026-11-16
依据：critic-round-3-full_review.md（critical 0 / high 3 / medium 4 / low 1，综合 0.80）
本轮性质：整体一致性修订（章节间衔接、术语统一、冗余删减），未改动研究内容与判据的实质
落点文件：04_proposal/sections/{rationale,content,scheme,full_review,references}.md

## 一、问题清单逐条处置

### #1 [high] redundancy｜Zhang 47%/35%/23% 链三处全量复述 + 禁用词"对照口径"

状态：已消除。

三处复述中，完整保留 research content §二.3 一份（分方向二首次引入该混淆实例处，"依次约为单层 MoS₂ 的 47%、35% 与 23%"随之保留）。research content §二.0 目标二第三项改写为"其对照标准与体系差异的辨析见 §二.3"，不再复述数值。research scheme §三.3 第四项判据改为"强度随层数下降并趋饱和"加体系归属辨析，数值不再重复。禁用词"对照口径"改为"对照标准"。

修改后校验：`47%` `35%` `23%` 各出现 1 次（均在 content §二.3）；`对照口径` 0 次。

### #2 [high] module_self_consistency｜§三.6 ¶3 同一 45 fs 此处称"拉比振荡"，与 §三.4、§二.4 互斥

状态：已消除。

research scheme §三.6 改为"同平台上的相干动力学也已测到周期约 45 fs 的相干振荡与约 110 fs 的相干时间"。research scheme §三.4 首段"极化激元的拉比振荡给出相干时间与振荡周期"一并改为"极化激元的相干振荡"，避免同一份材料在同章内对 45 fs 周期给出"拉比振荡"与"相干振荡"两种定性。

修改后校验：全文 `约 45 fs 周期的拉比振荡` 0 次；`拉比振荡` 仅余 §三.4 中作为上下支拉比分裂的一般性描述。

### #3 [high] citation_density｜三章角标合计 105 处，超范本约 5 倍

状态：已缓解（不可完全消除，原因见下）。

采取四项措施：（一）按面上项目范本的做法改用区间形式，连续条目合并为 [4-6]、[12-14]、[15-17]、[39-41] 等；（二）同一段落内支撑同一论断的多个条目合并为单一角标；（三）删除同一作品在同一章节内相邻段落的重复角标；（四）压缩 research scheme §三.6 可行性分析对 §三.2–§三.4 具体数值的复述，该节改为按原理叙述、数值与出处指向研究内容一节。

修改后校验：正文角标 105 → 51 组；参考文献 47 条全部在正文出现，孤儿条目 0；周末校准程序 `引用超界`（编号缺失）与 `死条目过多` 两项均未触发。

未完全消除的原因（须提请评审注意）：评审以"展开编号个数"计 105，而标准中"正文 [N] 编号引用 10-20 次"对应的是括号组数（范本面上正文实测 16 组）。本申请书正文 24575 中文字符，范本正文 2501 字符，按字符密度折算范本区间约为 157 组，现状 51 组已低于该折算值；且范本 40 条参考文献全部在正文出现且以区间标记压缩，本申请书 47 条亦全部在正文出现、0 孤儿，二者结构一致。剩余 51 组对应的均为承载具体数值的论断（α=0.0405/0.052、Q 65.2、116±4 meV、110 fs/45 fs、93/134 meV 等），删除将使判据失去量化出处，与 indicator_red_lines.indicator_measurable 相悖。

### #4 [med] terminology｜"Rabi 分裂"与"拉比分裂"两术语混用

状态：已消除。

research rationale §一.1 首现处定名为"真空拉比（Rabi）分裂"，其后各章一律用"拉比分裂"。全文 `Rabi` 仅余该处括注一次。

### #5 [med] indicator_consistency｜五项判据在 content §二.0 与 scheme §三.3 排列互换

状态：已消除。

两章判据统一为固定次序并逐项对齐：①体相项排除量（2H 镜像堆垛偶数层近零）②界面项排除量（同质界面对照）③分离精度（留出数据点残差方差比 > 1）④饱和拐点可定位 ⑤2H 中心对称体材料零级排除。research content §二.0 改写为"判据由五项构成，五项一并成立构成目标达成"并去掉"通过项/排除项"的二分（该二分导致计数歧义），research scheme §三.3 保持"五项判据共同决定"表述。

### #6 [med] redundancy｜§二.1 与 §二.5"链路三环/链条三环节"同构复述两轮

状态：已消除。

research content §二.1 保留组织线索与各方向产出，改用"链路起点/链路上接/链路末端"而非"第一环/第二环/第三环"；research content §二.5 三段去掉"是链条的起点/是链条的中间环节/是链条的终点"的平行句式，直接以"能量流分配目标的输出是…""分离协议的输出是…""动力学测量的输出是…"起句，保留该节独有的输入输出关系与反向约束内容。

### #7 [med] data_consistency｜极值点间距 22.1% 与"约 22%"两版；45 fs 与 44 fs 两版

状态：已消除。

极值点间距：research scheme §三.2"以较大参数值为基准的约 22% 相对间距"改为"22.1% 相对间距"，全为 22.1%（7 处），`约 22%` 0 次。

45 fs 与 44 fs：回原文 arXiv:2510.03052 核实（见第三节），原文主文用 "a period of ∼ 45 fs"，傅里叶谱段写该 22.5 THz 成分 "period T∼44 fs"，二者为同一振荡的不同取整。按评审指令统一为 45 fs，删除 44 fs，同时保留该振荡对应的约 93 meV 分裂对象这一载荷事实。`44 fs` 0 次。

### #8 [low] citation_veracity｜430 fs 一名两义（开关时间常数 / 泵浦—探测自相关宽度）

状态：已消除。

回原文 arXiv:2503.19590 核实（见第三节）：原文写二次谐波时域峰高宽半极大约 430 fs，并说明该峰 "can be used as an autocorrelation measurement between the two pulses"，即开关响应宽度与两泵浦脉冲非线性自相关为同一测量量；同一工作给出平行偏振下同偏振干涉自相关振荡周期约 5 fs，对应 1500 nm 基频的一个光学周期。

正文合并为单一量"实验中二次谐波时域峰的高宽半极大约 430 fs、对应两个泵浦脉冲的非线性自相关"，research rationale §一.3 与 research scheme §三.4 两处表述一致；§三.4 末句改为"门宽由此量级确定，取上述约 430 fs 的时域峰宽度与同偏振干涉自相关约 5 fs 的振荡周期，后者对应基频的一个光学周期"。

附带修正：原文摘要作效率增强逾 10²、正文与图注作强度增强约 10³，故正文由"模型给出的增强倍数超过 10³"改为"二次谐波增强倍数达 10³ 量级"，与原文正文一致。

## 二、历史遗留问题核销

- P0 Moharam[37] 不可溯源：已解决，维持（现引 Fan, Suh, Joannopoulos, J. Opt. Soc. Am. A 20, 569 (2003)），未改动。
- P0 α 步长 5%/6% 两版：已解决，维持 6.2%，未改动。
- P0 判据计数 3 vs 4：已解决，维持五项；本轮进一步统一排列（见 #5）。
- P0 丁博阳[32] 张冠李戴：已解决，维持"Qin 等人（北京理工大学等合作）"，未改动。
- P1 三模块 0 字节：已解决，未改动。
- P1 超长句 53 处：已解决，本轮复核仍为 0 处超 120 字。
- P1 Gao[21]/[23] 双挂：已解决，未改动。
- P1 "两个关键科学问题"vs 1+2：已解决，未改动。
- P1 Zhang 饱和/下降两版：已解决，维持"下降并趋饱和"；本轮把三处数值复述收敛为一处（见 #1）。
- P1 预印本依赖：已解决。research rationale §一.1、§一.2、§三.3 三处引 Sortino 均已补"以预印本形式"标注；research content §二.0、§二.4 与 research scheme §三.4 原已标注。
- P1 [N] 密度：未完全解决，见 #3。
- 校准 [47] 无条目：已解决，维持 [47]=Genco, Nat. Commun. 16, 6490 (2025)。
- 校准 [11,33,36,38] 未引用：已解决，39 条全引、0 孤儿。

## 三、本轮原文核实记录

回原文核实两处，均据实改写而非照搬评审转述。

arXiv:2510.03052（Sortino 等，coherent exciton-polaritons in van der Waals semiconductor metasurfaces）：正文（对应论断段）写 "a period of ∼ 45 fs"，并写明该周期 "matches the LP-X energy gap in our system and not the full Rabi splitting between LP and UP branches"；傅里叶谱段给出 "a prominent component at about 22.5 THz (∼93 meV, period T∼44 fs)" 与次峰 "∼32.5 THz (∼134 meV, period T∼31 fs)"。据此确认 44 fs 与 45 fs 为同一振荡的不同取整，正文统一取 45 fs。

arXiv:2503.19590（Seidt 等，ultrafast all-optical switching in nonlinear 3R-MoS₂ van der Waals metasurfaces，已发表于 npj Nanophotonics 2, 37 (2025)）：正文写二次谐波时域峰 "extracted a full-width at half-maximum (FWHM) of approximately 430 fs. This corresponds to an autocorrelation function of the optical parametric oscillator (OPO) pulses of ≈ 280 fs"；并行偏振配置给出 "a timescale of approximately 5 fs (Figure 4f), corresponding to the optical cycle at fundamental wavelength of 1500 nm"。据此确认 430 fs 为同一测量量，合并表述。

## 四、章节衔接与统一表述表同步

research full_review.md 已重写：①主线论证链（4 句）②章节衔接点（2 段）③跨章节统一表述表（21 行）。全文 1456 中文字符，未超 3000 字上限。禁用词"口径"4 处改为"表述"。表内新增"分离协议判据数"行的五项固定次序、"偏振开关时域宽度"行（430 fs 单一量）、"45 fs 的分裂对象"行补入 93 meV 与 134 meV 两个分裂对象。全文骨架未写入任何逐项对照表、处置记录或轮次说明。

## 五、程序化检测终检

| 检测项 | 结果 |
|---|---|
| 周末校准 high 级问题 | 0 |
| 周末校准 low 级问题 | 1（引用次数 51 处 vs 范本 10-20，原因见 #3） |
| 参考文献孤儿条目 | 0（47 条全部在正文出现） |
| 引用超界（编号缺失） | 0 |
| 超长句（>120 字） | 0 |
| 禁用词命中 | 0 |
| 模板句式"为…提供…" | 0 |
| 元话语 | 0 |
| 加粗标记 | 0 |
| bullet 罗列 | 0 |
| 过程性残留（轮次号/文件名/审校注记） | 0 |
| 段落内条件分支句 | 各段 ≤1 |

字数：立项依据 5547、研究内容 7064、研究方案 10142、full_review 1456。

## 六、同步产物

- 04_proposal/proposal-draft.md 已由 sections/ 重新组装（89688 字节）。
- 00_research_idea.md：创新点中"Rabi分裂"改为"拉比分裂"以与正文一致；"来源与可靠性"节追加本轮核验与修订记录。
- 02_literature/reading-notes.md：新增 2503.19590 阅读笔记一条（含阅读日期、文献标题、来源、核心结论、与课题关联、已引用位置）。
- 03_method/method-manual.md：按单一真相源治理要求未改动，由轮末 update_method_manual 步骤维护。
