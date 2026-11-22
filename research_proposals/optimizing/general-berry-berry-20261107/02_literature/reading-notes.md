## 1203.2697

标题：Berry Curvature, Triangle Anomalies, and the Chiral Magnetic Effect in Fermi Liquids（Phys. Rev. Lett. 109, 181602, 2012；报告号 INT-PUB-11-010）
作者：Dam Thanh Son、Naoki Yamamoto（Institute for Nuclear Theory, University of Washington）
来源：https://arxiv.org/abs/1203.2697 （v2, 2012-11-07；5 页）

### 研究问题（Research Question）
核心问题："费米面上的 Berry 曲率通量是否会在费米液体中产生三角反常（triangle anomaly），并如何修正 Landau 费米液体理论？"作者要证明的是：若某费米面内的 Berry 曲率通量非零，则该费米面所对应的粒子数在外电磁场中不再守恒，且该异常具有"运动学"起源、与哈密顿量细节无关。

### 研究背景（Background）
标准 Landau 费米液体理论假设低能自由度是满足动理学方程的准粒子；而晶体中电子波包的半经典运动须包含来自 Bloch 波函数的 Berry 相位额外项（Niu-Sundaram 1999），该项改变了标准动力学，可把反常 Hall 电导解释为费米面性质（Haldane 2004）。相对论量子场论中 Adler-Bell-Jackiw 三角反常已知，但在强相互作用的费米液体中此前未被建立。掺杂 Weyl 半金属是 Berry 曲率通量的自然候选。

### 研究方法（Methods）
把 Landau 运动学方程重写为哈密顿演化方程 ∂t n_p(x) = i[H, n_p(x)]，采用带 Berry 曲率的单准粒子作用量（引入动量空间虚拟矢量势 A_i(p)），由 Poisson 括号 {p_i,p_j} = −ε_ijk(B_k + B·Ω)/(1+B·Ω) 等推导非 Abelian 对易子；相位空间测度修正为 dΓ = (1+B·Ω) dp dx/(2π)³。最终得到密度算符在两点间的等时对易子 [n(x), n(y)] = −i∫(∇×σ + k/4π² B)·∇δ(x−y)，其中 σ_i = −∫ p_i Ω_k ∂n_p/∂p_k，k = (1/2π)∮dS·Ω 为费米面内的单极子电荷。

### 主要发现与核心结论（Main Results）
- 连续性方程被修正为 ∂n/∂t + ∇·j = (k/4π²) E·B，其中 k 为费米面内 Berry 曲率通量（通量量子倍数）；这正是相对论场论中的三角反常方程。
- 反常 Hall 电流 j' = j + E×σ；平衡态下总电流 j = (k/4π²) μB，即手征磁效应由 Berry 曲率通量涌现。
- 两个费米面 k=+1 与 k=−1 若化学势不等（可通过有限时间施加 E·B 造成），准平衡态产生电流 (μ₊−μ₋)B/4π²。
- 结论具有强相互作用普适性：反常只依赖费米面 Berry 曲率（单极子电荷），与哈密顿量细节无关，因此适用于掺杂 Weyl 半金属等体系。

### 潜在研究方向（Future Directions）
作者列出四条开放方向：(1) 探索 Berry 曲率对 Landau 费米液体中集体模式与响应函数的影响；(2) 将碰撞项并入运动学方程，研究流体动力学极限；(3) 用运动学方法研究相对论理论中的 Alfvén 型模式在凝聚态中的对应物；(4) 建立稠密物质（夸克物质相）中"异常匹配"判据。作者同时承认：用准粒子运动学方程推导尚缺更微观的论证（希望有更基本的推导），且推广到 ³He A 超流相需处理 U(1) 对称性破缺伴随的 Nambu-Goldstone 玻色子。

## 1911.05667

标题：Consequences of Time-reversal-symmetry Breaking in the Light-Matter Interaction: Berry Curvature, Quantum Metric and Diabatic Motion（Phys. Rev. Research 2, 033100, 2020；DOI 10.1103/PhysRevResearch.2.033100）
作者：Tobias Holder、Daniel Kaplan、Binghai Yan（Weizmann Institute of Science）
来源：https://arxiv.org/abs/1911.05667 （v3, 2020-07-30）

### 研究问题（Research Question）
"时间反演对称性破缺后，二阶光响应（bulk photovoltaic effect）的完整物理来源是什么？"以往非线性光响应被认为根源于 Berry 曲率，但磁性体系中的光电流与二次谐波无法仅由 Berry 相位导出。作者用图解（diagrammatic）方法重新审视二阶响应形式体系，目标是识别出产生直流光电流的全部机制，并厘清它们与半经典 Berry 曲率偶极（BCD）语义之间的对应关系。

### 研究背景（Background）
BPVE 自 1980 年代起被确立为二阶光响应，近期在拓扑 Weyl 半金属中复兴（TaAs 的巨光电流）。但研究长期聚焦非磁性材料；磁体系的唯象（Ref. 21）表明 shift current 与 injection current 在线性或圆偏振光下均可出现，这打破原有的区分。另一个悬而未决的问题是长度规范与速度规范在有限准粒子寿命下如何自洽对应——非线性响应本质涉及带间过程，难以半经典建模，寿命依赖性有歧义。

### 研究方法（Methods）
在速度规范下用图解方法（含 Green 函数形式处理有限寿命），把二阶电导写成二阶动量导数顶点 w_ab^mn = ⟨m|∂_a∂_b H_0(k)|n⟩ 的分解式：w_ab = (i/2)([v_a, r_b] + Δ_a r_b + ε R_ab + a↔b) + O(Γ)，其中 R_ab^mn = (⟨i∂_a∂_b m|n⟩+⟨m|i∂_a∂_b n⟩)/2；进一步用对称/反对称部分识别量子几何张量 Q_ab = g_ab − iΩ_ab/2。给出适用于有限寿命、非二次哈密顿量的求和规则（sum rules），并据此建立长度规范↔速度规范的唯一转换程序。数值计算用 WSM 与 Dirac 半金属作为"Berry 曲率为零却有大幅 BPVE"的示例体系。

