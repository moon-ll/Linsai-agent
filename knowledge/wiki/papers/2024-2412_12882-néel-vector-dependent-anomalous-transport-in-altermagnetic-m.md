---
title: "2024-2412_12882-néel-vector-dependent-anomalous-transport-in-altermagnetic-m"
type: "papers"
created: "2026-09-27T01:51:40Z"
updated: "2026-11-15T15:09:25Z"
tags: []
related: ["2412.12882", "Berry 曲率", "CrSb", "Kubo公式", "Néel vector-dependent anomalous transport in altermagnetic metal CrSb", "PLAN", "TDDFT", "arpes", "dmft", "general-order-parameter-ultrafast-readout-20260727", "反常霍尔效应", "固体HHG", "强场驱动", "自旋劈裂", "量子几何"]
source_raw: "2024-2412.12882-néel-vector-dependent-anomalous-transport-in-altermagnetic-m.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-27T12:17:48Z"
merged_from: ["wiki/papers/2412.12882.md"]
---

• # CrSb 中 Néel 矢量依赖的反常输运：第一性原理研究

  ## 林赛的理解

  这是一篇"地基型"论文——不是现象学新发现，而是为 CrSb 这个金属交错磁体（altermagnet）的反常输运建立了完整的理论地图：磁晶各向异性能（MAE）有多小、AHC/ANC 随 Néel 矢量取向怎么变、峰值在哪个方向、物理起源是什么。对我们做"超快读出序参量"这条线，它有三重价值：① 它给出了**Néel 矢量方向 → 反常输运张量元 → 可探测信号**的定量映射表，这正是超快探测需要的事前"信号预言"；② MAE 极小（各取向能量差 <1 meV）意味着 CrSb 的 Néel 矢量可以被衬底交换耦合轻易扳动——这既是稳态操控路径，也说明超快光场驱动时磁各向异性能垒不构成障碍；③ Berry 曲率集中于 SOC 打开的节点环附近、费米面处 AHC 随能量剧变（峰值 98 S/cm 紧邻 EF），这类"能量敏感型" Berry 曲率结构正是**交变磁矩与量子几何相关动力学**最可能出大信号的材料类型。弱点也要直说：纯理论工作，且 Néel 矢量实际转动角度依赖铁磁衬底交换耦合强度，文中只能给定性讨论，这给实验留下真实的空白。

  ## 研究问题

  核心问题：在金属交错磁体 CrSb 中，反常霍尔电导（AHC）与反常能斯特电导（ANC）如何依赖于 Néel 矢量的取向？具体分解为三问：

  1. CrSb 的磁晶各向异性能（MAE）有多大？Néel 矢量能否被外场（如铁磁衬底交换耦合）在实验上实际转动？
  2. 当 Néel 矢量从 c 轴转出时，AHC/ANC 张量的哪些分量出现、大小多少、最优取向是哪里？
  3. 显著的 AHC/ANC 的微观起源是什么（Berry 曲率分布在动量空间的何处、由什么产生）？

  ## 研究背景

  - 交错磁性（altermagnetism）是介于铁磁与反铁磁之间的第三类共线磁体：净磁化为零（如反铁磁），但两个反平行子晶格由旋转对称（而非反演/平移）联系，导致自旋劈裂能带（类铁磁）。首个实验确认的交错磁体是半导体 MnTe（ARPES 观测）。
  - 反常霍尔效应（AHE）在反铁磁中通常被 P·T 或 T|t 对称禁止（全布里渊区 Berry 曲率之和为零），但交错磁体允许非零净 Berry 曲率与内禀 AHE。此前已在 RuO₂、Mn₅Si₃、MnTe 中观测到，但各有硬伤：RuO₂ 基态磁性有争议；MnTe 是带隙约 1.3 eV 的半导体，电导不佳；Mn₅Si₃ 磁态对温度敏感且涉及非共线结构。
  - CrSb 是近期实验确认的金属交错磁体（NiAs 型，P6₃/mmc，g 波，自旋劈裂达 1.0 eV，费米面附近有表面 Fermi 弧，高迁移率多载流子），且 Néel 温度超过 700 K、基态对温度不敏感——正是研究反常输运所需的"干净金属平台"。
  - Néel 矢量沿 c 轴时 CrSb 的 AHE 被对称禁止，因此只有转动 Néel 矢量才能激活反常输运——MAE 大小决定了这条路是否可行，这是本文的出发点。

  ## 研究方法

  方法密度中等偏高：核心是 DFT + Wannier 插值 + Kubo 公式计算 Berry 曲率输运，计算设置完整可复现。按方法卡整理如下。

  **方法卡：CrSb 反常输运的第一性原理计算**

  - **原理**：DFT 自洽总能计算评估 MAE；由 Wannier 插值构建紧束缚哈密顿量，Kubo 公式计算 Berry 曲率（式 1），布里渊区积分得 AHC（式 2）与 ANC（式 3）；Néel 矢量转动时由对称性分析（并经 Symmetr 软件复核）确定 AHC/ANC 张量非零元。

  - **参数表**（数值均出自原文 §II 与正文/图表）：

    | 参数 | 取值 | 出处 |
    |------|------|------|
    | 晶体结构 | NiAs 型六方，空间群 P6₃/mmc（No. 194），实验晶格常数 a = b = 4.103 Å，c = 5.463 Å | §II；Fig. 1(a) |
    | DFT 软件/泛函 | VASP；PBE-GGA | §II |
    | 平面波截断能 | 400 eV | §II |
    | 能量收敛判据 | 10⁻⁷ eV | §II |
    | 弛豫/自洽 k 网格 | 11 × 11 × 9 | §II |
    | Wannier 投影初值 | Cr 3d 轨道 + Sb 5p 轨道（WANNIER90） | §II |
    | AHC/ANC 积分 k 网格 | 192 × 192 × 192（收敛测试后取值） | §II |
    | Hubbard U 稳健性检验 | U = 0 / 0.25 / 0.5 / 0.75 / 1 eV | Fig. 2, Table I |
    | MAE 总能比较 | 各 Néel 矢量取向总能差 < 1 meV（接近 DFT 精度极限） | Table I |
    | Mott 关系检验 | T = 50 K 下由 AHC 能量导数反推 ANC，与式 (3) 直接计算对比 | §III C, Fig. 4(a) |

  - **适用边界**：① MAE <1 meV 已逼近 DFT 精度极限，本文的"弱各向异性"结论在精度边界上，需实验（如扭矩磁强计）佐证；② 各取向总能计算未加 penalty functional 约束磁矩方向，作者将此视为 MAE 弱的旁证，但这也意味着不排除亚稳构型；③ AHC/ANC 为静态（平衡）输运量，不涉及频率依赖或外场动力学响应。

  - **代表作**：Yu, Shahid, Liu, Shao, Chen & Sun（2024/2025），arXiv:2412.12882——给出 CrSb 的 MAE 与 Néel 矢量取向依赖 AHC/ANC 全套理论数值；配套实验参照 Zhou et al., Nature (2025)（晶体对称性操控 CrSb 交错磁序，arXiv 全文引文 [69]）。

  ## 主要发现与核心结论

  1. **MAE 极小**：反铁磁态各 Néel 矢量取向（a、½a+b、c）的总能差小于 1 meV（以 c 轴取向为零点：a 方向 0.008–0.335 meV、½a+b 方向 0.119–0.567 meV，随 U 值变化，Table I）；除 U = 0.75 eV 外 c 轴取向为基态，与实验一致。反铁磁态能量显著低于铁磁态。这意味着 Néel 矢量可被铁磁衬底交换耦合轻易调控。
  2. **AHC 随 Néel 矢量取向强烈调制**：Néel 矢量从 c 转向 ½a+b 转到 45° 时 σxz 达最大 ≈ 72 S/cm；AHC 张量元随转角从 0 → 最大 → 回零（σxy 除外）。σxz 的能量依赖显示峰值约 98 S/cm 位于费米面左侧（空穴掺杂可迅速提升 AHC）。
  3. **ANC 同步出现且室温显著**：最强 AHC 对应取向的 ANC 最大值 -0.19 A/m/K（300 K 下 45° 取向 σxz 分量，Table II）；ANC 绝对值从 50 K 急升至 125 K 达峰（约 0.224 A/m/K），再缓降至 450 K；室温下仍为 -0.185 A/m/K。BC 公式与 Mott 关系（50 K）结果吻合。绝对值低于典型铁磁体但与 RuO₂ 相当。
  4. **起源为节点环的 SOC 隙**：第 25/26 自旋带在费米面附近形成多组节点环（M-C-B 面内两组×3 等价面共 6 个，由镜面保护；kz=0 面附近一个波形节点环由复共轭对称保护），纳入 SOC 后节点环打开能隙、在费米面处产生非零 Berry 曲率——显著 AHC/ANC 均源于此。不同自旋的节点环由 Mz 镜面联系。
  5. **实验方案设计**：CrSb(0-110) 膜沿 ½a+b 生长可测 σxz；转动 Néel 矢量靠铁磁衬底交换耦合驱动；取向 ½a+b 的情形须用绝缘铁磁衬底（如 CrI₃、Cr₂Ge₂Te₆）以免衬底自身 AHE 信号混入；沿 a 取向可用常规铁磁衬底（衬底磁矩沿 a 时 jAHE ∼ M×E 使衬底不贡献信号）。c 轴转动到 a/½a+b 的难易取决于温度、衬底-CrSb 交换能与 CrSb 内反铁磁交换劲度。
  6. CrSb 兼具高 Néel 温度（>700 K）、表面 Fermi 弧、高迁移率载流子与可开关的反常输运，被定位为研究交错磁输运的核心平台。

  ## 潜在研究方向

  1. Néel 矢量实际转动角度无法由第一性原理确定——依赖衬底交换耦合、CrSb 反铁磁劲度、温度等外参，文中仅有定性讨论，需微磁模拟或实验标定。
  2. MAE <1 meV 处于 DFT 精度边界，弱各向异性结论的定量可靠性受方法精度限制。
  3. 铁磁衬底方案中，CrSb 膜生长取向（0-110）、界面交换耦合强度、界面质量（如文献 [69] 用晶体对称性操控的方案）均待实验验证；金属衬底引入的寄生 AHE 信号需靠绝缘铁磁衬底规避。
  4. Néel 矢量倾斜（canting）由阻尼类自旋轨道力矩或 DMI 力矩诱导的贡献，在镜面对称破缺 CrSb 膜中需与交错磁内禀 AHE 区分（文献 [69] 表明主要来自交错磁序，但定量拆分未做）。
  5. 未涉及：频率/时间依赖响应、非线性输运、磁振子贡献——这些恰是超快动力学研究的入口。

  ## 与林赛研究的关联

  1. **序参量超快读出（order-parameter ultrafast readout）的直接接口**：本文给出了 CrSb 的"Néel 矢量取向 → AHC/ANC 张量 → 电学信号"定量映射，正是我们课题需要的探测通道预言：超快光脉冲驱动 Néel 矢量进动/瞬态转动后，反常霍尔电压可作为零净磁化序参量的**电学读出**；室温 ANC -0.185 A/m/K 还提供了热学读出备选。
  2. **强场驱动可行性论证**：MAE 极小（<1 meV/原子尺度）说明光场与自旋-晶格/交换通道耦合时，磁各向异性不构成额外势垒；45° 取向 AHC 峰值 98 S/cm 紧邻费米面，提示费米面工程（空穴掺杂）可把读出信号放大——这是方案写作中"信号量级预算"的直接素材。
  3. **量子几何与交变磁方向**：AHC/ANC 由节点环 SOC 隙产生、Berry 曲率在 k 空间呈节点环聚集分布，这种"几何源点高度局域"的结构是强场下量子几何贡献（反常输运的 Berry 曲率对）动力学放大的有利条件，可与本组交变磁矩动力学方向对接。
  4. **方法学复用**：VASP + Wannier90 + Kubo + 192×192×192 k 网格这套流程及对称性分析（Symmetr）做法，可直接移植为我们评估其它候选交错磁/莫尔磁体系反常输运响应的计算模板。
  5. 注意边界：本论文是平衡态静态输运，不含光场响应；我们做超快读出的理论预估时需在素材之上补充含时或微扰响应计算，不能直接把静态 AHC 当瞬态信号用。

  ## 来源
  - 蒸馏自全文（deep-read）


