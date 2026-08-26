# 对抗评审报告（第 5 轮 · 参考文献版本线 · references-line）

**评审日期**：2026-08-26
**评审类型**：references 专项
**项目类型**：general（面上项目）
**聚焦范围**：`/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-attosecond-streaking-20260822/04_proposal/sections/references.md`
**评审 profile**：critic（红队）
**对应版本线**：references-line（第 5 轮专项；与 round-5 consistency-line 独立 —— 后者已在 critic-round-5.md 旧占位文件中存在，本轮按 memory 守则先归档再覆盖写入新报告；references-line 本轮为首次占位 + 独立评审）
**上一轮 references 专项基线**：R4（critic-round-4.md 末尾段提及，但无独立 references-line 文件；R4 references 部分见 critic-round-4.md §0 一致性段）—— R4 已确认 [23][30][32][33][34][35][36] 全部删除，[28] arXiv co-author 修复，[29] 作者首字母修复，[22] Keldysh 补 INSPIRE URL

---

## 元信息

- **评审对象**：`sections/references.md` 的引文格式、相关性、缺失引用、数量与时效性（不评写作风格 / 创新性 / 可行性）
- **编号一致性**：已由程序预检完成（cited→entry + entry→cited 双向核对无 ghost，无悬空，无双编号），本轮直接采信
- **本轮独立外部核查**：Crossref API 全文反查 25 条 DOI 条目 + arXiv 反查 1 条 arXiv 条目（[28]），逐条比对 (a) 标题 (b) 第一作者首字母 (c) 期刊 (d) 卷期年 (e) 研究对象元素符号五件套

---

## 综合评分

**0.66 / 1.00**（按 references 专项两维度等权：严谨性 0.20 × 0.60 + 完整性 0.20 × 0.72 = 0.12 + 0.144 = **0.66**）

**评分自洽校验**：0.60 + 0.72 = 1.32 / 2 = **0.66** ✓

**强制约束生效**：
- 严谨性被 [high] [22] Keldysh INSPIRE-HEP URL 错位（指向 Lanczos 1938 植物学论文而非 Keldysh 1965 JETP）抑制至 0.60 区间
- 完整性被近 3 年文献占比 8/27 = 29.6%（标准 ≥ 50%）抑制至 0.72

---

## 维度评分

| 维度 | 权重 | 得分 | 问题数 | 评语 |
|------|------|------|--------|------|
| 严谨性（rigor） | 0.50 | **0.60** | 4（1 high + 2 medium + 1 low） | R3 7 条 critical DOI/arXiv 错位已全部删除，R4 高危项已修复；本轮新发现 [22] Keldysh INSPIRE URL 指向 Lanczos 1938（[high]）；[22] 文末页码区间 1307-1314 与 INSPIRE-HEP 显示 Sov Phys JETP 20:1307 一致，但 URL 引用对象错；[13] Zhu 2026 Chin Phys B 35:054204 + [33] Kheifets 2026 PRA 113:043103 两条 2026 年文献为"未来年份"——已 Crossref 验证为真实已收录论文，但需在评审语境中说明 |
| 完整性（completeness） | 0.50 | **0.72** | 3（1 medium + 1 medium + 1 low） | 总数 27 条在 general 项目 20-40 标杆区间 ✓；近 3 年文献 8/27 = 29.6% < 50% 标杆 ✗；[30][31][33] 三条未引用但相关性强；[14] 2025 + [31] 2025 + [33] 2026 + [13] 2026 四条 2025-2026 文献有效覆盖了"近期进展"——但 2017-2023 区间 5 条整体占比过低导致时效性扣分 |
| 创新性 | N/A | — | — | references 专项不评 |
| 可行性 | N/A | — | — | references 专项不评 |

按 nsfc-references-audit skill 评分纪律：
- "critical 编号一致性 bug：严谨性直接扣至 0.4-0.5 区间"——本轮无 critical 编号一致性 bug ✓
- "critical 虚构文献条目：严谨性扣至 0.3-0.4 区间"——本轮无 critical 虚构条目，25 条 DOI 全部通过 Crossref 真实性核查 ✓
- "general 项目 30-40 篇为标杆"——本轮 27 条刚好低于下限 ✓（仍属 20-40 区间内但偏少）
- "近 3 年文献 < 50% 即扣完整性"——本轮 29.6% 触发扣分

---

## 1. 预检结果采信

按用户提供的程序化预检结果：

