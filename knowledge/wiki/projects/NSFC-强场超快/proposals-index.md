---
title: "NSFC 课题生命周期索引"
type: "index"
created: "2026-11-16T05:07:03Z"
updated: "2026-11-16T05:30:14Z"
tags: []
related: ["MnPS3", "TDDFT", "TDSE", "general-chiral-hhg-20261101", "general-floquet-20261107", "general-phonon-hhg-20261101", "固体高次谐波", "强场超快", "相干声子"]
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
| attosecond-streaking | 面上 | 优化中 | 第3轮 | 0.76 | [版本](versions/general-attosecond-streaking-20260822.md) | [报告](reports/general-attosecond-streaking-20260822.md) |
| berry-berry | 面上 | 优化中 | 第2轮 | 0.82 | [版本](versions/general-berry-berry-20261107.md) | [报告](reports/general-berry-berry-20261107.md) |
| berry-mnps3-rashba | 面上 | 优化中 | 第0轮 | 0.79 | [版本](versions/general-berry-mnps3-rashba-20260816.md) | [报告](reports/general-berry-mnps3-rashba-20260816.md) |
| bsv-driven-hhg-quantum | 面上 | 待校验 | 第3轮 | 0.79 | [版本](versions/general-bsv-driven-hhg-quantum-20260726.md) | [报告](reports/general-bsv-driven-hhg-quantum-20260726.md) |
| chiral-hhg | 面上 | 优化中 | 第2轮 | 0.83 | [版本](versions/general-chiral-hhg-20261101.md) | [报告](reports/general-chiral-hhg-20261101.md) |
| floquet | 面上 | 优化中 | 第2轮 | 0.8300000000000001 | [版本](versions/general-floquet-20261107.md) | [报告](reports/general-floquet-20261107.md) |
| houston-kronig-penney-landau-zener | 面上 | 优化中 | 第3轮 | 0.85 | [版本](versions/general-houston-kronig-penney-landau-zener-20261004.md) | [报告](reports/general-houston-kronig-penney-landau-zener-20261004.md) |
| keldysh-schottky | 面上 | 优化中 | 第0轮 | 0.0 | [版本](versions/general-keldysh-schottky-20261115.md) | [报告](reports/general-keldysh-schottky-20261115.md) |
| moire-strong-field-probe | 面上 | 优化中 | 第3轮 | 0.81 | [版本](versions/general-moire-strong-field-probe-20260726.md) | [报告](reports/general-moire-strong-field-probe-20260726.md) |
| 课题设想/研究概要：固体高次谐波中的交错磁序参量探测与唯一归因 | 面上 | 优化中 | 第2轮 | 0.81 | [版本](versions/general-order-parameter-ultrafast-readout-20260727.md) | [报告](reports/general-order-parameter-ultrafast-readout-20260727.md) |
| 相干声子调控的固体高次谐波：晶格自由度进入强场非线性与电子-声子耦合的全光反演 | 面上 | 优化中 | 第2轮 | 0.875 | [版本](versions/general-phonon-hhg-20261101.md) | [报告](reports/general-phonon-hhg-20261101.md) |
| ssh-weyl | 面上 | 优化中 | 第4轮 | 0.8400000000000001 | [版本](versions/general-ssh-weyl-20260920.md) | [报告](reports/general-ssh-weyl-20260920.md) |
| t-tise2-2-2-2-cdw | 面上 | 优化中 | 第4轮 | 0.89 | [版本](versions/general-t-tise2-2-2-2-cdw-20261108.md) | [报告](reports/general-t-tise2-2-2-2-cdw-20261108.md) |
| tdse-tddft | 面上 | 优化中 | 第0轮 | 0.0 | [版本](versions/general-tdse-tddft-20261115.md) | [报告](reports/general-tdse-tddft-20261115.md) |
| tmd-bic-mie-anapole | 面上 | 优化中 | 第2轮 | 0.79 | [版本](versions/general-tmd-bic-mie-anapole-20261107.md) | [报告](reports/general-tmd-bic-mie-anapole-20261107.md) |
| transient-quantum-phase-optical | 重点 | 优化中 | 第3轮 | 0.8200000000000001 | [版本](versions/key-transient-quantum-phase-optical-20260726.md) | [报告](reports/key-transient-quantum-phase-optical-20260726.md) |

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

> 由 `scripts/kb_proposal_reorg.py` 自动更新（2026-11-16）。

<!-- linsai-wikilinks -->
## 关联概念

- [[MnPS3]]
- [[TDDFT]]
- [[TDSE]]
- [[general-chiral-hhg-20261101]]
- [[general-floquet-20261107]]
- [[general-phonon-hhg-20261101]]
- [[固体高次谐波]]
- [[强场超快]]
- [[相干声子]]
<!-- /linsai-wikilinks -->
