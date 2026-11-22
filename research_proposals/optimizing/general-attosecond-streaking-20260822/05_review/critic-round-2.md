# 参考文献检验报告（第 2 轮 · references 轮线）

项目类型：general（面上）｜对象：sections/references.md（35 条）｜审查日期：2026-09-15
预检采信：正文 33 编号 vs 列表 35 条连续无缺口；未引用 [23][35]。
上轮文件处理：live critic-round-2.md 属整体轮线，已归档为 .archive-critic-round-2-overall-consistency-line-superseded-by-references-line-20260915.md；同线上轮为 R1-references（2026-09-15）。

## 核验方法与总量
- 全量反查（非抽查）：29 条 DOI 经 CrossRef API 逐条解析；6 条 arXiv 经 abs 页 + OpenAlex 题名/作者链双路核验（S2 备选未用，避开 429）。
- 五件套 + 作者链逐位比对。结果：35/35 条真实存在，零虚构；题名/期刊/卷/页/年全部吻合；APS 短码 DOI（[18][20][24]）合法解析。
- R1 修复验收：清单 1-5（作者链 3 + 版本滞后 2）0 执行，全部残留；清单 6 部分修复（[20][21] 已挂正文，[23] 仍幽灵）；清单 8 已修复（全文统一刊名全称）。

## 问题清单
1. [high]｜全文件 R1残留｜清单1-5点名修复0执行，本轮实测原样残留｜按清单2-6逐字改写后全章grep复核
2. [medium]｜[6] L21 作者链｜2/3位Makabe K/Wang L不在官方链｜改 Ren X, Li J, Yin Y, et al.
3. [medium]｜[23] L55 作者链｜Nagele S与Feist J顺序互换｜改 Pazourek R, Feist J, Nagele S, Burgdörfer J
4. [medium]｜[24] L57 作者链｜Helml/Otto跳过官方2/3位Viefhaus/Hartmann｜改 Meier D, Viefhaus J, Hartmann G, et al.
5. [medium]｜[31] L71 版本滞后｜已见刊Ultrafast Science仍引预印本｜改 DOI: 10.34133/ultrafastscience.0128
6. [medium]｜[32] L73 版本滞后｜正式版4作者仍引单作者预印本｜改 Han M, Liang H, Liu Y, Lin C D. DOI: 10.34133/ultrafastscience.0145
7. [medium]｜[35] L79 版本滞后｜新发现：已见刊AAAI 2026仍引预印本｜改 Proc. AAAI v40i16, DOI: 10.1609/aaai.v40i16.38412
8. [medium]｜[23][35] 幽灵条目｜预检正文零引用；[23]系R1幽灵残留｜补入正文论证或删除并全局重排
9. [medium]｜L3 头部元叙述｜自述31挂点/覆盖88.6%，预检实测33编号/91.4%｜按预检实测改写，勿自报未验数
10. [low]｜L5 时效自述｜自述17条48.6%，实测2024-26仅16条45.7%｜按2023口径(51.4%)重算并注明统计窗口
11. [low]｜[21][25] vs [30-32][35]｜arXiv类目标注不统一（R1清单7残留）｜统一补齐或全部去除类目
12. [low]｜[25] L59｜2018预印本，OpenAlex未见正式版记录｜writer核验是否有刊出版，有则更新
13. [low]｜检索池回录｜R1清单9残留：核查元数据未回录02_literature/｜回录本轮35条元数据供后续复用

## 分项结论
- 引文格式：DOI/arXiv 二选一 35/35；卷页年齐全；刊名已全称统一。缺陷：作者链 3 处、版本滞后 3 处、arXiv 标注不统一。
- 引用相关性：主题集中于阿秒条纹测量、脉冲表征/重建、光电发射时延、水窗光源、ML 相位检索，与科学问题直接相关，无无关引用；[30][31][32] 覆盖"最短脉冲之争"正反方，支撑成立。
- 缺失引用：无"正文引用但列表缺失"；反向缺口为幽灵 [23][35]（清单 8）。
- 数量与时效：35 条在 20-40 区间；2023-2026 占 18/35=51.4% 达标（2024-2026 口径 45.7%，自述 48.6% 失实）。

## 锚点对比（[31]，官方记录逐字）
申请书：Ardana-Lamas F, Cousin S L, Lignieres J, Biegert J. Brilliant source of 19.2 attosecond soft X-ray pulses below the atomic unit of time. arXiv:2510.04086 [physics.optics], 2025 (preprint).
OpenAlex：Brilliant Source of 19.2-Attosecond Soft X-ray Pulses below the Atomic Unit of Time. Ultrafast Science, 2025. DOI 10.34133/ultrafastscience.0128；作者链 Ardana-Lamas/Cousin/Lignieres/Biegert 四人一致。
锚点对比结论：题名/作者/ID 三要素逐字吻合；差距仅在版本形态——已见刊仍引预印本（清单 5）。

## 评分依据
- 严谨性 0.72：真实性满分基底（35/35 全真，无虚构，不触发 0.3-0.4 降档）；扣分：R1 点名 5 项修复 0 执行（high）+ 作者链 3 处 + 版本滞后 3 处（medium）+ 标注不统一（low）。
- 完整性 0.88：数量、时效（2023 口径）达标；扣分：幽灵 2 条、头部元叙述两处自报数与实测不符。
- 综合评分 = (0.72+0.88)/2 = 0.80（精确两位小数，程序可解析）。

## 对抗结论
本轮发现 13 个问题（critical:0, high:1, medium:8, low:4）。
相比 R1（9 个问题）：残留 8、修复 1（刊名全称化）+部分修复 1（[20][21] 挂点）、新增 5（[35] 版本滞后、[35] 幽灵、覆盖数失实、时效自述失实、[25] 核验）。
是否达到输出标准：是（问题均可定位、可执行；无阻断性缺陷）。
返工优先级：清单 1-8 当轮修复并回grep验收；清单 9-13 次轮统一处理。writer 再次只动头部不动条目，将按"点名零执行"升级处理。
预检"27 条凭知识引用=虚构风险集中区"警示解除（全量反查零虚构），但该批元数据仍须回录（清单 13）。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.72
完整性：0.88
综合评分：0.80