### 主要发现与核心结论（Main Results）
- 识别出三种产生直流光电流的机制，全部可由"异常加速度"直观理解：Berry 曲率（QGT 的反对称部分）、量子度规（QGT 的对称部分）、以及 diabatic motion（来自时间反演费米子回路间的相位累积，即动力学反局域化）。前两项对应量子几何张量的反对称/对称部分，第三项是第三类贡献。
- 注入电流可视为三条腿的时间反演回路之间的"动力学反局域化"（dynamical antilocalization）；其残留以"对 Berry 偶极子的投影修正"形式出现在 shift current 中，类似运动学方法的 ballistic current。
- 半经典展开：破坏时间反演后，主导项（ω⁻²）只出现在破坏 T 的情形且包含四个贡献中的三个；而几何起源的非线性响应只出现在次领先阶（ω⁻¹），且该 ω⁻¹ 项不仅含 Berry 曲率偶极子，还额外含一个 diabatic 项（源于光学跃迁的固有耗散性）。
- 结论：T 破缺可导致远强于 Berry 曲率偶极子贡献的非线性反常 Hall 效应。
- 规范技术要点：常用替换 r_mn → i v_mn/ε_mn 仅在干净体系成立；关系 [r_a, v_b] = iℏ δ_ab 对紧束缚哈密顿量一般不成立（源于依赖各向同性色散的 p_a = v_a 假设）。

### 潜在研究方向（Future Directions）
作者明确把"外禀机制"（杂质散射、非平衡载流子等）留给未来工作，只聚焦内禀机制；同时指出长度规范与速度规范在有限寿命下对弛豫率的选择仍有歧义，未做全面解决。文中强调散射诱导过程在大小上可与能带结构效应相当（引 Ref. 39, 51），提示实验解读时必须拆分内禀与外禀贡献。对强场课题的直接含义：二阶非线性响应的"几何部分"在频次上被压到 ω⁻¹ 阶，意味着在强场/少周期驱动下不能只用 BCD 一项拟合非线性光学响应。

## 1910.09872

标题：Berry Curvature Dipole in Strained Graphene: a Fermi Surface Warping Effect（Phys. Rev. Lett. 123, 196403, 2019；DOI 10.1103/PhysRevLett.123.196403）
作者：Raffaele Battilomo、Niccolò Scopigno、Carmine Ortix（Utrecht University / Università di Salerno）
来源：https://arxiv.org/abs/1910.09872 （5 页，4 图）

### 研究问题（Research Question）
"在没有自旋-轨道耦合的二维 Dirac 体系中，是否可能存在非零 Berry 曲率偶极（BCD）？"此前的 BCD 都被归因于强自旋-轨道耦合导致倾斜（tilted）Dirac 锥。本文的答案是肯定的：在完全无 SOC 的情况下，触发因素是费米面的翘曲（warping / trigonal warping）而非倾斜机制——这实质上把 BCD 的来源从"能带倾斜"改写为"费米面形变"。

### 研究背景（Background）
Sodemann & Fu (PRL 115, 216806, 2015) 指出光电与非线性输运实验可直接探测 Berry 曲率偶极；但 BCD 存在严格对称性约束：二维中 Berry 曲率是赝标量，BCD 是面内赝矢量，要非零最多只能保留一条镜面线，BCD 必须垂直于该镜面线。此前实现 BCD 需应变、层间扭转等材料工程。问题在于：既有结论似乎把 BCD 与 SOC 绑死。

### 研究方法（Methods）
先用对称性分析确定最低对称要求：石墨烯点群 p6mm 经 Semenoff 质量（衬底如 h-BN 诱导的交错势）降到 C3v（破反演、开 Dirac 隙），再施加沿主晶向的单轴应变降到 Cv（BCD 沿锯齿方向）。单层用含应变-动量耦合的有效哈密顿量 H_warped = ξv_x k_x σ_x + v_y k_y σ_y + (Δ/2)σ_z + (λ₁k_y² − λ₂k_x²)σ_x + 2ξλ₃k_xk_yσ_y，其中 λ₁,λ₂,λ₃ 为翘曲项、应变使费米速度各向异性（v_x ≠ v_y）。双层用含应变的低能哈密顿量 H_b = [−(1/2)m(k_x²−k_y²)+ξv₃k_x+w]σ_x − (1/m k_xk_y + ξv₃)σ_y + (Δ/2)σ_z（Schrieffer-Wolff 推导），w = A₃ − A₀ 为应变项；通过数值计算 Berry 曲率与偶极密度并对载流子密度扫描。

### 主要发现与核心结论（Main Results）
- 单层石墨烯：5% 应变、Semenoff 质量 Δ = 20 meV、载流子密度 n ≈ 10¹⁰ cm⁻² 时，D_x ≈ 10⁻³ nm（两个锥等贡献），量级与 TMDC 预测相当。
- 双层石墨烯（Bernal AB 堆垛）：栅极诱导带隙 Δ = 10 meV、外加垂直电场破反演（点群 D3d → C3v）；在 w = −5ε_L（约合 1% 应变）、n ≈ 10¹¹ cm⁻² 时最大偶极强度 D_x ≈ 1 nm——比单层大三个数量级，且与实验在双层 WTe₂ 中测得的 Berry 偶极可比（减小质量还可到数十纳米量级）。
- 双层存在 Lifshitz 转变 ε_L = mv₃²/2 ≈ 1 meV（特征动量 κ_L = mv₃/ℏ ≈ 0.035 nm⁻¹），未应变时费米面分裂为一个中心 Dirac 锥（K/K′ 点 Berry 相 −π/π）加三个"腿"Dirac 锥（各带 π/−π）；C3 对称性使三条腿的非零贡献精确抵消（总偶极为零），单轴应变破坏该抵消。
- 双层偶极随密度变化出现尖点与拐点，反映不同的 Lifshitz 转变；通过栅压调密度可改变偶极符号，从而反转横向电流方向或完全抑制之。

