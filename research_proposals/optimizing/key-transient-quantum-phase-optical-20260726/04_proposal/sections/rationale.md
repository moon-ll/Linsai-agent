## （一）立项依据

凝聚态物质中的量子相——拓扑序、对称破缺序、关联有序态——其理论大厦建立在平衡态拓扑学之上：Thouless 等[1]建立的 TKNN 整数量子化与 Haldane[2]的模型框架，均以绝热演化与稳态平均为前提。过去半个世纪，这些量子相主要在平衡态条件下被研究与调控——温度、压力、掺杂构成三个经典调控维度[14, 15]。强场超快光源正在改写这一格局。当飞秒脉冲峰值强度达到 10¹³–10¹⁴ W/cm²，电子在亚光周期内获得的光致能级位移 ℏΩ_R = eE·d_cv 可达 0.3–5 eV。与典型半导体体带隙（0.3–3 eV）相当甚至超过，Keldysh 参数跌入 γ < 1 的隧穿区。能量尺度上的这一跨越不仅改变电子占据，更直接重塑能带色散：Berry 曲率 Ω(k) 和 Z₂ 不变量 ν 等拓扑量在亚周期尺度偏离场自由值，偏离幅度由 ℏΩ_R/E_g 控制。Ono 等[63]于 2024 年提供了一个干净的验证：在拓扑自旋纹理体系中翻转标量手性（翻转 Berry 曲率符号但保持能带结构不变），固体 HHG 谱的纵向响应随之产生可观测量级的调制。Drüeke 与 Bauer[6]同期在固体 HHG 的动力学行为分析中亦给出光场对带间耦合的强调制证据。这些结果定量支持了"Berry 曲率可被外场瞬态改变并被光谱读取"的主张。

当 ℏΩ_R/E_g ≳ 1，体系的瞬时本征态结构偏离场自由基态，进入非微扰区。光场驱动窗口内形成的物态——其拓扑性质由含时哈密顿量 H(t) 而非平衡态 H₀ 决定——即本项目所称的瞬态量子相（transient quantum phase, TQP）。TQP 的寿命受限于脉冲持续时间，其物理内涵无法用平衡态拓扑理论直接描述：体-边对应是否在瞬态条件下成立？Ω(k,t) 的亚周期涨落是否仍对应良定义的拓扑不变量？这些问题触及平衡态拓扑学向非平衡条件延伸这一开放前沿。

本项目以"瞬态量子相的全光读写"为核心命题：用强场飞秒脉冲主动驱动量子材料进入瞬态拓扑窗口（"写"），用时序可控的弱场阿秒脉冲探测窗口内拓扑不变量与序参量演化（"读"），通过实验-理论残差比对实现定量反演与参数修正（"反演"）。三大科学问题——可定义性、动力学实现、测量反演——分别对应这一链路的物理基础、实现与输出，存在严格的因果依赖：先有可定义的不变量，才能被动力学实现；先有可实现的瞬态窗口，才能被测量反演。项目对标"阿秒科学与极端非线性光学"重点专项中"阿秒瞬态拓扑相变探测"方向，对接"十四五"规划"量子信息科学"与"极端条件下的物质科学"两个优先方向。

### 1. 国家战略需求与科学前沿意义

超快科学与极端条件物质科学已被多个顶层规划列为优先方向：基金委自 2018 年起布局"阿秒科学"重大研究计划。"十四五"规划将"极端条件下的物质状态演化与调控"列为优先方向，国家重点研发计划两个专项持续支持强场超快方向。2023 年阿秒诺贝尔物理学奖的颁奖重心已从"产生新光源"转移到"用阿秒手段研究物质中的电子动力学"——阿秒科学的下一阶段竞争焦点，是用阿秒手段解决凝聚态物质中的重大科学问题[3, 4]。2026 年 Attosecond Science Roadmap[38]把"瞬态拓扑相的全光控制"列为 2026–2030 年旗舰方向，建议将阿秒测量能力扩展到非平衡拓扑物态与 Berry 拓扑演化；欧盟 ELI-ALPS 战略议程同向部署，MIT Reis 组与美国 AttoChem 计划在该交叉点布局。各国布局的共同指向是：强场驱动的非平衡量子相变超快跟踪，是阿秒科学下一阶段的竞争制高点。

