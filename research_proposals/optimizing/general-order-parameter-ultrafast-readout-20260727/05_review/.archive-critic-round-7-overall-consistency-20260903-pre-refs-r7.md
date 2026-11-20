# 对抗评审报告（第 7 轮 · 整体一致性审查）

## 元信息

- 申请书：altermagnet HHG 序参量可辨识性研究（面上项目 general）
- 审查日期：2026-08-21（晚间轮次；文件时间戳：rationale 11:02 / scheme 18:35 / content 18:36 / references 09:40 / full_review 08-19 07:43）
- profile：critic（NSFC 红队）
- 本轮聚焦：三章节 + full_review.md + references.md 的**整体一致性审查**（逻辑衔接、术语一致性、内容冗余/矛盾），不做逐段细审
- 事实核实：所有事实判断基于本轮实际读取全部五个文件 + Python 脚本交叉验证（[N] 编号双向对照、参数口径频次统计、超长句/修饰词/关联词统计、术语漂移扫描），未依赖记忆或上轮印象
- 归档说明：本文件名 critic-round-7.md 原存当日 12:00 的"研究方案段落级深审"版（74428 字节），已先复制为 `05_review/.archive-critic-round-7-scheme-deephreview-20260821.md` 后再写入本报告，无数据丢失
- 评分口径：4 维度（创新/可行/严谨/表达）各 0.25 等权（v6.9.25 评分纪律；上轮方案深审报告 0.71 使用了 0.30/0.25/0.25/0.20 变权重，本轮起统一等权，历史分数不直接可比）

---

## 0. 模块完整性检查

✅ 通过。三段式结构完整：rationale.md（81 行，4 小节：研究意义/现状/关键科学问题/总体框架）、content.md（75 行，6 小节：§2.1 框架/§2.2 R1/§2.3 R2/§2.4 R3/§2.5 特色创新/§2.6 年度计划）、scheme.md（101 行，7 小节：总路线/理论/实验/可行性/难点/创新/成果）、references.md（191 行，44 条 [N] 条目）。符合 general 三段式硬性要求。

一处结构偏移：按 proposal_templates.general，年度计划与预期成果应属（二）研究内容；当前年度计划在 content §2.6 与 scheme §7 **双写**，预期成果仅在 scheme §7（full_review.md §7 第一条已自认此归属张力）。见 M4。

---

## 1. 执行清单对照（逐条）

| # | 清单项 | 判断 | 证据 |
|---|---|---|---|
| 0 | 模块完整性 | ✅ 通过 | 见上节 |
| 1 | 读取全部文件与标准 | ✅ 通过 | 五文件 + nsfc-standards.json 全文读取 |
| 2a | 以科学问题为主线 | ✅ 基本通过 | "一个主体系、一个对照体系、一条可辨识性判据"贯穿三章 |
| 2b | 无 "A做了X B做了Y" 堆砌 | ❌ 不通过 | rationale L33 一段连续 8 个"某人等人"句（McCarter→Horstmann→Qiu→Sankar→Ren→Terashima→Du→Singh），脚本实测该行"等人"出现 8 次 |
| 2c | 无条目式表达替代论证 | ✅ 通过 | bullet_list_substitution 检测 0；全文叙述式 |
| 2d | 段间过渡与递进 | ✅ 通过 | R1→R2→R3 单向递进链明确（content §2.1） |
| 2e | 方案说明"为什么选这个方法" | ✅ 通过 | scheme §2 SBE 选择论证、§3 中红外选择理由均有 |
| 2f | 立项依据五层递进 | ✅ 通过 | 大背景（L5-L9）→脉络（L25-L47）→核心问题（L53-L67）→国内（L47）→定位（L69-L81） |
| 2g | 研究目标含量化指标 | ✅ 通过 | 三层判据（10%/1%/SNR>5/κ/后验 50%）均量化 |
| 2h | 创新四步闭环 | ✅ 基本通过 | scheme §6 三点均为"现有局限→方案→量化优势→收束"；但创新点（二）收束句 191 字超长（L81） |
| 2i | anti_ai 检测项 | ❌ 不通过 | 冗余修饰 27 次（阈值 12，扣 0.15）；>120 字超长句 18 处（扣 0.36）——程序化报告权威数据 |
| 2j | 指标红线 P0 | ⚠️ 部分不通过 | 13 项核心参数三章数值一致（见 §5 表）；但损伤阈值"预研已有 vs 启动后待标定"三处口径矛盾（H7） |
| 2k | 内容越界 | ⚠️ 部分不通过 | scheme §4"反演可行性"句逐字复述 §2 参数空间定义（H5，上轮 critical 已降级） |
| 2l | 锚点回归 | ✅ 已执行 | 见 §3 锚点对比 |

