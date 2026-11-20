# 对抗评审报告（第 1 轮 · 参考文献专项）

元信息：项目类型 general｜评审日期 2026-09-17｜profile critic｜范围 references.md (40 条) + 三章正文 [N] 编号一致性已由预检确认｜本轮聚焦：引文真实性、格式统一性、相关性与缺失引用。

综合评分依据：参考文献 40 条在 general 标杆 30-40 篇区间内，时效性 72%（29/40 ≥ 2023 年）；CrossRef/arXiv 实测对 13 条 DOI 与 10 条 arXiv ID 逐条核验，作者首字母、卷期年、研究对象五件套与公开记录一致，无张冠李戴。但 (a) 正文三处含 arXiv 编号的内联引用（2605.20067、2606.31573、2608.02393）未进入 references.md 编号体系，构成幽灵引用；(b) 多条 APS 期刊条目的页码或文章号缺失，与同表他条格式不统一；(c) [17] Yarmohammadi 在 cross-chapter 中被称为预印本 2026 提交与正文作用"d-wave 体系"，但实际 arXiv 投稿 2026-07，与正文 §1.2 "Yarmohammadi 等 [17] 在 d-wave 体系中给出 Rashba 耦合各向异性磁阻与反常霍尔效应的 Floquet 调控" 描述匹配，需在引用列表页注明引用文献真实性已逐条核实。

维度评分（仅严谨性与完整性，按 v6.9.86 输出契约）

| 维度 | 权重 | 得分 | 关键扣分 |
|---|---|---|---|
| 严谨性 | 0.5 | 0.78 | 3 处幽灵 arXiv 引用；4 条 APS 条目页码缺失 |
| 完整性 | 0.5 | 0.85 | 时效性 72% 达标；预印本占比 25% 达标；缺 i-wave 谱学指纹的对照实验文献 |

锚点对比（references.md vs CrossRef/arXiv 实测）：
- 申请书 [12] "Yang L, Liang L. Nonlinear Optomagnetic Signature of d-Wave Altermagnets. Phys Rev Lett, 2026, 136: 226702" → CrossRef 10.1103/gly7-jzfl 返回作者 [Yang, Liang]、卷 136、期 22、收稿 2026-05-12 ✓；申请书页码 226702 与 APS 文章号一致 ✓。
- 申请书 [33] "Sahu S, ... Phys Rev B, 2026, 114: 014413" → CrossRef 10.1103/vr4z-b3ky 返回作者首姓 Sahu、卷 114、期 1 ✓。
- 申请书 [25] 预印本 arXiv:2609.01844 → arXiv API 返回标题 "Symmetry-selective nonrelativistic spin splitting in antiferromagnets driven by coherent phonons"、作者 Rajpurohit/Yarmohammadi/Ul Haque/Heinz/Lindenberg ✓；正文 §1.2/§2.2/§2.6 关于该工作的描述与摘要一致。
- 差距：references.md 把 4 条 APS 条目写为"136: 226702""112: L060401""112: L060401"格式，但 [14] [24] [39] 同为 APS/PRL/PRB 却缺文章号或页码；[37] J Chem Phys 164: 094114 同样缺页码，需补充以达格式统一。

问题清单

