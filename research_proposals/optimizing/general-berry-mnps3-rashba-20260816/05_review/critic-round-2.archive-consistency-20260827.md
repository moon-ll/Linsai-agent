# 对抗评审报告（第 2 轮 · 整体一致性审查：rationale + content + scheme 三章联合）

项目类型：general（面上项目）
聚焦范围：三章节之间的逻辑衔接、术语一致性、内容冗余/矛盾（整体连贯性，非逐段细审）
评审日期：2026-08-27
评审依据：memory/nsfc-standards.json（general_principles.scoring_rubric v6.8.24 / indicator_red_lines / writing_style_rules.anti_ai_patterns / section_standards / reference_materials.benchmark_anchors / project_types.general）
配置核查声明：prompt 所引 `programmatic_checks` 与 `overall_review_requirements` 两键在 nsfc-standards.json 中不存在（实测顶层 8 键、general_principles 12 键均无此二者），按纪律不虚构其规则，程序化检测一律以 prompt 附带报告为准，记 [low] config 备案。

---

## 0. 评审前置核查（对象对账 + 文件归属 + 管线时序）

1. **检测对象对账**：程序化报告称全文字符数 20537。实测 rationale.md 6817 + content.md 5646 + scheme.md 8070 = 20533，加 2×2 字符分隔符 = 20537，精确匹配。检测对象为三章节拼接，无对象错位。整体轮的"检测对象=Σ章节"特性使历史错位问题自然消解，结案不复报。
2. **长句独立复核**：排除标题/表格/公式行后按句号切分实测 >120 字正文长句 30 处（rationale 11 / content 8 / scheme 11），程序报告 31 处（含 1 处表格行口径差），采信程序值 31，误差 1 处不改变结论。
3. **文件归属核查**：05_review/ 原 critic-round-2.md（05:20，48655 字节，scheme 专项版）与 critic-round-2.archive-scheme.md 内容不同（MD5 异）。按跨轮纪律已先备份为 `critic-round-2.archive-scheme-20260827.md`（48655 字节）再写入本报告，无覆盖事故。
4. **管线时序**：scheme.md mtime 08-27 05:57、content.md 05:58，均晚于上轮 scheme 专项报告（05:20）——writer 本轮确实推了 content+scheme 两条线的修改；rationale.md 自 08-19 20:17 后未动。本轮"已解决"判定与此事实吻合。

## 1. 模块完整性检查

- rationale.md：§1.1 大背景 → §1.2 领域脉络（三阶段）→ §1.3 核心问题（三瓶颈）→ §1.4 国内现状 → §1.5 本项目定位（双平台×双范式 + 三关键科学问题）。五层递进在位 ✓
- content.md：§2.1 总述 + §2.2–§2.4 三方向 + §2.5 研究目标（各带量化指标）+ §2.6 关键科学问题（各带可证伪条件）✓
- scheme.md：§3.1 总体方案与技术路线 + §3.2–§3.4 分方案 + §3.5 难点 + §3.6 可行性（方案→原理→结论链式）+ §3.7 特色创新（3 点四步闭环）+ §3.8 预期成果 + §3.9 年度计划（含 Go/No-Go）✓

**结论：标准模块齐全，无缺失章节。** 完整性不扣结构分；但 §3.6 与 §3.5/§3.2 存在功能回描（见 M-边界类与上轮归档报告），本章不重复展开。

## 2. 执行清单对照

| # | 执行清单条目 | 判定 | 证据定位 |
|---|---|---|---|
| 0 | 模块完整性 | 通过 | 三章模块齐全（见第 1 节） |
| 1 | 读取申请书 + 标准配置 | 通过 | 三章节 + nsfc-standards.json 全量读取（rubric 五档、红线七条、anti-AI 清单、六类锚点、section_standards 四节清单） |
| 2 | 逐条对照执行清单 | 通过 | 本表即对照结果 |
| 3 | 锚点对比（结构化 + 结论行） | 通过 | 见第 4 节，结论=差距明显 |
| 4 | 引用程序化检测结果入清单 | 通过 | H5/H6 两条 anti_ai 入清单；表达质量按天花板 0.50 强制限制并明示 |
| 5 | 按项目类型标准红队评审 | 通过 | 问题清单 24 条，每条标注红线/rubric/section_standards 条款 |
| 6 | 写作风格重点检查 | 部分不通过（申请书侧） | 叙述式主线 ✓、无 bullet ✓、引用嵌入 ✓；但超长句 31 处、模板句 9 处超标、跨章逐字重复 4 组（H7） |
| 7 | 每问题给可执行建议 + 条款 | 通过 | 问题清单逐条给 rewrite/recalculate/verify/remove 指令 |
| 8 | 严重度分级 | 通过 | critical 5 / high 8 / medium 7 / low 4 |
| 9 | 叙述式：科学问题为主线 | 通过 | 三章围绕"驱动→读出→分离"逻辑链组织，§2.1/§3.1 明示 |
| 10 | 叙述式：无 A做了X/B做了Y 堆砌 | 基本通过 | 引用多为嵌入式论证（对标 rationale_anchor）；但 §1.2 三阶段粗体标签式分段（**第一阶段**…）呈轻度脚手架化 |
| 11 | 叙述式：无 bullet 替代论证 | 通过 | 全文无 bullet；表格仅年度计划，合规 |
| 12 | 叙述式：段落过渡递进 | 部分通过 | 章内递进良好；跨章存在逐字复制而非"简引+深化"（H7） |
| 13 | 方案说明"为什么选这个方法" | 通过 | §3.2 L13（TDDFT+紧拾绑组合理由）、§3.3 L23（Volkov 仅作解析极限校验）、§3.3 L27（磁点群解析优先的理由） |
| 14 | 立项依据五层递进 | 通过 | §1.1–§1.5 五层在位 |
| 15 | 研究目标每条含量化指标 | 通过 | §2.5 三目标均带量化指标；但其中两条指标本身有数学/口径错误（C1/C3） |
| 16 | 特色创新四步闭环 | 通过 | §3.7 每点"局限→方案→量化优势→定位"，无"国际领先/填补空白"表述 |
| 17 | 指标红线 P0 检查 | 不通过 | C1（d′换算）、C3（D_sep 空转）、C5（验证率双口径）三项红线违规 |
| 18 | 内容越界检查 | 部分不通过 | content §2.2–§2.5 渗入方案参数细节（M6） |
| 19 | 历史遗留问题逐条核对 | 通过 | 见第 6 节核对表（5 项已解决、3 项残留、2 项转化升级） |

