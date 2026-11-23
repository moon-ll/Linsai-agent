---
title: "RABBITT"
type: "methods"
created: "2026-06-17T12:40:33Z"
updated: "2026-11-20T21:35:33Z"
tags: ["表征方法", "阿秒", "干涉", "type/method", "topic/HHG", "status/mature"]
related: ["2024-2407_14160-angular-momentum-dependence-in-multiphoton-ionization-and-at", "2025-2502_08811-continuous-rainbow-rabbitt-investigation-of-resonant-states", "2025-2506_07445-circular-rabbitt-goes-under-threshold", "2026-2602_22137-spectral-phase-pulse-shaping-alters-photoionization-time", "2403.13650", "2407.09662", "2407.14160", "2502.08811", "2503.09459", "2505.04837", "2506.07445", "2602.22137", "2609.37838", "2610.31187", "Continuum-continuum 跃迁振幅的解析表达（含角动量依赖）—— Ji", "FROG", "Han & Wörner (2024)", "Lewenstein模型", "RABBIT", "TDSE", "Ueda", "rainbow-RABBITT", "三步模型", "光致电离时间延迟探测电子相关——Ar 3s Cooper 最小附近的阿秒干涉研究", "基于光电子干涉的阿秒光场纠缠认证", "孤立阿秒脉冲", "相位匹配", "阿秒脉冲串", "高次谐波产生"]
source_raw: ""
growth_stage: "mature"
confidence: 0.9
aliases: ["reconstruction-of-attosecond-beating", "重建阿秒拍频干涉"]
updated_at: "2026-11-20T21:35:33Z"
merged_from: ["wiki/concepts/RABBITT.md"]
source_reliability: "reliable"
sources: ["[\"{\"title\": \"briefing-research_briefing_2026-06-08.md\", "\"source_type\": \"briefing\"}\"]", "{"title": "briefing-research_briefing_2026-06-08.md", "source_type": "briefing"}"]
settled_count: 17
---

<!-- methods-settle:v1 -->

## 原理

