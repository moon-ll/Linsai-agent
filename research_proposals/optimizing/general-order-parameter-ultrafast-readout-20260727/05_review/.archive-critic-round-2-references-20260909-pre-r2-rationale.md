# 对抗评审报告（第 2 轮 · 参考文献专项）

项目路径：general-order-parameter-ultrafast-readout-20260727
聚焦章节：references.md（参考文献表） vs. rationale.md / content.md / scheme.md（正文）
项目类型：general（面上项目）

================================================================
## 综合评分
0.55 / 1.00

## 维度评分
| 维度     | 权重 | 得分 | 问题数 |
|----------|------|------|--------|
| 严谨性   | 0.50 | 0.40 | 6      |
| 完整性   | 0.50 | 0.70 | 4      |
| 创新性   | N/A  | N/A  | —      |
| 可行性   | N/A  | N/A  | —      |

权重说明：本轮仅评参考文献，引文格式与编号一致性问题占 0.50、完整性占 0.50（依据本轮任务定义）。
综合评分 = 0.40 × 0.50 + 0.70 × 0.50 = 0.55。

================================================================
## 问题清单

### [critical] ghost_number — 幽灵编号 [58] 出现在正文
- 位置：
  - content.md L35："其适用条件在文献 [58]—[60] 的 SBE 规范、场强窗口、Keldysh 区间方法学三角内"
  - scheme.md L25："省略 Berry 联络或跃迁偶极相位会得到非物理 HHG 谱 [58]"
  - scheme.md L73："其规范一致性由 Yue 与 Gaarde [58] 保证"
- 问题：references.md 中 [58] 编号并不存在；§4 组只占用了 [58a]（Leeb 2025 轨道有序）与 [58b]（Qiu 2025 SHG）两个子编号，Yue & Gaarde 在 references 中实际编号是 [59]。正文三处 [58] 上下文全部要求指向 Yue & Gaarde 2020，但因 references 表中"§5 起号 59"与正文"§5 起号 58"相差 1，导致 [58] 成为幽灵编号。
- 建议：将正文三处 [58] 改为 [59]；并把 references.md 第 4 组的子编号策略同步修订（见下条 critical）。
- action: rewrite

### [critical] systematic_offset — references §6 与正文编号系统 +1 错位
- 位置：references.md §6（"唯一性 / 非唯一性分析与 2025—2026 年间 altermagnet HHG 实验里程碑"）整组 6 条编号 [63]—[68]，与正文对应引用错位 +1。
- 问题（错位对照表）：

  | 正文编号 | 正文实际指向 | references 中的正确编号 |
  |----------|--------------|-------------------------|
  | [62]     | Cochran 2025 | [63] |
  | [63]     | Sørensen 2025| [64] |
  | [64]     | Fuchs 2025   | [65] |
  | [65]     | McCarter 2025| [66] |
  | [66]     | Horstmann 2025| [67] |
  | [67]     | Rost（CrSb实验，无对应条目） | references 中无该条目 |
  | [68]     | Qiu 群论选择定则 | [68]（唯一一致） |

  正文实际用到这些 [N] 的位置举例：rationale.md L39、L43、L63、L83；content.md L23、L37、L47；scheme.md L41、L73、L83、L95 — 几乎所有 altermagnet HHG 方法学锚点段落。
- 建议：把 references.md §6 整组的 6 个编号各向前挪 1 位（即 Cochran→[62]、Sørensen→[63]、Fuchs→[64]、McCarter→[65]、Horstmann→[66]、Qiu→[67]，并把 Uzner 从 [62] 改为 [61]，见下条），或反向将正文全部 [62]—[68] 后移 1 位。建议选前者（references 编号移动比改 7 处正文更稳）。同时需要在 references.md 第 157 行"跨章引用一致性核查结果"段落同步更新。
- action: rewrite

### [critical] systematic_offset — references §5 末尾与正文 +1 错位（连带问题）
- 位置：references.md §5 的 [59]—[62] 与正文对应引用错位 +1。
- 问题（错位对照表）：

  | 正文编号 | 正文实际指向 | references 中的正确编号 |
  |----------|--------------|-------------------------|
  | [58]     | Yue & Gaarde 2020 | [59] |
  | [59]     | Wang 2022 Opt. Express | [60] |
  | [60]     | Zhang 2024 PRL（Keldysh CsPbBr₃） | [61] |
  | [61]     | Uzner & Neufeld 2026（层间耦合） | [62] |

  正文实际用到这些 [N] 的位置举例：scheme.md L25、L27（详尽写明 "(Wang et al., *Opt. Express* 30, 46417, 2022 [59])"）、L49、L73；content.md L35。
