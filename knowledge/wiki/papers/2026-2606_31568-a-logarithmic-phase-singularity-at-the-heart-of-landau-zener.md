---
title: "2026-2606.31568-a-logarithmic-phase-singularity-at-the-heart-of-landau-zener"
type: "papers"
created: "2026-11-01T06:06:01Z"
updated: "2026-11-15T15:09:21Z"
tags: []
related: ["Landau-Zener跃迁", "固体HHG", "非绝热跃迁"]
source_raw: "2026-2606.31568-a-logarithmic-phase-singularity-at-the-heart-of-landau-zener.md"
growth_stage: "seedling"
confidence: 0.5
---

## 林赛的理解

Landau-Zener 跃迁概率幅 a_LZ = exp[−π/(2ε)] 这个「用了一百年的公式」被围道积分追到了根上：一个对数相位奇点 + Cauchy 定理给出的 iπ。对我们强场链路的意义很直接——houston 课题的 KP/LZ 通道、Zener 隧穿区 HHG 判据都在引用这族公式，现在知道 Markov 近似与精确解同源（共享奇点结构），「近似是否引入系统性偏差」这个问题有了干净的答案：在该奇点主导的区段没有。

## 研究问题（Research Question）

LZ 跃迁概率幅公式的深层来源是什么？为何 Markov 近似与精确解给出相同结果？

## 研究背景（Background）

LZ 问题（1932）是能级交叉非绝热跃迁的基石模型，广泛应用于量子两能级体系；其概率幅的标准形式广被引用，但其解析结构来源与近似适用性的深层联系缺乏统一阐述。

## 研究方法（Methods）

复分析/围道积分：由复平面原点处简单极点的围道积分与约化啁啾参数 ε 确定波相位；构造连接实轴 ±1、上半平面绕过极点的渐近路径；下半半圆与渐近路径共同包围极点。

## 主要发现与核心结论（Main Results）

渐近围道值由 Cauchy 定理给出为 iπ（无量纲）；由此直接导出 a_LZ = exp[−π/(2ε)]；a_LZ 本质源于对数相位奇点，Markov 近似与精确解共享同一奇点结构——两者结果一致的原因由此澄清。

## 潜在研究方向（Limitations & Open Questions）

多能级链的奇点结构分类；耗散腔环境下奇点结构的稳定性；与周期驱动（Floquet-LZ 链）的结合。

## 与林赛研究的关联

- houston-kronig-penney-landau-zener 课题：LZ 通道概率幅的解析根基与「近似合法性」的引证锚；
- Zener 隧穿型截止判据（强场固体 HHG）中 LZ 公式的适用条件可引此文的奇点视角。

## 来源

- 蒸馏自摘要（abstract 级，arXiv 摘要补充，ZCode 消费；v7.2.103 修复叙述污染空壳页）

## 关联概念

- [[Landau-Zener跃迁]]
- [[非绝热跃迁]]

<!-- linsai-wikilinks -->
## 关联概念

- [[Landau-Zener跃迁]]
- [[固体HHG]]
- [[非绝热跃迁]]
<!-- /linsai-wikilinks -->
