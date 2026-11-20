---
title: "Wannier-Bloch 轨迹方法"
type: "methods"
created: "2026-10-31T11:38:00Z"
updated: "2026-11-15T15:09:19Z"
tags: []
related: ["Berry 曲率", "TDSE", "sbe-bloch-equations", "反常速度", "固体HHG", "固体HHG数值计算方法体系", "带内_带间电流分解"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
source_reliability: "reliable"
sources: ["{"title": "general-mos2-20260905", "source_type": "archived_proposal"}"]
- title: "general-mos2-20260905"
source_type: "archived_proposal"
---

> ⚠ **状态标注（2026-11-01 颗粒度体检）**：本页正文素材不足以支撑「参数表≥5行」的达标线（指导学生复现），如实保持低密度工作页状态，待深读素材回补后升级。已在专题关联网络中。
在电子轨迹中显式引入 Berry 连接和具有动量依赖的跃迁矩阵元，将倒空间几何对选择定则的约束映射到谐波阶次及倒空间轨迹长度，适用于 5—15 阶的逐阶分析。

## 参数表

**终极升级**（2026-11-01，canonical 要素，引用已核实/库内锚）：
Wannier–Bloch 轨迹方法：在倾斜/强场晶格中以 Wannier–Bloch 态（位置依赖布洛赫能量的局域基）传播波包，轨迹由局域加速度定理 k(t)=k₀+A(t) 与带内/带间通道分解给出——是速度规范 SBE 的轨迹化表述，天然分离带内电流与带间极化通道。

| 轨迹方程 | $\hbar\dot{k} = -eE(t)$；$\dot{r} = ∂ε(k)/\hbar∂k - \dot{k}×Ω(k)$ | Xiao RMP 2010 https://doi.org/10.1103/RevModPhys.82.1959 |
| 基组 | Wannier–Bloch 态（$H_W = H_0 - F·\hat{z}$，位置偏置） | [[sbe-bloch-equations]] |
| 通道分离 | 带内电流 $J_{intra} = -eΣ_k \dot{r} ρ_{nn}$ vs 带间 $J_{inter} ∝ π_{cv}$ | [[带内_带间电流分解]] |

✅ 通道归因、Berry 曲率反常速度的解析定位（[[固体HHG数值计算方法体系]] 轨迹视图）。
❌ 强场带间强耦合需全 TDSE；Wannier 基截断误差须收敛检查。

- D. Xiao, M.-C. Chang, Q. Niu, Rev. Mod. Phys. 82, 1959 (2010). https://doi.org/10.1103/RevModPhys.82.1959

## 代表作

- D. Xiao, M.-C. Chang, Q. Niu, Rev. Mod. Phys. 82, 1959 (2010). https://doi.org/10.1103/RevModPhys.82.1959

## 适用边界

✅ 通道归因、Berry 曲率反常速度的解析定位（[[固体HHG数值计算方法体系]] 轨迹视图）。
❌ 强场带间强耦合需全 TDSE；Wannier 基截断误差须收敛检查。



---

第三条路线：在轨迹中分别引入 Berry 连接与跃迁矩阵元的动量依赖，给出能带结构对谐波发射的调制机制；倒空间几何对选择定则的约束直接对应到谐波阶次与倒空间轨迹长度，适合 5—15 阶逐阶分析。

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry 曲率]]
- [[TDSE]]
- [[sbe-bloch-equations]]
- [[反常速度]]
- [[固体HHG]]
- [[固体HHG数值计算方法体系]]
- [[带内_带间电流分解]]
<!-- /linsai-wikilinks -->
