---
title: "2026-2603_08203-large-differential-attosecond-delays-in-solid-stat"
type: "papers"
created: "2026-08-29T15:40:33Z"
updated: "2026-11-15T15:09:25Z"
tags: []
related: ["2603.08203", "Berry 曲率", "Large differential attosecond delays in solid state photoemission", "PLAN", "RABBIT", "RABBITT", "固体HHG", "固体高次谐波", "固体高次谐波产生", "强场驱动", "拓扑绝缘体", "拓扑表面态", "莫尔超晶格", "量子几何", "阿秒延迟测量", "阿秒条纹相机", "高次谐波产生"]
source_raw: "2026-2603.08203-large-differential-attosecond-delays-in-solid-stat.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-25T15:43:22Z"
merged_from: ["wiki/papers/2603.08203.md"]
---

• # Large differential attosecond delays in solid state photoemission

  ## 林赛的理解

  这项工作把固体光电子发射的时间延迟测量推进到了自旋-轨道劈裂近邻能级之间的“微分”比较，直接动摇了“光电子在固体内以弹道群速度传播”的简化图像。对我们来说，这意味着在 HHG/阿秒探针实验中，光电子从产生到被真空探测器记录的延时不能再简单归约为体相内的传播时间；表面处晶格周期性的破缺、多次散射以及消逝波与传播布洛赫波的干涉共同决定了出射动力学。Bi₂Te₃ 与 Bi₂Se₃ 这类强自旋-轨道耦合的拓扑绝缘体，恰好为我们研究强场驱动下量子材料的超快电子动力学、尤其是表面与体态耦合通道的相对权重，提供了一个可定量对照的体系。

  ## 研究问题

  论文要回答的核心问题是：当两条光电子出射通道能量差极小（仅为自旋-轨道劈裂量级，约 1 eV 到 3 eV）、且具有相同轨道角动量时，它们之间的相对光电子发射延迟 τ_DAD 由什么物理机制决定？具体来说，这些延迟是否可以归因于原子内延迟、弹道输运，还是必须引入包含表面散射的严格单步光发射理论才能解释？研究目标是通过自旋-轨道劈裂的芯能级实现“差分”阿秒延迟测量，从而以前所未有的能量分辨率探测光电子逸出时间 t_esc(E_kin) 在邻近能量处的精细结构。

  ## 研究背景

  阿秒 XUV 脉冲的出现使人们能够在时域中直接测量原子、分子和固体中的光电子发射延迟，但固体中的相对延迟长期以来主要被解释为光电子波包在体相内的弹道传播时间， phenomenological 参数（群速度 v_g、有效质量、末态寿命）取自体相能带结构。然而，已有研究表明共振、末态带隙、等离激元激发、电子屏蔽以及原子内多体相互作用都会显著影响光电子动力学。由于以往报道的相对延迟往往对应能量差很大的末态，导致多种贡献无法解耦。本文提出利用自旋-轨道劈裂的芯能级：这些通道能量接近、来自同一发射原子、且由相同轨道角动量决定选择定则，从而几乎消除了弹道传播模型的贡献，使得任何可观测的较大 τ_DAD 都只能来源于 t_esc(E_kin) 的非平庸能量依赖。此前的一维 Kronig-Penney 模型已经预言在带隙附近和 Cooper 极小值处 t_esc 会有强烈变化；本文首次在实验上提供证据，并将这一现象与单步光发射理论中的消逝波/传播波相对权重联系起来。

  ## 研究方法

  实验上，作者采用 RABBITT（通过双光子跃迁干涉重构阿秒拍频）光谱学，使用由第 57 阶（ℏω_HH57 = 90.6±0.4 eV）和第 59 阶（ℏω_HH59 = 93.8±0.4 eV）谐波组成的阿秒脉冲序列。近红外（NIR）脉冲中心波长 790 nm，压缩后约 18 fs，光子能量 ℏω_NIR = 1.59±0.01 eV，重复频率 3 kHz；两束光 p 偏振并以 85° 入射到样品表面。XUV 经 Mo-Si 多层膜反射（反射峰 91.2 eV，带宽 5.8 eV），仅保留上述两个相邻奇次谐波。光电子以法线方向进入无场飞行时间谱仪，接收角 ±3°。样品为原位解离的 Bi₂Te₃（Bridgman 法生长）和 Bi₂Se₃（CVT 法生长）单晶，基压 <10×10⁻¹⁰ mbar；在 Bi₂Te₃ 上进行了 213 次独立 RABBITT 测量（4 个样品），在 Bi₂Se₃ 上进行了 187 次独立测量（3 个样品）。每次测量含 200 个延迟步长，步长约 70 as。

  数据分析采用新近发展的“固定相位与振幅关系”复拟合法，对 NIR-XUV 延迟轴做非均匀离散傅里叶变换（NUDFT），使用 Kaiser-Bessel 窗函数（β=4）并补零，再以八阶超高斯滤波器（半高全宽 100 THz）提取 2f_NIR 分量，最终由相位差计算相对延迟。

  理论上，作者将单步光发射理论与 Eisenbud-Wigner-Smith（EWS）时间延迟形式结合（OSTEWS），用 DFT-LDA 计算初/末态波函数，并用增广平面波方法计算时间反演低能电子衍射（TR LEED）末态。光学势 V_opt 取 1 eV 与 2 eV 两个值，分别对应非弹性寿命 τ_inel = 329 as 与 165 as。为排除原子内延迟，作者还进行了单组态 Dirac-Fock 相对论计算，估算气相 Bi 原子 d5/2 与 d3/2 壳层之间的相对光电离延迟。

  ## 主要发现与核心结论

  实验测得 Bi₂Te₃ 与 Bi₂Se₃ 中自旋-轨道劈裂芯能级的微分阿秒延迟为：

  - Bi₂Te₃：τ_DAD(Bi 5d) = 30±13 as；τ_DAD(Te 4d) = −39±18 as
  - Bi₂Se₃：τ_DAD(Bi 5d) = 31±10 as；τ_DAD(Se 3d) = −93±83 as

  对应的第 58 阶边带动能为：Bi 5d3/2 位于 60.4±0.4 eV，Bi 5d5/2 位于 63.5±0.4 eV；Te 4d3/2 位于 47.0±0.4 eV，Te 4d5/2 位于 48.4±0.4 eV。Bi 5d 自旋-轨道劈裂为 3.05 eV，Te 4d 为 1.47 eV。

  这些延迟既不能归因于原子内延迟（Dirac-Fock 计算表明在当前光子能量范围内该贡献通常 <5 as），也不能用弹道传播模型解释（含电子-空穴相互作用与红外场穿透的 Jellium 模型或弹道模型给出的 Bi₂Te₃/Bi₂Se₃ 微分延迟不超过 3 as）。相反，基于 OSTEWS 的单步光发射理论定量复现了实验观测到的 τ_DAD 值。

  理论进一步显示，τ_DAD 随 XUV 光子能量变化剧烈，某些通道可达 ±200 as 以上（例如 Bi₂Te₃ 中 Te 4d）。计算还表明 d5/2 与 d3/2 光电子的绝对延迟 τ_OSTEWS 几乎完全相同，从而确认原子内自旋-轨道延迟可忽略；观测到的微分延迟本质上来源于同一芯能级两个分量被激发到末态连续谱中不同能量处，因而探测了 t_esc(E_kin) 的局部斜率。

  光学势 V_opt 对 τ_DAD 的符号和大小有显著影响：V_opt 从 1 eV 增加到 2 eV 时，某些光子能量处的 τ_DAD 可从约 −100 as 翻转为同等大小的正值。这是因为 V_opt 增强了消逝波出射通道的相对权重，而消逝波通道与带边传播通道具有本质上不同的动力学——消逝波出射被“提前”，带边处由于群速度趋于零而被显著“延迟”。最终结论是：固体光电子发射延时由表面处晶格周期性破缺导致的复杂多次散射决定，末态连续谱中消逝波与传播波的相对权重变化是产生大微分阿秒延迟的根源。

  ## 潜在研究方向

  1. **扩展到更多量子材料体系**：将差分阿秒延迟方法推广到强关联氧化物、二维材料、莫尔超晶格以及交变磁（altermagnetic）材料，研究对称性破缺如何调制消逝波与传播波通道的相对权重。
  2. **能量依赖映射**：当前装置无法连续调谐 XUV 光子能量，而理论预言 τ_DAD(E) 变化剧烈。未来利用可调谐阿秒源或多组谐波阶次，可在实验上完整绘制延迟随末态能量的变化曲线。
  3. **自旋与角分辨 RABBITT**：结合自旋分辨与角度分辨测量，分离拓扑表面态、体态与表面共振的贡献，定量区分不同对称性通道。
  4. **非平衡动力学**：引入泵浦-探针方案，研究强场驱动或光激发后电子占据数变化、屏蔽环境改变对阿秒延迟的瞬时调制。
  5. **理论与计算方法**：把 OSTEWS 框架与更精确的多体理论（超越 LDA 的动力学屏蔽、电子-声子相互作用）结合，为固体 HHG 和光电子能谱提供统一的延时解释。
  6. **HHG 相位互补探测**：探讨固体高次谐波产生中的相位信息能否作为光发射延迟的独立探针，以交叉验证多次散射与带内/带间动力学图像。

  ## 与林赛研究的关联

  这项工作与本组方向的接口非常直接。首先，它提醒我们：在利用 HHG 或阿秒条纹相机研究强场驱动固体电子动力学时，若把光电子从材料内部到真空探测器的延时简单等同于体相群速度传播时间，会系统性地误解实验相位。Bi₂Te₃/Bi₂Se₃ 的拓扑表面态、强自旋-轨道耦合与量子几何性质，为我们未来在类似体系中开展强场驱动、阿秒分辨实验提供了可定量对照的基准。其次，论文所用的 RABBITT 与单步光发射理论框架，可以直接迁移到我们对莫尔材料、交变磁材料以及低维量子材料的阿秒光电子能谱分析中——这些体系中 broken inversion symmetry 与复杂的自旋-轨道耦合会在末态连续谱中创造出更丰富的消逝波/传播波干涉结构。最后，从方法学角度，把“差分”思路引入我们的 HHG/光电子联合实验，有助于压制系统误差、提取由量子几何（如 Berry 曲率）或强场诱导能带混合带来的微小时间延迟信号。

  ## 来源

  - 蒸馏自全文（deep-read）