RABBITT 用阿秒脉冲串的相邻奇次谐波叠加弱红外场，边带高度 S_SB(τ)=A+Bcos[2ωτ−C]（C=2ωτ_a）随 XUV-IR 延迟以两倍 IR 载频振荡、据此重建谐波拍频，边带振荡相位按标准框架解析分解为 EWS 本征延迟 + 连续-连续跃迁延迟 τ_cc + 原子相位项 τ_A（τ_a≈τ_W+τ_cc），该分解既是单通道延迟反演的标准框架也是多通道与角度/通道分辨光电离延迟提取的实验对应理论框架（边带振荡相位可提取角度与分波分辨时延；边带产额随 XUV-IR 延时的 2ω 振荡相位还可一并提取两光子跃迁矩阵元的复数相位与振幅，实现多通道单光子电离动力学的通道分辨完整表征），且已推广到多边带与高阶跃迁路径共存的情形（双谐波极简配置仅取一对相邻奇次谐波即可避开谐波串扰、干净分离高阶多光子路径并缓解分子低强度下的谱拥塞；氙 4d 亚层已据此分解出数十阿秒量级非零 Wigner 与 cc 分量且脉冲谱相位整形可主动偏移所测延迟，高谱分辨 RABBITT 可分辨 Cooper 极小附近快速相位结构，cc 相位修正虽可由解析表达式与可移植定标公式给出而不必逐案数值求解，但该普适 CC 公式建立于各向同性渐近近似之上，数十毫弧度（数阿秒）精度的双色光电离边带干涉相位测量已量化其系统偏差、表明渐近近似在此精度下失效，谐波谱光谱重叠时边带时延提取的不确定度亦已建立定量分析框架）；通用 τ_cc 概念已进一步推广为按光电子分波逐一施加的角动量依赖 IR 修正，可恢复弱关联分子发射积分与角度分辨边带时延的正确低能行为（与二阶阈上微扰理论及 R-matrix/RMT 从头算基准一致），大跃迁偶极矩体系尚需附加 τ_coupl、具显著永久偶极的分子尚需 τ_dLC 修正项；量子光场下振荡相位还出现经典理论没有的光子统计项；rainbow 变体（rRABBITT）把幅值与相位参数作为边带内电子能量的连续函数读出（实验上靠增强谱分辨并逐边带调谐激光载频实现），其连续化推广 crRABBITT 借助数值 TDSE 可达的两光子电离幅值，对原子/对称分子以宇称分离替代或辅以振幅相减，一次性同时分辨全部边带、无需调谐激光光子频率即可连续重建 He 与 H2 的阈下分立激发与阈上自电离共振全系列并检验共振区联系 RABBITT 相位与幅值的对数希尔伯特变换；圆偏振几何的推广有两个分支——更早的圆偏振阿秒计量将边带相位测量推广到圆偏振几何、分螺旋度通道提取相位并重构圆偏振阿秒脉冲的相位与含时偏振态，cuRABBITT 则以共旋/反旋双路径二向色性相位直接、模型无关地提取磁量子数分辨的双光子分波幅值比与相对相位，并结合宽带 rainbow 谱分析（宽带谐波使每个电子动能对应唯一谐波对组合）从能量分辨谱而非延迟扫描中解出幅值与相位、从而规避阈下边带缺失问题——阈下缺失的连续通道由分立 Rydberg 态激发流形替代，经 TDSE 与 Green 函数理论互证，在 He/Ar 揭示强共振、在 Xe 揭示类 Cooper 极小，把 Fano 倾向规则扩展到阈下区域并可检验其成立与失效；同属两路径相位灵敏测量的 ω/2ω 直通干涉变体以基频/倍频干涉替代高次谐波梳、适配 FEL 相位控制的角度分辨相位测量；此外相邻谐波两条上转换路径的干涉本身还可充当阿秒时间分辨的相关器，把模式间关联映射到边带强度/相位涨落，开辟阿秒相关干涉计量用途，且边带两光子跃迁幅度已被证明正比于场算符关联函数，据此可把延迟扫描的电子能谱转化为光学关联测量——阿秒 XUV 光场的量子纠缠信息被编码进光电子干涉条纹，从而以电子谱学实现对不可见 XUV 量子态的可测纠缠认证。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 典型光电离时间延迟量级 | 数十阿秒（tens of attoseconds，非零） | paper:2026-2602.22137-spectral-phase-pulse-shaping-alters-photoionization-time |
| 相干主驱动波长 | 800 nm | arXiv:2609.37838 |
| 主驱动峰值强度 | 1×10^14 W/cm² | arXiv:2609.37838 |
| TMBSV 信号模光子能量（≈0.58 ω_p） | 0.9 eV | arXiv:2609.37838 |
| TMBSV 闲置模光子能量（≈0.40 ω_p） | 0.62 eV | arXiv:2609.37838 |
| 泵浦有效和频 ω_s + ω_i = ω_p,eff | ≈1.52 eV | arXiv:2609.37838 |
| 偶次谐波干涉读出振荡频率 | 2ω_p | arXiv:2609.37838 |
| 分数谐波振幅关联带宽 | ≈20 eV（跨全部信号/闲置边带） | arXiv:2609.37838 |
| 涨落→场寂静转变时标 | 30 as | arXiv:2609.37838 |
| IR光子频率（驱动场） | ω = 6.09 eV（~200 nm波段） | paper:2025-2506.07445-circular-rabbitt-goes-under-threshold |
| 阈值附近Cooper型极小深度（Xe 4d, CR比值） | ~0.01 量级 | paper:2025-2506.07445-circular-rabbitt-goes-under-threshold |
| 边带调制相位测量精度（量化普适CC公式系统偏差所用） | 数十毫弧度（数阿秒） | paper:2026-2603.15293-breakdown-of-the-isotropic-asymptotic-approximation-in-two-c |

## 适用边界

