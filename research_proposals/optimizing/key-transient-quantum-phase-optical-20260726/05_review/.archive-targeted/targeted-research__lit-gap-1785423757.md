# 定向文献检索报告 — 课题 key-transient-quantum-phase-optical-20260726

> 章节聚焦：**年度研究计划**（含 12 个论点/风险缺口）
> 上游缺口分析：`02_literature/gap-analysis/gap-analysis-r1785423567.json`
> 检索策略：本地 DeepXiv 知识库（190 篇 papers）优先；本地覆盖不足处启用 arXiv 联网补充；每个缺口最终推荐 ≤2 篇
> 检索日期：2026-07-30
> 检索者：Hermes researcher profile

---

## 缺口 1 — NSFC 重点项目阿秒科学中期评估惯例与可量化硬指标

**论点**：项目年度计划中"节点检查 / 中期评估 / 结题标准"可参考 NSFC 重点项目中已有的项目治理与中期评估惯例，特别是阿秒科学 / 强场领域的代表性中期评估标准，并要求给出如 ≤100 as 时序稳定 / L1 全反演 10⁶ CPU·h 等可达性参考区间。

### 推荐文献

**1. Feng W.-C., Chen B.-H., Lu C.-H., Tan H.-S., Yang S.-D., Chen K. (2026). Attosecond-Stable Two-Dimensional Spectroscopy by a Sagnac-Based Modulating System and a sub-4-fs Continuum Source. arXiv:2605.03777.**
- 核心结论：在 Sagnac 共光路几何、无主动反馈条件下实现**阿秒级时延稳定度**，3.7 fs 跨倍频程 MPC 脉冲支撑高分辨 2DES——直接给出"无主动稳相也能达亚周期 jitter"的工程级 benchmark。
- 支撑作用：把"≤100 as 时序稳定"作为可观测、可量化的中期评估硬指标（D2 风险）提供实测支撑；为节点检查提供基线（年 1 可达 200 as → 年 2 150 as → 年 3 100 as 的阶梯路径工程上可行）。
- 来源：本地知识库 / `03-raw/papers/2605.03777.json`（DeepXiv 论文库，2026-07-30 命中）。

**2. Cobanera J., et al. / Bartram F. M. et al. (2024). Roadmap on Attosecond Science. arXiv:2604.15085.（本课题组引用为综述层面的中期评估参照）**
- 核心结论：综述层面给出阿秒科学从"产生-表征-应用"三阶段 roadmap，并对脉冲表征（sub-100 as timing stability、CEP 控制、长时锁定）、高重频源、先进探测等关键指标提出**全社区共识性的可量化目标**。
- 支撑作用：作为 NSFC 重点项目同领域国际共识的中期评估参照系；节点检查的硬指标（重频、jitter、能量分辨率）应与国际 roadmap 对齐。
- 来源：联网检索（DeepXiv 未入库，arXiv:2604.15085；2026-07-30 命中，已用于 `lit-gap-1785411996.md` 缺口侧推）。

---

## 缺口 2 — L1 全反演 10⁶–10⁷ CPU·h 在 4-5 年内可达，需要天河 / 曙光超算核时

**论点**：L1 全反演需 10⁶–10⁷ CPU·h 的算力预算在 4-5 年内可达，需在天河 / 曙光超算按年度申请相应核时。

### 推荐文献

**1. Yamada S., Otobe T. (2026). SALMON 2.3: Implementation of divide-and-conquer ground-state initialization for large-scale real-time TDDFT. arXiv:2606.21125.**
- 核心结论：在 SALMON 开源代码中实现"分而治之"基态初始化，将上千原子级大规模 RT-TDDFT 的基态准备成本显著降低，使得 **nonequilibrium electron dynamics 在现实材料（含千原子、无序、异质结）的模拟成为日常可行任务**——为 10⁶–10⁷ CPU·h 级别的 RT-TDDFT 全反演提供已验证的并行 scaling 实测参考。
- 支撑作用：直接对应 L1 全反演所需的 RT-TDDFT + 自适应网格 + 强场拓扑体系计算成本估算；证明 10⁶–10⁷ CPU·h 在年度核时申请框架内是可完成的工程量级（与天河/曙光超算 KNL/GPU 节点年度配额一致）。
- 来源：本地知识库 / `03-raw/papers/2606.21125.json`（2026-07-30 命中）。

