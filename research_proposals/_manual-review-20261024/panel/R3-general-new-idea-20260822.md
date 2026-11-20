# R3 引用审校 — general-new-idea-20260822（r4）

审校范围：`research_proposals/optimizing/general-new-idea-20260822/04_proposal/sections/` 下 `rationale.md`（立项依据）、`content.md`（研究内容）、`scheme.md`（研究方案）、`references.md`（参考文献），并纳入 `full_review.md`（整篇一致性审查）中的引用对账。
审校日期：2026-10-29。对账脚本：/tmp/panel-r4-citation-audit.py（复跑复核）+ 人工盲区排查。
refs 36 条。审校视角：期刊文献编辑（R3），只管引用真实准确、编号自洽、覆盖充分；科学正确性归 R1、语言归 R2。
**特别注意**：该课题正文近期经用户手动修订，参考文献表随之变动，本报告一律按当前实物对账。

---

## 一、编号对账（五项）

| 项 | 计数 | 明细 |
|---|---|---|
| 1. 占位符 | **0** | 正文三章 + full_review + references 全域无 `[TODO]`/`[待补]`/`[XX]`/`[]` 类未填编号 |
| 2. 死条目 | **0** | 见下方脚本盲区说明：`[3-5,22]` 混合形态覆盖 [4][5][22]，全域 36/36 实引 |
| 3. 超界 | **0** | 正文最大引用号 = 36 = refs 最大条目号 36，无越界 |
| 4. 一号两用 | **0** | refs 编号 1–36 严格升序、连续、无重号；每编号仅 1 个条目行 |
| 5. 断链 | **0** | 正文引用号集合 ⊆ refs 条目号集合，无"正文用了 refs 里没有"的编号 |

**⚠ 脚本盲区重要说明（本轮复核核心发现）**：复跑对账脚本输出"死条目 [4][5][22]、正文全域 distinct 33 / refs 36"，**与任务预跑结论（36/36 全被引）不符——经人工排查，脚本结论是假阳性**，根因是脚本正则仅支持两元素形态，不识别以下两处多元素引用：

- `rationale.md` L41：`理论基础为带间-带内双通道干涉的精细图像[3-5,22]。`——"区间+并列"混合形态，一次覆盖 [3][4][5][22] 四个编号；
- `content.md` L45 与 L79：`区别于既有交变磁 HHG 选择规则框架[16,17,18,20]。`——四元并列形态，覆盖 [16][17][18][20]（该四编号亦在 scheme L19/L41/L117 等处单独实引，无死条目风险）。

人工合并后：**正文全域 distinct 36 = refs 36，36/36 全被引，五项全 PASS——预跑"36/36 全被引"的结论经人工复核确认准确**；复跑脚本的"死条目"输出系工具正则局限，非实物缺陷。建议主代理后续升级对账脚本正则以支持 `[a-b,c]` 与多元素并列形态（供 M1 知悉，非正文必改项）。

补充口径（超出五项）：

- **分文件覆盖**：rationale 31 token / 27 distinct（缺 [3,4,5,16,20,22,34,35,36]，其中 [3,4,5,22] 由 L41 混合形态覆盖、[16,20] 在 scheme/content 实引）；content 7 token / 4 distinct（含 [16,17,18,20] 并列形态）；scheme 23 token / 13 distinct；full_review 1 token（L31 表格"文献 [13] 实测 307 K"）。全域合并 36/36。
- **full_review 口径**：full_review 尾表声明"文献编号｜全文唯一连续编号（1–36）"三处一致，与实物（36 条连续无跳号）相符，**尾注自证属实**。
- **上轮遗留核验（四项全部通过）**：
  ① **[27] 死条目已删、重排正确**：当前 refs 恰 36 条、编号 1–36 连续无缺号无重号，[26] Liu（PRL 手性磁子）与 [28] Jaeschke-Ubiergo（Atomic Altermagnetism）衔接自然，无重排残迹；
  ② **密勒指数去引用化无回退**：rationale L45 与 scheme L45 均为"（即密勒指数 100 与 010）"无方括号；Amin PEEM 语境的"100 nm–10 μm"（rationale L43）与"从 100 nm 涡旋到 10 μm 图案化单畴态"（scheme L77）均为长度量纲、无引用化形态，脚本密勒指数排除逻辑未误伤（占位符/超界计数 0 佐证）；
  ③ **Γ–L 改切文献挂靠到位**：content L45"模型校核沿 Γ–L 切的非高对称动量点等间距采样，对齐 Osumi 等人[13] ARPES 实测切向并避开 k_z=0 节点面"——Γ–L 切向显式挂靠 [13]；rationale L23"该分层归属是反演框架选择 Γ–L 非高对称切向作校核线的直接动因"承接同段 [13-15] 分歧语境（该区间形态脚本可识别）；
  ④ **用户手动修订新增引用重点核对**：Liu RuO₂ [21]、Osumi [13]、Mizuno [18]、Haag [17]、Liu 手性磁子 [26]、Long [8]、Liu 综述 [19]、Dal Din [12]、Usanov [14]、Zeng [15]、Amin [25]、Jaeschke-Ubiergo [28]、Osabutey [36] 全部联网核验（见第二节），元数据与正文声称全部匹配。
