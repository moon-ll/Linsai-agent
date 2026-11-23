---
title: "2026-2407_19609-attosecond-transient-grating-spectroscopy-with-nea"
type: "papers"
created: "2026-08-29T17:36:56Z"
updated: "2026-11-15T15:09:21Z"
tags: ["深度解析", "高次谐波", "阿秒科学"]
related: ["Attosecond transient grating spectroscopy with near-infrared grating pulses and an extreme ultraviolet diffracted probe", "固体HHG", "固体高次谐波", "强场驱动", "电荷密度波", "相干声子", "瞬态吸收光谱", "谷极化", "量子几何", "量子度规", "阿秒瞬态吸收", "阿秒科学", "高次谐波产生"]
source_raw: "2026-2407.19609-attosecond-transient-grating-spectroscopy-with-nea.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-25T15:42:08Z"
merged_from: ["wiki/papers/2407.19609.md"]
---

# Attosecond Transient Grating Spectroscopy with Near-Infrared Grating Pulses and an Extreme Ultraviolet Diffracted Probe

## 林赛的理解

这篇工作将瞬态光栅光谱（TGS）推向了阿秒量级——通过 HHG 产生的 XUV 阿秒脉冲探测由 sub-5 fs NIR 脉冲构建的瞬态光栅。我在强场驱动和 HHG 方面的积累使我能够理解其核心：NIR 500-1000 nm 少周期脉冲既驱动 HHG 产生 XUV，又是光栅写入光束。这种双功能设计是关键技术突破口。对我们的研究而言，ATGS 提供了 TAS 之外的选择——它能提取折射率变化 Δn，从而将吸收（ absorptive）和色散（dispersive）过程分离，这在研究载流子-声子相互作用时极具价值。特别值得关注的是该技术同时获取 ATAS 和 ATGS 来反解复介电函数的思路，以及利用交叉偏振 NIR 束产生自旋光栅的建议——这直接关联到我们关注的自旋密度波和量子材料中的自旋动力学。

## 研究问题（Research Question）
如何将瞬态光栅光谱（TGS）扩展至阿秒时间尺度，实现元素选择性的、无背景噪声的 ultrafast 动力学探测？具体而言：(1) 能否用 tabletop HHG 产生的 XUV 阿秒脉冲作为探针，探测由 sub-5 fs NIR 少周期脉冲构建的瞬态光栅？(2) 能否从同时获取的 ATAS 和 ATGS 数据中提取折射率变化 Δn，从而获得包括实值折射率在内的完整复介电函数？(3) 该技术能否应用于 Sb 半金属中的 ultrafast 光致动力学，解析载流子热化、冷却、复合及声子 dynamics？

## 研究背景（Background）
**学术脉络**：TGS 是四波混频非线性光谱的一种，通过两束非共线泵浦光在样品中产生瞬态光栅，探针光从光栅衍射。TGS 能同时探测吸收（幅度光栅）和折射率变化（相位光栅），其信号为两者之和（见公式）。相比 TAS 和 TRS 仅分别跟踪吸收或折射率动力学，TGS 包含更多信息，已广泛应用于金属/半导体的光载流子动力学、激子、超导准粒子、声子、自旋、磁化、电荷密度波、晶格应变和表面声波等研究。

**前人工作**：FEL 设施上的 XUV pump–XUV probe TGS 已用于纳米尺度载流子扩散研究，但因 FEL 脉冲宽度限制，时间分辨率仅 40-70 fs。Tabletop XUV TGS 虽有演示，但分辨率也在数百 fs 量级。阿秒研究虽已阐明相干声子、载流子热化、芯激子等现象，但主要局限于 TAS。TAS 存在光谱拥堵（spectral congestion）问题，且难以同时分离电子和空穴动力学。

**研究动机**：将阿秒方法论扩展至非线性非共线测量方案，可带来更高的信噪比、无背景的数据采集、免于光谱拥堵，以及超越 TAS 极限的更丰富数据集。

