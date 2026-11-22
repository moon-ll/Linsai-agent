---
title: "arpes"
type: "methods"
created: "2026-09-11T16:41:26Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "type/method"]
related: ["1T-TaS2 一级 CDW 相变中相干性的热滞坍缩", "1T-TaSe2 中 CDW 金属-绝缘畴的电子结构本质——triclinic 堆叠的关键角色", "2024-2411_18761-relativistic-and-nonrelativistic-spin-splitting-above-and-be", "2025-2510_03759-the-magnon-spectra-of-g-type-altermagnet-bulk-crsb", "2025-2512_24553-from-berry-curvature-to-quantum-metric-a-new-era-of-quantum", "2025-s41467-025-60020-z-kramers-nodal-lines-in-intercalated-tas2-superconductors", "2026-2503_04431-observation-of-non-adiabatic-landau-zener-tunnelin", "2026-2607.19242-time-resolved-arpes-in-pumped-excitonic-systems-floquet-phys", "2026-2610.10140-progress-and-prospect-of-ai-in-arpes-workflow", "2026-2610.17984-direct-view-of-exciton-and-carrier-dynamics-in-twisted-bilay", "2302.00604", "2405.12679", "2408.08997", "2411.18205", "2411.18761", "2503.04431", "2503.16670", "2506.03251", "2506.03261", "2507.14890", "2508.12985", "2510.03759", "2511.01388", "2512.10405", "2512.24553", "2603.16635", "2603.28725", "2609.07923", "2609.28293", "ARPES 与 DFT 研究 Co₁/₄TaSe₂：层状交错磁体与自旋劈裂基准", "CoNb4Se8 层状交变磁性化合物的电子结构（ARPES+DFT）", "CrSb", "Dynamic moiré-like band modulation in Dirac materials via multi-beam optical interference", "Floquet能带工程", "Floquet边带", "Observation of Floquet-induced gap in graphene", "PLAN", "Spin-dependent spectral weight in correlated Mott altermagnets", "Ultra-low-power electric-field control of altermagnetism in MnTe heterostructures（MnTe 异质结中的超低功耗电场调控交错磁性）", "Weyl半金属", "交变磁体", "强光激发 1T-TiSe₂ 中光诱导半金属态的超快形成", "拓扑表面态", "时间分辨ARPES", "时间反演对称性破缺", "相干声子", "自旋分辨ARPES", "自旋劈裂", "量子几何", "量子几何张量", "黑磷中赝自旋选择的Floquet能带工程"]
source_raw: ""
growth_stage: "mature"
confidence: 0.9
updated_at: "2026-11-15T03:45:39Z"
settled_count: 40
aliases: ["ARPES", "angle-resolved photoemission spectroscopy", "角分辨光电子能谱"]
---

<!-- methods-settle:v1 -->

## 原理

