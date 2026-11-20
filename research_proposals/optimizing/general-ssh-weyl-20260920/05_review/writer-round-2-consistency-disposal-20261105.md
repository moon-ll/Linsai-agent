# 修订处置记录 — 第 2 轮整体一致性审查（focus：表达质量）

课题：general-ssh-weyl-20260920｜类型：general（面上）｜日期：2026-11-05｜角色：writer

本文件为过程性材料，不进入申请书章节文件。修订落点：`04_proposal/sections/` 下 rationale.md、content.md、scheme.md、full_review.md、references.md。

---

## 一、评审问题逐条处置

| # | 问题 | 级别 | 处置 | 落点 |
|---|---|---|---|---|
| 1 | 超长句 20 处（>120 字），免赔 9，程序扣 0.22 | high | **已消除**：20 → 0。技术性长句按多分句拆分；LaTeX 显示公式块改写为短行并以 `\;` 续接符号避免行首触发列表检测 | scheme §2.1/§2.2/§3.1.2/§3.2.2/§3.3.2/§5、rationale §2.2/§4/§2.3、content §2.6 |
| 2 | δ_FP 协议句 content §2.2 ↔ scheme §2.3 跨章近重复 | high | **已消除**：定标协议以 scheme §2.3 为单一出处；content §2.2 改为「定标集与度量集彼此独立这一要求，构成 δ_FP 之外三项指标的可复算前提，δ_FP 的显著性水平设定见研究方案」 | content §2.2 |
| 3 | 「R=全量上界、残余恒不超过全量」三处逐字级复述 | high | **已消除**：保留 scheme §2.2 完整版；rationale §4 改为「R 与残余门槛 R_res 的分工在研究方案中给出」；content §2.5 改为「两层的分工由上界性质决定，R 与 R_res 的形式化定义、扣除项与扣除方法在研究方案中给出」 | rationale §4、content §2.5 |
| 4 | G1 统计口径同段两版（N=400 vs 2N=800） | medium | **已消除**：G1 统计量定义在 2N 上，全稿统一按 800 样本复算——1σ = ±0.77 pp、Wilson 单侧 95% 下界 93.6%（真值 95%）、点估计 ≥ 95% 达成概率 0.54。scheme §2.3 给出完整版，content §2.2/§2.6 同步「各类 400 个、总计 800 个」 | scheme §2.3、content §2.2、content §2.6 |
| 5 | THz 弱场校核窗 T₂ 未单独分档，与 Klimmer[38] 24 fs 张力未处理 | medium | **已消除**：弱场校核窗退相干时间单独分档，取 T₂ 在 5–25 fs 区间扫描（下界取 Korolev[36] 谷底 200 fs 与谷区外 10 fs 以下，上界取 Klimmer[38] 24±1 fs），并要求 R² ≥ 0.9 的达成在该区间内对 T₂ 不敏感，否则按适用边界标注散射参数可达区间 | scheme §3.1.2、scheme §2.2（R² 条目） |
| 6 | 「10¹¹ W/cm²$」悬空数学闭合符两处 | medium | **已消除**：两处均删去多余 `$`，恢复正确渲染 | scheme §2.1 |
| 7 | content §2.5 T≥0.3 预标定依据过强 | low | **已修改**：补「该预标定值由上文 Tornow 等人[42] 的 Berry 曲率宇称选择规则读出关系作量级预估，最终值以方向四双基线扫描回填为准」 | content §2.5 |
| 8 | 预印本占比逼近 30% 警戒线 | low | **未改动（维持现状）**：本轮新增 5 条均为 arXiv 预印本但直接服务于方法学论证链，非凑数引用；refs 条目已逐条标注预印本属性，发表状态以正式发表为准的限定语保留。投稿前复核项留待 references 专轮处理 | references.md |

---

## 二、AI 写作模式程序化检测（复算）

检测器：`scripts/proposal_lifecycle/optimize.py::_detect_ai_patterns`（含 AI_TERM_WHITELIST 遮蔽），以 §4 正文三章为输入。

