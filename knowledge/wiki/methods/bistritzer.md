---
title: "Bistritzer–MacDonald 层间耦合模型（指数衰减跳跃，含衰减长度参数）"
type: "methods"
created: "2026-10-17T23:41:17Z"
updated: "2026-11-01T04:55:12Z"
tags: ["方法学", "#type/method"]
related: ["2608.29062", "arXivID", "层间耦合"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-17T23:41:17Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

Bistritzer–MacDonald 模型以随层间距离指数衰减的跳跃（含衰减长度参数）将转角依赖的层间耦合编码进莫尔连续模型，预言魔角平带；该平带既为器件/实验设计提供目标扭转角窗口，也是转角双层石墨烯 HHG 转角指纹的物理来源。

## 参数表

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 能带模型 | Bistritzer-MacDonald 连续模型：v_F=2.34a eV、w₀/w₁=0.78、θ_mag≈1.12°；8 轨道 Wannier 拟合（跃迁截断 10 个莫尔晶格常数半径）；位置算符对角近似；未掺杂（化学势随温度设置）；两谷假设去耦（各谷满足 C₃/C₂T/镜面 M） | 研究方法·能带模型 
| 激光与数值 | E₀=1×10⁵ V/m；ω=1 meV（微波段，光子能量<平带带宽排除上导带跃迁）；高斯包络 FWHM 23.5 ps；100×100 Monkhorst-Pack k 网格；时间步长 2.41 fs；T₂=1000 fs≈Ω/4（已验证不影响结论）；扫描：转角 1.00–1.35°、温度 20–300 K、Γ-M 与 Γ-K 两方向 | 研究方法·时间演化与 HHG 计算/合并页 Methods 
| 核心结果 | 魔角处 H3/H5/H7 降数个量级（两方向一致）；1.06° vs 1.12° 产额差数个量级；<100 K 凹陷集中于 1.12°、高温后消失偏移；偶次谐波两谷相消 | 主要发现1-2/4/6 
| 魔角序列 | 周期 Δα ≃ 3/2；第一魔角 ~1.09°；预言系列 ~1.09°/2.65°/4.20°…每个均应重现 v_F=0 + 平带 + 最大带隙三重特征 | 核心要点 
| 无序模型 | 四种关联核：白噪声 S(k)=1、幂律 1/k^α、Lorentz 型 1/(1+ξ²k²)、扩展型 1/(1+ξ²k²)^α（最贴合实验畴壁结构）；莫尔模型用 Balents 2019 框架（无序仅通过 Q_μ·ũ(r) 进入 Δ(r) 相位） | 研究方法 
| 数值设置 | trigonally warped 色散 ε(k)=−k²/(2m*)+η(k_x³−3k_xk_y²) 离散为 720 个角向 patch；散射矩阵 W_ij=2πνḡ(k=p_j−p_i)；对称化碰撞算符对角化 + 小 k 二次色散拟合 D；对照基线为匹配平均散射率的 Anderson 白噪声 | 研究方法 
| 填充依赖 | ḡ(k) 在 k≈q_μ 发散，2k_F≈q₀（由 filling 决定）时无序效应强烈依赖掺杂浓度——与 tBLG 整数填充强关联相实验呼应 | 主要发现 
| TBG 模型 | Bistritzer-MacDonald 连续模型，θ=1.13°，电荷中性点；中心窄带 W≈5 meV；v_F≈17 km/s（数值 17.5）；a=0.246 nm、L_M=a/[2sin(θ/2)]、A_M=√3L_M²/2 | 研究方法·第1-2段 
| 驱动场 | 圆偏振 A(t)=(E/Ω)[cosΩt x̂−sinΩt ŷ]；Ω=5 meV/ℏ（窄带内单光子共振，W≤ℏΩ<2W）；Floquet 谐波截断：玩具模型 ±12、连续模型 ±6 | 研究方法·第1段 
| 速度与声子 | 玩具模型：重标两层石墨烯紧束缚 W=3.1 meV、v⁰_eff=18.9 km/s；连续模型 v⁰_eff=19.5 km/s；c_ph∈[17.9, 19.4] km/s；T_ph=1 K | 研究方法·第3段 
<!-- src:2024-2302_04127-high-harmonic-generation-with-a-twist-all-optical-char -->
<!-- src:2019-1808_05250-origin-of-magic-angles-in-twisted-bilayer-graphene -->
<!-- src:2608.29062 -->
<!-- src:2023-2301_02248-optical-control-of-slow-topological-electrons-in-moiré -->

## 适用边界

属低能莫尔连续近似，适用于小扭转角、长波莫尔尺度且平带物理主导的情形；层间跳跃幅度与衰减长度为唯象参数，需对具体堆叠方式与晶格弛豫效应标定，大角度或强弛豫时需修正。

## 代表作

- arXiv:2104.03311
- arXiv:1802.00652

## 证据日志

- 2026-10-17｜r81｜仅简报｜[paper:2021-2104.03311-high-order-harmonic-generation-from-twisted-bilayer-graphene] Bistritzer–MacDonald 层间耦合模型（指数衰减跳跃，含衰减长度参数）：将转角依赖的层间耦合编码进莫尔能带，是 HHG 转角指纹的物理来源。
- 2026-10-17｜r81｜仅简报｜[paper:2018-1802.00652-unconventional-superconductivity-in-magic-angle-graphene-sup] Bistritzer–MacDonald莫尔连续模型：该理论预言的魔角平带为器件设计提供了目标扭转角窗口，是实验设计的物理基础。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2608.29062]]
- [[arXivID]]
- [[层间耦合]]
<!-- /linsai-wikilinks -->
