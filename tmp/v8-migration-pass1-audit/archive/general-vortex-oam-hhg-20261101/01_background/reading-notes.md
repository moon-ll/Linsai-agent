## 2509.06430

**标题**：Perfect spatiotemporal optical vortex driven high harmonic generation
**作者**：C. Granados, B. Kumar Das, W. Gao（Eastern Institute of Technology, Ningbo；Jena；ELI ALPS）
**出处**：arXiv:2509.06430（2025-09-08），Optica（preprint, opticajournal）

### 研究问题（Research Question）
完美时空光学涡旋（PSTOV）光束能否作为驱动源，在原子气体中通过高次谐波发生（HHG）产生携带高拓扑荷（TC）的极紫外（XUV）谐波？具体要回答：横向 OAM 是否严格守恒、各级谐波的远场发散是否一致、以及 PSTOV 独特时空特性如何体现在近场时空谱（spatiospectral）结构中。

### 研究背景（Background）
携带 OAM 的涡旋光驱动 HHG 已在原子气体与固体中确立 OAM 缩放律 l_q = q×l 与"不同谐波发散相近"两条基本结论，主流模型为薄膜模型（TSM）+ Fraunhofer 衍射积分。空间涡旋（Laguerre-Gaussian / Bessel-Gauss）的束径随 TC 单调增大，是获得高 TC 谐波的根本障碍；完美空间涡旋（POV）用 TC 无关的环半径与环宽化解该问题并已被用于 HHG。时空涡旋（STOV）把 OAM 放在垂直于传播方向上，并天然携带时空耦合（STC）；实验上近期刚实现 PSTOV，且已有研究证实 STOV 驱动 HHG 中横向 OAM 守恒，但 STOV 的非线性过程、其时空特征如何映射到谐波仍鲜有研究。

### 研究方法（Methods）
纯理论建模（无实验）。基频 PSTOV 场写作 E = E₀exp(−iΦ)exp(−((r_xτ − r₀)/δ)²)，螺旋相位 −lφ = −l·arctan(w_xτ/w_τx)；原子气体目标用薄片模型（TSM）处理，忽略纵向相位匹配、保留横向相位匹配，谐波幅度取基频场的 p 次幂、总相位 Ψ_q = qΦ − α_q I_PSTOV（因偶极相位贡献比螺旋相位弱近一个数量级而忽略）；远场用 (x′−t′) 域的 Fraunhofer 衍射积分求 (β_x − ω) 域复振幅。数值参数：λ = 800 nm、l = 1 或 5、r₀ = 3 a.u.、δ = 0.3 a.u.、w_x = 1 a.u.、w_τ = 411 a.u.，p ≈ 3（由 I = 0.87–1.7×10¹⁴ W/cm² 范围内改变驱动强度标定）。

### 主要发现与核心结论（Main Results）
1) PSTOV 的时空幅度在 r₀ ≫ δ 渐近极限下与 TC 无关，l = 1 与 l = 5 的环半径、环宽与整体强度分布不变，TC 只能由相位图沿方位角数 2π 相移数读取（l = 1 相位图中的弯曲线源于空间与时间宽度之差）；但非渐近时高 TC 下幅度将重新依赖 TC。
2) 近场时空谱呈倾斜瓣状（tilted lobed）结构，第 q 阶谐波在主瓣之间出现 q 个极小，对应 l_q = ql（如 17 阶 → l = 17），即 OAM 缩放律在 STOV 驱动 HHG 中严格成立。
3) 远场 (β_x − ω) 域中，17/19/21 阶谐波的最大强度环横纵半径相近，即不同谐波发散相近、总环数相同（由 r₀ 决定），从而在远场生成 Bessel-Gauss 时空光学涡旋（Be-STOV）；低阶（微扰区）同样产生 Be-STOV。
4) 时空耦合在近场表现为空间啁啾 x_P(ω_q) = (n r₀ w_x w_τ)/(δ l c)·ω_q，本例 n = 0.9；只有在傅里叶积分中严格使用谐波能量 ω_q = qω（而非 ω）时啁啾斜率才与谐波阶数无关，否则将违反能量守恒。
5) 提升基频 TC 至 l = 5 时环半径与环宽几乎不变，但外环数量骤减（17/19 阶仅剩一条外环，21/23 阶无外环），谐波涡旋垂直环半径约为 l = 1 情形的 4 倍；高阶谐波的外环强度急剧下降。

