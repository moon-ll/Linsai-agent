## 2604.23506

**标题**：Ultrafast spectroscopy and role of interlayer coupling in high harmonic generation from layered solids
**作者**：Eyal Uzner, Ofer Neufeld（Technion 以色列理工学院，化学与物理学院）
**发表**：2026-04-26，9 页 4 图，physics.optics

### 研究问题（Research Question）
固体高次谐波（HHG）实验中激光几乎总是面内偏振，理论模型也普遍忽略层间跃迁（interlayer hopping）。本文要回答的核心问题是：在面内偏振驱动下，不可忽略的层间耦合能否改变 HHG 的典型发射特征（角度依赖、椭圆率依赖），以及能否从这些特征中定量反演出层间耦合强度。作者进一步追问这种耦合的物理起源——如何把非微扰的 HHG 过程对层间耦合参数做解析处理。

### 研究背景（Background）
固体 HHG 已被广泛用于探测能带结构（9,10）、Berry 曲率（11,12）、Berry 相位（13）、拓扑性质（14–22）、电子-声子相互作用（23–27）和能谷激发（28–32）。在二维/层状材料中，TDDFT 能给出准确预测但难以揭示层间相互作用的角色；半导体布洛赫方程（SBE）可分解电流各项、便于机制分析，但通常只用少数几条带且忽略层间跃迁。已有少数工作研究过含层间耦合的双层体系（49–53），但体相三维层状固体仍缺乏物理研究，层间作用对强场动力学的总体贡献也不清楚。

### 研究方法（Methods）
建立基于 4×4 紧束缚（TB）模型的 SBE 理论，含一阶层间跃迁：面内 2×2 哈密顿量（H₂D，含二阶近邻，β₁₂ = t₁Σ₃e^{ikaⱼ}，α = t₂Σ₆e^{ikbⱼ}），AB 堆垛体相为 3×3 分块矩阵加层间项 β₁₄ = t_z Σ₂e^{ikcⱼ}，能带解析为 E(k) = α ± |β₁₄|/2 ± √(4|β₁₂|² + β₁₄²)。在 Houston 基、长度规范下求解 SBE，4 阶 Runge-Kutta，时间步长 0.1 a.u.，k 网格 600×600×9；退相干时间 T₂ 取 25 fs（石墨）、20 fs（hBN）、5 fs（WS₂）。驱动条件：I₀ = 5×10¹¹ W/cm²，λ = 1600 nm，super-sin 包络共 8 个驱动周期（~21.35 fs FWHM），椭圆偏振由 ε 与主轴角 θ 描述。跃迁偶极 d_mn = i⟨u_m|∇ₖ|u_n⟩ 与动量矩阵元 p_mn = ⟨u_m|∇ₖH₃D|u_n⟩ 均解析给出；HHG 谱为 BZ 积分电流时间导数的傅里叶变换模平方。层间耦合参数 t_z 作为扰动量对 H₂D 展开到一阶。

### 主要发现与核心结论（Main Results）
- 足够强的层间耦合可改变 HHG 发射特征，即使驱动激光完全面内偏振。角度依赖上，石墨 H13 的 θ_max 由 30° 移到 45°（t_z ~ 200 meV）；hBN H9 出现 θ_max 移动（t_z ~ 300 meV）。石墨中 H3/H5/H7 等微扰谐波对 t_z 不敏感、需极大 t_z 才有调制；高阶非微扰谐波才显著移动。
- 椭圆率依赖上，石墨 H11 在 t_z ~ 0.5 eV 附近产额大幅下降、在 t_z ~ 1.2 eV 又回升；H15 效应相反。hBN H14 的 ε_max 由 0（典型类气体行为）移到 ~0.25（t_z ~ 0.5 eV）。这些特征对内带/带间两种发射机制都成立。
- 解析结果：电流 J(t) ≈ a₀(t) + a₁(t)t_z + a₂(t)t_z²（最多两次跃迁事件参与），因此 HHG 产额遵循 4 阶多项式 I⁽ⁿ⁾ ≈ h₀⁽ⁿ⁾ + h₁⁽ⁿ⁾t_z + h₂⁽ⁿ⁾t_z² + h₃⁽ⁿ⁾t_z³ + h₄⁽ⁿ⁾t_z⁴。数值验证（t_z < 100 meV）显示 4 阶多项式的 R² 显著高于简单幂律拟合（例如 H11 θ=0° 时 R² = 0.9988 vs 0.9855；H11 θ=5° 时 0.9993 vs 0.8303），且幂律拟合的 k⁽ⁿ⁾ 常为非整数、有时发散（如 H9 在 t_z > 60 meV 曲线发散）。
- 无能隙体系（石墨/石墨烯）特有结论：纯带内发射时 a₁(t) 消失，故只有 t_z 的偶次幂出现在产额中。
- 物理图像：层间耦合是对面内电子动力学的间接扰动，感应电流"拾取"最高到 t_z 二阶的微扰项，由此产生相对驱动角与椭圆率的独特行为。

