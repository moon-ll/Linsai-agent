---
title: "DFT计算"
type: "methods"
created: "2026-10-24T11:03:47Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法卡", "DFT", "第一性原理", "电子结构"]
related: ["2507.03996", "TDDFT", "arXivID", "强关联体系", "强场超快", "解析tight-binding", "超快自旋动力学"]
source_raw: ""
growth_stage: "growing"
confidence: 0.85
source_reliability: "reliable"
sources: ""
- title: "briefing-2026-10-23.md"
source_type: "briefing"
---

# DFT / TDDFT 计算

> 方法定位：课题管线中电子结构与强场响应的第一性原理计算底座。被 3 个课题
> kb-methods-pack 引用（2026-10-30 由空心补全，素材锚点 [[TDDFT]] 概念页）。

## 原理

**DFT**：以电子密度为基本变量的基态理论（Kohn–Sham 方程组）。
**TDDFT**（DFT 的含时推广，Runge–Gross 定理 1984：含时外场与含时密度一一对应）：求解含时 Kohn–Sham（TDKS）方程演化多体系统，代价远低于含时多体薛定谔方程。

两种工作模式：
1. **线性响应 TDDFT**（Casida 方程）：激发能/振子强度，适合微扰区（吸收谱、光学性质）；
2. **实时 RT-TDDFT**：显式传播 TDKS 轨道，处理任意强场非微扰问题（飞秒激光）；与核运动耦合成 Ehrenfest 动力学。

**磁性扩展**：自旋极化/非共线 TDDFT 显式算激光退磁、自旋流。
**主要误差源**：交换关联势的绝热近似（ALDA/AGGA）——无法描述双激发、长时间电荷转移。**数值实现**：Magnus / Crank–Nicolson / 强制时间反演对称传播子 + 实空间网格，天然适合 GPU 异构加速。

## 参数表

| 参数 | 数值/要点 | 出处 |
| --- | --- | --- |
| 理论基石 | Runge–Gross 定理（1984） | [[TDDFT]] |
| 主要误差源 | 绝热近似 xc（ALDA/AGGA） | [[TDDFT]] |
| 传播子 | Magnus / Crank–Nicolson / 强制时间反演对称 | [[TDDFT]] |
| 强场模式 | RT-TDDFT（非微扰，任意场强） | [[TDDFT]] |
| 电子-核耦合 | Ehrenfest 动力学（需非绝热时转面跳跃/NEGF） | [[TDDFT]] |

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 可调参数总数 | 5个（归一化前因子a0 + a1–a4） | [[2507.03996]]（arXiv 2507.03996） |
| 拟合输入电离概率 | 51个（单一强度8×10¹³ W/cm²） | [[2507.03996]] |
| 验证波长范围 | 0.2–1.2 μm | [[2507.03996]] |
| 验证强度范围 | 0.8–1.5×10¹⁴ W/cm² | [[2507.03996]] |
| 经典轨迹验证的电子到达阈值 | r ≥ 21 Å | [[2507.03996]] |
| 准静态隧穿指数因子 | e^{-2κ³/3|E|}（Eq.11），另含Tong-Lin型修正e^{-κ(a1a2)²|E|} | [[2507.03996]] |
| 平衡晶格常数（PBE基态，3R-MoS₂） | 3.15 Å | 基态DFT计算，与实验吻合 
| PBE间接带隙 | 1.29 eV | 基态DFT计算（PBE泛函） 
| VASP计算设置 | 550 eV 截断能，21×21×1 k网格，15 Å 真空层，optB86b-vdW描述层间范德华作用 | 方法部分（VASP + PAW + PBE） 
| 激光光子能量 | 2 eV（高于带隙） | 高斯包络脉冲 E(t)=E₀cos(ωt)exp[−(t−t₀)²/(2σ²)] 
<!-- src:2507.03996 -->
<!-- src:2025-2505_24186-photostriction-tunable-polarization-and-structural-dyn -->

## 适用边界

✅ 基态电子结构、激发谱（线性响应）、强场超快响应（RT-TDDFT）、超快自旋动力学（非共线扩展）。
❌ 绝热近似下：双激发、长时间电荷转移激发；强关联体系精度受限于 xc 泛函；比 GW/BSE 便宜但精度上限低。

## 代表作

- Runge & Gross, PRL 52, 997 (1984)（理论基石）；GPU 异构实现方向见 2603.21835

## 证据日志

- 2026-10-31 本页由空心补全（素材：concepts/TDDFT 57 行页聚合）。

<!-- linsai-wikilinks -->
## 关联概念

- [[2507.03996]]
- [[TDDFT]]
- [[arXivID]]
- [[强关联体系]]
- [[强场超快]]
- [[解析tight-binding]]
- [[超快自旋动力学]]
<!-- /linsai-wikilinks -->
