---
title: "2026-260914993-1d-interface-induced-real-space-berry-curvatu"
type: "papers"
created: "2026-09-26T10:52:49Z"
updated: "2026-11-16T05:30:15Z"
tags: []
related: ["1D Interface-Induced Real-Space Berry Curvature Gradient", "1D Interface-Induced Real-Space Berry Curvature Gradient Encoded in SpinValley-Coupled Nonlinear Photocurrent in Lateral Heterostructure", "Berry curvature dipole", "Berry 曲率", "Berry曲率", "MnPS3", "PLAN", "general-berry-mnps3-rashba-20260816", "光波电子学", "圆二色性", "层间耦合", "强场超快", "强场超快光学", "强场驱动", "泵浦探测", "谷极化", "量子几何", "非线性光学"]
source_raw: "2026-2609.14993-1d-interface-induced-real-space-berry-curvature-gr.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
digest_level: "abstract"
updated_at: "2026-10-27T12:48:06Z"
merged_from: ["wiki/papers/2609.14993.md"]
---

• ---
  title: "1D 界面诱导的实空间 Berry 曲率梯度：侧向异质结中自旋-谷耦合非线性光电流"
  type: papers
  created: "2026-09-26T10:52:30Z"
  updated: "2026-09-26T10:52:30Z"
  tags: ["valleytronics", "TMD", "光电流", "Berry曲率", "异质结", "拓扑光学"]
  related: ["谷电子学", "圆偏振光电流", "拓扑材料光学响应", "二维材料异质结", "非线性光学"]
  source_raw: "2026-2609.14993-1d-interface-induced-real-space-berry-curvature-gr.md"
  growth_stage: "growing"
  confidence: 0.7
  auto_grown: true
  review_status: "pending"
  ---

  # 1D 界面诱导的实空间 Berry 曲率梯度：侧向异质结中自旋-谷耦合非线性光电流

  ## 林赛的理解

  这篇工作触及我长期关注的一个核心问题：**Berry 曲率这类动量空间拓扑量，如何被"翻译"成可测量的实空间输运信号**。在强场超快光学里，我们习惯用高次谐波、超快泵浦探测去看拓扑物态的动力学响应；而这篇文章走的是另一条路——用稳态非局域光电流成像，把界面诱导的 Berry 曲率偶极（Berry curvature dipole）"读"出来。思路对我们有直接启发：界面（1D 边界）作为对称性破缺的天然来源，可以在法向入射下实现本征圆偏振光伏效应（CPGE），绕过了传统 CPC 依赖斜入射圆光子曳引效应的限制。

  我读这篇的动机不只是 valleytronics 本身，而是方法论：他们用空间分辨 + 光谱选择激发（MoSe₂、WSe₂、界面区三个区域分别激发），把信号来源做了区域归属——MoSe₂ 和 WSe₂ 的 CPC 响应极性相反（反映相反的 spin-valley 二色性），界面区则表现出增强的谷混合。这种"空间分辨归因"的思路，完全可以移植到我们的超快测量里：把空间选区与超快时间分辨结合起来，界面处的非平衡谷动力学应该是个富矿。

  ## 核心要点

  - **核心发现**：在 CVD 生长的单层 2D 侧向异质结（MoSe₂/WSe₂）上观测到法向入射下的本征 CPGE 清晰信号，机制归因于界面诱导的 Berry 曲率不对称性，即 Berry 曲率偶极。
  - **方法亮点**：
    - 非局域光电流测量跨越 1D 异质界面；
    - 空间分辨 + 光谱分辨的选择激发，分别探测 MoSe₂、WSe₂ 和界面区域；
    - 三个区域展现出量级与极性各不相同的 CPGE 响应，实现信号的空间归因。
  - **物理内涵**：MoSe₂ 与 WSe₂ 的相反响应极性对应两者相反的 spin-valley 二色性；界面区的差异响应反映增强的谷混合——界面对称性破缺同时调制了自旋-谷耦合。
  - **意义**：确立了侧向异质结作为实现"异质界面诱导 CPGE 型响应"的稳健平台，对谷电子学与自旋光电子器件设计有应用价值。

  ## 实验/研究关联

  - **与本实验室方向的交集**：
    - NSFC-强场超快项目的 valleytronics 方向：本文提供了一条稳态/光电探测路线去感知 Berry 曲率结构，可与我们超快探测路线互补——他们测"静态拓扑指纹"，我们测"拓扑量的非平衡演化"。
    - 界面作为对称性工程工具：1D 界面诱导的实空间 Berry 曲率梯度，提示我们强场驱动下的界面（畴壁、异质结）也可能是 HHG 中对称性破缺信号的增强来源。
  - **可借鉴的技术点**：
    - 空间-光谱双重分辨的测量设计；
    - 非局域（nonlocal）测量几何，把远离激发点的电流作为观测量，降低局域背景干扰。
  - **提示的交叉问题**：界面增强的谷混合是否对应更快的谷退相干？超快时间分辨 + 界面空间选区的组合目前文献中似乎稀缺，是一个空白点。

  ## 开放问题

  - 界面处 Berry 曲率偶极的定量强度未在摘要层面给出，需要阅读原文的定量分析；
  - 谷混合增强的机制（界面态？应力梯度？化学计量起伏？）尚待厘清；
  - CPGE 信号的温度依赖与载流子密度依赖未知——这决定了它是界面本征属性还是输运辅助效应；
  - 该稳态信号与超快非平衡谷动力学（如瞬态圆二色性、超快自旋/谷极化弛豫）如何对接，文中未涉及；
  - CVD 生长的界面原子结构（是否尖锐、有无合金化过渡区）对信号的影响未讨论，这直接关联可重复性。

  ## 来源
  - 原始材料：2026-260914993-1d-interface-induced-real-space-berry-curvatu.md
  - 蒸馏时间：2026-09-26T10:52:30Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：空间-光谱双重分辨非局域光电流测量——1D 侧向异质结（MoSe₂/WSe₂）界面诱导 Berry 曲率偶极的本征圆偏振光伏效应（CPGE）

