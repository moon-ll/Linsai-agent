---
title: "2023-2303.10129-covariant-derivatives-of-berry-type-quantities-application-t"
type: "papers"
created: "2026-11-01T10:04:41Z"
updated: "2026-11-15T15:09:25Z"
tags: []
related: ["Berry 曲率", "MnPS3", "anomalous-hall-effect", "berry-curvature", "berry-dipole", "gauge-covariance", "general-berry-mnps3-rashba-20260816", "method-manual", "non-abelian", "nonlinear-transport", "orbital-magnetic-moment", "wannier-interpolation", "wannier90", "wannierberri"]
source_raw: "2023-2303.10129-covariant-derivatives-of-berry-type-quantities-application-t.md"
growth_stage: "seedling"
confidence: 0.5
digest_level: "abstract"
---

• 全文缓存不存在，确认按摘要级（abstract）蒸馏。以下为产出内容：

  # Covariant derivatives of Berry-type quantities: Application to nonlinear transport（arXiv: 2303.10129）

  ## 研究问题（Research Question）
  [[berry-curvature]] 与 [[orbital-magnetic-moment]] 等 Berry 型几何量的导数（协变导数）应如何在 [[wannier-interpolation]]（Wannier 插值）框架内以规范协变的方式计算？这一问题直接制约非线性反常 [[anomalous-hall-effect]]（Hall）输运系数的可靠计算。

  ## 背景（Background）
  反常 Hall 电导的线性响应可由 Berry 曲率积分给出，而二阶等非线性输运响应依赖 Berry 曲率与轨道磁矩的动量导数。直接数值微分插值数据易破坏 [[gauge-covariance]]（规范协变性），导致收敛性差。本文属于 [[wannier90]] / [[wannierberri]] 非线性输运方法学谱系（代表作参见 wannier90 开发者相关工作）。

  ## 研究方法（Data & Method）
  发展一套 Wannier 插值方案，计算能带组的协变导数形式的 [[berry-curvature]] 与 [[orbital-magnetic-moment]] 的 [[non-abelian]]（非 Abelian）矩阵表达，保证导数计算全程保持规范协变。应用端以非线性反常 Hall 电导计算验证收敛性。

  ## 主要发现与核心结论（Main Results & Findings）
  - 给出了 Berry 型几何量协变导数的非 Abelian 矩阵插值公式，导数量继承规范协变性；
  - 该方案显著提高了 [[nonlinear-transport]] 中非线性反常 Hall 电导计算的收敛性（原始摘要级笔记未给出具体数值倍率，此处不作编造）。

  ## 潜在研究方向（Limitations & Open Questions）
  - 协变导数插值与更高阶非线性响应（如 [[berry-dipole]]、电导三阶项）的衔接，是后续可拓展方向；
  - 与课题 [[general-berry-mnps3-rashba-20260816]]（Berry-MnPS3-Rashba 方向）相关：可作为含自旋-轨道耦合体系中贝里曲率定量计算的方法素材，供 [[method-manual]] 方法卡归档参考。

  ---
  说明：raw 笔记为摘要级单条记录（无全文、无 PDF、无 abstract 字段正文），以上蒸馏未虚构任何数值与作者结论；元数据作者字段 "Spivak, Garrity, WannierBerri developers" 按纪律原样保留、未采信改写。digest_level=abstract，建议后续经 deep_read_pipeline 补全文后升级为 fulltext 精读。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：Berry 型几何量协变导数的 Wannier 插值方案（非 Abelian 矩阵公式，非线性反常霍尔输运）

**原理**：发展 Wannier 插值方案计算 Berry 曲率与轨道磁矩协变导数的非 Abelian 矩阵表达，保证导数计算全程规范协变——避免直接数值微分破坏规范协变性导致的收敛性劣化；以非线性反常霍尔电导计算验证收敛性提升。

**适用边界**：摘要级：收敛性提升未给数值倍率不作编造；与更高阶非线性响应（Berry 电偶极、电导三阶项）衔接为拓展方向；待 deep_read 补全文后升级精读。
**代表作**：Covariant derivatives of Berry-type quantities: Application to nonlinear transport, arXiv:2303.10129 (2023)
*方法卡回补 2026-11-01*

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry 曲率]]
- [[MnPS3]]
- [[anomalous-hall-effect]]
- [[berry-curvature]]
- [[berry-dipole]]
- [[gauge-covariance]]
- [[general-berry-mnps3-rashba-20260816]]
- [[method-manual]]
- [[non-abelian]]
- [[nonlinear-transport]]
- [[orbital-magnetic-moment]]
- [[wannier-interpolation]]
- [[wannier90]]
- [[wannierberri]]
<!-- /linsai-wikilinks -->