| 指标 | 修订前 | 修订后 | 阈值 | 扣分 |
|---|---|---|---|---|
| 死板关联词 | 6 | 3（同时 2、因此 1） | 48 | 0 → 0 |
| 模板句式「为…提供…」 | 0 | 0 | 8 | 0 → 0 |
| 模板主语「本项目拟/将」 | 0 | 0 | 5 | 0 → 0 |
| 冗余修饰词 | 16 | 9（有效 5、显著 2、完整 2） | 97 | 0 → 0 |
| **超长句** | **20** | **0** | 免赔 9 | **0.22 → 0** |
| 元话语 | 0 | 0 | 2 | 0 → 0 |
| 过度加粗 | 0 | 0 | 3/千字 | 0 → 0 |
| 编号/bullet 列表替代论述 | 0 | 0（修 LaTeX 续行后行首 `-`/`+` 不再构成列表块） | — | 0 → 0 |
| 自引用泛滥 | 0 | 0 | 10/15 | 0 → 0 |

**表达质量天花板：0.78 → 1.00**（修订前 0.78 受超长句扣 0.22 压制；修订后九项检测全部零扣分）。

修订过程中出现的 4 处新增长句（Trines/Yamada/Hogger 相关新引用段）已在本轮内二次拆分，复算为 0。

---

## 三、跨章口径同步

| 口径 | 同步动作 |
|---|---|
| G1 统计量 | scheme §2.3 完整版（2N=800，1σ ±0.77 pp，Wilson 单侧下界 93.6%，点估计达成概率 0.54）；content §2.2 与 §2.6 同步样本总数表述；full_review.md §三 对应行更新 |
| 弱场校核窗 T₂ | scheme §3.1.2 新增独立分档（5–25 fs 扫描 + 稳健性检查）；scheme §2.2 R² 条目补「达成须对弱场窗 T₂ 取值不敏感」；full_review.md §三 退相干分档行更新 |
| 定标协议单一出处 | scheme §2.3 保留完整版；content §2.2 改指针；full_review.md §三 自定标阈值协议行补「协议完整表述只在研究方案 §2.3」 |
| R/R_res 分工单一出处 | scheme §2.2 保留完整版；rationale §4 与 content §2.5 改指针；full_review.md §三 R ≥ 2 数值依据行注明分工论证的单一出处 |
| T ≥ 0.3 依据 | content §2.5 补量级预估与回填限定语；full_review.md §三 对应行同步 |

params.json 七条 canonical 的 stale_patterns 全稿零命中（rationale/content/scheme/full_review/references 全部扫描）。

---

## 四、本轮新增文献（5 条，元数据已联网核实 arXiv 原始记录）

| 编号 | 文献 | arXiv | 已引用位置 |
|---|---|---|---|
| [47] | A. Yamada and K. Yabana, "Microscopic Origin of Dephasing in Solids from First-Principles Electron-Phonon Interactions" | 2607.17109 | rationale §2.3；scheme §2.1 |
| [48] | A. T. Andersen, S. V. B. Jensen, and L. B. Madsen, "Intra- and intercycle analysis of intraband high-order harmonic generation" | 2404.06237（PRA 109, 063109） | rationale §2.3；content §2.4；scheme §3.2.1 |
| [49] | W. Hogger et al., "Coherent suppression and dephasing-induced reentrance of high harmonics in gapped Dirac materials" | 2503.11432 | rationale §2.3；content §2.4；scheme §2.2 |
| [50] | N. Boroumand et al., "Strong field physics in open quantum systems" | 2502.10240 | rationale §2.3；scheme §2.1 |
| [51] | R. Trines et al., "Dynamical symmetries in laser harmonic generation via a cubic nonlinearity" | 2507.08635 | rationale §2.1；content §2.2 |

五条的元数据（题名、作者、arXiv 号、期刊卷页）均取自 arXiv 原始记录页（联网核实），未凭记忆补全。参考文献总数 46 → 51。

---

## 五、历史遗留 P0 核对

