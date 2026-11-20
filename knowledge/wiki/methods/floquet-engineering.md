---
title: "floquet-engineering"
type: "methods"
created: "2026-09-06T07:31:00Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "type/method"]
related: ["2018-1807.02525-floquet-theoretical-formulation-and-analysis-of-high-harmoni", "2019-1905.05205-disorder-effects-on-the-origin-of-high-order-harmonic-genera", "2026-2503_04431-observation-of-non-adiabatic-landau-zener-tunnelin", "2026-2607.19242-time-resolved-arpes-in-pumped-excitonic-systems-floquet-phys", "2026-2608_11192-floquet-engineering-of-topological-phases-and-magneto-optica", "2026-s41567-026-03429-7-optical-control-of-electrons-in-a-floquet-topological-insula", "2302.00604", "2302.03918", "2311.13309", "2407.17917", "2502.11967", "2503.04431", "2503.21698", "2504.00122", "2504.06130", "2505.19894", "2506.02238", "2507.03791", "2508.14212", "2510.02452", "2602.14875", "2602.20862", "2603.28725", "2603.29106", "2606.31867", "2607.02717", "2607.19483", "2607.19897", "2608.11192", "2609.06480", "2609.17500", "2609.28293", "Berry曲率", "Berry曲率热点处的非绝热Hall效应（Floquet-Bloch Wilson loop有效性相关）", "Chern数", "Dynamic moiré-like band modulation in Dirac materials via multi-beam optical interference", "Floquet工程", "Floquet能带工程", "Floquet边带", "Geometric Floquet condition for quantum adiabaticity", "Lewenstein模型", "MnPS3", "Observation of Floquet-induced gap in graphene", "arpes", "交变磁体", "光致反常霍尔效应", "半导体Bloch方程", "双色调Floquet驱动在2D补偿磁体中产生巨垂直Edelstein极化", "反常霍尔效应", "层间耦合", "强场驱动", "拓扑绝缘体", "拓扑表面态", "相位匹配", "自旋劈裂", "量子度规", "黑磷中赝自旋选择的Floquet能带工程"]
source_raw: ""
growth_stage: "mature"
confidence: 0.9
updated_at: "2026-11-15T10:29:56Z"
settled_count: 44
aliases: ["Floquet 工程化", "Floquet工程", "Floquet理论"]
---

<!-- methods-settle:v1 -->

## 原理