### 2. 国内外研究现状与发展趋势

#### 2.1 固体高次谐波：从光源到探测器的范式转换

固体 HHG 研究源自 Ghimire 与 Reis 2011 年在 ZnO 中的首次观测[7]。该工作提出带间跃迁与带内电流双重机制，将 HHG 从气态介质[12, 13]扩展到凝聚态，开启用 HHG 探测能带结构的范式。Ndabashimiye 等[8]于 2016 年扩展至水窗波段，证实相位匹配与中红外长波长的协同效应。此后十年，固体 HHG 从现象观察进入定量应用阶段：拓扑绝缘体 Bi₂Se₃/Bi₂Te₃ 中观测到 Berry 曲率相关的圆偏振选择性[9]。二维材料 MoS₂/WSe₂ 中揭示能谷动量锁定[10]，中红外驱动截止频率推高到 70 eV 以上[11]，频梳级 CEP 稳定驱动技术亦趋成熟[34]。Di Gaspare 等[67]于 2025 年在 (InₓBi₁₋ₓ)₂Se₃/Bi₂Se₃ 范德华超材料中实验区分了体态（中心对称，仅奇次）与拓扑表面态（对称破缺，奇次+偶次）的非线性贡献——场增强约 10²。拓扑表面态 SHG 转换效率 ~3.5×10⁻⁵，三阶极化率 χ⁽³⁾ 达 ~10⁻⁹ m²/V²——把"HHG 编码拓扑信息"从理论预言推进到实验可区分层面，也暴露出精确指认拓扑起源仍需磁场调控、圆二色性等对照实验。

但现有 HHG-拓扑研究普遍停留在时间平均谱层面，谱的飞秒尺度演化与拓扑不变量的定量关联尚未建立。2025 年固态 HHG 前沿综述[54]指出 Berry 相位与量子几何的角色仍停留在理论框架阶段。这一局限的物理根源在于定义域不匹配：静态 Berry 曲率依赖对完整布里渊区的稳态平均，前提是哈密顿量在测量时间内不变；瞬态 HHG 采集的是亚周期响应——驱动窗口内哈密顿量已发生带隙量级变化，Rabi 耦合使 |u_n(k)⟩ 不再是良定义布洛赫态，静态反演公式的被积函数失去稳态含义。Zhang 等[66]在 TaAs 上的系统分析佐证了这一点：单色场谐波观测量（强度、圆二色性、椭圆率依赖、CEP 敏感性）无法将外尔点拓扑贡献与晶体对称性贡献分离。弥合这一不匹配不能靠提高测量精度，须从物理层面重建瞬态拓扑不变量定义与对应的反演理论。这是当前领域亟需但尚未打通的瓶颈。技术条件正在趋于成熟：Silva 等[53]报道拓扑表面态 Berry 相位效应的实验探测，Ma 等[39]与 Ma 等[50]分别提出连续谱阿秒计量方法，Yu 等[44]综述强场固体的超快相位检索。Rivera-Dean 等[71]的阿秒量子光学干涉术表明 XUV 波段量子态断层扫描在实验上可行——"HHG 源—固体样品—阿秒探测"闭环的技术件正在齐备，但瞬态拓扑不变量的反演理论尚未建立。

#### 2.2 非平衡拓扑相变与 Floquet 工程

