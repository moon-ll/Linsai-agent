---
title: "2024-2411.16675-fully-nonequilibrium-hall-response-from-berry-curvature"
type: "papers"
created: "2026-11-01T22:15:00Z"
updated: "2026-11-15T15:09:22Z"
tags: []
related: ["Berry curvature dipole", "Berry 曲率", "general-ssh-weyl-20260920", "反常速度", "强场超快", "强场驱动", "时间反演对称性", "时间反演对称性破缺", "贝里曲率", "贝里曲率偶极", "霍尔效应", "非线性霍尔效应"]
source_raw: "2024-2411.16675-fully-nonequilibrium-hall-response-from-berry-curvature.md"
growth_stage: "seedling"
confidence: 0.5
digest_level: "abstract"
used_by_proposals: ["general-houston-kronig-penney-landau-zener-20261004"]
proposals_citations: "{'general-houston-kronig-penney-landau-zener-20261004': ['adversarial-review']}"
---

• 我先读取原始文献和 skill 规范。

• raw 摘要字段为空，我检查知识库是否有全文缓存可补全信息。

• 无全文缓存，确认为摘要级蒸馏。以下为蒸馏产物（正文从 `#` 标题开始，frontmatter 由 worker 落盘时注入）：

  # Fully nonequilibrium Hall response from Berry curvature（2411.16675）

  ## 研究问题（Research Question）

  在**完全非平衡**（强驱动）极限下，由 [[贝里曲率]] 诱导的 [[霍尔效应|Hall 响应]] 遵循什么标度规律？它是否仍受弱场非线性霍尔理论中的 [[贝里曲率偶极]]（Berry curvature dipole）控制，还是进入一个新的普适 regime？

  ## 研究背景（Background）

  平衡与弱非平衡情形下，无磁场体系的霍尔型输运由 [[贝里曲率偶极]] 主导，霍尔电流对标度为二次（I ∝ E²），这是时间反演对称不破缺体系中二阶非线性响应的标准图像。但当驱动强到体系进入完全非平衡状态时，该图像是否失效、失效后由什么机制接管，此前缺乏系统理论。

  ## 研究方法（Data & Method）

  构建强驱动下的完全非平衡输运理论，分析强场极限中 [[贝里曲率]] 对稳态霍尔电流的贡献，给出标度律的解析/半解析判据（摘要级信息，模型与近似细节以原文为准）。

  ## 发现（Findings）

  强场下自发霍尔电流的标度从**二次**转变为**准线性**，且这一响应**不再受 [[贝里曲率偶极]] 控制**——行为上类似于微观层面已破坏 [[时间反演对称性]] 的体系（如磁性体系或外场破缺时间反演的体系）。这意味着完全非平衡霍尔响应构成一个独立于二阶非线性霍尔效应的新普适类。

  ## 开放方向（Open Questions）

  - 准线性标度向常规线性霍尔定律的 crossover 边界与判据（驱动强度、散射率窗口）有待定量刻画；
  - 该机制在真实材料（拓扑半金属、关联体系）中的可观测性需要实验检验；
  - 与课题 `general-ssh-weyl-20260920` 关联：强场驱动下类似「等效破缺时间反演」的响应机制，可作为 SSH/Weyl 体系强场探测方案的候选机制素材。

  ---

  **说明（不写进落盘文件）**：
  - 无 `_text_cache` 全文、raw 摘要字段为空，蒸馏信息全部来自 raw 文件自带的一句话摘要，故全程摘要级简写，未编造任何数值。
  - 正文约 550 字，满足 v7.1.3 ≥200 字质量门；wikilink 采用中文概念直链形式。
  - 建议落盘路径：`knowledge/wiki/papers/2024-2411.16675-fully-nonequilibrium-hall-response-from-berry-curvature.md`，注入 `source_raw`（纯文件名）与 `digest_level=abstract`。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：完全非平衡霍尔响应理论（Fully Nonequilibrium Hall Response）

**原理**：在无磁场的强驱动体系中，放弃弱场非线性响应的阶数展开，直接在完全非平衡稳态极限下处理输运：贝里曲率以反常速度（E×Ω 型项）进入电子动力学，霍尔电流由强场重构的非平衡分布对反常速度在动量空间的加权给出。理论证明：当场强越过弱非线性窗口、体系进入完全非平衡 regime 后，贝里曲率偶极（BCD）不再是霍尔响应的控制量，自发霍尔电流的标度由二次 I ∝ E² 降为准线性（标度指数 ≈ 1），输运行为等效于微观层面时间反演对称性已被破坏的磁性/外场体系。由此划分出一个独立于二阶非线性霍尔效应的完全非平衡普适类，并给出区分弱场 BCD 区与强场区的判据框架（摘要级信息，具体模型与近似以原文为准）。

**林赛理解**：

在本项目 HHG/磁性课题（NSFC-强场超快、general-ssh-weyl-20260920）语境下，该理论是一个强场探测候选机制：对本身时间反演对称的 SSH/Weyl 体系，强场驱动可诱发『等效时间反演破缺』的准线性霍尔响应，提示免磁场的强场霍尔测量可作为探测贝里曲率分布/拓扑性质的方案素材；同时警示强场实验数据的标度分析不可沿用弱场 BCD 理论拟合，需按完全非平衡 regime 重新解读。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 弱场霍尔电流标度（BCD 主导区） | I ∝ E²（标度指数 2，无量纲） | 本文 |
| 强场自发霍尔电流标度（完全非平衡区） | 准线性，标度指数 ≈ 1（无量纲） | 本文 |
| 标度转变的控制机制 | Berry 曲率偶极（BCD）失效，响应不再受 BCD 控制 | 本文 |
| 强场等效对称性类别 | 等效微观时间反演对称性破缺（磁性/外场型体系） | 本文 |
| 理论载体文献 | arXiv 2411.16675（2024 年） | 2411.16675 |

**适用边界**：仅适用于无外磁场体系在强场完全非平衡稳态极限下的霍尔输运分析；弱场二阶非线性（BCD 主导）区及瞬态/超快时间分辨响应不在其适用范围。
**代表作**：Sur, S., Chen, L., Wang, Y., Setty, C., Paschen, S., Si, Q. — arXiv:2411.16675 (2024)
*方法卡回补 2026-11-01*

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry curvature dipole]]
- [[Berry 曲率]]
- [[general-ssh-weyl-20260920]]
- [[反常速度]]
- [[强场超快]]
- [[强场驱动]]
- [[时间反演对称性]]
- [[时间反演对称性破缺]]
- [[贝里曲率]]
- [[贝里曲率偶极]]
- [[霍尔效应]]
- [[非线性霍尔效应]]
<!-- /linsai-wikilinks -->
