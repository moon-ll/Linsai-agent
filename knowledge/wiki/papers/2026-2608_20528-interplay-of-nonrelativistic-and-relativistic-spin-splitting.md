---
title: "2026-2608_20528-interplay-of-nonrelativistic-and-relativistic-spin-splitting"
type: "papers"
created: "2026-09-26T13:47:45Z"
updated: "2026-11-15T15:09:22Z"
tags: []
related: ["2602.20862", "2606.21281", "2606.31867", "2608.20528", "Berry 曲率", "MnPS3", "arpes", "交变磁体", "双色调Floquet驱动在2D补偿磁体中产生巨垂直Edelstein极化", "固体HHG", "强场驱动", "自旋劈裂", "量子几何", "非线性光学"]
source_raw: "2026-2608.20528-interplay-of-nonrelativistic-and-relativistic-spin-splitting.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
---

• # 交变磁体中非相对论与相对论自旋劈裂的相互作用（Interplay of nonrelativistic and relativistic spin splittings in altermagnets）

  ## 林赛的理解

  这篇工作解决了一个我一直关心的问题：交变磁体（altermagnet）的非相对论自旋劈裂（NRSS）是动量空间的效应，它如何与相对论性的 SOC 效应"串线"？作者的答案很干净——**NRSS 把弱 SOC  dressing 的能带本身已经自旋极化了，于是 Rashba 自旋劈裂不再受 SOC 强度限制，而是由 NRSS 的能量标度决定**。这相当于给 Rashba 效应提供了一个"非相对论放大器"。

  对我们最直接的用处有二：其一，NRSS 能量标度常在 0.1–1 eV，比典型 SOC（几十 meV）大一到两个量级，Rashba AM 的 Fermi 面被强烈非对称化，这意味着 **charge-to-spin conversion（Edelstein 效应）可以显著增强且 Néel 矢量可调**——这是一个可电控、可超快（THz 乃至光场）调控的自旋源。其二，他们给出的 tight-binding 三轨道 d-wave 模型 + 非中心对称 ISB 的构造方式，完全可以平移到我们的 Floquet/光场框架里——事实上作者自己就有双色 Floquet 驱动 RKKY、Floquet AMR/AHE 的姊妹工作（arXiv:2602.20862、2606.21281、2606.31867），说明这条路线的 Floquet 化是现成可接的。

  ## 研究问题

  - 破缺空间反演对称的交变磁体中，非相对论自旋劈裂（NRSS）如何重塑相对论性的 Rashba 效应（spin Rashba effect, SRE）？
  - NRSS 与 SOC、反演对称破缺（ISB）三种能量标度（E_NRSS、E_SOC、E_ISB）的竞争如何决定 Rashba 自旋劈裂的大小、自旋纹理的形态，以及电荷-自旋转换效率？
  - 这一机制是否能在真实材料（如非中心对称 g-wave 交变磁体 GdAlSi）中实现？

  核心论点：Rashba 自旋劈裂通常受限于 SOC 强度，但在交变磁体中它被 NRSS 能量标度所支配，因此可以远超本征相对论标度，产生巨大的、Néel 矢量可调的 charge-to-spin 转换。

  ## 研究背景

  - 交变磁体是实空间磁矩补偿、动量空间却存在非相对论自旋劈裂的非常规磁体（Hayami 2019、Yuan 2020、Šmejkal 2022 等奠基工作）。NRSS 已在 RuO₂、MnTe 中得到 ARPES 实验证实（如 Krempaský et al., Nature 626, 517 (2024)）。
  - 已有研究探索了交变磁体中 SOC 诱导的各向异性霍尔效应、磁光效应、XMCD 等，但 **NRSS 如何影响相对论现象基本未被探索**。
  - Rashba 效应（Bychkov-Rashba 1984）是自旋轨道电子学的核心：ISB + SOC 解除自旋简并，产生动量依赖自旋纹理。但 Rashba 劈裂量级一直被 SOC 强度卡住（Sunko et al., Nature 549, 492 (2017) 是例外思路）。
  - 机制的关键中间步骤是 **轨道 Rashba 效应（ORE）**：ISB 先通过自旋无关的轨道杂化产生轨道角动量（OAM）纹理并打开 E_ISB 能隙，SOC 再把 OAM 纹理"转印"为自旋纹理（Park et al. 2011 等）。
  - 本文的洞见：在 AM 中，由于 PT 对称性已破缺、能带本来就有 NRSS 自旋极化，ISB 在每个自旋通道内独立诱导 ORE，使轨道 Rashba 能带继承 NRSS——弱 SOC 只需"转印"，劈裂大小由 NRSS 决定。

  ## 研究方法

  - **Tight-binding 模型**：二维 d-wave 交变磁体，正方格子 A/B 两个自旋相反子格，每子格三个轨道 d_xy、d_yz、d_zx。哈密顿量 H_AM(k) = ĥ(k)τ̂_x + (Δ/2)(ℓ̂_y²−ℓ̂_x²)τ̂_z − J τ̂_z n̂·σ̂ + λ ℓ̂·σ̂，其中：
    - π 键最近邻跳跃 t = 0.5 eV；晶格常数 a = 5 Å
    - 晶体场劈裂 Δ（d_yz 与 d_zx 之间）控制 NRSS 大小，主算例 Δ = 2 eV，扫描 0–2 eV
    - 交换参数 J = 0.5 eV，Néel 矢量取 n̂ = ẑ（磁点群 4′/mm′m；ISB 后降为 4′m′m，宏观磁化严格为零）
    - SOC 强度 λ = 0.02 eV（弱 SOC 代表值）
  - **ISB 引入**：沿 ẑ 的局域电场产生反对称 interorbital 跳跃 γ = −0.05 eV，H_ISB(k) 在 Γ 点附近退化为标准 ORE 形式 α_OR ℓ̂·(ẑ×k)，轨道 Rashba 常数 α_OR = √2 a γ。
  - **自旋纹理与 Fermi 面分析**：计算自旋期望值的 k 空间分布，Fermi 面能量取 −1.0 eV。
  - **Spin Rashba-Edelstein 效应（SREE）数值计算**：对 E = E_x x̂ 计算 intra- 与 interband 电流诱导自旋极化 δS（Eq. 3a/3b，broadening Γ = 0.1 eV），并做子格分辨（δS_A、δS_B）与 Néel 矢量角度依赖分析（δS± 的 χ₀/χ₁/χ₂ 分解）。
  - **第一性原理**：对非中心对称 g-wave 交变磁体 GdAlSi 做探索性计算（FLEUR 代码），验证真实材料中机制成立。

  ## 主要发现与核心结论

  - **三个能量标度竞争决定 Rashba 物理**：
    - 常规反铁磁（Δ = 0，无 NRSS）：Rashba 劈裂 ∼ 2λ = 0.04 eV，由 SOC 决定；对 λ = 0.02 eV、γ = −0.05 eV，自旋 Rashba 耦合常数 α_SR ∼ |√2 a γλ/t| ≈ 14 meV·Å。
    - 中等 NRSS（E_SOC < E_NRSS ≲ E_ISB，如 Δ = 0.2 eV）：ORE 在每个自旋通道独立发生，轨道 Rashba 能带继承 NRSS 自旋极化，劈裂由 E_NRSS 支配，显著放大。
    - 强 NRSS（E_NRSS ≫ E_ISB，如 Δ = 2.0 eV）：自旋劈裂最大化，上界达 **∼ E_ISB/2**；代价是面内 Rashba 自旋纹理变弱（自旋更沿 Néel 矢量 ẑ 极化）。
  - **Fermi 面**：无 NRSS 时相反螺旋度的 Fermi 面近乎重合（贡献相互抵消）；引入 NRSS 后 Fermi 面强烈非对称，SREE 显著增强。E_ISB 由 γ 设定，通常远大于相对论劈裂。
  - **SREE 定量结果**（γ = −0.05 eV，λ = 0.02 eV，Γ = 0.1 eV）：
    - Δ = 0（常规 AFM）：intra 贡献 δS_y^A = δS_y^B（各向同性），inter 贡献的 δS_x 在两个子格 staggered，净响应为零。
    - Δ = 0.2 eV（AM）：δS_y 和 δS_x 都大幅放大，且既非纯 uniform 也非纯 staggered——多维自旋响应，可驱动丰富的电流诱导磁动力学。
    - ε_F = −1.0 eV 处扫描 (Δ ≥ 0, γ ≤ 0)：Δ = 0 时 δS_y 不随 |γ| 显著增强；Δ 一旦有限，即使 Δ、γ 很小两个分量都明显增大。注意：在动量无关交换劈裂的铁磁模型中观察不到这种增强，凸显 AM 自旋劈裂的独特作用。
  - **类铁磁 Edelstein 响应**：Rashba 能带沿 n̂ 强自旋极化，电场诱导 δS ∝ n̂×(ẑ×E)——与 Rashba 铁磁体自旋轨道力矩的角度依赖形式完全等价（Eq. 4 中 χ₁ 项），但**不需要净磁化**（对称性禁止 AHE 却允许此效应）。这与保 PT 的非中心对称 AFM 中 intra staggered/inter 非 staggered 的子格模式正好相反。
  - **材料验证**：第一性原理证实非中心对称 g-wave AM **GdAlSi** 实现该机制，说明不限于 d-wave 模型、可推广到不同自旋劈裂对称性。其他候选：铁电/极性 AM（BaCuF₄、Ca₃Mn₂O₇）、应变 RuO₂ 薄膜的极性交变相、栅压/衬底/非对称界面诱导 ISB 的 AM 薄膜与异质结。
  - 实验杠杆：γ 可通过栅压或应变主动调控；NRSS 常达 0.1–1 eV 标度，弱 SOC 下即可获得强 charge-to-spin 转换。

  ## 潜在研究方向

  - 机制目前建立在静态能带图像上；**Floquet/光场驱动下的版本是自然的下一步**——作者团队已有双色 Floquet 驱动 RKKY、Floquet AMR/AHE、Floquet 巨垂直 Edelstein 极化的系列预印本（arXiv:2602.20862、2606.21281、2606.31867），但本文的 NRSS-增强 Rashba 机制与周期驱动（尤其是 THz 场直接驱动 Néel 矢量进动/翻转）的耦合尚未系统研究。
  - **Néel 矢量动力学**：多维（uniform + staggered）自旋响应意味着复杂的多磁矩耦合，但真正的时间依赖翻转模拟（而非静态 Edelstein 响应）未做。
  - n̂ 取面内时体系允许弱铁磁（磁点群 m′mm′），此时效应与铁磁分量的纠缠值得澄清；本文为保持零磁化论证只做了 n̂ = ẑ。
  - GdAlSi 的第一性计算是"exploratory"（探索性），定量实验可观测量（如 Edelstein 系数绝对值、温度/无序/有限寿命效应）未给出。
  - 与手性 AM（chiral AM 中只有纵向 δS ∥ E）和非共线 AFM 的 Edelstein 效应的机制区分已论述，但实验判别方案未提。

  ## 与林赛研究的关联

  - **交变磁 + Rashba + 量子几何**：NRSS 重塑的 Rashba 能带意味着交变磁体的 Berry 曲率/量子几何在破缺反演对称后被强烈重构。我们 general-berry-mnps3-rashba 课题关注的正是 Rashba 与磁序/量子几何的耦合——本文给出"NRSS 作为 Rashba 放大器"的微观机制（ORE 转印 + E_NRSS/E_ISB/E_SOC 三标度竞争），可直接作为我们 MnPS₃ 体系分析能带劈裂与 Berry 曲率分布的模板。注意 MnPS₃ 是 van der Waals 反铁磁，是否具备 AM 型 NRSS 需要先做对称性判定。
  - **强场/阿秒超快接口**：E_NRSS 达 0.1–1 eV 对应 ~1–10 fs 动力学标度，与光场驱动兼容。栅压可调 γ（E_ISB）意味着电场可调的自旋-电荷转换效率——这正是超快自旋电子学/光控磁的接口。双色 Floquet 路线（作者姊妹工作）与我们强场驱动 Floquet 工程的经验直接对接。
  - **HHG 视角**：NRSS-增强的 Rashba 劈裂产生强非对称、强自旋极化的 Fermi 面与非平庸自旋纹理，固体 HHG 的自旋/圆偏通道对这些能带结构特征敏感；交变磁体动量空间的 d/g-wave 自旋劈裂也可能在 HHG 谱中留下可辨的对称性指纹——这是交变磁体非线性光学响应的一个开放方向，值得评估是否能作为 AM 序的光学读出手段。
  - **实验可行性**：候选材料清单（GdAlSi、极性 RuO₂ 薄膜、铁电 AM）均为薄膜/可栅控体系，与超快光学样品制备兼容。

  ## 来源
  - 蒸馏自全文（deep-read）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：交变磁体中非相对论与相对论自旋劈裂的协同放大：界面对称破缺 + 轨道 Rashba 效应转印（Tight-binding + SREE 计算）

