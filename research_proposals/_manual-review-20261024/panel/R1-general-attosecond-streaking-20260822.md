# R1 科学性评审 — general-attosecond-streaking-20260822（r5）

评审人：R1（领域资深 PI，强场超快光学）｜评审日期：2026-10-24｜评审对象：`04_proposal/sections/` 四模块（rationale / content / scheme / references / full_review，r5 版）
上游输入：`_manual-review-20261016/panel/R1-general-attosecond-streaking-20260822.md`（上轮 8 条，monitor 0.78→本轮 monitor 0.79）、`optimizing/.../05_review/manual-revision-20261016.md`（R1 8 条全采纳）、`04_proposal/params.json`（v7.2.19 跨章口径表，4 条）、`memory/nsfc-standards.json`（rigor 五项核查清单 `_checklist_v7217`）

专项任务：逐条核对 `params.json` 4 条口径条目在 rationale / content / scheme / full_review 四章的自洽性；对上轮 R1-01～R1-08 八条逐条复核「已修 / 回退 / 未动」；对全部作为论证支柱的文献数值做原文联网反查（20+ 锚点）；重点排查跨章数值口径互斥、文献锚定不成立、物理硬错。

---

## 一、专项核查（口径自洽）

### 1.1 params.json 四条口径条目逐条判定（程序化正则匹配 rationale/content/scheme/full_review）

| 口径条目 | stale_patterns 数 | 命中 | 判定 |
|---|---|---|---|
| rACE 10% 基准点与 8%–15% 区间口径 | 4 | 0 | **保持 ✓**（三章均已改"设计估值 + rACE 仅作方法学对照，其原文不含该数值"） |
| 甲烷/氮气两靶多通道贡献数值口径 | 4 | 0 | **保持 ✓**（scheme L55 / content L23 / rationale L102 已降级为设计估值并声明"独立原子截面库不含 shake-up 伴线分支比"） |
| 30%↔40% 映射锚点口径 | 3 | 0 | **保持 ✓**（rationale L102 / scheme L135 已改"外推估算，待实测校验"） |
| Ne 水窗段档位口径 | 2 | 0 | **保持 ✓**（scheme L53 / content L41 已改"2s/2p 共同释放 + 5%–8% 过渡带待标定"） |

**小结：4/4 口径条目保持，无偏离、无回退。** 上轮 R1-02 的全链降级执行到位（rationale L55/L102/L111、content L23、scheme L55/L135 六处对齐）。

### 1.2 上轮 R1-01～R1-08 逐条复核

| 编号 | 上轮 severity | 当前状态 | 复核依据 |
|---|---|---|---|
| R1-01（rACE 锚定复辟句） | critical | **已修 ✓** | rationale L55/L102 无"已发表工作报道的"；L55 明确"rACE 公开全文未见该数值表述" |
| R1-02（XCOM 伴线锚全链降级） | critical | **已修 ✓** | scheme L55/L88/L135、content L23/L25、rationale L102/L111 六处降级到"设计估值 + 第一阶段实测与 TDSE 模拟交叉标定" |
| R1-03（时间预算算术） | high | **已修 ✓** | scheme L96"最坏约 4–8 周"，显式假设"仅 3 个低截面能点组落入最坏情形" |
| R1-04（Ne 档位跨章矛盾） | high | **已修 ✓** | content L41 + scheme L53 + full_review L29 三处对齐"2s/2p 共同释放、5%–8% 过渡带并入单通道极限档" |
| R1-05（分档表 rACE 口径） | high | **已修 ✓** | scheme L82 表线性响应档行已改"本项目设计估值；rACE 作交叉验证方法学对照，其原文不含该区间" |
| R1-06（伪量化推导 π/2→1 rad） | medium | **已修 ✓** | 全文零命中"π/2 一通""取整为 1 rad"；scheme L69 改为分波偶极相位差 dη/dE 估算、区间 100–140 eV 落定 |
| R1-07（[46][47] 角标缺失） | medium | **已修 ✓** | rationale L4"Keldysh[46]…Corkum[47]"双角标在位；references L95/L97 条目齐备 |
| R1-08（140 eV 双值） | low | **已修 ✓** | content L33 + scheme L69 + full_review L24 三章对齐"100 eV（800 nm 设计值）/ 140 eV（1850 nm 水窗段）" |

