---
title: "sbe-bloch-equations"
type: "methods"
created: "2026-09-20T03:03:21Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "type/method"]
related: ["1409.2725", "1809.08109", "2021-2112_01745-high-harmonic-spectroscopy-of-light-driven-nonlinear-anisotr", "2023-2310_17007-unambiguous-discrimination-of-high-harmonic-generation-mecha", "2024-s41567-024-02640-8-ultrafast-high-harmonic-spectroscopy-of-solids", "2025-2510_12443-self-attention-enabled-quantum-path-analysis-of-high-harmoni", "2025-2512_01712-effects-of-zero-point-motion-in-the-high-harmonic-generation", "2026-2609.20085-transient-high-harmonic-generation-from-solids-fro", "2026-2609_20085-transient-high-harmonic-generation-from-solids-from-spectros", "2109.04508", "2111.10986", "2112.01745", "2206.11935", "2310.17007", "2401.12929", "2405.17673", "2408.09364", "2410.11542", "2410.17077", "2501.06885", "2503.11432", "2504.01640", "2508.07869", "2508.16494", "2510.12443", "2510.15207", "2510.22064", "2511.05112", "2511.13114", "2512.01712", "2512.15370", "2602.22463", "2603.05346", "2604.13901", "2605.28236", "2607.23652", "2608.20306", "2609.20085", "2610.15251", "5-11", "Berry 曲率", "Nodal-Line Semimetals 的非线性光学谱学：NbSi_xTe_2 二维节线半金属的 HHG 理论", "PLAN", "TDDFT", "TDSE", "Unveiling the Role of Electron-Phonon Scattering in Dephasing High-Order Harmonics in Solids", "bayesian-inference", "strong-field-ionization", "半导体Bloch方程", "单色激光场调控固体电子动力学以优化阿秒脉冲产生", "反常速度", "固体HHG", "固体超快高次谐波光谱学", "固体高次谐波", "固体高次谐波产生", "带内/带间电流分解", "带内载流子动力学对二维材料光学性质的影响：I. 一般理论", "强驱动固体中电子—空穴相干性的探测", "扭曲双层石墨烯中高次谐波产生的激光椭圆率依赖", "拓扑表面态", "波形控制", "莫尔超晶格", "谷分辨高次谐波：探测 Dirac 锥之外的对称性破缺", "谷极化", "贝叶斯反演", "阿秒瞬态吸收", "非线性光学", "高次谐波产生", "高次谐波光谱学"]
source_raw: ""
growth_stage: "mature"
confidence: 0.9
updated_at: "2026-11-15T10:28:44Z"
settled_count: 48
aliases: ["SBE", "半导体布洛赫方程"]
---

<!-- methods-settle:v1 -->

## 原理

