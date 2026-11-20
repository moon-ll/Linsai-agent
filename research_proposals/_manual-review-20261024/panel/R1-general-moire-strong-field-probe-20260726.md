# R1 科学性评审 — general-moire-strong-field-probe-20260726（r3）

评审人：R1（领域资深 PI，强场超快光学/凝聚态）｜评审日期：2026-10-29｜评审对象：`04_proposal/sections/` 四模块（rationale / content / scheme / references / full_review，r3 版）
上游输入：`_manual-review-20261016/panel/R1-general-moire-strong-field-probe-20260726.md`（上轮 10 条：major 4 / minor 6，R1 总评 0.78→本轮 monitor 0.91）、`optimizing/.../05_review/manual-revision-20261016.md`（R1 10 条全采纳，R1-05 调整执行）、`04_proposal/params.json`（v7.2.19 口径表，11 条条目）

专项任务：逐条核对 params.json 11 条口径条目（程序化正则匹配四章）；对上轮 R1-02～R1-11 逐条复核「已修 / 回退」；重点核查 12,400 原子口径、扭转角-莫尔周期-原子数换算链、三层正则化反演判据、I_c 内场标度与 λ⁻² 外推；联网反查 6 个承担判据链的量化锚。

---

## 一、专项核查（口径自洽）

### 1.1 params.json 11 条口径条目逐条判定（程序化正则匹配 rationale/content/scheme/full_review）

| 口径条目 | stale_patterns 数 | 命中 | 判定 |
|---|---|---|---|
| TDDFT 全原胞计算成本（10⁶×100=10⁸ 总账） | 2 | 0 | **保持 ✓**（三章均"总账 10⁸ 核时"口径，无裸写 10⁸/11,000 原子） |
| 双层原胞原子数（12,400） | 1 | 0 | **保持 ✓** |
| 联合观测维度（240–300 / 24–50×） | 2 | 0 | **保持 ✓**（60–100 点、6–17× 旧值零命中） |
| SHG 调制实验结论（开关比>10 倍、抑制约 90%） | 1 | 0 | **保持 ✓**（">30% 调制"零命中；本轮联网复核 Shan 摘要成立，见第四节） |
| 双层原子数推导链（10-16 轮修复） | 2 | 0 | **保持 ✓**（"推得……12,400"直接推得句式零命中；三处均为"[6] 原文取值 + θ=1.1° 推算 10,800 同量级"双轨表述） |
| 单参数点核时两口径（合计 2×10⁴ / 稳态 10⁴） | 2 | 0 | **保持 ✓**（scheme §3.2.3 两尺度拆分在位） |
| 联合维度协议端点构成（18+120+100=238→240 等） | 2 | 0 | **保持 ✓**（"×4 倍权重"零命中；端点算术 238/298 闭合） |
| 单一 HHG 谱数据点口径（18 点） | 2 | 0 | **保持 ✓**（"≤22 个数据点"零命中） |
| Lian 激子-激子排斥能（30–40 meV） | 2 | 0 | **保持 ✓**（32–44/9–41 零命中，三处 arXiv v2 口径 + "正式版以原文为准"括注） |
| 靶标 A 主判据双要素 | 1 | 0 | **保持 ✓**（rationale/content/scheme 三处均双要素同口径） |
| 1.3 μm 端 I_c 外推区间 | 1 | 0 | **保持 ✓**（典型值 1.1×10¹¹–4.3×10¹¹ 全区间在位，三档称谓统一） |

