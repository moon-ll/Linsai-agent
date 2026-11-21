---
title: "固体 HHG 数值计算方法体系（TDSE / SBE / rt-TDDFT / 紧束缚）"
type: "method-topics"
created: "2026-11-01T03:30:00Z"
updated: "2026-11-01T12:40:00Z"
tags: ["方法专题", "固体HHG", "数值方法", "SBE", "TDDFT", "TDSE"]
related: ["量子几何量测量方法谱系", "SFA_CQSFA统一量子轨道框架", "PIMD___rt-TDDFT_模拟液态水核量子_HHG", "DFT计算", "相位匹配"]
source_raw: "ssh-weyl scheme + 课题A推导 + 库内方法卡(2610.19967/2610.15251/2508.15631/2508.00296) + 已核实外部文献"
growth_stage: "growing"
confidence: 0.9
---

# 固体 HHG 数值计算方法体系（TDSE / SBE / rt-TDDFT / 紧束缚）

> **专题定位**：强激光入射晶体后谐波谱的数值预言方法——四套范式的理论原理、
> 算法实现与适用边界对照，达到可参照复现的程度。服务于研究方案章的引擎选型、
> 参数表设计与可行性论证。测量路线层（为什么用 HHG）见 [[量子几何量测量方法谱系]]。

固体高次谐波自 Ghimire 等在 ZnO 块体中首次观测以来[1]，其数值描述逐步形成四套互相校验的范式：多带含时薛定谔方程（TDSE）、半导体 Bloch 方程（SBE）、实时含时密度泛函理论（rt-TDDFT）与参数化紧束缚（TB）模型族。Vampa 等将气体三步模型推广为固体版本——价带电子隧穿至导带、在能带内被强场加速、随后带间复合辐射[2]——奠定了半经典图像的统一语言；Yue 与 Gaarde 的教程对含时视角与 SBE 框架给出了系统化表述[4]。本文按"基本理论原理 → 核心算法实现 → 典型应用案例"三板块组织，参数与流程细节以课题库内已核验材料为锚。

## 一、基本理论原理

**1.1 三步模型的固体对应。** 强场下晶体电子动力学可拆解为三个亚过程：带间隧穿（tunneling，场强在带隙上制造非绝热跃迁窗口）、带内加速（intra-band acceleration，加速度定理 k(t)=k₀+(e/ℏ)A(t) 驱动电子在能带色散上运动）、带间复合（recombination，电子回落价带辐射光子）。谐波截止能量由「带隙 + 带内获得的动能」给出，宏观上还须叠加传播修正（见 [[相位匹配]]）。这一图像由 Vampa 等通过全光学能带重构实验证实[2][3]。

**1.2 SBE：密度矩阵表述。** 以长度规范为工作规范（与 Vampa 2015 及课题 A 记号约定一致），偶极矩阵元 d_cv(k)=⟨u_c|∂_k u_v⟩ 即 Berry 联络的带间分量。导带-价带相干 π_cv(k,t) 的演化由半导体 Bloch 方程描述：

- iℏ∂_t π_cv = ε_g(k) π_cv + E(t)·d_cv (p_cc − p_vv) + (退相干项)
- iℏ∂_t p_cc = 2E·d_cv Im(π_cv) + (带内输运项)

其中 ε_g(k) 为瞬时带隙，p_cc/p_vv 为布居。**退相干**以唯象 T₂ 项进入（幅值与实现规范是复现的关键参数，见 §2.2）。规范选择（长度/速度/TDP 处理）对谱定量的影响与记号约定在 Yue-Gaarde 教程 §4 有系统讨论[4]；课题 A 推导路线以长度规范锁定符号表并显式保留跃迁偶极相位的规范依赖。

**1.3 TDSE：波函数表述。** 在含 N 条能带的紧束缚/平面波基组下直接传播含时薛定谔方程，iℏ∂_t ψ = H[k(t)] ψ，无需布居/相干分解假设，天然包含多带耦合与非微扰效应，代价是标度随能带数迅速增长。