Floquet工程以周期光场将固体哈密顿量化为Floquet-Bloch准能级与边带，其严格基础是Sambe扩展希尔伯特空间中把时间作为坐标的 K = H(t) − i∂_t 本征问题（给出准能量谱与周期性本征射线并作为绝热展开的严格基，该扩展空间静态本征问题表示还支持逐准能隙含反常π能隙的绕数/动态不变量拓扑分析、判定对称性约束破缺并区分无静态对应的驱动诱导边界态），将该Sambe扩展推进到BdG哈密顿量的光子扇区可精确加倍Cooper对关联流形（对称性加倍机制）并在Sigrist-Ueda/Balian-Werthamer自旋-宇称分类中新增Floquet频率宇称量子数、预言奇频-奇宇称-轨道单重态新配对通道及Floquet Majorana平带，高频非共振时Floquet-Magnus/van Vleck/Floquet-Schrieffer-Wolff展开可将其约化为时间平均的静态有效哈密顿量（在Ω大于带宽时近解析成立，量化光子缀饰、能带反转与有效规范场生成，并可在非共振圆偏振光下解析导出等效静态哈密顿量、揭示二聚化晶格上光致p波自旋劈裂项的来源与解析形式，Floquet-Schrieffer-Wolff展开进一步把圆偏振驱动系统约化为与磁八极矩同对称性的光致静态项即推广到多极矩的逆法拉第效应，高频/偏共振展开亦能明确标识破坏C̄2z∥T联合对称性、生成偶宇称单向极化自旋劈裂项的光致来源，线偏振光亦经高频展开给出光修饰跃迁各向异性与等效对称性破缺项、解释其足以诱导反常霍尔，椭圆偏振高频辐照经van Vleck展开映射为静态等效哈密顿量并以光致手性质量项在M/Γ带交叉处开拓扑能隙，离共振圆偏振驱动的高频展开亦在光子频率远离能带的高频区将周期驱动映射为准静态有效哈密顿量、给出符号随螺旋度可调的光致质量项（用于层间耦合体系中Floquet驱动拓扑相变的判定），双圆偏振驱动以两束反向旋转圆偏振光的振幅比为单一旋钮在时间平均有效哈密顿量层面实现级联拓扑相变的全光调谐）用于调控拓扑、Berry曲率、自旋轨道耦合、磁序、RKKY、频率转换、moiré能带与磁激发谱（如将圆偏振光约化为时间反演奇的有效磁相互作用项，使奇宇称磁振子分裂具有对光强与螺旋度的明确依赖，并以非平衡手段破坏有效时间反演、打开拓扑磁振子能隙；光场亦可视为对布洛赫带几何的周期调制、经周期驱动带混合给出螺旋度依赖的光致Berry曲率即光伏霍尔效应的统一机制；周期性圆偏振驱动可在Γ点以±1级replica带与母带反转实现陈数逐级可控的激光能带工程如三角铋烯），并可由周期光场动力学破缺PT/tT联合对称性实现反铁磁体到交变磁体（含由p波自旋劈裂刻画的光致奇宇称交变磁体）的光致瞬态转变，Floquet拓扑由准能隙Chern数与Rudner绕数等周期驱动专属不变量刻画（解释体Chern数为零却存在手性边界模的反常体边界对应，并以Rudner绕数量化反常Floquet-Anderson绝缘体中被泵浦的边界模式数即边界希尔伯特空间的量子化输运），周期调制诱导复隧穿/人工规范场的Floquet蜂窝光晶格提供可控规范通量与Floquet拓扑能带的干净平台以系统扫描无序-拓扑相互作用并指导实验参数选择，Floquet微运动算符分解把演化算符U(k,t)与等效哈密顿量分离、将量子度规推广为动量-时间空间中的时间分辨量以捕捉驱动周期内被时间平均抹掉的几何信息，GKSL量子主方程在Floquet表象写入Lindblad耗散以严格刻画周期驱动开放体系的非平衡稳态、逆法拉第效应的Floquet边带理论阐明圆偏振光诱导瞬态磁化的微观机制（手性、失谐与散射时间决定磁化符号与幅度），Floquet基下的绝热微扰展开以非绝热耦合⟨u_m|∂_t u_n⟩与准能隙之比给出跃迁幅上界（几何Floquet绝热性判据的核心中间量），Floquet-Keldysh非平衡格林函数可同时处理强场驱动和无序散射并逐谐波求得电流响应，Floquet准能级理论可给出任意时刻的谐波电流解析分量且Floquet定理可把周期驱动下的激光谐波产生纳入同一准能图像、由动力学对称性给出谐波频率选择的等价判据，强场下隧穿对象由裸带改为周期场修饰的准能带流形、回避交叉发生在Floquet边带之间并成为非绝热Landau-Zener隧穿通道，结合边带间距、出现时序与寿命的复制带分析能够区分激光直接驱动和泵浦激子内禀振荡场产生的Floquet物理（E(k)+nħω复制带映射可将观测边带归回准能带结构），边带指标n可视为离散自由度在Fermi边附近定义实验可测的边带占据谱，全对角化Floquet能带理论可解释边带折叠、回避交叉隙与带隙重整化的能带结构来源（如黑磷赝自旋选择能带工程），Floquet准能带/光致能带重整化分析定量给出带隙与自旋劈裂随场强和频率的重整及副本能带杂化，纳入光学Stark与Bloch-Siegert位移的Floquet哈密顿量（与半导体Bloch方程微扰解联用，给出强度依赖二阶极化率 |χyyy|² = |χint(1+αI)|²）把非微扰光致能带重整与微扰参量极化统一到同一框架并界定光谱学'调制区'与'探测区'的过渡，数值实现上可用Fourier-Sambe频域Floquet展开将含时哈密顿量在光子复本空间展开并对角化Floquet矩阵（已有Julia实现），结合Bloch定理与Floquet定理对强场驱动的周期晶体逐k点求解、直接获得准能带与Floquet态及准能谱的布里渊区结构，从而免去长时域演化即得到稳态谐波响应。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 石墨烯Floquet回避交叉能隙（扩展区图像定量拟合） | 241±18 meV | paper:2026-2603.28725-observation-of-floquet-induced-gap-in-graphene |

## 适用边界

