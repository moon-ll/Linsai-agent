## 2410.01424

标题：Terahertz harmonic generation across the Mott insulator-metal transition（Prajapati, Ray, Ilyakov, Ponomaryov 等，HZDR/Fribourg/IISER Bhopal；2024-10-02；已刊 Phys. Rev. B 113, 045118 (2026)）

### 研究问题
Mott 绝缘体在 THz 激发下能否产生高次谐波——THz 光子能量仅几个 meV，比 Mott 隙（约 1 eV）低三个数量级？若能，机制是什么，跨越 Mott 绝缘体-金属转变（IMT）各相的谐波行为有何不同？中心论点：THz HHG 由低能多体相互作用驱动，且 AFM 相的谐波增强不需要光子能量与 Mott 隙相当。

### 研究背景
THz HHG 研究此前集中于 Dirac/拓扑材料与超导体（Higgs 模式探测），Mott 绝缘体在理论上和实验上均未被探索。前人 MIR 激发 Ca2RuO4（Uchida, PRL 2022）发现高阶谐波随降温反常增强，由自旋-电荷耦合解释（Murakami 等 DMFT 理论预言），但仅限光子能量可与 Mott 隙比拟的高次谐波；关联金属态 V2O3 在光学波段无 HHG。THz 频段与强关联体系低能多体激发（meV 量级）天然匹配。

### 研究方法
实验：LaNiO3/LaAlO3(100)（PM 金属）与 NdNiO3/LSAT(100)（TN≈106 K、TIM≈150 K）高质量薄膜，ELBE 加速器窄带多周期 THz 脉冲（场强约 100 kV/cm、中心频率 0.3 THz）驱动，两级 0.9 THz 带通滤波器滤除基频，2 mm ZnTe 晶体时域电光探测 THG。理论：非平衡 DMFT（NESSi 库）——AFM/绝缘相用双轨道 Hubbard 模型（U=10、J=1，NCA 求解器），金属相用单带模型（U=2.5，OCA 求解器）。

### 主要发现与核心结论
三个相均观测到 THz THG 且行为迥异：PM 金属相降温单调增强（重整化准粒子带内非线性电流与频率依赖散射率）；PM 绝缘相趋势反转（Mott 隙打开压制载流子密度）；AFM 绝缘相在 TN 以下急剧上升，~5 K 处 THG 强度比 TN 处高一个数量级以上（自旋-电荷+轨道-电荷耦合、自旋极化子形成）。幂律 I3ω∝Iω^2.68（LaNiO3）/Iω^2.42（NdNiO3），指数显著小于 3，表明非微扰区；THG 对 THz 偏振近似各向同性。DMFT 复现各相特征并表明 THz 谐波增强对所有阶数成立，无需匹配 Mott 隙宽。

### 潜在研究方向
推广至 3d-5d 过渡金属氧化物（4d/5d 中自旋轨道耦合预期参与 THz HHG）；非平衡 DMFT 向 THz 低频段下探（长时演化、数值代价高）；为强关联体系设计高效 THz 谐波源策略，把材料范围从 Dirac/拓扑材料扩展出去；以 THz HHG 作为低能多体自由度的灵敏探针。

课题引用（2026-11-12；条目 2026-11-13 重排为 [38]）：references [38]（PRB 113(4), 045118, DOI 10.1103/ydjj-xxcl，CrossRef 核验）；scheme §3.6 材料风险段——跨相变产额比取"约两个数量级"量级参照（AFM 相 5 K 相对 TN 增强逾一个量级，与 PM 绝缘相反转趋势合计跨相变量级），端点精确数值维持 2026-10-16 裁决的量级表述。


## 2606.09622

标题：Evolution of terahertz third harmonic response across rare-earth nickelate phase-diagram（Prajapati, Ilyakov, Ponomaryov, Arshad, Kumar, Sahoo, Rana, Azab, Queisser, Schützhold, Deinert；2026-06-08）

### 研究问题
THz 三次谐波（THG）响应如何在镍酸盐完整相图上演化：改变稀土种类 R、外延应变、膜厚与各向异性应变从而调节相强度与转变温度时，THG 的温度依赖如何一一对应地变化？目标是建立负电荷转移绝缘体的 THz 谐波物理并寻找增强 THz 非线性的途径。

### 研究背景
承接作者前期工作（文中 ref.[49]，即 2410.01424）在 NdNiO3/LSAT 观察到的三相分明 THG 行为，但相图调控维度尚无系统研究。RNiO3 在 ZSA 方案下属负电荷转移绝缘体，基态为 d8L 描述、带隙具 p-p 特征；Ni-O-Ni 键角随 R 原子半径增大而增大，决定 Ni-3d/O-2p 杂化与金属性，而外延应变、膜厚可再调节 TMI 与相强度。MIT 的微观机制与多相变同时发生的因果仍是开放问题。

