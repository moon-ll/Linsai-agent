# R1 科学性评审 — general-ssh-weyl-20260920（r7，第四轮评审团）

评审人：R1（领域资深 PI，强场超快光学/凝聚态）｜评审日期：2026-10-29｜输入：rationale.md / content.md / scheme.md / references.md 四文件全文 + params.json（4 条口径）+ full_review.md + 上轮 R1 报告与确认表
联网核验：8 个量化锚（证据 URL 见第四节）

## 一、专项核查

### 1. params.json 口径表逐条判定（4 条全过）

| # | key | stale_patterns 命中 | canonical 落实情况 | 判定 |
|---|-----|---------------------|--------------------|------|
| 1 | Lorenzo [20] 增强量级口径 | **零命中**（7 条 pattern 含"（v1）/（v2）/增强上限为两个数量级（即/7 次谐波增强最高约"全扫） | rationale §2.2 L31 / content §2.2 L13 / §2.4 L37 / scheme §2.2 L63 / full_review §三 均为"首版 2–3 个数量级 → 第二版收敛上限两个数量级、阈值取保守下界 10²"单一口径；refs [20] 十人链 + v2 日期（2026-05-24）在位 | ✓ 维持 |
| 2 | 方向一 HOTI 计算原型表述 | **零命中**（"Bi₂Se₃ 家族 HOTI"等 3 条全扫） | rationale §2.2 L33 / content §2.1 / §2.2 / scheme §2.1/§3.1.2/§5.1 共 16 处均为"BHZ 推广模型级 HOTI（铰链态）+ Bi₂Se₃ 一阶 TI 实验参照"；研究空白处补"铋、SnTe 类候选" | ✓ 维持 |
| 3 | S_edge 阈值依据 | **零命中**（"边带量级约 0.1"等 3 条全扫） | scheme §2.2 L45 / content §2.2 L17 均为"与 Δκ 同款自定标 + 安全余量 + 正式发表后核实余量" | ✓ 维持 |
| 4 | Δt 阈值换算链 | **零命中**（"25 fs 驱动窗按三分之一/25/3/[14] 数值挂靠"全扫） | scheme §2.2 L53 / §5.2 L233 均为"30 fs 模型量级假设 × 1/3 ≈ 10 fs 自定标；25 fs 驱动窗仅作拟合时窗裕量"；[14] 无寿命数值挂靠 | ✓ 维持 |

**结论：上轮播种 4 条口径全部保持，无回退。**

### 2. 上轮 R1 意见（13 条）复核

| 上轮意见 | 裁决执行 | 本轮状态 |
|---|---|---|
| R1-01 [20] 数量级互斥（critical） | v2 收敛口径全稿统一 | ✓ 已修且维持（联网复核 v2 摘要在位，见锚 1） |
| R1-02 Bi₂Se₃=HOTI 错位（critical） | 保守改法②落地 16 处 | ✓ 已修且维持 |
| R1-03 S_edge 无源（high） | 改自定标 | ✓ 已修且维持 |
| R1-04 Δt 挂靠 [14]（high） | 改模型假设 | ✓ 已修且维持 |
| R1-05 嵌套差分路径依赖（high） | 顺序交换检验 + 操作性定义 | ✓ 已修且维持（scheme §3.2.2 L131） |
| R1-06 CFL（high）/R1-07 SBE 单式（high）/R1-08 循环论证（medium）/R1-09 refs 头注（high）/R1-10 散射时间（medium）/R1-11 T₂ 分档（medium）/R1-12 G1-δ_FP（low） | 均执行 | ✓ 全部在位（逐处核对 scheme §2.1 L29/L33、content L17、refs L3 头注 20+11+9=40 计数复核通过、scheme L133"散射参数量级约束"、L91 T₂ 五档、L67 互为补数句） |
| R1-13 超长句（medium） | 主链 8 处拆分 | ✓ 改善明显，本轮仅余零星（见 R1-06 意见级别以下不计） |

**上轮遗留项处置**：①full_review.md 旧口径——本轮已重写为 v2 口径且与四模块一致（遗留闭环）；②R1-02 改法①——维持保守改法②，无回退需求；③[20] 正文级证据——仍按"待正式发表核实"口径，可接受；④H15 自引用句式——scheme §1/§3.1.3 等处"多带 TDSE/SBE 引擎至拓扑 vs 非拓扑对照框架"等链式自指仍存（表达层，R2 域）；⑤⑥维持。

### 3. 死条目对账

refs [1]–[40] 连续、头注计数（仅 DOI 20 + 双挂 11 + 仅 arXiv 预印本 9 = 40）复核通过；四文件零 [?]/[TODO] 占位；零超界引用；本轮意见不涉及编号增删。

## 二、总评分（五项明细）