**小结：8/8 已修且无回退。** 本轮意见全部为新发现或上轮未覆盖项，不重复列已修条目。

### 1.3 编号与死条目对账

- references 列出 [1]–[48]，连续无缺号；正文引用上界 48，无超界引用。
- **死条目：[40]（Xia M 等，Complex-gate AO-FROG，arXiv:2608.30516）列于 references L83 但四章正文零引用。** 文献本身真实（2.26 μm 次周期、100–180 eV 氩、约 300 as 孤立脉冲），但作为孤条目存在编号对账缺口。
- 其余 47 条均有正文挂靠，无一号两用、无正文断链。

---

## 二、总评分

**总评分：0.79**（rigor 定档：五项过三 → 0.70–0.79 区间上沿；未达通道 B 验收线 0.82）

| 维度 | innovation | feasibility | rigor | expression | completeness | 总评 |
|---|---|---|---|---|---|---|
| 分数 | 0.84 | 0.74 | 0.77 | 0.82 | 0.80 | **0.79** |

### 五项核查明细（rigor 定档依据）

| 核查项 | 判定 | 依据 |
|---|---|---|
| ① 数值链一致 | ✗ | CH₄ C 1s 伴峰 291.6 eV 无文献支撑且与 Köppe 1996 给出的 shake-up 卫星阈（303/311 eV）冲突（R1-01）；FFAST 被当作光电离截面库使用但实为 X 射线形状因子库（R1-02）；XCOM 能段下限 1 keV 与"284–543 eV 截面核算"不自洽（R1-03）；[40] 死条目（R1-04） |
| ② 指标定义可操作 | ✓ | E_thr_low/high、Wilson 区间、d′/√J、D_sep 高斯极限公式、2%/5%/8%/10%/15%–30%/30%–50% 各档判据均有操作定义与可证伪条件；λ 扫描终止判据（2π 归一 RMS < 5%）明确 |
| ③ 文献支撑真实 | ✗ | FFAST 物理域错配（X 射线 MAC 库被称作光电离截面库）；CH₄ 291.6 eV 伴峰检索无据；He "多通道贡献近似为零"表述过强（R1-05）；Jarecki[42] 数值口径与原文不符（R1-07） |
| ④ 逻辑闭环 | ✓ | 失效机理（多通道 + 偶极相位）→ 三模块 → 双变量图谱 → 备选路径 A/B/C 的链条闭合；上轮 R1-01 复辟句已消除，无循环论证 |
| ⑤ 模块自洽 | ✗ | Jarecki[42] "284–531 eV" vs 原文 "200 to 600 eV"（R1-07）；氦"单通道极限"表述在极紫外与水窗两段自相矛盾且 He 存在 2s2p 关联卫星（R1-05）；Ishii[13] 光子通量"约 10⁶ 光子/秒"在 rationale 与 scheme 两章口径不一且原文无该数值（R1-06） |

**过 3 项 → rigor 落在 0.70–0.79 档**。本轮总评分 0.79 取该档上沿，理由：①②④三项基础扎实、上轮 8 条全部修复无回退、模块自洽与文献真实性仅剩 4 处可定点修复的局部缺陷；但 CH₄ 伴峰这条断的是"0.5 eV 微扰阈值"论证链的唯一量化支撑，FFAST 断的是"独立截面数据库"来源声明，二者均属机理层而非措辞层，故不给 0.80–0.89 档。

