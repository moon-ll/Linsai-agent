---
title: "2024-2405_12679-observation-of-spin-splitting-in-room-temperature-metallic-a"
type: "papers"
created: "2026-09-26T21:37:15Z"
updated: "2026-11-15T15:09:22Z"
tags: []
related: ["2405.12679", "CrSb", "Observation of Spin splitting in Room-Temperature Metallic Antiferromagnet CrSb", "arpes", "dmft", "general-new-idea-20260822", "交变磁体", "反常霍尔效应", "反铁磁自旋电子学", "固体高次谐波", "强场超快", "强场驱动", "相干声子", "自旋劈裂", "非线性光学"]
source_raw: "2024-2405.12679-observation-of-spin-splitting-in-room-temperature-metallic-a.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
aliases: ["10.1002/advs.202406529"]
digest_level: "fulltext"
updated_at: "2026-09-27T01:00:44Z"
merged_from: ["wiki/papers/2405.12679.md"]
---

• # 室温金属反铁磁体 CrSb 中的自旋分裂观测（ARPES）

  ## 林赛的理解

  这篇工作是"alter磁体（altermagnet）"概念提出后最干净的实验确认之一，而它对强场超快方向的价值不在自旋电子学本身，而在**它给"交变磁体中可动量分辨的自旋劈裂能带"提供了第一个高温、金属体系的高分辨实证**。对我们而言有三点直接可用：

  1. **强场驱动下的动量依赖自旋纹理**。CrSb 的自旋劈裂是反铁磁序诱导、SOC 无关、k 依赖的，其自旋纹理在三维布里渊区呈交替符号图案。强场超快泵浦这种体系时，不同 k 点自旋极化的电子感受到不同的光场选择定则——这是"交变磁 + 强场"耦合的实验入口。已有的交变磁方向词（交变磁/alter磁体）目前偏理论，这篇提供了可直接引用的能带级实验基准。
  2. **方法学复用价值高**。这是标准的同步辐射 hν 依赖 ARPES + GGA+U DFT 联用范式：内势标定（V₀ = 12.8/11.8 eV）、kz 扫描轨迹设计、二阶导数 + MDC 拟合的劈裂判据、带电缺陷导致的整体能量平移修正——我们课题方案中若涉及强场驱动的磁体系电子结构表征，这一整套测量-计算对照流程是可移植的素材。
  3. **被本组课题引用**（used_by_proposals: general-new-idea-20260822），说明它已在我们的方向论证链里，此笔记可支撑该课题的"交变磁体系中强场响应"论证段。

  ## 研究问题

  在 Néel 温度 T_N = 703 K 的金属反铁磁体 CrSb 中，能否用高分辨 ARPES 直接观测到由**非相对论对称性**（而非自旋-轨道耦合）诱导的、动量依赖（k-dependent）的自旋劈裂（spin splitting, SS），并刻画其在三维动量空间中的各向异性演化？

  核心判断标准有三条：

  - 劈裂应**在镜面对称平面（ΓMK、ΓKHA 平面及 kz = nπ/c 面）消失**、在非高对称点最大——排除 Zeeman 型劈裂；
  - 劈裂**对 SOC 强度不敏感**（文中明确：Sb 虽有显著 SOC，但对 SS 幅度影响甚微）——区别于 Rashba/Dresselhaus 型劈裂；
  - 自旋极化符号随 kz 反转、劈裂幅度随面内/面外方向周期性变化——区别于表面 Rashba（其面外 SS 幅度应恒定）。

  ## 研究背景

  - 传统磁体分类只覆盖有 SOC 的体系；**SOC 可忽略的磁体**（自旋与轨道部分解耦）长期被对称性理论忽视。Wu 等（2007）、Hayami 等（2019–2020）提出电子的各向异性动能运动产生有效 SOC，导致各向异性自旋劈裂 [1–3]；Yuan 等（2020）指出中心对称、低 Z 反铁磁中可存在显著 k 依赖 SS，并将 1651 个磁空间群归类为七种原型（SST-1 至 SST-7），其中 SST-4 预言了丰富 AFM 诱导 SS 材料 [4–6]。
  - Liu 等（2022）引入**自旋空间群（spin space group）**理论框架 [7]，并预言弱 SOC Z₂ 拓扑相、手性 Dirac 费米子、C 对自旋谷锁定、非相对论自旋霍尔效应、自旋劈裂扭矩、非相对论 Edelstein 效应、反常霍尔效应等一系列新现象 [7–25]；"altermagnet"一词即用于指称具有此类 AFM 诱导 SS 的共线反铁磁体 [26–28]。
  - 实验先行材料的局限：RuO₂ 的异常霍尔效应已有观察但其真实磁相仍有争议 [24, 31–34]；MnTe（~0.37 eV SS）与 MnTe₂ 均为有带隙的半导体，电导性不佳 [30, 35, 36]。CrSb 的优势：**金属导电性、面外 A 型反铁磁（面内铁磁耦合、相邻层反铁磁耦合）、T_N = 703 K 远高于室温、有效磁矩更大、自旋扭矩电导率更高**。
  - 前人在 CrSb 薄膜上用软 X 射线 ARPES 做过电子结构研究，但能量/动量分辨率不足，未能清晰观测预期的各向异性巨自旋劈裂 [39]——本工作用高分辨 VUV + 软 X 射线 ARPES 解决这一缺口。

  ## 研究方法

  **方法密度评估**：核心贡献是实验观测 + DFT 对照，实验章节参数详尽，按方法卡格式整理。

  ### 方法卡 1：同步辐射 ARPES 测定三维自旋劈裂能带

  - **原理**：hν 依赖 ARPES 通过改变光子能量扫描样品动量面外分量 kz，将测得的自由电子末态色散与 DFT 体态能带比对，定出内势 V₀ 与 kz 轨迹；在固定 kz 面内旋转测量方位角，即可重建 SS 在 3D 动量空间的周期性演化。
  - **样品**：CVT 法生长的 (001) 解理面毫米级六方单晶（Cr:Sb:I₂ = 1:1:0.1 摩尔比，双温区炉 T_L = 750 ℃、T_H = 850 ℃，保温两周）；自熔剂法（self-flux）生长的 (100) 解理面针状单晶（Cr:Sb = 3:7，6 h 升温至 1000 ℃ 保温 20 h，100 h 缓冷至 750 ℃ 后离心去 Sb 助熔剂）。
  - **测量序列与参数表**（均为原文数值）：

  | 参数 | 取值 | 出处 |
  |------|------|------|
  | 测量温度 | SSRF/HiSOR ≈ 30 K；SPring-8 ≈ 77 K | Experimental Section |
  | 真空度 | 优于 2×10⁻¹⁰ Torr，原位解理 | Experimental Section |
  | SSRF BL03U | Scienta Omicron DA30 分析器，p 偏振，hν = 40–120 eV | Experimental Section |
  | SSRF BL09U | DA30，p 偏振，hν = 94–144 eV | Experimental Section |
  | HiSOR BL09A | SPECS PHOIBOS 150，p 偏振，hν = 11–40 eV | Experimental Section |
  | SPring-8 BL25SU | DA30，C⁺ 圆偏振，hν = 400–650 eV（软 X 射线） | Experimental Section |
  | (001) 面内势 V₀ | 12.8 eV（ΓMLA 面 kz-kx CEC 比对 DFT 定出） | Fig. 2b |
  | (100) 面内势 V₀ | 11.8 eV | Fig. 4b |
  | 关键光子能量（(001) 面） | hν = 118 eV（bulk Γ，kz = 10π/c）、106 eV（Γ-A 中点，kz = 9.5π/c，SS 最大）、94 eV（A 点，kz = 9π/c，重新简并） | Fig. 2c |
  | 面内扫描（OBC 面） | hν = 106 eV，cut 1–5 方位角相对 Γ̄-M̄ 为 0°、10°、30°、50°、60° | Fig. 3 |
  | (100) 面测量 | hν = 82 eV（kz = 5.5π/a'，非高对称点）与 100 eV（kz = 6π/a'，bulk Γ） | Fig. 4c |
  | 数据分析 | EDC 方向二阶导数 + MDC 峰值拟合；MDC 自 EB = 0 至 0.8 eV 每 0.1 eV 偏移绘制 | Fig. 2/3 |
  | 能带整体平移修正 | (001) 数据 DFT 上移 0.15 eV、(100) 数据上移 0.31 eV（计入实际晶体带电缺陷） | Fig. 2c/4c |

  - **计算设置**：VASP + PAW，PBE 交换关联泛函，平面波截断能 520 eV，GGA+U 处理 Cr 3d（U = 1.0 eV），k 点 10×10×6（Γ 方案），实验晶格常数 a = b = 4.18 Å、c = 5.46 Å，原子力收敛 < 1×10⁻³ eV/Å，总能量收敛 1×10⁻⁷ eV；Wannier90 构造 Cr-d + Sb-s/p 最大局域化 Wannier 函数，WannierTools 模拟 CEC。
  - **辅助表征**：Rigaku SmartLab XRD（Cu Kα）确认 (001)/(100) 取向；Laue 衍射（样品距源 5 cm，曝光 120 s）定向；Nova NanoSem450 EDX（20 kV、1 nA）；SQUID-VSM（MPMS3，降温至 1.8 K，±7 T，FC/ZFC 2–400 K、500 Oe）。
  - **适用边界**：kz 展宽效应会在二阶导数图引入邻近 kz 能带的附加谱重（作者明确提及，见 Supporting Information Section V）；磁畴尺寸远小于光斑导致无法获得可靠的自旋分辨 ARPES 数据——本文用自旋积分 ARPES + 对称性论证替代；ARPES 测得的 ~0.8 eV 小于 DFT 预言的 1.1 eV，因靠近 E_F 的"spin-up"带未在数据中观测到。
  - **代表作**：Zeng et al. 2024（本工作，CrSb SS ≥0.8 eV）；Reimers et al. 2024, Nature Communications 15, 2116（CrSb 薄膜 alter磁体劈裂直接观测） [39]。

  ## 主要发现与核心结论

  1. **观测到巨自旋劈裂且随 kz 周期性演化**：在 (001) 面 ΓMLA 平面内，能带在 bulk Γ 点（hν = 118 eV）简并，随 kz 偏离开始劈裂为 α、β 两带，在 Γ-A 中点（hν = 106 eV）劈裂最大，到 A 点（hν = 94 eV）重新合并——完全符合反铁磁序诱导 SS 的对称性预言。
  2. **劈裂量级 ≥0.8 eV**：cut 3（最大 SS 位置）在 kx = ±0.439 Å⁻¹ 处能量尺度 ~0.8 eV，显著大于已知最大 SOC 诱导 SS——BiTeI ~0.2 eV [40]、GeTe ~0.2 eV [41]；DFT 预言非高对称方向最大可达 1.1 eV。
  3. **面内各向异性**：OBC 面（kz = 9.5π/c ≡ -0.5π/c）恒定能量面上 α、β 带构成六芒星（star of David）状图样；EB = 0、0.2、0.4 eV 的 CEC 显示其为空穴带特征。面内方位角从 Γ̄-M̄（cut 1）→ Γ̄-K̄（cut 3）→ 另一 Γ̄-M̄（cut 5）扫描时，α、β 带先合并（沿 Γ̄-K̄ 简并）再劈裂，满足自旋群操作 [C₂‖C₆zt] 的周期性。
  4. **(100) 面确认**：自熔剂法生长的 (100) 面晶体上沿非高对称方向 Ē-D̄ 测得 SS 同样约 0.8 eV（绿色虚线标注）。
  5. **排除其他劈裂机制**：高对称点不劈裂排除 Zeeman SS；中心对称晶体禁戒体 Dresselhaus 与 Weyl SS；表面 Rashba 的 SS 面外幅度应恒定，与"高对称面 SS 归零"的实验事实矛盾；自旋极化符号随 kz 反转、幅度随双向周期变化，区别于线性 k 项主导的 Rashba/Dresselhaus 纹理。结论：CrSb 中的 SS 是非传统反铁磁诱导的新类型。
  6. **SOC 无关性**：尽管 Sb 预期有显著 SOC，计算表明 SOC 对 SS 幅度无显著影响（Supporting Information Fig. S4）——劈裂由反铁磁序主导。
  7. **应用前景论证**：CrSb 的 SS 幅度（≥0.8 eV）大于 MnTe 报道值 ~0.37 eV [35/36]，金属性 + T_N ≈ 703 K 使其优于半导体候选；近期已观测到 CrSb 中 Néel 矢量的 100% 无磁场翻转 [38]，指向无磁场高密度存储器件。

  ## 潜在研究方向

  - **自旋分辨直接证据缺失**：因磁畴远小于光斑，未能做 spin-resolved ARPES；单畴化样品或更小光斑下的自旋纹理成像仍是开放问题（理想参照：MnTe₂ 的 plaid 状劈裂自旋分辨观测 [30]）。
  - **实验-理论差距**：ARPES 实测 ~0.8 eV vs DFT 预言 1.1 eV，靠近 E_F 的 spin-up 带未被观测到——原因未明（可能是矩阵元效应或表面态混杂）。
  - **磁畴与表面贡献的分离**：本文以对称性论证排除表面 Rashba，但缺乏对表面态的直接独立测量。
  - **器件层面的验证**：无磁场翻转虽已被观测 [38]，SS 与输运（自旋劈裂扭矩、非相对论 Edelstein 效应等预言现象 [21–23]）之间的定量关联尚未建立。
  - **Cr:Sb:I₂ 与 Cr:Sb 配比细节**：Experimental Section 中两处原料表述出现 "Te powder/Te ingots"（疑为原文笔误，应为 Sb），引用其实验配方时需注意核对。

  ## 与林赛研究的关联

  - **交变磁方向词的直接实验支撑**：这是"交变磁（altermagnet）+ 动量依赖自旋劈裂"从理论预言走向高分辨能带实验的关键节点，与本组方向词"交变磁"直接对应，可用于课题立项依据中"交变磁体系已有清晰能带级实验基准"的论证（该文已被 general-new-idea-20260822 引用）。
  - **强场驱动接口**：CrSb 的自旋纹理随 k 交替反转（自旋极化符号随 kz 反号），强场泵浦下不同 k 区电子的光跃迁选择定则不同，可产生 k 分辨的非平衡自旋布居——为"交变磁 + 强场超快"课题提供具体可检验的动量分辨实验构想（trARPES 或强场驱动自旋动力学）。
  - **HHG/阿秒接口**：金属 CrSb 在 T_N ≈ 703 K 仍为反铁磁序，其 SOC 无关的自旋劈裂意味着固相 HHG 中的自旋选择定则由磁序对称性而非原子序数主导——对"强场驱动固体高次谐波中磁序/对称性印记"的课题有概念支撑作用；Sb 重原子带来的 SOC 与 AFM 序的竞争也可作为对称性调控 HHG 发射的候选旋钮。
  - **方法学复用**：hν 依赖 ARPES 定内势 + DFT 平移修正 + 二阶导数/MDC 拟合判据的完整流程，以及 GGA+U（U = 1.0 eV）+ Wannier90/WannierTools 的计算管线，可直接迁移到我们课题方案中任何涉及磁性体系能带表征的章节（方法卡素材）。

  ## 来源
  - 蒸馏自全文（deep-read）


