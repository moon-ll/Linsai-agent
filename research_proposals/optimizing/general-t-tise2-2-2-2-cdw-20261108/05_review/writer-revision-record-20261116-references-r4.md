# 修订记录（参考文献专项 · 第 4 轮评审后）

课题：general-t-tise2-2-2-2-cdw-20261108（面上）
对象：sections/references.md（42→40 条），联动 sections/rationale.md、content.md、scheme.md、full_review.md
日期：2026-11-16
评审输入：05_review/critic-round-4-references.md（critical 0 / high 1 / medium 2 / low 2）

## 外部核验方式

- 33 条期刊条目：doi.org 内容协商逐条取题名/卷/页或文章号/年/作者链
- 7 条预印本条目：arXiv 批量 API 取题名、作者链、提交年、journal_ref 与 DOI 字段
- 33 条 DOI 全部取回，卷期页年与首三位作者与条目逐条一致；7 条 arXiv 全部零 journal_ref/doi 残留，无「已刊出未标注」漏项
- 标识符 40 条唯一，无重复

## critic 问题逐条处置

| # | 严重度 | 处置 | 结果 |
|---|---|---|---|
| 1 | high | [30] 题名材料实体错写（1T-TaSe₂→真身 1T-TaS₂）且缺副标题 | 已消除：按 PRL 118, 247401 刊出题名逐字回录，材料实体与副标题均更正。正文引述的 1T-TaS₂ 光致粗化结论本身正确，仅条目错 |
| 2 | medium | [28] 条目滞预印本形却挂刊版 DOI，刊版题名全异 | 已消除：按 npj Comput. Mater. 11, 152 (2025) 刊出题名回录；同时更正首作（真身首作 Pashov，原条目误以 Larsen 为首作） |
| 3 | medium | 预检「32 条虚构风险」口径失真，8 条未回录检索池 | 已缓解：外部核验已逐条替代池内回录（33 DOI + 7 arXiv 全覆盖）；本轮新增条目与四条著录更正均已写入 02_literature/reading-notes.md |
| 4 | low | 42 条超 30–40 上限 2 条 | 已消除：裁 [16][22][34] 三条单次引用且内容可由 [19] 承载的条目，新增 1 条真身条目，最终 40 条，落入 30–40 区间 |
| 5 | low | 章节文件混入处置记录类内容 | 已消除：过程性内容全部写入本文件，sections/ 五文件仅留正文 |

## 评审报告未列出的自主发现（本轮一并修复）

| 严重度 | 问题 | 处置 |
|---|---|---|
| critical | [23] 题名「Excitonic order in quantum materials: fingerprints, platforms and opportunities」含出版方未收录的杜撰副标题（CrossRef 与 Nature 页面均只有前者） | 已消除：删去副标题 |
| critical | content 2.2「介电屏蔽使单层 TiSe₂ 准粒子带隙重整化超过 60 meV」整句挂在 [28]（Pashov 等从头算工作），而该数值出自 Buchberger 等 PRX 15, 041028 (2025) 原文「>60 meV band gap renormalisation」 | 已消除：拆挂——屏蔽重整化改挂新增 [40]，从头算晶格涨落结论改挂 [26] |
| high | [15] 题名截短（真身含材料限定语「in the charge-density-wave material 1T-TiSe₂」） | 已消除：按刊出题名回录 |
| high | rationale §一.1「6–400 K 宽温区」「9 小时内电阻变化不超过 7%」两个数值随 [34] 裁撤失去出处，且 9 小时 7% 无法在证据池核实 | 已消除：改用 [19] 原文口径（300–400 K 逐级升压给出离散电阻台阶、非易失、可经热擦除复原、准对数型慢衰减） |
| high | rationale §一.4 与 full_review 口径表的 EuTe₄ 滞回温区「80–400 K」与 [19] 原文「100–500 K」不一致 | 已消除：两处统一为 100–500 K |
| medium | scheme §三.4「可持续至 650 K 量级、室温 Seebeck 系数超过 500 μV/K、zT 在 460 K 达 0.22」随 [22] 裁撤失去出处 | 已消除：改按 [19] 原文口径表述 |

## 裁撤条目与被承载内容的对应

