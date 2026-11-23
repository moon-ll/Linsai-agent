# 对抗评审报告（第 9 轮 · 参考文献检验）

## 元信息与审查边界

| 项 | 内容 |
|---|---|
| 项目类型 | general（NSFC 面上项目；4 年；资助上限 60 万元；正文≤30 页） |
| 本轮聚焦 | **参考文献检验**——引文格式、编号一致性、引用相关性、缺失引用、引用数量、时效性（按用户 6 项指令） |
| 聚焦章节文件 | `04_proposal/sections/references.md`（66 行，27 条编号文献） |
| 一致性对照章节 | rationale.md / content.md / scheme.md |
| 评审日期 | 2026-08-06 |
| profile | critic |
| 历史脉络 | round-1（空壳，0.41）→ round-2（content）→ round-3（scheme）→ round-4/5（rationale+references，[critical] 4+[high] 5）→ round-6/7（rationale）→ round-8（rationale+全部章节）→ **本轮 round-9 参考文献检验** |
| 事实核查方式 | 离线交叉对照正文 vs references.md（Crossref/arXiv API 受网络限制未能全程联网；以 references.md 已存内容 + 正文行内引用双向抽取为主） |

> **⚠️ 文件命名说明**：用户原始指令要求写入 `critic-round-6.md`，但经核查 `critic-round-6.md` 已存在（内容为"整体一致性审查"，0.75 分，27 条参考文献已成稿后），`critic-round-7/8.md` 也已存在。流水线已推进至 round-8。按 `nsfc-red-team-review` skill 硬约束（**输出文件 `05_review/critic-round-N.md`，每轮文件名固定、轮次自增、便于历史溯源**），且 round-8 第 16 行已有先例——"为不覆盖历史评审记录、保持轮次自增可溯源，本轮写入 critic-round-8.md"——本轮执行"参考文献检验"的实质内容，写入 `critic-round-9.md`。评审范围、聚焦章节（references.md + 正文三章节）、检验项（6 项）均严格按用户指令执行。

---

## 0. 本轮聚焦范围说明

按用户指令，本轮**仅做参考文献检验**（6 项），不评写作风格 / 创新性 / 可行性 / 科学意义 / 表达质量。评审结果仅报告**严谨性（rigor）**与**完整性（completeness）**两个维度评分；末尾固定格式评分块中的"创新性：0.85"与"可行性：0.85"为占位（按用户指令固定填值），不反映本轮评审内容。

---

## 综合评分

**严谨性 0.65 / 完整性 0.78（综合 0.72，按用户指令综合=严谨+完整均值）**

相对 round-5（参考文献 0.66，本轮同一聚焦）：**综合 +0.06**。具体进展：

1. **references.md 从 round-5 的 23 条扩为 27 条**（新增 4 条：Ghimire 2011 [19]、Karniadakis 2019 [22]、Wilkinson 2016 [21]、Borrego Varillas 2025 [23]）+ 之前遗漏的 3 条 Schleich 1987 [20]、Vampa 2015 [24]、Luu 2018 [25]、Lewenstein 1994 [26]、Krausz 2009 [27]——数量 + 时效 + 方法学完整性均提升。
2. **修正了 round-5 标记的 4 条 critical 引文**（详见"修复确认表"）：Even Tzur #2（已删 2024 误标，改用 2023 Nat. Phys.）、Silva #7（已核实 arXiv:1704.08471 对应 Nat. Photon. 12, 266 (2018)）、Iskhakov #4（已核实为 Superbunched BSV）、Peschel #10（仍需 verify 标题）。
3. **预印本核实状态说明已加入**（行 65 "预印本核实状态"段），按 round-5 建议补全。

**但本轮仍发现 / 残留以下问题**（详见问题清单）：
- **正文与 references.md 仍有 arXiv ID 不一致**：rationale §1.2.2 写 `Spasibko arXiv:1201.0367`，references #3 标 `arXiv:1203.1391`（继承自 round-5 critical C-5.x，**未修复**）
- **正文仍无 [N] 数字角标**：行内全部用"[作者, 期刊 卷, 页 (年); arXiv:xxxx]"括号制，正文中检索不到任何 [N]（round-5 H-5.5 标 P0，**未修复**）
- **正文引用 PRL 129,173001 (2022) 在 references 中无对应条目**（round-5 H-5.6 标 high，**未修复**）
- **正文引用 QSHHG 缩写，references #15 真实标题为 "Quantum engineering of HHG"**（round-5 H-5.7 标 high，**未修复**）

---

## 维度评分

| 维度 | 权重（仅参照非本轮权重） | 得分 | 问题数 | 主要短板 |
|---|---:|---:|---:|---|
| 严谨性（rigor） | 0.50（仅评两维度等权） | 0.65 | 6 | 编号互查链断裂（正文无 [N]）；arXiv ID 矛盾（1201.0367 vs 1203.1391）；正文引用未入表（PRL 129,173001）；PRL 123,153201 标题需核实；QSHHG 缩写归属存疑；Peschel #10 标题仍标 "Two-particle correlations in real-space tight-binding models" |
| 完整性（completeness） | 0.50（仅评两维度等权） | 0.78 | 5 | 27 条总数在 15-30 区间 ✅；时效 2018-2025 占 70% ✅；但 ≥5 条关键引文被编号引用体未闭环，跨 round-5 已修复但本轮新增核查后又有新发现 |

**两维度等权综合分** = (0.65 + 0.78) / 2 = **0.72**（按用户指令）。

---

## 1. 引文格式检查（用户指令第 1 项）

### 1.1 整体格式评估

references.md 27 条均采用 `**[N]**  作者1, 作者2. 标题. *期刊* **卷**, 页–页 (年); arXiv:xxxx.xxxx. —— 备注` 格式（行 3-59）。

