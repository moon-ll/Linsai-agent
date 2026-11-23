---
title: "2024-2407_07447-spin-splitting-in-altermagnetic-ruo2-enables-field-free-spin"
type: "papers"
created: "2026-08-29T09:55:08Z"
updated: "2026-11-15T15:09:20Z"
tags: []
related: ["PLAN", "强场超快", "强场超快光学", "自旋劈裂"]
source_raw: "2024-2407.07447-spin-splitting-in-altermagnetic-ruo2-enables-field-free-spin.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "abstract"
---

• ---
  title: "Spin Splitting in Altermagnetic RuO2 Enables Field-free Spin-Orbit Torque Switching via Dominant Out-of-Plane Spin Polarization"
  type: papers
  created: "2026-08-29T09:53:52Z"
  updated: "2026-08-29T09:53:52Z"
  tags: ["altermagnetism", "RuO2", "spin-orbit torque", "spin splitting", "field-free switching", "Néel vector", "HHG", "magnetic order readout"]
  related: ["altermagnetism", "spin-orbit torque", "HHG magnetic order readout", "Néel vector control"]
  source_raw: "2024-2407.07447-spin-splitting-in-altermagnetic-ruo2-enables-field-free-spin.md"
  growth_stage: "growing"
  confidence: 0.7
  auto_grown: true
  review_status: "pending"
  ---

  # Spin Splitting in Altermagnetic RuO2 Enables Field-free Spin-Orbit Torque Switching via Dominant Out-of-Plane Spin Polarization

  ## 林赛的理解
  作为强场超快光学 PI，我关注的是如何把这类静态自旋劈裂实验转化为超快光学读出。RuO2(101) 中反铁磁自旋劈裂效应（ASSE）产生面外 z 极化自旋并驱动无外场翻转，这意味着 Néel 矢的取向直接决定自旋极化方向。如果这一各向异性在飞秒尺度上保留，那么 HHG 的偏振/相位响应将携带 Néel 矢的指纹，为我们的 altermagnet HHG 磁有序读出方案提供具体的晶体取向与极化配置参考。

  ## 核心要点
  - **核心发现**：在反铁磁 RuO2(101) 中，ASSE 是产生自旋电流的主要机制；面外 z 方向自旋极化占主导，并产生反阻尼力矩，实现无外场下的确定性磁化翻转。
  - **方法亮点**：利用 Néel 矢方向对自旋极化的各向异性调控，把反铁磁序与电流驱动翻转关联起来；实验配置（RuO2(101) 取向、面外自旋极化）可直接迁移到超快光学探测设计。
  - **与现有工作的差异**：相比需要外场或铁磁层的传统 SOT 方案，这里利用 altermagnet 本征自旋劈裂即可实现无场翻转。

  ## 实验/研究关联
  - 该工作提示了 **altermagnet HHG 磁有序读出** 的实验坐标系：RuO2(101) 面、面外 z 极化、Néel 矢作为可调旋钮。
  - 若将飞秒脉冲与电流脉冲同步，或可观测自旋取向翻转前后的 HHG 信号变化，验证超快时间尺度上 ASSE 的各向异性是否保持。
  - 我们 "general-order-parameter-ultrafast-readout" 课题可以引用该文作为 RuO2 平台上序参量超快读出的实验依据之一。

  ## 开放问题
  - 原始材料仅为摘要级描述，缺乏具体实验条件（薄膜厚度、温度、电流密度、测量几何），需阅读原文后才能评估可重复性与可迁移性。
  - ASSE 在飞秒泵浦后的弛豫时间未知：Néel 矢的热涨落是否会抹平自旋极化的各向异性？
  - 面外 z 极化自旋在 HHG 中对应何种偏振选择定则？需要结合能带计算与对称性分析才能给出定量预测。
  - 无外场翻转的确定性是否依赖于畴结构？单畴与多畴样品的 HHG 响应可能不同，这是实验设计时必须区分的因素。

  ## 来源
  - 原始材料：2024-2407.07447-spin-splitting-in-altermagnetic-ruo2-enables-field-free-spin.md
  - 蒸馏时间：2026-08-29T09:53:52Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：交变磁 RuO₂(101) 中 ASSE 主导的面外自旋极化实现无外场自旋轨道力矩确定性翻转——Néel 矢量作为可调旋钮

**原理**：RuO₂(101) 中反铁磁自旋劈裂效应（ASSE，altermagnetic spin splitting effect）是产生自旋电流的主要机制：面外 z 方向自旋极化占主导并产生反阻尼力矩，实现无外场下的确定性磁化翻转；利用 Néel 矢方向对自旋极化的各向异性调控，把反铁磁序与电流驱动翻转关联——相比需要外场或铁磁层的传统 SOT 方案，altermagnet 本征自旋劈裂即可实现无场翻转；实验配置（RuO₂(101) 取向、面外自旋极化、Néel 矢可调旋钮）可直接迁移到超快光学探测设计。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 核心机制 | RuO₂(101)：ASSE 主导自旋电流；面外 z 自旋极化占主导 → 反阻尼力矩 → 无外场确定性翻转 | 核心要点 |

**适用边界**：摘要级描述缺具体实验条件（薄膜厚度/温度/电流密度/测量几何）——可重复性与可迁移性待原文评估；ASSE 在飞秒泵浦后的弛豫时间未知（Néel 矢热涨落是否抹平自旋极化各向异性）；面外 z 极化自旋在 HHG 中对应的偏振选择定则需结合能带计算与对称性分析给出定量预测；无外场翻转的确定性是否依赖畴结构（单畴 vs 多畴 HHG 响应可能不同）为实验设计必分因素。
**代表作**：Spin Splitting in Altermagnetic RuO₂ Enables Field-free Spin-Orbit Torque Switching via Dominant Out-of-Plane Spin Polarization（arXiv:2407.07447，2024）
*方法卡回补 2026-10-04*

<!-- linsai-wikilinks -->
## 关联概念

- [[PLAN]]
- [[强场超快]]
- [[强场超快光学]]
- [[自旋劈裂]]
<!-- /linsai-wikilinks -->