| 裁撤 | 原挂点 | 承载条目 | 承载依据 |
|---|---|---|---|
| [16] Ning 等（EuTe₄ 双向超快操控） | rationale §一.2 末段 | 整句删除 | 该段主题句「超快操控的目标正在从单一序参量扩展到竞争序的协同」由随后 Kogar 等 [8] 承接，段意完整 |
| [22] Takahashi 等（EuTe₄ 热电） | scheme §三.4 | [19] Lv 等 Nat. Commun. 17, 7123 (2026) | 原文「thermal hysteresis over a broad temperature range of 100–500 K」「nonvolatile」「fully reversible through a thermal erasure procedure」「300 K and 400 K」 |
| [34] Venturini 等（室温忆阻开关） | rationale §一.1 | [19] Lv 等 Nat. Commun. 17, 7123 (2026) | 原文「electrically driven, room-temperature, nonvolatile metastable states」「discrete resistivity plateaus」「multi-bit memory」 |

## 编号变更

裁 [16][22][34] 后全表重排，1–40 连续。新旧对应（正文角标已按新号同步改写，并逐条做「引述内容↔条目主题」语义复核）：
- 旧 [17]→新 [16]、旧 [18]→新 [17]、旧 [19]→新 [18]、旧 [20]→新 [19]、旧 [21]→新 [20]
- 旧 [23]→新 [21]、旧 [24]→新 [22]、旧 [25]→新 [23]、旧 [26]→新 [24]、旧 [27]→新 [25]、旧 [28]→新 [26]
- 旧 [29]→新 [27]、旧 [30]→新 [28]、旧 [31]→新 [29]、旧 [32]→新 [30]、旧 [33]→新 [31]
- 旧 [35]→新 [32]、旧 [36]→新 [33]、旧 [37]→新 [34]、旧 [38]→新 [35]、旧 [39]→新 [36]、旧 [40]→新 [37]、旧 [41]→新 [38]、旧 [42]→新 [39]
- 新 [40] 为本轮新增（Buchberger 等 PRX 15, 041028 (2025)）

## 历史遗留 P0 复核结果（本轮逐条核对）

| 问题 | 归属章节 | 结果 |
|---|---|---|
| rationale §一.2 赝隙相句原错挂 [7]（Grüner 1988） | full_review | 已消除：现挂 [38] = Fragkos 等赝隙相预印本 |
| Dharmasani / Dharmasiri 两版拼写 | content | 已消除：全稿 Dharmasani 零命中，Dharmasiri 3 处一致 |
| 时窗口径（秒级重建 vs ns–μs 主链 vs 飞秒至微秒） | content / scheme | 已消除：三章口径统一，中子 ns–μs 挂在白光飞行时间档、秒级分箱单列 |
| content 2.5 目标二「粗化指数 n 落点」缺主链测点 | full_review | 已消除：n 主链值（关联长度幂律段）与 n 重建段值（超晶格峰畴尺寸演化）双测点已在目标二写明 |
| references.md 0 字节、147 处角标无独立文献表 | content | 已消除：40 条独立文献表落盘，全稿角标↔条目零孤儿零悬空 |
| content 无成果节、年度计划缺失 | content | 已保持现状（2.5 目标二/2.7/2.8 已在章内，见 content.md 结构） |
| full_review 仅目录、缺主线链与口径表 | full_review | 已保持现状（主线论证链 + 跨章节统一口径表均在文件内） |

## 终检结果

- 参考文献表 40 条，编号连续，33 DOI + 7 arXiv 标识符全覆盖且唯一
- 正文↔列表双向零缺失：孤儿 0、悬空 0
- 2024 年及以后文献 28/40 = 70%（标准要求 ≥30%）
- 正文散文超长句（>120 字）0 处（full_review 表格行与章节索引不计）
- 正文修饰词合计 8（上限 12）；禁用词零命中；过程性表达仅「本项目拟」1 处
- 章节文件零工作流残留（轮次编号、内部文件名、审校注记、检索时间戳均未出现）
- 章节文件白名单合规：sections/ 下仍为 rationale/content/scheme/full_review/references 五模块

## 同步更新

- 00_research_idea.md：参考文献条数 42→40，删除 [22] 来源的 650 K/Seebeck/zT 表述，滞回温区改为 100–500 K
- 02_literature/reading-notes.md：新增 arXiv:2506.01470 精读笔记（含 >60 meV 原文定位与错挂拆分说明）、四条著录更正记录；既有条目中的旧编号 [41][42][7] 一并更新为 [38][39]
- 03_method/method-manual.md：本轮未改（方法学手册由专职步骤维护）
