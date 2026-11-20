---
title: "2025-2505.09187-wavefunction-free-approach-for-predicting-nonlinear-response"
type: "papers"
created: "2026-11-02T00:02:56Z"
updated: "2026-11-15T15:09:20Z"
tags: []
related: ["Berry 曲率", "Berry曲率", "Berry曲率偶极", "Weyl semimetal", "Weyl半金属", "强场超快", "非线性光学", "非线性光学响应"]
source_raw: "2025-2505.09187-wavefunction-free-approach-for-predicting-nonlinear-response.md"
growth_stage: "seedling"
confidence: 0.5
digest_level: "abstract"
---

• 我先读取原始论文和 skill 规范。

• 蒸馏完成。以下为入库正文（worker 落盘时注入 frontmatter）：

  # Wavefunction-Free Approach for Predicting Nonlinear Responses in Weyl Semimetals

  ## 研究问题（Research Question）

  能否在不显式求解/使用电子波函数的前提下，可靠预测 [[Weyl半金属]] 的非线性光学响应？本文以圆偏振光电流效应（CPGE，圆偏光整流）为具体算例，验证免波函数框架的可行性，并给出 [[Berry曲率偶极]]（BCD）的免波函数表达式。

  ## 背景（Background）

  [[非线性光学响应]]是探测拓扑半金属能带几何性质（[[Berry曲率]] 及其偶极矩）的核心手段，BCD 主导的 CPGE 电流是 [[Weyl半金属]] 的标志性输运/光学信号。常规第一性原理计算依赖完整的电子波函数与占据态求和，计算代价高，限制了对大体系、大范围参数扫描和非平衡响应的高效预测。

  ## 研究方法（Data & Method）

  - 构建不依赖波函数的响应预测框架：绕过显式波函数，从可计算的量（如单粒子谱函数/格林函数类信息）直接构造非线性响应。
  - 以圆偏光整流（CPGE 型的直流整流电流）为基准算例，与传统波函数方法对照验证。
  - 由该框架出发，解析导出 Berry 曲率偶极的免波函数公式，使 BCD 可在无波函数表示下计算。

  ## 主要发现（Main Results & Findings）

  - 免波函数方法可成功复现 Weyl 半金属的非线性响应（圆偏光整流），与波函数方法结果一致。
  - 计算速度较常规方法提升约千倍（原始摘要级信息，"千倍"为原文给出的量级）。
  - 导出 Berry 曲率偶极的免波函数解析公式，把 BCD 的计算从波函数表示中解放出来。

  ## 潜在研究方向（Limitations & Open Questions）

  - 摘要级信息未给出具体验证的材料体系清单与误差定量分析，正式引用时需回查原文核对基准体系与精度。
  - 免波函数响应公式向其他非线性效应（高次谐波、太赫兹整流、强场区）推广的条件尚待系统检验。
  - 与温度、无序、相互作用修正的耦合是否保持免波函数优势，是走向真实实验预言前需回答的问题。
  - 千倍加速若属实，对 [[强场超快]] 方向的大尺度非线性响应扫描与高通量材料筛选有潜在方法学价值。

  ---

  **说明**（给 worker/上游）：raw 条目 frontmatter 的 `abstract` 字段为空，正文仅有一行中文摘要；以上蒸馏严格基于该摘要级信息，未虚构具体材料体系、数值误差或实验参数，符合摘要级不编造数值的纪律。正文字数满足 ≥200 字质量门。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：Weyl 半金属非线性响应的免波函数预测框架（CPGE 算例 + Berry 曲率偶极解析公式）

**原理**：绕过显式电子波函数，从可计算量（单粒子谱函数/格林函数类信息）直接构造非线性响应：以圆偏光整流（CPGE）为基准算例与传统波函数方法对照验证——复现 Weyl 半金属非线性响应且结果一致；并由该框架解析导出 Berry 曲率偶极（BCD）的免波函数公式，把 BCD 计算从波函数表示中解放出来。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 计算速度提升 | 较常规波函数方法约千倍（原文量级口径） | 主要发现（Main Results & Findings） |

**适用边界**：摘要级：验证材料体系清单与误差定量分析未给，正式引用需回查原文；向高次谐波/太赫兹整流/强场区等其它非线性效应推广待检验；与温度、无序、相互作用修正耦合是否保持免波函数优势待答；千倍加速的实测标定待全文核实。
**代表作**：Wavefunction-Free Approach for Predicting Nonlinear Responses in Weyl Semimetals, arXiv:2505.09187 (2025)
*方法卡回补 2026-11-02*

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry 曲率]]
- [[Berry曲率]]
- [[Berry曲率偶极]]
- [[Weyl semimetal]]
- [[Weyl半金属]]
- [[强场超快]]
- [[非线性光学]]
- [[非线性光学响应]]
<!-- /linsai-wikilinks -->