### 研究方法
制备系列薄膜：La/Pr/Nd/SmNiO3 不同 R 组分；NdNiO3 分别生长在五种衬底上获得 -2.61%（YAlO3）、-0.45%（LaAlO3）、+1.37%（NdGaO3）、+1.58%（LSAT）、+3.38%（DyScO3）应变；10 nm 与 30 nm 膜厚对比；LaAlO3(110)/(001) 各向异性应变对比。0.3 THz 窄带脉冲驱动、测 0.9 THz 处 THG，并用 THG/FH 比值排除薄膜透射率随温度变化的影响。理论：对负电荷转移绝缘体的紧束缚模型解析计算，含键失比例（d8 S=1 与 d8L2 S=0 交替）与 AFM (1/4,1/4,1/4) 波矢序。

### 主要发现与核心结论
全绝缘薄膜（SmNiO3、NdNiO3/DyScO3）在实验分辨率内无 THG 信号；压应变（更导电）薄膜 THG 更强。尖锐 MIT 薄膜（电阻率跨转变变化 2-3 个量级）的 THG 局域极大/极小分别与 TMI、TN 精确重合；弱 MIT 薄膜的极值向低温移动，NdNiO3/YAlO3 甚至单调增强至最低温（轨道-电荷与自旋-电荷耦合压制了隙效应）。各向异性应变下沿压应变更大方向的 THG/FH 更高。理论给出：满带/空带/完全自旋极化的半满带及铁磁序均不发射谐波（Pauli 原理禁止跃迁），仅 AFM 型序允许；谐波强度品质因数为 qE·r/ω，故低频 THz 远比光学频段容易进入强场区。

### 潜在研究方向
通过电子/空穴掺杂（如 Nd0.97Ce0.03NiO3 可在低温稳定金属 AFM 相）与近/带隙光掺杂（photodoping）提高载流子密度以增强 THG 效率，尤其弥补 TIM 以下自由载流子减少；推广到 Mott-Hubbard 绝缘体、正电荷转移绝缘体及金属 AFM、绝缘 FM 等非常规物态；把 THz HG 发展为探测强关联材料多体相互作用非线性响应的常规工具。


## 2501.03650

标题：Terahertz-driven ultrafast dynamics of rare-earth nickelates by controlling only the charge degree of freedom（Prajapati, Kovalev, Ilyakov, Arshad, Dubey, Navale, Rana, Deinert；2025-01-07）

### 研究问题
强 THz 场能否只驱动镍酸盐中相互纠缠的电荷自由度、而不扰动晶格与自旋？中心论点：THz 光子可实现纯电子性、超快、局域的 Mott 绝缘体-金属转变（IMT），为解耦强关联体系基本自由度提供手段。

### 研究背景
镍酸盐 IMT 涉及电荷/自旋/轨道序与键失比例的同时转变，微观机制（位点选择性 Mott 转变）未完全理解；光致 IMT 在高 fluence 下耦合结构转变与声学声子激发，DC 场诱导 IMT 依赖局部 Joule 热且慢（需数百 ns 孵育时间并形成丝状导电通道）。THz 光子能量（meV）与低能相互作用匹配、热效应小，但 THz 场诱导的镍酸盐超快动力学此前从未被探索。

### 研究方法
THz 泵浦-光学探测（TPOP）：约 30 nm 的 LaNiO3/LaAlO3(100) 金属膜（透射几何）与 PrNiO3/NdGaO3(001) 一级 IMT 膜（TIM≈125 K，反射几何），800 nm 探测脉冲，基温 26 K/12 K，最大 THz 场强 Emax≈726 kV/cm。|ΔR|max 的场依赖用类 Zener 隧穿载流子密度公式 n=aE0·exp(−πEth/E0) 拟合；弛豫动力学用双指数/单指数拟合；系统排除了多光子吸收、共振声子激发（Nd 声子 23 meV、呼吸模 62 meV 等）与碰撞电离（需 MV/cm 量级）等替代机制。

### 主要发现与核心结论
Mott 绝缘态在阈值场 Eth≈145 kV/cm（对应 THz fluence ~0.18 mJ/cm²，明显低于光致 IMT 阈值 ~0.6 mJ/cm²）以上发生瞬时金属化，机制为价电子从 O-2p 带向 Ni-3d 上 Hubbard 带的量子隧穿并产生 doublon-holon 对；弛豫为两步：τf≈1 ps（电声热化）+ τs≈4 ps（电荷有序绝缘态恢复），且两时间常数基本不随 E0 变化——增大场强只增加隧穿载流子数目而非动能（光致 IMT 中两常数随 fluence 下降，且 THz 情形 τf 比光致大 2-3 倍）。金属态呈热电子气体行为，单指数弛豫 τ<1 ps 且随 E0 略增。两种状态下均无任何声学声子振荡特征，表明晶格自由度几乎未被扰动；40 ps 后样品仍处于亚稳金属态。

