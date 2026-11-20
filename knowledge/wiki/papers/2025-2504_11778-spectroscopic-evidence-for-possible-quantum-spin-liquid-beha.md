---
title: "2025-2504_11778-spectroscopic-evidence-for-possible-quantum-spin-liquid-beha"
type: "papers"
created: "2026-09-25T19:43:23Z"
updated: "2026-11-15T15:09:21Z"
tags: []
related: ["Mott绝缘体", "Mott转变", "Spectroscopic Evidence for Possible Quantum Spin Liquid Behavior in a Two-Dimensional Mott Insulator", "arpes", "general-moire-strong-field-probe-20260726", "层间耦合", "强场超快", "强场超快探测", "强场驱动", "电荷密度波", "自旋劈裂", "量子几何"]
source_raw: "2025-2504.11778-spectroscopic-evidence-for-possible-quantum-spin-liquid-beha.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-27T01:00:49Z"
merged_from: ["wiki/papers/2504.11778.md"]
---

• # Spectroscopic Evidence for Possible Quantum Spin Liquid Behavior in a Two-Dimensional Mott Insulator：基于 MBE 单层 1T-TaS2 的 ARPES 研究笔记

  ## 林赛的理解

  这是一篇把强关联电子物理推进到真正二维极限的扎实工作。我在意的不是他们"又观测到一个 QSL 候选"，而是方法论：去掉层间耦合之后，CCDW-Mott 耦合被剥离出来、谱学行为反而比体材料更"干净"——平带带宽约 10 meV（体材料约 10 倍大），Mott 隙 0.26 eV，CCDW-Mott 转变温度 353 ± 12 K（体材料 180 K 的两倍），且升降温无滞回，说明体材料的滞回来自堆垛竞争而非本质电子物理。对我们组的意义在于：他们建立了一套"可调控的 2D Mott/QSL 平台"——磁性掺杂可以打开/关闭自旋自由度的通道（Fe 致隙闭合、Na 只致化学势移动），这意味着 spinon-chargon 耦合强度是可以通过表面工程连续调制的。我们的强场超快方案如果能借这个平台，就有了一把可以主动调制 Mott 隙和自旋激发的"旋钮"。

  ## 研究问题

  单层 1T-TaS2（二维三角点阵、无层间耦合）是否具有量子自旋液体（QSL）基态？核心子问题包括：

  1. 剥离到二维极限后，CCDW-Mott 绝缘态是否依然稳定？转变温度与体材料相比如何变化？
  2. ARPES 谱能否观测到电子分数化（spinon-chargon 分离）的谱学指纹——即平带虽无色散但反常展宽、谱权重随动量快速衰减的连续谱？
  3. 磁性掺杂能否通过 itinerant spinon 与杂质的耦合（spinon Kondo cloud）调制 Hubbard 带隙，从而反证自旋自由度的存在？

  ## 研究背景

  - QSL 是量子涨落强到抑制磁有序的纠缠态，其分数化激发（spinon 携自旋不带电、chargon 带电不带自旋）是凝聚态中最奇异的现象之一，但直接观测困难（Balents, Nature 2010 综述）。
  - 在平均场图像下，移走一个电子后空穴态分裂为 spinon 空穴 + holon，二者色散的卷积给出复合谱函数，理论上可被 ARPES 探测——一维反铁磁链中已观测到双支自旋-电荷分离结构（Sr2CuO3、SrCuO2）。
  - 体 1T-TaS2 被认为是 gapless QSL 候选：20 mK 下无长程磁序、核四极共振呈 QSL 动力学行为、热导有有限剩余线性项（Ribak 2017、Klanjšek 2017、Kratochvilova 2017、Murayama 2020）。
  - 体材料在约 180 K 经历一级相变进入公度 CDW（CCDW）态，13 个面内 Ta 原子畸变形成 Star of David（SOD）团簇，构成 (√13×√13) 超结构，SOD 中心 Ta 原子局域一个未成对电子，自然对应 Mott 绝缘体图像；但多种堆垛构型的层间耦合使体材料低温绝缘相的性质长期有争议（Ritschel 2015 等）。
  - 单层极限的意义：去除层间耦合，暴露纯二维 Mott 物理；且理论已提出单层 1T-TaS2 是带 spinon Fermi surface（SFS）的 gapless U(1) QSL 候选（W.-Y. He et al., PRL 2018; W.-Y. He & P.A. Lee, PRB 2023）。此前 STM 已观测到单层 (√13×√13) SOD 超结构（Lin et al., Nano Res. 2020），但其能带结构与温度依赖从未被探索。

  ## 研究方法

  - **样品**：MBE 生长高质量单层 TaS2 薄膜（RHEED 显示尖锐衍射条纹）。Ta 面内三角点阵夹于两层 S 之间形成 1T 层。Ta 4f 芯能级劈裂与 ARPES 带结构均表明样品为 1T/1H 混合相，两相能带不互相干扰，1H 相穿过费米能级的能带可作费米面位置与化学势移动量的参考。
  - **谱学**：同步辐射 ARPES（如 45 eV p 偏振，Γ–M 方向，10 K 基准温度；芯能级扫描用 90 eV），系统温度扫描（10–330 K），能量分布曲线（EDC）的 leading-edge midpoint（LEM）提取能隙，随温度与掺杂演化。
  - **掺杂调控**：表面沉积 Fe（磁性）与 Na（非磁性）原子对比实验，Co 与 Au 掺杂作对照；载流子密度由费米面 Luttinger 面积定出（1H 相费米面主导）。
  - **理论**：DFT 计算带结构（含 PBE 与 van der Waals 修正）；slave rotor 形式下的低能有效模型——U(1) QSL with SFS 平均场哈密顿量，spinon 与 chargon 各有色散，Mott 隙设为 200 meV，DFT 平带带宽用于 holon 色散，spinon hopping 通过匹配 ARPES 连续谱 FWHM 拟合；温度依赖的能隙用半唯象 BCS 平均场方程拟合提取 T_C。

  ## 主要发现与核心结论

  1. **二维 Mott 绝缘态的确立**：10 K 时单层 1T-TaS2 在 Γ 点出现位于约 -0.26 eV 的平带 α，带宽约 10 meV（体材料的约 1/10），谱学能隙 0.26 eV；DFT 预测顶带带宽小于 30 meV，与实验一致。CCDW 折叠产生 α' 带；CDW 折叠的类空穴带 β 随动量增大向平带靠近；Ta 5d 来源的 γ 带在低温下被两个 CDW 能隙（束缚能 0.3 eV 与 0.9 eV）切割；带结构无明显光子能量依赖，证实二维特性。
  2. **CCDW-Mott 转变温度翻倍且无滞回**：LEM 能隙随温度减小但 330 K 仍未完全闭合；能隙平方对温度用 BCS 型平均场方程拟合给出 T_C = 353 ± 12 K，为体材料转变温度（180 K）的两倍，显示二维极限 CCDW-Mott 隙的鲁棒性；升降温能隙无差异，提示体材料的滞回源于堆垛序竞争。随温度升高平带强度大幅减弱，330 K 近乎消失；α 与 α' 带间能隙反而随温度增大——这与常规能带理论预言相反，且与 γ 带上随温度升高的闭合型 CDW 隙机制不同。
  3. **平带的反常谱学特征**：α 带在能量上无色散（约 10 meV），但 Γ 点 EDC 的 FWHM 达约 0.2–0.3 eV（随光子能量而异），为 1.3 eV 束缚能处 1H 带与 1T 带的 2–3 倍；谱权重随动量快速衰减。这些特征既非典型 CDW 体系、也非具有对称性破缺序的 Mott 绝缘体所有。
  4. **电子分数化的谱学证据**：低能有效模型（slave rotor，gapless U(1) QSL with SFS）定性复现了 Γ 点附近宽连续谱与 α–α' 带间谱权重抑制；抑制源于 spinon Fermi surface，其费米波矢位于 α 与 α' 带之间。模型参数：Mott 隙 200 meV，holon hopping 3 meV，spinon hopping 30 meV——后者与比热-温度系数异常大的实验结果自洽，且与 He & Lee（PRB 2023）的建议值一致；温度升高时连续谱在模型与实验中同步展宽。
  5. **磁性掺杂的独特响应**：10 K 下随 Fe 掺杂增加，平带强度降低、CDW 隙闭合，下 Hubbard 带边附近有谱强度填入 Mott 隙内（约 2.5 × 10^14 /cm^2 载流子密度时隙比未掺杂小 15 meV）；Co 掺杂有类似效应。该效应无法用刚性带移动描述（证明低温下并非普通能带绝缘体），解释为磁性杂质与 spinon 耦合（spinon Kondo cloud）吸引 chargon 导致的电荷再分布。未观测到分立共振峰，因共振只在杂质位于 SOD 中心时出现，而 ARPES 空间平均使不同 Fe 位置的谱抹平。
  6. **非磁性掺杂的对照行为**：Na 掺杂使下 Hubbard 带远离费米能级、谱强度增强（与 K 掺杂体 1T-TaS2、Au 掺杂单层 1T-TaSe2 一致）；以约 -1.3 eV 的两个 S 3p 带为化学势移动参考做扣除后，平带位置随 Na 掺杂几乎不变——化学势移动主导非磁性掺杂效应；而 Fe 掺杂使平带移近费米能级，直接指示 QSL 与磁性杂质的强耦合。
  7. **总体结论**：ARPES 证据支持单层 1T-TaS2 存在 QSL 态；低能谱为 spinon-holon 连续谱，可用带 SFS 的 U(1) QSL 电子分数化定性描述；掺杂实验揭示 spin 杂质-spinon-chargon 耦合引起的电荷再分布。工作把自旋-电荷分离从一维反铁磁链拓展到二维体系，推进了二维三角点阵 QSL 物理的理解。

  ## 潜在研究方向

  1. **磁性杂质位置控制**：分立共振峰要求杂质精确位于 SOD 中心，本文因 ARPES 空间平均而未能分辨——需 STM/纳米ARPES 联合或精确位置可控的掺杂（如原子操控）来验证 spinon Kondo 共振。
  2. **QSL 基态的直接判据**：本文证据是谱学一致性论证（连续谱 + 模型拟合），但 gapless U(1) QSL with SFS 与弱 CDW 序的竞争/共存尚未厘清；中子散射、μSR 或极低温热导在单层极限的测量仍是空白。
  3. **30 meV spinon hopping 的微观独立验证**：目前由谱宽拟合得出，比热系数只是旁证；需要更直接的自旋激发谱学（如 RIXS）确认。
  4. **掺杂调控的定量相图**：Fe 致隙闭合的最终归宿（金属化？超导？自旋玻璃？）未探明；载流子密度超过 ~2.5 × 10^14 /cm^2 后的演化值得系统追踪。
  5. **CCDW-Mott 耦合的因果方向**：353 ± 12 K 的转变是 CCDW 驱动 Mott 还是反之，单层极限提供了干净的拆解平台，但本文未深入。
  6. **1T/1H 混合相问题**：混合相虽提供了费米面参考，但也带来不均匀性；纯 1T 相样品的制备是实验瓶颈。

  ## 与林赛研究的关联

  - **强场驱动 + 莫尔体系的天然接口**：单层 1T-TaS2 本身就是 (√13×√13) 莫尔超结构（SOD 团簇），其 Mott 物理完全由莫尔周期势调控——这与我们"莫尔强场探测"课题共享同一材料平台。该工作证明了这个平台的 Mott 隙（0.26 eV）、带宽（约 10 meV）等关键能量尺度在二维极限的精确取值，正是设计强场驱动方案所需的输入参数。
  - **HHG/阿秒视角的可用旋钮**：本文最重要的启发是掺杂自由度——Fe（磁性，耦合自旋通道，致隙闭合 15 meV）vs Na（非磁性，仅化学势移动）。这意味着 spinon-chargon 通道可以被外部手段选择性开关；我们的强场超快方案可借鉴此思路：用强场阿秒脉冲泵浦 Mott 隙（0.26 eV，对应约 4.8 μm 中红外光子量级），观测 CCDW-Mott 态的超快退相干与可能的光致分数化激发弛豫通道。
  - **能量尺度对接强场物理**：平带约 10 meV 带宽、Mott 隙 200–260 meV、spinon hopping 30 meV——这些 meV 级能量完全落在强场驱动可及的非微扰区间（Keldysh 参数可控），适合检验强场下 Mott 体系的绝热-非绝热 crossover；353 ± 12 K 的 CCDW-Mott 转变也提供了一个温度可调的量子临界点供超快探测。
  - **量子几何与交变磁的延伸**：三角点阵 SOD 莫尔结构的平带（带宽 ~10 meV）提示非平庸量子几何（平带+局域轨道）的可能，与我们关注的量子几何效应方向相连；若后续证实 QSL 基态的拓扑序，其自旋激发与交变磁（altermagnetism）类自旋劈裂谱学的比较也值得留意。

  ## 来源
  - 蒸馏自全文（deep-read）