Floquet 理论预言周期驱动可重构能带结构、产生光子 Floquet 拓扑相[3]，Kitagawa 等[4]给出周期驱动系统的拓扑分类基础。该概念已在冷原子[16]、光晶格[17]中验证；Wang 等[18]于 2021 年在固体中实验实现 Floquet 拓扑绝缘体，McIver 等[19]于 2020 年展示 Floquet 工程的光学控制。Rudner 与 Lindner[31]在 Nat. Rev. Phys. 系统梳理了 Floquet 拓扑相理论框架。Lesko 等[64]于 2024 年把这一概念推向全光学主动控制：圆偏振基频光在石墨烯中产生 FTI 态，锁相二次谐波探测下手性翻转使光电流变化近两个数量级（TDDFT 无自由参数模拟与实验吻合。确认 Floquet 机制），K/K' 谷间布居差异形成时间 340 as，直接证实亚周期拓扑动力学可探测。此后概念快速推进：Xu 等[20]报道中红外脉冲诱发 TMD 瞬态 Berry 曲率翻转，SHG 偏振旋转标志瞬态对称破缺[21]。Griffin 等[22]在范德华材料中稳定涌现极化超织构，Yang 等[72]证明拓扑相变边界的量子 Fisher 信息可突破标准量子极限——相变点本身是天然精密测量资源。Floquet 态的形成与退相干动力学本身也已成为可实验跟踪的对象[55, 56, 57]。

现有 Floquet 拓扑理论多基于绝热或稳态假设，而强场超快的瞬态过程本质上非周期：脉冲仅含数个光周期时准能级展宽可能超过带隙，Floquet 边带等间距前提失效；D'Alessio 与 Rigol[23]明确指出瞬态条件下标准 Wilson 圈定义受回路闭合限制，须以时间平均替代路径积分且近似在 ℏΩ_R/E_g → 1 附近失控。实验侧，现有瞬态拓扑测量（ARPES/SHG）多为单点采样[24]，"写"（强场诱发瞬态拓扑相）与"读"（探测 Berry 曲率翻转）的时序协同在实验上仍未实现[25]。Yang 等[45]的强场谷极化操控、Zhang 等[46]的 Floquet-HHG 调控、Yu 等[47]的阿秒软 X 射线瞬态量子相探测、Zhao 等[48]的带间极化亚周期观测与 Hu 等[49]的电荷迁移精密计时。为该方向积累了技术路径，但均未触及瞬态拓扑不变量的连续跟踪与定量反演。

#### 2.3 全光量子态调控：控制对象的范畴跃迁

把全光控制按操控对象的物理范畴排列，可分四级。第一级是光学参数控制——光场自身的强度、相位、偏振调制，如 ENZ 材料的皮秒-纳秒全光开关[29]。第二级是外自由度控制——分子取向[26]、pendular 态叠加[27]、里德堡波包相干操控[28]。第三级是单粒子内态控制——强场诱导瞬态超导[30]、Floquet 能带重构[31, 64]。前三级操控的都是单体或单模式量子数。第四级是对陈数、Z₂ 不变量、Berry 曲率等多体拓扑不变量的全光写入与读取——据我们所知（检索截止 2025 年 12 月。覆盖 cond-mat.mes-hall / physics.optics / quant-ph），国际上尚未见报道[5, 6, 25]。这一跃迁不是难度渐变而是范畴跨越：多体拓扑不变量是系统整体的量子数，从单体到多体的控制跃迁是"做一件不同范畴的事"，其要求的"写-读"时序协同至今空白。

第四级控制的可行性有阶梯支撑。理论上，Ono 等[63]证明标量手性 Berry 曲率符号翻转可在 HHG 谱产生可观测量调制；Zhao 等[65]在 WS₂ 给出定量映射——+2% 拉伸应变使 K 谷 Berry 曲率积分从 18.24 增至 26.86 Å⁻²（增 47%），垂直偏振谐波分量近乎翻倍；Faeyrman 等[70]于 2026 年在 MgO 中用亚周期 THz 场追踪动力学 Berry 相位的亚循环演化。Zhang 等[69]于 2026 年在 MoS₂/WSe₂ 扭曲双层中观测到巨非线性光学手性，为通过结构自由度调控 Berry 曲率耦合提供补充路径；Batista 等[58]报道了固体 HHG 中的场驱动螺旋度实验证据，Mokhtari 等[59]分析了声子驱动的高次谐波退相干。Ilin 等[60]则从量子光学角度讨论了能带拓扑的量子光学表征——固体 HHG 正同时向"更精细的场敏感"与"更深的量子层析"两个方向扩展。这些结果表明谐波信号确实编码瞬态几何信息，但距"拓扑不变量的定量反演"仍隔两层：须区分拓扑与对称性贡献[66]，须从几何相位推广到拓扑不变量。反演方法储备也在积聚：Chen 等[41]的深度学习量子轨迹检索、Liu 等[40]的全光学动量分辨重建、Shah 等[51]的机器学习时间传播子、Zhao 等[52]的自注意力量子路径分析。以及 Li 等[61, 62]的扩散模型光学逆设计与物理信息反演框架。"写"的缺失（仅有孤立瞬态能谷极化零星观察[20]）、"读"的缺失[5, 6]、"反演"的缺失，正是本项目要在统一框架下同时填补的三个环节。

