# R3 引用审校 — key-transient-quantum-phase-optical-20260726（r5）

审校范围：`research_proposals/optimizing/key-transient-quantum-phase-optical-20260726/04_proposal/sections/` 下 `rationale.md`（立项依据）、`content.md`（研究内容）、`scheme.md`（研究方案）、`references.md`（参考文献），并纳入 `full_review.md`（整篇一致性审查）中的引用对账。
审校日期：2026-10-29。对账脚本：/tmp/panel-r4-citation-audit.py（复跑复核）+ 人工盲区排查。
refs 41 条。审校视角：期刊文献编辑（R3），只管引用真实准确、编号自洽、覆盖充分；科学正确性归 R1、语言归 R2。

---

## 一、编号对账（五项）

| 项 | 计数 | 明细 |
|---|---|---|
| 1. 占位符 | **0** | 正文三章 + full_review + references 全域无 `[TODO]`/`[待补]`/`[XX]`/`[]` 类未填编号 |
| 2. 死条目 | **0** | 正文三章引用号 distinct 41 / refs 41，差集为空；full_review 零编号引用，不改变结论 |
| 3. 超界 | **0** | 正文最大引用号 = 41 = refs 最大条目号 41，无越界 |
| 4. 一号两用 | **0** | refs 编号 1–41 严格升序、连续、无重号；每编号仅 1 个条目行 |
| 5. 断链 | **0** | 正文引用号集合 ⊆ refs 条目号集合，无"正文用了 refs 里没有"的编号 |

补充口径（超出五项）：

- **分文件覆盖**：rationale 49 token / 40 distinct（缺 [23]）；content 14 token / 10 distinct；scheme 22 token / 14 distinct；全域合并 41/41 —— [23] 在 content §2.2 与 §2.3 两次实引，rationale 侧仅以作者名出现（见意见 R3-01），全域无死条目。**复跑结论与预跑一致：41/41 全被引，五项全 PASS，复核确认预跑准确、无漏报。**
- **full_review 口径**：full_review.md 全文零编号引用；其尾表"参考文献表｜唯一（编号 1-41 连续无跳号）｜正文 [N] 挂点与列表一一对应"为自证声明，与实物（41 条连续、1–41 无跳号、41/41 实引）逐项相符，**尾注自证属实**。
- **格式变体排查**：正文引用形式全部为单个 `[N]`，未见 `[a,b]` 并列、`[a-b]` 区间或"区间+并列"混合形态（对账脚本正则不支持的两类形态在本课题不存在，故脚本无盲区暴露）；无中文逗号/顿号分隔的漏网编号。
- **密勒指数/晶向语境**：本课题正文无 `(100)(010)` 类三字密勒指数语境（材料记号均为 Bi₂Se₃/MoS₂/ΓK 等形式），脚本排除逻辑无需触发，无误伤、无漏判。
- **注释行藏引**：四章正文逐行复核，无 HTML 注释段、无标题行藏引。
- **强度换算链手算复核**（rationale L5–L9）：$I=\tfrac12 c\varepsilon_0 E_0^2$，$E_0=0.1$–$0.5$ V/Å = $1$–$5\times10^9$ V/m → $I\approx1.3\times10^{11}$–$3.3\times10^{12}$ W/cm²，与正文"约 $10^{11}$–$3\times10^{12}$ W/cm²"一致；Bi₂Se₃ 例 $d_{cv}=5$ Å·e × $E_0=0.5$ V/Å → $\hbar\Omega_R=2.5$ eV、$/E_g=0.3$ eV ≈ 8.3，正文"≈8"成立。换算链不依赖外部文献，无引用风险。
- **上轮遗留核验**：①[18]/[21] 错挂修复**无回退**——当前 [18]=Zhao C.（MgO Floquet-HHG，arXiv:2507.03791）、[21]=Zhao Z.（WS₂ 应变模拟，J. Phys. D），rationale L105/L117 与 scheme L187 三处挂点均正确且区分姓氏首字母（rationale L117"Zhao Z. 等[21]"、scheme L187"Zhao C. 等[18]"）；②χ⁽³⁾ 归属修复**无回退**——rationale L64 与 content L59 均保留"石墨烯 Dirac 载流子的 χ⁽³⁾≈10⁻⁹ m²/V²……该值并非本实验体系的拓扑绝缘体实测值"守卫表述。

---

## 二、联网核实记录