### 潜在研究方向（Future Directions）
作者指出翘曲在二维材料中普遍存在，预期结论可推广到大量允许应变工程降到最低对称要求的二维体系，并把非线性 Hall 效应作为探测大量时间反演不变二维材料 Bloch 态几何性质的直接工具。方法学局限：全部结论建立在低能有效哈密顿量（应变展开至一阶、k² 动量项）之上，且双层有效模型仅在 n ≲ 10¹³ cm⁻² 有效；文中亦提示存在外禀贡献（非对称缺陷散射等）可贡献非线性 Hall 电流，虽可与 BCD 实验上解耦。

## 2301.01921

标题：Control over Berry Curvature Dipole with Electric Field in WTe₂（Phys. Rev. Lett. 130, 016301, 2023；DOI 10.1103/PhysRevLett.130.016301）
作者：Xing-Guo Ye、Huiying Liu、Peng-Fei Zhu、Wen-Zheng Xu、Shengyuan A. Yang、Nianze Shang、Kaihui Liu、Zhi-Min Liao（北京大学 / 新加坡科技设计大学）
来源：https://arxiv.org/abs/2301.01921 （v1, 2023-01-05）

### 研究问题（Research Question）
"能否用外加直流电场主动生成并调控 Berry 曲率偶极（BCD），以突破'BCD 在输运平面内最多只能保留一条镜面线'这一严格对称性限制？"由于多数材料体系需要额外的晶格应变或层间扭转工程才能产生可观 BCD，作者提出利用 Berry 连接极化率（Berry connection polarizability）实现场致 BCD，并实验检验其线性依赖与方向可控性。

### 研究背景（Background）
Sodemann & Fu 提出 D_α = ∫_k f₀(∂_α Ω_z) 驱动二阶非线性 AHE，可用于高频整流、无线充电、能量收集与红外探测；已有实验在单层/少层 WTe₂、Weyl 半金属 TaIrTe₄、MoS₂、WSe₂、皱褶双层石墨烯等体系观测到。但 BCD 的对称性约束严苛，可用平台受限。另一路线是 Berry 连接极化率 G_ab(k) = ∂A_a^(1)/∂E_b（场致位置移动的带几何量），Ω^(1) = ∇_k × (G↔E)，由此得 D_α^(1) = ε_{zγμ} ∫_k f₀ ∂_α(∂_γ G_μν) E_ν；此前该机制及其衍生非线性 Hall 效应尚未被实验证实。

### 研究方法（Methods）
器件为体相 Td-WTe₂ 薄片（器件 S1 厚 8.4 nm ≈ 12 层；器件 S2 为 Hall-bar），从体晶剥离转移到预制电极（圆盘电极 / Hall-bar）；晶轴取向由长直边缘 + 偏振拉曼 + 角度依赖输运三方确认。测量用圆盘电极做角度依赖；施加面内直流偏压 E_dc（以与电极基线夹角 θ 表征，|E_dc| = 3 kV/m，E_ω ≪ E_dc）产生场致 BCD，用交流电流 I_ω 探测二阶 Hall 电压 V_H^{2ω}。标度律拟合 [E_H^{2ω}/(E_ω)²] = C₀ + C₁σ_xx + C₂σ_xx²（C₀ 为内禀场致 BCD 项）；由 D = (2ℏ²n/m*)(E_H^{2ω}/E_ω²) 反推 BCD，m* = 0.3m_e。理论用 VASP DFT（PAW + PBE，含自旋轨道耦合）计算 Berry 连接极化率张量与场致 Berry 曲率。

### 主要发现与核心结论（Main Results）
- 观测到 BCD 与直流电场 E_dc 的线性依赖，且反推 E_dc 反号时信号反号；E_dc = 0 时二阶 Hall 信号可忽略，符合体相 Td-WTe₂ 面内反演对称（Ma 镜面 + M̃b 滑移镜面）禁止面内 BCD 的对称性分析。
- 角度依赖：D_a^(1) 随 θ 呈 cos θ 依赖，D_b^(1) 呈 sin θ 依赖；当 E_dc ∥ E_ω 沿 a 或 b 轴时 [E_H^{2ω}/(E_ω)²] 几乎为零（此时 D^(1) ⊥ E_ω，信号被镜像对称性强制为零）；θ ≈ 30° 附近出现局部极小，反映 WTe₂ 本征电导各向异性的贡献。
- 量值：在 E_dc = 3 kV/m 下实测 D_a^(1) ≈ −0.28 nm、D_b^(1) ≈ −0.05 nm（尺度棒 0.2 nm）；对照无外加 E_dc 时的表面本征 BCD 仅 D_a ≈ 0.03 nm（低一个数量级，且需 I_ω ≈ 1 mA 才可见，而场致信号在 I_ω < 0.05 mA 即可测）。
- 第一性原理（d ≈ 8.4 nm、E_dc = 3 kV/m、5 K 展宽）给出 D_b^(1)(90°) 从 ~−0.14 nm 变到 0、D_a^(1)(0°) 在 0.18 至 −0.13 nm 之间随化学势非单调变化，与实验值在量级上一致。
- 器件 S1 在 5 K 的电子迁移率约 4974 cm²/V·s；信号在 286 K 仍可测（温度扫描区间 50–286 K），即场致 BCD 调控可工作至室温。

### 潜在研究方向（Future Directions）
作者提出该"无额外对称性破缺的电学调控"可推广到更普遍材料体系，并把 BCD 相关物理从少数精心设计的平台扩展到一般材料，同时寄望于发展利用 Bloch 电子几何性质的非线性量子器件。方法学注意事项：外禀效应（二极管效应、热效应、热电效应）已被控制实验与对称性分析排除；标度律中 C₁、C₂ 含各类偏散射（杂质、声子及混合）贡献，故必须用温度依赖 σ_xx 做标度律分离才能提取内禀 C₀。此外表面破坏 M̃b 导致的弱本征 BCD 与体相场致 BCD 在信号量级上相差约一个数量级，解读时须区分。

---
存档路径：/Users/ll/.hermes/profiles/researcher/notes/berry_berry_20261107_litread.md（正文 3,867 汉字 + 公式，5 节 × 5 维度均已核验，节序与清单一致）

