# 对抗评审报告（第 2 轮 · scheme.md 聚焦：研究方案 + 特色与创新 + 预期研究成果）

项目类型：general（面上项目）
聚焦章节：scheme.md §3.1–§3.9（研究方案、特色与创新、预期研究成果）
跨章一致性核查：content.md / rationale.md / references.md
评审日期：2026-08-27
评审依据：memory/nsfc-standards.json（general_principles.scoring_rubric v6.8.24 / section_standards.scheme / writing_style_rules + anti_ai_patterns / indicator_red_lines / reference_materials.benchmark_anchors / project_types.general）
说明：prompt 所引 programmatic_checks 与 overall_review_requirements 两键在 nsfc-standards.json 中不存在（实测 general_principles 下共 12 键，无此二者），按纪律不虚构其规则，程序化检测以 prompt 附带报告为准。

---

## 0. 评审前置核查（检测对象对账 + 文件归属）

按跨轮记忆纪律完成三项前置核查：

1. **检测对象对账**：程序化报告称全文字符数 20373。实测 scheme.md 8261 字符 + content.md 5291 + rationale.md 6817 + 2×2 分隔符 = 20373，精确匹配。检测对象为三章节拼接，非对象错位。分章复核超长句：scheme.md 13 处、content.md 7 处、rationale.md 12 处；检测例句（"堆叠几何与自旋取向""MnTe 370 meV""Ruiz-Tijerina"）全部出自 rationale.md，属拼接检测正常现象，不报 [high] 错位。
2. **文件归属核查**：05_review/ 原有 critic-round-2.md（8-19 21:19，48854 字节）经字节级比对与 critic-round-2.archive-scheme.md 完全相同——管线已归档腾位，本报告按指令安全覆盖写入，无覆盖事故风险。
3. **管线时序事实**：scheme.md mtime（8-19 19:00）早于上一轮 scheme 专项报告（8-19 21:19）；content.md mtime 8-19 21:08。即 writer 在上一轮 scheme 评审后未改动 scheme.md 一个字节，本轮 scheme 侧问题大量"未解决"是管线事实而非误报。上轮 scheme 侧 3 critical + 6 high **零修复**。

## 1. 模块完整性检查

scheme.md 含：§3.1 总体方案与技术路线 / §3.2–§3.4 三个分方案 / §3.5 关键技术难点 / §3.6 可行性分析 / §3.7 特色与创新（3 点）/ §3.8 预期研究成果 / §3.9 年度研究计划（含 Go/No-Go 判据）。
对照 section_standards.scheme 五条清单："总体方案+技术路线+分方案+可行性分析"模块齐全 ✓；"为什么选这个方法"论证存在（§3.2 TDDFT vs 紧束缚、§3.3 磁点群 vs 数值求解，为本章最大亮点）✓；"可行性不复述方案细节" ✗（§3.6 大段复述 §3.2/§3.4 的文献先例，见 H5）；"关键难点有解决方案" ✓（ALDA/Rashba 干扰/降级实验三难点均有路径）；"不出现为什么研究口吻" ✗（§3.5 难点三，上轮已报未修复）。
四模块中 2 项不通过。模块层面基本完整，但结构合规 2/5 未过线。

## 2. 执行清单对照（逐条通过/不通过）

| # | 执行清单条目 | 判定 | 证据定位 |
|---|---|---|---|
| 0 | 模块完整性 | 部分通过 | §3.1–§3.9 齐全；但 §3.5 与 §3.6 功能重叠（见 H5） |
| 1 | 读取申请书 + 标准配置 | 通过 | 四章节 + nsfc-standards.json 全量读取，含 scoring_rubric 五档、benchmark_anchors、anti_ai_patterns |
| 2 | 逐条对照执行清单 | 通过 | 本表即对照结果 |
| 3 | 锚点对比（结构化 + 结论行） | 通过 | 见第 4 节，结论=差距明显 |
| 4 | 引用程序化检测结果入清单 | 通过 | 见 H1/H2/H3，anti_ai 三项超标全部入清单 |
| 5 | 按项目类型标准红队评审 | 通过 | 问题清单 32 条，每条标注 rubric/红线条款 |
| 6 | 写作风格重点检查 | 部分不通过（申请书侧） | 知识罗列无、bullet 无、方法选择论证达标；但超长句/关联词/模板句超标 + 跨章逐字重复（H6） |
| 7 | 每问题给可执行建议 + 条款 | 通过 | 问题清单逐条给 rewrite/verify/recalculate 指令 |
| 8 | 严重度分级 | 通过 | critical 10 / high 12 / medium 8 / low 2 |
| 9 | 叙述式：科学问题为主线 | 通过 | §3.1 双平台×双范式围绕核心科学问题组织；R1→R2→R3 以"驱动→读出→分离"衔接 |
| 10 | 叙述式：无 A做了X/B做了Y 堆砌 | 基本通过 | scheme 引用多为论证嵌入；但 §3.3 "Morimoto 等人 2504.18845 的理论工作证明…"为孤立例证句且文献虚构（C9） |
| 11 | 叙述式：无 bullet 替代论证 | 通过 | 全文无 bullet；表格仅用于年度计划，合规 |
| 12 | 叙述式：段落过渡递进 | 部分通过 | §3.2→§3.3→§3.4 递进尚可；§3.5→§3.6 内容回头重复，逻辑非递进（H5） |
| 13 | 方案说明"为什么选这个方法" | 通过 | §3.2 L13、§3.3 L27 两处"选择 X 而非 Y 的理由"，对标 scheme_anchor 达标，为本章亮点 |
| 14 | 立项依据五层递进（简要） | 通过（非聚焦） | rationale §1.1–§1.5 五层结构在位 |
| 15 | 研究目标含量化指标（简要） | 通过（非聚焦） | content §2.5 三目标均带量化指标；但 3σ 口径混乱（H12） |
| 16 | 特色创新四步闭环 | 部分通过 | 三点均有"局限→方案→量化优势"骨架，但创新点一绝对化宣称（C8）、收束句模板化（M4） |
| 17 | anti_ai：死板关联词 | **不通过** | 拼接全文 21 次（阈值 20，"同时"16 次），扣 0.02；scheme 本体"同时"5 次（H2） |
| 18 | anti_ai：模板句式"为…提供…" | **不通过** | 9 次（阈值 8），扣 0.03（H3） |
| 19 | anti_ai：模板主语滥用 | 通过 | scheme "本项目拟"0 次、"本项目将"1 次 |
| 20 | anti_ai：超长句 >120 字 | **不通过** | 31 处（免赔 5），扣 0.52；scheme 本体 13 处占 12.6%，范本为 0（H1） |
| 21 | 红线：指标跨章一致 | **不通过** | D_sep 双定义（C6）、指纹量 5 vs 3（C7）、Floquet 场强口径（M2）、3σ/90%/70%（H12） |
| 22 | 红线：物理约束不冲突 | **不通过** | 0.4 V/Å≈4 MV/cm 换算错 10 倍，40 MV/cm 实际远超 R1 窗口两个量级（C5） |
| 23 | 红线：理论适用条件 | 部分不通过 | ALDA 失效边界有讨论（§3.5 难点一，达标）；Volkov 近似适用条件未注明（H8） |
| 24 | 红线："首次/从未"有支撑 | **不通过** | 创新点一"从未被作为独立动力学变量引入"无检索声明支撑，且被 2403.06531 先例部分推翻（C8） |
| 25 | 红线：方案→指标路径 | 部分通过 | 多数指标有路径；THz 泵浦频率缺失使磁序激发指标路径断链（H10） |
| 26 | boundary：方案章无"为什么研究"口吻 | **不通过** | §3.5 难点三为可行性内容（H4，上轮未修复） |
| 27 | boundary：可行性不复述方案 | **不通过** | §3.6 复述 §3.2/§3.4 文献先例（H5） |
| 28 | boundary：跨章不大量重复 | **不通过** | §3.1 核心科学问题句、范式 A/B 句与 content §2.1 逐字重复（H6） |

