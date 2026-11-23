---
title: "2026-2506_05621-coherent-phonon-motions-and-ordered-vacancy-compou"
type: "papers"
created: "2026-08-29T16:10:14Z"
updated: "2026-11-15T15:09:24Z"
tags: ["deepxiv-论文库", "深度解析", "阿秒瞬态吸收光谱"]
related: ["Coherent phonon motions and ordered vacancy compound mediated quantum path interference in Cu-poor CuInxGa(1-x)Se2 (CIGS) with attosecond transient absorption", "DFT计算", "固体HHG", "固体高次谐波", "强场电离", "强场驱动", "拍赫兹电子学", "相干声子", "瞬态吸收光谱", "量子几何", "阿秒瞬态吸收", "阿秒科学", "高次谐波产生"]
source_raw: "2026-2506.05621-coherent-phonon-motions-and-ordered-vacancy-compou.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-10-30T04:28:45Z"
merged_from: ["wiki/papers/2506.05621.md"]
---

# Coherent Phonon Motions and Ordered Vacancy Compound Mediated Quantum Path Interference in Cu-Poor CuInₓGa₍1₋ₓ₎Se₂ (CIGS) with Attosecond Transient Absorption

## 林赛的理解

这篇工作是我们研究CuPoor CIGS薄膜中相干晶格动力学和电子相干的典型案例。ATAS在Se M₄,₅吸收边的时频双重高分辨率特性，使我们首次能在ps和fs两个时间尺度同时捕捉到：① 来自Chalcopyrite和OVC两相的A₁g光学声子；② 两相导带间的量子路径干涉。18.6(3) fs的超快振荡直接对应ΔE_CB = 0.222(7) eV的导带带阶——这与DFT计算的0.25 eV高度吻合，验证了分布式异质结的存在。对于我们的HHG/阿秒研究方向，该工作揭示了CIGS体系中空穴冷却(~1.7 ps)比电子快、且声子退相干时间约2.27(8) ps的关键参数，为后续泵浦-探测实验时序设计提供了参考。

## 研究问题（Research Question）
本工作要回答的核心问题是：**Cu-poor CuInₓGa₍1₋ₓ₎Se₂ (CIGS)中的有序空位化合物(OVC)相与主相Chalcopyrite之间的相干晶格动力学和电子动力学如何相互作用，以及这种相互作用如何影响光伏性能相关的超快过程**。具体包括：

1. 能否在CIGS中首次直接观测到相干声子运动？
2. OVC相和Chalcopyrite相的A₁g声子模式如何通过分布式异质结（type-II带阶）产生量子路径干涉？
3. 热载流子（电子和空穴）各自的冷却时间是多少，差异来源是什么？

## 研究背景（Background）
### 学术脉络

高次谐波产生和阿秒光脉冲的发现使得在原子、分子和固体系统中测量电子动力学成为可能。**阿秒瞬态吸收光谱（ATAS）** 由于对价带和导带中的空穴和电子动力学具有出色的灵敏度，已成为在自然时间尺度上表征电子动力学的关键方法。

### CIGS光伏材料的重要性

CIGS (Cu(InₓGa₍1₋ₓ₎)Se₂) 是I-III-VI₂黄铜矿化合物，具有：
- 高吸收系数，允许1-2 μm厚吸收层
- 可调直接带隙（通过[Ga]/([Ga]+[In])比例）
- 当前最高光电转换效率23.6%

CIGS在串联太阳能电池和单结电池中都有重要应用前景。

### OVC的关键作用

**有序空位化合物(OVCs)** 在Cu-poor条件下形成，邻近体相CIGS产生埋置type-II异质结：
- 通过降低OVC中价带最大值(VBM)加宽带隙
- 形成空穴屏障，阻止空穴到达CIGS/CdS界面
- 改善电荷收集效率，减少复合损失
- OVC呈n型（费米能级在带隙上方），Chalcopyrite呈p型 → 形成p-n异质结

### 前人工作

