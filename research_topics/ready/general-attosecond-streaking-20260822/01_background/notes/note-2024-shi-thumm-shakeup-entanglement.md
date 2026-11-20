# Photoelectron–Residual-Ion Interaction in Angle-Resolved Streaked Shake-Up Ionization of Helium（氦原子角分辨条纹 shake-up 电离中的光电子–剩余离子相互作用）

- 课题 ID: general-attosecond-streaking-20260822
- 五维笔记（literature-reading skill 标准）
- 出处：Physical Review A, 2025, 111(1): 013119. DOI: 10.1103/PhysRevA.111.013119；arXiv:2409.03622
- 与本课题的关系：从头计算量化多通道电离与剩余离子纠缠对阿秒条纹延迟的贡献，是本课题多通道修正与角分辨修正的数值参照（[ref:8]）。

## 研究问题（Research Question）

在氦的 XUV-IR 条纹 shake-up 电离中，光电子与剩余 He⁺ 离子的纠缠如何影响可观测的条纹延迟？把绝对条纹延迟分解为 t_EWS + t_CLC + t_DLC 后，剩余离子偶极-激光耦合（DLC）项是否主导 shake-up 延迟，其随探测方向/动能/XUV 光子能量如何依赖？

## 研究背景（Background）

Ossiander et al.（Nat. Phys. 13, 280 (2017)）沿偏振方向测得 He 直接电离与 shake-up 的相对条纹延迟，理论与实验在阿秒尺度上一致；Schultze 2010 的 Ne 2s/2p 21±5 as 则引发电子关联辩论。此前工作只针对沿脉冲偏振方向发射，任意探测角的关联动力学未系统考察。

## 研究方法（Methods）

全维双电子 TDSE（para-He 耦合径向分波，split-operator Crank-Nicolson 传播）：XUV 90/100/110 eV、FWHIM 200 as、10¹² W/cm²，IR FWHIM 3 fs、4×10¹¹ W/cm²，40 个等间隔延迟覆盖 2 个 IR 周期。延迟提取用 SSD（质心拟合 p_f(τ) = −aA_IR(τ+t_s) + b）与 PWD 双方案互校；DLC 用 Stark 基偶极模型计算；按偶极选择规则展开各通道（direct 1 通道、n=2 5 通道、n=3 13 通道）。

## 主要发现与核心结论（Main Results）

模型：全维双电子 TDSE（para-He 耦合径向分波，split-operator Crank-Nicolson）；XUV 90/100/110 eV、FWHIM 200 as、10¹² W/cm²；IR FWHIM 3 fs、4×10¹¹ W/cm²；40 个等间隔延迟覆盖 2 个 IR 周期；延迟提取用 SSD（质心拟合 p_f(τ)=−aA_IR(τ+t_s)+b）与 PWD 双方案；DLC 用 Stark 基偶极模型。

偶极选择规则：direct 仅 1 通道，n=2 shake-up 5 通道、n=3 13 通道（一般 2n(n−1)+1）。

沿偏振方向模型 DLC 延迟与 Ossiander 关联延迟定量符合：n=2 为 7.3/6.7/5.9 as 对 7.8/6.55/5.6 as（90/100/110 eV，很好符合）；n=3 为 38.1/34.0/29.8 as 对 45.9/37.7/32.2 as（尚可）；ab initio DLC 在 n=2 反而小（1.4/2.5/3.9 as）。

绝对延迟随探测角快速下降主要源于 DLC 项的 1/cosθ 因子；shake-up 延迟符号在 θ≈40° 反转（剩余偶极取向改变）；CLC 延迟大角度变为角度依赖且为纯量子效应，经典轨迹仅 θ≲60° 与量子一致。

IR 场致剩余离子极化为小修正：n=2 壳 Δd_max ≈ 9.2×10⁻²，比 XUV 产生的 Stark 偶极 1.5 小 16 倍。

## 潜在研究方向（Future Directions）

n=3 shake-up 中 XUV 偶极 4.5 仅 6.5 倍于 IR 失真（Δd₃₁₀,max ≈ 0.69），IR 失真需进一步审查；条纹脉冲增强破坏"非失真偶极"假设时三项分解（t_EWS+t_CLC+t_DLC）失效，本文分析可为该参数域提供参考；大角度低信噪比区 DLC 模型与 ab initio 偏离的原因未解决。

## 对本课题的意义

提供"通道数—偶极选择规则"的解析结构（2n(n−1)+1），可直接作为本课题多通道模型的通道数判据；亦提示角分辨修正必须与能量分辨并置，不能只在单一角度标定。

source: KB页 wiki/papers/2024-2409_03622-photoelectronresidual-ion-entanglement-in-streaked-shake-up.md | raw/papers/2024-2409.03622-photoelectronresidual-ion-entanglement-in-streaked-shake-up.md | 检索池 references-source.md 条目[14]
