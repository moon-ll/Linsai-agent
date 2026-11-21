---
title: "2019-1906_10224-high-harmonic-generation-from-spin-polarised-defects-in-soli"
type: "papers"
created: "2026-08-29T14:36:49Z"
updated: "2026-11-15T15:09:21Z"
tags: []
related: ["1906.10224", "PLAN", "TDDFT", "general-houston-kronig-penney-landau-zener-20261004", "固体HHG", "强场超快", "强场超快光学", "强场驱动", "莫尔超晶格", "量子几何", "高次谐波产生", "高次谐波产生（HHG）"]
source_raw: "2019-1906.10224-high-harmonic-generation-from-spin-polarised-defects-in-soli.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-11-08T01:01:16Z"
merged_from: ["wiki/papers/1906.10224.md"]
---

# High-Harmonic Generation from Spin-Polarised Defects in Solids

## 林赛的理解

这篇工作对我们理解固体强场动力学中的缺陷物理具有重要参考价值。作为首批使用 full ab initio TDDFT 研究真实缺陷（而非一维模型）中 HHG 的理论工作，它建立了 vacancy 缺陷与 HHG 光谱特征之间的定量联系。特别值得注意的有三点：其一，boron vacancy 与 nitrogen vacancy 虽然只是缺失同一晶体中不同种类原子，却产生了定性完全不同的 HHG 光谱行为，这说明缺陷的电子结构而非化学种类主导了强场响应；其二，电子-电子相互作用在有缺陷体系中不可忽略，independent particle 近似会给出错误的定性结论；其三，spin polarization 的存在使得不同自旋通道的 HHG 响应可以截然不同，这在 valleytronics 和 spinronics 应用中具有潜在价值。

对我们组的 HHG/阿秒研究方向而言，一个直接的启示是：在研究真实材料（而非理想 pristine 晶体）时，缺陷的存在会显著改变 HHG 谱的低阶部分（尤其 third harmonic），而这种改变具有自旋依赖性。这意味着如果用 HHG 作为探针研究量子材料中的电子动力学，缺陷的贡献必须被仔细考虑——尤其当研究对象是二维材料或存在莫尔超晶格等天然缺陷富集体系时。另一方面，defect engineering 或许提供了一种调控 HHG 谱的途径。

## 研究问题（Research Question）
本工作要回答的核心问题是：**固体中的点缺陷（尤其是 spin-polarised vacancy）能否在强场驱动的高次谐波产生（HHG）过程中留下可辨识的特征指纹？如果能，这些特征与缺陷的哪些物理性质（电子结构、自旋、几何）相关？电子-电子相互作用在缺陷体系的 HHG 中扮演何种角色？**

具体而言，作者探讨了以下几个子问题：
1. 缺陷是否能在 HHG 光谱中产生可测量的特异性信号？
2. 自旋极化缺陷的不同自旋通道在 HHG 中的贡献是否不同？能否独立控制？
3. 电子-电子相互作用（beyond independent-particle approximation）对 defected-solid 的 HHG 有何影响？
4. 缺陷浓度对 HHG 光谱特征的影响如何？

## 研究背景（Background）
HHG 最初在气体原子和分子中发现并得到深入研究，为阿秒电子动力学探测提供了前所未有的分辨率。近年来，中红外和太赫兹激光源的发展使得在固体（半导体、介电材料、纳米结构）中实现非微扰高次谐波产生成为可能。Ghimire 等人（2011）的开创性工作标志着固体 HHG 研究的开端。由于固体中电子密度远高于气体，HHG 固体的谐波产额可能更高，且为紧凑型台面化阿秒光源（极紫外和软 X 射线能段）提供了有吸引力的路径。此外，HHG 还能用于成像固体的能带色散。

实际固体中缺陷不可避免。缺陷可以表现为空位、杂质、间隙原子（可中性或带电）、位错等形式。缺陷工程已被用于实现材料的理想特性，例如掺杂对电子学的革命性影响。某些缺陷还具有自旋极化特性。然而，缺陷在强场物理中的影响尚未被充分探索。