**原理**：揭示三能量标度竞争决定交变磁体 Rashba 物理的机制：界面对称破缺（ISB）先通过自旋无关轨道杂化产生轨道角动量（OAM）纹理并打开 E_ISB 能隙（轨道 Rashba 效应 ORE），SOC 再把 OAM 纹理'转印'为自旋纹理——交变磁体中 PT 已破缺、能带本来就有 NRSS 自旋极化，ISB 在每个自旋通道内独立诱导 ORE，使轨道 Rashba 能带继承 NRSS——弱 SOC 只需'转印'、劈裂大小由 NRSS 决定（上界达 E_ISB/2）。Tight-binding：二维 d-wave AM 正方格子 A/B 子格、每子格三轨道（dxy/dyz/dzx），H = h(k)τx + (Δ/2)(ℓy²−ℓx²)τz − Jτz n̂·σ + λℓ·σ；ISB 经反对称 interorbital 跳跃 γ = −0.05 eV 引入，α_OR = √2aγ。类铁磁 Edelstein 响应 δS ∝ n̂×(ẑ×E)（与 Rashba 铁磁体 SOT 角度依赖等价）但不需要净磁化。GdAlSi（非中心对称 g-wave AM）第一性原理验证机制成立。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| Tight-binding 参数 | t = 0.5 eV（π 键最近邻）；a = 5 Å；晶体场劈裂 Δ 主算例 2 eV（扫描 0–2 eV）；交换 J = 0.5 eV；SOC λ = 0.02 eV（弱 SOC 代表值）；ISB 跳跃 γ = −0.05 eV → α_OR = √2aγ；Fermi 面 −1.0 eV；SREE broadening Γ = 0.1 eV | 研究方法·Tight-binding 模型 |
| 三标度竞争 | 常规 AFM（Δ=0）：Rashba 劈裂 ~2λ = 0.04 eV（SOC 决定），α_SR ~ 14 meV·Å；中等 NRSS（E_SOC < E_NRSS ≲ E_ISB）：ORE 每自旋通道独立、劈裂由 E_NRSS 支配显著放大；强 NRSS（E_NRSS ≫ E_ISB）：自旋劈裂最大化（上界 ~E_ISB/2）但面内 Rashba 自旋纹理变弱 | 主要发现与核心结论·三个能量标度竞争 |
| 材料验证 | GdAlSi（非中心对称 g-wave AM，FLEUR 代码）第一性原理证实；其他候选：BaCuF₄、Ca₃Mn₂O₇、应变 RuO₂ 薄膜、栅压/衬底/非对称界面 ISB 的 AM 薄膜与异质结 | 主要发现与核心结论·材料验证 |

