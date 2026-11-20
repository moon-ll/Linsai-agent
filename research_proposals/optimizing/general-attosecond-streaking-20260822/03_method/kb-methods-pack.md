# 课题方法素材包（KB 自动聚合，v7.2.30 wikilink 节点格式）

- 课题：general-attosecond-streaking-20260822
- 生成时间：2026-11-20T11:40:59Z
- 方法关键词：FROG、HHG、一阶段实测与模拟、但该方法、共同勾勒了该技术、利用角积分探测、区的脉冲表征方法、发展修正的新方法、子档由模拟、征到量子相位测量、拟采用技术、方案的角积分方法、无需辅助测量、条关键论断与方法

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

### [[method-topics/量子光驱动HHG方法|量子光驱动 HHG 方法（BSV / 压缩光 / 输出态层析）]]
页：knowledge/wiki/method-topics/量子光驱动HHG方法.md
专题定位：以非经典光场（亮压缩真空 BSV、压缩态）驱动的 HHG——谐波光的

### [[method-topics/材料体系HHG方法|材料体系 HHG 方法（Weyl 半金属 / 交变磁体 / moiré / 高阶拓扑）]]
页：knowledge/wiki/method-topics/材料体系HHG方法.md
专题定位：四类量子材料的 HHG 指纹、模型栈与判据——每类材料「用什么模型、

### [[method-topics/宏观传播与相位匹配工程|宏观传播与相位匹配工程（气体 / 固体 / 量子驱动）]]
页：knowledge/wiki/method-topics/宏观传播与相位匹配工程.md
专题定位：单原子/单胞响应到宏观谐波输出的传播工程——相位失配的构成、

### [[method-topics/阿秒计量方法体系|阿秒计量方法体系（条纹术 / RABBITT / Wigner 时延）]]
页：knowledge/wiki/method-topics/阿秒计量方法体系.md
专题定位：阿秒时间信息提取的两大实验范式（streaking / RABBITT）与其

## 一、匹配的知识库方法页（8）

### [[methods/FROG|FROG]]
页：knowledge/wiki/methods/FROG.md
摘要：FROG 通过测量频率分辨的门控痕迹（非线性混频自相关迹或激光辅助光电子条纹谱）并以 FROG-CRAB/VTG-FROG 类迭代相位检索（广义投影+梯度下降）同时反演脉冲的时间包络与相位，可扩展至软X射线连续谱重建时域形状与啁啾并提取光电发射时延；新证据表明该重构可显式表述为从含噪二维谱图到脉冲场的贝叶斯统计反演而非纯数值优化问题，把测量噪声建模与不确定性量化纳入反演本体，与投影式迭代检索形成互补路径；同名异义的 CRAB 最优控制以少量随机基函数构成变分随机基对控制场降维参数化，使无梯度优化在高维控制空间可行，Group-CRAB 多智能体并行共识搜索增强对噪声、漂移与局部极值的鲁棒性，与 FROG 表征端构成强场脉冲的设计—测量闭环。  ## 适用边界  标准 FROG-CRAB 反演依赖中心动量近似与迭代收敛性：通道混合、脉冲啁啾与库仑-激光耦合（CLC）下提取的时延/相位相对真值

### [[methods/固体_HHG_理论四路线_SBE___TDDFT___Wannier-Bloch___规范处理|固体 HHG 理论四路线（SBE / TDDFT / Wannier-Bloch / 规范处理）]]
页：knowledge/wiki/methods/固体_HHG_理论四路线_SBE___TDDFT___Wannier-Bloch___规范处理.md
摘要： SBE 在能带色散局部抛物近似下给出截止标度律，把能带、电流与再碰撞相位联系起来；TDDFT 直接计算强场含时电流、对层间耦合与莫尔势不依赖经验参数，但仅适用莫尔周期小（大扭转角）构型；Wannier-Bloch 轨迹把倒空间几何约束直接对应到谐波阶次与倒空间轨迹长度；Berry 连接规范处理以 London/Coulomb 规范差值检验规范不变性。局限：四条路线均只描述理想晶体，扭转角 + 激子预激发 + 层间传播共同作用下的可检验映射尚无单一路线给出，多体修正须作为参数输入耦合项。  <!-- linsai-wikilinks --> ## 关联概念  - [[TDDFT]] - [[层

### [[methods/BSV驱动固体HHG实验|BSV驱动固体HHG实验]]
页：knowledge/wiki/methods/BSV驱动固体HHG实验.md
摘要： Rasputnyi等2024年在Mg:LiNbO₃与非晶硅中实现：单模脉冲25 fs FWHM（相干对照70 fs、同平均强度），光子数0–2×10¹³/脉冲（约2.5 μJ，1.6 μm中心波长），±1 V/Å亚周期电场涨落使4–7次谐波产额较同强度经典光提高5–15倍。  <!-- linsai-wikilinks --> ## 关联概念  _暂无关联概念_ <!-- /linsai-wikilinks --> 

### [[methods/二次谐波产生与HHG轨道角动量上转换|二次谐波产生与HHG轨道角动量上转换]]
页：knowledge/wiki/methods/二次谐波产生与HHG轨道角动量上转换.md
摘要： > ⚙ **管线工作页**（2026-11-01 分类）：本页为课题方案/管线中的操作子步骤，非独立可教学方法——不适用方法页 A 级判据，随母方法页与课题档案维护。 在ZnO/GaSe固态样品中结合二次谐波拓扑荷加倍与高次谐波轨道角动量上转换，来源报告最终TC达到36。

