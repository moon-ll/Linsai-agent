---
title: "2024-PhysRevLett_133_206401-large-band-splitting-in-g-wave-altermagnet-crsb"
type: "papers"
created: "2026-09-26T12:58:10Z"
updated: "2026-11-15T15:09:24Z"
tags: []
related: ["CrSb", "arpes", "general-order-parameter-ultrafast-readout-20260727", "交变磁体", "光致相变", "强场超快", "强场超快光学", "自旋劈裂", "非线性光学"]
source_raw: "2024-PhysRevLett.133.206401-large-band-splitting-in-g-wave-altermagnet-crsb.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
digest_level: "abstract"
---

• ---
  title: "Large Band Splitting in g-Wave Altermagnet CrSb（CrSb 交变磁体大能带劈裂）"
  type: papers
  created: "2026-09-26T12:57:47Z"
  updated: "2026-09-26T12:57:47Z"
  tags: ["交变磁体", "altermagnet", "CrSb", "自旋劈裂", "ARPES", "DFT", "磁性材料"]
  related: ["交变磁体", "自旋电子学", "时间反演对称破缺", "超快磁动力学", "序参量超快读出"]
  source_raw: "2024-PhysRevLett.133.206401-large-band-splitting-in-g-wave-altermagnet-crsb.md"
  growth_stage: "growing"
  confidence: 0.7
  auto_grown: true
  review_status: "pending"
  ---

  # Large Band Splitting in g-Wave Altermagnet CrSb（PRL 133, 206401, 2024）

  ## 林赛的理解

  我读这篇 PRL 的兴趣点很直接：CrSb 是目前报道的交变磁体（altermagnet）中自旋劈裂最大的体系之一——最大劈裂约 1.2 eV，奈尔温度超过 700 K。这意味着它是一种**室温以上稳定、自旋劈裂量可与费米面尺度直接对话**的磁性材料。对我做强场超快光学的人来说，这类材料是"序参量—电子结构耦合"的绝佳试验场：自旋劈裂能带结构直接决定了光激发载流子的自旋选择性，而 700 K 以上的奈尔温度意味着它不会像许多低维磁体那样在激光加热下立刻垮掉，这对超快泵浦实验是可贵的鲁棒性。该文被我们的 order-parameter ultrafast readout 课题引用，正是因为它为"用超快光学读出交变磁体的自旋序"提供了材料平台候选。

  ## 核心要点

  - **g-wave 交变磁体的大劈裂**：CrSb 表现出约 1.2 eV 的最大自旋劈裂，是交变磁体家族中非常突出的数值。
  - **高温磁性**：奈尔温度高于 700 K，远高于室温，排除了"磁性只在低温才存在"的实用性质疑。
  - **对称性证据链完整**：DFT 计算与 ARPES 角分辨光电子能谱相互印证，确认了 g-wave（d/g 型动量依赖）自旋劈裂的对称特征。
  - **狄拉克点动量空间分布**：实验观测到狄拉克点在动量空间中的分布，与交变磁体"动量依赖、净磁矩为零"的理论图像一致。
  - 注：原始材料仅提供摘要级信息（约 1.2 eV 劈裂、>700 K 奈尔温度、DFT+ARPES 证据），具体晶格结构、掺杂、样品制备等细节未给出，本笔记不作延伸。

  ## 实验/研究关联

  - **与"序参量超快读出"课题（general-order-parameter-ultrafast-readout-20260727）的直接关联**：交变磁体的自旋劈裂能带本身就是序参量（交错磁序）的谱学指纹。一个自然的超快读出思路是：用 THz 或近红外泵浦扰动磁序，用瞬态反射/透射或时间分辨光电子能谱追踪劈裂能带（特别是狄拉克点附近的谱权重）的瞬态演化。CrSb 的 700 K 奈尔温度为强泵浦下的温升裕量提供了保障。
  - **与强场 HHG / 非线性光学**：大自旋劈裂 + 时间反演对称破缺的结合，意味着奇偶阶谐波对磁序的敏感度可能与常规铁磁体不同，g-wave 的动量结构可能在谐波偏振结构中留下可识别印记——这是一个值得推导但本笔记暂不展开的方向。

  ## 开放问题

  - 摘要级材料未给出劈裂的具体动量位置与带宽细节，超快探测应优先瞄准哪些 k 点需要读原文或跟进 ARPES 数据。
  - 交变磁体净磁矩为零，常规磁光 Kerr/Faraday 信号可能很弱——超快读出需要验证何种光学观测量对交错磁序最敏感。
  - 强场泵浦是否会诱导磁序以外的效应（如光致相变、热致奈尔温度邻近动力学）掩盖序参量信号，需要实验上的对照设计。

  ## 来源
  - 原始材料：2024-PhysRevLett.133.206401-large-band-splitting-in-g-wave-altermagnet-crsb.md
  - 蒸馏时间：2026-09-26T12:57:47Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：g 波交变磁体 CrSb 的大能带劈裂——约 1.2 eV 最大自旋劈裂 + 奈尔温度 >700 K，DFT 与 ARPES 相互印证（PRL 2024）

**原理**：CrSb 为目前报道的交变磁体中自旋劈裂最大的体系之一：最大劈裂约 1.2 eV（可与费米面尺度直接对话的量级）、奈尔温度超过 700 K（远高于室温——排除'磁性只在低温存在'的质疑，为超快泵浦实验提供温升裕量）；对称性证据链完整：DFT 计算与 ARPES 相互印证，确认 g-wave（d/g 型动量依赖）自旋劈裂的对称特征；观测到狄拉克点在动量空间中的分布，与交变磁体'动量依赖、净磁矩为零'的理论图像一致。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 关键数值 | 最大自旋劈裂约 1.2 eV；奈尔温度 > 700 K；g-wave 对称性（DFT + ARPES 互证） | 核心要点 |

**适用边界**：摘要级信息（本页自注'不作延伸'），劈裂的具体动量位置与带宽细节未给（超快探测优先瞄准哪些 k 点需读原文）；交变磁体净磁矩为零——常规磁光 Kerr/Faraday 信号可能很弱、何种光学观测量对交错磁序最敏感待验证；强场泵浦是否诱导磁序以外效应（光致相变/热致奈尔温度邻近动力学）掩盖序参量信号需对照设计。
**代表作**：Large Band Splitting in g-Wave Altermagnet CrSb（DFT + ARPES，PRL 133, 206401, 2024）
*方法卡回补 2026-10-04*

<!-- linsai-wikilinks -->
## 关联概念

- [[CrSb]]
- [[arpes]]
- [[general-order-parameter-ultrafast-readout-20260727]]
- [[交变磁体]]
- [[光致相变]]
- [[强场超快]]
- [[强场超快光学]]
- [[自旋劈裂]]
- [[非线性光学]]
<!-- /linsai-wikilinks -->