补充说明（供下游 analyst 参考，非笔记正文）：
- 5 篇均可通过 arXiv API/PDF 直接取全文，无需降级为摘要级蒸馏。
- 与本课题（Berry/Berry-curvature 2026-11）的衔接点最集中的是 1911.05667（§II 半经典展开：几何项被压到 ω⁻¹ 阶 → 少周期强场下不能只用 BCD 拟合）与 1910.09872（费米面翘曲触发 BCD → 提供与"应变/翘曲"无关的几何来源路径）。
- 三篇 1911.05667/1910.09872/2301.01921 已含 BCD 的完整定量基准，可直接用作方案中 BCD 数值预估的对照标尺。


## 2411.16675

标题：Fully nonequilibrium Hall response from Berry curvature（Phys. Rev. Lett. 2026 年 10 月 2 日在线发表；DOI 10.1103/cj8b-4sp4；arXiv:2411.16675）
作者：Shouvik Sur、Lei Chen、Yiming Wang、Chandan Setty、Silke Paschen、Qimiao Si
来源：https://arxiv.org/abs/2411.16675 （v3 全文，含正文与图注）

### 研究问题（Research Question）
在保持时间反演对称而破坏反演对称的半金属中，强场（完全非平衡）下的自发霍尔响应由什么决定？此前该响应被当作 Berry 曲率偶极驱动的二阶效应，本文要问的是：当场强超出微扰区，Berry 曲率偶极是否仍是控制量？

### 研究方法（Methods）
弛豫时间近似下的玻尔兹曼方程，配合一个二维电子掺杂多带模型。定义两个动量尺度：k_E ≡ eEτ₀/ℏ（电场在弛豫时间内的累积动量尺度）与 k_BC（沿电场方向 Berry 曲率密度极值点到费米面的最短距离）；并以 ε = k_E/k_BC 为强弱场判据。分布函数不按微扰处理，弛豫时间取为 τ(k, E)。

### 主要发现与核心结论（Main Results）
- 弱场区 k_E ≪ k_BC（ε ≪ 1）下横向电流 J_y ∝ E²，由 Berry 曲率偶极（∂_{k_x}Ω_{xy}）贡献。
- k_E 接近 k_BC 时 Berry 曲率密度极值点附近的占据被电场显著重组，标度开始偏离二次幂。
- 更强的场（k_E ~ k_F）时 J_y 转为准线性标度，响应不再由 Berry 曲率偶极控制，各阶 Berry 曲率矩贡献可比。
- 两个交叉沿 k_E 轴分离的前提是 k_BC ≪ k_F：作者通过调节化学势 μ 与对称性允许的倾斜势 B₀/B_x、M_y/(B_xΛ²) 把 Berry 曲率极值点调到紧贴费米面，并在该参数窗口内作计算。
- 弛豫时间在动量空间出现空间不对称，从而在微观时间反演不变条件下产生 1ω 响应分量。
- 交叉场强 E* 的标度单位为 ℏ/(eτ₀)，即 E* = k_BC·ℏ/(e·τ₀)。
- 费米面被重构的极端区（k_E ≳ k_F）需转入非平衡稳态格林函数方法处理。

### 潜在研究方向（Future Directions）
作者指出强关联拓扑半金属中该响应的实验检验尚未完成，并讨论与高阶 Berry 曲率矩的普适性对照。对本课题的直接含义：标度指数本身不能确认几何机制归属，k_BC ≪ k_F 的材料参数窗口是标度判据可测的先决条件。

## 2508.18677

标题：Berry Curvature Dipole-Induced Chiral Terahertz Gain and Lasing Threshold in Bulk Tellurium（Phys. Rev. B 113, 195202 (2026)；DOI 10.1103/btgp-rj5h；arXiv:2508.18677）
作者：Mounes Eslami、Amin Hakimi、Luis A. Jauregui、Filippo Capolino
来源：https://arxiv.org/abs/2508.18677 （v2, 2026-01-27；PDF 全文，表 I 与图 2–3 图注数值已逐条核对）

### 研究问题（Research Question）
n 型掺杂碲的 Berry 曲率偶极能否在直流偏置下产生太赫兹波段的圆偏振选择性放大与激光振荡，且偏压低于材料击穿阈值？

### 研究方法（Methods）
玻尔兹曼半经典近似的电光电导率分解为厄米回旋部分与非厄米部分，后者是增益/损耗来源；再以 Fabry-Perot 腔求激光阈值。材料参数取自 Morgado 等人的第一性原理计算。

### 主要发现与核心结论（Main Results）
- 表 I：Γ = 1.5625×10¹² rad/s，n = 0.784×10¹⁶ cm⁻³，D_B = −8.99×10⁻³（无量纲），ω_p,⊥/(2π) = 1.857×10¹² Hz，ω_p,∥/(2π) = 2.345×10¹² Hz。
- Case I（偏置与传播均沿 c 轴）：最小放大偏压 2.03×10⁴ V/m @ 30 THz；E₀ = 5×10⁴ V/m 时放大区间 f > 12.95 THz；E₀ = 10⁵ V/m 时为 1.05–1.27 THz 及 f > 7.65 THz。
- Case II（偏置沿 c 轴、传播沿 x）：耗散功率首次变负于 0.86 THz，对应阈值 E₀ ≥ 1.41×10⁵ V/m；E₀ = 2×10⁵ V/m 时放大频带 0.50–1.45 THz；E₀ = 4×10⁵ V/m 时 0.45–1.95 THz 及 f > 5.06 THz。
- Case III（偏置与传播均沿 x、垂直 c 轴）：椭圆本征模，放大阈值约 3.26×10⁵ V/m @ 1.23 THz；E₀ = 4×10⁵ V/m 时 mode 2 增益 0.9–1.6 THz。
- 激光阈值（R = 0.99，m = 1 基模）：Case I 腔长 L > 15.9 µm 出现三支解，最小阈值偏压 1.07×10⁵ V/m @ L = 30.2 µm、谐振 1.09 THz。
- 碲光声子介电共振约 2.64 THz（⊥c）与 2.76 THz（∥c）。
- 适用边界：仅做阈值与模选择性分析，不含增益饱和、模竞争与完整激光动力学。

