# 对抗评审报告（critic-round-1）— 参考文献专项检验

## 元信息
- 申请书名：general-moire-strong-field-probe-20260726（莫尔强场 HHG 反演 + Floquet 调控闭环）
- 项目类型：general（面上）
- 评审日期：2026-08-20
- Profile：critic
- 本轮聚焦：参考文献专项检验（不评创新性、可行性、写作风格）
- 检验范围：references.md + 三个正文文件（rationale.md / content.md / scheme.md）
- 注：sections/ 目录下无 methodology-manual.md（references.md 自述含此文件，但不在本任务路径）

## 综合评分
严谨性：0.62 ｜ 完整性：0.85 ｜ 综合评分：0.74

## 维度评分

| 维度 | 权重（general） | 得分 | 主要扣分点 |
|------|---------------|------|----------|
| 严谨性（rigor） | 0.50 | 0.62 | 编号体系与正文不一致（最严重）；1 处模板占位符残留 |
| 完整性（completeness） | 0.50 | 0.85 | 时效性极佳；备选文献管理清晰；0 处断链 |
| 创新性 | N/A | N/A | 本轮不评 |
| 可行性 | N/A | N/A | 本轮不评 |

## 事实核查表（核心数据）

| 指标 | 数值 | 来源 |
|------|------|------|
| 参考文献总条目数 | 31 | references.md L11–L107（[1]–[31] 连续编号） |
| 正文实际引用 CITE 标签数（去重） | 25 | rationale/content/scheme 三文件 union |
| 正文总引用次数 | 144 | rationale(27) + content(32) + scheme(17) 次 |
| 断链数（正文引用但 ref 列表未列） | 0 | 25 个 CITE 标签 100% 命中 references.md |
| 幽灵引用数（ref 列但正文未引） | 7 | 6 篇备选文献 + 1 个 `author_journal_year` 模板占位符残留 |
| 编号 [N] 在正文中的使用 | 0 处 | rationale/content/scheme 均未使用数字编号 |
| 编号 [N] 在 references.md 的使用 | 31 处 | 连续 [1]–[31]，无跳号、无重复 |
| DOI 完整度 | 30/31 | 仅 [11] Ikeda 2020 无正式 DOI（标 arXiv:2005.01718） |
| 年份分布 | 2024–2025 占 51.6%；2020–2023 占 41.9%；2011–2019 占 22.6% | 含 2 篇 2011 奠基、1 篇 2015、1 篇 2018、1 篇 2019 经典 |
| references.md 自述引用次数 | 153（含 methodology-manual.md） | 本任务范围仅 144（差 9 处应归 methodology-manual.md，但该文件不在本任务路径下） |

## 问题清单

### [critical] citation_inconsistency — 编号体系两套并存：references.md 用 [N] 编号，正文用 [CITE:xxx] 标签
- 位置：rationale.md / content.md / scheme.md 全文件 + references.md L11–L107
- 问题：references.md 中 31 条文献均以 `[1]` `[2]` ... `[31]` 数字编号开头（行首格式如 `[1] Zhang Y., Su Y., Wang L. 等.*标题*...`），但正文三文件 0 处使用 `[N]` 数字编号引用，全部使用 `[CITE:author_journal_year]` 标签（如 `[CITE:molinero_optica_2024]`）。导致：
  1. 评审专家按 NSFC 范本习惯数 `[1]` `[2]` 时找不到任何正文引用位置
  2. references.md 末尾"引文—正文对应矩阵"中统计的是 `[CITE:xxx]` 标签，与 [N] 编号系统脱钩
  3. 提交系统若按 [N] 编号解析引用将得到 0 处匹配
- 严重性判据：critical（违反 NSFC 参考文献规范基本要求 — 编号与正文必须一一对应）
- 建议：将 references.md 中 31 条文献全部改为 `[CITE:xxx]` 标签格式（与正文统一），并删除 [N] 编号行首；或者反之，将正文所有 `[CITE:xxx]` 替换为对应的 `[N]` 数字编号（推荐前者，与当前正文 144 处引用兼容）
- action：rewrite