## 3. 写作风格评估（程序化检测引用）

**程序化检测发现 AI 写作模式，表达质量被强制限制在 0.50 以下。**

- 超长句（>120 字）：31 处，免赔 5 处，罚 0.52 —— 最严重项。critic 独立复核：rationale 11 / content 8 / scheme 11；最重单句 247 字（content L27 五指纹量定义句），次重 144 字（content L31 预期产出句）。
- 模板句式"为…提供…"：程序计 9 次（阈值 8，罚 0.03）。critic 宽口径正则实测 25 处（含"为…提供先例/基准/依据"变体），二者不矛盾：程序窗口更严。anti_ai_patterns 上限 15 次，宽口径已接近上限。
- 关联词：'同时' 14 次（content 独占 8 次，密度最高），'然而' 3、'此外' 1、'因此' 1，合计 19（阈值 20 边缘通过，但"同时"单点集中是 AI 味主要来源）。
- 冗余修饰 32 处（阈值 41 内）：'完整' 9 次（scheme 独占 6）偏高频。
- 通过项：meta_discourse 0（但 content L29 存在"待 R2 末段定量给出"工作流残留，程序未捕获，人检发现，见 H4）、excessive_bold 合规、bullet 替代 0、self_reference 0。
- 叙述式合规性总体判断：宏观叙事结构合格（无知识罗列、无 bullet 堆砌、引用嵌入式论证达标），微观句法卫生不合格（长句密度为范本锚点的数倍量级）。表达质量 = 0.45（0.60-0.69 档下修：大量模板套话 + 强制天花板 0.50）。

## 4. 锚点对比（强制项）

**对比一（语体·句法卫生）——rationale §1.2 vs rationale_example**

申请书原文（rationale L19，141 字单句）：
"MnTe 的 g-wave 自旋劈裂在 370 meV 量级，域工程（场冷±0.4 T）可将六重对称畴压至二重对称 [6]；软 X 射线 ARPES 进一步区分了弱交变 LKSD（节点面内 SOC 主导，约 100 meV）与强交变 LKSD（面外交换主导，约 0.5 eV）两机制。"

锚点（rationale_example）：
"2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生。"
（单句单一论断，年份+人物+[N]+单一观测事实，60 字内收束。）

差距：锚点句"一个事实一句话"，引用 [N] 紧跟人物；申请书句用分号捆三个论断（劈裂量级+域工程+两机制区分）成 141 字长句，信息密度高但可读性降档。语体方向不差（嵌入式引用已对标），差距在**句法切分纪律**：范本超 120 字句为 0，本稿 31 处。改写方向：按"量级→域工程→机制区分"切三句，每句一个 [N] 锚点。

**对比二（论证密度·数据驱动）——content §2.3 vs content_example**

申请书原文（content L27 节选，全句 247 字）：
"在圆偏振驱动下，i-wave 自旋劈裂的 HHG 响应具有五个可辨识特征：一是谐波螺旋度交替幅度 A_helicity（定义为左旋与右旋圆偏振驱动下同阶谐波产额的相对差值），二是椭圆度响应斜率 S_ellipticity（定义为谐波椭圆度对驱动椭圆度的导数在圆偏振基准点附近的值），三是偏振旋转角 θ（谐波偏振主轴相对于驱动偏振的旋转角度），四是……五是……"

锚点（content_example）：
"本项目拟采用理论与实验相结合的研究方法，建立包含局域电子态效应的量子轨迹模型，揭示局域电子态对高次谐波产生过程的影响机理。"
（总述段一句交代"方法→模型→机理"，定义性内容下沉到分方向内部逐个展开。）

差距：**数据驱动维度本稿强于锚点**（五指纹量全部带可操作定义，量化密度高），这是优点；但五个定义压缩进单句 247 字，违背范本"每段 3-6 句、150-300 字"的段落节奏——一句占满一段。改写方向：五指纹量改为"总起句 + 每指纹量一句"的 6 句段落，或拆为两段（前三个谱学量/后两个阶次量），信息不变。