## 3. 写作风格评估（引用程序化检测）

程序化检测天花板 0.50 —— **程序化检测发现AI写作模式，表达质量被强制限制**（上限 0.50）。

- 死板关联词 21 次（阈值 20，罚 0.02）：其中"同时"16 次，是典型的高频机械衔接。scheme 本体"同时"5 次（L15/L29/L37/L49/L57），如 §3.4 L37 "THz 泵浦脉冲……激发磁序动力学……同时触发层间滑移模式的相干振荡"、§3.6 L63 连续两句内出现。建议改写为内容驱动衔接（"进而、据此"或直接以物理对象开头）。
- 模板句式"为…提供…"9 次（阈值 8，罚 0.03）：scheme 本体 7 次，密度最高的 §3.2 L19 连续三句内两次（"为本方案提供了原理可行性先例"）、§3.7/§3.8 段尾成串（"为弱信号的实验探测提供了可行路径""为后续研究与材料筛选提供可重复使用的诊断工具""为后续实验验证提供工程化依据"）。anti_ai_patterns.quantitative_thresholds 上限 15 次未破，但程序化阈值 8 已破，须清理至全文 ≤8。
- 超长句 >120 字共 31 处（免赔 5，罚 0.52，最重项）：scheme 本体 13 处（103 句中占 12.6%），含 165 字（§3.8 L91）、161 字（§3.3 L31）、148 字（§3.9 L108）、139 字（§3.3 L27）四个极值句。范本 sentence_rhythm 明确"单句超 120 字必拆分"、范本实测超 120 字占比为 0。上轮已报 11 处（9.3%），本轮不降反升至 13 处——writer 未执行任何拆句。
- 达标项：meta_discourse 0、bullet_list 0、self_reference 0、excessive_bold 每千字 0.74（阈值 3）——scheme 无 PPT 化、无空洞元叙述，叙述式骨架是好的。

结论：scheme.md 的**结构叙事与方法选择论证符合范本精神**（这是与上轮相比值得肯定的存量优点），但句子工程（超长句）与机械衔接全面超标且较上轮恶化，加上零 [N] 角标的引用体例（C3），表达质量距范本仍有代差。

## 4. 锚点对比（scheme_anchor / innovation_anchor）

**对比一：方法选择论证（scheme_example 锚点）**
- 申请书原文（§3.2 L13）："选择 TDDFT 而非纯紧束缚的理由在于：层间滑移驱动的自旋劈裂切换涉及光致载流子激发对电荷密度的自洽反馈——这一过程必须通过自洽场迭代捕捉，无法在固定紧束缚框架下近似处理。"
- 锚点（scheme_example）："为了适应本项目的研究，需要在理想晶体的计算中引入杂质的作用，本项目将采用在周期性排布的原子结构中引入少量杂质原子来模拟掺杂半导体。首先，求解定态本征值问题获得……"
- 差距：结构上达标——两者都是"为什么选这个工具链+分步流程"；申请书甚至比锚点多了对比论证（"而非纯紧束缚"），论证密度不输范本。差距在配套：锚点段落句长全部 <100 字，申请书同类段落（L13 共 139 字单句）把三条理由塞进一句，可读性反而低于范本。**改写方向：保留对比论证骨架，把 139 字句拆为 2–3 句。**

**对比二：可行性分析的链式结构（scheme_anchor 特征描述）**
- 申请书原文（§3.6 L63）："原理成立性：THz 驱动层间剪切声子的原理已在 h-BN 体系（文献 2403.06531）中被数值验证，3–4 ps 翻转时间与 0.4 V/Å 阈值电场的参数与本方案 R1 的 0.1–1.0 MV/cm 场强范围处于同一量级。"
- 锚点（scheme_anchor）："可行性分析遵循'方案→原理→结论'链式论证，不复述方案细节。"
- 差距：形式上 §3.6 有"原理成立性→关键指标可达性→结论"三段链式，骨架达标；但实质上该段是对 §3.2 L19 先例的逐句复述（同一篇文献、同一参数），违反锚点"不复述方案细节"；且引用体例用裸 arXiv ID 而非范本 citation_style 的"'某人等人[N]在期刊上报道了X'"嵌入式角标；更要命的是数值本身错误（0.4 V/Å = 40 MV/cm ≠ 4 MV/cm，与 0.1–1.0 MV/cm 相差 40–400 倍，"同一量级"不成立，见 C5）。
**改写方向：可行性段只做"原理→指标"映射，先例引用保留一处（分方案内），数值必须换算复核。**

**对比三：创新点闭环（innovation_example 锚点）**
- 申请书原文（§3.7 创新点一 L73）："现有文献中，层间滑移自由度从未被作为独立动力学变量引入强场超快物理研究框架——晶格自由度在 HHG 研究中通常以热声子背景或准静态结构调制的方式影响电子动力学，而非主动参与超快动力学过程。本项目将层间滑移坐标从'被调控的对象'提升为'主动参与超快动力学的驱动变量'……"
- 锚点（innovation_example）："掺杂半导体高次谐波产生过程中存在许多局域电子散射过程，杂质原子对周期性势场的破坏及局域电子态的引入使得电子运动过程变得更为复杂。本项目根据费曼路径积分理论，通过引入散射传播子建立包含局域电子态效应的量子轨迹模型，是本项目的创新之处。"
- 差距：申请书四步闭环完整度高于锚点（多了"量化优势"段），每点字数 240 字上下 vs 锚点约 200 字，基本匹配。差距有二：其一，锚点对"局限"的陈述是机理性的、可检验的，申请书用"从未被……"绝对化全称判断且无检索范围声明——恰好踩中 novelty_claim_cautious 红线，且 2403.06531（光激发剪切模驱动滑移动力学）已构成反例张力；其二，收束句"有望为二维材料强场超快物理开辟一个新的研究方向"接近 anti_ai_patterns 的空洞概括句，锚点收束是"是本项目的创新之处"式的克制定位。**改写方向：'从未'改为带检索边界的限定表述（'据截至 2026-08 的检索，在……范围内尚无……'，与 rationale §1.5 L63 的检索声明口径统一），收束句改为具体定位。**

