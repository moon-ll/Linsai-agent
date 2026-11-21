---
title: "高次谐波自旋流作为交变磁自旋群对称性的动力学探针"
type: "papers"
created: "2026-08-21T04:50:14Z"
updated: "2026-11-15T15:09:25Z"
tags: ["高次谐波", "自旋流", "交变磁", "自旋群对称性", "HHG光谱学", "动力学选择定则"]
related: ["2606.31573", "CrSb", "arpes", "quantum metric", "交变磁态(altermagnet)", "固体HHG", "强场超快", "强场超快光学", "电荷流谐波vs自旋流谐波", "相干声子", "自旋劈裂", "自旋点群(SPG)", "自旋电子学动力学探测", "量子几何", "高次谐波选择定则"]
source_raw: "2026-2606.31573-high-harmonic-spin-current-signatures-of-altermagn.md"
growth_stage: "growing"
confidence: 0.7
auto_grown: true
review_status: "pending"
has_fulltext: true
updated_at: "2026-09-25T15:43:49Z"
merged_from: ["wiki/papers/2606.31573.md"]
---

# 高次谐波自旋流作为交变磁自旋群对称性的动力学探针

**论文**：Mizuno, arXiv:2606.31573 (2026)

## 林赛的理解

读到这篇的时候我第一反应是：终于有人在动力学端把自旋点群（SPG）这一套对称性语言接到了 HHG 上面。静态的 altermagnet 表征已经被 spin-resolved ARPES、磁二色性这些手段轮番做过了，但**动力学可观测量的对称性指纹**一直是缺位。Mizuno 这篇文章做的事情在我看来是"把对称性分析从静态搬到飞秒-阿秒尺度"，核心思路非常对我的胃口——利用 HHG 本身就是高对称性敏感的极端非线性过程。

我读完后的整体判断是：这是一篇**理论纲领性**的工作。它给出了在 HHG 中区分 FM、AFM、altermagnet 三相，以及把它们与磁性点群（magnetic point group）"伪装体"区分开的**完整选择定则表**。但我需要警觉的是：从"对称性允许/禁戒"到"实验室真的能拿出 spin-resolved 谐波信号"，中间还有不小的鸿沟。这一点在实验可操作性上要好好审视。

## 核心要点

### 1. 问题动机
- 自旋点群（spin point group, SPG）在弱自旋轨道耦合（SOC）极限下刻画磁相，特别是 altermagnetic 相的静态对称性，但其**动力学后果**几乎未被探索。
- 关键空白：能否用超快光学手段（尤其是 HHG）在飞秒时间尺度上探测 SPG 对称性？

### 2. 方法亮点
- 把**动力学对称性（dynamical symmetry）**概念扩展到包含 SPG 操作，推导出电荷流谐波与**自旋流谐波**的选择定则。
- 核心差异：**自旋流同时在实空间和自旋空间变换**，而电荷流只在实空间变换——这一点让自旋流谐波携带电荷流谐波不可触及的磁信息。
- 在一个**最小 altermagnetic 模型**（minimal model）上系统考察三种驱动极化下的谐波响应。

### 3. 关键结果
| 驱动方式 | 区分能力 |
|---------|---------|
| 轴对齐线偏振 | FM 与 altermagnet **不可区分**；AFM 因自旋流谐波消失可被识别 |
| 对角线偏振 | **可同时区分** FM / AFM / altermagnet 三相 |
| 单手性圆偏振 | 对区分三者与磁性点群"模仿者"提供**更锐利的自旋流谐波判据** |

### 4. 结论性论断
- 自旋流谐波（spin current harmonics）作为 SPG 对称性的**动力学探针**被正式建立。

## 实验/研究关联

