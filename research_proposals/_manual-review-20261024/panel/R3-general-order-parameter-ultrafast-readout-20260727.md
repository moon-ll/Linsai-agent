# R3 引用审校 — general-order-parameter-ultrafast-readout-20260727

审校范围：`research_proposals/optimizing/general-order-parameter-ultrafast-readout-20260727/04_proposal/sections/` 下 `rationale.md`（立项依据）、`content.md`（研究内容）、`scheme.md`（研究方案）、`references.md`（参考文献），并纳入 `full_review.md`（整篇一致性审查）中的引用对账。
审校日期：2026-10-24。对账脚本：/tmp/panel-r4-citation-audit.py（预跑）/tmp/r3-order-audit.py（复核脚本，含 full_review 口径与格式变体排查）
refs 42 条。审校视角：期刊文献编辑（R3），只管引用真实准确、编号自洽、覆盖充分；科学正确性归 R1、语言归 R2。

---

## 一、编号对账（五项）

| 项 | 计数 | 明细 |
|---|---|---|
| 1. 占位符 | **0** | 正文三章 + full_review + references 全域无 `[TODO]`/`[待补]`/`[XX]`/`[]` 类未填编号 |
| 2. 死条目 | **0** | refs 42 条（编号 1–42 连续无跳号）全部在正文三章被引用；最小引用次数为 1（[3][4][6][8][9][10][14][16][17][24][26][27][29][31][34][35][37][38][39][40][41][42]），最大 [1] 共 13 次 |
| 3. 超界 | **0** | 正文最大引用号 = 42 = refs 最大条目号 42，无越界 |
| 4. 一号两用 | **0** | refs 编号 1–42 严格升序、连续、无重号；每编号仅 1 个条目行（条目行号唯一，见明细） |
| 5. 断链 | **0** | 正文引用号集合 ⊆ refs 条目号集合，无"正文用了 refs 里没有"的编号 |

补充口径（超出五项）：

- **引用号覆盖**：正文三章引用号 42 distinct / 97 token（rationale 40、content 20、scheme 37）；refs 42 条 → 差值 0，**与预跑脚本结论一致，复核确认预跑"五项全 0（PASS）"准确**。
- **full_review 口径**：把 `full_review.md` 纳入引用集合后，死条目仍为 0（引用号集合不变，full_review 的 6 个编号 [1][12][22][30][32][33] 均为正文已用编号，无"full_review 独有"编号）。整篇一致性审查未引用任何正文未用条目。
- **格式变体排查**：正文引用形式统一为单个 `[n]`；未见 `[a,b]` 并列式、`[a-b]` 区间式；用正则穷举所有"含数字的非标准方括号"（排除注释行、排除圆括号内三字密勒指数 `(100)` 语境）→ 结果为空集，即无藏引、无漏网编号。密勒指数语境在本课题确实出现（rationale L45「q* = (1/2, 0)」、scheme L31「q* = (1/2, 0)」），预跑脚本的排除逻辑在本课题被实际触发且工作正常。
- **引用密度**：正文 97 次编号引用 / 42 条 refs，比值 2.31；范本为正文 10–20 次、refs 30–40 条。本课题两项均**显著高于范本**（97 次 vs 10–20 次；42 条 vs 30–40 条），但从被引分布看系实质覆盖而非灌水：前 10 条承担了"TiSe₂ 对照双源证据链—交错磁对称性框架—SOC 两极限—CrSb 体态基准—多体混合警示—唯一归因方法学"六条主线，且 42 条中无一条是"挂而不论"的空条目（最低引用次数也为 1，且落点明确）。**密度偏离属本课题体制所致（申请书把参考文献从标准编号制改为"条目 + 【关联】标注 + 分节"体例），非灌水，但需 R1 判断评审是否接受这种偏离范本的密度。**

---

## 二、联网核实记录

核实方法：① 29 条含 DOI 的条目全部经 Crossref REST API（`https://api.crossref.org/works/<DOI>`）按 DOI 逐条反查，逐字段比对期刊名/卷/期/页码或文章号/年份/首作者/作者链；② 全部 38 条带 arXiv 号的条目经 arXiv API（`https://export.arxiv.org/api/query?id_list=<id>`）反查标题、作者链、提交日期、`journal_ref`（是否已出正式版）、`<arxiv:doi>` 字段；③ 关键数值声称回原文（arXiv HTML 全文 / Nature / APS 页面 / PMC）逐句核对；④ 无 DOI 条目另经 OpenAlex 交叉确认。

**元数据逐字段比对结果：29 条含 DOI 条目的期刊名 / 年份 / 卷号 / 页码或文章号 / 首作者五字段全部一致，不符数 = 0。13 条无 DOI 的 arXiv 预印本经 arXiv API 反查，标题与作者链全部一致。虚构文献 0 条。**

