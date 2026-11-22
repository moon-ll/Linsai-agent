---
title: "2023-2306_16212-compact-realization-of-all-attosecond-pump-probe-spectroscop"
type: "papers"
created: "2026-08-29T16:54:06Z"
updated: "2026-11-16T05:30:14Z"
tags: []
related: ["VMI", "pump-probe", "quantum metric", "啁啾脉冲放大", "强场驱动", "泵浦探测", "量子几何"]
source_raw: "2023-2306.16212-compact-realization-of-all-attosecond-pump-probe-spectroscop.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
---

# Compact realization of all-attosecond pump-probe spectroscopy

## 林赛的理解

这篇工作解决了 attosecond pump-probe spectroscopy (APAPS) 从"概念验证"走向"普及应用"的关键瓶颈。传统 APAPS 受制于低重复率 (10–120 Hz) 和庞大光路结构，仅能实现 10–100% 的信号变化，信噪比极差。本工作首次在 1 kHz 商业激光器上实现 APAPS，利用离轴 HHG 几何 + 电离诱导自相位调制 blueshift，在紧凑光路中产生 10 nJ 级 XUV 脉冲，最终测得 ~1 Ar²⁺ ion/shot，shot noise ~1–2%。这意味着 APAPS 从此可以在普通实验室开展。对我们的研究而言：强场驱动下的多电子动力学（interatomic Coulombic decay、auger decay）若能用双 XUV 脉冲泵浦探测，就能以真正 attosecond 时间分辨率区分电子相关作用 vs 核运动——这是目前 HHG+NIR 方案无法提供的。

## 研究问题（Research Question）
如何将 attosecond pump-attosecond probe spectroscopy (APAPS) 从低重复率 (10–120 Hz)、大型专用装置的"概念验证"阶段推向高重复率 (1 kHz+)、紧凑化、商业激光驱动的"普及应用"阶段？具体目标：（1）利用商用 1 kHz Ti:sapphire 激光系统替代专用低重复率光源；（2）通过 hollow-core fiber 后压缩和紧凑 HHG 几何获得 isolated attosecond pulses；（3）实现双光子能量的 XUV pump–XUV probe 双色方案，使 pump 和 probe 可明确区分。

## 研究背景（Background）
### 学术脉络

Attosecond science 自 2000 年代初发展以来，HHG 产生的 XUV 脉冲一直是主流光源。但 HHG 产生的 XUV 脉冲能量极低（typically fJ–nJ），导致绝大多数实验只能以 XUV 作为 pump、NIR 作为 probe，构成 attosecond streaking 和 attosecond transient absorption spectroscopy 两大主流技术。

### NIR 作为 probe 的三重局限

1. **时间分辨率受限**：XUV-NIR 交叉相关至少数 fs，不在 attosecond 域。NIR 光学周期作为"时钟"虽可实现亚周期分辨率，但无法分辨从 attosecond 到 few-fs 跨度的动力学过程。
2. **多光子与场驱动干扰**：由于 XUV 光子通量低，NIR probe 强度常需达到能诱发多光子过程和场驱动样品修改的程度，可能掩盖或改变感兴趣的动力学。
3. **局域性差**：NIR 主要与价层电子相互作用，不适合研究核心/内价层电子的局域化动力学。

### 前期 APAPS 工作

| 研究组 | 年份 | 关键技术 | 局限 |
|--------|------|----------|------|
| Tzallas et al. | 2011 | 双 Mach-Zehnder 偏振门 | 低重复率 |
| Takahashi et al. | 2013 | 800+1300 nm 双色驱动，auto-correlation | 低重复率 |
| Midorikawa group | 2015–2016 | 强 attosecond pulse trains | 低重复率 |
| Kretschmar et al. | 2022 | 光学参量啁啾脉冲放大驱动 | 低重复率 |
| LCLS | 2020–2022 | X-ray free-electron laser | 大型装置 |

所有前期工作的共同瓶颈：setup 庞大、低重复率 (10–120 Hz)、信噪比受限（需 10–100% 信号变化，而 XUV-NIR 实验可达 10⁻⁴）。

## 研究方法（Methods）
### 激光系统与脉冲压缩

