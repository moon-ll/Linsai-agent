# 评审团亲审 findings — 整体一致性视角（reviewer）

课题：general-order-parameter-ultrafast-readout-20260727 ｜ 执行者：engine亲审 ｜ 日期：2026-10-03
方法：关键指标逐章 grep 定位数值与出处行；参考文献 [N] 双向闭合程序校验；full_review 口径表逐行对账正文。

## 问题清单

### V-1 [high] ±7 T 磁场切换时长与自述计算公式不符（数值口径不一致）
- 位置：scheme.md L71；full_review.md L31（口径表"装置磁场范围"行）
- 摘录：scheme L71 "±7 T 正反方向切换（含稳定时间）按 **45—150 分钟**量级规划实验时序（按 14 T 全变程 ÷ 变场率上下限计算）"
- 复算：14 T ÷ 0.1—0.3 T/min = **47—140 分钟**。正文声称"按…计算"却写 45—150（向外放宽的包络），两数不自洽，评审可复算挑错。
- 建议：scheme L71 与 full_review 口径表同步改为"47—140 分钟"。

### V-2 [medium] [42] 手性寿命差方向跨文件口径冲突（同 researcher 视角 R-1）
- scheme.md L29 "在 **A-M** 方向上 ~20 fs 的手性寿命差异"（正确，KB 证实）vs references.md L133 注记 "在 **Γ-L** 方向手性寿命差约 20 fs"（错误）。
- 建议：统一为 A-M 方向，修 references.md 注记。

### V-3 [medium] full_review ② 衔接点与 content §2.0 的科学问题结构不齐（Q0 缺失）
- 位置：full_review.md L11
- 摘录："§一.3 凝练的 **Q1+Q2** 在 §二.0 落地为 **G1/G2/G3 与 Q1/Q2 双向对应**"
- 问题：content §2.0（L13）实为"一个资格条件（Q0）与两个递进子问题（Q1/Q2）分别对接 G1、G2 与 G3"；骨架表述漏 Q0 且"G1 与 Q1/Q2 双向对应"映射错位（G1 对接 Q0 而非 Q1）。full_review 的职能即对账衔接，自身口径必须与正文严格一致。
- 建议：改为"§一.3 凝练的两个递进子问题在 §二.0 落地为资格条件 Q0 与子问题 Q1/Q2，分别对接 G1/G2/G3"。

### V-4 [low] 参考文献格式小瑕疵两处（无法在 KB 内核实，保留待核）
- references.md L161（[48]）："current version cited: **v4**" 无版本日期，与 [27] "current version cited: v2, 2026-05-13" 格式不齐。
- references.md L91（[33]）："arXiv:2607.23652 (v1, **2026-07**)" 月份精度，与全文"YYYY-MM-DD"精度不齐。
- 建议：需 arXiv 实查后补齐，本轮不改（禁止凭记忆构造版本日期）。

## 核验通过记录
1. **关键指标跨章口径逐项一致**（数值 | 出处行）：
   - CrSb Néel 733(4) K [27]：rationale L57 / content L33 / scheme L35 / full_review 表 ✓
   - MnTe Néel 约 310 K（仅"近相变"，无"跨相变"表述）：rationale L61 / content L71 / scheme L35、L73 ✓
   - TiSe₂ CDW 约 200 K：rationale L21、L47、L63 / content L25 / scheme L75 ✓
   - σ=0.5%—0.8%（预研实测）、合格线 0.75%—1.6%：rationale L43 / content L9（指针）/ scheme L11、L53 / full_review 表 ✓
   - κ 三档（10²/10⁴）+ 后验 <先验宽度 50%（σ_prior 口径已定义，R7 medium 问题 2 确认修复）：rationale L47 / content L11、L53 / scheme L15、L47、L53 ✓
   - CrSb 带隙初值 0.13（间接）/0.6（直接）eV：rationale L59 / scheme L33 / full_review 表 ✓
   - γ≈0.21—0.95（端点 0.205/0.948，5 μm 下移 40%）：scheme L61、L69 / full_review 表 ✓
   - 驱动场强 0.3—0.8 V/Å ≈ 1.2—8.5×10¹² W/cm²、降场强预案 0.1—0.3 V/Å：scheme L61、L67 / full_review 表 ✓
   - 温区 4—300 K（MnTe 至 310 K）、损伤阈值反射率变化 >5%、装置磁场 0—7 T：各章一致 ✓
   - FIM 7 参数（能带 3+序参量 2+SOC 2，7×7 维）：rationale L47 / content L11、L51 / scheme L47、L49 / full_review 表 ✓
   - MnTe 分裂 0.8 eV [38]、d 波先验 0.1—1.0 eV、Zeeman 0.81 meV、k_BT_N≈63 meV、手性磁振子 27(2) meV（Γ-L，L 点）：各处一致且经 KB/复算证实 ✓
2. **参考文献编号完整性**：正文 4 文件共引 [1]—[49]，references.md 49 条编号条目双向闭合——引用无缺条、无未引用条目、1—49 无跳号；分组内编号连续（R8 的 [11] 乱序已修复）；条目正文无评审日志残留（R8 medium 问题确认未复发）。
3. **full_review 语义与字数**：2410 字（不含空白）≤3000 上限；结构为主线论证链（①）+章节衔接点（②）+统一口径表（③），无逐项处置记录；③ 口径表逐行有正文出处（R7 问题 4 的孤儿值 290—310 K/E₂g/Level 2 已不存在），"altermagnet 仅 3 处定义括号"声明与正文实测一致。
4. **R7 遗留对账确认**：问题 2（先验宽度口径）已修；问题 3（[27] 归属）经 KB 核实为真；问题 7（检索日期三现）已统一为 2026-08。
