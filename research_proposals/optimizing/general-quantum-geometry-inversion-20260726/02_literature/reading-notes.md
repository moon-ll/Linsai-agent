## 2604.25706

Confirmed: pre-print only, no journal yet. Now I have all the substance needed. Let me synthesize the structured notes.

---

调研主题：DFT+U 带隙有效性的统一证明（general-quantum-geometry-inversion-20260726 相关方法学基础）
来源：arXiv:2604.25706 — Burgess & O'Regan, "Validity of DFT+U band gaps in all its known functional forms" (2026/04/28, 37 pages, 5 figures, 1 table)
URL：https://arxiv.org/abs/2604.25706
作者单位：University College Dublin + Trinity College Dublin（爱尔兰）
类别：cond-mat.str-el (primary); cond-mat.mtrl-sci, physics.chem-ph, physics.comp-ph
资助：Taighde-Éireann GOIPG/2020/1454 + 12/RC/2278_P2（与 ERDF 共同资助）
未发表（preprint only）；致谢 Tim Gould

研究问题（Research Question）
- 论文要回答的核心问题是：在广义 Kohn-Sham（GKS）实际计算框架下，DFT+U（含 DFT+U+J、DFT+U+V、DFT+U+U↑↓、DFT+U+F、BLOR、jmDFT、DFT+UCI 等所有已知变体）所给出的单粒子本征谱带隙，是否在概念上合法地等同于材料的"基本带隙"（fundamental gap，由总能量差 E(N+1)−2E(N)+E(N−1) 给出）。
- 中心论点是：长期以来学界普遍引用 Kohn-Sham 定理的严格陈述——只有最高占据本征值对应电离能、因此只有 −ε_HOMO 物理意义合法——并据此怀疑 DFT+U 谱学结果。本文要推翻这种疑虑，证明在"无缺陷的完美周期体系 + 收敛 k 点采样"这一标准实际条件下，GKS 边界本征值差 ε_LUMO − ε_HOMO 严格等于该泛函自己的基本带隙；且对所有迄今发表的 DFT+U 型泛函均成立。
- 该问题的深层动机是：DFT+U 在强关联材料（3d 过渡金属氧化物、4f 镧系氧化物、过渡金属配合物）的光谱预测中"光谱好于总能量"是公认的经验事实，但概念合法性长期被质疑，从而阻碍其作为标准化、可靠性方法被进一步开发。

