---
title: "tight-binding-model"
type: "methods"
created: "2026-09-06T14:41:04Z"
updated: "2026-11-21T11:35:42Z"
tags: ["方法学", "type/method"]
related: ["1807.01616", "2018-1807.02525-floquet-theoretical-formulation-and-analysis-of-high-harmoni", "2023-2310_17007-unambiguous-discrimination-of-high-harmonic-generation-mecha", "2024-2405_16125-impact-of-crystal-symmetries-and-weyl-nodes-on-high-harmonic", "2024-2410.14213-quantum-geometric-tensor-in-systems-with-fractional-band-dis", "2025-2506_13493-nonlinear-bulk-photocurrent-probe-of-z2-topological-phase-tr", "2026-2602.04854-real-and-momentum-space-analysis-of-topological-phases-in-2d", "2026-2606.07983-equilibrium-spin-currents-in-altermagnet-junctions-josephson", "2026-2608_11192-floquet-engineering-of-topological-phases-and-magneto-optica", "2026-2610.35991-theoretical-study-of-high-order-harmonic-generation-in-solid", "2111.10986", "2306.09575", "2310.17007", "2401.09884", "2405.16125", "2407.08420", "2408.04136", "2408.09364", "2410.11541", "2410.11542", "2412.13329", "2501.06885", "2503.13140", "2504.00122", "2506.05230", "2506.13493", "2508.14633", "2512.15370", "2601.12098", "2602.04854", "2602.14875", "2605.22294", "2606.23806", "2608.11192", "2608.26099", "2609.28293", "2610.15251", "5-11", "Berry 曲率", "Berry曲率", "Chern数", "Circular dichroism in high-order harmonic generation: Heralding topological phases and transitions in Chern insulators", "Dynamic moiré-like band modulation in Dirac materials via multi-beam optical interference", "Odd-Parity Chiral Magnons in Collinear Antiferromagnetic Multiferroics（共线反铁磁多铁体中的奇宇称手性磁振子）", "R-WSe₂/MoSe₂ 异质双层中 1s–2p 层间激子超快跃迁的贝里曲率贡献", "TDSE", "TiSe₂高次谐波揭示电荷密度波各向异性序参量", "Wannier函数", "Weyl半金属", "arXivID", "arpes", "circular-dichroism", "floquet-engineering", "交变磁体", "位移电流", "光致相变", "层间耦合", "带内载流子动力学对二维材料光学性质的影响：I. 一般理论", "强场驱动", "扭曲双层石墨烯中高次谐波产生的激光椭圆率依赖", "拓扑绝缘体", "有限尺寸效应", "电荷密度波", "自旋劈裂", "莫尔超晶格", "谷分辨高次谐波：探测 Dirac 锥之外的对称性破缺", "量子几何", "量子度规", "非线性光学", "高次谐波产生"]
source_raw: ""
growth_stage: "mature"
confidence: 0.9
updated_at: "2026-11-21T11:35:42Z"
settled_count: 57
aliases: ["tight-binding", "tight binding", "TB model", "TBM", "紧束缚"]
---

<!-- methods-settle:v1 -->

## 原理