### 潜在研究方向（Future Directions）
作者指出本文信号幅度所需的 t_z 仍大于石墨天然值（石墨层间跃迁约 ~20 meV），需在范德华键更强的材料中实现或用外部手段（压力、激光驱动相干声子与 Floquet 模）调制来验证；同时提醒，基于角度/椭圆率产额的固体 HHG 谱学分析需警惕——这些数值会随模型质量而变。层间耦合的"动力学时间调谐"可作为控制 HHG 与阿秒脉冲产生的新工具（gating 方案）。AB 堆垛并非 hBN 等有隙六方体系中最热力学稳定的结构（作者说明为简化分析而作此选择），沿 c 轴直接驱动、更高阶 t_z 项、电子-声子与电子-电子散射的完整处理等均留待后续。

---


## 2412.07779

**标题**：Evolution of Thought: Diverse and High-Quality Reasoning via Multi-Objective Optimization
**作者**：Biqing Qi, Zhouyi Qian, Yiang Luo, Junqi Gao, Dong Li, Kaiyan Zhang, Bowen Zhou（上海人工智能实验室 / 哈工大 / 清华）
**发表**：2024-11-24，cs.NE / cs.AI，CC BY-SA 4.0

> 备注：此篇 ID 与"general-phonon-hhg-20261101"（声子 HHG 偏振依赖）课题主题不匹配——它是多模态大模型推理方法学的计算机科学论文，检索清单可能存在主题漂移。按要求仍作深读笔记。

### 研究问题（Research Question）
核心问题：如何让多模态大模型（MLLM）的推理路径搜索同时优化"答案质量"和"路径多样性"两个目标，而不是像 CoT/ToT/GoT/MCTSr 那样只沿单一质量轴扩展？具体要解决两大缺陷：（1）只按质量剪枝导致收敛到局部最优、路径同质化；（2）父节点之间缺乏有效信息共享，造成搜索膨胀与效率低下。

### 研究背景（Background）
MLLM 在开放式问答、复杂数学与严格逻辑推理上受"黑箱推理"之限，答案易出现因果模糊与内部不一致。CoT 用贪心 top-1 单路径解码，质量提升但多样性受限；ToT 用深度/广度优先扩展树结构；GoT 引入节点聚合但依赖预定义聚合算子、只适合结构化固定状态问题；MCTSr 用动态剪枝提效却仍倾向收敛到少数高分路径。Self-Refine/Reflexion/Refiner 类方法过度依赖反复审议，计算效率低。遗传算法的种群选择、交叉、变异与非支配排序、拥挤距离、精英策略等机制在神经网络领域已有成熟应用，但在（多模态）LLM 推理中尚未被系统利用。

### 研究方法（Methods）
把推理路径搜索形式化为多目标优化（MOO）：目标一为质量 ℳ^Q(A)，采用"参考式打分"（先用 MLLM 生成参考答案再据此打分）以降低采样随机性导致的主观偏差；目标二为新颖度 ℳ^N(A)，由编辑距离项与 Sentence-BERT 语义距离项（1/2 − cos 相似度）加权构成，每轮加入新候选后重算全部已打分答案的新颖度。EoT 三步流程：（1）质量与多样性打分；（2）非支配排序分层，层内按质量分数排序，选出 Pareto 前沿上的父代；（3）交叉（随机取两个父代合并信息）与变异生成子代。CA（Condensation–Aggregation）机制：计算候选集距离矩阵 D(A,A′) = 归一化编辑距离 + 语义距离，用 K-Medoids 聚成 κ 簇，计算各簇平均质量并按降序排序，丢弃质量最低的 m 个簇后聚合生成最终答案。实验用 Qwen2-VL (7B)、LLaVA-NeXT (8B)、Phi-3.5-vision (4.5B)，数据集 MathVista / Math-Vision / GSM8K，指标 Pass@1 与 Pass@K（K=4,8），单张 Nvidia A100 80GB，答案格式 "The Answer is \boxed{}" 精确匹配判分；基线含 Gemini 1.5 Pro、GPT-4V、IO、CoT、Self-Refine（1 次迭代）、MCTSr（4 步扩展）、SPP、MAD（3 智能体 2 轮）、ToT（贪心 2 轮、每轮采样 5 个答案）。

