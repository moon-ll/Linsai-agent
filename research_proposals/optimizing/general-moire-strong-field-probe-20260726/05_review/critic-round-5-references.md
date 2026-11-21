# 参考文献检验报告（第 5 轮）

## 元信息
- 项目类型：general（面上）
- 检验对象：04_proposal/sections/references.md（32 条，L3–L69）
- 检验日期：2026-09-23
- 核查方法：32 条全量 CrossRef API + arXiv export API 逐条反查（题名/首作/期刊/卷期页/年份五件套），非抽查；编号一致性直接采信程序预检
- 上轮遗留：本轮为 references 第 5 轮专项（R4 报告见 critic-round-4-references.md）

## 核查结论总览
- 32 条中 27 条五件套与公开记录吻合（含 [15] Erratum DOI 10.1038/s41586-021-04368-4 反查为真：Nature 602, E19 (2022)）
- 预检点名 14 条"凭记忆"条目 [2,3,9,10,11,13,16,17,19,20,23,24,26,30] 已全部反查：13 条为真，仅 [30] 错挂——再次验证"凭记忆区须全量反查、勿预扣"
- [24][25][26] 初检 TITLE/AUT1 标记经下标/复合姓归一化复核为程序伪影，撤案
- [7] Ikeda T. N. 唯一作者、[12] Ryohei Ikeda 六作者链、[27] arXiv:2607.22532 五作者链均与 arXiv/CrossRef 一致

## 问题清单

### critical
- [critical]｜[30] L63｜期刊卷期年错挂：真身 PRL 120, 177401 (2018)，所写 PRResearch 6, 013033 (2024) 实为 Scarlatella 无关论文｜改为 Bauer & Hansen, Phys. Rev. Lett. 120, 177401 (2018), DOI: 10.1103/PhysRevLett.120.177401（arXiv:1711.05783 journal_ref 佐证）；action: rewrite

### high
- [high]｜[31] L65｜作者链虚构：真身作者为 Chinzei & Ikeda（仅 2 人），条目杜撰 Du M./Han H./Liu X.，且无 DOI｜改为 Chinzei K., Ikeda T. N., Phys. Rev. Res. 2, 013033 (2020), DOI: 10.1103/PhysRevResearch.2.013033；action: rewrite
- [high]｜[32] L67｜期刊卷期虚构 + 首作错排：PRB 106, 115317 (2022) 经 DOI 反查 404 不存在；真身为 J. Phys. Mater. 6, 045001 (2023)，首作 Varela Manjarres（Nikolić 为二作）｜改为 Varela Manjarres J., Nikolić B. K., J. Phys.: Mater. 6, 045001 (2023), DOI: 10.1088/2515-7639/aceaad（arXiv:2112.14685 DOI 字段佐证）；action: rewrite

### medium
- [medium]｜[18] L39｜arXiv:2302.12564 题名滞后：abs 页题为 "Valleytronics in bulk MoS2 by optical control of parity and time symmetries"，与正式版题名不一致且无 journal_ref 佐证关联｜删除该 arXiv ID 或核版本差异后加注；action: verify
- [medium]｜[27] L57｜"已接受待补卷期"信息滞后：CrossRef 显示已刊出，Nano Lett. 26(33), 10547–10553（2026-07-30 刊出）｜补全卷期页码并删"刊出后补"语；action: add
- [medium]｜L3 统计句｜"2024–2026 文献 18 条，占 56.2%"依赖 [30] 错年 2024；[30] 修正为 2018 后实际为 17 条 53.1%｜修 [30] 时同步改写 L3 统计句，防旧值滞留；action: recalculate
- [medium]｜[29]–[32]｜四条未被正文 [N] 引用，虽 L3/L69 有声明，但正式申请书参考文献表应与正文引用一一对应｜正文合适论断处补挂 [29]–[32] 角标，或移出参考文献表另列"研读基础"；action: add
- [medium]｜[11] L25 / L69｜工作日志语言泄漏：[11] 自注"（已与 arXiv:1704.08471 真身对齐）"、L69"依本项目 v6.9.64 范围排除条款…本节不预撰"均为内部流程语，不得进入正式申请书｜[11] 径用正式版题名 spectroscopy 并删自注；L69 删除或改为申请人待补说明；action: remove

### low
- [low]｜[19] L41｜年份口径：条目 (2024)，CrossRef 在线出版 2023-12-18（卷 20 属 2024 年卷）｜可辩护，统一采用卷年口径即可；action: verify
- [low]｜[23] L49｜年份口径：条目 (2011)，CrossRef 在线 2010-12-22（Nat. Phys. 7 卷年 2011）｜同上，保持卷年口径；action: verify

## 锚点对比（[30]）
- 申请书原文（L63）："Bauer D., Hansen K. K. 等. High-harmonic generation in solids with and without topological edge states. Physical Review Research 6, 013033 (2024)；亦见 arXiv:1711.05783."
- CrossRef 真身："Bauer D., Hansen K. K. High-Harmonic Generation in Solids with and without Topological Edge States. Physical Review Letters 120, 177401 (2018), DOI: 10.1103/PhysRevLett.120.177401"；而 DOI 10.1103/PhysRevResearch.6.013033 反查为 Scarlatella et al. "Stability of dissipatively-prepared Mott insulators of photons"
- 差距：作者/题名/arXiv 三真、期刊卷期年三假，错挂编号实际指向无关论文，且 2018→2024 虚增 6 年时效性；arXiv 页 journal_ref 即可定位真身，属可零成本自验而未验的错挂

## 对抗结论
- 本轮发现 10 个问题（critical:1, high:2, medium:5, low:2）
- 真实率 29/32（90.6%）：无整条凭空捏造，但 [30][31][32] 三条集中在"研读基础"区段（L61–L67），即 writer 凭学科知识补写的方法学锚文献——预检风险预警被证实
- 是否达到输出标准：否。critical/high 三条未修复前，参考文献表不可定稿；修复均为单行替换，成本极低
- 返工优先级：[30] → [31] → [32] → L3 统计句联动 → [27] 补卷期 → 工作日志语言清理 → [18] arXiv 题名核验
- 下一轮建议：writer 修复后，对本轮 3 条错挂行 grep 验收（防只改点名行残留）；命中真实文献回录 02_literature 检索池

## 评分
创新性：N/A
可行性：N/A
严谨性：0.66
完整性：0.82
综合评分：0.74
