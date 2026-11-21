# 对抗评审报告（第 7 轮 · references.md 专项检验）

**项目类型**：general（面上项目）
**评审日期**：2026-08-26
**聚焦章节**：`/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-attosecond-streaking-20260822/04_proposal/sections/references.md`（55 行 / 4611 字符 / 27 条参考文献）
**评审范围**：参考文献 [N] 编号一致性（采信预检）+ 文献真实性 DOI/arXiv 反查 + 内联引用准确性 + 引用相关性与时效性；不重做写作风格 / 创新性 / 可行性评估
**评分纪律**：仅评严谨性（rigor）与完整性（completeness）两维度；综合评分 = (严谨性 + 完整性) / 2；创新性 / 可行性填 N/A

---

## 综合评分

**0.58 / 1.00**（严谨性 0.35 / 完整性 0.80；等权均值；rigor 受 2 条 critical 虚构文献条目触发扣至 0.3-0.4 区间下限；completeness 因近 3 年文献 25.9% 远低于 50% 阈值扣至 0.80）

**评分自洽校验**：(0.35 + 0.80) / 2 = **0.575 ≈ 0.58** ✓（综合 0.58 误差 ≤ 0.02）

---

## 维度评分

| 维度 | 权重 | 得分 | 问题数 | 主要扣分点 |
|------|------|------|--------|------------|
| 严谨性（rigor） | — | 0.35 | 4（2 critical + 1 high + 1 medium） | ① [critical] [33] Kheifets DOI 写成 `10.1103/PhysRevA.113.043103`（404 Not Found）——真实 DOI 是 `10.1103/9jcm-8gd8`，R5 consistency-line §147 已确认真实，R7→本轮间被改错；② [critical] [16] Huppert 整条张冠李戴：references.md 写 Opt Express 24: 25840 (2016)，DOI `10.1364/oe.24.025840`——真实论文是 Rev Sci Instrum 86, 123106 (2015)，DOI `10.1063/1.4937623`（Crossref 反查确认）；③ [high] scheme.md §4.2 L77 内联 "Huppert等[16] 2016年" 年份错位（与 references.md [16] 错误年份一致，触发"参考文献-正文-真实文献"三向错位）；④ [medium] [27] Pazourek RMP 87, 765 / [30] Ortmann RPP 87: 086401 卷号一致 ✓ 但 [30] 题目"Understanding attosecond streaking"与 references.md 表述格式一致——属低风险项 |
| 完整性（completeness） | — | 0.80 | 3（1 high + 2 medium） | ① [high] 近 3 年文献（2023-2026）仅 7/27 = 25.9%，远低于 skill 评分纪律 50% 阈值；② [medium] 缺口 [5][7][10][23][28][32] 共 6 个编号虽为"历史已删除"无 ghost 风险，但跨章引用编号 1-33 不连续可能引起评审专家"是否有删除理由"的疑问（与 R5 consistency-line §134 残留一致）；③ [medium] 数量 27 条达标（20-40 区间），但近 3 年文献比例偏低削弱"时效性"完整性 |

---

## 一、执行清单对照（按本轮 prompt 四项）

| # | 检查项 | 结论 | 关键证据 |
|---|--------|------|----------|
| 1 | 引文格式（作者、年份、期刊、卷页、DOI/arXiv） | **不通过** | ① [16] 5 项元数据全错（期刊/卷/页/年/DOI）；② [33] DOI 404；③ 其他 25 条格式基本统一 |
| 2 | 引用相关性 | **通过** | 27 条全部与 attosecond streaking / HHG / 阿秒脉冲表征相关（含 [1] Goulielmakis 2010 Nature 466: 739-743 虽标题不含 "attosecond" 字样但为 attosecond streaking 标志性实验）；无无关引用 |
| 3 | 缺失引用 | **预检已确认**：无 ghost citation（正文引用但 references 缺失）；无悬空 references（列表有但正文未引用） | 预检双向核查通过 + R5/R6 已多次复核 [30][31] 引用已补齐 ✓ |
| 4 | 引用数量与时效性 | **数量通过 / 时效性不通过** | 总数 27 条达标（20-40）；近 3 年 7 条 = 25.9%（阈值 50%） |

