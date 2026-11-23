# 对抗评审报告（第 1 轮 · 整体一致性审查）

课题：general-mos2（面上）｜聚焦：rationale/content/scheme 三章衔接、术语、冗余与矛盾｜references/full_review 按指令排除｜程序预检（指标差异 5 组、冗余 5 组、AI 检测）已采信并复算复核。

## 执行清单对照

清单0. 通过——三段式模块齐全；特色创新/年度计划/预期成果编排在方案章而非模板所示内容章，结构自洽不扣分
清单1. 通过——三章与 nsfc-standards.json（general 权重 0.35/0.29/0.24/0.12）已实读
清单2. 通过——见上"执行清单对照"各行（本段即逐条结论）
清单3. 通过——锚点对比见下节，结论"基本接近"
清单4. 通过——AI 检测结果已列入问题清单（超长句 12 处，issue #5 关联）
清单5. 通过——红队评审完成，critical 2 / high 3 / medium 2 / low 1
清单6. 通过——写作风格检查完成：整体连贯叙述式，无 bullet 罗列；缺陷为超长句与审计语言（见问题 #5）
清单7. 通过——每条问题均附违反条款（indicator_red_lines.consistency_check 等）
清单8. 通过——按 P1（#1-#5）/P2（#6-#7）/P3（#8）分级

## 锚点对比

对1（立项依据·语体）
申请书：2011 年 Ghimire 等人以中红外激光驱动 ZnO 晶体，观测到非微扰固体 HHG[1]。
锚点：2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生。
差距：句式与嵌入方式同构达标；范本先用两段气体相背景再落固体，申请书首段直接以机制信息（带间/带内、Berry 曲率）推进，密度更高但叙事铺垫薄一层。

对2（研究方案·论证链）
申请书：协同项写为 H_int = α·d_ex·V_moiré……α 的初始值由 TD-HSEX 多带计算在主线样品结构上的输出标定；拟合区间覆盖 0°、13.4°、30° 三个扭转角与 ±100 meV 失谐范围。
锚点：首先，求解定态本征值问题获得掺杂半导体的电子能谱及跃迁偶极矩等信息。然后，利用数值方法获得电子演化的含时波函数……
差距：两者均为步骤式叙述，申请书公式与参数密度更高；但范本每步给出因果目的（"为了适应本项目……"），申请书多处只给参数区间不给选取理由，且"口径/冻结/降级"类词范本零出现。

锚点对比结论：基本接近

## 写作风格评估

三章均为连贯段落式行文，无 bullet 罗列，引用嵌入规范，数值密度高于范本；主要缺陷是 12 处超 120 字长句（免赔 6，扣 0.12）、scheme 章审计语言密度偏高（"口径"全文 11 处）、关键科学问题与判据句跨章复述。程序检测：transition_words 5/28 ✓、template_phrases 0 ✓、meta_discourse 0 ✓、long_sentences severe 12 处 ⚠️（penalty 0.12）。

## 问题清单

### [critical] indicator_consistency｜rationale §2.3.3 ↔ content §2.1｜魔角参数半迁移：7.5 vs 7.07 nm、δ²≈14θ² vs 4.6θ²、1.36 vs 1.35 nm｜按 δ=4.1%、θ=1.1° 统一重算（L≈7.07、比值≈4.6）后同步改 rationale 三处
复算：θ=1.1° 时 δ²/θ²=4.56，L=7.068 nm；rationale 同段"魔角附近（θ≈1.1°）δ²≈14θ²"自相矛盾（14θ² 对应 θ≈0.63°），且 7.5 nm 与 7.07 nm 跨章不闭合。content 已是新值，rationale 残留旧值，属典型半迁移。违反 indicator_red_lines.consistency_check、P1。

### [critical] citation_integrity｜rationale §1/§2.4、scheme §2｜[35] 同章双挂（VBO/CBO 计算 vs Luu-石英反演）、[28] 跨章异人（Patra vs Cárdenas）、Molinero 29↔30、Mrudul 30↔31、Almeida 31↔32、Zhong 24↔26｜做全文人名锚↔[N] 全量比对后统一重排
rationale 第 2 段 [35] 为 MoS₂/WSe₂ PBE 能带偏移，§2.4 同号挂 Luu 与 Wörner α-石英反演，同一编号在同章指向两篇不同文献；scheme [28]=Cárdenas 而 rationale [28]=Patra。正文体系内部即自相矛盾，不待 references 专轮即须整改。违反 indicator_red_lines 与 P1。