### 主要发现与核心结论（Main Results）
- 质量（Pass@1，Table 1）：EoT 在所有数据集上均优于同底模其他方法。Qwen2-VL：MathVista 45.42（IO 33.25，↑12.17）、Math-Vision 17.11（IO 10.20，↑6.91）、GSM8K 76.50（IO 50.00，↑26.50）、AVG 46.20（↑15.05）；LLaVA-NeXT：21.50 / 13.49 / 49.00，AVG 28.33（↑16.47）；Phi-3.5-vision：29.98 / 13.82 / 62.35，AVG 34.94（↑19.98）。仍略低于 Gemini 1.5 Pro（AVG 51.90）与 GPT-4V（AVG 53.12）。
- 多样性（Pass@K，Table 2）：EoT 全面领先。Pass@8 时 Qwen2-VL EoT AVG 71.13（MathVista 67.50、Math-Vision 51.64、GSM8K 94.25）对比 MCTSr 70.14、ToT 58.67；LLaVA-NeXT EoT AVG 61.73 vs MCTSr 59.63 / ToT 52.00；Phi-3.5-vision EoT AVG 65.66 vs MCTSr 57.71 / ToT 49.83。Phi-3.5 上 EoT 的 Pass@4 AVG 55.31 显著高于 MCTSr 47.43、ToT 33.93。
- 效率（Table 3，生成 K=12 个答案，time 单位 s）：ToT 需 2K 步、每答案 14.62 s；MCTSr 需 3K−1 步、每答案 26.36 s；EoT 需 2K+1 步、每答案 15.23 s——比 MCTSr 明显更快，步数与 ToT 相当。
- 消融：候选数 N = 3/6/9、代数 T = 1/2/3 时 pass@4 最大波动仅 5.13%，说明性能不依赖大规模种群；复杂任务上交叉/变异比 r = 1:5、父代 K = 3 最优；CA 机制仅当簇数 κ > 4 时才带来提升，κ ≤ 4 时因生成答案质量已高、丢弃会限制潜力而无益。

### 潜在研究方向（Future Directions）
作者结论认为 EoT 为启发式推理框架设计提供了新视角，但未展开具体局限。可识别的开放问题包括：质量打分仍依赖 MLLM 自身（参考式打分只是降低偏差，未引入外部验证器或过程奖励）；新颖度依赖编辑距离 + Sentence-BERT 的固定嵌入，跨语言/跨模态语义差异与长答案下的度量有效性未验证；全部实验限于 7B/8B/4.5B 开源多模态模型与数学推理三类基准，未覆盖通用多模态推理、科学问答与开放式生成；演化代数、簇数 κ、丢弃簇数 m 等超参需按任务调优；文中亦未讨论把 CA 机制推广到更复杂的推理结构（多步/带工具调用）时的表现。

---


## 2609.38727

**标题**：Metaphotonics for High-Harmonic Generation
**作者**：Pavel Tonkaev, Anton Rudenko, Ziwen Wang, Tran Trung Luu, Yuri Kivshar（ANU / Laboratoire Hubert Curien / 香港大学）
**发表**：2026-09-30，physics.optics，综述

### 研究问题（Research Question）
本综述要回答的中心问题：亚波长图案化结构（孤立共振器与超表面）能否成为高次谐波产生的新平台，从而绕开体相固体 HHG 必须依赖超高光强、限制可集成性的瓶颈？具体梳理不同共振类型（等离激元、Mie、Fano、BIC、导模共振）在 HHG 中的作用、是否会改写非线性响应的基本定律（选择规则、幂律标度），以及当前有哪些未解问题与可期的新方向。

### 研究背景（Background）
HHG 源自 1988 年 Ferray 等在氩气中的 33 阶（32.2 nm）观测，经 Keldysh 参数、Kuchiev 的再碰撞概念、Kulander/Schafer 的理论与 1993 年 Corkum 三步模型奠定基础；1990 年代后期用 800 nm、40 fs 脉冲在氩中获 19 阶谐波，得到 250 as 脉冲列、间隔 1.35 fs，开辟 EUV 阿秒光源。固体 HHG 自 Ghimire 等 2011 年在 ZnO 晶体中观测到 25 阶开始，已用于能带重建、Berry 曲率探测、晶格动力学时间分辨测量、26 pm 空间分辨率"显微镜"。液态 HHG 2018 年借 flat-jet 技术在纯水与醇类中实现，cutoff 超过 20 eV，后续刷新到 ~50 eV。建模三条主线为 TDSE、SBE、TDDFT，各有哈密顿量选择、独立粒子近似、非平衡交换关联势的局限。HHG 效率随阶数快速下降，推动研究者用纳米结构增强局域场。

### 研究方法（Methods）
文献综述（覆盖 ~195 条参考文献），按物理平台组织：气体→液体→非结构固体→亚波长共振器→超表面→广义概念与新材料→非常规功率标度→结论与展望。关键技术线索包括：等离激元纳米天线/锥形蓝宝石、AlGaAs 准-BIC 纳米谐振器（~3.7 µm 中红外、方位偏振激励）、Si/Si₃N₄ 双层柱磁-电耦合 Mie 模（前后向不对称发射）、Si 条+盘 Fano 超表面、GaP 非中心对称超表面、准-BIC 硅超表面（11 阶）、非晶硅磁偶极阵列、悬空硅膜准-BIC、LiNbO₃ 导模共振（至 7 阶）、Ge 梯度"骨形"超表面、Si-on-sapphire + hBN 极化激元杂化。理论层面归纳 TDSE/SBE/TDDFT 及含非局域项的流体-Maxwell 方法。

