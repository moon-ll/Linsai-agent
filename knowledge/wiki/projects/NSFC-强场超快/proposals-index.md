---
title: "NSFC 课题生命周期索引"
type: "index"
created: "2026-08-02T06:02:42Z"
updated: "2026-08-04T08:30:27Z"
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

| 课题 | 类型 | 当前轮次 | 分数 | 最新版本 | 优化报告 |
|------|------|---------|------|---------|---------|
| BSV-HHG 量子光场驱动 | 面上 | 第5轮 | 0.66 | [📄](versions/general-bsv-driven-hhg-quantum-20260726.md) | [📊](reports/general-bsv-driven-hhg-quantum-20260726.md) |
| 莫尔超晶格强场探针 | 面上 | 第5轮 | 0.72 | [📄](versions/general-moire-strong-field-probe-20260726.md) | [📊](reports/general-moire-strong-field-probe-20260726.md) |
| 序参量超快读出 | 面上 | 第5轮 | 0.71 | [📄](versions/general-order-parameter-ultrafast-readout-20260727.md) | [📊](reports/general-order-parameter-ultrafast-readout-20260727.md) |
| 量子几何反演 | 面上 | 第5轮 | 0.82 | [📄](versions/general-quantum-geometry-inversion-20260726.md) | [📊](reports/general-quantum-geometry-inversion-20260726.md) |
| 瞬态量子相全光读写 | 重点 | 第0轮 | 0.66 | [📄](versions/key-transient-quantum-phase-optical-20260726.md) | [📊](reports/key-transient-quantum-phase-optical-20260726.md) |

---

## 知识库结构

```
knowledge/wiki/projects/NSFC-强场超快/
├── MOC.md              ← 知识地图（入口）
├── proposals-index.md  ← 本页（生命周期索引）
├── proposals/          ← 元数据同步（由 proposal_kb_sync.py 维护）
├── versions/           ← 最新申请书快照（本结构新增）
├── reports/            ← 优化报告汇总（本结构新增）
├── decisions/          ← 决策记录
├── topics/             ← 课题方向笔记（T1-T5）
└── .gitkeep
```

> 数据流：`research_proposals/`（源）→ `proposal_kb_sync.py` → `proposals/`
> `research_proposals/`（源）→ `kb_proposal_reorg.py` → `versions/` + `reports/`

---

## 课题详情

### BSV-HHG 量子光场驱动

- **ID**：`general-bsv-driven-hhg-quantum-20260726`
- **类型**：面上项目
- **最新版本**：[versions/general-bsv-driven-hhg-quantum-20260726.md](versions/general-bsv-driven-hhg-quantum-20260726.md)
- **优化报告**：[reports/general-bsv-driven-hhg-quantum-20260726.md](reports/general-bsv-driven-hhg-quantum-20260726.md)
- **源文件**：`research_proposals/optimizing/general-bsv-driven-hhg-quantum-20260726/`

### 莫尔超晶格强场探针

- **ID**：`general-moire-strong-field-probe-20260726`
- **类型**：面上项目
- **最新版本**：[versions/general-moire-strong-field-probe-20260726.md](versions/general-moire-strong-field-probe-20260726.md)
- **优化报告**：[reports/general-moire-strong-field-probe-20260726.md](reports/general-moire-strong-field-probe-20260726.md)
- **源文件**：`research_proposals/optimizing/general-moire-strong-field-probe-20260726/`

### 序参量超快读出

- **ID**：`general-order-parameter-ultrafast-readout-20260727`
- **类型**：面上项目
- **最新版本**：[versions/general-order-parameter-ultrafast-readout-20260727.md](versions/general-order-parameter-ultrafast-readout-20260727.md)
- **优化报告**：[reports/general-order-parameter-ultrafast-readout-20260727.md](reports/general-order-parameter-ultrafast-readout-20260727.md)
- **源文件**：`research_proposals/optimizing/general-order-parameter-ultrafast-readout-20260727/`

### 量子几何反演

- **ID**：`general-quantum-geometry-inversion-20260726`
- **类型**：面上项目
- **最新版本**：[versions/general-quantum-geometry-inversion-20260726.md](versions/general-quantum-geometry-inversion-20260726.md)
- **优化报告**：[reports/general-quantum-geometry-inversion-20260726.md](reports/general-quantum-geometry-inversion-20260726.md)
- **源文件**：`research_proposals/optimizing/general-quantum-geometry-inversion-20260726/`

### 瞬态量子相全光读写

- **ID**：`key-transient-quantum-phase-optical-20260726`
- **类型**：重点项目
- **最新版本**：[versions/key-transient-quantum-phase-optical-20260726.md](versions/key-transient-quantum-phase-optical-20260726.md)
- **优化报告**：[reports/key-transient-quantum-phase-optical-20260726.md](reports/key-transient-quantum-phase-optical-20260726.md)
- **源文件**：`research_proposals/optimizing/key-transient-quantum-phase-optical-20260726/`


> 由 `scripts/kb_proposal_reorg.py` 自动更新。