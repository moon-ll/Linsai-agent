---
title: "Machine learning emulator for TDSE"
type: "papers"
created: "2026-11-19T04:59:46Z"
updated: "2026-11-19T05:26:58Z"
tags: ["机器学习代理模型", "TDSE", "强场物理", "量子动力学模拟"]
related: ["TDSE", "参数扫描加速", "强场超快", "强场超快光学", "数值求解TDSE", "载波包络相位"]
source_raw: "2024-2405.20931-machine-learning-emulator-for-tdse.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Machine learning emulator for TDSE

## 林赛的理解
这篇工作直击我们强场模拟中一个长期痛点：TDSE 数值求解在参数扫描（激光强度、波长、脉冲宽度、载波包络相位等）时计算成本极高。我们组做高次谐波或电离速率参数依赖研究时，一次扫描往往要跑成百上千次 TDSE，GPU/CPU 时间是瓶颈。机器学习代理模型（emulator/surrogate）若能在保持物理精度的前提下把参数空间的探索成本降低几个量级，对我们的提案论证（如 NSFC-强场超快项目）会是实质性的方法学升级。不过从元数据看，这篇只有摘要级描述，具体网络架构、训练数据规模和外推能力尚不清楚，需要精读原文评估。

## 核心要点
- 提出 TDSE 的代理模型辅助（surrogate-assisted）求解方案，用于量子动力学模拟。
- 目标是降低强场模拟中参数扫描的计算成本。
- 2024 年 arXiv 预印本（arXiv:2405.20931）。

## 实验/研究关联
- 与我们的 general-ssh-weyl-20260920 提案相关：若 Weyl/强场体系需要大规模参数依赖的波包动力学计算，ML emulator 可作为加速层。
- 可与我们现有的 TDSE 数值流程结合，先用 emulator 粗扫参数空间，再对感兴趣区域用全 TDSE 精修。
- 也可与解析模型（如 SFA/强场近似）交叉验证 emulator 的物理合理性。

## 开放问题
- 摘要未说明：训练数据来自什么体系（单电子？分子？）、什么激光参数范围？
- emulator 在训练域外的外推能力如何？强场物理中非线性极强（隧穿电离、共振）区域是否可靠？
- 是否能给出可解释的物理量（电离概率、谐波谱），还是只输出波函数本身？
- 与直接用 GPU 加速 TDSE 或 SFA 解析近似相比，性价比优势有多大？

## 来源
- 原始材料：2024-2405.20931-machine-learning-emulator-for-tdse.md
- 蒸馏时间：2026-11-19T04:59:46Z

<!-- linsai-wikilinks -->
## 关联概念

- [[TDSE]]
- [[参数扫描加速]]
- [[强场超快]]
- [[强场超快光学]]
- [[数值求解TDSE]]
- [[载波包络相位]]
<!-- /linsai-wikilinks -->

## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：TDSE 的机器学习仿真器（代理模型辅助（surrogate-assisted）TDSE 求解方案：降低强场模拟中参数扫描（激光强度/波长/脉宽/CEP）的计算成本——一次扫描往往成百上千次 TDSE、GPU/CPU 时间是瓶颈；emulator 粗扫参数空间+感兴趣区域全 TDSE 精修的组合策略）

**原理**：提出 TDSE 的代理模型辅助（surrogate-assisted）求解方案：目标是降低强场模拟中参数扫描（激光强度/波长/脉冲宽度/载波包络相位等）的计算成本（一次扫描往往要跑成百上千次 TDSE、GPU/CPU 时间是瓶颈）——ML 仿真器若能在保持物理精度前提下把参数空间探索成本降低几个量级，对强场项目论证是实质性方法学升级；组合策略：先用 emulator 粗扫参数空间、再对感兴趣区域用全 TDSE 精修；也可与解析模型（SFA/强场近似）交叉验证 emulator 的物理合理性。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 方法框架 | ML emulator 代理 TDSE（surrogate-assisted；2024，arXiv:2405.20931——训练数据体系/激光参数范围/外推能力均未载，摘要级无 PDF） | 核心要点（摘要级） |

**适用边界**：摘要级来源（无 PDF）——训练数据来自什么体系（单电子/分子）、什么激光参数范围未说明；emulator 在训练域外的外推能力未知（强场物理非线性极强：隧穿电离/共振区域是否可靠）；能否给出可解释的物理量（电离概率/谐波谱）还是只输出波函数本身待核；与直接 GPU 加速 TDSE 或 SFA 解析近似相比的性价比优势待比较。
**代表作**：arXiv:2405.20931（2024），Machine learning emulator for TDSE（TDSE ML 仿真器+粗扫精修组合策略素材；ssh-weyl 提案加速层候选）
*方法卡回补 2026-11-19*