---

## 二、[N] 引用编号 → 参考文献列表 一一对应表

| [N] | references.md 元数据（现状） | Crossref 真实记录 | 状态 |
|-----|---------------------------|------------------|------|
| [1] | Goulielmakis 2010 Nature 466: 739-743 | Nature 466: 739-743, vol/issue/page 一致 | ✓ 通过 |
| [2] | Cousin 2017 PRX 7: 041030 | PRX 7, 4, 041030, "Attosecond Streaking in the Water Window" | ✓ 通过 |
| [3] | Pabst 2016 PRA 94: 013411 | PRA 94, 1, 013411, "Eliminating the dipole phase..." | ✓ 通过 |
| [4] | Schultze 2010 Science 328: 1658-1662 | Science 328, 5986, 1658-1662, "Delay in Photoemission" | ✓ 通过 |
| [6] | Mairesse 2005 PRA 71: 011401 | PRA 71, 1, 011401, FROG for attosecond | ✓ 通过 |
| [8] | Krausz Ivanov 2009 RMP 81: 163-234 | RMP 81, 1, 163-234, "Attosecond physics" | ✓ 通过 |
| [9] | Ren 2018 J Opt 20: 023001 | J Opt 20, 2, 023001, "Attosecond light sources in the water window" | ✓ 通过 |
| [11] | Peschel 2022 Nat Commun 13: 5205 | Nat Commun 13, 1, 5205, "Attosecond dynamics of multi-channel single photon ionization" | ✓ 通过 |
| [12] | Inzani 2024 J Phys Photonics 6: 025007 | J Phys Photonics 6, 2, 025007, "Absolute delay calibration by analytical fitting" | ✓ 通过 |
| [13] | Zhu 2026 Chin Phys B 35: 054204 | Chin Phys B 35, 5, 054204, "Autocorrelation-based CNN..." | ✓ 通过 |
| [14] | Hutcheson 2025 PRR 7: L022074 | PRR 7, 2, L022074, "Phase evolution of strong-field ionization" | ✓ 通过 |
| [15] | White Chang 2019 OE 27: 4799 | OE 27, 4, 4799, "Attosecond streaking phase retrieval with neural network" | ✓ 通过 |
| **[16]** | **Huppert 2016 Opt Express 24: 25840, DOI 10.1364/oe.24.025840** | **真实: RSI 86, 123106 (2015), DOI 10.1063/1.4937623, "Attosecond beamline..."** | ✗ **整条张冠李戴**（5 项全错） |
| [17] | Itatani 2002 PRL 88: 173903 | PRL 88, 17, 173903, "Attosecond Streak Camera" | ✓ 通过 |
| [18] | Agostini 2004 RPP 67: 813-855 | RPP 67, 6, 813-855, "The physics of attosecond light pulses" | ✓ 通过 |
| [19] | Ishii 2014 Nat Commun 5: 3331 | Nat Commun 5, 3331, "CEP-dependent HHG in water window..." | ✓ 通过 |
| [20] | Popmintchev 2012 Science 336: 1287-1291 | Science 336, 6086, 1287-1291, "Bright Coherent Ultrahigh HHG in keV X-ray" | ✓ 通过 |
| [21] | Corkum 1993 PRL 71: 1994-1997 | PRL 71, 13, 1994-1997, "Plasma perspective on strong field MPI" | ✓ 通过 |
| [22] | Keldysh 1965 Sov Phys JETP 20: 1307-1314 (INSPIRE-HEP) | 历史经典论文，无 DOI；INSPIRE ID 1793133 实测可达 | ✓ 通过（无 DOI） |
| [24] | Eckle 2008 Science 322: 1525-1529 | Science 322, 5907, 1525-1529, "Attosecond Ionization and Tunneling Delay Time" | ✓ 通过 |
| [25] | Villeneuve 2017 Science 356: 1150-1153 | Science 356, 6343, 1150-1153, "Coherent imaging of an attosecond electron wave packet" | ✓ 通过 |
| [26] | Klünder 2011 PRL 106: 143002 | PRL 106, 14, 143002, "Probing Single-Photon Ionization on the Attosecond Time Scale" | ✓ 通过 |
| [27] | Pazourek 2015 RMP 87: 765-802 | RMP 87, 3, 765-802, "Attosecond chronoscopy of photoemission" | ✓ 通过 |
| [29] | Li 2024 Light Sci Appl 13: 193 | Light Sci Appl 13, 1, 193, "Coulomb focusing in attosecond angular streaking" | ✓ 通过 |
| [30] | Ortmann 2024 RPP 87: 086401 | RPP 87, 8, 086401, "Understanding attosecond streaking" | ✓ 通过 |
| [31] | Kim 2025 Opt Lett 50: 1093 | Opt Lett 50, 4, 1093, "CEP-independent field sampling..." | ✓ 通过 |
| **[33]** | **Kheifets 2026 PRA 113: 043103, DOI 10.1103/PhysRevA.113.043103** | **真实: PRA 113, 4, article-number 043103, DOI 10.1103/9jcm-8gd8** | ✗ **DOI 错位**（标题/作者/卷期正确，DOI 404） |

