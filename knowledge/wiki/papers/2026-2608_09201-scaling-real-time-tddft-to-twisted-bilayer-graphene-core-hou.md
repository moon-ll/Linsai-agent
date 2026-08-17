---
title: "论文精读 | Scaling Real-Time TDDFT to Twisted Bilayer Graphene: Core-Hour Benchmarks and Hybrid Tight-Binding Acceleration"
type: "papers"
created: "2026-08-15T21:19:45Z"
updated: "2026-08-17T05:19:30Z"
tags: ["rt-TDDFT", "twisted-bilayer-graphene", "moire-超晶格", "tight-binding", "计算基准", "强场超快"]
related: ["Scaling Real-Time TDDFT to Twisted Bilayer Graphene: Core-Hour Benchmarks and Hybrid Tight-Binding Acceleration", "TDDFT/TB杂交", "moiré强场探针", "固体高次谐波", "多尺度模拟", "量子几何反演"]
source_raw: "2026-2608.09201-scaling-real-time-tddft-to-twisted-bilayer-graphene-core-hou.md"
growth_stage: "growing"
confidence: 0.7
auto_grown: true
review_status: "pending"
---

# 论文精读 | Scaling Real-Time TDDFT to Twisted Bilayer Graphene: Core-Hour Benchmarks and Hybrid Tight-Binding Acceleration

## 林赛的理解

这篇笔记对应的是我一直悬着的一个问题：**在 moiré 体系里做实时 TDDFT 模拟，机时到底要烧到什么量级**。我们组做固体强场超快（HHG、载流子注入、亚周期响应），rt-TDDFT 是数值上的主力工具——在常规晶体（MoS₂、单层石墨烯这个量级）已经跑得很顺，但一旦碰到魔角附近的扭转双层石墨烯，超胞动辄上万原子，全 ab initio 的实时传播基本不现实。这篇工作直接给出 core-hour 随体系尺寸、扭转角、基组变化的标度基准，正是我写 NSFC 强场超快项目以及那两个 moiré 相关 proposal 时缺的可行性论据。

更让我在意的是他们提出的 TDDFT/TB 杂交加多尺度嵌入路线——这和我们想做的"强场作用区用 TDDFT 精确处理、moiré 大尺度背景用 TB"的图景高度吻合。如果这套方案在强场条件下站得住，我们就可以第一次真正模拟 flat band 里的场驱动动力学（Wannier-Stark 局域化、层间极化、非平庸量子几何对非线性响应的贡献），而不只是在 k·p 模型层面打转。

不过要提醒自己：目前库里只有摘要级信息（has_pdf: false），杂交格式、场耦合方式、具体标度指数都还没核实，引用其数据写 proposal 之前必须拉全文。

## 核心要点

### 核心发现
- 对**共度（commensurate）与非共度（incommensurate）** TBG 超胞系统基准测试了 rt-TDDFT 的 core-hour 开销
- 报告机时随**体系尺寸、扭转角、基组大小**的标度关系（具体标度指数需全文确认）
- 隐含结论：全 ab initio rt-TDDFT 在 moiré 尺度超胞上的成本可能构成实际瓶颈，由此引出加速方案（推断，待全文验证）

### 方法亮点
- **TDDFT/TB 杂交方法**作为降本路线：兼顾 ab initio 精度与 TB 的可扩展性
- **多尺度嵌入（multiscale embedding）**提案：面向 moiré 尺度电子动力学的分区处理框架
- 明确区分共度/非共度体系并分别讨论处理策略——非共度准周期结构的超胞近似是 twistronics 计算的老大难，正面处理值得肯定

## 实验/研究关联

- **直接支撑在库 proposal**：
  - `general-moire-strong-field-probe-20260726`：机时标度数据可直接写入"计算可行性"部分
  - `general-quantum-geometry-inversion-20260726`：杂交框架若能跑强场，量子几何对非线性响应的贡献就有了第一性计托底
- **对我们组的意义**：
  1. 界定 TBG 上固体 HHG / 强场载流子动力学模拟的"成本墙"，决定哪些参数空间可以纯 ab initio、哪些必须降级到 TB/k·p
  2. 杂交嵌入思路可迁移到我们关心的场景：均匀强场 + moiré 平带、层间偏压下的非线性响应
  3. 基准数据可用来校准我们自己的 TB 强场传播代码（Peierls 替换方案）的适用边界
- 作者列表里有 K. Watanabe——若为 hBN 晶体生长那位，可能有高质量样品背景，值得留意实验合作的可能性（仅为推测，待确认）

## 开放问题

### 批判性思考
- 摘要未

<!-- linsai-wikilinks -->
## 关联概念

- [[Scaling Real-Time TDDFT to Twisted Bilayer Graphene: Core-Hour Benchmarks and Hybrid Tight-Binding Acceleration]]
- [[TDDFT/TB杂交]]
- [[moiré强场探针]]
- [[固体高次谐波]]
- [[多尺度模拟]]
- [[量子几何反演]]
<!-- /linsai-wikilinks -->
