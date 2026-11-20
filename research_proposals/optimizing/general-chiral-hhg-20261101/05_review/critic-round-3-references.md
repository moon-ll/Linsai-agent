<!-- round-3-provenance -->
## 评审版本存证（程序化，round-3 同版本复核）
- 被评文件：`04_proposal/sections/references.md`
- 评前 sha256：`c3e21dda0c4152fb96a9663aff4155842b27beef213c467b1741de5627a97e6a`
- 评前 mtime：2026-11-06T00:24:27
- 评后复核 sha256：`c3e21dda0c4152fb96a9663aff4155842b27beef213c467b1741de5627a97e6a`（一致）
- 存证写入时间：2026-11-06T01:16:24

# 对抗评审报告（第 3 轮 · 参考文献专项）

项目类型：general｜日期：2026-11-06｜范围：references.md 41 条全量（85 行实读）
核验声明：本轮实读全文 41 条。22 条 DOI 条目经 CrossRef API 逐条字段级反查（题名/刊名/卷/页/文章号/首作者/作者序/刊版年份）；19 条 arXiv 条目经 arXiv Atom API 批量反查（题名全串相似度 + 首作姓 + 作者序 + 发布年月 + journal_ref/doi 字段）；[16][30][32] 另经 nature.com 文章页与 abs 页交叉定案。预检编号一致性结论直接采信，未重复核对。

## 综合评分
0.85 / 1.00（严谨性与完整性均值）

## 维度评分
维度｜权重｜得分｜问题数
严谨性｜0.50｜0.83｜5
完整性｜0.50｜0.87｜4

## 核验结论总览
- 虚构检测：41 条零虚构。22 条 DOI 条目 CrossRef 全部命中唯一记录，题名逐字全对，刊名/卷/页/文章号/首作/作者序全对；19 条 arXiv 条目题名、首作姓、作者数、发布年与 arXiv 记录全对，arXiv ID 段年月（YYMM）与 API 发布年月 19/19 一致。预检点名 12 条"未在检索池命中"条目经检索池全文 grep 与 CrossRef/arXiv 双证全部为真引（[1][4][9][14][17][29][33][35][36][37][38][40]）；检索池 grep 显示 19 条 arXiv 条目 ID 全部命中 reading-notes.md，10 条 DOI 条目在池内以题名/年份形态存在，预检告警为标识符形态差异而非虚构。
- 格式统一性：41/41 条有可溯源标识符（22 DOI + 19 arXiv），无一条缺标识符。折著规则"作者总数超过三人时列前三人并加 et al."逐条对表 40/41 合规（仅 [16] 例外）。
- 数量：41 条，超 20-40 上限 1 条（预检膨胀告警属实）。
- 时效：2023 年及以后 29 条（70.7%），其中 2026 年 19 条、2025 年 4 条，时效性优；早于 2020 年 9 条均为该领域奠基工作。
- 相关性：41/41 均在正文承载具体论断（含量级/频率/机理），零无关引用。
- 工作日志污染：对 04_proposal/sections/ 全目录 grep"轮/工作日志/本轮核验/遗留/裁撤/待补充/TBD/占位"族，仅命中物理表述"按未完成分离处理"与"主论文"等非日志语，不立案；本项无污染。

## 问题清单
[medium]｜[16] 括注｜"该文即 arXiv:2004.05191 正式发表版"失据：NC 12,3951 与 arXiv《Polarization of chirality》为两篇独立工作，前者摘要不提 arXiv ID｜删该括注，改注"同组概念论文 arXiv:2004.05191 另列"
[medium]｜[16] 作者｜5 位作者全列，违头注"超三人列前三加 et al."｜改"A. Ayuso, A. F. Ordonez, P. Decleva, et al."
[medium]｜全表 11 条纯 arXiv｜[5][12][18][23][25][26][27][31][34][39][41] 缺"（预印本）"标注，仅 [19][20][21][28] 有，体例互斥｜11 条统一补"（预印本，未见刊）"
[medium]｜[6][8][10][30][32][36] 刊名｜Nature 系四刊混用全称与缩写（Nature Physics/Nat. Photonics/Nature Materials/Nat. Commun.）｜全表统一为 Nature 系全称或 Nat. 缩写一套
[low]｜references 头注 vs 41 条｜总数超 20-40 上限 1 条，头注无裁撤说明｜裁 1 条弱关联条目或注明超限理由
[low]｜[32] 作者序｜二三作与 arXiv 序相反（arXiv: Grimes-Allington-Ueda；CR/条目: Grimes-Ueda-Allington）｜以 CR 刊版序为准可保留，加注"CR 刊版作者序"
[low]｜[13][22][24]｜APS 短码 DOI（fytr-8vtm/xcfl-mqpg/cpfx-c9h9）与全表长码体例不一｜注明短码为 CrossRef 唯一注册形

