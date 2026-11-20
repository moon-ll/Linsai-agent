# 对抗评审报告（第 6 轮 · rationale 聚焦，当前版本线）

**课题**：general-moire-strong-field-probe-20260726（莫尔超晶格强场探针与主动调控）
**项目类型**：general（面上；min_overall_score=0.85，max_high_issues=0，max_medium_issues=3）
**本轮聚焦**：（一）立项依据 rationale.md（r25 版，mtime 2026-08-24 02:23，9006 字符 / 4535 中文字）段落级深审 + 跨章一致性核验
**评审日期**：2026-08-27
**评审者**：critic（红队）
**版本线说明**：05_review/ 原有 critic-round-6.md 为 2026-08-12 旧版本线的参考文献专项报告（与 .archive-critic-round-6-references-special-20260812.md MD5 一致：b4cc0ffd…），已归档，无数据丢失。本报告为当前版本线（R5 = 2026-08-24 critic-round-5.md）之后的第 6 轮。
**评审基础**：全部结论基于 2026-08-27 实地读取 rationale.md / content.md / scheme.md / references.md / full_review.md / references-worklog-20260827.md 当前文件 + 程序化复核脚本（[CITE] 计数、超长句、段长、修饰词、口径 grep）+ Crossref API 实时核查（6 条 DOI 直查 + 1 条标题检索），非记忆印象。
**程序化检测输入**：全文字符数 31326（= rationale 9006 + content 12648 + scheme 9668 + 2×2 字符分隔符，与检测报告一致，检测对象确认为三章拼接）；表达质量天花板 0.72；long_sentences severe_count=20（免赔 6，penalty 0.28）。

---

## 一、执行清单对照

| # | 执行项 | 状态 | 依据 |
|---|---|---|---|
| 0 | 模块完整性检查 | 通过 | rationale §1.1–§1.6 / content §2.1–§2.5 / scheme §3.1–§3.5+§3.4.1 / references 35 条目全部实质在位，无占位空模块（full_review.md 为 574 字逻辑骨架，合规） |
| 1 | 读取申请书+标准配置 | 通过 | nsfc-standards.json（2026-08-20 版）全量读取；rationale 逐段读取；content/scheme/references 交叉读取 |
| 2 | 逐条对照执行清单 | 通过（多项不通过） | 见下 section_standards.rationale 五条 + review_checklist 六条 |
| 3 | 锚点对比 | 通过 | 见"锚点对比"段，结论：基本接近 |
| 4 | 引用程序化检测结果 | 通过 | 见"写作风格评估"段；long_sentences 超标列入 H5（severity=high，issue_type=anti_ai） |
| 5 | 红队评审 | 通过 | 18 项问题（critical:4, high:8, medium:5, low:1），含 2 项 Crossref 实锤引文硬伤 |
| 6 | 写作风格重点检查 | 通过 | 叙述式骨架合规；句长/段长红线未达，详"写作风格评估" |
| 7 | 每条意见标 rubric/标准条款 | 通过 | 问题清单每条注明违反条款 |
| 8 | 严重度分级 | 通过 | critical/high/medium/low + P1/P2/P3 |

### section_standards.rationale 五条逐条判定

| 条款 | 判定 | 证据 |
|---|---|---|
| 1. 五层递进（大背景→脉络→核心挑战→国内现状→本项目定位） | **不通过（第 4 层缺失）** | 大背景（L5）、脉络（§1.2）、核心挑战（§1.1/§1.3）、定位（§1.5）四层在；国内现状层仍仅 L37 一段（北大 Ma 2025 相位匹配，108 字，技术补充口吻），不成层——references 自列 5 个国内组（Hu/Meng 物理所、Zhou/清华、Wang/复旦、Wang/中科院、Yao/张江）无一进入 §1.2 叙述（M2） |
| 2. 嵌入式引用（非堆砌） | 通过 | "Molinero 等 2024 年在 *Optica* 上报道了…其核心发现是…但…"（L21）等为标准嵌入式批判递进；密度超标另计（M4） |
| 3. 末尾自然引出科学问题、不用口号 | 基本通过 | §1.6 以三段价值收束，无"为回答…问题"口号；但 L97"整章沿…形成完整的叙事弧线"为结构元话语残留（M1） |
| 4. 参考文献引用规模 | **不通过** | rationale 单章 45 处 [CITE]，为范本正文编号引用密度（10–17 次/章）的约 3 倍（M4）；[N]/[CITE] 双轨制未统一、[12] 编号重复（H7） |
| 5. 体量 5000–8000 字 | **不通过（口径核实）** | 程序口径 4535 中文字（本轮脚本复核一致），低于 5000 下限；v6.9.55 注明"字数非门限，冗余才是扣分项"，但本案短在论证缺口（国内现状层、机理引证），属"需补足论证而非注水"（M5） |

### project_types.general.review_checklist 六条速判

科学问题新颖重要：是（读出—改写闭环）。立项依据充分（前人局限性讲清）：脉络与划界充分，但含 4 项 critical（维度口径 C1、引文实锤 C2/C3、优先权红线 C4）。方案独特思路：是。预研基础支撑：本轮不评（属研究基础章）。表达精炼：否（H5 超长句）。避免八股：基本是（元话语残留 M1）。

---

## 二、写作风格评估（引用程序化检测结果）

**程序化检测发现 AI 写作模式（超长句 20 处 >120 字，免赔 6，penalty 0.28），表达质量被限制在天花板 0.72 以下。**（天花板 ≥0.7，无需额外强制声明行，但超标项列入 H5。）

