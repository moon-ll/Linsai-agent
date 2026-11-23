# R1 科学性评审 — general-bsv-driven-hhg-quantum-20260726（r2）

评审人：R1（领域资深 PI，强场超快光学/量子光 HHG）｜评审日期：2026-10-29｜评审对象：`04_proposal/sections/` 四模块（rationale / content / scheme / references / full_review，r2 版）
上游输入：`_manual-review-20261016/panel/R1-general-bsv-driven-hhg-quantum-20260726.md`（上轮 9 条：major 1 / minor 8，monitor 0.85→本轮 monitor 0.87）、`optimizing/.../05_review/manual-revision-20261016.md`（R1 9 条全采纳）、`04_proposal/params.json`（v7.2.19 口径表，1 组 10 条 stale_patterns）

专项任务：逐条核对 params.json 口径条目（程序化正则匹配四章）；对上轮 R1-01～R1-09 逐条复核「已修 / 回退」；重点核查 g⁽²⁾(0)/压缩度 r/光子统计物理链、SBE-Q 多带多体表述、QEF 三维度判据可操作性；联网反查 7 个承担判据链的量化锚。

---

## 一、专项核查（口径自洽）

### 1.1 params.json 口径条目逐条判定（程序化正则匹配 rationale/content/scheme/full_review）

| 口径条目 | stale_patterns 数 | 命中 | 判定 |
|---|---|---|---|
| BSV 驱动档单脉冲光子数档位与 HHG 阈值内推 | 10 | 0 | **保持 ✓**（scheme §3.2 内推链 3 μm FWHM→7×10⁻⁸ cm²→0.035 MW→1.8 nJ→7×10⁹ 全链复算通过；联动三处"3 μm FWHM"在位；5 μm/5 nJ/2×10¹⁰/0.1 MW/π(2.5 μm)²/2×10⁻⁷ cm² 六类旧值四章零命中） |

**小结：1/1 口径条目保持，无偏离、无回退。** 上轮 R1-01（方案 b）修复完整落档且经本轮独立复算确认（π(1.5 μm)²=7.07×10⁻⁸ cm² ✓；5×10¹¹ W/cm²×7×10⁻⁸ cm²=0.035 MW ✓；×50 fs=1.75 nJ ✓；÷2.48×10⁻¹⁹ J=7.05×10⁹ ✓；1 μm 档位换算 10⁸–10¹⁰ 光子↔0.02–2 nJ ✓）。

### 1.2 上轮 R1-01～R1-09 逐条复核

| 编号 | 上轮 severity | 当前状态 | 复核依据 |
|---|---|---|---|
| R1-01（驱动档上限与内推矛盾） | major | **已修 ✓** | scheme L19 五步内推全链自洽（见 1.1）；"落在……区间内"措辞替换旧"上限"结论句 |
| R1-02（g⁽²⁾=3+1/N 适用域） | minor | **已修 ✓** | scheme L15 / content L15 双处补注"仅对单模（或模式完全收集）成立，多模 2+1/M，M 上限随基线报告" |
| R1-03（U/W≈0.5 无锚） | minor | **已修 ✓** | rationale L43 / content L49 / scheme L31 三处统一"$U/W \lesssim 0.5$（按 cRPA 方法估计的有效 U 区间）" |
| R1-04（V≥0.05 待验量写成已验量） | minor | **已修 ✓** | content L73"当 SBE-Q 正向模型在第二年给出 $Q_F$ 预测值后……落在预测区间内即视为"——时态正确 |
| R1-05（段首管道符） | minor | **已修 ✓** | scheme §3.2 零命中 |
| R1-06（Ghimire 年份分裂） | minor | **已修 ✓** | references [19] "(2011)（2010 年 12 月在线）"；rationale L7 "2011 年（2010 年 12 月在线）" |
| R1-07（T₂ 3–5 fs 空档） | minor | **已修 ✓** | content L43 / scheme L47 补"3–5 fs 中间区间按唯象退相干主方程复核路径处理，不进入首轮主窗口" |
| R1-08（Prajapati 端点数值） | minor | **已修 ✓** | scheme L89 降为"达约两个数量级……仅取其量级作为参照" |
| R1-09（1T-TaS₂ 平台绑定） | minor | **已修 ✓** | rationale L43 / content L51"低温平台（≤100 K，4 K 兼容）" |

