---
title: "2025-2505_03354-physics-informed-neural-networks-in-electromagnetic-and-nano"
type: "papers"
created: "2026-09-27T18:51:23Z"
updated: "2026-11-15T15:09:24Z"
tags: []
related: ["PINN（物理信息神经网络）", "TDSE", "pump-probe", "quantum metric", "低阶谐波窗口（1-4 阶）", "强场超快", "强场驱动", "量子几何", "非线性光学"]
source_raw: "2025-2505.03354-physics-informed-neural-networks-in-electromagnetic-and-nano.md"
growth_stage: "seedling"
confidence: 0.5
digest_level: "fulltext"
---

# Physics-Informed Neural Networks in Electromagnetic and Nanophotonic Design

## 林赛的理解

这篇是 2025 年发表在 ArXiv 的综述（arXiv:2505.03354），系统梳理 PINN（物理信息神经网络）如何嵌入 Maxwell 方程等物理约束用于电磁/纳米光子学正向与逆向设计。对我们组的强场超快方向而言，这篇综述不是直接讲阿秒/HHG 的，但它把**FDTD/FEM 求解 Maxwell 方程 → PINN 嵌入 Maxwell 残差作为 loss → 逆向设计纳米结构**这条工具链梳理得很完整。我们做纳米针尖/纳米天线里 HHG 增强、莫尔/异质结里强场驱动量子几何响应、等离激元近场增强动力学时，PINN 框架可以替代/加速传统 FDTD，并对**数据稀缺、稀疏测量**的实验场景（阿秒瞬态、近场 mapping）特别有用。方法卡片中的 PINN 损失函数、collocation 点采样、AD 自动微分、混合 FDTD-CNN 架构是可直接复用的素材。

## 研究问题

核心问题：**如何用 PINN 把 Maxwell 方程等物理约束嵌入神经网络训练流程，使其在数据稀缺条件下仍能稳定地完成纳米光子/电磁结构的正向代理建模与逆向设计**，从而绕过传统"trial-and-error + FDTD/FEM 反复迭代"的范式。具体而言，论文试图回答四个子问题：(1) PINN 如何形式化地把 PDE 残差（Maxwell、波动方程等）作为额外损失与数据损失联合优化；(2) 在纳米光子学中，DNN/PINN 已成功应用在哪些前向/逆向设计任务（散射截面、相位梯度、超表面、全息、光学神经网路、可重构超表面等）；(3) PINN 与传统 FDTD/FEM 相比在精度-速度-可扩展性上的权衡；(4) 当前 AI 驱动光子设计的局限（可解释性、数据稀缺、非传统模式）与未来出路（多物理耦合、可适应架构、实用部署）。

## 研究背景

学术脉络：自 2010 年代以来，DNN 因 ImageNet/GAN/Transformer 浪潮迅速渗透到科学计算；纳米光子学传统依赖**FDTD（时域有限差分）**与**FEM（有限元）**精确求解 Maxwell 方程组，但这两类方法对宽带瞬态需要细网格、大内存，大规模三维模拟代价高昂。PINN 由 Raissi 等 2019 年提出，将 PDE 残差作为软约束嵌入神经网络损失，对**数据稀缺、需满足物理守恒**的逆问题具有天然优势。近五年 PINN 被引入纳米光子学：嵌入式 Maxwell 残差用于隐形斗篷逆向设计、THz 时域动力学建模、三维光衍射全息超表面、可编程超表面（相变/可调电介质）以及天线/FSS 设计。论文同时指出近年 DNN 在 forward design 已广泛成功（Malkiel 2018 散射预测、Peurifoy 2018 多层纳米结构光谱、Asano CNN 优化 2D-PC Q 因子、So/Wiecha 非周期超表面、U-Net 像素化超表面、注意力机制、GAN+拓扑优化高衍射效率超表面等）。

研究动机：(i) 传统正向电磁仿真（FDTD/FEM）算力瓶颈阻碍了高维设计空间探索；(ii) 逆向设计存在非唯一性，传统拓扑优化易陷入局部极小；(iii) 实验/仿真数据稀缺（特别是新型光学模式、瞬态过程）使得纯数据驱动方法泛化差；(iv) 缺乏统一的"AI 框架对比评估"——论文目的即填补这一空白。

## 研究方法