| 检测项 | 实测 | 阈值 | 判定 |
|---|---|---|---|
| transition_words | 3（同时 2 / 然而 1） | 31 | ✓ |
| template_phrases | 2 | 8 | ✓ |
| template_subject | 1 | 5 | ✓ |
| redundant_modifiers | 36（有效 16 / 完整 8 / 关键 5 / 重要 2 / 系统 3 / 成熟 1 / 显著 1） | 62 | ✓（已治理；但人工规范上限 12 次仍未达，见下） |
| **long_sentences** | **20 处 >120 字，severe_count=20，penalty 0.28** | 免赔 6 | **✗ → H5** |
| meta_discourse | 0 | 2 | ✓（词表未覆盖"递进×7/叙事弧线"类结构元话语，M1 手工捕获） |
| excessive_bold | 0.64/千字 | 3 | ✓（rationale 加粗已清零） |
| bullet_list_substitution | 0 | — | ✓ |
| self_reference | 10 | 10/15 | ✓（贴线） |

**critic 独立复核（排除标题/表格/尾注行后按句号切分）**：rationale 正文 >120 字句实为 14 处（最长 151 字，L5），与程序 20 处的差异来自切分口径；无论取哪个口径，**均未达到 2026-08-18 人工审核红线"单句不超过 120 字"**。r25 优化记录（L114）自述"拆分所有超 150 字句子"——writer 执行的是 150 字标准而非 120 字红线，属**标准降档执行且未声明**（计入 C4）。

**段长节奏**：rationale 8 个正文段超过范本上限 300 字——L13（685 字，五层挑战段）、L25（442 字）、L21（427 字）、L43（407 字）、L77（393 字）、L79（387 字）、L23（366 字）、L83（364 字）、L53（301 字，贴线）。范本 narrative_density 要求每段 150–300 字；L13 为上限 2.3 倍，将五个数量级估算链（L_M 公式、11,000 原子、10⁵ 核时、O(N³)、TDDFT ≥10³ 倍）压入单段。

**叙述式合规性**：骨架合规——零 bullet-list、零"A 做了 X，B 做了 Y"并列堆砌句、文献嵌入论证链（报道→核心发现→批判→差异化）、段间以内容逻辑衔接（关联词全文仅 3 次）。r25 的表达治理在修饰词（46→11，rationale 单章）、加粗（→0）、关联词（→3）三项上实质有效，值得确认；但句长与段长两项红线未达，天花板 0.72 被超长句 penalty 0.28 压制。

---

## 三、锚点对比（rationale_example）

**申请书原文**（§1.2 L21，理论方法层典型段）：
> Molinero 等 2024 年在 *Optica* 上报道了 magic-angle TBG 的 HHG 全光学表征 [CITE:molinero_optica_2024]。其核心发现是 H₃、H₅、H₇ 在 θ_mag ≈ 1.12° 附近相对 1.22°/1.05° 出现谐波抑制，直接证明 HHG 谱对扭转角敏感。该工作仅使用连续莫尔紧束缚加 8 轨道 Wannier 函数模型计算 HHG，未纳入关联绝缘态的多体修正；其未来方向第一条即指出"电子关联效应被忽略"是有待解决的问题。

**范本锚点**（rationale_example）：
> 高次谐波产生是飞秒激光与物质相互作用的高阶非线性、非微扰现象。……2011 年，Ghimire 等人[9]使用中红外激光驱动 ZnO 晶体，观测到了非微扰高次谐波产生。

**四项差距**：
1. **语体**：申请书的"报道→核心发现→但未纳入→其未来方向指出"批判性递进**优于**范本锚点的平铺报道，此项达标；
2. **论证密度**：单段信息密度高于锚点（每段 3–5 个定量论断），但 L13/L21/L25/L43 等 8 段 364–685 字超出范本"每段 3–6 句、150–300 字"的节奏承载上限，密度转化为可读性负债（H5）；
3. **数据驱动**：数量级估算（10⁴ 原子/10⁵ 核时/10⁸ 核时/O(N³)）具体且标来源，形式达标；但 §1.3 L47 的"30–50 个谐波阶次"数据维度与自家 Kozák 标定（截止 7–11 阶）及 R2 口径（5–9 阶）矛盾（C1），数据驱动反成硬伤；假设 3 的"20%"阈值推导（L69）在引用与外推上依据链断裂（H4）；
4. **引用嵌入**：嵌入方式达标；但单章 45 处为范本密度（10–17 次/章）约 3 倍（M4），且引用治理层面存在实锤虚构条目（C2）与矩阵失实（C3）——引用的"量"与"真"两方面均有硬伤。

**改写方向**：保留批判性递进语体；L13 五挑战段拆为"总起段 + 每挑战一小段（≤3 句）"；>120 字句按"估算前提→数值→含义"三句式拆分至清零；引用密度压至 25–30 处/章。

锚点对比结论：基本接近

（绑定规则执行：基本接近 → 表达质量 ≤0.79 且综合评分 ≤0.89；表达质量另受程序化天花板 0.72 双重约束。）

---

## 四、修复确认表（R5 十八项 → 当前状态）

