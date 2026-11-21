---
title: "Risk-Controlled DFT Selection for Machine-Learned Interatomic Potentials"
type: "papers"
created: "2026-11-13T11:18:48Z"
updated: "2026-11-13T11:35:42Z"
tags: ["机器学习势", "DFT", "数据选择", "主动学习", "强场超快"]
related: ["DFT数据生成成本", "NSFC-强场超快", "强场分子动力学", "强场超快", "强场超快光学", "机器学习原子间势"]
source_raw: "2026-2610.19630-risk-controlled-dft-selection-for-machine-learned-interatomi.md"
growth_stage: "seedling"
confidence: 0.4
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Risk-Controlled DFT Selection for Machine-Learned Interatomic Potentials

## 林赛的理解

我是做强场超快光学的，日常面对的是飞秒强激光场下电子—核耦合动力学：激光诱导相变、非热熔化、表面库仑爆炸这类过程。要理解这些过程，绕不开大规模原子模拟——经典势在强激发条件下不可靠，DFT-MD 又太贵，动辄几千原子、皮秒尺度的轨迹根本算不动。机器学习原子间势（MLIP）是把 DFT 精度带到这个尺度的现实路径，而我们的实际痛点恰恰在训练数据：每一条标注都要一次昂贵的 DFT 计算，强场场景下还常常是更贵的激发态计算。

所以看到"风险控制的 DFT 数据选取、降低 MLIP 训练计算成本"这个题目，我的第一反应是：这可能直接服务于我们的强场 MD 管线。但要坦诚地说，目前入库的原始材料只有标题和一句话描述（无摘要、无 PDF），以下理解均为基于题目的初步推断，等拿到原文后必须逐条核验修订。

## 核心要点

- **主题**：提出一种风险控制（risk-controlled）的 DFT 数据选取策略，用于降低机器学习原子间势（MLIP）训练所需的 DFT 计算成本。
- **核心思路（据单行摘要）**：更聪明地挑选"哪些构型值得去做 DFT 计算"，从而减少训练集构建的总开销。
- **方法细节缺失**：风险如何定义、选取准则是什么、在什么体系上验证、实际节省了多少成本——原始记录中均未提供（无摘要、无 PDF）。
- **文献元数据**：Kun Ryu et al., 2026, arXiv:2610.19630；deepxiv 评分 0.78；当前状态 pool/unread；已被 key-transient-quantum-phase-optical-20260726 提案列为候选相关文献。

### 方法亮点（推断，待核验）

- "风险控制"这一措辞暗示方法中存在某种可量化的风险/误差指标来指导 DFT 标注资源的分配。方向上这与主动学习、不确定性采样一族的思想相近，但它与普通主动学习的区别是否在于某种形式化的风险保证（statistical guarantee），是精读时要确认的第一件事。

## 实验/研究关联

- 该文献直接挂在 **NSFC-强场超快** 项目下，且被瞬态量子相光学提案（key-transient-quantum-phase-optical-20260726）引用，说明入库时已被判断与我们的强场瞬态相变模拟需求相关。
- 从我的研究视角看具体的接入点：强场泵浦驱动的超快结构动力学模拟需要 MLIP，而训练集构建是最大瓶颈。若该论文的选取策略有效，可以借鉴到我们自建强场 MD 训练集

<!-- linsai-wikilinks -->
## 关联概念

- [[DFT数据生成成本]]
- [[NSFC-强场超快]]
- [[强场分子动力学]]
- [[强场超快]]
- [[强场超快光学]]
- [[机器学习原子间势]]
<!-- /linsai-wikilinks -->

## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：风险控制的 DFT 数据选取降低 MLIP 训练计算成本（risk-controlled 策略：更聪明地挑选「哪些构型值得做 DFT 计算」——减少训练集构建总开销）

**原理**：提出风险控制（risk-controlled）的 DFT 数据选取策略，用于降低 MLIP 训练所需的 DFT 计算成本：更聪明地挑选「哪些构型值得去做 DFT 计算」从而减少训练集构建总开销（「风险控制」措辞暗示存在可量化的风险/误差指标指导 DFT 标注资源分配——与主动学习/不确定性采样一族思想相近，区别是否在于某种形式化风险保证（statistical guarantee）待精读确认）。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 主题 | risk-controlled DFT 数据选取降低 MLIP 训练计算成本（标题+一句话描述；Kun Ryu et al.，2026，arXiv:2610.19630、deepxiv 0.78、pool/unread、无摘要无 PDF——风险定义/选取准则/验证体系/节省成本均未提供） | 核心要点 |

**适用边界**：标题级预读（growth_stage: seedling、confidence 0.4、无摘要无 PDF）——以下理解均为基于题目的初步推断、拿到原文后必须逐条核验修订；风险如何定义/选取准则/验证体系/实际节省成本均未提供；与普通主动学习的区别（形式化风险保证？）待精读确认。
**代表作**：arXiv:2610.19630（Kun Ryu et al.，2026），Risk-Controlled DFT Selection for Machine-Learned Interatomic Potentials（强场 MD 训练集构建成本控制素材；标题级预读待全文）
*方法卡回补 2026-11-13*