**小结：9/9 已修且无回退。** 上轮确认表遗留项 4（full_review 旧内推数值 2×10¹⁰ 刷新）也已在本轮 full_review L45 落实为 3 μm/1.8 nJ/7×10⁹ 口径。

### 1.3 编号与死条目对账

- references 列出 [1]–[39] 连续无缺号；正文（含组合引用 [3,4]/[37,38]）引用上界 39，无超界、无一号两用、无死条目，39/39 全部有正文挂靠（程序化验证）。
- 上轮确认表"编号零增删"基线保持。

---

## 二、总评分

**总评分：0.87**（rigor 定档：五项过四 → 0.82–0.89 区间上沿；超通道 B 验收线 0.82，距 0.90 免检线差 0.03）

| 维度 | innovation | feasibility | rigor | expression | completeness | 总评 |
|---|---|---|---|---|---|---|
| 分数 | 0.88 | 0.85 | 0.86 | 0.85 | 0.87 | **0.87** |

### 五项核查明细（rigor 定档依据）

| 核查项 | 判定 | 依据 |
|---|---|---|
| ① 数值链一致 | ✗ | δ_V"高反差极限 √(2/N)"与自身完整式 δ_V=√((1−V²)/V²/N) 矛盾——V→1 代入完整式得 0，√(2/N) 对应 V=1/√3≈0.58（R1-02）；"较 Rasputnyi 峰值强度低 1–2 个量级"复算仅低 4 倍（5×10¹¹ vs 2×10¹² W/cm²，0.6 个量级）（R1-04）。其余数值链（内推五步、248 nJ、4.0×10¹⁵/mJ、10.8–20.2 eV、Zeeman 1 meV@9T、δ_q→N≥800、sinh²r、292 K 反推、1/27 光周期）全部复算通过 |
| ② 指标定义可操作 | ✓ | QEF 三维度、$Q_F$ 公式与经典极限回归 5%、No-Go（95% CI 跨零/偏差超校准不确定度两倍）、R²≥0.7+ΔAIC≥10、N_q≥800、三层降级标签——均可操作且四章同口径；Jensen 不等式上界形式书写正确 |
| ③ 文献支撑真实 | ✓ | 本轮 7 锚反查：Gothelf/Wang-dial/Jiang-Dorfman/Even Tzur-2502.09427/Lange/Lemieux/Jiang-Z 全部真实且主体表述相符（见第四节）；1 处预印本版本漂移（R1-03）与 1 dB 未核实（R1-06）属版本口径问题而非虚构 |
| ④ 逻辑闭环 | ✓ | 五环串联 + 三层降级 + 零均值场 Q_F 前提讨论（诚实且物理正确）闭环完整；R1-01 为局部表述逻辑倒置，不动摇论证链 |
| ⑤ 模块自洽 | ✓ | 跨章对照表（full_review L27–46）逐行核对成立；3 μm/1.8 nJ/7×10⁹、5% 阈值、150 mrad、q_ref∈{7,9}、四类对照四章一致；仅剩 R1-05 一处 2×10¹³ 与 2×10¹² 口径分裂 |

**过 4 项 → rigor 落 0.82–0.89 档，取 0.86。** 理由：①的两处缺陷均属局部近似/比较量级问题，核心内推链与判据阈值算术无误；上轮 9 条全修无回退、本轮 7 个文献锚无一虚构，修复机制持续有效。

**分数带语境**：0.87 > 0.82（通道 B 线）< 0.90（免检线）。修复 R1-02/R1-04（纯算术/措辞，半天工作量）并补 R1-03 版本口径后，①可过，五项全过 → rigor 0.90+，总评有望 0.90。