## 合并自「Spectroscopic Evidence for Possible Quantum Spin Liquid Behavior in a Two-Dimensional Mott Insulator」

## 阅读笔记

### general-moire-strong-field-probe-20260726

已获取完整论文内容。注意到这篇论文（2504.11778）实际是关于**单层 1T-TaS2 中量子自旋液体（QSL）行为的 ARPES 谱学证据**——Mott 绝缘体和分数化激发的研究，与"moiré 强场探针"课题存在间接关联（Mott 强关联基态为后续 HHG 探测提供材料平台）。下面按要求生成结构化笔记。

---

# 论文深度笔记

**arXiv ID**: 2504.11778
**题目**: Spectroscopic Evidence for Possible Quantum Spin Liquid Behavior in a Two-Dimensional Mott Insulator
**作者**: Haiyang Chen¹†, Fo-Hong Wang¹†, Qiang Gao¹, Xue-Jian Gao², Zhenhua Chen³, Yaobo Huang³, Kam Tuen Law², Xiao Yan Xu¹⁴#, Peng Chen¹#
**单位**: ¹上海交通大学 物理与天文学院；²香港科技大学 物理系；³上海光源 上海高等研究院；⁴合肥国家实验室
†共同一作；通讯: xiaoyanxu@sjtu.edu.cn; pchen229@sjtu.edu.cn

