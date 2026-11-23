# 超龄孤儿抽查表（前 50 条）

- 导出时间：2026-11-04T15:34:57Z
- 口径：42 天规则（`ORPHAN_MAX_AGE_DAYS=42`），在注册表深拷贝上复现 assign → form → recycle → prune 判定
- 即将清理总数：**268 条**；本表取前 50 条（存活天数降序，其次方向命中优先）
- 方向命中（核心范式 `core_theme_hit`，生产豁免口径 = 标题+摘要）：**268/268 （100.0%）**
- 对照口径（追加关键词后）：268/268 （100.0%）——关键词普遍带领域级标签，会显著虚高
- 最老存活天数：**81 天**
- 前 50 条覆盖唯一论文 48 篇（重复记录 2 条）
- 说明：生产链路 `prune_orphans(keep_fn=_is_core_theme_orphan)` 会保留核心范式孤儿；本表为 `keep_fn=None` 的 dry-run 口径，即"若无豁免将被清理"的集合。

| # | 论文标题 | arXiv/DOI | 方向命中 | 存活天数 | 所在簇最高相似度 | 首次入库时间 |
|---|---|---|---|---|---|---|
| 1 | Continuous relativistic high-harmonic generation from a kHz liquid-sheet plasma mirror | 2410.15404 | 是 | 81 | 0.133 | 2026-08-15T15:07:11Z |
| 2 | Valley-polarized Orbital and Spin Magnetism Induced by Femtosecond Optical Pulses in Two-Dimensional Semiconductors | 2605.31263 | 是 | 81 | 0.123 | 2026-08-15T14:53:44Z |
| 3 | Multi Moire Networks in Engineered Lateral Hetero-Bilayers: Programmable Phononic Reconfiguration and Second Harmonic Generation | 2505.01188 | 是 | 81 | 0.115 | 2026-08-15T14:33:29Z |
| 4 | Subcycle phase matching effects in short attosecond pulse trains | 2507.06386 | 是 | 81 | 0.115 | 2026-08-15T15:33:09Z |
| 5 | Optical control of electrons in a Floquet topological insulator | 2407.17917 | 是 | 81 | 0.112 | 2026-08-15T13:00:14Z |
| 6 | Terahertz third-harmonic generation of lightwave driven Weyl fermions far from equilibrium | 2508.16166 | 是 | 81 | 0.110 | 2026-08-15T15:26:57Z |
| 7 | Measuring and controlling the birth of quantum attosecond pulses | 2502.09427 | 是 | 81 | 0.105 | 2026-08-15T14:33:29Z |
| 8 | SALMON 2.3: Implementation of divide-and-conquer ground-state initialization for large-scale real-time TDDFT | 2606.21125 | 是 | 81 | 0.102 | 2026-08-15T15:33:09Z |
| 9 | Orbit-resolved spin holography: role of Coulomb focusing in target-dependent polarization | 2607.18118 | 是 | 81 | 0.100 | 2026-08-15T15:33:08Z |
| 10 | Multiscale Electronic Structure of Moiré Superlattices: Computational Cost Analysis Beyond 10,000 Atoms | 2608.09244 | 是 | 81 | 0.099 | 2026-08-15T14:24:55Z |
| 11 | Dynamical birefringence: Electron-hole recollisions as probes of Berry curvature | 1706.08449 | 是 | 81 | 0.096 | 2026-08-15T14:10:15Z |
| 12 | Quantum trajectory retrieval from solid-state high-harmonic spectra via deep learning | 2505.07230 | 是 | 81 | 0.093 | 2026-08-15T14:17:22Z |
| 13 | Electronic correlations in double ionization of atoms in pump-probe experiments | 1005.1253 | 是 | 81 | 0.093 | 2026-08-15T15:14:12Z |
| 14 | Terahertz third-harmonic generation of lightwave driven Weyl fermions far from equilibrium | 2508.16166 | 是 | 81 | 0.092 | 2026-08-15T15:26:57Z |
| 15 | Machine Learning Time Propagators for Time-Dependent Density Functional Theory Simulations | 2508.16554 | 是 | 81 | 0.092 | 2026-08-15T14:10:15Z |
| 16 | Magnon harmonic generation in antiferromagnets: Dynamical symmetry enriched by symmetry breaking | 2604.06700 | 是 | 81 | 0.091 | 2026-08-15T14:40:46Z |
| 17 | Attosecond Compression of Relativistic Electron Pulses via Continuous Harmonic Undulator Resonance | 2605.31083 | 是 | 81 | 0.090 | 2026-08-15T14:17:22Z |
| 18 | Symphony on Strong Field Approximation | 1812.11447 | 是 | 81 | 0.089 | 2026-08-15T15:20:52Z |
| 19 | Transient absorption and reshaping of ultrafast XUV light by laser-dressed helium | 1010.4558 | 是 | 81 | 0.089 | 2026-08-15T15:14:12Z |
| 20 | Extreme Ultraviolet High-Harmonic Interferometry of Excitation-Induced Bandgap Dynamics in Solids | 2502.20564 | 是 | 81 | 0.089 | 2026-08-15T15:26:57Z |
| 21 | Real-Time Time-Dependent Density Functional Theory for Pump-Probe Spectroscopies | 2605.27252 | 是 | 81 | 0.089 | 2026-08-15T15:00:32Z |
| 22 | High-efficiency water-window x-ray generation from nanowire array targets irradiated with femtosecond laser pulses | 2012.08856 | 是 | 81 | 0.088 | 2026-08-15T15:20:52Z |
| 23 | Twist tunable resonances in photonic bilayer for second harmonic generation | 2607.11300 | 是 | 81 | 0.086 | 2026-08-15T14:24:55Z |
| 24 | Magnetic- and electric-field-induced anomalous Hall currents from optical excitation of layered magnetic materials | 2410.05170 | 是 | 81 | 0.084 | 2026-08-15T14:10:15Z |
| 25 | Spin Splitting in Altermagnetic RuO2 Enables Field-free Spin-Orbit Torque Switching via Dominant Out-of-Plane Spin Polarization | 2407.07447 | 是 | 81 | 0.084 | 2026-08-15T14:40:46Z |
| 26 | Robust strong-field theory model for ultrafast electron transport through metal-insulator-metal tunneling nanojunctions | 2503.14531 | 是 | 81 | 0.084 | 2026-08-15T15:33:09Z |
| 27 | Introduction to theory of high-harmonic generation in solids: tutorial | 2111.08669 | 是 | 81 | 0.082 | 2026-08-15T15:07:12Z |
| 28 | A Unified Heterogeneous Implementation of Numerical Atomic Orbitals-Based Real-Time TDDFT within the ABACUS Package | 2603.21835 | 是 | 81 | 0.082 | 2026-08-15T14:17:22Z |
| 29 | SALMON 2.3: Implementation of divide-and-conquer ground-state initialization for large-scale real-time TDDFT | 2606.21125 | 是 | 81 | 0.082 | 2026-08-15T15:33:09Z |
| 30 | Broadband nonlinear Hall response and multiple wave mixing in a room temperature altermagnet | 2511.10471 | 是 | 81 | 0.081 | 2026-08-15T14:40:46Z |
| 31 | Attosecond quantum spectroscopy with entangled photon pairs | 2604.06707 | 是 | 81 | 0.080 | 2026-08-15T14:40:46Z |
| 32 | Keldysh tuning of photoluminescence in a lead halide perovskite crystal | 2407.15253 | 是 | 81 | 0.080 | 2026-08-15T14:40:46Z |
| 33 | Modular multiscale approach to modelling high-harmonic generation in gases | 2507.04115 | 是 | 81 | 0.080 | 2026-08-15T15:33:09Z |
| 34 | Light-Induced Valleytronics in Pristine Graphene | 2011.04973 | 是 | 81 | 0.080 | 2026-08-15T14:10:15Z |
| 35 | Attosecond physics in optical near fields | 2507.02673 | 是 | 81 | 0.079 | 2026-08-15T15:33:08Z |
| 36 | Ultrafast altermagnetophononics | 2607.13863 | 是 | 81 | 0.079 | 2026-08-15T14:17:22Z |
| 37 | Femtosecond Near-Infrared Ablation Thresholds of 2D Heterostructures: h-BN Encapsulated Graphene and TMD Monolayers | 2608.09312 | 是 | 81 | 0.078 | 2026-08-15T14:24:55Z |
| 38 | Compact realization of all-attosecond pump-probe spectroscopy | 2306.16212 | 是 | 81 | 0.077 | 2026-08-15T15:14:12Z |
| 39 | Attosecond metrology of bright quantum light | 2607.06395 | 是 | 81 | 0.077 | 2026-08-15T14:17:22Z |
| 40 | Spontaneous spin splitting and tunable valley polarization in a two-dimensional fully compensated ferrimagnet | 2606.25843 | 是 | 81 | 0.076 | 2026-08-15T14:24:55Z |
| 41 | Formation and Controlling of Optical Hopfions in High Harmonic Generation | 2410.06032 | 是 | 81 | 0.075 | 2026-08-15T15:07:11Z |
| 42 | Sculpting ultrafast mid-infrared light for solid-state high harmonic generation | 2512.19412 | 是 | 81 | 0.075 | 2026-08-15T15:26:58Z |
| 43 | Circular dichroism in second- and third-harmonic generation in chiral topological semimetal CoSi | 2604.03983 | 是 | 81 | 0.073 | 2026-08-15T14:53:44Z |
| 44 | Crystal symmetries and harmonic generation in altermagnets | 2408.16926 | 是 | 81 | 0.073 | 2026-08-15T14:10:15Z |
| 45 | SinBasis Networks: Matrix-Equivalent Feature Extraction for Wave-Like Optical Spectrograms | 2505.06275 | 是 | 81 | 0.073 | 2026-08-15T14:17:22Z |
| 46 | Adiabatic approach for high harmonic generation in solids induced by intense low-frequency pulses | 2512.24496 | 是 | 81 | 0.072 | 2026-08-15T14:10:15Z |
| 47 | Harmonic generation by metal nanostructures optically coupled to 2D transition metal dichalcogenide | 1812.09339 | 是 | 81 | 0.072 | 2026-08-15T15:14:12Z |
| 48 | High intensity attosecond beamline for XUV pump XUV probe measurements with photon energies up to 150 eV | 2604.12602 | 是 | 81 | 0.071 | 2026-08-15T15:33:09Z |
| 49 | Attosecond All-Optical Retrieval of Valley Polarization via Circular Dichroism in Transient Absorption | 2412.19612 | 是 | 81 | 0.071 | 2026-08-15T15:26:57Z |
| 50 | Photonic time stretch fieldoscopy: single-shot electric field detection at near-petahertz bandwidth | 2512.03665 | 是 | 81 | 0.070 | 2026-08-15T15:00:32Z |
