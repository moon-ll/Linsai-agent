---
title: "Quasi-Phase-Matching Enabled by van der Waals Stacking"
type: "papers"
created: "2026-11-17T11:12:50Z"
updated: "2026-11-17T11:21:26Z"
tags: ["准相位匹配", "二次谐波", "范德华堆垛", "3R-MoS2", "非线性光学"]
related: ["SHG", "TMD材料", "强场超快", "强场超快光学", "相位匹配"]
source_raw: "2024-2411.00303-quasi-phase-matching-enabled-by-van-der-waals-stacking.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Quasi-Phase-Matching Enabled by van der Waals Stacking

## 林赛的理解
这篇工作（arXiv:2411.00303，Tang, Sripathy, Qin, Lu 等，2024）的核心思路是利用 3R 相 MoS₂ 的破缺反演对称性，通过范德华堆垛的层间转角对齐实现准相位匹配（QPM），从而提升二次谐波（SHG）的转换效率与稳定性。从我们强场超快课题组的角度看，这属于"结构工程补偿相位失配"的路线：传统块体晶体依赖周期极化（如 PPLN）实现 QPM，而这里把周期性结构直接做进二维堆垛的层间自由度里。材料摘要级信息有限，具体层厚、转角周期、效率数值我暂不引用，待拿到 PDF 后补充。

## 核心要点
- 利用 3R-MoS₂ 的破反演对称性作为 SHG 的非线性来源。
- 通过范德华堆垛与层间对齐构造准相位匹配，补偿传播过程中的相位失配。
- 目标是同时提升二次谐波转换效率与输出稳定性。

## 实验/研究关联
- 与我们 NSFC-强场超快项目相关，已被 general-tmd-bic-mie-anapole-20261107 提案引用。
- 3R-TMD 家族是我们关注的材料平台之一；该工作提示层间转角可作为相位匹配的自由度，可能与我们关于 BIC/Mie/anapole 共振增强非线性的方向结合——即"共振增强 + 结构 QPM"的复合增强策略。

## 开放问题
- QPM 周期如何随堆垛层数与转角设计？转换效率提升的定量数据尚未获取。
- 该方案在强场/少周期脉冲条件下是否仍保持稳定（损伤阈值、相位噪声）？
- 与谐振增强机制（BIC、anapole）叠加时是否存在饱和或竞争效应？

## 来源
- 原始材料：2024-2411.00303-quasi-phase-matching-enabled-by-van-der-waals-stacking.md
- 蒸馏时间：2026-11-17T11:12:50Z

<!-- linsai-wikilinks -->
## 关联概念

- [[SHG]]
- [[TMD材料]]
- [[强场超快]]
- [[强场超快光学]]
- [[相位匹配]]
<!-- /linsai-wikilinks -->

## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：范德华堆垛实现的准相位匹配（3R-MoS₂ 破反演对称性作 SHG 非线性来源：范德华堆垛层间转角对齐构造准相位匹配（QPM）补偿传播相位失配——传统块体靠周期极化（PPLN）、这里把周期性结构直接做进二维堆垛的层间自由度——同时提升 SHG 转换效率与输出稳定性）

**原理**：利用 3R 相 MoS₂ 的破缺反演对称性作为 SHG 的非线性来源：通过范德华堆垛与层间对齐构造准相位匹配（QPM）、补偿传播过程中的相位失配（结构工程补偿相位失配路线——传统块体晶体依赖周期极化如 PPLN、本工作把周期性结构直接做进二维堆垛的层间自由度）；目标是同时提升二次谐波转换效率与输出稳定性。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 方案要素 | 3R-MoS₂ + vdW 堆垛层间转角对齐 QPM（Tang, Sripathy, Qin, Lu 等，2024，arXiv:2411.00303——QPM 周期随层数与转角的设计规律/转换效率提升定量数据未载，摘要级无 PDF） | 核心要点（摘要级） |

**适用边界**：摘要级来源（无 PDF）——QPM 周期随堆垛层数与转角设计的关系、转换效率提升定量数据待全文；强场/少周期脉冲条件下是否保持稳定（损伤阈值/相位噪声）未知；与谐振增强机制（BIC/anapole）叠加时是否存在饱和或竞争效应待探索（「共振增强+结构 QPM」复合增强策略候选）。
**代表作**：arXiv:2411.00303（Tang, Sripathy, Qin, Lu 等，2024），Quasi-Phase-Matching Enabled by van der Waals Stacking（层间转角 QPM+SHG 效率提升素材；tmd-bic-mie-anapole 提案引用）
*方法卡回补 2026-11-17*