半导体布洛赫方程（k 空间含时密度矩阵传播，Houston 基或长度/Wannier 规范，亦可实现为含时紧束缚+密度矩阵模拟，属 TDSE/密度矩阵/TDDFT 三类固体 HHG 模拟中的密度矩阵类，定位上桥接解析模型与 TDDFT 的中间强度区）在强场下以长度规范非微扰时间演化直接获得含高阶谐波成分的电流、绕开微扰展开阶数限制，长度规范方程显含带间相位积累、偶极诱导跃迁、带内加速（iF·∇k）与唯象退相四项，Houston 基形式确立为强场下布居与相干演化的标准框架（各 k 点方程解耦便于并行，配合 FFT 插值矩阵元后计算量可与稳态基相当，且已有并行开源实现），演化带间极化与载流子布居（含自旋与谷分辨），统一描述带间极化—带内电流耦合与退相干，定量分解带内/带间电流以实现固体 HHG 机制归属、偏振—自旋/谷极化映射、T2/γ(k) 假设检验与低次谐波峰位归属（数百次波长扫描逐一定位二次/三次谐波的偶极允许跃迁，2402.11449，简报级），多能带框架下可进一步逐导带分解各导带对谐波产率与平台的贡献（ZnO，ad5d95，简报级），含带内电流、带间极化与唯象失相的 SBE 可同时再现谐波谱与非线性吸收的角度/强度依赖，并作为连接 HHG 与 ATAS/ATRS 的主流理论桥梁；宏观传播层面，Maxwell-SBE 自洽耦合首次将体材料 HHG 的辐射源项与驱动场演化双向耦合、替代单向驱动近似，可区分反射/透射谐波谱的传播诱导差异、量化传播对透射谱与电子结构关联解释的干扰（2608.20306，回原文）；驱动场维度进一步扩展至量子化光场：将驱动光作为量子化场而非经典场代入 SBE 非微扰模拟，直接给出禁戒级次出现及其与非经典参数的依赖谱学证据（2605.28236，回原文定位片段仅含选择规则附录与文献、方法细节待回溯），涡旋/OAM 结构光驱动亦在双带加弛豫近似下给出带内/带间分解的微观贡献（2404.10293，简报级）；标准 SBE 同时定义了空间均匀驱动场极限，被用作对比验证空间非均匀系数方程所给偶次谐波与增强效应的基准框架（2508.00273，简报级）；含 Berry 曲率的半经典波包/SBE 模拟经在波包动力学中引入反常速度项 E×Ω(k) 将框架扩展至反常 HHG 表征，定量复现其波长与强度依赖特征并指认谐波机制（2206.11935，简报级）；多带/含 e-h 关联扩展推广至莫尔、节线/Weyl/磁性 WSM、Haldane 拓扑、倾斜-劈裂 Weyl 锥（手性光发射）、自旋-动量锁定 massive Dirac 拓扑表面态、拓扑能带 HHG 及单层/双层 TMD 层依赖响应，并延伸为 SWE 等价性交叉验证基准与单层 hBN 两带固体阿秒脉冲优化正向设计工具；相互作用维度上，含库仑修正的密度矩阵/半导体布洛赫方程多体扩展在标准平均场之外纳入载流子-载流子相互作用，追踪极化、布居与退相干随场的演化，用于描述单层材料 HHG 的多体增强（s41467-024-50534-3，简报级）；唯象 T2 物理地位经澄清（空间/传播诱导轨迹过滤与零点涨落系综平均的有效参数化，微观实空间退相干可替换超短拟合 T2，2410.04512 简报级），Wannier 规范退相算符经诊断修正（SDO 替代不适定的 CDO，2503.11432 与 2508.07869 原文确认）；带内电流—带间极化相干相消与退相再入（∼(ωT2)^−1 幂律）构成退相强度实验可测特征（2503.11432）；多带 SBE 再现实验谐波相位结构与瞬态带结构关联（2022.01010/2309.00734，简报级），ZnO 取向分辨 HHG 解读（2512.15370 原文确认，与实验仅定性一致）；2511.13114 经原文核对实为 rt-TDDFT、其结论不计入 SBE 方法能力；2603.05346（脉宽敏感 HHG 与手性 WSM RhSi）主文明示采用 TDDFT 计算、简报的 SBE/Houston 归属未获原文支持，其结论暂不计入 SBE 方法能力，待 Methods/SI 回溯确认；应用维度进一步延伸至参数反演：SBE 双带前向模型可作为贝叶斯推断流程（BayesHHG）中被代理的物理模拟器、定义参数—谐波谱映射，以能带间隙与失相时间等为反演目标并经 ZnO 体系演示（2301.08636，简报级）。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 磁性WSM两带d·σ模型晶格常数 a=b | 3.437 Å | paper:2021-2112.01745 |
| 磁性WSM两带d·σ模型晶格常数 c | 11.646 Å | paper:2021-2112.01745 |
| 磁性WSM模型跃迁积分 tx/ty/tz | 1.88 / 0.49 / 0.16 eV | paper:2021-2112.01745 |
| 磁性WSM模型Weyl点位置 | (±0.2 rad/au, 0, 0) | paper:2021-2112.01745 |
| MoS2 唯象退相时间 T2 | 100 fs | 方法页存档摘要（早期证据，出处待回原文回溯） |
| NbSe2 唯象退相时间 T2 | 10 fs | 方法页存档摘要（早期证据，出处待回原文回溯） |
| 多Weyl体系唯象退相时间 T2 | 1.5 fs | 方法页存档摘要（早期证据，出处待回原文回溯） |
| 倒空间均匀k无关T2拟合实验的典型量级 | 几飞秒量级（order of a few fs） | paper:2026-2609.20085 |
| Vampa等拟合实验所需唯象退相时间 T2 | ≈4 fs | paper:2025-2512.01712 |
| Floss等含宏观光传播模拟所用 T2 | 10 fs | paper:2025-2512.01712 |
| Du & Ma 声学晶格振动等效退相时间（室温，1D碳链） | ~25 fs | paper:2025-2512.01712 |
| Du & Ma 1D碳链 Debye 温度 Θ | 150 K | paper:2025-2512.01712 |

