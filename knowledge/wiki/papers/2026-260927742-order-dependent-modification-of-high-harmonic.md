---
title: "Order-Dependent Modification of HHG by Quantum Dissipation and Lamb Shift —— Lindblad 主方程下环境对谐波阶数分辨的重构"
type: "papers"
created: "2026-10-04T10:52:53Z"
updated: "2026-11-15T15:09:19Z"
tags: ["固体HHG", "开放量子系统", "Lindblad主方程", "Lamb移位", "量子耗散", "阶数依赖效应", "阿秒光谱学", "Lindblad方程", "Lamb位移", "attosecond光谱", "环境耦合", "deepxiv-论文库", "深度解析"]
related: ["Berry 曲率", "Order-Dependent Modification of HHG by Quantum Dissipation and Lamb Shift", "Order-Dependent Modification of High-Harmonic Generation by Quantum Dissipation and Lamb Shift", "TDDFT", "pump-probe", "固体HHG", "固体高次谐波", "多体环境耦合", "强场超快", "强场超快光学", "相干控制", "量子耗散与退相干", "量子输运", "高次谐波产生"]
source_raw: "2026-2609.27742-order-dependent-modification-of-high-harmonic-gene.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
updated_at: "2026-10-30T09:35:17Z"
merged_from: ["wiki/papers/2026-2609_27742-order-dependent-modification-of-high-harmonic-gene.md", "wiki/papers/2609.27742.md"]
---

# Order-Dependent Modification of HHG by Quantum Dissipation and Lamb Shift

## 林赛的理解

这篇 Zhang 等人的工作让我眼前一亮——它直接挑战了固体 HHG 领域里一个根深蒂固的"常识"：环境耦合（声子、载流子-载流子散射、晶格涨落）总是扮演抑制谐波的角色，至多带来均匀展宽。他们用一个看似简单的二能级+Lindblad 开放量子系统模型，证明了**当耦合谱密度（structural/decohesive）的截止频率超过能级间距时，环境反而能增强谐波产率，且这种增强带有鲜明的阶数选择性**。

对我所在的强场超快光学组来说，这正好切入我们长期关注但一直没有微观理论框架支撑的问题：固体 HHG 谱中**为什么低阶与高阶谐波的相对效率在不同材料中差异如此之大**？传统上我们用带内/带间贡献、recolliding trajectory、Berry curvature 这些"相干"图像解释，而环境一直被视为背景噪声。这篇论文把环境从"背景"提升为"主动调控自由度"，并且给出了一个可检验的微观判据（谱密度截止 vs 能级间距）。

更让我兴奋的是结论末尾那句"solid-state attosecond spectroscopy"——它把 HHG 谱重新定位为固体耗散的探针，而不是只作为阿秒光源的副产品。这与我们组尝试用谐波谱反演能带结构、电子关联的工作方向有直接接口。

## 核心要点

### 1. 反直觉的环境增强
- 耦合谱密度的截止频率 $\omega_c$ 超过系统能级间距 $\Delta E$ 时，环境**增强**而非压制谐波产率。
- 这是对"环境=损耗"图像的直接反驳。

### 2. 增强的微观机制
- 增强**不是**来自布居弛豫或退相干的"增益通道"。
- 而是源于 Lamb 移位（virtual photon exchange with bath）所诱导的**能级涨落（level fluctuations）**——本质上是环境对系统哈密顿量的动力学重整。

### 3. 阶数依赖的环境响应
- **低阶谐波**与**高阶谐波**呈现明显不同的环境响应。
- 这意味着弛豫时间（relaxation-time）的唯像图像在阶数分辨尺度上失效。
- 建立了"阶数选择性的环境重构"这一新机制。

### 4. 理论-实验桥接意义
- 谐波谱中的阶数依赖衰减轮廓不再只是"噪声"，而是蕴含**谱密度形状、Lamb 移位强度**等微观环境信息的载体。
- 为固体耗散谱学（dissipation spectroscopy via HHG）打开窗口。

## 方法亮点

