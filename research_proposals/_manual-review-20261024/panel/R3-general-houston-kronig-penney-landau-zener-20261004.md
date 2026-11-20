# R3 引用审校 — general-houston-kronig-penney-landau-zener-20261004

审校范围：`research_proposals/optimizing/general-houston-kronig-penney-landau-zener-20261004/04_proposal/sections/` 下 `rationale.md`（立项依据）、`content.md`（研究内容）、`scheme.md`（研究方案）、`references.md`（参考文献），并纳入 `full_review.md`（整篇一致性审查）中的引用对账。
审校日期：2026-10-29（第四轮评审团，课题 r2）。对账复核：主代理预跑脚本结论（42/42 全被引）经独立脚本 /tmp/r3-audit.py（含 full_review 口径、区间/并列展开、密勒指数排除）复现。
refs 42 条。审校视角：期刊文献编辑（R3），只管引用真实准确、编号自洽、覆盖充分；科学正确性归 R1、语言归 R2。
上轮遗留复核点：① 曾虚构"Calegaro[26]"——r2 references.md 已整体重写，[26] 现为 Korolev 真实条目，本轮联网核实；② full_review 曾跳号 [1]–[34] 但 refs 只有 33——已补丁，本轮核对无回退；③ 上轮 R4 显示 r1 遗留 P0 10/high 15——经查 05_review/round4-processor-disposition.md（2026-10-15）全部 P0/high 已处置（含 references 重写、6 条虚构/错挂条目按真身替换，见 refs-xcheck-mapping-r2.md），本轮以联网正核验证重写质量。

---

## 一、编号对账（五项）复核

| 项 | 计数 | 明细 |
|---|---|---|
| 1. 占位符 | **0** | 正文三章 + full_review + references 全域无 `[TODO]`/`[待补]`/`[XX]`/空括号 |
| 2. 死条目 | **0** | 正文三章 distinct = 42；并入 full_review 后仍 = 42 = refs 条目数，无零引用条目 |
| 3. 超界 | **0** | 正文最大引用号 = 42 = refs 最大条目号，无越界 |
| 4. 一号两用 | **0** | refs 编号 1–42 严格升序、连续、无重号 |
| 5. 断链 | **0** | 正文引用号集合 ⊆ refs 条目号集合，无"正文用了 refs 里没有"的编号 |

**复核确认预跑 PASS 结论准确，无漏报。** 脚本盲区人工补查：

- **区间/并列形式**：rationale L5 `[4–5]`（区间）、`[1,20,26]`、`[4,11,12]`（并列）、L61 `[16–17,27]`（混合）、content/scheme `[6,15]`、`[9,11]` 等，展开后均正确计入 distinct（合并 42/42）；无因展开遗漏造成的假死条目/假断链。
- **full_review 口径**：full_review 含 30 个引用 token / 26 distinct，全部落在正文三章已引集合内——纳入后五项计数不变。上轮跳号问题**未复发**（现行 full_review 为骨架式，无"[1]–[N]"全区间声明，逐个引用号均 ≤42 且在册）。
- **注释行藏引**：refs 头部体例说明行（L3–L7）无 `[N]` 编号；各条目行挂钩注释（括注）中的"§2.1/§2.2"为章节指代非引用编号；正文无 HTML 注释藏编号。
- **refs 头部体例自证 vs 实物**：体例声明"尚未见刊的预印本条目以 arXiv 编号标注并注明版本与年份，条目内不并列 arXiv 编号"——逐条清点：纯预印本 6 条 [12][30][31][32][41][42] 均含 arXiv 编号+版本+年份 ✓；36 条 DOI 条目均**无** arXiv 并列 ✓。体例自洽。但头部另一句"本章列 **40** 条文献条目"与实物 42 条不符（见意见 R3-02）。
- **正文预印本标注**（观察项，不入意见）：[12][31] 正文带"（预印本）"字样，[30][32][41][42] 正文未标——本课题头部未自证"正文引用处均标注预印本属性"，refs 条目已明示 arXiv，不构成失实；建议后续统一补标（与 ssh-weyl 体例对齐）。
- **引用密度**：正文编号引用 token 合计 149（rationale 57 / content 47 / scheme 45）+ full_review 30，refs 42 条全部被引，无灌水模式。

---

## 二、联网核实记录（限量）

