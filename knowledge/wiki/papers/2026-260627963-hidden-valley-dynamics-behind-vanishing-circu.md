---
title: "Hidden valley dynamics behind vanishing circular polarization in moiré excitons — 论文精读"
type: "papers"
created: "2026-09-28T04:50:32Z"
updated: "2026-11-15T15:09:24Z"
tags: ["能谷电子学", "莫尔激子", "圆偏振", "时间分辨PL", "双通道模型", "强场超快", "papers", "valley-tronics", "moiré-excitons", "TMD-heterostructure", "time-resolved-PL", "strong-field-ultrafast", "HHG-interpretation"]
related: ["2026-260627963-hidden-valley-dynamics-behind-vanishing-circu", "Hidden valley dynamics behind vanishing circular polarization in moiré excitons", "TMD异质结", "圆二色性", "多通道谷发射补偿假象", "层间激子动力学", "层间耦合", "强场超快", "强场超快光学", "强场驱动", "时间分辨helicity-resolved测量", "能谷电子学", "莫尔超晶格", "谷HHG圆二色信号解读", "谷极化", "谷极化假阴性", "谷高次谐波产生", "速率方程双通道模型", "门电场可调moiré超晶格", "门电场可调莫尔超晶格", "高次谐波产生"]
source_raw: "2026-260627963-hidden-valley-dynamics-behind-vanishing-circu.md"
growth_stage: "growing"
confidence: 0.75
digest_level: "abstract"
auto_grown: true
review_status: "pending"
updated_at: "2026-10-27T12:47:39Z"
merged_from: ["wiki/papers/2606.27963.md"]
---

# Hidden valley dynamics behind vanishing circular polarization in moiré excitons — 论文精读

## 林赛的理解

这篇 Urano et al. (2026) 的工作直接戳到了我自己最关心的一个方法学盲区：**时间积分的圆偏振度作为谷极化代理量的可靠性**。

作为做强场超快光学的 PI，我们组在谷高次谐波产生（valley HHG）和阿秒圆二色测量中，长期把"谐波圆二色性（CD）≈ 0"解读为"谷极化已弛豫"或"谷选择定则被破坏"。这篇文章用 TMD 莫尔超晶格上的层间激子作为模型体系，告诉我们：**零稳态圆偏振完全可能是两条 helicity 相反的发射通道在时间维度上互相补偿的结果，而与谷弛豫速率无关**。

作者用 helicity-resolved 时间分辨 PL 抓到了共圆/交叉圆分量在时间演化中的"交叉（crossing）"行为，这是单一通道模型无法产生的指纹特征。再配合一个最小双通道速率方程（A-like 和 B-like 莫尔通道，光学选择定则相反、衰减/退极化速率不同），就能完整复现观测。最妙的是这个 crossing time 还随门电场系统性移动——说明所谓"隐藏"的通道不仅是动力学上的真实自由度，而且是电学可调的。

对我而言，这等于给所有依赖时间积分圆偏振读出的谷电子学实验（包括我们自己的 valHHG CD 信号）敲了一记警钟：**不做时间分辨，你分不清"补偿"和"弛豫"**。

## 核心要点

- **核心反直觉结论**：莫尔层间激子中近零的稳态圆偏振度 ≠ 快速谷弛豫。它可能是 A-like 与 B-like 两条 helicity 相反的发射通道在时间积分窗口内动态补偿的产物。
- **关键实验证据**：helicity-resolved 时间分辨 PL 显示 σ⁺ 与 σ⁻ 分量的时间轨迹存在交叉——这是双通道共存、相反选择定则、差异衰减的标志性指纹。
- **最小理论模型**：双通道速率方程（两通道光学选择定则相反，各自独立的有效衰减率与退极化率），无需引入"单一快速谷弛豫"即可重现 crossing 现象。
- **电场可调性**：二维门电场–位移场 mapping 表明 crossing time 随静电掺杂/位移场系统性演化，证实这些隐藏通道是物理上可寻址的自由度，而非拟合 artefact。
- **方法学贡献**：把"时间积分圆偏振度"这一领域标准量的解读范式推翻——在多通道谷发射体中它会给出**假阴性（false-negative）**。

