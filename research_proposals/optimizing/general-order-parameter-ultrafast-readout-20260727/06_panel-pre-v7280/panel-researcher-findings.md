# 评审团 findings：科学内容视角（researcher）

评审员：engine 亲审（第二轮）｜ 课题：general-order-parameter-ultrafast-readout-20260727 ｜ 时间：2026-10-05

方法：5 章节全文通读；关键数值独立复算（γ 端点、I=½cε₀E²、Zeeman/k_BT_N 能标、sin(3φ) 三角恒等式、光子能量—波长换算）；8 处文献断言在 knowledge/wiki/papers/ 与 raw/pdfs/_text_cache/ 按 arxiv_id 逐条取证；r1 复核报告 4 条轻微观察与 writer 报告遗留 3 项（R-3/R-4/V-4）逐条消化。行号为修改前磁盘状态。

## 问题清单

### F-R1 [medium] R-3 遗留：references [37] 注记 0.8 eV 数值归属错误（本轮有据可修）

- 位置：references.md L111（[37] Krempaský 注记）
- 原文："【关联：MnTe ARPES 测得 Kramers 自旋简并的交错磁提升，非高对称动量点分裂达 0.8 eV，CrSb 候选信号机制的前置实验依据】"
- 证据：KB `wiki/papers/2024-2308_10117-observation-of-giant-band-splitting-in-altermagnetic-mnte.md` L75"实验定量：cut 3 上 |k_y| = 0.43π 处 band 1 与 band 2 分别位于结合能 1.25 eV 与 0.45 eV，对应交变磁劈裂 ~0.8 eV，与计算定量一致"——0.8 eV 系 [38] Osumi 的实测值；[37] Krempaský 无 KB 独立页面，其自身数值无法锚定。r1 复核已裁定"0.8 eV 出自 [38]"。正文 4 处 0.8 eV 均正确系于 [38]（rationale L59、scheme L55/L65、full_review L27），仅此注记错挂。
- 修改建议：[37] 注记删除"非高对称动量点分裂达 0.8 eV"，改为显式指向 [38]（合并重编号后新号 [35]）；不替 [37] 构造任何未经核实的替代数值。

### F-R2 [medium] R-4 遗留：references [16] 作者序——一手证据证实现行排序正确，结案不修

- 位置：references.md L49（[16] 条目）
- 原文："Werner, P., Lysne, M. & Murakami, Y. High harmonic generation in altermagnets."
- 证据：raw PDF 文本缓存 `knowledge/raw/pdfs/_text_cache/2407_07752.txt` L2："Philipp Werner, 1 Markus Lysne, 1, ∗ and Yuta Murakami 2"——论文署名序即 Werner 第一（Lysne 通讯作者）。r1 曾以"通行署名序冲突"存疑，本轮以一手 PDF 文本定案：现行条目与正文 5 处"Werner 等人 [16]"（rationale L23、content L37、scheme L29/L105/L115）全部正确。
- 处置：核实无误，不修改。R-4 遗留就此关闭。

### F-R3 [medium] 新发现：content L39 "L 点能量劈裂"定位超出 KB 证据

- 位置：content.md L39
- 原文："Singh 等人 [27] 随后由非弹性中子散射在 Γ-L 方向观测到该劈裂，L 点能量劈裂达 27(2) meV。"
- 证据：KB `wiki/papers/2025-2511_16086-chiral-spin-split-magnons-in-the-metallic-altermagnet-crsb.md` L90："沿 Γ–L 方向计算的能量劈裂在 H = 0.20 处达 27(2) meV，约为仪器能量分辨率（20 meV）大小"；L178：动量劈裂 0.30(2) Å⁻¹ 对应能量分裂 27(2) meV。KB 全文未出现"L 点"定位（且 L184 明示 J₁₁ 分配仍有不确定性）；27(2) meV 的 KB 支持口径为"沿 Γ–L 方向"。
- 修改建议：删"L 点"，改"沿 Γ-L 方向能量劈裂达 27(2) meV"；方向（Γ-L）与量值（27(2) meV）均为 KB 证实项，保留。

### F-R4 [low] V-4 遗留（可修部分）：references [33] 版本日期精度——KB 有精确日期

- 位置：references.md L91（[33] Granados 条目）
- 原文："arXiv:2607.23652 (v1, 2026-07)"
- 证据：KB `wiki/papers/2026-2607_23652-carrier-envelope-phase-control-of-orbital-angular-.md` L93："来源：https://arxiv.org/abs/2607.23652（v1，2026-07-26 提交）"。
- 修改建议：改"(v1, 2026-07-26)"。该条目本轮按 R8 方案并入合并条目（新号 [31]），日期精度在合并条目中一并落实。

### F-R5 [low] V-4 遗留（不可修部分）：references [48] v4 无日期——KB 证据不足，继续待核

- 位置：references.md L161（[48] Yu 条目）
- 原文："arXiv:2412.12882 (current version cited: v4)"
- 证据：KB `wiki/papers/2024-2412_12882-néel-vector-dependent-anomalous-transport-in-altermagnetic-m.md` L110 仅"提交:2024-12-17,v4 版"——证实 v4 存在但无 v4 具体日期。按纪律不凭记忆构造。
- 处置：保留原文，留待 arXiv 实查（参考文献专轮）。

### F-R6 [已核通过] 文献断言 KB 抽查相符清单（本轮新取证 6 处 + r1 已核 8 处）

