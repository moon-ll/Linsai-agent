---
title: "Nonrelativistic Functional Properties in Collinear Antiferromagnets Based on Multipole Representation Theory"
type: "papers"
created: "2026-10-01T18:53:17Z"
updated: "2026-11-15T15:09:24Z"
tags: ["反铁磁", "多极表示理论", "自旋点群", "非相对论响应", "MnPS3", "无SOC功能响应"]
related: ["Berry连接反铁磁", "MnPS3", "general-berry-mnps3-rashba-20260816", "共线反铁磁体", "多极矩", "强场超快", "强场超快光场调控反铁磁序", "自旋点群对称性", "非相对论反常输运"]
source_raw: "2025-2512.03657-nonrelativistic-functional-properties-in-collinear-antiferro.md"
growth_stage: "growing"
confidence: 0.65
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Nonrelativistic Functional Properties in Collinear Antiferromagnets Based on Multipole Representation Theory

## 林赛的理解

读完 Ogawa & Hayami 这篇 JPSJ 2026 的工作，第一感觉是它给我正在推进的 MnPS₃ / Rashba 体系提供了一个非常及时的对称性视角。Hayami 小组最近两年系统在做"自旋点群（spin point group）"下的多极分类，把共线反铁磁体里那些**不依赖自旋轨道耦合（SOC）就能存活**的功能响应一条条列出来——这件事对我们强场超快这一脉很重要，因为它意味着：即使在光场把 SOC 暂时"抹掉"的时间尺度上（亚周期、亚飞秒区间），反铁磁体仍可能保留一些可被光场驱动的非相对论自由度。

对我个人而言，最想抓住的是三件事：（1）他们给出的多极——响应对应表里，**纯由共线 AFM 序对称性允许的**那一支到底是哪些条目；（2）这些条目里有没有与光学二阶/三阶响应（shift current、注入电流、THG 磁二色性等）直接挂钩的；（3）MnPS₃ 作为他们分类中可能的某个具体空间群成员，落在哪一支、属于哪个多极通道。原料只是元数据级别，具体表里的条目、对应的磁点群、母多极，我都没看到，所以下面核心要点里我会把"已知骨架"和"待补全内容"分开标清楚，不去脑补。

## 核心要点

- **理论框架**：基于自旋点群对称性（spin point group），把共线反铁磁体里的多极矩做系统分类，识别哪些多极及其耦合的功能响应**不需要 SOC 就能存在**。
- **关键论断**：在共线 AFM 中存在一个**非相对论通道**的功能响应集合，这些响应在 SOC=0 极限下依然由对称性保护，因此是"纯磁序驱动"的，而不是 SOC 介导的。
- **方法亮点**：
  - 用多极表示理论（multipole representation theory）替代传统的磁多极枚举，得到与磁点群不完全等价的分类（spin point group 比 magnetic point group 更粗，但对纯共线序更自然）。
  - 系统扫描"无 SOC 仍存活"的响应条目（具体条目需进一步核对正文表格）。
- **发表与时间线**：JPSJ 2026（arXiv 2512.03657），与近期 altermagnet / 共线 AFM 功能响应浪潮同期。
- **可直接复用的产物**：一套（按自旋点群分类的）"非相对论功能响应清单"，可作为后续挑选候选材料与候选响应的对称性筛选器。

> ⚠️ 原料仅为摘要级元数据，**未给出**：具体的多极–响应对应表、所列举的反铁磁空间群列表、所计算的数值响应大小、是否涉及输运/光学/磁化率等具体响应函数。后续需读全文补全。

## 实验/研究关联

- **与 MnPS₃ / Berry–Rashba 提案的连接**：
  - MnPS₃ 是层状共线反铁磁体，恰好是 Hayami 分类体系的典型落点。提案 `general-berry-mnps3-rashba-20260816` 关注的是反铁磁序与 Berry 通道的耦合；如果 Ogawa & Hayami 的清单里包含由共线序单独（无 SOC）允许的 Berry 极化项或类反常项，那就不需要"硬等" Rashba 来产生非平凡输运/光学信号——这对提案的 baseline 论证有利。
  - 同时也意味着：在我们做**强场近红外/中红外 pump** 把 MnPS₃ 序参量瞬时淬灭的实验中，需要把"无 SOC 也能活"的通道与"必须 SOC 维持"的通道分开标定；前者是序淬灭后仍可能存留的信号本底。