### 潜在研究方向（Future Directions）
本文为纯理论工作，全部结论依赖 TSM 的偶极近似与 p ≈ 3 的固定标度因子，缺少实验验证与固体目标的检验。作者指出可延伸至固体靶中 STOV 的产生，研究电磁场拓扑与材料拓扑的耦合，并利用自旋—轨道角动量在非共线几何下的相互作用产生时空阿秒脉冲列；由于各阶谐波远场发散相近、空间重叠好且可聚焦，这些远场性质可用于产生时空光弹簧（light springs）。方法学上，POV 与 Bessel-Gauss 在空间及时空域互为傅里叶对这一性质是次级环结构的成因，值得进一步挖掘。

---


## 2607.23652

**标题**：Carrier–Envelope Phase Control of Orbital Angular Momentum in Solid-State High-Harmonic Generation
**作者**：Camilo Granados, Rajaram Shrestha（共同一作）, Bikash Kumar Das, Debobrata Rajak, Eric Cormier, Bálint Kiss, Carmelo Rosales-Guzman, Wenlong Gao（Eastern Institute of Technology Ningbo / ELI ALPS / FSU Jena / LP2N Bordeaux / CIO León）
**出处**：arXiv:2607.23652（2026-07-26），Optica Open preprint（2026-07-29）

### 研究问题（Research Question）
在少周期（few-cycle）涡旋脉冲驱动的固体 HHG 中，是否存在一个纯粹的时间自由度（载波包络相位 CEP）能够突破由旋转对称性与角动量守恒锁死的 OAM 缩放律 l_q = q×l，直接调控探测器有限光谱窗口内所测得的谐波拓扑荷（TC）？作者的答案是肯定的，但强调必须同时满足两个条件：晶体反演对称性破缺 + CEP 敏感的亚周期电子动力学。

### 研究背景（Background）
OAM 缩放律 l_q = q×l 已在原子气体与固体 HHG 中被广泛实验确认（Gauthier 2017 Nat. Commun.、Gariepy 2014 PRL、固体侧 Gauthier 2019 Opt. Lett.、Nagai 2024 Sci. Adv. 等），被视为涡旋驱动 HHG 的基本对称性约束。同时 CEP 对谐波强度、频谱结构、偏振与发射时刻的控制在原子与固体体系均已系统研究，理论上亦已预言少周期 OAM 脉冲可操控气体中谐波涡旋的 OAM 内容，但此前无论气体还是固体都缺乏实验证据。核心张力在于：旋转对称性锁定每一阶谐波的 OAM，而 CEP 直接支配亚周期电子动力学——"纯时间自由度能否改变空间拓扑结构"是本文要回答的开放问题。

### 研究方法（Methods）
实验在 ELI ALPS 的 MIR 实验室完成。OPCPA 中红外激光（中心波长 3200 nm，100 kHz，脉冲能量 100 µJ，4 周期输出）经专门优化的压缩级压缩至 16 fs（≈1.5–1.6 周期，TIPTOE 测量），再经螺旋相位板（SPP）产生 TC = 1 的涡旋束；用光学窗口加色散控制脉宽：全压缩 16 fs、4 mm CaF2 半拉伸 77.2 fs（7.2 周期）、7 mm CaF2 + 6 mm BaF2 拉伸 186 fs（17.4 周期）、未压缩 45 fs（4 周期）。CEP 由 AOPDF（Dazzler, Fastlite）主动设定并经 f-to-2f（Fringeezz）闭环反馈稳定，残余 CEP 抖动 < 150 mrad RMS，扫描从 −π 到 π 共 31 个等间距步长（步进 0.2 rad）。目标为 a-cut ZnO（50 µm、200 µm）与 c-cut ZnO（50 µm），150 mm 焦距 OAP 聚焦（焦斑约 50 µm），基频用 1 cm BK7 隔离；Avantes 光谱仪（200–1260 nm）做 CEP 扫描，Basler acA1440 相机（400–1000 nm）配单柱面镜做 HG 倾斜瓣型 OAM 分析（数主瓣间极小数即 TC），20 nm 带宽带通滤波（中心 550 ± 20 nm，落在 H5 与 H7 之间、偏近 H6）选取谱窗。理论侧用含复跃迁偶极矩 d(k) = |d(k)|e^{iΦ(k)} 的一维半导体 Bloch 方程（SBE）计算 HHG 光谱，并建立 TSM 扩展的两阶相干叠加模型，把带通滤波投影为复权重 a_q(φ) = |a_q|e^{i(qφ+χ_q)}，测得 TC 由绕数分析给出：ℓ = q×l 或 (q+n)×l，取决于哪个 OAM 分量在谱窗内占优。