| 编号 | 期刊/年份 | 核实结果 | 证据 URL |
|---|---|---|---|
| [1] | Commun. Mater. 2025 | ✓ v6(1) art.152；published 2025-07-18；作者链 11 位一致；摘要确认"below ~200 K 的 2×2×2 公度周期晶格畸变 + CDW 相下各向异性分量"；全文确认 3/5/7 阶谐波、~200 K 相变、H3/H5/H7 温度扫描 | https://api.crossref.org/works/10.1038/s43246-025-00873-5 |
| [2] | Phys. Rev. B 2025 | ✓ v112(8):085147；arXiv API 返 `journal_ref = Phys. Rev. B 112, 085147 (2025)` + `<arxiv:doi>10.1103/812z-nl4m</arxiv:doi>`；摘要确认"现象学平均场模型 + 含时薛定谔方程，复现 3/5/7 阶随偏振角强度分布" | https://api.crossref.org/works/10.1103/812z-nl4m |
| [3] | J. Phys. Chem. C 2026 | ✓ v130(4):1551-1561；arXiv API 返 DOI `10.1021/acs.jpcc.5c05450`；**但 arXiv 摘要与全文方法段显示该文方法为 RT-TDDFT（与 [4] 同法），非"解析理论"**——见意见 R3-04 | https://api.crossref.org/works/10.1021/acs.jpcc.5c05450 |
| [4] | arXiv:2008.07131, 2020 | ✓ Ahmed T, Yoo J, Prasankumar R, Zhu J-X（4 人）；2020-08-17 提交，v2 2020-12-17；**无 journal_ref、无 DOI → 确未见正式发表版，【预印本】标注成立**；摘要确认为实时 TDDFT | https://export.arxiv.org/api/query?id_list=2008.07131 |
| [5] | Phys. Rev. B 2026 | ✓ v113(7):075117；arXiv API 返 DOI `10.1103/bl2s-cv34`（正式版已出，refs 已按正式版著录） | https://api.crossref.org/works/10.1103/bl2s-cv34 |
| [6] | arXiv:2602.11645, 2026 | ✓ Shao T-H, Dai X, Hu W 等 20 人；2026-02-12 提交（v1）；**无 journal_ref、无 DOI → 确未见正式发表版，【预印本】成立**；摘要确认"MBE 在 InP(111) 上生长厘米级 α-MnTe、近零净磁矩下的 Berry 曲率反常霍尔" | https://export.arxiv.org/api/query?id_list=2602.11645 |
| [7] | Phys. Rev. Lett. 2025 | ✓ v134(9):096504；arXiv API 返 journal_ref + DOI；摘要确认 Hubbard 梯多体 HHG | https://api.crossref.org/works/10.1103/PhysRevLett.134.096504 |
| [8] | Phys. Rev. A 2024 | ✓ v109(6):063104；arXiv API 返 journal_ref + DOI；摘要确认"一维固体中强束缚激子的 HHG 谱学"——**该文不涉及激子凝聚**，见意见 R3-06 | https://api.crossref.org/works/10.1103/PhysRevA.109.063104 |
| [9] | PNAS 2024 | ✓ v121(6):e2316775121；published 2024-02-26 | https://api.crossref.org/works/10.1073/pnas.2316775121 |
| [10] | Phys. Rev. B 2019 | ✓ v99(18):184303；arXiv API 返 journal_ref + DOI | https://api.crossref.org/works/10.1103/PhysRevB.99.184303 |
| [11] | Phys. Rev. B 2024 | ✓ v110(23):235101；arXiv API 返 journal_ref + DOI；摘要逐条对应正文："SOC 无关时低阶偶次谐波依赖外磁场"、"SOC 引入高能峰与平台"、"纯交错磁或纯 SOC 无圆二色性，二者同时具备则出现圆二色性"、"自旋流及其高次谐波谱" | https://api.crossref.org/works/10.1103/PhysRevB.110.235101 |
| [12] | Phys. Rev. X 2022 | ✓ v12(3):031042；arXiv 标题为 "Altermagnetism: spin-momentum locked phase protected by non-relativistic symmetries"（正式版标题，preprint 版为旧题名）——著录正确 | https://api.crossref.org/works/10.1103/PhysRevX.12.031042 |
| [13] | Phys. Rev. Lett. 2024 | ✓ v132(23):236701；arXiv API 返 journal_ref + DOI | https://api.crossref.org/works/10.1103/PhysRevLett.132.236701 |
| [14] | J. Phys.: Condens. Matter 2026 | ✓ v38(17):175803；DOI `10.1088/1361-648X/ae6385` 有效；**arXiv API 返 no journal_ref/no DOI，但 Crossref 已有正式版著录**——refs 已按正式版著录，正确 | https://api.crossref.org/works/10.1088/1361-648X/ae6385 |
| [15] | arXiv:2607.13863, 2026 | ✓ Wang C, Wang Y, Meng S（3 人）；2026-07-15 提交；**无 journal_ref、无 DOI → 确未见正式发表版**；摘要确认"B₁g 模选择性破缺 → MnTe 瞬态补偿亚铁磁 + CrSb 可逆铁磁矩" | https://export.arxiv.org/api/query?id_list=2607.13863 |
| [16] | Phys. Rev. Lett. 2026 | ✓ v136(25):256702；短式 DOI `10.1103/nyy3-h8wr` 有效；arXiv API 返 journal_ref + DOI；摘要确认"Kerr（动量空间 Berry 曲率）与 Voigt（实空间各向异性）共存" | https://api.crossref.org/works/10.1103/nyy3-h8wr |
| [17] | Phys. Rev. B 2025 | ✓ DOI `10.1103/9gv7-vhxw` 有效：PRB 112(8), published 2025-08-07，作者链 Liu/Si/Zhang/Du/Zhang 与著录一致；**但 refs 所挂 arXiv:2410.05360 是完全无关的论文（冰盖水弹性波 Hamiltonian Dysthe 方程，J. Fluid Mech. 1002 (2025) A24）**——见意见 R3-01（critical） | https://api.crossref.org/works/10.1103/9gv7-vhxw |
| [18] | Phys. Rev. B 2025 | ✓ v111(6):064311；published 2025-03-10 | https://api.crossref.org/works/10.1103/PhysRevB.111.064311 |
| [19] | arXiv:2511.10471, 2025 | ✓ Sankar S, Cheng X, Chen X 等 13 人；2025-11-13 提交；**无 journal_ref、无 DOI → 确未见正式发表版**；摘要确认"室温 CrSb 宽带三阶非线性反常霍尔，源自 Berry 曲率四极矩的非线性电导率" | https://export.arxiv.org/api/query?id_list=2511.10471 |
| [20] | arXiv:2601.19105, 2026 | ✓ Terashima T 等 8 人；2026-01-27 提交，v2 2026-07-15；**无 journal_ref、无 DOI → 确未见正式发表版** | https://export.arxiv.org/api/query?id_list=2601.19105 |
| [21] | Phys. Rev. Materials 2026 | ✓ v10(6):063402；arXiv API 返 journal_ref + DOI | https://api.crossref.org/works/10.1103/hnjw-k826 |
| [22] | arXiv:2511.16086, 2025 | ✓ Singh A K, Heinsdorf N, Mancilla A A 等 11 人；2025-11-20 提交，v2 2026-05-13；**无 journal_ref、无 DOI → 确未见正式发表版**；全文确认 T_N = 733(4) K、Γ-L 方向手性自旋分裂、六重劈裂、**能量劈裂 27(2) meV（正文写 27(5) meV）**——见意见 R3-03 | https://export.arxiv.org/api/query?id_list=2511.16086 |
| [23] | Rev. Sci. Instrum. 2026 | ✓ v97(4):045209；DOI `10.1063/5.0316448` 有效；**arXiv API 返 no journal_ref/no DOI，但 Crossref 已有正式版著录**——refs 已按正式版著录，正确 | https://api.crossref.org/works/10.1063/5.0316448 |
| [24] | Phys. Rev. A 2020 | ✓ v101(5):053411；arXiv API 返 journal_ref + DOI | https://api.crossref.org/works/10.1103/PhysRevA.101.053411 |
| [25] | arXiv:2208.10032, 2022 | ✓ Wang S 等 6 人；2022-08-22 提交；**无 journal_ref、无 DOI → 确未见正式发表版**；OpenAlex 亦仅返回 arXiv DOI，未见正式版；摘要确认"多光子 → 隧穿标度转变" | https://export.arxiv.org/api/query?id_list=2208.10032 |
| [26] | PNAS 2025 | ✓ v122(33):e2426253122；published 2025-08-18 | https://api.crossref.org/works/10.1073/pnas.2426253122 |
| [27] | arXiv:2604.23506, 2026 | ✓ Uzner E, Neufeld O（2 人）；2026-04-26 提交；**无 journal_ref、无 DOI → 确未见正式发表版**；摘要确认"层间耦合对 HHG 角度/椭圆度依赖的调控" | https://export.arxiv.org/api/query?id_list=2604.23506 |
| [28] | arXiv:2607.23652, 2026 | ✓ Granados C 等 8 人；2026-07-26 提交；**无 journal_ref、无 DOI → 确未见正式发表版**；摘要确认"3.2 μm 涡旋光驱动 ZnO、TC 随 CEP 在相邻整数间切换" | https://export.arxiv.org/api/query?id_list=2607.23652 |
| [29] | Rep. Prog. Phys. 2023 | ✓ v86(11):116401；arXiv API 返 journal_ref + DOI | https://api.crossref.org/works/10.1088/1361-6633/acf144 |
| [30] | Nature 2026 | ✓ v656(8129):854-860；published 2026-07-16；arXiv API 返 journal_ref + DOI；摘要确认"3D 体分辨 g 波序参量、Y₄⁻³ = yz(3x²−y²)"；**全文确认面内角分布 r⁴sin³θ cosθ sin(3φ)、节点 φ = 0°/60°/120°**——正文 g 波角分布表述逐字对应 | https://api.crossref.org/works/10.1038/s41586-026-10902-z |
| [31] | Nature 2024 | ✓ v626(7999):517-522；published 2024-04-03；作者链 23 位（Krempaský 等，Jungwirth 组） | https://api.crossref.org/works/10.1038/s41586-023-06907-7 |
| [32] | Phys. Rev. B 2024 | ✓ v109(11):115102；arXiv API 返 journal_ref + DOI；**摘要确认"非高对称动量点分裂达 0.8 eV、ΓK 高对称切向 SOC gap ~0.3 eV"** | https://api.crossref.org/works/10.1103/PhysRevB.109.115102 |
| [33] | arXiv:2603.15035, 2026 | ✓ Woodgate C D, Menai N, Ernst A, Staunton J B（4 人）；2026-03-16 提交；**无 journal_ref、无 DOI → 确未见正式发表版**；摘要确认"金属 CrSb 远低于 T_N 即热无序削弱；半导体 MnTe 接近/高于 T_N 才恢复" | https://export.arxiv.org/api/query?id_list=2603.15035 |
| [34] | Phys. Rev. B 2026 | ✓ v114(6):065130；arXiv API comment 字段明示 "accepted for publication in Phys. Rev. B"，refs 按正式版著录正确；摘要确认"磁群形式化给出交换近似下遗漏的附加自旋劈裂" | https://api.crossref.org/works/10.1103/mytl-kml2 |
| [35] | Appl. Phys. Lett. 2025 | ✓ v126(4):042402；arXiv API 返 journal_ref + DOI；作者链 8 位（Bai Y 等，Xu F 为末位通讯） | https://api.crossref.org/works/10.1063/5.0240434 |
| [36] | Phys. Rev. B 2025 | ✓ v112(14):144421；arXiv API 返 journal_ref + DOI | https://api.crossref.org/works/10.1103/zn8d-ft9b |
| [37] | Phys. Rev. B 2025 | ✓ v111(17):174451；arXiv API 返 journal_ref + DOI；**摘要确认 LSWT 手性磁振子劈裂"由两条长程交换相互作用（体对角线方向）的劈裂主导"——正文"第 11、12 近邻交换通道（J₁₁/J₁₂）"表述需按原文口径复核**，见意见 R3-05 | https://api.crossref.org/works/10.1103/PhysRevB.111.174451 |
| [38] | arXiv:2606.31573, 2026 | ✓ Mizuno K（1 人）；2026-06-30 提交，v2 2026-10-08；**arXiv API 已返 `<arxiv:doi>10.1103/1vc6-c7rs</arxiv:doi>` → 正式版已出**（Crossref：Phys. Rev. B 114(20), art. L200403, published 2026-10-19）——refs 仍标【预印本】且未更新，见意见 R3-07 | https://api.crossref.org/works/10.1103/1vc6-c7rs |
| [39] | npj Quantum Mater. 2025 | ✓ v10(1):47；published 2025-01-21；作者链 6 位 | https://api.crossref.org/works/10.1038/s41535-025-00766-3 |
| [40] | Phys. Rev. B 2023 | ✓ v107(6):L060403；arXiv API 返 journal_ref + DOI；作者链 14 位 | https://api.crossref.org/works/10.1103/PhysRevB.107.L060403 |
| [41] | arXiv:2601.12743, 2026 | ✓ Rajak D 等 10 人；2026-01-19 提交；**无 journal_ref、无 DOI → 确未见正式发表版**；全文确认"体相 ZnO/GaSe/MgO（透射）+ Si 与单层 WSe₂（反射）"材料清单、OAM 守恒独立于晶体对称性/相互作用范围/强 SOC | https://export.arxiv.org/api/query?id_list=2601.12743 |
| [42] | arXiv:2603.25317, 2026 | ✓ Korshunov A 等 11 人；2026-03-26 提交；**无 journal_ref、无 DOI → 确未见正式发表版**；全文确认 q*=(1/2,0) 短程电荷涨落、T_N 处 Kohn 类异常、T < T_N 时 ~6 meV 重整化、SSCHA+DFPT；**该文 T_N = 712 K（与本课题 733(4) K 口径不同）** | https://export.arxiv.org/api/query?id_list=2603.25317 |

