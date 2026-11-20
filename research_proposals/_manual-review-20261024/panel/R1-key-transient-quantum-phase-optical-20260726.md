# R1 科学性评审 — key-transient-quantum-phase-optical-20260726（r5）

评审人：R1（领域资深 PI，强场超快光学/凝聚态）｜评审日期：2026-10-29｜评审对象：`04_proposal/sections/` 四模块（rationale / content / scheme / references / full_review，r5 版）
上游输入：`_manual-review-20261016/panel/R1-key-transient-quantum-phase-optical-20260726.md`（上轮 8 条，monitor 0.86→本轮 monitor 0.85）、`optimizing/.../05_review/manual-revision-20261016.md`（R1 8 条：采纳 3 / 改后采纳 3 / 无需改动 1）、`04_proposal/params.json`（v7.2.19 跨章口径表，7 条）

专项任务：逐条核对 params.json 7 条口径条目 stale_patterns 命中；对上轮 R1-01～R1-08 逐条复核「已修 / 回退」；重点复查强度换算链（V/Å ↔ W/cm²，I=½cε₀E₀²）全文一致性（上轮全链修复项，查回退）、χ⁽³⁾ 归属、量子相变判据链；引用编号对账；限量联网反查 6 组判据链量化锚。

---

## 一、专项核查（口径自洽）

### 1.1 params.json 七条口径条目逐条判定（程序化正则匹配 rationale/content/scheme/full_review）

| 口径条目 | stale_patterns 数 | 命中 | 判定 |
|---|---|---|---|
| peak_intensity_field_conversion | 3 | 0 | **保持 ✓**（rationale L5–L9：E₀ 0.1–0.5 V/Å ↔ I≈10¹¹–3×10¹² W/cm²，换算式显式；Bi₂Se₃ 例 0.5 V/Å ↔ 3.3×10¹² W/cm²、ℏΩ_R≈2.5 eV、ℏΩ_R/E_g≈8 标注极端对照点。全链复算见 §四锚 6） |
| berry_curvature_integral_unit | 4 | 0 | **保持 ✓**（§0 表 Berry 行"无量纲"、18.24→26.86 无单位口径；现存 Å⁻² 仅 2 处均为 BZ 面积合法量纲） |
| ref_zhao_18_vs_21_attribution | 4 | 0 | **保持 ✓**（WS₂ 语境 [21]×3：rationale L62/L117 + Zhao Z. 命名；MgO 语境 [18]×3：rationale L105/L131 + scheme L187 Zhao C. 命名；正文无内嵌刊名卷页） |
| chi3_graphene_attribution_ata_baseline | 3 | 0 | **保持 ✓**（rationale L64 χ⁽³⁾~10⁻⁹ m²/V² 明标石墨烯 Dirac 载流子对比值、"场增强两个数量级"归谐振环；content L59 ATA 起点改挂团队预研 SNR≈105；SHG 3.5×10⁻⁵ 全文零命中） |
| deltac_threshold_sigma_framing | 3 | 0 | **保持 ✓**（rationale L228–229 覆盖概率口径：0.20 位于 1.29σ–1.74σ、Φ≈90–96%；停止档 3.2σ–4.3σ 复算吻合） |
| inst_wipm_full_name | 1 | 0 | **保持 ✓**（rationale L173 "中国科学院武汉物理与数学研究所"） |
| refs_doi_status_5_23_34 | 3 | 0 | **保持 ✓**（[5][23][34] 刊版条目在位，references L9/L27/L38 与 Crossref 证录一致，未被降级为预印本） |

**小结：7/7 口径条目保持，无命中、无回退。** 上轮 R1-01 的强度换算链修复（含 M1 对上轮 R1 换算锚 10² 偏差的纠正）经本轮独立复算完全巩固。

### 1.2 上轮 R1-01～R1-08 逐条复核