## 适用边界

非微扰优势依赖给定能带结构与相干平均场泵浦近似（静态材料势、忽略载流子-载流子相互作用、非相对论与偶极近似），且隐含空间均匀驱动场假设——空间非均匀场下出现的偶次谐波与增强效应超出均匀场 SBE 描述范围、需非均匀系数方程扩展，SBE 仅作为均匀场极限基准（2508.00273，简报级）；唯象退相 T2 取值材料依赖且倒空间均匀 T2 拟合实验典型仅几飞秒、实为空间/传播诱导轨迹过滤与零点涨落系综平均的有效参数化（仅凭谐波产率无法区分传播效应与微观退相干）——Maxwell-SBE 自洽耦合（2608.20306）提供了处理传播修正的正向工具但也反向表明单向驱动近似下透射谱与电子结构关联的解释存在系统性风险（反射/透射谱差异、传播诱导啁啾可干扰带内/带间机制区分）；量子化驱动场扩展（2605.28236）目前为模型级趋势，禁戒级次出现的非经典参数依赖、具体哈密顿量实现与收敛性均待原文回溯确认；含 Berry 曲率反常速度项 E×Ω(k) 的半经典波包/SBE 反常 HHG 表征（2206.11935）为仅简报级证据，其波长/强度依赖定量复现与机制指认所依赖的能带与模型设置待回原文核对；2402.11449 峰位归属限于低次（二/三次）谐波且为简报级；2503.16329 中间强度区桥接定位与 2404.10293 OAM 光束双带弛豫近似分解均为简报级；ZnO 多能带逐导带通道分解（ad5d95）为简报级、逐带贡献指认依赖模型解释；退相对谐波谱作用非单调（相干相消抑制与退相再入），再入签名作为退相强度实验探针尚待实验验证，微观实空间退相干替换超短拟合 T2 的结论（2410.04512）目前为仅简报级证据待回原文核对；Wannier 规范数值实现中 CDO 在带简并/交叉处不适定、需以 SDO 类按能级差平滑的退相算符修正，且基于无场态的唯象退相算符不满足规范不变性；带内/带间电流分解依赖基选取、仅总电流为可观测量、机制指认依赖模型解释而非唯一实验观测，k 空间长度规范位置算符在周期边界下不适定且带数收敛与结构规范歧义显著，Weyl/磁性 WSM/节线/莫尔、倾斜-劈裂 Weyl 锥及 massive Dirac 表面态等扩展依赖两带/紧束缚极简模型与唯象退相、仅再现趋势；拓扑能带 HHG 通道定位（2401.01100）、TMD 层依赖通道分解与 SBE 同时再现 HHG 谱及非线性吸收角度/强度依赖（2303.10956）、GaAs 量子模拟单粒子层面对照、SBE 再现实验谐波相位结构（2022.01010 与 2309.00734 为同工作前后版）均为仅简报级证据待回原文核对；2511.13114 实为 rt-TDDFT、不构成 SBE 的数值验证；ZnO 取向分辨对照（2512.15370，回原文）与实验仅定性一致（实测四重 vs 模型三重）；共动参考系解析约化限于强场两带问题（2501.06885，简报级），激子基 SBE 覆盖微扰至饱和/非微扰区 SHG/THG 强度依赖的适用范围待原文确认；CEP 控制拓扑荷/OAM 开关（2607.23652）出自 1D 两带 SBE+唯象复偶极模型、属模型级趋势，需同时满足少周期驱动谱交叠与反演对称破缺两条件，长脉冲下无开关；涡旋强场 ZnO 阿秒涡旋描述及 T2 敏感性（2410.14385）为简报级待回溯；2603.05346 脉宽敏感 HHG 与 RhSi 局部手性谐波的主文计算为 TDDFT（定位片段明示）、简报的 SBE/Houston 归属未获原文支持，SBE 在脉宽维度效应上的模拟能力目前仍属未经证实的空白（待 Methods/SI 回溯）；忽略载流子-载流子相互作用的限定仅指标准平均场 SBE 实现——含库仑修正的多体密度矩阵/SBE 扩展（s41467-024-50534-3）已将其纳入并报告单层材料 HHG 的多体增强，但为仅简报级证据，库仑修正项的具体处理方式与多体增强结论均待回原文核对；贝叶斯反演扩展（2301.08636）以双带前向模型的代理模拟器定义参数—谐波谱映射，能带间隙/失相时间等反演结论受双带近似与代理（surrogate）精度制约，且以谐波谱反演 T2 亦继承仅凭产率无法区分传播效应与微观退相干的固有退化性，目前为仅简报级证据、反演设置与验证待回原文核对。

