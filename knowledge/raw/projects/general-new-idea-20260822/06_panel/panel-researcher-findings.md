# 评审团 findings——researcher 视角（科学内容）

评审员：engine 亲审（researcher 角色）｜ 课题：general-new-idea-20260822 ｜ 时间：2026-10-05（第二轮）

核查方式：通读 5 章节文本；对第一轮遗留靶子逐条在 knowledge/ 全库（含 raw/pdfs/_text_cache 全文缓存）重新取证；关键文献断言按 arxiv_id/DOI 定位专页与全文核对。不下"伪造"结论，核实不了标"待核"。

## R# r1 遗留靶子处置

### R13 [遗留 critical → 已核闭合（无需改动）] Osumi[13] "沿 Γ–K 约 0.3 eV 自旋轨道能隙"连续两轮未闭合

- 位置：rationale.md L29（"并给出沿 Γ–K 高对称线约 0.3 eV 的自旋轨道能隙"）、content.md L19、scheme.md L19/L79/L99、full_review.md L25/L36。
- 本轮取证：**原文全文已在库**——arXiv:2308.10117v2（即 PRB 109, 115102 的预印本，作者 Osumi T, Souma S, Aoyama T, Yamauchi K, Honma A, Nakayama K, Takahashi T, Ohgushi K, Sato T，与 [13] 条目逐一相符），全文缓存 `knowledge/raw/pdfs/_text_cache/2308_10117.txt`。摘要逐字："The magnitude of the splitting reaches 0.8 eV at non-high-symmetry momentum points, which is much larger than **the spin-orbit gap of ∼0.3 eV along the ΓK high-symmetry cut**"；结论节同义重申（"a small (∼0.3 eV) band splitting along the high-symmetry ΓK cut, suggestive of an additional contribution from the SOC"）；附录 C 给出单构型上限 0.25 eV（ΓK2 切）并以"∼0.3 eV along the ΓK cut"为实验判定值。样品为块体单晶（附录 A：Laue 背反射标定），T_N = 307 K。
- 判定：正文"沿 Γ–K 高对称线约 0.3 eV 的自旋轨道能隙""非高对称动量点达 0.8 eV""块体单晶""T_N≈310 K"四项表述与原文逐字相符，**归因与数值全部成立，无需任何改动**。scheme L99"实验在该方向观测到的约 0.3 eV 能隙即 SOC 诱导能隙"采原文摘要口径（结论节的 "suggestive of" 留有余地，摘要径称 spin-orbit gap），可接受。scheme L99"非相对论劈裂为零（节点面内）→ 该能隙即 SOC 能隙"的推理链另获 [19] 综述全文（2602_13590.txt L713-716）独立佐证："weak altermagnetic LKSD with a ∼100 meV splitting along the Γ–K path within a nodal plane"（Krempaský 数据，节点面内 SOC 诱导量级 image 一致）。
- 遗留状态：**两轮 critical 遗留就此闭合**。

### R14 [遗留 low → 已修] r1 复核观察项 1：差分 SNR 舍入张力（0.5×√30≈2.74 vs "可达 SNR≥3:1"）

- 位置：scheme.md L45："单个谱对（正负磁场各一幅）的差分信噪比约 0.5。按平方根律累计约 30 个差分单元……可达 SNR≥3:1。"
- 依据（原文上下文自洽，无需外部来源）：同句给出 6×10³ 光子/谱、泊松涨落 1.3%、差分目标 1%。单谱对差分噪声 = √2×1.3%≈1.83%，信噪比 = 1%/1.83% ≈ **0.55**；0.55×√30 ≈ 3.01，恰闭合"可达 3:1"。0.5 为 r1 改写时的过度舍入。
- 修改建议（已执行）：0.5 → 0.55。顺带使 10³ 档（单谱对 1.7，需 3 单元）与 10⁴ 档（单谱对 5.5，需 1 单元）的"1–6 个单元"阶梯同步精确闭合。

### R16 [遗留 R10 → 已核闭合（无需改动）] Ghimire[1] 3.25 μm 驱动波长

- 位置：scheme.md L57"ZnO（Ghimire 等[1]）在 3.25 μm 附近驱动"。
- 本轮取证：KB 页 `wiki/papers/2025-2505_19894-laser-dressed-partial-density-of-states.md` 两处明载"首个体固体 HHG 就是在纤锌矿 ZnO 中、3.25 µm 驱动下观测到的""（3.25 µm、>1 TW/cm² 驱动）"。**有据，维持原文。**