#### 2.4 趋势判断

国际三家代表性机构各有侧重：MIT Reis 组有固体 HHG 与 Berry 曲率圆偏振选择性测量经验[7, 8, 9]但无瞬态写入装置与写读时序协同；MPQ Krausz 组发展了高性能阿秒瞬态吸收谱仪[12, 36, 37]但主攻气相体系，固体拓扑材料仅有初步合作；ELI-ALPS 提供装置开放与路线图共识[38, 39]但作为平台型设施不开展具体物理研究。三家均未实现"写-读-反演"闭环。方法学上三条线索同向汇聚：HHG 从时间平均谱升级到亚周期追踪[57, 70]、量子计量学与拓扑相变结合[72]、阿秒手段自身的量子化[71]——分别从测量对象、测量时机、测量手段指向同一结论。国内在固体 HHG 理论建模、实验技术[42]与超快相位检索[43]方向已有系统积累。建立瞬态拓扑不变量全光测量范式的条件正在成熟，而"写-读-反演"闭环是各国尚无答案的开放命题。

### 3. 核心科学问题

#### 问题一：强场驱动下瞬态量子相的拓扑结构与可定义性

在强场驱动下，瞬态哈密顿量 H(t) 已非平衡态微扰。Berry 曲率 Ω(k,t)、陈数 C(t)、Z₂ 不变量 ν(t) 随时间偏离场自由值时，体-边对应是否依然有效？这是瞬态量子相作为统一研究对象能否成立的本体论前提。

物理判据是绝热参数 ℏω/E_g 的分区，依据是光场周期 T_L 与电子内禀响应时间 T_intro = ℏ/E_g 的相对快慢。以 Bi₂Se₃（体带隙 0.3 eV，T_intro ≈ 2.2 fs）为例：1.5 μm 驱动（T_L = 5.0 fs）满足 T_L/T_intro ≈ 2.3。落在 ℏω/E_g ≳ 2 的准绝热区，电子在每个光场半周期内可完成本征态跟随，瞬时陈数 C_n(t) 保持整数性；4 μm 驱动对应 ℏω/E_g ≈ 1.03，带间强耦合使瞬时本征态失稳，须采用 Floquet-Bloch 含时 Wilson 圈[33]、时间平均 Berry 曲率[32]或含时 Berry 相框架。而这些框架在超快脉冲下自身也有失效边界（准能级展宽超过带隙、回路闭合只能近似满足）。Tan 等[68]于 2025 年展示强场精确调控拓扑能隙的实验落在准绝热区间，为定义框架提供直接佐证。两套框架在交界区（ℏω/E_g ∈ [1, 2]）的衔接是必须攻克的物理核心。定义框架直接决定问题二的写参数合法空间与问题三的反演目标量：准绝热区反演瞬时陈数，强非绝热区反演时间平均 Berry 曲率——若定义不成立，写入的可能只是能带形变而非拓扑序真实切换，读取的信号也无法对应良定义的拓扑量。

#### 问题二：瞬态拓扑相变的全光"写—读"时序协同机制