**适用边界**：建立在静态能带图像上（Floquet/光场驱动的版本——作者团队有双色 Floquet RKKY/Floquet AMR/巨垂直 Edelstein 系列前印本——尚未系统研究）；Néel 矢量动力学（时间依赖翻转模拟）未做；n̂ 面内时允许弱铁磁（与铁磁分量的纠缠需澄清）；GdAlSi 为探索性计算（Edelstein 系数绝对值/温度/无序效应未给）；与手性 AM、非共线 AFM 的实验判别方案未提。
**代表作**：arXiv:2608.20528。强场接口：E_NRSS 达 0.1–1 eV 对应 ~1–10 fs 动力学标度与光场驱动兼容；栅压可调 γ（E_ISB）= 电场可调自旋-电荷转换效率——超快自旋电子学接口；NRSS-增强 Rashba 劈裂产生强非对称强自旋极化 Fermi 面，固体 HHG 的自旋/圆偏通道对其敏感——AM 序光学读出的开放方向。
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[2602.20862]]
- [[2606.21281]]
- [[2606.31867]]
- [[2608.20528]]
- [[Berry 曲率]]
- [[MnPS3]]
- [[arpes]]
- [[交变磁体]]
- [[双色调Floquet驱动在2D补偿磁体中产生巨垂直Edelstein极化]]
- [[固体HHG]]
- [[强场驱动]]
- [[自旋劈裂]]
- [[量子几何]]
- [[非线性光学]]
<!-- /linsai-wikilinks -->
