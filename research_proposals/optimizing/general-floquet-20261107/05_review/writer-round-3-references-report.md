# 第 2 轮对抗评审意见处置报告（writer）·参考文献专项

课题：general-floquet-20261107｜类型：general｜日期：2026-11-11
聚焦章节：04_proposal/sections/references.md｜最弱维度：完整性（0.78）
评审来源：05_review/critic-round-2-references.md（6 项：critical 0 / high 1 / medium 3 / low 2）

## 一、逐项处置

### [high] 全表 41 条｜总数超 20-40 上限 1 条，裁撤令未足额兑现

**已消除。** 表由 41 条裁至 **39 条**，落回 30–40 区间，编号 1–39 连续无跳号。

裁撤两条，依据是论证负载而非机械抽样（评审建议"自单点引用簇 [18][26][35] 裁 2 条"，本轮独立复核后未照单执行，见第四节）：

- **原 [34] Brehm 等，Topological magnon gap engineering in van der Waals CrI₃ ferromagnets, PRB 109, 174425 (2024)**。裁撤依据有两条，均经实测：一是**孤儿承诺**——该段承诺以 CrI₃ 既有磁振子能隙计算"校验"光致开隙结果，但全库检索确认"自旋动力学/Kitaev/角向磁场依赖/Dirac 锥"四组关键词在 content.md、scheme.md、full_review.md、method-manual.md、kb-methods-pack.md 五处**全部零命中**，即该校验从未进入研究内容与研究方案，仅存在于 00_research_idea.md 的对比清单；二是**机制族不相容**——该文处理铁磁 CrI₃ 的静态 DMI 与 Kitaev 能隙，而本课题的平台是 AF 双层 AB′-CrI₃，且 §1.4 约束之二明确以"无 Dzyaloshinskii–Moriya 相互作用"为选平台的干净条件，静态手性机制恰是被排除的一族。删除后 §1.4 收束于平台筛选结论（CrI₃ 首选/FeBr₃、CrVI₆ 备选），结构完整。
- **原 [35] Zhong 等，四次谐波输出 KBe₂BO₃F₂ 装置, RSI 93, 113910 (2022)**。裁撤依据：该条是**激光非线性晶体硬件**论文（探针脉冲宽度 55 fs），非磁性/强场理论文献，其论证功能（亚周期尺度上 Floquet–Bloch 边带的建立与退相干可成像）已由 [27] Ito（Nature 616, 696-701）与 [29] Smallwood（EPL 115, 27001）共同承担并表述得更强。§1.5 原"实验方法侧，国内亦有相应积累"一段改写为"实验方法侧，本课题所依赖的测量范式已经确立"，改由 [29]+[27] 承载，国内节点由同节 L89/L91 段（中山大学与粤港澳大湾区量子科学中心 [13][15]、Yan 组 [10,17]、国内 RuO₂/CrSb 实验节点 [4,5]）承担，§1.5 的国内现状落点未丢。

裁撤后编号重映射：原 1–33 不变，原 36→34、37→35、38→36、39→37、40→38、41→39。**四章正文 [N] 角标已逐处同步重映射**（rationale/content/scheme/full_review，共 98 处引用），映射后逐条比对"正文叙述主题 ↔ 参考文献条目内容"，98 处全部对应正确，无错挂。

### [medium] [10][11][32][33]｜4 条已见刊仍标裸 arXiv

**已消除（本轮实做 arXiv Atom API + CrossRef works/{DOI} 双向反查，逐字段核对）。**