研究背景（Background）
- 背景脉络：局域/半局域 XC 泛函系统性低估带隙（著名的"带隙问题"），传统修补方式包括杂化泛函（Rung 4，含部分精确交换）和 DFT+U（Hubbard 校正）。DFT+U 因近乎零的计算成本和高可扩展性，在高通量筛选、大胞复杂物理（电池正极、多铁、催化剂、高温超导母体）模拟中几乎是唯一可行的方法。
- 关键文献基线：Anisimov 等（FLL、AMF，1991-1993）开启 DFT+U；Liechtenstein 1995（轨道分辨 U_{mm'} 与 Hund's J）、Dudarev 1998（单一有效 U_eff = U−J，是当今最常被使用的形式）；后续扩展包括 DFT+U+J（2007）、DFT+U+U↑↓（自旋分辨双 U，2014）、DFT+U+V（位点间 V，2015）、DFT+U+F（2017）、jmDFT（2014）、BLOR/mBLOR（2014-2016）、DFT+UCI（2016）、Petukhov（2003）、Seo（2007）、非共线版本（Dudarev 2005）。本文首次用统一记号穷举这些变体。
- 前期理论推进：Ref. 192（Yang 等）已证明对纯局域/半局域泛函在晶体上的本征值带隙合法；Ref. 204（Kraisler 等）给出 GKS 框架下总能量变分的逻辑起点；本文将 Ref. 192 的论证方法推广到 DFT+U（含杂化泛函），并显式纳入赝势、PAW、自旋极化等实际条件。
- 现实驱动：DFT+U 历史三十年、发表论文数量众多（图 1 即统计），但学界已反复发现其"总能量在不同化学计量间不可比"，系统依赖 U 参数的拟合；故澄清带隙合法性成为发展下一代可靠 DFT+U 型泛函的必要前提。

研究方法（Methods）
- 方法论主干：解析证明 + 统一记号综述 + 极端解析模型（hydrogen lattice in Mott-Hubbard limit）。
- 关键推导路径：作者以 Ref. 204 的 GKS 总能量构造和变分逻辑为出发点，考虑可能非整数的电子数 N（统计混合系综）以及实变分占据数 f^i；写出带 Lagrange 乘子（正交归一约束、占据约束）的总能量泛函。对占据数 f^i 取导数并代入 Janak 定理，得到边界本征值 ϵ_F 对 f_F 的导数表达式（Eq. 18–23），该导数由 Hxc 核与 Fukui 函数卷积、以及 Hubbard 非局域势贡献组成。
- 核心论证（Section III）：证明在无缺陷周期体系中，对最高占据（H）和最低未占据（L）边界本征值，导数 dϵ_F/df_F 中所有项的贡献之和在无穷密 k 点采样下严格为零，从而使 ϵ_L − ϵ_H 不依赖 f，从而与基本带隙的总能量差定义严格一致。
- 分类综述（Section IV–VII）：对每一已知 DFT+U 变体（FLL/AMF 双计数、原始 Dudarev/Liechtenstein、扩展型 +J/+U↑↓/+V/+F、flat-plane 条件派生 jmDFT/BLOR/mBLOR/DFT+UCI、自旋-轨道/非共线），用统一记号重写其能量泛函，逐项解析验证"本征值带隙 = 基本带隙"的成立条件，并将所需固化的辅助参数（U、J、V、F₁-F₄、α、参考占据 {n₀}、投影基轴等）汇总成一张 17 行的"checklist 表"（Table 1）。
- 附录延伸：将证明推广到范数守恒赝势（Appendix B）、超软赝势与 PAW（Appendix C）、自旋非限制 GKS（Appendix D）；并在 Appendix A 用锂原子 vs. 锂离子/锂负离子案例显式说明"显式导数不连续性"（explicit derivative discontinuity）的必要性。
- 数值/解析测试：以氢原子点阵在无穷分离极限下作为"最接近 Hubbard 模型"的化学系统，分自旋极化（n^↑=1, n^↓=0）和非自旋极化（n^σ=0.5）两种情形，对各 DFT+U 变体在 U=5 eV、J=1 eV、V=0 eV 下非自洽地计算对带隙的修正量 ΔGKS^σ，绘制图 3、图 4；并对 d 轨道在八面体/四面体晶场下的子空间占据本征值 λ^σ_eg 与 λ^σ_t2g 给出 Dudarev 带隙修正的解析曲面（图 5）。

主要发现与核心结论（Main Results）
- 主定理：对"无缺陷完美周期体系 + 充分收敛 k 点采样"，DFT+U（含其全部已知变体）和杂化泛函给出的 GKS 本征值差 ε_LUMO − ε_HOMO 严格等于该泛函自身的基本带隙；并且 −ε_HOMO 和 −ε_LUMO 分别严格等于材料的电离势和电子亲和势。这一定理对纯局域/半局域泛函（Yang 等已证）、杂化泛函（数值已证）、以及所有 DFT+U 变体（本文解析证明）一并成立。
- 成立条件（Table 1）：需在 N-1、N、N+1 三次总能量计算中固定 Hubbard 参数（U、J、V、F₁-F₄ 等）、固定双计数辅助参数（参考占据 {n₀}、α 等）、固定子空间投影算符的原子轨道基轴（对非幺正不变的泛函）；空间轨道形状亦须固化。对分段定义泛函（jmDFT、BLOR、mBLOR、DFT+U+F），需在三次计算中用同一段形式。
- 不成立条件（重要负结果）：在有缺陷体系或孤立体系（如分子）中，定理不成立；此时本征值带隙与基本带隙之差为"显式导数不连续性"（explicit derivative discontinuity），可通过 Kraisler-Gould 等的导数不连续性校正方案修补，但对缺陷体系与分子而言，直接做电子增删的总能量差计算通常比校正更经济。
- 氢点阵数值结果（图 3，自旋极化，U=5 eV）：Dudarev/Liechtenstein/Petukhov/Czyżyk(FLL)/DFT+U+J 等"标准"FLL 双计数族泛函都将带隙上调 4–5 eV（与 U 量级一致）；但 Anisimov'91（AMF）反而把 Kohn-Sham 带隙降低 5 eV；Czyżyk'94(AMF) 和 Pickett'98(AMF) 对带边无修正；BLOR 把带隙降低 2 eV；而其修正版本 BLOR+Δ_xc 把带隙上调 4 eV——意味着 BLOR 原始版对带隙修补无效。
- 氢点阵非自旋极化结果（图 4）：几乎所有 DFT+U 变体对带隙均无修正（带边同向同量平移）；唯一的显著例外是 BLOR+Δ_xc，把带隙上调 6 eV。这是当前 DFT+U 族群在处理"金属性失效区间"时的关键短板。
- 显式导数不连续性的必要性（Appendix A，锂原子）：锂原子基态 1s²2s¹ 的基本带隙要求 HOMO↑–LUMO↓ 差 4.77 eV（IP−EA=5.39−0.62），而自旋翻转能要求同一本征值差为 0 eV；这两个条件无法同时满足，证明精确 GKS 泛函必须包含显式导数不连续性——这是 BLOR+Δ_xc 类修正的物理根据。
- 赝势/PAW 的兼容性：证明在范数守恒赝势、超软赝势和 PAW 势下均保持成立，使结论对几乎所有现行第一性原理软件（VASP、Quantum ESPRESSO、CASTEP 等）具有直接意义。

潜在研究方向（Future Directions）
- 下一代 DFT+U 泛函的设计方向（Section IX）：作者认为突破将来自两条路径——（a）"extended DFT+U"，即在 Hartree-Fock 启发的相互作用项中保留更多子空间平均参数；（b）"flat plane condition"，即通过对选定子空间施加更多精确条件，而非继续依赖 Hubbard 模型的导出。
- 关键开放问题之一：如何让 DFT+U 在"非自旋极化氢点阵"类金属性失效区间也能打开带隙。当前的标准 FLL/AMF 族泛函在此区间无法工作，BLOR+Δ_xc 是少数能给出修正的方向，但仍需验证其在实际金属氧化物上的稳定性。
- 自洽 U 计算的副作用：作者指出当用线性响应理论自洽确定 U 时，不同化学计量间的总能量直接可比性可能丧失（参 Ref. 143）；如何在"系统依赖的 U"与"跨化学计量的能量可比性"之间取得平衡是悬而未决的方法论难题。
- 显式导数不连续性的工程化：如何在 DFT+U 框架中高效、可控地引入类似 BLOR+Δ_xc 的显式 Δ_xc 项，以及它与现有赝势、PAW 实现、自旋-轨道耦合的兼容性，是将本文"概念合法性"转化为"实际可靠工具"的关键工程问题。
- 对超快/强场/量子几何反演方向的潜在启示（课题语境）：本文的方法学虽针对基态 DFT+U，但其"无缺陷周期体系 + 收敛 k 点"的合法性边界、以及"分段定义泛函在三次总能量计算中必须用同一段"的告诫，对任何依赖 DFT+U 给出母态能隙、再用其作为反演基线的方案（如用 DFT+U 得到的带隙/能带色散反演 Berry 相位、量子度规、Fubini-Study 张量）有直接参考价值——带隙合法性是量子几何反演可解性的第一道门槛。

补充笔记（写给后续 gap analysis / 项目维护）
- 这篇是方法学奠基类论文，与课题 general-quantum-geometry-inversion-20260726 的关联点在于：所有依赖 DFT+U 给出"基态带边结构"的量子几何反演框架，都隐含地依赖本文所证明的"DFT+U 本征谱带隙等于基本带隙"。因此这篇可作为"课题立项依据"环节的背书文献，标记为方法学基础支持。
- 论文 37 页、5 图 1 表，结构非常完整（理论证明 → 分类综述 → 检验清单 → 极限模型验证 → 赝势/PAW/自旋附录），适合在反演框架"研究方法"章节引用为 GKS 本征谱可解释性的引用点。
- 缺陷体系与孤立体系的不成立条件，是反演方法从晶体扩展到缺陷态/分子/团簇时需要补充导数不连续性校正的明确警示。
- 关键词建议：DFT+U bandgap validity, GKS eigenvalue, fundamental gap, derivative discontinuity, Hubbard U, Liechtenstein, Dudarev, BLOR, mBLOR, DFT+UCI, flat plane condition, hydrogen lattice, Mott-Hubbard, self-consistent U, linear-response U, pseudopotential, PAW。

文献定位
- arXiv ID：2604.25706（v1, 2026-04-28）
- 作者：Andrew C. Burgess, David D. O'Regan（UCD + Trinity College Dublin）
- DOI：尚未分配（preprint 阶段）
- 篇幅：37 页，5 图，1 表，4 附录
- 类别：cond-mat.str-el（首要）；cond-mat.mtrl-sci；physics.chem-ph；physics.comp-ph


## 2606.16108

Excellent. I have comprehensive content. Let me compile the structured note now.

---

## 调研主题
来源：[arXiv:2606.16108 — Optically Active Fractional Wannier-Center Displacement Drives Giant Second-Harmonic Generation](https://arxiv.org/abs/2606.16108)

**作者**：Hongsheng Pang, Lixin He（University of Science and Technology of China，中科大量子信息实验室 + 合肥国家实验室 + 合肥综合性国家科学中心人工智能研究院）  
**提交日期**：2026-06-15  
**学科分类**：Materials Science (cond-mat.mtrl-sci); Optics (physics.optics)  
**课题关联**：general-quantum-geometry-inversion-20260726（量子几何反演 → 这里指 Wannier 中心/Berry 相几何与非线性光学响应的连接）

---

## 研究问题（Research Question）

核心问题是：**能否将静态的、基于 Berry 相的体极化（formal polarization）转化为光学活性的几何机制，从而为非线性光学响应（特别是二次谐波产生 SHG 与移位电流 shift current）提供一种对称性指导的增强路径？**

更具体地讲，作者要回答的是：在非中心对称的量子化形式极化（Quantized Formal Polarization, QFP）晶体中，被占据态与低能未占据态的 Wannier 中心若落在不同的分数 Wyckoff 位置，对应的光学跃迁能否携带一个"格点尺度"的实空间位移，并由此产生一个巨大的"shift vector"（移位矢量），从而主导静态 SHG 与 shift-current 响应？

中心论点：对称性量子化的形式极化虽然是一个基态属性，但通过占据态与未占据态分别位于不同分数 Wannier-center 扇区之间的光学跃迁，它可以"变成光学活性"，这为巨型 SHG 与移位电流响应提供了一条对称性引导的几何路线。

---

## 研究背景（Background）

- **领域地位**：SHG 与 shift current 是非中心对称晶体中最典型的二阶非线性光学响应，应用涵盖频率转换、非线性光子学、光电子学，以及对称性分辨的材料表征（Shen 1984；Li 2021；Ngo 2022；Fiebig 2005 等）。其大小不仅由带隙、光学跃迁矩阵元决定，还强烈依赖电子波函数的"几何结构"（Sipe & Shkrebtii 2000；Fregoso 2017）。

- **关键几何量——shift vector**：在 Sipe–Shkrebtii 框架下，shift vector 描述了电子波包在一次光学跃迁中的实空间位移，它进入 SHG 静态极化率与 shift-current 响应的"带内（intraband）"贡献。其在布里渊区的平均值受"连接初末态的 Berry 相差"控制（Rashkeev 1998；Sturman & Fridkin 2021；Qian 2022）。

- **现代极化理论**：King-Smith & Vanderbilt 1993 指出，绝缘体的形式极化由占据 Wannier 中心位置相对于离子骨架决定（模一个极化量子）。Resta 1994、Vanderbilt 2018 的 Berry 相表述给出了规范的、可测量的几何定义。

- **本团队前期工作（QFP 框架）**：Pang & He 2025a (PRL) 提出"广义 Neumann 原理"将分数量子铁电与常规铁电统一在形式极化被对称性量子化的图像下；2025b 进一步重新定义极性界面的极化失配；2026 又指出 QFP 失配可驱动绝缘体-金属转变。这些工作确立了"分数 Wyckoff 位置上的占据 Wannier 中心"作为体相不变量。

- **关键观察（动机）**：在 QFP 晶体中，占据态与低能未占据态可能分别处于不同的分数 Wannier-center 扇区。这意味着允许的光学跃迁自然携带一个分数 Berry 极化差，是潜在的巨型 SHG 几何来源。

---

## 研究方法（Methods）

1. **几何机制推导**：
   - 从 Rashkeev–Sipe–Shkrebtii 框架出发，把静态 SHG 极化率分解为 interband（带间，由矩阵元乘积构成）和 intraband（带内，含矩阵元对 k 的协变导数）两部分；
   - 证明 intraband 项含有几何因子 |r|²·R（光学矩阵元强度 × shift vector），且 shift-current 响应也正比于同一个 |r|²·R；
   - 利用 Fregoso 2017 的 Berry 相公式 −e∫dk R_mn = Q W_mn + P_m − P_n，建立"布里渊区平均的 shift vector"与"初末带 Berry 相极化差"的直接联系。

2. **第一性原理筛选**：
   - 从 C2DB 数据库（Haastrup 2018；Gjerding 2021）筛选二维非磁性绝缘体，HSE+SOC 带隙 > 1.0 eV；
   - 限定点群为 C3、D3、C3v、C3h、D3h（同时允许面内 SHG 与 QFP 分支）；
   - 共得到 74 个零 QFP 候选与 161 个非零 QFP 候选。

3. **软件与参数**：
   - 使用 ABACUS 软件包（Li 2016；Chen 2010；Lin 2024, 2021），HSE 杂化泛函（Heyd 2003；Lin 2020），含自旋轨道耦合；
   - 紧束缚哈密顿量喂给 PYATB（Jin 2023）计算 Berry 相极化、shift-current 与 SHG 极化率；
   - Wannier 函数与分数 Wyckoff 位置逐带构建；动量分辨的 R、|r|²、|r|²·R 在 BZ 内作图。

4. **材料分析**：
   - 重点讨论两个二维代表：InPS3（P312, D3，作为"干净"模型）与 InNbBr6（同点群，最大响应）；
   - 三维验证材料：CdBiO3（放在 SM 中）。

---

## 主要发现与核心结论（Main Results）

1. **QFP 候选显著富集巨型 SHG**：在 C2DB 筛选中，非零 QFP 组的"大响应材料"占比明显高于零 QFP 组。HSE+SOC 下静态 SHG 极化率前三名都属于非零 QFP 类：
   - InNbBr6: **0.70 nm²/V**
   - AgAlAs₂Se₆: 0.33 nm²/V
   - InPS3: 0.23 nm²/V

2. **InPS3 是"干净"模型**：总 χ⁽²⁾ = 0.23 nm²/V 中，带内（intraband）贡献为 **+0.24**，带间（interband）贡献为 −0.01。即整响应几乎完全由 shift-vector 带内通道主导。
   - 最高占据带 Wannier 中心在 In1 位的分数 Wyckoff (2/3, 1/3)；
   - 最低未占据带 Wannier 中心在 In2 位的 (1/3, 2/3)；
   - 二者 P_occ = (2/3, 1/3)、P_unocc = (1/3, 2/3)，正好对应 P312 对称性允许的 QFP 分支；
   - 在 BZ 的大部分区域，shift vector R 都很大，且 |r|²·R 在 k 空间分布明显，证实 Wannier 中心位移是"光学活性"的。

3. **InNbBr6 是最大响应材料，但有显著带内/带间抵消**：总 χ⁽²⁾ = 0.70 nm²/V，但分解后 intraband = **+1.44**、interband = −0.74（部分抵消）。机制同样成立：
   - 占据带边态主要局域在 In 子格，对应 P_occ = (1/3, 2/3)；
   - 选定低能未占据态主要局域在 Nb 子格，对应 P_unocc = (2/3, 1/3)；
   - 二者跨不同分数 Wannier-center 扇区，再次提供大 BZ 平均 shift vector。

4. **从 PBE 到 HSE 的对比**：在 PBE 水平，InNbBr6 的带隙被低估到 0.92 eV，χ⁽²⁾ 被高估到 1.18 nm²/V。这表明 HSE+SOC 结果是"保守下界"，但仍使这些材料位居已知 2D 非线性光学强候选之列。

5. **三维材料中机制同样成立**：CdBiO3（SM 中）作为 3D 例子展示了相同的"分数 Wannier-center 跨扇区跃迁"机制，说明该几何原理不局限于二维体系。

6. **核心物理图像总结**：对称性量子化的形式极化本身只是基态属性；但当 QFP 晶体的占据带与低能未占据带分别位于不同分数 Wannier-center 扇区时，光学跃迁的 Berry 极化差（实空间位移）就是"格子尺度"的，自然放大 shift vector 与 intraband SHG 贡献。这为"对称性指导设计高性能非线性光学材料"建立了一条清晰的物理准则。

---

## 潜在研究方向（Future Directions）

1. **从二阶到高阶**：现有推导聚焦静态 χ⁽²⁾ 与 shift-current σ^abb(ω)；机制能否自然延伸到 χ⁽³⁾、三阶谐波、或者 HHG 高次谐波谱学（与强场动力学衔接）？QFP 晶体的 Wannier 中心分数扇区图像是否也编码在 TDDFT 实空间轨迹中？

2. **三维体系的系统化探索**：作者只在 SM 中给了一个 CdBiO3 例子，3D QFP 晶体中是否普遍存在巨大的 χ⁽²⁾？是否能为现有最强的红外/THz NLO 材料（如 GaAs、BaTiO₃、LiNbO₃）提供新的几何理解？

3. **带间-带内抵消的物理后果**：InNbBr6 的 interband = −0.74 nm²/V 强烈抵消了 intraband 的 +1.44，这种抵消是材料特异性还是 QFP 几何的普遍后果？能否用对称性或 Berry 相结构预测抵消的方向，从而筛选"未被抵消的"超大 χ⁽²⁾？

4. **温度、应变与相变对几何机制的影响**：QFP 框架本团队 2026 的工作指出 QFP 失配可驱动绝缘体-金属转变。QFP 跃迁或外加应变下"分数 Wannier 中心扇区"如何移动？能否动态地调制 χ⁽²⁾ 甚至实现光学开关？

5. **与 Berry curvature/quantum metric 的衔接**：课题名"quantum-geometry-inversion"暗示要从量子几何量（Berry curvature、quantum metric）反演材料参数。本工作主要使用 Berry 相极化（静态几何），是否可以把 quantum metric、Fubini-Study 度规也纳入 shift-vector 与 χ⁽²⁾ 的几何分解？这是把"几何量 ↔ 可测光学量"做成更完整反演问题的重要开放方向。

6. **实验验证与材料合成**：InPS3、InNbBr₆、AgAlAs₂Se₆、CdBiO₃ 是否已有实验报道的 SHG/shift-current 数据？实验上能否用偏振分辨 SHG + ARPES 直接"看见"分数 Wyckoff 中心？

7. **计算方法的局限**：
   - 仅在 HSE+SOC 水平报告数值，未考虑激子修正与 GW 修正；二阶响应在低维体系中对电子-电子关联较敏感；
   - 评估以"静态 χ⁽²⁾"为主，对真实 SHG 实验更常用的频域 χ⁽²⁾(2ω; ω, ω) 与 shift-current 谱仍以 SM 频谱为主，未做系统性数据库化；
   - "Wannier 中心"在纠缠能带（如 InNbBr6 多带情形）下用"分电荷密度求和"近似，方法论可进一步规范化。

来源：所有内容均来自 arXiv:2606.16108v1（HTML 全文与摘要）。


## 2511.13114

调研已完成。论文全文已通过 arXiv 与本地 PDF 解析获取，下面是结构化笔记（基于论文 v3，2026-05-18 更新版）。

────────────────────────────────────────
## 研究问题（Research Question）

论文的核心问题是：能否在二维单层 WS₂ 中通过两条"正交互不干扰"的控制维度——双色激光场的相对相位 Δφ（亚飞秒光学控制）与机械应变 ε（静态材料工程）——实现对高次谐波产生（HHG）的精确、独立且协同的调控，并以此作为探测和映射材料量子几何（特别是 Berry 曲率）的全光学探针。

中心论点：单层 WS₂ 的 HHG 主导机制为带间跃迁（贡献 >90% 总强度），而垂直极化谐波 Py 主要由带内异常速度（Berry 曲率 Ω 的横向分量）驱动；双色相位通过调控电子-空穴相干性来优化产额与截止能量，应变通过改带结构和 Berry 曲率来重塑偏振通道，两者形成正交、可叠加的双模控制框架。

────────────────────────────────────────
## 研究背景（Background）

HHG 作为强场物理的核心非线性现象，自 Ghimire 等人（2011）在块体晶体中首次观测到以来，在原子、分子、固体三大体系中均被广泛研究；固体 HHG 因晶格周期性和高电子密度展现出与气相截然不同的机制（interband 三步模型 + intraband 布洛赫振荡），被认为是紧凑型 EUV/阿秒源的理想载体。

二维材料（graphene、hBN、TMDs）兼具类原子与类块体响应的"双面性"——例如 hBN 在面外偏振下呈原子-like、面内偏振下呈块体-like，使其成为连接阿秒物理与凝聚态物理的桥梁。

在此前的 TMDs 应变研究中，Guan 等（2019, MoS₂）发现压应变通过平带化增强带内电流从而提升 HHG；而 Kim 等（2025, Nat. Commun. 16:9825）已证明单层 WS₂ 的 HHG 在 BZ 内存在 Γ 与 M 点之间的量子干涉贡献。本文的动机正是填补"WS₂ 中应变-量子几何-HHG"耦合机制这一空白，并将光学相位调控引入静态应变研究未曾触及的量子相干自由度。

带内（intraband）和带间（interband）机制在固体 HHG 中的相对主导性因材料和谐波阶数而异；NbOCl₂ 平带体系中带间极化主导，MoS₂ 应变中带内主导，WS₂ 中何者主导仍待澄清——本文正是要回答这个问题。

────────────────────────────────────────
## 研究方法（Methods）

计算方法：实时含时密度泛函理论（rt-TDDFT），使用 Octopus 代码实现；ALDA 泛函 + HGH 范数守恒赝势；实空间网格 0.21 Å（截断能 ~850 eV），保证高能导带态的准确描述；布里渊区采样采用 36×36×1 Monkhorst-Pack 网格，完整捕捉 BZ 范围内的电子动力学（包括 Γ 与 M 点贡献）。

激光设置：基频光 ħω₀ = 0.517 eV（λ₀ = 2400 nm，中红外）+ 二次谐波（ω₁ = 2ω₀）线性叠加；高斯包络 τ = 12 fs（1/e 强度时长 24 fs，FWHM ≈ 28.3 fs），中心 t₀ = 50 fs；基频光强 I₀ = 1×10¹² W/cm²；激光沿 x 轴（zigzag 方向）线偏振。

关键控制参数：双色场相对相位 Δφ（0 → 2π 扫描）、双色场振幅比 β（=0, 1）、激光强度（0.6–1.0×10¹² W/cm²）、双轴应变 ε（−4% 到 +4%，重点考察 −2%、0%、+2%）。

诊断工具：(1) 偏振分解的 HHG 谱（P∥ 与 P⊥ 分量）；(2) Gabor 小波时-频分析 S(t,ω)，揭示亚周期电子动力学；(3) 含时轨道投影（VBM-n 到 CBM+m 的占据数），追踪电子-空穴对的相干 Rabi 振荡；(4) Berry 曲率沿高对称路径 Γ-K'-M-K-Γ 的计算；(5) 半经典三步模型解释。

材料基态：LDA 计算单层 WS₂ 直接带隙 1.7 eV（实验 2.0 eV），K/K' 谷处存在大 BC（自旋轨道耦合+反演对称破缺导致）；晶格常数 a = 3.186 Å。

────────────────────────────────────────
## 主要发现与核心结论（Main Results）

机制归属（定量）：通过轨道投影分析证实 Px 平行分量贡献总强度 >90%，源自带间跃迁；Py 垂直分量虽较弱（~10%），但由带内异常速度主导，对 Δφ 高度敏感。

双色相位控制：Δφ ≈ 0.7π 时 HHG 总产额最大（总产额调制 ~10%，高能平台 4–30 阶调制 ~22%），Δφ = 0 和 π 时产额最低；Gabor 时频分析显示 Δφ = 0.7π 下 |A(t)| 呈多峰结构，维持 VBM-n↔CBM+m 间的持续 Rabi-like 相干振荡，保证电子-空穴相位锁定，利于相干复合；Δφ = π 下 |A(t)| 单峰主导，相位快速失同步，导致破坏性干涉并大幅压制高能谐波。

应变控制（核心新结果）：拉伸应变 +2% 时 Py 垂直谐波分量从 1467.0 a.u. 提升至 2894.6 a.u.——接近翻倍；与之定量对应，K 谷附近的积分 Berry 曲率从 18.24 Å⁻² 增加到 26.86 Å⁻²（线性乘子关系）；压应变 −2% 时直接-间接带隙转变引入 K 谷处 VBM-CBM 动量失配，带间跃迁偶极矩阵元大幅下降，HHG 显著猝灭。

与 MoS₂ 工作的对比：Guan 等发现 MoS₂ 压应变通过平带化增强带内电流提升 HHG；而 WS₂ 中压应变反因直接-间接带隙转变抑制带间主导的发射——表明 TMDs 的非线性响应具有强材料特异性，取决于带拓扑与载流子相干性的微妙竞争。

正交协同效应（Fig. 8 二维相图）：总谐波产额随应变变化约 27.6%（主要由 Px 主导）；Py 分量对应变更敏感（近翻倍）；拉伸应变 + Δφ = 0.3π 附近产额最高，相位调制在拉伸态下最为有效，在压缩或无应变态下相位调控几乎失效——证明光学相位控制以有利的能带/BC 为前提。

异常速度的解析推导：v(k) = ∇_k ε(k) − ḟ × Ω(k)，代入 ḟ = −eE(t) 与 E∥x̂, Ω∥ẑ 后横向电流 Jy ∝ |E(t)|·Ωz(k)，确认 BC 增大直接线性放大 Py。

────────────────────────────────────────
## 潜在研究方向（Future Directions）

LDA 泛函限制：当前计算的单层 WS₂ 直接带隙为 1.7 eV（实验 2.0 eV），虽不影响拓扑/对称性定性结论，但会影响截止能量等定量预测；未来需采用混合泛函（HSE06）或 GW 校正以精确定量能带边缘位置，特别是绝对截止能量。

缺陷与噪声的定量边界：本文定性论证了中等 S 空位（局部散射中心）不会抹除全局量子几何信号，但未给出缺陷密度上限；需要后续引入显式无序、缺陷和激光噪声模型，定量映射"拓扑鲁棒性边界"。

更广材料的拓展：当前以 WS₂ 为模型系统；该正交控制框架可推广到其他 2D TMDs（MoS₂、WSe₂、MoSe₂）、双层/异质结、扭转多层（moiré）以及拓扑材料（Weyl 半金属、Dirac 半金属），以检验带拓扑-量子几何-HHG 的普适关系。

量子度规而非仅 BC 的角色：本文聚焦 Berry 曲率（反常速度），但 Fubini-Study 量子度规对非线性响应的贡献（特别是带内轨道磁化项）尚未涉及；未来需结合完整量子几何张量（BC + 量子度规）进行 HHG 重建与反演。

实验验证：±2% 双轴应变已可通过柔性衬底/纳米气泡工程实现；亚飞秒双色相位控制已是阿秒光谱学基石；但将两条控制维度同时集成（应变台 + 双色干涉稳定相位）仍需实验端工程化。

极端应变与相变：>±3% 应变超出当前实验常规范围，可能进入新结构相（金属化、超导、CDW）；探索这一区间内 HHG 对结构相变/电子相变的灵敏度是开放问题。

高阶多体与强关联效应：本文在冻结离子近似下求解 rt-TDDFT，未包含电子-电子强关联与声子辅助激发；将多体动力学（GW-BSE、双激子、声子耦合）纳入 HHG 计算是下一步的理论方向。

应用前景：论文明确指出该框架可设计"高度可调谐的固态 EUV 光源"，并用于超快光谱学和阿秒科学；Py 通道作为全光学量子几何探针的概念可推广至非接触式应力/应变映射。

────────────────────────────────────────

来源：arXiv:2511.13114v3 [physics.comp-ph]，Zhao et al., "Orthogonal Attosecond Control of Solid-State Harmonics by Optical Waveforms and Quantum Geometry Engineering"，提交 2025-11-17，最新修订 2026-05-18。DOI: https://doi.org/10.48550/arXiv.2511.13114。PDF 已下载至 /tmp/2511.13114.pdf（42 页）。


## 2604.13729

I have all the information I need. Let me compose the structured research notes.

---

## 论文信息- **标题**: Nonlinear Circular Dichroism Reveals the Local Berry Curvature
- **arXiv ID**: 2604.13729
- **作者**: Nele Tornow, Paul Herrmann, Clemens Schneider, Ferdinand Evers, Jan Wilhelm, Giancarlo Soavi
- **分类**: cond-mat.mes-hall (主); physics.optics
- **发布日期**: 2026-04-15
- **来源**: https://arxiv.org/abs/2604.13729v1

---

## 研究问题（Research Question）
论文的核心研究问题是：**在非线性光学（具体为晶体高次谐波产生）的角动量守恒表象之下，光与晶体之间转移的角动量是否具有可观测的微观量子几何起源？** 传统非线性光学依赖宏观对称性论证，将圆偏谐波产生解释为对晶格施加的"扭矩"或反向的非线性旋转多普勒位移，但这些图像无法揭示角动量转移的微观机制。作者试图证明，光→晶体的角动量转移量在特定光学共振处正比于局域 Berry 曲率，从而在宏观守恒律与电子量子几何之间建立一条直接的定量等式。

## 研究背景（Background）
该工作处于三个研究领域的交汇点：（1）**固体高次谐波（HHG）**——自 Ghimire 等 2011 年首次在氧化锌中观测到以来，已成为探测晶体电子动力学和阿秒过程的成熟平台；（2）**Berry 曲率与量子几何**——作为能带拓扑的局域表征，已被证明支配着反常霍尔效应、磁光响应等线性输运，但向非线性光学领域的延伸仍是开放前沿；（3）**非线性圆二色性（nonlinear circular dichroism）**——在 SHG/THG 中作为对称性探针长期使用，但其在量子几何意义上的解读尚不充分。论文的研究动机正是要填补这一空白：利用单层半导体中的谐波 CD 作为"探针"，将角动量守恒律重新表述为 Berry 曲率的局域可观测信号。

## 研究方法（Methods）
论文采用**理论与实验结合**的路线：
- **理论**：从角动量守恒律出发，推导圆偏谐波产生中向晶体转移的角动量表达式，证明该量在某一光学共振频率处等于局域 Berry 曲率的函数；这要求超越宏观对称性论证，进入包含能带量子几何（Berry 连接、曲率、量子度规）的非线性响应张量计算。
- **实验**：在被选为"原子薄半导体"的二维材料（典型为单层过渡金属硫族化合物，monolayer TMD，如 WSe₂/MoS₂ 系列）上测量非线性谐波圆二色性。圆偏驱动场激发谐波，旋转偏振方向记录 CD谱，与基于 Berry 曲率的第一性原理/有效质量模型计算直接比对。
- **数据**：测量的非线性 CD 信号（特定谐波次数的左右旋强度差）作为 Berry 曲率读出。

## 主要发现与核心结论（Main Results）
- **核心定理**：在非线性谐波过程中，从光转移到晶体的角动量正比于该谐波对应光学共振处的局域 Berry 曲率，即 ΔJ ∝ Ω(k) 在共振 k 点的取值。
- **实验验证**：在原子薄半导体中实测的谐波 CD 信号与基于 Berry 曲率分布的理论预测一致——这意味着非线性 CD 不仅是对称性探针，更是 Berry 曲率的**全光读出**。
- **新物理图像**：将传统"扭矩"图像与量子几何联系起来；反过来，宏观旋转晶体的非线性旋转多普勒位移可被理解为 Berry 曲率的宏观表现。
- **方法学贡献**：建立了一种全光（all-optical）控制和读出局域 Berry 曲率的方法，为拓扑材料与能谷电子学提供光学探测工具。
- 与课题"量子几何反演"相关：HHG 光谱因此成为量子几何量的一个可**正向重建**的测量通道，反向问题（从 HHG 光谱反解 Berry 曲率）的可行性与这一正向映射密切相关。

## 潜在研究方向（Future Directions）
- **多带/量子度规扩展**：当前结论聚焦 Berry 曲率在某一共振处的贡献；量子度规（quantum metric）及其它几何张量分量在谐波过程中的角色，特别是与 Fubini-Study 度规、连接干涉项的非线性响应中的可分离性，仍是待解问题。
- **一般谐波次数 m 的标度律**：m > 1 的高阶谐波 CD 是否仍保持"正比于局域 Berry 曲率"的简洁关系，还是会引入多 k 点积分/混合，需要系统研究。
- **超越单层 TMD 的体系**：扭转双层（moiré）、磁性拓扑材料、altermagnet 等具有更复杂 Berry 曲率分布（k-space 多极结构）的体系中，CD读出的空间分辨率与定量保真度尚待检验。
- **HHG 反演框架中的几何反问题**：能否从测得的多阶谐波 CD 谱反解出 Berry 曲率在动量空间的二维分布？这与本课题立项的"quantum geometry inversion"直接相关，构成本论文方法的应用延伸。
- **实验精度限制**：非线性 CD 信号微弱，易受激射涨落、衬底效应、温度漂移影响；发展高灵敏度的差分探测方案是关键工程瓶颈。
- **强场效应**：高强度驱动下 Berry 曲率定义本身是否需要含时/含场修正（Floquet 几何、瞬态 Berry 曲率），是理论与实验的开放边界。

---

**课题关联分析**
本论文是课题 general-quantum-geometry-inversion-20260726 的关键一篇——它为"量子几何量可由 HHG 光谱读出"提供了正向证明，是建立"量子几何反演问题"（从 HHG 光谱反解 Berry 曲率/量子度规）的物理基础之一。下一阶段在研究内容/方案章节，应以此为锚点展开"反问题是否良定、正则化方案、k-空间分辨率与噪声敏感度"等讨论。


## 2608.01096

## 调研主题：general-quantum-geometry-inversion-20260726

### 论文信息

- **标题**：*Time-dependent Berry curvature and quantum metric of Floquet-Bloch states*  
- **作者**：S. Sajad Dabiri、Reza Asgari  
- **作者单位**：浙江师范大学物理系；伊朗基础科学研究所（IPM）量子物理与物质学校  
- **arXiv 编号**：[2608.01096](https://arxiv.org/abs/2608.01096)  
- **版本**：v1，2026 年 8 月 2 日提交  
- **主要分类**：cond-mat.mes-hall  
- **全文**：[HTML](https://arxiv.org/html/2608.01096)；[PDF](https://arxiv.org/pdf/2608.01096)  
- **检索说明**：当前工具集未提供独立的 `web_search` 接口，因此使用 arXiv 官方 API、HTML 全文和 PDF 完成论文信息核验与深度阅读。

**摘要概述：**  
论文将静态 Bloch 带中的 Berry 曲率与量子度规推广到周期性驱动的 Floquet-Bloch 态，并直接在 Floquet 态基底中定义时间依赖的量子几何张量。该框架推导出光学求和法则，解释理想 Floquet 带占据条件下谐波频率处第一阶直流 Hall 和纵向光学电导的消失。论文进一步提出同时包含时间与动量导数的混合 Berry 曲率，并将其与无需绝热演化的量子化电荷泵浦联系起来。时间方向上的量子度规被解释为 Floquet 带的能量涨落，混合分量则对应偏振—能量关联。作者还系统分析了时间反演、宇称、粒子—空穴、手性、旋转和反射等对称性，并通过 Rudner–Lindner–Berg–Levin（RLBL）模型及一个高度对称 Floquet 模型进行数值验证。

---

## 研究问题（Research Question）

1. 论文的核心问题是：能否在保留周期驱动系统完整微运动信息的同时，为 Floquet-Bloch 态建立一个同时包含 Berry 曲率、量子度规及其时间—空间混合分量的统一量子几何框架。  
2. 作者希望回答 Floquet 态的瞬时量子几何如何决定线性光学响应，特别是光学电导的谐波结构、时间分辨响应和光学求和法则。  
3. 论文还试图解释，混合的时间—动量几何量是否能够在不要求绝热参数变化的情况下产生量子化电荷泵浦。  
4. 另一个中心问题是，时间依赖量子度规是否具有直接的物理意义，例如能否表示 Floquet 带的能量涨落、偏振涨落以及偏振与能量之间的协方差。  
5. 最终，论文将上述问题统一为一个论点：周期驱动系统的光学响应、非绝热输运、拓扑泵浦、量子涨落和对称性约束，都可由同一个时间依赖量子几何张量描述。

来源：[arXiv:2608.01096，摘要与正文 Sec. I–II](https://arxiv.org/abs/2608.01096)

---

## 研究背景（Background）

1. 在静态 Bloch 能带理论中，Berry 曲率描述相邻动量点波函数之间的相位变化，通常与 Hall 响应、磁输运和 Chern 数等拓扑不变量相联系。  
2. 量子度规描述参数空间中相邻量子态之间的距离，控制波包扩散、介电响应、非线性光学以及超激发过程的若干性质。  
3. 对于周期驱动系统，Hamiltonian 满足 \(H(\mathbf{k},t)=H(\mathbf{k},t+T)\)，Floquet 态、准能量和 Floquet Brillouin 区取代了静态 Bloch 态和普通能带。  
4. 周期驱动能够产生静态系统不存在的拓扑相，例如反常 Floquet 拓扑绝缘体、Floquet 拓扑边缘态和拓扑泵浦，因此 Floquet 系统的拓扑结构不能只由某一瞬间的 Chern 数完整描述。  
5. 既有方法主要包括瞬时 Bloch 带、Sambe 扩展 Hilbert 空间和有效 Floquet Hamiltonian。瞬时带方法难以完整处理微运动，Sambe 方法扩大了 Hilbert 空间且物理图像较间接，而有效 Hamiltonian 主要描述一个驱动周期末的 stroposcopic 演化。  
6. 因此，论文指出：目前仍缺少一种直接在物理 Floquet 态基底中定义、保留完整时间依赖性、同时又与时间分辨光学实验相联系的系统性量子几何理论。

来源：[arXiv:2608.01096，Introduction，Sec. I](https://arxiv.org/abs/2608.01096)

---

## 研究方法（Methods）

1. 论文首先采用 Floquet 理论，将波函数写为  
   \[
   |\psi_\alpha(t)\rangle=e^{-i\epsilon_\alpha t}|\phi_\alpha(t)\rangle,
   \]
   其中 \(|\phi_\alpha(t+T)\rangle=|\phi_\alpha(t)\rangle\)，\(\epsilon_\alpha\) 为准能量。  
2. 通过一个驱动周期内的演化算符 \(U_T\) 获得 Floquet 态和准能量，并定义 Floquet 态基底下的时间依赖量子几何张量。其空间—空间分量可写为  
   \[
   \mathcal G_\beta^{mn}(t)
   =
   g_\beta^{mn}(t)
   -
   \frac{i}{2}\Omega_\beta^{mn}(t),
   \]
   其中量子度规 \(g^{mn}\) 是实对称部分，Berry 曲率 \(\Omega^{mn}\) 是虚反对称部分。  
3. 在 Berry 曲率定义中，作者使用 Floquet 态之间的 interband position matrix element  
   \[
   r^e_{\beta\alpha}
   =
   (1-\delta_{\alpha\beta})
   \langle\phi_\beta(t)|i\partial_{\mathbf k}|\phi_\alpha(t)\rangle.
   \]
   量子度规则由相同位置算符矩阵元的实部乘积构成，并具有规范不变性。  
4. 论文将光学电导按驱动周期作 Fourier 展开，利用 Floquet 态占据数、准能量和 interband position matrix elements 推导光学电导与量子几何量 Fourier 分量之间的求和法则。  
5. 作者进一步定义混合 Berry 曲率  
   \[
   \Omega_\alpha^{xt}
   =
   2\operatorname{Im}
   \sum_{\beta\ne\alpha}
   \langle\phi_\alpha|\partial_t\phi_\beta\rangle
   \langle\phi_\beta|\partial_{k_x}\phi_\alpha\rangle,
   \]
   并用它计算一个周期内的电荷中心位移。  
6. 数值验证采用 RLBL 周期驱动方格模型：每个原胞含两个无自旋原子，Hamiltonian 分为五个时间区间进行演化，动量范围为 \(-\pi<k_x,k_y<\pi\)。  
7. 此外，论文还构造了一个同时具有时间反演、宇称、粒子—空穴、宇称—粒子—空穴、宇称—时间、四重旋转和反射等对称性的五段式 Floquet 模型，用于检验对称性对量子几何张量的约束。

来源：[arXiv:2608.01096，Sec. II 与 Sec. III](https://arxiv.org/abs/2608.01096)

---

## 主要发现与核心结论（Main Results）

### 1. 建立时间依赖量子几何张量

1. 论文的核心结果是在 Floquet 态而非瞬时 Bloch 态或扩展 Sambe 空间中定义时间依赖的 Berry 曲率、量子度规和混合几何分量。该定义在零驱动频率极限下回到静态 Bloch 带几何，同时保留驱动周期内的完整微运动。  
2. 量子度规的实部描述 Floquet 态在动量—时间参数空间中的局域距离，Berry 曲率的虚部则描述其相位几何和拓扑性质。  
3. 时间方向上的量子度规满足  
   \[
   g_\alpha^{tt}
   =
   \langle E^2\rangle_\alpha(t)
   -
   \langle E\rangle_\alpha(t)^2,
   \]
   因而直接等于 Floquet 带的瞬时能量涨落。  
4. 类似地，\(g^{xx}_\alpha\) 对应偏振涨落，\(g^{xt}_\alpha\) 对应偏振与能量之间的协方差。由此，量子度规不再只是几何量，而成为描述 Floquet 态内部统计结构的统一语言。  
5. 该时间依赖几何量对规范变换保持不变；论文在附录 A 中分别证明了空间量子度规和时间方向量子度规的规范不变性。

### 2. 推导光学求和法则与谐波电导零点

1. 作者从 Floquet 光学电导的一般表达式出发，推导出光学电导与量子几何张量 Fourier 分量之间的光学求和法则。  
2. 在 Floquet 带为理想占据、每个带完全占据或完全空置的条件下，论文证明：对于 \(n\neq 0\)，第一阶直流 Hall 电导和谐波纵向电导满足  
   \[
   \sigma_{xy}^{[1]e(-n)}(n\Omega)=0,
   \qquad
   \sigma_{xx}^{[1]e(-n)}(n\Omega)=0.
   \]
   这里的零点针对驱动频率整数倍处的响应，而不是任意频率下的总电导均为零。  
3. 该结论的物理图像是：向上的 Floquet 边带跃迁与向下的光子辅助跃迁在理想占据条件下发生精确抵消，因此没有净的一阶直流响应。  
4. 与 \(n\neq 0\) 的结果不同，\(n=0\) 的 Hall 电导仍然可以量子化，其数值由占据 Floquet 带的 Chern 数总和决定。  
5. 在 RLBL 模型中，作者数值计算了 \(n=0,1,2,3,4,5\) 的 Hall 与纵向电导 Fourier 分量；前五个非零阶谐波在相应谐波频率处呈现论文所预言的零点。

### 3. 发现非绝热量子化电荷泵浦

1. 论文定义了同时包含动量导数与时间导数的混合 Berry 曲率 \(\Omega_\alpha^{xt}\)，并证明其在一个驱动周期内对动量和时间的积分是规范不变的。  
2. 对于具有非简并、准能量带隙且理想占据的 Floquet 带，一个周期内泵浦的电荷量等于占据 Floquet 带 Chern 数之和。  
3. 该结果将 Thouless 量子化泵浦从绝热参数调制推广到非绝热周期驱动情形：泵浦不需要外部偏压，也不需要额外缓慢调节另一组驱动参数。  
4. 论文指出，该机制不同于依赖边界态非对称占据或特殊边界偏压的非绝热泵浦方案，它是由占据 Floquet 带的体量子几何决定的内在泵浦。  
5. 在低频极限，时间依赖减弱，Floquet 态逐渐回到瞬时本征态，因此该机制自然包含通常的绝热 Thouless 泵浦结果。

### 4. RLBL 模型的数值结果

1. 在对称参数 \(J_1=J_2=J_3=5\pi/2\)、\(J_4=J_5=0\)、\(\delta=0\)、\(T=1\) 下，RLBL 模型的相带在 \(t=2T/5\) 处同时发生准能量 \(0\) 和 Floquet 区边界 \(\pi\) 附近的能隙闭合。  
2. 两个 gap closing 分别携带相反的拓扑电荷 \(+1\) 和 \(-1\)，并对应拓扑相变；该结果还与纳米带谱中的 Floquet 边缘态出现相一致。  
3. 当 \(\delta=0\) 时，宇称对称性要求 \(q^{xt}=q^{yt}=0\)，并要求混合 Chern 数 \(C^{xt}=C^{yt}=0\)，数值结果验证了这些约束。  
4. 在另一组参数 \(J=3\pi/2\)、\(T=1\)、\(\delta=0.5\pi/T\) 下，瞬时 Hamiltonian 始终保持时间反演对称性，但 Floquet 带本身获得 Chern 数 \(C_2=1\)。这体现了周期驱动诱导拓扑相的能力。  
5. 在 Floquet 区边界处发生带拓扑电荷为 \(+1\) 的 gap closing，并在 \(t>t_c\) 之后出现穿过动力学能隙的手性边缘态。  
6. 数值计算还显示，量子几何张量满足 isolated band 的几何不等式  
   \[
   \operatorname{Tr}(q^\beta)
   =
   q^{xx}_\beta+q^{yy}_\beta
   \ge C_\beta,
   \]
   以及相应的行列式/平方根不等式；由于该 Floquet 带满足 \(C_\beta=1\)，其量子权重的空间迹始终至少为 1。  
7. 当该模型的理想占据光学电导被计算后，时间平均纵向电导在有限频率范围内出现负实部。论文将其解释为 Floquet 边带之间允许向下跃迁所致，意味着传播探针场可能获得放大而不是单纯耗散。  
8. 光学响应在约 \(\omega=5\Omega\) 处仍保持有限，表明高阶 Floquet 边带具有有限的谱权重，光子辅助跃迁可以延伸到高谐波区域。

### 5. 对称性约束结果

论文给出的主要约束包括：

| 对称性 | 对量子几何或拓扑量的主要约束 |
|---|---|
| 时间反演对称性 | \(C_{xy}=C_{xt}=0\) |
| 子晶格（手性）对称性 | 总 Chern 数 \(C_{xy}=0\) |
| 粒子—空穴对称性 | 混合 Chern 数 \(C_{xt}=0\) |
| 宇称对称性 | \(q^{xt}=0\)，\(C_{xt}=0\) |
| 宇称—时间对称性 | \(\Omega_{xy}(t)+\Omega_{xy}(-t)=0\)，\(g_{xt}(t)+g_{xt}(-t)=0\) |
| 三重及以上旋转对称性 | \(q^{xx}=q^{yy}\)，\(q^{xy}=q^{xt}=C_{xt}=C_{yt}=0\) |
| 反射对称性 | \(q^{xy}=q^{xt}=0\)，\(C_{xy}=C_{xt}=0\) |

在完全对称的 Floquet 模型中，数值结果进一步验证了 \(q^{xx}=q^{yy}\)，并得到 \(q^{xy}=q^{yt}=C^{xt}=C^{yt}=0\)。

来源：[arXiv:2608.01096，Sec. II–IV，Table I，Figs. 1–4](https://arxiv.org/abs/2608.01096)

---

## 潜在研究方向（Future Directions）

1. **理想 Floquet 带占据问题**：论文的谐波电导零点和量子化泵浦结果均依赖“带完全占据或完全空置”的理想占据条件。实际 Floquet 态占据数并不一定满足普通 Fermi–Dirac 分布，而会依赖驱动开启方式、耗散、热效应和系统—环境耦合。  
2. **实验实现困难**：论文提出利用频率分辨和时间分辨泵浦—探测、太赫兹电导、偏振分辨光谱、圆二色性和时间分辨 ARPES 重建时间依赖量子几何量，但论文没有直接完成实验验证。如何从有限温、噪声和多谐波共存信号中提取 \(\Omega^{xy}\) 与 \(g^{xy}\) 仍是重要问题。  
3. **带隙与带交叉问题**：拓扑不变量和单带量子度规公式主要适用于准能量有能隙、带间非简并且 Floquet 态可以平滑追踪的情形。对于 Floquet 奇异点、准能量交叉和无序导致的局域化，需要对时间依赖几何量进行重新分类。  
4. **有限尺寸与数值截断问题**：论文主要采用理想化方格模型和有限动量网格计算；实际材料中还存在有限尺寸、边界无序、缺陷、声子耦合和多体相互作用，这些因素可能使理想几何关系发生修正。  
5. **相互作用 Floquet 系统**：论文明确指出未来可扩展到相互作用 Floquet 系统。需要研究时间依赖量子度规如何受到库仑相互作用、Mott 能隙、激子形成和多体重整化的影响。  
6. **无序、耗散与非厄米系统**：当前理论建立在幺正、封闭系统假设上。将时间依赖量子几何张量推广到无序、开放系统和非厄米 Floquet 系统，可能用于描述非互易输运、增益—损耗和复数 Berry 曲率。  
7. **非绝热泵浦的实验协议**：虽然论文给出了非绝热量子化泵浦的一般几何判据，但实际实现仍需发展快速开关 Floquet 态制备、特定频率的驱动控制、理想占据调节以及边界态与体态可区分的输运测量。  
8. **从光学响应到量子几何反演**：一个直接的应用方向是利用论文的光学求和法则，从实验测得的各阶光学电导反演动量分辨或时间分辨的量子几何张量，再与 Floquet 能谱、边缘态和泵浦电流联合验证。  
9. **与 inversion 课题的联系**：该论文主要讨论 Floquet 系统的 Berry 曲率和量子度规，而课题“general-quantum-geometry-inversion”关注从响应量反演几何量。因此，可进一步研究在高阶 Floquet 边带、混合 Berry 分量和非理想占据存在时，反问题是否仍具有唯一性，以及需要哪些正则化或额外约束。

来源：[arXiv:2608.01096，Conclusion 与附录](https://arxiv.org/abs/2608.01096)

---

## Round-9 新增文献条目（2026-08-13）

### [21] Khurelbaatar et al. 2026 — arXiv:2605.21925

- **阅读日期**：2026-08-13
- **文献标题**：Nonclassical Cutoff Fluctuations in Squeezed-Light-Driven High-Harmonic Generation
- **来源**：arXiv:2605.21925（2026-05-21 提交，Griffith U. / U. Southern Queensland）
- **核心结论**：在原子体系中证明 BSV 截止方差满足 $\Delta H^2(r)/\Delta H^2_{\text{SQL}} = e^{-2r}$（幅度压缩）的自校准关系，证明 BSV 量子光场可通过 Wigner 相空间方法被严格表征，并揭示截止方差具有 sub-SQL 的 Heisenberg 见证。
- **与课题关联**：作为 R1 量子态层级对比的辅助验证指标——BSV 量子态本身携带可发表的非经典性信息，独立于产额增强；为 R1 失败模式下"BSV-HHG 量子态描述层级选择"方法学论文提供独立的方法学支撑。
- **已引用位置**：申请书 §2.2 R1 节末段（"新文献支撑（与项目 R1 直接相关）"段）、方法学手册 §2A.3 节。

### [22] Rivera-Dean et al. 2026 — arXiv:2606.22714

- **阅读日期**：2026-08-13
- **文献标题**：Emergence of Gaussian entanglement and non-Gaussianity in high-harmonic generation driven by bright squeezed light
- **来源**：arXiv:2606.22714（2026-06-21 提交，UCL / MPSD / GTIIT / Technion / EIT 宁波 / ICFO / TU Wien）
- **核心结论**：在双色场（$\omega$ 相干场 + $2\omega$ BSV 扰动）构型下证明偶次谐波态可承载多模高斯纠缠。双模压缩参数达到阈值（$r \gtrsim 15$）时高斯性被破坏。
- **与课题关联**：高斯/非高斯边界正是 R1 三层描述对比的物理根源——条件单模态对应高斯保持，$P(n)$ 加权近似在阈值附近失效。该结论为 R1 §2.2 "近似层级的有效性边界"提供量化边界。
- **已引用位置**：申请书 §2.2 R1 节中段。

### [23] Yang 2025 — arXiv:2512.24553

- **阅读日期**：2026-08-13
- **文献标题**：From Berry curvature to quantum metric: a new era of quantum geometry metrology for Bloch electrons in solids
- **来源**：arXiv:2512.24553（2025-12 提交，综述）
- **核心结论**：综述通过自旋/偏振分辨 ARPES 在真实晶体中直接测量量子几何张量（Berry 曲率 + 量子度规）的最新进展，给出独立于 HHG 路径的实验精度基线（实部 ~0.1 rad、虚部 ~0.05 rad 级别）。
- **与课题关联**：作为 R2 反演结果的交叉验证基准，明确 R2 在 ARPES 路径之外的"全光学直接反演"差异化定位。Yang 给出的精度基线（~0.1 rad 量级）是 R2 SNR_{Ω/g} > 3 阈值的物理根据。
- **已引用位置**：申请书 §2.3 R2 节末段。

### [24] Sumaya-Martinez & Mulia-Rodriguez 2025 — arXiv:2512.23538

- **阅读日期**：2026-08-13
- **文献标题**：Fisher Information as an Operational Metric for Structured Optical Beams
- **来源**：arXiv:2512.23538（2025-12-29 提交）
- **核心结论**：将 Fisher 信息定义为结构光场参数估计的可操作度量。
- **与课题关联**：为 R2 选择 Fisher 信息矩阵条件数 $\text{cond}(\mathcal{I}) < 10$ 作为主判据提供方法学依据（与本项目"局部节点/曲率决定计量性能"的论证思路同源）。
- **已引用位置**：申请书 §2.3 R2 节中段（可辨识性指标 (ii) 处）。

### [25] Loaiza et al. 2025 — arXiv:2405.13885 / Quantum 9, 1822 (2025)

- **阅读日期**：2026-08-13
- **文献标题**：Nonlinear Spectroscopy via Generalized Quantum Phase Estimation
- **来源**：arXiv:2405.13885 / DOI: 10.22331/q-2025-08-07-1822（Xanadu Toronto）
- **核心结论**：提出广义量子相位估计（GQPE）框架用于多变量相位估计，可在量子计算机上以随响应阶数线性增长的电路成本计算任意阶非线性响应。
- **与课题关联**：为 R4 在 NN 框架外提供独立的方法学参照——当未来 NISQ 硬件成熟时，GQPE 可作为 R4 PINN 路径的对照基线，二者交叉验证可辨识性边界的可信度。
- **已引用位置**：申请书 §2.5 R4 节末段。

### [28] Raissi, Perdikaris & Karniadakis 2019 — J. Comput. Phys. 378, 686-707

- **阅读日期**：2026-08-13
- **文献标题**：Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations
- **来源**：DOI: 10.1016/j.jcp.2018.10.045（preprint arXiv:1711.10561 + 1711.10566）
- **核心结论**：PINN 框架的奠基性论文，将物理方程（一般是 PDE）作为软约束嵌入神经网络损失函数，实现前向求解与反演的统一框架。
- **与课题关联**：R4 PINN 反演框架的方法学根基。申请书 §2.5/§3.4 引用，方法学手册 §2D 顶部明示。三项物理约束（Hubbard-$U$ + 对称性 + 自能正则化）的联合嵌入是该框架在 HHG 几何量反演任务中的特定应用。
- **已引用位置**：申请书 §2.5 R4 节首段、方法学手册 §2D 顶部提示块。

### [29] Wilkinson et al. 2016 — Sci. Data 3, 160018

- **阅读日期**：2026-08-13
- **文献标题**：The FAIR Guiding Principles for scientific data management and stewardship
- **来源**：DOI: 10.1038/sdata.2016.18
- **核心结论**：FAIR 数据原则的原始奠基文献（Findable / Accessible / Interoperable / Reusable），已成为全球数据管理与共享的标准框架。
- **与课题关联**：HMG-Schema-1.0 数据格式的方法学声明依据——Findable（Zenodo DOI）/ Accessible（HTTPS）/ Interoperable（HDF5 + JSON Schema）/ Reusable（完整元数据）。该格式不申请专利，与 ICFO 联合推广通过 Zenodo + GitHub 开源发布。
- **已引用位置**：申请书 §2.4 R3 任务 3 节末段、方法学手册 §2C.4 FAIR 符合性声明段。
