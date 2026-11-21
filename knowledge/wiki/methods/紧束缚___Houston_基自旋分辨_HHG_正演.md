---
title: "紧束缚 + Houston 基自旋分辨 HHG 正演"
type: "methods"
created: "2026-10-31T11:38:12Z"
updated: "2026-11-15T15:09:19Z"
tags: []
related: ["arpes", "houston", "材料体系HHG方法", "自旋劈裂"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
source_reliability: "reliable"
sources: ["{"title": "general-new-idea-20260822", "source_type": "archived_proposal"}"]
- title: "general-new-idea-20260822"
source_type: "archived_proposal"
---

> ⚠ **状态标注（2026-11-01 颗粒度体检）**：本页正文素材不足以支撑「参数表≥5行」的达标线（指导学生复现），如实保持低密度工作页状态，待深读素材回补后升级。已在专题关联网络中。
方法手册方法 1：Step 1 用 8 带（4 价带+4 导带）紧束缚模型构造能带，k 点默认 20³、收敛 30³，参数取自 ARPES（Krempaský 2024；Osumi 2024）；Step 2 引入 g 波自旋劈裂项 H_alt(k) = Δ(k)·σ_z⊗f(k)，Δ(k) 取 0.3–0.8 eV，f(k) 为满足六方对称、三重方位角依赖（θ→θ+2π/3）的解析函数，与 Y₄⁻³ 型四组节点面结构一致。

## 参数表

**终极升级**（2026-11-01，canonical 要素，引用已核实/库内锚）：
紧束缚 Houston 基自旋分辨 HHG 正演：以 Houston 基（加速度 Bloch 态）构造自旋分辨的最小 TB 模型，正演计算自旋向上/向下通道的谐波谱——交磁体 d-wave 劈裂谱签名（3ω/5ω 各向异性）的数值引擎（[[houston]] 的自旋扩展）。

| 基组 | Houston 基：严格满足加速度定理的平移 Bloch 态 | [[houston]] |
| 自旋分辨 | H = H_orb⊗σ₀ + H_ex·σ_z（交磁 d-wave 劈裂场） | [[材料体系HHG方法]] |
| 正演输出 | 自旋分辨谐波谱 I_↑(ω)/I_↓(ω) → 各向异性比率 | [[材料体系HHG方法]] |

✅ 交磁体 HHG 签名的最小正演引擎（对照 Werner 3ω~15%/5ω~30% 预言）。
❌ 单带近似；SOC 强体系需四带；退相干 T₂ 需外置。

- P. Werner, M. Lysne, Y. Murakami, PRB 110, 235101 (2024). https://doi.org/10.1103/PhysRevB.110.235101

## 代表作

- P. Werner, M. Lysne, Y. Murakami, PRB 110, 235101 (2024). https://doi.org/10.1103/PhysRevB.110.235101

## 适用边界

✅ 交磁体 HHG 签名的最小正演引擎（对照 Werner 3ω~15%/5ω~30% 预言）。
❌ 单带近似；SOC 强体系需四带；退相干 T₂ 需外置。



---

8 带（4V+4C）紧束缚模型，k 点默认 20³、收敛 30³；能带参数取自 ARPES（Krempaský 2024、Osumi 2024）；g 波自旋劈裂项 H_alt(k) = Δ(k)·σ_z ⊗ f(k)，Δ(k) 取 0.3–0.8 eV，f(k) 为三重方位角依赖的六方对称解析函数（与 Y₄⁻³ 四组节点面一致）。

<!-- linsai-wikilinks -->
## 关联概念

- [[arpes]]
- [[houston]]
- [[材料体系HHG方法]]
- [[自旋劈裂]]
<!-- /linsai-wikilinks -->
