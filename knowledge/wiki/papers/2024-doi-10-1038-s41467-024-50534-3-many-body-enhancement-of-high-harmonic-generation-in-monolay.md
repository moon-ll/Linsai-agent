---
title: "Many-body enhancement of high-harmonic generation in monolayer MoS2"
type: "papers"
created: "2026-11-22T10:50:52Z"
updated: "2026-11-22T11:00:36Z"
tags: ["HHG", "MoS2", "多体效应", "激子", "Berry曲率", "TD-aGW"]
related: ["Berry 曲率", "二维材料", "强场超快", "强场超快光学", "扭转电子学", "扭转电子学强场探针", "高次谐波产生"]
source_raw: "2024-doi-10-1038-s41467-024-50534-3-many-body-enhancement-of-high-harmonic-generation-in-monolay.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Many-body enhancement of high-harmonic generation in monolayer MoS2

## 林赛的理解
这篇是我 NSFC-强场超快方向上必须精读的一篇：它把二维材料 HHG 中长期争论的“多体激子效应 vs 单粒子能带图像”问题给出了定量答案。我们组做 moiré 体系的强场探针方案时，最怕的就是把 HHG 谱简单当作能带结构/Berry 曲率的直接读出，而这篇工作表明激子屏蔽与 Berry 曲率是交织在一起的——垂直方向非单调的 HHG 响应正是这种纠缠的直接证据。作者用的是 TD-aGW（含时 ab initio GW），这是目前处理二维体系动态屏蔽最严谨的一档方法，值得作为我们理论对标的选择。

## 核心要点
- 研究对象：单层 MoS₂ 的高次谐波产生（HHG），重点在垂直方向的非单调谐波响应。
- 核心结论：多体激子效应与 Berry 曲率共同作用（交织），是垂直方向非单调 HHG 的关键机制；仅用单粒子能带图像不足以解释。
- 方法：TD-aGW（含时从头算 GW），可处理激发态动力学中的动态屏蔽与激子效应。
- 发表：Nature Communications 15, 6228 (2024)，无 arXiv 预印本，仅正式版。
- 团队：Lee, Yue, Gaarde（LSU 强场理论），Chan, Qiu（二维多体理论），理论与强场 HHG 领域的强强组合。

## 实验/研究关联
- 直接关联我们的 proposal "general-moire-strong-field-probe-20260726"：若用强场 HHG 探测 moiré 体系，必须考虑多体激子对谐波特性的重塑，而非只读几何相位/能带。
- Gaarde 组是我们 HHG 理论对标的重要参考；TD-aGW 可作为我们分析二维极限下屏蔽长度依赖的基准方法。
- 对我们的启示：在解析 HHG 谱前，需先评估激子结合能与驱动场峰值的相对尺度。

## 开放问题
- TD-aGW 的计算代价如何？能否推广到更大周期体系（如 moiré 超晶格）？
- 激子效应对平行 vs 垂直偏振 HHG 的贡献是否可分离，从而设计“激子敏感”的探测方案？
- 层间堆叠/扭转是否进一步改变这种多体增强的尺度规律？
- 原始笔记仅有摘要级信息，具体数值与图像细节待获取正式版全文后补充。

## 来源
- 原始材料：2024-doi-10-1038-s41467-024-50534-3-many-body-enhancement-of-high-harmonic-generation-in-monolay.md
- DOI: https://doi.org/10.1038/s41467-024-50534-3
- 蒸馏时间：2026-11-22T10:50:52Z

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry 曲率]]
- [[二维材料]]
- [[强场超快]]
- [[强场超快光学]]
- [[扭转电子学]]
- [[扭转电子学强场探针]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
