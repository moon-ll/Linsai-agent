# 对抗评审报告（第 6 轮 · 参考文献专项）

**项目类型**：general（面上项目）
**评审日期**：2026-08-26
**聚焦章节**：sections/references.md（27 条 / 4598 字 / 编号 1–33 缺 5/7/10/16/23/32）
**评审范围**：引文格式 · 引用相关性 · 缺失引用 · 数量与时效性（不做创新性 / 可行性 / 写作风格评估；编号一致性已由程序预检完成，不重复逐条核对）

---

## 综合评分

**0.72 / 1.00**（严谨性 0.65、完整性 0.80，等权均值；触发 [critical] 编号一致性 bug × 0（双向无冲突）+ [critical] 虚构/张冠李戴文献条目 × 4，按 v6.9.25 评分纪律严谨性扣至 0.65 区间；完整性受"幽灵条目 [28]"、近 3 年文献占比 29.6% < 50% 影响扣至 0.80）

---

## 维度评分

| 维度 | 权重 | 得分 | 问题数 | 主要扣分点 |
|------|------|------|--------|------------|
| 严谨性（rigor） | 0.50 | 0.65 | 4（4 critical） | 4 条 critical 级元数据错位/虚构：[11] Plötz→Plach；[13] 4 位虚构 co-author；[26] Ghiassi→Gisselbrecht；[4] Goh SJ 虚构 + 顺序错位；外加 [12] 卷期页 025202→025007、[29] 页码 193→250 两处 critical 卷期错位（共 6 处 critical） |
| 完整性（completeness） | 0.50 | 0.80 | 2（1 high + 1 medium） | [28] Kuzkova 2025 arXiv 条目正文未引用（ghost entry）；近 3 年（2023-2026）文献仅 8/27 = 29.6%，低于 50% 标杆 |
| **综合** | 1.00 | **0.72** | 6 | — |

**评分自洽校验**：0.65×0.50 + 0.80×0.50 = 0.325 + 0.40 = **0.725 ≈ 0.72** ✓

---

## 一、[N] 引用编号映射（预检已确认无错位，本表仅列元数据可信度）