此前关于掺杂半导体 HHG 的理论研究使用了简单的一维模型哈密顿量。Huang 等人发现施主掺杂半导体的第二平台效率增强；Tancogne-Dejean 等人用 TDDFT 预测了施主掺杂半导体 HHG 效率的数量级增强；Corkum 等人开发了浅杂质断层成像的概念框架。但这些工作仅考虑了一维模型系统，未对真实缺陷（通过几何优化和原子力松弛）进行研究。

六方氮化硼（h-BN）是一种理想的缺陷研究体系：它是宽带隙半导体（实验带隙约 6 eV），适合在无损伤阈值以下产生高次谐波；单层 h-BN 容易可视化感应电子密度和局域化缺陷态；硼或氮空位在 h-BN 中表现为自旋极化缺陷；其部分离子性键合特征使其成为探索非磁性 defected solids 中自旋分辨 HHG 的理想候选材料。

## 研究方法（Methods）
**计算方法**：采用时间依赖密度泛函理论（TDDFT）模拟 defected-solid 中的强场驱动电子动力学，使用 Octopus 代码传播 Kohn-Sham 方程。基态几何优化使用 Quantum ESPRESSO 代码。交换-关联泛函采用 PBE（Perdew-Burke-Ernzerhof）广义梯度近似（GGA），使用绝热近似处理含时模拟。使用 norm-conserving 赝势。

**超胞设置**：使用 5×5 超胞（50 原子）和 7×7 超胞（98 原子）模拟空位。5×5 超胞尺寸足够大，最近邻缺陷之间距离大于 12 Å，最小化了相邻缺陷间的相互作用。两种超胞收敛到相似的基态。空位浓度分别为约 2%（5×5）和约 1%（7×7）。

**激光参数**：15 fs 脉冲宽度（Gaussian sine-squared 包络），峰值强度 13.25 TW/cm²（在材料内部，对应折射率 n≈2.65 的平面光学索引），载波波长 1600 nm（对应光子能量 0.77 eV），线偏振，方向垂直于 h-BN 镜面（out-of-plane）。

**收敛参数**：实空间网格间距 0.18 Å，6×6 k-points 网格采样 2D 布里渊区，非周期方向模拟盒 74.08 Å，两侧各含 21.17 Å 吸收区，使用复吸收势方法（cap height h = -1 a.u.）避免谱感兴趣区域的反射误差。

**缺陷构型**：boron vacancy（V_B）和 nitrogen vacancy（V_N）均使系统产生自旋极化，总磁矩为 +1 µ_B。V_B 结构优化后局部三维对称性降低（Jahn-Teller 畸变），晶格常数 12.60 和 12.57 Å；V_N 晶格常数 12.48 Å；pristine h-BN 晶格常数 12.56 Å。原子坐标和晶格常数弛豫，力收敛到 10⁻³ eV/Å 以下。

**分析工具**：通过展开 5×5 超胞的能带结构来可视化 vacancy structures 的有效单粒子能带结构（谱函数）。用傅里叶变换总自旋极化含时电流计算 HHG 谱。用含时波函数在基态波函数基组上的投影计算激发电子数。

## 主要发现与核心结论

**1. 缺陷显著改变 HHG 光谱**

pristine h-BN 与含空位 h-BN 的 HHG 光谱存在两个显著差异：（1）低于带隙的谐波（below band-gap harmonics）显著增强；（2）接近能量截止的高阶谐波产额显著降低。

**2. 自旋分辨差异明显**

- **Boron vacancy（V_B）**：spin-down 通道的 third harmonic 强度比 spin-up 通道高约一个数量级。spin-down 通道的额外缺陷态（靠近价带顶）允许电子通过多个通道电离或复合，对 third harmonic 贡献更多。
- **Nitrogen vacancy（V_N）**：third harmonic 增强主要来自 spin-up 通道而非 spin-down 通道。这与 V_B 中的情况相反。

**3. 缺陷态的电子结构**

V_B（triple acceptor，带 +1 µ_B 磁矩）：
- 自旋-up：一个缺陷态推入价带（深能级）
- 自旋-down：两个缺陷态在带隙内（未占据）
- 缺陷态波函数主要来自邻近 N 原子的 p_x 和 p_y 轨道（σ 特性）

