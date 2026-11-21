# R3 引用审校 — general-ssh-weyl-20260920

审校范围：04_proposal/sections/{rationale,content,scheme,references}.md（refs 40 条，[1]–[40] 连续无跳号）。
审校日期：2026-10-17。对账脚本：/tmp/r3_citation_audit.py（终端执行故障，本次以等价正则提取+人工比对完成，脚本可复跑复核）。

## 编号对账（五项）

| 项 | 计数 | 明细 |
|---|---|---|
| 占位符 | 0 | 无 [?]/[TODO]/[N/A] 类残留 |
| 死条目 | 0 | 40 条均被三章引用；[31]–[34] 以区间 token [31-34] 引用（rationale L5），与 refs L9 头注声明一致 |
| 超界 | 0 | 正文最大引用号 40 = refs 最大号 |
| 一号两用 | 0 | refs 每编号唯一条目；[35] SSH/[36] Haldane/[37] Faeyrman/[38]/[39] Bai/[40] Li 挂位经逐条核对全部正确 |
| 断链 | 0 | 正文引用编号在 refs 全部有对应条目 |

P0 复核：①P0-critical「rationale 末组编号整组错位一格」（[36][37]应[35][36] 等）——**已修复**，当前 [35][36][37][38][39][40] 与条目实物逐一相符；②P0-high「refs 头注自证矛盾（[31]–[35] 五条气相/[4] 列预印本）」——**已修复**（头注现写"[31]–[34] 四条"，[4] 已按 Nat. Commun. 2018 刊本描述）。

## 联网核实记录（7 条，含证据 URL）

1. **[20] arXiv:2508.15631（Lorenzo 等，P0-critical 涉及）**：真实，但 v1/v2 摘要口径不同。
   - v2（2026-05-24，当前版）摘要："significant enhancements of the harmonic intensity yields, **reaching up to two orders of magnitude** relative to trivial phases" → 上限两个数量级（≤100 倍）。https://arxiv.org/abs/2508.15631
   - v1（2025-08-21）摘要："for the topological semimetal phase, we find a harmonic enhancement by **two to three orders of magnitude** in the Kagome lattice" → 拓扑半金属相 2–3 个数量级。https://arxiv.org/abs/2508.15631v1
   - 判定：refs 条目"增强上限两个数量级（摘要报告）"与 v2 一致 ✓；但正文 content/scheme 多处把 v1/v2 归属写反（见意见 R3-01）。v2 作者链增至 10 人（新增 M. Jangjan、S. Ghimire，顺序变动），refs 仍挂 v1 的 8 人链（见 R3-02）。
2. **[9] PRL 120, 177401 (2018)（Bauer & Hansen，支撑"14 个数量级"关键判据）**：真实，摘要原文 "the harmonic yield is found to differ by **up to 14 orders of magnitude**"，正文声称一致 ✓。https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.120.177401
3. **[16] Nano Lett. 25 (2025)（Pilch TaP，三因素分解校核基准）**：真实，Nano Lett. Vol 25 Issue 47（2025-08-22），TaP 纳米薄膜室温多周期窄带 THz THG，作者方向与条目一致。https://pubs.acs.org/toc/nalefd/25/47 ；https://www.semanticscholar.org/author/Renato-M.-A.-Dantas/25919557
4. **[19] Phys. Rev. Applied 24, L021001 (2025)（短 DOI 10.1103/3xs5-km1v 格式异常项）**：真实，link.aps.org/doi/10.1103/3xs5-km1v 直达；Rana/Mrudul/Bharti/Giri/Dixit，NbSiₓTe₂，2025-07-22 刊出。APS 2025 起启用新短 DOI 格式，条目无误。https://link.aps.org/doi/10.1103/3xs5-km1v
5. **[27] PRB 111, 184314 (2025)（国内 β-WP₂ 理论）**：真实，X. Liu, L. Geng, X.-S. Kong, J. Zhang, Y.-K. Fang, L.-Y. Peng 六人全对（彭亮佑通讯），SBE 选择定则+反常椭圆依赖与正文一致 ✓。https://journals.aps.org/prb/abstract/10.1103/PhysRevB.111.184314
6. **[29] Comput. Mater. Sci. 268, 114641 (2026)（中科院半导体所 MoS₂/hBN CRB）**：真实，Q.-G. Fan, K. Lai, …, Z. Wang（2026-04-01 刊出），实空间轨迹+Bloch 反常速度与条目描述一致 ✓。https://www.semanticscholar.org/paper/1e980a4e60824d7f0c79f953ddae7a115029a607
7. **[37] arXiv:2606.02238（Faeyrman，2026 新预印本）**：真实，六位作者（Faeyrman/Zhang/Ivanov/Peng/Dudovich/Piccoli）与条目一致；MgO THz 破缺反演对称、双色 HHG 分辨 Berry 相位实部（带内）与虚部（隧穿）与正文声称完全匹配 ✓。https://arxiv.org/abs/2606.02238
   附带：[26] arXiv:2510.01760（Duan Cd₃As₂ 微腔）在检索中同源出现，标题一致，真实 ✓。

## 正文声称与文献内容匹配性抽查

- [9]"最高增强达 14 个数量级" ✓（摘要原句 up to 14 orders）。
- [37]"实部（带内关联传导）与虚部（量子隧穿）" ✓（摘要 real↔intraband / imaginary↔tunneling）。
- [16] TaP 立方功率律、偏振衰减至圆偏振为零 ✓（主题级匹配；$I_{3f}\propto I_f^3$ 细节在原文正文，未见矛盾）。
- [29] MoS₂ 双峰 vs hBN 单调上升 ✓（摘要 anomalous Hall velocity/实空间轨迹口径一致）。
- [20]：refs/rationale 口径与 v2 一致 ✓；content/scheme 的 v1/v2 标注互驳 ✗（意见 R3-01）。
- [27] "type-II Weyl β-WP₂" ✓。

## 意见清单

[R3-01|high] content+scheme｜content L13、scheme L59/L233｜[20] v1/v2 版本归属颠倒：正文写"v1 摘要达两个数量级、v2 部分可达三数量级"｜原文摘录："增强峰值达 100 倍（v1）/部分计算可达 1000 倍（v2）"｜按实物互调：v1=拓扑半金属相 2–3 个数量级、v2=上限两个数量级；全句统一 v2 口径（≤100 倍），R=2 预标定不受影响，三处联动改。

[R3-02|high] references｜L49 条目 [20]｜作者链停留在 v1（8 人），当前 v2 已 10 人且顺序变动｜原文摘录："B. Lorenzo, C. Granados, D. Kim, C. Batista…A. Chacón"｜更新为 v2 作者链（Lorenzo, Batista, Jangjan, Kim, Menotti, Liu, Gao, Ghimire, Granados, Chacon）并标注访问版本日期。

[R3-03|low] references｜L7 头注｜[22] 兼有 DOI 与 arXiv:2510.15207 却未列入双挂类目，26+4 计数实为 25+5｜原文摘录："另 [11][23][24][26] 共 4 条 DOI＋arXiv 双挂"｜头注把 [22] 移入双挂类并改计数，保持自证一致。

## 结论

编号体系五项对账全零、P0 两项引用类问题已实质修复。联网反查 7 条全部真实可溯（含 3 条国内工作与 1 条 2026 预印本）。核心遗留问题是 [20]（支撑 S_edge 与 R=2 阈值的关键文献）的 v1/v2 版本归属在 content/scheme 颠倒、refs 作者链滞后一版，属可一次修毕的 high 项；无虚构引用、无断链死条目。
