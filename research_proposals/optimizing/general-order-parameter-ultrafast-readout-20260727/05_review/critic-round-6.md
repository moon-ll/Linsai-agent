# 对抗评审报告（第6轮 — 参考文献专项）

## 元信息

- 项目类型：general（NSFC 面上项目）
- 审查日期：2026-08-21
- 审查范围：references.md 双向 [N] 编号一致性 + 文献真实性 + 引用质量
- 审查文件：references.md（43 条正式条目）、rationale.md / content.md / scheme.md
- 上一轮文件处理情况：R32 修复清单已部分实施（[69] 幽灵引用、Schüle 编号统一、格式统一），但 [68] Weber 虚构元素符号 Mu 的 critical bug 未修复，且 references.md 自身元叙述多处自相矛盾

## 综合评分

0.55 / 1.00（按 general 项目严谨性 + 完整性两维度均值）

## 维度评分

| 维度 | 权重 | 得分 | 问题数 |
|------|------|------|--------|
| 严谨性（rigor） | 0.50 | 0.45 | critical:3, high:3, medium:2 |
| 完整性（completeness） | 0.50 | 0.70 | medium:2, low:1 |
| 综合评分 | — | 0.55 | total: 10 |

## [N] 引用编号一致性核查

正文（rationale.md + content.md + scheme.md）共使用 39 个独立 [N] 编号（出现 132 次 [N] 标记）。references.md 共定义 43 个有效 [N] 书目条目（外加 [58a]/[58b] 双编号不计为新增条目）。

### 双向映射表

| [N] | 正文使用次数 | 正文章节 | references.md 是否定义 | 备注 |
|-----|------------|----------|---------------------|------|
| [1] | 1 | rationale | ✓ | Kawakami 2020 |
| [2] | 1 | rationale | ✓ | Matsunaga 2017 |
| [3] | 1 | rationale | ✓ | Alcalá 2022 |
| [5] | 2 | rationale | ✓ | Puviani 2024 |
| [7] | 1 | rationale | ✓ | Li & Weng 2025 |
| [9] | 1 | rationale | ✓ | Ahmed 2020 |
| [10] | 1 | rationale | ✓ | Rehn 2025 |
| [11] | 16 | rationale/content | ✓ | Tyulnev 2025 |
| [12] | 12 | rationale/content/scheme | ✓ | Zhang 2025 |
| [13] | 1 | rationale | ✓ | Dziurawiec 2024 |
| [15] | 1 | rationale | ✓ | Hansen 2022 |
| [16] | 6 | rationale/content/scheme | ✓ | Murakami 2025 |
| [20] | 2 | rationale | ✓ | Jensen 2024 |
| [22] | 1 | rationale | ✓ | Hu 2024 |
| [23] | 1 | rationale | ✓ | Takayoshi 2019 |
| [24] | 6 | rationale/content/scheme | ✓ | Werner 2026 |
| [25] | 6 | rationale | ✓ | Šmejkal 2022 |
| [26] | 4 | rationale/content | ✓ | Leeb 2024 |
| [27] | 1 | rationale | ✓ | Ryan 2024 |
| [28] | 1 | rationale | ✓ | Garcia-Gaitan 2025 |
| [29] | 1 | rationale | ✓ | Gabriele 2025 |
| [30] | 1 | rationale | ✓ | Ly 2026 |
| [31] | 5 | rationale/content/scheme | ✓ | Cheng 2026 |
| [35] | 3 | rationale/content/scheme | ✓ | Granados 2026 |
| [36] | 2 | scheme | ✓ | Mandal 2025 |
| [39] | 1 | rationale | ✓ | Li 2023 |
| [55] | 0 | — | ✓ | Jita 2026（未引用） |
| [56] | 1 | rationale | ✓ | Sankar 2025 |
| [57] | 1 | rationale | ✓ | Ren 2026 |
| [58a] | 3 | rationale | ✓ | Leeb 2025 |
| [58b] | 3 | rationale/content | ✓ | Qiu 2025 |
| [59] | 4 | rationale/content/scheme | ✓ | Yue 2020 |
| [60] | 3 | rationale/content/scheme | ✓ | Wang 2022 |
| [61] | 3 | rationale/content/scheme | ✓ | Zhang 2024 |
| [62] | 10 | rationale/content/scheme | ✓ | Cochran 2025 |
| [63] | 16 | rationale/content/scheme | ✓ | Sørensen 2025 |
| [64] | 1 | rationale | ✓ | Fuchs 2025 |
| [65] | 1 | rationale | ✓ | McCarter 2025 |
| [66] | 1 | rationale | ✓ | Horstmann 2025 |
| [67] | 6 | rationale/content/scheme | ✓ | Rost 2025 |
| [68] | 0 | — | ✓ | **Weber "NdMu2Si₂" — 含虚构元素符号 Mu** |
| [70] | 0 | — | ✓ | Singh 2025（未引用） |
| [71] | 0 | — | ✓ | Ding 2026（未引用） |
| [72] | 0 | — | ✓ | Consiglio 2026（未引用） |

