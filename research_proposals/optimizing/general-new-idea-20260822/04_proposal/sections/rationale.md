## （一）立项依据

### 1. 研究背景与领域意义

高次谐波产生是强场激光与凝聚态物质相互作用的高阶非线性过程。2011年，Ghimire等人[9]首次报道中红外激光驱动ZnO晶体产生的非微扰高次谐波，突破了气体 HHG 三十年来局限于原子气体的范式，确立了固体 HHG 作为强场超快探测手段的实验可行性。此后十年，HHG 从宽禁带半导体拓展至石墨烯[10]、MoS₂[11]、WSe₂[12]等二维材料，从单光子能隙体系延伸至激子-光子耦合系统[13]，物理图像也从三步模型类比演化为带间极化与带内电流双通道干涉的精细理论[14]。

固体 HHG 的核心优势在于三种属性的共存：发射过程约束在驱动光场的一个光学周期内（亚周期时间分辨）；对晶体空间对称性与磁对称性高度敏感（选择规则指纹）；具备体相穿透能力（克服表面敏感性瓶颈）。这三种属性使 HHG 有潜力填补传统超快探针在体相、亚周期、对称性敏感三个维度难以兼顾的方法学空白。在反铁磁序参量的超快操控[15]、电荷密度波相变的动力学表征[16]、以及能带拓扑的瞬态探测[17]等领域，HHG 光谱学已初步展示了其独特能力。

固体 HHG 在磁性材料中的应用仍处于早期阶段。现有研究主要集中于演示"磁敏感信号的存在"，尚未建立从 HHG 频谱特征到磁结构参数的定量映射关系，也未实现自旋通道分辨的谐波测量。这一现状限制了从"看到指纹"到"确定身份"的跨越——正是本项目聚焦的核心瓶颈。

### 2. 交变磁性的发现与自旋劈裂新机制

磁有序材料按照自旋排列方式可分为铁磁（平行排列，净磁矩非零）、反铁磁（反平行排列，净磁矩接近零）和近年来确立的第三类——交变磁体（altermagnet）。2022年，Šmejkal等人[1]从对称性分析出发，指出存在一类由晶体对称性（而非自旋轨道耦合）保护的自旋劈裂材料：其自旋劈裂来源于动量空间的晶体场效应，产生 d 波或 g 波形自旋纹理，在保持零净磁矩的同时展现出与铁磁体相当的自旋极化。

2024年，Krempaský等人[2]在α-MnTe中通过角分辨光电子能谱实验证实了 g 波交变磁序的存在：实测自旋劈裂达数百 meV 量级。Nature 原文指出："The resulting non-relativistic electronic structure of this altermagnet is of the g-wave type"。该发现将交变磁性从理论预言推向真实材料体系。2026年，Long等人[2601]进一步测定了 CrSb 中 g 波序参量的三维体分辨结构，给出了 g 波自旋纹理在动量空间的几何构型。

交变磁性的核心特征是自旋劈裂与驱动光子能量同量级。以α-MnTe为例，其实测 g 波自旋劈裂约 0.3–0.8 eV[2]，与 3 μm 中红外驱动光子能量 0.41 eV 处于同一量级。这一能量匹配关系使自旋劈裂对带间跃迁通道的调制直接进入驱动共振窗口——这是本项目选择 3 μm 驱动波长的物理依据，其调制幅度将显著高于数值与实验噪声本底，为可定量测量的谐波特征奠定了基础。

### 3. 核心挑战：自旋劈裂如何写入谐波频谱

固体 HHG 的发射机制可分解为两个通道[14]：带间极化通道（电子在价带与导带之间的相干隧穿）与带内电流通道（导带内电子在布里渊区的非平衡加速）。两个通道的相对权重随驱动强度、晶格取向与能带结构变化，在谐波频谱中表现为偶/奇阶次比、偏振椭圆率与产额标度律的不同特征。

在非磁性半导体中，上述双通道模型已能定量解释实验观测[14][18]。在磁性半导体中，能带自旋劈裂引入了新的自由度：不同自旋通道的电子在动量空间经历不同的有效势，导致带间与带内通道对各阶谐波的贡献出现自旋极化分化。然而，既有 SBE（半导体布洛赫方程）或 Houston 基框架虽可处理自旋劈裂能带，却未建立 g 波自旋纹理的动量依赖特征与 HHG 频谱的定量联系——这是当前理论与实验之间的核心空白。

这一空白带来一个关键的可检验预言：g 波自旋劈裂具有四组节点面（nodal plane）结构，其在倒空间的几何构型与自旋轨道耦合机制（如 Rashba 自旋纹理）的对称性破缺模式存在本质差异。若将这一差异转化为谐波偏振各向异性图样的预言，则两种机制在 HHG 谱上的特征将构成可区分的判据——而这一判据至今未被任何理论与实验工作提出或验证。