紧束缚模型以原子（或Wannier）轨道为基、用有限截断内跃迁矩阵元构筑稀疏多带晶格哈密顿量，应用面广泛：含TiSe₂多带平均场CDW序参量、Wannier下折跨拓扑相变晶格模型、交变磁体最小模型族及p/d/f/g/i各型X波磁体框架、多带/两带闭式量子度规与Berry曲率（含Zeeman、密度矩阵、非厄米推广）、高次谐波机制分离与Floquet-Bloch光学电流、SSH/Holstein电声耦合联合求解、Wannier+TDDM含时驱动多层/扭转石墨烯逐谐波阶归源、魔角/魔距等价类距离依赖Slater-Koster层间跃迁、Haldane型复数次近邻手性跃迁、补偿亚铁磁巨自旋劈裂Wannier最小模型、Harper-Hofstadter在φ=1/4精确解析对角化、实对称化近线性百万原子级能带计算、层状反铁磁（CrI3）能带与偶极矩阵元作非线性光学输入、拓扑反铁磁量子度量偶极子、WP2/TaAs等Weyl半金属多带TDSE-HHG、ARPES初态Wannier输入、THz石墨烯纳米带Floquet、动态莫尔映射magic-angle到光场参数、蜂窝晶格交错交换场自旋劈裂、C8/C10准晶莫尔陈数镶嵌、转角双层1T-TaS2莫尔-莫特竞争、弱耦合分子晶体双分子二聚体最小模型、含三角翘曲与高阶项的扩展k·p/紧束缚逐阶对称破缺归源、可公度摩尔超晶格TB（θ=21.79°最小超胞提供tBLG能带与跃迁偶极矩阵元、作非微扰强场高阶非线性光学输入）、kagome紧束缚最小晶格模型（1/3填充Dirac能带、两个Dirac点，作为质量项分类载体）、Peierls相位耦合含时紧束缚（以跃迁相因子t·exp(ie/ℏ∫A·dl)引入光场，在有限尺寸样品谱中分辨Floquet二阶拓扑绝缘体0D角态与一阶/二阶边界态）、SSH型交错势双带链紧束缚模型（解析能带+闭式Floquet处理，解析证明HHG带内/带间双平台及宽度标度律）、两带紧束缚TDSE动量表解析解（对任意维度两格点单胞与任意矢量势A(t)给出单电子波函数系数的闭式解，可作数值TDSE与近似方法如Houston基+Landau-Zener的精确基准）、Grünwald-Letnikov分数阶导数紧束缚模型（格点上直接实现分数色散、等价幂律长程跃迁，可推广到其它晶格与维度做色散与量子几何工程）、二维交变磁体/p波磁体异质结格点模型直接计算平衡自旋流随结参数依赖、d波交变磁双子晶格有效模型以子晶格间跃迁强度为可调参量扫描相图并定位拓扑相变临界点与能隙闭合位置、奇异平带紧束缚晶格模型提供带触点与平带缠绕平台（演示量子几何使能的Landau-Zener隧穿与平带离域动力学）、DFT参数化k·p/紧束缚为不同扭转角异质双层提供低能能带与Berry曲率随堆叠几何演化输入（1s-2p层间激子语境）、莫尔微带连续/紧束缚模型提供电子态miniband色散与带边/范霍夫结构并决定激子极化子临界填充位置、最大局域化Wannier函数紧束缚插值（Wannier90类流程）在稠密k网格上高效计算自旋分辨位移电流张量频率谱（支撑VOX₂巨自旋位移电流与σxxx随铁电极化可调结论）、含层间跃迁紧束缚模型为单层/双层MoS₂提供真实能带与动量依赖跃迁偶极（使谐波计算超越抛物带/两带近似）、深度学习紧束缚哈密顿量以等变神经网络学习构型-哈密顿映射（对任意热构型以第一性原理精度即时给出TB矩阵元，使大体系、多热构型HHG计算在成本上可行）、DFT参数化V2Se2O族交变磁体最小TB哈密顿量（将DFT能带投影为以V-d轨道为主、可解析调用的多带模型，为输运与强场带动力学模拟提供真实能带基础）、ZnO各向异性多带紧束缚/k·p建模（提供沿不同晶轴方向的色散与带间偶极矩阵元d_cv(k)作为取向依赖HHG模拟的关键微观输入，以多个耦合价带经隧穿跃迁至导带的图像定性复现谐波产率随偏振角的强各向异性调制）、Haldane/陈绝缘体可调质量项紧束缚模型（同一模型内通过质量项连续扫描实现拓扑平庸相、非平庸相及相变点的对照研究，为拓扑高次谐波谱学提供单一模型内可连续调制的对照平台）、DFTB（密度泛函紧束缚，以DFT派生的最小基组双中心参数化将紧束缚扩展至数千原子量级大超胞，使不同空位构型的电子结构计算成为可能）、反自旋Laue群分类的最小k·p/紧束缚模型构建（为反交变磁体每个群类给出代表性最小模型、显式展示自旋劈裂的波矢依赖形式）、石墨烯强场能带模型（紧束缚/狄拉克锥，以中心对称二维能带体系为算例演示空间非均匀场诱导的偶次谐波与产率增强）、少带紧束缚Floquet-Bloch固态HHG的Julia实现（在少带TB框架下计算驱动电流及高次谐波谱，为固态HHG建模提供轻量可复用的数值途径）、Haldane通量/复跃迁磁振子紧束缚建模（将共线反铁磁多层中亚晶格内DMI映射为反手性Haldane通量，建立奇宇称手性磁振子劈裂符号与DMI几何的直观对应，把TB复跃迁框架从电子能带推广至磁振子体系）、超莫尔大尺度紧束缚建模（构造扭转石墨烯/hBN对齐等多尺度莫尔的原子级大体系哈密顿量，为核多项式（KPM）类无对角化谱算法提供2^30站点规模的测试平台）、Star-of-David团簇分子轨道/紧束缚分析（以CDW团簇分子轨道构筑有效单带模型量化CDW致窄带压缩因子、并构造有效单带Hubbard模型以估计U/W莫特判据，把TB能带下折延伸至强关联莫特相图判断）、各向异性蜂窝紧束缚模型（以跃迁各向异性、交换场取向与化学势为可调参量构造可控参数空间，充当对称性引导机器学习自旋依赖非线性响应研究的数据生成与对称性检验模型平台）、多轨道紧束缚晶格模型（以最简多轨道构型复现轨道序诱导的奇宇称p/f波自旋劈裂及其随序参量与Hund耦合的演化）、二聚化格子反铁磁紧束缚最小模型（完整演示PT简并解除、光致自旋劈裂与拓扑相变过程，将TB最小模型手段延伸至光致奇宇称交变磁性的机制演示）、开边界紧束缚数值对角化（直接展示同一准能隙内Floquet螺旋边界模与二阶角模的共存，验证混合高阶拓扑相的体边对应）、d波能隙紧束缚/BCS最小模型（二维方格子、铜氧化物费米面，以能隙节点与各向异性编码晶体对称性，作为取向分辨高次谐波超快读取高温超导配对序参量对称性指纹的理论来源）、方格子交错磁通零净磁通Haldane型紧束缚建模（以Peierls相位实现交错复跃迁，在无真实磁场条件下破缺时间反演并诱导拓扑能带）、AB堆叠双层Haldane紧束缚模型（含层间跃迁与层内Haldane磁通，使层间耦合与光驱动Floquet对拓扑相的贡献可被分离解析）、热原子实现Haldane紧束缚模型的Chern数能带分析（在调制深度、失谐与相位参数空间中解析带隙闭合与|C|=2高陈数相的出现，把Haldane型TB拓扑相图分析扩展至人工量子模拟平台）、ABC堆叠多层石墨烯紧束缚模型（提供层间隧穿t⊥与手性简并能带结构，构成与腔诱导项竞争的另一关键参数轴）、骰子（T3）晶格紧束缚模型（枢纽-边缘三子格框架、天然携带可承载非平庸拓扑的简并平带，服务非线性霍尔响应探测拓扑相变）、三带α-T3紧束缚哈密顿量（以单一含离面内SOC项的最小模型在石墨烯与骰子格子间连续插值，为Floquet自旋轨道补偿及平带/四极拓扑研究提供统一框架）、方八角格子+交错磁通/自旋轨道耦合调制紧束缚最小模型（展示Dirac节点与平带如何被SMF与SOC调制为拓扑非平庸能带）及配套DFT+Wannier紧束缚参数化（在候选材料中提取真实跃迁参数、论证方八角拓扑平带方案的材料可实现性）、以及菱方堆叠石墨烯多层紧束缚/能带模型（用于确定偶极零点位置与光学涡旋手性规则随层数和堆叠对称性的演化，把TB能带-偶极输入延伸到结构光场手性响应的对称性分析）。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| tBLG可公度摩尔超晶格最小超胞扭角 | 21.79° | 2020-2003.03201 |
| kagome紧束缚模型Dirac能带填充 | 1/3填充 | 2024-2409.12345 |
| kagome紧束缚模型Dirac点数 | 2个 | 2024-2409.12345 |
| 超莫尔TB无对角化谱算法测试平台规模 | 2^30站点 | 2024-2409.18898 |
| 热原子实现Haldane紧束缚模型高陈数相Chern数绝对值 | 2（无量纲，|C|=2） | 2025-2509.08411 |