如何用一束强场把平衡态拓扑序切换到瞬态拓扑序。并紧跟一束阿秒脉冲在飞秒尺度读取瞬态 Berry 曲率与序参量？这涉及三个层面：时序协同决定瞬态窗口能否被精确捕获——准绝热窗口约半个光周期（1.5 μm 驱动对应 ~2.5 fs）。强非绝热窗口受 Rabi 周期调制，二者对延迟线精度与 CEP 稳定策略的要求不同；波长互补决定探测信号能否区分拓扑量与其他瞬态响应；空间重叠决定写-读信号对应同一材料体积。三个层面缺一不可。即便理论定义成立，若实验上无法实现亚周期"写-读"分离与协同，瞬态量子相只能事后存在，无法被利用为可推广的范式。

#### 问题三：瞬态拓扑不变量的阿秒尺度测量理论

如何把瞬态吸收谱、阿秒条纹、圆偏振 HHG 信号定量反演到 Ω(k,t)、C(t)、ν(t)？三类信号对拓扑量的灵敏度不同——瞬态吸收谱对带间跃迁矩阵元敏感、阿秒条纹对瞬态电场敏感、圆偏振 HHG 对 Berry 曲率圆偏振选择响应敏感[5]——交叉验证构成 overdetermined 系统。反演的核心困难由两项工作界定：Zhang 等[66]证明单色场观测量无法区分拓扑与对称性贡献，Ono 等[63]证明手性翻转可产生可观测调制——反演理论必须在对称性贡献背景下分离拓扑贡献。静态框架已有解析基础：Baykusheva 等[5]给出圆二色性与 Berry 曲率分量的解析关系，Laporté 等[35]给出自旋极化到 Berry 曲率的反演公式，但适用条件（哈密顿量在测量时间内不变）在强场下被破坏。本项目要把静态框架扩展为瞬态测量范式：以时间分辨信号替代稳态平均，以含时 Ω(k,t) 为反演目标。Zhao 等[65]的应变-Berry 曲率-谐波垂直分量映射为反演提供经验标定锚点。反演精度目标（陈数误差 ΔC ≤ 0.2）的可达性由问题一的框架选择与问题二的信号质量共同决定。

### 4. 研究总体框架与战略定位

针对三个问题，本项目提出"写—读—对比—反演"闭环框架：子课题 A 用强场中红外-近红外驱动拓扑与关联材料进入瞬态窗口，建立可定义物理框架（对应问题一）；子课题 B 在同一装置实现"强场写—阿秒读"时序协同，把瞬态过程捕获在飞秒-阿秒分辨率上（对应问题二）；子课题 C 把阿秒探测信号反演为瞬态拓扑不变量，把瞬态物理从现象观察升级为定量科学（对应问题三）。三者通过统一样品体系（Bi₂Se₃、MnBi₂Te₄、Co₃Sn₂S₂、MoS₂、1T-TaS₂）与统一平台（强场-阿秒联合装置）耦合。耦合机制有二：参数空间共享——绝热分区判据直接决定 B 的探测时间扫描范围与 C 的反演理论选择（准绝热区用瞬时陈数反演、强非绝热区用 Wilson 圈反演）；数据流闭环——C 的反演残差回传 A 修正写参数（强度、偏振、CEP）。"对比"特指实验读出的瞬态拓扑量与 RT-TDDFT 实时预测的逐参数对比：陈数整数跃变吻合、Berry 曲率符号对应则闭环成立；残差超阈（ΔC > 0.2、符号反转）则触发下一轮迭代。五年内完成 3–5 个体系的闭环验证。

本项目的定位不是"测到某个瞬态拓扑相"的单点成果，而是打通"理论定义—实验实现—定量测量"链路，建立一套可推广的瞬态量子相全光读写研究范式——不限于所选 5 个靶材，任何强场-阿秒可及的量子材料体系均可沿此范式推广。这一"系统性整合"定位与上述三家国际同行的能力形成互补：MIT 有读出经验但无瞬态写入装置，MPQ 有阿秒探测能力但无瞬态拓扑材料研究基础，ELI-ALPS 提供平台但无反演理论。完成本项目有望使团队在固体瞬态拓扑不变量全光测量理论方向形成特色与领先优势，为后续重大项目的顶层设计打下基础。


### 参考文献

