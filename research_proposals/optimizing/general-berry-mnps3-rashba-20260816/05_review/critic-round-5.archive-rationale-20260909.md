# 对抗评审报告（第 5 轮）— general-berry-mnps3-rashba

聚焦：（一）立项依据（rationale.md，5089 CJK 字）。项目类型：general（面上）。
评审依据：memory/nsfc-standards.json v6.9.64（实际路径 /Users/ll/Desktop/LinSai-CoPilot/memory/nsfc-standards.json）。

## 执行清单对照

清单0. 通过——rationale/content/scheme/references/full_review 五模块齐备；研究基础按 scope_exclusion 不评。
清单1. 通过——已读取聚焦章全文、29 条参考文献表、content/scheme 交叉段、历史 R3/R4 报告。
清单2. 通过——本段即逐条对照。
清单3. 通过——2 对锚点对比见下节，含独立结论行。
清单4. 通过——程序化检测结果已列入问题清单 #4/#5（anti_ai）。
清单5. 通过——段落级红队评审见问题清单。
清单6. 通过——§1.4 文献罗列已标记（问题 #3/#6）。
清单7. 通过——每条问题附可执行修改指令与违反条款。
清单8. 通过——critical 1 / high 4 / medium 3。

## 锚点对比

对 1（引用嵌入方式）
申请书原文：Krempaský 等 [5] 用软 X 射线自旋分辨 ARPES 在 MnTe 体系中首次实验观测到交变磁性导致的 Kramers 自旋简并解除（§1.2 L17）。
锚点原文：2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生。
差距：同为"人名[N]+手段+体系+结果"嵌入式引用，申请书追加弱/强劈裂机制注解，论证密度不低于范本；该维度达标。

对 2（段间衔接与数据驱动）
申请书原文：现有二维交变磁体的自旋劈裂调控依赖机械滑移、热退火或静电压缩，响应时间受限于 MHz 量级，与 THz 自旋动力学的时间窗口失配（§1.3 L29）。
锚点原文：高次谐波产生是飞秒激光与物质相互作用的高阶非线性、非微扰现象。基于高次谐波光谱的超快探测技术使得在飞秒甚至阿秒尺度上实时探测物质中电子及原子核的微观动力学过程成为可能。
差距：均以物理量对比（MHz vs THz）驱动论证、无关联词堆砌；但申请书以"驱动端的瓶颈。"标签式短句开段，范本以完整陈述句开段，段首节奏略碎；其余段落（L25、L65）衔接质量与范本相当。

锚点对比结论：基本接近

## 写作风格评估

本章整体为连贯叙述式：五层递进（§1.1 大背景→§1.2 脉络→§1.3 三重瓶颈→§1.4 国内现状→§1.5 定位）结构完整，三科学问题收束自然（L63-71），数据驱动密度高（78 K、16-40 meV、0.5 eV、2-3 数量级）。短板集中在 §1.4：两段"作者（期刊，年份）"高密度罗列、超长句、国内/国际内容错位。过渡词仅"同时 7+因此 3"，无 bullet 替代论证，无模板句式/空洞概括句。
程序化检测引用：全文 24233 字符，天花板 0.88；long_sentences severe 6 处（免赔 5，扣 0.02，聚焦章实锤 L41/L43 两处）；self_reference 20 次超阈值 15（扣 0.10，聚焦章"本项目"9 次）；其余 8 项全部通过。

## 问题清单

1. [critical] red_line｜rationale 全章+content+scheme vs references.md｜文献表已重写为 29 条但正文 [N] 全部未同步，约 37 处锚点错位｜以现表为准全量重建映射并逐条核验：Ghorashi→[15]、Werner→[13]、Basnet(Cr-NiPS₃)→[16]、Sheng→[22]、Yarmohammadi→[17]、Gabriele→[26]、Bae→[27]、Rani→[28]、Wang(DL-MD)→[29]；Mavani/Reimers/Regmi/Yang&Liang/Gonzalez-Hernandez/Sheikh/Zhou 7 个无编号锚点补号（Zhou PRL 2024 现表无条目须补）；scheme 中 [30][31][32][33] 共 9 处指向不存在的编号；未引用条目 [6,10,11,12,21,24,25,28] 补引或删除重排。
   论证（critical 专项）：mtime 证据链确凿半迁移态——references.md（Sep 9 12:41 重写，29 条）晚于 scheme（12:24）/content（12:24）/rationale（12:17）。抽样实锤：rationale L21"Werner 等 [14]"→现表 [14]=Ezawa 椭圆二色性预印本；L23"Zhou 等 [22]"→现表 [22]=Sheng 滑移铁电；content"Ezawa [20]"→现表 [20]=Basnet&Hu 综述；scheme"Gabriele 等 [30]"→表止于 [29]。违反 indicator_red_lines.consistency_check 与 section_standards.references"正文有[N]角标与参考文献对应"。评审员任意抽一条即翻车，修复优先级 P0：先建 [N]→条目映射表，再三章联动重排，禁只改报告点名行（memory 教训：writer 修复常漏同判据他行）。