**分数带语境**：0.79 < 0.82（通道 B 验收线），距 0.90（免检线 / 评审团深改目标态）尚差 0.11。修复 R1-01～R1-03 三条 critical/high 后，五项可上"过四"档、rigor 落 0.82–0.89，总评分有望达 0.83–0.85，具备进入验收准备的条件。

---

## 三、意见清单

[R1-01|critical] 研究方案｜§2.1 L23｜CH₄ 伴峰 291.6 eV 无文献支撑且与卫星阈实测冲突，该值是 0.5 eV 微扰阈值的唯一定量支撑（①③）｜"该阈值覆盖甲烷 C 1s 主峰（290.7 eV）与伴峰（291.6 eV，能量差约 0.9 eV）等典型水窗多通道场景"｜改写为："通道间能量差不小于 0.5 eV 的适用条件，由 Köppe 等 1996 年实测的 CH₄ C 1s shake-up 卫星阈（303 eV 与 311 eV 附近，位于 C 1s 电离阈 290.7 eV 之上 12–20 eV）与本项目 TDSE 模拟端标定的残离子激发通道共同支撑；伴峰具体能量以第一阶段模拟端扫描结果为准。"

[R1-02|critical] 立项依据 / 研究方案｜rationale L87/L111、scheme L55/L88、full_review L26｜FFAST 物理域错配：NIST FFAST 为 X 射线形状因子/质量衰减系数库，不提供光电离截面，不能与 XCOM 并列为独立截面库（③⑤）｜"由本项目团队汇编自 NIST 光电离截面库（XCOM）与 FFAST 等独立截面数据库"｜全链改为："由本项目团队汇编自 NIST XCOM 光电离截面库（Scofield 相对论 Hartree–Fock 单电子模型）及 Verner–Yakovlev 分壳层光电离截面拟合；独立原子截面库不含 shake-up 伴线分支比，仅给出元素与壳层总截面。"并删除其余 4 处 "XCOM 与 FFAST" 并列表述。

[R1-03|critical] 立项依据 / 研究方案｜rationale L87、rationale L102/L111、scheme L55/L88｜XCOM 能段下限为 1 keV，用其核算 284–543 eV 水窗截面不成立；且 XCOM 不含子壳层分解，无法得出 Ar 3s/3p、Ne 2s/2p 相对占比（①②）｜"水窗低段 284–409.7 eV 的多电子电离截面数据主要来源于现有公开测量，由本项目团队汇编自 NIST 光电离截面库（XCOM）与 FFAST 等独立截面数据库"｜改为："水窗低段 284–409.7 eV 的多电子电离截面数据，由本项目团队汇编自 Verner–Yakovlev 分壳层光电离截面拟合（覆盖 10 eV–10 keV、含 Ar 3s/3p 与 Ne 2s/2p 子壳层分解）及实验文献；XCOM 数据库能段下限为 1 keV，不用于本项目水窗能段核算。"

[R1-04|high] 参考文献｜references L83｜[40] 为死条目：列于文献表但四章正文零引用，编号对账缺口（⑤）｜"[40]† Xia M, Nishimiya K, Dong D, et al. Complex-gate all-optical frequency-resolved optical gating…"｜二择一：（a）在 rationale §2.5 或 scheme §3.3 补挂 [40] 作为"复振（complex-gate）全光 FROG 备选重建方法"的对照锚，并注明其原文报告约 300 as 孤立脉冲、100–180 eV 氩靶；（b）删除 [40] 条目并将后续编号前移，补挂 [46][47] 于 rationale L4（须同步修正 references L95/L97 之后的编号与尾注）。推荐（a）。

