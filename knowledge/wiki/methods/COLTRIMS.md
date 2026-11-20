---
title: "COLTRIMS"
type: "methods"
created: "2026-06-17T12:40:33Z"
updated: "2026-11-15T15:09:19Z"
tags: ["表征方法", "动量谱", "冷靶反冲", "type/method", "topic/HHG", "status/mature", "status/growing"]
related: ["1005.1253", "2010-1005_1253-electronic-correlations-in-double-ionization-of-atoms-in-pum", "2610.16077", "VMI", "arXivID", "strong-field-ionization"]
source_raw: ""
growth_stage: "mature"
confidence: 0.75
aliases: ["cold-target-recoil-ion-momentum-spectroscopy", "冷靶反冲动量谱"]
updated_at: "2026-10-31T10:25:06Z"
settled_count: 3
---

<!-- methods-settle:v1 -->

## 原理

COLTRIMS（反应显微镜/冷靶反冲离子动量谱）以冷靶与飞行时间-位置灵敏探测器对电离产生的全部带电粒子做多体符合测量，逐事件重建各碎片三维动量：既可经动量匹配/库仑爆炸反演电离瞬间的核构型（如 D2O 强场三重电离全碎片动量成像），也可通过双电子符合动量成像获得电子对动量关联谱、区分序列与非序列双电离，还可对离子-电子（如氦）做符合测量重构极化面内完整动量矢量分布，为发射角统计提供实验基础。

## 参数表

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| BSV | 1600 nm；最高 10 µJ；四档强度 0.53/0.80/1.33/1.60×10¹⁴ W/cm² | §实验体系/BSV表征 
| 相干态驱动场 | 800 nm 线偏振 | [[2610.16077]] |
| BSV 场 | 1600 nm、零均值、作量子微扰 | [[2610.16077]] |
| BSV 宏观场近似成立条件 | 10¹² 量级、10 fs 脉冲 | [[2610.16077]] |
| 高增益 SPDC 阈值 | 约 10⁴ 光子/模 | [[2610.16077]] |
| g⁽²⁾ 测量比值 | 1.049–1.066 | [[2610.16077]] |
| 计数统计线性移动幅度 | 约 5% 阈值 | [[2610.16077]] |
| 相干光 | 1580 nm/70 fs/10 kHz/10¹³ W/cm²（TOPAS-Prime） | §光源与原子靶 
| BSV | 1580 nm/~150 fs/1400–1800 nm；双 3 mm BBO Type-I/间距 80 cm；椭圆偏振 0.7 | §光源与原子靶 
| 靶/探测 | Na 蒸气 170 °C/I_p=5.14 eV；COLTRIMS 7 V/cm+11 G；符合窗 0.2 a.u.；隧穿 ~0.01%/脉冲 | §测量装置 
<!-- src:2026-2604_06703-strong-field-ionization-of-atoms-with-bright-squeezed- -->
<!-- src:2610.16077 -->
<!-- src:2026-2604_05783-nonlinear-atomic-tunnelling-boosted-by-bright-squeezed -->

## 适用边界

依赖带电碎片与电子的近全收集及多体符合探测效率，核构型反演隐含瞬时电离/库仑爆炸近似；多重电离多粒子（含电子对、离子-电子对）符合事例率低、统计成本高，动量分辨率受引出场设置与靶温限制，极化面内动量矢量重构要求探测器几何与场配置覆盖相应立体角。

## 代表作

- 2008-0808.04690-attosecond-angular-streaking-eckle-et-al
- 2026-260527612-electron-spectra-from-strong-field-enhanced-i
- 2026-2610.26901-symmetry-and-quantum-interference-in-the-attosecon

## 证据日志

- 2026-09-19｜r25｜仅简报｜[paper:2026-260527612-electron-spectra-from-strong-field-enhanced-i] 全片段动量成像（反应显微镜/COLTRIMS 型符合测量）：以多体符合方式重建 D2O 三重电离各碎片三维动量，确定碎裂通道与电离时的核构型。
- 2026-10-24｜r92｜仅简报｜[paper:2026-2610.26901-symmetry-and-quantum-interference-in-the-attosecon] 双电子符合动量成像（COLTRIMS/反应显微镜类技术）：提供电子对动量关联谱，区分序列与非序列双电离并直接揭示电子-电子关联机制。
- 2026-10-31｜r105｜仅简报｜[paper:2008-0808.04690-attosecond-angular-streaking-eckle-et-al] COLTRIMS 反应显微镜（冷靶反冲离子动量谱）：对氦离子与电子做符合测量，重构极化面内完整动量矢量分布，为发射角统计提供实验基础。

<!-- /methods-settle:v1 -->

# COLTRIMS

## 林赛的理解

COLTRIMS（冷靶反冲动量谱）是"反应显微镜"——同时测量电离产生的电子和离子，三维重建全部动量。对原子分子强场过程，它能提供最完整的事件级信息。

## 核心要点

- 冷靶（supersonic jet）+ 均匀电场磁场 → 电子和离子都被引导到位置敏感探测器
- 多重符合 → 重建每个电离事件的完整动量
- 用于：双电离、库仑爆炸、分子断裂动力学

## 来源

- arXiv: 1005.1253（双电离关联）；`hhg-methods-report.md`

<!-- linsai-wikilinks -->
## 关联概念

- [[1005.1253]]
- [[2010-1005_1253-electronic-correlations-in-double-ionization-of-atoms-in-pum]]
- [[2610.16077]]
- [[VMI]]
- [[arXivID]]
- [[strong-field-ionization]]
<!-- /linsai-wikilinks -->