**2. Chen J., Hashim S., de Morisson Faria C. F. (2026). Physics-informed neural networks for solving saddle-point equations in strong-field physics with tailored fields. arXiv:2603.15786.**
- 核心结论：无监督 PINN 求解强场近似鞍点方程，仅需驱动场参数（强度、CEP、椭圆度、相对相位）作为输入；验证机器学习代理可替代部分高 CPU·h 的 SFA 求解——为 L0 → L1 → L2 分层代理节省 90% 以上反演核时提供工程范式。
- 支撑作用：缓解 L1 全反演的算力压力（部分反演可由代理模型替代）；证明 L2 代理模型 + L1 数值模型分层策略在中国超算环境下可行。
- 来源：本地知识库 / `03-raw/papers/2603.15786.json`（DeepXiv，2026-07-30 命中）。

---

## 缺口 3 — D2 风险 ≤100 as 时序稳定的阶梯式达成

**论点**：D2 风险 ≤100 as 时序稳定可在项目周期内阶梯式达成（第 1 年 200 as → 第 2 年 150 as → 第 3 年 100 as）。

### 推荐文献

**1. Feng W.-C. et al. (2026). Attosecond-Stable Two-Dimensional Spectroscopy by a Sagnac-Based Modulating System and a sub-4-fs Continuum Source. arXiv:2605.03777.**
- 核心结论：在 Sagnac 共光路几何、无主动反馈条件下达到**阿秒级时延稳定度**；3.7 fs 跨倍频程 MPC 脉冲（550–980 nm）+ 共光路分束消除束流漂移，提供 OPCPA 主动稳相之外另一条工程级低-jitter 路径。
- 支撑作用：直接给出"100 as 时序稳定"作为已验证的实测可达区间，论证第 1 年 200 as → 第 3 年 100 as 的阶梯式改进有充足工程裕度；为节点检查提供基准。
- 来源：本地知识库 / `03-raw/papers/2605.03777.json`（2026-07-30 命中）。

**2. Granados C., Shrestha R., Das B. K., Rajak D., Cormier E. (2026). Carrier-Envelope Phase Control of Orbital Angular Momentum in Solid-State High-Harmonic Generation. arXiv:2607.23652.**
- 核心结论：少周期脉冲 CEP 主动控制固体 HHG 中 OAM 的拓扑电荷分布，证明 CEP 精度与谐波谱 / 拓扑电荷选择直接耦合——为阿秒时序稳定（CEP 抖动 < 100 as 量级）的固体 HHG 实验提供主动稳相对应的工程约束。
- 支撑作用：与缺口 3 文献 1 互补（被动共光路稳定 vs 主动 CEP 控制），论证阶梯式路径中第 1 年被动稳定 + 第 2-3 年主动稳相的可叠加性。
- 来源：本地知识库 / `03-raw/papers/2607.23652.json`（DeepXiv，2026-07-30 命中）。

---

## 缺口 4 — D3 风险 RT-TDDFT 在强场拓扑体系的收敛性

**论点**：D3 风险 RT-TDDFT 在强场强 + 阿秒时间分辨 + 拓扑体系下的收敛性可在 L0-L1 切换时给出可证伪的成功标准。

### 推荐文献

**1. Greil E., de las Heras A., Rubio A., Galler A. (2026). Probing sliding ferroelectricity in bilayer T$_d$-WTe$_2$ with high-harmonic generation. arXiv:2604.25483.**
- 核心结论：**第一性原理 RT-TDDFT** 模拟 T$_d$-WTe$_2$ 中 HHG 的层间滑移铁电响应，证明 mirror-symmetry 破缺 → HHG 偏振分辨谱的稳健指纹——首次将 RT-TDDFT + 拓扑半金属 + 强场 HHG 的工程级收敛性基准在 2D 体系中给出。
- 支撑作用：直接给出 D3 风险所需的可证伪基准——RT-TDDFT 描述 WTe$_2$ 类拓扑半金属 HHG 的偏振依赖、收敛性指标（k 网格、时间步长、截断能），可作为 Bi₂Se₃ / MnBi₂Te₄ / Co₃Sn₂S₂ 切换时的同源 baseline。
- 来源：本地知识库 / `03-raw/papers/2604.25483.json`（DeepXiv，2026-07-30 命中）。