> 注：本节同时承担两个角色——(a) 综述本身的文献检索/筛选方法（review methodology），与 (b) 论文重点讲解的 PINN 方法学资产（方法卡素材）。论文全文因输入截断只覆盖到 §2.2，后续节段（很可能包含 PINN 反向设计、非线性光学、meta-optics、ONN、电磁应用、结论）未能读全，下方内容忠实于已得段落。

### (a) 综述方法（review pipeline）

论文采用**结构化主题综述**（非系统 PRISMA）方式：先按"AI/DNN 概念 → PINN 概念 → 纳米光子学基础 → 传统数值方法（FDTD/FEM）→ DNN 前向/逆向设计 → PINN 应用"线性铺陈，配以单图（图 1-4）总览各子方向代表作，引用编号 1-83（已读部分）集中在 2018-2025。综述的纳入标准是"AI/DNN/PINN 在电磁/纳米光子的代表性工作"，不含定量文献质量评分。

### (b) 关键方法卡——PINN（Physics-Informed Neural Network）

**原理**：PINN 把已知物理定律（PDE，如 Maxwell、波动方程）作为**软约束**嵌入神经网络损失函数。对要逼近的物理场 u(x,t)（电磁场、电势等），用一个参数为 θ 的 DNN 输出 u_θ(x,t)；训练时同时最小化数据损失（与观测/真值差异）和物理损失（PDE 残差），从而在小数据下获得符合物理的解，并天然支持反问题（材料参数/几何作为可学习变量）。

**参数表（数值原样，含单位与出处）**：

| 项 | 数值/形式 | 出处（论文方程/段） |
|---|---|---|
| 神经元前向 | a^(l) = f(W^(l)·a^(l-1) + b^(l)) | Eq.(1), §1.2.1 |
| 权重梯度（反向传播） | ∂L/∂w = (∂L/∂a)·(∂a/∂z)·(∂z/∂w) | Eq.(2), §1.2.2 |
| PINN 总损失 | ℒ = ℒ_data + λ·ℒ_PDE | Eq.(3), §1.3.2 |
| 物理（PDE 残差）损失 | ℒ_PDE = (1/N_c)·Σ‖𝒩[u_θ(x_i,t_i)]‖² | Eq.(4), §1.3.2 |
| PDE 形式 | 𝒩[u(x,t)] = 0，𝒩 为非线性微分算子 | §1.3.2 |
| 平衡超参数 | λ（数据损失与物理损失权重） | §1.3.2 |
| Collocation 点数 | N_c（域内采样点数） | §1.3.2 |
| 优化器 | Adam、SGD、RMSprop | §1.2.2 |
| 激活函数 | ReLU、sigmoid、tanh | §1.2.1 |
| 正则化 | Dropout、L1、L2 weight reg、Early stopping | §1.2.2 |
| 训练流程 | 数据准备 → collocation 采样 → 前向传播 → AD 求 PDE 残差 → 总损失 → 反向 Adam 更新 θ | §1.3.2 |
| 求导方式 | Automatic Differentiation（避免数值差分） | §1.3.2 |
| 代表架构变体 | PINN-DNN for Maxwell、CNN+FDM PINN、Physics-informed Autoencoder、Physics-informed LSTM | Fig.3a-d, §1.3.3 |
| 应用领域 | 反向隐形/几何优化、THz 时域动力学、3D 光衍射全息、可编程超表面、天线/FSS | §1.1, Fig.1 i-m |

**适用边界**：
- 适合：数据稀疏但 PDE 已知（Maxwell、波动、热传导）；正则化反问题（材料/几何参数推断）；需要物理一致性约束的代理建模
- 失效/困难：病态/多尺度问题（如亚波长金属边界附近的尖锐场梯度）；强散射/尖锐共振附近 PINN 易出现梯度偏差；高维参数空间 collocation 点数指数爆炸；非传统模式（拓扑光子态、强非线性）训练数据稀缺
- 统计/分辨率：未量化，依赖 collocation 点密度 N_c 与 λ 调节

### (b') 关键方法卡——FDTD vs FEM（传统数值电磁基线）

**原理**：FDTD 在时域离散 Maxwell 旋度方程蛙跳迭代，适合宽带瞬态；FEM 在频域离散 Helmholtz 形式，用基函数在有限单元上展开，适合复杂几何各向异性材料。

**参数表**：

