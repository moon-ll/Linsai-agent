# R1 科学性评审 — general-quantum-geometry-inversion-20260726（r4→r5）

评审人：R1（领域资深 PI，强场超快光学/凝聚态）｜评审日期：2026-10-29｜评审对象：`04_proposal/sections/` 四模块（rationale / content / scheme / references / full_review，r4 版）
上游输入：`_manual-review-20261016/panel/R1-general-quantum-geometry-inversion-20260726.md`（上轮 9 条：major 2 / minor 7，意见编号沿用 R3-xx 前缀；R1 总评 0.85→本轮 monitor 0.80）、`optimizing/.../05_review/manual-revision-20261016.md`（major 2 采纳 + minor 4 采纳 / R3-05、R3-06 驳回转 r5 / R3-08 延后）、`04_proposal/params.json`（v7.2.19 口径表 2 条，2026-10-18 sealed）

专项任务：逐条核对 params.json 2 条口径条目（程序化正则匹配四章）；对上轮 R3-01～R3-09 逐条复核「已修 / 回退 / 遗留」；重点核查 g²(0) 定义式（光子数算符标准形式）、Ω/g 可辨识性（cond(I)、Fisher 信息条件数表述）、数值口径两档；联网反查 6 个承担判据链的量化锚。

---

## 一、专项核查（口径自洽）

### 1.1 params.json 2 条口径条目逐条判定（程序化正则匹配 rationale/content/scheme/full_review）

| 口径条目 | stale_patterns 数 | 命中 | 判定 |
|---|---|---|---|
| g2(0) 定义式（光子数算符标准形式） | 2 | 0 | **保持 ✓**（rationale L23 现为 $g^{(2)}(0)=\langle\hat a^\dagger\hat a^\dagger\hat a\hat a\rangle/\langle\hat a^\dagger\hat a\rangle^2=\langle:\hat n^2:\rangle/\langle\hat n\rangle^2$，"$\hat n=\hat a^\dagger\hat a$ 为光子数算符"；场算符期望分母全文零命中） |
| g2(0) 数值口径（两档：多模 2+1/M / 单模简并 3+1/N） | 1 | 0 | **保持 ✓**（rationale L19 两档双存 + "单模热统计值 2 不用于 BSV"划界；RIN 50%↔g²≈1.5 / 200%↔g²≈3 经方差口径换算复核自洽——大 N 下 g²≈1+Var(n)/⟨n⟩²，50%=Var 口径对应 g²−1=0.5 ✓、200% 对应 g²−1=2 ✓） |

**小结：2/2 口径条目保持，无偏离、无回退。** 上轮两条 major 的修复经本轮独立物理复核成立：定义式对零均值 BSV 不再发散；数值口径"实验档读数 1.5–2（M≥2）/ 单模简并趋近 3"内部自洽（2+1/1=3 衔接两档端点 ✓）。

### 1.2 上轮 R3-01～R3-09 逐条复核

| 编号 | 上轮 severity | 当前状态 | 复核依据 |
|---|---|---|---|
| R3-01（g²(0) 定义式场算符分母发散） | major | **已修 ✓** | rationale L21–25 光子数算符标准形式 + 正规序二阶矩 + 大 N 展开式三件套齐备；params sealed 后零回退 |
| R3-02（数值口径三处互斥） | major | **已修 ✓** | rationale L19 两档双存；L25 RIN↔g² 换算闭合；rationale §1.4 L71"多模实验档 2+1/M 读数 1.5–2"传导到位 |
| R3-03（文献表乱序 + 计数） | minor | **已修 ✓** | references 物理排列现严格升序（[38][39][40][42]…[47][48][49]…[53][54][55][56]）；55 条计数与头注声明（[41] 预留、[40][54][55] 研读基础）逐条清点一致 |
| R3-04（Faeyrman 段重复） | minor | **已修 ✓** | rationale 现 2 处 Faeyrman 为不同语境（§1.2 机制引述 / §1.5 训练数据起点），逐字重复段已删 |
| R3-05（红移 2% 阈值裕度论证缺失） | minor | **部分落地** | rationale L41 已新增整段裕度论证（Sr₂CuO₃ 关联更强→红移更小、红移-阶次标度、0.01% 检出限支撑）——论证已补，但末句"按靶标关联强度下调阶次"与保守方向读法矛盾 → 本轮 R1-02 |
| R3-06（产额下界 10⁻⁷–10⁻⁶ 无文献锚） | minor | **未落地（两轮遗留）** | scheme L61 表述与上轮逐字相同，仍挂靠 [24]/[1] "实测范围同量级"，无换算式、无二次文献 → 本轮 R1-01（升级 medium） |
| R3-07（Rasputnyi 脉宽对照括注） | minor | **已修 ✓** | rationale L17"（相干对照 70 fs，同平均强度）"在位 |
| R3-08（U/W=0.50 图注双重身份） | minor | **延后（可接受）** | 相图未成图；scheme §1.0 L15 已有"失效界之上（0.5–1.0）由 BSV-SBE 多体修正承载"表述兜底；成图时补图注（列入结论提醒） |
| R3-09（g²>1.5 判据绑定模式数） | minor | **已修 ✓** | scheme L61"阈值按'多模实验档 2+1/M、单模简并档 3+1/N'两档双存定义选取"，近单模档恒高于阈值 |

