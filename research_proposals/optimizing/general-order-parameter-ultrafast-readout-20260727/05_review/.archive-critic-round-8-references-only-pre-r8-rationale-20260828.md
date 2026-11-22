# 对抗评审报告（第 8 轮，参考文献专项）

## 综合评分
0.55 / 1.00（references-only 评审；不计入写作风格维度）

## 维度评分
| 维度 | 权重 | 得分 | rubric 档位 | 主要短板 |
|---|---|---|---|---|
| 严谨性（rigor） | 0.5 | 0.45 | `scoring_rubric.dimensions.rigor.<0.5`（参考文献缺失/编号不一致） | 正文 [69] 完全失锚；references.md 自陈 "无空号"但 [N] 链存在 21 处空号；同一预印本（Schüle）既被规划 "纯 arXiv 引用"又被正文 [N] 引用 |
| 完整性（completeness） | 0.5 | 0.65 | `scoring_rubric.dimensions.completeness.0.6-0.7`（数量在区间上限、时效性整体合理但有 1 条旧文献边界使用模糊） | 引用总数 40 条超出任务指定 15—30 区间上限约 33%；时效性以 2024—2026 为主占 70 条 / 全部 78 个年份命中——符合"近 3 年充分"，但超导 HHG 三条早期文献年份错位需复核 |

**综合评分 = (0.45 + 0.65) / 2 = 0.55**

## 写作风格评估（必选）
本轮为 references-only 评审，按 SOUL.md "references-only 评审可省略本节"原则跳过 AI 检测与锚点对比，仅保留人工核对章节。

## 锚点对比（必选，缺失则报告无效）
- 申请书原文（rationale.md:35）："Schüle 等人以泵浦—探测 HHG 谱学建立了 MnTe 中 altermagnetic 序参量的亚周期时间分辨探测框架 [69]"
- 申请书原文（rationale.md:83）："MnTe 备选体系的相变温度（Née 温度约 310 K；[69]）"
- 范本（references.md §6 末）："另有 Schüle et al. arXiv:2606.12353 (2025) 在正文中以纯 arXiv 编号形式引用（未使用 [N] 编号），条目信息如下：…"
- 范本（references.md §8）："跨章引用一致性：所有正文 [N] 编号与本节条目一一对应；…无空号、无错位、无未对应编号。节 4 中 [58a]（Leeb arXiv:2501.11328）与 [58b]（Qiu arXiv:2504.06130）为近期新增条目…编号连续性由本节统一维护。"
- 差距：申请书正文用了 [69]，但 references.md 列表未含 [69]；references.md 自言"纯 arXiv 编号"与正文中实际存在的 [69] 互相否定；该工作（Schüle et al. arXiv:2606.12353）在正文三处出现（共 2 处 [69] + §5 §6 §8 中无数次提及"Schüle"），但 references.md §6 的"arXiv 编号引用"承诺从未兑现。
- 档位：`scoring_rubric.dimensions.rigor.<0.5`（核心锚点之一悬空）

## 执行清单对照（必选，references-only 可省略）
references-only 评审，按 SKILL 红队评审规则，本节省。

## 问题清单

### [critical] numbering_inconsistency — 正文 [69] 在参考文献列表中不存在（幽灵引用）

- 位置：rationale.md 第 35 行与第 83 行（共 2 处）
- 问题：
  - rationale.md:35 "Schüle 等人 …[69]，其贡献在于时间维度的引入"
  - rationale.md:83 "MnTe 备选体系的相变温度（Née 温度约 310 K；[69]）"
  - 但 references.md 的全部 [N] 条目只到 [68]，[69] 不存在
  - references.md §6 末尾明确写"Schüle et al. arXiv:2606.12353 (2025) 在正文中以纯 arXiv 编号形式引用（未使用 [N] 编号）"——承诺与正文实际引用 [69] 矛盾
  - references.md §8 自陈"无空号、无错位、无未对应编号"——与本缺陷矛盾
  - 后果：评审专家对照文献表直接判定至少一处"无源引用"，整份申请的方法学可信度受损
