# R1 科学性评审 — general-berry-mnps3-rashba-20260816（r2）

评审人：R1（领域资深 PI，凝聚态/强场超快方向）｜评审日期：2026-10-29｜评审对象：`04_proposal/sections/` 四模块（rationale / content / scheme / references / full_review，monitor 0.90 版）
上游输入：`_manual-review-20261016/panel/R1-general-berry-mnps3-rashba-20260816.md`（上轮 9 条，总评 0.77）、`optimizing/.../05_review/manual-revision-20261016.md`（R1 9 条全采纳 + R3 8 条 + R2 42 条）、`04_proposal/params.json`（v7.2.19 口径表，8 条）、R3 本轮交叉信息（预印本著录时效与数值颗粒度，独立复核）

专项任务：逐条核对 `params.json` 8 条口径条目在四章的自洽性（程序化正则匹配）；对上轮 R1-01～R1-09 逐条复核「已修 / 回退」；联网反查 8 个承担判据链的量化锚；重点排查跨章数值口径互斥、群论修复回退、物理硬错。

---

## 一、专项核查（口径自洽）

### 1.1 params.json 八条口径条目逐条判定（stale_patterns 程序化匹配 rationale/content/scheme/full_review/references）

| 口径条目 | stale_patterns 数 | 命中 | 判定 |
|---|---|---|---|
| i-wave 群论根基表述 | 6 | 0 | **保持 ✓**（rationale L17-19 / content L25 / scheme L5 均为 canonical 修正文本：C₃ 容许 l=3k、cos6θ 在列、波型归属由 PT 破缺自旋点群 C₆=C₃⊗C₂ 决定） |
| MnPS₃ 体相结构表述 | 1 | 0 | **保持 ✓**（rationale L19"单斜 C2/m 堆叠，无晶体学 C₃ 轴；单层理想蜂窝子格近似下母格子具三重轴"） |
| τ₂ 临界指数口径 | 1 | 0 | **保持 ✓**（rationale L37 无普适类标签，m = 0.44 ± 0.18 裸引） |
| [18] 势垒数据出处表述 | 1 | 0 | **保持 ✓**（全文唯一"实测值"命中为 full_review L21 否定声明"非实验实测值"；势垒三值挂 [17] 并标注静态 DFT 普查） |
| 延迟扫描总时序预算 | 0 | — | **保持 ✓**（scheme L75 预算段在位：16.7 min/点、4950+100 点、59 天不可行、三步对策，算术复核闭合） |
| 偏振通道泊松不确定度 | 2 | 0 | **保持 ✓**（content L33 "N ≈ 10³ 对应约 3%（1/√N）"、scheme L67 "N ≈ 5×10⁴ 得约 0.4%"，双口径关系已声明） |
| [37] 体系归属表述 | 1 | 0 | **保持 ✓**（rationale L43"层状反铁磁体（FePS₃ 家族）"家族降级表述；scheme L95 备份材料句按上轮裁决保留 FePS₃ 设计） |
| 弱场产额外部参照 | 1 | 0 | **保持 ✓**（scheme L67"量级假设取值，未经本方案装置实测标定"降级在位） |

**小结：8/8 口径条目保持，stale_patterns 全部零命中，无回退。** 但口径表自身存在三条注记编号漂移（见 R1-02），属登记表维护缺陷而非正文错误。

### 1.2 上轮 R1-01～R1-09 逐条复核

| 编号 | 上轮 severity | 当前状态 | 复核依据 |
|---|---|---|---|
| R1-01（引用错配 3 组） | critical | **已修 ✓** | Mavani=[19]（rationale L15）、Misawa g-wave=[34]（L27）、Ogawa 154 SPG 分类=[37]（L9、scheme L5）全部挂对，43→42 缩编后编号再未错挂 |
| R1-02（群论硬错 l=3 上限） | critical | **已修 ✓** | 三章均为 l=3k 修正文本 + C₆=C₃⊗C₂ 自旋点群归属 + "假设 i-wave 条件下"标注（rationale L19、content L23 标题行、scheme L5） |
| R1-03（体相 C2/m） | high | **已修 ✓** | rationale L19 限定句在位，堆叠修正由第一阶段 DFT+自旋空间群计算吸收 |
| R1-04（挂靠声明） | high | **已修 ✓** | references L7 按 42 条实测改写（9+11+22），抽查 [9][20][24][26][32][33][36] 挂靠全部属实 |
| R1-05（时序预算） | high | **已修 ✓** | scheme L75 预算段：4950 点×16.7 min+100 点≈59 天、抽稀 1.1×10³ 点、100 kHz 档 10 s/点，算术闭合 |
| R1-06（泊松公式） | medium | **已修 ✓** | "3%/√N""N_n"零命中 |
| R1-07（普适类标签） | medium | **已修 ✓** | "3D Heisenberg"零命中 |
| R1-08（弱场参照） | medium | **已修 ✓** | 降级为量级假设 + 未实测标定声明 |
| R1-09（[7] 体系归属） | low | **已修 ✓** | rationale L15/content L13 泛化为"双层范德华体系"，不点名 h-BN，与 R3 消解一致 |

