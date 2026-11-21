# R1 科学性评审 — general-attosecond-streaking-20260822

评审人：R1（领域资深 PI，强场超快光学方向）｜评审日期：2026-10-17｜输入：rationale.md / content.md / scheme.md / references.md 四文件全文

## 总评分

**总评分：0.78**

| 维度 | innovation | feasibility | rigor | expression | completeness |
|---|---|---|---|---|---|
| 分数 | 0.80 | 0.74 | 0.72 | 0.82 | 0.85 |

**五项核查（rigor 定档）**：①数值链一致 ✗（束线时间预算最坏端算术矛盾；其余 Up/γ/截止能量/中点能量/计数效率链/时能换算共 10 余条逐一复核通过）｜②指标定义可操作 ✓（G1/G2/G3 判据、双端度量分列、三档分档表均可操作）｜③文献支撑真实 ✗（四个外部文献锚全部核实为真，但 XCOM"伴峰截面比/多通道贡献核算"锚定在物理上不成立）｜④逻辑闭环 ✗（rationale §4 末段 rACE"独立外部参考"句与同段"rACE 全文无此数值"句直接互斥）｜⑤模块自洽 ✗（rationale 与 scheme 对 rACE 锚定状态口径不一；Ne 档位归属跨章矛盾）。**过 1 项 → rigor 0.72**。

**分数连续下降根因（monitor 负反馈病灶）**：本课题的争议核心是"四设计值的锚定体系"。每一轮优化都在"文献锚定值 ↔ 方案设定值"之间反复横跳：rationale §4 已把 rACE 8%–15% 降级为 XCOM 设计估值，但同段又残留"以 rACE 已发表工作报道的……为独立外部参考"复辟句，scheme §3.3 分档表又写"参考 Inzani 等[8]氩 3s/3p 典型区间"——三章三口径，任何一致性/判据有据检查都会重新命中；叠加 XCOM 锚根本不可能通过原文核对（库本身无伴线通道数据），critic/monitor 每轮都触发新的 critical，修复只做单点不改全链，形成"改一崩二"的振荡下降。**治本方案：一次性统一锚定声明**——8%–15% 与 10% 基准点全文统一为"XCOM 设计估值 + rACE 方法学对照"；XCOM 三能量点"主伴峰截面比"锚全文删除或改为 TDSE 模拟端标定值。

## 意见清单

[R1-01|critical] rationale｜§4 末段（设计阈值收口段）｜rACE 锚定同段自相矛盾：先承认原文无数值，复称其为独立外部参考（③④）｜"该对照基准点不依赖本项目自身设计值的循环论证：以 rACE 已发表工作报道的氩 3s/3p 在 XUV 高段多通道贡献典型区间为独立外部参考"｜删"已发表工作报道的"，改为"以氩 3s/3p 在 XUV 高段按 XCOM 核算的设计估值代入，rACE 仅作交叉验证的方法学对照"。

[R1-02|critical] rationale/scheme/content｜rationale L107/L115、scheme §3.1 段5 与 §3.3 分档表、content §2.2｜XCOM/FFAST 为独立原子近似截面库，无 shake-up 伴线通道概念，不能"核算"甲烷 18%–24%/氮气 16%–26% 多通道贡献或"主伴峰截面比"（③）｜"独立验证锚点为 NIST XCOM 截面库在 290.7 eV / 350 eV / 409.7 eV 三能量点上的甲烷 C 1s 主伴峰截面比"｜全部降级为方案设定值：伴线分支比改引 CH₄ C 1s shake-up 谱学实测文献或声明由本项目 TDSE 模拟端标定，XCOM 仅提供元素/壳层总截面。

[R1-03|high] scheme｜§3.3 末段（束线时间预算）｜时间预算算术矛盾：单组最坏 1–2 周 × 6 组 ≠ 合计最坏 4 周（①）｜"单组最坏约 1–2 周。六组合计纯采集典型约 2 周、最坏约 4 周"｜改为"最坏 4–8 周（假设仅低截面能点组落入最坏端）"并显式给出最坏组数假设，或重算。

[R1-04|high] scheme/rationale/content｜scheme §3.1 段3 与 content §2.4｜Ne 档位归属跨章矛盾：自述 XUV 高段 8%–15% 且"渐升"，水窗段又称"低于 5%"，隐含 2s/2p 比值在 150→284 eV 间骤降却无依据；且"光电子由 2p 价壳层释放"漏列开放的 2s 通道（阈 48.5 eV）（①⑤）｜"水窗段 284 eV 之上 Ne 1s 阈值约 870 eV 远高于能区上限，光电子由 2p 价壳层释放。按 XCOM 与 FFAST 核算，水窗段多通道贡献低于 5%"｜补 2s/2p 截面比随能量演化的数值依据；若依据不足，把 Ne 水窗档改为"5%–8% 过渡带、待实测标定"，并修正"仅 2p 释放"表述。

