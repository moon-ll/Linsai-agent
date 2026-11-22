# 参考文献专项检验报告（第 8 轮 · references.md）

- 对象：04_proposal/sections/references.md（47 条，2026-09-09 全文通读）；项目类型 general；标准 memory/nsfc-standards.json
- 方法：全表反查——Crossref 逐条核 21 个期刊 DOI + arXiv API 批量核 18 条预印本 + 定点补查（[26] 题名检索定位真身、[27] 候选 DOI 验真、[9][12][13] 摘要与作者链调取）。编号一致性由预检完成，采信不复核
- 文件处理：原 critic-round-8.md（今晨整体一致性轮）已归档为 .archive-20260909-critic-round-8-overall.md
- R7 critical 验收：4 条仅落地 1 条——[13] 已修复（题名/六作者/v2=2026-08-13 全对）；[9][12][26] 未修复仍为 critical；[31]（high）未修复

## 问题清单

[critical]｜[26]｜DOI 404；真身为 Aversa-Sipe PRB 52,14636(1995)，题名卷页年四件全错｜照 Crossref 官方记录整体重写，DOI 改 10.1103/PhysRevB.52.14636
[critical]｜[9]｜真实题名"Quantum Metric in Step Response"（Verma & Queiroz 仅2人），所载 HHG 题名仍虚构｜按 arXiv 官方记录改题名与作者，正文引用用途同步复核
[critical]｜[12]｜题名已改但一作仍"Bauer, D."；真实一作 Cárdenas（共3作者），组注张冠李戴｜照真实作者链 Cárdenas, Silva, Jiménez-Galán 改写并删组注
[high]｜[31]｜R7 点名未修：真实题名"Berry phase effects on electronic properties"｜按 Crossref 题名更正
[high]｜全表｜47 篇超出 20–40 区间且较 R7（46）不降反增｜执行裁撤：[28]/[41]、[8]/[44] 各留一，[24] 删或在正文并注
[high]｜缺失｜量子度规—非线性霍尔理论链缺奠基文（R7 已指出仍未补）｜补 Sodemann & Fu, PRL 115, 216806 (2015)，DOI 已验真
[medium]｜[9][11] 等18条｜"arXiv DOI: https://doi.org/…"URL 式著录不统一｜统一作"DOI: 10.48550/arXiv.XXXX.XXXXX"
[medium]｜全表｜工作日志污染：39/47 条内嵌中文工作注，另 [34]【正式发表】/ [19]"in press"状态注｜工作注全部迁移至 05_review，正式表剥净
[medium]｜全表｜作者著录三式并存（全列/前3+et al./单名+et al.）｜统一"前3作者 + et al."
[medium]｜[25]｜arXiv 号与 Quantum 期刊 DOI 并列，违反二选一｜保留期刊 DOI，删 arXiv 号
[medium]｜[27]｜无标识符条目，真 DOI 已验真却两轮未补｜补 DOI 10.1080/13642817908245359
[medium]｜[13]｜"红移5–15%"注在原文摘要不可见，精确区间来源未验｜对照原文结果部分核定，或改定性表述
[low]｜[45]｜"(2024, v3 2025-08)"版本号混注非标准｜删版本注，仅保留 2024
[low]｜[43]｜"et al."截断于第4作者，与全列式不统一｜随全表著录统一处理
[low]｜[19]｜"已收录 Adv. Phys. in press"属状态追踪注｜随工作注迁移一并剥净

## 锚点对比（题名逐字比对）

- 申请书 [26]：Aversa & Sipe, *Phys. Rev. B* **49**, 8869–8886 (1994), "Model of high-order harmonic generation in semiconductors"
- Crossref 10.1103/PhysRevB.52.14636 官方记录：Aversa & Sipe, *Phys. Rev. B* **52**, 14636–14645 (1995), "Nonlinear optical susceptibilities of semiconductors: Results with a length-gauge analysis"
- 差距：题名、卷、页、年四件全错且 DOI 404，属凭记忆拼装的"貌似合理"条目；同型拼装见 [9]（真实论文为 Verma & Queiroz 的阶跃响应量子度规测量，申请书题名系虚构）。修复不得止于改一处——须以官方记录整体重写条目，并 grep 正文凡据错误条目立论处同步复核。
- 锚点对比结论：差距明显

## 对抗结论

- 本轮 15 个问题（critical 3 / high 3 / medium 6 / low 3）
- 相比 R7：改善 1（[13] 题名作者已修复）；未解决 12（含 3 条 critical 跨轮未落地）；新增 2（[43][19] 著录细节）
- 真实性 44/47 通过；相关性 47/47（[24][29][27] 经正文核实为实质支撑引用，撤 R7 弱相关疑议）；时效性 2023+ 文献 26/47=55% 达标；无幽灵编号、无未引用条目
- 是否达到输出标准：否——3 条 critical 虚构/错位清零前参考文献表禁止进入终稿；R7 点名 critical 修复跨轮未落地的模式表明 writer 修复须当轮全表反查验收，不得凭其自报结案
- 下一轮验收要点：[26][9][12] 重写条目逐字段比对官方记录；裁撤后总数落入 20–40；中文工作注迁移后全表 grep 残留清零；[27] DOI 与 Sodemann & Fu 补录核查

## 评分
创新性：N/A
可行性：N/A
严谨性：0.40
完整性：0.75
综合评分：0.58