## 适用边界

本轮新证据（2026-2609.21586三带α-T3紧束缚哈密顿量，含离面内SOC项、作为石墨烯与骰子格子的插值最小模型）仅简报级携入、未携数值，核实前仅限定性结论（插值参数α的取值范围、SOC项形式与幅度、Floquet自旋轨道补偿机制及平带/四极拓扑相的具体参数化与判定判据均待回原文核实，且三带最小模型对真实α-T3材料多带细节与SOC截断的覆盖、Floquet驱动下SOC补偿结论对驱动参数的敏感性待评估）；上轮菱方堆叠石墨烯多层TB/能带模型（2026-2611.04076）亦仅简报级携入、未携数值，核实前仅限定性结论（菱方堆叠层数范围、层间跃迁参数化、偶极零点与手性规则的具体数值结论及堆叠对称性分类细节均待回原文核实，且TB偶极输入对光学涡旋手性判据的近似适用范围、层间/层内跃迁截断对手性规则结论的敏感性待评估）；此前各简报级条目（热原子Haldane、ABC多层石墨烯、骰子T3、方八角SMF/SOC及其DFT-Wannier参数化、零净磁通Haldane、AB双层Haldane、开边界Floquet对角化、d波能隙TB/BCS、多轨道与二聚化反铁磁TB、各向异性蜂窝TB、Star-of-David、超莫尔TB、Julia少带TB-Floquet、DMI磁振子TB、石墨烯非均匀场谐波、反自旋Laue群最小模型、DFTB、Haldane可调质量项TB、V2Se2O DFT-Wannier TB、深度学习TB、两带TDSE解析解（闭式解限定两格点单胞/两带单电子情形）、MoS₂含层间跃迁TB等）均未携数值、核实前仅限定性结论；交变磁体自旋位移电流Wannier插值（2025-2503.13140）已回原文核实但其所携数值（VOI₂极化−2.77×10⁻¹⁰ C/m与极化场7.026 V/Å）属Berry phase法材料属性而非TB本征参数、极化场由E=P/ε₀线性估算非自洽场结果外推需谨慎；ZnO各向异性多带TB/k·p（2025-2512.15370）片段内未含TB本征参数数值且模型预测三重角向调制与实验四重对称存在差异、待回全文核实；异质双层Berry曲率（2024-2408.04136）、莫尔微带激子极化子（2025-2503.07712）、奇异平带（2026-2601.20093）、分数阶导数（2024-2410.14213，其幂律长程跃迁突破传统近邻有限截断假设、尾部收敛性与稀疏性/成本需另行检验）、交变磁体异质结（2026-2606.07983）、d波交变磁双子晶格（2026-2602.04854）等简报级条目仍无核实数值，SSH链闭式Floquet（2018-1807.02525）、kagome质量项分类（2024-2409.12345）、应变石墨烯Peierls耦合Floquet（2026-2605.07190）及可公度摩尔超晶格TB（2020-2003.03201）核实前仅限已携数值（θ=21.79°、1/3填充、两个Dirac点）；模型整体精度仍受Wannier轨道质量、近邻截断半径与可公度超胞选取（仅特定离散扭角可严格周期化，超莫尔多尺度体系更依赖结构弛豫与层级参数化质量）限制，Peierls替换把光场仅以跃迁相位引入、强场/多带情形的规范与带间耦合近似需另行检验（少带Floquet-Bloch实现还叠加Floquet截断与收敛性问题，开边界Floquet对角化、双层Haldane-Floquet拓扑与光致相变类含时处理亦同），大体系实空间含时传播的计算成本仍随原子数显著增长（学习型TB或可摊薄多热构型采样的矩阵元获取成本、DFTB虽把可处理规模推进至数千原子量级但随机无序构型仍需大超胞统计采样与构型平均，超莫尔TB+核多项式类无对角化谱算法虽以2^30站点规模为测试平台但属静态谱方法、不改变含时波包传播本身的标度，且上述途径均以参数化/训练数据覆盖范围与转移误差为代价），Wannier插值对位移电流类响应的可靠性亦依赖所截Wannier基组对低能带的完整再现。