### 与我课题的直接接续点
1. **HHG 光谱学的对称性诊断**——我组目前在 ab-initio 框架下做固体 HHG 的对称性分析，Mizuno 的 SPG-dynamical symmetry 框架可以**直接接入**我们的选择定则推导，特别是 altermagnet 这类 d-wave / g-wave 自旋劈裂体系。
2. **电荷流谐波 vs 自旋流谐波的实验对应**——理论上自旋流谐波携带额外信息，但实验上**如何分离"自旋分辨的谐波"**是一个悬而未决的问题。可走的路径：
   - 圆偏振驱动的 helicity-dependent HHG（已部分成熟）
   - 谐波与自旋极化探测结合（spin-resolved photoelectron spectroscopy of harmonics，或时间分辨 spin-polarized STM，但都极具挑战）
3. **"磁性点群模仿者"问题**——这一点很有意思。Mizuno 强调某些磁性点群（magnetic point group）在电荷流谐波层面**模仿** altermagnet 行为，但自旋流谐波可以把它们劈开。这直接关系到我们解释实验数据时的**结构指认鲁棒性**——只看 HHG 强度谱可能被误导。

### 可借鉴的技术工具
- SPG 操作下的张量变换分类（不可约表示分解）
- 对驱动极化方向的系统扫描（轴对齐 vs 对角 vs 圆）作为"对称性探针序列"

## 开放问题

1. **实验可观测性**：自旋流谐波在固体 HHG 中的**信噪比与探测方案**如何？目前没有任何实验组（据我所知）真正测到 spin-resolved HHG 信号。这是最关键的瓶颈。
2. **多能带与轨道分辨**：Mizuno 用的是 minimal model。真实 altermagnet（如 MnTe, RuO₂）的多带结构、SOC 修正、晶体对称性破缺会不会**软化**这些干净的选择定则？
3. **非平衡态延拓**：SPG 是平衡态概念。超快激发本身可能瞬时打破 SPG，导致谐波指纹的**时间演化**——能否作为相干声子 / 自旋动力学的新探针？
4. **与量子几何量的联系**：我组关注的 quantum metric / Berry curvature 在 HHG 中的角色，与 SPG 自旋流谐波是否有**深层对应**？例如，altermagnet 的 d-wave 自旋劈裂是否对应某种 spin-Berry curvature 的谐波指纹？
5. **SOC 弱极限假设的适用边界**：文章在 weak-SOC 框架下成立。如果 SOC 强到足以显著耦合自旋与晶格，SPG 与传统磁性点群趋同，方法是否还有优势？
6. **该理论是否给出可量化的谐波强度比**（比如某种 helicity ratio / anisotropy ratio 作为序参量），而不只是"有没有"这种二元判据？这对实验数据处理至关重要。

## 来源
- 原始材料：2026-2606.31573-high-harmonic-spin-current-signatures-of-altermagn.md
- 蒸馏时间：2026-08-21T04:50:14Z


## 合并自「2606.31573」

# High-harmonic spin-current signatures of altermagnetic spin-group symmetry

