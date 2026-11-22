# 对抗评审报告·第3轮（参考文献专项）

> 角色：critic（红队）｜项目类型：key｜日期：2026-09-08｜对象：references.md（45 条）
> 文件时序：references.md（12:30）早于 rationale（18:15）/content（18:22）重写，正文引用未随重写同步——半迁移态复发
> 核验方式：CrossRef API 全量 22 条 DOI 反查 + arXiv API 全量 23 条 ID 反查 + doi.org 解析 + web 交叉验证；上轮 5 处错挂逐一 grep 验收
> 前置处置：原 critic-round-3.md（今 12:50 整体一致性轮）已归档为 .archive-20260908-critic-round-3-overall.md

## 核验总览
- 通过：30 条（17 条 DOI 条目题名/作者/卷期与 CrossRef 全符；13 条 arXiv 条目题名/一作与 arXiv API 全符）
- 实锤：虚构 5 条（[4][24][25][31][38]）；错构 2 条（[32][34]）；死链 1 条（[18]）；一作错置 1 条（[6]）
- 上轮移交 5 处正文-总表错挂（[6][14][15][16][17]）验收：0/5 修复
- 孤儿条目 8 条：[4][24][25][36][37][39][40][43]（[24] 系 [21] 复制变体；[4][25][38] 双重违规：孤儿+虚构）

## 锚点对比
申请书 [24]：C. Zhao, L. Jurkovičová, X. Zou, … A. Zaïr. Sub-cycle observation of interband polarization in solids driven by intense few-cycle fields. arXiv:2502.07390 (2025)
arXiv 2502.07390 真身：Jianhui Huang. Nonlinear Open-Loop Mean field Stackelberg Stochastic Differential Game
差距：作者列与 [21] 逐字相同（复制痕迹），arXiv ID 指向博弈论论文，所标题名 arXiv 全库无命中——凭记忆拼装条目的典型三重破绽（复制作者+挪用 ID+虚构题名）。
锚点对比结论：差距明显

## 问题清单
[critical]｜[4]｜DOI 真身=Strekha 慢光 LDOS 文；所标题名/作者全库无命中，纯虚构｜删；亚周期电子动力学需求改走 02_literature 检索回录
[critical]｜[24]｜作者列与[21]逐字同；2502.07390 实为 Stackelberg 博弈论文，纯虚构｜删；Zhao 组亚周期偏振文检索确认后重录
[critical]｜[25]｜"Hu 等晶体电荷迁移"题名 arXiv 无命中；2506.07013 实为 UNO 视觉里程计｜删或换真实固体阿秒电荷迁移文献并回录
[critical]｜[31]｜"Yu/Zhang 量子层析"题名无命中；2503.07256 实为中子星 Δ 共振（PRD 112）｜删；反演方法学改引真实综述
[critical]｜[38]｜DOI 130.086201 实为量子反常霍尔边缘通道文；"Shen 瞬态对称破缺"题名无命中｜删；scheme L71 标志信号改引真实 SHG 对称破缺文
[critical]｜[32]｜DOI=Junquera 极性氧化物 RMP；Tsuji 系列真身为 RMP 86, 779 (2014)｜整条换 Aoki 等 RMP 86, 779，DOI 10.1103/RevModPhys.86.779
[critical]｜[34]｜题名"双梳光谱"与 DOI 不符：10.1364/OPTICA.1.000010 实为微梳光时钟文｜题名改 Microresonator frequency comb optical clock
[high]｜[18]｜DOI 10.1126/science.1241373 于 CrossRef 与 doi.org 双 404｜改以 arXiv:1310.7563 或 Science 官网核准 DOI 后重录
[high]｜[6]｜arXiv 2510.15207 一作实为 Ciappina；Lucchini/Nisoli 不在作者列｜作者列按 arXiv 页面整行重抄
[high]｜content L33/L45/L47｜[6]=Ciappina、[14]=Lorenzo、[15]"Jakob"、[16][17]=Stammer 与总表错挂，0 修复｜全文 [N]→条目主题全量比对重排
[high]｜列表整体｜8 条孤儿未获正文引用｜逐条裁决：删除或在正文补锚点
[high]｜列表整体｜45 条超出 20-40 区间｜清虚构 5 条+裁决孤儿后压至 ≤40
[medium]｜[29]｜一作 "B. Lorenzo" 名首字母与全名待核｜按 arXiv 作者页核准
[medium]｜[21]｜arXiv 条目未核查是否已正式发表｜补卷期或统一 arXiv 体例
[medium]｜领域缺口｜磁拓扑体系（MnBi₂Te₄/Co₃Sn₂S₂，scheme D5 对象）无直接文献｜补 1-2 条磁拓扑 HHG/非线性光学文献
[low]｜[5][23]｜et al. 截断位置不统一（3 位 vs 10 位作者）｜统一为 3 作者+et al.

## 维度评分
| 维度 | 得分 | 依据 |
|---|---|---|
| 严谨性 | 0.30 | 9/45 条实锤（虚构 5+错构 2+死链 1+一作错置 1，占 20%）；上轮错挂零修复 |
| 完整性 | 0.72 | 45 条超上限；孤儿 8 条；时效达标（2023+ 占 30/45=67%）；磁拓扑小缺口 |

## 对抗结论
- 本轮 16 个问题（critical 7, high 5, medium 3, low 1）
- 相比上一轮（引文专项 R1）：新增实锤 9 条；上轮移交 5 处错挂未解决（0 修复）
- 是否达到输出标准：否——虚构条目成批存在且跨轮零修复，须全表重建后做第 4 轮复验
- 返工优先级：P0 删 5 条虚构+重建 [32][34]；P1 content 引用编号全量重排+修 [18][6]；P2 孤儿裁决+压数量+磁拓扑补引
- 下轮建议：writer 修复须将命中文献回录 02_literature/；第 4 轮做 [N]→条目全量比对与虚构清零验收

## 评分
创新性：N/A
可行性：N/A
严谨性：0.30
完整性：0.72
综合评分：0.51
