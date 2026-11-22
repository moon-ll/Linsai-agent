# 对抗评审报告（第2轮·rationale）｜general-tmd-bic-mie-anapole｜聚焦：立项依据

事实核实：rationale.md 实读全文 26657 字节（md5 32684179…c18，落盘前终验一致；正文 5505 字、38 条文献连续无跳号）；content.md 21K 抽查 grep；scheme/references/full_review 实测 0 字节。历史报告实读：round-1-rationale（空稿立案）、round-2-content、round-3-rationale（同 mtime 态）。本轮独立外部核验 6 项：Kumar[1]（10⁻⁷ m/V、三层×7、偶数层两个数量级，PRB 原文属实）；Zograf[5]（~800 pm/V@950 nm、>100 倍纳米盘，Nat. Photonics 18, 751 属实）；Tang[12]（2000 倍/1%/30°，arXiv:2503.20161 属实，仍为预印本）；Sortino[17]（110 fs/45 fs，arXiv:2510.03052 属实，仍为预印本）；**[38] Gu & Zhou 真实存在：Appl. Phys. Rev. 12(1), 010201, doi:10.1063/5.0242014 (2025)，上轮存疑撤销，但条目缺卷期页码**；**[37] Moharam "Opt. Lett. 28, 2301 (2003)" 三轮检索不可溯源——Moharam 体系为 RCWA 系列（JOSA A 12, 1068/1077 (1995) 等），无此卷期；时域耦合模通行出处为 Fan, Suh & Joannopoulos, "Temporal coupled-mode theory for the Fano resonance in optical resonators", JOSA A 20, 569 (2003)，残留 critical 坐实**。标准实读自 memory/nsfc-standards.json（general：创新 0.35/可行 0.29/严谨 0.24/表达 0.12）。

## 执行清单对照
清单1. 通过——五层递进齐备（§一.1→§一.5），层间承接句在位（rationale[5-61]）
清单2. 通过——具名+年份+[N] 嵌入式引用贯穿（如 rationale[7] Kumar 句式），非堆砌
清单3. 通过——§一.5 以"这三点的共同落点"收束引出科学问题，无口号式结尾（rationale[61]）
清单4. 不通过——正文 [N] 角标 65 次（程序统计），范本口径 10-20 次（citation_style v6.9.9），超约 3 倍
清单5. 通过——5505 字处参考区间 5000-8000（字数非门限，冗余才是判据）

## 锚点对比
对1（语体·数据驱动，rationale_anchor）
申请书原文：Kumar 等人 [1] 在 2013 年以二次谐波显微成像测得单层 MoS₂ 的 χ⁽²⁾ 约为 10⁻⁷ m/V（约 100 pm/V），自述为数量级估计（rationale[7]）
锚点原文：2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生
差距：具名+年份+[N]+数值四要素已对标范本；差距在句长（该句 122 字超范本节奏）与单位双写冗余
对2（引用密度·citation_style）
申请书原文：Malard 等人 [2] 同年…光强对泵浦功率的依赖斜率为 2.00±0.02，确认了信号的二阶起源（rationale[7]）
锚点原文：文献引用嵌入论证链：'某人等人[N]在期刊上报道了X'…正文 [N] 编号引用 10-20 次（范本实测 10-17 次）
差距：单句嵌入质量达标；全文 65 次超范本上限 3 倍，编号引用未收敛到关键论断处
锚点对比结论：差距明显

## 写作风格评估
五层递进完整，具名嵌入引用与数据密度为高水准；无罗列、无元话语、无加粗、无列表。两大未收敛项：超长句 53 处（上轮已立案，零修复）；[N] 角标 65 次。另"被"字被动句 13 处（程序统计），"耦合强度被发现""必须被写进""尚无被公认的协议"等 4 处非物理必要。程序化检测发现AI写作模式，表达质量被强制限制（天花板 0.50）。程序化检测结果行：超长句 severe_count=53/free_quota=5/penalty=0.96；transition_words 21<22、template_phrases 0、redundant_modifiers 17<44、其余 8 项 0 扣分。