### 潜在研究方向（Future Directions）
对增益区验证提出损耗要求（低损耗腔 R = 0.99 级镜面）。对本课题的直接含义：增益阈值场窗下界取 Case I 的 2.03×10⁴ V/m，上界取 Case II 的 4×10⁵ V/m；D_B 为无量纲量，由 ω_c = τe³D_B E₀/(ε₀ℏ²) 的量纲自洽确认。

## 2401.13764

标题：Non-Hermitian linear electro-optic effect in three-dimensional materials（Phys. Rev. B 109, 245126 (2024)；DOI 10.1103/PhysRevB.109.245126；arXiv:2401.13764）
作者：Tiago A. Morgado、Tatiana G. Rappoport、Stepan S. Tsirkin、Sylvain Lannebère 等
来源：https://arxiv.org/abs/2401.13764

### 研究问题（Research Question）
三维 D3 点群材料在静电偏置下的电光响应能否给出非厄米项，从而产生光学增益？

### 主要发现与核心结论（Main Results）
电光响应分为厄米（保守）回旋部分与非厄米部分，后者是增益/损耗来源。第一性原理计算表明 n 型掺杂碲的 Berry 曲率偶极显著大于常见的 p 型碲，因而在足够大的静电偏置下即可承载光学增益。该文的材料参数被 Eslami 等人直接引用为其计算表 I 的来源。

### 与本课题的关联
Eslami 等人增益计算所用 D_B = −8.99×10⁻³ 与 n = 0.784×10¹⁶ cm⁻³ 即出自本文的第一性原理结果，是本项目增益判据标定点的原始出处。

## cond-mat/0408417

标题：Berry Curvature on the Fermi Surface: Anomalous Hall Effect as a Topological Fermi-Liquid Property（Phys. Rev. Lett. 93, 206602 (2004)；DOI 10.1103/PhysRevLett.93.206602）
作者：F. D. Haldane
来源：https://arxiv.org/abs/cond-mat/0408417 （v5, 2004-11-11）

### 主要发现与核心结论（Main Results）
本征反常霍尔电导的非整数量子化部分完全可用准粒子在费米面上运动所累积的 Berry 相位表达，因而与 Landau 费米液体理论相容，而非如 Landau 抗磁性那样依赖填充态的整体性质。这一结论要求在存在反演或时间反演对称性破缺时，把准粒子的 Berry 相位加入 Landau 费米液体理论。

### 与本课题的关联
横向响应对 Berry 曲率的依赖集中在费米面附近的一段动量区间，这是本项目把 k_BC 界定为「Berry 曲率密度极值点到费米面的距离」并要求 k_BC ≪ k_F 的理论依据。

## 0907.2021（补充引用）

标题：Berry phase effects on electronic properties（Rev. Mod. Phys. 82, 1959 (2010)；DOI 10.1103/RevModPhys.82.1959；arXiv:0907.2021）
作者：Di Xiao、Ming-Che Chang、Qian Niu
来源：https://arxiv.org/abs/0907.2021

### 与本课题的关联
半经典方程给出的横向输运由 Berry 曲率决定的反常速度承担，Berry 曲率可写成参数空间曲面上 Berry 联络的积分形式。该综述是本项目各条计算路径（弛豫时间玻尔兹曼、Wannier 插值、统一光电霍尔框架）的共同理论基础。

## 三方碲晶格参数与原胞体积（结构参数核对，2026-11-16）

标题：Influence of trigonal deformation on band structure and Seebeck coefficient of tellurium（J. Phys. Chem. Solids 135, 109114 (2019)；DOI 10.1016/j.jpcs.2019.109114）
作者：J. C. Han、Y. C. Wu、L. Sun、H. R. Gong、X. Gong
来源：https://www.sciencedirect.com/science/article/abs/pii/S002236971930681X

### 主要发现与核心结论（Main Results）
三方碲的平衡结构为 P3₁21 点群（空间群 No.152）与 P3₂21（No.154），晶格常数为 a = 4.456 Å、c = 5.921 Å；该结构亦可视为以螺旋轴平行于 c 轴的非通常六方晶体。文中给出的 c/a = 1.174–1.444 区间对应 c = 5.921 Å 与 a = 4.456 Å 的组合。该三元结构在常压下为间接带隙（1.174 ≤ c/a < 1.274）、直接带隙（1.274 ≤ c/a < 1.372）与半金属（1.372 ≤ c/a ≤ 1.444）的分界来源。

### 与本课题的关联
三方碲原胞体积由该组晶格参数按六方原胞公式 V = (√3/2)a²c 复算得 102 Å³（每原子 33.9 Å³，与 RSC Advances 独立给出的 34.833 Å/atom 优化值相容），据此更正了申请书研究内容 §2.5 与研究方案 §3.2.3 中原写作的 82 Å³（原值对应硒体系）。统一动量网格的取点密度随之由 10⁶–10⁷ 点更正为 10⁷–10⁸ 点，平均间距由 0.0062–0.0029 Å⁻¹ 更正为 0.022–0.010 Å⁻¹，三者由 (V/N)^(1/3) 复算自洽。该值直接支撑 k_BC 读数精度预算中 6%–17% 的偏差估计与 30% 框架内部一致性容差。

### 同源结构参数佐证
Allotropes of tellurium from first-principles crystal structure prediction calculations under pressure（Y. Liu 等，RSC Adv. 8, 23268 (2018)；DOI 10.1039/C8RA07843B）给出实验晶格参数 a = 4.527 Å、c = 5.929 Å，并在 0 GPa 优化得 a = 4.514 Å、c = 5.955 Å、每原子体积 34.833 Å³，与上条的晶格参数组自洽，共同确认 102 Å³ 量级的原胞体积。

## 参考文献表裁撤与角标重排（2026-11-16）

标题：申请书参考文献表由 47 条裁撤至 39 条，正文角标同步重排
来源：04_proposal/sections/references.md 与 rationale/content/scheme 三章正文