### 潜在研究方向
需开展 THz 泵浦-结构探测实验以直接确证无结构转变（本文限于篇幅未做）；纯电子、超快、局域的 THz 诱导 IMT 可用于低热耗散、微型化的光电子器件（存储、开关、调制器、神经形态计算）；THz 选择性驱动单一自由度的能力可推广至合成光-物质相互作用新物态并解析多体相互作用中各自由度的角色。


## 2512.23538

标题：Fisher information as an operational metric for structured optical beams（J. Sumaya-Martinez, J. Mulia-Rodriguez；Universidad Autónoma del Estado de México；2025-12-29 提交，v1；预印本，未见刊出版）

### 研究问题与核心结论
把 Fisher 信息用作结构光场的操作度量：将实测强度分布视为统计对象，对横向位移等物理参数定义 Fisher 信息，证明熵相近的光模式可呈现截然不同的 Fisher 信息（节点结构与局部曲率决定灵敏度），Hermite-Gaussian 模随模阶系统增强，Laguerre-Gaussian 涡旋光束与有限能量 Bessel-Gauss 光束统一纳入该判据。核心结论：Fisher 信息给出实验可及的参数估计灵敏度比较准则，可与熵描述互补。

### 与课题关联
scheme §3.4 可辨识性诊断以 Fisher 信息矩阵条件数 cond(I)=λmax/λmin<10 为接收门槛。该文把"Fisher 信息作为操作度量"的用法在光学参数估计语境下落地（强度分布对物理参数的响应），为条件数判据的"参数估计可辨识性度量"定位提供形式依据；本项目将其从光束参数估计移植到 SBE-Q 多体参数反演语境。

### 课题引用（2026-11-12）
该文于 2026-11-13 参考文献裁撤轮出列（方案改以 Cramér–Rao 下界直接论述，不再引用），笔记保留作背景研读。作者名以 arXiv 官方页为准（Sumaya-Martinez J., Mulia-Rodriguez J.）。

## 2504.02567

标题：High harmonic generation in monolayer MoS2 controlled by resonant and near-resonant pulses on ultrashort time scales（P. Peterka, A. O. Slobodeniuk, T. Novotný 等；布拉格查理大学；APL Photonics 8, 086103 (2023)，DOI: 10.1063/5.0158995；arXiv:2504.02567，2025-04-03 提交）

### 研究问题与核心结论
单层 MoS₂ 的泵浦—探测类 HHG：2000 nm（0.62 eV）驱动观测谐波至第 10 阶（6 eV）；共振预激发产生高密度激子，经电子—电子散射引起超快退相干，压制相干带间极化与谐波产额，皮秒尺度随载流子复合恢复；近共振（低于激子跃迁）情形的双光子吸收载流子在脉宽重叠窗口内给出约 80 fs 的超快压制。

### 与课题关联
scheme §3.3 SBE-Q 适用条件的 T₂ 预筛段引用：该工作给出"预激发载流子经电子—电子散射在飞秒量级压低 HHG 产额"的直接实验证据，去相干时标可由同类测量逐样品标定，支撑 T₂ > 5 fs 预筛判据的可操作性。

### 课题引用（2026-11-12）
references [39]（2026-11-13 重排，原 [44]）；scheme §3.3 T₂ 预筛段。元数据经 arXiv 官方页与 AIP 出版社页双源核对（刊出于 APL Photonics，卷期页与 DOI 以刊版为准）。


## 2507.03791

标题：Floquet-engineering unveiled by high-harmonic generation（C. Zhao, L. Jurkovičová, X. Zou 等；arXiv:2507.03791v2，2026-06-09 更新；预印本，未见刊出版）

### 研究问题与核心结论
MgO 宽禁带固体的取向分辨 HHG：近红外少周期强场驱动（峰值强度约 1.7×10^12 W/cm²）下，HHG 产额随晶格方位角扫描呈现位于 HH12 附近的弧形特征，归属于布里渊区边界处 Floquet–Bloch 缀饰态与导带的非绝热耦合；TDSE 数值复现该特征并确认其 Floquet 来源。