**原理**：CVD 生长的单层 2D 侧向异质结（MoSe₂/WSe₂）上，法向入射下观测到本征 CPGE 清晰信号——机制为 1D 界面诱导的 Berry 曲率不对称性（Berry 曲率偶极）：界面（1D 边界）作为对称性破缺天然来源，绕过传统 CPGE 依赖斜入射圆光子曳引的限制；空间分辨 + 光谱选择激发（MoSe₂/WSe₂/界面区分别激发）实现信号空间归因：MoSe₂ 与 WSe₂ 的 CPC 响应极性相反（对应相反 spin-valley 二色性）、界面区呈现增强谷混合——界面对称破缺同时调制自旋-谷耦合；确立侧向异质结为'异质界面诱导 CPGE 型响应'的稳健平台。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 测量方案 | 非局域光电流测量跨越 1D 异质界面；空间分辨 + 光谱分辨选择激发（MoSe₂/WSe₂/界面三区归因）；法向入射本征 CPGE | 核心要点 |

**适用边界**：摘要级页面（digest_level=abstract），界面 Berry 曲率偶极的定量强度未给；谷混合增强机制（界面态/应力梯度/化学计量起伏）待厘清；CPGE 温度与载流子密度依赖未知（界面本征属性 vs 输运辅助效应）；稳态信号与超快非平衡谷动力学的对接未涉及；CVD 界面原子结构（尖锐度/合金化过渡区）对信号与可重复性的影响未讨论。
**代表作**：1D 界面诱导的实空间 Berry 曲率梯度：侧向异质结中自旋-谷耦合非线性光电流（MoSe₂/WSe₂ 侧向异质结，arXiv:2609.14993，2026）
*方法卡回补 2026-10-03*