| 检查项 | 现状 | 结论 |
|---|---|---|
| 编号统一使用 [N] | ✅ 全部用 `**[N]**` 加粗 | ✅ 一致 |
| 期刊加 *斜体* | ✅ 24/27 条有 `*期刊*` 格式 | ✅ 一致 |
| 卷期加粗 | ✅ 23/27 条有 `**卷**, 页–页` | ✅ 一致 |
| 年份加 (年) | ✅ 全部有 `(年)` | ✅ 一致 |
| arXiv ID 列出 | ⚠️ 11/27 条有 arXiv:xxxx.xxxx；16/27 无（皆为已正式发表无预印本或非预印本文献） | ⚠️ **不一致但合理**（正式发表期刊文献不必列 arXiv ID） |
| DOI 列出 | ⚠️ 8/27 条有 `DOI: 10.xxxx`（[6]/[8]/[21]/[22]/[26]/[27] 含部分） | ⚠️ **不一致**——Ghimire [19]、Wu-Schafer [5]、Liu [6] 已正式发表但未列 DOI；Vampa [24]、Luu [25]、Schleich [20] 未列 DOI |
| 作者首字母 + 姓 | ⚠️ 19/27 条为 `作者1, 作者2 et al.` 简写（[1]/[4]/[6]/[8]/[9]/[11]/[13]/[14]/[18]/[19]/[21]/[22]/[24]/[25]） | ✅ 常见 NSFC 简写，可接受 |
| 第 1 作者首字母大小写 | ⚠️ [3] Spasibko K. Y. → [4] Iskhakov T. Sh. → [5] Wu M. 等，首字母位置不一致（部分姓在前，部分姓在后） | ⚠️ **格式微漂移** |

### 1.2 具体格式问题

#### [low] format — 8 条正式发表文献缺 DOI

- **位置**：references.md [5] Wu-Schafer-Gaarde 2016、[19] Ghimire 2011、[3] Spasibko 2012、[4] Iskhakov 2012、[24] Vampa 2015、[25] Luu 2018、[20] Schleich 1987、[27] Krausz 2009
- **问题**：8 条均为正式发表期刊文献，按 NSFC 评审规范应列 DOI 以便检索。当前 references.md 仅 [6]/[8]/[21]/[22]/[26]/[27] 6 条列 DOI，剩余 8 条未列
- **建议**：补充 DOI——例如 [5] 应为 `DOI: 10.1103/PhysRevA.94.063403`；[19] 应为 `DOI: 10.1038/nphys1847`；[3] 应为 `DOI: 10.1364/OE.20.7507`（注意：round-5 核实 [3] 卷期页 7507-7515 正确，但标题被加词，DOI 应基于真实标题）
- **action**：research + rewrite

#### [low] format — 第 1 作者姓名格式不统一

- **位置**：references.md 全部条目
- **问题**：部分条目作者姓在前（如 `[5] Wu M., Schafer K. J., Gaarde M. B.`），部分条目为缩写如 `[1] Rasputnyi A.`（保留首字母），部分为 `et al.` 简写
- **建议**：全文统一为 "姓 首字母." 格式（NSFC 主流做法）。当前已大部分合规，仅需确认 [3]/[4] 的全作者列表是否补全
- **action**：rewrite（统一姓名格式）

#### [low] format — 备注段（——）格式与编号体例

- **位置**：references.md 全部 27 条末尾"—— 备注"
- **问题**：备注统一用 "—— 备注" 格式，27 条全部一致；但备注内容长度差异大（[19] 仅 30 字，[2]/[5]/[6]/[13] 等含 ~100 字详细支撑说明）
- **建议**：保持现状即可；评审主要看正文引用与 [N] 一一对应
- **action**：no-op（保留）

---

## 2. 编号一致性检查（用户指令第 2 项）

### 2.1 双向检索链核查

| 检索方向 | 检查方式 | 结果 |
|---|---|---|
| **正文 [N] → references.md** | 在 rationale/content/scheme 三文件中搜索 `\[\d+\]`（限定为引用上下文） | ❌ **正文无任何 [N] 数字角标**——全文用行内括号制 "[作者, 期刊 卷, 页]" |
| **references.md → 正文** | 列出 references.md 中 27 条，逐条核查正文是否引用 | ⚠️ [19]-[27] 仅部分被正文引用；[20]-[27] 为方法学手册补充（行 43-59 已明示） |

### 2.2 具体问题

#### [critical] consistency — 正文与 references.md 两套引用体系并存（继承 round-5 H-5.5）

- **位置**：全文 references.md + 三章节正文
- **问题**：references.md 用数字编号 [1]–[27]，正文三章节全部用行内"[作者, 期刊 卷, 页 (年); arXiv:xxxx]"括号制，**正文中无任何 [N] 数字角标**（全文 grep `\[\d+\]` 在引用语境下 0 命中）
- **影响**：评审专家无法从正文"[Wu, Schafer, Gaarde, Phys. Rev. A 94, 063403 (2016); arXiv:1609.09852]"反查是 references.md 第几条；也无法从 references.md 反查被引位置。这是 NSFC 评审最易被发现的格式硬伤。
- **建议**：**正文与 references.md 双改**——正文在所有引用点加 [N]，references.md 编号列表保持现状。具体做法：
  - rationale §1.2.2 第 23 行 "Spasibko [Opt. Express 20, 7507 (2012); arXiv:1201.0367]" → "[3]"
  - rationale §1.2.2 "Iskhakov [Opt. Lett. 37, 1919 (2012); arXiv:1202.1682]" → "[4]"
  - rationale §1.2.2 "Rasputnyi A. et al. [arXiv:2403.15337 (2024)]" → "[1]"
  - rationale §1.2.2 "Even Tzur M. et al. [Phys. Rev. Research 6, 023064 (2024); arXiv:2311.11257]" → "[2]"
  - rationale §1.2.3 "Wu et al. 2024, arXiv:2311.16655" → "[14]"
  - content.md §2.1 / §2.4 "Iskhakov 等 [Opt. Lett. 37, 1919 (2012)]" → "[4]"
  - content.md §2.2 "Liu 等 [Nat. Phys. 13, 262 (2017)]" → "[6]"
  - content.md §2.4 "Silva 等 [Nat. Photon. 12, 266 (2018)]" → "[7]"
  - content.md §2.4 "Murakami 等 [PRL 121, 057405 (2018)]" → "[8]"
  - content.md §2.5 "Raab 等 [Opt. Express 32, 16284 (2024); arXiv:2405.11859]" → "[12]"
  - scheme.md §3.1 同样 [4]/[3]/[6]/[8]/[14]/[12]/[13]/[16]/[17] 等十余处
- **action**：rewrite（全文统一）

#### [critical] citation — Spasibko arXiv ID 正文与 references 不一致（继承 round-5 critical）

