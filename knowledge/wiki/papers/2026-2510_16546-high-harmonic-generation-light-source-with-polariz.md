---
title: "2026-2510_16546-high-harmonic-generation-light-source-with-polariz"
type: "papers"
created: "2026-08-29T14:20:31Z"
updated: "2026-11-15T15:09:19Z"
tags: []
related: ["2025-251016546-high-harmonic-generation-light-source-with-po", "2510.16546", "Berry 曲率", "arpes", "强场驱动", "拓扑绝缘体", "相位匹配", "量子几何", "量子几何反演", "量子几何张量"]
source_raw: "2026-2510.16546-high-harmonic-generation-light-source-with-polariz.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-10-27T12:47:32Z"
merged_from: ["wiki/papers/2510.16546.md", "wiki/papers/2025-251016546-high-harmonic-generation-light-source-with-po.md"]
---

# High harmonic generation light source with polarization selectivity and sub-100-μm beam size for time- and angle-resolved photoemission spectroscopy

## 林赛的理解

这篇工作是 HHG 光源工程化的深度技术报告，直接解决了我组推进 TrARPES 能力边界的两个核心痛点：一是亚 100 μm 级束斑（57 μm×90 μm）使测量 exfoliated flakes 和 van der Waals 异质结成为可能；二是 s-pol./p-pol. 偏振选择性解决了不同轨道对称性 band's signal contrast 问题。对我组而言，gas cell vs capillary 的对比分析（稳定性 5% vs 20% RMS）是工程决策的关键参考，而 140 fs 时间分辨率结合 2 μm MIR pump 的配置直接打开了 Floquet 工程在 graphene K 点和 TMDC valley-selective 方向的实验窗口。

## 研究问题（Research Question）
如何实现一个兼具**亚 100 μm 束斑**（<100 μm）和**偏振选择性**的 HHG 探针光源，并将其与 MIR pump 耦合，以扩展 TrARPES 对量子材料的测量能力——特别是适用于 exfoliated flakes、van der Waals 异质结等小样品，以及需要偏振分辨的轨道对称性研究和 Floquet 工程。

## 研究背景（Background）
TrARPES 是捕获量子材料超快动力学的主流技术，过去二十年仪器发展迅速。现有探针光源方案存在根本局限：

- **FHG（BBO/LBO/KBBF 晶体）**：光子能量 5.3–7.0 eV，仅覆盖费米能级以下约 1 eV 范围，动量范围限制在 BZ 中心约 0.6 Å⁻¹ 以内，无法探测 graphene conical dispersion 或 TMDC 大动量 valley。
- **HHG（惰性气体 HHG）**：可提供足够高的光子能量以覆盖大多数量子材料的完整 BZ，过去十年已广泛应用于 TrARPES，但**束斑通常 >100 μm**，不适用于 exfoliated flakes 等小样品。
- 此外，不同偏振光对不同轨道具有不同偶极矩阵元，可选择性增强特定 band 的信号强度和对称性，但 HHG 偏振控制此前很少被系统开发利用。

## 研究方法（Methods）
### 材料体系与样品
- **TMDCs**：NbSe₂、MoSe₂、TiSe₂（CDW 材料）、WSe₂
- **拓扑绝缘体**：Bi₂Se₃
- **石墨烯**：epitaxial bilayer graphene on SiC

### 激光系统
- Ti:Sapphire amplifier：10 kHz repetition rate，1.4 mJ pulse energy，35 fs pulse duration，800 nm
- SHG：400 nm（用于驱动 HHG）
- MIR pump：2 μm wavelength（540 meV photon energy）

### HHG 产生方案对比
1. **Gas cell**：1 mm 内径镍管，in-situ 钻孔，Ar 气压 ~100 Torr
2. **Capillary**：6 cm 长，150 μm 内径石英波导

两种方案均使用 Ar 作为非线性介质。