---

## 研究问题（Research Question）

本论文的核心研究问题是：**单层 1T-TaS₂ 是否是真正的二维 Mott 绝缘体并展现出量子自旋液体（QSL）行为——即电子自旋与电荷能否发生分数化分离，形成独立的自旋子（spinon）和电荷子（holon/chargon）准粒子激发？** 具体而言，作者聚焦于三个层次的科学问题：第一，单层极限下 1T-TaS₂ 的基态到底是 band insulator 还是 Mott insulator？第二，如果属于 Mott 绝缘体，其低能激发是否携带自旋-电荷分离的"光谱连续谱"指纹？第三，磁性 vs 非磁性表面掺杂对低能激发的差异化响应，能否作为自旋子费米面（spinon Fermi surface, SFS）存在的关键判据？研究的目标是通过 ARPES 直接观测单层 1T-TaS₂ 在 Γ 点附近的扁平带（α 带）宽度异常、谱权重衰减以及掺杂响应，揭示二维三角晶格上分数化电子激发与 SFS 存在的可能性。

## 研究背景（Background）

1T-TaS₂ 自 1970 年代以来就是强关联电子体系的研究范式，体材料在 ~180 K 经历一级相变进入公度电荷密度波（CCDW）状态，十三个平面 Ta 原子畸变形成"Star of David"（SOD）簇，构成 (√13×√13) 超结构，每个 SOD 中心留下一个未配对电子，从而天然成为半填 Hubbard 模型的候选。1T-TaS₂ 同时被理论预言为无能隙 U(1) 量子自旋液体候选——核四极共振（NQR）显示 20 mK 以下仍无长程磁有序，热导率给出有限残余线性项，比热系数异常大。然而，体材料中复杂的层间耦合与堆垛序竞争使其低温绝缘相的本质长期存有争议，bulk 系统的相图因此难以厘清；将体系降至单层则可"关闭"层间耦合，提供研究二维三角晶格 Mott 物理和电子关联效应的纯净平台。论文还引入了 ARPES 探测自旋-电荷分离的思路：在 QSL 中光激发空穴会分裂成自旋子空穴和 holon，两支色散的卷积构成连续谱，与传统单一准粒子谱截然不同，这一判据已在 1D 反铁磁链的"双分支结构"中得到验证。本研究将这一思路推向二维 Mott 体系，旨在填补二维 QSL 直接光谱证据的空白，并为强场超快探测（如 HHG 探针）所关心的强关联基态提供清晰的能带结构画像。

