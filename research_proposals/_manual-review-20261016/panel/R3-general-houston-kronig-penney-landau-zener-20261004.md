# R3 引用审校 — general-houston-kronig-penney-landau-zener-20261004

审校范围：04_proposal/sections/{rationale,content,scheme,references}.md（refs 30 条，编号 [1]–[8]、[11]–[15]、[17]–[33]，跳号 [9][10][16][34] 头注声明为历史删除项）。
审校日期：2026-10-17。对账脚本：/tmp/r3_citation_audit.py（终端执行故障，以等价正则提取+人工比对完成，脚本可复跑）。
背景：该课题曾因文献虚构被大规模修复；本次重点验证现存 30 条是否全部真实可溯，并对 2024–2026 近年条目随机抽查 6 条。

## 编号对账（五项）

| 项 | 计数 | 明细 |
|---|---|---|
| 占位符 | 0 | 无未填编号 |
| 死条目 | 0 | 30 条均被三章引用（rationale 28 号 + content 补 [21] + scheme 补 [4][5][11][23]） |
| 超界 | 0 | 正文最大引用号 33 = refs 最大号 |
| 一号两用 | refs 层 0；正文层 2 | ①rationale L5"Calegaro 等[26]"所指文献（2026 现象学综述）在 refs 中不存在，[26] 编号实被 Vampa PRB 2015 占用（虚构引用+错占编号）；②rationale L41 同一 [33] 先挂"超倍频程超连续谱相干合成 ZnO 验证"再挂"Keldysh 跃迁"，前者非 arXiv:2208.10032 内容（见意见） |
| 断链 | 编号层 0；文献层 1 | "Calegaro[26]"引用对象不存在（检索无此文），属文献级断链 |

跳号 [9][10][16][34] 为头注声明的历史删除，合规；头注"条目数量 30 条"与实物一致 ✓。

P0 复核：①P0-critical#22"[12] 作者链卷期页全错（Jiang 系虚构）"——refs 条目已按 CrossRef 真身修复为 Liu C, Zheng Y, Zeng Z, Li R, NJP 22(7):073046 ✓，但正文"Jiang 等[12]"作者名未跟改（残留，R3-04）；②P0-critical#23"[24] 作者链错挂 Abanador"——已修复为 Wu M, Browne D A, Schafer K J, Gaarde M ✓；③P0-high#20"[16] 跳号"、#24"[16]/[29] 同文 arXiv:2410.09178"——已修复（[16] 删除、[29] 改引 ACS Photonics 刊版 DOI:10.1021/acsphotonics.5c00410）✓；④P0-high#25 头注"已核证"声明——现版头注已无该声明 ✓；⑤P0-high#12"Schmidt 等[7]/Srivastava 无编号"——grep 无 Schmidt[7]/Srivastava 残留，scheme 现写"Schubert 等[7]" ✓。

## 联网核实记录（11 条：P0/高风险 5 + 近年随机抽查 6，含证据 URL）

**高风险条目：**
1. **"Calegaro 等[26]"（rationale L5）**：**虚构**。多轮检索无"2026 年 Calegaro 固体 HHG 截止能量现象学综述"；相近真实人物为 Francesca Calegari（气相阿秒方向，J. Phys. B 49, 062001 综述为 2016 年且主题不符，https://public-pages-files-2025.frontiersin.org/journals/nanotechnology/articles/10.3389/fnano.2025.1667217/pdf ）。refs [26] 实为 Vampa PRB 91, 064302 (2015)。判定：虚构引用 + 编号错占（critical）。
2. **[29] ACS Photonics 12(5):2819-2827 (2025)**：真实。第一作者 **Zhaopin Chen**（陈，Technion），作者链 Chen/Levit/Kern/Roy/Goldner/Krüger 与 refs 条目一致 ✓。https://pubs.acs.org/doi/10.1021/acsphotonics.5c00410 ；https://figshare.com/collections/_/7787840 。但 rationale L7/L37 写"Zhang 等[29]"——作者错挂。
3. **[12] NJP 22(7):073046 (2020)**：真实（P0 给出的 CrossRef 真身，多处独立引文索引复核：https://www.frontiersin.org/journals/nanotechnology/articles/10.3389/fnano.2025.1667217/full ；https://exaly.com/paper-pdf/68953605/citation-report.pdf ）。第一作者 Liu C；正文"Jiang 等[12]"（rationale L23、content L15）为旧虚构作者链残留。
4. **[20] Rasputnyi, Nat. Phys. 20(12):1960-1965 (2024)**：真实，卷期页 DOI 全对（https://www.nature.com/articles/s41567-024-02659-x ）。但**内容错挂**：论文核心是亮压缩真空（BSV）superbunching 光子统计使 4–7 次谐波产额较同均强经典光增强 5–15 倍；样品 Mg:LN 中 Mg 掺杂为标准防损配方，全文无"缺陷态 vs 纯晶体"对比实验。正文三处（rationale L31、content L41、scheme L111/L121）将其归为"缺陷态使产额高于纯晶体"证据——citation_misattribution（critical，支撑方向二甄别协议的动机链）。
5. **[33] arXiv:2208.10032**：真实，作者王帅/贺新奎/梁玥瑛/苏亚北/方少波/魏志义（中科院物理所），内容为功率标度+Keldysh 多光子→隧穿转变 ✓（https://arxiv.org/abs/2208.10032 ）。rationale L41 首句把"超倍频程超连续光谱相干合成"方法学也挂 [33]，非该文内容（一号两用）。