---

## 2. 写作风格评估（引用程序化检测）

程序化检测发现 AI 写作模式，**表达质量被强制限制在天花板 0.50 以下**（本轮实评 0.47）。

检测明细（全文 31321 字符）：
- ⚠️ redundant_modifiers：27 次（阈值 12，扣 0.15）——有效 ×11、系统 ×7、关键 ×5、完整 ×3、成熟 ×1。脚本按章定位：scheme.md 独占 15 次（rationale 6 + content 6），"有效约束/有效验证/系统/关键"高频集中在 scheme §2/§5/§6。
- ⚠️ long_sentences：18 处 >120 字（扣 0.36）。脚本定位（按句号/分号切分）最严重段落：rationale L11（150 字检索句）、L31（Fuchs 138 字 + Weber 145 字 + Schüle 148 字三连）、L33（Qiu 172 字）、scheme L7（139 字实验层句）、L19（145 字）、L81（191 字创新点二收束句）。
- ✓ 其余七项（transition_words 8 次贴阈值、template_phrases 0、template_subject 0、meta_discourse 0、excessive_bold 0、bullet_list 0、self_reference 1）全部通过——死板关联词、模板句式、加粗标记的治理成果明显，R28/R24 修复保持有效。

叙述式合规性总体判断：结构上是连贯研究故事（无 bullet 化、无八股模板），但**句长节奏失控是当前最大表达短板**——范本句长中位约 56 字、超 80 字句占 12%-28%，本文超 120 字"严重档"即有 18 处，远超范本分布上限。

---

## 3. 锚点对比（强制项）

**对比一（rationale 开篇语体 vs rationale_example）**

申请书原文（rationale L9）：
> "扫描隧道显微镜与角分辨光电子能谱在原子尺度具有极高的能量分辨率。但两者都难以对体相序参量做非破坏性测量——表面敏感性构成第一类瓶颈。常规 tr-ARPES 与超快电子衍射的时间分辨通常落在数十飞秒至皮秒窗口，阿秒条纹技术可达亚飞秒精度。但其探测深度局限于表面数层原子……"

范本锚点（rationale_example）：
> "高次谐波产生是飞秒激光与物质相互作用的高阶非线性、非微扰现象。基于高次谐波光谱的超快探测技术使得在飞秒甚至阿秒尺度上实时探测物质中电子及原子核的微观动力学过程成为可能。人们利用原子、分子气体高次谐波进行了大量气相原子分子的超快探测和控制研究[1-8]……2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生。"

对比：语体均为客观陈述+数据驱动（"数十飞秒至皮秒"/"亚飞秒"vs 范本"飞秒甚至阿秒"），论证密度接近；差距在引用嵌入——范本以 [1-8]/[9] 编号嵌入论证链，申请书此段无引用（可接受），但相邻 L33 段滑向 8 连"某人等人"平行排布 + 10 处"（X et al., arXiv:NNNN, YYYY）"括注式纯文本引用，范本中不存在这种双重引用风格。

**对比二（scheme §4 可行性 vs scheme_anchor）**

范本锚点（scheme_anchor）："可行性分析遵循'方案→原理→结论'链式论证，不复述方案细节。"

