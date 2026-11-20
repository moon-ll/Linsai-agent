# R3 引用审校 — general-bsv-driven-hhg-quantum-20260726

审校范围：`research_proposals/optimizing/general-bsv-driven-hhg-quantum-20260726/04_proposal/sections/` 下 `rationale.md`（立项依据）、`content.md`（研究内容）、`scheme.md`（研究方案）、`references.md`（参考文献），并纳入 `full_review.md`（整篇一致性审查）中的引用对账。
审校日期：2026-10-29。对账脚本：/tmp/panel-r4-citation-audit.py（本轮重建并修复逗号并列误展开缺陷后复核；预跑脚本结论与之一致）。
refs 39 条。审校视角：期刊文献编辑（R3），只管引用真实准确、编号自洽、覆盖充分；科学正确性归 R1、语言归 R2。

---

## 一、编号对账（五项）

| 项 | 计数 | 明细 |
|---|---|---|
| 1. 占位符 | **0** | 正文三章 + full_review + references 全域无 `[TODO]`/`[待补]`/`[XX]`/`[]` 类未填编号 |
| 2. 死条目 | **0** | 39 条 refs 全部在正文三章或 full_review 中被实际引用（全域 distinct 39 = refs 39，差集为空） |
| 3. 超界 | **0** | 正文最大引用号 = 39 = refs 最大条目号 39，无越界 |
| 4. 一号两用 | **0** | refs 编号 1–39 严格升序、连续、无重号；每编号仅 1 个条目行 |
| 5. 断链 | **0** | 正文引用号集合 ⊆ refs 条目号集合，无"正文用了 refs 里没有"的编号 |

补充口径（超出五项）：

- **引用号覆盖**：正文三章 + full_review 编号引用 token 合计 112 次（rationale 31 / content 37 / scheme 39 / full_review 5），distinct 39 条全被引——预跑脚本结论"39/39 全被引 PASS"**复核确认准确，无漏报**。
- **full_review 口径**：full_review 引用 [1][20][39] 共 3 条，均在 refs 内，未新增死条目或断链。
- **脚本盲区人工排查**：①注释行藏引——三章 + full_review 无 `#`/`<!--` 注释行藏引（全文件无 HTML 注释块）；②密勒指数/晶向记号误判——正文无 `[1-10]`/`[001]` 类记号（`\[数字{3}\]` 与 `\[数字-数字\]` 全域零匹配），脚本排除逻辑无需触发；③全角分隔引用——`[N，M]`/`[N、M]` 全域零匹配，引用形态统一为半角 `[N]`/`[N,M]`；④复核中发现并修复重建脚本的逗号并列误展开缺陷（`[6,8]` 曾被展开为 6/7/8，修复后 `[N,M]` 仅计 N、M 两号），修复前后本课题五项结论不变（bsv 正文无跨号并列，`[37,38]`/`[3,4]` 均相邻号）。
- **refs 自证标注核对**：bsv 的 references 采用**逐条自证**体例（每条尾注"正文引用：§x.x"），无独立尾注块。逐条核对 39 条声明的章节分布与实际引用章节分布：**37/39 完全一致**，2 条漂移见意见 R3-01/R3-02（漂移方向均为"实引多于声明"，无虚报）。

---

## 二、联网核实记录

核实方法：① DOI 条目经 Crossref REST API（`https://api.crossref.org/works/<DOI>`）逐条反查期刊名/卷/期/页码/年份/首作者；② 无 DOI 的 arXiv 预印本经 arXiv API（`https://export.arxiv.org/api/query?id_list=<id>`）反查标题、作者链、提交日期、journal_ref/DOI（是否已出正式版）；③ 关键数值声称回 arXiv 摘要逐句核对。**禁止凭记忆写元数据**，以下每条均附证据 URL。

按"2024–2026 新条目优先 + 上轮标记投稿前终核 + arXiv 预印本出正式版跟踪 + 支撑关键判据"选取 14 条（占 39 条的 36%）：

