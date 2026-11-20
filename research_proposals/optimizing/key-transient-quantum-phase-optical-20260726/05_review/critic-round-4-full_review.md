# 对抗评审报告（第 4 轮 · 整体一致性审查）

元信息：key-transient-quantum-phase-optical-20260726｜重点项目｜2026-10-13｜profile=critic｜聚焦=rationale/content/scheme 三章整体一致性｜standards=memory/nsfc-standards.json（项目 memory 缺失，fallback 至仓库级 /Users/ll/Desktop/LinSai-CoPilot/memory/nsfc-standards.json，key 权重 0.33/0.27/0.27/0.13）。评审基于当日 02:32–08:49 版本文件实读，非记忆复述。

## 执行清单对照

清单0. 通过——rationale（五层递进）/content（总述+3方向+目标+KSP+年度）/scheme（路线+子课题+难点+创新+年度+成果）三模块在位，结构合规。
清单1. 通过——三章全文与 standards 五个字段块均已实读。
清单2. 不通过——rationale 清单第4条：[N] 引用实测 53 次＞35–47 上限（程序计数复核）；第5条体量 9744 字＞8000，须先清 Aich[32] 重复再复判是否实质长文。content 六条全过；scheme 五条全过（可行性融于 D1–D6 双路径，符合 key 不限提纲）。
清单3. 通过——2 对锚点对比见下节，结论独立成行。
清单4. 通过——anti_ai 超长句 28 处已立案为问题清单第 4 条（severity=high）。
清单5. 通过——按 key 标准完成红队评审，问题清单 8 条。
清单6. 通过——无 bullet 罗列、无"A做了X[1]"堆砌、无元话语（程序计 0）；narrative 缺陷仅超长句与元层语言混入。
清单7. 通过——每条问题均附违反条款与可执行建议。
清单8. 通过——critical 2 / high 3 / medium 3 / low 0。

## 锚点对比

对1（立项依据）：申请书（§2.1）"Di Gaspare 等人[9]于 2025 年在 (InₓBi₁₋ₓ)₂Se₃/Bi₂Se₃ 范德华超材料中实验区分体态（中心相，仅奇次）与拓扑表面态（对称破缺，奇次+偶次）的非线性贡献"。锚点"2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生现象。"。差距：同为人名+年份+体系+观测内容的嵌入结构且带数值密度，语体达标；差异仅句长（申请句超 80 字），属技术性长句非语体差距。
对2（研究方案）：申请书（§2.1(a)）"在标定子区间（ℏΩ_R/E_g ≲ 0.3）下，二阶项振幅约 10⁻² 量级，相对一阶约 10%，偏差 < 0.05 的承诺仅在该子区间内成立"。锚点"首先，求解定态本征值问题获得掺杂半导体的电子能谱及跃迁偶极矩等信息。然后，利用数值方法获得电子演化的含时波函数……"。差距：同为步骤+物理量+判据式行文且数据驱动更细；但"承诺/档位"等元层语言混入技术叙述，范本无此层，须压缩为物理陈述。
锚点对比结论：基本接近

## 写作风格评估

三章连贯段落式行文，模板短语/元话语/过度加粗/列表替代论证程序检测均为 0，嵌入引用与防御密度（条件句 0.55/千字＜2）达标，无堆砌式罗列。程序化检测发现AI写作模式，表达质量被强制限制：超长句(>120字)28处（免赔9，扣0.38），天花板 0.62 生效；scheme 残留禁用词"口径"×2。程序检测：transition 2/48✓、template 0/8✓、redundant 30/96✓、meta 0/2✓、bold 0✓、bullet 0✓、self-ref 6✓、long_sentence 28 处⚠。

## 问题清单