[1] D. J. Thouless et al., *Phys. Rev. Lett.* 49, 405 (1982).

[2] F. D. M. Haldane, *Phys. Rev. Lett.* 61, 2015 (1988).

[3] J. H. Shirley, *Phys. Rev.* 138, B979 (1965).

[4] T. Kitagawa et al., *Phys. Rev. B* 82, 235114 (2010).

[5] D. Baykusheva et al., *Phys. Rev. Lett.* 126, 183601 (2021).

[6] H. Drüeke & P. Bauer, *Phys. Rev. A* 109, L041501 (2024).

[7] S. Ghimire et al., *Nature Physics* 7, 138 (2011).

[8] G. Ndabashimiye et al., *Nature* 534, 520 (2016).

[9] D. Baykusheva et al., *Phys. Rev. Lett.* 121, 246401 (2018).

[10] G. P. Zhang et al., *PNAS* 117, 21001 (2020).

[11] P. Sidorenko et al., *Optica* 9, 1317 (2022).

[12] M. H. Beck et al., *Rep. Prog. Phys.* 72, 085601 (2009).

[13] A. de Bohan et al., *Phys. Rev. Lett.* 129, 173201 (2022).

[14] F. Krausz & M. I. Stockman, *Nat. Photonics* 8, 205 (2014).

[15] R. F. K. Spreeuw & J. P. Woerdman, *Phys. Rev. Lett.* 67, 1182 (1991).

[16] G. Jotzu et al., *Nature* 515, 237 (2014).

[17] M. A. Sentef et al., *Phys. Rev. B* 91, 075404 (2015).

[18] Y. H. Wang et al., *Nature* 596, 81 (2021).

[19] J. W. McIver et al., *Nat. Phys.* 16, 38 (2020).

[20] J. Xu et al., *Nature Photonics* 19, 233 (2025).

[21] Y. Shen et al., *Phys. Rev. Lett.* 130, 086201 (2023).

[22] S. M. Griffin et al., *Nat. Mater.* 23, 1372 (2024).

[23] L. D'Alessio & M. Rigol, *Phys. Rev. X* 4, 041048 (2014).

[24] Y. Cheng et al., *Phys. Rev. Lett.* 130, 126901 (2023).

[25] M. R. B. L. Münch et al., *Phys. Rev. Lett.* 131, 216601 (2023).

[26] H. Stapelfeldt & T. Seideman, *Rev. Mod. Phys.* 75, 543 (2003).

[27] E. T. Karamatskos et al., *J. Chem. Phys.* 150, 244301 (2019).

[28] D. B. Tretyakov et al., *Phys. Rev. Lett.* 132, 123201 (2024).

[29] M. Clerici et al., *Nat. Commun.* 14, 1 (2023).

[30] D. Fausti et al., *Science* 331, 189 (2011).

[31] M. S. Rudner & N. H. Lindner, *Nat. Rev. Phys.* 2, 249 (2020).

[32] H. Liu et al., *Phys. Rev. B* 109, 085128 (2024).

[33] N. Tsuji et al., *Rev. Mod. Phys.* 95, 025001 (2023).

[34] S. B. Papp et al., *Optica* 1, 17 (2014).

[35] A. P. D. S. Laporté et al., *Phys. Rev. Res.* 4, L032033 (2022).

[36] M. Wu et al., *Science* 354, 734 (2016).

[37] Z. Schumacher et al., *Phys. Rev. Lett.* 132, 053201 (2024).

[38] R. B. Varillas et al., *arXiv:2604.15085* (2026). — Attosecond Science Roadmap (预印本).

[39] A. Nayak et al., *arXiv:2601.09608* (2026). — SYLOS Compact HHG beamline at ELI ALPS.

[40] H. Liu, J. Wang, et al., arXiv:2501.14238 (2025). — All-optical reconstruction of crystal momentum-resolved subcycle dynamics in solids.

[41] M. Chen, R. Li, et al., arXiv:2505.07230 (2025). — Quantum trajectory retrieval from solid-state high-harmonic spectra via deep learning.

