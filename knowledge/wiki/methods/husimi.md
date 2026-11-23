---
title: "Husimi Q函数零差层析（正交分量同步测量）"
type: "methods"
created: "2026-10-31T16:56:04Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "#type/method"]
related: ["2501.09424", "2512.08540", "arXivID"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-31T16:56:04Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

通过双零差（双平衡探测）以注入真空噪声为代价实现正交分量X、P的单次同步采样，从而直接测得处处正定的Husimi Q函数准概率分布，既规避了Wigner函数负值重构的病态性，也无需完整的层析重构。

## 参数表

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 驱动构型 | 800 nm 强相干场 + 1600 nm 弱 BSV（微焦级）；两色延迟以阿秒精度扫描 | 研究方法·驱动方案 
| 对称性关系 | σ3=−σ1、σ4=−σ2；奇阶 |cosσ1+cosσ2|²、偶阶 |cosσ1−cosσ2|²、半整数阶 |i sinσ1±sinσ2|² | 研究方法·干涉原理 
| 半整数谐波统计 | g⁽²⁾≈2.3，与输入 BSV 匹配（单 BSV 光子过程） | 主要发现·1 
| 偶阶谐波统计 | g⁽²⁾≈4.8 超聚束，与输入 BSV 峭度 ⟨n̂⁴⟩/⟨n̂²⟩² 匹配（双 BSV 光子过程） | 主要发现·1 
| 亚周期调制 | 均值强度以 400 nm 周期（基频半周期）调制；g⁽²⁾ 与均值同相；奇阶振荡来自相干态与四 BSV 光子过程干涉（σ⁴ 阶） | 主要发现·2 
| 隧穿涨落压缩 | 相邻四阶谐波反解单发 σ1,2；β1–β2 负相关（一次隧穿噪声大则半周期后受抑）——可调量子性质隧穿势垒 | 主要发现·3 
| Husimi 层析特征 | H12.5（64 nm）非高斯压缩猫态（双瓣+中心洞）；H12（66 nm）单正交拉伸；H13（61.5 nm）主瓣+朝原点尾 | 主要发现·4 
| 探测波段 | 谐波 11–22 区间（示例 61.5–66 nm） | 研究方法·体系 
| 基准参数 | r=1.0（≈8.69 dB 压缩）、θ=φ=0、g=1.5；Wigner 全网格扫描 m=0–5 × n=0–4；保真度扫描 r∈[0,3]、g∈(1,10] | 研究方法·计算设置 
| (1,2) 大振幅猫态 | r=1.0、g=1.5：F₁=0.992（γ=0.803，α=2.0）；r=0.5 时 F_max=0.999（α=1.191）；F₁>0.99 的 α 范围 1.565–2.029 | 主要发现 
<!-- src:2025-2511_18362-attosecond-resolved-quantum-fluctuations-of-light-and- -->
<!-- src:2026-2605_23617-multiphoton-heralding-generates-large-amplitude-squeez -->

## 适用边界

以向探测端口注入真空噪声（劣化测量灵敏度）为代价；且Q函数为平滑化的准概率分布、处处正定，无法直接判读Wigner负性等精细非经典特征。

## 代表作

- arXiv:2501.09424
- arXiv:2512.08540

## 证据日志

- 2026-10-31｜r107｜仅简报｜[paper:2025-2501.09424-from-tomography-of-conditional-states-to-tomography-of-state] Husimi Q函数零差层析（正交分量同步测量）：以注入真空噪声为代价实现X、P单次同步采样，直接测得处处正定的Q函数，规避Wigner负值重构的病态性
- 2026-10-31｜r107｜仅简报｜[paper:2025-2512.08540-tunable-passive-squeezing-of-squeezed-light-through-unbalanc] Husimi Q函数直接采样测量：双零差同时测量X与P，单次采样即可直接获得准概率分布而无需完整层析重构。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2501.09424]]
- [[2512.08540]]
- [[arXivID]]
<!-- /linsai-wikilinks -->
