---
title: "2025-2511_01246-local-thermodynamic-dos-measurement-and-twist-angle-mapping"
type: "papers"
created: "2026-09-25T19:56:31Z"
updated: "2026-11-15T15:09:25Z"
tags: []
related: ["5-11", "Local thermodynamic DOS measurement and twist-angle mapping in graphene-hBN superlattices", "general-moire-strong-field-probe-20260726", "强关联体系", "强场超快", "强场驱动", "相位匹配", "莫尔超晶格", "量子几何"]
source_raw: "2025-2511.01246-local-thermodynamic-dos-measurement-and-twist-angle-mapping.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-27T01:00:53Z"
merged_from: ["wiki/papers/2511.01246.md"]
---

• # 局部热力学 DOS 测量与石墨烯-hBN 超晶格的扭转角成像

  ## 林赛的理解

  这篇工作对我们"莫尔体系强场超快探针"方向有几个直接的启发。第一，他们演示了一种完全不依赖输运的、空间分辨的**局域热力学 DOS 测量**——KPFM 通过力学探测访问局域化学势 μ，再由 μ(n) 反演逆压缩率 dμ/dn 与 DOS。这条"化学势 → 热力学 DOS"的技术路线与我组想做的"用强场光探针读取莫尔体系的局域电子结构"在哲学上同构：都是非输运、近零扰动、空间可分辨的电子结构读出手段。第二，他们把局域电子结构测量直接转化成了**扭转角成像**工具——利用 CNP 与空穴侧 SDP 的密度间隔 n_s 反演局域扭转角，并揭示了气泡诱导应变是扭转角不均匀性的主因。这提示我们在做莫尔强场实验时，样品内的局域扭转角/应变涨落可能是掩盖本征角度依赖效应（包括角度依赖的 HHG 响应、量子几何贡献）的关键混淆变量，必须像他们一样建立局域表征能力。第三，μ₀/n₀ 双偏移量图可以**分辨气泡位于哪个界面**（底 hBN-石墨烯界面 vs 石墨-底 hBN 界面），这种"纵向分层诊断"思想对理解莫尔器件中的静电环境与掺杂涨落很有参考价值。

  ## 研究问题

  真实莫尔器件中普遍存在扭转角空间不均匀性，块体平均测量（如输运）会把不同局域扭转角区域的信号平均掉，掩盖角度依赖的本征电子学效应。论文要回答的核心问题是：**能否用扫描探针以非侵入方式、空间分辨地测量莫尔体系的局域热力学 DOS，并据此重建局域扭转角空间分布，进而理解不均匀性的结构起源（气泡/应变）？** 具体目标包括：

  1. 用 KPFM 直接访问局域化学势 μ，并由 μ(n) 提取逆压缩率 dμ/dn 与局域热力学 DOS；
  2. 利用 DOS 中 CNP 与第二狄拉克点（SDP）的特征重建器件上的局域扭转角成像；
  3. 识别扭转角调制与气泡诱导应变的关系，并通过 μ₀/n₀ 偏移判定气泡所在界面。

  ## 研究背景

  - vdW 晶体堆叠时相邻层间微小的晶格失配或转角产生莫尔超晶格，这一长波周期势可显著重构低能电子能带（Bistritzer-MacDonald 连续模型），催生了魔角石墨烯超导、拓扑相等关联/拓扑现象，以及莫尔光子学与光电子器件提案。
  - 但器件间的电子学行为差异大、可重复性差，根源是堆叠构型的亚稳性——晶格弛豫导致显著的**扭转角不均匀性**（如 Uri 等用扫描 SQUID 在魔角石墨烯中成像、Yoo 等在扭转双层石墨烯中观察原子与电子重构）。
  - 现有局域探针（单电子晶体管、电容式静电计）需金属岛/量子点作为电荷传感器，会引入额外静电耦合；KPFM 的力学探测原理天然规避此问题，可无扰动地访问真正热力学性质，同时保持空间选择性。
  - 前人输运测量（Yankowitz 2012、Hunt 2013、Yu 2014）已见石墨烯-hBN 超晶格中的超晶格调制（SDP、Hofstadter 态），但块体平均掩盖了局域角度涨落。

  ## 研究方法

  - **技术平台**：自建低温（14 K 测量温度）Kelvin 探针力显微镜（KPFM）；针尖、石墨烯层、背栅同时施加 DC 偏压与小 AC 电压，悬臂梁经激光干涉监测；在调制频率 f_e 处找静电力归零的偏压 V_tip 即得针尖与石墨烯的接触电势差（CPD），从而直接访问化学势 μ。
  - **逆压缩率测量**：扫背栅电压 V_BG 测 μ(n)。最高灵敏档在背栅上叠加 AC 调制 V_m sin(ω_m t)，直接测得 dμ/dn，无需数值求导，显著提升信噪比（代价是峰展宽；0.5 V、1 V、2 V_RMS 调制对应载流子密度窗口约 0.58、1.15、1.73 ×10¹² cm⁻²，可做灵敏度-分辨率权衡，AC 模式灵敏度取向、DC 模式分辨率取向）。
  - **器件**：hBN 封装石墨烯/hBN 异质结（目标 0° 对齐），置于石墨背栅上。五步法逐层组装（PDMS 转移、PC 辅助拾取与玻璃化释放、NMP 除胶、IPA 清洗、300 °C 退火 ~10 min）。hBN/石墨、石墨/Ti-Au（5 nm/70 nm）电极结构。
  - **定标**：4 K 磁输运测 Landau fan（CNP 位于 V_BG ≈ -2 V，填充因子 ±2、±6、±10），得栅压-密度转换因子 dn/dV_BG = 0.408 ×10¹² cm⁻²V⁻¹，与几何电容一致。
  - **偏移扣除**：局域静电环境引入 n₀、μ₀ 偏移，以 CNP 处（n ≈ -1 ×10¹² cm⁻²）的 μ、n 为参考点重定义 n_G = n - n₀、μ_G = μ - μ₀。
  - **理论对照**：Bistritzer-MacDonald 连续模型在莫尔布里渊区对角化哈密顿量，得 CNP 与空穴侧 SDP 处的能隙、DOS(E)、n(E)，并对 DOS 施加 1/10 满填充密度窗口的展宽以模拟实验（对应主文 Fig. 2(d) 灰/红曲线）。
  - **输运表征**：4 K 双探针电阻 vs 载流子密度，CNP 主峰 + 电子/空穴两侧卫星峰；由满填充莫尔微带所需载流子密度估计器件平均扭转角 ~0.56°。

  ## 主要发现与核心结论

  1. **局域热力学 DOS 成功提取**：μ_G(n_G) 单调上升但斜率有明显变化；dμ_G/dn_G 在 CNP（蓝虚线）与满填充对应的卫星位置（绿虚线，对称分布于 CNP 两侧）出现显著峰，对应莫尔微带形成导致的 DOS 耗尽。AC 调制法比数值求导法信噪比显著更高（伴轻微展宽）。
  2. **测得 DOS 与连续模型计算定性一致**（P1 点与 ~100 nm 外 P2 点）：
     - E=0（CNP）与 SDP 处 DOS 抑制；
     - SDP 附近出现显著范霍夫奇点（vHS）峰（青色箭头标记，空穴侧）。
  3. **电子-空穴不对称**：电子侧与空穴侧 SDP 能量位置明显不同；由 D(E) ∝ |E|/(ħv_F)² 从数据斜率提取 Fermi 速度——相对于本征石墨烯，提取斜率电子侧大 ~1.119 倍、空穴侧大 ~1.158 倍，对应 v_F 压低 ~5.5%（电子侧）与 ~7.1%（空穴侧），与前人测量（25,30）相当；与破缺 C₂y 对称性的子晶格不对称势一致（DaSilva 2015）。
  4. **局域电荷杂质印记**：不同位置测得 DOS 中出现在理想能带无法解释的弱抑制（黑/橙箭头），形状与能量位置随测量位置显著变化，归因于局域电荷杂质。
  5. **一维线扫描扭转角成像**：dμ_G/dn_G 的 CNP 峰与空穴侧 SDP 峰沿扫描轨迹连续移动；密度间隔 n_s 的空间演化直接反映莫尔长度 l_m = a/√(δ²+θ²) 的变化，换算出位置依赖的局域扭转角轮廓，围绕输运平均角 θ_avg 分布，揭示输运测量无法获得的局域信息。
  6. **二维扭转角图与气泡-应变关联**（尺度条 1 μm）：
     - 区域 A、B 呈现明显不同的局域扭转角，对应形貌中的大气泡；A 处扭转角增大、B 处减小，说明气泡诱导应变可双向局域调制扭转角；
     - 粉色箭头处的小气泡对扭转角的影响反而**强于** A、B 处大气泡，推断小气泡紧邻石墨烯界面（很可能在底 hBN-石墨烯界面），大气泡位于更深界面（如石墨-hBN 界面）；
     - **界面判定**：n₀ 图的主特征与大气泡（A、B）强相关（远程电荷掺杂效应），μ₀ 图在大气泡处无特征、仅在小气泡处出峰（直接接触石墨烯改变局域费米能级/功函数差）——据此判定小气泡位于底 hBN/石墨烯界面，大气泡位于石墨背栅/底 hBN 界面。
  7. **总体结论**：电子 DOS 可作为石墨烯-hBN 莫尔器件中扭转角空间不均匀性的可靠指示，实现扭转角空间分布重建；扭转角调制在气泡处显著增强；μ/n 双偏移量联合分析可判定气泡纵向位置，为莫尔体系的应变分辨研究提供实用工具。

  ## 潜在研究方向

  - **非相互作用近似**：提取热力学 DOS 时假设化学势等于单粒子能量，相互作用/关联修正未纳入（强关联莫尔体系中该近似可能失效）。
  - **AC 调制分辨率代价**：灵敏度提升以谱线展宽（~1/10 满填充密度窗口）为代价，窄能隙/近简并特征可能被抹平；DC 模式信噪比受限。
  - **界面判定的间接性**：μ₀/n₀ 区分界面依赖"是否直接接触石墨烯"的定性判据，缺乏气泡深度/应变的定量模型与交叉验证（如 AFM 力学谱、STEM）。
  - **应变机制未定量建模**：气泡-扭转角耦合仅用莫尔长度几何关系 l_m = a/√(δ²+θ²) 定性关联，气泡尺寸、深度与局域应变张量/扭转角偏移之间的定量映射缺失。
  - **温度与能量分辨极限**：测量在 14 K，CNP/SDP 能隙与 vHS 分辨受温度与调制展宽限制；更低温下 Hofstadter 态与关联能隙的局域成像未做。
  - **适用体系范围**：仅在近对齐（~0.56°）石墨烯-hBN 单器件上演示；魔角 tBLG、小转角过渡金属硫族化合物等强关联体系中逆压缩率与单粒子 DOS 的关系需重新评估。
  - **时间维度缺失**：静态成像，无法追踪扭转角弛豫/气泡演化的动力学过程。

  ## 与林赛研究的关联

  - **莫尔强场探针方向（general-moire-strong-field-probe-20260726）**：本文给出"局域扭转角成像"这一关键实验前道能力。我们关心的角度依赖强场响应（如转角调制的 HHG 产率、SDP/vHS 能量处的共振增强、弗洛凯工程）在存在扭转角不均匀的真实器件中会被空间平均——本文证明 DOS 反演可绘制局域 θ 图，可作为强场光学实验前的样品局域表征与事后数据分选（按局域 θ 分 bin）工具。
  - **热力学 DOS 读出与强场读出互补**：dμ/dn 与我们的 HHG/瞬态吸收同属"非输运电子结构探针"，前者给静态热力学 DOS 及其空间分布，后者给动态非平衡响应；二者在同一空间坐标下联合，可把局域 θ、局域 vHS 能量与局域强场响应点对点关联，分离"角度效应"与"应变/掺杂效应"。
  - **量子几何/能带工程接口**：v_F 压低 ~5.5%/7.1% 与电子-空穴不对称直接反映莫尔势对狄拉克锥的重整；量子几何量（贝里曲率、轨道磁矩）在 SDP/vHS 附近的行为会随局域 θ 涨落而变化，本文的局域 DOS 图可为量子几何依赖的强场选择定则分析提供局域能带输入。
  - **应变工程通道**：气泡诱导的局域应变/扭转角调制是莫尔体系中可设计的空间势场；强场驱动下局域应变区可能成为 HHG 相位匹配或热点调控的切入点，本文的 μ₀/n₀ 界面诊断为此类器件设计提供了缺陷定位方法。
  - **方法学借鉴**：偏移扣除思想（以 CNP 为参考对齐 μ_G/n_G）与"灵敏度模式/分辨率模式"双模式权衡，可直接移植到我们的近场光学/光电流扫描平台的信号处理流程中。

  ## 来源
  - 蒸馏自全文（deep-read）


