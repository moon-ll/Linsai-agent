---
title: "Energy-Embedded Neural Solvers for One-Dimensional Quantum Systems"
type: "papers"
created: "2026-10-08T18:53:47Z"
updated: "2026-10-31T11:43:58Z"
tags: ["PINN", "量子系统求解", "神经网络", "薛定谔方程", "能量嵌入"]
related: ["PINN（物理信息神经网络）", "TDSE", "general-quantum-geometry-inversion-20260726", "一维量子系统", "强场电离", "强场超快", "强场超快光学", "强场超快动力学", "本征值问题", "物理信息神经网络", "量子几何", "量子几何反演"]
source_raw: "2025-2405.24194-energy-embedded-neural-solvers-for-one-dimensional-quantum-s.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Energy-Embedded Neural Solvers for One-Dimensional Quantum Systems

## 林赛的理解

这篇论文把"能量"作为显式约束嵌入到 PINN（物理信息神经网络）的损失函数中，用来求解一维定态薛定谔方程。摘要级信息提到覆盖了几类典型的势能模型——无限深势阱、谐振子、Woods-Saxon、双势阱——并同时给出基态与激发态的波函数和本征能谱。

作为强场超快光学的 PI，我第一眼看到的是"神经网络解薛定谔方程"这件事本身。我们在强场电离、高次谐波、attochemistry 这些方向上天天和时间依赖薛定谔方程（TDSE）打交道，数值求解的代价是实验和理论工作的主要瓶颈之一。这篇针对的是 TISE（定态），但**方法论本身**——把守恒量嵌入神经网络作为归纳偏置——对我有吸引力，因为它给我一个直觉：如果能量嵌入对 TISE 有效，那同样的思路能不能搬到 TDSE 上？比如把 Hamiltonian 量纲的能量（或者说作用量、phase）嵌入到网络里，来约束激光场–物质相互作用的演化？

另外一个我感兴趣的点是**激发态**的同时求解。强场里很多有意思的现象（通道关闭、recollision 对激发态的依赖、多电子动力学）都依赖对激发态结构的准确描述。如果神经网络方法能以统一的方式给出连续多个本征态，比起传统基组展开在工程实现上可能更轻量。

## 核心要点

- **方法核心**：基于能量的嵌入式 PINN 求解器。把定态薛定谔方程的能量（或者说能量作为拉格朗日乘子/约束条件）显式编入网络结构或损失函数，使网络在学习波函数的同时也对本征值进行约束。
- **覆盖体系**：摘要中列出的势能类型包括
  - 无限深方势阱（教科书基准）
  - 谐振子（解析解已知，便于验证）
  - Woods-Saxon 势（核物理相关的一维模型）
  - 双势阱（具有隧穿/简并结构）
- **输出**：同时获得基态和激发态的波函数 $\psi_n(x)$ 与本征能量 $E_n$。
- **定位**：属于"科学机器学习 / 物理信息机器学习"分支，arxiv 编号 2405.24194（2025 年发表）。

## 实验/研究关联

- **TDSE 求解的替代思路**：我们组目前用 TDSE 计算强场电离和谐波谱，多依赖 Crank-Nicolson、split-operator 或 t-SURFF 这类方法。PINN/能量嵌入路线如果能推广到含时情形，将多一个工具选项，尤其在多电子、多通道耦合导致 grid-based 方法难以承受时。
- **Woods-Saxon 与核结构远场类比**：Woods-Saxon 是核物理中常见的势形，强场里我更多看到的是它在描述量子阱、原子核壳模型的类比价值——但更重要的是，"用一个普适势表达 + 神经网络解"的范式能否迁移到我处理的势能形态（如库仑 + 激光场修正势、Coulomb-corrected strong-field approximation 的有效势）。
- **激发态与通道动力学**：双势阱的隧穿/简并结构让人联想到强场中的非绝热耦合、LICl 之类的两中心干涉效应。如果能量嵌入 PINN 能稳定给出多个相干叠加的态，对我处理 multi-state quantum dynamics 是一个可借鉴的基准。
- **项目归属**：摘要元数据显示被标注为 `NSFC-强场超快` 方向候选，且出现在 `general-quantum-geometry-inversion-20260726` 的 proposal 引用列表里，说明这条线已经进入我们组的视野。

## 开放问题

- **能量嵌入的具体形式**：摘要没有给出损失函数的精确构造。是把 $E$ 作为可学习参数 + 正交惩罚？还是把 Hamiltonian 期望值嵌入 loss？这直接影响对激发态收敛稳定性的判断。**需要读全文**。
- **TISE→TDSE 推广的可行性**：定态方程没有时间，能量嵌入很自然；但 TDSE 里"能量"不再是常数（激光场驱动下含时），嵌入策略需要重新设计。是用瞬时能量、还是用 Floquet 准能？这是我读完想优先和作者对照的点。
- **精度与可扩展性**：对于 Woods-Saxon、双势阱这类无解析解体系，能达到多高的相对能量误差？是否能和 DVR（离散变量表示）这类成熟方法在网格数 vs. 精度的 trade-off 上竞争？
- **与现有 PINN 文献的关系**：自 2019 年 Raissi 的 PINN 以来，定态量子力学问题的神经网络求解已经有相当多工作。这篇的"能量嵌入"相对现有 baseline（vanilla PINN、deep Ritz 等）的边际贡献需要量化——是工程优化还是原理性新意？
- **与 `quantum-geometry-inversion` 项目的接口**：元数据显示该论文被一个关于"量子几何反演"的 proposal 引用。是否意味着他们想用神经网络的 PDE 求解能力反过来做势能反演（从已知波函数/能谱推回势形）？这对我们做强场动力学反问题有潜在启发。

## 来源
- 原始材料：2025-2405.24194-energy-embedded-neural-solvers-for-one-dimensional-quantum-s.md
- 蒸馏时间：2026-10-08T18:53:47Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：能量嵌入物理信息神经网络求解一维定态薛定谔方程

**原理**：把能量作为显式约束嵌入 PINN 损失函数/网络结构，求解一维定态薛定谔方程并同时给出基态与激发态波函数 ψₙ(x) 与本征能量 Eₙ——能量嵌入作为归纳偏置约束本征值。覆盖四类典型势：无限深势阱、谐振子、Woods-Saxon、双势阱。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 方法核心 | 能量嵌入式 PINN（能量为可学习参数/约束，波函数与本征值联合输出） | 核心要点 |
| 覆盖势能 | 无限深方势阱 / 谐振子 / Woods-Saxon / 双势阱 | 核心要点 |

**适用边界**：摘要级：能量嵌入的具体损失构造（可学习 E + 正交惩罚 vs Hamiltonian 期望值嵌入）未知；TISE→TDSE 推广（激光驱动下能量非常数，需瞬时能量或 Floquet 准能策略）为开放设计问题；与 vanilla PINN/deep Ritz 的边际贡献未量化；无解析解体系的相对能量误差未给出。
**代表作**：Energy-Embedded Neural Solvers for One-Dimensional Quantum Systems, arXiv:2405.24194 (2025)
*方法卡回补 2026-10-08*

<!-- linsai-wikilinks -->
## 关联概念

- [[PINN（物理信息神经网络）]]
- [[TDSE]]
- [[general-quantum-geometry-inversion-20260726]]
- [[一维量子系统]]
- [[强场电离]]
- [[强场超快]]
- [[强场超快光学]]
- [[强场超快动力学]]
- [[本征值问题]]
- [[物理信息神经网络]]
- [[量子几何]]
- [[量子几何反演]]
<!-- /linsai-wikilinks -->
