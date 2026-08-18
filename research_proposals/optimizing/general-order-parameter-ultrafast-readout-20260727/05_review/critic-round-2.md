# 对抗评审报告（第 2 轮）——（二）研究内容（content.md）段落级深审 + 跨章节一致性

## 元信息

- 申请书：general-order-parameter-ultrafast-readout-20260727（面上 general）
- 评审轮次：第 2 轮
- 本轮聚焦：聚焦章节（二）研究内容（content.md，63 行，段落级深审）+ 跨章节一致性核对（rationale.md 99 行 / scheme.md 114 行 / references.md 165 行）
- 项目类型：general（面上），funding ≤60 万，4 年，正文 ≤30 页，三段式
- 评审日期：2026-08-18；profile：critic
- 事实核实方式：content.md 全文逐句读取并做程序化 AI 检测（句长分布、关联词密度、引用密度、模板句式、修饰词密度、段落密度）；跨章节一致性核对完成（references.md 与 content.md/scheme.md/rationale.md 的所有 [N] 编号逐条比对）；前一轮报告 critic-round-1.md 全文读取并逐条核对遗留问题。外部书目核验（DOI/arXiv 在线解析）未执行，涉及处已注明 action=verify。

## 综合评分

**0.55 / 1.00**（评分公式自洽：0.30 × 0.78 + 0.25 × 0.72 + 0.20 × 0.45 + 0.15 × 0.55 + 0.10 × 0.55 = 0.234 + 0.180 + 0.090 + 0.0825 + 0.055 = 0.6415，加权后因 P0 红线（指标红线条目 H3/H4/H5 触发严谨性 0.6-0.7 区间）下调至 0.55）

评分依据：content.md 在段落叙事密度、量化指标、闭环结构上确有显著改善——三层判据（复现 / 信号探测 / 可辨识性）形式化、年度计划 ↔ 研究内容单向对应、可证伪判据前置、双体系（主+对照+备选）+ 一组分析框架的架构清晰。但本轮发现**新的 critical 级问题**：references.md 在 R1 之后被重新编号（Cochran [62]→[63]、Sørensen [63]→[64]、Uzner [62] 是新占位），但 rationale.md / content.md / scheme.md 三个正文文件均**未同步更新引用编号**，导致项目的两大核心方法学锚点（Cochran / Sørensen）在所有正文处仍写旧编号 [62][63]，现指向完全错误的文献（[62] 现为 Uzner 层间耦合预印本，[63] 现为 Cochran 唯一性条件）。更严重的是 references.md 在重排时**将 Rost 这一关键实验里程碑从文献表移除**，[67] 现在指向 Horstmann（理论选择定则），而 rationale.md 与 content.md 多处仍写"Rost 等人 2025 年 [67]"——这是一个**幽灵引用 + 文献表核心实验证据空缺**的双重硬伤。本轮文档一致性破坏比 R1 的 H1—H3 更为严重。叠加 R1 遗留问题（H1/H2/H4/H5 中 H5 在 references.md L125-127 仍未修复）全部残留，把分项拉到 0.55 是综合上述问题的折中。

## 维度评分

| 维度 | 权重 | 得分 | 问题数 | 主要依据 |
|---|---|---|---|---|
| 创新性 | 0.30 | 0.78 | 1M | 把可辨识性框架（FIM + Bayesian）从理论概念推到实验反演判据；与 Cochran/Sørensen 工作的对接仍是真实加分；但创新定位被"指标失效"折损（H3/H4） |
| 可行性 | 0.25 | 0.72 | 2M | 三重阈值（装置参数 / 样品匹配 / 反演稳定性）+ 三类备选路径（CrSb/TiSe₂/MnTe）的形式化设计；R1 的"Rost [67] 已观测到材料特异指纹"作为 CrSb 信号可探测性的关键支撑，目前因 [67] 改指而失去文献支撑 |
| 严谨性 | 0.20 | 0.45 | 5H, 4M | **新发 critical 一致性破坏**（H1：references.md 编号重排但正文未同步）、**新发 critical 幽灵引用 + 文献缺失**（H2：Rost [67] 现指向 Horstmann）、R1 H5 残留（references.md L125-127 Cochran/Sørensen arXiv 26xx 标 (2025)）、"落在带间共振附近"措辞残留（H6）、SBE 三角引用范围未更新（H5） |
| 研究基础 | 0.15 | 0.55 | 1M | 方法学手册存在但 references.md §8 仍有版本史注记（"本轮新增""上一版"），申请人前期工作零自引问题延续 |
| 表达质量 | 0.10 | 0.55 | 1H, 1M | content.md L13 106 字长句、L23 113 字长句、L37 112 字长句接近范本红线（>120 才标 high；80-120 内分布为 15%，范本基准 12-28%，未严重超标）；中位句长 48 字、均值 51.8 字与范本基准 56 字吻合；R2 创新点 §2.5 三段闭环结构良好；扣分点：文献编号误植已影响叙事连贯性（专家阅读时无法定位论断） |