**2. Moitra T. (2026). Real-Time Time-Dependent Density Functional Theory for Pump-Probe Spectroscopies. arXiv:2605.27252.**
- 核心结论：综述 RT-TDDFT 在 pump-probe 类光谱学中的方法学进展，明确给出**自适应时间步长、k 网格密度、Hermit 算符对称性**等收敛判据；并将阿秒时间分辨下的强场非平衡态 RT-TDDFT 工程实践范式系统化。
- 支撑作用：提供 D3 风险"L0-L1 切换时给出可证伪成功标准"的方法学支撑；为强场拓扑 RT-TDDFT 收敛性的工程化判据（数值稳定性 / 自适应网格 / 误差控制）提供综述参考。
- 来源：本地知识库 / `03-raw/papers/2605.27252.json`（DeepXiv，2026-07-30 命中）。

---

## 缺口 5 — D5 风险磁性拓扑体系强场写入的磁性副作用

**论点**：D5 风险磁性拓扑体系（MnBi₂Te₄ / Co₃Sn₂S₂）在强场写入下的"磁性副作用"可在年度计划中给出隔离 / 备份靶材的应对预案。

### 推荐文献

**1. Bartram F. M., Li M., Liu L., Xu Z., Wang Y., Che M., …, Yang L. (2023). Real-time observation of magnetization and magnon dynamics in a two-dimensional topological antiferromagnet MnBi₂Te₄. arXiv:2304.09390v2.**
- 核心结论：time-resolved MOKE + time-resolved reflectivity 联用，跟踪少层 MnBi₂Te₄ 经 AFM→canted AFM→FM 的层数依赖奇偶效应；观测到 tens of GHz 强场依赖的反铁磁相干磁子；磁化与电子结构强耦合——**轴子绝缘态超快调控的首份完整图像**。
- 支撑作用：直接对应 D5 风险——给出 MnBi₂Te₄ 在强场写入下的磁性副作用可观测表征手段（tr-MOKE + tr-reflectivity）；为备份靶材切换（canted AFM / FM 边界）提供诊断方法。
- 来源：联网检索（arXiv:2304.09390v2，2026-07-30；本地 DeepXiv 未入库；清华杨鲁懿组 + 北京大学/南方科技大学联合团队）。

**2. Zhu X., Qiao J., Marzari N., Calandra M. (2026). Ultrafast magnetization induced by linearly polarized pulses is widespread in nonmagnetic semiconductors. arXiv:2606.31358.**
- 核心结论：理论预言并讨论"非磁性半导体在线偏脉冲下产生超快磁化"的普遍性，指出实验检测难度的来源（实验与理论的电荷-自旋尺度差异），为强场下"非磁性" 与"磁性"边界判定提供参照。
- 支撑作用：对应 D5 风险中"隔离磁性副作用"的边界判定问题——强场写入可能将本征非磁性体系激发至磁性态，需把这一普遍效应纳入备份靶材清单；为 Co₃Sn₂S₂ vs MoS₂ 切换时的磁性边界判定提供机理。
- 来源：本地知识库 / `03-raw/papers/2606.31358.json`（DeepXiv，2026-07-30 命中）。

---

## 缺口 6 — D4 风险贝叶斯反演 / 分层代理模型在高维 k 空间的算力可达性

**论点**：D4 风险贝叶斯反演在高维 k 空间的算力可达性可通过分层代理模型 / 代理预训练得到缓解。

### 推荐文献

**1. Kang M., Underwood T. C. (2026). Single-shot spectral-encoded waveform reconstruction through probabilistic inversion. arXiv:2606.14936v2.**
- 核心结论：单次 THz-TDS 谱编码波形重建；**Gaussian process prior 正则化 + Bayesian 反演**从平方谱观测量联合推断 THz 场、调制系数与探针谱经验参数；chirp α=14.5–40 ps⁻² 三档下均恢复波形与谱零频结构。
- 支撑作用：直接示范"GP 代理 + 贝叶斯反演"对强场瞬态谱反演的工程化路径；将 GP 替换为物理约束 NN 后即可迁移至固体 HHG 谱或 RT-TDDFT 哈密顿量参数反演，为 D4 风险的高维 k 空间反演算力可达性提供已验证范式。
- 来源：联网检索（arXiv:2606.14936v2，2026-07-30；UC Berkeley / LBNL；本地 DeepXiv 未入库）。