### 主要发现与核心结论（Main Results）
1) 少周期（≈1.5 周期）3.2 μm 涡旋束驱动 ZnO HHG 时，测量 TC 强烈依赖 CEP，在相邻整数间切换：φ = 0 时 l_q ≈ 6，φ = π 时 l_q = 5（驱动 TC = 1，H5 与 H6 分别为 5 与 6，符合 q×l 的单阶取值）。
2) 效应需两个"配料"同时具备：(i) 晶体反演对称性破缺（a-cut ZnO 产生偶次谐波，把相邻阶间距压到 n = 1，使谱窗内相邻阶重叠）；(ii) CEP 敏感的亚周期电子动力学（仅少周期脉冲具备）。SBE 计算显示只有引入复偶极矩（而非常规实偶极模型）才出现 CEP 依赖的相邻阶谱权重再分配，实偶极模型预言 CEP 不敏感。
3) 对照实验证实边界：c-cut ZnO（保留反演对称性，仅奇次谐波）CEP 扫描无对角极大特征、无 TC 切换；4 周期（45 fs）长脉冲与拉伸至 17.4 周期（186 fs）时 CEP 效应被完全抑制，此时可得到单一确定 TC 的谐波涡旋（近完美连续环）。
4) 物理图像：每一阶谐波单独仍严格满足 l_q = q×l，切换源于 CEP 控制的相邻阶谱权重再分配改变了探测窗内的主导 OAM 通道；相对相位 Δφ_rel(φ) = nφ + Δφ_0。
5) 全压缩（谱过宽、数阶重叠）时出现分数拓扑荷（旋转对称性破缺、暗径向开口）；引入中等啁啾收窄重叠区后切换表现为干净的相邻整数跳转。50 µm 厚晶体需不同啁啾量（1 mm BaF2，≈68 fs）才显现同等效应，TC 从 l_q = 5 变为 l_q ≈ 6（Δφ = π）；aZnO 转 90°（抑制偶次谐波）后切换被压制。
6) 反射与吸收对高阶 SHG 信号的影响需数值修正（2ω_LO 延迟 −4.5°、2ω_SAM 延迟 +4.1°、邻层引入 −1.5°/+2.1°，使 MoS2 相位改变 +3.6°）；啁啾不改变泵浦功率谱，只在时域展宽脉宽，由时带宽极限使谐波线宽 Γ_q 变窄从而减少相邻阶重叠。

### 潜在研究方向（Future Directions）
当前结论仅限于所探测的 550 ± 20 nm 谱区与检测系统灵敏度范围，且不同厚度晶体需匹配的啁啾条件——把同一机制推广到高次谐波（相邻阶同样重叠）即可实现 XUV 波段的波形控制与波形工程化结构化阿秒光源。作者亦指出"各层独立、无耦合"图景在激子共振附近与高通量极限失效，以及分数拓扑荷的产生机理与可否在更短波长（数纳米）范围获得仍是开放问题。技术上，20 nm 带通滤波 + 时空分离假设（未引入紧聚焦造成的时空耦合）限制了更精细的谱分辨 OAM 测量。


---

## 2505.21922（定向检索新增，2026-11-11）

**标题**：Dual-Polarization Second Harmonic Generation Interferometry for Imaging Antiparallel Domains and Stacking Angles of 2D Heterocrystals
**作者**：Juseung Oh, Wontaek Kim, Gyouil Jeong, Yeri Lee, Jihun Kim, Hyeongjoon Kim, Hyeon Suk Shin, Sunmin Ryu
**出处**：arXiv:2505.21922（2025-10-20），ACS Nano

### 核心结论
提出双偏振谱相干涉法（DP-SPI）与含该观测量的广义 SHG 叠加模型，克服传统仅测强度偏振测量无法分辨反平行畴、无法描述范德华复合晶体的缺陷。以干涉偏振法成像单层 TMDC 反平行畴，并由 TMD 异质双层的干涉图反演各层取向与堆叠角。方法的适用范围直接关联 D3h/C3h 点群下的 SHG 偏振选择规则。

