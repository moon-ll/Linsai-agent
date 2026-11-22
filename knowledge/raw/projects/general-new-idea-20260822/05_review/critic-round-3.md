# 对抗评审报告（第 3 轮 · 参考文献专项）

元信息：general ｜ 2026-09-07 ｜ 对象 04_proposal/sections/references.md（20 条）｜ 编号一致性采信程序预检，未重复核对。原 critic-round-3.md 为整体一致性线报告，已备份至 .archive-critic-round-3-consistency-line-20260907.md 后接管本文件名。
核查方法：CrossRef 逐条 DOI 反查 14 条（[15] 以 10.7498/aps.66.134207 构造反查）；arXiv API 批量反查 7 条，2408.05187/2405.02409 另取全作者链（17/20 人）逐名比对。

## 预检采信项
- 编号 1-20 连续，正文-列表双向无缺、无未引用条目；grep 抽验三个正文章节引用编号与预检口径一致。
- 数量 20 篇处 20-40 区间下限，达标。

## 核查结果总览
- 属实且准确：[1][2][5][7][8][9][19][20]；[15] 无标识符但实测真实
- 属实但年份错：[4][6]；已见刊未回录：[10][11][14]；作者链截断：[3][13][19]
- 与标识符不符（错位/虚构）：[12][16][17][18]

## 问题清单
[critical]｜[16] L33｜标题张冠李戴：2408.05187 真实题为 All optical excitation of spin polarization in d-wave altermagnets，作者链属实｜P1 action:rewrite 改用真实标题
[critical]｜[17] L35｜一作 Nádvorník 与 Springholz/Khosravi 均不在 2405.02409 作者链，真实题为 Altermagnetism imaged and controlled down to the nanoscale，一作 Amin｜P1 action:rewrite 一作+标题按实改
[high]｜[12] L25｜2606.31573 仅 Mizuno K 单作者，Hakobyan/Kato 系虚构合作者｜P1 action:remove 删两位合作者
[high]｜[18] L37｜DOI 实为 PRB 112:L081105(2025)、一作 Liu Y，非 Bhattacharya/PRL，卷期缺｜P1 action:rewrite 期刊卷页一作按 Crossref 改
[medium]｜[4] L9｜年份应为 2010，误作 2011｜P2 action:verify 改 2010
[medium]｜[6] L13｜年份应为 2016，误作 2017｜P2 action:verify 改 2016
[medium]｜[10][11][14] L21/23/29｜三篇 arXiv 已见刊未回录：Prog Surf Sci 100:100795(2025)、Nature 656:854-860(2026)、PRM 10:074413(2026)｜P2 action:update 换正式版 DOI
[low]｜[3][13][19] L7/27/39｜实际作者仅 3-5 人却写 et al.，作者信息损失｜P3 action:rewrite 删 et al. 或列全
[low]｜[15] L31｜无 DOI/arXiv 标识符，无法程序化溯源｜P3 action:add 补 DOI:10.7498/aps.66.134207（实测真实）
[low]｜全表｜20 篇踩区间下限；自旋分辨 HHG 检测技术类文献缺位｜P3 action:add 增补 3-5 篇 2024-2026 文献

## 相关性与缺失引用
- 20 条全部围绕交变磁体与固体高次谐波主题，无无关引用；预检双向核对无缺口。
- 时效性：2024-2026 文献 10/20=50%（含 2026 年 3 篇），达标但处边缘。

## 锚点对比
引用：[17] 申请书原文 "Nádvorník L, Springholz D, Khosravi M, et al. Nanoscale imaging and control of altermagnetism in MnTe. arXiv 2405.02409 (2024)"
对比：arXiv:2405.02409 真实记录 "Altermagnetism imaged and controlled down to the nanoscale — O. J. Amin, A. Dal Din, E. Golias 等 20 人 (2024)"
差距：标题同义改写掩盖错位，一作及前三位作者全部不在真实作者链——凭记忆克隆元数据的典型形态；同批实锤 [16][12][18]，writer 须对全部凭学科知识引用条目执行 DOI 反查后再定稿，命中文献回录 02_literature 检索池。
锚点对比结论：差距明显

## 对抗结论
- 本轮 10 个问题（critical 2 / high 2 / medium 3 / low 3）
- 无前轮参考文献专项基线（本轮首检）；预检高风险 10 条中 6 条核实真实（含 [15]），[12][16][17][18] 四条实锤
- 是否达输出标准：否——2 条 critical 张冠李戴未修复，文献层不可放行；返工优先级 P1=[16][17][12][18]，P2=[4][6][10][11][14]，P3=其余
- 下一轮：writer 修复后 critic 复核 4 条 P1 条目并抽验新换正式版 DOI 有效性

## 评分
创新性：N/A
可行性：N/A
严谨性：0.40
完整性：0.75
综合评分：0.58