语体 / 论证密度 / 数据驱动 / 引用嵌入四项逐项判定：语体（叙述式骨架）基本接近；论证密度（方法选择处）接近、（可行性段因复述而空转）差距明显；数据驱动达标（参数密度高且具体）；引用嵌入（零 [N] 角标 + 裸 arXiv ID + "文献 N"散文体例 + 文献真实性存亡问题）差距明显。

锚点对比结论：差距明显

## 5. 历史遗留问题核对（13 条逐项）

| 历史问题 | 归属 | 本轮实测 | 状态 |
|---|---|---|---|
| content 超长句 13.6% | content | 7 句 >120 字（10.3%） | **仍存在**（略降未达标）→ H11 |
| content §2.4/§2.5/§2.6 Floquet 场强上界缺失 | content | §2.4 L39 已补"上限 0.3 MV/cm"；§2.5 目标三（L51）、§2.6 问题三（L61）仍无上界 | **部分解决** → C10 |
| content §2.3 L27 [17] Ghorashi-Rappe 错配 | content | L23 现为 [18] | **已解决** |
| content §2.4 [21] Yarmohammadi 错配（含 rationale L25） | content/rationale | content L39 现为 [22]，rationale L25 现为 [22] | **已解决** |
| content 9 句 >120 字 | content | 7 句 | **仍存在** → H11（与第 1 条同源） |
| content 7 处 arXiv 裸引 | content | 本轮扫描裸 arXiv ID = 0 | **已解决** |
| §2.5 目标二 vs §2.6 问题二量级跳跃 | content | 80%/90%/70%/3σ 四数字仍并存认换算关系不明 | **仍存在** → H12 |
| content §2.1 / rationale [11] 绑 5 体系 | content/rationale | L7/L31/L53 仍以单一 [11] 支撑 NiCl₂/VS₂/CrSe₂ 势垒 16–40 meV + 普遍性论断；且 [11] 卷页真实性本轮 Crossref 未命中（见 C1 附注） | **仍存在** → H9 关联 |
| content "针对瓶颈一/二/三"僵硬平行结构 | content | 已改为"按'驱动→读出→分离'的逻辑链组织" | **已解决** |
| content §2.3 "两个特征"实为三个 | content | L27 现为"三个特征"并列一二三 | **已解决** |
| 记忆表行 4：rationale L25 + content [21] | — | 均已改 [22] | **已解决** |
| 记忆表行 5：content [17] 应为 [18] | — | 已改 [18] | **已解决** |

小结：content 侧 6 条已解决、4 条仍存、1 条部分解决——writer 对 content.md 的重写有效。但 **scheme.md 上轮 3 critical + 6 high 全部未动**（文件零修改），本轮全部按原文复报，severity 不降。另注意：已修复的 [18] 条目本身经 Crossref 反查 DOI 404（见 C1），修复了编号、修不了文献真实性。

## 6. 问题清单（P0 必改 / P1 强烈建议 / P2 建议）

### P0（critical）— 共 10 条

#### P0-1 [critical] rigor — references.md 系统性虚构文献 12 条，scheme.md 四处承重引用全部踩雷
- 位置：references.md [17] [18] [19] [21] [22] [23] [30] [32] [33] [34] [35] [36]；scheme.md §3.3 L29、§3.4 L47、§3.6 L63 承重引用
- 问题（本轮联网双源反查实证）：
  - arXiv API 反查（export.arxiv.org）：[30] 2408.11234 实为遥感生物量深度学习论文；[32] 2504.18845 实为 "Introducing Interval Neural Networks for Uncertainty-Aware System Identification"（作者 Ferah & Kumbasar）；[33] 2505.09237 实为算子代数 Haagerup 性质论文；[34] 2506.18439 实为量子下推自动机模型检验论文；[35] 2507.04513 实为推荐系统论文。五条均为"真实 arXiv ID + 虚构标题 + 虚构作者"的 LLM 伪造模式（[32] 还套用了领域知名作者 Morimoto）。
  - Crossref DOI 反查（api.crossref.org）：[19] 10.1103/PhysRevB.110.214301 实际标题为 plasmon/交换能主题；[21] 10.1103/PhysRevLett.134.056601 实际为 "Hidden Zero Modes and Topology of Multiband Non-Hermitian Systems"；[22] 10.1103/PhysRevLett.134.096901 实际为 "Exploring Single-Photon Recoil on Free Electrons"；[23] 10.1103/PhysRevB.111.184401 实际为镍酸盐超导主题；[36] 10.1103/PhysRevLett.133.246901 实际为稀土晶格 THz 动力学论文（其标题恰与另一篇真 arXiv 论文 2403.06531 相同——条目内部自相矛盾）。[17] [18] DOI 直接 404 不存在。
  - 对 scheme 的直接杀伤：§3.3 "Morimoto 等人 2504.18845 的理论工作证明 HHG 光谱能够编码量子度规和 Berry 曲率信息，为本方案的指纹理论提供了方法论基础"——支撑 R2 指纹理论的方法论文献不存在；§3.4 "继承 Yarmohammadi 等人（文献 21）的框架"——Floquet 理论源头不存在（[21] 实际是非厄米拓扑论文且作者也不是 Yarmohammadi）；§3.6 原理成立性的三条支柱中两条（文献 19/文献 21 体系）指向虚构或错配条目。
- 建议：P0 级重建。每条引用必须通过 doi.org/works 或 Crossref API 反查（200 OK 且标题/作者/期刊/年份四件套匹配）+ arXiv 条目必须通过 arxiv.org/abs/{id} 五件套核对（ID/标题/作者/年份/主题）。查无实据的条目整条删除并重检正文引用位。scheme §3.3/§3.4/§3.6 的三条承重句在文献重建前不得保留现有表述。
- action：research + verify + rewrite
- 违反条款：indicator_red_lines.no_exaggeration（文献先例失实）、rigor rubric "<0.60：多处事实错误"