- 在Si的L₂,₃吸收边ATAS测量恢复了谷间散射时间常数
- Si纳米颗粒中观察到声子瓶颈效应
- 共蒸镀CIGS在~10²⁰ cm⁻³载流子密度下，Shockley-Read-Hall复合为主导机制
- 载流子冷却时间（与声子平衡）~3 ps
- Raman测量已报道159 cm⁻¹和176 cm⁻¹两个A₁g峰

## 研究方法（Methods）
### 样品制备

- **基底**: Si₃N₄ (5 mm × 5 mm) + 用于光学表征的Si片 (5 mm × 15 mm)
- **HfO₂阻挡层**: ~20 nm ALD生长于Si基底上（250°C），防止Cu扩散
- **CIGS共蒸镀**: 固定开航蒸发源，质谱仪反馈控制蒸发率
- **化学配比**: Cu/(Ga+In) = 0.9（略Cu-poor），[Ga]/([Ga]+[In]) = 0.26
- **XRF确认**: 1 μm厚样品验证元素比例
- **CIGS厚度**: ~48 nm（通过椭偏仪测定）
- **Al₂O₃钝化层**: ~10 nm ALD生长于所有样品（120°C）抑制氧化
- **沉积温度**: 最高425°C，沉积时间75 s

### ATAS实验装置

**泵浦光**: 少量fs, 800 nm IR脉冲
**探测光**: 阿秒XUV脉冲

具体光路：
1. 35 fs, 2.3 mJ, 800 nm (1 kHz Ti:Sapphire Astrella激光)
2. 展宽：2 m中空光纤（充Ne）
3. 压缩：4 fs（啁啾镜 + ADP晶体补偿三阶色散）
4. Mach-Zehnder干涉仪分束
5. 探测臂：IR聚焦到Ar气室产生HHG → Al箔滤除残余IR → XUV
6. XUV与泵浦IR在环形镜合并 → 聚焦到CIGS样品
7. 二次Al箔滤除残余泵浦IR
8. 光栅色散 → CCD (PIXIS 400 B)记录

**泵浦产生载流子密度**: ~2 × 10²⁰ cm⁻³

### DFT计算

- **泛函**: PBE+U (Hubbard U = 5 eV on Cu 3d orbitals, Dudarev方法)
- **模型**: Ga-free chalcopyrite CuInSe₂ (Eg = 1 eV) 和模型CuIn₃Se₅ (OVC)
- **带隙校正**: 实验值 scissors-shift
- **测量带隙**: Eg = 1.1 eV（椭偏仪），直接带隙在Γ点
- **OVC与Chalcopyrite带隙差**: ΔEg = 0.18 eV

### 测量参数

**长扫描（~ps）**: −165 to 1973.4 fs，步长26.4 fs → 研究相干声子和热载流子冷却
**短扫描（~100 fs）**: 步长3.3 fs → 研究快速电子动力学

**能量参考**:
- VBM (3d₃/₂): E_VBM = 54.1 eV（从ΔA(ε,τ)零交叉确定）
- CBM (3d₅/₂): E_CBM = 54.5 eV
- 价带区域: 52.0–54.1 eV
- 导带区域: 54.5–55.2 eV
- Se 3d自旋轨道分裂: 0.65 eV

### 数据分析

**迭代分解**（遵循Zuerch et al.方法）:

ΔA(ε,τ) = ΔA_shift(ε,τ) + ΔA_broadening(ε,τ) + ΔA_carriers(ε,τ)

边缘位移贡献:
ΔA_shift(ε,τ) = Σⱼ αⱼ(Aⱼ(ε + ΔE_shift(τ)) − Aⱼ(ε))

其中αⱼ为两相占比，ΔE_shift(τ)为瞬态边缘位移。

## 主要发现与核心结论

### 1. 相干声子运动（低频）

**首次在CIGS中观察到相干声子动力学！**

