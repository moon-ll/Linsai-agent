---
title: "2025-2509_24071-c-berrytrans-a-c-code-for-first-principles-calculation-of-be"
type: "papers"
created: "2026-09-26T21:42:54Z"
updated: "2026-11-15T15:09:20Z"
tags: []
related: ["Berry 曲率", "key-transient-quantum-phase-optical-20260726", "交变磁体", "强场驱动", "自旋劈裂", "量子几何", "量子度规"]
source_raw: "2025-2509.24071-c-berrytrans-a-c-code-for-first-principles-calculation-of-be.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
---

• # C-BerryTrans：基于第一性原理直接计算 Berry 曲率驱动反常霍尔/能斯特电导的 C++ 代码

  ## 林赛的理解

  这篇工作对我们课题库中 `key-transient-quantum-phase-optical-20260726`（暂态量子相的光学读出）有直接的工具价值：它把 Berry 曲率 Ω 的第一性原理计算从 Wannier 插值的"手艺活"变成了一条免插值、可高通量的流水线。我们读拓扑物性文献时，Berry 曲率通常被当作动量空间的"磁单极"分布来讨论，而反常霍尔电导 AHC 与反常能斯特电导 ANC 正是 Ω 的布里渊区积分——这套公式体系（Kubo 形式 + 费米/熵权重）与我们讨论强场驱动下能带量子几何响应时的数学骨架是同源的。C-BerryTrans 的价值不在新物理，而在**数值保真度与可复现性**：直接用 WIEN2k 的 FP-LAPW 本征值与动量矩阵元算 Ω，绕开了 Wannier 函数质量这个最大的不确定度来源。如果我们要给候选材料（含交变磁体候选）算 Ω 分布、判断外尔点/能带交叉对输运的微观贡献，这个工具配合它自带的 k 路径分辨模式和 k 空间可视化模块，可以快速产出"哪段能带结构贡献 Ω"的微观图像——这正是方案写作里"量子几何 → 可观测输运"论证链需要的方法素材。方法卡部分我按原文把输入参数、能量窗口判据、数值细节全部原样整理。

  ## 研究问题

  论文要回答的问题是：**如何构建一个无需 Wannier 插值、直接从第一性原理波函数出发，高效且准确地计算 Berry 曲率驱动横向输运性质（反常霍尔电导 σᴬᴴᶜ_μν 与反常能斯特电导 αᴬᴺᶜ_μν）的计算工具，并使其适用于宽温区、宽化学势区间的高通量材料筛选？**

  具体拆解为四个子问题：
  1. 能否绕过 Wannier 化（maximally localized Wannier functions, MLWFs）带来的插值误差，直接用 DFT 本征值与动量矩阵元计算 Ω？
  2. 如何在 400×400×400 乃至更密的 k 网格上实现可扩展的并行计算与低内存数据管理？
  3. 能否把 Ω 计算（重计算）与 AHC/ANC 后处理（轻计算）解耦，使单次 Ω 计算后可在任意 (T, ω) 组合下快速重算输运系数？
  4. 计算结果在已充分研究的铁磁材料（Fe、Fe₃Ge、Pd、Fe₃Al、Co₂FeAl）上是否与文献报道值定量吻合？

  ## 研究背景

  - **Ω 的核心地位**：Berry 曲率决定晶体横向输运性质，无耗散霍尔电流对自旋电子学（spintronic）应用与量子拓扑现象至关重要；Heusler 磁体中可通过改变对称元素在磁化不变的情况下把 AHC 从 0 调到 ∼1600 Ohm⁻¹cm⁻¹（Co₂MnGa 与 Mn₂CoGa，原文引文献 [10]），显示其可调器件潜力。反常能斯特效应（ANE）在纳米器件中已实现 ∼13 ± 2 W/cm³ 的高功率密度（原文引文献 [11]），可用于热流探测、自旋卡洛里电子学与热梯度磁成像显微术。
  - **ANC 的费米面选择性**：与依赖全部占据带整体积分的 AHC 不同，ANC 只来自费米能附近的能带（原文引文献 [19–21]），因此 ANC 测量对表征费米能附近的 Ω 分布、验证外尔相特别有用——这是本工具物理动机的一部分。
  - **现有方法的瓶颈**：主流做法是基于紧束缚模型的 Wannier 插值（Wannier90、WannierTools）。高质量 Wannier 函数（HQWFs）要求目标能窗内能带可与其他能带解纠缠、投影对其他带贡献可忽略，且数目尽量少；但当目标区能带高度纠缠、强色散（如金属）时不存在解纠缠能窗，Wannier 化"hopeless"，插值结果可靠性成疑，且该过程高度依赖参数、无系统流程。
  - **直接计算的替代路线与空白**：此前有直接计算 AHC 的实现（LmtART 包，基于 FP-LMTO 基组），但 WIEN2k 使用的 FP-LAPW 基组被公认为最精确，且 WIEN2k 用户群最大——直接消费 WIEN2k 输出的 AHC/ANC 代码此前缺位，C-BerryTrans 填补此空白。
  - **工程动机**：AHC/ANC 通常需 400×400×400 以上 k 网格收敛；先前研究（原文引文献 [44]）表明 C++（OpenMP）并行优于 Python（multiprocessing），编译型可执行文件远快于解释型语言；二进制存储相比格式化文本可将文件体积缩小约 10–15 倍（原文明确"about 10-15 times"）。
  - **公式体系**：AHC 为 Ω 在整个 BZ 的积分并以 Fermi–Dirac 分布 fₙ(k) 加权（原文式 1）；ANC 在 Xiao 等人的框架下以熵函数核加权（原文式 2）。内在机制仅在清洁至中等脏极限有物理意义（Onoda–Sugimoto–Nagaosa 分类，原文引文献 [30]），脏极限由 skew scattering/side jump 等外在机制主导，本框架不含；且公式更适合低温区，300 K 下的散射机制未被捕获，与实验比较时须注意（原文也指出已有研究用式 1、2 做过室温计算，引文献 [22, 31, 32]）。
  - **SOC 的必要性**：SOC 为零时上下自旋子系统各自由实哈密顿量支配，Ωⁿ_μν(k) = −Ωⁿ_μν(−k)，式 1、2 积分消失——自旋通道自发破缺的时间反演对称性无法传递到轨道通道。故 AHC/ANC 计算必须包含 SOC，C-BerryTrans 设计即如此。

  ## 研究方法

  本文属**方法密度高**的论文（核心贡献即代码与计算流程），按方法卡格式整理如下。

  ### 方法卡：免插值 Berry 曲率 → AHC/ANC 第一性原理流水线（C-BerryTrans）

  **原理**：从 WIEN2k（FP-LAPW 基组）的 SOC 自洽计算输出直接抽取能带本征值 Eₙ 与动量矩阵元 ⟨ψ_nk|p_μ|ψ_n'k⟩，用 Kubo 型公式显式计算 Berry 曲率张量（原文式 3）：

  Ωⁿ_μν(k) = −(ℏ²/m²) Σ_{n'≠n} 2 Im[⟨ψ_nk|p_μ|ψ_n'k⟩⟨ψ_n'k|p_ν|ψ_nk⟩] / (Eₙ − Eₙ')²

  再对全 BZ 做离散化积分：AHC 以 fₙ(k) 加权求和 Σ_{n,k} fₙ(k)Ωⁿ_μν(k)（原文式 1），ANC 以熵核 [(Eₙ−E_F)fₙ(k) + k_B T ln(1+exp((Eₙ−E_F)/(−k_B T)))] 加权（原文式 2）。无 Wannier 插值，消除插值误差。数值处理上：能差低于 1E-8 Rydberg 的能带对按简并处理、其 Ω 贡献成对相消故显式排除，避免外尔点等处能分母发散引起的数值不稳定；动量矩阵元不满足与能量相同的不变性，故 Ω 在**全 BZ**（非不可约区）逐 k 点计算。

  **参数表（均出自原文）**：

  - 输入流水线变量（C-BerryTrans.input）：`case`（WIEN2k 目录名，须含 SOC 自洽结果）、`struct num`（结构编号 1–11，覆盖立方原胞/面心/体心、四方原胞/体心、六方原胞、正交原胞/底心/体心/面心、三方原胞）、`chemical potential`（ω 中心值，单位 Rydberg）、`emax`/`emin`/`estep`（ω 窗口上下界与步长，单位 meV）、`Tmin`/`Tmax`/`Tstep`（温度范围与步长，单位 K）、`spin pol`（1=自旋极化，0=非极化；SOC 恒含）、`kmesh`（如 `400 400 400`）、`shift in k`（1=网格平移避开高对称点，0=不平移）、`NUM THREADS`（OpenMP 线程数）、`num kp at once`（每线程每次处理的 k 点数，控 RAM）、`calc energy min`/`calc energy max`（相对 chemical potential 的能量窗口，单位 meV）、`calcEnSuitCheck`（1=启动 TAPEWF 错误预检，强烈推荐）、`property`（1=AHC，2=ANC）、`band`（0=常规全 BZ 积分；1=k 路径分辨模式）、`berryTrans plot at T`（绘图温度，K）。
  - 计算设置：k 网格在原始倒格矢 (g₁,g₂,g₃) 的 0–1 区间均匀剖分后按 Cracknell 约定转换到笛卡尔坐标，输出 WIEN2k 兼容的 case.klist 格式；`klist gen div` 模块为全 BZ 生成 k 列表（当前版本不生成 IBZ 网格）；NUM THREADS>1 时 k 列表均分为 case.klist1…case.klistNUM THREADS 分配到 process_1…process_NUM THREADS 子目录并行。
  - 推荐能量窗口判据：300 K 以下 AHC/ANC 取 ω 附近 **±1.5 eV** 能量区间即可涵盖相关能带（原文"not more than ± 1.5 eV"）；实用起点建议 ±0.5 eV，出现 TAPEWF 警告再逐步扩大；窗口必须保证每个 k 点至少有一条能带，否则 WIEN2k 报错，须终止重设（先算 DOS、再查高对称路径能带确认）。
  - 计算模式：`band=0` 全 BZ 稠密网格 + 积分出 AHC/ANC；`band=1` 沿用户自定义高对称 k 路径计算 Ω 加权的 AHC/ANC 贡献（费米权重或熵权重），不做 BZ 积分，用于分析能带交叉/色散特征与拓扑响应的微观关联。
  - 数据管理：band 分辨 Ω 以二进制 data.bin 存储（去格式化信息，体积约缩小 10–15 倍）；重计算（Ω）与轻后处理（postBerryTrans，任意 T、ω 窗口内单次运行扫描）解耦；后处理在过大的 T/ω 窗口下会出现 `free(): invalid size` 错误，缩小窗口即可（原文 Fig. 2，为代表性结果）。
  - 可视化模块：berryTrans_plot.py，交互式绘制 Ω_μν(k)×Fermi 分布或 Ω_μν(k)×熵分布在 k 空间的分布（μ,ν = x, y, z）。
  - 代码规模与许可：16 个 C++ 模块 + Makefile + C-BerryTrans.input + berryTrans_plot.py；外部库仅 cmath, vector, chrono, omp.h, cstdlib, string；GNU GPL 3.0；仓库 https://sourceforge.net/projects/c-berrytrans/。

  **适用边界**：
  - 仅描述**内在**贡献，物理上仅适用于清洁至中等脏极限（准粒子良好定义）；脏极限由 skew scattering、side jump 主导，不在框架内。
  - 更适合低温区；300 K 下散射机制未捕获，室温结果与实验直接比较须谨慎（尽管已有文献用同公式做室温计算）。
  - 要求 SOC 自洽计算作为输入；SOC 为零时横向响应严格为零。
  - 能量窗口过小会导致 TAPEWF 错误与段错误，calcEnSuitCheck=1 预检可避免；窗口不得完全落在能隙内。
  - 当前版本 klist_gen_div 不生成 IBZ 网格，全 BZ 计算；简并能带对按 1E-8 Rydberg 阈值剔除。

  **代表作**：V. Pandey, S. K. Pandey, arXiv:2509.24071（C-BerryTrans 本体，2025/2026 v3）；方法学参照 Xiao 等人的 ANC 熵加权框架（原文引文献 [21, 26]）。

  ## 主要发现与核心结论

  （原文全文在后处理章节之后截断，以下定量结果全部取自原文摘要与引言，数值原样保留。）

  - **Fe**：σᴬᴴᶜ_xy ≈ 775 S/cm（0 K）、≈ 744 S/cm（300 K），与文献报道值定量吻合。
  - **Fe₃Ge**：σᴬᴴᶜ_xy = 311 S/cm（300 K）。
  - **Co₂FeAl**：|σᴬᴴᶜ_xy| ≈ 56 S/cm（2 K）。
  - **Pd**：室温 |αᴬᴺᶜ_xy| ≈ 0.97 A K⁻¹ m⁻¹。
  - **Fe₃Al**：T ≤ 500 K 范围内 |αᴬᴺᶜ_xy| 最大值 ≈ 2.83 A K⁻¹ m⁻¹。
  - **Co₂FeAl**：αᴬᴺᶜ_xy ≈ 0.10 A K⁻¹ m⁻¹（300 K）。
  - 上述五材料 AHC/ANC 基准结果"show excellent agreement with previously reported data"，验证了免插值路线的数值精度。
  - **架构性结论**：先一次性算出 band 分辨 Ω 并存入二进制文件，之后对任意 (T, ω) 窗口的 AHC/ANC 只需快速后处理，单次运行即可扫描宽温区宽化学势区——这改变了 WannierTools"单温度逐次计算"的工作模式，主要计算时间花在 Ω 上，后处理相对快得多。
  - **微观洞察能力**：k 路径分辨模式（band=1）配合可视化模块，可展示特定能带交叉与色散特征如何贡献 Ω 驱动的 AHC/ANC，为拓扑材料探索提供微观图像。
  - **方法学结论**：对 300 K 以下输运，±1.5 eV（相对 ω）能量窗口足以捕获相关能带贡献，能带能量差大的能带对 Ω 贡献可忽略，提供了可操作的计算降本判据。

  ## 潜在研究方向

  - **外在机制缺失**：框架不含 skew scattering / side jump，脏极限材料及 300 K 以上温区与实验定量对照时会有系统偏差；如何把外在机制或有效弛豫时间近似纳入此类免插值流水线是开放问题。
  - **IBZ 对称性利用未实现**：当前 Ω 在全 BZ 逐点计算（因动量矩阵元不满足本征值的不变性），若能严格利用对称性缩减计算域，400×400×400 网格的成本还可大幅下降。
  - **后处理鲁棒性**：过大 T/ω 窗口触发 `free(): invalid size` 内存错误，说明后处理模块的内存管理有边界条件，大规模高通量批跑时需注意窗口分片。
  - **截断限制**：本次蒸馏获得的全文在后处理章节末尾截断，基准计算的技术细节（k 网格收敛测试、与文献逐值对比表、Section VI 的 k 路径模式细节）未见原文，引用具体对比数据时须回查全文。
  - ** beyond 输运**：Ω 的 k 空间分布数据（data.bin + 可视化模块）本质上是动量空间拓扑结构的资产，可外推到其他 Ω 派生量（如反常热电、轨道磁化、强场下的能带内/间相干效应）的计算管线，代码本身是否易扩展至此未见讨论。

  ## 与林赛研究的关联

  - **量子几何与 HHG 的接口**：Berry 曲率是布洛赫能带量子几何的核心量。强场驱动 HHG 中，能带间的强场动力学（带内加速、带间极化）对量子几何（Ω 与量子度规）敏感；本工具能以第一性原理保真度产出候选材料的 Ω(k) 分布与 k 路径分辨贡献，可为我们筛选/论证"量子几何显著"的强场响应材料提供输运侧的独立佐证（AHC/ANC 是 Ω 的积分探针）。
  - **暂态量子相的光学读出课题**：`key-transient-quantum-phase-optical-20260726` 若涉及拓扑相/交变磁相的光学指纹，ANC 的费米面选择性（只敏感费米能附近 Ω）正好对应"暂态相变后费米面重构"的探测逻辑——ω 扫描的 ANC(T, ω) 输出即是一张"费米能附近的 Ω 谱"，可作为光学读出之外的互补表征路线写进方案。
  - **莫尔与交变磁方向**：交变磁体（altermagnet）的动量空间自旋劈裂与 Ω 结构近年是热点；本工具对自旋极化体系（spin pol=1，SOC 恒含）的直接支持，加上 Heusler 体系的基准验证（Co₂FeAl 等），适合作为交变磁候选材料 AHC/ANC 的初筛工具，与我们的方向词直接挂钩。
  - **方法素材入库**：方法卡中的能量窗口判据（±1.5 eV / 300 K 以下）、简并阈值（1E-8 Rydberg）、k 网格基准（400×400×400）、窗口预检流程（DOS → 高对称路径能带 → calcEnSuitCheck）都是可直接复用的计算操作规范，可经 methods_settle 沉淀进 `knowledge/wiki/methods/`，供课题方案写作的"操作性五问"之计算侧条目引用。

  ## 来源
  - 蒸馏自全文（deep-read）