**小结：6/9 已修无回退；R3-05 部分落地（论证有但末句逻辑含混）；R3-06 连续两轮未动，本轮升级为 medium；R3-08 延后属合理。**

### 1.3 编号与死条目对账

- references 共 55 条（[1]–[40]+[42]–[56]，[41] 预留缺号），头注显式声明预留与研读基础（[40][54][55]）策略，正文引用编号集合与条目一一对位，无虚号、无死链、无一号两用（程序化验证）。
- 正文引用上界 56；[41] 缺号与 [40][54][55] 无正文落点均为头注声明内的设计行为，不构成对账缺陷。

---

## 二、总评分

**总评分：0.86**（rigor 定档：五项过四 → 0.82–0.89 区间；较上轮 0.85 上升，主因 ①数值链随两条 major 修复转通过）

| 维度 | innovation | feasibility | rigor | expression | completeness | 总评 |
|---|---|---|---|---|---|---|
| 分数 | 0.88 | 0.85 | 0.85 | 0.86 | 0.87 | **0.86** |

### 五项核查明细（rigor 定档依据）

| 核查项 | 判定 | 依据 |
|---|---|---|
| ① 数值链一致 | ✓ | 上轮唯一断链（g² 定义式/口径互斥）已修复；本轮全量复算通过：r=1→8.69 dB ✓、e^{-2r} 单调性 ✓、GPU 网格 16×11×101=17,776 与 0.9–2.7×10⁴ h 预算 ✓（粗档 11×11×101=12,221 ✓）、通量链 30 光子→3×10⁶ 脉冲→60×60 点→1.08×10¹⁰ 脉冲→3000 h/30 h ✓、SNR=√30≈5.5 ✓、cond(I)=10→轴比 1/√10=0.32 与 3 倍改善 ✓、Bonferroni 0.017→族错误率 4.9% ✓、相图 11×23=253+精扫 21×3=63 ✓、瑞利长度 940 μm 与横向 5–11% 退化 ✓、2.5 μJ/0.68 eV/5.5 比值/0.01% 分辨率 ✓、f-sum 标度 6.25%/7.5% ✓ |
| ② 指标定义可操作 | ✓ | 三档放大判据+双侧查表（禁止单侧命名机制）、$\tilde R_\Omega/\tilde R_g$ 收缩比定义与 Go≥2、2° 偏振突变（1° 步长×3 次重复的检出依据）、Δω/ω>2% 红移+双模型偏差比较、cond(I)<10 三指标、三档 PINN 误差阈值（5%/8%、15%/25%、20%/30%）、失效三场景——均可测量可证伪 |
| ③ 文献支撑真实 | ✗ | 产额基线"10⁻⁷–10⁻⁶ photons/pulse……与 [24]/[1] 实测范围同量级"无公开文本支撑且连续两轮未落地（R1-01，直接垫在 10⁻⁵ Go 门槛下）；"(1+U/W)² 文献常见"无引用（R1-03）。本轮 6 锚反查 Khurelbaatar/Faeyrman/Kang/Stammer/Tyulnev/Ikeda 全部真实且主体表述相符（见第四节）；Faeyrman rad 值、Tyulnev 197.3±3.5 小数位、Ikeda 50 meV 维持部分核实 |
| ④ 逻辑闭环 | ✓ | R1→R2→R3→R4 前置产出链完整、每级 No-Go 均有可发表边界结论、"产额增强≠Fisher 信息提升"贯穿、加性/乘性双侧判定禁止单侧命名；R1-02 为裕度论证段末句的局部表述矛盾，不动摇链条 |
| ⑤ 模块自洽 | ✓ | full_review 口径表 22 行逐行核对成立（10⁻⁵ 与通量预算同一身份、2°/2%/三档误差/三指标/253+63 栅格/1T-TaS₂ 相变序 550/350/180 K 四章一致）；params sealed 条目跨章零漂移 |

**过 4 项 → rigor 落 0.82–0.89 档，取 0.85。** 理由：①⑤经上轮 major 修复后全部通过且本轮复算零缺陷，②④完整；仅剩 ③一条 judging-chain 锚缺口（连续两轮遗留）加两处小引用瑕疵，故不给 0.90+。