V_N（single donor，带 +1 µ_B 磁矩）：
- 自旋-up 和自旋-down 各有一个缺陷态，更靠近导带
- 自旋-up 缺陷态被占据
- 缺陷态波函数主要来自邻近 B 原子的 p_z 轨道（π 特性）

**4. 电离动力学**

5×5 超胞中，V_B 有 1.6 个电子被电离，而 pristine h-BN 同期仅 0.25 个电子被电离。缺陷态扮演中间角色，促进 sequential 电离过程，但主要是填充原本未占据的带隙态，而非进一步电离到导带。

**5. 电子-电子相互作用的关键作用**

- **Pristine h-BN**：TDDFT 和 independent particle（IP）模型得到的 HHG 谱相似，无显著多体效应。
- **V_B**：TDDFT 和 IP 模型结果**显著不同**，说明电子-电子相互作用对 defected solids 的 HHG 必不可少。local field effects 导致高能谐波产额降低（感应偶极子产生屏蔽电场，抵消外加电场）；correlation effects 导致 third harmonic 产额变化。
- **V_N**：IP 模型能较好捕捉 third harmonic 增强，但 30-35 eV 区间的产额增加来自电子-电子相互作用。local field effects 比 V_B 弱，因为 π 型缺陷态的感应偶极子极化程度低于 σ 型缺陷态。

**6. 缺陷浓度的影响**

7×7 超胞（约 1% 掺杂浓度）的计算表明：third harmonic 增强以可比强度持续存在；高能区域与 pristine 光谱吻合良好。这与高能区主要由 bulk bands 主导的结论一致。

**7. V_B 与 V_N 的本质差异**

| 性质 | V_B | V_N |
|------|-----|-----|
| 缺陷态波函数字符 | σ（局域化感应偶极强） | π（感应偶极弱） |
| Local field effects | 强（高能谐波产额降低） | 弱（高能区更接近 pristine） |
| 自旋贡献 | 主要来自 spin-down | 主要来自 spin-up |
| 缺陷类型 | Triple acceptor | Single donor |
| HHG 谱特征 | 与 pristine 差异显著 | 与 pristine 较为接近 |

## 潜在研究方向（Future Directions）
**1. 实验验证**
目前工作完全基于理论计算，实验上验证这些预测（如 third harmonic 的自旋依赖增强、缺陷浓度效应）是重要的下一步。

**2. 更复杂的缺陷类型**
本工作仅研究了单空位（monovacancy），双空位（bi-vacancy）、杂质（impurities如碳替代掺杂）与间隙原子的 HHG 响应尚待探索。作者预测：碳掺杂缺陷的 HHG 行为应与 V_N 类似（因缺陷态靠近导带）；双空位如果缺陷态与邻近带隙较小，则不会显著改变 below band-gap harmonics。

**3. 缺陷成像**
使用 HHG 实现 spin-polarised defects 的成像是一个有吸引力的方向。但作者指出：对于稀磁杂质，正负磁矩缺陷数量相等，宏观平均后自旋信号相同，因此用圆偏振脉冲独立探测各自旋通道的方案在实际样品中可能不可行。

**4. 电子-杂质散射**
监测电子-杂质散射过程用 HHG 的可行性尚待研究。

**5. 二维及延伸体系**
进一步研究可扩展到其他二维材料（MoS₂、WS₂、石墨烯等）中的缺陷 HHG，以及三维延伸体系。

**6. 损伤阈值**
缺陷存在时能量吸收增加，导致损伤阈值降低。这一效应在更高光强下可能变得显著，需要系统研究。

**7. 其他激光参数**
脉冲宽度、波长、椭圆率等激光参数对 defected HHG 的影响尚未系统研究。

## 与林赛研究的关联

作为强场超快光学 PI，本工作对林赛组的研究有如下具体接口：

**HHG 物理**：本工作确认了缺陷会在 HHG 光谱中留下可辨识的指纹——特别是 third harmonic 的增强和自旋依赖性。这提示我们在用 HHG 作为探针研究量子材料时，需要区分缺陷贡献与 intrinsic 电子动力学。尤其当我们研究 MoS₂、WS₂、MoTe₂ 等二维材料的 HHG 时，样品中的 vacancy 或 substitutional defect 可能会显著影响低阶谐波。

