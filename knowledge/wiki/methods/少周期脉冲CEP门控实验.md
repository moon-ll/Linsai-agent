---
title: "少周期脉冲CEP门控实验"
type: "methods"
created: "2026-09-05T06:01:33Z"
updated: "2026-11-15T15:09:19Z"
tags: []
related: ["1310.7008", "1910.03236", "2407.05937", "25 W少周期2.2 µm OPCPA驱动的水窗软X射线源（100 kHz）", "2601.09608", "CEP稳定", "CEP门控", "ELI ALPS SYLOS Compact 高强度阿秒光源：紧凑几何下的毫焦级 XUV 阿秒脉冲串", "Generation of attosecond soft X-ray pulses in the water window using few-cycle IR pulses", "circular-dichroism", "三步模型", "固体HHG", "固体高次谐波", "孤立阿秒脉冲", "强场电离", "波形控制", "相位匹配", "相对论等离子体镜面", "相干声子", "谷极化", "载波包络相位", "阿秒脉冲串", "高次谐波产生"]
source_raw: ""
growth_stage: "mature"
confidence: 0.7
source_reliability: "reliable"
sources: ["{"title": "briefing-research_briefing_2026-06-08.md", "source_type": "briefing"}"]
updated_at: "2026-11-08T14:04:25Z"
settled_count: 20
aliases: ["few-cycle CEP gating", "CEP gating", "few-cycle pulse", "少周期", "CEP 门控"]
---

<!-- methods-settle:v1 -->

## 原理

