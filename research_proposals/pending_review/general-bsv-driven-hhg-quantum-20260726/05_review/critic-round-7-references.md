# 对抗评审报告（第 7 轮）— 参考文献

## 综合评分
0.725 / 1.00

## 维度评分
| 维度 | 权重 | 得分 | 问题数 |
| --- | --- | --- | --- |
| 严谨性 | 0.5 | 0.65 | 4 critical/high |
| 完整性 | 0.5 | 0.80 | 2 high + 2 medium + 1 low |
| 创新性 | — | N/A | — |
| 可行性 | — | N/A | — |

## 核查方法
CrossRef API 全量核查 19/35 条 DOI；arXiv API 核查 [3][4][13][23][33][34][35] 等条目元数据；
聚焦 [9][11][15][18][28][29][30][31][32][35] 等 2024-2026 最新条目逐条比对作者-卷-期-页；
正文 grep 验证 [36] 引用、[3]/[22] 引用情况。

## 问题清单

### CRITICAL
- [critical]｜references.md 列表｜正文 rationale.md 段 4 引用 [36]，但文献列表只有 1–35｜新增 [36] 条目或在正文删除 [36] 引用
- [critical]｜[11] Li A. et al. 元数据｜条目写 PRL 126(18)，CrossRef 实为 PRL 126 issue 13 (2021-04-02)｜issue 改 13
- [critical]｜[35] Wang F. 元数据｜条目称"第一完成单位为武汉理工大学"，CrossRef 实为 Wuhan Institute of Technology (武汉工学院/WIT) ≠ 武汉理工大学 (WUT)｜改"武汉工学院"或核对作者主页

### HIGH
- [high]｜[3] Spasibko OE 20 7507 (2012)｜列表有，正文三章 0 引用（孤儿）｜补引用或撤条目
- [high]｜[22] Raissi PINN JCP 378 (2019)｜列表有，正文三章 0 引用（孤儿）｜§2.1/§3.4 实有方法学需求，应补引用
- [high]｜[10][11][13][14][15][17][18][33][34][35]｜10 条使用 "et al." 截断，与详列全作者的 [1][2][5][8][9][26][27][28][29] 等格式不统一｜统一为详列所有作者或统一为 "et al."

### MEDIUM
- [medium]｜条目卷页格式｜范围页有的用连字符 "1960-1965" 有的用 en-dash "7507–7515"；文章号 "033079" 单列 vs 范围写法混用｜统一用 en-dash + 范围写法
- [medium]｜预印本标识｜[13][23][33][34] 未加"arXiv preprint"字样，与正式刊条目区分弱｜加 "arXiv preprint" 前缀

### LOW
- [low]｜[21] FAIR Guiding Principles｜边缘相关（数据管理通用原则），与 BSV-HHG 科学问题无直接连接｜保留可，标注"§2.6/§3.8 数据管理"
- [low]｜[25] Luu Berry 2018｜Vol 9 article 916，条目写"Nature Communications 9, 916"格式正确；但条目全 35 条内未单独抽"9 (2018)" year 标注散落｜统一年份位置
- [low]｜总体时效性｜2024-2026 文献 17/35=49%，达优秀档｜保留

## 工作日志污染核查
05_review 目录现有 critic-round-1..10 + 全评审系列文件，存在工作日志与本报告混放；本报告独立命名 critic-round-7-references.md 不需迁移。

## 预检项采信记录
- 编号一致性：34 个正文引用标记 vs 35 条目，正文 [36] 悬挂、[3][22] 孤儿已纳入上述清单
- 来源校验：本轮对 15 条未本地检索的 DOI/arXiv 全部通过 CrossRef/arXiv 实查，其中 [35] 单位名称为新发现事实错位

## 核查未发现问题的条目（已 CrossRef/arXiv 确认真身）
[1][2][4][5][6][7][8][9][10][12][13][14][15][16][17][18][19][20][21][22][24][25][26][27][28][29][30][31][32][33][34][35] 全部实存；其中 [13][15][23][33][34] 标注为预印本属实。

## 锚点对比三步法
1. 申请书典型句：[11] "Li A., et al. Quantum interference visibility spectroscopy in two-color photoemission from tungsten needle tips. Physical Review Letters 126(18), 137403 (2021). DOI: 10.1103/PhysRevLett.126.137403; arXiv: 2205.11161."
2. CrossRef 实据：issue 13 (2021-04-02)，arXiv 2205.11161 标注 journal_ref "Phys. Rev. Lett. 126, 137403 (2021)" 与 DOI 完全匹配，作者列表 Ang Li/Yiming Pan/Philip Dienstbier/Peter Hommelhoff。
3. 差距：issue 字段 18→13 的事实错位；arXiv 编号与正式刊 DOI 一一对应验证为真。改写方向：直接修正 issue 字段；保留 arXiv 与 DOI 双锚。

## 对抗结论
- 本轮发现 9 个问题（critical:3, high:3, medium:2, low:1）
- 相比上一轮：上轮 R6 未单做参考文献核查；本轮新发现 [36] 悬挂、[11] issue、[35] 单位事实错位三条 P0
- 是否达到输出标准：未达——[36] 悬挂为悬挂引用 P0 红线，需 writer 修复后才能进入下一轮

## 评分
创新性：N/A
可行性：N/A
严谨性：0.65
完整性：0.80
综合评分：0.725