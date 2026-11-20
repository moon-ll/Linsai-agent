# R3 引用审校 — key-transient-quantum-phase-optical-20260726

- 审校日期：2026-10-18
- 输入：`04_proposal/sections/{rationale.md, content.md, scheme.md, references.md}`（41 条文献）
- 方法：程序化编号对账（含 [a,b] 并列与 [a-b] 区间展开、数学区间 `\in [1,2]` 掩蔽）+ 高风险条目联网反查（WebSearch / WebFetch / arXiv API / doi.org 解析）
- 专项：复核 2026-10-11 "[32] 补 body 引用修复"的巩固状态 → **已巩固**（scheme.md §2.1(a) L101 "具体形式见 Aich 等[32]"，且该条经 APS 官方页全核实，见下）

## 编号对账

| 检查项 | 计数 | 明细 |
|---|---|---|
| 占位符 | 0 | 无（scheme L149 `[0.3, 1]` 为数学区间，非引用） |
| 死条目 | 0 | 41 条全部被正文引用（[32] ×1，10-11 修复保持有效） |
| 超界引用 | 0 | 无 |
| 一号两用 | 0 | 无重复编号 |
| 断链（编号空洞） | 0 | [1]–[41] 连续无空洞 |

- 头部声明核对："预印本 12 条（[4][11][12][18][22][24][26][29][31][36][37][41]），刊版 29 条，共 41 条" 与实际条目一致（✓）。
- 被引次数 TOP：[12]×10、[18]×6、[13]×5、[35]×4、[36]×4；[32]×1。
- 编号层完全干净；全部问题集中在**条目元数据与正文—文献内容对应关系**（见意见清单）。

## 联网核实记录（URL）

| 条目 | 核实结论 | 证据 URL |
|---|---|---|
| [3] Ono PRB 2024, 110:125111 | ✓✓ 全核实：作者 Ono/Okumura/Imai/Akagi、DOI 10.1103/PhysRevB.110.125111、内容匹配（标量手性变号→Berry 曲率变号、能带不变、纵向响应调制/横向不变） | http://export.arxiv.org/api/query?search_query=ti:"High harmonic generation from electrons moving in topological spin textures"（arXiv:2405.01351，journal_ref=PRB 110,125111） |
| [5] Ciappina Adv. Phys. 2025, 74:1-9 | △ 综述真实，**刊版元数据存疑**：arXiv 官方 comment 为 "Submitted to Advances in Physics (invited)"（投稿中），与本条"已刊出 74:1-9+DOI"矛盾；T&F DOI 页被反爬拦截无法确认；同库课题2（general-new-idea）截至 2026-08 判定其为纯预印本 | http://export.arxiv.org/api/query?id_list=2510.15207 ；https://doi.org/10.1080/00018732.2025.2598130（拦截） |
| [12] Faeyrman arXiv:2606.02238 | ✓ 存在；摘要确认 MgO + 强 THz 场 + HHG 直接分辨复 Berry 相实部/虚部，与正文（被引 10 次）描述一致 | https://arxiv.org/html/2606.02238v1 |
| [13] Uzan-Narovlansky Nature 626:66-71 | ✓✓ 全核实：Nature Asia 目次页 p.66、DOI 10.1038/s41586-023-06828-5 一致（023 前缀为 2023-12 在线/2024-02 刊出，正常） | https://www.natureasia.com/ja-jp/nature/626/7997 |
| [18] Zhao C. arXiv:2507.03791 | ✓ 论文真实；**内容为 MgO Floquet-Bloch 态 HHG 实验+理论**（宽禁带 MgO + 近红外少周期脉冲），正文 L104/L130/L397 的 MgO 语义正确 | https://arxiv.org/pdf/2507.03791v2 |
| [21] Zhao Z. J. Phys. D 2026, 59:215104 | ✓✓ DOI 10.1088/1361-6463/ae6c35 解析为 "Orthogonal attosecond control…"（Zhenjiang Zhao +5，2026-05-26 刊出）；arXiv:2511.13114 摘要确认**拉伸应变放大垂直偏振谐波、Berry 曲率重塑**——即正文 L116/L134 所引 WS₂ 应变模拟数据的真正出处 | https://discovery.researcher.life/topic/field-anomaly-relaxation/16629083 ；https://export.arxiv.org/pdf/2511.13114 |
| [23] Lorenzo PRB 2026, 114:084307 | △ 论文真实（arXiv:2508.15631，Haldane/Kane-Mele/Kagome、helicity/CD/体-边-角通道与正文 L140 匹配）；**刊版信息无法核实**：arXiv v2（2026-05-24）无 journal_ref/DOI 回标，doi.org/10.1103/7zjc-4b4r 解析失败，WebSearch 两轮无果 | http://export.arxiv.org/api/query?search_query=ti:"High harmonic spectroscopy from lower-order to higher-order topological insulators" |
| [32] Aich & Seradjeh PRB 2026, 114:065133 | ✓✓ **APS 官方页全核实**：标题/作者（Suman Aich, Babak Seradjeh）/卷期页（Vol.114, Iss.6, 065133, Published 27 July 2026）/DOI 10.1103/vcxm-dr2g 全对；摘要确认 mirror-filtered winding numbers + Wilson loop，与 scheme L101 引用语境匹配。附证：APS 新式短 DOI（10.1103/xxxx-xxxx）为真实注册形式 | https://doi.org/10.1103/vcxm-dr2g |
| [34] Kiselev PRL 2026, 137:106903 | ✓ 内容核实：arXiv:2510.12990（2025-10）单作者 Egor I. Kiselev，参数不稳定性+强 SHG 与 scheme L157 描述一致；PRL 刊版页码/DOI（10.1103/lwpl-brrr）未直接解析（格式与已证实 APS 短式一致，低风险） | https://arxiv.org/pdf/2510.12990v1 ；https://scholar.google.com/citations?user=uVgfDLwAAAAJ |

