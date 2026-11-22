---
title: "Synthesizing free-electron wave functions by stimulated near-field interactions"
arxiv_id: "2610.08325"
authors: "Álvaro Rodríguez Echarri, Albert Polman"
year: 2026
tags: ["deepxiv-论文库"]
project: ["NSFC-强场超快"]
direction: "阿秒科学"
source: "hermes-briefing"
imported_at: "2026-10-07T11:30:06Z"
score_deepxiv: 0.5
status: "unseen"
read_status: "unread"
has_pdf: false
---
# Synthesizing free-electron wave functions by stimulated near-field interactions

## 摘要
Stimulated electron-optical-near-field interactions imprint a coherent, phase-coherent modulation on the wave function of a free electron, of which the free-space dispersion subsequently converts into a train of attosecond density peaks. Light thereby becomes a tool for synthesizing the electron wave function itself, setting when, where, and how narrowly the electron density concentrates. Here we study photon-induced near-field electron microscopy (PINEM) to gain control over that synthesis in two stages: first for a single PINEM interaction, whose design parameters we obtain in closed form, and then for multiple PINEM interactions acting in parallel, which extends the control across space and time. The design rules follow from decomposing the propagated density into temporal harmonics, which we classify into three: (i) the arrival time of the attosecond train, fixed by the optical phase of the coupling; (ii) the distance at which the train forms, set by diffraction at the point where all classical trajectories converge; and (iii) the pulse duration, fixed by the imprinted energy spread. We evaluate these parameters for a scanning-electron-microscope (SEM) configuration at 10 keV, where the compression completes within tens of micrometers from the interaction region, with results 20% better than previous approaches. Letting the electron then interact with several spatially separated near fields in parallel, normal to the trajectory, each pathway carrying its own coupling strength and optical phase, we show that retaining or erasing which-path information changes both the propagated density and the measurable energy spectrum, the latter providing in turn a measure of the mutual coherence of the driving fields. These results establish PINEM as a quantitative synthesis tool for free-electron wave functions in compact, low-voltage electron microscopes.

## 背景概述与问题引入
自由电子与光场近场的受激相互作用（PINEM）会在电子波函数上印刻相干相位调制，自由空间色散随后将这种调制转化为阿秒级电子密度峰列。这使光成为"合成电子波函数"的工具——可以设定电子密度在何时、何地、多窄地聚焦。但此前该技术缺乏系统的设计规则：单次相互作用中，阿秒峰列的到达时刻、形成位置和脉宽分别由什么参数决定，没有解析答案；多个近场并行作用时波包整形能达到什么程度的时空控制，也未被系统研究。本文要解决的核心问题是为 PINEM 电子波函数合成建立一套定量设计框架。

## 关键发现及核心讨论
1. **单次 PINEM 的三个封闭形式设计规则**：将传播后的电子密度分解为时间谐波，证明有三个独立可调参数——阿秒峰列的到达时刻由耦合的光学相位固定；峰列形成的距离由衍射决定（所有经典轨迹会聚点）；脉冲宽度由印刻的能量展宽固定。三参数解耦意味着可以独立控制电子波包的"何时、何地、多窄"。
2. **SEM 低电压构型的定量评估**：在 10 keV 扫描电镜构型下，压缩在距相互作用区数十微米内完成，性能比先前方法好 20%。这证明无需透射电镜的高能电子，紧凑型低电压电子显微镜即可实现阿秒电子波包合成。
3. **多近场并行相互作用与路径信息**：让电子同时与多个空间分离的近场（垂直于电子轨迹）作用，每条路径携带各自的耦合强度与光学相位。保留或擦除路径信息（which-path information）会同时改变传播密度和可测能量谱——能量谱因此成为驱动场之间 mutual coherence 的测量手段。

## 主要方法
- **理论框架**：PINEM 相互作用的解析处理，传播密度的 temporal harmonics 分解
- **构型**：10 keV SEM 电子束 + 光学近场；多近场并行几何（近场垂直于电子轨迹排布）
- **验证对象**：传播后电子密度、能谱（能谱作为路径相干性的读出）

## 创新性
将 PINEM 从"观察电子-光相互作用"的工具转变为"定量合成自由电子波函数"的工具：给出单次作用的封闭形式设计规则，并用多近场并行把控制维度从单点扩展到时空全域；能谱读出驱动场 mutual coherence 是新的测量思路。

## 结论与展望
PINEM 可以作为紧凑低电压电子显微镜中自由电子波函数的定量合成工具，三条设计规则（到达时刻/形成距离/脉宽）解耦可调。后续方向包括多近场并行整形的实验实现、以能谱测量驱动场相干性，以及在通信、计算与信号处理频率上的器件应用。对本组的启示：电子波包的光学合成与我们的强场电子动力学操控在方法论上同构——"印刻相位 → 色散转化为时间结构"与 HHG 中"驱动场相位 → 电子轨迹干涉"共享同一逻辑，多路径相位控制思想值得借鉴到固体 HHG 的多带整形。