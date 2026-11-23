---
title: "2025-2507_14890-probing-the-band-structure-of-the-strongly-correlated-antife"
type: "papers"
created: "2026-09-25T21:47:38Z"
updated: "2026-11-15T15:09:20Z"
tags: []
related: ["Berry 曲率", "MnPS3", "Probing the band structure of the strongly correlated antiferromagnet NiPS3 across its phase transition", "arpes", "dmft", "general-berry-mnps3-rashba-20260816", "强关联体系", "强场驱动", "磁振子-声子耦合", "精确对角化", "量子几何"]
source_raw: "2025-2507.14890-probing-the-band-structure-of-the-strongly-correlated-antife.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-27T01:00:50Z"
merged_from: ["wiki/papers/2507.14890.md"]
---

• # Probing the band structure of the strongly correlated antiferromagnet NiPS3 across its phase transition

  ## 林赛的理解

  这篇工作是首个跨越 Néel 温度（TN ≈ 155 K）对 NiPS3 能带结构进行系统测绘的实验——用 μ-ARPES 加 DFT+U 把"磁序如何改写能带"这个强关联体系的核心问题钉在了实数上。对我最有价值的有三点：其一，它给出了磁致能带位移的定量指纹（~150 meV 的混合 Ni 3d/S 3p 带位移，且可唯一归因于 Ni 3t₂g-S 3p-S 3p-Ni 3t₂g 超交换路径）；其二，价带顶之上那个 DFT+U 完全无法复现的近平坦结构（E − EF ≈ −1.3 eV），是 NiPS3 区别于 MnPS3/FePS3 的"强关联签名"，这直接关系到我们组关心的光激发强关联态、激子-磁耦合的微观起源；其三，它补齐了 TMPS3 三兄弟（Ni/Fe/Mn）的对比拼图，为"同一化学环境下 U_eff 相近（1.2–1.8 eV）但关联强度迥异"这一反常现象提供了能带层面的证据链。这些定量基准（U_eff = 1.6 eV、能隙 1.8 eV、位移 150 meV）可以直接作为我们 MnPS3/Rashba-Berry 课题与 HHG 探测方案的理论参数输入。

  ## 研究问题

  论文要回答的核心问题：**NiPS3 的能带结构如何跨越反铁磁相变（TN ≈ 155 K）？** 具体拆分为三个子问题：

  1. 在 TN 之上与之下，NiPS3 的价带能带结构是否存在可分辨的变化（磁致能带位移），位移多大、发生在什么能量和动量位置？
  2. 通过与 DFT+U 计算对比，能否指认发生位移的能带的元素与轨道特征，并将其与特定的磁交换作用路径（如超交换）关联起来？
  3. NiPS3 中已知的光学强关联特征（如 1.47 eV 处的锐激子峰需多重态精确对角化才能描述）是否在**单粒子能带层面**也留下 DFT+U 无法捕捉的印记——即 NiPS3 是否比 MnPS3、FePS3 "更关联"？

  ## 研究背景

  - **vdW 二维磁体背景**：vdW 型二维铁磁/反铁磁材料可通过磁场、静电栅压、电流脉冲、应变、光、离子插层、邻近效应与莫尔晶格调控，且具有较强的磁电、磁弹、磁光耦合，是自旋电子学、磁光器件和磁传感的候选平台，也为研究 BKT 相变等基础问题提供载体。
  - **TMPS3 家族定位**：TMPS3（TM 为过渡金属）是层内反铁磁半导体，具有过渡金属原子构成的蜂窝层状结构（每个 TM 被共价键合的 (P₂S₆)⁴⁻ 双锥包围），较直接地实现了 Ising、XY、Heisenberg 三类二维磁模型。磁性来源于近邻 TM 间直接交换与经 S、P 原子媒介的间接超交换之间的竞争，由此产生 zigzag、Néel、stripy 三种长程反铁磁序。
  - **NiPS3 的特殊性**：NiPS3 具有显著的自旋-电荷耦合，产生与磁性相关联的自旋关联激子（层依赖特征、偏振特性与磁序关联），1.47 eV 处观测到超锐激子峰；该激子峰只有采用多重态型精确对角化才能被正确描述。其磁相互作用由第三近邻反铁磁交换主导（源于 Ni-S-P-S-Ni 路径上 p-d 轨道 substantial overlap），基态为层内 zigzag 反铁磁序，自旋基本面内沿 zigzag 方向、离面倾斜约 8°。单层中长程磁序很可能被抑制，可能导致 BKT 相变，可用高度各向异性 XXZ 模型描述。
  - **研究缺口**：NiPS3 的磁序已被多种手段探测，但**能带细节从未被跨越 TN 探测**——此前 ARPES 仅在室温（TN 之上）做过。同类工作作者团队已对 MnPS3（Néel 序，TN = 78 K）和 FePS3（zigzag 序，TN = 117 K）建立了"μ-ARPES + DFT+U"的方法学，本工作将该方法移植到 NiPS3 完成三材料对比。

  ## 研究方法

  **样品制备**：
  - 化学气相输运法合成 NiPS₃ 单晶：化学计量比 Ni、红磷、硫粉混合，额外加入 5% 过量硫作输运剂，石英安瓿高真空（~4·10⁻⁵ mbar）封管，双温区炉 740 °C（前驱区）/ 690 °C（产物区）保温一周。
  - 优化剥离工艺：洁净室中用 Scotch 胶带（Nitto ELP BT-150E-KL）将 NiPS₃ 剥离到 Au(5 nm)/Ti(1 nm) 镀层的 Si/SiO₂（氧化层 90 nm）衬底上（370 K 镀膜），剥离前在室温下做温和 O₂ 等离子灰化（功率 50 W，流量 100 sccm，25 s）去除金表面有机物；60 °C 下于等离子清洗后几分钟内完成剥离。金属镀层保证导电，避免低温 ARPES 中的荷电效应。
  - 选定样品区域：15 层厚、横向尺寸 17 × 21 µm²；AFM 显示 rms 粗糙度 0.14 nm、无明显污染。厚度控制至关重要——45 层样品在 90 K 时所有能带整体下移 0.3 eV（荷电效应）。

  **实验表征**：
  - **μ-ARPES / XPS**：在意大利 Elettra 同步辐射 NanoESCA 束线进行，UHV FOCUS NanoESCA 光电子发射电子显微镜（PEEM）k 空间映射模式，背景压力 5·10⁻¹¹ mbar；测量前 200 °C 退火数小时。光斑直径 5–10 µm，总能量分辨率（束线+分析器）50 meV；光子入射角相对表面法线 65°，方位角相对晶体 MΓM 方向偏 5°，p 偏振。费米能级由衬底 Au 膜的 ARPES 标定。温度通过液氦流量调节、Lake Shore DT-670E-BR 硅二极管测量。目前仅采集两个温度点（220 K 与 45 K）。
  - **XPS**（hν = 220 eV，光斑 15 µm）：确认 NiPS₃ 各组分芯能级峰及 S 俄歇峰；变光子能量（hν = 230 eV）将 S 俄歇峰移开以暴露 Ni 3p 峰；可见少量来自衬底的自旋分裂 Au 4f 峰。
  - **Raman**（室温与 77 K）：验证剥离样品的反铁磁相变——三个指纹：① 宽 2-magnon 散射峰（中心 ~530 cm⁻¹）在 TN 之下（77 K）出现、室温消失；② Ni 面内振动峰 P2 劈裂为双峰（磁振子-声子耦合）；③ (P₂S₆)⁴⁻ 双锥面内 E_g 型振动峰 P8 在 TN 之下呈现 Fano 共振线形（声子与 2-magnon 连续谱干涉）。八个主要 Raman 活性声子模式全部观测到，频率与文献吻合。

  **理论计算**：
  - DFT 采用 PBE 泛函 GGA，VASP 实现；PAW 方法描述离子-电子相互作用；平面波截断 550 eV，Γ 中心 Monkhorst-Pack k 点网格 8 × 14 × 8；高斯展宽 0.05 eV；层间 vdW 力用 Grimme D3 修正。
  - PBE+U（Dudarev 方案），3d 轨道的有效 Hubbard 参数 U_eff = U − J（J 固定为 1 eV），通过对比实验数据选定最优 U_eff = 1.6 eV、k_z = 0.1/Å；内势 12.1 eV（由光子能量依赖的 ARPES 数据佐证）。
  - 计算 zigzag（基态）、Néel 及无序顺磁构型（4 × 2 × 3 超胞 + 自旋轨道耦合，随机三维磁矩方向使净磁矩为零，不优化几何结构）；对反铁磁大单胞做能带展开（band unfolding）至原子六角布里渊区。
  - 对照计算：HSE（变 Hartree-Fock 交换比例）、G₀W₀、EVGW₀（以 PBE 为起点），用于检验价带顶之上额外结构的计算不可复现性。
  - 用中子衍射给出的 295 K 与 2 K 晶格参数缩放做 DFT+U 热收缩检验；用电子 Raman 光谱估算热收缩引起的电子态位移。

  ## 主要发现与核心结论

  1. **跨越 TN 的特征能带位移（核心结果）**：在 Γ 点附近，E − EF = −3.7 eV 处出现一条附加近平坦带（仅存在于 TN 之下，220 K 时不出现）；它在 TN 之上整体下移约 150 meV，几乎与 E − EF = −4.15 eV 的带合并。该平带延伸至 |k∥| ≈ 0.15/Å 处与向上色散带汇合；k 空间角平均数据显示 TN 之上为环状（ring）、之下为完整圆盘状（full circle）强度分布。向上色散带在 TN 之下也略微变平缓。

  2. **排除非磁起源**：该位移并非结构相变（中子衍射确认该温区无结构相变）或热收缩所致——电子 Raman 光谱与用 295 K/2 K 晶格参数做的 DFT+U 计算均表明 220 K 至 45 K 间热收缩引起的电子态位移小于 50 meV，远小于观测到的 ~150 meV。

  3. **轨道指认与超交换归因**：DFT+U（Ueﬀ = 1.6 eV, k_z = 0.1/Å）与 ARPES 在低能区（E − EF < −1.5 eV）吻合良好（特征 i–ix 一一对应）。位移带位于 Γ 点带隙交叉结构（iv, vi）的上支（ARPES 中 E − EF = −3.7 eV，DFT+U 中 E − EVBM = −2.2 eV），为混合 Ni 3d/S 3p 特征。电荷密度分析显示该态由 Ni 3t₂g（d_xy, d_xz, d_yz）轨道构成，右链上每个 Ni 3t₂g 轨道的三个瓣与相邻 S 3p 轨道重叠，其中两个 S 3p 轨道构成 Ni-S-P-S-Ni 超交换路径（两个铁磁耦合 Ni 原子之间，经单个 S 3p 轨道的两个瓣连接），第三个 S 3p 为"死端"（dead end），第四个 Ni 3t₂g 瓣不连接（lone lobe）。单侧单 S 轨道的超交换路径意味着反铁磁相互作用——这自然解释了该带在 zigzag 构型中铁磁链形成时能量上移（使该键更不利）。磁构型对比支持此指认：zigzag 构型 Γ 点带隙 ~0.3 eV 宽，Néel 构型增大到 ~0.4 eV，无序磁结构下特征 (iv, vi) 相对 zigzag 上移 ~100 meV。

  4. **DFT+U 无法复现的额外结构（强关联签名）**：ARPES 在价带顶之上观测到一个几乎无色散的肩状结构，E − EF ≈ −1.3 eV，在 TN 上下几乎相同，且与价带顶有相同的光子能量（k_z）依赖。DFT+U 以及 HSE（变 HF 交换比例）、G₀W₀、EVGW₀ 均无法复现该结构（各种方法只引起 Ni 3d PDOS 的位移，不能解释 Ni 相关能带束之上出现额外特征）。作者推测该结构很可能涉及 3d 能级多重态（可能包含配体贡献），将另文讨论。

  5. **与 MnPS3/FePS3 的对比（表 I 数据）**：
     - NiPS₃（本工作）：zigzag（XY 型）序，带隙 1.8 eV，TN = 155 K，Ueﬀ = 1.6 eV；跨越 TN 的位移带为混合 Ni 3d/S 3p 带 + 价带顶之上的额外带。
     - FePS₃：zigzag（Ising 型）序，带隙 1.5 eV，TN = 117 K，Ueﬀ = 1.2 eV；位移带为 S 3p、Fe 3d 与 P 3p 型带。
     - MnPS₃：Néel 序，带隙 2.94 eV，TN = 78 K，Ueﬀ = 1.8 eV；位移带为 Mn 3d 主导带。
     - 三种材料 Ueﬀ 相近（符合过渡金属 3d 能级化学环境相同的预期），但 NiPS₃ 的 ARPES 数据中出现 DFT 无法拟合的特征，而 MnPS₃ 的所有 ARPES 特征均可被 DFT+U 指认（FePS₃ 拟合需将 DFT+U 数据拉伸 7%）。
     - 电子结构差异根源：Mn²⁺ 3d⁵ 按 Hund 规则完全自旋极化；Ni²⁺ 3d⁸ 的 t₂g 能级全满、仅 e_g 能级接近全自旋极化。NiPS₃ 中 E − EMn_F ∈ [−5.5, −2] eV 的所有能带均有强（常为主导）Ni 3d 贡献，而 MnPS₃ 中 Mn 3d_z₂ 主导的两条带（E − EMn_F ∈ [−5, −4] eV）才是跨越 TN 变化最强的带。
     - 对比图中 NiPS₃ 的 ARPES 与 DFT+U 数据相对 E − EF 整体上移 0.4 eV 以与 MnPS₃ 低能带对齐（以 MnPS₃ 费米能级 EMn_F 为能量基准）。

  6. **未观测到 C₃ 对称性破缺**：尽管 zigzag 反铁磁结构破坏 C₃ 对称性，三个不同 ΓM 或 ΓK 方向在误差范围内完全一致；DFT+U 计算显示的对称性破缺不超过实验能量分辨率 50 meV。亦不能排除 1–10 µm 的小磁畴在 5 µm 光电子提取斑内部分重叠。

  7. **荷电效应定量基准**：45 层样品在 90 K 时所有能带整体下移 0.3 eV（荷电伪影），15 层 + 导电 Au/Ti 衬底方案有效抑制了该效应。

  8. 投稿附注（note added in proof）：一篇最新同期工作也给出了 NiPS₃ 的温度依赖 ARPES 数据，揭示出与本工作相似的能带特征，并以 U = 2.0 eV 合理对应。

  ## 潜在研究方向

  1. **近 TN 温度点缺失**：目前仅有 220 K 与 45 K 两个温度点（技术原因），无法追踪能带位移随温度的演化细节（如临界行为、序参量平方关系）。未来实验应补测接近 TN 的温点。
  2. **额外平带（E − EF ≈ −1.3 eV）的微观起源未解**：DFT 全家桶（DFT+U/HSE/GW）均失败，多重态机制（可能含配体贡献）仅停留在推测，需专门工作（作者预告另文讨论）。这是 NiPS₃ 强关联性的直接能带证据，也是最具理论挑战性的问题。
  3. **光学激子与能带结构的统一图像缺失**：1.47 eV 激子峰需多重态精确对角化描述，与本次观测的平带之间是否有关联尚无定论；自旋关联激子的微观起源仍在争论中。
  4. **为何仅观测到这一条位移带**：自旋极化的 3e_g 能级（更高能量处）未出现可分辨变化，作者猜想是 ARPES 选择定则（现有几何对相应能级不敏感）所致，需不同偏振/几何验证。
  5. **C₃ 对称性破缺与磁畴**：单畴尺寸 1–10 µm 与光斑 5 µm 相当，畴重叠可能掩盖本征对称性破缺；需更小光斑或单畴样品验证。
  6. **单层极限**：单层 NiPS₃ 长程磁序很可能被抑制（潜在 BKT 相变），其能带与体材/15 层的差异、以及磁涨落对能带的重整化均未探索。
  7. **方法学依赖**：U_eff 拟合依赖经验比对（且同期工作选 U = 2.0 eV），DFT+U 对关联效应的处理在 NiPS₃ 上系统性失效，需要 DMFT/簇方法等更强关联处理手段检验。
  8. **技术限制**：变温范围、能量分辨率 50 meV、仅两个 k_z 切片等限制了对更精细多体特征（如自旋极化裂分细节）的分辨。

  ## 与林赛研究的关联

  - **HHG / 强场驱动探测**：本文给出的定量能带指纹（Γ 点平带位于 E − EF = −3.7 eV、位移 ~150 meV、带隙 1.8 eV、Ueﬀ = 1.6 eV、内势 12.1 eV）可直接作为我们 HHG 探测 TMPS₃ 磁相变的能带输入参数。磁致 ~150 meV 的带位移意味着强场驱动下的非绝热电子动力学在 TN 两侧应有可分辨差异——这正是"用 HHG 光谱读出反铁磁序参量"方案的能带学基础。15 层 vs 45 层荷电效应（0.3 eV 下移）也提示我们在薄片 HHG 实验中的衬底与厚度设计。
  - **阿秒 / 超快时间分辨**：磁序对单粒子能带的实时改写（本工作为静态图像）正是我们阿秒泵浦-探测方案要捕捉的动态过程——泵浦扰动磁序后，-3.7 eV 平带的上移/下移响应时间就是交换相互作用的动力学时间尺度。
  - **交变磁（altermagnetism）与超交换几何**：本文将位移带唯一归因于 Ni 3t₂g-S 3p-S 3p-Ni 3t₂g 超交换路径的成键图像（单 S 轨道两侧连接 → 反铁磁），并给出 zigzag/Néel/无序三种磁构型下的带隙对比（0.3 eV / 0.4 eV / 上移 ~100 meV）——这套"交换路径-能带响应"的对应关系是我们理解 zigzag 反铁磁体系（含潜在交变磁候选）中动量依赖自旋劈分的模板。
  - **莫尔 / 转角体系**：NiPS₃ 是 vdW 剥离体系，文中提到其磁性与激子可通过邻近效应、莫尔晶格调控——转角 NiPS₃ 或 NiPS₃/石墨烯异质结中，磁致平带与莫尔平带的耦合是天然的多平带强关联平台。
  - **与本组 MnPS₃-Rashba-Berry 课题直接对口**：本课题（general-berry-mnps3-rashba-20260816）正在研究的 MnPS₃ 与本文 NiPS₃ 形成完美对照组——同为 TMPS₃，Mn 3d⁵（半满、完全自旋极化）vs Ni 3d⁸（t₂g 全满、e_g 近极化）的填充差异决定了交换主导能带完全不同（Mn 3d_z₂ 带 vs Ni 3d/S 3p 混合带）。表 I 的 Ueﬀ（Mn 1.8 eV / Ni 1.6 eV）与带隙（2.94 eV / 1.8 eV）数据可直接迁移到我们的 Berry 相位与 Rashba 估计中；而"NiPS₃ 需要超出 DFT+U 的多体处理"这一结论，为我们在 MnPS₃ 中采用类似方法时划出了可靠性边界。
  - **量子几何**：磁致带隙开合（zigzag ~0.3 eV → Néel ~0.4 eV）与平带的存在意味着 NiPS₃ 价带具有显著的量子几何（Berry 曲率/量子度量）分布，可作为强场驱动下 Berry 曲率耦合 HHG 的产生源；其关联修正（DFT 失效部分）恰恰可能是量子几何反常贡献最集中的区域。

  ## 来源
  - 蒸馏自全文（deep-read）