核实方法：① DOI 条目经 Crossref REST API（`https://api.crossref.org/works/<DOI>`）逐字段比对期刊名/卷/文章号/年份/作者链；② arXiv 预印本经 arXiv API（`https://export.arxiv.org/api/query?id_list=<id>`）反查标题、作者链、提交日期、journal_ref/DOI（判定是否已出正式版）；③ 关键数值声称回原文摘要（APS 页面/arXiv abstract）逐句核对。**禁止凭记忆写元数据**——下表每条均有证据 URL。

**抽样 22 / 41 条**（2024–2026 新条目、支撑关键判据条目、全部 APS 短式 DOI、以及尾注 † 状态抽验；重点条目全查）。**元数据不符数 = 0；虚构文献 0 条；短式 DOI 全部有效。**

| 编号 | 期刊/年份 | 核实结果 | 证据 URL |
|---|---|---|---|
| [3] | Phys. Rev. B 2024 | ✓ v110(12):125111；Ono A; Okumura S; Imai S; Akagi Y 四人链一致；标题"topological spin textures"与正文标量手性翻转论证对应 | https://api.crossref.org/works/10.1103/PhysRevB.110.125111 |
| [4] | arXiv:2604.15085, 2026 | ✓ "Roadmap on Attosecond Science"；Borrego-Varillas R, Agostini P, Ardana-Lamas F 作者链一致；**无 journal_ref → † 标注成立** | https://export.arxiv.org/api/query?id_list=2604.15085 |
| [5] | Adv. Phys. 2025 | ✓ v74(1-4):1-9；单作者 Ciappina M；Crossref 作者链仅 1 人，著录无 et al. 正确 | https://api.crossref.org/works/10.1080/00018732.2025.2598130 |
| [9] | Light Sci. Appl. 2025 | ✓ v14:337；Di Gaspare A; Ghayeb Zamharir S; Knox C 一致；摘要确认 THz 频段 HHG + 对称性主导 + 拓扑绝缘体范德华超材料 | https://api.crossref.org/works/10.1038/s41377-025-01847-5 |
| [10] | Nat. Commun. 2026 | ✓ v17:7642（2026-06-16）；Li S; Zhou W; Imroz K 等一致；标题"Disentangling…surface and bulk states"与正文"分离体/表面态贡献"对应 | https://api.crossref.org/works/10.1038/s41467-026-74310-7 |
| [12] | arXiv:2606.02238, 2026 | ✓ Faeyrman L, Zhang J, Ivanov M 等六人；**无 journal_ref → † 成立** | https://export.arxiv.org/api/query?id_list=2606.02238 |
| [13] | Nature 2024 | ✓ v626:66-71（2024-02-01）；Uzan-Narovlansky A; Faeyrman L; Brown G 等一致；标题"Observation of interband Berry phase in laser-driven crystals"逐字对应正文相位层定位 | https://api.crossref.org/works/10.1038/s41586-023-06828-5 |
| [14] | Rep. Prog. Phys. 2026 | ✓ v89:047901；Rivera-Dean J; Petrovic L; Lewenstein M; Stammer P 一致 | https://api.crossref.org/works/10.1088/1361-6633/ae5847 |
| [17] | Nat. Phys. 2026 | ✓ v22(10):1607-1614（2026-10 刊出）；摘要确认"圆偏振 1550 nm 飞秒脉冲在单层石墨烯产生 Floquet topological insulator + phase-locked 二次谐波操控"——与 rationale L101 声称（FTI + 锁相 SHG 电流调制 + TDDFT 吻合）逐项对应；刊出晚于正文两处"据 2026-09 检索"novelty 声明，但正文 L101 已自交代"前期以预印本形式报道"，无实质矛盾 | https://api.crossref.org/works/10.1038/s41567-026-03429-7 |
| [18] | arXiv:2507.03791, 2025 | ✓ Cong Zhao, Lucie Jurkovičová, Xiaozhou Zou 前三作者链逐字一致（v2 更新至 2026-06-09）；**无 journal_ref → † 成立** | https://export.arxiv.org/api/query?id_list=2507.03791 |
| [19] | Nat. Phys. 2026 | ✓ v22:1282-1286；Chassot F; Pulkkinen A; Kremer G 一致；摘要确认 SnTe 光致能带反转 Floquet 态 | https://api.crossref.org/works/10.1038/s41567-026-03341-0 |
| [21] | J. Phys. D 2026 | ✓ v59(21):215104；Zhao Z; Zheng Z; Xu Z 等一致；摘要确认"monolayer WS₂ 第一性原理模拟 + 正交阿秒控制 + 量子几何工程"（18.24→26.86 数值在原文正文，正文 L117 已自我声明摘要仅可证定性结论，处理诚实） | https://api.crossref.org/works/10.1088/1361-6463/ae6c35 |
| [23] | Phys. Rev. B 2026 | ✓ **短式 DOI `10.1103/7zjc-4b4r` 有效**；v114(8):084307（2026-08-24）；Lorenzo B; Batista C; Jangjan M; Kim D; Menotti J 五人链一致 | https://api.crossref.org/works/10.1103/7zjc-4b4r |
| [24] | arXiv:2604.07543, 2026 | ✓ Mokhtari S, Jelic V, Purschke D N 等一致；**无 journal_ref → † 成立**（正文 77–500 K 与 15–30 倍液氦外推自称"预印本一维链模型外推"，与 † 状态自洽） | https://export.arxiv.org/api/query?id_list=2604.07543 |
| [25] | Phys. Rev. Lett. 2024 | ✓ v133:156901（2024-10-07）；Hu S; Zhao H; Liu X; Chen Q; Chen D 一致；标题"Phonon-Coupled HHG…Nonadiabatic Electron-Phonon Interactions"与正文"电子-声子耦合与非绝热效应的区分"对应 | https://api.crossref.org/works/10.1103/PhysRevLett.133.156901 |
| [28] | Ultrafast Science 2026 | ✓ v6:0171；Nayak A; Dumergue M; Mukhopadhyay S 一致；摘要确认 SYLOS Compact 束线（ELI-ALPS） | https://api.crossref.org/works/10.34133/ultrafastscience.0171 |
| [30] | J. Phys. Chem. Lett. 2024 | ✓ v15:7254-7264（2024-07-18）；Neufeld O; Tancogne-Dejean N; Rubio A 三人一致 | https://api.crossref.org/works/10.1021/acs.jpclett.4c01383 |
| [31] | arXiv:2602.22578, 2026 | ✓ 单作者 Kai Watanabe；摘要确认"SSH–Hubbard 链 KS–多体 Berry 相位一致性 + U(1) twist"；**无 journal_ref → † 成立** | https://export.arxiv.org/api/query?id_list=2602.22578 |
| [32] | Phys. Rev. B 2026 | ✓ **短式 DOI `10.1103/vcxm-dr2g` 有效**；v114(6):065133；Aich S; Seradjeh B 两人一致 | https://api.crossref.org/works/10.1103/vcxm-dr2g |
| [34] | Phys. Rev. Lett. 2026 | ✓ **短式 DOI `10.1103/lwpl-brrr` 有效**；v137(10):106903（2026-09-04）；单作者 Kiselev E；摘要确认"光学声子参量不稳定性 → 反演对称动态破缺 + 强 SHG + 非平衡铁电性"——与 scheme L71 的 Mathieu 共振/稳态破缺表述逐项对应 | https://api.crossref.org/works/10.1103/lwpl-brrr |
| [35] | Mach. Learn.: Sci. Technol. 2026 | ✓ v7:035019；Shah K; Cangi A 两人一致 | https://api.crossref.org/works/10.1088/2632-2153/ae68d4 |
| [38] | APL Photonics 2025 | ✓ v10(8):080803；Csizmadia T; Gulyás Oldal L; Gilicze B 一致；摘要确认"双干涉仪 + 主动延迟稳定 + 超长采集"（±81 as/70 Hz 细节在原文正文，方向确认） | https://api.crossref.org/works/10.1063/5.0273558 |
| [41] | arXiv:2608.02456, 2026 | ✓ Kim D, Oh J, Koh K 等七人一致；**无 journal_ref → † 成立** | https://export.arxiv.org/api/query?id_list=2608.02456 |