**核实条数合计：42 / 42 条（29 条 DOI 经 Crossref + 13 条无 DOI 预印本经 arXiv API + 全部 38 条带 arXiv 号条目经 arXiv API 交叉确认 journal_ref/DOI 状态）。虚构文献 0 条；元数据错误 0 条（DOI/卷期页/年份/作者链/期刊名五字段不符数 = 0）。**

**短 DOI 新格式核查**：[16] `10.1103/nyy3-h8wr`、[17] `10.1103/9gv7-vhxw`、[21] `10.1103/hnjw-k826`、[34] `10.1103/mytl-kml2`、[36] `10.1103/zn8d-ft9b`、[5] `10.1103/bl2s-cv34`、[2] `10.1103/812z-nl4m`、[38] `10.1103/1vc6-c7rs` 八条均为 APS 2024 年起启用的短式 DOI，Crossref 均可正常解析且解析结果与著录完全一致 → **有效，非虚构**。

---

## 三、正文声称与文献内容匹配性抽查

抽查 18 条（被引最多 + 支撑关键判据 + 近年条目 + 争议链条 + 数值密集条目），**16 条匹配，2 条不匹配**。

| 正文声称（位置） | 文献实际内容 | 结论 |
|---|---|---|
| rationale L9/L23/L61、content L7/L71/L75、scheme L11/L43/L81/L107/L133「Tyulnev 等[1]在 TiSe₂ 中观测到 CDW 相进入后才出现的各向异性谐波分量，相变温度约 200 K」「3/5/7 阶谐波偏振不对称」 | Nature 正式版全文："exciting a 2×2×2 commensurate periodic lattice distortion below ~200 K"、"Harmonic yield for the 3rd, 5th, and 7th orders as a function of temperature"、"Below 100 K, H5 develops an asymmetry" | ✓ 200 K / 3-5-7 阶 / 相变下才出现，全对 |
| rationale L9、content L27、scheme L27/L107「Zhang 等[2]以含时薛定谔方程与现象学平均场多带模型结合，复现了 3/5/7 阶谐波偏振不对称的取向形貌」 | arXiv:2412.13329 摘要："simplified phenomenological mean-field model…HHG spectra is calculated through the time-dependent Schrödinger equation… correctly describes the measured intensity distribution of the third-, fifth-, and seventh-order harmonic generation as a function of polarization direction" | ✓ 方法与阶次逐字对应 |
| rationale L61「Tyulnev 实验 3/5/7 阶谐波相对强度约 10% 量级的不确定度」 | 正式版全文：误差棒口径为 "Error bars in all figures show one standard deviation"；全文正文出现的唯一百分比为反射率 "up to 22% relative rise"；另报告晶体取向偏差 "7° ± 2°" | ✗ **未见"10% 量级不确定度"表述**——见意见 R3-08 |
| rationale L23「Ahmed 与 Rehn 等人的两组 NbSe₂ 理论研究（实时 TDDFT 与解析方法互为方法学互补）[3][4]」；refs[3] 标注「NbSe₂ 单层 CDW 的 HHG 解析理论」 | arXiv:2310.03080 全文："we study the HHG of monolayer NbSe₂ using real-time time-dependent density functional theory (RT-TDDFT) simulations"；arXiv:2008.07131 摘要亦为实时 TDDFT | ✗ **[3] 与 [4] 方法相同（均为 RT-TDDFT），无"解析方法"对照**——见意见 R3-04 |
| rationale L15/L25、scheme L45、full_review L24「Šmejkal 等人[12]奠定交错磁作为独立磁性相的对称性分类与 Kramers 自旋简并提升的理论框架」「d 波主对称性分类依据」 | PRX 12, 031042（arXiv 题名 "Altermagnetism: spin-momentum locked phase protected by non-relativistic symmetries"）；正文 d 波归属与 𝒴₂⁻¹ 分类 | ✓ |
| rationale L31、content L45「Yang 等[16]在 MnTe 中以时间分辨磁光克尔—沃伊特效应观测到两类响应的共存，即动量空间的 Berry 曲率响应（Kerr 信号）与实空间的 Néel 序各向异性响应（Voigt 信号）」 | arXiv:2605.24320 摘要："coexistence of pronounced Kerr and Voigt effects in the altermagnet MnTe… Kerr effect originates from the intrinsic Berry curvature of altermagnetism distribution in momentum space, while the Voigt effect arises from an anisotropic permittivity" | ✓ |
| rationale L15、scheme L67/L79、full_review L27「MnTe 上角分辨光电子能谱已直接观测到动量依赖自旋分裂，非高对称动量点分裂达 0.8 eV[32]」 | arXiv:2308.10117 摘要："The magnitude of the splitting reaches 0.8 eV at non-high-symmetry momentum points, which is much larger than the spin-orbit gap of ~0.3 eV along the GK high-symmetry cut" | ✓ 数值逐字对应 |
| rationale L27、content L43、scheme L29/L85/L117「Werner 等人[11]指出，SOC 可忽略时低阶偶次谐波依赖外磁场方向，SOC 充分强时高能峰、谐波平台、圆二色性与自旋流谐波均出现」 | arXiv:2407.07752 摘要："The altermagnetism manifests itself in the magnetic field dependence of the low harmonics… Spin-orbit coupling leads to additional higher energy peaks and plateau structures… While the pure altermagnet or spin-orbit system exhibits no circular dichroism… an altermagnetic system with spin-orbit coupling shows such a dichroism. We also analyze the spin currents and their high harmonic spectrum." | ✓ 四个要素逐条对应（且正文"必须二者兼具才有圆二色性"的口径与原文一致） |
| rationale L35、scheme L45、full_review L24「g 波证认的交换劈裂遵循实球谐函数 𝒴₄⁻³ = zy(3x²−y²)，面内角分布为 sin(3φ) 形态，节点位于 0°/60°/120°」；「Long 等[30]由 dHvA 角谱作 g 波证认」 | Nature 全文："𝒴₄⁻³ = yz(3x²−y²)… or equivalently in spherical polars as r⁴sin³(θ)cos(θ)sin(3φ)… This function has nodes when θ = 0°, 90° and φ = 0°, 60°, 120°" | ✓ 面内角分布与节点位置逐字对应（本条为 g 波争议的判据基础，核实无误） |
| rationale L33、content L45、scheme L113、full_review L21/L40「Singh 等[22]由非弹性中子散射在 Γ-L 方向观测到六重动量空间劈裂，自旋波拟合给出能量劈裂 27(5) meV；能量维度受谱仪分辨率（约 20 meV）限制未直接分辨」 | arXiv:2511.16086 全文："The energy splitting reaches **27(2)** meV at H = 0.20… which is comparable to the instrumental resolution (20 meV) and therefore remains unresolved in the energy dimension"；"six-fold spin-wave splitting is clearly established along the six symmetrically equivalent (H, 0, 2.85) directions" | ✗ **数值 27(5) → 原文为 27(2) meV**（六重劈裂与 20 meV 分辨率口径 ✓）——见意见 R3-03 |
| rationale L77、content L35/L37、scheme L113、full_review L21「Néel 温度 733(4) K 由 Singh 等人[22]的极化中子衍射与磁化率测量共同标定」 | arXiv:2511.16086 全文："Magnetic susceptibility and polarized neutron diffraction measurements show that CrSb is a perfectly compensated Ising altermagnet below a Néel temperature of T_N = 733(4) K" | ✓ 三项口径（733(4) K、极化中子衍射、磁化率）全对 |
| rationale L79、scheme L35、full_review L25「第一性原理无序局域矩计算给金属态[33]」「金属 CrSb 在远低于 TN 即被热无序削弱、半导体 MnTe 接近 310 K 才恢复自旋简并」 | arXiv:2603.15035 摘要："via application of the disordered local moment picture… In metallic CrSb, this occurs at temperatures well below T_N… By contrast, in semiconducting MnTe… the spin degeneracy only returns at temperatures close to and above T_N" | ✓ |
| rationale L41、content L63「Granados 等人[28]证明少周期涡旋光驱动 ZnO HHG 中谐波拓扑荷可随载波包络相位在相邻整数间切换」 | arXiv:2607.23652 摘要："in the regime of few-cycle pulses… By driving HHG in a ZnO crystal with few-cycle (≈1.5 cycles) vortex beams centered at 3.2 μm, we observed that the measured TC becomes strongly CEP-dependent, switching between adjacent integer values" | ✓ 体系/波长/阶次全对 |
| content L63「Rajak 等人[41]在 ZnO、GaSe、MgO、Si 与单层 WSe₂ 上测得谐波轨道角动量严格随谐波阶次与驱动光拓扑电荷线性增长，该守恒独立于晶体对称性与强 SOC」 | arXiv:2601.12743 全文："(1) a-cut Zinc Oxide (ZnO)… (2) Gallium Selenide (GaSe)… (3) Magnesium Oxide (MgO)… in the reflection geometry for silicon (Si)… and monolayer Tungsten Diselenide (WSe₂)… the OAM conservation law is robust across all these widely differing crystalline symmetries" | ✓ 材料清单与几何逐一对应 |
| rationale L71「激子凝聚的 HHG 响应[8]涉及束缚态相干性」 | arXiv:2307.14693 摘要与题名："strongly bound excitons in solids… nonlinear response of ultrafast strong-field driven excitons in a one-dimensional solid"——**全文无 exciton condensation / superfluid / EPC 任何表述** | ✗ **该文研究的是激子本身的 HHG 谱学，不是激子凝聚**——见意见 R3-06 |
| scheme L31「Korshunov 等人[42]由 X 射线漫散射与非弹性散射在 CrSb 中观测到，T > T_N 时 M 点（q* = (1/2, 0)）的短程电荷涨落仍然存在，进入磁有序相后随即消失；T_N 处 q* 声子色散形成 Kohn 类异常；T < T_N 时交换致伸缩使该软模重整化约 6 meV」 | arXiv:2603.25317 全文："short-range charge-order fluctuations at the M point… q*=(1/2 0), persisting above the Neel temperature… these fluctuations collapse upon entering the magnetically ordered phase… At T_N the phonon dispersion at q* develops a pronounced Kohn-like anomaly… Below T_N, exchange striction dramatically renormalizes the associated soft phonon mode by approximately ~6 meV, the largest spin-phonon coupling ever reported" | ✓ 三段式表述与相位关系逐字对应 |
| rationale L43「孟胜课题组的早期工作给出利用全光学 HHG 谱学探测高压量子态的能带结构与电声耦合方法[9]」 | PNAS 121, e2316775121 题名 "Solid-state high harmonic spectroscopy for all-optical band structure probing of high-pressure quantum states" | ✓ |
| rationale L33、scheme L73/L109「Sankar 等人[19]在室温 CrSb 中观测到宽带非线性反常霍尔效应，表明 Berry 曲率四极矩贡献在光场驱动下可被分辨」 | arXiv:2511.10471 摘要："discovery of a broadband third-order nonlinear anomalous Hall effect in altermagnetic CrSb at room temperature… induced by the nonlinear electric susceptibility of a Berry curvature quadrupole" | ✓ |

