# 课题方法素材包（KB 自动聚合，v7.2.30 wikilink 节点格式）

- 课题：general-mos2-20260905
- 生成时间：2026-10-30T16:10:26Z
- 方法关键词：Berry、HHG、RABBITT、SHG、TDDFT、XUV、上分别测量、信息给出直接测量、光路与装置、分辨取决于光泵浦、反演在同一条测量、可见泵浦、各覆盖不同的测量、拟采用技术

> 用途：update_method_manual / writer 写方案时的可实施细节来源。
> **v7.2.30 起改 wikilink 节点格式**：每条方法/参数都附 `[[方法页slug]]` 双向链接，
> writer 落盘后由 `kb_pack_wikilink_guard.py` 校验（≥3 引用为达标）。
> 参数必须按参数溯源纪律标注来源；本包为 KB 索引摘要，取参数前读对应页原文。

## 一、匹配的知识库方法页（8）

### [[methods/PIMD___rt-TDDFT_模拟液态水核量子_HHG|PIMD + rt-TDDFT 模拟液态水核量子 HHG]]
页：knowledge/wiki/methods/PIMD___rt-TDDFT_模拟液态水核量子_HHG.md
摘要：基于**电子-核时间尺度分离**（激光驱动仅几 fs，核运动可忽略；液结构涨落为百 fs–ps）将量子核统计与超快电子动力学**显式解耦**：  1. **PIMD 构型采样**：用 PIGLET 加速的路径积分分子动力学采样含核量子离域（零点运动）的液态水构型系综； 2. **frozen-ion 快照传播**：每个构型作为冻结核快照，实时 TDDFT 传播强场下的电子动力学，逐快照计算 HHG 谱； 3. **系综平均**：对系综平均得宏观谱。该分离同时冻结了电声耦合的动力学部分，使液结构对超快动力学的影响可被单独检验。  **配套诊断协议**（本方法的方法论增量）：  - **相干/非相干谱分解**：S(ω)=|⟨I_k⟩|² 与 S_in(ω)=⟨|I_k|⟩² 的偏离直接量化跨快照相干性，配合复相位箱线图——无需演化密度矩阵即可把 dephasing 归因于液结构统计平均； -

### [[methods/统一Hamiltonian框架的rt-TDDFT|统一Hamiltonian框架的rt-TDDFT]]
页：knowledge/wiki/methods/统一Hamiltonian框架的rt-TDDFT.md
摘要：统一Hamiltonian框架的rt-TDDFT通过实时传播含时Kohn-Sham/TDSE方程追踪强场电子动力学，通道完备性要点依然成立——实时传播Kohn-Sham轨道直接给出含时宏观电流的傅里叶谱，带内与带间HHG发射通道同时天然包含而无需通道分离假设（rt-TDDFT第一性原理同时含带内与带间电流，全谱量化键长-截止能量关系，避免紧束缚/两带模型对能带结构的简化误差）；Floquet拓扑分支——TDDFT含时模拟在双色（ω–2ω）圆偏振强场下第一性原理重现光修饰能带结构与光电子谱，区分Floquet杂化隙与多光子边带贡献；交错磁自旋动力学分支——RT-TDDFT直接模拟线偏激光脉冲下RuO2飞秒自旋动力学，给出光致净磁化约0.2 μB/晶胞；频率混合谱学分支——多外场实时TDSE/TDDFT传播为非微扰区非线性光学提供不依赖微扰展开的模拟框架；磁-晶格动力学分支——非共线自旋rt-

### [[methods/RABBITT|RABBITT]]
页：knowledge/wiki/methods/RABBITT.md
摘要：RABBITT 用阿秒脉冲串相邻奇次谐波叠加弱红外场，边带高度 S=A+Bcos[2ωτ+C]（C=2ωτ_a）随 XUV-IR 延迟以两倍 IR 载频振荡、据此重建谐波拍频，边带振荡相位按标准框架解析分解为 EWS 本征延迟 + 连续-连续跃迁延迟 τ_cc + 原子相位项 τ_A（τ_R≈τ_W+τ_cc），该分解既是单通道延迟反演的标准框架也是多通道与角度/通道分辨光电离延迟提取的实验对应理论框架（边带相位振荡可提取角度与分波分辨的时延，为分波延迟差的理论预测提供实验验证），且已推广到多边带与高阶跃迁路径共存的情形（双谐波极简配置仅取一对相邻奇次谐波即可避开谐波串扰、干净分离高阶多光子路径、允许从两谐波之外的干涉带读取振荡并缓解分子低强度下的谱拥塞；氙 4d 亚层已据此分解出数十阿秒量级非零 Wigner 与 cc 分量且脉冲谱相位整形可主动偏移所测延迟，高谱分辨 RABBITT 可

