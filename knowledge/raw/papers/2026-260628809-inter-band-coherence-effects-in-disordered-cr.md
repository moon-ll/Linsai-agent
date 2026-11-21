---
title: "Inter-band coherence effects in disordered crystals: beyond the non-crossing approximation"
arxiv_id: "2606.28809"
authors: "Zhanning Wang, James H. Cullen, Roberto Raimondi, Dimitrie Culcer"
year: 2026
tags: ["deepxiv-论文库"]
project: ["NSFC-强场超快"]
direction: "能谷电子学"
source: "hermes-briefing"
imported_at: "2026-08-30T23:20:04Z"
score_deepxiv: 0.5
status: "unseen"
read_status: "unread"
has_pdf: false
---
# Inter-band coherence effects in disordered crystals: beyond the non-crossing approximation

## 摘要
We develop a quantum kinetic theory for Bloch electrons driven by a uniform dc electric field, extending the nonequilibrium density-matrix formalism beyond the non-crossing approximation. This extension is required to capture steady-state terms that are nominally zeroth order in disorder strength and compete with intrinsic band-geometric responses, as in anomalous Hall and related spin, orbital, and valley transport. Working in the length gauge with Gaussian white-noise disorder, we include impurity scattering to fourth order in the disorder potential. An iterative solution for the impurity-induced density-matrix fluctuations yields a connected V^4 collision integral after subtracting disconnected impurity pairings, thereby avoiding double counting. The resulting terms separate into self-energy corrections, ladder-type vertex renormalization, and crossed quantum-interference contributions. We clarify the correspondence between this density-matrix kinetic equation and the Keldysh formalism, and decompose the response into Fermi-surface and Fermi-sea components. As an application, we study the two-dimensional massive Dirac fermion model. We obtain analytical expressions for the single-particle lifetime, transport relaxation time, and longitudinal conductivity at the Born level, and then evaluate the anomalous Hall conductivity including crossed impurity processes. These processes generate an extrinsic contribution of order τ^0 that coexists with the intrinsic Berry-curvature term; for Gaussian white-noise disorder in this model, the Ψ-type contribution cancels while the X-type term remains finite. The formalism provides a consistent route for incorporating band geometry and crossed-disorder corrections into multiband transport, with applications to spin, pseudospin, orbital, and valley phenomena.

## 背景概述与问题引入
反常霍尔及相关自旋/轨道/谷输运的内禀贝里曲率响应与无序诱导的外禀贡献共存，但标准输运动理学（非交叉近似，即梯形图求和）在名义上无序零阶的稳态项上会失灵——这些项与内禀能带几何响应同阶竞争。要在密度矩阵框架内系统处理交叉量子干涉贡献，需要把杂质散射展开到无序势四阶并正确扣除非连通配对。

## 关键发现及核心讨论
- **连通 V^4 碰撞积分**：对杂质诱导密度矩阵涨落做迭代求解，扣除非连通杂质配对后得到无重复计数的四阶碰撞积分；分解为自能修正、梯形顶点重整化和交叉量子干涉三类贡献。
- **与 Keldysh 形式的对应**：明确了密度矩阵动理学方程与 Keldysh 形式体系的对应关系，并把响应对称分解为费米面与费米海分量。
- **2D massive Dirac 模型解析结果**：Born 阶给出单粒子寿命、输运弛豫时间、纵向电导解析式；包含交叉杂质过程后反常霍尔电导出现 τ^0 阶外禀贡献与内禀贝里曲率项共存——高斯白噪声下 Ψ 型贡献相消，X 型保持有限。

## 主要方法
- 长度规范 + 高斯白噪声无序的非平衡密度矩阵形式体系，杂质势展开至四阶。
- 迭代求解密度矩阵涨落 + 连通图筛选（扣除非连通配对避免双重计数）。
- 应用体系：二维 massive Dirac 费米子模型（解析输运系数）。

## 创新性
把非平衡密度矩阵动理学系统推进到非交叉近似之外：给出交叉量子干涉贡献的显式碰撞积分结构，使带几何与交叉无序修正在多带输运中可以一致纳入。

## 结论与展望
形式体系可直接用于自旋、赝自旋、轨道与谷现象的多带输运。对强场驱动体系（直流极限），带间相干效应与交叉无序过程是稳态响应不可忽略的成分——这也是固体 HHG 中带间极化 + 散射建模需要警惕的同阶竞争项。