- **OVC相A₁g声子**: 频率 ν_OVC^A1g = 159(4) cm⁻¹ → **4.8 THz**
- **Chalcopyrite相A₁g声子**: 频率 ν_CIGS^A1g = 176.2(7) cm⁻¹ → **5.3 THz**
- **Raman相对振幅**: α_CIGS^A1g = 65%, α_OVC^A1g = 35%
- **声子相位**: φ_OVC^A1g = 0.73(4) rad, φ_CIGS^A1g = 0.75(2) rad（接近π/4，DECP+ISRS混合激发机制）
- **相干声子退相干时间**: T_ph^2 = 2.27(8) ps
- **退相干机制**: 可能是Klemens衰减（一个相干光学声子转化为两个声学声子）

### 2. 热载流子冷却时间

| 载流子类型 | 冷却时间 |
|-----------|---------|
| 空穴 (τ_decay^hole) | **1.7(2) ps** |
| 电子 (τ_decay^electron) | **2.6(5) ps** |
| 晶格弛豫 (τ_decay^phonon) | **2.7(8) ps** |

- 空穴冷却时间与前人报道的~3 ps（10²⁰ cm⁻³载流子密度）一致
- 空穴冷却更快原因：价带态密度(DOS)更高 → 电子-声子散射矩阵元更大 → 更高散射率
- 载流子复合时间~750 ps（比冷却慢两个数量级）
- 主导复合机制：Shockley-Read-Hall复合

### 3. 核心能级位移

- **初始核心能级位移**: 45 meV
- **初始带隙 renormalization (BGR)**: 11 meV（核心能级位移抵消BGR）
- 相干声子动力学主要由吸收边缘位移描述

### 4. 量子路径干涉（高频振荡）

- **振荡周期**: Δτ = **18.6(3) fs**
- **对应导带带阶**: ΔE_CB = h/Δτ = **0.222(7) eV**
- **DFT计算值**: ΔE_th^CB = 0.25 eV（吻合！）
- **起源**: OVC和Chalcopyrite导带间的双光学路径干涉（type-II带阶）

**物理图像**:
- OVC和Chalcopyrite形成分布式异质结
- Cu-poor条件导致~3 nm间隔的OVC平面缺陷
- 在τ=0，IR光子将电子从价带激发到两个导带的相干叠加态
- XUV从Se 3d₅/₂核心态探测两导带间的相干性

**量子相干度**: C ≈ **0.19**（~20%部分相干）
- 来源：实验时间抖动、环境相互作用（电子-声子/电子-电子散射）、无界面区域贡献

**电子穿越结时间延迟**: t_W = φ/ΔE_CB × ℏ = **12.1(8) fs**（φ = 4.1(3) rad）

### 5. 空穴产生证据

- 价带区域(52.0–54.1 eV)出现吸收增加
- 归因于Se 3d壳层到价带跃迁的开启 → 证明有空穴产生

### 6. 能带结构特征

- **价带**: 主要由Cu 3d和Se 4p反键轨道组成
- **导带**: 主要由Se 4s和In 5s轨道组成
- CBM和VBM均具有Se特征 → Se M₄,₅边缘是探测光伏性能核心的element-specific探针

## 潜在研究方向（Future Directions）
### 现存局限性

1. **样品限制**: 仅50 nm厚CIGS薄膜，OVC间距~3 nm估计基于成分推导
2. **元素覆盖**: 仅探测Se M₄,₅边，未覆盖Cu、In、Ga边
3. **时间分辨率**: 受泵浦-探测脉冲间时间抖动限制
4. **理论模型**: 4-level模型为简化模型，界面波函数对称性匹配需要更详细理论研究
5. **空间信息缺失**: ATAS是积分测量，无空间分辨率

### 未解决的关键问题

1. **声子工程**: 如何通过相干声子运动有效存储热载流子能量（热声子瓶颈）以突破Shockley-Queisser极限？
2. **界面相干性**: 波函数在OVC/Chalcopyrite界面的对称性匹配如何影响直接界面电荷转移？
3. **Ag合金化效应**: Ag合金化虽有益于串联设计但促进OVC形成，如何平衡？
4. **异质结质量优化**: 如何调控OVC分布和带阶以最大化量子相干效应？