| 维度 | 分数 | 依据 |
|---|---|---|
| innovation | 0.83 | 方向三"Weyl 三因素嵌套差分 + 顺序交换检验 + TaP 实验校核"方法学创新扎实；方向一 HOTI 修复后（BHZ 推广模型 + Bi₂Se₃ 一阶参照）创新叙事成立；方向四 ZnO 对照边界标定为领域空白填充 |
| feasibility | 0.80 | 纯理论项目、引擎三类体系基准齐备、T₂ 分档 + 两类降级路径 + 弱耦合闭合条件声明均在位；σ₀/σ_full<0.05 仍无先例保证（已声明） |
| **rigor** | **0.74** | 五项核查过 2 项（①数值链 ✓：Δt 30/3、log₁₀(100)=2、X+Y+Z 嵌套公式、0.1 a.u.≈2.4 as、ZnO 激子 60 meV×50≈3 eV、refs 头注计数等主链逐一复核通过；②指标可操作 ✓：12 指标定义-阈值-统计标准齐备）｜③文献支撑 ✗：Cd₃As₂"Boltzmann 失效边界"与原文"confirm Boltzmann transport theory"冲突（R1-02）、Neufeld"激子耦合主要来源"归因摘要无源（R1-03）、Bharti-Dixit 奇/偶指纹对应错位（R1-04）｜④逻辑闭环 ✗：rationale 章内 L67"立方律约束节点贡献上限"与 L103"约束散射贡献 Z 的占比下限"互斥（R1-01）｜⑤模块自洽 ✗：rationale（L67/L103"Cd₃As₂→Z 下界"）与 content（L39"界定 Z 的上限"）跨章口径互斥（R1-01）。**过 2 项 → rigor 0.74** |
| expression | 0.82 | 上轮超长句大幅改善；余"紧绑定/紧束缚"不一致、"演化路径分为四步"实列三步等零星 |
| completeness | 0.88 | 四模块完整、12 指标—判据—年度计划—成果链闭合、full_review 骨架已同步 v2 口径、实验接口参数在位 |
| **总评** | **0.81** | 上轮 4 critical 全部维持修复、口径表零回退，稿件主链质量显著提升；剩余问题集中于方向三判据链的"约束方向"口径（一处统一即可消 3 条核查失败中的 2 条）与两处文献归因精度 |

## 三、意见清单

**[R1-01|high] rationale+content｜rationale §2.4 L67、§5(3) L103 ↔ content §2.4 L39｜Cd₃As₂ 对散射贡献 Z 的约束方向跨章互斥，且 rationale 章内 TaP 约束对象前后不一**（扣④⑤）｜"由该强度上限反推散射贡献 Z 的占比下界"（L103）vs"界定 Z 的上限（微腔近饱和区响应由场驱动非平衡动理学主导）"（content L39）；另 L67"TaP……约束节点贡献上限"vs L103"立方律……约束散射贡献 Z 的占比下限"｜统一为 content 口径并全链改写："Pilch 立方律约束弱场微扰区散射贡献 Z 的占比下限；Duan Cd₃As₂ 微腔数据界定近饱和区 Z 的占比上限（近饱和响应由场驱动非平衡动理学主导）"——rationale L67、L103、content L39、scheme §3.2.2 四处同步。

**[R1-02|high] content+rationale｜content §2.7 K3 L75、rationale §2.3 L47｜"Boltzmann 近似失效边界/Boltzmann 输运下不出现"与 Duan 原文直接冲突**（扣③）｜"该数据用于识别 Boltzmann 近似失效边界"；"该非整幂律在 Weyl 半金属（TaP 类）体系的 Boltzmann 输运近似下并不出现"｜联网核实 Duan（arXiv:2510.01760v2=刊版）摘要原文 "Our experimental results confirm the predictions by Boltzmann transport theory"——Cd₃As₂ 近饱和响应恰由 Boltzmann 输运描述。改为："该数据用于识别 Boltzmann 输运框架内弱场微扰区（严格立方律）与强场近饱和区（场驱动动理学、非整幂律）的适用边界"（content L75、rationale L47-49 同步）。

**[R1-03|high] scheme｜§3.3.1 L143 与 §4 可行性 L203｜Neufeld [6] 两处归因（激子耦合主要来源/强场多通道耦合理论）摘要无源**（扣③）｜"Neufeld 等人[6] 2023 年的《Physical Review X》也指出强场激子-HHG 耦合是非拓扑 HHG'拓扑样信号'的主要来源之一"｜联网核实 PRX 13, 031011 摘要与 Popular Summary 全文无 exciton/激子论述，其原文结论为"晶体对称性与化学性质贡献可能压过拓扑贡献"。§3.3.1 改为："Neufeld 等人[6] 2023 年指出晶体对称性与化学性质的贡献可能压过拓扑贡献，HHG-PL 双通道的竞争效应须以耦合模型而非独立通道描述处理"；§4 L203"与 Neufeld 等人[6]……的强场多通道耦合理论一致"删去或改为"与 Neufeld 等人[6]……关于非拓扑贡献可压过拓扑贡献的警示一致"。

