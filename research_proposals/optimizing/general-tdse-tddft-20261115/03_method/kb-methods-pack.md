# 课题方法素材包（KB 自动聚合，v7.2.30 wikilink 节点格式）

- 课题：general-tdse-tddft-20261115
- 生成时间：2026-11-20T11:41:03Z
- 方法关键词：COLTRIMS、TDDFT、TDSE、与参数到可观测量、两者的计算、信息计算、把传统方法、拟采用技术、用什么装置、的像素网格与探测、真值谱计算、量谱这类可观测量、须先给出预研方法

> 用途：update_method_manual / writer 写方案时的可实施细节来源。
> **v7.2.30 起改 wikilink 节点格式**：每条方法/参数都附 `[[方法页slug]]` 双向链接，
> writer 落盘后由 `kb_pack_wikilink_guard.py` 校验（≥3 引用为达标）。
> 参数必须按参数溯源纪律标注来源；本包为 KB 索引摘要，取参数前读对应页原文。

## 〇、方法专题（5，谱系/选型层）

### [[method-topics/固体HHG数值计算方法体系|固体 HHG 数值计算方法体系（TDSE / SBE / rt-TDDFT / 紧束缚）]]
页：knowledge/wiki/method-topics/固体HHG数值计算方法体系.md
专题定位：强激光入射晶体后谐波谱的数值预言方法——四套范式的理论原理、

### [[method-topics/强场电离量子轨道方法|强场电离量子轨道方法（SFA / CQSFA / Q-CCSFA）]]
页：knowledge/wiki/method-topics/强场电离量子轨道方法.md
专题定位：强场电离与再碰撞过程的半经典量子轨道方法谱系——从 Keldysh 理论到

### [[method-topics/HHG反演方法学|HHG 反演方法学（贝叶斯推断 / 神经网络正则化 / 约束优化）]]
页：knowledge/wiki/method-topics/HHG反演方法学.md
专题定位：从谐波谱反推凝聚态参数（能带色散、跃迁偶极、退相干时间、Berry 曲率、

### [[method-topics/阿秒计量方法体系|阿秒计量方法体系（条纹术 / RABBITT / Wigner 时延）]]
页：knowledge/wiki/method-topics/阿秒计量方法体系.md
专题定位：阿秒时间信息提取的两大实验范式（streaking / RABBITT）与其

### [[method-topics/激子与多体效应方法|激子与多体效应方法（exciton / doublon-holon / tdDMFT）]]
页：knowledge/wiki/method-topics/激子与多体效应方法.md
专题定位：关联效应对 HHG 的修正与利用——激子共振、Mott 体系 doublon-holon

## 一、匹配的知识库方法页（8）

### [[methods/统一Hamiltonian框架的rt-TDDFT|统一Hamiltonian框架的rt-TDDFT]]
页：knowledge/wiki/methods/统一Hamiltonian框架的rt-TDDFT.md
摘要：统一Hamiltonian框架的rt-TDDFT通过实时传播含时Kohn-Sham/TDSE方程追踪强场电子动力学，通道完备性要点依然成立——实时传播Kohn-Sham轨道直接给出含时宏观电流的傅里叶谱，带内与带间HHG发射通道同时天然包含而无需通道分离假设（第一性原理同时含带内与带间电流，全谱量化键长-截止能量关系，避免紧束缚/两带模型对能带结构的简化误差）；Floquet拓扑分支——TDDFT含时模拟在双色（ω–2ω）圆偏振强场下第一性原理重现光修饰能带结构与光电子谱，区分Floquet杂化隙与多光子边带贡献；交错磁自旋动力学分支——RT-TDDFT直接模拟线偏激光脉冲下RuO2飞秒自旋动力学，给出光致净磁化约0.2 μB/晶胞；二维全光磁控分支——实时TDDFT直接给出强场下自旋/磁矩与光电流的逐时刻微观演化，作为二维材料面内光控磁态与全光磁控验证的第一性原理工具；频率混合谱学分支—