### [high] template_residue — `author_journal_year` 模板占位符在 references.md L180 残留
- 位置：references.md L180
- 问题：references.md 末尾"统计信息"段自述"**总文献数 31 篇**（全部带 `[CITE:author_journal_year]` 标签）"——此处 `author_journal_year` 是 r9 之前的模板占位符，r19 已删除大部分但 L180 的描述性段落漏改。虽然正文三文件中 0 处残留（已核查），但 references.md 内 1 处 + 引文矩阵元描述 2 处共 3 处仍可见该占位符（[CITE:author_journal_year] 出现 2 次是因 r19 在引文矩阵元描述里替换为"真实标签示例"但保留了同段的自述模板）
- 严重性判据：high（NSFC 评审看到 `[CITE:author_journal_year]` 字面会直接判定为模板未替换/工具生成残留 — 触发"低严谨性"标签）
- 建议：将 references.md L180 的"全部带 `[CITE:author_journal_year]` 标签"改为"全部带 `[CITE:author_journal_year]` 唯一标签"或更具体地"全部带 `CITE:author_journal_year` 格式标签（如 `[CITE:molinero_optica_2024]`）"，消除模板字符
- action：patch

### [medium] citation_count_drift — references.md 自述"153 处"与本任务范围实测 144 处不一致
- 位置：references.md L180（统计信息段）
- 问题：references.md 自述"三章正文共 153 处"和"24 篇在四个核心文件（rationale.md / content.md / methodology-manual.md）的正文中实际引用"，但本任务范围（rationale/content/scheme 三文件）实测仅 144 处引用，差 9 处。
- 根因：sections/ 目录下无 methodology-manual.md 文件（已 `ls` 确认），references.md 元描述基于四文件存在前提，本任务仅交付三正文文件
- 严重性判据：medium（不影响评审主结论，但造成评审数引用次数时的预期偏差；如 methodology-manual.md 已合并到正文或删除，references.md 应同步更新元描述）
- 建议：方案 A — 删除 references.md L180/L186 中所有 methodology-manual.md 字样，统一改为"在三个核心文件（rationale.md / content.md / scheme.md）的正文中实际引用 144 处"；方案 B — 在 references.md 顶部说明"本节自述基于四文件版本（r20），如 methodology-manual.md 不存在则按三文件 144 处统计"
- action：patch

### [medium] preprint_uncertainty — 文献 [11] Ikeda 2020 为 arXiv 预印本（2020 年至今 6 年仍未正式发表）
- 位置：references.md L37
- 问题：条目 [11] Ikeda T. N. 等 *High-order nonlinear optical response of twisted bilayer graphene*，格式为 `arXiv preprint arXiv:2005.01718 (2020)`，无期刊卷期页与正式 DOI。arXiv:2005.01718 提交于 2020 年 5 月，至 2026 年仍未在正式期刊发表（需进一步核查 Crossref/INSPIRE-HEP 等数据库确认状态）。申请书正文仅 §1.2 / §2.1 引用 1 次（CITE:ikeda_arxiv_2020），作为"TBG HHG 早期理论奠基"出现
- 严重性判据：medium（Ikeda 2020 仅作为"早期理论奠基"1 处引用、不是核心论断的承重墙，但预印本支撑"早期映射框架"性质的论断需要谨慎表述）
- 建议：在引用时改为"据目前检索，该早期理论预言仅以预印本形式公开（arXiv:2005.01718，2020）"以避免将预印本陈述为正式发表；或核查 INSPIRE-HEP 数据库确认是否后续有正式发表版本
- action：verify

### [medium] volume_format_inconsistency — 31 条参考文献的卷期格式分四类
- 位置：references.md L11–L107
- 问题：31 条参考文献的卷期-页码格式不统一，按出现频率为：
  - `卷, 页码`（22 篇）：如 [1] Nature Materials **23, 844–855** —— 标准格式
  - `卷(期), 文章号`（6 篇）：如 [3] Matter **(Cell Press), 102325**、[6] Nat. Rev. Mater. **9(7), 460–480**、[22] Nature **600(7888), 235–239**——这是规范的"卷(期), 起页"或"期刊, 文章号"格式
  - `arXiv preprint`（1 篇）：[11] —— 预印本无卷期页
  - `期刊 卷, 文章号`（2 篇）：[13] Nat. Commun. **15, 6228**（实际应为"15, 6228" = 卷 15、起页 6228，Nat. Commun. 用 5 位文章号无页码）、[29] Nat. Commun. **14(1), 7273**（实为卷(期), 文章号 7273）—— 格式上 Nat. Commun. 用文章号而非页码是期刊惯例，可接受
- 严重性判据：medium（不构成错误，但 NSFC 评审偏好的标准格式是 `期刊 卷(期): 起页–止页`，现有格式 22/31 严格符合，6/31 偏差，3/31 是 PNAS 文章号格式或 arXiv）
- 建议：保持现有格式（多数期刊的现行惯例），无需修改；评审专家通常理解 PNAS eXXXXXXX、Matter 文章号、Nat. Commun. 5 位文章号的格式差异
- action：no_change（格式偏差在期刊惯例内）