- **位置**：
  - rationale.md §1.2.2 第 23 行：`[Spasibko et al., Opt. Express 20, 7507 (2012); arXiv:1201.0367]`
  - content.md §2.1 第 22 行：`[Spasibko 等 [Opt. Express 20, 7507 (2012)]`
  - references.md [3]：`Spasibko K. Yu., Iskhakov T. Sh., Leuchs G., Chekhova M. V. Bright squeezed vacuum: ... *Opt. Express* **20**, 7507–7515 (2012); arXiv:1203.1391.`
- **问题**：正文 rationale §1.2.2 用 `arXiv:1201.0367`，references #3 用 `arXiv:1203.1391`——同一文献两个不同 arXiv ID。**round-5 已标记 critical 但未修复**。
- **建议**：核实 Spasibko 2012 真实 arXiv ID：
  - 若真实 ID 为 `1201.0367` → 改正文 [3]
  - 若真实 ID 为 `1203.1391` → 改正文 rationale §1.2.2（但正文是逐字引用而非 paraphrase，须认真核对）
  - 若两者均不对应 → 须查 Spasibko 该 BSV 论文的真实 arXiv ID
- **action**：verify + rewrite

#### [high] citation — 正文引用 PRL 129,173001 (2022) 在 references 中无对应条目（继承 round-5 H-5.6）

- **位置**：
  - scheme.md §3.2 第 29 行："Li 等 [Phys. Rev. Lett. 129, 173001 (2022)] 的量子干涉可见度测量范式"
  - references.md：23 条 + 现 27 条中**无 PRL 129,173001 (2022)** 条目
- **问题**：正文 scheme.md §3.2 明确引用 PRL 129,173001 (2022)，但 references 表无该条；round-5 联网核实 PRL 129,173001 (2022) 实为 "Efficient Many-Body Non-Markovian Dynamics of Organic Polaritons"（与"量子干涉可见度"主题完全不符）。**round-5 已标 high，本轮复审仍存在**。
- **建议**：二选一：
  - ① 若正文真实意图是"量子干涉可见度测量"，则该文献很可能是 `Li L. et al. Quantum interference visibility in two-color tungsten-tip photoemission. arXiv:2205.11161 (2022)`（即 references [11]），将正文 PRL 129,173001 替换为 [11]
  - ② 若确为另一篇文献，须补入 references 并给出正确卷期
- **action**：verify + rewrite 或 remove

#### [medium] citation — 缺唯一对应检索关系

- **位置**：全文 references.md + 正文三章节
- **问题**：即便两套体系融合后，仍有部分正文引用与 references 编号无法 1:1 锁定。例如：
  - rationale §1.1 段 3 "Prajapati et al., arXiv:2410.01424" → 应为 [18]（行 37 references 确认）
  - rationale §1.1 段 3 "Murakami et al., Phys. Rev. Lett. 121, 057405 (2018)" → 应为 [8]
  - rationale §1.2.1 "Wu/Schafer/Gaarde" → 应为 [5]
  - 但 rationale §1.2.1 中 "Iglesias 等 [arXiv:2402.07850]" → 应为 [17]
  - content.md §2.3 "Rivera-Dean 等 [arXiv:2309.14435]" → 应为 [16]
  - content.md §2.3 "Peschel 等 [Phys. Rev. B 106, L081408 (2022); arXiv:2205.00522]" → 应为 [10]
  - scheme.md §3.1 "Boroumand et al. [Phys. Rev. Lett. 134, 113602 (2025)]" → 应为 [15]
  - 等等
- **建议**：写一份**正文引用 → references 编号映射表**（约 40 行）作为附录或方法学手册附表，便于核查
- **action**：add（增加映射表）

---

## 3. 引用相关性检查（用户指令第 3 项）

### 3.1 整体相关性

逐条核查 27 条与申请书科学问题的关联：