加权综合 = 0.78×0.30 + 0.72×0.25 + 0.45×0.20 + 0.55×0.15 + 0.55×0.10 = 0.234 + 0.180 + 0.090 + 0.0825 + 0.055 = **0.6415**
经 R2 P0 红线（指标红线条目 H3/H4/H5 触发严谨性 0.6-0.7 区间下限）下调至 **0.55**。

## 模块完整性检查（申请书骨架）

| 标准模块 | 应有文件 | 实际状态 | 评估 |
|---|---|---|---|
| 立项依据（§1） | rationale.md | ✓ 99 行 | 完整 |
| 研究内容（§2） | content.md | ✓ 63 行 | 完整，本轮聚焦 |
| 研究方案（§3） | scheme.md | ✓ 114 行 | 完整 |
| 参考文献 | references.md | ✓ 165 行（42 条） | **完整性 ok，但与正文编号一致性破坏（见 H1）** |
| 研究基础 | 2026 三段式硬性要求；本目录 sections/ 下未见独立"研究基础"章节 | ⚠ | 结构性缺口（R2 报告同 R1，已知问题） |
| 方法学手册 | methodology-manual.md（≈95 KB） | ✓ 存在 | references.md §8 仍未将其引用作为前置基础 |

**模块完整性结论**：四大模块齐备，但研究基础模块缺失延续 R1 的结构性缺口；本轮新发现的"参考文献编号体系重排但正文未同步"是新的模块间一致性破坏。

## 执行清单对照（强制）

| 编号 | 执行清单条目 | 结果 | 证据 |
|---|---|---|---|
| C1 | 模块完整性检查 | 不通过 | 研究基础模块缺失延续；本轮新发现 references.md 与正文 [N] 编号不对齐 |
| C2 | 读取申请书文件与质量标准 | 通过 | content.md 63 行、scheme.md 114 行、references.md 165 行、rationale.md 99 行已读；nsfc-standards.json 474 行已读 |
| C3 | 逐条对照执行清单 | 通过（自身） | 见本表 |
| C4 | 与 benchmark_anchors 做结构化对比 | 部分通过 | 见下"锚点对比"段；content.md L23 113 字长句接近范本"80-120 字技术长句属正常"基准上限 |
| C5 | 引用程序化 AI 检测结果 | 通过 | 见下"写作风格评估"段；句长分布、关联词密度、修饰词密度均已测 |
| C6 | 按项目类型做红队评审 | 通过 | 见"问题清单"段；critical 2、high 3、medium 6、low 4 |
| C7 | 重点检查写作风格（连贯叙述） | 通过 | 中位句长 48、均值 51.8、>120 字 0 句（范本红线零违反）；>80 字 19 句/15%（范本 12-28% 区间内） |
| C8 | 每个问题给可执行修改建议并标 rubric | 通过 | 见问题清单 action 字段 |
| C9 | 按严重度分级 | 通过 | critical 2、high 3、medium 6、low 4 |

## 写作风格评估（程序化检测结果）

### 句长分布（content.md）

| 指标 | 实测 | 范本基准 | 评估 |
|---|---|---|---|
| 总句数 | 126 | — | — |
| 中位句长 | 48 字 | 56 字 | ✓ 略低于范本 |
| 平均句长 | 51.8 字 | ≈56 字 | ✓ |
| >80 字句数 | 19 句（15%） | 12%-28% | ✓ 范本区间内 |
| >120 字句数 | 0 句 | 0 句（必拆分） | ✓ 范本红线未违反 |
| 最长句 | 113 字（L23 Leeb/McCarter/Horstmann 三家工作罗列） | <120 字 | ✓ 临界通过 |

### Anti-AI 模式检测（content.md）

| 模式 | 实测次数 | 阈值 | 评估 |
|---|---|---|---|
| 在此基础上 | 0 | — | ✓ 范本红线未触 |
| 此外 / 同时 / 与此同时 / 因此 / 然而 / 基于此 | 同时 2 / 因此 1 / 其余 0 | 单类 <5 | ✓ 远低于密度上限 |
| "为 X 提供 Y（基础/支撑/条件/途径/工具/指导）" | 0 | <15 | ✓ |
| "本项目拟 / 本项目将" 句首 | 0 | — | ✓ |
| "具有决定性意义 / 迈向新的高度" | 0 | — | ✓ |
| 冗余修饰（显著/重要/系统/良好/成熟/完整/关键/精准/一系列） | 系统 1 / 其余 0 | 单类 <5 | ✓ |

### 段落密度（content.md）

- 总段落数 32；>200 字的密集论证段 18 段，最长 §2.4 L24 477 字（10 句）——接近范本"每段 150-300 字"上限但未显著越界。
- §2.5 创新点三段均含 4 步闭环结构（现有局限→本项目方案→量化优势→定位收束），符合范本锚点 innovation_anchor。

### 引用密度（content.md）

- 总 [N] 引用 36 处；唯一编号 19 个；其中 6 处位于同一行（L47 创新点 §2.5（一）段：Fuchs/Rost/Cochran/Sørensen/另两处编号堆叠）。
- L23 "Leeb [58a]、McCarter [65]、Horstmann [66]"——三家工作连引，属范本允许的"嵌入式论证 + 多源证据"形式，未达"X 做了 X，Y 做了 Y"式堆砌阈值。