**[R1-04|medium] scheme｜§3.2.1 L103/L105｜X（节点）→奇次、Y（曲率）→偶次的指纹划分与 Bharti-Dixit 原文"反常电流（Berry 曲率）→奇次谐波"对应错位**（扣③）｜"节点贡献对应反常奇次谐波——该选择定则由 Bharti 与 Dixit[25] 2022 年（PRB 105, 155140）提出的 Berry 曲率分量宇称选择规则所驱动"｜联网核实其 arXiv 版（2112.01745）摘要："the anomalous current due to the Berry curvature results in odd harmonics"——原文奇次谐波由 Berry 曲率反常电流产生。改法：明示"节点贡献以奇次为主导、曲率贡献在手性匹配下进入偶次"为本项目开关差分的**工作假设**（预期指纹），Bharti-Dixit 规则仅提供偏振方向-宇称对应基序；或在正文级核实 PRB 105, 155140 的奇/偶阶次-曲率宇称对应细节后保留现有挂靠。

**[R1-05|medium] rationale｜§2.4 L67（演化路径段）｜"演化路径分为四步"实际仅列举三步**（扣④）｜"整条研究脉络的演化路径分为四步。2018 年，Luu 与 Wörner……；2018–2019 年，Bauer 与 Hansen……；2024–2026 年，研究推进到……"｜改"四步"为"三步"，或补第四步（ZnO 非拓扑对照基线 2017–2025，[21][30]）使计数闭合。

**[R1-06|low] rationale｜§3 L71｜"紧绑定"与全文统一术语"紧束缚"不一致**｜"并由 Kagome 紧绑定计算报告了上限两个数量级增强"｜改"紧束缚"。

**[R1-07|low] rationale+references｜rationale §2.4 L61、refs [39] 注｜Bai [39] 摘要为"偶次谐波"（even-order harmonics），"二次谐波"未在摘要级出现**（扣③）｜"二次谐波振荡相位发生显著移动"｜联网核实 PRL 133, 243801 摘要原文 "a significant shift in the oscillation phase of the even-order harmonics"。改"偶次谐波振荡相位发生显著移动"（rationale 与 refs [39] 注述两处同步），如正文确以 2nd harmonic 为分析对象则保留但补正文级核实标注。

**[R1-08|low] full_review｜§三口径表 L31｜"首版报告二至三个数量级增强（峰值约 100 倍）"数值归属含混**（扣①）｜"Lorenzo 等人[20] 首版报告二至三个数量级增强（峰值约 100 倍），第二版收敛为上限两个数量级"｜首版 2–3 个数量级对应 10²–10³；"约 100 倍"是第二版收敛值，括注位置造成首版峰值=10² 的误读。改为"首版报告二至三个数量级（10²–10³），第二版收敛为上限两个数量级（10²）"。

**量化换算复核通过项（不计扣分）**：0.1 a.u. = 2.42 as ✓；30 fs×1/3≈10 fs ✓；log₁₀(100)=2 与 R=2 ✓；X+Y+Z=(σ_full−σ₀)/σ_full 嵌套差分自洽 ✓；ZnO 激子束缚能 60 meV 与 HHG 光子能量 3 eV 相差 50 倍 ✓；refs 头注计数 20+11+9=40 ✓；800 nm/1800 nm 双基线、0.3–1 THz 弱场窗（数十 kV/cm≈10⁶–10⁷ W/cm²，与主窗 10¹⁰–10¹¹ 不冲突）✓；TaAs/TaP 同属反演破缺 type-I Weyl 族共形参 ✓。

## 四、量化锚核实记录（联网证据，8 个）

