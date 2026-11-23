# 对抗评审报告（第 2 轮 · content 聚焦）
课题 general-quantum-geometry-inversion-20260726｜类型 general｜聚焦（二）研究内容｜2026-10-01｜已实测读取 content.md 全文（189 行），交叉 rationale §1.1–§1.5、scheme 子节头与 §4.3/§4.4、manual v3.5 判据口径表与 L478、references 全 49 条；NEwwave 经 4 轮公网检索+全树反查，Silva-SWE、Raissi-PINN 身份联网核对。

## 执行清单对照
清单0. 通过——五模块齐备（rationale/content/scheme/references/full_review 均在位）
清单1. 通过——总述段（§2.1）、四个分方向（R1–R4 自解释标题）、目标凝练与关键问题（§2.8）齐备；特色创新实体按本项目布局归方案 §7，不判缺项
清单2. 通过——各 R 判据均量化（R 三档、≥2°、Δω/ω>2%、cond(I)<10、|ρ|<0.3、收缩比≥2、Ω<12%）
清单3. 通过——§2.8 Q1→R1+R3'、Q2→R2+R3+R4 映射明确，非泛泛列举
清单4. 通过——上轮点名的偏振步长 1° 已移方案；"三次扫描方差<10%""SNR 10:1"属判据定义非操作参数，不再判越界
清单5. 通过——四步链递进，R 间以判据显式衔接（R1 任务 4 两级→R3' 接力有分工声明）
清单6. 不通过——7507 字仍超参考上限，三档判据句两现、Q→R 映射句 8 处、§2.8 重述 §2.2/§2.4 数值，冗余实据未清零
清单7. 通过——评分与锚点结论、程序检测、问题计数三者自洽（综合=加权复算 0.7817→0.78）
清单8. 通过——本报告落盘 05_review/critic-round-2-content.md

## 锚点对比
对1（content_anchor）
申请书：BSV 场统计的非经典性（g^(2)(0)>1）已在 2024 年 Rasputnyi 等[8]的 Mg:LiNbO₃/a-Si 实验中被确证可提升 4–7 次谐波产额至少 5–15 倍（同平均强度）。
锚点：本项目拟采用理论与实验相结合的研究方法，建立包含局域电子态效应的量子轨迹模型，揭示局域电子态对高次谐波产生过程的影响机理。
差距：数值密度与判据化优于范本，嵌入式引用合规；但范本总述一段完成"方法+机理+应用"，申请书总述散于 §2.1 五段且三档口径句 §2.1/§2.2 两现，以密度换冗余。
对2（innovation_anchor）
申请书：本节内容向特色与创新点收束：第一项产出建立"BSV → HHG 反演精度"的工具链；第二、三项产出以"中等关联反演层"为差异化定位，把 HHG 谱学从机制层推向反演层。
锚点：本项目根据费曼路径积分理论，通过引入散射传播子建立包含局域电子态效应的量子轨迹模型，是本项目的创新之处。
差距：范本为就地四步闭环收束；申请书为指针式收束（"详细创新点结构见研究方案 §7"），本章创新点无实体落点，收束句近元叙述。
锚点对比结论：基本接近

## 写作风格评估
连贯段落式行文、引用嵌入与数值密度整体优于范本均值，无 bullet 罗列、无元话语、无空洞概括句。扣分：超长句 12 处（免赔 9）程序罚 0.06；§2.1↔§2.8 与 §2.2↔§2.4 判据数值复述；§2.4.3 末三连"提供参照"句式近罗列。程序检测：transition/template_subject/meta/bold/list/self_reference 全过线；long_sentences severe_count=12 罚 0.06，天花板 0.94；超长句属 anti_ai_patterns.remove 清单命中 → 表达质量按规则入 0.6–0.7 区间。

