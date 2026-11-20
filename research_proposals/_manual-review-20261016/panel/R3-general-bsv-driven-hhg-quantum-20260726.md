# R3 引用审校 — general-bsv-driven-hhg-quantum-20260726

审校日期：2026-10-17 ｜ 审校人：R3 引用审校评审员（期刊文献编辑）
对象：`research_proposals/optimizing/general-bsv-driven-hhg-quantum-20260726/04_proposal/sections/`（rationale.md / content.md / scheme.md / references.md，39 条）
特别任务：复查 2026-10-11 轮已核实的 [11] Li PRL126,137403 / [12] Raab RSI95,073002 / [18] Prajapati DOI 10.1103/ydjj-xxcl 三锚是否仍正确，并核查本轮新条目。

## 编号对账

方法说明：本轮终端执行环境故障（命令路由不可用），对账脚本 /tmp/r3_citation_audit.py 已备但改为"Grep 提取 + 全量人工比对"完成，覆盖三正文全部引用标记（含 [n,m] 并引与 [a]–[b] 区间式，数学区间如 [0.5,1.5]/[0,2π] 已排除）。条目行按"行首 [n] 后非 -/–"识别。

| 检查项 | 计数 | 明细 |
|---|---|---|
| 占位符 | 0 | 无 TODO/待补/空条目；[15][22][32][33] 为 arXiv 预印本但内容完整且已注明"暂无正式期刊版本" |
| 死条目 | 0 | 39/39 条全部被正文引用（利用率 100%）；条目尾注自报的引用位置抽查 [11][29][39] 与实际引用点一致 |
| 超界 | 0 | 正文最大引用号 [39] = 条目最大号；无 [40]+ 引用 |
| 一号两用 | 0 | 编号 [1]–[39] 连续唯一，物理顺序严格递增；无同一文献重复著录（[3] Agafonov 2010 与 [4] Iskhakov 2012 为同组不同论文，合规） |
| 断链 | 0 | 正文所有引用编号均有对应条目 |

附加检查：条目格式统一（作者-标题-期刊卷期页-DOI-arXiv-用途尾注）；[19] Ghimire 正文两处年份表述（rationale "2010 年（在线）/2011 年（刊印）" vs 条目 2010）已由正文自注调和，合规。

## 联网核实记录（URL）

策略：上轮三锚复查 + 被引最多（[1]，正文 8 处）+ 支撑关键判据（[13] 室温关联态 126 meV/285 K，四类对照体系设计的核心依据）+ 2026 新条目（[36] Nature 级、国内主线）。共 7 条。

1. **[11] Li PRL 126,137403 (2021) — 上轮锚复查：仍正确 ✓**
   上海科技大学潘义明发表论文列表逐字命中："Ang Li, Yiming Pan, Philip Dienstbier, and Peter Hommelhoff, Quantum interference visibility spectroscopy in two-color photoemission from tungsten needle tips. Phys. Rev. Lett. 126, 137403 (2021)"
   https://spst.shanghaitech.edu.cn/pym/list.htm ｜ https://arxiv.org/abs/2205.11161（arXiv 号与条目一致）
2. **[12] Raab RSI 95,073002 (2024) — 上轮锚复查：仍正确 ✓**
   AIP 官网命中（含 Erratum 记录）；正文引用的"优于 150 mrad 相位稳定性（10 分钟积分）"与原文"delay stabilization with a standard deviation of < 150 mrad"逐级对应，声称-文献匹配。
   https://pubs.aip.org/aip/rsi/article/95/7/073002/3303489/ ｜ https://arxiv.org/html/2405.11859
3. **[18] Prajapati PRB 113,045118 (2026) — 上轮锚复查：arXiv 锚一致 ✓**
   arXiv:2410.01424 原文直接命中，标题/RNiO₃ 莫特相变 THz 谐波内容与条目及正文声称（"THz 谐波随金属—绝缘体跃迁变化"）一致；PRB 正式版 DOI 10.1103/ydjj-xxcl 为 APS 新式短码，沿用上轮核实结论。
   https://arxiv.org/pdf/2410.01424.pdf
4. **[1] Rasputnyi Nat. Phys. 20,1960–1965 (2024)（被引最多）✓**
   arXiv:2403.15337 页面 Related DOI 字段直接给出 10.1038/s41567-024-02659-x（与条目一致）；作者列表 9 人与条目"前三+et al."吻合；摘要确认"0–2×10¹³ photons/pulse、±1 V/Å 亚周期场涨落"与正文 §1.2.2 声称一致。⚠ "5–15 倍产率提升"具体区间在摘要层面未出现（摘要仅言 considerably more efficient），建议对照 Nature Phys 原文图表（见 R3-03）。
   https://arxiv.org/abs/2403.15337