### 与课题关联
scheme §3.3 强关联接管路径段引用：为"Floquet 光缀饰态可由高次谐波谱学直接探测"提供宽禁带固体上的取向分辨实验证据，支撑 SBE-Q 失效后 Floquet 平均场接管路径的物理可检验性。

### 课题引用（2026-11-12）
references [40]（2026-11-13 重排，原 [45]）；scheme §3.3 强关联接管路径段。元数据经 arXiv 官方页核对（v2 为现行版，作者列表与题名以该版为准）。

## 10.1364/oe.525696

标题：Anisotropic below bandgap harmonic generation in β-gallium oxide（Mukhtar Hussain, André Mesquita Antunes, Gonçalo Vaz 等，里斯本大学/ELI-ALPS/NIMS 等；Optics Express 32(26), 47296–47305，2024-12-16 刊出）

### 研究问题与核心结论
宽禁带半导体 β-Ga₂O₃（Eg = 4.8 eV）的带隙下谐波产生首例非微扰研究：以约 3.0 μm、40 fs、100 kHz 中红外驱动（峰值强度约 1×10¹³ W/cm²），在 (100) 与 (010) 取向单晶上于空气中观测到至第 9 阶（H9 = 3.7 eV）谐波。β-Ga₂O₃ 属单斜 C2/m 空间群、兼具镜面与反演对称性，体相仅支持奇次阶谐波；实测偶次阶来自表面对称性破缺。高阶（H5–H9）呈四重各向异性偏振响应，(010) 图样相对 (100) 旋转 45°，角响应归因于多光子吸收概率随晶向的变化；带隙下谐波机制以带内振荡为主。低阶（H3/H4）观察到前后表面干涉导致的光谱条纹。

### 与课题关联
第四类对照（宽带隙非关联）β-Ga₂O₃ 备选支路的唯一直接实验依据：确认体相电偶极响应下偶次阶禁戒、定量窗口只取奇次阶 q = 5–7（15.5–21.7 eV，400 nm 倍频驱动），为该窗口的可测性（中红外驱动实测至第 9 阶）与奇偶阶来源判别提供实验支撑；四重各向异性为跨样品对照时的偏振设定提供参照。

### 课题引用（2026-11-13）
references [37]（2026-11-13 重排，原 [40]）；scheme §3.3 β-Ga₂O₃ 备选支路段、content §2.3 备选样品段。元数据经 DOI 落地页、里斯本大学研究门户与 NIMS 数据库三源核对（卷期页 47296–47305 一致）。


## 2026-11-13 参考文献回录批注（CrossRef 五件套核验轮）

以下 12 条为正文长期引用但未入笔记的已刊条目，2026-11-13 经 CrossRef API 逐条核对题名/首作/卷期页/年份后回录；编号为当日重排后的现行号（裁撤 5 条后 45→40）。

## 10.1103/PhysRevA.94.063403

标题：Multilevel perspective on high-order harmonic generation in solids（M. Wu, D. A. Browne, K. J. Schafer；Phys. Rev. A 94(6), 063403, 2016）。多带半导体布洛赫方程（SBE）方法学基础：带间跃迁与带内电流在同一框架内分离，谱形—带结构对应可逐阶计算。与课题关联：SBE-Q 的经典光驱动原型与方法学起点。课题引用：references [4]；rationale §1.2.1、scheme §3.5。

## 10.1103/PhysRevLett.121.057405

标题：High-Harmonic Generation in Mott Insulators（Y. Murakami, M. Eckstein, P. Werner；PRL 121(5), 057405, 2018）。Mott 绝缘体 HHG 理论奠基：Hubbard 修正以定量形式进入谐波谱。与课题关联：强关联样品多体修正进入 SBE-Q 的理论基线。课题引用：references [5]；rationale §1.2.1、scheme §3.5。

## 10.1103/PhysRevLett.124.157403

标题：Determination of Electron Band Structure using Temporal Interferometry（L. Li 等；PRL 124(15), 157403, 2020；第一完成单位华中科技大学武汉光电国家实验室）。固体 HHG 时域干涉反演能带结构方法学范式。与课题关联：国内"谱学—参数"反演主线。课题引用：references [6]；rationale §1.3。

## 10.1103/PhysRevB.106.245307

标题：Two-particle tight-binding description of higher-harmonic generation in semiconductor nanostructures（U. Peschel, M. Thümmler, T. Lettau 等；PRB 106(24), 245307, 2022）。实空间双粒子紧束缚方案。与课题关联：莫尔超晶格超出周期近似时的建模接管路径。课题引用：references [7]；content §2.2。

## 10.1103/PhysRevLett.126.137403

