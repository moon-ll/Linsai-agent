# 对抗评审报告（第 5 轮·整体一致性）— general-berry-mnps3-rashba

聚焦：三章节整体一致性（rationale 5015 / content 3792 / scheme 6964 CJK 字）。项目类型：general（面上）。
前置事实：references.md 29 条表（09-07）+ 三章节（09-09 03:22–04:38）。scheme.md mtime 晚于 scheme 聚焦轮报告（04:11），本轮对 [N] 映射做了全量程序化验收而非沿用上轮结论。标准实际路径 /Users/ll/Desktop/LinSai-CoPilot/memory/nsfc-standards.json；programmatic_checks 与 overall_review_requirements 字段在该文件中不存在，以 section_standards/scoring_rubric/indicator_red_lines/benchmark_anchors/scope_exclusion 为准。

## 执行清单对照

清单0. 通过——三模块齐备：rationale 五层递进（§1.1-1.5）、content 六件套（总述/三内容/目标/关键问题）、scheme 九子模块；研究基础等按 scope_exclusion 不查。
清单1. 通过——已读三章节全文、references 29 条（[N] 映射真值源）、full_review 骨架与 05_review 历史报告。
清单2. 通过——本报告即逐条对照（见上）。
清单3. 通过——2 对锚点见下节，末尾独立结论行。
清单4. 通过——self_reference 14 次列入问题清单 #3（anti_ai）。
清单5. 通过——红队评审叠加全量程序审计：[N] 87 处提取+姓氏-编号全量反查+四类数值口径比对+冗余句逐字比对。
清单6. 通过——三章均为连贯叙述，文献嵌入式引用，无条目堆砌（程序 bullet_list=0）。
清单7. 通过——每条问题附可执行指令与违反条款。
清单8. 通过——critical 1 / high 2 / medium 2 / low 2。

## 锚点对比

对 1（嵌入式引用语体）
申请书原文：Krempaský 等 [5] 用软 X 射线自旋分辨 ARPES 在 MnTe 体系中首次实验观测到交变磁性导致的 Kramers 自旋简并解除。（rationale §1.2 L17）
锚点原文：2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生。
差距：同为"作者[N]+手段+体系+结果"句式，且随句给出劈裂数值（约 100 meV/0.5 eV），数据密度不低于锚点；[N] 映射修复后嵌入有效。

对 2（content 总述段开篇）
申请书原文：本项目围绕立项依据所论证的三重瓶颈展开，主线是强场超快滑移调控与高次谐波谱学读出。（content §2.1 L5）
锚点原文：本项目拟采用理论与实验相结合的研究方法，建立包含局域电子态效应的量子轨迹模型，揭示局域电子态对高次谐波产生过程的影响机理。
差距：同以"本项目+路线+机理"开篇并兑现"问题→路线→机制→产出"四要素；范本单句闭合更紧，申请书以承接句展开后分述，结构同构、密度相当。

锚点对比结论：基本接近

## 写作风格评估

三章均为连贯论述式：文献全部以"某人等[N]+手段+结果"嵌入论证链，无 bullet 堆砌（bullet_list=0、template_phrases=0），段间以内容逻辑衔接；统一口径表 23 项经全量比对无矛盾，方案章"为什么选这个方法"论证密度为全稿最强。短板：一处跨章逐字复述破坏章节独有视角纪律；self_reference 14 次超阈；scheme 跨章指代体例不统一。
程序化检测：self_reference 14（阈值 10/15，penalty 0.05）；transition_words 10/24、redundant_modifiers 9/48、long_sentences severe 1/配额 5、excessive_bold 0、meta_discourse 0 均通过；天花板 0.95。

## 问题清单

