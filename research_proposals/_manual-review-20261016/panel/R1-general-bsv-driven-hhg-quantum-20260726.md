# R1 科学性评审 — general-bsv-driven-hhg-quantum-20260726

- 评审轮次：r1 重置后首轮深审（通道 B 晋级前把关）
- 评审对象：04_proposal/sections/ 四文件（rationale / content / scheme / references）
- 评审日期：2026-10-17
- 评审维度：物理硬错、创新点真实性、判据有据、跨模块口径一致、科学逻辑闭环

## 总评分（五项明细）

**总评分：0.85**（rigor 五项核查：过四项，扣①）

| # | 核查项 | 结论 | 依据 |
|---|--------|------|------|
| ① | 数值链一致 | **不通过** | 驱动档光子数上限（10⁸–10¹⁰）与 HHG 阈值内推结果（2×10¹⁰）直接矛盾（R1-01）；其余数值链（能量换算、内场标度、sinh²r 区间、7–13 阶光子能量）复算全部通过 |
| ② | 指标定义可操作 | 通过 | QEF 三维度、$Q_F=(I_{max}-I_{min})/(I_{max}+I_{min})$、No-Go 判据（95% CI 跨零、偏差>5%、R²≥0.7/ΔAIC≥10）均可操作且跨章同口径 |
| ③ | 文献支撑真实 | 通过 | 联网反查：Rasputnyi 2024（1.6 μm/25 fs/4–7 阶/至少 5–15 倍/0–2×10¹³ 光子/±1 V/Å）全组核实为真；Wu 2023 PRL（ν=1 关联能隙 ~126 meV、T_c >285 K）核实为真（证据见锚核实记录） |
| ④ | 逻辑闭环 | 通过 | "光源—样品—谱学—理论—反演"五环单向衔接 + 三层降级标签（多体态探针→分类工具→响应特征化）闭环完整；零均值场导致 $Q_F$ 一阶干涉为零的前提性讨论诚实且物理正确（混合阶项 n+m=q 通道分解核对无误） |
| ⑤ | 模块自洽 | 通过 | 抽查跨章口径：5% 偏差阈值（$Q_F$ 回归/BSV 标定）、150 mrad、q_ref∈{7,9}、7–13 阶、SnS₂ 2.1–2.3 eV、四类对照体系——rationale/content/scheme 三章一致；Gothelf 33 阶预言与 7–13 阶窗口的"机制层 vs 工程层"划界在 content §2.2 独立成段自洽 |

扣分标注：**①**（R1-01 结论句与自身算术矛盾；R1-02 g² 口径与档位配置存在张力）。

## 意见清单

[R1-01|major] scheme §3.2｜HHG 阈值内推段结论句与自身算术矛盾｜"该内推落在驱动档 $10^{8}$–$10^{10}$ 光子数上限，证明该工程参数区间的光子数可达 TMDC HHG 阈值强度"｜内推全文自算得 $N=5$ nJ $\approx 2\times10^{10}$ 光子，已超 $10^{10}$ 上限 2 倍，"落在上限"不成立。修改建议（三选一）：(a) 驱动档上限上调至 $3\times10^{10}$；(b) 聚焦收紧至 ≤3 μm FWHM（面积 $\approx7\times10^{-8}$ cm²，阈值能量 1.8 nJ ≈ $7\times10^{9}$ 光子，落在档内）；(c) 补引 800 nm 波段 TMDC HHG 阈值 ≤$2\times10^{11}$ W/cm² 的文献依据使 5 nJ 下调。

[R1-02|minor] content §2.1 / scheme §3.2｜$g^{(2)}(0)=3+1/N$ 公式适用域与"高增益多模统计标定档"配置存在口径张力｜"统计标定档运行于高增益多模区（皮秒级脉冲、单脉冲光子数 $10^{13}$ 量级），用以复现 $g^{(2)}(0)=2$ 与 $3+1/N$ 双配置基线"｜$3+1/N$ 仅对单模（或模式完全收集）简并 BSV 成立；高增益多模简并 BSV 实测为 $2+1/M$（M 为模式数）。建议补注："复现 $3+1/N$ 须在单模投影/模式全收集条件下进行，并给出 M 上限"。

[R1-03|minor] rationale §1.2.3 / content §2.3｜弱关联基线 $U/W\approx0.5$ 无文献锚｜"单层 TMDC MoS₂、WSe₂，$U/W\approx0.5$，作为本征'无关联'基线"｜建议补引 TMDC 有效 U 与带宽 W 的第一性原理估计（cRPA/GW 类文献），或将口径放宽为"$U/W\lesssim0.5$（按 cRPA 有效 U 估计区间）"。

[R1-04|minor] content §2.3｜$V\geq0.05$ 可见度门槛表述把待验量写成已验量｜"$V \geq 0.05$ 的可见度门槛落在 SBE-Q 模型预期区间"｜SBE-Q 第二年才建成，此句应改为"$V\geq0.05$ 预期落在 SBE-Q 预测区间内，待第二年定量确认"。

