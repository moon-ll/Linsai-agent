---
title: "2021-doi-10-1038-s42254-021-00314-5-physics-informed-machine-learning"
type: "papers"
created: "2026-09-27T00:23:26Z"
updated: "2026-11-15T15:09:21Z"
tags: []
related: ["PINN（物理信息神经网络）", "TDSE", "general-quantum-geometry-inversion-20260726", "强场超快", "强场超快光学", "量子几何", "量子几何反演"]
source_raw: "2021-doi-10-1038-s42254-021-00314-5-physics-informed-machine-learning.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
aliases: ["10.1038/s42254-021-00314-5-physics-informed-machine-learning.md", "s42254-021-00314"]
digest_level: "abstract"
---

• ---
  title: "Physics-informed machine learning"
  type: papers
  created: "2026-09-27T00:23:10Z"
  updated: "2026-09-27T00:23:10Z"
  tags: ["机器学习", "PINN", "科学计算", "多物理场", "深度xiv"]
  related: ["机器学习", "强场超快光学"]
  source_raw: "2021-doi-10.1038/s42254-021-00314-5-physics-informed-machine-learning.md"
  growth_stage: "growing"
  confidence: 0.7
  auto_grown: true
  review_status: "pending"
  ---

  # Physics-informed machine learning

  ## 林赛的理解

  这是 Karniadakis 等人在 *Nature Reviews Physics* 发表的 PINN（物理信息神经网络）方法综述。我只看了摘要级元数据，尚未精读全文。其核心思想是把物理定律（如偏微分方程残差）作为损失函数的一部分，让神经网络在数据稀疏甚至无数据区域仍满足物理约束。我把它收进知识库，是因为我的课题组长期面对强场超快过程的数值模拟瓶颈——含时薛定谔方程、多体传播子、3D 麦克斯韦方程耦合等计算成本随维度指数增长。如果 PINN 类方法能替代一部分高维模拟或反演，对我们的 HHG 谱学反演工作可能是一条值得探索的路线。但我要强调：这篇笔记只基于元数据，具体技术细节（损失函数构造、收敛性讨论、代表性算例）需要我安排时间精读原文后再补充，目前不要在申请书里引用其中的具体结论。

  ## 核心要点

  - 主题：Physics-informed machine learning（物理信息机器学习），PINN 方法论的权威综述（Nature Reviews Physics, 2021）。
  - 定位：融合数据驱动与数学物理约束，解决高维、多物理场问题——这正是传统数值方法（网格法）随维度受困的场景。
  - 作者阵容（Karniadakis 等）是 PINN 方向最核心的一脉，综述的可信度和覆盖面在该领域属于标杆级。
  - 该论文已被 `general-quantum-geometry-inversion-20260726` 课题引用，说明课题组已有实际使用需求。
  - 注意：原始材料 abstract 为空，正文只有一句话简介，**笔记中的理解全部基于元数据和领域常识，未经原文核实**。

  ## 实验/研究关联

  - **高维模拟**：强场超快光学中的含时多体动力学是典型的高维问题，PINN 的"维度规避"特性可能在替代部分 TDSE/麦克斯韦模拟上有潜力。
  - **反演问题**：PINN 天然适合正问题-反问题统一建模，与 HHG 谱反演、量子几何反演（`general-quantum-geometry-inversion-20260726`）的方向吻合——该课题已引用本文，可考虑后续精读支撑具体章节。
  - **数据稀缺场景**：实验数据昂贵时，物理约束可替代部分监督信号，这与我们实验样本有限的处境相关。
  - 关联强度目前是**方法论层面的间接关联**，具体哪个子问题可落地，需要精读或做小规模试算验证。

  ## 开放问题

  - PINN 在刚性（stiff）PDE、多尺度振荡解（强场过程正是高度振荡）上的收敛性是否可靠？文献社区对此一直有争议，需要读原文及后续批评文献再判断。
  - 对我们关心的强场振荡体系，PINN 相比传统 TDSE 数值传播是否有真实的计算优势，还是只在低维基准问题上漂亮？
  - 综述发表于 2021 年，此后 PINN 领域有大量方法改进（如 FNO、算子学习路线），是否需要补充更新的算子学习文献形成完整图谱？
  - 该论文目前 `read_status: unread`，是否值得纳入下一轮的精读清单，建议结合课题 `general-quantum-geometry-inversion-20260726` 的实际进度决定。

  ## 来源
  - 原始材料：2021-doi-10.1038/s42254-021-00314-5-physics-informed-machine-learning.md
  - 蒸馏时间：2026-09-27T00:23:10Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：Physics-informed machine learning——PINN 方法论权威综述（Karniadakis 等，Nature Reviews Physics 2021）

**原理**：PINN 方法论的权威综述：把物理定律（如偏微分方程残差）作为损失函数的一部分，让神经网络在数据稀疏甚至无数据区域仍满足物理约束——融合数据驱动与数学物理约束，解决高维、多物理场问题（传统网格法随维度受困的场景）；作者阵容（Karniadakis 等）为 PINN 方向最核心的一脉，综述可信度与覆盖面为领域标杆。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 定位 | PINN 权威综述（Nature Reviews Physics 2021）；物理定律入损失函数 + 数据驱动融合 | 核心要点 |

**适用边界**：摘要级页面且 abstract 为空（本页自注'理解全部基于元数据和领域常识，未经原文核实'），损失函数构造、收敛性讨论、代表性算例需精读补充；PINN 在刚性 PDE/多尺度振荡解上的收敛性争议未判；相对传统 TDSE 传播是否有真实计算优势（还是仅低维基准漂亮）未验证；2021 年后 FNO/算子学习路线的方法改进需补充图谱。
**代表作**：Karniadakis 等, Physics-informed machine learning（Nature Reviews Physics, doi:10.1038/s42254-021-00314-5, 2021，综述）
*方法卡回补 2026-10-04*

<!-- linsai-wikilinks -->
## 关联概念

- [[PINN（物理信息神经网络）]]
- [[TDSE]]
- [[general-quantum-geometry-inversion-20260726]]
- [[强场超快]]
- [[强场超快光学]]
- [[量子几何]]
- [[量子几何反演]]
<!-- /linsai-wikilinks -->