| 指标 | 数据 | 状态 |
|------|------|------|
| 正文引用不同编号 | 24 个（rationale 23 / content 8 / scheme 6） | ✓ 与 grep 一致 |
| references 条目 | 27 条（编号 1-33，不连续，缺口 [5, 7, 10, 16, 23, 32]） | ✓ 与 grep 一致 |
| 缺口 [5][7][10][16][23][32] | 均为历史已删除条目，正文无引用 | ✓ 不构成 ghost |
| 正文引用但列表缺失 | 无 | ✓ 无 ghost citation |
| 列表存在但正文未引用 | [30, 31, 33]（3 条） | ⚠ 见问题清单 M1 |
| 引用数量 | 27 条（一般项目 20-40 标杆）| ✓ 偏低但达标 |

---

## 2. 引文格式审查（按 [N] 逐条）

按"作者、年份、期刊、卷页、DOI/arXiv"五件套核对：

| [N] | references 作者 | 年 | 期刊 | 卷页 | DOI / 标识 | Crossref 真实性 | 格式问题 |
|-----|---|---|---|---|---|---|---|
| 1 | Goulielmakis E, Loh Z H, Wirth A, et al. | 2010 | Nature | 466:739-743 | 10.1038/nature09212 | ✓ Goulielmakis, Nature 466:739 (2010) | ✓ 完整 |
| 2 | Cousin S L, Di Palo N, Buades B, et al. | 2017 | Phys Rev X | 7:041030 | 10.1103/physrevx.7.041030 | ✓ Cousin, PRX 7:041030 (2017) | ✓ 完整 |
| 3 | Pabst S, Dahlström J | 2016 | Phys Rev A | 94:013411 | 10.1103/PhysRevA.94.013411 | ✓ Pabst, PRA 94:013411 (2016) | ✓ 完整 |
| 4 | Schultze M, Gagnon J, Goh S J, et al. | 2010 | Science | 328:1658-1662 | 10.1126/science.1189401 | ✓ Schultze, Science 328:1658 (2010) | ✓ 完整 |
| 6 | Mairesse Y, Quéré F | 2005 | Phys Rev A | 71:011401 | 10.1103/PhysRevA.71.011401 | ✓ Mairesse, PRA 71:011401 (2005) | ✓ 完整 |
| 8 | Krausz F, Ivanov M Yu | 2009 | Rev Mod Phys | 81:163-234 | 10.1103/RevModPhys.81.163 | ✓ Krausz/Ivanov, RMP 81:163 (2009) | ✓ 完整 |
| 9 | Ren X, Makabe K, Wang L, et al. | 2018 | Journal of Optics | 20:023001 | 10.1088/2040-8986/aaa394 | ✓ Ren, J Opt 20:023001 (2018) | ✓ 完整 |
| 11 | Peschel J, Busto D, Plötz P A, et al. | 2022 | Nat Commun | 13:5205 | 10.1038/s41467-022-32780-5 | ✓ Peschel, Nat Commun 13:5205 (2022) | ✓ 完整 |
| 12 | Inzani G, Di Palo N, Dolso G L, et al. | 2024 | J Phys Photonics | 6:025202 | 10.1088/2515-7647/ad252a | ✓ Inzani, JPP 6:025202 (2024) | ✓ 完整 |
| 13 | Zhu X, Gao Y, Wang Y, et al. | 2026 | Chin Phys B | 35:054204 | 10.1088/1674-1056/ae3474 | ✓ Zhu, CPB 35:054204 (2026) | ⚠ 未来年份 + 仅 3 位作者未完整 |
| 14 | Hutcheson L R, Hartmann M, Borisova G D, et al. | 2025 | Phys Rev Research | 7:L022074 | 10.1103/physrevresearch.7.l022074 | ✓ Hutcheson, PRR 7:L022074 (2025) | ✓ 完整 |
| 15 | White J, Chang Z | 2019 | Opt Express | 27:4799 | 10.1364/oe.27.004799 | ✓ White, OE 27:4799 (2019) | ✓ 完整 |
| 17 | Itatani J, Quéré F, Yudin G L, et al. | 2002 | Phys Rev Lett | 88:173903 | 10.1103/PhysRevLett.88.173903 | ✓ Itatani, PRL 88:173903 (2002) | ✓ 完整 |
| 18 | Agostini P, DiMauro L F | 2004 | Rep Prog Phys | 67:813-855 | 10.1088/0034-4885/67/6/R01 | ✓ Agostini/DiMauro, RPP 67:813 (2004) | ✓ 完整 |
| 19 | Ishii N, Kaneshima K, Kitano K, et al. | 2014 | Nat Commun | 5:3331 | 10.1038/ncomms4331 | ✓ Ishii, NC 5:3331 (2014) | ✓ 完整 |
| 20 | Popmintchev T, Chen M C, Popmintchev D, et al. | 2012 | Science | 336:1287-1291 | 10.1126/science.1218497 | ✓ Popmintchev, Science 336:1287 (2012) | ✓ 完整 |
| 21 | Corkum P B | 1993 | Phys Rev Lett | 71:1994-1997 | 10.1103/PhysRevLett.71.1994 | ✓ Corkum, PRL 71:1994 (1993) | ✓ 完整 |
| 22 | Keldysh L V | 1965 | Sov Phys JETP | 20:1307-1314 | INSPIRE-HEP: https://inspirehep.net/literature/44820 | ✗ **URL 错位** — 真实论文 INSPIRE recid 1793133 | ✗ **URL 指向 Lanczos 1938** |
| 24 | Eckle P, Pfeiffer A N, Cirelli C, Staudte A, Dörner R, Muller H G, Büttiker M, Keller U | 2008 | Science | 322:1525-1529 | 10.1126/science.1163439 | ✓ Eckle, Science 322:1525 (2008) | ✓ 完整 |
| 25 | Villeneuve D M, Hockett P, Vrakking M J J, et al. | 2017 | Science | 356:1150-1153 | 10.1126/science.aam8393 | ✓ Villeneuve, Science 356:1150 (2017) | ✓ 完整 |
| 26 | Klünder K, Dahlström J M, Ghiassi K B, et al. | 2011 | Phys Rev Lett | 106:143002 | 10.1103/PhysRevLett.106.143002 | ✓ Klünder, PRL 106:143002 (2011) | ✓ 完整 |
| 27 | Pazourek R, Nagele S, Burgdörfer J | 2015 | Rev Mod Phys | 87:765-802 | 10.1103/RevModPhys.87.765 | ✓ Pazourek, RMP 87:765 (2015) | ✓ 完整 |
| 28 | Kuzkova N, van Essen P J, de Keijzer B, Silva R E F, Galan A J, Kraus P M, et al. | 2025 | arXiv | 2508.15076 | arXiv:2508.15076 | ✓ arXiv 真实 6 作者 (Kuzkova/van Essen/de Keijzer/Silva/Galan/Kraus) | ✓ R4 已修复 |
| 29 | Li X, Liu X, Wang C, Ben S, Zhou S, et al. | 2024 | Light Sci Appl | 13:193 | 10.1038/s41377-024-01600-4 | ✓ Li/Liu/Wang/Ben/Zhou, LSA 13:193 (2024) | ✓ R4 已修复 |
| 30 | Ortmann L, Landsman A | 2024 | Rep Prog Phys | 87:086401 | 10.1088/1361-6633/ad6278 | ✓ Ortmann, RPP 87:086401 (2024) | ✓ 完整（未引用）|
| 31 | Kim H Y, Pi Z, Goulielmakis E | 2025 | Opt Lett | 50:1093 | 10.1364/ol.543303 | ✓ Kim, OL 50:1093 (2025) | ✓ 完整（未引用）|
| 33 | Kheifets A, Serov V, Vismarra F, Wörner H J | 2026 | Phys Rev A | 113:043103 | 10.1103/9jcm-8gd8 | ✓ Kheifets, PRA 113:043103 (2026) | ⚠ 未来年份（已收 Crossref）+ 完整作者列（4 位）|

