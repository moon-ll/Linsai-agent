# 课题方法素材包（KB 自动聚合，v7.2.30 wikilink 节点格式）

- 课题：general-ssh-weyl-20260920
- 生成时间：2026-11-16T15:42:02Z
- 方法关键词：Berry、HHG、SBE、TDSE、与量子光物态探测、中信号消失的方法、信号三类可观测量、呈现各向异性光谱、圆二色性光谱、强场高次谐波谱学、拟采用技术、曲率反演方法、的拓扑量子数探测、硅的温度依赖测量

> 用途：update_method_manual / writer 写方案时的可实施细节来源。
> **v7.2.30 起改 wikilink 节点格式**：每条方法/参数都附 `[[方法页slug]]` 双向链接，
> writer 落盘后由 `kb_pack_wikilink_guard.py` 校验（≥3 引用为达标）。
> 参数必须按参数溯源纪律标注来源；本包为 KB 索引摘要，取参数前读对应页原文。

## 〇、方法专题（6，谱系/选型层）

### [[method-topics/HHG反演方法学|HHG 反演方法学（贝叶斯推断 / 神经网络正则化 / 约束优化）]]
页：knowledge/wiki/method-topics/HHG反演方法学.md
专题定位：从谐波谱反推凝聚态参数（能带色散、跃迁偶极、退相干时间、Berry 曲率、

### [[method-topics/固体HHG数值计算方法体系|固体 HHG 数值计算方法体系（TDSE / SBE / rt-TDDFT / 紧束缚）]]
页：knowledge/wiki/method-topics/固体HHG数值计算方法体系.md
专题定位：强激光入射晶体后谐波谱的数值预言方法——四套范式的理论原理、

### [[method-topics/材料体系HHG方法|材料体系 HHG 方法（Weyl 半金属 / 交变磁体 / moiré / 高阶拓扑）]]
页：knowledge/wiki/method-topics/材料体系HHG方法.md
专题定位：四类量子材料的 HHG 指纹、模型栈与判据——每类材料「用什么模型、

### [[method-topics/强场电离量子轨道方法|强场电离量子轨道方法（SFA / CQSFA / Q-CCSFA）]]
页：knowledge/wiki/method-topics/强场电离量子轨道方法.md
专题定位：强场电离与再碰撞过程的半经典量子轨道方法谱系——从 Keldysh 理论到

### [[method-topics/激子与多体效应方法|激子与多体效应方法（exciton / doublon-holon / tdDMFT）]]
页：knowledge/wiki/method-topics/激子与多体效应方法.md
专题定位：关联效应对 HHG 的修正与利用——激子共振、Mott 体系 doublon-holon

### [[method-topics/量子光驱动HHG方法|量子光驱动 HHG 方法（BSV / 压缩光 / 输出态层析）]]
页：knowledge/wiki/method-topics/量子光驱动HHG方法.md
专题定位：以非经典光场（亮压缩真空 BSV、压缩态）驱动的 HHG——谐波光的

## 一、匹配的知识库方法页（8）

### [[methods/固体_HHG_理论四路线_SBE___TDDFT___Wannier-Bloch___规范处理|固体 HHG 理论四路线（SBE / TDDFT / Wannier-Bloch / 规范处理）]]
页：knowledge/wiki/methods/固体_HHG_理论四路线_SBE___TDDFT___Wannier-Bloch___规范处理.md
摘要： SBE 在能带色散局部抛物近似下给出截止标度律，把能带、电流与再碰撞相位联系起来；TDDFT 直接计算强场含时电流、对层间耦合与莫尔势不依赖经验参数，但仅适用莫尔周期小（大扭转角）构型；Wannier-Bloch 轨迹把倒空间几何约束直接对应到谐波阶次与倒空间轨迹长度；Berry 连接规范处理以 London/Coulomb 规范差值检验规范不变性。局限：四条路线均只描述理想晶体，扭转角 + 激子预激发 + 层间传播共同作用下的可检验映射尚无单一路线给出，多体修正须作为参数输入耦合项。  <!-- linsai-wikilinks --> ## 关联概念  - [[TDDFT]] - [[层

