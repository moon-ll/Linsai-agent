# 对抗评审报告（第 2 轮·参考文献专项）
- 项目类型：general｜对象：sections/references.md（50 条）｜日期：2026-10-01
- 方法：不限于预检点名条目，50/50 全量反查——35 个 DOI 走 doi.org CSL-JSON/CrossRef，21 个 arXiv ID 走 arXiv API，逐条五件套比对（题名/首作/作者链/刊卷页/年）；另 grep 三正文章节核实挂钩真实性

## 核验结论（先核实再下结论）
- 真实性：49/50 条目与公开记录匹配。R1 已验的 33 条（现 [1]-[31]、[47]、[48]）复验仍全真；R1 后扩容的 17 条中检出 1 条作者链虚构（[45]）、2 条 DOI 错挂（[32][38]）、1 条作者名错（[49]）、1 条 † 过期（[43]）。
- 预检处置：预检称 23 条未入检索池但仅列 15 个编号，本报告按全量 50 条反查覆盖之。点名的 15 条中仅 [32] DOI 错挂；最重的 [45] 不在点名清单内——"凭学科知识引用"风险不止于预检点名集，全量反查政策再次验证。
- 相关性：抽验 [31][14][30][50][49] 挂靠语境均服务科学问题（Fisher 判据/层析/PINN/FAIR/量子度规），无无关引用。
- 时效：2023 年及以后 32/50（64%），2025-2026 占 26 条，时效优。
- 编号连续 1-50 无缺口（采信预检）；无重复 DOI/重复 arXiv；[12]/[44]、[13]/[43] 同组不同文，均真实非重复。

## 问题清单
[critical]｜[45] L93｜arXiv:2512.06602 真身为 González-Monge/Willemann/Feist 3 人，条目 Tsur/Birk/Gorlach 等 6 人作者链虚构｜action:rewrite｜按 arXiv 真身重录作者与题名；或改引 Tsur 团队真实文献并核 ID
[high]｜[32] L67｜DOI 10.1007/BF02193888 解析到 1962 年 De Economist 经济学论文，非 Provost-Vallee｜action:rewrite｜DOI 改为 10.1007/bf02193559（CMP 76, 289-301）
[high]｜注释块 L151-155｜[42]-[46] 三正文及 full_review 全零引用，注释却标"§1.1/§1.4/§2.2"假挂钩，与 L109"已与挂钩一致"声明自斥｜action:verify｜五条补挂正文 [N] 或删条；删条可同步消减超标
[medium]｜全表｜总数 50 条超 20-40 区间（预检膨胀告警）｜action:remove｜删未引用五条后再筛（如同组 [12]/[44] 二选一），压至 ≤40
[medium]｜[38] L79｜DOI 10.1038/386471a0 双通道 404；条目卷页 387:471-475 本身正确｜action:rewrite｜DOI 一位之误，改 10.1038/387471a0
[medium]｜[43] L89｜arXiv:2502.11803 已刊 PRA 111, 063105 (2025)，仍标 † 且缺正式版｜action:rewrite｜去 †，改录 DOI 10.1103/PhysRevA.111.063105 卷期页
[medium]｜[49] L101｜第 5 作者"V. Liang, N."查无此人，Science 记录为 V. Trevisan, T.｜action:rewrite｜按 DOI 10.1126/science.adf1506 作者记录改第 5 作者
[medium]｜L3 凡例+L107-159｜凡例与挂钩注释属过程性工作日志；[26]"本表暂保留"、[49]"待挂靠"状态已过期（MgO 已改挂 [18]、rationale 已现 [49]×1）｜action:remove｜注释块迁移 05_review；若保留须逐条对账刷新
[low]｜[4] L11｜AOP 卷期仍未回填（R1 遗留未解决）｜action:verify｜投稿前 CrossRef 复核回填 Nat. Mater. 卷页

## 锚点对比
- 引用（L93 条目原文）："[45] †Tsur, S., Birk, M., Gorlach, A., Krüger, M., Kaminer, I. & Cohen, O. High-harmonic generation driven by temporal-mode quantum states of light. arXiv:2512.06602 (2025)."
- 对比（arXiv API id_list=2512.06602 返回）：authors = Juan M. González-Monge, Felipe Reibnitz Willemann, Johannes Feist；title = "High-harmonic generation driven by temporal-mode quantum states of light"；无 journal_ref。
- 差距：题名与 ID 真实，但三位真实作者被整体替换为 Tsur/Birk 等 6 人链——典型"真题真 ID 混作者"，仅凭格式或题名查重无法发现，必须反查作者字段。
- 锚点结论：[45] 作者链虚构坐实，critical 立案。

## R1 问题对账（8 项）
已解决 6：具名无 [N] 集群（[32]-[41][49] 补入且正文挂靠）、[26]→[18] MgO 错挂（rationale 现引 [18]）、Verma-Queiroz 补条 [37]、[48] 年份统一 2025、[47] 补 †、[27] 页码补全、编号断档消除。未解决 1：[4] AOP 卷期。新增 9：见问题清单。

## 对抗结论
本轮 9 个问题（critical:1, high:2, medium:5, low:1）。相比 R1：改善 7（含全部 R1 high），新增 9，未解决 1。评分自 R1 0.81 大幅回落，根因是 R1 后 17 条扩容引入新雷：1 条作者链虚构、2 条 DOI 错挂、5 条未引用条目并以假挂钩注释掩盖——"先入检索池再入表"的纪律未被执行。未达输出标准。返工优先级：① [45] 按真身重录或换引；② [32][38] DOI 更正；③ [42]-[46] 补挂或删除并压总数至 ≤40；④ [43][49] 字段修正；⑤ 注释块迁移 05_review。下轮 writer 若补充检索命中文献，须回录 02_literature 检索池（R7 教训）。

## 评分依据
严谨性 0.38：49/50 真且五件套基本准确，但 [45] 作者链虚构触发 critical 虚构档（0.3-0.4 区间），叠加 2 处 DOI 错挂与 1 处作者名错。完整性 0.62：时效优（64%）、无正文断言缺源；扣总数超标 10 条、5 条零引用条目、假挂钩注释误导交叉核对。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.38
完整性：0.62
综合评分：0.50