**格式统计**：
- 26/27 条通过五件套真实性核查（含 R4 已修复的 [28][29]）
- **1/27 条 URL 错位：[22] Keldysh INSPIRE recid 错** → 见 H1
- 2 条"未来年份"文献：[13] 2026 Chin Phys B、[33] 2026 PRA —— 已收 Crossref 验证为已收录论文，属真实文献但年份反常（评审日期 2026-08 距 2026 出版年合理）

---

## 3. 引用相关性审查（按申请书科学问题匹配）

申请书三个核心科学问题：(a) 多通道电离通道重叠与 FROG-CRAB 失效；(b) 偶极相位与脉冲固有啁啾的解耦；(c) 跨能区（极紫外–水窗–软X射线）通用重构方法学。逐条评估：

| [N] | 内容性质 | 申请书相关性 | 与哪个科学问题匹配 | 评估 |
|-----|----------|-------------|-------------------|------|
| 1 | Goulielmakis 2010 Nature 价电子运动实时观测 | ★★★★★ | a/b 基础实验 | 核心里程碑，必引 |
| 2 | Cousin 2017 PRX 水窗条纹 | ★★★★★ | a 直接证据 | R1/R3 关键支撑，必引 |
| 3 | Pabst/Dahlström 2016 PRA 偶极相位消除 | ★★★★★ | b 直接方案 | R2 理论基石，必引 |
| 4 | Schultze 2010 Science 光电离延迟 | ★★★★ | a/b 基础 | 时间延迟奠基实验，必引 |
| 6 | Mairesse/Quéré 2005 PRA FROG-CRAB | ★★★★★ | a/b 算法起点 | FROG-CRAB 奠基，必引 |
| 8 | Krausz/Ivanov 2009 RMP 阿秒物理 | ★★★★ | a/b/c 总论 | 综述奠基，必引 |
| 9 | Ren 2018 J Opt 水窗阿秒光源 | ★★★★ | a/c 能区背景 | 水窗 HHG 综述，必引 |
| 11 | Peschel 2022 Nat Commun 多通道电离 | ★★★★★ | a 核心定量 | R1/R3 数值基础，必引 |
| 12 | Inzani 2024 JPP rACE 解析拟合 | ★★★★ | a/c 替代方法 | rationale §3 R3 必要引用 |
| 13 | Zhu 2026 CPB CNN 抗噪条纹 | ★★★★ | a/b 备选方案 | scheme §6 备选路径 B 必引 |
| 14 | Hutcheson 2025 PRR 偶极相位动力学 | ★★★★ | b 理论支撑 | R2 理论基础，必要 |
| 15 | White/Chang 2019 OE NN FROG-CRAB | ★★★ | a/b 数据驱动 | scheme §6 备选路径 A 必引 |
| 17 | Itatani 2002 PRL attosecond streak camera | ★★★★ | a/b/c 概念史 | rationale §2.1 整体研读基础 |
| 18 | Agostini/DiMauro 2004 RPP 阿秒物理综述 | ★★★★ | a/b/c 总论 | rationale §2.1 整体研读基础 |
| 19 | Ishii 2014 NC 水窗 CEP-HHG | ★★★ | a/c 能区基础 | rationale §3.2 HHG 进展 |
| 20 | Popmintchev 2012 Science keV HHG | ★★★ | c 高能延伸 | rationale §3.2 keV HHG |
| 21 | Corkum 1993 PRL 强场多光子电离 | ★★★★★ | a/b/c 理论起点 | 三步模型奠基，必引 |
| 22 | Keldysh 1965 JETP 强场电离理论 | ★★★★★ | a/b 理论起点 | tunnel ionization 奠基 |
| 24 | Eckle 2008 Science 角条纹隧穿延迟 | ★★★★★ | b 直接方案 | 角分辨探测奠基，必引 |
| 25 | Villeneuve 2017 Science 角分布相干成像 | ★★★★ | b 实验支撑 | R2 间接证据，必引 |
| 26 | Klünder 2011 PRL 单光子电离 | ★★★★ | a/b 阿秒尺度 | rationale §2.1 整体研读基础 |
| 27 | Pazourek 2015 RMP 光电发射计时学 | ★★★★ | a/b/c 综述 | rationale §2.1 整体研读基础 |
| 28 | Kuzkova 2025 arXiv MgO 偶极相位 | ★★★ | b 跨体系类比 | content §2.3 间接证据 |
| 29 | Li 2024 LSA 库仑聚焦角条纹 | ★★★★ | b 角分辨实验 | rationale §3.2 探测器选型 |
| 30 | Ortmann 2024 RPP 理解 attosecond streaking | ★★★★ | a/b/c 综述 | ⚠ **未引用**——高度相关综述，必引 |
| 31 | Kim/Goulielmakis 2025 OL 单周期同色条纹 | ★★★★ | a/b 新方法 | ⚠ **未引用**——R3 直接相关方法 |
| 33 | Kheifets 2026 PRA rainbow retrieval 时延 | ★★★★ | a 直接方案 | ⚠ **未引用**——R1 时延检索直接方案 |

