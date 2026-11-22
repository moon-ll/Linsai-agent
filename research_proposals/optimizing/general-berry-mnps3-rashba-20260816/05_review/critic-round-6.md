# 对抗评审报告（第 6 轮·参考文献专项）

项目类型：general｜对象：references.md（30 条，mtime 09-10）｜日期：2026-09-10

## 一、核查方法与总量结论
- 30 条全量真实性反查：16 条 DOI 走 CrossRef+期刊落地页；9 条 arXiv 走全文标题/作者核验；5 条 APS 短 DOI（gly7-jzfl/jf1w-wdg8/c4dm-12ng/m4x3-fb5d 等）走 CrossRef API 核卷期与文章号。
- 真实性：30/30 真实存在，无虚构、无一作错置、无 DOI 死链。R5 标记的 [8] DOI ab27d8 已改为 ab27d5；[23] 卷期"9:82"已改为"2025, 10:11"——两项 high 闭环。
- 一作分裂核查：[16][20][21] Basnet 系均落 Rabindra Basnet（Arkansas/Fayetteville），CrossRef 一致；[3][4] Šmejkal/Sinova/Jungwirth 2022 两条分别 PRX 12 040501 与 031042，无重复编号。
- 预检口径：预检仍报"[1,2] 未引用"——R5 已澄清（rationale L5 合并逗号组 [1,2]），视为预检噪声；但 writer 终稿须确认该引用句确实存在以平后续 R7/R8。

## 二、四项检查结论
1. 引文格式：作者-年-刊-卷-页（Nature/Nanoscale/JPSJ）或卷-文章号（APS）严格按刊体例；DOI/arXiv 二选一；en-dash 页码统一。
2. 引用相关性：30 条全围绕"altermagnetism(19)/MPX3-MnPS3(8)/Rashba-SOC(2)/HHG(4)/滑移铁电+声子(3)"，与 Berry+MnPS3+Rashba+HHG 主线强相关，无无关引用。
3. 缺失引用：无幽灵编号；[30] Manchon 2015 已闭合 R5 Rashba 原始文献缺口。
4. 数量与时效：30 条∈[20,40] 达标；2023-2026 文献 22/30≈73%（≥50% 阈值达标）；2026 preprints 5/30≈17%（< 30% 上限达标）。

## 三、问题清单
[medium]｜L3+L5 [1][2]｜Baltz RMP / Jungwirth Nat Nano 题名完全相同"Antiferromagnetic spintronics"｜任一条加"(Review)"或年份括注消歧
[medium]｜L41 [20]｜Basnet & Hu Nanoscale 16:15851 系综述但条目未标 "(review)"｜条末补"(review)"
[low]｜L7+L9 [3][4]｜同三人组 Šmejkal/Sinova/Jungwirth、同年同刊（PRX 2022），仅文章号区分｜两行间补"综述/理论"或文章号提示
[low]｜L19 [9]｜实 7 位作者仅列 3+et al.，与他条 4-5 位不一致｜列首四位与他条对齐

## 四、锚点对比（[12] Yang & Liang PRL 136 226702）
引用："Yang L, Liang L. Nonlinear opto-magnetic signature of d-wave altermagnets. Phys Rev Lett, 2026, 136: 226702. DOI: 10.1103/gly7-jzfl"
对比（CrossRef+APS 落地页）：PRL 136 issue 22, art 226702, accepted 2026-05-12, Funder NSFC 12204329/12204331（川师大 Yang Lijun/Liang Long）。题名/刊卷/年/文章号/DOI 短码/作者机构全对齐；gly7-jzfl 属 APS 2026 新格式（同源 d4dm-12ng/jf1w-wdg8），非虚构。
锚点对比结论：达标

## 维度小结
- 严谨性 0.86：30/30 真实，DOI/arXiv 全量通过，R5 两 high 闭环；扣 [1,2] 同题名歧义+[20] 综述未标（2 medium）。
- 完整性 0.88：30∈[20,40]、73% 时效达标、Rashba 缺口闭合；扣 [1,2] 预检再报需 writer 终稿确认。

## 对抗结论
本轮发现 4 个问题（critical:0, high:0, medium:2, low:2）。相比 R5：2 high 闭环，无新增 critical/high；新增 2 medium 均为体例标注。达到输出标准：是。R7 验收＝①[1]/[2] 任一题面消歧；②[20] 补"(review)"；③终稿 grep 确认 [1,2] 在 rationale 引用句存在以平预检；④[3][4] 间补区分提示（可省）。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.86
完整性：0.88
综合评分：0.87
