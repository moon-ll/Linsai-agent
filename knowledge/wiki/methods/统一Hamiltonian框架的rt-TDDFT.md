---
title: "统一Hamiltonian框架的rt-TDDFT"
type: "methods"
created: "2026-08-22T06:00:35Z"
updated: "2026-11-15T15:09:19Z"
tags: []
related: ["1711.05783", "1809.06264", "1906.10224", "2024）", "2025-2502.01258-magnetizing-altermagnets-by-ultrafast-asymmetric-spin-dynami", "2025-2508_12563-enhancing-cutoff-energy-of-solid-high-harmonic-generation-fr", "2025-2512_01712-effects-of-zero-point-motion-in-the-high-harmonic-generation", "2026-2604_25483-probing-sliding-ferroelectricity-in-bilayer-t-_-ma", "2109.07693", "2304.09459", "2307.14090", "2401.09884", "2401.12929", "2407.16350", "2407.17917", "2505.09387", "2505.19894", "2508.12563", "2510.15207", "2512.01712", "2603.05346", "2603.19875", "2604.25483", "2607.17265", "2610.19967", "66", "Berry曲率", "CrSb", "First-principles electron-phonon scattering in real-time TDDFT", "Floss et al. 2021: Si与金刚石在近/中红外驱动下的高次谐波产生（TDDFT研究）", "HHG in solids with and without topological edge states — Bauer & Hansen (2018)", "Many-body enhancement of high-harmonic generation in monolayer MoS2", "Nature 626", "PLAN", "Probing Phonon Dynamics and Electron-Phonon Coupling by High Harmonic Generation in Solids", "TDDFT", "TDSE", "Unveiling the Role of Electron-Phonon Scattering in Dephasing High-Order Harmonics in Solids", "dmft", "nonlinear-optics", "pump-probe", "含时密度泛函", "固体HHG", "圆二色性", "实时含时密度泛函理论", "层间剪切模", "库仑关联对单层TMDC高次谐波生成的影响", "强场驱动", "拓扑绝缘体", "施主掺杂带隙材料中的高次谐波增强", "时变密度泛函理论", "液态水中的高次谐波生成探测核量子涨落", "激光驱动晶体中 interband Berry 相位的实验观测（Uzan-Narovlansky et al.", "相位匹配", "自旋劈裂", "谷极化", "载波包络相位", "阿秒瞬态吸收", "非线性光学", "面向阿秒物理的时变密度泛函理论技术综述：从气相到固体", "高次谐波产生"]
source_raw: ""
growth_stage: "mature"
confidence: 0.9
source_reliability: "reliable"
sources: ["{"title": "briefing-2026-08-02.md", "source_type": "briefing"}"]
updated_at: "2026-11-15T14:03:47Z"
settled_count: 51
aliases: ["rt-TDDFT", "real-time TDDFT", "TDDFT", "time-dependent density functional theory", "含时密度泛函", "实时含时密度泛函"]
---

<!-- methods-settle:v1 -->

## 原理