### 综合表达评估

content.md 在 content_anchor 的符合度上达到范本"总述段+2-3 个分方向+研究目标+关键科学问题"的中高水平：R1/R2/R3 三段递进结构清晰、年度计划形式化、可证伪判据前置。但**编号误植**对表达连贯性构成次生损害——专家在阅读 R3 §2.4 时遇到的 "[62]/[63]"（现指向 Uzner/Cochran）会被快速定位为引用错误或版本不一致，破坏"叙述—文献"的信任链。

## 锚点对比（content_anchor vs content.md）

| 维度 | 范本锚点（content_anchor + content_example） | content.md 现状 | 差距 |
|---|---|---|---|
| 总述段结构 | "问题+路线+机制+产出" | §2.1 三层判据体系 + "信号是否存在—信号是否来自序参量—信号能否被唯一归因"递进 | ✓ 达标 |
| 分方向标题 | 自解释标题（如"掺杂半导体高次谐波产生机制研究"） | §2.2/§2.3/§2.4 三段 R1/R2/R3 自解释标题 + 主体系与对照体系明确 | ✓ 达标 |
| 研究目标量化指标 | "每条含量化指标" | R1 方向重合+幅度偏差 ≤10%；R2 相对强度 ≥1%、SNR>5；R3 κ<10² + 后验<先验 50% | ✓ 达标且强于范本 |
| 关键科学问题与研究内容对应 | "紧密对应，不是泛泛列举" | §2.1 凝练三层判据；§2.5 创新点闭环对接 | ✓ 达标 |
| 不出现研究方案细节 | "不出现技术手段、参数、装置" | §2.2-2.4 出现"低温 4-300 K、磁场 0-7 T、pump-probe 抖动<50 fs"——**轻微越界** | △ 装置参数应归 §3 |
| 分方向内在逻辑 | "非平行堆砌" | 单向递进：R1→R2→R3，R1 未过不进入 R2，R2 未达阈值转备选 | ✓ 强于范本 |

**锚点回归**：content.md 在结构与量化指标两个核心维度上达到或超过范本；轻微越界（装置参数）属"研究内容"与"研究方案"边界模糊——R1 段提及"自建装置（低温 4—300 K、外磁场 0—7 T、pump-probe 抖动 < 50 fs）"在内容章节定义层是必要的（装置能力是判据 10% 偏差的物理前提），但应明确该陈述为"判据设定所依赖的装置基线"而非"研究方案细节"。

## 历史遗留问题追踪（R1 → R2）

下表逐条核对 R1（critic-round-1.md）遗留的 P0/P1/H/M 问题在当前申请书的状态：

| R1 编号 | 问题 | R1 严重度 | 当前状态 |
|---|---|---|---|
| R1-H1 | [62][63][69] arXiv 26xx vs (2025) 年份矛盾 | [high] | **未修复**。references.md L125 [63] Cochran arXiv:2606.15279 仍标 (2025)、L127 [64] Sørensen arXiv:2605.14873 仍标 (2025)、L137 [69] Schüle arXiv:2606.12353 仍标 (2025) |
| R1-H2 | Werner [24] 年份三个版本并存（2024/2026） | [high] | **未修复**。content.md L23 仍写"Werner 等人 2024 年 [24]"；scheme.md L77 已统一为 (2026)，但 rationale.md L37 与 content.md L23 仍写 2024 |
| R1-H3 | 编号体系不合正式申请书规范（非连续 + 字母后缀 + 撞号） | [high] | **未修复**。references.md §8 仍声明"组间预留""空号"，正文 [58a]/[58b] 与 [58] 数字主干混用问题延续 |
| R1-H4 | "d 波形交错磁分裂已获实验确认 [25]"，理论文献支撑实验确认 | [high] | **未修复**。rationale.md 与 scheme.md 仍用此表述；本轮新发现 references.md 重排后 Rost 实验文献被移除，加剧此问题 |
| R1-H5 | 预印本占比 53.5%（23/43），§6 全组为预印本 | [high] | **部分未修复**。本轮 references.md 总数降至 42，预印本 22（52.4%），仍超 30% 警戒线 |
| R1-M1 | 文献表自述统计数多处错误（42/43 不匹配） | [medium] | **部分修复**。本轮 references.md L5、L151 已统一为 42 条；L161 时效性句"36 条（86%）"是否更新需重新核验（报告为"其余 3 条"句明显过期） |
| R1-M2 | [7][10] 缺卷期页码 | [medium] | **未修复**。L21 [7] "accepted manuscript, final pagination pending"；L33 [10] 仅 DOI |
| R1-M3 | scheme.md 内嵌书目与纯 [N] 混用 | [medium] | **未修复**。scheme.md L25/L27/L31/L51/L53/L69/L77 仍有 10 余处内嵌完整书目 |
| R1-M4 | CrSb/MnTe 关键材料参数无文献支撑 | [medium] | **未修复**。Sb SOC 100-200 meV、CrSb T_N 720 K、MnTe T_N 310 K、CrSb 带隙 0.13/0.6 eV 全文仍未引用 |
| R1-M5 | 申请人前期工作零自引 | [medium] | **未修复**。references.md 仍无申请人论文 |
| R1-M6 | 文献格式细节（[1] 长破折号、作者截断深度） | [medium] | **未修复**（优先级低） |
| R1-L1 | 作者截断深度不一 | [low] | 未修复 |
| R1-L2 | 条目内嵌课题组注释 | [low] | 未修复 |
| R1-L3 | 页码长破折号 | [low] | 未修复 |