**1.4 rt-TDDFT：第一性原理表述。** 由 Runge–Gross 定理，实时传播含时 Kohn–Sham 方程即得宏观电流的傅里叶谱，带内与带间发射通道同时天然包含而无需通道分离假设，避免模型能带的简化误差[5][6]；代价是全第一性原理的计算成本，以及交换关联泛函的绝热近似误差（见 [[DFT计算]]）。

**1.5 TB 模型族：可调最小模型。** 以少数 hopping 参数参数化能带（如 SSH、Haldane、Kane-Mele、breathing Kagome、四带 BHZ），配合 EFT 幂次计数可把对称性破缺算符的谱签名解析化。其参数必须有第一性原理锚点（Wannier 化或 EDOS 拟合），避免自由调参——这是课题 A 推导路线在符号约定之后立的第一条纪律。

## 二、核心算法实现（可参照复现）

**2.1 通用工作流（四步）。** ① 结构与能带：DFT 或文献 TB 参数获得 ε_n(k)、d_cv(k)；② 场定义：矢势 A(t)，长度规范 E=−∂A/∂t；③ 时间演化：按范式选 SBE/TDSE/rt-TDDFT 引擎传播；④ 谱分析：宏观电流/极化的傅里叶变换 I(ω)=|ω²P(ω)|²，配合窗口函数与收敛性检查。库内 ssh-weyl 方案的引擎主窗参数：**1800 nm 基线 + MIR 3.2–6.4 μm 扩展窗，脉宽 30–100 fs，强度 10^10–10^11 W/cm²**；偏振三点（左旋/线/右旋）+ 椭圆率 ε∈[−1,1] 步长 0.1 连续扫描；取向扫描沿 You 2017 ZnO 实验配置[14]。

**2.2 SBE 引擎的复现要点。**
- **退相干时间 T₂ 分档**（库内 ssh-weyl 综合值，各档落在文献 1–10 fs 量级带内）：一维 SSH/Rice-Mele 链取 3 fs；二维 QWZ/Haldane 取 2 fs；三维 BHZ-HOTI 与 Weyl 半金属取 1.5 fs。同类体系参照：MgO 非微扰 SBE 计算取 T₁=7 fs、T₂=1.1 fs；单层 WSe₂ 反演得 T₂=24±1 fs（注明为下限，微扰区可比强场区长一个量级）[14]。
- **退相干算符实现**：在能量近简并子空间减小退相位算符幅值以消除载流子分布赝象（Thümmler 型修正，库内 scheme §第三步）。
- **验证清单**：γ=0 极限复现微扰光学系数；单带极限复现解析截止律；谱对时间步长与 k 网格收敛（ssh-weyl 采用 Γ 附近加密网格 + 双基线一致性 R/T 偏差 <10%）。

**2.3 TB 因果定位协议**（2610.19967 方法卡给出完整流程[10]）：单快照描述符穷举排除 → 映射到参数独立可调的低维 TB → 单参数替换测试定位关键物理量。参数锚定示例：r₀/σ_r 由氢键 O–O 对分布高斯加权拟合（判据 O···O≤3.5 Å、角≥150°）；γ_v 由投影 EDOS 的 Hann 核拟合；γ_c 按 3γ_v 并经激发态 EDOS 多核交叉验证。系综平均收敛判据：**50 snapshots 收敛至第 25 次谐波**。

**2.4 EFT 分层族**（2610.15251[11]）：H_λ(k)=|t/λ|[f(K_τ+λq)σ₊+h.c.]，尺度变换固定 v_F，把 warping 算符从 0 调到真实强度；展开参数 x=λa_cc·A₀ 领头阶有效至 x≈0.5，谷奇/谷偶谐波产量 ∝λ/∝λ²，λ=0 极限构成选择定则的严格空检验。