**对比三（引用嵌入·可行性链）——scheme §3.6 vs scheme_example**

申请书原文（scheme L65）：
"原理成立性：THz 驱动层间剪切声子的原理已在 h-BN 体系中被数值验证 [36]，该工作以机器学习力场分子动力学模拟证明 THz 脉冲可在 ps 内驱动层间滑移极化翻转；NiO 反铁磁绝缘体中的 THz-HHG 磁序读出 [20] 在实验上证明了 HHG 辐射与磁序参量动力学的时间同步；本课题组在固体 HHG 实验平台 [29] 与交变磁 HHG 选择定则方面有预研积累数据。"

锚点（scheme_example）：
"在前期的工作中，我们已经熟练掌握了利用含时薛定谔方程、含时密度泛函理论研究理想晶体高次谐波的数值模拟方法。为了适应本项目的研究，需要在理想晶体的计算中引入杂质的作用……"
（第一人称预研叙述，"已掌握→需引入→将采用→首先→然后"步骤流。）

差距：申请书 §3.6 的"方案→原理→结论"链式结构与锚点合规，文献嵌入方式（"已在 X 体系被验证 [36]"）与锚点同构；但锚点还包含**课题组自身预研的第一人称交代**，申请书仅一句带过（"本课题组…有预研积累数据"无任何量化支撑，如平台参数、已发表预研条目），预研基础的论证密度低于锚点。改写方向：§3.6 补 2-3 句课题组平台具体能力（中红外波长范围、THz 场强实测值、已发表选择定则工作的 [29] 具体结论）。

锚点对比结论：差距明显

依据：四个强制维度中，论证密度、数据驱动、引用嵌入三项基本达到锚点水准（个别处如数据驱动甚至超出），但**语体维度差距显著**——范本锚点超 120 字句为 0，本稿 31 处且分布三章均匀；模板句式 9 次超标；另存在范本中不可能出现的工作流元话语残留（content L29"待 R2 末段定量给出"、scheme 三处"content.md §…"文件名交叉引用）。按 v6.9.25 绑定规则：表达质量 ≤ 0.69（实际受程序天花板双限制 0.45）、综合评分 ≤ 0.84（实际 0.65）。

## 5. 跨章节指标一致性审查

### 5.1 程序预检三项差异的核对结论

| 指标 | 数值集分布 | 核对结论 |
|---|---|---|
| 时间 fs | rationale:[500]；content:[100]；scheme:[10,100,50] | **口径差异，非矛盾**。500 fs=Rajpurohit 切换窗口 [21]；100 fs=NEB 极化反转时标 [35] 与泵浦-探测分辨率目标；10 fs=光路抖动要求；50 fs=延迟扫描步长。四个不同物理量，各有归属，无需修改。 |
| 百分比 | content:[10,50,70,80,90,99]；scheme 多出 [20] | **scheme 独有的 20% 是真问题**：scheme L29"偏差 ≤ 20%"与 scheme L31/content §2.3 的"2 倍因子内一致"（=100% 偏差）构成同一指标（平台一验证）双口径 → C5。其余 90/70/80/99 在 fallback 逻辑链中口径一致（content §2.6 ↔ scheme Go/No-Go）。 |
| 能量 meV | rationale:[100,138,370,40]；content/scheme:[40] | **口径差异，非矛盾**。100 meV=弱交变 LKSD、138 meV=Fe₂CoGaTe₂ i-wave、370 meV=MnTe g-wave（均为文献值）；40=16–40 meV 势垒区间上界，三章一致（"16–40 meV"全文 9 处无漂移）。 |

### 5.2 程序预检未覆盖、本轮发现的口径矛盾

见问题清单 C1（d′≥3↔99%）、C3（D_sep 先验空转）、C4（[33] 一号两绑）、C5（验证率双口径）、H2（+50 ps 窗口 vs ps-ns 磁序层）、H1（R3 时序矛盾）。**结论：程序预检的三项警报中仅"百分比 20%"是真矛盾；程序未覆盖的数值互洽类问题（d′ 换算、meV↔THz、D_sep）是本轮 critical 的主体，后续轮次预检规则建议补入"同量纲换算互洽"与"指标-先验交叠"两条规则。**

### 5.3 术语一致性矩阵（抽查）

| 术语 | 出现位置 | 判定 |
|---|---|---|
| i-wave/第四型 | rationale L69"第四型"；content ×4"第四型"；scheme 0 次（一律 i-wave） | "第四型"序数无定义（M1），建议统一为"i-wave（C₄ 对称）" |
| Berry/Bery | rationale L35、content L35"Bery 曲率"；其余 15+ 处"Berry" | 错拼 ×2（H3） |
| 泵浦-探测/泵浦-探针 | content L19"泵浦-探针实验"；全文其余"泵浦-探测" | 单点漂移（M4） |
| 层锁定的 Berry 曲率 | content L31"层锁定"；[33] 标题"helicity-layer-lock" | 术语可，但该句 [33] 归属冲突（C4） |
| NRSS/SST-4B | rationale L55 / L11 | 各仅 1 次且未展开定义（H3 合并处理） |
| 方晶格/准交变磁 | rationale L53（[30] 匹配）、content L31/L49、scheme L5 | 一致 ✓ |