[R1-05|high] scheme｜§3.3 分档表（线性响应档行）｜跨模块口径不一：表内仍把 8%–15% 归于 Inzani[8]"典型区间"，与 rationale"rACE 公开全文未见该数值"直接冲突（⑤）｜"线性响应档 8%–15% ... rACE 交叉验证基准点（约 10%，参考 Inzani 等[8]氩 3s/3p 典型区间）"｜表内改为"约 10%，本项目 XCOM 设计估值；rACE 作交叉验证方法（其原文不含该区间）"。

[R1-06|medium] scheme｜§3.2 段4（100 eV 阈值推导）｜推导伪量化："π/2 一通约 1.57 rad，取整为 1 rad"物理依据不成立——偶极相位在发射时刻确定，非在 IR 半周期内累积；200 eV→100 eV 的折减亦无独立依据（④）｜"IR 半周期对应相移量按 π/2 一通约 1.57 rad，取整为 1 rad 量级。该量级对应光电子动能上限约 200 eV"｜删"取整"步骤，改为"以分波偶极相位差 dη/dE 与条纹能移量级估算的方案设定值，区间 100–140 eV 由模拟端标定落定"。

[R1-07|medium] references｜[46][47]（rationale §1 首段）｜Keldysh/Corkum 以名字-年份进入正文但无 [N] 角标挂靠，两条目孤儿化，与"47 条文献"陈述的挂靠预期不符（③⑤）｜"其强场电离物理可追溯至 Keldysh 于 1965 年建立的非微扰电离理论框架……与 Corkum 1993 年提出的三步模型"｜rationale §1 首段对应位置补 [46][47] 角标。

[R1-08|low] content｜§2.3｜二级修正 100 eV 阈值未同步"水窗段 140 eV"双值口径（rationale/scheme 已双值化）（⑤）｜"光电子动能跨越 100 eV 为该二级修正的动能启用阈值"｜补一句"800 nm 段设计值；水窗段（1850 nm）相应上移至 140 eV 量级，见方案 §3.2"。

**量化换算复核通过项（不计扣分，供管线对账）**：Up=9.33×10⁻¹⁴Iλ² 与 γ=√(I_p/2U_p)（800 nm、10¹⁰ W/cm²、I_p=14 eV → γ≈108>100 ✓）；HHG 截止 800 nm@(5–8)×10¹⁴ → 119–176 eV、1850 nm → ≥531 eV、1.6 μm → ~400 eV ✓；能区中点 100/346.85/476.35 eV ✓；N₂ 15.58 eV→115.6 eV、Ar 15.76 eV→84/134 eV、116–150 eV 二级激活区 ✓；Ar 2p 250.78/Kr 3d 93.8/Xe 4d 68/Ne 1s 870/CH₄ C1s 290.7 eV 阈值 ✓；计数链 1.8×10⁻⁷–2.0×10⁻⁶ ✓；条纹矢势展开 U_p=A₀²/4 与 A²/2=2U_p sin² 等价性 ✓。

## 量化锚核实记录

1. **Cousin 2017 PRX 7, 041030 — 322 as 孤立脉冲上限**：✅ 锚定成立。APS 摘要原文："we are able to confirm the generation of an isolated attosecond water-window SXR pulse and we can place an upper bound on the pulse duration of 322 as"。URL: https://journals.aps.org/prx/abstract/10.1103/PhysRevX.7.041030
2. **Schultze 2010 Science 328, 1658 — Ne 2s/2p 相对延迟约 21 as**：✅ 锚定成立。Science 摘要原文："We used attosecond metrology to reveal a delay of 21 ± 5 attoseconds"。URL: https://www.science.org/doi/abs/10.1126/science.1189401
3. **Gao 2025 arXiv:2508.14774 — 25±2 as、50–320 eV、>10¹² ph/s**：✅ 全部精确命中。摘要原文："we demonstrate the generation of 25±2 attosecond light pulses...spans photon energies from 50 eV to 320 eV...calibrated photon flux exceeding 10^12 photons per second"。URL: https://arxiv.org/abs/2508.14774
4. **Driver 2024 Nature 632, 762 — NO K 壳层时延高达 700 as**：✅ 锚定成立（正文"氧与氮两 K 壳层间相对时延"与原文表述一致）。arXiv 版原文："unexpectedly large delays, ranging up to 700 attoseconds in NO near the oxygen K-shell threshold"。URL: https://arxiv.org/html/2402.12764
5. **Inzani 2024 J. Phys. Photonics 6, 025007（rACE）—"优于 24 as 绝对延迟确定度"**：文献真实（DOAJ/Google Scholar 确认卷期页）。期刊版摘要未含显式 24 as 数值；作者同主题会议版标题为"Sub-Atomic-Unit Absolute Delay Calibration"（IEEE），与"优于原子单位时间"表述相容。**建议按机理级锚对待，正文引用时核对期刊版正文图注的确定度数值。** URL: https://www.doaj.org/article/1e9bd2ac3aa9468d9328a0db74e57ee8
6. **XCOM/FFAST"甲烷 18%–24%、氮气 16%–26% 多通道贡献"与"三能量点主伴峰截面比"**：❌ 锚定不成立（非文献不真实，而是数据源物理不支撑：独立原子近似库无 shake-up 伴线分支比），**需降级为方案设定值/模拟端标定值**——见 R1-02。