标题：Quantum Interference Visibility Spectroscopy in Two-Color Photoemission from Tungsten Needle Tips（A. Li, Y. Pan, P. Dienstbier 等；PRL 126(13), 137403, 2021）。双色场量子干涉可见度的逐脉冲测量范式。与课题关联：QEF 可见度维度与 $Q_F$ 自洽性检验的测量协议参照。课题引用：references [8]；rationale §1.4、content §2.2、scheme §3.4/§3.7。

## 10.1103/PhysRevLett.131.256201

标题：Giant Correlated Gap and Possible Room-Temperature Correlated States in Twisted Bilayer MoS2（F. Wu, Q. Xu, Q. Wang 等；PRL 131(25), 256201, 2023）。扭转双层 MoS₂ 半填充（ν=1）关联能隙约 126 meV、临界温度高至 285 K。与课题关联：第二类中等关联对照体系的选样依据。课题引用：references [9]；rationale §1.2.3、content §2.3、scheme §3.2。

## 10.1063/5.0055897

标题：High-order harmonic generation in 2D transition metal disulphides（J. M. Iglesias, E. Pascual, M. J. Martín 等；APL 119(1), 012101, 2021）。粒子系综蒙特卡洛给出单层 MoS₂/WS₂ 各阶阈值提取带宽（50 kV/cm 下 7 阶 23/8 GHz、9 阶 8/2 GHz），WS₂ 高阶提取代价更低。与课题关联：谱学环节产额计数率基准。课题引用：references [11]；rationale §1.2.1、content §2.2、scheme §3.3。

## 10.1007/s00340-026-08680-7

标题：Orientation-dependent high harmonic generation in ZnO（T. Apostolova, B. Kiss, D. Rajak 等；Appl. Phys. B 132(6), 84, 2026）。3 µm 驱动、约 1 TW/cm² 下 (0001) 面 ZnO 奇次谐波至第 13 阶；实验四重角调制与理论三重（发表版述六重）的分歧归因于多价带跃迁各向异性。与课题关联：固体截止律两类形式的实验对应。课题引用：references [23]；scheme §3.3。

## 10.1103/PhysRevA.102.033105

标题：Crystal-momentum-resolved contributions to multiple plateaus of high-order harmonic generation from band-gap materials（C. Yu, H. Iravani, L. B. Madsen；PRA 102(3), 033105, 2020）。一维线性链 TDDFT + 半经典 k 空间轨迹：更高平台源于初始晶体动量远离 Γ 点的电子。与课题关联：SBE-Q 在 k 空间分解层面给出预测的必要性依据。课题引用：references [25]；content §2.2。

## 10.1038/s41535-026-00890-8

标题：Failed superconductivity in a Mott spin liquid material（Y. Wang, V. Dobrosavljević, E. S. Choi 等；npj Quantum Materials 11(1), 68, 2026）。κ-(BEDT-TTF)₂X 家族 T→0 全局超导失稳、超导畴嵌入金属逾渗团簇。与课题关联：κ-Br 家族层面 U/W 分档参照（不安排 HHG 谱学）。课题引用：references [27]；content §2.3。

## 10.1038/s43246-025-00873-5

标题：High harmonic spectroscopy reveals anisotropy of the charge-density-wave phase transition in TiSe2（I. Tyulnev, L. Zhang, L. Vamos 等；Communications Materials 6(1), 152, 2025）。TiSe₂ 3/5/7 阶产额随偏振方位角非对称分布，出现于 CDW 相变温度（约 200 K）以下并持续演化至 14 K。与课题关联：TiSe₂ 锚点温度扫描与各向异性比判据的对标基线。课题引用：references [35]；content §2.3、scheme §3.3。

## 10.1038/s42005-026-02521-x

标题：Electron-phonon-dominated charge-density-wave fluctuations in TiSe2 accessed by ultrafast nonequilibrium dynamics（S. Fragkos, H. Orio, N. Girotto Erhardt 等；Communications Physics 9(1), 86, 2026）。时间分辨极紫外动量显微：CDW 起伏非共振熔化后约 700 fs 恢复，电子—声子散射为起源。与课题关联：TiSe₂ 锚点带重整量级与温漂控制判据的独立参照。课题引用：references [36]；scheme §3.3。
## 2026-11-16 参考文献回录批注（CrossRef 五件套 + arXiv abs 页核验轮）

以下 24 条为正文长期引用而此前未入笔记的条目，2026-11-16 经 CrossRef API（题名/作者链/刊名/卷期页/年份）与 arXiv abs 页（题名/作者链/版本/日期）逐条核对后回录；元数据一律以核验到的真身誊写，刊版与预印本题名不一致者已在参考文献条目内注明。

## 10.1038/s41567-024-02659-x