**阿秒技术**：固体 HHG 是紧凑型台面化阿秒光源的候选技术。本工作表明缺陷工程（defect engineering）可能提供一种调控 HHG 谱的途径——例如通过控制缺陷类型和浓度来优化特定谐波的产额。这对开发基于二维材料的新型阿秒光源有直接指导意义。

**交变磁与量子几何**：h-BN 虽然不是磁性材料，但本工作揭示的 spin-polarised defect states 与自旋的耦合提示了用 HHG 探测具有局域磁矩的缺陷态的可能性。在我们的研究中，若涉及具有磁性缺陷或磁性掺杂的二维材料（如 Cr-doped MoS₂ 或磁性隧道结），类似的物理可能适用。

**莫尔体系**：莫尔超晶格中天然存在大量堆叠诱导的缺陷和应变。本工作建立的缺陷-HHG 对应关系提示：莫尔材料的 HHG 谱可能部分反映莫尔局域态的缺陷特性，而非仅来自平带或拓扑性质。

**方法论启示**：本工作有力地证明了在研究 defected solids 的强场响应时，TDDFT（包含电子-电子相互作用的 adiabatic GGA）是必要的，independent-particle 近似可能给出错误的定性结论。这对林赛组使用第一性原理方法研究强场动力学有重要的方法论参考价值，特别是在处理包含缺陷的体系时。

## 来源

- 蒸馏自全文（deep-read）
- Mrudul M. S., Nicolas Tancogne-Dejean, Angel Rubio, Gopal Dixit. "High-Harmonic generation from spin-polarised defects in solids." *npj Computational Materials* 5, 180112 (2019). arXiv:1906.10224v3


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：TDDFT 自旋分辨缺陷 HHG（真实空位缺陷的强场指纹：V_B vs V_N 自旋通道不对称）

**原理**：对含真实空位缺陷（经几何优化+原子力松弛）的 h-BN 用实时间 TDDFT（Octopus 传播 Kohn-Sham 方程，PBE 绝热 GGA）模拟面外驱动强场动力学，傅里叶变换总自旋极化含时电流得自旋分辨 HHG 谱。核心结论：① 缺陷显著改变 HHG——带隙下谐波增强+近截止产额下降；② V_B（triple acceptor，σ 型缺陷态）三次谐波增强在 spin-down 通道高约一个数量级，V_N（single donor，π 型缺陷态）在 spin-up 通道，方向相反，由缺陷态能级位置与波函数字符决定；③ 有缺陷时电子-电子相互作用不可忽略（local field effects 屏蔽压低高能产额、correlation 改变 TH），independent-particle 近似给出错误定性结论；④ 缺陷扮演序贯电离的中间态角色（V_B 电离 1.6 电子 vs pristine 0.25 电子）；⑤ 1% 浓度下 TH 增强仍在，高能区回归 pristine（体带主导）。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 超胞/浓度 | 5×5 超胞 50 原子（约2%）与 7×7 超胞 98 原子（约1%）；最近邻缺陷间距 >12 Å；力收敛 <10^-3 eV/Å | 研究方法 |
| 激光 | 1600 nm（0.77 eV）；15 fs sin² 包络；13.25 TW/cm²（材料内，n≈2.65）；线偏振垂直于 h-BN 镜面（out-of-plane） | 研究方法 |
| 数值收敛 | 实空间网格 0.18 Å；6×6 k 点；非周期方向盒 74.08 Å，两侧各 21.17 Å 复吸收势（h = -1 a.u.） | 研究方法 |
| 缺陷构型 | V_B：Jahn-Teller 畸变，晶格常数 12.60/12.57 Å（pristine 12.56 Å），V_N 12.48 Å；均带 +1 µ_B 磁矩；V_B 缺陷态波函数来自近邻 N 的 p_x/p_y（σ），V_N 来自近邻 B 的 p_z（π） | 研究方法/结果 |
| 电离量对比 | V_B 电离 1.6 电子 vs pristine 0.25 电子（同条件下） | 主要发现 |
| 软件 | Octopus（TDDFT 传播）+ Quantum ESPRESSO（基态几何优化），norm-conserving 赝势 | 研究方法 |