### 与课题关联
为本课题分方向三的交叉标定路径提供独立方法学支撑：二次谐波极图不仅给出极性轴方向，还可分辨单层样品的取向差异，因而可作为层析反演的外部参照。本轮据此把 G3 判据中原先无容差的"与 X 射线衍射和二次谐波极图一致"改写为可检验的方位角容差。

### 已引用位置
申请书（二）研究内容 §二.4 分方向三（层析协议与外部参照段）与 §二.0 G3 判据、§二.6 目标（6）；（三）研究方案 §三.5、§三.8（3）；全文逻辑骨架统一表述表；课题设想验收判据 7。

---

## 2607.19937（定向检索新增，2026-11-11）

**标题**：Symmetry-Based Design Rules for Second-Harmonic Generation in Stacked and Twisted MoS2 Bilayers
**作者**：Sumanti Patra, Caterina Cocchi
**出处**：arXiv:2607.19937

### 核心结论
建立 MoS2 双层在四个点群（D3h、D3d、C3v、C3）到二阶非线性极化率张量 χ⁽²⁾ 的完整对称性映射框架，以群论论证结合第一性原理响应函数计算说明对称性破缺如何控制各张量元的激活与抑制。文中明确："In their monolayer form, semiconducting TMDs with chemical formula MX2 preferentially crystallize in the non-centrosymmetric point group D3h"，并指出 1H 相单层 MoS2 属 D3h 点群，含 C3 轴、水平镜面 σ_h 与三个竖直镜面 σ_v；因无反演中心故 χ⁽²⁾ 非零，仅余 χ_yyy = −χ_yxx = −χ_xxy = −χ_xyx 四个面内分量。

### 与课题关联
为申请书把单层 WSe₂ 的点群由 C3h 更正为 1H 三角棱柱相的 D3h 提供标准记法依据，并给出该点群下 χ⁽²⁾ 张量元的具体形式，二次谐波强度对入射偏振角的 cos²(3θ) 依赖即由此导出，构成"三阶角谐在二阶响应中的对应物"这一论证的物理依据。

### 已引用位置
申请书（二）研究内容 §二.4 分方向三（WSe₂ 点群与二阶选择定则段）；（三）研究方案 §三.5、§三.8（3）；全文逻辑骨架统一表述表；课题设想验收判据 7。

---

## 2605.21231（定向检索新增，2026-11-11）

**标题**：Destructive interference of second harmonic generation in AA stacked MoTe2/WSe2 heterobilayers
**作者**：Yiduo Wang, Yao Lu, Changshen Chen, Xiaotong Liao, Siyu Fan, Zhenyu Wang, Yao Tian Liu, Subi Du, Yingze Jia, Ye Zhu, Yingwei Wang, Jun He, Song Liu, Jiawei Ruan, Zhen Chen, Kai-Qiang Lin, Yang Xu
**出处**：arXiv:2605.21231

### 核心结论
在近 0°（AA）堆叠 MoTe2/WSe2 异质双层中发现非常规的 SHG 相消干涉，推翻了"单层 TMDC（无反演对称性，D3h）中 60° 堆叠抑制、0° 增强"的常规层分辨非线性极化叠加图像；结合原子分辨成像、激子杂化测量与 ab initio GW，说明 1H 相 WSe2/MoTe2 的 D3h 点群 χ⁽²⁾ 张量在异质堆叠中的干涉路径远比简单叠加复杂。

### 与课题关联
界定层析判据的适用边界：二次谐波极图作为外部参照时，其取向读出在堆叠结构中受干涉效应影响，故层析反演的一手信号取自高阶谐波角向分布，SHG 极图仅作独立参照而非被反演对象。本轮据此在 §二.4 保持"层析反演得到的阶数须与二阶选择定则相符、两者共同构成独立外部参照"的分工表述，未把 SHG 极图当作层析的拟合目标。

### 已引用位置
申请书（二）研究内容 §二.4 分方向三（外部参照分工段）。

---

## 2503.14982（2026-11-11 第 4 轮复核，无新增结论）

**标题**：High-order harmonic generation with orbital angular momentum beams: Beyond-dipole corrections
**作者**：Esra Ilke Albar, Valeriia P. Kosheleva, Heiko Appel, Angel Rubio, Franco P. Bonafé
**出处**：arXiv:2503.14982；Physical Review A, 2025, 112: 063109，DOI 10.1103/c1

