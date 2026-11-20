---
title: "Linking High-Harmonic Generation and Strong-Field Ionization in Bulk Crystals"
type: "papers"
created: "2026-11-01T05:40:00Z"
updated: "2026-11-15T15:09:23Z"
tags: ["topic/固体高次谐波", "topic/强场超快", "topic/强场电离"]
related: ["2303.10956", "三步模型", "半导体Bloch方程", "固体HHG", "固体高次谐波", "非线性光学"]
source_raw: "2023-2303.10956-linking-high-harmonic-generation-and-strong-field-ionization.md"
growth_stage: "seedling"
confidence: 0.6
arxiv_id: "2303.10956"
authors: "Jürgens, Roscam Abbing, Mero, Brown, Vrakking, Mermillod-Blondin, Kraus, Husakou"
year: "2023"
review_status: "pending"
digest_level: "abstract"
---

# Linking High-Harmonic Generation and Strong-Field Ionization in Bulk Crystals

## 林赛的理解

体固体 HHG 的机制归属（带内电流 / 带间再碰撞 / 电离相关通道）一直是理论归因模糊地带；这篇工作用「取向依赖的非线性吸收 + 谐波产率」联合测量，给出谐波发射与激光诱导电离之间无歧义关联的实验证据，等于把"电离相关通道"从解释选项升级为实证必要项。对我们课题的机制章节（ZnO/MgO 类宽禁带体系）意味着：把谐波产率与电离率做同取向扫描对比，是低成本高说服力的机制判据。

## 研究问题

体固体高次谐波的发射机制中，电离相关贡献占比多大、与谐波发射是否因果关联？

## 研究背景

强场超短脉冲驱动的体固体 HHG 已开辟极端非线性光学与亚周期光-物质相互作用新方向，但完整图像仍未建立；文献中并存三类机制归因：非线性带内电流、带间再碰撞、电离相关效应。三者都涉及激光驱动激发，单靠谐波谱本身难以判别。

## 研究方法

取向依赖的非线性吸收测量与谐波产生测量联合扫描（晶体取向为控制变量）；半导体 Bloch 方程（SBE）模拟；基于最大局域化 Wannier 函数计算的取向依赖电离率。

## 主要发现与核心结论

谐波发射与激光诱导电离之间存在**无歧义关联**（unambiguous correlation）：谐波产率取向依赖性与电离率取向依赖性一致，SBE 模拟与 Wannier 电离率计算共同支撑。

## 潜在研究方向

电离通道与带间再碰撞通道的定量分解；自由载流子对谐波相位的贡献；损伤前电离率作为谐波优化自由度。

## 与林赛研究的关联

- 课题机制章节：宽禁带体系（ZnO/MgO）HHG 归因须含电离相关通道，取向扫描吸收-谐波对比可作方案验证步。
- 电离率计算的 MLWF 路线与我们的 Wannier 哈密顿量管线兼容。
- 与 [[三步模型]] 的固体对应物（电离-加速-复合）边界讨论直接相关。

## 来源

- 蒸馏自摘要（abstract 级，arXiv 摘要补充，ZCode 消费）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：取向依赖非线性吸收-谐波产率联合扫描判定电离相关 HHG 通道（SBE + MLWF 电离率）

**原理**：以晶体取向为控制变量，联合扫描取向依赖的非线性吸收测量与谐波产生测量，配合半导体 Bloch 方程（SBE）模拟与基于最大局域化 Wannier 函数（MLWF）计算的取向依赖电离率——证明谐波发射与激光诱导电离之间存在无歧义关联：谐波产率取向依赖与电离率取向依赖一致。

**适用边界**：体晶体（宽禁带体系）实验+模拟；在带内电流/带间再碰撞/电离相关三类机制归因中实证支持电离相关通道，通道两两定量分解留待后续；摘要级不可作定量依据。
**代表作**：Jürgens et al., Linking High-Harmonic Generation and Strong-Field Ionization in Bulk Crystals, arXiv:2303.10956 (2023)
*方法卡回补 2026-11-01*

<!-- linsai-wikilinks -->
## 关联概念

- [[2303.10956]]
- [[三步模型]]
- [[半导体Bloch方程]]
- [[固体HHG]]
- [[固体高次谐波]]
- [[非线性光学]]
<!-- /linsai-wikilinks -->