标题：High-harmonic generation by a bright squeezed vacuum（A. Rasputnyi, Z. Chen, M. Birk 等；Nature Physics 20(12), 1960–1965, 2024；arXiv:2403.15337 v2，2024-04-09）。BSV 驱动 HHG 首例实验：单模 BSV 微扰经典驱动场，谐波产额相对相干光有量级提升。与课题关联：BSV-HHG 首例实验基线。课题引用：references [1]；rationale §1.2.2/§1.3、content §2.3、scheme §3.2/§3.5。

## 10.1103/PhysRevResearch.6.033079

标题：Generation of squeezed high-order harmonics（M. Even Tzur, M. Birk, A. Gorlach 等；Phys. Rev. Research 6(3), 033079, 2024；arXiv:2311.11257）。winding trail 量子态描述给出压缩谐波场的统计性质。与课题关联：谐波侧量子态的公式起点。课题引用：references [2]；rationale §1.2.2、content §2.2/§2.5、scheme §3.2/§3.3。

## 10.1364/OL.37.001919

标题：Superbunched bright squeezed vacuum state（T. Sh. Iskhakov, A. M. Pérez, K. Yu. Spasibko 等；Optics Letters 37(11), 1919–1921, 2012；arXiv:1202.1682，题名作 Super-bunched）。简并参量放大构型下 $g^{(2)}(0)=3+1/N$ 的超聚束。与课题关联：BSV 光源超聚束基线。课题引用：references [3]；rationale §1.2.2、content §2.1。

## 10.1088/0256-307X/43/5/050401

标题：Relative-intensity squeezing of high-order harmonic twin beams（S. Jiang, K. Dorfman；Chinese Physics Letters 43(5), 050401, 2026；arXiv:2311.10390）。强场 HHG 相对强度压缩谐波孪生光束的理论预言。与课题关联：谐波侧压缩特性的理论参照。课题引用：references [12]；rationale §1.3、content §2.5、scheme §3.4。

## 10.1103/PhysRevA.111.063105

标题：High-order harmonic generation in a crystal driven by quantum light（R. V. Gothelf, C. S. Lange, L. B. Madsen；Phys. Rev. A 111(6), 063105, 2025；arXiv:2502.11803 v2，2025-02-21，jref 指向 PRA 111, 063105）。ZnO 单带模型给出 BSV 相对相干光与 Fock 态更高的截止能量，源于 P 分布高拖尾。与课题关联：截止阶数推高机制层预言。课题引用：references [13]；rationale §1.2.2、content §2.2/§2.5、scheme §3.3。

## 10.1103/wyk5-k8tk

标题：Excitonic Enhancement of Squeezed Light in Quantum-Optical High-Harmonic Generation from a Mott Insulator（C. S. Lange, T. Hansen, L. B. Madsen；Phys. Rev. Lett. 135(4), 043603, 2025；arXiv:2503.15932）。Mott 体系激子能区压缩光增强机制。与课题关联：强关联样品的压缩光增强机制参照。课题引用：references [14]；content §2.3。

## 10.1103/hph3-kzb2

标题：Quantum path control in high-order harmonic generation via squeezed light（F. Wang, C. Yang, X. Cui 等；Phys. Rev. A 112(4), 043119, 2025；arXiv:2509.20876，题名作 via squeezed lights）。BSV 驱动下量子路径选择与阿秒脉冲宽度压缩。与课题关联：量子路径控制方法学。课题引用：references [16]；rationale §1.3。

## 10.1038/s41566-025-01673-6

标题：Photon bunching in high-harmonic emission controlled by quantum light（S. Lemieux, S. A. Jalil, D. Purschke 等；Nature Photonics 19(7), 767–771, 2025；arXiv:2404.05474）。ZnO 半导体 BSV 微扰经典驱动，观测谐波边带的超泊松光子聚束。与课题关联：BSV 固体 HHG 的早期实验对照。课题引用：references [17]；rationale §1.2.2。

## 10.1103/PhysRevLett.116.016601

标题：Diabatic mechanisms of higher-order harmonic generation in solid-state materials under high-intensity electric fields（T. Tamaya, A. Ishikawa, T. Ogawa, K. Tanaka；Phys. Rev. Lett. 116(1), 016601, 2016；arXiv:1701.02869，jref 指向 PRL 116, 016601）。交流 Zener 隧穿与半导体半金属化两类非微扰固体 HHG 成因及带宽限制型截止律。与课题关联：固体截止律的实验/理论对应。课题引用：references [19]；scheme §3.3。

## 10.1007/s00340-025-08506-y

