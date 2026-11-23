# 对抗评审报告：参考文献第 3 轮（general-ssh-weyl）

## 综合评分
0.55 / 1.00

## 维度评分
| 维度 | 权重 | 得分 | 问题数 |
|------|------|------|--------|
| 严谨性 (rigor) | 0.5 | 0.40 | 9 |
| 完整性 (completeness) | 0.5 | 0.70 | 6 |

（注：本轮仅评"引文真实性/格式/数量/时效"，创新性/可行性按契约填 N/A；未走 NSFC general 5 维加权。综合评分 = (严谨性+完整性)/2 = 0.55。）

## 本轮方法
对 14 条预检标记的"凭记忆引用"（[1,2,3,4,6,9,10,21,25,31,32,33,34,35]）及 arXiv 形式条目全部做 arXiv API / CrossRef API 反查；抽样 9 条关键 DOI 做标题/首作/卷期一致核对。重点反查对象：[27] Liu（彭良友）/[28] Lv β-WP₂（双轨）/[30] Jessen ZnO。

## 锚点对比

**申请书 [28] Lv β-WP₂ 锚**：
"Y.-Y. Lv 等, 'High-harmonic generation in Weyl semimetal β-WP₂ crystals,' Nat. Commun. 12, 6437 (2021); DOI: 10.1038/s41467-021-25899-0; arXiv:2107.07607"

**CrossRef 实测 + arXiv 实测**：
- DOI 真实：`10.1038/s41467-021-26766-y`（API 返回 Lv 等首作、Nat Commun 12, 6437, 2021 完全一致）；申请书写 `...25899-0` **不存在于该文**
- arXiv 2107.07607 实测标题："An epsilon-near-zero-based Dallenbach absorber"（Medvedev 2021, Opt. Mater.，与 Lv 论文无关）
- Lv 论文真实 arXiv ID 经多源核实无对应预印本——该文为 Nat Commun 直投，未挂 arXiv
- 整条锚链 3 项全错，是本轮最严重 P0

差距：申请书 [28] 锚文形式要素齐全但 DOI 与 arXiv ID 全部为虚构/张冠李戴；建议仅保留 DOI `10.1038/s41467-021-26766-y` 一项，去除 arXiv 字段，或将 [28] 改挂同主题已实测 arXiv ID 的替代条目（如 Medic PRB 109, 205130 [23] 已实测真实）。

## 反向核查清单（API 实测）
- arXiv ID 全量验证（10 条，全部存在且标题匹配）：2405.16125 / 2604.21121 / 2604.06051 / 2608.22136 / 2602.16454 / 2603.05346 / 2609.06119 / 2508.15631 / 2507.09234 / 2510.15207 ✓
- DOI 实测正确：[1][3][4][5][6][9][10][11][14][22→误标为综述 / 实际 [24][25][29][30→存疑] 见问题清单] —— 见下方分项
- DOI 实测错误（critical）：[28] DOI 与 arXiv ID 双错；[27] arXiv ID 错挂 ML 论文
- DOI 形式问题（medium）：[30] Jessen 用卷页形式 `10.1103/PhysRevB.112.214311`，实测 hash DOI 为 `10.1103/b56l-hvgn`（期刊页码对应正确，但 DOI 字符串形式不规范）

## 问题清单
[critical]｜references.md [28]｜DOI 错写为 ...25899-0 实测真身为 ...26766-y｜更正 DOI 为 10.1038/s41467-021-26766-y
[critical]｜references.md [28]｜arXiv:2107.07607 实为 Medvedev Dallenbach absorber 非 Lv 论文｜删除 arXiv 字段(Lv 论文无 arXiv 版)或改挂实测真实 arXiv 替代
[critical]｜references.md [27]｜arXiv:2507.14725 实为 ML "GRID: Continual Prompt Tuning" 非 HHG 论文｜删除 arXiv ID 或换实测 HHG arXiv
[high]｜references.md [30] Jessen｜DOI 形式 10.1103/PhysRevB.112.214311 非 APS 标准 hash 形式｜改为 10.1103/b56l-hvgn (CrossRef 实测真值)
[high]｜references.md [27] Liu 等｜arXiv 缺页×未注双份编号实测为 prompt tuning 工作｜去除 arXiv 字段保留 DOI 即可
[high]｜references.md [25]｜"M. Mrudul" 实测作者全名 "M. Mrudul M." 缩写不规｜核对 CrossRef 全名补全 Mrudul M.
[medium]｜references.md [22] Heide｜注释复用 R2c 模板(拓扑相变非异质结)但与正文 §1 是否一致未联动核对｜核对 rationale.md §1.1-1.2 是否把[22]严格定位为 TI 相变
[medium]｜references.md [26] Duan｜幂律 n: 2.3→0.3 与 R8 校准口径未注场强窗口｜补场强区间与饱和曲线 PDF 复算备注
[medium]｜references.md 总条目｜35条合标但 14 条凭记忆+9 条 arXiv 预印本未刊占 65.7%｜arXiv 占比压缩至 ≤6 条,凭记忆条目逐条 CrossRef/Scholar 反查
[low]｜references.md [22] 表述｜Ciappina 标 arXiv:2510.15207 但说明写"未见刊" arXiv 2025-10 投稿合理｜保留现状但加 "2025-10 投稿" 时间注释
[low]｜references.md [29] Fan et al.｜et al. 后未列全部作者,与 [27] 格式不一致｜统一格式: Fan 等 6 位作者全列或 et al.
[low]｜references.md [32-35] 4 条孤儿｜未引用条目 [31-34] 虽与气相/阿秒背景相关但当前正文未用｜下轮要么新增正文锚定,要么删除仅保留与本课题直接相关的 [35] Schubert GaSe

## 工作日志污染检查
references.md 无 TODO/TBD/占位符；预印本标注 "未见刊" 9 处与内容策略一致；未发现工作日志污染需迁移 05_review 的内容。

## 对抗结论
- 本轮发现 12 个问题（critical:3, high:3, medium:3, low:3）
- 相比 R2（critical 3, high 4, medium 4, low 2）：R2 三条 critical ([21][39][43]) 已被本轮删除/纠正（[21] You 已实证为 ZnO 非 graphene；[39] MgO 错位已重选；[43] 已重写）；但 R3 新发现 [27][28] 双 arXiv ID 张冠李戴 + [28] DOI 错位 共 3 条新 critical——本质属 R7 教训再现：凭记忆补 arXiv 字段时容易张冠李戴。
- 是否达到输出标准：否——3 条 critical (含 1 条占 β-WP₂ 实验核心锚的 [28]) 直接拉低严谨性至 0.40；下轮须严改后才能接近 0.75+ 出版水
- 返工优先级：P0=[28][27] 三连 + arXiv 占比压缩；P1=[30] DOI 形式规整；P2=作者全名统一

## 评分
创新性：N/A
可行性：N/A
严谨性：0.40
完整性：0.70
综合评分：0.55