**编号错位（critical）**：
- 正文使用 39 个独立 [N]，references.md 定义 43 个条目——4 个定义但未使用（[55]、[68]、[70]、[71]、[72]），其中 [68] Weber 条目本身存在文献真实性问题（见下文）。
- 无 [N] 幽灵引用：正文未引用 references.md 不存在的 [N]。

## 文献真实性核查（critical bug 源）

### [68] Weber 虚构元素符号（critical — 上一轮未修复）

**位置**：references.md L141

**问题**：条目标题为 "Spin eigenmodes of **NdMu2Si₂** and last touch of altermagnetic kinetics"。**Mu 在元素周期表中不存在**（Mu 是 muonium 的化学符号，不是原子序数元素）。条目短描述声称研究对象为 RuO₂，与标题完全矛盾。已知 arXiv:2408.05187 真实论文（Weber M. et al., 2024）题为 "All-optical excitation of spin polarization in d-wave altermagnets"，研究对象为 RuO₂ 而非 NdMu2Si₂。R32 修复清单将 [69] 改写为 [68] Weber，但反转过程中保留了 R31 之前引入的虚构元素符号 "Mu"，导致：
1. 标题与短描述研究对象矛盾（NdMu2Si₂ vs. RuO₂）
2. 元素符号 "Mu" 在周期表不存在
3. 实际 Weber 等人 2024 arXiv:2408.05187 论文标题为 d 波 altermagnet 自旋极化，不是 "eigenmodes of NdMu2Si₂"

**建议**：删除 [68] 现有条目，更换为 Weber M. et al. "All-optical excitation of spin polarization in d-wave altermagnets" arXiv:2408.05187 (2024)。或保留 [68] 但改为真正的 Weber 2024 论文（RuO₂）。

**action**：rewrite

### references.md 内部 §8 与 §6 元叙述自相矛盾（critical）

**位置**：references.md L161（§8 L 引用计数）、L129（§6 L 末尾）、L177（L32 修复清单）

**问题**：references.md 在三处对 [69] 编号的处理描述完全矛盾：
1. **L161** ("证据等级" 段) 与 L129（§6 段）实际未给 [69] 编号，但声称 [69] 是 Weber 正式发表条目
2. **L177** ("R32 修复清单") 写："[69] Weber 现已在列表中作为正式发表条目存在，正文以纯文本引用"——但 [69] 在 references.md 中**只有元叙述提及 4 次**，从未作为有效书目条目存在（L177 之后无 [69] 编号的 Author 起始行）
3. R32 修复清单同时声称 "[69] 在参考文献列表中不存在（幽灵引用）已修复" 且 "[69] Weber 现已在列表中作为正式发表条目存在"——但核实显示 [69] 既不是真正的书目条目也没有被修复为条目

**建议**：将 [69] 改为 [68]（因为 Weber 的实际条目是 [68]），或把 R32 修复清单中所有 [69] 都改为 [68]，并删除 [69] 在元叙述中的所有提及。

**action**：rewrite

## 问题清单

### CRITICAL 1: [68] Weber 文献真实性 bug 残留

- **位置**：references.md L141
- **问题**：标题 "NdMu2Si₂" 含虚构元素符号 Mu；标题与短描述研究对象矛盾（NdMu2Si₂ vs. RuO₂）；arXiv ID 2408.05187 对应的真实论文标题为 "All-optical excitation of spin polarization in d-wave altermagnets"（Weber M. et al., RuO₂ d 波 altermagnet 研究），不是 "Spin eigenmodes of NdMu2Si₂"
- **风险**：评审人若按 arXiv ID 反查会发现标题/作者/研究对象不一致，触发"AI 生成虚假文献"判定
- **建议**：将 [68] 完整改写为真正的 Weber 2024 论文（RuO₂ altermagnet 光学激发自旋极化），删除 "NdMu2Si₂" 虚构内容
- **action**：rewrite

### CRITICAL 2: references.md §8 与 §6 元叙述 [69] 编号处理自相矛盾

- **位置**：references.md L129、L161、L177、L179
- **问题**：R32 修复清单内部以及与 §6/§8 描述对 [69] 编号的处理完全自相矛盾——既声称 [69] Weber 已作为正式发表条目存在，又在同段说 "[69] 在参考文献列表中不存在（幽灵引用）已修复"；真实情况是 [69] 编号在 references.md 中仅作为 4 次元叙述提及，从未存在书目条目
- **风险**：评审人若读完整文件，会发现 [69] 的"已修复"描述与实际不符，触发"修复清单文本造假"判定
- **建议**：将 L129、L161、L177、L179 中所有 [69] 替换为 [68]（Weber 实际条目编号），删除 [69] Weber 的所有元叙述
- **action**：rewrite