经典解读依赖弱 IR 微扰、光电离截面随频率平滑变化与经典光场假设，且默认每个边带仅由相邻两谐波的两条路径构成——多边带或高阶跃迁路径共存时标准两路径分解不再直接适用、须按推广框架逐一处理（标准谐波串配置中多谐波串扰会污染高阶过程信号，双谐波极简配置可分离高阶多光子路径并缓解分子谱拥塞，代价是放弃完整脉冲串表征）；通用 τ_cc 及 τ_coupl、τ_dLC 等附加修正项仅在光电子与残余离子弱相互作用的高动能极限下定义良好，低能区须经分波分辨的角动量依赖 IR 修正方能恢复正确低能行为（该解析途径适用弱关联分子，用于高阶多光子或耦合模型的振幅计算时精度略降）；解析/普适 CC 修正公式建立于各向同性渐近近似，数十毫弧度（数阿秒）精度的双色光电离边带干涉相位测量已量化其系统偏差，达到该精度量级的延迟提取不能盲用普适 CC 公式、须计入超越各向同性渐近近似的修正；驱动光场具非经典光子统计时振荡相位出现经典分解式缺失的光子统计项、仅经典反演不再完备；截面剧变区（如 Cooper 极小附近）平滑假设失效、常规 RABBITT 受脉冲啁啾效应显著影响，需精细光子能量步进的高谱分辨测量方能分辨快速相位结构；相邻谐波/边带谱发生光谱重叠时会污染边带时延提取，须按定量不确定度分析框架评估误差后方可给出可靠延迟值；crRABBITT 的全边带一次性分辨目前仅限理论 TDSE 框架（振幅相减在实验上不可行，因双光子截面含 XUV/IR 干涉项，且相减要求足够短、谱足够宽的 XUV 脉冲），宇称分离要求原子或中心对称分子且初态具确定宇称，连续取谱还要求主谐波峰与边带峰足够宽而尚未重叠，实验 rRABBITT 仍须逐边带调节激光载频 ω 方能连续覆盖谱区；圆偏振各变体（圆偏振计量与 cuRABBITT）需圆偏振 XUV 谐波串与圆偏振 IR 并做螺旋度分辨探测，cuRABBITT 的阈下 rainbow 读出依赖宽带谐波使每个电子动能对应唯一谐波对组合且谱分析带宽足够（二向色性相位的解读以 TDSE/Green 函数理论基准为支撑），阈下机制中连续路径被分立 Rydberg 态替代、τ_a≈τ_W+τ_cc 的连续态解读不再直接适用，且圆偏振重构以脉冲偏振态已知/可控为前提；相关干涉用途读取的是边带强度/相位涨落而非平均振荡相位，标准延迟反演框架不直接适用、涨落信号解读依赖关联噪声源的表征与控制，而基于边带两光子跃迁幅度∝场算符关联函数的映射把延迟扫描能谱当作光学关联测量使用（如阿秒光场纠缠认证、将 XUV 量子态的纠缠信息编码进光电子干涉条纹）时，同样须在场算符关联而非经典平均场框架下解读、不能直接套用经典延迟反演；显著光谱相位整形仍会直接改变所测延迟与谱形，测量中须将本征电离动力学、光场相位整形贡献与光子统计贡献区分开。

## 代表作

- paper:2019-1907.13605-a-new-method-for-measuring-angle-resolved-phases-in-photoemi
- paper:2020-2005.12654-angle-resolved-time-delays-for-shake-up-ionization-of-helium
- paper:2020-2011.02989-decomposition-of-the-transition-phase-in-multi-sideband-sche
- paper:2021-2109.01581-attosecond-dynamics-of-multi-channel-single-photon-ionizatio
- paper:2022-2211.02769-attosecond-metrology-in-circular-polarization
- paper:2024-2403.13650-theory-of-attosecond-time-delays-in-multiphoton-multichannel
- paper:2024-2407.09662-analytical-expression-for-continuum-continuum-transition-amp
- paper:2024-2407.14160-angular-momentum-dependence-in-multiphoton-ionization-and-at

## 证据日志