### 主要发现与核心结论（Main Results）
- 单谐振器：Carletti 等理论预言高折射率介质纳米球 + ENZ 衬底耦合产生超高 Q 超腔，BIC 增强五次谐波（含级联过程），比常规 Mie 共振高数个量级；Zalogina 等在单个 AlGaAs 纳米谐振器中用准-BIC 模式（~3.7 µm）实验观测到至 7 阶谐波，而同样激发下的无结构 AlGaAs 薄膜无任何可测信号；Si/Si₃N₄ 谐振器呈现前向/后向三次、五次、七次谐波显著不对称，可通过谐振器直径与泵浦波长调谐。
- 超表面：Ginsberg 等在氩 + 全介质超表面实现五次谐波增强达 45 倍；Liu 等硅 Fano 超表面相对无图案硅膜增强超过两个数量级；Zograf 等准-BIC 硅超表面达 11 阶；非晶硅磁偶极超表面约 20 倍增强；悬空硅膜准-BIC 超表面高次谐波增强达 3 个数量级；GaP 超表面因破缺反演对称同时产生偶次与奇次谐波、至第 9 阶；LiNbO₃ 超表面达第 7 阶并进入深紫外；Ge 梯度超表面在宽调谐范围内高效产生三次与五次谐波。
- 杂化平台：Si-on-sapphire 超表面耦合薄层 hBN，中红外声子-极化激元与近红外光子共振双共振匹配，数值计算预测五次谐波产额比单独任一者提升 3 个数量级以上。
- 非常规功率标度：硅准-BIC 超表面共振下 SHG 呈立方依赖而非二次（偏离共振后恢复二次），FHG 呈近二次；悬空硅膜准-BIC 超表面中三、五、七、九阶的有效标度指数分别约为 2.4、3.0、4.6、4.5（对应整数阶 3、5、7、9），七阶相对无结构膜增强约 3 个数量级，九阶仅在共振附近出现；机制归因于 Kerr 引起的折射率变化、自相位调制、共振失谐与腔内场再分布。
- 首次固体 HHG 记录回顾：ZnO 至 25 阶；气体氩至 21 阶（FWHM 峰值 90 a.u.）；水/醇至 >20 eV，纪录 ~50 eV。

### 潜在研究方向（Future Directions）
作者列出明确挑战：整体转换效率（尤其高阶）仍低于传统体相系统，需兼顾强场约束、高损伤阈值与宽带的谐振器；"电子激发显著但尚未造成不可逆结构改变与加热"的最佳脉冲时序设计仍探索不足；亟需能同时处理纳米结构尺度与传播尺度的微观自洽数值方法（TDDFT/TDSE/全 BZ SBE 与 3D 传播不兼容），现有"预计算微观光流 + 逐 meta-atom 组合"路线忽略了超快互耦动力学与空间非局域效应；纳米结构与超表面尚未观测到标志性的"平台—截断"型 HHG 谱，这是进入非微扰区的关键一步；最优激光源（波长、偏振、轨道角动量）、材料与几何的联合优化尚无定论。作者预期三个方向：对高阶谐波振幅与相位的任意逐级按需控制；扩展 HHG 元光子功能（手性光、可重构 XUV 相阵）；阿秒脉冲的产生、控制与表征并最终芯片化。

---

## 2511.13114

**标题**：Orthogonal Attosecond Control of Solid-State Harmonics by Optical Waveforms and Quantum Geometry Engineering
**作者**：Zhenjiang Zhao, Zhihua Zheng, Zhiyi Xu, Xing Ran, Xiaolong Yao, Fangping Ouyang 等
**发表**：2025-11-17（arXiv 预印本，本课题引用轮次当轮经 arXiv 页面核实：标题、作者链与摘要一致）

### 核心结论

单层 WS₂ 的高次谐波产生可由双色场与机械应变工程两种正交手段协同控制：双色场相对相位（Δφ = 0.7π）为电子-空穴对的量子相干提供亚飞秒开关，从而优化谐波发射；拉伸应变调制总谐波产额，并使垂直偏振谐波分量增强近两倍。该增强的来源是双重的——应变改变的能带色散增强带内电流，同时 Berry 曲率的显著重塑大幅提高带间响应中的反常速度贡献。这一量子几何效应表现为谐波产额对应变的稳健单调依赖，以及垂直偏振谐波的显著放大，因而给出一个探测量子几何效应的清晰实验特征。文中把单层 WS₂ 定位为探索阿秒物理的模型体系。