## 问题清单
[critical] citation_authenticity｜§一.5 rationale[59]·条目[37]｜Moharam Opt. Lett. 28,2301(2003) 三轮检索不可溯源，Moharam 为 RCWA 系列无此卷期｜替换为 Fan, Suh & Joannopoulos, JOSA A 20, 569 (2003)（P1）
论证：该条目承担理论框架出师功能——正文明言框架"自 Moharam 等人 [37] 的周期阵列耦合模理论发展而来"，content.md §二.2 挂同一编号构建方法基础。检索证实 Moharam & Gaylord 体系为 rigorous coupled-wave analysis 光栅系列（JOSA A 12, 1068-1076 (1995)、1077-1086 (1995) 等），从未在 Opt. Lett. 28 (2003) 发表"周期阵列耦合模理论"；时域耦合模理论通行出处为 Stanford Fan 组 JOSA A 20, 569 (2003)。卷期号属虚构级错误，违反 references 标准"无张冠李戴（作者、期刊、年份与实际一致）"与 ③文献支撑真实，且 references.md 为 0 字节无第二落点可交叉核验，必须在迁库前修正。
[high] anti_ai｜§一.1-一.5 全文｜超长句>120字 53 处（罚0.96）上轮立案后零修复，残留（anti_ai_patterns 超长句条）｜按分号/逗号语义边界拆句至 120 字内，优先 §一.1-一.3 密集段（P1）
[high] physics_claim｜§一.3 rationale[39]｜"相干时间为 T…只能完成约 T/π 个周期"量纲不成立：T/π 仍为时间量纲非周期数｜代入 [17] 数据改写：T=110 fs、周期 45 fs，约完成 T·f_R≈2.4 个周期（P1）
[high] citation_density｜全文正文｜[N] 角标 65 次超范本 10-20 约 3 倍，残留（citation_style）｜每段保留 1-2 个关键论断挂 [N]，其余并入文末整体研读基础（P2）
[high] module_missing｜scheme.md/references.md/full_review.md｜三模块 0 字节（stat 实测），"方案→指标"路径与统一口径表无载体，残留（indicator_red_lines.implementation_path）｜writer 补齐 scheme 并迁移文献（P1）
[medium] citation_duality｜§一.2 rationale[31]·§一.4 [45]｜Gao 扭转角 150 倍内容 [21]/[23] 双条目跨节双挂，且"高明清"与条目 M. Gao 姓名错配，残留｜核实两篇是否同组工作，统一挂靠并更正人名（P2）
[medium] selfcontradiction｜§一.2 rationale[23]｜"材料阶段由 2013 年的三项工作奠定"实含 Trolle[3]（2014），残留｜改为"2013-2014 年的三项工作"（P2）
[medium] reference_format｜条目[38]｜Gu & Zhou 本轮核实为真（APR 12(1), 010201），但条目缺卷期页码，违反 references"格式统一"｜补全为 Appl. Phys. Rev. 12, 010201 (2025) 并补 doi（P3）

评分依据（档位，rubric 逐条对照）：创新性 0.84=0.80-0.89 档——能量流统一分配+干涉分离协议+相干时间约束三问题凝练锐利，与 Tang[12]/Yang[8]/Zhang[22] 区隔清晰，但未到"全新范式"档。可行性 0.65=0.60-0.69 档——定位段三点理由+器件先例齐备，但 scheme 0 字节使"方案→指标"路径无载体（implementation_path 断链），核心技术环节缺可行性论证。严谨性 0.66=0.60-0.69 档（五项过二）——①数值链过：[1][2][5][12] 数值经外部核验一致；②指标定义过：rationale 非判据载体，content 侧承接；③文献支撑不过：[37] 卷期不可溯源（位置 rationale[59]）；④逻辑闭环不过：T/π 量纲不成立（rationale[39]，SI 代入 T=110 fs/45 fs≈2.4 个周期）；⑤模块自洽不过：[21]/[23] 双挂+"高明清"人名错配（rationale[31,45]）——较上轮 0.72 降档系本轮新增 ④ 量纲核算未过项。表达质量 0.46=0.60-0.69 档下修——结构与嵌入引用优，但超长句 53 处（罚 0.96）+被动句 13 处（4 处非物理必要），天花板 0.50 强制生效；锚点结论"差距明显"绑定：表达≤0.69、综合≤0.84 均满足。综合=0.35×0.84+0.29×0.65+0.24×0.66+0.12×0.46=0.6961→0.70（脚本复算）。

## 评分
创新性：0.84
可行性：0.65
严谨性：0.66
表达质量：0.46
综合评分：0.70