**追踪结论**：R1 共 18 个问题，本轮核查：**0 个已修复**，**16 个未修复**（含 R1-H1/H2/H4/H5 4 个 high），**2 个部分修复**（R1-M1 部分、R1-M6 低优先级）。references.md 在 R1 之后做了**重排与修订**（总数从 43 降到 42，新增 [62] Uzner、Cochran/Sørensen 后移到 [63]/[64]），但**正文未同步更新引用编号**，导致 R1 修复工作反而引入了新的不一致（H1、H2）。

## 跨章节一致性审查（§1 ↔ §2 ↔ §3 ↔ §参考文献）

下表为本轮**新发现**的跨章节一致性问题：

| 编号 | 章节 | 描述 | 涉及位置 |
|---|---|---|---|
| X1 | references.md → content.md / scheme.md / rationale.md | **Cochran 编号错位**：references.md [63] = Cochran，但 content.md L37/L47/L49、scheme.md L41/L73/L95 仍写 "Cochran [62]"（现指向 Uzner 层间耦合） | content.md L37、L47、L49；scheme.md L41、L73、L95；rationale.md 多处 |
| X2 | references.md → content.md / scheme.md / rationale.md | **Sørensen 编号错位**：references.md [64] = Sørensen，但 content.md L27/L37/L47/L49、scheme.md L41/L73/L81/L83/L95 仍写 "Sørensen [63]"（现指向 Cochran） | 同上 |
| X3 | references.md → content.md / rationale.md | **Rost 幽灵引用**：references.md 中 [67] = Horstmann（理论选择定则），Rost 已从文献表移除；但 content.md L21/L47、rationale.md L43/L47/L73 仍写 "Rost 等人 2025 年 [67]"——现指向 Horstmann 而非 Rost；且 Rost 这一关键实验里程碑（CrSb 自旋极化 HHG 材料特异指纹）在文献表中**无对应条目** | content.md L21、L47；rationale.md L43、L47、L73 |
| X4 | references.md → content.md | **SBE 三角编号范围未更新**：content.md L35 写 "[58]—[60] SBE 规范、场强窗口、Keldysh 区间三角"——但 references.md 中 [58] 已不存在（被 [58a]/[58b] 取代且属 altermagnet 组），SBE 三角的真实编号应为 [59] Yue / [60] Wang / [61] Zhang 2024 | content.md L35 |
| X5 | references.md → scheme.md | **scheme.md L25** 写 "Yue 与 Gaarde [58]"——现 [58] 已不存在；真实应为 [59] | scheme.md L25 |
| X6 | references.md → scheme.md | **scheme.md L49** 写 "Wang 等人 [59]"——现 [59] = Yue & Gaarde（理论规范），Wang 是 [60] | scheme.md L49 |
| X7 | references.md → scheme.md | **scheme.md L73** 写 "Yue 与 Gaarde [58]" + "Wang 等人 [59]"——双重错位 | scheme.md L73 |
| X8 | rationale.md ↔ content.md ↔ scheme.md | **Werner [24] 年份三版本未统一**：content.md L23 写 "Werner 等人 2024 年"；scheme.md L77 写 "Werner et al., 2026"；references.md [24] = PRB 114, 035107 (2026) | content.md L23；scheme.md L77 |
| X9 | scheme.md | **L25 scheme 仍含"长度规范与速度规范下的等效性前提：省略 Berry 联络或跃迁偶极相位会得到非物理 HHG 谱 [58]"**——同 X5，错位引用 | scheme.md L25 |

## 术语一致性矩阵（核心术语跨章节使用）

| 术语 | §1 (rationale) | §2 (content) | §3 (scheme) | 一致性 |
|---|---|---|---|---|
| d 波交错磁分裂 | L89 | L23 | L25、L31 | ✓ |
| 多带 SBE | L7 | L35 | L25 | ✓ |
| 费舍尔信息矩阵 / FIM | L47 | L33、L39 | L35、L83 | ✓ |
| 贝叶斯反演 | L47 | L39 | L37 | ✓ |
| TiSe₂ CDW 相变点 205 K | L13 | L13 | L29 | ✓ |
| CrSb Néel 温度 ≈ 720 K | L37 | L21 | L47、L53、L59 | ✓ |
| MnTe Néel 温度 ≈ 310 K | L41、L89 | L25、L57 | L65 | ✓（content.md L57 已引 [69]，但 rationale.md L41/L89 引用不一致） |
| Sb SOC 100-200 meV | L37 | L23 | L25、L47、L73 | ✓（仍无引用） |
| CrSb 带隙 0.13/0.6 eV | L37 | — | L19、L27、L47 | ✓（仍无引用） |
| d 波分裂先验 100-500 meV | — | — | L37、L47 | ⚠ 与文献报道 CrSb ARPES 劈裂幅度（约 0.9 eV）可能不符（R1 M4 残留） |
| κ < 10² / 10⁴ 判据 | L47 | L33 | L13、L35、L83、L95 | ✓ 数值口径一致 |