## 研究方法（Methods）
**数据来源**：Tabletop 实验，UC Berkeley。

**实验装置（详见 Fig. 1a）**：
- **泵浦光**：Ti:sapphire 激光器（Coherent Astrella，1 kHz，7 mJ/pulse，35 fs，32 nm 带宽）→ 3 mJ 聚焦至 2.2 m 空心光纤（Ar 气，气压梯度 5 Torr→120 mTorr）产生 500–1000 nm 超连续谱 → 8 对双角宽带啁啾镜 + 熔融石英楔 + KDP 楔压缩至 ~5 fs → 90:10 分束 → 50:50 分束产生两束 NIR 泵浦臂 → 非共线聚焦至样品（θ=36 mrad 角度偏移，f=1 m 银凹面镜）。
- **探针光**：前述 NIR 光的一部分（较大功率束）进入 Kr 气室（~15 Torr）通过 HHG 产生 XUV 脉冲（25-45 eV）→ 100 nm Al 箔滤除 NIR → 金涂层环面镜聚焦至样品。
- **探测**：XUV 经金涂层平场光栅（Hitachi 01-0639）色散 → XUV CCD（Princeton Instruments Pixis XO 400-B）探测。CCD 置于双轴位移台上以同时获取 ATAS 和 ATGS 信号。
- **时延控制**：压电陶瓷台（Physik Instrumente P-620.1CD）+步进电机台（Physik Instrumente M-505-6DG）控制 XUV 探针相对 NIR 泵浦的延迟。

**材料体系**：30 nm 多晶 Sb 薄膜，蒸发于 30 nm Si₃N₄ 膜（Norcada NX5050X）上。NIR 泵浦强度 7.9 mJ/cm²（考虑 Sb 表面反射约 75% 后估算入射通量为 7.5 mJ/cm²）。NIR-XUV 偏移角 36 mrad，对应光栅周期约 11 μm（Λ = λIR/(2 sin(θ/2))）。

**关键方法**：
- **SVD（奇异值分解）**：分析 ATAS 和 ATGS 数据，分解出 lattice 和 carrier 主导的分量。
- **同时 ATAS + ATGS 采集**：由 ATAS 得幅度光栅效率 ηAMP = (Δk·d)²/(4α)，由 ATGS 得总光栅效率 ηTOTAL = TG(λ)/S₀(λ)，进而通过 ηPHA = ηTOTAL - ηAMP 和 Δn(λ,t) = [ηTOTAL(λ,t) - ηAMP(λ,t)]·λ/(4πd) 提取折射率变化 Δn。
- 时间零点通过拟合 Ar 3s3p6np 自电离信号的上升沿确定（指数修正高斯函数拟合）。

## 主要发现与核心结论

**Sb 中的 ultrafast 动力学时域分解**（Table ST1 及 Fig. 3, 4）：

| 过程 | 时间常数 |
|------|---------|
| A₁g 声子频率 | 4.13±0.02 THz |
| 相干声子振荡衰减 | 540±50 fs |
| 载流子热化（上升） | 16±4 fs |
| 热载流子冷却（衰减） | 45±8 fs |
| 电子-空穴复合 | 2.07±0.04 ps |

**折射率变化 Δn 的 SVD 分析**（Fig. 4d-f）：
- **N₁**：长寿命过程，单指数衰减 ~30 ps（可能为双指数），归因于载流子-声子和声子-声子动力学（热扩散），因光栅周期大于载流子和声子的平均自由程而无法确定其扩散寿命。
- **N₂**：衰减时间常数 1.3±0.3 ps，归因于晶格动力学。
- **N₃**：衰减时间 720±140 fs，归因于载流子动力学。