申请书原文（scheme L63 节选）：
> "反演可行性：参数空间 7—9 维以偏振—温度—磁场三重独立测量维度作为约束输入——三个维度各自作为连续变量在三维空间内形成多点采样，费舍尔信息矩阵的秩由测量点充分性决定，各参数方向梯度向量线性无关时矩阵满秩可计算条件数。"

对比：该句与 scheme §2 L27 的参数空间定义（"三类参数共计 7—9 个子参数，以偏振—温度—磁场三重独立测量维度作为约束输入。三个维度各自作为连续变量……矩阵满秩条件数可计算"）几乎逐字重合——这是"复述方案细节"，不是"方案→原理→结论"链。范本的可行性写法是"在前期的工作中，我们已经熟练掌握了……"式的能力论证。

**对比三（创新点 vs innovation_example）**

范本锚点每点约 200 字四步闭环；申请书 scheme §6 三点闭环结构齐全且带量化优势（κ 阈值、≤10% 判据、维度级信息），论证密度不低于范本；唯创新点（二）收束句 191 字（L81），范本单句均在 60 字内。

锚点对比结论：基本接近

（依据：语体、数据驱动、结构递进三项已对标范本；引用嵌入方式存在双轨分裂、句长节奏显著劣于范本、可行性一节复述方案细节，四项中两项有明确差距，未达"达标"所需的四项逐项举证。按 v6.9.25 绑定规则：表达质量 ≤0.79、综合 ≤0.89，本轮实评均满足。）

---

## 4. 跨章节一致性审查（本轮主体）

### 4.1 参数口径一致性表（脚本验证，全部 ✅）

| 指标 | rationale | content | scheme | 口径 |
|---|---|---|---|---|
| κ 可辨识阈值 | <10² / 10²—10⁴ / >10⁴（2 处） | 同（4 处） | 同（8 处） | ✅ 一致，Unicode κ 三章统一（LaTeX $\kappa$ 已清零——上轮残留已修复） |
| CrSb 信号判据 | ≥1%、SNR>5（2 处） | 同（3/4 处） | 同（4/5 处） | ✅ |
| TiSe₂ 复现判据 | ≤10%、±8%+2% | 同 | 同 | ✅ |
| Néel/相变温度 | 720K/310K/205K | 同 | 同 | ✅ |
| 场强窗口 | — | 0.8 V/Å（损伤） | 0.3—0.8 V/Å（8 处） | ✅ |
| 磁 Bragg 峰偏差 | — | <0.5% | <0.5% + <10K | ✅ |
| 后验约束 | — | 先验宽度 50%（5 处） | 同 | ✅ |
| 参数空间维数 | — | 7—9 | 7—9（4 处） | ✅ |
| 测量范围 | 4—300K/0—7T/0°—360° | 同 | 同 | ✅ |

13 项核心指标无一处数值冲突——这是相对历史轮次的实质改善。

### 4.2 引用编号一致性（脚本双向对照，❌ 多处失守）

44 条 [N] 条目、正文无幽灵编号（每个被引 [N] 均有条目）✅；但反向与归属问题严重：