## 研究方法（Methods）

1. **样品制备**：采用分子束外延（MBE）在衬底上生长高质量单层 1T-TaS₂ 薄膜，反射高能电子衍射（RHEED）确认锐利衍射花样以证明单晶质量；通过扫描隧道显微镜（STM）进一步观察到与体材料一致的 (√13×√13) SOD 型 CDW 超结构。
2. **能带测量手段**：在上海光源使用角分辨光电子能谱（ARPES），光子能量在 21–90 eV 范围，覆盖 ΓM 方向；通过改变光子能量确认1T 相能带无明显 k_z 色散，证实二维本征电子结构；角积分芯能级扫描（Ta 4f、5p）鉴别样品中 1T/1H 混合相比例。
3. **温度依赖测量**：10–330 K 连续变温采集 ΓM 方向能谱，以 Γ 点能量分布曲线（EDC）的"前沿中点"（leading-edge midpoint, LEM）作为能隙指示器，用半唯象 BCS 平均场方程拟合能隙平方 Δ²(T) 的温度依赖，从而提取 CCDW-Mott转变温度 T_C。
4. **表面掺杂对照实验**：分别沉积磁性（Fe、Co）与非磁性（Na、Au）吸附原子作为对照，利用1H 相穿越 Fermi 面的 Luttinger 面积推算面载流子密度，原位跟踪 α 平带结合能、化学势位移（以 S-3p 1.3 eV 带作内标）以及 EDC 强度随掺杂浓度的演化。
5. **理论计算**：第一性原理 DFT给出 1T 相顶带带宽 < 30 meV（与 ARPES 实验值 ~10 meV 比对），并基于 U(1) QSL 的 slave-rotor 平均场哈密顿量，建立低能有效模型，对自旋子（hopping = 30 meV）与 holon（hopping = 3 meV）的卷积谱函数进行了与 ARPES 直接对比的模拟。

