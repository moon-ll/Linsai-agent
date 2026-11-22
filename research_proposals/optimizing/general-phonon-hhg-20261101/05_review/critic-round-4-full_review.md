<!-- round-4-sha256 -->
## 评审版本存证（程序化，round-4 同版本复评）
- 被评文件：`04_proposal/sections/full_review.md`
- 评前 sha256：`09768d1beb4a89d00d75eb54c737ef898952149773834c1d2c39546d3fd804ac`
- 评前 mtime：2026-11-06T04:32:58
- 评后复核 sha256：`09768d1beb4a89d00d75eb54c737ef898952149773834c1d2c39546d3fd804ac`（一致）
- 存证写入时间：2026-11-06T06:29:24

# 对抗评审报告（第 4 轮·整体一致性）general-phonon-hhg｜2026-11-06｜聚焦：三章逻辑衔接/术语/冗余/矛盾

## 执行清单对照
清单0. 通过——三章模块齐备：rationale 五层递进；content 总述+3方向+目标+关键问题；scheme 总体+4分方案+消融+可行性+创新+年度+成果；研究基础类按 scope_exclusion 不查
清单1. 通过——三章节与 nsfc-standards.json 实读（md5：rat 6a262397／content 20bf0aa5／scheme e7bb1855）
清单2. 通过——即本清单逐条结论
清单3. 通过——锚点对比见下节，结论独立行
清单4. 通过——程序检测 9 项全 ✓ 零扣分（transition 3/33、模板句 0/8、模板主语 0/5、冗余修饰 17/67、超长句 severe 7≤免赔 7 penalty 0.0、元话语 0/2、加粗 0、列表 0、自指 0），无强制 anti_ai 立项项
清单5. 通过——红队评审完成：6 问题（high 1／medium 5）
清单6. 通过——无文献罗列与条目堆砌；防御句密度约 1.4 处/千字＜2；禁用词表零命中
清单7. 通过——每条附可执行建议与违反条款
清单8. 通过——severity 已分级（P1：问题 1；P2：问题 2-6）
指标预检 7 项：均为口径差异非矛盾——5.7fs=Herling T₂、417fs=CDW 周期、4.5/10fs=抖动/步长、0.42/1.04/1.5ps=调制与剪切模周期、7.3μm=hBN 声子共振、17.5/22.7μm=ZnO 模泵浦、0.8-3.2μm=驱动档、50K=Hatch 跃升/180K=CDW 相界/77-400K=Bose 窗、9.9meV=2.4THz 光子能、12.34eV=U_p@3×10¹³。Keldysh 五档 γ、周期-波数换算、阶次能量、步长占比 0.0096-0.066 经复算全部闭合
相关性复核 8 段（rationale ¶11/19/20/22-26）：均属核心论证或 section_standards 要求的国内现状层，零重叠系中文论证段误报，保留不改
历史遗留 8 条全部已解决：#1 "武汉物理与数学"零命中，L73 已用现名；#2/#5 §4 具名挂 [33,34,27,35,36]（孟胜/郑文洋/汪洋/刘灿东），"国内尚无系统工作"断言已改具名支撑表述；#3/#7 程序 severe 7≤免赔 7，分号切分复核实超 0；#4 scheme §5.4（L167-175）失效边界专段已在，content L11 指针落点实在；#6 content L9 已改"成为…观测对象"；#8 scheme §4.6 L139 核量子效应对照计算落点已挂（σ_ΔR/T₂/√(M_vω)），编号 [49]→[35]

## 锚点对比
对1（rationale_anchor）
申请："2011 年 Ghimire 等人[3]以中红外激光驱动 ZnO 晶体，观测到固体中的非微扰高次谐波产生，随后该现象在半导体、石墨烯与量子点等体系中相继被确认[4-6]。"
锚点："2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生。"
差距：语体与引用嵌入同构，续 [4-6] 收束，论证密度不低于范本。
对2（scheme_anchor）
申请："THz 泵浦用于 1T-TaS₂ 的电荷密度波振幅模（2.4 THz）。其光子能量约 9.9 meV，远低于带隙，不直接产生电子-空穴对，所激发的是该振幅模本身。"
锚点："为了适应本项目的研究，需要在理想晶体的计算中引入杂质的作用，本项目将采用在周期性排布的原子结构中引入少量杂质原子来模拟掺杂半导体。"
差距：同为"为何选此手段"式交代，数值密度（2.4THz/9.9meV/带隙比较）高于范本。
锚点对比结论：达标

## 写作风格评估
连贯段落式行文，引用以"某人等人[N]"嵌入论证链；程序检测 9 项全过零扣分，超长句 severe 7 恰用尽免赔额且分号复核实超 0；防御句约 1.4 处/千字＜2，禁用词零命中。拖累项是跨章复述（问题 1/2）与 1 处谓语悬空（问题 4），属结构而非语体缺陷。程序检测引用：transition_words 3/33✓、template_phrases 0✓、template_subject 0✓、redundant_modifiers 17/67✓、long_sentences penalty 0.0✓、meta_discourse 0✓、excessive_bold 0✓、bullet_list 0✓、self_reference 0✓。

## 问题清单
[high] redundancy｜rationale L89↔content L11、rationale L45↔scheme L197、content L47↔scheme L161/179、content L73↔scheme L171、content L59 χ²式↔scheme L119｜程序冗余指令 5 组经 grep 逐条验证全部在稿，跨章近逐字复述触"无跨章节内容重复"红线｜保留最合适章节一份，他章改"如§X所述"指代｜违反 content_boundaries＋section_coherence
论证：复述系双向越界——content L59/61 复述方案判据体（χ² 全式+σ 不进分母注记），scheme L197 可行性复述立项依据对 [28] 的方法链论证；scheme 11537 字超参考上限与此直接相关，处置令未执行。
[medium] redundancy｜content L61＋scheme L15/L179/L207｜"扣除量不确定度≤残余 30%否则只报告"同一判据四处复述｜目标留结论句、方案 §5.5 留判据体、创新(2)留一句定位｜违反 content_boundaries
[medium] dangling_pointer｜scheme L91｜"份额按研究内容第 3 节方式进入反演"误指，协变量协议实在第 4 节（L45）｜"第 3 节"改"第 4 节（方向三）"｜违反 indicator_red_lines.consistency_check
[medium] expression｜scheme L209｜"这一关系在谐波域尚无实验检验的观测对象"谓语悬空，系 R1#6 同型未同步句｜删"的观测对象"｜违反 rubric.expression
[medium] citation_style｜三章 [N] 共 72 处（rationale 42）｜超 style_benchmark v6.9.9"10-20 次"约 2.4 倍；section_standards"35-47"系旧值与 v6.9.9 冲突，以新校准为准｜非判据挂靠处改作者名行文，[N] 留给先例与判据｜违反 style_benchmark.citation_style
[medium] volume｜scheme 11537 字＞参考上限 10000｜冗余实测命中（问题 1/2），属可压缩超限而非实质性长文｜随去重处置后复测字数｜违反 section_standards.scheme 体量
对抗结论：本轮 6 问题（critical 0／high 1／medium 5）；历史 8 条全部解决；较 R3 新增未执行项=冗余处置令。综合 0.86 达 min_overall 0.85，但 max_high=0（high 1）、max_medium=3（5）均未过→未达输出标准；完成 5 组去重+指针修正+判据并档后复评。

## 评分
创新性：0.86
可行性：0.84
严谨性：0.88
表达质量：0.85
综合评分：0.86
