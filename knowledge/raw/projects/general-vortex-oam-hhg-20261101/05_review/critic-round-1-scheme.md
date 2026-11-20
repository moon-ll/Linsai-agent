# 对抗评审报告（第 1 轮·聚焦 scheme.md）

元信息：general-vortex-oam-hhg-20261101 / general 面上 / 2026-11-06 / critic profile / 本轮聚焦（三）研究方案、特色与创新、预期研究成果。
评审依据：memory/nsfc-standards.json 实读（general 权重 创新.35/可行.29/科学意义.24/表达.12；min_overall 0.85、max_high 0；section_standards.scheme 6 条；scoring_rubric；benchmark_anchors.scheme_anchor+example；anti_ai_patterns；indicator_red_lines）。注：prompt 所引 programmatic_checks/overall_review_requirements 两键在该 json 键名检索零命中，以 writing_style_rules/indicator_red_lines/section_standards 等价条款替代执行。scope_exclusion 生效：不评研究基础/工作条件。
事实核实：scheme.md 经 ls/wc/read_file/md5 四验为 0 字节（md5=d41d8cd9），references.md 同 0 字节；rationale（7816 原始字符）/content（9054）均为成稿。程序化检测"全文字符数 16872"=7816+9054+2 逐符相符，载体实为两成稿章，聚焦章无检测对象。方法学比对：KB briefing-2026-05-30/09-03 载 Rajak 组参数组与 Granados CEP 切换（l_q=5↔6），与 rationale §1.2 口径分列后无冲突；POV 整形、TDSE/SBE 求解器方法卡在库，方案开写有据可支。

## 执行清单对照
清单0. 不通过——标准模块四缺二：scheme.md 与 references.md 均 0 字节（三验空哈希）
清单1. 通过——聚焦文件与标准配置均实读，检测载体溯源完成
清单2. 不通过——section_standards.scheme 六条对 0 字节文件逐条判负，见问题清单
清单3. 通过——已取 scheme_anchor+scheme_example 两锚点对比，见下节
清单4. 不通过——聚焦章无检测对象；载体超长句 7 处超免赔扣 0.06，anti_ai 立案
清单5. 通过——已按 general 标准红队立案并附跨章简查（关键参数 grep 复算无冲突）
清单6. 不通过——narrative 检查在聚焦章无文本载体，与 R1-rationale/content 空稿同型
清单7. 通过——每条问题附 ≤40 字可执行建议并标注违反条款
清单8. 通过——问题按 critical/high/medium 分级并附 P1/P2/P3
历史遗留 1（rationale narrative 无载体）：已解决——rationale 为 20.2KB 成稿（本轮 md5=142c9a95 复验），五层递进齐备，非机械延续。
历史遗留 2（R1-rationale [high] narrative）：已解决——R1-content 报告基于当时文本判"已解决"，本轮复验维持；其新检 2 项属实判。

## 锚点对比
对 1（方法选择论证）：
申请书原文："整数拓扑荷 l_q 由 astigmatic 变换后的亮瓣强度极小值计数给出，其单次读出判定门限优于 ±0.5"（content §二.2）
锚点原文："每个技术选择都有'为什么选这个方法'的论证。"（scheme_anchor）
差距：方法已点名而选择理由与操作流程零载体，scheme.md 0 字，"为何选 astigmatic 而非其他拓扑荷测量"无从评估。
对 2（操作序列）：
申请书原文："研究内容 §二.6 八条目标 → 研究方案各节的'方案→指标'实现路径。"（full_review 衔接点）
锚点原文："首先，求解定态本征值问题获得掺杂半导体的电子能谱及跃迁偶极矩等信息。然后，利用数值方法获得电子演化的含时波函数……"（scheme_example）
差距：范本方案句是可直接开工的操作序列，本稿八条量化目标无一落地为步骤或装置参数。
锚点对比结论：差距明显