#### P0-2 [critical] red_line — §3.2/§3.6 场强换算错误 10 倍，可行性核心先例论证崩塌
- 位置：scheme.md §3.2 L19、§3.6 L63
- 问题：L19 "THz 脉冲（0.4 V/Å ≈ 4 MV/cm，1 THz 共振）"。单位换算：0.4 V/Å = 0.4 V / 10⁻¹⁰ m = 4×10⁹ V/m = **40 MV/cm**，不是 4 MV/cm，错 10 倍。连锁后果一：§3.6 "0.4 V/Å 阈值电场的参数与本方案 R1 的 0.1–1.0 MV/cm 场强范围处于同一量级"——40 MV/cm 与 0.1–1.0 MV/cm 相差 40–400 倍，"同一量级"被物理换算直接推翻，R1 全部驱动窗口的可行性论证失去先例支撑。连锁后果二：若坚持引文确为 0.4 V/Å，则须正面回答"为何本方案场强低 1.5–2 个量级仍能驱动滑移切换"（势垒高度差？材料差异？），否则 R1 的切换概率判据（≥10%）无物理依据。另：该数值组（0.4 V/Å、1 THz 共振、3–4 ps）在 2403.06531 摘要中无对应表述（摘要仅称 laser pulses 激发剪切模、机器学习力场 MD），正文参数待 writer 逐条核对回填页码/图号。
- 建议：① 立即改写换算（40 MV/cm）并重写 §3.6 "同一量级"句；② 补充一段"参数窗口差异的物理论证"（h-BN 势垒 vs NiCl₂/VS₂/CrSe₂ 势垒对比、共振增强因子），或下调 R1 场强宣称；③ 核对 2403.06531 正文（注意：该 arXiv 论文的标题挂在 refs [36] 的错误 PRL 卷页上，条目本身见 P0-1）。
- action：recalculate + research + rewrite
- 违反条款：indicator_red_lines.no_exaggeration / uncertainty_constraint、rubric feasibility "0.60-0.69：核心技术路线缺乏支撑"

#### P0-3 [critical] rigor — scheme.md 全文零 [N] 角标，"文献 N"散文体例（上轮 P0 未修复）
- 位置：scheme.md 全文（L19/29/47/63 六处"文献 N/裸 arXiv ID"）
- 问题：上轮已报，文本零修改，原样存在。全文 0 个 [N] 角标，引用一律"文献 2403.06531（Wang et al., 2024）""文献 19（García-Gaitán 等人）"散文体例 + 两处裸 arXiv ID（2403.06531 ×2、2504.18845 ×1）。范本 citation_style 要求"'某人等人[N]在期刊上报道了X'"嵌入式角标；rationale/content 均已用 [N] 体例，scheme 是四章节中唯一未切换的，构成全书体例分裂。
- 建议：全部改为嵌入式角标："Wang 等人 [36] 的第一性原理与机器学习力场模拟表明……"（编号以重建后的 references 为准）；删除全部裸 arXiv ID。
- action：rewrite
- 违反条款：reference_materials.style_benchmark.citation_style、section_standards.scheme（间接）、上轮 R2 P0 清单

#### P0-4 [critical] red_line — §3.4 "Yarmohammadi 等人（文献 21）"编号错配（上轮 P0 未修复 + 文献本身虚构）
- 位置：scheme.md §3.4 L47
- 问题：上轮已报，原文未动。refs [21] 是 Rajpurohit et al.（全光自旋劈裂开关），Yarmohammadi 的 Floquet-Rashba 工作是 [22]/[23]。content.md 同位点已改为 [22]，scheme 残留。且经 Crossref 反查 [21] 本身为虚构条目（实际论文主题完全无关）——修编号之外还须修文献本体（见 P0-1）。
- 建议：改写为 "Yarmohammadi 等人 [22]（编号以文献重建后为准）证明 Floquet 驱动结合 Rashba 耦合……"，并与 content §2.4 L39 的引用位对齐。
- action：rewrite + research
- 违反条款：indicator_red_lines.consistency_check、上轮 R2 P0 清单

#### P0-5 [critical] red_line — §3.6 "文献 19（García-Gaitán 等人）"编号错配（上轮 P0 未修复）
- 位置：scheme.md §3.6 L63（另 §3.4 L49 同一先例未标号）
- 问题：上轮已报，原文未动。refs [19] 是 Werner et al.（交变磁金属 HHG），García-Gaitán 的 NiO THz-HHG 工作是 [20]。rationale §1.2 L23 用 [20] 正确，scheme 用 [19] 错误，同一文献在三章节两种编号。附注：[20] 的 Nat Photonics 卷页（18:876）本轮 Crossref 未命中（标题检索仅返回会议摘要与俄文期刊），暂列待核——writer 须提供 DOI 过 doi.org 反查 200 OK 后方可保留。
- 建议：改为 [20] 并补角标；[20] 条目提供 DOI 验证记录。
- action：rewrite + verify
- 违反条款：indicator_red_lines.consistency_check、上轮 R2 P0 清单

#### P0-6 [critical] red_line — D_sep 同名双定义跨章分裂（scheme 重叠积分 vs content 信噪比之比）
- 位置：scheme.md §3.4 L39–43 vs content.md §2.5 目标三 L51
- 问题：scheme 定义 "D_sep = 1 − ∫f_e(t)·f_m(t)dt / √[∫f_e²dt·∫f_m²dt]"（归一化重叠积分），并解释 "D_sep = 1 表示完全正交分离"；content 目标三写 "分离度 D_sep ≥ 0.80（以两通道信号的信噪比之比为度量）"。同一符号、同一目标值 0.80、两种数学定义（重叠积分 vs 信噪比之比）——评审专家任取一处定义都能发现全书口径矛盾。这是 indicator_red_lines.consistency_check 的教科书式违规。scheme 的重叠积分定义更严格可取，应反向统一 content。
- 建议：以 scheme L41 的积分定义为准，改写 content §2.5 目标三的度量口径句；两处均保留"D_sep = 1 完全正交"的解释以保证可读性。
- action：rewrite（content 侧）+ verify
- 违反条款：indicator_red_lines.consistency_check / indicator_measurable

#### P0-7 [critical] red_line — 指纹量 5 vs 3 口径分裂 + "content.md §2.3 定义的五个指纹量"错引（上轮未修复且恶化）
- 位置：scheme.md §3.3 L25、L31（4/5 判据）、§3.7 L79、L81 vs content.md §2.3 L27、§2.5 目标二 L49
- 问题：上轮已报 5 vs 3 分裂，未修复。本轮新增两个硬伤：① L25 写"（对应 content.md §2.3 定义的五个指纹量）"——content §2.3 实际定义的是三个特征（A_helicity、S_ellipticity、θ），scheme 的第 (4) 阶次周期性、第 (5) 椭圆度过零点在 content 全章（含目标二、预期产出 L31"涵盖 A_helicity、S_ellipticity、θ"）从未出现，"五个"是 scheme 单方面加码且谎称对侧定义；② L31 把验证率判据自绑到五指纹口径"≥ 80%（即 4/5 个指纹量……在 2 倍因子内一致）"——若 content 侧只认三个指纹量，"4/5"分母无来源，判据无法执行。§3.7 L79/L81 创新点二同样以五指纹量宣称"突破核心瓶颈"。
- 建议：三选一并全书统一：a) content §2.3 补齐第 (4)(5) 指纹量定义（推荐，五量信息量更高）；b) scheme 删至三量并改判据为"3 个指纹量全部在 2 倍因子内"；c) scheme 明示"三个已定义量 + 两个候选量"分层。同步修改 §3.3 L25 的"§2.3 定义"引文、L31 判据分母、§3.7 创新点二表述。
- action：rewrite + add/remove
- 违反条款：indicator_red_lines.consistency_check、writing_style_rules.must（研究内容↔研究方案逻辑呼应）