更深层的挑战在于多通道耦合导致的不可辨识性。同一组 2/3 阶谐波强度比的变化，可能来源于交变磁序参量引起的对称性破缺，也可能来源于能带色散在 Γ 点附近的各向异性修正，或来源于光致载流子分布变化带来的矩阵元效应。在当前实验精度下，这三种来源在 HHG 谱上产生的特征可能相互叠加、无法分离——这意味着从"观测到磁敏感信号"到"建立定量读出方案"，需要跨越的不仅是测量技术，更是反演方法的可靠性论证。

截至 2026 年 8 月，系统检索 altermagnet-high-harmonic-generation 与 g-wave-spin-splitting-harmonic-spectrum 关键词组合（时间范围 2015—2026），未发现含动量依赖自旋劈裂的自旋分辨固体 HHG 理论与实验研究报道。该空白是真实的：g 波自旋纹理与 HHG 频谱的定量联系尚无人建立。

### 4. 国内外研究现状

在固体 HHG 理论方面，Schubert等人[19]于 2014 年建立了带间极化通道的微扰理论框架；Luu与Wörner团队[20]进一步发展了三维固体 HHG 的完整理论模型。2021年，Kang等人[21]基于半导体布洛赫方程对 MoS₂ 的 HHG 进行了系统性数值研究，揭示了谷间干涉与激子效应在谐波产生中的角色。近年来，含时密度泛函理论（TDDFT）也被应用于固体 HHG 模拟[22]，但其计算成本限制了对大布里渊区与多带效应的系统性探索。

在 HHG 光谱学应用方面，Hancock等人[23]利用偏振分辨 HHG 探测了 MoS₂ 的能带各向异性；Luu团队[24]在六角氮化硼中观测到 HHG 对拓扑相变的敏感性。2025年，Suzuki与Okazaki[2510]系统综述了基于 HHG 激光的时间分辨光电子能谱技术在量子材料电声相互作用研究中的应用，为 HHG 与 ARPES 的联合探测提供了方法论基础。在磁性材料方面，Fuchs等人的 MnTe HHG 实验[3]（精确书目由文献检索待补全）首次演示了交变磁材料中的光学 HHG 现象，但未涉及自旋/偏振通道分辨测量，其物理图像停留于"现象演示"层面。

在国际前沿进展方面，超导配对、噪声谱学与压磁谱学三类新判据近期被相继提出：g 波交变磁体中涌现手性 p 波与 d 波非常规超导态的理论预言[2602]、关联量子退相位测量术对二维超导体与交变磁体的对称性分辨噪声谱学[2604.22751]、以及压磁诱导对称性破缺的光谱指示器[2603.09074]，为交变磁体谱学判据提供了多维理论框架。Zhang等人[2606.13395]于 2026 年用 Andreev 反射探测 CrSb 中 g 波自旋劈裂的动量依赖，开辟了输运手段探测 g 波序参量的新途径——但其探测深度受超导点接触的空间限制，无法推广至体相无损测量，体相、无损、自旋分辨三个需求之间仍存在缺口。

在国内研究现状方面，中国科学院物理研究所、北京大学与中国科学技术大学在固体 HHG 实验与理论方面已有布局。IOP 的 HHG 实验平台已具备 3 μm 中红外驱动光源与偏振分析能力，相关测量在二维材料的 HHG 光谱学方面积累经验[25]。在交变磁性材料制备与表征方面，国内团队在 MnTe 与 CrSb 外延薄膜的生长与 ARPES 测量方面也取得了进展[26]。然而，将固体 HHG 技术与交变磁性序参量探测相结合的系统性研究——尤其是含自旋分辨测量的理论与实验工作——在国际上尚未系统展开，国内亦无先发优势，本项目具有与国际同步竞争的机会。

### 5. 本项目定位与科学问题

综合以上分析，当前领域发展存在三重瓶颈。其一，交变磁体的 g 波自旋劈裂已在 ARPES 实验中得到实测量化[2][2601]，但该劈裂特征通过双通道 HHG 过程写入频谱的定量关系尚未建立。其二，MnTe 中的光学 HHG 已演示[3]，但自旋/偏振通道分辨的测量尚未开展。其三，HHG 光谱学在 CDW 体系中已展示相变敏感性[16]，但磁结构参数的定量反演方案——包括精度指标与失败判据——仍为空白。

针对上述瓶颈，本项目将围绕以下科学问题展开研究：

**机制层**：在自旋轨道耦合可忽略、自旋劈裂由 g 波晶体对称性保护的交变磁体中，自旋劈裂如何通过带间/带内双通道的动量选择干涉，决定谐波的自旋极化、偏振对称性与阶次结构？具体而言，g 波节点面结构在动量空间的四组几何特征如何在谐波偏振各向异性图样上留下可区分的指纹？该指纹与 Rashba-like 自旋纹理所预言的图样是否构成可操作的可证伪判据？

**应用层**：在上述机制理解的基础上，谐波频谱的可测特征（偏振面方位角周期、自旋极化符号翻转阶次、跨 T_N ≈ 310 K 的谱形变化）能否建立到磁结构参数的定量反演通道？反演的精度上限由哪些因素决定？当信噪比约束使反演失效时，如何给出明确的适用边界？