标题：High-harmonic generation in zinc oxide subjected to intense mid-infrared femtosecond laser pulse（B. Obreshkov, T. Apostolova；Applied Physics B 131(8), 158, 2025；arXiv:2405.01571 v4，2025-02-13，jref 指向 Appl. Phys. B (2025) 131:158）。多带 ZnO 体材料的固体 HHG 理论，谐振与非谐振响应分离后给出带隙以上奇次谐波发射。与课题关联：固体 HHG 机制层对照。课题引用：references [20]；scheme §3.3。

## 10.1038/s41467-026-75173-8

标题：Propagation effects in high harmonic generation media driven by bright squeezed vacuum light（J. Rivera-Dean, D. Kanti, P. Stammer 等；Nature Communications 17(1), 8457, 2026；arXiv:2509.19608 v3，2025-11-04，arXiv 版题名为 Propagation of intense squeezed vacuum light in non-linear media，与刊版题名不同）。全量子化框架下 BSV 在介质中的传播，强 BSV 涨落引发电离与红外光子损耗导致退相干，限制传播长度并压低谐波产额。与课题关联：BSV 驱动 HHG 的传播层损耗机制。课题引用：references [22]；scheme §3.6。

## 10.1103/ffdj-mz2y

标题：Nonclassical cutoff fluctuations in squeezed-light-driven high-harmonic generation（T. Khurelbaatar, R. T. Sang, I. Litvinyuk；Phys. Rev. Research 8(4), 043107, 2026；arXiv:2605.21925）。压缩光驱动 HHG 的截止方差关系 $\Delta H^2(r)/\Delta H^2_{\rm SQL}=e^{-2r}$，方差极小值位于 $r_{\rm opt}\approx1.6$。与课题关联：压缩扫描上限取值的依据（BSV 形式需数值重标定）。课题引用：references [24]；scheme §3.3。

## 10.1038/s41566-018-0129-0

标题：High-harmonic spectroscopy of ultrafast many-body dynamics in strongly correlated systems（R. E. F. Silva, I. V. Blinov, A. N. Rubtsov 等；Nature Photonics 12(5), 266–270, 2018；arXiv:1704.08471，题名作 High harmonic imaging of ultrafast many-body dynamics in strongly correlated systems，与刊版题名不同）。一维半填充 Fermi-Hubbard 模型严格解基础上以高次谐波成像分辨 Mott 绝缘体光致相变的多体动力学。与课题关联：经典光 HHG 的多体动力学分辨能力。课题引用：references [26]；rationale §1.2.1。

## 10.1088/1361-6455/aebad3

标题：Emergence of Gaussian entanglement and non-Gaussianity in high-harmonic generation driven by bright squeezed light（J. Rivera-Dean, M. Even Tzur, M. F. Ciappina 等；J. Phys. B 59(21), 215401, 2026；arXiv:2606.22714 v2，2026-10-13，v2 说明论文已被 J. Phys. B 接收）。双色驱动（强相干场在 $\omega$、微扰 BSV 在 $2\omega$）下偶次谐波响应近似线性于 BSV 正交分量，谐波场呈非经典高斯纠缠。与课题关联：产物侧量子统计可辨认性判据。课题引用：references [28]；rationale §1.2.2。

## 10.1038/s41586-026-10485-9

标题：Nonlinear atomic tunnelling boosted by bright squeezed vacuum（Z. Jiang, S. Pan, J. Chen 等；Nature 654(8118), 356–360, 2026；arXiv:2604.05783 v2，2026-05-20）。300 nJ 平均脉冲能量的 BSV 产生的光电子动量谱峰等效于 7.1 μJ 相干光的作用效果，量子增益超过 20 倍。与课题关联：BSV 场统计可改写强场非线性有效强度的国内实验先例。课题引用：references [31]；rationale §1.3。

## 10.1117/1.AP.9.1.016001

标题：Quantum high-harmonic generation with entangled photon pairs（Z. Lyu, F. Sun, S. Yi 等；Advanced Photonics 9(1), 016001, 2026；arXiv:2604.06707，arXiv 版题名为 Attosecond quantum spectroscopy with entangled photon pairs；DOI 存档仅列末三位作者，作者链按 arXiv 官方页誊录）。2060 nm 单模 BSV、强度约 1.2 TW/cm²，x-cut 铌酸锂中观测到高次谐波至第 10 阶；逐次光子数统计的 $g^{(2)}$ 随阶次先升后降，非简并纠缠光子对构型下谐波保留量子诱导关联。与课题关联：BSV 固体 HHG 的逐次光子关联对照基线。课题引用：references [32]；rationale §1.3、scheme §3.5。

## 10.1103/PhysRevLett.129.147401

