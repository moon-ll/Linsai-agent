---
title: "Universal Convergence Metric for Time-Resolved Neutron Scattering"
type: "papers"
created: "2026-11-21T11:14:02Z"
updated: "2026-11-21T11:18:41Z"
tags: ["papers", "时间分辨中子散射", "高斯过程回归", "实验设计优化"]
related: ["1T-TiSe2-CDW-项目", "低通量中子源", "强场超快", "强场超快光学", "时间分辨探测", "泵浦探测"]
source_raw: "2025-2505.13512-universal-convergence-metric-for-time-resolved-neutron-scatt.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Universal Convergence Metric for Time-Resolved Neutron Scattering

## 林赛的理解
这篇来自 SNS EQSANS 合作组的工作提出用高斯过程回归（GPR）构建时间分辨小角中子散射的普适收敛指标。作为做超快光学的人，我关注的核心问题是测量信噪比与时间的权衡——这在泵浦探测实验中就是积累时间与漂移的权衡。他们发现剖面演化存在普适幂律标度，意味着可以从早期数据外推预测最佳测量时长，这对低通量紧凑加速器中子源上的时间分辨实验特别有价值。这种"用统计模型提前判断实验何时收敛"的思路，对我们规划低重复频率下的超快测量同样有借鉴意义。

## 核心要点
- 提出基于高斯过程回归的时间分辨 SANS 普适收敛指标。
- 揭示散射剖面演化的普适幂律标度。
- 可用早期数据预测最佳测量时长，优化时间分配。
- 对低通量紧凑加速器中子源的时间分辨实验优化尤为重要。

## 实验/研究关联
- 已被纳入 1T-TiSe₂ CDW 相关提案（general-t-tise2-2-2-2-cdw-20261108）的文献池，可能作为时间分辨中子/散射实验设计的方法学参考。
- 该方法论（收敛性预判、测量时长优化）可类比迁移到强场超快光学中的弱信号时间分辨测量规划。

## 开放问题
- "普适"幂律标度的适用范围：是否限于特定散射剖面类型或动力学类别？
- GPR 模型对非平稳、多时间尺度演化（如 CDW 中的多相竞争）是否稳健？
- 能否推广到其他低计数探测手段（如弱信号超快电子/中子衍射）？

## 来源
- 原始材料：2025-2505.13512-universal-convergence-metric-for-time-resolved-neutron-scatt.md
- 蒸馏时间：2026-11-21T11:14:02Z

<!-- linsai-wikilinks -->
## 关联概念

- [[1T-TiSe2-CDW-项目]]
- [[低通量中子源]]
- [[强场超快]]
- [[强场超快光学]]
- [[时间分辨探测]]
- [[泵浦探测]]
<!-- /linsai-wikilinks -->