| 编号 | 上轮 severity | 当前状态 | 复核依据 |
|---|---|---|---|
| R1-01（强度↔场强换算断裂） | major | **已修 ✓** | rationale L5–L9 以场强为锚全链重写，I=½cε₀E₀² 复算通过（0.1 V/Å→1.3×10¹¹、0.5→3.3×10¹² W/cm²） |
| R1-02（nm⁻²/Å⁻² 百倍口径差） | major | **已修 ✓** | §0 表 Berry 行改无量纲；18.24→26.86（增 47%，复算 26.86/18.24=1.473 ✓）无单位；BZ 面积 Bi₂Se₃≈2.7 Å⁻² 复算吻合（a=4.14 Å 六角 → 2.66 Å⁻²） |
| R1-03（WS₂ 错标 [18]） | major | **已修 ✓** | 与 R3-01 合并执行到位，三处 WS₂→[21] 三处 MgO→[18]，见 1.1 第三行 |
| R1-04（χ⁽³⁾ 归属失真+ATA 起点借用） | major | **已修 ✓** | rationale L64 归属改标 + content §2.3 L59 起点改挂预研数据链 |
| R1-05（18.24/26.86 待溯源） | minor | **已修 ✓** | rationale L117 标注"取自原文正文，公开摘要可证实定性结论"，付费墙边界诚实声明 |
| R1-06（示例越档 ℏΩ_R/E_g≈8） | minor | **已修 ✓** | rationale L9 "属带隙完全闭合的极端对照点，不在写入档（1–3）之内"，与 scheme §2.1(b) 三档对齐 |
| R1-07（单侧功效混用） | minor | **已修 ✓** | 覆盖概率口径在位（1.1 第五行） |
| R1-08（文献层可信，info） | info | **维持 ✓** | SNR≈105±18"不援引 DOI"诚实处理保留（rationale L279） |

**小结：8/8 已修且零回退。** 本轮意见全部为新发现或增强级建议，不重复已修条目。

### 1.3 编号与死条目对账

- references 列出 [1]–[41] 连续无缺号；程序化对账（含范围/列表式引用展开）：**零死条目、零超界、零一号两用、零断链**。
- 表头声明"预印本 12 条（[4][11][12][18][22][24][26][29][31][36][37][41]）+ 刊版 29 条"与实际计数一致（12+29=41）。

---

## 二、总评分

**总评分：0.87**（rigor 定档：五项全过 → 0.90+ 锚内取 0.90；已越通道 B 验收线 0.82，距 0.90 免检线差 0.03 为总评分口径）

| 维度 | innovation | feasibility | rigor | expression | completeness | 总评 |
|---|---|---|---|---|---|---|
| 分数 | 0.88 | 0.84 | 0.90 | 0.85 | 0.86 | **0.87** |

### 五项核查明细（rigor 定档依据）

| 核查项 | 判定 | 依据 |
|---|---|---|
| ① 数值链一致 | ✓ | 全链复算通过：强度换算链（锚 6）、σ 合成链 √(0.05²+0.02²+0.01²)=0.055→0.155/0.115、SNR 1/0.155=6.45/1/0.115=8.70、覆盖概率 Φ(1.29)=0.90/Φ(1.74)=0.96、停止档 0.50/σ=3.2–4.3σ、抖动 √(80²+50²)=94.3 / √(106²+50²)=117.2 / 75 mrad→79.6 as、ATA √(200²+50²)=206、波长比 1500/62=24.2 与 8000/20.7=386、样本预算 25 点×10⁴=2.5×10⁵ 发→4.2–5.6 min、算力 150×10³=1.5×10⁵ 与 4×10⁴×1 CPU·h、ℏω/E_g 落点 2.76/2.07/1.03/0.52/0.10–0.19/0.77–1.55/1.55–3.1 逐项复算吻合 |
| ② 指标定义可操作 | ✓ | ΔC 三档+σ 框架、SNR 失效边界（<6.5 失效/>8.7 扩展）、T_L/4 跨区判据、抖动 95% 时段覆盖率、17+3 窗口、Y1–Y5 逐年核验锚（初检 0.10/复核 0.05、窗口离散度 50 as）均可检验 |
| ③ 文献支撑真实 | ✓ | 本轮反查 6 组锚全部属实（§四）；上轮 [9]/[18]/[21] 归属修复巩固；三个无法外部核验的数值（18.24/26.86 付费墙、SNR 105±18 未发表预研、[24] 的 15–30 倍预印本外推）均已在正文以诚实边界标注，无过度声称 |
| ④ 逻辑闭环 | ✓ | 可定义性→写入→读出→反演→残差回传链条完整；每环节配失效边界与 D1–D6 双路径；与 Uzan/Faeyrman/Lesko 的边界划分（相位层→不变量层、单脉冲→写读协同）经三处交叉声明自洽 |
| ⑤ 模块自洽 | ✓ | full_review 跨章表 24 行与三章逐一核对无出入（E_g 取值、ΔC/SNR/抖动/能区/档位、年度锚）；[32] body 引用、代表体系定义、迭代周期口径贯通 |