## 主要发现与核心结论（Main Results）

1. **二维 Mott 绝缘体的直接证据**：单层 1T-TaS₂ 在 Γ 点附近出现一条几乎无色散的扁平 α 带，结合能约 –0.26 eV，带宽仅约 10 meV（约为体材料的十分之一）；10 K 下谱学能隙约 200 meV（论文摘要值），结合 DFT 预测带宽 < 30 meV，共同确认二维极限下 Coulomb 屏蔽减弱、轨道更局域，从而半填 Hubbard 模型成立，能隙为 Mott 能隙而非简单 band gap。
2. **电子分数化的"光谱指纹"**：α 平带虽然能量上几乎无色散，却在动量空间展现出异常宽的 EDC 半高全宽（FWHM ~0.2–0.3 eV，为1H 相带和 1T 相 1.3 eV 处的 2–3 倍），且谱权重随动量增大快速衰减——这与对称破缺型 Mott/CDW 体系截然不同。U(1) QSL 低能有效模型在 200 meV Mott 能隙、自旋子跃迁 30 meV、holon 跃迁 3 meV 的参数下，能够重现上述"谱学连续谱"特征，定性证明分数化激发的存在。
3. **转变温度提升与无能隙 QSL 特征**：单层 CCDW-Mott 转变温度 T_C = 353 ± 12 K（BCS 拟合），约为体材料 180 K 的两倍；升降循环无明显滞后表明无一级相变特征，与体材料的堆垛序竞争相区分。升温至 330 K 时 α 与 α'（CDW 折叠带）之间的能隙反而扩大，违反传统能带论预言，强烈暗示 α 与 α' 间存在自旋子费米面，谱权重抑制来自 SFS 的费米波矢位于两带之间。
4. **磁性 vs 非磁性掺杂的非对称响应**：Fe 表面掺杂（~2.5×10¹⁴ cm⁻²）使能隙较本征减小 ~15 meV，谱学上显示带边出现"隙内态"填充，归因于巡游自旋子与磁性杂质的 Kondo 耦合以及伴随的电荷重排；Co 掺杂给出类似行为。非磁性 Na 掺杂则使 α 带远离 Fermi 面、谱强度增强，表现为化学势位移主导的常规行为（与 K 掺杂 bulk 1T-TaS₂ 一致），而 S-3p 1.3 eV 处的内标带随掺杂同步移动证实化学势修正的必要性。

## 潜在研究方向（Future Directions）

1. **理论模型的关键参数仍非自洽**：自旋子 30 meV、holon 3 meV 的跃迁参数是手动匹配 ARPES FWHM 后设定的；论文自承"不同跃迁参数会给出迥异的谱形甚至 α 与 α' 边界顺序的翻转"，因此亟需严格微观计算（如 slave-rotor 或 parton 构造在单层极限下的精确求解）来约束参数空间，并排除常规多带/无序展宽对"连续谱"的替代解释。
2. **谱学观测的空间平均问题**：ARPES 给出面平均谱，因而 Fe 掺杂的"共振峰"被不同吸附位点的信号平均所抹平；未来应借助 STM/STS 在单原子尺度上识别 SOD 中心 vs 边缘位置的局域态密度，结合 QPI 探测 SFS 散射信号，以提供更直接的 Kondo 物理证据。
3. **单层样品的稳定性与可调性**：单层 1T-TaS₂ 在 MBE 生长时容易混入 1H 相（论文图 1(d) 显示 Ta 4f 分裂即标志混合相），且超薄样品在大气或低温测量循环中易退化。后续需要原位低温 ARPES 配以真空传递腔，并探索栅压/应变等连续可调手段以替代化学掺杂。
4. **向强场超快探测的延伸**：虽然本工作没有直接涉及 HHG，但单层 1T-TaS₂ 作为"二维强关联基态+QSL 候选"的清晰图像，强烈启发下一步将其作为 HHG/Mott 探针平台：Murakami–Werner 框架预言 Mott 绝缘体中可出现反常温度依赖的 HHG（PRL 129, 157401），将 ARPES 已确认的 ~10 meV 平带、200 meV Mott 能隙作为输入，可定量预测并检验 QSL 态对 HHG 谐波谱、椭圆率依赖及时间延迟的独特印记；这正是"moiré 强场探针"课题在关联绝缘体方向上的逻辑延伸点。

