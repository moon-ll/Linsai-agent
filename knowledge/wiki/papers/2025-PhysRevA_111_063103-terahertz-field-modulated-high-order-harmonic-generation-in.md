---
title: "2025-PhysRevA_111_063103-terahertz-field-modulated-high-order-harmonic-generation-in"
type: "papers"
created: "2026-09-26T11:16:28Z"
updated: "2026-11-15T15:09:21Z"
tags: []
related: ["general-mos2-20260905", "固体HHG", "固体高次谐波", "强场超快", "强场超快光学"]
source_raw: "2025-PhysRevA.111.063103-terahertz-field-modulated-high-order-harmonic-generation-in.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
digest_level: "abstract"
---

• ---
  title: "Terahertz-field-modulated high-order harmonic generation in monolayer MoS2"
  type: papers
  created: "2026-09-26T11:16:00Z"
  updated: "2026-09-26T11:16:00Z"
  tags: ["HHG", "太赫兹场调控", "单层MoS2", "固体高次谐波", "二维材料", "超快光谱"]
  related: ["固体高次谐波", "二维过渡金属硫族化合物", "亚周期干涉", "偶极相位", "超宽带太赫兹时域光谱"]
  source_raw: "2025-PhysRevA.111.063103-terahertz-field-modulated-high-order-harmonic-generation-in.md"
  growth_stage: "growing"
  confidence: 0.7
  auto_grown: true
  review_status: "pending"
  ---

  # Terahertz-field-modulated high-order harmonic generation in monolayer MoS2

  ## 林赛的理解
  我关注这篇文章的理由很直接：它把太赫兹（THz）场从"被探测对象"变成了"调控旋钮"，施加在单层 MoS2 的 HHG 过程上。我们组做固体强场超快光学，一直关心外场如何重塑电子的动力学轨迹——这篇工作给出的图景是：THz 场通过改变电子的偶极相位、扰动其传播轨迹，从而同时调控奇次与偶次谐波的产率及其比值。半经典轨迹分析加数值模拟的组合也是我惯用的方法论，读它时我主要想看两件事：一是亚周期干涉模型在这里如何具体落地，二是奇偶次谐波比值作为可观测量的灵敏度能否支撑他们宣称的"超宽带、超灵敏 THz 时域光谱方案"。

  ## 核心要点
  - **THz 场调控单层 MoS2 的 HHG**：外加太赫兹场可调节奇次与偶次谐波的产率及其比值，为谐波产率提供了一个原位、可调的外场旋钮。
  - **机制图像**：THz 场引入附加偶极相位（dipole phase），改变电子的半经典轨迹；这一相位调制进而影响亚周期干涉（subcycle interference）结构，反映在谐波谱上。
  - **方法组合**：数值模拟 + 半经典轨迹分析，用轨迹层面的因果链解释谱层面的观测信号。
  - **应用指向**：以 HHG 响应作为读出手段，提出超宽带、超灵敏的 THz 时域光谱方案。

  ## 实验/研究关联
  - 与我们"强场超快"方向的直接关联点：该文与 [general-mos2-20260905] 课题使用同一材料体系（单层 MoS2），可作为该课题中"外场调控 HHG"支线的文献支撑。
  - 方法论上可借鉴：把奇偶次谐波**比值**作为对 THz 场敏感的观测量，比单独看绝对产率更能抑制实验涨落——这一点对我们设计超快泵浦-探测读出方案有参考价值。
  - 亚周期干涉 + 偶极相位的分析框架，与我们处理固体 HHG 中"多轨迹贡献干涉"的思路同源，可用于对标我们现有课题中的机制解释口径。

  ## 开放问题
  - 摘要级材料未给出具体产率变化幅度、调控效率等定量结果；THz 场强与谐波比值之间的标定关系（线性区/饱和区）需要读正文核实，不能在此预设。
  - 奇偶次谐波在单层 MoS2（非中心对称体系，本征允许偶次谐波）中的权重如何随 THz 相位/偏振变化，是本工作的关键卖点，具体扫描参数待查原文。
  - "超宽带超灵敏 THz 时域光谱"的实际指标（带宽、探测极限、所需积分时间）在元数据中缺失，应用宣称的可行性需在精读时检验。
  - 本材料无摘要、无 PDF，confidence 维持 0.7；待获取全文后升级为精读并补全定量数据。

  ## 来源
  - 原始材料：2025-PhysRevA.111.063103-terahertz-field-modulated-high-order-harmonic-generation-in.md
  - 蒸馏时间：2026-09-26T11:16:00Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：THz 场调制 MoS₂ HHG（附加偶极相位 + 亚周期干涉，摘要级）

**原理**：外加 THz 场调节单层 MoS₂ HHG 奇次/偶次谐波产率及比值：THz 场引入附加偶极相位改变电子半经典轨迹 → 影响亚周期干涉结构反映在谐波谱；数值模拟+半经典轨迹分析因果链解释谱观测——以 HHG 为读出手段的超宽带 THz 时域光谱方案。

**适用边界**：页面为摘要级题录（63 行，无研究方法节），模拟参数/THz 场强未给出；不虚构参数。
**代表作**：本文（Phys. Rev. A 111, 063103 (2025)）
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[general-mos2-20260905]]
- [[固体HHG]]
- [[固体高次谐波]]
- [[强场超快]]
- [[强场超快光学]]
<!-- /linsai-wikilinks -->
