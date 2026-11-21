---
title: "First-principles electron-phonon scattering in real-time TDDFT"
type: "papers"
created: "2026-11-01T05:40:00Z"
updated: "2026-11-15T15:09:19Z"
tags: ["topic/TDDFT", "topic/电子声子耦合", "topic/计算方法"]
related: ["2607.17265", "TDDFT", "TDSE", "TDSE求解器", "arpes", "general-ssh-weyl-20260920", "含时密度泛函", "固体HHG", "固体高次谐波", "固体高次谐波产生", "实时含时密度泛函理论", "密度泛函微扰理论", "强场驱动", "高次谐波产生", "高次谐波产生（HHG）"]
source_raw: "2026-2607.17265-first-principles-electron-phonon-scattering-in-real-time-tdd.md"
growth_stage: "seedling"
confidence: 0.6
arxiv_id: "2607.17265"
authors: "Zhengwei Nie, Subhojit Pal, Marti Lüders, Alexander Buccheri, Hannes Hübener, Shunsuke A. Sato, Umberto De Giovannini"
year: "2026"
review_status: "pending"
digest_level: "abstract"
updated_at: "2026-11-08T01:04:06Z"
merged_from: ["wiki/papers/2607.17265.md"]
---

# First-principles electron-phonon scattering in real-time TDDFT

## 林赛的理解

我们的 RT-TDDFT/SBE 管线长期只有相干电子动力学，退相干靠唯象加宽硬塞；这篇把自能导出的碰撞积分（Born–Markov）塞进实时传播，让弛豫、退相干、时间分辨谱学都能在第一性原理层自洽出现——方法卡价值极高，直接是「计算设置」级别的可实施素材。

## 研究问题

如何在保持第一性原理精度的实时 TDDFT 中引入电子-声子散射（弛豫与退相干），使激光驱动固体的时间分辨谱学可预测？

## 研究背景

实时 TDDFT 给出激光驱动固体中相干电子动力学的第一性原理描述，但不含耗散通道：电子-声子散射导致的弛豫/退相干在原框架中缺失，长时动力学与有限温度谱学失真。

## 研究方法

耗散实时 TDDFT：自能导出的碰撞积分（Born–Markov 近似）嵌入实时传播；保留量子相干电子传播的同时引入 e-ph 散射通道；真实晶体材料的时间分辨光谱模拟。

## 主要发现与核心结论

框架可在真实材料中自洽模拟弛豫、退相干与时间分辨谱学：相干传播与散射耗散并存，避免了唯象展宽参数；适用于激光驱动固体的泵浦-探测类观测量。

## 潜在研究方向

超越 Born–Markov 的记忆效应；e-ph 与 e-e 散射联合；强场下的非平衡声子动力学。

## 与林赛研究的关联

- HHG 计算退相干修正：带间相干的 e-ph 退相干直接影响谐波相干性与平台结构——我们的 MoS₂/ZnO TDDFT 计算链可并入该碰撞积分。
- 方法卡候选：装置=计算框架、参数=碰撞积分构造、边界=Born–Markov 适用区。
- 与深读管线接口：has_fulltext 后按方法卡格式补参数表。

## 来源

- 蒸馏自摘要（abstract 级，arXiv 摘要补充，ZCode 消费）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：耗散实时 TDDFT：自能碰撞积分（Born–Markov）嵌入实时传播的第一性原理电子-声子散射

**原理**：在实时 TDDFT 中嵌入自能导出的碰撞积分（Born–Markov 近似），在保留量子相干电子传播的同时引入电子-声子散射通道——弛豫、退相干与时间分辨谱学在第一性原理层自洽出现，免除唯象展宽参数。

**适用边界**：Born–Markov 近似适用区（超越记忆效应为开放方向）；e-ph 与 e-e 散射联合、强场非平衡声子动力学未覆盖；摘要级，fulltext 到位后补碰撞积分构造参数。
**代表作**：Nie et al., First-principles electron-phonon scattering in real-time TDDFT, arXiv:2607.17265 (2026)
*方法卡回补 2026-11-01*


## 合并自「2607.17265」

## 深度解析

（来自简报深度分析）

## 阅读笔记

### general-ssh-weyl-20260920

*First-principles electron-phonon scattering in real-time TDDFT* — Z. Nie, S. Pal, M. Lüders, A. Buccheri, H. Hübener, S. A. Sato, U. De Giovannini (Univ. Palermo / MPI-SDM / Tohoku Univ.); arXiv v2, 2026-07-22, cond-mat.mtrl-sci