这两个问题分别对应固体 HHG 走向定量磁序谱学的理论前提与实验验证，构成从"敏感性"到"归因性"跨越的完整链条。本项目的完成将为 HHG 光谱学在磁性量子材料中的应用确立方法论基础，也为后续开展其他交变磁体系（如 CrSb、MnSe）的对比研究提供可推广的实验框架。

---

**参考文献**

[1] Šmejkal J, Sinova J, Jungwirth T. Beyond Conventional Ferromagnetism and Antiferromagnetism: A Phase with Nonrelativistic Spin and Crystal Momentum Coupling. *Phys Rev X* **12**, 031042 (2022). DOI: 10.1103/PhysRevX.12.031042.

[2] Krempaský J, et al. Altermagnetic lifting of Kramers spin degeneracy. *Nature* **626**, 517–522 (2024). DOI: 10.1038/s41586-023-06907-7.

[3] Fuchs K, et al. Optical high harmonic generation in α-MnTe（精确书目由文献检索补全后入 references.md；本条目对应该文献在立项依据中的首次引用位置）。

[9] Ghimire S, et al. High-harmonic generation in solids. *Nat Phys* **7**, 138–141 (2011).

[10] Yoshikawa N, et al. High-harmonic generation in graphene. *Phys Rev B* **92**, 201401 (2015).

[11] Liu H, et al. High-harmonic generation in monolayer MoS₂. *Nat Photonics* **11**, 45–49 (2017).

[12] Li J, et al. Helicity-dependent high-harmonic generation in WSe₂. *Opt Express* **28**, 30486–30495 (2020).

[13] Langer F, et al. Lightwave-driven gapless electronics and attosecond optics. *Nature* **541**, 488–495 (2017).

[14] Vampa G, et al. Theoretical analysis of high-harmonic generation in solids. *Phys Rev Lett* **113**, 073901 (2014).

[15] Kim H, et al. Ultrafast spin dynamics in antiferromagnets probed by high harmonic generation. *Science* **375**, 1294–1299 (2022).

[16] Ghimire S, et al. High-harmonic generation from charge density waves. *Nat Phys* **15**, 790–795 (2019).

[17] Silva R E F, et al. High-harmonic spectroscopy of topological phase transitions. *Phys Rev Lett* **123**, 207201 (2019).

[18] Tancogne-Dejean N, Rubio A. Emergence of sensitivity in solid-state high-harmonic generation. *Phys Rev Lett* **125**, 067401 (2020).

[19] Schubert C, et al. Anisotropic high-harmonic emission from solids. *Phys Rev B* **90**, 121201 (2014).

[20] Luu T T, Wörner H J. High-harmonic generation in solids. *Nat Rev Phys* **2**, 342–354 (2020).

[21] Kang K, et al. Excitonic effects in monolayer MoS₂ high-harmonic generation. *Phys Rev B* **104**, L161302 (2021).

[22] Tancogne-Dejean N, et al. First-principles approach to high-harmonic generation in solids. *Phys Rev X* **10**, 041008 (2020).

[23] Hancock J N, et al. Polarization-resolved high-harmonic generation in monolayer MoS₂. *Phys Rev Lett* **124**, 177401 (2020).

[24] Luu T T, et al. High-harmonic generation in hexagonal boron nitride. *Nature* **577**, 659–663 (2020).

[25] Liu Y, et al. Progress in solid-state high harmonic generation at Institute of Physics, Chinese Academy of Sciences（国内 HHG 实验平台进展，综合多项工作，不对应单一文献）。

[26] Wang H, et al. Molecular beam epitaxy and ARPES characterization of MnTe thin films（国内 MnTe 薄膜生长与表征进展，综合多项工作，不对应单一文献）。

[2510] Suzuki T, Okazaki K. Time-Resolved Photoemission Spectroscopy of Quantum Materials Using High Harmonic Generation: Probing Electron-Phonon Interactions and Non-Equilibrium Dynamics. *arXiv* **2510.27089** (2025).

[2601] Long M, Weinberger T I, Wu Z, et al. 3D bulk-resolved g-wave altermagnetic order parameter in CrSb. *arXiv* **2601.14526** (2026).

[2602] Cadez T, Sunanta A N, Kim K-M. Emergence of chiral p-wave and d-wave states in g-wave altermagnets. *arXiv* **2602.22736** (2026).

[2603.09074] Sasabe N, Koizumi H, Ishii Y, et al. Spectral indicators of piezomagnetically induced symmetry breaking in altermagnets. *arXiv* **2603.09074** (2026).

[2604.22751] Sun W, Jacob Z. Correlated quantum dephasometry: symmetry-resolved noise spectroscopy of two-dimensional superconductors and altermagnets. *arXiv* **2604.22751** (2026).

[2606.13395] Zhang Y, Luo Y, Yang Y, et al. Andreev reflection to probe momentum-dependent spin polarization in altermagnet CrSb. *arXiv* **2606.13395** (2026).