## 6. 历史遗留问题核对表（逐条实测）

| 历史问题 | 本轮实测 | 判定 |
|---|---|---|
| [P1] content 超长句 13.6% 偏高 | content >120 字句 9→8 处，全稿 31 处 | **仍存在**（并入 H5，severity 维持 high） |
| [P0] Floquet 驱动场强上界缺失 | content L39"场强上限 0.3 MV/cm"、L51"窗口 0.01–0.3 MV/cm"、scheme L45 同口径 | **已解决** ✓ |
| [P0] content L27 [17] Ghorashi-Rappe 错配 | rationale L23 / content L23 / scheme L29 均已改 [18] | **已解决** ✓ |
| [P0] content L43 [21] Yarmohammadi 错配 | rationale L25 / content L39 / scheme L49 均已改 [22]，[21]=Rajpurotit 归位 | **已解决** ✓（另注：rationale L25"Rajpurotit"拼写应为 Rajpurohit，随 H3 一并修） |
| [P1] content 9 句 >120 字 | 降为 8 句 | **部分改善，仍存在**（H5） |
| [P1] content 7 处 arXiv 裸引 | content 全文 0 处 arXiv 字样；scheme L75 的"arXiv"为检索范围列举非引用 | **已解决** ✓ |
| [P1] 目标二 vs 关键科学问题二量级跳跃（99% vs 90%/70%） | fallback 链已建立（90%→融合→70%），但"≥99% 与 d′≥3 等价"的换算本身错误 | **转化升级**为本轮 C1（critical） |
| [P1] [11] 绑 5 体系 | 现绑 3 种口径：滑移/莫尔铁电性（rationale L13）、机械滑移实验手段（L31）、NiCl₂/VS₂/CrSe₂ DFT 势垒（L53/content/scheme） | **部分残留**（H8，scope 缩小） |
| [P1] "针对瓶颈一/二/三"三段段首僵硬平行 | grep"针对瓶颈"=0，§2.2–§2.4 段首已改为内容驱动衔接 | **已解决** ✓ |
| [P1] §2.3"两个特征"实为三个 | content L27 已改"五个可辨识特征：一是…五是…"，与 scheme §3.3 五指纹量定义逐项对齐 | **已解决** ✓（且升级为五，跨章自洽） |

**小结：10 项历史问题中 6 项已解决、2 项部分残留、1 项并入本轮、1 项转化升级为 critical。writer 本轮修复效率良好，但新推文本引入了新的 critical 级数值互洽问题。**

## 7. 问题清单

### [critical] C1 red_line/indicator_measurable — d′≥3 与"分类准确率 ≥99%"等价换算错误
- 位置：content L49（目标二）、L59（关键科学问题二）；scheme L31、L83（创新点二量化优势）
- 问题：等方差双分布下最优判别准确率 = Φ(d′/2)。d′=3 → Φ(1.5)=93.3%，**不是 99%**；要达到 99% 需 d′=4.65。scheme L83 还将 d′≥3 误读为"分离显著性 3 倍 sigma"——3σ 均值间距恰恰对应 93.3% 而非 99%。四处同错，属同一指标跨章口径错误的 P0 红线（indicator_red_lines.consistency_check + indicator_measurable）。
- 建议：二选一并全稿统一——(a) 保留 d′≥3，把准确率承诺降为 ≥93%；(b) 保留 ≥99%，把指标改写为 d′≥4.65。同时删除"即分离显著性 3 倍 sigma"的错误注解，改为"d′=3 对应等方差双高斯 93.3% 最优判别准确率"。
- action：recalculate + rewrite；违反 scoring_rubric.rigor"0.60-0.69 存在指标矛盾"档、indicator_red_lines.consistency_check/indicator_measurable。

### [critical] C2 rigor — 层间滑移势垒 16–40 meV 与剪切声子频率 0.5–3.0 THz 的换算硬伤，动摇"共振驱动"可行性论证
- 位置：scheme L67（可行性·关键指标可达性）、scheme L17；content L7、rationale L31 同源表述
- 问题：1 meV = 0.2418 THz，16–40 meV 对应 3.9–9.7 THz，与宣称的 0.5–3.0 THz 区间**零重叠**。且物理上势垒高度（能量）与声子频率（势阱曲率）不是同一量，"势垒对应频率"本身需用 DFT 力常数计算而非换算。scheme L67"与 THz 源的调谐范围重叠"是 Go/No-Go 级可行性论断，当前数值链不成立；content L7"THz 驱动场强 0.1–1.0 MV/cm 与该势垒形成共振条件"还有范畴错误（场强不与势垒共振，频率才共振）。
- 建议：(1) 从 [11] 或补充文献中取 NiCl₂/VS₂/CrSe₂ 层间剪切声子频率的 DFT 直接计算值（ℏω=曲率），替换"势垒换算"逻辑；(2) 若真实剪切频率落在 3.9–9.7 THz，须同步修改 THz 源参数论证（商用源在 1–10 THz 可调）与 Floquet 窗口 0.5–3.0 THz 的关系说明；(3) content L7 改为"THz 驱动频率与层间剪切声子频率共振"。
- action：recalculate + verify（核对 [11][34] 是否给出剪切声子频率数值）；违反 indicator_red_lines.no_exaggeration/implementation_path、scoring_rubric.feasibility"0.60-0.69 核心技术路线缺乏支撑"档。

