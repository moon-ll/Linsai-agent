# 对抗评审报告（Round 1 · 参考文献专题）

## 元信息

| 项 | 值 |
|----|-----|
| 评审轮次 | Round 1（参考文献检验专题） |
| 项目类型 | NSFC general（面上） |
| 评审章节 | references.md + 三个正文章节（rationale / content / scheme） |
| 评审日期 | 2026-09-11 |
| 评审范围 | 引文格式、作者信息完整性、引用相关性、缺失引用、引用数量、时效性 |

## 数据快照（机器提取）

| 指标 | 数值 |
|------|------|
| 参考文献条目总数 | 49（预检已确认） |
| 正式发表条目（含 DOI 且非纯 arXiv DOI）| 28 / 49 ≈ 57.1% |
| 预印本条目（仅含 arXiv DOI）| 18 / 49 ≈ 36.7% |
| 无 DOI/arXiv 条目 | 1（[27] Fazekas-Tosatti） |
| 近 3 年（2024–2026）文献 | 30 / 49 ≈ 61.2% |
| 中间年份（2010–2014）文献 | 2（[31] 2010、[34] 2011） |
| pre-check 标记 31/48 条 DOI 未在检索产物中匹配 | 是 |

## 综合评分

0.68 / 1.00（参考文献不合格：发现 4 处 critical 级别的作者/编号错位，触发 P0 红线 no_exaggeration；rigor 强制扣至 0.6-0.7 区间；建议本轮必须修复后方可进入下一轮）

## 维度评分

| 维度 | 权重（仅参考文献两维度） | 得分 | 问题数 |
|------|---------|------|--------|
| 严谨性（rigor） | 0.50 | 0.65 | 7（5 critical, 1 medium, 1 low） |
| 完整性（completeness） | 0.50 | 0.72 | 4（1 critical, 2 medium, 1 low） |
| **综合** | — | **0.68** | **11** |

## 维度评分依据

严谨性 0.65：rationale.md 出现 4 处 critical 级别的 [N] 编号—作者—内容三重错位（Baykusheva→[26]、Du→[27]、Bauer→[12]、Uchida/Murakami→[12]），4 条正文引用全部指向错误条目或伪造的作者归属，构成 P0 红线（no_exaggeration / consistency_check）；[42] DOI 格式 10.1103/8lhh-gq58 不符合 PRR 期刊标准 DOI 模式（疑似手稿 ID 误填）；其余条目作者/期刊/年份基本完整。按 v6.9.25 评分纪律，P0 红线触发 → rigor 强制扣至 0.6-0.7 区间，取 0.65。

完整性 0.72：49 条总数超过 20–40 标杆上限 9 条（轻微超标）；近 3 年文献占比 61.2%（良好）；预印本条目 18 条（占 36.7%，部分条目未联网核实即纳入主列表）；中间年份（2010–2014）覆盖率低（仅 2 条）；引用相关性整体良好，但 Baykusheva/Du/Bauer/Uchida 四条错位条目的内容主题与 references.md 中的 [26][27][12] 完全不匹配，造成"正文论断找不到对应文献"的事实空缺。

---

## 锚点对比

锚点 1：references.md 的格式声明（references.md 第 3 行 "[1]–[28] 全部经 DOI/arXiv 单源核验；[29]–[41] 为经典奠基文献通过多份综述交叉引用确认"）

benchmark 对比：成熟的 NSFC 面上项目参考文献应在格式说明中明确"正文—编号交叉自检表"，主动披露"是否有列而未用"的条目。

差距：当前文档未提供自检表。本轮机器扫描发现 4 处正文—文献对应错误，全部来自 rationale.md 三段证据线的多体 HHG 论述。这些错位并非 [N] 编号本身缺失，而是 [N] 编号虽然存在，但正文叙述内容与编号指向条目的真实作者/标题完全不匹配——这是比"列而不用"更严重的"用而错位"。

锚点 2：rationale.md 第 21 行多体 HHG 段（"Silva 等 2018 年 [4] 在 Sr₂CuO₃ 上建立了一维 Mott 绝缘体 HHG 的奠基性观察"）

benchmark 对比：嵌入式引用应满足"作者名 + 编号 + 期刊/年份 + 一句话内容"四要素与对应条目严格一致。

差距：本段同一句话内嵌 4 处引用，其中 Baykusheva [26] 与 Du [27] 的引用编号与 references.md 中的实际条目完全错位——[26] 是 Aversa-Sipe 1995（半导体非线性极化率张量分解理论），[27] 是 Fazekas-Tosatti 1979（1T-TaS₂ 电学/磁性实验）。这两条错位不是引用格式问题，而是"正文叙述指向真实存在的论文，但该论文并不在所标 [N] 编号条目中"。这是 NSFC 评审眼中典型的文献不严谨信号。

