# 课题方法素材包（KB 自动聚合，v7.2.30 wikilink 节点格式）

- 课题：key-transient-quantum-phase-optical-20260726
- 生成时间：2026-11-16T15:42:01Z
- 方法关键词：Berry、Floquet、HHG、RABBITT、THz、XUV、弱场阿秒脉冲探测、或红外吸收率测量、拟采用技术、收等独立可观测量、曲率已有方法、根本的缺口在测量、线探针并可在模拟、衡态维度下被调控

> 用途：update_method_manual / writer 写方案时的可实施细节来源。
> **v7.2.30 起改 wikilink 节点格式**：每条方法/参数都附 `[[方法页slug]]` 双向链接，
> writer 落盘后由 `kb_pack_wikilink_guard.py` 校验（≥3 引用为达标）。
> 参数必须按参数溯源纪律标注来源；本包为 KB 索引摘要，取参数前读对应页原文。

## 〇、方法专题（6，谱系/选型层）

### [[method-topics/量子几何量测量方法谱系|量子几何量测量方法谱系（Berry 曲率 / 量子度规 / 拓扑数）]]
页：knowledge/wiki/method-topics/量子几何量测量方法谱系.md
专题定位：面向「用 HHG 读出凝聚态量子几何量」这一测量目标的路线谱系——

### [[method-topics/HHG反演方法学|HHG 反演方法学（贝叶斯推断 / 神经网络正则化 / 约束优化）]]
页：knowledge/wiki/method-topics/HHG反演方法学.md
专题定位：从谐波谱反推凝聚态参数（能带色散、跃迁偶极、退相干时间、Berry 曲率、

### [[method-topics/固体HHG数值计算方法体系|固体 HHG 数值计算方法体系（TDSE / SBE / rt-TDDFT / 紧束缚）]]
页：knowledge/wiki/method-topics/固体HHG数值计算方法体系.md
专题定位：强激光入射晶体后谐波谱的数值预言方法——四套范式的理论原理、

### [[method-topics/材料体系HHG方法|材料体系 HHG 方法（Weyl 半金属 / 交变磁体 / moiré / 高阶拓扑）]]
页：knowledge/wiki/method-topics/材料体系HHG方法.md
专题定位：四类量子材料的 HHG 指纹、模型栈与判据——每类材料「用什么模型、

### [[method-topics/阿秒计量方法体系|阿秒计量方法体系（条纹术 / RABBITT / Wigner 时延）]]
页：knowledge/wiki/method-topics/阿秒计量方法体系.md
专题定位：阿秒时间信息提取的两大实验范式（streaking / RABBITT）与其

### [[method-topics/量子光驱动HHG方法|量子光驱动 HHG 方法（BSV / 压缩光 / 输出态层析）]]
页：knowledge/wiki/method-topics/量子光驱动HHG方法.md
专题定位：以非经典光场（亮压缩真空 BSV、压缩态）驱动的 HHG——谐波光的

## 一、匹配的知识库方法页（8）

### [[methods/RABBITT|RABBITT]]
页：knowledge/wiki/methods/RABBITT.md
摘要：RABBITT 用阿秒脉冲串的相邻奇次谐波叠加弱红外场，边带高度 S_SB(τ)=A+Bcos[2ωτ−C]（C=2ωτ_a）随 XUV-IR 延迟以两倍 IR 载频振荡、据此重建谐波拍频，边带振荡相位按标准框架解析分解为 EWS 本征延迟 + 连续-连续跃迁延迟 τ_cc + 原子相位项 τ_A（τ_a≈τ_W+τ_cc），该分解既是单通道延迟反演的标准框架也是多通道与角度/通道分辨光电离延迟提取的实验对应理论框架（边带振荡相位可提取角度与分波分辨时延；边带产额随 XUV-IR 延时的 2ω 振荡相位还可一并提取两光子跃迁矩阵元的复数相位与振幅，实现多通道单光子电离动力学的通道分辨完整表征），且已推广到多边带与高阶跃迁路径共存的情形（双谐波极简配置仅取一对相邻奇次谐波即可避开谐波串扰、干净分离高阶多光子路径并缓解分子低强度下的谱拥塞；氙 4d 亚层已据此分解出数十阿秒量级非零 Wigne

### [[methods/瞬态吸收光谱|瞬态吸收光谱]]
页：knowledge/wiki/methods/瞬态吸收光谱.md
摘要：瞬态吸收光谱通过泵浦—延迟探测记录样品微分吸收（ΔT/T或ΔR/R）随延迟的演化，时间分辨地重建电子与激发态动力学，时间窗口既下探阿秒域、也可延伸到常规fs–ns之外的微秒—秒域（μs–s TA），直接捕捉被俘获载流子、晶格冷却与光电压衰减等慢过程并充当热、光电压与缺陷三类贡献分解的信号源；宽带阿秒XUV瞬态吸收进一步以单脉冲带宽覆盖元素整套芯边（如Ti全M2,3边），首次实现长程电荷密度波（CDW）有序与激子指纹的同时时域追踪，把芯能级探测从单一谱线拓展到全边指纹的同时读出；并可在特征共振（如WS2 A激子）处作差分探测以识别异质结构中来自空间分离层的邻近贡献信号；偏振分辨变体可解耦各向同性布居响应与各向异性矢量响应——瞬态二向色性用XUV偏振相对泵浦偏振平行/垂直两通道差分读出载流子/激子的取向与对称性弛豫，其圆二色性延伸（阿秒圆二色性光谱）则以左/右旋探测光的差分信号直接读出空穴环电