**小结：11/11 口径条目保持，无偏离、无回退。** 上轮三项 major 的核心数值链本轮独立复算全部通过：θ=1.1° 几何链（L_M=12.8 nm→面积 (√3/2)L_M²≈142 nm²→38.2 atom/nm²×142≈5,400 单层/10,800 双层；12,400↔θ≈1.03°，落在"[6] 原文 θ≈1.0°–1.05°"括档内）✓；联合维度端点（238→240、298→300、240/10=24、300/6=50）✓；核时两口径（10⁶/2×10⁴=50 倍、10⁵/2×10⁴=5 倍、稳态 10⁶/10⁴=100 倍=两个数量级）✓；I_c 内场标度与 λ⁻² 外推全部五组端点复算吻合（(3/1.3)²=5.33：2.7×10¹⁰/1.1–4.3×10¹¹/1.1×10¹² ✓；(3/4.5)²=0.444：2.2×10⁹/8.9×10¹⁰ ✓）；γ=1/√2 恒等式（U_p=e²E²/4mω² 与 γ=ω√(2mΔ)/eE 联立）✓；弱场非扰动性（2×10⁸ W/cm²、n=2、m*=0.3→δW≈0.14 meV<5 meV）✓；频率判据（2ħω<E_g→λ>1.4–1.7 μm）✓；周期数（50 fs/6.7–15 fs=3–8 周期）✓。

### 1.2 上轮 R1-02～R1-11 逐条复核

| 编号 | 上轮 severity | 当前状态 | 复核依据 |
|---|---|---|---|
| R1-02（×4 倍权重残留） | major | **已修 ✓** | scheme §3.2.4 改"波长档取 4 个（联合反演在 4 档上重复执行，不改变单档维度定义）"，×4 权重全文零命中 |
| R1-03（双层原子数推导断链） | major | **已修 ✓** | rationale L13/scheme L29/content L39 三处双轨表述（[6] 取值 12,400↔θ≈1.0°–1.05°；θ=1.1° 推算 10,800 同量级），推导链与引用值显式分离，几何复算通过 |
| R1-04（单参数点核时口径冲突） | major | **已修 ✓** | scheme §3.2.3 L59 拆"合计 2×10⁴（含一次性标定分摊）/稳态增量 10⁴"两口径，[6] 10⁵ 核时注明"纯 SBE 单角，不含标定与多体项"同口径比较 |
| R1-05（端点构成 229≠240 与 ≤22 漂移） | major | **已修 ✓（调整执行）** | 端点构成改 18+120+100=238 取整 240 / 18+180+100=298 取整 300；"≤22 个数据点"全文零命中 |
| R1-06（主判据第二要素跨章缺失） | minor | **已修 ✓** | rationale L76/scheme L151 均补"且恢复时间超出载流子复合时间一个量级以上" |
| R1-07（Lian 32–44 meV 与 arXiv 不符） | minor | **已修 ✓** | 三处统一"约 30–40 meV（arXiv:2308.10799v2 摘要取值，正式版数值以原文为准）"，"蓝移 9–41 meV"已删 |
| R1-08（α≈2.5 出处） | minor | **已修 ✓** | content L81 改"由 [23] 报道的产额-强度关系在本项目拟合框架下……取值（不是 [23] 原文直接给出的拟合参数）"，±0.05 同步归属化 |
| R1-09（SBE 10² 核时收敛论证缺失） | minor | **已修但留新矛盾** | scheme L43 补收敛测试框架（50×50 起、产额变化 <5% 判据、超预算上调 10³ 档）——但预算口径"10²–10³ k 点"与自述收敛下限 50×50=2.5×10³ 内部矛盾 → 本轮 R1-02 |
| R1-10（预研/预填值时态） | minor | **已修 ✓** | content L67"均为设计预填值，待第二年末合成数据验证程序建成后回填" |
| R1-11（1.3 μm 典型值只报下界） | minor | **已修 ✓** | scheme L119/rationale L82 补全 1.1×10¹¹–4.3×10¹¹ 全区间，三档称谓统一 |

**小结：10/10 已修，其中 R1-09 的修复文本自身引入一处新的内部矛盾（见 R1-02），其余无回退。**

### 1.3 编号与死条目对账

- references 分两节：正文引用文献 [1]–[28]+[31]（28 条）+ 研读基础文献 [29][30]，合计 31 条、编号连续 {1..31}；正文引用上界 31，无超界、无一号两用、无死条目（程序化验证）。
- references 头部声明与各章实引清单（rationale L108 自报实引 26 条）经程序化交叉核对一致；[24][27] 在立项依据未引但在其余章引用，符合头注声明。

---

## 二、总评分

