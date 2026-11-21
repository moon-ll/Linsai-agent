---
title: "高通量 DFT 计算流程"
type: "methods"
created: "2026-09-18T23:22:12Z"
updated: "2026-11-01T04:55:12Z"
tags: ["方法学", "type/method"]
related: ["2411.10790", "2507.14890", "2603.25317", "arXivID", "强关联体系", "电荷密度波", "自旋劈裂"]
source_raw: ""
growth_stage: "mature"
confidence: 0.5
updated_at: "2026-09-27T02:13:42Z"
settled_count: 2
---

<!-- methods-settle:v1 -->

## 原理

高通量 DFT 流程以统一标准化设置对大批量体系批量计算，通过 PBE 与 PBE+U 等泛函方案的批量比较给出泛函级方法学误差的统计分布，对含过渡金属 3d 的强关联体系可在特定轨道（如 Ni 3d）引入在位 Hubbard U 复现实验能隙与杂化带并分离磁序与关联各自对能带重构的贡献；第一性原理电子结构计算（可结合声子计算）还可从能带对称性量化交替自旋劈裂与磁各向异性能（MAE）以确认亚铁-交替磁性电子结构，并确认费米面附近平带的存在、从能带层面阐明电荷/自旋两种不稳定性的微观根源。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 统一流程批量计算体系数 | 638 个体系 | paper:2024-2411.10790-effect-of-hubbard-u-corrections-on-the-electronic-and-magnet |
| 交替自旋劈裂（DFT 电子结构计算值） | 344 meV | paper:2026-2607.11222-anomalous-transverse-response-and-multi-field-ferrialtermagn |

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 可验证）：
| 候选电荷密度波波矢 q* | (1/2, 0)（倒空间分数坐标） | [[2603.25317]] |
| 磁序引起的声子能量重整化 | 约 6 meV | [[2603.25317]] |
| 同步辐射实验覆盖的最低温度 | 80 K | [[2603.25317]] |

## 适用边界

统计结论反映泛函级方法学误差的分布而非个别体系的精确结论，强关联 3d 体系仅 PBE 不足以复现能隙与杂化带、需引入在位 U 修正，且统一流程的固定设置与大批量计算带来成本和单体系适配性局限；自旋劈裂/MAE 与平带不稳定性的判定属单体系能带分析，其可靠性依赖所选泛函精度与体系特定设置，不具高通量统计意义。

## 代表作

- arXiv:2411.10790
- arXiv:2507.14890
- arXiv:2607.11222
- arXiv:2603.25317

## 证据日志

- 2026-09-18｜r20｜仅简报｜[paper:2024-2411.10790-effect-of-hubbard-u-corrections-on-the-electronic-and-magnet] 高通量 DFT 计算流程：对 638 个体系统一流程批量比较 PBE 与 PBE+U，给出泛函级方法学误差的统计分布而非个例结论。
- 2026-09-18｜r20｜仅简报｜[paper:2025-2507.14890-probing-the-band-structure-of-the-strongly-correlated-antife] DFT+U 计算：在 Ni 3d 上引入在位库仑 U 处理强关联，复现实验能隙与 Ni 3d/S 3p 杂化带，并可分离磁序与关联各自对能带重构的贡献。
- 2026-09-19｜r27｜仅简报｜[paper:2026-2607.11222-anomalous-transverse-response-and-multi-field-ferrialtermagn] DFT 第一性原理电子结构计算：给出 344 meV 交替自旋劈裂与 MAE，从能带对称性上确认亚铁-交替磁性电子结构。
- 2026-09-19｜r27｜仅简报｜[paper:2026-2603.25317-flat-band-driven-competing-charge-and-spin-instabilities-in] DFT电子结构与声子计算：确认费米面附近平带的存在，并从能带层面给出电荷/自旋两种不稳定性的微观根源。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2411.10790]]
- [[2507.14890]]
- [[2603.25317]]
- [[arXivID]]
- [[强关联体系]]
- [[电荷密度波]]
- [[自旋劈裂]]
<!-- /linsai-wikilinks -->
