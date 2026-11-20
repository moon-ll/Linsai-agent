---
title: "TDSE求解器"
type: "methods"
created: "2026-06-17T12:40:33Z"
updated: "2026-11-15T15:09:19Z"
tags: ["计算方法", "TDSE", "数值模拟", "type/method", "topic/HHG", "status/mature", "status/growing"]
related: ["1401.2878", "1609.09852", "1807.01616", "2012.10328", "2020-2012_10328-deep-learning-and-high-harmonic-generation", "2024-2405_01351-high-harmonic-generation-from-electrons-moving-in-topologica", "2024-s41467-024-44775-5-spatiotemporal-imaging-and-shaping-of-electron-wave-function", "2025-2506_07445-circular-rabbitt-goes-under-threshold", "2025-2512_15370-orientation-dependent-high-harmonic-generation-in-zno", "2026-2604_06703-strong-field-ionization-of-atoms-with-bright-squeezed-vacuum", "2026-2610.35991-theoretical-study-of-high-order-harmonic-generation-in-solid", "2304.11661", "2311.13309", "2312.14174", "2405.01351", "2407.09662", "2409.03622", "2502.08811", "2506.07445", "2506.10379", "2509.06647", "2511.12372", "2512.15370", "2512.24496", "2604.06703", "2606.22714", "2609.20559", "5-11", "Berry曲率", "CEP稳定", "Continuum-continuum 跃迁振幅的解析表达（含角动量依赖）—— Ji", "Floquet工程", "Floquet边带", "Hamiltonian learning via inverse physics-informed neural networks", "Han & Wörner (2024)", "Lewenstein模型", "RABBIT", "RABBITT", "TDDFT", "TDSE", "Ueda", "arpes", "circular-dichroism", "rainbow-RABBITT", "strong-field-ionization", "三步模型", "亮压缩真空", "压缩真空态", "固体HHG", "固态高次谐波", "圆二色性", "带内/带间电流分解", "强场电离", "强场驱动", "掺杂体系中固态高次谐波生成对激光场强的依赖", "物理信息神经网络（PINN）", "电荷密度波", "相位匹配", "高次谐波产生", "高次谐波光谱学", "高次谐波谱学：一维准晶中的迁移率边"]
source_raw: ""
growth_stage: "mature"
confidence: 0.9
aliases: ["TDSE-solver", "time-dependent-schrodinger", "含时薛定谔求解"]
updated_at: "2026-11-15T10:23:15Z"
settled_count: 39
---

<!-- methods-settle:v1 -->

## 原理

