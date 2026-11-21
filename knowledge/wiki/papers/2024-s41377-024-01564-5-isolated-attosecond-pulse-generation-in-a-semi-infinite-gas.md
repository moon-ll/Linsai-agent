---
title: "2024-s41377-024-01564-5-isolated-attosecond-pulse-generation-in-a-semi-infinite-gas"
type: "papers"
created: "2026-09-27T00:11:36Z"
updated: "2026-11-15T15:09:20Z"
tags: []
related: ["FROG", "RABBIT", "RABBITT", "general-quantum-geometry-inversion-20260726", "孤立阿秒脉冲", "强场超快", "相位匹配", "阿秒科学", "高次谐波产生"]
source_raw: "2024-s41377-024-01564-5-isolated-attosecond-pulse-generation-in-a-semi-infinite-gas.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
aliases: ["s41377-024-01564"]
digest_level: "abstract"
---

• ---
  title: "Isolated attosecond pulse generation in a semi-infinite gas cell driven by time-gated phase matching"
  type: papers
  created: "2026-09-27T00:11:19Z"
  updated: "2026-09-27T00:11:19Z"
  tags: ["阿秒科学", "高次谐波", "孤立阿秒脉冲", "相位匹配", "泵浦-探测"]
  related: ["高次谐波产生", "阿秒泵浦-探测", "气体靶设计", "相位匹配调控"]
  source_raw: "2024-s41377-024-01564-5-isolated-attosecond-pulse-generation-in-a-semi-infinite-gas.md"
  growth_stage: "growing"
  confidence: 0.7
  auto_grown: true
  review_status: "pending"
  ---

  # Isolated attosecond pulse generation in a semi-infinite gas cell driven by time-gated phase matching（Vismarra et al., 2024）

  ## 林赛的理解

  这篇论文解决的是我做阿秒泵浦-探测实验时最关心的工程问题之一：孤立阿秒脉冲（IAP）的可靠产出。目前手头这条材料只有一行摘要级信息——在半无限气室（semi-infinite gas cell）中用"时间门控相位匹配"（time-gated phase matching）实现了 180 as 的孤立阿秒脉冲。没有正文、没有数值细节，所以我不会假装知道他们的驱动参数。

  但单就"时间门控相位匹配 + 半无限气室"这个组合，作为实验方案设计问题它是有信息量的：传统上 IAP 的相位匹配窗口本来就窄（电离导致的等离子体色散把匹配窗口压缩到电离饱和前的短暂时刻），"时间门控"这个说法意味着作者不是去追求全时域的匹配，而是显式地接受并利用了相位匹配本身的时间选择性——把有效谐波发射约束在一个时间门内，门内单脉冲、门外抑制。这和 ionization-gated / self-compression 路线在思想上同源，但表述上更强调相位匹配维度而非单纯的电离门控。半无限气室相对自由射流（free jet）的优势在于相互作用长度可控、气体密度分布可设计，我预期他们是用气室的几何/气压梯度来配合时间门控做空间-时间联合的匹配管理。

  180 as 作为结果不算 record 级别（近年来 IAP 已进入 ~50-100 as 区间），但摘要特意强调"适用于阿秒泵浦-探测实验"，说明卖点可能在**稳定性和通量**而非极限脉宽——对做实际泵浦-探测的用户来说，一个能长时间稳定出 180 as 的装置比一个偶尔出 100 as 的装置更有价值。这一点我深有同感。

  ## 核心要点

  - 实现了 180 as 孤立阿秒脉冲（材料仅给出此数值，无脉宽测量方式、无光谱覆盖范围细节）。
  - 采用**时间门控相位匹配**（time-gated phase matching）：利用相位匹配在时域上的选择性窗口，将有效谐波发射约束到单脉冲时间门内。
  - 靶型为**半无限气室**（semi-infinite gas cell），与常见的自由气体射流不同。
  - 定位为面向**阿秒泵浦-探测实验**的实用光源，而非追求极限脉宽纪录。

  ## 实验/研究关联

  - 与我关注的强场超快方向（NSFC-强场超快项目群）直接相关，已被 `general-quantum-geometry-inversion-20260726` 课题引用。
  - 对阿秒泵浦-探测方案的实验设计有直接参考价值：半无限气室的工程稳定性 + 时间门控的 IAP 选择机制，是我们在讨论 HHG 光源方案时值得对照的"另一条路线"。
  - 可与我知识库中"高次谐波产生""相位匹配调控"等概念页互链，作为气体靶几何设计的案例补充。

  ## 开放问题

  - 驱动条件完全未知：少周期脉冲的中心波长、CEP 稳定与否、脉冲能量——这些直接决定方法的可移植性，需读全文。
  - "时间门控"的确切物理机制待确认：是电离门控的相位匹配表述，还是涉及色散工程或双色场辅助？两者对实验复现的要求差别很大。
  - 180 as 的表征手段（RABBITT 还是 FROG-CRAB / d-scan？）、单发稳定性、光通量数据均缺失，无法评估其"适用于泵浦-探测"的实际成色。
  - 半无限气室相对于自由射流在 IAP 产率上的定量对比未给出。
  - 本笔记基于摘要级元数据，所有具体参数待获取全文（has_pdf: false）后核实，confidence 仅给 0.7。

  ## 来源
  - 原始材料：2024-s41377-024-01564-5-isolated-attosecond-pulse-generation-in-a-semi-infinite-gas.md
  - 蒸馏时间：2026-09-27T00:11:19Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：半无限气室时间门控相位匹配的 180 as 孤立阿秒脉冲产生

**原理**：时间门控相位匹配（time-gated phase matching）：利用相位匹配在时域上的选择性窗口把有效谐波发射约束到单脉冲时间门内；靶型为半无限气室（semi-infinite gas cell，区别于常见气体射流）；实现 180 as 孤立阿秒脉冲，定位为面向阿秒泵浦-探测实验的实用光源而非极限脉宽纪录。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 脉宽 | 180 as（孤立脉冲；材料未给测量方式与光谱覆盖细节） | §核心要点 |

**适用边界**：页面为摘要级题录（78 行），驱动参数、气压/气长与门控机制定量描述未给出。
**代表作**：本文（Light: Science & Applications，DOI 10.1038/s41377-024-01564-5）
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[FROG]]
- [[RABBIT]]
- [[RABBITT]]
- [[general-quantum-geometry-inversion-20260726]]
- [[孤立阿秒脉冲]]
- [[强场超快]]
- [[相位匹配]]
- [[阿秒科学]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
