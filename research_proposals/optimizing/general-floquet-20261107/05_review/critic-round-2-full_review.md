# 对抗评审报告（第 2 轮 · 整体一致性审查）

元信息：general-floquet 课题｜面上项目 general｜2026-11-11｜critic profile｜聚焦：rationale/content/scheme 三章节整体一致性（7016/5029/9025 字，均常规区间）｜三章节与 nsfc-standards.json（rubric、red_lines、锚点、general 权重 0.35/0.29/0.24/0.12）均已本轮实读；references 与 full_review 按 prompt 排除范围未审。

## 执行清单对照

清单0. 通过——三模块齐备：rationale 六节（含国内现状/定位）、content 八节（总述/三方向/目标/年度/关键问题/逻辑关联）、scheme 七节（路线/三方案/可行性/创新/成果），模块完整性无缺口。
清单1. 通过——三章节文件与标准 json（section_standards、scoring_rubric、indicator_red_lines、anti_ai_patterns、benchmark_anchors、project_types.general）已实读。
清单2. 通过——本段即逐条对照输出（0-8 共 9 条）。
清单3. 通过——2 对锚点对比见下段，含独立结论行。
清单4. 通过——程序化 AI 检测结果已引用（见写作风格评估段），无立案项。
清单5. 通过——红队立案 8 项（critical 1 / high 4 / medium 3）。
清单6. 通过——行文为连贯叙述式，无条目堆砌、无罗列式文献复述，narrative 类未立案。
清单7. 通过——每项问题附可执行修改建议与所违条款。
清单8. 通过——severity 与 P1/P2 分级均已标注。

## 锚点对比

对1（rationale_anchor：嵌入式引用与定位收束）
申请书原文：本课题不以"圆偏振光在共线磁体中诱导奇宇称劈裂"为立论点。该结论及其命名已由 Zhu 等人 [11] 建立，Huang 等人 [12] 把它推广为普适策略并给出候选体分类。
锚点原文：2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生。
差距：引用嵌入方式（"某人等人[N]+具体贡献"）、数值锚（Ã=0.2 Å⁻¹、ℏω=5 eV、20-40 meV）与由否定引出定位的收束均不低于范本特征。

对2（scheme_anchor：操作链与方法选择论证）
申请书原文：其中 λ = −√3 t² J₁(Ãa/√3)²/ω……这一标度形式是后续判据的数值支点，不作为待验证的假设处理。
锚点原文：首先，求解定态本征值问题获得掺杂半导体的电子能谱及跃迁偶极矩等信息。然后，利用数值方法获得电子演化的含时波函数……
差距：操作链同样逐步可执行，且每步附"为什么取该阶/该近似"的论证（n=1 对取阶理由、LSW 适用区间），论证密度不低于锚点。

锚点对比结论：达标

## 写作风格评估

三章节均为连贯段落式行文，段间以内容逻辑衔接；引用一律"某人等人[N]"嵌入式，未见"A做了X[1]，B做了Y[2]"堆砌；无编号列表替代论证、无元话语、无空洞概括句。残留缺陷为三处跨章复述与一处术语误词（见清单 2/5/6），不构成结构性 AI 味。程序化检测结果：transition_words 11/27（同时 7、因此 4）、template_phrases 0/8、template_subject 0/5、redundant_modifiers 26/55、long_sentences severe 3/免赔 6、meta_discourse 0、excessive_bold 0、bullet_list_substitution 0、self_reference 0——全部通过，无 anti_ai 立案项；skill 禁用词表 grep 零命中。

## 问题清单

[critical] rigor_reference｜rationale §1.4 L79｜"温度驱动的磁振子热霍尔行为 [24, 23]"错挂：[24]=Hasan 金属逆法拉第理论、[23]=Bock Floquet–Magnus 等价性，均非 MnPS₃ 热霍尔文献｜改挂 [19, 21]（Li 温度致相图、Yang 交换收缩热霍尔），删 [24, 23]｜P1（违 rigor 核查③ 文献支撑真实、red_lines.novelty_claim_cautious）

论证：该句位于"平台机会"论证关键位，为 §1.6 L113"光致跳变与已报道的温度致跳变 [21, 23, 24] 在信号层面区分开"提供对照数据支点；挂靠错使区分判据的文献基础虚置。且 [24] 在 L55/L107 挂 Hasan 逆法拉第、L79 挂热霍尔，[23] 在 L25 挂 Bock，同号双主题属系统性错挂。L113 的 [23, 24] 须同步清理。

[high] redundancy｜rationale §1.6 L109 ↔ scheme §3.2 L41｜"2α_so k_F 共振增强＋ω ≈ 0.6τ⁻¹ 极大值"整句跨章近逐字复现，程序已判重复、处置指令未执行｜scheme 侧改"如立项依据 §1.6 所述，窗口避开 2α_so k_F 与 0.6τ⁻¹ 两处共振"，删复述｜P1（违 NSFC 红线"无跨章节内容重复"；历史"三组冗余"残留之一）