| 项 | FDTD | FEM |
|---|---|---|
| 离散域 | 时间+空间 | 空间（频域） |
| 求解形式 | 显式时间步进 | 隐式大型方程组 |
| 强项 | 宽带瞬态、并行化、周期性结构、光子晶体 | 复杂几何、各向异性材料、局域场高精度 |
| 弱项 | 内存大、3D 精细网格代价高 | 大域宽带分析耗时长 |
| 适用任务 | 脉冲传播、时间分辨、瞬态 | 频域模式、局域场精细结构 |

**适用边界**：FDTD 在材料界面需细网格抑制数值伪影；FEM 内存取决于网格复杂度与基函数阶数；二者共同瓶颈是**大规模三维 + 宽带 + 多物理**。

### (b'') 关键方法卡——DNN 主流架构（用于前向代理与逆向生成）

**原理**：以输入-输出配对数据驱动学习纳米光子结构-光谱映射，支持快速推理。

**参数表（架构与典型任务）**：

| 架构 | 结构特点 | 纳米光子任务 |
|---|---|---|
| FNN（fully-connected） | 全连接层 | 散射光谱预测、低维参数→响应映射 |
| CNN | 卷积+池化，层级空间特征 | 非周期超表面远场、3D 纳米结构 transmittance/reflectance |
| U-Net（encoder-decoder） | 跳跃连接，像素级预测 | 像素化超表面→光谱、几何→光谱 |
| RNN/LSTM | 时序门控 | 光谱序列、波长相关色散特性 |
| Autoencoder / VAE / GAN | 潜空间压缩/生成 | 高衍射效率超表面逆向生成、数据增广 |
| Tandem DNN | forward+inverse 双网络串联 | 多层 SiO2-Si3N4 逆向设计 |
| 注意力增强 encoder-decoder | 关键区域加权 | 强各向异性/异质结构预测 |

**定量典型结果**：Liu 等训练数据 **500,000 labelled pairs**；Mohammed 等 SOI 功分器 **>90% transmission**；Gao 等轻量模型推理 **毫秒级**。

**适用边界**：泛化到未见几何需大量 FDTD 数据；纯数据驱动不保证物理一致性；适合"结构-光谱"相对平滑映射，对强共振、奇异点附近需结合 PINN 或迁移学习。

## 主要发现与核心结论

> 注：因全文截断至 §2.2 中段（"Moreover, developing hybrid models that combine neural networks with tradition…"），下列发现只覆盖论文已读段落。未读章节（很可能包含 PINN 反向设计细节、非线性光子学、超表面/光学神经网络新结果、未来展望）这一段不可考。

1. **DNN 前向代理可"数量级加速"传统 FDTD**：Malkiel 等早期工作给出"orders of magnitude faster"预测（相对于传统求解器），论文定性表述，未给具体倍数（避免升格）。

2. **多层纳米结构光谱预测**：Peurifoy 等使用多层 DNN 配合 FDTD 合成数据集训练，可"按需"生成远场散射图样，方法可扩展到宽类纳米光子器件。

3. **集成光子功分器优化**：Mohammed 等用 DNN 设计 SOI 功分器，达到 **>90% transmission**、低反射、精确功率分束比，**秒级**完成设计（原句："within seconds"）。

4. **SiO2-Si3N4 多层腔光调制**：Liu 等用 Tandem DNN（forward + inverse）训练 **500,000 labelled data pairs**（layer thicknesses → transmission spectra），处理逆向设计非唯一性，进一步扩展到 2D 多波长相位调制。

5. **CNN 用于 2D-PC 纳米腔**：Asano 等基于随机生成纳米腔数据集，CNN 建立结构-Q 因子映射，梯度优化得到"显著高于手工优化"的 Q 因子（原文 "dramatically higher than manual optimization methods"，未给具体倍数）。

6. **非周期超表面远场预测**：So 等用 2D 几何表示作为输入，CNN 学习空间相关性；Wiecha 等扩展到复杂 3D 纳米结构多光谱（transmittance、reflectance）预测，具备几何无关泛化能力。

7. **U-Net 像素化超表面→光谱**：Tan 等层级编码细粒几何→精确光谱；Gao 等加入注意力模块提升各向异性/异质结构预测精度，并提供物理解释性。

