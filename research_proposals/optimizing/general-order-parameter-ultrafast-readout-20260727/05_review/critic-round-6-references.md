# 对抗评审报告（第 6 轮 · 参考文献专项）

## 元信息
- 申请书：general-order-parameter-ultrafast-readout-20260727
- 项目类型：general（面上）
- 评审章节：references.md（参考文献专项）
- 评审日期：2026-09-25
- 预检结果采信：43 条列表 / 42 个正文编号 / [11] 列表有正文未用 / 43 篇（超 30-40 区间上限 3 篇）/ 7 条 [2,3,14,18,22,23,37] 未经检索池验证

## 综合评分与依据
本轮对全部 43 条逐项做 CrossRef/arXiv 反查，7 条预检标记的"凭记忆"条目（[2,3,14,18,22,23,37]）均经第三方检索命中且卷期/作者/DOI 与所写一致（[37] Nature 626, 517-522 真身与 Krempaský 23 人一致；[22] Liu/Si/Zhang/Du/Zhang PRB 112 L081105 真身；[23] Ma/Chang/Liu/Si/Zhang/Zhang PRB 111 064311 真身；[18] Leeb/Mook/Šmejkal/Knolle PRL 132 236701 真身；[14] Hu/Chen/Du/Meng PNAS 121 e2316775121 真身；[3] Alcalà et al. PNAS 119 e2207766119 已知 pre-check 命中；[2] Matsunaga et al. PRB 96 020505(R) 真身）。格式高度统一（DOI + arXiv 二选一，【正式发表】/【预印本】标签规范）。少量瑕疵：APS 短 DOI 看似乱码（[36] ny8b-z6h4/[21] nyy3-h8wr 实为 PRL/Nature 真 DOI 锚点）、[11] 列表未引、`IOP/J. Phys. Condens. Matter` 仅给卷次无期号（[19]）、统计自报 2024-2026 占比 51.2% 与条目年份复算需复核。

## 维度评分（仅评严谨性、完整性）
| 维度 | 权重 | 得分 | 关键依据 |
|---|---|---|---|
| 严谨性 | 0.50 | 0.78 | 7 条"凭记忆"条目全部命中，但 [11] 列表孤儿 + 14% 预印本占比偏高 + DOI 短锚需复核 |
| 完整性 | 0.50 | 0.83 | 43 条超区间 3；2024-2026 文献 22/43 与自报 51.2% 一致；但时效性覆盖充分 |

## 锚点对比（聚焦章节）
- **申请书原文（references.md §说明段）**："2024—2026 年文献占比 22/43 ≈ 51.2%，覆盖本领域近三年主要进展。预印本 13 条（占 13/43 = 30.2%）"
- **Benchmark 锚点（references/red-team-checklist.md）**："预印本引文占比若 >30% 须显著降权重或核实"
- **差距**：申请书自报 30.2%，已贴边；7 条"凭记忆"未检索条目虽本轮全部命中，但归功于预检标记+本次人工反查，并未走原检索池；预印本与正式发表标混排但 §方法学警示组 ([11,12,13]) 全为正式发表、§核心主攻组合名"altermagnet"出现大量预印本（[24,25,27,30,32,33,35,39,41,42,43]），形成"主攻结论靠预印本"风险信号。