### 与课题的关联

这是本课题能带几何型通道存在的第一性原理量级证据，与本项目"声子位移经由 Berry 曲率与带间极化重塑进入谐波响应"的机制设定直接对应。该文给出的应变—产额单调依赖正是本课题能量标度判据所假定的场强标度在应变轴上的对应物：谐波产额对晶格坐标的响应在本课题中由相干声子位移提供，而非静态应变。

### 已引用位置

- 研究方案 §4.1：论证"几何通道不是主导贡献"这一假定不能默认，因为晶格位移对量子几何的重塑足以产生百分之几十量级的偏振分辨谐波变化
- 研究方案 §7 可行性分析：作为理论模块在通道分解上要对标的范例
- 参考文献 [49]


---

## 2112.10117

**标题**：Effect of interlayer coupling and symmetry on high-order harmonic generation from monolayer and bilayer hexagonal boron nitride
**作者**：Dasol Kim, Yeon Lee, Alexis Chacón, Dong Eon Kim（POSTECH 原子秒科学技术中心）
**发表**：2022 年，Symmetry 14(1), 84；DOI 10.3390/sym14010084（预印本 arXiv:2112.10117，2021-12-19）

### 核心结论
用紧束缚哈密顿量配合半导体布洛赫方程，考察单层与两种堆垛（AB 与 AA'）双层六方氮化硼的高次谐波产生。结论是谐波发射图样强烈依赖三项彼此独立的因素：晶体的反演对称性、旋转对称性与层间耦合。该工作把"点群决定了哪些阶次与哪些偏振组合允许出现"从规则陈述推进为可计算的发射图样，并表明层间耦合作为一项独立于面内对称性的变量会改变图样。

### 与课题的关联
本课题的瞬时对称性破缺通道以"畸变改变点群、允许阶次集合随之改变"为物理机制，该文给出了这一机制在二维六方材料上的计算实现，直接支持本项目选择定则判据的可行性：对称性确实支配发射图样，且图样可由布洛赫方程层面算出，因此本项目的群论核对表不是纸上推演，而是有先例可循的计算对象。层间耦合对图样的独立影响同时说明，层间剪切声子引起的调制有可与面内模区分的偏振指纹，这构成本项目 MoS₂ 分支跨材料对照的理论依据。

### 已引用位置
- 立项依据第 2.5 节：对称性对谐波发射图样的支配在二维材料上的系统检验
- 研究内容第 3 节：MoS₂ 面内模与层间剪切模对照的理论依据
- 参考文献 [39]

---

## 2512.15370

**标题**：Orientation-dependent high harmonic generation in ZnO
**作者**：Tzveta Apostolova, Balint Kiss, Deborata Rajak, Katalin Pirisi, Rajaram Shrestha, Levente Abrok, Boyan Obreshkov, Jean Claude Kieffer, Dimitar Velkov
**发表**：Appl. Phys. B 132, 84 (2026)；DOI 10.1007/s00340-026-08680-7（开放获取）；预印本 arXiv:2512.15370 (2025-12-17)

### 核心结论
理论与实验考察 ZnO 在强中红外飞秒脉冲下的取向依赖高次谐波。理论由六方晶格对称性本身预言 (0001) 面内奇次谐波强度呈六重角调制、(11-20) 面内呈二重角调制，实验却测到四重对称性；作者把差异归因于多带结构的各向异性对电子-空穴激发动力学的作用。实验条件为 3.2 μm、45 fs、峰值强度 1 至 1.2 TW/cm²。

阶次集合与晶面取向的对应关系是本文最具体的数据：(0001) 切片的透射谱只出现奇次阶次并延伸至 13 阶，奇次强度在偏振方位角 0°、45°、90°、135°、180° 处出现峰值；(11-20) 切片的谱中奇次与偶次阶次并存，偶次强度只在方位角 45° 与 135° 处出现峰值。理论给出的直接带隙为 3.3 eV，价带顶三条能带向下色散。作者另指出，晶体双折射效应此前已被报道为造成晶格对称性与实测谐波对称性偏离的原因。

### 核验说明
arXiv v1 摘要写"三重角调制"，刊版摘要与正文写"六重角调制"（(0001) 面）与"二重角调制"（(11-20) 面）。本课题申请书按刊版口径引用六重/二重，并已把参考文献著录改为刊版 Appl. Phys. B 132, 84 (2026)，不再按预印本著录。