**总评分：0.84**（rigor 定档：五项过三 → 0.75–0.81 区间上沿 0.80；其余四维度拉升至 0.84。超通道 B 验收线 0.82）

| 维度 | innovation | feasibility | rigor | expression | completeness | 总评 |
|---|---|---|---|---|---|---|
| 分数 | 0.88 | 0.84 | 0.80 | 0.83 | 0.86 | **0.84** |

### 五项核查明细（rigor 定档依据）

| 核查项 | 判定 | 依据 |
|---|---|---|
| ① 数值链一致 | ✗ | SBE 层预算"mini-BZ 内 10²–10³ k 点、约 10² 核时/谱"与同句自述收敛下限"平带体系通常不低于 50×50"（=2,500 点>10³ 上限）矛盾（R1-02）——上轮 R1-09 修复文本自引入。其余数值链（12,400 几何链、核时三口径、联合维度端点、I_c 五组端点、γ 恒等式、λ⁻² 标度、频率/周期判据）本轮独立复算全部通过 |
| ② 指标定义可操作 | ✓ | TA 抑制>50%+恢复时间超复合一个量级（双要素三处同口径）、HHG 跳变>20%（条件性、取舍规则三分支）、Δα>0.2、莫尔势 RMS<15%、扭转角双档 ±0.02°/±0.05°–0.1°、No-Go（SNR=30 误差≥30%、I_c 超损伤阈值）均可测量可证伪 |
| ③ 文献支撑真实 | ✗ | Peterka 锚两处失准（"少数实验延伸至 H11"与原文窗口 2.7–6.2 eV÷0.62 eV=10 阶矛盾；"HHG 通道阈值约 10¹⁰ W/cm² 源自其驱动强度下端"无据——原文峰值至 5 TW/cm²、场强约 3 GV/m）（R1-01）；"DMRG/QMC 已被通用重整化群流程收敛至热力学极限偏差<3%"无文献锚（R1-03）；12,400/100×100 MP/10⁵ 核时公开文本仍不可核（R1-04）。Shan/Molinero/Ikeda/Zhao/Lian/Sun 主体全部核实为真 |
| ④ 逻辑闭环 | ✓ | 理论→反演→调控三段链路 + 第四年闭环校准 + Q1 为 Q2 前置的论证 + TBG 臂 Y1 标定/Y2 末决策早机制 + 六项风险降级路径完整；Floquet 三判据（频率/强度/周期数）与"少周期边界下仅作定性框架、定量以 SBE 全数值为准"的诚实划界成立 |
| ⑤ 模块自洽 | ✓ | full_review 跨章口径表 21 行逐行核对成立（12,400 双轨、18 点、240–300、三窗口、双档、88–352 倍、Lian/Ikeda 版本口径全部对齐）；仅 full_review L14 一处"HGG"错字（R1-07） |

**过 3 项 → rigor 落 0.75–0.81 档，取 0.80（上沿）。** 理由：上轮 4 条 major 全部修复且经本轮独立复算确认；本轮 ①③ 的缺陷均为局部点状（一处 k 点预算矛盾、两处引用归属失准、一处无锚声称），不属系统性断链；但其中 R1-01 挂在"3–11 阶 18 点"反演数据预算与"HHG 观测窗口 10¹⁰–10¹¹"两条判据链上，故不给 0.82+。

**分数带语境**：0.84 > 0.82（通道 B 线）< 0.90（免检线）。修复 R1-01/R1-02/R1-03 三条（各一处文本替换，合计半天工作量）后 ①③ 可过，五项全过 → rigor 0.90+、总评 0.90 可达。**提示**：本轮 monitor 0.91 相对 R1 独立核验偏高约 0.07，偏差主要来自 monitor 未覆盖 Peterka 锚两处失准与 k 点预算矛盾，建议以本轮 R1 清单为准做定向修补后再进验收。

---

## 三、意见清单