ARPES通过同时测量光发射电子的动能与出射角反推能量–动量色散并三维测绘占据态能带：费米面成像可直接观测节线环与费米面拓扑、为Berry相位解释提供独立于输运的谱学判据；可把电荷序能隙作为谱学读出的有序参量，动量分辨观测CDW/Mott能隙随温度坍塌与重现、一级相变滞回、金属畴与绝缘畴各自色散及能隙、跨NC-IC相界背折叠带强度/线宽与能带重构，并观测CDW能带重构与谱重随升降温历史的差异、把一级相变滞回确证到电子结构层面，还可给出表面敏感的能带结构与上下Hubbard带谱学证据、与STS层分辨结果交叉验证；静态ARPES可动量分辨观测费米面处CDW能隙及其方向依赖（Γ-Y最大/Γ-X最小），高分辨变温ARPES可逐温追踪体带隙在CDW转变前后的演化、以带隙–CDW序参量对应关系判别激子vs晶格起源，并以温度演化区分CDW能带重整化与激子形成所致谱函数改变、成为识别自发激子态（含奇偶层切换）的核心手段，ARPES–DFT逐段对照本身也成为甄别激子机制证据效力、暴露模型输入依赖的分析工具；飞秒tr-ARPES可以泵浦后各能带占据的飞秒弛豫指纹直接区分电荷转移隙与Mott隙，以亚百飞秒时间与动量分辨直接成像CDW能隙闭合、化学势移动及Γ-M能带瞬态交叠形成光致半金属态的全过程，高分辨trARPES以meV级分辨分辨CDW背散间隙瞬时闭合与折叠带解折叠，可测量CDW能隙光致熔化与恢复并把电子序与结构序参量动力学对齐比较，tr-ARPES/动量显微镜以能量–动量–时间三重分辨追踪载流子转移、谷间散射、瞬态能带、Floquet边带/复制带/杂化能隙及Floquet-moiré型瞬态能带并以亚周期时间戳分辨Floquet-Bloch带建立与失相，可借trion谱学判据分辨激子与trion双组分、在ReSe2中同时分辨激子谱特征与带边载流子布居并独立时间追踪以隔离激子解离通道，其第一性原理模拟（lesser格林函数/含时谱函数）可把相干声子光生与载流子–晶格动力学映射为可测谱学指纹，并在下一代超快光源支撑下动量分辨追踪瞬态能带占据与序参量演化、成为识别隐藏相的谱学手段，还可逐延迟追踪van Hove奇点能量位置振荡、以vHS调制直接给出电声耦合与瞬态能带调制的证据；自旋分辨ARPES给出交变磁非相对论自旋劈裂直接证据（CrSb量级约1 eV、近费米面0.93 eV及g波自旋织构，α-MnTe节点面d波型自旋极化，六角易面交变磁体0.2–0.4 eV劈裂能标），可逐分量重构Γ附近刺猬状自旋纹理，在CoNb4Se8中量化g波劈裂并区分NRSS与RSS，在近补偿铁磁体中量化恢复反演中心前后自旋劈裂坍缩约两个数量级，时间分辨自旋分辨ARPES与光电流探测联用还可经螺旋度依赖的自旋分辨光电流非对称性读出瞬态d波自旋织构、构成光致偶宇称单向极化自旋织构的实验验证方案；软X射线ARPES以体灵敏三维动量探测追踪d波劈裂符号在整个布里渊区的交替变化并分辨插层TaS2超导体Kramers节点线附近Ising型自旋极化；圆二色ARPES以左右旋谱强度不对称给出时间反演破缺与轨道手性指纹并逐带逐动量测绘布洛赫态手征、轨道角动量与准QGT；原位ARPES在MnTe/InP(111)薄膜给出370 meV交错磁d波自旋劈裂光谱证据；μ-ARPES/微聚焦ARPES以微米级光斑空间分辨解理面终止区域、在扭转角不均匀样品上锁定单一约9°扭转畴、在单一样品上选择性测量不同晶面区分体带与表面态；四维ARPES可作为能带重建和ARPESNet压缩的高维输入，ML驱动后处理与自能提取Σ(k,ω)反演的精度与失效模式已获系统综述；Co1/4TaSe2的ARPES直接分辨交错磁自旋劈裂峰并提供独立于计算的实验基准、跨T_N标定无序相中劈裂信号可分辨程度，原位电调T_N使同一样品可在磁有序与无序两侧扫描自旋劈裂；ARPES能带折叠/重构指纹与计算能带对照可指认准简并CDW态体系中不同温度下实际实现的CDW相，表面敏感ARPES类探针可分辨表面–体金属/绝缘对比并确认光切换后表面电子态的非易失持久改变而非瞬态响应，ARPES与霍尔/电阻输运联用可由能带填充与载流子浓度反演生长诱导的自掺杂效应、把生长参数与费米面位置及电子–声子耦合变化定量连接。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| MnTe/InP(111)薄膜d带自旋劈裂（原位ARPES，T_N以下） | 370 meV | paper:2024-2308.11180-broken-kramers-degeneracy-in-altermagnetic-mnte |
| CrSb近费米面非相对论自旋劈裂 | 0.93 eV（量级约1 eV） | paper:2024-2405.12679-observation-of-spin-splitting-in-room-temperature-metallic-a |
| 近补偿铁磁体恢复反演中心前后自旋劈裂坍缩幅度 | 约两个数量级 | paper:2026-2609.12931-spin-splitting-without-symmetry-a-nearly-compensated-ferrima |
| 微聚焦ARPES在扭转角不均匀样品上锁定的单一扭转畴角度 | 约9° | paper:2026-2610.17984-direct-view-of-exciton-and-carrier-dynamics-in-twisted-bilay |
| 库仑工程体系跨CDW转变的准粒子带隙重整化幅度（微区/nano-ARPES变温提取） | >60 meV | paper:2025-2506.01470-persistence-of-charge-ordering-instability-to-coulomb-engine |

## 适用边界