核实方法：① DOI 条目经 Crossref REST API（`https://api.crossref.org/works/<DOI>`）逐字段比对期刊/年/卷/期/页/首作者，APS 短式 DOI 一并验证解析；② arXiv 预印本经 arXiv API 反查标题、作者链、提交/更新日期、`journal_ref`/`<arxiv:doi>` 字段；③ 关键数值声称回 Crossref 摘要字段逐句核对。本轮正核 17 条：11 条 Crossref（4 条 2026 新刊 + 3 条 APS 短式 DOI + Korolev/Rasputnyi/Chen/Koll/Obreshkov/Tan 关键支撑）+ 6 条 arXiv 预印本全查。

| 编号 | 著录 | 核实结果 | 证据 URL |
|---|---|---|---|
| [26] | Nat. Commun. 17, 10954 (2026) | ✓ Korolev V; Lettau T; Krishna V 一作链；期刊/年/卷/页全对；摘要确认"momentum-dependent dephasing derived from first principles scattering rates"——**上轮虚构"Calegaro"槽位现为真实文献** | https://api.crossref.org/works/10.1038/s41467-026-78716-1 |
| [14] | Comput. Phys. Commun. 320, 109958 (2026) | ✓ Thümmler M; Lettau T; Croy A；期刊/年/卷/文章号全对 | https://api.crossref.org/works/10.1016/j.cpc.2025.109958 |
| [19] | Nat. Phys. 22(10), 1607–1614 (2026) | ✓ Lesko D; Weitz T; Wittigschlager S；卷期页年逐字段一致 | https://api.crossref.org/works/10.1038/s41567-026-03429-7 |
| [18] | Nat. Phys. 20(12), 1960–1965 (2024) | ✓ Rasputnyi A; Chen Z; Birk M；全对 | https://api.crossref.org/works/10.1038/s41567-024-02659-x |
| [27] | ACS Photonics 12(5), 2819–2827 (2025) | ✓ Chen Z; Levit M; Kern Y；全对（题名 "Attosecond Pulses from a Solid Driven by a Synthesized Two-Color Field at Megahertz Repetition Rate" 与 MgO 双色场 MHz 声称对应） | https://api.crossref.org/works/10.1021/acsphotonics.5c00410 |
| [33] | Phys. Rev. Research 8, 033302 (2026) | ✓ **短式 DOI `10.1103/sxcl-yqs7` 有效**；Molinero E; Amorim B; Ivanov M；全对 | https://api.crossref.org/works/10.1103/sxcl-yqs7 |
| [40] | PRB 113, 045418 (2026) | ✓ **短式 DOI `10.1103/4gwm-9lpy` 有效**；Hogger W; Riedel A; Roy D；全对 | https://api.crossref.org/works/10.1103/4gwm-9lpy |
| [39] | PRB 112, 155421 (2025) | ✓ **短式 DOI `10.1103/m4x3-fb5d` 有效**；Gabriele F; Ortix C; Cuoco M；全对 | https://api.crossref.org/works/10.1103/m4x3-fb5d |
| [38] | Optica 12(10), 1606 (2025) | ✓ Koll L; Jensen S V B; van Essen P；全对 | https://api.crossref.org/works/10.1364/optica.559022 |
| [20] | Appl. Phys. B 131, 158 (2025) | ✓ Obreshkov B; Apostolova T；期刊/年/卷/文章号全对（131 卷 8 期 158） | https://api.crossref.org/works/10.1007/s00340-025-08506-y |
| [34] | PRA 109, 063109 (2024) | ✓ Andersen A; Jensen S; Madsen L；全对（η_co 截止解析式出处成立） | https://api.crossref.org/works/10.1103/PhysRevA.109.063109 |
| [12] | arXiv:2601.21273v1, 2026 | ✓ Tianchen Hu 等 11 人，首 8 位（Hu T, Li F, Huang J, Qian C, Ding R, Wang H, Liu Q, Wu Q）逐位一致；2026-01-29 提交；**无 journal_ref → 预印本著录成立** | https://export.arxiv.org/api/query?id_list=2601.21273 |
| [30] | arXiv:2507.03791v2, 2026 | ✓ Cong Zhao 等 13 人；v1 2025-07-04、**v2 2026-06-09 与著录"v2, 2026"一致**；**无 journal_ref → 预印本著录成立** | https://export.arxiv.org/api/query?id_list=2507.03791 |
| [31] | arXiv:2208.10032v1, 2022 | ✓ Shuai Wang, Xinkui He, Yueying Liang, Yabei Su, Shaobo Fang, Zhiyi Wei（6 人）逐位一致；2022-08-22 提交；**无 journal_ref → 4 年未刊属实，预印本著录成立** | https://export.arxiv.org/api/query?id_list=2208.10032 |
| [32] | arXiv:2310.17007v4, 2025 | ✓ Brown G G, Silva R E F, Jiménez-Galán Á, Goulielmakis E, Ivanov M（5 人）；**v4 2025-11-05 与著录"v4, 2025"一致**；**无 journal_ref → 预印本著录成立** | https://export.arxiv.org/api/query?id_list=2310.17007 |
| [41] | arXiv:2605.23534v1, 2026 | ✓ Pieter J. van Essen, Aday Cárdenas, Rui E. F. Silva, Álvaro Jiménez Galán, Peter M. Kraus（5 人）逐位一致；2026-05-22 提交；**无 journal_ref → 预印本著录成立** | https://export.arxiv.org/api/query?id_list=2605.23534 |
| [42] | arXiv:2610.12136v1, 2026 | ✓ Mingyao Guo 等 10 人首 8 位（Guo M, Noguchi R, Hassan M M, Gomez Alvarado S J, Gomez R M, Chan Y-J, Wen Y-C, Wilson S D）逐位一致；**2026-10-08 提交**；无 journal_ref → 预印本著录成立；提交日期与"检索截止 2026 年 9 月"声明冲突（见意见 R3-03） | https://export.arxiv.org/api/query?id_list=2610.12136 |