Floquet-Magnus/van Vleck（含Floquet-Schrieffer-Wolff及线偏振/椭圆偏振/双圆偏振/离共振圆偏振等高频展开）仅在驱动频率Ω大于带宽且远离共振时收敛（且收敛性依赖是否纳入导带等远程能带的虚跃迁），共振强场或开放耗散体系须回到全对角化Floquet能带、Floquet-Keldysh或GKSL框架处理；Floquet拓扑判定不能仅凭静态体Chern数（体Chern数为零仍可承载手性边界模，且须逐准能隙含反常π能隙以绕数/动态不变量分析并区分无静态对应的驱动诱导边界态），须辅以准能隙Chern数/Rudner绕数等周期驱动专属不变量；频域Fourier-Sambe对角化以有限光子复本截断求解、只给出周期稳态谐波响应而无法覆盖瞬态建立与失相过程（周期内微运动几何信息即被时间平均框架抹掉、须借助微运动分解的时间分辨量子度规），瞬态区仍受准能带的亚周期建立与失相以及样品加热/损伤的光强上限约束。

## 代表作

- paper:2024-2411.13954-light-induced-renormalization-of-the-band-structure-of-chira
- paper:2026-2302.03918-geometric-floquet-condition-for-quantum-adiabaticity
- paper:2026-2606.31550-floquet-majorana-flat-bands-and-emergent-cooper-pair-symmetr
- paper:2025-2508.01783-floquet-theory-and-applications-in-open-quantum-and-classica
- paper:2026-2603.28725-observation-of-floquet-induced-gap-in-graphene
- paper:2023-2311.13309-buildup-and-dephasing-of-floquet-bloch-bands-on-subcycle-tim
- paper:2024-2403.09935-topological-frequency-conversion-in-rhombohedral-multilayer
- paper:2026-2503.04431-observation-of-non-adiabatic-landau-zener-tunnelin

## 证据日志

