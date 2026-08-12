---
title: "NSFC 课题生命周期索引"
type: "index"
created: "2026-08-12T07:19:13Z"
updated: "2026-08-12T07:19:13Z"
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
| bsv-driven-hhg-quantum | 面上 | 优化中 | 第7轮 | 0.79 | [版本](versions/general-bsv-driven-hhg-quantum-20260726.md) | [报告](reports/general-bsv-driven-hhg-quantum-20260726.md) |
| moire-strong-field-probe | 面上 | 优化中 | 第5轮 | 0.76 | [版本](versions/general-moire-strong-field-probe-20260726.md) | [报告](reports/general-moire-strong-field-probe-20260726.md) |
| order-parameter-ultrafast-readout | 面上 | 优化中 | 第0轮 | 0.55 | [版本](versions/general-order-parameter-ultrafast-readout-20260727.md) | [报告](reports/general-order-parameter-ultrafast-readout-20260727.md) |
| quantum-geometry-inversion | 面上 | 优化中 | 第7轮 | 0.78 | [版本](versions/general-quantum-geometry-inversion-20260726.md) | [报告](reports/general-quantum-geometry-inversion-20260726.md) |
| transient-quantum-phase-optical | 重点 | 优化中 | 第0轮 | 0.71 | [版本](versions/key-transient-quantum-phase-optical-20260726.md) | [报告](reports/key-transient-quantum-phase-optical-20260726.md) |

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

> 由 `scripts/kb_proposal_reorg.py` 自动更新（2026-08-12）。