---

## 问题清单

### [critical] 编号—内容一致性 — Baykusheva 等 2026 年 [26] 实际指向 Aversa-Sipe 1995
- 位置：rationale.md 第 21 行、第 29 行、第 41 行（三处）；references.md 第 53 行 [26]
- 问题：正文三处将 "Baykusheva 等 2026 年 [26] 在 Sr₂CuO₃ 上以 Floquet 工程实现 Hubbard 激子量子相干控制" 归于 [26]，但 [26] = Aversa & Sipe PRB 52, 14636 (1995) 关于半导体非线性极化率张量分解
- 建议：删除四处 [26] 引用，补入 Baykusheva 真实条目（floquet 工程 + Hubbard 激子对应 2024-2026 期间 PRX/PRL），并按新条目号全章同步；如找不到真实出处则改写为"近期理论预言"叙述
- action：research + rewrite

### [critical] 编号—内容一致性 — Du 等 2026 年 [27] 实际指向 Fazekas-Tosatti 1979
- 位置：rationale.md 第 21 行、第 29 行、第 41 行（三处）；references.md 第 55 行 [27]
- 问题：正文三处将 "Du 等 2026 年 [27] 在一维 Hubbard 模型上以精确对角化追踪 doublon-holon 动力学" 归于 [27]，但 [27] = Fazekas & Tosatti Philos. Mag. B 39, 229–244 (1979) 关于 1T-TaS₂ 掺杂实验
- 建议：删除三处 [27] 引用，补入 Du 真实条目（一维 Hubbard 精确对角化 doublon-holon 动力学）或改写为"近期多体精确对角化工作"叙述
- action：research + rewrite

### [critical] 编号—作者一致性 — Bauer 等 2026 年 [12] 实际作者为 Cárdenas
- 位置：rationale.md 第 41 行；references.md 第 25 行 [12]
- 问题：正文称 "Bauer 等 2026 年 [12] 在 MoS₂ 与 NbSe₂ 的对照计算"，但 [12] = Cárdenas, Silva & Jiménez-Galán arXiv:2604.13901，Bauer 不在作者链
- 建议：核实正文所指工作的真实作者链（MoS₂/NbSe₂ 对照 + 电子-电子相互作用对 HHG 修正）；若为独立论文则新增条目并分配新 [N] 编号；若为 [12] 内容的误传则改回 Cárdenas 归属
- action：research + rewrite

### [critical] 编号—作者一致性 — Uchida、Murakami 等 2026 年 [12] Uchida 不在引用库
- 位置：rationale.md 第 21 行、第 41 行；references.md 第 25 行 [12]
- 问题：正文两次称 "Uchida、Murakami 等 2026 年 [12]"；Uchida 在 references.md 中无对应作者链；Murakami 实为 [13] Ikeda 等论文的第二作者（[13] = Ikeda, Murakami, Sakai, Miyamoto, Ito & Okamoto）；正文把 SrCuO₂/Pr₂CuO₄ 维度效应工作归于 [12] 与 Cárdenas arXiv 条目内容不一致
- 建议：核实 SrCuO₂/Pr₂CuO₄ 维度对比 HHG 工作的真实作者链；如属 Okamoto 组的关联工作应改引 [13]；如为 Uchida 独立论文则新增条目
- action：research + rewrite

### [critical] 引用数量 — 49 条超出 30–40 篇标杆上限 9 条
- 位置：references.md 整体
- 问题：参考文献总数 49 条，超出面上项目 30-40 标杆上限 9 条；预印本条目 18 条占比 36.7%（部分条目标注"待 2026-Q4 联网核实"但已纳入主列表）
- 建议：将 18 条预印本中方法学借鉴定位条目（[15][16][18][23][24][47] 等）降级为"研读基础附录"，主列表压缩至 ≤40 条；同时联动解决 4 条错位引用问题
- action：remove

### [critical] 格式细节 — [42] DOI 格式 10.1103/8lhh-gq58 不符合 PRR 标准模式
- 位置：references.md 第 85 行 [42] Thorpe et al. Phys. Rev. Research 7, 043284 (2025)
- 问题：PRR 标准 DOI 应为 10.1103/PhysRevResearch.X.XXXXXXX；"8lhh-gq58" 形式疑为手稿 ID 误填入 DOI 字段，无法在 doi.org 解析
- 建议：通过 CrossRef 重新核实 [42] 真实 DOI；若 [42] 已正式发表则修正 DOI 字段，若仍为预印本则改回 arXiv 编号
- action：verify + rewrite