**ATGS vs ATAS 的关键差异**：
- ATAS 数据因自旋-轨道分裂的 4d5/2 和 4d3/2 芯能级跃迁而呈现光谱拥堵的重叠特征；ATGS 谱图更简洁，仅包含正信号，两个自旋轨道分量清晰分离。
- ATGS 信号实际上是 ATAS 数据的平方——ATGS 第一个 SVD 分量正比于 C₁×C₁，第二个正比于 C₁×C₂，其中 C₁ 和 C₂ 分别为 ATAS 的晶格和载流子 SVD 分量。
- 在早期时间延迟，ATGS 与 ATAS 平方积吻合良好；在较长时间延迟出现偏差——该偏差来源于折射率变化 Δn（相位光栅贡献）。

**技术验证结论**：ATGS 在 few-fs 尺度主要由吸收效应主导；在较长时间尺度需考虑 Δn 贡献。同时获取 ATAS 和 ATGS 可提取完整的复介电函数，包括实值折射率，提供比单独 TAS 更丰富的关于非吸收过程（如晶格和热动力学）的信息。

## 潜在研究方向（Future Directions）
**技术层面**：
1. **反射模式单晶样品**：现有研究受限于透射模式的多晶薄膜，纳米晶粒尺寸限制声子扩散寿命测量。未来应在单晶样品上进行反射模式 ATGS 以提取声子扩散寿命。
2. **外差检测（heterodyne setup）**：引入共传播且有固定延迟偏移的 XUV 参考光以分离幅度和相位光栅信息，更明确地区分吸收和色散过程。但 XUV 光束间亚光学周期量级的延迟控制是重大挑战。
3. **结合 FEL 优势**：将 ATGS 的时间分辨率和光谱带宽与 FEL 的高通量结合，在 ns 量级光栅周期下测量弛豫和热化前的电荷动力学与扩散长度。

**物理研究层面**：
1. **芯激子动力学**：ATGS 的亚 20 fs 时间分辨率可用于研究 fs-TGS 无法访问的芯激子动力学过程。
2. **元素选择性信息**：宽带 XUV 脉冲提供元素选择性数据，可处理为分别获得电子和空穴动力学及扩散信息。
3. **自旋光栅**：采用交叉偏振 NIR 束产生自旋光栅，可实现自旋动力学和扩散的阿秒时间分辨研究，应用于自旋密度波、自旋缺陷及自旋扩散、转移、弛豫等。

**理论层面**：
1. N₁ 长寿命成分的精确衰减模型——单指数 vs 双指数之争需要在更长扫描时间窗口中验证。
2. Sb 的电子-空穴复合机制（L 点导带底电子与 T 点价带顶空穴的复合，通过发射一个声子和两个 X 点光学声子进行）的声子模式细节尚需进一步理论分析。

## 与林赛研究的关联

**HHG 与强场驱动**：该工作是我们强场驱动 HHG 产生 XUV 技术的直接应用——NIR 少周期脉冲既通过 HHG 产生 XUV 探针，又作为瞬态光栅写入光束。这种"一束两用"的设计与我们长期积累的 HHG 知识直接对接。

**阿秒科学**：ATGS 提供了一种不同于 TAS 的阿秒探测手段——它不依赖吸收而是依赖衍射，因此避免了光谱拥堵问题，且能提取 Δn。这意味着我们可以同时获得吸收（ATAS）和折射率（ATGS）信息，这对理解量子材料的电子结构和晶格耦合至关重要。

**Sb 和 Peierls 畸变**：Sb 是经典的光致 Peierls 畸变体系，相干声子（A₁g 模式）通过位移激发（DECP）机制产生。该研究深化了我们对强场驱动下晶格动力学和载流子-声子相互作用的理解。

**交变磁与自旋密度波**：作者明确提出用交叉偏振 NIR 束产生自旋光栅的建议，这直接关联到交变磁和自旋密度波的研究。这为在我们关注的量子材料体系中探测自旋动力学提供了一条新途径。

**莫尔与量子几何**：虽然本文未直接涉及莫尔体系，但 ATGS 对折射率变化 Δn 的敏感性与量子几何（quantum geometry）中的贝里曲率和量子度规相关联。未来可将 ATGS 扩展至莫尔系统，研究其中的载流子-声子耦合和量子几何效应。

## 来源

