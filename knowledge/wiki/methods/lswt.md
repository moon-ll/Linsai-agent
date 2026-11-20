---
title: "线性自旋波理论（LSWT）磁振子带计算"
type: "methods"
created: "2026-10-31T06:43:16Z"
updated: "2026-11-01T11:30:00Z"
tags: ["方法学", "#type/method"]
related: ["2025-2506.21661-microscopic-origin-of-the-magnetic-interactions-and-their-ex", "MnPS3"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-31T06:43:16Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

线性自旋波理论（LSWT）在给定自旋哈密顿量（如由微观提取的交换参数 J 构建的模型，或光修饰后的有效哈密顿量）基础上，对磁有序基态做线性化自旋波展开，解析或数值计算磁振子色散与谱权重，为谱学实验提供可直接对比的理论谱，并可用于光调控体系（如 MnPS3）的磁振子能带与自旋分裂谱计算。

## 参数表

**终极升级**（2026-11-01，canonical 要素，引用已核实/库内锚）：
线性自旋波理论（LSWT）：围绕磁基态做 Holstein–Primakoff 变换，把自旋涨落映射为玻色子（磁振子），线性阶解析给出磁振子色散 ω(q) 与谱强——磁有序材料低能激发的标准工具，亦是交磁体 HHG 谱签名对称性分析的低能输入。

| HP 变换 | $S^z = S - a†a$，$S^+ ≈ √(2S)a$（铁磁参考态） | [1] |
| 色散 | LSWT 矩阵对角化给出 ω(q)（单 Q 非公度结构通式见 SpinW） | [1] |
| 工具 | SpinW（MATLAB）：单 Q 非公度磁结构 LSWT 通用实现 | [1] |

✅ 磁振子色散/谱强、交磁体低能模型参数锚定。
❌ 线性阶忽略磁振子-磁振子相互作用（强场/高温需 1/S 修正）；非共线磁序需局域坐标系框架。

- S. Toth, B. Lake, "Linear spin wave theory for single-Q incommensurate magnetic structures," J. Phys.: Condens. Matter 27, 166002 (2015). https://doi.org/10.1088/0953-8984/27/16/166002

## 适用边界

结果可靠性受输入哈密顿量与交换参数 J 提取精度的限制，且线性近似仅适用于磁有序态附近的小振幅自旋涨落（低温、远离磁相变与强非线性/强阻挫区），此时磁振子-磁振子相互作用可忽略。

## 代表作

- arXiv:2506.21661
- arXiv:2505.31411

## 证据日志

- 2026-10-31｜r104｜仅简报｜[paper:2025-2506.21661-microscopic-origin-of-the-magnetic-interactions-and-their-ex] 线性自旋波理论（LSWT）磁振子带计算：基于提取的J给出磁振子色散与谱权重，为谱学实验提供直接可对比的理论谱。
- 2026-10-31｜r104｜仅简报｜[paper:2025-2505.31411-odd-parity-magnons] 线性自旋波理论（LSWT）：在光修饰后的有效哈密顿量下解析/数值给出 MnPS3 磁振子能带与自旋分裂谱。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2025-2506.21661-microscopic-origin-of-the-magnetic-interactions-and-their-ex]]
- [[MnPS3]]
<!-- /linsai-wikilinks -->