### [critical] C3 red_line — D_sep ≥ 0.80 指标在先验下自动满足（指标空转）+ ps 降级方案违反采样定理
- 位置：content L37/L51（目标三）、scheme L41-43（定义式）、L59（难点三降级论证）
- 问题：按申请书自身先验（电子层衰减 <1 ps、磁序层 ps-ns、扫描窗口 −5 至 +50 ps），f_e(t)·f_m(t) 重叠积分趋零，D_sep ≈ 1 是设计使然的必然结果——指标与先验同值即失去考核意义。降级论证"ps 量级分辨率下…仍可实现 ≥80% 分离度"违反 Nyquist：亚 ps 电子层衰减在 ps 采样下混叠为瞬时伪影，D_sep 数值虽高但"电子层响应衰减至基线"的物理读出不可分辨。且 D_sep 定义式无噪声底处理（分类指标有 10% 高斯噪声，D_sep 却在无噪声理想波形上定义）。
- 建议：(1) 把 D_sep 的考核改为"含噪重建"口径（对 f_e/f_m 加入与分类判据同级的噪声后再算重叠）；(2) 或改用更有区分度的指标（如磁序层拟合时间常数的相对误差 ≤20% 且电子层残留串扰 ≤10%）；(3) 删除或重写 scheme L59 的 ps 降级段落，明确降级模式下哪些物理量仍可提取、哪些不可。
- action：recalculate + rewrite；违反 indicator_red_lines.indicator_measurable/uncertainty_constraint、scoring_rubric.rigor"0.60-0.69"档。

### [critical] C4 rigor — [33] 一号两绑：Zhang 泵浦-探针实验 与 Lin TDDFT 模拟共用一个编号
- 位置：content L19"2025 年 Zhang 等人的泵浦-探针实验 [33] 已在双层类 h-BN 铁电体中观测到亚 ps 层间滑移"vs content L31"Lin 等人的 TDDFT 模拟 [33] 已证明滑移铁电双层中圆偏振高次谐波的螺旋度…"；references [33] = Lin Z et al.（helicity-layer-locking）
- 问题：同一编号绑两个不同作者组、两种不同工作类型（实验 vs TDDFT 理论）。Zhang 的 h-BN 亚 ps 滑移动力学实验应另配编号（候选：[31] Wang Y 深度学习 MD 或 [36] Wang J——需 writer 核对真实文献后定），当前状态下评审专家一查即穿。
- 建议：核实 Zhang 2025 泵浦-探针实验的真实出处，分配独立编号并全稿统一；同步检查 scheme L15"[33, 35]"的光应力/位移电流机制归属是否受影响。
- action：verify + rewrite；违反 scoring_rubric.rigor"<0.60 多处事实错误"单项触发条（引文归属错误按本 skill 严重度标准为 critical）。

### [critical] C5 red_line/consistency_check — 平台一"验证"指标双口径：偏差 ≤20% vs 2 倍因子内一致
- 位置：scheme L29"验证在无噪声条件下指纹量的理论值与数值模拟值的偏差 ≤ 20%"vs scheme L31"验证率 ≥ 80%，即 5 个指纹量中至少 4 个的理论值与模拟值在 2 倍因子内一致"（content L49 承接后者口径）
- 问题：同一指标（平台一指纹验证）在同章相邻两段给出两个数值口径——20% 偏差与 2 倍因子（=100% 偏差）相差 5 倍，评审将直接质疑承诺底线。P0 红线"同一指标在不同章节（此处甚至同章）数值或口径必须一致"。
- 建议：统一为单一判据。建议保留"至少 4/5 指纹量偏差 ≤20%（无噪声）"作为严格口径、删除"2 倍因子"宽松口径；或将 2 倍因子明确降级为"含噪/含 Rashba 扰动下的最低可接受线"并分开命名（严格验证率 vs 鲁棒验证率）。
- action：rewrite；违反 indicator_red_lines.consistency_check、scoring_rubric.rigor"0.60-0.69 指标矛盾"档。

### [high] H1 red_line/timeline — R3 启动时序自相矛盾
- 位置：scheme L7"R3（时域分离方案设计，Year 1 Q4–Year 4 Q4）"vs scheme L106（年度表 Year 3 H1）"R3 启动泵浦-探测方案设计"
- 问题：技术路线称 R3 于 Year 1 Q4 启动，年度计划表称 Year 3 H1 启动，相差约 1.5 年；且 L7 自述 R3"整合前两者的理论预测"，逻辑上不可能先于 R1/R2 产出而启动。
- 建议：统一为 Year 3 H1 启动（与"整合前两者"逻辑一致），L7 改为"R3（Year 3 H1–Year 4 Q4）"；若确需 Year 1 Q4 开始预备性调研，须在年度表加一行区分"预研"与"启动"。
- action：rewrite；违反 indicator_red_lines.consistency_check、section_standards.scheme。

