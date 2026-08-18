# 对抗评审报告（第 2 轮）——参考文献专项检验

## 元信息

| 项目 | 内容 |
|------|------|
| 申请书 | key-transient-quantum-phase-optical（瞬态量子相全光读写） |
| 项目类型 | key（重点） |
| 评审日期 | 2026-08-14 |
| profile | critic |
| 本轮聚焦 | 参考文献检验（引文格式、编号一致性、引用相关性、缺失引用、引用数量、时效性） |
| 事实核实 | 基于 references.md（62 条）+ rationale.md（含嵌入文献表 54 条）+ content.md + scheme.md 正文全文交叉比对 |

---

## 综合评分

本轮为参考文献专项检验，仅评严谨性与完整性两个维度（创新性/可行性标记 N/A）。

**严谨性 0.62**：存在 2 个 critical 级引文错误（[12] 两版本为不同论文、[43]/[44] 引用矛盾），8 条参考文献从未被正文引用（"死引文"），rationale.md 嵌入文献表缺失 8 条，[62] 匿名作者无法核实。

**完整性 0.80**：引用总数充足且时效性好（2023–2026 年占 58%），但 62 条总量偏高，预印本占比 40.3% 超过 30% 阈值，核心论断仍有多处缺 foundational citation。

综合评分 = (0.62 + 0.80) / 2 = **0.71**

---

## 维度评分

| 维度 | 权重 | 得分 | 问题数 |
|------|------|------|--------|
| 严谨性 | 50% | 0.62 | 2 critical + 4 high + 2 medium |
| 完整性 | 50% | 0.80 | 2 high + 1 medium + 1 low |
| 创新性 | — | N/A | — |
| 可行性 | — | N/A | — |

---

## 检验结果总览

### 文件统计

| 文件 | 参考文献条数 | 正文引用编号 | 引用唯一数 |
|------|-------------|-------------|-----------|
| references.md | 62（[1]–[62]） | — | — |
| rationale.md（嵌入表） | 54（[1]–[54]） | [3]–[54]（正文段，排除[1][2][4]） | 47 |
| content.md（正文） | — | [5][9][20][21][32][33][34][58][59][60] | 10 |
| scheme.md（正文） | — | [5][6][9][18][19][20][21][31][32][33][34][51][52][61][62] | 15 |
| 三文件正文合计唯一引用 | — | — | 54 |

### 六项检查结论速览

| 检查项 | 结论 | 问题数 |
|--------|------|--------|
| 1. 引文格式 | 两套格式混用（全字段 vs et al. 简写），不统一 | 2 medium |
| 2. 编号一致性 | [43]/[44] 矛盾；8 条死引文；嵌入表缺 8 条 | 2 critical + 3 high |
| 3. 引用相关性 | [55][56][57] 与正文无关联；[62] 匿名作者不可核实 | 2 high |
| 4. 缺失引用 | TKNN/陈数、Haldane 模型等核心概念缺 foundational citation | 1 high + 1 medium |
| 5. 引用数量 | 62 条超出重点惯例（30–50），含 8 条死引文 | 1 medium |
| 6. 时效性 | 2023–2026 占 58%，时效性好；预印本占比 40.3% 偏高 | 1 high |

---

## 问题清单

### [critical] C1 — 引文归属错误：[12] 在 references.md 与 rationale.md 为两篇不同论文

- 位置：references.md 第 25 行 vs rationale.md 第 155 行
- 问题：同一编号 [12] 在两个文件中指向不同的期刊、卷号和年份：
  - references.md：M. H. Beck et al. "The multiconfiguration time-dependent Hartree method." Phys. Rep. 324, 1 (2000)
  - rationale.md：M. H. Beck et al. Rep. Prog. Phys. 72, 085601 (2009)
  - 期刊不同（Phys. Rep. vs Rep. Prog. Phys.），卷号不同（324 vs 72），年份不同（2000 vs 2009）
- 核实：MCTDH 方法的原始综述论文确实是 Beck et al., Phys. Rep. 324, 1–105 (2000)。references.md 的版本正确，rationale.md 的版本期刊、卷号、年份均错。
- 建议：将 rationale.md 嵌入表 [12] 统一修改为 references.md 版本：`M. H. Beck, A. Jäckle, G. A. Worth, H.-D. Meyer. The multiconfiguration time-dependent Hartree method. *Phys. Rep.* 324, 1 (2000). DOI: 10.1016/S0370-1573(99)00047-2`
- action：rewrite