### [[methods/B-spline_TDDFT_计算场自由_EWS_时延|B-spline TDDFT 计算场自由 EWS 时延]]
页：knowledge/wiki/methods/B-spline_TDDFT_计算场自由_EWS_时延.md
摘要：方法栈（以 [[1407.6613]] 为基准实现）：  1. **束缚态**：Hartree–Fock 自洽场；**连续态**：HF frozen-core + 散射相位 δ(ℓ,k)（Coulomb 相移 η + 短程修正）； 2. **电子关联**：RPAE（含交换随机相位近似）——自洽积分方程求约化偶极矩阵元，保留 time-forward 极点相位 φ^RPAE； 3. **光电子波包**：分波展开 Ψ(k,t)=Σℓ cℓ R(ε,ℓ)Y(ℓ,m)，矩阵元 D_k 闭式表达； 4. **对照**：3D TDSE 数值传播（优化单粒子势 + 矩阵迭代法，球谐展开）； 5. **EWS/Wigner 时延**：**τ_W = ℏ ∂arg(D_k)/∂ε**，对 XUV 谱密度加权能量平均，再对发射角 θ_k 角分辨。  关键物理：分波干涉的角向零点（如 P₂(cos θ) 在 ±

### [[methods/TDSE求解器|TDSE求解器]]
页：knowledge/wiki/methods/TDSE求解器.md
摘要：TDSE求解器通过数值求解含时薛定谔方程给出强场体系的第一性原理响应：既作为深度学习正/逆网络的物理引擎批量生成带物理标签训练集（单活性电子TDSE生成脉冲参数-光电子动量谱数据对），又作为机器学习仿真器的真值与训练数据来源提供量子动力学样本供仿真器学习，并在贝叶斯参数估计中充当似然函数的物理内核、把待估参数映射为时间分辨可观测量供与数据比对，还作为量子计量学基准验证SFA框架Fisher信息结论、与SFA量子轨迹联用验证电子波包干涉并提取势垒下电离轨迹参数；在量子光HHG方向经TDSE/SFA校验确立偶次谐波幅值对2ω场强的线性标度（源于微扰展开与选择律，论证性外推至库仑修正与固体HHG），支撑BSV双色驱动下高斯纠缠谐波态与量子隐形传态优势边界的解析刻画，且量子化BSV驱动场模型表明谐波偶极辐射继承驱动场压缩与关联结构、是Wigner负性出现的根源；在含库仑（模型）势模拟中作为真值已知

### [[methods/含时密度泛函_TDDFT_方法|含时密度泛函（TDDFT）方法]]
页：knowledge/wiki/methods/含时密度泛函_TDDFT_方法.md
摘要： TDDFT 直接计算晶体在强场下的含时电流，可从头算给出谐波产额及角分布，并能描述层间耦合和莫尔势而无需经验参数；其计算成本随莫尔原胞原子数急剧上升，当前只适合莫尔周期较小、扭转角较大的构型。  ## 参数表  **canonical 升级**（2026-11-01，教科书级方法要素，引用已核实）： 见 [[DFT计算]] 的 TDDFT 段：Runge–Gross 定理（1984）保证含时密度-外势一一对应，TDKS 方程实时传播给出强场响应。本页为其方法卡：两种模式（线性响应 Casida / 实时 RT-TDDFT）、绝热近似误差源、传播子选择（Magnus/CN/时间反演对称）。  

### [[methods/固体_HHG_理论四路线_SBE___TDDFT___Wannier-Bloch___规范处理|固体 HHG 理论四路线（SBE / TDDFT / Wannier-Bloch / 规范处理）]]
页：knowledge/wiki/methods/固体_HHG_理论四路线_SBE___TDDFT___Wannier-Bloch___规范处理.md
摘要： SBE 在能带色散局部抛物近似下给出截止标度律，把能带、电流与再碰撞相位联系起来；TDDFT 直接计算强场含时电流、对层间耦合与莫尔势不依赖经验参数，但仅适用莫尔周期小（大扭转角）构型；Wannier-Bloch 轨迹把倒空间几何约束直接对应到谐波阶次与倒空间轨迹长度；Berry 连接规范处理以 London/Coulomb 规范差值检验规范不变性。局限：四条路线均只描述理想晶体，扭转角 + 激子预激发 + 层间传播共同作用下的可检验映射尚无单一路线给出，多体修正须作为参数输入耦合项。  <!-- linsai-wikilinks --> ## 关联概念  - [[TDDFT]] - [[层