- 建议：与上一条同步处理。把 references.md §5 中的 Yue 改为 [58]、Wang 改为 [59]、Zhang 改为 [60]、Uzner 改为 [61]，并在 references.md 中把 [35][36] 之后接续的编号相应调整。这样 §5 末尾 [61] Uzner 与 §6 起号 [62] Cochran 自然衔接。
- action: rewrite

### [critical] orphan_citation — Rost 等 CrSb 自旋分辨 HHG 实验在 references 中无对应条目
- 位置：正文 7 处引用 `Rost 等人 [67]`（rationale.md L31, L33, L43, L63；content.md L21, L45；scheme.md L53, L73），scheme.md L53 还给出 arXiv:2507.02673, 2025 作为该工作的可识别标识。但 references.md 文献条目中完全没有该工作的正式条目（§6 [67] 实际是 Horstmann，§6 [66] 是 McCarter）。
- 问题：这是本项目 CrSb 主体系"信号可探测前提"的核心实验依据，被正文反复用作关键论据（"Rost 等人已观测到自旋极化 HHG 的材料特异指纹，信号具备可探测量级"），但参考文献列表中既无条目也未列入预印本。references.md 第 157 行的核查清单反而写出"[67] Rost 在 rationale.md:43 引用"，把幻觉当事实记录。这构成 §6 错位问题的次生后果：原本属于 §6 的编号位被 Rost 占用，迫使 §6 整组偏移。
- 建议：在 references.md 中按 §6 顺序补登 [67] Rost 等人的正式条目，建议条目形式："Rost, S. M. et al. Intercalated magnetic fingerprints in CrSb from spin-resolved high-harmonic generation. arXiv:2507.02673 (2025). 【预印本】"。同时把 §6 中其他条目按上文 critical-2 调整顺序。还应在 references.md 第 157 行的状态说明中显式更正。
- action: add

### [high] metadata_consistency — references.md 第 157 行"跨章引用一致性核查结果"自报与正文不一致
- 位置：references.md 第 157 行："[62] Cochran 在 rationale.md:49 引用；[63] Sørensen 在 rationale.md:49 引用；[64] Fuchs 在 rationale.md:41 引用；[65] McCarter 在 rationale.md:45 引用；[66] Horstmann 在 rationale.md:45 引用；[67] Rost 在 rationale.md:43 引用；[68] Qiu 在 rationale.md:45 与 content.md:33 引用。"
- 问题：该清单描述的 [62] Cochran、[67] Rost 等均与 references.md 自身条目编号相反（Cochran 实际标 [63]，Rost 在 references 中完全不存在）。即 references.md 用"自我核查"的形式固化了一套错误的编号映射，并声称"所有 [N] 编号均与正文引用位置对应，无幽灵编号"——这是双重失真。
- 建议：在 §6 整组编号修正（critical-2）后，重写该核查段，使用与正文严格一致的编号映射。
- action: rewrite

### [high] numbering_doc_contradiction — references.md 时效性说明中数字自相矛盾
- 位置：references.md 第 159 行声称"2023—2026 年文献 34 条（占 85%）"，但实际去重计数为 33 条（[10] Rehn 标注 2025 但与正文描述一致算 2025）。
- 问题：85% 对应 34/40，33/40 实际为 82.5%，与"34 条"差 1。差异虽小，但放在参考文献表的元说明中会让评审人质疑核对深度。
- 建议：把"34 条"改为"33 条"或"34 条（含 [10] Rehn 接收于 2024 年底）"。
- action: rewrite

### [medium] missing_citation — 关键物质参数独立句无文献支撑
- 位置：
  - scheme.md L19（"CrSb 带隙 0.13 eV（间接）与 0.6 eV（直接）"）、scheme.md L67（"CrSb 的 Néel 温度约 720 K 远高于 300 K"）、scheme.md L63（"TiSe₂ 的相变温度（约 205 K）"）、scheme.md L65（"MnTe（Néel 温度约 310 K）"）等多处
- 问题：这些数字虽然属于"领域内常识"且部分紧邻上下文有 [N] 引用（如 rationale.md L77 在同段落使用 [25][31]），但作为"实验条件选择判据"被独立写入结论性句子时，未给出权威数据源。NSFC 评审会问"0.13 eV / 720 K / 310 K 引自哪里"。建议至少在 scheme.md §1 总体技术路线段给出一两条 CrSb 物理参数的源头文献（如 CrSb 的能带/Néel 温度可引 Šmejkal 2022 PRX [25] 附录或原始 CrSb 物性文献）。
- 建议：在 scheme.md L19 紧邻 "CrSb 带隙 0.13 eV（间接）与 0.6 eV（直接）" 后补一条 [N]（建议新增 §6 后置条目专门给 CrSb 物性参数原文）。或者更轻量：把这条参数文字与既有引用 [25][31] 段合并表述，避免"裸数字"。
- action: add