少周期脉冲的电场波形由载波包络相位（CEP）唯一决定，通过CEP锁定与门控可选通特定半周期的强场发射实现孤立阿秒脉冲（IAP）产生：水窗HHG驱动源由BIBO-OPCPA参量放大提供的CEP稳定、1.6 μm、亚2周期mJ级中红外少周期脉冲，其半周期选择性本身即实现幅度门控、无需附加门控光场即可产生孤立阿秒脉冲，并借助U_p∝Iλ²的截止能量标度把HHG截止推入水窗（IAP脉宽一般为数十阿秒量级），该路线拓展至1 μm皮秒泵浦的2.2 μm、100 kHz、25 W、~250 µJ高平均功率OPCPA（压缩至约16.5 fs即约2.3周期，在峰值强度与电离/幅度门控间折中）；非线性自压缩的2.5 fs、CEP稳定近单周期光瞬态凭振幅门控将谐波发射约束于单一半周期，单次发射直接输出50–320 eV孤立超连续谱（IAP最短18 as）；少周期整形驱动场把谐波发射时间窗压缩至单周期内，作为获得孤立阿秒脉冲的时域手段且与拓扑调控兼容——以光谱-空间光学涡旋（SSOV）驱动HHG可产生拓扑荷不随谐波阶数标度（非标度ℓq、各谐波同拓扑荷）的高次谐波涡旋，突破纵向涡旋/STOV驱动下ℓq=qℓ标度对同拓扑荷合成的禁阻，使相位锁定的高次谐波可合成为携带横向轨道角动量（t-OAM）的阿秒时空涡旋（attosecond STOV，先在阿秒脉冲串内产生），再通过对驱动场施加空间啁啾、在横向空间坐标实现灯塔效应，把孤立阿秒STOV从脉冲串中空间隔离——把孤立阿秒门控从时间域（CEP/幅度门控）拓展到空间域，并揭示内禀OAM每光子（而非涡旋拓扑荷）才是一般随谐波阶数标度的物理量；CEP稳定少周期驱动可在过驱动（深电离）强度下运行，经氖/氩介质对比隔离出纯相位匹配门控效应，把门控机制从单原子波形控制扩展到宏观相位匹配层面；6-fs泵浦-探测脉冲对经延迟扫描选通分子增强电离窗口，把少周期门控拓展至核动力学电子谱测量；延时少周期强IR扰动HHG形成的streaking谱可实现全光学表征（重构整形IAP谱相位、反演IR激光CEP与高次谐波相位）；少周期中红外强场的偏振整形（椭圆率/螺旋度连续调控）把驱动场偏振态作为定量控制旋钮（谷极化非共振定量控制、圆偏振泵浦制备空穴环电流初态并以螺旋度控制电流方向），近圆偏振少周期脉冲强场电离借圆偏振消除再散射通道构成attoclock式电离时刻读出；少周期CMDS以脉冲谱形与谱相位的准确测量为分析必要输入；少周期强中红外驱动场凭短时性抑制载流子散射与损伤累积，凸显场驱动（非微扰）带内动力学的固体HHG谱学；高流量XUV阿秒光源对驱动激光提出能量—重频—CEP稳定性组合要求（SYLOS 1 kHz CEP稳定少周期CPA为组合基准）；短于声子周期的少周期近红外泵浦满足冲击极限，可干净启动位移性相干声子并抑制泵浦期间的平均化，把少周期脉冲'以短于内禀时间尺度实现干净选通'的优势从电子强场过程与载流子动力学拓展到载流子-声子耦合的晶格相干动力学控制；最新证据进一步表明，共振色散波发射可借色散波与残余泵浦的光谱分离进行光谱滤取，为短于10 fs的洁净强场脉冲开辟新的少周期驱动源路线，并以可见波段短波长少周期驱动验证HHG极紫外转换效率的显著提升（服务固体HHG谱学），与中红外λ²截止标度水窗路线构成'以截止能量换转换效率'的互补路线。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| HHG截止能量随驱动波长的标度指数 | 2（无量纲，E_cutoff ∝ λ²，U_p ∝ Iλ²） | paper:2024-2407.05937-generation-and-characterization-of-isolated-attosecond-pulse |
| 泵浦-探测脉冲对脉宽 | 6 fs | paper:2026-260527612-electron-spectra-from-strong-field-enhanced-i |
| HHG streaking用IR激光波长 | 800 nm | paper:2023-2309.02647-extension-of-all-optical-reconstruction-method-for-isolated |
| IR激光脉宽（FWHM） | 5 fs | paper:2023-2309.02647-extension-of-all-optical-reconstruction-method-for-isolated |
| IR激光峰值强度 | 2.5×10^14 W/cm² | paper:2023-2309.02647-extension-of-all-optical-reconstruction-method-for-isolated |
| 整形IAP峰值强度 | 2.5×10^11 W/cm² | paper:2023-2309.02647-extension-of-all-optical-reconstruction-method-for-isolated |
| 整形IAP光谱极小中心能量 | 60 eV | paper:2023-2309.02647-extension-of-all-optical-reconstruction-method-for-isolated |
| 光谱极小附近相位跳变 | 约 π rad | paper:2023-2309.02647-extension-of-all-optical-reconstruction-method-for-isolated |
| 自压缩近单周期驱动场脉宽（CEP稳定） | 2.5 fs | paper:2024-2411.12372-self-compressed-waveform-stable-light-transients-enabling-wa |
| 幅度门控孤立超连续谱带宽 | 50–320 eV | paper:2026-2604.24614-bright-isolated-light-pulses-reaching-18-attoseconds-from-hi |
| 幅度门控孤立阿秒脉冲脉宽（最短，据题名） | 18 as | paper:2026-2604.24614-bright-isolated-light-pulses-reaching-18-attoseconds-from-hi |
| BIBO-OPCPA中红外驱动脉冲波长（CEP稳定） | 1.6 μm | paper:2013-1310.7008-generation-of-attosecond-soft-x-ray-pulses-in-the-water-wind |

## 适用边界

