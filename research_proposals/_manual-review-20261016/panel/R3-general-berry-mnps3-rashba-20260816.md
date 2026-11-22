# R3 引用审校 — general-berry-mnps3-rashba-20260816

- 审校日期：2026-10-17
- 审校范围：04_proposal/sections/{rationale.md, content.md, scheme.md, references.md} + p0-general-berry-mnps3-rashba-20260816.md（11 条 open，其中 critical 2 条均涉引用，已逐条核实现状）
- 方法：程序化编号对账（/tmp 脚本）+ 高风险条目联网反查（含 P0 涉及条目）+ 正文声称匹配性抽查
- 结论速览：43 条文献全部真实存在（核实 8 条零虚构），但 **Mavani 错挂 [24] 三处未修复（P0 critical 残留）**，且 scheme 章存在两处**新错挂**（154 SPG 分类、光驱动滑移先例）；[20][39] 两条仍为零引用死条目，references L5 声明仍与实测不符。

## 编号对账（五项计数 + 明细）

| 项目 | 计数 | 明细 |
|---|---|---|
| 1) 占位符 | 0 | — |
| 2) 死条目（列了未被引） | 2 | **[20] Mavani（PRB 2025 L060401）、[39] Misawa（g-wave 多极观测）**，三章零挂靠——与 P0 #5/#11 记录一致，未修复 |
| 3) 超界（引了不存在编号） | 0 | 正文引用编号均在 1–43 内 |
| 4) 一号两用（同一文献多条目） | 0 | DOI/arXiv 查重无重复；[7]（Wang J，PRL 2024，ML 力场 MD）与 [25]（Wang Y，arXiv 2026，deep learning MD）为不同团队的 h-BN 工作，非重复条目 |
| 5) 正文断链（编号在 references 缺失） | 0 | — |

被引次数 Top：[13] Ghorashi-Rappe 10、[21] Rajpurohit 9、[18] Sheng 8、[5] Wrzos 7、[29] Sahu 7、[41] Yarmohammadi 6、[28] Ul Haque 6。

## P0 清单核实现状（引用相关 4 条）

| P0 条目 | 现状核实 |
|---|---|
| #4 [critical] citation_misattribution（rationale 5 处：Ghorashi=[15]、Ogawa=[18]、Mavani=[24]） | **部分修复**：rationale L35/L119 Ghorashi 已正确挂 [13]✓；L37/L119 Ogawa 压磁已正确挂 [15]✓；content/scheme 同类错挂已消失。**但 Mavani=[24] 仍有 3 处残留**（rationale L15、L31、L71），真身 [20] 零引用 |
| #7 [critical] citation_misattribution（rationale L15/L17/L35/L119：Rani=[28] 等） | **部分修复**：L17 Rani 已正确挂 [24]✓，L35/L119 已改 [13]/[15]✓；L15 的 Mavani=[24] 未修复（见上）。另发现 scheme 两处新错挂（见意见 R3-04/R3-05），疑为修复平移时引入 |
| #2 [high] refs_statement（L5 声明"[11]/[25]/[38] 三章均挂靠"） | **未修复**：实测 [11] 无 scheme 挂靠（仅 rationale/content）、[25] 无 content 挂靠（仅 rationale/scheme）、[38] 无 scheme 挂靠且 rationale L61 以 arXiv 软引用替代编号 |
| #5/#11 [high] orphan_refs（[20][39] 零挂靠） | **未修复**：程序化对账确认两编号三章零出现 |

## 联网核实记录（8 条，含 P0 涉及）

| 条目 | 检索证据 URL | 结论 |
|---|---|---|
| [20] Mavani et al., PRB 112, L060401 (2025) | https://arxiv.org/abs/2503.09877 | ✓ 真实。作者 Mavani/Huang/Samanta/Tsymbal 与条目一致；摘要确认"polar-layer stacking of AFM-ordered bilayers…NRSS…switchable by electric polarization…spin-space group approach"，与正文声称内容完全匹配——错挂的唯一真身；arXiv 页未见 PRB journal-ref，条目已自标"上线前 journals.aps.org 核对" |
| [24] Rani & Juraschek, PRL（accepted 2026） | https://arxiv.org/html/2510.22036v1 及 https://www.jurascheklab.com/publications | ✓ 真实。组页确认"P. Rani and D. M. Juraschek, Nonlinear phononic slidetronics, PRL, Accepted"；摘要确认 h-BN 双层经非线性声子实现极化翻转，与 scheme §3.2 用法（对照通道）匹配 |
| [21] Rajpurohit et al., arXiv:2609.01844 | https://arxiv.org/html/2609.01844v1 | ✓ 真实。摘要确认"coherent phonons can dynamically induce and control NRSS…Γ-point infrared-active phonons lifts the spin degeneracy…residual sublattice-connecting symmetries determine the momentum-space form"，与 swave/d-wave 对称性选择声称一致 |
| [5] Wrzos et al., JPCC 130, 6295 (2026) | https://arxiv.org/html/2511.22209 | ✓ arXiv 版真实，S1/S2 堆叠两类 NRSS 分类与 rationale §1.5 逐点匹配；**JPCC 刊版卷页 130:6295–6303 未能独立核实**（arXiv 页无 journal-ref，条目未列入上线前核验清单） |
| [7] Wang J et al., PRL 133, 126801 (2024) | https://pubmed-d.ncbi.nlm.nih.gov/39373442/ 及 https://pld.nju.edu.cn/ | ✓ 真实。PubMed 摘要确认"laser-pulse deterministic control of sliding polarization in **bilayer hexagonal boron nitride** by first principles and molecular dynamics simulation with machine-learned force fields"，content §2.2"h-BN 模型体系+ps 级翻转时标"声称成立；南京大学一作，rationale 国内归属正确 |
| [25] Wang Y et al., arXiv:2604.27342 | https://arxiv.org/abs/2604.27342 | ✓ 真实。作者 Wang Yinan/Chen Poyen/Mizoguchi Teruyasu；摘要确认"coherent single-domain rigid sliding, completing within **5 ps**"，与 scheme §3.2"5 ps 内完成极化翻转"精确匹配（50 K/300 K/2 ps 温度细节未在摘要核到） |
| [37] Li et al., Nat. Commun. 17, 9507 (2026) | ORCID 0009-0001-0565-3911（期刊条目 DOI 10.1038/s41467-026-77233-5） | ✓ 真实（2026-09-04 见刊）。标题为"…in a layered antiferromagnet"未点名 FePS₃，正文三处断言"FePS₃ 反铁磁绝缘体"未见独立佐证，建议核对原文体系 |
| [42] Ogawa & Hayami, arXiv:2609.04883 | https://arxiv.org/pdf/2609.04883 | ✓ 真实。摘要确认"all 32 nonmagnetic and 122 collinear spin point groups"＝154，与正文"154 个 SPG 分类"匹配——但该声称当前挂在 [15]（压磁文）下，属错挂（见 R3-04） |

