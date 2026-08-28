---
title: "Realizing giant valley polarization effect based on monolayer altermagnets"
type: "papers"
created: "2026-08-28T12:50:56Z"
updated: "2026-08-28T12:50:56Z"
tags: ["altermagnet", "valley-polarization", "first-principles", "valleytronics", "monolayer", "2D-magnetism"]
related: ["Berry curvature", "MNPS3", "Rashba effect", "ultrafast spin-valley dynamics", "valley-selective optical excitation"]
source_raw: "2026-2603.19619-realizing-giant-valley-polarization-effect-based-on-monolaye.md"
growth_stage: "growing"
confidence: 0.7
auto_grown: true
review_status: "pending"
---

# Realizing giant valley polarization effect based on monolayer altermagnets

## 林赛的理解

这篇文章的题目很吸引人——单层 altermagnet 中实现"巨自发能谷极化"。从我的角度看，这篇工作的核心价值不在于又一个 valley material 的发现，而在于把 **altermagnetism** 这一 2022 年以后才被正式命名的磁性序，与 **valleytronics** 这条已经比较成熟的研究线做了一个理论上的嫁接。如果预言成立，这等于打开了一类全新的"自旋-能谷"耦合平台——不同于传统 TMDs 靠打破反演对称性 + SOC 产生 valley splitting 的路径，altermagnet 本身就具备 **d 波/p 波自旋劈裂对称性**，结合其 broken time-reversal symmetry（虽然 net magnetization 为零），天然可能在能带中嵌入 valley-resolved 的拓扑结构。

我们组一直在 Berry curvature / Rashba 相关体系上布局（general-berry-mnps3-rashba-20260816 proposal），这篇文章的逻辑让我立刻想到：**能否用强场超快手段（few-cycle mid-IR, circularly polarized pump）去 pump-probe 这种 altermagnet 的 valley population，并读出 valley polarization 的超快动力学？** 这是一个可能比 MnPS3 更有意思的体系——因为 altermagnet 的 spin-split 是动量依赖的（不是简单的 Zeeman-like），所以 valley-resolved optical selection rules 应该会展现出独特的 circular dichroism 特征。

## 核心要点

1. **材料体系**：单层 altermagnet（具体材料未在摘要中给出，需要读全文确认），通过第一性原理 DFT 计算预言。
2. **关键现象**：**giant spontaneous valley polarization**——"spontaneous" 这一点很关键，意味着不需要外加磁场、不需要 circularly polarized light pumping，是基态本身就有的 valley imbalance。这与 TMDs（如 MoS₂）需要打破 time-reversal symmetry（磁性掺杂、外场）才能获得 valley polarization 的传统方案形成对比。
3. **物理机制**：altermagnet 的 d-wave/p-wave 自旋劈裂对称性（spin-momentum locking without net magnetization）与能谷处的 Berry curvature 分布产生耦合，导致某一 valley 在能量上显著低于另一 valley。
4. **"giant"的含义**：推测 valley splitting 量级远超传统 SOC-induced valley splitting（通常几 meV 到几十 meV），可能达到几十到上百 meV 量级——这对室温 valleytronic device 是关键的。
5. **扩展性**：作为 valleytronics 材料方案的拓展，提示 altermagnet 是一类具有 valley 物理的母体材料库。

## 实验/研究关联

与林赛工作的潜在交叉点：

- **强场超快 pump-probe 表征**：如果我们能用 few-cycle circularly polarized mid-IR pump + time-resolved ARPES / Kerr microscopy 去追踪这种体系的 valley population dynamics，将能直接验证"spontaneous valley polarization"的理论预言，并探测 valley depolarization 的超快时间尺度（预期在 fs–ps 区间）。
- **Berry curvature 探测**：与 MNPS3 / Rashba 体系中的 Berry curvature measurement 思路打通——可能利用 high-harmonic generation (HHG) 作为 Berry curvature 的全光探针（HHG 的 circular dichroism 对 Berry curvature 敏感，已有文献支撑）。
- **自旋-能谷耦合的超快操控**：altermagnet 的 spin-split 是晶格对称性保护的，那么在强光场下能否 transiently 打破对称性来翻转 valley polarization？这与 Floquet engineering 在 TMDs 中的应用有方法论上的类比。
- **样品制备**：单层 altermagnet 的实验制备可能比 MnPS3 更具挑战性——需要与材料生长组（MBE / 机械剥离）建立合作，或者寻找已经在实验中可获得的相关体系。

## 开放问题

1. **"Giant" 的具体量级和材料**：全文必须读，确认是哪一种/几种 altermagnet，valley splitting 具体多少 meV，DFT 用的什么泛函（PBE? HSE06? SCAN+U?）。Altermagnet 的 DFT 预测对交换关联泛函非常敏感，需要仔细评估。
2. **实验可及性**：哪种单层 altermagnet 已经在实验上合成出来？如果没有，预言的可验证性如何？候选体系如 RuO₂、MnTe 等已经有 bulk altermagnet 证据，但单层稳定性如何？
3. **温度稳定性**：自发 valley polarization 是否能在室温下保持？这对实际应用至关重要。
4. **超快动力学**：valley polarization 的形成/退极化时间尺度是 fs 还是 ps？这直接影响能否用我们现有的 pump-probe 平台（~10 fs resolution）去追踪。
5. **与现有 valleytronics 材料的对比**：相比 CrI₃ / CrBr₃ 这类 ferromagnetic 2D material 的 valley splitting，这个工作的优势在哪里？altermagnet 的 zero net magnetization 是否反而是优点（无 stray field）？
6. **强场下的非线性响应**：在 strong-field regime（>10¹² V/m），altermagnet + valley polarization 的体系是否会产生 novel HHG 或 high-order sideband 信号？这可能是我们组可以理论先行的方向。

## 来源
- 原始材料：2026-2603.19619-realizing-giant-valley-polarization-effect-based-on-monolaye.md
- 蒸馏时间：2026-08-28T12:50:56Z
- arXiv ID: 2603.19619
- 相关提案：general-berry-mnps3-rashba-20260816
- 关联项目：NSFC-强场超快

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry curvature]]
- [[MNPS3]]
- [[Rashba effect]]
- [[ultrafast spin-valley dynamics]]
- [[valley-selective optical excitation]]
<!-- /linsai-wikilinks -->
