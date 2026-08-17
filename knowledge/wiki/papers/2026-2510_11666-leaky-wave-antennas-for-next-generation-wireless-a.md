---
title: "精读笔记：Leaky Wave Antennas for Next Generation Wireless Applications in sub-THz Frequencies — 现状与挑战（arXiv:2510.11666）"
type: "papers"
created: "2026-08-15T22:59:05Z"
updated: "2026-08-17T05:19:28Z"
tags: ["论文精读", "leaky-wave-antenna", "sub-THz", "波束扫描", "角频耦合", "6G", "时空耦合"]
related: ["Smith-Purcell辐射", "beam squint", "光子学辅助毫米波产生", "太赫兹源（光学整流/双色成丝/自旋电子THz）", "相位匹配", "脉冲前沿倾斜", "角色散与时空光场调控"]
source_raw: "2026-2510.11666-leaky-wave-antennas-for-next-generation-wireless-a.md"
growth_stage: "growing"
confidence: 0.7
auto_grown: true
review_status: "pending"
---

# 精读笔记：Leaky Wave Antennas for Next Generation Wireless Applications in sub-THz Frequencies — 现状与挑战

**arXiv**: [2510.11666](https://arxiv.org/abs/2510.11666) ｜ **作者**: Natalie Lang, Atsutse Kludze, Nir Shlezinger ｜ **类型**: 综述（survey）｜ **deepxiv 评分**: 0.25

## 林赛的理解

这篇综述讲的是通信那边的事，但一开头那个关键词"angle-frequency coupling（角-频耦合）"就把我抓住了——这不就是我们在压缩器/展宽器里天天打交道的角色散（angular dispersion）吗？所谓漏波天线（LWA），本质上就是一个**辐射型的光栅/棱镜**：导波模式沿结构传播时逐步向外泄漏，泄漏角由相位匹配条件 sin θ(ω) = β(ω)/k₀ 决定——这套数学和切伦科夫辐射、Smith-Purcell 效应是同源的，我在强场和电子加速相关的工作里并不陌生。

通信的人把它叫"频控波束扫描，无需移相器"；在我眼里这是一个**"空间啁啾辐射器"**——把频谱沿角度铺开。我们在 LiNbO₃ 里用脉冲前沿倾斜实现相位匹配的宽带 THz 产生，是在**源头**做频-角映射；LWA 则是在**辐射端**做同样的映射。两者互为对偶。

坦率地说，deepxiv 给它打了 0.25 分，说明对我组的核心方向相关性不高——它是一篇信号处理/通信视角的综述，没有新物理。但它对我有两点真实价值：一是概念迁移的机会（时空光场调控 ↔ 漏波结构），二是它把 sub-THz 硬件层面"还缺什么"列了一份清单（源、调制、工艺、损耗），而这恰恰是超快光子学（光子学辅助产生、宽带 THz 脉冲）可以切入的地方。低分不等于没用的论文，这篇属于"跨界启发型"文献。

## 核心要点

### 核心发现
- **单一

<!-- linsai-wikilinks -->
## 关联概念

- [[Smith-Purcell辐射]]
- [[beam squint]]
- [[光子学辅助毫米波产生]]
- [[太赫兹源（光学整流/双色成丝/自旋电子THz）]]
- [[相位匹配]]
- [[脉冲前沿倾斜]]
- [[角色散与时空光场调控]]
<!-- /linsai-wikilinks -->