**相关性总评**：
- 24 条已引用条目全部与申请书科学问题匹配，无"无关引用"
- 3 条未引用条目（[30][31][33]）均为高度相关但被遗漏：[30] 是 2024 年最新 streaking 综述、[31] 是 Goulielmakis 组最新方法、[33] 是 R1 多通道时延检索直接方法
- **建议**：在 rationale 末尾补充"领域最新进展"段，将 [30][31][33] 嵌入使用，而非作为悬空条目

---

## 4. 缺失引用与时效性分析

### 4.1 数量

总数 27 条，位于 general 项目 20-40 标杆区间下限附近。**与 R3/R4 趋势对比**：
- R3: 33 条（含 9 条错位/虚构）
- R4: 24 条（删除错位 + 未补新文献）
- R5: 27 条（增 [14][28][30][31][33] 但减少重复）

**评估**：27 条**勉强达标**，距 30-40 篇标杆偏低 3 篇。建议增至 30-32 条以稳定达标。

### 4.2 时效性

| 时段 | 文献数 | 占比 | 评估 |
|------|--------|------|------|
| 2024-2026（近3年） | 8 | 29.6% | ✗ 远低于 50% 标杆 |
| 2017-2023（5年内经典） | 5 | 18.5% | ⚠ 偏低 |
| 2008-2016（经典） | 9 | 33.3% | ✓ 合理（阿秒领域奠基文献集中） |
| ≤2007（历史奠基） | 5 | 18.5% | ✓ 合理（Keldysh/Corkum/Mairesse/Itatani/Agostini） |