---

## 四、引用覆盖充分性评估

- **被引最多的条目**：[1]（Tyulnev 2025，13 次：rationale L9/L23/L61、content L7/L71/L75、scheme L11/L43/L81/L107/L133、full_review L7/L34）、[22]（Singh，8 次）、[2]（Zhang，7 次）、[18]（Ma，6 次）、[30]（Long，6 次）、[11]（Werner，5 次）。前 10 条承担了"TiSe₂ 实验—理论双源证据链""交错磁对称性框架与分类""SOC 两极限""CrSb 体态基准与 g 波争议""多体混合警示""唯一归因方法学"六条主线，引用结构与论证链匹配。
- **关键判据的引用支撑**：TiSe₂ 复现判据（[1][2]）、CrSb 信号判据（[20][21][22]）、g/d 波争议前置判据（[12][30][34][36][37]）、多通道混合警示（[5][7]）、反演维度边界（[28][41]）、SOC 连续参数化（[11]）、正演模型规范与场强窗口（[24][25][26][27]）、独立验证层（[19][22][23][35][39][40][42]）均有对应条目。
- **无引用支撑的关键论断**：三处，均已显式声明"文献未给出"或自标为方案设定值——① rationale L29「近期研究表明交换场可在不依赖重金属原子序数的条件下产生 Rashba/Weyl/Dresselhaus 型自旋纹理」**（该段无任何编号引用，检索池三源中亦无对应记录）**；② rationale L69「超导序参量涨落的 HHG 探测已在多个超导体系中展示 Higgs 模式与准粒子非线性的可分辨信号，但 Higgs 模式与相位模之间的归因仍存争议」**（该段无编号引用）**；③ 各项工程阈值（σ = 0.5%—0.8%、κ 三档、后验 50%、10 倍量级等）均自标为设计值，处理方式正确，不属漏引。
- **覆盖缺口（low）**：rationale L23 中「Ahmed 与 Rehn 等人的两组 NbSe₂ 理论研究」以**作者名 + [3][4] 并列**形式挂在同一句，未区分哪一条对应实时 TDDFT、哪一条对应"解析方法"——这一缺口的成因见 R3-04。
- **密度判断**：正文 97 次编号引用 / 42 条 refs，比值 2.31，显著高于范本（正文 10–20 次 / refs 30–40 条）。从被引分布看**无"同一条目反复充数"模式**（[1] 13 次、[22] 8 次、[2] 7 次各有实质不同的支撑点；42 条中最低引用次数为 1）。结论：**覆盖充分**，密度偏离源于本课题"编号 + 【关联】长标注"体例，非灌水。

