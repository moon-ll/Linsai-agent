---
title: "Physics-Informed Neural Networks and Extensions（精读笔记）"
type: "papers"
created: "2026-10-09T04:51:40Z"
updated: "2026-11-15T15:09:19Z"
tags: ["papers", "PINN", "物理信息神经网络", "逆问题", "PDE求解", "数据驱动发现", "强场超快", "TDSE"]
related: ["TDSE", "general-quantum-geometry-inversion-20260726", "太赫兹场反演", "强场电离", "强场超快", "数据驱动PDE发现", "物理信息神经网络(PINN)", "逆PDE问题", "量子几何", "量子几何反演"]
source_raw: "2024-2408.16806-physics-informed-neural-networks-and-extensions.md"
growth_stage: "growing"
confidence: 0.6
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Physics-Informed Neural Networks and Extensions（精读笔记）

## 林赛的理解

拿到 Raissi、Perdikaris、Ahmadi、Karniadakis 这篇综述时，我第一反应是把它和我们组目前的两条主线对齐：一条是**强场超快过程中的 forward / inverse PDE 求解**（含 TDSE、Maxwell、SBE 等），另一条是**从实验观测量反演场或势能面的数据驱动建模**。

Raissi 团队是 PINN 这一支路线的开创者。这篇 2024 年的综述加扩展（arXiv:2408.16806）相当于把过去几年的延展工作做了一次系统盘点。我关心的是三件事：

1. **forward PDE 求解的精度与可扩展性**是否已经能用到三维含时的光场–物质耦合问题；
2. **inverse PDE 框架**对我们一直在做的太赫兹近场反演、阿秒条纹反演（attosecond streaking）、以及最近被列入 proposal 的"量子几何反演（general-quantum-geometry-inversion-20260726）"有多大借鉴价值；
3. **data-driven PDE discovery**（比如 PDE-Net、SINDy 类思路的神经网络版本）能否在仅有少量实验数据点的强场测量上稳定地给出可解释的方程。

摘要级信息告诉我们这篇是综述+扩展，覆盖 forward/inverse PDE 以及数据驱动的 PDE 发现。但**没有给具体数值性能指标**——下面凡涉及精度、对照基线、可推广维度等我都明确标注"待精读确认"，避免凭印象编造。

## 核心要点

- **作者与定位**：Raissi、Maziar Raissi, Paris Perdikaris, Nazanin Ahmadi, George Em Karniadakis（Brown / Notre Dame 等 PINN 学派的代表团队），2024 年 arXiv:2408.16806，是 PINN 提出后的综述并扩展（论文库评分 0.95，深耕度较高，标注来自 deepxiv-论文库）。
- **主题范围（按原始摘要）**：
  - forward PDE 问题的 PINN 求解；
  - inverse PDE 问题（带可学习参数的偏微分方程反演）；
  - **数据驱动的 PDE 发现**（从数据中回归出方程结构）。
- **方法家族**：以 PINN 为核心，扩展通常包含：
  - 残差式软约束 + 自动微分；
  - 域分解 / 分区训练（domain decomposition）以缓解梯度病态；
  - 与贝叶斯/高斯过程结合做不确定性量化；
  - 与算子学习（DeepONet / Fourier Neural Operator）耦合处理参数化 PDE；
  - 数据-物理联合损失函数框架。
- **可类比的强场场景**（仅为映射方向，**原始材料没有给出 PINN 在强场 TDSE 上的具体案例**，需在 PDF 中确认）：
  - forward：求解 1D/2D TDSE 或 SBE 给出高次谐波谱；
  - inverse：从光电子动量分布或 HHG 谱反演电离势或势能面形貌；
  - discovery：从强场扫描数据中提取有效的少能级模型哈密顿量。
- **与本组的关联（按关联字段）**：
  - 项目方向：NSFC-强场超快；
  - 关联 proposal：general-quantum-geometry-inversion-20260726。
  - 这意味着在精读时我要重点看 **inverse PDE** 与 **PDE discovery** 两章。

## 实验/研究关联