| 要素 | 做法 | 评价 |
|------|------|------|
| 系统模型 | 二能级系统（TLS） | 简化但抓住了"level spacing"这一核心标尺 |
| 浴模型 | 偶极-偶极相互作用热库（supper-Ohmic-like spectral density） | 比纯洛伦兹浴更具物理动机 |
| 动力学 | Lindblad 主方程（非幺正演化） | 标准但严谨；正确处理了耗散与相干 |
| 关键参量 | 谱密度截止频率 $\omega_c$ vs 能级间距 $\Delta E$ | 引入了清晰的物理判据 $\omega_c > \Delta E$ |
| 分析层面 | 阶数分辨的产率与谱形 | 直接对应实验可观测量 |

方法上的一个亮点是把 Lindblad 框架中常被忽略的**Lamb 移位项**（幺正修正部分）单独拉出来，与耗散（dissipator）解耦分析——这在多数 HHG 模拟中是直接被丢掉或重整到能级里去的。

## 与林赛工作的关联

1. **固体 HHG 的相干 vs 耗散图像**：我们组目前用 TDDFT + 少周期脉冲串级模拟 MgO、Si 等宽带隙绝缘体的谐波，一直把电子-声子耦合当作"耗散通道"加 phenomenologically。这篇工作提示我们：**Lamb 移位项可能贡献显著的阶数依赖调制**，需要在我们的多体模拟里重新评估。

2. **阶数依赖的能带反演**：之前我们关注的是 Berry curvature 在谐波阶上的签名（circular dichroism 的阶数结构）。如果叠加**环境诱导的阶数选择增强/压制**，会显著影响反演的可靠性。这是个 paper 需要进一步扩展的耦合测量。

3. **阿秒固体带耗散为探针**：如果能构造一个"环境指纹"——比如 $\omega_c/\Delta E$ 与谐波阶谱的映射——就有可能在阿秒时间尺度上测量材料的电子-声子耦合强度。这与我们用 HHG 探测电子关联、瞬时结构的长程目标完全一致。

4. **多脉冲/双色场下的环境效应**：我们组擅长多光束整形。这篇工作如果扩展到非马尔可夫 regime，或多场调控下环境如何"工程化"调控谐波，会是非常自然的下一步。

## 批判性思考

### 优点
- 物理图像清晰、可检验性强（明确的判据 $\omega_c > \Delta E$）。
- 把 Lamb 移位显式纳入 HHG 理论，是相对论性 QED 传统在固体中的罕见落地。

### 需要追问的问题
1. **二能级近似的有效性**：真实固体 HHG 涉及整个 Brillouin 区的 k-resolved 跃迁、能带色散、多能级干涉。TLS 结果能在多大程度上推广到连续带？是否需要做能带积分？
2. **谱密度的微观实现**：偶极-偶极耦合热库在固体中具体对应哪种激发？光学声子？plasmon？激子库？不同的物理实现可能给出截然不同的 $\omega_c$。
3. **Lamb 移位的可观测签名**：增强是否仅来自"能级涨落的统计平均"，还是有可测的相位印记（如 chirp、CEP 依赖）？如果只有强度变化，实验上难以与简单的相干增强区分。
4. **与已知"环境增强"机制的关系**：已有工作（如 plasmonic enhancement、resonance enhancement）也报告了类似现象。本文的"Lamb 移位增强"与这些机制是叠加、竞争还是统一？
5. **马尔可夫性**：Lindblad 框架隐含了马尔可夫假设。在固体阿秒尺度，电子-声子耦合常表现出非马尔可夫特征——这是否会改变 $\omega_c > \Delta E$ 的判据？
6. **谐波相位的影响**：只讨论了产率（intensity），没有涉及相位。HHG 的阿秒啁啾对环境是否敏感？如果是有，是更强的实验可观测信号。

### 建议的实验检验
- 用 pump-probe 注入已知浓度的载流子（改变 $\omega_c$），观察谐波阶谱的非单调响应。
- 在不同晶体温度下测量（改变声子占据从而改变有效 $\omega_c$），观察低阶 vs 高阶的差异化响应。
- 用 sub-cycle 脉冲验证增强的瞬时特性是否与 Lamb 移位的 virtual 过程时间尺度一致。

## 开放问题

- Lamb 移位诱导的谐波增强是否在**连续带**体系中仍存在？是否需要修改判据？
- **非马尔可夫**环境下阶数依赖效应如何修正？
- 能否从实测谐波阶谱**定量反演**固体中的有效谱密度 $\omega_c$？
- 多体环境中，Lamb 移位与 Kondo-like 重整是否存在竞争？
- 阶数依赖的环境重构能否用来**主动工程化**谐波谱形（e.g., 优化特定阶的效率）？

