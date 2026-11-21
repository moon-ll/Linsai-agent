# R1 科学性评审 — key-transient-quantum-phase-optical-20260726

- 评审人：R1（科学性，强场超快光学/凝聚态方向 PI）
- 评审日期：2026-10-16（落盘 2026-10-18）
- 评审对象：`04_proposal/sections/` 四模块（rationale / content / scheme / references），r4 版本
- 课题定位：国家重点项目（key），按从严标准执行
- 巩固性背景：2026-10-11 评审团曾做 5 处量纲修补 + [32] 补 body 引用，本轮重点检查修补巩固性与剩余科学短板

## 总评分（五项明细）

**总评分：0.78**（rigor 五项过三：①✗ ②✓ ③✗ ④✓ ⑤✓；锚定纪律：过三=0.78，禁折中）

| # | 核查项 | 判定 | 依据 |
|---|--------|------|------|
| ① | 数值链一致 | **未过** | R1-01（首段强度↔场强换算断裂约 3–7 倍）、R1-02（nm⁻² 与 Å⁻² 单位口径冲突，差 100 倍）；其余数值链（ΔC 预算 0.055/0.155/0.115、SNR 6.5–8.7、抖动方和根 94/117 as、样本量 2.5×10⁵ 发、ℏω/E_g 分区落点 2.76/1.03/2.07/0.10–0.19/0.75–1.55/1.5–3.1）逐一复算全部自洽 |
| ② | 指标定义可操作 | 过 | ΔC 三档（0.20/0.50）、SNR 区间、T_L/4 跨区判据、抖动 ≤100 as、17+3 组窗口、二阶偏差 <0.05（限标定子区间）均可检验；月度里程碑绑定判据 |
| ③ | 文献支撑真实 | **未过** | R1-03（WS₂ 模拟工作两处错标 [18]，题录文字与编号冲突）、R1-04（[9] 的 χ⁽³⁾ 10⁻⁹ m²/V² 实为原文中石墨烯数值，归属失真并被借用为 ATA 标度起点）、R1-05（18.24/26.86 两数值公开摘要未含，待正文核对）；抽查条目本身（[9][18][21][23][40]）全部真实存在，无伪造模式 |
| ④ | 逻辑闭环 | 过 | 可定义性→写入→读出→反演→残差回传链条完整；每环节配失效边界与备份路径（D1–D6 双路径）；"事后可观测→可写可读可反演"的目标递进有据 |
| ⑤ | 模块自洽 | 过 | 四文件间 ΔC 阈值、SNR、E_g 取值口径、代表体系定义、迭代周期、靶材分区全部一致；2026-10-11 补引的 [32]（Aich）在 scheme §2.1(a) 有 body 引用，巩固到位 |

**巩固性结论**：上次量纲修补的 §0 约定表本身自洽（ℏΩ_R 的 eV·V=1 eV 换算正确），[32] 补引成功；但 §0 "以 nm⁻² 为统一记录单位"的声明未同步落实到 §2.2 与 §5(2) 的 Å⁻² 用法（R1-02），属修补不彻底；首段强度-场强断裂（R1-01）不在上次修补覆盖范围内，为新发现。

**与自评的差异说明**：末三轮 0.74/0.74/0.84、monitor 0.86 高于本轮 0.78，差异全部来自可复核的客观缺陷（四项 major 均附原文摘录与外部证据），非口径分歧。

## 意见清单