- **注释行藏引**：四章逐行复核，无 HTML 注释段、无标题行藏引。

---

## 二、联网核实记录

核实方法：① DOI 条目经 Crossref REST API 逐字段比对期刊名/卷/期/文章号/年份/作者链；② arXiv 条目经 arXiv API 反查标题、作者链、v1/v2 日期、journal_ref（判定 † 状态）；③ 关键数值声称回原文摘要（arXiv abstract / APS 页面 / WebSearch 索引）逐句核对。**禁止凭记忆写元数据**——下表每条均有证据 URL。

**抽样 19 / 36 条**（优先级按任务要求：2024–2026 交变磁新条目、支撑关键判据条目、APS 短式 DOI、† 状态抽验）。**元数据不符数 = 0；虚构文献 0 条；短式 DOI 全部有效；† 状态声明全部属实。**

| 编号 | 期刊/年份 | 核实结果 | 证据 URL |
|---|---|---|---|
| [7] | Nature 2024 | ✓ v626(7999):517-522；Krempaský J; Šmejkal L; D'Souza S 等一致。**DOI 前缀 023 无异常**：2023 年注册、2024-02-14/15 在线/刊出，著录"Nature, 2024, 626: 517-522"正确（正文"节点面四组构型/三组平行 c 轴过 Γ、K + k_z=0"细节出自原文正文，公开摘要方向确认） | https://api.crossref.org/works/10.1038/s41586-023-06907-7 |
| [8] | Nature 2026 | ✓ v656(8129):854-860（2026-08-26/27）；Long M; Weinberger T; Wu Z 等一致；标题"3D bulk-resolved g-wave altermagnetic order parameter in CrSb"与正文"三维体分辨结构"逐字对应（𝒴₄⁻³ 实球谐细节出自原文正文） | https://api.crossref.org/works/10.1038/s41586-026-10902-z |
| [9] | Phys. Rev. Lett. 2024 | ✓ v133(20):206401（2024-11-13）；Ding J; Jiang Z; Chen X 等一致；标题"Large Band Splitting in [g-wave altermagnet CrSb]" | https://api.crossref.org/works/10.1103/PhysRevLett.133.206401 |
| [11] | Nat. Commun. 2025 | ✓ v16:1442（2025-02-07）；Yang G; Li Z; Yang S 等一致；摘要确认"synchrotron-based ARPES 三维 k 空间自旋劈裂测绘" | https://api.crossref.org/works/10.1038/s41467-025-56647-7 |
| [12] | arXiv:2511.01690, 2025 | ✓ Dal Din A, Usanov D A, Šmejkal L 等 12 人链一致（2025-11-03 提交）；**无 journal_ref → "†纯 arXiv 预印本"成立** | https://export.arxiv.org/api/query?id_list=2511.01690 |
| [13] | Phys. Rev. B 2024 | ✓ v109(11):115102（2024-03-01）；Osumi T; Souma S; Aoyama T 等一致。**关键判据三数值逐句核实**（arXiv:2308.10117 摘要）：`splitting reaches 0.8 eV at non-high-symmetry momentum points` ✓、`spin-orbit gap of ~0.3 eV along the GK high-symmetry cut` ✓、`T_N = 307 K` ✓、`photon-energy-tunable ARPES + first-principles` ✓ | https://api.crossref.org/works/10.1103/PhysRevB.109.115102 ；https://arxiv.org/abs/2308.10117 |
| [14] | arXiv:2603.16635, 2026 | ✓ Usanov D A, D'Souza S W, Dal Din A 等一致（v1 2026-03-17 / v2 2026-07-21）；**无 journal_ref → † 成立** | https://export.arxiv.org/api/query?id_list=2603.16635 |
| [15] | arXiv:2511.02447, 2025 | ✓ Zeng M, Liu P, Zhu M-Y 等 13 人链一致（2025-11-04）；**无 journal_ref → † 成立** | https://export.arxiv.org/api/query?id_list=2511.02447 |
| [17] | Phys. Rev. Mater. 2026 | ✓ **短式 DOI `10.1103/ypfs-fy39` 有效**；v10(7):074413（2026-07-22）；Haag L; Weber M; Leckron K; Šmejkal L; Sinova J 一致；摘要确认"For planar d-wave altermagnets…Here, we theoretically analyze the response of the prototypical bulk g-wave altermagnet α-MnTe"（sin(4α) 函数形式出自原文正文，d 波先例 vs g 波分析的对照结构确认） | https://api.crossref.org/works/10.1103/ypfs-fy39 |
| [18] | Phys. Rev. B 2026 | ✓ **短式 DOI `10.1103/1vc6-c7rs` 有效**；v114(20):L200403（2026-10-19）；**单作者 Mizuno K**，著录"Mizuno K."无 et al. 正确；尾注"[18] 现已挂刊版 DOI"属实，† 亦见 arXiv:2606.31573 的双标注合规 | https://api.crossref.org/works/10.1103/1vc6-c7rs |
| [19] | Nano Convergence 2026 | ✓ v13(1):6（2026-02-11）；Liu J; Ma X; Zhang X 等一致（"d 波对应 RuO₂/MnTe₂、g 波对应 MnTe/CrSb"判读模板出自原文正文，方向确认） | https://api.crossref.org/works/10.1186/s40580-026-00536-2 |
| [20] | J. Phys.: Condens. Matter 2026 | ✓ v38:175803（2026-05）；**单作者 Ly O**，著录"Ly O."正确；尾注"†亦见 arXiv:2602.09738"双标注合规 | https://api.crossref.org/works/10.1088/1361-648X/ae6385 |
| [21] | Phys. Rev. B 2025 | ✓ **短式 DOI `10.1103/9gv7-vhxw` 有效**；v112(8):L081105（2025-08-07）；Liu Y; Si M; Zhang G 等一致；**APS 摘要逐句核实**："With the Hubbard U, altermagnetism appears and the Kramers degeneracy is lifted…clover shape"、"the dumbbell-shape anisotropy…likely to be intrinsic, indicating weak altermagnetism in RuO₂"——与正文"无 U 哑铃形 → 引入 U 后四叶草形、谐波各向异性作为交变磁性判据"逐字对应（波型归属歧义另见 R3-04） | https://api.crossref.org/works/10.1103/9gv7-vhxw ；https://journals.aps.org/prb/abstract/10.1103/9gv7-vhxw |
| [25] | Nature 2024 | ✓ v636(8042):348-353（2024-12-12）；Amin O; Dal Din A; Golias E 等一致；摘要确认"纳米尺度成像与操控交变磁性"（PEEM 100 nm–10 μm 畴结构细节出自原文正文） | https://api.crossref.org/works/10.1038/s41586-024-08234-x |
| [26] | Phys. Rev. Lett. 2026 | ✓ **短式 DOI `10.1103/m8lc-f8gk` 有效**；v136(23):236705（2026-06-12）；Liu Z; Kikuchi H; Wei Z; Asai S; Enderle M 一致；标题"Observation of Switchable Chiral Magnons in an Altermagnet"逐字 | https://api.crossref.org/works/10.1103/m8lc-f8gk |
| [28] | arXiv:2503.10797, 2025 | ✓ Jaeschke-Ubiergo R, Bharadwaj V K, Campos W 等一致；**摘要逐句核实原子交变磁分类**："atomic altermagnetism, in MnTe, La₂O₃Mn₂Se₂ and Ba₂CaOsO₆"、"In the A₂O₃M₂Se₂ family…a ferroically ordered d-wave form factor"、"In MnTe…g-wave form factor"——与正文"La₂O₃Mn₂Se₂/A₂O₃M₂Se₂ 家族属 d 波、Ba₂CaOsO₆ 属纯 g 波原子反铁磁体"对应（Ba₂CaOsO₆ 节点面沿 a/b 晶轴细节出自原文正文）；**无 journal_ref → † 成立** | https://export.arxiv.org/api/query?id_list=2503.10797 |
| [32] | Adv. Phys. 2025 | ✓ v74(1-4):1-9；**Crossref 作者链仅 1 人（Ciappina M）**——著录"Ciappina M F, et al."中 et al. 属多余（见 R3-05）；同篇在 key-transient 课题著录为单作者，两课题同篇条目格式不一致 | https://api.crossref.org/works/10.1080/00018732.2025.2598130 |
| [35] | Quantum 2026 | ✓ v10:2055（2026-04-08）；Poteshman A; Yun J; Taminiau T; Galli G 一致；摘要确认"ill-posed inverse problem…trans-dimensional model selection"（与正文"跨维度 MCMC、并行回火"的借鉴定位相符） | https://api.crossref.org/works/10.22331/q-2026-04-08-2055 |
| [36] | arXiv:2404.05671v2, 2025 | ✓ Osabutey G, Richardson R, Page G L 三人链一致；**v1 2024-04-08 / v2 2025-10-31——尾注"[36] arXiv v1 2024 / v2 2025，按 v2 著录年份"逐字属实**；无 journal_ref → † 成立 | https://export.arxiv.org/api/query?id_list=2404.05671 |

