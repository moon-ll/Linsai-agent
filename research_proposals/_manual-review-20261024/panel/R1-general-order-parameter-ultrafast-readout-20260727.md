# R1 科学性评审 — general-order-parameter-ultrafast-readout-20260727（r8 后评审团轮）

评审人：R1（领域资深 PI，凝聚态/强场超快方向）｜评审日期：2026-10-29｜评审对象：`04_proposal/sections/` 四模块（rationale / content / scheme / references / full_review，monitor 0.74 版）
上游输入：`_manual-review-20261016/panel/R1-general-order-parameter-ultrafast-readout-20260727.md`（上轮 6 条，总评 0.80）、`optimizing/.../05_review/manual-revision-20261016.md`（R1 6 条 + R3 9 条 + R2 38 条全处置）、`04_proposal/params.json`（v7.2.19 口径表，13 条）、R3 本轮交叉信息（5 项，独立复核）

专项任务：逐条核对 `params.json` 13 条口径条目；对上轮 R1-01～R1-06 逐条复核「已修 / 回退」；联网反查 6 个承担判据链的量化锚；重点排查 G1/G2/G3 判据链的来源真实性、场强换算链闭合、d/g 波对称性数学。

---

## 一、专项核查（口径自洽）

### 1.1 params.json 十三条口径条目逐条判定（程序化正则匹配四模块）

| 口径条目 | stale_patterns 数 | 命中 | 判定 |
|---|---|---|---|
| citation_bai_multicarrier_hall | 2 | 0 | **保持 ✓**（rationale L45"溯源至多带输运而非反常霍尔 [35]"，Bai=[35] 正确） |
| citation_kravchuk_gwave_magnon | 2 | 0 | **保持 ✓**（content L47 / scheme L31 两处 [36] 正确） |
| citation_zhang_lswt_chiral_magnon | 1 | 0 | **保持 ✓**（content L45 Zhang=[37]；scheme L89 Yu=[39] 正确挂法未被误改） |
| citation_mizuno_spin_group_selection_rule | 1 | 0 | **保持 ✓**（content L41 Mizuno=[38]） |
| citation_werner_altermagnet_hhg | 2 | 0 | **保持 ✓**（Werner 全部 [11]：rationale L27、content L43、scheme L85/L117；scheme L45 [15] 为 Wang-Meng 正确挂法——"同作者两号并存"回归点实测无回归） |
| citation_mandal_precision_apparatus | 1 | 0 | **保持 ✓**（scheme L75"工程基线"挂 [23]） |
| numerics_chiral_magnon_splitting_27meV | 1 | 0 | **表述保持，但数值本身与原文不符 → R1-03**（canonical 所称"v1 摘要载 27(5) meV"经本轮实测证伪：v1/v2 摘要均无该数） |
| expression_sigma_design_estimate | 1 | 0 | **保持 ✓**（rationale L55"设计估值区间……第 1 年随装置信噪比标定一并定值"） |
| expression_tn_733k_measurement_caliber | 0 | — | **保持 ✓**（733(4) K 本轮联网原文摘要级证实；705—723 K 口径注在位） |
| expression_field_strength_conversion_chain | 2 | 0 | **保持 ✓**（低重频 Ø0.5–1.3 mm / 高重频 95 μm→0.80、190 μm→0.30 端点在位，换算复核闭合） |
| expression_internal_doc_reference | 1 | 0 | **带残留**（stale 精确串零命中，但 full_review L21/L23 口径表"方法学手册附录一致/方法学手册一致"两处内部文档名未随 R2-06 统一为"本项目装置参数附录"→ R1-07） |
| expression_search_timestamp_format | 2 | 0 | **保持 ✓**（"2026 年 8 月"中文格式，"2026-08"零命中） |
| expression_final_verdict_wording | 3 | 0 | **保持 ✓**（"终判"系零命中，统一"最终判定"） |

**小结：12/13 保持、1 条带残留；上轮全部编号修复无回退。** 但口径表第 7 条（27 meV）的 canonical 事实依据被本轮核验证伪（见 R1-03），属口径表自身须修正项。

### 1.2 上轮 R1-01～R1-06 逐条复核