**2.5 范式选型表。**

| 需求 | 推荐 | 理由 |
|---|---|---|
| 对称性选择定则/解析标度 | TB+EFT | 幂次计数给出 ∝λ 标度，λ=0 空检验 |
| 多带耦合、非微扰、激子 | TDSE / rt-TDDFT | 无通道分离假设；TDDFT 第一性原理 |
| 反演工程化、参数扫描 | SBE | 成本低，T₂ 可控，适配 8 维约束扫描 |
| 液体/无序体系、核量子效应 | PIMD+rt-TDDFT | 电子-核时间尺度解耦（见 [[PIMD___rt-TDDFT_模拟液态水核量子_HHG]]） |

### 扩展 A：规范问题与跃迁偶极相位（TDP）处理

固体 HHG 理论的著名分歧：长度规范与速度规范的 SBE 在超出双带近似的真实材料计算中给出不同的谐波谱（尤其低阶），文献称 gauge issue。课题 A 推导路线的处置：① 全程锁定长度规范（与 Vampa 2015、Wang 2026 一致）；② 跃迁偶极相位（TDP）在某些模拟中被证明不重要（Gu & Kolesik 2022），但解析推导必须显式保留其规范依赖；③ 交叉检验用速度规范复算低阶谱对照（规范一致性作为数值正确性诊断之一）。
实用建议：对 ≥3 带模型，避免直接跨规范比较绝对产额；比较同规范下的相对量（各向异性比率、阈值位置）。

### 扩展 B：收敛与诊断清单（工程化扩展）

- **k 网格**：Γ 附近加密 + 全域均匀双层；谐波阶 N 的收敛要求 k 网格密度 ∝ N²（经验）
- **时间步**：传播子稳定性（Magnus 二阶 ~0.01 fs @ 10¹¹ W/cm²）
- **吸收边界**：动量空间无边界，实空间网格需 mask 防反射伪影
- **γ→0 检验**：场→0 极限复现微扰光学系数（χ⁽²⁾/线性吸收）
- **规范交叉检验**：长度/速度规范低阶谱定性一致
- **双基线一致性**：800/1800 nm 各自满足 R/T 偏差 <10% 才认定阈值有效

### 扩展 C：实验各向异性案例数字（联网检索补充）

- **MgO 各向异性（You 2017，Nat. Phys. 13, 345）**：谐波效率随激光偏振与晶轴夹角强烈变化，转动晶体呈**六重对称图样**（sixfold）——「谐波对成键敏感」的原始证明，开启晶向分辨 HHG；正确 DOI 10.1038/nphys3955（文献常误引 3911）。
- **ZnO（Ghimire 2011）**：首次块体 HHG 观测（截止 ~13 阶 @ 3.4 μm）；ZnO 激子结合能 ~60 meV 量级使其成为激子-HHG 通道竞争的原型。
- 后续：Garg 等「偏振分辨 ZnO 谐波」与 Langer 等「对称控制时域结构」把六重图样推进到偏振态层析与时域门控。

- Y. S. You, D. A. Reis, S. Ghimire, "Anisotropic high-harmonic generation in bulk crystals," Nat. Phys. 13, 345–349 (2017). https://doi.org/10.1038/nphys3955
- S. Ghimire et al., Nat. Phys. 7, 138 (2011). https://doi.org/10.1038/nphys1847

## 三、典型应用案例

**案例 1（材料族对比）**：Lorenzo 等以 Haldane/Kane-Mele/breathing Kagome 三个紧束缚模型系统对比 Chern/TI/HOTI 的 HHG 谱学，报告拓扑相相对平庸相产额增强上限两个数量级（第二版摘要收敛值）[8]——TB 族在拓扑指纹筛选上的代表作；库内 ssh-weyl 课题据此设定 R=2 的保守阈值下界。