**尾注自证核对**：refs 头部声明——①"†纯 arXiv 预印本"编号为 [12][14][15][28][33][36]：实物逐条数恰为该 6 条 ✓（抽验 5 条均无 journal_ref，† 成立）；②"[18][32] 现已挂刊版 DOI"：✓ 两条均挂 DOI 并附"亦见 arXiv"双标注；③"[17][21][26] 为美国物理学会新式 DOI 编规则"：三条短 DOI 全部有效，**但 [18] 的 DOI 10.1103/1vc6-c7rs 同为新式短 DOI 却未列入该句**（仅被"现已挂刊版"句覆盖），见 R3-03；④"[36] v1/v2 按著录"✓。

**Kerr/Voigt 声称溯源（重要）**：rationale L47"时间分辨磁光测量在 MnTe 薄膜中观测到 Kerr 与 Voigt 效应共存……"经 WebSearch 定位，出处为 **arXiv:2605.24320《Ultrafast Magneto-optical Fingerprints of Altermagnetism in MnTe》**，其摘要与正文声称逐字对应（"Kerr effect originates from the intrinsic Berry curvature…Voigt effect arises from an anisotropic permittivity induced by the in-plane Néel order…transient Kerr signal exhibits faster relaxation dynamics than the transient Voigt signal"）。**该文献在本地知识库有页（`knowledge/wiki/papers/2026-2605_24320-*.md`）但本课题 `02_literature/` 检索池无记录**——处置见 R3-02。