### 值得探索的方向

1. **多元素边缘探测**: Cu M边、In N边、Ga L边 → 追踪各元素特异性动力学
2. **泵浦注量依赖**: 载流子密度对冷却时间和相干性的影响
3. **温度依赖**: 低温下相干声子寿命和量子干涉增强可能性
4. **其他黄铜矿成分**: Ag-alloyed CIGS等体系
5. **量子相干计量**: 利用18.6 fs振荡作为光伏材料中量子相干性的诊断工具

## 与林赛研究的关联

### HHG/阿秒方向

- **HHG产生探针脉冲**: 工作中用Ar气HHG产生XUV阿秒脉冲，直接关联我们的HHG研究方向
- **ATAS时频联合分辨率**: 26.4 fs和3.3 fs步长的瞬态吸收测量展示了高时间分辨率泵浦-探测技术
- **core-level探针机制**: Se 3d → CB/Se 3d → VB跃迁的state-blocking信号读取，与我们用HHG探测固体高次谐波的思路一致

### 强场驱动

- **fs IR泵浦**: 4 fs, 800 nm IR脉冲在CIGS中产生~2×10²⁰ cm⁻³载流子密度
- **高次谐波过程**: HHG产生XUV探针依赖于强场电离和复合过程

### 交变磁 / 莫尔 / 量子几何

- **分布式异质结**: OVC平面缺陷间距~3 nm形成周期性势阱
- **量子相干度0.19**: 表明电子在两相导带间存在非平凡波函数重叠——与量子几何（quantum geometry）概念相关
- **type-II带阶ΔE_CB = 0.222(7) eV**: 对应量子路径干涉的相位积累，可视为量子几何在光伏异质结中的直接探针

### 具体接口

- 该工作中的**18.6 fs量子干涉振荡**可作为光伏体系量子相干性诊断的**参考基准**
- **2.27(8) ps声子退相干时间**和**0.8(4) ps电子退相干时间**为后续泵浦-探测实验的延迟范围设计提供依据
- **Raman测量的声子频率**（159 cm⁻¹和176.2 cm⁻¹）可用于拉曼激发实验的频率参考

## 来源

- 蒸馏自全文（deep-read）
- arXiv: 2506.05621v2 [cond-mat.mtrl-sci] 18 Aug 2025
- 作者: Hugo Laurell, Jonah R. Adelman, Elizaveta Yakovleva, Carl Hägglund, Kostiantyn Sopiha, Axel Stenquist, Han K. D. Le, Peidong Yang, Marika Edoff, Stephen R. Leone
- 单位: UC Berkeley, Lawrence Berkeley National Lab, Lund University, Uppsala University
- 发表状态: 2026年投稿，2025年8月更新


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：CIGS 相干声子运动与有序空位化合物（ALD/CIGS 共蒸镀 + 质谱反馈，248 行）

**原理**：ALD HfO₂ 阻挡层（20 nm/250 °C）防 Cu 扩散 + CIGS 共蒸镀（质谱反馈；Cu/(Ga+In)=0.9 Cu-poor、[Ga]/([Ga]+[In])=0.26；~48 nm 椭偏测厚）+ Al₂O₃ 钝化（10 nm/120 °C）——研究相干声子运动与有序空位化合物。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| CIGS 共蒸镀 | Cu/(Ga+In)=0.9；[Ga]/([Ga]+[In])=0.26；~48 nm；XRF 确认 | §样品制备 |
| ALD | HfO₂ ~20 nm @250 °C；Al₂O₃ ~10 nm @120 °C | §样品制备 |

**适用边界**：页面提取限样品制备开头（声子运动结果在后续）；页面提取不完整处不虚构。
**代表作**：本文（arXiv:2506.05621）
*方法卡回补 2026-09-28*


