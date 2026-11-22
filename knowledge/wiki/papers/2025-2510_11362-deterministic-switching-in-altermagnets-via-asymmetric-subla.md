---
title: "2025-2510.11362-deterministic-switching-in-altermagnets-via-asymmetric-subla"
type: "papers"
created: "2026-11-01T08:01:48Z"
updated: "2026-11-15T15:09:23Z"
tags: []
related: ["2510.11362", "Berry 曲率", "FeSb2", "Landau-Lifshitz-Gilbert 模拟", "Neel 矢量", "altermagnet", "arpes", "交变磁体", "反铁磁体", "反铁磁自旋电子学", "奈尔序", "奈尔矢量", "强场超快", "强场超快光学", "微磁模拟", "自旋劈裂", "超快自旋动力学"]
source_raw: "2025-2510.11362-deterministic-switching-in-altermagnets-via-asymmetric-subla.md"
growth_stage: "seedling"
confidence: 0.5
digest_level: "abstract"
updated_at: "2026-11-08T01:02:42Z"
merged_from: ["wiki/papers/2510.11362.md"]
---

• 我先读 raw 原文和 literature-reading skill 文件。

• raw 只有摘要级信息（digest_hint=abstract），按四要素摘要级蒸馏，不虚构全文数值。以下为蒸馏产物：

  # Deterministic Switching in Altermagnets via Asymmetric Sublattice Spin Current

  ## 研究问题（Research Question）

  如何在不施加外磁场的条件下，实现[[交变磁体]]（[[altermagnet]]）奈尔矢量（[[奈尔矢量]]）的确定性翻转？传统[[反铁磁体]]翻转依赖交换偏置或超快激光等手段，论文针对交变磁体自旋排列的特殊对称性，提出一种仅用电流驱动的确定性翻转机制。

  ## 研究背景（Background）

  [[奈尔序]]的电控翻转是[[反铁磁自旋电子学]]的核心难题。交变磁体兼具铁磁样的能带劈裂与反铁磁样的净磁化消失特性，但其两个子晶格之间的磁化补偿关系使常规自旋流难以产生非对称扭矩，实现无外场确定性翻转缺乏可行的机制设计。

  ## 研究方法（Method）

  作者提出**非对称子晶格自旋流**（asymmetric sublattice spin current）驱动机制，利用[[Landau-Lifshitz-Gilbert 模拟|LLG 方程模拟]]在掺杂 [[FeSb2|FeSb₂]] 体系中进行[[微磁模拟]]验证，并将该机制推广至 g 波与 i 波对称性的交变磁体。

  ## 发现（Findings）

  - 非对称子晶格自旋流可在无外场条件下驱动 [[Neel 矢量]] 的 **180° 确定性翻转**，翻转时间约 **40 ps**。
  - 机制在掺杂 FeSb₂ 中经 LLG 模拟验证，并推广到 **g 波**与 **i 波**两类交变磁体，显示机制对磁对称性类别的普适性。
  - 为交变磁体的纯电控、快速、确定性写入提供了新的机制路径，与超快自旋动力学写入方案互补。

  （注：本条目按摘要级蒸馏，仅含摘要明示的数值——180° 翻转、约 40 ps；其余参数需全文精读补充。）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：非对称子晶格自旋流驱动交变磁体奈尔矢量确定性翻转（LLG 微磁模拟验证）

**原理**：提出非对称子晶格自旋流驱动机制：利用交变磁体子晶格间不对称的自旋输运产生非对称扭矩，在无外场条件下驱动奈尔矢量 180° 确定性翻转；在掺杂 FeSb₂ 体系经 Landau-Lifshitz-Gilbert（LLG）微磁模拟验证，并推广至 g 波与 i 波对称性交变磁体。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 奈尔矢量翻转 | 180° 确定性翻转，约 40 ps | 发现（Findings） |