---

## 五、意见清单

| 编号 | severity | 模块 | 位置 | 问题 | 原文摘录 | 修改建议 |
|---|---|---|---|---|---|---|
| R3-01 | **critical** | 参考文献 | refs 条目 [17]（references.md L47）；正文 rationale L35、full_review L24 | **arXiv 号错挂到完全无关论文**：refs 所挂 arXiv:2410.05360 经 arXiv API 反查为 "A Hamiltonian Dysthe equation for hydroelastic waves in a compressed ice sheet"（冰盖水弹性波，J. Fluid Mech. 1002 (2025) A24，作者 Guyenne/Kairzhan/Sulem），与 "Anisotropic high harmonic generation as a gauge of altermagnetism in RuO₂" 无任何关系。同条目的 DOI `10.1103/9gv7-vhxw` 真实有效（PRB 112(8), published 2025-08-07, 作者 Liu/Si/Zhang/Du/Zhang 全对），故**错误仅在 arXiv 号** | `[17] Liu, Y. Q., Si, M. S., Zhang, G. P., Du, H. & Zhang, Z. M. Anisotropic high harmonic generation as a gauge of altermagnetism in RuO₂. *Phys. Rev. B* **112**, L081105 (2025). DOI: 10.1103/9gv7-vhxw; arXiv:2410.05360.` | 删除错误 arXiv 号，改挂正确预印本号。**该文 arXiv API 按标题与作者检索均零命中、OpenAlex 的 locations 也只返回 DOI（无 arXiv 版本），故正确做法是删除 "arXiv:2410.05360" 整段，仅保留 DOI 著录**（正式版著录已足够）；若 M1 坚持保留预印本号，须先在 arXiv/OpenAlex 定位到真实编号再回填，不得凭推测填写。证据：https://export.arxiv.org/api/query?id_list=2410.05360 与 https://api.openalex.org/works/doi:10.1103/9gv7-vhxw |
| R3-02 | **critical** | 立项依据 | rationale L61（§一.3 第一条判据阈值合成段）；连带 full_review L34「TiSe₂ 复现判据」行 | **正文声称的文献数值在原文中不存在**：正文称"Tyulnev 实验 3/5/7 阶谐波相对强度约 10% 量级的不确定度（覆盖激光涨落、晶体取向与温度扫描步长等合成效应）"，但 [1] 正式版全文（含 Methods、图注）误差棒口径仅写 "Error bars in all figures show one standard deviation"，正文出现的唯一百分比是反射率 "up to 22% relative rise"，另报告晶体取向偏差 "7° ± 2°"——**无"10% 量级不确定度"这一数值**。该 10% 是本项目判据阈值的合成依据，属"把自设阈值写成文献数值"，一旦被评审追查即为不可辩护 | `该阈值由两部分合成：Tyulnev 实验 3/5/7 阶谐波相对强度约 10% 量级的不确定度（覆盖激光涨落、晶体取向与温度扫描步长等合成效应），以及本项目正演—反演流程的工程余量。` | 改为**明示为项目自设的合成经验取值**，不再挂靠文献数值口径，例如："该阈值由两部分合成：一是覆盖激光涨落、晶体取向偏差（[1] 实测晶体轴与偏振夹角偏差为 7° ± 2°）与温度扫描步长的相对强度稳定度，本项目按 10% 量级保守取值；二是本项目正演—反演流程的工程余量。第 1 年以实测复现精度校准该阈值的合理性。"同时同步 full_review L34 对照表该行。证据：https://www.nature.com/articles/s43246-025-00873-5 |
| R3-03 | **high** | 研究内容 | content L45（§二.3 自旋激发维度段）；连带 full_review L40、scheme L89 附近口径 | **正文数值与原文不符**：正文写"自旋波拟合给出能量劈裂 27(5) meV"，而 [22] arXiv:2511.16086 全文明确为 "The energy splitting reaches **27(2)** meV at H = 0.20"。同一句的其余两项（六重动量空间劈裂、约 20 meV 谱仪分辨率致能量维未直接分辨）经核实与原文一致，故属孤立数值错误 | `Singh 等人[22]由非弹性中子散射在 Γ-L 方向观测到六重动量空间劈裂特征，自旋波拟合给出能量劈裂 27(5) meV` | 将 27(5) meV 改为 **27(2) meV**，并同步 full_review L40「手性磁振子能量劈裂」行（现写 "27(5) meV"）与 scheme 中涉及该数值的段落。证据：https://arxiv.org/html/2511.16086v2 |
| R3-04 | **high** | 立项依据 + 参考文献 | rationale L23；refs 条目 [3]（references.md L11） | **方法学对照关系描述错误 + refs 标注错误**：正文称 NbSe₂ 两组研究为"实时 TDDFT 与解析方法互为方法学互补"，refs[3] 亦标注"NbSe₂ 单层 CDW 的 HHG 解析理论"。但 arXiv:2310.03080 全文方法段为 "we study the HHG of monolayer NbSe₂ using **real-time time-dependent density functional theory (RT-TDDFT)** simulations"，与 [4]（arXiv:2008.07131，实时 TDDFT）**方法完全相同**——两文不构成"TDDFT vs 解析方法"的对照，[3] 也不是解析理论 | `Ahmed 与 Rehn 等人的两组 NbSe₂ 理论研究（实时 TDDFT 与解析方法互为方法学互补）[3][4] 同样指出 HHG 对 CDW 序敏感` ／ `【关联：NbSe₂ 单层 CDW 的 HHG 解析理论，§一.2 NbSe₂ 理论敏感性证据】` | ① refs[3] 标注改为"NbSe₂ 单层 CDW 的 HHG 实时 TDDFT 理论"；② 正文改为"两组实时 TDDFT 研究（[3] 聚焦单层 NbSe₂ 的 2H 与 CDW 两相、奇偶谐波与偏振的对应关系，[4] 聚焦泵浦强度依赖与 CDW 序的可辨识特征）"或等价表述，去掉"解析方法"这一不存在的对照轴；③ 不得新增池外条目，两条均在池内（`literature-report.md` 有 Ahmed/Rehn 记录）。证据：https://arxiv.org/html/2310.03080v2 与 https://export.arxiv.org/api/query?id_list=2008.07131 |
| R3-05 | **medium** | 研究内容 | content L45（§二.3 自旋激发维度段）；refs 条目 [37]（references.md L115） | **原文表述精度不足**：正文称 [37] 预言 CrSb 手性磁振子劈裂"由等长而对称不等价的第 11、12 近邻交换通道（J₁₁/J₁₂）驱动"。arXiv:2503.12920 摘要原文为 "primarily driven by the splitting of two **long-range exchange interactions**, with exchange paths along the **body diagonal lines** of the unit cell"——**未以 J₁₁/J₁₂ 编号指称**；J₁₁/J₁₂ 是同文体系化 Heisenberg 拟合的参数化用语（该文正文以"第 11、12 近邻"表述两体通道），[22] 则以 J₁₂ 标记贡献六重劈裂的特定交换通道。当前写法把两篇文献的参数体系混用 | `Zhang 等人[37]以线性自旋波理论预言 CrSb 的手性磁振子劈裂由等长而对称不等价的第 11、12 近邻交换通道驱动。` | 改为贴合原文的表述，例如："Zhang 等[37]以线性自旋波理论（LSWT）与含时密度泛函微扰理论预言，CrSb 手性磁振子劈裂主要由**两条长程交换相互作用（体对角线方向）的劈裂**驱动（LSWT 给出最高约 9 meV、约 140 meV 高激发能区；TD-DFPT 给出最高约 30 meV 但受 Stoner 连续体 Landau 阻尼严重涂抹）。"若要保留 J₁₁/J₁₂ 记法，须加"（对应文中体系化 Heisenberg 拟合的第 11、12 近邻通道）"并注明与 [22] 的参数化对应关系。证据：https://export.arxiv.org/api/query?id_list=2503.12920 |
| R3-06 | **medium** | 立项依据 | rationale L71（§一.3 范围限定说明段） | **文献内容错挂**：[8] 被表述为"激子凝聚的 HHG 响应[8]涉及束缚态相干性"，但 Jensen 等（PRA 109, 063104）的标题与摘要均为 "High-harmonic spectroscopy of **strongly bound excitons** in solids"——研究对象是**强束缚激子本身**的 HHG 谱学（有限激子布居在 HHG 谱中留下独特签名、可反演激子布居、激子复合与激子能级移动的谱印记），**全文无 exciton condensation / superfluid / EPC 任何表述**，与"激子凝聚"这一物相无关 | `激子凝聚的 HHG 响应 [8] 涉及束缚态相干性，与磁序对称破缺机制独立。` | 改为"强束缚激子的 HHG 响应[8] 涉及激子态的相干布居（有限激子布居在谐波谱中留下可反演的独特签名），与磁序对称破缺机制独立。"；同段首句「这里不追求在同一研究中对超导、激子凝聚等多种序参量类型开展归因研究」中"激子凝聚"若指物相，可保留为范围排除语，但**不得再把 [8] 挂到"激子凝聚"名下**。证据：https://export.arxiv.org/api/query?id_list=2307.14693 |
| R3-07 | **medium** | 参考文献 | refs 条目 [38]（references.md L117） | **预印本已出正式版但条目未更新**：arXiv API 对 arXiv:2606.31573 已返回 `<arxiv:doi>10.1103/1vc6-c7rs</arxiv:doi>`；Crossref 反查该 DOI 为 **Phys. Rev. B 114(20), art. L200403, published 2026-10-19**（作者 Mizuno K，标题一致）。条目仍标【预印本】、未给 DOI 与卷期页，与本文件其余条目的著录体例（凡有正式版者一律按正式版著录，如 [2][5][14][23][34][35][36][37]）不一致 | `[38] Mizuno, K. High-harmonic spin-current signatures of altermagnetic spin-group symmetry. arXiv:2606.31573 (v1, 2026-06-30). 【预印本】【关联：自旋点群框架下电荷/自旋电流 HHG 选择定则…】` | 改为正式版著录：`[38] Mizuno, K. High-harmonic spin-current signatures of altermagnetic spin-group symmetry. *Phys. Rev. B* **114**, no. 20, L200403 (2026). DOI: 10.1103/1vc6-c7rs; arXiv:2606.31573 (v2, 2026-10-08).【正式发表】`，并把【关联】标注中的"§二.3 …弱 SOC 极限"等说明保留；正文 content L41 称引"（理论方案）"可保持（该文仍为理论工作），但若正文写"预印本"字样需同步改。证据：https://api.crossref.org/works/10.1103/1vc6-c7rs |
| R3-08 | **medium** | 立项依据 + 研究方案 | rationale L61（§一.3 阈值合成段）；full_review L34（TiSe₂ 复现判据行） | **同 R3-02 的口径在对照表中被固化**：full_review 跨章节统一指标对照表"TiSe₂ 复现判据"行把 10% 写为"（设计值：文献实验不确定度量级 + 工程余量合成经验取值）"，虽已标注"设计值"，但"文献实验不确定度量级"仍暗示该量级出自 [1]，而 [1] 未给出该数值 | `TiSe₂ 复现判据 \| 方向与 Tyulnev [1] 一致，幅度偏差 ≤ 10%（设计值：文献实验不确定度量级 + 工程余量合成经验取值）` | 与 R3-02 同步改为"（设计值：本项目按激光涨落、晶体取向偏差与温度扫描步长保守取定的相对强度稳定度量级 + 工程余量的合成经验取值，非 [1] 直接给出的不确定度）"。 |
| R3-09 | **medium** | 立项依据 | rationale L29（§一.2 结尾段） | **关键论断零引用支撑且池中无对应记录**：该段断言"近期研究表明交换场可在不依赖重金属原子序数的条件下产生 Rashba/Weyl/Dresselhaus 型自旋纹理"，并以此"为本项目 SOC 通道的弱 SOC 极限判据提供独立参照"——该句**无任何编号引用**；检索 `02_literature/` 三源（gap-analysis、candidates.bib 系列、reading-notes.md）按 "Rashba" 检索**零命中**，即池中无任何可支撑该断言的条目 | `近期研究表明交换场可在不依赖重金属原子序数的条件下产生 Rashba/Weyl/Dresselhaus 型自旋纹理。这一非相对论 SOC 路径扩展了弱 SOC 极限下 HHG 候选信号的约束条件，也为本项目 SOC 通道的弱 SOC 极限判据提供独立参照。` | **按文献池三源纪律，池中无记录不得写入引用**。二选一：① 去掉该段（该段与本项目主线关联弱，删除不影响论证完整性，且 [11] 已直接给出弱 SOC 极限的 HHG 判据）；② 若保留，须先在池三源中补入可支撑的原始文献（如交换场驱动自旋纹理的非相对论 SOC 理论/实验条目），再配编号。**严禁凭记忆补引池外文献。** |
| R3-10 | **medium** | 立项依据 | rationale L69（§一.3 末段） | **关键论断零引用支撑**：该段断言"超导序参量涨落的 HHG 探测已在多个超导体系中展示 Higgs 模式与准粒子非线性的可分辨信号，但 Higgs 模式与相位模之间的归因仍存争议"，该句**无任何编号引用**；检索池三源按 "Higgs" 命中 `literature-report.md` 一处（缺口记录文本，非可引条目），`reading-notes.md` 无对应条目 | `超导序参量涨落的 HHG 探测已在多个超称体中展示 Higgs 模式与准粒子非线性的可分辨信号，但 Higgs 模式与相位模之间的归因仍存争议。` | 该段的作用是划定范围（不把超导/激子纳入归因框架），**可改为不依赖具体文献声称的范围声明**："超导序参量涨落与激子凝聚等序参量类型的 HHG 探测已形成独立研究方向，其中超导体系的 Higgs 模式与相位模归因争议是本领域内的公开争论；其归因框架与本项目的交错磁序参量不可辨识性框架不共享，故不纳入本项目。"若要保留具体文献声称，须先在池三源补入对应条目后再配编号。 |
| R3-11 | **low** | 参考文献 | refs 文件通篇（references.md 头部与全部 42 条） | **refs 缺少头部格式规则声明与尾部总注**：本文件采用"作者. 标题. 期刊, 年, 卷(期): 页. DOI: …; arXiv: …【正式发表/预印本】【关联：…】"的自定义体例，并以 12 个分节（### 1. … ### 12. …）组织，但**文件开头没有一条体例说明**（对比同批次 attosecond 课题的 references.md 头部有完整规则声明），**文件末尾也没有尾注**（说明条目总数、编号连续性、预印本标注口径与文献检索截止时间）。读者（尤其评审）无从判断 42 条的构成逻辑、预印本标注含义与检索截止口径 | （references.md L1—L7 为标题与第一分节标题，其后直接是 [1] 条目；文件末尾为 [42] 条目，无尾注） | 建议补一段**头部体例说明**（统一格式、期刊名/卷期页写法、DOI 与 arXiv 并列规则、【正式发表】/【预印本】/【综述】标记含义、【关联】标注为"该条在本项目中的支撑位置与口径"）与**一段尾部总注**（条目 42 条、编号 1—42 连续且全部已在正文对应位置引用、其中 N 条为 arXiv 预印本尚未见正式发表版、本申请书文献检索截止于 2026 年 8 月）。注：正文 rationale L11/L45 与 scheme L141 均声明"截至 2026 年 8 月检索"，refs 尾部宜与此口径一致（现 refs 中最新条目为 2026-10-19 正式发表的 [38]，若采纳 R3-07 更新，则检索截止线须一并声明为"2026 年 10 月"或注明 [38] 为补充检索获得）。 |
| R3-12 | **low** | 立项依据 | rationale L77（§一.4 CrSb 选择理由段） | **文献池口径差异未加说明**：正文自陈"既有热力学—输运口径的文献测值约 705—723 K，与 733(4) K 的差异属测量口径不同"，其中 705—723 K 区间**无编号引用**；另 [42]（Korshunov 等）实测 T_N = 712 K 亦落在该区间内，而正文在 scheme L31 引 [42] 时**未提及该 T_N 数值**，读者无法把"705—723 K"与池内已有条目 [42] 的 712 K 对上 | `既有热力学—输运口径的文献测值约 705—723 K，与 733(4) K 的差异属测量口径不同，量级判断不受影响。` | 补编号并明示口径，例如："既有热力学—输运口径的文献测值约 705—723 K（如 [42] 的 T_N = 712 K），与 733(4) K 的差异属测量口径不同"。注：[42] 在池中有完整阅读笔记（`02_literature/reading-notes.md` 首条即 2603.25317 的笔记，T_N = 712 K 已在其"主要发现"节第 (1) 条），属池内条目，可直接引用，**不涉及池纪律风险**。证据：https://arxiv.org/html/2603.25317v1 |

