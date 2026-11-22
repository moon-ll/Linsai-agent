---
title: "自洽 Hartree-Fock 平均场"
type: "methods"
created: "2026-11-14T07:20:38Z"
updated: "2026-11-14T07:20:38Z"
tags: ["方法学", "#type/method"]
related: []
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-11-14T07:20:38Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

自洽 Hartree-Fock 平均场通过将两体相互作用解耦为平均场并在选定基组（实空间格点或能带基）上自洽迭代求解相互作用哈密顿量，得到自旋/能谷/味等对称破缺的关联基态；全带推广表明须在含全部远程莫尔带的基组上自洽求解非局域交换，远程带经交换与屏蔽通道定量改变味破缺基态能序。

## 适用边界

单参考平均场仅描述静态对称破缺的 HF 基态，无法涵盖动态关联与强量子涨落；截断至低能带的投影基组会因缺失远程带的交换与屏蔽通道而对味破缺基态能序产生定量乃至定性偏差，全带方案则以更大基组的计算成本为代价。

## 代表作

- arXiv:2409.18898
- arXiv:2509.19764

## 证据日志

- 2026-11-14｜r132｜仅简报｜[paper:2024-2409.18898-correlated-states-in-super-moiré-materials-with-a-kernel-pol] 自洽 Hartree-Fock 平均场：在超大超莫尔格点上自洽迭代求解相互作用哈密顿量，获得自旋/能谷等对称破缺的关联基态。
- 2026-11-14｜r132｜仅简报｜[paper:2025-2509.19764-general-many-body-perturbation-framework-for-moiré-systems] 全带 Hartree-Fock：在含全部远程莫尔带的基组上自洽求解非局域交换，证明远程带通过交换与屏蔽通道定量改变味破缺基态能序。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

_暂无关联概念_
<!-- /linsai-wikilinks -->
