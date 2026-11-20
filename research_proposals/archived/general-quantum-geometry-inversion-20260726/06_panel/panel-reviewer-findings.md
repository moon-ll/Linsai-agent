# 评审团定点核查（reviewer·整体一致性，第二轮）

课题 general-quantum-geometry-inversion-20260726 ｜ 视角：跨章数值口径 / 章节衔接 / 参考文献编号连续性 ｜ 2026-10-05
核查方式：程序化复测（引用编号双向差集、模式 grep）+ 关键指标逐章逐行比对。行号以本轮修改前磁盘文本为准。

## 一、r1 遗留靶子

- **V2-1（R#①，r1 V4 残留）[medium] scheme.md:L99**：跨章失效判据口径残留 1 处——"$U/W \gtrsim 1$ 区间的失效点"。同口径各章现状：rationale.md:L43"$U/W > 0.5$ 时…判为失效"、content.md:L107/L159"在 $U/W \approx 1.0$–1.2 区间的失效幅度"、scheme.md:L3（开篇指针"失效界 $U/W > 0.5$ 见 §1.2…1.2 为框架适用上限"）、scheme.md:L129（§4.4"$U/W > 0.5$ 时失效…$U/W > 1.2$ 时进入框架适用边界失效"）、full_review.md:L36 口径表行。scheme:L99 是唯一与 content 定量口径（1.0–1.2 失效幅度）不一致的表述。修改建议：统一为"检验单电子紧束缚框架在 $U/W \approx 1.0$–1.2 区间的失效幅度"。修改后 grep `失效点` 应仅余 scheme:L161"外推失效点"（合法异义，不改）。
- **V2-2（R#④，r1 观察⑨）[low] content.md:L151 ↔ scheme.md:L145**：Σ 代理库预计算启动时点季度级张力。scheme §5.1 时间线：第 2 年一季度粗档（12221 点）→ 二季度全档（17776 点）；content:L151 现文把"代理库预计算"与"R4 自第 2 年二季度启动"绑在同一动作（scheme:L19 亦定义 R4 = 第 2 年二季度–第 4 年四季度）。修改建议：content:L151 拆分为"损失函数设计自二季度启动；Σ 预计算按研究方案 §5.1 时间线先行（一季度粗档、二季度全档）"。数值核算（本轮新查）：16×11×101 = 17776 ✓、11×11×101 = 12221 ✓、17776×(0.5–1.5) GPU·h = 0.9×10⁴–2.7×10⁴ ✓、粗档 6.1×10³–1.8×10⁴ ✓、总算力下界 0.9×10⁴+10³+1.152×10³ ≈ 1.1×10⁴ ✓ 上界 2.9×10⁴ ✓、20 卡并行 550–1450 h ≈ 23–60 天 ✓——scheme 内算力链自洽，仅需消除 content 侧时点措辞张力。
- **V2-3（r1 遗留④）[low，待核延续] references.md:[4]**："Nat. Mater., 2026 (advance online publication, 卷期待 CrossRef 回填)"。声明性遗留，保留原样，待外部元数据。
- **V2-4（R#③，r1 V16/T6 残留）[medium，不适用-越权] 03_method/method-manual.md**：本轮实查手册仍为"该格式在 NEwwave 基础上扩展两个关键字段"（§3.6），与五章正文（content:L117、scheme:L123"自建该格式，不沿用既有标准…三个领域专属字段"）存在字段数 2 vs 3 与扩展基础表述双互斥；5%→3σ 约定声明同样在手册侧待补。03_method/ 属本轮禁改目录，移交 method-manual 维护链（update_method_manual 任务族）处理，交接说明见修改报告"遗留与风险"。

## 二、程序化复测通过项（本轮新查）

- **V2-5 引用编号连续性与闭环（修改前基线）**：references.md 编号 1–50 连续无重号；四章 cited-not-defined = []、defined-not-cited = []（50/50 双向闭合）。[N] 计数：rationale 59 / content 28 / scheme 55 / full_review 2。本轮 researcher S2-2（T3）拟新增 [51] 条目并在 content:L41 补挂，修改后须复验 51/51 闭合。
- **V2-6 跨章关键指标口径逐项比对（通过，不改）**：
  - 失效界 $U/W > 0.5$：rationale:L43 / content:L83 / scheme:L3、L129 / full_review:L36 —— 一致。
  - 主区 ≲1.0、扩展区 ≤1.2、$n \leq 11$、$r \leq 1.5$（r=1 ≈ 8.69 dB）：rationale:L65/L73、content:L15、scheme:L3、full_review:L34 —— 一致（"≲/≤"混用为 r1 已接受的表述容差）。
  - 红移判据 $\Delta\omega/\omega > 2\%$：content:L107 / scheme:L129 / full_review:L33 —— 一致。
  - 偏振突变 ≥ 2°（避开 1.5° 边缘值）：rationale:L49 / content:L91 / scheme:L105、L127、L187 —— 一致。
  - $\mathcal{R}_{\Omega,g}^{\text{CDW}} \geq 2$ 乘性必要条件 + 三档 + <1.2 降级：rationale:L61 / content:L97/L99/L161 / scheme:L43/L115 / full_review:L35、L37 —— 一致。
  - Bi₂Te₃ 判据 0.05 Å⁻¹/20%/30%：content:L73 / scheme:L93 / full_review:L38 —— 一致。
  - 训练分档阈值（5%/8%、15%/25%、20%/30%）与 f-sum 阈值（<5%、×(1+0.5·U/W)、×1.5）：content:L129/L133 / scheme:L133/L161/L167/L171 / full_review:L22–L31 —— 一致（6.25%/7.5% 插值核算正确）。
  - 产额下界 $10^{-5}$ / Plan B $10^{-6}$×6 个月 / $g^{(2)}(0)>1.5$：content:L43/L51 / scheme:L53/L59/L179 / full_review:L17–L18 —— 一致。
  - R3 任务 2 时段"第 2 年四季度–第 3 年四季度"：content:L103/L153 / scheme:L19、L117 / full_review:L32 —— 一致。
  - HMG-Schema 三字段名（quantum_geometry_metadata / cryogenic_environment / bsv_quantum_light_metadata）：content:L117 / scheme:L123 逐字一致。
- **V2-7 full_review 语义（通过）**：全文 CJK 748 字（≤3000 字），保持"主线论证链 + 章节衔接点 + 跨章节统一口径表"的全文骨架语义；口径表 26 行与正文章节号（content §2.x / scheme §x.x）抽查落点正确。
- **V2-8 章节衔接（通过）**：rationale §1.5 双线结构 → content §2.6 年度节点 → scheme §1.2 时序互指闭合；"四步逻辑链"同口径 3 处（见 critic findings）；scheme 开篇三指针（三档→§1.3、适用域→§1.4、失效界→§1.2）与 full_review 衔接点描述一致。
