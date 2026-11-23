---
title: "能谷贝里曲率偶极矩诱导的非线性能谷霍尔效应"
type: "papers"
created: "2026-10-05T04:53:07Z"
updated: "2026-11-15T15:09:24Z"
tags: ["能谷电子学", "贝里曲率偶极矩", "非线性霍尔效应", "对称性分析", "第一性原理", "层状材料", "deepxiv-论文库", "深度解析", "Berry曲率偶极", "层群分类"]
related: ["2504.06130", "2608.16020", "Berry curvature dipole", "Berry 曲率", "Floquet工程", "Valley Berry Curvature Dipole Induced Nonlinear Valley Hall Effect", "Valley Berry curvature dipole induced nonlinear valley Hall effect", "arpes", "pump-probe", "time-reversal symmetry", "valley Hall effect", "valley-HHG圆二色性", "交变磁体", "光致贝里曲率", "圆二色性", "强场超快", "强场超快光学", "时间反演不变能谷", "相干声子", "能谷分辨非线性响应", "能谷电子学", "能谷霍尔效应", "谷霍尔效应", "贝里曲率偶极矩(BCD)", "量子几何", "非线性光学", "非线性霍尔效应", "高次谐波产生", "高次谐波产生（HHG）"]
source_raw: "2026-2609.29226-valley-berry-curvature-dipole-induced-nonlinear-va.md"
growth_stage: "growing"
confidence: 0.6
digest_level: "abstract"
auto_grown: true
review_status: "pending"
updated_at: "2026-10-27T12:48:12Z"
merged_from: ["wiki/papers/2609.29226.md", "wiki/papers/2026-260929226-valley-berry-curvature-dipole-induced-nonline.md"]
---

# 能谷贝里曲率偶极矩诱导的非线性能谷霍尔效应

## 林赛的理解

读这篇 Xiong、Zhang、Zhang 的工作，从我的强场超快光学背景出发，核心信息是：**他们把传统能谷霍尔效应（valley Hall effect）从"贝里曲率本身"层面推进到了"贝里曲率偶极矩（BCD）"层面，得到一种全新的非线性能谷霍尔响应**。而且这个机制有一个非常严格的对称性筛选——它要求能谷之间是**时间反演不变的连接关系**（time-reversal-invariant valleys），而不是常规的时间反演配对能谷。这一点很关键，意味着材料必须破坏某些对称性使得 K 和 K' 在 T 操作下各自映射到自身而不是互换。

作为超快光学 PI，我立刻想到的是：这个 vBCD 的非线性响应天然适合用**圆偏振/线偏振强光场**来驱动和切换，因为外加驱动场方向直接调控非线性霍尔响应是他们明确指出的结论。而能谷自由度本身又是光场（特别是圆偏振光）能够直接耦合的物理量（光学选择定则）。这给我一个直觉：**vBCD 应该能在飞秒尺度上被光场瞬时调控**，而且它的非局域输运信号可能提供一种新的 all-optical 探测方案。

但我也需要清醒地认识到：原始摘要只给到这一层级，具体的层群列表、对称约束的具体形式、应变 Nb₃SBr₇ 的能带结构数值、vBCD 的大小量级——这些都没有给出。我不能从摘要里编造。

## 核心要点

1. **新机制——谷贝里曲率偶极矩（vBCD）**：把 Berry curvature dipole 这一原本用于解释非线性电荷霍尔的概念，**特化到能谷自由度上**，提出一种由 vBCD 引起的非线性能谷霍尔效应。

2. **严格的对称性筛选**：该效应**禁止于常规时间反演配对的能谷**（即 inversion-related 或 T-related K/K'），**只允许于时间反演不变的能谷**（T-invariant valleys，即每个 K 谷在 T 操作下映射到自身）。这给出了一种非常 clean 的材料筛选判据。