### 束斑优化策略
使用 toroidal mirror（f = 750 mm，1:1 成像比）聚焦。三自由度调节（R1 yaw、R2 pitch、R3 roll），其中 R1 和 R2 对束斑敏感，R3 不敏感。预对齐使用大气激光指针，最终用 Au/SiO₂ knife-edge pattern 在 UHV 中原位校准（Au 边缘 sharp <1 μm）。

### 偏振控制
在 HHG chamber 前插入 waveplate 控制驱动激光偏振，进而控制 HHG 输出偏振（s-pol. vs p-pol.）。

### 时间分辨率测量
通过追踪 graphene 光致激发电子在 0.5 eV 处的 delay trace，用 Gaussian 拟合提取仪器时间分辨率。

## 主要发现与核心结论

### 1. Gas cell vs Capillary：Gas cell 更适合本应用

| 参数 | Gas cell | Capillary |
|------|----------|-----------|
| 对输入脉冲能量要求 | 较宽松（~10 μJ 仍可行，若紧聚焦） | 严格（通常需 >1 mJ） |
| 对输入束要求 | 容忍度较高 | 需严格对准、束斑和模式 |
| 稳定性（RMS fluctuation） | **5%** | **20%**（无束指向稳定） |
| 最大光子通量（100 Torr Ar） | **3.5×10¹¹ photons/s** | 未给出具体数值 |

结论：gas cell 是本系统的更好选择。

### 2. 能量分辨率 < 80 meV

- Polycrystalline Au 费米边拟合：总能量分辨率 **76±20 meV**（扣除 80 K 热展宽 28 meV + 分析仪展宽 40 meV）
- WSe₂ K 点单晶测量：overall linewidth **71±2 meV**（与探头能量分辨率一致）

### 3. 束斑优化至 57 μm × 90 μm

- Toroidal mirror 三自由度优化策略有效
- 垂直束斑对 R2 rotation 极其敏感：R2 从 0 到 -1 mrad 变化，垂直束斑几乎翻倍
- 该束斑尺寸使 exfoliated flakes 和 van der Waals 异质结的 TrARPES 成为可能

### 4. HHG 偏振选择性显著提升不同轨道的信号对比度

- **NbSe₂**（Γ-K 方向）：Se 4p 轨道 band 在 p-pol. 下强度显著高于 s-pol.
- **MoSe₂**（K valley）：Mo 4d 自旋轨道分裂在 p-pol. 下更清晰可辨
- **TiSe₂**（Γ-M 方向，90° 旋转几何）：CDW 诱导的 Se 4p 折叠带在 **s-pol.** 下更清晰（p-pol. 反而变差——样品几何决定最优偏振）
- **Bi₂Se₃**：不同偏振同样揭示不同轨道特征

核心物理：偶极矩阵元随偏振方向变化，通过选择偏振使电场方向与轨道方向对齐，可最大化特定轨道的 photoemission 强度。

### 5. MIR pump–HHG probe 耦合实现 140 fs 时间分辨率

- **时间分辨率**：**140±10 fs**（Gaussian 拟合 0.5 eV 处 delay trace）
- 双层石墨烯光激发电子弛豫动力学：
  - **τ₁ = 90±10 fs**：hot electrons 通过 optical phonons 衰减
  - **τ₂ = 1800±200 fs**：hot electrons 通过 acoustic phonons 衰减
- 结果与已发表文献一致

### 6. 系统架构总结

- 10 kHz 放大器 + 1.4 mJ 高脉冲能量：同时支持 HHG probe + MIR pump + FHG probe
- FHG：适合 zoom-in BZ 中心精细能带结构
- HHG：覆盖完整 BZ 的大能量-动量范围
- MIR pump（2 μm）：更强的 light-matter interaction，适用于 Floquet 工程

