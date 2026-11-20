# 对抗评审报告（第 8 轮·参考文献专项）

- 项目类型：general（attosecond streaking）；审查对象：references.md（40 条，L3–L81）
- 核验方法：全量反查（非抽查）——34 条 DOI 走 api.crossref.org，6 条 arXiv ID 走 export.arxiv.org；比对题名/作者链/卷期/文章号
- 编号一致性：采信程序预检（40 条 1–40 连续、双向无缺口），本轮不重复

## 核验通过面

- 34/34 DOI 在 Crossref 全部解析成功，题名、卷期、年份、页码/文章号与出版方一致；作者链逐条吻合
- 6/6 arXiv ID（[21][24][29][34][39][40]）在 arXiv export API 全部命中，题名与作者链真实；[21][24] 确无 jref，"未正式发表"注记诚实
- R7 两项 P0 修复完成：[34] 题名已改为真实 SinBasis Networks: Matrix-Equivalent Feature Extraction for Wave-Like Optical Spectrograms（AAAI2026, jref 实存）；[20] DOI 已改为短式 10.1103/ll25-15dm（实解析至 PRL 135,183202）
- 数量 40 ∈ [20,40]；近 3 年（2024–2026）23/40 = 57%，满足 50% 门槛；DOI/arXiv 二选一无缺项；无无关引用
- 作者截断已统一为 3–4 人 + et al.（[35] 由 18 人全列改为 Reinhard J, Wiesner F, Hennecke M, et al.）

## 问题清单

- [medium]｜[18][20][23]（L37/L41/L47）｜R7 medium 标记的"长/短式 DOI 混用"未解决（[20] 改为短式 10.1103/ll25-15dm，但 [18] 10.1103/9jcm-8gd8 与 [23] 10.1103/csvm-858f 同为短式混于长式全表中）｜统一换为出版方标准长式（10.1103/PhysRevA.113.043103 / 10.1103/PhysRevLett.135.183202 / 10.1103/PhysRevAccelBeams.28.074601），或在全表加注"APS 2025 后文章采用短式 DOI 作为正式发布路径"并扩注全部三条
- [medium]｜L83 尾注｜自述"逐条以 Crossref API 与 arXiv export API 反查 DOI/arXiv ID"但仅列举 [20][34] 两条修复挂注,详述强度与声明略不匹配｜尾注改为"本表 34 条 DOI 已逐条经 Crossref API 解析校验、6 条 arXiv ID 已逐条经 arXiv export API 解析校验（详注见 [20][34]）"
- [low]｜[18]（L37）｜作者列表未加 et al.（4 人全列 Kheifets, Serov, Vismarra, Wörner），与全表 27 条 +et al. 截断规则不一致｜加 ", et al." 收尾，与全表统一
- [low]｜[30][31][39]（L61/L63/L79）｜作者列表未加 et al.（4 人全列 Ardana-Lamas/Cousin/Lignieres/Biegert 或 Han/Liang/Liu/Lin），与全表 +et al. 截断规则不一致｜加 ", et al." 收尾，与全表统一

## 锚点对比（[34]）

- 申请书（L69）：Zhu Y, Zhang Z, Zhang R, et al. SinBasis Networks: Matrix-Equivalent Feature Extraction for Wave-Like Optical Spectrograms. arXiv:2505.06275 [cs.LG], 2025（AAAI2026 海报收录；提出 SinBasis 网络框架，将卷积与注意力机制统一改写为权重矩阵上的 sin(·) 元映射，对含 80,000 合成阿秒条纹谱图在内的多类波状图像数据集验证 CNN/ViT/Capsule 三类架构在周期性结构识别与平移鲁棒性上的同步增益）
- 真实记录（arXiv export API 2026-09-23 抓取）：id=2505.06275, title="SinBasis Networks: Matrix-Equivalent Feature Extraction for Wave-Like Optical Spectrograms", authors=[Yuzhou Zhu, Zheng Zhang, Ruyi Zhang, ...], journal_ref="The 40th Annual AAAI Conference on Artificial Intelligence (AAAI2026)", submitted=2025-05-06
- 差距：R7 标记的"真 ID 假题名"已修复为真实题名；正文三处引用须同步核查"四架构比较"等表述是否已按真实内容（卷积/注意力矩阵等价重构 + sin 谱先验）改写或替换（建议 grep "四架构\|四类架构\|CNN、ViT、CNN-ViT、Capsule"）

锚点结论：[34] R7 P0 已修复为真题名 + 真 AAAI2026 出处，但正文论断与真实内容是否同步改写尚未核验（grep 残留风险，属 R8 提示项）

## 维度评分

| 维度 | 权重 | 得分 | 问题数 |
| --- | --- | --- | --- |
| 严谨性 | 0.5 | 0.84 | m2/l2 |
| 完整性 | 0.5 | 0.92 | 无新增缺口 |

评分依据：34 DOI + 6 arXiv 全量反查通过，R7 两项 P0 已修复；本轮严谨性扣分源于 DOI 短/长式混用未解决及尾注自述强度略大；完整性扣分源于 [18][30][31][39] 4 条未统一 +et al. 截断，但不影响可读性与真实性。

## 对抗结论

- 本轮 4 个问题（critical:0, high:0, medium:2, low:2）
- 较历史轮：R7 critical [34] 题名虚构已修复；R7 high [20] DOI 404 已修复；R7 medium [35] 作者截断已修复；R7 medium DOI 混用与 L81 尾注部分修复（[20] 改短式，其余两条未联动）；新增 4 条 +et al. 截断遗漏
- 是否达到输出标准：是——无 P0/红线，40 条文献全部经独立反查验证为真，引用数量与时效性均达标
- 返工优先级：DOI 长/短式统一 → 尾注措辞精确化 → 4 条 +et al. 收尾
- writer 后续轮次应将本轮 Crossref/arXiv 命中回录 02_literature/ 检索池

## 评分
创新性：N/A
可行性：N/A
严谨性：0.84
完整性：0.92
综合评分：0.88