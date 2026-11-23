---
title: "From Chern to Winding: Topological Invariant Correspondence in the Reduced Haldane Model"
type: "papers"
created: "2026-11-18T11:04:22Z"
updated: "2026-11-18T11:20:36Z"
tags: ["拓扑不变量", "Haldane模型", "SSH模型", "边缘态", "维度约化"]
related: ["Berry 曲率", "Chern数", "SSH绕数", "强场超快", "强场驱动", "手性边缘态", "拓扑相变", "拓扑边缘态"]
source_raw: "2025-2505.20472-from-chern-to-winding-topological-invariant-correspondence-i.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# From Chern to Winding: Topological Invariant Correspondence in the Reduced Haldane Model

## 林赛的理解
这篇工作做的是我一直关注的事：把二维拓扑不变量在一维截面上给出严格、可解析的对应。作者对 Haldane 模型锯齿边界纳米条做了精确解析，通过维度约化把它映射为动量依赖的扩展 SSH 链，证明约化模型的绕数 ν 严格重现母体的 Chern 数。对我们组的意义在于：高谐波产生的拓扑响应（如谐波手性、贝里曲率驱动的发射）需要一个能在实空间、有限体系中直接计算的不变量，绕数恰恰比 Chern 数更贴近纳米条/ribbon 的几何。闭式的边缘态波函数与色散、临界动量 kc 以及相边界 M = ±3√3λ，也为我们在拓扑材料（如转角双层、Haldane 型光晶格）中设计强场实验提供了干净的解析基准。这项工作已被 general-ssh-weyl-20260920 提案引用，说明 SSH–Weyl 主线与它有直接接口。

## 核心要点
- **体—边界对应的解析实现**：Haldane 模型锯齿边界纳米条可精确约化为动量依赖的扩展 SSH 链，边缘态由 SSH 型绕数刻画。
- **不变量对应**：约化一维模型的绕数 ν 严格重现母体二维模型的 Chern 数（"From Chern to Winding"）。
- **闭式结果**：边缘态波函数与色散、临界动量 kc 均有解析表达式；拓扑相边界为 M = ±3√3λ。
- **物理机制**：Haldane 质量（时间反演破缺）与 Semenoff 质量（反演破缺）的竞争驱动拓扑相变。

## 实验/研究关联
- 已被提案 general-ssh-weql（general-ssh-weyl-20260920）引用，可作为该提案中 SSH 链—Weyl 体系不变量对应部分的解析支撑。
- 对强场超快实验的启示：拓扑边缘态的闭式波函数便于估算强激光下边缘态对高次谐波产率与手性的贡献；TRS 破缺项（Haldane 质量）与圆偏振驱动的等效破缺之间可能存在可探测的对照。
- 项目归属：NSFC-强场超快。

## 开放问题
- 约化映射对一般边界（非锯齿）是否同样严格？绕数—Chern 对应在多大程度上依赖边界细节？
- 扩展 SSH 链的动量依赖性在强场驱动（周期性 Floquet 调制）下如何影响绕数与边缘态稳定性？
- 该解析框架能否推广到三维 Weyl 体系（切线绕数—Chern 数对应），与我们的 SSH–Weyl 提案直接衔接？
- 摘要级信息未给出具体波函数形式与数值验证，需获取全文核验解析细节。

## 来源
- 原始材料：2025-2505.20472-from-chern-to-winding-topological-invariant-correspondence-i.md
- 蒸馏时间：2026-11-18T11:04:22Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：从 Chern 到绕数：约化 Haldane 模型的拓扑不变量对应（Haldane 模型锯齿边界纳米条精确解析→维度约化映射为动量依赖扩展 SSH 链：**约化模型的绕数 ν 严格重现母体二维模型的 Chern 数**（体-边对应的解析实现）；闭式边缘态波函数与色散、临界动量 kc、相边界 M = ±3√3λ 均有解析表达式）

**原理**：对 Haldane 模型锯齿边界纳米条做精确解析：通过维度约化把它映射为动量依赖的扩展 SSH 链、边缘态由 SSH 型绕数刻画——证明约化一维模型的绕数 ν 严格重现母体二维模型的 Chern 数（「From Chern to Winding」= 体-边对应的解析实现）；闭式结果：边缘态波函数与色散、临界动量 kc 均有解析表达式、拓扑相边界为 M = ±3√3λ；物理机制：Haldane 质量（时间反演破缺）与 Semenoff 质量（反演破缺）的竞争驱动拓扑相变；意义：高谐波产生的拓扑响应（谐波手性/Berry 曲率驱动发射）需要能在实空间有限体系直接计算的不变量——绕数比 Chern 数更贴近纳米条/ribbon 几何。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 相边界 | M = ±3√3λ（Haldane 质量 vs Semenoff 质量竞争驱动拓扑相变；解析细节与数值验证未载，摘要级无 PDF） | 核心要点（摘要级） |

**适用边界**：摘要级来源（无 PDF）——约化映射对一般边界（非锯齿）是否同样严格、绕数-Chern 对应在多大程度上依赖边界细节待核；扩展 SSH 链动量依赖性在强场驱动（周期性 Floquet 调制）下对绕数与边缘态稳定性的影响未知；解析框架能否推广到三维 Weyl 体系（切线绕数-Chern 数对应）与 ssh-weyl 提案直接衔接待探索；应用启示：边缘态闭式波函数便于估算强激光下边缘态对 HHG 产率与手性的贡献、TRS 破缺项与圆偏振驱动等效破缺可能存在可探测对照。
**代表作**：arXiv:2505.20472（2025），From Chern to Winding: Topological Invariant Correspondence in the Reduced Haldane Model（绕数-Chern 对应解析实现素材；ssh-weyl 提案引用）
*方法卡回补 2026-11-18*

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry 曲率]]
- [[Chern数]]
- [[SSH绕数]]
- [[强场超快]]
- [[强场驱动]]
- [[手性边缘态]]
- [[拓扑相变]]
- [[拓扑边缘态]]
<!-- /linsai-wikilinks -->
