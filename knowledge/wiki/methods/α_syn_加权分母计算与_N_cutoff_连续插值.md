---
title: "α_syn 加权分母计算与 N_cutoff 连续插值"
type: "methods"
source_reliability: "reliable"
sources:
  - title: "general-mos2-20260905"
    source_type: archived_proposal
updated: "2026-11-07T08:24:15Z"
---

协同放大系数 α_syn = (N_cutoff_syn − max(N_cutoff_ex, N_cutoff_tw)) / max(N_cutoff_ex, N_cutoff_tw)；各 N_cutoff 由谐波谱包络截止拐点的连续插值给出，避免整数阶次下相对阈值的离散误差（文本在此处截断）。