- **激光器**： commercial Ti:sapphire laser system (Spitfire Ace, Spectra Physics)，1 kHz，central wavelength 800 nm，initial pulse duration 36 fs
- **后压缩**：取 3 mJ 脉冲注入 differentially pumped hollow-core fiber（长度 1 m，core diameter 400 µm），充 He 3.5 bar，经 6 片 chirped mirrors (PC70, Ultrafast Innovations) 和 two wedges 压缩至 **3.8 fs**，pulse energy 降至 1 mJ

### 紧凑 HHG 装置

- **驱动激光聚焦**：spherical mirror (f = 75 cm)，在气体喷嘴位置 peak intensity = **5×10¹⁵ W/cm²**
- **气体喷嘴 placement**：距 driving laser focus **~3.5 cm upstream**（即在驱动激光束腰前方 several Rayleigh lengths），而非传统的位置在焦点处
  - 此离焦几何（out-of-focus geometry）产生相对高的 XUV pulse energy (10 nJ) 和小的 virtual source size
  - 在气体喷嘴位置的 NIR peak intensity 估计为 **1×10¹⁵ W/cm²**
- **气体**：Kr（双色 APAPS）和 Xe（单色 APAPS），backing pressure **4 bar**
- **Al filter**：100 nm 厚，阻挡剩余 NIR

### 过驱动 HHG 与 Blueshift

- 在 overdriven regime 下，HHG 介质（Kr）中发生 ionization-induced self-phase modulation (SPM)，使驱动激光频率瞬态上移（blueshift）
- 由于 HHG efficiency ∝ λ⁻⁶·⁵ (Kr)，blueshift 实际上有利于 HHG 转换效率
- 实验测得：HHG jet on 相比 off，驱动激光光谱显著 blueshifted

### 双色 XUV Pump-Probe 方案

- **球面多层镜**（f = 5 cm）分光 + 聚焦：
  - **Mirror A**：高反射率 < 25 eV（用于 pump，centered ~20 eV）
  - **Mirror B**：反射峰在 33.5 eV（用于 probe）
- 两束 XUV 在垂直方向分开，再经 delay stage 和 closed-loop mirror mount 重叠
- XUV beam waist radius：horizontal ~1.2 µm，vertical ~2.4 µm（紧聚焦）

### 离子检测

- **Velocity-map imaging spectrometer (VMIS)**，spatial imaging mode 运行
- Atomic density in interaction region：~**10¹³ cm⁻³**
- 检测：microchannel plate / phosphor screen + CCD camera

## 主要发现与核心结论

### 信号估算

双光子电离事件数（collinear beams）：

$$N_{event} = c \times 2\pi n_0 N_{pump}\sigma_{pump} N_{probe}\sigma_{probe} / \lambda_{pump}$$

其中 c = 1（λpump ≫ λprobe）或 c = 0.5（λpump = λprobe），实验条件 0.5 < c < 1。

**参数取值**：
- n₀ = **10¹³ cm⁻³**
- Npump = **3.75×10⁷** photons
- Nprobe = **2.8×10⁷** photons
- σpump(Ar at 20 eV) = **32.5 Mb**
- σprobe(Ar⁺ at 33.5 eV) = **10 Mb**

理论预测：collinear 条件下产生 **2–3 Ar²⁺ ions/shot**；非共线配置下约低 3 倍。

### 双色 APAPS 实验（Ar 双电离）

- Pump (20 eV) → Ar → Ar⁺；Probe (33.5 eV) → Ar⁺ → Ar²⁺
- 实测产生约 **1 Ar²⁺ ion/laser shot**，与理论预测一致
- Shot noise error：~**1%**（每个 delay point 累积 ~8000 Ar²⁺ ions over 4000 shots×2 scans）

**关键时间参数**：
- 单个 attosecond burst 宽度：**240 as**
- Pre-/post-pulse 相对强度：**(16 ± 2)%**
- Ar²⁺ 产量从 20% 增至 80% 的 risetime：**630 as**

### XUV 自相关测量

- 两相同 mirror A 脉冲自相关，过程：two-photon double ionization of Ar (直接双电子发射)
- 测得零延迟处 dominant peak，±0.8 fs 处有 satellite peaks（对应 pre-/post-pulses）
- Shot noise error：~**2%**（~0.5 Ar²⁺ ions/shot）
- Satellite peaks 间距显著短于 half driving laser oscillation period (~1.3 fs)，表明 driving laser 在 HHG 介质中已 blueshifted

### Blueshift 确认

