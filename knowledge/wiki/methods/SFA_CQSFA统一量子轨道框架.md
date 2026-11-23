---
title: "SFA/CQSFA统一量子轨道框架"
type: "methods"
created: "2026-10-31T05:33:43Z"
updated: "2026-10-31T05:33:43Z"
tags: []
related: ["2610.16077", "2610.19967", "TDSE", "三步模型", "强场电离"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
source_reliability: "reliable"
sources: ""
- title: "briefing-2026-10-22.md"
source_type: "briefing"
---

# SFA / CQSFA 统一量子轨道框架

> 方法定位：强场电离/HHG 的半经典量子轨道基座——saddle-point 方程定轨道、Coulomb 修正定精度（2026-10-31 由空心补全，素材锚点 [[2610.16077]] 与 [[2610.19967]] 方法卡）。

## 原理

**SFA（强场近似）**：电离幅对 Volkov 态（激光场中自由电子）展开，忽略束缚态之外的再散射细节——HHG 三步模型与 ATI 量子轨道理论的出发点。

**Saddle-point 方程**：发射时刻 t_i 与初动量由 ∂S/∂t = 0、∂S/∂p = 0 的鞍点定——每个鞍点解对应一条量子轨道（短/长轨道族），相位 = 作用量 S 沿轨道积分。

**CQSFA（Coulomb-corrected SFA，Keldysh–SFA–Popruzhenko 2008 谱系）**：SFA 基础上保留末态 Coulomb 势修正（散射相位、轨迹偏折），恢复光电子动量谱低能结构；[[2610.16077]] 的 Q-CCSFA 进一步把经典场量替换为量子光场期望/取样——量子光版 CQSFA。

**固体对应**：气体 saddle-point + action phase 提取迁移到固体 SBE 半经典近似（课题 A 推导 Step 1.3）；系综平均引入 dephasing 与 SBE 显式退相干项构成对照方案（[[2610.19967]]）。

## 参数表

| 要素 | 内容 | 出处 |
| --- | --- | --- |
| 鞍点方程 | ∂S/∂t=0, ∂S/∂p=0 | [[2610.16077]] |
| CQSFA 谱系 | Keldysh–SFA–Popruzhenko (2008) | [[2610.16077]] |
| 量子化扩展 | Q-CCSFA：场量→量子期望/取样 | [[2610.16077]] |
| 固体迁移 | SBE 半经典 + saddle-point（课题 A Step 1.3） | [[2610.19967]] |
| dephasing 对照 | 系综平均 vs SBE 显式退相干项 | [[2610.19967]] |

## 适用边界

✅ 气相电离/HHG/ATI 的轨道分辨解释；量子光扩展（Q-CCSFA）作为光场读出基座。
❌ 束缚态动力学/再散射细节超出 SFA；多电子关联缺失（对照 TDSE/RPAE）；固体需 SBE 重表述（不能直接套气体公式）。

## 代表作

- Keldysh (1965)；Popruzhenko 谱系 (2008)；[[2610.16077]]（Q-CCSFA）；[[2610.19967]]（固体迁移对照）

## 证据日志

- 2026-10-31 由空心补全（素材：两张已回补方法卡的 SFA 段聚合）。

<!-- linsai-wikilinks -->
## 关联概念

- [[2610.16077]]
- [[2610.19967]]
- [[TDSE]]
- [[三步模型]]
- [[强场电离]]
<!-- /linsai-wikilinks -->
