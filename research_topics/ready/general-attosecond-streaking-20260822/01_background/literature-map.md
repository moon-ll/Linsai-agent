# 背景调研：阿秒条纹技术文献地图

- 课题 ID: general-attosecond-streaking-20260822
- 任务: B1 背景调研（researcher profile）
- 产出: 01_background/literature-map.md
- 检索日期: 2026-11-18
- 溯源约定: 每条文献末行 `source: <KB页名|raw/papers路径|检索池>`，全部同步写入 `04_references/references.bib`
- 元数据核验: 本轮用 arXiv API（export.arxiv.org，id_list 与 search_query 两种形式）+ CrossRef REST API（api.crossref.org/works/{DOI}）逐条实测；arXiv API 单次 503/429 时改用 CrossRef 与本地 raw 页互补

---

## 〇、领域脉络速览（本节置于文首，便于 B4 组装节选携带文献锚点与 KB 链接）

### 脉络主干（六段式，每段带文献锚点）

| 阶段 | 时期 | 核心进展 | 文献锚点 |
|---|---|---|---|
| ① 范式起点 | 2002–2005 | 条纹相机建立"发射时刻→动量"映射；FROG-CRAB 建立条纹谱图与 FROG 的数学等价，并引入中心动量近似（CMA）——本课题要修正的对象本体 | [ref:itani2002attosecond] [ref:mairesse2005frequency] |
| ② 语义翻转 | 2010 | 证明 FROG 检索出的是电子时域波包 χ(t) 而非 XUV 包络 E_XUV(t)；CMA 在 Cooper 极小处完全失效；由此建立"条纹=量子相位探针"的路径 | [ref:yakovlev2010attosecond] |
| ③ 偶极相位系统性 | 2010–2016 | 相对延迟实验确认偶极相位可引入数十阿秒且有非平凡能量依赖；里德堡波包方案用角积分结构性消除偶极相位，并以多态波包冗余信息实现内在自洽检验 | [ref:schultze2010delay] [ref:pabst2016eliminating] |
| ④ 跨能区扩展 | 2017 | 水窗区（≤350 eV）首次条纹测量，孤立脉冲 322 as；揭示截面骤降、多壳层同时电离、啁啾破坏检索保真度；给出"带宽/条纹位移比"算法边界 | [ref:cousin2017attosecond] |
| ⑤ 电子动力学探针化 | 2022–2026 | 多通道相位可测、CLC 延迟分解框架、rainbow 连续相位反演、条纹内连续-连续角动量倾向提取——条纹从表征工具变为量子相位探针 | [ref:peschel2022attosecond] [ref:shi2024photoelectron] [ref:ortmann2024understanding] [ref:kheifets2026rainbow] [ref:gao2026hidden] |
| ⑥ 当代反演前沿 | 2025–2026 | AO-FROG 复值门修正（相位+振幅调制并存）、通用 in-line 波形表征、解析方差传播、协方差时间检索、渐近近似破缺量级实测 | [ref:xia2026complex] [ref:leung2025universal] [ref:ji2025quantitative] [ref:wang2024covariance] [ref:rajendran2026breakdown] |

### 关联的知识库页（全清单见 §3，链接均指向 knowledge/wiki/ 实存页）

方法与专题：[[阿秒计量方法体系]]（条纹术/RABBITT/Wigner 时延三块，含四步条纹反演流程、边带相位分解公式 φ_{2q} = 2φ_{2q±1} + Δφ_W + Δφ_cc + Δφ_XUV、角分辨 EWS 计算栈）、[[FROG]]、[[RABBITT]]、[[RABBIT与RABBITT]]、[[VMI_双色_RABBIT_光电子谱]]、[[表征方法]]、[[阿秒科学]]、[[强场物理]]、[[强场电离量子轨道方法]]。

概念：[[阿秒延迟测量]]、[[阿秒条纹与瞬态吸收谱联用观测激发态偶极跃迁的相对符号]]、[[阿秒脉冲串]]、[[阿秒脉冲合成]]、[[阿秒瞬态吸收]]、[[RABBIT]]、[[rainbow-RABBITT]]、[[transient-quantum-phase]]、[[Attosecond-quantum-optics]]、[[CEP稳定]]、[[TDSE]]、[[VMI]]、[[水窗口]]、[[中红外驱动HHG]]、[[3_μm_中红外驱动窗口]]、[[隧穿时间]]。

论文页：[[1006.1827]]、[[1602.08144]]、[[1710.02208]]、[[general-attosecond-streaking-20260822]]（课题本体页，另见 `wiki/projects/NSFC-强场超快/{versions,reports,proposals}/`）。

---

## 〇、检索方法与数据质量声明

### 0.1 检索路径

| 路径 | 工具 | 覆盖 |
|---|---|---|
| 本地知识库页面 | `knowledge/wiki/papers/`（3875 个 paper 页） | 已有五维蒸馏笔记、方法卡、关联概念 wikilink |
| 本地原始条目 | `knowledge/raw/papers/` | frontmatter 含 arxiv_id / authors / year / journal / abstract / tldr，为 KB 页的一手元数据底座 |
| 既有检索池 | `04_references/references-source.md`（43 条）、`01_background/reference-metadata-crossref.md`（40 条 CrossRef 实测回录） | 本课题前序轮次已建立的著录池，A4 溯源主依据 |
| arXiv API | `export.arxiv.org/api/query?id_list=` 与 `search_query=` | 近 24 个月新检索，命中 115 条 `abs:attosecond AND abs:reconstruction` |
| CrossRef API | `api.crossref.org/works/{DOI}` | 题名/期刊/卷期/文章号/年份/首作署名逐条比对 |

### 0.2 关键发现：知识库存在 3 处元数据缺陷（已在本轮修正，严禁沿用旧 ID）

本轮实测发现知识库与既有检索池中的部分 arXiv 编号与真实论文不对应，若直接沿用会产出错误引用。已逐条核验并给出正确标识：

| 知识库/旧记录中的 ID | 实测结果 | 正确标识 | 处置 |
|---|---|---|---|
| `2403.05073`（KB 记为 rainbow retrieval） | arXiv 实为 "Private Count Release: A Simple and Scalable Approach for Private Data Analytics"（cs.CR, Ryan Rogers, 2024-03-08） | 该文为期刊论文，无 arXiv 预印本；正确著录为 Phys. Rev. A 113(4) 043103 (2026)，DOI 10.1103/9jcm-8gd8 | 本文件按 DOI 著录；引用时不得写 arXiv:2403.05073 |
| `2405.06275`（KB 记为 Ji & Wörner RABBIT 不确定度） | arXiv 实为 "Pruning as a Domain-specific LLM Extractor"（cs.CL, Nan Zhang et al., NAACL 2024 Findings） | J. Phys. B 58, 135601 (2025)，DOI 10.1088/1361-6455/adea62（CrossRef 实测） | 本文件按 DOI 著录；引用时不得写 arXiv:2405.06275 |
| `2312.14174`（KB 记为 Evaluating the accuracy of attosecond streaking time-delay measurements） | 该 KB 页正文实为超导约瑟夫森结负微分电阻论文（Pedersen et al., Physica C 2014），元数据与正文严重不匹配，且 KB 已在页内显式标注此冲突 | 既有检索池著录为 "Evaluating the accuracy of attosecond streaking time-delay measurements"（Kasmi et al., 2023），但本轮未取得可核验的 arXiv/CrossRef 对应 | 本文件降级处理：列入"待核验"，不作为 A1 支撑条目 |