### [high] H2 rigor — 延迟扫描窗口 +50 ps 无法覆盖宣称的 ps-ns 磁序层演化
- 位置：scheme L37"时间延迟扫描范围设定为 −5 ps 至 +50 ps…覆盖电子层衰减（<1 ps）与磁序层演化（ps-ns 量级）的完整时间窗口"
- 问题：ns = 1000 ps，+50 ps 窗口对 ns 量级磁序恢复的覆盖率仅数个百分点，"完整时间窗口"名不副实；与 content §2.4"磁序恢复（ps-ns）"的口径冲突。
- 建议：二选一——(a) 若磁序层指 ps 至数十 ps（如 Néel 矢量相干进动），把"ps-ns"改窄为"ps–数十 ps"并说明 ns 尾段不在本轮范围；(b) 若确需 ns，加"分段扫描"说明（对数延迟轴或双窗口）。
- action：rewrite；违反 indicator_red_lines.consistency_check、uncertainty_constraint。

### [high] H3 rigor — "Bery 曲率"错拼 ×2 + 未定义缩略语 NRSS/SST-4B + "Rajpurotit"人名拼写
- 位置：rationale L35、content L35（Bery）；rationale L55（NRSS，全稿仅此一次未展开）、L11（SST-4B 未展开）；rationale L25（Rajpurotit→Rajpurohit）
- 问题：以 Berry 曲率为核心概念之一的申请书正文两处拼成"Bery"，属评审观感级硬伤；NRSS（应为 non-relativistic spin splitting）与 SST-4B 均为单次出现未定义缩略语。
- 建议：全局替换"Bery→Berry"；NRSS 首现处展开"非相对论自旋劈裂（NRSS）"或直接用中文全称；SST-4B 补"层间 SST-4B 对称性破缺型自旋劈裂"一句定义；人名更正。
- action：rewrite；违反 writing_style_rules、scoring_rubric.expression"0.70-0.79 术语漂移"档（rigor 侧计）。

### [high] H4 rigor/pipeline_integrity — 正文残留工作流元话语与源文件名交叉引用
- 位置：content L29"（待 R2 末段定量给出）"；scheme L25"对应 content.md §2.3 定义的五个指纹量"、L35"已在 content.md §2.4（源头见立项依据 §1.3）明确"、L47"content.md §2.4 设定亚 100 fs 分辨率为目标"；content L59"（见 references [32]）"；content L51"（窗口 0.01–0.3 MV/cm，与方案章节 §3.4 一致）"
- 问题：正式申请书不得出现内部文件名（content.md）与评审轮次标记（R2 既指研究主线又与评审轮次 R2 混淆）；"待…给出"是未完成内容的占位声明，程序 meta_discourse 检测未捕获但属同类。
- 建议："content.md §2.3"→"第二部分研究内容之二"；"待 R2 末段定量给出"→直接给出阈值（同段两行后已有 50% 阈值，见 M3，顺带解决）；"见 references [32]"→"见文献 [32]"；"与方案章节 §3.4 一致"→删除（指标应自含口径）。
- action：remove + rewrite；违反 writing_style_rules.meta 相关清理要求、学术规范。

### [high] H5 anti_ai — 超长句 31 处（>120 字），罚 0.52，表达质量天花板 0.50 的主因
- 位置：全稿分布 rationale 11 / content 8 / scheme 11；最重：content L27（247 字）、content L31（144 字）、rationale L19/L21（141/128 字）
- 问题：程序化检测 severe_count=31（免赔 5），罚 0.52。范本锚点超 120 字句为 0；anti_ai_patterns 明令"超过 120 字属严重超长句"。历史问题（content 13.6%）部分改善但未达标。
- 建议：优先拆解 content L27（五指纹量定义句→总起句+每量一句）、content L31（预期产出句→分号改句号）、rationale L19/L21/L23（三阶段段落中分号捆的多论断句逐一切开）；目标全稿 >120 字句降到 ≤5（免赔额度内）。
- action：rewrite；违反 anti_ai_patterns"超长句：超过 120 字属严重超长句"、scoring_rubric.expression 强制档。

### [high] H6 anti_ai — 模板句式"为…提供…"9 次超标 + "同时"14 次单点集中 + 冗余修饰"完整"9 次
- 位置：程序计数模板句 9 处（阈值 8，罚 0.03）；critic 宽口径 25 处接近上限 15 的两倍；"同时"content 独占 8 次；"完整"scheme 独占 6 次
- 问题：anti_ai_patterns 上限"为提供类句式 15 次"，宽口径实测已 25；"同时"高频是死板关联词主源。
- 建议：(1) 按反模式清单替换——"为 X 提供基础/工具/依据"→"支撑 X""确立 X""作为 X 的判据"；(2) content §2.2–§2.4 中 8 处"同时"至少删减 5 处（多数可直接删词或改"；"分句）；(3) scheme"完整理论框架/完整闭环/完整时间窗口"6 处"完整"删 4 处。
- action：rewrite；违反 anti_ai_patterns.remove 第 2/1/5 条。

