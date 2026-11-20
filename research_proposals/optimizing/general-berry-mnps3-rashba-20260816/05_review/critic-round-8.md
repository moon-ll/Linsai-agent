# 对抗评审报告（第 8 轮·参考文献专项）

项目类型：general｜对象：references.md（35 条）｜日期：2026-09-16

核查方法：35 条全经 CrossRef API + arXiv abs 反查；编号一致性采信预检；正文未读全文，凭预检与引用位点确认缺失。

## 核查结论总览

- 真实性：34/35 实证为真，**1 条 [35] 严重失实**：作者署名"Sliding ferroelectric experimental group"为虚构词组，arXiv:2508.16422 真实作者为 Horstmann/Emeis/Caviezel（ETH Zurich）。
- 编号一致性：scheme.md 引用 [36]–[41] 共 6 个幽灵编号未列入文献列表；[1][2][34] 仍未被任何章节引用。
- R7 整改：8 项中仅 [22] 标签与 [33] 标题 2 项完成；[11][23] 作者链、[14] 正式版、[1][2] 未引用、[7][12] 格式均未处置；R7 漏检 [35] 虚构与 6 项幽灵编号。

## 问题清单

- [critical]｜[35] L71｜作者署名虚构：arXiv:2508.16422 真实首作者 Horstmann J G｜改"Horstmann J G, Emeis C, Caviezel A, et al."（action: rewrite）
- [critical]｜scheme.md L1886/1908/3519/3561/1174/4024｜幽灵编号 [36]–[41] 共 6 处：Hamer/Coello-Fiallos/Peschel/Tancogné-Dejean（×2）/Winkler 已内联引用但文献列表未列｜按正文作者+期刊补录 6 条（action: add）
- [high]｜[11] L23｜R7 点名作者链 pos3 错位仍未改｜按官方链改"Regmi R B, Bhandari H, Thapa B, Hao Y, et al."（action: rewrite）
- [high]｜[23] L47｜R7 点名"Suárez Morell E"姓拆分错位仍未改｜改 Morell E S 或保留 Suárez Morell E（action: rewrite）
- [high]｜[33] L67｜R7 点名标题"coupled to magnetic ordering"应改为"and magnetic correlations"仍未改｜按 DOI 官方标题逐字更正（action: rewrite）
- [high]｜[14] L29｜R7 点名可升级正式版仍未改（仍标 preprint）｜统一为"Phys Rev B, 2026, 114: L111201. DOI: 10.1103/5rrq-5g1k"（action: rewrite）
- [medium]｜[1][2][34]｜R7 点名未引用本轮仍 0 次引用｜补引或删除并重编号（action: add/remove）
- [medium]｜[7] L15｜R7 点名"Rybak M"人名格式不统一仍未改｜统一全篇格式（action: rewrite）
- [medium]｜[12] L25｜R7 点名 DOI 码制混杂仍未统一｜全文统一为期刊全称式或短码（action: rewrite）

## 锚点对比

- 引用：[35] Sliding ferroelectric experimental group. Coherent phonon control beyond amplitude saturation in a sliding ferroelectric. arXiv:2508.16422, 2025 (preprint)
- 对比（arXiv 官方）：Horstmann J G, Emeis C, Caviezel A, Meier Q N, Lottermoser Th, Caruso F, Fiebig M. arXiv:2508.16422 (2025)
- 差距：作者署名以"实验组名"伪词组替换真名，与 R5 Mu 元素符号同型虚构；标题/期刊/年份/编号全真实但作者链全军覆没，按 P0 红线判 critical。

锚点对比结论：未达标

## 维度评分

| 维度 | 权重 | 得分 | 依据 |
|---|---|---|---|
| 严谨性 | 0.5 | 0.40 | [35] 虚构署名（critical）+ [11][23][33][14] R7 未处置（high×4）+ 格式（medium×3）；critical 虚构扣至 0.3-0.4 区间 |
| 完整性 | 0.5 | 0.62 | 6 项幽灵编号（critical 一致性）+ [1][2][34] 未引用；总数 35 在标杆区间、近 3 年 ~66% 达标 |

## 对抗结论

- 本轮发现 9 个问题（critical:2, high:4, medium:3）
- 相比 R7：改善 1 项（[33] 标题确认）+ 退步 1 项（[35] 虚构 R7 漏检）+ 新增 critical 一致性 6 项幽灵编号；R7 点名 8 项中 6 项仍未处置
- 是否达标：否（[35] 虚构属 P0 红线违规、6 项幽灵编号属 critical 一致性违规，须当轮处置）
- 返工优先级：P1（critical）→ [35] 改回 Horstmann J G + 补录 [36]-[41]；P2（high）→ [11][23][33][14]；P3（medium）→ [1][2][34] 未引用、[7][12] 格式

## 评分
创新性：N/A
可行性：N/A
严谨性：0.40
完整性：0.62
综合评分：0.51