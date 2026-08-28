---
title: "ML加速发现可合成的高温altermagnets与巨大自旋劈裂"
type: "papers"
created: "2026-08-28T12:22:06Z"
updated: "2026-08-28T12:22:06Z"
tags: ["altermagnet", "machine-learning", "high-throughput-screening", "spin-splitting", "strong-field-ultrafast", "DFT", "Néel-temperature"]
related: ["AB2C2D compounds", "THz spin dynamics", "altermagnetism", "high-throughput DFT", "non-relativistic spin splitting", "ultrafast demagnetization"]
source_raw: "2026-2605.27888-machine-learning-accelerated-discovery-of-synthesizable-high.md"
growth_stage: "growing"
confidence: 0.6
auto_grown: true
review_status: "pending"
---

# ML加速发现可合成的高温altermagnets与巨大自旋劈裂

## 林赛的理解

作为一个做强场超快光学的PI，我通常关心的不是材料是否"新"，而是材料能否在皮秒–飞秒时间尺度上、在强场（高电场或强磁场）下展现出**可控的非平衡自旋动力学**。这篇文章吸引我是因为它把"altermagnet"这一相对年轻的磁性范式推向了一个**工程化筛选的层级**，并给出了具体的数字：1.88 eV的非相对论自旋劈裂、~390 K的Néel温度、以及34个低形成能候选。我第一反应是——这个量级的能级劈裂，已经落在近红外–可见泵浦–探测的能量窗口里，而且Néel温度足够高，意味着**不需要液氦就能在常温做超快实验**，这对实验端是极其友好的。

从方法论角度看，作者用机器学习加速了高通量筛选，这本身是一种趋势。但我更在意的是：**这个体系的空间群对称性是什么？**altermagnet的核心是d-wave/g-wave等各向异性的自旋分裂，只有特定对称性才允许。换句话说，论文标题里"giant spin splitting"实际上是被对称性"允许"才显得巨大——这一点在摘要里没展开，我必须去正文里确认。

## 核心要点

- **材料体系**：四方AB2C2D化合物（四元），用机器学习模型加速DFT筛选
- **筛选规模**：从大规模候选池中筛出**34个低形成能**候选，意味着具备实验合成可行性
- **明星材料**：RbMn2Te2O
  - 非相对论自旋劈裂：**1.88 eV**
  - Néel温度：**~390 K**（室温以上）
- **物理意义**：
  - Altermagnet的标志性特征——**无自旋轨道耦合（SOC）也能有大的自旋劈裂**，来源是晶格对称性而非相对论效应
  - 与传统铁磁/反铁磁不同，altermagnet在动量空间呈现d-wave/g-wave型的自旋纹理
- **方法亮点**：
  - ML辅助的高通量筛选框架，避免了对每个候选做完整DFT
  - 形成能作为可合成性的代理指标

## 实验/研究关联

我尝试把这份工作和组里的几个方向做映射：

1. **超快退磁化（ultrafast demagnetization）**
   - Altermagnet在强激光激发下，电子被激发到自旋劈裂的能带之间，会不会表现出**新的退磁通道**？传统反铁磁（如NiO）的超快退磁在THz尺度已被广泛研究，altermagnet的对称性保护劈裂可能允许**相干自旋振荡**的观测，这是我们THz时域光谱能直接捕捉的。

2. **强场下的自旋重整**
   - 1.88 eV的劈裂量级意味着：如果我们用中红外强场（~MV/cm）来驱动带间激发，可能在亚周期时间尺度上**重塑自旋纹理**。这是一个有意思的非绝热调控窗口，但需要确认该材料的相干时间和散射率。

3. **Néel温度390 K的实用性**
   - 这是关键卖点。我们的cryostat可以降到液氦温区，但**常温工作**意味着可以用更高重频的放大器（如1 kHz Ti:Sa或甚至MHz级Yb）而不必担心热负载，对信噪比和统计性都是巨大的提升。

4. **AB2C2D四元化合物的合成路径**
   - 作为PI我也要务实：Mn基氧化物涉及Rb这类活泼碱金属，**固相反应需要严格控氧分压**。如果合作方能拿到样品，ARPES+时间分辨ARPES是验证自旋劈裂对称性的金标准。

## 开放问题

我对这篇工作保持几个批判性的疑问：

1. **ML模型的"黑箱"风险**：训练集的偏差会直接决定候选池的质量。34个低形成能候选里有多少是**真正新发现**，有多少是已知材料的"再发现"？需要看补充材料的清单。

2. **1.88 eV是否真"giant"**：对比反铁磁MnTe的<0.1 eV自旋劈裂，1.88 eV确实大。但这个值是在PBE/GGA级别算的，还是包含了HSE06？**带隙和劈裂对泛函敏感**，需要确认计算层级。

3. **自旋劈裂的实验可观测性**：
   - ARPES能直接看到k-dependent的劈裂，但需要高分辨。
   - **输运端**：anomalous Hall effect在altermagnet中是否存在、是否被对称性禁止？这关系到能否用简单的电学手段表征。

4. **与现有altermagnet候选的比较**：
   - MnTe、CrSb、RuO2是已被广泛研究的altermagnet候选，RbMn2Te2O相对于它们的**独特优势**是什么？是温度？是劈裂大小？还是可合成性？我没在摘要里看到差异化论述。

5. **强场超快实验的具体可行性**：
   - 1.88 eV对应~690 nm光子，恰好在Ti:Sa二次谐波（400 nm）和基频（800 nm）之间。**是否可被单光子直接激发**？能带结构细节决定这一点。

6. **动态层面的缺失**：
   - 这是一个**纯静态**的理论筛选工作。altermagnet在非平衡下的行为（光致相变、超快磁化翻转）目前仍属空白。如果我考虑以此为样品申请beamtime，需要明确"我们测什么物理问题"。

## 来源
- 原始材料：2026-2605.27888-machine-learning-accelerated-discovery-of-synthesizable-high.md
- 蒸馏时间：2026-08-28T12:22:06Z

<!-- linsai-wikilinks -->
## 关联概念

- [[AB2C2D compounds]]
- [[THz spin dynamics]]
- [[altermagnetism]]
- [[high-throughput DFT]]
- [[non-relativistic spin splitting]]
- [[ultrafast demagnetization]]
<!-- /linsai-wikilinks -->
