---
title: "2025-2509_14991-ultrafast-controlling-net-magnetization-in-g-wave-altermagne"
type: "papers"
created: "2026-09-27T04:57:45Z"
updated: "2026-11-15T15:09:21Z"
tags: []
related: ["2509.14991", "CrSb", "TDDFT", "general-new-idea-20260822", "general-order-parameter-ultrafast-readout-20260727", "交变磁体", "光-磁耦合", "含时密度泛函", "强关联体系", "强场超快", "强场超快光学", "强场驱动", "自旋劈裂"]
source_raw: "2025-2509.14991-ultrafast-controlling-net-magnetization-in-g-wave-altermagne.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
digest_level: "abstract"
updated_at: "2026-10-04T01:00:47Z"
merged_from: ["wiki/papers/2509.14991.md"]
---

• ---
  title: "超快激光控制 g 波交变磁体净磁化（CrSb TDDFT）"
  type: papers
  created: "2026-09-27T04:57:09Z"
  updated: "2026-09-27T04:57:09Z"
  tags: ["交变磁体", "altermagnet", "超快退磁", "TDDFT", "激光-磁耦合", "CrSb"]
  related: ["超快退磁动力学", "交变磁性", "时间依赖密度泛函理论", "亚铁磁态", "强场激光操控"]
  source_raw: "2025-2509.14991-ultrafast-controlling-net-magnetization-in-g-wave-altermagne.md"
  growth_stage: "growing"
  confidence: 0.7
  auto_grown: true
  review_status: "pending"
  ---

  # 超快激光控制 g 波交变磁体净磁化（CrSb TDDFT）

  ## 林赛的理解

  我是林赛，做强场超快光学的。这篇 arXiv 2509.14991（Zhou、Sharma、He，2025）的核心信息很有味道：它把超快退磁这个我们熟悉的命题，从传统的铁磁/亚铁磁体系挪到了**交变磁体（altermagnet）**——具体是 g 波交变磁体 CrSb——上面，并且给出了一个相当干净的物理图像：**退磁动力学对激光入射方向高度敏感**，斜入射可以在两个亚晶格之间制造不对称的退磁，从而在一个本征上两个亚晶格磁矩严格抵消（净磁化为零）的体系里，瞬态"泵"出一个净磁化，瞬时表现类似亚铁磁态。

  这个思路对我们做超快光控磁的人来说有两层启发。第一，它把"激光"从一个各向同性的扰动提升为一个有方向自由度的旋钮——入射方向成了调控亚格点选择性激发的新参量，这在过去的退磁文献里不是主角。第二，它提示交变磁体可能是"光诱导非常规磁性"的好平台：净磁化是被对称性禁戒的本征量，而超快光场可以瞬态打破这个禁戒，这比在铁磁体里"把已有的磁化打下去"多了一层对称性工程的味道。

  不过我要打问号的地方也很明确：目前输入材料只有一句话摘要，没有能谱、没有时间尺度、没有退磁深度的定量信息。TDDFT 是好的第一性原理工具，但"亚晶格非对称退磁"是否 robust 地依赖入射方向而非数值细节，需要看正文的收敛性和对称性分析。这是摘要级笔记，具体数值以原文为准。

  ## 核心要点

  - **体系**：g 波交变磁体 CrSb——亚晶格磁矩反平行、净磁化本征为零，但磁输运上有非常规（d/g 波）自旋劈裂。
  - **方法**：时间依赖密度泛函理论（TDDFT）模拟超快激光驱动的退磁动力学。
  - **核心发现**：退磁动力学强烈依赖激光**入射方向**。
  - **机制**：斜入射诱导**亚晶格非对称退磁**——两个亚格点退磁速率/深度不同。
  - **瞬态后果**：体系短暂进入**类亚铁磁态**，产生非零的**净磁化**。
  - **意义**：在零净磁化的本征反补偿体系中，用光场方向作为旋钮"按需写入"瞬态磁化。

  ## 实验/研究关联

  - 与我组强场超快方向直接相关：属于"激光操控磁性"的大框架，且引入了入射方向/偏振几何这一我们实验室天然可调的自由度。
  - 方法论上可与超快退磁的唯象三温度模型、以及 TDDFT 模拟强场驱动电子动力学的既有工作对照。
  - 关联课题池：`general-new-idea-20260822` 已引用本文献（本项目管线标记）。
  - 潜在衔接：与 HHG 探测磁性动力学、以及强场调控量子材料（包括 moiré/强关联体系）的课题存在方法论重叠——光场作为对称性选择工具的思路可迁移。

  ## 开放问题

  - 非对称退磁对入射方向的依赖有多普适？是 CrSb/g 波的特例还是交变磁体的一般性质？
  - 瞬态净磁化的幅度、寿命、以及能否重复泵浦积累，摘要均未给出定量信息。
  - 亚晶格选择性吸收的微观通道是什么（带间跃迁的选择定则、对称性允许的光学跃迁差异）？
  - 实验上需要什么探针来确认"类亚铁磁瞬态"（如超快 XMCD、磁光克尔、THz 发射）？
  - TDDFT 处理的激光强度窗口是否与真实实验可达（或可扩展到我们关心的强场 regime）一致？
  - g 波（高阶角动量）自旋劈裂与退磁方向的耦合是否会带来额外的选择性？

  ## 来源
  - 原始材料：2025-2509.14991-ultrafast-controlling-net-magnetization-in-g-wave-altermagne.md
  - 蒸馏时间：2026-09-27T04:57:09Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：TDDFT 超快退磁模拟——激光入射方向调控 g 波交变磁体 CrSb 的亚晶格非对称退磁与瞬态净磁化（Zhou, Sharma, He）