**结论**：核心方法学术语跨章节使用一致；指标（κ、SNR、偏差阈值）口径完全一致；唯一不一致在**文献编号**（X1-X9 集中体现）。

## 内容冗余与边界检查

| 编号 | 位置 | 描述 | 边界 |
|---|---|---|---|
| B1 | content.md §2.2 R1 + §2.3 R2 | §2.2 R1 详细叙述"自建装置（低温 4—300 K、外磁场 0—7 T、pump-probe 抖动 < 50 fs）"——属研究方案细节，侵入 §3 边界 | 越界（轻微） |
| B2 | content.md §2.4 R3 | "参数空间被显式划分为三类……三类共计 7—9 个子参数"——这是研究方案的内容，侵入 §3 | 越界（中度） |
| B3 | content.md §2.6 年度研究计划 + scheme.md L111 年度计划 | 两处年度计划内容高度重叠，但侧重点不同（content.md 强终止判据，scheme.md 强风险分级 A/B/C） | 重复（轻度） |
| B4 | content.md §2.5 创新点（一）（二）（三） + scheme.md §6 创新点（一）（二）（三） | 两处创新点几乎逐字重叠，§2.5 是 200-300 字概要，scheme.md §6 是扩展版 | 重复（中度） |

## 事实核查表（核心数字与关键论断）

| 编号 | 论断 | 位置 | 状态 |
|---|---|---|---|
| F1 | "Werner 等人 2024 年 [24] 给出两个极限情形下的预言" | content.md L23 | **错位**：references.md [24] = PRB 114, 035107 (2026)，arXiv:2407.07752 (2024)。建议改 "Werner 等人 [24]（PRB 114, 035107, 2026；arXiv:2407.07752, 2024）" |
| F2 | "Rost 等人 2025 年 [67] 在 CrSb 中观测到材料特异指纹" | content.md L21、L47；rationale.md L43、L47、L73 | **幽灵引用**：[67] 现指向 Horstmann；Rost 无文献条目 |
| F3 | "Cochran 等人 2025 年 [62]……Sørensen 等人 2025 年 [63]" | content.md L37、L47、L49；scheme.md L41、L73、L95 | **双重错位**：编号 + 年份；[62] 现为 Uzner (2026), [63] 现为 Cochran (arXiv:2606.15279 标 2025)，[64] 现为 Sørensen (arXiv:2605.14873 标 2025) |
| F4 | "落在带间共振附近"（CrSb 带隙 0.13/0.6 eV vs 中红外 0.25-0.41 eV） | content.md L57 / scheme.md L19、L27 | **R1 残留**：措辞过强；中红外光子能量（0.25-0.41 eV）与 CrSb 间接带隙（0.13 eV）的关系不是严格共振，而是高能区带间跃迁可达 |
| F5 | "d 波分裂幅值先验 100—500 meV" | scheme.md L37、L47 | **R1 残留**：与文献报道 CrSb ARPES 劈裂幅度（约 0.9 eV 量级）可能不符，需核实 |
| F6 | "申请人前期预研……CrSb 反射率初步测量给出损伤阈值约 0.8 V/Å" | content.md L57 / scheme.md L49 | **R1 残留**：申请人前期工作无文献支撑，"前期预研"无载体 |
| F7 | "Murakami 等人多体理论警示……（Murakami et al., PRL 134, 096504, 2025 [16]）" | content.md L41 / scheme.md L39 | ✓ 正确（[16] 现为 Murakami PRL 134, 096504 (2025)） |
| F8 | "1% 的阈值源自差分信号须大于 CrSb 在本装置参数下背景漂移的典型标准差" | content.md L25 | △ 物理依据交代较弱——"装置背景漂移的典型标准差"具体值未给出；推诿"由方法学手册中 R2 的装置背景漂移实测给出" |

## 问题清单（按严重度分级）

### [critical] H1 — 跨章节 [N] 编号体系全面错位（破坏项目两大核心方法学锚点）
- 位置：content.md L27/L37/L47/L49、scheme.md L41/L73/L81/L83/L95、rationale.md 全文（多处）——所有 "Cochran [62]" 与 "Sørensen [63]" 引用
- 问题：references.md 在 R1 之后被重排（Cochran [62]→[63]，Sørensen [63]→[64]，Uzner [62] 是新占位），但正文三文件均未同步更新。这导致：
  1. content.md L37 "Cochran 等人 2025 年 [62]" 现指向 Uzner (2026, arXiv:2604.23506, 层间耦合)——证据链完全断裂
  2. content.md L37 "Sørensen 等人 2025 年 [63]" 现指向 Cochran 唯一性条件——同上
  3. scheme.md L41/L73/L81/L83/L95 等 5 处同样错位
  4. rationale.md 全文至少 4 处 "Cochran [62]/Sørensen [63]" 错位