## 合并自「Local thermodynamic DOS measurement and twist-angle mapping in graphene-hBN superlattices」

## 阅读笔记

### general-moire-strong-field-probe-20260726

I now have the full paper content. Let me organize the structured notes per the five dimensions required.

---

# 调研主题：local thermodynamic DOS 与扭转角 mapping — KPFM 用于 graphene-hBN moiré 超晶格

来源：[arXiv:2511.01246 — Local thermodynamic DOS measurement and twist-angle mapping in graphene-hBN superlattices](https://arxiv.org/abs/2511.01246)
- 作者：Namkyung Lee, Hangyeol Park, Seungwon Jung, B.J., N.L., J.J. et al.（v1: 2025-11-03；v2: 2025-11-11）
- 提交领域：cond-mat.mes-hall
- 篇幅：15 页，4 幅主图

## 研究问题（Research Question）
- 核心问题：如何在具有局域扭转角（twist-angle）无序的 graphene-hBN moiré 器件中，**以非扰动、高空间分辨方式同时获得局域热力学态密度（thermodynamic DOS）和扭转角 landscape**，从而超越传统输运测量的体平均限制。
- 具体目标：(1) 验证 cryogenic KPFM（Kelvin probe force microscopy）能否在 ~100 nm 空间尺度下提取 moiré 系统的局域化学势 μ(n) 及其导数 dμ/dn（inverse compressibility）；(2) 将 μ转换为局域 DOS（E）后与连续模型计算对比；(3) 利用 DOS 中 moiré 边带（SDP）填充所对应的载流子密度 Δn，反推局域扭转角 θ(x,y)，构建二维 θ-map；(4) 通过 μ₀ 与 n₀ 偏移图分辨气泡（bubble）位于石墨/hBN 界面还是 hBN/graphene 界面。
- 中心论点：局域 DOS 对扭转角变化敏感，可作为比输运更可靠的 moiré 局域"指纹"，从而把 strain-bubble 工程变成可主动设计的自由度。

## 研究背景（Background）
- Moiré superlattice 通过扭转角工程（graphene/hBN、TBG、twisted TMD）实现 flat band、superconductivity、Chern insulator 等关联与拓扑物相，是过去十年的核心舞台之一；但器件中**实际扭转角并非单值**——pick-up/relaxation 过程中的应变、气泡、局部滑移都会引入 ~0.1° 量级的 spatial disorder，使 bulk transport 的输运信号（如 side peak 位置）成为大面积平均，无法揭示局部应变与电子结构的耦合。
- 现有局域探测手段（SET 单电子晶体管、电容式 electrometry）依赖金属 island 或 QD 作电荷灵敏元件，会引入额外静电耦合，**对系统本身造成扰动**，不适合直接读取热力学量。
- KPFM 走"纯力学"路径——通过测量 tip 与 sample 间 contact potential difference（CPD）反推 μ，并已用于 graphene/2D 体系，但常规 KPFM 灵敏度不足以分辨 moiré 微小能隙与 SDP 填充对应的精细 DOS特征；本文将 cryogenic KPFM + 二次调制（back-gate AC modulation）相结合，实现 dμ/dn 的高 SNR 直接测量。

## 研究方法（Methods）
- **器件制备**：PDMS 干法转移 + PC玻璃化辅助拾取，得到 hBN/graphene/hBN/graphite stack；顶部 hBN 与 graphene 晶轴刻意0° 对齐，目标 moiré 周期；300 °C 退火 10 min 以松弛界面。
- **bulk标定**：两探针输运测量在 4 K 下扫 back-gate，得到主 CNP 峰与 electron/hole 两侧的 moiré side peak，由填充 moiré miniband 所需载流子密度反推**平均扭转角 ~0.56°**（略偏0°），并由 Landau fan 在 ν=±2、±6、±10 处确认填充序列。
- **局域探测**：自建低温 KPFM（cantilever 通过激光干涉仪监控），tip + back-gate 同时加 DC 偏置与小幅 AC 调制（fω的一阶力分量被锁定放大以解析 CPD）；通过 nulling 提取 V_CPD → μ；在 μ vs n 测量中再叠加 back-gate 上的 AC 调制 Vg sin(ωt)，**直接读出 dμ/dn** 而非数值微分，从而显著提升 SNR；权衡是 AC 幅度（0.5/1/2 V，对应 0.58/1.15/1.73 ×10¹² cm⁻² 密度窗口）增大时谱峰会增宽，故可切换 AC/灵敏模式 vs DC/分辨模式。
- **理论参考**：Bistritzer–MacDonald 连续模型在 moiré Brillouin zone 内对角化 Hamilton 量，计算 CNP 附近能带、gap、SDP 与 vHS，得到 DOS(E) 与 n(E) 作为对照，并引入 1/10 moiré 填充的密度窗平均以模拟实验展宽。
- **空间 mapping**：沿一维轨迹与二维红框区域分别扫描 μ(n) → 提取 CNP–SDP 间距 Δn → 通过 l = a/√(δ + θ²) 反演 θ(x,y)；同时记录 μ₀、n₀ 偏移图用于判断气泡界面位置。

## 主要发现与核心结论（Main Results）
- **DOS 与连续模型定性一致**：在 CNP（E=0）与两侧第二 Dirac 点（SDP）处 DOS 被压制；SDP 附近出现 van Hove 奇点（vHS，cyan箭头标出）；CNP 附近 Fermi velocity 相对本征 graphene 在 electron/hole 侧分别**降低 ~5.5% 与 ~7.1%**（斜率因子 1.119、1.158），与早期实验/理论值量级一致；SDP 能量的 electron-hole 不对称与 C₂ 对称性破缺（sublattice 不对称势）相符。
- **CNP 与 moiré 边带同时出现在 dμ/dn 上**：SNR 改善的 AC 模式同时显示 CNP 峰（blue）与对称分布的 SDP 峰（green），峰位载流子密度对应 moiré miniband满填充；point-to-point 取 μ(n) 转换成 DOS(E) 后，P1 与相距 ~100 nm 的 P2 之间整体 moiré 形状（CNP 压制、SDP 压制、hole-side vHS）保持稳定，但出现黑/橙箭头所指**局部 DOS 压制**，被解读为局域电荷杂质。
- **Δn(位置) 直接给出 θ(x) 谱**：沿一条线轨迹，dμ/dn 中 CNP–hole-side SDP 间距 Δn 连续变化，反映局域扭转角变化；转换得到的 θ(x) 分布在输运平均 θ≈0.56°（红线）附近，揭示 transport 看不到的局部涨落。
- **二维 θ-map 与气泡应变一一对应**：红框内 A、B 两区出现明显不同 θ，A 处 θ 升高、B 处 θ 降低；A、B 位置在形貌图上对应 trapped bubble，bubble-induced strain 使局域扭转角向两侧偏移；A、B 之外的散点（如粉色箭头）对一处更小的 bubble 反应反而更强，提示**小 bubble 更靠近 graphene界面、影响更大**，大 bubble 则可能在更深的 graphite/hBN 界面。
- **μ₀ vs n₀ 偏移可分辨 bubble 界面归属**：n₀ 偏移图中 A、B 大气泡位置出现显著特征（远程掺杂效应），而 μ₀ 偏移图在 A、B 处没有相应特征，仅在小 bubble（粉色箭头）处出现信号；由此判断**小 bubble 位于 bottom hBN/graphene 界面，大 bubble 位于 graphite/hBN 界面**——这是仅靠形貌图无法区分的结论。

## 潜在研究方向（Future Directions）
- **拓展材料体系**：方法可推广至 twisted bilayer graphene（TBG）、twisted TMD homobilayer（如 tMoS₂、tWSe₂）与 trilayer/四层 moiré；尤其在 TBG 的 magic angle 附近，局域 θ 不均匀性被广泛怀疑是"为什么器件之间重复性差"的根源，KPFM-DOS 可能提供直接的局域测量。
- **角度分辨率与扫描速度**：当前 Δn 提取受 AC 调制引入的密度窗展宽影响（0.5 V ↔ 0.58 × 10¹² cm⁻²），存在 SNR ↔ 分辨率取舍；进一步降低1/f 噪声、提升 Q-factor 或引入 ML/相位提取算法可在不牺牲 SNR 的情况下把角度分辨率推到 ~0.05° 以下，以分辨 magic angle 附近的微弱梯度。
- **从被动 mapping 到主动应变工程**：得到 θ(x,y) 与 bubble 界面归属后，可在制备阶段通过控制降温速率、堆叠张力、选择特定 polymer（PC vs PDMS）来主动设计 bubble 分布，从而**把"扭转角 disorder"从噪声源变成 designer degree of freedom**；文中也明确把此列为 future device design 方向。
- **强场/超快探针的潜在联用**：与课题 general-moire-strong-field-probe-20260726 直接相关——KPFM 给出的局域 θ 可作为 HHG/Berry-curvature 检索的先验（prior），用于缩小 inverse problem 解空间；反过来，光泵浦（photo-induced strain、stacking switch）后原位 KPFM mapping 有望捕捉**光致扭转角重排**这一全新瞬态自由度。
- **开放问题**：(1) μ₀、n₀ 偏移的相对大小是否可定量化为"距 graphene 的界面距离"——目前仅做二分类判据，需要 calibration；(2) DOS 中的局域杂质压制（黑/橙箭头）能否反演为单个杂质的散射势？(3) 该方法在低温极限（mK）与高磁场下的表现尚未验证，对于关联相边界处的局域 DOS 测量尤为关键；(4) AC 调制的 averaging 效应使得 vHS 高度与宽度的定量比较仍受系统误差制约，需要更精细的反卷积方案。
- **局限与注意事项**：测得的 DOS 是 thermodynamic（对所有动量平均）而非谱函数 A(k,E)，无法给出动量分辨信息；与 STM/STS 的 local spectrum 互补而非替代；当前数据为 14 K 下采集，更低温度下关联相变附近的局域重整化效应不可直接外推。

---

File reference：完整论文 PDF / 摘要已通过 web_extract 获取，原始链接 https://arxiv.org/abs/2511.01246。如需把笔记追加到 wiki（~/Desktop/hermes_workspace/knowledge_base/AI_wiki/）或同步到 DeepXiv 知识库，告诉我目标路径即可。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：局域热力学 DOS 测量与扭角映射（14 K KPFM：AC 调制直测 dµ/dn + BM 对照，0.56° TDBG）

**原理**：自建 14 K KPFM：针尖/石墨烯/背栅同时加 DC+AC，调制频率 f_e 处静电力归零偏压即 CPD → 直接访问化学势 µ；AC 调制直测 dµ/dn（0.5/1/2 V_RMS 对应密度窗口 0.58/1.15/1.73×10¹² cm⁻²，灵敏度-分辨率权衡）；定标：4 K Landau fan（CNP@V_BG≈−2 V，±2/±6/±10）得 dn/dV_BG=0.408×10¹² cm⁻²V⁻¹；偏移扣除以 CNP 参考；BM 连续模型对照（能隙/DOS 施加 1/10 满填充展宽模拟实验）；输运估平均扭角 ~0.56°——局域热力学 DOS 测量+扭角映射。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 测量 | T=14 K；AC 调制 0.5/1/2 V_RMS；dn/dV_BG=0.408×10¹² cm⁻²V⁻¹ | §技术平台/定标 |
| 扭角 | ~0.56°（满填充莫尔微带载流子密度估计） | §输运表征 |

**适用边界**：AC 调制致峰展宽（灵敏度-分辨率权衡）；单栅耦合扫描（无独立 D 调控）；页面提取限方法节（局域 DOS 谱结果在正文）。
**代表作**：本文（arXiv:2511.01246）
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[5-11]]
- [[Local thermodynamic DOS measurement and twist-angle mapping in graphene-hBN superlattices]]
- [[general-moire-strong-field-probe-20260726]]
- [[强关联体系]]
- [[强场超快]]
- [[强场驱动]]
- [[相位匹配]]
- [[莫尔超晶格]]
- [[量子几何]]
<!-- /linsai-wikilinks -->
