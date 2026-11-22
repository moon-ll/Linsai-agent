---
title: "Ab initio time-dependent GW approach for nonequilibrium exciton-phonon coupled dynamics across momentum space"
type: "papers"
created: "2026-11-22T04:58:02Z"
updated: "2026-11-22T05:24:53Z"
tags: ["TD-GW", "exciton-phonon-coupling", "trARPES", "WSe2", "valley-scattering", "first-principles"]
related: ["arpes", "moiré强场探测", "trARPES", "强场泵浦-探测", "激子动力学", "谷间散射"]
source_raw: "2026-2607.15411-ab-initio-time-dependent-gw-approach-for-nonequilibrium-exci.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Ab initio time-dependent GW approach for nonequilibrium exciton-phonon coupled dynamics across momentum space

## 林赛的理解
这篇工作正好卡在我最关心的交叉点上：首性原理方法直接给出动量分辨的激子-声子耦合动力学，并且与 trARPES 可观测量对接。我们组做 WSe2 及转角体系的强场泵浦-探测，长期受困于"实验测到动量空间信号变化，但没有理论能从头算激子谷间散射"。Diana Qiu 组的 TD-aGW-ph 方法如果可靠，等于给我们的 trARPES 数据补上了定量解释层。K→Q 谷 0.5 ps 的转移时间尺度也与我们在 TMD 中观察到的谷布居弛豫量级一致，值得作为基准案例精读。

## 核心要点
- 提出 TD-aGW-ph 方法：全布里渊区、首性原理的含时 GW 框架，处理非平衡激子-声子耦合动力学。
- 应用对象：WSe2 中 K 谷 → Q 谷的激子超快转移，时间尺度约 0.5 ps。
- 直接模拟并给出 trARPES（时间分辨 ARPES）信号响应，理论可与实验动量分辨观测对比。
- 覆盖整个布里渊区的电声耦合，而非仅高对称点近似。

## 实验/研究关联
- 已被 general-moire-strong-field-probe-20260726 提案引用，可支撑 moiré/强场探测项目中的理论建模部分。
- K→Q 谷散射是 TMD 谷动力学核心问题；若叠加强场/转角自由度，可探讨强场对谷间散射速率的调控。
- trARPES 仿真输出格式可直接对标我们谱仪的动量-能量窗口设计。

## 开放问题
- 强场（近带隙或带间强泵浦）下 GW 自能和激子图像是否仍收敛？方法对场强上限的适用范围？
- 计算成本：全 BZ 含时 GW 能否推广到转角 moiré 超胞？
- 声子是否为热声子近似？非平衡声子布居的反馈如何处理？
- 0.5 ps 转移时间与现有实验（ ours 及文献）的定量一致性如何？
- 摘要级信息，未提供数值细节，需获取全文后补充验证。

## 来源
- 原始材料：2026-2607.15411-ab-initio-time-dependent-gw-approach-for-nonequilibrium-exci.md
- 蒸馏时间：2026-11-22T04:58:02Z

<!-- linsai-wikilinks -->
## 关联概念

- [[arpes]]
- [[moiré强场探测]]
- [[trARPES]]
- [[强场泵浦-探测]]
- [[激子动力学]]
- [[谷间散射]]
<!-- /linsai-wikilinks -->