3. **对称性与层群分析**：作者**枚举了候选层群**并给出 vBCD 存在的详细对称性约束条件。这部分是论文的方法论亮点——从群论出发的系统性分类。

4. **驱动场方向可调控**：非线性 valley Hall 响应以及非线性电荷 Hall 响应均可通过**改变驱动电场方向**来控制。这意味着响应张量的角度依赖是高度各向异性的，可作为实验指纹。

6. **材料实例**：在**应变 Nb₃SBr₇** 中通过第一性原理计算验证。这是个具体的可实验材料，但需注意：原文用"strained"修饰，意味着需要应变工程来达到所需对称性。

7. **非局域输运信号**：讨论了 vBCD 引起的非线性 valley Hall 的**非局域输运特征**——这是实验可观测量的预测。

## 实验/研究关联

从强场超快光学 PI 的视角，几个直接的关联点：

- **Floquet / light-induced Berry curvature 的类比**：我们已经知道圆偏振光可以在石墨烯等 Dirac 材料中**光致生成有效 Berry curvature**，驱动所谓的"光学 Floquet 能谷霍尔效应"。vBCD 的存在意味着——如果我们能用强场瞬时调控 Berry curvature 分布及其偶极矩，就可能在飞秒时间尺度上**开关**这种非线性霍尔响应。

- **高次谐波作为 BCD 探针**：在我们组擅长的**高次谐波产生（HHG）**中，最近几年已有理论工作（如文献中关于 BCD scaling of HHG 的讨论）指出，**贝里曲率偶极矩会调制高次谐波的偏振依赖和椭圆依赖**。如果 vBCD 能在对称性合适的层状材料中被识别，那么** HHG 椭圆依赖谱**有可能作为 vBCD 的**全光指纹**。这是值得和组内讨论的方向。

- **光电流注入（photogalvanic effect / shift current）**：非线性霍尔响应本质上是二阶光电流响应。**圆偏振光的光电流（CPGE）和线偏振光的 shift / injection current** 在反演对称破缺的能谷材料中已有大量研究。vBCD 的发现意味着二阶光电流张量中有一类被忽略的**偶极矩起源分量**，它和传统 Berry curvature 起源的分量可以通过**偏振旋转对称性**和**角度依赖**区分开来（具体怎么区分需要看正文）。

- **应变工程 + 超快应变脉冲**：Nb₃SBr₇ 用的是应变，这让我立刻联想到**超快应变脉冲 / phonon pumping**——用 THz 或中红外脉冲激发相干声子模式，瞬时打破/恢复对称性，从而**在皮秒时间尺度内开关 vBCD**。这种 time-resolved 测量可以区分静态 BCD 贡献和动态光场贡献。

- **非局域输运的时域对应物**：论文讨论的是非局域 DC 输运。在超快光学中，对应物可能是**两个空间分离点的时域电流关联**，或者用**时间分辨 ARPES / tr-STM** 来直接成像贝里曲率偶极矩的动量空间分布。

## 开放问题

1. **vBCD 的量级到底有多大？** 摘要没说。第一性原理在 Nb₃SBr₇ 里给出的 vBCD 数值是多少（相对于 BCD 的常规量级）？它是否足以在实验上观测？这是判断论文影响的关键参数。

2. **"时间反演不变能谷"的物理图像**：什么样的层群才能给出 T-invariant valley？通常 T 把 K 映到 -K；如果要 K 在 T 下不变，需要时间反演对称中心就在 K 点上（K = -K 即 Γ 点），或者 K 在 T 下是自身的镜像。这对应的是不是 inversion + T 的复合操作把 K 映到自身？需要看正文。

3. **光场如何瞬时调控 vBCD？** 既然驱动场方向能调控响应，强场脉冲的偏振矢量变化就能在单发激光层面上调控 vBCD 引起的电流。但脉冲持续时间（几个飞秒）和 Berry curvature 的响应时间尺度是否匹配？这是一个时间尺度问题。