### 研究问题（Research Question）
能否把第一性原理电子-声子耦合直接嵌入实时含时密度泛函理论（rt-TDDFT）的单粒子密度矩阵演化中，给出同时包含布居弛豫与相干性衰减的非幺正耗散框架，并使其仍能给出真实晶体材料的时间分辨光谱观测量（尤其是 tr-ARPES）。核心论点是：耗散项不应是唯象退相干模型，而应来自自能导出的碰撞积分，使布居弛豫与相干衰减源自同一套微观散射道。

### 研究背景（Background）
rt-TDDFT 已成为研究强场驱动固体超快电子动力学的最成功第一性原理手段之一，可直接给出载流子激发、固体高次谐波产生（HHG）、Floquet 工程与光电子学等强场现象；但其严格幺正的闭量子系统表述无法描述不可逆弛豫、热化与退相干，而 e-ph 相互作用是载流子散射、能量耗散与退相干的主导通道。虽有唯象退相干模型与密度矩阵开放体系形式等方案，一个实用框架仍须满足三条要求：耗散动力学直接由第一性原理 e-ph 相互作用导出；一致地同时描述布居弛豫与相干衰减；对真实晶体材料计算上可行。作者指出与只演化载流子布居的半经典 Boltzmann 方法相比，本框架保留完整单粒子密度矩阵，因而可同时访问弛豫与退相干动力学。

### 研究方法（Methods）
理论上把电子视为与热声子库弱耦合的开放量子系统，总哈密顿量分为 H_S + H_E + H_S-E，二次量子化的 e-ph 耦合由第一性原理矩阵元 g^λ_mn(k,q) 给出（式7）；在 Born–Markov 近似下对声子自由度做部分迹，得到含布居-增益损失型对角项与带内/带间相干衰减非对角项的碰撞积分（式 9），并给出态依赖散射率 γn(k,t)（式 10）；所得演化满足 CPTP 性质。数值上采用混合表示：相干部分在实空间网格做 Kohn-Sham 传播，耗散碰撞积分在"活动空间"中施加，活动空间取瞬时哈密顿量的绝热 KS 基（类似 Houston 态形式），以吸收场驱动的可逆带内运动；投影后需做剩余空间补全以避免范数丢失（式 15–17），再做正交 Procrustes 规范固定（SVD，式 21–22）以保持轨道连续。速率由 Fermi 黄金规则（式 18）算出，并在细 k 网格上计算、粗 k 网格上演化，用几何簇平均做粗粒化（式 19）。计算：Octopus 代码，HGH赝势 + LDA，实空间网格间距 0.21 Å、时间步长 2 as，声子库温度 300 K；QE + EPW 给 e-ph 矩阵元，平面波截断 80 Ry。WS2：晶格常数 a = 3.15 Å，含自旋轨道耦合，30×30 MP k 网格，CP/LP 泵浦峰值强度分别为 2.5×10¹⁰ 与 1.0×10¹¹ W/cm²，激光带宽 0.5 eV，探测脉冲 128 eV/0.2 eV 带宽， phonon 在 12×12×1 q 网格上算后插值到 180×180×1 稠密 k/q 网格。Si：晶格常数 5.38 Å，20×20×20 MP k 网格，2.5 eV 线偏激光、峰值强度 2.5×10¹⁰ W/cm²，phonon 在 6×6×6 网格上算后插值到 40×40×40 网格。

### 主要发现与核心结论（Main Results）
体硅（2.5 eV 激发，弛豫前 150 fs）：ODOS 显示高能导带态与深价带空穴在数十 fs 内耗尽、谱权重在带边累积；能量分辨寿命分别为 40 fs @ 2.6 eV（Γ 谷）、106 fs @ 1.6 eV（导带 L 谷）、45 fs @ −1.2 eV（价带 L 谷），其中导带寿命与实验值 30 fs @ 2.6 eV、120 fs @ 1.6 eV 定量一致。动量分辨寿命 Γ 谷 8 fs、L 谷 14 fs，远短于能量分辨寿命，说明载流子先被散出谷、再弛豫能量（准平衡热电子集合体在宏观能量衰减前形成）；X 谷逐渐积累，是后续 ps 尺度级联冷却与谷内热化的前兆。WS2（2 eV 泵浦、300 K）：CP 光下 K 谷选择性占据，K→Q/Q′ 为快通道（前 30 fs 内 Q 与 Q′ 因各向异性 e-ph 耦合而不同、之后相等），K→K′ 为慢通道；K 谷耗尽拟合得区间谷散射时间 20 fs；LP 光下 K 谷寿命 17 fs，与实验值 16 fs 吻合（实验测的是激子动力学而本框架模拟自由载流子且未含长程偶极相互作用）。tr-ARPES（tSURFF，2 eV CP 泵浦 + 128 eV 探测，忽略 SOC）：τ = 0 时 Q/Q′ 谷强度按 300 倍放大显示，经泵浦-探测卷积模型 I(τ) = (I_pump ∗ I_probe ∗ R)(τ) 拟合得 τ0 = 13 fs，比含 SOC 的 20 fs 更短，与忽略 SOC 打开了额外散射道相一致。

