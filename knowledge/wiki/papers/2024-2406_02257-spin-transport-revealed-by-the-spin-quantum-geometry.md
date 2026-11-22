---
title: "2024-2406_02257-spin-transport-revealed-by-the-spin-quantum-geometry"
type: "papers"
created: "2026-09-27T00:11:05Z"
updated: "2026-11-15T15:09:19Z"
tags: []
related: ["2406.02257", "Berry 曲率", "general-quantum-geometry-inversion-20260726", "位移电流", "反常霍尔效应", "强场超快", "强场驱动", "拓扑绝缘体", "量子几何", "量子几何张量", "量子度规", "非线性霍尔效应"]
source_raw: "2024-2406.02257-spin-transport-revealed-by-the-spin-quantum-geometry.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
---

• # Spin transport revealed by the spin quantum geometry（自旋量子几何揭示的自旋输运）

  ## 林赛的理解

  这篇工作是量子几何（QGT）框架向自旋自由度的一次系统性推广，价值不在于某个单一效应，而在于它给出了一张**完整的对称性—响应映射表**：自旋 QGT（spin QGT）统管自旋流，Zeeman QGT 统管自旋磁化，线性/非线性、内禀/外禀、DC/AC 全部到二阶电场为止都能在一张表（Table I）里对号入座。对我们组而言，这篇论文是"量子几何 → 可观测输运响应"这一逻辑链条在自旋侧的模板——我们关心的强场超快场景中，Berry 曲率、量子度规及其偶极矩正是光致电流、非线性霍尔、位移电流的共同语言。尤其值得注意的是 **AC 场下的位移自旋流（displacement spin current）**：它是绝缘体中、无需耗散的频率依赖响应，与超快自旋电子学（ultrafast spintronics）直接对口，是"光场—量子几何—自旋流"接口的干净理论载体。方法上，密度矩阵响应理论 + 低能有效 Dirac 模型 + 对称性分析（P/T/PT 宇称表）的推导套路，可以直接搬进我们课题的输运理论小节。一线要留意：该文作者信息与 frontmatter 元数据不符（详见"来源"节），引用时须以原文为准。

  ## 研究问题

  能否把描述电荷输运的量子几何张量（QGT）框架，推广到 Bloch 电子的**自旋自由度**上，从而统一描述电场诱导的自旋流（spin current）与自旋磁化（spin magnetization）？具体子问题包括：

  - 已知自旋响应——内禀自旋霍尔效应（Sinova 等）、磁性自旋霍尔效应（Mn3Sn）、Edelstein 效应、近年发现的非线性自旋流/自旋磁化——能否在统一的几何对象下归类？
  - 是否存在被遗漏的新响应函数？作者预言了三类：**位移自旋流/自旋磁化**（AC 场、绝缘体中可存在）、**非线性 Drude 自旋流（NDSC）** 与 **非线性 Drude 自旋磁化（NDSM）**（均正比于弛豫时间平方 τ²）。
  - 这些新响应在真实材料（拓扑绝缘体 Dirac 模型）中量级如何，能否超过近年颇受关注的非线性内禀对应项？

  ## 研究背景

  - 电荷输运的量子几何语言已相当成熟：T 奇 Berry 曲率（BC）支配铁磁内禀反常霍尔效应；T 偶 P 奇 Berry 曲率偶极（BCD）驱动非中心对称金属的非线性霍尔效应（Sodemann & Fu, 2015；WTe₂ 实验）；P 奇 T 奇但 PT 偶的量子度规偶极（QMD）导致无反演磁体的内禀非线性霍尔效应（CuMnAs、Mn₃Sn 相关实验，Science 381, 181 (2023)、Nature 621, 487 (2023)）。
  - 自旋侧响应长期各自为政：自旋流（内禀自旋霍尔、磁性自旋霍尔、非线性自旋霍尔）与自旋磁化（Edelstein 效应、磁体中的内禀自旋磁化、中心对称磁体中的非线性自旋生成）已知由波函数决定，但缺乏统一的量子几何表述。
  - 前人已有拼图碎片：spin BC 已知用于理解内禀自旋霍尔效应（Sinova et al., PRL 92, 126603 (2004)）；spin QM 的类似表达式散见于早期文献（Freimuth et al. 2014；Zhang et al. 2024）但未从量子几何视角明确讨论；Zeeman QGT 由本组前期工作（Xiang et al., PRL 134, 116301 (2025)）基于自旋子 Bloch 态 Hilbert 空间的量子距离提出，已用于内禀回转磁流（gyrotropic magnetic current）。本文在此基础上完成自旋侧的统一。

  ## 研究方法

  理论方法论文（无实验装置），方法密度集中在**密度矩阵响应理论 + 模型计算**，按方法卡要素整理如下。

  **原理**：以密度矩阵形式论（density matrix formalism）推导电场二阶以内自旋流/自旋磁化的响应张量，按弛豫时间 τ 的幂次分解（σ = σ⁽⁰⁾+σ⁽¹⁾+σ⁽²⁾，β 同理），识别每一项的几何本源（spin/Zeeman 的 QM、BC、QMD、BCD）；核心几何对象为自旋 QGT（T^ab;c_nm = va;c_nm vb_mn / ε²_nm，由自旋流算符 v̂a;c = {v̂a, σ̂c}/4 构造）与 Zeeman QGT（T̄^ab_nm = ra_nm σb_mn）。

  **计算设置与参数表**（数值均原样来自原文）：

  - 弛豫时间（数值计算取）：τ = 0.5 ps（Fig. 1(a)、Fig. 1(b) 均取此值，引用 Ref. [23]）
  - NDSC 模型（拓扑晶体绝缘体 SnTe 表面一对有质量 Dirac 锥，含倾斜项）：H_sΛ = vx kx σ̂y − s vy ky σ̂x + β σ̂z + s α ky，s = ±1；参数 vx = vy = 10⁵ m/s，β = 10 meV，α = 0.1 vx（Fig. 1(a)）
  - 该模型自旋 QM 相关分量：gyx;y_±∓ = s vx α(v²y k²y + β²) / [8(v²x k²x + v²y k²y + β²)²]，对 kx、ky 均为偶函数
  - NDSM 模型（破缺 T 对称的有质量 Dirac 模型，拓扑绝缘体表面可实现）：H = v(kx σ̂x + ky σ̂y) + Δ σ̂z；参数 Δ = 40 meV（Fig. 1(b)）
  - 该模型 Zeeman BC：Ω̄xz_±∓ = ∓v²Δkx/(v²k² + Δ²)^{3/2}，Ω̄yz_±∓ = ∓v²Δky/(v²k² + Δ²)^{3/2}
  - NDSM 解析结果：β⁽²⁾_zxx = μB e²/ℏ² · τ²/(16π) · Δ(μ²−Δ²)/|μ|³，μ ∉ (−Δ, Δ)
  - 内禀对应项解析结果：β⁽⁰⁾_zxx = μB e² [3(1+π)Δ³ − 5πΔ|μ|²]/(960π²|μ|⁵) + Δ(|μ|²−Δ²)/(960π²|μ|⁵)（μ ∉ (−Δ, Δ)，含 Fermi-sea 与 Fermi-surface 两部分）；β⁽⁰⁾_zyy = μB e² · 3(1−2π)Δ³/(960π²|μ|⁵)（μ ∈ [−Δ, Δ]，仅 Fermi-sea 贡献）
  - 零温、逐化学势 μ 数值积分（Eq. (9)），与内禀项对比
  - 补充材料（SM）含第一性原理计算（引用 VASP/PAW、PBE 泛函、Dudarev LSDA+U、Wannier90，见 Refs. [76]-[79]），用于位移自旋霍尔电流的模型之外验证
  - 对称性分析：对 spin/Zeeman QGT 的 QM、BC、QMD、BCD 在 P、T、PT 下的宇称列表（Table I），据此为新效应选模型（NDSC 需 P 破缺 → SnTe 型模型；NDSM 为 P 偶 T 奇 → 破 T 的 Dirac 模型）
  - 量级标度律（量纲分析）：σ⁽²⁾_abd;c / σ⁽⁰⁾_abd;c ~ τ²μ²/ℏ²；取 τ ~ 10⁻¹³ s、μ ~ 10⁻² eV（moderately dirty 轻掺杂）得比值 ~ 2，即 NDSC 与内禀非线性项竞争可比

  **适用边界**：Eqs. (4)-(5)、(9)-(12) 仅为 Fermi-surface 贡献，只出现在金属；Eqs. (6)-(8)、(13)-(14) 含 Fermi-sea 贡献，金属与绝缘体均可；Eqs. (13)-(14) 分别忽略四带与三带过程，其影响一般认为可忽略（Refs. [83]-[86]）；Eq. (3) 在无自旋轨道耦合时为零，Eq. (2) 在自旋极化体系中退化为常规 QGT；σ⁽¹⁾_ab;c 还可能含 vab;c_nn = ⟨un|{∂a∂bH, σ̂c}|un⟩/2 项，但当 H 对 ka 为线性或二次时不贡献自旋霍尔流，可忽略（footnote 80）。

  **代表作**：Xiang, Jin & Wang, arXiv:2406.02257（本文，自旋量子几何统一框架）；Xiang et al., PRL 134, 116301 (2025)（Zeeman QGT 与本框架的直接前身）。

  ## 主要发现与核心结论

  1. **统一框架建立**：自旋 QGT 统辖自旋流、Zeeman QGT 统辖自旋磁化；至电场二阶为止所有已知自旋响应均可归入 spin/Zeeman 的 QM、BC、QMD、BCD——线性外禀自旋流由 T 奇 spin QM 支配（磁性自旋霍尔效应，对应 Mn₃Sn 与 Fe₃GeTe₂/MoTe₂ 观测），线性外禀自旋磁化由 T 偶 Zeeman BC 支配（Edelstein 效应）；线性内禀自旋流由 T 偶 spin BC 支配（Sinova 内禀自旋霍尔效应），线性内禀自旋磁化由 T 奇 Zeeman QM 支配（磁绝缘体）。
  2. **新响应一：位移自旋流与位移自旋磁化**。AC 电场下，自旋 BC 与自旋 QM（Zeeman BC 与 Zeeman QM）同时贡献频率依赖的内禀响应（Eqs. (7)-(8)，λ₁^nm = −ω²cos(ωt)/(ω²−ε²_nm)，λ₂^nm = ε_nm ω sin(ωt)/(ω²−ε²_nm)）；σ⁽⁰⁾_ab;c(ω)（a≠b）给出**内禀位移自旋霍尔流**，绝缘体中亦可存在——此为首次提出（内禀位移自旋磁化已有前人讨论，Refs. [65][66]）。
  3. **新响应二：NDSC 与 NDSM**，均 ∝ τ²（类比非线性 Drude 电荷电流），分别由 spin QMD 与 Zeeman BCD 诱导，与其非线性内禀对应项共享同一量子几何本源。
  4. **定量量级（Dirac 模型计算，τ = 0.5 ps）**：
     - NDSC：σ⁽²⁾_yxy;y 在带隙附近出现大峰并随 μ 变号，比非线性内禀自旋霍尔电导 σ⁽⁰⁾_yxy;y **大两个量级**；带隙内 σ⁽⁰⁾ 的 Fermi-sea 贡献可忽略。
     - NDSM：β⁽²⁾_zxx 比其内禀对应项 β⁽⁰⁾_zxx **大三个量级**（Δ = 40 meV），NDSM 在该体系中占主导。
     - 标度分析：moderately dirty（τ ~ 10⁻¹³ s）+ 轻掺杂（μ ~ 10⁻² eV）下，NDSC/内禀 ~ 2、NDSM/内禀 ~ 2，二者将与内禀对应项竞争。
  5. **应用展望**：NDSC 可望像非线性内禀自旋霍尔流一样实现无外场垂直磁化翻转（field-free switching）；NDSM 可在中心对称磁体中产生自旋极化；线性位移自旋霍尔流是超快自旋电子学的候选机制；spin BCD 为 P 奇 T 奇 PT 偶，可像常规 QMD 的非线性反常霍尔流一样用于反铁磁体中 Néel 矢量翻转的探测。
  6. 全文的自旋输运公式（Eqs. (5)-(13)）与第一性原理结合，可解释实验并指导自旋电子学量子材料设计；Eqs. (2)-(3) 还可推广至光诱导的共振自旋流/自旋磁化（本文仅处理非共振情形）。

  ## 潜在研究方向

  - **实验验证缺失**：NDSC、NDSM、内禀位移自旋霍尔流均为理论预言，尚无实验观测；第一性原理 + 材料筛选（哪些真实材料的 spin QMD / Zeeman BCD 最大）是直接的下一步。
  - **共振推广未展开**：Outlook 明确指出 spin/Zeeman QGT 可揭示光照下的共振自旋流（Ref. [50]）与共振自旋磁化（Refs. [67][68]），本文限于非共振情形——光频域（含太赫兹—可见）的显式公式与材料实现是开放问题。
  - **多带过程**：Eqs. (13)-(14) 忽略了四带/三带过程，仅在"影响可忽略"的假设下成立，严格评估其修正有待后续工作。
  - **耗散与 τ 依赖的两面性**：NDSC/NDSM 依赖 τ²，moderately dirty 区间才与内禀项竞争；极干净极限内禀项主导、极脏极限 Drude 图像本身失效，最优窗口的定量边界值得细化。
  - **常规 QM 的旁路贡献**：Eqs. (13)-(14) 还可源自常规 QM（gab_nm），几何本源的归属在多带实际材料中可能不唯一。
  - 位移自旋流的"极化函数"类比推导（SM）与位移电荷电流的 ℏω ≪ ε_nm 绝热极限之间的衔接、以及绝缘体中实验读取方式（探测方案）尚未给出。

  ## 与林赛研究的关联

  - **量子几何 ↔ 输运/光响应的统一语言**：本工作把"QM/BC/QMD/BCD → 电荷响应"的词典完整复制到自旋侧。我们课题中 HHG、阿秒探测、强场驱动电流所依赖的 Berry 曲率与量子度规，在此框架下可与自旋自由度对接——为"强场驱动 + 自旋分辨探测"（如 spin-resolved HHG 或自旋极化光电流）提供理论抓手。
  - **位移自旋流（AC、绝缘体、无能耗）是"超快 + 量子几何"的直接接口**：其频率依赖结构 λ₁、λ₂ 含共振分母 (ω²−ε²_nm)，与 Ahn, Guo, Nagaosa, Vishwanath（Nat. Phys. 18, 290 (2022)）的共振光学响应几何理论同源；将本文非共振公式推进到光频共振区，正是 Outlook 点名未做的方向，与我们强场超快主线天然互补。
  - **磁性自旋霍尔效应 = T 奇 spin QM 项（Eq. (4)）**，正是 frontmatter 摘要所述 Mn₃Sn 磁性自旋霍尔效应（Kimata et al., Nature 565, 627 (2019)；Mook et al., PRR 2, 023065 (2020)）与 Goswami 等量子几何方案的理论落点——本组 quantum-geometry-inversion 课题（used_by: general-quantum-geometry-inversion-20260726）的方法学引文链可由此文 Table I 反向追溯。
  - **非线性 Drude 自旋响应的 τ² 标度**提示一个普遍教训：在含耗散的强场/非线性输运中，外禀 τ 幂次项可以在 moderately dirty 区间压倒内禀几何项（此处大 2-3 个量级）——评估我们方案中非线性光电流的几何贡献时，必须同步估计 Drude 型背景，否则几何信号可能被淹没或误读。
  - **方法学可直接迁移**：密度矩阵响应理论 + τ 幂次分解 + P/T/PT 宇称表选模型 + 低能 Dirac 模型参数化（vx、Δ、倾斜 α）的推导流程，是我们课题"输运/光响应理论小节"的可复用方法素材；SM 中 VASP(PBE, Dudarev U) + Wannier90 的第一性原理管道同样适用于我们材料候选的量子几何量计算。
  - **莫尔方向**：Eq. (1) 与多带 QGT 的形式与转角体系的量子几何（moiré 平带、Berry 物理）文献（Ref. [37]）一致，自旋 QGT 在莫尔磁体/转角磁异质结中的推广是潜在交叉点。

  ## 来源

  - 蒸馏自全文（deep-read）
  - arXiv:2406.02257v3 [cond-mat.mtrl-sci]（2025-08-05 版）；原文作者：Longjun Xiang, Hao Jin（通讯，jh@szu.edu.cn）, Jian Wang（通讯，jianwang@hku.hk），深圳大学 / 粤港澳大湾区量子科学中心 / 香港大学
  - **元数据核对警示**：frontmatter 中 authors 字段（"C. Xiao, H. Liu, J. Zhao, H. Z. Lu et al."）与摘要段（述及 Goswami 等 Mn₃Sn 方案）与本 PDF 全文内容不符——该作者组合对应 C. Xiao 等的非线性自旋生成系列工作（本文 Refs. [63][64]）。引用本文时须以原文作者 Xiang, Jin & Wang 为准；摘要段所述 Mn₃Sn 磁性自旋霍尔效应结论实际由本文 Eq. (4)（spin QM 项）承接并引用 Kimata et al. 2019 / Mook et al. 2020，非 Goswami。DOI 字段为空，保持原样。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：自旋量子几何驱动的自旋输运理论（自旋/Zeeman QGT 分解 + 弛豫时间幂次响应）