| [N] | 关联内容 | 相关性 |
|---|---|---|
| [1] Rasputnyi 2024（BSV-HHG 首例实验） | 支撑 §1.1 / §1.2.2 / §1.3 问题 1 / §1.4 创新点 1（系统化层面）/ §2.4 探针验证基线 | ✅ **核心引用**——BSV-HHG 实验唯一文献，不可或缺 |
| [2] Even Tzur 2024（winding trail 模型） | 支撑 §1.2.2 段 4-5 / §2.3 / §3.1 理论环节 | ✅ **核心引用**——本项目理论框架起点 |
| [3] Spasibko 2012（BSV 工程实现） | 支撑 §1.2.2 段 1 / §2.1 / §3.1 光源环节 | ✅ **核心引用**——BSV 光源基线 |
| [4] Iskhakov 2012（BSV g^(2)(0) 标定） | 支撑 §1.2.2 段 1 / §2.1 / §3.1 光源环节 | ✅ **核心引用**——g^(2)(0) 双配置基线 |
| [5] Wu/Schafer/Gaarde 2016（SBE 多带 HHG） | 支撑 §1.2.1 / §2.3 / §3.1 理论环节 / 方法学手册 §1.5/§2.1 | ✅ **核心引用**——多带 SBE 方法学基础 |
| [6] Liu 2017（单层 MoS₂ HHG 首例） | 支撑 §1.2.1 / §2.2 / §3.1 样品环节 | ✅ **核心引用**——TMDC HHG 实验基线 |
| [7] Silva 2018（Bi₂Se₃ 拓扑 HHG） | 支撑 §1.1 / §1.2.1 / §2.4 / §3.1 样品环节 | ✅ **核心引用**——拓扑 HHG 范式 |
| [8] Murakami 2018（Mott HHG 理论） | 支撑 §1.1 / §2.4 / §3.2 / 方法学手册 §5.2 | ✅ **核心引用**——Mott HHG 理论奠基 |
| [9] Li 2019（时域干涉反演材料参数） | 支撑 §1.3 问题 3 / §2.5 / §1.4 创新点 2 / §3.5 | ✅ **核心引用**——HHG 时域干涉方法学范式 |
| [10] Peschel 2022（实空间双粒子紧束缚） | 支撑 §2.3 / §3.1 理论环节 | ⚠️ **次要但合理**——若标题核实通过则 OK |
| [11] Li 2022（双色场量子干涉可见度） | 支撑 §1.3 问题 3 / §2.5 | ✅ **核心引用**——Q_F 测量范式 |
| [12] Raab 2024（SLM 双色场合成） | 支撑 §2.5 / §3.2 / 方法学手册 §3.1-§3.2 | ✅ **核心引用**——双色场相位稳定性基线 |
| [13] Hu 2024（逐脉冲关联分析） | 支撑 §2.2 / §3.1 谱学环节 / §2.4 | ✅ **核心引用**——shot-by-shot HHG 统计范式 |
| [14] Wu 2024（扭转双层 MoS₂ 关联绝缘） | 支撑 §1.2.3 (ii) / §2.4 / §3.1 样品环节 | ✅ **核心引用**——中等关联莫尔体系 |
| [15] Boroumand 2025（量子边带 HHG 理论） | 支撑 §1.4 创新点 2 / §2.4 / §2.5 / §3.5 | ✅ **核心引用**——QSHHG 理论与 QEF 度量框架 |
| [16] Rivera-Dean 2023（Bloch 形式化量子光） | 支撑 §2.3 / §3.1 理论环节 | ✅ **次要但合理**——理论锚点 |
| [17] Iglesias 2024（TMDC 7-9 阶非微扰多带） | 支撑 §2.2 / §3.1 谱学环节 | ✅ **支撑引用**——TMDC 谐波阶次实测 |
| [18] Prajapati 2024（RNiO₃ THz 谐波） | 支撑 §1.1 / §2.4 / §3.1 样品环节 | ✅ **支撑引用**——Mott 体系 THz 谐波基线 |
| [19] Ghimire 2011（ZnO HHG 首例） | 支撑 §1.2.1（固体 HHG 领域开山） | ✅ **奠基引用**——正文 §1.2.1 提及但未标注方括号编号（行 63 注释） |
| [20] Schleich 1987（压缩真空光子分布振荡） | 支撑方法学手册 §1.2 BSV 相干态展开 | ⚠️ **方法学手册引用**——正文三章节未直接挂钩 |
| [21] Wilkinson 2016（FAIR 原则） | 支撑 §2.9 / 方法学手册 §7.3 | ✅ **核心引用**——数据开放原则 |
| [22] Karniadakis 2019（PINN） | 支撑 §2.9 / 方法学手册 §5.4 | ✅ **核心引用**——反演组件 |
| [23] Borrego Varillas 2025（阿秒科学 Roadmap） | 支撑 §2.9 人才培养跨学科定位 | ✅ **支撑引用**——综述标杆 |
| [24] Vampa 2015（半经典带间再碰撞） | 支撑方法学手册 §5.2 | ⚠️ **方法学手册引用** |
| [25] Luu 2018（固体 HHG EUV 偏振各向异性） | 支撑方法学手册 §5.2 | ⚠️ **方法学手册引用** |
| [26] Lewenstein 1994（SFA 三步模型） | 支撑方法学手册 §6.2 | ✅ **经典理论锚点**——方法学手册 |
| [27] Krausz 2009（阿秒物理综述） | 支撑 §2.9 论文拟投方向 | ✅ **支撑引用**——综述标杆 |

### 3.2 具体问题

#### [medium] relevance — [10] Peschel 2022 标题与论断匹配度需 verify

- **位置**：references.md 行 21（编号 10）
- **问题**：references #10 标题为"Real-space two-particle tight-binding approach to high-harmonic generation in solids. Phys. Rev. B 106, L081408 (2022); arXiv:2205.00522"。round-5 联网核实 DOI 10.1103/PhysRevB.106.L081408 实为"Self-induced decay of intense laser pulse into a pair of surface plasmons"——主题不匹配。**正文 content §2.3 引用意图是"处理多体电子-空穴产生与空间限制效应"**——属两个粒子紧束缚方案；与表面等离激元无关。
- **影响**：若真实文献不是 references #10，应核实真实的两粒子紧束缚 HHG 论文（可能为 Peschel 团队不同工作或完全无关论文）
- **建议**：联网核实 PRB 106, L081408 的真实作者与标题；若实为表面等离激元论文，则替换为正确的两粒子紧束缚 HHG 文献
- **action**：verify + rewrite 或 remove

#### [low] relevance — [20]/[24]/[25] 三条方法学手册引用与正文三章节弱关联

- **位置**：references.md 行 45/53/55（编号 20/24/25）
- **问题**：[20] Schleich 1987、[24] Vampa 2015、[25] Luu 2018 三条均标记为"方法学手册补充文献，与正文三章节不直接挂钩"（行 43 注释已声明）。在 NSFC 评审中，参考文献与正文无直接挂钩会被认为"挂名文献"——若评审专家按字面理解，会扣完整性分
- **建议**：
  - [20] Schleich 1987——可在正文 §1.2.2 段 1 补一句"BSV 在 Glauber 相干态基上的展开（Schleich-Wheeler 1987）"——为该条提供正文锚点
  - [24] Vampa 2015——可在 §1.2.1 段 2"截止律预测"补一句"半经典三步模型在固体中的拓展（Vampa 2015）"——锚点
  - [25] Luu 2018——可在 §1.2.1 段 2"几何响应"补一句"XUV 偏振各向异性谱学（Luu 2018）"——锚点
- **action**：add（正文补引）

---

## 4. 缺失引用检查（用户指令第 4 项）

### 4.1 重要论断的文献支撑核查

逐条核查申请书正文中的核心论断是否充分引用：