**教训**：知识库 `wiki/papers/` 层的 `arxiv_id` 字段并非全部经过 arXiv API 验证；凡要在课题报告中承重引用的条目，必须回到 `raw/papers/` frontmatter + arXiv/CrossRef 实测双重确认。

### 0.3 覆盖声明

- 本文件只收"检索池/知识库中确有记录"或"本轮 arXiv/CrossRef 实测命中"的文献，无凭记忆补写条目。
- 数值一律保留原值并注明出处页；无法核实者标注"摘要级未给"，不填充。
- 检索截止 2026-11-18。

---

## 一、领域地图

### 1.1 范式起点：条纹相机与 FROG-CRAB 的诞生（2002–2005）

阿秒条纹技术的基本图像在 2002 年确立：XUV 光子电离产生的光电子在共线少周期 IR 场中受到矢势 A(t) 调制，末态动量 p(t_r) ≈ p₀ − A(t_r)，条纹轨迹把"发射时刻"直接映射为"动量"，因此条纹场是一把超快快门。脉冲表征侧，Itatani 等把这一图像写成"attosecond streak camera"[ref:itani2002attosecond]，Mairesse 与 Quéré 则把条纹谱图与频率分辨光学门控（FROG）作形式类比，引入"中心动量近似（CMA）"并给出 FROG-CRAB 检索算法[ref:mairesse2005frequency]——这是后续一切脉冲反演的方法学母体。该阶段的隐含假设是：相关跃迁矩阵元在脉冲带宽内近似为常数，于是重建结果被视为 XUV 脉冲复包络。

对本课题的意义：任何"条纹重构=脉冲表征"的表述都隐含这一近似，它是后续所有失效讨论的共同源头，也是本课题要剥离的对象。

### 1.2 语义翻转：条纹重构的是电子波包而非光脉冲（2010）

Yakovlev 等证明，在一般情形下 FROG 检索出的"脉冲"并非 XUV 复包络 E_XUV(t)，而是出射光电子的时域波包 χ(t)[ref:yakovlev2010attosecond]。他们把主方程无近似地改写为以 χ(t) 为"脉冲"、以无穷级数和为"门"的 FROG 形式，并指出中心动量近似在 Cooper 极小（D(p₀)=0）处完全失效。由此确立了两条路径：一是把 χ̃(p) ∝ D(p)·Ẽ_XUV(p²/2−p₀²/2) 作为量子相位探针——先在矩阵元已知的原子上标定 XUV 谱相位，再对目标体系二次测量反推 D(p) 的相位[ref:yakovlev2010attosecond]；二是把 CMA 失效本身确立为方法学边界，成为"剥离靶材相关相位"这一课题命题的理论起点。

对本课题的意义：这一翻转是本课题三篇核心文献中第一篇的立论基础——条纹与量子相位不是两件事，而是同一测量的两种读法。

### 1.3 偶极相位的系统性与"剥离"诉求（2010–2016）

相对电离延迟实验确立了一个硬事实：束缚-连续与连续-连续跃迁的偶极相位可引入数十阿秒延迟，且具有非平凡能量依赖[ref:schultze2010delay]。这一系统性误差直接污染 FROG-CRAB/PROOF 的脉冲相位重建。Pabst 与 Dahlström 提出用相干里德堡波包量子拍频的替代表征方案[ref:pabst2016eliminating]：先激光制备相干里德堡波包，再用待测 XUV 电离，通过角度积分消除偶极相位，并以多态波包的冗余谱信息做内在自洽检验。三点关键技术事实：球对称母离子（碱金属 K⁺、Ne⁺）+ 实数化径向波函数使偶极矩阵元为实数；角度积分借球谐正交性消去散射相位 η_{Lf}；N>2 能级波包产生 C(N,2) 个拍频，满足 φ(j₁,j₃)=φ(j₁,j₂)+φ(j₂,j₃) 约束。

对本课题的意义：这是"偶极相位可被结构性消除而非仅能标定"的第一个可操作方案，为本课题的角积分解耦模块提供了物理依据。

### 1.4 跨能区扩展：水窗软 X 射线条纹与 FROG-CRAB 的保真度危机（2017）

Cousin 等首次在水窗波段（284–543 eV）实现阿秒条纹测量，驱动源为 1850 nm sub-2-cycle CEP 稳定脉冲[ref:cousin2017attosecond]。该工作同时交付了成果与警告：孤立脉冲宽度上限 322 as（当时最短 SXR 脉冲报道）；但光电离截面比 XUV 低数个量级、多电子壳层同时访问使条纹图样复杂化、>200 eV 的 attochirp 补偿用传统材料方案（Zr/Al/Ne 箔）因透射可忽略而不可行。其算法层面的定量结论最为致命：当带宽 ≤60 eV 且条纹场 10¹¹ W/cm² 时 FROGCRAB 与 LSGPA 均能满意重建；当带宽扩展至 100 eV 而条纹场仍为 10¹¹ W/cm² 时两种算法均失效；将条纹场提升至 10¹² W/cm² 后两者均成功——即超宽带重建的关键约束是条纹位移量需与带宽量级相当。

对本课题的意义：这给出了"跨能区稳健性"问题的第一个可量化边界（带宽/条纹位移比），本课题的多通道修正确有明确的适用区间设计需求。

### 1.5 从脉冲表征到电子动力学探针：多通道与关联效应的显式建模（2022–2026）

随着单通道假设被打破，研究重心转向把多通道、角分辨与多电子关联显式纳入条纹反演。Peschel 等用双光子干涉测量 Ne 外层光电离中不同角动量通道的相位与幅值，揭示通道间干涉[ref:peschel2022attosecond]；Shi 与 Thumm 进一步从头计算氦 XUV-IR 条纹谱，区分直接电离与 shake-up（残余离子 n=2,3）通道，量化残余离子-光电子纠缠对条纹延迟的贡献[ref:shi2024photoelectron]；Ortmann 与 Landsman 的教程把条纹总延迟分解为纯电离延迟与 Coulomb-laser-coupling（CLC）项，并界定二者可干净分离与分解失效的条件[ref:ortmann2024understanding]。Kheifets 等的 rainbow retrieval 把"逐能点拟合条纹中心位移"改为"对整条宽带轨迹做连续相位反演"，在 He 1s / Ar 3p / Xe 4d 三种基准靶上分别解析 Coulomb 相、Cooper 极小与巨型形状共振结构[ref:kheifets2026rainbow]。Gao 等进一步发现条纹本质多光子，用反演奇筛选分离出 P₁/P₃ Legendre 分量，其复系数给出有效 s/d 双光子振幅比，量化了连续-连续角动量倾向[ref:gao2026hidden]。

对本课题的意义：这一阶段的进展恰恰是在回答"剥离靶材相关相位"的具体技术细节——CLC 项、多通道交叉项、角依赖、关联修正，逐项对应本课题误差预算中的条目。

### 1.6 反演方法的当代前沿：替代算法与自参考机制（2025–2026）

