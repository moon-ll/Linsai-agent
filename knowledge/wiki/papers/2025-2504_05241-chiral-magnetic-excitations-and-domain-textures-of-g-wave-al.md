---
title: "Chiral magnetic excitations and domain textures of g-wave altermagnets"
type: "papers"
created: "2026-10-02T04:54:35Z"
updated: "2026-11-12T01:48:07Z"
tags: ["altermagnet", "g-wave", "chiral-magnon", "CrSb", "MnTe", "domain-wall", "ultrafast-magnetics"]
related: ["CrSb", "altermagnet分类学", "交变磁体", "序参量超快读出", "强场 THz泵浦", "强场超快", "手性磁振子", "自旋劈裂"]
source_raw: "2025-2504.05241-chiral-magnetic-excitations-and-domain-textures-of-g-wave-al.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
used_by_proposals: ["general-order-parameter-ultrafast-readout-20260727"]
proposals_citations: "{'general-order-parameter-ultrafast-readout-20260727': ['adversarial-review']}"
---

# Chiral magnetic excitations and domain textures of g-wave altermagnets

## 林赛的理解

读到 Kravchuk 等人这篇 g 波 altermagnet（交变磁体）的磁激发理论工作时，我首先感到的是一种"正当其时"的兴奋。Altermagnet 作为与铁磁、反铁磁并列的第三类磁序被命名不过是两三年前的事，而 g 波子类（自旋劈裂在 k 空间呈现 l=4 角动量对称性，区别于已大量研究的 d 波子类）的磁激发谱学框架在本文才被给出，这对我们做强场超快的人来说是非常关键的一块拼图。

从超快光学的视角，我特别注意到摘要里给出的两条最硬的结论：

**第一**，CrSb（易轴 g 波原型）中 chiral magnon 的劈裂保持 g 波对称，且**每支携带 kink-magnons independent 的量子化磁矩**。这一点之所以打动我，是因为它给出了一个**与动量无关**的可观测标记：传统的反铁磁 magnons 两支完全补偿，零磁学计数；而 g 波 altermagnet 的两支虽然保持某种 Kramers 退简并，但每支都自带一个可被光学探针（time-resolved MOKE、THz 磁谱）直接读出的磁矩——这意味着我们不必去分辨单个 k 点的激发就能用一束超快脉冲读出"我现在激发的是 chiral plus 还是 minus"，这对我们的初探泵浦-探测构型极其友好。

**第二**，CrSb 畴壁本身具有**取向依赖的净磁化**。这是与传统 180° 反铁磁畴壁最本质的不同——传统 AF 畴壁不带净磁矩，因而是"光学不可见的"，而 g 波 CrSb 畴壁天然可被 Kerr 显微镜或 Faraday 扫时看见。这意味着 CrSb 畴壁不仅是一个静态序参量的边界，还是一个**本征带磁的可控自由度**。强场超快脉冲（特别是圆偏振的近单周期 THz 脉冲）能否可逆地翻转畴壁取向，是我们当前 NSFC 强场超快项目下"general-order-parameter-ultrafast-readout"提案想直接去问的问题，这篇文章把可问的问题具体化了。

MnTe 作为易面 g 波原型，其各向异性"改变了"劈裂——这个改变的具体含义（被压制、被重新分配、还是被反转）需要从全文确认。我会在拿到 PDF 后优先确认这一点。

## 核心要点

- **研究对象**：g 波 altermagnet 的磁激发谱与畴壁静态。
- **CrSb（易轴原型）**：chiral magnon 在动量空间中劈裂，但 g 波对称性在两支上均被保持；每支 chiral magnon 携带一个**与动量 k 无关的量子化磁矩**——这是本文最具可观测性的理论预言。
- **MnTe（易面原型）**：单轴各向异性改变了 chiral magnon 劈裂的结构（摘要层面仅到此，细节待全文）。
- **普适 g 波特征量**：作者提出一个同时包含能量与磁矩的标量（或矢量？）特征量，用于刻画 g 波谱（特征谱的"指纹"）。这意味着 g 波 altermagnet 的磁激发可被一个紧致量子化分度来标记。
- **CrSb 畴壁**：畴壁具有**取向依赖的净磁化**——这是与普通反铁磁反平行但畴壁传统 180° 序参量畴壁"中性"性质的根本区别，提供了天然带磁、可被超快光学读出的畴壁。

## 实验/研究关联

- **材料可行性**：CrSb 与 MnTe 都是已被实验合成的实际材料，前者是易轴 g 波原型，后者是易面 g 波原型。我们无需另找靶材，可直接以这两个体系为对象开展强场超快实验。
- **量子化磁矩的光学读出**：`k` 无关的量子化磁矩意味着 THz 磁谱（探测超快频率的 Faraday / Kerr 旋转）应能看到两条正磁谱分别贡献一个分立的磁振幅——这与之前对 d 波 altermagnet 的预期（动量依赖、可被带间跃迁调制）完全不同。需重新评估我对 altermagnet 磁振子谱学普遍特征的既有图像。
- **畴壁作为超快可控单元**：CrSb 畴壁带磁这一点，使畴壁从"被动物理对象"升级为"主动可写元件"。具体


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：g 波交变磁体手性磁振子谱与畴壁净磁化理论

**原理**：建立 g 波 altermagnet 磁激发谱学与畴结构理论框架。核心机制：CrSb（易轴原型）中 chiral magnon 两支在动量空间劈裂但 g 波对称性保持，每支携带与动量 k 无关的量子化磁矩——提供动量无关的可观测标记，可用 time-resolved MOKE/THz 磁谱整体读出；CrSb 畴壁具有取向依赖的净磁化（区别于传统 180° AFM 畴壁的电中性'光学不可见'），天然可被 Kerr/Faraday 显微读出。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 量子化磁矩 | 每支 chiral magnon 携带与动量 k 无关的量子化磁矩 | 核心要点 |
| 体系 | CrSb（易轴 g 波原型）、MnTe（易面 g 波原型） | 核心要点 |
| 普适特征量 | 同时包含能量与磁矩的 g 波特征量（谱'指纹'） | 核心要点 |

**适用边界**：摘要级：MnTe 易面单轴各向异性'改变'劈裂的具体方式（压制/重分配/反转）待全文；普适特征量是标量还是矢量未明；畴壁净磁化的取向依赖定量关系未给出。
**代表作**：Kravchuk et al., Chiral magnetic excitations and domain textures of g-wave altermagnets, arXiv:2504.05241 (2025)
*方法卡回补 2026-10-04*

<!-- linsai-wikilinks -->
## 关联概念

- [[CrSb]]
- [[altermagnet分类学]]
- [[交变磁体]]
- [[序参量超快读出]]
- [[强场 THz泵浦]]
- [[强场超快]]
- [[手性磁振子]]
- [[自旋劈裂]]
<!-- /linsai-wikilinks -->
