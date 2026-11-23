---
title: "隐含波动率曲面（IVS）构建"
type: "methods"
created: "2026-10-18T06:41:14Z"
updated: "2026-10-18T06:41:14Z"
tags: ["方法学", "#type/method"]
related: []
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-18T06:41:14Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

隐含波动率曲面（IVS）由市场期权报价反解得到，作为定价模型输入可显式携带当前市场风险中性分布信息；在联合校准框架中，IVS拟合项充当基准损失项，同时界定了仅以IVS拟合为目标的传统校准的拟合目标与局限。

## 适用边界

依赖市场期权报价的覆盖度与质量，期权数据稀疏或市场状态剧变时反解得到的IVS不稳定；且仅以IVS拟合为损失的传统校准存在局限（如难以同时约束方差期限结构），需将其作为联合目标的基准项处理。

## 代表作

- arXiv:2509.05911
- arXiv:2509.08096

## 证据日志

- 2026-10-18｜r83｜仅简报｜[paper:2025-2509.05911-deep-learning-option-pricing-with-market-implied-volatility] 隐含波动率曲面（IVS）构建：以市场期权报价反解的IVS作为模型输入，使定价模型显式携带当前市场风险中性分布信息。
- 2026-10-18｜r83｜仅简报｜[paper:2025-2509.08096-joint-calibration-of-the-volatility-surface-and-variance-ter] 隐含波动率曲面校准：作为联合目标函数的基准损失项，界定了传统校准的拟合目标与局限。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

_暂无关联概念_
<!-- /linsai-wikilinks -->