[critical] red_line｜rationale §1.2 L23 ↔ scheme §3.3 L29｜Gabriele [26] 判据句两章约 60 字逐字复述｜scheme 侧改写为"如 §1.2 所引 Gabriele 判据，θ 的群论约束即源于二重旋转破缺与 Berry 曲率非零"式指代，不复述论证
论证：程序冗余检测与逐字比对均实锤（含"Gabriele 等 [26]"编号与句式全同）。违反 indicator_red_lines.consistency_check 关联的"无跨章节内容重复"红线及 content_boundaries；R4 同类问题（跨章字面复述）即列 critical，本轮残留此 1 处，须当轮验收。

[high] consistency｜rationale §1.2 L19｜"Liu 等（综述见 [20,21]）"一作实为 Basnet，与 §1.4 L41"Basnet 与 Hu"矛盾｜改为"Basnet 与 Hu [20,21]（MPX₃ 系列综述）"，全稿 grep"Liu 等"复核
[high] anti_ai｜全稿（三章节）｜self_reference 14 次超阈（10/15，扣 0.05）｜压缩"本项目/本方案/本节"句首自指，多数可直接以动词或内容词开头，降至 10 以下
[medium] consistency｜scheme §3.1 L5、§3.2 L17｜跨章指代作"§一/§二"，rationale 与 content 均用"§1.x/§2.x"｜统一为 §1.2/§2.2 式数字编号，全文 grep"§[一二三]"清零
[medium] evidence｜rationale §1.4 L41-43｜四项"国内"归属（[22][24][9][25]）无机构署名佐证｜补机构标识（本轮已反查 [9] 为南京大学团队）或改"华人学者参与"口径，支撑 novelty_claim_cautious
[low] structure｜content 全章｜3792 字低于参考区间下限 4000｜§2.2/§2.4 各补 1 段与研究方案的衔接论证（指代式，非复述）
[low] rigor｜rationale §1.4 L45｜检索声明截止 2026-08，距提交窗口渐近｜定稿前复检四库并更新截止日期，检索式留档备查

已解决核验（历史遗留，基于当前文本实测）：① 正文 [N] 映射三章节全量修复——87 处引用全部落在 1-29、无表外编号、29 条文献全被引用；姓氏-编号全量反查仅 #2 一处错置（此前 R5 遗留的 37+19+23 处错位已清零）。② 周末校准"8 条未引用 [6,10,11,12,21,24,25,28]"已消解。③ R4 references [4][10][11] 题名零命中项：现表 [10] Mazin arXiv:2309.02355、[11] Regmi CoNb₄Se₈（Nat Commun 16:4399）经外部反查为真实文献且内容匹配，[4] 为 Šmejkal PRX 真文。④ full_review 纯净性告警系字节误判：CJK 实测 1172 字 < 3000 上限，内容仅主线链+衔接点+口径表三件套，无需迁移。⑤ 预检 4 项数值差异（fs/K/百分比/meV）均为口径差异非矛盾（fs 为步长 vs 极限、K 为样品环境 vs T_N vs 异质体系、百分比为各指标专属阈值）。⑥ 相关性 2 段均属核心论证，程序误报。

## 评分

是否达到输出标准：否——综合 0.80 < 0.85 门槛，critical 1 + high 2 未清零（max_high_issues=0）；R6 验收 = #1 复述改指代后逐字复检 + #2/#3 修复 + grep 复核。

创新性：0.86（rubric 0.80-0.89 档：谱学指纹反问题+滑移独立动力学变量，与前人区隔清晰、边界显式声明）
可行性：0.86（rubric 0.80-0.89 档：技术路线闭环、三通道辨识与 Z* 核验等难点均有对策与回退，指标有可操作定义）
严谨性：0.68（rubric 0.60-0.69 档：跨章逐字复述 critical + 一作归属错置；指标口径全一致、[N] 映射已修复，故居档内高位）
表达质量：0.78（rubric 0.70-0.79 档：锚点"基本接近"封顶 0.79；self_reference 14 超阈压至档内）

```
## 评分
创新性：0.86
可行性：0.86
严谨性：0.68
表达质量：0.78
综合评分：0.80
```