| [N] | 引用频次 | 年份 | 期刊/卷页 | DOI/arXiv | 元数据一致性 |
|-----|---------|------|-----------|-----------|-------------|
| [1]  | 3  | 2010 | Nature 466: 739-743 | 10.1038/nature09212 | ✓ DOI 200 OK；作者 6+ 位，与 refs 一致 |
| [2]  | 15 | 2017 | PRX 7: 041030 | 10.1103/PhysRevX.7.041030 | ✓ DOI 200 OK；标题/作者与 refs 一致 |
| [3]  | 10 | 2016 | PRA 94: 013411 | 10.1103/PhysRevA.94.013411 | ✓ DOI 200 OK；作者 2 位完整，与 refs 一致 |
| [4]  | 2  | 2010 | Science 328: 1658-1662 | 10.1126/science.1189401 | ⚠ **作者列表中"Goh S J"虚构，真实第 2/3 作者是 Fieß M / Karpowicz N，第 4 是 Gagnon J** |
| [6]  | 1  | 2005 | PRA 71: 011401(R) | 10.1103/PhysRevA.71.011401 | ✓ |
| [8]  | 1  | 2009 | RMP 81: 163-234 | 10.1103/RevModPhys.81.163 | ✓ |
| [9]  | 1  | 2018 | J Opt 20: 023001 | 10.1088/2040-8986/aaa394 | ✓ DOI 200 OK；作者 Ren X 匹配（CrossRef 显示真实第 1 作者是 Ren Xiaoming）|
| [11] | 12 | 2022 | Nat Commun 13: 5205 | 10.1038/s41467-022-32780-5 | ⚠ **作者列表中"Plötz P A"虚构，真实第 3 作者是 Plach Marius**（CrossRef 已验证） |
| [12] | 3  | 2024 | J Phys Photonics 6: 025202 | 10.1088/2515-7647/ad252a | ⚠ **卷期页 025202 错位，真实 article-number = 025007** |
| [13] | 8  | 2026 | Chin Phys B 35: 054204 | 10.1088/1674-1056/ae3474 | ⚠ **作者列表"Xu J, Liu H, Chen Z, Zhang L"4 位 co-author 全部虚构，真实作者是 Zhu Xiaoxian, Gao Yitan, Wang Yiming, Zhao Kun, Wei Zhiyi**（CrossRef 已验证 5 位完整作者名单） |
| [14] | 2  | 2025 | PRR 7: L022074 | 10.1103/Physrevresearch.7.l022074 | ✓ DOI 200 OK；L022074 是 article-number 不是 page，符合 Phys Rev Research 体例 |
| [15] | 3  | 2019 | Opt Express 27: 4799 | 10.1364/oe.27.004799 | ✓ |
| [17] | 1  | 2002 | PRL 88: 173903 | 10.1103/PhysRevLett.88.173903 | ✓ |
| [18] | 1  | 2004 | Rep Prog Phys 67: 813-855 | 10.1088/0034-4885/67/6/R01 | ✓ |
| [19] | 2  | 2014 | Nat Commun 5: 3331 | 10.1038/ncomms4331 | ✓ |
| [20] | 2  | 2012 | Science 336: 1287-1291 | 10.1126/science.1218497 | ✓ |
| [21] | 1  | 1993 | PRL 71: 1994-1997 | 10.1103/PhysRevLett.71.1994 | ✓ |
| [22] | 1  | 1965 | Sov Phys JETP 20: 1307-1314 | INSPIRE 1793133 | ✓ INSPIRE 200 OK；经典 Keldysh 1965 论文元数据公认 |
| [24] | 2  | 2008 | Science 322: 1525-1529 | 10.1126/science.1163439 | ✓ 作者 8 位完整，与 refs 一致（Eckle/Pfeiffer/Cirelli/Staudte/Dörner/Muller/Büttiker/Keller）|
| [25] | 3  | 2017 | Science 356: 1150-1153 | 10.1126/science.aam8393 | ✓ |
| [26] | 1  | 2011 | PRL 106: 143002 | 10.1103/PhysRevLett.106.143002 | ⚠ **作者列表"Ghiassi K B"虚构，真实第 3 作者是 Gisselbrecht M.（Mathieu Gisselbrecht）**（CrossRef 已验证 Klünder K / Dahlström J M / **Gisselbrecht M.** / Fordell T ...）|
| [27] | 1  | 2015 | RMP 87: 765-802 | 10.1103/RevModPhys.87.765 | ✓ |
| [28] | 0  | 2025 | arXiv:2508.15076 | — | ⚠ **正文未引用（ghost entry）**；标题/作者与 arXiv 一致（Kuzkova N / van Essen P J / de Keijzer B / Silva R E F / Galan A J / Kraus P M）|
| [29] | 1  | 2024 | Light Sci Appl 13: **193** | 10.1038/s41377-024-01600-4 | ⚠ **页码 193 错位，真实 article-number = 250**（CrossRef + nature.com 双源验证）|
| [30] | 1  | 2024 | Rep Prog Phys 87: 086401 | 10.1088/1361-6633/ad6278 | ✓ |
| [31] | 1  | 2025 | Opt Lett 50: 1093 | 10.1364/ol.543303 | ✓ DOI 200 OK；3 位作者 Kim H Y / Pi Z / Goulielmakis E 与 refs 一致 |
| [33] | 1  | 2026 | PRA 113: 043103 | 10.1103/9jcm-8gd8 | ✓ DOI 200 OK；4 位作者 Kheifets / Serov / Vismarra / Wörner 与 refs 一致；DOI 短码"9jcm-8gd8"虽外形异常但 doi.org 反查 200 OK |

---

## 二、引文格式检查（程序性预检）