统一Hamiltonian框架的rt-TDDFT通过实时传播含时Kohn-Sham/TDSE方程追踪强场电子动力学，通道完备性要点依然成立——实时传播Kohn-Sham轨道直接给出含时宏观电流的傅里叶谱，带内与带间HHG发射通道同时天然包含而无需通道分离假设（第一性原理同时含带内与带间电流，全谱量化键长-截止能量关系，避免紧束缚/两带模型对能带结构的简化误差）；Floquet拓扑分支——TDDFT含时模拟在双色（ω–2ω）圆偏振强场下第一性原理重现光修饰能带结构与光电子谱，区分Floquet杂化隙与多光子边带贡献；交错磁自旋动力学分支——RT-TDDFT直接模拟线偏激光脉冲下RuO2飞秒自旋动力学，给出光致净磁化约0.2 μB/晶胞；二维全光磁控分支——实时TDDFT直接给出强场下自旋/磁矩与光电流的逐时刻微观演化，作为二维材料面内光控磁态与全光磁控验证的第一性原理工具；频率混合谱学分支——多外场实时TDSE/TDDFT传播为非微扰区非线性光学提供不依赖微扰展开的模拟框架；磁-晶格动力学分支——非共线自旋rt-TDDFT耦合核运动同时演化电子与晶格自由度，把超快退磁拆分为电子贡献与声子-自旋耦合贡献两阶段（前20 fs电子驱动）；对称性验证分支——RT-TDDFT在保持规范与体系对称性的前提下数值验证选择定则、谐波偏振分布与二色信号，桥接对称性理论与实验谐波谱；Maxwell-TDDFT全极小耦合分支——时域麦克斯韦方程与KS-TDDFT双向自洽耦合传播，以全最小耦合形式实现超越偶极近似的光-物质第一性原理动力学（周期体系KS含时传播，octopus类实空间实现）；键长-截止能量分支——各向同性应变调制键长，7.5%键长压缩使固体HHG截止能量提升近三分之一，机制为带隙展宽诱导带间截止能量增强；周期体系基准与多尺度缺失环节分支——周期体系rt-TDDFT直接积分时变KS方程为硅等晶体强场电子动力学与HHG谱的第一性原理基准，单胞微观响应需与宏观相位匹配/传播耦合方能复现实验峰结构；动态U(t)分支——时间依赖DFT+U（RT-TDDFT+U）揭示强场动力学中在位Hubbard U随屏蔽电子演化，非平衡模拟需动态更新在位关联参数而非取固定U；拓扑相HHG对比分支——实空间网格、绝热LDA的实时TDDFT直接模拟强场驱动的有限长一维离子链，给出拓扑与平庸两相完整谐波谱与产率差异；DMFT关联核分支——将DFT+DMFT的含频局域自能映射为时间非局域TDDFT交换关联核，使实时传播在强场动力学中包含电子关联重整，而无关联核的TDDFT实时传播（BaTiO3强场电流/偶极HHG谱）作为对照基准时不出现超谐波，表明超谐波为关联诱导；激子HHG谱学分支——TDDFT+长程修正交换关联核在一维模型固体中同时演化强场能带动力学与电子-空穴相互作用，重现强束缚激子并观测其对HHG谱的调制；声子动力学-电声耦合分支——real-time TDDFT从第一性原理同时演化电子态与强场响应，无先验模型地给出固体HHG谱及其时间演化，用以以HHG探测声子动力学与电子-声子耦合；各向异性泛函-含时杂化分支——针对二维材料体系的各向异性泛函在正确带隙与交换的基础上做含时DFT光学响应，与长程修正XC核、动态U(t)、DMFT时间非局域核并列构成修正半局域绝热核带隙/交换误差的候选XC基础路径；耗散-电声散射分支——耗散型rt-TDDFT在标准相干传播中加入第一性原理碰撞积分（电子-声子散射），使真实晶体超快电子动力学模拟带上微观退相位与弛豫（与动态U(t)、DMFT时间非局域核分别对应退相与关联两类平均场缺失的互补修正方向）；泵浦-探测瞬态谱学分支——RT-TDDFT在不引入唯象参数的前提下实时传播泵浦驱动的非平衡电子态，作为整套超快泵浦-探测瞬态谱计算的动力学内核；阿秒瞬态吸收分支——TDDFT从头算模拟单层hBN的阿秒瞬态吸收谱，作为同时包含多体与局域场效应的阿秒时间分辨基准；多尺度传播耦合分支——rt-TDDFT从头算求解强场下单胞内带内电流与带间极化作为不含经验参数的微观谐波源项，TDDFT–Maxwell多尺度耦合把该源项逐薄片嵌入麦克斯韦传播方程并考虑局域场反馈，实现纳米-微米跨尺度自洽模拟；导带布居基准分支——rt-TDDFT含时演化作为无参数基准预言ZnO导带布居，直接给出多带耦合下的激发电子数并量化与Keldysh/SBE预言的偏差；含SOC光致能带重整分支——速度规范含时矢势+自旋轨道耦合的TDDFT在强场下逐周期追踪手性Te自旋劈裂能带的瞬态演化，给出超越静态Floquet模型的含SOC光致能带响应；手性声子磁光分支——TDDFT从头算给出CrI3中声子贡献的磁光响应，定量确认0.22 cm-1劈裂下圆二色信号仍可观测；四分量相对论手性响应分支——四分量相对论RT-TDDFT以含磁偶极/电四极响应的全相对论实时传播，直接给出强场下诱导分子电流与圆二色信号，是手性响应定量模拟的基准工具；滑移铁电HHG分支——实时TDDFT给出双层Td-WTe2无模型参数的第一性原理时间分辨电流与谐波谱，镜面对称破缺所致铁电态在偏振分辨HHG谱中产生稳健特征从而实现极化状态的光学辨识，电子-晶格耦合TDDFT进一步表明0.24 THz层间剪切模式足够慢、与负责谐波发射的超快电子响应有效解耦，确立HHG谱学作为二维滑移铁电与晶格对称性的非侵入探针；自旋极化缺陷HHG分支——自旋极化实时实空间TDDFT（含几何优化与原子力弛豫的真实缺陷体系，超越一维模型哈密顿量）直接输出自旋通道分辨的固态HHG谱，揭示同一非磁性固体（h-BN）中两个自旋通道的谐波结构可截然不同，提供自旋极化缺陷特异的HHG指纹与在非磁性宿主中独立操控自旋通道电子动力学的可能，IP-TDDFT对照计算进一步表明电子-电子相互作用（局域场效应）对缺陷固体HHG是必需的，而完整TDDFT中诱导密度演化与缺陷波函数空间结构共同决定谐波谱差异；非绝热Ehrenfest电荷有序分支（上轮待融合线索并入）——非绝热TDDFT结合Ehrenfest分子动力学在单次实时模拟中同时获得激发态电子结构演化与晶格受力，无需预设序参量即可观察电荷有序的自发涌现及其时标；RT-TDDFTB大规模分支（本轮新增）——实时含时密度泛函紧束缚（RT-TDDFTB）使数百原子等离激元纳米粒子的实时电子动力学在计算上可行，以其能级结构与偶极响应作为电子-电子散射动力学的底座，把统一实时传播框架经密度泛函紧束缚Hamiltonian近似扩展到全DFT成本不可及的介观纳米粒子尺度。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| h-BN键长各向同性压缩量（应变调制HHG截止能量） | 7.5% | paper:2025-2508.12563（r91） |
| 7.5%键长压缩下固体HHG截止能量提升幅度 | 近1/3（相对提升） | paper:2025-2508.12563（r91） |
| CrSBr电子驱动退磁阶段时长 | 前20 fs | paper:2025-2506.05058（r90） |
| CrI3手性声子磁光圆二色仍可观测对应的劈裂 | 0.22 cm-1 | paper:2025-2506.11258（r120） |
| 双层Td-WTe2层间剪切模式频率（与HHG电子响应解耦判据） | 0.24 THz | paper:2026-2604.25483（r123） |
| RuO2光致净磁化 | 约0.2 μB/晶胞 | 既有知识摘要（交错磁自旋动力学分支，早期轮次证据） |
| RT-TDDFTB可实时模拟的等离激元纳米粒子原子规模 | 数百原子 | paper:2026-2603.05695（本轮） |