| 编号 | 问题 | 定位 |
|---|---|---|
| [59] | scheme L19 将 **Wang** 多光子→隧穿标度转变标为 [59]；[59] 实为 Yue & Gaarde 规范工作。同文件 L63 同句 trio 引用全部正确（"[59] Yue、[60] Wang、[61] Zhang"），证明 L19 为错位残留 | scheme L19 vs references L115-119 |
| [60] | scheme L19 将 **Zhang CsPbBr₃ Keldysh 交叉**标为 [60]；[60] 实为 Wang | 同上 |
| [61] | scheme L19 将 **Uzner & Neufeld 层间耦合**标为 [61]；[61] 实为 Zhang 钙钛矿。**Uzner & Neufeld 在 44 条中无任何条目、无纯文本策略声明** | scheme L19 |
| [64] | Fuchs 双轨：rationale L31 纯文本（"Fuchs et al., arXiv:2503.04431"）vs content L59 [64] 编号；references L165 却称"rationale 行 31 以 [64] 编号引用"——三处状态互相矛盾 | 跨章 |
| [56] | Sankar 双轨：rationale L33 用 [56] 编号 vs scheme L39/L43/L63 纯文本 ×3（R27 策略），两章策略相反 | 跨章 |
| [65][66] | McCarter/Horstmann 双轨：rationale L33 纯文本 vs content L25 [65][66] 编号；references 称"rationale 行 35 与 content 行 23"——行号与引用方式双失实（实际 rationale L33、content L25） | 跨章 |
| [67] | references L165 称仅在 rationale 4 处引用，漏记 content（2 处）与 scheme（2 处）；full_review L83 R27 记录"scheme 的 [67] 已全部改纯文本"，当前 scheme L43/L63 又是 [N] 编号——writer 违反自设策略且 full_review 记录过时 | 跨章 |
| [55] | Jita 条目正文零引用，且 §8 豁免清单只列 [70][71][72]，未含 [55]——"正文直接引用 41 条"计数虚高（实际 distinct ≤40） | references §8 |
| [68] | 条目标题 "Spin eigenmodes of **NdMu2Si₂** and last touch of altermagnetic kinetics" 与附注（RuO₂ MOKE 实验）及正文引用（RuO₂）完全不符；"NdMu2Si₂"非有效化学式，疑为虚构残留（历史评审已确认，未修复） | references L143 |
| 无条目 | 正文引用但文献表缺失：Terashima（arXiv:2601.19105，rationale L33/L73）、Du（arXiv:2609.21303，rationale L33/L73）、Qiu 群论（arXiv:2508.16166，rationale L33）——至少 3 项纯 arXiv 文本引用未列条目，references L3 纯文本策略声明只涵盖 Schüle/Weber 两条 | rationale |

### 4.3 术语一致性

| 术语 | 状态 |
|---|---|
| altermagnet 中文译名 | ⚠️ "交变磁"（rationale L31，Cheng 工作处）vs "交错磁"（rationale L17/L29、scheme L43）混用；英文 altermagnet 三章统一（42/6/25 次）主导，中文两译名需统一 |
| SBE 缩写 | ⚠️ 展开式"半导体布洛赫方程（SBE）"仅在 scheme L7；装订顺序上 SBE 首次出现于 content L13"多带 SBE 正演模型"，未展开 |
| κ 符号 | ✅ 三章 Unicode 统一（5/12/14 处），上轮 LaTeX 残留已清零 |
| 序参量读出层级 | ✅ "敏感性≠直接度量"限定在三章 + full_review 四处口径一致 |

### 4.4 逻辑衔接与冗余

- R1→R2→R3 递进链 + 年度硬规则（"上一年终止判据未通过不进入下一年"）在 content §2.1/§2.6 与 scheme §1/§7 一致 ✅
- ❌ 年度计划双写：content §2.6 完整版（11 行，四年度+判据）与 scheme §7 L97 压缩版重复展开同一内容（1%/SNR/κ/XRD 判据两处各述一遍）
- ❌ full_review.md 与正文现状脱节（详见 H8）：其 §7 自称"content.md 未给出逐年度时间节点表"，与 content §2.6 直接矛盾；其引用的"截至 2026 年 7 月…"检索限定句在当前 rationale 中已被改写为"截至 2026 年 8 月…"（L11/L47）；其称 references 48 条（实际 44）、content 三小节（实际六小节）

---

## 5. 历史遗留问题核对（逐条，基于当前文本实际判断）