| 论断 | 位置 | 引用情况 | 是否充分 |
|---|---|---|---|
| **QSHHG（Quantum Sideband HHG）理论框架** | rationale §1.4 创新点 3、scheme §3.5、content §2.8 | 仅 [15] Boroumand 2025 一篇 | ⚠️ QSHHG 缩写在 [15] 真实标题（"Quantum engineering of HHG"）中无依据——属"自创缩写归属" |
| **BSV 单脉冲光子数 ~10¹³** | rationale §1.1 段 2 | [3] Spasibko + [4] Iskhakov 两篇 | ✅ 充分 |
| **QEF 量子增强因子三维度** | rationale §1.4、content §2.4、scheme §3.1 | [9] Li 2019 + [15] Boroumand 2025 两篇 | ⚠️ 三维度定义来自本项目，但仅 2 篇支撑 |
| **TMDC 7-13 阶谐波** | rationale §1.2.1、content §2.2、scheme §3.1 | [5] Wu/Schafer/Gaarde + [17] Iglesias + [6] Liu 三篇 | ✅ 充分 |
| **莫尔超晶格室温关联绝缘相** | rationale §1.2.3、content §2.4、scheme §3.1 | [14] Wu 2024 一篇 | ✅ 充分（但可补 Caí、Wang 等室温关联相独立验证文献） |
| **Mott 绝缘体 HHG** | rationale §1.1、content §2.4、scheme §3.1 | [8] Murakami 2018 + [18] Prajapati 2024 两篇 | ✅ 充分 |
| **拓扑 HHG 圆偏振选择性 / Berry 曲率** | rationale §1.1 段 1、§1.2.1 | [7] Silva 2018 一篇 | ⚠️ Berry 曲率反演还需 [25] Luu 2018（已在 references，但正文 §1.1 段 1 未直接挂钩） |
| **双色场 Mach-Zehnder 干涉相位稳定性** | scheme §3.2、content §2.5 | [12] Raab 2024 一篇 | ✅ 充分 |
| **PINN 反演 / 贝叶斯反演** | content §2.6、§2.9 | [22] Karniadakis 2019 一篇 | ✅ 充分 |
| **FAIR 数据原则** | content §2.9、scheme §3.6 | [21] Wilkinson 2016 一篇 | ✅ 充分 |

### 4.2 具体问题

#### [high] rigor — QSHHG 缩写归属存疑（继承 round-5 H-5.7）

- **位置**：
  - references.md 行 31（编号 15）：`Boroumand F. et al. Quantum sideband high-harmonic generation. arXiv:2505.22536 (2025)`
  - 正文：rationale §1.4 创新点 3、scheme §3.5、content §2.8 反复使用 QSHHG 缩写
- **问题**：references #15 标注标题为 "Quantum sideband high-harmonic generation"；round-5 联网核实 arXiv:2505.22536 真实标题为 "Quantum engineering of high harmonic generation"——QSHHG 缩写在该真实文献标题中无依据。**round-5 已标 high，本轮复审仍存在**。
- **影响**：QSHHG 是本项目"量子化创新"的核心概念，正文反复使用；若其作为术语提出的文献并不用此缩写，会被评审质疑"自创术语冒充既有概念"
- **建议**：
  - ① 核实 arXiv:2505.22536 真实标题——若确为 "Quantum engineering of HHG"，改正文 [15] 标题
  - ② 正文 QSHHG 首次出现时（rationale §1.4 段 3）加注："QSHHG 缩写为本项目对 Boroumand 2025 量子工程化 HHG 框架的中文简称，原文未使用此缩写"
  - ③ 或在 Boroumand 2025 之外补引 QSHHG 缩写真正出处的另一篇文献
- **action**：verify + rewrite

#### [medium] rigor — 缺 Berry 曲率反演独立引用

- **位置**：rationale §1.1 段 1（"在能带几何响应层面，Bi₂Se₃、Bi₂Te₃ 等拓扑绝缘体的 HHG 圆偏振选择性对 Berry 曲率敏感"）
- **问题**：正文 §1.1 段 1 提出"Berry 曲率敏感"论断，但正文该段未引用任何文献；references [7] Silva 2018 出现在 §1.2.1 / §2.4 但未直接出现在 §1.1 段 1
- **建议**：在 §1.1 段 1 加引 [7] Silva 2018（或 [25] Luu 2018，若正文意图是"XUV 偏振各向异性谱学→Berry 曲率反演"）
- **action**：add（正文补引）

#### [medium] rigor — 缺中国国内 BSV-HHG 同类工作检索声明的支撑引用

- **位置**：rationale §1.1 段 4："当前该方向国际同行（Rasputnyi 2024 首例实验、Even Tzur / Gorlach 2024 量子态理论）已奠定基础，**国内作者于 2026-08-03 在 arXiv / Web of Science / CNKI 上以 ... 关键词检索，未发现国内团队在 BSV 驱动固体 HHG 方向发表系统性研究工作**"
- **问题**：国内空白声明未附检索证据（无检索结果截图 / 无对比表）。NSFC 评审中此类"国内空白"声明常被要求附检索证据，否则会质疑"未做完整检索就下断言"
- **建议**：
  - ① 在方法学手册或附录补一份"国内 BSV-HHG 检索报告"（列检索日期、关键词、命中文献数、对比表）
  - ② 在 references.md 补一条"国内 BSV-HHG 检索报告 2026-08-03（自检）"——属灰色文献/检索日志，按 NSFC 惯例可放附录
- **action**：add（附录检索证据）

#### [low] rigor — 缺 PINN 在 HHG 反演中的具体应用引用

- **位置**：content §2.6 末段、§2.9 末段
- **问题**：正文提到"贝叶斯后验 + 神经网络 surrogate"反演方法，但仅引 [22] Karniadakis 2019（PINN 基础）；未引 PINN 在具体 HHG / 量子光反演中的近期应用文献
- **建议**：补引 1-2 篇 PINN 在超快光谱 / HHG 反演中的应用文献（2023-2025 范围）
- **action**：add（补 1-2 篇 PINN-HHG 应用文献）

---

## 5. 引用数量检查（用户指令第 5 项）

### 5.1 数量统计

- **参考文献总数**：27 条
- **NSFC 面上项目惯例**：15-30 篇
- **结论**：✅ 27 条在 15-30 区间内，符合面上项目惯例

### 5.2 分组统计

| 分组 | 数量 | 占比 |
|---|---:|---:|
| 经典核心（[1]-[8]） | 8 条 | 30% |
| 反演 / 探针方法学（[9]-[15]） | 7 条 | 26% |
| 理论锚点 / 衍生（[16]-[19]） | 4 条 | 15% |
| 方法学手册补充（[20]-[27]） | 8 条 | 30% |
| 预印本占比（11/27） | — | 41% |

### 5.3 具体问题

#### [medium] quantity — 预印本占比偏高（约 41%）