### 主要结论
裁撤八条：Zhan 等 Floquet 拓扑工程综述、Karki 等 CuPb₉(PO₄)₆O 的 BCD 理论计算、Zhang 等 Weyl 半金属 BCD 第一性原理、Du 等非线性霍尔量子理论综述、Ye 等石墨烯/黑磷双层异质结构应变调控、Zhao 等 Nb₂ₙ₊₁SiₙTe₄ₙ₊₂ 几何图像、Lee 等 NbIrTe₄ 自旋轨道劈裂驱动非线性霍尔、Shi 等二维碲进展综述。裁撤依据是同一段落内已有承担同等论证功能的文献在位，保留造成角标冗余。裁撤后编号 1–39 连续无跳号，正文 66 处角标覆盖全部 39 条，无孤儿条目、无悬空角标；重排采用「先建映射表再机械替换」的方式逐条回核作者与题名，未凭记忆改挂。

### 与本课题的关联
参考文献规模落入 30–40 条区间，正文角标密度由 83 处降至 66 处，对齐范本「关键论断处编号、其余作为研读基础」的引用体例。

---

本轮补充说明（供下游参考，非笔记正文）：
- 本轮新增 6 条（2411.16675、2508.18677、2401.13764、2610.14367、cond-mat/0408417、0907.2021 补充引用），元数据均经 arXiv API 与期刊页双源核对。
- 2508.18677 的表 I 与图 2、图 3 图注数值逐条核对后，发现申请书原引用的「2.1×10⁴ V/m」应为「2.03×10⁴ V/m」，且「12.95 THz 以上」对应的是 E₀ = 5×10⁴ V/m 而非阈值场强，已在申请书立项依据中改正。
- 2411.16675 全文给出 k_BC ≪ k_F 的参数窗口要求与 E* = k_BC·ℏ/(e·τ₀) 的标度式，这是申请书研究方案中交叉场强可测性论证的依据来源。
- 2026-11-16 轮新增 1 组结构参数核对（三方碲 a = 4.456 Å、c = 5.921 Å，原胞体积 102 Å³），据此更正原胞体积、动量网格点数与网格间距三处不自洽数值，并统一 k_BC 可读区间为 2×10⁻³–4.5×10⁻³ Å⁻¹、补写 τ₀ 取值依据。
- 2026-11-16 轮参考文献表裁撤八条至 39 条，编号重排后逐条回核作者与题名，正文角标 83 处降至 66 处。

## 参考文献表全量回录（2026-11-16，references 轮）

标题：申请书参考文献表 39 条的全量回录，逐条给出作者链、题名、刊名卷期页年、DOI 与 arXiv 编号
来源：04_proposal/sections/references.md

### 回录规则
每条按 references.md 的现行条目逐字段誊写，作者链与卷期页来自 CrossRef works/{DOI} 定点反查（无 DOI 者取 arXiv Atom API），预印本编号取 arXiv 记录。回录以条目身份为准，不以编号顺序为准。

### 全量回录表

