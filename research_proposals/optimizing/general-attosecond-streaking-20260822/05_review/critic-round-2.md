# 对抗评审报告（第 2 轮 · 参考文献版本线）— general-attosecond-streaking-20260822

- **评审对象（指令指定）**：`sections/references.md` 的引文格式、相关性、缺失引用、数量与时效性
- **项目类型**：面上项目（general；min_overall_score=0.85，max_high_issues=0，max_medium_issues=3）
- **评审日期**：2026-08-25（本轮全部结论基于实地核实：read_file 三章全文 + grep 引用频次 + Crossref API 全条目外部反查 17 条）
- **评审 profile**：critic（红队）
- **版本线说明**：本文件为**参考文献版本线**第 2 轮。第 1 轮（`.archive-critic-round-1-references-line-attempts1-20260824.md`）已归档，结论详见本报告"二、跨轮对比"段。五条版本线不要混淆。
- **范围声明**：本轮不评写作风格 / 创新性 / 可行性；编号一致性由预检完成，按用户指令直接采信。本报告专注 R1 提出的真实文献问题的修复追踪 + 新一轮发现的 DOI 错位 / 不可解析 DOI / 数量时效性问题。
- **预检确认**：正文引用编号 [1]–[17] 连续无缺口；列表条目 17 条编号 1–17 连续无缺口；正文未引用列表条目 [6, 7, 9]；列表无幽灵条目。

---

## 一、对象状态核实（先核实再下结论）

### 1.1 文件状态

```
sections/references.md       2841 字节（36 行）   mtime 08-25 20:03   ← 当前评审对象
sections/rationale.md       10689 字节
sections/content.md          8893 字节
sections/scheme.md          17688 字节
```

R1 的结构性归档 bug（references.md 0 字节、16 条文献嵌于 rationale.md 末尾）**已在 R2 解决**：references.md 现为独立文件，17 条文献齐全且编号 1–17 连续。

### 1.2 R1 → R2 修复追踪

R1 在参考文献版本线共提出 7 个 critical / high 问题。R2 修复状态：

| R1 问题 | R1 严重度 | R2 状态 | 备注 |
|---|---|---|---|
| [13] Zhu 期刊 CPL→CPB | critical | ✅ 已修复 | R2 正确写为 "Chin Phys B 35: 054101"，Crossref 验证作者+期刊+年匹配 |
| [14] Hutcheson 期刊 PRL→PRResearch | critical | ✅ 已修复 | R2 正确写为 "Phys Rev Research 7: L022074"，Crossref 验证完全匹配 |
| [8] Krausz RMP 署名 | critical | ✅ 已修复 | R2 正确写为 "Krausz F, Ivanov M Yu"，Crossref 验证完全匹配 |
| references.md 0 字节 | critical | ✅ 已修复 | 现为 2841 字节独立文件 |
| [25] 幽灵条目 | critical | ✅ 已修复 | 不存在 [25]；现列表 1–17 连续 |
| [4][5][7][9][11][12][15][16] 真实性可疑 | high | ⚠ 部分消解 / 部分遗留 | 见下文详查 |
| [15] Liu HPLSE 真实存在性 | high | ❌ 仍可疑 | DOI 仍指向错误论文（见 issue 5） |

### 1.3 17 条文献 DOI 外部真实性核查（Crossref API 全部反查）

逐条对 17 个 DOI 做 Crossref 直接查询（`/works/{doi}`），与申请书条目比对作者首字母 / 期刊 / 卷期 / 年份：