### [critical] C2 — [43]/[44] 引用矛盾：注释声明统一用 [43]，但正文实际引用 [44]，且 [43] 从未被引用

- 位置：references.md 第 87–89 行（[43][44] 条目注释）vs rationale.md 第 37 行（§2.1 正文）
- 问题：
  - references.md [44] 注释写道"与 [43] 为同一系列工作，正文引用统一使用 [43]"
  - 但实际正文中唯一引用的是 [44]（rationale.md §2.1："Yu 等[44]综述了强场驱动固体中超快相位检索方法的发展"）
  - [43] 在三份正文中从未出现
  - 二者为同一 arXiv ID（2503.07256），[44] 为 [43] 的精简标题版本
- 建议：二选一——
  - 方案 A（推荐）：删除 [44]，将 rationale.md §2.1 中的 `[44]` 改为 `[43]`，并在 [43] 条目中补完整标题
  - 方案 B：删除 [43]（从未引用），将 [44] 改为正式编号保留
- action：remove + rewrite

---

### [high] H1 — 8 条参考文献从未被正文引用（死引文）

- 位置：references.md [1][2][4][43][50][55][56][57]
- 问题：以下 8 条参考文献在 rationale.md / content.md / scheme.md 的正文段落中从未以 [N] 形式引用：
  - [1] Thouless et al. 1982（TKNN 陈数奠基论文）——"TKNN 陈数"在 content.md 中被提及（"并非把平衡态 TKNN 陈数原样照搬"），但未给出引用 [1]
  - [2] Haldane 1988（无朗道能级的量子霍尔效应模型）——Floquet 拓扑相变讨论中未引用
  - [4] Kitagawa et al. 2010（周期驱动量子系统的拓扑表征）——与 Floquet 拓扑直接相关但未引用
  - [43] 见 C2
  - [50] Ma et al. 2024（阿秒计量）——从未引用
  - [55] Lucchini et al. 2023（Floquet-Bloch 带的建立与退相）——从未引用
  - [56] Lucchini et al. 2023（固体高次谐波干涉仪）——从未引用
  - [57] Lucchini et al. 2024（Mott-CDW 相变中的 HHG 跟踪）——从未引用
- 风险：评审专家会质疑这些文献存在的必要性——是凑数还是遗漏引用？8 条死引文占总数的 13%。
- 建议：
  - [1][2][4]：应在正文首次提及相关概念处补引（见 H3）
  - [50]：检查是否有对应正文段落遗漏了引用，或删除
  - [55][56][57]：这三条均为 Lucchini 组的工作，与正文关联不明确——若正文无对应论述，应删除
- action：add（补引用）或 remove（删除无用条目）

### [high] H2 — rationale.md 嵌入文献表缺失 [55]–[62]，与 references.md 不同步

- 位置：rationale.md 第 131–239 行（"### 参考文献"节）
- 问题：rationale.md 末尾的嵌入参考文献表仅到 [54]，缺失 [55]–[62] 共 8 条。而 content.md 和 scheme.md 的正文引用了 [58][59][60][61][62]。
  - 若申请书以 rationale.md 的嵌入表作为最终提交版本，content.md/scheme.md 中引用的 5 条参考文献将无定义。
  - references.md 是完整版（62 条），但两份文件未同步。
- 建议：确保最终提交版本使用统一的参考文献表。若 references.md 为权威版本，则 rationale.md 末尾的嵌入表应删除或补齐 [55]–[62]。
- action：verify + rewrite

### [high] H3 — 核心概念缺 foundational citation：TKNN 陈数、Haldane 模型、Floquet 拓扑表征

- 位置：多处
- 问题：
  - "陈数 C(t)" 在全文出现 40+ 次，但奠基论文 [1] Thouless et al. 1982（TKNN）从未被引用。content.md 明确提到"TKNN 陈数"但仍未引 [1]。
  - "Haldane 模型""Floquet 拓扑相"在 §1.1、§2.2 多处讨论，[2] Haldane 1988 从未引用。
  - [4] Kitagawa et al. 2010"周期驱动量子系统的拓扑表征"与本项目 Floquet 拓扑主题直接对应，从未引用。