近 24 个月的重心明显转向反演算法本身。Xia 等把 FROG 扩展为"全光学频率分辨光学门控"（AO-FROG），证明弱微扰场在 HHG 过程中同时引起相位与振幅调制，因此需要复值门函数，实验用 2.26 μm sub-cycle 驱动表征了 100–180 eV 的氩孤立阿秒脉冲，重建给出约 300 as 时长及谱相位[ref:xia2026complex]。Leung 等提出基于任意非线性响应的通用 in-line 波形表征（CRIME / lazyCRIME），在标准工作站上数分钟达到阿秒精度，并演示了在 ATAS 实验中的非侵入同步表征[ref:leung2025universal]。Ji 与 Wörner 给出光谱重叠条件下 RABBIT 阿秒时延提取的解析方差传播公式，并证明 global-fit 与 complex-fit 在最小二乘意义下严格等价[ref:ji2025quantitative]。Wang 等给出角分辨脉冲式条纹的协方差分析框架，指出动量分布位移在脉冲式条纹区建立了 dressing-free 与 dressed MD 之间的紧连接，由此产生跨不同 MD 形状共有的普适协方差结构，可从中提取时间信息[ref:wang2024covariance]。Rajendran 等则用非相邻 XUV 谐波自参考方案实测检验双色调制中各向同性渐近近似的破缺，观测到数十毫弧度（数阿秒量级）偏离并由全维模拟归因于离心势项[ref:rajendran2026breakdown]。

对本课题的意义：这段前沿同时给出两条对本课题有直接操作价值的东西：一是"相位与振幅调制同时存在"这一 AO-FROG 结论，正是本课题要修正 FROG-CRAB 单通道假设时必须处理的另一半；二是协方差框架与解析方差传播，为本课题的误差预算提供了可借用的统计骨架。

---

## 二、核心文献组

> 共 16 篇，其中近 24 个月（2024-11 之后）8 篇，满足 A1 的"≥8 篇 + 近 24 个月 ≥3 篇"。
> 关系一句话为与本课题（阿秒条纹 → 量子相位测量）的直接接口。
> 关键数值/结论原样保留并注明出处页。

### [ref:itani2002attosecond] Itatani J, Quéré F, Yudin G L, et al. Attosecond streak camera

- **出处**: Physical Review Letters, 2002, 88(17): 173903. DOI: 10.1103/PhysRevLett.88.173903
- **关系**: 条纹相机的理论原点，给出"发射时刻 → 末态动量"映射公式，是全课题的物理母式。
- **关键结论**: 光电子末态动量在 IR 场下按 p(t_r) = p₀ − A(t_r) 调制，条纹轨迹因而直接编码发射时刻；此即"IR 条纹场作为超快快门"的原始表述。
- **出处页**: `knowledge/wiki/papers/` 检索池条目 [20]（references-source.md）

### [ref:mairesse2005frequency] Mairesse Y, Quéré F. Frequency-resolved optical gating for complete reconstruction of attosecond bursts

- **出处**: Physical Review A, 2005, 71(1): 011401. DOI: 10.1103/PhysRevA.71.011401
- **关系**: FROG-CRAB 算法的原始文献，是本课题要修正的对象本体（中心动量近似 CMA 即源于此）。
- **关键结论**: 建立条纹谱图与 FROG 谱图的数学等价，为完整重建孤立阿秒脉冲引入频率分辨光学门控与中心动量近似两条关键假设。
- **出处页**: 检索池条目 [5]（references-source.md）

### [ref:yakovlev2010attosecond] Yakovlev V S, Gagnon J, Karpowicz N, et al. Attosecond streaking enables the measurement of quantum phase

- **出处**: Physical Review Letters, 2010, 105(7): 073001. DOI: 10.1103/PhysRevLett.105.073001；arXiv:1006.1827（本地 `knowledge/raw/papers/2010-1006.1827-*.md`）
- **关系**: 本课题核心文献之一——论证条纹测量可直接重构光电离释放电子波包的量子谱相位，把阿秒条纹从脉冲表征工具拓展为电子动力学探针。
- **关键结论（原样保留，出处：KB 页 `wiki/papers/2010-1006_1827-*.md` 精读笔记）**:
  - FROG 检索出的脉冲 P₂(t) = χ(t)，而非此前认为的 XUV 包络 P₁(t) = E_XUV(t)；χ(t) = i/π ∫₀^∞ ⟨p|Ψ(t)⟩ e^{ip₀²/2 t} dp。
  - 中心动量近似在 D(p₀) = 0（Cooper 极小）处完全失效：图1(c) 与真实谱图图1(a) 几乎无相似性，而以 χ(t) 为脉冲的重建图1(d) 与真实谱图高度一致。
  - 数值验证设置：模拟 Ar 3s Cooper 极小 42.5 eV、p₀ = 1.77 a.u.；XUV 高斯包络 FWHM = 150 as；条纹激光 FWHM = 5 fs、中心波长 750 nm、矢势峰值 0.1 a.u.
  - 关系式：χ̃(p) ∝ D(p)·Ẽ_XUV(p²/2 − p₀²/2)，故测量 χ̃ 的相位即得 D(p) 的相位（至一常数相位）。
  - 门函数级数 G₂(t) = [∑ₙ aₙ ∂ⁿg(p,t)/∂tⁿ]|_{p=p₀}，近似为 G₂(t) ≈ e^{iΦ(p₀,t)}，且此路径完全不触碰 D(p) 本身。
- **对本课题**: 这是"剥离靶材相关相位"命题的理论源头——D(p) 与 E_XUV(p) 在 χ̃ 中纠缠，任何不做剥离的重建都会把靶材相位误记为脉冲相位。

### [ref:schultze2010delay] Schultze M, Fieß M, Karpowicz N, et al. Delay in photoemission

- **出处**: Science, 2010, 328(5986): 1658-1662. DOI: 10.1126/science.1189401
- **关系**: 确立偶极相位/相对延迟的实验量级，是本课题"剥离靶材相关相位"的动机来源。
- **关键结论**: 测得 Ne 价壳 2s/2p 相对光发射延迟 ±21 ± 5 as；该值与多电子理论（HF/RPAE/R-matrix/B-spline）存在至今未消解的系统性张力，构成"测量到什么相位"这一争议的起点。
- **出处页**: `knowledge/wiki/method-topics/阿秒计量方法体系.md` 案例 1 与 §2.4 适用边界

### [ref:pabst2016eliminating] Pabst S, Dahlström J M. Eliminating the dipole phase in attosecond pulse characterization using Rydberg wave packets

- **出处**: Physical Review A, 2016, 94(1): 013411. DOI: 10.1103/PhysRevA.94.013411；arXiv:1602.08144（本地 `knowledge/raw/papers/2016-1602.08144-*.md`，read_status: deep-read）
- **关系**: 本课题核心文献之一——提出基于相干里德堡波包量子拍的替代表征方案，用角积分消除偶极相位依赖，并借多态波包冗余谱信息实现内在自洽检验。
- **关键结论（原样保留，出处：KB 页 `wiki/papers/2016-1602_08144-*.md` 方法卡）**:
  - 相对 FROG-CRAB 与 PROOF 的三点关键差异：(i) 中间态是束缚态；(ii) pump 与 probe 是序贯的；(iii) 光电子测量对全部探测角积分。
  - 孤立脉冲验证案例：ω₀ = 74 eV、光谱 FWHM 7.4 eV、Fourier 极限 247 as；线性啁啾 φ_X(ω) = 100 as²(ω−ω₀)²；二次啁啾 φ_X(ω) = 100 as³(ω−ω₀)³。
  - K 两能级波包 4p–5p：ε₅ₚ − ε₄ₚ = 1.36 eV；三能级波包 4p–7p–8p：ω₈₄ = 2.26 eV、ω₇₄ = 2.12 eV、ω₈₇ = 0.14 eV。
  - 脉冲串验证：第 48、49、50 次谐波（800 nm），每谐波光谱 FWHM δω = 400 meV；相邻谐波相对相位差定义值 48–49 次间 −π/4、49–50 次间 π/3；从 73.7 eV 与 75.3 eV 处提取的拍频相位为 −0.34π 与 0.49π。
  - 关联效应：RPAE 计算下 K 4p–5p 角积分谱（70–80 eV）关联诱导群延迟斜率约 −0.052 as/eV，方向光电子谱为 0.12 as/eV（方向谱超过两倍且符号相反）；角积分谱中心延迟约 6 as 仅为常数偏移。
  - Ne Fano 共振情形（2s⁻¹3s，寿命 6.4 fs，Γ = 0.1 eV；脉冲 25.9 eV、508 as）：角积分谱关联诱导延迟 ≤ ±3 as，方向谱可达 −30 as。
  - 自检验：N=3 波包产生 C(3,2)=3 个拍频，完全满足 φ(4p,8p) = φ(4p,7p) + φ(7p,8p)，与解析解精确吻合——作者称为现有超快脉冲重建方法中独一无二的能力。
  - K 4p–5p 在 HF 框架下角积分谱群延迟严格为零（理论精确值）；方向性谱因 Cooper 极小使相位在 20–90 eV 区间非单调变化 π/2，对应延迟约 80 as 量级。