**统计**：27 条中 25 条完全通过 + 2 条 critical issue（[16][33]）

---

## 三、关键冲突点（按严重度分级）

### [critical] literature_fabrication — [33] Kheifets DOI 404 不存在

- **位置**：`04_proposal/sections/references.md` L55
- **问题**：
  - references.md 写 `[33] Kheifets A, Serov V, Vismarra F, Wörner H J. Rainbow retrieval of atomic time delays in attosecond streaking. Phys Rev A, 2026, 113: 043103. DOI: 10.1103/PhysRevA.113.043103`
  - **doi.org/api/handles/10.1103/PhysRevA.113.043103 → HTTP 404 Not Found**
  - 真实 DOI（Crossref + doi.org 双确认）：`10.1103/9jcm-8gd8`，已 R5 consistency-line §147 验证
  - 标题、作者（Kheifets / Serov / Vismarra / Wörner）、卷期（PRA 113, 4）、文章号（043103）**全部正确**——仅 DOI 错位
  - 触发 v6.9.25 评分纪律 "critical 虚构文献条目：严谨性扣至 0.3-0.4 区间"
- **建议**：
  - **action: rewrite** —— 将 L55 改为 `[33] Kheifets A, Serov V, Vismarra F, Wörner H J. Rainbow retrieval of atomic time delays in attosecond streaking. Phys Rev A, 2026, 113: 043103. DOI: 10.1103/9jcm-8gd8`
  - writer 写完须跑 doi.org/api/handles/10.1103/9jcm-8gd8 验证 200 OK
  - 注意：R5 报告已正确记录真实 DOI，R7→本轮间被改错——属"历史正确 → 当前错误"的回归 bug，建议 writer 查 git/repair log 找变更源头
- **影响范围**：rationale §2.3 L31 / content §2.6 K2 / references.md [33] 三处引用 [33]——三向闭环中只有 references.md [33] 的 DOI 字段错位，正文表述"近期提出的'彩虹检索'"无具体卷期引用，不触发正文错位

### [critical] literature_fabrication — [16] Huppert 整条张冠李戴（5 项元数据全错）