**适用边界**：摘要级：仅含摘要明示数值，其余参数需全文精读补充；FeSb₂ 掺杂体系 LLG 模拟层面，实验路径未验；与超快自旋动力学写入方案互补。
**代表作**：Deterministic Switching in Altermagnets via Asymmetric Sublattice Spin Current, arXiv:2510.11362 (2025)
*方法卡回补 2026-11-01*


## 合并自「2510.11362」

## 阅读笔记

### general-new-idea-20260822

已获得完整正文。现在我有全部所需信息来撰写结构化笔记。

---

## 调研笔记：arXiv:2510.11362

**论文题目**：Deterministic Switching in Altermagnets via Asymmetric Sublattice Spin Current
**作者**：Sayan Sarkar, Sunit Das, Amit Agarwal（印度 IIT Kanpur 理论凝聚态组）
**arXiv ID**：2510.11362（v1, 2025-10-13）
**领域**：cond-mat.mes-hall / cond-mat.mtrl-sci### ## 研究问题（Research Question）

- 论文的核心问题是：**在 even-parity（d-wave / g-wave / i-wave）交变磁体（altermagnet，AM）中，如何实现无外磁场（field-free）的确定性 180° Néel 矢量翻转**——这是 altermagnet 自旋电子学存储器走向实用化的关键瓶颈。
- 具体而言：传统 Néel 自旋轨道力矩（NSOT）机制要求每个亚晶格破缺局部反演对称性，因此**在具有局部反演对称的 d-wave/g-wave/i-wave AM（如 RuO₂、KV₂Se₂O、掺杂 FeSb₂）中间会消失**；本文即提出一种**不依赖反演对称性破缺、不依赖强自旋轨道耦合**的通用翻转机制。
- 中心论点是：利用 d-wave altermagnet 的**方向依赖自旋劈裂 Fermi 面**自然产生"亚晶格非对称自旋电流"（Asymmetric Sublattice Spin Current, ASSC），这种电流在 HM/AM 异质结中注入后会形成**不平衡的场类力矩（field-like torque）和阻尼类力矩（damping-like torque）**，从而在数十皮秒内驱动 Néel 矢量翻转。

### ## 研究背景（Background）

-现有磁存储技术面临两难：铁磁体（FM）易检测但有杂散场、动态速度有限；常规反铁磁体（AFM）有 THz 动力学和抗杂散场优势，却缺乏便捷的电学读出通道；**交变磁体（AM）兼具两者优点**——补偿磁序（无杂散场、THz 动力学）+ 大非相对论自旋劈裂（可由反常霍尔信号电学读出）。
- 前人工作主要包括：(i) NSOT（Železný 2014/2017, Chen 2019, Bodnar 2018）——需要局部反演对称破缺；(ii) Néel 自旋电流（Shao 2023, Zhang 2025）——需特殊亚晶格几何或辅助磁场；(iii) 磁八极矩注入（Han 2025, Baek 2025）——实验上极难控制。
- d-wave AM 的标志性对称性是 spin group `[C²||C⁴_z|τ]`，由两重自旋旋转 + 四重实空间旋转 + 平移构成，在 Γ-S、R-Z方向存在强自旋劈裂；本文选用**掺杂 FeSb₂（Pnnm 空间群）**作为代表体系（未掺杂时为 Kondo 绝缘体，电子掺杂后变为金属 d-wave AM），也讨论了向 RuO₂[110]、KV₂Se₂O[100]、MnTe[11-20]、FeS₂[120] 的推广。
- **研究动机**：尽管 AM 自旋电子学应用前景广阔，但"deterministic 控制 AM 序"仍是公开难题，需要一种 field-free、适用于 even-parity 中心对称 AM 的通用翻转协议。

### ## 研究方法（Methods）