4. **和高次谐波的定量联系**：vBCD 是否进入 HHG 的 yield / ellipticity dependence？如果能建立 mapping，我们可以用 HHG 作为 tabletop 探针来表征 vBCD，而无需做输运测量。

5. **多体相互作用的影响**：摘要完全没提电子-电子相互作用。Nb₃SBr₇ 是关联体系？是否需要考虑激子修正？

6. **温度与无序**：vBCD 作为偶极矩，对动量空间分布的对称破缺敏感。室温下热展宽和缺陷散射是否会压制这种效应？需要 K 温度实验验证。

7. **材料清单是否完整？** 候选层群有几个？除了 Nb₃SBr₇，是否有更易合成、更适合超快测量的材料（如已知的高迁移率 TMD 异质结、扭转多层石墨烯等）？

## 来源
- 原始材料：2026-2609.29226-valley-berry-curvature-dipole-induced-nonlinear-va.md
- 蒸馏时间：2026-10-05T04:53:07Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：谷贝里曲率偶极矩（vBCD）诱导非线性能谷霍尔效应（对称性筛选 + DFT 验证）

**原理**：把 Berry curvature dipole 特化到能谷自由度，提出由 vBCD 引起的非线性能谷霍尔效应。核心机制：严格的对称性筛选——效应禁止于常规时间反演配对能谷、只允许于时间反演不变能谷（每个 K 谷在 T 操作下映射到自身）；作者枚举候选层群并给出 vBCD 存在的群论约束（系统性分类为方法论亮点）；非线性 valley Hall 与非线性电荷 Hall 响应均可通过改变驱动电场方向调控（各向异性角度依赖为实验指纹）；在应变 Nb₃SBr₇ 中第一性原理验证，并给出非局域输运可观测量预言。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 对称性判据 | 仅允许时间反演不变能谷（T-invariant valleys）；常规 TR 配对能谷中被禁止 | 核心要点 |
| 调控手段 | 改变驱动电场方向控制非线性 valley/charge Hall 响应 | 核心要点 |
| 材料实例 | 应变 Nb₃SBr₇（第一性原理验证，需应变工程达到所需对称性） | 核心要点 |

**适用边界**：摘要级（页面自注不可编造）：vBCD 量级、层群完整清单、对称约束具体形式、Nb₃SBr₇ 能带数值均未给出；'时间反演不变能谷'的层群物理图像、多体相互作用、温度/无序容忍度待正文；与 HHG 椭圆依赖谱的全光指纹联系为页面引申设想非原文内容。
**代表作**：Xiong, Zhang, Zhang, arXiv:2609.29226 (2026)
*方法卡回补 2026-10-05*

## 合并自「Valley Berry curvature dipole induced nonlinear valley Hall effect」

# Valley Berry curvature dipole induced nonlinear valley Hall effect