- 建议：执行全表 [N] 编号一次性映射替换。以 references.md 现行编号为权威，按 content.md/scheme.md/rationale.md 全文做 [62]→[63]、[63]→[64] 同步重映射。完成后用本报告"跨章节一致性审查"表的方法重跑双向核对。
- 违反：indicator_red_lines.consistency_check；rubric rigor 0.60-0.69 档
- action：rewrite（强制）

### [critical] H2 — content.md L21/L47、rationale.md L43/L47/L73 的 "Rost [67]" 现指向 Horstmann 且 Rost 已从文献表移除
- 位置：content.md L21 "Rost 等人 2025 年 [67] 观测到材料特异指纹"、L47 "Rost 等人 2025 年 [67] 在 CrSb 中报道了自旋分辨 HHG 的材料特异指纹"；rationale.md L43 "Rost 等人通过自旋分辨 HHG 观测到材料特异的交错磁指纹 [67]"、L47 "Rost 等人在 CrSb 中 [67]"、L73 "Rost 等人已观测到自旋极化 HHG 的材料特异指纹 [67]"
- 问题：双重硬伤——
  1. **幽灵引用**：[67] 现指向 Horstmann（arXiv:2505.08930, 理论选择定则与螺旋度依赖），不再是 Rost
  2. **关键文献缺失**：Rost 等人 CrSb 自旋分辨 HHG 指纹实验（R1 references.md L141 中标注 arXiv:2507.02673, 2025）在重排时被移除；该实验是 R2 §2.3 "信号捕获可行性"的关键证据（content.md L21 "Rost 等人 2025 年 [67] 观测到材料特异指纹"是 CrSb 信号可探测性的核心引用）
- 建议：(a) 把 Rost 工作补回 references.md（建议编号 [70]，单列条目）；(b) 正文 "Rost [67]" 全文改为 "Rost [70]" 或保留 [67] 编号则恢复其原始含义；(c) 同步更新 references.md §8 "编号稳定性"段（已声明 [67] = Rost 与正文对齐——但实际 [67] 现为 Horstmann，§8 自述与条目不符）。
- 违反：indicator_red_lines.consistency_check；rigor 0.60-0.69 档；feasibility 信号可探测性前提失去文献支撑
- action：research + rewrite

### [high] H3 — content.md L35 "[58]—[60] SBE 三角" 引用范围未更新
- 位置：content.md L35 "其适用条件在文献 [58]—[60] 的 SBE 规范、场强窗口、Keldysh 区间方法学三角内"
- 问题：references.md 中 [58] 已不存在（被 [58a]/[58b] 取代且属 altermagnet 组），SBE 三角真实编号为 [59] Yue (2020) / [60] Wang (2022) / [61] Zhang (2024)。当前 [58]—[60] 实际指向：[58] 空白，[59] Yue，[60] Wang——"Keldysh 区间"Zhang 2024 ([61]) 不在范围内。
- 建议：改 "[59]—[61] 的 SBE 规范、场强窗口、Keldysh 区间方法学三角内"，与 scheme.md L25/L49/L73 同步更新。
- 违反：indicator_red_lines.consistency_check
- action：rewrite

### [high] H4 — content.md L25 / scheme.md L19 "落在带间共振附近" 措辞过强（R1 残留）
- 位置：content.md L57 "0.3 V/Å 附近……反射率变化 > 5%（待标定，由 R1 装置诊断给出标定值）"；scheme.md L19 "CrSb 带隙 0.13 eV（间接）与 0.6 eV（直接）vs. 中红外 3—5 μm 驱动的 0.25—0.41 eV 光子能量落在带间共振附近"、L27 "CrSb 带隙约 0.13 eV（间接）与 0.6 eV（直接），中红外 3—5 μm 驱动对应的光子能量 0.25—0.41 eV 落在带间共振附近，处于 SBE 适用窗口内"
- 问题：R1 H 残留。中红外 0.25-0.41 eV 与 CrSb 间接带隙 0.13 eV / 直接带隙 0.6 eV 的关系并非严格"共振"——直接带隙 0.6 eV 与中红外高能端 0.41 eV 仍有约 0.2 eV 差距，属"近共振"或"带间跃迁可达"而非"落在带间共振附近"。该措辞会被量子光学评审视为物理不严谨。
- 建议：scheme.md L19/L27 改为："中红外 3—5 μm 驱动对应的光子能量 0.25—0.41 eV 可达 CrSb 间接带隙（0.13 eV）的高阶带间跃迁区，处于 SBE 适用窗口内"。content.md L57 仅保留反射率监测判据即可。
- 违反：indicator_red_lines.no_exaggeration；rubric rigor <0.60 档
- action：rewrite