### [[methods/瞬态吸收光谱|瞬态吸收光谱]]
页：knowledge/wiki/methods/瞬态吸收光谱.md
摘要：瞬态吸收光谱通过泵浦—延迟探测记录样品微分吸收随延迟的演化，时间分辨地重建电子与激发态动力学；在光学飞秒区，中红外泵浦—宽带探测构型可分辨固体（如ZnO单晶）中强场瞬时可逆的带边红移，从而把快电子响应与热效应、损伤等慢过程区分开；现已延伸至水窗软X射线阿秒区——用孤立19.2 as、中心243 eV并跨越碳K边的超宽带脉冲实现元素/位点特异性芯能级瞬态测量（此类亚原子单位时间脉冲的时域波形须以阿秒条纹术，即同步IR条纹场把X射线波形编码进光电子动量谱直接诊断——该条纹计时范式现已由光学高次谐波推进到硬X射线波段：在XFEL（LCLS）上以阿秒X射线脉冲触发芳香分子芯能级电离、IR弱场作相位计时，提取百阿秒量级发射时延；相应阿秒条纹谱图记录XUV光电离电子动量随XUV–IR延迟的偏移，是延迟信息的直接来源，经解析拟合可实现绝对延迟定标；其近圆偏振变体角向条纹/阿秒钟则以近圆偏振场把电离时刻映

### [[methods/TDSE求解器|TDSE求解器]]
页：knowledge/wiki/methods/TDSE求解器.md
摘要：TDSE求解器通过数值求解含时薛定谔方程给出强场体系的第一性原理响应：既可作为物理引擎为深度学习正/逆网络生成带物理标签的训练集（与SFA类方法并列，可由单活性电子TDSE批量生成脉冲参数-光电子动量谱数据对），也可作为量子计量学基准验证SFA框架下的Fisher信息结论，还可与SFA量子轨迹分析联用验证电子波包干涉图样并提取势垒下电离的量子轨迹参数；在含库仑（模型）势的数值模拟中作为数值精确基准生成真值时间延迟已知的合成条纹谱数据集，可升级为双电子全关联TDSE从头求解He在XUV+IR场下的两电子演化、为条纹/shake-up光发射提供不含单活性电子近似的严格基准（双电子TDSE亦可为He shake-up各通道提供含相位的角分辨双光子矩阵元、充当全部延迟分析的基准数据），并可经含时R-matrix（RMT）内外区耦合的多体TDSE把全关联含时求解推进至F⁻九电子体系、量化多体关联对a

### [[methods/tr-shg|时间分辨二次谐波产生（TR-SHG）]]
页：knowledge/wiki/methods/tr-shg.md
摘要：TR-SHG 采用泵浦–探测构型，通过对称性敏感的二阶非线性光学通道读出瞬态对称破缺，作为分辨量子材料中隐藏相与结构序演化的互补探针（注：本轮另一线索属 HHG 方法，不并入本页）。  ## 适用边界  仅对耦合到二阶极化率的瞬态对称性变化敏感，属间接读出通道，需与其他互补探针联用才能唯一指认隐藏相/结构序，且信号通常较弱、需逐延迟扫描。  ## 代表作  - arXiv:2610.11126  ## 证据日志  - 2026-10-09｜r60｜仅简报｜[paper:2026-2610.11126-probing-and-manipulating-quantum-materials-with-st] 时间分辨二次谐波产生（TR-SHG）：以对称性敏感的非线性光学通道读出瞬态对称破缺，是分辨隐藏相与结构序演化的互补探针。 - 2026-10-09｜r60｜仅简报｜[paper:2026-2