### [high] H7 boundary/redundancy — 跨章逐字重复：核心句三连抄
- 位置：(a) 范式句"范式 A…回答'能否驱动'的问题，建立光-晶格-自旋三体耦合的非线性响应理论"content L9 ≈ scheme L5 逐字重复；(b) "真正可时域分离的只有'电子层（fs-ps…）'与'磁序层（ps-ns）'两个层次"rationale L35 / content L35 / scheme L35 三章逐字三连抄；(c) "16–40 meV/unitcell"9 处、"0.1–1.0 MV/cm"11 处高频复现
- 问题：三章对同一物理图像采用复制粘贴而非"一处完整论证+他处简引"，既冗余又放大后续修改的失同步风险（本次 C2 修换算时就须改 9 处）。
- 建议：rationale §1.3 保留完整论证（首次出现）；content §2.4 改为"如立项依据 §1.3 所析，电子层与磁序层构成唯一可分离的两层"一句简引；scheme §3.4 删除重复解释，直接引用结论；范式句在 scheme §3.1 压缩为半句。
- action：rewrite；违反 prompt 内容越界条款"跨章节大量重复内容"、style_benchmark.narrative_density。

### [high] H8 rigor — [11] 一号多口径残存（历史问题部分残留）
- 位置：rationale L13"滑移/莫尔铁电性 [11]"、L31"机械滑移 [11]"（实验手段口径）、L53/content L7/L13/scheme L17/L103"NiCl₂/VS₂/CrSe₂ 滑移势垒 [11]"（DFT 势垒口径）；references [11] = Sheng 等系统性 DFT 堆叠工程理论
- 问题：[11] 是理论计算文献，L31 将其绑"机械滑移"这一实验调控手段的口径仍错位（该句意在说明现有实验调控手段慢，应引实验文献）；L13"滑移/莫尔铁电性"与堆叠工程 DFT 亦非同一对象。
- 建议：L31 的"机械滑移 [11]"改引滑动铁电实验文献（如 [31]/[36] 系）或补独立编号；L13 的 [11] 限定为"堆叠工程诱导自旋劈裂的系统性计算 [11]"。
- action：verify + rewrite；违反 indicator_red_lines 一致性要求、引文归属纪律。

### [medium] M1 rigor — "第四型交变磁自旋劈裂"序数称谓无定义且非公认
- 位置：rationale L69；content L21/L23/L49/L59
- 问题：交变磁性分类无公认"第四型"序数（d/g/i 按晶格波矢分类，序数因计数起点而异），首次出现未定义前三个型是什么，评审可质疑术语自造。
- 建议：统一改为"i-wave 自旋劈裂（四重旋转对称 C₄、节点线过 Γ）"，删除全部"第四型"序数（5 处）。
- action：rewrite；违反术语规范。

### [medium] M2 rigor — 目标一"不确定性 ≤10%"以 3 个泛函样本方差度量，统计效力不足
- 位置：content L47、scheme L17
- 问题：3 样本方差自由度仅 2，"≤10%"的置信区间宽到几乎不可证伪；且"泛函离散度"与"统计不确定性"是两个概念混用。
- 建议：改述为"泛函间最大相对离散 ≤10%（PBE/PBE+U/HSE 三者极差/均值）"——极差口径 3 样本也可定义；或补第 4 个泛函/刀切法。
- action：rewrite；违反 indicator_red_lines.indicator_measurable。

### [medium] M3 rigor — Rashba 干扰阈值"待 R2 末段定量给出"与同段已用 50% 阈值自相矛盾
- 位置：content L29
- 问题：前半句称阈值"待 R2 末段定量给出"（未完成占位），同段后半句已使用"变化超过 50%"作为判定阈值——同一阈值一处说没有、一处已在用。
- 建议：删除"待 R2 末段定量给出"，直接定义"阈值取指纹量基线值的 50%"，与 scheme §3.5 难点二的 50%/10% 口径对齐。
- action：rewrite；违反 indicator_red_lines.consistency_check。

### [medium] M4 terminology — "泵浦-探针"与"泵浦-探测"漂移
- 位置：content L19（唯一一处"泵浦-探针实验"）
- 建议：统一为"泵浦-探测"。
- action：rewrite。

### [medium] M5 novelty_claim_cautious — 两处未限定检索范围的绝对声明
- 位置：rationale L35"这一方案在现有文献中未被提出"；content L13"层间滑移自由度从未被作为独立动力学变量引入强场超快物理研究框架"
- 问题：§1.5（rationale L63）与 scheme §3.7（L75）均有规范的"据截至 2026-08 检索（WoS/arXiv/APS-IOP）"限定版本，但此两处未复用限定语，绝对化表述在限定版之外构成红线软违规。
- 建议：两处复用 §1.5 的限定句式（"据目前检索…尚未见"）。
- action：rewrite；违反 indicator_red_lines.novelty_claim_cautious。

### [medium] M6 boundary — content 渗入研究方案参数细节
- 位置：content L47（PBE/PBE+U/HSE 泛函方差）、L49（Monte Carlo 200 次采样）、L51（驱动场强窗口+方案章节指针）
- 问题：section_standards.content 明令"不出现研究方案细节（技术手段、参数、装置）"。量化指标本身合规，但指标的可实现路径参数（泛函三件套、采样次数）属方案层内容。
- 建议：content 保留指标名与数值（"切换概率不确定性 ≤10%""区分度 d′≥3"），把度量方式（泛函方差/MC 采样协议）移至 scheme §3.2/§3.3（现已存在，删 content 侧即可）。
- action：remove + rewrite；违反 section_standards.content 第 4 条、content_boundaries。