标题：Signatures of multiband effects in high-harmonic generation in monolayer MoS₂（L. Yue, R. Hollinger, C. B. Uzundal 等；Phys. Rev. Lett. 129(14), 147401, 2022；arXiv:2112.13032 v2，2022-02-15）。平行偏振奇次谐波在约 3.5 eV 上下发生角度位移，归因于多条导带的复合偶极矩差异。与课题关联：SBE-Q 保留多导带跃迁的实验依据。课题引用：references [33]；content §2.2。

## 10.1038/s41567-026-03425-x

标题：Real-space imaging of moiré-confined excitons in twisted bilayer MoS₂（L. J. M. Westenberg, L. Eek, J. D. Verbakel 等；Nature Physics 22(10), 1594–1599, 2026；arXiv:2511.20398）。2° 扭转双层 MoS₂ 室温光电流原子力显微成像给出莫尔周期约 9 nm 与位点选择性的激子局域化图像。与课题关联：莫尔关联态的空间参照坐标。课题引用：references [34]；scheme §3.3。

## arXiv:2505.22536

标题：Quantum engineering of high harmonic generation（N. Boroumand, A. Thorpe, G. Bart 等；arXiv:2505.22536，2025-05-28，预印本，未见刊出版）。提出 quantum sideband high harmonic generation（QSHHG）闭式理论，给出边带模与扰动量子模之间的多模纠缠判据；原文明确量子场非经典性质向谐波边带的转移尚未在实验上确证。与课题关联：QEF 可见度维度的标定方法学锚点。课题引用：references [10]；content §2.5、scheme §3.7。

## arXiv:2509.13518

标题：Quantum Dial for High-Harmonic Generation（L. Wang, A. M. Parks, A. Thorpe 等；arXiv:2509.13518v3，2026-09-01 更新，预印本，未见刊出版）。经典场 $E_0=3\times10^{9}$ V/m（1.2 TW/cm²）、中心波长 3.2 μm；弱 BSV 场 $E_s\sim5\times10^{7}$ V/m、约 1 nJ，能量占比低于经典驱动场的 5%，作为"optical dial"调控谐波谱、发射角分布与电离，并给出谷对比响应。与课题关联：驱动场强版本锚定（文献参照，非参数移植）。课题引用：references [15]；rationale §1.2.2。

## arXiv:2605.28236

标题：Symmetry breaking by quantum light in solid-state high-harmonic generation（P. Stammer, J. Rivera-Dean, D. Kim 等；arXiv:2605.28236，2026-05-27，预印本，未见刊出版）。量子涨落破坏驱动场动力学对称性而保留晶体空间对称性，石墨烯与 MoS₂ 给出不同的允许谐波通道集合；涨落诱导谐波满足 $g^{(2)}(0)\geq3$，经典允许谐波近泊松。与课题关联：非经典光场改写选择规则的机制参照。课题引用：references [18]；rationale §1.1/§1.2.3。

## arXiv:2511.18362

标题：Attosecond-resolved quantum fluctuations of light and matter（M. Even Tzur, C. Mor, N. Yaffe 等；arXiv:2511.18362，2025-11-23，预印本，未见刊出版）。BSV 与强场联合驱动固体 HHG，把 BSV 的量子性质转移到 XUV 阿秒脉冲，以阿秒干涉重建谐波与阿秒脉冲的量子态。与课题关联：$Q_F$ 相空间表征的实验参照。课题引用：references [21]；content §2.3、scheme §3.4/§3.5。

## arXiv:2602.10882

标题：Sub-Poissonian Statistics and Quantum Non-Gaussianity from High-Harmonic Generation（D. Theidel, M. Nahra, I. Karuseichyk 等；arXiv:2602.10882v4，2026-06-13 更新，预印本，未见刊出版）。对三个双位数阶次谐波测量点击统计并以见证子认证非经典性；高阶谐波在相干光驱动下呈压缩与纠缠，跨阶 heralded 测量可工程化出亚泊松光子统计态与量子非高斯态。与课题关联：$g^{(2)}_{\rm HHG,q}(0)$ 偏离泊松分布预测的实验侧统计参照。课题引用：references [29]；content §2.2。

## arXiv:2604.20388

标题：Quantum Optical Signatures of Band Geometry in Solid-State High Harmonics（D. Ilin, A. S. Solntsev, I. Iorsh；arXiv:2604.20388v3，2026-11-09 更新，预印本，未见刊出版；v3 版题名由 Band Topology 改为 Band Geometry）。把带几何性质映射为谐波的量子光学特征，SSH 模型给出拓扑相中更强的 HHG 响应与更强的量子光特征。与课题关联：拓扑绝缘体对照位的带间几何—光子统计对接方法学参照。课题引用：references [30]；content §2.3。