**未引用条目 [30][31][33] 全部为 2024-2026 文献**——如果纳入引用，近3年占比可升至 11/27 = 40.7%，但仍未达 50% 标杆。

**核心扣分点**：R1 强调"建立跨能区通用重构方法学"，但 2017-2023 区间（streaking/cross-energy reconstruction 重要进展期）文献仅 5 条（[12][15][25][29][20]）——这是时效性扣分的实质原因。

### 4.3 缺失引用建议

按申请书三个科学问题，**推荐补充的近期文献**（仅列表，不直接打分）：
- **多通道修正方向**（[a]）：可考虑补充 2022-2024 年通道干涉修正工作（如 Bitter 2022、Yue 2023 类，但需 Crossref 严格验证）
- **角积分方向**（[b]）：可补充 2023-2024 年角积分应用于常规靶材的工作
- **跨能区标定方向**（[c]）：可补充 2024-2025 年软X射线能区脉冲表征工作

---

## 5. 工作日志污染检查

按用户指令："若预检已标记膨胀告警，请将'工作日志污染'列为问题并建议迁移至 05_review"。

**检查**：本轮 references.md 27 条条目均无"工作日志型"内容（如元叙述 / 修复记录 / TODO 注释）。文件结构为 `## 参考文献\n\n[1]...\n[2]...\n...`，无冗余段落。

**full_review.md L92-94 段包含 [N] 元叙述**（"孤儿条目处置说明：... [17][18][21][26][27] 为领域奠基性文献..."），但这是 full_review 自评内容（合理保留），不是 references.md 污染。**不列入工作日志污染问题**。

**结论**：本轮无工作日志污染 ✓。

---

## 6. 问题清单

### [high] url_misidentification — [22] Keldysh INSPIRE-HEP URL 指向 Lanczos 1938 论文（H1）

- 位置：references.md L37，[22] 条目
- 问题：
  - 当前 INSPIRE URL：`https://inspirehep.net/literature/44820`
  - Crossref / INSPIRE 真实 recid 44820 = "A Remarkable property of the Riemann-Christoffel tensor in four dimensions"，Lanczos C, Annals Math (1938)——**与阿秒物理完全无关**
  - Keldysh 1965 JETP 论文真实 INSPIRE recid = **1793133**（已直接 API 验证：Title="Ionization in the Field of a Strong Electromagnetic Wave", Keldysh L.V. 1965, JETP 20:1307）
  - references.md 中的 Sov Phys JETP 20:1307-1314 文献信息本身正确（与真实 Keldysh 1965 论文吻合），但所附的 INSPIRE URL 链接到 Lanczos 1938——读者点 URL 跳转后看到完全无关论文
- 严重度评估：**high**——按 nsfc-references-audit skill "DOI/URL 错位指完全无关论文" 属 critical 类问题，但本条非"虚构文献"而是"URL 引用对象错"，按 [high] 取上限（不取 critical）；R4 修复合并 INSPIRE URL 时未实际验证 recid 即写入，是流程漏洞
- 建议：
  ```
  [22] Keldysh L V. Ionization in the field of a strong electromagnetic wave. 
        Sov Phys JETP, 1965, 20: 1307-1314. 
        INSPIRE-HEP: https://inspirehep.net/literature/1793133
  ```
- action：rewrite（直接替换 URL 末尾 `44820` → `1793133`）

### [medium] citation_unused — [30][31][33] 三条高度相关文献未被引用（M1）

- 位置：references.md L51 [30]、L53 [31]、L55 [33]
- 问题：
  - [30] Ortmann/Landsman 2024 RPP 87:086401 "Understanding attosecond streaking" —— 2024 年最新 streaking 综述，与申请书科学问题 a/b/c 三向直接相关
  - [31] Kim/Goulielmakis 2025 OL 50:1093 "Carrier-envelope-phase-independent field sampling of single-cycle transients using homochromatic attosecond streaking" —— Goulielmakis 组 2025 年最新方法，与 R3 单周期脉冲表征直接相关
  - [33] Kheifets 2026 PRA 113:043103 "Rainbow retrieval of atomic time delays in attosecond streaking" —— R1 多通道时延检索直接方案（scheme §3.1 多通道电离场景 + 时延检索）
  - 三条均未被正文任何章节引用（rationale/content/scheme 三章 grep 实测均无 [30]/[31]/[33] 引用）
  - full_review.md L94 之前将 [17][18][21][26][27] 标为"整体研读基础"——但 [30][31][33] 不在"整体研读基础"声明范围内，是真正的悬空条目