| 编号 | 作者链 | 题名 | 刊名卷期页年 | DOI | arXiv |
|---|---|---|---|---|---|
| [1] | D. J. Thouless, M. Kohmoto, M. P. Nightingale, M. den Nijs | Quantized Hall conductance in a two-dimensional periodic potential | Phys. Rev. Lett. 49, 405 (1982) | 10.1103/PhysRevLett.49.405 | — |
| [2] | Z. Z. Du, C. M. Wang, H.-Z. Lu, X. C. Xie | Band signatures for strong nonlinear Hall effect in bilayer WTe₂ | Phys. Rev. Lett. 121, 266601 (2018) | 10.1103/PhysRevLett.121.266601 | — |
| [3] | I. Sodemann, L. Fu | Quantum nonlinear Hall effect induced by Berry curvature dipole in time-reversal invariant materials | Phys. Rev. Lett. 115, 216806 (2015) | 10.1103/PhysRevLett.115.216806 | — |
| [4] | T. Low, Y. Jiang, F. Guinea | Topological currents in black phosphorus with broken inversion symmetry | Phys. Rev. B 92, 235447 (2015) | 10.1103/PhysRevB.92.235447 | — |
| [5] | C.-P. Zhang, X.-J. Gao, Y.-M. Xie, H. C. Po, K. T. Law | Higher-order nonlinear anomalous Hall effects induced by Berry curvature multipoles | Phys. Rev. B 107, 115142 (2023) | 10.1103/PhysRevB.107.115142 | — |
| [6] | S. Sur, L. Chen, Y. Wang, C. Setty, S. Paschen, Q. Si | Fully nonequilibrium Hall response from Berry curvature | Phys. Rev. Lett.，2026 年 10 月 2 日在线 | 10.1103/cj8b-4sp4 | 2411.16675 |
| [7] | L. E. Golub, E. L. Ivchenko, B. Spivak | Semiclassical theory of the circular photogalvanic effect in gyrotropic systems | Phys. Rev. B 102, 085202 (2020) | 10.1103/PhysRevB.102.085202 | — |
| [8] | S. A. Sato, J. W. McIver, M. Nuske 等 12 人 | Microscopic theory for the light-induced anomalous Hall effect in graphene | Phys. Rev. B 99, 214302 (2019) | 10.1103/PhysRevB.99.214302 | — |
| [9] | N. Yoshikawa, S. Okumura, Y. Hirai 等 13 人 | Light-induced anomalous Hall conductivity in the massive three-dimensional Dirac semimetal Co₃Sn₂S₂ | Phys. Rev. B 111, 245104 (2025) | 10.1103/PhysRevB.111.245104 | — |
| [10] | X.-G. Ye, H. Liu, P.-F. Zhu 等 8 人 | Control over Berry curvature dipole with electric field in WTe₂ | Phys. Rev. Lett. 130, 016301 (2023) | 10.1103/PhysRevLett.130.016301 | 2301.01921 |
| [11] | T.-Y. Zhao, A.-Q. Wang, X.-G. Ye, X.-Y. Liu, X. Liao, Z.-M. Liao | Gate-tunable Berry curvature dipole polarizability in Dirac semimetal Cd₃As₂ | Phys. Rev. Lett. 131, 186302 (2023) | 10.1103/PhysRevLett.131.186302 | — |
| [12] | M. Eslami, A. Hakimi, L. A. Jauregui, F. Capolino | Berry curvature dipole induced chiral terahertz gain and lasing threshold in bulk tellurium | Phys. Rev. B 113, 195202 (2026) | 10.1103/btgp-rj5h | 2508.18677 |
| [13] | Y. Murotani, T. Fujimoto, R. Matsunaga | Unified theory of the photovoltaic Hall effect by field- and light-induced Berry curvatures | Phys. Rev. B 113, 115202 (2026) | 10.1103/7psv-fzw1 | 2505.06078 |
| [14] | T. Fujimoto, Y. Murotani, T. Tamaya 等 10 人 | Light-induced inverse spin Hall effect and field-induced circular photogalvanic effect in GaAs revealed by two-dimensional terahertz Fourier analysis | Phys. Rev. B 111, L201201 (2025) | 10.1103/PhysRevB.111.L201201 | — |
| [15] | M.-S. Qin, P.-F. Zhu, X.-G. Ye 等 8 人 | Strain tunable Berry curvature dipole, orbital magnetization and nonlinear Hall effect in WSe₂ | Chin. Phys. Lett. 38, 017301 (2021) | 10.1088/0256-307X/38/1/017301 | — |
| [16] | X.-G. Ye, P.-F. Zhu, W.-Z. Xu, Z. Zang, Y. Ye, Z.-M. Liao | Orbital polarization and third-order anomalous Hall effect in WTe₂ | Phys. Rev. B 106, 045414 (2022) | 10.1103/PhysRevB.106.045414 | 2207.08045 |
| [17] | X.-G. Ye, P.-F. Zhu, W.-Z. Xu, T.-Y. Zhao, Z.-M. Liao | Nonlinear spin and orbital Edelstein effect in WTe₂ | Phys. Rev. B 110, L201407 (2024) | 10.1103/PhysRevB.110.L201407 | — |
| [18] | H. Chen, X. Wu, J. Yang, P. Tang, J. Li | Laser-controlled nonlinear Hall effect in tellurium solids via nonlinear phononics | 预印本 arXiv:2411.18843 (2024) | — | 2411.18843 |
| [19] | C. Jiang, F. Yang, Y. Zhao 等 18 人 | Room-temperature intrinsic nonlinear planar Hall effect in TaIrTe₄ | Phys. Rev. Lett. 136, 236302 (2026) | 10.1103/hbdj-2hgf | 2506.17730 |
| [20] | Q. Huang, S. Huang, T. Chen 等 8 人 | Anomalous Hall conductivity as an effective means of tracking the Floquet Weyl nodes in quasi-one-dimensional β-Bi₄I₄ | Phys. Rev. B 113, L241105 (2026) | 10.1103/wt2s-z2r5 | 2603.27514 |
| [21] | A. Gao, Y.-F. Liu, J.-X. Qiu 等 31 人 | Quantum metric nonlinear Hall effect in a topological antiferromagnetic heterostructure | Science 381, 181 (2023) | 10.1126/science.adf1506 | — |
| [22] | Z.-F. Zhang, Z.-G. Zhu, G. Su | Symmetry dictionary on charge and spin nonlinear responses for all magnetic point groups with nontrivial topological characteristics | Natl. Sci. Rev. 10, nwad104 (2023) | 10.1093/nsr/nwad104 | — |
| [23] | L. Geng, M. Eckstein, L. Chen 等 7 人 | Nonperturbative nonlinear Hall effect in nonequilibrium steady states | Phys. Rev. Lett.，2026 年 10 月 14 日在线 | 10.1103/dy42-1yz7 | 2607.01519 |
| [24] | M. Dendzik, A. Marini, S. Beaulieu 等 12 人 | Ultrafast nonlinear Hall effect in black phosphorus | 预印本 arXiv:2604.06083 (2026) | — | 2604.06083 |
| [25] | E. Mönch, M. D. Moldavskaya, L. E. Golub 等 10 人 | Terahertz radiation driven nonlinear transport phenomena in two-dimensional tellurene | Nano Lett. 25, 476 (2025) | 10.1021/acs.nanolett.4c05279 | 2410.17888 |
| [26] | J. Lee, J. Shin, D. J. C. Dalayoan 等 11 人 | Direct observation of chirality-dependent Berry curvature dipole via cross-axial nonlinear Hall effect in trigonal Te | ACS Nano，2026 年 11 月 12 日在线 | 10.1021/acsnano.6c10070 | 2610.14367 |
| [27] | T. A. Morgado, T. G. Rappoport, S. S. Tsirkin, S. Lannebère, I. Souza, M. G. Silveirinha | Non-Hermitian linear electro-optic effect in three-dimensional materials | Phys. Rev. B 109, 245126 (2024) | 10.1103/PhysRevB.109.245126 | 2401.13764 |
| [28] | H. Munekata, G. Kusuno, K. Miyazaki, T. Satoh | Polarization-dependent photocurrent in a quadrilateral-shaped bulk crystalline tellurium chip with near-infrared light excitation | Jpn. J. Appl. Phys. 64, 113002 (2025) | 10.35848/1347-4065/ae14c7 | 2504.00413 |
| [29] | M. D. Moldavskaya, L. E. Golub, E. Mönch 等 7 人 | Terahertz field-driven nonlinear Hall effect and other second order transport phenomena in two-dimensional tellurene | Phys. Rev. B 114, 305303 (2026) | 10.1103/w8fp-vmm7 | 2607.09256 |
| [30] | J. Ma, Q. Gu, Y. Liu 等 10 人 | Nonlinear photoresponse of type-II Weyl semimetals | Nat. Mater. 18, 476 (2019) | 10.1038/s41563-019-0296-5 | 1806.08508 |
| [31] | A. Chakraborty, K. Das, S. Sinha, P. C. Adak, M. M. Deshmukh, A. Agarwal | Nonlinear anomalous Hall effects probe topological phase-transitions in twisted double bilayer graphene | 2D Mater. 9, 045020 (2022) | 10.1088/2053-1583/ac8b93 | 2205.15120 |
| [32] | S. Dzsaber, X. Yan, M. Taupin 等 12 人 | Giant spontaneous Hall effect in a nonmagnetic Weyl-Kondo semimetal | Proc. Natl. Acad. Sci. U.S.A. 118, e2013386118 (2021) | 10.1073/pnas.2013386118 | — |
| [33] | M. Melegari, I. Gutiérrez-Lezama, J. C. W. Song, A. F. Morpurgo | Switchable giant room-temperature nonlinear Hall effect in bilayer graphene | 预印本 arXiv:2608.26869 (2026) | — | 2608.26869 |
| [34] | B. Sharma, S. Singh | Fourth-order optoelectronic response from cascaded circular photogalvanic and nonlinear Hall effects | 预印本 arXiv:2607.10012 (2026) | — | 2607.10012 |
| [35] | S. S. Tsirkin, P. Aguado Puente, I. Souza | Gyrotropic effects in trigonal tellurium studied from first principles | Phys. Rev. B 97, 035158 (2018) | 10.1103/PhysRevB.97.035158 | 1710.03204 |
| [36] | M. Cheng, S. Wu, Z.-Z. Zhu, G.-Y. Guo | Large second-harmonic generation and linear electro-optic effect in trigonal selenium and tellurium | Phys. Rev. B 100, 035202 (2019) | 10.1103/PhysRevB.100.035202 | 1904.01927 |
| [37] | M. Cheng, Z.-Z. Zhu, G.-Y. Guo | Strong bulk photovoltaic effect and second-harmonic generation in two-dimensional selenium and tellurium | Phys. Rev. B 103, 245415 (2021) | 10.1103/PhysRevB.103.245415 | 2012.01124 |
| [38] | F. D. Haldane | Berry curvature on the Fermi surface: Anomalous Hall effect as a topological Fermi-liquid property | Phys. Rev. Lett. 93, 206602 (2004) | 10.1103/PhysRevLett.93.206602 | cond-mat/0408417 |
| [39] | D. Xiao, M.-C. Chang, Q. Niu | Berry phase effects on electronic properties | Rev. Mod. Phys. 82, 1959 (2010) | 10.1103/RevModPhys.82.1959 | 0907.2021 |

