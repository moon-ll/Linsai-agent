---
title: "NSFC 课题生命周期索引"
type: "index"
created: "2026-08-18T04:01:47Z"
updated: "2026-08-18T04:01:47Z"
tags: []
related: []
source_raw: ""
growth_stage: "growing"
confidence: 1.0
project: ["NSFC-强场超快"]
---

# NSFC 课题生命周期索引

本页聚合 `research_proposals/` 中各课题的最新状态、版本和优化报告。

## 课题总览

| 课题 | 类型 | 状态 | 当前轮次 | 分数 | 最新版本 | 优化报告 |
|------|------|------|---------|------|---------|---------|
| berry-mnps3-rashba | 面上 | 优化中 | 第0轮 | 0.1 | [版本](versions/general-berry-mnps3-rashba-20260816.md) | [报告](reports/general-berry-mnps3-rashba-20260816.md) |
| bsv-driven-hhg-quantum | 面上 | 优化中 | 第0轮 | 0.75 | [版本](versions/general-bsv-driven-hhg-quantum-20260726.md) | [报告](reports/general-bsv-driven-hhg-quantum-20260726.md) |
| moire-strong-field-probe | 面上 | 待校验 | 第8轮 | 0.78 | [版本](versions/general-moire-strong-field-probe-20260726.md) | [报告](reports/general-moire-strong-field-probe-20260726.md) |
| order-parameter-ultrafast-readout | 面上 | 优化中 | 第1轮 | 0.74 | [版本](versions/general-order-parameter-ultrafast-readout-20260727.md) | [报告](reports/general-order-parameter-ultrafast-readout-20260727.md) |
| quantum-geometry-inversion | 面上 | 待校验 | 第1轮 | 0.7 | [版本](versions/general-quantum-geometry-inversion-20260726.md) | [报告](reports/general-quantum-geometry-inversion-20260726.md) |
| transient-quantum-phase-optical | 重点 | 待校验 | 第4轮 | 0.53 | [版本](versions/key-transient-quantum-phase-optical-20260726.md) | [报告](reports/key-transient-quantum-phase-optical-20260726.md) |

---

## 知识库结构

```
knowledge/wiki/projects/NSFC-强场超快/
├── MOC.md              ← 知识地图（入口）
├── proposals-index.md  ← 本页（生命周期索引）
├── proposals/          ← 元数据同步（由 proposal_kb_sync.py 维护）
├── versions/           ← 最新申请书快照（由 kb_proposal_reorg.py 维护）
├── reports/            ← 优化报告汇总 + 评分变化表（由 kb_proposal_reorg.py 维护）
├── decisions/          ← 决策记录
├── topics/             ← 课题方向笔记（T1-T5）
└── .gitkeep
```

> 数据流：`research_proposals/`（源）→ `proposal_kb_sync.py` → `proposals/`
> `research_proposals/`（源）→ `kb_proposal_reorg.py` → `versions/` + `reports/`

> 由 `scripts/kb_proposal_reorg.py` 自动更新（2026-08-18）。