---

## 三、意见清单

[R1-01|medium] 研究内容｜§2.3 L57｜带隙差→"谐波阶窗口位移"的因果表述与谱峰物理不符，"分辨率之外→不产生可识别位移"逻辑倒置（扣④①）｜"带宽差值对应的谐波阶窗口位移在 q=7 阶约 8%、q=9 阶约 7%。该位移量落入典型 VUV-EUV 光谱仪分辨率（Δλ/λ~10⁻³ 至 10⁻⁴ 量级）之外，不产生可识别谱峰位移"｜8%/7% 远大于 10⁻³，若谱峰真有该位移则必然可分辨；实际物理是固体谐波峰位锁定在驱动频率整数倍 qω₀、不随带隙移动，带隙差只能进入谱形/截止/多光子共振条件。建议整段替换为："莫尔带隙（约 1.1–1.5 eV）与 SnS₂（约 2.1–2.3 eV）的带隙差折算到谐波能量标度为 ΔE_g/(qħω₀)≈5%–11%（q=7–9），但谐波峰位由驱动频率整数倍 qω₀ 锁定、不随带隙位移，故不出现谱峰移动；该带隙差以多光子共振条件与截止位置的体系间差异进入谱形，量级足够作为 SBE-Q 反演层带边位置的先验输入（反演实现路径由方案章末段承接）。"

[R1-02|medium] 研究方案｜§3.4 L61｜δ_V"高反差极限"近似与同句给出的完整式自相矛盾（扣①）｜"其完整形式为 δ_V=√((1−V²)/V²)·1/√N_fringe。高反差极限下 δ_V≈√(2/N_fringe)"｜按完整式 V→1 时 δ_V→0（I_min→0 时可见度对计数涨落不敏感），√(2/N) 实际对应 V=1/√3≈0.58。建议替换为："按 δ_V=√((1−V²)/(V²·N_fringe)) 估算（N_fringe 为条纹总计数），V≥0.6 的常用工作区 δ_V≤5% 对应 N_fringe≥800；V→1 极限下 δ_V→0，800 计数为覆盖整个工作区的保守下界。"

[R1-03|medium] 立项依据｜§1.2.2 L33｜quantum dial 驱动场强数值锚随预印本版本漂移，与现行 arXiv 版不符（扣③）｜"驱动场强 3.3×10¹⁰ W/cm²，取自 arXiv 版本"｜arXiv:2509.13518 现行 v3（2026-09-01）正文为经典驱动 E₀=3×10⁹ V/m（1.2 TW/cm²）、λ₀=3.2 μm、τ=30 fs、BSV 约 1 nJ（约 10¹⁰ 光子、E_s≈5×10⁷ V/m），未见 3.3×10¹⁰ W/cm²。建议改为："驱动场强 1.2 TW/cm²（arXiv v3，2026-09；早期版本参数有更新，数值以现行版本为准）"。MoS₂ 单层、约 5% 能量 BSV、K/K′ 谷对比响应三项表述与现行版本相符，无需改动。

[R1-04|medium] 研究方案｜§3.2 L21｜与 Rasputnyi 峰值强度的比较量级复算不符（扣①）｜"达到覆盖 TMDC HHG 阈值强度的峰值功率，较 Rasputnyi 等 [1] 原文光源参数下的峰值强度低 1–2 个量级"｜[1] 原文对照强度 2 TW/cm²（2×10¹² W/cm²），本项目阈值工作点 5×10¹¹ W/cm²，仅低 4 倍（0.6 个量级）；脉冲能量/光子数才是低约 2 个量级（1.8 nJ vs 248 nJ）。建议改为："……达到覆盖 TMDC HHG 阈值强度的峰值功率；其脉冲能量（约 1.8 nJ）较 Rasputnyi 等 [1] 原文（约 248 nJ）低约两个量级，峰值强度（5×10¹¹ W/cm²）低约 4 倍。"（后句"单脉冲光子数低约 2–4 个数量级"复算成立，保留。）