- **位置**：`04_proposal/sections/references.md` L27
- **问题**：
  - references.md 写 `[16] Huppert A, Jordan I, Wörner H J. Attosecond beamline with actively stabilized and spatially separated beam paths. Opt Express, 2016, 24: 25840. DOI: 10.1364/oe.24.025840`
  - **真实论文（Crossref 验证）**：Huppert M, Jordan I, Wörner H J. "Attosecond beamline with actively stabilized and spatially separated beam paths." **Rev Sci Instrum 86, 123106 (2015)**, DOI: 10.1063/1.4937623
  - **5 项元数据全错**：
    | 字段 | references.md | 真实 | 错位 |
    |------|--------------|------|------|
    | 期刊 | Opt Express | Rev Sci Instrum | ✗ |
    | 卷 | 24 | 86 | ✗ |
    | 页 | 25840 | 123106 | ✗ |
    | 年份 | 2016 | 2015 | ✗ |
    | DOI | 10.1364/oe.24.025840 | 10.1063/1.4937623 | ✗ |
  - **标题正确**——这是典型 LLM 痕迹：标题未改但期刊/卷期/年/DOI 全虚构
  - **正文 scheme.md §4.2 L77 同步错位**："Huppert等[16] 2016年报道的 He-Ne激光联合白光干涉仪方案在 XUV与IR空间分离的阿秒光束线中达到 26 as rms延迟稳定"——年份与 references.md 一致错误
  - 触发 v6.9.25 评分纪律 "critical 虚构文献条目：严谨性扣至 0.3-0.4 区间"
- **建议**：
  - **action: rewrite** —— references.md L27 改为 `[16] Huppert M, Jordan I, Wörner H J. Attosecond beamline with actively stabilized and spatially separated beam paths. Rev Sci Instrum, 2015, 86: 123106. DOI: 10.1063/1.4937623`
  - **action: rewrite** —— scheme.md §4.2 L77 "Huppert等[16] **2016年**报道..." 改为 "Huppert等[16] **2015年**报道..."（与真实年份对齐）
  - writer 写完须跑 doi.org/api/handles/10.1063/1.4937623 验证 200 OK + Crossref 元数据比对
  - **同步影响**：R7 overall consistency 报告 §4.2 提到的"100 as 延迟稳定性"论证基线原本引 Huppert[16] 26 as——若 Huppert 实际是 RSI 2015 而非 OE 2016，"26 as rms"这个数字是否确实来自该论文须二次确认（摘要明确提到"actively stabilized"和"white-light interferometer"，主体结果在 Huppert et al. RSI 86, 123106 (2015) 表 1 / Fig. 4，数字 26 as 与正文一致 ✓）
- **影响范围**：scheme.md §4.2 L77（唯一引用处）；正文 [16] 年份错位是 R7→本轮间的回归 bug

### [high] literature_temporal_mismatch — [16] 正文内联引用年份与 references.md 同步错位

- **位置**：`04_proposal/sections/scheme.md` §4.2 L77
- **问题**：正文写 "Huppert等[16] **2016年**报道..."——与 references.md [16] 写"Opt Express, 2016, 24: 25840"年份一致（同步错位），但**真实年份是 2015**。一旦 references.md [16] 按建议改为 RSI 2015，正文也须同步改为 2015 年，否则会出现"正文年份 ≠ references.md 年份"的二级错位
- **建议**：
  - **action: rewrite** —— scheme.md §4.2 L77 "Huppert等[16] 2016年报道" → "Huppert等[16] 2015年报道"
  - 与上面 [16] critical issue 的修复动作**合并为同一处编辑**——避免两次修改产生中间态
- **触发依据**：本项是 [critical] [16] 张冠李戴的**正文衍生错位**，单独触发 [high] 是为了双重保险：若 writer 修 references.md 时漏改正文，则仍属 high 级"参考文献-正文不一致"

### [medium] temporal_coverage — 近 3 年文献占比 25.9% 远低于 50% 阈值