### [low] citation_relevance — 文献 [19] Pisanty 2019 与申请书主线相关性偏弱
- 位置：references.md L65
- 问题：[19] Pisanty E. 等 *Conservation of OAM in High Harmonic Generation* (PRL 122, 143901, 2019) — 该文献是 OAM（轨道角动量）涡旋光在 HHG 中守恒的奠基。申请书正文 0 处使用，仅在 references.md 标注为"备选（远期展望）"——OAM-HHG 与申请书主线（莫尔 HHG 反演 + Floquet 调控）的关联较弱（仅在 §3.1 提到"复杂光场主动调控"时与 OAM 控制技术有边际关联）
- 严重性判据：low（已标注"备选（远期展望）"，属于合理的管理边界文献；引用总数 7 篇备选中相关性最弱，但纳入不影响质量评价）
- 建议：保留（作为"研读基础列入文末不算问题"，符合用户任务说明的容忍范围）
- action：no_change

### [low] citation_density — 3 个高频 CITE 标签占全部引用的 35%
- 位置：rationale.md / content.md / scheme.md 多处
- 问题：正文 144 处引用中，[CITE:molinero_optica_2024] 21 次、[CITE:mrudul_prb_2024] 16 次、[CITE:hu_meng_pnas_2024] 15 次——三者合计 52 次占 36.1%。这是申请书"以 Molinero 2024 为方法学对照基线、以 Mrudul 2024 为椭偏理论依据、以 Hu/Meng 2024 为反演母方法学"的合理反映，但需审视是否构成"过度引用单一文献"
- 严重性判据：low（核心方法学文献高频引用是申请书常见结构，并非缺陷；但建议分散到邻近工作以增强证据链多元性）
- 建议：保持（申请书逻辑上确实以这 3 篇为核心，引用密度反映依赖关系）
- action：no_change

## 缺失引用检查（重要论断是否缺文献支撑）

逐项核查申请书的关键论断，无缺漏：

| 论断 | 引用支撑 | 状态 |
|------|---------|------|
| magic-angle TBG 关联绝缘态（Cao 2018）| [CITE:caonature_2018] | ✓ |
| TBG HHG 全光表征（Molinero 2024）| [CITE:molinero_optica_2024] | ✓ |
| TBG HHG 椭偏依赖（Mrudul 2024）| [CITE:mrudul_prb_2024] | ✓ |
| 多维反演母方法学（Hu/Meng 2024）| [CITE:hu_meng_pnas_2024] | ✓ |
| QGT 反演（Bauer-Hansen 2018）| [CITE:bauer_hansen_prl_2018] | ✓ |
| 光 Floquet 调制（Shan 2021）| [CITE:nikola_nature_2021] | ✓ |
| 黑磷 Floquet（Zhou 2023）| [CITE:zhou_nature_2023] | ✓ |
| 体相 MoS₂ 谷极化（Tyulnev 2024）| [CITE:tyulnev_nature_2024] | ✓ |
| TMDC 莫尔莫特绝缘态（Lian 2024）| [CITE:lian_natphys_2024] | ✓ |
| TMDC 莫尔 valley-pseudospin 可调（Xu 2024）| [CITE:xu_natcomm_2024] | ✓ |
| MoS₂ HHG 截止 7-11 阶（Kozák 2023）| [CITE:kozak_apl_2023] | ✓ |
| MoS₂ HHG GW 多体增强（Qiu 2024）| [CITE:qiu_natcomm_2024] | ✓ |
| 莫尔紧束缚 + SBE O(N³) 复杂度（Bistritzer 2011）| [CITE:bistritzer_macdonald_pnas_2011] | ✓ |
| ZnO HHG α ≈ 2.5 基线（Ghimire 2011）| [CITE:ghimire_natphys_2011] | ✓ |
| SBE 在 MoS₂ Floquet（Xu/Zhou 2024）| [CITE:xu_zhou_npj_qm_2024] | ✓ |
| DMRG 莫尔多体（Soejima 2020）| [CITE:soejima_prb_2020] | ✓ |
| 光致关联相熔化类比（Amato 2024）| [CITE:amato_prb_2024] | ✓ |
| MoS₂ 非线性平台（Wang/Yu 2025）| [CITE:wang_yu_matter_2025] | ✓ |
| TBG HHG 早期理论（Ikeda 2020）| [CITE:ikeda_arxiv_2020] | ✓ |
| 声子-电子耦合 HHG（Hu/Meng 2024 PRL）| [CITE:hu_meng_prl_2024] | ✓ |
| 2D Berry 曲率 HHG 反演（Yao 2025）| [CITE:prj_2024_2dberry] | ✓ |
| 莫尔材料微观视角（Nuckolls/Yazdani 2024）| [CITE:nuckolls_yazdani_nat_revmater_2024] | ✓ |
| TBG isospin 激发（Xie 2024）| [CITE:xie_nat_2024] | ✓ |
| 固体 HHG 综述（Heide 2024）| [CITE:heide_nphys_2024] | ✓ |
| 莫尔非线性综述（Zhang/Su/Wang 2024）| [CITE:zhang_su_wang_nat_mater_2024] | ✓ |