CEP门控与延迟/幅度门控仅在少周期脉冲下有效——CEP稳定的亚2周期/2.5 fs近单周期驱动可无附加门控产生孤立阿秒脉冲，但均依赖传播中的波形与CEP逐发稳定；脉宽较长时波形对CEP及延迟不再敏感、幅度门控亦难以限定最强半周期的单次发射；λ²截止标度是三步模型近似下的单原子标度，实际受电离势、电离饱和与宏观相位匹配限制——过驱动（深电离）强度下相位匹配本身成为主导可门控机制且需氖/氩介质对比方能与电离/波形门控分离；水窗驱动存在单发mJ/低重频与高重频/较低单脉冲能量间的能量—重频—稳定性三方权衡（SYLOS 1 kHz为基准）；streaking全光学重构依赖EQRS/SFA模型、已知光谱特征与CEP/延迟稳定；增强电离延迟门控依赖核波包拉伸动力学；attoclock单向读出要求近圆偏振（偏离圆偏时再散射通道复活）；固体HHG要求脉冲短于载流子散射与损伤累积时间尺度；冲击式相干声子激发以泵浦脉宽严格短于声子周期（冲击极限）为前提；SSOV空间门控阿秒STOV目前仅由全量子SFA偶极+麦克斯韦远场传播的数值模拟支持，各类整形/结构化/高功率少周期驱动源成本与复杂度较高；新纳入的色散波光谱滤取净化路线依赖色散波与残余泵浦间的充分光谱分离，所得<10 fs洁净脉冲仍长于2.5 fs近单周期极限，且可见波段短波长驱动以λ²标度下截止能量的降低换取极紫外转换效率的显著提升，须按目标波段与通量需求在效率路线与中红外水窗路线间取舍。

## 代表作

- paper:2024-2407.05937-generation-and-characterization-of-isolated-attosecond-pulse
- paper:2026-260527612-electron-spectra-from-strong-field-enhanced-i
- paper:2023-2309.02647-extension-of-all-optical-reconstruction-method-for-isolated
- paper:2022-2209.04928-polarization-shaped-strong-field-control-over-valley-polariz
- paper:2024-2411.12372-self-compressed-waveform-stable-light-transients-enabling-wa
- paper:2013-1310.7008-generation-of-attosecond-soft-x-ray-pulses-in-the-water-wind
- paper:2020-1910.03236-water-window-soft-x-ray-source-enabled-by-a-25-w-few-cycle-2
- paper:2015-1506.06567-extreme-ultraviolet-high-harmonic-spectroscopy-of-solids

## 证据日志