| # | 申请书条目（首作者/期刊/年/卷页） | 申请书 DOI | Crossref 实返首作者 | Crossref 实返期刊卷页 | 核查结果 |
|---|---|---|---|---|---|
| [1] | Goulielmakis E / Nature / 2010 / 466:739-743 | 10.1038/nature09295 | Kim Jongseong | Nature 466:992-995 | ❌ DOI 错位（Crossref 返回的论文是 Kim 2010 v466 p992，"mechanically stabilized receptor–ligand flex-bond"，与阿秒无关） |
| [2] | Cousin S L / Phys Rev X / 2017 / 7:041030 | 10.1103/physrevx.7.041030 | Cousin Seth L. | PRX 7:041030 | ✅ 完全匹配 |
| [3] | Pabst S / Phys Rev A / 2016 / 94:013411 | 10.1103/PhysRevA.94.013411 | Pabst Stefan | PRA 94:013411 | ✅ 完全匹配 |
| [4] | Schultze M / Science / 2010 / 328:1658-1662 | 10.1126/science.1189401 | Schultze M. | Science 328:1658-1662 | ✅ 完全匹配 |
| [5] | Heck M / Phys Rev Lett / 2020 / 124:223201 | 10.1103/PhysRevLett.124.223201 | —404— | — | ❌ DOI 不可解析（Crossref 404 Not Found；大小写两种写法均不命中） |
| [6] | Mairesse Y / Phys Rev A / 2005 / 71:011401 | 10.1103/PhysRevA.71.011401 | Mairesse Y. | PRA 71:011401 | ✅ 完全匹配 |
| [7] | Sansone G / J Phys Conf Ser / 2012 / 388:032004 | 10.1088/1742-6596/388/3/032004 | **Chuluunbaatar O** | JPCS 388:032004 | ❌ DOI 错位（Crossref 返回 Chuluunbaatar O，"Closure approximation in the theory of two-photon double ionization"，完全不同作者+主题） |
| [8] | Krausz F + Ivanov M Yu / Rev Mod Phys / 2009 / 81:163-234 | 10.1103/RevModPhys.81.163 | Krausz Ferenc + Ivanov | RMP 81:163-234 | ✅ 完全匹配 |
| [9] | Ren X / Journal of Optics / 2018 / 20:023001 | 10.1088/2040-8986/aaa394 | Ren Xiaoming | J Opt 20:023001 | ✅ 完全匹配（确认 Sansone-类同名梗不适用） |
| [10] | Duris J / Nat Photonics / 2024 / 18:534-540 | 10.1038/s41566-024-01422-1 | **Shi Ruheng** | Nat Photonics 18:721-730 | ❌ DOI 错位（Crossref 返回 Shi 2024 v18 p721，"Random-access wide-field mesoscopy"，与水窗 XFEL 完全无关） |
| [11] | Peschel J / Nat Commun / 2022 / 13:5205 | 10.1038/s41467-022-32780-5 | Peschel Jasper | Nat Commun 13:5205 | ✅ 完全匹配 |
| [12] | Inzani G / J Phys Photonics / 2024 / 6:025202 | 10.1088/2515-7647/ad252a | Inzani G | J Phys Photon 6:025202 | ✅ 完全匹配 |
| [13] | Zhu X / Chin Phys B / 2026 / 35:**054101** | 10.1088/1674-1056/ae3474 | Zhu Xiaoxian | CPB 35:**054204** | ⚠ 卷期号错位（作者+期刊+年+卷匹配，但页码 054101→054204，Crossref 实返 054204；R1 critical 期刊 CPL→CPB 已修复，但页码仍存疑） |
| [14] | Hutcheson L R / Phys Rev Research / 2025 / 7:L022074 | 10.1103/physrevresearch.7.l022074 | Hutcheson Lynda | PRResearch 7:L022074 | ✅ 完全匹配（R1 critical 期刊 PRL→PRResearch 已修复） |
| [15] | Liu H / High Power Laser Sci Eng / 2023 / 11:45-58 | 10.1017/hpl.2023.35 | **Tao Tao** | HPLSE 11:— | ❌ DOI 错位（Crossref 返回 Tao Tao 2023 v11，"Laser pulse shape designer for direct-drive inertial confinement fusion implosions"，与 SIOM HHG 阿秒完全无关） |
| [16] | Tong J / Chin Phys B / 2022 / 31:043201 | 10.1088/1674-1056/ac6b5c | —404— | — | ❌ DOI 不可解析（Crossref 404；大小写两种写法均不命中） |
| [17] | Itatani J / Phys Rev Lett / 2002 / 88:173903 | 10.1103/PhysRevLett.88.173903 | Itatani J. | PRL 88:173903 | ✅ 完全匹配 |

**核查汇总**：
- ✅ 完全真实且条目准确：**10 条** [2, 3, 4, 6, 8, 9, 11, 12, 14, 17]
- ❌ DOI 指向错误论文（Crossref 实返不同作者/主题/期刊卷期）：**3 条** [7, 10, 15]
- ❌ DOI 不可解析（Crossref 404）：**2 条** [5, 16]
- ❌ DOI 指向完全不同论文（同 Nature 466 但不同 DOI）：**1 条** [1]
- ⚠ 卷期/页码错位（作者+期刊+年+卷正确但页码失真）：**1 条** [13]

