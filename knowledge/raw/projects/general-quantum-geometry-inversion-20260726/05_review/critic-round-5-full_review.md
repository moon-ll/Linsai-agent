# 对抗评审报告（第 5 轮·整体一致性审查）
项目类型：general（面上）；聚焦：rationale/content/scheme 跨章一致性与逻辑衔接；评审依据：memory/nsfc-standards.json + nsfc-writing skill（本轮 references/full_review 正文域外，预检采信并抽测）。

## 执行清单对照
模块完整性. 通过——立项依据/研究内容/研究方案三模块齐备，特色创新与预期成果并入方案章 §7/§8。
rationale1. 通过——1.0 领域意义→1.1/1.2 脉络与挑战→1.3 问题→1.6 国内现状与首创性边界，五层递进齐备。
rationale2. 通过——嵌入式引用为主（"Ghimire 等 2011 年在 ZnO 晶体中观测到体相高次谐波[24]"）。
rationale3. 通过——以检索窗声明收束，无"为回答…问题"口号。
rationale4. 不通过——[N] 角标 53 次，超 35–47 上限（范本校准编号引用 10–17 次）。
rationale5. 通过——5374 字处常规区间。
content1. 通过——2.1 总述+R1–R4 分方向+2.6 计划+2.8 问题。
content2. 通过——各 R 节判据均量化（三档放大、收缩比≥2、误差阈值三档）。
content3. 通过——Q1=R1+R3'、Q2=R2+R3+R4 显式映射。
content4. 通过——装置/协议细节（HBT、JSON-LD、GPU 预算）均转 scheme。
content5. 通过——R1→R2→R3→R4 单向因果链，段间承接句明确。
scheme1. 通过——§1 总纲+§2–§5 分方案+§6.1 集中可行性。
scheme2. 通过——三层描述、经典基线选择均给出"为什么选"论证。
scheme3. 通过——§6.1 四条"方案→原理→结论"链。
scheme4. 通过——§6 通用风险清单+各 R 节降级路径。
scheme5. 通过——未见"为什么研究/为什么可行"口吻。
scheme6. 不通过——14092 字超参考上限且冗余命中（三指标定义 scheme 内 3 处、Ikeda 50 meV/1.7% 锚点全文 6 处复述），不属"论证密集的实质性长文"。
跨章指标预检 5 项差异复核. 通过——均为口径差异非矛盾：1.6 μm=BSV 源中心波长（Rasputnyi 档）vs 1.5 μm=R2/R3 驱动波长；温度集分属文献扫描区间（14/283 K）、实验窗（80–300 K）与相变点（200/180/350 K）；meV/eV 数值各归其语境。
canonical 口径合规. 通过——g2(0) 定义式为光子数算符标准形式，禁用旧形式 grep 零命中；多模 2+1/M（读数 1.5–2）/单模简并 3+1/N 两档表述三章一致。

## 锚点对比
锚点一（立项依据·语体与引用嵌入）
申请书：'高次谐波产生（HHG）是飞秒激光与物质相互作用的高阶非线性、非微扰现象[25]……Ghimire 等 2011 年在 ZnO 晶体中观测到体相高次谐波[24]，开辟了固体 HHG 的实验路线'（rationale §1.0）。
锚点：'高次谐波产生是飞秒激光与物质相互作用的高阶非线性、非微扰现象……2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生。'
差距：开篇语体、嵌入式引用与年份-体系-推进链同构于范本，数据密度不低于范本——本段达标。
锚点二（方案·步骤叙事与方法论证）
申请书：'量子态层面的处理起点是双模压缩真空态……BSV 场统计的独立可标定性由 Lvovsky 2009 年[14]的连续变量量子态层析综述与 Breitenbach 等 1997 年[38]的实验层析工作共同确立'（scheme §2.1）。
锚点：'在前期的工作中，我们已经熟练掌握了利用含时薛定谔方程、含时密度泛函理论研究理想晶体高次谐波的数值模拟方法……首先，求解定态本征值问题……然后，利用数值方法获得电子演化的含时波函数……'
差距：步骤链与"为什么选"论证密度达标，但句长与嵌套层级明显超范本节奏，自指句首密集，流畅度低于范本。
锚点对比结论：基本接近