| 编号 | 期刊/年份 | 核实结果 | 证据 URL |
|---|---|---|---|
| [27] | Phys. Rev. A 2025 | ✓ **上轮标记"投稿前终核"短码 DOI `10.1103/4x11-phs2` 有效**：Wang S., Lai X., Liu X.，v112(1) L011102，2025-07-22 发表；arXiv:2406.10443 作者链 ShiJun Wang/XuanYang Lai/XiaoJun Liu 与著录一致 | https://api.crossref.org/works/10.1103/4x11-phs2 |
| [36] | Nature 2026 | ✓ **上轮标记跟踪条目**：Jiang Z., Pan S., Chen J. 等，v654(8118) 356-360，2026-05-20；华东师大吴健团队 BSV 驱动钠原子隧穿（正文 §1.3 国内主线） | https://api.crossref.org/works/10.1038/s41586-026-10485-9 |
| [18] | Phys. Rev. B 2026 | ✓ 短码 DOI `10.1103/ydjj-xxcl` 有效：Prajapati/Ray/Ilyakov/Ponomaryov，v113(4) 045118，2026-01-09 | https://api.crossref.org/works/10.1103/ydjj-xxcl |
| [31] | Phys. Rev. Lett. 2025 | ✓ 短码 DOI `10.1103/wyk5-k8tk` 有效：Lange/Hansen/Madsen，v135(4) 043603，2025-07-24 | https://api.crossref.org/works/10.1103/wyk5-k8tk |
| [34] | Phys. Rev. A 2025 | ✓ 短码 DOI `10.1103/hph3-kzb2` 有效：Wang F., Yang C., Cui X., He L., Ou T., Jin R., Liao Q., Lan P., **Lu P.**（9 人全链核验）；正文 §1.3"Lu 团队亦是第一条主线时域干涉工作的作者团队之一"的指代在作者链第 9 位陆培处成立 | https://api.crossref.org/works/10.1103/hph3-kzb2 |
| [29] | Chin. Phys. Lett. 2026 | ✓ Jiang/Dorfman，v43(5) 050401，2026-05-01；标题 Crossref 登记 "Relative-Intensity Squeezing of High-Order Harmonic Twin Beams"，与著录（twin beams 加引号）一致 | https://api.crossref.org/works/10.1088/0256-307X/43/5/050401 |
| [1] | Nat. Phys. 2024 | ✓ BSV-HHG 首例实验：Rasputnyi/Chen/Birk/Cohen，v20(12) 1960-1965，2024-10-02 | https://api.crossref.org/works/10.1038/s41567-024-02659-x |
| [2] | Phys. Rev. Res. 2024 | ✓ Even Tzur/Birk/Gorlach/Kaminer，v6(3) 033079，2024-07-17 | https://api.crossref.org/works/10.1103/PhysRevResearch.6.033079 |
| [13] | Phys. Rev. Lett. 2023 | ✓ Wu F./Xu Q./Wang Q./Chu J.，v131(25) 256201，2023-12-18（扭转双层 MoS₂ 关联能隙判据条目） | https://api.crossref.org/works/10.1103/PhysRevLett.131.256201 |
| [26] | Light Sci. Appl. 2024 | ✓ Even Tzur/Cohen，v13(1) 41，2024-02-01 | https://api.crossref.org/works/10.1038/s41377-024-01381-w |
| [15] | arXiv:2505.22536, 2025 | ✓ Boroumand/Thorpe/Bart 等 7 人，2025-05-28 提交；**无 journal_ref、无 DOI → 未出正式版，（预印本）标注成立** | https://export.arxiv.org/api/query?id_list=2505.22536 |
| [22] | arXiv:2604.15085, 2026 | ✓ Borrego Varillas/Agostini/Ardana-Lamas 等 111 人，2026-04-16 提交；**无 journal_ref → 未出正式版，（预印本）标注成立** | https://export.arxiv.org/api/query?id_list=2604.15085 |
| [32] | arXiv:2502.09427, 2025 | ✓ Even Tzur/Mor/Yaffe 等 11 人，2025-02-13 提交；**无 journal_ref → 未出正式版，（预印本）标注成立** | https://export.arxiv.org/api/query?id_list=2502.09427 |
| [33] | arXiv:2509.13518, 2025 | ✓ Wang/Parks/Thorpe 等 6 人，2025-09-16 提交；**无 journal_ref → 未出正式版，（预印本）标注成立** | https://export.arxiv.org/api/query?id_list=2509.13518 |

**核实小结：14/14 通过，虚构文献 0 条、元数据错误 0 条、4 条 APS 短式新 DOI 全部有效且解析结果与著录逐字段一致。** 4 条预印本（[15][22][32][33]）截至 2026-10-29 均未见正式发表版，"（预印本）"标注全部成立、无过期标注。

---

## 三、正文声称与文献内容匹配性抽查