[R1-05|high] 研究内容 / 立项依据｜content L41、content L39、rationale L18/L19、full_review L34｜"氦气单一 1s 通道的多通道贡献近似为零"表述过强且与同段自相矛盾：He 1s 电离阈 54.4 eV 之上存在 2s2p 双重激发关联卫星（60–64 eV 区可观强度），水窗 284–543 eV 区"近似为零"不严格；content L39 写"氦气单一 1s 通道的多通道贡献低于 5%"、L41 写"近似为零"，两处口径不一（①③⑤）｜"水窗能区 284 eV 之上，氦气单一 1s 通道的多通道贡献近似为零"｜改为："水窗能区 284–543 eV 内氦气的 2s2p 关联卫星通道相对 1s 通道贡献为小量（文献报道该类卫星主要分布在 54–64 eV 关联阈附近，随光子能量升高快速衰减；本项目所涉能区的具体量级由第一阶段 TDSE 模拟端核算），本项目按 ≤5% 单通道极限档处理，不作为严格零通道假设。"

[R1-06|high] 立项依据 / 研究方案｜rationale L78、scheme L43/L47｜Ishii[13] 光子通量"约 10⁶ 光子/秒"在 rationale 与 scheme 间口径不一（scheme 按效率链给出 10⁶–10⁸/秒），且 Ishii 2014 原文只给出 150–300 eV 区间转换效率约 10⁻⁹（谱仪后），未给出光子通量数值，该锚不成立（①②）｜"其谱截止约 325 eV、光子通量约 10⁶ 光子/秒量级"｜改为："其谱截止约 325 eV，150–300 eV 区间由红外脉冲到软 X 射线连续谱的转换效率经谱仪后约为 10⁻⁹ 量级（原文口径，为本项目光子通量估算的效率参照）。"

[R1-07|medium] 研究方案｜scheme L43｜Jarecki[42] 能区数值与原文不符：原文为"水窗 200–600 eV"，申请书写"覆盖 284–531 eV 水窗能区"，属把实验的衍射观测能段（约 500 eV）与源谱范围混同（③⑤）｜"Jarecki 等[42]于 2024 年以 2.1 μm、10 kHz OPCPA 系统演示水窗软 X 射线衍射，覆盖 284–531 eV 水窗能区"｜改为："Jarecki 等[42]于 2024 年以 2.1 μm、10 kHz、27 fs OPCPA 系统在氦气腔中产生源谱跨 200–600 eV 的软 X 射线脉冲，以能量色散方式演示水窗软 X 射线衍射（结构动力学观测点位于约 500 eV，探测系统分辨率约 1 eV）。"

[R1-08|medium] 研究方案｜scheme L88｜水窗高段 Xe 4d / Kr 3d 芯态-价态占比的"截面曲线"来源声明不成立：XCOM 与 FFAST 均不提供子壳层光电离曲线，无法支撑 Xe 4d 与 Kr 3d 的占比标定（①②③）｜"该占比以 NIST 光电离截面库（XCOM）与 FFAST 等数据库的 Xe 4d、Kr 3d 光电离曲线结合实测数据交叉标定"｜改为："该占比由 Verner–Yakovlev 分壳层光电离截面拟合给出的 Xe 4d、Kr 3d 分壳层曲线与实测数据交叉标定（XCOM 与 FFAST 均为 X 射线能段库，不用于本项分壳层光电离核算）。"

[R1-09|medium] 研究内容 / 研究方案｜content L39、scheme L53、scheme L65｜氩 3s/氖 2s 阈值与"通道开放"的因果表述含混：阈值低于能区下限只说明该通道在能区内已开放，不说明其贡献占比；且 Ar 3s 阈 29.2 eV 对应的是 Ar 第一电离能 15.76 eV 之上的 3s 亚壳层，文本把两者混用（①②）｜"Ne 2s 电离阈 48.5 eV、Ar 3s 阈 29.2 eV 之上通道开放，Ne 2s/2p 双壳层与 Ar 3s/3p 在 50–150 eV 全段贡献从阈能附近的低位渐升、高段约 8%–15%"｜改为："Ne 2s 亚壳层电离阈 48.5 eV、Ar 3s 亚壳层电离阈 29.24 eV 均低于本能区下限 50 eV，故 2s/3s 通道在 50–150 eV 全段开放；其相对 2p/3p 通道的贡献随入射能量升高由阈能附近的低位单调升至高段约 8%–15%（分壳层截面比由 Verner–Yakovlev 拟合给出并经第一阶段实测标定）。"

