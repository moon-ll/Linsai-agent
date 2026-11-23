# 评审团亲审 findings · 科学内容视角（researcher）

课题：general-moire-strong-field-probe-20260726 ｜ 执行：engine 亲审 ｜ 日期：2026-10-03
方法：通读 5 章节全文；数值逐项复算；关键文献以 knowledge/wiki/papers 与 knowledge/raw/pdfs/_text_cache 按条目核对；不调用外部 LLM/CLI。历史问题对照 05_review/critic-round-8-*（R8 为最近一轮评审）。

## 问题清单

**SR-1 [critical] 全原胞 TDDFT 核时跨章两口径互斥（R8 critical 复发未清）**
- 位置：content.md L49 vs rationale.md L13/L89、scheme.md L21、full_review.md 统一口径表 L45
- 摘录：content L49"按莫尔原胞 ~6,200 原子 × 100 时步 × 100 轨道态估算，单参数点 ≥10⁶ 核时……有三个数量级以上的差距"；rationale L89"从 ≥10⁸ 核时降至约 2×10⁴ 核时"
- 问题：同一指标（全原胞 TDDFT 单角/单参数点核时）rationale/scheme 记 ≥10⁸、content 记 ≥10⁶。且按 ≥10⁶ 基准，2×10⁴ 对 10⁶ 仅 50 倍（1.7 个量级），"三个数量级以上"宣称在其自报口径下不成立；口径表该行三列均写 ≥10⁸，content 正文与自家骨架表互斥。
- 建议：content L49 改按双层原胞 ~11,000 原子估算（11,000×100×100 = 1.1×10⁸，自洽闭合），统一为 ≥10⁸ 核时，并与 rationale"比 SBE 高至少 10³ 倍"注明同口径。

**SR-2 [high] 莫尔原胞原子数三口径（11,000 / 6,200 / 12,400，R8 high 复发未清）**
- 位置：rationale.md L13、scheme.md L21 vs content.md L43、content.md L145
- 摘录：content L43"莫尔原胞含约 6,200 个原子。按……原胞面积 164 nm² 推得，TBG 双层口径约 12,400 原子"；rationale L13"莫尔元胞含碳原子数约 11,000"
- 问题：三值并存。几何复核：莫尔原胞为三角布拉维格子，原胞面积应为六角面积 (√3/2)L_M² ≈ 142 nm²（content 的 164 nm² 误用 L_M²），按 38 atom/nm² 得单层约 5,400、双层约 10,800 ≈ 11,000——恰与 [6]（Molinero）计算采用的 11,000 原子原胞一致（rationale L13、scheme L21 所引即此值）。
- 建议：全链统一"单层约 5,400、双层约 11,000（与 [6] 原胞同口径）"，修正 content 的 164 nm² 面积口径。

**SR-3 [high] 损伤阈值误挂 Peterka [22]（R8 rationale high#4 后半复发）**
- 位置：content.md L29
- 摘录："tMoS₂ 损伤阈值约 10¹² W/cm²，依据 Peterka 等 2023 年在 *APL Photonics* 上报告的单层 MoS₂ 实验值 [22]"
- 问题：R8 已对该文 web 实查——报告的是 H5–H10 谐波实测与驱动强度，无 10¹² W/cm² 损伤阈值数据；引用失实属 rigor 红线。
- 建议：改标"工程化估算量级，精确值由 Y1 样品对接阶段实测标定"，删除 [22] 挂靠（scheme L129 无挂靠、口径表行名"单层 MoS₂ 实验值，异质结 Y1 实测"同步微调）。

**SR-4 [high] Peterka 截止阶次 scheme 两处残留旧值 7–11 阶（R8 rationale high#4 前半未同步）**
- 位置：scheme.md L65、L85 vs rationale.md L57（已改 H5–H10）
- 摘录：scheme L65"实验标定 MoS₂ 单层 HHG 截止阶次为 7–11 阶 [22]"；L85"截止阶次 7–11 阶所对应的驱动强度下端"
- 问题：同一文献同一观测量两章两值（H5–H10 vs 7–11 阶），R8 明确要求"同步 scheme 两处"。
- 建议：scheme 两处改"实测谐波为 H5–H10 阶（少数实验延伸至 H11）"。

**SR-5 [high] rationale No-Go 括注 1.3 μm 端典型值 4.3×10¹¹ 与 scheme 三端点无对应（R8 content high#3 复发）**
- 位置：rationale.md L83 vs scheme.md L89
- 摘录：rationale L83"按方案章 §3.3.2 工程化标定的 1.3 μm 端典型端 4.3×10¹¹ W/cm²"；scheme L89"典型端约 1.1×10¹¹ W/cm²"
- 问题：scheme 端点（2.7×10¹⁰ / 1.1×10¹¹ / 1.1×10¹²）经 R7/R8 复算闭合，rationale 的 4.3×10¹¹ 是旧值残留，跨章互斥。
- 建议：rationale 改"1.3 μm 端典型值约 1.1×10¹¹ W/cm²"。

**SR-6 [medium] 自由参数压缩比两口径：content"减少约 2/3"（12–24→4–8）vs scheme"6–10 实参数"**
- 位置：content.md L63 vs scheme.md L53
- 摘录：content L63"将自由参数减少约 2/3"；scheme L53"莫尔势的有效自由度下降到约 6–10 实参数"
- 问题：12–24 的 2/3 为 4–8，与 scheme 的 6–10 不一致（R7 起方案章已定为 6–10，冗余度 24–50× 按此闭合）。
- 建议：content 对齐 6–10，并挂 §3.2.4。

