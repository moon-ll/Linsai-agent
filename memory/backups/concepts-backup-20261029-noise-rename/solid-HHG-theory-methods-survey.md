---
title: "固体 HHG 的 SBE 理论框架：规范选择、Berry 几何与扩展三步模型"
type: "concepts"
created: "2026-08-15T05:51:46Z"
updated: "2026-10-24T11:03:23Z"
tags: ["固体HHG", "半导体布洛赫方程", "规范选择", "Berry曲率", "退相干", "TMD谷电子学"]
related: ["2025-2508_07869-semiconductor-bloch-equations-in-wannier-gauge-with-well-beh", "2508.07869", "Berry 曲率", "Berry联络", "Wannier规范", "三步模型", "层间耦合", "相位匹配", "隧穿时间", "非经典光"]
source_raw: "solid-HHG-theory-methods-survey.md"
growth_stage: "mature"
confidence: 0.7
auto_grown: true
review_status: "pending"
---

# 固体 HHG 的 SBE 理论框架：规范选择、Berry 几何与扩展三步模型

## 林赛的理解

我是做气体 HHG 出身的，最早把固体的电子-空穴回碰当成“固体版三步模型”来理解——这个直觉对了一半。Yue & Gaarde 那篇 2102.11964 纠正了我两个根深蒂固的习惯性假设：隧穿不一定发生在最小带隙（Γ 点），回碰也不必完美。**不完美回碰**——电子-空穴在实空间还分离着就能复合发射——在很多常见实验条件下反而主导谐波发射。这直接解释了为什么我们组在中红外驱动 ZnO 时，椭圆率依赖比气体情形“钝”得多：如果发射主要来自完美回碰，椭圆率扫下去信号应该死得更快。

规范问题是我最踩过坑的地方。学生用速度规范跑 SBE，带数截断不够时结果漂移；更危险的是 h-BN 这类无反演对称材料，忽略跃迁偶极相位（TDP）和 Berry 联络，直接给出**非物理的谐波谱**——看着像结果，其实是规范伪影。我现在的组规是：VG/LG 双规范交叉验证，凡涉及电流分解或退相干的计算走长度规范（LG，少带即可收敛），只看总电流时用速度规范（VG，结构规范独立、更快），Berry 联络必须用平滑规范处理，最终只信任规范不变量（Berry 曲率、总电流、谐波谱）。

退相干时间 $T_2$ 我一直当作唯象参数对待，但 2508.07869 提醒我常退相干算符（CDO）在带交叉附近有 $1/|E_m-E_n|$ 型奇点，会在载流子分布上打出非物理扭结——这对我们从 HHG 谱反演带结构是系统性污染源。平滑退相干算符（SDO）是个实用的补丁。

最有实验想象力的是 TMD 方向：Yoshikawa 组用 4.8 μm 中红外在单层 MoSe₂/WSe₂ 上做到 18 阶，zigzag 激发下偶次谐波垂直偏振、奇次平行——这套选择定则把谷指标和晶格对称性直接写进了偏振态。对我们组来说，这相当于一个全光学的 Berry 曲率/层间耦合探针，不用电极、不用磁场。

## 核心要点

### 定义

**半导体布洛赫方程（SBE）** 是描述强激光场下多带固体中密度矩阵演化的耦合方程组，是固体 HHG 理论建模的主力框架。它统一描述两条发射通道——带间极化电流与带内加速电流——并通过跃迁偶极/Berry 联络天然携带能带几何信息。围绕 SBE 的三个核心技术议题构成本概念页面：

1. **规范选择**（结构规范 vs 激光规范；速度规范 vs 长度规范；Wannier 规范）
2. **Berry 几何效应**（Berry 联络/曲率、谷指标、层间耦合对 HHG 的印记）
3. **扩展三步模型**（全 BZ 隧穿、不完美回碰、鞍点分析）

### 物理直觉