**定档理由**：五项全过 → rigor 取 0.90 档（0.90+ 锚下沿）。剩余 4 条意见全部为 low/info 级增强项（R1-01～R1-04），无一条触及机理层或判据链。总分 0.87 为五维平均，其中 feasibility 扣分点为 2 μm 端 117 as 超指标须第 3 年压缩（已声明应急三级路径）与 Co₃Sn₂S₂ 类比标度可能退出（已声明退出条件），均属已对冲的声明性风险。

**分数带语境**：0.87 > 0.82（通道 B 验收线），< 0.90（免检线）。上轮 0.78 → 本轮 0.87 的抬升全部由可复核的修复支撑（8/8 修复零回退 + 本轮 6 组锚反查通过 + 数值链全复算通过），非口径放宽。

---

## 三、意见清单

[R1-01|low] 立项依据｜§2.3 L139｜[24] 段未注明实测材料为超纯硅，跨材料外推边界未显式（③）｜"Mokhtari 等[24]于 2026 年实验测量 77–500 K 温区 HHG 产额随温度的明显变化（随降温上升）"｜改为："Mokhtari 等[24]于 2026 年在超纯硅（反射构型、77–500 K 温控）中实验测量 HHG 产额随温度的明显变化（随降温上升）；该结论向拓扑/关联体系的跨材料外推由其一维原子链模型承担。"

[R1-02|low] 研究方案｜§2.1(a) L61｜高频区两端点合并表述易误读波段对应（①表述）｜"高频区（$\hbar\omega/E_g \approx 2$–2.76）对应 1.5 μm 驱动（$\hbar\omega \approx$ 0.83 eV，Bi₂Se₃ 等窄带隙拓扑材料）"｜改为："高频区（$\hbar\omega/E_g \approx 2.07$–2.76，分别对应 2 μm 与 1.5 μm 驱动；$\hbar\omega \approx$ 0.62–0.83 eV，Bi₂Se₃ 等窄带隙拓扑材料）。"

[R1-03|info] 核验档案｜references L42｜[38] ±81 as 与 PID 70 Hz 两个具体数值未能在公开可抓取文本直证（题录/ELI ALPS HR 束线/非共线 Mach–Zehnder/长时数天稳定均核实）｜"Csizmadia 等[38]于 2025 年在 ELI-ALPS HR 束线上实现 ±81 as 数天长期稳定度……PID 反馈速率 70 Hz"｜无需改正文；建议向核验档案补开放仓储 PDF（real.mtak.hu）结果节解析截图，坐实 ±81 as/70 Hz 两数值。

[R1-04|low] 口径表（非正文）｜04_proposal/params.json 条目 1 note｜note 中拓扑写入档 E₀↔W/cm² 换算较 I=½cε₀E₀² 高 10 倍（canonical 正确、正文不含该数值，防 writer 按 note 引数）（①）｜"拓扑写入档 E₀≈0.06–0.18 V/Å ↔ 5×10¹¹–4×10¹² W/cm²"｜note 内改为"拓扑写入档 E₀≈0.06–0.18 V/Å ↔ 约 4.8×10¹⁰–4.3×10¹¹ W/cm²"（下轮播种时随 canonical 维护一并修正）。

---

## 四、量化锚核实记录