- 违反条款：`scoring_rubric.dimensions.rigor` 之"编号一致性"；indicator_red_lines 之"宣称缺乏文献支撑"
- 建议（rewrite，择一即可）：
  1. 正文 [69] 改为"Schüle et al., arXiv:2606.12353 (2025)"纯 arXiv 编号形式（与 references.md §6 注释一致），同时把这条信息合并/补充进 [68] 现有 Qiu 团队合著条目之中——若 Schüle arXiv:2606.12353 就是 Qiu 等人系列的扩展预印本，建议与 [68] 合并条目
  2. 把 [69] 正式加入参考文献列表（§6 末尾将该条目升级为完整 [N] 编号条目），与其他 arXiv 预印本 [62]–[67] 形制保持一致，并修正 §8 "无空号"承诺措辞
  3. 进一步核实 arXiv:2606.12353 这条引用的真实性——若该预印本实际上不存在于 arXiv，则引用本身非法，必须撤除整段论断
- priority：P1 必改
- action：rewrite + verify

### [critical] numbering_gap — 参考文献 [N] 序列出现 21 处空号，与 §8 "无空号" 承诺直接冲突

- 位置：references.md 全文编号
- 问题：references.md 实际编号为 1, 2, 3, 5, 7, 9, 10, 11, 12, 13, 15, 16, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 35, 36, 39, 55, 56, 57, 58, 58a, 58b, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68。空号包括 4, 6, 8, 14, 17, 18, 19, 21, 32, 33, 34, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54（共 21 处）。而 references.md §8 明确声称"无空号、无错位、无未对应编号"——自相矛盾
- 违反条款：`scoring_rubric.dimensions.rigor` 之"完整性"与"编号一致性"；indicator_red_lines 之"章节间逻辑呼应"
- 建议（rewrite）：
  1. 取消 §8 "无空号"承诺，替换为"按主题分组排列，组内允许空号以便后续插入"
  2. 或选择重新连续编号 1—42，剔除所有空号（连同对应的 [58a]/[58b] 一起改为 [38]/[39]）——但这是大改，工作量大
  3. 最低限度修复：把 §8 的"无空号、无错位、无未对应编号"改为"按主题分组排列编号，组内连续，组间存在预留编号以便补充新文献"，保持叙述一致性
- priority：P1 必改
- action：rewrite

### [high] cross_section_inconsistency — 同一篇 Schüle arXiv:2606.12353 在三处用不同编号方案（[69] vs arXiv 编号 vs 承诺）

- 位置：references.md §6 末尾 + §8 + 正文 rationale.md 行 35、行 83
- 问题：
  - references.md §6 末尾说该条目"以纯 arXiv 编号形式引用（未使用 [N] 编号）"
  - references.md §8 又将该条计为"正文以纯 arXiv 编号形式直接引用的预印本 1 条"
  - 但正文实际以 [69] 引用（rationale.md 行 35、行 83）
  - 全文件检索 "arXiv:2606.12353" 仅命中 references.md §6 一次，正文与 content.md/scheme.md 均无该字符串——等于该工作的 arXiv 编号作为"交叉核对线索"已实质丢失
- 违反条款：`scoring_rubric.dimensions.rigor` 之"编号一致性 / 作者信息完整性"
- 建议（rewrite）：
  1. 与上一问题合并处理，统一为方案 A（改正文为纯 arXiv 编号）或方案 B（把 [69] 正式入库）
  2. 选定方案后，把 references.md §6 末尾的"正文交叉核对线索"段落也同步更新
- priority：P1 必改
- action：rewrite

### [high] format_inconsistency — 文献条目格式在三类间不统一（以 §1 之外条目的 arXiv 标注为例）

- 位置：references.md 多处条目
- 问题：正式发表条目一般格式为"作者. 标题. 期刊 卷, 页码 (年份). DOI: …; arXiv: …."。但部分条目格式不一致：
  - [1] Kawakami：缺少卷期页码（仅 *Nat. Photonics* (2020)），无卷号
  - [7] Li & Weng：DOI 字段直接写为 "10.1103/dvy6-r5sr（APS 接受手稿号，正式卷期待发表）"，且 arXiv 编号 2509.08370 标注为 2025 但 arXiv 实际月份（09 月）对应 2025 年——没问题，但 [7] 实际是 2025 年文章，原文写为 "[7] Li, X. & Weng, Z.-Y. … *Phys. Rev. B* (2025). DOI: … ; arXiv:2509.08370"——这是接受但未排卷的格式，与其他正式发表条目不同
  - [14]、[17]、[18]、[19]、[21]、[32]–[34]、[37]、[38]、[40]–[54] 都缺失（即空号之"无内容"），不应出现这种空号与已填条目混杂