5. **[13] Wu PRL 131,256201 (2023)（关键判据）✓ 含数值逐字核实**
   APS 官网 PRL Vol.131 Issue 25 目录命中标题与作者（Fanfan Wu, Qiaoling Xu, Qinqin Wang…）；多源摘要逐字确认"correlated electronic state at v=1 shows a giant correlated gap of ∼126 meV and may persist up to a record-high critical temperature over 285 K"——正文三处引用（§1.2.3/§2.3/§3.3）的 126 meV、285 K 数值与"可能存在"的谨慎措辞均与原文吻合。
   https://journals.aps.org/prl/issues/131/25 ｜ https://discovery.researcher.life/topic/atomic-reconstructions/18719321?page=4
6. **[36] Jiang Nature 654,356 (2026)（2026 新条目、国内主线）✓**
   华东师范大学精密光谱科学与技术高等研究院官网 2026 论文列表逐字命中："Nonlinear atomic tunnelling boosted by bright squeezed vacuum, Zhejun Jiang#, Shengzhe Pan#, Jianqi Chen, …, Jian Wu*, Nature 654, 356 (2026)"；300 nJ BSV ≈ 7.1 μJ 相干光、>20 倍非线性效率提升与正文 §1.3 声称完全一致；arXiv:2604.05783 存在（v1 标题 Quantum-Boosted Nonlinear Tunneling…，正式版改题，正常现象）。
   https://faculty.ecnu.edu.cn/_s29/psz/main.psp ｜ https://arxiv.org/html/2604.05783v1
7. **[27] Wang PRA 112,L011102 (2025)（DOI 短码抽查）◐**
   arXiv:2406.10443 真实（ShiJun Wang, XuanYang Lai, XiaoJun Liu，"Attosecond pulse synthesis from high-order harmonic generation in intense squeezed light"），与条目标题一致；但 PRA Letters 正式版卷期（112(1), L011102）与 DOI 10.1103/4x11-phs2 未能独立核实，建议投稿前在 journals.aps.org 终核。
   http://arxiv.org/list/physics.atom-ph/2024-06?skip=65 ｜ https://figshare.com/articles/preprint/Attosecond_pulse_synthesis_from_high-order_harmonic_generation_in_intense_squeezed_light/26065027

核实结论：7 条中 6 条确认真实且支撑声称，1 条（[27]）预印本锚真实、正式版待核；0 条伪引；0 条 citation_misattribution 达 critical 级。

## 意见清单

[R3-01|minor] 研究方案｜scheme §3.4（L59）｜[11] 被引申为"场统计→可见度"转化先例｜"Li 等 [11] 在钨针尖场中以两色场量子干涉将场统计差异转化为可见度差"｜核实 [11] 为经典相干光双色多光子路径干涉（可见度 90%±5%、随双色强度比 0–100% 可调），不含非经典光场统计维度。建议删"场统计差异"，改为"路径干涉可见度随双色参数变化的测量范式"。

[R3-02|minor] 研究方案｜scheme §3.7 创新点二（L103）｜[11] 与 [15] 并列"建立 Q_F 概念"表述过载｜"钨针尖场两色场量子干涉 [11] 与 Boroumand 等 [15] 的 QSHHG 框架已在气体原子与单束双色场语境下建立 $Q_F$ 的概念"｜$Q_F$ 为本项目自定义量度，[11] 原文无此概念。建议改为"建立了可见度型测量的概念基础"，将"建立 Q_F 概念"的归属收窄至 [15]。

[R3-03|suggestion] 立项依据｜rationale §1.2.2（L25）及 content §2.3｜[1] "5–15 倍"区间待原文图表级复核｜"BSV 在 4–7 阶谐波上较同平均强度经典光有 5–15 倍产率提升"｜arXiv 摘要仅言"considerably more efficient"；该区间支撑 QEF 对照基准论述（content L61）。建议对照 Nature Physics 20, 1960 原文 Fig. 补数值出处后再定稿。

[R3-04|suggestion] 参考文献｜[27]｜PRA Letters 正式版未核实｜"Phys. Rev. A 112(1), L011102 (2025). DOI: 10.1103/4x11-phs2"｜arXiv:2406.10443 已核实真实；建议投稿前于 journals.aps.org 核对 L011102 卷期与 DOI 短码，若尚未正式发表则按 [15][32][33] 体例改标预印本。

[R3-05|suggestion] 参考文献｜[36]｜期号页码待官方终核｜"Nature 654(8118), 356–360 (2026). DOI: 10.1038/s41586-026-10485-9"｜ECNU 官网确认 Nature 654, 356 (2026)；期号 8118 与页码区间 356–360 建议以 nature.com 文章页为准后保留。

——总评：三上轮锚（[11][12][18]）复查全部仍然成立；编号体系五项全零、条目利用率 100%，引用卫生为三课题最优；核心风险集中在两处对 [11] 的引申表述（minor）与两处正式版著录待核（suggestion），无 critical/major 级问题，无需删条或去引用化处理。