---

## 三、正文声称与文献内容匹配性抽查

抽查 7 条（支撑关键判据 + 用户新增引用 + 2024–2026 新条目），**7/7 匹配，未发现"正文说 A、文献做 B"**；1 条存在表述歧义（R3-04）。

| 正文声称（位置） | 文献实际内容 | 结论 |
|---|---|---|
| rationale L23 / scheme L21/L45/L101 / content L15/L45「g 波自旋劈裂综合取值 0.3–0.8 eV，依据 Krempaský [7] 与 Osumi [13] 实测；Osumi 在非高对称动量点 0.8 eV、沿 Γ–K（g 波节点面内）约 0.3 eV SOC 能隙；所用样品为块体单晶解理」 | arXiv:2308.10117 摘要："splitting reaches **0.8 eV at non-high-symmetry momentum points**"、"**spin-orbit gap of ~0.3 eV along the GK high-symmetry cut**"、photon-energy-tunable ARPES on hexagonal MnTe | ✓ 三数值逐句对应（"块体单晶解理"为样品细节，出自原文正文，方向确认） |
| rationale L47 / scheme L9/L33「T_N ≈ 307–310 K：307 K 为 ARPES 实测值，310 K 为设计取整值，样品实测以 SQUID ±2 K 为准」 | Osumi 摘要："high critical temperature (**T_N = 307 K**)"；307/310 双口径在全文三章 + full_review 尾表四处一致 | ✓ |
| rationale L33 / scheme L85「RuO₂ 第一性原理预言[21]：取向依赖谐波产额无 Hubbard U 时呈哑铃形、引入 U 后交变磁序出现并转变为四叶草形，由此提出谐波各向异性作为交变磁性判据」 | APS 摘要："With the Hubbard U, altermagnetism appears…**clover shape**"、"**dumbbell-shape** anisotropy…indicating weak altermagnetism in RuO₂" | ✓ 逐字对应（"g 波节点面参考点"表述歧义另列 R3-04） |
| rationale L31 / scheme L117/L123「Haag 等[17]理论预言块体 g 波交变磁体线偏振脉冲激发下的非平衡自旋密度呈偏振-角度相关响应（sin(4α) 八区交替），区别于平面 d-wave 的 sin(2α)；该结论针对弱光注入非平衡自旋密度、不涉 HHG 频谱」 | PRM 摘要："For planar **d-wave** altermagnets…Here, we theoretically analyze the response of the prototypical bulk **g-wave** altermagnet α-MnTe"；正文对适用边界的自我限定与摘要对照结构一致 | ✓（sin(4α)/sin(2α) 函数形式出自原文正文，方向确认） |
| rationale L19「Krempaský 等[7]在 α-MnTe 中经 SARPES 证实 g 波交变磁序并给出节点面几何构型（三组平行 c 轴过 Γ、K 点 + 一组 k_z=0，共四组）」 | Nature 摘要确认"Altermagnetic lifting of Kramers spin degeneracy"（MnTe 体系）；节点面四组构型细节出自原文正文 | ✓（方向确认） |
| rationale L45 / scheme L45「DFT 部分波展开预言[28]：La₂O₃Mn₂Se₂、A₂O₃M₂Se₂ 家族属 d 波（d_{x²-y²} 型）；Ba₂CaOsO₆ 属纯 g 波原子反铁磁体，节点面沿晶轴 a、b（密勒指数 100 与 010）」 | arXiv:2503.10797 摘要："atomic altermagnetism, in MnTe, La₂O₃Mn₂Se₂ and Ba₂CaOsO₆"、"A₂O₃M₂Se₂ family…d-wave form factor"、"In MnTe…g-wave form factor" | ✓（d 波家族逐字对应；Ba₂CaOsO₆ g 波与节点面晶向出自原文正文） |
| content L63/L69「Usanov 等[14]从 SARPES 反卷积区分基态自旋纹理与光发射诱导极化；Zeng 等[15]指出 α-MnTe 可观测自旋纹理呈 k_z 无关 Rashba 型分布、多畴平均贡献很小——两种结论并存构成竞争解释」 | arXiv:2603.16635 标题"Discerning ground state and photoemission-induced spin textures in altermagnetic α-MnTe" ✓；arXiv:2511.02447 标题"Non-altermagnetic spin texture in MnTe" ✓（k_z 无关/Rashba 细节出自原文正文） | ✓ |

