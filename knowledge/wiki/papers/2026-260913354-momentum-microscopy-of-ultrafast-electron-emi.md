---
title: "2026-260913354-momentum-microscopy-of-ultrafast-electron-emi"
type: "papers"
created: "2026-09-26T10:52:20Z"
updated: "2026-11-15T15:09:19Z"
tags: []
related: ["2609.13354", "MnPS3", "Momentum microscopy of ultrafast electron emission from a strongly driven optical nanoantenna", "general-berry-mnps3-rashba-20260816", "光波电子学", "固体HHG", "强场超快", "强场驱动", "拍赫兹电子学"]
source_raw: "2026-2609.13354-momentum-microscopy-of-ultrafast-electron-emission.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
digest_level: "abstract"
updated_at: "2026-10-27T12:48:06Z"
merged_from: ["wiki/papers/2609.13354.md"]
---

• ---
  title: "动量显微术观测强驱动光学纳米天线的超快电子发射"
  type: papers
  created: "2026-09-26T10:51:44Z"
  updated: "2026-09-26T10:51:44Z"
  tags: ["强场物理", "光电子发射", "纳米天线", "光波电子学", "超快光谱"]
  related: ["强场隧穿电离", "纳米局域场增强", "PEEM", "petahertz电子学", "少周期激光"]
  source_raw: "2026-2609.13354-momentum-microscopy-of-ultrafast-electron-emission.md"
  growth_stage: "growing"
  confidence: 0.7
  auto_grown: true
  review_status: "pending"
  ---

  # 动量显微术观测强驱动光学纳米天线的超快电子发射

  ## 林赛的理解

  这篇工作我关心它的真正价值：它把"看清电子从哪来"和"看清电子往哪去"这两件事放进同一台仪器里做了。长期以来强场纳米光发射的研究有个结构性短板——光电子能谱/动量谱给出的是动量空间信息，但没有实空间分辨率，只能做单发射体或均匀阵列；PEEM 有纳米级实空间分辨率，却看不到动量分布。对非均匀纳米结构（真实的器件形态几乎都是非均匀的），你只能二选一。本文首次把 PEEM 和动量显微（k-PEEM）整合到同一台仪器上，用少周期驱动场照射双孔纳米天线（尖端半径 <10 nm），在实空间-动量空间联合维度上分辨了近场中两类电子轨迹：quiver 轨迹表现为定向、角分布更聚焦的发射，subcycle 轨迹则给出更宽的横向动量分布。这个"动量分布宽度 ↔ 轨迹类别"的映射，是我们做纳米几何强场控制时一直想要但没有测量手段支撑的诊断量。

  ## 核心要点

  - **仪器层面创新**：首次在同一仪器内联合 PEEM（实空间分辨）与动量显微（动量分辨），突破"能谱无空间分辨、PEEM 无动量分辨"的二选一困境。
  - **样品**：双孔（double-hole）纳米天线，尖端半径 <10 nm，属强场纳米局域增强的典型几何。
  - **驱动**：少周期（few-cycle）强场激光脉冲。
  - **核心物理发现**：近场中存在两类电子轨迹，动量指纹不同——
    - quiver 轨迹 → 定向、角分布聚焦的发射；
    - subcycle 轨迹 → 更宽的横向动量分布。
  - **对既有认知的修正**：该结果与此前纳米尖端（nanotip）发射体的报道特征不一致。作者把 nanotip 归类为"被超短光场驱动的曲面发射体"这一更大类别中的特例——即 nanotip 的行为不能外推为纳米天线的一般规律。
  - **应用指向**：超快相干电子发射源、petahertz 光波电子学。

  ## 实验/研究关联

  - 与我 NSFC-强场超快课题（方向 lightwave_electronics）直接相关：论文方向标签即归入该项目，属于纳米几何强场光电子控制的测量方法学前沿。
  - 方法学上对我的启示：
    - 纳米尺度强场问题里，**测量维度的联合**（实空间 × 动量空间 × 少周期时间尺度）本身就是科学产出，而非仅仅是工程改良；
    - "轨迹类别 → 动量分布特征"可作为一种诊断语言，用于评估纳米天线的近场形态与发射可控性，未来设计 petahertz 电子源时需要区分目标轨迹类型；
    - 提醒我在引用 nanotip 文献结论时要谨慎——曲面发射体的几何曲率可能是决定发射动量特征的关键变量，双孔天线与尖端的差异本质上是**几何类别**差异而非材料差异。
  - 可迁移的思考框架：把"强场近场轨迹分类"作为分析纳米光发射数据的先验结构，配合动量谱数据做模式识别。

  ## 开放问题

  - 摘要级材料未给出两类轨迹在能量分辨上的定量差异（如截止能量、产额比例），需要读原文补全。
  - quiver/subcycle 轨迹的相对权重如何随驱动场强、脉宽（少周期内 CEP 稳定性）、天线几何参数变化？这决定该方法能否用于可控轨迹选择。
  - 双孔天线的近场增强分布与单尖端、bowtie 等其他几何的对比是否系统做过？"曲面发射体大类"的内部细分（曲率、对称性）还缺乏统一图景。
  - k-PEEM 的时间分辨能力在本文中如何体现（是稳态动量成像还是泵浦-探测）？摘要未说明。
  - 该仪器的通量/计数率限制决定了它能否推广到更弱信号的纳米结构或单分子尺度发射体。

  ## 来源
  - 原始材料：2026-260913354-momentum-microscopy-of-ultrafast-electron-emi.md
  - 蒸馏时间：2026-09-26T10:51:44Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：PEEM + 动量显微联合成像（k-PEEM）分辨纳米天线强场电子轨迹