### [[methods/压缩光_HHG_截止方差关系|压缩光 HHG 截止方差关系]]
页：knowledge/wiki/methods/压缩光_HHG_截止方差关系.md
摘要： 对压缩光驱动 HHG，归一化截止方差满足 ΔH²(r)/ΔH²_SQL=exp(−2r)。该指数关系不依赖绝对真空场幅度，因此对纳米尺度模体积的不确定性较稳健。

### [[methods/8_带紧束缚___Houston_基自旋分辨_HHG_正演|8 带紧束缚 + Houston 基自旋分辨 HHG 正演]]
页：knowledge/wiki/methods/8_带紧束缚___Houston_基自旋分辨_HHG_正演.md
摘要： 构造 8 带（4 价带 + 4 导带）紧束缚模型，k 点默认 20³、收敛判据 30³；能带参数取自 ARPES 实验（Krempaský 2024；Osumi 2024），与判据口径表一致。  <!-- linsai-wikilinks --> ## 关联概念  - [[arpes]] <!-- /linsai-wikilinks --> 

### [[methods/EFT_框架下的_valley-resolved_HHG|EFT 框架下的 valley-resolved HHG]]
页：knowledge/wiki/methods/EFT_框架下的_valley-resolved_HHG.md
摘要：构造分层 Hamilton 族 **H_λ(k)=|t/λ|[f(K_τ+λq)σ₊ + h.c.]**：通过尺度变换 a_cc→λa_cc、t→t/λ，在固定 Fermi 速度 v_F 下把 trigonal warping（晶格三度对称破缺）算符从 0 连续调到最近邻紧束缚真实石墨烯强度（λ=1）；λ=0 极限为各向同性 Dirac 锥。  该对称极限构成**严格空检验**：ω-2ω 反旋圆极化场下的谷对比度 P_N 在 λ=0 由选择定则严格为零（非数值巧合）。激光矢势幅 A_0 充当「碰撞能量」角色，**x=λa_cc·A_0 为唯一展开参数**；EFT 幂次计数预言谷奇谐波产量 ∝λ 线性增长、谷偶谐波 ∝λ²，与高维算符的标准 EFT 行为一致。带内动力学用 SBE 求解：H4 在 x≲0.5 内领头 warping 修正即可解释真实石墨烯谷对比至 10% 以内；H4/H5 旋

### [[methods/Bessel-Gauss_选择性准相位匹配单色_HHG|Bessel-Gauss 选择性准相位匹配单色 HHG]]
页：knowledge/wiki/methods/Bessel-Gauss_选择性准相位匹配单色_HHG.md
摘要： 用 Bessel-Gauss 光束实现选择性准相位匹配以获得单色 HHG（论文 2403.04288，正文仅标题级描述）。  <!-- linsai-wikilinks --> ## 关联概念  - [[相位匹配]] <!-- /linsai-wikilinks --> 

## 二、带方法卡的论文页（6）

### [[papers/2026-2603_27477-a-dual-sideband-attosecond-interferometry-setup|双边带阿秒干涉术装置（HHG Ar XUV + He 靶 + NOPA 1200 nm 探针 + 多技术模块）]]
页：knowledge/wiki/papers/2026-2603_27477-a-dual-sideband-attosecond-interferometry-setup.md
参数样例：参数；---；驱动；探针

### [[papers/2024-241119046-noncollinear-phase-matching-of-high-harmonic|固体 HHG 的非共线相位匹配（不对称光子上转换：强场 N+1 光子 + 弱场 1 光子横向动量补偿）]]
页：knowledge/wiki/papers/2024-241119046-noncollinear-phase-matching-of-high-harmonic.md

### [[papers/2026-2601_12098-real-symmetric-hamiltonian-enables-near-linear-scaling-for-f|实对称哈密顿量实现近线性标度费米面提取（实对称嵌入 + shift-invert Arnoldi + LDL/Sylvester 惯性 + KD-tree）]]
页：knowledge/wiki/papers/2026-2601_12098-real-symmetric-hamiltonian-enables-near-linear-scaling-for-f.md
参数样例：参数；---；TB 参数

### [[papers/2024-2410_02973-resolving-polarization-switching-pathways-of-sliding-ferroel|滑移铁电体极化翻转路径分辨的层分辨激子反射对比光谱（双栅 + 1.6 K + 多循环统计）]]
页：knowledge/wiki/papers/2024-2410_02973-resolving-polarization-switching-pathways-of-sliding-ferroel.md
参数样例：参数；---；测量温度；固定掺杂密度

### [[papers/2023-2311_01371-metrological-robustness-of-high-photon-number-optical-cat-st|HHG 猫态的损耗通道 QFI 分析（零差相位估计协议）]]
页：knowledge/wiki/papers/2023-2311_01371-metrological-robustness-of-high-photon-number-optical-cat-st.md

### [[papers/2022-s41467-022-32780-5-attosecond-dynamics-of-multi-channel-single-photon-ionizatio|双光子干涉测量 Ne 原子外层单光子电离的多通道动力学——各角动量电离通道的相位与幅值分别提取（Peschel 等，Nature Communications 2022）]]
页：knowledge/wiki/papers/2022-s41467-022-32780-5-attosecond-dynamics-of-multi-channel-single-photon-ionizatio.md
参数样例：参数；---；对象与手段