**适用边界**：纯理论（实验验证缺失）；仅单空位（双空位/掺杂/间隙原子未做）；仅面外偏振单一取向；脉宽/波长/椭圆度依赖未系统扫描；缺陷增加能量吸收导致损伤阈值降低未量化；稀磁杂质正负磁矩对消使自旋分辨探测在真实样品不可行（作者自评）；TDDFT 用绝热 PBE（激子/非绝热效应缺失）；结果基于 h-BN，外推到其它二维材料需重新验证。
**代表作**：Mrudul, Tancogne-Dejean, Rubio, Dixit, npj Comput. Mater. 5, 180112 (2019)；Ghimire 2011（固体 HHG 开山）；Huang/Tancogne-Dejean 掺杂 HHG 前作
*方法卡回补 2026-09-27*


## 合并自「1906.10224」

## 深度解析

（来自简报深度分析）

## 阅读笔记

### general-houston-kronig-penney-landau-zener-20261004

**High-Harmonic generation from spin-polarised defects in solids** — M. S. Mrudul, Nicolas Tancogne-Dejean, Angel Rubio, Gopal Dixit. *npj Comput. Mater.* **6**, 10 (2020). DOI 10.1038/s41524-020-0275-z

### 研究问题（Research Question）
缺陷（空位）能否在强场驱动电子动力学中留下可辨识的"指纹"，特别是自旋极化缺陷？电子–电子相互作用对缺陷与体材料是否起不同作用？能否在非磁性宿主中对不同自旋通道独立操控电子动力学？缺陷引起的对称性破缺如何改变 HHG 谱？

### 研究背景（Background）
固态 HHG 自 Ghimire 等 2011 年 ZnO 单晶工作以来已成为阿秒电子动力学探针与紧凑 XUV 源路线。此前关于缺陷影响 HHG 的工作几乎都是一维模型哈密顿量（供体掺杂半导体效率提升若干数量级、独立粒子模型、紧束缚 Anderson 模型给出无序导致的清晰峰），未做真实缺陷的几何优化与力松弛；电子–电子相互作用、自旋、缺陷引起的对称性破缺等均未触及。h-BN 因带隙宽（实验 6 eV，DFT-PBE 给出 4.73 eV）、B/N 空位为自旋极化缺陷（+1 μ_B），是研究自旋分辨 HHG 的理想体系。

### 研究方法（Methods）
ab initio TDDFT（OCTOPUS 代码推进 Kohn-Sham 方程），GGA-PBE 泛函，绝热近似，norm-conserving 赝势；实空间网格 0.18 Å，2D Brillouin 区 6×6 k 点，半周期边界，模拟盒 74.08 Å（每侧 21.17 Å 吸收区，CAP 高度 h = −1 a.u.）。几何优化用 Quantum ESPRESSO（截断 150 Ry，10×10×1 k 点，力收敛 10⁻³ eV/Å，真空 >20 Å）；缺陷用超胞法：5×5（50 原子，浓度 2%）与 7×7（98 原子，~1%）；弛豫晶格常数 V_B 12.60 Å、V_N 12.57 Å、pristine 12.56 Å。激光：1600 nm（0.77 eV）、15 fs FWHM、sin² 包络、峰值 13.25 TW/cm²（按面内折射率 ~2.65 折算），偏振垂直于 h-BN 镜面。HHG 谱由自旋分辨时变电流的 Fourier 变换给出，激发电子数由时间演化波函数在基态波函数上投影计算；并以独立粒子（IP）近似对比，分离局域场效应与关联效应。