## 实验/研究关联

- **与我组 valHHG 工作的直接关联**：
  - 我们组用圆偏 pump + 线偏驱动产生的高次谐波 CD 来表征谷极化弛豫时间。如果驱动–发射过程也存在多通道贡献（例如不同的莫尔位点、不同层间激子态、或偶数次/奇数次谐波的不同选择定则通道），那么"CD 随延迟衰减到零"也可能被误读。
  - 这篇工作给出的教训是：**必须做 helicity-resolved 时间分辨的 CD 扫描**，而不是只看在某个延迟点上的积分 CD 值。我们组现有的时间分辨 CD 数据需要重新审视是否存在 crossing 特征。
- **技术迁移可能**：
  - helicity-resolved TRPL 是稳态测量，做不了 fs/as 时间尺度。但原理可以平移到 pump–probe 型的阿秒 CD 测量：在每条谐波阶次上独立分辨 σ⁺ pump 与 σ⁻ pump 的谐波产量作为延迟函数，看是否存在 crossing。
  - 双通道速率方程模型可以推广为多通道版本，作为我们组解析 valHHG 数据的备选框架。
- **样品体系借鉴**：
  - 该工作使用 hBN 封装 + 双栅极 TMD 莫尔异质结（典型配置，Watanabe/Taniguchi 石墨栅极）。我们组如果要做 valHHG 的电学调控实验，这种器件结构可以直接复用。
- **NSFC-强场超快项目层面**：
  - 论文把"隐藏谷动力学"作为可电学调控的自由度展示，这与我们项目的核心目标（用强场光场调控谷自由度）方向一致。可以作为我们"光场 + 电场联合调控"方案的方法学支撑文献。

## 开放问题

- **通道数与普适性**：最小模型只需要两个通道，但真实莫尔体系里莫尔位点可能有多种（R-type、H-type、AA-like 等），每个位点的层间激子选择定则是否都恰好二分？还是需要三通道甚至连续分布？作者没有排除 N>2 的可能。
- **从 PL 到 HHG 的可移植性**：PL 测的是自发辐射末态的布居，而 HHG 测的是强场驱动下的相干极化–辐射过程。两者的多通道机制是否同源（层间激子本身）？还是 PL 中看到的双通道在 HHG 中会被强场筛选/混合？这是我组应该尽快用实验回答的问题。
- **crossing time 的物理含义**：作者把 crossing time 与有效衰减/退极化速率联系起来，但没有给出与莫尔位点结构、激子–声子耦合、层间耦合强度等微观参数的定量映射。这是连接现象学与微观机制尚缺的桥梁。
- **时间分辨率下限**：TRPL 的时间分辨率受探测器限制，对应的物理过程在亚皮秒–纳秒尺度。如果在 fs/as 尺度做 valHHG，多通道补偿窗口会不会短到根本无法用稳态 CD 看到？也就是说，**这篇工作揭示的假阴性在强场超快实验中是否真的存在，还是被超快时标天然规避了**？这决定了我们对该警示的紧迫程度。
- **电场调控的机制**：门电场改变 crossing time 是通过调谐通道能量（改变相对占据）、还是通过调谐退极化（改变相对速率）？两者在我们自己的 valHHG 实验中对应完全不同的物理图景。
- **与激子–激子湮灭、多体效应的区分**：莫尔体系中高密度激发下双通道也可能被解释为高密度激子–激子相互作用引起的赝象。需要低激发极限下的对照实验来锁定。

## 来源
- 原始材料：2026-260627963-hidden-valley-dynamics-behind-vanishing-circu.md
- 蒸馏时间：2026-09-28T04:50:32Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：helicity 分辨时间分辨 PL 揭示莫尔激子'隐藏谷动力学'（双通道速率方程模型，薄卡）

