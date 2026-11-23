---
title: "Engineering altermagnetic symmetry to enable anomalous Hall response in Cr_{1-x}Mn_xSb"
type: "papers"
created: "2026-10-02T04:59:25Z"
updated: "2026-11-15T15:09:22Z"
tags: ["altermagnet", "CrSb", "Mn-substitution", "anomalous-Hall", "magnetic-phase-diagram", "spin-flip", "epitaxial-thin-film"]
related: ["CrSb", "altermagnetism", "general-order-parameter-ultrafast-readout", "pump-probe", "spin-split band", "strong-field ultrafast pump-probe", "交变磁体", "强场超快", "强场驱动", "自旋劈裂"]
source_raw: "2026-2602.06173-engineering-altermagnetic-symmetry-to-enable-anomalous-hall.md"
growth_stage: "growing"
confidence: 0.6
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Engineering altermagnetic symmetry to enable anomalous Hall response in Cr_{1-x}Mn_xSb

## 林赛的理解

读到这篇 arXiv:2602.06173 时，我第一反应是：Fischer、Odenbreit、Gomonay 这组人马又把"交变磁体（altermagnet）"这个还算新的概念往可工程化的方向推了一步。CrSb 是这类 d-wave 型自旋分裂材料的代表体系之一，原始 CrSb 的晶体对称性是否天然允许反常霍尔（AHE）本来就是一个微妙的问题——反常霍尔要的是时间反演对称破缺 + 一定空间对称的破缺/保留组合，纯 altermagnet 在 Néel 点以下时间反演是破的，但具体能不能给出有限 σ_xy 取决于点群细节。这篇工作的思路就很直接：在 (100) 取向的外延薄膜里做 Cr/Mn 替代合金化 Mn substitution），用化学压力 / 局域对称破缺去"裁剪"磁对称性，直到 AHE 信号浮现，并配合磁相图与自旋翻转测量把这种对称性工程和输运响应之间的因果链钉死。

从我们组的角度，我关心的是：这是一个可以用强场超快手段去"读"和"写"交变磁序的候选体系。AHE 的出现本身可以被视作交变磁对称性的一个宏观序参量代理量（proxy），这就和我们手上 "general-order-parameter-ultrafast-readout" 那条 NSFC 主线的想法对上了——如果我们能用 pump–probe / HHG / THz 发射谱在同一片 (Cr,Mn)Sb 薄膜上追踪 AHE 的瞬态演化，就能直接看到交变磁序在飞秒–皮秒时间尺度上的动力学，这是传统输运或者 XMCD 难以覆盖的窗口。

## 核心要点

- **体系**：外延 CrSb(100) 薄膜，通过 Cr 位掺 Mn 实现 Cr₁₋ₓMnₓSb 替代合金。
- **核心方法**：用元素替代作为"对称性工程"手段——改变局部的晶体场与交换相互作用，从而调控磁空间群，把本来禁止 AHE 的对称性改造成允许 AHE 的对称性。
- **核心发现**：在合适的 Mn 含量窗口内，Cr₁₋ₓMnₓSb 出现可观测的反常霍尔响应，证实 altermagnet 中 AHE 可以通过对称性裁剪而被"打开"，而不是必须依赖外加磁场或非共线自旋结构。
- **表征手段**：包含磁相图（横轴应为 Mn 含量 x 与温度 T，可能还有磁场 H）以及与自旋翻转（spin-flip / spin-flop）过程相关的测量，用于确认反常霍尔的磁有序起源而非简单寄生效应。
- **意义**：为 altermagnet 中横向输运响应的"按需设计"提供了一条 chemical route，并且把 altermagnetism 和 AHE 这两件事在实验上更紧密地绑在一起。

## 实验/研究关联

- **与我们 general-order-parameter-ultrafast-readout 主线的对接**：AHE 的 σ_xy 完全可以作为一个宏观、可电学读出的交变磁序参量代理。我们接下来可以问：飞秒光激发下 σ_xy(t) 的衰减时间常数是多少？它是不是比 Néel 序的衰减更快，从而暴露出"自旋劈裂带"和"磁对称性"两个层面的解耦？这个量在我们之前讨论的序参量分类里属于"对称性敏感"那一类，和磁化强度 M(t) 是不同的可观测量。
- **强场驱动的可能性**：CrSb 类体系自旋轨道耦合不弱、磁各向异性又强，意味着一个中等强度的 THz 或中红外脉冲可能就足以驱动 spin-flop / spin-flip。我们组擅长的强 THz 场泵浦 + 时间分辨 MOKE / 二次谐波 (SHG) 应该能直接和他们的准静态自旋翻转测量做时间尺度的对接。
- **样品来源**：注意这篇明确写的是 epitaxial (100) 薄膜，这意味着外延应力、衬底诱导对称破缺可能和 Mn 替代效应叠加在一起。我们在设计对照实验时，要意识到"对称性工程"未必只来自 Mn 替代——衬底 / 厚度 / 界面效应也得纳入讨论。
- **相图复用价值**：他们测出的 T–x（可能还有 H）磁相图可以作为我们飞秒扫描的"地图"，决定在不同 x 下应该把泵浦通量集中在相边界附近以最大化序参量的瞬态响应。