### [[methods/TDSE求解器|TDSE求解器]]
页：knowledge/wiki/methods/TDSE求解器.md
摘要：TDSE求解器通过数值求解含时薛定谔方程给出强场体系的第一性原理响应：既作为深度学习正/逆网络的物理引擎批量生成带物理标签训练集（单活性电子TDSE生成脉冲参数-光电子动量谱数据对），又作为机器学习仿真器的真值与训练数据来源提供量子动力学样本供仿真器学习，并在贝叶斯参数估计中充当似然函数的物理内核、把待估参数映射为时间分辨可观测量供与数据比对，还作为量子计量学基准验证SFA框架Fisher信息结论、与SFA量子轨迹联用验证电子波包干涉并提取势垒下电离轨迹参数；在量子光HHG方向经TDSE/SFA校验确立偶次谐波幅值对2ω场强的线性标度（源于微扰展开与选择律，论证性外推至库仑修正与固体HHG），支撑BSV双色驱动下高斯纠缠谐波态与量子隐形传态优势边界的解析刻画，且量子化BSV驱动场模型表明谐波偶极辐射继承驱动场压缩与关联结构、是Wigner负性出现的根源；在含库仑（模型）势模拟中作为真值已知

### [[methods/floquet-engineering|floquet-engineering]]
页：knowledge/wiki/methods/floquet-engineering.md
摘要：Floquet工程以周期光场将固体哈密顿量化为Floquet-Bloch准能级与边带，其严格基础是Sambe扩展希尔伯特空间中把时间作为坐标的 K = H(t) − i∂_t 本征问题（给出准能量谱与周期性本征射线并作为绝热展开的严格基，该扩展空间静态本征问题表示还支持逐准能隙含反常π能隙的绕数/动态不变量拓扑分析、判定对称性约束破缺并区分无静态对应的驱动诱导边界态），将该Sambe扩展推进到BdG哈密顿量的光子扇区可精确加倍Cooper对关联流形（对称性加倍机制）并在Sigrist-Ueda/Balian-Werthamer自旋-宇称分类中新增Floquet频率宇称量子数、预言奇频-奇宇称-轨道单重态新配对通道及Floquet Majorana平带，高频非共振时Floquet-Magnus/van Vleck/Floquet-Schrieffer-Wolff展开可将其约化为时间平均的静态

### [[methods/固体_HHG_理论四路线_SBE___TDDFT___Wannier-Bloch___规范处理|固体 HHG 理论四路线（SBE / TDDFT / Wannier-Bloch / 规范处理）]]
页：knowledge/wiki/methods/固体_HHG_理论四路线_SBE___TDDFT___Wannier-Bloch___规范处理.md
摘要： SBE 在能带色散局部抛物近似下给出截止标度律，把能带、电流与再碰撞相位联系起来；TDDFT 直接计算强场含时电流、对层间耦合与莫尔势不依赖经验参数，但仅适用莫尔周期小（大扭转角）构型；Wannier-Bloch 轨迹把倒空间几何约束直接对应到谐波阶次与倒空间轨迹长度；Berry 连接规范处理以 London/Coulomb 规范差值检验规范不变性。局限：四条路线均只描述理想晶体，扭转角 + 激子预激发 + 层间传播共同作用下的可检验映射尚无单一路线给出，多体修正须作为参数输入耦合项。  <!-- linsai-wikilinks --> ## 关联概念  - [[TDDFT]] - [[层

### [[methods/高次谐波光谱|高次谐波光谱（采集与判读）]]
页：knowledge/wiki/methods/高次谐波光谱.md
摘要：高次谐波光谱方法学覆盖 XUV/HUV 谐波谱的采集、标定与判读三段：**采集**用平场谱仪（变线距凹面光栅 + MCP/CCD，单发覆盖宽谱窗）或光栅单色仪；**标定**用已知发射线定波长轴、用滤片组定效率曲线；**判读**从谱形提取平台/截止结构、奇偶阶次比与支路强度，连接到能带与量子几何信息。  ## 参数表  | 要素 | 数值/要点 | 出处 | | --- | --- | --- | | 平场谱仪 | 变线距凹面光栅（VLS），像差修正后单发覆盖数十 eV 窗，XUV 段分辨率 ~0.1–0.5 eV | [1] | | 波长标定 | 已知线（He/Ne 放电线、已标定谐波阶次）定轴；能量轴不确定度与光栅焦面拟合残差挂钩 | [1] | | 判读口径 | 截止阶次 q_max 由平台末端下降沿判读；带隙内/上阶次判读按 q·ℏω₀ 与 E_g 比较（缺席阶次标注而非充数） |

