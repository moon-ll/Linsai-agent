# 方法学手册

## 概述

本手册为申请书正文的方法学细节补充，包含：理论模型的适用条件与失效边界、TDSE 数值模拟参数设计、误差评估协议、探测器规格参数表、以及全文技术路线图的纯文字版描述。申请书重思路重论证，细节归属本手册。

---

## 1. 理论模型适用条件与失效边界

### 1.1 多通道耦合条纹信号模型（对应 R1）

**物理出发点**：光电离的量子力学描述——光电子在 XUV 脉冲与 IR 条纹场联合作用下的最终动能为

$$E_{\mathrm{final}} = E_{\mathrm{kin}} + U_{\mathrm{p}} \sin^2(\omega t + \phi_{\mathrm{CEP}}) + \vec{A}(t) \cdot \vec{k}$$

其中 $E_{\mathrm{kin}}$ 为无场光电子动能，$U_{\mathrm{p}}$ 为有质动力势，$\vec{A}(t)$ 为 IR 场矢势，$\vec{k}$ 为光电子动量。

**适用条件**：
- 通道间能量差大于 1 eV（保证波函数在能量域可分离）
- 通道重叠宽度在 0.5–2 eV 区间（典型 C K 边附近多通道构型）
- 电离过程为准单电子近似（多通道效应表现为不同电离阈的贡献叠加，而非能带结构效应）

**失效边界**：
- 通道间强耦合导致波函数混合显著时（能量差小于 0.5 eV），双通道近似退化为单通道，修正项形式需重新标定
- 当通道重叠宽度超过 2 eV 时，干涉项的余弦形式近似不再成立

### 1.2 解析修正项的数学形式（对应 R1）

干涉项数学形式以通道间相位差 $\Delta\phi$ 与通道强度比 $R = I_2/I_1$ 为参量：

$$S(E) = S_1(E) + S_2(E) + 2\sqrt{S_1 S_2}\cos(\Delta\phi)$$

其中第三项为干涉项。成立前提：两通道电子波包须相干叠加，谱上重叠宽度不小于相干宽度。

**修正项有效性的数值判据**（模拟端）：重构脉冲与 TDSE 输入真值的均方根相位误差小于 5%。

### 1.3 角积分偶极相位压制（对应 R2）

理论预估角积分可将偶极相位贡献压制至小于 2%，此时脉冲包络信息可以被独立提取。该估计来自 Pabst & Dahlström (2016) 的角动量量子力学对称性分析。

**失效条件**：角积分残余偶极相位贡献大于 5% 时，触发 CNN 备选方案。

---

## 2. TDSE 数值模拟参数设计

### 2.1 双通道耦合基准模拟

| 参数 | 数值 | 说明 |
|------|------|------|
| 通道组合 | C 2s / N 2s | 模拟 C K 边 284 eV 和 N K 边 409.7 eV |
| 通道间能量差 | 1–2 eV | 典型 K 边邻近双通道构型 |
| 通道重叠宽度 | 0.5–2 eV | 视具体能区靶材调整 |
| 驱动激光波长 | 800 nm（Ti:sapphire） | 基准参数 |
| 条纹场强度 | 5×10¹¹ W/cm² | 典型条纹场参数 |
| 脉冲宽度 | 300 as（XUV）+ 30 fs（IR） | 对应实验室参数 |

### 2.2 三通道扩展模拟（参数扫描）

在双通道基准附近扩展参数空间：

- 通道数：2–3（第三通道为 C 2p 或 N 2p）
- 能量范围：284–409.7 eV
- 重叠度：0.5–2 eV（逐 0.25 eV 扫描）
- 通道混合度：以通道投影算子衡量

### 2.3 计算成本估算

双通道基准点（2 通道 × 3 能量 × 3 重叠度）共 18 个参数点，每点 TDSE 传播约 200 CPU-hours（三维球坐标格点），总计算量约 3600 CPU-hours。三通道扩展模拟在基准数据库建立后选择性验证，额外计算量约 1000 CPU-hours。

---

## 3. 探测器与实验平台参数

### 3.1 位置灵敏探测器（TOF 阵列）

| 参数 | 数值 |
|------|------|
| 通道数 | 16 |
| 能量分辨率 | ΔE/E ≈ 1% @ 400 eV |
| 角向覆盖 | 360°（全圆周） |
| 时间分辨率 | < 100 as RMS（延迟稳定度） |
| 单通道 @ 400 eV 能量分辨率 | 约 4 eV |

### 3.2 两套光源平台

**极紫外平台**：
- 中心能量：100 eV
- 脉冲宽度：小于 300 as
- 驱动激光：1 kHz Ti:sapphire（30 fs，3 mJ/pulse）

**软 X 射线平台**：
- 方案：高次谐波产生 + 碳 K 边增强构型
- 覆盖范围：水窗（284–409.7 eV）及更高能区

---

## 4. 误差评估协议

### 4.1 多通道修正算法误差评估（R1）

终止判据：重构误差从大于 20% 降至小于 5%

**误差定义**（模拟端）：$\delta_{\mathrm{RMS}} = \sqrt{\langle(\phi_{\mathrm{recon}} - \phi_{\mathrm{TDSE}})^2\rangle}$，以 TDSE 输入脉冲相位为真值