8. **数据稀缺缓解**：Ma 等半监督 + 自监督预训练；Chen 等（2022）迁移学习（大数据集预训练 → 小数据集微调）；Adibnia 等（2023）RNN 把光谱视为时序序列，相邻波长相关性建模优于全连接网络；Gao 等（2022）通过剪枝压缩模型，**毫秒级**推理实现实时反馈。

9. **生成式逆向设计**：Liu 等无监督自动发现超表面结构；Jiang 等 GAN + 拓扑优化在高衍射效率目标波长/入射角超表面设计上**显著减少训练数据需求**（未量化）。

10. **传统方法权衡**：FDTD 适合宽带瞬态但内存大；FEM 适合复杂几何各向异性频域但大域耗时；二者共同推动 AI 代理/PINN 嵌入方向。

11. **PINN 三重价值**（论文 §1.3.1 概括）：(i) 物理作为归纳偏置，降低数据需求；(ii) 强制物理一致性（守恒律、边界）；(iii) 天然支持反问题（材料/几何可学习）。PINN 损失 = ℒ_data + λ·ℒ_PDE（Eq. 3-4），通过自动微分（AD）避免数值差分。

12. **新兴 PINN 架构**：PINN-DNN for Maxwell（场与材料参数双网络）、CNN+FDM PINN（空间依赖 + PDE 残差）、Physics-informed Autoencoder（潜空间 + 物理损失）、Physics-informed LSTM（时序微分方程约束）。

13. **PINN 在光子学的应用图谱**（已读段归纳）：逆向设计 + 隐形斗篷（嵌入 Maxwell，ref 11）、THz 时域动力学（ref 12）、3D 光衍射全息（ref 15）、可编程超表面相变/可调电介质（ref 14）、天线/FSS hybrid gradient-physics（ref 13）。

## 潜在研究方向

> 注：以下综合论文已读段明示的开放问题 + 截断未读段可能在的议题。

**论文明示局限**（摘要 + §1.1 末尾 + §1.3.1 暗示）：
- AI 模型**可解释性有限**——物理机制如何涌现于网络权重仍不清晰
- **非传统光学模式数据稀缺**——拓扑光子态、强非线性、奇异光学现象的训练样本严重不足
- **多物理耦合建模**仍是开放问题（光-热-力-电-磁耦合）
- **可扩展架构与实用部署**——从仿真代理到实验闭环、从离线设计到实时自适应控制
- **数据-物理平衡超参数 λ 缺乏普适选择准则**

**对强场超快方向的隐性局限**（林赛视角补充）：
- PINN 在强场非微扰区（Keldysh γ ~ 1，隧穿电离）的适用性未在论文中讨论——非微扰 HHG 不再由线性 Maxwell 主导，需耦合 TDSE 或 SFA 模型
- 阿秒瞬态（sub-fs、as 时间尺度）对应的极高时间分辨率需求，与 PINN collocation 采样密度冲突
- 近场等离激元增强区域的**尖锐场梯度**（金属界面 nm 级）易使 AD 残差爆炸
- 实验数据带噪、稀疏、单发（single-shot），PINN 中 ℒ_data 与 ℒ_PDE 的 λ 选择成为关键
- 量子几何/莫尔能带中的强场响应需 Berry connection / quantum metric 嵌入，PINN 框架原生不支持——需扩展

**论文提到的未来机遇**：可扩展多物理建模、可适应（adaptive）架构、AI 优化光子器件的实用部署。

## 与林赛研究的关联

具体接口与潜在应用：

1. **HHG 增强纳米结构逆向设计**：我们用纳米针尖/纳米天线/介质球产生近场增强 HHG，传统靠 FDTD sweep + 强场 TDSE 计算，代价极大。论文 §1.3 的 PINN-DNN-for-Maxwell 框架（图 3a，ref 30）可作为近场代理，结合我们已有的强场模型做"几何 → 增强因子 → HHG 产额"端到端逆向。Maxwell 残差作为 ℒ_PDE 的 λ 平衡是直接可迁移的关键。

2. **阿秒脉冲整形/聚焦超表面设计**：论文 §1.1 + Fig.1(d)/(j)/(m) 提到的 phase-gradient 全息与可编程 metasurface 直接对应阿秒脉冲波前控制；PINN-guided 3D 衍射（ref 15）可加速宽带（XUV-soft-X）超表面设计。强场超快实验常需色散补偿 + 波前整形，PINN 嵌入波动方程提供物理一致性。