- **位置**：`04_proposal/sections/references.md` 全文
- **问题**：27 条中 2023-2026 年文献仅 7 条 = 25.9%（[12][13][14][29][30][31][33]），按 nsfc-references-audit skill "时效性 < 50% 即扣完整性"规则扣分
- **现状**：1993-2022 年文献 20 条（74.1%），多为经典奠基（Corkum 1993 / Keldysh 1965 / Krausz 2009 RMP / Schultze 2010 Science 等）——这些是申请书需要的奠基引用，不可删除
- **建议**：
  - **action: research** —— 在 attosecond streaking 领域补充 2023-2026 关键新工作至 ≥13 条（≥50%），候选方向：
    - 多通道/角分辨（已有 [29] Li 2024 Light Sci Appl / [12] Inzani 2024 JPP / [30] Ortmann 2024 RPP，可再加 1-2 条 2025-2026 进展）
    - HHG 水窗能区（已有 [9] Ren 2018 + [19] Ishii 2014，建议补 1-2 条 2024+ 实验进展）
    - 神经网络表征（已有 [13] Zhu 2026 + [15] White 2019，可补 1 条 2024+ CNN/Transformer 进展）
    - 彩虹检索/相位检索（已有 [33] Kheifets 2026，可补 2024-2025 中间过渡工作）
  - 目标：总数保持 30-35 条（仍在 20-40 标杆区间），近 3 年占比 ≥50%
  - 注意：新增条目须逐条跑 DOI 反查 + Crossref 元数据比对，避免再次引入 critical 级 LLM 虚构文献 bug（参考 [33]/[16] 的失败模式）
- **影响范围**：仅完整性扣分，不触发严谨性扣分（前提是新增文献全部真实）

### [medium] numbering_gap — 6 个跳号 [5][7][10][23][28][32] 缺位

- **位置**：`04_proposal/sections/references.md` 全文
- **问题**：参考文献编号 1-33 不连续，缺口 [5][7][10][23][28][32] 共 6 个——预检已确认这些编号在 rationale/content/scheme 三章均无引用（ghost entry 风险解除），属"历史已删除"遗留——R5 consistency-line §134 + full_review.md L14 元叙述均明确"已在历史轮次中删除"
- **建议**：
  - **action: research/remove** —— **方案 A（推荐）**：保留现状（不重新编号），在 references.md 末尾加一行元叙述："注：编号 [5][7][10][23][28][32] 已在 R1-R5 修订轮次中删除，对应原始文献因张冠李戴 / 主题不符 / 重复引用等原因不再保留。"——避免评审专家疑惑
  - **方案 B（备选）**：将 27 条全部重新编号为 1-27 连续，去除所有跳号——但需同步修改 rationale/content/scheme 三章所有 [N] 引用，工作量较大且无功能收益
  - 不建议"补全 6 条新文献填满 1-33 编号"——会引入新一轮 LLM 虚构风险
- **影响范围**：形式问题，不触发引用准确性扣分

---

## 四、锚点对比（references.md vs Crossref/arXiv 真实记录逐字对比）

### 锚点 1：[33] Kheifets 2026 PRA（DOI 错位）

| 来源 | 内容 |
|------|------|
| **references.md L55** | `[33] Kheifets A, Serov V, Vismarra F, Wörner H J. Rainbow retrieval of atomic time delays in attosecond streaking. Phys Rev A, 2026, 113: 043103. DOI: 10.1103/PhysRevA.113.043103` |
| **Crossref 真实记录** | Title: "Rainbow retrieval of atomic time delays in attosecond streaking" / Authors: Anatoli Kheifets, Vladislav Serov, Federico Vismarra, Hans Jakob Wörner / Container: Physical Review A / Volume: 113 / Issue: 4 / Article-number: 043103 / DOI: 10.1103/9jcm-8gd8 / Published: 2026-04-02 |
| **doi.org 反查 current DOI** | `https://doi.org/api/handles/10.1103/PhysRevA.113.043103` → **HTTP 404 Not Found** |
| **doi.org 反查 real DOI** | `https://doi.org/api/handles/10.1103/9jcm-8gd8` → HTTP 200 OK |
| **差距** | 标题、作者、卷期、文章号（113/4/043103）**全部对齐**；DOI 错位（虚假 `PhysRevA.113.043103` vs 真实 `9jcm-8gd8`）——典型 LLM "用真实期刊 + 卷期 + 文章号 + 真实文章标题" 构造伪 DOI 模式 |
| **差距性质** | **DOI 构造性虚构**——4 个字段正确仅 DOI 错误，更隐蔽，比张冠李戴更难发现（DOI 表面格式合法 `10.1103/PRA.x.y.nnnnn` 但对应 handle 不存在） |
| **改写方向** | 直接将 DOI 改为 `10.1103/9jcm-8gd8`，其余字段全部保留 |

