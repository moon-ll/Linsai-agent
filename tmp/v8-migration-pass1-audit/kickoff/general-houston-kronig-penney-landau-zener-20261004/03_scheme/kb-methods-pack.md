# 课题方法素材包（KB 自动聚合，v7.2.30 wikilink 节点格式）

- 课题：general-houston-kronig-penney-landau-zener-20261004
- 生成时间：2026-11-16T15:42:02Z
- 方法关键词：Berry、Floquet、HHG、SBE、TDDFT、XUV、与电磁传播模拟、区分变量与待测量、多尺度全光学探测、层第一性原理计算、平衡与拓扑态探测、并通过泵浦、建六种全光学探测、强度三重分辨测量

> 用途：update_method_manual / writer 写方案时的可实施细节来源。
> **v7.2.30 起改 wikilink 节点格式**：每条方法/参数都附 `[[方法页slug]]` 双向链接，
> writer 落盘后由 `kb_pack_wikilink_guard.py` 校验（≥3 引用为达标）。
> 参数必须按参数溯源纪律标注来源；本包为 KB 索引摘要，取参数前读对应页原文。

## 〇、方法专题（6，谱系/选型层）

### [[method-topics/固体HHG数值计算方法体系|固体 HHG 数值计算方法体系（TDSE / SBE / rt-TDDFT / 紧束缚）]]
页：knowledge/wiki/method-topics/固体HHG数值计算方法体系.md
专题定位：强激光入射晶体后谐波谱的数值预言方法——四套范式的理论原理、

### [[method-topics/HHG反演方法学|HHG 反演方法学（贝叶斯推断 / 神经网络正则化 / 约束优化）]]
页：knowledge/wiki/method-topics/HHG反演方法学.md
专题定位：从谐波谱反推凝聚态参数（能带色散、跃迁偶极、退相干时间、Berry 曲率、

### [[method-topics/量子几何量测量方法谱系|量子几何量测量方法谱系（Berry 曲率 / 量子度规 / 拓扑数）]]
页：knowledge/wiki/method-topics/量子几何量测量方法谱系.md
专题定位：面向「用 HHG 读出凝聚态量子几何量」这一测量目标的路线谱系——

### [[method-topics/材料体系HHG方法|材料体系 HHG 方法（Weyl 半金属 / 交变磁体 / moiré / 高阶拓扑）]]
页：knowledge/wiki/method-topics/材料体系HHG方法.md
专题定位：四类量子材料的 HHG 指纹、模型栈与判据——每类材料「用什么模型、

### [[method-topics/阿秒计量方法体系|阿秒计量方法体系（条纹术 / RABBITT / Wigner 时延）]]
页：knowledge/wiki/method-topics/阿秒计量方法体系.md
专题定位：阿秒时间信息提取的两大实验范式（streaking / RABBITT）与其

### [[method-topics/强场电离量子轨道方法|强场电离量子轨道方法（SFA / CQSFA / Q-CCSFA）]]
页：knowledge/wiki/method-topics/强场电离量子轨道方法.md
专题定位：强场电离与再碰撞过程的半经典量子轨道方法谱系——从 Keldysh 理论到

## 一、匹配的知识库方法页（8）

### [[methods/固体_HHG_理论四路线_SBE___TDDFT___Wannier-Bloch___规范处理|固体 HHG 理论四路线（SBE / TDDFT / Wannier-Bloch / 规范处理）]]
页：knowledge/wiki/methods/固体_HHG_理论四路线_SBE___TDDFT___Wannier-Bloch___规范处理.md
摘要： SBE 在能带色散局部抛物近似下给出截止标度律，把能带、电流与再碰撞相位联系起来；TDDFT 直接计算强场含时电流、对层间耦合与莫尔势不依赖经验参数，但仅适用莫尔周期小（大扭转角）构型；Wannier-Bloch 轨迹把倒空间几何约束直接对应到谐波阶次与倒空间轨迹长度；Berry 连接规范处理以 London/Coulomb 规范差值检验规范不变性。局限：四条路线均只描述理想晶体，扭转角 + 激子预激发 + 层间传播共同作用下的可检验映射尚无单一路线给出，多体修正须作为参数输入耦合项。  <!-- linsai-wikilinks --> ## 关联概念  - [[TDDFT]] - [[层

### [[methods/PIMD___rt-TDDFT_模拟液态水核量子_HHG|PIMD + rt-TDDFT 模拟液态水核量子 HHG]]
页：knowledge/wiki/methods/PIMD___rt-TDDFT_模拟液态水核量子_HHG.md
摘要：基于**电子-核时间尺度分离**（激光驱动仅几 fs，核运动可忽略；液结构涨落为百 fs–ps）将量子核统计与超快电子动力学**显式解耦**：  1. **PIMD 构型采样**：用 PIGLET 加速的路径积分分子动力学采样含核量子离域（零点运动）的液态水构型系综； 2. **frozen-ion 快照传播**：每个构型作为冻结核快照，实时 TDDFT 传播强场下的电子动力学，逐快照计算 HHG 谱； 3. **系综平均**：对系综平均得宏观谱。该分离同时冻结了电声耦合的动力学部分，使液结构对超快动力学的影响可被单独检验。  **配套诊断协议**（本方法的方法论增量）：  - **相干/非相干谱分解**：S(ω)=|⟨I_k⟩|² 与 S_in(ω)=⟨|I_k|⟩² 的偏离直接量化跨快照相干性，配合复相位箱线图——无需演化密度矩阵即可把 dephasing 归因于液结构统计平均； -

