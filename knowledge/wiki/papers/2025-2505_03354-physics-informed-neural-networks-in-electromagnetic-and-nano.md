---
title: "Physics-Informed Neural Networks in Electromagnetic and Nanophotonic Design（论文精读笔记）"
type: "papers"
created: "2026-08-15T21:58:42Z"
updated: "2026-08-15T21:58:42Z"
tags: ["PINN", "纳米光子学", "电磁逆设计", "光学反演", "域迁移", "机器学习"]
related: ["Maxwell方程求解", "NSFC-强场超快", "相位恢复", "瞬态量子相位光学", "逆问题"]
source_raw: "2025-2505.03354-physics-informed-neural-networks-in-electromagnetic-and-nano.md"
growth_stage: "growing"
confidence: 0.7
auto_grown: true
review_status: "pending"
---

# Physics-Informed Neural Networks in Electromagnetic and Nanophotonic Design（精读笔记）

## 林赛的理解

这篇是 Abdelraouf 等人 2025 年的综述（arXiv:2505.03354），系统梳理 PINN 在电磁与纳米光子设计中的应用。需要先说明：我库里的条目目前只有摘要级信息（read_status: unread，has_pdf: false），本笔记第一轮蒸馏基于管线摘要加我对该领域的既有判断，部分“要点”是按领域惯例补全的先验，待全文到位后必须回填核验。

从我的立场看，这篇综述的价值不在于“设计纳米光子器件”本身，而在于它给出的两个技术骨架：**物理约束下的光学反演**（从稀疏散射/近场数据恢复介电分布与场分布）和**域迁移**（把一个几何/材料/频段学到的解迁移到另一个域）。这两件事恰好是我在 "transient quantum phase optics" proposal 里最缺的工具——如何从有限的瞬态光谱干涉数据中反演强场诱导的时变相位，本质上就是一个病态逆问题。

但我也要先泼自己一盆冷水：PINN 在电磁领域演示的问题尺度（几个波长、线性、多为频域）与我们的问题（飞秒–阿秒时间分辨、非微扰非线性、传播–电子动力学多尺度耦合）之间隔着数量级的鸿沟。综述里能直接抄的大概是框架和方法论，而不是任何一家的具体损失函数。

## 核心要点

### 核心发现（摘要级蒸馏，待全文核验）
1. **综述定位**：PINN 在电磁/纳米光子学的系统性回顾，覆盖正问题（PDE 约束求解）与逆问题（光学反演）两条主线。
2. **光学反演**：以 Maxwell/Helmholtz 方程残差作为软约束，从散射场、近场或模式数据中恢复介电常数分布、几何拓扑或源参数，无需大规模标注数据。
3. **域迁移（domain transfer）**：学到的解/参数化可跨几何、材料、频段迁移，缓解逐工况重训的成本——这是该综述区别于一般 PINN 综述的特色标签，也是管线给它打的关联锚点。
4. **应用面**：超表面、波导、等离激元结构、散射反演等纳米光子逆设计场景。

### 方法亮点
- 物理嵌入方式：PDE 残

<!-- linsai-wikilinks -->
## 关联概念

- [[Maxwell方程求解]]
- [[NSFC-强场超快]]
- [[相位恢复]]
- [[瞬态量子相位光学]]
- [[逆问题]]
<!-- /linsai-wikilinks -->
