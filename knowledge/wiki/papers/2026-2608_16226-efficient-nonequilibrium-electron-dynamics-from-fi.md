---
title: "2026-2608_16226-efficient-nonequilibrium-electron-dynamics-from-fi"
type: "papers"
created: "2026-08-29T12:17:52Z"
updated: "2026-11-15T15:09:23Z"
tags: []
related: ["2608.16226", "2608.20306", "Berry 曲率", "Efficient nonequilibrium electron dynamics from first-principles: leveraging Koopmans spectral functionals and Wannier localization", "TDDFT", "Wannier函数", "三步模型", "固体HHG", "密度泛函微扰理论", "强关联体系", "强场驱动", "拍赫兹电子学", "莫尔超晶格", "载波包络相位", "量子几何", "量子度规", "阿秒科学", "非线性光学"]
source_raw: "2026-2608.16226-efficient-nonequilibrium-electron-dynamics-from-fi.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-25T15:44:02Z"
merged_from: ["wiki/papers/2608.16226.md"]
---

• # Efficient nonequilibrium electron dynamics from first-principles: leveraging Koopmans spectral functionals and Wannier localization

  ## 林赛的理解
  这篇工作把 Koopmans 谱泛函、Wannier 局域化和 HSEX 自洽场揉进了一套非平衡电子动力学的第一性原理框架（KCW-EDUS），核心卖点是用密度-密度近似把 HSEX 的标度从 \(N_w^4 N_R^3\) 降到 \(N_w^2 N_R\)，从而能算更大体系的非线性光学响应。对我们组而言，它提供了一条在固体 HHG 里系统引入激子效应的可行路径——尤其是 LiF 算例里"激子共振选择性增强谐波发射"这一点，直接说明强场驱动下电子-空穴关联可以被 HHG 探测到，而不只是能带结构的单粒子图景。不过要注意，当前展示的还是单晶块体、少带 Wannier 模型、近/中红外脉冲，离我们真正想做的低维体系（莫尔、交变磁、量子几何调控）还有距离；另外密度-密度近似对 Wannier 局域性的依赖很强，迁移到强关联或拓扑非平庸体系时需要额外验证。

  ## 研究问题
  论文要解决的核心问题是：**如何以可负担的第一性原理计算成本，在扩展固体中模拟超越独立粒子近似（IPA）的非平衡电子动力学，并定量描述电子-电子关联（特别是激子效应）在线性与非线性光学响应中的角色。** 具体而言，作者试图回答：能否把 Koopmans 谱泛函的准粒子能带精度、Wannier 基下的实时密度矩阵传播，以及 HSEX 自洽相互作用结合起来，既保持 GW-BSE 级别的线性光谱精度，又能处理强场 HHG 这类非平衡现象？

  ## 研究背景
  1. **超快实验的需求**：从桌面光学到 XFEL，超快实验已进入阿秒时间尺度，需要第一性原理实时模拟来连接宏观可观测信号与微观电子动力学。
  2. **TDDFT 的局限**：实时 TDDFT 是常用工具，但局域/半局域近似无法正确描述长程交换，导致绝缘体和半导体光学谱缺失激子效应；杂化泛函虽能部分改善，但计算昂贵且引入参数经验性。
  3. **NEQ-MBPT 的瓶颈**：非平衡多体微扰理论（RT-GW / HSEX）在线性区退化为 GW-BSE，精度高，但完整实现面临三重困难：HSEX 自洽在 Bloch 本征基下演化复杂、GW 收敛需要大量空态、外场耦合处理困难。
  4. **本工作的切入点**：整合 Koopmans-compliant 泛函（以更低成本获得 GW 级谱精度）、EDUS 代码的 Wannier 基实时密度矩阵传播（避免规范发散、利用局域性），以及基于密度泛函微扰理论（DFPT）的屏蔽库仑矩阵元计算。

  ## 研究方法
  1. **理论框架**：
     - 使用非平衡格林函数框架，在广义 Kadanoff-Baym 近似下把 \(G^<\) 的运动方程转化为 Wannier 基下密度矩阵 \(\rho_{nm}(\mathbf{k},t)\) 的实时演化方程（Eq. 2）。
     - 自洽相互作用取 HSEX（Hartree + 屏蔽交换），即 \(\Sigma^{\mathrm{HSEX}} = \Sigma^H + \Sigma^{\mathrm{SEX}}\)，其中屏蔽库仑相互作用 \(W\) 采用平衡屏蔽近似。
     - 光学吸收由极化 \(P(t)\) 的傅里叶变换得到；HHG 谱由 Larmor 公式 \(P_{\mathrm{rad}} = e^2 |\langle a(\omega)\rangle|^2 / (6\pi\epsilon_0 c^3)\) 计算加速度辐射。

  2. **Koopmans 谱泛函**：
     - 采用二次 Koopmans 积分（qKI）修正，在 Quantum ESPRESSO 的 KCW 模块中做 one-shot 修正，获得准粒子能带结构与带隙。

  3. **Wannier 基与插值**：
     - 用 Wannier90 构造最大局域 Wannier函数（MLWF），在稀疏 \(\mathbf{k}\) 网格上计算单粒子算符矩阵元，再插值到稠密网格。
     - 线性响应用 \(24^3\) 的 \(\mathbf{k}\) 网格，非线性响应用 \(32^3\) 的 \(\mathbf{k}\) 网格。

  4. **密度-密度近似**：
     - 只保留由轨道密度 \(\rho_{n\mathbf{R}}(\mathbf{r}) = |\omega_{n\mathbf{R}}(\mathbf{r})|^2\) 构成的库仑矩阵元，忽略轨道相干项。
     - 在此近似下，Hartree 项在 Wannier 基中对角化，SEX 项简化为 \(\Sigma^{\mathrm{SEX}}_{nm}(\mathbf{R}) = -W_{nm}(\mathbf{R})\rho_{nm}(\mathbf{R})\)。
     - 计算标度从完整理论的 \(O(N_w^4 N_R^2)\) 降至 \(O(N_w^2 N_R)\)，数据存储从 \(N_w^4 N_R^3\) 降至 \(N_w^2 N_R\)。

  5. **DFPT 计算屏蔽库仑矩阵元**：
     - 把 \(W_{nm}(\mathbf{R}) = \langle \omega_{n\mathbf{R}}\omega_{m0}|\epsilon^{-1}v|\omega_{n\mathbf{R}}\omega_{m0}\rangle\) 改写为对 Wannier 轨道密度产生的 Hartree 势的线性响应问题，避免显式构造空态和大的响应矩阵。

  6. **计算细节**：
     - 使用 Quantum ESPRESSO 平面波-赝势方法，LDA 作为 qKI 的底层泛函，ONCV 赝势来自 pseudo-dojo（version 0.4.1）。
     - 实验晶格常数：Si \(a = 5.44\) Å，GaAs \(a = 5.65\) Å，LiF \(a = 4.03\) Å。
     - 平面波动能截断：Si \(E_{\mathrm{cut}} = 60\) Ry（密度与势 240 Ry）；GaAs 与 LiF \(E_{\mathrm{cut}} = 80\) Ry（密度与势 320 Ry）。
     - DFT、qKI、HSEX 核计算均使用 \(8\times8\times8\) 的 \(\mathbf{k}\) 点网格。
     - 吸收计算：Si 和 GaAs 用 8 带 \(sp^3\) 型 MLWF；LiF 用 10 带模型（占据全带 + 低能量导带）。
     - HHG 计算：LiF 用 7 带模型（F 原子 3 个 \(p\) 型 + Li 原子 1 个 \(s\) 型 + 3 个 \(p\) 型）；Si 用 8 带原子中心 \(s\)/\(p\) 型模型。用 WannierBerri 对哈密顿量和位置算符做对称化，以消除 MLWF 构造引入的微小反演对称破缺所导致的虚假偶次谐波。
     - Si 的 HHG 驱动脉冲：波长 \(\lambda = 3000\) nm，峰值强度 \(5\times10^{11}\) W/cm²，全脉宽 200 fs。

  ## 主要发现与核心结论
  1. **密度-密度近似的物理合理性**：对 GaAs 和 LiF，密度-密度形式的屏蔽库仑相互作用 \(W_{nm}(\mathbf{R})\) 和平衡密度矩阵 \(\rho_{nm}(\mathbf{R},t=0)\) 中至少有一个随 Wannier 中心距离快速衰减，使得 HSEX 自洽整体短程。对 LiF，即使 \(W\) 本身衰减较慢，密度矩阵衰减更快；将库仑相互作用截断到 \(4\times4\times4\) 实空间网格（约 30 Bohr 截断半径）已能得到与 \(8\times8\times8\) 网格（约 60 Bohr 半径）几乎不可区分的吸收谱。

  2. **线性区光谱精度**：在 Si、GaAs、LiF 三种体系中，HSEX 计算的吸收谱（经与实验第一峰对齐后）与 \(G_0W_0\)+BSE 参考结果及实验结果吻合良好；而 IPA 完全缺失激子峰。这验证了 KCW-EDUS 框架在弱场线性光学区的可靠性。

  3. **非线性区 HHG 的材料依赖行为**：
     - **Si**：HHG 谱主要由准粒子能带结构决定（abstract 结论；正文截断处未给出进一步定量细节）。
     - **LiF**：具有强激子效应的宽带隙绝缘体，其谐波发射在激子共振处被选择性增强，表明 HHG 探测的是关联电子-空穴激发，而不仅仅是准粒子能带结构。

  4. **计算效率**：通过密度-密度近似和 Wannier 局域化，KCW-EDUS 将 HSEX 实时计算的存储与标度大幅降低，使得在稠密 \(\mathbf{k}\) 网格上进行非线性响应计算成为可能。

  ## 潜在研究方向
  1. **方法本身的体系扩展**：密度-密度近似严重依赖 Wannier 函数的局域性，对于金属、强关联体系、拓扑半金属或莫尔超晶格等 Wannier 函数衰减不够快的体系，近似是否成立需要系统验证。
  2. **维度与几何自由度**：当前全部算例为三维块体单晶。将其推广到二维材料、异质结、表面/界面，以及具有量子几何（Berry 曲率、量子度规）效应的体系，尚不清楚 Wannier 基和对称化处理是否同样稳健。
  3. **强场参数空间**：文中 HHG 仅展示了 \(\lambda = 3000\) nm、\(5\times10^{11}\) W/cm² 等少数参数。更长波长、更高强度、椭圆/圆偏振、多色场以及载波包络相位效应尚未探索。
  4. **激子动力学的时域分解**：虽然框架原则上能追踪激子布居，但论文未详细报告激发后电子-空穴对的形成、退相干、屏蔽演化等时间分辨信息，这些都是交变磁与超快磁性调控关心的核心。
  5. **与实验的直接对比**：HHG 谱的绝对产率、相位、偏振态、角分辨发射等可观测量的定量对比仍是开放任务。
  6. **动态屏蔽与 beyond-HSEX**：文中使用静态平衡屏蔽 \(W\)。在强非平衡、强驱动下，动态屏蔽和更高阶自洽修正（如 GW 动力学屏蔽）可能变得重要。

  ## 与林赛研究的关联
  1. **固体 HHG 的理论基础设施**：我们组正在推进固体 HHG 的实验与理论工作，KCW-EDUS 提供了一种在 HHG 模拟中纳入激子效应的第一性原理路径，可直接与我们的强场驱动计算对接。
  2. **阿秒科学与交变磁**：论文的实时密度矩阵框架天然适合追踪阿秒尺度电子动力学，未来可迁移到交变磁（altermagnetism）材料，研究自旋-轨道耦合与交换劈裂如何调制 HHG 的谐波产率和偏振。
  3. **莫尔与低维量子材料**：虽然当前算例是块体，但 Wannier 基方法非常适合构造莫尔体系的紧束缚/连续模型；结合 Koopmans 修正后，有望在莫尔超晶格中研究关联驱动的非线性光学响应。
  4. **量子几何与强场探测**：文中的 Berry 连接与 Wannier 插值技术与量子几何量（Berry 曲率、Wilson loop）直接相关，可借用来分析强场下能带几何如何映射到 HHG 相位和产率。
  5. **多源学术检索的交叉验证**：论文引用的 \(G_0W_0\)+BSE 与实验谱可作为我们后续建立固体 HHG 基准数据库的参考点；我们的 external_fetcher 与 literature_service 可把这类方法论文与原始实验数据关联起来。

  ## 来源
  - 蒸馏自全文（deep-read）