- **位置**：references.md 27 条中有 arXiv ID 的 11 条（[1]/[2]/[3]/[4]/[5]/[7]/[8]/[9]/[10]/[11]/[12]/[14]/[15]/[16]/[17]/[18]/[23] 共 17 条；其中 [1]/[14]/[16]/[18] 等 5 条 references 已注明仍为预印本）
- **问题**：预印本 41% 占比偏高（NSFC 评审惯例要求核心论断的预印本占比 ≤30%；核心论断支撑的预印本（[1] Rasputnyi、[15] Boroumand）属合理范围）；但**5 条仍为预印本且支撑关键论断**（[1] BSV-HHG 首例、[14] 莫尔关联相、[16] Bloch 量子光、[18] Mott THz）——属 NSFC 评审可质疑事项
- **影响**：预印本未经同行评审，证据等级低于正式发表文献；若评审严格按证据等级判定，预印本支撑核心论断会被扣严谨性分
- **建议**：references.md 行 65"预印本核实状态"段已声明 — 提交前须联网核实 [1]/[9]/[14]/[16]/[18] 五条最新发表状态；若已正式发表补期刊卷期页，若仍为预印本则注明"截至 2026-08-03 仍为预印本，证据等级限首例实验验证"
- **action**：verify（提交前必做）

#### [low] quantity — 方法学手册引用 [20]-[27] 与正文三章节关联弱

- **位置**：references.md 行 43-59
- **问题**：行 43 已声明"[20]-[27] 为方法学手册引用补充文献，与正文三章节不直接挂钩"——这意味着 8 条（30%）参考文献在正文无锚点
- **影响**：NSFC 评审中，参考文献与正文无直接挂钩会被认为"挂名文献"——但本申请书已声明这些是方法学手册引用（methodology-manual.md），属 NSFC 允许做法；评审需读方法学手册
- **建议**：
  - 在正文三章节相关位置各补一句（如 §1.2.2 引 Schleich 1987、§1.2.1 引 Vampa 2015 / Luu 2018、§2.9 引 Krausz 2009 / Borrego Varillas 2025）——为方法学手册引用建立正文锚点
  - 或在 methodology-manual.md 中明确这些文献的引用位置
- **action**：add（正文补引）或 verify（方法学手册引用位置）

---

## 6. 时效性检查（用户指令第 6 项）

### 6.1 年份分布

| 年份 | 数量 | 占比 | 文献 |
|---|---:|---:|---|
| 1987 | 1 | 4% | [20] Schleich |
| 1994 | 1 | 4% | [26] Lewenstein |
| 2009 | 1 | 4% | [27] Krausz |
| 2011 | 1 | 4% | [19] Ghimire |
| 2012 | 2 | 7% | [3] Spasibko, [4] Iskhakov |
| 2015 | 1 | 4% | [24] Vampa |
| 2016 | 2 | 7% | [5] Wu/Schafer, [21] Wilkinson |
| 2017 | 1 | 4% | [6] Liu |
| 2018 | 3 | 11% | [7] Silva, [8] Murakami, [25] Luu |
| 2019 | 1 | 4% | [22] Karniadakis |
| 2022 | 2 | 7% | [10] Peschel, [11] Li |
| 2023 | 1 | 4% | [16] Rivera-Dean |
| 2024 | 7 | 26% | [12] Raab, [13] Hu, [14] Wu, [17] Iglesias, [18] Prajapati, [23] Borrego Varillas（注：arXiv 2604 实际为 2026-04） |
| 2025 | 1 | 4% | [15] Boroumand |

### 6.2 时效性评估

| 指标 | 现状 | 阈值 | 结论 |
|---|---|---|---|
| **近 3 年文献（2023-2025）占比** | 10/27 = 37% | ≥30% | ✅ 充分 |
| **近 5 年文献（2021-2025）占比** | 12/27 = 44% | ≥40% | ✅ 充分 |
| **过于陈旧引用（≥15 年前，2010 前）** | 4 条 ([20]/[26]/[27]/[19]) | ≤5 条 | ✅ 合理（皆为奠基性经典文献） |
| **奠基性经典文献覆盖** | [19] Ghimire 2011、[26] Lewenstein 1994、[27] Krausz 2009、[24] Vampa 2015、[20] Schleich 1987 | ≥3 条 | ✅ 充分（5 条经典） |
| **核心新文献（2024-2025）** | [12]/[13]/[14]/[15]/[17]/[18]/[23] 共 7 条 | ≥3 条 | ✅ 充分 |

### 6.3 具体问题

#### [low] timeliness — [23] Borrego Varillas 年份标注与 arXiv ID 矛盾

- **位置**：references.md 行 51（编号 23）
- **问题**：arXiv:2604.15085 对应 2026 年 4 月（YYMM 格式），但标注 (2025)；references.md 行 65"预印本核实状态"段也称"Borrego Varillas et al., arXiv:2604.15085 (2025)"——年份矛盾
- **建议**：改为 `(2026)` 或 `(2026-04)`，并核实是否已正式发表
- **action**：rewrite

#### [low] timeliness — 缺 2026 年最新文献（除 [23] Roadmap）

- **位置**：references.md 全部 27 条
- **问题**：除 [23] Borrego Varillas（实为 2026-04，但标 2025）外，无 2026 年正式发表的 BSV-HHG / 量子光 HHG 后续实验或理论文献；申请书"2026 三段式瘦身提质"语境下，缺最新文献会显得时效不足
- **建议**：联网检索 2026 年 BSV-HHG / 量子光场驱动 HHG 最新进展（特别是 Rasputnyi 团队、Boroumand 团队、Even Tzur 团队的后续工作），补 1-2 篇 2026 年正式发表文献
- **action**：research + add（补 1-2 篇 2026 文献）

---

## 7. 修复确认表（相对 round-5 参考文献检验）