**正核 17 条：虚构文献 0 条；元数据错误 0 条；DOI 全部有效（含 3 条 APS 短式新格式）；6 条预印本全部确认未见正式发表版，arXiv 版本号著录（v1/v2/v4）逐条与 API 日期一致。** r1 时代 6 条虚构/错挂条目（详见 refs-xcheck-mapping-r2.md）经重写后本轮抽验**零复发**。其余 25 条（[1]–[11][13][15]–[17][21]–[29][35]–[37] 标准长式 DOI 期刊条目与气相/固体奠基经典）按限量纪律未联网正核，著录经人工目检与知名事实比对未见异常。

---

## 三、正文声称与文献内容匹配性抽查（8 条重点）

| 正文声称（位置） | 文献实际内容 | 结论 |
|---|---|---|
| rationale L29 / scheme §2.2 L53：「Korolev[26] 3–5 μm、约 1.5 TW/cm² 波长依赖标度仅在引入第一性原理动量依赖电子-声子散射率时可被定量复现，给出 5–10 fs 有效退相干时间，并指出 2–5 fs 经验值缺乏弱场光谱支撑」 | Crossref 摘要："combine wavelength-dependent HHG measurements in monolayer and bulk semiconductors with ab initio many-body calculations of electron–phonon scattering…the measured wavelength scaling of the HHG yield is **quantitatively reproduced only when** semiconductor Bloch equations incorporate **momentum-dependent dephasing derived from first principles** scattering rates" | ✓ 框架逐句对应（5–10 fs、2–5 fs 批评为正文级数值，摘要无矛盾） |
| rationale L17 / content §2.2 L19：「Brown[32] 把谐波发射按辐射跃迁所涉 Wannier 态的空间间距 ΔR 分辨，给出规范不变的带内/带间机制判别式」 | arXiv:2310.17007 摘要："physically transparent and **gauge-invariant** approach for distinguishing intraband and interband HHG mechanisms…**resolving the harmonic emission according to the separation between Wannier states inv**olved" | ✓ 逐句对应 |
| rationale L19：「Guo[42] 在 Mott 绝缘体 La₂CuO₄ 中谐波截止稳定约 4 eV 不随场强变化，截止由 Hubbard 带内禀能量尺度决定」 | arXiv:2610.12136 题名 "Dynamical many-body control of high harmonic generation in a Mott insulator"、摘要 "strongly correlated materials, where electronic excitations arise from **many-body interactions** rather than single-particle band dispersion" | ✓ 框架对应（La₂CuO₄/4 eV 为正文级数值，摘要无矛盾） |
| rationale L43：「该组王帅、贺新奎、梁玥瑛、苏亚北、方少波、魏志义等人…Keldysh 跃迁[31]」 | arXiv:2208.10032 作者链 Shuai Wang / Xinkui He / Yueying Liang / Yabei Su / Shaobo Fang / Zhiyi Wei——六人姓名逐位对应（中科院物理所团队归属成立） | ✓ |
| rationale L7/L39 / refs [27] 注：「Chen[27] MgO 800+2000 nm 合成双色场、1 MHz 重频、谱宽约 9 eV、中心 16.5 eV；三带 SBE 预测约 730 as」 | Crossref 题录 "Attosecond Pulses from a Solid Driven by a Synthesized Two-Color Field at Megahertz Repetition Rate" ✓；9 eV/16.5 eV 为正文级；**refs 挂钩注写"~700 as"与正文"约 730 as"不一致（见意见 R3-04）** | ◐ 题录一致，数值口径内讧 |
| rationale L19：「Obreshkov[20] 2–8 μm 扫描，2–3 μm 主频梳 27 阶、3 μm 以上副频梳 30–45 阶、两梳合并后 50 阶；截止与峰值场强线性」 | Crossref 题录 "High-harmonic generation in zinc oxide subjected to intense mid-infrared femtosecond laser pulse"（ZnO+MIR 主题对应）；阶次细目为正文级 | ✓（题录级） |
| rationale L61 / scheme §4.2：「Lesko[19] 为石墨烯 Floquet 拓扑态整流/光电流读出，非谐波谱学读出」 | Crossref 题录 "Optical control of electrons in a Floquet topological insulator"；正文多处显式自限"方法学对照而非固体谐波谱学先例"（rationale L63、full_review L16） | ✓ 划界诚实，无越界引用 |
| rationale L5：「观测体系从 ZnO、MgO 等宽禁带晶体[1,20,26]推广到单层 MoS₂、Bi₂Te₃ 与 NbOI₂ 等低维体系[4,11,12]」 | [4] Bai 为 **Bi₂Se₃**（非 Bi₂Te₃，Bi₂Te₃ 对应 [5] Schmid）；[26] Korolev 为单层 MoS₂/WSe₂ + 体相 CdSe（非"ZnO、MgO 等宽禁带晶体"） | ✗ **材料名与编号错配，见意见 R3-01** |