- Fig. 5：HHG jet off 时驱动光谱 centered ~800 nm；HHG jet on 时 substantial blueshift
- 主因：ionization-induced SPM
- 由于 HHG efficiency ∝ λ⁻⁶·⁵ (Kr)，blueshift 实际上提升了 HHG 转换效率

### XUV 脉冲能量与强度

| 参数 | Mirror A (pump) | Mirror B (probe) |
|------|-----------------|-----------------|
| XUV pulse energy at source | 10 nJ | 10 nJ |
| 实际到达相互作用的 pulse energy | **0.12 nJ** | **0.15 nJ** |
| XUV peak intensity | **8×10¹² W/cm²** | **1×10¹³ W/cm²** |

## 潜在研究方向（Future Directions）
### 现存局限

1. **Shot noise 限制**：当前实验质量受限于 shot noise（1–2%），虽远优于前期 APAPS 的 10–100% signal change 要求，但进一步提升精度需要：
   - 更高 HHG conversion efficiency（理论预测均匀气体密度分布优于当前近似抛物线分布）
   - 更高重复率（100 kHz–1 MHz 激光系统已存在）
   - 更高目标密度（光子检测方案如 transient absorption 可比离子检测高数个量级）

2. **Pre-/post-pulses**：当前 satellite pulses 相对强度 **(16 ± 2)%**，CEP 依赖性强。CEP stabilization + single-shot CEP tagging 可实现数据按 CEP intervals 分类，有望获得更 isolated pulses。

3. **信噪比差距**：XUV-NIR transient absorption 已实现 10⁻⁴ 级 pump-probe signal changes，当前 APAPS 尚未达到此灵敏度。

### 开放问题

1. **固体样品 APAPS**：当前 setup 在少数几发内防止样品损伤 + 高灵敏度探测小 transient signal changes 的组合使其有望应用于固体（如 transition metal dichalcogenides、莫尔 systems）
2. **内壳层 decay 过程中的多电子关联**：inner-shell hole decay、interatomic/intermolecular Coulombic decay
3. **Attosecond 域量子纠缠**：attosecond 时间尺度的量子纠缠测量
4. **电子相干性与退相干时间测量**：electronic coherences and dephasing times，用于理解生物相关系统中的 charge migration
5. **Attosecond pump-probe coincidence spectroscopy**：高重复率下可能实现

## 与林赛研究的关联

- **HHG**：本工作展示的 compact HHG geometry（out-of-focus gas jet placement + ionization-induced blueshift）可用于我们产生更强 XUV 脉冲的 HHG 优化，特别是针对 Kr 介质 λ⁻⁶·⁵ 缩放关系意味着 blueshift 的 driving laser 可提升效率
- **阿秒**：首次在 1 kHz 商业激光上实现真正的 XUV-XUV pump-probe，attosecond 时间分辨率（240 as pulses，630 as risetime）直接服务于电子动力学 sub-cycle 研究
- **强场驱动**：overdriven HHG regime 的 physics（ionization-induced SPM）是强场光学的核心机制，与我们关注的强场驱动多电子动力学直接相关
- **交变磁 / 莫尔**：作者明确指出 APAPS 可应用于固体（包括 semiconductors、2D materials），未来可结合交变磁 field 或莫尔 structure研究量子几何驱动的超快电子动力学
- **量子几何**：attosecond pump-probe 可探测由量子几何（Berry curvature、quantum metric）主导的谷间相干和赝自旋动力学

## 来源

- 蒸馏自全文（deep-read）：M. Kretschmar, E. Svirplys, M. Volkov, T. Witting, T. Nagy, M. J. J. Vrakking, B. Schütte, "Compact realization of all-attosecond pump-probe spectroscopy," *Science Advances* (2023), arXiv:2306.16212

<!-- methods-backfill:v1 -->

## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：紧凑全阿秒泵浦-探测光谱（all-attosecond pump-probe spectroscopy, APAPS）