#### P0-8 [critical] red_line — §3.7 创新点一"从未被作为独立动力学变量引入强场超快物理研究框架"绝对化宣称无支撑且存反例张力
- 位置：scheme.md §3.7 L73（content.md §2.2 L13 同句复制）
- 问题："现有文献中，层间滑移自由度从未被……"是全称否定判断：① 无检索范围/截止日期声明（rationale §1.5 L63 有规范的检索声明，scheme 未沿用，口径不一）；② 与本申请书自己引用的 2403.06531（Wang 2024：激光脉冲激发剪切模实现滑移铁电确定性调控）直接存在张力——该工作正是"层间滑移坐标参与超快强场动力学"，创新点必须收窄到本项目的真实增量（"作为独立动力学变量用于自旋劈裂切换的理论方案"而非"参与超快动力学"本身）。novelty_claim_cautious 要求未完成研究用"拟/有望首次"。
- 建议：改写为与 rationale §1.5 统一的限定表述："据截至 2026-08 的检索（Web of Science、arXiv、APS/IOP），层间滑移坐标虽已进入光驱动动力学研究 [36]，但尚未被作为独立动力学变量用于交变磁自旋劈裂的超快切换与 HHG 读出方案"。content §2.2 L13 同步修改。
- action：rewrite
- 违反条款：indicator_red_lines.novelty_claim_cautious

#### P0-9 [critical] rigor — §3.3 以虚构文献作 R2 方法论基础（arXiv 2504.18845 = 神经网络论文）
- 位置：scheme.md §3.3 L29
- 问题："Morimoto 等人 2504.18845 的理论工作证明 HHG 光谱能够编码量子度规和 Berry 曲率信息，为本方案的指纹理论提供了方法论基础。"arXiv API 反查：2504.18845 实际是 "Introducing Interval Neural Networks for Uncertainty-Aware System Identification"（作者 Mehmet Ali Ferah、Tufan Kumbasar，控制系统主题），与 HHG/量子度规毫无关系——refs [32] 为虚构条目（真实 ID + 虚构标题 + 套用知名作者姓氏）。R2 指纹理论的方法论支撑是虚构的。content §2.3 L27 同引 [32] 同罪。
- 建议：找到量子度规-Berry 曲率 HHG 编码的真实文献（该方向确有代表性理论工作，writer 须给出可反查的 arXiv ID/DOI）重建 [32]，两处引用同步更新；找不到则删除该句，指纹理论的方法论基础改由磁点群选择定则 [18]（重建后）承担。
- action：research + rewrite
- 违反条款：indicator_red_lines.no_exaggeration、rigor rubric "<0.60：多处事实错误"

#### P0-10 [critical] rigor — 历史遗留：content §2.5/§2.6 Floquet 场强上界仍缺失（部分解决）
- 位置：content.md §2.5 目标三 L51、§2.6 问题三 L61；scheme.md §3.4 L43
- 问题：历史 P0"content Floquet 驱动场强上界缺失"本轮仅部分修复——content §2.4 L39 已补"上限 0.3 MV/cm"，但 §2.5 目标三的量化指标（"Floquet 增强因子 ≥ 5 倍"）与 §2.6 问题三的最优参数窗口两处仍无场强上界，指标没有完整参数域。scheme §3.4 L43 给出的是"0.01–0.3 MV/cm"（带下界），与 content 的"上限 0.3"（无下界）口径不对齐（下界差异另计入 M2）。
- 建议：content §2.5/§2.6 补"驱动场强 ≤ 0.3 MV/cm（窗口 0.01–0.3 MV/cm，与 scheme §3.4 一致）"；三处（§2.4/§2.5/§2.6/scheme §3.4）统一为同一区间表述。
- action：add + rewrite
- 违反条款：indicator_red_lines.indicator_measurable / implementation_path、历史 P0 清单

### P1（high）— 共 12 条

#### P1-1 [high] anti_ai — 超长句 31 处（scheme 本体 13 处、12.6%，较上轮 11 处恶化）
- 位置：scheme.md 极值句 L91（165 字）、L31（161 字）、L108（148 字）、L27（139 字）、L13（139 字）等 13 处；content 7 处、rationale 12 处
- 问题：程序化检测 severe_count 31、罚 0.52（表达质量最大扣分项）。范本 sentence_rhythm 实测超 120 字占比为 0 且明确"单句超 120 字必拆分"。上轮已报 scheme 11 处，本轮升到 13 处——writer 未做任何拆句作业。
- 建议：每句拆为 2–3 句，拆分点选在"——""；""（）"处。例：L31 可拆为"判据设定分两层。目标二要求理论预言的 HHG 指纹在平台一数值模拟中的验证率 ≥ 80%，即 4/5 个指纹量的理论值与模拟值在 2 倍因子内一致。在平台二上，理论须能区分 i-wave 与 d-wave/g-wave 自旋劈裂类型，区分度 ≥ 3σ——该区分度以 Monte Carlo 模拟中加入 10% 高斯噪声后的分类准确率为度量。"（注意此句重写须先落 P0-7 的口径）。
- action：rewrite
- 违反条款：anti_ai_patterns.remove（超长句）、expression rubric "0.60-0.69 及以下"

#### P1-2 [high] anti_ai — 死板关联词 21 次超标（"同时"16 次）
- 位置：拼接全文；scheme 本体"同时"5 次（L15/L29/L37/L49/L57）
- 问题：程序化检测 count 21 > 阈值 20，罚 0.02。"同时"在 §3.4 L37 一句内两次衔接两组物理过程，机械感最强。
- 建议：改内容驱动衔接——L37 "THz 泵浦脉冲激发磁序动力学（ps-ns 量级），并触发层间滑移模式的相干振荡"→"THz 泵浦脉冲在 ps-ns 窗口驱动磁序参量进动；层间滑移模式则被同一脉冲的相干分量激发，振荡 confined 在 fs-ps 窗口"。全文"同时"压缩至 ≤6 次。
- action：rewrite
- 违反条款：anti_ai_patterns.remove（死板关联词）、style_benchmark.narrative_density（段间用内容逻辑衔接）

