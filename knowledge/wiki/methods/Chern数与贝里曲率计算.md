---
title: "Chern数与贝里曲率计算"
type: "methods"
created: "2026-09-26T07:03:47Z"
updated: "2026-11-08T05:06:52Z"
tags: ["方法学", "#type/method"]
related: ["2504.00122", "Chern数", "Floquet工程"]
source_raw: ""
growth_stage: "mature"
confidence: 0.6
updated_at: "2026-09-27T02:13:42Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

Chern数由贝里曲率在布里渊区上的积分给出，用于读出光驱动/Floquet切换前后拓扑不变量的符号变化（符号由 sgn(ηAxAy) 固定）并作为霍尔类响应的可读出判据；随驱动参量增大可出现 ΔC=±1/±2/±3 的拓扑相变序列，f波奇宇称磁体在圆偏光（CPL）下Floquet能带可达 C_lattice=±2，各转变均伴随带隙闭合及隙处贝里曲率的重分布。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| Floquet能带Chern数（f波奇宇称磁体，CPL驱动） | C_lattice = ±2 | 2026-2607.19483-optical-magnetic-switching-in-odd-parity-magnets-with-spin-o |
| 驱动诱导拓扑相变的Chern数变化序列 | ΔC = ±1/±2/±3 | 2025-2504.00122-dynamical-generation-of-higher-order-spin-orbit-couplings-to |
| 基准跳跃幅度 t | 0.2 eV | 2026-2607.19483-optical-magnetic-switching-in-odd-parity-magnets-with-spin-o |
| 自旋轨道耦合强度 λ | 0.12 eV | 2026-2607.19483-optical-magnetic-switching-in-odd-parity-magnets-with-spin-o |
| 交换耦合 J | 0.06 eV | 2026-2607.19483-optical-magnetic-switching-in-odd-parity-magnets-with-spin-o |
| 驱动光子能量 ℏω（对应波长约1240 nm，近红外） | 1.0 eV | 2026-2607.19483-optical-magnetic-switching-in-odd-parity-magnets-with-spin-o |
| 无量纲驱动振幅（示意性强驱动参数） | Ax = Ay = 1.8 | 2026-2607.19483-optical-magnetic-switching-in-odd-parity-magnets-with-spin-o |
| 对应峰值光强（a = 4 Å 时 E0 ≈ 4.5×10^9 V/m） | 约 2.69×10^12 W/cm² | 2026-2607.19483-optical-magnetic-switching-in-odd-parity-magnets-with-spin-o |

## 适用边界

适用边界：在Floquet工程框架下的奇宇称磁性+SOC体系（结论不依赖特定晶格正规化），Chern数改变只能发生在带隙闭合处；文中~2.69×10^12 W/cm²为示意性强驱动而非效应阈值，感应磁化与Floquet隙随驱动强度连续开启且符号在任何强度下由 sgn(ηAxAy) 给定，小费米面体系可在更弱驱动下满足切换条件 kF ≲ |AxAyJ/ω|。

## 代表作

- 2026-2607.19483-optical-magnetic-switching-in-odd-parity-magnets-with-spin-o
- 2025-2504.00122-dynamical-generation-of-higher-order-spin-orbit-couplings-to

## 证据日志

- 2026-09-26｜r36｜回原文｜[paper:2026-2607.19483-optical-magnetic-switching-in-odd-parity-magnets-with-spin-o] Chern数与贝里曲率计算：表征切换前后拓扑不变量的符号变化，给出霍尔类响应的可读出判据。
- 2026-09-26｜r36｜回原文｜[paper:2025-2504.00122-dynamical-generation-of-higher-order-spin-orbit-couplings-to] 陈数与贝里曲率计算：给出ΔC=±1/±2/±3随驱动参量的相变序列及隙处贝里曲率分布。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2504.00122]]
- [[Chern数]]
- [[Floquet工程]]
<!-- /linsai-wikilinks -->