## 写作风格评估
三章节均为连贯段落式行文，文献嵌入论证链，判据与数值密度高于范本；短板集中在 scheme：长句多层嵌套、自指句首密集，且跨章锚点（Ikeda 50 meV/1.7%）与三指标定义多处复述。模板句式、元话语、过渡词均零命中，AI 味属句长/自引用型而非模板型。
程序化检测引用：long_sentences severe 13（免赔 9，扣 0.08）；self_reference 31（阈值 10/15，扣 0.10）；transition_words 4/50✓、template_phrases 0✓、meta_discourse 0✓、redundant_modifiers 4/101✓；表达质量天花板 0.82。

## 问题清单
1. [high] indicator_dangling｜scheme §1.0/§7.1｜实验侧判据 R̃_Ω/R̃_g 全篇零定义即引用，所指 §4.2 并无此符号｜§4.2 补 R̃ 计算式与测量协议，或全文统一改用 R^CDW｜indicator_red_lines.indicator_measurable（full_review 口径表同步修）
2. [high] criteria_missing｜scheme §4.2/§4.4｜R3' 实验 Go 值 R^CDW≥2 与收缩比计算式未落方案章（content §2.4.2/§2.6.3 两处有，scheme 零处）｜§4.4 补 R3' Go 条目并写明收缩比计算式与测量协议｜indicator_red_lines.implementation_path
3. [high] terminology_drift｜rationale §1.5（L73）｜第三指标名"通道相关系数"与 content/scheme"后验相关系数"两版｜rationale 统一改为"后验相关系数"并补阈值 |C|<0.3｜indicator_red_lines.consistency_check
4. [high] anti_ai｜全文（scheme 为主）｜程序检测自引用 31 次超阈值、超长句 severe 13 处（免赔 9）｜拆分 >120 字长句、削减"本节/本项目"句首至 15 次内后复测｜anti_ai_patterns
5. [medium] criteria_ambiguity｜content §2.2（L31）｜三层差异判据同章两版："SNR 阈值 10:1"与"差异 10%"混用｜统一为"差异<10%（对应 SNR≥10:1 检出限）"｜indicator_measurable
6. [medium] criteria_drift｜scheme §4.4 vs rationale §1.3（L53）｜Q2 失效判据两版：SBE 对 Hubbard-corrected 偏差/BSV-SBE 对实验偏差，"与立项依据一致"系部分虚指｜scheme 补对应关系句，或 rationale 改为与实施层同式｜consistency_check
7. [medium] citation_density｜rationale 全章｜[N] 角标 53 次超 35–47 上限，密度过高近堆砌｜背景性引用转为整体研读基础，仅关键论断留编号角标｜section_standards.rationale[4]
8. [low] stale_warning｜预检纯净性告警｜复测 full_review.md：去空白 2426 字≤3000、骨架三部分结构合规、零核查记录词，"929 字/5KB 超限"按字节口径误判｜无需重写，管线侧修正计数口径即可｜section_standards.full_review[1-3]

本轮 8 问题（critical 0/high 4/medium 3/low 1）；高优先级返工为问题 1–3（R3' 判据链在方案章断裂）与问题 4（anti_ai）。综合 0.79<0.85 且 high 问题 4 项超 max_high_issues=0，未达输出标准，writer 须先修复 P1 项再入下轮。

评分依据（rubric 档位）：
创新性 0.84——0.80-0.89 档：BSV 光子统计×Ω/g 反演误差、三指标可辨识性判据空间、CDW 相图均与前人（Rasputnyi 产额增强、Tyulnev 单篇 CDW 报道）有清晰区隔，未达"全新范式"档。
可行性 0.82——0.80-0.89 档：ZnO 同码复现偏差 5%、PINN 原型 Ω<12%、通量预算诚实（3000h 压缩至 30h 有 OPCPA 路径）、降级路径完备；BSV 源依赖合作方属个别风险。
严谨性 0.72——五项过三（①数值链一致、③文献真实性本轮域外按 references 专轮采信、④逻辑闭环）；②指标可操作未过：R̃_Ω/R̃_g 零定义、R3' Go≥2 无计算式与测量协议（问题 1/2）；⑤模块自洽未过：指标名两版、Q2 失效判据两版（问题 3/6）——rubric 过三=0.70-0.79 档。
表达质量 0.68——anti_ai 检出（自引用 31+超长句 13）按规则扣至 0.6-0.7 区间，天花板 0.82 未触及；锚点"基本接近"上限 0.79 不构成约束。
综合 0.79=0.84×0.35+0.82×0.29+0.72×0.24+0.68×0.12（严谨性承科学意义权重槽，按 project_types.general 权重）。

## 评分
创新性：0.84
可行性：0.82
严谨性：0.72
表达质量：0.68
综合评分：0.79
