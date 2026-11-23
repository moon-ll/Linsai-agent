---
title: "自动微分求 PDE 残差"
type: "methods"
created: "2026-10-03T03:02:44Z"
updated: "2026-11-14T11:34:42Z"
tags: ["方法学", "#type/method"]
related: ["TDSE", "TDSE求解器", "固体HHG", "固体HHG数值计算方法体系", "正演模型数值校验判据_R1_双基准", "相位匹配"]
source_raw: ""
growth_stage: "growing"
confidence: 0.5
updated_at: "2026-10-31T20:02:13Z"
settled_count: 2
---

<!-- methods-settle:v1 -->

## 原理

利用自动微分对网络输出（解或动量函数的连续可微表示）解析地精确求任意阶时空偏导（如 u_t、u_x、u_xx、ψ''），在无网格的连续域上构造 PDE 残差，取代有限差分且残差不含离散化误差；还可对任意坐标（含动量/波矢 k 等参数）求导，便于处理以 k 为参数的能带类方程及积分-微分混合算子，并避免有限差分的噪声放大。

## 参数表

**终极升级**（2026-11-01，canonical 要素，引用已核实/库内锚）：
偏微分方程数值求解（HHG 语境：Maxwell 传播方程、TDSE 空间离散）——有限差分/谱方法两大族，分裂步长 Fourier 是强场传播的标准实现。

| 方法 | 有限差分（结构网格）/ 谱方法（周期域，指数收敛） | [[固体HHG数值计算方法体系]] |
| 分裂步长 | 线性算符（衍射/色散）谱域精确解 + 非线性算符局部精确 | [[相位匹配]] |
| 收敛 | 网格与时间步双重收敛检查（库内双基准纪律） | [[正演模型数值校验判据_R1_双基准]] |

✅ 宏观传播、波包演化、电流谱合成。
❌ 刚性/多尺度问题需隐式或自适应方法；谱方法对不连续解有 Gibbs 振荡。

- 库内工程化：[[TDSE求解器]]（数值引擎细节）、[[相位匹配]]（宏观传播四项分解）

## 适用边界

仅当目标函数以可微的神经网络解析表示时才能精确求导，导数准确性受网络对真解的光滑逼近程度限制；对非网络形式的散乱离散数据本身仍需差分等数值手段。

## 代表作

- arXiv:1711.10566
- arXiv:2411.02177
- arXiv:2504.05367
- arXiv:2408.16806

## 证据日志

- 2026-10-03｜r49｜仅简报｜[paper:2017-1711.10566-physics-informed-deep-learning-part-ii-data-driven-discovery] 自动微分求 PDE 残差：对网络输出直接求高阶时空偏导，使稀疏散乱数据下的导数计算不再受有限差分噪声放大之害。
- 2026-10-03｜r49｜仅简报｜[paper:2025-2411.02177-physics-informed-neural-networks-viewpoint-for-solving-the-d] 自动微分：对网络表示的动量函数精确求导以构造方程中的导数项，避免数值差分误差，便于处理积分-微分混合算子。
- 2026-10-03｜r49｜仅简报｜[paper:2025-2504.05367-physics-informed-neural-networks-for-one-dimensional-quantum] 自动微分：直接对网络输出求二阶导获得动能项 ψ''，免去网格差分离散，适用于无网格的连续域求解。
- 2026-10-31｜r108｜仅简报｜[paper:2024-2408.16806-physics-informed-neural-networks-and-extensions] 自动微分构建 PDE 残差损失：无需离散化即可对任意坐标（含动量/波矢参数）求导，便于处理以 k 为参数的能带类方程。
- 2026-10-31｜r108｜仅简报｜[paper:2017-1711.10566-physics-informed-deep-learning-part-ii-data-driven-discovery] 自动微分构造PDE残差：对网络输出精确求 u_t、u_x、u_xx 等偏导，取代有限差分，残差无离散化误差。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[TDSE]]
- [[TDSE求解器]]
- [[固体HHG]]
- [[固体HHG数值计算方法体系]]
- [[正演模型数值校验判据_R1_双基准]]
- [[相位匹配]]
<!-- /linsai-wikilinks -->