TDSE求解器通过数值求解含时薛定谔方程给出强场体系的第一性原理响应：既作为深度学习正/逆网络的物理引擎批量生成带物理标签训练集（单活性电子TDSE生成脉冲参数-光电子动量谱数据对），又作为机器学习仿真器的真值与训练数据来源提供量子动力学样本供仿真器学习，并在贝叶斯参数估计中充当似然函数的物理内核、把待估参数映射为时间分辨可观测量供与数据比对，还作为量子计量学基准验证SFA框架Fisher信息结论、与SFA量子轨迹联用验证电子波包干涉并提取势垒下电离轨迹参数；在量子光HHG方向经TDSE/SFA校验确立偶次谐波幅值对2ω场强的线性标度（源于微扰展开与选择律，论证性外推至库仑修正与固体HHG），支撑BSV双色驱动下高斯纠缠谐波态与量子隐形传态优势边界的解析刻画，且量子化BSV驱动场模型表明谐波偶极辐射继承驱动场压缩与关联结构、是Wigner负性出现的根源；在含库仑（模型）势模拟中作为真值已知的合成条纹谱基准，可升级为双电子全关联TDSE（He在XUV+IR场、He与H2 crRABBITT）或经含时R-matrix内外区耦合推进至F⁻九电子体系，并可做含各向异性分波与残余势的全维从头计算——复现实验偏差、确认各向同性渐近近似的破缺源于非渐近与非各向同性贡献；在RABBITT家族中充当幅相提取理论基准（cuRABBITT揭示He/Ar强共振与Xe Cooper类极小、crRABBITT变IR载频分辨全谱边带并分离直接/共振通道），并可验证RABBITT类半经典理论（至中强探针场）及扩展至随机量子光场（Husimi分布采样+系综平均）；阿秒条纹方面以单/双活性电子从头TDSE全模拟分离激光场致时间平移（tCLC与tdLC），与BSR多电子EWS延迟组合验证亚阿秒精度严格可加分解；求解域从气相原子推广至固态——动量空间多能带/晶体动量表象少带TDSE、紧束缚两带链与实空间TDSE、学习TB哈密顿量上的传播、周期晶格势MgO超短脉冲模拟、准周期Aubry-André-Harper链并扩展至连续极限非公度势的一维mobility edge体系（强场实时传播直接模拟波包动力学并提取谐波谱、避开布里渊区周期性假设）、Kondo格子斯格明子晶体与Haldane/Kane-Mele拓扑模型、显式掺杂半导体带模型，以及沿多晶向的取向分辨模拟（ZnO中定量给出谐波谱随晶体取向与偏振角的变化）；并可做亚周期Floquet工程含时演化、XUV+IR条纹Ne全模拟、泵浦-探测CD映射，以及以精确解为全量子数值基准定量标定半经典模型在谱形、截止与相位上的误差幅度——最新扩展至以TDSE精确解对比谐波产额与相位，校验高精度半经典强场Herman-Kluk传播子方法的精度与适用范围。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 偶次谐波幅值对2ω场强的标度律 | 线性标度（源于微扰展开+选择律，论证可外推至库仑修正与固体HHG） | paper:2026-2606.22714-emergence-of-gaussian-entanglement-and-non-gaussia |
| BSV驱动压缩参数工作区间 | r ~ 10（e^{±2r} ~ 10^{±8}，单正交象限简化模型） | paper:2026-2606.22714-emergence-of-gaussian-entanglement-and-non-gaussia |
| ZnO取向分辨模拟/实验驱动波长 | 3.2 μm（MIR，ELI-ALPS OPCPA） | paper:2025-2512.15370-orientation-dependent-high-harmonic-generation-in-zno |
| ZnO驱动脉冲参数 | ~45 fs FWHM（~4个光周期）、~100 μJ、100 kHz、CEP稳定 | paper:2025-2512.15370-orientation-dependent-high-harmonic-generation-in-zno |
| ZnO谐波产额扫描峰值强度 | I = 1 TW/cm²（低于ZnO损伤阈值，焦斑150 μm × 136 μm） | paper:2025-2512.15370-orientation-dependent-high-harmonic-generation-in-zno |
| ZnO样品构型 | 厚度50 μm；c-cut(0001)仅奇次谐波，a-cut(1120)奇偶次均有（观测至13th-19th阶） | paper:2025-2512.15370-orientation-dependent-high-harmonic-generation-in-zno |
| Ne 2s-2p 相对条纹时延（Schultze 实验值） | 21 ± 5 as | paper:2014-1401.2878-time-delays-for-attosecond-streaking-in-photoionization-of-n |
| 理论Ne 2s-2p相对条纹时延与实验值之比 | 约小2倍（理论∆tS≈实验/2） | paper:2014-1401.2878-time-delays-for-attosecond-streaking-in-photoionization-of-n |
| RABBITT边带产额随XUV/IR延迟τ的振荡频率 | 2ω（两倍IR光子频率，S2q(τ)=A+Bcos[2ωτ+C]） | paper:2025-2506.07445-circular-rabbitt-goes-under-threshold |
| uRABBITT阈下条件 | (2q−1)ω < |Ei| < (2q+1)ω（奇次谐波之一落于电离阈下，经分立Rydberg激发补足吸收路径） | paper:2025-2506.07445-circular-rabbitt-goes-under-threshold |

## 适用边界

