---
title: "Implementation of a laser-neutron pump-probe capability at HYSPEC"
type: "papers"
created: "2026-11-21T11:10:38Z"
updated: "2026-11-21T11:18:41Z"
tags: ["泵浦-探测", "非弹性中子散射", "非平衡态磁学", "激光-中子联用"]
related: ["HYSPEC", "pump-probe", "强场超快", "强场超快光学", "时间分辨谱学", "泵浦探测", "非平衡磁振子"]
source_raw: "2023-2310.10540-implementation-of-a-laser-neutron-pump-probe-capability-at-h.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Implementation of a laser-neutron pump-probe capability at HYSPEC

## 林赛的理解
这篇工作在 ORNL 散裂中子源 HYSPEC 谱仪上实现了激光-中子泵浦探测能力：用纳秒脉冲激光激发非平衡磁振子，再用非弹性中子散射探测。作为做强场超快光学的人，我对泵浦-探测框架本身非常熟悉，但这里的“探针”换成了中子——这是光学手段做不到的：中子能直接测量磁振子的动量分辨色散与占据，不依赖光学选择定则。这说明超快/非平衡测量的探针正在从光学向 X 射线、中子扩展，对我在 1T-TaS2 类 CDW 体系上做时间分辨测量是一个重要的互补视角。

## 核心要点
- 在 HYSPEC（ORNL 散裂中子源）建成激光-中子泵浦探测能力。
- 泵浦：纳秒脉冲激光，激发体系进入非平衡态（非平衡磁振子）。
- 探测：非弹性中子散射，具备动量分辨能力。
- 意义：为非平衡态中子研究开辟新方向，将泵浦-探测范式引入中子散射领域。

## 实验/研究关联
- 与我组的 general-t-tise2-2-2-2-cdw-20261108 提案相关：CDW 体系非平衡动力学可用中子泵浦-探测作为磁/结构序的互补探针，补充光学超快测量的动量信息缺失。
- 时间尺度需注意：纳秒激光泵浦 + 中子探测，远慢于飞秒光学泵浦-探测；适用于慢恢复动力学或长寿命非平衡态，不能直接覆盖超快 CDW 堆叠转变（ps 级）。

## 开放问题
- 时间分辨率与重复频率如何匹配中子脉冲结构？激发-探测占空比损失多大？
- 非平衡磁振子探测的信噪比与数据获取时间？
- 能否推广到飞秒激光泵浦 + 中子探测（需超高重复频率激光）？
- 对 CDW/电子向列序等非磁非平衡态，中子泵浦-探测的适用边界在哪里？

## 来源
- 原始材料：2023-2310.10540-implementation-of-a-laser-neutron-pump-probe-capability-at-h.md
- 蒸馏时间：2026-11-21T11:10:38Z

<!-- linsai-wikilinks -->
## 关联概念

- [[HYSPEC]]
- [[pump-probe]]
- [[强场超快]]
- [[强场超快光学]]
- [[时间分辨谱学]]
- [[泵浦探测]]
- [[非平衡磁振子]]
<!-- /linsai-wikilinks -->