[R1-05|low] 立项依据｜§1.3 L59｜Rasputnyi 光子数口径与本文 §1.2.2/scheme §3.2 不一致（扣⑤）｜"Rasputnyi 等已用 2×10¹³ 光子/脉冲的 BSV 在固体 HHG 上验证产率提升"｜原文口径为平均光子数 2×10¹²、光子数分布覆盖 0 至 2×10¹³（尾部），本章 L25 与 scheme L21 均按"平均 2×10¹²"表述。建议改为："Rasputnyi 等已用平均光子数 2×10¹²（分布尾部达 2×10¹³）的 BSV 在固体 HHG 上验证产率提升，国内既有制备能力在该量级上具备对接基础。"

[R1-06|low] 立项依据｜§1.2.2 L29｜"约 1 dB"相对强度压缩量级无公开页证据（扣③）｜"前者产物侧可达约 1 dB 的相对强度压缩"｜arXiv:2311.10390 摘要层未给 dB 数值，arXiv 页亦未挂 Chinese Physics Letters 43, 050401 (2026) 卷期。建议降为量级表述"产物侧可达 dB 量级的相对强度压缩（数值以原文图表为准）"，并把 CPL 卷期交 R3 投稿前终核（沿用上轮 R3-04/05 遗留项机制）。

[R1-07|low] 研究方案｜§3.4 L63｜[29] 被引申承担"谐波选择规则由 Liouville 方程对称性决定"，超出其摘要可证范围（扣③）｜"该自洽性检验与开放系统谐波选择规则呼应——Liouville 方程对称性而非 Hamilton 对称性决定谐波选择规则 [29]"｜[29]（Jiang & Dorfman）核心是强场微扰展开下的孪生光束相对强度压缩，摘要无谐波选择规则/开放系统对称性内容。建议删除该呼应句或改为"[29] 给出强场 HHG 谐波与孪生光束对的相对强度压缩判据，其经典极限与 QEF 可见度回归检验同源"；若保留 Liouville 对称性表述，须换挂含该结论的原始文献并交 R3 核实。

---

## 四、量化锚核实记录（本轮 7 锚，上轮已核 3 锚不重复）