| 锚 | 申请书位置 | 核实结果 | 证据 URL |
|---|---|---|---|
| [24] Mokhtari：77–500 K 温区、随降温上升、一维链模型 | rationale L139、L234 | ✅ 成立。正文："temperature control from 77 K to 500 K via PID-regulated resistive heating"；"harmonic yield increases significantly with decreasing temperature"；一维原子链模型 ✓；材料为超纯硅（正文未标注，→ R1-01）；液氦外推 15–30 倍未在可抓取部分直证（正文截断），该值申请书已标"预印本外推、第 1 年实测重标" | https://arxiv.org/html/2604.07543v1 |
| [41] Kim：ML 力场 1404 原子超胞 5 ns、>200 K SoD 形变-重构相干平移、~350 K 畸变塌缩 | content L23 | ✅ 成立，逐项吻合："1404-atom supercells over 5 ns"；"Above 200 K, SoD clusters translate coherently by transiently dissolving and re-forming"；"Only near 350 K does the SoD distortion itself collapse" | https://arxiv.org/abs/2608.02456 |
| [38] Csizmadia：ELI ALPS HR 束线、非共线 MZ 双干涉仪、PID、数天长稳 | scheme L165/L211/L244 | ✅ 主体成立：APL Photonics 10, 080803（2025-08-20），"HR Gas beamline of ELI ALPS"、Mach–Zehnder XUV–IR、PID 反馈、"long-term (hours to days) acquisition" 全部核实；±81 as 与 70 Hz 数值未直证（→ R1-03） | https://real.mtak.hu/223510/1/080803_1_5.0273558.pdf |
| [17] Lesko：圆偏振产生 FTI + 锁相二次谐波操控、谷极化电流 | rationale L101、scheme L185 | ✅ 成立："focusing circularly polarized femtosecond laser pulses at 1550 nm on monolayer graphene, we generate a Floquet topological insulator (FTI). With a phase-locked second harmonic field, we dynamically control electrons"；"FTI valley-polarized currents" ✓ | https://arxiv.org/html/2407.17917 |
| [11] Zhang TaAs：单色场四类观测量不含外尔锥签名 | rationale L73（反演核心困难论证） | ✅ 成立，逐字吻合："intensity, circular dichroism, ellipticity dependence, and carrier-envelope phase dependence, are not found to carry a signature of the Weyl cones" | https://arxiv.org/abs/2405.16125 |
| 强度换算链（上轮修复项防回退复算） | rationale L5–L9、scheme §2.1(b) | ✅ 成立：I=½cε₀E₀² 下 0.1 V/Å→1.33×10¹¹、0.5 V/Å→3.32×10¹² W/cm²；原子单位锚 51.42 V/Å↔3.51×10¹⁶ W/cm²；ℏΩ_R=5×0.5=2.5 eV、/0.3=8.3≈8；定义保持档 E₀≤0.3E_g/d_cv 公式量纲自洽 | 本地复算（无外部 URL） |
| [30] Neufeld 泛函基准（GGA 最优） | rationale L236、scheme §2.3(b) | ○ 本轮限量内未独立反查；题录（JPCL 15:7254, 2024）与已知一致，上轮无异议，维持"可信、待抽核" | — |
| [13] Uzan-Narovlansky Nature 626:66-71 | rationale L28/L34/L79/L143 | ○ 题录与 2024 年 Nature 工作事实一致，历轮评审无异议，本轮未重查 | — |

---

## 五、结论

**剩余意见性质：增强级微调，无方向性或机理层风险。** 上轮 8 条全部修复且零回退，7/7 口径条目保持，数值链全复算通过，6 组联网锚全部属实。本轮仅余 2 条 low 正文建议（[24] 材料标注、波段端点表述）、1 条 info 核验档案补图、1 条 params.json note 的 10× 滑差提醒（正文不受影响）。

**建议：通过 R1 科学性关。** 总评分 0.87 已过通道 B 验收线（0.82）。若采纳 R1-01/R1-02 两条 low（半小时工作量）并补 R1-03 核验档案，R1 侧无遗留阻塞项；是否进入验收由 M1 汇总 R2/R3 意见后统一裁决。R1-04 提请下轮播种时修正 params note，防止后续 writer 轮次按 note 把 10 倍偏差的 W/cm² 数值写入正文——这是本轮唯一具有前瞻风险的发现。