3. **THz 强场驱动**：论文明确把 THz pulse dynamics（ref 12, Fig.1j）作为 PINN 应用之一。THz 场是强场驱动的常用激发源（尤其在磁性材料中驱动自旋动力学），PINN 建模 THz-物质相互作用可作前向代理。

4. **交变磁/莫尔系统中的强场响应**：这一块论文未直接覆盖，但 PINN 思路可扩展——把 magnetic LL equation 或 Landau-Lifshitz-Gilbert（LLG）方程嵌入 ℒ_PDE，结合实验 pump-probe 数据反推有效各向异性、阻尼、Berry curvature 参数。

5. **量子几何（quantum geometry）的强场指纹**：Berry connection / quantum metric / nonlinear Hall 等响应可作为可学习物理量嵌入 PINN；这是论文未触及但与我们方向（"强场驱动量子几何"潜在主题词）密切相关的扩展方向。建议作为**课题方案的方法素材**：以 PINN 为基座，针对 Keldysh 隧穿区耦合 TDSE/SFA，构建"强场专用 PINN"。

6. **数据稀缺问题与我们契合**：阿秒实验数据天然稀缺、昂贵、单发，论文 §1.3.1 强调 PINN "物理作为归纳偏置降低数据需求"正是我们最需要的特性。Ma 半监督 + Chen 迁移学习 + Adibnia RNN 时序光谱 三套策略可迁移到阿秒光谱反演与近场 mapping。

7. **方法资产沉淀**：把"Maxwell PINN + AD + collocation + λ 平衡 + Adam 训练"整理成可复用方法卡（参数表已在上面 (b) 节沉淀），供后续 proposals 与组内方法页融合。

**与方向词的引用**：
- HHG / 阿秒：接口 1, 2, 6
- 强场驱动：接口 1, 3, 4, 5
- 交变磁：接口 4
- 莫尔：接口 4（LLG + 莫尔耦合）
- 量子几何：接口 5

## 来源

- 蒸馏自全文（deep-read）；注：arXiv:2505.03354 全文长度超出本次输入截断，已读内容覆盖 §1-§2.2 中段（"Moreover, developing hybrid models that combine neural networks with tradition…"处截断）。后续节段（PINN 反向设计、非线性光学、meta-optics、ONN、电磁应用、挑战与未来方向、结论）未读，相关定量结论留待补全。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：PINN 物理信息神经网络（电磁/纳米光子综述讲解版）

**原理**：把已知物理定律（PDE，如 Maxwell/波动方程）作为软约束嵌入神经网络损失：DNN 输出 u_θ(x,t)，训练同时最小化数据损失与 PDE 残差损失 ℒ = ℒ_data + λ·ℒ_PDE，PDE 残差经自动微分（避免数值差分）在 N_c 个 collocation 点上评估；小数据下获得符合物理的解，天然支持反问题（材料参数/几何作为可学习变量）。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 总损失 | ℒ = ℒ_data + λ·ℒ_PDE；ℒ_PDE = (1/N_c)·Σ‖𝒩[u_θ(x_i,t_i)]‖²（λ 为平衡超参数） | Eq.(3)(4), §1.3.2 |
| 优化器/激活 | Adam、SGD、RMSprop；ReLU、sigmoid、tanh | §1.2 |
| 正则化 | Dropout、L1/L2 weight reg、Early stopping | §1.2.2 |
| 架构变体 | PINN-DNN for Maxwell、CNN+FDM PINN、Physics-informed Autoencoder、Physics-informed LSTM | Fig.3a-d |
| 应用 | 反向隐形/几何优化、THz 时域动力学、3D 光衍射全息、可编程超表面、天线/FSS | §1.1 |

**适用边界**：本页为结构化主题综述（非 PRISMA，无定量文献质量评分）；全文因输入截断仅覆盖至 §2.2（约引用 1-83），PINN 反向设计、非线性光学、meta-optics、ONN 等后续节未读全，方法学资产以后半部分为准可能不完整。
**代表作**：本综述（arXiv:2505.03354）；Raissi et al. PINN 原始框架（综述内引用）
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[PINN（物理信息神经网络）]]
- [[TDSE]]
- [[pump-probe]]
- [[quantum metric]]
- [[低阶谐波窗口（1-4 阶）]]
- [[强场超快]]
- [[强场驱动]]
- [[量子几何]]
- [[非线性光学]]
<!-- /linsai-wikilinks -->