- **理论框架**：以 spin group 为基础的对称性论证 + 紧束缚能带计算 + 微观自旋输运 + Landau-Lifshitz-Gilbert (LLG) 动力学模拟四步走。
- **能带模型**：构建与 Pnnm 空间群兼容的最小四带紧束缚模型（基矢 |A↑⟩、|A↓⟩、|B↑⟩、|B↓⟩），自旋劈裂项 `J_z σ_z sin(k_x)sin(k_y)` 自然产生 d-wave 形式因子。哈密顿量包括 `ε₀(k)`、`t_x(k)`（亚晶格间跃迁）、`t_z(k)`（亚晶格内跃迁）、`λ_k·σ`（SOC 项）和 `J·σ`（Néel 序参量）。参数（单位 eV）：t₁ₓ=-0.1, t₁ᵧ=-0.05, t₂=-0.05, t₃=0.06, t₄ₓ=0.1, t₄ᵧ=0.05, t₅=-0.05, t₆=0.05, t₇=-0.1, t₈=0.15, J_z=0.1。
- **自旋输运**：计算亚晶格分辨的纵向自旋电导率 `σ^ν_A/B`，将其分解为 Drude 项（τ-odd）与自旋-贝里曲率（SBC，τ-even）项；在 altermagnet 中 Drude 项为主导且唯一贡献。注入的自旋电流由 `J^s_{A/B} = σ^AM_{A/B} E_int = σ^AM_{A/B} ρ^HM_∥ J^s_inj` 给出，**两个亚晶格的非对称性由 AM 自身的自旋电导率沿电流方向上的差异决定**。
- **LLG 模拟**：使用修正的两亚晶格耦合 LLG 方程，包含 γ（旋磁比）、α（Gilbert 阻尼）、`B^eff_i = B^ans + B^ex_i + B^ext`（各向异性+亚晶格间交换+外场），力矩 `τ^FL_i = |τ_i|ξ^FL (m̂_i × σ̂^ν)` 和 `τ^DL_i = |τ_i|ξ^DL [m̂_i × (m̂_i × σ̂^ν)]`，并引入与方向相关的唯象调制因子 `η(θ) = (1+cos²(θ/2))/2`（模拟 TMR 类效应）。
- **实验参数**：取 HM 中 E=10 V/μm → 自旋电流 Js ~ 10¹³ (ℏ/2e) A/m²，10% 跨界面传输，FeSb₂ 的 Ms~1.5×10⁵ A/m（Fe 磁矩 ~1 μB），α=0.005，J_ex=100 meV，总有效场 ~0.83 T。

### ## 主要发现与核心结论（Main Results）

- **自旋电导率的亚晶格非对称性**：在 [110] 与 [1-10] 两个正交方向上，σ^z_∥_A 和 σ^z_∥_B 不仅**大小不等**，而且在两个方向之间**符号反转**，直接证明了 ASSC 的存在并具有晶体取向可调性。
- **铁磁体失效但 ASSC 成功的关键判据**：`[C²||C⁴_z|τ]` spin group 允许每个亚晶格保持反演对称性而整体系仍存在非相对论自旋劈裂；这是 ASSC 在局部中心对称 AM 中仍能工作的根本原因，也是它优于 NSOT 的核心。
- **翻转动力学**：在合理参数下，FeSb₂ 的 Néel 矢量在 **~40 ps 内完成 180° 确定性翻转**；自旋力矩比 ξ^DL/ξ^FL 固定时，把 ξ^DL/ξ^FL 增大将使翻转时间从 ~20 ps 延长到 ~200 ps；减小 ASSC 比率 J^s_B/J^s_A 加快翻转；过大的阻尼类力矩会让 Néel 矢量进入**自旋力矩振荡器（spin-torque oscillator）**式的持续振荡，确定性翻转失败。
- **稳定性的双重锁定机制**：(1) 当 Néel 矢量旋转到 xy 平面时 B^ex 与 τ^FL 同时达极大，越过该点后 τ^FL 符号反转提供**负反馈**钉扎最终态；(2) 翻转完成后 Fermi 面自旋极化随之翻转，自然**阻断同极化自旋的进一步注入**，需反转 HM 偏置才能回到初态。
- **电学读出**：d-wave AM 的反常霍尔电导率在 Néel 矢量翻转后**符号反转**，提供与 ASSC 写入天然兼容的 AHE 读出通道（σ_λ₀=5 meV 即可产生显著 AHE）。
- **Table 1 横向比较**：NSOT 需破缺反演对称 + 强 SOC；Néel 自旋电流仅限 A/C 型 AFM 且需特殊几何或弱磁场；磁八极矩（SOT仍需配合）；**ASSC 是唯一不依赖强 SOC、无需特殊几何、适用于 d/g/i-wave中心对称 AM 的方案**。