**原理**：首次在同一仪器内联合实空间分辨（PEEM）与动量空间分辨（动量显微），对少周期强场驱动下的纳米天线电子发射做实空间×动量空间联合成像；按'轨迹类别→动量指纹'区分两类近场电子轨迹——quiver 轨迹给出定向、角分布聚焦的发射，subcycle 轨迹给出更宽的横向动量分布。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 样品 | 双孔（double-hole）纳米天线，尖端半径 <10 nm | 核心要点 |
| 驱动 | 少周期（few-cycle）强场激光脉冲 | 核心要点 |

**适用边界**：摘要级材料，无两类轨迹的能量分辨定量差异（截止能量/产额比例）；k-PEEM 的时间分辨模式（稳态还是泵浦-探测）摘要未说明；轨迹权重随场强、CEP、几何的变化未给出。
**代表作**：双孔纳米天线 k-PEEM（本文，摘要级）。
*方法卡回补 2026-09-28*


## 合并自「Momentum microscopy of ultrafast electron emission from a strongly driven optical nanoantenna」

# Momentum microscopy of ultrafast electron emission from a strongly driven optical nanoantenna

**arXiv**: [2609.13354](https://arxiv.org/abs/2609.13354) | **方向**: 纳米结构强场光发射+PEEM/MM联用

## 深度解析

### 研究问题（Research Question）

Gap: 现有纳米结构强场光发射研究要么靠单纳米尖端的传统光电子谱(没有空间分辨, 仅适用于孤立发射器或均匀阵列), 要么靠 PEEM(实空间)单独看局域发射但缺动量分布. 双孔纳米天线的两种几何(双尖端 vs 单尖端)的'近场拓扑如何决定亚周期 vs quiver 电子发射角'存在争议. Contributions: 首次在同一台 PEEM/MM 仪器里联合测量双孔金纳米天线在 2000 nm 20 fs 强场下的实空间与动量空间光发射, 在 sub-10 nm 顶点上分辨出'quiver 电子主导的方向性发射'与'subcycle 电子主导的横向分布'两条不同的电子轨迹签名; 论证此前 nanotip 上观察到的 subcycle 定向发射其实是更广参数空间的一个特例, 平坦/圆润曲面才是普遍情况.

### 研究背景（Background）

(1) 直接对接林赛课题 C(拍赫兹电子学): 纳米天线强场光发射是拍赫兹电子源的两条主流技术之一, 另一条是双场(激光+THz). 本文用 SWIR 20 fs 200 kHz 在 40 nm Au 单晶孔阵列上的结果与林赛 DFG 项目'近场增强亚周期光发射'有现成接口 — 课题 C 若想从孔/针几何入手, 本文给出了 (r_x, r_y) 相图的整套仿真模板, 可以直接迁移到 W/Si/石墨烯天线. (2) 与课题 B(固体HHG+反演)互补: 课题 B 关注晶体内部 interband+intraband 动力学, 本论文关注金属表面 subcycle 真空电子动力学. 两个尺度通过 Floquet 桥梁(论文末段)耦合, 林赛的 sigma_solid (课题 A) 是固体内的, 这里讨论的是表面外的 simple-man 场, 但二者在切向场分量、几何阈值 (r_y = 3.5 nm 对应课题 A 中 omega-2omega 的某个强度阈值) 上存在结构同构. (3) 与课题 A(action phase 迁移)的几何同构: 论文 Fig. 5(d) 显示 alpha 对 E_NF 的导数在 r_y = 3.5 nm 处翻号 — 这是'几何控制下的相位锁定 vs 解锁'的指纹, 与林赛课题 A 中'特定角度下 sigma_solid 翻号'(ZnO / WSe2 等)的方法学是同一套: 改变一个几何/对称参数, 看可观测物理量的'翻号/过零'. (4) 局限: simple-man 模型忽略 Coulomb repulsion(论文承认只在极低 ~65 e/pulse 时可信), 忽略表面污染(非线性阶数 5.6 vs 7.7 的解释), 忽略量子隧穿势垒细节; 当前只到 40.8 TW/cm2, 没到更高强度, quiver vs 亚周期在高 I_NF 的进一步演化未探明; 2D MM 不含 k_z, 完整 3D 分布尚未测. (5) 社区对接: Vogelsang(Oldenburg)+ Dombi(Wigner)+ Hecht(Wurzburg)是纳米强场光发射的欧陆核心组, 与林赛课题组若要合作纳米天线/PEEM 实验, 是现成接口; Z. Papa 在 ELI ALPS(布达佩斯)是欧洲极端光设施节点, 林赛拍赫兹课题用到的阿秒源 ELI 可对接.

### 研究方法（Methods）

- PEEM+MM 单仪器切换: 不需要两台机器, 改变静电透镜激励就在实空间/动量空间模式间切换, 保留飞行时间能量分辨.
- PEEM 焦点直接测量: 用 PEEM 自带的实空间模式直接测量 SWIR 焦斑大小, 与 FDTD 算出的场增强因子 20 联合得到局部近场强度 I_NF 的实验校准.
- 椭球近场+simple-man 混合模拟: 用解析椭球近场(非 FDTD)作输入, 加 simple-man 电子轨迹积分, 跑大参数扫描; 给椭球 r_x=5 nm + r_y=2.5/10 nm 两组对照.
- 横向近场切向分量分析: 把切向场分量单独抽出, 看它在 apex 附近是把电子拉向中心(圆 apex)还是推出(tip), 用以解释几何依赖的发射角.
- 绝热参数 delta = l_NF / l_q 量化: 把'亚周期 vs quiver'的边界量化成 delta ~ 1, 给实验与模拟一个共享判据.
- SWIR 2000 nm + 200 kHz 重频 + 20 fs: 重频比此前 nanotip 单发 1 kHz 实验高两个数量级, 适合纳米光子学实用化.

### 主要发现与核心结论（Main Results）

- 首次 PEEM + MM 联合强场实验: 单台仪器通过切换静电透镜激励在实空间模式(PEEM, 40 nm 分辨率)与动量空间模式(MM, 6 mA^-1 分辨率)间切换, 配以飞行时间能量分辨. 双孔天线(顶点半径 ~10 nm, 间距 350 nm, 40 nm Au 单晶薄片)在 SWIR 强场下两个顶点同时发射光电子, 实空间图清晰可见.
- 非线性 5.6 介于多光子极限 7.7(基于 Au 功函数 4.8 eV / 0.62 eV 光子)之间, 暗示有表面污染与宽激光谱的低光子通道; 在 ~25 TW/cm2 处有产额 kink, 标志多光子 -> 强场过渡.
- 动量分布随强度演化: 低强度 (12 TW/cm2) 接近各向同性圆斑; 中强度沿 k_x(顶点方向)拉长; 高强度 (40.8 TW/cm2) 在 k_y 方向也出现展宽, 在 k_x = 0 处的横切面出现明显'shoulder'(~k_y = +/- 1 A^-1), 即向两侧被加速的电子.
- 能量分布宽度远小于 10 U_p 截止: 最高强度下能量分布半高宽 ~0.7 U_p(+k_x 方向) 和 ~0.4 U_p(-k_x), U_p = 15.2 eV. 因为 quiver 振幅 l_q = eE/m omega ~ 3.5 nm 接近近场衰减长度 l_NF ~ 3.4 nm, 绝热参数 delta = l_NF/l_q ~ 1, 电子在不到一个光周内被踢出近场, 拿不到全部 U_p, 体现亚周期机制.
- 亚周期 vs quiver 分类: 与 simple-man 模型+椭球近场模拟对比, 沿顶点方向主加速的归 quiver(振幅与近场尺度相当时, 电子在近场内往复多个半周); 沿横向出现的电子归亚周期(被瞬时近场踢出, 沿切向场分量飞离).
- 与 nanotip 实验结果的对比: 此前 nanotaper 文献(Pflaum/Faisal 等)报告亚周期电子沿前向窄锥发射(指向 apex 法线); 本论文观察到亚周期电子反而是大角度分布, 沿横向. 矛盾源于切向场分量方向: 平坦/圆润 apex(r_y > r_x)切向力指向 apex 中心(把 quiver 电子向内拉, 把亚周期向外推), 而 nanotip(r_y < r_x)切向力指外, 产生相反行为.
- 椭球参数空间扫描: 改变 r_y 在 2.5-10 nm 区间 + 改变近场强度, 得到发射角 alpha_final 的二维相图. 三大区域: rescattering(<20 deg) / quiver(17-25 deg) / 亚周期(角度随 r_y 增加而变宽). 在 r_y = 3.5 nm 处, 亚周期电子对近场强度的导数 d alpha/dE_NF 翻号 — 这就是'tip vs 平坦'过渡的几何阈值.
- 结论: '定向发射'是有限参数集(r_y < 3.5 nm 的尖几何)的特殊行为, 实际更普遍的参数区间(r_y > 3.5 nm 的圆润几何)恰恰相反, quiver 更定向, 亚周期发散. 这是对纳米结构强场控制图像的修订.

### 潜在研究方向（Future Directions）

- 三维动量(TOF 完整 E-k_x-k_y): 当前只测 2D (k_x, k_y), 加 TOF 就能看完整 3D 动量空间, 是论文末点名的下一步.
- 空间选择 MM: 在 PEEM 中间像面加虹彩光阑, 仅让选定位置的电子进入 MM, 可做异质纳米结构的空间-动量关联谱学.
- 材料扩展: 当前是 Au 单晶, 换 Ag / Cu / W / 半导体可以看功函数与电子亲和势对 quiver vs 亚周期分布的影响.
- 时间分辨: 引入泵-探测(single-cycle SWIR + 探针)对发射时间分辨到亚周期尺度, 看 quiver 与亚周期电子的时间窗.
- 纳米天线几何设计: r_y = 3.5 nm 是过渡阈值, 工程上可以做'可调曲率'纳米结构(例如用 FIB 不同剂量逐点写 apex 形貌)来筛选单类电子轨迹.
- 耦合到 Floquet 工程: 作者末段点明, 强场光发射的近场拓扑与材料内 Floquet 工程相互影响, 联合分析材料内 Floquet 态 + 材料外光电子是新兴方向.

### 来源

- [arXiv 2609.13354](https://arxiv.org/abs/2609.13354)
- 导入自 hermes 深度分析（2026-09-17T15:00:21Z）


## 阅读笔记

### general-berry-mnps3-rashba-20260816

# Momentum microscopy of ultrafast electron emission from a strongly driven optical nanoantenna

**arXiv ID**: 2609.13354
**作者**: K. Harland, G. Hergert, Z. Papa, X. Wu, L. Hansen, J. Altenburg, K. Meier, A. Klosgen, B. Hecht, J.-S. Huang, P. Dombi, J. Vogelsang (U Oldenburg + ELI ALPS + Leibniz IPHT Jena + U Wurzburg + U Jena + Wigner RCP)
**日期**: 2026-09-11
**方向**: 纳米结构强场光发射+PEEM/MM联用

## 研究问题（Research Question）

Gap: 现有纳米结构强场光发射研究要么靠单纳米尖端的传统光电子谱(没有空间分辨, 仅适用于孤立发射器或均匀阵列), 要么靠 PEEM(实空间)单独看局域发射但缺动量分布. 双孔纳米天线的两种几何(双尖端 vs 单尖端)的'近场拓扑如何决定亚周期 vs quiver 电子发射角'存在争议. Contributions: 首次在同一台 PEEM/MM 仪器里联合测量双孔金纳米天线在 2000 nm 20 fs 强场下的实空间与动量空间光发射, 在 sub-10 nm 顶点上分辨出'quiver 电子主导的方向性发射'与'subcycle 电子主导的横向分布'两条不同的电子轨迹签名; 论证此前 nanotip 上观察到的 subcycle 定向发射其实是更广参数空间的一个特例, 平坦/圆润曲面才是普遍情况.

## 研究背景（Background）

(1) 直接对接林赛课题 C(拍赫兹电子学): 纳米天线强场光发射是拍赫兹电子源的两条主流技术之一, 另一条是双场(激光+THz). 本文用 SWIR 20 fs 200 kHz 在 40 nm Au 单晶孔阵列上的结果与林赛 DFG 项目'近场增强亚周期光发射'有现成接口 — 课题 C 若想从孔/针几何入手, 本文给出了 (r_x, r_y) 相图的整套仿真模板, 可以直接迁移到 W/Si/石墨烯天线. (2) 与课题 B(固体HHG+反演)互补: 课题 B 关注晶体内部 interband+intraband 动力学, 本论文关注金属表面 subcycle 真空电子动力学. 两个尺度通过 Floquet 桥梁(论文末段)耦合, 林赛的 sigma_solid (课题 A) 是固体内的, 这里讨论的是表面外的 simple-man 场, 但二者在切向场分量、几何阈值 (r_y = 3.5 nm 对应课题 A 中 omega-2omega 的某个强度阈值) 上存在结构同构. (3) 与课题 A(action phase 迁移)的几何同构: 论文 Fig. 5(d) 显示 alpha 对 E_NF 的导数在 r_y = 3.5 nm 处翻号 — 这是'几何控制下的相位锁定 vs 解锁'的指纹, 与林赛课题 A 中'特定角度下 sigma_solid 翻号'(ZnO / WSe2 等)的方法学是同一套: 改变一个几何/对称参数, 看可观测物理量的'翻号/过零'. (4) 局限: simple-man 模型忽略 Coulomb repulsion(论文承认只在极低 ~65 e/pulse 时可信), 忽略表面污染(非线性阶数 5.6 vs 7.7 的解释), 忽略量子隧穿势垒细节; 当前只到 40.8 TW/cm2, 没到更高强度, quiver vs 亚周期在高 I_NF 的进一步演化未探明; 2D MM 不含 k_z, 完整 3D 分布尚未测. (5) 社区对接: Vogelsang(Oldenburg)+ Dombi(Wigner)+ Hecht(Wurzburg)是纳米强场光发射的欧陆核心组, 与林赛课题组若要合作纳米天线/PEEM 实验, 是现成接口; Z. Papa 在 ELI ALPS(布达佩斯)是欧洲极端光设施节点, 林赛拍赫兹课题用到的阿秒源 ELI 可对接.

## 研究方法（Methods）

- PEEM+MM 单仪器切换: 不需要两台机器, 改变静电透镜激励就在实空间/动量空间模式间切换, 保留飞行时间能量分辨.
- PEEM 焦点直接测量: 用 PEEM 自带的实空间模式直接测量 SWIR 焦斑大小, 与 FDTD 算出的场增强因子 20 联合得到局部近场强度 I_NF 的实验校准.
- 椭球近场+simple-man 混合模拟: 用解析椭球近场(非 FDTD)作输入, 加 simple-man 电子轨迹积分, 跑大参数扫描; 给椭球 r_x=5 nm + r_y=2.5/10 nm 两组对照.
- 横向近场切向分量分析: 把切向场分量单独抽出, 看它在 apex 附近是把电子拉向中心(圆 apex)还是推出(tip), 用以解释几何依赖的发射角.
- 绝热参数 delta = l_NF / l_q 量化: 把'亚周期 vs quiver'的边界量化成 delta ~ 1, 给实验与模拟一个共享判据.
- SWIR 2000 nm + 200 kHz 重频 + 20 fs: 重频比此前 nanotip 单发 1 kHz 实验高两个数量级, 适合纳米光子学实用化.

## 主要发现与核心结论（Main Results）

- 首次 PEEM + MM 联合强场实验: 单台仪器通过切换静电透镜激励在实空间模式(PEEM, 40 nm 分辨率)与动量空间模式(MM, 6 mA^-1 分辨率)间切换, 配以飞行时间能量分辨. 双孔天线(顶点半径 ~10 nm, 间距 350 nm, 40 nm Au 单晶薄片)在 SWIR 强场下两个顶点同时发射光电子, 实空间图清晰可见.
- 非线性 5.6 介于多光子极限 7.7(基于 Au 功函数 4.8 eV / 0.62 eV 光子)之间, 暗示有表面污染与宽激光谱的低光子通道; 在 ~25 TW/cm2 处有产额 kink, 标志多光子 -> 强场过渡.
- 动量分布随强度演化: 低强度 (12 TW/cm2) 接近各向同性圆斑; 中强度沿 k_x(顶点方向)拉长; 高强度 (40.8 TW/cm2) 在 k_y 方向也出现展宽, 在 k_x = 0 处的横切面出现明显'shoulder'(~k_y = +/- 1 A^-1), 即向两侧被加速的电子.
- 能量分布宽度远小于 10 U_p 截止: 最高强度下能量分布半高宽 ~0.7 U_p(+k_x 方向) 和 ~0.4 U_p(-k_x), U_p = 15.2 eV. 因为 quiver 振幅 l_q = eE/m omega ~ 3.5 nm 接近近场衰减长度 l_NF ~ 3.4 nm, 绝热参数 delta = l_NF/l_q ~ 1, 电子在不到一个光周内被踢出近场, 拿不到全部 U_p, 体现亚周期机制.
- 亚周期 vs quiver 分类: 与 simple-man 模型+椭球近场模拟对比, 沿顶点方向主加速的归 quiver(振幅与近场尺度相当时, 电子在近场内往复多个半周); 沿横向出现的电子归亚周期(被瞬时近场踢出, 沿切向场分量飞离).
- 与 nanotip 实验结果的对比: 此前 nanotaper 文献(Pflaum/Faisal 等)报告亚周期电子沿前向窄锥发射(指向 apex 法线); 本论文观察到亚周期电子反而是大角度分布, 沿横向. 矛盾源于切向场分量方向: 平坦/圆润 apex(r_y > r_x)切向力指向 apex 中心(把 quiver 电子向内拉, 把亚周期向外推), 而 nanotip(r_y < r_x)切向力指外, 产生相反行为.
- 椭球参数空间扫描: 改变 r_y 在 2.5-10 nm 区间 + 改变近场强度, 得到发射角 alpha_final 的二维相图. 三大区域: rescattering(<20 deg) / quiver(17-25 deg) / 亚周期(角度随 r_y 增加而变宽). 在 r_y = 3.5 nm 处, 亚周期电子对近场强度的导数 d alpha/dE_NF 翻号 — 这就是'tip vs 平坦'过渡的几何阈值.
- 结论: '定向发射'是有限参数集(r_y < 3.5 nm 的尖几何)的特殊行为, 实际更普遍的参数区间(r_y > 3.5 nm 的圆润几何)恰恰相反, quiver 更定向, 亚周期发散. 这是对纳米结构强场控制图像的修订.

## 潜在研究方向（Future Directions）

- 三维动量(TOF 完整 E-k_x-k_y): 当前只测 2D (k_x, k_y), 加 TOF 就能看完整 3D 动量空间, 是论文末点名的下一步.
- 空间选择 MM: 在 PEEM 中间像面加虹彩光阑, 仅让选定位置的电子进入 MM, 可做异质纳米结构的空间-动量关联谱学.
- 材料扩展: 当前是 Au 单晶, 换 Ag / Cu / W / 半导体可以看功函数与电子亲和势对 quiver vs 亚周期分布的影响.
- 时间分辨: 引入泵-探测(single-cycle SWIR + 探针)对发射时间分辨到亚周期尺度, 看 quiver 与亚周期电子的时间窗.
- 纳米天线几何设计: r_y = 3.5 nm 是过渡阈值, 工程上可以做'可调曲率'纳米结构(例如用 FIB 不同剂量逐点写 apex 形貌)来筛选单类电子轨迹.
- 耦合到 Floquet 工程: 作者末段点明, 强场光发射的近场拓扑与材料内 Floquet 工程相互影响, 联合分析材料内 Floquet 态 + 材料外光电子是新兴方向.


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：PEEM + MM 单仪器联合成像：纳米天线强场光发射的 quiver/subcycle 轨迹几何相图

**原理**：单台仪器切换静电透镜激励实现实空间（PEEM，40 nm 分辨）与动量空间（MM，6 mA⁻¹ 分辨）模式联合 + 飞行时间能量分辨；双孔金纳米天线在 SWIR 强场下以近场衰减长度与 quiver 振幅之比 δ=l_NF/l_q~1 为判据分类电子轨迹——quiver 电子（近场内往复多半周）沿顶点方向定向发射、subcycle 电子（被瞬时近场踢出）沿切向场分量大角度分布；椭球近场 + simple-man 轨迹积分跑 (r_x, r_y) 相图扫描，发现 r_y=3.5 nm 是发射角对近场强度导数的翻号阈值——'定向发射'仅是尖几何（r_y<r_x）特例，圆润曲面才是普遍情况。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 驱动与样品 | 2000 nm / 20 fs / 200 kHz SWIR；双孔金纳米天线（顶点半径 ~10 nm、间距 350 nm、40 nm Au 单晶）；FDTD 场增强因子 20；非线性阶数 5.6（多光子极限 7.7，Au 功函数 4.8 eV / 0.62 eV 光子）；~25 TW/cm² 处产额 kink 标志多光子→强场过渡 | 研究方法/主要发现 |
| 动量与能量 | 高强度 40.8 TW/cm² 下 k_y 向展宽 + k_x=0 横切面 shoulder（~k_y=±1 Å⁻¹）；能量分布半高宽 ~0.7 U_p（+k_x）/0.4 U_p（−k_x），U_p=15.2 eV（远小于 10 U_p 截止——亚周期机制）；l_q≈3.5 nm、l_NF≈3.4 nm、δ~1 | 主要发现 |
| 几何相图 | 椭球 r_x=5 nm + r_y 2.5–10 nm 扫描：rescattering（<20°）/quiver（17–25°）/subcycle（角度随 r_y 增宽）三区；r_y=3.5 nm 处 dα/dE_NF 翻号（tip vs 平坦过渡阈值）；simple-man 模型仅极低 ~65 e/pulse 可信 | 主要发现 |

**适用边界**：simple-man 模型忽略 Coulomb 斥力与表面污染；未到更高强度（quiver/subcycle 在高 I_NF 的演化未探明）；2D MM 不含 k_z（完整 3D 分布未测）；结论限于 Au 双孔几何（W/Si/半导体待扩展）。注：本页与 2026-260913354-momentum-microscopy-of-ultrafast-electron-emi 为同一论文的重复蒸馏记录，本卡侧重几何相图细节。
**代表作**：PEEM/MM 联合纳米天线强场光发射（Harland et al.，Oldenburg/ELI ALPS/Würzburg 等，本文）；修订 nanotip 文献的'定向发射'外推。
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[2609.13354]]
- [[MnPS3]]
- [[Momentum microscopy of ultrafast electron emission from a strongly driven optical nanoantenna]]
- [[general-berry-mnps3-rashba-20260816]]
- [[光波电子学]]
- [[固体HHG]]
- [[强场超快]]
- [[强场驱动]]
- [[拍赫兹电子学]]
<!-- /linsai-wikilinks -->