### [[methods/sbe-bloch-equations|sbe-bloch-equations]]
页：knowledge/wiki/methods/sbe-bloch-equations.md
摘要：半导体布洛赫方程（k 空间含时密度矩阵传播，Houston 基或长度/Wannier 规范，亦可实现为含时紧束缚+密度矩阵模拟，属 TDSE/密度矩阵/TDDFT 三类固体 HHG 模拟中的密度矩阵类，定位上桥接解析模型与 TDDFT 的中间强度区）在强场下以长度规范非微扰时间演化直接获得含高阶谐波成分的电流、绕开微扰展开阶数限制，长度规范方程显含带间相位积累、偶极诱导跃迁、带内加速（iF·∇k）与唯象退相四项，Houston 基形式确立为强场下布居与相干演化的标准框架（各 k 点方程解耦便于并行，配合 FFT 插值矩阵元后计算量可与稳态基相当，且已有并行开源实现），演化带间极化与载流子布居（含自旋与谷分辨），统一描述带间极化—带内电流耦合与退相干，定量分解带内/带间电流以实现固体 HHG 机制归属、偏振—自旋/谷极化映射、T2/γ(k) 假设检验与低次谐波峰位归属（数百次波长扫描逐一定位

### [[methods/统一Hamiltonian框架的rt-TDDFT|统一Hamiltonian框架的rt-TDDFT]]
页：knowledge/wiki/methods/统一Hamiltonian框架的rt-TDDFT.md
摘要：统一Hamiltonian框架的rt-TDDFT通过实时传播含时Kohn-Sham/TDSE方程追踪强场电子动力学，通道完备性要点依然成立——实时传播Kohn-Sham轨道直接给出含时宏观电流的傅里叶谱，带内与带间HHG发射通道同时天然包含而无需通道分离假设（第一性原理同时含带内与带间电流，全谱量化键长-截止能量关系，避免紧束缚/两带模型对能带结构的简化误差）；Floquet拓扑分支——TDDFT含时模拟在双色（ω–2ω）圆偏振强场下第一性原理重现光修饰能带结构与光电子谱，区分Floquet杂化隙与多光子边带贡献；交错磁自旋动力学分支——RT-TDDFT直接模拟线偏激光脉冲下RuO2飞秒自旋动力学，给出光致净磁化约0.2 μB/晶胞；二维全光磁控分支——实时TDDFT直接给出强场下自旋/磁矩与光电流的逐时刻微观演化，作为二维材料面内光控磁态与全光磁控验证的第一性原理工具；频率混合谱学分支—

### [[methods/半经典动力学方程贝里曲率反常速度|半经典动力学方程（贝里曲率反常速度项）]]
页：knowledge/wiki/methods/半经典动力学方程贝里曲率反常速度.md
摘要：半经典波包动力学中，贝里曲率通过反常速度项 v_anom=(e/ħ)E×Ω(k) 将瞬态电流映射为非平衡占据上的Berry曲率加权积分，是绝热霍尔响应的标准框架；新证据进一步表明，该方程在贝里曲率热点的非绝热区失效，需引入贝里曲率的普适延拓来描述非绝热霍尔效应。  ## 参数表  **联网检索升级**（2026-11-01，引用已核实）：半经典波包动力学方程组（Xiao–Chang–Niu RMP 2010 综述标准形式）——**$\dot{r} = (1/\hbar)∂ε_n/∂k − \dot{k}×Ω_n(k)$**（群速度 + 反常速度）、**$\hbar\dot{k} = −eE − e\dot{r}×B$**（加速度定理 + Lorentz）——Berry 曲率以反常速度进入输运与光学响应，是带内 HHG 通道几何依赖的解析来源。二阶半经典玻尔兹曼在此基础上加散射项做非线性输运

### [[methods/TDSE求解器|TDSE求解器]]
页：knowledge/wiki/methods/TDSE求解器.md
摘要：TDSE求解器通过数值求解含时薛定谔方程给出强场体系的第一性原理响应：既作为深度学习正/逆网络的物理引擎批量生成带物理标签训练集（单活性电子TDSE生成脉冲参数-光电子动量谱数据对），又作为机器学习仿真器的真值与训练数据来源提供量子动力学样本供仿真器学习，并在贝叶斯参数估计中充当似然函数的物理内核、把待估参数映射为时间分辨可观测量供与数据比对，还作为量子计量学基准验证SFA框架Fisher信息结论、与SFA量子轨迹联用验证电子波包干涉并提取势垒下电离轨迹参数；在量子光HHG方向经TDSE/SFA校验确立偶次谐波幅值对2ω场强的线性标度（源于微扰展开与选择律，论证性外推至库仑修正与固体HHG），支撑BSV双色驱动下高斯纠缠谐波态与量子隐形传态优势边界的解析刻画，且量子化BSV驱动场模型表明谐波偶极辐射继承驱动场压缩与关联结构、是Wigner负性出现的根源；在含库仑（模型）势模拟中作为真值已知