| 编号 | 归属 | 状态 | 本轮核对结果 |
|---|---|---|---|
| P0-1 数值链 §4 算力预算 ↔ §3.1.2 步长与步数 | scheme | 已解决 | **维持**：Δt = 0.1 a.u.（2.42×10⁻³ fs）→ 30–100 fs 主窗 1.2×10⁴–4.1×10⁴ 步、叠加后脉冲 1.7×10⁴–4.6×10⁴ 步；THz 通道 Δt = 0.2 a.u.（4.84×10⁻³ fs）→ 0.3 THz 下 6.9×10⁶–1.4×10⁷ 步、1 THz 下 2.1×10⁶–4.1×10⁶ 步。旧「0.01 fs」表述零残留。本轮为消除超长句改写了算力预算段的分句，未触动数值 |
| P0-2 判据自相矛盾 §2.2 ΔI_gap 两层分工 | scheme | 已解决 | **维持并强化**：全量层 ΔI_gap^full ≥ R(=2) 与残余层 ΔI_gap^res ≥ R_res 两层分工明确，「R 因而不作为残余门槛，只作全量层的判定值」的论证保留在 scheme §2.2 完整版 |
| P0-3 Δt 拟合时窗下限两版 | scheme | 已解决 | **维持**：§2.2 时窗下限 ≥ 30 fs 覆盖寿命衰减周期；Bera 等人[13] 的约 25 fs 驱动窗口作裕量参考，不参与阈值换算 |
| P0-4 末组文献编号整组错位一格 | rationale 等 | 已解决 | **维持**：refs [46] Schüler 与正文角标对应正确；本轮新增 [47]–[51] 编号连续无跳号，角标与 references.md 条目一一对应已逐条核验 |
| P0-5 [20] 增强上限两数量级表述 | content | 已解决 | **维持**：全稿统一 Lorenzo 等人[18]（正文角标）刊版口径 reaching up to two orders of magnitude；本轮 rationale §2.2 该句为消除超长句做了分句改写，数值与版本归属未变 |

---

## 五之二、跨章复述收敛（scheme 侧）

新增文献的引用一度在 rationale / content / scheme 三处形成 34–69 字的重复片段，共 6 处。处理方式：schemes 侧（技术章）改写为方法学指向或自含表述，文献综述性叙述只保留在 rationale（现状章）与 content（内容章）一处。

| 重复片段 | 处理 |
|---|---|
| Andersen[48] 周内/周期间分解（69 字，scheme↔rationale） | scheme 保留机制读出规则一句，删去与 rationale 重复的文献复述 |
| Yamada[47] 退相干由布居动力学主导（60 字，scheme↔rationale） | scheme 保留该结论对引擎 T₂ 建模的直接含义，删去工作方法的重复描述 |
| Hogger[49] 重入机制（38 字，scheme↔content） | scheme 只保留对镜像差分协议解耦要求的工程含义 |
| Boltzmann 两区间划分（31 字，scheme↔rationale） | scheme 改为自含表述 |
| R = 2 数值依据（34 字，scheme↔rationale/content） | scheme 补回版本归属的保守下界表述，成为该数值的唯一完整出处 |

复算：跨章共同片段 ≥30 字者由 6 处降至 0 处（脚本对 scheme×content、scheme×rationale 两组做最长公共子串扫描）。

---

## 六、文件纯净性与边界核查

- 章节文件只含正文：rationale/content/scheme/full_review/references 五文件无轮次编号、无内部文件名、无审校注记、无检索时间戳。
- full_review.md 为纯骨架：主线论证链 + 章节衔接点 + 跨章节统一表述表 + 纯净性声明，CJK 1973 字（上限 3000），无逐项对照表与轮次说明。
- 过程性材料（本文档）归 05_review/，未写入任何章节文件。
- 内容边界：未新增研究基础/工作条件/团队/经费内容；可行性分析仍限「原理成立 + 方法对照 + 降级路径」层面。
- 禁用词表（nsfc-writing 第三节）逐词 grep：章节文件零命中。

---

## 七、遗留与建议

1. 评审条目 8（预印本占比）为低级别，本轮维持现状。建议在 references 专轮统一复核 [17][18][19][32][42][43][44][45][47][48][49][50][51] 的发表状态，必要时更新期刊卷页与 DOI。
2. 表达质量天花板已解除压制（0.78 → 1.00），下一轮建议聚焦严谨性与可行性的实质提升：THz 弱场窗 T₂ 扫描区间（5–25 fs）为方案设定值，其下界与上界的文献归属已分列，建议在方法学手册中补齐反演协议。
3. 方案设定值清单（本项目自定、非文献直出）：S_edge ≥ 0.2、R_HOTI ≥ 10、Δκ ≥ 20%、T ≥ 0.3、R = 2、R_res 回填规则、弱场窗 T₂ 扫描区间 5–25 fs、X + Y + Z ≥ 95%。
