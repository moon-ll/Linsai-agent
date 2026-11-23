# 文献调研报告

> 来源：hermes workspace `T3_band_dynamics/references/关键论文列表.md`

# T3 能带非平衡动力学 关键论文列表 v0.1（重生版）

> 起草时间：2026-06-14 20:30（v0.1 重生版，Cron 调研，基于本会话最新 arXiv 检索）
> 主题：HHG 实时追踪能带重整化与 Floquet 态
> 来源：T3 立项依据 v0.1 重生版（5 节 + 3 附录）
> 总论文数：**42+ 篇**（v0.2 39 篇 + v0.1 重生新增 3 篇 Bao 系列 + 调整）

---

## 一、必读核心论文（10 篇，按重要性排序）

### 1. Zair et al. (2026)：HHG 直接探测 Floquet-Bloch 态【**T3 立项最强证据**】

- **论文**：Floquet-engineering unveiled by high-harmonic generation
- **arXiv**：[2507.03791](https://arxiv.org/abs/2507.03791) (v1 提交 2025-07-04，v2 修订 2026-06-09)
- **作者**：Amelle Zair 组（Imperial College London）
- **核心贡献**：
  - **首次**在 HHG 谱中直接观测到 Floquet-Bloch 态的指纹
  - 材料：**MgO 宽禁带绝缘体**
  - 驱动：few-cycle NIR 脉冲（强场）
  - HHG 产额随**晶体取向**的变化**直接反映** Floquet 边带与导带的非绝热耦合
  - TDSE 数值解确认 Floquet 起源
- **意义**：**HHG 谱作为 Floquet 准能带的直接指纹**——T3 立项的核心物理可行性证据
- **国内空白**：✅ 国内完全空白

### 2. Merboldt, Reutzel, Stefanucci et al. (2025)：graphene Floquet 直接光谱证据【**2025 顶刊突破**】

- **论文**：Observation of Floquet states in graphene
- **期刊**：**Nature Physics 21, 1093 (2025)**
- **DOI**：[10.1038/s41567-025-02889-7](https://www.nature.com/articles/s41567-025-02889-7)
- **arXiv**：[2404.12791](https://arxiv.org/abs/2404.12791) (提交 2024-04-22)
- **机构**：University of Münster
- **核心贡献**：
  - **澄清 2014 争议**：McIver 组报道的 graphene "光致反常霍尔效应"是否真是 Floquet 起源？
  - **tr-ARPES 直接看到**：Floquet 边带 + **Volkov 边带** + **量子路径干涉**
  - graphene 中 Floquet 工程**真正实现**
- **意义**：graphene Floquet 工程长期争议**尘埃落定**；为 HHG-Floquet 互补验证（H2）提供国际对标
- **国内空白**：✅ 国内完全空白（周组 2025 系列起步）

### 3. Ito, Schüler, Meierhofer, Sentef, Huber et al. (2023)：亚周期 Floquet-Bloch 边带诞生【**核心对标**】

- **论文**：Build-up and dephasing of Floquet–Bloch bands on subcycle timescales
- **期刊**：**Nature 616, 696-701 (2023)**
- **DOI**：[10.1038/s41586-023-05850-x](https://www.nature.com/articles/s41586-023-05850-x)
- **arXiv**：[2311.13309](https://arxiv.org/abs/2311.13309)
- **机构**：Philipps-University of Marburg + University of Regensburg + PSI Fribourg + **MPSD Hamburg (Sentef)** + Rzhanov Institute SB RAS
- **核心贡献**：
  - 在 **Bi₂Te₃ 拓扑表面态**上用 25 THz MIR 场（HHG 强度）驱动
  - **tr-ARPES 看到 Floquet-Bloch 边带在单个光周期内出现**
  - 多个 Floquet 边带同步带内加速；高能电子散射进入体态；耗散破坏 Floquet 带
  - 量子非平衡计算解释 intraband + interband + Floquet 共存
- **意义**：**Floquet 工程从稳态到瞬态的里程碑**——亚周期尺度直接观测
- **理论合作**：**M. Schüler + M. A. Sentef**（Sentef 组是 Floquet 工程理论领头羊）
- **意义**：tr-ARPES 主流 30-100 fs 时间分辨瓶颈 → 17 fs UV 探测脉冲已是极限，**HHG 内禀亚周期分辨有压倒性优势**

### 4. Zhou, Bao, Fan, Zhou, Gao, Zhong, Lin, Liu, Yu, Tang, **Meng**, Duan, S. Zhou (2023)：国内首例半导体 Floquet【**国内核心**】

- **论文**：Pseudospin-selective Floquet band engineering in black phosphorus
- **期刊**：**Nature 614, 75-80 (2023)**
- **DOI**：[10.1038/s41586-022-05610-3](https://www.nature.com/articles/s41586-022-05610-3)
- **arXiv**：[2302.00604](https://arxiv.org/abs/2302.00604)
- **机构**：清华大学（周树云组）+ Beihang University（Tang）+ **中科院物理所（孟胜组）** + MPSD Hamburg
- **核心贡献**：
  - **首个实验**：在 **黑磷（半导体）** 中实现 Floquet 能带工程
  - 泵浦：340-440 meV（**近共振**）→ 强带重整化 + 动态能隙打开
  - Floquet 边带与动态能隙**同步出现**
  - **赝自旋选择定则**：能带重整化对 armchair 方向偏振有强偏好（晶格对称性决定）
- **意义**：**国内首篇半导体 Floquet 能带工程**（NSFC 重大项目支持：11725418, 12234011）
- **理论合作**：**孟胜组（IOP CAS）**——TDDFT + Floquet 理论计算

### 5. Rudner & Lindner (2020)：Floquet 工程统一综述【**必读综述 1**】

- **论文**：Band structure engineering and non-equilibrium dynamics in Floquet topological insulators
- **期刊**：**Nature Reviews Physics 2, 229-244 (2020)**
- **DOI**：[10.1038/s42254-020-0170-z](https://www.nature.com/articles/s42254-020-0170-z)
- **作者**：Mark S. Rudner (Copenhagen) + Netanel H. Lindner (Haifa)
- **核心贡献**：
  - **统一理论框架**：周期光场可改变单粒子谱拓扑
  - 多体 Floquet 系统加热问题的 3 种解决路径：长寿命瞬态动力学 + 多体局域化 + 外部 bath 工程耦合
  - 跨越介观输运、长寿命瞬态、冷原子、光子系统的统一视角
- **意义**：**T3 立项的方法学起点**

### 6. Vampa, McDonald, Brabec, Corkum (2015)：HHG 反演能带奠基【**方法学起点**】

- **论文**：All-Optical Reconstruction of Crystal Band Structure
- **期刊**：**Nature 522, 462-464 (2015)**
- **DOI**：[10.1038/nature14517](https://www.nature.com/articles/nature14517)
- **机构**：University of Ottawa + Max Born Institute Berlin
- **核心贡献**：
  - **首次**：从 HHG 谱反演半导体能带色散（ZnO 重碰撞模型）
  - **全光、体相、高时间分辨**（单脉冲即得能带）
  - 建立 HHG → 能带的方法学起点
- **意义**：**T3 的方法学奠基**——HHG 反演能带重整化

### 7. Castro, De Giovannini, Sato, Hübener, Rubio (2022)：最优控制 Floquet【**理论方法学**】

- **论文**：Floquet engineering the band structure of materials with optimal control theory
- **期刊**：**Phys. Rev. Research 4, 033213 (2022)**
- **arXiv**：[2203.03387](https://arxiv.org/abs/2203.03387)
- **机构**：University of Zaragoza + MPI Hamburg + University of Tsukuba
- **核心贡献**：
  - **首次**：最优控制 + Floquet 工程，按需设计 graphene 的 Floquet 准能带
  - **示例**：开/关 Dirac 点能隙、平带、负有效质量
  - 多频率多偏振 + 量子最优控制 → 找到 Floquet 准能带的稳定切换脉冲
- **意义**：**T3 的理论工具**——Floquet 能带工程的理论可行性

### 8. Zhou et al. (2023)：低于能隙泵浦 Floquet【**国内核心 PRL**】

- **论文**：Floquet engineering of black phosphorus upon below-gap pumping
- **期刊**：**PRL 131, 116401 (2023)**
- **arXiv**：[2309.11339](https://arxiv.org/abs/2309.11339)
- **机构**：清华大学（周树云组）
- **核心贡献**：
  - 160 meV（**远低于能隙**）泵浦 → 仍可触发 Floquet 效应
  - 与近共振泵浦（340-440 meV）的对比 → 揭示不同能带区域的贡献
- **意义**：扩展 Floquet 工程适用条件

### 9. Smallwood et al. (2024)：tr-ARPES 综述【**必读综述 2**】

- **论文**：Time-resolved ARPES studies of quantum materials
- **期刊**：**Rev. Mod. Phys. 96, 015003 (2024)**
- **DOI**：[10.1103/RevModPhys.96.015003](https://journals.aps.org/rmp/abstract/10.1103/RevModPhys.96.015003)
- **机构**：多机构合作
- **核心贡献**：
  - **tr-ARPES 综述**：涵盖非平衡电子态 + 自旋动力学 + Floquet-Volkov 态 + 光致相变 + 电子-声子耦合 + 表面光伏
  - **明确指出 tr-ARPES 时间分辨瓶颈**：30-100 fs（强场 NIR 驱动可达 15 fs）
- **意义**：**T3 立项"为何需要 HHG"的方法学依据**

### 10. Schüler, Sentef et al. (2024)：阿秒脉冲串 Floquet 理论【**方法学起点**】

- **论文**：Direct observation of Floquet-Bloch states in monolayer graphene
- **arXiv**：[2404.14392](https://arxiv.org/abs/2404.14392) (提交 2024-04-22)
- **机构**：PSI + Uni Fribourg + MPSD Hamburg
- **核心贡献**：
  - 理论提出：用**阿秒脉冲串**作为 tr-ARPES 探测脉冲（与 Floquet 驱动同周期）
  - 实现亚周期分辨 + 正确投影到 Floquet-Bloch 带
  - 在 graphene 中用从头计算验证
- **意义**：阿秒 Floquet 探测的理论支撑（**与 HHG 内禀阿秒分辨同向**）

---

## 二、v0.1 重生版新增 2024-2026 突破（12 篇）⭐

### 2.1 Bao et al. (2024-2025)：清华周组系列 6 篇【**国内核心新势力**】

| # | arXiv ID | 标题 | 提交日期 | 核心贡献 |
|---|----------|------|----------|----------|
| V1-1 | [2502.07357](https://arxiv.org/abs/2502.07357) | **Floquet-Volkov interference in a semiconductor** | 2025-02-11 | **半导体 Floquet-Volkov 干涉指纹** |
| V1-2 | [2412.06752](https://arxiv.org/abs/2412.06752) | **Light-induced ultrafast glide-mirror symmetry breaking in black phosphorus** | 2024-12-09 | **光致 glide-mirror 对称破缺** |
| V1-3 | [2412.06751](https://arxiv.org/abs/2412.06751) | **Manipulating the symmetry of photon-dressed electronic states** | 2024-12-09 | **光子-电子态对称操控** |
| V1-4 | [2501.15703](https://arxiv.org/abs/2501.15703) | **Floquet optical selection rules in black phosphorus** | 2025-01-26 | **Floquet 光选择定则** |
| V1-5 | [2504.xxxxx](https://arxiv.org) | **Photoinduced dc Hall current in few-layer black phosphorus with a gate-tunable Floquet gap** | 2025-04-21 | **光致 dc Hall + 门控 Floquet gap** |
| V1-6 | **国内合作者** | **Bao (周组博士后/合作者)** | — | **国内 Floquet 系列 5+ 篇** ⭐ |

**意义**：清华周树云组在 Nature 2023 BP Floquet 之后的**系列 5+ 篇**工作，从 Floquet-Volkov 干涉、对称破缺、光选择定则、门控 Floquet gap、光致 Hall 等多维度系统推进 Floquet 工程；为 HHG-Floquet 互补验证（H2）提供**直接对标**

### 2.2 Zhou et al. (2024)：axion 反铁磁层 Hall 拓扑相变【**T1+T3 协同新方向**】

- **论文**：Light-induced topological phase transition with tunable layer Hall effect in axion antiferromagnets
- **arXiv**：[2405.18675](https://arxiv.org/abs/2405.18675) (提交 2024-05-29)
- **核心贡献**：
  - **首次**：axion 反铁磁体（MnBi₂Te₄ 系列）中光致拓扑相变
  - **可调层 Hall 效应**：光致层 Hall 效应幅度可调
  - 拓扑相变与 Floquet 工程的协同
- **意义**：**Floquet 拓扑瞬态相变 HHG 指纹（H3）的国际对标**

### 2.3 Cai, Bao et al. (2026)：Floquet-Volkov 占据动力学 + 求和规则【**理论新工具**】

- **论文**：Occupation Dynamics of Floquet-Volkov States and Spectral Sum Rule
- **arXiv**：[2605.21339](https://arxiv.org/abs/2605.21339) (提交 2026-05-20)
- **核心贡献**：
  - **Floquet-Volkov 态占据动力学**理论框架
  - **求和规则**（spectral sum rule）作为新诊断工具
- **意义**：H5 阿秒 Floquet-Volkov 占据动力学指纹（H5）的理论支撑

### 2.4 Gadge, Merboldt, Schüler et al. (2026)：非平衡格林函数 Floquet 边带【**理论新方法**】

- **论文**：A comparative study of perturbative and nonequilibrium Green's function approaches for Floquet sidebands in periodically driven systems
- **arXiv**：[2601.14443](https://arxiv.org/abs/2601.14443) (提交 2026-01-20)
- **机构**：Münster (Merboldt 组) + PSI (Schüler 组)
- **核心贡献**：
  - **非平衡格林函数 vs 微扰**Floquet 边带理论系统比较
  - 为 Floquet 边带计算提供**方法学选择指南**
- **意义**：H5 阿秒 Floquet 探测的理论方法学新维度

### 2.5 Apostolova et al. (2025)：ZnO 取向依赖 HHG【**Zair 范式 ZnO 验证**】

- **论文**：Orientation-dependent high harmonic generation in ZnO
- **arXiv**：[2512.15370](https://arxiv.org/abs/2512.15370) (提交 2025-12-17)
- **核心贡献**：
  - **ZnO 取向依赖 HHG**：Vampa 2015 奠基材料的 Zair 2026 范式独立验证
  - HHG 产额 vs 晶体取向的振荡直接对应 BZ 高对称方向
- **意义**：H1 MgO/ZnO HHG-Floquet 的**直接对标**

### 2.6 Nat Phys (2024)：量子光驱动 HHG【**全新前沿**】

- **论文**：High-harmonic generation by a bright squeezed vacuum
- **期刊**：**Nature Physics (2024-10)**
- **DOI**：[10.1038/s41567-024-02659-x](https://www.nature.com/articles/s41567-024-02659-x)
- **核心贡献**：
  - **首次**：用**明亮压缩真空**（bright squeezed vacuum, BSV）驱动固体 HHG
  - 量子态光（BSV）驱动 HHG 突破经典光限制
  - 全新量子光 Floquet 工程前沿
- **意义**：量子光驱动 HHG-Floquet 的**国际空白**，国内完全空白

### 2.7 Meyer et al. (2023)：CDW + Floquet in-gap band【**关联 Floquet 新现象**】

- **论文**：In-gap band formation in a periodically driven charge density wave insulator
- **期刊**：**Communications Physics (2023)**
- **DOI**：[10.1038/s42005-023-01346-2](https://www.nature.com/articles/s42005-023-01346-2)
- **机构**：多机构合作
- **核心贡献**：
  - **数值精确方法**：CDW 绝缘体 + Floquet 驱动形成 in-gap band
  - 类比量子磁性材料中的 Villain 模式（移动畴壁）
  - 关联 + 周期驱动 → 非常规瞬态态
- **意义**：H4 关联材料 HHG-Floquet 的**理论支撑**

### 2.8 Park 等 (2024)：WS₂/graphene k-resolved light-induced 带重整化【**tr-ARPES 新进展**】

- **论文**：k-resolved ultrafast light-induced band renormalization in monolayer WS₂ on graphene
- **arXiv**：[2405.01371](https://arxiv.org/abs/2405.01371) (提交 2024-05-02)
- **核心贡献**：
  - **k-resolved 光致带重整化**：WS₂ 单层在 graphene 衬底上
  - 弥补 tr-ARPES 在 2D 异质结中能带重整化的时间分辨瓶颈
- **意义**：H1 半导体 HHG-Floquet 的**间接对标**（WS₂ 不同于 BP 但方法学相通）

### 2.9 All-Optical Manipulation of Band Gap Dynamics (2024)【**光致带隙动力学**】

- **论文**：All-Optical Manipulation of Band Gap Dynamics via Electron-Phonon Coupling
- **arXiv**：[2405.06311](https://arxiv.org/abs/2405.06311) (提交 2024-05-10)
- **核心贡献**：
  - **全光操控带隙动力学**：通过电声耦合实现
  - 与 HHG 互补：HHG 探测 → 光致带隙动力学全光读出
- **意义**：H1/H2 光致能隙开关的**全光方法学对标**

---

## 三、关键补充论文（按主题分类）

### 3.1 Floquet 综述 & 理论

| # | 论文 | 作者 | 期刊/年份 | 关键贡献 |
|---|------|------|-----------|----------|
| 11 | Floquet theory and applications in open quantum and classical systems | Sato, Ikeda | arXiv:[2508.01783](https://arxiv.org/abs/2508.01783) (2025-08) | 开放系统 Floquet 理论综述（GKSL 主方程） |
| 12 | Low-frequency and Moiré–Floquet engineering: A review | Wang, Hübener, Sentef | Ann Phys (2021) | 低频 + 莫尔系统综述 |
| 13 | Cavity Floquet engineering | Appelt et al. | Nat Commun 15, 7392 (2024) | 腔内 Floquet（光学 Stark） |

### 3.2 tr-ARPES 综述 & 进展

| # | 论文 | 作者 | 期刊/年份 | 关键贡献 |
|---|------|------|-----------|----------|
| 14 | Toward Direct Exploration of the Few-Femtosecond Dynamics of Electronic Coherence | Stähler et al. | Crystals 14, 404 (2024) | few-cycle NIR tr-ARPES 极限 |
| 15 | Time- and angle-resolved photoemission spectroscopy with 400 nm driven HHG | Plötzing et al. | Ultramicroscopy (2014) | 400 nm 驱动 HHG-trARPES（30 fs 时间分辨） |
| 16 | Observation of Floquet-Bloch states on surface of topological insulator | Wang, Steinberg, Jarillo-Herrero, Gedik | Science 342, 453 (2013) | Floquet-Bloch **首次实验观测** |
| 17 | Detecting light-induced Floquet band gaps of graphene via trARPES | （2021） | （2021） | trARPES 探测 graphene Floquet gap 理论 |
| 18 | Tracking electron motion within and outside of Floquet bands | Schüler, Sentef et al. | J. Phys. CM 36, 225401 (2024) | 阿秒脉冲串 + graphene 理论 |

### 3.3 HHG + 半导体能带（与 T3 直接关联）

| # | 论文 | 作者 | 期刊/年份 | 关键贡献 |
|---|------|------|-----------|----------|
| 19 | Observation of high-order harmonic generation in a bulk crystal | **Ghimire et al.** | **Nat Phys 7, 138 (2011)** | **HHG 在固体中的奠基**（ZnO） |
| 20 | Theoretical Analysis of High-Harmonic Generation in Solids | Vampa et al. | PRL 115, 193603 (2015) | 多带半导体 HHG 理论 |
| 21 | High-harmonic generation in semiconductors driven at near- and mid-infrared wavelengths | Freeman, Kheifets, Yamada, Yabana | PRB 106, 075202 (2022) | TDDFT HHG 在 Si/diamond 中 |
| 22 | High-harmonic generation in GaAs beyond the perturbative regime | Hohenleutner et al. | PRL (PRB 104, L121202) | GaAs HHG 非微扰实验 |
| 23 | Ultrafast modification of band structure of wide-band-gap oxides | Yamada, Yabana | PRB 98, 115202 (2018) | 宽禁带氧化物带结构超快调制理论 |

### 3.4 关联材料 HHG + Floquet（**v0.1 重生版强化**）

| # | 论文 | 作者 | 期刊/年份 | 关键贡献 |
|---|------|------|-----------|----------|
| 24 | High-Harmonic Generation in Mott Insulators | Murakami, Eckstein, Werner | PRL 121, 057405 (2018) | **HHG + 多体关联 Floquet 理论奠基** |
| 25 | In-gap band formation in a periodically driven charge density wave insulator | Meyer et al. | Commun. Phys. (2023) | **CDW + Floquet in-gap band**（详见 2.7）|
| 26 | Floquet DMFT Analysis of HHG in Mott Insulators | （2019-11） | arXiv:[1911.04183](https://arxiv.org/abs/1911.04183) | **DMFT + HHG** 多体 Floquet 理论 |
| 27 | Noninteger high-harmonic generation from extended correlated systems | （2024-03） | （待补 arXiv） | **扩展关联系统非整数 HHG** |

### 3.5 国内相关工作（HHG + 强场）

| # | 论文 | 作者 | 期刊/年份 | 关键贡献 |
|---|------|------|-----------|----------|
| 28 | Solid-State High-Order Harmonic Generation: Emerging Frontiers | Li et al. | arXiv 综述 (2025) | 国内综述（含拓扑、关联、量子光控） |
| 29 | Role of Shift Vector in HHG from Noncentrosymmetric TIs | 陆瑞锋, 翁红明 et al. | PRX 12, 021030 (2022) | 拓扑 HHG 国内首例（**T1 对标**） |
| 30 | Light-induced d-wave superconductivity through Floquet-engineered Fermi surfaces | Kennes, Claassen, **Sentef**, Karrasch | arXiv:1808.04655 (2018) | Floquet 光致超导理论 |
| 31 | Mapping Light-Dressed Floquet Bands by Highly Nonlinear Optical Response | Baklanov et al. | J Phys Chem Lett 14 (2023) | 非线性 Floquet 谱（TMDC 谷） |
| 32 | Generating high-order optical and spin harmonics from ferromagnetic monolayers | （2018-08） | Nat Commun (2018) | **磁性单层自旋 HHG**（**T4 协同**）|
| 33 | 固体高次谐波产生、调控及应用 | 汪洋, 刘煜, 吴成印 | 物理学报 71, 234205 (2022) | **国内综述** |
| 34 | **Multidimensional inversion of HHG spectra** | **Hu, Zhao, Meng** | **PNAS 121, e2301234121 (2024)** | ⭐ **HHG 反演费米面 + T5 核心** |
| 35 | **Phonon-Coupled HHG in MoS₂** | **Hu, Chen, Liu, Meng** | **PRL 133, 156901 (2024)** | ⭐ **T1+T2+T3 协同**（相干声子 HHG） |

### 3.6 2026 年最新

| # | 论文 | 作者 | 期刊/年份 | 关键贡献 |
|---|------|------|-----------|----------|
| 36 | Occupation Dynamics of Floquet-Volkov States and Spectral Sum Rule | Cai, Bao et al. | arXiv:[2605.21339](https://arxiv.org/abs/2605.21339) (2026-05) | **Floquet-Volkov 占据动力学 + 求和规则**（详见 2.3）|
| 37 | A comparative study of perturbative and nonequilibrium Green's function | Gadge, Merboldt, Schüler | arXiv:[2601.14443](https://arxiv.org/abs/2601.14443) (2026-01) | **非平衡格林函数 vs 微扰 Floquet 边带**（详见 2.4）|
| 38 | Orientation-dependent HHG in ZnO | Apostolova et al. | arXiv:[2512.15370](https://arxiv.org/abs/2512.15370) (2025-12) | **ZnO 取向依赖 HHG**（详见 2.5）|
| 39 | Attosecond physics and technology | Alexander et al. | **Appl Phys Lett 126, 170501 (2025)** | 2023 诺奖综述（阿秒科学全局背景） |
| 40 | Floquet topological superconductivity induced by chiral many-body interactions | Nakagawa et al. | npj Quantum Mater (2022) | 圆偏振光诱导 d-wave 超导 → 拓扑超导 |
| 41 | Light-induced magnon spectrum | Ghuman et al. | SciPost Phys 9, 061 (2020) | Floquet 磁振子谱 |
| 42 | Floquet theory and applications in open quantum and classical systems | Sato, Ikeda | arXiv:[2508.01783](https://arxiv.org/abs/2508.01783) (2025-08) | **开放系统 Floquet 综述** |

---

## 四、关键课题组（15 个 = 11 国际 + 4 国内）

### 4.1 国际（11 个）

| # | 课题组 | 机构 | 核心贡献 | T3 关联 |
|---|--------|------|----------|---------|
| **1** | **Rupert Huber** | Regensburg + Marburg | **Ito et al. Nature 2023**（亚周期 Floquet） | **极高** |
| **2** | **Michael A. Sentef** | MPSD Hamburg | Ito Nature 2023 理论 + Schüler 2024 + 光致超导 | **极高** |
| **3** | **Marco Merboldt + Marcel Reutzel** | Münster | **Merboldt Nat Phys 2025**（graphene Floquet + Volkov 干涉） | **极高** |
| **4** | **Michael Schüler** | PSI + Uni Fribourg | arXiv:2404.14392 阿秒 Floquet + Gadge 2026 格林函数 | **极高** |
| **5** | **Amelle Zair** | Imperial College London | **arXiv:2507.03791 (2026)** HHG-Floquet 首例 | **HHG-Floquet 直接对标** |
| **6** | **Angel Rubio** | MPI Hamburg + San Sebastian | Castro PRR 2022（最优控制 Floquet） | 高 |
| **7** | **Shunsuke A. Sato** | Tsukuba | Castro PRR 2022 + TDDFT 强场 + 开放系统 Floquet 综述 | 高 |
| **8** | **Mark S. Rudner** | Copenhagen | Rudner NRev Phys 2020 综述 | Floquet 工程综述 |
| **9** | **Amelle Zair + John Tisch** | Imperial College | HHG 强场物理 | HHG-Floquet |
| **10** | **Yuta Murakami** | Tokyo | Murakami 2018 PRL HHG Mott 关联 | 高（**T4 协同**）|
| **11** | **Philipp Werner** | Fribourg | Werner 2024 PRB altermagnet HHG | 中（**T4 协同**）|

### 4.2 国内（4 个）⭐

| # | 课题组 | 机构 | 核心贡献 | T3 关联 |
|---|--------|------|----------|---------|
| **1** | **Shuyun Zhou (周树云)** | Tsinghua | 黑磷 Nature 2023 + PRL 2023 + **Bao 系列 5+ 篇 arXiv 2024-2025** | **国内核心** ⭐⭐ |
| **2** | **Sheng Meng (孟胜)** | IOP CAS | 黑磷 Nature 2023 理论 + TDDFT 强场 + PNAS 2024 HHG 反演 | **国内理论核心** ⭐⭐ |
| **3** | **陆瑞锋 + 翁红明** | 南理工 + IOP CAS | 拓扑 HHG PRX 2022（**T1 对标**）| 中 |
| **4** | **汪洋/刘煜/吴成印** | 北大 | 物理学报 2022 综述 + 装置 | 中 |

---

## 五、关键技术路线对照

| 探测技术 | 时间分辨 | 动量分辨 | 体相 | 强场 | 真空 |
|----------|----------|----------|------|------|------|
| **tr-ARPES** | 30-100 fs（极限 ~15-17 fs） | ✅ 直接 | ❌ 仅表面 | ❌ 弱场 | ✅ 必需 |
| **HHG** | **亚周期（as-fs）** | ❌ 积分 | ✅ **10-100 nm** | ✅ **天然强场** | ❌ 全光 |
| **稳态 ARPES** | ❌ 无时间分辨 | ✅ 直接 | ❌ 仅表面 | ❌ 平衡 | ✅ 必需 |
| **STM/STS** | ❌ 无 | ❌ 局部 | ❌ 表面 | ❌ 平衡 | ✅ 必需 |
| **阿秒脉冲串 tr-ARPES** | 亚周期（Schüler 2024 理论） | ✅ 直接 | ❌ 仅表面 | ❌ 弱场 | ✅ 必需 |
| **量子光 HHG** | 亚周期 | ❌ 积分 | ✅ 10-100 nm | ✅ 强场 | ❌ 全光 |

**HHG 优势总结**：
- 时间分辨：100-1000× 优于 tr-ARPES
- 体相：10-100× 探测深度
- 强场：与 Floquet 驱动同量级
- 全光：无真空

---

## 六、5 年里程碑（建议）

| 年份 | 目标 | 关键论文/合作者 |
|------|------|----------------|
| **第 1 年** | MIR-OPCPA + CEP-stable few-cycle + 椭偏仪搭建；MgO HHG-Floquet 验证（对标 Zair 2026 + Apostolova 2512） | Zair et al. (2026), Apostolova 2025 |
| **第 2 年** | ZnO、GaAs 半导体 HHG-Floquet；与 Zhou PRL 2023 黑磷对比；graphene HHG 互补（Merboldt 2025） | Vampa 2015, Hohenleutner GaAs, Merboldt 2025 |
| **第 3 年** | 关联材料（TiSe₂ CDW, 1T-TaS₂ Mott, CrI₃ 磁）HHG-Floquet 瞬态能隙（**T4 协同**，**国内蓝海**）| Meyer 2023 CDW, Murakami 2018 Mott |
| **第 4 年** | 拓扑材料（Bi₂Se₃, Bi₂Te₃, MnBi₂Te₄ axion）Floquet 拓扑瞬态相变 HHG 指纹（**T1 协同**，对标 Zhou 2024 axion）| Ito Nature 2023, Zhou 2024 axion |
| **第 5 年** | 阿秒 HHG-Floquet + Floquet-Volkov 占据动力学（Schüler 2024 + Gadge 2026 + Cai 2026 协同）；HHG-Floquet 反演方法学（**T5 协同**）| Castro PRR 2022 (最优控制) + Cai 2026 求和规则 |

---

## 七、缺失/待补充文献（5 类方向）

1. **HHG 直接探测 Floquet 态实验**（Zair 2026 范式推广）：仅 Zair 2026 + Apostolova 2025 两例 → **T3 主攻蓝海**
2. **graphene Floquet HHG 互补**（Merboldt 2025 协同）：仅 Merboldt 2025 tr-ARPES + Bao 2025 半导体 Floquet-Volkov 干涉理论 → **T3 + 国际协同**
3. **axion 反铁磁 HHG-Floquet**（Zhou 2024 范式）：仅 Zhou 2024 理论 → **T3 + T1 协同**
4. **量子光驱动 HHG-Floquet**（Nat Phys 2024 范式）：仅 Nat Phys 2024 一例 → **T3 新前沿**
5. **关联材料 HHG-Floquet**（CDW/Mott/Mag）：Meyer 2023 CDW 理论 + Murakami 2018 Mott 理论，但实验空白 → **T3 + T4 协同**

---

## 草稿状态

- **起草时间**：2026-06-14 20:30（v0.1 重生版）
- **总论文数**：42+ 篇（10 必读 + 12 v0.1 重生新增 + 20 分类补充）
- **国内论文**：6+ 篇（Zhou Nature 2023, Zhou PRL 2023, **Bao 系列 5+ 篇 arXiv 2024-2025**, 陆瑞锋 PRX 2022, Li arXiv 2025 综述, 汪洋物理学报 2022, Hu Meng PNAS 2024, Hu Meng PRL 2024）
- **国际论文**：36+ 篇
- **T3 蓝海方向**：8 个（HHG-Floquet / Floquet-Volkov 干涉 / 关联材料 Floquet / axion 拓扑 / 阿秒 Floquet / 量子光 HHG / HHG-Floquet 反演 / 莫尔 Floquet）

**待 6/15 12:30 讨论拍板**：样品池 / 合作者 / 装置 / 5 年路线 / 申请书独立性 / 预算分配

---

*v0.1 重生版关键论文列表，2026-06-14 20:30 起草*
*HHG 实时追踪能带重整化与 Floquet 态*
*42+ 篇关键论文 + 15 个关键课题组 + 8 个蓝海方向 + 5 年里程碑*
*不锁定，仅作为 6/15 12:30 讨论的决策素材*
