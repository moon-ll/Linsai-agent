# 对抗评审报告（第 5 轮 · 整体一致性审查）

元信息：key-transient-quantum-phase-optical-20260726｜重点项目｜2026-10-22｜profile=critic｜聚焦=rationale/content/scheme 三章整体一致性｜standards=memory/nsfc-standards.json（项目 memory 缺失，fallback 至仓库级 /Users/ll/Desktop/LinSai-CoPilot/memory/nsfc-standards.json，key 权重 创新0.33/系统0.27/战略0.27/可行0.13）。评审基于当日实读三章全文 + 程序化 grep 复核，非记忆复述。

## 执行清单对照

清单0. 通过——rationale（五层递进）/content（总述+3方向+目标+KSP+年度）/scheme（路线+子课题+协同+难点+创新+年度+成果）三模块在位，key 不限提纲合规。
清单1. 通过——三章全文与 standards 五个字段块（section_standards/programmatic 参数/overall/scope_exclusion/indicator_red_lines/scoring_rubric/style_benchmark/benchmark_anchors）均已实读。
清单2. 不通过——rationale 第 4 条 [N] 引用 56 次超 35–47 上限；content §5 两处"方案侧承接"声明虚指（见问题 1，consistency_check 违例）；其余各章条款过。
清单3. 通过——2 对锚点对比见下节，结论独立成行。
清单4. 通过——anti_ai 超长句 12 处立案为问题 3（severity=high）。
清单5. 通过——按 key 标准完成红队评审，问题清单 8 条。
清单6. 通过——无 bullet 罗列、无"A做了X[1]"堆砌、元话语 0（程序检测）；narrative 缺陷为超长句与管线语混入，均已立案。
清单7. 通过——每条问题附违反条款与可执行建议。
清单8. 通过——critical 1 / high 3 / medium 4 / low 0。

## 锚点对比

对1（立项依据）：申请书（rationale §2.1）"Di Gaspare 等人[9]于 2025 年在 (InₓBi₁₋ₓ)₂Se₃/Bi₂Se₃ 范德华超材料中区分了体态与拓扑表面态的非线性贡献。"／锚点"2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生。"／差距：同为人名+年份+体系+观测内容嵌入结构，且机制细节（奇偶次对称选择）密度高于范本，句长略超属技术性长句。
对2（研究方案）：申请书（scheme §2.1(a)）"在标定子区间（ℏΩ_R/E_g ≲ 0.3）下，二阶项振幅约 10⁻² 量级，相对一阶约 10%，偏差 < 0.05 的承诺仅在该子区间内成立。"／锚点"首先，求解定态本征值问题获得掺杂半导体的电子能谱及跃迁偶极矩等信息。然后，利用数值方法获得电子演化的含时波函数……"／差距：数值密度与适用条件限定严于范本，步骤+判据式行文同构；"承诺"一词残留元层语体，范本无此层。
锚点对比结论：达标

## 写作风格评估

三章连贯段落式行文，程序检测 transition 2/49✓、template 0/8✓、元话语 0/2✓、加粗 0✓、bullet 0✓、冗余修饰 26/98✓；引用嵌入与防御密度达标。超长句(>120字)12处超免赔9（扣0.06），天花板 0.94 生效；content §5 残留"口径"×2 与"单一真相源"管线语，scheme 残留"申报"×2。程序检测：long_sentence 12处⚠，其余各项全过。

## 问题清单