## 写作风格评估
聚焦章无文风载体：连贯叙述、"为何选此法"论证、操作流程全部缺位。程序化检测对象实为 rationale+content（16872 字逐符相符，载体错位），超长句 7 处属成稿章存量问题；方案开写即须控句长与关联词，防把 χ²/门限/束腰判据罗列成清单。KB 方法卡在库可支取。
程序化检测结果：全文字符数 16872（=rationale+content）；long_sentences severe 7 处（免赔 4）扣 0.06；transition_words 5/16、template_phrases 1/8、冗余修饰 7/33 均过；表达天花板 0.94。

## 问题清单
[critical(P1)] completeness｜scheme.md 全文｜0 字节，技术路线/特色创新/预期成果整体缺失｜以 content §二.2-§二.5+八条目标为骨架成稿 ≥6000 字实质论证（违 scoring_rubric<0.60 档；占位降档规则）
论证：上游判据与参数齐备（χ²<5.99、束腰 65/40/25/15 μm、η≥0.1、N*≤20%），属可修复结构性缺稿而非质量缺陷。
[critical(P1)] structure｜scheme.md 四要素｜总体方案/技术路线/分方案/可行性分析全缺位｜按 scheme_anchor 写"总体→分方案（物理产出衔接）→可行性"，每法答"为何选它"（违 section_standards.scheme 1-3）
[high(P1)] consistency｜full_review 衔接点→scheme｜"三套分方案""方案→指标路径"两指针指向空章｜scheme 成稿落实编号对应，或骨架暂注"待撰"（违 indicator_red_lines.consistency_check）
[high(P1)] anti_ai｜载体 rationale§1.3/content§二.0｜超长句>120 字 7 处（免赔 4）扣 0.06，载体错位｜拆长句至≤120 字；scheme 开写即控句长（违 anti_ai_patterns；天花板 0.94）
[high(P2)] implementation_path｜content §二.6→scheme｜八条量化指标均无"方案→指标"实现路径｜每条指标在方案章落测量协议/计算式/装置参数（违 indicator_red_lines.implementation_path）
[medium(P2)] verification｜rationale §1.2｜Rajak 强度已补"按聚焦光斑"分列句，6.4e11 出处仍未核｜对照 Rajak 原文复核口径并补出处（违 indicator_red_lines.no_exaggeration）
[medium(P3)] completeness｜references.md｜0 字节，rationale [N]1-34 无对应文献表｜建 30-40 篇表与正文 [N] 一一对应（违 section_standards.references）
[medium(P3)] content_boundary｜content §二.1｜"SBE–传播统一模拟先行完成"属方案时序，前置越界｜该句移入 scheme 技术路线节（违 content_boundaries）

## 档位依据
创新性 0.30——scoring_rubric <0.60 档"无明显创新"：方案侧方法独特性论证零载体；上游三通道可加分解与 l̄_q 设计显露创新内核，取档内偏上值。
可行性 0.10——<0.60 档"关键环节完全缺失"：技术路线、装置、流程、可行性分析整体为零。
严谨性 0.15——五项核查清单过≤1：①数值链②指标可操作③文献真实④逻辑闭环在聚焦章均无载体（④"方法"环断裂），仅⑤模块自洽可判（grep 复算 5.99/≤3%/≤2%/η≥0.1/≤20% 跨章无冲突）；未过项①②④位置=scheme.md。
表达质量 0.10——<0.60 档"结构混乱"：零文本；锚点结论"差距明显"→表达≤0.69、综合≤0.84 双重上限生效。
综合=0.35×0.30+0.29×0.10+0.24×0.15+0.12×0.10=0.182，取 0.18（脚本加权复核）。未达 general 输出标准（0.85，max_high=0）：本轮因内容缺失无法准确评分，先补实质内容再进入正常对抗轮。返工优先级：P0=写出 scheme.md 实稿（四要素+八指标路径+可行性）；P1=拆载体章超长句、补 Rajak 出处。

## 评分
创新性：0.30
可行性：0.10
严谨性：0.15
表达质量：0.10
综合评分：0.18
