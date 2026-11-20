---
title: "DFT+U 第一性原理能带计算（含自旋轨道耦合）"
type: "methods"
created: "2026-10-16T16:46:33Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "#type/method"]
related: ["1406.5137", "2512.23904", "arXivID", "arpes", "竞争性反铁磁相：多铁性纤锌矿过渡金属硫族化合物", "自旋劈裂"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-16T16:46:33Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

在DFT框架上对局域d电子引入Hubbard U校正（必要时纳入自旋轨道耦合）进行总能与能带计算，可直接判定磁性基态并给出自旋劈裂能带的第一性原理证据，如有机候选化合物中的补偿亚铁磁基态与巨型自旋劈裂，以及MnX家族中竞争反铁磁相（A型AFM→交替磁）的相边界。

## 参数表

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 计算设置 | VASP PAW；PBE+D3（校验 r2SCAN+rVV10 meta-GGA）；15×15×3 Monkhorst-Pack（含 Γ）；Gaussian smearing 0.05 eV；截断 400 eV；晶格 a = 2.461 Å、c = 10.061 Å（实验值）；层间 vdW 距离 3.354 Å（比石墨 3.473 Å 小 3.5%） | 研究方法·计算设置 
| DSS 曲率定量 | L=18 平板弯曲深度 20 meV；L=60 平板 34 meV（PBE）；r2SCAN+rVV10 L=60 为 36 meV；半无限 (001) 表面 38 meV——与 ARPES 实验 32 meV（Zhang et al., PNAS 121, e2410714121）符合良好 | 主要发现与核心结论 
| IQG 空间分辨 | |Ω|/TrG 呈凸形分布：K̄ 中心 ≈0.96（r2SCAN+rVV10 下 0.958，泛函差异极小、稳健）；DSS 内环严格 = 1；偏离机理：TrG 峰比 |Ω| 峰更宽（外环贡献）、近 K 点 |Ω| 衰减更快；+0.03 Å⁻¹ 朝 M 方向比 −0.03 Å⁻¹ 朝 Γ 方向更接近 1（节线投影为三角非圆）；K′ 谷行为相同但旋转 30° | 主要发现与核心结论 
| 拓扑与表面态 | 无 SOC：K 点附近沿 kz 螺旋手性节线、(001) 投影为环绕 K̄ 三角扭曲节线环；含 SOC 节线带隙仅 0.03 meV；Wilson loop：kz=0.0 与 0.5 平面均非平凡（奇数绕数）→ Z2w3 = 1、Z4 = 0（石墨烯层 QSH 态堆垛）；侧表面 E_F−1.5 eV 两个表面狄拉克点（Γ̄N 与 ȲN，TRS 保护、偶数个确认弱 TI 体边对应） | 主要发现与核心结论 
| DFT 设置 | VASP PAW/PBE；500 eV；12×12×6 Γ 中心；D3-BJ；U=3 eV；力 <10⁻⁴ eV/Å | §研究方法 
| 筛选空间 | T=V/Cr/Mn/Fe/Co/Ni；y=1/4/1/3；M=Nb/Ta；X=Se/S | §研究方法 
| DFT 设置 | ELK LAPW；PBE-GGA；U=4.0/J=0.97 eV（FLL）；26×26×16；a=4.134 Å、c=6.652 Å；±4.447 µB | §电子基态 
| 脉冲参数 | τ_FWHM=40 fs；Γ=100 meV；ρ_E=4 mJ/cm²；RPA 32×32×20/0.003 Ha | §介电函数与脉冲参数 
| 价带偏移 VBO（实验） | 0.83 eV | 主要发现与核心结论 
| 导带偏移 CBO（实验） | 0.76 eV | 主要发现与核心结论 
<!-- src:2026-2607_28491-drumhead-surface-states-of-rhombohedral-graphite-with- -->
<!-- src:2026-2601_02481-an-altermagnetic-materials-library-in-intercalated-tra -->
<!-- src:2026-2505_13415-optical-signatures-of-bulk-g-wave-altermagnetism-in-mn -->
<!-- src:1406.5137 -->

## 适用边界

结果对Hubbard U取值较敏感且依赖磁构型采样的完备性（相边界的确定依赖竞争相总能比较），自旋轨道耦合仅在涉及自旋劈裂判据时开启；成本高于标准GGA计算但低于杂化泛函。

## 代表作

- paper:2024-2404.12345-compensated-ferrimagnets-with-colossal-spin-splitting-in-org
- paper:2025-2512.23904-competing-antiferromagnetic-phases-in-multiferroic-wurtzite

## 证据日志

- 2026-10-16｜r74｜仅简报｜[paper:2024-2404.12345-compensated-ferrimagnets-with-colossal-spin-splitting-in-org] DFT+U 第一性原理能带计算（含自旋轨道耦合）：在候选有机化合物中直接给出补偿亚铁磁基态与巨型自旋劈裂能带的第一性原理证据。
- 2026-10-16｜r74｜仅简报｜[paper:2025-2512.23904-competing-antiferromagnetic-phases-in-multiferroic-wurtzite] DFT+U 第一性原理计算：比较 MnX 家族中竞争反铁磁相的总能与电子结构，定位 Cr 掺杂驱动的 A 型 AFM→交替磁相边界。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[1406.5137]]
- [[2512.23904]]
- [[arXivID]]
- [[arpes]]
- [[竞争性反铁磁相：多铁性纤锌矿过渡金属硫族化合物]]
- [[自旋劈裂]]
<!-- /linsai-wikilinks -->