## 合并自「2603.08203」

# Large differential attosecond delays in solid state photoemission

**arXiv**: [2603.08203](https://arxiv.org/abs/2603.08203) | **方向**: attosecond science

---

## 研究问题（Research Question）

This work delivers the first measurement of differential attosecond delays (tau_DAD) by using spin-orbit-split core levels as nearly degenerate initial states, directly probing the derivative of the photoelectron escape time tesc(Ekin) with simultaneous high temporal and energy resolution. It fills a long-standing gap: previous relative photoemission delays compared channels with large energy differences and different angular momenta, which entangled transport, intra-atomic, and final-state effects. By isolating a few-eV energy window with identical initial-state symmetry, the authors unambiguously show that ballistic and intra-atomic pictures fail, and that only one-step photoemission theory with explicit surface scattering reproduces the data - forcing the field to abandon the nearly-free-electron group-velocity picture of photoemission timing in solids.

## 研究背景（Background）

Three concrete physical interfaces to Lin Sai's program. (1) Final-state continuum physics: the TR-LEED states with coexisting evanescent (band-gap, imaginary-k) and propagating Bloch components are the same band-structure construct that governs solid-state HHG in ZnO and TMDs - the HHG electron-hole trajectories traverse evanescent states inside band gaps, so the demonstrated 30-200 as escape-time modulation by evanescent/propagating weight directly informs how surface/interface scattering imprints phase and timing on harmonic emission. (2) Differential probing by spin-orbit-split or valley-contrasted states: the tau_DAD strategy of comparing nearly-degenerate channels that share initial symmetry maps onto TMD valley-HHG, where K/K' valley states or spin-orbit-split bands offer differential probes of valley- and spin-resolved final-state scattering times; an OSTEWS-style treatment could disentangle valley-contrast delays from transport. (3) Lightwave / petahertz electronics: the finding that emission timing is gateable by ~100 as purely through surface scattering (not ballistic velocity) suggests the surface itself is an ultrafast switch - the same surface-limited escape phase sets the launch condition for subsequent lightwave-driven transport, so petahertz-electronics schemes should treat the emission step as a dispersive, scattering-engineered timing element rather than an instantaneous injector.

## 研究方法（Methods）

- Differential attosecond delay (tau_DAD) concept: measuring the RABBITT delay difference between spin-orbit-split d5/2 and d3/2 core levels of the SAME emitter atom (ESO = 1-3 eV, same orbital angular momentum, same final-state continuum), which eliminates ballistic-transport ambiguity and isolates the derivative of the escape time tesc(Ekin) with high temporal AND energy resolution.
- Convolution-tolerant RABBITT delay extraction combining the complex-fit method with fixed RABBITT phase and amplitude relations between sidebands and principal bands (ref. [36]), enabling reliable delays even when spin-orbit splitting (e.g. Te 4d ESO = 1.47 eV approx  hbar*omega_NIR = 1.59 eV) produces spectrally overlapping, near-pi-shifted sideband oscillations.
- Signal-processing pipeline for delay extraction: non-uniform discrete Fourier transform (NUDFT, accounting for piezo-stage step non-uniformity), Kaiser-Bessel windowing (beta=4), zero-padding, and eighth-order super-Gaussian spectral filtering at 2f_NIR (FWHM 100 THz) to yield the complex frequency-integrated RABBITT spectrum Z(Ekin) fit with only 2 independent parameters per channel.
- OSTEWS one-step calculation pipeline: DFT-LDA initial states from a single-quintuple-layer slab (relativistic Koelling-Harmon second-variational), time-reversed LEED final states from a semi-infinite crystal via the extended augmented-plane-wave method, with a tunable optical potential Vopt; the photoelectron arrival time is the E-derivative of the dipole matrix-element phase referenced to a plane half a van-der-Waals gap above the topmost atomic layer.
- Single-configuration Dirac-Fock ab-initio gas-phase photoionization delay calculations used as a control to bound and exclude intra-atomic spin-orbit contributions at the experimental photon energies.

## 主要发现与核心结论（Main Results）

- Measured differential attosecond delays (tau_DAD = tau_d5/2 - tau_d3/2) on the order of 30-100 as: Bi2Te3 gives tau_DAD(Bi 5d) = 30 +/- 13 as (weighted mean of 213 RABBITT shots on 4 samples) and tau_DAD(Te 4d) = -39 +/- 18 as; Bi2Se3 gives tau_DAD(Bi 5d) = -93 +/- 83 as and tau_DAD(Se 3d) = 31 +/- 10 as. These are the same magnitude as delays previously reported between chemically distinct core levels, despite probing only a 1-3 eV spin-orbit energy gap.
- Ballistic transport is quantitatively excluded: Jellium time-dependent-Schrodinger-equation calculations (with electron-hole interaction and IR-field penetration) and ballistic propagation models predict tau_DAD <= 3 as for Bi2Te3/Bi2Se3 across a broad parameter range - an order of magnitude below experiment. The ballistic picture (tesc = Lambda/vg = tau_inel) cannot produce a 30% change in inelastic lifetime over a few eV.
- Intra-atomic spin-orbit delays are excluded: single-configuration Dirac-Fock gas-phase photoionization calculations predict relative d5/2-d3/2 delays < 5 as at the 90-94 eV photon energies used here; the same tau_OSTEWS(Ekin) curve for d3/2 and d5/2 channels (Supp. Fig. 7) confirms the differential delay is purely a final-state-energy effect, not an initial-state spin-orbit effect.
- One-step theory with Eisenbud-Wigner-Smith delay (OSTEWS) quantitatively reproduces all four experimental tau_DAD values. The TR-LEED final states contain both evanescent (imaginary-k, band-gap) and propagating (Bloch, current-carrying) components whose relative amplitudes vary strongly over the 1-3 eV spin-orbit energy scale, producing tesc variations of tens to >200 as.
- The OSTEWS tau_DAD curves show extreme photon-energy variability reaching well beyond +/-200 as (e.g. Te 4d in Bi2Te3). The sign and magnitude flip with the only free parameter, the optical potential Vopt (1 eV vs 2 eV, i.e. tau_inel = 329 as vs 165 as): at 72 eV in Bi2Te3, a -100 as feature becomes +100 as as Vopt increases, because Vopt preferentially weights evanescent emission channels.
- Physical mechanism for the sign structure: emission via evanescent TR-LEED states in band gaps is advanced (tunneling-like negative group delay), whereas emission via states at band edges is delayed due to vanishing group velocity (vg -> 0). The near-coincidence of tau_DAD(Bi 5d) approx 30 as in both Bi2Te3 and Bi2Se3 is accidental - a general property of solid-state photoemission, not material-specific.

## 潜在研究方向（Future Directions）

- Extend tau_DAD measurements across a tunable XUV photon-energy range (the OSTEWS curves predict +/-200 as variability) to map the full tesc(Ekin) landscape and locate band-gap/band-edge features in the final-state continuum of Bi2Te3/Bi2Se3 - currently infeasible with the fixed Mo-Si multilayer at 91 eV.
- Apply the tau_DAD spin-orbit-probe technique to other topological insulators and spin-orbit-coupled solids (e.g. TMDs, WSe2-type layered compounds, heavy-element surfaces) to test whether the evanescent/propagating interplay and the breakdown of the ballistic picture are universal fingerprints of structured final-state continua.
- Exploit the strong Vopt dependence of tau_DAD as a spectroscopic handle to constrain the inelastic lifetime tau_inel and optical potential from the time-domain data, inverting the usual assumption - delay measurements become a probe of electron-electron scattering phase space.
- Develop coherent-control or waveform-shaping schemes that selectively gate evanescent vs propagating final-state channels (e.g. via surface-plasmon or strong-field dressing), using the demonstrated 100-as tunability of emission timing as a controllable attosecond switch.
- Investigate the connection between surface-scattering-controlled emission timing and multi-photon strong-field regimes (HHG, lightwave electronics) where evanescent band-gap propagation is central, to test whether the same OSTEWS escape-time physics governs sub-cycle electron dynamics beyond single-photon photoemission.



## 深度解析

### 研究问题（Research Question）

This work delivers the first measurement of differential attosecond delays (tau_DAD) by using spin-orbit-split core levels as nearly degenerate initial states, directly probing the derivative of the photoelectron escape time tesc(Ekin) with simultaneous high temporal and energy resolution. It fills a long-standing gap: previous relative photoemission delays compared channels with large energy differences and different angular momenta, which entangled transport, intra-atomic, and final-state effects. By isolating a few-eV energy window with identical initial-state symmetry, the authors unambiguously show that ballistic and intra-atomic pictures fail, and that only one-step photoemission theory with explicit surface scattering reproduces the data - forcing the field to abandon the nearly-free-electron group-velocity picture of photoemission timing in solids.

### 研究背景（Background）

Three concrete physical interfaces to Lin Sai's program. (1) Final-state continuum physics: the TR-LEED states with coexisting evanescent (band-gap, imaginary-k) and propagating Bloch components are the same band-structure construct that governs solid-state HHG in ZnO and TMDs - the HHG electron-hole trajectories traverse evanescent states inside band gaps, so the demonstrated 30-200 as escape-time modulation by evanescent/propagating weight directly informs how surface/interface scattering imprints phase and timing on harmonic emission. (2) Differential probing by spin-orbit-split or valley-contrasted states: the tau_DAD strategy of comparing nearly-degenerate channels that share initial symmetry maps onto TMD valley-HHG, where K/K' valley states or spin-orbit-split bands offer differential probes of valley- and spin-resolved final-state scattering times; an OSTEWS-style treatment could disentangle valley-contrast delays from transport. (3) Lightwave / petahertz electronics: the finding that emission timing is gateable by ~100 as purely through surface scattering (not ballistic velocity) suggests the surface itself is an ultrafast switch - the same surface-limited escape phase sets the launch condition for subsequent lightwave-driven transport, so petahertz-electronics schemes should treat the emission step as a dispersive, scattering-engineered timing element rather than an instantaneous injector.

### 研究方法（Methods）

- Differential attosecond delay (tau_DAD) concept: measuring the RABBITT delay difference between spin-orbit-split d5/2 and d3/2 core levels of the SAME emitter atom (ESO = 1-3 eV, same orbital angular momentum, same final-state continuum), which eliminates ballistic-transport ambiguity and isolates the derivative of the escape time tesc(Ekin) with high temporal AND energy resolution.
- Convolution-tolerant RABBITT delay extraction combining the complex-fit method with fixed RABBITT phase and amplitude relations between sidebands and principal bands (ref. [36]), enabling reliable delays even when spin-orbit splitting (e.g. Te 4d ESO = 1.47 eV approx  hbar*omega_NIR = 1.59 eV) produces spectrally overlapping, near-pi-shifted sideband oscillations.
- Signal-processing pipeline for delay extraction: non-uniform discrete Fourier transform (NUDFT, accounting for piezo-stage step non-uniformity), Kaiser-Bessel windowing (beta=4), zero-padding, and eighth-order super-Gaussian spectral filtering at 2f_NIR (FWHM 100 THz) to yield the complex frequency-integrated RABBITT spectrum Z(Ekin) fit with only 2 independent parameters per channel.
- OSTEWS one-step calculation pipeline: DFT-LDA initial states from a single-quintuple-layer slab (relativistic Koelling-Harmon second-variational), time-reversed LEED final states from a semi-infinite crystal via the extended augmented-plane-wave method, with a tunable optical potential Vopt; the photoelectron arrival time is the E-derivative of the dipole matrix-element phase referenced to a plane half a van-der-Waals gap above the topmost atomic layer.
- Single-configuration Dirac-Fock ab-initio gas-phase photoionization delay calculations used as a control to bound and exclude intra-atomic spin-orbit contributions at the experimental photon energies.

### 主要发现与核心结论（Main Results）

- Measured differential attosecond delays (tau_DAD = tau_d5/2 - tau_d3/2) on the order of 30-100 as: Bi2Te3 gives tau_DAD(Bi 5d) = 30 +/- 13 as (weighted mean of 213 RABBITT shots on 4 samples) and tau_DAD(Te 4d) = -39 +/- 18 as; Bi2Se3 gives tau_DAD(Bi 5d) = -93 +/- 83 as and tau_DAD(Se 3d) = 31 +/- 10 as. These are the same magnitude as delays previously reported between chemically distinct core levels, despite probing only a 1-3 eV spin-orbit energy gap.
- Ballistic transport is quantitatively excluded: Jellium time-dependent-Schrodinger-equation calculations (with electron-hole interaction and IR-field penetration) and ballistic propagation models predict tau_DAD <= 3 as for Bi2Te3/Bi2Se3 across a broad parameter range - an order of magnitude below experiment. The ballistic picture (tesc = Lambda/vg = tau_inel) cannot produce a 30% change in inelastic lifetime over a few eV.
- Intra-atomic spin-orbit delays are excluded: single-configuration Dirac-Fock gas-phase photoionization calculations predict relative d5/2-d3/2 delays < 5 as at the 90-94 eV photon energies used here; the same tau_OSTEWS(Ekin) curve for d3/2 and d5/2 channels (Supp. Fig. 7) confirms the differential delay is purely a final-state-energy effect, not an initial-state spin-orbit effect.
- One-step theory with Eisenbud-Wigner-Smith delay (OSTEWS) quantitatively reproduces all four experimental tau_DAD values. The TR-LEED final states contain both evanescent (imaginary-k, band-gap) and propagating (Bloch, current-carrying) components whose relative amplitudes vary strongly over the 1-3 eV spin-orbit energy scale, producing tesc variations of tens to >200 as.
- The OSTEWS tau_DAD curves show extreme photon-energy variability reaching well beyond +/-200 as (e.g. Te 4d in Bi2Te3). The sign and magnitude flip with the only free parameter, the optical potential Vopt (1 eV vs 2 eV, i.e. tau_inel = 329 as vs 165 as): at 72 eV in Bi2Te3, a -100 as feature becomes +100 as as Vopt increases, because Vopt preferentially weights evanescent emission channels.
- Physical mechanism for the sign structure: emission via evanescent TR-LEED states in band gaps is advanced (tunneling-like negative group delay), whereas emission via states at band edges is delayed due to vanishing group velocity (vg -> 0). The near-coincidence of tau_DAD(Bi 5d) approx 30 as in both Bi2Te3 and Bi2Se3 is accidental - a general property of solid-state photoemission, not material-specific.

### 潜在研究方向（Future Directions）

- Extend tau_DAD measurements across a tunable XUV photon-energy range (the OSTEWS curves predict +/-200 as variability) to map the full tesc(Ekin) landscape and locate band-gap/band-edge features in the final-state continuum of Bi2Te3/Bi2Se3 - currently infeasible with the fixed Mo-Si multilayer at 91 eV.
- Apply the tau_DAD spin-orbit-probe technique to other topological insulators and spin-orbit-coupled solids (e.g. TMDs, WSe2-type layered compounds, heavy-element surfaces) to test whether the evanescent/propagating interplay and the breakdown of the ballistic picture are universal fingerprints of structured final-state continua.
- Exploit the strong Vopt dependence of tau_DAD as a spectroscopic handle to constrain the inelastic lifetime tau_inel and optical potential from the time-domain data, inverting the usual assumption - delay measurements become a probe of electron-electron scattering phase space.
- Develop coherent-control or waveform-shaping schemes that selectively gate evanescent vs propagating final-state channels (e.g. via surface-plasmon or strong-field dressing), using the demonstrated 100-as tunability of emission timing as a controllable attosecond switch.
- Investigate the connection between surface-scattering-controlled emission timing and multi-photon strong-field regimes (HHG, lightwave electronics) where evanescent band-gap propagation is central, to test whether the same OSTEWS escape-time physics governs sub-cycle electron dynamics beyond single-photon photoemission.

### 来源

- [arXiv 2603.08203](https://arxiv.org/abs/2603.08203)
- 导入自 hermes 深度分析（2026-08-08T16:23:45Z）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：固态大差分阿秒延迟的 RABBITT 测量（H57/H59 + 213/187 次独立测量 + NUDFT/Kaiser-Bessel + OSTEWS 理论）

**原理**：RABBITT：H57（90.6±0.4 eV）+ H59（93.8±0.4 eV）阿秒脉冲序列 + NIR 790 nm/18 fs/3 kHz p 偏振 85° 入射；Mo-Si 多层膜（91.2 eV/5.8 eV 带宽）选双谐波；法线 TOF ±3°；样品 Bi₂Te₃（Bridgman）213 次 + Bi₂Se₃（CVT）187 次独立测量（200 延迟步/70 as/基压 <10⁻¹⁰ mbar）；数据分析：固定相位-振幅关系复拟合 + NUDFT（Kaiser-Bessel β=4+补零+八阶超高斯 100 THz）提取 2f_NIR 分量；理论：OSTEWS（单步光发射+EWS，DFT-LDA 初/末态+增广平面波 TR LEED 末态，V_opt=1/2 eV→τ_inel=329/165 as）；Dirac-Fock 相对论估算气相 Bi d₅/₂-d₃/₂ 相对延迟排除原子内。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| SXR/NIR | H57 90.6±0.4 eV；H59 93.8±0.4 eV；NIR 790 nm/18 fs/3 kHz；p 偏振 85° | §研究方法 |
| 统计 | Bi₂Te₃ 213 次（4 样品）/Bi₂Se₃ 187 次（3 样品）；200 延迟步/70 as；基压 <10×10⁻¹⁰ mbar | §研究方法 |
| 理论 | OSTEWS；V_opt=1/2 eV→τ_inel=329/165 as；Dirac-Fock 原子内参考 | §研究方法 |

**适用边界**：OSTEWS 理论依赖单步模型近似；V_opt 两个值的不确定度（329/165 as 差异反映光学势敏感性）；页面提取限方法节（大差分延迟数值在结果）。
**代表作**：本文（arXiv:2603.08203）
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[2603.08203]]
- [[Berry 曲率]]
- [[Large differential attosecond delays in solid state photoemission]]
- [[PLAN]]
- [[RABBIT]]
- [[RABBITT]]
- [[固体HHG]]
- [[固体高次谐波]]
- [[固体高次谐波产生]]
- [[强场驱动]]
- [[拓扑绝缘体]]
- [[拓扑表面态]]
- [[莫尔超晶格]]
- [[量子几何]]
- [[阿秒延迟测量]]
- [[阿秒条纹相机]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