## 来源
- 原始材料：2026-260927742-order-dependent-modification-of-high-harmonic.md
- 蒸馏时间：2026-10-04T10:52:53Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：Lindblad 主方程下环境对 HHG 的阶数分辨重构——谱密度截止 ω_c > ΔE 时环境增强而非压制谐波产率，Lamb 移位诱导能级涨落为微观机制（Zhang 等）

**原理**：挑战固体 HHG 领域'环境耦合总扮演抑制角色'的根深蒂固常识：二能级系统 + Lindblad 开放量子系统模型证明——当耦合谱密度截止频率 ω_c 超过系统能级间距 ΔE 时，环境反而增强谐波产率且带鲜明阶数选择性；增强微观机制：非来自布居弛豫或退相干'增益通道'，而源于 Lamb 移位（与热库的虚光子交换）诱导的能级涨落——环境对系统哈密顿量的动力学重整；阶数依赖环境响应：低阶与高阶谐波呈现明显不同的环境响应——弛豫时间唯像图像在阶数分辨尺度上失效，建立'阶数选择性的环境重构'新机制；理论-实验桥接：谐波谱的阶数依赖衰减轮廓不再是'噪声'而是蕴含谱密度形状/Lamb 移位强度等微观环境信息的载体——为固体耗散谱学（dissipation spectroscopy via HHG）打开窗口。方法表：TLS 系统（抓住 level spacing 核心标尺）+ 偶极-偶极热库（super-Ohmic-like 谱密度）+ Lindblad 主方程（正确处理耗散与相干）+ 关键判据 ω_c > ΔE；把常被忽略的 Lamb 移位项（幺正修正）单独拉出与耗散解耦分析。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 核心判据 | 谱密度截止频率 ω_c > 能级间距 ΔE 时环境增强谐波产率（阶数选择性） | 核心要点 |
| 机制 | Lamb 移位诱导能级涨落（非布居弛豫/退相干增益）；环境从'背景'提升为'主动调控自由度' | 核心要点 |

**适用边界**：二能级近似有效性——真实固体 HHG 涉及全 Brillouin 区 k-resolved 跃迁/能带色散/多能级干涉，TLS 结果向连续带推广需能带积分；谱密度微观实现未明（偶极-偶极热库在固体中具体对应光学声子/plasmon/激子库——不同物理实现给出截然不同 ω_c）；Lamb 移位的可观测签名（仅强度变化还是有相位印记如 chirp/CEP 依赖）待区分；与 plasmonic/resonance enhancement 等已知'环境增强'机制的关系（叠加/竞争/统一）未厘清；Lindblad 隐含马尔可夫假设——固体阿秒尺度电-声子耦合的非马尔可夫特征是否改变 ω_c > ΔE 判据未知；仅讨论产率未涉相位（HHG 阿秒啁啾对环境是否敏感或为更强可观测信号）。
**代表作**：Zhang 等, Order-Dependent Modification of HHG by Quantum Dissipation and Lamb Shift（Lindblad 主方程，arXiv:2609.27742，2026）
*方法卡回补 2026-10-04*


## 合并自「Order-Dependent Modification of HHG by Quantum Dissipation and Lamb Shift」

# Order-Dependent Modification of HHG by Quantum Dissipation and Lamb Shift

> Zhang, Wu, Li (2026), arXiv:2609.27742

## 林赛的理解

这篇 letter 抓住了我一直在关注的一个核心张力：**在固体 HHG 中，电子从来都不是"裸"系统——它嵌在能带、多体关联、声子浴里，而我们通常用一个单一的退相干时间 T₂ 来抹平这一切**。作者用 Lindblad 主方程处理一个与热浴通过偶极-偶极相互作用耦合的二能级系统，并指出当耦合谱密度的截断频率大于能级间距时，环境的贡献不再是单纯的压制，反而可以通过 Lamb shift 诱导的剧烈能级涨落来**提升**谐波产额。这一点很关键，因为：

