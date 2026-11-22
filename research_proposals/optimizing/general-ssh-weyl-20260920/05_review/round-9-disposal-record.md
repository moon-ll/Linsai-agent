# 处置记录：第 9 轮（整体一致性修订）

**课题**：general-ssh-weyl-20260920（面上 general）｜**日期**：2026-10-30｜**修订范围**：整体一致性（章节衔接、术语统一、冗余删减），聚焦表达质量
**输入**：`critic-round-8-full_review.md`（8 条问题，critical 0 / high 3 / medium 4 / low 1）+ 历史遗留 P0/P1 清单 + 定向检索报告 `lit-gap-1793321173.md`

---

## 一、R8 问题清单逐条处置

| # | 级别 | 定位 | 问题 | 处置 | 状态 |
|---|---|---|---|---|---|
| 1 | high | C:L13/L37/L49、R:L31、S:L63 | [20] v1→v2 版本收敛史正文 5 现 | 仅 R:L31 保留全史；C:L13 改"报告拓扑相相对平庸相谐波产额峰值增强达两个数量级"、C:L37 删去整句、C:L49 改"上限两个数量级所对应的 log₁₀ 比值"、S:L63 改"报告的拓扑相增强上限两个数量级"。版本史现数由 5 降为 1（正文）／1（口径表）／1（参考条目） | 已消除 |
| 2 | high | R:L29 ↔ C:L25 | Liu ESSH 三组句跨章近逐字双现 | C:L25 首句改为视角性引用"ESSH 选择定则的偶/奇宇称维度为方向二的边界态判据提供了新维度。如立项依据所述，…"，删 Liu[12] 推广与光斑移位的复述。"七条线索"改为显式列举以保住计数可核 | 已消除 |
| 3 | high | 全稿（scheme 集中） | 程序超长句 severe 11 超免赔 7，罚 0.08 | 逐句按分号／冒号边界拆分：S:L9 指标覆盖句（147→三句）、S:L53 Korolev 句（132→两句）、S:L65 与 S:L185 δ_CD 计算式句、S:L219 失效情形句（167→两句）、S:L231/L237/L243 三处创新点量化收束句（156/123/198）、S:L53 创新点二首句、C:L25/C:L27。正文三章实测真超长句 0（仅余 δ_CD 公式行，LaTeX 计入字符导致的程序误报） | 已消除 |
| 4 | medium | S:L237 ↔ S:L53 | Δt 30/3≈10 fs 推导与时窗 ≥30 fs 在创新点二近逐字复述 | L237 末句改"Δκ 与 Δt 的阈值依据同判据形式化一节所述，由大样本参数反演与时间分辨扫描自定标给出" | 已消除 |
| 5 | medium | S:L269 ↔ S:L67 | G1 与三指标"同一套验收条件+互为补数"句章内两现 | L269 改"其样本平衡与不平衡的处理规则同判据形式化一节" | 已消除 |
| 6 | medium | S:L11 | 内联 `arXiv:2604.06051` 绕过 [N] 角标体系 | 改"第一类是 Li 等人[8]（预印本）报告的 Bi₂Se₃ 厚度-双色场分离数据" | 已消除 |
| 7 | medium | C:L13 ↔ R:L31 | [20] 增强归属两版（R 三类拓扑绝缘体对比 vs C 呼吸 Kagome 单模型） | **联网逐版核实 arXiv:2508.15631**：v1（2025-08-21）摘要为"for the topological semimetal phase, we find a harmonic enhancement by two to three orders of magnitude in the Kagome lattice"；v2（2026-05-24）摘要为"we identify significant enhancements of the harmonic intensity yields, reaching up to two orders of magnitude relative to trivial phases"，且模型为 Haldane／Kane-Mele／breathing Kagome 三个紧束缚模型分别对应 Chern／TI／HOTI。据此判定：两版陈述的**归属范围本就不同**（v1 限定 Kagome 拓扑半金属相，v2 覆盖拓扑相整体），critic 判定的"单模型收窄"为真实缺陷而"三模型"表述本身准确。统一方案：全稿改挂三模型对比口径（与 v2 摘要一致），删除"Kagome 紧束缚模型上对比 Haldane、Kane-Mele 与 breathing Kagome 三类拓扑绝缘子"这一把 Haldane／Kane-Mele 说成 Kagome 模型内部相的错误句法。C:L13／R:L31／R:L49／R:L73／R:L77／C:L7／S:L179／full_review 口径表／references [20]／00_research_idea.md 全部同步 | 已消除（含一处原句法错误） |
| 8 | low | S:L261 ↔ S:L269 | 两处"四类体系"枚举互异 | L269 改"十二项指标在一维 SSH、二维 Qi-Wu-Zhang、三维 BHZ 推广 HOTI 与三维 Weyl/TI/HOTI、ZnO 四类体系上完成度量与验证，TaP THz 三次谐波数据作为散射贡献参数的校核基准"，与 L261 体系枚举一致并把 TaP 明确为校核数据而非体系 | 已消除 |

## 二、历史遗留问题核对