---

## 四、引用覆盖充分性评估

- **被引最多的条目**：[13] Osumi（全文约 13 次：rationale ×2、content ×3、scheme ×7、full_review ×1）——作为主锚点条目承担"劈裂取值 + T_N + Γ–K SOC 能隙 + Γ–L 校核切向"四重判据，被引密度与角色匹配；[3] Liu MoS₂（scheme 复现基准，×4）、[7] Krempaský（×4）、[18] Mizuno（×4）。
- **关键判据的引用支撑**：劈裂 0.3–0.8 eV（[7][13]）、T_N 307–310 K（[13] + SQUID 自测）、Γ–K 0.3 eV（[13]）、Rashba 竞争解释（[15][14]）、RuO₂ 各向异性判据（[21]）、g/d 波判读模板（[19]）、畴结构对照（[25]）、MCMC 方法（[34][35][36]）均有条目支撑。
- **⚠ 覆盖缺口（本轮唯一实质发现，rationale §4 研究现状段两处具体实验结果零编号引用）**：
  ① rationale L47 第二段"飞秒激光诱导的协同电荷-晶格-自旋相变实验中，时间分辨反射率与双折射显示自旋序瞬态熔化伴随声子非线性与能带隙加速收缩……"——整段具体实验结果描述无引用。**检索池内有逐字对应条目**：`02_literature/targeted-research/lit-gap-1792460814.md` L18 记录 arXiv:2509.11722（Lu Tiangao 等 2025，"Ultrafast cooperative electronic, structural, and magnetic switching in an altermagnet"，相关度 0.92，池内摘要与正文描述逐句对应）→ 允许接入（R3-01）；
  ② rationale L47 第一段"时间分辨磁光测量在 MnTe 薄膜中观测到 Kerr 与 Voigt 效应共存……二者弛豫时间不同"——整段无引用。溯源结果为 arXiv:2605.24320（摘要逐字对应），**但该文献仅在本 地知识库有页、`02_literature/` 池内无记录**——按"新增引用建议必须池内可查、池外不得建议写入"纪律，不得直接建议写入（R3-02）。
  §4 节为"国内外研究现状"，现状段描述具体实验结果而不带引用，评审无法溯源，属实质性引用缺口（medium）。