静态ARPES仍是表面敏感、仅探测占据态的准平衡积分手段，费米面与Berry相位判据属拓扑间接推定，自旋分辨模式受计数效率、样品均匀性、化学计量与矩阵元伪影限制，半导体低温测量需导电衬底，软X射线模式不能同时保持自旋分辨（体/表面贡献拆分仍需晶面或能量依赖交叉判据），μ-ARPES与微聚焦/位置分辨ARPES虽可剥离终止差异、锁定单一约9°扭转畴并选择性测量不同晶面，但层分辨超快动力学数据可靠性以先锁定单一畴为前提且不能消除表面敏感性与畴平均问题；CDW能隙与滞回的电子结构读出受空间/能量分辨和热历史影响、须逐温稳定扫描并以升降温历史可分辨的逐温序列（而非单点快照）为前提，跨CDW转变体带隙演化与带隙–序参量对应关系以高分辨变温序列的温度稳定性与能量分辨为前提，变温区分CDW能带重整化与激子形成亦以两类谱函数变化可分离为前提且激子态指认属温度演化对比的机制判别而非对激子凝聚的独立直接成像，ARPES–DFT对照的甄别力受计算模型输入依赖限制、失配本身不能直接证伪某一微观机制，CrSb等解理面表面态指认不能替代体拓扑不变量测量；tr-ARPES受泵浦扰动及时间/能量分辨折衷约束、强场下Floquet缀饰图像在dressed带间主导中央峰后失效，区分电荷转移隙与Mott隙、Floquet成带/失相亚周期时间戳、激子解离通道隔离、隐藏相与光致亚稳金属态指认均属泵浦诱导的非平衡瞬态判别而非平衡基态直接成像，光致CDW能隙闭合与Γ-M瞬态交叠所成像的半金属态为光致瞬态，电子序与结构序参量动力学对齐以CDW能隙作可靠电子序读出且两序参量可在同一样品对齐测得为前提，相干声子等载流子–晶格耦合谱指纹目前以lesser格林函数第一性原理模拟的正向映射为据而非独立直接反演，trion与激子双组分分辨以理论谱形判据为据；QGT提取依赖布洛赫波函数导数、矩阵元与相位且准QGT严格比例关系主要限于两带或近孤立能带，SARPES探测诱导极化须以一步光发射计算分离、刺猬纹理的磁致/Rashba判定须三自旋分量完整重构、近补偿铁磁体结论属对比性证据，时间分辨自旋分辨ARPES–光电流方案对瞬态d波自旋织构的读出目前为文献提出的实验验证方案而非已实现的实验测量，其解读依赖螺旋度依赖非对称性与自旋织构的对应模型且叠加泵浦扰动与自旋分辨计数效率双重限制，交变磁劈裂解读受关联强度对可提取值的理论上限约束、RuO2类候选未经检验的劈裂值不能直接视为本征基态劈裂，MnTe的370 meV读出依赖薄膜外延质量与T_N以下有序相成立、迁移须重新标定，Co1/4TaSe2在T_N以上残余信号须依实测可分辨程度判别，原位电调T_N的相界比较以该次实验标定的T_N与信号可分辨性为界，ML重建/压缩依赖低秩先验、自能提取可分辨ΔΣ(ω)尺度与失效模式随方法而异且后处理不能替代物理模型校验，ARPES对照只能排除静态占据态电子结构变化而不能直接测量磁振子阻尼等动态互作，tr-ARPES逐延迟追踪vHS能量位置振荡属泵浦扰动下的非平衡瞬态探测、以vHS谱特征在所用时间/能量分辨下可逐延迟追踪为前提，微区/nano-ARPES跨CDW转变的带隙重整化（>60 meV）与转变行为读出依赖微区空间分辨与样品区域均匀性，转变行为对屏蔽不敏感属特定库仑工程体系的对比性证据、数值与结论迁移到其他体系须重新标定；准简并CDW态中的相指认依赖能带折叠/重构指纹与计算能带对照、受模型输入依赖限制且不能替代对各竞争相自由能差的独立测量，表面–体金属/绝缘对比与非易失表面金属态切换的读出属表面敏感探测、向体相行为外推需交叉验证且持久改变的判定以排除瞬态响应的对照测量为前提，自掺杂反演以能带填充与载流子浓度的联合定量标定为前提且生长参数–费米面位置–电声耦合变化的定量连接属相关性关联而非因果判定；上下Hubbard带的ARPES谱学读出属表面敏感证据、向体相基态的指认以与STS层分辨等独立手段交叉验证为前提。

## 代表作

