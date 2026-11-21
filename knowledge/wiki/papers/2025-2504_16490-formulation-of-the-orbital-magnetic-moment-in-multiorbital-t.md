---
title: "Formulation of the orbital magnetic moment in multiorbital tight-binding models: Application to the inverse Faraday effect"
type: "papers"
created: "2026-11-16T11:24:07Z"
updated: "2026-11-16T11:28:08Z"
tags: ["papers", "轨道磁矩", "逆法拉第效应", "Floquet", "紧束缚模型", "Wannier"]
related: ["Floquet engineering", "Schrieffer-Wolff transformation", "general-floquet-20261107", "inverse Faraday effect", "orbital magnetism", "强场超快", "强场超快磁学", "拓扑绝缘体", "超快磁光"]
source_raw: "2025-2504.16490-formulation-of-the-orbital-magnetic-moment-in-multiorbital-t.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Formulation of the orbital magnetic moment in multiorbital tight-binding models: Application to the inverse Faraday effect

## 林赛的理解
这篇工作直接戳中我们强场超快项目里一个长期存在的模糊地带：用圆偏振飞秒激光泵浦材料产生静态磁化的逆法拉第效应（IFE），我们实验上通常默认响应主要来自自旋或宏观自由载流子，而这篇理论工作明确指出——在多轨道体系中，轨道磁矩响应显著大于自旋磁矩，且各轨道贡献量级相当。这对我们解读超快全光磁翻转（AO-MFM）实验中的瞬态磁化信号很有警示意义：测到的磁化可能主要是轨道起源，尤其在 s-p 杂化显著的体系（半导体、拓扑材料界面）中。此外，作者指出 Wannier 轨道自身的电偶极矩对轨道磁矩有贡献——这是常规晶格轨道磁矩公式里被丢掉的项，说明我们过去基于单带/单轨道模型估计 IFE 的量级可能系统性偏差。

## 核心要点
- 建立了多轨道紧束缚模型中轨道磁矩的完整理论表述，明确电偶极（位置算符）在多轨道基组下的非对角角色。
- 证明总轨道磁矩可分解为若干贡献，其中 Wannier 轨道电偶极矩的贡献是被常规晶格体系轨道磁矩表达式忽略的项。
- 以 s-p 紧束缚体系作为 IFE 最小模型：
  - 用 Schrieffer-Wolff 变换解析地厘清各磁矩贡献的物理起源；
  - 用 Floquet 形式主义数值验证，解析与数值在同一基准上定量一致。
- 主要结论：轨道磁矩响应显著大于自旋磁矩响应；轨道磁矩各贡献量级相当，轨道自由度在 IFE 中是本质性的。
- 已发表于 Phys. Rev. B 112, 155134 (2025)；arXiv:2504.16490。

## 实验/研究关联
- **NSFC-强场超快项目**：IFE 是我们圆偏振强场泵浦实验的核心物理之一；本文提示实验建模需包含轨道磁化通道而非仅自旋通道。
- **general-floquet-20261107 提案**：本文的 Floquet 数值方法 + Schrieffer-Wolff 解析的双轨策略，是我们撰写 Floquet 提案时可借鉴的方法学模板——解析分解提供物理解释，Floquet 提供定量基准。
- 对我们用 Wannier 化紧束缚模型拟合材料再做光致磁化预测的流程：需检查是否遗漏了轨道内电偶极矩项，否则 IFE 量级估计可能有系统误差。
- 与超快磁光测量（瞬态 Kerr/Faraday）的解读相关：磁光信号中轨道与自旋权重的分解需重新审视。

## 开放问题
- 结论基于 s-p 最小模型；在真实材料（如 GdFeCo、重金属/铁磁界面、拓扑绝缘体表面态）中各轨道贡献的相对量级是否仍“量级相当”？
- 强场极限下（超出微扰/Floquet 弱场范围）轨道磁矩响应是否饱和、出现多光子共振增强？我们的实验区间是否落在本文理论适用范围内？
- 电偶极矩贡献项是否存在可以实验区分的特征（如轨道对称性依赖、偏振螺旋依赖的选择定则）？
- 与声子/耗散、退相干耦合下瞬态轨道磁矩的寿命如何——对飞秒时间分辨测量可观测性的影响尚不清楚。
- 摘要级元数据未给出具体数值结果，需获取全文（has_pdf: false）做精读补全。

## 来源
- 原始材料：2025-2504.16490-formulation-of-the-orbital-magnetic-moment-in-multiorbital-t.md
- 蒸馏时间：2026-11-16T11:24:07Z

<!-- linsai-wikilinks -->
## 关联概念

- [[Floquet engineering]]
- [[Schrieffer-Wolff transformation]]
- [[general-floquet-20261107]]
- [[inverse Faraday effect]]
- [[orbital magnetism]]
- [[强场超快]]
- [[强场超快磁学]]
- [[拓扑绝缘体]]
- [[超快磁光]]
<!-- /linsai-wikilinks -->

## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：多轨道紧束缚模型中轨道磁矩的完整表述及逆法拉第效应应用（Wannier 轨道自身电偶极矩对轨道磁矩有贡献——常规晶格体系轨道磁矩公式被丢掉的项；IFE 最小 s-p 模型：Schrieffer-Wolff 解析分解 + Floquet 数值验证双轨定量一致——**轨道磁矩响应显著大于自旋磁矩、各轨道贡献量级相当**）

**原理**：建立多轨道紧束缚模型中轨道磁矩的完整理论表述：明确电偶极（位置算符）在多轨道基组下的非对角角色——总轨道磁矩可分解为若干贡献、其中 Wannier 轨道电偶极矩的贡献是被常规晶格体系轨道磁矩表达式忽略的项；以 s-p 紧束缚体系作 IFE（逆法拉第效应）最小模型：用 Schrieffer-Wolff 变换解析厘清各磁矩贡献物理起源 + Floquet 形式主义数值验证（解析与数值同基准定量一致——方法学双轨模板）；主要结论：轨道磁矩响应显著大于自旋磁矩响应、各轨道贡献量级相当（轨道自由度在 IFE 中是本质性的）。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 发表信息 | Phys. Rev. B 112, 155134 (2025)；arXiv:2504.16490（具体数值结果未载，摘要级 has_pdf false） | 核心要点 |

**适用边界**：结论基于 s-p 最小模型——真实材料（GdFeCo/重金属铁磁界面/拓扑绝缘体表面态）中各轨道贡献是否仍「量级相当」待验证；强场极限（超出微扰/Floquet 弱场范围）下轨道磁矩响应是否饱和/多光子共振增强待测；电偶极矩贡献项的实验区分特征（轨道对称性/偏振螺旋选择定则）待发展；声子/耗散/退相干耦合下瞬态轨道磁矩寿命（飞秒可观测性）未明；实验警示：IFE 实验建模需包含轨道磁化通道而非仅自旋通道（AO-MFM 瞬态磁化信号可能主要是轨道起源，s-p 杂化显著体系尤甚）——Wannier 化紧束缚拟合流程若遗漏轨道内电偶极矩项则 IFE 量级估计有系统误差。
**代表作**：arXiv:2504.16490（PRB 112, 155134，2025），Formulation of the orbital magnetic moment in multiorbital tight-binding models（轨道磁矩完整表述+IFE 轨道主导结论+双轨方法学模板素材；floquet 提案引用）
*方法卡回补 2026-11-16*