正文声称—文献内容匹配性抽查（[3]/[12]/[13]/[32]/[34] 共 5 处关键判据句）：均与原文摘要级一致，未发现除 [18]/[21] 错挂之外的 misattribution。rationale L22 对 [3] "数值预言、倍数未实验确认"的限定诚实（arXiv 摘要自述 "we numerically investigate"）。

## 意见清单

[R3-01|critical] 立项依据｜rationale L116（§2.2）与 L134（§2.3）｜WS₂ 应变-Berry 曲率模拟数据错挂 [18]，实为 [21] 内容｜"†Zhao 等[18]于 2026 年正式发表的 WS₂ 第一性原理模拟（J. Phys. D, 2026, 59: 215104）"｜两处 [18] 改引 [21]：J. Phys. D 59:215104 属 Zhenjiang Zhao（[21]），[18]=Zhao C. 的 MgO Floquet 实验（arXiv:2507.03791）；删"[18] 正式发表版"表述；L58 处 [21] 引用保持不变

[R3-02|high] 参考文献｜references [5]｜Ciappina 综述刊版元数据与其 arXiv 投稿状态矛盾，无法核实｜"*Adv. Phys.*, 2025, 74: 1-9. DOI: 10.1080/00018732.2025.2598130"｜arXiv:2510.15207 comment 为"Submitted to Adv. Phys. (invited)"且页码 1-9 异常短；降级为预印本条目"arXiv:2510.15207, 2025"，与课题2 [33] 口径统一；或补 T&F 官方页证据后保留刊版

[R3-03|high] 参考文献｜references [23]｜PRB 刊出信息（114:084307+短 DOI）三渠道均无法核实｜"Phys. Rev. B, 2026, 114: 084307. DOI: 10.1103/7zjc-4b4r"｜论文本身真实（arXiv:2508.15631）；在补得 APS 官方页证据前，降级为"arXiv:2508.15631, 2025"预印本条目，正文三处引用语义不受影响

[R3-04|medium] 参考文献｜references [34]｜PRL 137:106903 与 DOI 10.1103/lwpl-brrr 未能直接解析｜"Phys. Rev. Lett., 2026, 137: 106903. DOI: 10.1103/lwpl-brrr"｜内容与作者已核实（arXiv:2510.12990→PRL 时间线合理）；条目保留，建议补 doi.org 解析记录入核验档案，若解析失败按 R3-03 同口径降级

[R3-05|low] 立项依据｜rationale L104/L130 与 scheme L397｜[18] 三处 MgO 语义描述本身正确，勿随 R3-01 误改｜"最接近的 †Zhao 等[18]（MgO Floquet-Bloch 实验）"｜R3-01 修正仅动 L116/L134 两处 WS₂ 数据句；MgO 语境的 [18] 引用保持原样，并统一"†Zhao 等"人名指代（Zhao C. 系与 Zhao Z. 系避免混称）

## 结论

编号层零缺陷（五项全零，[32] 修复巩固）；引用质量的核心风险为**1 处 critical 错挂**（[18]/[21] 张冠李戴，涉及被引 6 次的核心参照条目）与**2 条无法核实的刊版元数据**（[5]/[23]，建议按"无法核实→去刊版化"处理）。高风险条目反查 8 条：全核实 5、内容真实但元数据存疑 2、DOI 未直接解析 1。