### 与课题的关联
本项目选择定则判据的核心命题是"畸变改变点群因而改变允许阶次集合"，而该工作把这条命题的实验面完整暴露出来：晶面取向、偏振方位角与阶次奇偶三者互相锁定，既有可核对的对应（(0001) 切片只有奇次阶次），也有明确的偏离（六重/二重预测 vs 实测四重）。偏离的存在正是本项目判据设计为"零与非零跨模对照"而非"孤立检验一个模"的直接理由——多带各向异性带来的偏离若不预先纳入考虑，就会被误判为通道甄别的失败。该文的偶次阶次方位角依赖（45° 与 135° 峰值）亦为本项目泵浦方位角扫描（间隔 30°、覆盖 60° 扇区）的设计提供实测参照。

### 已引用位置
- 立项依据第 2.5 节：群论规则集的边界，以及阶次集合与晶面取向的实验对应
- 研究内容第 3 节：零与非零对照比孤立检验更必要
- 参考文献 [41]


---

## 参考文献核验回录（2026-11-09）

以下条目在本课题的检索池中此前只有题名或作者姓氏的零散提及，本轮按统一著录规则补入完整记录。题名、作者链、刊名、卷页与 DOI 逐条对照 CrossRef 注册记录核验，预印本对照 arXiv abs 页核验，核验日期 2026-11-09。

### 10.1038/nphys1847
**标题**：Observation of high-order harmonic generation in a bulk crystal
**作者**：S. Ghimire, A. D. DiChiara, E. Sistrunk, N. G. Johnson, A. V. Vampa, C. McKinney, A. M. Ndabashimiye, H. N. Liu（作者前三位著录）
**发表**：Nat. Phys. 7, 138-141 (2011)；DOI 10.1038/nphys1847
**核验出处**：CrossRef api.crossref.org/works/10.1038/nphys1847，题名、卷、页、年、作者链逐字段一致
**与课题的关联**：固体高次谐波的起点文献，本项目 ZnO 材料选择与中红外驱动方案的上游依据。
**已引用位置**：立项依据第 1 节；参考文献 [3]

### 10.1038/nphys3955
**标题**：Anisotropic high-harmonic generation in bulk crystals
**作者**：Yong Sing You, David A. Reis, Shambhu Ghimire
**发表**：Nat. Phys. 13, 345-349 (2017)；DOI 10.1038/nphys3955
**核验出处**：CrossRef api.crossref.org/works/10.1038/nphys3955，题名、卷、页、年、作者链逐字段一致
**与课题的关联**：体相晶体的各向异性谐波发射，与 [3] 共同构成固体高次谐波在体相半导体中的确认序列。
**已引用位置**：立项依据第 1 节；参考文献 [4]

### 10.1038/s41467-018-03397-4
**标题**：Measurement of the Berry curvature of solids using high-harmonic spectroscopy
**作者**：T. T. Luu, H. J. Wörner
**发表**：Nat. Commun. 9, 916 (2018)；DOI 10.1038/s41467-018-03397-4
**核验出处**：CrossRef api.crossref.org/works/10.1038/s41467-018-03397-4，题名、卷、页、年、作者链逐字段一致
**与课题的关联**：Berry 曲率读出的奠基工作，是本项目"能带几何型通道"存在的实验依据。
**已引用位置**：立项依据第 1 节；参考文献 [5]

### 10.1038/s41566-019-0574-4
**标题**：Attosecond spectral singularities in solid-state high-harmonic generation
**作者**：A. Uzan, G. Orenstein, Á. Jiménez-Galán 等 16 位
**发表**：Nat. Photonics 14, 183-187 (2020)；DOI 10.1038/s41566-019-0574-4
**核验出处**：CrossRef api.crossref.org/works/10.1038/s41566-019-0574-4，题名、卷、页、年、作者链逐字段一致
**与课题的关联**：固体谐波谱的相干控制与节点几何读出，与 [5] 共同支撑"能带几何进入强场光谱读出对象"这一论断。
**已引用位置**：立项依据第 1 节；参考文献 [6]

### 10.1103/PhysRevA.93.033852
**标题**：High-order-harmonic generation from periodic potentials driven by few-cycle laser pulses
**作者**：Z. Guan, X. Zhou, X. Bian
**发表**：Phys. Rev. A 93, 033852 (2016)；DOI 10.1103/PhysRevA.93.033852
**核验出处**：CrossRef api.crossref.org/works/10.1103/PhysRevA.93.033852，题名、卷、页、年、作者链逐字段一致
**与课题的关联**：周期势中的少周期驱动固体谐波理论框架之一，用于界定本项目的"玻恩-奥本海默近似"对象。
**已引用位置**：立项依据第 1 节；参考文献 [7]

### 10.1038/s41467-017-00764-5
**标题**：Ellipticity dependence of high-harmonic generation in solids originating from coupled intraband and interband dynamics
**作者**：N. Tancogne-Dejean, O. D. Mücke, F. X. Kärtner, A. D. Falcone
**发表**：Nat. Commun. 8, 745 (2017)；DOI 10.1038/s41467-017-00764-5
**核验出处**：CrossRef api.crossref.org/works/10.1038/s41467-017-00764-5，题名、卷、页、年、作者链逐字段一致
**与课题的关联**：带内与带间动力学耦合的固体谐波框架，是本项目位移电流型与能带几何型两通道划分的模型背景。
**已引用位置**：立项依据第 1 节；参考文献 [8]