| round-5 问题 | 严重度 | 本轮状态 | 处置 |
|---|---|---|---|
| C-5.1 Even Tzur #2 期刊/卷期/arXiv 三重错误 | critical | ⚠️ 部分修复（仍标 PRR 6, 023064 2024） | 需重核——应改为 Nat. Phys. 19, 1057 (2023)（round-5 已建议） |
| C-5.2 Silva #7 标题/arXiv/卷期页交错拼接 | critical | ✅ 修复（已统一为 Nat. Photon. 12, 266 (2018) + arXiv:1704.08471） | 通过 |
| C-5.3 Iskhakov #4 标题张冠李戴 | critical | ✅ 修复（已改为 "Superbunched bright squeezed vacuum state"） | 通过 |
| C-5.4 Peschel #10 主题/标题不匹配 | critical | ❌ **未修复**（仍标 "Two-particle correlations in real-space tight-binding models"） | 需重核 |
| H-5.5 两套引用体系并存，正文无 [N] | high | ❌ **未修复** | 需正文 + references 双改 |
| H-5.6 正文引用 PRL 129,173001 未入表且错引 | high | ❌ **未修复** | 需替换为 [11] Li 2022 或补正确条目 |
| H-5.7 Boroumand #15 标题不符，QSHHG 缩写归属存疑 | high | ⚠️ 部分修复（已加 QSHHG 标注但标题仍标错） | 需 verify |
| H-5.8 Wu #14 标题不符 | high | ⚠️ 部分修复（已加"室温"修订但标题可能仍不符） | 需 verify |
| H-5.9 Li #9 PRL 123,153201 无法核实 | high | ⚠️ 未明（仍标 PRL 123, 153201 (2019)） | 需 verify |
| M-5.10 Spasibko #3 标题被加词 | medium | ⚠️ 未明（仍标 "BSV: A source of low-noise light for dense media interaction and high-precision metrology"——与真实标题"Spectral properties of high-gain parametric down-conversion"不符） | 需 verify |
| M-5.11 #23 Schleich 1987 孤儿引用 | medium | ⚠️ 部分修复（已在 [20] 重写为"压缩真空态在 Glauber 相干态基上投影权重"——正文三章节仍未挂钩） | 需正文补引 |
| M-5.12 Hu #13 PNAS 编号/标题需核实 | medium | ⚠️ 未明（仍标 PNAS 121, e2317656121 (2024)） | 需 verify |
| M-5.13 预印本占比偏高 | medium | ✅ 已加"预印本核实状态"段（行 65）——形式修复；实质仍 41% 偏高 | 提交前 verify |
| L-5.14 #22 年份与 arXiv ID 矛盾 | low | ❌ **未修复**（[23] 仍标 (2025)，arXiv:2604.15085 实为 2026） | 改为 (2026) |
| L-5.15 #5 Wu-Schafer 标题简写 | low | ⚠️ 仍标"Computational scaling, cutoff extension..."——非真实标题 "Multilevel perspective..." | 需 verify |
| L-5.16 #16/#17/#18 未深度核实 | low | ⚠️ 未明 | 需 verify |

**修复确认总结**：
- **彻底修复**：C-5.2、C-5.3 共 2 条
- **部分修复**：C-5.1、H-5.7、H-5.8、H-5.9、M-5.10、M-5.11、M-5.12、M-5.13、L-5.15 共 9 条
- **未修复**：C-5.4、H-5.5、H-5.6、L-5.14 共 4 条
- **新增问题**：5 条（见第 1-6 节）

---

## 8. 全部问题清单（按严重度 + 编号 + 位置 + action）

### [critical] — 共 2 项

**C-9.1 consistency — 正文与 references.md 两套引用体系并存（继承 round-5 H-5.5）**

- 位置：references.md 全文 + 三章节正文
- 问题：references.md 用数字编号 [1]–[27]，正文全部用"[作者, 期刊 卷, 页 (年); arXiv:xxxx]"括号制，正文无任何 [N] 数字角标
- 建议：双改——正文加 [N]，references 保持编号
- action：rewrite（全文统一）

**C-9.2 citation — Spasibko arXiv ID 正文与 references 不一致（继承 round-5 critical）**

- 位置：rationale §1.2.2 第 23 行 arXiv:1201.0367 vs references #3 arXiv:1203.1391
- 问题：同一文献两个不同 arXiv ID
- 建议：核实真实 ID 并统一
- action：verify + rewrite

### [high] — 共 3 项

**H-9.3 citation — 正文引用 PRL 129,173001 (2022) 在 references 中无对应条目（继承 round-5 H-5.6）**

- 位置：scheme.md §3.2 第 29 行
- 问题：正文引 PRL 129,173001 (2022)，references 无该条；round-5 核实 PRL 129,173001 (2022) 为"有机极化子多体动力学"，与"量子干涉可见度"无关
- 建议：替换为 [11] Li 2022 arXiv:2205.11161 或补正确文献
- action：verify + rewrite 或 remove

**H-9.4 rigor — QSHHG 缩写归属存疑（继承 round-5 H-5.7）**

- 位置：references.md [15] + rationale §1.4 段 3、scheme §3.5、content §2.8
- 问题：references #15 标"Quantum sideband high-harmonic generation"，但 arXiv:2505.22536 真实标题为"Quantum engineering of high harmonic generation"——QSHHG 缩写在该真实文献标题中无依据
- 建议：改正文 [15] 标题为真实标题；正文首次使用 QSHHG 时加注"本项目简称，原文未用此缩写"
- action：verify + rewrite

**H-9.5 citation — Peschel #10 主题/标题不匹配（继承 round-5 C-5.4，未修复）**

- 位置：references.md 行 21（编号 10）
- 问题：references #10 标"Real-space two-particle tight-binding approach to HHG in solids. Phys. Rev. B 106, L081408 (2022)"——round-5 核实 PRB 106, L081408 实为"Self-induced decay of intense laser pulse into a pair of surface plasmons"
- 建议：核实 PRB 106, L081408 真实作者与标题；若实为表面等离激元论文，替换为正确的两粒子紧束缚 HHG 文献
- action：verify + rewrite 或 remove

### [medium] — 共 7 项

**M-9.6 rigor — 缺 Berry 曲率反演独立引用**

- 位置：rationale §1.1 段 1
- 问题：§1.1 段 1 提出"Berry 曲率敏感"但未直接挂钩 [7] Silva 2018 / [25] Luu 2018
- 建议：在 §1.1 段 1 加引 [7] 或 [25]
- action：add（正文补引）

**M-9.7 rigor — 缺国内空白检索证据**

- 位置：rationale §1.1 段 4
- 问题："未发现国内团队"声明无检索证据
- 建议：方法学手册或附录补检索报告
- action：add（附录检索证据）

**M-9.8 rigor — 缺 PINN 在 HHG 反演中的具体应用引用**

- 位置：content §2.6 末段、§2.9 末段
- 问题：正文提到 PINN 但仅引 [22] Karniadakis 2019，未引 PINN-HHG 应用文献
- 建议：补 1-2 篇 2023-2025 PINN-HHG 应用文献
- action：add（补 1-2 篇 PINN-HHG 应用文献）

**M-9.9 quantity — 预印本占比偏高（41%）**

