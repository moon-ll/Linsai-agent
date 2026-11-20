---
title: "Low-Frequency Divergence of Circular Photomagnetic Effect in Topological Semimetals"
type: "papers"
created: "2026-11-20T05:19:26Z"
updated: "2026-11-20T05:28:31Z"
tags: ["papers", "拓扑半金属", "逆法拉第效应", "圆光磁效应", "赝自旋费米子", "Floquet工程"]
related: ["Floquet调控", "general-floquet-20261107", "光致磁性", "强场超快", "强场驱动", "拓扑半金属", "逆法拉第效应"]
source_raw: "2022-2201.06243-low-frequency-divergence-of-circular-photomagnetic-effect-in.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Low-Frequency Divergence of Circular Photomagnetic Effect in Topological Semimetals

## 林赛的理解
这篇文章击中了我一直关心的一个问题：逆法拉第效应（IFE）在低频驱动下到底如何标度。我们组在做强场红外/THz 驱动的 Floquet 工程时（见 general-floquet-20261107 提案），一直假设光致磁化在低频区行为温和，而这篇工作明确指出拓扑半金属中高赝自旋费米子的轨道矩贡献呈 ω^(-1) 低频发散标度——这直接意味着用中红外乃至 THz 场驱动拓扑半金属，可以放大地产生光致磁化。更妙的是，响应张量与能带 Chern 数直接挂钩，把拓扑不变量变成了可测的光磁响应。摘要提到红外光下磁化强度可达 1 μB/nm³ 量级，这对我们设计超快全光磁操控实验是一个非常有吸引力的数字（需读全文确认条件）。

## 核心要点
- 拓扑半金属中高赝自旋（high-pseudospin）费米子具有显著的圆光磁效应（IFE 的轨道矩贡献）。
- 低频下光致磁化按 ω^(-1) 标度发散，暗示低频/长波驱动可增强响应。
- 响应张量与能带 Chern 数直接关联：IFE 成为探测能带拓扑的光学手段。
- 红外光驱动下光致磁化可达约 1 μB/nm³ 量级（据摘要）。

## 实验/研究关联
- 与 NSFC-强场超快项目及 general-floquet-20261107 提案直接相关：低频发散标度为中红外/THz 强场驱动下的 Floquet 磁调控提供了理论依据。
- 提示可在拓扑半金属（高赝自旋费米子体系）上开展圆偏振中红外泵浦—磁化探测（如 MOKE/时间分辨磁光）实验验证 ω^(-1) 标度。
- IFE 响应张量—Chern 数的对应关系提供了一种非接触、全光学读出能带拓扑的方案。

## 开放问题
- ω^(-1) 发散在多低频率下失效？趋近共振或 Drude 耗散区是否截断该标度？
- 1 μB/nm³ 的估计依赖何种载流子密度、温度和场强条件？是否在实验可达参数范围内？
- 高赝自旋费米子在真实材料（而非模型体系）中的实现程度如何？候选材料是什么？
- 轨道矩贡献与自旋矩贡献的相对大小和可分离性——能否用实验区分？
- 与我们 Floquet 提案中缀饰态图像的自洽性：发散行为在强场（非微扰）区是否仍成立？

## 来源
- 原始材料：2022-2201.06243-low-frequency-divergence-of-circular-photomagnetic-effect-in.md
- 蒸馏时间：2026-11-20T05:19:26Z

<!-- linsai-wikilinks -->
## 关联概念

- [[Floquet调控]]
- [[general-floquet-20261107]]
- [[光致磁性]]
- [[强场超快]]
- [[强场驱动]]
- [[拓扑半金属]]
- [[逆法拉第效应]]
<!-- /linsai-wikilinks -->

## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：拓扑半金属圆光磁效应的低频发散（拓扑半金属中高赝自旋费米子的圆光磁效应（IFE 轨道矩贡献）：**光致磁化按 ω^(-1) 低频发散标度**+响应张量与能带 Chern 数直接关联=IFE 成为能带拓扑的光学探针；红外光驱动下磁化可达 ~1 μB/nm³ 量级——中红外/THz 强场驱动放大地产生光致磁化的理论依据）

**原理**：拓扑半金属中高赝自旋（high-pseudospin）费米子具有显著圆光磁效应（IFE 的轨道矩贡献）：光致磁化在低频下按 ω^(-1) 标度发散（低频/长波驱动增强响应）；响应张量与能带 Chern 数直接挂钩——把拓扑不变量变成可测的光磁响应（非接触全光学读出能带拓扑）；红外光驱动下光致磁化可达约 1 μB/nm³ 量级（摘要级估计）。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 低频标度 | 光致磁化 ∝ ω^(-1)（发散标度；失效下限频率/共振与 Drude 耗散截断未载，摘要级无 PDF） | 核心要点（摘要级） |
| 磁化量级 | 红外光驱动下 ~1 μB/nm³（依赖载流子密度/温度/场强条件待全文，摘要级） | 核心要点（摘要级） |

**适用边界**：摘要级来源（无 PDF）——ω^(-1) 发散在多低频率下失效（共振/Drude 耗散区是否截断）待全文；1 μB/nm³ 估计的具体条件（载流子密度/温度/场强）与实验可达性待核；高赝自旋费米子真实材料实现程度与候选材料不明；轨道矩与自旋矩贡献的相对大小及实验可分离性待查；发散行为在强场非微扰区是否仍成立（与 Floquet 缀饰态图像自洽性）待评估；圆偏中红外泵浦+MOKE/时间分辨磁光探测为直接验证路线。
**代表作**：arXiv:2201.06243（2022），Low-Frequency Divergence of Circular Photomagnetic Effect in Topological Semimetals（ω^(-1) 低频发散 IFE+Chern 数光磁响应素材；floquet 提案直接相关）
*方法卡回补 2026-11-20*