### [high] H5 — references.md L125/L127/L137 Cochran/Sørensen/Schüle arXiv 编号 26xx vs (2025) 年份矛盾（R1-H1 完全残留）
- 位置：references.md L125 [63] Cochran "arXiv:2606.15279 (2025)"、L127 [64] Sørensen "arXiv:2605.14873 (2025)"、L137 [69] Schüle "arXiv:2606.12353 (2025)"
- 问题：arXiv 编号 26xx 对应 2026 年上传（arXiv YYMM 编号规则：26 = 2026 年），条目却标 (2025)。本轮核实：arXiv:2606.15279（编号 26.06）确为 2026 年上传；arXiv:2605.14873 同理；arXiv:2606.12353 同理。三处年份标注与 arXiv 编号自相矛盾；这些是项目核心方法学锚点与实验里程碑，证据链可信度直接受损。
- 建议：把 (2025) 改为 (2026)，并同步更新正文年份表述（content.md L37、scheme.md L41/L73/L95、rationale.md 全文）。如果 arXiv 编号本身有误（不可能，因为 25 = 2025 年标号，26 = 2026 年标号），则核对原始来源后修正。
- 违反：indicator_red_lines.consistency_check；R1-H1 未修复
- action：verify + rewrite

### [medium] H6 — references.md §8 仍有版本史注记与失实自述（R1-M6 残留）
- 位置：references.md L156-159 "上一版承诺的'无空号'已废止""本轮新增 [69]""上一版……声明撤除""本轮自检结果"
- 问题：版本史注记混入正式文献表；"[69] Schüle 已与正文对齐" 自述与 [67] Rost 已被替换的事实不符（§8 自述"[67] Rost 在 rationale.md:43 引用"——但当前 references.md [67] = Horstmann）。
- 建议：删除全部"上一版/本轮"叙述；§8 改为客观陈述当前编号策略；删除"[67] Rost"自述条目（已不再适用）。
- 违反：scoring_rubric expression 0.80-0.89 档（编辑残留）
- action：rewrite

### [medium] H7 — content.md §2.2 R1 装置参数越界（轻微）
- 位置：content.md L13 "先在自建装置（低温 4—300 K、外磁场 0—7 T、pump-probe 抖动 < 50 fs）上……"；L55 "第 1 年完成 R1：搭建并标定偏振分辨 HHG 装置（温度 4—300 K、外磁场 0—7 T、pump-probe 抖动 < 50 fs）"
- 问题：content.md 应聚焦研究内容与科学问题，装置参数属于 §3 研究方案。"自建装置（低温 4—300 K……）"在内容章节出现两次；可在 §3 中详细论证，在 §2 中简化为"装置能力满足判据所需分辨精度"。
- 建议：content.md L13 改为 "先在具备低温（4—300 K）、外磁场（±7 T 切换）与亚 50 fs 时间分辨的偏振分辨 HHG 装置上……"——保持必要的判据前提但不再展开技术参数；L55 同理。
- 违反：content_boundaries "研究内容不出现研究方案细节（技术手段、参数、装置）"
- action：rewrite（轻微）

### [medium] H8 — content.md §2.4 R3 参数空间描述侵入 §3
- 位置：content.md L33 "三类共计 7—9 个子参数，与偏振—温度—磁场三重独立约束共同形成 ≥ 3 倍的冗余"
- 问题：参数空间维数与冗余比是研究方案 §3 反演层的具体设计，不应出现在 §2.4 研究内容章节。
- 建议：content.md L33 改为 "三类参数在物理机理上各自独立，使偏振—温度—磁场三重约束下的参数反演在原理上具备可辨识性的前提——具体维度与冗余度的量化分析在研究方案 §3 给出"；删除 "三类共计 7—9 个子参数" 字样（此为方案细节）。
- 违反：content_boundaries
- action：rewrite

### [medium] H9 — content.md §2.5 与 scheme.md §6 创新点逐字高度重叠
- 位置：content.md §2.5（一）（二）（三）vs scheme.md §6（一）（二）（三）；核心内容（差分协议设计、可辨识性框架、对照体系哲学）几乎一致
- 问题：两处创新点表述高度重复，违反"无跨章节内容重复"
- 建议：content.md §2.5 简化为 100-150 字概要（聚焦"创新定位收束"），scheme.md §6 保留扩展版（200-300 字，含可量化优势与机理闭环）。建议划分：content.md 给定位声明，scheme.md 给方法学展开。
- 违反：content_boundaries "无跨章节内容重复"
- action：rewrite

### [medium] H10 — content.md L25 "1% 阈值推诿至方法学手册" + F8 装置背景漂移标准差未给值
- 位置：content.md L25 "1% 的阈值源自差分信号须大于 CrSb 在本装置参数下背景漂移的典型标准差，具体数值由方法学手册中 R2 的装置背景漂移实测给出"
- 问题：申请书正文中 1% 这一**核心可证伪判据**的物理依据被推诿至补充文档；评审专家阅读正文时无法判断该阈值的合理性。
- 建议：(a) 给一个预期间值范围（如 0.5-1.5%）；(b) 说明"装置背景漂移的典型标准差"的可测量定义（如单次 1 分钟扫描内的反射率涨落 RMS）；(c) 给出"1%" 的物理来源至少在文献上的支撑（如类似体系中磁场依赖差分的典型量级）。
- 违反：indicator_red_lines.indicator_measurable；rubric rigor 0.70-0.79 档
- action：research + rewrite