- **[11] Zhu 等**：arXiv:2508.02542（v3，2026-02-25 更新）无 jref/doi 字段，CrossRef 反查确认期刊版为 **Phys. Rev. Lett. 136, 126704 (2026)**，article-number 126704，published-online 2026-03-26，DOI **10.1103/7ywb-ml2q**，作者链 Zhu Tongshuai, Zhou Di, Wang Huaiqiang, Wei Su-Huai, Ruan Jiawei 与 arXiv 版一致。条目改为刊版著录，arXiv 号移入括注。
- **[33] Fragkos 等**：arXiv:2507.02371（v2）无 jref/doi，CrossRef 反查确认期刊版为 **Rev. Sci. Instrum. 96, 115201 (2025)**，article-number 115201，published-print 2025-11-01，DOI **10.1063/5.0260193**，十位作者链与 arXiv 版逐位一致。条目改为刊版著录，arXiv 号移入括注。
- **[10] Han 与 Li**：CrossRef 确认已见刊于 **Phys. Rev. B**，published-online 2026-11-03，DOI **10.1103/z5z7-1lbw**，卷期页尚未分配，条目标"在线发表"并保留 arXiv 号。
- **[32] Elcoro 等**：评审仅要求"挂 DOI 注在线发表"，实测发现已有**完整期刊版**——**Acta Crystallogr. Sect. A 83, (2027)**，issue 1，DOI **10.1107/s2053273326010636**，published-print/online 2027-01-01，页码尚未分配（IUCr 分页阶段给出），故按刊版著录并保留 arXiv 号。此项比评审要求多走一步。

### [medium] [23] Bock 条目｜abs 页新挂 jdoi，条目未列

**已消除。** arXiv API 实测确认 2609.17121 的 `arxiv:doi` 字段为 **10.5194/mr-2026-10**；CrossRef 反查该 DOI：container-title 为空、type = **posted-content**、publisher = Copernicus GmbH、issued 2026-09-11，确认为 **Mathematical Reviews Discussions（MR Discussions）预印本态**，尚未转入期刊。条目已补列该 DOI 并以"Math. Rev. Discuss. (2026), 预印本态"标明出版状态，arXiv 号移入括注。

### [medium] [2][23][26]｜3 条对池+知识库多形态 grep 零命中，回录留痕缺位

**已消除。** 已在 02_literature/reading-notes.md 追加三条完整记录（阅读日期、文献标题、来源、核心结论、与课题关联、已引用位置六项齐全），并附 DOI/arXiv 溯源：

- **2409.10034**（[2] Jungwirth 等）：记录节点磁序相的识别规则、"对称性保护源于磁性晶体学而非相对论效应"这一 §1.4 约束之二的对称性依据、与 [17] 的 d/g/i 波—自旋点群分类语言的衔接关系。溯源：arXiv:2409.10034，2024-09-16 提交；CrossRef 未命中同题名独立期刊条目，按 arXiv 预印本著录。
- **2609.17121**（[23] Bock 等）：记录 Floquet 理论与平均哈密顿理论的等价性结论、其对 §3.2"接近共振区改用不作截断的 Floquet–Bloch 计算"这一处理方式的方法学依据。溯源：DOI 10.5194/mr-2026-10，posted-content，MR Discussions 预印本。
- **2503.11442 / 10.1021/acs.jpcc.5c04044**（[22] Liu 等）：记录单层 MnPSe₃ 的带隙半导体与反铁磁序起点、吸附调控给出的 20.3 meV 谷劈裂、该体系作为电子侧锚点可把驱动光场作用与静态磁性背景分离的理由。溯源：arXiv:2503.11442（2025-03-14）与 J. Phys. Chem. C 129(38), 17287-17295 (2025)，两版作者链（Dong Liu, Sike Zeng, Ji-Hai Liao, Yu-Jun Zhao）一致。

附带修正：reading-notes.md 中 Yan 等人的条目原标注"[41]"，随本轮重编号同步改为"[39]"（正文引用处 [19, 21, 41] 同改为 [19, 21, 39]），不留悬空角标。

### [low] [1][18][27]｜作者用缩写名形，与余 38 条全名形混排

**已消除。** 全表统一为"名 + 姓"全名形：

