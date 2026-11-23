定点核查完成，报告已落盘：
/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-bsv-driven-hhg-quantum-20260726/06_panel/panel-critic-findings.md

核查方法：五章节文件全部实读；预检管线定位到 scripts/proposal_lifecycle/section_hygiene.py 并实跑其告警函数与迁移函数（非凭历史记录判定）；表达红线全部程序化扫描（禁用词/括号交叉引用/条件分支/超长句/术语 grep/破折号计数）。

遗留 2 条核对结果：

1. QEF 三维度枚举互斥（critical）——已解决。rationale L9 现为三指标实名枚举（$QEF_{\rm vis}$ / $QEF_{\rm yield}^{(q_{\rm ref})}$ / 全谐波求和比），与 content §2.3 L63 定义处逐项一致；"噪声关联比"在申请书本体（04_proposal/ 五文件）零命中，现存命中全在 05_review/ 评审域历史报告，属过程记录留存，无需清洗。

2. 预检骨架告警误报（critical）——本体侧已达标，管线判据未改，误报可复现。当前 full_review.md 实测 1490 中文字＜3000 上限、骨架头正确、工作记录特征零命中、迁移 dry-run 不触发（"骨架零迁移"子项达成）；但实跑 full_review_purity_text() 对本项目仍输出 critical 级"纯净性告警"——根因是 section_hygiene.py L191 的字节子句（size > 4500B；实测 6894B）未随修复删除。告警函数与迁移函数双逻辑分叉：迁移已按中文字数判，告警仍吃字节。修复归属工程侧（删 L191 字节子句），writer 不动章节文件。

新发现 5 条（critic 职责范围内）：

- P1 [medium] scheme §3.4/§3.5 前置门控叙事 2 处（"只有通过该检验…才进入物理解释"、"前置门槛"+两处"降级路径："标签句）
- P2 [medium] $QEF_{\rm yield}^{(\sum)}$ 术语跨章漂移：定义名"全谐波求和比"3 处 vs "全谱求和比"2 处（rationale L81、scheme L83）
- P3 [high] scheme §3.6–§3.8 判据三节重列（5% 阈值×3、$N_q \geq 800$×2、两倍偏离×2），且 L143 一边写"不在此重列"一边重列；L157 单段 306 字含 5 个条件分支句，超"每段 ≤1"纪律
- P4 [low] rationale 导航句 11 句/6042 字，指向"研究内容章分方向三"的指针重复 8 次
- P5 [low] 破折号"——"全稿 18 处未归零（rationale 7/content 3/scheme 8）

顺带零回退确认：canonical 禁用旧值（5 μm/5 nJ/2×10^10/0.1 MW/3.3×10^10）五文件 grep 全部零命中；骨架表与正文抽查无失同步；禁用词表命中为零。

汇总：待修 6 项——writer 侧 5 项（P1–P5），工程侧 1 项（预检判据，section_hygiene.py L191）；已解决 1 项。