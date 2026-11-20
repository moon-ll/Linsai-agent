---
title: "Band splitting in the altermagnet CrSb (Mineev, PRB 2026)"
type: "papers"
created: "2026-09-27T10:54:32Z"
updated: "2026-11-15T15:09:19Z"
tags: ["altermagnet", "CrSb", "spin-splitting", "magnetic-group-theory", "ultrafast-order-parameter-readout"]
related: ["CrSb", "alternagnetism", "arpes", "general-order-parameter-ultrafast-readout", "general-order-parameter-ultrafast-readout-20260727", "pump-probe", "spin-group-symmetry", "ultrafast-magneto-optics", "交变磁体", "强场超快", "强场超快光学", "强场驱动", "非线性光学"]
source_raw: "2026-PhysRevB.114.065130-band-splitting-in-the-altermagnet-crsb.md"
growth_stage: "growing"
confidence: 0.55
auto_grown: true
review_status: "pending"
aliases: ["PRB"]
digest_level: "abstract"
---

# Band splitting in the altermagnet CrSb (Mineev, PRB 2026)

## 林赛的理解

Mineev 这篇文章我必须认真读。强场超快光学这一块，对 altermagnet 的兴趣不只是"新一类磁序"这种说法——而在于 altermagnet 的 band splitting 既有交换（exchange）贡献，又额外叠加了由磁群（magnetic group）对称性约束产生的部分。这意味着即使在零净磁化的状态下，spin-resolved 的 band 结构仍然存在，而超快 pump-probe、MOKE、二次谐波这些手段有可能在不依赖宏观磁化的情况下读出 order parameter。我团队目前在推进的 "general-order-parameter-ultrafast-readout" 提案，正缺这种"对称性预言的、可被时域光学信号验证的 band splitting"作为微观抓手。CrSb 是已知 altermagnet 体系里相对干净的候选，Mineev 用磁群形式把它做了规范化梳理，正合所需。

## 核心要点

- **体系与对象**：CrSb，典型 altermagnet（零净磁化、但具有自旋分裂的能带）。
- **方法亮点**：使用 magnetic-groups formalism（磁群形式体系）而非单纯的空间群来分析能带劈裂——这是关键。空间群只允许平庸的自旋简并解除，而磁群能捕捉由"自旋空间 + 晶格空间"联合操作产生的新对称约束。
- **核心论断**：在交换近似（exchange approximation）之外，CrSb 的 band splitting 存在**额外来源**——这部分由磁群对称性决定，是 altermagnet 的"signature"，也是与普通反铁磁体的根本区别。
- **物理图像（基于磁群惯例的理解）**：CrSb 的 Néel 矢量方向连接两套子晶格，其磁点群允许 spin-up / spin-down 在动量空间中按特定对称模式（典型为 d-wave / g-wave 型节点结构）分裂，这部分不能被简单海森堡交换所还原。
- **应用层面（推断）**：这种对称性起源的劈裂对超快激发下的 order parameter dynamics 极其敏感——任何打破磁群对称的操作（光场极化、应力脉冲、强 THz 驱动）都会立即反映在 spin-splitting 的可探测信号中。

## 实验/研究关联

- **直接对接提案**：`used_by_proposals: general-order-parameter-ultrafast-readout-20260727`——本文正是该提案的文献支撑：论证"order parameter 的微观可观测载体是 band splitting"，从而证明用光学手段读出 order parameter 在原理上是合法的。
- **与强场超快实验的接口**：
  - **时间分辨 MOKE / 二阶非线性光学**：在 pump 后跟踪 Néel 矢量重定向时，band splitting 的角度依赖会直接调制 SHG / MOKE 张量元——这是 altermagnet 区别于反铁磁的可观测量。
  - **高次谐波（HHG）**：强场条件下，HHG 的偏振依赖已被证明能映射晶体对称性；推广到磁群对称性，可以做 altermagnet 的"全光对称性诊断"。
  - **TR-ARPES 对照**：希望实验组能给出 fs-时间分辨的 spin-resolved band map，与 Mineev 的磁群预测做直接对照。
- **理论—实验闭环的缺口**：本文目前 abstract 为空、PDF 标记为 false；我读到的核心信息来自标题级 metadata + 二次笔记。"额外 spin splitting 究竟有多大""在布里渊区哪些节点处最显著""是否对 Néel 矢量重取向有非平庸响应"这些定量问题都还需要从正文里挖。