## 合并自「Observation of Spin splitting in Room-Temperature Metallic Antiferromagnet CrSb」

## 阅读笔记

### general-new-idea-20260822

I now have comprehensive information about this paper. Let me compile the structured research notes.

# 论文深度笔记：CrSb 室温金属反铁磁体中的自旋劈裂观测

来源：[arXiv:2405.12679](https://arxiv.org/abs/2405.12679)（已被 *Advanced Science* 接收发表，DOI: 10.1002/advs.202406529）

## 研究问题（Research Question）

本研究的核心问题是：**金属性反铁磁体 CrSb 是否存在非相对论性、自旋轨道耦合（SOC）无关但具有显著动量依赖性的"交替磁体（altermagnet）型"自旋劈裂（spin splitting, SS）？劈裂的强度、维度各向异性和对称性根源是什么？**

论文的中心论点是：CrSb 作为一种具有 P6₃/mmc 空间群的 NiAs 型 A 型反铁磁金属，应通过自旋群（spin group）而非 SOC 表现出巨大的、k 依赖的自旋劈裂。作者旨在通过 ARPES 直接测量这一现象，并利用 DFT 验证其对称性来源，从而为室温反铁磁自旋电子学提供候选材料。

## 研究背景（Background）

该研究的学术背景建立在"交替磁体（altermagnetism）"这一新兴概念之上。Šmejkal、Mazin、Jungwirth 等人近期提出，在共线反铁磁体中存在第三类磁性——即使将 SOC 设为零，其子格通过旋转或镜面对称（如 [C₂ || Mz] 或 [C₂ || C₆zt]）连接，使电子自旋自由度部分解耦于轨道自由度，导致 k 依赖的自旋劈裂。

前期工作中已观测到的相关材料包括：RuO₂ 中的反常霍尔效应（但其磁基态存在争议）、MnTe 和 MnTe₂（但带隙较大导电性差）。CrSb 因 T_N = 703 K（远超室温）、为金属性且具有更大的自旋劈裂，被预测为更优的候选材料。已有 CrSb 薄膜的软 X 射线 ARPES 研究，但缺乏 VUV 范围的高分辨三维动量空间完整测量。本文的动机是填补这一空白。

## 研究方法（Methods）

**样品制备**：采用化学气相输运（CVT，Cr:Sb:I₂ = 1:1:0.1，750–850 °C 两周）生长 (00l) 晶面单晶；采用自助熔剂法（Cr:Sb = 3:7，1000 °C 缓冷）生长 (l00) 晶面单晶。通过 XRD、Laue 衍射、SQUID-VSM 磁化测量确认晶体质量。

**ARPES 测量**：在上海 SSRF（BL03U/BL09U）、广岛 HiSOR（BL09A）和 Spring-8（BL25SU）进行 VUV（11–144 eV）和软 X 射线（400–650 eV）测量，能量分辨率覆盖体带（94–118 eV）和表面态（12–37 eV）。样品在 2×10⁻¹⁰ Torr 真空中原位解理，测量温度 30–77 K。通过改变光子能量实现 k_z 扫描。

**理论计算**：使用 VASP + PAW 方法，PBE 泛函，GGA+U 修正（Cr 3d 轨道 U = 1.0 eV），平面波截断能 520 eV，k 点网格 10×10×6，并基于 Wannier90 构建最大局域化 Wannier 函数，使用 WannierTools 模拟常能量等值线（CEC）。实验晶格常数 a = b = 4.18 Å，c = 5.46 Å。

**数据分析方法**：对 E-k 切片进行面积归一化，关于 k_x = 0 对称化处理；通过 EDC 二次导数和 MDC 峰拟合提取能带色散。

## 主要发现与核心结论（Main Results）

1. **自旋劈裂的幅度与维度**：ARPES 直接测量到 CrSb 中两条体带 α 和 β 沿面外方向周期性能量简并与劈裂：在 Γ（hν = 118 eV, k_z = 10π/c）和 A（hν = 94 eV, k_z = 9π/c）点简并，在 Γ-A 中点（hν = 106 eV, k_z = 9.5π/c）劈裂最大。**最大劈裂能 ≈ 0.8 eV**（在 k_x = ±0.439 Å⁻¹ 处），沿 E-D 方向也为 ~0.8 eV，DFT 预测可达 1.1 eV。

2. **k_z 依赖性**：劈裂仅在 k_z ≠ nπ/c 处出现，面外方向呈周期振荡；ΓMK 和 ΓKHA 高对称面内 SS = 0，OBC 和 ΓMLA 面内 SS 最大。

3. **k_// 依赖性**：在 (001) 面内，常能量等值线呈"大卫之星"六角星图案；α、β 带随方位角变化（0°→30°→60°）靠近、合并、再劈裂，与 [C₂ || C₆zt] 自旋群对称操作一致。

4. **SOC 贡献的定量排除**：DFT 计算显示 Sb 元素虽重（强 SOC），但在 ΓMK 等高对称点和带交叉处的 SOC 诱导 SS 仅 ≈0.1 eV，远小于总劈裂 0.8–1.1 eV，证明劈裂主要源于反铁磁序本身。

5. **与其它机制的区分**：通过排除 Zeeman（高对称点无劈裂）、体 Dresselhaus/Weyl（中心对称禁止）和表面 Rashba（k_z 方向非均匀），证实 CrSb 展示的是新型 AFM 诱导 SS。

6. **与同类材料比较**：CrSb 的 SS（≥0.8 eV）显著大于 BiTeI 和 GeTe 中已知最大的 SOC 诱导 SS（~0.2 eV），也大于 MnTe 中的 ~0.37 eV，结合 T_N = 703 K 和金属导电性，更适合室温自旋电子学应用。

## 潜在研究方向（Future Directions）

1. **自旋分辨测量的限制与突破**：作者明确指出，由于可能存在远小于光斑尺寸的磁畴，难以获得可靠的自旋分辨 ARPES 数据。文中未直接可视化自旋极化纹理（不同于 MnTe₂），未来需要纳米尺度自旋分辨技术或单畴样品。

2. **"自旋向上"带的缺失**：DFT 预测的 1.1 eV 劈裂中，部分靠近 E_F 的"自旋向上"红带未在 ARPES 中观测到，原因未详细讨论，需要进一步研究表面态、矩阵元效应或电子关联对测量的影响。

3. **理论计算与实验的微小偏差**：DFT 预测 1.1 eV vs ARPES 0.8 eV，以及带需上移 0.15–0.31 eV（来自实晶体中荷电缺陷）才能匹配实验，提示需要更精确的电子关联处理（如 DMFT、自能修正）或 GW 近似。

4. **应用方向**：论文引用 arXiv:2403.07396 中 CrSb 的 100% 无场 Néel 矢量翻转，预示 CrSb 在无场高密度磁存储器件中的应用前景。后续可探索自旋-力矩效率、自旋输运、非线性光学（如高次谐波）的自旋极化效应等。

5. **强场超快动力学问题（与课题"general-new-idea"直接相关）**：CrSb 作为典型的 d-wave altermagnet，其非平衡态自旋极化、THz 驱动下的瞬态自旋极化（参考 Haag 等的 altermagnet 超快自旋极化预测）、相干声子诱导自旋劈裂调控（参考 Rajpurohit 的 THz NRSS）以及高次谐波中的 altermagnet 选择定则（参考 Šmejkal, Mizuno 等的 i-wave 理论）等，都是尚未解决的关键开放问题。

6. **更广泛的 altermagnet 材料族**：MnTe（d-wave, 半导体）、CrSb（金属, 高 T_N）、RuO₂（争议）等不同体系的横向比较将有助于建立统一的"交替磁体自旋电子学"框架。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：室温金属交变磁体自旋劈裂的多源同步辐射 ARPES 观测（hν 扫描 kz 重建 + 四束线互补）

**原理**：hν 依赖 ARPES 扫面外动量 kz：自由电子末态色散与 DFT 体带比对定内势 V₀ 与 kz 轨迹，固定 kz 面内旋转方位角重建自旋劈裂（SS）在 3D 动量空间的周期性演化；双生长路线：CVT（001) 面毫米级单晶（Cr:Sb:I₂=1:1:0.1，双温区 750/850 ℃ 保温两周）与自熔剂法 (100) 面针状单晶（Cr:Sb=3:7，1000 ℃ 保温 20 h 缓冷 100 h）；四束线互补覆盖宽 hν（11–650 eV）重建全 3D 劈裂图。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 测量温度/真空 | SSRF/HiSOR ≈30 K；SPring-8 ≈77 K；优于 2×10⁻¹⁰ Torr 原位解理 | §Experimental |
| 束线/分析器 | SSRF BL03U（DA30，p 偏振，40–120 eV）；BL09U（DA30，94–144 eV）；HiSOR BL09A（PHOIBOS 150，11–40 eV）；SPring-8 BL25SU（DA30，C⁺ 圆偏振，400–650 eV 软 X） | §Experimental |
| 生长 | CVT：T_L=750 ℃、T_H=850 ℃、两周；自熔剂：Cr:Sb=3:7、1000 ℃×20 h、100 h 缓冷至 750 ℃ | §样品 |

**适用边界**：软 X 段（77 K）与 VUV 段（30 K）温度不一致引入对比误差；末态色散法 kz 定标依赖自由电子近似（内势经验拟合）；解理面表面态贡献需 hν 依赖甄别。
**代表作**：本文（arXiv:2405.12679）；束线：SSRF BL03U/BL09U + HiSOR BL09A + SPring-8 BL25SU
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[2405.12679]]
- [[CrSb]]
- [[Observation of Spin splitting in Room-Temperature Metallic Antiferromagnet CrSb]]
- [[arpes]]
- [[dmft]]
- [[general-new-idea-20260822]]
- [[交变磁体]]
- [[反常霍尔效应]]
- [[反铁磁自旋电子学]]
- [[固体高次谐波]]
- [[强场超快]]
- [[强场驱动]]
- [[相干声子]]
- [[自旋劈裂]]
- [[非线性光学]]
<!-- /linsai-wikilinks -->
