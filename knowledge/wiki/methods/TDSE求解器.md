---
title: "TDSE求解器"
type: "methods"
created: "2026-06-17T12:40:33Z"
updated: "2026-06-17T12:40:33Z"
tags: ["计算方法", "TDSE", "数值模拟", "#type/method", "#topic/HHG", "#status/mature", "#status/mature", "#status/mature", "#status/growing", "#status/growing", "#status/growing", "#status/growing"]
related: ["Lewenstein模型", "三步模型"]
aliases: ["TDSE-solver", "含时薛定谔求解", "time-dependent-schrodinger"]
growth_stage: "growing"
confidence: 0.8
---

# TDSE 求解器

## 林赛的理解

TDSE（含时薛定谔方程）数值求解是 HHG 理论的"ground truth"。Lewenstein 模型是近似，TDSE 是精确（在单活性电子近似下）。我验证任何新理论模型，都会先和 TDSE 结果对比。

## 核心要点

**方法**：
- 单活性电子（SAE）近似 + 模型势
- 分裂算符法（split-operator）或 Crank-Nicolson 时间传播
- 吸收边界（mask function 或 CAP）防边界反射

**输出**：偶极矩 x(t) 的傅里叶变换 → HHG 谱

**局限**：
- 单电子近似（不含多电子关联）
- 计算成本随维度急剧上升（原子 1D 容易，分子 3D 困难）

## 来源

- `hhg-methods-report.md`；arXiv: 0707.4192（改进模型对比 TDSE）