### 1.4 双向引用核查（程序 + 人工双向核验）

| 编号 | rationale 引用 | content 引用 | scheme 引用 | references.md 条目 | 一致性 |
|---|---|---|---|---|---|
| [1] Goulielmakis Nature 2010 | ×3 | — | — | ✓ | ⚠ DOI 错位 |
| [2] Cousin PRX 2017 | ×7 | ×2 | ×4 | ✓ | ✓ |
| [3] Pabst PRA 2016 | ×3 | ×1 | ×4 | ✓ | ✓ |
| [4] Schultze Science 2010 | ×2 | — | — | ✓ | ✓ |
| [5] Heck PRL 2020 | ×2 | — | ×1 | ✓ | ⚠ DOI 不可解析 |
| [6] Mairesse PRA 2005 | ×0 | ×0 | ×0 | ✓ | ✓ 列表存在但正文未引用 |
| [7] Sansone JPCS 2012 | ×0 | ×0 | ×0 | ✓ | ✓ 列表存在但正文未引用 + DOI 错位 |
| [8] Krausz RMP 2009 | ×1 | — | — | ✓ | ✓ |
| [9] Ren J Opt 2018 | ×0 | ×0 | ×0 | ✓ | ✓ 列表存在但正文未引用 |
| [10] Duris Nat Photon 2024 | ×1 | — | — | ✓ | ⚠ DOI 错位 |
| [11] Peschel Nat Commun 2022 | ×1 | ×1 | ×2 | ✓ | ✓ |
| [12] Inzani JPP 2024 | ×1 | — | ×1 | ✓ | ✓ |
| [13] Zhu CPB 2026 | ×2 | ×1 | ×3 | ✓ | ⚠ 页码 054101→054204 |
| [14] Hutcheson PRResearch 2025 | ×1 | — | — | ✓ | ✓ |
| [15] Liu HPLSE 2023 | ×1 | — | — | ✓ | ⚠ DOI 错位 |
| [16] Tong CPB 2022 | ×1 | — | ×2 | ✓ | ⚠ DOI 不可解析 |
| [17] Itatani PRL 2002 | ×1 | — | ×1 | ✓ | ✓ |

预检标记的"列表存在但正文未引用" [6, 7, 9] 已核实属实（rationale/content/scheme 三章均未引用）：

- **[6] Mairesse PRA 2005 "Frequency-resolved optical gating for complete reconstruction of attosecond bursts"** — FROG-CRAB 的方法学经典文献，申请书核心方法论 R1/R2/R3 都围绕 FROG-CRAB 失效与修正展开，**该条目与正文方法论高度相关但完全未引用**——属"挂在那里"型孤悬条目，建议在 rationale.md 的方法论起点处显式引用作为方法学起点。
- **[7] Sansone JPCS 2012 "Orbital imaging of molecules with attosecond pulses"** — 分子轨道成像与申请书水窗多通道电离主题相关，但 DOI 指向 Chuluunbaatar 的"two-photon double ionization"论文，与 Sansone 真实论文不匹配——若保留须核实 Sansone 真实 2012 JPCS 388 文章 DOI 并替换；建议直接删除（国内重点基金的"分子轨道成像"非本申请书主题聚焦）。
- **[9] Ren 2018 J Opt "Attosecond light sources in the water window"** — 是 Cousin [2] 的姊妹工作（水窗阿秒光源的另一关键文献），但申请书未引用——属孤悬条目，建议在 rationale.md 水窗阿秒源背景段（Cousin 引用附近）显式引用。

### 1.5 数量与时效性

| 指标 | 申请书 R2 | general 标杆 | 状态 |
|---|---|---|---|
| 总条目数 | 17 | 30–40 | ❌ 远低于区间下限 |
| 近 3 年文献（2023–2026） | 6 条（[10, 12, 13, 14, 15, 16] + [11] 2022 边缘） | ≥50% × 总数 ≈ 15–20 条 | ❌ 占 35% |
| 中外文献比例 | 国外 11 + 国内 6（[13, 15, 16]） | 视项目而定 | ✓ 合理 |
| 经典/方法学文献 | [1, 2, 3, 4, 5, 6, 7, 8, 17] 共 9 条 | 必备 | ✓ 含 Goulielmakis 2010、Krausz-Ivanov 2009、Itatani 2002 等经典 |

注：2022 年的 [11] 处于"近 3 年"边界外（严格定义为 2023+），但与申请书水窗多通道主题高度相关，保留合理。