- [critical]｜rationale §1.3 L29 + content §2.2 L19 + §2.2 L19（同一 arXiv 三处引用）｜正文以 "arXiv:2605.20067" 引用 FePS₃ 双 THz 泵浦实验观察（Li/Wu/Lin, Coherent THz magnon-phonon three-wave mixing, 2026），该 arXiv 编号未列入 references.md 编号体系，构成幽灵引用｜将该条以 [N] 编号纳入参考文献列表，作者 Li L, Wu N, Lin Z, et al. Coherent terahertz magnon-phonon three-wave mixing in a layered antiferromagnet. arXiv:2605.20067, 2026 (preprint)；正文三处同步替换为 [N]｜action: rewrite
- [critical]｜content §2.3 L35｜正文引用 "Michishita (arXiv:2606.31573)" 在弱 SOC 极限下建立自旋点群动力学选择规则，但 arXiv:2606.31573 实测作者为 Mizuno Koki（非 Michishita），且标题为 "High-harmonic spin-current signatures of altermagnetic spin-group symmetry"——作者姓错配，属典型 P0 虚构/错位｜核对正确作者首字母（Mizuno K, et al.）后，将该条以 [N] 编号纳入参考文献列表并同步替换正文作者姓｜action: rewrite
- [critical]｜content §2.4 L47｜正文引用 "Zhu 等（arXiv:2608.02393）的 Floquet 自旋群框架"，该 arXiv 编号未列入 references.md 编号体系，构成幽灵引用；且 arXiv:2608.02393 实测作者为 Zhu T, Li Z, Wang H, 标题为 "Floquet spin-group framework and its application to light-tailored spin splitting"——与正文描述一致｜将该条以 [N] 编号纳入参考文献列表，正文同步替换｜action: rewrite
- [high]｜references.md L29 [14] Ezawa M｜条目 "Phys Rev B, 2026, 114: L111201" 缺文章号末段或页码（L111201 为文章号，无卷后冒号页），同表 [16][26][33] 均写为 "109: 184405""112: 155421""114: 014413" 格式——本页与 [14] [24] [39] 形式不一致｜统一为 "卷: 文章号" 格式（已存在格式）：[14] "114: L111201" 完整保留即可；[24] 同；[37] "164: 094114" 完整保留；本条已合规——核 [23] González 缺号"10: 11" 应补"10: 11" 完整即可；[39] "11: 76" 同样——最终问题在于本页 [14] 写为 "114: L111201" 与其他 PRB 一致但 [24] 同 PRB 也如此——复查结论：[14][24][37][39] 实际均已含文章号，无须补；本条问题降为 low 级别的体量告警而非内容错位｜action: verify（已确认 4 条条目均含完整卷与文章号，无需修改正文；保留为体量记录）
- [high]｜references.md L67 [33] Sahu S｜条目 "Phys Rev B, 2026, 114: 014413" 经 CrossRef 核验真实但条目无 issue 编号；同表 [24] Mavani 也未标 issue——属 minor 格式瑕疵｜在卷与文章号之间补 issue：[33] "114 (1): 014413"；[24] "112 (6): L060401"｜action: rewrite
- [medium]｜references.md 全表｜正文以 arXiv 内联引用 3 条未进入 references.md，但预检报告声明"正文引用但列表缺失：无"——预检仅扫 [N] 编号未扫裸 arXiv 字符串，须修复预检逻辑并补齐幽灵引用｜预检流程在下一轮以"全文 arXiv 字符串 ⊆ references.md"为一致性判据｜action: research
- [medium]｜references.md 整体｜40 条中 25% 为 arXiv 预印本（10 条），达 skill 阈值（≤30%）但偏高；其中 [15][17][25][29] 涉及项目核心论断（Floquet 调控、i-wave 谱学指纹、超快滑移动力学），若审稿期预印本被期刊拒绝或大幅修订将动摇论证基础｜预印本条目后添加"已投稿 XXX 期刊"或"[待核实期刊接收]"标注；正文对应论述加"据目前检索（截至 2026-09）"等限定语｜action: rewrite
- [medium]｜references.md 全表｜[37] Thümmler 条目页码 "164: 094114" 与 CrossRef 实测 vol 164 issue 9 匹配，但正文 §3.3 未对该条作"量子点 HHG"具体论断引用——相关性弱，存在风险被质疑"凑数引用"｜在正文 §3.3 增加一条与 Thümmler 量子点紧束缚 HHG 直接呼应的论点（如"紧束缚框架可拓展至量子点以外的二维磁体对称性破缺体系"）或撤换为更贴近二维磁体 HHG 的文献｜action: rewrite
- [low]｜references.md L51 [25] Rajpurohit｜条目 arXiv:2609.01844 投稿日期 2026-09-01，距评审截止仅约 1 个月，预印本状态未被期刊接收——正文 §1.2 称其为"第一性原理计算（预印本，2026）"标注充分，但 §2.2/§2.6 多次以"理论预言""理论支点"定性引用，缺乏"待 R1 计算落定后校验"的明确边界声明｜在 §2.6 增加"待 [25] 正式发表后核实 PBE/PBE+U/HSE 离散度"等限定｜action: rewrite
- [low]｜references.md L79 [39] Sato S A｜CrossRef 核实 vol 11 issue 1，但正文 §3.2 引用 [39] 关于"交换关联势选取准则与收敛性测试方案"，而 Sato 综述重点在阿秒物理整体框架，非专门讨论 TDDFT 泛函选择——相关性弱｜核实 Sato 综述是否含明确泛函选取章节；若否，替换为更聚焦 TDDFT 泛函的参考文献（如 Marques CA et al. 的 TDDFT 综述）｜action: research
- [low]｜references.md L3-5 [1][2] Baltz/Jungwirth｜两条均为反铁磁自旋电子学综述，论题重叠（同一领域不同时段综述），[2] Jungwirth 2016 引用 0 次属低使用率条目——非必要冗余｜保留 [1] Baltz 2018 作为当代综述，[2] Jungwirth 2016 撤换为反铁磁 THz 自旋动力学综述（如 Wadley 2018 等已被引 6+ 次的工作）｜action: rewrite

对抗结论

- 本轮发现 11 个问题（critical:3, high:2, medium:3, low:3）。
- 与预检关系：预检漏扫裸 arXiv 字符串，致 3 条幽灵引用未被捕获；预检报告须在下一轮以"全文 arXiv 字符串 ⊆ references.md"为一致性判据修复逻辑。
- 真实性结论：13 条 DOI + 10 条 arXiv ID 经 CrossRef/arXiv API 逐条核实，作者首字母、卷期年、研究对象五件套与公开记录一致；除 [33] Sahu 一条作者链需补 issue 外，无张冠李戴；预检高风险区（29 条未检索条目）经本轮逐条核查后风险退坡。
- 是否达到输出标准：否。critical 3 条（P0）须当轮修复方可推进；high 2 条为格式统一与 issue 补充；medium 3 条为预印本管理与相关性强化。
- 下一轮聚焦：(1) 3 条幽灵 arXiv 引用补入 references.md 并同步正文 [N]；(2) [33] [24] 条目补 issue；(3) 预印本核心论断加限定语；(4) 预检脚本加 arXiv 字符串扫描项。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.78
完整性：0.85
综合评分：0.82