- 违反条款：`scoring_rubric.dimensions.rigor` 之"作者、年份、期刊、卷页是否完整"
- 建议（rewrite）：
  1. [1] Kawakami 增补 *Nat. Photonics* 的卷期页码（实为 **14**, 995—1000 之类，可在 Crossref 核对）
  2. [7] Li & Weng 在 DOI 行前明确加注 "accepted manuscript, final pagination pending"，并把作者首字母顺序、ORCID 等按 NSFC 偏好统一
  3. 空号处理：见问题 2 修复方案
- priority：P2 强烈建议
- action：rewrite

### [high] completeness_quantity — 参考文献总数 40 条超出任务指定区间 15—30 上限约 33%

- 位置：references.md 全文
- 问题：本次任务硬约束"参考文献总数是否在 15-30 篇区间（NSFC 面上项目惯例）"，实际总独立编号数 39 条（含 [58a]/[58b] 双编号去重后 40 条）。超出上限 30 条约 33%
- 注意：这是任务指标冲突——NSFC 面上项目的真实惯例是 30—50 条，15—30 区间是本任务的人工约束。但仍需按任务硬约束报告
- 违反条款：`scoring_rubric.dimensions.completeness` 之"引用数量" + 本任务硬约束
- 建议（rewrite 或 verify）：
  1. 方案 A（按任务硬约束）：合并同类预印本与实验组关联条目（如 §6 中 5 条 Mathias 组 [64]/[65]/[66]/[67]/[68] 可保留 2 条核心），降至 25—30 条
  2. 方案 B（按 NSFC 真实惯例）：保留 35—45 条区间，与同行评审预期匹配，并在评审报告中说明 15—30 区间的来源不一致——但本评审无法替申请人做决定
  3. 最低限度：保留所有"正文直接引用"的 39 条不变，把 §6 中 3 条"正文未直接引用"的 [65]/[66]/[68] 删除或移入附录（不计入正文主参考文献表）
- priority：P2 强烈建议
- action：rewrite

### [medium] completeness_aging — 早期文献（2017 年 [2]、2003 年 arXiv 编号用于 [58] 即 Yue/Gaarde 2020 PR A）边界标注需要复核

- 位置：references.md [2]、[23]、[58]
- 问题：
  - [2] Matsunaga 2017（NbN Higgs mode）：作为超导背景对照尚可，但 2017 年文献距今 9 年，时效性一般
  - [23] Takayoshi 2019（PRB 99, 184303）：磁性 HHG 一般理论基础，距今 7 年
  - [58] Yue & Gaarde 2020 PRA 102, 013119：SBE 规范基础文献，距今 6 年——这是方法学经典，2017 / 2019 / 2020 三条可保留
  - 但其任务约束"是否包含近 3 年（2023—2026）的文献"——三条 ≥ 3 年的文献需要给出"经典方法学锚点"的明确说明，否则会被评审专家质疑时效性
- 违反条款：`scoring_rubric.dimensions.completeness` 之"时效性"
- 建议：references.md §8 已承诺"正式发表 20 条，预印本 22 条"——建议在 §8 增列"时效性说明"，明确指出 2017/2019/2020 三条作为方法学经典锚点的角色（与 §1 注释一致，本节已隐含说明，但更明确陈述一句可强化）
- priority：P3 建议
- action：rewrite

### [medium] completeness_unused — references.md 自陈 3 条预印本 [65]/[66]/[68] 正文未直接引用，列入正文交叉核对