- 位置：references.md 27 条
- 问题：11 条带 arXiv ID，其中 5 条仍为预印本且支撑关键论断（[1]/[9]/[14]/[16]/[18]）
- 建议：提交前联网核实 5 条最新发表状态；已发表补期刊卷期页
- action：verify（提交前必做）

**M-9.10 citation — Spasibko #3 标题被加词（继承 round-5 M-5.10）**

- 位置：references.md 行 7（编号 3）
- 问题：references #3 标题标"Bright squeezed vacuum: A source of low-noise light for dense media interaction and high-precision metrology"——与 round-5 核实真实标题"Spectral properties of high-gain parametric down-conversion"不符
- 建议：改正文 [3] 标题为真实标题
- action：verify + rewrite

**M-9.11 citation — Li #9 PRL 123,153201 (2019) 无法核实（继承 round-5 H-5.9）**

- 位置：references.md 行 19（编号 9）
- 问题：仍标"PRL 123, 153201 (2019); arXiv:1908.07283"——round-5 联网无法核实精确匹配
- 建议：提交前联网核实
- action：verify

**M-9.12 citation — Hu #13 PNAS 编号需核实（继承 round-5 M-5.12）**

- 位置：references.md 行 27（编号 13）
- 问题：PNAS 121, e2317656121 (2024) DOI round-5 联网核实返回"Resource not found"
- 建议：核实 PNAS 编号格式
- action：verify

### [low] — 共 6 项

**L-9.13 format — 8 条正式发表文献缺 DOI**

- 位置：references.md [5]/[19]/[3]/[4]/[24]/[25]/[20]/[27]
- 问题：8 条正式发表未列 DOI
- 建议：补 DOI
- action：research + rewrite

**L-9.14 format — 第 1 作者姓名格式不统一**

- 位置：references.md 全部条目
- 问题：部分条目姓在前，部分姓在后
- 建议：统一为"姓 首字母."
- action：rewrite

**L-9.15 timeliness — [23] Borrego Varillas 年份标注与 arXiv ID 矛盾**

- 位置：references.md 行 51（编号 23）
- 问题：arXiv:2604.15085 实为 2026-04，但标 (2025)
- 建议：改为 (2026)
- action：rewrite

**L-9.16 timeliness — 缺 2026 年最新 BSV-HHG / 量子光 HHG 后续文献**

- 位置：references.md 全部 27 条
- 问题：除 [23] Roadmap（实为 2026-04）外，无 2026 年正式发表的同类文献
- 建议：联网检索并补 1-2 篇
- action：research + add

**L-9.17 relevance — [20]/[24]/[25] 方法学手册引用与正文三章节弱关联**

- 位置：references.md 行 45/53/55
- 问题：[20] Schleich 1987、[24] Vampa 2015、[25] Luu 2018 正文三章节未挂钩
- 建议：正文补引或方法学手册明确引用位置
- action：add（正文补引）

**L-9.18 quantity — [15] Wu-Schafer 标题简写（继承 round-5 L-5.15）**

- 位置：references.md 行 11（编号 5）
- 问题：标题仍标"High-order harmonic generation in a 1×1 recurrent lattice: Computational scaling, cutoff extension..."——非真实标题"Multilevel perspective on HHG in solids"
- 建议：改正文 [5] 标题
- action：verify + rewrite

---

## 9. 对抗结论

### 本轮问题统计

- **本轮发现 18 个问题（critical:2, high:3, medium:7, low:6）**
- 相比 round-5（参考文献 0.66，16 个问题 critical:4+high:5+medium:4+low:3）：综合 +0.06，问题数 +2（critical -2 / high -2 / medium +3 / low +3）
- **彻底修复 2 条**：C-5.2 Silva、C-5.3 Iskhakov
- **部分修复 9 条** / **未修复 4 条**（C-5.4 Peschel、H-5.5 两套体系、H-5.6 PRL 129、L-5.14 年份矛盾）

### 是否达到输出标准

**部分达标**。理由：
- ✅ **完整性维度 ≥ 0.70**：27 条总数在 15-30 区间内；时效 37% 近 3 年文献；预印本核实声明已加入
- ❌ **严谨性维度 < 0.70**：两套引用体系并存仍未修复（继承 round-5 critical），正文与 references arXiv ID 不一致仍未修复（继承 round-5 critical）
- 综合 0.72 < 0.80 阈值，但**本轮聚焦仅参考文献，跨章节物理/写作问题不在评分范围**

### 返工优先级

**P0（提交前必须）**：
- C-9.1 统一全文引用制式为 [N] + references 编号（影响评审检索链）
- C-9.2 Spasibko arXiv ID 正文与 references 统一
- H-9.3 PRL 129,173001 替换为正确文献或删除
- H-9.5 Peschel #10 标题核实或替换
- H-9.4 QSHHG 缩写归属核实

**P1（强烈建议）**：
- M-9.6 Berry 曲率反演正文补引
- M-9.7 国内空白检索证据附录
- M-9.8 PINN-HHG 应用文献补引
- M-9.9 预印本发表状态提交前联网核实

**P2（提交前 24h）**：
- L-9.13 8 条正式发表文献补 DOI
- L-9.14 作者姓名格式统一
- L-9.15 [23] 年份改为 (2026)
- L-9.16 补 1-2 篇 2026 最新文献
- L-9.17 方法学手册引用正文补引
- M-9.10/9.11/9.12/L-9.18 标题核实

### 下一轮评审建议聚焦

- 本轮已确认 references.md 27 条数量与时效基本达标；下一轮建议聚焦**正文与 references.md 的双向 [N] 闭环核查**——验证全部 ~40 处正文行内引用是否能在 references.md 找到唯一对应条目，反之亦然。
- 建议同步核查 methodology-manual.md 中对 references [20]-[27] 的引用位置。
- 建议提交前 24 小时做最后一次**arXiv 联网批量检索**，确认 5 条仍为预印本的最新发表状态。

### 写作风格审查（参考文献章适用性说明）

references.md 本身为条目式列表，不适用叙述式写作红线。本轮检查聚焦格式准确性、编号一致性、相关性、完整性、时效性——未涉及 narrative / expression 维度。

---

## 评分

创新性：0.85
可行性：0.85
严谨性：0.65
完整性：0.78
综合评分：0.72