### 复核结论
本轮对该文的两个引用数值作了独立复算，结论与前轮一致，无新增内容：原文自述的量级对照为"平面波二阶谐波的修正比三阶谐波高约 10³ 倍"，160% 出自涡旋束横向场梯度最强位置的偶次谐波角向幅度修正，0.07% 出自平面波对照情形的奇次谐波非偶极修正，二者不是同一对比对象，不可相除。按原文自身参数（800 nm、峰值场强 2.72×10¹⁰ V/m、原子置于第一环亮斑 r = 2545 nm）复算 β = a/r_ring = 3.4×10⁻⁴；由 160% 按 β 线性外推至 2% 读出灵敏度得 β ≥ 4.2×10⁻⁶，提案门限 5×10⁻⁵ 为其 11.8 倍裕度（正文表述为 12 倍裕度），门限处预期修正 23.6%。

### 与课题关联
本轮该文在申请书三章中的引用位置作了分工改写，以消除跨章逐字复现：立项依据 §1.2 保留该结果的实验意义解读（涡旋束几何提供了一条可独立标定的强场非偶极通道），研究内容 §二.3 保留其作为 A_nd 上下界的界定（160% 上界与 0.07% 下界来源不同，共同界定非偶极效应量级），研究方案 §三.2 保留其作为标定量级参照的功能（β = a/r_ring 的标定量来源）。三处不再共用同一整句，数值与归属未变。

### 已引用位置
申请书（一）立项依据 §1.2；（二）研究内容 §二.3 分方向二；（三）研究方案 §三.2 理论正演；全文逻辑骨架 §三 跨章节统一表述；课题设想"来源与可靠性"一节。

---

## 阶次集合与带隙关系的独立复算（2026-11-11，方案章第 3 轮对抗评审后修订）

**来源**：申请书（三）研究方案 §三.1 谐波阶次集合段的数值链自查；所用材料带隙与 3.2 μm 驱动光子能量按申请书既有口径取自研究内容章与立项依据章。

### 复算结论

本轮对抗评审指出主网格阶次集合 Q_main = {3, 5, 7, 9, 11, 13, 15} 为全奇集，而"偶阶分量强于奇阶"这一判据需要偶阶在场，二者自相矛盾。独立复算确认该矛盾成立，并连带发现两处带隙关系表述反向。

驱动光子能量按 1239.842 eV·nm / 3200 nm 复算为 0.3875 eV，据此逐项核对：

| 材料 | 带隙 (eV) | 带隙内光子数上限 | 主网格可用阶次（修正后 Q_main = {3,4,5,6,7,9,11}） |
| --- | --- | --- | --- |
| ZnO | 3.37 | 8 | {3, 4, 5, 6, 7} |
| GaSe | 2.60 | 6 | {3, 4, 5, 6} |
| 单层 WSe₂ | 2.00 | 5 | {3, 4, 5} |
| MgO | 7.80 | 20 | 七阶全可用（最高阶光子能量 4.26 eV） |
| Si | 1.10 | 2 | 无带隙内阶次（三阶 1.16 eV 已在其上） |

复算同时确认两处反向表述：原"七阶在 ZnO 与 MgO 上全部位于带隙内"中 MgO 成立而 ZnO 不成立（九阶 3.49 eV 已超 ZnO 带隙，原集合含九阶以上）；原"Q_cal 全部落在 ZnO 带隙以上"恰好相反，Q_cal = {3,5,7,9,11} 中三阶 1.16 eV、五阶 1.94 eV、七阶 2.71 eV 三项落在 ZnO 带隙内，九阶与十一阶在其上。

原文中"Si 的可用阶次为 {3}"一句亦有同类缺陷：三阶光子能量 1.16 eV 已高于 Si 的 1.1 eV 带隙，不属于"带隙内"阶次。修正后的表述把 Si 明确为不贡献带隙内阶次、只作中心对称对照项。

### 与课题关联

主网格集合改为 {3, 4, 5, 6, 7, 9, 11} 后，"奇阶五项、偶阶两项"的原有文字表述成立，偶阶分量判据在主网格上重新具备可比较的数据支撑。该集合仍为七阶，故主网格点数 5×7×8×8 = 2240 点、各块机时 149.3 / 16.0 / 2.7 / 2.4 / 4.2 小时、合计 174.6 小时的核算链不变。Q_cal = {3, 5, 7, 9, 11} 与 Q_ax = {5, 7, 9} 均为 Q_main 的子集，三集合的同源关系成立。