## 适用边界

本质仍是相干平均场实时传播——绝热半局域/近似XC核的带隙、交换与关联误差需借助长程修正核、动态U(t)、DMFT时间非局域核或第一性原理碰撞积分修正，单胞结果还需与Maxwell传播/相位匹配多尺度耦合方能对照宏观实验，且全DFT实空间实现的计算成本限制可模拟尺度，扩展到数百原子等离激元纳米粒子须以RT-TDDFTB的紧束缚参数化近似换取，其精度受参数化传递性约束。

## 代表作

- paper:2026-2603.05695-real-time-electron-electron-scattering-dynamics-in-plasmonic
- paper:2025-2505.09387-technical-review-time-dependent-density-functional-theory-fo
- paper:2024-2409.08959-full-minimal-coupling-maxwell-tddft-an-ab-initio-framework-f
- paper:2017-1705.10707-ab-initio-multi-scale-simulation-of-high-harmonic-generation
- paper:2025-2508.12563-enhancing-cutoff-energy-of-solid-high-harmonic-generation-fr
- paper:2026-2607.17265-first-principles-electron-phonon-scattering-in-real-time-tdd
- paper:2024-PhysRevB.110.205136-correlation-induced-generation-of-superharmonics-in-the-high
- paper:2019-1901.00610-ultrafast-charge-ordering-by-self-amplified-exciton-phonon-d

## 证据日志

