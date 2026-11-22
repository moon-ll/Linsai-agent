---
title: "Lifshitz–Kosevich 分析与有效质量提取"
type: "methods"
created: "2026-09-18T23:21:39Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "type/method"]
related: ["2025-2509_21303-topological-nontrivial-berry-phase-in-altermagnet-crsb", "2026-2601_19105-altermagnetic-spin-split-fermi-surfaces-in-crsb-revealed-by", "2509.21303", "2601.19105", "CrSb", "Dingle温度", "自旋劈裂"]
source_raw: ""
growth_stage: "mature"
confidence: 0.6
updated_at: "2026-09-27T02:13:42Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

Lifshitz–Kosevich 分析通过拟合量子振荡（SdH/dHvA）幅值随温度的衰减提取各支回旋有效质量（并辅以场强依赖给出 Dingle 温度等散射参量），结合 Onsager 关系 F=(ℏ/2πe)A 将频率定标为费米面极值截面积，从而为区分 altermagnetic 自旋劈裂费米面支并与能带计算对齐提供定量依据；其相位因子 γ 与朗道指数图截距 n0 还可相互校验、支撑贝利相位的判读。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| CrSb 频率–费米面截面积定标（Onsager 关系 F=(ℏ/2πe)A） | F = 300 T 对应垂直 c 轴布里渊区截面积的 1% | arXiv:2601.19105 |
| SdH 傅里叶分析磁场窗口（B∥c，CVT 样品） | 30–41.5 T | arXiv:2601.19105 |
| SdH 傅里叶分析磁场窗口（B∥a* 与 θ=−60°，助熔剂样品） | 15–41.5 T | arXiv:2601.19105 |
| dHvA 扭矩傅里叶分析磁场窗口（B∥a） | 5–17.5 T | arXiv:2601.19105 |
| 量子振荡测量最高磁场 | 41.5 T（电阻磁体+He-3）；17.5 T（超导磁体+稀释制冷） | arXiv:2601.19105 |
| 量子振荡样品 RRR（助熔剂法 / CVT 法） | 6.8 / 9.8（无量纲） | arXiv:2601.19105 |
| LK 波形拟合相位因子 γ（F1/F2/F3，δ=+1/8） | 0.2711 / 0.2297 / 0.2063（无量纲） | arXiv:2509.21303 |
| LK 拟合贝利相位 Φ（F1/F2/F3，δ=−1/8） | 0.9578π / 1.0406π / 1.0874π | arXiv:2509.21303 |
| 朗道指数图截距 n0（F1/F2/F3） | −0.2280 / −0.5193 / −0.1667（无量纲） | arXiv:2509.21303 |
| 磁输运测量最高磁场（水冷磁体） | 35 T | arXiv:2509.21303 |

## 适用边界

需要金属型、品质因数足够的样品（本例 RRR≈7–10）在极低温高场（5–41.5 T，He-3/稀释制冷）下获得分辨良好的多频振荡；贝利相位提取对相位偏移约定 δ=±1/8 及拟合方式（LK 波形拟合 vs 朗道指数图）敏感（如 F2 的 n0=−0.5193 与 F1/F3 明显不一致），多带叠加、谐波（2α、3α、2ε）及低频杂峰（带 * 峰需剔除）会增加拟合不确定性；半导体（如 MnTe）不适用量子振荡验证。

## 代表作

- arXiv:2601.19105
- arXiv:2509.21303

## 证据日志

- 2026-09-18｜r20｜回原文｜[paper:2026-2601.19105-altermagnetic-spin-split-fermi-surfaces-in-crsb-revealed-by] Lifshitz–Kosevich 分析与有效质量提取：由振荡幅值的温度依赖提取各支回旋有效质量，为区分劈裂费米面支并与能带计算对齐提供定量依据。
- 2026-09-18｜r20｜回原文｜[paper:2025-2509.21303-topological-nontrivial-berry-phase-in-altermagnet-crsb] Lifshitz-Kosevich型量子振荡分析：作为标准配套手段，可给出回旋有效质量与散射（Dingle温度），支撑贝利相位判读。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2025-2509_21303-topological-nontrivial-berry-phase-in-altermagnet-crsb]]
- [[2026-2601_19105-altermagnetic-spin-split-fermi-surfaces-in-crsb-revealed-by]]
- [[2509.21303]]
- [[2601.19105]]
- [[CrSb]]
- [[Dingle温度]]
- [[自旋劈裂]]
<!-- /linsai-wikilinks -->
