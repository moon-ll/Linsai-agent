---
title: "课题设想 — 最新版本"
type: "proposal_version"
proposal_id: "general-moire-strong-field-probe-20260726"
project_type: "general"
latest_round: 7
last_score: 0.62
status: "optimizing"
created: "2026-08-20T15:39:06Z"
updated: "2026-08-20T15:39:06Z"
project: ["NSFC-强场超快"]
growth_stage: "growing"
confidence: 1.0
---

# 课题设想 — 最新版本

**课题 ID**：`general-moire-strong-field-probe-20260726`
**类型**：general
**最新轮次**：第 7 轮
**当前分数**：0.62
**状态**：优化中
**同步时间**：2026-08-20T15:39:06Z

---

## 章节概览

| 章节 | 标题 | 行数 |
|------|------|------|
| content | content | 170 |
| full_review | full_review | 141 |
| rationale | rationale | 112 |
| references | references | 196 |
| scheme | scheme | 76 |

## 课题简介

# 课题设想

> 项目类型：面上项目
> 课题 ID：`general-moire-strong-field-probe-20260726`

## 核心问题

莫尔超晶格中的关联量子态（关联绝缘态、flat band 拓扑态）长期依赖电学输运与扫描隧道谱读出，前者受困于皮秒时间分辨，后者受针尖扰动制约——两者均无法在亚周期时间尺度上"看见"莫尔势、扭转角与关联态的瞬时图像。

本课题提出用强场超快激光驱动固体高次谐波产生（HHG）作为全光、非接触、亚周期的探针，建立"读出—改写"全光闭环：在不扰动莫尔体系的前提下定量反演莫尔势与扭转角，并在同一光场平台上通过光 Floquet 工程主动改写 flat band 与关联绝缘态。

## 科学意义

莫尔体系代表强关联与拓扑物理交叉的新兴平台，但其超快动力学长期缺乏合适的探针手段。将 HHG 从均匀体系扩展至莫尔自由度，意味着一旦闭环建立，任何莫尔材料（ TMDC 莫尔异质结、魔角石墨烯等）的能带结构、关联强度与量子态可以在亚周期时间窗口被非接触读出并主动调控，为关联物态的超快探测与操控开辟一条全新实验路径。

## 核心创新

**创新一：降阶有效模型**——建立"小原胞 TDDFT 标定参数 → 连续莫尔紧束缚 + 半导体布洛赫方程 → 张量网络关联修正"三段式降阶框架，将 >10⁴ 原子莫尔原胞的计算量从 >10⁸ 核时压缩至约 2×10⁴ 核时（降阶 4 个数量级），填补大原胞莫尔强场响应理论的空白。

**创新二：多观测联合反演**——针对单一 HHG 谱反演莫尔势的欠定病态性，建立"物理先验硬约束（C₃ 对称性 + 平移对称性）+ HHG 谱/椭偏依赖/瞬态吸收三类观测量联合 + Tikhonov 正则化"三层反演框架，在 SNR=50 噪声下将扭转角分辨率压缩至 ±0.05°、莫尔势 RMS 误差 < 15%。

（完整简介见 [源文件](research_proposals/optimizing/general-moire-strong-field-probe-20260726/04_proposal/proposal-draft-merged.md)）

## 来源

- 最新申请书：[research_proposals/optimizing/general-moire-strong-field-probe-20260726/04_proposal/proposal-draft-merged.md](research_proposals/optimizing/general-moire-strong-field-probe-20260726/04_proposal/proposal-draft-merged.md)
- 各章节文件：`research_proposals/optimizing/general-moire-strong-field-probe-20260726/04_proposal/sections/`
- 优化报告：[reports/general-moire-strong-field-probe-20260726.md](reports/general-moire-strong-field-probe-20260726.md)

> 本页由 `scripts/kb_proposal_reorg.py` 自动生成。