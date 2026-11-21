# 评审团 findings —— general-ssh-weyl-20260920（退回后完善轮，2026-11-04）

> 执行：引擎亲审模式（v7.2.97 契约，评审员 = 执行者本人）。
> 核查方式：5 章节全文 Read + 口径表 params.json 逐条对照 + params-conflicts.json（clean，23 项 0 冲突）+ grep 定点复查 + WebSearch/WebFetch 联网核实（任务包明示允许）。
> 编号说明：任务包按旧编号体系书写（You 2017=[20]、Lorenzo=[19]、Thakur=[18]、退相干链=[43]-[46]）；11-03 引用重排后 You 2017=**[19]**、Lorenzo=[18]、Thakur=[17]、退相干链=[36]-[39]。本轮判定一律以磁盘现行编号为准。
> 时间线说明：两处 critical 靶子在本任务包发射（2026-11-03T16:24:30Z）之前已由同日 writer 轮修复（sections 修改时间早于包发射时间）；本轮按契约逐条核销，并对修复的事实基础做联网复核。

## 一、遗留核对表（任务包核查靶子）

| # | 靶子 | 级别 | 判定 | 磁盘证据（行号为现行文本） |
|---|------|------|------|--------------------------|
| T1 | citation_integrity：You 2017 各向异性 HHG 样品 ZnO→MgO 全链（任务包：rationale §2.4 L65、content §2.5、scheme §3.4 校核一、references [20] 注释） | CRITICAL | ✓ 已解决（本轮联网复核事实基础后核销） | ① 正文全部 6 处挂 MgO：content L41「You 等人[19]于 2017 年在 MgO 单晶中报告 HHG 各向异性光谱……四重角分布」、scheme L11 / L91 / L189 / L195（校核一）/ L232 / L270 同口径；② references [19] 注释「MgO 单晶中 HHG 的晶体取向依赖……四重角分布，与立方结构一致」；③ 全稿 grep 无「You+ZnO」误挂——ZnO 侧各向异性已正确挂 Jessen[28]（content L41「ZnO 块体……并报告谐波发射的各向异性谱学性质」）；④ 旧 L81-83 对照维度论述（现 rationale L85-L93）已改写为「ZnO 与 MgO 共同承担非拓扑参考角色」：ZnO 承担多通道竞争区、MgO 承担纯对称性各向异性扣除，无以 ZnO 各向异性为对照维度的残留；⑤ [20] 现挂 Ciappina 2025 综述（rationale L9、content L15），与 You 2017 无涉，联网核实该综述真实存在（Adv. Phys. 74, 1-9, 2025） |
| T2 | indicator_consistency：G1 样本协议两版（各≥200 vs 各 N=100） | CRITICAL | ✓ 已解决（核销） | ① content L17「样本规模取高阶拓扑相与低阶拓扑相各不少于 200 个独立随机参数样本」；② scheme L67「两类样本数各为 N，N 以 200 为下限，与研究内容方向一的样本协议一致」，并含 G1 = N_correct/(2N) 计算式与判定操作（双变量指纹落域）；③ full_review L34 统一表述表「各类 N ≥ 200，与方向一样本协议一致……统计功效足够」；④ 全稿 grep「N=100 / 各 100 个」= 0。三处同一口径，互斥解除 |

## 二、上轮（2026-11-01）low 豁免项消化情况

| # | 豁免项 | 状态 | 证据 |
|---|--------|------|------|
| B | 「陈绝缘体/Chern 绝缘体」译名混用 | ✓ 已消化（writer 轮完成） | grep「陈绝缘体」全稿 = 0，统一「Chern 绝缘体」 |
| C | S:L109（现 L109）[18]→现[17] Thakur「三类贡献独立指纹」归属待核实 | → 本轮联网核实并修复（见 N1） | arXiv:2609.06119 摘要实测：证实边带强度对相对螺旋性与偏振面取向高度敏感 + 电子-空穴退相干时钟；**未**主张 Weyl 节点/Berry 曲率/散射三类指纹彼此独立 |
| D | C:L7 依赖链「方向一至三」含自身微瑕 | ✓ 已消化（writer 轮完成） | 现 content L7 依赖链为「方向二、三的算法载体／方向三与方向四的判据集在对照验证处交汇」，无自含式表述；余处「标定方向一至三所产拓扑判据」（L57/L71）语义正确（方向四标定一至三） |

## 三、新发现表（本轮 ≤5 条）

