---
has_fulltext: true
title: "Few-cycle electro-optic light on thin-film lithium niobate"
arxiv_id: "2608.11393"
authors: "Xinyi Ren, Chun-Ho Lee, Ian Christen, Clayton Cheung, Reshma Kopparapu"
year: 2026
tags: ["deepxiv-论文库"]
project: ["NSFC-强场超快"]
direction: "阿秒科学"
source: "hermes-briefing"
imported_at: "2026-08-13T10:40:22Z"
score_deepxiv: 0.5
status: "unseen"
read_status: "unread"
has_pdf: false
---
# Few-cycle electro-optic light on thin-film lithium niobate

## 摘要
The twin fields of ultrafast optics and nonlinear photonics enable applications ranging from attosecond science and ultrafast electronics to molecular spectroscopy, nonlinear optics, quantum nanophotonics and precision metrology. Here we demonstrate an integrated multi-functional nonlinear photonic system that transforms continuous-wave (CW) light into high-peak-power femtosecond pulses and harnesses them for pulse-driven nonlinear optics on thin-film lithium niobate (TFLN). Microwave-driven electro-optic (EO) broadening followed by integrated dispersive compression generates 230-fs Fourier-transform-limited pulses with energies up to 3.3 pJ at 30.7 GHz, orders of magnitude higher pulse energy than previous integrated pulse synthesis at comparable repetition rates. In a 0.3-meter dispersion-engineered TFLN waveguide, soliton dynamics compress the pulses to 35 fs (6.7 optical cycles), accompanied by coherent spectral broadening exceeding 330 nm. In a fully-monolithic architecture, EO synthesis, dispersive compression and a high-Q nonlinear resonator are integrated on a single TFLN chip, enabling resonantly-enhanced pulse pumping and coherent spectral broadening at pulse energies as low as 400 fJ.

## 背景概述与问题引入
阿秒科学与超快光子学的长期目标之一, 是把少周期光脉冲的合成与强非线性相互作用集成到一块可扩展的芯片平台上。传统方案依赖体块钛宝石振荡器 + 放大器 + 外部色散补偿链路: 体积庞大, 难以扩展, 且脉冲能量与重复频率之间难以兼顾。在光通信频率(约 30 GHz 量级)下, 此前集成平台虽展示了 CW-> 脉冲合成, 但单脉冲能量受限于 fJ 量级, 不足以驱动片上非线性过程。本文核心问题: 在 TFLN 平台上同时实现高重频(30 GHz 量级)、pJ 量级单脉冲能量、少周期(<10 cycle) 脉宽与单芯片全集成非线性应用。

## 关键发现及核心讨论
- **EO 展宽 + 色散压缩生成 230 fs / 3.3 pJ 脉冲, 30.7 GHz 重频**: TFLN 上微波驱动的电光相位调制对 CW 光进行频谱展宽, 经集成色散压缩输出 230 fs (FT 极限) 脉冲, 单脉冲能量 3.3 pJ, 比同等重频下此前集成方案高出数个量级。
- **0.3 m 色散工程波导孤子压缩至 35 fs (6.7 个光周期), 光谱展宽 > 330 nm**: 设计色散使脉冲在长波导中经历孤子自压缩, 脉宽由 230 fs 进一步压到 35 fs, 同时伴随 > 330 nm 的相干光谱展宽, 为后续频率转换奠基。
- **单芯片集成: EO 合成 + 色散压缩 + 高 Q 微腔, 400 fJ 即可驱动非线性展宽**: EO 调制器、色散波导与高 Q 微腔集成在同一 TFLN 芯片上, 400 fJ 脉冲能量就能在微腔中实现共振增强泵浦与相干光谱展宽, 闭合低能量集成脉冲合成链路。
- **从 CW 直接到片上少周期非线性光学的端到端路径**: 统一微波可控脉冲合成与脉冲驱动非线性相互作用, 连接 CW 激光输入与少周期非线性输出, 是该工作最核心的系统级贡献。

## 主要方法
- **材料体系**: 薄膜铌酸锂 (TFLN), 兼顾强电光系数、低损耗波导与 CMOS 兼容加工。
- **脉冲合成路线**: 微波驱动的电光相位调制 (EO broadening) -> 集成色散波导压缩 -> 色散工程波导中孤子动力学二次压缩。
- **波导设计**: 0.3 m 长色散工程波导用于 230 fs -> 35 fs 孤子压缩, 同步优化色散曲线与非线性长度匹配。
- **集成非线性应用**: 高 Q 微腔 (high-Q resonator) 作共振增强泵浦, 实现 400 fJ 量级非线性光谱展宽。
- **测量表征**: 自相关/FROG 类脉宽测量、谱宽测量、片上光-电-光全链路验证。

## 创新性
首次在 TFLN 单芯片上同时实现 30 GHz 量级 pJ 能量的少周期脉冲合成与集成非线性应用演示, 把微波驱动 EO 合成、色散/孤子压缩与高 Q 微腔非线性统一为单一平台, 比此前同等重频下集成方案脉冲能量高出数个量级。

## 结论与展望
工作建立了一条 CW -> 片上少周期非线性光学的端到端集成路径, 预期可应用于微波光子学、光频合成与计量, 以及中红外与太赫兹产生等场景。