---
title: "时间分辨二次谐波产生（TR-SHG）"
type: "methods"
created: "2026-10-09T16:48:26Z"
updated: "2026-11-08T05:06:52Z"
tags: ["方法学", "#type/method"]
related: ["2026-2510_16546-high-harmonic-generation-light-source-with-polariz", "2608.13548", "All-optical switching of nonlinear structured light in crystal-engineered van der Waals materials", "arXivID", "二次谐波产生", "非线性光学", "高次谐波产生", "高次谐波产生（HHG）"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-09T16:48:26Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

TR-SHG 采用泵浦–探测构型，通过对称性敏感的二阶非线性光学通道读出瞬态对称破缺，作为分辨量子材料中隐藏相与结构序演化的互补探针（注：本轮另一线索属 HHG 方法，不并入本页）。

## 参数表

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 样品 | 46 nm 厚 3R-MoS₂ 人工晶体（HQ Graphene 块体干法剥离 + 电子束光刻 + 聚碳酸酯印章按 0°/120°/240°/360° 拼接，四区边长 ~8 µm）；偏振分辨 SHG 花瓣图案确认取向 | 研究方法 
| 光路 | 1030 nm Yb 飞秒（150 fs、76 MHz）；参考光 2 mm BBO 倍频；75 mm 透镜聚焦、NA=0.5 物镜收集 + 光谱滤波；TWINS 最小延迟步长 ~0.07 fs | 研究方法 
| 切换结果 | 四种延迟下分别产生 l=+1 涡旋、HG（−45°）、l=−1 涡旋、HG（+45°）；干涉条纹可见度以两倍光学周期振荡（极大=涡旋态、极小=HG 态）——sub-fs 精度 OAM 切换证据 | 主要发现 
| 机制特性 | 几何相位因子 3θ（CP 泵浦）随晶向线性变化、LP 泵浦仅振幅调制（HG01/HG10 相位奇点）；机制与波长无关（无共振）；转换效率对晶向不变（几何相位编码不损耗效率） | 主要发现 
| 激光 | Ti:Sa 10 kHz/1.4 mJ/35 fs/800 nm；SHG 400 nm；MIR 2 µm/540 meV | §激光系统 
| 驱动条件 | 驱动光频率调谐至 ≈ 2ω_phonon（半频参量通道） | 核心要点 
| 光源与几何 | OPO 1030 nm、75 MHz、96 fs；斜入射 β=±50°（透射主装置）；激发物镜 10× NA 0.26；光斑约 1.3 µm；反射装置 NA 0.5、β=±22.5° 同时注入（抑制空间不均）；激子扫描 OPA 3 kHz、约 180 fs、1030–1360 nm | 研究方法·方法卡参数表 
| 样品 | Au 胶带法（150 nm Au/SiO₂/Si+PVP+热释放胶带）从 CVT WS₂ 块体剥出约 1×1 cm² 单晶单层；tear-and-stack 扭转堆叠至 8 层；四层 ⟨0°,30°,60°,90°⟩；扭转角不确定度约 ±1°（偏振分辨 SHG 标定） | 研究方法·方法卡参数表·样品制备 
| 界面手性数值 | χ_xyz,norm：+0.021（⟨0°,30°⟩）/−0.024（⟨0°,−30°⟩，单层归一，反号律验证）；三层 ⟨0°,30°,60°⟩ ≈0.032（相干相加）/⟨0°,30°,0°⟩ ≈0（反号界面相消）；四层激子共振处约 0.14（3 倍增强） | 主要发现·双层/三层/激子共振增强 
| 对称性结论 | 四层赝 4₃ 螺旋禁戒 χ_xxx（正入射信号强抑制、β=±50° 信号几乎相同）；扭 30° 体极限 D12 只允许 χ_xyz；八层 χ_xyz 随厚度近似线性增长 | 主要发现·四层赝螺旋对称·体材料极限 
<!-- src:2608.13548 -->
<!-- src:2026-2510_16546-high-harmonic-generation-light-source-with-polariz -->
<!-- src:2025-2510_12990-dynamical-breaking-of-inversion-symmetry-strong-second -->
<!-- src:2023-2303_06508-tunable-quantum-emitters-in-layered-twisted-bilayer-ws -->

## 适用边界

仅对耦合到二阶极化率的瞬态对称性变化敏感，属间接读出通道，需与其他互补探针联用才能唯一指认隐藏相/结构序，且信号通常较弱、需逐延迟扫描。

## 代表作

- arXiv:2610.11126

## 证据日志

- 2026-10-09｜r60｜仅简报｜[paper:2026-2610.11126-probing-and-manipulating-quantum-materials-with-st] 时间分辨二次谐波产生（TR-SHG）：以对称性敏感的非线性光学通道读出瞬态对称破缺，是分辨隐藏相与结构序演化的互补探针。
- 2026-10-09｜r60｜仅简报｜[paper:2026-2602.09625-macroscopic-spin-orbit-interaction-through-strong-field-pump] 高次谐波产生（HHG）：谐波的波前与偏振结构编码系综局域分子取向，充当自旋-轨道转换的输出通道。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2026-2510_16546-high-harmonic-generation-light-source-with-polariz]]
- [[2608.13548]]
- [[All-optical switching of nonlinear structured light in crystal-engineered van der Waals materials]]
- [[arXivID]]
- [[二次谐波产生]]
- [[非线性光学]]
- [[高次谐波产生]]
- [[高次谐波产生（HHG）]]
<!-- /linsai-wikilinks -->