| 编号 | 上轮 severity | 当前状态 | 复核依据 |
|---|---|---|---|
| R1-01（引用错挂 7 处） | critical | **已修 ✓** | Werner [11]×4、Kravchuk [36]×2、Mandal [23]、Mizuno [38]、Zhang [37] 全链挂对；grep 旧错挂模式零命中 |
| R1-02（σ 预研实测） | high | **已修 ✓** | rationale L55 改"设计估值区间，第 1 年随装置信噪比标定一并定值" |
| R1-03（§三.2→§三.3 指针） | medium | **已修 ✓** | scheme L35 改指"载流子加热与热损伤的可行性风险及降场强预案见 §三.3"，§三.3 L71 预案段实在 |
| R1-04（机时聚合） | medium | **已修 ✓** | scheme L77：72 方位角×2 场向=144 次变场→5–14 天，采集 24 min 相对可忽略，按 14 天/温度点编排 |
| R1-05（27 meV 折算说明） | low | **已修（数值本身另立 R1-03）** | 折算值说明半句在位，但 27(5) 括号值与 [22] 正文 27(2) 不符 |
| R1-06（T_N 口径注） | low | **已修 ✓** | 733(4) K 本轮原文摘要级证实成立（"below a Néel temperature of T_N = 733(4) K"），705—723 K 口径注在位 |

**小结：6/6 处置到位无回退；上轮 P0 #8/#9（full_review 换算链与 No-Go 行）本轮实测已闭合**（full_review L29 场强行、L38 归因分档行与正文一致）。

### 1.3 编号与死条目对账

- references 列出 [1]–[42]，连续无缺号；正文引用上界 42，无超界、无断链。上轮遗留的 Korshunov 条目已补入为 [42]（scheme L31 挂靠在位）、Rajak 为 [41]（content L63 挂靠在位），死条目零。
- 无一号两用。条目数 42 略超 40 上限（P0 #13 曾以 40 为界），属 R2/R4 风格域，不计科学性问题。

---

## 二、总评分

**总评分：0.81**（rigor 定档：五项过四 → 0.82–0.89 档下沿，因③含一条 critical 虚指压至 0.82；未达通道 B 验收线 0.82，差 0.01）

| 维度 | innovation | feasibility | rigor | expression | completeness | 总评 |
|---|---|---|---|---|---|---|
| 分数 | 0.82 | 0.76 | 0.82 | 0.80 | 0.84 | **0.81** |

### 五项核查明细（rigor 定档依据）

| 核查项 | 判定 | 依据 |
|---|---|---|
| ① 数值链一致 | ✓ | 场强链两端闭合（1.5 mJ·100 fs·Ø0.5/1.3 mm→0.76/0.29 V/Å；30 μJ·50 fs·Ø95 μm→0.80、10 μJ·30 fs·Ø190 μm→0.30 V/Å，I=½cε₀E² 复核 1.2×10¹²–8.5×10¹² W/cm²）✓；γ = √(E_g/2U_p) 端点 0.206/0.951 与"5 μm 下移 40%"✓；gμ_B·7T=0.81 meV、k_B·733K=63 meV ✓；14T÷(0.1–0.3 T/min)=47–140 min、144 次变场 5–14 天 ✓；σ×(1.5–2.0)=0.75%–1.6% ✓；M=10⁴@1 kHz=10 s→144 点 24 min ✓；g 波 𝒴₄⁻³=zy(3x²−y²) 面内 ∝ sin3φ 节点 0°/60°/120°、反节点 30°/90°/150° 与 d 波 cos2φ 节点 45°/135° 的互补扫描论证数学复核成立 ✓；B_SF≈√(2B_E·B_K) 框架正确 ✓ |
| ② 指标定义可操作 | ✓ | G1 三子判据（方向/幅度/温度旁证，旁证"不参与判定"定位明确）、G2 双判据、G3 三档双判据、FIM 7×7 与 δ/S≈1/√N、先验 3 倍文献不确定度、No-Go 出口、±B 迟滞预检与损伤阈值标定均前置第 1 年——全部可操作可证伪。R1-06 所指"幅度偏差 ≤ 10%"比对对象漂移为表述层瑕疵，判据本身仍可执行 |
| ③ 文献支撑真实 | ✗ | Tyulnev "10% 量级不确定度"无原文支撑（G1 阈值来源半数虚指，R1-01 critical）；[17] 条目 arXiv 号错挂至无关领域论文（R1-02 high）；27(5) meV 与 [22] 原文 27(2) 不符且口径表 canonical 依据被证伪（R1-03 high）；[3][4] 同为 RT-TDDFT 而"解析方法互补"定性失实（R1-04 medium）；[8] "强束缚激子"被升格为"激子凝聚"（R1-05 medium）。三处 high+ 集中在③ |
| ④ 逻辑闭环 | ✓ | 标定→探测→归因三阶段单向递进 + Go/No-Go 树 + 正反结果双出口完整；上轮 σ 时间线与指针问题已修；"磁场反转差分非零前提"三段论证（Zeeman 相消声明 + B-线性偶次通道群论把关 + ±B 迟滞预检）不留实验后解释空间。10% 虚指伤及阈值来源论证（计入③），判据链结构本身自洽 |
| ⑤ 模块自洽 | ✓ | full_review 跨章口径表 26 行与正文实测一致（上轮 P0 #8/#9 已闭合）；δ/σ/σ_prior 三符号区分四模块统一；TiSe₂ 温度旁证四文档同步。R1-07 所指 full_review 两处"方法学手册"用语残留属登记层 |

