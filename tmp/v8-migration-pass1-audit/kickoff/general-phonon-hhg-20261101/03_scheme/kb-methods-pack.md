# 课题方法素材包（KB 自动聚合，v7.2.30 wikilink 节点格式）

- 课题：general-phonon-hhg-20261101
- 生成时间：2026-11-16T15:42:03Z
- 方法关键词：Berry、DFT、DMFT、HHG、TDDFT、THz、中用高次谐波光谱、因而可被直接探测、坐标是被主动泵浦、增强屏蔽以及泵浦、声子泵浦、幅与相位可用泵浦、式选择的声子泵浦、引入带来一个方法

> 用途：update_method_manual / writer 写方案时的可实施细节来源。
> **v7.2.30 起改 wikilink 节点格式**：每条方法/参数都附 `[[方法页slug]]` 双向链接，
> writer 落盘后由 `kb_pack_wikilink_guard.py` 校验（≥3 引用为达标）。
> 参数必须按参数溯源纪律标注来源；本包为 KB 索引摘要，取参数前读对应页原文。

## 〇、方法专题（6，谱系/选型层）

### [[method-topics/固体HHG数值计算方法体系|固体 HHG 数值计算方法体系（TDSE / SBE / rt-TDDFT / 紧束缚）]]
页：knowledge/wiki/method-topics/固体HHG数值计算方法体系.md
专题定位：强激光入射晶体后谐波谱的数值预言方法——四套范式的理论原理、

### [[method-topics/激子与多体效应方法|激子与多体效应方法（exciton / doublon-holon / tdDMFT）]]
页：knowledge/wiki/method-topics/激子与多体效应方法.md
专题定位：关联效应对 HHG 的修正与利用——激子共振、Mott 体系 doublon-holon

### [[method-topics/HHG反演方法学|HHG 反演方法学（贝叶斯推断 / 神经网络正则化 / 约束优化）]]
页：knowledge/wiki/method-topics/HHG反演方法学.md
专题定位：从谐波谱反推凝聚态参数（能带色散、跃迁偶极、退相干时间、Berry 曲率、

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

### [[methods/统一Hamiltonian框架的rt-TDDFT|统一Hamiltonian框架的rt-TDDFT]]
页：knowledge/wiki/methods/统一Hamiltonian框架的rt-TDDFT.md
摘要：统一Hamiltonian框架的rt-TDDFT通过实时传播含时Kohn-Sham/TDSE方程追踪强场电子动力学，通道完备性要点依然成立——实时传播Kohn-Sham轨道直接给出含时宏观电流的傅里叶谱，带内与带间HHG发射通道同时天然包含而无需通道分离假设（第一性原理同时含带内与带间电流，全谱量化键长-截止能量关系，避免紧束缚/两带模型对能带结构的简化误差）；Floquet拓扑分支——TDDFT含时模拟在双色（ω–2ω）圆偏振强场下第一性原理重现光修饰能带结构与光电子谱，区分Floquet杂化隙与多光子边带贡献；交错磁自旋动力学分支——RT-TDDFT直接模拟线偏激光脉冲下RuO2飞秒自旋动力学，给出光致净磁化约0.2 μB/晶胞；二维全光磁控分支——实时TDDFT直接给出强场下自旋/磁矩与光电流的逐时刻微观演化，作为二维材料面内光控磁态与全光磁控验证的第一性原理工具；频率混合谱学分支—

### [[methods/PIMD___rt-TDDFT_模拟液态水核量子_HHG|PIMD + rt-TDDFT 模拟液态水核量子 HHG]]
页：knowledge/wiki/methods/PIMD___rt-TDDFT_模拟液态水核量子_HHG.md
摘要：基于**电子-核时间尺度分离**（激光驱动仅几 fs，核运动可忽略；液结构涨落为百 fs–ps）将量子核统计与超快电子动力学**显式解耦**：  1. **PIMD 构型采样**：用 PIGLET 加速的路径积分分子动力学采样含核量子离域（零点运动）的液态水构型系综； 2. **frozen-ion 快照传播**：每个构型作为冻结核快照，实时 TDDFT 传播强场下的电子动力学，逐快照计算 HHG 谱； 3. **系综平均**：对系综平均得宏观谱。该分离同时冻结了电声耦合的动力学部分，使液结构对超快动力学的影响可被单独检验。  **配套诊断协议**（本方法的方法论增量）：  - **相干/非相干谱分解**：S(ω)=|⟨I_k⟩|² 与 S_in(ω)=⟨|I_k|⟩² 的偏离直接量化跨快照相干性，配合复相位箱线图——无需演化密度矩阵即可把 dephasing 归因于液结构统计平均； -