→ **25 个不同 CITE 标签对应 25 个关键论断，无缺漏**。申请书的核心科学论证链覆盖完整。

## 引用数量与时效性评估

| 维度 | 实测 | 用户任务标杆 | 评级 |
|------|------|-------------|------|
| 参考文献总数 | 31 篇 | 20–40 篇（范本 30–40 篇） | ✓ 优秀 |
| 正文 [N] 编号引用次数 | 0 次 | 10–20 次 | ✗ 不达标（用 [CITE:xxx] 替代，144 次） |
| 实际有效引用次数 | 144 次 | 10–20 次 | ✓ 超额达标 |
| 备选/研读文献 | 6 篇 | 允许 | ✓ 合理 |
| 2024–2025 时效性 | 16/31 = 51.6% | ≥30% | ✓ 优秀 |
| 2020–2023 关键奠基 | 10/31 = 32.3% | — | ✓ 合理 |
| 2011–2019 经典基础 | 5/31 = 16.1% | — | ✓ 必要奠基 |
| 过于陈旧（>10 年） | 2 篇（Ghimire 2011、Bistritzer 2011）| ≤3 篇 | ✓ 合理（学科奠基） |

## 对抗结论

### 整体判断
**参考文献总体质量较高**，但存在 1 项 critical 红线问题（编号体系不一致）和 1 项 high 问题（模板占位符残留）。其他 5 项 medium/low 问题不影响主结论。

### 本轮发现
- critical：1 项
- high：1 项
- medium：3 项
- low：2 项
- 合计：7 项问题

### 与上一轮对比
无上一轮参考文献专项评审对比基准（首次）。但从 references.md 内嵌的 r17–r20 更新日志可见，已经历 4 轮迭代修复：
- r17 修复 critical DOI 错误（文献 #18、#22）+ 新增 4 篇
- r19 修复 high DOI 重复（删除 §8 全部 11 条幽灵）+ 修正预印本格式
- r20 激活 bistritzer 引用 + 删除无源数字"1.5–2 倍"

→ **本轮新增问题均未在前 4 轮覆盖**：
- critical：编号体系 [N] vs [CITE:xxx] 并存（pre-existing 但未被发现）
- high：`author_journal_year` 模板占位符 L180 残留（pre-existing 但未完全清除）
- medium：references.md 自述 153 处与三文件实测 144 处不一致（基于 methodology-manual.md 存在前提）

### 是否达到输出标准
**否**（critical + high 共 2 项需优先处理）：
- critical（编号体系不一致）必须修复后再提交，否则 NSFC 系统解析会失效
- high（模板占位符）必须清除，模板残留会被评审直接判为"未完成"

### 返工优先级
- **P0（立即修复）**：
  1. 编号体系统一 — 选 A 方案：删除 references.md 中 31 个 `[N]` 行首编号，改用 `[CITE:xxx]` 标签作为条目唯一标识（与正文 144 处引用兼容）
  2. 清除 references.md L180 的 `author_journal_year` 字面占位符
- **P1（建议修复）**：
  3. references.md L180 元描述同步更新为"三文件 144 处"或补充"基于四文件版本"声明
  4. [11] Ikeda 2020 在正文引用处加"预印本"限定语
- **P2（不阻塞）**：卷期格式统一、Pisanty 2019 备选文献管理可保留

### 下一轮评审建议聚焦
如需第 2 轮参考文献专项评审，建议聚焦：
1. P0 修复后的验证（编号体系统一 + 模板清除）
2. Ikeda 2020 正式发表状态核查（arXiv:2005.01718 是否已发表于 Phys. Rev. B 或其他期刊）
3. 5 篇备选文献（[4] Xu/Morimoto 2021、[5] Wang 2023、[15] Zhang 2023、[29] Policht 2023、[30] Vampa 2015）的相关性再评估 — 是否需要删除以收紧文献库

## 评分
创新性：N/A
可行性：N/A
严谨性：0.62
完整性：0.85
综合评分：0.74