## 问题清单
1. [critical-P1] citation_integrity｜§2.4.4 L119｜HMG 基标准"NEwwave"具名无[N]且外部六查不可溯｜给出文献/DOI 证明或改挂实有标准（违反 novelty_claim_cautious、rubric.rigor 0.6–0.69 档）
论证：4 轮公网检索（HHG 数据标准/FAIR/Zenodo/MSCA 定向）仅命中海浪 NewWave 理论、R 语言包与 Horizon 原材料项目；references 49 条与 Ciappina 2025 综述[19]均无此实体，唯一出处是 manual 自证。数据交付物基标准须引证或更名。
2. [critical-P1] indicator_consistency｜§2.4.4"三个领域专属字段"↔manual v3.5 L478"两个关键字段"｜扩展字段数跨文档 2 vs 3 互斥｜以判据口径表为单一真相源统一为三字段并同步改 manual L478（违反 indicator_red_lines.consistency_check）
论证：manual L478 仅列 quantum_geometry_metadata 与 cryogenic_environment 两字段，L496 又出现 bsv_quantum_light_metadata（11 项必填），同册内即自相矛盾；content/scheme 均写"三个"。属半迁移旧值，P0 口径要求立即报告不得自行解释。
3. [critical-P1] citation_integrity｜§2.5 L127｜Raissi 具名无[N]且误称"综述"（系 PINN 原始方法论文）｜改"Raissi 等[30]提出 PINN"并删"综述"二处定性（违反 section_standards"正文有[N]对应"；身份错挂）
4. [high-P1] pointer_integrity｜§2.4.3 L109｜"§1.1 提到的三条独立证据线"在 rationale §1.1 无对应表述，指针悬空｜改指 §1.2 实际段落或删该句（key-sch-R1 判例同型：指针指向不存在表述）
5. [high-P2] anti_ai｜全文（检测报告例句：R 三档句、截止阶次衔接句、边界判据沿用句）｜超长句 12 处超免赔 9，程序罚 0.06｜按分号边界拆双层从句为 2–3 句（违反 anti_ai_patterns.remove"超长句"；表达强制 0.6–0.7）
6. [medium-P2] narrative_issue｜§2.4.3 末四段（Baykusheva[29]/Lange[22]/Uchida[23]）｜三连"为本任务提供参照"句式罗列文献未嵌入论证｜并入红移判据与外推边界的论证链，或删减至一条（违反 writing_style_rules.citation_style）
7. [medium-P2] redundancy｜§2.1/§2.2/§2.8｜三档句两现、Q→R 映射句 8 处、§2.8 重述 10%/≥2°/2% 数值｜三档句只留 §2.1 一处余改指针；§2.8 删数值复述（违反 v6.9.55：超上限须冗余零命中）
8. [medium-P2] audit_language｜§2.2/§2.6 等｜"交付"12 处、"节点处置"3 处、"硬性阈值"2 处、"触发"2 处内部语言残留｜改"形成/给出""节点未达成时""先决条件""若…失败则"（违反 skill 三、禁用词表）

评分档位依据（rubric 对照）
- 创新性 0.86：0.80–0.89 档——BSV 统计→Fisher 信息增益的加性/乘性归属、可辨识性边界量化、条件性判据框架系新机制新视角，与前人（Rasputnyi 产额增强、Tyulnev 偏振基准）清晰区隔
- 可行性 0.83：0.80–0.89 档——SBE 复现 Vampa ZnO 5%、1D-CNN 原型 Ω<12%（n=200）预研支撑；BSV 源外协与 HBT r 值回填属个别风险且有 Plan B
- 严谨性 0.65：0.60–0.69 档——具名断链残留（Raissi）+指针悬空+NEwwave 不可溯+字段数 2v3 互斥，四项并存按档强制
- 表达质量 0.70：0.6–0.7 档强制（超长句命中 anti_ai remove 清单）；锚点"基本接近"上限 0.79 内取区间顶
- 门槛对照：综合 0.78 < min_overall 0.85，critical 3 + high 2 > max 0，未达输出标准
- 较上轮（0.76→0.78）：修复——具名挂[N] 5 处（Sumaya/Yang/Ilin/de-la-Peña 等）、创新点收束句、任务 2 启动节点、§2.6.5 并入 §2.7、主语错挂句；新增——NEwwave 溯源、字段数互斥、§1.1 悬空指针；残留——Raissi 未挂、超长句 14→12 未清零、判据复述
- 下轮建议：writer 优先清 3 critical + 1 high（NEwwave、字段 2v3、Raissi 挂目、悬空指针），再做长句拆分与 §2.8 减重；critic 下轮聚焦 scheme §4.3 字段口径落地

## 评分
创新性：0.86
可行性：0.83
严谨性：0.65
表达质量：0.70
综合评分：0.78
