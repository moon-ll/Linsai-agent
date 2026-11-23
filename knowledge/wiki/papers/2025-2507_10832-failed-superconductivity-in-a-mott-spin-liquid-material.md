---
title: "Failed superconductivity in a Mott spin liquid material"
type: "papers"
created: "2026-10-05T18:52:21Z"
updated: "2026-11-15T15:09:19Z"
tags: ["Mott自旋液体", "量子相变", "超导-金属转变", "有机导体", "磁电输运"]
related: ["2507.10832", "Mott转变", "general-bsv-driven-hhg-quantum-20260726", "κ-(BEDT-TTF)2X体系", "固体HHG", "强场THz光谱", "强场超快", "强场超快光学", "普适电导涨落", "电荷密度波", "量子超导-金属转变"]
source_raw: "2025-2507.10832-failed-superconductivity-in-a-mott-spin-liquid-material.md"
growth_stage: "growing"
confidence: 0.6
digest_level: "abstract"
auto_grown: true
review_status: "pending"
updated_at: "2026-10-11T01:01:12Z"
merged_from: ["wiki/papers/2507.10832.md"]
---

# Failed superconductivity in a Mott spin liquid material

## 林赛的理解

作为做强场超快光学的 PI,我对这类"量子临界"体系的兴趣主要不在其平衡态输运本身,而在于:当系统被推到超导-金属量子相变(QSMT)边界附近时,微观的配对振幅(pair amplitude)是否仍存在?如果存在,它的时间尺度、相位相干长度、以及它如何被光场"撬动"或"拆解",正是强场 THz 和中红外泵浦-探测能直接回答的问题。Wang 等人在 κ-STFx 这种化学替代的有机莫特自旋液体中观测到全局超导被压制但仍存在局域超导畴(inhomogeneous SC),并报告了高场下的普适电导涨落(UCF),这给我提供了一条思考的轴线——**在 T→0 的量子金属中,残留的相位相干如何响应光场驱动?**

## 核心要点

- **材料体系**:化学替代的 κ-STFx 有机莫特自旋液体(基于 BEDT-TTF 类分子导体家族)。
- **核心实验手段**:磁电输运(magnetotransport)与交流磁化率(ac susceptibility)联合表征。
- **核心发现**:
  - 即使温度趋于零,**全局性超导始终无法建立**,即超导转变温度被压制到 T_c → 0。
  - 系统处于一种由**嵌入在渗流金属中的超导畴**构成的 mixed state。
  - 在高磁场下出现**量子超导-金属转变(quantum superconductor-to-metal transition, QSMT)**的指纹。
  - 高场区观测到**普适电导涨落(universal conductance fluctuations, UCF)**,提示介观尺度相位相干的消失。
- **物理解读**:莫特自旋液体母体中可能存在预成对(preformed pairs)或局域相位刚度,但不足以跨越渗流阈值实现长程相位相干;化学替代和磁场共同将体系推到了量子临界点。

## 实验/研究关联

- **与林赛组强场 THz 泵浦-探测的关联**:在 QSMT 附近,超导涨落的特征时间(相位弛豫时间 τ_φ)对温度与磁场的响应极为敏感。单周期或亚周期强场 THz 脉冲可以直接驱动 Cooper 对的 Higgs 模,如果在 κ-STFx 中能观测到残余的集体模响应,即可推断超导畴的动力学完整性。
- **与 HHG 量子路径的关联**:该工作被标记为与"general-bsv-driven-hhg-quantum"相关。在强关联边缘,价带的相干性下降会使高次谐波发射的效率、偏振特性、多平台结构发生显著变化,这正是我们目前关注的方向。κ-STFx 这种"几乎但不超导"的态,可能提供比纯超导样品更丰富的 HHG 谱学信息——因为部分相干、部分涨落的体系对驱动场的非线性响应会显著放大。
- **方法借鉴**:磁电输运 + 局域磁化率 + UCF 分析的多探针联合判定量子临界性的思路,可以平移到**时间分辨版本**:用时间分辨磁化率(例如 Faraday/Kerr 旋转动力学)替代静态 ac susceptibility,用时间分辨电导涨落谱替代 UCF,直接测量相干性崩塌的时间结构。

## 开放问题

- 残留超导畴的特征尺度与化学替代浓度的关系是什么?是否可以通过调节组分将体系"冷冻"到 QSMT 的临界侧?
- 普适电导涨落(UCF)在高场下出现,意味着相位相干体积的临界行为——这是否对应一个**有限温度的量子临界扇区**,可以由 ac susceptibility 提取出动态临界指数?
- 在这种"failed SC"体系中,**Cooper 对预成对温度 T\* 与长程相位相干温度 T_θ 的分离**是否显著?这是 fs 时间分辨光学能直接区分的。
- 强场 THz 脉冲能否**人为重建相位相干**(即"光致超导")?在 QSMT 临界侧,理论上相干长度对驱动场最敏感。
- 化学替代引起的无序与莫特物理的纠缠:QSMT 是由无序驱动的(BM-SM 类)还是由量子涨落驱动的?UCF 的标度行为可能给出判据。