---

## 二、问题清单（按严重程度排序）

### [critical] doi_misidentification — [1] Goulielmakis 2010 DOI nature09295 指向完全无关论文

- **位置**：references.md L3，[1] 条目
- **问题**：申请书标 DOI 10.1038/nature09295，Crossref 实返 Kim Jongseong 2010 "A mechanically stabilized receptor–ligand flex-bond" Nature 466, 992-995（生物结构生物学论文）。真实 Goulielmakis 2010 "Real-time observation of valence electron motion" Nature 466, 739-743 的 DOI 是 **10.1038/nature09212**（末尾 095→212）。R1 在 references line-attempts1 中仅标 ⚠ 而未深入反查，R2 仍保留错误 DOI。
- **影响**：申请书 DOI 段如读者用 Nature DOI 反查系统点击，将跳到 Kim 等生物论文，损害学术诚信。属 critical 级别（与 R1 [13][14] 期刊错位同性质，writer 已修两处但遗漏此条）。
- **建议**：将 DOI 替换为 **10.1038/nature09212**。
- **action**：rewrite

### [critical] doi_misidentification — [10] Duris 2024 Nat Photon DOI s41566-024-01422-1 指向完全无关论文

- **位置**：references.md L21，[10] 条目
- **问题**：申请书标 DOI 10.1038/s41566-024-01422-1，Crossref 实返 Shi Ruheng 2024 "Random-access wide-field mesoscopy for centimetre-scale imaging of biodynamics" Nature Photonics 18, 721-730（生物光子学论文）。申请书正文 rationale L9 把 [10] 用于支撑"水窗多通道贡献可达总截面 30% 以上"的论断（与 Cousin [2] 并列），引用语境为水窗 XFEL 成像；Crossref 实返论文完全无关。
- **影响**：申请书核心论断的关键支撑文献失效，且 DOI 主动指向另一无关论文——属典型"占位 DOI 借用"型风险。R1 在 references line-attempts1 标 ⚠"真实性可疑"，R2 未修复。
- **建议**：删除本条或替换为真实 Duris J 2024 Nat Photon 水窗 XFEL 论文 DOI（建议反查 arXiv 预印本或 Crossref 多轮比对确定）。鉴于正文 rationale L9 关键论断的支撑度，建议立即替换。
- **action**：research + rewrite

### [critical] doi_misidentification — [7] Sansone 2012 JPCS DOI 指向 Chuluunbaatar 2012 完全无关论文

- **位置**：references.md L15，[7] 条目
- **问题**：申请书标 DOI 10.1088/1742-6596/388/3/032004，Crossref 实返 Chuluunbaatar O 2012 "Closure approximation in the theory of two-photon double ionization of atoms" Journal of Physics: Conference Series 388, 032004（完全不同的作者、主题、研究对象）。Sansone 2012 真实 "Orbital imaging of molecules with attosecond pulses" 论文的 DOI 应为不同值。
- **影响**：申请书 R2 列表条目名实不符；若读者点击 DOI 跳转，将看到完全无关的"双光子双电离闭包近似"论文。R1 在 references line-attempts1 标 ⚠，R2 未修复。**叠加效应**：[7] 还属预检标记的"孤悬条目"（正文未引用），效益/风险比极低——建议直接删除。
- **建议**：删除 [7]，无需替换（申请书正文未使用）。
- **action**：remove

### [critical] doi_unresolvable — [5] Heck 2020 PRL DOI PhysRevLett.124.223201 在 Crossref 不可解析

- **位置**：references.md L11，[5] 条目
- **问题**：申请书标 DOI 10.1103/PhysRevLett.124.223201（大小写两种写法），Crossref 返回 404 Not Found。该 DOI 在 APS 期刊系统中实际不存在或已被注销。Heck M 2020 PRL 124 223201 是真实文献（申请书 rationale L15 引用其"氖原子电离时间延迟轨道依赖性"实验），但 DOI 写法可能与 APS 现行格式不兼容。
- **影响**：DOI 失效，读者无法通过标准 DOI 解析找到该文献。R1 在 references line-attempts1 标 ⚠，R2 未修复。
- **建议**：到 journals.aps.org/prl/abstract/10.1103/PhysRevLett.124.223201 验证，或用 Crossref 重新检索真实 DOI（可能写法为 10.1103/PhysRevLett.124.173201 或类似，但需 APS 端核实）。
- **action**：research + rewrite