TDSE逐点全维求解成本高：作为训练标签源或机器学习仿真器真值时精度与可靠域由参数空间覆盖决定、仿真器不能外推训练样本分布之外，作为贝叶斯参数估计似然内核时须随采样链反复调用正向求解、成本随待估参数维数与链长急剧攀升，且从头算能力受激光强度/波长/波形参数限制、数值结果仅对应特定参数点而无解析洞察；量子光HHG的高斯纠缠结论以低耗尽条件和谐波幅值对驱动场涨落的线性依赖（微扰区）为前提，随压缩参数r增大线性近似失效、谐波态转向非高斯，单正交象限BSV模型仅捕获主导统计性质，偶次谐波线性标度向库仑修正与固体HHG的外推属论证性外推而非直接验证；'物理精确'以单活性电子近似为前提，多电子关联需双电子全关联TDSE或RMT多体TDSE（已示范F⁻九电子），成本随电子数急剧攀升；Ne条纹基准中SAE/双活性电子TDSE+BSR的2s-2p相对时延比实验小约2倍，存在shake-up伴线污染时须保持警觉，其亚阿秒可加分解以XUV弱场一阶微扰与IR中等强场为前提；cuRABBITT理论基准限于单活性电子+模型势TDSE及He/Ar/Xe所设圆偏阈下运动学区间，crRABBITT需在多IR载频下重复计算且以谱峰足够宽未重叠为条件；全维TDSE基准本身证实各向同性渐近近似会因非渐近、非各向同性贡献而破缺，凡依赖该近似的解析结论在相应实验比对区间不适用；固态各实现（少带多能级、紧束缚链/实空间、学习哈密顿量、掺杂模型、拓扑模型、取向分辨ZnO）均限于各自模型设定与所模拟参数区间、不含电子-电子关联与宏观传播，ZnO理论三重调制与实验四重对称的偏差提示结果对激光波长与峰值强度敏感、不直接外推至真实三维材料，连续极限非公度势实时传播属一维模型、其mobility edge谐波光谱结论限于所模拟势形与场参数窗口；以TDSE精确解为基准的半经典标定（含Herman-Kluk传播子的谐波产额与相位对比）所划定的精度与适用范围仅对所校验体系与参数区间成立，不外推到未覆盖的场强/体系。

## 代表作

- paper:2025-2506.07445-circular-rabbitt-goes-under-threshold
- paper:2014-1401.2878-time-delays-for-attosecond-streaking-in-photoionization-of-n
- paper:2020-2012.10328-deep-learning-and-high-harmonic-generation
- paper:2023-2303.13940-femtosecond-pulse-parameter-estimation-from-photoelectron-mo
- paper:2020-2008.10070-quantum-estimation-in-strong-fields-in-situ-ponderomotive-se
- paper:2024-s41467-024-44775-5-spatiotemporal-imaging-and-shaping-of-electron-wave-function
- paper:2023-2312.14174-evaluating-the-accuracy-of-attosecond-streaking-time-delay-m
- paper:2025-2511.12372-generation-of-bright-and-controllable-isolated-attosecond-x

## 证据日志