**8 条抽查：6 条匹配、1 条题录一致但数值口径内讧（R3-04）、1 条编号错配（R3-01）。**

---

## 四、引用覆盖充分性评估

- **被引最多的条目**：[9] Yue & Gaarde（反常谐波两条指纹，贯穿三章 + full_review 约 10 次）、[22] Wu（Houston 态等价性，约 8 次）、[6] Xu（子带隙缺陷态，约 7 次）、[26] Korolev（T₂ 取值基准）、[30] Zhao（Floquet 边带）、[2] Vampa、[8] Navarrete、[13] Floss 各 4–6 次。引用结构与"三通道分解→缺陷甄别→门控读出"三方向论证链匹配。
- **关键判据的引用支撑**：T₂ 同材料基准（[26]）、KP 拟合 4.19 eV 出处（[8]）、反常谐波 ~1 eV 阈值（[9]）、规范不变三判据（[28][32][33]）、偶次谐波自旋纹理判据（[39]）、Floquet 边带（[30]）、MHz 双色场先例（[27]）、气相门控谱系（[16][17]）均有对应条目。
- **无引用支撑的关键论断**：四处"据 2026 年 9 月公开文献检索尚无报道"空白声明（三角甄别、k 分辨门控、跨材料横向对照、Floquet 瞬态占据）均显式给出检索口径——处理方式正确，不属漏引；但检索口径本身与 [42] 收录时间冲突（R3-03）。
- **国内现状支撑**：[31]（中科院物理所，作者链核实）、[29]（王敢/杜桃园，中国地质大学（武汉）/华南理工）真实且归属无误；rationale §2.5 与 full_review 的"国内空白"论断有检索口径背书。
- **覆盖判断**：42 条全部被引、六个主题簇（三通道分解/Berry 反常/缺陷甄别/门控 Floquet/多尺度传播/国内外现状）各有 3–9 条支撑，无单条充数模式。**覆盖充分。**

---

## 五、意见清单

