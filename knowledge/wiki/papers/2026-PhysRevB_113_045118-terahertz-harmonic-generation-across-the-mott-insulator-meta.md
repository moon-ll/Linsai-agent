---
title: "Terahertz harmonic generation across the Mott insulator-metal transition"
type: "papers"
created: "2026-09-29T10:57:12Z"
updated: "2026-11-15T15:09:21Z"
tags: ["THz-HHG", "强关联体系", "Mott相变", "稀土镍酸盐", "集体模式诊断", "三次谐波"]
related: ["Berry 曲率", "THz非线性光谱", "arpes", "transient quantum phase", "低能集体激发", "强关联材料非线性响应", "强场超快", "强场超快光学", "瞬态量子相变"]
source_raw: "2026-PhysRevB.113.045118-terahertz-harmonic-generation-across-the-mott-insulator-meta.md"
growth_stage: "growing"
confidence: 0.65
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Terahertz harmonic generation across the Mott insulator-metal transition

## 林赛的理解

这篇 PhysRevB 113, 045118 (2026) 的工作把稀土镍酸盐体系作为舞台，用 THz 三次谐波（THz-3ω）跨过了 Mott 绝缘体–金属相变来诊断强关联低能集体模式。这正是我组一直在追踪的方向——THz HHG 作为强场超快光学中一种"全光、无接触、亚周期分辨"的探针，能否真正解耦出电子关联驱动的集体模式（如呼吸模、电荷密度涨落、参量振幅模式）而非仅仅是单粒子带间/带内响应的非线性延伸。

从方法论上讲，THz 驱动的三次谐波处于一个非常有趣的窗口：光子能量低（~meV），驱动场本身可以直接共振或近共振地驱动低能集体激发，因此 3ω 信号对 Hubbard U、带边重整化、以及相变附近的关联长度变化应当极为敏感。这一点与我们在 mid-IR HHG 中习惯的高能电子带间发射形成互补。

## 核心要点

- **体系与问题**：稀土镍酸盐（RNiO₃ 家族，原始摘要未指明具体组分），跨 Mott 绝缘体–金属相变。
- **核心手段**：THz 场驱动的三次谐波产生（THz-3ω），即 THz 频段的 HHG。
- **核心论点**：THz-HHG 可作为强关联集体模式（非单粒子响应）的非线性诊断工具。
- **关注窗口**：低能（meV 量级）集体模式对谐波产生的贡献，以及在 Mott 转变附近的演化。
- **与提案关联**：被 key-transient-quantum-phase-optical 提案引用，说明此文被视为"瞬态量子相变的光学读出"方向的支撑文献之一。

## 实验/研究关联

- **与我组方向的对接**：我组在强场超快光学中常用的 mid-IR/近-IR HHG 关注的是带间发射与 Berry 曲率等高能响应；THz-HHG 把窗口推到了关联尺度本身。如果 THz-3ω 真的能选择性读出集体模式，那它就提供了一个"关联指纹"通道——这是 mid-IR HHG 难以做到的。
- **方法可迁移性**：稀土镍酸盐的相变可由温度、应变、掺杂、电学门压等多参量调控，THz-3ω 对其中哪一类控制变量最敏感，是决定其能否拓展到瞬态（光泵浦–THz 探测）实验的关键。
- **与瞬态量子相变提案的关系**：本工作被 transient quantum phase 提案引用，提示其可能提供了一个稳态下"集体模式非线性响应"的基线参考。但稳态 3ω 与光泵浦驱动的瞬态非平衡 3ω 之间的联系与差异，仍需在阅读全文后判断。

## 开放问题

- **关键信息缺失**：原始摘要为空，材料组分（NdNiO₃？SmNiO₃？）、实验温度范围、THz 场强、是否做了时间分辨或仅做频域 3ω 等均未给出。需要在拿到 PDF/正文后核实。
- **集体模式的指认**：THz-3ω 信号中如何区分（a）单粒子 Hubbard 带间非线性响应、（b）呼吸模/振幅模（amplitude mode）、（c）声子或晶格贡献？原文是否给出了基于模型的分离？
- **跨相变的标度行为**：3ω 强度在 Mott 转变附近是发散、突变还是连续？其标度律是否与静态关联长度挂钩？
- **瞬态延展**：如果用光泵浦将体系驱动至瞬态金属态，THz-3ω 是否能追踪非平衡集体模式的时间演化？这将直接决定该方法能否服务于瞬态量子相变提案。
- **对比基准**：与已有的 mid-IR 3ω、THz 时域光谱（光学电导率）、以及 ARPES/RIXS 的静态/准静态集体模式测量相比，THz-HHG 的信息冗余度与新增量是什么？

## 来源
- 原始材料：2026-PhysRevB.113.045118-terahertz-harmonic-generation-across-the-mott-insulator-meta.md
- 蒸馏时间：2026-09-29T10:57:12Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：THz 三次谐波跨 Mott 相变诊断集体模式

**原理**：用 THz 场驱动的三次谐波产生（THz-3ω）诊断稀土镍酸盐跨 Mott 绝缘体–金属相变的低能集体模式。核心机制：meV 量级 THz 光子可直接近共振驱动关联电子体系的集体激发（呼吸模/振幅模等），3ω 信号对 Hubbard U、带边重整化及相变附近关联长度变化敏感，与 mid-IR HHG 的高能带间发射互补，提供'关联指纹'通道。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 体系 | 稀土镍酸盐 RNiO₃ 家族（具体组分未指明） | 核心要点 |
| 观测通道 | THz 三次谐波（THz-3ω） | 核心要点 |
| 诊断对象 | 低能（meV 量级）集体模式在 Mott 转变附近的演化 | 核心要点 |

**适用边界**：页面自注'原始摘要为空'：材料组分、实验温度范围、THz 场强、是否时间分辨/仅频域 3ω 均未给出，不做推断。3ω 信号中单粒子带间响应、集体模式、声子贡献的模型分离方法页面未涉及。
**代表作**：Terahertz harmonic generation across the Mott insulator-metal transition, Phys. Rev. B 113, 045118 (2026)
*方法卡回补 2026-10-04*

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry 曲率]]
- [[THz非线性光谱]]
- [[arpes]]
- [[transient quantum phase]]
- [[低能集体激发]]
- [[强关联材料非线性响应]]
- [[强场超快]]
- [[强场超快光学]]
- [[瞬态量子相变]]
<!-- /linsai-wikilinks -->