### 已引用位置

申请书（三）研究方案 §三.1；全文逻辑骨架 §三 跨章节统一表述；课题设想"参数网格与机时预算"一节。


---

## Wang 2023：涡旋谐波束的叠层成像先例（2026-11-13，第 3 轮整体一致性评审轮新增引用）

**阅读日期**：2026-11-13

**文献标题**：High-fidelity ptychographic imaging of highly periodic structures enabled by vortex high harmonic beams

**来源**：Wang B, Brooks N J, Johnsen P C, et al. Optica, 2023, 10(9): 1245. DOI: 10.1364/optica.498619（CrossRef 当轮核实：卷 10、期 9、页 1245；检索自 lit-gap-1794233951 定向检索报告）

**核心结论**：以携带轨道角动量的激光驱动产生的高次谐波涡旋光束作探针，实现极紫外叠层相干衍射成像，对强周期性样品获得高保真、高可靠成像，并首次演示对周期样品中近衍射极限孤立缺陷的叠层成像。涡旋探针的内禀模式多样性解决了高周期样品衍射图样多样性不足、重构收敛差的难题。

**与课题关联**：本课题立项依据 §1.1 用其论证"谐波涡旋已从待表征对象转为成像探针"的应用侧进展，与 Gauthier[17] 的半导体谐波 OAM 读出、Uzan-Narovlansky[29] 的多带能带结构观测并列，共同支撑"同一测量平台的应用一侧正在展开"的论证链，随后引出本课题在份额分配阶段的空缺定位。

**已引用位置**：申请书（一）立项依据 §1.1 第 5 段；参考文献表 [39]。


---

## [40] Voisine 2025：欠密等离子体二次谐波中广义角动量的显式对称性破缺（第 3 轮整体一致性评审轮新增引用）

**阅读日期**：2026-11-13

**文献标题**：Explicit Symmetry Breaking of Generalized Angular Momentum by Second-Harmonic Generation in Underdense Plasmas

**来源**：Voisine A, Béjot P, Billard F, et al. Laser & Photonics Reviews, 2025, 19(6): 2401180. DOI: 10.1002/lpor.202401180（当轮 web 检索核实卷期页：期刊标注 2024-12-16 在线、卷 19 期 6、文章号 2401180；检索自 lit-gap-1794233951 定向检索报告）

**核心结论**：自旋-轨道非可分光场的广义角动量（GAM）电荷在欠密等离子体的二次谐波产生过程中不守恒、仅平均守恒；对称性破缺本身构成驱动场拓扑的可探测签名，可进而用于构造鲁棒拓扑吸引子。

**与课题关联**：为立项依据 §1.2 二阶序列论证链补入等离子体侧先例——OAM 守恒在二阶非线性过程中即已呈现"仅平均守恒"的破缺，支撑本课题核心判断"固体强场条件下守恒律能否成立是需要被检验的物理命题，而非可援引的前提"；与 Gui[24]/Hancock[25] 的时空涡旋二阶实验并列，共同界定"以 OAM 通道分辨材料响应"方法学中守恒条件的边界。

**已引用位置**：申请书（一）立项依据 §1.2（Hancock 段之后）；参考文献表 [40]。

---

## 经典文献回录（2026-11-13，第 3 轮参考文献检验后）

**回录说明**：以下 18 条为参考文献表中的奠基与基础条目（气体侧阿秒探测、固体 HHG 建立、OAM 标度律理论、角动量分辨探针），此前仅有评审端 CrossRef 逐字段核验记录、未在检索池留痕，本轮按评审处置指令回录。编号为现行 40 条参考文献表编号，来源行自该表现表逐字提取，正文引用位置当轮对照申请书正文记录。

### 参考文献 [1]

**来源**：Niikura H, Légaré F, Hasbani R, et al. Probing molecular dynamics with attosecond resolution using correlated wave packet pairs. Nature, 2003, 421: 826-829. DOI: 10.1038/nature01430
**核心结论**：以关联波包对在阿秒尺度追踪分子核运动，确立气体 HHG 阿秒探测范式。
**与课题关联**：立项依据开篇气体侧时间分辨率参照。
**已引用位置**：申请书（一）立项依据 §1.1 第 1 段。