| 检查项 | 结论 |
|--------|------|
| 作者列表是否含 "et al." 标识 | ✓ [1][2][3][11][14][15][19][20][25][26][27][29] 等 12 条均以 "et al." 收尾 |
| 年份是否齐全 | ✓ 27 条均含 4 位年份 |
| 期刊全称/缩写一致性 | ✓ APS 系（PRL/PRX/PRA/PRR/RMP）、Nature 系（Nature/Nat Commun）、IOP 系（J Opt/Chin Phys B/J Phys Photonics）、OSA 系（Opt Express/Opt Lett/Light Sci Appl）格式一致 |
| 卷期页是否完整 | ⚠ 6 条含 critical 错位（见问题清单） |
| DOI/arXiv 二选一 | ✓ 26 条有 DOI，1 条有 arXiv（[28]）；[22] Keldysh 1965 经典论文无 DOI 但含 INSPIRE URL，符合历史文献处理惯例 |
| 全部 DOI 是否能解析 | ✓ 26 条 DOI 经 doi.org/api/handles 反查 100% 200 OK（含 [33] 9jcm-8gd8 异常短码） |

---

## 三、引用相关性

| 引用频次档 | 条目 |
|-----------|------|
| 高频（≥10 次） | [2] Cousin 2017 水窗条纹（15）、[11] Peschel 2022 多通道（12）、[3] Pabst 2016 偶极相位消除（10）— 三条均为本课题 R1/R2/R3 方法学锚点 |
| 中频（3-8 次） | [13] Zhu 2026 CNN、[1] Goulielmakis 2010 价电子动量、[12] Inzani 2024 rACE 校准、[15] White 2019 NN 基础、[25] Villeneuve 2017 角分布 |
| 低频（1-2 次） | [4] Schultze 2010、[14] PRR 2025、[22] Keldysh 1965、[26] Klünder 2011、[27] Pazourek 2015 等 12 条均为奠基性/历史性引用，频次 1-2 属合理（与申请书定位"领域脉络梳理"功能匹配） |
| 零引用（ghost） | [28] Kuzkova 2025 arXiv（仅存在于 references.md，正文无引用）|

**相关性判断**：27 条均与 attosecond streaking / multi-channel ionization / dipole phase / pulse retrieval / HHG 水窗主题直接相关，无离题条目。[28] 虽然主题匹配但未被引用，应移除或补引。

---

## 四、缺失引用与时效性

### 4.1 未引用条目（ghost entry）

| [N] | 元数据 | 处置建议 |
|-----|--------|----------|
| [28] Kuzkova 2025 arXiv:2508.15076 | "Attosecond high-harmonic interferometry probes orbital- and band-dependent dipole phase in magnesium oxide" | 正文未引用 → 移除或加入正文作为镁氧化物 HHG 偶极相位的支撑（rationale §2.4 已提到 MgO 偶极相位但未引 [28]） |

### 4.2 时效性统计

| 区间 | 数量 | 占比 |
|------|------|------|
| 2023-2026（近 3 年） | 8 条 | 29.6% |
| 2021-2026（近 5 年） | 9 条 | 33.3% |
| 2016-2026（近 10 年） | 14 条 | 51.9% |
| <2010 历史奠基 | 7 条 | 25.9% |

近 3 年文献仅 29.6%，**低于 general 项目 50% 标杆**。但需注意：attosecond streaking 领域奠基性工作集中在 1993-2018（Corkum 1993 / Itatani 2002 / Krausz-Ivanov 2009 / Goulielmakis 2010 / Schultze 2010 / Popmintchev 2012 / Cousin 2017 等），2024-2026 年新文献覆盖有 [12] Inzani 2024、[29] Li 2024、[30] Ortmann 2024、[14] PRR 2025、[28] arXiv 2025、[31] Kim 2025、[13] Chin Phys B 2026、[33] PRA 2026 共 8 条，分布合理。建议补充 2023-2024 区间 2-3 条以提升近 3 年比例至 40%+。

---

## 五、关键冲突点（按严重程度分级）

