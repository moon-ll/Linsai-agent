---
title: "自旋极化DFT（PBE）电子结构计算"
type: "methods"
created: "2026-10-03T06:43:52Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "#type/method"]
related: ["2112.12712", "CrPX3单层水吸附的DFT研究（CrPS3与CrPSe3本征及缺陷体系）", "DFT计算", "arXivID", "arpes"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-03T06:43:52Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

基于PBE泛函的（自旋极化）DFT计算可直接给出二维材料电子结构基准：对磁性半导体CrPS3/CrPSe3单层提供PBE带隙标尺用于MPX3家族横向比较，对TMDC异质结（如MoSe2/WS2，II型对齐）提供基态几何、层间结合与初始带对齐基线。

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
| 平面波动能截断 | 600 eV | DFT 计算细节（方法部分） 
| VS₂ 的 U 参数 | U=3.0 eV | GGA+U_eff 处理局域 d 轨道 
<!-- src:2026-2607_28491-drumhead-surface-states-of-rhombohedral-graphite-with- -->
<!-- src:2026-2601_02481-an-altermagnetic-materials-library-in-intercalated-tra -->
<!-- src:2026-2505_13415-optical-signatures-of-bulk-g-wave-altermagnetism-in-mn -->
<!-- src:2024-2411_17493-ubiquitous-van-der-waals-altermagnetism-with-slidingmo -->

## 适用边界

PBE为半局域GGA泛函，系统性低估带隙且本身不含层间范德华色散（层间结合与带隙绝对值不可定量外推），所得数值宜作同泛函体系内部横向标尺；对Cr系磁性体系须开启自旋极化方得正确基态。

## 代表作

- arXiv:2112.12712
- arXiv:2501.08138

## 证据日志

- 2026-10-03｜r50｜仅简报｜[paper:2021-2112.12712-adsorption-of-water-on-the-pristine-and-defective-semiconduc] 自旋极化DFT（PBE）电子结构计算：给出CrPS3/CrPSe3单层PBE带隙基准，可直接作为MPX3家族带隙横向比较的标尺。
- 2026-10-03｜r50｜仅简报｜[paper:2025-2501.08138-two-dimensional-transition-metal-dichalcogenides-based-bilay] DFT（PBE）：给出异质结基态几何、层间结合与初始带对齐基线（MoSe2/WS2 为 II 型）。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2112.12712]]
- [[CrPX3单层水吸附的DFT研究（CrPS3与CrPSe3本征及缺陷体系）]]
- [[DFT计算]]
- [[arXivID]]
- [[arpes]]
<!-- /linsai-wikilinks -->