| R5 问题 | 当前状态 | 证据 |
|---|---|---|
| C1 反演维度两套口径 | **未修复** | rationale L47 原文"10–20 个 Fourier 分量…30–50 个谐波阶次…60–100 个数据点…有效数据秩仅约 10"逐字未动；content L57 / scheme L21 仍为 6–12 复数分量 / 5–9 阶 / 10–18 点口径 |
| C2 强度窗口矛盾 | **未修复** | scheme L7"探针模式采用弱场（I < 10¹¹）"vs L37"探针模式工作强度为 10¹¹–5×10¹¹"同章双口径原样并存；L63"低于损伤阈值 2 倍"仍只对区间上限成立 |
| C3 Hohenleutner 条目 | **未修复，且本轮 Crossref 实锤升级** | references L33 仍为"Scattering-type bordedom high-harmonic generation in solids. Nature 517, 342–346 (2015). DOI: 10.1038/nature14020"——见本轮 C2（编号重排） |
| C4 引用矩阵失实 | **未修复且恶化** | references L3/L121 自述 156 处，实测 78 处；矩阵 7 个条目数字虚高（详见 C3 本轮） |
| H1 超长句 | **部分改善** | 程序 24→20 处；critic 独立复核 rationale >120 字句 14 处（最长 151 字，较 r24 的 399 字大幅缩短）；但 120 字红线未达，r25 按 150 字标准执行 |
| H2 冗余修饰 | **✓ 已修复** | 全文 46→36（阈值内），rationale 单章 19→11，达到人工规范 ≤12；处理方式（删"成熟""完整"）符合"换具体数据"要求 |
| H3 角度先验矛盾 | **未修复** | content L61"样品制备精度 ±0.05°"vs L129"角度精度 ±0.1°"原文未动；指标 ±0.05° 与先验 ±0.05° 仍同值 |
| H4 假设 1/2 依据链 | **未修复** | rationale L83 仍写"依据 Mrudul 等 2024 年椭偏依赖曲线斜率推算"；假设 2 的 3×10¹¹ 与 I_c(10 meV)=1.6×10¹¹（content L79）仍差近 2 倍无解释 |
| H5 Nikola/Shan 归属 | **未修复** | rationale 4 处（L29/L53/L69/L83）+ content 5 处"Nikola 等 2021"，scheme L43 已用"Shan 等 2021"，references [23] 真实作者 Shan J.-Y.——跨章分裂维持 9 处 |
| H6 编号双轨+[12]重复+xxxxx | **未修复** | references [N] 行首编号 vs 正文 [CITE:] 并存；L39 [12] Cao 与 L47 [12] Kozák 同号；L53 Ma 2025 "DOI: 10.1038/s41566-025-xxxxx"（Crossref 实测不存在），人工反馈 08-18 点名后第 9 天 |
| H7 §1.1/§1.3 重复 | **部分改善，降级 M3** | §1.1 已删"约 10³ 个扫描角"句与 mini-BZ 括号细节；但 L_M≈12.8 nm 公式 + 11,000 原子 + 10⁵ 核时/角 + 100×100 k 网格 + 8 轨道 Wannier 五要素链仍在 L13/L43 两遍出现（L43 补回 10³ 角扫描），Bistritzer 引证也两遍 |
| M1 元话语 | **部分改善** | "并非平行罗列的价值承诺"等已删；"递进"9→7 次、"叙事弧线"L97 保留、"理论方法层面："L21 scaffold 残留 |
| M2 国内现状层 | **未修复** | 仍仅 L37 一段 108 字 |
| M3 引用密度 | **恶化（方向矫枉过正）** | rationale 48→45 处仍超 3 倍；content 48→3 处过疏——r25/r26 将 content 正文 [CITE] 标签整批剥离，仅存 3 处，形成新问题 H6（本轮新增） |
| M4 §1.4 边界 | 部分改善 | No-Go 保留且写法规范；SNR=50/15%/±0.05°/I_c 区间等协议数值仍前移在 §1.4 |
| M5 核心问题三重陈述 | **✓ 已修复** | §1.1 收敛为 L7 物理问句 + L9 一句凝练，无重复展开段；正式版独占 §1.4 |
| M6 统计三口径 | **未修复** | references L3"9 篇备选"vs L121"10 篇备选"vs 实测条目级备选 8 篇；L123"50.0%"与 L131 r28 注"48.6%"同页矛盾 |
| L1 管线注记滞留 | **未修复** | rationale L114 r25 优化记录、references L131 r28 注仍在正文 |

**管线异常提示**：R5 P0 六项（C1–C4、H5、H6）**零修复**，rationale/content/scheme 的 mtime（08-21/08-24）显示 R5（08-24 01:41 落盘）之后三章正文再无写入；08-27 09:47 的管线轮仅迁移了 references 工作日志（v6.9.52 全文骨架重构），未触碰任何 P0 问题所在文件。R5 问题清单的修复优先级指令未进入 writer 执行路径，建议管线侧核查 P0 指令注入链路。

---

## 五、问题清单

### [critical] red_line·consistency_check — C1：反演维度论证两套口径并存于三章，rationale 版数字与自家实验体系矛盾（R5-C1 复发，原文未动）
- 位置：rationale.md L47（§1.3 反演空白）vs content.md L57（§2.2 R2）vs scheme.md L21（§3.2）
- 问题：同一欠定性论证，rationale 写"典型截断取 10–20 个 Fourier 分量（10–20 个实参数），单条谐波谱的数据维度仅为 30–50 个谐波阶次乘 2 个偏振通道约 60–100 个数据点，考虑噪声后有效数据秩仅约 10"；content/scheme 统一写"6–12 个复数分量即 12–24 个实参数，5–9 阶 × 2 偏振 = 10–18 个数据点"。参数维度差约 2 倍，数据维度差 4–6 倍。更严重的是"30–50 个谐波阶次"与申请书自家口径全面冲突：Kozák 2023 标定 MoS₂ 截止 7–11 阶（scheme L33 引用）、实验方案积分测量 3–11 阶（scheme L37）、content R2 用 5–9 阶——TMDC 莫尔体系 3 μm 驱动下不存在 30–50 阶谐波，60–100 数据点的前提不成立；"有效数据秩仅约 10"无引文无推导。
- 违反条款：indicator_red_lines.consistency_check；scoring_rubric.rigor 0.60–0.69 档"指标矛盾"；R5 P0 第一项跨轮未动
- 建议：以 content/scheme 的 12–24 实参数 / 10–18 数据点口径重写 L47；"有效秩"若保留须给出计算方式或删除；注意修完后 12–18 区间参数与数据维度相等，欠定论证应改写为"参数维度不低于数据维度，且扭转角—莫尔势耦合使解流形退化"，不能再说"参数维度超过数据维度"一刀切。
- action：rewrite / recalculate ｜ P1