- **无引用支撑但处理得当的论断**：d(3ℏω)/dλ ≈ 0.41 eV/μm（换算推导值）、H_SF ~ 10² T 交换场估算、MoS₂ 畴尺寸"块体尚无直接文献需预研实测"（scheme L77 显式声明）、产额缩放"尚无直接文献，将以预研实测标定"（scheme L59）——均为显式自我声明的设计值/待实测项，不属漏引。
- **检索截止声明**：full_review 尾表声明"正文以'据现有文献'式表述，不写检索时间戳"，与实物相符（三章及 refs 尾注均无检索截止时间戳）——声明与实物一致，无口径矛盾。收录最新条目 [18]（2026-10-19 刊出）与该声明兼容。
- **密度判断**：正文 62 次编号引用 / 36 条 refs，密度合理；条目集中在 2024–2026 交变磁文献与 HHG 理论两簇，与"实验空白 + 理论起步"的立项定位一致——**除 L47 两处现状段漏引外覆盖充分**。

---

## 五、意见清单

| 编号 | severity | 模块 | 位置 | 问题 | 原文摘录 | 修改建议 |
|---|---|---|---|---|---|---|
| R3-01 | medium | 立项依据 | rationale L47（§4 第二段） | 研究现状段具体实验结果零引用：飞秒相变实验整段描述无编号，评审无法溯源；**对应文献在检索池内有逐字记录，允许接入** | `飞秒激光诱导的协同电荷-晶格-自旋相变实验中，时间分辨反射率与双折射显示自旋序瞬态熔化伴随声子非线性与能带隙加速收缩，是强磁关联与自旋-电荷耦合驱动的超快开关过程。` | 接入池内条目 arXiv:2509.11722（Lu T, Wu A, Li J, et al. Ultrafast cooperative electronic, structural, and magnetic switching in an altermagnet. arXiv:2509.11722, 2025，†纯 arXiv 预印本）：在该句末标注引用并按 refs 现行格式在 [36] 后追加为 [37]；池内证据：`02_literature/targeted-research/lit-gap-1792460814.md` L18（相关度 0.92，摘要与正文描述逐句对应）。注意新增编号后 full_review 尾表"全文唯一连续编号（1–36）"三处需同步改为 1–37。 |
| R3-02 | medium | 立项依据 | rationale L47（§4 第一段） | 研究现状段具体实验结果零引用：Kerr/Voigt 双重性整段描述无编号；溯源文献（arXiv:2605.24320，摘要与正文逐字对应）**在本地知识库有页但 02_literature 检索池无记录**，按池纪律不得直接建议写入 | `时间分辨磁光测量在 MnTe 薄膜中观测到 Kerr 与 Voigt 效应共存：前者源自交变磁动量空间 Berry 曲率，后者源自实空间 Néel 序各向异性介电性，二者弛豫时间不同，由此构成交变磁双重性的超快指纹。` | 交 M1 裁决，二选一：①先经检索流程将该文献（arXiv:2605.24320《Ultrafast Magneto-optical Fingerprints of Altermagnetism in MnTe》，本地 KB 页 `knowledge/wiki/papers/2026-2605_24320-*.md` 已存在）补入 02_literature 池后再按 R3-01 同款流程接入正文与 refs；②若不入池，将该段改写为弱化表述（如"近期时间分辨磁光研究提示交变磁双重性可能形成超快指纹"），去除具体实验结论的确定性口吻。**不建议直接写入池外条目。** |
| R3-03 | medium | 参考文献 | refs 尾注（references.md L3） | 尾注自证不完整：声明"[17][21][26] 为美国物理学会 2024 年起启用的新式 DOI 编规则"，但 [18] 的 DOI `10.1103/1vc6-c7rs` 同为新式短 DOI（经 Crossref 验证有效）未列入该句，仅被前句"[18][32] 现已挂刊版 DOI"部分覆盖，读者无从得知 [18] 的 DOI 亦属不与长式互换的新式规则 | `[17][21][26] 为美国物理学会 2024 年起启用的新式 DOI 编规则，其编号不与早期长式 DOI 互换，条目按出版社原始记录著录。` | 改为 `[17][18][21][26] 为美国物理学会…`（[18] 保留原"现已挂刊版 DOI"句，两句不冲突）。 |
| R3-04 | low | 立项依据 | rationale L33 | 波型归属表述歧义："RuO₂ 的第一性原理计算预言[21]给出了 g 波节点面谐波定量映射方向的定量参考点"——RuO₂ 属 d 波体系（本课题 refs [19] 综述自分"d 波对应 RuO₂"，Liu 2025 原文亦不涉 g 波节点面），该句易被读作"RuO₂ 具有 g 波节点面"；scheme L85"其与目标体系 MnTe 的 g 波对称性互补"表述正确 | `RuO₂ 的第一性原理计算预言[21]给出了 g 波节点面谐波定量映射方向的定量参考点：取向依赖的谐波产额在无 Hubbard U 时呈哑铃形……` | 改为"RuO₂（d 波体系）的第一性原理计算预言[21]给出了走向谐波各向异性定量映射的参考点：……"，与 scheme L85 的"互补"表述及 refs [19] 的 d 波分类对齐，消除跨章歧义。 |
| R3-05 | low | 参考文献 | refs 条目 [32]（references.md L67） | 单作者条目误加 "et al."：Crossref 作者链仅 Ciappina M 一人（同篇在 key-transient 课题 refs [5] 著录为单作者无 et al.，两课题同篇条目格式不一致，且违反本表头部"作者超过三人时列前三作者加 et al."规则） | `[32] Ciappina M F, et al. Solid-State High-Order Harmonic Generation: Emerging Frontiers in Ultrafast and Quantum Light Science.` | 删去 "et al."：`[32] Ciappina M F. Solid-State High-Order Harmonic Generation…`。证据：https://api.crossref.org/works/10.1080/00018732.2025.2598130 |