[R1-01|medium] 研究方案 / 立项依据｜scheme L89/L113、rationale L57｜Peterka 锚两处失准：H11 超出原文实测窗口，10¹⁰ 阈值挂靠"驱动强度下端"无据（扣③①）｜"实测谐波为 H5–H10 阶（少数实验延伸至 H11）"；"HHG 通道阈值约 10¹⁰ W/cm²，源自 Peterka 等 2023 年 [22]……所对应的驱动强度下端"｜原文（arXiv:2504.02567，APL Photonics 8, 086103 同文）实测"harmonic frequencies up to the 10th order corresponding to the photon energy of 6 eV"（窗口 2.7–6.2 eV÷0.62 eV 恰为 10 阶，11 阶=6.82 eV 超窗口上沿）；实验段驱动"peak intensity up to 5 TW/cm²"（约 3 GV/m），未见 10¹⁰ W/cm² 下端。建议：三处统一改为"实测谐波为 H3 窗口下之 H5–H10 阶（0.62 eV 驱动对应 2.7–6.2 eV 窗口，第 10 阶即窗口上沿）；单谱 18 点预算中 H5–H10 有实测锚，H3/H4 与 H11 为设计外推端（其可测性由第一项正向模型产额谱形预判）"；阈值句改为"HHG 观测窗口 10¹⁰–10¹¹ W/cm² 按本项目样品损伤预算与产额-强度曲线下沿设定，Peterka 峰值驱动（至 5×10¹² W/cm²）仅作谱窗与产额量级参照"。

[R1-02|medium] 研究方案｜§3.2.2 L43｜SBE 预算"10²–10³ k 点"与自述收敛下限 50×50=2,500 点矛盾（扣①）｜"平带体系的收敛网格通常不低于 mini-BZ 内 50×50，本项目以谐波产额变化 < 5% 为收敛判据从 50×50 起加密测试。预算按 mini-BZ 内 10²–10³ k 点、约 10² 核时/谱计"｜50×50=2.5×10³ 已超预算上限 10³。建议改为："预算按 mini-BZ 内 10³ 量级 k 点（收敛测试从 50×50=2,500 点起、以谐波产额变化 <5% 为判据加密锁定）计，该层对应 10²–10³ 核时档；主路径 tMoS₂（扭转角 1–3°，平带化弱于 magic-angle TBG）若收敛测试通过于更粗网格，则按实测收敛档下调用时。"并同步 §3.2.3 L59"SBE 约 10² 核时"为"10²–10³ 核时档"与 params 条目 canonical 措辞。

[R1-03|medium] 研究内容｜§2.2.1 L47｜"DMRG 与量子蒙特卡洛结果已被通用重整化群流程收敛至与热力学极限偏差 < 3%"无文献锚、主语含混（扣③）｜"其二，强关联子空间的 cluster 多体基准（DMRG 与量子蒙特卡洛结果）已被通用重整化群流程收敛至与热力学极限偏差 < 3%"｜同段另两条支撑（ZnO 复现 <6%、Σ-SBE 界面 <2%）均有归属，唯此条既无引用也无"本团队/文献"限定，"<3%"为硬数字。建议二择一：(a) 补挂 DMRG/QMC 有限尺寸标定方法学文献；(b) 改为"以有限尺寸标定流程外推，设计目标为与热力学极限偏差 < 3%（设计值，第三层构建时以 DMRG/QMC 基准复核）"。

[R1-04|medium] 研究方案 / 立项依据｜scheme L29、rationale L13、content L119｜"12,400 原子/100×100 MP 网格/8 轨道 Wannier/单角 10⁵ 核时"公开文本连续两轮不可核（扣③）｜"Molinero 等 2024 年在 magic-angle TBG HHG 计算中采用的双层原胞 12,400 原子……上述工作以 100×100 Monkhorst–Pack k 网格加 8 轨道 Wannier 函数求解半导体布洛赫方程（SBE），单角纯 SBE 基准约 10⁵ 核时"｜arXiv:2302.04127v1 可读部分为连续模型（Bistritzer–MacDonald 类），Methods 仅见"adapt the Wannier function model of TBG with 8 orbitals per valley"；θ_mag=1.12°、H3/H5/H7 抑制数个量级、扫描角 1.00°–1.35° 均核实，但 12,400/100×100/10⁵ 核时三参数未见于公开文本（Optica 正式版 Methods 待核）。本轮几何换算 12,400↔θ≈1.03° 与申请书括档自洽，暂不判失实。建议：在首次出现处加括注"（[6] Optica 正式版 Methods 口径；arXiv 版可读部分未含该组数值）"，并保留几何推算（θ=1.1°→10,800）作为回退表述；投稿前以 Optica 正式版完成终核，若无法证实则整组降为"按几何推算的等效规模（约 10⁴ 原子量级）"。