**过 4 项（①②④⑤）→ rigor 0.82（0.82–0.89 档下沿）。** 压下沿理由：③的 critical（Tyulnev 10% 虚指）直接命中 G1 资格判据的物理依据，与上轮③错挂（可 grep 修复）不同，它需要改写论证句式并三处联动；在上轮 0.80 基础上，编号错挂清零与换算链全闭合使④恢复，但新增三处文献级缺陷使③维持失败。

**分数带语境**：0.81 < 0.82（通道 B 验收线），差 0.01。修复 R1-01（改设计估值口径）+ R1-02（删/换 arXiv 字段）+ R1-03（27(2) 与口径表同步）三条后，③可恢复"过五"或至少摆脱 critical，rigor 0.84–0.86、总评 0.83–0.85，进入验收准备。

---

## 三、意见清单

[R1-01|critical] 立项依据｜§一.3 L61（联动 scheme L121、full_review L34）｜G1 阈值来源虚指：正文称"Tyulnev 实验 3/5/7 阶谐波相对强度约 10% 量级的不确定度"，本轮联网核验 [1] 摘要无此数值、R3 正文核验亦无；把自设设计阈值的依据一半挂在原文不存在的"文献不确定度"上，答辩不可守（③④）｜"该阈值由两部分合成：Tyulnev 实验 3/5/7 阶谐波相对强度约 10% 量级的不确定度（覆盖激光涨落、晶体取向与温度扫描步长等合成效应），以及本项目正演—反演流程的工程余量"｜改为："该阈值为本项目设计取值：以同类偏振分辨固体 HHG 实验中激光涨落、晶体取向与温度扫描步长等效应的典型重复性量级为经验参照，叠加正演—反演流程的工程余量合成而定；Tyulnev 等 [1] 原文未报告该不确定度数值，第 1 年 TiSe₂ 复现阶段将以实测复现精度校准该阈值的合理性。"（scheme §三.5 L121"实验不确定度量级"同步改"典型重复性量级经验参照"；full_review L34"文献实验不确定度量级"同步改"经验参照量级"。）

[R1-02|high] 参考文献｜references L47 [17] 条目｜arXiv 号错挂：arXiv:2410.05360 实为数学类流体力学论文（Guyenne 等，"A Hamiltonian Dysthe equation for hydroelastic waves in a compressed ice sheet"，J. Fluid Mech. 1002, A24），与 RuO₂ 交错磁 HHG 毫无关系；DOI（10.1103/9gv7-vhxw）与条目内容本身正确，溯源链断裂（③）｜"[17] Liu, Y. Q., Si, M. S., … DOI: 10.1103/9gv7-vhxw; arXiv:2410.05360."｜删除该 arXiv 字段、以 DOI 为唯一溯源锚（正确 arXiv 号经两轮检索未获，不得代填；定稿前在 NASA ADS 按 DOI 反查一次，查得后可补回）。

[R1-03|high] 研究内容｜§二.3 L45（联动 params.json 第 7 条、full_review L40）｜27(5) meV 与原文不符：本轮实测 [22] v1 与 v2 摘要均无 27(5)（params canonical 所称"v1 摘要载 27(5) meV"证伪），R3 正文核验值为 27(2) meV；数值与不确定度括号均需按原文落定（①③）｜"自旋波拟合给出能量劈裂 27(5) meV；该值为动量维六重劈裂经自旋波色散拟合的折算值"｜改为"自旋波拟合给出能量劈裂 27(2) meV；该值为动量维六重劈裂经自旋波色散拟合的折算值"（full_review L40 同步；params.json 该条 canonical 改为"27(2) meV（[22] v2 正文自旋波拟合折算值，动量维六重劈裂换算，能量维度受谱仪分辨率限制未直接分辨）"，stale_patterns 增补 "27(5) meV"；刊版发表后以刊版复核）。

