# 参考文献检验报告（第 1 轮 · references 轮线）

项目类型：general（面上）｜对象：04_proposal/sections/references.md（32 条）
审查日期：2026-09-15｜预检：程序编号一致性已采信（29 个正文编号 vs 32 条列表，缺口=[20][21][23]）
上轮文件处理：原 critic-round-1.md 属"整体一致性轮线"，已归档为 .archive-critic-round-1-overall-consistency-line-superseded-by-references-line-20260915.md

## 核验方法与总量
- 全量反查（非抽查）：27 条 DOI 经 CrossRef API 解析，5 条 arXiv 经 abs 页/OpenAlex/Semantic Scholar 反查
- 五件套比对：标题/首作者/期刊/卷期页/年份 + 作者链逐位比对（判例：ID/题名双真仍可藏虚构作者链）
- 结果：32/32 条真实存在，无虚构条目，标题/期刊/卷/页/年份全部吻合；3 条 APS 短 DOI（[18][20][24]）合法解析，按判例不判问题

## 问题清单
1. [medium]｜[6] 作者链｜第2/3位 Makabe K/Wang L 不在官方作者链｜改为 Ren X, Li J, Yin Y, et al.
2. [medium]｜[23] 作者链｜第2/3位 Nagele S/Feist J 顺序互换｜改为 Pazourek R, Feist J, Nagele S, Burgdörfer J
3. [medium]｜[24] 作者链｜Helml/Otto 实为官方第4/5位，跳过 Viefhaus/Hartmann｜改为 Meier D, Viefhaus J, Hartmann G, et al.
4. [medium]｜[31] 版本滞后｜已正式发表仍引 arXiv 预印本｜更新为 Ultrafast Science 2025, DOI: 10.34133/ultrafastscience.0128
5. [medium]｜[32] 版本滞后｜正式版为 4 作者仍引单作者预印本｜改为 Han M, Liang H, Liu Y, Lin C D. Ultrafast Science 2026（DOI: 10.34133/ultrafastscience.0145）
6. [medium]｜[20][21][23] 幽灵条目｜列表存在但三章正文均未引用｜逐条补入正文论证或删除并全局重排编号
7. [low]｜[21][25] vs [30-32] 格式｜arXiv 类目标注不统一（前者无 [physics.*]）｜统一补齐或全部去除类目标注
8. [low]｜[22] 期刊名｜用全称，其余条目均用缩写｜统一为 J. Phys. B: At. Mol. Opt. Phys.
9. [low]｜全列表 检索池回录｜预检 25 条凭记忆条目经核验为真但未回录｜将本轮核查元数据回录 02_literature/ 供后续轮复用

## 分项结论
- 引文格式：DOI/arXiv 二选一 32/32 满足；卷/页（或文章号）齐全；年份齐全。缺陷仅作者链 3 处、arXiv 标注与期刊名缩写不统一（见清单 1-3、7-8）。
- 引用相关性：32 条主题集中于阿秒条纹测量、脉冲表征/重建、光电发射时延、水窗光源，与申请书科学问题直接相关，未发现无关引用。[29] 奠基文、[5] FROG-CRAB、[28] 综述构成合理脉络；[30][31][32] 覆盖"最短脉冲之争"正反双方，支撑动机成立。
- 缺失引用：无"正文引用但列表缺失"；反向缺口即幽灵条目 [20][21][23]（清单 6）。
- 数量与时效：32 条，落在 20-40 达标区间；2023-2026 年文献 17 条（53%）≥50% 时效线，达标。近三年含 2025-2026 前沿 9 条（[10][18][19][20][21][22][24][30][31][32] 中 10 条），跟踪性良好。

## 锚点对比（[31]，官方记录逐字）
申请书：Ardana-Lamas F, Cousin S L, Lignieres J, Biegert J. Brilliant source of 19.2 attosecond soft X-ray pulses below the atomic unit of time. arXiv:2510.04086 [physics.optics], 2025 (preprint).
arXiv 2510.04086：标题逐字一致；作者链 Ardana‐Lamas; S. L. Cousin; J. Lignières; J. Biegert 一致（仅 Lignières 重音符差异，不立案）。
差距：该文已见刊 Ultrafast Science 2025（DOI 10.34133/ultrafastscience.0128），申请书停留在预印本形态，正式版本信息缺失。
锚点对比结论：达标
（题名/作者/ID 三要素逐字吻合；差距仅在版本形态，已列清单 4。）

## 评分依据
- 严谨性 0.78：真实性满分基底（32/32 真，无虚构、无卷期页年错误，APS 短 DOI 判例合规）；扣 3 处作者链错位（medium）+2 处版本滞后（medium 属格式/严谨交界）。无 critical，不触发 0.4-0.5 降档。
- 完整性 0.88：数量、时效、双向缺口中"缺失引用"均达标；仅幽灵条目 3 条（medium）扣分。
- 综合评分 = (0.78+0.88)/2 = 0.83（精确两位小数，程序复核通过）。

## 对抗结论
本轮发现 9 个问题（critical:0, high:0, medium:6, low:3）。
相比预检警示（25 条未验证=虚构风险集中区）：全量反查后零虚构，风险解除，是本轮最大正面结论；但作者链逐位比对仍抓出 3 处 ID/题名双真掩盖的作者错位，验证"仅核 ID+题名"验收口径不可靠。
是否达到输出标准：是（问题均可定位、可执行；无阻断性缺陷）。
返工优先级：清单 1-3（作者链）与清单 6（幽灵条目三选一处置）当轮修复；清单 4-5（版本更新）次轮前完成；清单 7-9 随下轮统一格式时一并处理。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.78
完整性：0.88
综合评分：0.83