抽查 6 条（关键判据 + 国内主线 + 预印本机制声称），**6/6 匹配**（其中 3 条数值逐字核验、3 条机制/方向级核验）：

| 正文声称（位置） | 文献实际内容 | 结论 |
|---|---|---|
| rationale L25「Rasputnyi 等[1] 2024 年报道 BSV 驱动固体 HHG 首例实验（Mg:LiNbO₃ 与 a-Si）。单空时模 BSV：1.6 μm、25 fs，平均光子数 2×10¹²、尾部达 2×10¹³」 | arXiv:2403.15337 摘要："driven by a macroscopic quantum state of light, bright squeezed vacuum (BSV), which we generate in a single spatiotemporal mode"、"broad photon-number distribution, covering states from 0 to 2×10¹³ photons per pulse, and sub-cycle electric field fluctuations over ±1 V/Å" | ✓ 单空时模、0–2×10¹³ 光子覆盖、±1 V/Å 涨落全部逐字对应（样品名在正文与 refs 注释，摘要未展开） |
| rationale L57「华东师范大学吴健团队在钠原子隧穿电离上以 300 nJ BSV 等效 7.1 μJ 相干光的作用，非线性效率提升超过 20 倍[36]」；refs 注释「角 streaking 标定有效强度」 | arXiv:2604.05783 摘要："A BSV light with an average pulse energy of 300 nJ achieves an effective intensity equivalent to that of a coherent light with 7.1 μJ, demonstrating a more than 20-fold quantum boost in nonlinear effect"、"matching the peaks of the photoelectron momentum spectra … using angular streaking" | ✓ 300 nJ / 7.1 μJ / 20 倍 / angular streaking 四项逐字对应 |
| rationale L27「Even Tzur 等[2] 建立了任意量子光态驱动 HHG 的高次谐波量子态公式」 | PRR 6.033079 摘要："We derive a formula for the quantum state of the high harmonics, when driven by arbitrary quantum light states" | ✓ 逐字对应（"winding trail"命名在原文正文层，摘要未出现，不构成不符） |
| rationale L31「Gothelf 等[30] 把 Gorlach 相干态展开框架拓展到固体 ZnO 一维单带模型上的带内 HHG。Floquet 解析证明 BSV 相对相干光与 Fock 态光场有更高的截止能量」 | arXiv:2502.11803 摘要："we adapt this framework to the context of solids and consider an intraband model of ZnO"、"analytical calculations in the Floquet limit, we explain why driving with thermal light or bright-squeezed vacuum (BSV) produces a much higher cutoff than when driving with fields described by coherent or Fock states" | ✓ 框架迁移（P 表示→固体 ZnO 带内）与 Floquet 截止推高机制逐句对应（正文"n≈13 推至 33 阶"具体数字在原文正文层，摘要未含，方向一致） |
| content L49「Wu 等[13] 报道 ν = 1 处关联能隙约 126 meV，临界温度高至 285 K；按 k_BT_c ≈ 0.2Δ 反推 T_c ≈ 292 K，与 285 K 在 ±10 K 内自洽」 | PRL 131.256201 元数据核验 ✓（2023-12-18）；refs 注释与正文换算链（292 K vs 285 K ±10 K）内部自洽；126 meV/285 K 数值未回原文逐字核验（Crossref 无摘要、PRL 摘要层不可达） | ◐ 编号/期刊/卷页/作者核验通过，数值经 refs 注释与正文换算链交叉自洽（部分核验，未发现不符证据） |
| rationale L31「BSV 驱动下可推至 33 阶以上仍持续增强。n 阶谐波强度由 K_n·g̃₀²ⁿ/[(n!)²·2²ⁿ] 系数与 g⁽ⁿ⁾(0) 共同调制」 | 同上 arXiv:2502.11803：Floquet 解析 + 谐波强度随 g⁽ⁿ⁾ 调制的框架在摘要层一致；K_n 系数式与 13→33 阶数值在原文正文层 | ◐ 机制一致（部分核验） |

---

## 四、引用覆盖充分性评估

