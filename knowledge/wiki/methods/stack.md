---
title: "hBN封装双栅扭转双层石墨烯器件制备（tear-and-stack拣取转移）"
type: "methods"
created: "2026-10-17T23:41:46Z"
updated: "2026-11-01T04:55:12Z"
tags: ["方法学", "#type/method"]
related: ["2026-2608_04151-valley-polarization-of-moiré-interlayer-exciton-co", "arXivID"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-17T23:41:46Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

采用tear-and-stack定向拣取转移技术将单层石墨烯撕裂后按设定角度旋转堆叠，并以hBN封装构成扭转双层石墨烯（TBG）双栅（顶栅+底栅）器件，可将扭转角精准控制在魔角附近（约1.1°），同时独立调控载流子密度（填充因子）与垂直位移场，为观测平带关联绝缘与超导等关联相提供实验前提。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 扭转角（魔角） | 约1.1° | arXiv:1802.00553; arXiv:1802.00652 |

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 光源与几何 | OPO 1030 nm、75 MHz、96 fs；斜入射 β=±50°（透射主装置）；激发物镜 10× NA 0.26；光斑约 1.3 µm；反射装置 NA 0.5、β=±22.5° 同时注入（抑制空间不均）；激子扫描 OPA 3 kHz、约 180 fs、1030–1360 nm | 研究方法·方法卡参数表 
| 样品 | Au 胶带法（150 nm Au/SiO₂/Si+PVP+热释放胶带）从 CVT WS₂ 块体剥出约 1×1 cm² 单晶单层；tear-and-stack 扭转堆叠至 8 层；四层 ⟨0°,30°,60°,90°⟩；扭转角不确定度约 ±1°（偏振分辨 SHG 标定） | 研究方法·方法卡参数表·样品制备 
| 界面手性数值 | χ_xyz,norm：+0.021（⟨0°,30°⟩）/−0.024（⟨0°,−30°⟩，单层归一，反号律验证）；三层 ⟨0°,30°,60°⟩ ≈0.032（相干相加）/⟨0°,30°,0°⟩ ≈0（反号界面相消）；四层激子共振处约 0.14（3 倍增强） | 主要发现·双层/三层/激子共振增强 
| 对称性结论 | 四层赝 4₃ 螺旋禁戒 χ_xxx（正入射信号强抑制、β=±50° 信号几乎相同）；扭 30° 体极限 D12 只允许 χ_xyz；八层 χ_xyz 随厚度近似线性增长 | 主要发现·四层赝螺旋对称·体材料极限 
| 实验配置 | attoDRY800 5 K；703 nm 脉冲（200 kHz、<70 ps、1.765 eV）；IRF = 890 ps；光谱分辨率 2 nm；低/高 IX 密度 37.5 nW / 1.5 µW；IXX 比 IX 蓝移 30 meV；CW 阈值 ~750 nW、I_IXX ∝ P^1.2 | 研究方法（同源记录）/ 主要发现 
| 再极化机制 | 激发后 ~1 ns 短暂极化 → 10 ns 内基本无偏振（衰减比 IX 快两个数量级）→ ν_IX→1 时圆偏振回升至 ~0.6（IX 仅 ~0.3）；线偏振激发下不出现；机制：单占据位点近满时 IXX 从多数谷复合一个激子留下少数谷 IX——与极化 IX 库相互作用驱动（打破时间反演） | 主要发现与核心结论（同源记录） 
| 器件 | D0.94/D1.02/D1.03/D1.12（扭角）；Cr/Au 5/60 nm 接触；部分衬底 285 nm SiO₂ | §样品与制备 
| 输运/测量温度 | 4 K 恒温器锁相交流电测；霍尔 0.7 T；10 K 附近整数填充电阻振荡；THz 光电流 1.6–20 K | §输运/THz 测量 
| 哈密顿量参数 | κ±=[4π/(3a_M)](−√3/2,∓1/2)；Δ±(r)=2VΣ_{j=1,3,5}cos(g_j·r±ψ)；ΔT(r)=w(1+e^{−ig₂r}+e^{−ig₃r}) | §方法卡1 
| 光源 | 1550 nm 宽带超辐射二极管，3 dB 带宽 90 nm（ℏω ≈ 0.8 eV）；10 m 保偏光纤入 ³He 恒温器；4.5 µm 光斑 | 研究方法·方法卡（装置配置） 
<!-- src:2023-2303_06508-tunable-quantum-emitters-in-layered-twisted-bilayer-ws -->
<!-- src:2026-2608_04151-valley-polarization-of-moiré-interlayer-exciton-co -->
<!-- src:2025-2406_16532-terahertz-photocurrent-probe-of-quantum-geometry-and-i -->
<!-- src:2025-2509_07360-quantum-phases-in-twisted-homobilayer-transition-metal -->
<!-- src:2026-2606_06389-revealing-quantum-geometry-effects-in-magic-angle-twis -->

## 适用边界

有效性强依赖扭转角精准对准至魔角附近（约1.1°，角度控制精度是形成可观测平带关联相的前提），并需hBN封装保证界面洁净及双栅对填充因子与垂直位移场的独立调控能力；逐片手工拣取转移导致制备通量与良率受限。

## 代表作

- paper:2018-1802.00553-correlated-insulator-behaviour-at-half-filling-in-magic-angl
- paper:2018-1802.00652-unconventional-superconductivity-in-magic-angle-graphene-sup

## 证据日志

- 2026-10-17｜r81｜仅简报｜[paper:2018-1802.00553-correlated-insulator-behaviour-at-half-filling-in-magic-angl] hBN封装双栅扭转双层石墨烯器件制备（tear-and-stack拣取转移）：实现约1.1°精度的魔角样品，并独立调控载流子密度与垂直位移场。
- 2026-10-17｜r81｜仅简报｜[paper:2018-1802.00652-unconventional-superconductivity-in-magic-angle-graphene-sup] hBN封装TBG双栅器件与tear-and-stack定向转移技术：实现扭转角精准控制（~1.1°）并独立调控填充因子与垂直位移场，是观测平带关联相的实验前提。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2026-2608_04151-valley-polarization-of-moiré-interlayer-exciton-co]]
- [[arXivID]]
<!-- /linsai-wikilinks -->