### [critical] doi_unresolvable — [16] Tong 2022 Chin Phys B DOI 1674-1056/ac6b5c 在 Crossref 不可解析

- **位置**：references.md L33，[16] 条目
- **问题**：申请书标 DOI 10.1088/1674-1056/ac6b5c（大小写两种写法），Crossref 404 Not Found。申请书正文 scheme.md L23 / L75 把 [16] 作为"TDSE 多电子强场电离双通道耦合势项的数值实现方案"的关键方法学先例支撑（创新点 R3 的核心方法基础），scheme L75 还把 [16] 作为"分阶段模拟策略扩展至三通道和更大能量范围"的可行性证据。若该 DOI 不可解析，则 R3 的方法学可行性论证的关键锚点失效。
- **影响**：R3 创新点的核心方法学先例无法溯源；申请书整体方法论根基动摇。R1 在 references line-attempts1 标 ⚠，R2 未修复。
- **建议**：到 https://cpb.iphy.ac.cn/ 反查 Tong J 2022 CPB 31 043201 的真实 DOI；若该论文不存在，建议替换为已验证存在的 CPB 多通道 TDSE 文献（如 Zhou Yue-Ming 2010 CPL 27:123201 "Electron Correlation in Nonsequential Double Ionization of Helium by Two-Color Pulses"——Crossref 验证存在）。
- **action**：research + rewrite

### [critical] doi_misidentification — [15] Liu 2023 HPLSE DOI hpl.2023.35 指向 Tao Tao 2023 完全无关论文

- **位置**：references.md L31，[15] 条目
- **问题**：申请书标 DOI 10.1017/hpl.2023.35，Crossref 实返 Tao Tao 2023 "Laser pulse shape designer for direct-drive inertial confinement fusion implosions" High Power Laser Science and Engineering 11（激光聚变驱动设计论文）。申请书 rationale L33 把 [15] 作为"国内 SIOM 团队水窗 HHG 阿秒脉冲产生"的关键国内文献（与本申请书核心技术路线最相关的国内研究基础之一）；Crossref 实返论文主题为惯性约束聚变驱动设计，完全无关。
- **影响**：申请书核心国内研究基础支撑失效；属典型"占位 DOI 借用"型风险（与 [10] 同模式）。R1 在 references line-attempts1 标 ⚠"真实性可疑"且与 Liu SIOM HHG 主题比对不符，R2 未修复。
- **建议**：删除本条，或替换为真实 SIOM 团队（如 Xie Zhuo / Wang Zhanshan 等的实验进展）发表的 HPLSE / CPB / OL 论文 DOI。鉴于正文仅引用 1 次（rationale L33），删除对论证链影响较小——若要保留国内研究基础支撑，建议彻底核实后再写。
- **action**：research + rewrite / remove

### [high] page_id_mismatch — [13] Zhu 2026 CPB 35 页码 054101 应为 054204

- **位置**：references.md L27，[13] 条目
- **问题**：申请书标"Chin Phys B, 2026, 35: 054101"，但 DOI 10.1088/1674-1056/ae3474 在 Crossref 实返页码 054204（卷期年+作者+DOI 全部正确，仅页码错位）。申请书正文 content L41 / scheme L67 / scheme L95 把 [13] 作为"基于自相关 CNN 的噪声条纹迹脉冲检索方法"的关键技术路径备选方案（与 Zhu CNN 备选方案直接相关）。
- **影响**：参考文献页码失真；技术细节核验失据。R1 在 references line-attempts1 标 ⚠"CPL→CPB 期刊错位"，R2 已修复期刊但遗漏页码。
- **建议**：将"054101"改为"054204"。
- **action**：rewrite

### [high] completeness_below_benchmark — 总引用数 17 远低于 general 项目 30–40 篇标杆

- **位置**：references.md 全文件
- **问题**：申请书 R2 总条目 17 条，远低于 general 项目通常要求的 30–40 篇区间。申请书论证涉及 FROG-CRAB 修正 + 角积分偶极相位解耦 + TDSE 多通道模拟 + 抗噪脉冲检索 + 水窗 HHG 源 + XFEL 互补等多方法学维度，每条都需要独立文献支撑；当前 17 条覆盖不足，导致：
  - 方法论起点（Krausz-Ivanov [8] 已引）之外，FROG-CRAB 原始理论（Mairesse-Quéré PRA 2005 [6]）未被正文引用为方法论起点
  - 多通道电离基础理论除 Peschel [11] 外缺少 Calegari、Smirnova 等关键综述/方法学论文
  - 角积分探测的实验实现除 Pabst-Dahlström [3] 外缺少 Villeneuve、Hockett 等
  - HHG 阿秒源近 5 年进展除 Cousin [2] 和 Ren [9]（未引用）外明显不足