## 开放问题

1. **定量量级缺失**：磁群贡献的 band splitting 在 CrSb 里是 meV 量级还是更大？这直接决定超快实验中能否在 fs–ps 时间窗内被分辨。
2. **Néel 矢量方向依赖**：CrSb 已知有自旋重取向行为（spin-flop / reorientation），Mineev 的磁群分析在哪个 Néel 取向上给出的 splitting 谱最强？这是设计 pump-polarization 实验的关键。
3. **vs. exchange-only 模型的可区分观测量**：是否存在某个动量点或光学张量元，能够在实验上**无歧义**地区分"纯交换劈裂"与"磁群附加劈裂"？如果没有，这篇工作的可观测性就只停在能带计算层。
4. **与 RuO₂ / MnTe 等其他 altermagnet 的可比性**：磁群形式体系是否对所有 d-wave / g-wave / i-wave altermagnet 给出统一预言，还是对 CrSb 这类六角结构有特殊结论？这关系到我们后续是否要把 readout 方法拓展到其他体系。
5. **强场驱动的对称破缺**：用强 THz / 中红外脉冲瞬时打破磁群对称后，band splitting 的瞬态演化能否被读出？这是 Mineev 这种静态磁群分析留给动态实验的"接口问题"，也是我团队下一步可以设计的实验。

## 来源
- 原始材料：2026-PhysRevB.114.065130-band-splitting-in-the-altermagnet-crsb.md
- 蒸馏时间：2026-09-27T10:54:32Z
- 关联元数据：score_deepxiv 0.82，status pool→unseen，arxiv_id PhysRevB.114.065130
- 待补：原文 PDF、完整 abstract、具体数值结果（abstract 为空，需调取原文）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：磁群形式体系分析交变磁体 CrSb 的能带劈裂——交换近似之外的磁群对称性额外来源（Mineev，PRB 2026）

**原理**：用 magnetic-groups formalism（磁群形式体系）而非单纯空间群分析 CrSb（零净磁化但有自旋分裂能带的典型 altermagnet）：空间群只允许平庸的自旋简并解除，磁群能捕捉'自旋空间+晶格空间'联合操作产生的新对称约束；核心论断：交换近似之外 CrSb 的 band splitting 存在额外来源——该部分由磁群对称性决定，是 altermagnet 的 signature、与普通反铁磁的根本区别；物理图像：Néel 矢量连接两套子晶格，磁点群允许 spin-up/down 按特定对称模式（典型 d-wave/g-wave 节点结构）在动量空间分裂，不能被简单海森堡交换还原；对称性起源的劈裂对超快激发下的序参量动力学极敏感（光场极化/应力脉冲/强 THz 驱动破缺磁群对称立即反映在 spin-splitting 可探测信号中）。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 理论框架 | 磁群形式体系（magnetic-group formalism）；交换近似之外磁群对称性决定的额外 band splitting（altermagnet signature） | 核心要点 |

**适用边界**：摘要级页面且 abstract 为空（本页自注'核心信息来自标题级 metadata + 二次笔记'），磁群贡献劈裂的定量量级（meV 或更大）、在布里渊区哪些节点最显著、对 Néel 矢量重取向的非平庸响应均需从正文挖；CrSb 已知自旋重取向（spin-flop）下哪个 Néel 取向劈裂最强未明；'纯交换劈裂'与'磁群附加劈裂'的可区分观测（动量点/光学张量元）未给；磁群形式对 d/g/i-wave 各体系的统一性（vs CrSb 六角结构特殊性）未确认；强 THz/中红外瞬时破缺磁群后劈裂瞬态演化的动态接口留给实验。
**代表作**：Mineev, Band splitting in the altermagnet CrSb（磁群形式体系，PRB 114, 065130, 2026，deepxiv 0.82）
*方法卡回补 2026-10-04*

<!-- linsai-wikilinks -->
## 关联概念

- [[CrSb]]
- [[alternagnetism]]
- [[arpes]]
- [[general-order-parameter-ultrafast-readout]]
- [[general-order-parameter-ultrafast-readout-20260727]]
- [[pump-probe]]
- [[spin-group-symmetry]]
- [[ultrafast-magneto-optics]]
- [[交变磁体]]
- [[强场超快]]
- [[强场超快光学]]
- [[强场驱动]]
- [[非线性光学]]
<!-- /linsai-wikilinks -->