- **对本课题**: 提供"偶极相位可结构性消除"的完整理论路径；但其自身残余项（K 的 RPAE 约 6 as 常数中心延迟需绝对定标、Ne Fano 的 interchannel coupling ≤ ±3 as、τ 时间零点稳定性要求高）为本课题误差预算提供了逐项参照量级。

### [ref:cousin2017attosecond] Cousin S L, Di Palo N, Buades B, et al. Attosecond streaking in the water window: A new regime of attosecond pulse characterization

- **出处**: Physical Review X, 2017, 7(4): 041030. DOI: 10.1103/PhysRevX.7.041030；arXiv:1710.02208（本地 `knowledge/raw/papers/2017-1710.02208-*.md`，read_status: deep-read）
- **关系**: 本课题核心文献之一——在水窗软 X 射线波段（高达 350 eV）首次实现条纹测量并表征出 322 as 孤立脉冲，同时揭示该能区光电离截面骤降、多电子壳层同时电离及阿秒啁啾会破坏传统 FROGCRAB 检索的保真度。
- **关键结论（原样保留，出处：KB 页 `wiki/papers/2017-1710_02208-*.md` 方法卡）**:
  - 首次水窗区阿秒条纹测量；孤立脉冲宽度上限 **322 as**（FROGCRAB 重建）；中心光子能量 ~250 eV（3d 壳层电离，电离势 94 eV → 电子能量 150 eV）；光谱带宽 >100 eV（理论上支持 20 as 脉冲宽度，远小于原子时间单位 24 as）；条纹位移 ~50 eV。
  - 驱动与装置：Ti:Sa 放大器 cryogenically cooled、2-stage、40 fs、7 mJ、1 kHz；OPA (TOPAS-HE) 3-stage white-light seeded、被动 CEP 稳定；1850 nm idler 45 fs；空芯光纤 + bulk 压缩后 0.4 mJ、12 fs、CEP stable、sub-2-cycle；HHG 焦点 54 µm、强度 4.3×10¹⁴ W/cm²、3 bar Ne 自由靶 <1 mm 作用区；SXR 通量 5.6×10⁵ photons/s（284–350 eV on target）；条纹场强度 3.2×10¹¹ W/cm²；ToF 谱仪 Stefan Kaasdorf ETF10、461 mm drift tube、E/ΔE = 50；采集 10 hours（300 counts/s）。
  - FROGCRAB 采样参数：δE = 0.34 eV、δτ = 5.9 as、N = 2048、Δτ = 12 fs、ΔE = 700 eV。
  - 算法保真度边界：带宽 ≤60 eV 且条纹场 10¹¹ W/cm² 时 FROGCRAB 与 LSGPA 均能满意重建；带宽扩展至 100 eV 而条纹场仍为 10¹¹ W/cm² 时**两种算法均失效**；条纹场提升至 10¹² W/cm² 后两者均成功——超宽带重建的关键约束是条纹位移量需与带宽量级相当。
  - attochirp 统计分辨阈值：attochirp 为 2500 as² 时几乎无法统计分辨，5000 as² 时可明确辨别。
  - 偶极发射相位：Kr 3d 在 243 eV 处 GDD = −10.7 as²（可忽略）。
  - 材料 GDD 补偿不可行：250 eV 脉冲补偿 2500 as² chirp 需 ~13 µm Zr 箔或 ~6 bar Ne（10 mm cell），但透射可忽略；**>200 eV 的 attochirp 补偿用传统方案不可行**。
  - 探测气体选 Kr 的理由：3d 壳层在 ~300 eV 光子能量下光电离截面相对较高；He 截面极低；Ne、Ar、Xe 多壳层重叠使解释复杂。
- **对本课题**: 本课题"跨能区稳健谱相位重构"命题的问题源头。它同时给出三重要求：截面骤降→采样/信噪比设计，多壳层同时电离→多通道修正必需，啁啾破坏检索→算法需自带啁啾鲁棒性。

### [ref:peschel2022attosecond] Peschel J, Busto D, Plach M, et al. Attosecond dynamics of multi-channel single photon ionization

- **出处**: Nature Communications, 2022, 13(1): 5205. DOI: 10.1038/s41467-022-32780-5；本地 `knowledge/raw/papers/2022-s41467-022-32780-5-*.md`
- **关系**: 证明单光子电离的多通道相位与幅值可被干涉测量，是本课题"多通道修正"模块的实验先例。
- **关键结论**: 利用双光子干涉技术测量 Ne 原子外层光电离中不同角动量通道的相位和幅值，揭示通道间干涉效应（出处：KB raw 页中文摘要，原样保留）。
- **对本课题**: 给出"通道间相位差 Δφᵢⱼ 是可观测量而非扰动"的实验依据——本课题方案中的交叉项 2√(S₁S₂)·cos(Δφ) 因此有可测量对象。

### [ref:shi2024photoelectron] Shi H, Thumm U. Photoelectron–residual-ion interaction in angle-resolved streaked shake-up ionization of helium

- **出处**: Physical Review A, 2025, 111(1): 013119. DOI: 10.1103/PhysRevA.111.013119；arXiv:2409.03622（本地 `knowledge/raw/papers/2024-2409.03622-*.md`）
- **关系**: 从头计算量化多通道电离与剩余离子纠缠对阿秒条纹延迟的贡献，是本课题多通道修正与角分辨修正的数值参照。
- **关键结论（原样保留，出处：KB 页 `wiki/papers/2024-2409_03622-*.md` 精读笔记）**:
  - 模型：全维双电子 TDSE（para-He 耦合径向分波，split-operator Crank-Nicolson）；XUV 90/100/110 eV、FWHIM 200 as、10¹² W/cm²；IR FWHIM 3 fs、4×10¹¹ W/cm²；40 个等间隔延迟覆盖 2 个 IR 周期。
  - 偶极选择规则：direct 仅 1 通道，n=2 shake-up 5 通道、n=3 13 通道（一般 2n(n−1)+1）。
  - 沿偏振方向模型 DLC 延迟与 Ossiander 关联延迟定量符合：n=2 为 7.3/6.7/5.9 as 对 7.8/6.55/5.6 as（90/100/110 eV，很好符合），n=3 为 38.1/34.0/29.8 as 对 45.9/37.7/32.2 as（尚可）；ab initio DLC 在 n=2 反而小（1.4/2.5/3.9 as）。
  - 绝对延迟随探测角快速下降主要源于 DLC 项的 1/cosθ 因子；shake-up 延迟符号在 θ ≈ 40° 反转；CLC 延迟大角度变为角度依赖且为纯量子效应，经典轨迹仅 θ ≲ 60° 与量子一致。
  - IR 场致剩余离子极化为小修正：n=2 壳 Δd_max ≈ 9.2×10⁻²，比 XUV 产生的 Stark 偶极 1.5 小 16 倍。
  - 局限：n=3 shake-up 中 XUV 偶极 4.5 仅 6.5 倍于 IR 失真（Δd₃₁₀,max ≈ 0.69）；大角度低信噪比区 DLC 模型与 ab initio 偏离的原因未解决。