| 历史问题（首见于 R7 方案深审） | 当前状态 |
|---|---|
| [critical] §4 可行性分析大段复述方案技术细节 | **部分解决**：装置参数复述（Rost/Mandal 句的技术指标展开）已压缩为先例论证；但"反演可行性"句仍逐字复述 §2 L27 参数空间定义 → 降级 [high] H5 |
| [critical] §4 复述"Rost…材料特异指纹 + Mandal [36]…" | **部分解决**（同上，Rost/Mandal 仍在 §4 但已一句话先例化） |
| [high] §3 L45—L51 Sankar 225 字超长句 | **已解决**：原句已拆分；但拆分产物 L39（130 字）+ L43（131 字）两新超长句 → 计入 H1 |
| [high] §1 L19 三重阈值 197 字超长句 | **已解决**：拆为多句，每句 <120 字 |
| content.md LaTeX $\kappa$ 残留（跨章红线） | **已解决**：三章 Unicode κ 统一，LaTeX 0 处 |
| §6 创新点（二）193 字超长句 | **未解决**：现为 scheme L81，191 字 |
| 跨章 Sankar 引用方式不统一 | **未解决并扩大**：确认 Fuchs/McCarter/Horstmann 同样双轨（H3） |

---

## 6. 问题清单

### [critical] citation_mismatch — scheme §2 L19 SBE 方法学三角引用三连错位
- 位置：scheme.md L19（§2 理论方法，适用条件段）
- 问题："Wang 等人实验观测到…功率标度转变 **[59]**"（应 [60]）；"Zhang 等人在 CsPbBr₃…观测到 Keldysh 交叉 **[60]**"（应 [61]）；"Uzner 与 Neufeld 阐明层间耦合 **[61]**"（[61] 被双重占用）。同文件 L63 同三文献引用全部正确，证明 L19 为错位残留。违反 section_standards.references"无张冠李戴"+ full_review 标准"正文有[N]角标对应"。
- 建议：L19 三处编号改为 [60]/[61]/（Uzner 句单独处理，见 C2）；全局 grep "Wang 等人.*\[59\]" 复核。
- action：rewrite；P1

### [critical] ghost_reference — Uzner & Neufeld 幽灵文献
- 位置：scheme.md L19 末句
- 问题："Uzner 与 Neufeld 阐明层状固体中层间耦合对 HHG 谱的调控效应 [61]"——references.md 44 条无此作者条目，无纯文本引用策略声明；如系真实文献须补条目并另配编号，如系生成残留须删句（层间耦合论点可由 [12] TiSe₂ 拟合与正演模型自评估承担）。
- action：verify 后 add/remove；P1

### [high] anti_ai — 程序化检测双超标：18 处超长句 + 27 处冗余修饰
- 位置：全文；超长句重灾区 rationale L11/L31×3/L33、scheme L7/L19/L39/L43/L63/L81
- 问题：>120 字句 18 处（扣 0.36），冗余修饰 27 次（阈值 12，扣 0.15）；"有效"×11（scheme 独占集中）与范本数据驱动风格冲突。违反 anti_ai_patterns"超长句：单句>120 字 [high]"与"冗余修饰堆砌"。
- 建议：每句拆为 ≤2 个 60 字级分句；"有效约束/有效验证"保留判据定义处（如"后验标准差 < 先验宽度 50% 方视为参数被有效约束"），删除修饰性用法；优先拆 scheme L81（191 字创新点收束句）与 rationale L33（172 字 Qiu 句）。
- action：rewrite；P1

### [high] narrative — rationale §2 L33 文献堆砌段
- 位置：rationale.md L33（现状段"后续工作进一步…"）
- 问题：单段连续 8 个"某人等人"句（McCarter/Horstmann/Qiu/Sankar/Ren/Terashima/Du/Singh），典型"A做了X B做了Y"平行罗列，违反 writing_style_rules.forbidden[0]；虽有主题句与 L35 收束句，中段仍为堆砌。
- 建议：按功能重组为 2-3 组——"信号机制理论补充（McCarter/Horstmann/Qiu）→ 材料可行性锚点（Sankar/Ren/Terashima/Du/Singh）"，每组以论证句带出文献，删去与主线无关者（如 Singh 磁子、Du 拓扑可压缩为一句"另有量子振荡与磁输运工作确认 CrSb 自旋分裂费米面与拓扑特性"）。
- action：rewrite；P1