### CRITICAL 3: §8 引用计数与正文实际不符

- **位置**：references.md L161
- **问题**：§8 声称"正文直接引用 40 条"，但实际正文（rationale.md + content.md + scheme.md）使用 39 个独立 [N] 编号（39 ≠ 40）。R32 修复清单 L187 也明确"§8 引用计数错误 | §8 称'39 条正文引用'但实际为 40 条 | 已修复"，但该修复本身基于错误的基线（40 而非 39）
- **风险**：元叙述计数与实际 [N] 频次不一致，评审人核对会立即发现
- **建议**：重新核算正文 [N] 实际频次（详查：去掉重复的 [62] Cochran 计 1 次的话独立编号为 39 个；按 [N] 出现次数总和为 132 次）；将 §8 改为"正文使用 39 个独立 [N] 编号，累计出现 132 次"
- **action**：rewrite

### HIGH 1: §4 元叙述将 [62] Cochran 误归入 §4 引用

- **位置**：references.md L161（§8 引用分组）
- **问题**：§8 声称 §4 引用 17 条（"[23]–[31]、[55]–[57]、[58a]、[58b]、[70]、[71]、[72]"），但 [62] Cochran 实际位于 §5 而非 §4；§4 实际独立编号为 13 个（[23-31]、[55-57]、[58a]、[58b]），加上 [70-72] 未引用条目共 17 个，但元叙述把 [62] Cochran 也列入 §4 不准确
- **建议**：删除 §8 中 [62] 编号（若 §8 计数仅含 §4 的话），或明确标注 [62] 实际位于 §5
- **action**：rewrite

### HIGH 2: 编号策略声明与实际空号矛盾

- **位置**：references.md L5、L158
- **问题**：L5 声称"全表每个 [N] 在列表中均有对应条目，无正文幽灵编号"，但实际正文使用的 [N] 编号中存在大量 [68]（未引用）、[70]（未引用）、[71]（未引用）、[72]（未引用）、[55]（未引用）——这些条目在 references.md 中存在但正文未使用。R32 修复清单承认这是"组间预留编号是本表的设计特征"，但 L5 的"无空号"措辞与实际空号（[4]、[6]、[8]、[14]、[17]–[19]、[21]、[32]–[34]、[37]、[38]、[40]–[54]）矛盾
- **建议**：将 L5 改为"正文使用的 [N] 编号在列表中均有对应条目"（移除"全表每个 [N] 均有对应"的全称命题）；§8 "组间预留" 描述已经修正
- **action**：rewrite

### HIGH 3: [68] Weber 短描述与 [70] Singh 标题自相矛盾

- **位置**：references.md L141（[68] Weber 短描述）、L97（[70] Singh 实际条目）
- **问题**：references.md L141 [68] Weber 短描述声称研究对象为 RuO₂，但 R32 修复清单 L177 写"Schüle 统一为纯文本引用……消除了与 [68] Qiu 合著群的潜在重复"——这里出现 [68] Qiu，但实际 [68] 是 Weber 不是 Qiu。R32 文本错误地把 [68] 编号归属给 Qiu 而非 Weber（[58b] 才是 Qiu 的编号）
- **建议**：R32 修复清单 L177 / L179 中 "[68] Qiu" 改为 "[58b] Qiu"
- **action**：rewrite

### MEDIUM 1: §8 时效性数据与实际不符

- **位置**：references.md L165
- **问题**：L165 声称"参考文献 43 条中，2023—2026 年文献 37 条（占 86%）"——实际 2023-2026 年文献 34 条（79.1%），2024-2026 年为 33 条（76.7%）。差异 3 条可能因元叙述把 [58a]/[58b] 双编号作为单一条目计数，或漏计 2026 年条目
- **建议**：重新核算时效性，按"2023-2026 年文献 34 条（79.1%）"或"2024-2026 年文献 33 条（76.7%）"重新表述
- **action**：recalculate

### MEDIUM 2: [68] Weber 条目 arXiv 时间与正式发表时间矛盾

- **位置**：references.md L141
- **问题**：[68] Weber 标注 "Phys. Rev. X **16**, 021051 (2026). DOI: 10.1103/PhysRevX.16.021051; arXiv:2408.05187 (2024)"。若 2024 年 8 月 arXiv 预印本至 2026 年正式发表跨度 2 年是合理的，但配合虚构标题 "NdMu2Si₂" 形成"2024 年 8 月真实存在的预印本 + 2026 年期刊增补了虚构标题"的可疑模式
- **建议**：用真实 Weber 2024 论文替换当前 [68] 条目；保留 arXiv:2408.05187 ID 与 2026 年正式发表标注
- **action**：rewrite