[R1-04|medium] 立项依据｜§一.2 L23（联动 references [3] 关联注）｜"解析方法互为方法学互补"定性失实：[3] Rehn 原文摘要明示"using real-time time-dependent density functional theory"，与 [4] Ahmed 同为 RT-TDDFT，两文不构成"TDDFT vs 解析"的互补对（③⑤）｜"Ahmed 与 Rehn 等人的两组 NbSe₂ 理论研究（实时 TDDFT 与解析方法互为方法学互补）[3][4] 同样指出 HHG 对 CDW 序敏感"｜改为"Rehn 与 Ahmed 等人的两组 NbSe₂ 实时 TDDFT 理论研究 [3][4]（分别覆盖 CDW 相变前后的谐波响应预测与飞秒激光驱动模拟）同样指出 HHG 对 CDW 序敏感"；references [3] 关联注"解析理论"改"实时 TDDFT"。

[R1-05|medium] 立项依据｜§一.3 L71｜[8] 研究对象升格：原文标题与内容为"strongly bound excitons（强束缚激子）"的 HHG 谱学，非"激子凝聚（exciton condensation）"；正文把束缚态相干性的讨论对象由强束缚激子改写为激子凝聚，与条目关联注（已正确写"强束缚激子"）不一致（③）｜"激子凝聚的 HHG 响应 [8] 涉及束缚态相干性，与磁序对称破缺机制独立"｜改为"强束缚激子的 HHG 响应 [8] 涉及束缚态相干性，与磁序对称破缺机制独立"。

[R1-06|medium] 立项依据 / 研究内容 / 研究方案｜rationale §一.3 第一判据、content §二.0 G1 第二项、scheme §三.1 理论层｜"幅度偏差 ≤ 10%"比对对象三章漂移：rationale 语境为复现 Tyulnev 报道、content G1 第二项明确为"SBE 正演 vs 装置实测"、scheme L11 为复现口径，同一 10% 承载两个不同判据对象而未声明（②⑤）｜rationale §一.3"3/5/7 阶谐波偏振不对称方向与 Tyulnev [1] 报道一致，幅度偏差 ≤ 10%"｜统一为 content G1 三子判据分工：rationale 判据一末补"（幅度偏差对象为自建多带 SBE 正演预测对自建装置实测，定义同研究内容 G1 第二项）"；scheme L11 同步补半句，使复现方向判据与模型幅度判据的主语显式分离。

[R1-07|medium] 全文一致性｜full_review L21、L23｜内部文档名残留：口径表"出现章节"列两处写"方法学手册附录一致/方法学手册一致"，该文档在申请书内无对应物，scheme 侧上轮已统一为"本项目装置参数附录"，登记表未同步（上轮遗留 7 的落实）（⑤）｜"正文 §一.4、§二.3、§三.2/§三.3、方法学手册附录一致"｜两处"方法学手册（附录）"删去或改"本项目装置参数附录"；其余 24 行无此问题。

[R1-08|low] 立项依据 / 研究方案｜rationale §一.2 L27、scheme §三.2 L45｜[22] 自身波型结论未纳入争议表述：Singh v2 原文明确"Our observations unambiguously point to a g-wave altermagnetic ground-state order for CrSb"，申请书已引 [22]（T_N 与手性磁振子）却未提其 g-wave 判定，"d 波 [12] vs g 波 [30] 开放争议"的天平呈现失衡（③）；另 [22] 仍为预印本（v2 2026-05-13，journal-ref 空），R3-09 遗留续期｜"CrSb 的波型尚存 d 波分类与 g 波 dHvA 节点证认 [30] 的开放争议，本项目不单边预设"｜改为"CrSb 的波型尚存 d 波分类 [12]、g 波 dHvA 节点证认 [30] 与中子衍射磁群 g-wave 判定 [22] 之间的开放争议，本项目不单边预设"；提交前在 doi.org 复核 [22] 刊版状态。

---

## 四、量化锚核实记录