- **对本课题**: 提供"通道数—偶极选择规则"的解析结构（2n(n−1)+1），可作为本课题多通道模型的通道数判据；亦提示角分辨修正必须与能量分辨并置。

### [ref:ortmann2024understanding] Ortmann L, Landsman A S. Understanding attosecond streaking

- **出处**: Reports on Progress in Physics, 2024, 87(8): 086401. DOI: 10.1088/1361-6633/ad6278
- **关系**: 系统化给出条纹延迟的物理分解框架（纯电离延迟 vs CLC 项），是本课题误差预算中"哪些项可分离、哪些不可分"的判据来源。
- **关键结论**: 综述系统阐述 Coulomb-laser-coupling（CLC）项在阿秒条纹中的物理起源，明确它不是数值噪声或高阶修正，而是条纹信号中结构性贡献的来源之一；给出把条纹总延迟分解为纯电离延迟与 CLC 贡献的框架，并界定两贡献可干净分离与分解失效的条件边界（出处：KB 页 `wiki/papers/2024-ad6278-*.md` 核心要点，原样保留）。
- **注**: KB 该页为摘要级蒸馏（digest_level: abstract），未给出具体数值阈值；arXiv 编号在 KB 中为占位代号 `ad6278`，本轮未取得其标准 arXiv ID，故以 CrossRef 实测 DOI 为准著录。
- **对本课题**: 本课题方案中"角度积分残余偶极相位贡献小于 2%"这类质量线，不能从文献直接引用，只能作为方案设定值——该结论由本综述的"分解边界"性质推得。

### [ref:kheifets2026rainbow] Kheifets A, Serov V, Vismarra F, et al. Rainbow retrieval of atomic time delays in attosecond streaking

- **出处**: Physical Review A, 2026, 113(4): 043103. DOI: 10.1103/9jcm-8gd8（CrossRef 实测：题名、期刊、卷期、文章号 043103、日期 2026-04-02、四位作者 Kheifets A / Serov V / Vismarra F / Wörner H 全部一致）
- **关系**: 提供"一次宽带测量 + 连续相位反演"的鲁棒路径，直接对应本课题"跨能区稳健谱相位重构方法"的目标形态。
- **关键结论（原样保留，出处：KB 页 `wiki/papers/2026-9jcm-8gd8-*.md` 核心要点）**:
  - 方法对象：He 1s、Ar 3p、Xe 4d 三种典型体系；核心输出为连续提取跨越宽光电子能量的电离相位与原子时间延迟 τ(E)，而非离散能量点的拟合值。
  - 三种可解析结构：He 低能区的 Coulomb 相；Ar Cooper 极小附近相位/延迟急剧变化；Xe 4d 巨型形状共振区的延迟峰结构。
  - 方法学定位：把 rainbow 散射中从 Airy 结构反推相位的思路用于整条 trace 拟合，替代逐能点分析。
  - 局限（KB 标注）：Cooper 极小等相位剧变区对模型假设（参考势、交换、关联处理）的敏感性与误差传递未定量；与 RABBITT 双光子路线的 Wigner 延迟定义自洽性未解决；分子取向/振动平均体系的推广未验证；PDF 缺失（has_pdf=false）。
- **对本课题**: 这是本课题"方法学修正 + 跨能区标定"两步走的直接方法学参照。特别注意其未定量部分——正是本课题可以填空的缺口。

### [ref:gao2026hidden] Gao J, Hasan M, Eisenhutt Z, et al. Hidden perturbative structure in attosecond streaking

- **出处**: arXiv:2610.24891 [physics.atom-ph]（arXiv API 实测：v1 提交 2026-10-17，v2 更新 2026-10-22，8 pages / 4 figures，作者 Jingsong Gao, Mahmudul Hasan, Zach Eisenhutt, Vladislav Serov, Hao Liang, Meng Han, Anatoli Kheifets）；无 DOI。本地 `knowledge/raw/papers/2026-2610.24891-*.md`
- **关系**: 证明条纹可作为连续-连续（CC）角动量倾向的相位敏感探针，是本课题"量子相位探测手段"这一目标在 2026 年的最新实现。
- **关键结论（原样保留，出处：KB raw 页 Abstract + `wiki/papers/2026-2610_24891-*.md` 精读笔记）**:
  - 通过筛选 IR 基频下的反演奇响应，从氦条纹数据分离出以 P₁ 与 P₃ Legendre 分量为主的角分布，其复系数给出有效 s/d 双光子振幅比。
  - 多通道双电子 TDSE 计算表明 Fano 型倾向在计入电子关联后仍然存活。
  - 计入实验 XUV attochirp 后模型重现测得的发射边趋势（说明探测脉冲相位结构不可忽略）。
  - 近阈值计算预言与束缚态氦 np Rydberg 系列相关的共振振幅与相位特征。
  - 数值细节（出处：KB 精读笔记）：连续谱用五通道双电子 TDSE（PAHF，有限元 DVR + 外复标度），IR 5.0 fs、950 nm（ω = 0.04796 a.u.）、13 个延迟（0.484 fs 间隔）；近阈 SAE：400 as XUV（Ω = 0.90 a.u.）+ 204 nm（10¹¹ W/cm²、31 延迟）；实验数据 E = 30–58 eV（2 eV bin）、121 延迟、360 角行；BASEX/rBASEX 双反演；有效 s/d 比由 reff(E) = [6A₁/A₃ − 4]/5 反演。
  - 局限（KB 标注）：P₁+P₃ 约化依赖初态 s 态与平行线偏振，推广到其它初态/分子/固体需重构角通道集；吸收边对反演技术敏感（BASEX vs rBASEX 系统差异），应以发射边为主基准。
- **对本课题**: 给出"角分布反演 + 啁啾感知"的现成工具链，可直接作为本课题角积分模块的对照基准（该文恰恰依赖角分辨，故与角积分方案互补）。

### [ref:xia2026complex] Xia M, Nishimiya K, Dong D, et al. Complex-gate all-optical frequency-resolved optical gating for ultrabroadband isolated attosecond pulse characterization

- **出处**: arXiv:2608.30516 [physics.optics]（arXiv API 实测：提交 2026-08-31，11 pages / 4 figures，作者 Minshuang Xia, Kaito Nishimiya, Dianhong Dong, Yuxi Fu, Eiji J. Takahashi）；无 DOI。本地 `knowledge/raw/papers/2026-2608.30516-*.md`
- **关系**: 直接针对本课题"传统 FROG-CRAB 检索保真度不足"这一缺口，给出替代算法族——并指出 FROG 族同样需要修正（须用复值门函数）。
- **关键结论（原样保留，出处：KB raw 页 Abstract）**:
  - 实验演示 AO-FROG 用于表征中红外 sub-cycle 场产生的超宽带孤立阿秒脉冲；把 AO-FROG 框架扩展到常规"仅相位调制"近似之外，建立基于强场近似（SFA）的理论框架，证明弱微扰场在 HHG 过程中**同时引起相位与振幅调制**，因此准确脉冲重建需要复值门函数。
  - 使用 2.26 μm sub-cycle 驱动激光，表征 100–180 eV 范围的氩中孤立阿秒脉冲。
  - 实测 AO-FROG 迹呈现随延迟变化的谱调制，源于微扰场对电子轨道与电离概率的改变；SFA 模拟重现实验观测并确认计入电离诱导的振幅调制的重要性。
  - 重建的时域与频域性质给出孤立脉冲时长约 300 as 及其谱相位，从而提供所生成脉冲阿秒啁啾的访问途径。