## 潜在研究方向（Future Directions）
1. **进一步缩小束斑**：当前 57 μm × 90 μm 已 < 100 μm，但逼近更小样品（< 10 μm 级的纳米结构）仍需持续优化
2. **Floquet 工程拓展**：当前 MIR pump 2 μm 已实现 540 meV 光子能量，结合 HHG probe 可在 graphene K 点探测 Floquet-Bloch states，或在 TMDC 中实现 valley-selective Floquet 工程
3. **更高重复率 HHG**：目前 10 kHz 是时间分辨率与信噪比的折中，更高重复率（如 500 kHz）可提高counts rate 但需权衡热负荷
4. **偏振调制 ARPES**：利用 s-pol./p-pol. 偏振选择性提取轨道赝自旋纹理和 Berry 曲率信息
5. **更短脉冲 MIR pump**：若要将时间分辨率推至 < 100 fs 亚光学周期 regime，需压缩 MIR pump 脉冲宽度
6. **attosecond TrARPES**：当前 140 fs 分辨率尚不足以探测电子超快散射过程（fs 以下），需结合 HHG attosecond 脉冲

## 与林赛研究的关联

- **HHG**：本文核心工具，本组 HHG 光源设计参考 gas cell 方案的高稳定性策略
- **阿秒**：文章结尾提及 attosecond TrARPES 是未来方向，与我组 attosecond 探测能力建设直接相关
- **强场驱动**：HHG 本身即是强场物理过程，驱动激光偏振控制技术可迁移至其他强场实验
- **交变磁**：文中未涉及，但 TMDCs 的 valley degree of freedom 与交变磁存在物理联系
- **莫尔、量子几何**：偏振选择性揭示的轨道赝自旋纹理、Berry 曲率是量子几何的实验探针，石墨烯 bilayer 的双锥能带是量子几何的典型体系
- **石墨烯 K 点 Floquet 工程**：本文已论证可行性，是我组可立即开展的实验方向

## 来源

- 蒸馏自全文（deep-read）：Zhong, Cai, Bao et al. (Tsinghua/Fudan), arXiv:2510.16546v1, 2025/2026


## 合并自「2510.16546」

# 2510.16546 — 面向 TrARPES 的偏振可选亚 100μm HHG 探针

