# 评审团复核报告（panel-verify-report）

- 课题：key-transient-quantum-phase-optical-20260726　日期：2026-11-04
- 复核方式：修改后以磁盘文本为准逐条重读核销（非凭修改记忆），关键行经 grep/重读双重确认
- 修改范围：04_proposal/sections/ 下 full_review.md（1 处）、scheme.md（4 处），共 5 处编辑；未跑脚本、未调 LLM API（WebSearch 仅作引用元数据核实）；未运行 --adopt-engine（按指示由主会话统一收尾）

## 一、核销表

### 新发现条目（本轮）

| 条目号 | 级别 | 已解决/部分/未解决 | 文本证据 |
|---|---|---|---|
| C1（P1） | medium | 已解决 | full_review.md L51："唯一（编号 1–50 连续无跳号）"——与 references.md 实际 50 条（grep -c '^\[' = 50）一致；"1–48"全文零命中 |
| C2（P2） | low | 已解决 | scheme.md L131"Zhao C. 与 Zou X.[36]于 2025 年将自注意力 Transformer……"、L179/L205"Shah 与 Cangi[35]、Zhao C. 与 Zou X.[36]"；裸写"Zhao 与 Zou"全文零命中；与 rationale L105 及 reading-notes.md 具名约定（2026-11-03）四方一致 |
| C3（P3） | low | 已解决 | scheme.md L127 句尾新增："……月扫描规模也与超算机时配额一致；产出的 Berry 曲率与量子度规数据即子课题 C 反演的目标量，并为 L2 采样反演提供前向模型输入。"——QMT 数据去向与验收归属点明，无数值/技术内容改动 |

### 上轮亲审条目存活核对（L 系列，逐条对照当前磁盘文本）

| 条目号 | 级别 | 已解决/部分/未解决 | 文本证据 |
|---|---|---|---|
| L1（上轮 C1 [44] Dubey 作者链） | high | 已解决（替代演化，非回潮） | 重写移除该条目，语境改挂 Jiménez-Galán[45]（rationale L79"亚周期能谷极化控制（Jiménez-Galán 等[45]）"，Optica 2021 sub-cycle valleytronics 池记录+WebSearch 实证）；"Dubey/†Neufeld/2609.23615"零命中，编号 1–50 无悬空 |
| L2（上轮 C2 [21]"观测"→"第一性原理预测"） | high | 已解决 | rationale L43"多带谐波光谱响应已有第一性原理预测[22]"（重编号后语义不变）；L81"该工作属模拟预言而非实验观测" |
| L3（上轮 C3 标题粘连） | high | 已解决 | rationale L149"#### 问题三：瞬态拓扑不变量的阿秒尺度测量理论"独立成行；"。####"全文零命中 |
| L4（上轮 C4 ℏΩ_R 下端自洽） | medium | 已解决 | rationale L5"0.1–5 eV"+L7 组合推导句保留（1 Å·e×0.1 V/Å=0.1 eV、10 Å·e×0.5 V/Å=5 eV 复算成立） |
| L5（上轮 C5 指标表编号计数） | medium | 已解决（本轮重写后曾回潮为 1–48，经 C1 修复） | 见 C1 |
| L6（上轮 C6 Co₃Sn₂S₂ 括注） | medium | 已解决 | rationale L169"（四组有隙体系 Bi₂Se₃、MnBi₂Te₄、MoS₂、1T-TaS₂ 与无能隙类比参考 Co₃Sn₂S₂）" |
| L7（上轮 C7 超长句拆分 6 处） | medium | 已解决 | 重写保持句读纪律：>125 字散文句全文零残留（公式密集句不计） |
| L8（上轮 C8 Watanabe 单作者 / Zhao 与 Zou） | low | 已解决 | rationale L97/L163"Watanabe[31]"单作者✓；"Zhao C. 与 Zou X.[36]"四处统一（见 C2） |
| L9（上轮 C9 content 指代） | low | 已解决 | content L47"（该工作针对静态拓扑相）" |
| L10（上轮 C10 low：2013 观测无挂引） | low | 已解决（重写补挂） | rationale L67 挂 Wang 等[16]（Science 2013, 342: 453, DOI 10.1126/science.1239834，池+WebSearch 双验） |
| L11（上轮 C11 low：† 前缀不统一） | low | 已解决（重写统一） | 12 条 arXiv 预印本全带 †、38 条刊版全不带，策略一致 |
| L12（上轮 C11 low：§0 节名错位） | low | 已解决（重写移除） | §0 并入开篇，"§0"指针零命中 |
| L13（上轮 C11 low：QMT 段归属） | low | 已解决（部分由重写完成，余项经 C3 补齐） | scheme L127 算力协调句（重写已有）+ 数据去向短语（C3） |

## 二、复核补充确认

- **引用完整性**：正文挂点并集 1–50 无缺号、无越界，与 references.md 50 条及 full_review 指标表"编号 1–50 连续无跳号"三方一致；50 条引用全部有据（43 条池记录 + 7 条 WebSearch 实证，逐字段吻合，无编造）。
- **口径表**：params.json 7 组 stale_patterns 修改前后 grep 零命中；本轮修改未触碰任何 canonical 语义（Zhao 归属语义保持，仅具名形式升级）。
- **遗留移交项**：params.json canonical 编号描述（[18]→[19]、[21]→[22]）因重写插入 [16] 整体位移，属口径表元数据维护，超出本评审红线（仅 sections/ 5 文件 + 06_panel/ 产物），已记入 panel-findings.md 附注 A 请主会话同步。
- **数值链复算**：换算、抖动 RSS、误差合成、覆盖概率、分区矩阵、数据量/算力预算、波长比全部通过（详见 panel-findings.md 第四节）。
- **退回意见（feedback-6）核对**：critical 项（手册八要素升级）属 method_manual 模块职责，不在本评审范围；medium 项（手册与 scheme 口径一致性）经 method-manual.md 交叉核对通过（100 as 预算/L1 算力链/QMT 参数/三级命名逐项一致）。

## 三、判定

新发现 3 条（1 medium + 2 low）全部解决；上轮 17 处修复中 16 处存活或被重写以更优方式替代，1 处（指标表计数）回潮即修复；上轮 low 未修 4 项全部消化。无未解决的 critical/high。

复核结论: 通过