### [[methods/sbe-bloch-equations|sbe-bloch-equations]]
页：knowledge/wiki/methods/sbe-bloch-equations.md
摘要：半导体布洛赫方程（k 空间含时密度矩阵传播，Houston 基或长度/Wannier 规范，亦可实现为含时紧束缚+密度矩阵模拟，属 TDSE/密度矩阵/TDDFT 三类固体 HHG 模拟中的密度矩阵类，定位上桥接解析模型与 TDDFT 的中间强度区）在强场下以长度规范非微扰时间演化直接获得含高阶谐波成分的电流、绕开微扰展开阶数限制，长度规范方程显含带间相位积累、偶极诱导跃迁、带内加速（iF·∇k）与唯象退相四项，Houston 基形式确立为强场下布居与相干演化的标准框架（各 k 点方程解耦便于并行，配合 FFT 插值矩阵元后计算量可与稳态基相当，且已有并行开源实现），演化带间极化与载流子布居（含自旋与谷分辨），统一描述带间极化—带内电流耦合与退相干，定量分解带内/带间电流以实现固体 HHG 机制归属、偏振—自旋/谷极化映射、T2/γ(k) 假设检验与低次谐波峰位归属（数百次波长扫描逐一定位

### [[methods/TDSE求解器|TDSE求解器]]
页：knowledge/wiki/methods/TDSE求解器.md
摘要：TDSE求解器通过数值求解含时薛定谔方程给出强场体系的第一性原理响应：既作为深度学习正/逆网络的物理引擎批量生成带物理标签训练集（单活性电子TDSE生成脉冲参数-光电子动量谱数据对），又作为机器学习仿真器的真值与训练数据来源提供量子动力学样本供仿真器学习，并在贝叶斯参数估计中充当似然函数的物理内核、把待估参数映射为时间分辨可观测量供与数据比对，还作为量子计量学基准验证SFA框架Fisher信息结论、与SFA量子轨迹联用验证电子波包干涉并提取势垒下电离轨迹参数；在量子光HHG方向经TDSE/SFA校验确立偶次谐波幅值对2ω场强的线性标度（源于微扰展开与选择律，论证性外推至库仑修正与固体HHG），支撑BSV双色驱动下高斯纠缠谐波态与量子隐形传态优势边界的解析刻画，且量子化BSV驱动场模型表明谐波偶极辐射继承驱动场压缩与关联结构、是Wigner负性出现的根源；在含库仑（模型）势模拟中作为真值已知

### [[methods/自发反常霍尔效应测量|自发反常霍尔效应测量]]
页：knowledge/wiki/methods/自发反常霍尔效应测量.md
摘要：在零净磁化条件下测量贝里曲率驱动的横向电输运响应，作为交错磁对称破缺的电学指纹；反常霍尔信号是 Berry 曲率对占据态动量积分的宏观读出，可通过应变调控直接探测拓扑响应的演化。  ## 参数表  **联网检索升级**（2026-11-01，引用已核实）：半经典波包动力学方程组（Xiao–Chang–Niu RMP 2010 综述标准形式）——**$\dot{r} = (1/\hbar)∂ε_n/∂k − \dot{k}×Ω_n(k)$**（群速度 + 反常速度）、**$\hbar\dot{k} = −eE − e\dot{r}×B$**（加速度定理 + Lorentz）——Berry 曲率以反常速度进入输运与光学响应，是带内 HHG 通道几何依赖的解析来源。二阶半经典玻尔兹曼在此基础上加散射项做非线性输运。  | 要素 | 公式 | 出处 | | --- | --- | --- | |

### [[methods/Wannier-Bloch_轨迹方法|Wannier-Bloch 轨迹方法]]
页：knowledge/wiki/methods/Wannier-Bloch_轨迹方法.md
摘要： > ⚠ **状态标注（2026-11-01 颗粒度体检）**：本页正文素材不足以支撑「参数表≥5行」的达标线（指导学生复现），如实保持低密度工作页状态，待深读素材回补后升级。已在专题关联网络中。 在电子轨迹中显式引入 Berry 连接和具有动量依赖的跃迁矩阵元，将倒空间几何对选择定则的约束映射到谐波阶次及倒空间轨迹长度，适用于 5—15 阶的逐阶分析。  ## 参数表  **终极升级**（2026-11-01，canonical 要素，引用已核实/库内锚）： Wannier–Bloch 轨迹方法：在倾斜/强场晶格中以 Wannier–Bloch 态（位置依赖布洛赫能量的局域基）传播波包，轨迹

