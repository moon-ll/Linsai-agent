---
title: "2026-2607_10397-on-the-measurability-of-wigner-time-delays-at-shape-resonanc"
type: "papers"
created: "2026-08-29T11:27:44Z"
updated: "2026-11-15T15:09:20Z"
tags: []
related: ["2607.10397", "RABBIT", "TDSE", "arpes", "pump-probe", "强场驱动", "莫尔超晶格", "量子几何", "阿秒条纹相机", "阿秒科学"]
source_raw: "2026-2607.10397-on-the-measurability-of-wigner-time-delays-at-shape-resonanc.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-25T15:43:52Z"
merged_from: ["wiki/papers/2607.10397.md"]
---

• # On the measurability of Wigner time delays at shape resonances in photodetachment of polyatomic anions

  ## 林赛的理解

  这项工作对我们组的意义非常直接：它指出了**用光剥离负离子（photodetachment）替代中性光电离来“干净”地测量 Wigner 时间延迟**的可行路径。中性体系里，长程库仑势让连续态—连续态（continuum-continuum, c-c）延迟在低能区（<20 eV）占据主导，必须额外建模或近似扣除；而负离子光剥离没有残余库仑势，c-c 延迟在 5–10 eV 以上基本消失，理论上可以直接读出电子散射共振的本征时间延迟。文中对 NO₃⁻ 的预测——低能 shape resonance 延迟可达 **1 fs**——正好落在阿秒/飞秒强场驱动的测量窗口里。对我们HHG、阿秒脉冲和强场驱动的研究而言，最有价值的操作启示是：**只有在电子出射方向接近光偏振方向时，测到的 RABBIT/streaking 延迟才等于 Wigner 延迟**；偏离该方向时，多 partial-wave 干涉会让测量延迟呈现与 Wigner 延迟不同的角分布。这一“偏振对齐出射”准则可以直接移植到我们的条纹相机、角分辨阿秒测量或 future anion-beam 实验中。虽然本文不涉及莫尔、交变磁等具体材料体系，但其对连续态相位、散射共振与 c-c 相位污染的精确处理，对我们研究强场驱动下的量子几何相位、低能电子散射以及后续拓展到更复杂分子/凝聚相体系都有方法论参考价值。

  ## 研究问题

  1. 在**多原子负离子光剥离**中，能否用 RABBIT 或 streaking 直接测得低能 shape resonance 处的 Wigner 时间延迟？
  2. 由于分子体系存在多个电子 partial-wave 贡献，**测量延迟（RABBIT/streaking）与内在 Wigner 延迟之间的角分布关系**是什么？在什么条件下二者等价？
  3. 以硝酸根负离子 NO₃⁻ 为具体对象，预测其价层与芯层（N 1s、O 1s）光剥离的时间延迟特征，并评估实验可行性。

  ## 研究背景

  阿秒科学的核心目标之一是把电子动力学探测到其自然时间尺度。光电子发射过程中， outgoing electron 与剩余离子/分子相互作用的相位信息被编码在波函数的复相位里，其能量导数即为 Wigner（Eisenbud-Wigner-Smith）时间延迟。RABBIT 和 streaking 等泵浦-探测技术通过附加红外场改变光电子谱，从而以阿秒精度提取该延迟，但红外场同时引入了 c-c 延迟，可能掩盖单光子 Wigner 延迟。

  在中性光电离中，残余正离子的长程库仑势使 c-c 延迟在低能（<20 eV）占主导，需要通过各种渐近近似或显式时域/频域模型扣除。尽管已有从惰性气体、分子、液体到固体的广泛应用，但库仑延迟仍是解释低能分子延迟特征的主要障碍。负离子光剥离没有残余库仑势，因而有望成为直接观测长单光子延迟和电子关联延迟的平台，并提供低能电子-分子散射共振（包括长寿命 shape resonance）的时间依赖图像。此前理论工作多集中于原子负离子（F⁻、Cl⁻、Br⁻、I⁻、Li⁻、H⁻）和小分子负离子（BeH⁻、C₂⁻、CN⁻），而多原子负离子体系的理论与实验研究几乎空白。本文选取 NO₃⁻，一方面因其 shape resonance 丰富，另一方面因其 O 1s 芯层光剥离被认为可在 XFEL 上实现角向自参考 streaking 实验。

  ## 研究方法

  本研究为**从头算理论计算**，采用固定核（fixed-nuclei）近似，除特别说明外均使用 Hartree 原子单位。

  - **单光子光剥离**：对 H⁻、Cl⁻ 和 NO₃⁻ 价层使用 **R-matrix 方法**（UKRmol+ 程序包）；对 NO₃⁻ 同时使用 **complex Kohn 方法** 与 **Schwinger 变分方法**（ePolyScat 程序包）以相互校验。
  - **RABBIT 延迟**：在含显式 c-c 跃迁的二阶微扰理论框架下计算吸收路径 M⁺ 与发射路径 M⁻，通过  
    \[
    \tau_R(E,\hat k)=\frac{1}{2\omega}\arg(M^{+*}M^-)
    \]
    提取 RABBIT 延迟；并与单光子 Wigner 延迟的有限差分近似  
    \[
    \tau_1(E,\hat k)=\frac{1}{2\omega}\arg\sum_{\ell,m,\mu} d^1_{\ell m\mu}(\Omega_+)^*d^1_{\ell m\mu}(\Omega_-)
    \]
    比较。
  - **时域模拟**：用 **R-matrix with time-dependence（RMT）** 方法求解含时薛定谔方程，分别模拟 RABBIT（阿秒脉冲列 + IR 场）和 streaking（单个阿秒脉冲 + IR 场）。RABBIT 信号在 sideband 能量 \(E_n=2n\omega-E_{\rm IP}\) 处拟合 \(P=a+b\cos[2\omega(\tau+\tau_R)]\)；streaking 则通过 \(\vec k_f(\tau)=\vec k_0-\vec A_{\rm IR}(\tau+\tau_S)\) 拟合提取 \(\tau_S\)。
  - **计算细节**：H⁻ 与 Cl⁻ 的束缚轨道在 MOLPRO 中用 Hartree-Fock 轨道（H⁻：aug-cc-pVTZ；Cl⁻：cc-pVTZ）；R-matrix 球半径 **120 bohr**，连续电子用 **240 条九阶 B-spline** 表示，H⁻ 最大角动量 \(\ell_{\max}=5\)，Cl⁻ \(\ell_{\max}=6\)。IR 光子能量取 **ω = 0.517 eV**。
  - **参考系**：先在分子坐标系计算，再通过数值平均得到实验室系（随机取向）结果。附录给出取向平均、阈值行为、Born 近似以及 H⁻ 角分布的进一步细节。

  ## 主要发现与核心结论

  - **光剥离是测量低能 Wigner 延迟的更干净平台**。由于没有残余库仑势，c-c 延迟在 **5–10 eV 以上基本为常数/可忽略**，远低于中性光电离中库仑延迟在 <20 eV 占主导的情况。
  - **H⁻ 是理想极限**：基态 1s 电子被 z 偏振光子剥离后只产生纯 p0 中间波。单光子延迟各向同性，R-matrix（static-exchange）给出峰值约 **21 as（在 6 eV）**，并在高能趋于零；若计入剩余氢原子极化，阈值处延迟为 **46 as**。由于单一 partial-wave 主导，RABBIT 延迟与单光子延迟在 **>5 eV** 时完全一致且各向同性。
  - **多 partial-wave 导致角依赖差异**：H⁻ 中 RABBIT 信号在 **θ ≈ 90°** 附近消失，引起相位 π 跳变，对应延迟跳变 **π/(2ω)=2 fs**（ω=0.517 eV）；延迟符号在 **~3 eV** 附近改变，导致 θ≈90° 处出现 **2π/(2ω)** 的不连续。
  - **Cl⁻ 展示典型分子式复杂行为**：3p 电子剥离后产生 s、d0 和 d±1 波，单光子谱受 **54 eV 处的 Cooper 最小** 主导，θ=0° 处出现约 **−100 as** 的负延迟。RABBIT 延迟与单光子延迟在一般角度上不同；但在 **θ=0°** 时，几何因子与 c-c 幅度效应几乎相互抵消，二者几乎重合。
  - **c-c 幅度效应不可完全忽略**：即使在高能极限，两个 intermediate partial-wave 的 c-c 系数比并不趋于 1，例如 Cl⁻ 中 \(|C_{d0\to p0}|/|C_{s\to p0}|\to 2/\sqrt5\approx0.89\)。这导致在 **~40 eV 和 ~70 eV**（\(|M^1_{p\to d0}|/|M^1_{p\to s}|\approx1\)）处 RABBIT 与单光子延迟差异最大；即使在 **100 eV**，大角度下仍有 **2–5 as** 的残余差异。
  - **NO₃⁻ 的预测**：价层与芯层光剥离在 **<25 eV** 区域由 shape resonance 主导，Wigner 延迟可达 **1 fs**。RABBIT/streaking 模拟表明，如此长的共振延迟可以在**可忽略的 c-c 延迟下被测量**，从而直接获得 Wigner 延迟。
  - **偏振方向出射是关键**：对多原子分子，RABBIT 延迟的角分布一般不同于 Wigner 延迟；但当电子出射方向接近光源偏振方向时，测量延迟与 Wigner 延迟在 **≳5 eV** 区域一致。
  - **芯层光剥离的简化特征**：NO₃⁻ 的 **N 1s 光剥离**属于单一/主导 intermediate partial-wave 情形，类似于 H⁻，其单光子与 RABBIT 延迟各向同性且一致。
  - **实验建议**：提出用 X 射线对 NO₃⁻ 进行 **O 1s 芯层光剥离**，结合自参考角向 streaking（self-referencing angular streaking）在 XFEL 上实施；前提是能够获得足够高的负离子密度。类似实验已在 LCLS 对 NO 和氮杂苯分子的光电离中实现。

  ## 潜在研究方向

  - **核运动效应**：本文采用固定核近似，忽略了 NO₃ 价层剥离后由 Jahn-Teller 和 pseudo-Jahn-Teller 效应引起的复杂非绝热振动动力学。后续需评估核运动对 shape resonance 能量、宽度和时间延迟的修正。
  - **实验实现瓶颈**：目前尚无负离子光剥离时间延迟的实验报道，主要挑战在于制备足够密度且稳定的分子负离子束流；O 1s 芯层方案需要软 X 射线 + IR 双束在 anion target 上实现。
  - **取向平均的 TDSE 计算**：实验室系 streaking 模拟需要对大量分子取向分别求解 TDSE，计算量 prohibitive；可发展近似取向平均或降维模型。
  - **更低能量行为**：文中重点在 >5 eV；<5 eV 区域 c-c 延迟并非完全消失，且剩余偶极与红外场的耦合可能重新引入延迟贡献，需要针对极性/多原子负离子进一步建模。
  - **芯层空穴与后续衰变**：O 1s 光剥离涉及内壳层空穴，Auger 衰变和芯层库仑后作用未被纳入，可能影响 X 射线 streaking 信号解释。
  - **体系拓展**：将方法推广到其他多原子负离子、团簇负离子乃至溶剂化负离子，建立低能电子-分子散射共振的时间域数据库。

  ## 与林赛研究的关联

  - 这项工作与本组 **HHG、阿秒脉冲、强场驱动** 的研究主线直接接壤：它提供了一条用负离子光剥离“绕过”库仑 c-c 延迟、直接测量 Wigner 延迟的技术路线，可融入我们未来的阿秒条纹相机或 RABBIT 实验设计。
  - 文中基于 partial-wave 展开、角分布选择与 c-c 相位分析的系统性方法，对我们理解和控制强场驱动电子发射中的相位/延迟信息具有直接借鉴价值；尤其是“只在偏振对齐方向读 Wigner 延迟”这一判据，可用于优化角分辨探测几何。
  - 低能 shape resonance 的 **fs 级时间延迟** 与强场电子再碰撞所探知的低能电子-分子散射共振属于同一物理区间，可桥接“静态散射相位”与“时间域延迟测量”。
  - 连续态相位的能量导数本质上是连续态的量子几何量，本文对散射相位与延迟的严格处理，可为我们在更复杂体系（包括未来涉及量子几何、莫尔超晶格能带工程的方向）中建立类似的相位-延迟分析框架。
  - 实验接口上，可与 XFEL 合作方讨论 NO₃⁻ 负离子束的 O 1s 自参考角向 streaking 方案；若实现，将成为负离子光剥离时间延迟的首次实验测量。

  ## 来源

  - 蒸馏自全文（deep-read）