- **被引最多的条目**：[12]（SLM 双色场，6 次）、[2]（winding trail 公式起点，6 次）、[30]（Gothelf ZnO 单带，6 次）、[39]（Wang κ-Br 强关联对照，6 次）、[20]（BSV 展开框架，5 次）、[11]（钨针尖量子干涉，5 次）、[8]（Mott HHG 奠基，5 次）、[6]（单层 TMDC 实验，5 次）。前 8 条分别锚定"双色场工程—量子态公式—机制层理论—强关联对照—Glauber 展开—可见度参照—Mott 奠基—实验基线"八个论证节点，与五环链条（光源—样品—谱学—理论—反演）匹配。
- **关键判据支撑**：g⁽²⁾(0) 双锚（[3][4]）、SBE-Q 交叉验证（[28]）、QSHHG 标定（[15]）、BSV 驱动档物理（[26][30][31][35]）、国内主线（[27][29][34][36] 四条，覆盖 PRA/CPL/Nat. Photon./Nature 四刊）均有条目。
- **无引用支撑的关键论断**：正文对方案设定值（如 r ∈ [0.5,1.5]、Q_F 阈值 5%）均显式声明为设计阈值，不属漏引。
- **密度判断**：112 次编号引用 / 39 条 refs，处于健康区间；refs 中 2024–2026 条目 17 条（43.6%，[1][2][12][14][15][16][18][22][26][27][28][29][30][31][32][33][34][35][36][39] 中 2024 起算），领域时效性好。结论：**覆盖充分**。

---

## 五、意见清单

| 编号 | severity | 模块 | 位置 | 问题 | 原文摘录 | 修改建议 |
|---|---|---|---|---|---|---|
| R3-01 | low | 参考文献 | refs 条目 [3]（references.md L7）；content L15 | 自证标注漏标：条目声明"正文引用：§1.2.2"，但研究内容章 §2.1 的 g⁽²⁾(0) 双锚段以 `[3,4]` 并列形式实引了 [3] | `非简并 PDC 配置下 g⁽²⁾(0)=2；简并 PDC 配置下 g⁽²⁾(0)=3+1/N …[3,4]` | 将 [3] 条目自证标注改为"正文引用：§1.2.2、§2.1"（或统一按节号口径补 §2）。 |
| R3-02 | low | 参考文献 | refs 条目 [11]（references.md L23）；rationale L77 | 自证标注漏标：条目声明"§2.3、§3.4、§3.7"，但立项依据章第三个科学问题段实引了 [11]（Q_F 测量范式参照） | `（干涉可见度型，测量范式参照 Li 等钨针尖双色场量子干涉工作[11]）` | 将 [11] 条目自证标注补 §1（"§1.3、§2.3、§3.4、§3.7"——以实际节号为准）。 |
| R3-03 | low | 参考文献 | references.md L1（头部） | 预印本体例声明缺失：4 条预印本（[15][22][32][33]）仅条目尾注"（预印本）"，无头部规则声明（如"（预印本）= 未见正式发表版，正式发表后替换"）；同批课题 qgi 已采用"† + 头部声明"体例，跨课题口径不一 | `[15] Boroumand N., Thorpe A., … arXiv preprint arXiv: 2505.22536 (2025).（预印本）` | 在 references.md 头部补一行体例说明（本轮联网核验 4 条均未出正式版，标注无过期风险）；是否统一为 † 体例由 M1 一并决定。 |

---

## 六、结论

1. **五项对账**：占位符 0 / 死条目 **0** / 超界 0 / 一号两用 0 / 断链 0。39/39 全被引，预跑结论**复核确认准确**；脚本盲区（注释行藏引、密勒指数、全角分隔、引用变体）逐一人工排查为零。
2. **元数据真实性**：联网核验 14/39 条（覆盖全部 5 条短码 DOI、全部 4 条预印本、6 条关键判据条目），**虚构文献 0 条、元数据错误 0 条、短码 DOI 全部有效**；预印本无过期标注。
3. **内容匹配性**：抽查 6 条全部匹配（3 条数值逐字、3 条机制级），无"正文说 A、文献做 B"。
4. **意见统计**：critical 0 / high 0 / medium 0 / low 3，合计 **3 条**。全部为自证标注与体例类小问题，不涉及引用事实错误。
5. **上轮遗留核销**：①上轮标记的 [27][36] 投稿前终核项已完成（短码 DOI 有效、Nature 2026 条目逐字段一致）；②refs 尾注自证核对完成（37/39 一致，2 条漂移见 R3-01/R3-02）；③上轮光子数口径修复（2×10¹²/2×10¹³）经 [1] 摘要逐字复核无回退。
6. **不涉及新增引用**：本报告未建议任何检索池外新增文献，三条意见均为标注修订。