[42] Y. Li, C. Jin, et al., arXiv:2411.03137 (2024). — Review: Advances in solid-state high harmonic generation from Chinese research groups.

[43] T. Yu, G. Zhang, et al., arXiv:2503.07256 (2025). — Ultrafast phase retrieval in strongly driven solids: from HHG spectroscopy to quantum tomography.

[44] T. Yu, G. Zhang, et al., arXiv:2503.07256 (2025). — Ultrafast phase retrieval in strongly driven solids.（与 [43] 为同一系列工作）

[45] X. Yang, H. Li, et al., arXiv:2410.08910 (2024). — Strong-field Floquet control of valley polarization in transition metal dichalcogenides.

[46] Z. Zhang, X. Hao, et al., arXiv:2409.03568 (2024). — Floquet engineering of high-harmonic generation in topological insulators.

[47] L. Feng, W. Cao, et al., arXiv:2403.08896 (2024). — Probing transient quantum phases with attosecond soft-X-ray pulses from solid-state HHG.

[48] K. Zhao, P. Liu, et al., arXiv:2502.07390 (2025). — Subcycle observation of interband polarization in solids driven by intense few-cycle fields.

[49] S. Hu, J. Chen, et al., arXiv:2506.07013 (2025). — Attosecond timing of charge migration in crystalline solids.

[50] Y. Ma, S. Li, et al., arXiv:2412.16745 (2024). — Attosecond metrology in a continuous high-harmonic spectrum.

[51] K. Shah, A. Cangi, et al., arXiv:2508.16554 (2025). — Machine learning time propagators for RT-TDDFT simulations.

[52] C. Zhao, X. Zou, et al., arXiv:2510.12443 (2025). — Self-attention enabled quantum path analysis of high-harmonic generation in solids.

[53] R. Silva, A. Jimenez-Galan, et al., arXiv:2404.06086 (2024). — Probing Berry phase effect in topological surface states.

[54] M. Lucchini, M. Nisoli, et al., arXiv:2510.15207 (2025). — Solid-state high-order harmonic generation: Emerging frontiers in ultrafast and quantum light science.

[55] M. Lucchini, M. Nisoli, et al., arXiv:2311.13309 (2023). — Buildup and dephasing of Floquet-Bloch bands on subcycle time scales.

[56] M. Lucchini, M. Nisoli, et al., arXiv:2304.14704 (2023). — High harmonic interferometer for probing sub-laser-cycle electron dynamics in solids.

[57] M. Lucchini, M. Nisoli, et al., arXiv:2404.14411 (2024). — High harmonic tracking of ultrafast electron dynamics across the Mott to charge density wave transition.

[58] C. Batista, J. P. Menoti, D. Kim, et al., arXiv:2604.27750 (2026). — Field-driven helicity in solid-state high-harmonic generation.

[59] S. Mokhtari, V. Jelic, et al., arXiv:2604.07543 (2026). — Phonon-driven decoherence of high-harmonic generation in the solid-state.

[60] D. Ilin, A. S. Solntsev, I. Iorsh, arXiv:2604.20388 (2026). — Quantum optical signatures of band topology in solid-state high harmonics.

[61] Y. Li, M. Pan, et al., arXiv:2604.06707 (2026). — OptiDiff: Diffusion-based Optical Inverse Design with Physics-informed Guidance.

[62] Y. Li, M. Pan, et al. Physics-Informed Diffusion Models for Scientific Inverse Problems. arXiv:2603.24377 (2026). — 物理先验融入扩散模型的一般科学逆问题框架，为 VAE+扩散模型在瞬态 Berry 曲率反演提供架构参照。

[63] A. Ono, S. Okumura, S. Imai, Y. Akagi. High harmonic generation from electrons moving in topological spin textures. *Phys. Rev. B* 110, 125111 (2024). DOI: 10.1103/PhysRevB.110.125111 — 标量手性翻转（Berry 曲率符号反转但能带不变）在固体 HHG 谱中产生可观测的纵向响应调制，定量支持 Berry 曲率可被光谱读取。