- 风险：重点项目评审专家必然关注拓扑物态基础——连 TKNN 和 Haldane 都不引，会被质疑学术严谨性。
- 建议：
  - 在正文首次定义"陈数 C(t)"处补引 [1]：如 rationale.md §1 问题一段落"瞬时陈数 C_n(t) 可作为瞬态拓扑不变量"后加 [1]
  - 在 §2.2 讨论 Floquet 拓扑相处补引 [2][4]
  - 在 content.md "TKNN 陈数"处补引 [1]
- action：add

### [high] H4 — 预印本占比 40.3%（25/62），超过 30% 阈值

- 位置：references.md [38]–[62]
- 问题：25 条 arXiv 预印本占总引用 40.3%。其中多条支撑核心论断：
  - [40] Liu et al. 全光重建技术——支撑 §2.3 Berry 曲率读取核心方法
  - [41] Chen et al. 深度学习量子轨迹——支撑 §2.3 反演方法
  - [58] Batista et al. 固体 HHG 螺旋度——支撑 content.md §2.2 子课题 B
  - [59] Mokhtari et al. 声子退相干——支撑 content.md §2.3 误差分析
  - [60] Ilin et al. 量子光学签名——支撑 content.md §3 Q3 第四类约束
- 风险：>30% 预印本且支撑核心论断，评审专家会质疑这些工作的可靠性（未经同行评审）。skill 专项检查第 6 条明确要求"若 >30% 须显著降权重或核实"。
- 建议：
  - 逐条核实 [40][41][58][59][60] 是否已被正式接收/发表，若已发表则更新为正式引用
  - 对仍为预印本的条目，正文引用时加限定语（如"据预印本报道"）
  - 考虑用已发表的同类工作替换部分预印本
- action：verify

### [high] H5 — [62] 作者署名"Anonymous"，引文不可核实

- 位置：references.md 第 125 行；scheme.md §2.3(a) 和 §5(3) 引用
- 问题：[62] 署名为"Anonymous. Physics-Informed Diffusion Models for Scientific Inverse Problems. arXiv:2603.24377 (2026)"。学术引用中不应出现"Anonymous"——这要么是双盲评审中的投稿（不应以作者名引用），要么是作者信息缺失/未核实。正文两处（scheme.md §2.3a 和 §5(3)）将其作为方法学参照引用。
- 建议：核实 arXiv:2603.24377 的真实作者信息并补全；若确为匿名/双盲投稿，应改为标注"作者匿名"并说明引用理由，或替换为已发表的同方向工作。
- action：verify

---

### [medium] M1 — 引文格式两套混用，不统一

- 位置：references.md 全文
- 问题：62 条参考文献存在两套格式：
  - 格式 A（完整版）：全作者列表 + 文章标题 + 期刊全名 + 卷页 + 年份 + DOI。如 [1][2][3][4][7][8][12][14][16][19][23][26][30]，共约 13 条。
  - 格式 B（简写版）："第一作者 et al." + 无标题 + 期刊全名 + 卷页 + 年份，多数无 DOI。如 [5][6][9][10][11][13][17][18][20]–[22][24][25][27]–[29][31]–[37]，共约 24 条。
  - 格式 C（预印本）："第一作者 et al." + 标题 + arXiv ID + 年份。如 [38]–[62]，共 25 条。
- 建议：统一为一种格式。NSFC 推荐使用"全作者（或前 3 作者 + et al.）+ 标题 + 期刊全名 + 卷, 页 (年) + DOI"。至少应为所有已发表文献补齐标题和 DOI。
- action：rewrite

### [medium] M2 — journal name 在 references.md 与 rationale.md 嵌入表间缩写不一致

- 位置：references.md vs rationale.md 嵌入表
- 问题：同一期刊在两份文件中使用了不同的缩写形式：
  | 编号 | references.md | rationale.md |
  |------|--------------|-------------|
  | [14] | Nature Photonics | Nat. Photonics |
  | [19] | Nature Physics | Nat. Phys. |
  | [22] | Nature Materials | Nat. Mater. |
  | [29] | Nature Communications | Nat. Commun. |
  | [31] | Nature Reviews Physics | Nat. Rev. Phys. |
  | [35] | Phys. Rev. Research | Phys. Rev. Res. |
- 建议：全文统一使用期刊全名（NSFC 不强制缩写格式，但同一份申请书内须一致）。
- action：rewrite

### [medium] M3 — 62 条参考文献总量偏高（重点惯例 30–50 条），含 8 条死引文