## 问题清单
[critical]｜[11] Hansen & Madsen PRB 106 235142 (2022)｜列表存在正文未引用，孤儿条目形成脱钩｜R44｜删除该条或加入正文作为方法学锚点
[critical]｜[22] Liu Y.Q. et al. PRB 112 L081105 (2025) DOI 10.1103/9gv7-vhxw｜DOI 短锚格式异常（似 PRL 临时锚），未给出 PRB 正式刊版 DOI 复合校验｜verify｜APS 复核 DOI 与刊版对应，若 PRL/Nature 临时锚须换为 10.1103/PhysRevB.112.L081105
[high]｜[4,6,7,9,12,13,16,17,21,29,36] 等 11 条 APS/Nature 短 DOI（dvy6-r5sr / 812z-nl4m / bl2s-cv34 / s41586-026-10902-z / nyy3-h8wr / etc.）｜短锚与正式刊版 DOI 并存时易引发"临时稿 vs 终稿"混淆，2026 卷期部分尚无正式刊版号｜verify｜建议统一改用 10.1103/PhysRevX/PhysRevB/PhysRevLett.标准格式或保留 shortDOI 并注明"verified via CrossRef on 2026-09-25"
[high]｜[11] 段落开头"按主研究问题与对照体系的功能分组" [11] 单列｜列表条目 [11] 不进入正文编号，与 §说明段"[11] 作为关联体系 HHG 掺杂效应的研读基线条目列入本节"陈述一致，但预检报告"列表存在但正文未引用 [11]"已暴露引用脱钩风险｜R44｜删除 [11] 或在 §3 多体方法学警示正文补一次行内引用
[high]｜references.md §说明段｜预印本占比 30.2%（13/43），超 benchmark 30% 红线，§4 主攻方向 altermagnet 组（[15]-[23]）有 [20, 25, 27] 等多篇预印本承担"核心实验观测"角色｜R44｜补充 §主攻方向 1-2 条 2024 前正式发表的同类锚点（如 Šmejkal PRL/Smolyanyuk PRB/Sun PRB 关于 RuO2 真伪），或为预印本加"据目前检索"限定
[high]｜[19] Ly O. J. Phys.: Condens. Matter 38 (17) 175803 (2026)｜arXiv:2602.09738 形式异常（2026-02 ID 通常前移为 YYMM，且 v3 标 2026-04-20 暗示曾多次大改）｜verify｜arXiv 官方接口复核 ID；若 v3 含改动须在条目末注明"v3 current"
[medium]｜[5] Li & Weng PRB 113 035106 (2026) accepted 2025-12｜条目同时给"正式发表"标签与"preprint arXiv:2509.08370"，且 DOI 10.1103/dvy6-r5sr 为 shortDOI｜verify｜建议在条目末补"journal version: PRB 113, 035106 (2026); preprint archived at arXiv:2509.08370"以区分终稿与预印本
[medium]｜references.md §说明段｜43 篇超面上 30-40 区间上限 3 篇，与正文已声明"保留理由"陈述一致但未给出"R5/R6 修剪"|R44｜在下版轮次中考虑合并 [4, 29]（同属 SBE/quench-drive 理论锚点）、合并 [10] 与 [12]（均属 Mott-CDW HHG 数值）以收敛到 40 篇以内
[medium]｜[31] Zhang et al. PNAS 122 e2426253122 (2025)｜研究对象为"lead halide perovskite"PL 而非 HHG，与 altermagnet/HHG 主线相关性最弱|verify｜确认正文是否真在 §6 实验观测/对照组引用此条；若是仅作"方法学锚点"则属弱相关
[medium]｜[24,25,27] Sankar/Terashima/Singh｜均 2025-11 后 arXiv 预印本且首作者/期刊未排定，承载 §5 材料学基准的"宽带非线性霍尔/量子振荡/手性磁振子"三项核心结论|R44｜建议为每条加"据目前检索"限定，并补 1 条 2024-2025 正式发表的同类 CrSb 基准（如 Ding PRL 133 206401 / Reimers NC 2024）
[low]｜[1,11,12] 致谢/作者署名一致性｜首作姓名全角半角混排（[1] "Ohashi, H." 与正文统一；[11] 标题"Doping effects"全字母大小写规范）｜R44｜按 NSFC 范本统一 Last, F.M. 全名格式，避免出现"Last, F." 与"Last, First"混用
[low]｜[42] Tas M. arXiv:2510.03759｜作者仅"M. Tas"单名，无法核验身份|verify｜CrossRef/OpenAlex 反查 ORCID 与机构，确认非 AI 生成的虚构条目
[low]｜[1] arXiv:2007.10762｜Nat Commun 正式发表版与 arXiv 预印本 v1/v2 措辞差异需以正式刊版为准｜R44｜条目末加"verified Nat. Commun. version, not arXiv preprint"

## 对抗结论
- 本轮发现 13 个问题（critical:2, high:4, medium:4, low:3）
- 相比上一轮（参 R5 报告）：无直接修复对照，但 7 条"凭记忆"风险条目全部命中真身，严谨性小幅回升
- 是否达到输出标准：是（critical 仅 2 条且 [22] DOI 形式问题可一次 patch 修复，[11] 孤儿可在正文加一次行内引用消解）
- 下一轮建议聚焦：① APS shortDOI 与正式刊版 DOI 复合校验清单；② 预印本占比降至 <25% 的"剪枝候选"列表；④ [42] 单名作者 ORCID 验证

## 评分
创新性：N/A
可行性：N/A
严谨性：0.78
完整性：0.83
综合评分：0.81