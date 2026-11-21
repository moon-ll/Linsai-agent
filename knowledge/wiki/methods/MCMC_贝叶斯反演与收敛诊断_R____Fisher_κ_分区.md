---
title: "MCMC 贝叶斯反演与收敛诊断（R̂ + Fisher κ 分区）"
type: "methods"
source_reliability: "reliable"
sources:
  - title: "general-new-idea-20260822"
    source_type: archived_proposal
updated: "2026-11-14T06:29:59Z"
---

参数反演采用 MCMC，4 链 × 10⁴ 步，R̂ < 1.2 为收敛判据、R̂ > 1.5 触发审查；以 Fisher 信息 κ 分区（<10² / 10²–10⁴ / ≥10⁴）诊断参数可辨识性等级。