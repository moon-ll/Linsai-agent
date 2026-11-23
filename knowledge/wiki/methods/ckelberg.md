---
title: "Landau-Zener-Stückelberg-Majorana (LZSM) 干涉"
type: "methods"
created: "2026-10-24T21:32:09Z"
updated: "2026-11-08T05:06:52Z"
tags: ["方法学", "#type/method"]
related: ["2024-2404.08466-a-different-perspective-on-the-landau-zener-dynamics", "2404.08466", "arXivID"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-24T21:32:09Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

LZSM 干涉指系统被周期驱动多次穿越能隙（免交叉）点时，相继 Landau-Zener 隧穿路径间发生干涉并形成干涉谱；绕狄拉克点演化积累的 π 马约拉纳相位可解释动量分布的相干位移与畸变，但在 Andreev 体系中因非幺正演化与退相干，标准干涉分析须经系统修正后方可用于解读谱线。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 马约拉纳相位（绕狄拉克点） | π rad | paper:2026-2602.12844-subcycle-videography-of-lightwave-driven-landau-zener-majora |

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 原子与驱动 | ω_eg=0.057 a.u.（类 Rb，λ≈800 nm）；经典场 Ω_L=0.2ω_eg≈0.0117 a.u.；高斯包络 τ₀=100 fs | 研究方法 
| 量子模耦合 | 真空 Rabi 耦合 Ω₃=0.0041√ω_L、Ω₅=0.0031√ω_L；ω_L=ω_eg/5 时 Ω₃≈0.0098ω_eg、Ω₅≈0.0059ω_eg | 研究方法 
| 共振波长 | 诱导多光子共振 λ_L≈2190 nm（自由场三光子共振 2400 nm）；激发概率随波长呈 Stückelberg 振荡（脉冲沿两次共振干涉） | 主要发现 
| 纠缠判据 | R₃₅=⟨a†₃a†₅a₅a₃⟩²/(⟨a†²₃a²₃⟩⟨a†²₅a²₅⟩)，五光子共振附近 R₃₅>1；S_Q 在 R₃₅<1 区域仍非零——R<1 不代表无纠缠；R 随驱动场强增大而减小 | 主要发现 
| LZ 概率振幅 | exp(−πε/2)；终值 a(τ→∞) = exp(−π/(2ε)) 决定跃迁后圆心半径 | 研究背景/主要发现与核心结论 
| 线性化忽略项 | φ̈_h²(τ) = 4ε²τ²𝒮²cos²(β−ετ²)——secular 增长，非线性经 cos² 倍频产生线性方程与 Markov rate function 中不存在的高次谐波 | 主要发现与核心结论 
<!-- src:2026-2609_06480-quantum-optics-of-harmonic-generation-in-the-strongly- -->
<!-- src:2404.08466 -->

## 适用边界

标准 LZSM 干涉分析隐含幺正、相干演化假设；在 Andreev 等开放体系中非幺正演化与退相干使干涉图样偏离标准模型，需系统修正后才能可靠解读 LZSM 干涉谱。

## 代表作

- paper:2026-2607.09859-landau-zener-tunneling-and-quantum-interference-of-andreev-s
- paper:2026-2602.12844-subcycle-videography-of-lightwave-driven-landau-zener-majora

## 证据日志

- 2026-10-24｜r94｜仅简报｜[paper:2026-2607.09859-landau-zener-tunneling-and-quantum-interference-of-andreev-s] Landau-Zener-Stückelberg-Majorana (LZSM) 干涉：本文揭示在Andreev体系中相继LZ穿越的干涉因非幺正演化和退相干需系统修正，为解读LZSM干涉谱提供适用边界。
- 2026-10-24｜r94｜仅简报｜[paper:2026-2602.12844-subcycle-videography-of-lightwave-driven-landau-zener-majora] Landau-Zener-Stückelberg-Majorana干涉分析：以绕狄拉克点获得的 π 马约拉纳相位解释相继隧穿路径干涉造成的动量分布相干位移与畸变。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2024-2404.08466-a-different-perspective-on-the-landau-zener-dynamics]]
- [[2404.08466]]
- [[arXivID]]
<!-- /linsai-wikilinks -->