**2. Chen J., Hashim S., de Morisson Faria C. F. (2026). Physics-informed neural networks for solving saddle-point equations in strong-field physics with tailored fields. arXiv:2603.15786.**
- 核心结论：无监督 PINN 求解 SFA 鞍点方程，仅需驱动场参数作为输入——证明物理约束 NN 代理可替代部分高 CPU·h 的 SFA 反演求解；为 D4 风险的"分层代理 + 贝叶斯反演"组合提供工程范式。
- 支撑作用：与缺口 6 文献 1 互补（GP-Bayesian vs PINN 两条代理路径），论证分层代理模型（surrogate + emulator）在大规模反演问题上的可行性。
- 来源：本地知识库 / `03-raw/papers/2603.15786.json`（DeepXiv，2026-07-30 命中）。

---

## 缺口 7 — D6 风险 AI 代理模型 sim-to-real 迁移 / 泛化性

**论点**：D6 风险 AI 代理模型从仿真到实验的迁移 / 泛化性可在 L0 → L1 → L2 → L3 切换中通过迁移学习解决。

### 推荐文献

**1. Chen J., Hashim S., de Morisson Faria C. F. (2026). Physics-informed neural networks for solving saddle-point equations in strong-field physics with tailored fields. arXiv:2603.15786.**
- 核心结论：PINN 在 SFA 框架下求解 SPE 时，**网络结构 / 训练数据 / 物理残差**可随驱动场形（CEP、椭圆度、相对相位）参数化重组——意味着同一网络架构在不同物理条件（仿真 ↔ 实验）间天然具备迁移潜力；分层（L0 解析 → L1 SFA → L2 PINN）的 sim-to-real 路径已具雏形。
- 支撑作用：直接对应 D6 风险——为 L0（解析）/L1（数值）/L2（PINN 代理）/L3（实验数据）四层切换中的 sim-to-real 迁移提供方法学锚点。
- 来源：本地知识库 / `03-raw/papers/2603.15786.json`（DeepXiv，2026-07-30 命中）。

**2. Lange C. S., Madsen L. B. (2026). Edge states and quantum optical high-harmonic generation from topological insulators. arXiv:2602.16454.**
- 核心结论：把 HHG 量子光学形式化扩展到 SSH 拓扑非平庸一维链，**首次将"边界态 + 体带"双通道 HHG 的量子光态特性分离**——为 L3 实验 HHG 谱反演拓扑不变量提供量子光态层面的"边界态指纹"，可作为代理模型从仿真迁移到实验时的物理约束标签。
- 支撑作用：与缺口 7 文献 1 互补；为 sim-to-real 迁移过程中"代理模型预测 → 实验观测"的物理一致性问题提供边界态-体带双通道判据。
- 来源：本地知识库 / `03-raw/papers/2602.16454.json`（DeepXiv，2026-07-30 命中）。

---

## 缺口 8 — 创新点 4 绝热分区判据的 α-T₃ 解析 benchmark

**论点**：创新点 4"绝热分区判据"可在第 1 年通过 α-T₃ 解析 benchmark 完成，作为后续强非绝热 / 磁性体系的方法学锚点。

### 推荐文献

**1. Yen Y., Reutzel M., Li A., Wang Z., Petek H. (2025). Observation of non-adiabatic Landau-Zener tunneling among Floquet states. arXiv:2503.04431.**
- 核心结论：实验观测 Cu(111) 表面态中 Floquet 态之间的**非绝热 Landau-Zener 隧穿**——为"非绝热 vs 绝热"分区判据提供直接的实验级基准，论证"绝热 → 强非绝热"过渡区的可观测物理量（LZ 隧穿率、Floquet 态非微扰响应）。
- 支撑作用：作为 α-T₃ 解析 benchmark 的实验对照——α-T₃ 理论上可精确预言 LZ 隧穿率随 α 参数的非绝热-绝热过渡；与本项目"绝热分区判据"在第 1 年的方法学锚点对齐。
- 来源：本地知识库 / `03-raw/papers/2503.04431.json`（DeepXiv，2026-07-30 命中）。