### [high] reference_mismatch｜rationale §1 ↔ scheme §3.2｜泵浦可调谐窗口 1.25—2 eV vs NOPA 1.4—2.1 eV 起点漂移｜统一为装置实际值；若 1.25—2 系 Peterka 引文窗口则显式标注出处
违反 indicator_red_lines.consistency_check，P1。

### [high] redundancy｜content §2.5/§2.6 ↔ rationale §3 ↔ scheme §2/§3.3｜Q1/Q4 设问、R² 0.85—0.90 处置句、α_syn 双分支句三章复述（程序检出 5 组）｜判据句保留 content §2.6 单点，scheme/rationale 改"如 §二所定"式指针
违反 NSFC"无跨章节内容重复"红线与 content_boundaries，P1。

### [high] anti_ai｜全文（scheme 为主）｜超长句 12 处（>120 字，免赔 6）+"口径"11 处+"触发停机排查""冻结"等审计语言｜长句拆分；"口径"改"定义/判据"，审计句改叙述式
违反 anti_ai_patterns（超长句、内部管线工作语言），P1；表达质量由此压至 0.6-0.7 区间。

### [medium] numerical_claim｜scheme §4｜自由度修正 18%÷1.074=16.8%≠15%，三步映射数值不闭合｜起点改 16%（→14.9%）或阈值表述放宽为"≤17% 设计值"
违反 indicator_red_lines.indicator_measurable，P2。

### [medium] unfounded_claim｜scheme §7 特色(1)｜"逐阶映射比 SHG 严格约一个数量级"无推导支撑｜给出 11 条曲线 vs 单构型的自由度对比算式，或删去"数量级"
违反 novelty_claim_cautious（无依据量化断言），P2。

### [low] volume｜content 全章｜3842 字低于参考区间下限｜§2.3 反演方向可扩展机制层论证（不加方案细节）

相关性复核裁决：rationale §2.3.1-2.3.3 与 scheme η(N) 段均属选择定则链/标度律核心论证，全部保留。预检数值差异裁决：μm/nm/百分比/eV 各组多为异物理量集合（1030 nm 掺镱、200 nm 滤波片、1.6 μm 缀饰场等），真互斥仅莫尔周期组与泵浦窗口，均已立案。

## 评分
创新性：0.82
rubric 依据（0.80-0.89 档）：协同判据 α_syn 同样品定义、三基准反演标定、点群逐阶映射，与前人有清晰区隔；未达 0.9 档系"全新科学问题"尚不成立。

可行性：0.80
rubric 依据（0.80-0.89 档）：技术路线完整，CEP 压缩/Han[40] 范本/Csizmadia ±81as 有文献锚定；380→59 mrad 两步压缩依赖预备实验验证，属"个别难点合理应对"而非充分预研。

严谨性：0.68
rubric 依据（0.70-0.79 档降档至 0.6-0.7 区间）：存在跨章指标半迁移与同号异人引用（indicator_red_lines 违规，强制扣至 0.6-0.7）；逻辑链本身完整故取区间上段。

表达质量：0.68
rubric 依据：超长句 12 处命中 anti_ai_patterns 列举项，强制 0.6-0.7 区间；锚点结论"基本接近"限制 ≤0.79；叙述式与数据密度达标故取区间上段。

综合评分：0.76
加权：0.82×0.35+0.80×0.29+0.68×0.24+0.68×0.12=0.764（科学意义权重槽由严谨性承载）。未达 min_overall 0.85：2 个 critical 在案，达标无望，须先清 P1。

## 对抗结论

本轮发现 8 个问题（critical:2, high:3, medium:2, low:1）。首轮无残留基线，全部为新增。是否达到输出标准：否——P1 五项未清，其中莫尔周期半迁移与引用编号错位属评审一票否决级缺陷。下轮建议：writer 先做 [N]↔人名全量比对重排与 rationale §2.3.3 数值统一，再做判据句指针化与去审计语言，完成后聚焦 rationale 章深审。