- 2026-09-06｜r1｜回原文｜[paper:2026-2602.22137-spectral-phase-pulse-shaping-alters-photoionization-time] 阿秒光电离计时（streaking/RABBITT 类时间延迟测量）：以阿秒计时方案量化相位整形引入的延迟偏移，建立脉冲相位—电离时间的实验映射。
- 2026-09-06｜r2｜仅简报｜[paper:2025-2505.04837-photoionization-time-delays-probe-electron-correlations] 高谱分辨 RABBITT 阿秒干涉：以精细光子能量步进分辨 Cooper 最小附近快速变化的相位结构，直接重建 3s 通道时间延迟谱，是解决理论-实验分歧的实验关键。
- 2026-09-18｜r18｜仅简报｜[paper:2024-2403.13650-theory-of-attosecond-time-delays-in-multiphoton-multichannel] RABBITT 双光子干涉理论：给出侧带振荡相位到 EWS 延迟 + τ_cc + τ_A 的解析分解式，是实验延迟反演的标准框架。
- 2026-09-18｜r18｜仅简报｜[paper:2025-2503.09459-attosecond-photoionization-delays-of-xenon-4d-subshell] RABBITT相位复原：通过双光子边带振荡相位提取延迟，并分解出Wigner分量与连续-连续跃迁分量。
- 2026-09-18｜r19｜仅简报｜[paper:2026-doi-10-1103-qygr-6xcg-photon-statistics-time-delay-in-quantum-attosecond-photoelec] RABBIT（双光子边带干涉重建阿秒拍频）：作为承载光场量子统计信息的干涉骨架，边带振荡相位中出现经典理论没有的光子统计项。
- 2026-09-18｜r19｜仅简报｜[paper:2026-doi-10-1088-1361-6455-ae68cc-continuous-rainbow-rabbitt-investigation-of-resonant-states] Rainbow RABBITT（连续谱阿秒脉冲 + IR 侧带干涉）：以电子能量为连续变量读出两光子振幅比与相位差，免除谐波调谐式波长扫描，直接给出共振区完整复振幅谱
- 2026-09-27｜r43｜回原文｜[paper:2024-2403.13650-theory-of-attosecond-time-delays-in-multiphoton-multichannel] RABBITT双光子干涉理论：给出边带振荡相位与原子延迟的关系，是多通道延迟提取的实验对应框架
- 2026-10-02｜r47｜仅简报｜[paper:2024-2407.09662-analytical-expression-for-continuum-continuum-transition-amp] 双光子跃迁矩阵元 / cc相位提取（RABBITT框架）：将cc振幅应用于XUV+IR双光子干涉路径，分离出进入时延提取的原子相位项，给出可移植的定标公式。
- 2026-10-03｜r53｜回原文｜[paper:2025-2502.08811-continuous-rainbow-rabbitt-investigation-of-resonant-states] Rainbow RABBITT（连续能量边带干涉）：用宽带 XUV+IR 使边带相位随电子能量连续读出，实现优于谐波间距限制的高能量分辨共振扫描。
- 2026-10-03｜r53｜回原文｜[paper:2025-2506.07445-circular-rabbitt-goes-under-threshold] 圆偏振 RABBITT（cuRABBITT）：利用圆偏振谐波串+圆偏振 IR 的共旋/反旋双路径干涉，直接、模型无关地提取磁量子数分辨的双光子电离幅值与相对相位。
- 2026-10-11｜r70｜仅简报｜[paper:2025-2405.06275-quantitative-uncertainty-analysis-of-extracting-attosecond-d] RABBIT（双光子干涉重建阿秒拍频）：本文针对其光谱重叠情形建立了时延提取不确定度的定量分析框架。
- 2026-10-17｜r78｜仅简报｜[paper:2020-2011.02989-decomposition-of-the-transition-phase-in-multi-sideband-sche] RABBITT阿秒干涉计量：提供从边带拍频相位提取时延的标准框架，本文将其推广到多边带/高阶路径共存的情形。
- 2026-10-24｜r91｜回原文｜[paper:2024-2407.14160-angular-momentum-dependence-in-multiphoton-ionization-and-at] RABBITT 双光子干涉计量（阿秒脉冲串+红外弱场）：通过边带相位振荡提取角度/通道分辨的时间延迟，为分波延迟差的理论预测提供实验验证。
- 2026-10-24｜r91｜仅简报｜[paper:2019-1907.13605-a-new-method-for-measuring-angle-resolved-phases-in-photoemi] 类 RABBITT 侧带干涉的对比框架：与 RABBITT 型阿秒干涉同属两路径相位灵敏测量，但此处以 ω/2ω 直通干涉替代高次谐波梳，适配 FEL 相位控制。
- 2026-10-24｜r91｜仅简报｜[paper:2020-2005.12654-angle-resolved-time-delays-for-shake-up-ionization-of-helium] RABBITT（阿秒脉冲串 + 弱 IR）模拟：通过边带相位随 XUV-IR 延迟的振荡提取角分辨双光子时间延迟。
- 2026-10-31｜r105｜仅简报｜[paper:2026-2609.37838-attosecond-correlation-interferometry] 阿秒脉冲串双光子干涉（RABBITT 型边带干涉）：相邻谐波的两条上转换路径干涉充当阿秒时间分辨的相关器，把模式间关联映射到边带强度/相位涨落。
- 2026-10-31｜r105｜仅简报｜[paper:2022-2211.02769-attosecond-metrology-in-circular-polarization] 圆偏振阿秒干涉术（circular RABBITT）：将边带相位测量推广到圆偏振几何，分螺旋度通道提取相位，实现圆偏振阿秒脉冲的相位与含时偏振态重构。
- 2026-11-01｜r112｜回原文｜[paper:2025-2502.08811-continuous-rainbow-rabbitt-investigation-of-resonant-states] 连续 rainbow RABBITT（XUV 超连续 + 弱 IR 探测）：以连续能量取谱替代离散边带，实现对共振 Fano 剖型及其相位结构的逐点连续测绘。
- 2026-11-01｜r113｜回原文｜[paper:2025-2506.07445-circular-rabbitt-goes-under-threshold] 圆偏振 RABBITT（cuRABBITT）：利用螺旋度选择的双光子跃迁干涉直接提取电离幅值与分波相对相位，把 RABBITT 相位计量从阈上拓展到阈下谐波。
- 2026-11-01｜r113｜回原文｜[paper:2025-2506.07445-circular-rabbitt-goes-under-threshold] 彩虹宽带光谱分析（rainbow RABBITT）：宽带谐波使每个电子动能对应唯一谐波对组合，从能量分辨谱而非延迟扫描中解出幅值与相位，规避阈下边带缺失问题。
- 2026-11-08｜r127｜仅简报｜[paper:2026-2610.31187-entanglement-certification-of-attosecond-light-fields-with-p] 光电子干涉-关联函数映射（RABBITT 型边带）：证明边带两光子跃迁幅度正比于场算符关联函数，把延迟扫描的电子能谱转化为光学关联测量
- 2026-11-15｜r138｜仅简报｜[paper:2021-2109.01581-attosecond-dynamics-of-multi-channel-single-photon-ionizatio] RABBITT 双光子阿秒干涉：通过边带产额随 XUV-IR 延时的 2ω 振荡相位，提取两光子跃迁矩阵元的复数相位与振幅，实现通道分辨的完整表征。
- 2026-11-15｜r139｜仅简报｜[paper:2026-2603.15293-breakdown-of-the-isotropic-asymptotic-approximation-in-two-c] 双色光电离边带干涉（RABBITT类）相位测量：在数十毫弧度（数阿秒）精度上测量边带调制相位，量化普适CC公式的系统偏差。
- 2026-11-20｜r1｜仅简报｜[paper:2026-2610.31187-entanglement-certification-of-attosecond-light-fie] 光电子干涉谱学（RABBITT型边带干涉）：将阿秒XUV光场的量子纠缠信息编码进光电子干涉条纹，实现不可见XUV量子态的可测认证。