### [[methods/含时密度泛函_TDDFT_方法|含时密度泛函（TDDFT）方法]]
页：knowledge/wiki/methods/含时密度泛函_TDDFT_方法.md
摘要： TDDFT 直接计算晶体在强场下的含时电流，可从头算给出谐波产额及角分布，并能描述层间耦合和莫尔势而无需经验参数；其计算成本随莫尔原胞原子数急剧上升，当前只适合莫尔周期较小、扭转角较大的构型。  ## 参数表  **canonical 升级**（2026-11-01，教科书级方法要素，引用已核实）： 见 [[DFT计算]] 的 TDDFT 段：Runge–Gross 定理（1984）保证含时密度-外势一一对应，TDKS 方程实时传播给出强场响应。本页为其方法卡：两种模式（线性响应 Casida / 实时 RT-TDDFT）、绝热近似误差源、传播子选择（Magnus/CN/时间反演对称）。  

### [[methods/floquet-engineering|floquet-engineering]]
页：knowledge/wiki/methods/floquet-engineering.md
摘要：Floquet工程以周期光场将固体哈密顿量化为Floquet-Bloch准能级与边带，其严格基础是Sambe扩展希尔伯特空间中把时间作为坐标的 K = H(t) − i∂_t 本征问题（给出准能量谱与周期性本征射线并作为绝热展开的严格基，该扩展空间静态本征问题表示还支持逐准能隙含反常π能隙的绕数/动态不变量拓扑分析、判定对称性约束破缺并区分无静态对应的驱动诱导边界态），将该Sambe扩展推进到BdG哈密顿量的光子扇区可精确加倍Cooper对关联流形（对称性加倍机制）并在Sigrist-Ueda/Balian-Werthamer自旋-宇称分类中新增Floquet频率宇称量子数、预言奇频-奇宇称-轨道单重态新配对通道及Floquet Majorana平带，高频非共振时Floquet-Magnus/van Vleck/Floquet-Schrieffer-Wolff展开可将其约化为时间平均的静态

## 二、带方法卡的论文页（6）

### [[papers/2026-2607_17265-first-principles-electron-phonon-scattering-in-real-time-tdd|耗散实时 TDDFT：自能碰撞积分（Born–Markov）嵌入实时传播的第一性原理电子-声子散射]]
页：knowledge/wiki/papers/2026-2607_17265-first-principles-electron-phonon-scattering-in-real-time-tdd.md

### [[papers/2609.20085|SBE-鞍点统一框架（半导体布洛赫方程 + 鞍点近似描述固体 HHG）]]
页：knowledge/wiki/papers/2609.20085.md
参数样例：参数；---；均匀退相干时间 T2（谱线拟合值）；闭式解中的退相干因子

### [[papers/2026-2510_16546-high-harmonic-generation-light-source-with-polariz|偏振可编程 HHG 光源（多材料筛选：TMDC/拓扑绝缘体/外延双层石墨烯 + SHG/MIR 双驱动）]]
页：knowledge/wiki/papers/2026-2510_16546-high-harmonic-generation-light-source-with-polariz.md
参数样例：参数；---；材料；激光

### [[papers/2025-2511_18362-attosecond-resolved-quantum-fluctuations-of-light-and-matter|BSV 微扰双色 HHG：单发光子统计 + 原位四缝干涉量子态层析 + 隧穿涨落阿秒分辨]]
页：knowledge/wiki/papers/2025-2511_18362-attosecond-resolved-quantum-fluctuations-of-light-and-matter.md
参数样例：参数；---；驱动构型；对称性关系

### [[papers/2610.15251|EFT 分层 Hamilton 族 H_λ（可调 trigonal warping 的谷分辨 HHG 探针框架）]]
页：knowledge/wiki/papers/2610.15251.md
参数样例：参数；---；warping 耦合 λ；EFT 展开参数 x=λa_cc·A_0

### [[papers/2025-2508_00296-tracking-doublon-holon-dynamics-in-high-harmonic-generation|Sr₂CuO₃ Mott 绝缘体 HHG 中 doublon-holon 动力学的亚周期追踪（反射 HHG + tr-反射 + tdDMFT/NCA）]]
页：knowledge/wiki/papers/2025-2508_00296-tracking-doublon-holon-dynamics-in-high-harmonic-generation.md
参数样例：参数；---；MIR；tdDMFT 参数