- **对本课题**: 本课题若在 2 μm 级驱动上做水窗段表征，"相位调制+振幅调制同时存在"是必须处理的第二类失效源，与多通道交叉项并列进入修正项设计。

### [ref:leung2025universal] Leung C S, Wiese J, Brupbacher K, et al. Universal in-line waveform characterization using arbitrary non-linear responses

- **出处**: arXiv:2511.04436 [physics.optics]（arXiv API 实测：提交 2025-11-06，13 pages / 8 figures）；无 DOI（arXiv 实测 doi/jref 字段为空）
- **关系**: 提供"非侵入式、任意非线性响应"的波形表征替代路线，与本课题"发展修正的新方法学"诉求高度同构。
- **关键结论（原样保留，出处：arXiv API 摘要）**:
  - 当代波形分辨表征方案受制于装置特定要求，严重限制适应性且未能建立例行在线诊断的标准程序。
  - 实验证明：来自多种介质与非线性观测量的相对产额测量，结合其开源重建算法族（CRIME 与 lazyCRIME），可在标准工作站上数分钟内实现阿秒精度量级的稳健波形检索。
  - 该框架已适配多种配置，包括非侵入式的、于阿秒瞬态吸收光谱（ATAS）实验期间的同步波形表征。
- **对本课题**: 提供了"跳出 FROG-CRAB 单一范式"的第三条路（相对产额 + 任意非线性响应 + 开源算法），本课题的方案选型应把它列为候选路线并作对比论证。

### [ref:ji2025quantitative] Ji J-B, Wörner H J. Quantitative uncertainty analysis of extracting attosecond delays from spectrally overlapping RABBIT experiments

- **出处**: Journal of Physics B: Atomic, Molecular and Optical Physics, 2025, 58: 135601. DOI: 10.1088/1361-6455/adea62（CrossRef 实测：题名、期刊、卷 58、页 135601、日期 2025-07-09、作者 Ji / Wörner 全部一致）
- **关系**: 为本课题误差预算提供可解析传播的统计骨架（相位提取方差 vs 能谱重叠度的定量关系），是"修正后方法学须自带误差传播"这一要求的现成范式。
- **关键结论（原样保留，出处：KB 页 `wiki/papers/2025-2405_06275-*.md` 核心要点）**:
  - 对"光谱重叠情形下"的 RABBIT 迹线做严格最小二乘处理，推导出相位提取的**方差公式**，其大小与能谱重叠程度直接挂钩，给出从数据本身即可评估误差上限的判据。
  - 证明 **global-fit**（对完整 spectrogram 拟合）与 **complex-fit**（对 sideband 振荡做复数拟合）在最小二乘意义下等价，两者给出相同的相位估计和相同的不确定度。
  - 使 RABBIT 的不确定度报告从经验性 bootstrap 升级为解析可传播的统计量。
  - 未决问题（KB 标注）："重叠程度"的具体度量未在摘要给出；是否讨论 systematic 偏差（如 AC-Stark 移位、CLC 偏倚）与统计误差分开；双色场相对相位抖动与 XUV-IR 时序抖动是否纳入误差传播。
- **对本课题**: 本课题跨能区标定实验的误差条设计可直接移植该方差传播框架；但须注意其假定噪声为高斯白噪声或已知协方差矩阵——真实实验的 XUV 谐波 shot-to-shot 强度涨落是否仍在框架内需自证。

### [ref:wang2024covariance] Wang J, Guo Z, Isele E, et al. Covariance analysis of impulsive streaking

- **出处**: arXiv:2411.01729 [physics.data-an]（arXiv API 实测：v1 提交 2024-11-04，v2 更新 2024-12-20，22 pages / 13 figures，作者 Jun Wang, Zhaoheng Guo, Erik Isele, Philip H. Bucksbaum, Agostino Marinelli, James P. Cryan, Taran Driver）；无 DOI。本地 `knowledge/raw/papers/2024-2411.01729-*.md`
- **关系**: 提供从含噪/涨落条纹数据中提取时间信息的统计方法，对应本课题"低信噪比下稳健重构"与误差预算需求。
- **关键结论（原样保留，出处：arXiv API 摘要）**:
  - 提出角分辨条纹实验协方差建模的完整框架；在脉冲式条纹（impulsive streaking）区间，电子动量分布（MD）的位移为无 dressing 的 MD 与 dressed MD 之间提供紧连接，该连接建立起跨不同 MD 形状共有的普适协方差结构（与 MD 的具体形状无关）。
  - 基于该框架发展了从角分辨条纹测量中检索时间信息的方法，使更准确、更稳健的时间测量成为可能。
- **对本课题**: 本课题在水窗段面临的正是"单发涨落 + 多壳层重叠 + 有限计数"三重劣化；协方差法提供了一条不依赖逐发定标的替代路线，可作为本课题算法方案的候选对照。

### [ref:rajendran2026breakdown] Rajendran S, Benito de Lama M, Maroju P K, et al. Breakdown of the isotropic asymptotic approximation in two-colour photoionisation

- **出处**: arXiv:2603.15293 [physics.atom-ph]（arXiv API 实测：提交 2026-03-16，v1，作者列表含 Sooraj Rajendran, Miguel Benito de Lama, Praveen Kumar Maroju, Michele Di Fraia, …, Johannes Feist, Alicia Palacios, Giuseppe Sansone 共 31 位）；无 DOI。本地 `knowledge/raw/papers/2026-2603.15293-*.md`
- **关系**: 直接给出"分析近似本身的破缺量级"，是本课题"修正项之外的分析近似须逐项计入误差预算"这一判断的外部实验参照。
- **关键结论（原样保留，出处：KB 页 `wiki/papers/2026-2603_15293-*.md` 精读笔记 + `01_background/reading-notes.md`）**:
  - 自参考方案：以基频三倍频（3ω）辐射的两个相邻 XUV 相干谐波光电离，同时叠加频率为 ω 的同步复制光并扫描延迟；两路径末态宇称不同，故仅沿共同偏振方向半空间积分观测产额振荡。
  - 实验观测到渐近近似预测值与实测边带相位之间存在**数十毫弧度（对应数阿秒量级）**的偏离，与全维模拟一致；全维模拟表明**离心势项是破缺的主导贡献源**，渐近近似自身的附加近似占次要地位。
  - 在约 13–15 eV 光电子动能区即可分辨 1–2 as 量级的偏离；同一动能（10 eV）处，涉及更多近红外光子交换的相位差偏离（约 0.05 rad ≈ 3 as）大于仅差一个光子的相位差偏离（约 0.025 rad ≈ 1.5 as）。
  - 误差棒随近红外强度升高而缩小；实验点在最高强度处与 TDSE 预测相容而与渐近近似预测不相容。
- **对本课题**: 本课题 5% 相位误差在水窗低段对应时间域判据 0.60 as，与该文给出的 1–2 as 破缺量级相当——这意味着即使修正项全部到位，分析近似的固有破缺仍可能主导残差，必须在方案中显式声明。

---

## 三、知识库关联