1. [critical] consistency｜content §2.3+§3 目标三 ↔ scheme｜TA-RABBITT 类相位两处注"定义见 §三 §2.2(b)"，scheme 全文 0 处 RABBITT，指针落空｜在 scheme §2.2(b) 补 TA 吸收谱与 RABBITT 条纹联合相位的定义句及合成式（violates indicator_red_lines.consistency_check + full_review 清单"章节衔接点"）
2. [critical] consistency｜scheme §2.2(c) ↔ rationale §5｜XUV 窗 30–60 eV 称覆盖 Bi O₄,₅ ~26 eV 与 Se M₄,₅ ~55 eV，均在窗外或边缘；预研信号窗 35–45 eV 亦不含 26｜统一能区口径：窗改 20–60 eV 并逐边点核验，或改写覆盖表述与预研窗（violates indicator_red_lines.consistency_check，P0）
3. [high] redundancy｜rationale §3 末段 ↔ scheme §2.1(a)｜Aich[32] 镜像对称 Wilson 圈句两章近重复（程序检测命中）｜保留 scheme 定义位，rationale 改"拓扑学参照见 §三 §2.1(a)"式指针（violates section_standards.full_review 无跨章重复 + 冗余红线）
4. [high] anti_ai｜全案（rationale 9+scheme 主体）｜超长句 >120 字 28 处超免赔额，扣 0.38，天花板 0.62｜按多分号分句拆分至 ≤120 字，优先拆程序示例三句与 §2.3(b) 误差长句（violates anti_ai_patterns.超长句 + writing_style_rules）
5. [high] banned_term｜scheme §2.2(a)/(b)｜禁用词"口径"残留 2 处（"声明口径""贡献口径"）｜改"表述/定义"，全章 grep 复查归零（violates skill 第三节禁用词表）
6. [medium] structure｜sections/full_review.md｜骨架告警按 critical 传入，实测 CJK 1067 字/非空白 2437 字均在 3000 内，内容仅骨架三部分合规；bytes 5682 系字节口径误用｜维持骨架不动，向管线回告计数口径应为字符数（依据 section_standards.full_review 第 3 条，按字符口径判通过）
7. [medium] citation_density｜rationale｜[N] 引用 53 次超 35–47 上限，41 条文献全量用足｜合并低任务并列引用（如 [34]/[36]/[37] 类），压至 ≤47（violates section_standards.rationale 第 4 条）
8. [medium] feasibility｜scheme §4 D4｜"约 50 节点"与 L1 需 3000–6000 核×1–10 周不匹配，机时支撑"结题时核定"时点倒挂｜节点数按 6000 核×运行周数复算改写，机时核定改"立项前申请、第 1 年落实"（violates scoring_rubric.feasibility 0.80-0.89 档"先例支撑"）

问题 1 论证：content §2.3 与 §3 目标三两处以"定义见 §三 §2.2(b)"把核心反演约束 TA-RABBITT 类相位的定义外包给方案章，程序 grep scheme 全文 RABBITT 计数为 0。该量是 Q3 可证伪判据（SNR 6.5–8.7）的信号基础，定义缺失使三章反演链在术语层断裂，评审团亲审必现质疑，故定 critical。
问题 2 论证：scheme §2.2(c) 声明探测能区 30–60 eV 覆盖 Bi O₄,₅（~26 eV）与 Se M₄,₅（~55 eV）吸收边附近；26 eV 在窗外、55 eV 贴上缘，"覆盖"不成立。rationale §5 预研又以 35–45 eV 为信号窗，与两处边点均不重合，同一探测能区出现两套互不兼容的取窗依据，属指标红线级口径矛盾，故定 critical。

## 评分
创新性：0.88
可行性：0.80
严谨性：0.65
表达质量：0.62
综合评分：0.74

评分依据（放块前存档）：创新性 0.88=rubric 0.80-0.89 档，不变量层对相位层的推进+五靶材分区判据与 Uzan/Faeyrman 区隔声明充分，未达 0.90 档因瞬态拓扑测量方向已被 2026 Roadmap 列为旗舰、非前人未触及。可行性 0.80=0.80-0.89 档，预研 SNR 105±18、装置已有、六大难点双路径；扣于 2 μm 端 117 as 超指标与 D4 算力存疑。严谨性五项核查：②指标可操作过（三档判据/SNR/误差合成/抖动预算 8 项复算全吻合）、③文献支撑过（采信 references 专轮，抽读无误挂）——①数值链一致不过（XUV 能区两套口径，问题2）、④逻辑闭环不过（TA-RABBITT 定义断裂，问题1）、⑤模块自洽不过（同上+Aich 重复）——过二，落 0.60-0.69 档取 0.65，未过项位置已指明。表达质量 0.62=天花板强制（超长句 28 处，扣 0.38），锚点结论"基本接近"允许 ≤0.79 但不得突破天花板。综合按 key 权重映射计算：0.33×0.88+0.27×0.65（严谨承系统性权重）+0.27×0.62（表达承战略表达权重）+0.13×0.80=0.737≈0.74。

## 对抗结论

本轮 8 个问题（critical:2, high:3, medium:3, low:0）。较上轮：历史 P0 四条全部保持（三档判据-误差预算绑定数值全链一致、1T-TaS₂ 切割声明三处在位、Floquet 收敛表述与 0.3 上界未回退、Co₃Sn₂S₂ 分区外声明一致），"闭环"由 53→24→本轮仅 1 处且属物理语境白名单，收敛达标；新增本轮 8 项均为跨章衔接与表达层，物理内核零伤。是否达到输出标准：否——key 阈值 min_overall 0.90 / max_high 0 / max_medium 2，当前 0.74 且 critical 2。返工优先级：P0=问题 1/2（writer 先补 TA-RABBITT 定义句并统一 XUV 能区，两处均为单点修复）；P1=问题 3/4/5；P2=问题 6/7/8。下轮建议聚焦：修复后复检 scheme §2.2(b) 新增定义句与 content 两处指针的闭环，并对全案能区-边点-预研窗做一次端点联算。