1. **它直接挑战了"统一阻尼"的图像**——即 T₂ 越短，谱越宽越弱的传统直觉。我们组之前在解谱、做 sub-cycle tracing 时也常被这种简化假设坑过。
2. **它揭示了 order-dependent 的行为**——低阶与高阶谐波对环境的响应不同，这意味着我们用 HHG 谱去反推电子动力学时，不同阶的"信噪比"和物理内容可能截然不同。
3. **这是一个模型层面的结果**（二能级 + Lindblad），还远不是真实固体的多带 + 多体图像，但作为**机制原型的证明**，它具有方向性的指导意义。

作为 PI，我读这种 paper 不是为了重复它，而是想从中提取**可迁移的物理图像**和**可能的新实验思路**。

## 核心要点

### 主要发现
- **反直觉的增强效应**：当环境耦合谱密度的截断频率 $\omega_c$ 超过系统能级间距时，热浴耦合**不是单纯压制**谐波效率，反而可以**增强**谐波产额。
- **机制归属**：增强源自 Lamb shift 引起的**剧烈能级涨落**（level fluctuations）——而非通常所认为的纯耗散通道。
- **Order 依赖性**：环境对 HHG 的影响**显著依赖于谐波阶次**，低阶与高阶谐波表现出明显不同的响应行为。
- **理论框架**：使用 Lindblad master equation 处理二能级系统与热浴的偶极-偶极耦合。

### 方法亮点
- **Lindblad + 偶极-偶极耦合**的设定，比常见的纯退相干速率（pure dephasing rate）模型更微观，因为它把 bath 的谱结构 $\omega_c$ 作为显式参数。
- **明确区分 Lamb shift 与 dissipation**——这是 Jaynes-Cummings / spin-boson 文献中常见的拆分视角，但**很少被带入强场 HHG 的讨论**。
- **Order-dependent 分析**——把谐波谱按阶次切片，而不是只关心 cutoff 或总效率，这种"谱分辨"的角度对 attosecond 谱学非常重要。

## 实验/研究关联

### 与林赛工作的潜在连接

1. **固体 HHG 中的退相干解读**：我们组在解释实验 HHG 谱时，常需要引入一个 effective dephasing time。这个工作提示我们：**单一 T₂ 可能根本不够**——能级间距与 bath cutoff 的相对大小，可能决定谐波是被压低还是被放大。

2. **Attosecond 谱学的环境探针**：如果不同阶的谐波对环境的敏感度不同，那 HHG 谱本身就可能成为**多体环境谱密度的探针**——这一点对凝聚态 attosecond 谱学有直接意义。

3. **与 Lamb shift 工程**：如果在实验中能通过材料工程（如改变 plasmonic 近场结构的谱截断）来调制 $\omega_c$，可能实现对谐波产额的定向调控。这是一个潜在的可验证预言。

### 与近期文献的呼应
- 与近年来"环境辅助量子输运"（environment-assisted quantum transport）的图像在精神上类似——bath 不一定总是敌人。
- 固体 HHG 领域最近开始关注 electron-phonon coupling 对谐波偏振与 ellipticity 的影响，这篇 paper 把视角推进到了**非马尔可夫/谱结构层面**。

## 批判性思考

### 局限性（需要警惕的地方）
- **二能级系统的过度简化**：固体 HHG 的能带结构（band structure）、Berry curvature、多带间干涉是核心物理，二能级图像能否 capture 这些是存疑的。**增强效应的具体数值大小**在这里被完全省略（摘要未给出），所以我们无法判断这个效应是否足够显著以在真实固体中存活。
- **偶极-偶极耦合 bath 的物理合理性**：在固体中，主流的 bath 是 phonons（声子浴），其谱密度特征与这里假设的偶极-偶极型可能不一致。需要追问：这个模型的 bath spectral density $J(\omega)$ 是否对应一个**现实的固体 bath**？
- **缺少与实验的直接对比**：摘要完全没有给出现有实验数据的比对，这是 letter 风格的限制，但也意味着理论的实验可证伪性需要后续工作来补。
- **Order-dependence 的物理解释模糊**：为什么低阶和高阶会表现不同？是因为 Lamb shift 主要修改了 resonance 条件（影响低阶），还是因为高阶对能级瞬时位置更敏感？这需要更细致的微观光谱分析。

### 我会问作者的问题
1. 增强效应在 $N$-level 或连续谱系统中是否仍然存在？还是二能级模型特有的 artifact？
2. $\omega_c$ 跨越能级间距的临界行为是 smooth 还是 sharp？这个阈值是否对应一个 **level crossing / avoided crossing**？
3. 如果把偶极-偶极耦合替换为 electron-phonon Fröhlich 型耦合，结论是否定性保持？