- papers:2025-2510.03759-the-magnon-spectra-of-g-type-altermagnet-bulk-crsb
- paper:2026-2609.12931-spin-splitting-without-symmetry-a-nearly-compensated-ferrima
- paper:2026-2610.19370-odd-to-even-layer-switch-of-spontaneous-excitonic-state-in-t
- paper:2026-2601.03358-light-induced-even-parity-unidirectionally-polarized-spin-sp
- paper:2025-s41467-025-60020-z-kramers-nodal-lines-in-intercalated-tas2-superconductors
- paper:2024-2405.12679-observation-of-spin-splitting-in-room-temperature-metallic-a
- paper:2024-2308.11180-broken-kramers-degeneracy-in-altermagnetic-mnte
- paper:2024-2402.01613-altermagnetic-lifting-of-kramers-spin-degeneracy

## 证据日志

- 2026-10-24｜r94｜仅简报｜[paper:2025-2502.06416-hedgehog-like-spin-texture-and-time-reversal-symmetry-breaki] 圆二色 ARPES（CD-ARPES）：左右旋激发的谱强度不对称性给出时间反演对称性破缺与轨道手性的谱学指纹，与自旋纹理交叉验证。
- 2026-10-24｜r94｜仅简报｜[paper:2025-2511.11448-trion-signatures-in-arpes-of-2d-semiconductors] 时间分辨 ARPES / 动量显微镜：本文为该技术首次提供 trion 谱学特征的理论判据，使 tr-ARPES 可分辨激子与 trion 双组分。
- 2026-10-25｜r96｜仅简报｜[paper:2024-2308.11180-broken-kramers-degeneracy-in-altermagnetic-mnte] 原位角分辨光电子能谱（in-situ ARPES）：直接分辨d带色散在TN以下分裂，给出370 meV自旋劈裂的直接光谱证据。
- 2026-10-30｜r102｜仅简报｜[paper:2026-2610.10140-progress-and-prospect-of-ai-in-arpes-workflow] ARPES 自能提取（Σ(k,ω) 反演）：综述各类 ML 与传统方法在自能提取上的精度与失效模式，界定可分辨的 ΔΣ(ω) 尺度。
- 2026-10-30｜r102｜仅简报｜[paper:2026-2610.10140-progress-and-prospect-of-ai-in-arpes-workflow] ML 驱动的 ARPES 数据后处理：去噪、谱函数重构与自动化谱分析，替代人工逐谱拟合。
- 2026-10-30｜r102｜仅简报｜[paper:2026-2610.17984-direct-view-of-exciton-and-carrier-dynamics-in-twisted-bilay] 微聚焦/位置分辨 ARPES：在扭转角不均匀的样品上锁定单一 ~9° 扭转畴，保证层分辨超快动力学数据的可靠性。
- 2026-11-01｜r112｜仅简报｜[paper:2024-2501.03798-build-up-and-dephasing-of-floquet-bloch-bands-on-subcycle-ti] 亚周期时间分辨 ARPES / 超快动量显微：在驱动周期内为 Floquet 边带的强度与色散打时间戳，是分辨成带与失相动力学的核心技术。
- 2026-11-01｜r113｜仅简报｜[paper:2025-2501.10649-spin-degenerate-bulk-bands-and-topological-surface-states-as] 微聚焦ARPES（micro-focused ARPES）：以微米级光斑在单一样品上选择性测量不同晶面，直接区分体带与表面态贡献、回避大光斑混叠。
- 2026-11-01｜r113｜仅简报｜[paper:2024-2402.01613-altermagnetic-lifting-of-kramers-spin-degeneracy] 软X射线ARPES（SX-ARPES）：提供体灵敏的三维动量探测，追踪d波型自旋劈裂随极角/方位角在整个布里渊区的交替符号变化。
- 2026-11-06｜r116｜仅简报｜[paper:2026-2604.11906-isolating-exciton-dissociation-pathways-in-rese2] 时间-角度分辨光电子谱（TR-ARPES）：同时分辨激子的动量空间谱特征与带边载流子布居，实现两类布居的独立时间追踪。
- 2026-11-07｜r119｜仅简报｜[paper:2026-2607.12783-photogeneration-and-signatures-of-coherent-phonons-in-time-r] tr-ARPES第一性原理模拟（lesser格林函数/含时谱函数）：从G^<(k,t,t')构造泵浦-探测光电子谱，把微观载流子-晶格动力学映射为可测谱学指纹。
- 2026-11-08｜r127｜仅简报｜[paper:2024-2408.08997-ultrafast-creation-of-a-light-induced-semimetallic-state-in] 时间分辨角分辨光电子能谱（tr-ARPES）：以亚百飞秒时间与动量分辨直接成像CDW能隙闭合、化学势移动及Γ-M能带瞬态交叠的全过程。
- 2026-11-08｜r127｜仅简报｜[paper:2025-2509.16493-dynamics-of-a-jointly-commensurate-moiré-charge-density-wave] 时间分辨ARPES (tr-ARPES)：直接测量CDW能隙的光致熔化与恢复，将电子序幅度动力学与结构序参量动力学对齐比较。
- 2026-11-13｜r128｜仅简报｜[paper:2026-2611.15997-what-can-next-generation-ultrafast-light-sources-t] 时间分辨角分辨光电子能谱（tr-ARPES）：动量分辨追踪瞬态能带占据与序参量演化，是识别隐藏相的谱学手段。
- 2026-11-13｜r128｜仅简报｜[paper:2021-2106.09774-unconventional-hysteretic-transition-in-a-charge-density-wav] 角分辨光电子能谱（ARPES）：直接观测 CDW 能带重构与谱重随升降温历史的差异，证明滞回发生在电子结构层面
- 2026-11-13｜r129｜仅简报｜[paper:2023-2306.00311-ultrafast-switching-from-the-charge-density-wave-phase-to-a] 高分辨时间分辨角分辨光电子能谱（trARPES）：以 meV 级能量分辨直接分辨 CDW 背散间隙的瞬时闭合与折叠能带的解折叠，提供了光致亚稳金属态的直接电子结构证据。
- 2026-11-13｜r129｜仅简报｜[paper:2025-2508.06464-observation-of-momentum-dependent-charge-density-wave-gap-in] 角分辨光电子能谱（ARPES）：直接动量分辨地观测费米面处 CDW 能隙及其 Γ-Y 最大/Γ-X 最小的方向依赖，是本文核心证据。
- 2026-11-13｜r130｜仅简报｜[paper:2023-2303.06188-exploring-the-charge-density-wave-phase-of-1t-tase2-mott-or] 飞秒时间分辨角分辨光电子能谱（tr-ARPES）：通过泵浦后各能带占据的飞秒弛豫动力学直接区分电荷转移与 Mott 隙——两种机制给出可区分的瞬态占据演化指纹。
- 2026-11-13｜r130｜仅简报｜[paper:2024-2408.05958-inconsistencies-between-experimental-and-theoretical-band-st] 角分辨光电子能谱（ARPES）：直接实验测得 TiSe2 全动量分辨能带，提供了检验理论预言的基准数据。
- 2026-11-13｜r130｜仅简报｜[paper:2024-2408.05958-inconsistencies-between-experimental-and-theoretical-band-st] ARPES-DFT 直接对照分析：将实测谱与计算带逐段比对的方法本身成为甄别激子机制证据效力的工具，暴露了模型输入依赖问题。
- 2026-11-13｜r130｜仅简报｜[paper:2026-2608.05059-direct-evidence-for-robust-bulk-band-gap-across-the-charge-d] 高分辨角分辨光电子能谱（ARPES）：以动量分辨方式直接观测体带隙在 CDW 转变前后的演化，是给出『激子 vs 晶格』判据的核心手段
- 2026-11-13｜r130｜仅简报｜[paper:2026-2608.05059-direct-evidence-for-robust-bulk-band-gap-across-the-charge-d] 变温 ARPES 带隙追踪：通过温度序列测量建立带隙大小与 CDW 序参量的对应关系，从而判断带隙的微观起源
- 2026-11-14｜r132｜仅简报｜[paper:2026-2610.19370-odd-to-even-layer-switch-of-spontaneous-excitonic-state-in-t] 变温角分辨光电子能谱（变温 ARPES）：通过温度演化区分 CDW 能带重整化与激子形成导致的谱函数改变，是识别自发激子态的核心手段。
- 2026-11-14｜r133｜仅简报｜[paper:2024-2407.17015-unveiling-van-hove-singularity-modulation-and-fluctuated-cha] 时间分辨ARPES (tr-ARPES)：在动量-能量空间逐延迟追踪vHS能量位置振荡，直接给出电声耦合与瞬态能带调制的实空间-动量分辨证据。
- 2026-11-14｜r133｜仅简报｜[paper:2025-2506.01470-persistence-of-charge-ordering-instability-to-coulomb-engine] 变温角分辨光电子能谱（微区/nano-ARPES）：跨CDW转变温度追踪准粒子能带演化，同时提取带隙重整化幅度（>60 meV）与转变行为，发现后者对屏蔽不敏感。
- 2026-11-14｜r134｜仅简报｜[paper:2025-2509.06414-quasidegenerate-charge-density-wave-states-in-1t-tise2] ARPES（角分辨光电子能谱）：以能带折叠/重构指纹与计算能带对照，指认不同温度下实验中实际实现的CDW相。
- 2026-11-14｜r134｜仅简报｜[paper:2025-2512.21628-nonvolatile-optical-switching-of-surface-metallicity-in-1t-t] 表面敏感电子表征（STM/STS/ARPES类表面探针）：用于分辨表面-体金属/绝缘对比，并确认切换后表面电子态的持久改变而非瞬态响应。
- 2026-11-14｜r134｜仅简报｜[paper:2026-2604.19110-controlling-quantum-materials-by-growth-thermodynamics-kinet] ARPES与霍尔/电阻输运表征：由能带填充与载流子浓度反演生长诱导的自掺杂效应，把生长参数与费米面位置、电子-声子耦合变化定量连接。
- 2026-11-14｜r135｜仅简报｜[paper:2025-2509.17419-topical-review-the-nature-of-the-ground-state-and-possibilit] ARPES角分辨光电子能谱：提供表面敏感的能带结构与上下Hubbard带谱学证据，与STS层分辨结果交叉验证。
- 2026-11-15｜r137｜仅简报｜[paper:2026-2601.03358-light-induced-even-parity-unidirectionally-polarized-spin-sp] 时间分辨自旋分辨 ARPES 与光电流探测：通过螺旋度依赖的自旋分辨光电流非对称性读出瞬态 d 波自旋织构，作为本文提出的实验验证方案。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[1T-TaS2 一级 CDW 相变中相干性的热滞坍缩]]
- [[1T-TaSe2 中 CDW 金属-绝缘畴的电子结构本质——triclinic 堆叠的关键角色]]
- [[2024-2411_18761-relativistic-and-nonrelativistic-spin-splitting-above-and-be]]
- [[2025-2510_03759-the-magnon-spectra-of-g-type-altermagnet-bulk-crsb]]
- [[2025-2512_24553-from-berry-curvature-to-quantum-metric-a-new-era-of-quantum]]
- [[2025-s41467-025-60020-z-kramers-nodal-lines-in-intercalated-tas2-superconductors]]
- [[2026-2503_04431-observation-of-non-adiabatic-landau-zener-tunnelin]]
- [[2026-2607.19242-time-resolved-arpes-in-pumped-excitonic-systems-floquet-phys]]
- [[2026-2610.10140-progress-and-prospect-of-ai-in-arpes-workflow]]
- [[2026-2610.17984-direct-view-of-exciton-and-carrier-dynamics-in-twisted-bilay]]
- [[2302.00604]]
- [[2405.12679]]
- [[2408.08997]]
- [[2411.18205]]
- [[2411.18761]]
- [[2503.04431]]
- [[2503.16670]]
- [[2506.03251]]
- [[2506.03261]]
- [[2507.14890]]
- [[2508.12985]]
- [[2510.03759]]
- [[2511.01388]]
- [[2512.10405]]
- [[2512.24553]]
- [[2603.16635]]
- [[2603.28725]]
- [[2609.07923]]
- [[2609.28293]]
- [[ARPES 与 DFT 研究 Co₁/₄TaSe₂：层状交错磁体与自旋劈裂基准]]
- [[CoNb4Se8 层状交变磁性化合物的电子结构（ARPES+DFT）]]
- [[CrSb]]
- [[Dynamic moiré-like band modulation in Dirac materials via multi-beam optical interference]]
- [[Floquet能带工程]]
- [[Floquet边带]]
- [[Observation of Floquet-induced gap in graphene]]
- [[PLAN]]
- [[Spin-dependent spectral weight in correlated Mott altermagnets]]
- [[Ultra-low-power electric-field control of altermagnetism in MnTe heterostructures（MnTe 异质结中的超低功耗电场调控交错磁性）]]
- [[Weyl半金属]]
- [[交变磁体]]
- [[强光激发 1T-TiSe₂ 中光诱导半金属态的超快形成]]
- [[拓扑表面态]]
- [[时间分辨ARPES]]
- [[时间反演对称性破缺]]
- [[相干声子]]
- [[自旋分辨ARPES]]
- [[自旋劈裂]]
- [[量子几何]]
- [[量子几何张量]]
- [[黑磷中赝自旋选择的Floquet能带工程]]
<!-- /linsai-wikilinks -->