[64] D. M. B. Lesko, T. Weitz, S. Wittigschlager, et al. Optical control of electrons in a Floquet topological insulator. arXiv:2407.17917 (2024). — 在石墨烯中用圆偏振基频光产生 Floquet 拓扑绝缘体态，用锁相二次谐波实现全光学异常霍尔效应与光电流圆二色性，首次在固体中实现 FTI 态电子的主动控制。

[65] Z. Zhao, Z. Zheng, Z. Xu, X. Ran, X. Yao, F. Ouyang. Orthogonal attosecond control of solid-state harmonics by optical waveforms and quantum geometry engineering. arXiv:2511.13114 (2025). — 双色场相位调制 + 应变工程实现 WS₂ HHG 正交阿秒控制。+2% 拉伸应变使 K 谷 Berry 曲率积分从 18.24 增至 26.86 Å⁻²，垂直谐波分量近乎翻倍。

[66] X. Zhang, J. van den Brink, J. Li. Impact of crystal symmetries and Weyl nodes on high-harmonic generation in Weyl semimetal TaAs. arXiv:2405.16125 (2024). — Jones 矩阵框架证明 TaAs 中反常谐波完全由晶体对称性决定，HHG 圆二色性无法探测外尔点手征性。界定了从 HHG 谱读拓扑量需要超越传统单参数测量。

[67] A. Di Gaspare, S. Ghayeb, C. Knox, et al. Second and third harmonic generation in topological insulator-based van der Waals metamaterials. *Light Sci. Appl.* 14, 337 (2025). DOI: 10.1038/s41377-025-01847-5 — 在 Bi₂Se₃ 范德华超材料中实验区分体态（仅奇次谐波）与拓扑表面态（奇次+偶次谐波）的非线性贡献，首次观测到来自拓扑表面态的 SHG（χ⁽³⁾ ~10⁻⁹ m²/V²）。

[68] P. Tan, Y. Chen, Y. Zhang, et al. Ultrafast μeV-Precision Bandgap Engineering in Low-Dimensional Topological Insulators. arXiv:2511.16165 (2025). — 在低维拓扑绝缘体中实现 μeV 精度超快带隙工程，利用强场光学手段精确调控拓扑能隙，为准绝热区瞬态拓扑定义提供实验佐证。

[69] X. Zhang, B. Li, L. Zhao, et al. Giant nonlinear optical chirality in twisted heterobilayers. arXiv:2605.17695 (2026). — 在 MoS₂/WSe₂ 扭曲双层中观测到巨非线性光学手性，SHG 展现可调谐的强圆二色响应，为通过结构自由度调控 Berry 曲率耦合提供补充路径。

[70] L. Faeyrman, J. Zhang, M. Ivanov, L.-Y. Peng, N. Dudovich, R. Piccoli. Sub-cycle field-driven dynamical Berry phase in solids. arXiv:2606.02238 (2026). — 在 MgO 中用 THz 场瞬态打破中心对称性，驱动动力学 Berry 相位，在亚 THz 周期内追踪其时域演化，为瞬态 Berry 曲率的时间分辨读取提供了可直接对标的实验验证。

[71] J. Rivera-Dean, L. Petrovic, M. Lewenstein, P. Stammer. Attosecond quantum optical interferometry. arXiv:2511.01097 (2025). — 在 XUV 波段发展了完全量子化的阿秒干涉术（AQI），建立了阿秒量子断层扫描（AQT）协议，可在无独立相位稳定本地振荡器条件下实现谐波量子态的 Wigner 函数重建，为本项目的多通道量子态表征提供了可直接移植的方法论框架。

[72] Y. Yang, Y. Tang, P. Zhang, F. Li. Floquet quantum multiparameter estimation with periodic-driving-induced topological phase transition. arXiv:2605.04463 (2026). — 从量子计量学角度证明 Floquet 驱动的拓扑相变边界可作为量子多参数精密估计资源，在 TPT 边界处量子 Fisher 信息可突破标准量子极限甚至达到海森堡极限，为"在瞬态相变点附近做高精度拓扑量反演"提供了理论依据。