- 2026-10-30｜r102｜仅简报｜[paper:2023-2302.00604-pseudospin-selective-floquet-band-engineering-in-black-phosp] Floquet能带理论（全对角化）：解释边带折叠、避免交叉能隙与带隙重整化的能带结构来源
- 2026-10-31｜r104｜仅简报｜[paper:2025-2505.31411-odd-parity-magnons] Floquet 高频展开：将圆偏振光约化为时间反演奇的有效磁相互作用项，给出分裂对光强与螺旋度的明确依赖。
- 2026-11-01｜r110｜仅简报｜[paper:2026-2605.31411-odd-parity-magnons] 圆偏振光 Floquet 调控：作为非平衡手段破坏有效时间反演、打开拓扑磁振子能隙，提示光控磁振子拓扑的光学路径。
- 2026-11-01｜r112｜仅简报｜[paper:2024-2501.03798-build-up-and-dephasing-of-floquet-bloch-bands-on-subcycle-ti] Floquet-Bloch 准能带分析（E(k)+nħω 复制带）：把观测边带映射回准能带结构，量化修饰带随场包络的时序演化。
- 2026-11-01｜r112｜仅简报｜[paper:2026-2604.05244-edge-universality-in-floquet-sideband-spectra] Floquet 边带占据分析：将边带指标 n 视为离散自由度，定义了 Fermi 边附近边带占据谱这一问题框架。
- 2026-11-06｜r116｜仅简报｜[paper:2024-2410.17747-transition-from-antiferromagnets-to-altermagnets-symmetry-br] Floquet周期驱动工程：提出用周期性光场动力学破缺PT/tT对称性，实现光诱导的AFM→AM瞬态转变，是光控物态调控的新对称性机制。
- 2026-11-07｜r117｜仅简报｜[paper:2025-2508.01783-floquet-theory-and-applications-in-open-quantum-and-classica] GKSL 量子主方程（Floquet 表象）：将 Lindblad 耗散写入 Floquet 基，严格刻画周期驱动的非平衡稳态，是激光驱动耗散固态体系的标准理论工具（fallback：LLM 融合失败，附录式追加）
- 2026-11-07｜r117｜仅简报｜[paper:2025-2508.01783-floquet-theory-and-applications-in-open-quantum-and-classica] Floquet 高频展开 / van Vleck 有效哈密顿量：在 Ω 大于带宽时给出近解析有效哈密顿量，量化光子缀饰、能带反转与有效规范场的生成（fallback：LLM 融合失败，附录式追加）
- 2026-11-07｜r117｜仅简报｜[paper:2025-2508.01783-floquet-theory-and-applications-in-open-quantum-and-classica] 逆法拉第效应的 Floquet 边带理论：阐明圆偏振光诱导瞬态磁化的微观机制，连接光学驱动与磁性调控，手性、失谐、散射时间决定磁化符号与幅度（fallback：LLM 融合失败，附录式追加）
- 2026-11-07｜r120｜仅简报｜[paper:2024-2411.13954-light-induced-renormalization-of-the-band-structure-of-chira] Floquet 准能带/光致能带重整化分析：把含时能带映射为准能谱，量化带隙与自旋劈裂随场强、频率的重整及副本能带杂化。
- 2026-11-07｜r122｜仅简报｜[paper:2025-2507.08635-dynamical-symmetries-in-laser-harmonic-generation-via-a-cubi] Floquet定理：把周期驱动下的谐波产生纳入Floquet准能图像，给出频率选择的等价判据。
- 2026-11-08｜r123｜仅简报｜[paper:2026-2611.00354-a-julia-implementation-of-floquet-bloch-theory-for] Fourier-Sambe 频域 Floquet 展开：将含时哈密顿量在光子复本空间展开并对角化 Floquet 矩阵，直接获得准能带与 Floquet 态，避免长时域演化即可得到稳态谐波响应。
- 2026-11-08｜r123｜仅简报｜[paper:2026-2611.00354-a-julia-implementation-of-floquet-bloch-theory-for] Floquet-Bloch 理论：结合 Bloch 定理与 Floquet 定理对强场驱动的周期晶体逐 k 点求解，给出准能谱的布里渊区结构。
- 2026-11-15｜r137｜仅简报｜[paper:2025-2508.18360-light-induced-odd-parity-altermagnets-on-dimerized-lattices] Floquet理论/高频展开：在非共振圆偏振光下推导等效静态哈密顿量，揭示光致p波自旋劈裂项的来源与解析形式。
- 2026-11-15｜r137｜仅简报｜[paper:2026-2605.08049-light-driven-octupolar-inverse-faraday-effect-and-multipolar] Floquet-Schrieffer-Wolff高频展开：将圆偏振驱动系统地约化为时间平均的静态有效项，揭示出与磁八极矩同对称性的光致项。
- 2026-11-15｜r137｜仅简报｜[paper:2026-2601.03358-light-induced-even-parity-unidirectionally-polarized-spin-sp] Floquet 理论（高频/偏共振展开）：给出圆偏振驱动的等效哈密顿量，明确标识出破坏 C̄2z∥T 并生成偶宇称自旋劈裂项的光致来源。
- 2026-11-15｜r137｜仅简报｜[paper:2025-2508.20154-probing-disorder-driven-topological-phase-transitions-via-to] Floquet 工程蜂窝光晶格（周期调制诱导复隧穿/人工规范场）：提供可控规范通量与 Floquet 拓扑能带的干净平台，用于系统扫描无序-拓扑相互作用。
- 2026-11-15｜r137｜仅简报｜[paper:2025-2508.20154-probing-disorder-driven-topological-phase-transitions-via-to] Floquet 拓扑不变量与准能谱分析（gap Chern 数/绕数）：解释体 Chern 数为零但存在手性边界模的反常体边界对应，并指导实验参数选择。
- 2026-11-15｜r137｜仅简报｜[paper:2026-2611.02785-quantized-pumping-of-boundary-hilbert-space-in-chiral-floque] Rudner 绕数不变量（Floquet 拓扑不变量）：量化非相互作用 AFAI 中被泵浦的边界模式数目，作为单粒子手征 Floquet 拓扑的判据。
- 2026-11-15｜r137｜仅简报｜[paper:2026-2611.02785-quantized-pumping-of-boundary-hilbert-space-in-chiral-floque] 反常 Floquet-Anderson 绝缘体（AFAI）模型：提供体局域化加手征边缘态的典型平台，演示边界希尔伯特空间的量子化输运。
- 2026-11-15｜r138｜仅简报｜[paper:2026-2603.06486-linearly-polarized-light-induced-anomalous-hall-effect-and-t] Floquet 高频展开（Floquet-Magnus / van Vleck 有效哈密顿量）：给出光修饰跃迁各向异性与等效对称性破缺项，解释线偏振光为何足以诱导反常霍尔。
- 2026-11-15｜r138｜仅简报｜[paper:2025-2505.06078-unified-theory-of-the-photovoltaic-hall-effect-by-field-and] Floquet/周期驱动带混合：将光场视为对布洛赫带几何的周期调制，给出光致Berry曲率及其螺旋度依赖的产生机制。
- 2026-11-15｜r138｜仅简报｜[paper:2026-2602.00569-floquet-quantum-geometry-in-periodically-driven-topological] Floquet 微运动算符分解（演化算符 U(k,t) 与等效哈密顿量分离）：使量子度规被推广为动量-时间空间中的时间分辨量，捕捉驱动周期内被平均掉的几何信息。
- 2026-11-15｜r138｜仅简报｜[paper:2025-2509.19992-breakdown-of-the-symmetry-constraint-in-a-floquet-topologica] Floquet 理论 / Sambe 扩展空间表示：将时间周期驱动系统映射为扩展空间静态本征问题，给出准能谱并逐准能隙分析拓扑，是判定约束破缺的框架基础。
- 2026-11-15｜r138｜仅简报｜[paper:2025-2509.19992-breakdown-of-the-symmetry-constraint-in-a-floquet-topologica] Floquet 拓扑不变量（绕数/动态不变量）：刻画各准能隙（含反常 π 能隙）的拓扑，区分静态无对应的驱动诱导边界态。
- 2026-11-15｜r138｜仅简报｜[paper:2025-2509.08068-laser-engineered-γ-point-topology-in-trigonal-bismuthene] Floquet 能带工程（周期性圆偏振驱动）：±1 级 replica 带与母带在 Γ 点反转，实现激光对陈数的逐级、可控调控。
- 2026-11-15｜r138｜仅简报｜[paper:2026-2610.26163-bicircular-light-tunable-topological-phases-and-nonlinear-ha] 双圆偏振 Floquet 工程：以两束反向旋转圆偏振光的振幅比为单一旋钮，在时间平均有效哈密顿量层面实现级联拓扑相变的全光调谐。
- 2026-11-15｜r138｜仅简报｜[paper:2026-2610.26163-bicircular-light-tunable-topological-phases-and-nonlinear-ha] Floquet 拓扑不变量计算：标识级联相变中各相的拓扑类别并定位临界振幅比。
- 2026-11-15｜r138｜仅简报｜[paper:2026-2602.05745-anomalous-thermoelectric-and-thermal-hall-effects-in-irradia] 高频 Floquet 有效哈密顿量（van Vleck 高频展开）：将椭圆偏振高频光辐照映射为静态等效哈密顿量，揭示光致手性质量项在 M/Γ 带交叉处开拓扑能隙的机制。
- 2026-11-15｜r139｜仅简报｜[paper:2026-2603.24551-interlayer-coupling-and-floquetdriven-topological-phases-in] Floquet高频展开（离共振圆偏驱动有效哈密顿量）：在光子频率远离能带的高频区将周期驱动映射为准静态有效哈密顿量，得到符号随螺旋度可调的光致质量项。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2018-1807.02525-floquet-theoretical-formulation-and-analysis-of-high-harmoni]]
- [[2019-1905.05205-disorder-effects-on-the-origin-of-high-order-harmonic-genera]]
- [[2026-2503_04431-observation-of-non-adiabatic-landau-zener-tunnelin]]
- [[2026-2607.19242-time-resolved-arpes-in-pumped-excitonic-systems-floquet-phys]]
- [[2026-2608_11192-floquet-engineering-of-topological-phases-and-magneto-optica]]
- [[2026-s41567-026-03429-7-optical-control-of-electrons-in-a-floquet-topological-insula]]
- [[2302.00604]]
- [[2302.03918]]
- [[2311.13309]]
- [[2407.17917]]
- [[2502.11967]]
- [[2503.04431]]
- [[2503.21698]]
- [[2504.00122]]
- [[2504.06130]]
- [[2505.19894]]
- [[2506.02238]]
- [[2507.03791]]
- [[2508.14212]]
- [[2510.02452]]
- [[2602.14875]]
- [[2602.20862]]
- [[2603.28725]]
- [[2603.29106]]
- [[2606.31867]]
- [[2607.02717]]
- [[2607.19483]]
- [[2607.19897]]
- [[2608.11192]]
- [[2609.06480]]
- [[2609.17500]]
- [[2609.28293]]
- [[Berry曲率]]
- [[Berry曲率热点处的非绝热Hall效应（Floquet-Bloch Wilson loop有效性相关）]]
- [[Chern数]]
- [[Dynamic moiré-like band modulation in Dirac materials via multi-beam optical interference]]
- [[Floquet工程]]
- [[Floquet能带工程]]
- [[Floquet边带]]
- [[Geometric Floquet condition for quantum adiabaticity]]
- [[Lewenstein模型]]
- [[MnPS3]]
- [[Observation of Floquet-induced gap in graphene]]
- [[arpes]]
- [[交变磁体]]
- [[光致反常霍尔效应]]
- [[半导体Bloch方程]]
- [[双色调Floquet驱动在2D补偿磁体中产生巨垂直Edelstein极化]]
- [[反常霍尔效应]]
- [[层间耦合]]
- [[强场驱动]]
- [[拓扑绝缘体]]
- [[拓扑表面态]]
- [[相位匹配]]
- [[自旋劈裂]]
- [[量子度规]]
- [[黑磷中赝自旋选择的Floquet能带工程]]
<!-- /linsai-wikilinks -->