1. **Lorenzo 2025/2026 Kagome HOTI（refs [20]，R=2 判据链核心）**：✅ 锚定成立且为当前在线状态。arXiv v2（2026-05-24，与 refs 注记日期一致）摘要原文："significant enhancements of the harmonic intensity yields, reaching up to two orders of magnitude relative to trivial phases"。作者链 10 人（Lorenzo/Batista/Jangjan/Kim/Menotti/Liu/Gao/Ghimire/Granados/Chacon）与 refs [20] 完全一致。URL: https://arxiv.org/abs/2508.15631
2. **Pilch 2025 TaP THz 立方律（refs [16]，G3 校核基准）**：✅ 完全成立。摘要原文："a perturbative cubic power-law dependence on the terahertz drive"、"multicycle narrowband terahertz pulse with a peak field strength of down to tens of kV/cm"、"Boltzmann transport theory"、"field-driven kinetics of the Weyl fermions"——申请书的"严格立方律/多周期窄带/数十 kV/cm/Boltzmann 归因"四要点全部命中。"圆偏振处为零"为正文级细节（摘要仅言 sensitive tuning by polarization），物理上与圆偏振 THG 角动量选择定则相容，风险低。URL: https://arxiv.org/abs/2508.16166
3. **Duan 2026 Cd₃As₂ 微腔（refs [26]，G3 上限约束）**：⚠ 论文真实（arXiv v2 注明 "Revised to match the published version in Nano Letters"，journal-ref Nano Lett. 26, 10554-10560 (2026) 与 refs 完全一致，作者链 10 人一致），"giant enhancement/near-saturation/field-driven kinetic"定性成立；但摘要明言 "confirm the predictions by Boltzmann transport theory"——申请书"识别 Boltzmann 近似失效边界"（content L75）与"非整幂律在 Boltzmann 输运近似下并不出现"（rationale L47）与之冲突（→R1-02）；裸膜幂指数 2.3、微腔 0.9→0.3 及 10³/10² 增强倍数为正文级数值，摘要未逐字给出，建议按机理级锚对待。URL: https://arxiv.org/abs/2510.01760
4. **Medic 2024 semi-Dirac（refs [23]，方向三方法学依据）**：✅ 完全成立。摘要原文："anomalous high harmonics are due to excitations at momenta where the dispersion is not strictly linear and that in the linearized low-energy theory the anomalous response is harmonic only"——申请书"增强源自对严格线性色散的高阶偏离而非线性化贡献"逐字吻合；journal-ref PRB 109, 205130 一致。URL: https://arxiv.org/abs/2402.12899
5. **Neufeld 2023 PRX 13, 031011（refs [6]，方向四依据）**：⚠ 论文真实、立场（拓扑签名 Probably Not、四类观测量不可靠、对称性/化学贡献可压过拓扑）与申请书引用完全一致；但摘要及 Popular Summary 全文无 exciton/激子与"多通道耦合理论"论述——scheme §3.3.1/§4 两处具体归因无源（→R1-03）。URL: https://journals.aps.org/prx/abstract/10.1103/PhysRevX.13.031011
6. **Jessen 2025 ZnO HHG-PL（refs [30]，I_threshold 基准）**：✅ 完全成立。摘要原文："an intensity-driven transition in the characteristics of the fifth harmonic, indicating a change in the underlying generation mechanism"，且"non-perturbative intensity scaling + blueshift / PL superlinear + redshift (exciton-exciton scattering)"四要素全命中申请书 content §2.5 与 refs 注述。作者链 6 人一致。URL: https://arxiv.org/abs/2508.09364
7. **Bai 2024 PRL 133, 243801（refs [39]，国内现状）**：✅ 论文真实（SIOM/上科大/张江联合，与 refs 注述一致），双色 HHG 光谱在 TSS 读出 Berry 相位效应成立；摘要级为"偶次谐波振荡相位显著移动"，"二次谐波"为正文级细节（→R1-07）。URL: https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.133.243801
8. **Bharti & Dixit 2022 PRB 105, 155140（refs [25]，T≥0.3 预估与 X/Y 指纹依据）**：⚠ 论文真实（IIT Bombay Gopal Dixit 主页出版物列表确认题名/卷期一致）；其 arXiv 版摘要："the anomalous current due to the Berry curvature results in odd harmonics, which encode the symmetry and magnitude of the Berry curvature"——宇称选择规则存在成立，但申请书 X→奇次/Y→偶次的划分与原文"曲率→奇次"的对应存在错位风险（→R1-04）。URL: https://arxiv.org/html/2112.01745v1 ；https://www.phy.iitb.ac.in/en/content/gopal-dixit

2026 年预印本（[7][8][12][13][15][17][18][37][38]）超出可核验窗口或非判据链承担者，本轮未核验，正文预印本标注完整，风险可控。

## 五、结论

上轮 4 条 critical 全部维持修复、params 口径 4 条零回退、full_review 已同步——该课题主数值链（[20] 口径/Δt/S_edge/ΔI_gap/R_HOTI）已达全链一致，是三课题中基础最扎实者。本轮剩余问题高度集中于**方向三判据链的"约束方向"口径**（R1-01 一处统一即可同时消解④⑤两项核查失败）与**两处文献归因精度**（R1-02 Boltzmann、R1-03 Neufeld——均为改写一句话级别的修复）。建议 M1 修改按 R1-01→R1-02→R1-03 顺序执行，处理完毕后该课题具备冲击 0.88+ 的条件；R1-04 建议正文级核实后定夺。
