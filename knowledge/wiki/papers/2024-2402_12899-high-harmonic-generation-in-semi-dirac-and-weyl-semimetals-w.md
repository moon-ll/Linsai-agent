---
title: "2024-2402_12899-high-harmonic-generation-in-semi-dirac-and-weyl-semimetals-w"
type: "papers"
created: "2026-09-26T14:05:38Z"
updated: "2026-11-15T15:09:23Z"
tags: []
related: ["2402.12899", "Berry 曲率", "Berry曲率", "High-harmonic generation in semi-Dirac and Weyl semimetals with broken time-reversal symmetry: Exploring merging of Weyl nodes", "Weyl semimetal", "general-ssh-weyl-20260920", "交变磁体", "固体HHG", "强场超快", "强场驱动", "自旋劈裂", "量子几何"]
source_raw: "2024-2402.12899-high-harmonic-generation-in-semi-dirac-and-weyl-semimetals-w.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-27T01:00:43Z"
merged_from: ["wiki/papers/2402.12899.md"]
---

• # High-harmonic generation in semi-Dirac and Weyl semimetals with broken time-reversal symmetry: Exploring merging of Weyl nodes

  ## 林赛的理解

  这篇工作对我们组的意义很直接：它把"反常高次谐波（AHHG）到底探什么"这个问题在拓扑半金属家族里讲清楚了——AHHG 不探 Berry 曲率本身，而是探**对严格线性（锥形）色散的偏离**。当一对 Weyl 节点相互靠近并合并为 semi-Dirac 节点时（抛物线方向沿节点分离矢、另两维保持锥形），反常谐波强度显著增强并在 |γ|=1 和 |γ|=3 处出现峰。这给了我们一个可操作的实验判别工具：用横向（垂直于偏振和节点分离方向）电流谱的谐波强度剖面，区分 Weyl、3D Dirac 和 semi-Dirac 三种 regime——这正是"HHG 作为谱学表征手段"路线里一直被含糊带过的核心物理。对我们 NSFC-强场超快方向，这可以接入 HHG/阿秒表征拓扑材料与量子几何的课题框架：量子几何（Berry 曲率、跃迁偶极）在这里被作者显式拆解，结论是 Berry 曲率贡献与带间贡献量级相当、不能用 Berry 曲率单独解释——这个"反面结论"对我们写 proposal 时论证"为什么需要全 SBE 动力学而非唯象几何响应"非常有用。另一个可复用的点是他们的机制图像：远离节点的非线性色散区域贡献不抵消、节点靠近 Γ 点时抵消失效，以及 γ≈2.9 处因贡献区域收缩再扩张而产生的强度 dip——这种"对称性→抵消→偏离对称极限即信号"的论证套路，可以直接搬到我们对莫尔体系平带、对交变磁体系动量依赖自旋劈裂的 HHG 分析里。

  ## 研究问题

  论文的核心问题是：**在破缺时间反演对称（TRS-broken）的拓扑半金属中，反常高次谐波（AHHG，即垂直于驱动电场的电流响应中的高次谐波）的微观起源是什么？它如何随一对 Weyl 节点的间距变化，并在节点合并为 semi-Dirac 节点（沿分离方向抛物线、另两维锥形的 parabolic-2D-conical 色散）时发生什么变化？** 具体拆解为三个子问题：

  1. 在 Weyl 节点分离很大的 regime，反常谐波究竟由什么决定——拓扑（Berry 曲率/Chern 数）还是色散的非线性偏离？
  2. 节点靠近并合并（|γ|→1、|γ|→3）过程中，AHHG 强度如何演化，semi-Dirac regime 是否增强？
  3. 这些结果能否为实验上区分 Weyl、Dirac 与 semi-Dirac 半金属提供可判别的光谱特征？

  ## 研究背景

  - 凝聚态 HHG 因超快光学应用潜力和作为材料表征手段受到广泛关注；Dirac/Weyl 半金属因无能隙线性能带色散和高载流子迁移率被认为是高效 HHG 体系。
  - Weyl 半金属中线性反常响应（反常 Hall）正比于 Weyl 节点间距，因而与拓扑直接相关；反常高次谐波曾被提议用于探测 Berry 曲率（Weyl 点处 Berry 曲率发散），但有工作指出 Berry 曲率贡献并非在所有驱动频率下都占主导。
  - Weyl 节点带合并可产生拓扑平庸但色散奇异的 **semi-Dirac** regime（沿节点分离方向抛物线、垂直平面 2D 锥形），需与双 Weyl（double-Weyl，两方向抛物线）区分。实例材料：SrNbO₃（四重简并 semi-Dirac 点由非对称空间群对称保护）、ZrTe₅（parabolic-2D-conical 色散但带 6 meV 微小能隙）。
  - 已有理论工作研究 TRS 破缺或反演对称破缺 DSM/WSM 中的 AHHG，其中 Avetissian 等（Phys. Rev. A 106, 033107 (2022)）认为分离 Weyl 节点的 AHHG 随节点间距增大——本文作者指出该结论与他们的结果矛盾（分歧在补充材料 S6 中给出解释），并指出"Weyl 物理中哪些因素真正贡献于 AHHG"的定性理解仍然缺乏。
  - 同期相关研究：Bharti & Dixit（Phys. Rev. B 107, 224308 (2023)）在多 Weyl 体系中发现 AHHG 增强，强调导带高占据的作用——本文提供互补视角（色散非线性的作用）。

  ## 研究方法

  - **模型**：最小 3D 两能带晶格 Hamiltonian H(k)=∑ᵢdᵢ(k)σᵢ，dₓ = t cos(akₓ)+t cos(bk_y)+t cos(ck_z)−γ，d_y = t sin(bk_y)，d_z = t sin(ck_z)（对称参数选择 tₓ=t_y=t_z=t，a=b=c）。Hamiltonian 破缺 TRS、保留反演对称与镜像对称；±γ 的 Hamiltonian 由幺正变换联系（σ_z H(R−k̃,−γ)σ_z = H(k,γ)）。
  - **相图**（随 γ 变化，详见 SM S1）：|γ|>3 为平庸绝缘体；1<|γ|<3 为一对 Weyl 节点；|γ|<1 为两对 Weyl 节点；临界点上 semi-Dirac regime——|γ|=3 单个 semi-Dirac 节点（k₀=(0,0,0)），|γ|=1 三个 semi-Dirac 节点。半 Dirac 点位于时间反演不变动量（TRIM），全 BZ 共 8 个；Weyl 锥在 k₀=π/2（γ=±2）时各向同性。
  - **驱动**：t=0 时刻施加 z 偏振超短红外脉冲，E(t)=E₀f_τ(t−T/2)sin(ω₀t)，高斯包络 f_τ(t)=exp(−t²/(2τ²))。
  - **动力学**：Houston 基下的半导体 Bloch 方程（SBE）描述密度矩阵 ρᵏ_mn，含退相干时间 T₂；初态为满价带。电流由速度矩阵元加权密度矩阵求和，辐射谱 I(ω)=ω²|J(ω)|²（Larmor 公式）；用宽度 2δω=ω₀ 的滤波器提取各阶谐波的时间序列。
  - **数值参数**（取 a=1 Å、t=1 eV）：ℏω₀ = 0.2 eV，E₀ = 0.043 V/Å，τ = 40 fs，T = 790 fs，T₂ = 3 fs（沿用 Phys. Rev. B 105, 155140 (2022) 的选择），布里渊区 60³ 离散。
  - **低能连续模型**：对 Γ 点做 Taylor 展开得到 semi-Dirac 连续模型，与晶格结果对比验证主导贡献来自 Γ 附近；对分离 Weyl 节点做线性化展开以分析对称性导致的抵消。

  ## 主要发现与核心结论

  1. **分离 Weyl 节点 regime：反常高次谐波消失（线性化极限下）**。对每个分离良好的 Weyl 节点，绕节点存在 C2z 转动对称（轴为电场偏振方向），给出 J_y(qₓ,q_y,q_z) = −J_y(−qₓ,−q_y,q_z)，线性化（锥形色散）近似下各节点附近的贡献相互抵消。因此：(i) 线性化 Weyl 色散下 AHHG 响应为零；(ii) 有限响应只能来自对严格线性的偏离——即色散不再锥形但仍非零激发的动量区域。此结论在（一定限制下）对 tilted type-I Weyl 半金属同样成立。这与 Avetissian 等提出的"AHHG 随节点间距增大"图像相反（分歧解释见 SM S6）。
  2. **semi-Dirac regime 反常谐波显著增强**。横向谱 I_y 中偶次谐波因反演对称消失；semi-Dirac regime（γ=1 和 γ=3）高次谐波强度远高于 WSM regime（γ=2）。峰强度随 γ 的扫描（Fig. 4，按 max_γ I_y 归一）显示：基频 √I₀=16.09，三次谐波 √I₀=0.269，五次 √I₀=0.029，七次 √I₀=0.001；满足对称性 I_y(γ)=I_y(−γ) 且 I_y(γ=0)=0（源于反演对称与式(1)对称性）。基频从 γ=0 增至 γ=1、再从 γ=1 减至 γ=3（遵循反常 Hall 电流 ∝ 节点间距，2k₀=2 arccos(γ−2)，Chern 数切片 Cₓ(|kₓ|<k₀)=−1；|γ|<1 时两对节点贡献 Cₓ=2，基频上升快一倍）；而高次谐波在 |γ|=1 和 |γ|=3 出现明显的峰，γ=3 的峰高于 γ=1，源于对称参数选择下三个 semi-Dirac 点共存（若跳跃参数不等，γ=1 处的峰会劈裂）。
  3. **节点合并的微观机制**。利用镜像对称 J_y(kₓ)=J_y(−kₓ)：Weyl 节点靠近 Γ 点（γ→3）时，(1) Γ 附近非线性色散区激发密度增大且无抵消项，反常电流增大；(2) 非线性区收缩先使强度下降，随后外部区域（kₓ>k₀）贡献主导又使强度回升——解释 Fig. 4 中 γ≈2.9 附近的 dip；极限 γ→3 时仅 kₓ>k₀→0 的外区贡献，且因单节点 J_y(qₓ=0)=0 有 J_y(kₓ=0)→0，semi-Dirac 点处附加约束 J_y(kₓ=0)=0。γ>3 后 kₓ=0 附近区域重新贡献，但带隙增宽使激发密度快速下降，总响应回落。
  4. **AHHG 不能用 Berry 曲率单独解释**。对响应做贡献分解：Berry 曲率贡献与带间贡献量级相当，且高次谐波仅由 Weyl/semi-Dirac 点附近的激发（N_c）与带间极化（ρ_vc）产生，无法用 Cₓ(kₓ)（Chern 数切片）表达。
  5. **驱动参数依赖**（SM S3）：小 ω₀、E₀ 时三次谐波仅在两个 semi-Dirac regime（γ=1、3）附近尖峰，中间 Weyl regime 被抑制；增大 E₀ 响应整体增强（关联激发密度，直至饱和 N_c=0.5，带间区域贡献变显著、well-separated 判据弱化，γ=2 附近的 WSM regime 响应也上升）；增大 ω₀ 响应幅度下降且 γ 依赖变平缓（共振条件 ℏω_cv=nℏω₀ 偏离节点、跃迁偶极 d_vc 下降、对低能细节不敏感）。ω₀=0.2 eV 时三、五次谐波贡献高度定域于 Weyl 节点附近，ω₀=0.8 eV 时远离开节点处也有贡献。
  6. **半填充与掺杂**：费米面在 Weyl 点时结果成立；小掺杂不改变结论（双带同空或同满的动量区域不贡献电流）；大掺杂会使 Fig. 4 的峰减弱（kₓ=0 附近区域停止贡献）。

  ## 潜在研究方向

  - 对真实材料做现实计算：SrNbO₃（非对称对称保护的 semi-Dirac 点在 BZ 边界，加外磁场可产生 Weyl 节点对——值得研究）和 ZrTe₆（ZrTe₅）体系；需处理这类材料中的四重简并。
  - 2D 材料中类似效应：如黑磷（black phosphorus），其临界点具有二次-线性混合色散。
  - TRS 破缺模型中过倾斜（over-tilted）type-II Weyl 锥对 AHHG 的影响，留作后续研究。
  - 本文结论与同期多 Weyl 体系工作（强调导带占据的作用）互补；两者统一图像（占据 vs 色散非线性）的权重尚未厘清。
  - 局限：简化晶格模型、单参数 γ 控制相变、对称参数选择使 γ=1 处三峰合并（非对称跳跃下劈裂，实际材料中可能已分离）；大 ω₀ 下 well-separated 判据失效后需要重新审视机制分类。

  ## 与林赛研究的关联

  - **HHG 作为拓扑材料表征**：本文给出一套明确的"谐波强度-γ 剖面"判据（semi-Dirac 峰 vs Weyl 抑制），可直接嫁接到我们 HHG/阿秒方向里"强场驱动谱学读出拓扑态"的实验方案设计——特别是横向电流几何（垂直于偏振与节点分离方向）这一测量构型，与我们交变磁（altermagnet）/Weyl 体系中反对称磁输运的测量逻辑同构。
  - **量子几何的角色澄清**：Berry 曲率贡献与带间贡献量级相当、AHHG 源于色散非线性而非几何量本身——这个结论是我们写申请书论证"需要含动量耦合的实时间 SBE 动力学而非静态几何响应理论"的关键引证，可挂入 general-ssh-weyl-20260920 课题的方法学依据部分。
  - **机制可迁移性**：C2z 对称→贡献抵消→"偏离理想极限即信号"的论证框架，与我们莫尔体系中平带 HHG（偏离平带即信号）和交变磁体系中动量依赖自旋劈裂的谐波指纹分析高度同构，可作为我们理论分析的对照模板。
  - **实验接口**：驱动参数 ℏω₀=0.2 eV（中红外）、E₀=0.043 V/Å、τ=40 fs、T₂=3 fs 落在常规强场超快实验可达区间；ZrTe₅（含 6 meV 能隙的 semi-Dirac 候选）是现实可测体系，可作为我们课题中材料筛选的具体对象。
  - **与莫尔方向对话**：semi-Dirac 色散（一个方向抛物线、两维锥形）与莫尔魔角附近"平带+狄拉克锥"混合色散在数学结构上相似，其色散非线性驱动的谐波增强机制可能对莫尔体系平带-锥交叉区的 HHG 预测有借鉴意义。

  ## 来源
  - 蒸馏自全文（deep-read）