### [medium] 时效性 — 2010–2014 中间区间文献覆盖低（仅 2 条）
- 位置：references.md 整体
- 问题：2010–2014 区间仅 [31] Xiao-Chang-Niu 2010 综述与 [34] Ghimire 2011 实验，2012–2014 完全空缺；该区间正值固体 HHG 理论与拓扑材料发展期
- 建议：在 references.md 第 3 行"核验说明"段补一句"2012–2014 文献以气体 HHG 与早期拓扑材料为主，与 BSV × 固体能带 × Berry/度规交叉点无直接对应故未引用"；或选择性补入 Schubert 2014、Higuchi 2014 等关键文献
- action：add（解释性备注）/ research

### [medium] 完整性 — 18 条预印本条目标注"待 2026-Q4 联网核实"但已入主列表
- 位置：references.md 第 23–47 行 [11][12][15][16][17][18][20][21][22][23][24][44][46][47][48][49] 等条目末尾
- 问题：18 条预印本条目末尾均标注"正式发表状态待 2026-Q4 联网核实"——但本评审日期为 2026-09-11，距 2026-Q4 约 1.5 个月，主列表纳入未联网核实文献存在预印本 ID 错填风险（R7 实测教训）
- 建议：writer 在下一轮优先对 [11][12][15][16][17][44] 等正文高频引用条目做联网核实；核实未通过的条目降级到"研读基础附录"
- action：research + verify

### [medium] 引用相关性 — [16] 边缘态主题与本项目 Berry/度规反演主轴相关性偏弱
- 位置：references.md 第 33 行 [16]；正文仅 content.md 第 4 行 `[5, 7] 与电子结构边界 [10, 11, 16]` 合并引用一次
- 问题：[16] = Lange & Madsen 边缘态 + 量子光 HHG 拓扑绝缘体，核心论题"边缘态对 HHG 贡献"与本项目 Ω/g 反演主轴有交集但非核心论证；正文仅合并引用一次
- 建议：在条目末补充"边缘态方法学借鉴"限定语，或移至研读基础附录
- action：rewrite

### [low] 格式细节 — [27] Fazekas-Tosatti 无 DOI/arXiv 标识符无法溯源
- 位置：references.md 第 55 行 [27]
- 问题：pre-check 已标记无 DOI/arXiv 条目 1 条；条目末尾仅说"无 DOI, 通过多份综述交叉引用确认"——1979 年旧文献无 DOI 合理但缺 ISBN/期刊 URL 备用溯源
- 建议：补 Philos. Mag. B 期刊 ISSN 0031-8086 或 Taylor & Francis DOI 历史记录链接；或在该条末注明"1979 年前文献无 DOI 属合理豁免"
- action：rewrite

### [low] 格式细节 — [13] arXiv:2508.00296 v2 2026-08-13 修订时序异常
- 位置：references.md 第 27 行 [13]
- 问题：v1 提交 2025-08、v2 修订 2026-08，跨越 12 个月——arXiv 论文通常一年内完成 v2，该条目修订时序超出常态，可能 v2 为新内容实质增订
- 建议：核实 v2 相对 v1 的实质修订内容（是否更换作者链/标题）；若属实质增订则条目末补一句"v2 实质增订"
- action：verify + rewrite

---

## 对抗结论

- 本轮发现 11 个问题（critical: 5, medium: 4, low: 2）
- **5 个 critical 中 4 个集中于"编号—作者—内容三重错位"**：Baykusheva→[26]、Du→[27]、Bauer→[12]、Uchida/Murakami→[12]。这是 NSFC 评审眼里最刺眼的"用而错位"信号，必须修复
- **最严重的是 4 处正文错位引用**：rationale.md 第 21/29/41 行连续出现 Baykusheva、Du 两条错位，把 2026 年新作错配到 1979/1995 经典文献；Bauer、Uchida 两个正文出现的人名在 references.md 完全没有对应作者链——属 P0 红线 no_exaggeration
- 相比 R1 上一版本（41 条）：新增 8 条但未做作者链重核，4 处错位源自本轮新增条目与正文叙述的同步失误
- **是否达到输出标准**：**否**——存在 5 个 critical 必须修复后方可达到 general 项目参考文献合格线
- 修复优先级（按对抗思维）：
  1. **最高优先级**（critical ×4）：核实 Baykusheva、Du、Bauer、Uchida/Murakami 四处错位引用的真实文献，删除伪造引用或补入正确条目
  2. **高优先级**（critical ×1）：核实 [42] DOI 真实格式
  3. **中优先级**（critical ×1）：压缩 49 → ≤40 条总数
  4. **低优先级**（medium/low）：时效性解释、预印本核实、引用相关性补限定语
- 修复完成后，预计严谨性可由 0.65 → 0.88，完整性可由 0.72 → 0.85，综合评分可由 0.68 → 0.86

## 评分
创新性：N/A
可行性：N/A
严谨性：0.65
完整性：0.72
综合评分：0.68