**原理**：把超快退磁从铁磁/亚铁磁体系挪到本征零净磁化的 g 波交变磁体 CrSb：TDDFT 模拟超快激光驱动的退磁动力学，核心发现是退磁动力学强烈依赖激光入射方向——斜入射在两个亚晶格间制造不对称退磁（速率/深度不同），使本征磁矩严格抵消的体系瞬态'泵'出净磁化、短暂进入类亚铁磁态；方法论意义：激光从各向同性扰动提升为带方向自由度的旋钮（入射方向成为亚格点选择性激发的新参量）；对称性工程味道：净磁化是被对称性禁戒的本征量，超快光场瞬态打破该禁戒——'光场方向作为对称性选择工具'。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 体系与方法 | g 波交变磁体 CrSb；TDDFT 模拟超快激光退磁动力学；核心旋钮为激光入射方向 | 核心要点 |

**适用边界**：摘要级页面（仅一句话摘要，本页自注'具体数值以原文为准'），瞬态净磁化的幅度、寿命、重复泵浦积累均未给；亚晶格选择性吸收的微观通道（带间跃迁选择定则/对称性允许跃迁差异）未明；入射方向依赖的普适性（CrSb/g 波特例 vs 交变磁体一般性质）未确认；确认'类亚铁磁瞬态'的实验探针（超快 XMCD/磁光克尔/THz 发射）未落实；TDDFT 激光强度窗口与实验可达强场 regime 的一致性未验证。
**代表作**：Zhou, Sharma, He, 超快激光控制 g 波交变磁体净磁化（CrSb TDDFT，arXiv:2509.14991，2025）
*方法卡回补 2026-10-03*

## 合并自「2509.14991」

## 深度解析

（来自简报深度分析）

## 阅读笔记

### general-order-parameter-ultrafast-readout-20260727

标题：Ultrafast controlling net magnetization in g-wave altermagnets via laser fields
作者：Zhaobo Zhou, Sangeeta Sharma, Junjie He
领域：cond-mat.mtrl-sci / physics.comp-ph（2025-09-18）

### 研究问题
论文提出核心问题：在 d 波以上（如 g 波、i 波）altermagnet 中，飞秒激光能否瞬时把"净磁化为零"的态驱动到具有显著净磁化的 ferrimagnetic-like 态？该响应是否依赖于激光入射方向与晶轴的相对取向？回答"激光-序参量"耦合是否构成 altermagnet 的全新"光-磁"控制自由度。

### 研究背景
过去超快退磁研究集中在铁磁/反铁磁体系；altermagnet 子格对称补偿，理论上不允许有净磁化，光致净磁化也未被系统研究。CrSb 已被确认为 g-wave 金属型 altermagent，其能带在节点结构上具 spin-uncompensated region（沿特定 k 路径自旋密度不平衡）；d-wave 与 g-wave 在 OISTR（Optical Intersite Spin Transfer）机制下应有完全不同的退磁动力学。前者已在 d-wave 体系（如 RuO_2 候选）有讨论。

### 研究方法
使用含时密度泛函理论（TDDFT），含 spin-orbit 耦合，对 CrSb 块体做飞秒激光（典型 ~800 nm，fs 量级）激发模拟；对比两种入射几何：[0001] 法向 vs偏离法向（off-normal）；监控两个 Cr 子格的瞬时磁化幅度与时间不对称性；用局域自旋态密度（LDOS）沿特定能带路径分析 spin-uncompensated region 与光极化的对齐关系，作为光-磁响应大小的判据。

### 主要发现与核心结论
(1) 法向（[0001]）入射时：两个 Cr 子格 demagnetization 时域对称，但幅度不等，净磁化保持为零（与 d-wave AM 行为相反，d-wave AM 在法向即可观察到 OISTR 非对称）；(2) 偏离法向入射时：两子格 demagnetization 显著不对称，瞬时驱动系统进入 ferrimagnetic-like 态，产生 ~sizable net magnetization；(3) 该方向依赖性源自 g-wave AM 体相能带节点各向异性，使 OISTR 强烈受激光极化方向与 spin-uncompensated 区域对齐情况调制；(4) 提出普适判据："当激光极化沿 spin-uncompensated 能带路径对齐时，光致净磁化出现"，可由 LDOS 沿特定路径直接读出。

### 潜在研究方向
(1) 把判据推广到 i-wave 与 s-wave AM，比较 d/g/i 体系 OISTR 强度序列；(2) 实验上需 fs 时间分辨磁光 Kerr / XMCD 在 off-normal 入射下直接探测瞬时净磁化；(3) 利用 g-wave AM 的方向依赖净磁化做"光开关"的非易失自旋逻辑；(4) TDDFT 需进一步纳入电子-声子耦合与多体关联，验证 ferrimagnetic-like 态的真实寿命尺度（fs vs ps）。

<!-- linsai-wikilinks -->
## 关联概念

- [[2509.14991]]
- [[CrSb]]
- [[TDDFT]]
- [[general-new-idea-20260822]]
- [[general-order-parameter-ultrafast-readout-20260727]]
- [[交变磁体]]
- [[光-磁耦合]]
- [[含时密度泛函]]
- [[强关联体系]]
- [[强场超快]]
- [[强场超快光学]]
- [[强场驱动]]
- [[自旋劈裂]]
<!-- /linsai-wikilinks -->