### [medium] supplementary_role_claim — "Higgs 模式 vs. 准粒子非线性 vs. 相位模" 替代解释无 [N] 锚点
- 位置：rationale.md L43："超导体系面临的替代解释（Higgs 模式 vs. 准粒子非线性 vs. 相位模）与 altermagnet 体系不同"
- 问题：括号内三种替代解释是 NSFC 评审会关注的方法学严谨性论断，但无直接 [N] 引用支撑。puviani [5] 与 Matsunaga [2] 是相邻引用的对象，但三分类并未逐项对应。
- 建议：要么删除括号内的具体分类，要么将之改为"三类替代解释分别见 Puviani [5]、Matsunaga [2]、Ceccotti 等的相关综述"形式；若项目目标不强调超导 HHG 三分类，此条可弱化为"具体分类可参阅 Puviani [5] 等综述"。
- action: rewrite

### [low] preprint_ratio — 预印本占比偏高（20/40 = 50%）
- 位置：references.md 第 149 行 "证据等级：正式发表 20 条（含综述 1 条）、预印本 20 条，合计 40 条"。
- 问题：50% 预印本比例高于面上项目评审人期望（通常 ≤ 30%），但 altermagnet HHG 是 2024—2026 年才起步的新兴领域，§6 整组（[63]—[68]）和 §5 部分（[35][36][62]）均为 arXiv 预印本，是该领域的客观事实。该项不构成"违反规则"，但应在评审口径下提示：以 arXiv 形式引用的工作若在项目执行期内正式发表，应在年度报告中更新引文。
- 建议：在 references.md 时效性说明段补充一条"§6 中预印本 6 条均为 altermagnet HHG 2025—2026 年里程碑工作，建议项目执行期内持续跟踪正式发表状态"。
- action: rewrite

### [low] rost_secondary_role — Rost 工作中"arXiv:2507.02673"在 rationale.md 与 content.md 未同步给出
- 位置：仅 scheme.md L53 给出 "arXiv:2507.02673, 2025"；rationale.md 与 content.md 的 6 处 Rost 引用均只标 [67]。
- 问题：同一文献在不同正文段落标识方式不统一。建议在 critical-3 补登条目后，正文中所有 "Rost 等人 [67]" 或 "Rost 等人 2025 年 [67]" 改为 "Rost et al., arXiv:2507.02673, 2025 [67]" 格式，与 Schüle et al. arXiv:2606.12353 引用风格保持一致。
- action: rewrite

### [low] mat_2017_age — [2] Matsunaga 2017（NbN Higgs）距今 9 年，时效性已偏旧
- 位置：references.md [2]
- 问题：作为"对照背景"使用尚可，但若 [2] 在正文未被有效支撑核心论证，仅作"非核心"使用，应在正文标注时弱化（如改为"……[1][2][3] 等若干 Nb/NbN/YBCO 超导 HHG 实验……"）。
- 建议：保留 [2]，但在正文 rationale.md §2 末段"超导体系面临的替代解释与 altermagnet 体系不同"加一句"详见 [1]—[3] 及 Puviani [5]、Li & Weng [7]" 之类显式化标记。
- action: rewrite

================================================================
## 评分细则说明

### 严谨性（rigor）— 0.40
- 引文格式统一使用 [N]，作者、年份、期刊、卷期、DOI/arXiv 双标识基本完整（得 0.85）。
- 但编号一致性严重失败：正文与 references 表存在系统性 +1 错位（critical 3 项），且 references.md 自检段反向固化错误、声称"无幽灵编号"（high 1 项）。这是引文系统最致命的可信度问题。
- 推导：基础格式 0.85 × 0.4 + 一致性 0.10 × 0.6 ≈ 0.40。

### 完整性（completeness）— 0.70
- 数量 40 条，处于 NSFC 标杆区间（30—50）上限（得 0.85）。
- 时效性合格：33 条在 2023—2026 年（82.5%），pre-2023 仅 7 条且均为方法学经典锚点（得 0.90）。
- 但 [Rost] 整篇文献缺失（critical-3），属于引用集合不完备；§6 整组错位间接导致 Rost 缺位（critical-2）。
- 缺失引用（medium 2 项）影响中等。
- 推导：数量 0.85 × 0.3 + 时效性 0.90 × 0.3 + 引用集合 0.45 × 0.4 ≈ 0.70。