---

## 六、结论

1. **五项对账**：占位符 0 / 死条目 0 / 超界 0 / 一号两用 0 / 断链 0。预跑脚本结论**复核准确**；经 full_review 口径、格式变体穷举（含本课题实际出现的 q* = (1/2, 0) 密勒/倒格矢语境，排除逻辑工作正常）与"注释行藏引"排查**未发现漏报**，42 条 refs 全部被正文引用，无死条目。
2. **元数据真实性**：42/42 条经 Crossref + arXiv API + OpenAlex 联网核实，**虚构文献 0 条、DOI 全部有效（含 8 条 APS 短式新 DOI）、卷期页/年份/期刊名/首作者四字段不符数 = 0**。**唯一实质性元数据错误是 [17] 的 arXiv 号错挂到一篇完全无关的冰盖水弹性波论文**（R3-01，critical）；另 [38] 已有正式版（PRB 114, L200403, 2026-10-19）但条目仍标预印本（R3-07，medium）。
3. **内容匹配性**：抽查 18 条，**16 条匹配、2 条不匹配**——① rationale L61 把本项目自设的 10% 阈值写成 "[1] 的 10% 量级不确定度"，而 [1] 全文无此表述（R3-02，critical）；② rationale L23 / refs[3] 把同为 RT-TDDFT 的 [3][4] 说成"实时 TDDFT 与解析方法互为互补"（R3-04，high）。另有三处数值/表述偏差：27(5) → 27(2) meV（R3-03，high）、[37] 的"第 11、12 近邻 J₁₁/J₁₂"→ 原文作"两条长程交换相互作用（体对角线方向）"（R3-05，medium）、[8] 由"强束缚激子"被错挂到"激子凝聚"名下（R3-06，medium）。
4. **意见统计**：critical 2 / high 2 / medium 6 / low 2，合计 **12 条**。
5. **需 M1 裁决的关键项**：R3-01（[17] arXiv 号——**删除 arXiv 号、仅保留 DOI 正式版著录是唯一安全解**，因该文在 arXiv 与 OpenAlex 均无可定位的预印本版本，严禁凭推测回填编号）；R3-02（10% 阈值的文献挂靠必须解除，否则构成"自设阈值伪装为文献数值"）；R3-04（[3][4] 方法对照关系与 refs[3] 标注须同步改正，两处不可只改其一）。
6. **不涉及新增引用**：本报告未建议任何检索池外的新增文献。R3-09（Rashba 段）与 R3-10（Higgs 段）给出的均为**去引用化**方案（改写为范围声明或删除）；R3-12 建议补挂的 [42] 属池内条目（`reading-notes.md` 有完整笔记）；R3-04/R3-05/R3-06 均为既有条目的**表述校正**，不改编号、不引新条目。三源纪律核验结果：`02_literature/` 下**无 `candidates.bib` 单文件**（仅有 `targeted-research/candidates-*.bib` 15 个分片 + `gap-analysis/*.json` 12 份 + `reading-notes.md`），本报告所引池内条目（[3][4][42] 等）均可在 `literature-report.md` / `reading-notes.md` / `candidates-*.bib` 中查到对应记录。
7. **元数据体例的一处全篇偏差（供参考，未单列意见）**：本文件条目采用"前三位作者 + et al."的折断（如 [1] "Tyulnev, I., Zhang, L., Vamos, L., Poborska, J., Bhattacharya, U., Chhajlany, R. W., Grass, T., Mañas-Valero, S., Coronado, E., Lewenstein, M. & Biegert, J." 全列 11 人、[6]/[19]/[22] 等则折为 et al.），折断规则在文件内**不统一**（[1] 11 人全列、[16] 12 人全列、[19] 13 人折 et al.、[31] 23 人全列）。因属全篇体例而非事实错误，且 R3-11 已建议补入头部体例说明统一规则，此处不单列意见，建议 M1 在补体例说明时一并明确折断阈值。