## 合并自「High-harmonic generation in semi-Dirac and Weyl semimetals with broken time-reversal symmetry: Exploring merging of Weyl nodes」

## 阅读笔记

### general-ssh-weyl-20260920

信息已经足够完整。现在我整理结构化笔记。

## 调研主题
来源：[arXiv:2402.12899 — High-harmonic generation in semi-Dirac and Weyl semimetals with broken time-reversal symmetry: Exploring merging of Weyl nodes](https://arxiv.org/html/2402.12899v1)（Medic et al., Jožef Stefan Institute, Slovenia; 期刊 Phys. Rev. B 109, 205130 (2024)）

---

## 研究问题（Research Question）

论文聚焦的核心问题是：**在破缺时间反演对称性（TRS）的 Weyl 半金属（WSM）中，异常高次谐波（AHHG，电流方向垂直于电场极化方向）究竟由什么物理机制主导？特别是当一对 Weyl 节点逐渐靠近并最终合并为半 Dirac（semi-Dirac）节点时，异常高次谐波的强度与偏振依赖性如何演化？**

作者明确指出：在已有的 WSM HHG 文献中，存在两种相互竞争但难以分辨的图像——一种强调"良分离 Weyl 节点"贡献主导，节点分离越大 AHHG 越强（Avetissian et al. 2022）；另一种强调能带偏离严格线性色散（非线性区）的贡献（Bharti, Mrudul, Dixit 2022）。本研究试图通过扫描一个最小模型中可调参数 γ（控制 Weyl 节点距离）来**解开这两种贡献**，并考察 Weyl 节点合并为半 Dirac 点这一拓扑相变附近的谐波响应。

具体研究问题可拆为三点：(i) AHHG 在良分离 Weyl 节点的线性色散极限下是否真的为零？(ii) 半 Dirac 区的 AHHG 是否显著增强（能否作为实验判据）？(iii) Weyl 锥的倾斜（type-II）对 AHHG 有何影响？

---

## 研究背景（Background）

- **AHHG 在拓扑材料中的兴起**：固体 HHG 自 Ghimire 等 2011 年 ZnO 实验以来成为研究凝聚态电子结构与关联的强有力探针。AHHG（异常电流分量 J⊥E）是揭示 Berry 曲率与拓扑性质的关键观测量。
- **前期工作**：Silva et al. (Nat. Photon. 2019)、Luu & Wörner (Nat. Commun. 2018, 9, 916) 等提出 AHHG 可探测 Berry 曲率；Liu et al. (Nat. Phys. 2017) 在 WTe₂ 中实验观测到反常谐波；Yue & Gaarde (PRL 130, 166903, 2023) 指出 Berry 曲率对 AHHG 的贡献在不同驱动频率下未必主导。
- **Weyl 与 Dirac 半金属的色散差异**：Weyl 节点处 Berry 曲率发散，理论上预期 AHHG 增强；然而 Bharti & Dixit (PRB 107, 224308, 2023) 在 multi-Weyl 系统中发现 AHHG 增强由导带布居数决定，与"Berry 曲率主导"图像冲突。
- **半 Dirac 半金属**：两对 Weyl 节点合并会形成"沿分离方向抛物线、垂直平面线性锥"的混合色散。SrNbO₃（由非对称对称性保护）、ZrTe₅（有 ~6 meV 微小能隙）是已知的候选材料。
- **研究动机**：作者认为 WSM 中 AHHG 的物理图像"qualitatively poor"，需要在一个可解析的最小模型中清晰区分"well-separated nodes"贡献与"non-linearity of dispersion"贡献。

---

## 研究方法（Methods）

- **模型**：采用最小三维格点模型 H(k) = d(k)·σ，dₓ(k) = t cos(akₓ) + t cos(bk_y) + t cos(ck_z) − γ, d_y(k) = t sin(bk_y), d_z(k) = t sin(ck_z)，取 t=1 eV、a=b=c=1 Å 的对称简化。该模型具有正交对称性、**破缺 TRS 但保留反演对称（IS）与镜像对称**。
- **相图扫描**：通过调节参数 γ，可系统遍历三个相——(i) |γ|>3 平凡绝缘体；(ii) 1<|γ|<3 单对 Weyl 节点；(iii) |γ|<1 双对 Weyl 节点；(iv) |γ|=1（三个 semi-Dirac 点）与 |γ|=3（一个 semi-Dirac 点）的临界拓扑相变。
- **方法学**：用半导体 Bloch 方程（SBE）在 Houston 基底下求解密度矩阵演化；T₂ = 3 fs 有效退相干时间；Brilouin 区60³ 离散化。
- **激光参数**：ℏω₀ = 0.2 eV（中红外），E₀ = 0.043 V/Å，τ = 40 fs 高斯包络，总持续 T = 790 fs；偏振 ē = ê_z。
- **分析工具**：(1) Larmor 公式 I(ω) = ω²|J(ω)|² 提取辐射谱；(2) 滤波提取特定谐波的时序 Jᵞᵠ(t)；(3) 在 ky–kz 平面切片累加以分辨节点贡献的 k 空间来源；(4) 与 Weyl 节点附近线性化连续模型做对照验证。
- **评估对象**：异常分量 Iᵧ（垂直于电场与节点分离方向），重点关注奇次谐波（偶次因 IS 消失）。

---

## 主要发现与核心结论（Main Results）

1. **AHHG 在良分离 Weyl 节点下消失**：在每个 Weyl 节点附近做 Taylor 展开后，对该节点存在 C₂z 旋转对称 σ_z H(−q_x,−q_y,q_z) σ_z = H(q_x,q_y,q_z)，由此推出 Jᵧ(q) = −Jᵧ(−q)，使良分离极限下线性化区贡献严格对消。因此 **WSM 中 AHHG 仅源于偏离严格线性色散的 k 空间区域**（这是本文最核心结论）。该结论与 Avetissian et al. (2022) 的观点存在分歧，论文在 SM S6 给出消歧论证。

2. **半 Dirac 区 AHHG 显著增强**：图4 显示 |γ|=1（三 semi-Dirac 点）和 |γ|=3（一 semi-Dirac 点）处出现高次谐波（ω=3ω₀ 及以上）的尖锐峰，强度比 WSM 内部（γ=2）高数个量级。半 Dirac 沿节点分离方向是抛物线色散，Berry曲率与态密度在合并点附近集中，激发与带间极化同时增强，使 AHHG 远高于纯 WSM。γ=3 峰值高于 γ=1 峰值的原因是当前模型 t_x=t_y=t_z 对称选取下三 semi-Dirac 点共存。

3. **第一谐波 vs 高次谐波呈现相反行为**：第一谐波 Iᵧ(ω₀) 在 |γ| 由 0→1 单调上升、由 1→3 单调下降，由线性 intra-band 反常霍尔电流 ∝ Weyl 节点分离（= 2 arccos(γ−2)）解释；而高次谐波则在 |γ|=1, 3 处出现双峰结构，并在 γ≈2.9 处存在一个 dip（图 4）。Dip 的物理起源是：当 Weyl 节点接近 Γ 点时，Γ 附近非线性色散且有激发的 k 体积先增大后缩小——这是从节点合并图像导出的细致图景。

4. **拓扑保护的 IS 选择定则**：因保留反演对称，所有偶次谐波严格为零，仅剩奇次谐波 Iᵧ(ω=(2n+1)ω₀)。

5. **与多 Weyl 系统的互补视角**：作者将其结果与 Bharti & Dixit (PRB 107, 224308, 2023) 的 multi-Weyl AHHG 工作并列——后者强调导带布居数，前者强调"偏离严格线性"——两者共同指向：WSM AHHG **不是** Berry 曲率单独主导。

6. **倾斜 Weyl 锥的影响（SM S5）**：在 type-I 倾斜范围内结论仍成立；type-II 过倾斜的情形留作未来工作。

---

## 潜在研究方向（Future Directions）

- **真实材料计算**：作者明确建议对 SrNbO₃ 与 ZrTe₅ 进行第一性原理带结构基础上的 realistic 计算，特别是 SrNbO₃ 的 semi-Dirac 点受非对称对称性保护，外加磁场可生成 Weyl 节点对，是检验本预言的理想平台。
- **四重简并的扩展**：semi-Dirac 材料的四重简并要求将模型推广到 4 带，这是本工作当前未涵盖的。
- **二维类比体系**：黑磷等具有"混合抛物-线性"色散的 2D 材料可作为 2D 版图的对应检验。
- **过倾斜 type-II Weyl 锥的 AHHG**：本文仅在 type-I 倾斜下论证，type-II（含"倾倒"色散）的反常谐波响应仍是开放问题。
- **高掺杂下的破坏**：本结果适用于半填充与轻掺杂；高掺杂会湮灭图 4 中的谐波增强峰，因为 k_x≈0 区不再贡献 AHHG（SM S3）。
- **3D Dirac vs semi-Dirac 实验区分**：作者提出 AHHG 增强可作为实验区分 3D Dirac 和半 Dirac 相的非接触光学探针，但需在真实材料上完成实验对照。
- **多体修正**：当前为单粒子 SBE + 有效退相干时间（T₂=3 fs），未包含电子-电子关联与多体散射对谐波产率的影响——尤其在半 Dirac 区拓扑边界附近，关联效应可能改写预言。
- **开放争议**：与 Avetissian et al. (PRA 106, 033107, 2022) 关于 WSM 中 AHHG 与节点分离关系的结论存在分歧，作者在 SM S6 给出论证但未完全消解；该分歧暗示可能存在模型/参数依赖性，需更多独立工作验证。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：semi-Dirac/Weyl 半金属 HHG 的最小晶格模型 + Houston 基 SBE 模拟

**原理**：最小 3D 两能带晶格哈密顿量 H(k)=d(k)·σ（dₓ=t cos ak_x+t cos bk_y+t cos ck_z−γ 等，对称取 tₓ=t_y=t_z、a=b=c）：破缺 TRS 保留反演与镜像对称，γ 扫描遍历相图（|γ|>3 平庸绝缘体 / 1<|γ|<3 一对 Weyl / |γ|<1 两对 Weyl / |γ|=1,3 临界 semi-Dirac，半 Dirac 点位于 TRIM）；Houston 基 SBE 求密度矩阵（含 T₂，初态满价带），电流=速度矩阵元加权密度矩阵和，辐射谱 Larmor 公式 I(ω)=ω²|J(ω)|²；宽度 2δω=ω₀ 滤波器提取各阶谐波时序；ky–kz 切片累加分辨节点贡献，与 Γ 点/Weyl 节点线性化连续模型对照。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 数值参数 | a=1 Å、t=1 eV；ℏω₀=0.2 eV；E₀=0.043 V/Å；τ=40 fs 高斯包络；T=790 fs；T₂=3 fs；BZ 60³ 离散 | §数值参数 |
| 相图 | |γ|>3 平庸；1<|γ|<3 一对 Weyl；|γ|<1 两对 Weyl；|γ|=1（三个 semi-Dirac 点）与 |γ|=3（一个）临界 | §相图 |

**适用边界**：T₂=3 fs 沿用文献选择（退相干机制唯象）；对称简化模型（tₓ=t_y=t_z）非真实材料参数；偶次谐波因反演对称消失（评估限奇次）。
**代表作**：本文（arXiv:2402.12899）；T₂ 选择沿用 Phys. Rev. B 105, 155140 (2022)
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[2402.12899]]
- [[Berry 曲率]]
- [[Berry曲率]]
- [[High-harmonic generation in semi-Dirac and Weyl semimetals with broken time-reversal symmetry: Exploring merging of Weyl nodes]]
- [[Weyl semimetal]]
- [[general-ssh-weyl-20260920]]
- [[交变磁体]]
- [[固体HHG]]
- [[强场超快]]
- [[强场驱动]]
- [[自旋劈裂]]
- [[量子几何]]
<!-- /linsai-wikilinks -->