**尾注 † 状态核对**：refs 头部声明"预印本 12 条（[4][11][12][18][22][24][26][29][31][36][37][41]），刊版 29 条；预印本见刊后将逐条回录刊版 DOI"。实物逐条数 †：恰为该 12 条，刊版 29 条 ✓。抽验的 6 条预印本（[4][12][18][24][31][41]）arXiv API 均无 journal_ref/DOI，† 标注**全部成立**，无"已出正式版未更新"情况。

**短式 DOI 小结**：本课题 3 条短式新 DOI（[23] 7zjc-4b4r、[32] vcxm-dr2g、[34] lwpl-brrr）经 Crossref 全部有效解析且与著录逐字段一致；refs 头部声明"DOI 保留出版方原始注册形式（含短式或长式，不做调整）"，自证与实物相符。

---

## 三、正文声称与文献内容匹配性抽查

抽查 8 条（被引最多 + 支撑关键判据 + 上轮修复点 + 2026 新条目），**8/8 匹配，未发现"正文说 A、文献做 B"**。

| 正文声称（位置） | 文献实际内容 | 结论 |
|---|---|---|
| rationale L24–26「Ono 等[3]人为翻转标量手性 $S_i\cdot(S_j\times S_k)$ 符号……仅翻转 Berry 曲率符号分布而不改变能带色散；纵向响应可观测量级调制、横向不变；其本身是数值预言」 | PRB 110:125111 标题/摘要方向"HHG from electrons moving in topological spin textures"；正文对"数值预言、纵/横比未经实验确认"已作显式自我声明 | ✓（含诚实边界声明） |
| rationale L101「Lesko 等[17]用圆偏振基频光在石墨烯产生 FTI 态，以锁相二次谐波场操控电子，观测 SHG 手性翻转引起的电流调制，无自由参数 TDDFT 吻合」 | Crossref 摘要："circularly polarized femtosecond laser pulses at 1,550 nm on monolayer graphene, we generate a Floquet topological insulator. With a phase-locked sec[ond harmonic]…" | ✓ 逐项对应（1550 nm/圆偏振/FTI/锁相 SHG） |
| rationale L107 / scheme L71「Kiselev[34]：光学声子经参量不稳定性进入稳态、动态破坏反演对称、产生强 SHG 与铁电整流」 | PRL 137:106903 摘要："inversion symmetry can be dynamically broken by optical phonons…parametric instability…steady state with inversion symmetry breaking phonon trajectories and strong second harmonic generation" | ✓ 机制链逐项对应 |
| rationale L64 / content L59「Di Gaspare 等[9]在 (InₓBi₁₋ₓ)₂Se₃/Bi₂Se₃ 超材料区分体态（仅奇次）与拓扑表面态（奇偶并存）贡献；原文另以石墨烯 χ⁽³⁾~10⁻⁹ m²/V² 作对比参照、并非 TI 实测值」 | Light Sci. Appl. 14:337 摘要确认 THz HHG + 对称性主导 + TI 超材料；χ⁽³⁾ 归属石墨烯的守卫表述两处保留（上轮修复项） | ✓（上轮修复无回退） |
| rationale L105/L117、scheme L187「†Zhao 等[18]（MgO，Floquet-Bloch 边带、非绝热弧形特征 F>1）」与「Zhao Z. 等[21]（WS₂，+2% 应变 Berry 曲率积分 18.24→26.86、垂直偏振分量近翻倍）」 | [18] arXiv:2507.03791 = Cong Zhao（MgO Floquet-engineering HHG）；[21] J. Phys. D = Zhao Z（WS₂ 正交阿秒控制）——两位 Zhao 挂点正确、姓氏首字母区分，上轮错挂修复无回退；[21] 数值细节正文已自我声明"取自原文正文、摘要可证定性结论" | ✓（上轮修复无回退） |
| rationale L238「Watanabe[31]从 SSH-Hubbard 链多体严格解证明 KS 与多体 Berry 相位在反转对称保护的 Z₂ SPT 相数值精度内一致」 | arXiv:2602.22578 摘要："when a density-matching Kohn–Sham (KS) description can reproduce a many-body Berry phase…SSH–Hubbard chain on a ring" | ✓ |
| rationale L236「Neufeld 等[30]2024 沿雅各布天梯对 LDA/GGA/meta-GGA/杂化泛函在强场-物质相互作用下基准比较；GGA 表现最优、meta-GGA 与杂化可现非物理结果」 | JPCL 15:7254-7264 标题"Benchmarking Functionals for Strong-Field Light-Matter Interactions in Adiabatic TDDFT"；Neufeld 三人链一致（泛函排序细节出自正文，方向确认） | ✓ |
| scheme L165/L244「Csizmadia 等[38]于 2025 年在 ELI-ALPS HR 束线实现 ±81 as 数天长期稳定，XUV–IR 非共线 Mach-Zehnder 双干涉仪、PID 70 Hz」 | APL Photonics 10:080803 摘要确认"double interferometer…active delay stabilization…ultralong acquisitions"（±81 as/70 Hz 数值在原文正文，方向与装置架构确认） | ✓ |