**小结：9/9 已修且无回退，上轮 critical（群论 + 引用错配）双修复在两轮重排后仍保持。** 本轮意见全部为新发现或上轮遗留项的续期跟踪。

### 1.3 编号与死条目对账

- references 列出 [1]–[42]，连续无缺号；正文引用上界 42，无超界。
- 42/42 全部有正文挂靠，无死条目；跨章共用声明（[5][7][12][17][20][24][26][36][37] 三章、11 条两章、22 条单章）与实测一致。
- 无一号两用（arXiv+DOI 双版标注条目为单条目溯源格式）。

---

## 二、总评分

**总评分：0.84**（rigor 定档：五项过四 → 0.82–0.89 档中段；已过通道 B 验收线 0.82，距 0.90 免检线尚差 0.06）

| 维度 | innovation | feasibility | rigor | expression | completeness | 总评 |
|---|---|---|---|---|---|---|
| 分数 | 0.85 | 0.80 | 0.85 | 0.82 | 0.86 | **0.84** |

### 五项核查明细（rigor 定档依据）

| 核查项 | 判定 | 依据 |
|---|---|---|
| ① 数值链一致 | ✓ | THz 光子-势垒多光子匹配（16.4/25.5/39.9 meV → 2–4/3–6/5–10 光子）✓；80–100 Ry≈1100–1400 eV、0.01–0.05 a.u.≈0.24–1.2 as ✓；d′=2.09→93%、1.81→90% 双高斯换算 ✓；D_sep 高斯极限 1−√(2τ₁/τ₂)、达阈 τ₂≥50τ₁、最不利组合 111/50≈2.2 倍裕量 ✓；产额链 10⁸→÷1 kHz=10⁵/脉冲→×10⁻⁶=10⁻¹→×10⁶ 积分=10⁵→分光 5×10⁴→1/√N=0.4% ✓；59 天预算与抽稀对策闭合 ✓；(F/F₀)^2n 压低 10⁻⁶ 与六阶光子能量 2.5–5 eV 换算 ✓；τ₂/τ₁=111–4000 与实测区间闭合 ✓。R1-01 延迟轴轴型-步长失配属表述层（预算按 100 点计保守正确），带注通过 |
| ② 指标定义可操作 | ✓ | 五指纹量（A_helicity/S_ellipticity/θ/过零点/阶次周期性）定义与反演角色分工、d′ 与 √J 主从关系、D_sep 双套表述用途分离、γ = Δ_gap²/(4ħ\|dε/du\|·v) 无量纲化与适用条件逐项检验、切换概率 Wilson 区间、三通道权重 0.7 判据均有操作定义与可证伪条件 |
| ③ 文献支撑真实 | ✗ | 核验 8 锚中 6 个精确成立、0 个证伪，但 2 处承担论证支点的数值未获原文可核验：[18] AA′ 堆叠 60–80 meV 劈裂（content L13"层移直接改写劈裂结构"的量级锚，摘要与可达正文截断段未见）与 [38] Basnet 饱和场 8 T/0.24 μB/f.u.（rationale L29，上轮遗留 L-5 续期）；另 [27] m=0.44±0.18 未在摘要出现；[26][39] 著录状态两处待定稿前复核。以 medium 意见跟踪，不计虚指但未达"全部量化锚可核验"标准 |
| ④ 逻辑闭环 | ✓ | 群论前提（l=3k + 自旋点群判定 + 假设波型标注）自洽；驱动-读出-分离三重瓶颈→三内容→三目标→三可证伪条件的链条闭合；Floquet 5 倍增强的可行性已作防御性降级表述；i-wave 判定前 d/g 备选通道（六光子→双/四光子迁移）有程序化出口 |
| ⑤ 模块自洽 | ✓ | full_review 跨章口径表 34 行与四章实测一致；泊松双口径（10³ 基线/5×10⁴ 预算）关系已显式声明；上轮修复无跨章失配。R1-02 所指 params.json 注记编号漂移属登记表与正文的编号映射缺陷（3 处），非正文模块间失配 |