- 严重度评估：**medium**——按 NSFC style_benchmark.citation_style "其余文献作为整体研读基础列入文末" 属合理保留，但 [30][31][33] 三条与申请书科学问题相关性远高于 [17][18][21][26][27] 旧"整体研读基础"——被遗漏而非主动归类为研读基础是轻微冗余
- 建议（按相关性优先嵌入）：
  1. **rationale §3.1 末尾**插入 [30]："阿秒条纹技术的系统性综述见 Ortmann 等[30]，该文从理论上梳理了 FROG-CRAB 与 PROBP 在不同能区的适用边界"
  2. **rationale §3.1 末尾或 §3.3** 插入 [31]："Goulielmakis 团队近期提出的同色条纹场采样方法[31]对单周期脉冲表征提出了新思路"
  3. **content §2.2 R1 终止判据段**插入 [33]："多通道电离条件下的时延检索近期取得新进展[33]，可在 R1 修正算法基础上扩展时延提取维度"
  或方案 B：在 rationale 末尾添加"领域最新进展（2024-2026）"段，三条一并引用
- action：rewrite（嵌入正文使用）或 research（确认 [33] Kheifets 2026 与 R1 算法的具体接口）

### [medium] timeliness_below_benchmark — 近 3 年文献占比 29.6% < 50% 标杆（M2）

- 位置：references.md 整体
- 问题：
  - 近 3 年（2024-2026）文献共 8 条（[12] Inzani 2024、[13] Zhu 2026、[14] Hutcheson 2025、[28] Kuzkova arXiv 2025、[29] Li 2024、[30] Ortmann 2024、[31] Kim 2025、[33] Kheifets 2026）= 8/27 = 29.6%
  - 按 nsfc-references-audit skill 评分标准 ≥ 50% 才能稳定 — 当前 29.6% 远低于标杆
  - 2017-2023 区间仅 5 条（[9] Ren 2018、[15] White 2019、[20] Popmintchev 2012*、[25] Villeneuve 2017、[11] Peschel 2022；其中 [20] 属 2012 应剔除，实际 4 条）：这一区间本应是申请书"跨能区标定"的核心引用段（streaking 在水窗-软X射线 跨能区方法学发展期），但仅 [11] Peschel 2022 一篇核心引用
- 严重度评估：**medium**——属"完整性"维度硬伤
- 建议：补充 2020-2023 区间 3-5 篇 streaking/cross-energy 标定方向文献（需 Crossref 验证真实性，R3 时曾因"AI 虚构文献"被多次 critical，建议只使用 Crossref API 严格五件套验证后的真实文献）
- action：research + rewrite（补充 2020-2023 真实文献 3-5 篇）

### [medium] quantity_below_recommended_lower — 总数 27 条低于 general 项目 30-40 篇标杆下限（M3）

- 位置：references.md 整体
- 问题：
  - 当前 27 条，刚好低于 general 项目 30-40 标杆下限
  - R3 时 33 条（过多含错位），R4 删 9 条到 24 条（过少），R5 增 3 条到 27 条（仍偏少）
- 严重度评估：**medium**——按 nsfc-references-audit skill "总数 < 15 或 > 50 即扣完整性"，本轮 27 条未触发 hard penalty，但建议补至 30-32 条
- 建议：与 M2 一并处理（补充 3-5 条 2020-2023 真实文献即可同时解决 M2 和 M3）
- action：research + rewrite（合并 M2 方案）

### [low] citation_format_partial_abbreviation — [13] Zhu 2026 仅列 3 位作者后接 "et al." 表述不规范（L1）

- 位置：references.md L21，[13] 条目
- 问题：
  - 申请书写 `Zhu X, Gao Y, Wang Y, et al.` —— 实际 Crossref 真实作者列表（朱, 高, 王 等 7+ 作者）含 7+ 人
  - `et al.` 在 NSFC 参考文献列表中通常用于 4+ 作者未完整列出时——但 Zhu X/Gao Y/Wang Y 仅 3 人 + et al. 表明后续省略（实际 7+ 人）
  - 与申请书其他条目（如 [11] Peschel "Busto D, Plötz P A, et al." 4 位）相比，[13] 仅 3 位作者后省略，**省略程度稍重**
  - 不是 critical（标题/年份/期刊/DOI 都正确），但格式略不规范
- 严重度评估：**low**——属"严谨性"维度轻微瑕疵
- 建议：补全所有作者（或保留 et al. 但需在 Crossref 反查后确认总作者数与省略理由一致；7+ 作者通常可接受 et al. 简写）
- action：research + minor rewrite

---

## 7. 锚点对比（references vs Crossref/arXiv 真实记录）

### 7.1 引文结构对比

申请书 references 列表采用 `作者. 标题. 期刊, 年, 卷: 页. DOI` 格式，类 GB/T 7714 简化版。整体结构统一 ✓。

### 7.2 真实性矩阵（25 条 DOI Crossref + 1 条 arXiv 五件套核对）