### ## 潜在研究方向（Future Directions）

- **材料平台扩展**：已识别的可行性体系——金红石结构 RuO₂[110]/HM、KV₂Se₂O[100]/HM；g-wave体系 MnTe[11-20]/HM、FeS₂[120]/HM；i-wave 体系有待发掘。两项关键优化条件：(i) AM 层外延对准，使自旋劈裂最强的 k 方向与 HM 自旋霍尔电流方向重合；(ii) 注入自旋极化方向应平行于 Néel 矢量。
- **面内 Néel 矢量的特殊挑战**：MnTe 的 Néel 矢量在面内，常规横向自旋霍尔电流效率低，需借助 Wang 2025、Sarkar 2025 提出的**共线（collinear）自旋霍尔效应**材料平台，异质结构设计仍待优化。
- **遗留实验问题**：(1) 真实器件中跨界面自旋传输 10% 是保守假设，提高界面质量有望进一步缩短翻转时间（往 10 ps 以下推进）；(2) 翻转阈值电流密度的温度依赖、缺陷与无序的影响、多次循环耐久性未见讨论；(3) 论文是纯理论 + LLG 模拟，**实验验证是首要开放问题**。
- **与其它候选机制的取舍**：磁八极矩（Han 2025 / Baek 2025）也是 field-free 候选，但目前八极矩的实验操控困难；NSOT 在反演破缺体系中仍有效，未来可能形成"ASSC 主管 even-parity 中心对称 AM、NSOT 主管 odd-parity 破缺 AM"的互补格局。
- **未解决的基础问题**：(1) 自旋翻转的最终速度极限（与 J_ex、α 的标度关系）尚未系统给出；(2) ASSC 在多畴、非共线、非均匀电流下的鲁棒性；(3) 与 AHE 读出耦合时的串扰与信噪比；(4) 如何把 ASSC 与强场超快光学/THz 调控结合，探索**光-电-磁**协同翻转的可能性——这对林赛关注的"瞬时磁序光读出与控制"方向具有潜在价值。

---

**关键引用**（用于后续追溯）：
- Šmejkal et al., 2022 (Sci. Adv.) — altermagnet 理论奠基
- Mazin et al., 2021 — FeSb₂ 第二阶段 altermagnet 候选
- Krempaský et al., 2024 (Nature) — MnTe d-wave 自旋分辨 ARPES
- Sarkar et al., 2025 — 同组关于共线自旋霍尔效应的近期工作


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：自旋群对称性论证 + 紧束缚能带计算 + 亚晶格分辨自旋输运（Drude/SBC 分解）+ LLG 动力学模拟（不对称亚晶格自旋电流 ASSC 确定性翻转交变磁体）

