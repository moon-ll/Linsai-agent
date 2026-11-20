# R3 联网核实报告 — general-bsv-driven-hhg-quantum-20260726 3 条可疑条目

> 核实时间：2026-10-11
> 核实方法：WebSearch + WebFetch + DOI handle 权威解析
> 核实范围：M2.1 移交的 DOI/arXiv 硬约束条目

## 总判定表

| 条目 | DOI 真实性 | arXiv 真实性 | 期刊卷期页 | 建议处理 |
|------|----------|------------|----------|---------|
| [11] Li et al., PRL 126, 137403 (2021) | ✓ 真实 | ✓ 真实 (2205.11161) | ✓ 一致 | **保留原文**；可加注释说明 arXiv 晚于期刊发表 |
| [12] Raab et al., RSI 95, 073002 (2024) | ✓ 真实 | ✓ 真实 (2405.11859) | ✓ 一致 | **保留原文**，无需修改 |
| [18] Prajapati et al., PRB 113, 045118 (2026) | ✓ APS accepted-manuscript handle | ✓ 真实 (2410.01424) | ✓ 一致 | **保留原文**；建议注释 DOI 阶段 |

## 条目 [11] 字段对账

| 字段 | 待核实条目 | 权威来源 | 对账结果 |
|------|-----------|---------|---------|
| arXiv ID | 2205.11161 | arxiv.org/abs/2205.11161 | ✓ 2022-05-23 提交 |
| 标题 | Quantum interference visibility spectroscopy in two-color photoemission from tungsten needle tips | arXiv abs 页 | ✓ 字面完全一致 |
| 第一作者 | Li A. | arXiv 作者列表 | ✓ "Ang Li" |
| 其他作者 | et al. | arXiv 作者列表 | ✓ Pan, Dienstbier, Hommelhoff |
| 期刊 | Physical Review Letters | arXiv Journal ref + DOI 解析 | ✓ "Phys. Rev. Lett." |
| 卷期页 | 126(13), 137403 (2021) | arXiv Journal ref | ✓ 一致 |
| DOI | 10.1103/PhysRevLett.126.137403 | doi.org handle API | ✓ 真实注册，2021-04-02 |

**建议**：保留原文；可选注释「arXiv 2022-05-23 上挂（已发表于 PRL 126, 137403 (2021)）」澄清挂靠时序。

## 条目 [12] 字段对账

| 字段 | 待核实条目 | 权威来源 | 对账结果 |
|------|-----------|---------|---------|
| arXiv ID | 2405.11859 | arxiv.org/abs/2405.11859 | ✓ 2024-05-20 提交 |
| 标题 | Highly versatile, two-color setup for high-order harmonic generation using spatial light modulators | arXiv abs 页 | ✓ 字面完全一致 |
| 第一作者 | Raab A.-K. | arXiv 作者列表 | ✓ "Ann-Kathrin Raab" |
| 其他作者 | et al. | arXiv 作者列表 | ✓ Schmoll, Simpson, Redon, Fang, Guo, Viotti, Arnold, L'Huillier, Mauritsson |
| 期刊 | Review of Scientific Instruments | AIP 出版页 | ✓ RSI |
| 卷期页 | 95(7), 073002 (2024) | AIP 出版页 | ✓ 95(7), 073002 (July 16, 2024) |
| DOI | 10.1063/5.0212578 | doi.org handle API | ✓ 真实注册，2024-07-16 |

**建议**：保留原文，无需修改。DOI 中 "5" 是 AIP 2023 年后新格式版本/前缀字段，非异常。

## 条目 [18] 字段对账

| 字段 | 待核实条目 | 权威来源 | 对账结果 |
|------|-----------|---------|---------|
| arXiv ID | 2410.01424 | arxiv.org/abs/2410.01424 | ✓ 2024-10-02 提交 |
| 标题 | Terahertz harmonic generation across the Mott insulator-metal transition | arXiv abs 页 | ✓ 字面完全一致 |
| 第一作者 | Prajapati G. L. | arXiv 作者列表 | ✓ "Gulloo Lal Prajapati" |
| 其他作者 | et al. | arXiv 作者列表 | ✓ Ray, Ilyakov, Ponomaryov, Arshad, de Oliveira, Dubey, Rana, Deinert, Werner, Kovalev |
| 期刊 | Physical Review B | arXiv Journal ref | ✓ "Phys. Rev. B" |
| 卷期页 | 113(4), 045118 (2026) | arXiv Journal ref | ✓ 一致 |
| DOI | 10.1103/ydjj-xxcl | doi.org handle API | ✓ 真实注册，APS 内部 accepted-manuscript handle，2025-12-16 创建 |

**建议**：保留原文。`10.1103/ydjj-xxcl` 是 APS 在论文被接收后分配的内部 DOI 占位（accepted-manuscript 阶段），已通过 doi.org 权威解析验证为 APS 注册 handle，harvest.aps.org 全文检索可命中。**非杜撰、非异常**，是 APS 标准 accepted-manuscript 阶段 DOI 形式。可注释「DOI 为 accepted-manuscript 阶段 APS 内部 handle；最终刊载于 PRB 113, 045118 (2026)」以澄清。

## 总结

3 条参考文献**全部真实存在**，未发现虚构或杜撰条目。M2.1 移交的 3 条 DOI/arXiv 硬约束项目**无修改必要**，建议全部保留原文。条目 [11] 可加 arXiv 时序注释；条目 [18] 可加 DOI 阶段说明；条目 [12] 无需任何修改。

## 后续 R3 联核实任务（剩余）

- attosecond **Pabst-Dahlström [3]** 残余上界精确量化
- attosecond **Kheifets [18]** 实测残余区间精确量化
- moire OP-R4-02/03/04/05 结构性意见（已移交第 7 遍，非 DOI 核实范围）