[R1-05|low] 研究方案｜§3.4 L133｜Zhao [31] 驱动脉冲波段：原文摘要为 near infrared，申请书写"中红外"（扣③）｜"Zhao 等 2025 年以 MgO 少周期（<10 周期）中红外脉冲驱动 HHG 实验首次直接证实 Floquet-Bloch 边带态"｜原文摘要"driven by few cycle near infrared pulses"。建议改"近红外少周期脉冲"。MgO 靶、少周期、FBS 的 HHG 直接证据、晶体取向依赖各项表述相符。

[R1-06|low] 参考文献｜references [23]、rationale L19、content L81｜Ghimire 正式卷期为 Nature Physics 7(2), 138 (2011)（2010 年 12 月在线），引用表落 (2010)（扣③）｜"Nature Physics 7(2), 138–141 (2010)"｜与 BSV 课题同源问题（该课题上轮已统一为 2011 口径）。建议 [23] 改"(2011)（2010 年 12 月在线）"，rationale §1.2"2010 年报道"行文同步。

[R1-07|low] 全文一致性｜full_review L14｜"HGG 跳变"错字（扣⑤）｜"I_c 低于窗口时 HGG 跳变不可执行"｜改"HGG"→"HHG"。

[R1-08|low] 研究方案｜§3.2.1 L37｜"莫尔计算需从'对低能带投影'转向'对全带做穷举处理'"方法学主张无引用（扣③）｜"近期莫尔多体数值方法学研究指出，莫尔计算需从……"｜建议补挂该论断的原始文献（如 [28] 类张量网络全带处理路线或相应方法学论文），或改写为"与 [28] 所代表的张量网络全带处理路线一致，本层标定涵盖全带的远程带贡献"。

---

## 四、量化锚核实记录（本轮 6 锚；上轮已核 3 锚附复用结论）

