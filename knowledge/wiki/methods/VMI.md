---
title: "VMI"
type: "methods"
created: "2026-06-17T12:40:33Z"
updated: "2026-11-15T01:19:45Z"
tags: ["表征方法", "光电子", "动量成像", "type/method", "topic/HHG", "status/mature", "status/growing"]
related: ["2024-s41467-024-44775-5-spatiotemporal-imaging-and-shaping-of-electron-wave-function", "2026-2604_06703-strong-field-ionization-of-atoms-with-bright-squeezed-vacuum", "2604.06703", "COLTRIMS", "RABBIT", "RABBITT", "VMI 双色 RABBIT 光电子谱", "strong-field-ionization", "强场电离"]
source_raw: ""
growth_stage: "mature"
confidence: 0.9
aliases: ["velocity-map-imaging", "速度映射成像"]
updated_at: "2026-11-15T01:19:45Z"
settled_count: 5
merged_from: ["wiki/concepts/VMI.md"]
---

• # VMI（速度映射成像）

  ## 原理

  VMI（速度映射成像）利用静电透镜将光电子（及离子）初速度矢量映射为位置灵敏探测器上的二维分布，测量二维动量谱以提取电子波包干涉图样的角向/径向结构。一次曝光即可获得完整的角度分辨光电子动量分布，是 RABBITT、COLTRIMS 等实验的标准探测方案。

  可分辨 Xe 强场电离的角向-能量分布及对 BSV 驱动场强量子涨落稳健的蜘蛛状全息条纹，且谱中编码的飞秒脉冲波形与强度信息可被机器学习提取用作脉冲表征；与 TimePix 类像素阵列探测器结合可在探测面直接获得高动量分辨的电子/离子谱并实现快速阵列式粒子符合探测；进一步地，角分辨三维电子动量成像/符合测量（VMI/COLTRIMS 类）是提取二色不对称度、分离螺旋度通道并重构光场偏振态（圆偏振阿秒计量）的实验关键。

  **canonical 升级**（2026-11-01，教科书级方法要素，引用已核实）：
  速度映射成像（VMI）用静电透镜把光碎片/光电子按初始速度一比一映射到位置敏感探测器，反演后直接给出三维动量分布——阿秒条纹/RABBITT 实验的标准探测端。

  | 要素 | 内容 | 出处 |
  | --- | --- | --- |
  | 映射条件 | 等焦条件：静电透镜使同速度粒子聚焦于探测器同半径 | [1] |
  | 探测器 | MCP + 荧光屏 + 相机；层析或 pBasex 反演 | [1] |
  | 分辨 | 典型 Δp/p 百分比量级（电压比与谱仪长度定） | [1] |

  ✅ 光电子/离子三维动量谱；COLTRIMS 反应显微镜的核心成像单元。
  ❌ 只测动量投影（需层析重构 3D）；对超快过程本身时间分辨取决于泵浦-探测而非 VMI。

  - A. T. J. B. Eppink, D. H. Parker, "Velocity map imaging of ions and electrons using electrostatic lenses," Rev. Sci. Instrum. 68, 3477–3484 (1997). https://doi.org/10.1063/1.1148310

  ## 核心要点

  - 静电透镜聚焦 → 位置 = f(初始速度)
  - 探测器：MCP + 荧光屏 + CCD/相机
  - 与 RABBITT 结合：角度分辨的阿秒时间延迟测量

  ## 参数表

  | 参数 | 数值 | 出处 |
  | --- | --- | --- |
  | BSV驱动场二阶关联函数g(2) | 2.18 / 1.97 / 1.83 / 1.78（随脉冲能量增大而减小） | paper:2026-2604.06703-strong-field-ionization-of-atoms-with-bright-squeezed-vacuum |
  | q-QTMC模拟所用平均峰值光强 | 0.53 / 0.80 / 1.33 ×10^14 W/cm² | paper:2026-2604.06703-strong-field-ionization-of-atoms-with-bright-squeezed-vacuum |
  | BSV平均脉冲能量 | 3.3 / 5.0 / 8.3 μJ | paper:2026-2604.06703-strong-field-ionization-of-atoms-with-bright-squeezed-vacuum |

  ## 适用边界

  作为二维投影式测量通常需满足轴对称条件、或采用切片/符合技术（如与像素阵列结合的粒子符合探测）才能重构三维动量分布，而二色不对称度提取、螺旋度通道分离与偏振态重构等任务必须依赖角分辨三维动量谱/符合测量而非二维投影单独完成；径向能量分辨受驱动场噪声制约（强度涨落经 ac-Stark 位移模糊能量位置、抹平 ATI 环）而全息干涉结构对量子涨落具韧性；基于动量谱的脉冲参数机器学习反演依赖训练数据质量与信息编码完整性，其精度上限仍受谱仪自身能量/动量分辨本领限制；符合探测的分辨与吞吐受像素阵列读出速度/时间性能约束（具体数值历轮证据均未提供）。

  ## 简报关联

  - 2026-11-10 简报以「VMI 双色 RABBIT 光电子谱（67 as 步进）」形式出现，出自 2611.10970 工作。

  ## 代表作

  - paper:2024-s41467-024-44775-5-spatiotemporal-imaging-and-shaping-of-electron-wave-function
  - paper:2026-2604.06703-strong-field-ionization-of-atoms-with-bright-squeezed-vacuum
  - paper:2023-2303.13940-femtosecond-pulse-parameter-estimation-from-photoelectron-mo
  - paper:2025-2603.04942-fast-array-based-particle-coincidence-detection-in-a-timepix
  - paper:2022-2211.02769-attosecond-metrology-in-circular-polarization

  ## 证据日志

  - 2026-09-13｜r15｜仅简报｜[paper:2024-s41467-024-44775-5-spatiotemporal-imaging-and-shaping-of-electron-wave-function] 动量分辨电子谱探测（VMI/COLTRIMS类）：测量二维光电子动量分布以获取干涉图样及其角向/径向结构。
  - 2026-09-19｜r25｜回原文｜[paper:2026-2604.06703-strong-field-ionization-of-atoms-with-bright-squeezed-vacuum] 光电子动量谱成像（VMI/COLTRIMS类测量）：分辨Xe电离的角向-能量分布及蜘蛛状全息结构随驱动场量子统计的变化。
  - 2026-10-09｜r61｜仅简报｜[paper:2023-2303.13940-femtosecond-pulse-parameter-estimation-from-photoelectron-mo] 光电子动量谱成像（VMI类测量）：作为反演输入观测量，验证动量分布中编码的脉冲波形与强度信息可被机器提取。
  - 2026-10-11｜r72｜仅简报｜[paper:2025-2603.04942-fast-array-based-particle-coincidence-detection-in-a-timepix] 速度映射成像（VMI）：静电透镜把动量映射到探测面，与像素阵列结合获得高动量分辨的电子/离子谱。
  - 2026-10-31｜r105｜仅简报｜[paper:2022-2211.02769-attosecond-metrology-in-circular-polarization] 三维电子动量成像/符合测量（VMI/COLTRIMS类）：角分辨三维动量谱是提取二色不对称度、分离螺旋度通道并重构偏振态的实验关键。

  ## 来源

  - arXiv: 0908.2575（动量空间层析）；`hhg-methods-report.md`

<!-- linsai-wikilinks -->
## 关联概念

- [[2024-s41467-024-44775-5-spatiotemporal-imaging-and-shaping-of-electron-wave-function]]
- [[2026-2604_06703-strong-field-ionization-of-atoms-with-bright-squeezed-vacuum]]
- [[2604.06703]]
- [[COLTRIMS]]
- [[RABBIT]]
- [[RABBITT]]
- [[VMI 双色 RABBIT 光电子谱]]
- [[strong-field-ionization]]
- [[强场电离]]
<!-- /linsai-wikilinks -->