| 遗留项 | 归属 | 核对结果 |
|---|---|---|
| [critical] Δt 拟合时窗下限两版（L53 取 [14] 25 fs / L233 要求 ≥30 fs） | scheme | **已消除（上一轮）**。本轮复核 S:L53 为单一段落，内含"拟合时窗下限取 ≥ 30 fs"与"25 fs 驱动窗仅作时窗裕量参考"，非两版。L237 原整段复述已改指代，本轮不再有第二处推导 |
| [critical] full_review [20] 版本归属三处颠倒 | full_review | **已消除（上一轮）**。本轮重写骨架后口径表行为"Lorenzo 等人[20] 2025（预印本）：Haldane、Kane-Mele、breathing Kagome 三模型对比，摘要『reaching up to two orders of magnitude relative to trivial phases』；首版二至三个数量级，第二版收敛为上限两个数量级"，与 canonical 一致 |
| [high] rationale 超长句 4 句（L67 334 字、L71 281 字） | rationale | **已消除（上一轮）**。本轮实测 rationale 真超长句 0 |
| [high] rationale 20 处节号自指 | rationale | **已消除（上一轮）**。本轮 grep 复核 rationale 全文 `§` 计数为 0 |
| [high] [37] MgO 挂 Weyl 节点动力学维度 | rationale | **已消除（上一轮）**。R:L55 现行表述为"该工作在强场 Berry 相位动力学的方法维度与 β-WP₂ 理论互为参照" |
| [high] R:L67 ↔ R:L103 两条实验基准章内两现 | rationale | **已消除（上一轮）**。R:L67 现为国内研究现状两处空白，R:L103 为散射贡献 Z 的上下限约束分工 |
| [high] content 5 句超长句 | content | **已消除（上一轮）**。本轮实测 0，且新增拆句后仍为 0 |
| [high] content 19 处导航指针 | content | **已消除（上一轮）**。本轮复核跨章指针仅 1 处（"研究方案 §2.2"），密度 0.19/千字，低于 ≤1/千字预算 |
| [high] scheme §5.1"四项指标" vs §7.2"三项细指标+G1" | scheme | **已消除（上一轮）**。本轮复核两处均为"三项指标与终止判据 G1 构成同一套验收条件"，L269 改指代后不再展开 |
| [high] scheme §7.4 晶体取向参数落空 | scheme | **已消除（上一轮）**。S:L91 含晶体取向扫描步 |
| [medium] 创新点三/四处"第五次谐波谱形转变"三现 | 跨章 | **已消除（上一轮）** |
| [medium] rationale/content [20] v1→v2 收敛史三现 | 跨章 | **本轮已消除**（见问题 1） |

## 三、本轮附加修订（表达质量专项）

1. **冗余修饰词与死板关联词逐词削减**："同时" 5→2（rationale 三处改"还"、"前提下"）；"完整" 1→0（方案判据形式化"至少一个完整的衰减周期"→"至少一个衰减周期"）；"有效" 8→7；"系统" 6→5（余下为"系统比较/系统分析"动词用法与白名单"系统误差"）。新增"在此基础上""此外""与此同时""基于此""然而""因此""值得注意的是""需要指出""为…提供…基础/支撑/途径""本项目拟/将"0 命中。
2. **禁用词"口径"清除**：full_review 标题与表头"跨章节统一口径表"→"跨章节统一表述表"。
3. **方案章可行性段落复述**：S:L213 与 S:L179 三条多变量扫描文献近乎重复，S:L213 改指代句。
4. **研究内容 Ilin 邻句重复**：C:L27 合并"Ilin 等人[42]…"相邻两句。
5. **满索引同步**：00_research_idea.md 四处 [20] 表述与本轮口径对齐，头注增写 R12 修订条目；02_literature/reading-notes.md 追加三条阅读记录（[8] 复核、[20] v1/v2 版本归属核实、[18] Thakur）。

## 四、程序化复测结果

| 检测项 | 修订前 | 修订后 |
|---|---|---|
| 正文真超长句（>120 字，去公式块） | 约 5 处 | **0**（余 1 处为 δ_CD LaTeX 公式行误报，中文正文仅约 30 字） |
| 句长中位数 | — | **49 字**（范本约 56 字） |
| 80–120 字技术句占比 | — | **14.7%**（范本 12%–28%） |
| 死板关联词 / 模板句式 / 元话语 | 5 处"同时" | **全 0** |
| canonical 禁用模式（25 项） | — | **全 0** |
| 12 项指标跨章数值一致性 | — | **全部一致**（R_HOTI ≥ 10、S_edge ≥ 0.2、δ_FP < 5%、Δκ ≥ 20%、η_SF ≥ 95%、Δt ≤ 10 fs、X+Y+Z ≥ 95%、σ_dec ≤ 5 个百分点、R² ≥ 0.9、ΔI_rev ≥ 0.5×I_threshold、ΔI_gap ≥ R（R=2）、δ_CD ≥ T（T≥0.3）） |
| full_review 篇幅 | 1347 中文字 | **1406 中文字**（≤3000 上限），三部分齐备，过程性材料零残留 |
| 章节体量 | rationale 6467／content 5527／scheme 10301 | rationale 6515／content 5528／scheme 10256 中文字 |

## 五、文件产出

- 修订：`04_proposal/sections/rationale.md`、`content.md`、`scheme.md`、`full_review.md`、`references.md`（[20] 条目句法修正）
- 同步：`00_research_idea.md`（口径对齐 + R12 头注）、`02_literature/reading-notes.md`（三条阅读记录）
- 组装：`04_proposal/proposal-draft.md` 由 `scripts/proposal_sections.py::assemble_draft()` 重新生成（116415 字节）
- 未触及：`03_method/method-manual.md`（方法学手册单一真相源，由轮末专职步骤维护）

## 六、遗留与说明

1. **δ_CD 公式行程序误报**：S:L65 句"计算式为 $\delta_{\text{CD}} = …$"在字符计数上为 139 字，因 LaTeX 记号计入所致，中文正文部分仅约 30 字。公式属方法学手册归属地，此处保留计算式为指标可操作性的必要条件，不作删除或改写。
2. **无待解决 P0**：R8 三条 high 与历史 P0/P1 清单逐条复核后均已消除或确认消除。
3. **本轮为一致性修订**，研究内容、技术路线、创新点无重大调整，故课题设想仅作口径同步而非结构重写。