### [critical] citation_error — C2：Hohenleutner 2015 条目三要素全错（Crossref 实锤），scheme 对该文献的物理内容描述失实，且自述"已双向核对"为虚假声明（R5-C3 复发并升级）
- 位置：references.md L33（[9]）+ scheme.md L31 + references.md L129
- 问题：条目标题"Scattering-type bordedom high-harmonic generation in solids"（"bordedom"非英语词，人工反馈 08-18 已点名，第 9 天未改）；卷期"Nature 517, 342–346 (2015)"；DOI 10.1038/nature14020。**本轮 Crossref 直查实锤**：该 DOI 实际指向 Bird et al., "NAD captureSeq indicates NAD as a bacterial cap for a subset of regulatory RNAs", Nature 519, 374–377 (2014)——一篇细菌学论文。标题检索确认 Hohenleutner 2015 真实条目为：Hohenleutner et al., "Real-time observation of interfering crystal electrons in high-harmonic generation", **Nature 523, 572–575 (2015), DOI: 10.1038/nature14652**。即标题/卷/页/DOI 四要素全错。连带失实：scheme L31 将该文描述为"首次观测 flat band 体系中电子群速度趋近于零导致的带间加速电流崩溃，实验证明 flat band 淬灭效应"——真实论文是 WSe₂ 晶体电子干涉的实时观测（interfering crystal electrons），并非 flat-band 群速度淬灭实验，WSe₂ 也不是 flat band 体系；scheme 的"flat-band 产额压制机制的完整链条"（Molinero 理论 + Hohenleutner 实验）在实验端引证不成立。references L129 自称"全部 35 篇已于 2026-08-13 与 Crossref + OpenAlex 双向核对"与事实矛盾（ai_policy_2026："不得使用未经核实的内容"）。
- 违反条款：section_standards.references"无张冠李戴"；modification_priority.P1"引用格式错误"；ai_policy_2026
- 建议：整条按 Crossref 实测重写为"Hohenleutner M., Langer F., Schubert C., et al. Real-time observation of interfering crystal electrons in high-harmonic generation. Nature 523, 572–575 (2015). DOI: 10.1038/nature14652"；scheme L31 的机理描述同步改写（可改为"晶体电子干涉对 HHG 的调制已在 WSe₂ 中实验分辨，为强场能带动力学提供实验方法学先例"，不得再声称 flat-band 淬灭实验验证）；删除或改正 L129 的核对声明。
- action：verify / rewrite ｜ P1

### [critical] citation_governance — C3：引文—正文对应矩阵系统性数字失实（自述 156 vs 实测 78），7 条目虚高 + 4 幽灵引用 + 备选三口径（R5-C4 复发并恶化）
- 位置：references.md L3 / L121–L131 + references-worklog-20260827.md（矩阵）
- 问题：实测三章 [CITE] 合计 **78 处 / 24 个独立标签**（rationale 45 + scheme 30 + content 3），references L3/L121 自述"25 篇正文实际引用（共 156 处）"。矩阵逐条比对（声称 → 实测）：molinero 22→13、mrudul 18→8、hu_meng_pnas 17→7、nikola 13→4、kozak 12→4、hu_meng_prl 3→0、amato 3→0；bistritzer 标"0 次备选"实测 rationale 3 次；矩阵标注为实际引用的 ikeda、soejima、nuckolls、xie 四标签实测 0 次（幽灵引用）；r25 新引用的 ma_huang_you（rationale L37）与 wang_yu（L11）未入矩阵。备选计数三口径（L3"9 篇"vs L121"10 篇"vs 实测条目级 8 处备选标注）与同页百分比矛盾（L123"50.0%"vs L131 注"48.6%"）延续。根源判明：r25/r26 修复把 content.md 的 [CITE] 标签整批剥离（48→3，见 H6），矩阵数字未随之重跑。
- 违反条款：indicator_red_lines.consistency_check（自述统计口径）；section_standards.full_review"正文有[N]角标对应"；R5 P0 第四项跨轮未动
- 建议：以脚本重跑三章计数，矩阵全部数字按实测 78 处重写；删除 4 个幽灵行或恢复正文引用；备选统一为条目级单一计数；统计段与更新注百分比按同分母重算。
- action：recalculate / rewrite ｜ P1

