---
title: "Relativistic spin-momentum locking in ferromagnets"
type: "papers"
created: "2026-09-29T18:51:20Z"
updated: "2026-11-15T15:09:25Z"
tags: ["自旋-动量锁定", "铁磁体", "DFT计算", "d-wave/g-wave", "YVO3", "MnTe", "相对论效应", "反常霍尔"]
related: ["Berry curvature", "MnPS3", "Rashba效应", "arpes", "general-berry-mnps3-rashba-20260816", "二次谐波产生", "反常霍尔效应", "强场超快", "强场超快光学", "相干声子", "自旋劈裂", "自旋泵浦", "超快磁光"]
source_raw: "2026-2602.13768-relativistic-spin-momentum-locking-in-ferromagnets.md"
growth_stage: "growing"
confidence: 0.5
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Relativistic spin-momentum locking in ferromagnets

## 林赛的理解

我注意到这篇 Gong、Fakhredine、Autieri 的工作是与我之前一份 NSFC 提案（general-berry-mnps3-rashba-20260816）相关的，标注分数 0.86 不算低。从摘要级描述看，它的核心命题是用第一性原理（DFT）证明**铁磁体中"自旋-动量锁定"本质上是一种相对论效应**，并在 YVO₃ 和 MnTe 这两种截然不同的磁有序体系上验证了这一点——一个是我熟悉的关联氧化物（YVO₃ 是钙钛矿型莫特绝缘体），另一个是当代磁性拓扑材料研究里绕不开的候选（MnTe 是 altermagnet 的标杆之一）。

对我所在的强场超快光学方向来说，这篇的关键价值在于：当我们用飞秒激光脉冲在铁磁体里驱动超快退磁或光诱导自旋流时，电子被激发到非平衡态，其自旋-动量耦合的"对称性指纹"（d-wave / g-wave 等角动量通道分量）会直接决定哪些动量方向的电子能更有效地贡献反常霍尔电流、二次谐波产生、以及时间分辨 ARPES 能看到的瞬时自旋纹理。所以这里的"锁定"不只是基态概念，而是超快过程中**自旋极化泵浦方向与电子群速度方向**的耦合规则。

不过原始材料只有摘要级元数据，正文/方法/数值都没给，我需要在读到 PDF 后才能补全判断。

## 核心要点

- **核心命题**：铁磁体中的自旋-动量锁定（spin-momentum locking）被明确归因于相对论效应（自旋-轨道耦合），并通过 DFT 计算给出证明。
- **体系选择**：YVO₃（关联钙钛矿氧化物，铁磁/反铁磁莫特体系）和 MnTe（磁性化合物，altermagnet 候选）—— 选取两个**磁性对称性不同**的体系做对比验证。
- **关键特征**：两种材料都展示出 **d-wave 与 g-wave 角动量通道分量的混合**——意味着自旋-动量锁定并非单一对称性主导，而是高阶角动量通道共存。
- **方法学**：基于密度泛函理论（DFT）的电子结构计算；具体交换关联泛函、是否含 SOC 的对照计算细节、是否使用 Wannier 紧束缚下采样等方法信息尚未在原始材料中给出。
- **已挂载去向**：已被引入 "general-berry-mnps3-rashba-20260816" 提案的文献池，提示与 Berry curvature / Rashba / MnPS3 三条线索都有关联。

## 实验/研究关联

与我组工作的几条具体对接点：

1. **强场超快退磁 → 非平衡自旋纹理**  
   在 YVO₃ 这类 Mott 体系中，飞秒激光驱动的超快退磁过程里电子被瞬时"加热"到高能态，其自旋-动量锁定的对称性（d-wave + g-wave 混合）会调制相干声子与自旋波的耦合通道。如果能在 TR-ARPES 或时间分辨二次谐波上分辨 d-wave / g-wave 贡献，就能区分不同对称性通道的退磁时间常数。

2. **MnTe / MnPS₃ 家族对比**  
   MnTe 被归为 altermagnet，其自旋劈裂在动量空间具有 d-wave/g-wave 等的对称性；MnPS₃ 是反铁磁范德华材料，被我们用作对比。这篇给出 MnTe 的自旋-动量锁定 DFT 描述，正好补齐我们做 Rashba / altermagnet 对照时的"基态参考谱"。

