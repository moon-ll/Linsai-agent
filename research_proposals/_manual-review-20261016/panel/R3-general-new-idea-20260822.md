# R3 引用审校 — general-new-idea-20260822

- 审校日期：2026-10-18
- 输入：`04_proposal/sections/{rationale.md, content.md, scheme.md, references.md}`（37 条文献）
- 方法：程序化编号对账（含 [a,b]/[a-b] 展开、晶向符号识别）+ 高风险条目联网反查（WebSearch / WebFetch / arXiv API / doi.org 解析）
- 专项：已知缺陷两条——死条目 [27] 与"超界引用 [100]"——均已给出**确定性处理方案**（见意见 R3-01/R3-02）。**重要更正：[100] 不是引用，是晶向密勒指数**，前轮反馈（feedback-5/calibration-2026-10-18）的定性有误。

## 编号对账

| 检查项 | 计数 | 明细 |
|---|---|---|
| 占位符 | 0 | 无（scheme L79 `[1̄100]` 为晶向符号，非引用） |
| 死条目 | 1 | **[27]** Li C et al. "Topological Weyl altermagnetism in CrSb"——文献表收录但正文三个模块零引用（grep sections/*.md 确认） |
| 超界引用 | 1（**误报**） | **[100]** @rationale L53："节点面沿 [100]、[010]"——Ba₂CaOsO₆ g 波节点面的**晶向密勒指数**，非文献引用；references 无 [100] 属正常，无需补条目 |
| 一号两用 | 0 | 无重复编号 |
| 断链（编号空洞） | 0 | [1]–[37] 连续无空洞 |

- 头部声明核对："†纯 arXiv 预印本 [12][14][15][18][29][33][34]" 共 7 条，与实际标注一致（✓）；[20][27][36] 另有"†亦见 arXiv"刊版+预印本双标注。
- 被引次数 TOP：[13]×7、[3]×5、[16]×5、[17]×5、[18]×5、[7]×4。
- 注：`[8-11]`（rationale L53）区间展开为 8/9/10/11 四条，均有效；`[16,17,18,20]`（content §2.5/§2.7）并列形式解析正常。

## 联网核实记录（URL）

| 条目 | 核实结论 | 证据 URL |
|---|---|---|
| [7] Krempaský Nature 626:517-522 | ✓✓ 全核实：Scholar + PSI 官方 + arXiv:2308.10681 确认 Nature 626(7999):517-522 (2024)、DOI 10.1038/s41586-023-06907-7、作者表一致；g-wave MnTe SARPES 主题匹配（"四组节点面"具体构型为数值级细节，摘要未显示） | https://www.psi.ch/de/news/science-features/altermagnetism-proves-its-place-on-the-magnetic-family-tree ；https://arxiv.org/pdf/2308.10681v1.pdf |
| [13] Osumi PRB 109:115102 | ✓✓ 全核实（被引最多 ×7，支撑 0.8 eV 劈裂/0.3 eV SOC 能隙/T_N 关键数值）：arXiv:2308.10117 + 两条独立他引确认卷期页；光子能量可调 ARPES + 强各向异性带劈裂与正文一致。**注意：论文摘要 T_N = 307 K，正文多处写 310 K** | https://arxiv.org/html/2308.10117 ；https://arxiv.org/html/2507.14710v2（他引） |
| [16] Werner PRB 110:235101 | ✓✓ 全核实：RIKEN CEMS 官方列表 + arXiv:2407.07752（Werner/Lysne/Murakami）；**内容精确匹配**——摘要确认"纯交变磁或纯 SOC 体系无圆二色、二者耦合才有"，与 scheme §3 副检验设计（"纯交变磁极限 CD 禁戒，SOC 参与按 [16] 预期非零"）逐句对应 | https://cems.riken.jp/en/projects_paper/page/3?lang=en ；https://arxiv.org/pdf/2407.07752 |
| [17] Haag PRM 10:074413 | ✓✓ 核实：MPI-CPfS 官方出版物列表确认 Phys. Rev. Materials 10(7), 074413, pp.1-10 (2026)，作者 Haag/Weber/Leckron/Šmejkal/Sinova/Schneider 全对；短 DOI 10.1103/ypfs-fy39 未直接解析（APS 短式已被课题1 [32] 证实为真实注册形式，低风险）；sin(4α) 八区交替细节为数值级，摘要未显示 | https://www.cpfs.mpg.de/2002134/publications?year= |
| [21] Liu PRB 112:L081105 | ✓ 部分核实：Exaly 两处引用报告确认 "Anisotropic high harmonic generation as a gauge of altermagnetism in RuO₂, PRB 2025, 112"；Letters 页码 L081105 与短 DOI 10.1103/9gv7-vhxw 未直接解析；哑铃形/四叶草形（Hubbard U 开关）细节摘要级未显示（项目内部已登记待核，维持） | https://exaly.com/paper-pdf/74630843/citation-report.pdf |
| [27] Li C Commun. Phys. 8:311 | ✓✓ **条目真实且元数据全对**（arXiv:2405.14777 journal_ref=Commun. Phys. 8, 311 (2025)、DOI 10.1038/s42005-025-02232-9、15 位作者逐一匹配）——死条目成因是"列而未引"，**非伪造条目**；内容为 CrSb 自旋劈裂达 ~1 eV + Weyl 节点 + 自旋极化 Fermi 弧 | http://export.arxiv.org/api/query?search_query=all:"Topological Weyl altermagnetism in CrSb" |

正文声称—文献内容匹配性抽查：[16] 圆二色选择规则（scheme §3）精确匹配；[13] "光子能量可调 ARPES + 各向异性劈裂"（rationale §2）匹配；[17] "线偏振脉冲激发非平衡自旋密度偏振-角度相关"（rationale §3）与标题级匹配。未发现 misattribution；两处数值级细节（[21] 哑铃/四叶草、[7] 四组节点面构型）维持待核标记。

## 意见清单

[R3-01|critical] 立项依据｜rationale L53｜"[100]"为晶向密勒指数被误判超界引用，勿按前轮建议补条目｜"Ba₂CaOsO₆（双钙钛矿，无局域偶极）属纯 g 波原子反铁磁体，节点面沿 [100]、[010]"｜确定性方案：**去引用化**——改写为"节点面沿晶轴 a、b 方向（即密勒指数 100 与 010）"消除方括号歧义；同时在程序化引用对账工具中加晶向符号白名单（`[hkl]`/`[1̄100]` 形态）；驳回 feedback-5"为 [100] 补充参考文献条目"的错误处置

[R3-02|critical] 参考文献｜references [27]｜死条目：真实文献列而未引，NSFC 规范不允许｜"Li C, Hu M, Li Z, … van den Brink J. Topological Weyl altermagnetism in CrSb. Commun. Phys., 2025, 8: 311"｜确定性方案 A（推荐）：删除 [27]，[28]–[37] 整体前移重编号，正文 10 处同步改（rationale L25/L47/L51/L53/L55、scheme L79/L89/L91 等处 [28]→[27]…[37]→[36]）；方案 B（次选）：在 rationale §4 CrSb 对照句增补实质论述（"CrSb 兼具 ~1 eV 交变磁自旋劈裂与 Weyl 拓扑[27]"）后挂载；禁止为凑引用空挂

[R3-03|medium] 立项依据+研究方案｜rationale L53、scheme §1/§3 多处｜T_N 取值 310 K 与所引 [13] 论文实测 307 K 偏差未说明｜"MnTe 奈尔温度约 310 K""T_N ≈ 310 K（SQUID 独立测定 ±2 K）"｜统一表述为"约 307 K（ARPES 文献 [13] 实测）"或注明 310 K 为设计取整值及其来源，避免反演目标 3 参数之一锚在偏差值上

[R3-04|medium] 参考文献｜references [21]｜RuO₂ 哑铃形/四叶草形机制细节联网摘要级未验证（卷 112 已核实）｜"取向依赖的谐波产额在无 Hubbard U 时呈哑铃形，引入 Hubbard U 后……转变为四叶草形"｜维持项目内部"待核"标记直至核对原文正文/附图；DOI 10.1103/9gv7-vhxw 建议补 doi.org 解析记录

[R3-05|low] 参考文献｜references [17]/[21]｜两条 APS 短式 DOI 未直接解析（格式与已证实真实短式一致）｜"DOI: 10.1103/ypfs-fy39""DOI: 10.1103/9gv7-vhxw"｜条目其余元数据已由官方列表核实，保留；建议核验档案补两条 doi.org 解析截图，解析失败则改标 arXiv 号

[R3-06|low] 立项依据｜rationale L25｜[7] 四组节点面几何构型（三组平行 c 轴过 Γ/K + k_z=0）为数值级细节，摘要未显示｜"三组平行于 c 轴、过 Γ 与 K 点的自旋简并节点面，加一组 k_z=0 节点面，共四组"｜标注待核或引 [7] 原文图/补充材料定位（节点面构型是 g 波指纹论证的几何基础，建议正文级核对一次）

## 结论

编号层两处真缺陷（死条目 [27] + 晶向 [100] 误报）均已有确定性方案；**核心更正：[100] 是晶向符号而非超界引用，前轮"补条目"建议必须驳回**，否则将向文献表塞入无关条目。[27] 为真实文献（元数据全核实）但正文零引用，按方案 A 删除重编号最干净。高风险条目反查 6 条：全核实 3（[7]/[13]/[16]/[27] 中的 4 条元数据级全对）、部分核实 2（[17]/[21] 卷期对、DOI/细节待补证）、T_N 数值偏差 1 处（307 vs 310 K）。未发现 citation_misattribution。