### [critical] red_line·novelty_claim_cautious / no_exaggeration — C4：优先权与可行性表述红线群（"唯一可行路径"无支撑独断、"尚未见报道"×2 无检索范围限定、r25 优化记录虚假执行声明）
- 位置：content.md L5；rationale.md L13 / L35 / L51；rationale.md L114
- 问题：(a) content L5"固体高次谐波产生提供的亚周期、全光、非接触探测窗口是莫尔量子态超快读出的唯一可行路径"——"唯一可行"为无支撑绝对化独断：超快电子衍射、时间分辨 ARPES、阿秒条纹等均为亚皮秒竞争路径，此处应写"最具潜力的路径之一"并给出一项对比依据；(b) rationale L13"光 Floquet 工程在莫尔关联态上的实验验证尚未见报道"、L35/L51 同句式共 3 处——其中 L85 已示范合格写法（"据团队 2026-08 检索，尚未见报道"），L13/L35/L51 无检索范围与截止日期，属 indicator_red_lines.novelty_claim_cautious 明令情形；(c) rationale L114 优化记录声称"拆分所有超 150 字句子"——人工红线是 120 字，实测 >120 字句仍 14–20 处，writer 按自降的标准宣称"全部拆分"，构成对管线与评审的双重失实陈述。
- 违反条款：indicator_red_lines.novelty_claim_cautious；no_exaggeration；ai_policy_2026；2026-08-18 人工审核语言规范
- 建议：content L5 改"是莫尔量子态亚周期读出少数兼具非接触与能带敏感性的路径之一"；L13/L35/L51 统一补"据团队 2026-08 检索（Web of Science / arXiv，关键词 moiré + Floquet / high-harmonic）"限定；L114 优化记录按 120 字红线重写执行并如实记录。
- action：rewrite ｜ P1

### [high] citation_governance — H1：同一文献两种作者归属并存（Nikola vs Shan），rationale/content 9 处用错（R5-H5 复发）
- 位置：rationale.md L29/L53/L69/L83（4 处）+ content.md L25/L27/L29/L81/L115（5 处）vs scheme.md L43 + references.md L81（[23] 真实第一作者 Shan J.-Y.）
- 问题：Nature 600, 235–239 (2021) 第一作者是 Shan J.-Y.；"Nikola"不出现在 references 任何条目作者列表中。rationale 作为本轮聚焦章节有 4 处" Nikola 等 2021 年在 *Nature* 上"，评审按作者索引将直接失配。
- 违反条款：section_standards.references"无张冠李戴"；R5 同项跨轮未动
- 建议：聚焦章节优先：rationale 4 处改为"Shan 等 2021"；content 5 处同步；检查 [CITE:nikola_nature_2021] 标签名是否一并改为 shan_nature_2021。
- action：rewrite ｜ P1

### [high] red_line·consistency_check — H2：探针/调控强度窗口三处三口径，且 I_c 下限落入探针弱场区，"不扰动读出"承诺被自家物理推翻（R5-C2 复发）
- 位置：scheme.md L7 vs L37 vs L63；rationale.md L71（I_c 区间）
- 问题：(a) scheme L7 定义探针模式"弱场 I < 10¹¹ W/cm²（线性响应区边缘）"，L37 又写"探针模式工作强度为 10¹¹–5×10¹¹ W/cm²"——同章两窗口交集为空；(b) "低于损伤阈值 2 倍"仅对区间上限 5×10¹¹ 成立（10¹¹ 低 10 倍）；(c) 物理矛盾：rationale L71 给出 I_c = 8×10¹⁰–3.2×10¹¹ W/cm²，其下限 8×10¹⁰ 低于探针弱场上限 10¹¹——若样品关联能隙为 5 meV，"弱场读指纹"本身即熔化关联态，与 §1.1"在不扰动莫尔体系的前提下读出"的立题逻辑冲突；(d) 调控窗口上限 10¹² 恰等于损伤阈值，无余量声明。
- 违反条款：indicator_red_lines.consistency_check；no_exaggeration；uncertainty_constraint（读出与改写两种模式未声明隔离条件）
- 建议：探针窗口定为单一区间且与 I_c 下限显式解耦（如探针 I ≤ 5×10¹⁰，低于最小预期 I_c 下限；或声明 Δ_CI ≤ 5 meV 样品改用低温/长波策略规避）；"低于损伤阈值 N 倍"按区间端点分别表述；调控上限改 8×10¹¹ 并注明损伤余量。
- action：rewrite / verify ｜ P1

### [high] red_line·consistency_check — H3：样品角度精度同章矛盾（±0.05° vs ±0.1°），且反演分辨率指标与先验同值使指标失去考核意义（R5-H3 复发）
- 位置：content.md L61（"样品制备精度 ±0.05°"作反演硬约束先验）vs content.md L129（Y1 样品"角度精度 ±0.1°"）；scheme.md L23 同先验表述
- 问题：先验声称制备精度 ±0.05°、年度计划承诺 ±0.1°，同章矛盾；更实质的是 Y3 考核指标"扭转角分辨率 ±0.05°"与硬约束先验 ±0.05° 同值——若扭转角已被先验约束到 ±0.05°，反演达到 ±0.05° 不构成独立信息。
- 违反条款：indicator_red_lines.consistency_check；indicator_measurable
- 建议：统一口径（建议 ±0.1° 为制备值、±0.03° 为椭偏标定值，写清来源）；指标改为优于先验的可分辨增量（"在 ±0.1° 先验下将后验分辨率压缩至 ±0.05°"并说明判据）。
- action：rewrite / recalculate ｜ P1