## 合并自「2607.10397」

# On the measurability of Wigner time delays at shape resonances in photodetachment of polyatomic anions

**arXiv**: [2607.10397](https://arxiv.org/abs/2607.10397) | **方向**: attosecond science, RABBIT/streaking, photodetachment, Wigner delay, shape resonance

---

## 研究问题（Research Question）

Gap: RABBIT and streaking routinely measure photoionization time delays, but the long-range Coulomb tail + continuum-continuum delay hide every low-E (< 5 eV) feature, exactly where molecular shape resonances and electron-correlation signatures live. Negative-ion photodetachment has no Coulomb tail, so the Wigner delay is directly accessible; this paper systematizes that promise for polyatomics, computes 1-fs-class shape-resonance delays in NO3- (valence and core), and shows RABBIT/streaking can recover the Wigner delay (continuum-continuum negligible above 4 eV) if emission is along the IR/UV polarization axis. Concretely proposes a feasible O 1s self-referencing angular-streaking experiment at LCLS/XFEL.

## 研究背景（Background）

Two-sided relevance. (1) Methodological reference: in your solid-attosecond/attosecond-ARPES the < 5 eV time structure is precisely the regime Coulomb hides; the bare-Wigner baseline demonstrated here on NO3- is the cleanest theoretical anchor you can cite when fitting low-E streaking features in solids. (2) Practical bridge: the self-referencing core-streaking idea (N 1s vs O 1s sharing the same anion as intrinsic t=0) generalizes to solids — use shallow-core (e.g., M-edge or L-edge of a transition-metal element in a 2D TMD) of one constituent as the in-situ pump-probe time marker, replacing external XUV-IR interferometric stabilization. Feasibility-wise your 800 nm few-cycle + post-compression could access NIR-IR streaking; the anion-density challenge is foreign to solids, where you have plenty of bulk electron density.

## 研究方法（Methods）

- Three-method scattering cross-check on a polyatomic anion: R-matrix (UKRmol+), complex Kohn, Schwinger variational (ePolyScat) for fixed-nuclei Wigner delay.
- Perturbative RABBIT + time-dependent R-matrix-with-time-dependence (RMT) to simulate angle-resolved RABBIT and streaking spectra; the perturbative route is cheap for full angular scans, RMT for accuracy on selected angles.
- Self-referencing scheme: simultaneous detachment of N 1s and O 1s from the same NO3- anion provides an intrinsic time-zero, bypassing the need for a separate reference arm and reducing XUV/IR jitter to first order.

## 主要发现与核心结论（Main Results）

- NO3- valence detachment: shape resonances at 5.5 eV and 23 eV above threshold, with Wigner delays up to 1 fs and 100 as respectively.
- N 1s core detachment: shape resonance near 7 eV gives ~500 as Wigner delay; O 1s: two resonances at 6.5 and 16 eV with 900 as and 300 as.
- Along the IR/UV polarization direction, RABBIT/streaking delays coincide with single-photon Wigner delay and continuum-continuum delay is essentially negligible for E > 4 eV.
- Off the polarization axis the measured delay differs from the Wigner delay because of intermediate partial-wave interference; emission-direction selection is essential, not optional.
- H- and Cl- serve as analytic baselines: H- shows single partial wave, isotropic; Cl- already shows two-channel angular structure at high E, before going molecular.

## 潜在研究方向（Future Directions）

- Run the O 1s self-referencing angular streaking at LCLS or European XFEL: first direct measurement of femtosecond Wigner delay at a polyatomic shape resonance.
- Extend the protocol to a library of polyatomic anions (CN-, C2H-, halide cluster anions) to build a shape-resonance timing database.
- Theory side: heavy-element basis sets (Br-, I-, SF6-) require further development; relativistic + open-shell contributions near threshold need quantification.
- Bridge single-molecule anion to condensed-phase: cluster-anion photodetachment of (H2O)n- or (NH3)n- for size-dependent shape-resonance timing.



## 深度解析

### 研究问题（Research Question）

Gap: RABBIT and streaking routinely measure photoionization time delays, but the long-range Coulomb tail + continuum-continuum delay hide every low-E (< 5 eV) feature, exactly where molecular shape resonances and electron-correlation signatures live. Negative-ion photodetachment has no Coulomb tail, so the Wigner delay is directly accessible; this paper systematizes that promise for polyatomics, computes 1-fs-class shape-resonance delays in NO3- (valence and core), and shows RABBIT/streaking can recover the Wigner delay (continuum-continuum negligible above 4 eV) if emission is along the IR/UV polarization axis. Concretely proposes a feasible O 1s self-referencing angular-streaking experiment at LCLS/XFEL.

### 研究背景（Background）

Two-sided relevance. (1) Methodological reference: in your solid-attosecond/attosecond-ARPES the < 5 eV time structure is precisely the regime Coulomb hides; the bare-Wigner baseline demonstrated here on NO3- is the cleanest theoretical anchor you can cite when fitting low-E streaking features in solids. (2) Practical bridge: the self-referencing core-streaking idea (N 1s vs O 1s sharing the same anion as intrinsic t=0) generalizes to solids — use shallow-core (e.g., M-edge or L-edge of a transition-metal element in a 2D TMD) of one constituent as the in-situ pump-probe time marker, replacing external XUV-IR interferometric stabilization. Feasibility-wise your 800 nm few-cycle + post-compression could access NIR-IR streaking; the anion-density challenge is foreign to solids, where you have plenty of bulk electron density.

### 研究方法（Methods）

- Three-method scattering cross-check on a polyatomic anion: R-matrix (UKRmol+), complex Kohn, Schwinger variational (ePolyScat) for fixed-nuclei Wigner delay.
- Perturbative RABBIT + time-dependent R-matrix-with-time-dependence (RMT) to simulate angle-resolved RABBIT and streaking spectra; the perturbative route is cheap for full angular scans, RMT for accuracy on selected angles.
- Self-referencing scheme: simultaneous detachment of N 1s and O 1s from the same NO3- anion provides an intrinsic time-zero, bypassing the need for a separate reference arm and reducing XUV/IR jitter to first order.

### 主要发现与核心结论（Main Results）

- NO3- valence detachment: shape resonances at 5.5 eV and 23 eV above threshold, with Wigner delays up to 1 fs and 100 as respectively.
- N 1s core detachment: shape resonance near 7 eV gives ~500 as Wigner delay; O 1s: two resonances at 6.5 and 16 eV with 900 as and 300 as.
- Along the IR/UV polarization direction, RABBIT/streaking delays coincide with single-photon Wigner delay and continuum-continuum delay is essentially negligible for E > 4 eV.
- Off the polarization axis the measured delay differs from the Wigner delay because of intermediate partial-wave interference; emission-direction selection is essential, not optional.
- H- and Cl- serve as analytic baselines: H- shows single partial wave, isotropic; Cl- already shows two-channel angular structure at high E, before going molecular.

### 潜在研究方向（Future Directions）

- Run the O 1s self-referencing angular streaking at LCLS or European XFEL: first direct measurement of femtosecond Wigner delay at a polyatomic shape resonance.
- Extend the protocol to a library of polyatomic anions (CN-, C2H-, halide cluster anions) to build a shape-resonance timing database.
- Theory side: heavy-element basis sets (Br-, I-, SF6-) require further development; relativistic + open-shell contributions near threshold need quantification.
- Bridge single-molecule anion to condensed-phase: cluster-anion photodetachment of (H2O)n- or (NH3)n- for size-dependent shape-resonance timing.

### 来源

- [arXiv 2607.10397](https://arxiv.org/abs/2607.10397)
- 导入自 hermes 深度分析（2026-08-08T16:23:45Z）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：R-matrix / complex Kohn / Schwinger 变分三方法交叉校验 + 微扰 RABBIT + RMT 时域模拟（多原子负离子光剥离 Wigner 延迟）

**原理**：固定核近似下计算多原子负离子（NO₃⁻）光剥离时间延迟：负离子无残余库仑势，c-c 延迟 >4–5 eV 可忽略，shape 共振本征 Wigner 延迟可直接读出；单光子延迟用三种散射方法交叉校验，RABBIT 延迟 τ_R = (1/2ω)arg(M⁺*M⁻) 二阶微扰计算并经 RMT 含时薛定谔方程模拟（sideband 拟合 P = a + b·cos[2ω(τ+τ_R)]）；提出同分子 N 1s/O 1s 同时剥离的自参考角向 streaking 方案（本征 t=0，免外部参考臂）。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| R-matrix 球半径 | 120 bohr | 研究方法（计算细节） |
| 连续电子基组 | 240 条九阶 B-spline | 研究方法（计算细节） |
| 最大角动量 | H⁻ ℓ_max = 5；Cl⁻ ℓ_max = 6 | 研究方法（计算细节） |
| IR 光子能量 | ω = 0.517 eV | 研究方法（计算细节） |
| 束缚轨道 | H⁻ aug-cc-pVTZ；Cl⁻ cc-pVTZ（MOLPRO Hartree-Fock） | 研究方法（计算细节） |
| H⁻ 基准延迟 | 峰值 ~21 as @6 eV（static-exchange）；计极化阈值处 46 as | 主要发现 |
| NO₃⁻ 价层共振延迟 | 5.5 eV 共振达 1 fs；23 eV 共振 100 as | 主要发现 |
| NO₃⁻ 芯层共振延迟 | N 1s ~7 eV：~500 as；O 1s 6.5/16 eV：900/300 as | 主要发现 |
| Cl⁻ 参考量 | Cooper 最小 54 eV，θ=0° 负延迟 ~−100 as；c-c 幅度比极限 2/√5 ≈ 0.89 | 主要发现 |
| 偏振对齐判据 | 出射沿光偏振方向时 RABBIT/streaking 延迟 ≡ Wigner 延迟（E ≳ 5 eV） | 主要发现 |

**适用边界**：固定核近似忽略 Jahn-Teller/pseudo-Jahn-Teller 非绝热振动；<5 eV 区 c-c 延迟非完全消失（剩余偶极-IR 耦合重新引入）；偏离偏振轴出射时多 partial-wave 干涉使测量延迟 ≠ Wigner 延迟（方向选择是必要条件）；实验瓶颈为负离子束密度；O 1s 空穴 Auger 衰变未纳入。
**代表作**：On the measurability of Wigner time delays at shape resonances in photodetachment of polyatomic anions（arXiv:2607.10397）
*方法卡回补 2026-10-03*

<!-- linsai-wikilinks -->
## 关联概念

- [[2607.10397]]
- [[RABBIT]]
- [[TDSE]]
- [[arpes]]
- [[pump-probe]]
- [[强场驱动]]
- [[莫尔超晶格]]
- [[量子几何]]
- [[阿秒条纹相机]]
- [[阿秒科学]]
<!-- /linsai-wikilinks -->