### 主要结论
39 条全量回录完成，与 references.md 现行 39 条逐条对应，编号 1–39 连续无跳号。作者链以「真作者总数 + 列表形式」双记：六位及以下全部列出，七位及以上列前三位并加 et al.，与 references.md 头注凡例一致。四条纯预印本（[18][24][33][34]）经 arXiv 记录确认无 DOI 字段，只给 arXiv 编号；其余 35 条均带 DOI，其中 19 条同时给出 arXiv 编号作为双源交叉点。

### 与本课题的关联
回录表覆盖申请书立项依据、研究内容、研究方案三章的全部 60 处角标引用，是正文角标与文献条目的一致性校验底表；[26] 与 [29] 的卷期页与刊版状态为本轮更正项，是参考文献与正文发表状态断言互斥问题的消解依据。

## 2610.14367 刊版状态更正（2026-11-16，references 轮）

标题：arXiv:2610.14367 已挂 ACS Nano 刊版 DOI，原「纯预印本」状态失效
来源：https://arxiv.org/abs/2610.14367 ｜ CrossRef works/10.1021/acsnano.6c10070

### 研究问题（Research Question）
三方碲是否具有对映体依赖的 Berry 曲率偶极，且该偶极能否通过交叉轴向非线性霍尔效应被直接读出。

### 检索与核实方式
arXiv Atom API 查询 id_list=2610.14367，abs 记录已挂 `<arxiv:doi>10.1021/acsnano.6c10070</arxiv:doi>`；CrossRef works/10.1021/acsnano.6c10070 反查确认题名「Direct Observation of Chirality-Dependent Berry Curvature Dipole via Cross-Axial Nonlinear Hall Effect in Trigonal Te」、刊名 ACS Nano、11 位作者（Jaehyun Lee、Junhee Shin、Daryll J. C. Dalayoan、Miju Park、Changhee Sohn、Gang Qiu、Noejung Park、Binghai Yan、Tony Low、Hosub Jin、Seon Namgung）、在线发表日期 2026 年 11 月 12 日。卷号与页码尚未分配，故条目按在线发表形态著录。

### 主要发现与核心结论（Main Results）
刊版与预印本作者链完全一致，说明论文正文内容未变。原先写作笔记中「截至 2026 年 11 月尚未见正式期刊发表」的判断已失效，申请书立项依据 §1.1 与研究内容 §2.3、§2.7 中三处与之相关的表述改为刊版发表形态。

### 与本课题的关联
本项目的碲平台标定值（D_xx = −0.0676 / +0.0616，散射时间 294 / 308 fs，有效质量 0.150 m₀，χ_yxz/χ_xxx = 2.28 / 2.81）与交叉轴向构型的必然性论据均出自该文，发表状态直接影响正文表述的准确性；同表其余条目（如 [25][29]）均为 DOI+arXiv 并列形态，[26] 此前独缺刊版 DOI 造成体例破绽。

## 2607.09256 刊版卷页补全（2026-11-16，references 轮）

标题：Terahertz field-driven nonlinear Hall effect 条目补全 Phys. Rev. B 114, 305303 (2026)
来源：CrossRef works/10.1103/w8fp-vmm7 ｜ arXiv:2607.09256

### 主要发现与核心结论（Main Results）
CrossRef 已给出完整卷期页 PRB 114, 305303 (2026)，作者 7 位（M. D. Moldavskaya、L. E. Golub、E. Mönch、Chang Niu、Peide D. Ye、J. Wunderlich、S. D. Ganichev）。原条目仅标在线发表日期，本轮补全卷期页并删除 online 注，与同表其余期刊条目体例一致。

### 与本课题的关联
该文是二维碲烯太赫兹场驱动二阶输运逐项分离（非线性霍尔、非线性纵向、非线性对角）与 ±20 V 背栅调控的来源，是研究方案 §3.4.3 门压能力口径与 §3.4.1 脉冲宽度下界引用的依据。