### [[methods/半经典动力学方程贝里曲率反常速度|半经典动力学方程（贝里曲率反常速度项）]]
页：knowledge/wiki/methods/半经典动力学方程贝里曲率反常速度.md
摘要：半经典波包动力学中，贝里曲率通过反常速度项 v_anom=(e/ħ)E×Ω(k) 将瞬态电流映射为非平衡占据上的Berry曲率加权积分，是绝热霍尔响应的标准框架；新证据进一步表明，该方程在贝里曲率热点的非绝热区失效，需引入贝里曲率的普适延拓来描述非绝热霍尔效应。  ## 参数表  **联网检索升级**（2026-11-01，引用已核实）：半经典波包动力学方程组（Xiao–Chang–Niu RMP 2010 综述标准形式）——**$\dot{r} = (1/\hbar)∂ε_n/∂k − \dot{k}×Ω_n(k)$**（群速度 + 反常速度）、**$\hbar\dot{k} = −eE − e\dot{r}×B$**（加速度定理 + Lorentz）——Berry 曲率以反常速度进入输运与光学响应，是带内 HHG 通道几何依赖的解析来源。二阶半经典玻尔兹曼在此基础上加散射项做非线性输运

### [[methods/阿秒条纹相机|阿秒条纹相机]]
页：knowledge/wiki/methods/阿秒条纹相机.md
摘要：阿秒条纹相机以飞秒强红外激光场作条纹场（红外矢势充当阿秒时钟），在光电离瞬间通过IR矢势调制光电子末态动能/动量、把发射时刻映射为能量偏移，扫描XUV/X射线脉冲与IR延迟、由条纹能移随延迟的变化重构谱图并重构XUV时域相位，即可逐电离通道提取streaking及Wigner光发射延迟（ts=tEWS+tCLC+tDLC，从头模拟可直接重现实验可测条纹谱并反演通道依赖的条纹相移/延迟，揭示shake-up相对延迟主要由剩余离子-光电子相互作用主导且强烈依赖发射方向），同时可由streaking谱反演直接表征XUV脉冲宽度与发射时序（如80 eV XUV脉冲）并实验验证相位匹配门控等孤立阿秒脉冲产生机制，适用范围已由XUV拓展至K边/水窗软X射线并直接测得短至18 as的孤立脉冲、且在X射线（分子电离）波段建立了由条纹能移提取Wigner延迟的完整分析流程（其动量谱提延迟精度已被系统评估，a

## 二、带方法卡的论文页（6）

### [[papers/2025-2508_00296-tracking-doublon-holon-dynamics-in-high-harmonic-generation|Sr₂CuO₃ Mott 绝缘体 HHG 中 doublon-holon 动力学的亚周期追踪（反射 HHG + tr-反射 + tdDMFT/NCA）]]
页：knowledge/wiki/papers/2025-2508_00296-tracking-doublon-holon-dynamics-in-high-harmonic-generation.md
参数样例：参数；---；MIR；tdDMFT 参数

### [[papers/2026-2510_16546-high-harmonic-generation-light-source-with-polariz|偏振可编程 HHG 光源（多材料筛选：TMDC/拓扑绝缘体/外延双层石墨烯 + SHG/MIR 双驱动）]]
页：knowledge/wiki/papers/2026-2510_16546-high-harmonic-generation-light-source-with-polariz.md
参数样例：参数；---；材料；激光

### [[papers/2025-2511_18362-attosecond-resolved-quantum-fluctuations-of-light-and-matter|BSV 微扰双色 HHG：单发光子统计 + 原位四缝干涉量子态层析 + 隧穿涨落阿秒分辨]]
页：knowledge/wiki/papers/2025-2511_18362-attosecond-resolved-quantum-fluctuations-of-light-and-matter.md
参数样例：参数；---；驱动构型；对称性关系

### [[papers/2026-2603_27477-a-dual-sideband-attosecond-interferometry-setup|双边带阿秒干涉术装置（HHG Ar XUV + He 靶 + NOPA 1200 nm 探针 + 多技术模块）]]
页：knowledge/wiki/papers/2026-2603_27477-a-dual-sideband-attosecond-interferometry-setup.md
参数样例：参数；---；驱动；探针

### [[papers/2026-2607_28491-drumhead-surface-states-of-rhombohedral-graphite-with-near-i|菱方石墨鼓面态近理想量子几何的第一性原理核验（DFT+Wannier+Wilson loop+Kubo QGT 空间分辨）]]
页：knowledge/wiki/papers/2026-2607_28491-drumhead-surface-states-of-rhombohedral-graphite-with-near-i.md
参数样例：参数；---；计算设置；DSS 曲率定量

### [[papers/2026-2607_13863-ultrafast-altermagnetophononics|第一性原理 + 自旋群对称性分析 + 非平衡晶格动力学 + 双色 THz 和频激发方案（超快交变磁声子学）]]
页：knowledge/wiki/papers/2026-2607_13863-ultrafast-altermagnetophononics.md
参数样例：参数；---；双色 THz 频率；泵浦偏振
