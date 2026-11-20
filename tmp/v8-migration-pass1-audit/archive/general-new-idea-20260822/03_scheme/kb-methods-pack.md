# 课题方法素材包（KB 自动聚合，v7.2.30 wikilink 节点格式）

- 课题：general-new-idea-20260822
- 生成时间：2026-10-30T15:57:58Z
- 方法关键词：DFT、HHG、MBE、体磁结构定量谱学、偏振通道分离测量、拟采用技术、波自旋与电荷泵浦、通道分离测量

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

### [[methods/bsv-driven-hhg-quantum_课题理论三角|bsv-driven-hhg-quantum 课题理论三角]]
页：knowledge/wiki/methods/bsv-driven-hhg-quantum_课题理论三角.md
摘要：三角三支（课题 03_method/kb-methods-pack 定义）：  1. **输入态表征**：[[2608.16027]] —— BSV 驱动场的量子态表征（光子统计/Wigner 函数）； 2. **输入态→电子动力学解析连接**：[[2604.09284]] —— 量子光场如何映射到强场电子响应； 3. **输出态**：[[2410.15503]] —— HHG 输出光场的量子态（谐波光子统计/纠缠）。  配套方法族（三部曲 + 闭环电离端）： - [[2604.06707]]：BSV-driven HHG **谐波端**； - [[2604.06703]]：BSV-only **电离端**； - [[2610.16077]]（Q-CCSFA）：电离端的相敏反演——「量子光场→强场过程→量子光场可读出」闭环的方法基座。  课题 A 延伸：气相 action phase 分解

### [[methods/dft-pbe|自旋极化DFT（PBE）电子结构计算]]
页：knowledge/wiki/methods/dft-pbe.md
摘要：基于PBE泛函的（自旋极化）DFT计算可直接给出二维材料电子结构基准：对磁性半导体CrPS3/CrPSe3单层提供PBE带隙标尺用于MPX3家族横向比较，对TMDC异质结（如MoSe2/WS2，II型对齐）提供基态几何、层间结合与初始带对齐基线。  ## 适用边界  PBE为半局域GGA泛函，系统性低估带隙且本身不含层间范德华色散（层间结合与带隙绝对值不可定量外推），所得数值宜作同泛函体系内部横向标尺；对Cr系磁性体系须开启自旋极化方得正确基态。  ## 代表作  - arXiv:2112.12712 - arXiv:2501.08138  ## 证据日志  - 2026-10-03｜r50｜仅简报｜[paper:2021-2112.12712-adsorption-of-water-on-the-pristine-and-defective-semiconduc] 自旋极化DFT（PBE

### [[methods/dft-u|DFT+U 第一性原理能带计算（含自旋轨道耦合）]]
页：knowledge/wiki/methods/dft-u.md
摘要：在DFT框架上对局域d电子引入Hubbard U校正（必要时纳入自旋轨道耦合）进行总能与能带计算，可直接判定磁性基态并给出自旋劈裂能带的第一性原理证据，如有机候选化合物中的补偿亚铁磁基态与巨型自旋劈裂，以及MnX家族中竞争反铁磁相（A型AFM→交替磁）的相边界。  ## 适用边界  结果对Hubbard U取值较敏感且依赖磁构型采样的完备性（相边界的确定依赖竞争相总能比较），自旋轨道耦合仅在涉及自旋劈裂判据时开启；成本高于标准GGA计算但低于杂化泛函。  ## 代表作  - paper:2024-2404.12345-compensated-ferrimagnets-with-colossal-spin-splitting-in-org - paper:2025-2512.23904-competing-antiferromagnetic-phases-in-multiferroic-wu

### [[methods/DFT计算|DFT计算]]
页：knowledge/wiki/methods/DFT计算.md
摘要：**DFT**：以电子密度为基本变量的基态理论（Kohn–Sham 方程组）。 **TDDFT**（DFT 的含时推广，Runge–Gross 定理 1984：含时外场与含时密度一一对应）：求解含时 Kohn–Sham（TDKS）方程演化多体系统，代价远低于含时多体薛定谔方程。  两种工作模式： 1. **线性响应 TDDFT**（Casida 方程）：激发能/振子强度，适合微扰区（吸收谱、光学性质）； 2. **实时 RT-TDDFT**：显式传播 TDKS 轨道，处理任意强场非微扰问题（飞秒激光）；与核运动耦合成 Ehrenfest 动力学。  **磁性扩展**：自旋极化/非共线 TDDFT 显式算激光退磁、自旋流。 **主要误差源**：交换关联势的绝热近似（ALDA/AGGA）——无法描述双激发、长时间电荷转移。**数值实现**：Magnus / Crank–Nicolson / 强