- 2026-10-17｜r76｜仅简报｜[paper:2024-2304.11661-laser-field-strength-dependence-of-solid-high-harmonic-gener] TDSE（一维周期势+掺杂模型势）：在单电子数值实验中显式包含掺杂/杂质势，直接对比掺杂与本征系统的全阶次HHG谱。
- 2026-10-17｜r80｜仅简报｜[paper:2023-2308.15087-on-the-limitations-of-the-semi-classical-picture-in-high-har] 含时薛定谔方程（TDSE）数值基准：以全量子数值解为对照，定量标定半经典模型在谱形、截止与相位预言上的误差幅度。
- 2026-10-18｜r82｜回原文｜[paper:2023-2311.13309-buildup-and-dephasing-of-floquet-bloch-bands-on-subcycle-tim] 亚周期含时模拟（TDSE / 半导体布洛赫方程）：数值求解含时薛定谔方程以追踪能带在单周期内的建立与演化
- 2026-10-24｜r91｜仅简报｜[paper:2020-2005.12654-angle-resolved-time-delays-for-shake-up-ionization-of-helium] 双电子含时薛定谔方程（TDSE）从头算求解：为氦 shake-up 各通道提供含相位的角分辨双光子矩阵元，是全部延迟分析的基准数据。
- 2026-10-24｜r91｜仅简报｜[paper:2020-2003.12409-electron-correlation-and-short-range-dynamics-in-attosecond] 含时 R-matrix（RMT）多体 TDSE：对 F⁻ 九电子体系做内外区耦合的全关联含时薛定谔方程求解，量化多体关联对 attoclock 偏移角的贡献。
- 2026-10-24｜r92｜仅简报｜[paper:2024-2401.04299-time-dependent-theory-of-reconstruction-of-attosecond-harmon] TDSE含时薛定谔方程数值模拟：作为基准验证半经典理论对边带产额与相位的预言，确认其在中强探针场下仍适用。
- 2026-10-24｜r92｜回原文｜[paper:2016-1609.09852-multi-level-perspective-on-high-order-harmonic-generation-in] 多能级 TDSE（晶体动量表象）：用 Γ 点附近几条能带截断的时域薛定谔方程复现了固态 HHG 的多平台谱，验证了少带模型的充分性。
- 2026-10-30｜r100｜回原文｜[paper:2025-2512.24496-adiabatic-approach-for-high-harmonic-generation-in-solids-in] 含时薛定谔方程数值演化（TDSE）：作为基准校验绝热近似的适用窗口（频率、场强、脉冲长度范围）。
- 2026-10-30｜r101｜仅简报｜[paper:2022-2211.06244-formation-of-the-solid-state-high-order-harmonic-generation] 动量空间 TDSE（紧束缚两带链模型）：为固体 HHG 提供全量子基准谱，可与半导体 Bloch 方程或 Houston 基结果互证。
- 2026-10-30｜r102｜仅简报｜[paper:2026-2610.35991-theoretical-study-of-high-order-harmonic-generation-in-solid] 紧束缚基组下的强场含时传播（含时薛定谔/半导体布洛赫方程）：在学习得到的 TB 哈密顿量上求解载流子动力学，提取带内/带间电流得到谐波谱。
- 2026-10-31｜r104｜仅简报｜[paper:2019-1911.12092-cooper-minimum-of-high-order-harmonic-spectra-from-mgo-cryst] 固态含时薛定谔方程（TDSE）强场HHG模拟（周期晶格势、超短脉冲驱动）：给出MgO谐波全谱及~16 eV凹陷的直接数值证据，并通过扫描强度/脉宽确认极小位置不随动力学参数移动。
- 2026-10-31｜r104｜仅简报｜[paper:2025-PhysRevLett.134.203201-phase-resolved-attoclock] 含时薛定谔方程（TDSE）数值模拟：作为无模型偏倚的基准，对照 CEP 依赖的角条纹移动以抽取真实电离/隧穿延迟。
- 2026-10-31｜r106｜仅简报｜[paper:2018-1807.01616-circular-dichroism-in-high-order-harmonic-generation-heraldi] 两带 Haldane 模型 + k 空间含时薛定谔方程实时演化：给出 Chern 绝缘体在强圆偏场下的完整谐波谱及其随拓扑参数的演化，是固态 HHG 拓扑研究的基准数值方案。
- 2026-10-31｜r107｜仅简报｜[paper:2024-2407.09662-analytical-expression-for-continuum-continuum-transition-amp] TDSE 数值求解（基准对照）：提供完全数值基准，验证解析表达式在低动能、高角动量区的定量可靠性。
- 2026-10-31｜r107｜仅简报｜[paper:2023-2303.17300-are-there-universal-signatures-of-topological-phases-in-high] 含时薛定谔方程（TDSE）全布里渊区模拟（紧束缚/Kane-Mele模型）：在完全相同晶格上做精确量子动力学，排除了近似误差，使拓扑/平庸对比成为受控实验。
- 2026-10-31｜r109｜仅简报｜[paper:2024-2410.04512-real-space-perspective-on-dephasing-in-solid-state-high-harm] 紧束缚晶格含时薛定谔方程（TDSE）模拟：在单电子相干演化中直接复现退相干特征，分离带内/带外电流并追踪极化衰减。
- 2026-11-01｜r110｜仅简报｜[paper:2026-2403.05073-rainbow-retrieval-of-atomic-time-delays-in-attosecond-streak] 含时薛定谔方程（TDSE）单活跃电子模拟：Kheifets/Serov 用 TDSE 计算宽带条纹迹与提取相位，为检索方案提供基准并解释 He/Ar/Xe 实验延迟结构。
- 2026-11-01｜r112｜回原文｜[paper:2025-2502.08811-continuous-rainbow-rabbitt-investigation-of-resonant-states] 两光子微扰理论 / TDSE 数值计算（He 与 H2）：给出含共振两光子跃迁振幅的完整复数值，可分离直接通道与共振通道对边带相位的各自贡献。
- 2026-11-01｜r113｜回原文｜[paper:2025-2506.07445-circular-rabbitt-goes-under-threshold] TDSE 数值求解：为 He/Ar/Xe 提供含自电离共振与 Cooper 极小的圆偏振双光子电离基准幅值与相位。
- 2026-11-01｜r113｜回原文｜[paper:2014-1401.2878-time-delays-for-attosecond-streaking-in-photoionization-of-n] 单活性电子 TDSE 全模拟：直接模拟 XUV+IR streaking 过程并提取条纹相移，量化 CLC 修正并验证分解式的加和性。
- 2026-11-01｜r113｜回原文｜[paper:2014-1401.2878-time-delays-for-attosecond-streaking-in-photoionization-of-n] 双活性电子 TDSE：检验 SAE 近似的可靠性并纳入部分电子关联对时延的影响。
- 2026-11-07｜r117｜回原文｜[paper:2026-2606.22714-emergence-of-gaussian-entanglement-and-non-gaussia] 强场近似（SFA）结合 TDSE 校验的谐波幅值标度分析：确立偶次谐波幅值对 2ω 场强的线性标度这一核心前提，并论证该线性源于微扰展开+选择律、可外推至库仑修正与固体 HHG。
- 2026-11-07｜r117｜仅简报｜[paper:2026-2609.20559-high-order-correlations-and-ultrafast-wigner-negat] 量子化驱动场下的强场相互作用模型（含时薛定谔方程/强场近似框架）：将 BSV 作为量子化光场而非经典场驱动原子，给出谐波偶极辐射继承驱动场压缩与关联结构的理论图像，是 Wigner 负性出现的根源
- 2026-11-07｜r117｜回原文｜[paper:2025-2512.15370-orientation-dependent-high-harmonic-generation-in-zno] 取向分辨强场 TDSE 数值模拟：沿多个晶向求解含时薛定谔方程，直接给出谐波谱随晶体取向的定量变化。
- 2026-11-07｜r121｜仅简报｜[paper:2026-2601.17164-highly-accurate-semiclassical-strong-field-herman-kluk-propa] TDSE 精确解基准校验：以含时薛定谔方程精确解对比谐波产额与相位，标定了半经典方法的精度与适用范围。
- 2026-11-08｜r127｜仅简报｜[paper:2025-2509.06647-high-harmonic-spectroscopy-of-mobility-edges-in-one-dimensio] 强场含时薛定谔方程实时传播（连续极限非公度势）：直接模拟强场驱动下的电子波包动力学并提取谐波谱，避开布里渊区周期性假设。
- 2026-11-14｜r134｜仅简报｜[paper:2025-2502.11342-revisiting-the-charge-density-wave-superlattice-of-1t-tise2] 选区电子衍射（SAED）：以空间分辨方式映射CDW超晶格反射，识别出两种空间分离、层间排序不同的CDW相。
- 2026-11-15｜r139｜仅简报｜[paper:2026-2603.15293-breakdown-of-the-isotropic-asymptotic-approximation-in-two-c] 全维含时薛定谔方程（TDSE）模拟：包含各向异性分波与残余势的全维从头计算复现实验偏差，确认破缺源于非渐近、非各向同性贡献。
- 2026-11-15｜r139｜仅简报｜[paper:2024-2405.20931-machine-learning-emulator-for-tdse] TDSE 数值求解（强场模拟）：作为真值与训练数据来源，提供机器学习仿真器学习所需的量子动力学样本。
- 2026-11-15｜r139｜仅简报｜[paper:2024-2403.17274-bayesian-parameter-estimation-for-quantum-dynamics] 含时量子动力学正向模型（TDSE类模拟）：作为似然函数的物理内核，把待估参数映射为时间分辨可观测量供与数据比对。

