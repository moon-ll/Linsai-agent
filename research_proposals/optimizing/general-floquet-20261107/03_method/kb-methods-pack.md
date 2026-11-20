# 课题方法素材包（KB 自动聚合，v7.2.30 wikilink 节点格式）

- 课题：general-floquet-20261107
- 生成时间：2026-11-20T11:41:00Z
- 方法关键词：Floquet、一判据表可观测量、磁薄膜的吸附调控

> 用途：update_method_manual / writer 写方案时的可实施细节来源。
> **v7.2.30 起改 wikilink 节点格式**：每条方法/参数都附 `[[方法页slug]]` 双向链接，
> writer 落盘后由 `kb_pack_wikilink_guard.py` 校验（≥3 引用为达标）。
> 参数必须按参数溯源纪律标注来源；本包为 KB 索引摘要，取参数前读对应页原文。

## 〇、方法专题（1，谱系/选型层）

### [[method-topics/量子几何量测量方法谱系|量子几何量测量方法谱系（Berry 曲率 / 量子度规 / 拓扑数）]]
页：knowledge/wiki/method-topics/量子几何量测量方法谱系.md
专题定位：面向「用 HHG 读出凝聚态量子几何量」这一测量目标的路线谱系——

## 一、匹配的知识库方法页（8）

### [[methods/floquet-engineering|floquet-engineering]]
页：knowledge/wiki/methods/floquet-engineering.md
摘要：Floquet工程以周期光场将固体哈密顿量化为Floquet-Bloch准能级与边带，其严格基础是Sambe扩展希尔伯特空间中把时间作为坐标的 K = H(t) − i∂_t 本征问题（给出准能量谱与周期性本征射线并作为绝热展开的严格基，该扩展空间静态本征问题表示还支持逐准能隙含反常π能隙的绕数/动态不变量拓扑分析、判定对称性约束破缺并区分无静态对应的驱动诱导边界态），将该Sambe扩展推进到BdG哈密顿量的光子扇区可精确加倍Cooper对关联流形（对称性加倍机制）并在Sigrist-Ueda/Balian-Werthamer自旋-宇称分类中新增Floquet频率宇称量子数、预言奇频-奇宇称-轨道单重态新配对通道及Floquet Majorana平带，高频非共振时Floquet-Magnus/van Vleck/Floquet-Schrieffer-Wolff展开可将其约化为时间平均的静态

### [[methods/Floquet工程|Floquet工程]]
页：knowledge/wiki/methods/Floquet工程.md
摘要： Baykusheva等用于实现Hubbard激子相干控制的方法，通过周期性驱动调制强关联体系的激发态。  <!-- linsai-wikilinks --> ## 关联概念  - [[强关联体系]] - [[相干控制]] <!-- /linsai-wikilinks --> 

### [[methods/Floquet工程实现Hubbard激子相干控制|Floquet工程实现Hubbard激子相干控制]]
页：knowledge/wiki/methods/Floquet工程实现Hubbard激子相干控制.md
摘要： Baykusheva等通过Floquet工程实现对Hubbard激子的相干控制，印证多体响应的可控性。  <!-- linsai-wikilinks --> ## 关联概念  - [[Floquet工程]] - [[相干控制]] <!-- /linsai-wikilinks --> 

### [[methods/Chern数与贝里曲率计算|Chern数与贝里曲率计算]]
页：knowledge/wiki/methods/Chern数与贝里曲率计算.md
摘要：Chern数由贝里曲率在布里渊区上的积分给出，用于读出光驱动/Floquet切换前后拓扑不变量的符号变化（符号由 sgn(ηAxAy) 固定）并作为霍尔类响应的可读出判据；随驱动参量增大可出现 ΔC=±1/±2/±3 的拓扑相变序列，f波奇宇称磁体在圆偏光（CPL）下Floquet能带可达 C_lattice=±2，各转变均伴随带隙闭合及隙处贝里曲率的重分布。  ## 参数表  | 参数 | 数值 | 出处 | | --- | --- | --- | | Floquet能带Chern数（f波奇宇称磁体，CPL驱动） | C_lattice = ±2 | 2026-2607.19483-optical-magnetic-switching-in-odd-parity-magnets-with-spin-o | | 驱动诱导拓扑相变的Chern数变化序列 | ΔC = ±1/±2/±3 | 2

### [[methods/trarpes|时间/角度分辨光电子能谱（trARPES）]]
页：knowledge/wiki/methods/trarpes.md
摘要：以泵浦-探测光电子发射在角度（动量）分辨的能带测量上叠加飞秒时间维度，直接成像泵浦诱导的能带重整化、Floquet边带与动态能隙及其超快时间演化，并可实现层分辨，直接区分不同层（如扭转双层石墨烯两层）的载流子布居与激子谱特征动力学。  ## 参数表  **库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）： | 泵浦 | 515 nm；通量 1.5–2.5 mJ/cm² | §泵浦条件  | 电声耦合 | dE_g/dL=1.1 eV/nm；dE_c/dL=0.2 eV/nm | §第一性原理计算  | trARPES 对照 | K 点电子 0.6 ps；空穴双指数快 ~2 ps/慢 >5 ps | §互补表征  | 泵浦 | IR 1.2 eV/135 fs/2.7 mJ/cm²；LCP/RCP | §研究方法  | XUV 探针 | 21.6 eV（H9）

