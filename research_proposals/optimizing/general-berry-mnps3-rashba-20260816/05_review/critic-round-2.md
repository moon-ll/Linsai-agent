# 对抗评审报告（第 2 轮 · 参考文献专项）

元信息：项目类型 general｜评审日期 2026-09-18｜profile critic｜范围 references.md（40 条）+ 三章正文 [N] 编号一致性已由预检确认｜本轮聚焦：5 条裸 arXiv 幽灵引用补齐、预印本管理、时效性、相关性、格式统一性。

## 综合评分依据
R1 对 11 条核心 DOI/arXiv ID（[12][14][19][24][26][33][37][39] + 2605.20067/2606.31573/2608.02393/2609.17500/2504.14821）经 CrossRef/arXiv API 逐条核查，作者首字母、卷期年、研究对象五件套与公开记录一致，无张冠李戴。预检高风险区 29 条未经检索条目经逐条比对元数据后退坡。但 (a) 5 条裸 arXiv 内联引用（2605.20067/2606.31573/2608.02393/2609.17500/2504.14821）仍未纳入 references.md 编号体系，预检漏扫后未补，构成幽灵引用；(b) [33] Sahu 条目缺 issue 编号未补；(c) 预印本核心论断（[15][17][25][28]）占 4/10，缺期刊接收状态标注。

## 维度评分
| 维度 | 得分 | 关键扣分 |
|---|---|---|
| 严谨性 | 0.75 | 5 条幽灵 arXiv；[33] issue 仍缺 |
| 完整性 | 0.82 | 数量 40 达上限；时效性 47.5% 退步；[1][2] 双 Baltz/Jungwirth 重叠 |

## 锚点对比（references.md vs CrossRef/arXiv 实测）
- [12] Yang "Nonlinear Optomagnetic Signature of d-Wave Altermagnets" PRL 136:226702（2026）→ CrossRef 10.1103/gly7-jzfl 返回作者 Yang Lijun/Liang Long（四川师范大学）、卷 136、issue 22、文章号 226702、收稿 2026-05-12 ✓
- [14] Ezawa "Spin-selective elliptic optical dichroism..." PRB 114:L111201（2026）→ CrossRef 10.1103/5rrq-5g1k 返回作者 Ezawa Motohiko（东京大学）、卷 114、issue 11、文章号 L111201、含 arXiv:2603.07490 预印本关联 ✓
- [33] Sahu "Ultrafast dynamics of SOEE... NiPS3" PRB 114:014413（2026）→ CrossRef 10.1103/vr4z-b3ky 返回作者 Sahu Sidhanta 等 10 人、卷 114、issue 1、文章号 014413 ✓；申请书缺 issue 编号
- [26] Gabriele "Hallmarks of spin textures for HHG in 2D" PRB 112:155421（2025）→ CrossRef 10.1103/m4x3-fb5d 返回 4 作者含 Gabriele/Ortix/Cuoco/Forte、卷 112、issue 15 ✓
- arXiv:2608.02393 Zhu "Floquet spin-group framework"（2026）→ arXiv 实测作者 Tongshuai Zhu、标题与正文 §2.4 描述一致 ✓
- 差距：5 条幽灵 arXiv 的真实性已验证，但未被吸收到 references.md 元数据，使编号体系与正文引用错位——已从"真实性未核实"降为"格式未补齐"。

## 问题清单