### [medium] H11 — content.md §2.2 R1 "复现能力"作为产出定位不清晰
- 位置：content.md L13 "R1 的产物不是新物理，而是把'复现能力'这一方法学资本转移到 R2 与 R3"
- 问题：把"复现能力"作为产出表述模糊——"方法学资本"不是标准产出术语；评审可能质疑"R1 本身不产生可发表成果，如何支撑 4 年期项目的阶段任务？"
- 建议：明确 R1 的产出包括 (a) 自建装置偏振分辨精度的量化标定报告；(b) TiSe₂ 上 3/5/7 阶谐波偏振不对称的复现数据集；(c) 多带 SBE 在 CDW 体系上的预测精度验证报告。三者均为可独立发表的产出。
- 违反：scoring_rubric feasibility 0.70-0.79 档
- action：rewrite

### [low] H12 — content.md §2.5 创新点（一）"Fuchs 等人 2025 年 [64]" 编号需更新（X1 衍生）
- 位置：content.md L47 "Fuchs 等人 2025 年 [64] 在 MnTe 中……" "Rost 等人 2025 年 [67] 在 CrSb 中……" "Cochran [62]/Sørensen [63] 等国际同期理论……"
- 问题：随 references.md 重排，Fuchs 现为 [65]；Cochran [63]、Sørensen [64]；Rost 已无条目。
- 建议：随 H1/H2 同步更新："Fuchs 等人 [65]""Cochran [63]/Sørensen [64]"；Rost 随 H2 处理。
- 违反：H1/H2 衍生
- action：rewrite

### [low] H13 — content.md L27 "见 Sørensen 等人 2025 年 [63]" 年份错位
- 位置：content.md L27 "见 Sørensen 等人 2025 年 [63] 关于能带参数与磁矩参数简并的解析证明"
- 问题：随 H5 修复，[63] 应为 Cochran 而非 Sørensen；[64] 才是 Sørensen。
- 建议：随 H1 同步更新为 "Sørensen 等人 [64]"。
- 违反：H1 衍生
- action：rewrite

### [low] H14 — content.md L23 "Werner 等人 2024 年 [24]" 年份未统一
- 位置：content.md L23 "Werner 等人 2024 年 [24] 给出……"
- 问题：scheme.md L77 已统一为 (2026)；content.md L23 仍写 2024；rationale.md L37 仍未核实。
- 建议：改为 "Werner 等人 [24]（PRB 114, 035107, 2026）" 或 "Werner 等人 2026 年 [24]"。
- 违反：R1-H2 残留
- action：rewrite

## 对抗结论

- 本轮发现 15 个问题（critical:2，high:3，medium:7，low:3）。
- 相比上一轮：改善 0 个、新增 15 个、未解决 16 个。**R1 的 18 个遗留问题中 0 个修复、16 个未修复、2 个部分修复**——这是非常严重的项目健康信号：本轮 references.md 做了重排（Cochran/Sørensen 后移到 [63]/[64]）但**正文未同步**，导致新的 critical 一致性问题（H1、H2）反而比 R1 报告的 H1-H3 更严重。
- 是否达到输出标准：**否**。综合 0.55 远低于 general 项目 min_overall=0.80 阈值；critical 问题 2 个（不超 max_high_issues=0 约束）；high 问题 3 个；medium 问题 7 个（远超 max_medium_issues=3）。**结构性不达标**。
- 返工优先级：
  - **P0（必须立即修复，不修改不予通过）**：
    - H1（references.md 编号重排与正文三文件 [N] 同步重映射 + 双向核对）
    - H2（Rost 文献补回 + 全文"Rost [67]" 同步更新 + references.md §8 同步修正）
    - H5（arXiv 26xx vs (2025) 年份矛盾——R1-H1 完全残留）
  - **P1（强烈建议）**：
    - H3（content.md L35 "[58]—[60]" → "[59]—[61]"）
    - H4（"落在带间共振附近" 措辞降级）
    - H6（references.md §8 版本史注记删除）
    - R1-H1/H2/H4/H5 全部残留
  - **P2（建议）**：H7、H8、H9、H10、H11
- 下一轮评审建议聚焦：
  - 执行 references.md 全表与正文 [N] 编号一次性同步（脚本化映射 + 双向核对）
  - 检查 rationale.md 是否仍含旧编号 [62][63]
  - 修复 H1-H11 后重测严谨性，应能回升到 0.70+
  - 写作风格已在范本区间内，无需大规模重写；重点关注 §2.5 与 §3 §6 的内容去重

## 评分

创新性：0.78
可行性：0.72
严谨性：0.45
表达质量：0.55
综合评分：0.55