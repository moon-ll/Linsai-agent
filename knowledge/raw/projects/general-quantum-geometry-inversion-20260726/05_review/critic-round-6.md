# 参考文献专项检验报告（第 6 轮 · references.md）

元信息：general-quantum-geometry-inversion-20260726｜general（面上）｜2026-09-15｜对象：04_proposal/sections/references.md（51 条全文通读）｜编号一致性由程序预检完成，采信未复核｜同轮号旧档 critic-round-6.md（整体一致性线）已归档为 critic-round-6-archive-overall-20260915.md

## 核验方法与真实性结论
全量反查（不止预检 32 条优先批）：38 条 DOI 逐条 CrossRef API 比对标题/一作/年份/卷号（MathML 记录已剥离再比，[43] 初判相似度 0.66 系此伪警）；18 条 arXiv 经 abs 页/Semantic Scholar 反查（arXiv API 直连被 reset，改 web 通道）；[21] 由 Semantic Scholar 收录页定位验真。
结论：51 条全部真实存在，无虚构条目、幽灵 DOI、作者错位、近似重复（标题去重扫描 0 命中）。预检标记的 32 条"凭学科知识引用"区经逐条外部核查无一虚构，虚构风险本轮排除。唯一实质失真为 [13] 标题（见清单）。
时效性：2024–2026 文献 28/51（55%）达标；引用相关性抽验（[24] Fisher 信息→R2 判据、[28] FAIR→数据管理、[23] Yang 综述→量子几何计量）均对应正文实际语境，无不相关引用。

## 问题清单
[high]｜[13] L27｜列表题"HHG during ultrafast melting of a Mott insulating state"≠arXiv v1 原题"…reflecting the sub-cycle evolution of the Mott transition under a mid-infrared electric field"，且 CrossRef 查无此题刊出版｜替换为 v1 原题；如已有刊版补真实卷期｜verify
[high]｜全文 L3–L107｜总条数 51 超出 20–40 区间（预检"超出区间"）｜裁并同组近重复文献（Lange/Madsen 系 [16][20][45]、Vampa 系 [1][3]）压至 ≤40｜remove
[medium]｜[1] L3｜Vampa 2015 正文零引用（预检：仅此条列表存在未引用）｜在气-固 HHG 联结语境补引或随裁并删除｜add
[medium]｜[47] L97｜"Ilin, D. et al."作者链不完整，全表唯一截断且系预印本无版面限制｜补全作者名单｜rewrite
[medium]｜[46] L95｜arXiv:2510.22064 已见刊（DOI 10.1103/sxcl-yqs7）仍按预印本引用｜更新为刊出版信息｜verify
[medium]｜[15][43][44][49][50]｜DOI 与 arXiv 双标识并存，违反"DOI/arXiv 二选一"统一口径｜保留 DOI 删 arXiv 尾注｜rewrite
[low]｜[23] L47｜DOI 置于题名之前，字段顺序异于全表｜移至题名后统一｜rewrite
[low]｜[6][28][42]｜et al. 截断（Nature 系惯例，可接受）｜如求全表统一可补前 10 作者｜rewrite

工作日志污染：预检未标膨胀告警；sections/ 四文件正则实测 0 命中，不立案。

## 维度评分
严谨性 0.84：51 条全真、作者链完整度高；扣 [13] 标题失真及 5 条双标识/[47] 截断/[23] 字段序。
完整性 0.75：51 条超区间、[1] 未引用、[46] 刊版滞后、预印本占 13/51（25%）偏高；时效性 55% 达标不扣。

## 锚点对比
申请书 [43]（L88）：Zhang, L., Tyulnev, I., … Lewenstein, M. PRB 112, 085147 (2025) + DOI 10.1103/812z-nl4m + arXiv:2412.13329。
外部记录（arXiv 2412.13329 v2 + CrossRef）：同题（TiSe₂ CDW 各向异性）、同作者链、vol 112 / art 085147 / 2025 全符。
差距：五件套零差距；仅"DOI+arXiv 双标识"与全表口径不一。
锚点结论：[43] 五件套（题名/一作/刊/卷期/年）与外部记录逐字一致。

## 对抗结论
本轮 8 个问题（critical:0, high:2, medium:4, low:2）。风险性质已从 R7 时代的"虚构条目"退坡为"元数据精度与体量控制"：无 critical，文献底盘真实可靠；[13] 标题失真须当轮验收；51→≤40 裁并、[1] 处置、[46] 刊版更新为 writer 下轮必办，新增文献须同步回录 02_literature 检索池。high 清零后本表可达可提交状态。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.84
完整性：0.75
综合评分：0.80
