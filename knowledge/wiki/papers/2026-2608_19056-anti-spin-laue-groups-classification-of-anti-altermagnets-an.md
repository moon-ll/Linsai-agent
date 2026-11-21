---
title: "Anti-spin Laue groups: classification of anti-altermagnets and their representative minimal models"
type: "papers"
created: "2026-11-12T11:08:11Z"
updated: "2026-11-15T15:09:21Z"
tags: ["altermagnet", "反交变磁体", "anti-spin-Laue-group", "磁群分类", "自旋劈裂", "MAGNDATA", "dearxiv", "论文精读", "literature", "deep-read"]
related: ["Berry相位", "CrSb", "MnPS3", "NSFC-强场超快", "Paper: 2608.19056", "Rashba效应", "交变磁体", "交变磁性", "动量空间自旋极化", "劳厄群", "强场超快", "强场超快光学", "自旋劈裂"]
source_raw: "2026-2608.19056-anti-spin-laue-groups-classification-of-anti-altermagnets-an.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
updated_at: "2026-11-15T01:16:04Z"
merged_from: ["wiki/papers/2608.19056.md"]
---

# Anti-spin Laue groups: classification of anti-altermagnets and their representative minimal models

## 林赛的理解

这类对称性分类文章对我这种做实验的人反而是最实用的"地图"。交变磁性之所以这两年这么热，是因为它证明了一个反直觉的事实：净磁矩为零的反铁磁序里也可以有动量空间的自旋劈裂。而对我们做强场超快光学的人来说，"k空间有自旋结构、实空间无净磁化"的体系意味着新的光与物质相互作用通道——可以用光去驱动、去读取一个宏观上"隐形"的自旋自由度。

这篇文章补的是分类版图的另一半：他们提出"反自旋劳厄群"这个新框架，用21个群把反交变磁体（anti-altermagnets）分类清楚，再与10个自旋劳厄群拼


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：反自旋劳厄群分类框架（21 个反自旋劳厄群分类反交变磁体 + 与 10 个自旋劳厄群拼合：交变磁/反交变磁对称性版图补全 + 代表性最小模型）

**原理**：提出「反自旋劳厄群」（anti-spin Laue groups）新框架补全对称性分类版图另一半：用 21 个反自旋劳厄群把反交变磁体（anti-altermagnets，即净磁矩为零且无动量空间自旋劈裂的补偿磁序）分类清楚，再与 10 个自旋劳厄群（交变磁体类）拼合——给出交变磁性/反交变磁性完整对称性版图与代表性最小模型；「k 空间有自旋结构、实空间无净磁化」体系意味着新的光与物质相互作用通道（光驱动/读取宏观「隐形」自旋自由度）。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 分类框架 | 21 个反自旋劳厄群（反交变磁体）+ 10 个自旋劳厄群（交变磁体）拼合完整版图 + 代表性最小模型（笔记正文截断：仅保留框架开头，MAGNDATA 对照与最小模型细节未载） | 核心要点（截断前） |

**适用边界**：阅读笔记正文截断（「再与 10 个自旋劳厄群拼」处中断、仅约 30 行）——按截断前内容写薄卡、boundary 留痕，待笔记完整后升级本卡；MAGNDATA 数据库对照与代表性最小模型细节待补。
**代表作**：arXiv:2608.19056，Anti-spin Laue groups: classification of anti-altermagnets and their representative minimal models（交变磁/反交变磁对称性版图补全；笔记截断待补）
*方法卡回补 2026-11-12*

## 合并自「Paper: 2608.19056」

## 深度解析

（来自简报深度分析）

## 阅读笔记

### general-berry-mnps3-rashba-20260816

**Anti-spin Laue groups: classification of anti-altermagnets and their representative minimal models**（Lange, Jaeschke-Ubiergo, Mook, Sinova；JGU Mainz/Münster/Texas A&M；cond-mat.mtrl-sci，2026-08-19，8 页快报）

### 研究问题
反交磁体（anti-altermagnets）具有奇宇称非相对论自旋劈裂，却缺少与交磁体“自旋 Laue 群”类似的约化动量空间对称性分类。本文提出反自旋 Laue 群（anti-spin Laue groups）以补齐这一缺失，并给出系统化、材料导向的最小四带模型构造算法，使奇宇称与偶宇称非常规磁体在同一框架下平权。

### 研究背景
交磁体已有 10 个自旋 Laue 群描述其偶宇称 d/g/i 波劈裂，MnTe、CrSb 等体材实验证实。近年补偿非共线磁体扩展出奇宇称劈裂：Tt 对称（时间反演×平移）共面磁体中面内自旋期望值非相对论极限下恒为零，仅存垂直分量且 S⊥(−k)=−S⊥(k)，呈 p/f/h 波图样。既有分类只能逐群分析自旋点群/空间群，无法暴露多群共享的动量空间对称性。

