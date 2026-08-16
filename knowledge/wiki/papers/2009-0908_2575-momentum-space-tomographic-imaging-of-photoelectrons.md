---
title: "论文精读：动量空间光电子层析成像——用偏振旋转+滤波反投影重建三维动量分布（Smeenk et al. 2009）"
type: "papers"
created: "2026-08-15T18:09:37Z"
updated: "2026-08-15T18:09:37Z"
tags: ["论文精读", "强场电离", "光电子动量分布", "VMI", "层析成像", "Abel反演", "椭圆偏振", "滤波反投影"]
related: ["ATI高阈电离", "Abel逆变换", "COLTRIMS反应显微镜", "Radon变换", "强场隧穿电离", "速度映射成像VMI"]
source_raw: "2009-0908.2575-momentum-space-tomographic-imaging-of-photoelectrons.md"
growth_stage: "growing"
confidence: 0.7
auto_grown: true
review_status: "pending"
---

# 论文精读：Momentum Space Tomographic Imaging of Photoelectrons（Smeenk, Arissian, Staudte, Villeneuve & Corkum, J. Phys. B 2009）

## 林赛的理解

这是 Corkum 组（NRC/渥太华大学联合阿秒实验室）2009 年的方法学论文。在强场这个圈子里泡了这么多年，我对 VMI + Abel 反演的痛点再熟悉不过：只要偏振一变成椭圆、分子一排列、或者动量分布出现任何前后不对称，Abel 就失效——剩下的选项要么上 COLTRIMS（昂贵、复杂、分辨率打折），要么干脆放弃三维信息。这篇论文给出了一条很“光学”的出路：与其转动探测器或样品，不如转动光。用波片旋转激光偏振方向，在各向同性原子气体中电子动量分布会随之刚性旋转，逐角度记录 2D 投影，再用经典 CT 的滤波反投影重建完整三维分布。

我特别欣赏的一点是它的低门槛化：一台普通 2D VMI 加一个旋转波片，就能做原本需要反应显微镜才能完成的全三维动量测量。而且他们用线偏振下的 Abel 反演结果作为内置 benchmark，层

<!-- linsai-wikilinks -->
## 关联概念

- [[ATI高阈电离]]
- [[Abel逆变换]]
- [[COLTRIMS反应显微镜]]
- [[Radon变换]]
- [[强场隧穿电离]]
- [[速度映射成像VMI]]
<!-- /linsai-wikilinks -->
