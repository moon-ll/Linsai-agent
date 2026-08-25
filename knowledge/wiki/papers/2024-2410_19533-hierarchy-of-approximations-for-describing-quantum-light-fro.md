---
title: "量子光HHG的近似层级：Fermi-Hubbard模型研究（Lange & Madsen 2024）精读笔记"
type: "papers"
created: "2026-08-25T05:05:01Z"
updated: "2026-08-25T05:12:33Z"
tags: ["高次谐波", "量子光学", "费米-哈伯德模型", "固体HHG", "BSV", "非经典光", "近似方法层级", "论文精读"]
related: ["BSV驱动HHG量子化正演模型", "亮压缩真空", "半导体布洛赫方程", "固体高次谐波", "输入-输出理论", "高次谐波产生", "高次谐波产生的量子光学理论"]
source_raw: "2024-2410.19533-hierarchy-of-approximations-for-describing-quantum-light-fro.md"
growth_stage: "growing"
confidence: 0.6
auto_grown: true
review_status: "pending"
---

# 量子光HHG的近似层级：Fermi-Hubbard模型研究（Lange & Madsen 2024）精读笔记

## 林赛的理解

这篇论文正好戳中我们 BSV 项目最头疼的方法学问题：**描述固体 HHG 产生的量子光，到底需要多“量子”的模型？** 我们组做固体 HHG 模拟的常规做法是把驱动场当经典参数，解含时薛定谔方程或半导体布洛赫方程——这在相干态激光驱动下没问题。但 BSV（亮压缩真空）本质上是光子数涨落极大、相位不确定的量子态，驱动场的量子涨落会不会通过非线性过程传递到谐波端、什么时候必须显式处理介质对场的反作用，这直接决定我们 proposal "general-bsv-driven-hhg-quantum-20260726" 里正演模型的计算量级。

Madsen 组从气体 HHG 的量子光学理论起家（输入-输出框架、谐波间量子关联），这次把工具搬到 Fermi-Hubb

<!-- linsai-wikilinks -->
## 关联概念

- [[BSV驱动HHG量子化正演模型]]
- [[亮压缩真空]]
- [[半导体布洛赫方程]]
- [[固体高次谐波]]
- [[输入-输出理论]]
- [[高次谐波产生]]
- [[高次谐波产生的量子光学理论]]
<!-- /linsai-wikilinks -->