### [medium] M7 rigor — rationale 正文编号引用密度超上限
- 位置：rationale 全文 [N] 引用实例如 50 次（distinct 31/36）
- 问题：section_standards.rationale 要求"正文引用 35-47 次"，实测 50 次略超上限；[13]（Gonzalez-Hernandez 电控自旋劈裂）在全稿三章节中零引用（僵尸条目，参考文献专轮处理，此处备案）。
- 建议：合并低信息引用（如 L9 连续 [8][8,9][8] 三处可并为两处）；[13] 若保留需在 §1.4 国内现状或 §1.1 补一处引用，否则从文献表删除。
- action：verify + rewrite；违反 section_standards.rationale 第 4 条。

### [low] L1 expression — "THz 乃至亚-THz"递进方向颠倒
- 位置：rationale L5
- 建议：改为"亚 THz 至 THz 频段"。
- action：rewrite。

### [low] L2 rigor — [8,9] 绑"剥离极限单层"实验口径存疑
- 位置：rationale L9"剥离极限可达单层或 few-layer，界面化后磁性保持稳定 [8,9]"，[8] 为 MnPS₃|TMDC 堆叠理论计算文献
- 建议：单层剥离与磁性保持应引 MnPS₃ 实验表征文献，[8] 仅覆盖堆叠计算部分。
- action：verify。

### [low] L3 expression — "80%"双语义近邻易混
- 位置：content L49（验证率 ≥80%）与 L51（D_sep ≥0.80）相邻两段
- 建议：其一改述（如 D_sep 写"0.80 以上"或验证率写"五分之四指纹量"）避免评审误读为同一指标。
- action：rewrite。

### [low] L4 config — prompt 引用的两个标准键不存在
- 位置：nsfc-standards.json（顶层 8 键 + general_principles 12 键中均无 programmatic_checks / overall_review_requirements）
- 问题：prompt 要求重点读取的两键缺失，本轮按纪律未虚构其规则，以 prompt 附带程序报告替代。
- 建议：管线侧修复 prompt 模板或在 standards 中补齐两键，避免每轮重复备案。
- action：verify（管线配置）。

## 8. 对抗结论

- 本轮发现 24 个问题（critical 5 / high 8 / medium 7 / low 4）。
- 相比上一轮（scheme 专项：3 critical 遗留 + 内容线问题）：历史 10 项中 6 项已解决、2 项部分残留、2 项转化升级；本轮新增 critical 5 项中 4 项（C1/C2/C3/C5）为 writer 新推 content/scheme 文本引入的数值互洽类问题——修复速度良好但新增文本的定量自洽校验缺失，建议 writer 建立改稿后"数值链条自检清单"（换算类：meV↔THz、d′↔准确率；口径类：同一指标单一口径；窗口类：指标-先验交叠）。
- 程序预检 3 项警报核对：fs 与 meV 两组为合理口径差异（结案），百分比组的 scheme-20% 为真矛盾（已立 C5）。
- 是否达到输出标准：**否**。general 阈值 min_overall 0.85 / max_high_issues 0 / max_medium_issues 3，本轮综合 0.65、high+ 13 项、medium 7 项，全部超限。5 项 critical 中 C1/C2/C3 直接动摇三项研究目标的量化承诺，C4 为引文归属硬伤，C5 为同章口径矛盾——P0 返工优先级：C4（一分钟可修）→ C5 → C1 → C2 → C3。
- 下一轮建议聚焦：C2 修复后的物理链条复审（THz 源参数-剪切声子频率-Floquet 窗口三者联动修改的一致性）+ H5 超长句拆解后的 content.md 复测；references 专轮顺带处理 [13] 僵尸条目与 [33] 重编号的文献表联动。

---

评分依据（档位对照，置于评分块之前以保解析格式）：
- 创新性 0.82 → rubric.innovation"0.80-0.89：明确创新点，在已有方向上提出新视角/新方法/新机制，与前人有清晰区隔"——滑移坐标升格为动力学变量、i-wave 五指纹反演表、时域分层测量三个创新点区隔清晰；不足 0.9 档因整体为已有框架（[18][22][32]）的推广组合，未达"全新科学问题/范式"。
- 可行性 0.72 → rubric.feasibility"0.70-0.79：基本可行但存在风险点，部分关键技术缺少预研验证"——理论先行+课题组双平台预研是加分项，但 C2 共振换算错误使核心可行性论断当前不成立，R3 时序矛盾（H1）削弱计划可信度。
- 严谨性 0.62 → rubric.rigor"0.60-0.69：论证有明显缺陷，存在事实错误、指标矛盾"——C1/C3/C5 三项指标矛盾 + C4 引文归属错误 + 红线违规按纪律扣入 0.6-0.7 区间下沿。
- 表达质量 0.45 → rubric.expression"<0.60：大量模板套话"与"0.60-0.69"之间，受程序天花板 0.50 双重限制（超长句 31 处罚 0.52 + 模板句超标罚 0.03）。
- 综合 = (0.82+0.72+0.62+0.45)/4 = 0.6525 ≈ 0.65（本轮四维度等权，锚点结论=差距明显 → 综合上限 0.84、表达上限 0.69，均满足）。

## 评分
创新性：0.82
可行性：0.72
严谨性：0.62
表达质量：0.45
综合评分：0.65