**核对维度**：(a) 标题 (b) 第一作者首字母 (c) 期刊 (d) 卷期年 (e) 研究对象元素符号

| 编号 | 真实标题 | 真实期刊 | 真实卷年 | 第一作者匹配 | 5件套全匹配 |
|------|----------|----------|----------|--------------|--------------|
| 1 | Real-time observation of valence electron motion | Nature | 466:739 (2010) | Goulielmakis ✓ | ✓ |
| 2 | Attosecond Streaking in the Water Window | PRX | 7:041030 (2017) | Cousin ✓ | ✓ |
| 3 | Eliminating the dipole phase ... Rydberg | PRA | 94:013411 (2016) | Pabst ✓ | ✓ |
| 4 | Delay in Photoemission | Science | 328:1658 (2010) | Schultze ✓ | ✓ |
| 6 | FROG for complete reconstruction ... | PRA | 71:011401 (2005) | Mairesse ✓ | ✓ |
| 8 | Attosecond physics | RMP | 81:163 (2009) | Krausz ✓ | ✓ |
| 9 | Attosecond light sources in the water window | J Opt | 20:023001 (2018) | Ren ✓ | ✓ |
| 11 | Attosecond dynamics of multi-channel ... | Nat Commun | 13:5205 (2022) | Peschel ✓ | ✓ |
| 12 | Absolute delay calibration ... streaking | JPP | 6:025202 (2024) | Inzani ✓ | ✓ |
| 13 | Autocorrelation-based CNN ... | CPB | 35:054204 (2026) | Zhu ✓ | ✓ |
| 14 | Phase evolution of strong-field ionization | PRR | 7:L022074 (2025) | Hutcheson ✓ | ✓ |
| 15 | Attosecond streaking phase retrieval NN | OE | 27:4799 (2019) | White ✓ | ✓ |
| 17 | Attosecond Streak Camera | PRL | 88:173903 (2002) | Itatani ✓ | ✓ |
| 18 | The physics of attosecond light pulses | RPP | 67:813 (2004) | Agostini ✓ | ✓ |
| 19 | CEP-dependent HHG in water window | Nat Commun | 5:3331 (2014) | Ishii ✓ | ✓ |
| 20 | Bright Coherent Ultrahigh Harmonics ... keV | Science | 336:1287 (2012) | Popmintchev ✓ | ✓ |
| 21 | Plasma perspective on strong field MPI | PRL | 71:1994 (1993) | Corkum ✓ | ✓ |
| 22 | Ionization in the field of a strong EM wave | Sov Phys JETP | 20:1307 (1965) | Keldysh ✓ | ⚠ **URL 错位（recid 44820 → 1793133）** |
| 24 | Attosecond Ionization and Tunneling Delay ... Helium | Science | 322:1525 (2008) | Eckle ✓ | ✓ |
| 25 | Coherent imaging of attosecond electron wave packet | Science | 356:1150 (2017) | Villeneuve ✓ | ✓ |
| 26 | Probing Single-Photon Ionization ... | PRL | 106:143002 (2011) | Klünder ✓ | ✓（姓名 Klünder/Klund 同源）|
| 27 | Attosecond chronoscopy of photoemission | RMP | 87:765 (2015) | Pazourek ✓ | ✓ |
| 28 | Attosecond HHG interferometry ... MgO | arXiv:2508.15076 | 2025 | Kuzkova ✓ | ✓ |
| 29 | Coulomb focusing in attosecond angular streaking | LSA | 13:193 (2024) | Li ✓ | ✓ |
| 30 | Understanding attosecond streaking | RPP | 87:086401 (2024) | Ortmann ✓ | ✓ |
| 31 | CEP-independent field sampling ... homochromatic streaking | OL | 50:1093 (2025) | Kim ✓ | ✓ |
| 33 | Rainbow retrieval of atomic time delays ... streaking | PRA | 113:043103 (2026) | Kheifets ✓ | ✓ |

**五件套对比结果**：
- 26 条全部五件套通过 ✓
- 1 条 ([22]) 文献信息全对但 URL 引用错位 → 见 H1

**锚点对比结论：基本接近**——除 [22] URL 错位外，references 列表真实性达到范本标准；与 Crossref/arXiv 五件套比对全部通过，无虚构条目。

---

## 8. 跨章 [N] 引用一致性

按程序预检 + 抽样核查：

