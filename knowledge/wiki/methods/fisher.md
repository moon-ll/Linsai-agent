---
title: "量子Fisher信息（QFI）分析"
type: "methods"
created: "2026-10-09T20:02:26Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "#type/method"]
related: ["arXivID", "arpes", "强场电离"]
source_raw: ""
growth_stage: "growing"
confidence: 0.5
updated_at: "2026-10-10T03:21:56Z"
settled_count: 2
---

<!-- methods-settle:v1 -->

## 原理

以Fisher统计量化'可分辨性'：量子Fisher信息（QFI）给出参数估计的终极量子精度极限——既可为光学猫态相位估计给出极限并分解为经典/量子份额以追踪损耗下各自的衰减，也可为强场电离的Up估计提供首个量子精度极限、作为评估任何场强测量方案的信息论基准；其经典判别近亲则作标量诊断用：最大Fisher判别比（FDR）以层级可分性定位多任务网络中表征瓶颈发生的具体层级，Fisher线性判别分析（FLDA）把高维密度矩阵特征投影到单一判别方向并以标量阈值二分类，为纠缠探测提供线性代价的可扩展替代。

## 参数表

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 基准参数 | r=1.0（≈8.69 dB 压缩）、θ=φ=0、g=1.5；Wigner 全网格扫描 m=0–5 × n=0–4；保真度扫描 r∈[0,3]、g∈(1,10] | 研究方法·计算设置 
| (1,2) 大振幅猫态 | r=1.0、g=1.5：F₁=0.992（γ=0.803，α=2.0）；r=0.5 时 F_max=0.999（α=1.191）；F₁>0.99 的 α 范围 1.565–2.029 | 主要发现 
| 成功概率 | 单次试验 ~1.15%，对比传统 4 光子分束器相减 R⁴~10⁻⁴（R~0.02–0.05）——产率提升约两个数量级 | 主要发现 
| (4,1) 等效 5 光子相减 | 注入 4 探测 1 得 α≈2.24（≈√5）大振幅猫态，g=1.5 固定时全部 r 保真度 >0.99 | 主要发现 
| Fock 叠加配置 | (1,3)→偶宇称 |0⟩+|2⟩+|4⟩（与 a†²|Ψ₀⟩ 匹配 F≥0.998）；(1,4)→奇宇称 |1⟩+|3⟩+|5⟩（与三个光子操作态 F≥0.998） | 主要发现 
| 自旋极化类比量 | 损耗下 C 衰减远慢于 N（N 消失后 C 仍显著高于最小值 1），且 C 与 QFI 正相关 | 主要发现·量子计量 
| 计算参数 | 紧束缚近似 + 长度规范 + EDAC 散射；单光子能量 ħω = 40 eV；石墨烯内势 V₀ = 17 eV、非弹性平均自由程 5 Å、散射阶数 30、l_max = 15、角网格 1°、团簇 R = 20 Å（482 原子）、功函数 W = 6 eV；hBP 内势 10 eV、422 原子团簇（借用 Ga/As 4p 径向积分与相移） | 研究方法·ARPES 矩阵元 / 材料体系 
| 验证精度 | state-only（固定矩阵元只变态）：ARPES 估算的 CFI 对石墨烯与 hBP、度规迹 Tr[g] 与应变响应 ϵ 在除 Γ 点外所有 k 点精确等于最优 QFI——符合精度 10⁻⁷；full（矩阵元与态同变）出现表观上界违反（优化偏振只在中心 λ 值做，偏离后 D 不再对应固定轴测量）；可重构 QFI 区域主要在带隙小的区域（态变化占主导） | 主要发现与核心结论 
| 量子极限与基准 | ξ_QL = 4η/(1−η)；单通经典极限 ξ_SP = 4η；非平衡 N00N 连续最优 (ξ/ξ_QL)_opt = (1−1/η)/(e·lnη) ≈ 0.38；MP 连续最优 ≈ 0.648(1−η)/(η·ln²η) ≈ 0.65 | 主要发现与核心结论 
| 实验装置 | 偏振 MZ 干涉仪（H/V 双模）；BBO heralded 单光子；PPBS + 2×45° QWP + EHWP 样品；四镜循环光路（M2 位置定通过次数 N）；22.5° HWP + 方解石位移器实现 50:50 分析 | 研究方法 
<!-- src:2026-2605_23617-multiphoton-heralding-generates-large-amplitude-squeez -->
<!-- src:2026-2608_22511-estimating-the-fisher-information-from-arpes-in-genera -->
<!-- src:2026-2606_14254-dose-efficient-quantum-phase-estimation-in-lossy-optic -->

## 适用边界

QFI是信息论精度下界而非具体测量方案，实际方案须逼近该界方能获益；光学损耗等退相干下猫态QFI的量子份额（量子优势）会衰减，且计算QFI需对体系量子态/动力学有准确模型；FDR/FLDA属经典线性判别近似，隐含'单一判别方向可分'假设，只提供判别与层级定位而非量子精度界，不能替代QFI的极限分析。

## 代表作

- arXiv:2311.01371
- arXiv:2008.10070
- arXiv:2509.03233
- arXiv:2609.18525

## 证据日志

- 2026-10-09｜r61｜仅简报｜[paper:2023-2311.01371-metrological-robustness-of-high-photon-number-optical-cat-st] 量子Fisher信息（QFI）分析：量化猫态相位估计极限，并将QFI分解为经典/量子份额以追踪损耗下各自衰减行为
- 2026-10-09｜r61｜仅简报｜[paper:2020-2008.10070-quantum-estimation-in-strong-fields-in-situ-ponderomotive-se] 量子Fisher信息（QFI）：首次为强场电离给出 Up 估计的量子精度极限，作为评估任何场强测量方案的信息论基准。
- 2026-10-10｜r63｜仅简报｜[paper:2026-2609.18525-triprobe-probing-task-separability-beyond-classification-for] 最大 Fisher 判别比（FDR）：作为层级可分性的标量量化指标，用于定位多任务网络中表征瓶颈发生的具体层级。
- 2026-10-10｜r63｜仅简报｜[paper:2025-2509.03233-scalable-entanglement-detection-in-quantum-systems-via-fishe] Fisher线性判别分析（FLDA）：把高维密度矩阵特征投影到单一判别方向并以标量阈值二分类，为纠缠探测提供线性代价的可扩展替代方案。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[arXivID]]
- [[arpes]]
- [[强场电离]]
<!-- /linsai-wikilinks -->
