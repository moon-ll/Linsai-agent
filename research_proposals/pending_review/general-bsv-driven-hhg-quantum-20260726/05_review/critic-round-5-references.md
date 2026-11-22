# 参考文献第 5 轮检验报告（general-bsv-driven-hhg-quantum-20260726）

元信息：general ｜ 2026-09-21 ｜ 范围 = references.md 全部 35 条 CrossRef + arXiv export API 双通道全量反查（题名/一作/卷期页/年份四件套比对；编号一致性采信程序预检，未重复核验）。上轮遗留：文件内 round-9 核实声明（L73/L55）本轮实测部分失实，见 #3/#5。

## 全量核查结论
35 条全部真实存在，无虚构条目（相较历史 R7 判例显著进步）。但预检划定的 16 条检索池外"风险区"预判成立：全表共 8 个条目存在元数据失真或状态过期，其中 1 处已渗入正文内联引用。

## 问题清单
[critical]｜[11] L23 及正文 scheme §3.2｜卷期错挂：真实为 PRL 126,137403(2021)；所写 129(17),173001(2022) 经 CrossRef 确认系 Fowler-Wright 极化子论文｜改为 PRL 126(18), 137403 (2021) + DOI 10.1103/PhysRevLett.126.137403；同步订正 scheme §3.2 内联"PRL 129,173001 (2022)"及 L19/L75 归属说明｜action:recalculate
[high]｜[15] L31｜DOI 10.1103/PhysRevResearch.7.043284 经 doi.org 与 CrossRef 双查均 404；PRR 7 卷 043284 实为"He-HHG in gases and solids"他文，系拼装失效号｜删该 DOI 仅留已验真的 arXiv:2505.22536，检索到正式 DOI 后回录检索池｜action:verify
[high]｜[16] L33｜已见刊仍标预印本：arXiv abs 页 journal_ref 与 CrossRef 证实发表于 PRB 109, 035203 (2024)｜改期刊卷期并补 DOI 10.1103/PhysRevB.109.035203，从 L73 预印本声明中移出，年份 2023→2024｜action:verify
[high]｜[22] L45｜一作错位：CrossRef 证实真实一作为 Raissi M.，Karniadakis G. E. 系末作｜作者序改写为 Raissi M., Perdikaris P., Karniadakis G. E.｜action:rewrite
[medium]｜[27] L55｜DOI 留空并自称"核实受限"，实 CrossRef 题名检索即得 10.1038/s41377-024-01381-w（题/作/卷页全合）｜补入该 DOI，删除留空托辞｜action:add
[medium]｜[35] L71｜全表唯一未被正文引用条目（预检确认）｜在 §1.2.2/§2.5 量子路径选择论断处补引，或整条删除｜action:add
[low]｜[30] L61｜L73 声明已知见刊 CPL 43(5),050401(2026)，条目未录真实 DOI｜补 DOI 10.1088/0256-307X/43/5/050401｜action:add
[low]｜[7] L15｜题名转录差异：刊本题为"High harmonic imaging…"非"…spectroscopy"（DOI/作者/jref 均合，同文）｜按刊本题名订正｜action:rewrite
[low]｜[12][13][21]｜其余条目全列作者，此三条"et al."截断，体例不一｜统一为全列或"前三作 + et al."｜action:rewrite

## 引用相关性
35 条均与 BSV-HHG / 固体 HHG / 量子光驱动 / MoS₂ 莫尔 / Mott 关联 / PINN 反演主线相关，未发现无关引用；[21] FAIR、[22] PINN、[23] Roadmap 为数据与 AI 方法支撑引文，属规范用法。

## 数量与时效性
35 条处于 20–40 达标区间；2023–2026 年文献 18/35 = 51.4%（含 [16] 订正后），踩线达标。writer 后续回录检索池时建议优先补 2025–2026 年 BSV-HHG 新文以拉开余量。

## 对抗结论
本轮 9 个问题（critical:1, high:3, medium:2, low:3），波及 8 个条目 + 1 项体例。相比上轮：无虚构为实质进步；但 [11] 卷期错挂已固化进正文内联引用与 L19/L75 双处归属说明，属 writer 把错误卷期"自洽化"的典型半迁移，必须连带正文一并修。是否达到输出标准：否——critical 未清零，writer 修复后 R6 复审验收。

评分依据（独立于评分块）：严谨性 0.72——无虚构条目（利好），但 1 处 critical 卷期错挂渗入正文锚点、3 处 high 元数据失真（失效 DOI/预印本状态过期/一作错位），8/35 条目需修；完整性 0.86——数量、时效、无引用缺口均达标，扣 1 条未引用条目与 2 处真实 DOI 未录。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.72
完整性：0.86
综合评分：0.79