### [[methods/B-spline_TDDFT_计算场自由_EWS_时延|B-spline TDDFT 计算场自由 EWS 时延]]
页：knowledge/wiki/methods/B-spline_TDDFT_计算场自由_EWS_时延.md
摘要：方法栈（以 [[1407.6613]] 为基准实现）：  1. **束缚态**：Hartree–Fock 自洽场；**连续态**：HF frozen-core + 散射相位 δ(ℓ,k)（Coulomb 相移 η + 短程修正）； 2. **电子关联**：RPAE（含交换随机相位近似）——自洽积分方程求约化偶极矩阵元，保留 time-forward 极点相位 φ^RPAE； 3. **光电子波包**：分波展开 Ψ(k,t)=Σℓ cℓ R(ε,ℓ)Y(ℓ,m)，矩阵元 D_k 闭式表达； 4. **对照**：3D TDSE 数值传播（优化单粒子势 + 矩阵迭代法，球谐展开）； 5. **EWS/Wigner 时延**：**τ_W = ℏ ∂arg(D_k)/∂ε**，对 XUV 谱密度加权能量平均，再对发射角 θ_k 角分辨。  关键物理：分波干涉的角向零点（如 P₂(cos θ) 在 ±

### [[methods/bsv-driven-hhg-quantum_课题理论三角|bsv-driven-hhg-quantum 课题理论三角]]
页：knowledge/wiki/methods/bsv-driven-hhg-quantum_课题理论三角.md
摘要：三角三支（课题 03_method/kb-methods-pack 定义）：  1. **输入态表征**：[[2608.16027]] —— BSV 驱动场的量子态表征（光子统计/Wigner 函数）； 2. **输入态→电子动力学解析连接**：[[2604.09284]] —— 量子光场如何映射到强场电子响应； 3. **输出态**：[[2410.15503]] —— HHG 输出光场的量子态（谐波光子统计/纠缠）。  配套方法族（三部曲 + 闭环电离端）： - [[2604.06707]]：BSV-driven HHG **谐波端**； - [[2604.06703]]：BSV-only **电离端**； - [[2610.16077]]（Q-CCSFA）：电离端的相敏反演——「量子光场→强场过程→量子光场可读出」闭环的方法基座。  课题 A 延伸：气相 action phase 分解

## 二、带方法卡的论文页（6）

### [[papers/2026-2510_16546-high-harmonic-generation-light-source-with-polariz|偏振可编程 HHG 光源（多材料筛选：TMDC/拓扑绝缘体/外延双层石墨烯 + SHG/MIR 双驱动）]]
页：knowledge/wiki/papers/2026-2510_16546-high-harmonic-generation-light-source-with-polariz.md
参数样例：参数；---；材料；激光

### [[papers/2025-2511_18362-attosecond-resolved-quantum-fluctuations-of-light-and-matter|BSV 微扰双色 HHG：单发光子统计 + 原位四缝干涉量子态层析 + 隧穿涨落阿秒分辨]]
页：knowledge/wiki/papers/2025-2511_18362-attosecond-resolved-quantum-fluctuations-of-light-and-matter.md
参数样例：参数；---；驱动构型；对称性关系

### [[papers/2026-2603_27477-a-dual-sideband-attosecond-interferometry-setup|双边带阿秒干涉术装置（HHG Ar XUV + He 靶 + NOPA 1200 nm 探针 + 多技术模块）]]
页：knowledge/wiki/papers/2026-2603_27477-a-dual-sideband-attosecond-interferometry-setup.md
参数样例：参数；---；驱动；探针

### [[papers/2024-241119046-noncollinear-phase-matching-of-high-harmonic|固体 HHG 的非共线相位匹配（不对称光子上转换：强场 N+1 光子 + 弱场 1 光子横向动量补偿）]]
页：knowledge/wiki/papers/2024-241119046-noncollinear-phase-matching-of-high-harmonic.md

### [[papers/2026-2602_12396-symmetries-of-spin-splitting-induced-by-spin-orbit-coupling|点群表示论统一分类——非磁晶体中 SOC 诱导自旋劈裂的对称性地图（Rashba/Dresselhaus/Weyl/Ising 四类原型枚举，Yang, Fernandes, Birol）]]
页：knowledge/wiki/papers/2026-2602_12396-symmetries-of-spin-splitting-induced-by-spin-orbit-coupling.md
参数样例：参数；---；分类框架

### [[papers/2024-2408_02310-laser-induced-core-polarization-effects-in-high-order-harmon|TDDFT 系统计算激光诱导核极化对固体 HHG 的影响 + 双色泵浦-探测选择性激活内壳层通道（陆培祥组，PRA 110, 023104, 2024）]]
页：knowledge/wiki/papers/2024-2408_02310-laser-induced-core-polarization-effects-in-high-order-harmon.md
参数样例：参数；---；方法栈