### [[methods/第一性原理DFT计算非共线磁性SOC|第一性原理DFT计算（非共线磁性+SOC）]]
页：knowledge/wiki/methods/第一性原理DFT计算非共线磁性SOC.md
摘要：基于密度泛函理论并显式开启非共线磁序与自旋-轨道耦合（SOC）进行结构弛豫与电子结构计算：对反平行堆叠磁性vdW多层可系统证明滑移/莫尔铁电与交变磁性共存的普适性并提取自旋劈裂与电极化数值估计，可通过能量与电子结构双重判据验证NiBr2/MnBr2交变磁-铁电多铁基态，也能给出pristine与缺陷/掺杂CrSb中自旋劈裂能带及磁性点群变化的基态图像；含强SOC的能带（如应变下非中心对称Bi2O2X的带边SOC劈裂）可作为量子几何与非线性光学（SHG等）响应计算的输入。  ## 参数表  | 参数 | 数值 | 出处 | | --- | --- | --- | | 平面波截断能 | 600 eV | paper:2025-2501.16741-quantum-geometric-origin-of-strain-tunable-giant-second-harm | | 布里渊区采样k点网

### [[methods/SALMON_rt-TDDFT___Williams-Lax|salmon-williams-lax]]
页：knowledge/wiki/methods/SALMON_rt-TDDFT___Williams-Lax.md
摘要：威廉斯–拉克斯（Williams–Lax）均匀半经典近似给出强场下带间跃迁/弗朗兹–凯尔迪什吸收的解析速率；新证据补充：开源实时TDDFT软件（SALMON系，Yabana组生态）提供可复现的固体强场光电耦合计算流程及气相–固相对比算例，可作为该半经典方法移植与第一性原理基准检验的现成平台。  ## 适用边界  Williams–Lax 依赖抛物带、偶极近似与准静态均匀场假设，在非抛物带、强散射或超短脉冲非偶极效应显著时失效；SALMON 实时TDDFT 需长时间实传播、成本随体系尺度与脉冲时长增长，且受交换关联泛函近似限制，适合作为对照基准而非大规模替代。  ## 代表作  - 2025-2505.09387-technical-review-time-dependent-density-functional-theory-fo  ## 证据日志  - 2026-10-24｜r92｜仅简

## 二、带方法卡的论文页（6）

### [[papers/2026-2601_12098-real-symmetric-hamiltonian-enables-near-linear-scaling-for-f|实对称哈密顿量实现近线性标度费米面提取（实对称嵌入 + shift-invert Arnoldi + LDL/Sylvester 惯性 + KD-tree）]]
页：knowledge/wiki/papers/2026-2601_12098-real-symmetric-hamiltonian-enables-near-linear-scaling-for-f.md
参数样例：参数；---；TB 参数

### [[papers/2023-2311_01371-metrological-robustness-of-high-photon-number-optical-cat-st|HHG 猫态的损耗通道 QFI 分析（零差相位估计协议）]]
页：knowledge/wiki/papers/2023-2311_01371-metrological-robustness-of-high-photon-number-optical-cat-st.md

### [[papers/2026-2607_28491-drumhead-surface-states-of-rhombohedral-graphite-with-near-i|菱方石墨鼓面态近理想量子几何的第一性原理核验（DFT+Wannier+Wilson loop+Kubo QGT 空间分辨）]]
页：knowledge/wiki/papers/2026-2607_28491-drumhead-surface-states-of-rhombohedral-graphite-with-near-i.md
参数样例：参数；---；计算设置；DSS 曲率定量

### [[papers/2026-2601_02481-an-altermagnetic-materials-library-in-intercalated-transitio|插层过渡金属双硫属化物交变磁材料库的系统 DFT 筛选（T_yMX₂：VASP PBE+U+D3+对称性判据）]]
页：knowledge/wiki/papers/2026-2601_02481-an-altermagnetic-materials-library-in-intercalated-transitio.md
参数样例：参数；---；DFT 设置；筛选空间

### [[papers/2026-2610_19967-high-harmonic-generation-probes-quantum-nuclear-fl|PIMD + RT-TDDFT 第一原理液体 HHG（核量子涨落探针，液态水）]]
页：knowledge/wiki/papers/2026-2610_19967-high-harmonic-generation-probes-quantum-nuclear-fl.md
参数样例：参数；---；量子核采样产额抑制

### [[papers/2026-2505_13415-optical-signatures-of-bulk-g-wave-altermagnetism-in-mnte|MnTe 体 g 波交变磁性光学签名（ELK LAPW+U + 布居速率方程 + S_exc(α) 分解为 d/g 波样）]]
页：knowledge/wiki/papers/2026-2505_13415-optical-signatures-of-bulk-g-wave-altermagnetism-in-mnte.md
参数样例：参数；---；DFT 设置；脉冲参数