[R1-10|low] 全文一致性｜full_review L26、rationale L87｜"XCOM 与 FFAST 仅提供元素与壳层总截面"的口径声明在 full_review 跨章节统一表述表中无对应条目，四章一致性表遗漏该条（⑤）｜full_review 表中无"截面数据来源与口径"行｜在 full_review §三 跨章节统一表述表补一行："| 光电离截面数据源与口径 | Verner–Yakovlev 分壳层拟合（10 eV–10 keV，含子壳层分解）为主，XCOM 不用于水窗能段；独立原子截面库不含 shake-up 伴线分支比 | 立项依据、研究内容、研究方案 |"

---

## 四、量化锚核实记录

| 锚 | 申请书位置 | 核实结果 | 证据 URL |
|---|---|---|---|
| Cousin 2017 水窗条纹 322 as 上限 | rationale L10、full_review L5 | ✅ 成立。原文："confirm an upper limit of the duration of the isolated pulse of 322 as" | https://arxiv.org/html/1710.02208v1 |
| Ardana-Lamas 19.2 as / 谱中心 243 eV / 上沿 390 eV | rationale L38 | ✅ 成立 | https://spj.science.org/doi/10.34133/ultrafastscience.0128 |
| Ardana-Lamas Kr 3d 截面 "3p 的约 10 倍、4p 的近 100 倍" | rationale L38 | ✅ 成立。原文："nearly 10 times larger than that of the Kr(3p) shell and almost 100 times larger than that of the Kr(4p) shell" | https://arxiv.org/abs/2510.04086 |
| Han 等 Comment 质疑三项（Auger / 低能谐波 / 固有啁啾） | rationale L38、scheme L98 | ✅ 成立 | https://arxiv.org/abs/2510.17949 |
| Ardana-Lamas Reply 预印本 | rationale L38、scheme L98 | ✅ 存在（arXiv:2511.08391） | https://arxiv.org/abs/2511.08391 |
| Gao 25 ± 2 as、50–320 eV、>10¹² 光子/秒 | rationale L37、scheme L98 | ✅ 成立 | https://arxiv.org/abs/2508.14774 |
| Gao 18 as（Nat. Commun. 17, 8810） | rationale L37、scheme L98 | ✅ 成立，谱跨 50–320 eV | https://arxiv.org/abs/2606.27963 |
| Ishii 2014：1.6 μm、9.0 fs、550 μJ、1 kHz、截止 325 eV | rationale L78、scheme L43 | ✅ 成立 | https://www.nature.com/articles/ncomms4331 |
| **Ishii 2014 光子通量"约 10⁶ 光子/秒"** | rationale L78 | ❌ **不成立**：原文只给"150–300 eV 区间转换效率经谱仪后约 10⁻⁹"，无光子通量数字 → R1-06 | https://www.nature.com/articles/ncomms4331 |
| Pupeikis 2020：2.2 μm、16.5 fs、25 W、14 GW、100 kHz | scheme L43 | ✅ 成立。原文："extending beyond 0.6 keV"、"photon energies up to 0.6 keV" | https://ethz.ch/content/dam/ethz/special-interest/phys/quantum-electronics/ultrafast-laser-physics-dam/publications_awards/publications/2020/466%20(optica-7-2-168%202020)%20mid-IR%20OPCPA%2025W%20100kHz.pdf |
| **Pupeikis 2020 "覆盖 280–620 eV"** | scheme L43 | ⚠️ **口径需改**：原文表述为"延伸超过 0.6 keV"，未给 280 eV 下限；ETH 官方新闻稿称"延伸到 620 eV 覆盖整个水窗"。建议改"延伸至 0.6 keV 以上，覆盖水窗全段" | 同上 |
| Jarecki 2024：2.1 μm、10 kHz、27 fs | scheme L43 | ✅ 成立（原文另载 2.3 bar 氦气腔、光谱 200–600 eV、分辨率约 1 eV@500 eV） | https://arxiv.org/abs/2407.05964 |
| **Jarecki 2024 "覆盖 284–531 eV"** | scheme L43 | ❌ **不符**：原文为"photon energies across the water window from 200 to 600 eV" → R1-07 | https://arxiv.org/abs/2407.05964 |
| Blöchl 2025：2.1 μm、6.9 fs、2.35 mJ、10 kHz | scheme L45 | ✅ 成立 | https://www.osti.gov/pages/biblio/2571766 |
| Fu 2020：TW 级驱动、水窗 nJ 级、较前人高约两个量级 | scheme L47 | ✅ 成立（水窗段 >3.5 nJ） | https://scispace.com/pdf/high-efficiency-ultrafast-water-window-harmonic-generation-ns52qhbyrp.pdf |
| Hasan 2026：Auger 相对 4d 光电子时间偏移约 1.32 fs、中心 130 eV | scheme L100 | ✅ 成立。原文："time shift of ∼1.32 fs relative to the 4d photoelectrons"、"centered at 130 eV" | https://arxiv.org/abs/2512.19965 |
| Tarrant 2025：相干 shake-up、"呼吸离子" | rationale L31、scheme L21 | ✅ 成立 | https://arxiv.org/abs/2503.21976 |
| Gao 2610.24891：多通道两电子 TDSE、s/d 双光子振幅比分离 | scheme L21 | ✅ 成立 | https://arxiv.org/abs/2610.24891 |
| SinBasis Networks：80 000 张合成阿秒条纹光谱 | rationale L56 | ✅ 成立 | https://ojs.aaai.org/index.php/AAAI/article/view/38412 |
| Peschel 2022：Ne 2p₆ 基态 → εs/εd 分波、角分辨 RABBIT | rationale L28、scheme L108 | ✅ 成立 | https://www.nature.com/articles/s41467-022-32780-5 |
| Pabst & Dahlström 2016 PRA 94, 013411 | rationale L46 等 | ✅ 文献真实（纯理论方案，未给残余量化上界，与申请书表述一致） | https://doi.org/10.1103/PhysRevA.94.013411 |
| Kheifets 等 PRA 2026, 113, 043103 | rationale L106、scheme L110 | ✅ 文献真实，未报告残余区间数字，与申请书表述一致 | https://doi.org/10.1103/9jcm-8gd8 |
| Inzani 2024 rACE：绝对延迟确定度优于原子单位时间 | rationale L52 | ✅ 成立（"accuracy better than the atomic unit of time"） | https://doi.org/10.1088/2515-7647/ad252a |
| CH₄ C 1s 电离阈 290.7 / 290.892 eV | scheme L23/L55 | ✅ 成立（DESY SR-76/04 给 290.7 eV；Urquhart & Gillies 2005 给 290.892 eV） | https://cds.cern.ch/record/2941767 |
| CH₄ C 1s 振动精细结构 3962 meV、寿命展宽 8310 meV | R1-01 判据（差 0.9 eV ≈ 2.3 个振动量子，属振动结构而非 shake-up 伴峰） | ✅ 成立 | https://ui.adsabs.harvard.edu/abs/1996PhRvA..53.4120K |
| **CH₄ C 1s shake-up 卫星阈 303 eV 与 311 eV** | R1-01 判据 | ✅ **成立且与申请书冲突**。Köppe 1996 原文："Two structures labeled a b … at photon energies of hν=303 eV and hν=311 eV … located several eV below the shakeup satellite thresholds indicated by 1–4" | https://ui.adsabs.harvard.edu/abs/1996PhRvA..53.4120K |
| **CH₄ C 1s 伴峰 291.6 eV** | scheme L23 | ❌ **无文献支撑**：Urquhart 2005 NEXAFS 精细结构在 286.72–288.66 eV（1s→3s 287.00、1s→3p 288.17），全文零命中 291；检索亦无 291.6 eV 存在 C 1s shake-up 卫星的证据 → R1-01 | https://arxiv.org/abs/2005.13551（Urquhart & Gillies 2005 JPCA 109, 2151） |
| **NIST FFAST = X 射线形状因子/MAC 库（非光电离截面库）** | rationale L87/L111、scheme L55/L88 | ❌ **物理域错配**：FFAST 由 Chantler 等编，为 X 射线衍射/干涉仪/晶体学服务，能段阈至 433 keV，给出 f₁/f₂ 与质量衰减系数；不含光电离截面 → R1-02 | https://www.nist.gov/pml/note-nist-x-ray-attenuation-databases ; https://pages.nist.github.io/FFAST.jl/example/ |
| **XCOM 能段下限 1 keV** | rationale L87/L102/L111、scheme L55/L88 | ❌ **与水窗能段不自洽**：XCOM 为 1 keV–100 GeV；且 NIST 明确说明"XCOM data set presents results only for energies above 1 keV" → R1-03 | https://www.nist.gov/pml/xcom-photon-cross-sections-database ; https://www.nist.gov/pml/note-nist-x-ray-attenuation-databases |
| Ne 2s 亚壳层阈 48.5 eV | content L39/L41、scheme L53 | ✅ 成立（LBL XDB：Ne 2s = 48.5 eV） | https://xdb.lbl.gov/Section1/Periodic_Table/Ne_Web_data.htm |
| [40] Xia 等 Complex-gate AO-FROG（arXiv:2608.30516） | references L83 | ⚠️ **文献真实但正文零引用**（死条目） → R1-04 | https://arxiv.org/abs/2608.30516 |