## 锚点对比
申请书原文（references L35，[16] 括注）："D. Ayuso, A. F. Ordonez, P. Decleva, M. Ivanov, O. Smirnova, Enantio-sensitive unidirectional light bending, Nat. Commun. 12, 3951 (2021). DOI: 10.1038/s41467-021-24118-4（该文即 arXiv:2004.05191 所载 chirality polarization 概念工作的正式发表版）."

CrossRef 权威记录（10.1038/s41467-021-24118-4）：题名"Enantio-sensitive unidirectional light bending"，作者 Ayuso/Ordonez/Decleva/Ivanov/Smirnova，Nat. Commun. 12, 3951，2021-06-24，relation 字段为空。

arXiv:2004.05191 实况：题名"Polarization of chirality"，2020-04-10 提交，5 作者同名序，abs 页 journal_ref 与 doi 字段均为 None。摘要主张"chiral dichroism in emission direction reaches its highest possible value of 200%"，主题为手性偶极/多极与手性偏振概念。nature.com 刊版正文全文检索不到字符串"2004.05191"，且该刊版自述"Our work introduces the concepts of polarization of chirality"——即 NC 论文是引入并应用该概念的后续工作，而非 arXiv 预印本的发表版。

差距：条目把"概念论文→应用论文"的后续承接关系写成"同一篇的正式发表版"，属工作同一性误判。二者虽共享作者群与概念内核，但题名、核心结论与实验内容不同（前者手性偏振概念+200% 圆二色，后者对映敏感干涉仪+单向弯折）。所幸正文 rationale L27 引用的"圆二色可达 200%"在 NC 刊版正文中确有对应表述（CD(β) 达 200% 上限），故实质论断的溯源成立，失据仅限条目括注本身。同一括注的作者列示（5 人全列）另违头注折著规则。

## 对抗结论
- 本轮发现 7 个问题（critical:0, high:0, medium:4, low:3）
- 相比 R2：R2 的 1 条 high（rationale L29/L37 的 PI-MOCD 20% 失据）经本轮实读 rationale L33/L41 复核已修复——20% 量级表述已删除，改为 Berry 几何起源的定性论述；R2 的 4 条 medium 中，[30] 题名尾句已按 CrossRef 注册形逐字补录并加括注 arXiv:1401.4101（已修复）、期刊缩写体例未修（延续，[6][8][10][30][32][36] 六条仍混用）、预印本号保留规则已统一（已修复，[22][30][32] 三条见刊条目一律括注预印本）、条目数 41 条与"20-40 篇"上限冲突未裁（延续）。
- R1 的 12 个问题（3 high + 7 medium + 2 low）经三轮逐条复核全部修复：页码、题名、标识符、折著声明、刊版回录五项均已落实，41 条零虚构。
- 新增本轮问题：4 个（[16] 括注同一性误判、[16] 折著违规、11 条预印本标注缺失、Nature 系刊名混用），均为一行可修。
- 未解决遗留：1 条（条目数 41 超上限 1 条，连续三轮未裁）
- 是否达到输出标准：是——零虚构、零 high，7 个问题均为 medium/low 且可一行修复
- 返工优先级：先删/改 [16] 的 arXiv 同一性括注（唯一涉及文献同一性判断的条目）→ [16] 补 et al. → 11 条补"（预印本）" → 统一 Nature 系刊名体例 → 裁 1 条或声明超限理由
- 下一轮建议：writer 完成上述 4 项 medium 后，核其修改是否波及正文角标与 rationale L27 的 200% 表述；条目数若仍为 41 条须给出具名可裁条目，否则数量项从 medium 升级 high

## 评分
创新性：N/A
可行性：N/A
严谨性：0.83
完整性：0.87
综合评分：0.85