### 10.1103/PhysRevLett.122.193901
**标题**：Reciprocal-Space-Trajectory Perspective on High-Harmonic Generation in Solids
**作者**：L. Li, P. Lan, X. Zhu 等 7 位
**发表**：Phys. Rev. Lett. 122, 193901 (2019)；DOI 10.1103/PhysRevLett.122.193901
**核验出处**：CrossRef api.crossref.org/works/10.1103/PhysRevLett.122.193901，题名、卷、页、年、作者链逐字段一致
**与课题的关联**：倒空间量子轨迹模型，把晶格位移直接写进电子轨迹，是本项目"位移电流型通道"的模型出处。
**已引用位置**：立项依据第 1 节；参考文献 [9]

### 10.1126/sciadv.adz5621
**标题**：Isostructural electronic transition in MoS₂ probed by solid-state high-harmonic generation spectroscopy
**作者**：B. R. Nebgen, V. C. Lee, J. A. Spies 等 8 位
**发表**：Sci. Adv. 12, eadz5621 (2026)；DOI 10.1126/sciadv.adz5621
**核验出处**：CrossRef api.crossref.org/works/10.1126/sciadv.adz5621，题名、卷、文章号、年、作者链逐字段一致
**与课题的关联**：等结构电子相变的谐波指纹为偏振各向异性整体旋转约 30°，是本项目把偏振量列为一级观测量的直接依据。
**已引用位置**：立项依据第 2.5 节；研究内容第 2 节；研究方案第 3.2 节；参考文献 [29]

### 10.1126/sciadv.aea7877
**标题**：Ultrafast decoherence in solid-state high-harmonic generation induced by nuclear-electronic entanglement
**作者**：S. Hu, Q. Chen, R. Zhao 等 7 位
**发表**：Sci. Adv. 12, eaea7877 (2026)；DOI 10.1126/sciadv.aea7877
**核验出处**：CrossRef api.crossref.org/works/10.1126/sciadv.aea7877，题名、卷、文章号、年、作者链逐字段一致
**与课题的关联**：核量子效应经由核-电子纠缠诱导电子退相干，给出 σ_ΔR、T₂ 与 √(M_v ω) 的经验关系，是本项目区分"相干分量"与"系综平均"的那条对照计算的先例。
**已引用位置**：立项依据第 4 节；研究方案第 4.6 节；参考文献 [37]

### 10.1021/acs.nanolett.5c05443
**标题**：Dynamical Control of Coulomb Interactions and Hubbard Bands in Monolayer 1T-TaS₂
**作者**：Niklas Notter, Markus Aichhorn, Anna Galler
**发表**：Nano Lett. 26, 4973-4978 (2026)；DOI 10.1021/acs.nanolett.5c05443（arXiv:2510.26584，2025-10-30 预印本）
**核验出处**：CrossRef api.crossref.org/works/10.1021/acs.nanolett.5c05443，题名、卷、页、年、作者链逐字段一致；arXiv abs/2510.26584 页题名与作者链一致、著录 DOI 相同
**核心结论**：单层 1T-TaS₂ 中星形电荷密度波振幅同时调制 Hubbard U 与有效库仑屏蔽，约 3% 的振幅压缩即可使带宽反超库仑作用，驱动 Mott 绝缘体-金属转变，为相干声子实现皮秒内动态调控电子关联提供定量依据。
**与课题的关联**：本项目 1T-TaS₂ 分支的关联调制标定来源，其"电荷密度波振幅至 Hubbard 带位移"的实验定标关系在该文中被明确呼吁建立。
**已引用位置**：立项依据第 2.4 节与第 3 节；研究内容第 4 节；研究方案第 5.2 节；参考文献 [25]

### 10.1364/OE.615079
**标题**：Identifiability limits of scattering from solid-state high-harmonic generation
**作者**：Y. Shi, Y. Gu, S. Chang 等 5 位
**发表**：Opt. Express 34(23), 44127 (2026)；DOI 10.1364/OE.615079
**核验出处**：CrossRef api.crossref.org/works/10.1364/OE.615079，题名、卷、页、年、作者链逐字段一致
**与课题的关联**：从反问题一侧指出固态高次谐波所含散射信息存在可辨识度上限，是本项目把通道份额可辨识性写成显式检验项而非默认成立的直接依据。
**已引用位置**：立项依据第 2.2 节；参考文献 [21]