**误差定义**（实验端）：拟合残差（r.m.s.）与 Cousin et al. PRX 7, 041030 (2017) 公开数据组的偏差

### 4.2 角积分偶极相位压制效率评估（R2）

终止判据：跨靶材可比性误差小于 5%

**可比性误差定义**：同脉冲条件下不同靶材（Ar, Kr）提取的脉冲包络之间的 r.m.s. 偏差，阈值为 5% 相对峰值强度

### 4.3 跨能区误差图谱（R3）

自变量：光子能量区间（极紫外 50–150 eV / 水窗 284–409.7 eV / 软 X 射线 409.7–543 eV）、通道重叠宽度（eV，对应多通道贡献百分比）

因变量：修正算法与传统 FROG-CRAB 的偏差

合格阈值：小于 5%

失效边界：光子能量超过 409.7 eV（N K 边电离阈值）或通道重叠宽度超过 2 eV（对应多通道贡献超过 50%）

---

## 5. 参考文献真实性核查状态（本章修订后）

|| [N] | 条目 | 核查状态 |
|-----|------|---------|
| [1] | Goulielmakis et al. Nature 2010 | ✓ 真实（Crossref验证） |
| [2] | Cousin et al. PRX 2017 | ✓ 真实（Crossref验证） |
| [3] | Pabst & Dahlström PRA 2016 | ✓ 真实（Crossref验证） |
| [4] | Schultze et al. Science 2010 | ✓ 真实（Crossref验证） |
| [6] | Mairesse & Quéré PRA 2005 | ✓ 真实（Crossref验证） |
| [8] | Krausz & Ivanov RMP 2009 | ✓ 真实（Crossref验证） |
| [9] | Ren et al. J Opt 2018 | ✓ 真实（Crossref验证） |
| [11] | Peschel et al. Nat Commun 2022 | ✓ 真实（Crossref验证） |
| [12] | Inzani et al. J Phys Photonics 2024 | ✓ 真实（Crossref验证） |
| [13] | Zhu et al. Chin Phys B 2026 | ✓ 真实（Crossref验证） |
| [14] | Hutcheson et al. PR Research 2025 | ✓ 真实（Crossref验证；DOI小写属APS风格等价格式） |
| [15] | White J, Chang Z. Opt Express 2019 | ✓ 真实（Crossref验证） |
| [17] | Itatani et al. PRL 2002 | ✓ 真实（Crossref验证） |
| [18] | Agostini & DiMauro RPP 2004 | ✓ 真实（Crossref验证） |
| [19] | Ishii et al. Nat Commun 2014 | ✓ 真实（Crossref验证） |
| [20] | Popmintchev et al. Science 2012 | ✓ 真实（Crossref验证） |
| [21] | Corkum PRL 1993 | ✓ 真实（Crossref验证；期刊无DOI，INSPIRE-HEP已附） |
| [22] | Keldysh JETP 1965 | ✓ 真实（经典无DOI，INSPIRE-HEP已附） |
| [24] | Eckle et al. Science 2008 | ✓ 真实（Crossref验证：DOI 10.1126/science.1163439；作者8人全列） |
| [25] | Villeneuve et al. Science 2017 | ✓ 真实（Crossref验证） |
| [26] | Klünder et al. PRL 2011 | ✓ 真实（Crossref验证） |
| [27] | Pazourek et al. RMP 2015 | ✓ 真实（Crossref验证） |
| [28] | Kuzkova et al. arXiv:2508.15076 2025 | ✓ 真实（作者6人全列，已核实） |
| [29] | Li et al. Light Sci Appl 2024 | ✓ 真实（Crossref验证；作者前5已列） |
| [30] | Ortmann & Landsman RPP 2024 | ✓ 真实（Crossref验证；新增） |
| [31] | Kim et al. Opt Lett 2025 | ✓ 真实（Crossref验证；新增） |
| [32] | Hajivassiliou et al. NJP 2023 | ✓ 真实（Crossref验证；新增） |
| [33] | Kheifets et al. PRA 2026 | ✓ 真实（Crossref验证；新增） |

**本轮已删除条目**（critical 伪造/错位）：[16]（原虚构 Liu Science 2025）、[23]（原 Itatani DOI 错位至植物学论文）、原 [30]（原虚构 Silva Nat Photonics 2025）、原 [31]（原虚构 Murari Opt Express 2025）、[32]（原 Bizau DOI 错位至冷原子论文）、[33]（原 Hu DOI 错位至双俄歇论文）、[34]（原 Chen 作者虚构）、[35]（原 Brown 重复引用 + 虚构）、[36]（原 Li 作者虚构）

**本轮新增条目**（2026-08-26 Crossref验证）：[30] Ortmann RPP 2024、[31] Kim Opt Lett 2025、[32] Hajivassiliou NJP 2023、[33] Kheifets PRA 2026

**近3年文献占比**：2023-2026年文献共 9 条（[12][13][14][28][29][30][31][32][33]），占总文献 33 条的 27.3%，较上轮 20.8% 显著提升。