2. [high] rigor｜rationale §1.4 L43/L45｜"国内研究现状"节两段主体为国际工作：L43 自称"国际团队"（Krempaský/Reimers），L45"Stanford 团队"；国内团队机构归属无一明示｜重写 §1.4：Sheng/Liu/Zhou/Wang 等国内工作补机构归属与贡献定位，国际里程碑（Krempaský、Reimers、Stanford THz）移回 §1.2 或删。违反 section_standards.rationale 五层递进之"国内现状"层职责。

3. [high] rigor｜rationale §1.2 L17 ↔ §1.4 L43｜Krempaský"首次观测 Kramers 简并解除"与 Reimers"0.6 eV 劈裂"两处字面级重复论述，跨节冗余｜§1.4 删重，仅保留一句"谱学读出能区/分辨率基准见 §1.2"式回指。违反 writing_style_rules"各章逻辑呼应"与 red_line 隐式重复。

4. [high] anti_ai｜rationale §1.4 L41、L43｜超长句 >120 字全文 6 处超免赔额 5，聚焦章实锤 2 处（L41 Basnet 段、L43 ARPES 段 206 字，独立复核确认）｜按文献单位拆句：每项工作独立成句（≤100 字），冒号总起改为分述。违反 anti_ai_patterns"超长句"与 sentence_rhythm"单句超 120 字必拆分"。

5. [high] anti_ai｜全文档（聚焦章 §1.4/§1.5 为主）｜自引用 20 次超阈值 15（扣 0.10）；聚焦章"本项目"9 次，§1.5 段首"平台一/平台二/范式 A/范式 B"标签式开头密集｜删无信息量主语，段首改内容词开头（如"滑移多层体系承担……"），全章"本项目"压至 5 次以内。违反 anti_ai_patterns"模板主语滥用"。

6. [medium] expression｜rationale §1.4 L41-L45｜"作者（期刊，年份）"式罗列 7 连发，编号引用缺失致论证链断裂（同信息在 §1.2 均有 [N]）｜统一改"某人等 [N] 报道了 X"嵌入式引用，与 §1.2 引用体例对齐。违反 section_standards.rationale"嵌入式论证"条款。

7. [medium] rigor｜rationale §1.1 L5｜"自旋动力学上限可达 THz 乃至亚-THz 频段"上限表述逻辑倒置（亚-THz 低于 THz）｜改"覆盖亚 THz 至 THz 频段"。违反 scoring_rubric.rigor"表述精确"。

8. [medium] structure｜rationale §1.2 L23｜"相邻体系亦有进展"段游离于"三阶段"框架外，与阶段三（L21 超快动力学）主题重叠｜并入 L21 段尾作补充证据，删"亦有进展"过渡句。

历史遗留核对：①R3 P0 跨章"数量级"——已解决，rationale L25/content L33/L35/scheme L39/L51/L65/L75 全部统一为"2-3 个数量级"；②[1][2][5][3] 奠基综述无编号——已解决，L5 [1,2]、L7 [3][4] 且与新表对应正确；③检索声明——已解决，L31"检索范围与截止日期见 §1.4"+L47 四库联合检索声明+L61 回指，三处锚定；④R4 references 33 条错配——旧表已整体重写为 29 条，真实性核验归 references 专轮，但触发本轮 critical #1（正文未同步）；⑤周末校准 8 条未引用 [6,10,11,12,21,24,25,28]——仍存在（与当前未引用集完全一致），并入 critical #1 处理，不重复计分。

## 评分
创新性：0.82
可行性：0.80
严谨性：0.62
表达质量：0.74
综合评分：0.75