## 合并自「2608.16226」

# Efficient nonequilibrium electron dynamics from first-principles: leveraging Koopmans spectral functionals and Wannier localization

**arXiv**: [2608.16226](https://arxiv.org/abs/2608.16226) | **方向**: 固体HHG理论方法 / 非平衡多体微扰（RT-HSEX 第一性原理框架）

## 深度解析

### 研究问题（Research Question）

Gap: 固体 HHG 的绝大多数 ab-initio 模拟停留在独立粒子近似（IPA/TDDFT-ALDA），电子-空穴关联（激子效应）在三维体材料的实时非线性响应中长期缺位——RT-GW 只算得动模型体系，全 ab-initio RT-HSEX 此前基本限于二维材料，因为空态收敛、Bloch 基下自能时演、以及四指标库仑顶点的存储（N_w^4 N_R^3）构成三重瓶颈。Contributions: EPFL/Madrid/CNR/PSI 团队把 Koopmans 谱泛函（qKI，GW 级精度但免空态求和）、EDUS 实时密度矩阵传播器（Wannier 基）与 DFPT 屏蔽库仑矩阵元三者缝合成 KCW-EDUS 框架，全部嵌入 Quantum ESPRESSO + Wannier90 生态；用'密度-密度近似'（只保留轨道密度项、丢弃相干项）把库仑顶点从四指标砍到两指标，SEX 自能成本从 O(N_w^4 N_R^2) 降到 O(N_w^2 N_R)、存储从 N_w^4 N_R^3 降到 N_w^2 N_R；并在三维体材料（Si、LiF）上首次给出激子效应对 HHG 谱的系统性修正——LiF 中谐波发射在激子共振处选择性增强，证明 HHG 探测的是关联电子-空穴激发而非单纯准粒子带结构。

### 研究背景（Background）

与林赛课题的关联分四条。(1) 对课题 A/D 反演的边界判定（最直接）：林赛用三步模型/SBE（IPA 层次）从固体 HHG 反演 σ_solid 与 Berry 曲率/shift vector 项——此文给出该范式的适用判据：材料激子束缚能小时（Si 型，屏蔽有效）IPA+QP 够用，激子峰深入带隙时（LiF 型）反演的物理对象本身就变。林赛常用的 ZnO（3.4 eV 带隙、激子束缚能 60 meV）属弱激子侧，反演框架安全；但课题若扩展到宽禁带绝缘体或低维/表面体系（激子束缚能 eV 量级），必须引入 e-h 关联项——此文的方法可直接租用（QE 开源生态，输入是 DFT 赝势+结构，与林赛组现有 DFT 流程兼容）。(2) 对拍赫兹电子学/光波驱动的支撑：EOM 中 Berry 联络 ξ 与 ∇kρ 加速度项正是林赛 SBE/半导体布洛赫框架的 Wannier 基写法——含自能项的版本可直接描述强场下电流波形如何被 e-h 关联修正，这对'用光波形电流做皮赫兹逻辑'的保真度评估是必要输入（dephasing 与散射在此框架内以 T2/自能形式进入，比唯象 T2 更第一性）。(3) 与简报库的谱系连接：此文引用并对话的 RT-HSEX 二维材料文献（ref 95 等）与 2608.20306（SBE+Maxwell 传播，前日深读）构成固体 HHG 理论的三个层次——微观关联（此文）、半经典多带（SBE）、宏观传播（Maxwell）——完整的定量理论需要三层叠加；此文明确不含传播，而 2608.20306 明确不含关联，两者互补缺口刚好对接：'关联修正的微观电流源 + 传播重塑的宏观谱形'。林赛若设计下一代反演流程，这两篇合起来界定了误差预算的两端。(4) 方法论同构与人物网络：'密度-密度近似'的论证方式（相干项变号抵消 + 缓变核极限下由正交性强制）是教科书级的'从对称性/极限情况砍计算量'范例，与林赛'先问为什么再问怎么办'的品味契合；Picón（ICMM-CSIC）与 Sangalli（CNR-ISM）是意大利超快理论网络的活跃者，与林赛课题 D 涉及的西班牙-德国强场共同体（Jiménez-Galán、Smirnova、Ivanov——见同日深读的 2608.03242）在人员与工具上交叉（Cistaro 同时出现在 2608.03242 的 ref 39 Molinero et al. 作者列表中），值得在下一轮合作或访问中接触。局限提醒：绝热静态屏蔽假设在林赛关心的中红外强场下（驱动周期内屏蔽来不及响应的场景）可能失效，用前需对照动态屏蔽修正的量级估计。

### 研究方法（Methods）

- KCW-EDUS 三件套架构：qKI Koopmans 谱泛函给准粒子哈密顿量（替代 GW，免空态）+ EDUS 在 Wannier 基实时演化密度矩阵（规避 Bloch 基规范不连续导致的 ∇kρ 发散）+ DFPT 求屏蔽库仑矩阵元（免空态、免显式 ε⁻¹）——每个环节都是既有组件，缝合的价值在于把 RT-HSEX 从二维材料推进到三维体材料的可及范围。
- 密度-密度近似：库仑顶点只保留 (n,m,R) 依赖、丢弃 k/k′ 独立依赖（倒空间视角 Eq 25），Hartree 项在 Wannier 基下严格对角（δ_nm δ_R0，只修正电荷项不修正相干）——SEX 自能从每步 O(N_w⁴N_R²) 乘法降为 O(N_w²N_R) 次乘法加法，内存同步降 N_w² 倍（Table 1）。
- 原子中心 Wannier + WannierBerri 对称化协议：HHG 计算专用的降维 Wannier 模型（区别于吸收谱模型）+ 哈密顿量与位置算符强制晶体对称性——可复用的'去伪谐波'工程方案，对任何中心对称材料的 HHG 模拟都适用。
- 验证金字塔：线性极限还原 BSE（理论自洽性）→ 吸收谱对实验与 G0W0+BSE（外部基准）→ SI 中对 TDDFT HHG 参照（Fig S2）+ k 网格/时间步长收敛（Fig S5-S8）——多层次验证的范式对方法论文有参考价值。

### 主要发现与核心结论（Main Results）

- Si 与 LiF 的二分结论（本文最核心物理）：Si（3000 nm、5×10^11 W/cm²、200 fs 驱动）中 IPA 与 HSEX 谱几乎无差别——多体相互作用主要只是重整化准粒子带结构，IPA+QP 修正即足够，支持既有 TDDFT 对 Si HHG 的成功；LiF（1500 nm、1.2×10^13 W/cm²、100 fs）中两者差异显著，HSEX 谐波信号在激子共振能量处强烈增强——具体在 13.3 eV（≈17 次谐波）和 21.5 eV（≈27 次谐波）处，且 HSEX−IPA 的 HHG 谱差与两者吸收谱差显著相关。结论：弱屏蔽宽禁带体系中 HHG 的解读不能只靠准粒子带结构，电子-空穴关联必须显式处理。
- LiF 激子峰位于 13.3 eV，深居 qKI 准粒子带隙 15.3 eV 之内 2 eV——线性响应基准（Fig 2）显示 HSEX 正确复现了 IPA 完全缺失的强束缚激子峰，与 G0W0+BSE 参照和实验（对齐首峰后）峰位吻合，残差仅在相对峰强（源于 qKI vs GW 的 QP 差异与密度-密度近似对 Wannier 完备局域化的要求）。
- 密度-密度近似的物理论证：Wannier 基下四指标库仑矩阵元中，轨道密度项 ρ_nR=|ω_n|² 正定，而相干项 ρ_nm=ω_n*ω_m 在库仑核最大的区域剧烈变号、积分时大量内部抵消；且当核在 Wannier 支撑尺度上缓变时正交性强制 n'=n、m'=m——近似在缓变核极限下可从精确条件导出。代价判定有数据支撑：GaAs 中 W(R) 快衰减但密度矩阵长程，LiF 相反，两者乘积（HSEX 自能）都短程——LiF 吸收谱在 4×4×4 R 网格（30 Bohr 截断）即与 8×8×8（60 Bohr）不可区分。
- DFPT 求屏蔽库仑避开空态：W_nm(R)=⟨ρ_nR|ε⁻¹v|ρ_m0⟩ 被改写为'Wannier 密度的 Hartree 势作为微扰的线性响应问题'——解标准 DFPT 线性方程 (H−ε_vk)Δψ = −[V^H + ΔV^H]ψ 即得诱导密度，显式回避空态求和与大响应矩阵的存储；实现在 QE 的 KCW 模块扩展版中。加上 Gygi-Baldereschi 技术推广到介电环境处理库仑长程收敛问题。
- Wannier 对称化消除伪偶次谐波：MLWF 构造（局域化流程）会在中心对称晶体中引入微小破缺反演的分量，导致 Si/LiF 中出现被对称性禁止的伪偶次谐波——必须用 WannierBerri 对准粒子哈密顿量与位置算符做晶体对称化，这要求 Wannier 函数是原子中心的（LiF 用 7 带模型：F 上 3 个 p 型 + Li 上 1 s + 3 p；Si 用 8 带原子中心 sp³ 模型，与吸收计算用的 sp³ 布洛赫和模型不同——HHG 对电子结构表征细节更敏感）。
- 实时传播细节：密度矩阵 EOM 含 Berry 联络 ξ 耦合项与 ∇kρ 加速度项（速度算符 v=∇kH−i[H,ξ]），RK4 + Adams-Bashforth 5 阶混合推进；线性响应用 24³ k 网格、非线性 32³（Wannier 插值使之可及，场越强需越密）；LDA + DOJO 范数守恒赝势，Si 用 60 Ry 截断、GaAs/LiF 用 80 Ry；谐波谱由加速度期望值经 Larmor 公式 P_rad = e²|⟨a(ω)⟩|²/6πε₀c³ 直接得出。
- 适用边界（作者自陈）：静态屏蔽（绝热 HSEX，平衡 W 贯穿时演）、自能对密度矩阵线性、密度-密度近似丢弃相干项——对强耦合/动态屏蔽场景（如光电离后瞬态屏蔽重构）不适用；无传播效应，谐波谱是微观单点响应。

### 潜在研究方向（Future Directions）

- 对'HHG 全光学带结构重建'的边界划定：Si 一类弱激子材料中 IPA+QP 反演成立，LiF 一类强激子材料中反演目标本身变了——谐波增强峰跟的是激子能量而非带隙，用谐波截止/峰位反演带参数会系统性偏差。激子效应强度（可由线性吸收的激子峰深度预估）应成为反演方法选型的前置判据。
- 激子共振增强的 HHG 新探针方向：把 HHG 谱差（含关联 − 无关联）与吸收谱差的关联作为'关联指纹'，推广到其他宽禁带/弱屏蔽体系（碱金属卤化物、稀土卤化物、金刚石）以及激发态动力学（激子解离、Mott 转变对 HHG 的实时响应）。
- 作者框架的天然扩展：动态屏蔽（RT-GW 而非绝热 HSEX）、两光子/瞬态吸收谱（框架已支持 time-dependent observable）、二维材料的 excitonic HHG 与此前 RT-HSEX 文献的对接——成本优势（DFPT 免空态）使这些扩展从'算不动'变'算得动'。
- 与 SBE 半经典路线的关系：此框架的 EOM 就是含 HSEX 自能项的 SBE（密度矩阵形式、length gauge 等价的 ξ 耦合写法）——半经典两带 SBE 用户可把这个框架当作'多带+关联'的系统升级路径，而不是另起炉灶。

### 来源

- [arXiv 2608.16226](https://arxiv.org/abs/2608.16226)
- 导入自 hermes 深度分析（2026-09-08T15:00:18Z）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：KCW-EDUS：Koopmans 谱泛函 + Wannier 局域化的高效非平衡电子动力学（RT-HSEX 推广到三维体材料的激子 HHG）

**原理**：把 Koopmans 谱泛函（qKI，GW 级精度免空态求和）+ EDUS 实时密度矩阵传播器（Wannier 基，规避 Bloch 基规范不连续）+ DFPT 屏蔽库仑矩阵元缝合成 KCW-EDUS 框架（Quantum ESPRESSO + Wannier90 生态）；密度-密度近似（只保留轨道密度项、丢弃相干项——相干项在库仑核最大区域剧烈变号积分抵消）把 SEX 自能从 O(Nw⁴NR²) 降到 O(Nw²NR)、存储从 Nw⁴NR³ 降到 Nw²NR。核心物理结论：Si（3000 nm、5×10¹¹ W/cm²）中 IPA 与 HSEX 谱几乎无差别（多体作用主要是重整化准粒子带结构）；LiF（1500 nm、1.2×10¹³ W/cm²）中 HSEX 谐波在激子共振（13.3 eV ≈ H17、21.5 eV ≈ H27）处选择性增强——弱屏蔽宽禁带体系中 HHG 探测的是关联电子-空穴激发而非单纯准粒子带结构。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 计算设置 | Quantum ESPRESSO LDA + ONCV 赝势（pseudo-dojo 0.4.1）；实验晶格 Si 5.44 Å/GaAs 5.65 Å/LiF 4.03 Å；截断 Si 60 Ry、GaAs/LiF 80 Ry（密度与势 240/320 Ry）；8×8×8 k 网格；吸收：Si/GaAs 8 带 sp³ MLWF、LiF 10 带；HHG：LiF 7 带、Si 8 带原子中心 s/p 模型 + WannierBerri 对称化（消除 MLWF 反演破缺伪偶次谐波）；Si HHG 驱动：3000 nm、5×10¹¹ W/cm²、200 fs | 研究方法·计算细节 |
| 密度-密度近似 | Hartree 项 Wannier 基严格对角（δnmδR0）；SEX 项 Σ = −W_nm(R)ρ_nm(R)；GaAs 中 W(R) 快衰减但密度矩阵长程、LiF 相反——乘积（HSEX 自能）都短程；LiF 吸收谱 4×4×4 R 网格（30 Bohr）与 8×8×8（60 Bohr）不可区分 | 研究方法·密度-密度近似 / 主要发现 |
| 线性基准 | Si/GaAs/LiF 的 HSEX 吸收谱（与实验第一峰对齐后）与 G0W0+BSE 及实验吻合良好；IPA 完全缺失激子峰；LiF 激子峰 13.3 eV 深居于 qKI 准粒子带隙 15.3 eV 之内 2 eV | 主要发现与核心结论·线性区光谱精度 |

**适用边界**：静态平衡屏蔽（绝热 HSEX——强非平衡/驱动周期内屏蔽来不及响应场景可能失效，需动态屏蔽修正量级估计）；密度-密度近似依赖 Wannier 局域性（金属/强关联/莫尔超晶格等衰减不快体系需验证）；全部算例为三维块体（二维/异质结/表面/量子几何体系未探）；激子动力学的时域分解（e-h 对形成/退相干/屏蔽演化的时间分辨）未报告；HHG 谱绝对产率/相位/偏振/角分辨与实验的定量对比未做。
**代表作**：EPFL/Madrid/CNR/PSI 团队（arXiv:2608.16226）。强场接口：材料激子束缚能小时（Si 型）IPA+QP 够用、激子峰深入带隙时（LiF 型）反演物理对象本身变——HHG 反演 σ_solid 与 Berry 曲率的适用判据；ZnO（激子束缚 60 meV）属弱激子侧反演框架安全；与 SBE（半经典多带）+ Maxwell（宏观传播）构成固体 HHG 理论三层（微观关联/半经典/传播）——关联修正微观电流源 + 传播重塑宏观谱形互补对接，界定反演误差预算两端。
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[2608.16226]]
- [[2608.20306]]
- [[Berry 曲率]]
- [[Efficient nonequilibrium electron dynamics from first-principles: leveraging Koopmans spectral functionals and Wannier localization]]
- [[TDDFT]]
- [[Wannier函数]]
- [[三步模型]]
- [[固体HHG]]
- [[密度泛函微扰理论]]
- [[强关联体系]]
- [[强场驱动]]
- [[拍赫兹电子学]]
- [[莫尔超晶格]]
- [[载波包络相位]]
- [[量子几何]]
- [[量子度规]]
- [[阿秒科学]]
- [[非线性光学]]
<!-- /linsai-wikilinks -->