- 2026-10-24｜r90｜仅简报｜[paper:2025-2506.05058-ultrafast-magneto-lattice-dynamics-in-two-dimensional-crsbr] 实时含时密度泛函理论（rt-TDDFT，非共线自旋）：给出时间分辨的磁矩与电子态演化，识别出前20 fs电子驱动退磁阶段的微观来源。
- 2026-10-24｜r90｜仅简报｜[paper:2025-2506.05058-ultrafast-magneto-lattice-dynamics-in-two-dimensional-crsbr] 电子-离子耦合实时动力学（rt-TDDFT + 核运动）：同时演化电子与晶格自由度，从而把退磁拆分为电子贡献与声子-自旋耦合贡献两个阶段。
- 2026-10-24｜r91｜仅简报｜[paper:2024-2409.08959-full-minimal-coupling-maxwell-tddft-an-ab-initio-framework-f] Maxwell-TDDFT 自洽耦合传播：时域麦克斯韦方程与 KS-TDDFT 双向耦合，首次以全最小耦合形式实现超越偶极的光-物质第一性原理动力学。
- 2026-10-24｜r91｜仅简报｜[paper:2024-2409.08959-full-minimal-coupling-maxwell-tddft-an-ab-initio-framework-f] 周期体系 KS 含时传播（octopus 类实空间 TDDFT）：为固体强场响应提供可与解析模型对标的数值实现基础。
- 2026-10-24｜r91｜仅简报｜[paper:2025-2503.19433-lights-symmetry-asymmetry-and-their-role-in-nonlinear-optics] 实时含时密度泛函理论（RT-TDDFT）模拟：在保持规范与体系对称性的前提下数值验证选择定则、谐波偏振分布与二色信号，桥接对称性理论与实验谐波谱。
- 2026-10-24｜r91｜回原文｜[paper:2025-2508.12563-enhancing-cutoff-energy-of-solid-high-harmonic-generation-fr] 实时含时密度泛函理论（rt-TDDFT）：第一性原理同时包含带内与带间电流，全谱量化键长—截止能量关系，避免紧束缚/两带模型对能带结构的简化误差。
- 2026-10-24｜r92｜仅简报｜[paper:2026-2604.06927-development-of-ab-initio-hubbard-parameter-calculation-schem] 时间依赖DFT+U（RT-TDDFT+U, U(t)）：揭示强场动力学中U随屏蔽电子演化，提示非平衡模拟需动态更新在位关联参数。
- 2026-10-24｜r92｜仅简报｜[paper:2025-2505.09387-technical-review-time-dependent-density-functional-theory-fo] 实时含时密度泛函理论（real-time TDDFT）：周期体系下直接积分时变Kohn-Sham方程，给出硅等晶体强场电子动力学与HHG谱的第一性原理基准。
- 2026-10-24｜r92｜仅简报｜[paper:2025-2505.09387-technical-review-time-dependent-density-functional-theory-fo] Maxwell-TDDFT多尺度传播耦合：本文指出的缺失环节：单胞微观响应需与宏观相位匹配/传播耦合才能复现实验峰结构，指明多尺度建模方向。
- 2026-10-24｜r94｜仅简报｜[paper:2018-1711.05783-high-harmonic-generation-in-solids-with-and-without-topologi] 实时 TDDFT（实空间网格、绝热 LDA）：直接模拟强场驱动的有限长一维离子链，给出拓扑/平庸两相的完整谐波谱与产率差异。
- 2026-10-25｜r95｜仅简报｜[paper:2024-PhysRevB.110.205136-correlation-induced-generation-of-superharmonics-in-the-high] TDDFT实时传播（固体HHG模拟）：实时演化强场驱动下BaTiO3的电流/偶极得到HHG谱，作为无关联核时的对照基准（此时不出现超谐波）。
- 2026-10-25｜r95｜仅简报｜[paper:2024-PhysRevB.110.205136-correlation-induced-generation-of-superharmonics-in-the-high] DMFT自能导出的TDDFT交换关联核（DFT+DMFT→TDDFT映射）：将动力学平均场的含频局域自能映射为时间非局域XC核，使TDDFT在强场动力学中包含电子关联重整——本文核心技术。
- 2026-10-25｜r96｜仅简报｜[paper:2024-2104.07366-high-harmonic-spectroscopy-of-strongly-bound-excitons-in-sol] 含时密度泛函理论（TDDFT + 长程修正交换关联核）：在一维模型固体中同时演化强场能带动力学与电子-空穴相互作用，是重现强束缚激子并观测其对 HHG 调制的关键工具。
- 2026-10-25｜r97｜仅简报｜[paper:2023-2304.09459-probing-phonon-dynamics-and-electron-phonon-coupling-by-high] 实时含时密度泛函理论（real-time TDDFT）：从第一性原理同时演化电子态与强场响应，无先验模型地给出固体HHG谱及其时间演化。
- 2026-10-25｜r99｜仅简报｜[paper:2025-2504.01684-an-anisotropic-functional-for-two-dimensional-material-syste] TDDFT光学/含时杂化计算：在正确带隙与交换基础上做含时DFT光学响应，为非线性/强场模拟提供一致框架。
- 2026-10-30｜r100｜仅简报｜[paper:2026-2607.17265-first-principles-electron-phonon-scattering-in-real-time-tdd] 耗散型 rt-TDDFT（含碰撞项的实时 TDDFT）：在标准相干 rt-TDDFT 中加入第一性原理碰撞积分，使真实晶体超快电子动力学模拟首次带上微观退相位与弛豫
- 2026-10-31｜r105｜仅简报｜[paper:2025-2509.07612-first-principles-approach-to-ultrafast-pump-probe-spectrosco] 实时含时密度泛函理论（RT-TDDFT）：在不引入唯象参数的前提下实时传播泵浦驱动的非平衡电子态，是整套瞬态谱计算的动力学内核。
- 2026-10-31｜r105｜仅简报｜[paper:2025-2505.10813-attosecond-transient-absorption-spectroscopy-in-monolayer-he] 含时密度泛函理论（TDDFT）：从头算模拟单层hBN的阿秒瞬态吸收谱，作为包含多体与局域场效应的基准。
- 2026-10-31｜r106｜仅简报｜[paper:2025-2512.14328-in-plane-optically-tunable-magnetic-states-in-2d-materials-v] 实时含时密度泛函理论（real-time TDDFT）：直接给出强场下自旋/磁矩与光电流的逐时刻微观演化，是全光磁控验证的第一性原理工具。
- 2026-11-01｜r112｜仅简报｜[paper:2017-1705.10707-ab-initio-multi-scale-simulation-of-high-harmonic-generation] 实时 TDDFT（含时密度泛函理论）：从头算求解强场下单胞内带内电流与带间极化，提供不含经验参数的微观谐波源项。
- 2026-11-01｜r112｜仅简报｜[paper:2017-1705.10707-ab-initio-multi-scale-simulation-of-high-harmonic-generation] TDDFT–Maxwell 多尺度耦合传播：将微观电流作为源项逐薄片嵌入麦克斯韦传播方程并考虑局域场反馈，实现纳米-微米跨尺度自洽模拟。
- 2026-11-07｜r117｜仅简报｜[paper:2025-2503.16329-real-time-simulations-of-laser-induced-electron-excitations] 实时 TDDFT（rt-TDDFT）含时演化：作为无参数基准预言 ZnO 导带布居，直接给出多带耦合下的激发电子数，并量化与 Keldysh/SBE 预言的偏差。
- 2026-11-07｜r120｜仅简报｜[paper:2024-2411.13954-light-induced-renormalization-of-the-band-structure-of-chira] 含时密度泛函理论（TDDFT，速度规范含时矢势 + 自旋轨道耦合）：在强场下逐周期追踪手性 Te 自旋劈裂能带的瞬态演化，给出超越静态 Floquet 模型的含 SOC 光致响应。
- 2026-11-07｜r120｜仅简报｜[paper:2025-2506.11258-theory-of-infrared-magneto-optical-effects-from-chiral-phono] 含时密度泛函理论（TDDFT）：从头计算CrI3中声子贡献的磁光响应，定量确认0.22 cm-1劈裂下圆二色信号仍可观测。
- 2026-11-07｜r122｜仅简报｜[paper:2025-2503.16986-light-induced-persistent-electronic-chirality-in-achiral-mol] 四分量相对论实时TDDFT（RT-TDDFT）：含磁偶极/电四极响应的全相对论实时传播，直接给出强场下诱导分子电流与圆二色信号，是手性响应定量模拟的基准工具。（fallback：LLM 融合失败，附录式追加）
- 2026-11-07｜r122｜回原文｜[paper:2026-2607.17109-microscopic-origin-of-dephasing-in-solids-from-fir] 实时TDDFT（real-time TDDFT）：提供含时电子动力学与光响应/固体HHG谱的直接第一性原理模拟框架。（fallback：LLM 融合失败，附录式追加）
- 2026-11-08｜r123｜回原文｜[paper:2026-2604.25483-probing-sliding-ferroelectricity-in-bilayer-t-_-ma] 实时含时密度泛函理论（real-time TDDFT）：给出双层 WTe2 中无模型参数的第一性原理时间分辨电流与谐波谱。
- 2026-11-08｜r124｜回原文｜[paper:2019-1906.10224-high-harmonic-generation-from-spin-polarised-defects-in-soli] 自旋极化实时实空间TDDFT（含时密度泛函实时传播）：直接输出自旋通道分辨的固态HHG谱，揭示同一非磁性固体中两个自旋通道的谐波结构可截然不同。
- 2026-11-13｜r130｜仅简报｜[paper:2019-1901.00610-ultrafast-charge-ordering-by-self-amplified-exciton-phonon-d] 非绝热 TDDFT 结合 Ehrenfest 分子动力学：在单次实时模拟中同时获得激发态电子结构演化与晶格受力，无需预设序参量即可观察电荷有序的自发涌现及其时标。（fallback：LLM 融合失败，附录式追加）
- 2026-11-15｜r140｜仅简报｜[paper:2026-2603.05695-real-time-electron-electron-scattering-dynamics-in-plasmonic] RT-TDDFTB（实时含时密度泛函紧束缚）：使数百原子等离激元纳米粒子的实时电子动力学在计算上可行，提供能级结构与偶极响应作为散射动力学底座。

