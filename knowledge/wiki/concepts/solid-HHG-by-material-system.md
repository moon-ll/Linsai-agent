---
title: "固体高次谐波产生"
type: "concepts"
created: "2026-08-15T14:15:08Z"
updated: "2026-08-15T14:15:08Z"
tags: ["solid-HHG", "强场物理", "凝聚态非线性光学", "带内电流", "带间极化", "TDDFT", "半导体布洛赫方程"]
related: ["Berry曲率与谷极化", "Houston基底SBE", "实时TDDFT", "椭圆度分辨光谱", "气相HHG三步模型", "阿秒偶极相位测量"]
source_raw: "solid-HHG-by-material-system.md"
growth_stage: "growing"
confidence: 0.7
auto_grown: true
review_status: "pending"
---

# 固体高次谐波产生

## 林赛的理解

我做了多年气相 HHG，第一次认真读固体 HHG 文献时最大的观念冲击是：**气相里那个“电子离化—加速—回碰”的三步模型，在晶体里要搬到 k 空间重新讲一遍，而且只讲一半**。固体中真正主导的往往是带内电流——电子根本不需要离开价带，只要在被强场驱动的布洛赫振荡中扫过非抛物线色散区，速度本身就是非正弦的，谐波就出来了。带间那部分则不是真实空间的“回碰复合”，而是价带—导带布居的相干振荡与 k 空间布洛赫波包的演化。所以每次审固体 HHG 的稿子，我第一个问题永远是：**你怎么区分带内和带间的贡献？** Si 那篇偏振分辨工作（`1805.10453`）说服我的原因，就是它用最便宜的实验手段——椭圆度扫描——把 HH5（纯带内）、HH7（带内带间耦合）、HH9（主要带内）干净地分开了。椭圆度分辨就是我眼中的“机制光谱仪”。

第二个让我兴奋的点是：**材料是可以设计的**。气相 HHG 里介质就是原子给的；固体里，堆垛方式（h-BN 的 AA' 决定反演对称性、石墨烯 AA vs AB 改变整支谱）、层数、Berry 曲率、谷自由度、甚至拓扑相变和超导转变，全都是旋钮。这意味着 HHG 不只是个光源问题，而是**全光学的能带结构探针**。

实验上我也吃过亏：透射几何里相位失配和传播效应会毁掉物理解释，所以 GaAs 那篇用反射几何（`2004.04492`）的选择我特别有共鸣。理论工具箱上我的经验是：TDDFT（Octopus 这类实时实空间方法）是定量金标准，但 SBE + 紧束缚模型才是快速建立物理直觉的工具——改一个层间跳跃参数 $t_\perp$ 立刻看到谱怎么变，这种透明性对设计实验无可替代。

## 核心要点

### 定义
固体 HHG 指强激光场（典型 $10^{-2}$–$10^{-1}$ V/Å，强度 0.1–10 TW/cm² 量级）作用于凝聚态晶体时，通过**带内电流**与**带间极化**两类非线性机制，产生驱动频率整数倍相干辐射的过程。与气相 HHG 的本质区别：介质是具有平移对称性与能带结构的周期体系，谐波响应直接编码晶格对称性、色散形状、层间耦合与拓扑性质。

### 物理直觉
1. **双通道机制**：
   - *带内*：电子在能带内沿 k 空间被场驱动（$\hbar\dot{k} = -eF(t)$），非抛物线色散 $\varepsilon_n(k)$ 使速度 $v_n(k)$ 非正弦 → 非线性电流。零带隙体系（单层石墨烯）中主导。
   - *带间*：场致 Zener 隧穿/激发建立价带—导带相干布居，布居振荡频率 $\sim \varepsilon_g(k)/\hbar$ 随 k 演化 → 谐波辐射，类比（但不等于）气相三步模型的“复合”步骤。