## 代表作

- 2018-1807.02525-floquet-theoretical-formulation-and-analysis-of-high-harmoni
- 2020-2007.13434-intense-laser-driven-electron-dynamics-and-high-harmoni
- 2024-2401.01100-topological-high-harmonic-spectroscopy
- 2024-2409.12345-classification-of-mass-terms-in-kagome-semimetals
- 2026-2605.07190-floquet-second-order-topological-insulator-in-strained-graph
- 2020-2003.03201-high-order-nonlinear-optical-response-of-a-twisted-bilayer-g
- 2026-2610.15251-valley-resolved-high-harmonics-probe-symmetry-brea
- 2024-110.115415-dependence-of-high-harmonic-generation-in-twisted-bilayer-gr

## 证据日志

- 2026-10-25｜r97｜仅简报｜[paper:2024-2408.04136-berry-curvature-contribution-towards-1s-2p-interlayer-excito] 第一性原理能带与贝里曲率计算（DFT参数化k·p/紧束缚）：为不同扭转角下异质双层提供低能能带与贝里曲率随堆叠几何演化的定量输入。
- 2026-10-25｜r97｜仅简报｜[paper:2025-2503.07712-purely-electronic-model-for-exciton-polaron-formation-in-moi] 莫尔微带连续/紧束缚模型：提供电子态的莫尔miniband色散与带边/范霍夫结构，作为极化子物理的输入并决定临界填充位置。
- 2026-10-25｜r98｜回原文｜[paper:2025-2503.13140-giant-spin-shift-current-in-two-dimensional-altermagnetic-mu] 最大局域化瓦尼尔函数紧束缚插值（Wannier90类流程）：在稠密k网格上高效计算自旋分辨位移电流张量的频率谱。
- 2026-10-25｜r98｜仅简报｜[paper:2021-2111.10986-high-harmonic-generation-in-monolayer-and-bilayer-of-transit] 紧束缚模型（含层间跃迁）：为单层/双层 MoS2 提供真实能带与动量依赖跃迁偶极，使谐波计算超越抛物带/两带近似。
- 2026-10-30｜r101｜仅简报｜[paper:2020-2007.13434-intense-laser-driven-electron-dynamics-and-high-harmonic-gen] 两带紧束缚TDSE动量表解析解：对任意维度两格点单胞与任意矢量势A(t)给出单电子波函数系数的闭式解，可作数值TDSE与近似方法（如Houston基+Landau-Zener）的精确基准。
- 2026-10-30｜r102｜仅简报｜[paper:2026-2610.35991-theoretical-study-of-high-order-harmonic-generation-in-solid] 深度学习紧束缚哈密顿量（等变神经网络学习构型-哈密顿映射）：对任意热构型以第一性原理精度即时给出 TB 矩阵元，使大体系、多热构型的 HHG 计算在成本上可行。
- 2026-10-31｜r103｜仅简报｜[paper:2026-2602.09465-realistic-tight-binding-model-for-v2se2o-family-altermagnets] DFT-Wannier紧束缚参数化：将DFT能带投影为以V-d轨道为主的最小TB哈密顿量，为输运或强场带动力学模拟提供可直接调用的可解析多带模型。
- 2026-10-31｜r106｜回原文｜[paper:2025-2512.15370-orientation-dependent-high-harmonic-generation-in-zno] 各向异性能带与带间偶极矩阵元建模（紧束缚/k·p）：提供ZnO沿不同晶轴方向的色散与d_cv(k)输入，是取向依赖模拟的关键微观参量。
- 2026-10-31｜r109｜仅简报｜[paper:2024-2401.01100-topological-high-harmonic-spectroscopy] Haldane/陈绝缘体紧束缚模型（可调质量项）：通过质量项连续扫描实现同一模型内拓扑平庸相、非平庸相及相变点的对照研究。
- 2026-11-06｜r115｜仅简报｜[paper:2026-2608.04742-atomic-scale-ordering-of-sulfur-vacancies-enhances-charge-tr] DFTB（密度泛函紧束缚）：使数千原子量级大超胞中不同空位构型（有序 vs 随机）的电子结构计算成为可能。
- 2026-11-06｜r116｜仅简报｜[paper:2026-2608.19056-anti-spin-laue-groups-classification-of-anti-altermagnets-an] 最小k·p/紧束缚模型构建：为每个群类给出代表性最小模型，显式展示自旋劈裂的波矢依赖形式（如d/g波节点图样），可直接用于输运与光学响应估算。
- 2026-11-07｜r118｜仅简报｜[paper:2025-2508.00273-spatially-inhomogeneous-field-induced-harmonic-radiation-in] 石墨烯强场能带模型（紧束缚/狄拉克锥）：提供中心对称二维能带体系作为算例，演示非均匀场诱导的偶次谐波与产率增强。
- 2026-11-08｜r123｜仅简报｜[paper:2026-2611.00354-a-julia-implementation-of-floquet-bloch-theory-for] 紧束缚模型固态 HHG 计算：在少带紧束缚框架下计算驱动电流及高次谐波谱，为固态 HHG 建模提供轻量途径。
- 2026-11-08｜r123｜仅简报｜[paper:2026-2605.22294-odd-parity-chiral-magnons-in-collinear-antiferromagnetic-mul] Haldane 通量/复跃迁紧束缚建模：将亚晶格内 DMI 映射为反手性 Haldane 通量，建立手性劈裂符号与 DMI 几何的直观对应。
- 2026-11-14｜r132｜仅简报｜[paper:2024-2409.18898-correlated-states-in-super-moiré-materials-with-a-kernel-pol] 超莫尔大尺度紧束缚建模：构造扭转石墨烯/hBN 对齐等多尺度莫尔的原子级大体系哈密顿量，为算法提供 2^30 站点规模的测试平台。
- 2026-11-14｜r135｜仅简报｜[paper:2025-2509.17419-topical-review-the-nature-of-the-ground-state-and-possibilit] Star-of-David团簇分子轨道/紧束缚分析：量化CDW导致的窄带压缩因子，并构造有效单带Hubbard模型以估计U/W莫特判据。
- 2026-11-14｜r136｜仅简报｜[paper:2026-2610.28529-symmetry-guided-machine-learning-of-spin-dependent-nonlinear] 各向异性蜂窝紧束缚模型：通过调节跃迁各向异性、交换场取向与化学势构造可控参数空间，充当数据生成与对称性检验的模型平台。
- 2026-11-15｜r137｜仅简报｜[paper:2025-2508.18361-odd-parity-altermagnetism-originated-from-orbital-orders] 多轨道紧束缚晶格模型：以最简多轨道模型复现轨道序诱导的p/f波自旋劈裂及其随序参量、 Hund耦合的演化。
- 2026-11-15｜r137｜仅简报｜[paper:2025-2508.18360-light-induced-odd-parity-altermagnets-on-dimerized-lattices] 二聚化格子反铁磁紧束缚模型：提供最小晶格模型完整演示PT简并解除、光致自旋劈裂与拓扑相变过程。
- 2026-11-15｜r138｜仅简报｜[paper:2025-2509.19992-breakdown-of-the-symmetry-constraint-in-a-floquet-topologica] 开边界紧束缚数值对角化：直接展示同一准能隙内螺旋边界模与二阶角模的共存，验证混合高阶拓扑相的体边对应。
- 2026-11-15｜r138｜仅简报｜[paper:2025-2503.21766-ultrafast-readout-of-the-order-parameter-symmetry-in-high-tc] d波能隙紧束缚/BCS最小模型（二维方格子、铜氧化物费米面）：以能隙节点与各向异性编码晶体对称性，是取向分辨谐波指纹的理论来源。
- 2026-11-15｜r139｜仅简报｜[paper:2025-2503.04161-square-lattice-model-with-staggered-magnetic-fluxes-zero-che] Haldane型零净磁通紧束缚建模（佩尔斯相位）：以交错复跃迁相位在无真实磁场条件下破缺时间反演并诱导拓扑能带。
- 2026-11-15｜r139｜仅简报｜[paper:2026-2603.24551-interlayer-coupling-and-floquetdriven-topological-phases-in] AB堆叠双层Haldane紧束缚模型：含层间跃迁与层内Haldane磁通的模型使层间耦合与光驱动对拓扑的贡献可被分离解析。
- 2026-11-15｜r140｜仅简报｜[paper:2025-2509.08411-realizing-the-haldane-model-in-thermal-atoms] Haldane紧束缚模型的Chern数能带分析：用以解析调制深度、失谐与相位参数空间中的带隙闭合与高陈数（|C|=2）相的出现。
- 2026-11-15｜r140｜仅简报｜[paper:2025-2504.03842-tunable-topological-phases-in-multilayer-graphene-coupled-to] 多层石墨烯（ABC 堆叠）紧束缚模型：提供层间隧穿 t⊥ 与手性简并能带结构，构成与腔诱导项竞争的另一关键参数轴。
- 2026-11-15｜r140｜仅简报｜[paper:2026-2605.21229-probing-topological-phase-transitions-via-nonlinear-hall-res] 骰子（T3）晶格紧束缚模型：提供枢纽-边缘三子格框架，天然携带可承载非平庸拓扑的简并平带。
- 2026-11-15｜r140｜仅简报｜[paper:2025-2511.13349-topologically-nontrivial-flat-bands-and-quantum-hall-crossov] 紧束缚模型（方八角格子 + SMF/SOC 调制）：给出最小模型，展示 Dirac 节点与平带如何被交错磁通和自旋轨道耦合调制为拓扑非平庸能带。
- 2026-11-15｜r140｜仅简报｜[paper:2025-2511.13349-topologically-nontrivial-flat-bands-and-quantum-hall-crossov] DFT + Wannier 紧束缚参数化：在候选材料中提取真实跃迁参数，论证方八角拓扑平带方案的材料可实现性。
- 2026-11-21｜r1｜仅简报｜[paper:2026-2611.04076-chirality-rules-for-optical-vortices-in-rhombohedr] 菱方堆叠石墨烯多层紧束缚/能带模型：用于确定偶极零点位置与手性规则随层数和堆叠对称性的演化。
- 2026-11-21｜r1｜仅简报｜[paper:2026-2609.21586-floquet-spin-orbit-compensation-and-flat-and-quadr] 紧束缚模型（三带 α-T3 哈密顿量）：提供插值石墨烯与骰子格子的最小模型框架，含离面内 SOC 项。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[1807.01616]]
- [[2018-1807.02525-floquet-theoretical-formulation-and-analysis-of-high-harmoni]]
- [[2023-2310_17007-unambiguous-discrimination-of-high-harmonic-generation-mecha]]
- [[2024-2405_16125-impact-of-crystal-symmetries-and-weyl-nodes-on-high-harmonic]]
- [[2024-2410.14213-quantum-geometric-tensor-in-systems-with-fractional-band-dis]]
- [[2025-2506_13493-nonlinear-bulk-photocurrent-probe-of-z2-topological-phase-tr]]
- [[2026-2602.04854-real-and-momentum-space-analysis-of-topological-phases-in-2d]]
- [[2026-2606.07983-equilibrium-spin-currents-in-altermagnet-junctions-josephson]]
- [[2026-2608_11192-floquet-engineering-of-topological-phases-and-magneto-optica]]
- [[2026-2610.35991-theoretical-study-of-high-order-harmonic-generation-in-solid]]
- [[2111.10986]]
- [[2306.09575]]
- [[2310.17007]]
- [[2401.09884]]
- [[2405.16125]]
- [[2407.08420]]
- [[2408.04136]]
- [[2408.09364]]
- [[2410.11541]]
- [[2410.11542]]
- [[2412.13329]]
- [[2501.06885]]
- [[2503.13140]]
- [[2504.00122]]
- [[2506.05230]]
- [[2506.13493]]
- [[2508.14633]]
- [[2512.15370]]
- [[2601.12098]]
- [[2602.04854]]
- [[2602.14875]]
- [[2605.22294]]
- [[2606.23806]]
- [[2608.11192]]
- [[2608.26099]]
- [[2609.28293]]
- [[2610.15251]]
- [[5-11]]
- [[Berry 曲率]]
- [[Berry曲率]]
- [[Chern数]]
- [[Circular dichroism in high-order harmonic generation: Heralding topological phases and transitions in Chern insulators]]
- [[Dynamic moiré-like band modulation in Dirac materials via multi-beam optical interference]]
- [[Odd-Parity Chiral Magnons in Collinear Antiferromagnetic Multiferroics（共线反铁磁多铁体中的奇宇称手性磁振子）]]
- [[R-WSe₂/MoSe₂ 异质双层中 1s–2p 层间激子超快跃迁的贝里曲率贡献]]
- [[TDSE]]
- [[TiSe₂高次谐波揭示电荷密度波各向异性序参量]]
- [[Wannier函数]]
- [[Weyl半金属]]
- [[arXivID]]
- [[arpes]]
- [[circular-dichroism]]
- [[floquet-engineering]]
- [[交变磁体]]
- [[位移电流]]
- [[光致相变]]
- [[层间耦合]]
- [[带内载流子动力学对二维材料光学性质的影响：I. 一般理论]]
- [[强场驱动]]
- [[扭曲双层石墨烯中高次谐波产生的激光椭圆率依赖]]
- [[拓扑绝缘体]]
- [[有限尺寸效应]]
- [[电荷密度波]]
- [[自旋劈裂]]
- [[莫尔超晶格]]
- [[谷分辨高次谐波：探测 Dirac 锥之外的对称性破缺]]
- [[量子几何]]
- [[量子度规]]
- [[非线性光学]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