- 2026-09-18｜r18｜仅简报｜[paper:2024-2407.05937-generation-and-characterization-of-isolated-attosecond-pulse] 中红外少周期驱动高次谐波：利用截止能量随驱动波长平方上移，把相干辐射推至碳K边以上的水窗波段。
- 2026-09-19｜r25｜仅简报｜[paper:2026-260527612-electron-spectra-from-strong-field-enhanced-i] 少周期泵浦-探测脉冲对（6-fs pulse pairs）：通过延迟扫描控制电离发生时的核拉伸几何，把增强电离窗口在时间上选通并与其他电离通道区分开。
- 2026-09-26｜r41｜回原文｜[paper:2024-2407.05937-generation-and-characterization-of-isolated-attosecond-pulse] 中红外少周期驱动高次谐波（HHG）：利用 U_p∝Iλ² 的截止标度把连续谱推到碳K边以上，给出水窗下边界阿秒源的可行参数窗口。
- 2026-09-26｜r41｜回原文｜[paper:2023-2309.02647-extension-of-all-optical-reconstruction-method-for-isolated] 孤立阿秒脉冲产生（少周期驱动+门控方案）：提供待表征的超连续谱/孤立阿秒脉冲源，是方法验证的对象。
- 2026-09-27｜r42｜回原文｜[paper:2022-2209.04928-polarization-shaped-strong-field-control-over-valley-polariz] 少周期中红外强场偏振整形（椭圆率/螺旋度连续调控）：把驱动场偏振态本身作为谷极化的定量控制旋钮，区别于依赖共振圆偏振激发的传统方案。
- 2026-10-02｜r46｜仅简报｜[paper:2024-2411.12372-self-compressed-waveform-stable-light-transients-enabling-wa] 自压缩少周期光瞬态产生（非线性自压缩/波形稳定技术）：在传播中自压缩出 2.5 fs 且 CEP 稳定的近单周期驱动场，为水窗 HHG 提供高峰值强度、逐发可重复的光源。
- 2026-10-02｜r46｜仅简报｜[paper:2024-2411.12372-self-compressed-waveform-stable-light-transients-enabling-wa] 少周期振幅门控孤立阿秒脉冲产生：近单周期驱动场将高次谐波发射约束于单一半周期，无需额外门控即可获得孤立阿秒爆发。
- 2026-10-02｜r47｜仅简报｜[paper:2013-1310.7008-generation-of-attosecond-soft-x-ray-pulses-in-the-water-wind] BIBO-OPCPA中红外少周期驱动源：以BIBO晶体参量放大获得1.6 μm、亚2周期、CEP锁定的mJ级脉冲，是驱动水窗HHG的前提技术。
- 2026-10-03｜r50｜仅简报｜[paper:2026-2609.36621-attosecond-circular-dichroism-spectroscopy-of-hole] 圆偏振少周期脉冲强场电离：作为泵浦在原子中制备磁子能级相干叠加型空穴环形电流，光场螺旋度直接控制电流方向。
- 2026-10-03｜r55｜仅简报｜[paper:2026-2609.27027-coherent-multidimensional-spectroscopy-at-the-few-] 少周期脉冲谱形与谱相位表征：脉冲谱（含相位）的准确测量成为该分析流程的必要输入条件。
- 2026-10-10｜r68｜仅简报｜[paper:2020-1910.03236-water-window-soft-x-ray-source-enabled-by-a-25-w-few-cycle-2] 中红外少周期OPCPA（2.2 µm、100 kHz、25 W、~250 µJ）：以1 µm皮秒泵浦的参量放大架构，把少周期中红外驱动器的平均功率与重频推到当时最高水平，是水窗HHG通量提升的核心使能技术。
- 2026-10-10｜r68｜仅简报｜[paper:2020-1910.03236-water-window-soft-x-ray-source-enabled-by-a-25-w-few-cycle-2] 少周期中红外脉冲压缩：将2.2 µm脉冲压缩至约16.5 fs（~2.3个周期），兼顾峰值强度与电离/幅度门控，有利于产生宽带连续水窗谱。
- 2026-10-11｜r69｜仅简报｜[paper:2026-2601.09608-a-high-intensity-attosecond-light-source-in-compact-geometry] 高能量CEP稳定少周期CPA驱动激光（SYLOS, 1 kHz）：提供驱动能量—重频—CEE稳定性的组合基准，说明高流量XUV对驱动源的具体要求。
- 2026-10-11｜r72｜仅简报｜[paper:2026-2410.xxxxx-bright-isolated-light-pulses-reaching-18-attoseconds-from-hi] 少周期幅度门控HHG：仅在最强半周期内单次发射，直接产生50–320 eV孤立超连续谱，避免了附加门控技术的通量损耗。
- 2026-10-11｜r73｜仅简报｜[paper:2015-1506.06567-extreme-ultraviolet-high-harmonic-spectroscopy-of-solids] 少周期 MIR 驱动场：以少周期强中红外脉冲驱动，抑制载流子散射与损伤累积，凸显场驱动（非微扰）带内动力学。
- 2026-10-17｜r78｜仅简报｜[paper:2026-2604.24614-bright-isolated-light-pulses-reaching-18-attoseconds-from-hi] 少周期幅度门控产生孤立阿秒脉冲：依赖少周期+CEP稳定使仅最强半周期辐射，无需复杂门控即得孤立脉冲。
- 2026-10-17｜r78｜仅简报｜[paper:2019-1912.07918-phase-matching-mechanism-for-high-harmonic-generation-in-the] 少周期CEP稳定驱动HHG（过驱动强度）：以深电离强度下运行的CEP稳定少周期脉冲在氖/氩间对比，隔离出纯相位匹配门控效应。
- 2026-10-31｜r105｜仅简报｜[paper:2008-0808.04690-attosecond-angular-streaking-eckle-et-al] 近圆偏振少周期脉冲强场电离：圆偏振消除再散射通道，使末态动量方向单向反映电离瞬间的矢势方向。
- 2026-10-31｜r107｜仅简报｜[paper:2013-1310.7008-generation-of-attosecond-soft-x-ray-pulses-in-the-water-wind] BIBO-OPCPA少周期中红外光源：提供CEP稳定的1.6 μm亚2周期驱动场，是把HHG截止推入水窗的直接前提。
- 2026-10-31｜r107｜仅简报｜[paper:2013-1310.7008-generation-of-attosecond-soft-x-ray-pulses-in-the-water-wind] 少周期幅度门控：利用亚2周期脉冲的半周期选择性实现无附加门控光场的孤立阿秒脉冲产生。
- 2026-11-01｜r110｜仅简报｜[paper:2026-2609.36621-attosecond-circular-dichroism-spectroscopy-of-hole] 圆偏振少周期脉冲强场电离：利用角向选择性电离制备磁子能级相干叠加，即环电流初态，把光子自旋转化为离子的轨道角动量/磁矩。
- 2026-11-06｜r114｜仅简报｜[paper:2026-2604.00622-generating-intense-attosecond-pulses-and-vectorizing-polariz] 少周期整形驱动场：将谐波发射时间窗压缩至单周期内，是获得孤立阿秒脉冲的时域手段，可与拓扑调控兼容。
- 2026-11-06｜r115｜回原文｜[paper:2025-2506.07465-isolated-attosecond-spatio-temporal-optical-vortices-interpl] 孤立阿秒脉冲门控（少周期/时间门控）：确保输出为单个携带时空涡旋结构的阿秒脉冲而非阿秒脉冲串。
- 2026-11-07｜r120｜仅简报｜[paper:2024-2411.09035-coherently-coupled-carrier-and-phonon-dynamics-in-elemental] 少周期近红外泵浦激发：泵浦短于声子周期，满足冲击极限，干净启动位移性相干声子并抑制泵浦期间的平均化。
- 2026-11-08｜r127｜仅简报｜[paper:2026-2610.15108-resonant-dispersive-wave-emission-a-route-toward-few-cycle-t] 色散波光谱滤取与少周期脉冲净化：利用色散波与残余泵浦的光谱分离获得小于 10 fs 的洁净强场脉冲。
- 2026-11-08｜r127｜仅简报｜[paper:2026-2610.15108-resonant-dispersive-wave-emission-a-route-toward-few-cycle-t] 可见波段少周期脉冲驱动的高次谐波产生：以短波长、少周期驱动验证 HHG 极紫外转换效率的显著提升，服务固体 HHG 谱学。

<!-- /methods-settle:v1 -->

使用sub-1.5-cycle、CEP门控激光脉冲在kHz重频下驱动相对论等离子体镜面，实现XUV连续谱产生与电子束attosecond控制；CEP稳定性约380 mrad rms、可持续约1小时。

<!-- linsai-wikilinks -->
## 关联概念

- [[1310.7008]]
- [[1910.03236]]
- [[2407.05937]]
- [[25 W少周期2.2 µm OPCPA驱动的水窗软X射线源（100 kHz）]]
- [[2601.09608]]
- [[CEP稳定]]
- [[CEP门控]]
- [[ELI ALPS SYLOS Compact 高强度阿秒光源：紧凑几何下的毫焦级 XUV 阿秒脉冲串]]
- [[Generation of attosecond soft X-ray pulses in the water window using few-cycle IR pulses]]
- [[circular-dichroism]]
- [[三步模型]]
- [[固体HHG]]
- [[固体高次谐波]]
- [[孤立阿秒脉冲]]
- [[强场电离]]
- [[波形控制]]
- [[相位匹配]]
- [[相对论等离子体镜面]]
- [[相干声子]]
- [[谷极化]]
- [[载波包络相位]]
- [[阿秒脉冲串]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