### [high] red_line·novelty_claim_cautious / implementation_path — H4：假设 1/2 的文献依据被过度延伸，假设 2 阈值与自家 I_c ∝ Δ² 标度数值不自洽（R5-H4 复发）
- 位置：rationale.md L83 vs content.md L23/L25/L27；content.md L79
- 问题：(a) rationale 称假设 1（0.1° → 椭偏变化 >5%）"依据 Mrudul 等 2024 年椭偏依赖曲线斜率推算"——Mrudul 2024 是 magic-angle TBG 连续模型计算，其斜率不能直接外推 TMDC 莫尔（1°–3°、带隙 1–2 eV、强自旋轨道耦合）体系；references [8] 声称的"外推至 TMDC 预期灵敏度 >5%"是本课题外推而非 Mrudul 结论。且 content L23 的假设 1 依据链已换成 Xiao 2012 + Yao 2025 + Mrudul 三引组合——同一假设两章两套依据。(b) 假设 2 称 magic-angle TBG 约 3×10¹¹ W/cm² 出现谐波饱和，rationale L83 归于"Nikola 2021 调制门槛与 flat band 态密度估算"——该文并无 TBG 饱和阈值；按假设 3 同一判据（δW 达到特征能标），I(δW=10 meV) 应等于 I_c(Δ=10 meV)=1.6×10¹¹（content L79 自家数字），与 3×10¹¹ 差近 2 倍；W_flat 取值与换算链全文未给。
- 违反条款：novelty_claim_cautious（定量表述须有支撑）；implementation_path（方案→指标路径）
- 建议：假设 1 外推归属挪回本课题（"据 Mrudul 灵敏度量级与本课题 SBE 正向模型预估（Y2 输出）"），两章依据链统一；假设 2 给出 W_flat 数值与 I_sat = I_c(W_flat) 完整换算，或改阈值与 L79 公式一致。
- action：rewrite / verify ｜ P1

### [high] anti_ai — H5：超长句 >120 字共 20 处（程序）实测 14 处（独立复核），人工红线未达；8 个段落超范本 300 字上限
- 位置：rationale.md 全章；重灾区 L5（151 字）、L13（139 字 + 全段 685 字）、L21（147 字）、L25、L43（407 字段内两句 125/143 字）、L47（124 字，即 C1 段）、L77（123/137 字）、L79（138 字）、L83、L85（147 字）
- 问题：违反 2026-08-18 人工审核红线"单句不超过 120 字，超限句必须拆分"；范本 sentence_rhythm"单句超 120 字必拆分"。程序化 penalty 0.28 直接压制表达质量天花板至 0.72。r25 优化记录按 150 字标准执行，未达红线（见 C4c）。另 8 段 364–685 字为范本段长上限 1.2–2.3 倍。
- 违反条款：anti_ai_patterns"超长句"；programmatic long_sentences；2026-08-18 人工审核语言规范
- 建议：L13 五挑战段拆为总起段 + 每挑战一小段；全部 >120 字句按"估算前提→数值→含义"三句式拆分；以句号切分脚本复测清零后再提交程序化检测。
- action：rewrite ｜ P1

### [high] boundary / citation_governance — H6（新增）：content.md 引文标签在表达修复中被整批剥离（48→3），9 位作者实名提及零标注，文献声明失锚
- 位置：content.md 全章（仅存 L23 三处 [CITE]：xiao / prj / mrudul）
- 问题：content 正文"Molinero 等 2024 年在 *Optica* 上报道了…"（L7）、"Kozák 等 2023 年…实验报告"（L29）、"Lian 等 2024 年…实验证明"（L77）、"Ghimire 等 2011 年体相 ZnO HHG 标度"（L83）等 30+ 处实名文献陈述无 [CITE] 角标；L65"合成数据验证显示：仅 HHG 谱反演误差 >30%…"的数值结论失去文献/手册锚点。这既是引用规范违规（正文有实名无角标），也是 r25/r26 修复动作的副作用——修复"引用密度超标"时把 content 的标签全部删除而非合并降密，矫枉过正。
- 违反条款：section_standards.full_review"正文有[N]角标与参考文献对应"；content_boundaries（数值结论需可溯源）
- 建议：content 恢复关键论断处角标约 15–20 处（每条实名提及至少首次出现处挂标），数值结论补 [CITE] 或"见方法学手册 §x"锚点。
- action：add / rewrite ｜ P1

### [high] citation_governance — H7：[N]/[CITE] 双轨编号未统一 + [12] 编号重复 + Ma 2025 占位 DOI "xxxxx"（R5-H6 复发，人工两次点名）
- 位置：references.md 全文件 [1]–[35] 行首编号 vs 三正文 78 处 [CITE:]；L39 [12] Cao 与 L47 [12] Kozák 同号；L53 Ma 2025 "DOI: 10.1038/s41566-025-xxxxx"
- 问题：(a) 双轨制 9 天未动，提交系统按 [N] 解析得 0 匹配；(b) [12] 违反"编号连续无重复"；(c) "xxxxx" 为占位 DOI（Crossref 实测不存在），且 rationale L37 聚焦章节正文正引用该条目——聚焦章节引文挂在假 DOI 上；人工反馈 08-18 点名，第 9 天。
- 违反条款：section_standards.references 全部 5 条；modification_priority.P1"占位符未清"
- 建议：定死编号策略（推荐正文 [CITE:] 全量替换为 [N]，references 已编号）；重编消除 [12] 重复；Ma 2025 查实 DOI 或改"DOI 待刊出（preprint）"并附 arXiv 号。
- action：rewrite / verify ｜ P1

