# 课题方法素材包（KB 自动聚合，v7.2.30 wikilink 节点格式）

- 课题：general-berry-berry-20261107
- 生成时间：2026-11-20T11:41:00Z
- 方法关键词：THz、三阶反常霍尔测量、不含实验测量、中电场连续调控、为螺旋度分辨测量、也缺少独立于计算、件下被重构与调控、几何量的调控、向非线性霍尔测量、在强场与光场调控、太赫兹发射谱测量、定共享同一组计算、异质结中应变调控、拟采用技术

> 用途：update_method_manual / writer 写方案时的可实施细节来源。
> **v7.2.30 起改 wikilink 节点格式**：每条方法/参数都附 `[[方法页slug]]` 双向链接，
> writer 落盘后由 `kb_pack_wikilink_guard.py` 校验（≥3 引用为达标）。
> 参数必须按参数溯源纪律标注来源；本包为 KB 索引摘要，取参数前读对应页原文。

## 一、匹配的知识库方法页（6）

### [[methods/thz-spectroscopy|thz-spectroscopy]]
页：knowledge/wiki/methods/thz-spectroscopy.md
摘要：THz spectroscopy uses ultrashort strong-field THz pulses to resonantly excite infrared-active phonons for time-resolved detection of lattice/magnetic low-energy dynamics, with 2D THz spectroscopy mapping diagonal and cross peaks to separate linear phonon response from nonlinear phonon–phonon/phonon–magnetic coupling channels (as in FePS3, where an IR-active phonon nonlinearly displaces the 3.27 TH

### [[methods/实时_DMFT_与中红外强场实验联合分析|实时 DMFT 与中红外强场实验联合分析]]
页：knowledge/wiki/methods/实时_DMFT_与中红外强场实验联合分析.md
摘要： > ⚠ **状态标注（2026-11-01 颗粒度体检）**：本页正文素材不足以支撑「参数表≥5行」的达标线（指导学生复现），如实保持低密度工作页状态，待深读素材回补后升级。已在专题关联网络中。 将中红外强场实验与实时 DMFT 结合，用于识别亚周期 Mott 熔化、高阶谐波红移及 doublon-holon 复合激发引起的瞬时能带重整。  ## 参数表  **终极升级**（2026-11-01，canonical 要素，引用已核实/库内锚）： 实时 DMFT（tdDMFT）与中红外强场实验的联合分析：tdDMFT 把强关联晶格映射为含时自洽杂质问题，直接预言中红外驱动的 Mott 体系谐波

### [[methods/sp-stm|自旋极化扫描隧道显微镜（SP-STM）准粒子干涉成像]]
页：knowledge/wiki/methods/sp-stm.md
摘要：自旋极化扫描隧道显微镜（SP-STM）准粒子干涉成像以磁化针尖实现自旋分辨的局域态密度（LDOS）成像，通过读取实空间LDOS振荡（Friedel振荡）的几何振幅，将其转换为动量空间的量子几何信息（如量子度规），是拓扑绝缘体等体系全量子几何张量测量的核心实验载体与探测手段。  ## 参数表  **库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）： | 价带偏移 VBO（实验） | 0.83 eV | 主要发现与核心结论  | 导带偏移 CBO（实验） | 0.76 eV | 主要发现与核心结论  | VBO（DFT 计算） | 0.94 eV | 主要发现与核心结论  | 能带模型 | Bistritzer-MacDonald 连续模型：v_F=2.34a eV、w₀/w₁=0.78、θ_mag≈1.12°；8 轨道 Wannier 拟合（跃迁截断 10 个

### [[methods/磁空间群对称性与线性自旋波建模|磁空间群对称性分析与线性自旋波建模]]
页：knowledge/wiki/methods/磁空间群对称性与线性自旋波建模.md
摘要：基于磁空间群/磁点群对称性分析判定系统对称性允许的相互作用项与序参量约束——例如亚晶格间旋转型联系操作使轨道矩可存活而自旋矩严格补偿、并约束轨道矩方向，以及制约手性劈裂与非互易色散的允许项——进而以线性自旋波建模定量拟合THz磁子色散，支撑实验判读。  ## 参数表  **终极升级**（2026-11-01，canonical 要素，引用已核实/库内锚）： 磁空间群（MSG）对称性 + 线性自旋波（LSWT）建模的组合方法：以 MSG 约束磁振子色散的对称允许形式，LSWT 给出定量色散/谱强，用于交磁体/多 Q 磁序的低能模型锚定——对称性层与动力学层的接口方法。  | MSG 约束 | 磁振子色散 ω(q) 须满足 MSG 不变量 | [[对称性与群论选择定则]] | | LSWT | HP 变换 + 单 Q 非公度通式（SpinW 实现） | [[lswt]] | | 交磁应用 |

### [[methods/dmft|dmft]]
页：knowledge/wiki/methods/dmft.md
摘要：DMFT 将晶格强关联电子模型以局域自能自洽映射为 Anderson 杂质模型（量子杂质问题），是揭示单轨道 Hubbard 模型中隐藏 Kondo 晶格结构的核心工具，既可在模型层面解析 U 驱动的金属–绝缘体相变与轨道选择性 Mott 转变全相图，也可经非平衡/含时扩展计算 Mott 体系 THz 非线性光学响应（AFM 绝缘相谐波由自旋-电荷/轨道-电荷耦合主导、金属相来自重整化带内电流等相区依赖机制仍然成立）；结合 cRPA 的 DFT+DMFT 可进一步从第一性原理建立晶格畸变与关联的定量联系：CDW 振幅通过改变轨道局域化与电子屏蔽调制有效 Hubbard U，使 Hubbard 带随 CDW 振幅协同移动，减小畸变可驱动 Mott 绝缘体向关联金属转变（如单层 1T-TaS2），为光控二维关联相提供微观机制。  ## 参数表  | 参数 | 数值 | 出处 | | --- |

### [[methods/122|122个磁点群对称性分类]]
页：knowledge/wiki/methods/122.md
摘要：将晶体点群扩充时间反演（灰色/黑白）操作后按122个磁点群分类，对各阶非线性响应张量（三阶THG极化率χ^(3)、二阶纵向非线性电导、霍尔张量等）做完备群论约化，由磁结构与Néel矢量取向给出每个磁点群下各张量元素的允许/禁戒选择定则，并可延伸至PT对称下层分辨量子几何量（贝里曲率及贝里曲率偶极、量子度规偶极）的存活判据与电场奇偶性判定。  ## 参数表  | 参数 | 数值 | 出处 | | --- | --- | --- | | 磁点群总数 | 122个 | 2025-2506.27548 | | THG分析张量阶数 | 3阶（χ^(3)） | 2025-2506.27548 | | 纵向非线性电导分析张量阶数 | 2阶 | 2025-2505.15016 |  **库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）： | 数值参数 | t = 1，λ =

## 二、带方法卡的论文页（6）

### [[papers/2026-2607_28491-drumhead-surface-states-of-rhombohedral-graphite-with-near-i|菱方石墨鼓面态近理想量子几何的第一性原理核验（DFT+Wannier+Wilson loop+Kubo QGT 空间分辨）]]
页：knowledge/wiki/papers/2026-2607_28491-drumhead-surface-states-of-rhombohedral-graphite-with-near-i.md
参数样例：参数；---；计算设置；DSS 曲率定量

### [[papers/2025-2508_00296-tracking-doublon-holon-dynamics-in-high-harmonic-generation|Sr₂CuO₃ Mott 绝缘体 HHG 中 doublon-holon 动力学的亚周期追踪（反射 HHG + tr-反射 + tdDMFT/NCA）]]
页：knowledge/wiki/papers/2025-2508_00296-tracking-doublon-holon-dynamics-in-high-harmonic-generation.md
参数样例：参数；---；MIR；tdDMFT 参数

### [[papers/2026-2607_13863-ultrafast-altermagnetophononics|第一性原理 + 自旋群对称性分析 + 非平衡晶格动力学 + 双色 THz 和频激发方案（超快交变磁声子学）]]
页：knowledge/wiki/papers/2026-2607_13863-ultrafast-altermagnetophononics.md
参数样例：参数；---；双色 THz 频率；泵浦偏振

### [[papers/2026-2601_02481-an-altermagnetic-materials-library-in-intercalated-transitio|插层过渡金属双硫属化物交变磁材料库的系统 DFT 筛选（T_yMX₂：VASP PBE+U+D3+对称性判据）]]
页：knowledge/wiki/papers/2026-2601_02481-an-altermagnetic-materials-library-in-intercalated-transitio.md
参数样例：参数；---；DFT 设置；筛选空间

### [[papers/2503.14531|Van Vleck 传播子强场近似（Van Vleck-propagator SFA，含边界与镜像势的 MIM 结强场输运模型）]]
页：knowledge/wiki/papers/2503.14531.md
参数样例：参数；---；zeta 参数（纳米结尺寸判据）；Herink 空间受限长度参数 δ

### [[papers/2023-2306_09766-ultrafast-switching-of-topological-invariants-by-light-drive|光致应变诱导拓扑不变量超快切换（Bi₂Se₃：光泵浦 → 面外应变 → Z₂ 瞬态翻转 → 相干电导读出）]]
页：knowledge/wiki/papers/2023-2306_09766-ultrafast-switching-of-topological-invariants-by-light-drive.md
参数样例：参数；---；应变与翻转
