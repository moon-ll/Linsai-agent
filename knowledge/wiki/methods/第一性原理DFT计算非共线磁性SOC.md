---
title: "第一性原理DFT计算（非共线磁性+SOC）"
type: "methods"
created: "2026-09-19T07:00:47Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "type/method"]
related: ["2025-2501_16741-quantum-geometric-origin-of-strain-tunable-giant-second-harm", "2501.16741", "CrSb", "DFT计算", "自旋劈裂", "量子几何", "非线性光学"]
source_raw: ""
growth_stage: "mature"
confidence: 0.6
updated_at: "2026-09-27T02:13:42Z"
settled_count: 2
---

<!-- methods-settle:v1 -->

## 原理

基于密度泛函理论并显式开启非共线磁序与自旋-轨道耦合（SOC）进行结构弛豫与电子结构计算：对反平行堆叠磁性vdW多层可系统证明滑移/莫尔铁电与交变磁性共存的普适性并提取自旋劈裂与电极化数值估计，可通过能量与电子结构双重判据验证NiBr2/MnBr2交变磁-铁电多铁基态，也能给出pristine与缺陷/掺杂CrSb中自旋劈裂能带及磁性点群变化的基态图像；含强SOC的能带（如应变下非中心对称Bi2O2X的带边SOC劈裂）可作为量子几何与非线性光学（SHG等）响应计算的输入。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 平面波截断能 | 600 eV | paper:2025-2501.16741-quantum-geometric-origin-of-strain-tunable-giant-second-harm |
| 布里渊区采样k点网格（Monkhorst-Pack） | 13×13×4 | paper:2025-2501.16741-quantum-geometric-origin-of-strain-tunable-giant-second-harm |
| 结构弛豫力收敛判据 | 残余离子力 < 10⁻³ eV/Å | paper:2025-2501.16741-quantum-geometric-origin-of-strain-tunable-giant-second-harm |
| 交换关联泛函（带隙经MBJ修正） | GGA-PBE + modified Becke-Johnson | paper:2025-2501.16741-quantum-geometric-origin-of-strain-tunable-giant-second-harm |
| Bi2O2X应变示例（诱导层间位移极化） | 6% 双轴应变 | paper:2025-2501.16741-quantum-geometric-origin-of-strain-tunable-giant-second-harm |
| 应变驱动Bi2O2X的SHG磁化率χ(2)量级 | ~1 nm/V | paper:2025-2501.16741-quantum-geometric-origin-of-strain-tunable-giant-second-harm |

## 适用边界

适用于低维层状体系（磁性vdW多层及非中心对称极性半导体）在非共线磁性+SOC下的基态能量、能带、自旋劈裂与极化计算，并可作为量子几何/非线性光学响应计算的能带输入；结果依赖泛函选择（PBE带隙偏小需MBJ修正）、磁构型/SOC及应变/缺陷设置，且SHG等响应量并非DFT直接输出而需Wannier插值与量子几何后处理；强关联效应、有限温与超快动力学过程仍超出直接适用范围。

## 代表作

- paper:2025-s11433-025-2698-5-ubiquitous-van-der-waals-altermagnetism-with-slidingmoire-fe
- paper:2026-acs.jpclett.6c00283-intrinsic-altermagneticferroelectric-multiferroicity-and-mag
- paper:2025-2501.16741-quantum-geometric-origin-of-strain-tunable-giant-second-harm
- paper:2026-2602.21135-effect-of-symmetry-breaking-on-altermagnetism-in-crsb-and-fo

## 证据日志

- 2026-09-19｜r22｜仅简报｜[paper:2025-s11433-025-2698-5-ubiquitous-van-der-waals-altermagnetism-with-slidingmoire-fe] 第一性原理DFT计算（非共线磁性+SOC）：对系列反平行堆叠磁性vdW多层的系统计算，证明滑移/莫尔铁电与交变磁性共存的普适性并给出自旋劈裂与极化的数值估计。
- 2026-09-19｜r22｜仅简报｜[paper:2026-acs.jpclett.6c00283-intrinsic-altermagneticferroelectric-multiferroicity-and-mag] 第一性原理DFT计算：验证NiBr2/MnBr2交变磁+铁电多铁基态的能量与电子结构稳定性。
- 2026-09-20｜r28｜回原文｜[paper:2025-2501.16741-quantum-geometric-origin-of-strain-tunable-giant-second-harm] DFT+SOC 第一性原理能带计算：提供含强自旋轨道耦合的 Bi2O2X 能带，确认非中心对称结构与带边 SOC 劈裂，是全部响应计算的输入。
- 2026-09-20｜r28｜仅简报｜[paper:2026-2602.21135-effect-of-symmetry-breaking-on-altermagnetism-in-crsb-and-fo] 第一性原理DFT能带计算：给出pristine与缺陷/掺杂CrSb中自旋劈裂能带及磁性点群变化的基态图像。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2025-2501_16741-quantum-geometric-origin-of-strain-tunable-giant-second-harm]]
- [[2501.16741]]
- [[CrSb]]
- [[DFT计算]]
- [[自旋劈裂]]
- [[量子几何]]
- [[非线性光学]]
<!-- /linsai-wikilinks -->