| 编号 | severity | 模块 | 位置 | 问题 | 原文摘录 | 修改建议 |
|---|---|---|---|---|---|---|
| R3-01 | high | 立项依据 | rationale L5（§1 末句） | 编号错挂两处：① 正文写"Bi₂Te₃"但所挂 [4] 为 Bai 等 **Bi₂Se₃** 表面态工作（Bi₂Te₃ 对应 [5] Schmid，未挂）；② "ZnO、MgO 等宽禁带晶体"挂 [26] Korolev，其体系为单层 MoS₂/WSe₂ 与体相 CdSe，非宽禁带晶体 | `观测体系从 ZnO、MgO 等宽禁带晶体[1,20,26]推广到单层 MoS₂、Bi₂Te₃ 与 NbOI₂ 等低维体系[4,11,12]` | 改为：宽禁带晶体 `[1,20]`；低维体系 `[4,11,12]` 中 Bi₂Te₃ 改 Bi₂Se₃（与 [4] 对齐），或补挂 [5] 写成 `[4,5,11,12]` 并保留 Bi₂Te₃ |
| R3-02 | medium | 参考文献/整篇一致性审查 | references.md L3（头部）；full_review.md L46（口径表末行） | 头部自证与实物不符：声明"本章列 **40** 条文献条目"，实际 42 条；full_review 口径表同写"参考文献 **40** 条，编号 1–40 连续无跳号…三章正文引用并集覆盖全部 40 条"——两处计数与编号范围均为 r1 旧口径，未随重写更新 | `本章列 40 条文献条目，正文 [N] 角标与条目一一对应，编号连续无跳号` | 两处同步改为"42 条…编号 1–42 连续"；full_review 口径表末行"覆盖全部 42 条"同改 |
| R3-03 | medium | 立项依据/研究内容/研究方案 | rationale L35/L39/L45/L57/L61、content §2.2/§2.3/§2.4、scheme §5、full_review L47（"检索限定"行） | 检索截止声明与实际收录条目时间不符：全文统一口径"据 2026 年 9 月公开文献检索"，但 [42] Guo 为 **2026-10-08** 提交的 arXiv 预印本（arXiv API 确认），已越截止线 | `据 2026 年 9 月公开文献检索，把缺陷密度作为可调控参数…尚无公开报道` | 统一更新为"2026 年 10 月"（全文约 8 处 + full_review 口径表同步），或在 [42] 条目尾注"（2026 年 10 月补充检索获得）"；二选一，不可两处口径不一 |
| R3-04 | low | 参考文献/立项依据 | refs [27] 挂钩注（references.md L61）；rationale L39 | 数值口径内讧：同一工作 [27] 的三带 SBE 脉宽预测，refs 挂钩注写"**~700 as**"，rationale §2.4 写"约 **730 as**"，读者无法判断何者为原文值 | `三带 SBE 数值预测 ~700 as 脉冲宽度`（refs）／`三带 SBE 数值模拟预测脉冲宽度约 730 as`（rationale） | 回 Chen 等 ACS Photonics 12, 2819 (2025) 原文核对后统一为同一数值（两处同改） |

---

## 六、结论

1. **五项对账**：占位符 0 / 死条目 0 / 超界 0 / 一号两用 0 / 断链 0——**复核确认预跑 PASS 结论准确**；区间/并列、full_review 藏引、注释行、体例自证四类易漏情形排查后均无漏报（唯一自证失实为条目计数 40≠42，见 R3-02）。
2. **元数据真实性**：联网正核 17 条（11 Crossref + 6 arXiv 预印本全查），**虚构 0、元数据错误 0、DOI 全有效**（含 3 条 APS 短式新格式）；r1 时代虚构/错挂条目经重写后零复发；6 条预印本版本号著录逐条与 arXiv API 一致。
3. **上轮遗留复核**：Calegaro[26] 虚构已根治（Korolev 真实条目 + 摘要级内容核实）；full_review 跳号未复发；r1 遗留 P0/high 经 R4 处置记录（2026-10-15）逐项确认已解决，本轮正核验证引用侧质量达标。
4. **内容匹配性**：抽查 8 条，6 条匹配、1 条数值口径内讧（R3-04）、1 条编号错配（R3-01）。
5. **意见统计**：critical 0 / high 1 / medium 2 / low 1，合计 **4 条**。
6. **需 M1 裁决的关键项**：R3-01（§1 首段材料-编号错配，改动牵动 [5] 是否补挂）；R3-03（检索截止口径全文 8+ 处联动，建议一次性批量替换）。
7. **不涉及新增引用**：本报告未建议任何新增文献；R3-01 的 [5] 补挂为既有在册条目，无池纪律风险。