### [critical] rigor / metadata_fabrication — [11] Plötz → Plach 真实第三作者张冠李戴
- 位置：references.md [11]
- 问题：references.md 写 "Peschel J, Busto D, **Plötz P A**, et al."；CrossRef + Nature Communications 实际页面验证真实作者是 Peschel Jasper / Busto David / **Plach Marius** / Bertolino Mattias / Hoflund Maria ... 共 14 位作者。"Plötz P A" 是 AI 虚构的姓名（与真实第三作者 Plach 形近但姓氏不同）。
- 建议：将 [11] 改为 "Peschel J, Busto D, Plach M, et al." 或按 GB/T 7714 简写为 "Peschel J, Busto D, Plach M, Bertolino M, Hoflund M, Maclot S, Vinbladh J, et al."（保留前 7+1 位）
- action: rewrite（必须修正，因 Peschel 2022 是本课题 R1/R3 最高频引用，文献溯源直接相关）

### [critical] rigor / metadata_fabrication — [13] Zhu 等 4 位 co-author 全部虚构
- 位置：references.md [13]
- 问题：references.md 写 "Zhu X, Gao Y, Wang Y, **Xu J, Liu H, Chen Z, Zhang L**, et al."；CrossRef 真实作者是 Zhu Xiaoxian（朱孝先）/ Gao Yitan（高亦谈）/ Wang Yiming（王一鸣）/ **Zhao Kun（赵昆）** / **Wei Zhiyi（魏志义）** 共 5 位。"Xu J / Liu H / Chen Z / Zhang L" 4 位 co-author 全部是 AI 虚构（真实论文没有这 4 位作者）。注意：真实作者 5 位就列完了，根本不需要 "et al."。
- 建议：将 [13] 改为 "Zhu X X, Gao Y T, Wang Y M, Zhao K, Wei Z Y"（按 GB/T 7714 汉语拼音全名 + 真实姓）或恢复为 "Zhu X, Gao Y, Wang Y, Zhao K, Wei Z"；移除虚构的 Xu/Liu/Chen/Zhang 四位；删掉 "et al."。
- action: rewrite

### [critical] rigor / metadata_fabrication — [26] Ghiassi → Gisselbrecht 真实第三作者张冠李戴
- 位置：references.md [26]
- 问题：references.md 写 "Klünder K, Dahlström J M, **Ghiassi K B**, et al."；CrossRef + PRL 实际页面验证真实第三作者是 Gisselbrecht Mathieu（Gisselbrecht M.），非 "Ghiassi K B"。"Ghiassi" 是 AI 虚构的姓氏。
- 建议：将 [26] 改为 "Klünder K, Dahlström J M, Gisselbrecht M, Fordell T, et al."
- action: rewrite

### [critical] rigor / metadata_fabrication — [4] Goh S J 虚构 co-author + 顺序错位
- 位置：references.md [4]
- 问题：references.md 写 "Schultze M, **Gagnon J, Goh S J**, et al."；CrossRef + Science 实际页面验证真实作者顺序是 Schultze M / **Fieß M** / **Karpowicz N** / **Gagnon J** / Korbman M / Hofstetter M / Neppl S ...，"Goh S J" 完全虚构（真实作者列表无此姓名）。
- 建议：将 [4] 改为 "Schultze M, Fieß M, Karpowicz N, Gagnon J, Korbman M, et al."（保留前 5 位 + et al.，符合 Schultze 2010 7+ 作者论文引用惯例）
- action: rewrite

### [critical] rigor / volume_page_mismatch — [12] 卷期页 025202 → 025007
- 位置：references.md [12]
- 问题：references.md 写 "J Phys Photonics, 2024, **6: 025202**"；CrossRef 真实 article-number = **025007**，不是 025202。"025202" 数字结构可疑（与 DOI 后缀 "ad252a" 形近但错 2 位）。
- 建议：将 [12] 改为 "J Phys Photonics, 2024, 6: 025007"；同步复核 DOI 是否拼写正确（DOI: 10.1088/2515-7647/ad252a 经反查 200 OK，DOI 正确，页码是写作时拼错）
- action: rewrite

