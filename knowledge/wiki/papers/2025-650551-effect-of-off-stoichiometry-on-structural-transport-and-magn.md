---
title: "反铁磁 CrSb 中非化学计量比对结构、输运与磁性的影响"
type: "papers"
created: "2026-10-11T12:01:27Z"
updated: "2026-10-31T11:47:44Z"
tags: ["altermagnet", "CrSb", "off-stoichiometry", "ultrafast-magnetism", "order-parameter-readout"]
related: ["CrSb", "altermagnetism", "arpes", "general-order-parameter-ultrafast-readout-20260727", "interstitial-defects", "non-equilibrium-order-parameter", "strong-field-THz-driving", "强场超快", "强场超快光学", "自旋劈裂"]
source_raw: "2025-650551-effect-of-off-stoichiometry-on-structural-transport-and-magn.md"
growth_stage: "growing"
confidence: 0.6
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# 反铁磁 CrSb 中非化学计量比对结构、输运与磁性的影响

## 林赛的理解
作为强场超快光学 PI，我看这篇论文的切入点不是凝聚态细节本身，而是它能否告诉我如何去**光学读出** altermagnetic 序参量。CrSb 这类 alternagnet 在外场下应具有比传统反铁磁更丰富的 THz/自旋电子学响应，且其"实空间各向异性、自旋空间各向异性"的耦合方式天然适合用强场作为瞬时对称性破缺探针。这篇 DESY 团队的工作点出：CrSb 的化学计量比偏差（Cr 过量）会让间隙 Cr 占据 2d 位点并形成低自旋磁团簇，进而打开 altermagnetic 能隙。这意味着 altermagnetic 序参量本身对缺陷高度敏感，因此我组在用泵浦-探测去"读"它的瞬态演化时，必须把样品质量与名义化学比作为零先验坐标，否则所测到的"动力学"很可能只是缺陷相关团簇的局域响应而非本征 alternagnet 响应。提案 general-order-parameter-ultrafast-readout-20260727 把 CrSb 列为候选材料，本文对样品批次筛选是直接的技术依据。

## 核心要点
- 研究对象：反铁磁（altermagnetic）CrSb，聚焦 Cr 过量这一非化学计量比条件下的多体响应。
- 结构层面：多余的 Cr 进入间隙位，明确占据 2d Wyckoff 位置，形成间隙式缺陷。
- 磁性层面：间隙 Cr 在 2d 位上聚合，形成**低自旋磁团簇**；这意味着 CrSb 的本征磁基态并非简单的反铁磁二亚格子序，而存在缺陷诱导的局域磁化重排。
- 输运/能带层面：伴随磁团簇形成，体系出现**altermagnetic 能隙**——即 alternagnet 的自旋劈裂型能隙在化学比条件下被打开或修饰。
- 综合效应：化学计量比偏差同时改写了结构对称性、磁基态与电子能带结构，是 alternagnet 序参量稳定性研究的关键变量。

## 方法亮点
- 多性质联立：把结构（衍射确认 2d 占位）、输运（电输运反映能隙）与磁性（磁矩/有序化）三类表征在同一批样品上自洽比对，使缺陷-磁性-电子结构之间的因果链相对清晰。
- 化学比作为连续调控变量：利用名义化学比偏差做"原位的"序参量调控，比外加掺杂或压力更贴近真实生长窗口。

## 实验/研究关联
- 与我组提案 **general-order-parameter-ultrafast-readout-20260727** 直接相关：CrSb 是 alternagnet 序参量超快读出的候选体系之一。本文结论意味着，在做 THz/强场泵浦-光学探测实验前，**必须**对样品做名义化学比和无序度的预表征；否则瞬态信号无法归因。
- 与 NSFC-强场超快项目方向契合：强场（高场 THz 或中红外）作为瞬态对称性破缺工具，对于在 alternagnet 中驱动和读出自旋-晶格耦合动力学是合适的；本工作指出间隙 Cr 的存在会产生局域低自旋团簇，这本身就是强场泵浦可瞄准的"亚稳局域序"特征。
- 缺陷与序参量稳定性的关联：可借鉴本文思路，把 alternagnet 序参量在不同无序度下的"鲁棒性曲线"作为超快读出实验设计的依据——只在能隙清晰、化学比接近标称的样品上做时间分辨测量，把含缺陷样品留给静态表征。

## 开放问题
- 原文摘要级别信息不足以判断 2d 间隙 Cr 的**浓度阈值**（从哪一化学比开始低自旋团簇主导磁响应），以及能隙是否随 Cr 过量单调演化——这对选择泵浦-探测样品批次至关重要。
- 低自旋磁团簇的**时间尺度**未给出：这类局域磁团簇在飞秒-皮秒尺度上是否稳定、能否被强场 THz 瞬时翻转，是 alternagnet 序参量超快读出可行性的关键。
- 强场下间隙 Cr 的晶格局域稳定性是否会被破坏、是否会引起**非平衡化学比涨落**——这对瞬态谱学（如 time-resolved XMLD 或 tr-ARPES）解释造成额外复杂度，但本工作未触及。
- 缺乏本工作的具体实验参数（如温度区间、磁场范围、能隙数值、晶体结构精修数据），需进一步获取 PDF 后再补充判断。

## 来源
- 原始材料：2025-650551-effect-of-off-stoichiometry-on-structural-transport-and-magn.md
- 蒸馏时间：2026-10-11T12:01:27Z
- 关联提案：general-order-parameter-ultrafast-readout-20260727
- 关联项目：NSFC-强场超快
- arXiv ID：650551


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：CrSb 非化学计量比的结构–输运–磁性联立表征（间隙 Cr 缺陷效应）

**原理**：在反铁磁（交变磁）CrSb 中引入 Cr 过量的名义化学比偏差，同一批样品上联立结构（衍射确认占位）、输运（电输运反映能隙）与磁性（磁矩/有序化）三类表征。核心发现：多余 Cr 进入间隙 2d Wyckoff 位并聚合形成低自旋磁团簇，伴随交变磁能隙的打开/修饰——化学计量比同时改写结构对称性、磁基态与电子结构，是序参量稳定性研究的关键变量。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 研究对象 | 交变磁 CrSb（Cr 过量非化学计量条件） | 核心要点 |
| 缺陷占位 | 间隙 Cr 占据 2d Wyckoff 位置 | 核心要点 |
| 磁结构 | 间隙 Cr 聚合形成低自旋磁团簇 | 核心要点 |
| 电子结构 | 伴随团簇形成出现交变磁能隙 | 核心要点 |

**适用边界**：摘要级来源，温度区间/磁场范围/能隙数值/结构精修数据均未给出；2d 间隙 Cr 的浓度阈值（团簇主导磁响应的起始化学比）未知；低自旋团簇的飞秒-皮秒稳定性与强场 THz 可翻转性未测——泵浦-探测样品批次筛选前必须预表征化学比与无序度。
**代表作**：DESY team (2025), Effect of off-stoichiometry on structural, transport and magnetic properties of altermagnetic CrSb（页面条目 650551）
*方法卡回补 2026-10-11*

<!-- linsai-wikilinks -->
## 关联概念

- [[CrSb]]
- [[altermagnetism]]
- [[arpes]]
- [[general-order-parameter-ultrafast-readout-20260727]]
- [[interstitial-defects]]
- [[non-equilibrium-order-parameter]]
- [[strong-field-THz-driving]]
- [[强场超快]]
- [[强场超快光学]]
- [[自旋劈裂]]
<!-- /linsai-wikilinks -->
