---
title: "强场近似（SFA，含 Lewenstein 模型）"
type: "methods"
created: "2026-11-15T16:10:50Z"
updated: "2026-11-16T05:30:14Z"
tags: ["方法学", "#type/method"]
related: ["Lewenstein模型", "TDSE", "三步模型", "固体HHG", "固体HHG机制", "截止定律", "高次谐波产生"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.7
settled_count: 0
---

# 强场近似 SFA（含 Lewenstein 模型）

<!-- methods-settle:v1 -->

## 原理

强场近似（Strong-Field Approximation, SFA）是单活电子图像下的解析 HHG 理论：① 忽略库仑势对已电离电子的影响（连续态用 Volkov 态描述，只受激光场作用）；② 基态仅通过电离振幅与复合偶极耦合，动态忽略激发态布居。Lewenstein 模型是 SFA 的标准定量实现：偶极加速度写作"电离振幅 × 量子轨道传播相量 × 复合偶极"的积分，对传播相位作驻相近似后得到分立量子轨道（短轨道/长轨道），每条轨道有确定的发生时刻与相位——这是 HHG 阿秒啁啾（attochirp）与轨道干涉分析的解析基础。

## 参数表

| 要素 | 数值/公式 | 出处 |
| --- | --- | --- |
| Volkov 态 | 连续态电子在平面波场中的严格解，含 A²(t) 项（速度规范自然分离） | [1] |
| 偶极相位 | 复合偶极带 α ∝ I_p/E 的强度依赖相位，驱动阿秒啁啾 | [2] |
| 驻相条件 | ∂S(t_r,t_i)/∂t = 0 给出分立（t_i, t_r）量子轨道；S 为赝动能+电离能作用量 | [2] |
| 截止定律 | E_cut = I_p + 3.17 U_p（SFA 经典轨道回碰最大值） | [1][2] |
| U_p 公式 | U_p [eV] = 9.337×10⁻¹⁴ × I[W/cm²] × λ²[μm²] | [1] |
| 轨道干涉 | 长短轨道相位差 → 谱干涉调制（plateau 调制周期随场强变化） | [2] |

- [1] P. B. Corkum, Phys. Rev. Lett. 71, 1994 (1993). https://doi.org/10.1103/PhysRevLett.71.1994
- [2] M. Lewenstein et al., Phys. Rev. A 49, 2117 (1994). https://doi.org/10.1103/PhysRevA.49.2117

## 适用边界

SFA 忽略库仑长程作用：截止偏低估（库仑修正 +~1.3U_p 量级观测）、再散射电子波包展宽低估；速度规范下规范不变性需谨慎处理（倍频系数争议史）；多电子极化与隧道出口位置修正超出框架；固体中晶格势不可忽略，须换用 SBE/TDSE 数值演化（[[TDSE]]、[[固体HHG机制]]）。SFA 的价值在解析轨道图像与标度律，不在于绝对产额精度。

## 代表作

- Lewenstein et al., PRA 49, 2117 (1994)（SFA 定量框架原始文献）
- Corkum, PRL 71, 1994 (1993)（半经典三步图像）
- 库内应用：`knowledge/wiki/papers/2404.10293.md`（涡旋 HHG 幂次标度与轨道图像）

<!-- linsai-wikilinks -->
## 关联概念

- [[Lewenstein模型]]
- [[TDSE]]
- [[三步模型]]
- [[固体HHG]]
- [[固体HHG机制]]
- [[截止定律]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