- **扩展三步模型**：传统图像假设电子在最小带隙处隧穿并完美回碰。实际在常见实验场景中，电子-空穴对在最小带隙之外的整个 BZ 产生，且以不完美回碰（复合时电子-空穴仍空间分离）为主导发射机制。有效跃迁偶极 $\boldsymbol{\mathcal{Q}}^{\mathbf{k}}=\Delta\boldsymbol{\mathcal{A}}^{\mathbf{k}}-\mathbf{d}^{\mathbf{k}}$（Berry 联络差减跃迁偶极）同时进入能量与动量两个鞍点方程，把几何相位效应编码进谐波相位。
- **双通道发射**：带间电流来自极化的复合（“再结合辐射”），带内电流来自晶体动量空间中的加速（非线性电流）。谐波谱的阶次结构与偏振依赖是两通道干涉的指纹。
- **规范与可观测量**：Bloch 态可带任意 $\mathbf{k}$ 依赖相位，Berry 联络 $\boldsymbol{\mathcal{A}}_n^{\mathbf{k}}$ 是规范依赖量，Berry 曲率 $\boldsymbol{\Omega}_n=\nabla_{\mathbf{k}}\times\boldsymbol{\mathcal{A}}_n^{\mathbf{k}}$ 是规范不变量。物理结论（谐波谱、总电流）必须规范无关；规范选择只影响数值表现（收敛速度、电流分解的自然性、奇点行为）。
- **退相干的双重角色**：$T_2$ 既是模拟与实验对齐的关键唯象参数，又是数值陷阱来源——CDO 在简并/带交叉处的发散会制造非物理的 k 空间扭结。

### 数学表达

**SBE 完整形式（速度规范）**：

$$
\dot{\rho}_{mn}^{\mathbf{K}}(t) = -i\left[E_m^{\mathbf{K}+\mathbf{A}(t)}-E_n^{\mathbf{K}+\mathbf{A}(t)}-\frac{i(1-\delta_{mn})}{T_2}\right]\rho_{mn}^{\mathbf{K}}(t) - i\mathbf{F}(t)\cdot\sum_l\left[\mathbf{d}_{ml}^{\mathbf{K}+\mathbf{A}(t)}\rho_{ln}^{\mathbf{K}}(t)-\rho_{ml}^{\mathbf{K}}(t)\mathbf{d}_{ln}^{\mathbf{K}+\mathbf{A}(t)}\right]
$$

其中 $\mathbf{K}$ 为随 $\mathbf{A}(t)$ 运动的移动参考系晶行动量，$\mathbf{d}_{mn}^{\mathbf{k}}=i\langle u_m^{\mathbf{k}}|\nabla_{\mathbf{k}}|u_n^{\mathbf{k}}\rangle$。

**带间/带内电流**：

$$
\mathbf{j}_{\text{ter}}(t) = -\sum_{\mathbf{K}}\sum_{m\neq n}\rho_{nm}^{\mathbf{K}}(t)\,\mathbf{p}_{mn}^{\mathbf{K}+\mathbf{A}(t)}, \qquad
\mathbf{j}_{\text{tra}}(t) = -\sum_{\mathbf{K}}\sum_n\rho_{nn}^{\mathbf{K}}(t)\,\mathbf{p}_{nn}^{\mathbf{K}+\mathbf{A}(t)}
$$

**鞍点方程（半经典近似）**：

$$
\omega_g^{\boldsymbol{\kappa}(t,s)}+\mathbf{F}(s)\cdot\boldsymbol{\mathcal{Q}}^{\boldsymbol{\kappa}(t,s)} = 0, \qquad
\Delta\mathbf{R}^{\mu}\equiv\Delta\mathbf{r}-\boldsymbol{\mathcal{D}}^{\mathbf{k},\mu}+\boldsymbol{\mathcal{Q}}^{\boldsymbol{\kappa}(t,s)} = \mathbf{0}
$$

**规范变换与 Berry 联络**：

$$
|\tilde{u}_n^{\mathbf{k}}\rangle = e^{i\varphi_n^{\mathbf{k}}}|u_n^{\mathbf{k}}\rangle, \qquad \boldsymbol{\mathcal{A}}_n^{\mathbf{k}} = i\langle u_n^{\mathbf{k}}|\nabla_{\mathbf{k}}|u_n^{\mathbf{k}}\rangle
$$

**CDO 奇点与 SDO 修正**：

$$
\frac{1}{T_2^{\text{CDO}}}\propto\frac{1}{|E_m^{\mathbf{k}}-E_n^{\mathbf{k}}|}, \qquad
\frac{1}{T_2^{\text{SDO}}} = \frac{1}{T_2}\, f(\Delta E_{\mathbf{k}}),\quad f\to 0 \text{ 当 } \Delta E_{\mathbf{k}}\to 0
$$

**MoS₂ 单层价带 Berry 曲率（线性展开）**：

$$
\Omega_v^{\text{mono}}(\mathbf

<!-- linsai-wikilinks -->
## 关联概念

- [[2025-2508_07869-semiconductor-bloch-equations-in-wannier-gauge-with-well-beh]]
- [[2508.07869]]
- [[Berry 曲率]]
- [[Berry联络]]
- [[Wannier规范]]
- [[三步模型]]
- [[层间耦合]]
- [[相位匹配]]
- [[隧穿时间]]
- [[非经典光]]
<!-- /linsai-wikilinks -->