### [[methods/半经典动力学方程贝里曲率反常速度|半经典动力学方程（贝里曲率反常速度项）]]
页：knowledge/wiki/methods/半经典动力学方程贝里曲率反常速度.md
摘要：半经典波包动力学中，贝里曲率通过反常速度项 v_anom=(e/ħ)E×Ω(k) 将瞬态电流映射为非平衡占据上的Berry曲率加权积分，是绝热霍尔响应的标准框架；新证据进一步表明，该方程在贝里曲率热点的非绝热区失效，需引入贝里曲率的普适延拓来描述非绝热霍尔效应。  ## 参数表  **联网检索升级**（2026-11-01，引用已核实）：半经典波包动力学方程组（Xiao–Chang–Niu RMP 2010 综述标准形式）——**$\dot{r} = (1/\hbar)∂ε_n/∂k − \dot{k}×Ω_n(k)$**（群速度 + 反常速度）、**$\hbar\dot{k} = −eE − e\dot{r}×B$**（加速度定理 + Lorentz）——Berry 曲率以反常速度进入输运与光学响应，是带内 HHG 通道几何依赖的解析来源。二阶半经典玻尔兹曼在此基础上加散射项做非线性输运

### [[methods/二阶半经典玻尔兹曼非线性输运|二阶半经典玻尔兹曼非线性输运]]
页：knowledge/wiki/methods/二阶半经典玻尔兹曼非线性输运.md
摘要：半经典玻尔兹曼输运方程按电场幂次微扰展开：展开至二阶时得到纵向非互易电流与直流整流电压（可用于两端器件的读出信号估算），并将（层分辨的）贝里曲率偶极映射为各层方向相反的二阶霍尔电流，给出非线性层霍尔电导的解析表达及其弛豫时间、门电压依赖；展开至更高阶时，三阶电导可解析地关联到量子度规偶极矩与四极矩的费米面积分，从而把非线性输运系数与能带量子几何量直接联系起来。  ## 参数表  **联网检索升级**（2026-11-01，引用已核实）：半经典波包动力学方程组（Xiao–Chang–Niu RMP 2010 综述标准形式）——**$\dot{r} = (1/\hbar)∂ε_n/∂k − \dot{k}×Ω_n(k)$**（群速度 + 反常速度）、**$\hbar\dot{k} = −eE − e\dot{r}×B$**（加速度定理 + Lorentz）——Berry 曲率以反常速度进入输运

### [[methods/半导体布洛赫方程_SBE_框架|半导体布洛赫方程（SBE）框架]]
页：knowledge/wiki/methods/半导体布洛赫方程_SBE_框架.md
摘要： 固体 HHG 理论描述的第一条解析路线：把能带、电流与再碰撞相位联系起来，奠定带间极化与截止阶次的解析基础；在能带色散局部抛物近似下给出截止阶次标度律，已在大带隙半导体 ZnO 等体系中被实验观测。  <!-- linsai-wikilinks --> ## 关联概念  - [[固体HHG]] - [[截止阶次标度律]] <!-- /linsai-wikilinks --> 

## 二、带方法卡的论文页（6）

### [[papers/2024-2304_11661-laser-field-strength-dependence-of-solid-high-harmonic-gener|掺杂体系固态 HHG 的激光场强依赖 TDSE 分析（阈值反转判据）]]
页：knowledge/wiki/papers/2024-2304_11661-laser-field-strength-dependence-of-solid-high-harmonic-gener.md
参数样例：参数；---；增强反转阈值

### [[papers/2026-2607_17265-first-principles-electron-phonon-scattering-in-real-time-tdd|耗散实时 TDDFT：自能碰撞积分（Born–Markov）嵌入实时传播的第一性原理电子-声子散射]]
页：knowledge/wiki/papers/2026-2607_17265-first-principles-electron-phonon-scattering-in-real-time-tdd.md

### [[papers/2610.15251|EFT 分层 Hamilton 族 H_λ（可调 trigonal warping 的谷分辨 HHG 探针框架）]]
页：knowledge/wiki/papers/2610.15251.md
参数样例：参数；---；warping 耦合 λ；EFT 展开参数 x=λa_cc·A_0

### [[papers/2503.14531|Van Vleck 传播子强场近似（Van Vleck-propagator SFA，含边界与镜像势的 MIM 结强场输运模型）]]
页：knowledge/wiki/papers/2503.14531.md
参数样例：参数；---；zeta 参数（纳米结尺寸判据）；Herink 空间受限长度参数 δ

### [[papers/2609.20085|SBE-鞍点统一框架（半导体布洛赫方程 + 鞍点近似描述固体 HHG）]]
页：knowledge/wiki/papers/2609.20085.md
参数样例：参数；---；均匀退相干时间 T2（谱线拟合值）；闭式解中的退相干因子

### [[papers/1704.06218|固体 HHG 非绝热效应理论：k 空间阶梯式导带激发（发射延迟 → 高平台红移 + 中心对称晶格偶次谐波 k 空间轨迹破缺 + 不对称系数 A(N) 定量指标 + 脉冲长度为干净对照旋钮）]]
页：knowledge/wiki/papers/1704.06218.md
参数样例：参数；---；模型与参数；通道计数