**原理**：用商用 1 kHz Ti:sapphire 激光经 hollow-core fiber 后压缩至 3.8 fs 驱动 HHG，产生 isolated XUV 脉冲；通过离焦（out-of-focus）气体喷嘴几何 + 过驱动 regime 下的电离诱导自相位调制（SPM）blueshift 获得 10 nJ 级 XUV 输出；再用两片窄带球面多层镜将 XUV 分成双色（~20 eV pump / 33.5 eV probe）经 delay stage 重合于样品，由 VMI 离子成像实现真正的 XUV-XUV attosecond 时间分辨泵浦探测。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 激光器 | commercial Ti:sapphire (Spitfire Ace), 1 kHz, 800 nm 中心波长, 初始脉宽 36 fs | 研究方法·激光系统与脉冲压缩 |
| hollow-core fiber 后压缩 | fiber 长 1 m、芯径 400 µm、充 He 3.5 bar，3 mJ 入射，经 6 片 chirped mirrors (PC70) 压缩至 3.8 fs / 1 mJ | 研究方法·激光系统与脉冲压缩 |
| HHG 聚焦镜焦距 | f = 75 cm（球面镜） | 研究方法·紧凑 HHG 装置 |
| 气体喷嘴位置 | 距 driving laser focus ~3.5 cm upstream（束腰前方数 Rayleigh 长度） | 研究方法·紧凑 HHG 装置 |
| 驱动激光峰值强度（焦点处） | 5×10¹⁵ W/cm² | 研究方法·紧凑 HHG 装置 |
| NIR 峰值强度（喷嘴处） | 1×10¹⁵ W/cm² | 研究方法·紧凑 HHG 装置 |
| HHG 气体 | Kr（双色 APAPS）/ Xe（单色 APAPS），backing pressure 4 bar | 研究方法·紧凑 HHG 装置 |
| NIR 滤除 | Al filter 厚 100 nm | 研究方法·紧凑 HHG 装置 |
| 双色分光镜 | 球面多层镜 f = 5 cm；Mirror A 高反 <25 eV（pump, ~20 eV），Mirror B 反射峰 33.5 eV（probe） | 研究方法·双色 XUV Pump-Probe 方案 |
| XUV 束腰半径 | 水平 ~1.2 µm × 垂直 ~2.4 µm（紧聚焦） | 研究方法·双色 XUV Pump-Probe 方案 |
| XUV 脉冲能量（光源处） | 10 nJ | 主要发现·XUV 脉冲能量与强度 |
| XUV 脉冲能量（相互作用处） | Mirror A 0.12 nJ / Mirror B 0.15 nJ | 主要发现·XUV 脉冲能量与强度 |
| XUV 峰值强度 | pump 8×10¹² W/cm² / probe 1×10¹³ W/cm² | 主要发现·XUV 脉冲能量与强度 |
| 相互作用区原子密度 | ~10¹³ cm⁻³ | 研究方法·离子检测 |
| 探测器 | velocity-map imaging spectrometer (VMIS)，spatial imaging 模式；MCP/phosphor screen + CCD | 研究方法·离子检测 |
| 单 attosecond burst 宽度 | 240 as | 主要发现·双色 APAPS 实验 |
| pre-/post-pulse 相对强度 | (16 ± 2)% | 主要发现·双色 APAPS 实验 |
| Ar²⁺ 产量 risetime（20%→80%） | 630 as | 主要发现·双色 APAPS 实验 |
| 信号产率与噪声 | ~1 Ar²⁺ ion/shot（4000 shots×2 scans 累积 ~8000 ions），shot noise ~1–2% | 主要发现·双色 APAPS 实验 |
| 双光子电离事件数估算式 | N_event = c·2π n₀ N_pump σ_pump N_probe σ_probe / λ_pump；n₀=10¹³ cm⁻³, N_pump=3.75×10⁷, N_probe=2.8×10⁷, σ_pump(Ar@20 eV)=32.5 Mb, σ_probe(Ar⁺@33.5 eV)=10 Mb；共线预测 2–3 Ar²⁺/shot | 主要发现·信号估算 |

**适用边界**：面向气相原子/分子样品的离子检测方案，受 shot noise（1–2%）限制且 satellite pulses 相对强度 (16±2)% 需 CEP 稳定才能抑制；固体样品需同时解决少数几发内损伤防护与高灵敏度探测小 transient 信号的问题。
**代表作**：Kretschmar et al. 2023, Science Advances (arXiv:2306.16212)
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[VMI]]
- [[pump-probe]]
- [[quantum metric]]
- [[啁啾脉冲放大]]
- [[强场驱动]]
- [[泵浦探测]]
- [[量子几何]]
<!-- /linsai-wikilinks -->