- 蒸馏自全文（deep-read）
- arXiv: 2407.19609
- 作者: Rafael Quintero-Bermudez, Lorenz Drescher, Vincent Eggers, Kevin Gulu Xiong, Stephen R. Leone（UC Berkeley）


## 合并自「Attosecond transient grating spectroscopy with near-infrared grating pulses and an extreme ultraviolet diffracted probe」

# Attosecond transient grating spectroscopy with near-infrared grating pulses and an extreme ultraviolet diffracted probe

**arXiv**: [2407.19609](https://arxiv.org/abs/2407.19609) | **方向**: 阿秒科学

---

## 为什么值得关注

首次实现阿秒瞬态光栅光谱（ATGS），将瞬态光栅技术的时间分辨率推至阿秒尺度。相比传统瞬态吸收光谱（ATAS），ATGS 提供无背景、无光谱拥堵的信号，且能同时获取振幅和相位信息，完整提取复介电常数。这对理解固体中载流子和晶格动力学提供了更丰富的信息维度。

## 研究问题（Research Question）

瞬态光栅光谱（TGS）在金属/半导体研究中已成熟，但受脉冲宽度限制，FEL 的 XUV-XUV TGS 时间分辨只到 40–70 fs，桌面 XUV TGS 仅 100 fs 量级；阿秒时间分辨只能通过瞬态吸收（ATAS）实现，但 ATAS 谱线拥挤、无背景抑制能力。本工作首次实现具有阿秒分辨率的瞬态光栅光谱（ATGS）：用两束亚 5 fs 的 NIR 泵浦写入光栅，HHG 产生的 25–45 eV 阿秒 XUV 探针衍射，并同时采集 ATAS+ATGS 以提取复介电函数（Δn + Δk），把阿秒光谱的能力从纯吸收推进到振幅+相位全信息测量。

## 研究背景（Background）

本工作硬件栈与林赛实验平台几乎一致——Coherent Astrella 800 nm Ti:Sa + 中空芯光纤超连续 + Kr 气 HHG + XUV CCD 是阿秒实验室的标准桌面配置；迁移到林赛 800 nm 平台是直接的，无供应链障碍。ZnO（林赛核心材料）的 Zn L 边（~1022 eV）目前在桌面 HHG 难以达到，但 O K 边（~530 eV）和 Zn M 边（~10–90 eV）正好落在 25–45 eV ATGS 谱窗附近——可以直接测 ZnO 价带电子-空穴复合、激子动力学、声子耦合，与林赛已有的 ZnO HHG 数据形成强互补。对 TMD（MoS₂、WSe₂）：Mo N 边（~30–70 eV）和 W 4f（~35–45 eV）也落在 25–45 eV ATGS 窗口，可同步提取谷极化动力学与晶格振动，是 ATAS 谱拥挤时唯一可行的元素选择性路线。关键参数参考：NIR 泵浦 ~7.9 mJ/cm²，光栅周期 11 µm，Sb 上得到 16 fs 热化与 540 fs 声子衰减——这些时间尺度与 TMD 激子-声子耦合（50–500 fs）和 ZnO 自由载流子复合（ps 级）量级匹配。结论：方法完全可迁移，建议优先在 ZnO 上演示 ATGS（无需新建 HHG），随后在 WSe₂ 单层上测自旋/谷扩散。

### 与林赛研究的关联与建议

- 与阿秒瞬态吸收光谱（ATAS）直接相关：ATGS 是 ATAS 的扩展，提供额外的相位信息，现有或将来的 ATAS 实验可以整合 ATGS 测量。
- 复介电常数提取：阿秒光谱中的复介电常数是关键，本文提供了从 ATAS+ATGS 联合提取的完整方法。
- 载流子-声子耦合：固体 HHG 研究中载流子散射退相干是关键，ATGS 能直接测量载流子-声子相互作用时间尺度（20–50 fs）。
- 时间分辨率：亚 5 fs 泵浦 + 阿秒探针，足以分辨固体 HHG 中的超快电子动力学。
- 数据分析：SVD 方法可迁移到固体 HHG 数据分析，分离不同动力学通道。
- 建议：考虑在现有系统中加入第二束 NIR 泵浦，实现 ATGS 测量，提供额外相位信息，更完整地理解载流子动力学。

## 研究方法（Methods）

- **ATGS 实验配置**：Coherent Astrella Ti:Sa（1 kHz, 7 mJ, 35 fs）→ 3 mJ 注入 2.2 m 中空芯光纤（内径 700 µm，Ar 压力梯度 5 Torr→120 mTorr）产生 500–1000 nm 超连续；8 对 PC1332 啁啾镜 + SiO₂ 楔 + KDP 楔压缩到 ~5 fs；90:10 分束，强部分入 200 µm Kr 气室（~15 Torr）HHG 产生 25–45 eV XUV；弱部分再 50:50 分成两束非共线泵浦。
- **时间零点校准**：使用 Ar 3s3p6np 自电离信号拟合，确定泵浦-探针重叠。
- **同步 ATAS+ATGS 采集**：XUV CCD（Pixis XO 400-B）同时记录零级（共线 ATAS）和 ±1 级（离轴 ATGS）衍射——一次曝光即获得 Δk 与 Δn 的互补信息。
- **SVD 分解 + DECP 模型拟合**：将 ATAS/ATGS 二维时-能谱奇异值分解，分离晶格和载流子动力学分量，分量按 ATAS² / ATAS×ATAS 关系映射到 ATGS 分量，再分别用 DECP 模型（A1g 振荡 + 指数衰减）拟合，提取热化/冷却/复合时间常数。
- **相位-振幅光栅分离公式**：η_PHA = η_TOTAL - η_AMP；Δn(λ)=λ·(η_TOTAL(λ)-η_AMP(λ))^(1/2)/(d·α(λ)^(1/2))，从一次测量提取复折射率全谱动态。

## 主要发现与核心结论（Main Results）

- **首次演示桌面 ATGS**：两束非共线亚 5 fs 500–1000 nm NIR 泵浦（θ=36 mrad 偏角，光栅周期 ~11 µm）写入瞬态光栅，HHG 产生 25–45 eV 阿秒 XUV 探针，在 30 nm 多晶 Sb 薄膜（Si₃N₄ 衬底）上观测到清晰的离轴衍射信号。
- **提取 Sb 全部超快载流子与晶格动力学常数**：载流子热化 16±4 fs、热载流子冷却 45±8 fs、电子-空穴复合 2.07±0.04 ps；A1g 相干声子频率 4.13±0.02 THz，振荡衰减 540±50 fs，符合 Peierls 失稳 DECP 模型。
- **元素选择性与背景抑制优势**：ATGS 信号在 Sb N₄,₅ 边（4d₅/₂, 4d₃/₂ 自旋轨道分裂能


## 深度解析

### 研究问题（Research Question）

瞬态光栅光谱（TGS）在金属/半导体研究中已成熟，但受脉冲宽度限制，FEL 的 XUV-XUV TGS 时间分辨只到 40–70 fs，桌面 XUV TGS 仅 100 fs 量级；阿秒时间分辨只能通过瞬态吸收（ATAS）实现，但 ATAS 谱线拥挤、无背景抑制能力。本工作首次实现具有阿秒分辨率的瞬态光栅光谱（ATGS）：用两束亚 5 fs 的 NIR 泵浦写入光栅，HHG 产生的 25–45 eV 阿秒 XUV 探针衍射，并同时采集 ATAS+ATGS 以提取复介电函数（Δn + Δk），把阿秒光谱的能力从纯吸收推进到振幅+相位全信息测量。

### 研究背景（Background）

本工作硬件栈与林赛实验平台几乎一致——Coherent Astrella 800 nm Ti:Sa + 中空芯光纤超连续 + Kr 气 HHG + XUV CCD 是阿秒实验室的标准桌面配置；迁移到林赛 800 nm 平台是直接的，无供应链障碍。ZnO（林赛核心材料）的 Zn L 边（~1022 eV）目前在桌面 HHG 难以达到，但 O K 边（~530 eV）和 Zn M 边（~10–90 eV）正好落在 25–45 eV ATGS 谱窗附近——可以直接测 ZnO 价带电子-空穴复合、激子动力学、声子耦合，与林赛已有的 ZnO HHG 数据形成强互补。对 TMD（MoS₂、WSe₂）：Mo N 边（~30–70 eV）和 W 4f（~35–45 eV）也落在 25–45 eV ATGS 窗口，可同步提取谷极化动力学与晶格振动，是 ATAS 谱拥挤时唯一可行的元素选择性路线。关键参数参考：NIR 泵浦 ~7.9 mJ/cm²，光栅周期 11 µm，Sb 上得到 16 fs 热化与 540 fs 声子衰减——这些时间尺度与 TMD 激子-声子耦合（50–500 fs）和 ZnO 自由载流子复合（ps 级）量级匹配。结论：方法完全可迁移，建议优先在 ZnO 上演示 ATGS（无需新建 HHG），随后在 WSe₂ 单层上测自旋/谷扩散。

### 研究方法（Methods）

- ATGS 实验配置：Coherent Astrella Ti:Sa（1 kHz, 7 mJ, 35 fs）→ 3 mJ 注入 2.2 m 中空芯光纤（内径 700 µm，Ar 压力梯度 5 Torr→120 mTorr）产生 500–1000 nm 超连续；8 对 PC1332 啁啾镜 + SiO₂ 楔 + KDP 楔压缩到 ~5 fs；90:10 分束，强部分入 200 µm Kr 气室（~15 Torr）HHG 产生 25–45 eV XUV；弱部分再 50:50 分成两束非共线泵浦。
- 同步 ATAS+ATGS 采集：XUV CCD（Pixis XO 400-B）同时记录零级（共线 ATAS）和±1 级（离轴 ATGS）衍射——一次曝光即获得 Δk 与 Δn 的互补信息。
- SVD 分解 + DECP 模型拟合：将 ATAS/ATGS 二维时-能谱奇异值分解，分量按 ATAS² / ATAS×ATAS 关系映射到 ATGS 分量，再分别用 DECP 模型（A1g 振荡 + 指数衰减）拟合，提取热化/冷却/复合时间常数。
- 相位-振幅光栅分离公式：η_PHA = η_TOTAL - η_AMP；Δn(λ)=λ·(η_TOTAL(λ)-η_AMP(λ))^(1/2)/(d·α(λ)^(1/2))，从一次测量提取复折射率全谱动态。

### 主要发现与核心结论（Main Results）

- 首次演示桌面 ATGS：两束非共线亚 5 fs 500–1000 nm NIR 泵浦（θ=36 mrad 偏角，光栅周期 ~11 µm）写入瞬态光栅，HHG 产生 25–45 eV 阿秒 XUV 探针经 Kr 气产生，在 30 nm 多晶 Sb 薄膜（Si₃N₄ 衬底）上观测到清晰的离轴衍射信号。
- 提取 Sb 全部超快载流子与晶格动力学常数：载流子热化 16±4 fs、热载流子冷却 45±8 fs、电子-空穴复合 2.07±0.04 ps；A1g 相干声子频率 4.13±0.02 THz，振荡衰减 540±50 fs，符合 Peierls 失稳 DECP 模型。
- ATGS 信号在 Sb N₄,₅ 边（4d₅/₂, 4d₃/₂ 自旋轨道分裂能级）区呈现「纯正、清晰可辨」特征，而 ATAS 中两条谱线严重重叠拥挤；ATGS 提供了背景抑制、谱去卷积的元素选择性优势。
- ATGS 与 ATAS 联合测量首次同步提取瞬时折射率变化 Δn(t)：从 ATGS 总效率中减去由 ATAS 推算的振幅光栅效率 η_AMP，得到相位光栅 η_PHA，进而 Δn=λ·(η_TOTAL-η_AMP)^(1/2)/(d·α^(1/2))；在 Δn 的 SVD 分解中观察到 ATAS 不可见的长寿命（~30 ps）扩散分量 N1，归因于载流子-声子、声子-声子热扩散。
- ATGS 数据满足 D = Σ_i C_i·C_j（ATAS SVD 分量的乘积）的平方关系，理论预言在短延迟严格成立；偏差出现在长延迟，正是 Δn 相位光栅贡献的体现，证明 ATGS 不是 ATAS 的简单冗余而是其互补。
- 泵浦强度 7.9 mJ/cm²，NIR-XUV 偏角 36 mrad；样品 30 nm Sb 在 30 nm Si₃N₄ 上，每 5 分钟移动样品点以避免累积损伤。

### 潜在研究方向（Future Directions）

- 把 ATGS 迁移到 TMD 单层（MoS₂、WSe₂）与 ZnO：元素选择性可在过渡金属 M 边或 Zn L 边探测，谷/层间动力学可同时从 Δk 和 Δn 提取，是 ATAS 难以分离的。
- 采用反射式 ATGS 在单晶样品上提取声子扩散寿命（目前因 11 µm 光栅周期大于载流子平均自由程、多晶晶粒受限而无法定量）。
- 用交叉偏振 NIR 写入自旋光栅，在自旋密度波、自旋缺陷、自旋扩散体系上实现阿秒自旋动力学 ATGS。
- 外差 ATGS：用同向延迟 XUV 参考光分离纯振幅/纯相位光栅，进一步隔离吸收与色散分量（要求亚光学周期延迟稳定，对 XUV 是工程挑战）。
- 结合 FEL 通量与桌面 ATGS 时间分辨：HHG 通量提升后写入纳米尺度 XUV 光栅，测热化前的电荷动力学与扩散长度。

### 来源

- [arXiv 2407.19609](https://arxiv.org/abs/2407.19609)
- 导入自 hermes 深度分析（2026-08-17T05:13:30Z）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：阿秒瞬态光栅光谱学（ATGS：XUV 探针 + NIR 双泵非共线光栅 + 双轴位移台同时测 ATAS/ATGS）

**原理**：NIR 双泵臂（θ=36 mrad 非共线→光栅周期 Λ≈11 µm）+ XUV 探针（25–45 eV Kr HHG→100 nm Al 滤波→环形镜聚焦）作用于 30 nm 多晶 Sb 薄膜（30 nm Si₃N₄ 上），XUV 经平场光栅色散由双轴位移台上的 CCD 同时获取 ATAS 与 ATGS 信号——首次同时测量的阿秒瞬态光栅光谱学（NIR 泵浦 7.9 mJ/cm²）。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 泵浦 | Ti:Sa 1 kHz/7 mJ/35 fs→HCF 5 Torr–120 mTorr→8 对啁啾镜+楔+KDP 楔→~5 fs；NIR 7.9 mJ/cm²；θ=36 mrad→Λ≈11 µm | §实验装置 |
| XUV 探针 | Kr ~15 Torr HHG；25–45 eV；100 nm Al 滤波；Hitachi 01-0639 平场光栅+Pixis XO 400-B CCD | §实验装置 |
| 样品 | 30 nm 多晶 Sb / 30 nm Si₃N₄（Norcada NX5050X） | §材料体系 |

**适用边界**：页面提取限装置方法（ATGS 信号解译在结果）；页面提取不完整处不虚构。
**代表作**：本文（arXiv:2407.19609）；平台：UC Berkeley tabletop
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[Attosecond transient grating spectroscopy with near-infrared grating pulses and an extreme ultraviolet diffracted probe]]
- [[固体HHG]]
- [[固体高次谐波]]
- [[强场驱动]]
- [[电荷密度波]]
- [[相干声子]]
- [[瞬态吸收光谱]]
- [[谷极化]]
- [[量子几何]]
- [[量子度规]]
- [[阿秒瞬态吸收]]
- [[阿秒科学]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