<!-- /methods-settle:v1 -->

在同一综述中统一1c / 2c amfX2C / 4c Dirac-Coulomb三种Hamiltonian处理瞬态吸收(TAS)与瞬态圆二色性(TCD)

<!-- linsai-wikilinks -->
## 关联概念

- [[1711.05783]]
- [[1809.06264]]
- [[1906.10224]]
- [[2024）]]
- [[2025-2502.01258-magnetizing-altermagnets-by-ultrafast-asymmetric-spin-dynami]]
- [[2025-2508_12563-enhancing-cutoff-energy-of-solid-high-harmonic-generation-fr]]
- [[2025-2512_01712-effects-of-zero-point-motion-in-the-high-harmonic-generation]]
- [[2026-2604_25483-probing-sliding-ferroelectricity-in-bilayer-t-_-ma]]
- [[2109.07693]]
- [[2304.09459]]
- [[2307.14090]]
- [[2401.09884]]
- [[2401.12929]]
- [[2407.16350]]
- [[2407.17917]]
- [[2505.09387]]
- [[2505.19894]]
- [[2508.12563]]
- [[2510.15207]]
- [[2512.01712]]
- [[2603.05346]]
- [[2603.19875]]
- [[2604.25483]]
- [[2607.17265]]
- [[2610.19967]]
- [[66]]
- [[Berry曲率]]
- [[CrSb]]
- [[First-principles electron-phonon scattering in real-time TDDFT]]
- [[Floss et al. 2021: Si与金刚石在近/中红外驱动下的高次谐波产生（TDDFT研究）]]
- [[HHG in solids with and without topological edge states — Bauer & Hansen (2018)]]
- [[Many-body enhancement of high-harmonic generation in monolayer MoS2]]
- [[Nature 626]]
- [[PLAN]]
- [[Probing Phonon Dynamics and Electron-Phonon Coupling by High Harmonic Generation in Solids]]
- [[TDDFT]]
- [[TDSE]]
- [[Unveiling the Role of Electron-Phonon Scattering in Dephasing High-Order Harmonics in Solids]]
- [[dmft]]
- [[nonlinear-optics]]
- [[pump-probe]]
- [[含时密度泛函]]
- [[固体HHG]]
- [[圆二色性]]
- [[实时含时密度泛函理论]]
- [[层间剪切模]]
- [[库仑关联对单层TMDC高次谐波生成的影响]]
- [[强场驱动]]
- [[拓扑绝缘体]]
- [[施主掺杂带隙材料中的高次谐波增强]]
- [[时变密度泛函理论]]
- [[液态水中的高次谐波生成探测核量子涨落]]
- [[激光驱动晶体中 interband Berry 相位的实验观测（Uzan-Narovlansky et al.]]
- [[相位匹配]]
- [[自旋劈裂]]
- [[谷极化]]
- [[载波包络相位]]
- [[阿秒瞬态吸收]]
- [[非线性光学]]
- [[面向阿秒物理的时变密度泛函理论技术综述：从气相到固体]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
