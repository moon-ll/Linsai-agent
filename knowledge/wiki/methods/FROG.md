---
title: "FROG"
type: "methods"
created: "2026-06-17T12:40:33Z"
updated: "2026-11-15T11:22:32Z"
tags: ["表征方法", "阿秒", "频率分辨", "type/method", "topic/HHG", "status/mature"]
related: ["2104.07687", "2312.14174", "2410.10189", "One decade of quantum optimal control in the chopped random basis：CRAB量子最优控制十年综述", "RABBIT", "RABBITT", "bayesian-inference", "孤立阿秒脉冲"]
source_raw: ""
growth_stage: "mature"
confidence: 0.9
aliases: ["FROG-CRAB", "frequency-resolved-optical-gating", "频率分辨光学门控"]
updated_at: "2026-11-15T10:26:47Z"
settled_count: 7
---

<!-- methods-settle:v1 -->

## 原理

FROG 通过测量频率分辨的门控痕迹（非线性混频自相关迹或激光辅助光电子条纹谱）并以 FROG-CRAB/VTG-FROG 类迭代相位检索（广义投影+梯度下降）同时反演脉冲的时间包络与相位，可扩展至软X射线连续谱重建时域形状与啁啾并提取光电发射时延；新证据表明该重构可显式表述为从含噪二维谱图到脉冲场的贝叶斯统计反演而非纯数值优化问题，把测量噪声建模与不确定性量化纳入反演本体，与投影式迭代检索形成互补路径；同名异义的 CRAB 最优控制以少量随机基函数构成变分随机基对控制场降维参数化，使无梯度优化在高维控制空间可行，Group-CRAB 多智能体并行共识搜索增强对噪声、漂移与局部极值的鲁棒性，与 FROG 表征端构成强场脉冲的设计—测量闭环。

## 适用边界

标准 FROG-CRAB 反演依赖中心动量近似与迭代收敛性：通道混合、脉冲啁啾与库仑-激光耦合（CLC）下提取的时延/相位相对真值存在系统性偏差，宽带/快变谱相位重构病态、仅给带宽平均延迟，完整重建还需条纹径迹足够信噪比与充分延时采样；贝叶斯统计反演路径显式建模谱图噪声，但其可靠性取决于噪声模型与先验假设的选取，且采样式推断计算代价高于广义投影迭代；CRAB 最优控制与 FROG-CRAB 仅为缩写撞名，前者的降维优化可行性不可直接外推到后者的病态反演问题。

## 代表作

- arXiv:2310.07079
- arXiv:2312.14174
- arXiv:2410.10189
- arXiv:2407.05937
- arXiv:2403.05073
- arXiv:2104.07687
- arXiv:2205.15574
- Kane & Trebino, IEEE J. Quantum Electron. 29, 571 (1993)

## 证据日志

- 2026-09-18｜r18｜仅简报｜[paper:2023-2312.14174-evaluating-the-accuracy-of-attosecond-streaking-time-delay-m] 条纹谱延迟反演（FROG-CRAB 类相位重建）：本文检验标准反演算法在多通道/啁啾/CLC 存在时提取延迟相对真值的偏差。
- 2026-09-18｜r18｜仅简报｜[paper:2024-2410.10189-complete-temporal-characterization-of-isolating-water-window] 完整相位检索重建（FROG-CRAB / VTG-FROG 类算法）：从条纹径迹同时反演脉冲时间包络与相位，给出完整时间表征而非仅脉宽下限。
- 2026-09-26｜r41｜回原文｜[paper:2024-2407.05937-generation-and-characterization-of-isolated-attosecond-pulse] 条纹迹时域重建（FROG-CRAB/类Volkov反演）：从条纹迹反演软X射线连续谱的时域形状与啁啾，给出脉宽的定量结论。
- 2026-09-27｜r42｜回原文｜[paper:2023-2312.14174-evaluating-the-accuracy-of-attosecond-streaking-time-delay-m] FROG-CRAB相位检索：标准条纹谱反演算法，其在通道混合、啁啾与CLC下的失效边界被定量表征。
- 2026-10-03｜r51｜仅简报｜[paper:2026-2403.05073-rainbow-retrieval-of-atomic-time-delays-in-attosecond-streak] FROG-CRAB相位重构：作为对照基线：迭代重构对宽带/快变相位病态，只能给出带宽平均延迟，凸显rainbow方法优势。
- 2026-10-17｜r75｜仅简报｜[paper:2021-2104.07687-one-decade-of-quantum-optimal-control-in-the-chopped-random] CRAB最优控制算法：截断随机傅里叶基参数化控制场实现降维优化，可直接移植到强场脉冲波形设计问题。
- 2026-10-17｜r75｜仅简报｜[paper:2021-2104.07687-one-decade-of-quantum-optimal-control-in-the-chopped-random] Group-CRAB多智能体协同优化：多优化器并行共识搜索，显著增强对噪声、漂移和局部极值的鲁棒性。
- 2026-10-17｜r76｜仅简报｜[paper:2022-2205.15574-quantum-optimal-control-practical-aspects-and-diverse-method] CRAB 变分随机基：用少量随机基函数参数化控制场实现降维，使无梯度优化在高维控制空间仍可行。
- 2026-11-15｜r139｜仅简报｜[paper:2023-2310.07079-frog-retrieval-via-bayesian-inference] FROG（频率分辨光学门）：把脉冲表征显式表述为从含噪二维谱图到脉冲场的统计反演问题，而非纯数值优化问题。

<!-- /methods-settle:v1 -->

# FROG（FROG-CRAB）

## 林赛的理解

FROG-CRAB（Complete Reconstruction of Attosecond Burst）是把传统 FROG 技术推广到阿秒脉冲表征的方法。用孤立阿秒脉冲 + IR 场，扫描延时记录光电子谱，通过相位反演重建阿秒脉冲的时间结构。

## 核心要点

- 与 RABBITT 互补：FROG-CRAB 用孤立脉冲，RABBITT 用脉冲串
- 反演算法：PCGPA（Principal Component Generalized Projections Algorithm）
- 两者在相同条件下结果一致（arXiv: 0707.4228）

## 来源

- arXiv: 0707.4228

<!-- linsai-wikilinks -->
## 关联概念

- [[2104.07687]]
- [[2312.14174]]
- [[2410.10189]]
- [[One decade of quantum optimal control in the chopped random basis：CRAB量子最优控制十年综述]]
- [[RABBIT]]
- [[RABBITT]]
- [[bayesian-inference]]
- [[孤立阿秒脉冲]]
<!-- /linsai-wikilinks -->