---

## 四、引用覆盖充分性评估

- **被引最多的条目**：[12] Faeyrman（全文约 7 次：rationale ×4、content ×2、scheme ×1，承担"相位层读出边界"主线对照）、[18] Zhao C.（×5，Floquet 非微扰写入）、[13] Uzan-Narovlansky（×4，相位层实验锚点）、[7] Baykusheva（×3，圆偏振解析框架）、[15] Rudner-Lindner（×3）。前 10 条承担"可定义性判据—Floquet 工程—相位层对照—装置可行性"四条主线，引用结构与论证链匹配。
- **关键判据的引用支撑**：标量手性可观测调制（[3]）、对称性混杂不可分（[11]）、相位层/不变量层分界（[13][12][31]）、泛函基准（[30]）、声子退相干约束（[24][25]）、装置先例（[38][28]）、α-T₃ 解析基准（[40]）均有对应条目。
- **无引用支撑的关键论断的处理**：Bi₂Se₃ 预研 SNR ≈ 105（rationale L275–279）已显式声明"未在公开期刊以独立题录发表，故不援引 DOI"；WS₂ 应变数值已声明"摘要可证定性结论"；MoS₂ 双层带隙 1.6 eV 等材料参数为标定任务（子课题 A 第 1 年核定）——均处理得当，不属漏引。
- **检索截止/新颖性声明 vs 收录时间**：本课题 refs 尾注无"检索截止于 X 年 X 月"总声明（仅 rationale L113/L175 两处 novelty 声明"据 2026-09 检索"）。唯一晚于该线的条目 [17]（Nat. Phys. 22(10)，2026-10 刊出）已由正文"前期以预印本形式报道"表述兼容，无口径矛盾。距评审日（2026-10-29）novelty 检索已 40+ 天，建议下一轮修订时刷新，属流程提示非引用错误（不单列意见）。
- **密度判断**：正文 85 次编号引用 / 41 条 refs；refs 略高于常规 20–40 条，但尾注已给出六类不可替代支撑的分类理由，且 41/41 全实引、无同质冗余——**覆盖充分，条目数合理**。