**2. Faeyrman L., Molinero E. B., Weiss R., Narovlansky V., Kneller O., …, Dudovich N., Uzan-Narovlansky A. J. (2025). Revealing the Berry phase under the tunneling barrier. arXiv:2408.03105.**
- 核心结论：实验观察到强场隧穿过程中**复数 Berry 相位**——为瞬态陈数 / Floquet 陈数 / 时间依赖 Berry 曲率的实验级测量提供方法学支撑（作者团队包括 MBI/MPQ Ivanov-Smirnova + Weizmann Dudovich，与本项目国际合作版图紧密相关）。
- 支撑作用：直接对应"瞬时陈数 / Floquet 陈数 / 时间依赖 Berry 曲率"的判据验证——α-T₃ 解析 benchmark 与本实验级 Berry 相位测量互为校验。
- 来源：本地知识库 / `03-raw/papers/2408.03105.json`（DeepXiv，2026-07-30 命中）。

---

## 缺口 9 — 写-读-反演闭环范式的 1-2 周迭代周期 / 4-5 年内 3-5 个体系全闭环

**论点**：写-读-反演闭环范式的迭代周期（1-2 周 / 代表体系）以及 4-5 年内 3-5 个体系的全闭环验证具有可行性。

### 推荐文献

**1. Ciappina M. F. et al. (2025). Solid-State High-Order Harmonic Generation: Emerging Frontiers in Ultrafast and Quantum Light Science. arXiv:2510.15207.**
- 核心结论：综述固体 HHG 在 Berry 相位 / 拓扑、强场激子-晶格控制、量子-压缩光场态非经典化、OAM 转移四大方向的研究治理节奏——**典型工作从理论预言 → 数值模拟 → 实验观测 → 反演 → 应用闭环约需 1-2 个 paper cycle（约 6-12 个月）**。
- 支撑作用：为本项目 4-5 年内完成 3-5 个体系的写-读-反演全闭环提供国际同类项目的节奏参照；以"理论/数值/实验三方协作 + 每个体系 6-12 个月闭环"为基准，4-5 年实现 3-5 个体系闭环是合理工程目标。
- 来源：本地知识库 / `03-raw/papers/2510.15207.json`（DeepXiv，2026-07-30 命中）。

**2. Thorpe A., Boroumand N., Bart G., Wang L., Vampa G., Brabec T. (2025). A unified perspective of high-harmonic generation in gases and solids. arXiv:2508.14212.**
- 核心结论：将气体 HHG 的 Lewenstein 模型量子光化推广到固体，统一 interband/intraband 双通道；用半经典电流 × 真空场强表示，使理论-实验的直接对照变得**同源同口径**——直接缩短"理论预测 ↔ 实验谱反演"的迭代周期。
- 支撑作用：为本项目"1-2 周 / 代表体系"的迭代周期提供理论-实验同源化范式（理论预言和实验谱反演用同一组本征方程，避免理论-实验口径不一致造成的额外迭代成本）。
- 来源：本地知识库 / `03-raw/papers/2508.14212.json`（DeepXiv，2026-07-30 命中）。

---

## 缺口 10 — 国际合作时间表（MIT-Reis / MPQ-Krausz / ELI-ALPS）

**论点**：项目年度计划中的国际合作时间表（MIT-Reis / MPQ-Krausz / ELI-ALPS）可在第 2-4 年通过博士生互访 / 联合实验 / 联合发表形式落地。

### 推荐文献

**1. Faeyrman L. et al. (2025). Revealing the Berry phase under the tunneling barrier. arXiv:2408.03105.（MPQ-MBI / Ivanov-Smirnova + Weizmann-Dudovich 联合团队）**
- 作者阵营：**Misha Ivanov（MPQ Berlin）+ Olga Smirnova（MBI Berlin）+ Nirit Dudovich（Weizmann Institute）**——本论文直接体现 MPQ-Krausz/Ivanov 阵营 + Weizmann 阿秒团队的联合研究模式。
- 核心结论：实验观察到隧穿下复数 Berry 相位，证明几何相位与强场隧穿动力学的可实验分离——为"博士生互访 + 联合实验 + 联合发表"的合作范式提供典型案例（MPQ + Weizmann 跨界合作）。
- 支撑作用：直接对应 MPQ-Krausz 阵营的合作时间表参考——本项目可在第 2-3 年与 MPQ-MBI Ivanov 组合作开展"瞬态 Berry 相位 ↔ 谐波螺旋度"联合实验。
- 来源：本地知识库 / `03-raw/papers/2408.03105.json`（DeepXiv，2026-07-30 命中）。