**原理**：d-wave 交变磁体的方向依赖自旋劈裂 Fermi 面自然产生亚晶格非对称自旋电流（ASSC）——在 HM/AM 异质结注入后形成不平衡的场类+阻尼类力矩驱动 Néel 矢量翻转；关键判据——spin group [C²||C⁴z|τ] 允许每个亚晶格保持局部反演对称而整体系仍有非相对论自旋劈裂（ASSC 在局部中心对称 AM 中仍工作的根本原因，优于 NSOT——后者要求每个亚晶格破缺局部反演）；自旋电导分解为 Drude 项（τ-odd）与自旋-Berry 曲率 SBC 项（τ-even），AM 中 Drude 为主导且唯一贡献；亚晶格非对称性由 AM 自身自旋电导率沿电流方向的差异决定；双锁定机制——Néel 矢量旋转到 xy 平面时 B^ex 与 τ^FL 同时极大、越过该点 τ^FL 符号反转提供负反馈钉扎 + 翻转完成后 Fermi 面自旋极化随之翻转自然阻断同极化自旋进一步注入。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 紧束缚参数（eV） | t₁ₓ=−0.1, t₁ᵧ=−0.05, t₂=−0.05, t₃=0.06, t₄ₓ=0.1, t₄ᵧ=0.05, t₅=−0.05, t₆=0.05, t₇=−0.1, t₈=0.15, J_z=0.1（Pnnm 兼容最小四带模型，劈裂项 J_zσ_z sin k_x sin k_y） | 研究方法（能带模型） |
| 实验参数 | HM 中 E = 10 V/μm → 自旋电流 Js ~ 10¹³(ℏ/2e) A/m²；10% 跨界面传输；FeSb₂ Ms ~ 1.5×10⁵ A/m（Fe 磁矩 ~1 μB）；α = 0.005；J_ex = 100 meV；总有效场 ~0.83 T | 研究方法（实验参数） |
| 翻转动力学 | FeSb₂ Néel 矢量 ~40 ps 内完成 180° 确定性翻转；ξ^DL/ξ^FL 增大使翻转时间从 ~20 ps 延长到 ~200 ps；过大阻尼类力矩进入自旋力矩振荡器式持续振荡（确定性翻转失败） | 主要发现（翻转动力学） |
| 电学读出 | d-wave AM 反常霍尔电导率在 Néel 矢量翻转后符号反转（σ_λ₀ = 5 meV 即可产生显著 AHE）——与 ASSC 写入天然兼容 | 主要发现（电学读出） |
| 材料平台 | 掺杂 FeSb₂（Pnnm，未掺杂 Kondo 绝缘体、电子掺杂后金属 d-wave AM）；推广 RuO₂[110]、KV₂Se₂O[100]、MnTe[11-20]、FeS₂[120]；优化条件——外延对准使自旋劈裂最强 k 方向与 HM 自旋霍尔电流方向重合、注入自旋极化平行于 Néel 矢量 | 研究背景/潜在研究方向 |

**适用边界**：纯理论 + LLG 模拟（实验验证是首要开放问题）；跨界面自旋传输 10% 为保守假设（界面质量提高有望往 10 ps 以下推进）；翻转阈值电流密度的温度依赖、缺陷与无序影响、多次循环耐久性未讨论；面内 Néel 矢量（MnTe）常规横向自旋霍尔电流效率低（需共线自旋霍尔效应平台，异质结构设计待优化）；自旋翻转速度极限标度、多畴/非共线/非均匀电流鲁棒性、AHE 读出串扰信噪比未系统给出；与强场超快光学/THz 调控结合的光-电-磁协同翻转未探索。
**代表作**：Sarkar, Das & Agarwal, Deterministic Switching in Altermagnets via Asymmetric Sublattice Spin Current（arXiv:2510.11362，IIT Kanpur）
*方法卡回补 2026-10-03*

<!-- linsai-wikilinks -->
## 关联概念

- [[2510.11362]]
- [[Berry 曲率]]
- [[FeSb2]]
- [[Landau-Lifshitz-Gilbert 模拟]]
- [[Neel 矢量]]
- [[altermagnet]]
- [[arpes]]
- [[交变磁体]]
- [[反铁磁体]]
- [[反铁磁自旋电子学]]
- [[奈尔序]]
- [[奈尔矢量]]
- [[强场超快]]
- [[强场超快光学]]
- [[微磁模拟]]
- [[自旋劈裂]]
- [[超快自旋动力学]]
<!-- /linsai-wikilinks -->