---

## 六、结论

1. **五项对账**：占位符 0 / 死条目 0 / 超界 0 / 一号两用 0 / 断链 0。**36/36 全被引，五项全 PASS**。注意：复跑脚本因不识别 `[3-5,22]`（rationale L41）与 `[16,17,18,20]`（content L45/L79）多元素形态而误报"死条目 [4][5][22]"，**系工具假阳性，预跑"36/36 全被引"结论经人工复核确认准确**；建议主代理升级对账脚本正则（支持区间+并列及多元素并列），供 M1 知悉。
2. **上轮遗留四项全部核销**：[27] 死条目删除后 36 条连续无残迹；密勒指数 (100)(010) 去引用化无回退（脚本排除逻辑验证无误伤）；Γ–L 改切挂靠 [13] 到位；用户手动修订新增的 13 条引用（RuO₂/Osumi/Mizuno/Haag/手性磁子/Long/综述/Dal Din/Usanov/Zeng/Amin/Atomic AM/Osabutey）元数据与正文声称**全部核验匹配**。
3. **元数据真实性**：抽样 19/36 条经 Crossref + arXiv API 联网核实，**虚构文献 0 条、元数据错误 0 条、4 条 APS 短式 DOI 全部有效、† 状态声明逐条属实**（[36] v1/v2 年份声明与 arXiv API 逐字吻合）。
4. **内容匹配性**：抽查 7 条全部匹配——关键判据链（0.8 eV 非高对称点 / Γ–K ~0.3 eV SOC gap / T_N 307 K / 哑铃→四叶草 / d-g 波家族分类）逐句回原文核实通过；1 处波型归属歧义（R3-04）。
5. **意见统计**：critical 0 / high 0 / medium 3 / low 2，合计 **5 条**。
6. **需 M1 裁决的关键项**：R3-02（rationale L47 Kerr/Voigt 段零引用，溯源文献 arXiv:2605.24320 在本地 KB 有页但 02_literature 池无记录——入池后接入 or 弱化表述，二选一）。R3-01（2509.11722 池内有记录可直接接入）连带 full_review 尾表编号声明 1–36 → 1–37 的同步改动。**本报告所有新增引用建议均在池内可查或明确要求先入池，无池纪律风险。**