## 来源
- 原始材料:2025-2507.10832-failed-superconductivity-in-a-mott-spin-liquid-material.md
- 蒸馏时间:2026-10-05T18:52:21Z


## 合并自「2507.10832」

## 深度解析

（来自简报深度分析）

## 阅读笔记

### general-bsv-driven-hhg-quantum-20260726

**标题**: Failed superconductivity in a Mott spin liquid material  
**作者**: Yuxin Wang, Vladimir Dobrosavljević, Eun Sang Choi, Yohei Saito, Atsushi Kawamoto, Andrej Pustogow, Martin Dressel, Dragana Popović  
**arXiv**: 2507.10832 [cond-mat.supr-con]，2025-07-14 v1

### 研究问题
在准二维 κ-有机自旋液体（带宽调控的 Mott 金属-绝缘体转变附近、无其他竞争序的单带系统）中，超导涨落如何出现又为何"失败"——即为何零温下全局超导无法建立、而代之以嵌于金属逾渗团簇中的超导畴？

### 研究背景
κ-(BEDT-TTF)₂X（X = Cu[N(CN)₂]Br、Cu[N(CN)₂]Cl 等）是有机电荷转移盐家族中的范本：单 Hubbard 带、半填充、强关联、无磁性长程序或电荷密度波等竞争，是检验 Mott转变与非常规超导配对机制的"清洁平台"。前人工作确立该体系存在带宽调控的 Mott转变与超导圆顶；本文聚焦在 Mott 绝缘体-费米液体相共存区，观察超导的失稳行为。

### 研究方法
化学取代 κ-有机盐以调控带宽；磁输运（magnetotransport）测量电阻随磁场、温度的演化；交流磁化率（ac susceptibility）探测超导涨落；通过加磁场驱动量子超导-金属相变（superconductor-to-metal transition）以表征超导畴尺度与逾渗几何。

### 主要发现与核心结论
发现 1：尽管存在明显超导涨落信号，零温极限下全局超导无法建立，电阻不消失。发现 2：体系实际状态为金属逾渗团簇中嵌入的超导畴（superconducting domains embedded in metallic percolating cluster），其在磁场下经历量子超导-金属相变。发现 3：交流磁化率结果提示虽未达全局零电阻，但相位相干长度仍可在有限畴内建立。这一结果为研究强关联单带系统中的配对与相位相干解耦提供了非常干净的实验平台。

### 潜在研究方向
- 与课题的接口：在 BSV 驱动的固体 HHG 框架下，Mott 自旋液体（如 κ-有机）作为电子关联极端化但又能与量子光耦合的候选介质，其涨落如何转译到谐波谱与光子统计是未开发的方向。
- 揭示了"配对成功但相位失败"机制，需进一步研究超导畴的空间分布、尺寸分布以及与逾渗几何的关系；
- 探索其他单带 Mott 候选（三角格子、蜂窝格子有机盐）中是否出现同样现象；
- 压力、化学取代、磁场扫描的相图补全，以厘清超导-金属量子相变的普适临界指数。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：化学取代带宽调控 + 磁输运/交流磁化率探测超导畴逾渗

**原理**：研究 κ-有机 Mott 自旋液体中超导涨落为何'失败'（零温全局超导不建立）。核心机制：化学取代调控带宽 → 磁输运测电阻随磁场/温度演化 → 交流磁化率探测超导涨落 → 磁场驱动量子超导-金属相变以表征超导畴尺度与逾渗几何；发现体系实为金属逾渗团簇中嵌入的超导畴，配对（有限畴内相位相干可建立）与全局相位锁定解耦——'配对成功但相位失败'。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 体系 | κ-(BEDT-TTF)₂X 有机电荷转移盐（单 Hubbard 带、半填充、强关联、无竞争序） | 研究背景 |
| 调控手段 | 化学取代带宽调控 + 磁场驱动量子超导-金属相变 | 研究方法 |
| 探针组合 | 磁输运（电阻-磁场/温度演化）+ 交流磁化率（超导涨落） | 研究方法 |

**适用边界**：超导畴空间分布/尺寸分布与逾渗几何的关系为后续方向；压力/化学取代/磁场扫描的完整相图与量子相变普适临界指数未完成。
**代表作**：Yuxin Wang, V. Dobrosavljević, ..., M. Dressel, D. Popović, Failed superconductivity in a Mott spin liquid material, arXiv:2507.10832 (2025)
*方法卡回补 2026-10-04*

<!-- linsai-wikilinks -->
## 关联概念

- [[2507.10832]]
- [[Mott转变]]
- [[general-bsv-driven-hhg-quantum-20260726]]
- [[κ-(BEDT-TTF)2X体系]]
- [[固体HHG]]
- [[强场THz光谱]]
- [[强场超快]]
- [[强场超快光学]]
- [[普适电导涨落]]
- [[电荷密度波]]
- [[量子超导-金属转变]]
<!-- /linsai-wikilinks -->