**案例 2（多体效应）**：Sr₂CuO₃ Mott 绝缘体的 HHG doublon-holon 动力学亚周期追踪（反射 HHG + tdDMFT/NCA）[9]——关联体系中单粒子图像失效、需要多体引擎的实证；对应范式选型表「多体」行。

**案例 3（液相与核量子效应）**：首篇 PIMD+frozen-ion rt-TDDFT 液态水 HHG[10]，核量子离域致第一平台产额压制约一个量级、H19 局部极小——解耦假设与系综协议的完整复现路径见库内方法卡。

**案例 4（解析控制）**：EFT 分层 Hamilton 族将谷对比度的物理归因从数值观察提升为幂次计数定理[11]，并给出空检验滤除非物理谷信号的工作流。

**案例 5（气相-固相统一）**：Wang 等的气相 action phase 分解 φ_act=φ_coh+σ[12] 经 Thorpe 等的气-固统一框架[13]向固体迁移，课题 A 给出 σ_solid 的 inter/intra 双通道三分解推导路线——数值范式与解析相位理论在该路线交汇。

## 参考文献

[1] S. Ghimire, A. D. DiChiara, E. Sistrunk, P. Agostini, L. F. DiMauro, D. A. Reis, "Observation of high-order harmonic generation in a bulk crystal," Nat. Phys. 7, 138–141 (2011). https://doi.org/10.1038/nphys1847
[2] G. Vampa et al., "All-optical reconstruction of crystal band structure," Nature 522, 462–464 (2015). https://doi.org/10.1038/nature14517
[3] G. Vampa, T. J. Hammond, N. Thiré, B. E. Schmidt, F. Légaré, C. R. McDonald, T. Brabec, D. D. Klug, P. B. Corkum, "All-optical reconstruction of crystal band structure," Phys. Rev. Lett. 115, 193603 (2015). https://doi.org/10.1103/PhysRevLett.115.193603
[4] L. Yue, M. B. Gaarde, "Introduction to theory of high-harmonic generation in solids: a tutorial," arXiv:2111.08669 (2021, J. Opt. tutorial). https://arxiv.org/abs/2111.08669
[5] N. Tancogne-Dejean, A. Rubio, "Impact of the electronic band structure in high-harmonic generation spectra of solids," Phys. Rev. Lett. 118, 087403 (2017). https://doi.org/10.1103/PhysRevLett.118.087403
[6] N. Tancogne-Dejean, O. D. Mücke, F. X. Kärtner, A. Rubio, "Atomic-like high-harmonic generation from two-dimensional materials," Sci. Adv. 4, eaao5207 (2018). https://doi.org/10.1126/sciadv.aao5207
[7] S. Ghimire, A. D. DiChiara, E. Sistrunk, G. Ndabashimiye, U. B. Szafruga, A. Mohammad, P. Agostini, L. F. DiMauro, D. A. Reis, "High-harmonic generation from solids," Nat. Phys. 15, 10 (2019). https://doi.org/10.1038/s41567-018-0315-5
[8] B. Lorenzo et al., "High harmonic spectroscopy from lower-order to higher-order topological insulators," arXiv:2508.15631 (2025; 已刊 DOI: 10.1103/7zjc-4b4r). https://arxiv.org/abs/2508.15631
[9] "Tracking doublon-holon dynamics in high harmonic generation from Sr₂CuO₃ (反射 HHG + tr-反射 + tdDMFT/NCA)," arXiv:2508.00296. https://arxiv.org/abs/2508.00296
[10] Trenins, Tancogne-Dejean, Mondal, Rubio, Wörner, Kelly, Neufeld, Rossi et al., "High-harmonic generation probes quantum nuclear effects in liquid water (PIMD + frozen-ion rt-TDDFT)," arXiv:2610.19967 (2026). https://arxiv.org/abs/2610.19967
[11] Pais, Iorio, Ciappina, "EFT 分层 Hamilton 族 H_λ（可调 trigonal warping 的谷分辨 HHG 探针框架）," arXiv:2610.15251 (2026). https://arxiv.org/abs/2610.15251
[12] Wang et al., "Action phase decomposition φ_act = φ_coh + σ in gas-phase BSV-driven HHG," arXiv:2607.20941 (2026). https://arxiv.org/abs/2607.20941
[13] Thorpe et al., "气体-固体统一框架（h'κ/h''κ 双通道分解）," arXiv:2508.14212. https://arxiv.org/abs/2508.14212
[14] 库内综合：`/Users/ll/Desktop/LinSai-CoPilot/research_proposals/pending_review/general-ssh-weyl-20260920/04_proposal/sections/scheme.md`（本地可验证路径）（T₂ 分档、场窗、扫描协议；其中 T₂ 各档综合自 Walz/Klimmer 等 SBE 计算文献，原始 DOI 见该文件引文表）