### 研究方法
用符号特征 χ⊥ 把自旋点群元投影到 S⊥ 的保持/反转行为上，得空间母点群一维不可约表示 γ⊥；反自旋 Laue 群定义为其图像 L_anti={(γ⊥(g),g)|g∈G}，且与自旋 Laue 群加有效反演不同，须加有效“反演”[C2||P]。模型构造化为表示论问题：irrep 乘积规则 Γ_d1⊗Γ_d2⊗Γ_d3=Γ_S⊥（S⊥(k)∼d1(k)[d2(k)×d3(k)]⊥），区分 Type-A/B（Type-C 略去），并对 MAGNDATA 数据库穷举筛选材料。

### 主要发现
识别三类（RI_s、RII_s、RIII_s）共 21 个反自旋 Laue 群，与 10 个自旋 Laue 群共同完成共线动量空间自旋极化非常规磁体的完整分类；实现 160 个不等价共面自旋点群→21 群的多对一约化，5748 个自旋空间群全部归入三类，并证明任何 q≠0 共面磁体必具共线动量空间自旋极化。MAGNDATA 筛出 83 个候选（NiI2、NiPS3、CeNiAsO、GeCo2O4、InMnO3、ErAuIn、LuMnO3、VCl2、LaMnAu5 等）；为 4/mmm 结构（候选 Pr2PdAl7Ge4）构造 p/f/h 波代表性模型（ASLG 1̅4/2m1m1m、2̅4/2m2m1m、1̅4/2m2m2m），奇宇称分波含 p、P-f/B-f、h、j、l 波。

### 潜在研究方向
Type-C 模型（磁矩承载二维 irrep，对应自旋母群 622、422 及 n>2 的 Cn）本文未展开；框架可扩展到多自旋分量混合宇称体系与具共线 d/g/i 波极化的非共线系统。83 个候选中 NiPS3 与本课题直接相关的反交磁劈裂实验验证是后续关键方向。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：反自旋 Laue 群分类与最小四带模型构造算法（反交磁体奇宇称自旋劈裂的对称性框架 + MAGNDATA 穷举筛选）

**原理**：用符号特征 χ⊥ 把自旋点群元投影到垂直自旋分量 S⊥ 的保持/反转行为上，得空间母点群一维不可约表示 γ⊥；反自旋 Laue 群定义为图像 L_anti={(γ⊥(g), g) | g∈G}——与自旋 Laue 群（交磁体偶宇称 d/g/i 波劈裂）加有效反演不同，须加有效「反演」[C2∥P]；最小模型构造化为表示论问题：irrep 乘积规则 Γ_d1⊗Γ_d2⊗Γ_d3 = Γ_S⊥（S⊥(k)∼d1(k)[d2(k)×d3(k)]⊥），区分 Type-A/B，对 MAGNDATA 数据库穷举筛选材料——使奇宇称（anti-altermagnets）与偶宇称（altermagnets）非常规磁体在同一框架下平权。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 分类结果 | 识别三类（RI_s、RII_s、RIII_s）共 21 个反自旋 Laue 群，与 10 个自旋 Laue 群共同完成共线动量空间自旋极化非常规磁体完整分类；160 个不等价共面自旋点群 → 21 群多对一约化；5748 个自旋空间群全部归入三类；任何 q≠0 共面磁体必具共线动量空间自旋极化（证明） | 主要发现 |
| 候选材料与代表模型 | MAGNDATA 筛出 83 个候选（NiI2、NiPS3、CeNiAsO、GeCo2O4、InMnO3、ErAuIn、LuMnO3、VCl2、LaMnAu5 等）；为 4/mmm 结构（候选 Pr2PdAl7Ge4）构造 p/f/h 波代表性模型（ASLG 1̅4/2m1m1m、2̅4/2m2m1m、1̅4/2m2m2m），奇宇称分波含 p、P-f/B-f、h、j、l 波 | 主要发现 |

**适用边界**：Type-C 模型（磁矩承载二维 irrep，对应自旋母群 622、422 及 n>2 的 Cn）未展开；框架可扩展到多自旋分量混合宇称体系与具共线 d/g/i 波极化的非共线系统（尚未实现）；Tt 对称共面磁体面内自旋期望值非相对论极限恒为零、仅存垂直分量（S⊥(−k)=−S⊥(k)，p/f/h 波图样）——框架适用边界即共面磁体；83 个候选的奇宇称劈裂实验验证（尤其 NiPS3）是后续关键方向。
**代表作**：Lange, Jaeschke-Ubiergo, Mook, Sinova, Anti-spin Laue groups: classification of anti-altermagnets and their representative minimal models, arXiv:2608.19056 (2026)
*方法卡回补 2026-11-05*

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry相位]]
- [[CrSb]]
- [[MnPS3]]
- [[NSFC-强场超快]]
- [[Paper: 2608.19056]]
- [[Rashba效应]]
- [[交变磁体]]
- [[交变磁性]]
- [[动量空间自旋极化]]
- [[劳厄群]]
- [[强场超快]]
- [[强场超快光学]]
- [[自旋劈裂]]
<!-- /linsai-wikilinks -->
