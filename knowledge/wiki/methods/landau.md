---
title: "Landau-Zener 隧穿模型（非绝热近似）"
type: "methods"
created: "2026-10-23T20:00:53Z"
updated: "2026-11-08T05:06:52Z"
tags: ["方法学", "#type/method"]
related: ["2024-2404.08466-a-different-perspective-on-the-landau-zener-dynamics", "2026-2503_04431-observation-of-non-adiabatic-landau-zener-tunnelin", "2404.08466", "2503.04431"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.6
updated_at: "2026-10-23T20:00:53Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

Landau-Zener 隧穿以 P≈exp(−πΔ²/(2ħv)) 将回避交叉处的非绝热布居转移量化为能隙 Δ 与失谐扫描速率 v 的竞争，是线性扫频二能级回避交叉的标准基准；新证据将其推广为强场非线性光-物质相互作用中 Floquet 修饰态间的一般非微扰机制——修饰光电子终态在与其他 Floquet 态形成的回避交叉处经 LZ 隧穿获得布居，使高场强下多光子光电子能谱出现 Floquet 修饰（微扰）图像无法描述的附加结构。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 观测特征场强 F0^exp（AT 劈裂/LZ 特征出现的场强区间） | ~2.2 V/nm | arXiv:2503.04431 |
| 驱动光子能量 ωp（置于 SS-IP1 间隙的 1/3 以增强三光子共振 4PP） | 1.54 eV | arXiv:2503.04431 |
| 相干泵浦/探测脉冲宽度 | 20 fs | arXiv:2503.04431 |
| 脉冲延迟扫描相位精度 | 50 as | arXiv:2503.04431 |
| ITR-4PP 信号在驱动频率处的振荡周期 | 2.7 fs | arXiv:2503.04431 |
| IP1-SS 相干修饰保持时间（相干性远慢于脉冲包络，支撑相干 LZ 动力学） | ~10 fs | arXiv:2503.04431 |

## 适用边界

模型依赖线性扫频（恒定失谐速率 v）下孤立回避交叉的二能级相干近似：低场强下微扰 Floquet 修饰图像（Autler-Townes 劈裂）仍成立，只有当场强进入非微扰区（Cu(111) 实验中 F0≳2.2 V/nm 谱偏离二重劈裂、出现中央主峰等附加结构）才必须以修饰态间 LZ 隧穿描述，且其实验验证需要阿秒相位精度与场幅可控的 ITR-mPP，成本与复杂度较高。

## 代表作

- arXiv:2503.04431
- arXiv:2404.08466

## 证据日志

- 2026-10-23｜r87｜回原文｜[paper:2026-2503.04431-observation-of-non-adiabatic-landau-zener-tunnelin] Landau-Zener 隧穿模型（非绝热近似）：以 P≈exp(−πΔ²/(2ħv)) 把边带布居转移量化为能隙与失谐扫描速率的竞争，给出绝热-非绝热边界的判据。
- 2026-10-23｜r87｜仅简报｜[paper:2024-2404.08466-a-different-perspective-on-the-landau-zener-dynamics] Landau-Zener二能级模型：作为线性扫频回避交叉的标准基准，文中以其为载体重构跃迁概率的解析推导

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2024-2404.08466-a-different-perspective-on-the-landau-zener-dynamics]]
- [[2026-2503_04431-observation-of-non-adiabatic-landau-zener-tunnelin]]
- [[2404.08466]]
- [[2503.04431]]
<!-- /linsai-wikilinks -->
