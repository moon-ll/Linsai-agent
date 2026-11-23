---
title: "TDSE求解器"
type: "methods"
created: "2026-06-17T12:40:33Z"
updated: "2026-11-21T11:35:57Z"
tags: ["计算方法", "TDSE", "数值模拟", "type/method", "topic/HHG", "status/mature", "status/growing"]
related: ["1401.2878", "1609.09852", "1807.01616", "2012.10328", "2020-2012_10328-deep-learning-and-high-harmonic-generation", "2024-2405_01351-high-harmonic-generation-from-electrons-moving-in-topologica", "2024-s41467-024-44775-5-spatiotemporal-imaging-and-shaping-of-electron-wave-function", "2025-2506_07445-circular-rabbitt-goes-under-threshold", "2025-2512_15370-orientation-dependent-high-harmonic-generation-in-zno", "2026-2604_06703-strong-field-ionization-of-atoms-with-bright-squeezed-vacuum", "2026-2610.35991-theoretical-study-of-high-order-harmonic-generation-in-solid", "2304.11661", "2311.13309", "2312.14174", "2405.01351", "2407.09662", "2409.03622", "2502.08811", "2506.07445", "2506.10379", "2509.06647", "2511.12372", "2512.15370", "2512.24496", "2604.06703", "2606.22714", "2609.20559", "5-11", "Berry曲率", "CEP稳定", "Continuum-continuum 跃迁振幅的解析表达（含角动量依赖）—— Ji", "Floquet工程", "Floquet边带", "Hamiltonian learning via inverse physics-informed neural networks", "Han & Wörner (2024)", "Lewenstein模型", "RABBIT", "RABBITT", "TDDFT", "TDSE", "Ueda", "arpes", "circular-dichroism", "rainbow-RABBITT", "strong-field-ionization", "三步模型", "亮压缩真空", "压缩真空态", "固体HHG", "固态高次谐波", "圆二色性", "带内/带间电流分解", "强场电离", "强场驱动", "掺杂体系中固态高次谐波生成对激光场强的依赖", "物理信息神经网络（PINN）", "电荷密度波", "相位匹配", "高次谐波产生", "高次谐波光谱学", "高次谐波谱学：一维准晶中的迁移率边"]
source_raw: ""
growth_stage: "mature"
confidence: 0.9
aliases: ["TDSE-solver", "time-dependent-schrodinger", "含时薛定谔求解"]
updated_at: "2026-11-21T11:35:57Z"
settled_count: 43
---

<!-- methods-settle:v1 -->

## 原理

TDSE求解器通过数值求解含时薛定谔方程给出强场体系的第一性原理响应：既作为深度学习正/逆网络的物理引擎、机器学习仿真器真值与贝叶斯参数估计似然内核，又作为量子计量学基准验证SFA框架Fisher信息结论，并为非绝热隧穿电离中的通道分解与时间延迟理论提供基准验证；在量子光HHG方向经TDSE/SFA校验确立偶次谐波幅值对2ω场强的线性标度并支撑量子化BSV驱动下纠缠谐波态刻画；含库仑模拟中作为合成条纹谱、相位分辨attoclock与rainbow条纹检索真值基准，可升级至双电子全关联TDSE或RMT多体TDSE（F⁻九电子）；阿秒条纹方向以从头TDSE验证亚阿秒可加分解，且全维TDSE含各向异性分波与残余势可复现两光子电离实验偏差、确认非偶极/非各向同性破缺来源，开源实现Qprop-nd以Coulomb-propagator/FGH算法在单活跃电子框架下纳入非偶极项；求解域推广至固态（多能带/紧束缚/实空间/拓扑模型/取向分辨ZnO/非公度势mobility edge/MgO Cooper极小）并作为半经典方法与绝热近似精度标定基准；在无序固态体系中TDSE/TDDFT类含无序量子动力学模拟用于区分能带结构与退相干通道贡献；软件实现上TDSE-Z以弱形式Galerkin离散化BenDaniel-Duke厄米动能算符配几何自适应B样条网格统一求解原子/分子/半导体体系一至三维强场动力学，GPU卸载静态本征、CPU优化时间传播。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 隧穿劈裂WKB符合精度（GaAs/Al0.3Ga0.7As双量子阱） | 亚百分位（sub-percent，跨两个以上量级复现指数衰减） | paper:2026-2608.18472-unified-strong-field-dynamics-simulations-from-ato |
| TDSE-Z求解维度 | 1至3维 | paper:2026-2608.18472-unified-strong-field-dynamics-simulations-from-ato |
| 并行扩展规模 | 数百CPU核强扩展性稳健 | paper:2026-2608.18472-unified-strong-field-dynamics-simulations-from-ato |
| 偶次谐波幅值对2ω场强的标度律 | 线性标度（微扰展开+选择律） | paper:2026-2606.22714-emergence-of-gaussian-entanglement-and-non-gaussia |
| BSV驱动压缩参数工作区间 | r ~ 10（e^{±2r} ~ 10^{±8}） | paper:2026-2606.22714-emergence-of-gaussian-entanglement-and-non-gaussia |
| ZnO驱动波长 | 3.2 μm（~45 fs FWHM，I = 1 TW/cm²） | paper:2025-2512.15370-orientation-dependent-high-harmonic-generation-in-zno |
| MgO固态TDSE谐波谱Cooper极小位置 | ~16 eV（不随强度/脉宽移动） | paper:2019-1911.12092-cooper-minimum-of-high-harmonic-spectra-from-mgo-cryst |
| Ne 2s-2p相对条纹时延（Schultze实验值） | 21 ± 5 as（理论约为其一半） | paper:2014-1401.2878-time-delays-for-attosecond-streaking-in-photoionization-of-n |
| RABBITT边带振荡频率 | 2ω（S2q(τ)=A+Bcos[2ωτ+C]） | paper:2025-2506.07445-circular-rabbitt-goes-under-threshold |
| uRABBITT阈下条件 | (2q−1)ω < |Ei| < (2q+1)ω | paper:2025-2506.07445-circular-rabbitt-goes-under-threshold |
| a-Si隧穿电离增强实验驱动波长 | 3.6 μm，约50 fs脉宽 | paper:2026-2511.14678-giant-enhancement-of-attosecond-tunnel-ionization- |
| Ga离子注入剂量范围 | 2×10¹² – 4×10¹⁶ ions·cm⁻² | paper:2026-2511.14678-giant-enhancement-of-attosecond-tunnel-ionization- |