#### P1-3 [high] anti_ai — 模板句式"为…提供…"9 次超标
- 位置：拼接全文 9 次（阈值 8），scheme 本体 7 次（L13/L19/L29/L75/L87/L91/L93）
- 问题：程序化检测罚 0.03。§3.8 L91–L93 三段连续以"为…提供…"收尾（"为后续研究与材料筛选提供可重复使用的诊断工具""为后续实验验证提供工程化依据"），成串模板。
- 建议：§3.8 两处改为具体动词："上述理论工具将以开源代码形式发布（TDDFT 框架基于 Octopus、指纹表以标准数据格式提供），可直接复用于后续材料筛选""该方案直接对接本课题组现有 HHG 平台的工程接口"。全文压至 ≤8。
- action：rewrite
- 违反条款：anti_ai_patterns.remove（模板句式）、expression rubric

#### P1-4 [high] boundary — §3.5 难点三为可行性内容，溢出方案章（上轮未修复）
- 位置：scheme.md §3.5 L57
- 问题：上轮已报，原文未动。难点三"THz 泵浦-探测的实验实现成本与可行性……与国内已建立平台的团队合作（已有合作意向），避免从零建设"整段回答"为什么能做成"，属可行性分析；且其降级方案（ps 分辨率替代）与 §3.4 L37、content §2.4 L37 的降级表述三处重复。
- 建议：难点三保留"技术难点+物理解决路径"（抖动 <10 fs 的要求从何而来、如何以 ps 分辨率保住 D_sep ≥ 0.80），将合作平台、建设成本两句移入 §3.6 关键指标可达性段；降级表述全书只保留 content §2.4 一处完整版，scheme 引用之。
- action：rewrite + remove
- 违反条款：section_standards.scheme 第 5 条、content_boundaries

#### P1-5 [high] boundary — §3.6 复述 §3.2/§3.4 可行性依据，违反"可行性不复述方案细节"
- 位置：scheme.md §3.6 L63 vs §3.2 L19、§3.4 L49
- 问题：§3.6"原理成立性"段与 §3.2 L19（2403.06531 先例）、§3.4 L49（NiO 先例 + 预研 + 回退方案）逐点重复：同一批文献、同一批参数、同一批平台条件各出现两次。scheme_anchor 明确"可行性分析遵循'方案→原理→结论'链式论证，不复述方案细节"。
- 建议：§3.2/§3.4 内嵌的"可行性依据"段（L19、L49）是内容越界的另一面——分方案内保留一句话指引（"原理先例见 §3.6"），完整论证集中在 §3.6；§3.6 改写为纯"原理→指标"映射表（每项指标：先例出处→本方案参数窗口→可达性结论），不再复述先例细节。
- action：rewrite + remove
- 违反条款：section_standards.scheme 第 3 条、style_benchmark.structure_pattern

#### P1-6 [high] boundary — §3.1 与 content §2.1 核心科学问题句、范式 A/B 句逐字重复
- 位置：scheme.md L5 vs content.md L5/L9
- 问题："强激光能否在 fs-ps 时域通过相干激发层间滑移模式与 Floquet 缀饰实现对交变磁自旋-能谷态的超快切换"scheme L5 与 content L5 逐字相同；"范式 A 回答'能否驱动'的问题，建立光-晶格-自旋三体耦合的非线性响应理论；范式 B 回答'如何测量'的问题，建立圆偏振 HHG 指纹与自旋劈裂参数的定量对应关系"scheme L5 与 content L9 逐字相同（仅括注差异）。两大段跨章 copy-paste。
- 建议：scheme §3.1 改为承接式表述："在 content.md 确立的双平台×双范式框架下，本方案将三个研究内容部署为三条技术主线：R1 兑现范式 A 的'驱动'（TDDFT+多带紧束缚……）……"——方案章应写"怎么做"，框架定义留给内容章。
- action：rewrite
- 违反条款：content_boundaries（跨章节大量重复）、style_benchmark.section_coherence

#### P1-7 [high] rigor — "content.md §2.3 明确"章节错引（时域层次实在 §2.4）
- 位置：scheme.md §3.4 L35
- 问题："物理时域层次已在 content.md §2.3 明确"——content 中"电子层/磁序层两层可分离"的时域层次表述在 §2.4 L35（源头 rationale §1.3 L35）；§2.3 是 HHG 指纹内容。同章 L45 "content 2.4 设定亚 100 fs 分辨率为目标"却引对了章节——同一 content 在 scheme 两种指称，至少一处笔误。跨章锚点引用错误会误导评审专家查证。
- 建议：L35 改"content.md §2.4（源头见立项依据 §1.3）"；全书做一遍 §X.Y 交叉引用核对。
- action：verify + rewrite
- 违反条款：writing_style_rules.must（各章逻辑呼应）、rigor rubric 0.70-0.79 档（表述不精确）

#### P1-8 [high] rigor — Volkov 近似适用条件与失效边界未注明
- 位置：scheme.md §3.3 L23
- 问题："利用非微扰 Volkov 近似或数值求解含时薛定谔方程计算 HHG 谱"——Volkov 近似忽略束缚态与库仑效应，源于强场电离区（隧道区）的单电子图像；用于固体多带体系时其适用域（能带内电流主导 vs 带间极化主导）有明确限制。indicator_red_lines.theory_applicability 要求"使用某理论框架前须说明其适用条件，并注明失效边界"。对照：ALDA 的失效边界在 §3.5 难点一有规范讨论（这是达标样板），Volkov 无。且"或"字暴露工具选择未定——方案书应主次分明。
- 建议：明确主工具为多带紧束缚 TDSE 数值求解，Volkov 仅作解析极限校验，并补一句适用条件："Volkov 近似仅在电离阈值以上、单带加速图像成立时用于解析定性，带间相干效应显著的低阶谐波区一律以 TDSE 为准。"
- action：add + rewrite
- 违反条款：indicator_red_lines.theory_applicability

#### P1-9 [high] rigor — 平台一文献基础坍塌：[30] 虚构 + [11] 待核 + scheme 势垒值无角标溯源
- 位置：scheme.md §3.2 L17；rationale §1.5 L53、content §2.1 L7（同源）；references [30] [11]
- 问题：平台一（NiCl₂/VS₂/CrSe₂）的三重文献支撑本轮反查全部动摇：[30]（滑移方晶格耦合准交变磁，arXiv:2408.11234）实为遥感论文，虚构；[11]（Sheng 堆叠工程 DFT，npj 10:215）Crossref bibliographic 检索未命中该标题/卷页组合，待 writer 提供 DOI 验证；[34]（THz 剪切声子可行性）虚构。scheme §3.2 L17 的"16–40 meV/unitcell（来自静态 DFT 计算，材料为 NiCl₂/VS₂/CrSe₂）"无角标，数值无法溯源——该势垒区间是 R1 共振驱动逻辑的物理地基。
- 建议：[30] 删除或替换为可反查的真实文献；[11] 提供 DOI 过 Crossref 验证；scheme L17 补 [N] 角标并注明"势垒值取自 [11] 表 X"级别的事源粒度。若 [11] 亦不实，16–40 meV 须由本课题组自行计算给出（转为预研数据并说明方法）。
- action：research + verify + add
- 违反条款：indicator_red_lines.no_exaggeration、rigor rubric "<0.60：多处事实错误"