## 意见清单

- [R3-01|critical] rationale｜§1.1 L15、§1.2 L31、§1.4 L71（共 3 处）｜Mavani 错挂 [24]，真身 [20]｜"Mavani 等 [24] 基于自旋空间群证明…可由电极化直接翻转"｜三处 [24]→[20] 全链改正；P0 #7 明列此项，为跨轮残留，改后 grep "[24]" 复验仅剩 Rani 句
- [R3-02|critical] scheme｜§3.1 L5｜154 SPG 多极分类错挂 [15]，真身 [42]｜"Ogawa 与 Hayami [15] 给出 154 个 SPG 的活动多极分类后已指出 7 个 PT 破缺 SPG…"｜[15] 是 g-wave 压磁文，154 SPG 分类出自 [42]（联网已核实 32+122=154）；rationale L9/L93 挂 [42] 正确，scheme 该处应同步改 [42]
- [R3-03|critical] scheme｜§3.6 L105｜光驱动滑移先例错挂 [9]，真身 [7]｜"环节一（光场→滑移）的图像与时标已由 Wang 等 [9] 给出：光驱动层间滑移极化翻转的 ps 量级数值验证已建立"｜[9] 是 Regmi CoNb₄Se₈ 交变磁实验，与"光驱动滑移极化翻转数值验证"完全无关；改为 [7]（PubMed 已核实 h-BN+ML 力场 MD）
- [R3-04|high] references｜[20][39]｜死条目零挂靠（P0 #5/#11 未修复）｜"43 条全部与正文 [N] 引用一一对应…每条均在论证链中挂靠至少一处"｜[20] 挂靠点被 R3-01 修复后自然消除；[39] Misawa g-wave 多极观测建议在 rationale §1.2 Reimers 段（L29，与 [43] 相邻）补挂或删条重排
- [R3-05|high] references｜L5 声明｜"三章均挂靠"再被实测证伪（P0 #2 未修复）｜"[11]/[25]/[38]…在三个章节均有正文挂靠"｜[11] 缺 scheme、[25] 缺 content、[38] 缺 scheme；按实测计数改写声明，或补挂（如 [25] 的 5 ps 先例可入 content §2.2）
- [R3-06|medium] rationale｜§1.3 L61｜Mizuno 软引用与编号体系不统一｜"Mizuno（arXiv:2606.31573, 2026）在弱 SOC 极限下建立自旋点群动力学选择规则"｜content/scheme 均用 [38]，rationale 该处改挂 [38] 编号，保持全链一致
- [R3-07|medium] references｜[5]｜刊版卷页未独立核实且未入核验清单｜"J Phys Chem C, 2026, 130: 6295–6303. DOI: 10.1021/acs.jpcc.5c08239"｜arXiv:2511.22209 已核实但无 journal-ref；建议并入 L9"上线前核验条目"清单（当前仅列 [10]/[12]/[20]/[24]）
- [R3-08|medium] rationale/scheme｜§1.3 L51、§3.4 L91｜[37] 体系归属待核｜"Li 等 [37] 在 FePS₃ 反铁磁绝缘体中以双 THz 泵浦…"｜联网仅核到标题"in a layered antiferromagnet"，正文三处点名 FePS₃；核对原文确认体系后保留，若不符改"层状反铁磁体（FePS₃ 家族）"

正面确认（不计意见）：[13]/[15]/[24]/[42] 四条 P0 涉及文献全部真实存在且内容与声称匹配；Ghorashi-Rappe=[13]、Ogawa 压磁=[15]、Rani=[24] 的既有修复在 rationale/content 两章已落实；[21] 的引用边界声明（references L7"限于 u-Δ 参数化交叉校验"）与 rationale §1.5/scheme §3.2 实际用法一致。