| # | 类别 | 位置 | 描述 | 处置 |
|---|------|------|------|------|
| N1 | citation_attribution [medium] | scheme L109 | 「三类贡献各自具备独立指纹目前仅有 [17] 摘要级证据」超出 arXiv:2609.06119 摘要实际内容（摘要给出的是偏振依赖指纹通道与退相干时钟，非三类指纹独立性证明） | 本轮修复：改「摘要级旁证——边带指纹的偏振依赖通道与电子-空穴退相干时钟，该摘要未直接证明三类指纹彼此独立」，保留「严格成立是本方案首要检验内容」的检验定位 |
| N2 | citation_terminology [medium] | rationale L65 + references [27] 注释 | 「Bloch 反常速度与 Berry 曲率」与 [27] 摘要原文「interplay of Bloch velocity and anomalous Hall velocity」不对应：反常霍尔速度即 Berry 曲率项，与 Berry 曲率并列属同义反复，且丢失 Bloch 群速度半边 | 本轮修复（联网核实有据）：rationale 改「Bloch 群速度与 Berry 曲率决定的反常霍尔速度」，references [27] 注释同步「Bloch 群速度与反常霍尔速度（Berry 曲率项）的竞争」；摘要中「魔比例 1.5:1」「MoS₂ 双峰（1.5:1 与单色极限）」「hBN 单调上升」三项数值/现象描述与原文一致，无需改动 |
| N3 | pointer_integrity [medium] | rationale L29 | 「是上文二维 Chern 绝缘体 HHG 工作的拓扑起点」指针悬空：上文（§2.1/§2.2 前文）无任何 Chern 绝缘体 HHG 工作，Chern 在全章首现即本句；实际所指是 L35 Lorenzo[18] 三模型对比的 Haldane/Chern 分支（后文） | 本轮修复：改「是下文三个紧束缚模型对比中 Chern 绝缘体分支的拓扑起点」，指向 L35 实锚；纯指针修正，无技术内容变更 |
| N4 | indicator_definition [medium，记录不修] | scheme L67 + full_review L34 | 「当两类样本数相等时，G1 与 δ_FP 互为补数，即 G1 = 1 − δ_FP」在 δ_FP 现行定义（「平庸相样本被误判为高阶拓扑相的占比」，content L17/scheme L47，单侧假阳性）下并非无条件成立：按 FP/N 口径需 FN=FP，按 FP/(2N) 口径需 FN=0。两阈值（δ_FP<5%、G1≥95%）在补数语义下自洽，属解释性附注的精度问题 | 记录不修：修正须先裁决 δ_FP 占比分母口径（属指标定义变更，跨 content/scheme/full_review 三处联动），留待下一 writer 轮统一处理；不阻塞本轮判定 |
| N5 | citation_unverified_detail [low，待核实] | rationale L65 | 「hBN 因 Berry 曲率较弱、色散各向异性较强而单调上升」的机制归因超出 [27] 摘要（摘要仅陈述 hBN 随 2ω 主导单调上升），本轮未能核实正文是否含此归因 | 记录待核实：如后续核实无据，删机制半句、保留「hBN 单调上升」现象描述即可；不阻塞 |

## 四、核查通过项（本轮定点抽查，无问题）

- 引用编号：references 40 条整、连续无跳号；正文最大引用 [40]；退相干参数链完整保留（旧[43]-[46]=现[36]-[39] Korolev/Walz/Klimmer/Thümmler），本轮零触碰。
- 口径表对齐：Lorenzo 增强量级 v2 口径（rationale L35「预印本首版/第二版」表述）、R=2 保守下界 10²、Pilch 立方律→Z 下限 / Duan 裸膜 2.3→Z 上限、Δt=30/3≈10 fs、Neufeld 归因句式，均与 params.json canonical 一致；params-conflicts.json clean（23 项 0 冲突）。
- 十二项指标数值跨章一致：R_HOTI≥10 / S_edge≥0.2 / δ_FP<5% / Δκ≥20% / η_SF≥95% / Δt≤10fs / X+Y+Z≥95% / σ_dec≤5pp / R²≥0.9 / ΔI_rev≥0.5×I_threshold / ΔI_gap≥R=2 / δ_CD≥T=0.3，content §2.2-§2.6 ↔ scheme §2.2 ↔ full_review 统一表述表三处同值。
- [19] You 2017 / [20] Ciappina / [17] Thakur / [27] Fan 四条均经联网核实存在且属性（年份、期刊、样品、核心结论）与条目一致。
- 「预印本」标注与已刊状态无矛盾（[18][13][10][21] 等已刊条目正文均未误标预印本）。

复核依据汇总：本轮修复 4 处 Edit（rationale L29/L65、references [27]、scheme L109），修复后 grep 复核全部落盘；详细核销见 panel-verify-report.md。