1. [critical] consistency_pointer｜content §5 Y1+Y2里程碑 ↔ scheme §6/§1.3｜"方案侧以同样数值承接"声明两处虚指：§6 无"10个驱动点/初检0.10/50as离散度"，§1.3 无误差预算｜scheme §6 Y1 补驱动点数与初检/复核阈值、Y2 补 50as 离散度锚，或将 content 声明改实指（violates indicator_red_lines.consistency_check + implementation_path，P1）
2. [high] numeric_consistency｜scheme §2.2(c)｜"波长比约 25–400 倍"与同句括注端点 24、387 两版并存（24<25、387<400）｜概数改"约 24–390 倍"与端点自洽，或删概数留端点（violates 严谨性清单①数值链一致，P1）
3. [high] anti_ai｜全案（程序报告）｜超长句 >120 字 12 处超免赔 9 处，扣 0.06｜优先拆程序示例三句（场强换算句、Bi₂Se₃ Rabi 例句）与 §2.3(b) 误差长句至 ≤120 字（violates anti_ai_patterns.超长句，P1）
4. [high] citation_factuality｜scheme §2.3(b) ↔ rationale §3｜复述句处置未执行，且 scheme 版将 Neufeld[30] 纯计算基准改称"实验-计算对照"，定性失实｜scheme 版改"计算对照"并整句换为"（泛函基准详见 §一 §3）"式指针（violates 无跨章重复+文献事实定性，P2）
5. [medium] banned_term｜content §5、scheme §2.2(b)｜"口径"×2、"单一真相源"管线语、"申报"×2 残留｜改"判据定义/表述"，删管线语改直陈，全章 grep 归零（violates skill 第三节禁用词表，P2）
6. [medium] structure｜sections/full_review.md 纯净性告警｜实测 CJK 1136 字、非空白 2477 字均 ≤3000，骨架三部分合规，5KB 系 UTF-8 字节口径误用｜维持骨架不动，回告管线计数口径应为字符数（依据 section_standards.full_review 第 3 条，P3）
7. [medium] citation_density｜rationale｜[N] 引用 56 次超 35–47 上限，41 条全用足，较 R4 的 53 次反升｜合并低任务并列引用（如 [34]/[36]/[37] 类）压至 ≤47（violates section_standards.rationale 第 4 条，P2）
8. [medium] pointer_partial｜content §5 Y3 ↔ scheme §6 Y3｜"连续 8 小时内至少 95% 记录时段"验收协议未在 §6 承接，仅核心数值 ≤100 as 在位｜scheme §6 Y3 补 8h/95% 验收句，或 content 删该限定（violates consistency_check，P2）

问题 1 论证：content §5 三个年度里程碑均以"方案侧 §6 里程碑段以同样数值与口径承接，与本节保持单一真相源"自证跨章一致，但程序 grep 证伪：scheme §6 第 1 年段无"10 个驱动点"与"初检 0.10/复核 0.05"，第 2 年段无"窗口时间位置离散度 ≤50 as"，且所指"§1.3 误差预算"实为数据流回路节、无任何误差预算内容。两处声明的被指对象不存在，评审专家按指针核查即穿帮，年度可证伪标准的验证链在跨章衔接层断裂，与 R4 TA-RABBITT 指针落空同构，故定 critical。

## 评分
创新性：0.88
可行性：0.82
严谨性：0.66
表达质量：0.86
综合评分：0.81

评分依据（放块前存档）：创新性 0.88=rubric 0.80-0.89 档——不变量层对相位层推进+五体系 ℏω/E_g 分区判据+与 Uzan/Faeyrman/Zhao C. 三路区隔声明充分；不取 0.90 档因瞬态拓扑测量已被 2026 Roadmap 列旗舰方向，非前人未触及。可行性 0.82=0.80-0.89 档——两套 OPCPA 与阿秒光路为已有装置、预研 SNR 105±18、D1–D6 均双路径、2 μm 端 117 as 超指标已配三级应急与裕度声明；扣于 L1 反演 10⁶–10⁷ CPU·h 依赖超算配额。严谨性五项核查：②指标可操作过（三档判据/SNR 6.5–8.7/误差分层合成/抖动分项预算复算吻合）、③文献真实过（采信 references 专轮全量反查，抽读无误挂）；①数值链不过（scheme §2.2(c) 25–400 与 24/387 两版，问题2）、④逻辑闭环不过（content §5 两处承接虚指，问题1）、⑤模块自洽不过（同上+复述双版，问题4）——过二，落 0.60-0.69 档取 0.66，未过项位置已指明。表达质量 0.86：锚点结论"达标"允许入 0.85+，但受程序化超长句 penalty 0.06 与管线语残留压至 0.86，未超天花板 0.94。综合=0.33×0.88+0.27×0.66+0.27×0.86+0.13×0.82=0.807≈0.81。

## 对抗结论

本轮 8 个问题（critical:1, high:3, medium:4, low:0）。较 R4：两个 critical 均已修复并经程序验证（TA-RABBITT 类相位定义与合成式已落 scheme §2.2(b)，content 两处指针闭环；XUV 能区统一为 20–60 eV 主窗+扩展段并与预研窗 35–45 eV 声明自洽）；"口径"禁用词由 scheme 2 处清零但迁移至 content 2 处；[N] 密度 53→56 反升。新增本轮 8 项中 1 critical 为 R4 同类指针虚指在年度里程碑层复发，物理内核（判据数值链、误差预算、三档处置）本轮复算全部一致未伤。是否达到输出标准：否——key 阈值 min_overall 0.90 / max_high 0 / max_medium 2，当前 0.81 且 critical 1、high 3。返工优先级：P1=问题 1/2/3；P2=问题 4/5/7/8；P3=问题 6。下轮建议聚焦：修复后对 content §5 三处承接声明与 scheme §6 五个年度段做逐数值回扫，并对全案"约 N–M"概数与括注端点数字做一次同段自洽筛查。