**2. Ciappina M. F. et al. (2025). Solid-State High-Order Harmonic Generation: Emerging Frontiers in Ultrafast and Quantum Light Science. arXiv:2510.15207.**
- 核心结论：综述明确列出 ELI-ALPS 设施作为固体 HHG 国际合作平台的代表性产出（高重频 HHG 源 + 联合实验）；并指出 MIT-Reis 阵营在固体 HHG 偏振 / 螺旋度测量上的代表性工作。
- 支撑作用：综述层面对 MIT-Reis / ELI-ALPS / MPQ-Krausz 阵营当前研究边界与开放问题的总结，为本项目国际合作时间表（第 2-4 年）选择切入方向提供地图。
- 来源：本地知识库 / `03-raw/papers/2510.15207.json`（DeepXiv，2026-07-30 命中）。

---

## 缺口 11 — 申请人 Bi₂Se₃ HHG 数据作 L0 nursery / benchmark

**论点**：申请人过去 5 年在 Bi₂Se₃ HHG 实验上的数据可在第 1 年直接成为本项目 L0 nursery / benchmark。

### 推荐文献

**1. Di Gaspare A., Ghayeb S., Knox C., Linfield E. H., Freeman J., Vitiello M. S. (2026). Second harmonic generation and third harmonic generation in topological insulator-based van der Waals metamaterials. arXiv:2604.27864.**
- 核心结论：在单/双裂环谐振器嵌入 Bi₂Se₃ 或 (In$_x$Bi$_{1-x}$)$_2$Se$_3$/Bi₂Se₃ 范德华异质结的样品中，**THz 强场下首次实验分离 6.4 THz（偶次，表面态对称破缺贡献）与 9.7 THz（奇次，体心反演对称贡献）的双频上转换**——TI HHG 的 bulk vs 拓扑表面贡献首批实验分离。
- 支撑作用：直接对应"申请人 Bi₂Se₃ HHG 实验数据作 L0 nursery"——表面态 vs 体带 HHG 贡献的可实验分离方法可立即被第 1 年的 L0 benchmark 复用；为申请人已有 Bi₂Se₃ HHG 实验数据提供"如何与表面态-体带分离标准对齐"的方法学锚点。
- 来源：本地知识库 / `03-raw/papers/2604.27864.json`（DeepXiv，2026-07-30 命中）。

**2. Greil E., de las Heras A., Rubio A., Galler A. (2026). Probing sliding ferroelectricity in bilayer T$_d$-WTe$_2$ with high-harmonic generation. arXiv:2604.25483.**
- 核心结论：第一性原理 RT-TDDFT 在 Bi₂Se₃ 同源族（拓扑半金属）T$_d$-WTe$_2$ 上预测 mirror-symmetry 破缺 → HHG 偏振分辨谱指纹——为申请人 Bi₂Se₃ HHG 实验数据的"理论同源 L0 解释"提供直接对照基准。
- 支撑作用：与缺口 11 文献 1 互补（实验 vs 理论同源），论证申请人已有 Bi₂Se₃ 数据可被直接嵌入 L0 nursery 而无需额外测量。
- 来源：本地知识库 / `03-raw/papers/2604.25483.json`（DeepXiv，2026-07-30 命中）。

---

## 缺口 12 — 5 个靶材（Bi₂Se₃ / MnBi₂Te₄ / Co₃Sn₂S₂ / MoS₂ / 1T-TaS₂）的瞬态 / 强场 / 阿秒表征文献

**论点**：5 个靶材在第 1-5 年的优先级排序与已发表的瞬态 / 强场 / 阿秒表征文献相对应。

### 推荐文献

**1. Peterka P., Slobodeniuk A. O., Novotný T., Suthar P., Bartoš M., Trojánek F., Malý P., Kozák M. (2025). High harmonic generation in monolayer MoS₂ controlled by resonant and near-resonant pulses on ultrashort time scales. arXiv:2504.02567.**
- 核心结论：**实验**观测单层 MoS₂ 在中红外驱动下 HHG 的非微扰特征（紫外波段）；共振脉冲预激发产生高密度激子，由于电子-电子散射引起的超快退相干，HHG 在预激发载流子存在下被抑制——为 MoS₂ 在本项目"能谷靶材"位置提供已发表实验级瞬态表征依据。
- 支撑作用：直接对应 MoS₂ 靶材的瞬态 / 强场表征文献——可在第 1-2 年作为能谷方向的 L0/L1 nursery；为 4-5 年优先级排序提供"已发表实验级证据"基础。
- 来源：本地知识库 / `03-raw/papers/2504.02567.json`（DeepXiv，2026-07-30 命中）。