**近年条目随机抽查（2024–2026，6 条）：**
6. **[13] arXiv:2601.21273（NbOI₂，2026）**：真实 ✓，11 位作者 Hu/Li/Huang/Qian/Ding/Wang/Liu/Wu/Lu/Zhang/Wang 与条目一致；4 μm 驱动、各向异性奇偶次谐波至 16 阶匹配。https://arxiv.org/abs/2601.21273
7. **[15] Thümmler, CPC 320:109958 (2026)**：真实 ✓（Jena Gräfe 组官网逐字段一致：作者五人、卷 320、文章号、DOI）。https://www.chemgeo.uni-jena.de/14960/publikationen
8. **[21] Lesko, Nat. Phys. 22(10):1607-1614 (2026)**：真实 ✓（MPSD 官网），graphene Floquet 光控电子，content L61"报告的是 graphene Floquet 拓扑态上的整流电流而非 HHG 谱学读出"与内容匹配 ✓。小瑕疵：refs 作者顺序与官网（Weitz 居第二位）不一致；scheme L129 称其为"综述"实为研究论文。https://www.mpsd.mpg.de/7709/publikationen?year=2026
9. **[31] Wang, PRA 109, 063511 (2024)**：真实 ✓，Gan Wang/Yu-Xuan Chen/Mingjie Li/Tao-Yuan Du，地大（武汉）+华南理工，偏振分辨对称性判读 MoS₂ 带内-带间主导通道，与正文声称完全匹配。https://journals.aps.org/pra/abstract/10.1103/PhysRevA.109.063511
10. **[32] Zhao, arXiv:2507.03791（Floquet-engineering，2025）**：真实，MgO Floquet-Bloch 边带+布里渊区边缘非绝热耦合+瞬态破缺时间反演，与 rationale L19 描述高度匹配 ✓。**但 refs 作者链错误**：实际 Zhao C, **Jurkovičová L**, Zou X, Miller B T Q, …, **Zaïr A**（13 人）；条目所写"Jiang L, Zuerch M"中 Zuerch M 不在作者列表（拼凑作者链）。https://arxiv.org/abs/2507.03791
11. **[25] Yue & Gaarde, PRL 124, 153204 (2020)**：真实（hBN 不完全再碰撞理论：电子-空穴对极化能、子循环双峰、ERM 含 Berry 连接/曲率/偶极相位）。**内容错挂**：rationale L5 将其列入"超快载流子预激发调制[25]"，论文无任何预激发调制内容。https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.124.153204

## 正文声称与文献内容匹配性抽查

- ✓ 匹配：[13] NbOI₂ 各向异性 16 阶；[15] 良态去相干；[21] graphene Floquet 非 HHG 读出（正文自我限定正确）；[31] 国内偏振分辨通道判读；[32] Floquet 边带机制；[33] Keldysh 跃迁；[29] MHz 双色场 XUV（内容级）。
- ✗ 不匹配：[20] 被归为缺陷态增强证据（实为量子光统计增强）；[25] 被归为预激发调制（实为不完全再碰撞）；"Calegaro[26]"对象不存在。
- △ 弱匹配：scheme L53 T₂ 四材料取值（MoS₂ 4 fs/ZnO 6 fs/MgO 8 fs/Bi₂Se₃ 5 fs）仅列三条依据文献且顺序与材料序列对不上（Schubert[7] 与 Hohenleutner[11] 均为 ZnO 工作，MoS₂ 与 Bi₂Se₃ 取值无文献锚点）。

## 意见清单