#### P1-10 [high] rigor — 2403.06531 先例参数真实性待核（0.4 V/Å/1 THz/3–4 ps 摘要无对应）
- 位置：scheme.md §3.2 L19、§3.6 L63
- 问题：P0-2 已修换算；此处独立追踪参数来源。arXiv 摘要仅含"laser pulses 激发剪切模、机器学习力场 MD、滑移铁电翻转、动态磁场"，无 THz、无场强数值、无 ps 时标（摘要级）。scheme 声称的"1 THz 共振、3–4 ps 翻转"若为论文正文数字，须给出图表定位；若为 writer 推测，则整段先例论证失实。另该论文使用的是机器学习力场 MD 而非 TDDFT——scheme 将其作为"R1 TDDFT 路线的原理可行性先例"存在方法学错位（先例证明的是 MD 尺度可模拟，不是 TDDFT 可模拟）。
- 建议：核对论文正文回填"（图 X / 表 Y）"级引用；在先例句中如实表述方法差异："该工作以第一性原理训练的机器学习力场完成 MD 模拟，本方案在其参数结论基础上以 TDDFT 补全电子动力学自洽性。"
- action：verify + rewrite
- 违反条款：indicator_red_lines.no_exaggeration、rigor rubric 0.70-0.79 档以下

#### P1-11 [high] expression — 历史遗留：content.md 7 句 >120 字仍存在（10.3%）
- 位置：content.md（§2.2 L17、§2.4 L37/L39 等密集区）
- 问题：历史清单"content 超长句 13.6%"经 8-19 重写降至 10.3%（7 句），改善但未达范本 0 标准。上轮报 9 句，本轮 7 句。
- 建议：优先拆 §2.4 L37（电子层/磁序层双层论证句群）与 L39（Floquet 参数列举句），拆法同 P1-1。
- action：rewrite
- 违反条款：anti_ai_patterns.remove（超长句）

#### P1-12 [high] rigor — 3σ/90%/70%/80% 四数字口径混乱 + "分类准确率可达 3σ"量纲混淆
- 位置：scheme.md §3.3 L31、§3.7 L81、§3.9 L108 vs content.md §2.5 L49、§2.6 L59
- 问题：历史遗留（§2.5 vs §2.6 量级跳跃）未解决且 scheme 加剧：① content L49 "区分度 ≥ 3σ（以加入 10% 高斯噪声后的分类准确率为度量）"把区分度（效应量）与准确率（百分比）混为一种量；scheme L81 更写"分类准确率可达 3σ（对应 > 99.7% 置信度）"——σ 是效应量单位，准确率是百分比，99.7% 是正态置信水平，三个不同量纲串在一句；② 阈值序列 content L59 为"<90% 引入融合策略、仍 <70% 不可行"，scheme L108 Go/No-Go 直接用"<70% 不可行"，跳过 90% 融合层——两章判据层级不一致；③ 80% 验证率（理论 vs 模拟一致）与上述分类准确率是两个指标，正文多处并用时未标区分。
- 建议：统一定义一处（建议 scheme §3.3 L31）："区分度以两类指纹分布的分离显著性 d′ 计，判据 d′ ≥ 3；等价的分类准确率判据为 ≥ 99%（10% 高斯噪声、Monte Carlo 200 次）。Go/No-Go 分层与 content §2.6 一致：准确率 < 90% 启动多指纹量融合，融合后仍 < 70% 判不可行。"其余位置全部引用该定义。
- action：recalculate + rewrite
- 违反条款：indicator_red_lines.consistency_check / indicator_measurable

### P2（medium）— 共 8 条

#### P2-1 [medium] rigor — 平台二定位措辞三级递增："唯一靶标"（content L7）→"唯一体系"（scheme L5）vs rationale"理想载体"（L55）
- 建议：统一为"目前已知唯一同时具备三自由度的体系（据检索截至 2026-08）"——"唯一"须挂检索声明，否则降为"理想载体"。违反 novelty_claim_cautious。action：rewrite
#### P2-2 [medium] rigor — Floquet 场强下界口径：scheme "0.01–0.3 MV/cm"（L43）vs content 仅"上限 0.3"（L39）
- 建议：三处统一为 0.01–0.3 MV/cm 区间（含 P0-10 的 §2.5/§2.6 补齐）。违反 consistency_check。action：add
#### P2-3 [medium] expression — §3.9 年度表时间粒度混乱："Year 3"整年行与"Year 3 Q3–Q4"半年行嵌套并存
- 位置：scheme.md L104/L105。Year 3 行写"R3 启动泵浦-探测方案设计"，紧接着 Year 3 Q3–Q4 行写"R3：完成方案设计"，启动与完成挤在同一年且粒度不一。
- 建议：统一粒度为 Year 1 / Year 2 H1 / Year 2 H2 / Year 3 H1 / Year 3 H2 / Year 4，或全部按年。action：rewrite
#### P2-4 [medium] expression — 创新点收束句模板化
- 位置：§3.7 L73"有望为二维材料强场超快物理开辟一个新的研究方向"、L87"为弱信号的实验探测提供了可行路径"。
- 建议：改为克制定位（对标 innovation_example"是本项目的创新之处"）："这一坐标提升是本项目的概念创新"或直接删去空泛句。违反 anti_ai_patterns（空洞概括句边缘）。action：rewrite
#### P2-5 [medium] rigor — TDDFT 计算参数与预算：k 网格 12×12×1 偏粗、多轨迹×3 泛函×3–4 ps 全电子演化成本未讨论
- 位置：scheme.md §3.2 L11。12×12×1 对螺旋度分辨的 HHG 谱收敛性偏弱（同类工作常 18×18 起）；切换概率需 N_total 条轨迹 × PBE/PBE+U/HSE 三泛函 × ps 级演化，§3.6 只给"Monte Carlo 3 个月"，TDDFT 主成本无预算句。
- 建议：补"k 网格收敛性测试（12×12 至 24×24）+ 单轨迹成本 × 轨迹数 × 泛函数的机时估算"。违反 feasibility rubric 0.70-0.79 档（部分关键技术缺少预研验证）。action：add
#### P2-6 [medium] rigor — §3.8 成果表述两处失当："论文署名应为全部作者"、"博士研究生具备独立开展理论与实验能力"
- 位置：scheme.md L95。理论为主的课题（R1–R3 全为理论+方案设计）承诺博士生"独立开展实验"超出项目范围；"署名全部作者"非 NSFC 成果承诺惯用语。
- 建议：改为"论文标注本项目资助（No. XXXXXXXX）""培养 2–3 名博士生掌握强场超快理论模拟与实验方案设计能力"。action：rewrite
#### P2-7 [medium] rigor — THz 泵浦频率未指定，磁序激发路径断链
- 位置：scheme.md §3.4 L37。泵浦只给场强（0.1–1.0 MV/cm）未给频率——反铁磁共振激发对频率敏感（MnPS₃ Néel 温度 78 K 对应磁共振频率量级须给出），且与 Floquet 缀饰场（0.5–3.0 THz）同处 THz 频段，二者频段隔离/时序分步未说明（三光束方案：THz 泵浦 + Floquet 缀饰 + 中红外探测）。
- 建议：补泵浦中心频率与带宽、三光束时序图说明（泵浦-缀饰-探测的先后与频段隔离）。违反 implementation_path。action：add
#### P2-8 [medium] rigor — 跨章错别字："Bery 曲率"（content §2.4 L35、rationale §1.3 L35 双现）
- 简要一致性检查发现（非本轮聚焦）：两章同错 Berry→Bery，说明 copy-paste 传播。scheme 无此错。action：rewrite

