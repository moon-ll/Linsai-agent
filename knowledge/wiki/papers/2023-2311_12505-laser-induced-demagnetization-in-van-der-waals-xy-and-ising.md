---
title: "2023-2311_12505-laser-induced-demagnetization-in-van-der-waals-xy-and-ising"
type: "papers"
created: "2026-09-26T14:12:06Z"
updated: "2026-11-15T15:09:20Z"
tags: []
related: ["Berry 曲率", "Laser-induced Demagnetization in van der Waals XY- and Ising-like Antiferromagnets NiPS3 and FePS3", "MnPS3", "general-berry-mnps3-rashba-20260816", "pump-probe", "固体HHG", "强场超快", "强场驱动", "莫尔超晶格", "量子几何"]
source_raw: "2023-2311.12505-laser-induced-demagnetization-in-van-der-waals-xy-and-ising.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
aliases: ["10.1103/PhysRevMaterials.8.014408"]
digest_level: "fulltext"
updated_at: "2026-09-27T01:00:42Z"
merged_from: ["wiki/papers/2311.12505.md"]
---

• # Laser-induced Demagnetization in van der Waals XY- and Ising-like Antiferromagnets NiPS3 and FePS3（Kuntu et al., 2023）

  ## 林赛的理解

  这是一篇非常扎实、而且直接服务我们 NSFC-强场超快 课题的对照实验工作。NiPS3 和 FePS3 是 MPS3 家族里磁结构最相似的一对——同为 zigzag 反铁磁序、同为绝缘体、自旋-晶格主导退磁（约 5–10 ps 的亚纳秒量级），唯一的本质差异是二维普适类：NiPS3 是 2D XY（β=0.21±0.06），FePS3 是 2D Ising（β=0.10±0.03）。作者用同一个探测量（交换线二色性 exLD）扫温度，干净地证明了"退磁度随温度的演化由序参量的临界行为决定"这一热驱动图像，同时指出只有 FePS3 在 TN 附近出现显著临界慢化（τ2 升到 ~100 ps），根源不是自旋-声子耦合常数不同（两者 gsp 同量级），而是自旋比热在 TN 处有无 λ 峰。这意味着：超快退磁的"快慢"不是材料内禀自旋动力学的直接度量，必须扣除热力学（比热）背景——这对我们解读任何 MPS3 体系的超快磁动力学数据都是必要的清醒剂。

  另外两条对我们有直接工具价值：其一，exLD 探针不依赖 AFM 矢量取向，且文中明确它对铁磁型 Voigt/Kerr 信号在 FePS3 几何下天然免疫（L 垂直面），是探测 zigzag 序的干净通道；其二，NiPS3 的退磁度在 Ep=1.88 eV（局域 d-d 跃迁）出现共振增强，而 FePS3 没有——说明激发通道的选择性可以调谐能量向参与自旋-声子耦合的声子（如剪切模）的注入效率。这正是强场超快操控磁性可借力的"选择性泵浦"思路：泵浦光子能量本身就是调控旋钮，不只是加热功率。

  ## 研究问题

  论文要回答的核心问题：在晶体结构、zigzag 反铁磁序、绝缘体性质都几乎相同的两种范德华硫代磷酸盐 NiPS3（2D XY 普适类）和 FePS3（2D Ising 普适类）中，**激光诱导的超快退磁（AFM 序的部分淬灭）在多大程度上、以何种方式反映磁有序的普适类（universality class）与维度性？**具体分解为三个子问题：

  1. 退磁的"程度"（demagnetization degree，以瞬态 exLD 幅度 Δφd 度量）随温度是否呈现由序参量临界指数 β 决定的临界行为？NiPS3 与 FePS3 是否分别服从 2D XY（β=0.231）与 2D Ising（β=0.125）？
  2. 退磁的"时间"（demagnetization time τ2）在逼近奈尔温度 TN 时是否出现临界慢化（critical slowing down）？慢化是否依赖普适类？
  3. 若两者的退磁时间行为不同，其微观根源是什么——是自旋-声子耦合常数 gsp 不同，还是磁比热（spin specific heat）行为不同？

  ## 研究背景

  - 超快退磁（飞秒激光脉冲后磁有序的淬灭）自 1996 年发现以来，已催生全光磁翻转、超短自旋流、宽带 THz 发射等应用方向。金属中由电子-声子耦合主导，特征时间 <100 fs；绝缘体中由自旋-晶格耦合主导，过程在亚纳秒量级（subnanosecond range）。
  - 退磁过程对磁有序温度附近的临界现象天然敏感，因此**有序类型与维度性**——与电子能带结构、自旋与其他能量/角动量库耦合并——同成为决定退磁动力学的关键变量。
  - 层状范德华磁性材料（MPS3 家族：M = Mn, Fe, Co, Ni）提供了一组绝佳对照体系：晶体结构同族、层间交换弱（准二维），但自旋排列多样；单/双层极限下磁有序可发生剧烈变化，也是检验 Mermin-Wagner 定理及二维磁有序幸存机制的平台。
  - 此前该家族中 MnPS3、FePS3、CoPS3 均有超快退磁时间报道（30 ps、约 10 ps 量级、2 ps），唯独 NiPS3 缺少皮秒尺度数据。且 FePS3 中观测到 TN 附近的慢化，而 NiPS3 的慢化与否、NiPS3 与 FePS3 的直接对照（两者恰好覆盖 XY 与 Ising 两种普适类，且在淬灭轨道角动量上居于 MnPS3 与 CoPS3 之间）从未系统做过。这正是本工作的空白填补点。
  - 值得注意的是，文献 [32] 已报道过 FePS3 体材料的激光退磁，本工作在薄片上重复并扩展了这一结果，同时首次给出 NiPS3 的对照数据。

  ## 研究方法

  **材料与样品**：
  - NiPS3 与 FePS3：单斜晶系 C2/m (#12)，过渡金属离子在 ab 面内呈蜂窝结构；带隙分别为 1.7 eV 与 1.5 eV（由涉及 P 与 S 态的电荷转移跃迁决定），带隙内近红外区有更弱的 M²⁺ d-d 跃迁。
  - TN：NiPS3 为 155 K，FePS3 为 118 K。NiPS3 中磁矩形成铁磁耦合的 zigzag 链，链内 ab 面反铁磁耦合、沿 c 轴相邻层铁磁耦合；FePS3 面内 zigzag 序相同但相邻层反铁磁耦合。NiPS3 可用 2D XY 或 XXZ 模型描述（L 沿 a 轴、略偏离 ab 面），FePS3 为 2D Ising（L 垂直于层面）。
  - 机械剥离制备薄片（氩气手套箱内胶带剥离，转移到 Si/285 nm SiO2 衬底）：NiPS3 侧向尺寸约 80 µm、平均厚度 200 nm；FePS3 约 90 µm、180 nm——厚度大于 50 nm，性质对应体材料。

  **结构/磁性表征（Raman）**：
  - LabRAM HR Evolution 光谱仪，532 nm（2.33 eV）连续激光，入射功率限 0.4 mW，1800 lines/mm 光栅，Leica 50× 物镜（NA=0.55），光斑 2 µm；Linkam THMS600 控温。
  - NiPS3：顺磁相 P1 声子峰 178.3 cm⁻¹，AFM 态下简并 E-like 模劈裂，偏振频率差 Δω ∝ |T−TN|^(2β)，拟合得 β = 0.24±0.04、TN = 155±0.5 K，确认 2D XY 有序。
  - FePS3：顺磁相 98 cm⁻¹ 宽峰，TN 以下出现 87 与 93 cm⁻¹ 两个区折叠（ZF）峰；ZF1 峰（87 cm⁻¹）积分强度在 TN = 118 K 降为零。

  **超快泵浦-探测**：
  - 探测光：PHAROS（Yb:KGW）再生放大器，170 fs、Epr = 1.2 eV、5 kHz；泵浦光：ORPHEUS 光参量放大器，光子能量 Ep = 1.63–1.97 eV，脉宽 σ ≈ 170 fs，泵浦通量 F = 2.5 mJ/cm²，入射角约 5°，光斑约 35 µm；探测光通量 7 mJ/cm²，正入射光斑 11 µm（响应已验证线性）。
  - 穿透深度：NiPS3 泵浦 300 nm、探测 4 µm；FePS3 泵浦 800 nm、探测 7 µm。
  - 温度范围 T = 78–295 K（Linkam HFS600）；测量泵浦诱导的偏振旋转 Δφ 与反射率 ΔR。
  - **核心探针：交换线二色性（exLD）**——对沿 c 轴入射、偏振沿 zigzag 链（a 轴）与垂直链（b 轴）的光吸收/折射之差，源于自旋关联对光学性质的影响；对 zigzag 磁有序敏感且**不依赖 AFM 矢量 L 的取向**（与要求 L 在面内的 Voigt/Kerr 效应不同，后者在 FePS3 薄片几何下应消失）。
  - 数据分析：以 T = 173 K > TN 的曲线作参考扣除温度无关背景；退磁度取 Δtd = 45 ps 处的 Δφd（在绝大多数温度下瞬态 exLD 已饱和，且 45 ps > 3τ2）；动力学用双指数函数 Δφ(Δt,T) = Σᵢ Bᵢ(T)[e^(−Δt/τᵢ)−1] 拟合。

  **理论建模**：
  - 序参量幂律：L ∝ (TN − T)^β（T < TN）；exLD ∝ L²，故 Δφd = D[(TN − (T+ΔTs))^(2β) − (TN − T)^(2β)]（式3），远临界区线性化为 Δφd = −2Dβ(TN − T)^(2β−1)ΔTs(T)（式4），从而 τ2 与自旋加热时间 τs 直接关联。
  - 两温度模型（晶格 Tp、自旋 Ts，忽略电子）：ρCp/μ · dTp/dt = gsp(Ts − Tp) + P(t)；ρCs/μ · dTs/dt = gsp(Tp − Ts)。晶格比热 Cp 用 Debye 函数拟合文献总比热数据得到，磁比热 Cs = C − Cp；吸收功率 P(t) 按薄片近似（d ≈ 200 nm）含吸收系数 α 与吸收率 A = 1 − R（Fresnel 公式）；电子-声子弛豫约 2 ps，快于所测过程故电子库可忽略。

  ## 主要发现与核心结论

  1. **两种材料中均观测到激光诱导的部分退磁**：TN 以下泵浦引起 exLD 瞬态下降，恢复时间超出实验窗口；信号随探测偏振角 φ 变化、φ 旋转 90° 时符号反转、TN 以上消失，且全温区不依赖泵浦偏振——确认为热驱动退磁。NiPS3 上此前无皮秒尺度报道，本工作首次补齐。FePS3 的整体偏振旋转变化比 NiPS3 大一个量级（order of magnitude larger）。

  2. **退磁度呈临界行为，指数匹配各自普适类**：
     - NiPS3：β = 0.21±0.06，与 2D XY 模型值 0.231 及 Raman 测得 0.24±0.04 一致。
     - FePS3：β = 0.10±0.03，与 2D Ising 模型值 0.125 及穆斯堡尔测量值 0.16±0.01 一致。
     - 拟合还需修正实验奈尔温度：因热接触不佳与累积激光加热，TN,exp = TN − ≈13 K，即 NiPS3 为 142 K、FePS3 为 105 K。

  3. **临界慢化只在 FePS3 出现**：
     - FePS3 的慢分量 τ2 在 TN,exp 附近升至 100 ps；NiPS3 的 τ2 仅轻微增长，全温区不超过 15 ps。
     - FePS3 另有快分量 τ1 ≈ 1.5 ps 且不依赖温度——判定其非退磁通道，可能源于光学系数 D（含交换耦合 J）的激光诱导变化：ΔR 也以约 1.5 ps 下降；作者排除了金属型自旋翻转电子-声子散射机制和 CoPS3 式快退磁解释（Fe2+ 虽同样有未淬灭轨道角动量）。

  4. **慢化差异源于磁比热而非耦合常数**：
     - 两温度模型拟合给出的自旋-声子耦合常数同量级：gsp = (3.2±0.8)×10¹⁶ W·m⁻³·K⁻¹（NiPS3）、(1.2±0.4)×10¹⁶ W·m⁻³·K⁻¹（FePS3）。
     - τ2 = τs = Cs/gsp：NiPS3 的 Cs(T) 在 TN 处无明显特征，FePS3 则呈明显 λ 峰，因此只有 FePS3 出现比热发散导致的慢化。
     - 激光诱导的自旋温升很小：NiPS3 中 ΔTs < 20 K，FePS3 中 < 10 K，且在 TN,exp 附近有极小值。

  5. **远离临界区的退磁时间两者相近，且补齐 MPS3 家族全谱**：
     - NiPS3 与 FePS3 在远离 TN 时退磁时间均为约 5–10 ps。
     - 家族对比：MnPS3 约 30 ps、FePS3/NiPS3 约 5–10 ps、CoPS3 约 2 ps——按 Mn–Fe, Ni–Co 递减。该趋势与 TN 高低（NiPS3 最高 155 K，MnPS3 仅 78 K）和磁矩大小均无直接关联；作者推断**未淬灭轨道角动量**（Co 最强、Mn 为零）通过影响自旋-声子耦合决定退磁快慢。

  6. **泵浦光子能量依赖**：
     - NiPS3 的 Δφd 在 Ep = 1.88 eV 出现局域极大，与文献吸收峰吻合（局域 d-d 跃迁），提示从 Ni²⁺ 3d 激发态向参与自旋-声子耦合的声子（如剪切模）存在高效能量耗散通道；测量选定 Ep = 1.88 eV。
     - FePS3 在 Ep = 1.63–1.97 eV 范围无显著光谱依赖（测量取 Ep = 1.97 eV），可能与其更窄的带隙（1.5 vs 1.7 eV）使 d-d 跃迁贡献不突出有关；退磁时间在所测光谱范围内也无可见趋势。

  7. 其他细节数值：NiPS3 薄片约 80 µm、200 nm 厚，FePS3 约 90 µm、180 nm 厚；泵浦 2.5 mJ/cm²、探测 7 mJ/cm²；探测 1.2 eV、170 fs、5 kHz；NiPS3 中 P1 峰 178.3 cm⁻¹、FePS3 ZF1 峰 87 cm⁻¹；FePS3 序恢复时间（文献 [29] 报道）在 TN 附近可达 1000 ps，比 NiPS3 长约两个量级，归因于低层间热导率；TN 以上约 10 K 范围内仍有微弱非零瞬态 exLD 信号，源于短程磁序，模型未涵盖。

  ## 潜在研究方向

  1. **τ1 快分量的微观起源未确定**：是 ΔD（光学系数含交换耦合 J 被声子调制，类比 Y3Fe5O12 的 THz 泵浦实验）还是其他机制，需进一步实验区分。
  2. **短程磁序的贡献**：TN,exp 以上 ~10 K 内模型（式3）无法描述残余信号，需在模型中显式纳入短程序或涨落。
  3. **共振增强机制待深挖**：NiPS3 在 1.88 eV 的 d-d 共振为何能高效驱动退磁（剪切声子的角色）？为何 FePS3 无对应效应？文中明确"require further studies"。
  4. **薄片/单层极限未触及**：本工作样品 180–200 nm，对应体材料行为；磁序已知在 NiPS3 双层、FePS3 单层仍可存活，临界慢化与比热机制在少层极限下是否成立是开放问题。
  5. **轨道角动量-自旋-声子耦合的定量理论**：家族内 Mn→Co 退磁时间趋势（30 ps → 2 ps）目前只有定性推测（轨道角动量未淬灭程度影响 gsp），缺乏第一性原理定量刻画。
  6. 原文到此截断（致谢部分之后未提供），附录 A（线性响应验证、电子-声子弛豫细节）与参考文献表不可见，个别引用编号对应的具体文献未能逐一核对。

  ## 与林赛研究的关联

  - **HHG / 阿秒 / 强场驱动**：MPS3 是我们 general-berry-mnps3-rashba-20260816 课题的核心材料体系。本文证明 NiPS3 在 Ep=1.88 eV 的 d-d 局域跃迁是选择性能量注入通道——强场驱动的固体 HHG 光谱学恰好可以分辨带间电荷转移与局域 d-d 通道的贡献，HHG 强度随泵浦能量/偏振的依赖可与本文的 Δφd(Ep) 曲线交叉验证激发通道归属。
  - **交变磁（altermagnet）/ zigzag 反铁磁探测**：exLD 不依赖 AFM 矢量取向、且天然免疫铁磁型 Voigt/Kerr 背景，是 zigzag（交变磁候选）序的超快零场探针范式；我们的超快读出方案可借鉴其"以 T > TN 参考曲线扣除非磁背景"的数据处理流程。
  - **莫尔 / 二维极限**：NiPS3 磁序可存活至双层，莫尔超晶格调制自旋-晶格耦合后，TN 附近的比热奇点与临界慢化行为（本文核心机制 τ2 = Cs/gsp）可作为莫尔体系磁相变的超快判据。
  - **量子几何 / Berry 相位方向**：退磁时间的家族趋势由轨道角动量经自旋-声子耦合传递，提示 Berry 相位与轨道纹理对自旋翻转通道的控制——这与我们 Rashba/量子几何课题的"几何量调控超快磁动力学"主线直接呼应。
  - **实验设计接口**：170 fs、1.63–1.97 eV 泵浦 + 1.2 eV 探测的通量参数（2.5/7 mJ·cm⁻²）、TN 附近 ~13 K 的表观温漂修正，均可直接迁移为我们 MnPS3 对照实验的标定基准（MnPS3：TN=78 K、无轨道角动量、退磁 30 ps）。

  ## 来源
  - 蒸馏自全文（deep-read）


## 合并自「Laser-induced Demagnetization in van der Waals XY- and Ising-like Antiferromagnets NiPS3 and FePS3」

## 阅读笔记

### general-berry-mnps3-rashba-20260816

已收集到足够信息。论文发表于 *Phys. Rev. Materials* 8, 014408 (2024)。下面生成结构化笔记。

注意：用户将这篇论文（arXiv:2311.12505，课题为 general-berry-mnps3-rashba-20260816）送来阅读。需要明确提示：论文研究对象是 NiPS₃ 与 FePS₃ 的激光致退磁动力学，并非 MnPS₃ 的 Rashba/贝里曲率性质。但 NiPS₃ / FePS₃ 与 MnPS₃ 同属 MPS₃ 家族，方法学与临界行为结论对理解 MnPS₃ 时间分辨谱学有直接借鉴意义。

---

# arXiv:2311.12505 结构化笔记

**论文题目**：Laser-induced Demagnetization in van der Waals *XY*- and Ising-like Antiferromagnets NiPS₃ and FePS₃（范德华 *XY*- 与 Ising-型反铁磁体 NiPS₃ 与 FePS₃ 的激光致退磁）

**作者**：D. V. Kuntu, E. A. Arkhipova, L. A. Shelukhin, F. Mertens, M. A. Prosnikov, I. A. Eliseyev, A. N. Smirnov, V. Yu. Davydov, S. Mañas-Valero, E. Coronado, M. Cinchetti, A. M. Kalashnikova（共 11 人，俄、德、西班牙合作）

**arXiv**：2311.12505 [cond-mat.mes-hall]（v1: 2023-11-21，v2: 2024-01-31，12 页 6 图）

**发表期刊**：*Phys. Rev. Materials* **8**, 014408 (2024)，DOI: 10.1103/PhysRevMaterials.8.014408

---

## 研究问题（Research Question）

论文的核心问题是：**当具有不同磁各向异性与自旋-轨道耦合强度（即不同维度 universality class）的二维范德华反铁磁体被飞秒激光激发时，其临界行为（demagnetization degree 与 demagnetization time）在 Néel 温度附近如何区别？** 具体而言，作者比较两类 zigzag 反铁磁体：XY-like NiPS₃（S=1，未淬灭轨道矩）与 Ising-like FePS₃（S=2，强单离子各向异性），追问：(i) 退磁幅值对温度的临界指数是否符合各自 universality class 的预言？(ii) Néel 温度附近的临界减速（critical slowing down）是否普遍存在？(iii) 决定两类材料退磁时间差异的微观耦合机制是 spin-orbit coupling 还是 spin-lattice coupling？

## 研究背景（Background）

MPS₃（M=Mn, Fe, Co, Ni）家族是研究 2D 磁性的范德华基准体系，其中 MnPS₃ 为 Heisenberg 型、CoPS₃ 为 XXZ 型、FePS₃ 为 Ising 型、NiPS₃ 为 XY 型，本工作集中研究后两者。激光致超快退磁在金属中由 electron-phonon coupling 主导（< 100 fs），在绝缘体中由 spin-lattice coupling 主导（皮秒至亚纳秒），因此介磁 van der Waals 体系是研究自旋-晶格耦合动力学的理想平台。NiPS₃ 与 FePS₃ 同为 zigzag 反铁磁体且以自旋磁矩为主，但轨道矩淬灭程度居中（介于 Mn²⁺ 的 L=0 与 Co²⁺ 的最大未淬灭轨道矩之间），故二者构成对称比较：维度/各向异性类比实验的天然配对。前人工作（Zhang et al., 2021）已证实 FePS₃ 在 Néel 温度附近出现 demagnetization time 显著减缓（> 100 ps），但 NiPS₃ 的皮秒尺度退磁数据此前尚未报道；Khusyainov et al., 2023 报道 CoPS₃ 出现 1–5 ps 快退磁并将其归因于 Fe/Co 中未淬灭轨道矩与强 SOC。本研究正是填补 NiPS₃ 在皮秒尺度的实验空白并澄清"未淬灭轨道矩是否必然加速退磁"这一争议。

## 研究方法（Methods）

- **样品制备**：固态反应法生长 NiPS₃ 与 FePS₃ 单晶（合作组 Siskins 2020、Mertens 2022 工艺），手套箱内 Scotch tape 机械剥离至 Si/285 nm SiO₂ 基底；NiPS₃ 厚度 ~200 nm、横向80 μm，FePS₃ 厚度 ~180 nm、横向 90 μm，对应体相行为。
- **静磁表征**：532 nm 激发 LabRAM HR Evolution 共聚焦拉曼系统，对 NiPS₃ 用 P1 模 (178.3 cm⁻¹) 平行/正交偏振分裂得到 β=0.25、T_N=155 K（确认 2D XY普适类 [Vaz 2008]）；对 FePS₃ 用 zone-folding 峰 ZF1 (87 cm⁻¹) 强度归零温度定 T_N=118 K，确认2D Ising 普适类。
- **泵浦-探测 (pump-probe)**：Yb:KGW (PHAROS) 5 kHz、170 fs、1.2 eV 探测；OPA (ORPHEUS) 1.63–1.97 eV 泵浦，泵浦注量 2.5 mJ/cm²。NiPS₃ 泵浦选 1.88 eV（吸收峰位），FePS₃ 用 1.97 eV。Linkam HFS600 控温 78–295 K。
- **探测物理量**：time-resolved exchange linear dichroism (exLD)——一种沿 /⊥ 锯齿链方向偏振光反射偏振面旋转；只敏感于 zigzag 序参量而不敏感于反铁磁矢量 L 的朝向，因此适用于两种材料。
- **数值建模**：双温度模型（two-temperature model, Anisimov 1974）耦合晶格与自旋两热库，含电子-声子（~2 ps 快速平衡）→ 声子-自旋耦合；磁比热 C_M(T) 由 Siskins 2020 的总比热减去 Debye 拟合得到，作为温度依赖输入；光吸收按 Fresnel 公式从复折射率计算，吸收长度 NiPS₃ 4 μm、FePS₃ 7 μm；泵浦激光功率密度由 Walowski 公式（2012）估算。
- **数据分析**：双指数衰减 Δθ(τ) = A₁ exp(-t/τ₁) + A₂ exp(-t/τ₂) 拟合；exLD 振幅 ∝ L²，由 Landau 理论导出 Δ(exLD) ∝ (T_N - T)^(2β)·(ΔT_spin) 线性近似。

## 主要发现与核心结论（Main Results）

- **T_N 确认**：拉曼独立定 T_N(NiPS₃) = 155 K (β=0.25，2D XY)，T_N(FePS₃) = 118 K；与体相文献一致。
- **退磁幅值临界行为**：两种材料 ΔexLD 均在 T_N 之下接近 T_N 时出现峰值，符合 Landau 理论 L ∝ (T_N - T)^β预言的临界发散；NiPS₃ 拟合给出 β ≈ 0.25（XY 普适类），FePS₃ 给出对应 Ising 普适类的临界指数——这说明"退磁幅值由静态 order parameter 临界行为决定"。
- **退磁时间关键差异（核心发现）**：FePS₃ 的 τ_demag 在 T_N 附近显著上升至 ~100 ps（critical slowing down 明显）；而 NiPS₃ 的 τ_demag 始终在 5–15 ps 之间、随温度变化微弱，**未出现显著临界减速**。
- **跨家族比较**：除慢化区外，NiPS₃ 与 FePS₃ 的 τ_demag 均落在 **5–10 ps** 区间；比 Khusyainov 2023 报道的 CoPS₃（1–5 ps）更长、远短于 MnPS₃ 此前报道值（>> 10 ps）。
- **机制解释**：双温度模型成功复现两材料 τ_demag差异。NiPS₃ 与 FePS₃ 的退磁时间都与各自 **spin specific heat C_M(T)** 行为良好相关——C_M 在 T_N 处发散程度决定声子-自旋能量传递所需的"热库大小"，从而调控 τ_demag。NiPS₃ 的 C_M 较弱（XY 类，长程序更接近 Mermin-Wagner 极限），故无显著临界减速。
- **双指数起源**：FePS₃ 中 τ₁(τ_慢) 与 τ₂(τ_快) 行为不同——τ₂ ~3 ps 几乎不随 T 变化，被归因于非磁性光学响应（exLD 之外的部分），不是真正的退磁过程；这与 Khusyainov 2023 在 CoPS₃ 中观察到的 1–5 ps "快速退磁"机制不同（后者源自未淬灭轨道矩 + SOC），故作者排除 SOC 是 FePS₃ 快过程的成因。
- **关键判据**：M²⁺ 离子的**未淬灭轨道矩并非退磁加速的充分条件**；真正决定 τ_demag 的是维度普适类决定的 spin heat capacity 行为及 spin-lattice coupling 强度。

## 潜在研究方向（Future Directions）

- **方法学局限**：双温度模型假设电子-声子耦合 ~2 ps 完成、对 MPS₃ 这一带隙仅 ~1.5–1.7 eV 的绝缘体该假设可能略简化；未显式包含 magnon-phonon 耦合通道。
- **样本局限**：研究仅在 ~180–200 nm 的厚 flakes 上完成，与体相一致；**单层/少层极限下** Mermin-Wagner 效应、维度 crossover 是否改变临界减速行为尚未触及，这是 MnPS₃/NiPS₃/FePS₃ 2D 极限的关键问题，对应课题 MnPS₃ 体系（general-berry-mnps3-rashba-20260816）后续应考察的层数依赖性。
- **未淬灭轨道矩的角色**：本研究排除 SOC 是 FePS₃ 快退磁成因，但**未直接测量轨道矩弛豫通道**——后续可做 element-resolved、时间分辨 XMCD 区分 spin vs orbital动力学。
- **MPS₃ 家族对比**：MnPS₃（课题目标体系）属 Heisenberg 类、退磁更慢，本工作 CoPS₃ 的快退磁与 NiPS₃/FePS₃ 的 5–10 ps 中等退磁提示 MnPS₃ 可能在50 ps–ns 量级；这暗示 MnPS₃ 的 spin-phonon coupling 最弱，**为时间分辨贝里曲率/Berry 曲率读取方案提供更宽的"时间窗口"**——是课题 MnPS₃ Rashba/贝里读取实验设计的关键参考。
- **微观 spin-lattice 通道**：实验未区分直接 phonon-magnon 散射 vs phonon-orbital 散射 vs phonon-lattice-defect 散射路径；未来的 Raman/THz 时域谱可分辨通道权重。
- **未解决问题**：T_N 附近 exLD 临界指数测量误差较大；不同切向应力/堆垛层数是否影响 β 与 τ_demag；NiPS₃ 中是否真无 critical slowing down（实验温度区间 78–295 K 跨越 T_N = 155 K，但低温端接近78 K 仍有残余退磁信号）。

---

**附：来源链接**
- arXiv abstract: https://arxiv.org/abs/2311.12505
- HTML全文: https://arxiv.org/html/2311.12505v2
- 期刊版: https://doi.org/10.1103/PhysRevMaterials.8.014408
- NASA ADS: https://ui.adsabs.harvard.edu/abs/2024PhRvM...8a4408K/abstract


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：exLD 泵浦-探测对比研究 XY/Ising 反铁磁退磁（NiPS₃ vs FePS₃：退磁度临界指数匹配普适类，临界慢化由磁比热 λ 峰决定而非耦合常数）

**原理**：交换线二色性（exLD）作 zigzag 反铁磁序探针：沿 c 轴入射、a/b 偏振吸收差，敏感 zigzag 序且不依赖 AFM 矢量 L 取向（区别于要求 L 在面内的 Voigt/Kerr——后者在 FePS₃ 薄片几何天然消失，exLD 对铁磁背景免疫）；exLD∝L²。对照设计：NiPS₃（2D XY，T_N=155 K）与 FePS₃（2D Ising，T_N=118 K）晶体结构/zigzag 序/绝缘性几乎相同，仅普适类不同。核心发现：① 退磁度 Δφd 随温度呈临界行为，指数匹配各自普适类——NiPS₃ β=0.21±0.06（2D XY 理论 0.231）、FePS₃ β=0.10±0.03（2D Ising 0.125，穆斯堡尔 0.16±0.01）；需修正实验 T_N（热接触不佳+激光累积加热使 T_N,exp=T_N−约 13 K：142 K/105 K）；② 临界慢化只在 FePS₃ 出现（τ₂ 升至约 100 ps；NiPS₃ 全温区 <15 ps）——两温度模型拟合给出 gsp 同量级（NiPS₃ (3.2±0.8)×10¹⁶、FePS₃ (1.2±0.4)×10¹⁶ W·m⁻³K⁻¹），差异根源是磁比热：FePS₃ 的 Cs(T) 在 T_N 有 λ 峰（比热发散致慢化）、NiPS₃ 无特征（τ₂=τs=Cs/gsp）——'退磁快慢必须扣除热力学比热背景才是自旋动力学的度量'；③ FePS₃ 快分量 τ₁≈1.5 ps 温度无关、非退磁通道（可能为光学系数 D 含 J 的激光诱导变化）；④ 远离 T_N 两材料退磁均约 5–10 ps，补齐 MPS₃ 家族谱：MnPS₃ 约 30 ps→Fe/Ni 5-10 ps→CoPS₃ 约 2 ps——与未淬灭轨道角动量（Mn 零→Co 最强）相关但非充分条件；⑤ NiPS₃ 退磁度在 Ep=1.88 eV（局域 d-d 跃迁）共振增强——泵浦光子能量是选择性激发通道旋钮；FePS₃ 1.63–1.97 eV 无光谱依赖。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 样品 | 机械剥离薄片（Ar 手套箱）于 Si/285 nm SiO₂：NiPS₃ 约 80 µm×200 nm、FePS₃ 约 90 µm×180 nm（>50 nm 体材料行为）；带隙 1.7/1.5 eV；T_N 155/118 K | 研究方法·材料与样品 |
| Raman 表征 | 532 nm、0.4 mW、1800 lines/mm、NA=0.55、光斑 2 µm；NiPS₃：P1 峰 178.3 cm⁻¹ 劈裂 Δω∝|T−T_N|^{2β} 得 β=0.24±0.04、T_N=155±0.5 K；FePS₃：ZF1 峰（87 cm⁻¹）积分强度归零定 T_N=118 K | 研究方法·结构/磁性表征（Raman） |
| 泵浦-探测 | Yb:KGW（PHAROS）170 fs、1.2 eV 探测、5 kHz；OPA 泵浦 1.63–1.97 eV、约 170 fs、通量 2.5 mJ/cm²、约 5° 入射、光斑约 35 µm；探测 7 mJ/cm² 正入射 11 µm（线性已验证）；穿透深度：NiPS₃ 泵 300 nm/探 4 µm、FePS₃ 800 nm/7 µm；T=78–295 K | 研究方法·超快泵浦-探测 |
| 分析方法 | exLD 探针（zigzag 序敏感、不依赖 L 取向）；T=173 K>T_N 参考曲线扣背景；退磁度取 Δt=45 ps 处 Δφd；双指数拟合 Δφ=ΣB_i[e^{−Δt/τ_i}−1]；序参量幂律 Δφd=D[(T_N−(T+ΔTs))^{2β}−(T_N−T)^{2β}]；两温度模型（忽略电子，e-ph 约 2 ps 快平衡）：ρC_p/μ·dT_p/dt=gsp(Ts−Tp)+P(t)、ρCs/μ·dTs/dt=gsp(Tp−Ts)；Cp 用 Debye 函数拟文献总比热、Cs=C−Cp | 研究方法·核心探针·数据分析·理论建模 |
| 关键数值 | β：NiPS₃ 0.21±0.06（XY）、FePS₃ 0.10±0.03（Ising）；T_N,exp=T_N−约 13 K（142/105 K）；临界慢化仅 FePS₃（τ₂→100 ps vs NiPS₃ <15 ps）；gsp：3.2±0.8 vs 1.2±0.4×10¹⁶ W m⁻³K⁻¹；远临界区两者均 5-10 ps；FePS₃ τ₁≈1.5 ps 温度无关非退磁；自旋温升 ΔTs<20 K（Ni）/<10 K（Fe）；NiPS₃ 1.88 eV d-d 共振增强 | 主要发现2-6 |

**适用边界**：τ₁ 快分量微观起源未定（ΔD 机制候选）；T_N,exp 以上约 10 K 残余 exLD（短程磁序）模型未涵盖；1.88 eV 共振增强机制（剪切声子角色）与 FePS₃ 无对应效应的原因待研究；180–200 nm 薄片=体材料（单层/少层极限未触及）；轨道角动量-自旋-声子耦合缺第一性原理定量；原文致谢后截断（附录 A 不可见）；两温度模型忽略 magnon-phonon 通道、e-ph 2 ps 假设对 1.5-1.7 eV 带隙绝缘体略简化。
**代表作**：Kuntu et al., Phys. Rev. Materials 8, 014408 (2024), arXiv:2311.12505；Khusyainov 2023（CoPS₃ 2 ps 对照）；Zhang 2021（FePS₃ 慢化前报道）；关联课题 general-berry-mnps3-rashba-20260816
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry 曲率]]
- [[Laser-induced Demagnetization in van der Waals XY- and Ising-like Antiferromagnets NiPS3 and FePS3]]
- [[MnPS3]]
- [[general-berry-mnps3-rashba-20260816]]
- [[pump-probe]]
- [[固体HHG]]
- [[强场超快]]
- [[强场驱动]]
- [[莫尔超晶格]]
- [[量子几何]]
<!-- /linsai-wikilinks -->