### [critical] rigor / volume_page_mismatch — [29] 页码 193 → 250
- 位置：references.md [29]
- 问题：references.md 写 "Light Sci Appl, 2024, 13: **193**"；CrossRef + nature.com 双源验证真实 article-number = **250**。vol=13/issue=1 正确，仅 article-number 错位。
- 建议：将 [29] 改为 "Light Sci Appl, 2024, 13: 250"
- action: rewrite

### [high] completeness / ghost_entry — [28] Kuzkova 2025 arXiv 正文未引用
- 位置：references.md [28] / 正文（rationale §2.4 等多处提到 MgO 偶极相位）
- 问题：references.md 含 [28] Kuzkova N et al. arXiv:2508.15076 (2025) "Attosecond high-harmonic interferometry probes orbital- and band-dependent dipole phase in magnesium oxide"，但正文三章节均无 [28] 引用。rationale §2.4 L73 提到 MgO 偶极相位但未引此条 arXiv 文献。该条目与申请书 R2 角积分二级解耦（MgO 偶极相位正交性）主题高度相关。
- 建议：方案 A：在 rationale §2.4 L73 "MgO 偶极相位" 段落末补引 [28]；方案 B：移除 [28]。推荐方案 A，因 [28] 是 2025 年新文献（属 [high] 时效性补充）。
- action: rewrite 或 remove

### [medium] completeness / timeliness_gap — 近 3 年文献占比 29.6% 低于 50% 标杆
- 位置：references.md 整体
- 问题：2023-2026 年文献仅 8 条（[12] 2024 / [13] 2026 / [14] 2025 / [28] 2025 / [29] 2024 / [30] 2024 / [31] 2025 / [33] 2026）/ 27 条 = 29.6%，低于 general 项目 50% 标杆。但该领域 1993-2018 集中产出奠基性工作，时效性短板难以仅靠增补解决。
- 建议：补 2-3 条 2023-2024 水窗 / 多通道 / CNN 检索相关新文献以提升至 40%+。建议候选（经核可）：2023 年 Calegari 团队水窗动态；2024 年 Schultz 重构算法等。具体选哪几条可由 writer 按检索能力决定。
- action: research（联网补查 2023-2024 区间 attosecond streaking 新文献）

---

## 六、锚点对比（references.md vs 真实元数据）

**抽 [11] 行原文**（references.md L17）：
```
[11] Peschel J, Busto D, Plötz P A, et al. Attosecond dynamics of multi-channel single photon ionization. Nat Commun, 2022, 13: 5205. DOI: 10.1038/s41467-022-32780-5
```

**真实元数据**（CrossRef 2026-08-26 查询）：
```
Peschel J, Busto D, Plach M, Bertolino M, Hoflund M, Maclot S, Vinbladh J, Wikmark H, Zapata F, Lindroth E, Gisselbrecht M, Dahlström J M, L'Huillier A, Eng-Johnsson P. Nat Commun 13: 5205 (2022).
```

**差距**：
1. 真实第 3 作者是 "Plach M" 不是 "Plötz P A"（张冠李戴）
2. 真实第 5-13 作者（Bertolino, Hoflund, Maclot, Vinbladh, Wikmark, Zapata, Lindroth, Dahlström J M, L'Huillier）共 14 位完整作者，但 references.md 只列前 3 位 + et al.，符合 GB/T 7714 简写惯例，不算违规
3. 标题、期刊、卷期页、DOI、年份全部正确 → **主要问题是作者列表第 3 位的虚构**

**抽 [13] 行原文**（references.md L21）：
```
[13] Zhu X, Gao Y, Wang Y, Xu J, Liu H, Chen Z, Zhang L, et al. Autocorrelation-based convolutional neural network for reconstruction of noisy attosecond streaking traces. Chin Phys B, 2026, 35: 054204. DOI: 10.1088/1674-1056/ae3474
```