2. **对称性即选择定则**：中心反演对称晶体禁戒偶次谐波；奇数层 h-BN 打破反演对称 → 偶次谐波出现。点群决定圆驱动下谐波螺旋度的交替模式（Si 的 $O_h$ vs α-石英的 $D_3$）。
3. **材料自由度即旋钮**：层数与堆垛（h-BN 1–6 层收敛到体材料极限、石墨烯 AB vs AA）、Berry 曲率与谷（MoS₂ 双层 Berry 曲率依赖层间跳跃强度）、有效质量反差（α-石英：重价带 5–10 $m_e$ vs 轻导带 0.3 $m_e$，利于机制归因）。
4. **扰动/非扰动边界**：低场区谐波强度遵循 $I_n \propto E^{2n}$ 标度律；超过材料依赖阈值场强（GaAs 约 4–6 MV/cm）后出现偏离标度律的振荡行为，源于场致动态能带修改与 Floquet 图像中的动态局域化。

### 数学表达

**谱的提取（TDDFT 路线，`1807.02961` / `1607.00747`）**：

$$
\mathrm{HHG}(\omega) = \left|\mathcal{F}\!\left[\frac{\partial}{\partial t}\int_\Omega d^3\mathbf{r}\,\mathbf{j}(\mathbf{r},t)\right]\right|^2,
\qquad
I(\omega) = \left|\int_0^{T_e} J(t)\,e^{-i\omega t}dt\right|^2
$$

**电流的带内/带间分解（概念形式）**：

$$
j(t) = \underbrace{e\sum_{n,\mathbf{k}} \rho^{\mathbf{k}}_{nn}\, v_n\!\big(\mathbf{k}+\mathbf{A}(t)\big)}_{j_{\rm intra}}
\;+\;
\underbrace{\frac{d}{dt}\sum_{m\neq n,\mathbf{k}} \mathbf{d}_{mn}\,\rho^{\mathbf{k}}_{nm}}_{j_{\rm inter}}
$$

**Houston 基底半导体布洛赫方程（SBE，`2011.12252`）**：

$$
i\frac{d}{dt}\rho^{\mathbf{k}}_{mn} = \mathcal{E}^{\mathbf{k}+\mathbf{A}(t)}_{mn}\rho^{\mathbf{k}}_{mn} + i\frac{\tilde{\delta}_{mn}}{T_2}\rho^{\mathbf{k}}_{mn} - \mathbf{F}(t)\cdot\sum_l\!\left(\mathbf{d}^{\mathbf{k}+\mathbf{A}(t)}_{ml}\rho^{\mathbf{k}}_{ln} - \mathbf{d}^{\mathbf{k}+\mathbf{A}(t)}_{ln}\rho^{\mathbf{k}}_{ml}\right)
$$

**紧束缚输入（石墨烯）**：单层 $\hat{H}_0 = -t_0 f(\mathbf{k})\hat{a}^\dagger_\mathbf{k}\hat{b}_\mathbf{k} + \text{h.c.}$（$t_0 = 2.7$ eV）；AB 双层加层间跳跃 $t_\perp = 0.48$ eV，K 点附近色散由线性变二次型。

**谐波椭圆率（实验机制判据，`1805.10453`）**：

$$
|\epsilon_{\rm HH}| = \sqrt{I_{\min}/I_{\max}}
$$

### 体系全景（截至 2026 年）
宽禁带介电体（h-BN、α-石英、MgO）→ 传统半导体（Si、GaAs）→ 2D 材料（石墨烯、TMD）→ 拓扑材料（Haldane 模型、Na₃Bi、TaAs）→ 扭转/双层体系（莫尔超晶格）→ 磁性/SOC 材料（Rashba）→ 关联电子体系（Ca₂RuO₄ 莫特绝缘体、TiSe₂ CDW）→ 高温超导体（YBCO，奇金属→赝能隙→超导）→ 手性/圆极化 HHG。

## 实验/研究关联

| 实验/工作 | 关键参数 | 对本概念的支撑 |
|---|---|---|
| **Si 偏振分辨 HHG**（`1805.10453`） | 2 μm (100) Si，2.1 μm 驱动，0.6–0.7 TW/cm²，Octopus + mBJ 对比 | 椭圆度分辨分离机制：HH5 纯带内（<3.1 eV 直接带隙）、HH7 耦合（JDOS 峰）、HH9 带内主导；椭圆驱动 ε

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry曲率与谷极化]]
- [[Houston基底SBE]]
- [[实时TDDFT]]
- [[椭圆度分辨光谱]]
- [[气相HHG三步模型]]
- [[阿秒偶极相位测量]]
<!-- /linsai-wikilinks -->
