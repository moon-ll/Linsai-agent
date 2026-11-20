# 评审团定点核查 findings（v7.2.81 引擎亲审）

> 课题：general-houston-kronig-penney-landau-zener-20261004
> 评审员：引擎亲审模式（不调用外部 LLM/脚本，全部亲自读文、检索、核对、判定）
> 日期：2026-11-01
> 核查对象：04_proposal/sections/ 五章节全文（rationale/content/scheme/full_review/references）+ params.json 口径表；06_panel-preaudit-20261101/ 仅作参考、不作结论。

## 核查方式说明

- 五章节全文通读（Read 全量，非节选），逐条比对任务下发的 15 条历史遗留靶子（行号 + 原文）。
- 残留检索：对旧口径/旧编号/旧表述做全文 grep（"能区上分离""Lesko 等[21]""已按真身独立核证""Jiang 等[11]/[12]"等，全部零命中）。
- 引用并集核对：三章正文引用编号并集逐号清点为 1–42 全覆盖、无孤儿条目（与 full_review 口径表"三章正文引用并集覆盖全部 42 条"声明一致）。
- 引用网检：8 条关键引用经 WebSearch/WebFetch 核实真实元数据（详见文末清单）。注意：本环境网检为真实外部源，refs 中 2026 年条目（[12][14][19][26][30][41][42] 等）部分仅能核实到 DOI/录用页层面，未逐字段核到卷期页的已在下表注明。
- 超长句核查：引擎逐句人工计数（口径：含中英文与标点的单句字符数，句界按 。；：切分），对三章目测最长的 12 句逐一实数，最长 108 字，无 >120 字句。
- 本轮未对 5 个章节文件做任何 Edit：全部 critical/high 靶子在当前盘面文本（writer 2026-11-01 04:10–04:15 修复落盘后版本）上已解决，本轮为独立实证复核而非修复轮。

## 表 A：遗留靶子核对表（15 条）

