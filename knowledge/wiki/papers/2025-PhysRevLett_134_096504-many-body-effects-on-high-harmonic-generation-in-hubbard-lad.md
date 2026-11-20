---
title: "2025-PhysRevLett_134_096504-many-body-effects-on-high-harmonic-generation-in-hubbard-lad"
type: "papers"
created: "2026-09-27T02:15:09Z"
updated: "2026-11-15T15:09:21Z"
tags: []
related: ["general-quantum-geometry-inversion-20260726", "三步模型", "固体高次谐波", "强关联体系", "强场超快", "高次谐波产生"]
source_raw: "2025-PhysRevLett.134.096504-many-body-effects-on-high-harmonic-generation-in-hubbard-lad.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
digest_level: "abstract"
---

• ---
  title: "Many-Body Effects on High-Harmonic Generation in Hubbard Ladders（Hubbard 梯子中高次谐波产生的多体效应）"
  type: papers
  created: "2026-09-27T02:14:50Z"
  updated: "2026-09-27T02:14:50Z"
  tags: ["强场物理", "高次谐波产生", "强关联体系", "Hubbard模型", "多体效应"]
  related: ["固体高次谐波", "强关联电子体系", "U/t 比值", "doublon-holon 动力学"]
  source_raw: "2025-PhysRevLett.134.096504-many-body-effects-on-high-harmonic-generation-in-hubbard-lad.md"
  growth_stage: "growing"
  confidence: 0.7
  auto_grown: true
  review_status: "pending"
  ---

  # Many-Body Effects on High-Harmonic Generation in Hubbard Ladders（Hubbard 梯子中高次谐波产生的多体效应）

  ## 林赛的理解

  这篇 PRL（Murakami, Hansen, Takayoshi, Madsen, Werner, 2025）是强关联体系 HHG 方向我重点关注的一类工作。我团队这些年一直在推动"HHG 作为关联电子体系探针"这条线，而 Hubbard 梯模型是少数能在严格数值框架（如非平衡格林函数方法，合作者 Werner/Madsen 组正是这条技术路线的主力）下处理强耦合极限的体系。

  核心信息一句话：他们把 U/t（在位库仑排斥与跃迁能的比值）扫过一个完整区间，系统给出不同关联强度下谐波谱、关联动力学的演化图像，并检验了 doublon-holon 三步模型的适用边界。这对我们特别有价值——强场 HHG 文献里"弱关联近似 + 能带图象"与"原子极限图象"长期各说各话，中等关联区（U/W 中等到大）恰恰是实验上最有意思、理论上最不干净的区域。他们给出的框架把 U/W 作为一个有序参数把整个谱系串起来，这正是我想在自己的课题里借鉴的组织方式。

  需要注意：我手头只有摘要级元数据，具体数值（谐波截止规律、各关联区的标度关系）尚未核对原文，后续精读时要重点确认。

  ## 核心要点

  - **研究对象**：Hubbard 梯（ladder）模型中的强场 HHG，多体效应的系统研究。
  - **核心变量**：U/t 比值（关联强度），系统揭示其对谐波谱与关联动力学的影响。
  - **理论框架**：针对中等关联区（U/W 中等）的高次谐波给出完整框架，连接弱关联能带图象与强关联原子极限图象。
  - **机制检验**：考察了 doublon-holon 三步模型（强关联 HHG 的准粒子图象：doublon-holon 对产生、加速、复合发光）在参数空间中的适用性。
  - **来源团队**：Werner / Madsen 组——非平衡强关联数值方法（NEGF 等）的主力团队，方法学上可信度高。

  ## 实验/研究关联

  - 关联体系 HHG 是我们 NSFC-强场超快方向的核心课题之一，本文已被路由到课题 `general-quantum-geometry-inversion-20260726`，可在该课题的立项依据中作为"强关联 HHG 已有系统性理论工作"的支撑文献。
  - 对我们的直接启示：
    - 把 U/W（或 U/t）当作扫描参数组织 HHG 结果，可作为我们分析强关联样品 HHG 数据的参照系；
    - doublon-holon 三步模型的适用边界，可作为我们解释实验谱时判断"准粒子图象是否失效"的依据；
    - 梯子几何（准一维、两条链的耦合）介于链与面之间，对我们将 HHG 推广到准一维材料（如自旋链、 ladder 化合物）有直接借鉴意义。
  - 方法学上，NEGF 类严格数值结果可作为我们代理模型（tight-binding + 平均场）结果的基准校验。

  ## 开放问题

  - 摘要未给出具体标度关系：谐波产率、截止阶次随 U/t 如何变化？需要精读原文提取定量结论。
  - doublon-holon 三步模型在 U/t 的哪个区间开始失效、失效后由什么机制接管？
  - 梯子间链间耦合（rung hopping）对 HHG 的独立影响是否被单独剥离？（摘要只提 U/t。）
  - 与真实材料的对接：哪些实验体系（铜氧 ladder 化合物等）落在他们扫描的 U/W 区间？
  - 该文的框架是否可以直接平移到自旋-轨道耦合或 d-p 模型体系，还是 Hubbard 单带特殊性较强？

  ## 来源
  - 原始材料：2025-PhysRevLett.134.096504-many-body-effects-on-high-harmonic-generation-in-hubbard-lad.md
  - 蒸馏时间：2026-09-27T02:14:50Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：Hubbard 梯子中高次谐波产生的多体效应——U/t 全区间扫描与 doublon-holon 三步模型适用边界（Murakami, Hansen, Takayoshi, Madsen, Werner，PRL 2025）

**原理**：以 Hubbard 梯模型（准一维、两条链耦合，介于链与面之间）为载体，把关联强度 U/t 扫过完整区间，系统给出不同关联强度下谐波谱与关联动力学的演化图像；针对中等关联区（U/W 中等——实验最有意思、理论最不干净的区域）给出完整 HHG 框架，连接弱关联能带图象与强关联原子极限图象；检验 doublon-holon 三步模型（强关联 HHG 准粒子图象：doublon-holon 对产生-加速-复合发光）在参数空间中的适用性；Werner/Madsen 组的非平衡格林函数（NEGF）严格数值方法为方法学背书。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 组织参数 | U/t 比值全区间扫描（弱关联能带图象 ↔ 强关联原子极限的统一谱系） | 核心要点 |
| 发表信息 | Murakami, Hansen, Takayoshi, Madsen, Werner, PRL 134, 096504 (2025) | 林赛的理解 |

**适用边界**：摘要级页面（digest_level=abstract），谐波产率/截止阶次随 U/t 的标度关系未给出（需精读提取）；doublon-holon 三步模型失效区间与接管机制未明；rung 链间耦合对 HHG 的独立影响是否剥离未知；与真实材料（铜氧 ladder 化合物等）的 U/W 区间对接未做；框架向 SOC/d-p 模型体系的可移植性未验证。
**代表作**：Murakami, Hansen, Takayoshi, Madsen, Werner, Many-Body Effects on High-Harmonic Generation in Hubbard Ladders（PRL 134, 096504, 2025）
*方法卡回补 2026-10-03*

<!-- linsai-wikilinks -->
## 关联概念

- [[general-quantum-geometry-inversion-20260726]]
- [[三步模型]]
- [[固体高次谐波]]
- [[强关联体系]]
- [[强场超快]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