### 主要发现与核心结论（Main Results）
V_B 的带隙以下谐波显著增强、而接近截止处产额大幅低于 pristine；自旋分辨显示第三谐波中自旋向下通道比自旋向上强约一个数量级，而高能区产额下降在两自旋通道上完全一致——说明高能区由体带主导，缺陷态不直接参与。V_B 含 1 个自旋向上 + 2 个自旋向下的带隙内缺陷态（全部未占据），构成三重受主，波函数由空位附近 N 原子的 p_x、p_y 态贡献、具 σ 特征；V_N 中自旋向上/向下各 1 个缺陷态靠近导带、自旋向上态被占据，构成单施主，波函数由 B 原子的 p_z 态贡献、具 π 特征。激发电子数：V_B 超胞 1.6 个电子，pristine 仅 0.25 个；脉冲结束后电子仍留在缺陷态，说明宽禁带宿主中发生的是向空隙态的净布居转移而非向导带永久提升。TDDFT 与 IP近似对 pristine h-BN 结果相似（无显著多体效应），对 V_B 却差异显著，说明缺陷固体 HHG 中电子–电子相互作用是本质要素、IP 近似会给出定性错误预测；局域场效应（局域化诱导电荷的振荡偶极屏蔽外场）主导 V_B 高能区产额下降，且因诱导电场源自自旋求和的诱导密度而对两自旋通道等效。V_N 谱与 pristine 相似（局部对称性保留），只在带隙以下（第三谐波增强，自旋向上主导）及 30–35 eV 区间产额上升；7×7（~1%）下第三谐波增强仍保持可比强度。

### 潜在研究方向（Future Directions）
宏观平均下正负磁矩缺陷数目相同，用圆偏振分别探测上/下自旋通道的设想不成立（信号重合），需另寻自旋分辨方案。后续方向：用 HHG 监测电子–杂质散射、更复杂缺陷（双空位，因缺陷态与带边间距小预期带隙以下谐波无显著变化）、埋藏缺陷成像的实用方案，以及二维与扩展体系中孤立缺陷的强场电子动力学。

---


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：自旋分辨 ab initio TDDFT 的 h-BN 缺陷 HHG（几何优化超胞 + IP 对照分离局域场/关联效应）

**原理**：ab initio TDDFT（OCTOPUS，GGA-PBE）+ Quantum ESPRESSO 几何优化超胞模拟 B/N 空位自旋极化缺陷：自旋分辨电流 Fourier 变换给谱——V_B 带隙以下谐波显著增强、第三谐波自旋向下通道比向上强约一个数量级，高能区产额下降两自旋通道一致（体带主导、缺陷态不参与）；TDDFT 与 IP 近似对 V_B 差异显著——缺陷固体 HHG 中电子-电子相互作用是本质要素（局域场效应主导高能区下降，因诱导场源自自旋求和密度而对两自旋等效）；V_N 局部对称保留谱近 pristine。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 激光参数 | 1600 nm（0.77 eV）、15 fs FWHM、sin² 包络、峰值 13.25 TW/cm²、偏振垂直镜面 | 研究方法 |
| 超胞设置 | 5×5（50 原子，2%）/7×7（98 原子，~1%）；晶格常数 V_B 12.60 Å、V_N 12.57 Å、pristine 12.56 Å | 研究方法 |
| 激发电子数 | V_B 超胞 1.6 个 vs pristine 0.25 个（净布居转移向空隙态而非导带） | 主要发现与核心结论 |

**适用边界**：宏观平均下正负磁矩缺陷数目相同，圆偏振分别探测自旋通道的设想不成立（信号重合）；双空位（缺陷态近带边）预期带隙下谐波无显著变化；埋藏缺陷成像实用方案待发展；h-BN 带隙 PBE 4.73 eV（实验 6 eV）。
**代表作**：Mrudul, Tancogne-Dejean, Rubio & Dixit, High-Harmonic generation from spin-polarised defects in solids, npj Comput. Mater. 6, 10 (2020), arXiv:1906.10224
*方法卡回补 2026-11-02*

<!-- linsai-wikilinks -->
## 关联概念

- [[1906.10224]]
- [[PLAN]]
- [[TDDFT]]
- [[general-houston-kronig-penney-landau-zener-20261004]]
- [[固体HHG]]
- [[强场超快]]
- [[强场超快光学]]
- [[强场驱动]]
- [[莫尔超晶格]]
- [[量子几何]]
- [[高次谐波产生]]
- [[高次谐波产生（HHG）]]
<!-- /linsai-wikilinks -->
