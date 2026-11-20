---
title: "2025-s41598-025-92900-1-physics-informed-neural-networks-with-hybrid-kolmogorov-arno"
type: "papers"
created: "2026-09-26T21:30:47Z"
updated: "2026-11-15T15:09:24Z"
tags: []
related: ["TDSE", "TDSE求解器", "general-quantum-geometry-inversion-20260726", "强场电离", "强场超快", "强场超快光学", "量子几何", "量子几何反演"]
source_raw: "2025-s41598-025-92900-1-physics-informed-neural-networks-with-hybrid-kolmogorov-arno.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
aliases: ["s41598-025-92900"]
digest_level: "abstract"
---

• ---
  title: "Physics-informed neural networks with hybrid Kolmogorov-Arnold network and augmented Lagrangian function for solving partial differential equations"
  type: papers
  created: "2026-09-26T21:30:10Z"
  updated: "2026-09-26T21:30:10Z"
  tags: ["PINN", "KAN", "机器学习求解PDE", "科学计算", "NSFC-强场超快"]
  related: ["物理信息神经网络", "Kolmogorov-Arnold网络", "薛定谔方程数值求解", "TDSE求解器"]
  source_raw: "2025-s41598-025-92900-1-physics-informed-neural-networks-with-hybrid-kolmogorov-arno.md"
  growth_stage: "growing"
  confidence: 0.7
  auto_grown: true
  review_status: "pending"
  ---

  # Physics-informed neural networks with hybrid Kolmogorov-Arnold network and augmented Lagrangian function for solving partial differential equations

  ## 林赛的理解

  这是 2025 年发表在 Scientific Reports 上的一篇方法学论文，提出 AL-PKAN：把 Kolmogorov-Arnold 网络（KAN）与增广拉格朗日方法（augmented Lagrangian）结合用于求解偏微分方程。核心思路有两层：

  一是网络结构上，用 KAN 替代 PINN 中惯用的 MLP。KAN 的可学习激活函数（B-spline 参数化）在逼近光滑解和表达函数组合结构上有理论优势，这一点在函数拟合基准上已有报道，本文把它落到 PDE 求解场景。

  二是约束处理上，不直接把边界/初始条件以固定权重罚函数的形式硬塞进损失函数，而是把罚因子和拉格朗日乘子都做成可学习参数，随训练过程自适应更新——这就是"增广拉格朗日 + PINN"的混合方案。罚函数法的老问题是权重需要手调、软约束过松或过紧都难收敛，可学习的乘子相当于让优化器自己决定"该多重视这条边界条件"。

  作为做强场超快光学的 PI，我对这篇的兴趣点很直接：我们组数值求解含时薛定谔方程（TDSE）、光传播方程（UPPE）的耗时是仿真管线的主要瓶颈之一，PINN 类方法若能在大自由度、长传播距离上替代或加速传统网格法，对 HHG 谱反演、少周期脉冲与介质相互作用建模都有潜在价值。但摘要级信息太少，我还无法判断 AL-PKAN 处理多维、刚性（stiff）PDE 的实际表现，这类方法在振荡解和长时间积分上的稳定性是硬门槛。

  ## 核心要点

  - **方法名称**：AL-PKAN（augmented Lagrangian + physics-informed KAN）
  - **两个可学习组件**：① KAN 作为解的表示网络（替代 MLP）；② 增广拉格朗日框架下罚因子与拉格朗日乘子均为可学习参数，自适应平衡 PDE 残差与边界/初值约束
  - **动机**：PINN 损失中软约束权重需手工调节且跨问题迁移差；可学习乘子自动调节约束强度
  - **任务类型**：偏微分方程求解（本文具体基准问题因摘要缺失未详）
  - **来源**：Scientific Reports（期刊号 s41598），2025，Zhang 等
  - deepxiv 评分 0.82，已标记供 `general-quantum-geometry-inversion-20260726` 课题参考

  ## 实验/研究关联

  - **TDSE/UPPE 求解加速**：KAN-PINN 路线若成熟，可作为强场电离、HHG 模拟的替代求解器候选，值得组内做一次小规模复现（Poisson/谐振子等标准基准先行）
  - **反问题场景**：PINN 天然支持"数据 + 物理"混合损失，与我们在做的量子几何反演（从 HHG 谱反推能带/波形）契合——物理约束项正缺一个鲁棒的权重自适应机制，AL 思路可直接借鉴
  - **方法借鉴优先级**：即便不换求解器内核，"可学习拉格朗日乘子"这一技巧也可迁移到我们现有 PINN 基线的损失工程上，成本最低
  - **待验证**：无 PDF 全文，具体测试了哪些 PDE、与标准 PINN/hp-VPINN 的对比幅度、训练开销均未知，不建议在申请书中引用具体数字

  ## 开放问题

  - AL-PKAN 在高频振荡解（强场体系特征）上是否保持收敛？KAN 的样条激活对振荡函数的逼近能力需实测
  - 增广拉格朗日乘子的自适应更新是否引入新的超参数负担（如更新步长、乘子初始化）？
  - 相比"权重退火/NTK 加权"等软约束自动加权方案，AL 路线的净收益几何？需同一组 PDE 基准上的对照
  - 多维问题（3D TDSE 约化坐标）上 KAN 参数量与训练成本是否可接受？
  - 后续应获取全文并核对：基准 PDE 清单、误差指标、与哪些基线方法对比

  ## 来源
  - 原始材料：2025-s41598-025-92900-1-physics-informed-neural-networks-with-hybrid-kolmogorov-arno.md
  - 蒸馏时间：2026-09-26T21:30:10Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：PINN 混合 Kolmogorov-Arnold 表示（Scientific Reports，摘要级）

**原理**：物理信息神经网络混合 Kolmogorov-Arnold 网络（PINN + hybrid KAN）表示——题录页未含研究方法节。

**适用边界**：页面为摘要级题录（81 行，无研究方法节）；不虚构参数，待精读后升级。
**代表作**：本文（Scientific Reports，DOI 10.1038/s41598-025-92900-1）
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[TDSE]]
- [[TDSE求解器]]
- [[general-quantum-geometry-inversion-20260726]]
- [[强场电离]]
- [[强场超快]]
- [[强场超快光学]]
- [[量子几何]]
- [[量子几何反演]]
<!-- /linsai-wikilinks -->