| 锚 | 申请书位置 | 核实结果 | 证据 URL |
|---|---|---|---|
| Molinero [6] Optica 11, 171 (2024)｜θ_mag、谐波抑制、**12,400/100×100/10⁵ 核时组** | rationale L13/L21、scheme L29/L45 | ○ **主体 ✓、成本组参数未核**："a strong suppression of the intensity of the odd non-linear harmonics for twist angles near θ_mag…differ by several orders of magnitude" ✓；θ=1.12°/1.22°/1.05°、扫描 1.00°–1.35° ✓；Methods"Wannier function model of TBG with 8 orbitals per valley" ✓（谷内 8 轨道）；连续模型（非原子显式）✓；**12,400 原子/100×100 MP/10⁵ 核时未见于 arXiv v1 可读文本** → R1-04 | https://arxiv.org/html/2302.04127v1 |
| Ikeda [12] arXiv:2508.00296（v2 2026-08-13）｜Sr₂CuO₃ Mott 熔化 | rationale L25/L78、scheme L133/L149 | ✅ 主体成立：摘要"intense MIR pulse induces melting of a Mott-insulator state in a one-dimensional cuprate, Sr₂CuO₃…electric-field amplitude exceeds 6 MV/cm…each harmonic frequency decreases from odd multiples of the MIR frequency…DMFT…redshifts"✓；v2 修订日期与引用一致 ✓；Δ_Mott 1.76 eV/tdDMFT 1.5 eV 未见于摘要（申请书已按"预印本/数值以正式版为准"括注，维持部分核实） | https://arxiv.org/abs/2508.00296 |
| **Peterka [22] APL Photonics 8, 086103 (2023)｜H5–H10、0.62 eV、2.7–6.2 eV、强度** | rationale L57、scheme L89/L113 | ○ **主体 ✓、两处失准** → R1-01："driving pulse of 0.62 eV (wavelength of 2000 nm)" ✓；"ultraviolet spectral region 2.7-6.2 eV" ✓；"harmonic frequencies up to the 10th order…6 eV" ✓（无 H11）；"We observe harmonic orders 5-9 at 2.8-5.5 eV"（偏振分辨档）✓；"peak intensity up to 5 TW/cm²"、"field strength of about 3 GV/m"、"25 kHz 重频、38 fs" ✓——未见 10¹⁰ W/cm² 强度下端 | https://arxiv.org/html/2504.02567 |
| Zhao [31] arXiv:2507.03791（v2 2026-06-09）｜Floquet-Bloch 边带态 HHG 指认 | scheme L133 | ✅ 成立："direct evidence of their role in high-harmonic generation spectroscopy has remained elusive. Here, we present combined experimental and theoretical evidence that FBSs can be probed by HHG emission in…magnesium oxide (MgO) driven by few cycle **near infrared** pulses"——"首次直接证实"成立；波段 near IR → R1-05 | https://arxiv.org/abs/2507.03791 |
| Shan [15] Nature 600, 235 (2021)｜MnPS₃ SHG 开关 | rationale L31（params 红线条目） | ✅ 成立："coherent on-off switching of its optical second harmonic generation efficiency on the timescale of 100 femtoseconds with no measurable dissipation. At driving electric fields of order 10⁹ V/m, the on-to-off…"（PubMed/arXiv 2206.08385 摘要，on/off 比>10 与抑制约 90% 同源），"开关比超 10 倍、抑制约 90%、100 fs、无热耗散"四要素全部相符 | https://pubmed-d.ncbi.nlm.nih.gov/34880426/ ; https://arxiv.org/pdf/2206.08385 |
| Sun [28] PRR 7, 043288 (2025)｜N~10⁹ super-moiré | scheme L55/L159、rationale L47 | ✅ 题名级成立："Self-consistent tensor network method for correlated super-moiré matter beyond one billion sites"——"N~10⁹ 量级"相符；"1D"细节与 QTCI 组合表述未深核（支撑性锚，非判据链） | https://journals.aps.org/prresearch/abstract/10.1103/PhysRevResearch.7.043288 |
| （复用上轮）Lian [19] 30–40 meV（本轮已按 arXiv v2 口径统一，零回退） | rationale L78、content L133、scheme L149 | ✅ 上轮已核 | https://arxiv.org/abs/2308.10799 |
| （未核，额度用尽）Zhou [17] 黑磷泵浦 340–440 meV vs 带隙 330 meV 划界句 | content L17 | ○ 未反查，交 R3 引用轮核对 | — |

---

## 五、结论

**剩余意见性质：点状缺陷，非方向性风险。** 无 critical。上轮 4 条 major（×4 权重、12,400 推导断链、核时口径、维度端点）全部修复且经本轮独立复算确认，11 条 params 口径零回退——该课题的修复纪律在三轮迭代中持续有效。本轮 4 条 medium 中，R1-01（Peterka 锚两处失准）与 R1-02（k 点预算自相矛盾）分别挂在"18 点反演数据预算/HHG 观测窗口"与"降阶框架算力可行性"两条判据链上，属答辩现场易被追问的位置，但均为单点文本替换可修复；R1-04 的成本组参数需一次 Optica 正式版终核闭环。

**建议：暂缓验收准备，先做一轮定向修补（半天至一天工作量）。** 修补顺序：R1-01 三处统一改写（H3/H4/H11 标注为设计外推 + 阈值句改挂样品预算）→ R1-02 k 点预算口径统一（联动 params canonical 措辞）→ R1-03 无锚声称归属化 → R1-04 加"正式版 Methods 口径"括注。完成后五项可全过（①③补齐），rigor 0.90+、总评 0.90，与 monitor 0.91 的分歧将收敛。R1-05～R1-08 四条 low 可随下一轮文字修订顺手处理。
