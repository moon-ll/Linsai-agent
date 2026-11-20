# 课题方法素材包（KB 自动聚合，v7.2.30 wikilink 节点格式）

- 课题：general-quantum-geometry-inversion-20260726
- 生成时间：2026-10-30T16:10:25Z
- 方法关键词：Berry、DMFT、HHG、固体高次谐波光谱、次独立测量

> 用途：update_method_manual / writer 写方案时的可实施细节来源。
> **v7.2.30 起改 wikilink 节点格式**：每条方法/参数都附 `[[方法页slug]]` 双向链接，
> writer 落盘后由 `kb_pack_wikilink_guard.py` 校验（≥3 引用为达标）。
> 参数必须按参数溯源纪律标注来源；本包为 KB 索引摘要，取参数前读对应页原文。

## 一、匹配的知识库方法页（8）

### [[methods/统一Hamiltonian框架的rt-TDDFT|统一Hamiltonian框架的rt-TDDFT]]
页：knowledge/wiki/methods/统一Hamiltonian框架的rt-TDDFT.md
摘要：统一Hamiltonian框架的rt-TDDFT通过实时传播含时Kohn-Sham/TDSE方程追踪强场电子动力学，通道完备性要点依然成立——实时传播Kohn-Sham轨道直接给出含时宏观电流的傅里叶谱，带内与带间HHG发射通道同时天然包含而无需通道分离假设（rt-TDDFT第一性原理同时含带内与带间电流，全谱量化键长-截止能量关系，避免紧束缚/两带模型对能带结构的简化误差）；Floquet拓扑分支——TDDFT含时模拟在双色（ω–2ω）圆偏振强场下第一性原理重现光修饰能带结构与光电子谱，区分Floquet杂化隙与多光子边带贡献；交错磁自旋动力学分支——RT-TDDFT直接模拟线偏激光脉冲下RuO2飞秒自旋动力学，给出光致净磁化约0.2 μB/晶胞；频率混合谱学分支——多外场实时TDSE/TDDFT传播为非微扰区非线性光学提供不依赖微扰展开的模拟框架；磁-晶格动力学分支——非共线自旋rt-

### [[methods/berry|Berry 曲率偶极（BCD）分析]]
页：knowledge/wiki/methods/berry.md
摘要：Berry 曲率偶极（BCD）分析通过动量空间中 Berry 曲率分布的一阶矩描述非中心对称体系的二阶响应，新证据表明其解析框架可推广到温度梯度驱动的横向非线性能斯特/热输运、与电学非线性霍尔形成互补读出通道，且光驱动体系的 Berry 曲率存在闭式公式，可在能隙处定位曲率热点并追踪其随光场的演化。  ## 适用边界  BCD 仅在空间反演破缺（时间反演可保持）的体系中非零，温度梯度与电场驱动的解析表达均基于半经典小扰动展开，光驱动闭式曲率结果依赖特定能带模型近似，强场或强梯度下需高阶修正。  ## 代表作  - paper:2025-2505.16999-nonlinear-thermal-and-thermoelectric-transport-from-quantum - paper:2026-2603.29106-exploring-non-trivial-band-structu

### [[methods/EFT_框架下的_valley-resolved_HHG|EFT 框架下的 valley-resolved HHG]]
页：knowledge/wiki/methods/EFT_框架下的_valley-resolved_HHG.md
摘要：构造分层 Hamilton 族 **H_λ(k)=|t/λ|[f(K_τ+λq)σ₊ + h.c.]**：通过尺度变换 a_cc→λa_cc、t→t/λ，在固定 Fermi 速度 v_F 下把 trigonal warping（晶格三度对称破缺）算符从 0 连续调到最近邻紧束缚真实石墨烯强度（λ=1）；λ=0 极限为各向同性 Dirac 锥。  该对称极限构成**严格空检验**：ω-2ω 反旋圆极化场下的谷对比度 P_N 在 λ=0 由选择定则严格为零（非数值巧合）。激光矢势幅 A_0 充当「碰撞能量」角色，**x=λa_cc·A_0 为唯一展开参数**；EFT 幂次计数预言谷奇谐波产量 ∝λ 线性增长、谷偶谐波 ∝λ²，与高维算符的标准 EFT 行为一致。带内动力学用 SBE 求解：H4 在 x≲0.5 内领头 warping 修正即可解释真实石墨烯谷对比至 10% 以内；H4/H5 旋