| # | 靶子摘要 | 级别 | 当前文本证据 | 判定 |
|---|---------|------|-------------|------|
| 1 | [3] 真身 Kane-Mele"签名不可靠"，9 处错挂 MoS₂ 两指纹 | CRITICAL | [3] 全稿仅 3 处具名（rationale L33、scheme L117、full_review L13），均按"旋向/反常椭圆度/椭圆二色/发射时延四类拓扑签名不可靠"真身结论挂靠；两指纹全链改挂 [9]（Yue & Gaarde），旧 9 处错挂零残留 | 已解决（网检坐实 [3] PRX 13, 031011 作者链与 [9] PRL 130, 166903 真实性） |
| 2 | refs 旧 [12] 虚构 Jiang 7 人条目，真身 Liu C 等 NJP 22(7):073046(2020) | CRITICAL | 现 refs [11] 即该真身条目，作者链/卷期页/DOI 与 IOP 原页逐字段一致；虚构条目无残留 | 已解决 |
| 3 | refs 旧 [24] 作者链错挂（Abanador/漏 Browne），真身 Wu M, Browne, Schafer, Gaarde | CRITICAL | 现 refs [22]：Wu M, Browne D A, Schafer K J, Gaarde M B, PRA 94(6): 063403 (2016)，与 APS 原页一致；无 Abanador（任务所记"Browne S"实为 Dana A. Browne，refs 记 D A 正确） | 已解决 |
| 4 | rationale L5 ZnO 挂 GaSe[7]、MoS₂ 挂 WSe₂ | HIGH | 现文 ZnO 组挂 [1,20]（Ghimire/Obreshkov 均 ZnO）、低维组挂 [4,11,12]（Bi₂Se₃/MoS₂/NbOI₂），与真身一致；[7]（GaSe）全文未挂 ZnO，[10]（WSe₂）未错挂 | 已解决 |
| 5 | 纯 arXiv 条目以定论口吻支撑动机链（旧 [13]/[33] 等） | HIGH | 六条真 arXiv 条目 [12][30][31][32][41][42] 正文作者式引用处均带"（预印本）"限定；[13] 为 2018 已刊 Floss PRA、[33] 为 2026 已刊 PRR，原靶子对象已随 refs 换真身而消解 | 已解决 |
| 6 | scheme [21] 真身 Lesko，正文挂"非平衡 Berry 曲率读出"内容错挂 | HIGH | 现 [21] = Klemke（Nat Commun 10: 1319, 2019，偏振分辨 HHG 谱学），正文两处（L103 可行性佐证、L125 方法学基准）均为其真实内容；Lesko 改挂 [19]，"石墨烯 Floquet 拓扑态/整流电流读出"描述与 arXiv 2407.17917 及其 Nat Phys 2026 刊版一致 | 已解决 |
| 7 | 超长句：rationale 17 处 / content 16 处 / scheme 10 处 >120 字 | HIGH | writer 04:14 已全量拆分；引擎逐句人工计数抽查三章最长 12 句（rationale L19 Zhao 句 108、L19 蓝移红移句 105、L37 Jiang 句 107、L21 van Essen 句 92、content L29 第二层句 92、L81 目标二句 96、scheme L103 k 路径句 107、L131 解决路径句 90、full_review L8 主线句 113 等），全部 ≤120 字，技术内容/数值/引用编号未变 | 已解决 |
| 8 | scheme"能区上分离"不成立（缺陷窗 0.4–1.5 eV 与反常窗 <1 eV 重叠） | HIGH | scheme L89 改为"两个窗口在 0.4–1.0 eV 重叠，本方案据此不把能区分离当作独立判据。1.0–1.5 eV 段由子带隙选择规则单独承担区分。重叠的 0.4–1.0 eV 段改由另外两项判据承担"；content L51、scheme L153、full_review L36 口径表三处同口径 | 已解决 |
| 9 | 2.4 μm 档"5–13 阶"与"5–11 阶+13 阶边界"两版冲突 | HIGH | scheme L13 压缩为分档回指（"逐档数值见 §3.1"）；L71 统一为"2.4 μm 驱动 5–11 阶（2.58–5.68 eV）入主通道，13 阶 6.72 eV 处于 6.7 eV 上限边界"；L81 同口径；逐档能量复算（0.8/1.6/2.4/3.2 μm）全部自洽 | 已解决 |
| 10 | full_review 1511 字超骨架上限且含过程内容 | CRITICAL | 现为"主线论证链 + 章节衔接点 + 跨章节统一口径表"三段式骨架；头注声明过程材料一律入 05_review/，正文无处置记录/轮次说明；体量约 1850 汉字（预审计程序口径，引擎复核结构无过程内容），低于 3000 字上限 | 已解决 |
| 11 | full_review Rasputnyi 违 canonical 列入缺陷偶次谐波动机链 | HIGH | 现 L14 明确"Rasputnyi[18] 在三章中的角色限于驱动场量子统计……不作为缺陷偶次谐波的证据"；动机链留偶极相位[15]与缺陷局域化[6]；与 params.json [18] 语境口径一致 | 已解决 |
| 12 | full_review"研究方案"文献列表虚报（scheme 实引仅 25 篇） | HIGH | 虚报列表已删除，口径表改为计数声明"三章正文引用并集覆盖全部 42 条，无孤儿条目、无未被引用条目"；引擎逐号清点属实（1–42 全覆盖） | 已解决 |
| 13 | refs [16]/[29] 同文双编号（arXiv:2410.09178 已见刊 ACS Photonics） | HIGH | 双编号已消除；ACS Photonics 刊版现为 [27]（Chen Z, Levit M, Kern Y, Roy B, Goldner A, Krüger M，12(5): 2819-2827, 2025，DOI 10.1021/acsphotonics.5c00410），作者链与 arXiv 原页逐字一致；正文 MgO/800+2000 nm/MHz/9 eV 平台/730 as claims 与原文摘要逐项吻合 | 已解决 |
| 14 | refs 头注"已按真身独立核证"声明被证伪 | HIGH | 现头注为体例说明（条目排列/预印本标注规则/括注作用），无核证声明 | 已解决 |
| 15 | [33] 见刊状态须复查 | HIGH | 网检 APS 录用页真实：PRR 8, 033302，2026-09-11 刊出（Received 2025-10-24, Accepted 2026-08-03），DOI 10.1103/sxcl-yqs7 与 refs 条目一致；条目保留原状 | 已解决 |