### 参考文献 [2]

**来源**：Goulielmakis E, Loh Z H, Wirth A, et al. Real-time observation of valence electron motion. Nature, 2010, 466: 739-743. DOI: 10.1038/nature09212
**核心结论**：实时观测原子价电子运动。
**与课题关联**：与 [3] 以聚合角标支撑价电子运动实时观测与波函数重构论述。
**已引用位置**：申请书（一）立项依据 §1.1 第 1 段（聚合角标 [2,3]）。

### 参考文献 [3]

**来源**：Kienberger R, Goulielmakis E, Uiberacker M, et al. Atomic transient recorder. Nature, 2004, 427: 817-821. DOI: 10.1038/nature02277
**核心结论**：阿秒瞬态记录仪，把亚周期电子动力学测量推进到阿秒尺度。
**与课题关联**：同 [2]。
**已引用位置**：申请书（一）立项依据 §1.1 第 1 段（聚合角标 [2,3]）。

### 参考文献 [4]

**来源**：Ghimire S, DiChiara A D, Sistrunk E, et al. Observation of high-order harmonic generation in a bulk crystal. Nature Physics, 2011, 7: 138-141. DOI: 10.1038/nphys1847
**核心结论**：中红外激光驱动 ZnO 晶体观测到非微扰高次谐波，固体 HHG 开山实验。
**与课题关联**：立项依据领域脉络起点。
**已引用位置**：申请书（一）立项依据 §1.1 第 2 段。

### 参考文献 [5]

**来源**：Ndabashimiye G, Ghimire S, Wu M, et al. Solid-state harmonics beyond the atomic limit. Nature, 2016, 534: 520-523. DOI: 10.1038/nature17660
**核心结论**：固体谐波超越原子截止极限。
**与课题关联**：立项依据方法论论证链第一环。
**已引用位置**：申请书（一）立项依据 §1.1 第 3 段。

### 参考文献 [7]

**来源**：Wu M, Ghimire S, Reis D A, et al. High-harmonic generation from Bloch electrons in solids. Physical Review A, 2015, 91: 043839. DOI: 10.1103/physreva.91.043839
**核心结论**：基于布洛赫电子的半导体布洛赫方程模型。
**与课题关联**：研究方案 SBE 理论正演的文献前提。
**已引用位置**：申请书（一）立项依据 §1.1 第 3 段。

### 参考文献 [8]

**来源**：Vampa G, McDonald C R, Orlando G, et al. Semiclassical analysis of high harmonic generation in bulk crystals. Physical Review B, 2015, 91: 064302. DOI: 10.1103/physrevb.91.064302
**核心结论**：带间再碰撞半经典模型，把固体 HHG 电子动力学还原为可解释的轨迹物理。
**与课题关联**：立项依据轨迹物理序列第一环。
**已引用位置**：申请书（一）立项依据 §1.1 第 4 段。

### 参考文献 [9]

**来源**：Allen L, Beijersbergen M W, Spreeuw R J C, et al. Orbital angular momentum of light and the transformation of Laguerre-Gaussian laser modes. Physical Review A, 1992, 45: 8185-8189. DOI: 10.1103/physreva.45.8185
**核心结论**：具有螺旋相位的光场每个光子携带 lħ 外禀角动量，与自旋角动量独立。
**与课题关联**：OAM 概念奠基文献。
**已引用位置**：申请书（一）立项依据 §1.1 OAM 段。

### 参考文献 [10]

**来源**：Hernández-García C, Picón A, San Román J, et al. Attosecond extreme ultraviolet vortices from high-order harmonic generation. Physical Review Letters, 2013, 111: 083602. DOI: 10.1103/physrevlett.111.083602
**核心结论**：携带拓扑荷的红外场驱动高次谐波传播后仍保有螺旋相位结构，l_q = q·l₀ 标度律首个理论预言。
**与课题关联**：立项依据 OAM 标度律叙事的理论起点。
**已引用位置**：申请书（一）立项依据 §1.1 标度律段。

### 参考文献 [11]

**来源**：Rego L, San Román J, Picón A, et al. Nonperturbative twist in the generation of extreme-ultraviolet vortex beams. Physical Review Letters, 2016, 117: 163202. DOI: 10.1103/physrevlett.117.163202
**核心结论**：标度律在微扰区不成立，须由再碰撞轨迹的非微扰扭量修正给出正确结果。
**与课题关联**：支撑标度律是非微扰过程产物的论证。
**已引用位置**：申请书（一）立项依据 §1.1 标度律段。