## 开放问题

- Mn 替代到底打开了哪一种对称性？是把镜面 / 旋转破坏了，还是只是改变了 d-wave 自旋分裂的 nodal direction？这点摘要里没给，必须看正文里的磁群分析或者对称指标。
- AHE 在多大 x 范围内是稳定的？临界 x_c 是相变式的还是 crossover？这直接决定它能不能当一个干净的可逆"开关"。
- 自旋翻转相关测量给出的是哪种序参量响应——是 staggered magnetization、还是 net magnetization？这一点对区分真正的 altermagnetic AHE 和寄生铁磁分量贡献的 AHE 至关重要。摘要信息不足以判断。
- 没有任何关于载流子浓度、迁移率、各向异性磁电阻的数据被提及，而在我们设计 ultrafast 实验的 pump fluence 时，这些参数是估算 spin temperature / demagnetization 幅度的必要输入——需要回到正文和补充材料里去找。
- 反常霍尔信号究竟是 intrinsic (Berry curvature) 还是 extrinsic (skew scattering / side-jump) 主导？这个问题的回答决定了我们做 pump-probe 时该期待的是 Berry curvature 的相干操控还是杂质散射通道的瞬态重整。

## 来源
- 原始材料：2026-2602.06173-engineering-altermagnetic-symmetry-to-enable-anomalous-hall.md
- 蒸馏时间：2026-10-02T04:59:25Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：Cr 位 Mn 替代合金化 Cr₁₋ₓMnₓSb：对称性裁剪打开交变磁体反常霍尔

**原理**：在 CrSb(100) 外延薄膜中通过 Cr 位掺 Mn（Cr₁₋ₓMnₓSb）做'对称性工程'——元素替代改变局域晶体场与交换相互作用，把本来禁止反常霍尔（AHE）的磁空间群改造成允许 AHE 的对称性；在合适 Mn 含量窗口内出现可观测的反常霍尔响应，证实 altermagnet 中 AHE 可通过化学对称性裁剪'打开'（无需外加磁场或非共线自旋结构）；配合磁相图与自旋翻转测量钉死对称性工程与输运响应的因果链。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 体系 | 外延 CrSb(100) 薄膜，Cr 位掺 Mn（Cr₁₋ₓMnₓSb 替代合金） | 核心要点 |
| 核心发现 | 合适 Mn 含量窗口内出现可观测反常霍尔响应（AHE 因对称性裁剪而'打开'） | 核心要点 |

**适用边界**：Mn 替代打开的具体对称性（镜面/旋转破坏 vs d-wave nodal direction 改变）未给；AHE 稳定的 x 范围与临界 x_c（相变式 vs crossover）未定；自旋翻转测量给出的是 staggered 还是 net magnetization 未明（区分真 altermagnetic AHE 与寄生铁磁贡献的关键）；载流子浓度/迁移率/AMR 数据缺失（pump fluence 估算必要输入）；AHE 是 intrinsic（Berry curvature）还是 extrinsic（skew/side-jump）主导未回答。
**代表作**：(Cr,Mn)Sb 交变磁对称性工程 AHE（Fischer/Odenbreit/Gomonay，本文，arXiv 2602.06173）；AHE 的 σ_xy(t) 可作交变磁序参量的电学可读代理。
*方法卡回补 2026-10-02*

<!-- linsai-wikilinks -->
## 关联概念

- [[CrSb]]
- [[altermagnetism]]
- [[general-order-parameter-ultrafast-readout]]
- [[pump-probe]]
- [[spin-split band]]
- [[strong-field ultrafast pump-probe]]
- [[交变磁体]]
- [[强场超快]]
- [[强场驱动]]
- [[自旋劈裂]]
<!-- /linsai-wikilinks -->