## 表 B：新发现问题表（本轮主动发现，共 1 条）

| # | 位置 | 级别 | 描述 | 处置建议 |
|---|------|------|------|---------|
| P1 | scheme.md §3.1 L73 | low | 现文"子带隙扩展通道覆盖 0.4–1.5 eV……对应 2.4–3.2 μm 驱动的 3 阶与子带隙判据所需能区"。复算：2.4 μm 3 阶 = 3×0.5167 ≈ 1.55 eV，高于子带隙窗上缘 1.5 eV，亦在 L71 所列 2.4 μm 主通道记录阶次（5–11 阶）之外；子带隙通道真正覆盖的 3 阶仅 3.2 μm（3×0.3875 ≈ 1.16 eV）。属边界归腔表述不严，不影响三角判据执行（1.0–1.5 eV 段区分与 0.4–1.0 eV 重叠段分工均在窗内成立） | 下轮改为"对应 3.2 μm 驱动的 3 阶与子带隙判据所需能区"，或在 §3.1 注明 2.4 μm 3 阶（1.55 eV）由主通道下缘覆盖。本轮不改（low 级 + 涉及探测通道口径的设计表述，保守精准原则下留待方案作者确认） |

## 附：引用网检记录（外部来源清单）

1. [3] Neufeld 等——APS 原页（journals.aps.org/prx/abstract/10.1103/PhysRevX.13.031011）：作者链 Neufeld O, Tancogne-Dejean N, Hübener H, De Giovannini U, Rubio A 与 refs 一致。
2. [9] Yue & Gaarde——PRL 130, 166903 (2023)"Characterizing Anomalous High-Harmonic Generation in Solids"检索坐实，两指纹改挂出处成立。
3. [11] Liu C 等——IOP 原页（10.1088/1367-2630/ab9a88）：Candong Liu, Yinghui Zheng, Zhinan Zeng, Ruxin Li，NJP 22(7): 073046 (2020) 逐字一致。
4. [22] Wu M 等——APS/检索：Mengxi Wu, Dana A. Browne, Kenneth J. Schafer, Mette B. Gaarde，PRA 94, 063403 (2016) 一致。
5. [27] Chen Z 等——arXiv:2410.09178 原页 + ACS Photonics 检索：Zhaopin Chen, Mark Levit, Yuval Kern, Basabendra Roy, Adi Goldner, Michael Krüger；12(5): 2819-2827 (2025)；MgO/800+2000 nm/MHz/9 eV 平台/730 as/三带 SBE 逐项吻合。
6. [29] Wang G 等——APS 原页（10.1103/PhysRevA.109.063511）：Gan Wang（中国地质大学（武汉））、Yu-Xuan Chen、Mingjie Li、Tao-Yuan Du（华南理工/地大武汉），PRA 109(6): 063511 (2024)；rationale §2.5 国内归属表述属实。
7. [21] Klemke 等——Nat Commun 10, 1319 (2019) 检索：实验材料含 ZnO 与 MgO，scheme L103 归属成立。
8. [19] Lesko 等——arXiv:2407.17917 检索：单层石墨烯体系、相锁二次谐波场、"harmonic Floquet 谱学"；刊版 Nature Physics (2026) DOI 10.1038/s41567-026-03429-7 与 refs 一致。
9. [33] Molinero 等——APS 录用页（journals.aps.org/prresearch/accepted/10.1103/sxcl-yqs7）：PRR 8, 033302，2026-09-11 刊出，作者链与 refs 一致。