- **阿秒/强场反演链条**：我们组已有的太赫兹近场重建、阿秒条纹反演，本质上都是 inverse PDE；PINN 提供的"在残差损失里同时拟合数据和方程"的思路，比纯数据驱动的神经网络更贴合物理可解释性需求，是天然候选替代/补充方案。
- **量子几何反演（提案方向）**：从瞬态光谱或光电子数据反演 Berry 联络、Bloch 矢量等几何量，对应高度非线性、强先验的 inverse 问题。PINN 的扩展版本在带约束条件下做参数反演，是非常对口的工具，**但具体精度与可扩展性等读了正文再说**。
- **HHG / 高次谐波模拟**：TDSE 是 PINN 文献中已积累较多 toy example 的方程，但**实际三维含时偶极-速度规范下的大尺度 HHG 计算是否被 PINN 触及，原摘要没有体现，需要在精读时单独核查**。
- **可借鉴的工程经验**：分区训练、自适应权重、谱基函数结合等扩展，几乎都是把 PINN 从"能跑"推到"能用在真实 PDE 上"的关键，这也是无论做哪个强场 PDE 项目都要先吃透的工程经验。

## 开放问题

- 原始材料**没有给出** PINN 在三维 TDSE、强场 SBE 或 Maxwell–TDSE 耦合问题上的基准数值（如相对 L2 误差、收敛步数、对训练点数的标度律等）——精读时必须补全。
- **计算成本**：PINN 在网络-网格联合训练下通常比传统谱方法慢若干个量级，对超快时间尺度下需要大量采样的反问题是否可行，原文若未给出计时对比，就要在我们自己的 toy code 上复测。
- **可观测先验的注入**：强场实验中常见的探测器只测到电子动量分布的二维切片，PINN 是否能优雅地把这种"投影测量"作为数据约束而非简单 MSE，原文是否覆盖我尚未确认。
- **不确定性**："弱标注 + 强物理"的场景在 PINN 综述里通常走向贝叶斯 PINN / GAN-PINN，是否能直接迁移到光场反演的不确定度估计，需要在扩展章节里核对。
- **数据发现 PDE 的可识别性**：从少量实验点反推方程（SINDy-PDE / PDE-Net 思路）在噪声+少样本下是否仍然稳定，这是我们可能用上"量子几何反演"的根基，原文如果有专门章节讨论，要优先精读。

## 来源
- 原始材料：2024-2408.16806-physics-informed-neural-networks-and-extensions.md
- arXiv ID：2408.16806
- 关联项目：NSFC-强场超快
- 关联 proposal：general-quantum-geometry-inversion-20260726
- 蒸馏时间：2026-10-09T04:51:40Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：PINN 综述与扩展：forward/inverse PDE 求解 + 数据驱动 PDE 发现

**原理**：PINN 开创团队（Raissi/Perdikaris/Karniadakis）对物理信息神经网络的系统综述与扩展，覆盖三大主题：forward PDE 求解（残差软约束 + 自动微分）、inverse PDE 反演（带可学习参数的方程参数反演）、数据驱动 PDE 发现（从少量数据回归方程结构）。扩展家族涵盖域分解/分区训练（缓解梯度病态）、贝叶斯/高斯过程不确定性量化、算子学习耦合（DeepONet/Fourier Neural Operator）与数据-物理联合损失框架。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 主题范围 | forward PDE 求解 + inverse PDE 反演 + 数据驱动 PDE 发现（三合一综述） | 核心要点 |
| 方法家族 | 残差软约束+自动微分 / 域分解分区训练 / 贝叶斯 UQ / 算子学习（DeepONet/FNO） | 核心要点 |
| 论文库评分 | 0.95（deepxiv-论文库深耕度标注） | 核心要点 |

**适用边界**：综述+扩展性质（无原创数值案例）：未给出三维 TDSE/强场 SBE/Maxwell-TDSE 耦合问题的基准数值（相对 L2 误差、收敛步数、标度律）；PINN 网格-网络联合训练通常比谱方法慢数个量级（对超快采样反问题的可行性需自行复测）；投影测量作为数据约束（非简单 MSE）的优雅处理未确认；SINDy-PDE 少样本+噪声下的方程可识别性未系统讨论——均需精读补全。强场映射（太赫兹近场反演/阿秒条纹/量子几何反演）为页面引申关联。
**代表作**：M. Raissi, P. Perdikaris, N. Ahmadi, G. E. Karniadakis, Physics-Informed Neural Networks and Extensions, arXiv:2408.16806 (2024)
*方法卡回补 2026-10-09*

<!-- linsai-wikilinks -->
## 关联概念

- [[TDSE]]
- [[general-quantum-geometry-inversion-20260726]]
- [[太赫兹场反演]]
- [[强场电离]]
- [[强场超快]]
- [[数据驱动PDE发现]]
- [[物理信息神经网络(PINN)]]
- [[逆PDE问题]]
- [[量子几何]]
- [[量子几何反演]]
<!-- /linsai-wikilinks -->