### 参考文献 [22]

**来源**：Yokoshi N, Kato A. Optical vortex probe of loop-current chirality in moiré materials. Physical Review B, 2026, 113: 245303. DOI: 10.1103/dlgp-bgbb
**核心结论**：以光学涡旋探针分辨莫尔材料内禀环流手性，内禀贡献出现在螺旋度依赖直流光电流的 Δℓ = 3 通道。
**与课题关联**：角动量分辨探针方法雏形；Δℓ = 3 进入层析探针库设置依据。
**已引用位置**：申请书（一）§1.2、（二）研究内容、（三）研究方案（各 1 次）。

### 参考文献 [23]

**来源**：Rego L, Dorney K M, Brooks N J, et al. Generation of extreme-ultraviolet beams with time-varying orbital angular momentum. Science, 2019, 364: eaaw9486. DOI: 10.1126/science.aaw9486
**核心结论**：制备携带时变 OAM 的极紫外自扭矩光束。
**与课题关联**：气体侧时变 OAM 先例，探索方向最近邻对照。
**已引用位置**：申请书（一）§1.2、（二）研究内容（各 1 次）。

### 参考文献 [26]

**来源**：You Y S, Reis D A, Ghimire S. Anisotropic high-harmonic generation in bulk crystals. Nature Physics, 2017, 13: 345-349. DOI: 10.1038/nphys3955
**核心结论**：块状晶体中各向异性与偏振取向依赖的独立测量。
**与课题关联**：晶体各向异性进入角动量分配问题的实验先声。
**已引用位置**：申请书（一）立项依据 §1.1 第 2 段。

### 参考文献 [27]

**来源**：Li L, Lan P, Zhu X, et al. Reciprocal-space-trajectory perspective on high-harmonic generation in solids. Physical Review Letters, 2019, 122: 193901. DOI: 10.1103/physrevlett.122.193901
**核心结论**：倒空间轨迹模型。
**与课题关联**：轨迹物理序列一环，理论正演的倒空间语言前提。
**已引用位置**：申请书（一）立项依据 §1.1 第 4 段。

### 参考文献 [28]

**来源**：Yue L, Gaarde M B. Imperfect recollisions in high-harmonic generation in solids. Physical Review Letters, 2020, 124: 153204. DOI: 10.1103/physrevlett.124.153204
**核心结论**：固体中电子碰撞后未必回到空穴附近，非理想再碰撞普遍存在。
**与课题关联**：界定固体再碰撞图像适用边界。
**已引用位置**：申请书（一）立项依据 §1.1 第 4 段。

### 参考文献 [29]

**来源**：Uzan-Narovlansky A J, Jiménez-Galán Á, Orenstein G, et al. Observation of light-driven band structure via multiband high-harmonic spectroscopy. Nature Photonics, 2022, 16: 428-432. DOI: 10.1038/s41566-022-01010-1
**核心结论**：以多带高次谐波光谱观测强场驱动下的瞬态能带结构。
**与课题关联**：固体 HHG 作为物性探针的代表工作。
**已引用位置**：申请书（一）立项依据 §1.1 第 5 段。

### 参考文献 [34]

**来源**：Flores-Cova G, Das B K, Rosales-Guzman C, et al. A new twist on astigmatic transformation: Beyond Laguerre-Gaussian beams. arXiv:2610.31313 [physics.optics], 2026. †
**核心结论**：把 astigmatic 变换推广到拉盖尔-高斯之外的光束族，拓扑荷读出有闭式解析与实验双重支撑。
**与课题关联**：测量端选择 astigmatic 变换的方法依据。
**已引用位置**：申请书（三）研究方案读出方案段与可行性段（2 次）。

### 参考文献 [38]

**来源**：Heide C, Kobayashi Y, Johnson A C, et al. Probing electron-hole coherence in strongly driven 2D materials using high-harmonic generation. Optica, 2022, 9: 512-516. DOI: 10.1364/optica.444105
**核心结论**：以高次谐波探测强场驱动二维材料的电子-空穴相干性。
**与课题关联**：单层 WSe₂ 进入样品矩阵的先例支撑。
**已引用位置**：申请书（一）立项依据 §1.1 第 5 段。