### [high] cross_reference — 跨章引用策略分裂（Fuchs/Sankar/McCarter/Horstmann 双轨）
- 位置：rationale L31/L33 vs content L25/L59 vs scheme L39/L43/L63；references L3
- 问题：同一文献在 rationale 用纯 arXiv 文本、在 content/scheme 用 [N] 编号（或相反）；references L3 只为 Schüle/Weber 两条声明纯文本豁免。违反 full_review 标准"术语全文统一"（引用方式属表达口径）。
- 建议：确立单一规则——凡入表文献一律 [N] 编号，纯 arXiv 文本仅限 Schüle/Weber 两条声明豁免；据此将 rationale 的 Fuchs→[64]、McCarter→[65]、Horstmann→[66] 补编号，scheme 的 Sankar 补 [56]；或反向全部纯文本并更新 references 声明。
- action：rewrite；P1

### [high] reference_missing — 正文引用文献未列入参考文献表
- 位置：rationale L33（Terashima、Du、Qiu arXiv:2508.16166）、L73（Terashima、Du）
- 问题：5 处纯 arXiv 文本引用在 44 条表中无条目、无策略声明。违反 section_standards.references"正文有[N]角标与参考文献对应"的双向一致性。
- 建议：Terashima/Du/Qiu 群论三条补入 §4 组（可用预留空号 [32]—[34]），或在 references L3 声明中显式扩列纯文本豁免清单。
- action：add；P1

### [high] boundary — scheme §4"反演可行性"句复述 §2 参数空间定义（残留降级）
- 位置：scheme.md L63（§4 可行性分析，反演可行性句）
- 问题：与 §2 L27 参数空间表述几乎逐字重合（"7—9 维/三重维度/多点采样/满秩可计算条件数"），违反 content_boundaries"可行性不复述研究方案做法"；上轮 [critical] 的装置技术参数复述已删，故降级。
- 建议：该句改写为"方案→原理→结论"链："反演可行性已由同行推进到可检验层面（Cochran [62] 给出唯一性条件、Sørensen [63] 证明多解结构），本项目反演框架的每一判据均有解析对应物，无须依赖未经验证的拟合假设。"删除参数空间复述。
- action：rewrite；P1

### [high] consistency — [68] Weber 条目标题与内容不符（残留确认）
- 位置：references.md L143
- 问题：标题 "Spin eigenmodes of NdMu2Si₂ and last touch of altermagnetic kinetics" 与附注/正文引用的 RuO₂ MOKE 内容无关，"NdMu2Si₂"非有效化学式，系上轮已确认的虚构残留，未修复。违反 section_standards.references"无张冠李戴（作者、期刊、年份与实际一致）"。
- 建议：按 arXiv:2408.05187 真实标题重写条目（正式发表信息以 Phys. Rev. X 16, 021051 对应论文为准），正文 rationale L31 引用文字不变。
- action：verify+rewrite；P1

### [high] consistency — CrSb 损伤阈值三处口径矛盾
- 位置：scheme.md L39 vs references.md L109
- 问题：scheme L39 章内自相矛盾（"上限 0.8 V/Å 来自损伤阈值标定"→后又"强场损伤阈值将在项目启动后第 1 年内正式标定"）；references L109 称"以本项目前期预研测量结果（约 0.8 V/Å）为依据"。0.8 V/Å 究竟是已有预研数据还是待标定未知量，三处三种口径。违反 indicator_red_lines.consistency_check（P0 红线）。
- 建议：统一为一种叙事——若确有前期预研，scheme L39 改"0.8 V/Å 取自前期预研的反射率损伤阈值（±5% 判据），项目第 1 年内将完成正式标定以细化"；若预研仅为估计，references L109 删除"前期预研测量结果"表述，改"工程估计值"。
- action：rewrite；P1