### 10.1038/s41524-024-01399-z
**标题**：Enhanced high harmonic efficiency through phonon-assisted photodoping effect
**作者**：J. Zhang, O. Neufeld, N. Tancogne-Dejean 等 7 位
**发表**：npj Comput. Mater. 10, 202 (2024)；DOI 10.1038/s41524-024-01399-z
**核验出处**：CrossRef api.crossref.org/works/10.1038/s41524-024-01399-z，题名、卷、文章号、年、作者链逐字段一致
**说明**：定向检索报告曾把该文系于 arXiv:2410.17956，经核验该 arXiv 号实为一篇毫秒脉冲星射电灵敏度论文，与本课题无关；本条以期刊版 DOI 为准，不采用该 arXiv 号。
**核心结论**：含时密度泛函理论耦合经典离子动力学，表明相干光学声子可显著增强固体谐波产率，体相六方氮化硼中横向光学声子（E1u）增强约 20 倍。
**与课题的关联**：声子辅助的光致掺杂效应使声子位移直接改写谐波产额，是本项目"晶格坐标是产额的直接变量"这一命题的定量上游证据。
**已引用位置**：立项依据第 2.1 节；参考文献 [17]

### 10.7693/wl20211102
**标题**：二维材料高次谐波及光波电子学
**作者**：刘灿东, 曾志男, 李儒新
**发表**：物理 50(11), 725-731 (2021)；DOI 10.7693/wl20211102；上线日期 2021-11-12
**核验出处**：CrossRef 未收录中文《物理》；doi.org handle 解析至 http://www.wuli.ac.cn/cn/article/doi/10.7693/wl20211102（http_code=200），期刊页 citation_title / citation_author / citation_journal_title / citation_volume / citation_issue / citation_firstpage / citation_lastpage / citation_publication_date / citation_doi 九项 meta 逐字段读出，与著录完全一致
**与课题的关联**：国内固体高次谐波二维材料侧的综述，支撑本项目"国内研究现状"一节与二维材料分支的定位。
**已引用位置**：立项依据第 4 节；参考文献 [36]

### 10.3788/gzxb20245306.0653210
**标题**：基于 h-BN 的方向依赖高次谐波产生（特邀）
**作者**：郑文洋, 刘灿东, 白亚, 刘鹏, 李儒新
**发表**：光子学报 53, 0653210 (2024)；DOI 10.3788/gzxb20245306.0653210（未见 arXiv 版；检索聚合曾误挂 arXiv:2412.07779——该 ID 实为 cs.AI 论文 Evolution of Thought，见同文件同名深读笔记，2026-11-11 引擎亲审 C3 更正）
**核验出处**：CrossRef api.crossref.org/works/10.3788/gzxb20245306.0653210，题名、卷、文章号、年、作者链逐字段一致；lit-gap 检索记录与之一致（其 ID 字段误挂已注记更正）
**与课题的关联**：截止区奇次谐波的晶格取向依赖出现 30° 角度偏移，是本项目以偏振与取向信息为一级观测量的实测依据。
**已引用位置**：立项依据第 4 节；研究方案第 7 节；参考文献 [38]

---

## 本轮回录的两处池内记录订正

**arXiv:2410.17956 与 arXiv:2311.18407 的著录归属**。定向检索报告把这两条分别系于"体相 h-BN 声子辅助光致掺杂使谐波增强约 20 倍"与"单层及双层 h-BN 高次谐波谱相位的取向依赖（Optics Express, DOI 10.1364/oe.607505）"。经 arXiv abs 页逐条核验，2410.17956 的实际题名为 "Radio sensitivity to a new population of millisecond pulsars in the Sagittarius Dwarf Spheroid"（Gebauer-Werner 等，2024-10-23），2311.18407 的实际题名为 "Weak solutions of Moffatt's magnetic relaxation equations"（Tan，2023-11-30），二者与上述物理内容无关，且后者在 arXiv 上无 journal reference。两项物理内容分别由文献 [17]（npj Comput. Mater. 10, 202，DOI 10.1038/s41524-024-01399-z）与文献 [30]（Symmetry 14(1), 84，DOI 10.3390/sym14010084）承担，参考文献表按后者著录，检索报告中的这两条 arXiv 编号作废。

**文献 [23] 与 [24] 的分工**。[23]（Hu 等，arXiv:2304.09459，2023-04-19）与 [24]（Hu 等，Phys. Rev. Lett. 133, 156901，2024）为同一工作的预印本与期刊扩展版，池内 supplementary-sources-2026-11-06.json 的摘要末句已写明"后扩展发表于 PRL 133, 156901 (2024)"。正文分工为：[23] 用于陈述理论主张（谐波谱携带声子动力学与电子-声子耦合指纹、给出带分辨与模式分辨的读出方案），[24] 用于陈述实验结果（单层二硫化钼中观测到声子调制下谐波信号的相位延迟）。参考文献表在 [23] 条目末尾标注两者的对应关系。