可关联的知识库页（`knowledge/wiki/` 下，已核实存在）：

### 3.1 方法/专题页

- [[阿秒计量方法体系]] — `wiki/method-topics/阿秒计量方法体系.md`：条纹术/RABBITT/Wigner 时延三大块，含四步条纹反演流程、RABBITT 边带相位分解公式 φ_{2q} = 2φ_{2q±1} + Δφ_W + Δφ_cc + Δφ_XUV、条纹卷积模型与 cc 修正、角分辨 EWS 计算栈（HF/RPAE/分波展开/TDSE 对照），以及 Ne τ_W(2p-2s) 前向值 4.82 as（SAE）/ 8.19 as（RPAE）与 ~±57° 的 P₂ 零点基准。本课题方案的"条纹信号模型"与"角分辨修正"两节可直接承接此页。
- [[FROG]] — `wiki/methods/FROG.md`
- [[RABBITT]] — `wiki/methods/RABBITT.md`
- [[RABBIT与RABBITT]] — `wiki/methods/RABBIT与RABBITT.md`
- [[VMI_双色_RABBIT_光电子谱]] — `wiki/methods/VMI_双色_RABBIT_光电子谱.md`
- [[表征方法]] — `wiki/mocs/表征方法.md`
- [[阿秒科学]] — `wiki/mocs/阿秒科学.md`
- [[强场物理]] — `wiki/mocs/强场物理.md`

### 3.2 概念页

- [[阿秒延迟测量]]（原子光发射延迟的测量与解释）、[[阿秒条纹与瞬态吸收谱联用观测激发态偶极跃迁的相对符号]]、[[阿秒脉冲串]]、[[阿秒脉冲合成]]、[[阿秒瞬态吸收]]、[[阿秒科学]]
- [[RABBIT]]、[[RABBITT]]、[[rainbow-RABBITT]]（rainbow RABBITT 连续谱分析，与 [ref:kheifets2026rainbow] 的 rainbow retrieval 同族方法学）
- [[transient-quantum-phase]]、[[Attosecond-quantum-optics]]、[[CEP稳定]]、[[TDSE]]、[[VMI]]
- [[水窗口]]（水窗能区物理与实验约束）、[[中红外驱动HHG]]、[[3_μm_中红外驱动窗口]]（长波驱动 → SXR 截止路径）
- [[隧穿时间]]（与 Wigner/CLC 延迟分解相邻的隧穿时间解释框架）
- [[强场电离量子轨道方法]]、`wiki/method-topics/强场电离量子轨道方法.md`

> 说明：知识库中尚无以 "Cooper minimum / Coulomb phase / atomic time delay / shape resonance / attosecond streaking" 命名的独立概念页——这些词目前只作为 tag 出现在相关论文页的 frontmatter `related:` 字段中（如 `wiki/papers/2026-9jcm-8gd8-*.md`）。为避免产生死链，此处改链至实际存在的等价中文概念页；上述英文概念名可作为后续知识库补页的候选条目。

### 3.3 论文页（本课题可直接引用的 KB 蒸馏笔记 + 方法卡）

| KB 页 | 对应本文件 |
|---|---|
| `wiki/papers/2010-1006_1827-attosecond-streaking-enables-the-measurement-of-quantum-phas.md` | [ref:yakovlev2010attosecond] |
| `wiki/papers/2016-1602_08144-attosecond-pulse-characterization-with-coherent-rydberg-wave.md` | [ref:pabst2016eliminating] |
| `wiki/papers/2017-1710_02208-attosecond-streaking-in-the-water-window-a-new-regime-of-att.md` | [ref:cousin2017attosecond] |
| `wiki/papers/2024-2409_03622-photoelectronresidual-ion-entanglement-in-streaked-shake-up.md` | [ref:shi2024photoelectron] |
| `wiki/papers/2026-2610_24891-hidden-perturbative-structure-in-attosecond-streak.md` | [ref:gao2026hidden] |
| `wiki/papers/2026-9jcm-8gd8-rainbow-retrieval-of-atomic-time-delays-in-attosecond-streak.md` | [ref:kheifets2026rainbow] |
| `wiki/papers/2026-2608_18773-electron-correlation-enables-phase-coherent-one-at.md` | 见 §1.6 备选 |
| `wiki/papers/2024-ad6278-understanding-attosecond-streaking.md` | [ref:ortmann2024understanding] |
| `wiki/papers/2024-2411_01729-covariance-analysis-of-impulsive-streaking.md` | [ref:wang2024covariance] |
| `wiki/papers/2026-doi-10-1088-2515-7647-ae4957-self-referenced-sampling-of-attosecond-visible-vacuum-ultrav.md` | 自参考采样对照方案（摘要级） |

### 3.4 课题本体页

- [[general-attosecond-streaking-20260822]] — `wiki/projects/NSFC-强场超快/versions/general-attosecond-streaking-20260822.md`、`wiki/projects/NSFC-强场超快/reports/general-attosecond-streaking-20260822.md`、`wiki/projects/NSFC-强场超快/proposals/general-attosecond-streaking-20260822.md`
- 原始条目底座（`knowledge/raw/papers/`）：`2010-1006.1827-attosecond-streaking-enables-the-measurement-of-quantum-phas.md`、`2016-1602.08144-attosecond-pulse-characterization-with-coherent-rydberg-wave.md`、`2017-1710.02208-attosecond-streaking-in-the-water-window-a-new-regime-of-att.md`、`2024-2409.03622-photoelectronresidual-ion-entanglement-in-streaked-shake-up.md`、`2024-2411.01729-covariance-analysis-of-impulsive-streaking.md`、`2025-2405.06275-quantitative-uncertainty-analysis-of-extracting-attosecond-d.md`、`2025-2507.11497-photoemission-chronoscopy-of-the-iodoalkanes.md`、`2026-2403.05073-rainbow-retrieval-of-atomic-time-delays-in-attosecond-streak.md`、`2026-2603.15293-breakdown-of-the-isotropic-asymptotic-approximation-in-two-c.md`、`2026-2608.18773-electron-correlation-enables-phase-coherent-one-at.md`、`2026-2608.30516-complex-gate-all-optical-frequency-resolved-optica.md`、`2026-2610.24891-hidden-perturbative-structure-in-attosecond-streak.md`
  > 注意：`2026-2403.05073-*.md` 与 `2025-2405.06275-*.md` 两个 raw 文件的 `arxiv_id` 字段与真实论文不符（见 §0.2），引用须按 DOI 著录，不得引用其 arXiv 字段。

### 3.5 本课题既有背景产物（承接，非本轮新增）

- `01_background/gap-report.md` — 周末输入补充的拟解决空白与创新方向清单（2026-08-22 cl_20260815_91c280）
- `01_background/direction-calibration.md` — 方向标定
- `01_background/reading-notes.md` — 前序轮次五维笔记（2610.24891 / 2409.03622 / 2507.11497 / 2603.15293）
- `01_background/reference-metadata-crossref.md` — 40 条 CrossRef 实测回录池
- `04_references/references-source.md` — 43 条既有著录池

---

## 四、领域地图到本课题的方法学落点

本节把上面的文献脉络收束为对本课题可直接推进的三条方法路线（仅给方向与判据锚点，不展开方案）。

### 4.1 路线甲：多通道失效修正（对应 [ref:cousin2017attosecond][ref:peschel2022attosecond][ref:shi2024photoelectron][ref:xia2026complex]）