<!-- methods-backfill:v1 -->

## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：C-BerryTrans：免 Wannier 插值的 Berry 曲率→AHC/ANC 第一性原理流水线（WIEN2k FP-LAPW）

**原理**：直接从 WIEN2k（FP-LAPW 基组）SOC 自洽输出抽取本征值与动量矩阵元，按 Kubo 型公式显式计算 Berry 曲率张量 Ωⁿ_μν(k)（能差 <1E-8 Rydberg 的简并带对显式剔除防发散），全 BZ 离散积分得 AHC（Fermi-Dirac 权重）与 ANC（熵核权重，费米面选择性）；重计算（Ω，重）与后处理（任意 T/ω 扫描，轻）解耦，k 路径分辨模式（band=1）定位能带交叉对输运的微观贡献——绕开 Wannier 插值误差的最大不确定度来源。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| k 网格基准 | 400×400×400（全 BZ；动量矩阵元无对称不变性，不用 IBZ） | 研究方法·参数表 |
| 能量窗口判据 | 300 K 以下 ±1.5 eV（相对 ω）足够；实用起点 ±0.5 eV 出 TAPEWF 警告再扩；窗口不得全落能隙 | 研究方法·推荐能量窗口判据 |
| 简并剔除阈值 | 1E-8 Rydberg（能带对成对相消处理） | 研究方法·原理 |
| 输入流水线变量 | case/struct num(1–11)/chemical potential(Ryd)/emax·emin·estep(meV)/Tmin·Tmax·Tstep(K)/spin pol/kmesh/shift in k/NUM THREADS/num kp at once/calcEnSuitCheck(1=预检)/property(1=AHC,2=ANC)/band(0=全BZ,1=k路径) | 研究方法·参数表 |
| 数据管理 | band 分辨 Ω 存二进制 data.bin（体积缩小约 10–15 倍）；后处理窗口过大会报 free(): invalid size，缩小窗口分片 | 研究方法·数据管理 |
| 基准验证 | Fe σ_xy≈775 S/cm(0 K)/744 S/cm(300 K)；Fe₃Ge 311 S/cm(300 K)；Co₂FeAl |σ|≈56 S/cm(2 K)；Pd |α|≈0.97 A K⁻¹m⁻¹(室温)；Fe₃Al 最大 2.83 A K⁻¹m⁻¹(≤500 K) | 主要发现 |
| 代码规模/许可 | 16 个 C++ 模块（仅 cmath/vector/chrono/omp 等标准库）+ berryTrans_plot.py；GNU GPL 3.0 | 研究方法·代码规模 |

**适用边界**：仅内在机制（清洁至中等脏极限）；脏极限 skew scattering/side jump 不在框架内；更适合低温区，300 K 散射机制未捕获，室温对比须谨慎；必须 SOC 自洽输入（SOC=0 时横向响应严格为零）；klist 不生成 IBZ；后处理 T/ω 窗口过大触发内存错误需分片。
**代表作**：Xiao et al.（ANC 熵加权框架）；Onoda–Sugimoto–Nagaosa（内在机制极限分类）
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry 曲率]]
- [[key-transient-quantum-phase-optical-20260726]]
- [[交变磁体]]
- [[强场驱动]]
- [[自旋劈裂]]
- [[量子几何]]
- [[量子度规]]
<!-- /linsai-wikilinks -->