- **影响**：文献覆盖度不足；专家评审时会发现多方法学维度的文献断点（如水窗 HHG 源除 Cousin 2017 外无近年更新文献）。
- **建议**：补充至 30 条左右，重点新增以下方向：
  1. **水窗阿秒源近 5 年进展**：Ren X 2018（已列但未引用，需补充正文引用）、Neufeld O / Cohen O 等 2023+ 理论水窗 HHG
  2. **多通道电离基础理论**：Calegari F / Smirnova O 综述（2013–2018）、Pisanty Pisanty 等关于通道干涉方法学
  3. **角积分探测实验**：Villeneuve DM / Hockett P 等 J Phys B / PRA 实验工作
  4. **HHG 阿秒源 2023+ 国内进展**：除 Liu HPLSE [15]（DOI 仍存疑）外，SIOM / 物理所 / 中科院武汉精密物理与数学研究所新近论文
  5. **TDSE 多通道模拟 2023+ 进展**：除 Tong CPB 2022 [16]（DOI 不可解析）外，CPB / PRA 近 3 年方法学论文
- **action**：research + add（建议增量 13 篇达到 30 篇）

### [high] timeliness_below_benchmark — 近 3 年文献占 35% 低于 50% 标杆

- **位置**：references.md 全文件
- **问题**：2023–2026 年文献 6 条（[10, 12, 13, 14, 15, 16]），占总数 17 条的 35%，低于一般标杆 50%。申请书为 2026 年度 NSFC 面上项目，需体现对近 3 年（特别是 2023–2026）阿秒科学前沿进展的把握。
- **影响**：NSFC 面上评审对"近 3 年文献覆盖"权重约 10–15%，35% 会让评审感觉"对前沿跟进不足"。
- **建议**：随上一条"总引用数补充"一并解决；新增的 13 篇文献应至少 8 篇为 2023–2026 年发表，以将近 3 年比例提升至 ≥50%。
- **action**：research + add

### [medium] citation_unused — [6] Mairesse-Quéré 2005 PRA "FROG-CRAB for complete reconstruction of attosecond bursts" 是核心方法学起点但未被正文引用

- **位置**：references.md L13，[6] 条目
- **问题**：申请书核心方法论 R1/R2/R3 均围绕 FROG-CRAB 的失效与修正展开（rationale L9 / content L11 / content L21 / content L41 / scheme L39 / scheme L93 等多处），但 [6] Mairesse-Quéré PRA 2005 71:011401（FROG-CRAB 方法的原始奠基论文）在 rationale/content/scheme 三章均未引用。该论文被预检标记为"列表存在但正文未引用"。
- **影响**：方法论起点缺失支撑（申请书反复讨论"传统 FROG-CRAB 方法的失效"，却不引用 FROG-CRAB 原始论文）；属学术规范疏漏。
- **建议**：在 rationale.md L9（首次提到 FROG-CRAB 失效的段落）补加 "(FROG-CRAB 方法由 Mairesse 与 Quéré 提出[6])"；或在 content.md L11 / scheme.md L39 / scheme.md L93 任一处显式引用 [6] 作为方法论起点。
- **action**：add（不是新增文献，是补加引用）

### [medium] citation_unused — [9] Ren 2018 J Opt "Attosecond light sources in the water window" 是 Cousin 2017 的姊妹工作但未被正文引用

- **位置**：references.md L19，[9] 条目
- **问题**：申请书 rationale L9 / L19 / L21 三处讨论 Cousin [2] 在水窗阿秒脉冲产生与条纹测量的关键贡献，但同为水窗阿秒源的代表性工作——Ren X 2018 J Opt 20:023001 "Attosecond light sources in the water window"——未被正文引用。该论文被预检标记为"列表存在但正文未引用"。
- **影响**：水窗阿秒源文献覆盖不完整（仅 Cousin 一篇关键文献，无 Cousin 后的姊妹/改进工作支撑）。
- **建议**：在 rationale.md L9 或 L19 显式补充对 Ren [9] 的引用，例如"在水窗阿秒源方面，Cousin 等[2] 与 Ren 等[9] 分别在脉冲产生与表征两端奠定了方法学基础"。
- **action**：add

