---
title: "thz-spectroscopy"
type: "methods"
created: "2026-09-26T10:20:49Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "#type/method"]
related: ["2604.13429", "2607.08829", "2610.11126", "arXivID", "交变磁体"]
source_raw: ""
growth_stage: "mature"
confidence: 0.7
updated_at: "2026-11-08T03:36:13Z"
settled_count: 2
aliases: ["THz spectroscopy", "terahertz spectroscopy", "THz probe", "THz detection", "THz field", "太赫兹谱", "太赫兹光谱", "太赫兹探测"]
---

<!-- methods-settle:v1 -->

## 原理

THz spectroscopy uses ultrashort strong-field THz pulses to resonantly excite infrared-active phonons for time-resolved detection of lattice/magnetic low-energy dynamics, with 2D THz spectroscopy mapping diagonal and cross peaks to separate linear phonon response from nonlinear phonon–phonon/phonon–magnetic coupling channels (as in FePS3, where an IR-active phonon nonlinearly displaces the 3.27 THz Raman mode to induce metastable net magnetization); a complementary field-scanned magnon spectroscopy mode (Raman/THz detection) uses an external magnetic field to rotate the Néel vector and monitors the switching of magnon mode intensity/visibility, mapping the spectral response directly onto the order-parameter orientation—as demonstrated in the altermagnetic semiconductor α-MnTe, where fields up to 2.5 T continuously reorient the collinear Néel vector and render the chiral, spin-split (~2 meV) magnon modes robust and tunable.

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| FePS3 Raman-active phonon mode frequency (ΩR) | 3.27 THz | arXiv:2510.16993 |
| LiNbO3倾斜波 front源带宽 | 0.1–1 THz（宽带单周期） | arXiv:2610.11126 |
| 有机晶体DSTMS/DAST覆盖 | 1–10 THz，场强达MV/cm | arXiv:2610.11126 |
| GaSe差频可调范围 | 10–100 THz | arXiv:2610.11126 |
| SECUF双强场THz源参数 | 3–20 THz可调，TW级峰值功率 | arXiv:2610.11126 |
| 驱动THz脉冲中心频率 | ~1 THz | arXiv:2604.13429 |
| 驱动脉冲带宽 | 0.3–2.5 THz | arXiv:2604.13429 |
| B₁ᵤ 红外活性声子频率 ω_IR | ~1.17 THz（沿c轴驱动） | arXiv:2604.13429 |
| 交叉耦合声子模式 Q_S 频率 | ~1.68 THz | arXiv:2604.13429 |
| 谐波峰位（2/3/4ω_IR） | 2.34 / 3.51 / 4.68 THz | arXiv:2604.13429 |
| 和频边带（2ω_IR+ω_S，三阶交叉耦合） | 4.02 THz | arXiv:2604.13429 |
| α-MnTe奈尔温度 T_N | 310 K | arXiv:2607.08829 |

## 适用边界

THz声子相干操控要求目标模式红外活性、可被整形的强场THz脉冲序列共振驱动且与Raman/磁性模式有足够非线性耦合（常规正比于光场平方的Raman过程无法在脉冲结束后实现确定性磁序控制）；磁场扫描磁振子光谱则要求磁振子模式的强度/可见性依赖奈尔矢量取向、且材料磁振子谱足够锐利——在金属型交变磁体中磁振子信号会被短准粒子寿命和巡游电子背景展宽/掩盖，且对共线基态外场仅将六重简并退化为二重、奈尔矢量旋转受各向异性与场强相对大小限制（α-MnTe在~1 T即近饱和），同时THz源覆盖与样品透明度构成实际成本约束。

## 代表作

- arXiv:2510.16993
- arXiv:2607.08829

## 证据日志

- 2026-09-26｜r37｜回原文｜[paper:2025-2510.16993-coherent-terahertz-control-of-metastable-magnetization-in-fe] 二维太赫兹光谱（2D THz spectroscopy）：以激发-探测频率二维映射中的对角峰与交叉峰，把线性声子响应与声子-声子、声子-磁序的非线性耦合通道逐一分辨开。
- 2026-11-08｜r124｜回原文｜[paper:2026-2607.08829-magnetic-field-control-of-the-néel-vector-and-magnon-visibil] 磁场依赖的磁振子光谱学（拉曼/太赫兹探测）：以磁场扫描奈尔矢量取向，实时监测磁振子模式强度/可见性的切换，把光谱响应映射为序参量取向。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2604.13429]]
- [[2607.08829]]
- [[2610.11126]]
- [[arXivID]]
- [[交变磁体]]
<!-- /linsai-wikilinks -->