---

**与课题关联性提示**：该论文虽不直接研究"moiré superlattice"，但 1T-TaS₂ 是 2D 强关联 Mott绝缘体的标杆材料，与"moiré 强场探针"课题所关心的"twisted homobilayer/TaS₂ 强场响应"和"通过 HHG 反推 moiré 平带参数"在物理基础上直接呼应——可作为"非 moiré 但提供关联基态基准"的对照文献使用。

<!-- methods-backfill:v1 -->

## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：变温ARPES+LEM能隙分析+slave-rotor低能谱模拟（二维Mott/QSL判据链）

**原理**：用同步辐射ARPES直接测量单层1T-TaS₂的能带结构与温度/掺杂演化，以Γ点EDC前沿中点（LEM）跟踪Mott能隙，用半唯象BCS平均场方程拟合Δ²(T)提取CCDW-Mott转变温度；再以slave-rotor平均场（U(1) QSL带spinon费米面）模型计算spinon-holon卷积谱函数，与ARPES连续谱直接比对，作为电子分数化/自旋-电荷分离的谱学判据。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| ARPES光子能量 | 21–90 eV（p偏振 45 eV 主档，芯能级扫描 90 eV） | 研究方法第2条，深度笔记 Methods 2 |
| 基准测量温度 | 10 K | 研究方法-谱学，笔记 Methods 温度扫描起点 |
| 温度扫描范围 | 10–330 K | 研究方法第3条，笔记 Methods 3 |
| 平带α结合能 | 约 -0.26 eV（Γ点） | 主要发现1 |
| 平带α带宽 | 约 10 meV（体材料的约1/10） | 主要发现1；DFT预测顶带带宽 <30 meV |
| 谱学Mott能隙 | 0.26 eV（10 K）；摘要值约 200 meV | 主要发现1/7 |
| Γ点EDC半高全宽 | 约 0.2–0.3 eV（随光子能量而异，为1H/1T带1.3 eV处的2–3倍） | 主要发现3 |
| CCDW-Mott转变温度 | T_C = 353 ± 12 K（BCS型平均场方程拟合Δ²(T)），体材料约180 K的两倍 | 主要发现2 |
| 低能模型Mott隙 | 200 meV | 研究方法-理论，主要发现4 |
| spinon hopping | 30 meV（匹配ARPES连续谱FWHM拟合，与He & Lee PRB 2023一致） | 主要发现4 |
| holon hopping | 3 meV | 主要发现4 |
| Fe掺杂致隙减小 | 约15 meV（载流子密度 2.5 × 10^14 /cm² 时） | 主要发现5 |
| 化学势参考内标 | S 3p 带，约 -1.3 eV | 研究方法第4条，主要发现6 |

**适用边界**：低能模型中spinon/holon hopping为手动拟合谱宽得出而非微观推导，α–α′带边顺序对参数敏感；ARPES面平均会抹平Fe位点分辨的共振峰，QSL证据为谱学一致性论证而非基态直接判据。
**代表作**：Haiyang Chen, Fo-Hong Wang et al. (Xiao Yan Xu, Peng Chen), 2025, arXiv:2504.11778
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[Mott绝缘体]]
- [[Mott转变]]
- [[Spectroscopic Evidence for Possible Quantum Spin Liquid Behavior in a Two-Dimensional Mott Insulator]]
- [[arpes]]
- [[general-moire-strong-field-probe-20260726]]
- [[层间耦合]]
- [[强场超快]]
- [[强场超快探测]]
- [[强场驱动]]
- [[电荷密度波]]
- [[自旋劈裂]]
- [[量子几何]]
<!-- /linsai-wikilinks -->