**arXiv**: [2609.29226](https://arxiv.org/abs/2609.29226) | **方向**: 能谷电子学

## 深度解析

### 研究问题（Research Question）

Gap: 非线性能谷霍尔效应 (nonlinear VHE, jv ~ E^2) 此前的机制全部要求 T-odd (时间反演奇)——存在于 T-连接谷体系 (graphene/TMD 的 K-K' 谷, 靠时间反演相连). TRIV (time-reversal-invariant valleys, 谷坐在 T-不变动量点, 两谷靠晶体对称性相连而非 T) 体系的非线性 VHE 是未开发领域. Contributions: 揭示一类此前未探索的非线性 VHE——能谷 Berry 曲率偶极 (vBCD) 机制, 具有 T-even 特征: 对 T-连接谷严格禁止, 只在 TRIV 体系允许. 对称性分析识别支持该效应的全部 layer groups (中心矩形晶格类); vBCD 与 (电荷) BCD 在 2D 面内永远垂直——通过驱动场方向可选择性地产生能谷霍尔电流或电荷霍尔电流. 有效模型 + 第一性原理 (应变单层 Nb3SBr7) 演示, 预言非局域输运信号随电阻率的标度律.

### 研究背景（Background）

agent 打 5 分的判断 (DC 输运, 无光场) 在字面上正确, 但低估了概念接口的价值. (1) 课题 D (valley-selective sigma_solid) 的对称性方法论同构: 本文的核心问题是'谷间对称性关系 (T vs 晶体 Q) 如何决定非线性响应的允许性'——与课题 D 的 WSe2 谷选择 HHG (K/K' 靠 T 连接, 圆偏振选择) 是同一对称性分析在不同响应通道的应用. TRIV 框架提示: 若把课题 D 推广到 TRIV 材料, 谷选择的物理会完全不同 (T-even 机制允许)——这是课题 D 材料空间的一个未探索维度. (2) Berry curvature dipole 与非线性光学的共享概念: BCD 在非线性霍尔 (DC) 和某些非线性光学响应 (如 circular photogalvanic 类) 中都出现; vBCD 的光学对应物是光场版机制的现成出发点——lightwave valleytronics 的 TRIV 扩展. (3) Fudan Xiao Cong + HK PolyU Yang Shengyuan 组: 能带几何与非线性输运理论的活跃组, 林赛 valley 方向的理论合作候选. (4) 与 2608.16020 (有限动量几何): 一个把量子几何扩展到有限动量 (强场), 一个把谷几何量扩展到 T-even 偶极 (TRIV)——量子几何工具箱的两次正交扩展. (5) 诚实定位: 本文本身是 DC 输运理论, 对林赛光场主线是概念/对称性借鉴而非直接方法来源——agent 的 5 分合理, 深读的价值在对称性框架的迁移潜力. (6) 局限: 纯理论 (输运公式+第一性原理); Nb3SBr7 应变工程未实验演示; 非局域标度律的验证依赖高质量器件; 无光场动力学.

### 研究方法（Methods）

- vBCD 概念与对称性分类: 能谷分辨的 Berry curvature dipole 作为新的能带几何量; 支持 layer groups 的系统枚举——TRIV 材料筛选的操作手册.
- 场方向通道选择: vBCD x BCD 垂直性 -> 驱动场方向切换能谷/电荷霍尔通道——器件层面的正交控制旋钮.
- 非局域标度律判别术: V_NL ~ rho^n 的幂次 (3/4 vs 5) 区分 vBCD/BCD 主导 vs T-连接机制——纯电学测量的机制指纹.
- chi_v 可由局域非线性电荷输运独立标定 (zeta_v 同)——局域+非局域联测的机制诊断流程.

### 主要发现与核心结论（Main Results）

- vBCD 新机制: 能谷 Berry 曲率偶极 (valley Berry curvature dipole) 诱导的非线性 VHE 是 T-even 的——与既有非线性 VHE 机制 (Drude 类分布修正/Berry-connection polarizability, 全 T-odd) 本质不同. T-连接谷体系严格禁止, TRIV 体系允许.
- TRIV 对称性框架: 谷坐在 T-不变动量点 (如 BZ 边界中点), 两谷由晶体对称性 Q (而非 T) 相连. 支持该效应的 layer groups 属中心矩形晶格类——候选材料空间的第一性原理判据.
- vBCD 与 BCD 垂直 + 场方向选择: vBCD 和电荷 BCD 在 2D 面内总是互相垂直. 驱动场沿 vBCD -> 纯能谷霍尔; 沿 BCD -> 纯电荷霍尔. 一个器件两个通道, 由场方向切换——非互易的通道控制.
- 材料演示: 应变单层 Nb3SBr7 有可观 vBCD. 沿 y 方向 (vBCD 方向) 驱动时非线性能谷霍尔电导 chi_v ~ 0.18 mA/V^2——可测的量级.
- 非局域标度律 (实验判据): TRIV 体系的直接/逆非线性 VHE 若由 vBCD/BCD 主导, 则 chi_v, zeta_v 都 ~ tau -> 非局域信号 V_NL^3w ~ rho^3, V_NL^4w ~ rho^4. 与 T-连接谷体系 (实验观测 rho^5, He et al. graphene 超晶格) 不同——标度律直接区分机制.
- 逆非线性 VHE 不互易: 线性情形直接/逆 VHE 靠 Onsager 互易; 非线性情形 (T-连接与 TRIV 都是) 两过程对称性不同不互易——逆过程由 valley density gradient 驱动 (jc = -tau z_hat x F(Lambda_c dot F)).
- 公式 (18)(19) 对 T-连接与 TRIV 都通用——非线性能谷输运的一般框架.

### 潜在研究方向（Future Directions）

- 实验验证: 应变 Nb3SBr7 单层的非局域测量 (V^3w ~ rho^3 或 V^4w ~ rho^4 是 vBCD 指纹)——与 graphene 超晶格 rho^5 对照.
- TRIV 材料家族扩展: 中心矩形晶格 layer groups 的系统筛选 (2D 材料数据库)——比 Nb3SBr7 更大 vBCD 的候选.
- 光场版本 (与林赛方向的关键接口): vBCD 是 DC 输运量, 但其光学对应物 (能谷分辨的非线性霍尔型光学响应) 在 TRIV 体系应该存在——光驱动 vBCD 类效应是把本文物理接入 lightwave valleytronics 的路径.
- 与 altermagnet 能谷体系交叉: TRIV 的对称性分析框架 (晶体对称性 Q 连接谷) 与 altermagnet 的自旋分裂谷同构——交变磁体中 vBCD 类量的对称性允许性值得检查.
- 动态/ Floquet 版本: 周期场驱动下的 vBCD 修饰 (与 2504.06130 OS/BS 相干调制的交叉)——瞬时 vBCD 的超快控制.

### 来源

- [arXiv 2609.29226](https://arxiv.org/abs/2609.29226)
- 导入自 hermes 深度分析（2026-10-09T12:05:05Z）


## 合并自「Valley Berry Curvature Dipole Induced Nonlinear Valley Hall Effect」

# Valley Berry Curvature Dipole Induced Nonlinear Valley Hall Effect

## 林赛的理解

作为长期在强场超快光学方向做 PI 的人，我读这篇论文的第一反应是把它放到"Berry 曲率几何量在非线性响应里的角色"这条主线上——只不过作者处理的是 DC 输运的二阶非线性霍尔，而我组更关心的是光场（特别是强少周期激光）驱动的非线性极化和高次谐波产生（HHG）。这篇论文的真正价值在我看来不在 Nb3SBr7 这个具体材料，而在它给出的那套语言：**将 Berry 曲率偶极（BCD）从总 Berry 曲率层面推广到"能谷分辨的 Berry 曲率偶极"（vBCD），并明确写出在哪些层群对称性下这个偶极是非零的、在哪些对称性下被严格禁止**。这套"对称性选择定则 → 二阶非线性响应"的推理路径，跟我们在 valley-HHG、shift-current、injection current 里用的几乎是同一套工具，只是一个走实空间电荷流、一个走动量空间能谷流。我会在笔记里专门对照一下两边的对称性语言是不是真的同构。

## 核心要点

- **新机制：vBCD 诱导的非线性能谷霍尔效应**。作者提出 valley Berry curvature dipole（vBCD），把它作为一类此前未被识别的非线性能谷霍尔响应的几何起源。和传统的 BCD 机制相比，关键区别在于这里的偶极是按能谷分辨的（valley-resolved），而不是全 Brillouin 区 Berry 曲率的整体偶极。
- **对称性判据是这篇论文的核心结论之一**：
  - 该效应在常规的"time-reversal-connected 能谷"体系中**被对称性禁止**；
  - 在"time-reversal-invariant 能谷"的能谷电子体系中**被允许**。
  作者据此列出了候选层群和 vBCD 的详细对称性约束。
- **驱动场方向可作为调控旋钮**：非线性能谷霍尔响应和与之伴随的非线性电荷霍尔响应，都能通过改变驱动场方向来切换/调控。这意味着 vBCD 提供了两个独立但耦合的响应通道。
- **材料实例验证**：应变下的 Nb3SBr7（层状材料）。第一性原理计算被用来展示 vBCD 在真实材料中的非零取值与场方向响应；并讨论了对应的非局域（nonlocal）输运特征作为实验可观测信号。
- **方法组合**：层群对称性分类与 vBCD 约束推导 → 有效模型 → 第一性原理（应变 Nb3SBr7）→ 非局域输运讨论。属于"对称性筛选 + 模型验证 + 材料落地"的典型三段式。

## 实验/研究关联

- **与我组的强场超快光学的最直接接口在对称性语言**：vBCD 这套"哪些对称操作允许 / 禁止二阶能谷分辨响应"的判据，跟我们在 valley-HHG 中分析圆二色性（CD）和 selection rules 时用的层群 / 空间反演 / 镜面 / 时间反演乘操作的框架几乎是一一对应的。具体到我组关心的两个问题：
  1. **shift-current / injection-current 类型的光电流二阶响应**和这里的非线性能谷霍尔在对称性层面是否共享同一组允许层群？
  2. **强场 valley-HHG 的圆二色性**——即左旋 vs 右旋圆极化驱动下 HHG 产率的差异——其选择定则能否用同样的"vBCD-like 能谷分辨几何量"重写？
  如果这两个问题的答案是"基本同构"，那它意味着 DC 二阶输运和光驱动二阶非线性响应在底层共享同一类能谷分辨几何张量，区别只在驱动场的频率（DC vs 光学）。
- **材料平台层面**：应变 Nb3SBr7 作为可调"能谷对称性破缺"材料的做法，启发我可以去看 Nb3XBr7 / Nb3XCl7 这一族是否能在强光场下作为"对称性可调的能谷 HHG 候选体系"。
- **非局域输运 vs 光学远场**：作者把实验可观测信号定位在非局域输运（nonlocal transport）上。我组对应的可观测信号应该是**反射 / 透射 HHG 谱中的二阶 valley-resolved 通道**，例如特定阶次谐波的圆二色性或 valley-polarization-dependent yield。

## 开放问题

- vBCD 在 Nb3SBr7 上的数值量级（原文摘要未给出具体数值），以及它和已有 BCD 贡献的相对大小——需要回原文正文/补充材料确认。
- **时域对应物**：vBCD 是 DC 平衡态几何量。如果在 pump–probe 框架中瞬时打破时间反演对称性（譬如用圆极化光脉冲瞬时注入 valley polarization），vBCD 是否会诱导一个**时间依赖的非线性能谷霍尔流**？这跟我组一直在追的"光场瞬时调控 valley Hall response"直接挂钩。
- **从 DC 到光频的推广**：是否可以把 vBCD 的对称性分类直接翻译成 valley-HHG 的 CD 选择定则？两边用到的对称操作相同，但光频下还多出 photon energy / 跃迁选择性的额外约束，是否会进一步限制某些原本在 DC 下允许的通道？
- **非局域输运信号 vs 非局域光学信号**：作者讨论的 nonlocal transport 是电学测量，我组对应的是否可以是 nonlocally generated HHG（例如从一个 valley 区域注入电流、在相邻 valley 区域辐射 HHG）？这是一个可能的合作方向。
- **温度 / 应变扫描作为验证手段**：应变 Nb3SBr7 提供了连续的对称性调控自由度。可以问：随着应变连续变化，vBCD 是否出现一个突变（对称性破缺的相变点）？这跟我组用应变调控 valley-HHG CD 的经验非常类似，值得平行比较。

## 来源
- 原始材料：2026-260929226-valley-berry-curvature-dipole-induced-nonline.md
- 蒸馏时间：2026-10-04T12:00:18Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：能谷 Berry 曲率偶极（vBCD）诱导的非线性能谷霍尔效应——能谷分辨几何偶极新机制 + 层群对称性选择定则 + 应变 Nb₃SBr₇ 第一性原理验证

**原理**：将 Berry 曲率偶极（BCD）从总 Berry 曲率层面推广到'能谷分辨的 Berry 曲率偶极'（valley BCD, vBCD）——作为一类此前未被识别的非线性能谷霍尔响应的几何起源（关键区别：偶极按能谷分辨而非全布里渊区整体偶极）；对称性判据为核心结论：该效应在常规'time-reversal-connected 能谷'体系中被对称性禁止、在'time-reversal-invariant 能谷'的能谷电子体系中被允许——据此列出候选层群与 vBCD 详细对称性约束；驱动场方向为调控旋钮：非线性能谷霍尔与伴随的非线性电荷霍尔响应均可通过改变驱动场方向切换/调控——vBCD 提供两个独立但耦合的响应通道；方法组合：层群对称性分类与 vBCD 约束推导 → 有效模型 → 第一性原理（应变 Nb₃SBr₇ 层状材料展示 vBCD 非零取值与场方向响应）→ 非局域输运讨论（实验可观测信号）——'对称性筛选 + 模型验证 + 材料落地'典型三段式。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 对称性判据 | vBCD 在 time-reversal-connected 能谷体系被禁止；在 time-reversal-invariant 能谷体系被允许；驱动场方向切换响应通道 | 核心要点 |

**适用边界**：vBCD 在 Nb₃SBr₇ 上的数值量级及与已有 BCD 贡献的相对大小（摘要未给具体数值）需回原文确认；DC 平衡态几何量——时域对应物（pump-probe 中圆极化光脉冲瞬时注入 valley polarization 后 vBCD 是否诱导时间依赖非线性能谷霍尔流——光场瞬时调控直接挂钩）未讨论；DC 到光频的推广（对称性分类是否可翻译为 valley-HHG CD 选择定则——光频多出 photon energy/跃迁选择性额外约束）未验证；非局域输运信号 vs 非局域光学信号的对应未建立；应变连续调谐下 vBCD 突变（对称破缺相变点）未扫描。
**代表作**：Valley Berry Curvature Dipole Induced Nonlinear Valley Hall Effect（层群对称分类 + DFT 应变 Nb₃SBr₇，arXiv:2609.29226，2026）
*方法卡回补 2026-10-04*

<!-- linsai-wikilinks -->
## 关联概念

- [[2504.06130]]
- [[2608.16020]]
- [[Berry curvature dipole]]
- [[Berry 曲率]]
- [[Floquet工程]]
- [[Valley Berry Curvature Dipole Induced Nonlinear Valley Hall Effect]]
- [[Valley Berry curvature dipole induced nonlinear valley Hall effect]]
- [[arpes]]
- [[pump-probe]]
- [[time-reversal symmetry]]
- [[valley Hall effect]]
- [[valley-HHG圆二色性]]
- [[交变磁体]]
- [[光致贝里曲率]]
- [[圆二色性]]
- [[强场超快]]
- [[强场超快光学]]
- [[时间反演不变能谷]]
- [[相干声子]]
- [[能谷分辨非线性响应]]
- [[能谷电子学]]
- [[能谷霍尔效应]]
- [[谷霍尔效应]]
- [[贝里曲率偶极矩(BCD)]]
- [[量子几何]]
- [[非线性光学]]
- [[非线性霍尔效应]]
- [[高次谐波产生]]
- [[高次谐波产生（HHG）]]
<!-- /linsai-wikilinks -->
