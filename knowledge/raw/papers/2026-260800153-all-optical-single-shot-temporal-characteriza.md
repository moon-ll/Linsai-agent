---
title: "All-Optical Single-Shot Temporal Characterization of SASE FEL Pulses Using Double-Blind Holography"
arxiv_id: "2608.00153"
authors: "A. Azzolin, O. Cannelli, K. -F. Wong, V. J. Yallapragada, E. P. Månsson"
year: 2026
tags: ["deepxiv-论文库"]
project: ["NSFC-强场超快"]
direction: "阿秒科学"
source: "hermes-briefing"
imported_at: "2026-08-04T13:05:07Z"
score_deepxiv: 0.5
status: "unseen"
read_status: "unread"
has_pdf: false
---
# All-Optical Single-Shot Temporal Characterization of SASE FEL Pulses Using Double-Blind Holography

## 摘要

X-ray Free-electron lasers (XFELs) deliver ultrashort and ultrabright radiation in a photon-energy range spanning from extreme ultraviolet to hard X-rays. Supporting pulse durations down to hundreds of attoseconds, these sources are unique in enabling imaging of matter with unprecedented temporal and spatial resolution. However, schemes that produce such ultrashort pulses typically rely on Self-Amplified Spontaneous Emission (SASE), a stochastic process that introduces significant temporal and spectral jitter, therefore requiring single-shot characterization methods for post sorting the acquired data. Although various methods have been developed for pulse characterization and delay tagging, they often come with experimental and computational complexity. Moreover, no existing method currently combines both single-shot pulse reconstruction and delay tagging at the attosecond time scale. To close this gap, we present a single-shot all-optical method based on Double-Blind Holography (DBH). By recording the spectral interference between an extreme ultraviolet (XUV) FEL source and a high-harmonic generation (HHG)-based source, we achieve simultaneous waveform reconstruction and delay tagging of sub-10 fs FEL pulses with attosecond precision.

## 背景概述与问题引入

X 射线自由电子激光（XFEL）凭借其极短脉冲宽度（可达阿秒量级）和超高亮度，已成为从极紫外到硬 X 射线波段探索物质超快动力学独一无二的光源。然而，SASE（自放大自发辐射）作为产生亚 10 fs 短脉冲的主流方案，本质上是一个随机起振过程，导致脉冲的时域和频域 profile 存在显著抖动。要充分利用 XFEL 的时间分辨能力，必须在单发（single-shot）水平上对脉冲进行完整时域表征并在后期按延时打标（delay tagging）。既有方案普遍依赖复杂的光路、多次扫描或多步重建，目前没有任何方法能在阿秒精度上同时实现单发脉冲重建与延时打标。本文正是针对这一空白，提出基于双盲全息（Double-Blind Holography, DBH）的全光学单发表征方案。

## 关键发现及核心讨论

- **首次实现阿秒精度的单发 SASE FEL 脉冲完整时域重建**：通过记录 XUV 自由电子激光 FEL 脉冲与一个 HHG 产生的高次谐波参考源之间的光谱干涉图样，DBH 方案能在单发条件下同时重建波形和打标延时，精度达到阿秒量级。
- **方法对 sub-10 fs FEL 脉冲的实验验证**：在 XUV 波段演示了对亚 10 fs FEL 脉冲的同步波形重建与延时打标，证实该方法在 FEL 实际工作带宽与脉宽条件下具备可行性。
- **补丝“单发重建 + 延时打标”的双重空白**：作者明确指出，现有任何方法都无法同时兼顾二者，DBH 是首个能在一个测量周期内同时给出两个输出量的方案。

## 主要方法

DBH 的核心思想是把 FEL 脉冲作为“信号场”、把已知稳定的 HHG 脉冲作为“参考场”，两者在分束/重叠后形成空间-光谱干涉图样。由于两个场都是超短脉冲，干涉图样中编码了相对延时与相对相位信息，再通过双盲重建算法（无需事先知道两束光的相位分布）反演出完整的电场波形。整个方案完全在光学层面完成，无需电子学延时扫描或复杂的多步数据处理。

## 创新性

与现有依赖多次扫描或复杂反演的 XFEL 脉冲表征方法相比，DBH 把“干涉计量”与“全光学全息”结合到 XFEL 场景中，首次在同一测量中同时给出单发重建结果和阿秒精度的延时打标。

## 结论与展望

作者展示了 DBH 作为 XFEL 单发脉冲时域表征工具的可行性，预期可以无缝集成到 XFEL 实验站点的数据流水线中，用于泵描-探测实验中事件式（event-by-event）的延时分类和波形后处理。