### MEDIUM 3: [36] Mandal 装置参数描述与正文实际需求轻微不一致

- **位置**：references.md L111（[36] Mandal 条目）、scheme.md L51
- **问题**：[36] Mandal 装置描述"载波包络相位抖动 < 200 mrad"作为本项目装置基线，但 scheme.md L51 描述的本项目场强校准依赖的是 Mandal 装置的"气体阿秒条纹场的驱动场绝对校准"——这一表述暗示技术路线图使用了阿秒条纹场，但正文实际方案并未提及阿秒条纹
- **建议**：核对 [36] Mandal 装置的实际方法学描述是否包含阿秒条纹场；若不含，正文 scheme.md L51 移除"气体阿秒条纹场的驱动场绝对校准"措辞
- **action**：verify

### LOW 1: [67] Rost 引用位置 4 处与正文核对

- **位置**：references.md L163、[67] Rost 实际正文引用
- **问题**：references.md L163 声称 [67] Rost 在 rationale.md 行 33、行 51、行 63、行 77 引用；实际正文搜索显示 [67] 确实出现在这 4 个位置，但内容均简短（多作为支撑性引用而非论证核心），与 references.md "CrSb 主体系首批直接实验证据" 的定位匹配
- **建议**：维持现状
- **action**：keep

## 锚点对比（参考文献真实标题 vs references.md 描述）

1. **引用**：references.md L141 [68] Weber 条目
   "Weber, F. et al. Spin eigenmodes of NdMu2Si₂ and last touch of altermagnetic kinetics. *Phys. Rev. X* **16**, 021051 (2026). DOI: 10.1103/PhysRevX.16.021051; arXiv:2408.05187 (2024)."

2. **对比**：arXiv:2408.05187 真实论文（按 R32 修复清单自身引用 "arXiv:2408.05187"）
   "All-optical excitation of spin polarization in d-wave altermagnets"（Weber M. et al., 2024，研究对象 RuO₂）

3. **差距**：① 标题完全不符（"Spin eigenmodes of NdMu2Si₂" vs. "All-optical excitation of spin polarization in d-wave altermagnets"）；② 研究对象不符（NdMu2Si₂ vs. RuO₂）；③ "Mu" 元素符号在周期表不存在；④ 第一作者姓 Weber 实际为 M. Weber（按 R32 修复前历史），但当前条目标注 "Weber, F. et al."——首字母不匹配

**差距执行**：立刻将 [68] 当前条目替换为真实的 Weber M. et al. 2024 论文（标题、研究对象、第一作者首字母均需修正）

## 对抗结论

- **本轮发现 10 个问题**（critical:3, high:3, medium:3, low:1）
- 相比上一轮：R32 修复清单承认并解决了 9 项历史问题，但 [68] 虚构元素符号 Mu 的 critical bug 跨轮未修复；references.md 自身元叙述多处自相矛盾（R32 修复清单内部、§8 与 §6、§8 计数与正文实际 [N] 频次）
- **未解决**：[68] Weber 虚构元素符号（跨 R31/R32 两轮，作为 deferred bug 持续残留）；[69] 编号在 references.md 元叙述中的所有提及未清理
- **新增**：R32 修复清单 L177 / L179 中 "[68] Qiu" 编号错误（应为 [58b] Qiu）；§8 引用计数 40 与正文实际 39 不符
- **是否达到输出标准**：否。本次评审的关键判断是 [68] Weber 虚构元素符号 Mu 仍未修复（critical bug 跨轮残留），且 references.md 自身存在大量自相矛盾的元叙述。若直接提交 NSFC，评审人按 arXiv:2408.05187 反查会立即发现 [68] 标题/作者/研究对象与原始论文不一致，触发"AI 生成申请书 + 虚构文献"判定
- **返工优先级**：① [68] Weber 条目整体重写（critical）；② references.md L129/L161/L177/L179 中 [69] 全部替换为 [68] 并清理元叙述（critical）；③ §8 引用计数修订为 39（critical）；④ 修复清单 L177/L179 "[68] Qiu" 改为 "[58b] Qiu"（high）
- **下一轮建议**：writer 重写 [68] 条目后，进入 R7 再次核查所有 [N] 编号一致性；同时启动 arXiv / DOI 反查工作流，对所有 23 条预印本逐条反查标题、作者、研究对象

## 评分

创新性：N/A
可行性：N/A
严谨性：0.45
完整性：0.70
综合评分：0.55