**原理**：对 hBN 封装 + 双栅 TMD 莫尔异质结的层间激子做 helicity 分辨时间分辨 PL：σ⁺ 与 σ⁻ 分量时间轨迹出现'交叉（crossing）'——这是 A-like 与 B-like 两条光学选择定则相反、衰减/退极化速率不同的发射通道共存的标志性指纹；最小双通道速率方程无需'单一快速谷弛豫'假设即可复现。核心方法学结论：近零的稳态（时间积分）圆偏振度可由两通道时间补偿产生、与谷弛豫速率无关——时间积分 CD 是多通道谷发射体的假阴性代理量；crossing time 随门电场/位移场系统演化，证明隐藏通道电学可寻址。

**适用边界**：摘要级来源薄卡：crossing time 数值、通道衰减率、样品转角/成分等定量参数页面未给出，不虚构；最小模型未排除 N>2 通道可能；PL（自发辐射布居）到 HHG（强场相干极化）的可移植性未验证——fs/as 尺度多通道补偿窗口是否存在是开放问题；crossing time 与莫尔位点/激子-声子耦合等微观参数的定量映射缺失；高密度激子-激子相互作用的赝象可能性需低激发对照排除。
**代表作**：Urano et al. (2026)（arXiv 2606.27963，莫尔激子隐藏谷动力学，蒸馏 2026-09-28）。方法学警示：valley-HHG 圆二色 ≈0 不能解读为谷极化已弛豫——必须做 helicity 分辨时间分辨扫描。
*方法卡回补 2026-09-28*


## 合并自「Hidden valley dynamics behind vanishing circular polarization in moiré excitons」

# Hidden valley dynamics behind vanishing circular polarization in moiré excitons