### 潜在研究方向（Future Directions）
现有实现依赖 Born–Markov 与 secular 近似、把声子当作热平衡库、速率取自平衡态 e-ph 矩阵元——作者称这些"界定了当前适用范围而非根本性限制"，强非马尔可夫效应、热声子、相干核运动以及离子坐标演化的反馈都需要扩展浴描述、碰撞核或活动空间-实空间耦合。作者明确指出框架可推广到光子、磁振子、衬底等环境通道，可用于腔修饰材料、自旋-声子弛豫、声子辅助激子解离，以及退相干与相干驱动直接竞争的强场现象——并特别点名固体高次谐波产生（solid-state HHG）与泵浦-探测谱学是"特别自然的目标"，因为其解释往往依赖于常规幺正 rt-TDDFT 中缺失的弛豫与退相干机制。（对本课题直接相关：可作为固体 HHG 建模中唯象弛豫/去相干参数的 ab initio 依据来源。）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：第一性原理 e-ph 散射嵌入实时 TDDFT 的非幺正耗散框架（布居+相干统一）

**原理**：把第一性原理 e-ph 矩阵元经 Born-Markov 碰撞积分直接嵌入 rt-TDDFT 单粒子密度矩阵演化：布居弛豫与相干衰减源自同一套微观散射道（非唯象 T2），CPTP 性质保证；混合表示（实空间 KS 传播 + 活动空间绝热基施加碰撞积分 + Procrustes 规范固定）使真实晶体材料可行——为固体 HHG/泵浦-探测谱学中缺失的弛豫退相干机制提供 ab initio 依据。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 体硅能量分辨寿命 | 40 fs @ 2.6 eV（Γ 谷）/ 106 fs @ 1.6 eV（L 谷）/ 45 fs @ −1.2 eV（与实验 30/120 fs 定量一致） | 主要发现 |
| 体硅动量分辨寿命 | Γ 谷 8 fs、L 谷 14 fs（先散出谷再弛豫能量） | 主要发现 |
| WS₂ 谷间散射 | K→Q/Q′ 快通道（30 fs 内）；区间谷散射 20 fs（CP）/ K 谷寿命 17 fs（LP，实验 16 fs） | 主要发现 |
| 计算设置 | Octopus + HGH 赝势/LDA，网格 0.21 Å、步长 2 as；QE+EPW 矩阵元；WS₂ 180×180×1 稠密 k/q 网格 | 研究方法 |

**适用边界**：Born-Markov + secular 近似、声子热平衡库、平衡态速率（强非马尔可夫/热声子/相干核运动需扩展）；WS₂ 的 13 fs（无 SOC）vs 20 fs（含 SOC）差异表明散射道开放性依赖 SOC 处理；LP 实验对比的是激子而模拟为自由载流子（未含长程偶极）。
**代表作**：Nie et al., First-principles electron-phonon scattering in real-time TDDFT, arXiv:2607.17265 (2026)
*方法卡回补 2026-10-29*

<!-- linsai-wikilinks -->
## 关联概念

- [[2607.17265]]
- [[TDDFT]]
- [[TDSE]]
- [[TDSE求解器]]
- [[arpes]]
- [[general-ssh-weyl-20260920]]
- [[含时密度泛函]]
- [[固体HHG]]
- [[固体高次谐波]]
- [[固体高次谐波产生]]
- [[实时含时密度泛函理论]]
- [[密度泛函微扰理论]]
- [[强场驱动]]
- [[高次谐波产生]]
- [[高次谐波产生（HHG）]]
<!-- /linsai-wikilinks -->