- **与 NSFC 强场超快项目的连接**：
  - 自旋点群分类对**亚周期动力学**尤其有用：在光场把 SOC 驱动的项暂时压制的时间窗口内，自旋点群允许的（纯由共线序给出的）响应可被视作"反铁磁序的纯光学指纹"。
  - 可作为后续博士/硕士生选题的对称性筛选工具：先用 Hayami 的清单挑候选材料与候选响应，再用我们的强场超快平台做时间分辨验证。
- **与既有文献谱系的关系**：与 Šmejkal 等关于 altermagnet 的工作、以及 Hayami 自己之前关于"磁多极–反常输运"的工作形成连续的同一条线，我们组之前没系统跟进，需要补课。

## 开放问题

1. **具体清单**：Ogawa & Hayami 给出的"无 SOC 仍存活"的功能响应完整列表到底是什么？哪些是线性（dc 输运、磁化率），哪些是二阶/非线性（shift current、注入电流、磁电、THG / SHG）？
2. **MnPS₃ 归属**：MnPS₃（P2₁/c 或其磁基态所属空间群）在他们的自旋点群分类下落在哪一支？对应的母多极是哪个（磁八极？电四极？）？
3. **时间分辨可观测性**：纯自旋点群允许的响应在强场 pump 后（序参量被瞬时压制）是否能留下一个**特征时间常数不同的残余信号**？这关系到能否在实验上把它从 SOC 通道里剥离。
4. **与 altermagnet 的边界**：自旋点群给出的非相对论响应集合与 altermagnet 预测的功能响应是包含、相交还是互斥关系？两者在共线 AFM 的子类里如何区分？
5. **超快可调控性**：能否通过强场光场瞬时改变自旋点群归属（例如通过改变自旋轴方向），从而"打开/关闭"某些非相对论响应通道？这是我们 NSFC 项目里想推动的"光控对称性"思路的延伸。
6. **计算/实验空缺**：原文是纯理论框架，是否已有对应材料的 DFT 或光学实验验证？（原料未给实验对应信息，待补）

## 来源
- 原始材料：2025-2512.03657-nonrelativistic-functional-properties-in-collinear-antiferro.md
- 蒸馏时间：2026-10-01T18:53:17Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：自旋点群多极表示理论——共线反铁磁体中无需 SOC 存活的非相对论功能响应分类（Ogawa & Hayami，JPSJ 2026）

**原理**：基于自旋点群（spin point group）对称性对共线反铁磁体的多极矩做系统分类，识别哪些多极及其耦合的功能响应不需要自旋轨道耦合（SOC）就能存在——非相对论通道的功能响应集合在 SOC=0 极限下仍由对称性保护，是'纯磁序驱动'而非 SOC 介导；方法亮点：用多极表示理论（multipole representation theory）替代传统磁多极枚举，得到与磁点群不完全等价的分类（自旋点群比磁点群更粗但对纯共线序更自然）；产物为一套按自旋点群分类的'非相对论功能响应清单'——可作为候选材料与候选响应的对称性筛选器。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 框架 | 自旋点群多极表示理论；共线 AFM 无 SOC 仍存活的功能响应分类（纯磁序驱动通道） | 核心要点 |

**适用边界**：摘要级元数据（本页自注'已知骨架与待补全内容分开标清，不脑补'），具体多极-响应对应表、反铁磁空间群列表、数值响应大小、响应函数类型（输运/光学/磁化率）均未给出；MnPS₃ 在分类中的具体归属（磁点群/母多极）未知；与 altermagnet 功能响应的包含/相交/互斥关系未明；纯理论框架无 DFT/光学实验对应；强场 pump 后序参量压制下非相对论通道的残余信号时间常数（从 SOC 通道剥离的实验可行性）未评估。
**代表作**：Ogawa & Hayami, Nonrelativistic Functional Properties in Collinear Antiferromagnets Based on Multipole Representation Theory（JPSJ 2026；arXiv:2512.03657）
*方法卡回补 2026-10-04*

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry连接反铁磁]]
- [[MnPS3]]
- [[general-berry-mnps3-rashba-20260816]]
- [[共线反铁磁体]]
- [[多极矩]]
- [[强场超快]]
- [[强场超快光场调控反铁磁序]]
- [[自旋点群对称性]]
- [[非相对论反常输运]]
<!-- /linsai-wikilinks -->
