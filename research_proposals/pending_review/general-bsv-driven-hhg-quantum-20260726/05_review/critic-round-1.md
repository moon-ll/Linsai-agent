# 参考文献检验报告（第 1 轮）
项目：general-bsv-driven-hhg-quantum-20260726｜类型：general（面上）｜聚焦：references.md｜日期：2026-09-09
方法：33/33 条全量 CrossRef + arXiv API 反查（含预检 16 条凭记忆条目，未抽查）；编号一致性采信预检。旧 critic-round-1.md（整体一致性轮）已归档为 .archive-critic-round-1-pre-referencesline2-20260909.md。

## 四项检查结论
1 格式：22 条含 DOI、24 条含 arXiv，其中 13 条双标违反"二选一"；5 条 et al. 与全列风格并存；2 条 APS 代号式 DOI。
2 相关性：31/33 条紧扣 BSV/量子光驱动固体 HHG 主题；[20] FAIR 疑无关，[21] PINN 视方案而定。
3 缺失引用：预检双向无缺口（正文 33 ↔ 列表 33），采信，无幽灵编号。
4 数量时效：33 条在 20-40 区间达标；2023-2026 文献 16 条 = 48.5%，略低于 50% 基准。

## 问题清单
[critical]｜[13] L27｜一作后 15 位作者虚构：真名单 Xu/Wang Q./Chu 等 23 人，Register/Tutuc/Hennig/Shan 等不在文中｜rewrite:按 arXiv 真名单重列，可前 6 人 + et al.
[critical]｜[21] L43｜一作错置+4 人虚构：真作仅 Raissi/Perdikaris/Karniadakis 3 人，Kevrekidis/Lu/Wang/Yang 不在文中｜rewrite:改为 Raissi M., Perdikaris P., Karniadakis G. E.
[high]｜[11] L23｜标题意译+漏正式发表：已刊 PRL 126, 137403 (2021)，真题为 …visibility spectroscopy…needle tips｜verify:改逐字真题并补 DOI 10.1103/PhysRevLett.126.137403
[high]｜[7] L15｜标题关键词错：真题 "High harmonic imaging of…" 非 "high-harmonic spectroscopy of"｜rewrite:按 Nat. Photonics 真题逐字改正
[high]｜[17] L35｜文章号误：正式版 PRB 113, 045118 (2026)，条目作 L041107｜verify:改为 045118
[medium]｜[17] L35｜一作 Gulloo Lal Prajapati 缩写应 G. L.；真 11 人仅列 3+et al.｜rewrite:规范缩写并统一 et al. 政策
[medium]｜[12] L25｜Simpson 缩写 E. E. 误（CrossRef 为 E. R.）；真 10 人仅列 3+et al.｜verify:改 E. R. 并补全或统一截断
[medium]｜[16] L33｜Martín 缩写漏 J.；et al. 仅遮 Rengal 1 人，截断无意义｜rewrite:补全 4 人 Iglesias/Pascual/Martín M. J./Rengal
[medium]｜[14] L29｜真 7 人仅列 3+et al.（漏 Wang/Purschke/Vampa/Brabec），与他条全列不一｜add:补全 7 人
[medium]｜全表 13 条｜[1]-[5][7]-[10][12][17][26][27] DOI 与 arXiv 双标违反"二选一"，与仅 DOI/仅 arXiv 三态并存｜rewrite:已刊标 DOI、preprint 标 arXiv，全表单轨
[medium]｜[20] L41｜FAIR 数据管理原则与 BSV-HHG 科学问题无直接关联，疑装饰引用｜remove:核正文承接句，无则删除
[medium]｜时效性全表｜2023-2026 文献 16/33=48.5%，低于 50% 基准｜add:增补 1-2 篇 2025-26 量子光 HHG 文献
[low]｜[21] L43｜PINN 与主题关联取决于 scheme 是否用神经网络反演｜verify:确认承接后保留
[low]｜[27] L55｜DOI 10.1103/4x11-phs2 为 APS 代号式，与 PhysRev 式不统一｜verify:换标准 DOI 统一
[low]｜[17] L35｜DOI 10.1103/ydjj-xxcl 同为代号式｜verify:同 [27] 统一处理
[low]｜[22] L45｜111 人 Roadmap 为 preprint，正文引用宜指向具体贡献段｜verify:标注 preprint 并落实承接
[low]｜[14] L29｜中文注释（preprint；正式发表状态待核实）混入英文条目｜rewrite:删注释或统一语种
[low]｜[19] L39｜1987 年 Schleich-Wheeler 为压缩态光子统计基础文献，主题契合｜legacy:保留

## 锚点对比（[21] vs CrossRef 10.1016/j.jcp.2018.10.045）
- 申请书：Karniadakis G. E., Kevrekidis I. G., Lu L., Perdikaris P., Wang S., Yang L. … JCP 378, 686-707 (2019)
- 真实记录：Raissi M., Perdikaris P., Karniadakis G. E.｜标题一致｜JCP 378, 686-707 (2019)
- 差距：一作错置+4 人虚构，卷期页年全对——元数据"半真半假"是本轮虚构的主要形态，格式校验无法检出，必须逐位反查作者名单
锚点对比结论：差距明显

## 对抗结论
本轮 18 个问题（critical 2 / high 3 / medium 7 / low 6）。两处 critical 均为作者层虚构（[13] 15 人拼凑、[21] 一作错置+4 人杜撰），且 [13][21][7][12][16][19][20] 全部落在预检标记的"凭记忆引用"未验证池内，印证该池为虚构风险集中区；检索池内条目亦非全净（[11] 标题意译、[17] 文章号误）。R2 验收口径：①[13][21] 作者逐位比对；②[7][11][17] 标题/文章号逐字；③全表 DOI/arXiv 单轨化。未达输出标准（存在 critical）。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.35
完整性：0.80
综合评分：0.575
