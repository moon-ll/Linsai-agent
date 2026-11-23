# 评审团复核报告（panel-verify-report）

- 课题：key-transient-quantum-phase-optical-20260726　日期：2026-11-01
- 复核方式：修改后以磁盘文本为准逐条重读核销（非凭修改记忆），关键行经 grep/重读双重确认
- 修改范围：04_proposal/sections/ 下 rationale.md（9 处）、content.md（1 处）、scheme.md（5 处）、full_review.md（1 处）、references.md（1 处），共 17 处编辑；未跑脚本、未调 LLM API

## 一、核销表

| 条目号 | 级别 | 已解决/部分/未解决 | 文本证据 |
|---|---|---|---|
| C1（P1） | high | 已解决 | references.md L48："†Dubey K.A., Neufeld O. Attosecond charge migration timescales…"；rationale.md L85："……理论计量研究（†Dubey 与 Neufeld[44]）。"（作者链据 WebSearch 核实 arXiv:2609.23615 双作者更正；预印本 † 标记与 15 条计数不变） |
| C2（P2） | high | 已解决 | rationale.md L51："能谷动量锁定与光驱动能带结构变化的多带谐波光谱响应已有第一性原理预测[21]。"——与 §2.2 末段"该工作属模拟预言而非实验观测"不再矛盾；grep"观测[21]"零命中 |
| C3（P3） | high | 已解决 | rationale.md L146–148：段落以句号收束，空行后"#### 问题三：瞬态拓扑不变量的阿秒尺度测量理论"独立成行；全文"。####"粘连零命中 |
| C4（P4） | medium | 已解决 | rationale.md L6："随之达到 0.1–5 eV。该范围由材料带间偶极矩与场强的组合决定：……即得 1 Å·e×0.1 V/Å=0.1 eV 至 10 Å·e×0.5 V/Å=5 eV 的全跨度。Bi₂Se₃……（见下例）。这一量级……"——下端与场强窗口端点自洽，387 字长句拆为 4 句（Bi₂Se₃ 中段 0.5–2.5 eV 锚点不变，与 params.json 换算链一致）；grep"0.3–5 eV"零命中 |
| C5（P5） | medium | 已解决 | full_review.md L55："唯一（编号 1-44 连续无跳号）"——与 references.md 实际条目数一致；正文挂点 1–44 各出现 ≥1 次经重扫确认 |
| C6 | medium | 已解决 | rationale.md L171："统一样品体系（四组有隙体系 Bi₂Se₃、MnBi₂Te₄、MoS₂、1T-TaS₂ 与无能隙类比参考 Co₃Sn₂S₂）"，与 scheme §1.2 口径对齐，本节"五个靶材"计数自洽 |
| C7 | medium | 已解决 | 超长句拆分 5 处落盘：rationale L85（"（†Dubey 与 Neufeld[44]）。亚周期能谷极化控制……"）、L91（三级排比改三句）、L91 后句（"演示层面。结构自由度……"）、L113（"机制分析。实验侧……"）、scheme L73（"合计约 2.5×10⁵ 发。2 μm 端……"）；复扫散文句无 >120 字残留（表格行与公式密集句不计） |
| C8 | low | 已解决 | rationale L99"Watanabe 分别给到"（单作者）；scheme L125/L173/L199"Zhao 与 Zou[36]"（双作者，与"Shah 与 Cangi[35]"惯例统一） |
| C9 | low | 已解决 | content.md L47："（该工作针对静态拓扑相）"，指代明确 |
| C10 | low | 未解决（合理豁免） | rationale §2.2"2013 年……Floquet-Bloch 态的实验观测"无挂引：补引须先核实 Wang et al., Science 2013 元数据，本轮未检索到池内记录，按"宁可少一条，不可编一条"纪律不动，转下轮 |
| C11 | low | 未解决（合理豁免） | scheme §2.3(a) QMT 算力段验收归属、正文 † 前缀统一策略、§0 节名错位：均为表述优化类 low 项，不影响可执行性与正确性，转下轮酌情 |

## 二、复核补充确认

- 修改后引用完整性重扫：正文 [N] 唯一编号 44 个（1–44 无缺号、无越界），与 full_review 指标表"编号 1-44 连续无跳号"及 references.md 表头"预印本 15 条+刊版 29 条=44"三方一致；
- 修改未触碰 params.json 口径表任何 canonical/stale 条目（口径表 7 组 stale_patterns 修改前后 grep 均零命中）；
- 数值链复算（换算、抖动 RSS、误差合成、覆盖概率、分区矩阵、数据量/算力预算）全部通过，详见 panel-findings.md 第二节；
- 预审（06_panel-preaudit-20261101）三角色 14 条经逐条核对全部已在现文落地，无回潮。

## 三、判定

critical/high 全部解决（C1–C3），medium 全部解决（C4–C6），low 两项合理豁免转下轮（C10–C11）。无未解决的 critical/high。

复核结论: 通过