## 代表作

- paper:2018-1809.08109-reciprocal-space-trajectory-perspective-on-high-harmonic-gen
- paper:2025-2510.22064-semiconductor-wannier-equations-a-real-time-real-space-appro
- paper:2025-2504.01640-controlling-photoexcited-electron-spin-by-light-polarization
- paper:2023-2310.17007-unambiguous-discrimination-of-high-harmonic-generation-mecha
- paper:2024-s41567-024-02640-8-ultrafast-high-harmonic-spectroscopy-of-solids
- paper:2024-2405.17673-ultrafast-high-harmonic-spectroscopy-of-solids
- paper:2024-PhysRevB.110.035405-moiré-excitons-in-biased-twisted-bilayer-graphene-under-a
- paper:2026-2604.13901-contrasting-ultrafast-light-driven-electron-hole-interaction

## 证据日志

- 2026-10-24｜r93｜回原文｜[paper:2026-2609.20085-transient-high-harmonic-generation-from-solids-fro] 半导体Bloch方程（SBEs）：自洽分解带内电流与带间极化贡献，指认各谐波阶次的通道来源。
- 2026-10-24｜r93｜回原文｜[paper:2025-2512.01712-effects-of-zero-point-motion-in-the-high-harmonic-generation] 含退相干项的半导体布洛赫方程（SBE）模拟：对照表明唯象T2实际上只是零点涨落系综平均效应的有效参数化。
- 2026-10-24｜r94｜回原文｜[paper:2018-1809.08109-reciprocal-space-trajectory-perspective-on-high-harmonic-gen] 半导体布洛赫方程 (SBEs)：作为 RST 轨迹图像的量子基准，验证轨迹分解的正确性并显现多轨迹量子干涉效应。
- 2026-10-25｜r96｜回原文｜[paper:2025-2503.11432-coherent-suppression-and-dephasing-induced-reentrance-of-hig] 半导体布洛赫方程/密度矩阵动力学（长度规范，两能级有质量Dirac模型）：分别计算带内电流与带间极化的谐波贡献，直接证实二者相干相消并定位抑制的谐波阶次。
- 2026-10-25｜r98｜仅简报｜[paper:2021-2111.10986-high-harmonic-generation-in-monolayer-and-bilayer-of-transit] 强场半导体布洛赫方程（Houston 基）：强场下布居与相干演化的标准框架，是分解谐波微观通道的计算载体。
- 2026-10-30｜r100｜仅简报｜[paper:2023-2303.10956-linking-high-harmonic-generation-and-strong-field-ionization] 半导体布洛赫方程（SBE）模拟：含带内电流、带间极化与唯象失相的 SBE 同时再现谐波谱与非线性吸收的角度/强度依赖。
- 2026-10-30｜r100｜回原文｜[paper:2025-2508.07869-semiconductor-bloch-equations-in-wannier-gauge-with-well-beh] 半导体布洛赫方程（SBE）密度矩阵动力学：提供含退相干的强场载流子动力学核心框架，本文将其在 Wannier 规范下整体重写
- 2026-10-30｜r101｜仅简报｜[paper:2026-2606.04295-quantum-simulations-of-ultrafast-optical-spectroscopy-of-sem] 半导体布洛赫方程（SBE）经典模拟：作为基准，GaAs 单粒子 SBE 结果与量子模拟定量一致，验证了映射的正确性。
- 2026-10-31｜r104｜回原文｜[paper:2025-2511.13114-orthogonal-attosecond-control-of-solid-state-harmonics-by-op] 半导体布洛赫方程（SBE）模拟：将谐波分解为带内电流与带间极化两部分分别计算，是通道分离论证的核心工具。
- 2026-10-31｜r104｜仅简报｜[paper:2022-2022.01010-observation-of-light-driven-band-structure-via-multi-band-hi] 半导体布洛赫方程（SBEs）模拟：在强场固态HHG建模中再现实验谐波相位结构，连接微观带动力学与宏观发射。
- 2026-10-31｜r104｜仅简报｜[paper:2023-2309.00734-observation-of-light-driven-band-structure-via-multiband-hig] 多带半导体布洛赫方程（SBE）模拟：把谐波谱与多带布居、带间耦合矩阵元和瞬态带结构定量关联，是解读实验的物理基准。
- 2026-10-31｜r106｜回原文｜[paper:2025-2512.15370-orientation-dependent-high-harmonic-generation-in-zno] 多带TDSE/半导体布洛赫方程（SBE）模拟：同时求解带内电流与带间极化的相干动力学，并将谐波分解为两通道贡献以定位各向异性来源。
- 2026-10-31｜r109｜仅简报｜[paper:2024-2401.01100-topological-high-harmonic-spectroscopy] 半导体布洛赫方程（SBE）/Houston 基矢强场动力学：在拓扑能带上自洽求解激光驱动演化，并分离带内/带间电流以定位拓扑信号的来源通道。
- 2026-10-31｜r109｜仅简报｜[paper:2024-2410.04512-real-space-perspective-on-dephasing-in-solid-state-high-harm] 半导体布洛赫方程（SBE）+ 唯象 T2 对比：证明微观实空间退相干可替换拟合实验所需的超短 T2 参数，统一了此前唯象处理与第一性动力学的矛盾。
- 2026-11-01｜r111｜仅简报｜[paper:2025-2501.06885-the-impact-of-intraband-carrier-dynamics-on-the-optical-prop] 共动（加速）参考系中的半导体布洛赫方程：把带内加速严格变换为含时失谐与含时相位，将强场两带问题化为解析可控的驱动二能级形式。
- 2026-11-01｜r111｜仅简报｜[paper:2025-2511.05112-unexpected-increase-of-intensity-dependent-excitonic-second] 激子基半导体Bloch方程（SBE）：在激子表象求解密度矩阵动力学，统一覆盖从微扰区到饱和/非微扰区的SHG与THG强度依赖响应。
- 2026-11-06｜r114｜回原文｜[paper:2026-2607.23652-carrier-envelope-phase-control-of-orbital-angular-] 固态 HHG 微观模型（带内电流 + 带间极化 / 半导体布洛赫方程图像）：为亚周期发射时序如何映射为方位相位并改写 OAM 谱提供解释框架（依据固态 HHG 领域通行方法推断）。
- 2026-11-06｜r115｜仅简报｜[paper:2024-2410.14385-attosecond-vortices-in-semiconductor-materials] 半导体Bloch方程（SBE，含唯象退相干时间）：给出ZnO在涡旋强场下带内/带间电流的微观响应，并量化退相干时间T2对平台谐波产率与相位的影响。
- 2026-11-07｜r117｜仅简报｜[paper:2024-2402.11449-nonlinear-harmonic-spectra-in-bilayer-van-der-waals-antiferr] 含时波包/半导体布洛赫方程动力学模拟：通过数百次波长扫描的动力学模拟逐一定位对二次、三次谐波有贡献的偶极允许跃迁，是全文峰位归属的数据基础。
- 2026-11-07｜r117｜回原文｜[paper:2026-2605.28236-symmetry-breaking-by-quantum-light-in-solid-state-high-harmo] 量子化驱动场 + 半导体布洛赫方程非微扰数值模拟：将驱动光作为量子化场而非经典场代入固体 HHG 模拟，直接给出禁戒级次出现及其与非经典参数依赖的谱学证据。
- 2026-11-07｜r117｜仅简报｜[paper:2025-2503.16329-real-time-simulations-of-laser-induced-electron-excitations] 半导体布洛赫方程（SBE）：在预设能带结构下描述带间极化与布居动力学，用于桥接解析模型与 TDDFT 的中间强度区。
- 2026-11-07｜r117｜仅简报｜[paper:2024-2404.10293-orbital-angular-momentum-beam-assisted-high-order-harmonic-g] 半导体布洛赫方程（SBE）模拟：在双带加弛豫近似下把 HHG 谱分解为带内电流与带间极化的微观贡献，给出谐波强度的可计算来源。
- 2026-11-07｜r117｜回原文｜[paper:2026-2608.20306-computational-methods-of-wave-propagation-for-semi] Maxwell-半导体布洛赫方程自洽耦合求解：核心方法贡献——首次将体材料 HHG 的辐射源项与驱动场演化双向耦合，替代单向驱动近似。
- 2026-11-07｜r117｜回原文｜[paper:2026-2608.20306-computational-methods-of-wave-propagation-for-semi] 半经典 SBE 动量网格积分：作为偶极源项发生器，支撑含时极化的非线性辐射计算。
- 2026-11-07｜r118｜仅简报｜[paper:2024-doi-10-1088-1674-1056-ad5d95-high-order-harmonic-generation-in-zno-crystals-driven-by-one] 多能带半导体布洛赫方程（SBE）数值求解：在多能带框架下自洽演化密度矩阵，逐带分解各导带对谐波产率与平台的贡献，是本文的核心计算手段。
- 2026-11-07｜r118｜仅简报｜[paper:2025-2508.00273-spatially-inhomogeneous-field-induced-harmonic-radiation-in] 半导体Bloch方程（SBE）：作为均匀场极限的基准框架，用于对比验证非均匀系数方程给出的偶次谐波与增强效应。
- 2026-11-08｜r123｜回原文｜[paper:2026-2603.05346-pulse-duration-sensitive-high-harmonics-and-attosecond-local] 半导体布洛赫方程 / Houston 基组含时模拟：复现脉宽依赖的谐波谱与偏振，分离带内电流与带间极化对局部手性光的各自贡献。
- 2026-11-08｜r124｜仅简报｜[paper:2022-2206.11935-characterizing-anomalous-high-harmonic-generation-in-solids] 含 Berry 曲率的半经典波包/半导体布洛赫方程模拟：在波包动力学中引入反常速度项 E×Ω(k)，定量复现波长与强度依赖特征并指认谐波机制。
- 2026-11-14｜r132｜仅简报｜[paper:2024-doi-10-1038-s41467-024-50534-3-many-body-enhancement-of-high-harmonic-generation-in-monolay] 密度矩阵/半导体布洛赫方程演化（含库仑修正）：提供强场下载流子相干动力学框架，用以追踪极化、布居与退相干随场的演化。
- 2026-11-15｜r139｜仅简报｜[paper:2023-2301.08636-bayeshhg-bayesian-inference-for-high-harmonic-generation-spe] 半导体布洛赫方程（双带前向模型）：作为被代理的物理模拟器，定义参数—谐波谱映射，能带间隙、失相时间等是反演目标（以 ZnO 体系为演示）。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[1409.2725]]
- [[1809.08109]]
- [[2021-2112_01745-high-harmonic-spectroscopy-of-light-driven-nonlinear-anisotr]]
- [[2023-2310_17007-unambiguous-discrimination-of-high-harmonic-generation-mecha]]
- [[2024-s41567-024-02640-8-ultrafast-high-harmonic-spectroscopy-of-solids]]
- [[2025-2510_12443-self-attention-enabled-quantum-path-analysis-of-high-harmoni]]
- [[2025-2512_01712-effects-of-zero-point-motion-in-the-high-harmonic-generation]]
- [[2026-2609.20085-transient-high-harmonic-generation-from-solids-fro]]
- [[2026-2609_20085-transient-high-harmonic-generation-from-solids-from-spectros]]
- [[2109.04508]]
- [[2111.10986]]
- [[2112.01745]]
- [[2206.11935]]
- [[2310.17007]]
- [[2401.12929]]
- [[2405.17673]]
- [[2408.09364]]
- [[2410.11542]]
- [[2410.17077]]
- [[2501.06885]]
- [[2503.11432]]
- [[2504.01640]]
- [[2508.07869]]
- [[2508.16494]]
- [[2510.12443]]
- [[2510.15207]]
- [[2510.22064]]
- [[2511.05112]]
- [[2511.13114]]
- [[2512.01712]]
- [[2512.15370]]
- [[2602.22463]]
- [[2603.05346]]
- [[2604.13901]]
- [[2605.28236]]
- [[2607.23652]]
- [[2608.20306]]
- [[2609.20085]]
- [[2610.15251]]
- [[5-11]]
- [[Berry 曲率]]
- [[Nodal-Line Semimetals 的非线性光学谱学：NbSi_xTe_2 二维节线半金属的 HHG 理论]]
- [[PLAN]]
- [[TDDFT]]
- [[TDSE]]
- [[Unveiling the Role of Electron-Phonon Scattering in Dephasing High-Order Harmonics in Solids]]
- [[bayesian-inference]]
- [[strong-field-ionization]]
- [[半导体Bloch方程]]
- [[单色激光场调控固体电子动力学以优化阿秒脉冲产生]]
- [[反常速度]]
- [[固体HHG]]
- [[固体超快高次谐波光谱学]]
- [[固体高次谐波]]
- [[固体高次谐波产生]]
- [[带内/带间电流分解]]
- [[带内载流子动力学对二维材料光学性质的影响：I. 一般理论]]
- [[强驱动固体中电子—空穴相干性的探测]]
- [[扭曲双层石墨烯中高次谐波产生的激光椭圆率依赖]]
- [[拓扑表面态]]
- [[波形控制]]
- [[莫尔超晶格]]
- [[谷分辨高次谐波：探测 Dirac 锥之外的对称性破缺]]
- [[谷极化]]
- [[贝叶斯反演]]
- [[阿秒瞬态吸收]]
- [[非线性光学]]
- [[高次谐波产生]]
- [[高次谐波光谱学]]
<!-- /linsai-wikilinks -->