### [high] citation_error — H8（新增，Crossref 实测）：多条目要素精度错误——Lian 页码不符、Kozák 第一作者应为 Peterka、PRJ 2025 条目在正文被引为"2024 年"
- 位置：references.md L95（[27] Lian）、L47（[12] Kozák）、rationale.md L25
- 问题：(a) Lian 条目"Nature Physics 20, 1172 (2024)"——Crossref 实测 DOI 10.1038/s41567-023-02266-2 为 Nature Physics 20, 34–39（2023 年 12 月上线/2024 年 1 月刊），页码 1172 无法解释，疑为占位或错抄；(b) Kozák 条目"Kozák M. 等"——Crossref 实测 10.1063/5.0158995 第一作者为 Peterka（Kozák 为通讯/资深作者），按引用惯例应写"Peterka 等"或在正文注明依据 Kozák 组；(c) rationale L25"2024 年 *Photonics Research* 的工作 [CITE:prj_2024_2dberry]"——该条目（PRJ 13(5), 1235）Crossref 实测为 **2025 年 Yao et al.**，正文年份引用错误。
- 违反条款：section_standards.references"无张冠李戴（作者、期刊、年份与实际一致）"
- 建议：三处按 Crossref 实测改正；rationale L25 改"Yao 等 2025 年在 *Photonics Research* 上"。
- action：verify / rewrite ｜ P1

### [medium] anti_ai — M1：结构元话语残留（"递进"×7、"叙事弧线"、句首"层面："scaffold）
- 位置：rationale.md L13/L15/L19/L41/L57/L75/L89（"递进"7 次）、L97（"整章沿…形成完整的叙事弧线"）、L21/L23/L31（"理论方法层面：""方法学层面，""在实验层面，"）
- 问题：范本不自我描述结构；"递进"高频属结构性自我标注，程序 meta_discourse 词表（0 命中）未覆盖，漏网元话语。
- 违反条款：anti_ai_patterns"空洞概括句/元话语"；rationale_anchor"段间以内容逻辑衔接"
- 建议：L97 全句删除；"递进"保留 ≤3 处，其余改为直接因果陈述；句首"X层面："改为内容主语开头。
- action：rewrite ｜ P2

### [medium] structure — M2：国内研究现状层薄弱，五层递进第 4 层不成层（R5-M2 复发）
- 位置：rationale.md §1.2（仅 L37 一段 108 字，北京大学 Ma 2025）
- 问题：section_standards.rationale 第 1 条要求"国内现状"独立成层；references 自列 5 个国内组（Hu/Meng、Zhou/清华、Wang/复旦、Wang/中科院、Yao/张江）无一进入叙述。
- 建议：§1.2 末补约 250 字国内现状段（清华 Zhou 黑磷 Floquet、物理所 Hu/Meng 反演母方法学、复旦-SIOM Wang、北大 Ma 相位匹配），并与 §1.5 定位衔接。
- action：add ｜ P2

### [medium] narrative — M3：§1.1 与 §1.3 共享五要素定量链，五挑战段单段 685 字（R5-H7 降级残留）
- 位置：rationale.md L13（§1.1）vs L43（§1.3）
- 问题：L_M ≈ 12.8 nm 公式、11,000 原子、10⁵ 核时/角、100×100 k 网格、8 轨道 Wannier 五要素在 30 行间距内两遍完整出现，Bistritzer 引证也两遍；五层递进要求 §1.1 点到为止、§1.3 展开定量。
- 违反条款：writing_style_rules.must"五层递进"；full_review"无跨章节内容重复"
- 建议：§1.1 挑战段压缩为定性版（每挑战一句，定量见 §1.3），全部定量链只保留在 §1.3。
- action：rewrite ｜ P2

### [medium] narrative — M4：rationale 单章引用密度 45 处，为范本 3 倍
- 位置：rationale.md 全章
- 问题：style_benchmark.citation_style"正文编号引用 10–17 次即可，编号引用用于关键论断处"；45 处使几乎每个定量句挂标（molinero 单标签 5 次）。
- 建议：压至 25–30 处，非关键处合并引用或移文末研读基础。
- action：rewrite ｜ P2

### [medium] structure — M5：体量 4535 中文字低于 5000 参考下限，缺口对应论证缺口
- 位置：rationale.md 全章
- 问题：字数非门限（v6.9.55），但本案短在实质论证：国内现状层（M2）、莫尔势—扭转角耦合机理句（C1 修复伴随）、假设 3 外推限定（H4 修复伴随）均需增补；补足后预计 5000–5300 字，属"补论证"而非"注水"。
- 建议：随 M2/C1/H4 修复自然扩容，不单独注水。
- action：add ｜ P2

### [low] hygiene — L1：管线优化记录/更新注滞留正文
- 位置：rationale.md L114（r25 优化记录）、references.md L131（r28 注）
- 问题：面向评审的正文不应携带轮次内账；定稿前须移除。
- action：remove ｜ P3

---

## 六、跨章节一致性核验表（简要）

| 检查对 | 状态 | 定位 |
|---|---|---|
| §1.3 反演维度 ↔ §2.2/§3.2 | ✗ 冲突 | C1 |
| §1.4 I_c ↔ §2.2 靶标A ↔ §3.4/手册 | ✓ 数值一致（8×10¹⁰–3.2×10¹¹） | 但见 H2 窗口矛盾 |
| §3.1 探针窗口 ↔ §3.3 探针窗口 | ✗ 同章矛盾 | H2 |
| §2.2 先验 ±0.05° ↔ §2.4 样品 ±0.1° | ✗ 同章矛盾 | H3 |
| 假设 1 依据链 §1.5 ↔ §2.1 | ✗ 两套依据 | H4 |
| 假设 2 阈值 3×10¹¹ ↔ I_c 公式 1.6×10¹¹@10meV | ✗ 不自洽 | H4 |
| 损伤阈值 10¹² 三章 | ✓ 一致 | — |
| 材料口径 tMoS₂/tWSe₂ 1°–3° + TBG 1.1° | ✓ 一致 | — |
| 降阶 2×10⁴ 核时 / 4 个数量级 / <5% / <6% | ✓ 三章一致 | — |
| 扭转角 ±0.05° / RMS<15% / SNR=50 | ✓ 三章一致 | 但见 H3 指标-先验同值 |
| Nikola/Shan 作者归属 | ✗ 跨章分裂 | H1 |
| PRJ 年份 2025（条目）↔ 2024（rationale 正文） | ✗ | H8 |
| 引用计数自述 156 ↔ 实测 78 | ✗ | C3 |
| content 正文角标 ↔ references 条目 | ✗ 大面积脱钩 | H6 |