---

## 五、结论

**剩余意见性质：点状缺陷，非方向性风险。** 三条 critical（R1-01 CH₄ 伴峰、R1-02 FFAST、R1-03 XCOM 能段）全部集中在"截面数据来源与量化锚"这一条支线上，是可定点替换的引用与数值问题，不动摇方法学主线：双通道 TDSE 模型、解析修正项形式、偶极相位二级解耦策略、跨能区双变量图谱的物理框架自洽，②指标定义可操作与④逻辑闭环两项完整通过。上轮 8 条 critical/high 全部修复且无回退，说明该课题的修订机制有效。

**建议：暂不进入验收准备，先做一轮定向修补（1–2 天工作量）。** 修补路径：R1-02 与 R1-03 可合并为一次"截面数据源口径统一"改写（rationale L87/L102/L111、content L23、scheme L55/L88/L135 共 8 处），R1-01 需把 291.6 eV 替换为 Köppe 1996 的 303/311 eV 卫星阈并相应调整论证句，R1-04 二择一处置死条目。完成后五项核查可达"过四"（①②③⑤补齐），rigor 落 0.82–0.89、总评分 0.83–0.85，进入通道 B 验收准备。

**一个必须提示的连带影响**：R1-03 改口径后，申请书现有的"8%–15%（氩）""18%–24%（甲烷）""16%–26%（氮气）""约 10%（rACE 基准点）"四个多通道贡献估值将彻底失去外部数据来源锚（它们原本就已被上轮 R1-02 降级为"设计估值"）。这些数字当前已正确标注为待标定设计值，逻辑上无矛盾，但评审人在答辩现场大概率会追问"8% 从哪来"。建议在修订时统一补一句可核验的文献指针（例如 Verner–Yakovlev 1996 J. Phys. B 29, 3279 的分壳层拟合或 Kennedy 1972 对 Ne 2s/Ar 3s 的计算），否则把"待第一阶段实测标定"写进正文摘要级显著位置，以避免在答辩环节成为致命追问点。