## 合并自「Coherent phonon motions and ordered vacancy compound mediated quantum path interference in Cu-poor CuInxGa(1-x)Se2 (CIGS) with attosecond transient absorption」

# Coherent phonon motions and ordered vacancy compound mediated quantum path interference in Cu-poor CuInxGa(1-x)Se2 (CIGS) with attosecond transient absorption

**arXiv**: [2506.05621](https://arxiv.org/abs/2506.05621) | **方向**: 阿秒瞬态吸收光谱

## 深度解析

### 研究问题（Research Question）

Gap: CIGS 是薄膜光伏主力 (纪录效率 23.6%), 其效率提升依赖的 OVC (ordered vacancy compound) 埋藏型-II异质结此前只有稳态/慢时间尺度表征, CIGS 中的相干声子从未被观测, 更没有元素特异的阿秒时间分辨测量. Contributions: 首次对 CIGS 薄膜做 ATAS (跨 Se M4,5 边), 同时分辨两相 (chalcopyrite + OVC) 的 A1g 相干声子, 空穴/电子热载流子冷却时间, 以及 18.6 fs 周期的导带间量子路径干涉 (QPI) — 后者给出两相导带偏移 0.222(7) eV, 12.1 fs 的界面渡越时间和 0.19 的相干度, 提出 '光伏量子相干度量学' 的概念.

### 研究背景（Background）

方法论同构直接命中三条主线. (1) 拍赫兹电子学/阿秒科学: 这篇的 QPI 模板 — 拍频周期 → 能级间距, 相位 → 渡越时间 tW = ħ∂φ/∂E, 衰减 → 退相干 — 与我们用阿秒脉冲测量载流子群延迟/散射延迟的工具箱同构, 只是干涉仪的 两臂 从 '长短量子轨迹' 换成 '两相导带'. 12.1 fs 的界面渡越时间测量本质上是型-II 结上的电荷转移计时, 是 '光频电子学' 度量学在光伏材料上的实例. (2) 能谷物理: OVC 的 Z 能谷随 Cu 贫乏浮现, Γ-Z 谷间跃迁因界面波函数重叠而弱允许 — 与我们在固体 HHG 里关心的谷布居/谷相干 (能谷间量子拍) 是同一类物理, 这里用芯能级光谱而非谐波读出. '混相 = 分布式异质结 = 内置干涉仪' 的图像可迁移: 任何有埋藏界面的材料 (畴壁, 层状扭转角) 都可能藏着可读的谷间相干. (3) 固体 HHG 的机制对照: 55 THz 量子拍由 IR 制备叠加 + XUV 芯能级探测读出, 与固体 HHG 中激发态布居对谐波产额的调制共享理论骨架 (Lindblad/密度矩阵处理); 0.8 ps 的长电子相干时间及 '空间分离压低散射' 的机制, 对我们讨论固体 HHG 中退相干时间 (通常假设 <10 fs) 是一个重要的反例边界 — 退相干不是材料常数, 而是态的空间定域化的函数. (4) 边界与局限: 本文无 HHG 产物分析, Se M4,5 芯能级 (~55 eV) 探测需要 XUV 光谱仪, 与我们的固体 HHG 平台是互补而非直接叠加; 相干度 0.19 的估计链依赖多个近似 (Raman 布居, 载流子比例迁移), 数字应看作量级而非精确值; 摘要与正文的空穴冷却表述矛盾, 引用时以正文 1.7 ps (空穴) vs 2.6 ps (电子) 为准.

### 研究方法（Methods）

- 两晶相导带间的 QPI 度量学: 用拍频周期读导带偏移 (ΔE = h/Δτ), 用振荡衰减读电子退相干, 用相位读界面渡越时间 (tW = ħφ/ΔE) — 一套完整的 '量子拍模板', 把混相半导体变成内置干涉仪.
- 4 能级 Lindblad 主方程微扰解: |VB> + |CB1> (OVC) + |CB2> (chalcopyrite) + |3d5/2> 芯能级, 推出 ΔA ∝ -ρ11 - ρ22 - 2|ρ12|exp(-Γτ)cos(ΔEτ/ħ + φ) — 芯能级光谱直接读非对角相干元的解析框架.
- 迭代分解 (Zuerch 方法) 扩展到双相体系: ΔA = 边移 + 态阻塞 + 激发态展宽, 两相比例 αj 由 Raman 定标, 边移由 DFT Se-DOS 卷积 Lorentzian (Γ=0.8 eV) 正向计算验证.
- 相干度估计流程: Raman 归一化强度 → 布居; 分解得到的载流子/边移比 → 振荡幅度归一化 → |ρ12| → C — 可迁移到任何有双末态量子拍的体系.
- 实验: 4 fs IR 泵浦 (空心芯光纤展宽 + 啁啾镜 + ADP 三阶色散补偿), Ar 气高次谐波产生 few-burst 阿秒 XUV 脉冲, 泵浦载流子密度 2e20 cm-3; 快扫描 3.3 fs 步长, 55 THz 振荡在三次独立测量中复现.

### 主要发现与核心结论（Main Results）

- CIGS 首次观测到相干声子: 两个 A1g 模 — chalcopyrite 相 176.2(7) cm-1 与 OVC 相 159(4) cm-1 (Raman 确认归属), 两频叠加产生拍频, 约 1 ps 处振幅最小 (解相干) 后复相. 共享退相干时间 T2ph = 2.27(8) ps, 声子相位 0.73(4)/0.75(2) rad (接近 pi/4), 表明 DECP 与 ISRS 混合激发机制; 退相干通道为 Klemens 衰减 (一个光学声子转两个声学声子).
- 空穴与电子冷却时间分别测定: 空穴 1.7(2) ps, 电子 2.6(5) ps, 晶格弛豫 2.7(8) ps — 空穴冷却时间约为电子一半, 归因于价带更大的态密度 (电子-声子散射矩阵元含 DOS, 可散射末态多则速率高). 注意: 摘要写 'slower cooling of holes' 与正文数字矛盾 (正文空穴更快), 以正文数据为准.
- 18.6(3) fs 周期 (~55 THz) 快振荡 = 两相导带间量子路径干涉: 4 fs IR 泵浦在 chalcopyrite CB (Γ) 与 OVC CB (Z) 制备相干叠加, XUV 从 Se 3d5/2 芯能级探测. 拍频周期直接给出导带偏移 ΔECB = h/Δτ = 0.222(7) eV, 与 DFT 外推值 0.25 eV 一致.
- 电子相干时间 T2e = 0.8(4) ps — 远超典型半导体 (GaAs 室温 12.9 fs). 机制解释: type-II 异质结处两相 CB 态空间分离, 压低相间电子-电子/电子-声子散射; 剩余的相内散射主要通过相干 A1g 声子发生. 相位 φ = 4.1(3) rad 对应电子穿越结的群延迟 tW = 12.1(8) fs.
- 相干度定量: 由 Raman 强度定布居 (OVC 35% / CIGS 65%), 由振荡幅度定非对角元 |ρ12| ≈ 0.09, 得 C = |ρ12|/sqrt(ρ11ρ22) ≈ 0.19. 有限相干度来自实验抖动/噪声, 环境散射, 以及无结区域的纯态阻塞贡献.
- 迭代分解给出芯能级响应定量: 初始芯能级结合能移动 45 meV, 带隙重整化 (BGR) ≈ 11 meV; 声子对 ΔA 的调制通过吸收边移动 (ECBM 与芯能级同时被调制) 实现, 而载流子贡献为负的态阻塞.
- 样品物理: 共蒸镀 Cu-poor CIGS (Cu/(Ga+In)=0.9, GGI=0.26), Eg=1.1 eV 直接带隙; Cu 贫乏导致 OVC 类平面缺陷平均间距 ~3 nm — 膜内形成分布式 type-II 异质结, 这是 QPI 所需波函数重叠的来源; DFT (PBE+U, U=5 eV on Cu 3d) 系列计算显示 Z 点能谷随 Cu 浓度降低而浮现并下移.

### 潜在研究方向（Future Directions）

- 作者明示: 相干时间对载流子密度的依赖测量 — 分离相间/相内散射贡献, 检验空间定域化延展相干时间的假说.
- '光伏量子相干度量学': 高频振荡对比度 (相干度) 可能成为光伏性能的新观测量 — 界面波函数重叠决定电荷分离效率, 相干度是其超快代理量.
- 推广到其他混相/异质结体系: 型-II vdW 异质结, 量子阱, 多形材料 — 只要两末态导带可在光学上相干叠加, 即可用此干涉仪读带偏移/渡越时间/退相干.
- 相干声子与电子相干的耦合: 本文猜测相内电子散射经由相干 A1g 声子保持相位 — 声子相干性 '喂养' 电子相干性的方向值得专门设计实验.
- 对 Ag 合金化 (增强 OVC 形成) 的 tandem CIGS: OVC 比例可调 → QPI 对比度与相干度可作为 OVC 含量的无损伤表征手段.

### 来源

- [arXiv 2506.05621](https://arxiv.org/abs/2506.05621)
- 导入自 hermes 深度分析（2026-10-29T15:00:21Z）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：CIGS 阿秒瞬态吸收：相干声子分辨 + 双相导带量子路径干涉度量学

**原理**：对 Cu-poor CIGS 跨 Se M₄,₅ 边做 ATAS：同时分辨 chalcopyrite/OVC 两相 A1g 相干声子、载流子冷却时间，并首次观测 18.6 fs 周期的两相导带间量子路径干涉（QPI）——混相半导体成为内置干涉仪，以拍频读导带偏移、相位读界面渡越时间、衰减读退相干，提出'光伏量子相干度量学'。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| QPI 周期与导带偏移 | 18.6(3) fs（~55 THz）→ ΔE_CB = 0.222(7) eV（与 DFT 0.25 eV 一致） | 主要发现 |
| 界面渡越时间 | t_W = 12.1(8) fs（相位 φ = 4.1(3) rad） | 主要发现 |
| 电子相干时间 | T2e = 0.8(4) ps（空间分离压低散射，远超 GaAs 室温 12.9 fs） | 主要发现 |
| 相干度 | C ≈ 0.19（Raman 布居 + 振荡幅度链式估计） | 主要发现 |
| 相干声子 | 两相 A1g：176.2(7)/159(4) cm⁻¹，共享 T2ph = 2.27(8) ps | 主要发现 |
| 载流子冷却 | 空穴 1.7(2) ps / 电子 2.6(5) ps（正文为准，摘要表述矛盾） | 主要发现 |

**适用边界**：相干度估计链依赖多近似（应看作量级）；无 HHG 产物分析（Se M₄,₅ ~55 eV 需 XUV 谱仪）；摘要与正文空穴冷却表述矛盾以正文为准；QPI 需两相波函数重叠（分布式 type-II 结特有）。
**代表作**：Laurell et al., Coherent phonon motions and OVC mediated quantum path interference in Cu-poor CIGS with ATAS, arXiv:2506.05621 (2025)
*方法卡回补 2026-10-29*

<!-- linsai-wikilinks -->
## 关联概念

- [[Coherent phonon motions and ordered vacancy compound mediated quantum path interference in Cu-poor CuInxGa(1-x)Se2 (CIGS) with attosecond transient absorption]]
- [[DFT计算]]
- [[固体HHG]]
- [[固体高次谐波]]
- [[强场电离]]
- [[强场驱动]]
- [[拍赫兹电子学]]
- [[相干声子]]
- [[瞬态吸收光谱]]
- [[量子几何]]
- [[阿秒瞬态吸收]]
- [[阿秒科学]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