- [R1-01|major] rationale（一）§首段｜强度-场强换算｜首段强度窗口与示例场强数值断裂｜原文："峰值强度达到 5×10¹³–10¹⁴ W/cm²……以 Bi₂Se₃……E₀ ≈ 0.5 V/Å"｜修改建议：5×10¹³–10¹⁴ W/cm² 对应 E₀≈0.19–0.27 V/Å（I=½cε₀E₀²），0.5 V/Å 对应约 3.3×10¹⁴ W/cm²。二选一：例改 E₀≈0.27 V/Å、ℏΩ_R≈1.4 eV；或强度上界改 3×10¹⁴ W/cm² 并同步全文 ℏΩ_R 区间表述。
- [R1-02|major] rationale §0 vs §2.2/§5(2)｜Berry 曲率积分单位｜统一声明与实际用例单位冲突且量纲存疑｜原文："本文以 nm⁻² 为统一记录单位"vs"从 18.24 增至 26.86 Å⁻²"｜修改建议：BZ 上 ∫Ω(k)d²k 物理上无量纲（=2πC）。统一改为无量纲积分值（或明确定义为"Berry 曲率峰值 Ω(K)，单位 Å²"），并同步替换 §0、§2.2、§5(2) 三处，消除 100 倍口径差。
- [R1-03|major] rationale §2.2 末段、§2.3 第四级段｜WS₂ 模拟引用编号错位｜[21] 题录内容两处错标为 [18]｜原文："†Zhao 等[18]于 2026 年正式发表的 WS₂ 第一性原理模拟（J. Phys. D, 2026, 59: 215104）"｜修改建议：J. Phys. D 59:215104 是 [21]（Zhao Z. 组）题录，[18] 是 arXiv:2507.03791（MgO 实验）。上述两处及 §2.3 "†Zhao 等[18]在 WS₂……"均改引 [21]；MgO 实验处的 [18] 保留。
- [R1-04|major] rationale §2.1 + content §2.3｜[9] 数值归属失真｜χ⁽³⁾ 10⁻⁹ m²/V² 系原文石墨烯值，非 TI 体系，且被借作 ATA 标度起点｜原文："三阶极化率 χ⁽³⁾ 达约 10⁻⁹ m²/V²……借其物理量级……作 ATA 标度反演的起点"｜修改建议：原文该数值描述石墨烯 Dirac 载流子 THz 热电子非线性（较典型半导体大 7 个量级）；"场增强约 10²"指 SRR 谐振环而非"体态场增强"。删除或改标归属，ATA 标度起点仅取自团队预研 SNR≈105（rationale §5 已有此数据链）。
- [R1-05|minor] rationale §2.2/§5(2)｜18.24→26.86 待溯源｜两数值未见于原文公开摘要，无法在付费墙外核对｜原文："+2% 拉伸应变使 K 谷 Berry 曲率积分从 18.24 增至 26.86 Å⁻²"｜修改建议：标注具体出处（图/表编号），并注明原文摘要仅可证实"垂直谐波分量近翻倍"的定性结论。
- [R1-06|minor] rationale 首段 vs scheme §2.1(b)｜示例耦合强度越档｜Bi₂Se₃ 例 ℏΩ_R≈2.5 eV 对应 ℏΩ_R/E_g≈8.3，超方案三档上界（写入档 1–3）｜原文："ℏΩ_R ≈ 2.5 eV"｜修改建议：例旁注明该点属"带隙完全闭合的极端对照点"（scheme 已有该极端档表述），或改取写入档内值（如 E₀≈0.2 V/Å、ℏΩ_R≈1 eV）。
- [R1-07|minor] rationale §3 问题三｜统计表述不严谨｜"零点假设……单侧功效约 90%"混淆检验方向与功效定义｜原文："该零点假设对应 1.29σ，单侧功效约 90%"｜修改建议：改为"工程阈值 0.20 位于合成不确定度 1.3σ（保守）–1.7σ（去偏）处，对应正态覆盖概率约 90–96%"。
- [R1-08|info] references｜文献层整体可信｜抽查 5 条关键锚定文献全部真实存在；APS 短式 DOI（10.1103/7zjc-4b4r 等）经 Crossref 反查为 2025–2026 年合法新格式｜建议：预研 SNR≈105±18"不援引 DOI"的诚实处理方式（rationale §5）值得保留。

## 量化锚核实记录（证据 URL）

1. **[9] Di Gaspare et al., Light Sci. Appl. 14:337 (2025)** — 存在性 ✓（arXiv:2604.27864 与 LSA DOI 关联确认）。核实结论：原文为 THz QCL（3.25 THz）驱动 SRR 谐振环 + Bi₂Se₃/(In,Bi)₂Se₃，区分体态（奇次）/拓扑表面态（奇+偶次）属实；但 χ⁽³⁾~10⁻⁹ m²/V² 出现于石墨烯 Dirac 材料语境（"This is a consequence of the third order non-linearity (χ⁽³⁾~10⁻⁹ m²/V²), that is almost seven orders of magnitude larger than that of typical semiconductor heterostructure lasers"），非 TI 体系数值；"场增强至两个量级"指谐振环（"electric field amplification factors up to two orders of magnitude larger than in a bare film"），非"体态场增强"；SHG 效率 3.5×10⁻⁵ 未见于已抓取正文部分，未能证实。→ R1-04、R1-05 依据。
   - https://arxiv.org/abs/2604.27864 （含 Journal reference: Light Sci Appl 14, 337 (2025); DOI 10.1038/s41377-025-01847-5）
2. **[21] Zhao Z. et al., J. Phys. D 59:215104 (2026)** — Crossref 确认真实（Zhao Zhenjiang、Zheng Zhihua、Xu Zhiyi et al.，新疆大学，2026-05-26 出版，题名吻合）。摘要证实"tensile strain modulates the total harmonic yield and specifically amplifies the perpendicular harmonic component by nearly a factor of two"+ Berry curvature reshaping（垂直分量近翻倍 ✓）；18.24/26.86 两个数值未见于摘要（正文付费墙）。→ R1-03、R1-05 依据。
   - https://api.crossref.org/works/10.1088/1361-6463/ae6c35
3. **[40] Illes, Carbotte, Nicol, PRB (2015) α-T₃ 模型** — 真实（SciSpace 收录 PRB 2015-12-07，题名逐字吻合；卷 92 与 245410 文章号合理）。判据框架的模型基础可靠。
   - https://scispace.com/authors/e-illes-1qx25iwdq4
4. **[23] Lorenzo et al., PRB 114 (2026)** — DOI 10.1103/7zjc-4b4r 经 Crossref 反查命中（Lorenzo, Batista, Jangjan et al. incl. Ghimire，PRB 114 issue 8，2026-08-24），APS 短式 DOI 合法。→ R1-08 依据。
   - https://api.crossref.org/works/10.1103/7zjc-4b4r
5. **[18] arXiv:2507.03791（MgO Floquet-Bloch）** — 真实（"MgO driven by a strong few-cycle near-infrared field……Floquet–Bloch sidebands"与申请书描述一致）。→ R1-03 中 [18] 与 [21] 为两项不同工作的确认依据。
   - https://arxiv.org/html/2507.03791v2