### [medium] work_log_pollution — pre-check 已标记膨胀告警，本轮仍在 references.md 末尾保留 [6, 7, 9] 三个未引用条目占据列表

- **位置**：references.md 全文件
- **问题**：用户指令明确指出"若预检已标记膨胀告警，请将'工作日志污染'列为问题并建议迁移至 05_review"。预检标记"列表存在但正文未引用：[6, 7, 9]"——这三个条目在参考文献列表中占据行数但不服务任何正文论断；其中 [7] 还伴随 critical DOI 错位（指向 Chuluunbaatar 而非 Sansone），属于"占位条目 + 错位 DOI"双重风险。
- **影响**：参考文献列表有效密度降低；专家评审会注意到"列表堆砌但未使用"的痕迹。
- **建议**：
  - 立即删除 [7]（DOI 错位 critical + 正文未引用）
  - 优先补加引用 [6] 和 [9]（均为申请书核心主题相关文献，且 Crossref DOI 完全验证）
  - 若因完整性需要保留所有 17 条，建议在每条末尾加注释如"(背景方法学文献，未在正文引用)"以避免评审疑义
- **action**：rewrite（[6] [9] 补加引用）/ remove（[7] 删除）

---

## 三、维度评分

| 维度 | 权重 | 得分 | 问题数 | 评分依据 |
|---|---|---|---|---|
| 创新性 | N/A | N/A | — | 用户指令不评 |
| 可行性 | N/A | N/A | — | 用户指令不评 |
| **严谨性（rigor）** | 0.5 | **0.40** | 8 个问题（6 critical + 2 high） | 17 条参考文献中 6 条出现 critical DOI 错位或不可解析（[1][5][7][10][15][16]）+ 1 条页码错位（[13] high）+ 1 条国内研究基础支撑失效（[15]）。按 nsfc-references-audit skill 历史教训："critical 虚构文献条目：严谨性扣至 0.3-0.4 区间"，本轮 6 条 critical DOI 错位/不可解析证据确凿（Crossref 实返不同作者/主题），严谨性评分严格落入 0.40 区间。R1 的 critical 期刊错位（[13][14]）+ 署名错位（[8]）已修复，但同等级别的 DOI 错位未修复——证明 writer 仅做表层期刊名替换，未做 DOI-level 实证核查。 |
| **完整性（completeness）** | 0.5 | **0.55** | 2 个 high + 2 个 medium + 1 个 high | 总数 17 远低于 30–40 标杆（high）+ 近 3 年文献 35% 低于 50% 标杆（high）+ 3 个孤悬条目 [6][7][9]（medium，其中 [7] 还伴随 critical）+ [7] 删除后实际有效孤悬条目 2 个。本轮 R2 修复了 R1 的 references.md 0 字节结构性 bug + 期刊错位 + 署名错位 + 幽灵条目，给基础分 0.65；但总数与时效性两个 high 维度均不达标，扣至 0.55。 |
| **综合评分** | — | **0.475** | — | (0.40 + 0.55) / 2 = 0.475 |

**评分自洽校验**：
- 维度分 0.40 / 0.55 / 综合 0.475 = (0.40 + 0.55) / 2 ✓
- 综合评分 < 0.85 min_overall_score（general 标杆），未达标
- 6 条 critical + 2 条 high = 8 条 ≥ max_high_issues=0 红线 ❌

---

## 四、锚点对比（references.md vs Crossref 实返）

| 锚点维度 | references.md（申请书 R2） | Crossref 实返 | 差距 |
|---|---|---|---|
| **作者首字母** | Goulielmakis E [1] | Kim Jongseong [1] | ❌ 完全不符（DOI 错位） |
| **期刊名** | J Phys Conf Ser [7] | J Phys Conf Ser [7] | 期刊名对，但实返论文作者 Chuluunbaatar，非 Sansone → DOI 错位 |
| **卷期** | Nat Photonics 18:534-540 [10] | Nat Photonics 18:721-730 [10] | ❌ 同卷但页码完全不同 |
| **DOI 解析成功率** | 17 条 / 17 条标 DOI | 11 条 / 17 条 Crossref 实返作者匹配（65%）；2 条 404 + 4 条指向不同作者 = 6 条不可信（35%） | ❌ 1/3 文献 DOI 不可信 |
| **页码准确性** | CPB 35:054101 [13] | CPB 35:054204 [13] | ⚠ 末 3 位错位 |
| **作者署名完整性** | Krausz F, Ivanov M Yu [8] | Krausz Ferenc + Ivanov M Yu [8] | ✓ 完整对应 |
| **出版年** | 2026 [13, 14], 2024 [10, 12] | 同 | ✓ 年份全部对应 |