**过 4 项（①②④⑤）→ rigor 落 0.82–0.89 档，取 0.85。** 理由：①②④⑤四项基础扎实且上轮 9 条全部保持；③未过的原因不是文献虚指（零证伪），而是两处数值锚停留在"未证实"状态——这类问题可用一次原文核对（1 天内）闭环，但闭环前不满足"亲审通过"的 0.90+ 锚。

**分数带语境**：0.84 > 0.82（通道 B 验收线），课题具备进入验收准备的基础；完成 R1-03/R1-04 两处数值锚核对与 R1-05 著录更新后，③可补齐至"过五"，rigor 有望 0.88–0.90，冲击免检线。

---

## 三、意见清单

[R1-01|medium] 研究方案｜§3.4 L73（并涉 L75、L103）｜延迟轴"对数轴+固定步长 10 fs"轴型失配：0.1–10 ps 按 10 fs 线性步长为 990 点，与 L75 预算"对数轴约 100 点"矛盾；L103"步进 10 fs，对数延迟轴最小分辨率"同病（①②）｜"对数延迟轴覆盖 0.1–10 ps，步长 10 fs，解析电子层的 fs-ps 衰减"｜改为："短延迟段覆盖 0.1–10 ps，按每量级 50 点对数采样（最小采样间隔约 5 fs，位于 0.1 ps 端；10 ps 端约 0.47 ps），共约 100 点，解析电子层的 fs-ps 衰减；若需亚 10 fs 均匀步进，仅在该段 0.1–1 ps 子区间执行（90 点），与 §3.4 时序预算的'对数轴约 100 点'口径一致。"（L103"步进 10 fs"同步改为"最小采样间隔约 5 fs"。）

[R1-02|medium] 口径登记｜04_proposal/params.json｜口径表三条注记的文献编号未随 43→42 缩编重排同步：canonical/note 中 "[18] Sheng 势垒"（现 [18] 实为 González，Sheng=[17]）、"按 [29] 原文"的 Sahu τ₂（现 [27]）、"[37] Li 三波混频"（现 [32]）；按 canonical 编号指引执行会把正确挂靠改错（⑤）｜params.json "「[18] 势垒数据出处表述」canonical：[18] Sheng 等势垒量级 16.4–39.9 meV/unitcell…"｜三处编号同步为现行体系（Sheng=[17]、Sahu=[27]、Li=[32]），并加一条通用 note："编号重排后本表编号须与 references.md 现行编号对账后方可执行。"

[R1-03|medium] 研究内容｜§2.2 L13｜[18] González "AA′ 堆叠给出约 60–80 meV 的动量依赖自旋劈裂"未获原文可核验：摘要与本次抓取的正文段（III.1–III.4）均未见该区间，值域是否对应 AA′ 系列的具体构型待核；该值承担"横向位移直接改写劈裂结构"的量级论证（③）｜"AA' 堆叠给出约 60–80 meV 的动量依赖自旋劈裂 [18]"｜二择一：（a）对照 [18] 正文 III.6 节（Stacking-Dependent Band Splitting）与图 4/5 核实后锚定为"AA′ 堆叠系列中 XX 构型的最大劈裂约 XX meV"；（b）暂降为"AA′ 堆叠系列多个构型的动量依赖自旋劈裂达数十 meV 量级 [18]，具体值以原文图 4/5 为准"。