| 断言（正文位置） | KB 证据 | 结论 |
|---|---|---|
| [36] 交换劈裂遵循 𝒴₄⁻³ = zy(3x²−y²)，面内 sin(3φ)，节点 0°/60°/120°（content L41） | `2026-2601_14526` L42/L93：论文自身记法"笛卡尔形式 zy(3x²−y²)，球坐标形式 r⁴ sin³θ cosθ sin3φ；节点位于 φ=0°、60°、120°" | 相符（含记法） |
| [46] 等长而对称不等价的第 11、12 近邻通道（content L39） | `2025-2503_12920` L53："等键长（8.989 Å）的第 11 与第 12 近邻交换 J₁₁、J₁₂ 的量值差" | 相符 |
| [42] K 点 275 meV、A-M 方向手性寿命差 ~20 fs（references [42] 注记、scheme L31） | `2025-2510_03759` L21/L49/L52 | 相符 |
| [7] TiSe₂ 相变温度约 200 K（scheme L77 引 [7]） | `2024-2412_13329` L31："在 Tc ≈ 200 K 转变为 2×2×2 公度 CDW 态" | 相符（scheme L77 引用无误，不改动） |
| [41] M 点短程电荷涨落与 ~6 meV 量级 Kohn 异常（scheme L31） | `2026-2603_25317` L67/L69：M 点漫散射增强 + "软化约 6 meV（文中称 approximately ∼6 meV）" | 相符（量级口径一致） |
| [25] 多条自旋非简并频率分支（content L33） | `2026-2601_19105` L54："多个量子振荡频率分支 α、β、δ、ε、ζ……自旋劈裂费米面一致解释" | 相符 |
| [48] 不同 Néel 矢量取向总能量差 < 1 meV（scheme L85） | `2024-2412_12882` L139："总能差小于 1 meV，逼近 DFT 精度极限" | 相符 |
| [27] 733(4) K、[21] Kerr/Voigt、[6] 约 200 K/3-5-7 阶、[24] 三阶 NLAHE、[38] 0.8 eV、[16] 两极限、[39] DLM 温度演化 | r1 复核报告 KB 核对项 | 沿用 r1 结论 |

另：[23]"三阶 Pancharatnam–Berry 张量"无 KB 独立页面，正文（rationale L11）与注记自洽，无法核对亦无冲突信号——保持原文不标伪。

### F-R7 [已核通过] 数值自洽独立复算（本轮重算，全部闭合）

- γ 端点：ħω(3 μm)=0.413 eV 独立代入 γ = ω√(2m\*E_g)/(eE)：m\*=1、E=0.8 V/Å 得 0.205 ✓；m\*=3、E=0.3 V/Å 得 0.945≈0.948 ✓；5 μm 下移 40%（ω∝1/λ）✓。
- I = ½cε₀E²：0.3 V/Å → 1.33×10¹²、0.8 V/Å → 8.54×10¹² W/cm² ✓。
- Zeeman：2×0.05788 meV/T×7 T = 0.810 meV ✓；k_B×733 K = 63.2 meV ✓。
- 光子能量：3—5 μm → 0.413—0.248 eV，正文"0.25—0.41 eV" ✓。
- g 波面内分布：sinφ(3cos²φ−sin²φ) = 3sinφ−4sin³φ = sin3φ，节点 φ=0°/60°/120°、反节点 30°/90°/150° 与 zy(3x²−y²) 面内投影自洽 ✓。
- σ 折算：0.5%×1.5=0.75%、0.8%×2.0=1.6% ✓。

### F-R8 [medium] R8 九条合并方案的科学边界：3 条可合并、6 条不可按条目合并

- 依据：`05_review/critic-round-8-references.md` L50-63 载明九条方案。逐条科学评估：
  - item 1 [8]+[9]：同组（Zhu J.-X. 等）双方法（解析理论正式发表 + 实时 TDDFT 预印本）同一结论——可合并；
  - item 4 [30]+[31]：γ 渡越区界定双锚（固体 HHG 标度转变 + 钙钛矿 PL Keldysh 交叉），scheme L33 同句陈述——可合并；
  - item 5 [33]+[35]：同团队（Granados/Rajak/Gao 重叠）涡旋光 OAM 双工作，rationale L31/content L57 主张互补——可合并；
  - item 2 [11]：评估结论为不可替代——[11] 提供"国内 MBE 样品工程可获得性 + 静态反常霍尔"证据（rationale L33），[21] 为"时间分辨磁光观测"，主张不同、作者团队叙事不同，替换将丢失国内可获得性论证环节——保留；
  - items 6/7/8/9（[39]+[40]、[42]+[27]、[43]+[18]、[47]+[16]）：均为理论/观测异质对（DLM 计算≠磁群分析；Tas 计算≠Singh 观测——r1 复核已明示"两条不同事实"；Liu 奇宇称 SOC≠Leeb 轨道有序；Mizuno 选择定则≠Werner 两极限）。条目级合并将迫使正文引用错挂出处，违反"引用类修改必须以核实过的来源为准"纪律——不执行条目合并；
  - item 3 [14]：与 [9] 合并到"国内方法学"组——[14] 所在 §3 组已含国内材料工程条目，组内归并不减条目数，不产生条目级动作。
- 修改建议：执行 item 1/4/5 三处条目合并（49→46 条），正文 3 处引用句同步改写为单号多主张句式（rationale L21、content L57、scheme L33）；items 2/3/6/7/8/9 记录评估结论不动作。

## 创新增量核查（无新问题）

§2.5 三条创新与 §三.6 三条特色的增量主张（κ+后验双判据的可辨识性优先范式、差分协议受控化、对照体系前置）在 KB 检索口径（2026-08，scheme L139）内成立，且与 r1 复核"新引入问题：无"一致；本轮未发现削弱增量成立性的新文本。