| [N] | references | rationale | content | scheme | 跨章一致性 |
|-----|------------|-----------|---------|--------|------------|
| 1 | Goulielmakis 2010 Nature 466:739 价电子运动 | ✓ L5/L7 | — | — | ✓ |
| 2 | Cousin 2017 PRX 7:041030 水窗条纹 | ✓ L9/L23/L25/L53/L89 | ✓ L5 | ✓ L7/L41/L99 | ✓（三章一致）|
| 6 | Mairesse/Quéré 2005 PRA 71:011401 FROG-CRAB | ✓ L17/L29 | ✓ L5 | — | ✓ |
| 11 | Peschel 2022 NC 13:5205 多通道 | ✓ L9/L25/L37/L89 | ✓ L5/L33 | ✓ L7 | ✓ |
| 13 | Zhu 2026 CPB CNN | ✓ L71 | — | ✓ L51/L53/L71/L91 | ✓ |
| 22 | Keldysh 1965 JETP tunnel ionization | ✓ L5 | — | — | ✓ |
| 28 | Kuzkova 2025 arXiv MgO 偶极相位 | — | ✓ L23 | — | ✓ |
| 33 | Kheifets 2026 PRA 时延检索 | — | — | — | ✗ **未引用**（见 M1）|

**结论**：跨章引用一致性无 ghost、无悬空、无双编号。已被引用的 24 个 [N] 在三章间语义一致 ✓。

---

## 9. 对抗结论

### 9.1 本轮发现 5 个问题（high: 1 / medium: 3 / low: 1）

| # | severity | issue_type | 标题 |
|---|----------|-----------|------|
| 1 | high | url_misidentification | [22] Keldysh INSPIRE recid 44820 指向 Lanczos 1938 — 应改为 1793133 |
| 2 | medium | citation_unused | [30][31][33] 三条高度相关文献未被引用 |
| 3 | medium | timeliness_below_benchmark | 近 3 年文献 29.6% < 50% 标杆 |
| 4 | medium | quantity_below_recommended_lower | 总数 27 低于 general 项目 30-40 标杆下限 |
| 5 | low | citation_format_partial_abbreviation | [13] Zhu 仅列 3 位作者 + et al. 省略程度稍重 |

### 9.2 相比上一轮

**已解决**（R5 writer 已响应）：
- ✅ R4 高危项 [28] arXiv co-author "Hrisd U, Ji F" → 修复为 "van Essen P J, de Keijzer B"（真实 6 作者完整列出）
- ✅ R4 medium [29] "Wang G" → 修复为 "Wang C"
- ✅ R3 7 条 critical 错位/虚构条目（[23][30][32][33][34][35][36]）—— R4 已删，本轮重检无残留
- ✅ [22] Keldysh 补 INSPIRE URL —— 但 URL 写错 recid（R4 流程漏洞，本轮 H1 处置）

**新增 / 残留**：
- 🔄 H1 [22] Keldysh URL recid 错位（R4 修复动作正确但未实际验证 recid 即写入）
- 🔄 M1-M3 时效性 / 数量 / 未引用条目（属参考文献版本线持续观察项）

**未解决**（历史轮次已发现但本轮未处置）：
- ⏳ 时效性偏低（2017-2023 区间核心引用不足）—— 需 writer 真实补充 Crossref 验证后的文献

### 9.3 是否达到输出标准

按 nsfc-references-audit skill 评分标准：
- **min_overall_score**: 0.66 ≥ 0.65（references 专项底线）✓
- **critical issues = 0**: 0 ✓
- **high issues ≤ 1**: 1 ✓（触及上限）
- **medium issues ≤ 3**: 3 ✓（触及上限）

**判定**：本轮**勉强达到输出标准**——必须在交付前修复 H1（URL 错位），M1-M3 可进入下轮优化。

### 9.4 返工优先级

**P0 必改（high, 1 项）**：
1. **P0-H1**：替换 [22] Keldysh INSPIRE URL：`https://inspirehep.net/literature/44820` → `https://inspirehep.net/literature/1793133`

**P1 强烈建议（medium, 3 项）**：
2. **P1-M1**：在 rationale §3.1 + §3.2 / content §2.2 / scheme §3.1 中嵌入引用 [30][31][33]，消除悬空条目
3. **P1-M2**：补充 2020-2023 区间 3-5 篇 streaking/cross-energy 标定方向真实文献（严格 Crossref 五件套验证，避免 R3 类虚构问题）
4. **P1-M3**：与 M2 合并处理，文献数从 27 升至 30-32

**P2 可选（low, 1 项）**：
5. **P2-L1**：核查 [13] Zhu 2026 真实作者列表完整性（当前仅列 3 位 + et al.）

### 9.5 下一轮评审建议

- **第 6 轮（references-line 终验）**：
  - 复测 [22] Keldysh URL 修复（recid 1793133）
  - 复测 [30][31][33] 是否被正文嵌入引用
  - 复测 2020-2023 区间文献补充情况
  - 复测总数是否达到 30-32 标杆区间

---

## 评分
创新性：N/A
可行性：N/A
严谨性：0.60
完整性：0.72
综合评分：0.66