3. **反常霍尔与自旋泵浦**  
   d-wave/g-wave 混合特征直接影响反常霍尔电导的动量空间分布函数（σ_xy(k)），对我们在异质结中泵浦-探测自旋流的工作有直接参考意义——尤其是当我们需要判断"观测到的霍尔信号到底来自界面 Rashba 还是体相 altermagnet 自旋劈裂"这一类歧义性问题时。

4. **二次谐产生（SHG）的对称性筛选**  
   YVO₃ 是 SHG 实验中常被用来探测磁对称性破缺的体系（Cr³⁺ 自旋有序改变 SHG 选择定则）。如果 DFT 预言的 d-wave/g-wave 混合能在 SHG 极化分析中被区分，将是连接第一性原理与超快磁光学的直接桥梁。

## 开放问题

- **原始材料严重不完整**：摘要字段为空，方法、数值、k 空间分辨的自旋纹理图、是否包含 Berry curvature 计算都没有。需要获取 PDF / arxiv 全文（arxiv_id: 2602.13768）后重写本笔记。
- **"相对论"的精确含义**：是说必须包含完整 SOC？还是仅在标量相对论（scalar-relativistic）下就有，但全相对论（全四点 Dirac）下出现新分量？这关系到在轻元素体系中的可推广性。
- **d-wave / g-wave 共存的物理起源**：是晶体对称性（点群）强制要求，还是自旋-轨道矩阵元在动量空间的选择规则自然涌现？这一区分对**预言新材料**非常重要。
- **温度与磁性相变**：YVO₃ 在低温下有 T_N ≈ 77 K 的反铁磁有序和 ~114 K 的结构相变，DFT 计算在哪个磁基态下做的？是否考虑了磁畴平均？这会显著改变 d-wave / g-wave 的相对权重。
- **超快可观测性**：自旋-动量锁定是基态属性，激光激发后多久、多大程度上保留？这个非平衡寿命直接决定我们能否在 TR-ARPES 上"拍到"它——目前缺乏理论或实验的时标估计。
- **与 altermagnet 文献的关系**：近期关于 altermagnet 的若干工作（Šmejkal, Ahn 等）已经从对称性分类角度给出了自旋劈裂的 d/g/i-wave 枚举，本文的 DFT 结果是否与之定量吻合？这关系到分类学是否被实际材料验证。

## 来源
- 原始材料：2026-2602.13768-relativistic-spin-momentum-locking-in-ferromagnets.md
- 蒸馏时间：2026-09-29T18:51:20Z
- arXiv ID：2602.13768
- 已挂载提案：general-berry-mnps3-rashba-20260816（NSFC-强场超快）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：DFT 证明铁磁体自旋-动量锁定的相对论起源（YVO₃ 与 MnTe 双体系验证）

**原理**：以第一性原理 DFT 证明铁磁体中的自旋-动量锁定本质上是相对论效应（自旋-轨道耦合），并在 YVO₃（关联钙钛矿莫特体系）与 MnTe（altermagnet 候选）两个磁性对称性不同的体系上验证——两种材料都展示 d-wave 与 g-wave 角动量通道分量的混合，即自旋-动量锁定并非单一对称性主导而是高阶角动量通道共存。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 体系 | YVO₃（关联钙钛矿氧化物）+ MnTe（altermagnet 候选）；两体系均呈 d-wave 与 g-wave 通道混合 | 核心要点 |

**适用边界**：摘要字段为空（方法/数值/k 空间自旋纹理/Berry curvature 计算均缺失，需 PDF 后重写笔记）；'相对论'的精确含义（完整 SOC vs 标量相对论）未明；YVO₃ 的 T_N≈77 K 反铁磁与 ~114 K 结构相变下 DFT 磁基态选取未说明；自旋-动量锁定的非平衡寿命（超快可观测性）无时标估计。
**代表作**：铁磁体自旋-动量锁定相对论起源（Gong/Fakhredine/Autieri，本文，arXiv 2602.13768，deepXiv 0.86）。
*方法卡回补 2026-09-29*

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry curvature]]
- [[MnPS3]]
- [[Rashba效应]]
- [[arpes]]
- [[general-berry-mnps3-rashba-20260816]]
- [[二次谐波产生]]
- [[反常霍尔效应]]
- [[强场超快]]
- [[强场超快光学]]
- [[相干声子]]
- [[自旋劈裂]]
- [[自旋泵浦]]
- [[超快磁光]]
<!-- /linsai-wikilinks -->