<!-- linsai-wikilinks -->
## 关联概念

- [[量子几何量测量方法谱系]]
- [[PIMD___rt-TDDFT_模拟液态水核量子_HHG]]
- [[DFT计算]]
- [[SFA_CQSFA统一量子轨道框架]]
- [[相位匹配]]
- [[高次谐波产生]]
- [[B-spline_TDDFT_计算场自由_EWS_时延]]
- [[Chern数与贝里曲率计算]]
- [[EFT_框架下的_valley-resolved_HHG]]
- [[RABBITT]]
- [[SALMON_rt-TDDFT___Williams-Lax]]
- [[TDSE求解器]]
- [[Wannier-Bloch_轨迹方法]]
- [[arpes]]
- [[bayesian-inference]]
- [[bsv-driven-hhg-quantum_课题理论三角]]
- [[dft-pbe]]
- [[dft-u]]
- [[dft]]
- [[dmft]]
- [[fisher]]
- [[floquet-engineering]]
- [[houston]]
- [[informed]]
- [[landau]]
- [[metropolis]]
- [[mlff]]
- [[pump-probe]]
- [[p波磁体对称性分析]]
- [[sbe-bloch-equations]]
- [[tight-binding-model]]
- [[tomography]]
- [[trarpes]]
- [[半经典动力学方程贝里曲率反常速度]]
- [[双位点DFT加U修正]]
- [[含时密度泛函_TDDFT_方法]]
- [[应变工程晶格与单轴应变扫描]]
- [[现代极化理论与Berry相位计算]]
- [[磁性点群输运张量对称性分析]]
- [[磁空间群对称性与线性自旋波建模]]
- [[第一性原理DFT计算vdW修正滑移势垒]]
- [[第一性原理DFT计算非共线磁性SOC]]
- [[紧束缚___Houston_基自旋分辨_HHG_正演]]
- [[统一Hamiltonian框架的rt-TDDFT]]
- [[解析tight-binding]]
- [[量子几何张量分析]]
- [[高通量DFT计算流程]]
- [[pde]]
- [[Kubo公式线性响应输运计算]]
- [[TDSE]]
- [[Wigner-Smith时延]]
- [[bistritzer]]
- [[cc]]
- [[circular-dichroism]]
- [[runge]]
- [[sp-stm]]
- [[偏振_手性分辨谐波探测]]
- [[半导体布洛赫方程_SBE_方法]]
- [[固定能带半经典作用量与鞍点轨迹]]
- [[带内_带间电流分解]]
- [[平均场紧束缚密度矩阵反演]]
- [[磁空间群_晶体对称性分析]]
- [[自动微分构造方程残差网络]]
- [[自动微分构造物理约束损失]]
- [[自旋群_磁空间群对称性分析]]
- [[自旋轨道耦合磁各向异性能计算]]
- [[量子几何张量（量子度规）动量空间计算与可视化]]
<!-- /linsai-wikilinks -->