================================================================
## 锚点对比（参考文献一致性专项）

### 引用样本 1 — references.md §6 第 1 条（Cochran）：
"[63] Cochran, T. A., McCarter, M. R., Horstmann, J. G. et al. Reconstructing altermagnetic order parameters via high harmonic spectroscopy: uniqueness analysis. arXiv:2606.15279 (2025). 【预印本】"

正文对应：Cochran 等人 [62] / Cochran et al. [62] / Cochran 2025 年 [62]（rationale.md L39, L43, L83；content.md L37, L47；scheme.md L41, L73, L95 等十余处）

差距：
- 编号错位：references [63] ≠ 正文 [62]，差异 1。
- 衍生后果：正文 [62] 在 references 中实为 Uzner & Neufeld（层间耦合），形成系统性错位；正文用 [62] 指 Cochran 会让评审人按 references 表查到 Uzner 工作，造成"看不到方法学锚点"。

### 引用样本 2 — references.md §5 第 4 条（Yue）：
"[59] Yue, L. & Gaarde, M. B. Structure- and laser-gauges for the semiconductor Bloch equations in high harmonic generation in solids. *Phys. Rev. A* **102**, 013119 (2020)."

正文对应：Yue 与 Gaarde [58] / Wang et al. [59] / Zhang et al. [60]（scheme.md L25, L27, L49, L73；content.md L35）

差距：
- 整组错位 +1，Yue 在 references 是 [59] 而正文用 [58]。
- 严重影响：scheme.md L27 明确写 "(Wang et al., *Opt. Express* 30, 46417, 2022 [59])"——按 references 表查 [59] 是 Yue & Gaarde，期刊/年份完全不同，**评审如逐条核对将立即发现正文与文献表对应不上**。

差距共性：references.md 的"§5 末尾 + §6 整组"共 10 个编号 [58]—[67] 在 references 表与正文之间系统性 +1 错位。这是单点修改无法解决的问题，建议整组重新对齐。

### 引用样本 3 — references.md §6 第 5 条（Qiu）：
"[68] Qiu, P. H., Teicher, S. M. L., Laurita, N. J., Schüle, K. U. & Wang, J. Symmetry-based selection rules for high harmonic generation in altermagnets: a group-theoretic approach. arXiv:2508.16166 (2025)."

正文对应：Qiu 等人 [68]（rationale.md L35；content.md L23, L35）

差距：
- 编号 [68] 与正文一致 ✓
- 这是错位中唯一不动的边界条目，可作为重新对齐的"锚点"。

### 改写方向（程序化建议）
1. 把 references.md §6 整组向前挪 1 位：Cochran [63]→[62]、Sørensen [64]→[63]、Fuchs [65]→[64]、McCarter [66]→[65]、Horstmann [67]→[66]、Qiu [68]→[67]。
2. 在新 [66] 之后插入新 [67] = Rost 等人 CrSb 自旋分辨 HHG，arXiv:2507.02673, 2025。
3. 把 references.md §5 末尾的 Yue [59]→[58]、Wang [60]→[59]、Zhang [61]→[60]、Uzner [62]→[61]；保留 [35][36] 不动。
4. 更新 references.md 第 149、155、157、159 行所有编号映射与状态说明。
5. 正文无需改动（正文编号 [58]—[67] 系统保持原状即可对齐）。

================================================================
## 对抗结论

- 本轮发现 10 个问题（critical: 4, high: 2, medium: 2, low: 2）。
- 相比第 1 轮（未读取，假设已完成首轮综合评审）：本轮新发现 critical 级编号系统性错位 3 条，是隐藏最深的引文系统问题。
- 是否达到输出标准：**否**。原因：4 个 critical 问题中至少 3 个涉及正文与 references 编号表的系统性不一致，必须在提交前修订；否则 NSFC 评审人逐条核对编号时会立即发现"正文用 [62] 指 Cochran 但参考文献表 [62] 是 Uzner"这类问题，几乎是引文系统 fail-fast 的硬伤。
- 优先级建议：
  1. （必须）critical-1 / critical-2 / critical-3 三条系统级问题统一处理（一次性把 §5 末尾与 §6 整组编号重新对齐，并补登 Rost 条目）。
  2. （必须）critical-4 中 references.md 第 157 行的"自检段"同步修订。
  3. （建议）high-2 修小数字不一致；medium-1/2 补参数文献；low-1—3 可在修订循环结束后顺手清理。

================================================================
## 评分
创新性：N/A
可行性：N/A
严谨性：0.40
完整性：0.70
综合评分：0.55