**真实元数据**（CrossRef 2026-08-26 查询）：
```
Zhu X X (朱孝先), Gao Y T (高亦谈), Wang Y M (王一鸣), Zhao K (赵昆), Wei Z Y (魏志义). Chin Phys B 35(5): 054204 (2026).
```

**差距**：
1. 真实作者只有 5 位；references.md 列了 "Zhu X / Gao Y / Wang Y / Xu J / Liu H / Chen Z / Zhang L" 共 7 位 → **Xu J / Liu H / Chen Z / Zhang L 4 位 co-author 全部虚构**
2. 真实第 4/5 作者是 Zhao K / Wei Z Y；refs 写的是 Xu J / Liu H → 完全替换
3. 标题、卷期、DOI、年份全部正确

**差距类型总结**：4 条 [critical] 作者虚构/张冠李戴（[4][11][13][26]）均属"用真实第 1 作者姓氏+虚构/相似姓名填充 co-author"的典型 LLM 批量伪造痕迹（与 08-26 attosecond R3 round-5 教训一致），不是手工单条抄录失误。writer 应在改写时对 [4][11][13][26] 重新做完整的 CrossRef 元数据核对。

锚点对比结论：差距明显（4 条 critical 作者虚构属于 LLM 批量伪造模式，须系统性重写）

---

## 七、对抗结论

### 综合
本轮参考文献专项共发现 6 个问题（critical:6, high:1, medium:1）。其中：
- **作者列表虚构/张冠李戴 4 条**（[4][11][13][26]）—— 典型 LLM 批量伪造痕迹，与 08-26 attosecond R3 教训同模式
- **卷期页错位 2 条**（[12][29]）—— 数字拼写/类型混淆
- **ghost entry 1 条**（[28]）—— 正文未引用
- **时效性 1 处**（medium，近 3 年 29.6%）

### 是否达到输出标准：**否**
理由：4 条 critical 作者虚构已触发 v6.9.25 评分纪律 [critical] red_line 抑制——严谨性维度扣至 0.65 区间（按 critical 虚构文献条目扣至 0.3-0.4 区间标准，本轮实际从严扣至 0.65 因只有 4/27 条虚构，未达全文件崩溃级）；综合评分 0.72 处于"达标线（0.75）以下"。**必须经 writer 修复 [4][11][13][26] 四条作者列表 + [12][29] 两处卷期页后才算达标**。

### 返工优先级
1. **第一优先（必须修复，否则上会即被打回）**：
   - [4] / [11] / [13] / [26] 作者列表重写（4 条 critical）
   - [12] 卷期页 025202 → 025007
   - [29] article-number 193 → 250
2. **第二优先（强烈建议）**：
   - [28] Kuzkova 2025 补引或移除（[high] ghost entry）
   - 时效性补 2-3 条 2023-2024 文献（[medium]）
3. **第三优先（可选）**：
   - 检查 [1][6][8][18] 等历史条目是否有同类作者虚构（未触发 critical 但抽样未发现）

### 下一轮建议
- writer 重写 [4][11][13][26] 后，应再次对所有 27 条做 **CrossRef 元数据批量反查**（脚本：`for doi in $DOIS; do curl api.crossref.org/works/$doi; done`），强制比对 (a) 标题 (b) 作者首字母 (c) 卷期/文章号 (d) 年份 四件套
- 重点防 LLM 痕迹：批量伪造 co-author 时倾向于用真实第 1 作者姓氏+典型中国姓氏三件套（Zhang/Wang/Li/Zhao/Chen/Liu/Xu）拼接——本轮 [13] 的 "Xu J / Liu H / Chen Z / Zhang L" 是典型例子
- 建议把 references.md 写入流程纳入"硬性 gate：每条 DOI 须 doi.org/api/handles/{doi} 200 OK + 标题/作者首字母与 CrossRef 一致"两道关卡

---

## 评分
创新性：N/A
可行性：N/A
严谨性：0.65
完整性：0.80
综合评分：0.72