### [high] outdated_review — full_review.md 整体一致性结论基于过时快照
- 位置：full_review.md L41/L51/L55/L63
- 问题：①L63 称"content.md…未给出逐年度的时间节点表"，实际 content §2.6 已有完整四年度计划（直接矛盾）；②L41 引用的"截至 2026 年 7 月…尚未发现…系统实验报道"限定句在当前 rationale 已改写为 2026 年 8 月版（L11/L47），证据引用失效；③L55 称 references 48 条（实际 44）；④L51 称 content 三小节（实际六小节）。整体一致性审查文件自身与正文不一致，构成"审查者失审"。
- 建议：full_review.md 按当前文件状态重写 §6/§7（模块现状、残留风险），所有正文引文改为现版本行号；或在文首标注"基于 08-19 快照，待重审"。
- action：rewrite；P1

### [medium] reference_count — §8 "正文直接引用 41 条"计数失实
- 位置：references.md L163/L171
- 问题：[55] Jita 正文零 [N] 引用（脚本验证），却未像 [70]-[72] 那样列入组内描述豁免；41 条口径实际为 ≤40。
- 建议：将 [55] 并入 §8 豁免清单（"[55] 为组内描述引用"）并把计数改为 40，或为 Jita 在正文补一处 [N] 引用（如 rationale L29 候选信号段）。
- action：recalculate；P2

### [medium] position_stale — §6/§8 引用位置行号与方式双重过时
- 位置：references.md L135-L139/L165
- 问题：[64]/[65]/[66]/[58b] 标注的 rationale 行号（31/35）与引用方式（"[N] 编号引用"）均与当前纯文本状态不符；content 行号 23 实为 25。
- 建议：重新生成"编号→文件→行号→方式"四列核查表，与 [56] 双轨修复（H3）联动更新。
- action：verify；P2

### [medium] terminology — 中文译名与缩写展开不统一
- 位置：rationale L31（"交变磁"）vs L17/L29/scheme L43（"交错磁"）；content L13 SBE 首现未展开
- 建议：全文统一"交错磁"（或全用英文 altermagnet）；SBE 展开式提前至 content L13 首次出现处。
- action：rewrite；P2

### [medium] duplication — 年度计划双写与预期成果归属
- 位置：content §2.6 vs scheme §7 L97
- 问题：同一四年度计划两处展开（判据各述一遍），跨章冗余；预期成果仅存 scheme，与模板归属（研究内容）不符（full_review L63 已自认）。
- 建议：content §2.6 保留完整版（含判据），scheme §7 压缩为一句"年度安排详见（二）§2.6，第四年完成独立交叉验证与成果整理"；最终组装时将预期成果移入（二）。
- action：rewrite；P2

### [medium] physics_precision — TiSe₂ 相变表述简化为纯 CDW
- 位置：rationale L27、content §2.2、scheme L47（"CDW 相变 205 K/CDW 相"）
- 问题：所引 [11] Tyulnev 与 [13] Dziurawiec 原文标题均为 "Mott-to-charge-density-wave phase transition"，TiSe₂ 的 205 K 转变含 Mott（激子绝缘体）分量；申请书通篇简化为纯 CDW 相变，复现判据的物理表述不完整，评审专家核对 [11] 标题即见偏差。
- 建议：在 TiSe₂ 首次出现处加一句限定："TiSe₂ 在 205 K 发生 Mott-CDW 联合转变 [11][13]，本项目的复现对象限定为其 CDW 分量引起的 C₄ 对称性变化"。
- action：rewrite；P2

### [medium] consistency — 驱动光-带隙匹配口径两版
- 位置：rationale L73"落在带间共振附近" vs scheme L19/L37/L39"与带隙量级相当"
- 问题：0.25—0.41 eV 相对 0.6 eV 直接带隙为亚带隙、相对 0.13 eV 间接带隙为超带隙，"带间共振附近"不成立；两版表述并存且口径不一。
- 建议：统一为 scheme 版"与带隙量级相当，有利于…"，rationale L73 删"共振"。
- action：rewrite；P2