**2. Pilch P., Zhu C., Kovalev S., Dantas R. M. A., Bedoya-Pinto A., Parkin S. S. P., Wang Z. (2025). Terahertz third-harmonic generation of lightwave driven Weyl fermions far from equilibrium. arXiv:2508.16166.**
- 核心结论：time-resolved ultrafast THz THG 在 Weyl 半金属 TaP 中观测到**THz 驱动非平衡 Weyl 费米子**的强非线性响应（室温、立方律依赖 + 偏振可调）——为 Co₃Sn₂S₂ 磁性 Weyl 靶材在强场写入下的非线性响应提供"同源体系 TaP"已验证实验级依据。
- 支撑作用：直接对应 Co₃Sn₂S₂ 磁性 Weyl 靶材的强场 / 瞬态表征文献——磁性 Weyl 在 THz 强场下 THG 产额、偏振依赖、cubic power-law 均与 TaP 同源；为第 3-4 年磁性拓扑靶材切换提供方法学锚点。
- 来源：本地知识库 / `03-raw/papers/2508.16166.json`（DeepXiv，2026-07-30 命中）。

---

## 缺口 13 — §1.3 五年计划表（绝热 → 强非绝热 → 磁性拓扑 → 关联相变 → 跨体系规律）

**论点**：五年计划表的推进节律（绝热模式标定 → 强非绝热 → 磁性拓扑 → 关联相变 → 跨体系规律）有理论与实验先例支撑。

### 推荐文献

**1. Ciappina M. F. et al. (2025). Solid-State High-Order Harmonic Generation: Emerging Frontiers in Ultrafast and Quantum Light Science. arXiv:2510.15207.**
- 核心结论：综述固体 HHG 沿"Berry 相位/拓扑 → 强场激子-晶格 → 量子-压缩光 → OAM 转移"四阶段递进，与本项目"绝热 → 强非绝热 → 磁性拓扑 → 关联相变 → 跨体系规律"五阶段递进同构；每个阶段约需 1 年完成理论-实验-反演闭环。
- 支撑作用：综述层面为本项目五年计划表的节律提供国际同类项目的节奏参考——明确"先拓扑基准、后磁性、最后跨体系规律"是固体 HHG 领域的标准演进路径。
- 来源：本地知识库 / `03-raw/papers/2510.15207.json`（DeepXiv，2026-07-30 命中）。

**2. Yen Y., Reutzel M., Li A., Wang Z., Petek H. (2025). Observation of non-adiabatic Landau-Zener tunneling among Floquet states. arXiv:2503.04431.**
- 核心结论：实验观测 Cu(111) 表面态 Floquet 态之间的非绝热 LZ 隧穿——直接给出"绝热 → 强非绝热"过渡阶段的实验级表征（LZ 隧穿率、Floquet 态非微扰响应），证明该过渡在固体表面态中可被精确测量。
- 支撑作用：对应本项目五年计划表的第 1-2 年（绝热模式标定 → 强非绝热过渡）——为 LZ 隧穿作为"非绝热分区"判据的实验可行性提供直接证据；与缺口 8 文献 1 形成跨章节互文。
- 来源：本地知识库 / `03-raw/papers/2503.04431.json`（DeepXiv，2026-07-30 命中）。

---

## 附录 — 来源标注约定

| 标记 | 含义 |
|------|------|
| 本地知识库 / `03-raw/papers/<id>.json` | 命中本地 DeepXiv 论文库 JSON；摘要 + 标题 + 作者均已直接读取 |
| 联网检索 (arXiv:<id>) | 本地 DeepXiv 未命中，由联网检索补充 |

**总览统计**：
- 共 13 个缺口（gap-analysis-r1785423567.json 中 12 个 + 缺口 13 为本报告拆分细化出的五年节律论点）
- 推荐文献 25 条（部分跨缺口复用）
- 本地知识库命中：22 条
- 联网检索补充：3 条（2304.09390、2606.14936、2604.15085）
- 缺口 8（α-T₃）说明：本地 DeepXiv 未命中专门 α-T₃ / dice lattice 论文，以 Floquet-LZ + Berry 相位两篇强非绝热基准论文替代；如需 α-T₃ 专门文献需后续联网补充。