[high] cross_consistency｜content §2.5 L56 ↔ scheme §3.4 L77-81｜R ≥ 20 阈值判据两章均只落 MnPSe₃ 电子侧（scheme 磁振子线 L81 无 R 落点），content L7 总目标却把两通道分离方法归入覆盖共线反铁磁体全类｜两章统一注"R 判据在 MnPSe₃ 电子侧复算"，或 scheme 补单层 MnPS₃ 侧 R 落点｜P1（违 indicator_red_lines.implementation_path；历史 R2 遗留残迹）

[high] terminology｜scheme L19/L99/L127｜"判据的主观测量"三处，"主观"系 primary observable 误译，科学语境构成歧义（判据不应"主观"）｜全文统一改"主要观测量"｜P1（违 writing_style_rules 术语准确）

[high] cross_consistency｜rationale §1.2 L47｜"已经覆盖了五项内容"实列仅 4 项（p/f 劈裂与命名、光致轨道霍尔与高陈数相、自旋点群磁振子分类、热霍尔突变标志），L49 又称"这三类工作"，计数词互扰｜L47 按枚举改"四项"，L49"三类"核对指涉｜P2（违 rigor 核查① 计数链一致）

[medium] redundancy｜rationale L115 ↔ content L7；content L33 ↔ scheme L129｜使命句（对称性分析+第一性原理……统一判据体系……定量预言）与"例外暴露为表内矛盾点"论证跨章复述｜content/scheme 侧改"如立项依据/研究内容所述"式指代｜P2（违 content_boundaries 跨章重复；历史残迹）

[medium] cross_consistency｜scheme §3.4 L97｜能量分辨率"须落在 20 至 40 meV 量级以下"以 40 meV 为门，与同句"终端 44 meV 能力同阶"弱冲突（预检 meV 差异项：40 vs 44 同段并用）｜改"须优于 40 meV；终端现能力 44 meV，须再压缩约 10%"｜P2（违 indicator_red_lines.indicator_measurable）

[medium] rigor_definition｜scheme §3.4 L83｜λ 一符两义：相图标定 λ=0.4（Zhang 无量纲耦合）与色散计算 λ=0.2 并用，且同段与归一化光场 Ã 邻近，未注区分｜两处 λ 首现各加限定语（"层间耦合强度 λ"），或后者改记 λ′｜P2（违 rigor 核查② 指标定义可操作）

历史遗留核销（12 项逐条对当前文本核实）：已解决 9——B_eff 量纲（折算式已改 Δ_E,IFE = gμ_B μ₀ M_orb，gμ_B×等效场量纲闭合）；R≥20⇔占比换算（三处均 95%，复算 20/21≈95.2% 自洽）；content 目标三平台两版（已改"载体为 AB′ 堆垛 CrI₃ 双层平台"）；拓扑计算挂单层 MnPS₃（content L41 已显式限定拓扑计算在双层平台）；content §2.1 总述（L7 已列三平台分工）；scheme §3.1 漏双层（L5 已含"破缺 [C₂⊥||ℳ_z] 的 AB′ 堆垛 CrI₃ 双层平台"）；磁致弹性/磁声子两名并存（grep"磁致弹性"零命中，全稿统一"磁声子耦合"）；R 比值方向（R=|Floquet|/|IFE|，与 95% 归因光子缀饰一致）；超长句 28 处（程序复测 severe 3，低于免赔 6）。残留 2——[24,23] 错挂（=清单1，本次升级 critical）；跨章复述两组（=清单2/6，含程序指令未执行项）。未审 1——[1] Smejkal 条目属 references 排除域，由 references 专轮预检覆盖，本轮不重复扣分。

对抗结论：本轮 8 项（critical 1 / high 4 / medium 3），较上轮 12 项遗留：9 已解决、2 残留、1 出域。未达输出标准（综合 0.81 < 0.85 阈值，high 4 > 上限 0），瓶颈为文献挂靠错与 R 判据落点断链。返工优先级：P1 先清 1/2/3/4，P2 随后 5-8。下轮建议 writer 修后跑 rationale+scheme 联动复核。

评分档位依据（rubric 逐条对照）：创新性 0.85——0.80-0.89 档"已有方向上提出新方法/新机制，与前人清晰区隔"：两通道频率幂次分离判据与 69 行跨子系统配对表成立；未达 0.90+ 因科学问题仍在 Floquet 奇宇称磁性既有方向内深化。可行性 0.81——0.80-0.89 档"主要技术有文献支撑，个别难点有应对"：三平台均有先例与标定参数（Ã=0.2 Å⁻¹、λ=0.4、44 meV 终端），R≥20 窗口仅单平台落点压至档内低位。严谨性 0.74——五项核查过三：①④⑤过（4 K/95%/Ã 单一口径；问题→方法→验证链完整；章节间无互斥数值），②不过（R 判据 MnPS₃ 侧零落点，位置 content L56/scheme L81）、③不过（rationale L79 错挂），0.70-0.79 档。表达质量 0.80——0.80-0.89 档"表达清晰、整体连贯"：锚点结论=达标（语体/论证密度/数据驱动/引用嵌入四项逐项对比不低于范本），三处复述与误词 ×3 使其居档位下沿；程序天花板 1.00 未触。

## 评分
创新性：0.85
可行性：0.81
严谨性：0.74
表达质量：0.80
综合评分：0.81