**分数带语境**：0.86 > 0.82（通道 B 线）< 0.90（免检线）。**提示**：本轮 monitor 0.80 低于 R1 独立核验（0.86），方向与 moire 相反——monitor 偏低可能受平台期检测拖累；以本轮 R1 清单为准。修复 R1-01（一处改写为自含设计估算或补引绝对计数文献）与 R1-02（一句话逻辑修正）后，③④补齐，五项全过 → rigor 0.90+、总评 0.90 可达。

---

## 三、意见清单

[R1-01|medium] 研究方案 / 研究内容｜scheme L61、content L35｜产额基线 10⁻⁷–10⁻⁶ photons/pulse 挂靠 [24]/[1]"实测范围同量级"无公开文本支撑，连续两轮遗留（上轮 R3-06 转 r5 未落地），直接垫在 10⁻⁵ Go 门槛的"提高一个量级"推导下（扣③）｜"固体 HHG 在 800 nm 钛宝石驱动、$10^{14}$ W/cm² 峰值强度经典光条件下的实测产额下限约为 $10^{-7}$–$10^{-6}$ photons/pulse。该量级与 Ghimire 等[24] ZnO 体相 HHG 实验及 Luu-Wörner[1] 偏振分辨 HHG 的实测范围同量级。"｜[24] 公开文本以转换效率/相对产额表述，未见 photons/pulse 口径。建议替换为自含设计估算："该下界为本项目设计估算：按 ZnO 类固体 HHG 实验（[24] 等）的单阶谐波转换效率 10⁻⁸–10⁻⁷ 与驱动脉冲约 10¹⁴ 光子/脉冲的量级链折算（换算式与探测效率假设列入方法手册），属设计值而非文献直接给出值；$10^{-5}$ 判据即在该估算下界之上再留一个量级裕度。"若坚持文献口径，须补引有绝对光子计数的二次文献并交 R3 引用轮核实。

[R1-02|medium] 立项依据｜§1.2 L41｜红移阈值裕度论证末句与保守方向的自洽读法矛盾；低阶 0.5% 的幂律来源未注明（扣④③）｜"两项标度合起来给出保守方向：阈值取在最强观测锚之上、按靶标关联强度下调阶次"｜前文明言靶标（1T-TaS₂，U/W≈1.0–1.2）关联弱于 Sr₂CuO₃、期望红移更小，且"红移随阶次上升，11 阶 1.7% 对应低阶约 0.5%"——若"下调阶次"（观测窗口移到 5–7 阶），红移标度跌至 0.5% 档，2% 阈值将不可达；与"阈值取在最强观测锚之上"并置后语义自相矛盾。建议替换为："两项标度合起来给出保守方向：阈值取在最强观测锚（11 阶 1.7%）之上，观测窗口宜站在红移-阶次标度的高阶段（≥9–11 阶）以贴近锚点；若受产额限制下移至 5–7 阶，则按红移-阶次标度（低阶约 0.5%，标度取自 [10] 原文图表，正式版回核）把阈值同步下调至 0.5%–1% 档并注明外推依据。"

[R1-03|low] 研究内容｜§2.5 L91｜"比文献常见的 $(1+U/W)^2$ 平方修正更保守"——"文献常见"无引用（扣③）｜"物理验证 Go 判据采用 $(1+0.5 \cdot U/W)$ 线性标度，比文献常见的 $(1+U/W)^2$ 平方修正更保守（后者需二阶或非微扰论证）"｜建议补挂该平方标度的代表文献，或改为"比二阶微扰型 $(1+U/W)^2$ 包络（作为非必要引入的上限形式）更保守"。

---

## 四、量化锚核实记录（本轮 6 锚；上轮已核 3 锚附复用结论）