### [[methods/SALMON_rt-TDDFT___Williams-Lax|salmon-williams-lax]]
页：knowledge/wiki/methods/SALMON_rt-TDDFT___Williams-Lax.md
摘要：威廉斯–拉克斯（Williams–Lax）均匀半经典近似给出强场带间跃迁/弗朗兹–凯尔迪什吸收的解析速率；新证据确立其时间域推广（Yamada & Yabana，基于 SALMON 实时 TDDFT）——把电子–声子退相化为冻结的热+零点核构型响应的统计平均（实践上单发构型即可、无需系综平均），金属中自然涌现 ~10 fs Drude 阻尼、介质中不引入经验 T2 即得干净高次谐波谱，且超胞动力学映射回原胞密度矩阵表明退相主要由对角布居动力学而非非对角相干衰减主导，可作为该半经典方法移植与第一性原理基准检验的现成平台。  ## 参数表  | 参数 | 数值 | 出处 | | --- | --- | --- | | 金属(Al) Drude 弛豫时间 τ | ~10 fs | 2607.17109 | | 热无序温度（含热运动与零点运动） | 300 K | 2607.17109 | | 超

### [[methods/COLTRIMS|COLTRIMS]]
页：knowledge/wiki/methods/COLTRIMS.md
摘要：COLTRIMS（反应显微镜/冷靶反冲离子动量谱）以冷靶与飞行时间-位置灵敏探测器对电离产生的全部带电粒子做多体符合测量，逐事件重建各碎片三维动量：既可经动量匹配/库仑爆炸反演电离瞬间的核构型（如 D2O 强场三重电离全碎片动量成像），也可通过双电子符合动量成像获得电子对动量关联谱、区分序列与非序列双电离，还可对离子-电子（如氦）做符合测量重构极化面内完整动量矢量分布，为发射角统计提供实验基础。  ## 参数表  **库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）： | BSV | 1600 nm；最高 10 µJ；四档强度 0.53/0.80/1.33/1.60×10¹⁴ W/cm² | §实验体系/BSV表征  | 相干态驱动场 | 800 nm 线偏振 | [[2610.16077]] | | BSV 场 | 1600 nm、零均值、作量子微扰 |

### [[methods/含时密度泛函_TDDFT_路线|含时密度泛函（TDDFT）路线]]
页：knowledge/wiki/methods/含时密度泛函_TDDFT_路线.md
摘要： 第二条路线：直接计算晶体在强场下的含时电流，给出从头算层面的产额与角分布，对层间耦合与莫尔势的描述不依赖经验参数；局限是计算成本随莫尔原胞原子数急剧上升，目前仅适用于莫尔周期小（大扭转角）的构型。  <!-- linsai-wikilinks --> ## 关联概念  - [[层间耦合]] <!-- /linsai-wikilinks --> 

## 二、带方法卡的论文页（6）

### [[papers/2026-2607_17265-first-principles-electron-phonon-scattering-in-real-time-tdd|耗散实时 TDDFT：自能碰撞积分（Born–Markov）嵌入实时传播的第一性原理电子-声子散射]]
页：knowledge/wiki/papers/2026-2607_17265-first-principles-electron-phonon-scattering-in-real-time-tdd.md

### [[papers/2609.20085|SBE-鞍点统一框架（半导体布洛赫方程 + 鞍点近似描述固体 HHG）]]
页：knowledge/wiki/papers/2609.20085.md
参数样例：参数；---；均匀退相干时间 T2（谱线拟合值）；闭式解中的退相干因子

### [[papers/1704.06218|固体 HHG 非绝热效应理论：k 空间阶梯式导带激发（发射延迟 → 高平台红移 + 中心对称晶格偶次谐波 k 空间轨迹破缺 + 不对称系数 A(N) 定量指标 + 脉冲长度为干净对照旋钮）]]
页：knowledge/wiki/papers/1704.06218.md
参数样例：参数；---；模型与参数；通道计数

### [[papers/2024-2408_02310-laser-induced-core-polarization-effects-in-high-order-harmon|TDDFT 系统计算激光诱导核极化对固体 HHG 的影响 + 双色泵浦-探测选择性激活内壳层通道（陆培祥组，PRA 110, 023104, 2024）]]
页：knowledge/wiki/papers/2024-2408_02310-laser-induced-core-polarization-effects-in-high-order-harmon.md
参数样例：参数；---；方法栈

### [[papers/2507.03996|GASFIR（General Approximator for Strong-Field Ionization Rates，强场电离率通用近似器）]]
页：knowledge/wiki/papers/2507.03996.md
参数样例：参数；---；可调参数总数；拟合输入电离概率

### [[papers/2026-2610_05895-bifurcation-of-laser-dressed-band-extrema-in-solid|低频强场下激光 dressed 带极值的分叉理论（瞬时 dressed 基 + Löwdin 分区 + KP 数值验证）]]
页：knowledge/wiki/papers/2026-2610_05895-bifurcation-of-laser-dressed-band-extrema-in-solid.md
参数样例：参数；---；KP 模型设置；X 点临界场
