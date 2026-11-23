---
title: "2024-s41567-024-02640-8-ultrafast-high-harmonic-spectroscopy-of-solids"
type: "papers"
created: "2026-09-27T04:54:31Z"
updated: "2026-11-15T15:09:24Z"
tags: []
related: ["Berry 曲率", "Berry曲率", "arpes", "固体HHG", "固体高次谐波", "强场超快", "高次谐波光谱学"]
source_raw: "2024-s41567-024-02640-8-ultrafast-high-harmonic-spectroscopy-of-solids.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
aliases: ["s41567-024-02640"]
digest_level: "abstract"
---

• ---
  title: "Ultrafast high-harmonic Spectroscopy of Solids（Nature Physics 2024 综述）"
  type: papers
  created: "2026-09-27T04:53:52Z"
  updated: "2026-09-27T04:53:52Z"
  tags: ["固体高次谐波", "超快光谱学", "Berry曲率", "拓扑材料", "多体关联", "综述"]
  related: ["强场超快", "固体HHG", "moiré强场探测", "拓扑光电子学"]
  source_raw: "2024-s41567-024-02640-8-ultrafast-high-harmonic-spectroscopy-of-solids.md"
  growth_stage: "growing"
  confidence: 0.6
  auto_grown: true
  review_status: "pending"
  ---

  # Ultrafast high-harmonic Spectroscopy of Solids（Nature Physics 2024 综述）

  ## 林赛的理解

  这是一篇 Nature Physics 上关于**固体高次谐波（HHG）光谱学**的综述（Heide, Kobayashi, Haque, Ghimire，Nat. Phys. 20, 1546-1557, 2024）。Ghimire 组是固体 HHG 领域的开创性团队之一，这篇综述的分量在于它把过去几年"HHG 不仅是辐射源、更是能谱学工具"这条主线系统化了。我目前只有摘要级的元数据（原文摘要为空），尚未拿到全文，所以下面基于我对该领域的了解和题录信息给出理解框架，具体论证和数值以通读原文为准。

  从题录看，综述的核心定位是：固体 HHG 光谱学作为**超快探测手段**，可以同时触及三条主线——

  - **电子能带结构**：HHG 谱的截止位置、多平台结构对能带色散和带隙敏感；
  - **拓扑性质与 Berry 曲率**：偶次谐波、圆偏振选择性等对称性破缺信号可映射 Berry 连接/曲率的贡献；
  - **多体关联**：在关联材料中，谐波辐射携带电子-电子相互作用、激子乃至非平衡相的信息。

  这与我课题组"用强场超快光探测量子材料"的总路线高度同构——HHG 光谱学本质上是把"泵浦-探测"压缩到单个光周期内、无需时间延迟扫描的全光学能谱学。

  ## 核心要点

  - **综述性质**：系统梳理固体 HHG 作为超快光谱学工具的理论框架与实验进展，非单篇原创结果报道。
  - **三大探测对象**：能带结构、拓扑性质（含 Berry 曲率讨论）、多体关联效应。
  - **方法论意义**：HHG 光谱提供亚周期时间分辨与全布里渊区动量信息的结合，这是传统 ARPES 或线性光谱难以同时获得的。
  - **领域地位**：Nature Physics 综述 + Ghimire 团队主笔，可作为该方向的权威参考框架与入门/引用锚点。

  ## 实验/研究关联

  - **直接支撑课题**：已被 `general-moire-strong-field-probe-20260726`（moiré 体系强场探测）引用为文献依据。moiré 超晶格的平带、可调控拓扑与强关联恰好落在本综述"能带 + 拓扑 + 多体"三主轴的交叉点上，HHG 光谱学可为 moiré 体系提供非平衡、亚周期分辨的整体能谱读出——这是我们课题方法学设计的关键参照。
  - **对课题组的方法学价值**：综述中对 Berry 曲率可观测量的梳理（如偏振选择性、偶次谐波）可直接转化为 moiré/二维材料 HHG 实验的观测量选取依据。
  - **待办**：获取全文（当前 `has_pdf: false`），精读后对"Berry 曲率相关章节"和"关联材料章节"做深度笔记，回填到本页。

  ## 开放问题

  - 原文摘要为空，综述的具体章节结构、覆盖的实验体系清单、对理论模型（如半导体 Bloch 方程、Wannier 图像）的取舍均未确认，需通读后补全。
  - 综述对**关联材料 HHG** 的讨论深度如何？是否给出可操作的观测量-物理量对应表？这是与我们 moiré 课题最相关的部分。
  - 对 **Berry 曲率贡献**的提取：综述是否讨论了如何从谐波谱中定量（而非仅定性）分离 Berry 曲率项与带内/带间电流的贡献？
  - 综述成文于 2024 年，此后（2024-2026）固体 HHG 能谱学在转角体系、激子 HHG 方向的新进展需要另行追踪补链。

  ## 来源
  - 原始材料：2024-s41567-024-02640-8-ultrafast-high-harmonic-spectroscopy-of-solids.md
  - 蒸馏时间：2026-09-27T04:53:52Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：综述——固体高次谐波光谱学：能带结构/拓扑（Berry 曲率）/多体关联三大探测主线（Heide, Kobayashi, Haque, Ghimire，Nature Physics 2024）

**原理**：系统梳理固体 HHG 作为超快光谱学工具（非辐射源视角）的理论框架与实验进展，三大探测对象——①电子能带结构（截止位置/多平台结构对能带色散与带隙敏感）；②拓扑性质与 Berry 曲率（偶次谐波、圆偏振选择性等对称破缺信号映射 Berry 联络/曲率贡献）；③多体关联（关联材料中谐波携带 e-e 相互作用/激子/非平衡相信息）；方法论意义：HHG 光谱同时提供亚周期时间分辨与全布里渊区动量信息——传统 ARPES 或线性光谱难以兼得；Ghimire 组（固体 HHG 开创团队）主笔的权威参考框架。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 发表信息 | Heide, Kobayashi, Haque, Ghimire, Nature Physics 20, 1546-1557 (2024) | 林赛的理解 |
| 三大主线 | 能带结构 + 拓扑/Berry 曲率 + 多体关联 | 核心要点 |

**适用边界**：摘要级页面且原文摘要为空（本页自注'具体论证和数值以通读原文为准'），章节结构、实验体系清单、对 SBE/Wannier 模型的取舍均未确认；关联材料 HHG 的讨论深度与观测量-物理量对应表待查；Berry 曲率贡献的定量（非定性）分离方案是否给出待核；2024 年后转角体系/激子 HHG 新进展需另行补链；has_pdf: false。
**代表作**：Heide, Kobayashi, Haque, Ghimire, Ultrafast high-harmonic Spectroscopy of Solids（Nature Physics 20, 1546-1557, 2024，综述）
*方法卡回补 2026-10-03*

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry 曲率]]
- [[Berry曲率]]
- [[arpes]]
- [[固体HHG]]
- [[固体高次谐波]]
- [[强场超快]]
- [[高次谐波光谱学]]
<!-- /linsai-wikilinks -->