| 锚 | 申请书位置 | 核实结果 | 证据 URL |
|---|---|---|---|
| Gothelf [30] PRA 111, 063105 (2025)｜BSV 截止推高 | rationale L31、content L29、scheme L43 | ✅ 主体成立：arXiv 挂正式卷期 PRA 111, 063105 ✓；摘要"driving with thermal light or BSV produces a much higher cutoff than coherent or Fock states"✓；ZnO intraband 单带模型 ✓。"n≈13→33 阶以上"与系数式 $K_n\tilde g_0^{2n}/[(n!)^2 2^{2n}]$ 未在摘要层逐字出现（正文层未核，量级方向与摘要一致） | https://arxiv.org/abs/2502.11803 |
| **Wang quantum dial [33] 驱动场强 3.3×10¹⁰ W/cm²** | rationale L33 | ❌ **与现行版本不符**：arXiv v3（2026-09-01）正文 E₀=3×10⁹ V/m=1.2 TW/cm²、BSV ~1 nJ/10¹⁰ 光子 → R1-03。MoS₂ 单层 ✓（"We choose MoS₂…monolayer"）、约 5% 能量 ✓（"less than 5% of the classical driving energy"）、谷对比响应 ✓（§I.2 "BSV Induced Valleytronic Effects"） | https://arxiv.org/abs/2509.13518 ; https://arxiv.org/html/2509.13518v3 |
| Jiang & Dorfman [29] 孪生光束 RIS | rationale L29/L55、scheme L63 | ✅ 文献真实：arXiv:2311.10390 摘要"produce a series of relative-intensity squeezed high-order harmonic twin beams…frequencies cover a broad range"✓；⚠️ "约 1 dB"与 CPL 43, 050401 卷期未从公开页核实 → R1-06 | https://arxiv.org/abs/2311.10390 |
| Even Tzur [32] 阿秒量子态层析 | rationale L27、content L75、scheme L63 | ✅ 成立：摘要"imprint the quantum correlations of the input BSV onto…harmonics' field…reconstruction of the quantum state of the harmonics through homodyne-like tomography…squeezing in…field induced tunneling"✓；"4-缝亚周期干涉仪/反 Radon 变换/Wigner 函数"细节未逐字核（摘要层为 homodyne-like tomography，方向一致） | https://arxiv.org/abs/2502.09427 |
| Lange-Hansen-Madsen [31] Mott 激子压缩光 | rationale L33、content L53 | ✅ 成立：摘要"exciton…generates squeezing at the exciton energy…relate this nonclassical response to the nonvanishing time correlations of the current operator"——与"压缩度由电流算符双时关联函数 C(t',t'') 决定"相符 ✓；"ω≈15ω_L"具体倍数未在摘要层出现；PRL 135, 043603 卷期 arXiv 页未挂（交 R3 投稿前终核） | https://arxiv.org/abs/2503.15932 |
| Lemieux [35] ZnO 超泊松边带 | rationale L25 | ✅ 全部成立：摘要"perturb high-harmonic emission from a semiconductor with a bright squeezed vacuum field resulting in the emission of sidebands…with super-Poissonian statistics, indicating that the emitted photons are bunched" | https://arxiv.org/abs/2404.05474 |
| Jiang Z. [36] Nature 2026 钠原子 BSV 隧穿 | rationale L57、references [36] | ✅ 全部成立：摘要"A BSV light with an average pulse energy of 300 nJ achieves an effective intensity equivalent to that of a coherent light with 7.1 μJ, demonstrating a more than 20-fold quantum boost…using angular streaking"；Nature (2026) + DOI 10.1038/s41586-026-10485-9 ✓；通讯作者 Ni/Wu（华东师范大学）✓ | https://arxiv.org/abs/2604.05783 |
| （未核，额度用尽）Wang F. [34] PRA 112, 043119"小于一个原子时间单位的孤立阿秒脉冲" | rationale L57 | ○ 未反查，交 R3 引用轮核对 | — |

上轮已核锚（Rasputnyi 1.6 μm/25 fs/4–7 阶/5–15 倍/0–2×10¹³/±1 V/Å；Wu 2023 ν=1 126 meV/285 K；Ghimire 2011 卷期）本轮未重复反查，其中 Wu 2023 新增的"k_BT_c≈0.2Δ→292 K±10 K 自洽"换算本轮复算通过（0.2×126 meV=25.2 meV↔292.4 K ✓）。

---

## 五、结论

**剩余意见性质：点状缺陷，非方向性风险。** 无 critical。4 条 medium 全部集中在数值表述层（窗口位移逻辑、δ_V 极限近似、版本漂移、峰值强度比较量级），不动摇三条主线：SBE-Q 多带量子化理论的适用—失效边界结构完整；QEF 三维度 + $Q_F$ 自洽锚 + 显式 No-Go 的判据体系可操作且四章同口径；上轮 major（驱动档内推矛盾）修复经独立复算确认成立。7 个新文献锚无一虚构，国内工作（Li 时域干涉、Jiang-Dorfman、Wang 路径控制、ECNU BSV 隧穿）四条储备锚全部真实。

**建议：可进入验收准备，先做一轮半天量级的定向修补。** R1-01/R1-02/R1-04 为纯文本替换（各一处），R1-03 需按 arXiv v3 更新一个数值并注明版本，R1-05/R1-06/R1-07 为一句话级口径修正。完成后 ①数值链可过，五项全过，rigor 0.90+、总评 0.90 可达。修补时注意 R1-03 的替换数值（1.2 TW/cm²）与本文驱动档（5×10¹¹ W/cm² 量级）的量级关系表述保持"文献参照"而非"参数移植"定位，避免引入新的跨章矛盾。
