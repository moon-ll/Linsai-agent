---
title: "量子光HHG的近似层级：Fermi-Hubbard模型研究（Lange & Madsen 2024）精读笔记"
type: "papers"
created: "2026-08-25T05:05:01Z"
updated: "2026-11-15T15:09:22Z"
tags: ["高次谐波", "量子光学", "费米-哈伯德模型", "固体HHG", "BSV", "非经典光", "近似方法层级", "论文精读"]
related: ["BSV驱动HHG量子化正演模型", "general-bsv-driven-hhg-quantum-20260726", "亮压缩真空", "半导体布洛赫方程", "固体HHG", "固体高次谐波", "输入-输出理论", "高次谐波产生", "高次谐波产生的量子光学理论"]
source_raw: "2024-2410.19533-hierarchy-of-approximations-for-describing-quantum-light-fro.md"
growth_stage: "growing"
confidence: 0.6
auto_grown: true
review_status: "pending"
has_fulltext: true
---

# 量子光HHG的近似层级：Fermi-Hubbard模型研究（Lange & Madsen 2024）精读笔记

## 林赛的理解

这篇论文正好戳中我们 BSV 项目最头疼的方法学问题：**描述固体 HHG 产生的量子光，到底需要多“量子”的模型？** 我们组做固体 HHG 模拟的常规做法是把驱动场当经典参数，解含时薛定谔方程或半导体布洛赫方程——这在相干态激光驱动下没问题。但 BSV（亮压缩真空）本质上是光子数涨落极大、相位不确定的量子态，驱动场的量子涨落会不会通过非线性过程传递到谐波端、什么时候必须显式处理介质对场的反作用，这直接决定我们 proposal "general-bsv-driven-hhg-quantum-20260726" 里正演模型的计算量级。

Madsen 组从气体 HHG 的量子光学理论起家（输入-输出框架、谐波间量子关联），这次把工具搬到 Fermi-Hubb


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：量子光 HHG 的近似层级框架（Fermi-Hubbard 模型）

**原理**：系统回答'描述固体 HHG 产生的量子光需要多量子的模型'：从经典驱动场 + 含时薛定谔/半导体 Bloch 方程近似，到显式处理驱动场量子涨落与介质对场反作用的近似层级比较。核心机制：Madsen 组从气体 HHG 量子光学理论（输入-输出框架、谐波间量子关联）出发把工具搬到 Fermi-Hubbard 模型，界定经典场近似何时失效——直接决定 BSV 驱动 HHG 正演模型的计算量级。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 模型平台 | Fermi-Hubbard 模型 | 标题/林赛的理解 |
| 理论工具 | 输入-输出框架 + 谐波间量子关联（气体 HHG 量子光学理论迁移） | 林赛的理解 |

**适用边界**：页面'林赛的理解'小节在'搬到 Fermi-Hubb'处截断，具体近似层级划分与结论未获得；BSV 提案正演模型选型的直接方法学依据。
**代表作**：Lange & Madsen, Hierarchy of approximations for describing quantum light from high-harmonic generation, arXiv:2410.19533 (2024)
*方法卡回补 2026-10-04*

<!-- linsai-wikilinks -->
## 关联概念

- [[BSV驱动HHG量子化正演模型]]
- [[general-bsv-driven-hhg-quantum-20260726]]
- [[亮压缩真空]]
- [[半导体布洛赫方程]]
- [[固体HHG]]
- [[固体高次谐波]]
- [[输入-输出理论]]
- [[高次谐波产生]]
- [[高次谐波产生的量子光学理论]]
<!-- /linsai-wikilinks -->
