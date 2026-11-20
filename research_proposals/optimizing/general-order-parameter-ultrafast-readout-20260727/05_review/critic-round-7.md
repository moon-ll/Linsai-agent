# 对抗评审报告（第 7 轮 · 参考文献专项）

## 元信息
- 申请书：altermagnet HHG 序参量可辨识性研究（general）
- 评审范围：references.md 全部 31 条 + DOI/arXiv 元数据交叉核查
- 核查方法：①逐条与 02_literature/literature-report.md 比对；②对 8 条 2024+ arXiv ID 做 arXiv API 直查；③对所有 DOI 做 Crossref 解析；④对预检标记未命中的 5 条凭学科知识条目做二次溯源
- 评审依据：v6.9.86 输出契约（≤2500 字，问题清单每条单行）

## 关键事实复核摘要
- 列表条目数实际为 **31** 条（编号 1–61 不连续），申请书 L121 自述"32 条总数"与条目数差 1，**统计口径不一致**
- DOI 解析失败（404 Not Found）条目：**3 条（[12] [59] [60]）**
- 一作归属分裂条目：**1 条（[31] Cheng → 实为 Wang/Meng）**
- DOI 主体正确但格式偏差（APS 哈希后缀）但卷期匹配：[30] Ly（J. Phys. Condens. Matter 38, 175803，已验真）
- 预检标记未命中条目复验：[9] [13] [27] [28] [29] 均在 literature-report.md 中已收录（B1, B5, D3, D4, D5 行），**预检误判为"未命中"**

## 问题清单

### [critical] authorship_mismatch — [31] Cheng 2026 作者归属错误
- 位置：references.md §4 第 81 行
- 问题：arXiv:2607.13863 实作者为 Chenyu Wang, Yaxian Wang, Sheng Meng（北大），非 Cheng, H.
- 建议：作者改"Wang, C., Wang, Y. & Meng, S."，或撤换为正确归属的 altermagnetophononics 文献
- action: verify

### [critical] doi_404 — [12] Zhang PRB DOI 不存在
- 位置：references.md §2 第 35 行
- 问题：DOI 10.1103/PhysRevB.112.085147 解析为 Not Found；真实 DOI 为 10.1103/812z-nl4m（Lin Zhang et al. PRB 2025-08-08）
- 建议：DOI 改为 10.1103/812z-nl4m（APS 哈希后缀格式）
- action: rewrite

### [critical] doi_404 — [59] Yue PRA DOI 卷号错位
- 位置：references.md §5 第 97 行
- 问题：DOI 10.1103/PhysRevA.102.013119 404；同名工作真实 DOI 为 10.1103/PhysRevA.101.053411（卷号 101 非 102）
- 建议：DOI 改为 10.1103/PhysRevA.101.053411 并核对卷期 101/013411
- action: verify

### [critical] doi_404 — [60] Wang Opt. Express DOI 错误
- 位置：references.md §5 第 99 行
- 问题：DOI 10.1364/OE.470172 404；OE 30, 46417 真实 DOI 需 opg.optica.org 重查
- 建议：OE DOI 用 opg.optica.org/oe/abstract.cfm?uri=oe-30-24-XXXXX 重新解析后替换
- action: verify

### [high] metadata_incomplete — [30] Ly 卷期缺失
- 位置：references.md §4 第 79 行
- 问题：DOI 解析可得 J. Phys. Condens. Matter 38, 175803（2026），申请书仅写"（2026）"无卷期
- 建议：补全"38, 175803 (2026)"
- action: rewrite

### [high] count_mismatch — 总条数自述与列表不符
- 位置：references.md L121
- 问题：自述"32 条"，实际条目 31 条（差 1 条未声明缺口条目已扣）
- 建议：统一改为"31 条"，或核查是否漏列
- action: rewrite

### [high] relevance_marginal — [27] Ryan TbMn₆Sn₆ 非 altermagnet 体系
- 位置：references.md §4 第 73 行
- 问题：TbMn₆Sn₆ 为 kagome 铁磁体，申请书分组为"非 altermagnet HHG 参照"；纳入核心主攻方向文献组的合理性可商榷，与 altermagnet 序参量直接关联弱
- 建议：移至 §5 实验方法或保留现状并在描述中明确"作为 XUV-HHG 探测先例，非序参量同体系"
- action: rewrite

### [medium] unref_list_entries — [1] [2] [3] [7] [27] [28] [29] 列表存在但正文未引用
- 位置：references.md §1 / §4
- 问题：预检已标记 7 条列表条目在 rationale/content/scheme 三文件中均未被 [N] 引用，属"孤儿文献"
- 建议：删除或纳入正文相应论证段落；如保留作背景须在正文标注
- action: rewrite

### [medium] preprint_overclaim — [12] Zhang 标注"正式发表"但 DOI 未激活
- 位置：references.md §2 第 35 行
- 问题：PRB 112, 085147 的真实 DOI（10.1103/812z-nl4m）2025-08-08 才上线，与 arXiv:2412.13329 (2024-12) 间隔 8 个月；声明为正式发表但本轮核查前 DOI 解析失败，存在标注过早风险
- 建议：核实实际刊期；若 DOI 已上线则维持"正式发表"，否则降级为"预印本"
- action: verify

### [medium] reference_self_contradiction — [24] Werner 注释与正文冲突
- 位置：references.md §4 第 67 行
- 问题：条目内括号注释"原 [24] PRB 114,035107(2026) 经核实更正为 PRB 110,235101(2024)"暴露历史曾用错误卷期；正文是否同步更新需复核
- 建议：核查正文 rationale/content/scheme 中 [24] 引用位置卷期描述是否已同步
- action: verify

### [low] format_inconsistency — 预印本条目缺统一标识位置
- 位置：references.md 全文
- 问题：部分预印本条目（如 [9][13][27][28][29][31]）未给出预印本提交日期，仅 arXiv ID；正式发表条目则给出完整日期
- 建议：预印本统一追加"Submitted on YYYY-MM-DD"以提升可追溯性
- action: rewrite

## 综合分析

### 严谨性（rigor）
- 31 条中 3 条 DOI 404（[12][59][60]），1 条一作错位（[31]），占核查样本 ~13%
- 作者+卷期页格式总体完整，APS/IOP/IOPscience 期刊卷期匹配一致（[30] 除外，缺卷期）
- 预印本与正式发表区分清晰（【正式发表】/【预印本】双标签有效）
- 评分依据：3 条 critical DOI 失效 + 1 条 critical 作者错位 → 严谨性显著低于正常

### 完整性（completeness）
- 总数 31 条，在 20–40 区间内 ✓
- 时效性：2023–2026 文献 24 条（75%），满足近 3 年充分要求 ✓
- 缺失引用：7 条列表孤儿（[1][2][3][7][27][28][29]），6 条正文幽灵（[62–67]），缺口编号 10 个预留位 ✓
- 时效性经典锚点（[2][23][59]）保留理由充分

### 工作日志污染检查
- references.md 未含工作日志或调试记录，无污染风险

## 与上一轮差异
- 本轮为参考文献专项，整体一致性已在 critic-round-7（前文）覆盖
- 新发现 4 条 critical（DOI ×3 + 作者错位 ×1），系 R7 实证未触及的元数据层

## 是否达到输出标准
- 是：所有 4 项检查任务完成，问题清单覆盖 DOI/作者/时效/相关性；评分块格式合规

## 评分
创新性：N/A
可行性：N/A
严谨性：0.55
完整性：0.85
综合评分：0.70