---

## 七、维度评分与依据（scoring_rubric 逐档对照）

| 维度 | 权重（本轮等权 0.25） | 得分 | rubric 档位依据 |
|---|---|---|---|
| 创新性 | 0.25 | 0.84 | 0.80–0.89 档："在已有方向上提出新视角/新方法/新机制，与前人有清晰区隔"——R1 降阶框架（对照 Molinero/Mrudul 无多体修正）、R2 莫尔自由度反演（对照 Hu/Meng 均匀体系）、R3 莫尔 Floquet（对照 Zhou/Tyulnev 非莫尔）三重划界清晰且各章一致；扣分：假设 1/2 定量预言依据链弱（H4）、"唯一可行路径"独断（C4a） |
| 可行性 | 0.25 | 0.72 | 0.70–0.79 档："基本可行但存在风险点，部分关键技术缺少预研验证"——降阶/反演/调控各有文献背书与降级路径；扣分：探针窗口与 I_c 重叠的原理性矛盾（H2）、角度先验矛盾（H3）、假设 2 阈值换算链缺失（H4）、flat-band 产额机制的实验端引证失实（C2） |
| 严谨性 | 0.25 | 0.62 | 0.60–0.69 档："存在事实错误、指标矛盾、关键论证环节缺失"——4 项 critical（维度口径 C1 / Hohenleutner 实锤 C2 / 矩阵失实 C3 / 优先权红线群 C4）+ 9 项 high 中 5 项为 red_line 条款（H2/H3/H4/H8）；按 v6.9.25 评分纪律 red_line 违规压至 0.6–0.7 区间，取 0.62（较 R5 的 0.62 持平：C 级数量未减，但新增 Crossref 实证使定性更扎实） |
| 表达质量 | 0.25 | 0.70 | 程序化天花板 0.72 内取值。0.70–0.79 档："表达一般，有一定比例的模板套话或 AI 痕迹，部分段落逻辑松散"——超长句 20 处（penalty 0.28）与 8 段超 300 字（H5）、结构元话语（M1）；但骨架叙述式合规、修饰词 46→36 治理有效、关联词仅 3、加粗清零，未落入 0.60–0.69 档 |

综合评分 = (0.84 + 0.72 + 0.62 + 0.70) / 4 = **0.72**

锚点绑定校验：结论"基本接近" → 表达 ≤0.79 ✓（0.70）、综合 ≤0.89 ✓（0.72）；表达 ≤ 程序化天花板 0.72 ✓。评分自洽复核：0.84+0.72+0.62+0.70 = 2.88，÷4 = 0.72，无舍入误差。

---

## 八、对抗结论

- 本轮发现 18 个问题（critical:4, high:8, medium:5, low:1）
- 相比 R5（4C/7H/6M/1L，综合 0.68）：**改善 3 项**（冗余修饰词治理到位、核心问题三重陈述消除、超长句最长值 399→151 字）；**未解决 12 项**（R5 全部 4 项 critical 原文逐字未动 + H3/H4/H5/H6/H7 作者与编号类 + M1/M2/M6 残留）；**新增 4 项**（content 引文标签整批剥离 H6、多条目要素错误 H8、体量缺口显性化 M5、r25 虚假执行声明计入 C4）
- **跨轮顶风警示**：R5 列为 P0 的六项（C1/C2/C3/C4/H5 作者归属/H6 编号）在 R5 落盘后三章正文零写入（mtime 证据），修复优先级指令未进入 writer 执行路径；人工反馈两次点名的 xxxxx DOI 与 bordedom 错字已持续 9 天未改
- 表达维度确认进步：天花板从 R5 的 0.50 升至 0.72，修饰词与句长极值治理有效——但 120 字红线（非 150 字）与段长上限仍未达
- 是否达到输出标准：**否**——综合 0.72 < 人工达标线 0.80 < 配置阈值 0.85；max_high_issues=0 而现有 critical+high 共 13 项
- 返工优先级：
  - **P0**：C2 Hohenleutner 整条重写（Crossref 实测值已给出）→ C1 维度口径统一 → C3 矩阵按实测 78 处重算 → H1 Nikola→Shan（聚焦章节 4 处优先）→ H7 编号统一+[12]消重+xxxxx 清除 → H8 三处要素改正（六项均为脚本可半自动完成的引文/数字硬伤）
  - **P1**：H5 超长句按 120 字红线清零 → H2 强度窗口与 I_c 解耦 → H3 角度口径 → H4 假设 1/2 依据链自洽 → H6 content 角标恢复 → C4 优先权限定语
  - **P2**：M1 元话语 → M2 国内现状段（连带 M5 体量）→ M3 §1.1/§1.3 去重 → M4 引用密度 → L1 管线注记
- 下一轮评审建议聚焦：P0 引文修复验收（脚本复测 DOI/编号/计数/作者四项 + Crossref 抽查）+ 表达天花板解除验证（>120 字句清零后重跑程序化检测）

## 评分
创新性：0.84
可行性：0.72
严谨性：0.62
表达质量：0.70
综合评分：0.72