### 锚点 2：[16] Huppert 2015（整条张冠李戴）

| 来源 | 内容 |
|------|------|
| **references.md L27** | `[16] Huppert A, Jordan I, Wörner H J. Attosecond beamline with actively stabilized and spatially separated beam paths. Opt Express, 2016, 24: 25840. DOI: 10.1364/oe.24.025840` |
| **Crossref 真实记录** | Title: "Attosecond beamline with actively stabilized and spatially separated beam paths" / Authors: M. Huppert, I. Jordan, H. J. Wörner / Container: **Review of Scientific Instruments** / Volume: **86** / Issue: **12** / Page: **123106** / DOI: **10.1063/1.4937623** / Published: **2015-12-01** |
| **scheme.md §4.2 L77** | "Huppert等[16] **2016年**报道的 He-Ne激光联合白光干涉仪方案在 XUV与IR空间分离的阿秒光束线中达到 26 as rms延迟稳定" |
| **差距** | 标题正确 ✓ / 作者姓 Huppert A vs Huppert M（中间名首字母差异属可接受）/ **期刊、卷、页、年份、DOI 全部 5 项错位**——Opt Express 2016 → Rev Sci Instrum 2015；24: 25840 → 86: 123106；DOI 10.1364 → 10.1063；典型 "标题未改 + 期刊卷期/DOI 全虚构" LLM 痕迹 |
| **差距性质** | **整条元数据张冠李戴**——比 DOI 构造性虚构更严重，因为期刊层面（OE→RSI）就完全错位 |
| **改写方向** | 期刊改为 "Rev Sci Instrum"，卷改为 "86"，页改为 "123106"，年份改为 "2015"，DOI 改为 "10.1063/1.4937623"；同步修改 scheme.md §4.2 L77 年份 "2016年" → "2015年" |

**锚点对比结论：差距明显**——2 条 critical issue 均属 LLM 痕迹导致的元数据构造性虚构 / 张冠李戴，是 references 真实性核验中最隐蔽的 bug 模式（DOI 表面格式合法 + 标题正确 + 卷期数字符合 PRA/OE 编号规则，但实际 handle 不存在或卷期错位）。其他 25 条锚点对比均无差距。

---

## 五、问题清单（按严重度 + 编号 + 位置 + action）

| # | severity | issue_type | 位置 | 问题 | action |
|---|----------|-----------|------|------|--------|
| 1 | critical | literature_fabrication | references.md L55 | [33] Kheifets DOI 写成 `10.1103/PhysRevA.113.043103`（404 不存在），真实 DOI 是 `10.1103/9jcm-8gd8` | rewrite |
| 2 | critical | literature_fabrication | references.md L27 | [16] Huppert 整条张冠李戴：Opt Express 2016 → 真实 RSI 2015；24: 25840 → 真实 86: 123106；DOI 10.1364/oe.24.025840 → 真实 10.1063/1.4937623；年份 2016 → 2015（5 项全错） | rewrite |
| 3 | high | literature_temporal_mismatch | scheme.md §4.2 L77 | "Huppert等[16] **2016年**报道" 与真实论文 2015 年错位（与 #2 同步错位） | rewrite |
| 4 | medium | temporal_coverage | references.md 全文 | 近 3 年文献 7/27 = 25.9%（阈值 50%），时效性偏弱 | research |
| 5 | medium | numbering_gap | references.md 全文 | 6 个跳号 [5][7][10][23][28][32] 缺位，可能引起评审专家"删除理由"疑问 | add 元叙述 / remove 跳号 |