---

## 五、意见清单

| 编号 | severity | 模块 | 位置 | 问题 | 原文摘录 | 修改建议 |
|---|---|---|---|---|---|---|
| R3-01 | low | 立项依据 | rationale L137 | 首次出现的关键文献仅以作者名出现未带编号：Lorenzo（对应 [23]）在"四组证据共同支撑"段论证 Berry 曲率可分辨指纹时无编号，读者需到 content §2.2（L47/L61 已引 [23]）自行配对 | `Lorenzo 等在 Haldane/Kane-Mele/Kagome 模型上证明 Berry 曲率在低阶与高阶拓扑绝缘体中具有可分辨的指纹特征。` | 补编号：`Lorenzo 等[23]在 Haldane/Kane-Mele/Kagome 模型上证明…`。该条目已在池内（refs [23]，PRB 2026 短 DOI 已核验有效），属既有条目补编号，无池纪律风险。 |

---

## 六、结论

1. **五项对账**：占位符 0 / 死条目 0 / 超界 0 / 一号两用 0 / 断链 0。**41/41 全被引，五项全 PASS，复核确认预跑脚本结论准确、无漏报**；full_review 零编号引用，尾注"编号 1-41 连续无跳号、正文挂点与列表一一对应"的自证声明与实物逐项相符。
2. **元数据真实性**：抽样 22/41 条经 Crossref + arXiv API 联网核实（覆盖 2024–2026 全部关键新条目、3 条 APS 短式新 DOI、6 条 † 预印本状态、上轮全部修复点），**虚构文献 0 条、元数据错误 0 条、短式 DOI 全部有效、† 标注全部成立**（无"预印本已出正式版未更新"情况）。
3. **内容匹配性**：抽查 8 条全部匹配；上轮遗留两项修复（[18]/[21] 错挂、χ⁽³⁾ 归属）**均无回退**；换算链（0.1–0.5 V/Å → 10¹¹–3×10¹² W/cm²、ℏΩ_R=2.5 eV、ℏΩ_R/E_g≈8）手算复核通过。
4. **意见统计**：critical 0 / high 0 / medium 0 / low 1，合计 **1 条**。
5. **无需 M1 裁决项**；R3-01 为零风险补编号。本轮 R3 无新增引用建议（无池纪律风险），课题引用体系经五轮优化后已收敛。