### [medium] preprint_ratio — 预印本占比 52%，核心锚点全部为预印本
- 位置：references.md §8（23/44 条预印本）
- 问题：核心方法学锚点 [62] Cochran、[63] Sørensen、主体系首批实验 [67] Rost、装置基线 [36] Mandal 均为预印本；若任一被推翻或重大修订，判据链受连带影响。超物理领域专项 30% 警戒线。
- 建议：§8 已显式标注证据等级（合规）；补充一段"预印本依赖风险与对冲"——说明 [62][63] 结论互为正反面、[67] 与 [58b]/[56] 互为独立佐证，单一预印本失效不颠覆判据链。
- action：add；P2

### [medium] section_ownership — §8 引用位置清单只覆盖 rationale
- 位置：references.md L165
- 问题：自称"跨章引用一致性核查"，具体位置仅列 rationale 行号，content/scheme 的 [N] 位置（如 [59] content L39、[36] scheme L41/L63、[67] scheme L43/L63）全部缺失。
- 建议：扩为三文件全覆盖清单（与 H3 修复联动）。
- action：add；P2

### [low] style — 零散表达
- 位置：rationale L11（150 字检索句可压缩至 80 字内）；scheme L43"（见立项依据 §4 与研究内容 §2）"与 content 内"见 §2"交叉引用格式不统一
- action：rewrite；P3

---

## 7. 对抗结论

- 本轮发现 21 个问题（critical:2, high:9, medium:8, low:1+并入项），其中程序化 AI 模式 2 项按强制约束列为 [high]
- 相比上一轮（方案深审，综合 0.71/变权重口径）：**改善 6 个**（κ LaTeX 残留、§1 L19 三重阈值 197 字句、§3 Sankar 225 字句、§5 难点二/难点四超长句、§4 boundary 由 critical 降 high、死板关联词与加粗保持清零）；**新增 8 个**（引用三连错位、Uzner 幽灵、跨章引用双轨扩大、Terashima/Du 无条目、损伤阈值口径矛盾、full_review 失审、[55] 计数、TiSe₂ Mott 分量）；**未解决 2 个**（创新点二 191 字句、Sankar 引用方式）
- 是否达到输出标准：**否**——综合 0.69 < general 阈值 0.85；max_high_issues=0 未满足（high 及以上 11 个）
- 核心判断：三章的**参数口径一致性已达高水位**（13 项指标零冲突，可辨识性判据链闭合），科学问题与递进结构经受住了整体审查；当前的系统性短板已从"物理论证"转移到"引用治理"——编号错位、幽灵条目、双轨引用方式、审查文件失审，均属 P1 可机械修复项。修复完这批后，表达质量（超长句拆分）是通往 0.85 的最后主障碍。
- 返工优先级：P0 = C1/C2（引用错位+幽灵，一次 rewrite 可清）→ P1 = H3/H4/H6/H7（引用治理+口径统一）→ P1 = H1/H2（超长句拆分+L33 重组）→ P2 = 其余
- 下一轮建议聚焦：references.md 专项复查（引用治理修复验证 + [68] 标题核实），配合 nsfc-references-audit 工作流

---

## 评分

创新性：0.84
可行性：0.78
严谨性：0.68
表达质量：0.47
综合评分：0.69

（档位依据：创新 0.80-0.89"明确创新点、与前人清晰区隔"——可辨识性范式与四档判据成立；可行 0.70-0.79"基本可行但存在风险点，部分关键技术缺少预研验证"——损伤阈值口径矛盾+核心锚点全预印本+无预研章节；严谨 0.60-0.69"论证有明显缺陷，存在事实错误"——引用错位/幽灵/标题失实三处事实错误，参数口径虽一致不足以拉回；表达受程序化天花板 0.50 强制，检测 penalty 合计 0.51，结构连贯故取 0.47。综合=四维等权平均 0.69，与锚点结论"基本接近"上限兼容。）