### [[methods/含时密度泛函_TDDFT_方法|含时密度泛函（TDDFT）方法]]
页：knowledge/wiki/methods/含时密度泛函_TDDFT_方法.md
摘要： TDDFT 直接计算晶体在强场下的含时电流，可从头算给出谐波产额及角分布，并能描述层间耦合和莫尔势而无需经验参数；其计算成本随莫尔原胞原子数急剧上升，当前只适合莫尔周期较小、扭转角较大的构型。  ## 参数表  **canonical 升级**（2026-11-01，教科书级方法要素，引用已核实）： 见 [[DFT计算]] 的 TDDFT 段：Runge–Gross 定理（1984）保证含时密度-外势一一对应，TDKS 方程实时传播给出强场响应。本页为其方法卡：两种模式（线性响应 Casida / 实时 RT-TDDFT）、绝热近似误差源、传播子选择（Magnus/CN/时间反演对称）。  

### [[methods/SALMON_rt-TDDFT___Williams-Lax|salmon-williams-lax]]
页：knowledge/wiki/methods/SALMON_rt-TDDFT___Williams-Lax.md
摘要：威廉斯–拉克斯（Williams–Lax）均匀半经典近似给出强场带间跃迁/弗朗兹–凯尔迪什吸收的解析速率；新证据确立其时间域推广（Yamada & Yabana，基于 SALMON 实时 TDDFT）——把电子–声子退相化为冻结的热+零点核构型响应的统计平均（实践上单发构型即可、无需系综平均），金属中自然涌现 ~10 fs Drude 阻尼、介质中不引入经验 T2 即得干净高次谐波谱，且超胞动力学映射回原胞密度矩阵表明退相主要由对角布居动力学而非非对角相干衰减主导，可作为该半经典方法移植与第一性原理基准检验的现成平台。  ## 参数表  | 参数 | 数值 | 出处 | | --- | --- | --- | | 金属(Al) Drude 弛豫时间 τ | ~10 fs | 2607.17109 | | 热无序温度（含热运动与零点运动） | 300 K | 2607.17109 | | 超

### [[methods/B-spline_TDDFT_计算场自由_EWS_时延|B-spline TDDFT 计算场自由 EWS 时延]]
页：knowledge/wiki/methods/B-spline_TDDFT_计算场自由_EWS_时延.md
摘要：方法栈（以 [[1407.6613]] 为基准实现）：  1. **束缚态**：Hartree–Fock 自洽场；**连续态**：HF frozen-core + 散射相位 δ(ℓ,k)（Coulomb 相移 η + 短程修正）； 2. **电子关联**：RPAE（含交换随机相位近似）——自洽积分方程求约化偶极矩阵元，保留 time-forward 极点相位 φ^RPAE； 3. **光电子波包**：分波展开 Ψ(k,t)=Σℓ cℓ R(ε,ℓ)Y(ℓ,m)，矩阵元 D_k 闭式表达； 4. **对照**：3D TDSE 数值传播（优化单粒子势 + 矩阵迭代法，球谐展开）； 5. **EWS/Wigner 时延**：**τ_W = ℏ ∂arg(D_k)/∂ε**，对 XUV 谱密度加权能量平均，再对发射角 θ_k 角分辨。  关键物理：分波干涉的角向零点（如 P₂(cos θ) 在 ±