### R17 [遗留 R10 → 部分闭合] Amin[25] 30 nm α-MnTe(0001)/InP(111)A 薄膜参数

- 位置：scheme.md L75"30 nm α-MnTe(0001) 薄膜（InP(111)A 衬底）上成像了从 100 nm 涡旋到 10 μm 图案化单畴态的畴结构"。
- 本轮取证：KB 专页 `2024-s41586-024-08234-x-nanoscale-imaging-and-control-of-altermagnetism-in-mnte.md` 证实 XMCD/XMLD-PEEM、MnTe 纳米-微米尺度涡旋/畴壁/单畴实空间成像与可控操控（定性部分成立）；"InP(111)A 衬底"作为 MnTe 薄膜生长衬底在 Dal Din 全文缓存（`2401_09187.txt` L123/L340 "single crystalline MnTe films were grown on InP (111) A substrates"）有据。
- 残留待核："30 nm"厚度与"100 nm–10 μm"畴尺寸区间两个数值 KB（含全文缓存）无记载 → **数值维持原文保留，标待核**（Amin 论文自身无 arXiv 全文在库）。

### R18 [遗留 R10 → 待核维持] Liu[21] 哑铃形/四叶草形细节

- 位置：rationale.md L47。
- 本轮取证：KB 无该文（PRB 112, L081105）专页与全文；grep dumbbell/clover 仅命中无关语境（CrSb 费米面哑铃、原子 p0 轨道哑铃）。**按"核实不了不改写"纪律原文保留。**

### R19 [遗留 R10 → 待核维持] rationale L75 "HHG 光谱学在电荷密度波体系中已展示相变敏感性"（无锚）

- 本轮取证：KB 最接近的证据为 `2404_14411.txt`（Dziurawiec 等，"High Harmonic Tracking of Ultrafast Electron Dynamics across the Mott to Charge Density Wave Phase Transition"）——**模型计算**（扩展 Hubbard 模型，非实验），不足以支撑"已展示"的实验口径；未发现实验性 CDW-HHG 相变敏感性文献在库。
- 处置：不凭记忆补锚、不改写；文献专轮可裁决是否改述为"理论与实验均有展示"并补锚。

## N# 新发现问题

### N1 [high → 待核] arXiv:2406.02238 与本课题创新缺口声明的潜在重叠

- 位置：rationale.md L13（"尚未建立从 HHG 频谱特征到磁结构参数的定量映射关系"）、rationale.md L47（"该方向的定量研究目前仅有 Liu 等人[21]……实验层面对交变磁体各向异性 HHG 的测量仍属空白"）、scheme.md L115（"既有的交变磁 HHG 理论框架尚未在 g 波体系上完成定量对接"）。
- 证据：KB 页 `2024-2406_02238-mnte-hhg-altermagnet-fingerprint-precision-classification.md`（deepxiv 推送 score 0.85，2026-09-30 入库，**status: unseen，正文未读、无全文缓存**），标题"MnTe 中高次谐波对交替磁体对称性的探测精度分类"。作者字段仅记"multiple"，**经查非已引的 [16] Werner（2407.07752，有独立专页）**。若该文确为 MnTe（g 波体系）HHG 对称性指纹+精度分类工作，则与上述三处缺口声明直接相关。
- 处置：KB 记录仅元数据级，不得据标题改写正文；三处声明均带"检索截至 2026 年 8 月"限定、当时陈述为真。**标待核，建议文献专轮最优先读取该文全文**并对照三处缺口声明决定是否补引/限定。

### N2 [medium → 已修] scheme L49 顺磁相数据点归属错置（算术不成立）

- 位置：scheme.md L49："300–320 K 跨 T_N ≈ 310 K 加密至 5 K 步长（5 点）**以确保不少于 5 个顺磁相数据点**。320–340 K 以 5 K 步长延伸（4 点）。"
- 问题：T_N≈310 K 时 300–320 K 段内顺磁相点仅 315、320 两点，该段不可能"确保 ≥5 个顺磁相点"；≥5 的要求实际由 315–340 K 共 6 点满足（315,320 + 325,330,335,340）。content.md L51（目标 2"顺磁相获取不少于 5 个数据点"）与 scheme.md L137 依赖此设计，归属错置构成设计-指标链条上的口径瑕疵。
- 修改建议（已执行）：把"确保 ≥5 顺磁相点"改挂到两段合计口径："……（5 点）刻画相变邻域。320–340 K 以 5 K 步长延伸（4 点），两段合计提供 6 个顺磁相数据点（315–340 K），满足不少于 5 个的设计要求。"总点数 15+5+4=24 不变。