## 适用边界

TDSE逐点全维求解成本高：作为训练标签源/仿真器真值/贝叶斯似然内核时可靠域由参数空间覆盖与采样成本决定，多电子关联需双电子TDSE或RMT多体TDSE（成本随电子数急剧攀升；复杂固态无序体系常需TDDFT类近似），Ne条纹2s-2p时延理论值偏小约2倍且可加分解以XUV一阶微扰为前提，非偶极扩展（如Qprop-nd）限于单活跃电子框架且非偶极项适用性受波长/强度限制，量子光HHG高斯纠缠结论限于低耗尽与微扰线性区（r增大失效），固态各实现限于各自模型设定、不含电子-电子关联与宏观传播，含无序模拟需能区分能带结构变化与退相干通道对HHG谱的混合贡献、动态无序与液相体系尚待扩展；TDSE-Z类有效质量框架以单活性电子为前提、时间传播引擎目前仅CPU优化，且维度对HHG谱完全捕获至关重要、低维结果不可直接外推至真实三维体系；随机量子光场采样方案的统计精度受轨迹样本数限制；作为非绝热隧穿电离时延理论基准时，其验证有效性仍以模型哈密顿量（如通道分解近似）的设定为前提。

## 代表作

- paper:2026-2608.18472-unified-strong-field-dynamics-simulations-from-ato
- paper:2026-2609.35401-qprop-nd-a-nondipole-extension-of-the-qprop-packag
- paper:2026-2609.25753-photon-statistics-control-of-strong-field-rydberg-
- paper:2026-2610.35440-harp-a-simulation-tool-for-high-order-harmonic-gen
- paper:2026-2610.08609-time-delay-in-nonadiabatic-tunneling-ionization
- paper:2025-2506.07445-circular-rabbitt-goes-under-threshold
- paper:2014-1401.2878-time-delays-for-attosecond-streaking-in-photoionization-of-n
- paper:2020-2012.10328-deep-learning-and-high-harmonic-generation

## 证据日志

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
- 2026-11-20｜r1｜回原文｜[paper:2026-2608.18472-unified-strong-field-dynamics-simulations-from-ato] 含时薛定谔方程（TDSE）数值传播：作为框架核心引擎，统一求解原子/分子/半导体有效质量体系的强场动力学。
- 2026-11-20｜r1｜仅简报｜[paper:2026-2609.25753-photon-statistics-control-of-strong-field-rydberg-] 含时薛定谔方程（TDSE）求解：用于在采样场轨迹下演化原子波函数并统计里德堡态激发概率。
- 2026-11-20｜r1｜仅简报｜[paper:2026-2610.35440-harp-a-simulation-tool-for-high-order-harmonic-gen] 单原子响应（SFA/TDSE偶极）：提供含相位与频率依赖的微观谐波源项，作为传播计算的输入。
- 2026-11-21｜r1｜回原文｜[paper:2026-2511.14678-giant-enhancement-of-attosecond-tunnel-ionization-] 含无序的强场量子动力学模拟（如 TDDFT 或 TDSE 模型）：区分无序对能带结构与相干性/退相干通道的各自贡献
- 2026-11-21｜r1｜仅简报｜[paper:2026-2609.35401-qprop-nd-a-nondipole-extension-of-the-qprop-packag] TDSE 数值求解（Coulomb-propagator / FGH 算法）：给出单活跃电子框架下含非偶极项的推广形式与开源实现
- 2026-11-21｜r1｜仅简报｜[paper:2026-2610.08609-time-delay-in-nonadiabatic-tunneling-ionization] 含时薛定谔方程（TDSE）数值模拟：为通道分解与时间延迟理论提供基准验证。

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