[R1-05|minor] scheme §3.2｜表格符号残留污染段首｜"|HHG 阈值强度所需最低光子数内推论证如下"｜删除段首多余的"|"字符。

[R1-06|minor] rationale §1.1 / references [19]｜Ghimire 文献年份口径分裂｜rationale 写"2010 年（在线）/2011 年（刊印）"，引用表落 "(2010)"｜Nat Phys 7(2) 138–141 正式卷期为 2011；建议引用表统一为 (2011)，行文保留"2010 年 12 月在线"括注。

[R1-07|minor] content §2.2 / scheme §3.3｜$T_2$ 筛选窗口 3–5 fs 空档未定义归属｜"须先经第一年的瞬态吸收与 PL 线宽预研筛选 $T_2$ 预期大于 5 fs 的样品批次"；"1–3 fs 下限区间的样品标记为 SBE-Q 失效风险区"｜3–5 fs 样品（既不过 5 fs 筛选线又不在 1–3 fs 风险区）处理路径未定义；建议补一句"3–5 fs 样品按唯象退相干主方程复核路径处理"。

[R1-08|minor] scheme §3.6｜引用数值自带"需回原文复算"标记进入定稿｜"THz 谐波跨相变产额比端点 75–360 倍（端点数值需回原文图复算）"｜定稿前应完成 Prajapati 等原文图值复核；未核实前建议降为量级表述（~10² 倍）并保留复核注。

[R1-09|minor] rationale §1.2.3｜1T-TaS₂"需 4 K 低温平台"的物理必要性表述过强｜"强关联——Mott 绝缘体候选 1T-TaS₂ 等，需 4 K 低温平台"｜1T-TaS₂ 公度 CDW/Mott 基态在 <180 K 已形成，4 K 属工程选择而非物理必需；建议改为"低温平台（≤100 K，4 K 兼容）"以免评审质疑平台绑定。

## 量化锚核实记录（证据 URL）

### 锚 1（课题 1 核心实验基线）：Rasputnyi et al. 2024, Nat. Phys. 20, 1960 / arXiv:2403.15337
- 申请书声称：1.6 μm、25 fs、4–7 阶、同平均强度 5–15 倍产率提升、光子分布 0 至 2×10¹³、±1 V/Å 亚周期涨落。
- 核实结果：**全部为真**。原文："Both pulses are centred at 1.6 μm (0.77 eV), with the former having a duration of 70 fs (FWHM) and the latter of 25 fs"；"the BSV-generated 4th–7th harmonics show at least 5 to 15 times higher yield than the same harmonics driven by coherent pulses with identical mean intensity (2 TW cm⁻²)"；"covering states from 0 to 2×10¹³ photons per pulse, and sub-cycle electric field fluctuations over ±1 V/Å"。
- 附注：原文对照相干光脉宽为 70 fs（BSV 25 fs），申请书本课题未提此差异但课题 3 scheme 已括注，可对齐；"平均光子数 $2\times10^{12}$"未在摘要/正文可见部分逐字出现，与原文"尾部超均值 6 倍概率 2%"自洽，判部分核实（量级无争议）。
- 证据：https://arxiv.org/abs/2403.15337 ；https://arxiv.org/html/2403.15337v2

### 锚 2（中等关联对照体系依据）：Wu F. et al. 2023, PRL 131, 256201
- 申请书声称：扭转双层 MoS₂ ν=1 处关联能隙约 126 meV、临界温度高至 285 K。
- 核实结果：**为真**。原文摘要："the correlated electronic state at v = 1 shows a giant correlated gap of ~126 meV and may persist up to a record-high critical temperature over 285 K"。
- 证据：https://arxiv.org/pdf/2311.16655 ；http://www.iop.cas.cn/xwzx/kydt/202312/P020231222624231372165.pdf

### 锚 3（领域开山文献年份）：Ghimire et al., Nat. Phys. 7, 138
- 核实结果：正式卷期 2011 年（2010 年 12 月在线）。rationale"2010（在线）/2011（刊印）"双口径正确，但引用表统一落 2011 更规范（见 R1-06）。第三方综述确认实验参数（3.25 μm、100 fs、500 μm ZnO、5 TW/cm²、至 25 阶）。
- 证据：https://www.materialsfutures.org/article/doi/10.1088/2752-5724/ac740d

## 评审结论

通道 B 晋级前科学质量总体扎实：判据体系（QEF 三维度 + $Q_F$ 自洽锚 + 显式 No-Go）完整可操作，文献锚经反查真实，零均值场干涉机制的物理讨论诚实准确。**唯一 major 为驱动档光子数上限与阈值内推的 2 倍矛盾（R1-01），属可行性论证枢纽数字，晋级前应修复**；其余为口径与表述级 minor。修复 R1-01、R1-02 后五项可全过，届时可达 0.90+。