- 位置：references.md 全文
- 问题：用户指定检验标准为"15–30 篇区间（NSFC 面上项目惯例）"，本项目为 key（重点），惯例参考区间为 30–50 条。62 条超出上限，其中 8 条为死引文（见 H1），实际有效引用为 54 条。
- 建议：删除 8 条死引文后为 54 条，仍在偏高区间。建议进一步精简低相关性的预印本（如 [50] 未引用、[55][56][57] 未引用），将总量控制在 45–50 条。
- action：remove

### [medium] M4 — 缺失引用：Berry 曲率定义、Z₂ 不变量定义首次出现无 foundational citation

- 位置：rationale.md §1（首次定义拓扑量段落）
- 问题：Berry 曲率 Ω(k)、Z₂ 不变量 ν 在全文频繁使用，但首次出现时未引用奠基文献。Berry 曲率的原始定义应引 Berry 1984（M. V. Berry, Proc. R. Soc. Lond. A 392, 45 (1984)），Z₂ 不变量的原始定义应引 Kane & Mele 2005（PRL 95, 146802）。这两篇 foundational paper 完全缺失。
- 建议：在首次定义处补引。若已有 [1][2] 覆盖部分基础，至少补充 Berry 1984。
- action：add

---

### [low] L1 — [43] 与 [44] 标题不完全一致，同一 arXiv ID 对应两个不同标题

- 位置：references.md [43] 第 87 行、[44] 第 89 行
- 问题：同一 arXiv:2503.07256，[43] 标题为"Ultrafast phase retrieval in strongly driven solids: from HHG spectroscopy to quantum tomography"，[44] 标题为"Ultrafast phase retrieval in strongly driven solids"。前者有副标题，后者无。
- 建议：解决 C2 后此问题自动消解。
- action：remove

---

## 对抗结论

### 本轮发现统计

- 总计 13 个问题（critical: 2, high: 5, medium: 4, low: 1 + 1 from C2 subsumed）
- 扣分构成：critical 问题直接拉低严谨性至 0.62；预印本比例与死引文拉低完整性至 0.80

### 按检查项汇总

| 检查项 | 发现 | 严重度 |
|--------|------|--------|
| 1. 引文格式 | 两套格式混用；Nature 系列期刊名缩写不一致 | medium × 2 |
| 2. 编号一致性 | [12] 两版本为不同论文；[43]/[44] 矛盾；8 条死引文；嵌入表缺 8 条 | critical × 2 + high × 2 |
| 3. 引用相关性 | [55][56][57] 与正文无关联；[62] 匿名不可核实 | high × 2 |
| 4. 缺失引用 | TKNN/Haldane/Berry/Z₂ foundational citation 缺失 | high × 1 + medium × 1 |
| 5. 引用数量 | 62 条偏高，8 条死引文 | medium × 1 |
| 6. 时效性 | 时效性好（2023–2026 占 58%）；预印本 40.3% 偏高 | high × 1 |

### 是否达到输出标准

**否。** 参考文献存在 2 个 critical 级错误（[12] 引文归属错误、[43]/[44] 引用矛盾），且 foundational citation（TKNN/Haldane/Berry）缺失，预印本比例超标。这些问题在重点项目评审中会被直接质疑学术规范。

### 返工优先级

- **P0（必须立即修复）**：
  1. C1：修正 rationale.md [12] 为正确期刊/卷号/年份
  2. C2：解决 [43]/[44] 矛盾，统一引用
  3. H3：在正文首次定义处补引 [1] TKNN、[2] Haldane、[4] Kitagawa
- **P1（本轮内修复）**：
  4. H1：处理 8 条死引文（补引用或删除）
  5. H2：同步 references.md 与 rationale.md 嵌入表
  6. H4：核实预印本发表状态，降低预印本比例
  7. H5：核实 [62] 作者信息
- **P2（后续轮次）**：
  8. M1–M4：统一引文格式、journal name 缩写、精简总量

### 下一轮建议聚焦

- 修复 P0 后做一轮引用一致性复检
- 重点核实 [38]–[62] 预印本的正式发表状态
- 确认最终提交使用哪份文献表（references.md 还是 rationale.md 嵌入表），二者必须完全一致

---

## 评分
创新性：N/A
可行性：N/A
严谨性：0.62
完整性：0.80
综合评分：0.71