**arXiv**: [2606.27963](https://arxiv.org/abs/2606.27963) | **方向**: 能谷电子学/moiré激子/TMD异质结（直接对林赛能谷方向）

---

## 研究背景与问题（Background & Research Question）

能谷读出的标准手段是测稳态光致发光的圆偏振度（DCP, $P_v$）。在 moiré 激子里常见到 $P_v \approx 0$，惯常解释是谷快速退极化，但这是基于时间积分测量的推断，从未被时间分辨验证。moiré 体系里不同格点（A-like/B-like）可以有相反光学选择规则，时间积分会给出假阴性。

Urano et al. (2026) 用 helicity-resolved 时间分辨 PL 拆穿了一个被领域默认多年的陷阱：**时间积分圆偏振度接近零 ≠ 谷弛豫快**。作者证明在电学可调的莫尔激子里，存在 A-like 和 B-like 两个 helicity 相反的发射通道，两者在时间演化上发生交叉（crossing），时间积分后互相抵消，呈现为"假阴性"。这条 paper 相当于一把通用的"反陷阱手术刀"：必须做时间分辨 + 门电场二维扫描才能分离通道。

### 直接警示

- 若用 HHG 的圆偏振度（不同谐波阶 $\sigma^+$/$\sigma^-$ 强度比）推断谷极化，且样品有多个响应通道（moiré/不同带/不同谐波机制），同样的相消陷阱会出现。**任何只看 CD 幅值而不分辨时间/能量通道的工作，都存在被假阴性误导的风险**。
- 我们在分析 HHG-CD 衰减时常用一个有效退极化时间 $\tau_v$ 拟合。如果实际是多通道 $\tau_{v,1} \neq \tau_{v,2}$，单 $\tau_v$ 拟合会给出错误物理。这篇 paper 是重审那批数据的方法论依据。

### 与其他工作的互补

- 与 2606.28809 互补：那篇给带间电流散射的理论基石，这篇给谷动力学的实验陷阱。
- 方法学对照：本工作用 TRPL（ns 时间分辨），谷 HHG 用 HHG（fs–as）。两套时间窗互补——PL 看 ns 发射动力学，HHG 看 fs–as 相干电子动力学，能探到共同种群衰减 $\Gamma$ 以下的超快过程。

---

## 研究方法（Methods）

- **螺旋度分辨时间分辨光致发光（helicity-resolved TRPL）**：在双栅控 WSe₂/WS₂（twist angle $0.14 \pm 0.20°$，R-type，4 K）上测时域 $\sigma^+$/$\sigma^-$ 分量。
- **SHG 表征确定近 0°（R-type）堆叠**：heterobilayer 的 SHG 强于单层指建设性干涉，区分近 0°（R-type）与近 60°（H-type）。该 twist angle 和堆叠判据是样品表征的直接参考。
- **最小两通道率方程模型**：明确声明这是唯象拟合，不是微观 A–B 跃迁时间的唯一确定（$t_{\text{cross}}$ 是 emergent helicity-compensation time，不是微观 A–B 跃迁时间，后者发生在 sub-ps 尺度）。
- **栅场二维映射（$t_{\text{cross}}$ vs $V_g$）**：把隐谷动力学的电可调性定量化为 $t_{\text{cross}}$ 的系统性演化。

样品工艺参考：hBN 封装 + 高质量石墨栅极 TMD moiré 异质结——若未来做强场实验，这套工艺路线成熟可复制。

---

## 主要发现与核心结论（Main Results）

### 范式颠覆

在多通道谷发射体（moiré 超晶格、A-like/B-like 共存）中，时间积分圆偏振度可以给出谷极化的**假阴性**。"零偏振"不再等同于"快速谷弛豫"。

### 实验指纹：时域 crossing（核心）

在 $P_v \approx 0$ 的栅压区，$\sigma^-$ 在早延时更强，$\sigma^+$ 在晚延时更强，两 trace 在有限时间 $t_{\text{cross}}$ 交叉。螺旋度差分信号 $D(t) = I_{\sigma^+} - I_{\sigma^-}$ 从负到正反转符号——这是多通道共存、helicity 相反分量动态补偿的直接证据，**任何单一快速弛豫过程都无法解释这种现象**。单一指数退极化曲线 $P(t) \propto \exp(-t/\tau_v)$ 根本无法复现这种符号反转。

### 双通道最小模型

A-like 与 B-like moiré 通道具有**相反光学选择定则** + **不同有效衰减/退极化速率**，即可在速率方程层面重现 helicity crossing，无需引入单一快速弛豫通道：

$$D(t) = \exp(-\Gamma t)\left(D_A \exp(-2\gamma_A t) + D_B \exp(-2\gamma_B t)\right), \quad D_A \cdot D_B < 0$$

$$t_{\text{cross}} = \frac{1}{2(\gamma_A - \gamma_B)} \ln\left(\frac{D_A}{-D_B}\right)$$

共同种群衰减 $\Gamma$，但不同谷退极化率 $\gamma_A, \gamma_B$。

### 电场可调性

二维门电场/位移场映射显示 $t_{\text{cross}}$ 系统性演化——隐藏谷动力学是**电学可控的自由度**，而非样品不可改变的固有属性。有限 $t_{\text{cross}}$ 恰好出现在 $P_v \approx 0$ 区域附近：证明静态极化为零不是无结构的退极化区，而是隐谷动力学最显著的区。

### 关键警示

时间积分圆偏振度在多螺旋度通道共存时会给谷极化的假阴性（false negative）。单稳态 $P_v$ 不足以确定谷弛豫动力学。

---

## 实验/研究关联

### 与谷 HHG 圆二色信号解读的直接关联

我们在 HHG 实验中通常用高次谐波的圆二色性（CD）作为驱动场谷注入与弛豫的探针。如果谐波发射本身也来自多个 helicity 相反的子带/通道贡献，时间积分 CD 同样可能被动态补偿抹平。**time-resolved + gate-field 2D mapping 是分离多通道谷发射体的通用手段**。

### Attosecond 瞬态吸收/反射的启示

如果把 helicity-resolved 时间分辨 PL 换成 helicity-resolved attosecond 瞬态吸收，理论上能在亚周期时间尺度上直接看到两个 helicity 通道的解耦——这是强场手段相对 PL 的天然优势（时间分辨率高得多）。可以做思想实验：在 moiré 超晶格上做 helicity-resolved attosecond 瞬态吸收，看是否能用同样的双通道模型拟合。

### 门电场扫描作为解耦工具

作者展示了 gate-field 2D map 可以系统性调出 crossing time。我们组在强场实验中一般不扫 gate field，但若做 WSe₂/MoS₂ moiré 异质结的 HHG，完全可以把 gate voltage 作为独立维度，验证 HHG-CD 是否也呈现类似的"通道解耦-补偿"行为。moiré 激子的 A/B 通道有相反选择规则 + 电可调，本身就是用栅压调控能谷对强场响应的平台。若用栅压扫描把系统调到 $P_v \approx 0$ 的隐谷区，可看 HHG 谱是否对隐藏的螺旋度动力学敏感。

### moiré 作为谷-HHG 平台的启示

moiré 激子的 A/B 通道有相反选择规则 + 电可调，这本身就是用栅压调控能谷对强场响应的平台。

---

## 潜在方向与开放问题（Future Directions & Open Questions）

### 具体未来方向

- **TRPL 扩展到磁场下**（Zeeman 分裂 K/K'）：看 $t_{\text{cross}}$ 如何随谷分裂演化，能把 A/B 通道的谷退极化率分开。
- **不同 twist angle/堆叠（H-type）下重复**：验证 A/B 选择规则反转是否是普适机制。
- **时间分辨圆偏振 HHG**：用 HHG 而非 PL 读谷动力学——HHG 是相干过程，能访问 PL 探不到的超快（fs–as）谷动力学，直接指向 valley-HHG 方向。
- **理论推广**：把两通道模型推广到 N 通道 + 相干耦合，看 crossing 是否是 generic feature，以及与 A–B 位间相干隧道的关系。

### 开放问题

- **多通道是否在所有 TMD moiré 体系中普遍存在？** A-like/B-like 命名暗示作者已识别两个具体通道，但通道数是否可能 >2？三通道或连续通道分布下，单一 crossing time 的概念是否还成立？
- **强场驱动下通道布居是否会重整？** 在强光场（HHG 所需 ~10¹³ W/cm² 量级）下，A-like 和 B-like 通道的相对布居、衰减率、selection rule 是否仍然和弱场 PL 测量一致？场致通道耦合是 open question。
- **helicity crossing 是否就是 CD 假阴性的唯一指纹？** 是否存在其他多通道构型在时间积分下产生零偏振但不出现明显 crossing（例如衰减率差异巨大、但稳态权重互补）？
- **gate-tunable crossing time 的微观机制**：是位移场直接调控两个通道的振幅权重，还是通过改变层间激子波函数重叠从而改变有效衰减率？需要更微观的角度（DFT + 紧束缚 + 速率方程联合）。
- **强场超快实验的时间分辨率优势能否反过来"证明"该假阴性？** 可以做 helicity-resolved sub-cycle 测量，看 HHG-CD 在 attosecond 时间尺度上是否也呈现 crossing——这是对该 paper 结论的最直接强场验证。

---

## 来源

- [arXiv 2606.27963](https://arxiv.org/abs/2606.27963)
- 原始材料：`2026-260627963-hidden-valley-dynamics-behind-vanishing-circu.md`
- 导入自 hermes 深度分析（2026-08-08T16:23:45Z）
- 蒸馏时间：2026-08-31T04:50:08Z

---

## 关联概念

- [[多通道谷发射补偿假象]]
- [[时间分辨helicity-resolved测量]]
- [[谷HHG圆二色信号解读]]
- [[速率方程双通道模型]]
- [[门电场可调moiré超晶格]]


## 深度解析

### 研究问题（Research Question）

Gap: 能谷读出的标准手段是测稳态光致发光的圆偏振度(DCP, Pv). 在moire激子里常见到Pv约等于0, 惯常解释是谷快速退极化, 但这是基于时间积分测量的推断, 从未被时间分辨验证. moire体系里不同格点(A-like/B-like)可以有相反光学选择规则, 时间积分会给出假阴性. 贡献: 用螺旋度分辨TRPL证明Pv约等于0的稳态谷极化背后隐藏着明确的时域螺旋度动力学: co/cross圆偏振分量在时域发生crossing(符号反转), 时间积分的相消制造了无极化的假象.

### 研究背景（Background）

最直接警示: 你的能谷HHG实验不能用时间积分圆偏振度判读. 这篇核心结论: 多螺旋度通道共存时时间积分会造假阴性. 直接警告: 若你用HHG的圆偏振度(不同谐波阶sigma+/sigma-强度比)推断谷极化, 且样品有多个响应通道(moire/不同带/不同谐波机制), 同样相消陷阱会出现. 探测方案必须时间分辨或通道分辨. moire作为谷-HHG平台的启示: moire激子的A/B通道有相反选择规则+电可调, 这本身就是用栅压调控能谷对强场响应的平台. 你的valley-HHG若在moire TMD上做, 可用栅压扫描把系统调到Pv约等于0的隐谷区, 看HHG谱是否对隐藏的螺旋度动力学敏感. twist angle 0.14度的参考: 近对齐R-type WSe2/WS2是moire激子标准平台, 这个twist angle和堆叠判据(SHG建设性干涉)是样品表征的直接参考. 方法学对照: 他们用TRPL(ns时间分辨), 你用HHG(fs-as). 两套时间窗互补: PL看ns发射动力学, HHG看fs-as相干电子动力学. 你的实验能探到他们模型里共同种群衰减Gamma以下的超快过程. 与2606.28809互补: 那篇给带间电流散射的理论基石, 这篇给谷动力学的实验陷阱.

### 研究方法（Methods）

- 螺旋度分辨时间分辨光致发光(helicity-resolved TRPL): 在双栅控WSe2/WS2(twist angle 0.14+-0.20度, R-type, 4K)上测时域sigma+/sigma-分量.
- SHG表征确定近0度(R-type)堆叠: heterobilayer的SHG强于单层指建设性干涉, 区分近0度(R-type)与近60度(H-type).
- 最小两通道率方程模型: 明确声明这是唯象拟合, 不是微观A-B跃迁时间的唯一确定(tcross是emergent helicity-compensation time, 不是微观A-B跃迁时间, 后者发生在sub-ps尺度).
- 栅场二维映射(tcross vs Vg): 把隐谷动力学的电可调性定量化为tcross的系统性演化.

### 主要发现与核心结论（Main Results）

- 时域crossing(核心): 在Pv约等于0的栅压区, sigma-在早延时更强, sigma+在晚延时更强, 两trace在有限时间tcross交叉. 螺旋度差分信号D(t)=Isigma+(-)Isigma-从负到正反转符号: 单一指数退极化曲线P(t)正比于exp(-t/tauv)根本无法复现这种符号反转.
- 两通道唯象模型: A-like/B-like moire发射通道有相反圆偏振选择规则+不同有效弛豫率. D(t)=exp(-Gamma*t)(DA*exp(-2*gammaA*t)+DB*exp(-2*gammaB*t)), DA*DB<0, tcross=[1/(2(gammaA-gammaB))]*ln(DA/-DB). 共同种群衰减Gamma, 但不同谷退极化率gammaA, gammaB.
- 电可调性: tcross随栅场系统演化; 有限tcross恰好出现在Pv约等于0区域附近: 证明静态极化为零不是无结构的退极化区, 而是隐谷动力学最显著的区.
- 关键警示: 时间积分圆偏振度在多螺旋度通道共存时会给谷极化的假阴性(false negative). 单稳态Pv不足以确定谷弛豫动力学.

### 潜在研究方向（Future Directions）

- TRPL扩展到磁场下(Zeeman分裂K/K-prime): 看tcross如何随谷分裂演化, 能把A/B通道的谷退极化率分开.
- moire不同twist angle/堆叠(H-type)下重复: 验证A/B选择规则反转是否是普适机制.
- 时间分辨圆偏振HHG: 用HHG而非PL读谷动力学: HHG是相干过程, 能访问PL探不到的超快(fs-as)谷动力学, 直接指向valley-HHG方向.
- 理论把两通道模型推广到N通道+相干耦合: 看crossing是否是generic feature, 以及与A-B位间相干隧道的关系.

### 来源

- [arXiv 2606.27963](https://arxiv.org/abs/2606.27963)
- 导入自 hermes 深度分析（2026-09-06T04:40:17Z）

<!-- methods-backfill:v1 -->

## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：螺旋度分辨时间分辨 PL（helicity-resolved TRPL）+ 双通道率方程 + 栅场二维扫描：拆穿 moiré 激子圆偏振'假阴性'（WSe₂/WS₂）

**原理**：时间积分圆偏振度 P_v≈0 习惯性解读为谷快速退极化，但这是时间积分测量的推断——moiré 体系中 A-like/B-like 格点可携带相反光学选择定则，两个 helicity 相反的发射通道在时间演化上交叉（crossing），积分后互相抵消呈现假阴性。方法：helicity-resolved TRPL 在双栅控 WSe₂/WS₂ 上分辨时域 σ⁺/σ⁻ 分量；SHG 强度对比（异质双层强于单层=建设性干涉）判定近 0° R-type 堆叠；最小两通道率方程唯象拟合（明确声明 t_cross 是 emergent helicity-compensation time，非微观 A→B 跃迁时间——后者在 sub-ps 尺度）；栅场二维映射把隐谷动力学的电可调性定量化为 t_cross(V_g) 系统演化。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 样品/测量 | 双栅控 WSe₂/WS₂（twist angle 0.14±0.20°，R-type，4 K）；hBN 封装+高质量石墨栅极；时域 σ⁺/σ⁻ 分量分辨 | 研究方法 |
| 堆叠判据 | SHG：异质双层强于单层=建设性干涉（近 0° R-type）；弱于=近 60° H-type | 研究方法·SHG 表征 |
| 模型口径 | 最小两通道率方程=唯象拟合；t_cross 为 emergent 补偿时间（非微观跃迁时间） | 研究方法·最小两通道率方程模型 |

**适用边界**：两通道率方程为唯象拟合（非微观 A-B 跃迁动力学的唯一确定）；TRPL 时间窗为 ns 量级（sub-ps 的微观 A→B 跃迁在其分辨之外，需与 HHG/as 手段互补）；4 K 低温测量（室温行为未验）；单一 twist angle 样品（0.14°）。
**代表作**：Urano/Chouhan/…/Kitaura arXiv:2606.27963 (2026)；互补理论 2606.28809（带间电流散射）
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[2026-260627963-hidden-valley-dynamics-behind-vanishing-circu]]
- [[Hidden valley dynamics behind vanishing circular polarization in moiré excitons]]
- [[TMD异质结]]
- [[圆二色性]]
- [[多通道谷发射补偿假象]]
- [[层间激子动力学]]
- [[层间耦合]]
- [[强场超快]]
- [[强场超快光学]]
- [[强场驱动]]
- [[时间分辨helicity-resolved测量]]
- [[能谷电子学]]
- [[莫尔超晶格]]
- [[谷HHG圆二色信号解读]]
- [[谷极化]]
- [[谷极化假阴性]]
- [[谷高次谐波产生]]
- [[速率方程双通道模型]]
- [[门电场可调moiré超晶格]]
- [[门电场可调莫尔超晶格]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
