---
title: "2022-s41598-022-12348-5-attosecond-stable-dispersion-free-delay-line-for-easy-ultraf"
type: "papers"
created: "2026-09-27T03:21:58Z"
updated: "2026-11-15T15:09:20Z"
tags: []
related: ["FROG", "general-quantum-geometry-inversion-20260726", "阿秒科学"]
source_raw: "2022-s41598-022-12348-5-attosecond-stable-dispersion-free-delay-line-for-easy-ultraf.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
aliases: ["10.1038/s41598-022-12348-5", "s41598-022-12348"]
digest_level: "abstract"
---

• ---
  title: "Attosecond stable dispersion-free delay line for easy ultrafast metrology"
  type: papers
  created: "2026-09-27T03:21:41Z"
  updated: "2026-09-27T03:21:41Z"
  tags: ["超快计量", "延迟线", "干涉仪", "色散补偿", "阿秒稳定性"]
  related: ["超快激光", "光学干涉测量", "脉冲表征"]
  source_raw: "2022-s41598-022-12348-5-attosecond-stable-dispersion-free-delay-line-for-easy-ultraf.md"
  growth_stage: "growing"
  confidence: 0.7
  auto_grown: true
  review_status: "pending"
  ---

  # Attosecond stable dispersion-free delay line for easy ultrafast metrology

  ## 林赛的理解

  这篇文章（Krishna et al., Scientific Reports, 2022）的核心思想我很熟悉：用一个**无色散的刀刃棱镜（knife-edge prism）分束干涉延迟线**，同时实现大于 500 fs 的延迟扫描范围和亚飞秒乃至阿秒量级的机械/光学稳定性。这类器件在超快计量里是"基础设施"级别的贡献——不追求新奇物理，而是解决我们每天实际面对的老问题：传统延迟线要么用双通平移台（扫描范围受限于行程，且长行程下指向漂移严重），要么用延迟块切换（离散、不便）。

  "Dispersion-free" 这个卖点值得注意：刀刃棱镜让两束光在半透膜上"空间分离"而不是用分束镜反射，原理上避免了材料色散对两臂的影响——这对宽带超快脉冲（尤其是 <10 fs 脉冲和 UV/XUV 波段）是关键，因为两臂哪怕引入不对称的二阶/三阶色散，干涉条纹的包络和相位都会失真。

  但坦白说，目前我手上只有一句话级别的元数据，正文的信噪比数据、稳定性测试方法（是 Allan deviation 还是干涉条纹相位直方图？）、波长适用范围都没有。我按"值得收藏、待精读"处理它，不做过度推断。

  ## 核心要点

  - **器件定位**：刀刃棱镜分束的无色散干涉延迟线，面向"易用型超快计量"（easy ultrafast metrology）——强调搭建和维护门槛低。
  - **延迟范围**：> 500 fs，覆盖绝大多数泵浦-探测和干涉表征需求（FTIR 类 IAC / SPIDER / SEA-FROG 等）。
  - **稳定性**：声称达到阿秒级稳定——即两臂光程差的漂移远低于光周期量级，长时间积分下条纹相位不跑。
  - **色散特性**：器件级无色散设计，避免了延迟量扫描时两臂色散量变化引入的系统误差。

  ## 实验/研究关联

  - 我们的强场 HHG / 阿秒科学实验里，泵浦-探测和 XUV 表征链路都依赖稳定延迟线；阿秒级光程稳定对高次谐波光谱干涉、attosecond streaking 类测量是硬性要求。
  - 该课题已被 `general-quantum-geometry-inversion-20260726` 课题引用，作为超快计量仪器层面的支撑文献。
  - 若器件真如所述"易搭建"，可作为我们实验室自制延迟线的参考方案，降低对商用长行程平移台的依赖。

  ## 开放问题

  - 阿秒稳定性的具体测试手段和环境条件（温度、振动隔离）未在元数据中给出——这是判断可复现性的关键，需读正文确认。
  - 适用波长范围（是否覆盖我们关心的 800 nm 基频与 XUV 波段）未给出。
  - >500 fs 延迟扫描内的线性度和迟滞（hysteresis）表现未知。
  - 与旋转玻璃块（pair of wedges）方案、以及商用 attocube 压电平移台的性价比对比，需要正文数据支撑。

  ## 来源
  - 原始材料：2022-s41598-022-12348-5-attosecond-stable-dispersion-free-delay-line-for-easy-ultraf.md
  - 蒸馏时间：2026-09-27T03:21:41Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：刀刃棱镜无色散阿秒稳定延迟线（>500 fs 扫描范围 + 阿秒级稳定：易用型超快计量基础设施）【摘要级薄卡】

**原理**：刀刃棱镜（knife-edge prism）分束的干涉延迟线：两束光在半透膜上空间分离而非用分束镜反射，器件级避免延迟扫描时两臂材料色散变化引入的系统误差（对 <10 fs 宽带脉冲与 UV/XUV 波段关键——不对称二阶/三阶色散会使干涉条纹包络与相位失真）。同时实现大于 500 fs 的延迟扫描范围与亚飞秒至阿秒量级的光程稳定性（两臂光程差漂移远低于光周期，长时间积分条纹相位不跑）。定位：泵浦-探测、IAC/SPIDER/SEA-FROG 类干涉表征的'基础设施'级器件，强调搭建维护门槛低。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 关键指标 | 延迟扫描范围 >500 fs；稳定性达阿秒量级；色散自由（器件级） | 核心要点（摘要级，测试方法未入库） |

**适用边界**：摘要级薄卡：阿秒稳定性的具体测试手段（Allan deviation/条纹相位直方图）与环境条件（温度/隔振）未入库；适用波长范围（800 nm/XUV）未给；>500 fs 扫描内线性度与迟滞未知；与旋转玻璃块对/商用压电平移台的性价比对比缺正文数据。
**代表作**：Krishna et al., Sci. Rep. (2022), DOI: 10.1038/s41598-022-12348-5；关联课题 general-quantum-geometry-inversion-20260726（计量仪器支撑）
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[FROG]]
- [[general-quantum-geometry-inversion-20260726]]
- [[阿秒科学]]
<!-- /linsai-wikilinks -->
