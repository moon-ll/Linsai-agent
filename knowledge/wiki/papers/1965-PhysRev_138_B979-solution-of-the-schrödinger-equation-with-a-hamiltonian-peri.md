---
title: "1965-PhysRev_138_B979-solution-of-the-schrödinger-equation-with-a-hamiltonian-peri"
type: "papers"
created: "2026-09-26T13:39:37Z"
updated: "2026-11-15T15:09:21Z"
tags: []
related: ["Floquet工程", "TDSE", "key-transient-quantum-phase-optical-20260726", "强场电离", "强场超快", "强场超快光学", "瞬态量子相位", "阿秒科学"]
source_raw: "1965-PhysRev.138.B979-solution-of-the-schrödinger-equation-with-a-hamiltonian-peri.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
digest_level: "abstract"
---

• ---
  title: "Shirley 1965：含时周期哈密顿量的薛定谔方程求解（Floquet 形式体系奠基作）"
  type: papers
  created: "2026-09-26T13:39:04Z"
  updated: "2026-09-26T13:39:04Z"
  tags: ["Floquet理论", "含时哈密顿量", "强场物理", "理论基础", "周期驱动系统"]
  related: ["强场HHG理论", "Floquet工程", "含时薛定谔方程", "周期驱动量子系统"]
  source_raw: "1965-PhysRev.138.B979-solution-of-the-schrödinger-equation-with-a-hamiltonian-peri.md"
  growth_stage: "growing"
  confidence: 0.7
  auto_grown: true
  review_status: "pending"
  ---

  # Shirley 1965：含时周期哈密顿量的薛定谔方程求解

  ## 林赛的理解

  这是 Floquet 形式体系的奠基论文，我把它当作强场超快光学的理论起点之一来读。我们做阿秒科学、强场电离和 HHG，系统 Hamiltonian 在强激光场下天然是时间周期的——这意味着薛定谔方程原则上可以借助 Floquet 定理化为准定态问题处理。Shirley 1965 是把这一思路系统化、做成标准方法的那篇文献，被引 3800 余次，说明它不是"一篇老文章"，而是几代强场理论工作的公共语言。

  我需要坦承：手头只有摘要级元数据，正文细节（他具体如何构造 Floquet 哈密顿量、怎么处理规范选择、有没有讨论高频极限）我尚未核实。所以这篇笔记先立框架，精读全文后再回填技术细节。

  ## 核心要点

  - **问题设定**：Hamiltonian 具有时间周期性 H(t+T)=H(t)，求解相应的含时薛定谔方程。
  - **核心思想**：利用 Floquet 定理，将含时问题映射为准定态（quasi-energy）本征值问题——含时系统的"定态"被 Floquet 模式取代，准能量定义在模 ℏω 的 Brillouin 区结构上。
  - **方法地位**：这是处理周期驱动量子系统的标准形式体系，后续 Floquet 工程、强场微扰论、 dressed-state 图像等均建立在其上。
  - **影响力**：被引 3800 余次，是 Floquet 理论方向的基础参考文献。

  ## 实验/研究关联

  - **强场 HHG 与 ATI**：周期激光场中的原子，其 Floquet 态给出光电子谱的通道结构（吸收/放出 n 个光子的边带），是理解强场电离谱型的理论骨架。本论文已被 `key-transient-quantum-phase-optical-20260726` 课题引用，说明它直接支撑我们关于瞬态量子相位与光学读出方向的立项论证。
  - **瞬态量子相位**：我们关注的"泵浦后量子相位演化"若驱动场周期化近似成立，Floquet 准能级劈裂可作为相位读出的参照系。
  - **与 BSI/隧穿图像的关系**：Keldysh 隧穿图像与 Floquet 图像在强场极限下互为补充——前者直观、后者谱学结构清晰。

  ## 批判性思考

  - **摘要在原始材料中为空**：本笔记基于元数据与领域常识写成，凡涉及具体公式推导、适用范围边界（如非微扰场强下 Floquet 展开的收敛性）均未核实，精读全文前不宜作为引证依据。
  - **Floquet 方法的隐含代价**：准能量本征值问题在截断光子数后维度膨胀，强场区数值成本不低；现代 workhorse（直接数值积分 TDSE）在多数实际计算中已替代解析 Floquet 处理，但概念框架仍不可替代。
  - **开放点**：该文是否讨论了与高频展开（后来的 van Vleck / Magnus 高频极限）的衔接？这决定它对我们"多周期脉冲下有效哈密顿量"类课题的直接可用度。

  ## 来源
  - 原始材料：1965-PhysRev.138.B979-solution-of-the-schrödinger-equation-with-a-hamiltonian-peri.md
  - 蒸馏时间：2026-09-26T13:39:04Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：Shirley 1965——含时周期哈密顿量的薛定谔方程求解（Floquet 形式体系奠基作，被引 3800+）

**原理**：Floquet 形式体系的奠基论文：对时间周期性 H(t+T)=H(t) 的哈密顿量，利用 Floquet 定理将含时薛定谔方程映射为准能量（quasi-energy）本征值问题——含时系统的'定态'被 Floquet 模式取代，准能量定义在模 ℏω 的 Brillouin 区结构上；方法地位：处理周期驱动量子系统的标准形式体系，后续 Floquet 工程、强场微扰论、dressed-state 图像均建立在其上——几代强场理论工作的公共语言。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 问题设定 | H(t+T)=H(t) 周期哈密顿量 → Floquet 准能量本征值问题；被引 3800 余次（Phys. Rev. 138, B979, 1965） | 核心要点 |

**适用边界**：摘要在原始材料中为空（本页自注'基于元数据与领域常识，精读全文前不宜作为引证依据'），具体 Floquet 哈密顿量构造、规范选择处理、高频极限讨论未核实；准能量本征值问题截断光子数后维度膨胀、强场区数值成本不低（现代直接 TDSE 数值积分已在多数实际计算中替代解析 Floquet 处理，但概念框架不可替代）；是否讨论了与高频展开（van Vleck/Magnus）的衔接未确认。
**代表作**：J. H. Shirley, Solution of the Schrödinger Equation with a Hamiltonian Periodic in Time（Phys. Rev. 138, B979, 1965，Floquet 形式体系奠基）
*方法卡回补 2026-10-04*

<!-- linsai-wikilinks -->
## 关联概念

- [[Floquet工程]]
- [[TDSE]]
- [[key-transient-quantum-phase-optical-20260726]]
- [[强场电离]]
- [[强场超快]]
- [[强场超快光学]]
- [[瞬态量子相位]]
- [[阿秒科学]]
<!-- /linsai-wikilinks -->