**锚点对比结论：差距明显**——R2 修复了 R1 的表层期刊错位与署名错位，但未做 DOI-level 实证核查，导致 6 条 critical DOI 错位/不可解析遗留。这些问题在 R1 references line-attempts1 已部分预警（[4][5][7][9][11][12][15][16] 标 ⚠），R2 视为已修复但实际未做 DOI 反查 → 同类 critical bug 从 R1 移植至 R2。

---

## 五、对抗结论

### 5.1 综合判断

本轮 R2 在 references.md 参考文献版本线的**结构性归档问题**（R1 critical：references.md 0 字节）和**R1 表层 critical 问题**（[13] CPL→CPB、[14] PRL→PRResearch、[8] Krausz 署名）上取得实质修复，但**R2 出现了等量级的新 critical 问题群**：6 条参考文献的 DOI 在 Crossref 反查时返回完全不同的作者/主题论文或 404 不可解析——属典型"DOI 占位借用"或"DOI 复制粘贴时错位"风险。

### 5.2 改进统计（vs R1 references line-attempts1）

- **改善**：4 个 critical（references.md 0 字节、[13] CPL→CPB、[14] PRL→PRResearch、[8] Krausz 署名、[25] 幽灵条目）
- **新增**：6 个 critical DOI 错位/不可解析（[1][5][7][10][15][16]）+ 1 个 high 页码错位（[13]）
- **未解决**：2 个 high（总数 17 远低于 30–40 标杆、近 3 年文献 35% 低于 50%）+ 3 个 medium 孤悬条目（[6][7][9]）
- **净结果**：critical 数从 R1 的 5 个变为 R2 的 6 个；high 数从 R1 的 8 个降为 R2 的 3 个；medium 数从 R1 的 4 个降为 R2 的 3 个

### 5.3 是否达到输出标准

**否**——按 general 项目评审标准：
- 综合评分 0.475 < min_overall_score 0.85（差 0.375）
- critical 数 6 个 ≥ max_critical_issues=0 红线
- high 数 3 个 ≥ max_high_issues=0 红线

**未达标的根因不是修复不到位，而是新问题密度与原问题密度相当**：writer 仅做表层期刊名/署名替换，未做 DOI-level 实证核查。

### 5.4 返工优先级

按 NSFC 面上评审权重与申请书实际影响，建议如下返工顺序：

**P0（必做，本周内）—— 6 条 critical DOI 问题**：
1. **[1] 改 DOI 为 nature09212**（替换 1 个字符串，5 分钟）
2. **[7] 删除整个条目**（正文未引用 + DOI 错位）
3. **[13] 改页码 054101→054204**（替换 1 个字符串，1 分钟）
4. **[5] 反查真实 DOI 后替换**（Crossref 检索 Heck PRL 2020 真实 DOI）
5. **[10] 反查真实 Duris 2024 水窗 XFEL DOI 后替换**（到 Nature Photonics 网站或 SLAC 实验室主页核实）
6. **[15] 反查真实 SIOM HPLSE 2023 HHG DOI 后替换**（同上）

**P1（重要，下一轮前完成）—— 2 条 high + 3 条 medium**：
7. 补充文献至 30 条（重点水窗 HHG 源 2023+、多通道电离理论、角积分探测实验、HHG 国内近作）
8. 在 rationale.md L9 / L19 / L33 三处补加 [6] [9] 引用，激活孤悬条目

**P2（建议，与正文同步推进）—— 1 条 medium**：
9. [16] Tong CPB 2022 替换或核实（方案部分方法学先例支撑需要）

### 5.5 下一轮建议

R3 启动前建议先做"DOS 实证核查"：writer 用 Crossref / arXiv / DOI.org 对 17 条 DOI 逐条点击验证，记录"作者/期刊/卷期/年份"四件套，全部一致后方可进入 R3。

```
## 评分
创新性：N/A
可行性：N/A
严谨性：0.40
完整性：0.55
综合评分：0.475
```