[R1-04|medium] 立项依据｜§1.2 L29｜[38] Basnet "饱和场约 8 T、磁矩约 0.24 μB/f.u."两数值未见于摘要级核验（本次已核：9% Cr 取代 + 场致自旋极化成立，URL 见第四节），上轮遗留 L-5 续期（③）｜"9% Cr 取代即在 NiPS₃ 中诱导出场致自旋极化，饱和场约 8 T、磁矩约 0.24 μB/f.u."｜对照 PRB 109, 184405 正文图表核实后保留精确数值；定稿前未核到则降为"9% Cr 取代即在 NiPS₃ 中诱导出场致自旋极化（饱和场与磁矩量级见 [38] 正文图表）"。

[R1-05|medium] 参考文献｜references L59（[26]）、L85（[39]）｜R3 交叉信息称 [26] 已正式发表 Nat Commun（2026-10-20）、[39] 已正式发表 npj 2D Mater. Appl.（2026-10-07），本轮复核 arXiv journal-ref 均为空、出版方站点检索未获独立证实，著录状态悬置（③）｜"[26] Ul Haque S R, Cross M J, Rajpurohit S, et al. … arXiv:2510.00605, 2025"｜定稿前在 doi.org/nature.com 复核两条：若已见刊则按 references 自述"以正式版为主、预印本号列于其后"更新著录；若未确认，保持预印本著录不动作现状处理。[24]（arXiv:2604.27342，v1 2026-04-30）仍为预印本，著录正确。

[R1-06|low] 立项依据｜§1.2 L37｜[27] Sahu 临界指数 m = 0.44 ± 0.18 与"幂律发散"表述：双时标主锚（τ₁≈1–9 ps、τ₂≈1–4 ns、T_N 附近临界慢化）已摘要级精确证实，m 值与幂律指数定义未在摘要出现，正文级未核（③）｜"τ₂ 在 Néel 温度附近呈幂律发散，临界指数 m = 0.44 ± 0.18"｜维持现表述（上轮已摘普适类、口径回挂 [27] 原文），定稿前对 PRB 114, 014413 正文核对 m 的定义式后加半句"（τ₂ ∝ |T−T_N|^{−m}，定义按 [27] 原文）"。

---

## 四、量化锚核实记录

| 锚 | 申请书位置 | 核实结果 | 证据 URL |
|---|---|---|---|
| Krempaský [3] MnTe 弱/强两档劈裂（约 100 meV / 约 0.5 eV） | rationale L25 | ✅ **双双成立**（上轮遗留 L-5"100 meV 档未获佐证"结案）。原文结论段："The weak altermagnetic mechanism generates extraordinary relativistic spin-splitting magnitude ~100 meV … The strong altermagnetic mechanism … reaches a remarkable half-eV scale" | https://scispace.com/pdf/altermagnetic-lifting-of-kramers-spin-degeneracy-pbcutdspek.pdf（Nature 626, 517–522） |
| Sahu [27] SOEE τ₁≈1–9 ps、自旋重整 τ₂≈1–4 ns、T_N 附近临界慢化 | rationale L37、content L41、scheme L83 | ✅ **精确成立**。原文摘要："two distinct relaxation timescales: fast (1-9 ps) and slower components (1-4 ns) associated with SOEE coherence and spin reordering … shows critical slowing down around TN"。m=0.44±0.18 未见于摘要（→R1-06） | https://arxiv.org/abs/2509.04900（PRB 114, 014413） |
| Ul Haque [26] 1.7 THz/4.5 THz 相干声子、振荡幅度与平衡 SHG 同量级、仅在反铁磁相 | rationale L43/L81、content L19、scheme L109 | ✅ 内容锚全部成立："giant oscillations in the antiferromagnetic phase, with amplitudes comparable to the equilibrium signal … two vibrational modes at 1.7 THz and 4.5 THz"。峰值场 0.5 MV/cm 未见于摘要（正文级，正文亦引作预印本口径未冲突）；见刊状态未证实（→R1-05） | https://arxiv.org/abs/2510.00605 |
| Wang 等 [24] h-BN 相干单畴刚性滑移 5 ps | content L13、scheme L31、full_review L50 | ✅ **主锚成立**："coherent single-domain rigid sliding, completing within 5 ps, constitutes a physically viable ultrafast switching mechanism"。50 K/300 K→2 ps 为正文级细节，摘要未载；仍预印本（journal-ref 空），著录正确 | https://arxiv.org/abs/2604.27342 |
| González [18] 双层 MnPS₃ AA/AA′ → II 型 AFM/III 型交变磁、层移能量面 | rationale L13、content L13 | ⚠️ **相结构锚成立**（摘要："the bilayer can host either Type II (AFM) or Type III (altermagnetic) phases depending sensitively on stacking and spin alignment"）；**60–80 meV 劈裂区间未核到**（正文抓取截断于 III.4，III.6 未达）→ R1-03 | https://arxiv.org/html/2505.17212v1 |
| Basnet [38] 9% Cr 取代 NiPS₃ 场致自旋极化 | rationale L29 | ⚠️ 主体成立（摘要："field-induced spin polarization in lightly (9%) Cr-substituted NiPS₃"）；饱和场 8 T、0.24 μB/f.u. 两数未见于摘要 → R1-04 | https://arxiv.org/abs/2404.02091（PRB 109, 184405） |
| Wrzos [5] MnPS₃/TMDC S1/S2 堆叠两型 NRSS 分类 | rationale L71 | ✅ 意外佐证成立：原文结论 "(i) In S2 … protected crossings away from Γ, characteristic of altermagnetic order … (ii) S1 … spin splitting throughout the Brillouin zone, including the Γ point"，与申请书 S1/S2 表述逐点对应 | https://arxiv.org/html/2511.22209 |
| Greil [39] WTe₂ 滑移铁电 HHG（TDDFT+层间剪切+偏振分辨） | scheme L17 | ⚠️ 方法学锚成立（摘要：first-principles TDDFT、interlayer shear、polarization-resolved HHG、0.24 THz 剪切模）；所引计算参数（8×8×1 网格、500 eV 截断能、10⁻⁸ eV 判据）属正文方法节细节，本次未核；见刊状态未证实（→R1-05） | https://arxiv.org/abs/2604.25483 |
| Li [32] 层状反铁磁体三波混频 Nat Commun 17, 9507 (2026) | rationale L43/L59、content L19 | ✅ 著录与发表确认（通讯作者主页载 DOI 10.1038/s41467-026-77233-5） | https://physics.nju.edu.cn/szdw/qbmd/20240321/i262086.html |
| MnPS₃ T_N ≈ 78 K 与 4–77 K 工作窗 | rationale L85、scheme L73、content L99 | ✅ 常识值成立（Kim 等 [6] 单层/体相口径约 78 K），1 K 余量声明自洽 | https://doi.org/10.1088/2053-1583/ab27d5（[6] 著录） |