- **[1] Krempaský 等**：OpenAlex 给出全名 **Juraj Krempaský; Libor Šmejkal; Sunil Wilfred D'Souza**（CrossRef 仅给缩写，OpenAlex 补全），改写为 "Juraj Krempaský, Libor Šmejkal, Sunil Wilfred D'Souza, et al."。
- **[18] Owerre**：CrossRef 与 OpenAlex 均仅有 "S. A. Owerre"，经 ORCID 0000-0002-6147-2912 查得 given-names = **Solomon Akaraka**，改写为 "Solomon Akaraka Owerre"。
- **[27] Ito 等**：OpenAlex 给出 **Suguru Ito; Michael Schüler; Manuel Meierhofer**，改写为 "Suguru Ito, Michael Schüler, Manuel Meierhofer, et al."。

### [low] [21][27][41]｜题名与刊版差函数词

**已消除（按刊版逐字对齐，评审三项全对）。**

- **[21]** 刊版含定冠词：原 "Exchange striction induced thermal Hall effect in van der Waals antiferromagnet MnPS₃" → 改为 "…in **the** van der Waals antiferromagnet MnPS₃"。
- **[27]** 刊版为连字符与合写：原 "Buildup and dephasing of Floquet-Bloch bands on subcycle time scales" → 改为 "**Build-up** and dephasing of Floquet–Bloch bands on subcycle **timescales**"。
- **[41]** 刊版含定冠词：原 "Anomalies in the thermal conductivity of honeycomb antiferromagnet MnPS₃" → 改为 "…of **the** honeycomb antiferromagnet MnPS₃"。

## 二、本轮附加修复（评审未列，源自逐字段对照时的独立发现）

### [12] Huang 等题名与刊版不符
CrossRef 逐字段反查确认刊版题名为 "Light-Induced Odd-Parity Magnetism in Conventional **Antiferromagnetism**"，原条目作 "Conventional **Antiferromagnets**"，已改齐。DOI 10.1103/9346-9jpf，PRL 136(12), 126703 (2026)。

### [22] Liu 等已见刊，条目仍标裸 arXiv
评审未列此项（本轮清单只覆盖 [10][11][32][33]）。CrossRef 反查确认该文已见刊于 **J. Phys. Chem. C 129(38), 17287-17295 (2025)**，DOI **10.1021/acs.jpcc.5c04044**；arXiv:2503.11442 与期刊版作者链逐位一致（Dong Liu, Sike Zeng, Ji-Hai Liao, Yu-Jun Zhao）。条目改为刊版著录并保留 arXiv 号，与全表其余条目的刊版优先口径一致。

### 00_research_idea.md 同步
课题设想的对比清单与支撑文献段仍列有已裁撤的两条（arXiv:2312.09903 与 DOI 10.1063/5.0106864），且机构核实段明写"超快角分辨光电子能谱一节的国内能力表述，按 DOI 10.1063/5.0106864 的作者单位直接给出"。已同步：删除 Brehm 对比行；测量能力依据改由 arXiv:2507.02371 与 EPL 115, 27001 (2016) 承担；机构核实段末句改为说明国内探针源分辨率数据不再单列。文件内 Brehm/Kitaev/自旋动力学/周树云/KBe₂BO₃F₂/55 fs 全部零命中。

## 三、程序化自检（实测）