| 锚 | 申请书位置 | 核实结果 | 证据 URL |
|---|---|---|---|
| Singh [22] T_N = 733(4) K、完美补偿 Ising 交错磁、Γ-L 手性自旋分裂、J₁₁/J₁₂ 驱动 | rationale L77、content L35/L45、full_review L21 | ✅ **摘要级精确成立**（v1 与 v2 摘要均载："perfectly compensated Ising altermagnet below a Néel temperature of T_N = 733(4) K"；正文 Fig.1 说明载 J₁₁/J₁₂ 通道；Fig.3 说明载 6-fold 强度分布——Zhang [37] 预言→[22] 证实的证据链双向成立） | https://arxiv.org/abs/2511.16086 |
| **Singh [22] 能量劈裂 27(5) meV** | content L45、full_review L40 | ❌ **与原文不符**：v1/v2 摘要均无 27(5)（params canonical"v1 摘要载"证伪）；v2 摘要另载 J₁=23(4)、J₂=−5.4(8)、J₃=5.2(8)、D=0.15(4) meV 与磁振子隙 13(2) meV，均非 27；R3 正文核验值为 27(2) → R1-03 | https://arxiv.org/abs/2511.16086v1 ; https://arxiv.org/html/2511.16086v2 |
| Singh [22] g-wave 基态判定 | （申请书未引） | ⚠️ 原文明确 "unambiguously point to a g-wave altermagnetic ground-state order" + 3D-Ising 临界指数 β=0.33(5)——已引文献的关键结论被选择性省略 → R1-08 | https://arxiv.org/html/2511.16086v2 |
| **[17] arXiv:2410.05360** | references L47 | ❌ **错挂确认**：该号为数学类冰盖水弹性波论文（Guyenne/Kairzhan/Sulem，J. Fluid Mech. 1002, A24 (2025)），与 RuO₂ 交错磁 HHG 完全无关；DOI 与条目内容正确 → R1-02 | https://arxiv.org/abs/2410.05360 |
| **Tyulnev [1] "3/5/7 阶谐波相对强度约 10% 量级不确定度"** | rationale L61 | ❌ **无原文支撑**：arXiv 摘要仅泛述"anisotropic component below the CDW transition temperature"，无不确定度数值；R3 正文核验同无 → R1-01。内容锚本体（偏振不对称指纹、CDW 相以下才出现）成立 | https://arxiv.org/abs/2409.04216 |
| **Rehn [3] "解析理论"** | rationale L23、references [3] 关联注 | ❌ **定性失实**：原文摘要明示 "we predict the HHG response … using real-time time-dependent density functional theory"，与 [4] 同为 RT-TDDFT → R1-04 | https://arxiv.org/abs/2310.03080 |
| Jensen [8] 研究对象 | rationale L71 | ⚠️ 原文为 "strongly bound excitons in solids"（强束缚激子），正文写作"激子凝聚"属对象升格 → R1-05（标题级即可判定） | https://doi.org/10.1103/PhysRevA.109.063104 |
| 场强换算链（0.3–0.8 V/Å 两档四端点）与 γ 端点 | scheme L63/L65、full_review L29/L30 | ✅ 全闭合（本轮手工复算：1.5 mJ·100 fs·Ø0.5 mm→0.76 V/Å、Ø1.3 mm→0.29；30 μJ·50 fs·Ø95 μm→0.80、10 μJ·30 fs·Ø190 μm→0.30；γ=√(E_g/2U_p) 端点 0.206/0.951、5 μm 下移 40%） | 本地换算复核 |
| Osumi [32] MnTe 非高对称点分裂 0.8 eV、T_N≈307 K | rationale L79、scheme L67 | ✅ 上轮已核成立，本轮正文引用分工（0.8 eV 出自 [32] 而非 [31]）保持正确 | https://arxiv.org/html/2308.10117 |

---

## 五、结论

**剩余意见性质：文献层收尾 + 一处判据来源改写，非结构缺陷。** 本轮一条 critical（Tyulnev 10% 虚指）与两条 high（[17] arXiv 错挂、27(5)→27(2)）全部是"引用与原文的对表"问题，修复路径明确且不动摇方法学主线：①②④⑤四项完整通过，三阶段递进 + Go/No-Go 树 + 磁场反转差分的三段非零前提论证构成的方法学骨架自洽，场强/γ/机时/Zeeman 全换算链闭合。上轮 6 条全部保持、P0 #8/#9（full_review）已闭合，修订机制有效。

**建议：暂缓进入验收，先做一轮定向修补（半天至一天）。** 优先级：R1-01（G1 阈值来源改口，rationale/scheme/full_review 三处联动，是唯一需要改写论证句式的条目）→ R1-02（删 arXiv 字段，一行）→ R1-03（27(2) 数值 + params canonical 同步，两文件）→ R1-04/R1-05（两处定性改词）。完成后③可摆脱 critical，rigor 0.84–0.86、总评 0.83–0.85，过通道 B 验收线。

**两个必须提示的连带影响**：其一，R1-03 改 27(2) 后，content §二.3"预言与证实构成一条独立证据链"的定量端（Zhang [37] 预言侧数值 vs Singh [22] 证实侧 27(2)）建议在修订时补一次两侧数值的对表句，避免"证实"停留在定性；其二，R1-08 若采纳（补 [22] g-wave 判定），波型争议的表述将从"二对一"变为"d 波单极 vs g 波双证"，`正演模型预留对称性开关`（scheme §三.2）的程序化出口应同步把默认主对称性从 d 波改为"启动期磁群初判 + dHvA 校准后二择一"，以免默认值与证据天平背离被评审追问。