**arXiv**: [2606.31573](https://arxiv.org/abs/2606.31573) | **方向**: HHG光谱学

---

## 研究问题（Research Question）

This paper fills a critical theoretical gap: spin point groups (SPGs) are well established for classifying equilibrium magnetic phases in the weak-SOC regime, but their dynamical consequences for nonlinear optical responses were completely unexplored. The author extends the dynamical-symmetry selection-rule framework—previously applied only to charge-current HHG under ordinary crystallographic or magnetic point groups—to include independent spin-space rotations, thereby deriving selection rules for both charge and spin current HHG in altermagnets. The key conceptual advance is that spin currents transform as D_v(g_r) ⊗ D_s(g_s) (a vector in both real and spin space), whereas charge currents transform only as D_v(g_r) (a scalar under spin rotations); this asymmetry means spin current HHG can reveal magnetic symmetry information invisible to charge current HHG. The paper provides concrete, experimentally testable criteria—especially a circularly-polarized-drive scheme—that distinguish ferromagnetic, antiferromagnetic, and altermagnetic phases, and cleanly separates nonrelativistic altermagnetic spin splitting from relativistic SOC-induced splitting. This establishes spin current HHG as a new symmetry-resolved nonlinear probe of weak-SOC magnets.

## 研究背景（Background）

This paper is directly relevant to Lin Sai's core interest in using HHG spectroscopy to probe symmetry breaking and phase transitions in solids. The key insight—that spin current HHG accesses magnetic symmetry information invisible to charge current HHG—extends the symmetry-resolved HHG spectroscopy paradigm that Lin Sai already employs in ZnO and TMD systems. The selection-rule framework is wavelength-independent (it is purely symmetry-based), so the conclusions hold equally at 800 nm as at mid-IR; this is important given Lin Sai's disrupted mid-IR supply chain. At 800 nm Ti:Sapphire driving wavelength, the modulo-four spin-current harmonic shift under circular polarization could in principle be tested in altermagnet heterostructures (e.g., RuO2/Pt for inverse spin Hall readout), although the harmonic orders would be lower than in mid-IR-driven experiments and the interband contribution may dominate. The diagonal-LPL criterion (spin current routed to transverse vs longitudinal channel depending on magnetic phase) is particularly accessible—it requires only linear polarization rotated to [110], which is trivial at 800 nm. The paper's approach of deriving experimentally verifiable selection rules from first-principles symmetry arguments mirrors the methodology Lin Sai uses for ZnO (where crystal orientation-dependent HHG selection rules have been exploited), and the extension to spin currents opens a route to probe magnetic order dynamics on the femtosecond timescale. A natural next step for Lin Sai would be to combine this spin-current HHG framework with existing TMD or ZnO heterostructure expertise to design an 800-nm-driven circular-polarization experiment targeting the altermagnetic phase fingerprint, or to adapt the selection-rule methodology to probe magnetic phase transitions in materials with controllable magnetic order.

## 研究方法（Methods）

- Extension of dynamical-symmetry selection-rule theory to spin point groups: the formalism G_τ O(t) G_τ^{-1} = D(g) O(t+τ) is generalized so that g = [g_s∥g_r] acts on observables through their full spin-and-space representation. This is the first systematic derivation of HHG selection rules where spin-space and real-space operations are treated independently, appropriate for the weak-SOC regime.
- A minimal two-sublattice D4h tight-binding model that captures all three magnetic phases (type-I ferromagnet, type-II antiferromagnet, type-III d-wave altermagnet) within a unified Hamiltonian framework H_I, H_II, H_III, enabling direct numerical verification of the symmetry-derived selection rules via real-time density-matrix propagation (phenomenological EoM with T2 relaxation, 501×501 k-mesh, 4th-order Runge-Kutta integrator).
- A symmetry-based protocol for experimentally distinguishing weak-SOC magnetic phases using polarization control: (1) LPL_x as null test, (2) LPL_[110] for SPG-sensitive spin-current channel routing (longitudinal vs transverse), and (3) single-helicity CPL for unambiguous modulo-four spin-current harmonic fingerprinting that cannot be mimicked by SOC systems.
- Explicit comparison of SPG-derived selection rules against magnetic-point-group (MPG) selection rules (Tables II–V), demonstrating that only the fixed-helicity CPL geometry yields a spin-current signature unique to SPG symmetry—LPL selection rules are partially reproduced by MPG, but CPL selection rules from [C2∥C_n] cannot be reproduced by any MPG operation under the same drive.

## 主要发现与核心结论（Main Results）

- Charge current selection rules depend only on real-space operations g_r and are therefore identical for type-I (ferromagnetic [E∥D4h]) and type-III (altermagnetic [E∥D2h]+[C2x∥(D4h−D2h)]) phases, because the charge current is a scalar under spin transformations D_Je([g_s∥g_r]) = D_v(g_r). Spin current selection rules depend on both real and spin space D_Js([g_s∥g_r]) = D_v(g_r) ⊗ D_s(g_s), so they differ between type-I and type-III magnets—the operations [E∥g_r] and [C2x∥g_r] impose conflicting constraints on spin currents but identical constraints on charge currents.
- Under axis-aligned linear polarization (LPL_x), the dynamical symmetries ([E∥C2y];T/2) and ([E∥C2x];0) are shared by all three magnetic phases, so LPL_x is completely non-diagnostic: it gives identical odd-order longitudinal charge and z-polarized spin current harmonics for type-I and type-III, and cannot distinguish them.
- Under diagonal linear polarization LPL_[110], the type-III altermagnet is distinguished: the odd-order z-polarized spin-current harmonic appears in the transverse channel J^(2m+1)_{s,z,⊥} for type-III, whereas it appears in the longitudinal channel J^(2m+1)_{s,z,∥} for type-I. However, this LPL criterion is ambiguous because certain magnetic point groups can mimic the same selection rule, so LPL alone cannot unambiguously attribute the signal to SPG origin versus SOC origin.
- Single-helicity circularly polarized light (CPL) provides the sharpest criterion: the fourfold dynamical symmetry gives modulo-four selection rules. Type-I allows J^(4m±1)_{s,z,±}, whereas type-III allows J^(4m∓1)_{s,z,±}—a clean modulo-four shift of allowed spin-current harmonics. Type-II forbids all z-polarized spin current harmonics. Crucially, the antiunitary magnetic point group operation C4zT (the SOC analogue) flips the helicity of CPL and therefore is NOT a dynamical symmetry of the same single-helicity drive, making CPL a unique probe that separates nonrelativistic altermagnetic splitting from relativistic SOC-induced splitting.
- The type-II (antiferromagnetic) phase is distinguished from both type-I and type-III by the total absence of z-polarized spin current harmonics at ALL orders, under any drive geometry, because its SPG contains both [E∥g_r] and [C2x∥g_r] for all g_r, which impose incompatible constraints on the spin current.

## 潜在研究方向（Future Directions）

- Extend the framework from the minimal D4h d-wave altermagnet model to realistic candidate materials (e.g., RuO2, CrSb, MnTe) with ab initio band structures, to verify that the SPG selection rules survive beyond the tight-binding approximation and to identify materials where the spin-current HHG signal is strongest.
- Develop a quantitative detector-level theory for spin-to-charge conversion at the altermagnet/strong-SOC-metal interface (e.g., Pt inverse spin Hall effect), including the conversion tensor Λ and interface symmetry, to predict which spin-current harmonic channels survive conversion and are measurable in practice—the paper explicitly leaves this as future work.
- Explore other altermagnetic wave symmetries (g-wave, i-wave, p-wave) beyond d-wave, which will have different SPG structures [C2∥g_r] with different coset decompositions G−H, potentially yielding different modulo-n selection rules under n-fold CPL drives and expanding the palette of symmetry-resolved probes.
- Investigate the effect of finite SOC and canted magnetic moments on the sharpness of the SPG selection rules: in real materials with non-negligible SOC, the clean separation between SPG and MPG descriptions will break down, and understanding the crossover regime is essential for experimental interpretation.
- Propose concrete experimental geometries at accessible wavelengths (800 nm Ti:Sapphire or mid-IR OPA) on altermagnet thin films or heterostructures, with circular polarization and spin-current detection via inverse spin Hall voltage, to test the modulo-four spin-current harmonic shift predicted for the type-III phase.



## 深度解析

### 研究问题（Research Question）

This paper fills a critical theoretical gap: spin point groups (SPGs) are well established for classifying equilibrium magnetic phases in the weak-SOC regime, but their dynamical consequences for nonlinear optical responses were completely unexplored. The author extends the dynamical-symmetry selection-rule framework—previously applied only to charge-current HHG under ordinary crystallographic or magnetic point groups—to include independent spin-space rotations, thereby deriving selection rules for both charge and spin current HHG in altermagnets. The key conceptual advance is that spin currents transform as D_v(g_r) ⊗ D_s(g_s) (a vector in both real and spin space), whereas charge currents transform only as D_v(g_r) (a scalar under spin rotations); this asymmetry means spin current HHG can reveal magnetic symmetry information invisible to charge current HHG. The paper provides concrete, experimentally testable criteria—especially a circularly-polarized-drive scheme—that distinguish ferromagnetic, antiferromagnetic, and altermagnetic phases, and cleanly separates nonrelativistic altermagnetic spin splitting from relativistic SOC-induced splitting. This establishes spin current HHG as a new symmetry-resolved nonlinear probe of weak-SOC magnets.

### 研究背景（Background）

This paper is directly relevant to Lin Sai's core interest in using HHG spectroscopy to probe symmetry breaking and phase transitions in solids. The key insight—that spin current HHG accesses magnetic symmetry information invisible to charge current HHG—extends the symmetry-resolved HHG spectroscopy paradigm that Lin Sai already employs in ZnO and TMD systems. The selection-rule framework is wavelength-independent (it is purely symmetry-based), so the conclusions hold equally at 800 nm as at mid-IR; this is important given Lin Sai's disrupted mid-IR supply chain. At 800 nm Ti:Sapphire driving wavelength, the modulo-four spin-current harmonic shift under circular polarization could in principle be tested in altermagnet heterostructures (e.g., RuO2/Pt for inverse spin Hall readout), although the harmonic orders would be lower than in mid-IR-driven experiments and the interband contribution may dominate. The diagonal-LPL criterion (spin current routed to transverse vs longitudinal channel depending on magnetic phase) is particularly accessible—it requires only linear polarization rotated to [110], which is trivial at 800 nm. The paper's approach of deriving experimentally verifiable selection rules from first-principles symmetry arguments mirrors the methodology Lin Sai uses for ZnO (where crystal orientation-dependent HHG selection rules have been exploited), and the extension to spin currents opens a route to probe magnetic order dynamics on the femtosecond timescale. A natural next step for Lin Sai would be to combine this spin-current HHG framework with existing TMD or ZnO heterostructure expertise to design an 800-nm-driven circular-polarization experiment targeting the altermagnetic phase fingerprint, or to adapt the selection-rule methodology to probe magnetic phase transitions in materials with controllable magnetic order.

### 研究方法（Methods）

- Extension of dynamical-symmetry selection-rule theory to spin point groups: the formalism G_τ O(t) G_τ^{-1} = D(g) O(t+τ) is generalized so that g = [g_s∥g_r] acts on observables through their full spin-and-space representation. This is the first systematic derivation of HHG selection rules where spin-space and real-space operations are treated independently, appropriate for the weak-SOC regime.
- A minimal two-sublattice D4h tight-binding model that captures all three magnetic phases (type-I ferromagnet, type-II antiferromagnet, type-III d-wave altermagnet) within a unified Hamiltonian framework H_I, H_II, H_III, enabling direct numerical verification of the symmetry-derived selection rules via real-time density-matrix propagation (phenomenological EoM with T2 relaxation, 501×501 k-mesh, 4th-order Runge-Kutta integrator).
- A symmetry-based protocol for experimentally distinguishing weak-SOC magnetic phases using polarization control: (1) LPL_x as null test, (2) LPL_[110] for SPG-sensitive spin-current channel routing (longitudinal vs transverse), and (3) single-helicity CPL for unambiguous modulo-four spin-current harmonic fingerprinting that cannot be mimicked by SOC systems.
- Explicit comparison of SPG-derived selection rules against magnetic-point-group (MPG) selection rules (Tables II–V), demonstrating that only the fixed-helicity CPL geometry yields a spin-current signature unique to SPG symmetry—LPL selection rules are partially reproduced by MPG, but CPL selection rules from [C2∥C_n] cannot be reproduced by any MPG operation under the same drive.

### 主要发现与核心结论（Main Results）

- Charge current selection rules depend only on real-space operations g_r and are therefore identical for type-I (ferromagnetic [E∥D4h]) and type-III (altermagnetic [E∥D2h]+[C2x∥(D4h−D2h)]) phases, because the charge current is a scalar under spin transformations D_Je([g_s∥g_r]) = D_v(g_r). Spin current selection rules depend on both real and spin space D_Js([g_s∥g_r]) = D_v(g_r) ⊗ D_s(g_s), so they differ between type-I and type-III magnets—the operations [E∥g_r] and [C2x∥g_r] impose conflicting constraints on spin currents but identical constraints on charge currents.
- Under axis-aligned linear polarization (LPL_x), the dynamical symmetries ([E∥C2y];T/2) and ([E∥C2x];0) are shared by all three magnetic phases, so LPL_x is completely non-diagnostic: it gives identical odd-order longitudinal charge and z-polarized spin current harmonics for type-I and type-III, and cannot distinguish them.
- Under diagonal linear polarization LPL_[110], the type-III altermagnet is distinguished: the odd-order z-polarized spin-current harmonic appears in the transverse channel J^(2m+1)_{s,z,⊥} for type-III, whereas it appears in the longitudinal channel J^(2m+1)_{s,z,∥} for type-I. However, this LPL criterion is ambiguous because certain magnetic point groups can mimic the same selection rule, so LPL alone cannot unambiguously attribute the signal to SPG origin versus SOC origin.
- Single-helicity circularly polarized light (CPL) provides the sharpest criterion: the fourfold dynamical symmetry gives modulo-four selection rules. Type-I allows J^(4m±1)_{s,z,±}, whereas type-III allows J^(4m∓1)_{s,z,±}—a clean modulo-four shift of allowed spin-current harmonics. Type-II forbids all z-polarized spin current harmonics. Crucially, the antiunitary magnetic point group operation C4zT (the SOC analogue) flips the helicity of CPL and therefore is NOT a dynamical symmetry of the same single-helicity drive, making CPL a unique probe that separates nonrelativistic altermagnetic splitting from relativistic SOC-induced splitting.
- The type-II (antiferromagnetic) phase is distinguished from both type-I and type-III by the total absence of z-polarized spin current harmonics at ALL orders, under any drive geometry, because its SPG contains both [E∥g_r] and [C2x∥g_r] for all g_r, which impose incompatible constraints on the spin current.

### 潜在研究方向（Future Directions）

- Extend the framework from the minimal D4h d-wave altermagnet model to realistic candidate materials (e.g., RuO2, CrSb, MnTe) with ab initio band structures, to verify that the SPG selection rules survive beyond the tight-binding approximation and to identify materials where the spin-current HHG signal is strongest.
- Develop a quantitative detector-level theory for spin-to-charge conversion at the altermagnet/strong-SOC-metal interface (e.g., Pt inverse spin Hall effect), including the conversion tensor Λ and interface symmetry, to predict which spin-current harmonic channels survive conversion and are measurable in practice—the paper explicitly leaves this as future work.
- Explore other altermagnetic wave symmetries (g-wave, i-wave, p-wave) beyond d-wave, which will have different SPG structures [C2∥g_r] with different coset decompositions G−H, potentially yielding different modulo-n selection rules under n-fold CPL drives and expanding the palette of symmetry-resolved probes.
- Investigate the effect of finite SOC and canted magnetic moments on the sharpness of the SPG selection rules: in real materials with non-negligible SOC, the clean separation between SPG and MPG descriptions will break down, and understanding the crossover regime is essential for experimental interpretation.
- Propose concrete experimental geometries at accessible wavelengths (800 nm Ti:Sapphire or mid-IR OPA) on altermagnet thin films or heterostructures, with circular polarization and spin-current detection via inverse spin Hall voltage, to test the modulo-four spin-current harmonic shift predicted for the type-III phase.

### 来源

- [arXiv 2606.31573](https://arxiv.org/abs/2606.31573)
- 导入自 hermes 深度分析（2026-08-08T16:23:45Z）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：自旋点群动力学对称性选择定则：自旋流谐波作为交变磁相的对称性分辨探针

**原理**：把动力学对称性选择定则框架推广到自旋点群（SPG）：可观测量按完整自旋-空间表示变换 g=[g_s∥g_r]，自旋流按 D_v(g_r)⊗D_s(g_s) 变换（电荷流仅 D_v(g_r)、自旋旋转下为标量）——自旋流谐波携带电荷流谐波不可及的磁对称信息；在最小两子格 D4h 紧束缚模型（H_I 铁磁/H_II 反铁磁/H_III d 波交变磁统一框架）上以实时密度矩阵传播（501×501 k 网格、RK4、T2 弛豫）数值验证；给出三极化判据序列：LPL_x 为 null 检验（三相不可区分）、LPL_[110] 使 d 波交变磁的自旋流谐波路由到横向通道（但可被磁性点群模仿）、单螺旋 CPL 给出 modulo-4 自旋流谐波指纹（type-I 允许 J^(4m±1)、type-III 允许 J^(4m∓1)、type-II 全禁戒），且 C4zT 反单元操作因翻转 CPL 螺旋度不是同螺旋度驱动的动力学对称——CPL 判据把非相对论交变磁劈裂与相对论 SOC 劈裂干净分开。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 数值模型 | 最小两子格 D4h 紧束缚（捕获全部三相）；实时密度矩阵传播 + T2 弛豫；501×501 k 网格；四阶 Runge-Kutta | 研究方法 |
| 三极化判据 | LPL_x：完全非诊断（三相相同奇阶纵充电荷/自旋流谐波）；LPL_[110]：type-III 的 z 偏振自旋流谐波出现在横向通道 J^(2m+1)_{s,z,⊥}（type-I 纵向）——但可被某些磁性点群模仿；单螺旋 CPL：modulo-4 指纹 J^(4m±1)_{s,z,±}（type-I）vs J^(4m∓1)_{s,z,±}（type-III），type-II 全阶全几何禁戒 | 主要发现 |
| SPG vs MPG | 仅固定螺旋度 CPL 几何给出 SPG 独有签名（[C2∥C_n] 的 CPL 选择定则无法被任何 MPG 操作在同一驱动下复现）；LPL 选择定则可被 MPG 部分复现 | 主要发现 |

**适用边界**：weak-SOC 极限（SOC 强时 SPG 与磁性点群趋同、方法优势消失）；minimal D4h d 波模型（真实 RuO2/CrSb/MnTe 多带/SOC 修正/晶体破缺未验证）；自旋流谐波的探测方案未建立（需 altermagnet/强 SOC 金属界面的自旋-电荷转换张量理论，作者明示留作后续）；二元判据（无量化谐波强度比）；超快激发对 SPG 的瞬态破坏未探讨。
**代表作**：自旋流 HHG 对称性探针理论（Mizuno，本文）；选择定则波长无关（800 nm 与中红外同样成立），可在 RuO2/Pt 反自旋霍尔几何检验 modulo-4 位移。
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[2606.31573]]
- [[CrSb]]
- [[arpes]]
- [[quantum metric]]
- [[交变磁态(altermagnet)]]
- [[固体HHG]]
- [[强场超快]]
- [[强场超快光学]]
- [[电荷流谐波vs自旋流谐波]]
- [[相干声子]]
- [[自旋劈裂]]
- [[自旋点群(SPG)]]
- [[自旋电子学动力学探测]]
- [[量子几何]]
- [[高次谐波选择定则]]
<!-- /linsai-wikilinks -->