- 位置：references.md §6 末尾与 §8
- 问题：references.md 自己承认 [65]、[66]、[68] 三条"正文未直接引用但与 [24] Werner 2024 框架互补"。然而 NSFC 评审一般把参考文献区分为"正文直接引用"和"补充参考"两类。如果把所有条目都纳入同一编号体系而不区分，会让审阅人误以为它们在正文有支撑，进而质疑"虚假引用"
- 验证：在 content.md 行 29、rationale.md 行 39、rationale.md 行 33 三处确实出现了 [65]/[66]/[68] 引用——即实际正文有引用，与 §6/§8 注释"正文未直接引用"矛盾
- 违反条款：`scoring_rubric.dimensions.rigor` 之"编号一致性 / 自我声明一致性"
- 建议（rewrite）：
  1. §6 / §8 的"正文未直接引用"声明要么删除，要么改为"正文以 arXiv + [N] 编号形式交叉引用"——前者更稳妥
  2. 在 §6 末尾说明清楚 [65]/[66]/[68] 在正文的具体出现位置（如 "rationale.md 行 39"）
- priority：P2 强烈建议
- action：rewrite

### [medium] cross_section_duplication — 同一作者群（Schüle）出现至少两次不同角色引用

- 位置：references.md [68] + references.md §6 末尾 "Schüle et al. arXiv:2606.12353"
- 问题：[68] Qiu 等人合著者中已含 "Schüle, K. U."；§6 末尾又有独立的 "Schüle et al. arXiv:2606.12353 (2025)"。若 [68] Qiu arXiv:2508.16166 与 Schüle arXiv:2606.12353 实际是同一工作的不同编号，需要在 references.md 中做出归并说明
- 违反条款：`scoring_rubric.dimensions.rigor` 之"作者信息完整性"
- 建议（research + rewrite）：
  1. 申请人查 arXiv:2606.12353 与 arXiv:2508.16166 关系
  2. 若不同，归一；若相同，删 Schüle arXiv:2606.12353 独立条目并在 [68] Qiu 加注
- priority：P3 建议
- action：research

### [low] format_minor — DOI 写法、Hugeness 简写、"et al." 用法需统一

- 位置：references.md 全文条目
- 问题：
  - 部分条目的作者列表用 "et al." 简写（如 [1]、[27]、[28]、[30]、[31]、[55]、[56]、[57]）而其他条目用全作者列表。这是国际惯例，但 NSFC 部分评审偏爱"超过 3 个作者时用 et al."的一致规则
  - 部分预印本条目缺 DOI（如 [9]、[13]、[27]、[28]、[29]、[30]、[31]、[35]、[36]、[55]、[56]、[57]、[58a]、[58b]、[61]、[62]–[68] 全部），符合 arXiv 预印本实际——但[10]、[11]、[12] 三条同时给出 DOI 与 arXiv，格式与缺 DOI 的预印本条目不一致
- 违反条款：`scoring_rubric.dimensions.rigor` 之"引文格式统一性"
- 建议：保持"无 DOI 即不写 DOI"规则，对已发表预印本同时给 DOI 与 arXiv 编号保持现有规则即可；统一"et al." 用法（建议全部条目统一，超过 3 个作者即 et al.）
- priority：P3 建议
- action：rewrite

### [low] completeness_review — 综述引用仅 1 条（[39] Li 2023），缺国内综述补充

- 位置：references.md §7
- 问题：综述只 1 条（国内 Li/Lan/Lu 2023）。NSFC 评审有时希望见到 ≥ 2 条综述以体现"领域图景全面"。但本项目本身是聚焦 altermagnet HHG，综述 1 条合理
- 建议：保留 1 条即可，无需修改
- priority：P3 建议（仅为提示，不扣分）

## 对抗结论

- 本轮 10 个问题（critical:2, high:3, medium:4, low:2）
- 相比上一轮（典型上一轮常见为格式 / aging，本次最严重为编号一致性与承诺一致性）
- **核心瓶颈：references.md §6/§8 与正文 rationale.md 之间对 [69] / Schüle arXiv:2606.12353 的处理存在三向矛盾**——这是评审红线级缺陷，P1 必改
- 次瓶颈：参考文献序号空号 21 处与"无空号"承诺直接冲突，连同 [69] 幽灵引用，构成"评审红线 + 自陈一致性破坏"双重扣分
- 综合评估：参考文献严谨性显著不足，完整性有较强时效性但总数超标
- 是否达标：**否**。两份 critical 问题未解决前不可提交

## 评分
创新性：N/A
可行性：N/A
严谨性：0.45
完整性：0.65
综合评分：0.55