## 合并自「Néel vector-dependent anomalous transport in altermagnetic metal CrSb」

## 阅读笔记

### general-order-parameter-ultrafast-readout-20260727

笔记已写入。结构化分析如下:

# 论文笔记:2412.12882 — Néel vector-dependent anomalous transport in altermagnetic metal CrSb

**基本信息**
- 标题:Néel vector-dependent anomalous transport in altermagnetic metal CrSb
- 作者:Tianye Yu, Ijaz Shahid, Peitao Liu, Xing-Qiu Chen, Yan Sun, Daoxin Su
- 机构:中国科学院金属研究所 (沈阳)
- 提交:2024-12-17,v4 版
- 来源:[arXiv:2412.12882](https://arxiv.org/abs/2412.12882)
- 课题相关度:**高** — CrSb 是 altermagnet HHG 序参量读出的关键实验材料;此论文提供了 Néel 电场可调 + Berry 曲率物理图像。

## 研究问题 (Research Question)

- **核心问题**:在金属性 altermagnet CrSb 中,当 Néel 矢量(序参量)被外场旋转到不同晶向时,其反常霍尔电导 (AHC) 与反常能斯特电导 (ANC) 如何随之变化?何种 Néel 取向能让这两个输运张量达到最大值?
- **中心论点**:CrSb 具有**极低的磁晶各向异性能 (MAE)**,使 Néel 矢量可被外电场或相邻铁磁层交换偏置轻易旋转;当 Néel 矢量从 c 轴旋转 45° 至 ½a+b 方向时,AHC 与 ANC 同时达到峰值,这是 SOC 在多个 nodal ring 处打开能隙、产生显著 Berry 曲率分布的结果。
- **目标**:把 CrSb 定位为继 RuO₂、MnTe、Mn₅Si₃ 之后第四个可系统研究 altermagnet 反常输运的金属平台,并提出具体实验构型。

## 研究背景 (Background)

- **领域背景**:交变磁性 (altermagnetism) 是 Šmejkal 等 2022 年提出的新型共线磁有序,既有铁磁的自旋劈裂能带,又有反铁磁的零净磁矩,核心是旋转对称(而非反演或平移)连接两套磁亚晶格,产生 d-wave/g-wave/i-wave 对称性劈裂。
- **前人工作**:RuO₂ 的磁性基态仍有争议;MnTe 为首个 ARPES 确认的 altermagnet 但属半导体(带隙 ~1.3 eV),导电性差限制输运测量;Mn₅Si₃ 磁态对温度敏感且涉非共线结构 — 三个候选材料各有缺陷。
- **CrSb 现状**:2024 年被多个独立 ARPES 团队确认拥有高达 ~1.0 eV 的非相对论性自旋劈裂,具备高 T_N > 700 K、表面 Fermi arc、高载流子迁移率、非线性磁场 Hall 效应等突出优势。
- **研究动机**:此前 altermagnet 反常输运的 Néel 矢量依赖性尚未系统化;CrSb 弱 MAE 的发现打开了"电场可调序参量"的窗口,亟需理论预测各方向的输运响应,为实验提供靶向 AHE 信号方案。

## 研究方法 (Methods)

- **第一性原理平台**:VASP + PBE-GGA;实验晶格常数 a=b=4.103 Å,c=5.463 Å;截断能 400 eV,能量收敛 10⁻⁷ eV。
- **k 网格**:自洽 11×11×9;Berry 曲率/AHC/ANC 计算 192³。
- **紧束缚模型**:WANNIER90 以 Cr-3d 和 Sb-5p 轨道为初猜构造 Wannier 函数。
- **输运公式**:Kubo公式积分 Berry 曲率 Ω_ij^n 得 AHC;Berry 曲率加权 (E_n − E_F) f_n 积分得 ANC;低温 ANC 用 Mott 关系 α_ij = (π²/3)(k_B²T/e)(∂σ_ij/∂E)|_{E_F} 交叉验证。
- **参数扫描**:旋转 Néel 从 c 轴到 a、a+b、½a+b 三个代表方向,0°–90° 区间的 AHC/ANC;U = 0–1 eV 扫描 MAE 稳定性。
- **对称性校验**:用 Symmetr 软件双校验非零 AHC/ANC 张量元。
- **实验构型**:提出铁磁绝缘体衬底 (CrI₃, Cr₂Ge₂Te₆) 通过交换偏置驱动 CrSb Néel 矢量旋转的两种薄膜几何。

## 主要发现与核心结论 (Main Results)

- **弱 MAE 定量化**:不同 Néel 方向的 altermagnetic 态总能差 **< 1 meV**,逼近 DFT 精度极限;不同 U 值下 Néel 沿 c 均为基态;无 penalty functional 时 SCF 自然收敛到预设 Néel 取向,证实 CrSb MAE 极弱。
- **AHC 的方向依赖**:当 Néel 从 c 旋转到 ½a+b 时,σ_xz 与 σ_xy 非零;AHC 张量元在 45° 取峰值,90° 回到零。最强 **σ_xz ≈ 72 S/cm**,出现在 Néel 旋转 45° 时;其能量依赖在 E_F 左侧出现约 **98 S/cm** 尖峰,意味着轻空穴掺杂可显著放大 AHC。
- **ANC 定量结果**:300 K 下 Néel 沿 ½a+b、旋转角 45° 时,α_xz 达 **-0.19 A/m/K** 最大值;温度扫描显示 |α| 从 50 K 急升到 125 K (~0.224 A/m/K),125–450 K 缓降,室温 300 K 仍保持 **-0.185 A/m/K**,与 RuO₂ 相当。
- **Mott 关系交叉验证**:50 K 下由 Mott 公式推出的 ANC 与 Berry 曲率直接积分结果高度一致,证明 AHC 峰附近的尖变化是 ANC 大的根源。
- **微观起源**:不含 SOC 时沿 M-C-B 路径自旋向下带在 E_F 附近有两个交叉点;加入 SOC 后这些交叉点打开能隙,使 E_F 位于 gap 中,贡献 Berry 曲率。全 Brillouin 区存在六条 + wave-like 多组 nodal ring,均被 SOC 打开能隙后产生显著 Berry 曲率 — **AHC/ANC 的本源是 SOC 在 nodal ring 处打开的能隙**。
- **实验可行性**:CrSb (01-10) 薄膜 + 铁磁绝缘体衬底 (CrI₃、Cr₂Ge₂Te₆) 的两种几何;**衬底必须是绝缘体**,否则金属衬底 AHE 污染信号;Néel 倾斜由 damping-like SOT + DMI 矩驱动,AHE 主要来自 altermagnetic 序而非简单 canting(实验已证实)。

## 潜在研究方向 (Future Directions)

- **实验验证紧迫性**:所有 AHC/ANC 数值均为 DFT 预测,亟需在 CrSb薄膜上生长并与铁磁绝缘体异质集成,实测 Néel 旋转下的反常 Hall 信号。
- **DFT 方法局限**:总能差 < 1 meV 已达 DFT 极限,MAE 数值高度依赖交换关联泛函(LDA/PBE/SCAN/DFT+U);不同 U 下基态方向可能反转(Table I 中 U=0.75 eV 时 a 略低于 c),需要 DMFT/QMC/混合泛函复核。
- **Néel 矢量动力学空白**:论文仅涉及平衡态 AHC/ANC,**未涉及 Néel 在外场下的超快动力学** — 这正是 HHG 序参量超快光读出课题的核心。CrSb 弱 MAE 暗示 GHz-THz 尺度的 Néel 进动可被光场直接驱动,但需含时 DFT + LLG 模拟。
- **HHG 兼容性挑战**:CrSb 金属性带来自旋劈裂 ~1.0 eV,但固体 HHG 在带隙 1–3 eV 半导体中效率最高;CrSb 金属性可能导致 HHG 转换效率低、信号衰减快,需 SBE 或 RT-TDDFT 评估 CrSb HHG 可行性,并与 TiSe₂、MnTe 等窄带隙 altermagnet 比较。
- **多序参量分辨**:CrSb 是 g-wave altermagnet(4 个 nodal plane),对称破缺模式比 d-wave (MnTe) 更复杂;HHG 中如何从偏振/椭偏依赖区分 g-wave vs d-wave 是开放问题,需要张量化的非线性电导率展开。
- **nodal ring 工程**:SOC 在 nodal ring 处打开能隙是 AHC 的核心 — 通过应变/掺杂/外延应力调控 nodal ring 位置可放大 AHC;但目前缺乏"应变—nodal ring—AHC"系统映射,需进一步研究。
- **类比拓展**:CrSb 的成功预示其他 NiAs 型 altermagnet (CrAs, MnSb, VPt 等) 可能呈现弱 MAE + 大自旋劈裂 + 显著 AHE 组合,可作为寻找新金属 altermagnet 平台的材料基因组路线图。

笔记文件已保存:`~/Desktop/hermes_workspace/knowledge_base/literature_notes/general-order-parameter-ultrafast-readout-20260727/2412.12882-CrSb_altermagnet_transport_note.md`


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：CrSb Néel 矢依赖反常输运的第一性原理计算（Wannier 插值 + Kubo Berry 曲率 + Symmetr 复核）

**原理**：DFT 自洽总能评估 MAE；Wannier 插值（Cr 3d + Sb 5p 投影，WANNIER90）构建紧束缚哈密顿量，Kubo 公式算 Berry 曲率，BZ 积分得 AHC 与 ANC；Néel 矢转动时由对称性分析（Symmetr 软件复核）确定 AHC/ANC 张量非零元——建立 Néel 矢方向 → 反常输运张量的完整映射。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 晶体结构 | NiAs 型六方 P6₃/mmc（No.194）；a=b=4.103 Å、c=5.463 Å（实验值） | §II |
| DFT 设置 | VASP；PBE-GGA；截断 400 eV；能量收敛 10⁻⁷ eV；弛豫/自洽 k 网格 11×11×9 | §II |

**适用边界**：页面提取限方法节（Kubo 积分 k 网格密度与结果数值在正文/图表）；Kubo 公式限线性响应输运；Wannier 投影窗口选择影响插值质量。
**代表作**：本文（arXiv:2412.12882）；工具链：VASP + WANNIER90 + Symmetr
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[2412.12882]]
- [[Berry 曲率]]
- [[CrSb]]
- [[Kubo公式]]
- [[Néel vector-dependent anomalous transport in altermagnetic metal CrSb]]
- [[PLAN]]
- [[TDDFT]]
- [[arpes]]
- [[dmft]]
- [[general-order-parameter-ultrafast-readout-20260727]]
- [[反常霍尔效应]]
- [[固体HHG]]
- [[强场驱动]]
- [[自旋劈裂]]
- [[量子几何]]
<!-- /linsai-wikilinks -->
