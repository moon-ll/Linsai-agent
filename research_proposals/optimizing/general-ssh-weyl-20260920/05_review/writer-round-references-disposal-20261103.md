# Writer 处置记录（references 轮，2026-11-03）

评审输入：critic-round-1-references.md（6 条问题，critical 0 / high 0 / medium 3 / low 3）
聚焦维度：严谨性（0.88）

## 独立核验（执行情况）

按独立核验纪律，三条文献类指令先行联网核实，全部属实后执行：
- [37] 作者链：arXiv API（2401.12929）返回 11 人全名单，Korolev…Peschel 之后确有 S. Graefe、G. Soavi、D. Kartashov——截断失真成立。
- [10] 首作：CrossRef（10.1103/PhysRevB.99.195428）作者全列 Hannah Jürß; Dieter Bauer——首字母失真成立。
- [15] 题名：arXiv API（2405.16125）原文题名 "…high-harmonic generation in Weyl semimetal TaAs"——"high-order" 失真成立。

## 逐条处置

1. [medium] [37] 作者栏 8/11 截断
   - 已修复。补全为 11 人全名单（+ S. Graefe, G. Soavi, D. Kartashov），经 arXiv API 逐名核实。
   - 状态：已修复。

2. [medium] 41 条超出 20–40 篇上限 1 条
   - 已修复。功能替代论证：[3] Osika（PRX 2017）在正文中仅承担"半经典轨迹解读"与"Berry 曲率核心物理量"两处一句话挂靠（rationale 各 1 处），其论证功能分别由 [2] Vampa 再碰撞句吸收与直接陈述承担；[15] TaAs（Jones 矩阵）深嵌三章节 5+ 处（rationale §2.3、content §2.4、scheme §3.2.2 形参一），承担不可替代的"对称性主导反常偶次谐波"结论，不可裁。
   - 裁撤 [3] 后全稿 41→40 重编号（[4..41]→[3..40]），rationale 两句功能替代改写，content/scheme/full_review 纯重编号。程序断言：正文引用并集 40/40、孤儿 0、幽灵 0、编号连续。
   - 状态：已修复。

3. [medium] 条目内长评注（[16][25][33][34][36][37][41] 旧编号）
   - 已修复。八条评注全部压回一句定位语，实验参数与机制细节归正文论证链（rationale §2.3、content §2.4、scheme §3.2.2/§3.1.2）与 reading-notes。
   - 状态：已修复。

4. [low] [10] 首作 "C. Jürß"
   - 已修复。改 "H. Jürß"，CrossRef 实名核实。
   - 状态：已修复。

5. [low] [15] 题名 "high-order harmonic generation"
   - 已修复。逐字改回 "high-harmonic generation"，arXiv 原文核实。
   - 状态：已修复。

6. [low] 预检解析器区间 token 误报（非申请书缺陷）
   - 无需修改。采纳 critic 结论：[30][31]（旧编号）为实引，不删条；本轮重编号后区间 token 为 [29-30]，已验证展开无孤儿。
   - 状态：不适用（预检误报更正）。

## 历史遗留 P0 核对（本轮状态报告）

- P0-1（rationale [20] You 各向异性 critical，R1 首见）：前轮已修复——当前 rationale/content/scheme/references 中 [20]→现 [19] You 2017 仅承担 MgO 各向异性基准，与 [18] Lorenzo 增强口径（两个数量级、预印本首版/第二版表述）分立无混淆；本轮 grep 全五文件 stale 模式（（v1）/（v2）/v1 摘要/文献刊本/v2 部分计算可达 10³ 等）计数 0。
- P0-2（content ↔ scheme G1 样本各≥200 vs N=100，full_review critical，R1 首见）：前轮已修复——本轮实测 content L17"各不少于 200 个"与 scheme"以 200 为下限"一致，full_review 口径表 N ≥ 200 行同步，无回退。
- P0-3（scheme Δt 时窗 25 vs 30 fs，已解决 R8 起）：scheme §2.2 现"拟合时窗下限取 ≥ 30 fs"，25 fs 仅作裕量说明，维持现状。
- P0-4（rationale 末组文献编号整组错位，已解决 R8 起）：本轮全稿重编号后程序断言编号连续（1–40）、零幽灵，维持。
- P0-5（content [20] 增强上限表述，已解决 R8 起）：现口径统一为 [18]（新编号）"两个数量级"，维持。

## 附：重编号映射与自查数据

- 映射：old 1-2 不变；old [4..41] → new [3..40]（跳过 old 3）。
- 引用统计（token 计数）：rationale 38、content 35、scheme 68、full_review 28；正文实引并集 40/40。
- 条目体例：40 条均有 DOI 或 arXiv 编号；预印本条目在年份后标注"预印本"。
- 头注更新：全文 40 条、三章实引 40、2024–2026 占比 25/40。
- 修改后五文件禁用词/旧口径扫描：全部 0 命中。