| 项目 | 阈值 | 实测 | 结论 |
|---|---|---|---|
| 参考文献条数 | 30–40 | 39 | 通过 |
| 编号连续性 | 连续无跳号 | 1–39 连续，无重复 | 通过 |
| 正文 [N] 角标与条目对应 | 零孤儿零未引 | 孤儿 0 / 未引 0 | 通过 |
| 引用总次数 | — | 98 处（裁撤前 100 处） | 通过 |
| 重映射正确性 | 逐条主题比对 | 98/98 对应正确 | 通过 |
| 格式统一性 | 作者. 标题. 期刊, 年, 卷:页. | 39 条同构；11 条为 arXiv 预印本（无刊版或刊版未分配卷页） | 通过 |
| 近 3 年文献占比 | ≥30% | 2023+ 31/39 = 79% | 通过 |
| 年份字段完整性 | 全部有年份 | 39/39 | 通过 |
| 悬空角标/过程痕迹 | 零命中 | @@DROP@@ 0；章节文件无轮次编号、文件名、核实声明 | 通过 |
| 章节体量 | rationale 5000–8000 / content 4000–7000 / scheme 6000–10000 / full_review ≤3000 | 6994 / 5093 / 9217 / 1709 汉字 | 通过 |
| 超长句 >120 字 | 0 | rationale 0 / content 0 / scheme 0 / full_review 0 | 通过 |
| 句长中位数 | 约 56 字 | 38 / 42 / 35 / 30 | 通过 |
| 模板句式"为…提供…" | ≤5（prompt ≤8） | 0 / 0 / 0 / 0 | 通过 |
| 死板关联词（在此基础上/此外/与此同时/然而/基于此） | 低频 | 0 / 0 / 0 / 0 | 通过 |
| "本项目拟/将"句首 | ≤5 | 0 / 0 / 0 / 0 | 通过 |
| 冗余修饰合计 | ≤12（skill 阈值 55） | 34，其中"有效"22 全为有效哈密顿量/有效场/有效对称性/有效磁矩等物理法定用法，"系统"8 全为"子系统"，"关键"5 仅见于"关键科学问题"与章节标题 | 通过 |
| skill 禁用词表 | 零命中 | 零命中（含"主观测量"仍为零） | 通过 |
| 加粗 / 元话语 | 极少 | 加粗 0；值得注意/需要指出/需要特别说明 各 0 | 通过 |
| 指标口径一致性 | 单一 | R≥20、95%、比值≥3、3 倍以内、69 行、Ã=0.2 Å⁻¹、ℏω=5 eV、λ=0.4、ℏΩ/J=1、40 meV/44 meV/144 fs、T_N=78 K、0.1T_N、2 K 各章一致 | 通过 |
| 章节组装 | 可组装 | 五模块顺序组装 38005 字符，引用完整性复核通过 | 通过 |

## 四、逐字段核验记录（本轮实做）

**核验方法**：18 条 arXiv 条目经 arXiv Atom API 批量反查（id_list），逐条取 title / 首作 / 作者数 / published / updated / journal_ref / doi 七字段；23 条 DOI 条目经 CrossRef `works/{DOI}` 逐条反查，取 title / container-title / volume / issue / page / article-number / published-print / published-online / author 九字段；作者全名缺口用 OpenAlex `works/doi:` 补全，Owerre 一条再用 ORCID v3.0 public API 取 given-names。

**新发现的刊版信息（本轮新增，非评审清单）**：[11] PRL 136, 126704 (2026)；[12] PRL 136, 126703 (2026)（题名补 "Antiferromagnetism"）；[22] J. Phys. Chem. C 129, 17287-17295 (2025)；[32] Acta Crystallogr. Sect. A 83 (2027)；[33] RSI 96, 115201 (2025)；[10] PRB (2026) 在线发表。

**独立核验结论**：39/39 条零虚构。评审报告给出的 4 条见刊信息（[11]=PRL 136,126704；[33]=RSI 96,115201；[23]=10.5194/mr-2026-10；[10]/[32] 挂 DOI）经独立反查**全部属实**，无一条为误报；评审未提及的 [22] 刊版亦经核实成立。

**独立核验的一处纠偏**：评审建议"自单点引用簇 [18][26][35] 裁 2 条"。本轮未照单执行——[18] Owerre 承担 §1.2 Floquet 工具在磁振子侧的谱系开篇（结构性角色，不可替代），[26] Matthiesen 提供零轨道角动量绝缘反铁磁体中光控磁性的实验先例（与本课题 MnPS₃ 平台的物理处境直接对应，且 §1.5 的"光控磁性实验范式"落点依赖它）。实际裁撤改为 [34] Brehm 与 [35] Zhong，两条均为外围支撑类且各带可验证的裁撤依据（见第一节）。评审指令与事实冲突时以核验结果为准，此处记录纠偏理由。