| 锚 | 申请书位置 | 核实结果 | 证据 URL |
|---|---|---|---|
| **Khurelbaatar [12] arXiv:2605.21925｜e^{-2r}、r_opt≈1.6、自校准见证** | rationale L35/L67、scheme L57/L221 | ✅ **核心成立**（上轮 R3-05 遗留的作者复核项，本轮独立核验）：摘要"the normalized cutoff variance decays exponentially with the squeezing parameter, independent of the absolute vacuum-field amplitude and therefore robust against uncertainties in the effective nanoscale mode volume. A subleading phase-noise contribution from the anti-squeezed quadrature produces a variance minimum near r_opt ~ 1.6…self-calibrating Heisenberg witness"——不依赖真空幅度/模体积 ✓、r_opt≈1.6 由反压缩相位噪声次级项决定 ✓、自校准海森堡见证 ✓；精确 e^{-2r} 指数（vs 一般指数衰减）正文级未逐字核 | https://arxiv.org/abs/2605.21925 |
| Faeyrman [16] arXiv:2606.02238｜MgO 复 Berry 相实/虚部 | rationale L45/L81、scheme §7.3 | ✅ 机制层成立："a strong THz field can transiently break inversion symmetry in MgO, inducing a dynamical complex Berry phase…directly resolve the Berry phase, accessing both its real and imaginary components. The first is associated with coherent intraband dynamics while the second with quantum tunneling"——实部带内相干/虚部隧穿归属 ✓；实部 0.1–0.3 rad、虚部 0.05–0.15 rad 具体区间与"MgO 谱可由经典 SBE 精确复现"未在摘要层出现（正文级部分核实） | https://arxiv.org/abs/2606.02238 |
| Kang [52] Nat. Phys.（arXiv:2412.17809）｜CoSn QGT 重建 | content L53 | ✅ 成立："we develop a framework to measure the QGT…using polarization-, spin-, and angle-resolved photoemission…demonstrate the effective reconstruction of the QGT in solids in the archetype kagome metal CoSn"；DOI 10.1038/s41567-024-02678-8 与条目一致；"首次在晶体中重建 QGT 实部与虚部"由"measurements restricted only to artificial two-level systems→in this work…in solids"支撑 | https://arxiv.org/abs/2412.17809 |
| Stammer [9] arXiv:2605.28236｜圆偏振量子光破缺选择定则 | rationale L17 | ✅ 成立："quantum fluctuations break the dynamical symmetry of the driving field while preserving the crystal symmetry, which enables the generation of classically forbidden harmonics"（graphene/MoS₂、圆偏振量子光） | https://arxiv.org/abs/2605.28236 |
| Tyulnev [11] Commun. Mater. 6, 152 (2025)｜TiSe₂ T_c | rationale L47、content §2.4.1 | ○ 量级成立：预印本（arXiv:2412.13329）"transition…into a commensurate 2×2×2 CDW state at transition temperature T_c≈200 K"；197.3±3.5 K 小数位仍未从公开文本核实（维持部分核实；正文主用 ~200 K，风险低） | https://arxiv.org/pdf/2412.13329v1.pdf |
| （复用本轮 moire 侧核验）Ikeda [10] arXiv:2508.00296｜Mott 熔化红移机制 | rationale L27、content §2.4.3 | ✅ 主体成立（摘要级：Sr₂CuO₃、>6 MV/cm、谐波偏离 MIR 奇数倍、DMFT 周期内电子结构重构、刚带体系可忽略）；11 阶 50 meV/1.76 eV/1.5 eV 维持部分核实（申请书已按预印本口径标注） | https://arxiv.org/abs/2508.00296 |
| （未核，额度用尽）González-Monge [45] Husimi 三条（垫 10% 三描述阈值）、Khurelbaatar [44] 全息 Fisher 四次方标度、Sumaya-Martinez [31]、Ilin [47]、Sala [4]、Han [3] | scheme L37/L85/L79、rationale L11 | ○ 未反查，交 R3 引用轮；Wang [48]（Nature 621, 487, 2023）、Gao [49]（Science 381, 181, 2023）两条为领域知名实验，凭 DOI/卷期判真 | — |

---

## 五、结论

**剩余意见性质：收尾级，非方向性风险。** 无 critical。上轮仅有的两条物理硬错级 major（g²(0) 定义式发散、数值口径三处互斥）已彻底修复且 sealed 后零回退——本轮对定义式、两档口径、RIN 方差换算做了独立物理复核，全部成立。该课题的判据体系（三档放大+双侧查表、三独立可辨识性指标、三档 PINN 误差阈值、每级 No-Go 可发表）是三份申请书中最完整的一套；本轮 6 个判据链锚反查无一虚构，其中 Khurelbaatar 的 r_opt≈1.6 判据锚（上轮遗留作者复核项）已独立核验成立。

**建议：完成两项收尾即可进入验收准备（合计半天内）。** R1-01 是唯一连续两轮遗留的实质缺口——10⁻⁵ Go 门槛的基线句要么改为自含设计估算（推荐，零新增引用）、要么补引绝对计数文献；R1-02 为一句话逻辑修正。完成后 ③补齐、④无保留，五项全过 → rigor 0.90+、总评 0.90。另两条提醒（非意见）：(a) 相图成图时落实上轮 R3-08 的 U/W=0.50 图注；(b) Faeyrman rad 区间、Tyulnev 197.3±3.5、Ikeda 50 meV/1.76 eV 三个部分核实数值在投稿前以正式版/正文图表回核，沿用上轮遗留项机制。