**SR-7 [medium] §3.2.4 联合维度算术残留一跳（R8 scheme critical#1 的残余）**
- 位置：scheme.md L53
- 摘录："（HHG 谱 ~22 点、椭偏依赖扫描 ~30 角度步、TA ~15 时延点；在不同扫描档位组合下叠加可达 240–300 上限）"
- 问题：22+30+15=67 与 240–300 之间靠"组合叠加"一句带过，组合因子未量化；240–300 对有效自由度 6–10 的 24–50× 冗余本身闭合，矛盾只在括注内部。
- 建议：括注显式写"单档合计 ~67 点；叠加多波长工作点与椭偏×时延二维扫描档位后达 240–300 量级"（平台 1.3–4.5 μm 多工作点为 §3.3.2 既有设计，不引入新数值）。

**SR-8 [medium] 弱场非扰动估算量纲链不可复算且机制名实不符**
- 位置：scheme.md L87
- 摘录："按 Pockels 效应估算：δW_flat = αE₀²/2。其中 α 取 TMDC 层极化率 ~10⁻⁹ esu，V_Moiré ≈ 10⁴ cm²/V。代入……得 δW ≈ 0.6 meV"
- 问题：esu 极化率与 cm²/V 量纲组合无法复算出 0.6 meV；"Pockels 效应"（χ² 线性电光）与 αE₀² 二阶 Stark 机制名实不符。结论方向（≪5 meV）稳健：按假设 3 已建立的抖动能量标度（U_p ≈ 9.33×10⁻¹⁴·I·λ²，内场 /n²，m* 0.3–0.6 mₑ），I = 2×10⁸ W/cm²、λ = 3 μm 对应 δW_flat ≈ 0.02–0.1 meV，仍远低于 5 meV。
- 建议：改挂与假设 3 同式的抖动能量标度核算（公式已在正文建立，自洽、可复算），结论不变。

**SR-9 [medium] 创新点 2 复述"12–24 vs ≤22"欠定论证（跨章复述残留）**
- 位置：content.md L151 vs rationale.md L57（单一出处）、content.md L59（既有指针）
- 摘录："单一 HHG 谱反演莫尔势是欠定逆问题，莫尔势 12–24 个实参数 vs 单一 HHG 谱 ≤22 个数据点……"
- 问题：该论证单一出处已在立项依据反演空白段，content L59 已设指针，L151 再展开一次，属"单一出处+指针"纪律残留。
- 建议：L151 收敛为指针。

**SR-10 [low] "5×10⁸–10¹⁰ 段"整句跨章逐字重复（R8 full_review medium 残留）**
- 位置：content.md L89 vs scheme.md L85（逐字同句）
- 建议：scheme 表后句保留（§3.3.2 为强度窗口数值单一出处），content 侧改写并挂 §3.3.2。

## 引用真实性抽查与公式复算（核实记录）

- [12] arXiv:2508.00296：全文缓存（knowledge/raw/pdfs/_text_cache/2508_00296.txt）标题 *High-harmonic generation during ultrafast melting of a Mott insulating state*、前三作者 Ryohei Ikeda / Yuta Murakami / Daiki Sakai，与 references 条目一致；正文两处锚点（Δ_Mott ≈ 1.76 eV 为 σ 谱 CT 峰、tdDMFT 260 K 给 ≈1.5 eV）与 KB 深读页（wiki/papers/2025-2508_00296-tracking-doublon-holon-dynamics-…）逐字吻合。"红移归因亚周期 Mott 熔化"表述与 KB 结论一致。核实通过。
- [27] Kumar 等 *Supermoiré-Trapped Quadrupolar Exciton*：KB 深读页（wiki/papers/2025-2607_22532-supermoiré-trapped-quadrupolar-exciton.md）在库，δ ≈ 11.5 meV 与"扭转角失配下仍稳定"表述与 scheme §3.5 引用一致。核实通过。
- [29] arXiv:2510.09548、[30] arXiv:2410.22277：KB 均有论文页；[30] 经 R8 引用专项 web 反查已见刊 Nature 650(8103), 875–881 (2026)，建议换正式版（另列 RV-3）。
- [6][15][25][14][3][22] 六条 R8 轮 web 实查通过；[28] APS 短 DOI 10.1103/krjp-mn4v 经 R8 反查为真身（PRR 7, 043288），勿判虚构。27 条 DOI 在 R8 全量 doi.org 反查"零虚构、零错挂"，本轮不重复下结论。
- 公式复算：L_M = a₀/(2sin(θ/2)) → 12.8 nm ✓；Keldysh γ 在 δW_flat = Δ_CI 处 = 1/√2 恒立（与波段无关）✓；λ⁻² 三端点 2.7×10¹⁰ / 1.1×10¹¹ / 1.1×10¹² ✓；ħω = 0.95–0.27 eV（1.3–4.5 μm）✓；88–352 倍 / 75–300 倍端点 ✓；40 倍端点比（n_eff⁴ × m*² × Δ_CI⁴）✓；重频 100 kHz = 2 个数量级增益 ✓。
- 创新增量：点 1（ΔΣ(ω) 多体项 vs [6][8] 均无多体、且 [8] 自认开放问题）成立；点 2（多观测联合反演 vs [13] 单一几何量、均匀体系）成立；点 3 相对 [12] 的"周期调制 vs 单脉冲熔化、Δ_CI 低约 2 个量级"划界成立（[12] KB 页证实其机制为单脉冲熔化+红移读出）。创新增量总体成立。
- 待核项（不虚构结论）：[4] Matter 2025、[9] Nat. Mater. 2024、[10] npj Quantum Mater. 9, 90、[16] PRB 109, 054424、[21] Photonics Res. 2025 在 KB 无对应论文页，本轮按 R8 doi.org 全量反查结论采信，标记"待核（R8 已查）"。