### [[methods/landau|Landau-Zener 隧穿模型（非绝热近似）]]
页：knowledge/wiki/methods/landau.md
摘要：Landau-Zener 隧穿以 P≈exp(−πΔ²/(2ħv)) 将回避交叉处的非绝热布居转移量化为能隙 Δ 与失谐扫描速率 v 的竞争，是线性扫频二能级回避交叉的标准基准；新证据将其推广为强场非线性光-物质相互作用中 Floquet 修饰态间的一般非微扰机制——修饰光电子终态在与其他 Floquet 态形成的回避交叉处经 LZ 隧穿获得布居，使高场强下多光子光电子能谱出现 Floquet 修饰（微扰）图像无法描述的附加结构。  ## 参数表  | 参数 | 数值 | 出处 | | --- | --- | --- | | 观测特征场强 F0^exp（AT 劈裂/LZ 特征出现的场强区间） | ~2.2 V/nm | arXiv:2503.04431 | | 驱动光子能量 ωp（置于 SS-IP1 间隙的 1/3 以增强三光子共振 4PP） | 1.54 eV | arXiv:2503.

### [[methods/tight-binding-model|tight-binding-model]]
页：knowledge/wiki/methods/tight-binding-model.md
摘要：紧束缚模型以原子（或Wannier）轨道为基、用有限截断内跃迁矩阵元构筑稀疏多带晶格哈密顿量，应用面广泛：含TiSe₂多带平均场CDW序参量、Wannier下折跨拓扑相变晶格模型、交变磁体最小模型族及p/d/f/g/i各型X波磁体框架、多带/两带闭式量子度规与Berry曲率（含Zeeman、密度矩阵、非厄米推广）、高次谐波机制分离与Floquet-Bloch光学电流、SSH/Holstein电声耦合联合求解、Wannier+TDDM含时驱动多层/扭转石墨烯逐谐波阶归源、魔角/魔距等价类距离依赖Slater-Koster层间跃迁、Haldane型复数次近邻手性跃迁、补偿亚铁磁巨自旋劈裂Wannier最小模型、Harper-Hofstadter在φ=1/4精确解析对角化、实对称化近线性百万原子级能带计算、层状反铁磁（CrI3）能带与偶极矩阵元作非线性光学输入、拓扑反铁磁量子度量偶极子、WP2/

### [[methods/tomography|平衡零差层析（homodyne tomography）]]
页：knowledge/wiki/methods/tomography.md
摘要：平衡零差层析通过扫描本底振荡（LO）相位测得各相位下正交分量的边缘分布，再经反演重构 Wigner 函数/密度矩阵，常作为与外差层析逐点对比的基准方案；但新证据表明该重构流程脆弱——即使对不含非经典性的经典模型数据，也可能反演出带 Wigner 负值的密度矩阵。  ## 参数表  **库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）： | 发表 | Shen, Zhou, Wang & Wang (2026), arXiv:2609.28680 | 标题行 | | 1D 模型参数 | 周期边界直接带隙半导体：软化参数 s = 25 a.u.、介电常数 ε = 5 a.u.、杂质电离势 E_g − ε₀ = 106.4 meV；激光 F₀ = 10⁻⁴ a.u.（I₀ = 3.5×10⁸ W/cm²）、λ₀ = 50 µm、12 cycle 高斯包络；相干时间

## 二、带方法卡的论文页（6）

### [[papers/2026-2607_17265-first-principles-electron-phonon-scattering-in-real-time-tdd|耗散实时 TDDFT：自能碰撞积分（Born–Markov）嵌入实时传播的第一性原理电子-声子散射]]
页：knowledge/wiki/papers/2026-2607_17265-first-principles-electron-phonon-scattering-in-real-time-tdd.md

### [[papers/2024-2404_12791-observation-of-floquet-states-in-graphene|石墨烯中 Floquet 态的实验观测（Merboldt et al. 2024：强光场周期驱动下电子能带相干缀饰成准能带结构的谱学确认——光驱动拓扑从间接信号推向缀饰能带本身的直接观测）]]
页：knowledge/wiki/papers/2024-2404_12791-observation-of-floquet-states-in-graphene.md
参数样例：参数；---；实验范式

### [[papers/2025-2508_00296-tracking-doublon-holon-dynamics-in-high-harmonic-generation|Sr₂CuO₃ Mott 绝缘体 HHG 中 doublon-holon 动力学的亚周期追踪（反射 HHG + tr-反射 + tdDMFT/NCA）]]
页：knowledge/wiki/papers/2025-2508_00296-tracking-doublon-holon-dynamics-in-high-harmonic-generation.md
参数样例：参数；---；MIR；tdDMFT 参数

### [[papers/2026-2609_30365-repulsion-driven-p-i-p-superconductivity-in-a-sing|DMRG 数值判定排斥相互作用驱动的 p-ip 拓扑超导（单能谷 Dirac）]]
页：knowledge/wiki/papers/2026-2609_30365-repulsion-driven-p-i-p-superconductivity-in-a-sing.md
参数样例：参数；---；数值方法；掺杂结构

### [[papers/2026-2510_16546-high-harmonic-generation-light-source-with-polariz|偏振可编程 HHG 光源（多材料筛选：TMDC/拓扑绝缘体/外延双层石墨烯 + SHG/MIR 双驱动）]]
页：knowledge/wiki/papers/2026-2510_16546-high-harmonic-generation-light-source-with-polariz.md
参数样例：参数；---；材料；激光

### [[papers/2026-2610_13251-ultrafast-laser-stimulated-field-emission-from-a-m|金属激光辅助场发射的 NEGF 多体框架（第二玻恩近似+自洽 Dyson）]]
页：knowledge/wiki/papers/2026-2610_13251-ultrafast-laser-stimulated-field-emission-from-a-m.md
