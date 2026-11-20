---
title: "Keldysh 参数判据（隧穿极限）"
type: "methods"
created: "2026-10-11T14:03:29Z"
updated: "2026-11-01T04:55:12Z"
tags: ["方法学", "#type/method"]
related: ["1409.2725", "2503.14531", "2507.03996", "arXivID", "强场电离"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-11T14:03:29Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

Keldysh 参数 γ（随场强增大、频率降低而减小）区分强场电离机制：γ≲1 时电子-空穴对在峰值场经带间隧穿产生、三步图像适用；γ≈1 标定隧穿-多光子过渡区，指示体系工作在非微扰强场区间。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 隧穿极限阈值（三步图像适用条件） | γ≲1（无量纲） | paper:2014-1409.2725-theoretical-analysis-of-high-harmonic-generation-in-solids |
| 隧穿-多光子过渡区位置 | γ≈1（无量纲） | paper:2011-1112.1139-redshift-in-the-optical-absorption-of-zno-single-crystals-in |

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| zeta 参数（纳米结尺寸判据） | ζ = γ·ln(γ+√(1+γ²))/(2δ)，无量纲 | [[2503.14531]] |
| regime 分界 | ζ > 1：光子辅助隧穿主导（与 γ 无关）；ζ < 1：激光场/Keldysh 主导 | [[2503.14531]] |
| 光子辅助隧穿电流特征 | J ~ exp[−2d·√(2m(|E0|eff − nħω))/ħ]（矩形势垒指数衰减） | [[2503.14531]] |
| 基本信息 | arXiv:2511.15100（2025，4 作者） | 核心要点 |
| 可调参数总数 | 5个（归一化前因子a0 + a1–a4） | [[2507.03996]]（arXiv 2507.03996） |
| 拟合输入电离概率 | 51个（单一强度8×10¹³ W/cm²） | [[2507.03996]] |
| 验证波长范围 | 0.2–1.2 μm | [[2507.03996]] |
| 验证强度范围 | 0.8–1.5×10¹⁴ W/cm² | [[2507.03996]] |
| 经典轨迹验证的电子到达阈值 | r ≥ 21 Å | [[2507.03996]] |
| 准静态隧穿指数因子 | e^{-2κ³/3|E|}（Eq.11），另含Tong-Lin型修正e^{-κ(a1a2)²|E|} | [[2507.03996]] |
<!-- src:2503.14531 -->
<!-- src:2025-2511_15100-thermalization-of-quantum-light-induced-by-classical-n -->
<!-- src:2507.03996 -->

## 适用边界

三步图像与带间隧穿描述仅在 γ≲1 的隧穿极限内可靠；γ≈1 处于隧穿-多光子机制混合的过渡区，判据仅作半定量分界，γ 明显大于 1 后隧穿极限图像失效。

## 代表作

- paper:2014-1409.2725-theoretical-analysis-of-high-harmonic-generation-in-solids
- paper:2011-1112.1139-redshift-in-the-optical-absorption-of-zno-single-crystals-in

## 证据日志

- 2026-10-11｜r73｜仅简报｜[paper:2014-1409.2725-theoretical-analysis-of-high-harmonic-generation-in-solids] Keldysh 参数判据（隧穿极限）：划定三步图像适用范围：γ≲1 时电子-空穴对在峰值场经带间隧穿产生。
- 2026-10-11｜r73｜仅简报｜[paper:2011-1112.1139-redshift-in-the-optical-absorption-of-zno-single-crystals-in] Keldysh 参数分析：量化 γ≈1 的隧穿-多光子过渡区，标定体系工作在非微扰强场区间。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[1409.2725]]
- [[2503.14531]]
- [[2507.03996]]
- [[arXivID]]
- [[强场电离]]
<!-- /linsai-wikilinks -->