### [[methods/含时密度泛函_TDDFT_路线|含时密度泛函（TDDFT）路线]]
页：knowledge/wiki/methods/含时密度泛函_TDDFT_路线.md
摘要： 第二条路线：直接计算晶体在强场下的含时电流，给出从头算层面的产额与角分布，对层间耦合与莫尔势的描述不依赖经验参数；局限是计算成本随莫尔原胞原子数急剧上升，目前仅适用于莫尔周期小（大扭转角）的构型。  <!-- linsai-wikilinks --> ## 关联概念  - [[层间耦合]] <!-- /linsai-wikilinks --> 

### [[methods/实时_DMFT_与中红外强场实验联合分析|实时 DMFT 与中红外强场实验联合分析]]
页：knowledge/wiki/methods/实时_DMFT_与中红外强场实验联合分析.md
摘要： > ⚠ **状态标注（2026-11-01 颗粒度体检）**：本页正文素材不足以支撑「参数表≥5行」的达标线（指导学生复现），如实保持低密度工作页状态，待深读素材回补后升级。已在专题关联网络中。 将中红外强场实验与实时 DMFT 结合，用于识别亚周期 Mott 熔化、高阶谐波红移及 doublon-holon 复合激发引起的瞬时能带重整。  ## 参数表  **终极升级**（2026-11-01，canonical 要素，引用已核实/库内锚）： 实时 DMFT（tdDMFT）与中红外强场实验的联合分析：tdDMFT 把强关联晶格映射为含时自洽杂质问题，直接预言中红外驱动的 Mott 体系谐波

## 二、带方法卡的论文页（6）

### [[papers/2026-2607_28491-drumhead-surface-states-of-rhombohedral-graphite-with-near-i|菱方石墨鼓面态近理想量子几何的第一性原理核验（DFT+Wannier+Wilson loop+Kubo QGT 空间分辨）]]
页：knowledge/wiki/papers/2026-2607_28491-drumhead-surface-states-of-rhombohedral-graphite-with-near-i.md
参数样例：参数；---；计算设置；DSS 曲率定量

### [[papers/2025-2508_00296-tracking-doublon-holon-dynamics-in-high-harmonic-generation|Sr₂CuO₃ Mott 绝缘体 HHG 中 doublon-holon 动力学的亚周期追踪（反射 HHG + tr-反射 + tdDMFT/NCA）]]
页：knowledge/wiki/papers/2025-2508_00296-tracking-doublon-holon-dynamics-in-high-harmonic-generation.md
参数样例：参数；---；MIR；tdDMFT 参数

### [[papers/2026-2601_02481-an-altermagnetic-materials-library-in-intercalated-transitio|插层过渡金属双硫属化物交变磁材料库的系统 DFT 筛选（T_yMX₂：VASP PBE+U+D3+对称性判据）]]
页：knowledge/wiki/papers/2026-2601_02481-an-altermagnetic-materials-library-in-intercalated-transitio.md
参数样例：参数；---；DFT 设置；筛选空间

### [[papers/2609.20085|SBE-鞍点统一框架（半导体布洛赫方程 + 鞍点近似描述固体 HHG）]]
页：knowledge/wiki/papers/2609.20085.md
参数样例：参数；---；均匀退相干时间 T2（谱线拟合值）；闭式解中的退相干因子

### [[papers/2026-2505_13415-optical-signatures-of-bulk-g-wave-altermagnetism-in-mnte|MnTe 体 g 波交变磁性光学签名（ELK LAPW+U + 布居速率方程 + S_exc(α) 分解为 d/g 波样）]]
页：knowledge/wiki/papers/2026-2505_13415-optical-signatures-of-bulk-g-wave-altermagnetism-in-mnte.md
参数样例：参数；---；DFT 设置；脉冲参数

### [[papers/2026-2607_17265-first-principles-electron-phonon-scattering-in-real-time-tdd|耗散实时 TDDFT：自能碰撞积分（Born–Markov）嵌入实时传播的第一性原理电子-声子散射]]
页：knowledge/wiki/papers/2026-2607_17265-first-principles-electron-phonon-scattering-in-real-time-tdd.md