## 合并自「1D Interface-Induced Real-Space Berry Curvature Gradient Encoded in SpinValley-Coupled Nonlinear Photocurrent in Lateral Heterostructure」

## 阅读笔记

### general-berry-mnps3-rashba-20260816

我已收集到论文的完整信息。现在整理结构化笔记如下。

---

## 调研主题
来源：[arXiv:2609.14993 — 1D Interface-Induced Real-Space Berry Curvature Gradient Encoded in Spin-Valley-Coupled Nonlinear Photocurrent in Lateral Heterostructure](https://arxiv.org/abs/2609.14993)（Chakraborty 等，印度 IIT Kharagpur + 德国 RWTH Aachen，2026-09-14 投稿，cond-mat.mes-hall）。

## 研究问题（Research Question）
- 核心问题：在原子级锐利的 1D 异质界面（MoSe2–WSe2 横向异质结，LHS）下，能否在法向入射（normal incidence）下观测到由 Berry 曲率偶极子（Berry Curvature Dipole, BCD）驱动的本征圆光电流效应（CPGE），而无需借助斜入射的光子拖曳效应（CPDE）？
- 目标：探究 1D 异质界面对称性破缺与 spin-valley 耦合之间的内禀联系，以及这种实空间 Berry 曲率梯度如何被编码进非线性光电流中。
- 中心论点：横向异质界面诱导的非均匀 Berry 曲率分布产生有限 BCD，使 CPGE 即使在零栅压（VG=0 V）和零偏压（VDS=0 V）下也可被观测，从而为 valleytronics 与光自旋电子学提供新平台。

## 研究背景（Background）
- 圆极化光电流（CPC）在碲、量子阱、Weyl 半金属、二维 TMD 中已被广泛报道，但 monolayer TMD 由于镜面对称性保留，净 Berry 曲率贡献抵消，使本征 CPGE 在法向入射下难以观测，过去观测的多为斜入射下的圆光子拖曳效应（CPDE）。
- Xiao 等人（PRL 108, 196802, 2012）的 spin-valley 耦合理论奠定了 monolayer TMD 的 valley 选择激发与 Berry 曲率基础；Yuan 等人（Nat. Nanotechnol. 9, 851, 2014）首次在 WSe2 中观测 spin-valley 耦合 CPGE；Duan 等人（Nat. Nanotechnol. 18, 867, 2023）提出对称性失配异质界面产生 BCD。
- 在 van der Waals 异质结中，扭转角 / 堆垛 / 异质界面已被用来破缺镜面对称，但 sub-micron 局域激发、源漏电极中线对齐下的 CPGE 至今未实现。本工作将 Sahoo 等人（Nature 553, 63, 2018）发展的"one-pot 边缘外延"CVD 横向异质结生长方法应用到 spin-valley CPGE 研究中，填补了内禀异质界面 BCD 与光电流机制的研究空白。

## 研究方法（Methods）
- 样品制备：CVD 单层 MoSe2–WSe2 LHS 通过 one-pot 水辅助边缘外延生长在 Si/SiO2 衬底上；MoSe2 在 N2+H2O 氧化气氛下先生长，随后切换至 Ar+H2(5%) 在 MoSe2 边缘上外延 WSe2，1D 界面原子级锐利（HAADF-STEM 实测）。
- 器件结构：PDMS/PC 干法转移 + hBN 封装 + 石墨烯接触，LHS 置于背栅（FLG）FET 构型，电极 Cr(5 nm)/Au(70 nm)；源-漏电极横跨 1D 异质界面，非局域测量。
- 光电测量：AttoLIQUID1000 低温恒温器（4 K），NA=0.82 物镜将 ~636 nm 激光聚焦至 ~400 nm 亚微米光斑；半波片 / 1/4 波片 + ANR240 piezo rotator 自动控制偏振态；287 Hz 光学斩波器 + SR830 锁相（增益 10^6，电流灵敏度 5 nA）提高信噪比；用反射对比（RC）、PL、KPFM、I–V 与 transfer特性表征器件。
- 数据分析：极化依赖光电流用现象学方程 I_PC(θ) = C·sin(2θ) + L1·sin(4θ) + L2·cos(4θ) + D 拟合，分别提取 CPGE 系数 C、线性光电流效应 LPGE 系数 L1、线性光子拖曳 LPDE 系数 L2 及偏振无关背景 D；定义 CPC 极化率 |C/(C+L1+L2)|×100% 与 FOM = C/L2。
- 理论建模：在 massive Dirac fermion 框架下分别写出轨道型 Berry 曲率（Ω_orbital）与自旋型 Berry 曲率（Ω_spin）表达式（包含 Rashba α_R、Ising SOC λc,v 与带隙 Δ）；用 ∂Ω(k,x)/∂x 表示实空间 Berry 曲率梯度，推导出 CPGE 电流正比于该梯度（式 2–7）；并对 VG依赖的空间 Ω(k,x) 与 BCD 分布进行数值模拟。

## 主要发现与核心结论（Main Results）
- 在 636 nm（接近 MoSe2 B 激子共振）激发下，MoSe2 域局域激发的 1/4 波片依赖光电流在 θ=45° 与 θ=135° 表现明显不对称，证明存在 helicity 依赖的 CPC；半波片下 IPC(45°)≈IPC(135°)，排除各向异性、器件非均匀、接触不对称与光路失准的影响，证实 CPGE（非 CPDE）为主导机制。
- 拟合得到的 CPGE 系数 C 在1/4 波片下相对权重 |C/(C+L1+L2)| 从 15% 提升到 66%（≈3 倍增强），LPGE 系数 L1 始终大于 LPDE 系数 L2，表明异质界面降低了晶体对称性使 LPGE 允许。
- 在三个激发位点（MoSe2 / 1D 界面 / WSe2）的对比测量中：C 的极性在 MoSe2 与 WSe2 之间反转（VG=1.5 V, VDS=−0.8 V），归因于两者相反的 Ising SOC 自旋排列 → 相反 Berry 曲率极性；界面信号极性与 WSe2 相同，源于 MoSe2 较弱的 SOC 引起更强 valley 混合从而抑制 MoSe2-like 贡献；LPDE 极性在三个位点相同（仅依赖偏振角，与对称性无关）。
- CPC 极化率（VG=1.5 V, VDS=−0.8 V）分别为 37%（MoSe2）/ 30%（界面）/ 16%（WSe2）；FOM 在 MoSe2 域随反向 VDS 单调增大（最大 ~2.5），而在界面处减小——前者由载流子漂移增强 BCD 异常速度，后者由 depletion 加宽抬高背景电流；MoSe2 的 CPC 极化率随 VDS 增加单调上升至 ~10%。
- 532 nm 离共振激发下 CPGE 响应显著减弱（Fig. S13），证实激子共振调控 helicity-载流子转换效率；MoSe2 B 激子共振 + bright 最低激子态使其 CPGE 幅值最大，WSe2 暗激子态则压制其响应。
- 模拟结果（图 5d–f）显示自旋 Berry 曲率 Ω_spin 在 MoSe2 与 WSe2 之间极性反转，BCD 在 1D 界面处达最大值，CPGE 电流极性反转与实验一致；定性地证实了 spin-type Berry 曲率在 Δ~1–2 eV ≫ α_R, λ~10–100 meV 下占主导，Ω_spin ≫ Ω_orbital。

## 潜在研究方向（Future Directions）
- 当前理论框架仅考虑平衡条件下的内禀几何贡献，未显式包含激子共振依赖的光学吸收效率与载流子非平衡分布；MoSe2 与 WSe2 的 CPGE 幅值在模拟中可比，而实验观测到明显不对称——后续需引入 nonequilibrium 动力学与激子效应做完整定量对照。
- 异质界面处 valley混合与内建电场之间的竞争虽已定性讨论（界面 CPGE 介于 MoSe2 与 WSe2 之间），但具体机制尚需更精细的微观理论，特别是 in-plane 电场与平移对称性破缺对 Berry 曲率极性的修改（文中明确指出"a detailed understanding ... requires further theoretical investigation"）。
- 当前测量局限于 4 K；尚不清楚室温下 BCD 与 CPGE 的稳定性，以及 spin-valley 寿命（MoSe2 已报道达100 ns @ RT）是否足以保留 helicity 信息；走向器件应用需要在 RT 下进一步验证。
- 异质界面处 CPGE 的空间分辨尺度（400 nm 光斑 vs. 1D 界面宽度）还可进一步缩小光斑至 ~100 nm 以下，从而实现真正的"界面内"局域探测；也可拓展至三组分 LHS（如 MoSe2–WSe2–MoS2）或更复杂的周期性 lateral superlattice，用于设计 chirality 可编程光电流器件。
- 与其它对称性破缺策略（扭转角、应变、垂直堆垛）的 CPGE benchmark（Table 1 / Fig. S16）显示 LHS 的 CPC 极化率约 37%，仍低于应变/扭转角等机制；如何通过栅压、磁场、介电环境工程进一步放大界面 BCD，是走向实用 valleytronic 器件的关键开放问题。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：横向异质结 1D 界面的实空间 Berry 曲率梯度 CPGE 光电流谱学

**原理**：以 one-pot 边缘外延 CVD 生长原子级锐利 MoSe2–WSe2 横向异质结（LHS），源漏电极横跨 1D 界面做法向入射光电流测量：界面诱导的非均匀 Berry 曲率分布产生有限 Berry 曲率偶极子（BCD），使本征圆光电流效应（CPGE）在零栅压零偏压下即可观测（区别于斜入射的光子拖曳 CPDE）；偏振依赖光电流用 I_PC(θ)=C·sin2θ+L1·sin4θ+L2·cos4θ+D 拟合分解 CPGE/LPGE/LPDE 系数；massive Dirac fermion 框架推导 CPGE 电流正比于实空间 Berry 曲率梯度 ∂Ω(k,x)/∂x。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 样品与器件 | CVD 单层 MoSe2–WSe2 LHS（水辅助边缘外延，HAADF-STEM 确认 1D 界面原子级锐利）；hBN 封装 + 石墨烯接触 + FLG 背栅 FET；电极 Cr(5 nm)/Au(70 nm) | 研究方法 |
| 光学测量 | 4 K（AttoLIQUID1000）；NA=0.82、636 nm 聚焦 ~400 nm 光斑（近 MoSe2 B 激子共振）；287 Hz 斩波 + SR830 锁相（增益 10⁶、电流灵敏度 5 nA）；半波片/四分之一波片 + ANR240 piezo rotator 自动偏振控制 | 研究方法 |
| CPGE 定量 | 1/4 波片下 CPGE 相对权重 |C/(C+L1+L2)| 从 15% 提升到 66%（~3 倍增强）；CPC 极化率 37%（MoSe2）/30%（界面）/16%（WSe2）；C 极性在 MoSe2 与 WSe2 之间反转（相反 Ising SOC → 相反 Berry 曲率极性）；FOM=C/L2 在 MoSe2 域最大 ~2.5；532 nm 离共振激发 CPGE 显著减弱 | 主要发现 |
| 理论 | 自旋型 Berry 曲率 Ω_spin ≫ Ω_orbital（Δ~1–2 eV ≫ α_R, λ~10–100 meV）；BCD 在 1D 界面处最大；模拟复现 CPGE 极性反转 | 主要发现 |

**适用边界**：理论仅平衡态内禀几何贡献（缺激子共振吸收效率与非平衡分布，MoSe2/WSe2 幅值不对称未定量复现）；界面 valley 混合 vs 内建电场竞争需更精细微观理论；4 K 测量（室温稳定性与 spin-valley 寿命保留未验证）；400 nm 光斑 vs 1D 界面宽度的空间分辨极限；LHS 的 CPC 极化率 37% 仍低于应变/扭转角机制。
**代表作**：MoSe2–WSe2 横向异质结 CPGE（Chakraborty et al.，IIT Kharagpur/RWTH Aachen，本文）；理论上游 Xiao 2012 PRL spin-valley 耦合、Duan 2023 对称性失配界面 BCD。
*方法卡回补 2026-09-28*

## 深度解析

### 研究问题（Research Question）

Gap: 单层 TMD 的圆偏振光电流 (CPC) 通常被镜面对称压制——正常入射下的 CPGE (circular photogalvanic effect, 纯内禀不对称驱动) 实验上难以观测, 已有报道多为斜入射 CPDE (光子拖曳, 外禀). 产生有限 BCD (Berry curvature dipole) 的已有策略 (离轴照明/垂直堆叠失配晶格) 都不是单片内禀方案. Contributions: 在 CVD 生长的 MoSe2-WSe2 单层侧向异质结 (LHS) 上观测到清晰的 CPGE 特征: 正常入射圆偏振光 + 光电晶体管几何 + 非局域光电流探测跨越 1D 异质界面. 机制: 尽管每个畴内局域对称性保持, 两种材料跨越 1D 界面的无缝整合引入全局对称破缺 -> 界面材料不均匀性驱动 Berry 曲率不对称分布 -> 有限 BCD. MoSe2/WSe2/界面三区的 CPGE 幅度与极性各不相同 (揭示相反的自旋-能谷二向色性 + 1D 界面增强的谷混合). 背栅调控演示 CPGE 可调性 (与 BCD 对费米面的敏感度一致). 无需外部门/偏置即可观测有限 CPGE.

### 研究背景（Background）

agent 打 5 分 ('非光驱动') 的判断部分错误——本文是圆偏振光驱动的光电流实验, 光-物质相互作用是核心; 它缺的是'强场/超快'维度. (1) 与课题 D (valley-selective sigma_solid) 的直接接口: 本文演示的界面 BCD 是 Berry 曲率实空间梯度的可测后果——课题 D 的 sigma_solid 分解中 Berry 项 (Omega_c - Omega_v) 在非均匀体系 (界面/moire) 需要加实空间梯度项, 本文提供该修正的实验证据与平台. (2) 与 2609.29226 (vBCD, 10-09 深读) 的同期组合: 一篇是 TRIV 体系的动量空间 vBCD 理论 (T-even 新机制), 一篇是常规 TMD 侧向异质结的实空间 BCD 实验——'Berry 曲率偶极工程'的两个正交方向 (k 空间 vs 实空间), 林赛若写 valley 方向的 concept note 应该把两者并列. (3) RWTH Aachen Stampfer/Beschoten/Waldecker 组: 2D 材料光电输运核心组, LHS 样品质量一流. (4) 圆偏振光电流与林赛 lightwave valleytronics 的物理邻接: CPGE 是圆偏振光的直流极限; 亚周期圆偏振场驱动的瞬态光电流 (lightwave 版 CPGE) 是课题 D 的相邻问题. (5) 局限: 稳态测量 (无时间分辨); BCD 定量提取依赖模型假设; 界面原子结构未直接表征; 1D 界面谷混合的物理 (增强退相干) 对量子应用是双刃剑.

### 研究方法（Methods）

- 1D 界面 BCD 工程: 用侧向异质结的原子级锐利界面作为 Berry 曲率梯度的内禀源——区别于离轴照明 (外禀) 和垂直堆叠 (层间耦合复杂) 的第三条路线.
- 空间+光谱分辨的三区 CPGE 诊断: MoSe2/界面/WSe2 分别激发 + 圆偏振度扫描——把 CPGE 的空间起源 (界面 vs 畴) 和激子共振 (光谱) 同时分辨.
- CPGE vs CPDE 的正常入射判据: 正常入射抑制 CPDE -> 观测的螺旋度依赖性归因于 CPGE——干净的机制分离实验设计.
- 非局域光电流几何: 探测跨越 1D 界面的非局域光电流——对界面处 BCD 的局域生成敏感.

### 主要发现与核心结论（Main Results）

- 1D 界面诱导的实空间 Berry 曲率梯度: MoSe2-WSe2 LHS 的全局对称破缺在界面产生 Berry curvature 的不对称分布 (BCD)——'实空间梯度'编码在自旋-能谷耦合非线性光电流中. 这是不需要任何外加不对称 (斜入射/失配堆叠) 的内禀 BCD 方案.
- 正常入射 CPGE 观测: 抑制了常规面内 CPDE 贡献 (正常入射无拖曳动量), 观测的非零 CPC 与 CPGE 主导机制一致——单层 TMD 体系中此前实验困难的效应.
- 三区对比光电流谱学: 选择激发 MoSe2 畴/界面/WSe2 畴, CPGE 分量 (还有 LPGE/LPDE) 的幅度和极性各异——与激子共振条件/谷选择激发/两材料相反自旋排序/界面 BCD 生成关联.
- 1D 界面增强谷混合: 界面区的 CPGE 响应反映增强的 intervalley 混合——1D 界面是谷退相干的源, 也是 BCD 的源.
- 背栅可调性: CPGE 随静电掺杂 (亚阈值电压) 演化——BCD 对费米面敏感的实验指纹, 器件化的控制旋钮.
- 零偏置/零门限工作: 无外部门和偏置场下仍观测到有限 CPGE——两个谷对比 2D TMD 整合成 LHS 后内禀支持光螺旋度依赖的载流子输运.
- 平台价值: 单层 LHS 成为工程化非线性自旋-能谷光电子学 (valleytronics + optospintronics) 的鲁棒材料平台.

### 潜在研究方向（Future Directions）

- 超快版本 (关键接口): 当前是稳态/准稳态光电流; 泵浦-探测的时间分辨 CPGE 会给出界面 BCD 的建立时间——与光波电子学的亚周期控制衔接.
- 界面 BCD 的非线性光学对应: DC/准 DC 的 BCD 光电流与非线性光学响应 (如 CPGE 型高阶过程) 共享量子几何根源——LHS 平台的 HHG/非线性光谱版本是自然的下一步.
- 材料组合扫描: MoSe2-WSe2 之外的 LHS 组合 (MoS2-WSe2 / MoTe2-WSe2), 界面 BCD 幅度的材料依赖.
- 1D 界面的原子结构关联: 界面原子级结构 (CVD 生长质量) 与谷混合/BCD 幅度的定量关系——材料工程的控制变量.
- 与 moire 平台 (2606.05093) 的对比: 侧向 1D 界面 (本文) vs 扭转 moire (0D 局域化) 是两种不同的对称破缺工程——组合成十字形/网状 LHS 可能产生新拓扑光电流.

### 来源

- [arXiv 2609.14993](https://arxiv.org/abs/2609.14993)
- 导入自 hermes 深度分析（2026-10-13T04:40:04Z）

<!-- linsai-wikilinks -->
## 关联概念

- [[1D Interface-Induced Real-Space Berry Curvature Gradient]]
- [[1D Interface-Induced Real-Space Berry Curvature Gradient Encoded in SpinValley-Coupled Nonlinear Photocurrent in Lateral Heterostructure]]
- [[Berry curvature dipole]]
- [[Berry 曲率]]
- [[Berry曲率]]
- [[MnPS3]]
- [[PLAN]]
- [[general-berry-mnps3-rashba-20260816]]
- [[光波电子学]]
- [[圆二色性]]
- [[层间耦合]]
- [[强场超快]]
- [[强场超快光学]]
- [[强场驱动]]
- [[泵浦探测]]
- [[谷极化]]
- [[量子几何]]
- [[非线性光学]]
<!-- /linsai-wikilinks -->
