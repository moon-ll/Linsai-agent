# 评审团核销报告 —— general-ssh-weyl-20260920（退回后完善轮，2026-11-04）

> 执行：引擎亲审模式（v7.2.97 契约）。核查方式：5 章节全文 Read + params.json 口径表逐条对照 + params-conflicts.json 清点（clean）+ grep 定点复查 + WebSearch/WebFetch 联网核实。
> 判定口径：以磁盘文本为唯一依据；已解决项须给出磁盘证据方可核销。编号说明：任务包旧号（You=[20]、Thakur=[18]、退相干链=[43]-[46]）已重排为现行号（[19]、[17]、[36]-[39]），本报告一律用现行编号。

## 一、核销表

| 条目号 | 条目 | 级别 | 状态 | 文本证据 |
|--------|------|------|------|----------|
| 1 | [CRITICAL] citation_integrity：You 2017 各向异性 HHG 样品 ZnO→MgO 全链 | CRITICAL | 已解决（本轮联网复核事实基础后核销） | content L41「You 等人[19]于 2017 年在 MgO 单晶中报告 HHG 各向异性光谱……四重角分布」；scheme L11/L91/L189/L195（校核一）/L232/L270 全部 MgO；references [19] 注释 MgO；全稿无 You+ZnO 误挂（ZnO 各向异性正确挂 Jessen[28]）；旧 L81-83 对照维度论述（现 rationale L85-L93）已改「ZnO 与 MgO 共同承担非拓扑参考角色」。联网核实：You, Reis & Ghimire, Nat. Phys. 13, 345-349 (2017) 样品为 MgO，MgO 挂法与原文一致；[20] 现挂 Ciappina 2025 综述（Adv. Phys. 74, 1-9），经核实真实存在 |
| 2 | [CRITICAL] indicator_consistency：G1 样本协议两版（≥200 vs N=100） | CRITICAL | 已解决（核销） | content L17「各不少于 200 个独立随机参数样本」＝ scheme L67「两类样本数各为 N，N 以 200 为下限，与研究内容方向一的样本协议一致」（含 G1=N_correct/(2N) 与判定操作）＝ full_review L34「各类 N ≥ 200」；grep「N=100/各 100 个」全稿 = 0 |
| 3 | 上轮豁免 B：「陈绝缘体/Chern 绝缘体」译名混用 | low | 已解决（核销） | grep「陈绝缘体」全稿 = 0，统一「Chern 绝缘体」 |
| 4 | 上轮豁免 C：S:L109 [17] Thakur「三类贡献独立指纹」归属存疑 | medium（本轮升级核实） | 本轮修复后核销 | scheme L109 改为「仅有 [17] 摘要级旁证——边带指纹的偏振依赖通道与电子-空穴退相干时钟，该摘要未直接证明三类指纹彼此独立；其严格成立是本方案首要检验内容」；证据：arXiv:2609.06119 摘要实测（螺旋性/取向敏感 + 退相干时钟，无三类指纹独立性主张） |
| 5 | 上轮豁免 D：C:L7 依赖链「方向一至三」含自身微瑕 | low | 已解决（核销） | 现 content L7「方向二、三的算法载体／方向三与方向四的判据集在对照验证处交汇」无自含表述；L57/L71「标定方向一至三所产拓扑判据」语义正确 |
| 6 | 新发现 N2：rationale L65 + references [27]「Bloch 反常速度与 Berry 曲率」术语与 [27] 原文不对应 | medium | 本轮修复后核销 | rationale L65 改「Bloch 群速度与 Berry 曲率决定的反常霍尔速度」；references [27] 注释同步「Bloch 群速度与反常霍尔速度（Berry 曲率项）的竞争」；证据：arXiv:2507.09234 摘要「interplay of Bloch velocity and anomalous Hall velocity」；摘要中魔比例 1.5:1、MoS₂ 双峰、hBN 单调上升三项原描述与原文一致保留 |
| 7 | 新发现 N3：rationale L29「上文二维 Chern 绝缘体 HHG 工作」指针悬空 | medium | 本轮修复后核销 | 改「是下文三个紧束缚模型对比中 Chern 绝缘体分支的拓扑起点」，指向 L35 Lorenzo[18] 实锚；grep 确认旧句式 = 0；纯指针修正无技术内容变更 |
| 8 | 新发现 N4：scheme L67/full_review L34「平衡时 G1 = 1 − δ_FP」在现行 δ_FP 定义下需附加条件 | medium | 豁免（记录不修，不阻塞） | 修正须先裁决 δ_FP 占比分母口径（FP/N 需 FN=FP；FP/2N 需 FN=0），属指标定义变更、跨三文件联动，留待下一 writer 轮；两阈值在补数语义下自洽 |
| 9 | 新发现 N5：rationale L65「hBN 因 Berry 曲率较弱、色散各向异性较强」机制归因超出 [27] 摘要 | low | 豁免（记录待核实） | 摘要仅陈述 hBN 单调上升；本轮未能核实正文归因；如后续核实无据，删机制半句保留现象描述 |

## 二、本轮修复清单（4 处 Edit，全部联网核实有据）

1. rationale L29：「上文二维 Chern 绝缘体 HHG 工作的拓扑起点」→「下文三个紧束缚模型对比中 Chern 绝缘体分支的拓扑起点」（悬空指针改实锚）
2. rationale L65：「Bloch 反常速度与 Berry 曲率」→「Bloch 群速度与 Berry 曲率决定的反常霍尔速度」（对齐 arXiv:2507.09234 原文术语）
3. references [27] 注释：「差异源于 Bloch 反常速度与 Berry 曲率」→「差异源于 Bloch 群速度与反常霍尔速度（Berry 曲率项）的竞争」（与 rationale 同步）
4. scheme L109：「仅有 [17] 摘要级证据」→「仅有 [17] 摘要级旁证——边带指纹的偏振依赖通道与电子-空穴退相干时钟，该摘要未直接证明三类指纹彼此独立」（归属精确化）

## 三、复核说明

- 修复后磁盘 grep 复核：旧句式/旧术语（上文二维 Chern、Bloch 反常速度、摘要级证据[17]）全部清零；两处 critical 靶子指纹（You+ZnO 误挂、N=100）全稿 = 0。
- 关键锚点在位：references 40 条整、编号连续；退相干参数链完整（旧[43]-[46]=现[36]-[39]），零触碰；params.json 与 params-conflicts.json 未改动；十二项指标数值三文件同值；「预印本」标注与已刊状态无矛盾。
- 联网核实记录（4 项）：You 2017 Nat. Phys. 13, 345 样品 MgO ✓；Ciappina Adv. Phys. 74, 1-9 (2025) 综述存在 ✓；arXiv:2507.09234 摘要（魔比例 1.5:1、MoS₂ 双峰、hBN 单调、双速度竞争）✓；arXiv:2609.06119 摘要（螺旋性/取向敏感 + 退相干时钟，无三类指纹独立性）✓。
- 红线遵守：仅编辑 04_proposal/sections/ 下 rationale.md / scheme.md / references.md 三个文件 + 本 06_panel/ 两产物；未运行任何脚本、未调用 LLM API（联网核实仅 WebSearch/WebFetch，任务包明示允许）；未运行 --adopt-engine（按指示留给主会话）。
- 判定：两处 CRITICAL 均已解决，无 critical/high 未解决项。

复核结论: 通过