<!-- /methods-settle:v1 -->

# TDSE 求解器

## 林赛的理解

TDSE（含时薛定谔方程）数值求解是 HHG 理论的"ground truth"。Lewenstein 模型是近似，TDSE 是精确（在单活性电子近似下）。我验证任何新理论模型，都会先和 TDSE 结果对比。

## 核心要点

**方法**：
- 单活性电子（SAE）近似 + 模型势
- 分裂算符法（split-operator）或 Crank-Nicolson 时间传播
- 吸收边界（mask function 或 CAP）防边界反射

**输出**：偶极矩 x(t) 的傅里叶变换 → HHG 谱

**局限**：
- 单电子近似（不含多电子关联）
- 计算成本随维度急剧上升（原子 1D 容易，分子 3D 困难）

## 来源

- `hhg-methods-report.md`；arXiv: 0707.4192（改进模型对比 TDSE）

<!-- linsai-wikilinks -->
## 关联概念

- [[1401.2878]]
- [[1609.09852]]
- [[1807.01616]]
- [[2012.10328]]
- [[2020-2012_10328-deep-learning-and-high-harmonic-generation]]
- [[2024-2405_01351-high-harmonic-generation-from-electrons-moving-in-topologica]]
- [[2024-s41467-024-44775-5-spatiotemporal-imaging-and-shaping-of-electron-wave-function]]
- [[2025-2506_07445-circular-rabbitt-goes-under-threshold]]
- [[2025-2512_15370-orientation-dependent-high-harmonic-generation-in-zno]]
- [[2026-2604_06703-strong-field-ionization-of-atoms-with-bright-squeezed-vacuum]]
- [[2026-2610.35991-theoretical-study-of-high-order-harmonic-generation-in-solid]]
- [[2304.11661]]
- [[2311.13309]]
- [[2312.14174]]
- [[2405.01351]]
- [[2407.09662]]
- [[2409.03622]]
- [[2502.08811]]
- [[2506.07445]]
- [[2506.10379]]
- [[2509.06647]]
- [[2511.12372]]
- [[2512.15370]]
- [[2512.24496]]
- [[2604.06703]]
- [[2606.22714]]
- [[2609.20559]]
- [[5-11]]
- [[Berry曲率]]
- [[CEP稳定]]
- [[Continuum-continuum 跃迁振幅的解析表达（含角动量依赖）—— Ji]]
- [[Floquet工程]]
- [[Floquet边带]]
- [[Hamiltonian learning via inverse physics-informed neural networks]]
- [[Han & Wörner (2024)]]
- [[Lewenstein模型]]
- [[RABBIT]]
- [[RABBITT]]
- [[TDDFT]]
- [[TDSE]]
- [[Ueda]]
- [[arpes]]
- [[circular-dichroism]]
- [[rainbow-RABBITT]]
- [[strong-field-ionization]]
- [[三步模型]]
- [[亮压缩真空]]
- [[压缩真空态]]
- [[固体HHG]]
- [[固态高次谐波]]
- [[圆二色性]]
- [[带内/带间电流分解]]
- [[强场电离]]
- [[强场驱动]]
- [[掺杂体系中固态高次谐波生成对激光场强的依赖]]
- [[物理信息神经网络（PINN）]]
- [[电荷密度波]]
- [[相位匹配]]
- [[高次谐波产生]]
- [[高次谐波光谱学]]
- [[高次谐波谱学：一维准晶中的迁移率边]]
<!-- /linsai-wikilinks -->