## 合并自「Probing the band structure of the strongly correlated antiferromagnet NiPS3 across its phase transition」

## 阅读笔记

### general-berry-mnps3-rashba-20260816

笔记已写入：/Users/ll/.hermes/profiles/researcher/notes/2507.14890_note.md

---

## 调研主题
**来源**: [arXiv:2507.14890 — Probing the band structure of the strongly correlated antiferromagnet NiPS3 across its phase transition](https://arxiv.org/abs/2507.14890) (Pestka et al., RWTH Aachen / ML4Q; 通讯作者 M. Morgenstern)

### 研究问题（Research Question）
利用微米分辨角分辨光电子能谱（μ-ARPES）测量 NiPS3 在奈尔温度 T_N ≈ 155 K 跨越相变前后的能带位移，定量表征涉及 Ni 3d / S 3p 杂化的价带在磁有序态下的能量变化，并结合 DFT+U 与 MnPS3、FePS3 的横向对比，回答"DFT+U 在 NiPS3 中是否出现系统性失败、是否能据此刻画该体系的强关联本质"。

### 研究背景（Background）
TMPS3（M = Mn, Fe, Ni）层状反铁磁体是研究 2D Ising/XY/Heisenberg 磁性的模型平台；NiPS3 具有 zigzag AFM 基态、显著的自旋-电荷耦合及 ~1.47 eV 自旋相关激子，但其能带此前仅在室温（远高于 T_N）下测量；MnPS3 与 FePS3 的前期工作（Strasdas2023、Pestka2024）已建立 Au 衬底 + 解理薄层抑制充电的实验范式；本工作正是将该方法外推至更具强关联挑战性的 NiPS3。

### 研究方法（Methods）
样品：气相输运 NiPS3 单晶，Nitto 胶带 60 °C 解理至 Au(5 nm)/Ti(1 nm)/SiO2/Si 衬底；用 AFM/Raman（2-磁振子峰、P2 劈裂、P8 Fano 线型）独立确认 AFM 相变。
测量：Elettra NanoESCA μ-ARPES，PEEM k-space 模式，束斑 5–10 μm，能量分辨率 50 meV，p 偏振，65° 入射，T = 45 K 与 220 K 双温度对比，Au 衬底定 E_F。
计算：VASP/PBE+U（Dudarev，J = 1 eV），最优 U_eff = 1.6 eV；4×2×3 顺磁超胞 + 反折叠；HSE、G0W0、EVGW0 辅助验证。

### 主要发现与核心结论（Main Results）
Γ 点附近一条 Ni 3d / S 3p 混合能带在 T < T_N 时由 −3.85 eV 上移约 150 meV 至 −3.7 eV；已排除结构相变与热收缩（均 < 50 meV）的解释。
DFT+U 给出 zigzag Γ 点 gap ~0.3 eV、Néel ~0.4 eV；顺磁相对 zigzag 上移 ~100 meV，与实验定性一致。
电荷密度显示该能带涉及 Ni 3t2g–S 3p–Ni 3t2g 反铁磁超交换路径；zigzag 中一条链形成键合，另一条无重叠，正好解释能带因铁磁链排列而向上位移。
E-E_F ≈ −1.3 eV 处出现 ARPES 肩状特征（无 T 依赖、与 VBM 共享 k_z 色散），在 DFT+U、HSE、G0W0、EVGW0 中均无法重现——作者归因于 NiPS3 3d 多重态/多体效应。
未观测到 zigzag 应有的 C3 对称破缺，DFT+U 预测的破缺也小于实验分辨（50 meV）。

### 潜在研究方向（Future Directions）
T_N 附近的临界 ARPES（当前仅 45 K / 220 K 两点）——补足磁涨落与 CDW 交叉动力学。
−1.3 eV 额外特征需多体对角化、DMFT、GW+BSE 等超越 DFT 的方法，作者预告另文发表。
与时间分辨谱学（tr-ARPES、HHG）联立，可在飞秒尺度追迹磁相变附近的能带动力学，与本课题 MnPS3 强场自旋分裂主线直接衔接。
纳米光斑/spin-resolved ARPES 可进一步检验 C3 破缺与 Ni 3t2g 自旋极化（当前受单畴尺寸 ~1–10 μm 限制）。
与光学/Raman 数据（1.47 eV 激子-磁振子耦合）协同，鉴别"缺失能带"是否与自旋相关激子同源——这关系到 NiPS3 强关联物理的完整图像。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：强关联反铁磁绝缘体 NiPS₃ 带结构的 µ-ARPES 探测（CVT + 优化剥离 + 拉曼三指纹佐证）

**原理**：CVT 生长 NiPS₃（+5% 过量 S 输运剂，740/690 °C 双温区一周）；优化剥离：Scotch 胶带剥到 Au(5 nm)/Ti(1 nm) 导电衬底（370 K 镀膜，防低温 ARPES 荷电），O₂ 等离子灰化（50 W/100 sccm/25 s）去有机物，60 °C 下几分钟内完成剥离——15 层 17×21 µm² 样品（AFM rms 0.14 nm；45 层样品 90 K 荷电整体下移 0.3 eV 的教训）；µ-ARPES/XPS（Elettra NanoESCA PEEM k 映射，5×10⁻¹¹ mbar，光斑 5–10 µm，总分辨 50 meV，220/45 K）；Raman 三指纹证 AFM 相变（2-magnon 峰 ~530 cm⁻¹、P2 劈裂、P8 Fano 共振）。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| CVT 生长 | 化学计量比 + 5% 过量 S；~4×10⁻⁵ mbar 封管；740 °C/690 °C 一周 | §样品制备 |
| µ-ARPES | Elettra NanoESCA；光斑 5–10 µm；分辨 50 meV；65° 入射 p 偏振；220 K/45 K；真空 5×10⁻¹¹ mbar | §实验表征 |
| 荷电教训 | 45 层样品 90 K 全带下移 0.3 eV（荷电效应）→ 15 层 + 导电衬底 | §样品制备 |

**适用边界**：仅两个温度点（220/45 K）；荷电效应的层厚敏感性限制薄样信号；页面提取限方法节（能带结果在正文）。
**代表作**：本文（arXiv:2507.14890）；束线：Elettra NanoESCA
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry 曲率]]
- [[MnPS3]]
- [[Probing the band structure of the strongly correlated antiferromagnet NiPS3 across its phase transition]]
- [[arpes]]
- [[dmft]]
- [[general-berry-mnps3-rashba-20260816]]
- [[强关联体系]]
- [[强场驱动]]
- [[磁振子-声子耦合]]
- [[精确对角化]]
- [[量子几何]]
<!-- /linsai-wikilinks -->
