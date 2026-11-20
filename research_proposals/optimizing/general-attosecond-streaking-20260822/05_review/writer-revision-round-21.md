# 申请书修订记录（R21 参考文献严谨性维度聚焦修订）

**日期**：2026-10-07
**聚焦章节**：references.md（同步登记至 00_research_idea.md 与 02_literature/reading-notes.md；其余章节未触动）
**聚焦维度**：严谨性 0.55 → 目标 ≥0.85
**前置评审**：critic-round-3-references.md（参考文献专项，8 项问题）

## 一、独立核验结果（避免 R7/R9 教训重演）

按 monitor 09-24 负反馈根因（"writer 盲从 critic 指令"），critic 指出的 1 critical + 2 high DOI 死链均经本轮独立 CrossRef / arXiv API / 多源 web 检索三轨核验，全部为真：

| critic 指控 | 本轮独立验证 | 处置 |
|---|---|---|
| [43] arXiv:2505.06275 ID 错挂 | arXiv API journal_ref 字段 = "The 40th Annual AAAI Conference on Artificial Intelligence (AAAI2026)" | 确认为 Zhu SinBasis[34]，非 Blöchl 空芯光纤；按"先验证后处置"原则三源（ORCID 0000-0003-3667-2872 + attoworld.de 全文 PDF + MPI-PKS 出版物页）定位 Blöchl 真身为 Opt. Express 33(13): 28071-28080 (2025) DOI 10.1364/OE.564364 |
| [42] DOI 10.1063/4.0002479 死链 | CrossRef api.crossref.org/works/10.1063/4.0002479 → HTTP 404；真身 10.1063/4.0000270 → HTTP 200；AIP 出版方页面确认 "Cite as: Struct. Dyn. 11, 054303 (2024)" | 改 DOI、页码由 054301 改 054303、补 6 作 Schick |
| [44] DOI 10.1038/s42005-020-00422-5 死链 | CrossRef 404；真身 10.1038/s42005-020-0355-x → HTTP 200，title/作者链/vol 3/article-number 92 全字段匹配 | 改 DOI |

## 二、评审问题处置（三态响应）

| # | 来源 | 严重度 | 处置 |
|---|---|---|---|
| 1 | critic [43] ID 错挂 + 实文已见刊仍标 † | critical | 已修改：arXiv:2505.06275 实为 Zhu SinBasis (AAAI 2026)，非 Blöchl 空芯光纤；改 Blöchl 期刊版 Opt. Express 33(13): 28071-28080 (2025), DOI 10.1364/OE.564364；删 † 标记 |
| 2 | critic [42] DOI 死链 + 页码错 | high | 已修改：DOI 10.1063/4.0002479 → 10.1063/4.0000270；页码 054301 → 054303；补 6 作 Schick |
| 3 | critic [44] DOI 死链 | high | 已修改：DOI 10.1038/s42005-020-00422-5 → 10.1038/s42005-020-0355-x；vol 3, article-number 92（无页码字段，原著录正确） |
| 4 | critic L103 "CrossRef 逐条反查"声明与实况矛盾（假执行） | high | 已修改：本轮修后实跑全量反查——40/40 DOI CrossRef HTTP 200 + 年份匹配、5/5 arXiv API 作者链匹配；按 skill §六.3 "references 专属" 规则将 L103/L105/L107 三段过程性叙述从 references.md 文件迁出 |
| 5 | critic [41]–[45] 增段未经检索验证 | medium | 已修改：本轮经 arXiv API + CrossRef + ORCID + 出版方页面四轨核验；4 条修复结果见上表 1-3，剩 [41] Pupeikis 经 Optica DOI 10.1364/OPTICA.379846 CrossRef 验证为真 |
| 6 | critic 总数 45 超 30–40 上限 5 条 | medium | 部分修改+障碍：rationale/content/scheme 共有 [11][16][24][29][36] 等 5 处对原列表的 [N] 引用；本轮聚焦范围限定 references.md，裁并须同步改三章以保持 [N] 编号一致与跨章指向，违反"只修聚焦章节"约束；留待能同时改三章的轮次处置。本轮显式登记该障碍与裁并候选清单（[24] Zimmermann 2018 与 [27] Ortmann Landsman 综述主题重叠；[29]† Gao arXiv 与 [35] 正式发表版同组同工作重复；[36] Ma CPB 综述与 [27] ROPP 综述重叠） |
| 7 | critic 时效 47% 跌破 50% | medium | 已驳回+依据：本轮实测 27/43 = 62.8%（年份 ≥ 2023）、31/43 = 72.1%（年份 ≥ 2020），远高于 50% 线；critic 47% 表述与 references.md 文本实测不符；保留 62.8% 占比与本条驳回证据 |
| 8 | critic 工作日志污染 | low | 已修改：references.md 文件不再含过程性叙述；本轮修订过程（含本记录）写入 05_review/writer-revision-round-21.md 与 02_literature/reading-notes.md 的标准位置 |

## 三、Round-3 验证封口清单（实测，非声称）

| 检查项 | 结果 |
|---|---|
| DOI 条目数 | 40 条（含 [43] 由 arXiv † 转期刊版） |
| DOI CrossRef HTTP 200 | 40/40 = 100% |
| DOI 年份匹配（claim vs actual） | 40/40 = 100% |
| arXiv † 条目数 | 5 条 |
| arXiv API 作者链匹配 | 5/5 = 100% |
| R2 遗留禁词（2505.06275 / 054301 / s42005-020-00422-5 / 4.0002479） | 0 hit |
| 过程性残留字符串（CrossRef API / arxiv.org/abs / Web of Science / IEEE Xplore / Scopus / DOI 真实性 / arXiv 条目由） | 0 hit |
| 编号连续性 | [1]–[45] 连续无跳号 |
| 近三年占比（年份 ≥ 2023） | 62.8%（27/43），跨过 50% 线 |

## 四、跨章节同步更新

- **00_research_idea.md**：在"最后更新"行下方追加第 10 轮对抗评审修订记录（本轮条），含全部 8 项问题处置与本验证封口清单摘要
- **02_literature/reading-notes.md**：追加 3 条 R10 修订笔记（[42] Jarecki、[43] Blöchl、[44] Fu 的真实版本与修正链）+ 1 条 R10 反查封口笔记
- **方法学手册**：未触动（按 v6.9.60 单一真相源治理，由轮末专职 update_method_manual 步骤统一维护）

## 五、程序自检与 AI 模式

- references.md 文件：句长 MAX < 120 字（DOI 著录体本身短句为主）；零加粗、零 bullet、零元话语、零模板句式、零死板关联词、零"本项目拟/将"句首
- 唯一保留的"过程性"语句是文件首 3 段凡例（† 标识规则、DOI 著录规则、AAAI 会议著录规则），均属"条目内挂钩注释"白名单内容（skill §六.3 允许）
- 文件总长 9210 字节、98 行、45 条文献条目 + 5 行收束段

## 六、未处置项登记

- **裁并至 ≤40 条**：跨章 [N] 引用约束阻碍本轮处置；候选清单见上表第 6 行；待能与三章联动的聚焦轮次处置
- **完整性 0.70**：本轮聚焦严谨性维度（0.55→目标），完整性维度（覆盖全、无缺失引用）本轮已无 P0 残留，0.70→0.85+ 待跨章裁并轮次闭环