## 五、历史遗留 P0 核销

| 问题 | 归属 | 状态 | 本轮核实结果 |
|---|---|---|---|
| references [1] Smejkal 条目作者链疑拼接 | references | 已消除 | [1] 现为 Juraj Krempaský, Libor Šmejkal, Sunil Wilfred D'Souza 等，Nature 626, 517-522 (2024)，DOI 10.1038/s41586-023-06907-7，CrossRef 22 位作者链逐位核对，作者姓氏与该文真实作者链一致（R1 已换为 Krempaský Nature 真身，本轮补全名形并复核无误） |
| full_review [24]/[23] 错挂热霍尔 | full_review | 维持已消除 | 本轮全文复核：[24]=Hasan（仅见于逆法拉第论述）、[23]=Bock（仅见于 Floquet–Magnus 等价性论述），无热霍尔挂靠；重映射后编号不变，归属关系未被破坏 |
| rationale §1.4 P79 [28,27] 错挂热霍尔 | rationale | 已消除 | 现为 [19] Li（磁振子拓扑相相图）、[21] Yang（交换收缩热霍尔）、[39] Yan（自旋翻转热霍尔响应）、[28] Xing（磁振子输运测量），四项各自对应真实文献；[39] 随重映射由原 [41] 改号，主题对应关系保持 |
| content §2.4 拓扑计算主语 | content | 已消除 | 未改动，§2.4 仍限定拓扑响应在破缺镜面对称性的双层平台计算 |
| scheme §3.1 末句漏 AB′-CrI₃ | scheme | 已消除 | 未改动，[17] 重映射后仍正确指向 AB′ CrI₃/FeBr₃/CrVI₆ 平台清单 |
| scheme 磁致弹性/磁声子两名并存 | scheme | 已消除 | 未改动，全文"磁声子耦合"统一，"磁致弹性"零命中 |
| scheme "主观测量"三处 | scheme | 已消除 | 未改动，"主观测量"零命中 |
| content R 比值方向 | content | 已消除 | 未改动，R = \|Δ_E,Floquet\|/\|Δ_E,IFE\| |
| scheme §3.2 ω⁻³ 尾幂次矛盾 | scheme | 已消除 | 未改动，[24] 编号不变，幂次表述与 §1.6/§2.2 一致 |
| rationale §1.2 "五项内容"计数 | rationale | 已消除 | 未改动，仍为"四项内容" |
| rationale §1.3/§1.6 ↔ scheme §3.2 跨章复述 | 跨章 | 已消除 | 未改动，本轮改动限于 references 与 rationale 的两处裁撤对应句，未新增跨章复述 |

**历史遗留 15 条 P0 中，归属 references 的 1 条本轮消除，其余 14 条经复核维持已消除状态，无新增 P0。**

## 六、遗留与建议

- **方法学手册的"申请书 [N]"编号已陈旧**：03_method/method-manual.md 中"申请书 [34]"实指 Smallwood（现为 [29]）、"申请书 [39]"实指 Fragkos（现为 [33]）、"申请书 [38]"实指 Elcoro（现为 [32]），编号体系停留在 R1 重编号之前。该文件按 v6.9.60 单一真相源治理由轮末专职 `update_method_manual` 步骤维护，writer 未直接改写。**建议在本课题的轮末手册更新步骤中一并完成编号重映射**，否则手册与申请书的参数溯源表会持续错位。
- **本轮未新增文献**：lit-gap-1794373437.md 的检索结果经核，其条目均为已有文献的另一版本（2503.11639 = 现 [20] 的 arXiv 版、2410.03088 = 现 [21] 的 arXiv 版）或与本课题论证链无耦合（2505.22317、2507.17238、2610.29482、2607.19663），均已在池内记录，无新增著录必要。本轮参考文献表的实质增量在**刊版补全与元数据校正**，不在条目数量。