[R3-01|critical] rationale｜L5｜"Calegaro 等[26]"文献不存在，[26] 实为 Vampa PRB 2015，虚构引用错占编号｜原文摘录："2026 年 Calegaro 等[26]对固体 HHG 截止能量的现象学综述进一步把电场、波长…"｜删该句，或改挂真实综述（Ciappina, Adv. Phys. 74 (2025)；Goulielmakis & Brabec, Nat. Photon. 16, 411 (2022)）并新增条目，不得复用 [26]。

[R3-02|critical] rationale+content+scheme｜rat L31、con L41、sch L111/L121｜[20] Rasputnyi 被归为"缺陷态使产额高于纯晶体"证据，论文实为 BSV 光子统计增强、无缺陷对比实验｜原文摘录："证明，缺陷态可使谐波产额高于纯晶体，把缺陷谐波的产额调制推到可对照实验的水平"｜四处改为"亮压缩真空光子统计（superbunching）使谐波产额较同均强经典光增强 5–15 倍"；方向二缺陷动机链仅保留 Xu[6] 支撑或补真实缺陷-产额文献。

[R3-03|critical] scheme｜L53｜T₂ 四材料取值依据仅三条文献且两重复 ZnO，MoS₂/Bi₂Se₃ 取值无锚｜原文摘录："依据分别为 Schubert 等[7]、Hohenleutner 等[11]、Korolev 等[28]的室温实测值"｜逐材料补依据或改"参照 ZnO/MgO 实测值量级外推，Bi₂Se₃/MoS₂ 待本项目标定"，删除"分别为"的假一一对应。

[R3-04|high] rationale+content｜rat L23、con L15｜"Jiang 等[12]"作者错挂，该文第一作者为 Liu C（P0#22 修复残留）｜原文摘录："Jiang 等[12]在速度规范下以紧束缚三带模型描述单层 MoS₂"｜两处改"Liu 等[12]"，全文 grep "Jiang 等[12]" 清零。

[R3-05|high] rationale｜L7/L37｜"Zhang 等[29]"作者错挂，ACS Photonics 该文第一作者为 Chen Z（Zhaopin Chen）｜原文摘录："Zhang 等[29]在 MgO 中以 800 nm + 2000 nm 合成双色场、1 MHz 重频…"｜两处改"Chen 等[29]"。

[R3-06|high] references｜L67 条目 [32]｜作者链拼凑：Jiang L 与 Zuerch M 均不在该文作者列表（实际第二作者 Jurkovičová L、通讯 Zaïr A）｜原文摘录："Zhao C, Jiang L, Zuerch M, et al. Floquet-engineering unveiled by high-harmonic generation"｜按 arXiv v2 改"Zhao C, Jurkovičová L, Zou X, et al."（13 人取前三+et al.），并补 v2 版本年份 2026。

[R3-07|high] rationale｜L41｜[33] 一号两用：首句"超倍频程超连续谱相干合成"非 arXiv:2208.10032 内容｜原文摘录："以超倍频程超连续光谱相干合成技术在 ZnO 体系中实现少周期极端光场驱动…[33]"｜首句另挂真实合成光场文献（如同组 Ultrafast Science/PRL 工作并补条目）或删去首句只保留 Keldysh 跃迁句。

[R3-08|high] rationale｜L5｜[25] 错挂"超快载流子预激发调制"，论文为 hBN 不完全再碰撞理论（无预激发内容）｜原文摘录："缺陷态局域化[6]、范德华铁电体各向异性[13]、超快载流子预激发调制[25]"｜该列表项删除或改挂真实预激发文献；[25] 在 L59 的再碰撞语境引用可保留。

[R3-09|low] references+scheme｜refs L45 条目 [21]、sch L129｜[21] 作者顺序与官网不一致（Weitz 居次席）；scheme 称其为"综述"实为研究论文｜原文摘录："由综述[21]中示范的非平衡 Berry 曲率读出方法学延伸而来"｜条目作者序按官网校正（Lesko, Weitz, Wittigschlager, Li, Heide, Neufeld, Hommelhoff）并补卷期页 22(10):1607-1614；scheme"综述"改"研究工作"。

## 结论

大规模修复后编号体系已收敛（占位/死条目/超界/断链计数层面全零，跳号有声明），联网核实 11 条中 10 条文献本体真实、卷期页可信，P0 五项引用类问题已实质修复四项半。但修复呈"refs 已改、正文未跟"的半程状态：仍存 1 条虚构引用（Calegaro[26]）、1 条关键内容错挂（[20] 缺陷归因，三处）、1 条拼凑作者链（[32]）、2 条作者名错挂（Zhang[29]/Jiang[12]）与 [33] 一号两用、[25] 错挂。建议本轮一次性执行 R3-01～R3-08 后全文 grep 复核。