### N3 [medium → 已修] rationale L25 Reimers[10] 句材料名缺失 + "自旋分辨"超出 KB 证据

- 位置：rationale.md L25："Reimers 等人[10]于 2024 年以软 X 射线**自旋** ARPES 在 **(100)** 薄膜上直接观测到 g 波带劈裂**（自旋分辨）**，与同年体相样品上以高分辨率 ARPES 测量给出的大带劈裂（非自旋分辨）相互印证。"
- 证据：KB 专页（s41467-024-46476-5）明确"Reimers 与 Šmejkal 等人在 **CrSb(100) 薄膜**上用**软 X 射线 ARPES**"，未载自旋分辨；[19] 综述全文（2602_13590.txt L809-812）描述其方法为"Using both P- and S-polarized light, they verified the parity selection rules of the split bands"——**偏振依赖测量，非自旋分辨探测**；该文标题亦为"band splitting"（自旋积分可观测）。两处 KB 证据一致指向自旋积分测量。
- 问题：正文断言超出可证口径；且句子漏掉材料名，"该结论"（上句主语为 MnTe Krempaský[7]+CrSb Long[8]混述）指代悬置。
- 修改建议（已执行）：改按 KB 可证口径——"以软 X 射线 ARPES 在 CrSb(100) 薄膜上直接观测到 g 波带劈裂，并经 P/S 偏振依赖测量验证劈裂带的宇称选择规则，与同年体相单晶高分辨率 ARPES 给出的大带劈裂相互印证"。印证逻辑（薄膜/体相两条独立路径）不受影响；若文献专轮证实 [10] 确含自旋分辨探测可回滚。

### N4 [low → 不适用] scheme L33 单脉冲能量 0.5–5 μJ 与 A_eff 口径

- 按直径读法（D=50–100 μm，w=25–50 μm）复算 0.15–2.4 μJ；按 1/e² 半径读法（w=50–100 μm）复算 0.6–9.4 μJ。原文 0.5–5 μJ 不精确落在任一口径内，但处于两读法包络内，且下游结论（×1 kHz → 平均功率毫瓦量级）在任一读法下均稳健，无后续判据依赖此区间。
- 处置：不动。预研阶段以实测光斑口径定死定义后自然收敛。

### N5 [low → 不适用] scheme L55 "InGaAs/InSb 响应截止约 5.5 μm"

- InGaAs 长波截止约 2.6 μm，5.5 μm 由 InSb 决定；作为"探测链联合响应截止约 5.5 μm"的链级口径成立（InSb 为链中最长波元件）。是否删 InGaAs 取决于实际装置配置，KB 不可核。处置：不动，留预研确认。

## 核查通过清单（抽查，未立案）

- [16] Werner 圆二色规则（"纯交变磁体无圆二色性、交变磁与 SOC 共存时有圆二色性"，rationale L39/scheme L39）：KB 专页 2024-2407_07752 证实（"无磁场时 altermagnet+SOC 的非线性横向电流和圆二色"）。
- [8] Long CrSb 序参量"实球谐函数 Y₄⁻³"（rationale L23）：KB 页 2026-2503_10797（[29] 原子交变磁性）证实"CrSb……ḡ₃ ≡ Y₄,₋₃ 谐波分量，g 波节点结构与动量空间自旋劈裂节点结构一致"。
- [3] Liu MoS₂ 0.30 eV / 至 13 阶（scheme L7 复现窗口）：KB 页 1802.10120 证实 mid-IR ~0.3 eV/~4 μm 驱动、清晰观测至 H13（3.9 eV）；6–13 阶为其子窗，属设计选择。
- [13] Osumi 0.8 eV 非高对称点、光子能量可调 ARPES+第一性原理（rationale L29）：全文摘要逐字证实。
- scheme L23 计算量账（28+6+30+数十≈百次；MCMC 4×10⁴ CPU·h）与 §8 三处闭合：r1 R2 结论未回归。
- 自洽数值抽算全部通过：dE/dλ≈0.41 eV/μm（三光子 1.23 eV/3 μm）、0.1 eV 漂移↔±0.25 μm 调谐、H_SF=√(2H_E·H_A)≈14 T>±7 T、5 μm↔0.25 eV、0.30 eV↔4.1 μm、10² counts/s×60 s=6×10³、原子 SOC/劈裂比 0.5–1.7、带内比 0.375–1.0。
- rationale L31"g 波劈裂 d 波四重翻转/g 波更高阶节点面"、content L27 节点面方位凹陷与阶次间隔论证：与四组节点面构型自洽，无发现。