### [[methods/现代极化理论与Berry相位计算|现代极化理论/Berry相位极化计算]]
页：knowledge/wiki/methods/现代极化理论与Berry相位计算.md
摘要：现代极化理论将晶体极化定义为绝热过程中占据态布洛赫波函数沿k点串累积的Berry相位，极化仅在两结构差值意义下有定义（以量子eR/Z取模），本组据此定量提取滑移铁电的面外极化及其随层间堆叠的翻转，并支撑滑移极化与自旋-能谷耦合强度的线性标度；新证据进一步将Berry联络/曲率纳入量子几何张量统一框架——其实部为量子度规（支配光吸收、非线性电导、体光伏等光学响应），虚部为Berry曲率（其布里渊区积分经TKNN公式给出Hall输运），子丛几何表述与X波磁体综述均在该框架下统一刻画度规与曲率，Berry相位极化计算即这一几何对象在极化差分提取中的具体实现。  ## 参数表  | 参数 | 数值 | 出处 | | --- | --- | --- | | 量子度规-曲率逐点约束 det g_n^{μν}(k) | ≥ (Ω_n^{xy}/2)^2，无量纲 | paper:2025-2512.054

### [[methods/bsv-driven-hhg-quantum_课题理论三角|bsv-driven-hhg-quantum 课题理论三角]]
页：knowledge/wiki/methods/bsv-driven-hhg-quantum_课题理论三角.md
摘要：三角三支（课题 03_method/kb-methods-pack 定义）：  1. **输入态表征**：[[2608.16027]] —— BSV 驱动场的量子态表征（光子统计/Wigner 函数）； 2. **输入态→电子动力学解析连接**：[[2604.09284]] —— 量子光场如何映射到强场电子响应； 3. **输出态**：[[2410.15503]] —— HHG 输出光场的量子态（谐波光子统计/纠缠）。  配套方法族（三部曲 + 闭环电离端）： - [[2604.06707]]：BSV-driven HHG **谐波端**； - [[2604.06703]]：BSV-only **电离端**； - [[2610.16077]]（Q-CCSFA）：电离端的相敏反演——「量子光场→强场过程→量子光场可读出」闭环的方法基座。  课题 A 延伸：气相 action phase 分解

### [[methods/dmft|dmft]]
页：knowledge/wiki/methods/dmft.md
摘要：DMFT 将晶格强关联电子模型以局域自能自洽映射为量子杂质问题，既可在模型层面解析 U 驱动的金属–绝缘体相变与轨道选择性 Mott 转变全相图（含单轨道 Hubbard 模型中的隐藏 Kondo 晶格物理），也可经非平衡/含时扩展计算 Mott 体系 THz 非线性光学响应（AFM 绝缘相谐波由自旋-电荷/轨道-电荷耦合主导、金属相来自重整化带内电流等相区依赖机制仍然成立）；结合 cRPA 的 DFT+DMFT 可进一步从第一性原理建立晶格畸变与关联的定量联系：CDW 振幅通过改变轨道局域化与电子屏蔽调制有效 Hubbard U，使 Hubbard 带随 CDW 振幅协同移动，减小畸变可驱动 Mott 绝缘体向关联金属转变（如单层 1T-TaS2），为光控二维关联相提供微观机制。  ## 参数表  | 参数 | 数值 | 出处 | | --- | --- | --- | | Mott 能

### [[methods/PIMD___rt-TDDFT_模拟液态水核量子_HHG|PIMD + rt-TDDFT 模拟液态水核量子 HHG]]
页：knowledge/wiki/methods/PIMD___rt-TDDFT_模拟液态水核量子_HHG.md
摘要：基于**电子-核时间尺度分离**（激光驱动仅几 fs，核运动可忽略；液结构涨落为百 fs–ps）将量子核统计与超快电子动力学**显式解耦**：  1. **PIMD 构型采样**：用 PIGLET 加速的路径积分分子动力学采样含核量子离域（零点运动）的液态水构型系综； 2. **frozen-ion 快照传播**：每个构型作为冻结核快照，实时 TDDFT 传播强场下的电子动力学，逐快照计算 HHG 谱； 3. **系综平均**：对系综平均得宏观谱。该分离同时冻结了电声耦合的动力学部分，使液结构对超快动力学的影响可被单独检验。  **配套诊断协议**（本方法的方法论增量）：  - **相干/非相干谱分解**：S(ω)=|⟨I_k⟩|² 与 S_in(ω)=⟨|I_k|⟩² 的偏离直接量化跨快照相干性，配合复相位箱线图——无需演化密度矩阵即可把 dephasing 归因于液结构统计平均； -