<!-- /methods-settle:v1 -->

# RABBITT

## 定义

RABBITT（Reconstruction of Attosecond Beating By Interference of Two-photon Transitions）是测量阿秒时间延迟的"金标准"方法。

## 原理

用一个孤立阿秒脉冲串（odd harmonics）加上弱红外（IR）驱动场，通过双光子跃迁的边带振荡，反推出电离时间延迟：

- XUV（odd harmonics）+ IR（fundamental）→ 产生 sideband（even harmonics）
- Sideband 振荡相位 ∝ 电离-连续态相位差 → 阿秒时间延迟 τ = Δφ/(2ω)
- 扫描 IR-XUV 延时，测 sideband 振荡

## 测量的是什么

电子从某能级电离后在连续态中积累的相位（Wigner-like delay）。

## 与其他方法对比

- **vs FROG**：RABBITT 需要阿秒脉冲串（频率梳），FROG-CRAB 用孤立阿秒脉冲。
- 简报标签中明确提到的相位匹配/高次谐波产生相关技术。

## 来源

- arXiv: 0707.4228（RABBITT vs FROG 对比）
- `hhg-methods-report.md`

## 关联概念

- [[FROG]]
- [[Lewenstein模型]]
- [[三步模型]]



---

Reconstruction of Attosecond Beating by Interference of Two-Photon Transitions，用于测量attosecond脉冲



---

来源明确列出该方法名称，但未在所给节选中说明其配置、数据重建方式或结果。

<!-- linsai-wikilinks -->
## 关联概念

- [[2024-2407_14160-angular-momentum-dependence-in-multiphoton-ionization-and-at]]
- [[2025-2502_08811-continuous-rainbow-rabbitt-investigation-of-resonant-states]]
- [[2025-2506_07445-circular-rabbitt-goes-under-threshold]]
- [[2026-2602_22137-spectral-phase-pulse-shaping-alters-photoionization-time]]
- [[2403.13650]]
- [[2407.09662]]
- [[2407.14160]]
- [[2502.08811]]
- [[2503.09459]]
- [[2505.04837]]
- [[2506.07445]]
- [[2602.22137]]
- [[2609.37838]]
- [[2610.31187]]
- [[Continuum-continuum 跃迁振幅的解析表达（含角动量依赖）—— Ji]]
- [[FROG]]
- [[Han & Wörner (2024)]]
- [[Lewenstein模型]]
- [[RABBIT]]
- [[TDSE]]
- [[Ueda]]
- [[rainbow-RABBITT]]
- [[三步模型]]
- [[光致电离时间延迟探测电子相关——Ar 3s Cooper 最小附近的阿秒干涉研究]]
- [[基于光电子干涉的阿秒光场纠缠认证]]
- [[孤立阿秒脉冲]]
- [[相位匹配]]
- [[阿秒脉冲串]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
