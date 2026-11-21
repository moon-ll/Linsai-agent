# 对抗评审报告（第 5 轮·参考文献专项）

- 项目类型：key（瞬态量子相的全光读写与时序反演）
- 审查日期：2026-10-23
- 范围：references.md 全 41 条（编号一致性采信预检）；refs 专项上轮为 R4（2026-10-14），本轮为验收+全量反查：29 条 DOI 经 CrossRef 逐条五件套比对，12 条 arXiv 经 export API 反查，头注/时效/挂点程序复算

## R4 修复验收（全部通过）
- 头注计数 12/29/41 及 † 编号列表与实物程序复算一致 ✅
- [17] 已补卷期 Nat. Phys. 22: 1607-1614 ✅；[9] 题名已按刊版改 ✅
- [23][32][34] 三条 APS 短式 DOI CrossRef 全部解析成功，R4-low 解除 ✅

## 核验统计
- 真实性：41/41 可溯源，零虚构零错挂。29 条 DOI 题名/卷/年逐条全符；12 条 arXiv 题名/作者链/年份全符，journal_ref 与 doi 字段均为空——头注"纯 arXiv 预印本"声明本轮逐条重查后仍成立（纪律：见刊状态逐轮复查，上轮核实不豁免本轮）
- 预检 15 条风险条目 [1,2,3,5,7,9,10,13,14,15,17,19,20,21,23] 逐条反查全部通过，R7 型虚构未重现
- 作者链：29 条 DOI 前三作者姓逐条核对全一致（[23] 已按官方序重排验收）；arXiv 12 条前三作者缩写逐条比对一致
- 时效性：2024-2026 文献 32/41 = 78%，达标（≥50%）
- 相关性：41/41 均有正文实引锚点（程序复算零孤儿）；边界条目 [28] 装置、[31] SSH-Hubbard、[34] 非线性声子、[39] MnBi₂Te₄、[40] α-T₃ 均挂实质论断，无无关引用
- 格式：DOI/arXiv 二选一零违例；et al. 截断与头注"前三+et al."规则一致，无超三作者全列
- 工作日志污染：四章 grep（工作日志/检索记录/本轮修改/待补充/TODO/TBD）零命中；预检膨胀告警实为总数 41>40，非日志文本残留，无迁移对象
- 附注：content/scheme 各仅实引 8/12 条，密度偏低属正文侧议题，本轮不立案

## 维度评分
| 维度 | 得分 | 依据 |
|---|---|---|
| 严谨性 | 0.87 | 41/41 全真、作者链题名卷期逐条核过；余 [34] 题名漏词、[9][38] 复合姓截断 |
| 完整性 | 0.85 | 零孤儿零缺失、时效 78%；总数 41 超上限为第三轮残留 |

## 问题清单
[medium]｜[34] Kiselev｜题名漏词 nonequilibrium，与刊版题名不符｜按 CrossRef 官方题名补该词；action: rewrite
[medium]｜全表｜总数 41 超出 20-40 上限，R4/R8 两轮提出未处置（残留）｜删最弱单点条目或头注加一句超限说明；action: remove/verify
[low]｜[9]/[38]｜复合姓截断：官方为 Ghayeb Zamharir/Gulyás Oldal｜按官方姓补全两处；action: rewrite
[low]｜12 条†预印本｜占 29%（8 条 2026 新挂），未过 30% 警戒线｜见刊后逐条回录刊版 DOI；action: verify

## 锚点对比
- 引用（[34] 条目）：Dynamical breaking of inversion symmetry, strong second harmonic generation, and ferroelectricity with nonlinear phonons
- CrossRef（10.1103/lwpl-brrr）：Dynamical Breaking of Inversion Symmetry, Strong Second Harmonic Generation, and Nonequilibrium Ferroelectricity with Nonlinear Phonons
- 锚点结论：仅漏饰词 nonequilibrium，作者/卷期/DOI 全对，属可修微瑕而非虚构错挂，补词即收敛。

## 对抗结论
- 本轮 4 个问题（critical:0, high:0, medium:2, low:2）
- 相比 R4：改善 4（头注计数 high、[17] 补卷期、[9] 题名、短 DOI 验证），新增 2（[34] 漏词、[9][38] 复合姓截断），残留 1（总数超限）
- 是否达到输出标准：是——零虚构、零错挂、零孤儿、时效达标，剩余皆元数据微修，当轮可收敛
- 返工优先级：[34] 补词 → 总数取舍（若删条须同步正文全部标记并 grep 复核）→ [9][38] 补姓 → 见刊回录
- 下轮建议：writer 补充检索命中回录 02_literature 检索池；refs 专项可转抽检模式（新增/改动条目全查，存量抽 20% 复验）

## 评分
创新性：N/A
可行性：N/A
严谨性：0.87
完整性：0.85
综合评分：0.86