**arXiv**: [2510.16546](https://arxiv.org/abs/2510.16546) | **方向**: HHG光谱学 | Ultrafast Science 2025-10 | **引用 2** | Haoyuan Zhong 等 12 人（清华：**张洪云/周树云/陶镇生**）

## 深度解析

### 研究问题（Research Question）

TrARPES 的 HHG 探针两个关键参数长期未被系统优化：束斑尺寸（通常几百 μm~mm 级，限制小样品/微区测量）与偏振控制（XUV 偏振通常由产生过程固定，无法做轨道选择探测）。本文给出 10 kHz 放大器平台的系统方案。

### 主要发现与核心结论（Main Results）

| 指标 | 数值 | 意义 |
|---|---|---|
| 探针束斑 | 57×90 μm | 亚 100 μm，适配小样品 |
| 偏振控制 | s/p 可选 | 轨道选择探测（跃迁矩阵元对称性选择定则） |
| 时间分辨 | 140 fs（2 μm MIR 泵浦 + HHG 探针） | 中红外泵浦工程可行 |
| 示范 | MoS₂/WSe₂ + Bi₂Se₃ + 双层石墨烯 | 偏振增强不同对称性能带；石墨烯分辨两条弛豫通道 |

### 与林赛课题的关联

1. **避坑情报**：周树云/陶镇生（在 7-26 方向校准的避坑清单上）的平台型论文。其路线是"HHG 当探针照样品，光电子读出"（**末态光电子**）；林赛主攻是"HHG 谱本身作为反演探针"（**中间态量子几何**）。两条线互补但在"偏振控制 HHG 探测量子材料对称性"的交集会撞车——**proposal 差异化论证应明确写出此分界**。
2. **泵浦臂工程先例**：2 μm OPA + 10 kHz 达 140 fs，证明商用中红外泵浦路线工程可行，比引 800 nm 泵浦文献更有说服力（中红外正是"测—控闭环"的控臂）。
3. **方法同构**：他们的 s/p 偏振选择 → 轨道分辨，与量子几何反演的"多维光场组合"用同一套选择定则物理，只是反演目标从能带对称性升级到量子几何张量。**其实验数据可作反演方法的实验先导**。
4. **本质区别**：140 fs 离亚周期还远（受泵浦脉宽与电子飞行时间展宽限制）；HHG 谱的亚周期信息不受此限（谐波相位编码在发射过程内）——差异化论证第二点。

### 来源

- [arXiv 2510.16546](https://arxiv.org/abs/2510.16546)
- 简报深读 2026-08-14/15（本会话）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：偏振可编程 HHG 光源（多材料筛选：TMDC/拓扑绝缘体/外延双层石墨烯 + SHG/MIR 双驱动）

**原理**：多材料体系筛选 HHG 偏振可编程光源：TMDC（NbSe₂/MoSe₂/TiSe₂-CDW/WSe₂）+ 拓扑绝缘体 Bi₂Se₃ + 外延双层石墨烯/SiC；激光：Ti:Sa 10 kHz/1.4 mJ/35 fs/800 nm + SHG 400 nm + MIR 2 µm（540 meV）。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 材料 | NbSe₂/MoSe₂/TiSe₂(CDW)/WSe₂/Bi₂Se₃/epitaxial bilayer graphene on SiC | §材料体系与样品 |
| 激光 | Ti:Sa 10 kHz/1.4 mJ/35 fs/800 nm；SHG 400 nm；MIR 2 µm/540 meV | §激光系统 |

**适用边界**：页面提取限方法框架（偏振可编程机制在后续）；页面提取不完整处不虚构。
**代表作**：本文（arXiv:2510.16546）
*方法卡回补 2026-09-28*


## 合并自「2025-251016546-high-harmonic-generation-light-source-with-po」

# High harmonic generation light source with polarization selectivity and sub-100-μm beam size for time- and angle-resolved photoemission spectroscopy

## 林赛的理解

这是一篇工程性很强的仪器论文，清华周树云组与复旦团队合作，解决了 HHG-Probe TrARPES 实用化中的两个关键瓶颈：束斑尺寸（57 μm×90 μm）和偏振选择性。核心贡献不在物理发现，而在于把一个"能做"的技术路线打磨到"好用"——gas cell 稳定性（RMS 5%）显著优于 capillary（20%），用 knife-edge scan 在 UHV 中实测束斑，通过 R2 pitch rotation 校准建立系统方法论。双层石墨烯演示了 140 fs 时间分辨率，分辨出 90 fs（光学声子）和 1800 fs（声学声子）两个弛豫通道。这套系统与 2 μm MIR pump 耦合后，为 Floquet 工程和 TMDCs 谷选择激发提供了实验接口。对林赛 PI 而言，HHG 偏振选择性是直接可用的工具——通过切换 s-pol./p-pol. 可以选择性增强特定轨道的贡献，这对于研究 Moiré 系统中的隐藏序（hidden orders）是一个额外的表征维度。

## 研究问题（Research Question）
如何实现一个兼具高光子通量（>10¹¹ ph/s）、亚百微米束斑（<100 μm）、能量分辨率优于 80 meV、且具备偏振选择性的 HHG probe 光源，用于 TrARPES 测量——以覆盖石墨烯 conical dispersion、TMDCs momentum valleys 等需要大动量范围的量子材料体系。

## 研究背景（Background）
**TrARPES 技术演进**：TrARPES 是捕捉量子材料超快动力学的主流实验技术，过去二十年经历了快速发展，从单纯的动力学测量逐步扩展到利用强泵浦光作为控制手柄来调控瞬态电子结构或诱导相变。仪器规格中泵浦决定光与材料的激发耦合方式，探头光束则决定可探测的材料类型及能量/动量范围。

**现有探头光源的局限**：
- **FHG（四次谐波）**：基于 BBO/LBO 晶体可产生高达 6.3 eV 光子能，或 KBBF 器件可调谐 5.3–7.0 eV。但仅覆盖 Fermi 能级以下约 1 eV 范围，可达动量范围局限于 Brillouin 区中心附近约 0.6 Å⁻¹。无法覆盖石墨烯 conical dispersion 或 TMDCs 大动量谷等感兴趣的电子结构。

- **HHG（高次谐波）**：使用惰性气体作为非线性介质，可提供足够高的光子能量访问大多数量子材料所需的大能量和大动量范围。过去十年已逐步应用于 TrARPES 测量，在能量分辨率和光子通量方面取得了重大进展。但典型束斑 >100 μm，不适合探测小样品（ exfoliated flakes、van der Waals 异质结构）。

**两个被忽视的优化方向**：
1. **束斑尺寸优化**：需小于 100 μm 才能扩展到小样品研究
2. **偏振选择性控制**：不同偏振光可选择性增强具有不同轨道贡献和对称性的能带（由偶极矩阵元决定），这对研究轨道伪自旋和 Berry  curvature 至关重要

## 研究方法（Methods）
**激光系统**：10 kHz Ti:Sapphire 放大器，800 nm，脉冲能量 1.4 mJ，脉宽 35 fs

**HHG 生成方案（对比两种）**：
- **Gas cell**：1 mm 内径镍管，原位钻孔透射，Ar 气压在 100 Torr 附近达到相位匹配
- **Capillary**：6 cm 长，150 μm 内径石英波导
- Gas cell 对输入脉冲能量和光束要求更宽松（10 μJ 即可），稳定性更好（RMS 5% vs 20%）

**驱动方式**：基频光的二次谐波（SH, 400 nm）驱动 HHG（相较基频驱动可获得更高效率且更易隔离目标谐波）

**光束处理与传输**：Au 镜导引，Toroidal mirror（焦距 750 mm，1:1 成像比）聚焦，Al/Sn 金属膜滤波（阻隔残余 SH、隔离 7 次谐波、与 0.5 mm 狭缝共同保护高真空）

**偏振控制**：HHG 腔前插入波片（WP）控制驱动激光偏振，从而控制 HHG 输出偏振（s-pol. 或 p-pol.）

**束斑优化方法**：
- 使用激光笔在大气中预对齐 toroidal mirror（反射光学元件，波长无关）
- Toroidal mirror 有三个旋转自由度：R1（yaw）、R2（pitch）、R3（roll）；束斑尺寸对 R1 和 R2 敏感，对 R3 不敏感
- 在 UHV 中使用沉积在绝缘 SiO₂上的 Au 图案（边缘锐利度 <1 μm）进行 knife-edge scan，实测 HHG 束斑

**TrARPES 集成**：HHG probe + 2 μm MIR pump，双层石墨烯演示时间分辨率

**能量分辨率表征**：多晶 Au 的 Fermi 边拟合，WSe₂ 单晶能带线宽分析

## 主要发现与核心结论

1. **Gas cell vs. Capillary 对比**：
   - Gas cell RMS 波动 5%，Capillary RMS 波动 20%（无束指向稳定）
   - Gas cell 对脉冲能量和光束要求更低（10 μJ 级别可行）
   - 选择 gas cell 作为最终方案

2. **光子通量**：Gas cell 在 ~100 Torr Ar 气压下达到最大光子通量 3.5×10¹¹ photons/s（光阑后测量，photodiode responsibility 0.25 A/W）

3. **能量分辨率**：
   - Polycrystalline Au Fermi 边拟合：总能量分辨率 76±20 meV（扣除 80 K 热展宽 28 meV 和分析器展宽 40 meV 后）
   - WSe₂ 单晶线宽分析：71±2 meV（扣除热展宽和分析器展宽后）
   - 探头能量分辨率优于 80 meV

4. **优化束斑尺寸**：57 μm × 90 μm（horizontal × vertical）
   - R2 rotation 对垂直束斑极为敏感：从 0 到 -1 mrad 变化几乎使束斑加倍
   - 束斑优化是实现小样品（exfoliated flakes、van der Waals 异质结构）测量的关键步骤

5. **偏振选择性**：
   - **NbSe₂**：Se 4p 轨道贡献的能带在 p-pol. 下强度显著增强
   - **MoSe₂**：K 谷附近 Mo 4d 自旋轨道分裂在 p-pol. 下更好地被分辨
   - **TiSe₂**（Γ-M 方向）：CDW 感生的 Se 4p 折叠带在 s-pol. 下更好地被揭示（样品几何不同导致最优偏振不同）
   - **Bi₂Se₃**：同样展现出偏振依赖的能带强度调制
   - 证明 HHG 偏振选择性可用于获取高质量数据，适用于不同材料或几何构型

6. **双层石墨烯 TrARPES**：
   - 泵浦波长 2 μm，泵浦光子能 540 meV，泵浦通量 1 mJ cm⁻²，p-pol.
   - **时间分辨率**：140±10 fs（Gaussian 拟合）
   - **电子温度演化**：双指数弛豫
     - τ₁ = 90±10 fs：热电子通过光学声子衰减
     - τ₂ = 1800±200 fs：热电子通过声学声子衰减
   - 与先前报道一致

7. **系统级总结**：
   - 高光子通量
   - 能量分辨率优于 80 meV
   - 亚百微米束斑（57 μm×90 μm）
   - 140 fs 时间分辨率（MIR pump）
   - 偏振选择性
   - 10 kHz / 1.4 mJ 放大器激光器为 MIR pump 和 Floquet 工程提供充足脉冲能量

## 潜在研究方向（Future Directions）
1. **技术扩展**：
   - 将亚百微米束斑 HHG probe 应用于 exfoliated graphene flakes、TMDCs 单层及 Moiré 异质结构
   - 进一步压缩束斑（如 <30 μm）的极限探索

2. **Floquet 工程**：
   - 石墨烯 K 点 Floquet 态探测
   - TMDCs 谷选择 Floquet 工程
   - 目前 Floquet 工程研究仅限于少数半导体和拓扑绝缘体，该系统使其扩展到石墨烯和 TMDCs 成为可能

3. **偏振选择性深度应用**：
   - 利用 s-pol./p-pol. 差异提取轨道 pseudospin texture 和 Berry curvature 信息
   - 时间域偏振调制（circular dichroism without circular photons）

4. **MIR pump 参数空间**：
   - 探索 2 μm 以外的其他 MIR 波长（Floquet 工程需低于带隙泵浦）
   - 泵浦通量、偏振对光致涌现现象的调控

5. **系统兼容性**：
   - HHG probe 与 FHG probe 的组合使用（FHG 适合高分辨 zoom-in BZ 中心，HHG 覆盖全 BZ）
   - 与其他泵浦源（可见、近红外）的耦合

6. **仪器极限**：
   - 时间分辨率受 35 fs 泵浦脉宽限制，140 fs 仪器响应主要来自 MIR pump 产生的chirped 脉冲
   - 束斑稳定性长期监测（小时量级）

## 与林赛研究的关联

- **HHG 光源本身**：这篇工作是一个可以直接引用的 HHG-Probe TrARPES 仪器参考，尤其是束斑优化方法论（toroidal mirror R2 pitch calibration、UHV knife-edge scan）和 gas cell 稳定性数据
- **偏振选择性**：对于 Moiré 系统（如 twisted bilayer graphene、ABC-TLG）中的隐藏序，偏振切换是选择性增强特定轨道信号的有效工具，可与林赛组的 Moiré 表征技术耦合
- **时间分辨率 140 fs**：对于强场驱动交变磁研究，140 fs 足以追踪电子系动力学，但若需追踪真正的阿秒尺度过程（如 HHG 本身）仍需进一步压缩
- **2 μm MIR pump**：与强场驱动交变磁的泵浦方案有技术接口——高脉冲能量 10 kHz 系统是驱动 MIR-OPA 或产生强场 HHG 的理想平台
- **量子材料体系**：TMDCs（NbSe₂、MoSe₂、TiSe₂）和拓扑绝缘体 Bi₂Se₃ 的偏振依赖数据，对理解 Moiré 系统中的对称性破缺和能带工程有参考价值

## 来源

- 蒸馏自全文（deep-read），arXiv:2510.16546，周树云组（清华）、陶振声组（复旦），2025

<!-- methods-backfill:v1 -->

## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：亚百微米束斑偏振选择性 HHG-TrARPES 光源（SH 驱动 gas cell + toroidal 束斑标定）

**原理**：10 kHz Ti:Sapphire 放大器倍频（400 nm SH）驱动 Ar gas cell 产生 HHG 作 TrARPES 探针：金属膜滤波隔离 7 次谐波、toroidal mirror 1:1 成像压缩束斑（R2 pitch 旋转角标定束斑尺寸敏感度）、UHV 内 knife-edge scan 实测束斑；腔前波片切换驱动偏振实现 HHG 输出 s/p 偏振选择性（轨道/对称性选择性增强能带）；配 2 μm MIR pump 演示双层石墨烯时间分辨率与双通道电子弛豫。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 激光系统 | 10 kHz Ti:Sapphire；800 nm；1.4 mJ；35 fs | 研究方法·激光系统 |
| HHG 介质 | gas cell：1 mm 内径镍管原位钻孔透射；Ar ~100 Torr 相位匹配；输入 10 μJ 级即可 | 研究方法·HHG 生成方案 |
| 光子通量 | 3.5×10¹¹ photons/s（~100 Torr Ar，光阑后 photodiode 0.25 A/W） | 主要发现·2 |
| 能量分辨率 | 总 76±20 meV（Au Fermi 边拟合，扣 80 K 热展宽 28 meV、分析器 40 meV）；WSe₂ 线宽法 71±2 meV | 主要发现·3 |
| 束斑尺寸 | 57 μm×90 μm（H×V）；R2 pitch 从 0 到 −1 mrad 几乎使束斑加倍 | 主要发现·4 |
| 稳定性对比 | gas cell RMS 5% vs capillary（6 cm/150 μm）RMS 20%（无束指向稳定） | 主要发现·1 |
| 双层石墨烯 TrARPES | 2 μm pump（540 meV，1 mJ/cm²，p-pol.）；时间分辨率 140±10 fs；τ₁=90±10 fs（光学声子）、τ₂=1800±200 fs（声学声子） | 主要发现·6 |

**适用边界**：时间分辨率受 35 fs 泵浦脉宽与 MIR chirped 脉冲限制（140 fs），追踪阿秒尺度过程需再压缩；束斑稳定性长期（小时级）监测未报；偏振选择性最优配置依赖样品几何（NbSe₂ p-pol. vs TiSe₂ s-pol.）；Floquet 工程需低于带隙泵浦，2 μm 外波长未探索。
**代表作**：周树云组（清华）×陶振声组（复旦），arXiv:2510.16546 (2025)
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[2025-251016546-high-harmonic-generation-light-source-with-po]]
- [[2510.16546]]
- [[Berry 曲率]]
- [[arpes]]
- [[强场驱动]]
- [[拓扑绝缘体]]
- [[相位匹配]]
- [[量子几何]]
- [[量子几何反演]]
- [[量子几何张量]]
<!-- /linsai-wikilinks -->
