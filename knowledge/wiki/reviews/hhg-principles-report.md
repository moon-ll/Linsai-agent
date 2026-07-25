---
title: "HHG 光谱学原理与理论模型"
type: "review"
created: "2026-05-19T00:00:00Z"
updated: "2026-06-23T02:42:19Z"
tags: ["HHG", "综述", "理论", "#type/report", "#topic/HHG", "#status/mature"]
related: ["Corkum", "Lewenstein模型", "RABBITT", "三步模型", "截止定律", "相位匹配", "高次谐波产生"]
source_raw: ""
growth_stage: "mature"
confidence: 0.9
---

# HHG 光谱学原理与理论模型

**调研范围**：2010–2026 年高次谐波光谱学核心文献

**最后更新**：2026-06-17 UTC


---

## 1. 三步模型与截止定律

### 1.1 原子 HHG 的经典三步模型

高次谐波产生（HHG）的核心物理图像由 Corkum（1993）提出，包含三个阶段：

1. **隧穿电离**（Tunneling ionization）：强激光场压低原子势垒，电子隧穿出势垒。

2. **激光场中传播**（Propagation）：电子在激光场中加速，获得动能。

3. **复合与辐射**（Recombination）：电子返回母离子，部分动能以高能光子形式辐射。

![三步模型示意](placeholder：三步模型图）

### 1.2 截止定律（Cutoff Law）

单原子截止能量：

$$E_{\text{cutoff}} \approx 3.17\,U_p + I_p$$

其中 $U_p = e^2E_0^2/(4m\omega^2) \propto I\lambda^2$ 是ponderomotive能，$I_p$ 是电离势。

**关键意义**：截止能量随驱动光波长 $\lambda$ 的平方增长 → 长波长驱动产生更高能量谐波。

---

## 2. 量子力学理论框架

### 2.1 Lewenstein 模型（SFA）

基于强场近似（SFA）的半解析理论，将 HHG 谱分解为：

$$S(\omega) = W(E)\,\frac{d\sigma(\omega)}{d\Omega}$$

其中 $W(E)$ 是返回电子波包，$d\sigma/d\Omega$ 是光电复合截面。

该分解是分子轨道断层成像（Itatani et al.）的理论基础。

### 2.2 固体 HHG 的特殊性

固体中电子有效质量 $m^*$ 替换电子质量，带隙 $E_g$ 替换 $I_p$：

$$E_{\text{cutoff}} \approx E_g + 2U_p$$

固体 HHG 机制包含 intra-band（带内布洛赫振荡）和 inter-band（带间隧穿）两种贡献。

---

## 3. 各年代表性理论进展


### 2021 年


### Introduction to theory of high-harmonic generation in solids: tutorial（2021）
- **作者**：Lun Yue Mette B. Gaarde
- **引用**：98 次 | **标签**：spectroscopy, theory, solids, tutorial, review
- **摘要**：High-harmonic generation (HHG) in solids has emerged in recent years as a rapidly expanding and interdisciplinary field, attracting attention from both the condensed-matter and the atomic, molecular, and optics communities. It has exciting prospects for the engineering of new light sources and the p


### 2019 年


### On the Quantum-Optical Nature of High Harmonic Generation（2019）
- **作者**：Alexey Gorlach Ofer Neufeld Nicholas Rivera Oren Cohen Ido Kaminer
- **引用**：137 次 | **标签**：theory, quantum-optics, HHG
- **摘要**：High harmonic generation (HHG) is an extremely nonlinear effect, where a medium is driven by a strong laser field, generating coherent broadband radiation with photon energies ranging up to the X-ray and pulse durations reaching attosecond timescales. Conventional models of HHG treat the medium quan


### 2018 年


### Symphony on Strong Field Approximation（2018）
- **作者**：K. Amini J. Biegert F. Calegari A. Chacón M. Ciappina A. Dauphin D. Efimov C. Figueira de Morisson Faria Krzysztof Giergiel Piotr Gniewek A. Landsman M. Lesiuk M. Mandrysz A. Maxwell R. Moszynski L. Ortmann José Antonio Pérez-Hernández A. Picón E. Pisanty J. Prauzner-Bechcicki K. Sacha N. Suárez A. Zaïr J. Zakrzewski M. Lewenstein
- **引用**：183 次 | **标签**：theory, SFA, strong-field-approximation
- **摘要**：This paper has been prepared by the Symphony collaboration (University of Warsaw, Uniwersytet Jagiello\\'nski, DESY/CNR and ICFO) on the occasion of the 25th anniversary of the "simple man's models" which underlie most of the phenomena that occur when intense ultrashort laser pulses interact with ma

### Reciprocal-space-trajectory perspective on high harmonic generation in solids（2018）
- **作者**：Liang Li Pengfei Lan Xiaosong Zhu Tengfei Huang Qingbin Zhang Manfred Lein Peixiang Lu
- **引用**：80 次 | **标签**：theory, reciprocal-space, trajectory
- **摘要**：We revisit the mechanism of high harmonic generation (HHG) from solids by comparing HHG in laser fields with different ellipticities but constant maximum amplitude. It is shown that the cutoff of HHG is strongly extended in a circularly polarized field. Moreover, the harmonic yield with large ellipt


### 2011 年


### Time-resolved photoemission by attosecond streaking: extraction of time information（2011）
- **作者**：S. Nagele R. Pazourek J. Feist K. Doblhoff-Dier C. Lemell K. Tőkési J. Burgdörfer
- **引用**：136 次 | **标签**：theory, measurement, streaking, TDSE
- **摘要**：Attosecond streaking of atomic photoemission holds the promise to provide unprecedented information on the release time of the photoelectron. We show that attosecond streaking phase shifts indeed contain timing (or spectral phase) information associated with the Eisenbud-Wigner-Smith time delay matr


### 2010 年


### Probing single-photon ionization on the attosecond time scale（2010）
- **作者**：K. Klünder J. M. Dahlström M. Gisselbrecht T. Fordell M. Swoboda D. Guénot P. Johnsson J. Caillat J. Mauritsson A. Maquet R. Taïeb A. L’Huillier
- **引用**：461 次 | **标签**：theory, measurement, RABBITT, attosecond
- **摘要**：We study photoionization of argon atoms excited by attosecond pulses using an interferometric measurement technique. We measure the difference in time delays between electrons emitted from the 3s² and from the 3p⁶ shell, at different excitation energies ranging from 32 to 42 eV. The determination of

### Bright Coherent Ultrafast Soft X-Ray Harmonics Spanning the Water Window from a Tabletop Light Source（2010）
- **作者**：M.C. Chen P. Arpin T. Popmintchev M. Gerrity B. Zhang M. Seaberg M.M. Murnane H.C. Kapteyn
- **引用**：312 次 | **标签**：theory, water-window, phase-matching
- **摘要**：We demonstrate fully phase matched high-order harmonic generation with emission spanning the water window spectral region important for bio- and nano-imaging and a breadth of materials and molecular dynamics studies. We also generate the broadest bright coherent bandwidth (~300eV) to date obtained f


### 2007 年


### Improved Lewenstein model for high-order harmonic generation of atoms and molecules with scattering wavefunctions（2007）
- **作者**：Anh-Thu Le Toru Morishita C. D. Lin
- **引用**：1 次 | **标签**：theory, Lewenstein-model, SFA
- **摘要**：We demonstrate a simple method to improve the Lewenstein model for the description of high-order harmonic generation (HHG). It is shown that HHG spectra can be expressed as the product of a returning electron wave packet and the photo-recombination cross sections, where the former can be extracted f


### 1999 年


### Quantum theory of a high harmonic generation as a three-step process（1999）
- **作者**：M. Yu. Kuchiev V. N. Ostrovsky
- **引用**：40 次 | **标签**：theory, three-step, quantum-model
- **摘要**：Fully quantum treatment explicitly presents the high harmonic generation as a three-step process: (i) above threshold ionization (ATI) is followed by (ii) electron propagation in a laser-dressed continuum. Subsequently (iii) stimulated (or laser assisted) recombination brings the electron back into 


---

*本报告由 LinSai-CoPilot 基于 deepxiv 真实文献生成于 2026-06-17*

<!-- linsai-wikilinks -->
## 关联概念

- [[Corkum]]
- [[Lewenstein模型]]
- [[RABBITT]]
- [[三步模型]]
- [[截止定律]]
- [[相位匹配]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