- [critical]｜references.md + rationale §1.3/§1.4/§2.2 + content §2.2/§2.3/§2.4 + scheme §3.3｜5 条裸 arXiv（2605.20067/2606.31573/2608.02393/2609.17500/2504.14821）未纳入 references.md 编号体系，构成幽灵引用｜5 条以 [N] 编号纳入参考文献列表（Zhang Q et al. Coherent terahertz magnon-phonon three-wave mixing arXiv:2605.20067 [41]；Mizuno K et al. High-harmonic spin-current signatures arXiv:2606.31573 [42]；Zhu T et al. Floquet spin-group framework arXiv:2608.02393 [43]；Mahmood F et al. Visualizing Berry curvature arXiv:2609.17500 [44]；Wang D et al. Band-spin-valley coupled exciton arXiv:2504.14821 [45]），正文同步替换为 [N]；action: rewrite
- [high]｜references.md L67 [33] Sahu｜条目 Phys Rev B 2026, 114: 014413 缺 issue 编号；同表 [26] 112: 155421 也缺 issue，CrossRef 实测 issue 分别为 1/15｜在卷与文章号之间补 issue：[33] "114 (1): 014413"；[26] "112 (15): 155421"；[13] "110 (23): 235101"；[14] "114 (11): L111201"；[24] "112 (6): L060401"；[12] "136 (22): 226702"；[16] "109: 184405"；action: rewrite
- [high]｜references.md L3-5 [1][2]｜两条目均为反铁磁自旋电子学综述，论题重叠，[2] Jungwirth 2016 正文引用 0 次属低使用率条目｜保留 [1] Baltz 2018 作为当代综述，[2] Jungwirth 2016 撤换为反铁磁 THz 自旋动力学综述（如 Kimel 2020 Nat Phys 综述）；action: rewrite
- [medium]｜references.md 预印本条目 [15][17][25][28]｜4 条预印本涉及项目核心论断（i-wave 多光子选择定则、Floquet-Rashba 调控、声子-劈裂线性关系、slidetronics 框架），若审稿期预印本被期刊拒绝或大幅修订将动摇论证基础｜预印本条目后添加"已投稿 XXX 期刊（截至 2026-09 未见接收记录）"或"[期刊审稿中]"标注，正文对应论述加"据目前检索（截至 2026-09）"等限定语；action: rewrite
- [medium]｜references.md L31 [15] Ghorashi｜条目 arXiv:2606.27548（2026）投稿日期 2026-06，距评审截止仅约 3 个月，正文 §1.2/§2.3/§3.2 多处以"选择定则框架"定性引用，缺乏"待正式发表后核实 PBE/PBE+U/HSE 离散度"的明确边界声明｜在 §2.6 增加"待 [15] 正式发表后核实对称性判据在六光子过程的边界条件"等限定；action: rewrite
- [low]｜references.md L3 [1] Baltz｜该综述被正文 0 次引用，仅作为背景阅读保留——与 [2] Jungwirth 2016 论题完全重叠｜已在 [high] 问题中合并处理（撤换 [2]）；action: rewrite
- [low]｜references.md L79 [39] Sato｜CrossRef 核实 vol 11 issue 1，但正文 §3.2 引用 [39] 关于"交换关联势选取准则"，而 Sato 综述重点在阿秒物理整体框架，非专门讨论 TDDFT 泛函选择——相关性弱｜核实 Sato 综述是否含明确泛函选取章节；若是则保留，若否则替换为 Marques CA et al. 的 TDDFT 综述；action: research

## 对抗结论

- 本轮发现 7 个问题（critical:1, high:2, medium:2, low:2）。
- 与 R1 关系：R1 标记的 3 条幽灵 arXiv（2605.20067/2606.31573/2608.02393）仍未补；R1 新发现 arXiv:2609.17500 与 arXiv:2504.14821 同样未进入编号体系——预检漏扫 arXiv 字符串问题未修复，致 5 条幽灵引用累积。
- 真实性结论：12 条 DOI + 4 条新增 arXiv ID 经 CrossRef/arXiv API 逐条核实，五件套与公开记录一致；29 条未检索条目经元数据比对后风险退坡；R1 中"6 条凭记忆条目经 CrossRef 核查为虚构/错位"的教训在本课题不成立。
- 数量时效：40 条达上限 30-40；近 3 年 19/40 = 47.5%（达标但较 R1 的 72% 退步 24.5 个百分点，主因大量 2025-2026 新发表文献含于未引用 [1][2] 与早期条目）；预印本 10/40 = 25%（达 ≤30% 阈值）。
- 是否达到输出标准：否。critical 1 条（5 条幽灵 arXiv 一次性补齐）须当轮修复方可推进；high 2 条为 issue 补齐与综述撤换；medium 2 条为预印本管理。
- 下一轮聚焦：(1) 5 条幽灵 arXiv 一次性纳入 [41]–[45] 并同步替换正文；(2) [33][26][13][14][24][12][16] 条目补 issue 编号；(3) 预印本核心论断加期刊审稿状态标注；(4) [2] 撤换为反铁磁 THz 自旋动力学综述；(5) 预检脚本加"全文 arXiv 字符串 ⊆ references.md"扫描项。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.75
完整性：0.82
综合评分：0.78