- 问题定义：水窗段光电离截面骤降导致必须用较高通量与较长时间采集，而多壳层同时电离 + 多通道相位干涉使 FROG-CRAB 的二阶响应基础失效。
- 文献锚点：[ref:cousin2017attosecond] 给出"带宽 ≤60 eV + 10¹¹ W/cm² 可重建 / 100 eV + 10¹¹ W/cm² 失效 / 100 eV + 10¹² W/cm² 成功"的硬边界；[ref:shi2024photoelectron] 给出通道数解析结构 2n(n−1)+1 与 DLC 项 1/cosθ 角依赖、θ ≈ 40° 符号反转；[ref:peschel2022attosecond] 给出通道间相位差 Δφᵢⱼ 的可观测性；[ref:xia2026complex] 给出"相位调制与振幅调制同时存在"这一第二类失效源。
- 判据锚点：以 [ref:cousin2017attosecond] 的 322 as 上限与 10¹² W/cm² 阈值作为跨能区重建保真度的外部标尺。

### 4.2 路线乙：偶极相位角积分解耦（对应 [ref:pabst2016eliminating][ref:gao2026hidden][ref:ji2025quantitative][ref:rajendran2026breakdown]）

- 问题定义：FROG-CRAB/PROOF 忽略束缚-连续与连续-连续偶极相位，该相位可引入数十阿秒延迟且有非平凡能量依赖。
- 文献锚点：[ref:pabst2016eliminating] 给出球对称母离子 + 角积分的消除机制与残余量级（K 角积分关联斜率 −0.052 as/eV vs 方向谱 0.12 as/eV；Ne Fano 角积分 ≤ ±3 as vs 方向谱可达 −30 as；RPAE 中心延迟约 6 as 需绝对定标）；[ref:gao2026hidden] 给出角分布反演（P₁/P₃、reff(E) = [6A₁/A₃ − 4]/5、BASEX/rBASEX 系统差异）；[ref:ji2025quantitative] 给出相位提取方差的解析传播与 global-fit ≡ complex-fit 等价性；[ref:rajendran2026breakdown] 给出渐近近似破缺的量级（数十毫弧度 / 1–2 as，13–15 eV 动能区可分辨，离心势项为主导）。
- 判据锚点：以 [ref:rajendran2026breakdown] 的 1–2 as 破缺量级与 [ref:pabst2016eliminating] 的 ±3 as 残余量为本课题角积分模块的"不可压缩残差"下限。

### 4.3 路线丙：跨能区标定与自洽检验（对应 [ref:kheifets2026rainbow][ref:leung2025universal][ref:ji2025quantitative][ref:wang2024covariance]）

- 问题定义：需要一条能给出连续 τ(E) 曲线、并自带内禀自洽检验的重构方法，而非逐能点拟合拼接。
- 文献锚点：[ref:kheifets2026rainbow] 给出 rainbow retrieval 的连续相位反演与三类基准靶（He/Ar/Xe）结构解析，同时指出其在 Cooper 极小区的模型敏感性与误差传递未定量；[ref:leung2025universal] 给出 CRIME/lazyCRIME 的非侵入式通用波形表征路径；[ref:ji2025quantitative] 给出可解析传播的不确定度骨架；[ref:wang2024covariance] 给出协方差法在含涨落数据中的时间信息提取；[ref:pabst2016eliminating] 的 N>2 能级波包自洽关系 φ(j₁,j₃) = φ(j₁,j₂) + φ(j₂,j₃) 是现有脉冲重构方法中独一无二的内在自检机制。
- 判据锚点：以 [ref:kheifets2026rainbow] 的"未定量"清单与 [ref:pabst2016eliminating] 的自洽约束作为本课题"自洽检验"模块的可执行判据来源。

---

## 五、检索方法与覆盖说明（补充）

### 5.1 本轮实际执行的检索

1. `arXiv API id_list=` 批量（12 + 8 + 7 + 7 + 1 篇），单次返回上限受服务端 503/429 影响，间隔 15–25 s 重试，全部成功解析。
2. `arXiv API search_query=`：
   - `abs:attosecond AND abs:reconstruction`（sortBy=submittedDate desc，max_results=60）→ totalResults = 115，用于近 24 个月扫描。
   - `au:Woerner AND abs:RABBIT` → 命中 Wörner 组 RABBIT 系列（1906.07059 / 2506.07445 cuRABBITT / 2407.09662 / 2302.04137 / 2301.03697 等），确认 rainbow RABBITT 与 Wigner/cc 延迟分离工作构成邻近方法学簇。
   - `au:Ji AND au:Woerner AND cat:physics.atom-ph` → 同上。
   - 已知失败模式：`abs:"rainbow retrieval"`、`ti:"Rainbow retrieval..."`、`ti:spectrally AND ti:overlapping`、`abs:attosecond AND abs:reconstruction AND cat:physics.optics` 均返回 totalResults = 0——arXiv API 对带引号短语与多前缀 AND 组合支持不佳，**不可据此断定论文不存在**，须改用 CrossRef 题录检索（本轮正是靠 CrossRef 定位了 Ji & Wörner 与 rainbow retrieval 两篇的正确标识）。
3. `CrossRef REST`：
   - `works/10.1103/9jcm-8gd8` → rainbow retrieval：Physical Review A 113(4) 043103，2026-04-02，作者 Kheifets A / Serov V / Vismarra F / Wörner H。
   - `works?query.bibliographic=Quantitative uncertainty analysis...` → J. Phys. B 58, 135601 (2025-07-09)，作者 Ji / Wörner，DOI 10.1088/1361-6455/adea62。
4. 本地知识库检索：`knowledge/wiki/papers/`（3875 页）按 attosecond/streaking/pulse-retrieval/water-window/soft-x-ray-attosecond/time-delay 六组关键词筛文件名；`knowledge/raw/papers/` 按 12 个 arXiv ID 定位原始条目。

### 5.2 覆盖边界（诚实声明）

- 本文件**未**逐篇精读全文：仅 [ref:yakovlev2010attosecond][ref:pabst2016eliminating][ref:cousin2017attosecond][ref:shi2024photoelectron][ref:gao2026hidden] 有 KB 全文级（digest_level: fulltext / has_fulltext: true）蒸馏笔记与完整方法卡，数值取自这些一手蒸馏；[ref:kheifets2026rainbow][ref:ortmann2024understanding][ref:ji2025quantitative] 为摘要级蒸馏（digest_level: abstract），已明确标注"未定量"部分；[ref:xia2026complex][ref:leung2025universal][ref:wang2024covariance][ref:rajendran2026breakdown] 的数值取自 arXiv API 官方摘要原文。
- 近 24 个月内候选极多（115 条 `abs:attosecond AND abs:reconstruction`），本文件只收了与本课题命题直接相关且元数据经实测的 8 篇，未做穷尽列举。
- 水窗 SXR 光源侧（[ref:cousin2017attosecond] 所需的光子通量/脉冲能量工程）另有 Pupeikis 2020 Optica、Fu 2020 Commun. Phys. 等条目在检索池中，本文件未纳入核心文献组（属方案层的装置问题，非本课题的计量学命题）。
- 待核验条目：既有检索池条目 "Evaluating the accuracy of attosecond streaking time-delay measurements"（Kasmi et al., 2023）的 arXiv/CrossRef 标识本轮未取得，KB 对应页正文与元数据冲突，暂不承重。

---

## 六、引用键与 bib 对照

文献锚点统一采用 `[ref:<bib键>]` 实键格式（v8.0.6 对齐：原 [ref:N] 序号锚点按 bib 头部声明的顺序映射替换），与 `04_references/references.bib` 条目键一一对应；bib 每条末行带 `source:` 溯源行（A4 硬门）。