**统计**：critical 2 / high 1 / medium 2 / low 0 = 共 5 个问题

---

## 六、对抗结论

### 综合

- **综合评分**：**0.58 / 1.00**（严谨性 0.35 + 完整性 0.80 均值）
- **是否达到输出标准**：**否**
  - general 项目 quality_threshold: min_overall_score = 0.85，本轮 0.58 远低于 0.85（差 0.27）
  - max_high_issues = 0，本轮 high 1 个（不达标）
  - max_medium_issues = 3，本轮 medium 2 个（达标）
  - **不达标核心原因**：2 条 critical 文献真实性 bug（[33] DOI 404 / [16] 整条张冠李戴）触发 v6.9.25 评分纪律严谨性扣至 0.3-0.4 区间下限

### 相比上一轮（R7 overall consistency 2026-08-26）

| 维度 | R7 overall consistency | R7 references 专项（本轮） | 变化 |
|------|----------------------|---------------------------|------|
| 严谨性 | 0.65 | **0.35** | ↓ 0.30（本轮 2 条 critical 文献真实性 bug 比 R7 的 1 条 critical 编号错位更严重） |
| 完整性 | — | 0.80 | 新评维度 |
| 综合 | 0.78 | **0.58** | ↓ 0.20 |
| critical 数 | 1 | **2** | +1（新增 [33] DOI 错位；[16] 张冠李戴是 R7 未发现的新 critical） |
| high 数 | 2 | **1** | -1（R7 [high] ghost entry [28] 已被预检解除） |
| medium 数 | 3 | **2** | -1 |

**关键变化**：
- **改善**：R7 [high] ghost entry [28] 残留问题已解决（预检确认 references.md 不再含 [28]，正文无 [28] 引用）
- **未解决**：R7 [critical] Luttmann [20] 错位已修复（scheme.md 不再含 Luttmann），但衍生出新 [critical] [16] 张冠李戴 + [critical] [33] DOI 错位——属"修一处漏洞、引入新漏洞"模式
- **新增**：R7 未发现的 [16] 整条张冠李戴（critical 级）+ [33] DOI 错位（critical 级）+ 时效性偏弱（medium 级）

### 返工优先级

- **P0（必须立即修改）**：
  1. 修复 [33] Kheifets DOI 为 `10.1103/9jcm-8gd8`（writer 须跑 doi.org/api/handles 200 OK + Crossref 元数据比对 5 件套）
  2. 修复 [16] Huppert 整条为 RSI 2015 + 同步修复 scheme.md §4.2 L77 年份 2016→2015（同样须跑 doi.org 200 OK + Crossref 比对）
- **P1（强烈建议）**：
  3. 补充 6-7 条 2023-2026 文献至近 3 年占比 ≥50%（每条须 DOI 反查验证）
- **P2（定稿前整改）**：
  4. 在 references.md 末尾加跳号 [5][7][10][23][28][32] 元叙述说明

### 下一轮评审建议聚焦

- 重点核查 R8 是否落实 P0 修复（[16][33] DOI 必须 200 OK）
- 重点核查 writer 补充的 6-7 条新文献**是否每条都跑 DOI 反查**（避免重蹈 [16][33] 覆辙）
- 建议加一轮 **cross-file audit** 专门核查 R7→R8 间所有被 writer 改动的文献元数据是否引入新 critical bug——本轮发现的 [16][33] 都是 R5→R7 间历史正确 → 当前错误的回归 bug，说明 writer 的文献修改动作本身需要 audit 流程保护

---

## 评分
创新性：N/A
可行性：N/A
严谨性：0.35
完整性：0.80
综合评分：0.58