### [[methods/瞬态吸收光谱|瞬态吸收光谱]]
页：knowledge/wiki/methods/瞬态吸收光谱.md
摘要：瞬态吸收光谱通过泵浦—延迟探测记录样品微分吸收随延迟的演化，时间分辨地重建电子与激发态动力学；在光学飞秒区，中红外泵浦—宽带探测构型可分辨固体（如ZnO单晶）中强场瞬时可逆的带边红移，从而把快电子响应与热效应、损伤等慢过程区分开；现已延伸至水窗软X射线阿秒区——用孤立19.2 as、中心243 eV并跨越碳K边的超宽带脉冲实现元素/位点特异性芯能级瞬态测量（此类亚原子单位时间脉冲的时域波形须以阿秒条纹术，即同步IR条纹场把X射线波形编码进光电子动量谱直接诊断——该条纹计时范式现已由光学高次谐波推进到硬X射线波段：在XFEL（LCLS）上以阿秒X射线脉冲触发芳香分子芯能级电离、IR弱场作相位计时，提取百阿秒量级发射时延；相应阿秒条纹谱图记录XUV光电离电子动量随XUV–IR延迟的偏移，是延迟信息的直接来源，经解析拟合可实现绝对延迟定标；其近圆偏振变体角向条纹/阿秒钟则以近圆偏振场把电离时刻映

## 二、带方法卡的论文页（6）

### [[papers/2025-2508_00296-tracking-doublon-holon-dynamics-in-high-harmonic-generation|Sr₂CuO₃ Mott 绝缘体 HHG 中 doublon-holon 动力学的亚周期追踪（反射 HHG + tr-反射 + tdDMFT/NCA）]]
页：knowledge/wiki/papers/2025-2508_00296-tracking-doublon-holon-dynamics-in-high-harmonic-generation.md
参数样例：参数；---；MIR；tdDMFT 参数

### [[papers/2025-2511_18362-attosecond-resolved-quantum-fluctuations-of-light-and-matter|BSV 微扰双色 HHG：单发光子统计 + 原位四缝干涉量子态层析 + 隧穿涨落阿秒分辨]]
页：knowledge/wiki/papers/2025-2511_18362-attosecond-resolved-quantum-fluctuations-of-light-and-matter.md
参数样例：参数；---；驱动构型；对称性关系

### [[papers/2026-2607_16477-measuring-the-dipole-phase-of-bloch-trajectory-har|单片共路干涉仪测量固体 HHG 偶极相位（强度-z 联合扫描 + Bloch 振荡轨迹归因）]]
页：knowledge/wiki/papers/2026-2607_16477-measuring-the-dipole-phase-of-bloch-trajectory-har.md
参数样例：参数；---；激光系统；样品

### [[papers/2025-2510_16672-phase-matching-of-high-harmonic-generation-in-twisted-van-de|扭转范德华晶体的 Pancharatnam–Berry 相位匹配——moiré 倒格矢准动量补偿实现 hBN 五次谐波 4×10⁻⁵ 转换效率纪录与纯圆偏振发射（北大刘开辉/洪昊组，PRL 135, 166902, 2025）]]
页：knowledge/wiki/papers/2025-2510_16672-phase-matching-of-high-harmonic-generation-in-twisted-van-de.md
参数样例：参数；---；关键数据；机制

### [[papers/2024-241119046-noncollinear-phase-matching-of-high-harmonic|固体 HHG 的非共线相位匹配（不对称光子上转换：强场 N+1 光子 + 弱场 1 光子横向动量补偿）]]
页：knowledge/wiki/papers/2024-241119046-noncollinear-phase-matching-of-high-harmonic.md

### [[papers/2610.15251|EFT 分层 Hamilton 族 H_λ（可调 trigonal warping 的谷分辨 HHG 探针框架）]]
页：knowledge/wiki/papers/2610.15251.md
参数样例：参数；---；warping 耦合 λ；EFT 展开参数 x=λa_cc·A_0
