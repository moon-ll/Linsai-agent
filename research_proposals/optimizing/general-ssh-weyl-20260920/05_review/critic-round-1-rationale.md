# 对抗评审报告（第 1 轮）——立项依据 rationale.md

项目：general-ssh-weyl-20260920（面上 general）；本轮聚焦：（一）立项依据；评审日期 2026-11-03。
前置核查：canonical 禁用模式在 4 个章节文件程序扫描零命中；rationale 角标 39 处去重 34 篇，[1]–[36] 挂靠与 references 表逐一对位无错号；判据指针 ΔI_gap/阈值 R/阈值 T/σ₀<0.05 经程序 grep 在 scheme 全部落地（σ₀ 为 LaTeX 形式 $\sigma_0/\sigma_{\text{full}}$）；[9] "14 个数量级" 与 [15] 预印本状态已联网复核属实。

## 执行清单对照
清单1. 通过——五层递进齐备（§1 意义→§2 现状→§3 空白→§4 定位→§5 科学问题）
清单2. 通过——39 处角标均为"某人等人[N]+年份+贡献"嵌入式，无"A做了X[1]，B做了Y[2]"堆砌
清单3. 通过——§5 末段自然收束于统一框架，无"为回答…问题"式口号
清单4. 通过——正文角标 39 处∈35–47；参考文献 40 篇∈30–40（编号连续无跳号）
清单5. 通过——6563 字∈5000–8000

## 锚点对比
对1（引用嵌入/数据驱动，开篇段）：
申请书原文：Ghimire 等人[1]于 2011 年在中红外激光驱动 ZnO 晶体时首次实验观测到固体 HHG，把这一非微扰强场过程从气相拓展到凝聚态体系。
锚点原文：2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生。
差距：句式与数据嵌入（年份/驱动/材料/事件）同构，另多一层意义收束，论证密度不低于范本。

对2（段间衔接/末尾收束）：
申请书原文：四条线索最终收敛于同一框架——以 Berry 曲率分布与边界态为统一可观测量的多带强场动力学框架，其成立条件与失效边界由 ZnO 对照验证最终落实。
锚点原文：末尾自然引出科学问题，不使用"为回答...问题"式口号；段间以内容逻辑衔接（非关联词）。
差距：末段自然收束无口号；但 §3/§5 以"第一/第二/（1）（2）"序号推进段落，内容逻辑衔接弱于范本。
锚点对比结论：基本接近

## 写作风格评估
连贯叙述式主线确立：以科学问题驱动行文，段落密度均衡，他人成果全部"报道/实现"式客观转述，数值（14 个数量级、666 as、幂指数 2.3 与 0.9→0.3）嵌入论证链，无条目罗列与元话语。程序化检测：transition_words 0/39、template_phrases 0/8、template_subject 0/5、redundant_modifiers 12/79、meta_discourse 0/2、excessive_bold 0、bullet_list 0、self_reference 0、severe long_sentences 6/7（免罚额内）——AI 写作模式零命中，无 anti_ai 强制扣分项；天花板 1.00 不构成约束。失分点为序号推进与角标密度。

## 问题清单
1. [critical] citation_integrity｜rationale §2.4 L65（连带 content §2.5、scheme §3.4 校核一、references [20] 注释）｜[20] You 2017 各向异性 HHG 样品实为 MgO，正文四处写 ZnO｜[20] 全链改挂 MgO，L81-83 以 ZnO 各向异性为对照维度的论述同步改写｜违反 rubric 严谨性③⑤、indicator_red_lines.consistency_check｜P1
   论证：Nature 官方摘要明言 "using single-crystal MgO"，图 1–5 全为 MgO、无 ZnO 取向数据；scheme 扫描配置两处写 MgO 而校核一写 ZnO，同章两版互斥，张冠李戴+模块不自洽双重违例（联网核实记录在案）。
2. [high] indicator_undefined｜rationale §4 L91｜判据一"带隙频率处的强度比"频窗与归一化未定义，两体系带隙频率不同一｜方案侧明确 I 的频点/积分窗与同驱动归一化协议｜违反 indicator_red_lines.indicator_measurable｜P1
3. [high] evidence_sufficiency｜rationale §5 L103｜Cd₃As₂ 三数量级增强含微腔腔场增益，直接界定散射 Z 上界依据不足｜补剥离腔增益论证或改以裸膜幂律 2.3 为界｜违反 indicator_red_lines.theory_applicability｜P2
4. [medium] logic_gap｜rationale §4 L91（对接 scheme §3.4）｜R=2 源自 [19] 同族拓扑/平庸对比，移植为跨材料（拓扑 vs ZnO）判据下界属对象错位｜补非拓扑差异（带隙/偶极矩）归一化扣除后再判定拓扑增量｜违反 rubric 严谨性②｜P2
5. [medium] narrative_structure｜rationale §3 L73-83｜四空白以"第一/第二/第三/第四"序号推进，段间内容衔接弱｜删序号，按现象→机制→对照递进重衔｜违反 style_benchmark.narrative_density｜P2
6. [medium] citation_trace｜rationale §2.4 L55｜彭-Weizmann MgO 工作即 §2.1 [33] Faeyrman 同作，未标 [33] 无法对位｜段末补 [33] 角标｜违反 section_standards.rationale#2｜P3
7. [low] narrative_density｜rationale L21｜Heide [5] 单句成段，信息密度低于周边｜并入次段或充实相变点响应细节｜P3
8. [low] citation_density｜rationale 全章｜角标 39 处超范本口径（10–17），非关键论断挂靠冗余｜次要论断去角标，文献以整体研读身份入表｜违反 style_benchmark.citation_style｜P3

维度依据：
- 创新性 0.82＝rubric 0.80–0.89 档：四方向+统一标尺+判别阈值表，与前人有清晰区隔；未达 0.90 档全新范式。
- 可行性 0.80＝rubric 0.80–0.89 档：技术路线有文献支撑，三条判据指针经程序核验全部在 scheme 落地；R=2 移植依据待补（问题 4）。
- 严谨性 0.74＝rubric 0.70–0.79 档（五项过三）：③不过——[20] MgO 错挂为 ZnO（L65）；⑤不过——scheme 内 [20] 晶体归属两版互斥；①数值链、②指标定义、④逻辑闭环过。
- 表达质量 0.78＝rubric 0.70–0.79 档顶部：程序检测 AI 模式零命中，扣分点为序号推进与角标密度；锚点结论＝基本接近，≤0.79 上限生效。
- 综合 0.79＝0.35×0.82＋0.29×0.80＋0.24×0.74＋0.12×0.78（面上权重）。低于 0.85 阈值，主因 critical#1；该项修复后严谨性可回 0.85+ 档。

## 评分
创新性：0.82
可行性：0.80
严谨性：0.74
表达质量：0.78
综合评分：0.79