### P3（low）— 共 2 条

#### P3-1 [low] expression — 泛函缩写体例不一：scheme §3.2 L17 "Heyd-Scuseria-Ernzerhof hybrid" 全称 vs content L47 "HSE"
- 建议全书首次出现给全称+缩写，此后一律缩写。action：rewrite
#### P3-2 [low] rigor — "Octopus 与 Q-e 配合的 TDDFPT 模块"术语混用（TDDFT vs TDDFPT；Q-e 应作 Quantum Espresso 或 QE）
- TDDFPT 特指线性响应微扰，与实时 TDDFT 是两回事，方案正文以实时 TDDFT 为主线，此处易误导。action：rewrite

---

## 7. 多维度评分（依据 scoring_rubric 档位）

评分依据逐档引用（general_principles.scoring_rubric v6.8.24）：

- **创新性 0.72（0.70-0.79 档："选题有一定新意，但创新点表述不够锐利，或与已有工作的差异需更充分论证"）**：双平台×双范式与"滑移坐标升格为驱动变量"的概念组合有真实新意，指纹反演框架有方法学增量；但创新点一的核心宣称采用无支撑全称否定（P0-8），与 Wang 2024 先例的差异论证不足，恰好落在本档描述上。
- **可行性 0.63（0.60-0.69 档："可行性存疑，核心技术路线缺乏支撑，或关键装置/指标超出当前技术水平"）**：技术链条设计与风险-回退体系（ALDA 修正、Rashba 敏感度、降级实验、Go/No-Go）是全章最扎实的部分；但核心先例数值换算错 10 倍且"同一量级"论断崩塌（P0-2）、平台一文献地基坍塌（P1-9）、THz 泵浦频率缺失（P2-7）、TDDFT 机时无预算（P2-5），核心技术路线的支撑面出现结构性漏洞，落入 0.60-0.69 档中位。
- **严谨性 0.55（<0.60 档："多处事实错误或逻辑矛盾，无法支撑研究结论"的边缘，兼 red_line 纪律）**：按纪律 indicator_red_lines 违规（consistency_check ×3、novelty_claim、no_exaggeration）应扣至 0.6-0.7 区间；但本轮联网双源反查确证 12 条虚构/错配文献 + DOI 404 ×2 + 换算错误 ×1，属 rubric 明文的"多处事实错误"，量级超出常规红线情形，取 0.55（低于常规区间、落在 <0.60 档内）。上轮 0.55 维持——零修复且新增确证。
- **表达质量 0.45（受程序化天花板 0.50 强制；锚点结论=差距明显 → 表达 ≤0.69）**：程序化检测发现 AI 写作模式，表达质量被强制限制。三项超标（超长句 31 处罚 0.52、模板句 9 处罚 0.03、关联词 21 次罚 0.02），scheme 超长句占比 12.6% vs 范本 0 且较上轮恶化；零 [N] 角标体例与范本嵌入式引用差距代差级。叙述骨架与方法论证亮点使分数不至于贴地板，取 0.45。

综合评分 = (0.72 + 0.63 + 0.55 + 0.45) / 4 = 0.5875 ≈ 0.59（四维等权，误差 <0.02 自洽）。锚点绑定校验：差距明显 → 综合 ≤0.84 ✓、表达 ≤0.69 ✓。对照 project_types.general.quality_threshold（min_overall 0.85 / max_high_issues 0 / max_medium_issues 3）：本轮 critical 10、high 12、medium 8，远超门槛。

## 评分
创新性：0.72
可行性：0.63
严谨性：0.55
表达质量：0.45
综合评分：0.59

## 8. 对抗结论

- 本轮发现 32 个问题（critical:10, high:12, medium:8, low:2）。
- 相比上一轮（scheme 专项 3 critical + 6 high）：**改善 0 个，新增 17 个（P0 新增 7：D_sep 双定义、指纹量错引细化、novelty 绝对化、refs 虚构体系、换算错误、content Floquet 部分残留；P1/P2 新增 10），未解决 9 个**（scheme.md 自上轮评审后零字节修改，上轮 9 条全部原样复报，severity 不降）。历史遗留 13 条核对：content 侧已解决 6、仍存 4、部分解决 1，另 2 条为同位重复计数——writer 对 content.md 的重写有效，scheme.md 完全未动。
- 本轮最大增量发现：references.md 系统性文献虚构经 arXiv API + Crossref API 双源确证（12 条错配/虚构 + 2 条 DOI 404 + 2 条待核），scheme.md 的四处承重引用（指纹理论方法论、Floquet 框架、可行性两先例）全部踩雷；叠加 0.4 V/Å 换算错 10 倍导致的可行性先例崩塌。**文献真实性是本轮最高优先级：在 references 重建并逐条联网验证之前，任何表达层优化都是次级工作。**
- 是否达到输出标准：**否**。综合 0.59 << 0.85 门槛，critical 10 >> 0 上限。整改顺序建议：① P0-1/P0-9/P1-9 文献重建与双源验证（research+verify）→ ② P0-2 换算重算与可行性论证重写 → ③ P0-3/4/5 角标体例切换 → ④ P0-6/7/10 与 P1-12 指标口径全书统一 → ⑤ P1-1/2/3 表达整改（拆句、去模板）→ ⑥ P1-4/5/6 boundary 与重复内容重组。
