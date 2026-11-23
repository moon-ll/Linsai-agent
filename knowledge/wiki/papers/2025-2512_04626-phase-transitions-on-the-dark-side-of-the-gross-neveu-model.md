---
title: "Phase transitions on the dark side of the Gross-Neveu model: Spontaneous O(4N) symmetry breaking at repulsive coupling"
type: "papers"
created: "2026-11-18T11:15:49Z"
updated: "2026-11-18T11:20:36Z"
tags: ["Gross-Neveu模型", "量子相变", "量子蒙特卡洛", "陈绝缘体", "量子反常霍尔"]
related: ["Dirac半金属", "Gross-Neveu普适类", "强场超快", "强场超快光学", "拓扑相变", "自发对称性破缺"]
source_raw: "2025-2512.04626-phase-transitions-on-the-dark-side-of-the-gross-neveu-model.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Phase transitions on the dark side of the Gross-Neveu model: Spontaneous O(4N) symmetry breaking at repulsive coupling

## 林赛的理解

这篇工作研究的是 2+1 维 Gross-Neveu 模型在排斥耦合一侧的量子相变，用大尺度量子蒙特卡洛（QMC）给出了从无质量 Dirac 半金属到量子反常霍尔（QAH）绝缘体的连续转变证据，转变过程中空间反演与时间反演对称性自发破缺，破缺模式为 O(4N)。

我的实验室做的是强场超快光学，虽然不直接做晶格 QMC，但这篇论文对我们有方法学上的启发：强场超快调控（如 Floquet 周期光驱动）正是可以在固态晶格体系中诱导 Dirac 半金属到陈绝缘体转变的手段。理论这边把相互作用驱动的关联相变基准化，等于给光驱动实验提供了"零场参考态"——我们先要知道相互作用本身能把体系推到哪里，才能分辨光场诱导的赝平衡相与真正的非平衡相。这在我们 general-ssh-weyl-20260920 提案里（该文已被标记为引用文献）是关键的一环。

## 核心要点

- 体系：2+1 维 Gross-Neveu 模型，聚焦此前较少探索的排斥耦合（"dark side"）一侧。
- 方法：大尺度无符号问题量子蒙特卡洛模拟。
- 相变图像：无质量 Dirac 半金属 → 量子反常霍尔绝缘体的连续量子相变。
- 对称性：转变伴随空间反演与时间反演对称性的自发破缺，破缺模式为 O(4N)。
- 意义：为 Haldane 型陈绝缘体的关联机制提供了无偏数值基准。

## 实验/研究关联

- 与课题组 NSFC-强场超快项目及 general-ssh-weyl-20260920 提案相关，可作为光驱动 Dirac 体系实现陈绝缘体相的平衡态理论对照。
- 强场超快视角：Floquet/光泵浦可在光学晶格与转角材料中诱导同类 Haldane 型序，QMC 基准有助于区分相互作用、驱动与耗散各自的角色。
- QAH 绝缘体与拓扑缺陷动力学是非平衡相变实验中可探测的序参量信号（时间分辨克尔/霍尔测量）。

## 开放问题

- O(4N) 破缺模式的临界指数与标准 Gross-Neveu 普适类（如 Gross-Neveu-XY/SO(5)）的关系如何？摘要级材料未给出。
- 光驱动（Floquet）条件下该相变如何被改写——是否存在光诱导增强或抑制陈绝缘体序的机制？
- 该模型与实际固态/冷原子体系（Haldane 模型实现）的对应程度有限，实验可迁移性待评估。
- 摘要未提供具体数值结果（临界耦合、有限尺度外推细节），需读全文确认。

## 来源
- 原始材料：2025-2512.04626-phase-transitions-on-the-dark-side-of-the-gross-neveu-model.md
- 蒸馏时间：2026-11-18T11:15:49Z

<!-- linsai-wikilinks -->
## 关联概念

- [[Dirac半金属]]
- [[Gross-Neveu普适类]]
- [[强场超快]]
- [[强场超快光学]]
- [[拓扑相变]]
- [[自发对称性破缺]]
<!-- /linsai-wikilinks -->

## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：Gross-Neveu 模型暗侧的相变：排斥耦合下自发 O(4N) 对称性破缺（2+1 维 Gross-Neveu 模型排斥耦合一侧的大尺度无符号问题 QMC：**无质量 Dirac 半金属 → 量子反常霍尔（QAH）绝缘体的连续量子相变**（伴随空间反演与时间反演对称性自发破缺、破缺模式 O(4N)）——为 Haldane 型陈绝缘体的关联机制提供无偏数值基准=光驱动实验的「零场参考态」）

**原理**：研究 2+1 维 Gross-Neveu 模型在排斥耦合一侧（「dark side」，此前较少探索）的量子相变：方法为大尺度无符号问题量子蒙特卡洛（QMC）模拟；相变图像：无质量 Dirac 半金属 → 量子反常霍尔（QAH）绝缘体的连续量子相变——转变伴随空间反演与时间反演对称性的自发破缺、破缺模式为 O(4N)；意义：为 Haldane 型陈绝缘体的关联机制提供无偏数值基准（方法学启发：强场超快调控（Floquet 周期光驱动）正是可在固态晶格体系诱导 Dirac 半金属到陈绝缘体转变的手段——理论把相互作用驱动的关联相变基准化=给光驱动实验提供「零场参考态」：先要知道相互作用本身能把体系推到哪里、才能分辨光场诱导的赝平衡相与真正非平衡相）。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 方法与结果 | 大尺度无符号问题 QMC + 排斥耦合 O(4N) 自发破缺 → Dirac 半金属到 QAH 绝缘体连续相变（临界耦合/有限尺度外推细节/O(4N) 破缺模式与 Gross-Neveu 普适类关系未载，摘要级无 PDF） | 核心要点（摘要级） |

**适用边界**：摘要级来源（无 PDF）——O(4N) 破缺模式的临界指数与标准 Gross-Neveu 普适类（Gross-Neveu-XY/SO(5)）的关系未给出；光驱动（Floquet）条件下该相变如何被改写（是否存在光诱导增强或抑制陈绝缘体序的机制）待探索；模型与实际固态/冷原子体系（Haldane 模型实现）的对应程度有限、实验可迁移性待评估；具体数值结果（临界耦合/有限尺度外推）需读全文确认；QAH 绝缘体与拓扑缺陷动力学是非平衡相变实验可探测的序参量信号（时间分辨克尔/霍尔测量）。
**代表作**：arXiv:2512.04626（2025），Phase transitions on the dark side of the Gross-Neveu model（排斥耦合 QMC 基准+光驱动 Dirac→QAH 相变零场参考态素材；ssh-weyl 提案引用）
*方法卡回补 2026-11-18*