**原理**：密度矩阵形式论推电场二阶以内自旋流/自旋磁化响应张量，按弛豫时间幂次分解（σ=σ⁽⁰⁾+σ⁽¹⁾+σ⁽²⁾）识别各阶的几何本源：自旋 QGT（T^ab;c=v^a;c v^b/ε²，自旋流算符 {v̂a,σ̂c}/4 构造）与 Zeeman QGT 的 QM/BC/QMD/BCD 四分量；对称性宇称表（P/T/PT，Table I）指导模型选择——NDSC（P 破缺，SnTe 型倾斜有质量 Dirac 锥）验证自旋 QM 效应、NDSM（破 T 有质量 Dirac）验证 Zeeman BC 效应，零温逐化学势数值积分与解析渐近对比；SM 用 VASP+Wannier90 做位移自旋霍尔电流的第一性验证。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 弛豫时间 | τ = 0.5 ps（数值计算取值） | §计算设置 |
| NDSC 模型 | vx=vy=10⁵ m/s，β=10 meV，α=0.1vx（SnTe 表面有质量倾斜 Dirac 锥） | §计算设置 |
| NDSM 模型 | Δ = 40 meV；解析 β⁽²⁾_zxx=µB e²τ²/(16π)·Δ(µ²−Δ²)/|µ|³（µ∉(−Δ,Δ)） | §计算设置 |

**适用边界**：半经典弛豫时间展开（τ 幂次截断在强散射下失效）；模型为有效 Dirac 描述（材料细节进参数）；零温结果向有限温外推未系统给出。
**代表作**：本文（arXiv:2406.02257）；第一性验证：VASP/PAW + PBE + Dudarev LSDA+U + Wannier90
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[2406.02257]]
- [[Berry 曲率]]
- [[general-quantum-geometry-inversion-20260726]]
- [[位移电流]]
- [[反常霍尔效应]]
- [[强场超快]]
- [[强场驱动]]
- [[拓扑绝缘体]]
- [[量子几何]]
- [[量子几何张量]]
- [[量子度规]]
- [[非线性霍尔效应]]
<!-- /linsai-wikilinks -->