---

## 五、结论

**剩余意见性质：核对型收尾，非结构性缺陷。** 本轮零 critical、零 high：上轮两项 critical（群论硬错、引用错配）经两轮编号重排后修复保持，八条口径无回退，全部承担判据链的换算链（多光子匹配、d′/D_sep/泊松/产额链/59 天预算）复核闭合。六条意见中四条为数值锚的原文核对（R1-03/R1-04/R1-06 + R1-05 著录），一条为表述层轴型修正（R1-01），一条为登记表维护（R1-02），均可定点修复且不动摇方法学主线。

**建议：可进入验收准备，建议先行一轮 1 天量级的定向收尾。** 优先级排序：R1-03（60–80 meV，承担 u-Δ 参数化量级论证）与 R1-04（8 T/0.24 μB）各需一次原文正文核对，核到则保留精确值、核不到则按给出的降级文本替换；R1-02 须在下一轮 writer 修订**之前**完成（否则口径表编号指引会诱发新的错挂）；R1-05 两条著录在定稿前统一复核。完成后五项核查可达"过五"，rigor 0.88–0.90，总评具备冲击免检线（0.90）的条件。

**一个连带提示**：R1-03 若选择降级路线（b），content §2.2 的"AA′ 堆叠约 60–80 meV"是全文唯一给出 MnPS₃ 侧劈裂量级的位置，降级后"滑移→劈裂"环节的量级感将完全依赖平台一的 Sheng 普查与 [20] 声子-劈裂线性关系（50–100 meV@0.05 Å）。二者物理对象不同（前者是非 MnPS₃ 三方体系的势垒、后者是 MnPS₃ 声子振幅驱动），答辩时"MnPS₃ 层移本身能带来多大劈裂"的追问将只能回答"待第一阶段 DFT 计算"。这不是缺陷（申请书已正确把确切数值定位为待计算项），但建议在修订时把该预期管理显式写入 content §2.2 末句，避免现场被动。
