---
title: "Quantum simulations of ultrafast optical spectroscopy of semiconductors on digital quantum computers in the semi-classical approximation"
type: "papers"
created: "2026-11-01T05:40:00Z"
updated: "2026-11-08T05:06:54Z"
tags: ["topic/量子计算", "topic/计算方法", "topic/半导体光学"]
related: ["2606.04295", "First-principles electron-phonon scattering in real-time TDDFT", "TDDFT", "半导体Bloch方程", "强场驱动", "量子光学"]
source_raw: "2026-2606.04295-quantum-simulations-of-ultrafast-optical-spectroscopy-of-sem.md"
growth_stage: "seedling"
confidence: 0.6
arxiv_id: "2606.04295"
authors: "Mykhailo Klymenko, Thong Hoang, Jared H. Cole, Muhammad Usman"
year: "2026"
review_status: "pending"
digest_level: "abstract"
---

# Quantum simulations of ultrafast optical spectroscopy of semiconductors on digital quantum computers

## 林赛的理解

半导体超快光谱的量子计算替代路线：把含 Hartree-Fock 的线性光学响应映射成耦合经典振子系统后在数字量子机上模拟，无噪声极限下与 GaAs 经典结果定量一致。当下对我们是"远期期权"——但「超越 HF 后经典面临层级问题而量子复杂度不变」这个论证值得进方法视野，作为强场多体计算的长期路线图注脚。

## 研究问题

能否在数字量子计算机上以半经典近似模拟半导体的超快光学/时域光谱，替代经典 SBE 类求解？

## 研究背景

经典半经典方法（半导体布洛赫方程）模拟固体超快光学已成熟，但超越 Hartree-Fock 的多体关联使经典计算复杂度层级增长；量子模拟在特定查询复杂度假设下可证明优势（参照 PRX 13, 041041 (2023)）。

## 研究方法

布里渊区离散化的数字量子模拟框架；含洛伦兹展宽、有限温度带填充与降维效应；线性吸收与光学增益模拟；含 Hartree-Fock 多体相互作用的线性光学响应映射为耦合经典振子系统；与 GaAs 经典单粒子模拟对比验证。

## 主要发现与核心结论

无噪声极限下与经典模拟达到定量一致；NISQ 硬件噪声等效于额外散射源（谱展宽增大）；映射后的振子系统在特定假设下具有可证明的量子优势；超越 HF 后经典面临 hierarchy problem 而量子算法复杂度不变。

## 潜在研究方向

关联多体（超 HF）项的量子模拟；噪声缓解策略与谱展宽分离；固体强场驱动的全量子处理。

## 与林赛研究的关联

- 强场 HHG 多体效应（双电子、激子通道）的长期计算路线图：层级问题论证直接对上我们 TAE-SFA/多体 HHG 方向。
- 量子硬件噪声=额外散射的类比，对 SBE 退相干建模有概念启发（配合 [[First-principles electron-phonon scattering in real-time TDDFT]] 的第一性原理散射）。

## 来源

- 蒸馏自摘要（abstract 级，arXiv 摘要补充，ZCode 消费）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：半导体超快光学响应的数字量子计算机模拟（半经典近似 + Hartree-Fock 耦合振子映射）

**原理**：把含 Hartree-Fock 多体相互作用的线性光学响应映射为耦合经典振子系统，在布里渊区离散化的数字量子模拟框架中模拟半导体线性吸收与光学增益（含洛伦兹展宽、有限温度带填充与降维效应）；无噪声极限下与 GaAs 经典单粒子模拟定量一致。

**适用边界**：半经典近似（经典场+量子电子）；NISQ 硬件噪声等效额外散射源（谱展宽增大）；超越 HF 后经典面临 hierarchy problem 而量子算法复杂度不变——优势论证依赖特定查询复杂度假设；摘要级。
**代表作**：Klymenko et al., Quantum simulations of ultrafast optical spectroscopy of semiconductors on digital quantum computers in the semi-classical approximation, arXiv:2606.04295 (2026)
*方法卡回补 2026-11-01*

<!-- linsai-wikilinks -->
## 关联概念

- [[2606.04295]]
- [[First-principles electron-phonon scattering in real-time TDDFT]]
- [[TDDFT]]
- [[半导体Bloch方程]]
- [[强场驱动]]
- [[量子光学]]
<!-- /linsai-wikilinks -->