### 对未来工作的启发
- 在**多带 + Lindblad**框架下重做这个分析，可能是通向真实固体 HHG 环境效应的一步。
- 实验上：能否通过**温度依赖的 HHG 测量**（改变 phonon bath 的有效谱密度）来检验 order-dependence 预言？
- 能否把这种 Lamb-shift 增强效应作为一种**相干控制的新通道**——即通过设计环境而非设计驱动场来调控 HHG？

## 开放问题

- 这个 order-dependent 增强效应在多带 / 连续谱系统中是否存活？
- 增强效应的物理图像（level fluctuations）能否被实验直接探测？例如通过 HHG 谱的亚周期 tracing。
- bath 谱密度 $J(\omega)$ 的具体形式对结论的鲁棒性如何？
- 这个机制是否可以为**固态 attosecond 谱学**提供新的环境表征方法？

## 来源
- 原始材料：2026-2609.27742-order-dependent-modification-of-high-harmonic-gene.md
- 蒸馏时间：2026-10-05T04:53:58Z
- arXiv: [2609.27742](https://arxiv.org/abs/2609.27742)


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：Lindblad 主方程分析量子耗散与 Lamb shift 对 HHG 的阶次依赖修正

**原理**：分析环境耦合对高次谐波产生的非平凡修正。核心机制：Lindblad 主方程处理与热浴偶极-偶极耦合的二能级系统，把 bath 谱密度截断频率 ω_c 作为显式参数——当 ω_c 超过系统能级间距时，热浴耦合不再单纯压制谐波效率，反而经 Lamb shift 诱导的剧烈能级涨落增强谐波产额；环境对 HHG 的影响显著依赖谐波阶次（低阶与高阶响应不同），明确区分 Lamb shift 与 dissipation 两个通道。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 理论框架 | Lindblad master equation，二能级系统 + 热浴偶极-偶极耦合 | 方法亮点 |
| 关键条件 | 谱密度截断频率 ω_c > 系统能级间距时出现增强（反直觉） | 主要发现 |
| 增强机制 | Lamb shift 诱导的剧烈能级涨落（非纯耗散通道） | 主要发现 |

**适用边界**：二能级模型原型（页面自警）：多带/Berry 曲率/多带干涉等固体核心物理未涵盖；增强效应的具体数值大小摘要未给出；偶极-偶极型 bath 谱密度是否对应真实固体声子浴存疑；无实验对比；order-dependence 的微观解释（Lamb shift 修改共振条件 vs 高阶对瞬时能级敏感）需正文细化；多带 + Lindblad 重做分析、温度依赖 HHG 测量检验为后续方向。
**代表作**：Zhang, Wu, Li, Order-Dependent Modification of HHG by Quantum Dissipation and Lamb Shift, arXiv:2609.27742 (2026)
*方法卡回补 2026-10-05*


## 合并自「Order-Dependent Modification of High-Harmonic Generation by Quantum Dissipation and Lamb Shift」

# Order-Dependent Modification of High-Harmonic Generation by Quantum Dissipation and Lamb Shift

**arXiv**: [2609.27742](https://arxiv.org/abs/2609.27742) | **方向**: 固体HHG

## 深度解析

### 研究问题（Research Question）

First Lindblad master-equation treatment of HHG in a driven two-level system coupled to a heat bath. Decomposes environmental influence into dissipator plus Lamb shift and finds the two act in opposite directions: dissipation suppresses all harmonics monotonically, while the Lamb shift can enhance harmonic yield when the bath cutoff frequency omega_c exceeds the level spacing Delta_E. Breaks the universal relaxation-time (T2) damping picture that most solid-HHG models import uncritically.

### 研究背景（Background）

Direct hit on the decoherence/dissipation module of solid-HHG theory that project A needs but does not yet have. The sigma_solid derivation currently carries dephasing as a phenomenological T2 factor - this paper shows that treatment is structurally wrong: the coherent part of the environment (Lamb shift) is also order-selective and can add channels rather than remove them. Two transferable pieces: (1) the even-order-only modulation of the Lamb shift is a symmetry statement (inherits omega(t) even-harmonic content) that survives beyond two-level; (2) the sideband-channel counting argument gives a way to think about how environment-mediated mixing redistributes spectral weight across harmonic orders without destroying the main emission. For ZnO modeling: the relevant bath cutoffs (LO phonon ~70 meV vs band gap 3.4 eV) sit far below optical-transition spacings, so the omega_c > Delta_E enhancement regime is unlikely for interband transitions but could apply to intra-excitonic or shallow-donor spacings.

### 研究方法（Methods）

Lindblad master equation with explicit separation of Lamb-shift Hamiltonian from dissipator; interaction-picture Bessel expansion of the off-diagonal density matrix element mapping sideband channels to harmonic orders; instantaneous-eigenfrequency fluctuation-spectrum analysis of H_LS(t)

### 主要发现与核心结论（Main Results）

- Switching threshold at omega_c ~ Delta_E: bath spectral-density cutoff below the level spacing gives suppression, above it gives enhancement - the environment is not always a sink
- Lamb shift alone reproduces the full threshold behavior (control calculation with dissipator set to zero); dissipator alone gives pure monotonic suppression at all omega_c
- Lamb shift oscillates at even multiples of the driving frequency (0, +/-2omega, +/-4omega...) because it inherits the instantaneous eigenfrequency omega(t) = sqrt((Delta_E)^2 + 4|d|^2|E(t)|^2) which contains only even harmonics of the field
- Sideband picture: Lamb-shift modulation at 2m*omega shifts the n-th harmonic response to (n-2m)-th order channels (Bessel-function coefficients); higher harmonics have more sideband channels so gain grows with order - explains order-selective enhancement
- Order-dependent nonmonotonicity: low harmonics (5,7,9) rise monotonically with coupling eta; high harmonics (11,13,15) first rise then fall as dissipation overtakes the Lamb-shift gain

### 潜在研究方向（Future Directions）

Extension beyond the two-level model to multiband crystals with realistic spectral densities (phonon bath, electron-electron bath); order-resolved experimental test of the omega_c threshold in a material where the bath spectrum is tunable (e.g. temperature-dependent phonon bath)

### 来源

- [arXiv 2609.27742](https://arxiv.org/abs/2609.27742)
- 导入自 hermes 深度分析（2026-10-30T04:40:24Z）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：Lindblad 主方程处理二能级 HHG：量子耗散与 Lamb 移动的阶次依赖修饰

**原理**：首个对受驱二能级系统 HHG 的 Lindblad 主方程处理：环境影响分解为耗散子 + Lamb 移动，二者方向相反——耗散单调抑制所有谐波，Lamb 移动在浴截断频率 ω_c > 能级间距 Δ_E 时反而增强产额；Lamb 移动以驱动频率偶数倍振荡（继承瞬时本征频率 ω(t) 的偶次含量），边带通道计数解释阶次选择性增强——打破固体 HHG 模型普遍照搬的普适 T2 阻尼图像。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 开关阈值 | ω_c ~ Δ_E（低于抑制/高于增强；Lamb 移动单独即可复现全部阈值行为） | 主要发现 |
| Lamb 移动振荡频率 | 0, ±2ω, ±4ω…（驱动频率偶数倍） | 主要发现 |
| 阶次依赖非单调性 | 低阶（5/7/9）随耦合 η 单调上升；高阶（11/13/15）先升后降 | 主要发现 |

**适用边界**：二能级模型（多能带晶体+真实谱密度待推广）；ZnO 应用判断：LO 声子 ~70 meV 远低于带间跃迁间距 3.4 eV，ω_c > Δ_E 增强区对带间跃迁不太可能、对激子内/浅施主间距可能适用。
**代表作**：Wang et al., Order-Dependent Modification of HHG by Quantum Dissipation and Lamb Shift, arXiv:2609.27742 (2026)
*方法卡回补 2026-10-30*

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry 曲率]]
- [[Order-Dependent Modification of HHG by Quantum Dissipation and Lamb Shift]]
- [[Order-Dependent Modification of High-Harmonic Generation by Quantum Dissipation and Lamb Shift]]
- [[TDDFT]]
- [[pump-probe]]
- [[固体HHG]]
- [[固体高次谐波]]
- [[多体环境耦合]]
- [[强场超快]]
- [[强场超快光学]]
- [[相干控制]]
- [[量子耗散与退相干]]
- [[量子输运]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
