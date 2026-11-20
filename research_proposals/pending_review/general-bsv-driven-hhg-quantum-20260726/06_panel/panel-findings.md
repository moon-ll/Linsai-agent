# 评审团定点核查报告（panel-findings）

- 课题：general-bsv-driven-hhg-quantum-20260726
- 日期：2026-11-04（引擎亲审模式：评审员=执行者本人，未调用任何外部 LLM/脚本跑评审）
- 本轮性质：**退回后完善轮的主动深审**（课题自 pending_review 人工退回、轮次归零，rationale/references 于 11-04、content/scheme/full_review 于 11-03 被管线重写）——重点核查重写质量
- 核查范围：04_proposal/sections/ 五文件全文实读 + 04_proposal/params.json（数值单一真相源）+ 05_review/params-conflicts.json（clean=true，零残留）+ 检索池/KB/联网核证
- 核查维度：引用完整性（角标-钩挂对账）/ 引用真实性（联网核验）/ 口径一致性（params.json 禁用值）/ 超长句 / AI 模板句 / 跨章结构

## 一、上轮（2026-11-01）修复幸存性核对

| 上轮条目 | 幸存状态 | 证据 |
|---|---|---|
| 修复 1：rationale §1.2.2 Schleich-Wheeler 首提及补角标（原 [18]） | **幸存**（重编号后仍在） | rationale.md L25 现文"Schleich-Wheeler 框架[16]给出"（参考文献表重排后 [18]→[16]，指向同一 Schleich-Wheeler 1987 JOSA B 条目） |
| 修复 2：references [18]（现 [16]）挂钩更正为"§1.2.2、§3.2" | **部分幸存**——挂钩注释幸存；但 §3.2 位置的正文角标被本轮重写剥除，挂钩一度重新虚标 | 重写后 scheme.md §3.2"Schleich-Wheeler 框架"无角标；本轮已恢复（见 P2） |
| 修复 3：content §2.0 L5 155 汉字长句拆分 | **幸存** | content.md L5 保持"总起句 + 物理层/方法学层/反演精度层分述 + 收束句"结构，全稿 >120 汉字句复扫零命中 |
| 上轮 T1：QEF 三指标实名口径（vis / yield(q_ref) / yield(Σ)） | **幸存** | rationale §1.4 与 content §2.3 L65 三指标实名枚举逐项一致，无"噪声关联比"残留（五文件 grep 零命中） |
| 上轮 low P3："强度—偏振—干涉三维对比"第三维枚举 | **被重写消解** | 该短语 rationale.md grep 零命中；L9 现文改为"产额与干涉可见度构成两个主对比量，偏振态作为主动扫描参数一并记录而非独立对比维度"，枚举矛盾不复存在 |
| 上轮 low P4：挂钩清单缺实引位置（[1]/[9]/[23]/[24]/[25]） | **被重写重构**——旧挂钩体系整体重排；重排后出现反向缺陷（见 P2），本轮对账后归零 | 本轮机检：46 条钩挂与正文角标逐一对应，零幻影、零缺漏 |
| 上轮 low P5：content 64 处直引号 | **恶化**（rationale 加入直引号阵营） | 直引号计数：rationale 56 + content 64，scheme/full_review 为弯引号；本轮仍豁免（见 P4） |

## 二、新发现问题（本轮主动发现，共 4 条）

| 编号 | 级别 | 位置 | 问题 | 处置 |
|---|---|---|---|---|
| P1 | high | content.md L53/L55/L71、scheme.md L97/L99/L125 | **4 篇文献以内联书目形式在正文引用但不入参考文献表**：Wang 等 npj Quantum Materials **11**, 68 (2026)；Prajapati 等 PRB **113**, 045118 (2026)；Sumaya-Martinez 与 Mulia-Rodriguez arXiv: 2512.23538；Raissi 等 JCP **378**, 686–707 (2019)。与体例说明"本表条目与正文角标一一对应"直接冲突，且 NSFC 规范要求凡引必列 | 增补 [43]–[46] 四条条目 + 正文 6 处改角标并删除内联书目括注。书目依据：CrossRef/arXiv 官方源逐条联网核验通过（4/4）+ KB 论文页佐证（2507.10832 / 2410.01424 / 2512.23538 均有全文级蒸馏页）+ 历史编号条目原样在案（05_review/.monitor-diff-r1/-r5/-r8） |
| P2 | high | rationale/content/scheme 全文 | **退回重写系统性剥除正文角标**：退回前 r7 稿正文 127 个角标 → 重写后仅 45 个（统一口径：剔除数学区间、[n,n] 连标对计 2）；约 30 处钩挂声称位置失去角标成为幻影（重灾区：scheme §3.3–§3.7 全部机制叙述、content §2.3/§2.5 对照体系与创新点段、rationale §1.2.3/§1.3），违背"条目末挂钩注释给出承担论证位置"的体例契约；含上轮修复 2 的回退（[16] §3.2） | 恢复被剥除的正文角标（机检角标总数 45 → 96，恢复 51 处），同步校正 4 条钩挂（[7] 删 §2.2/§3.3/§3.6、[9] 删 §3.7、[13] 删 §3.7、[36] 删 §2.1——四处经实读确认正文确无对应论证位）；机检对账 46 条钩挂零幻影、零多余，条目编号连续 1–46 |
| P3 | medium | full_review.md L33（跨章对照表） | r 扫描上限依据行把"压缩光截止方差极小值 r_opt≈1.6 [36]"论证归属到左栏"立项依据/研究内容（§2.1）"，实读确认该论证仅在方案章 §3.3（content §2.1 只给 r∈[0.5,1.5] 区间、无 r_opt 机制论证）；[36] 钩挂随之虚标 §2.1 | 表格行改写：r 区间设定归 §2.1（左栏），r_opt≈1.6 [36] 机制论证移入右栏 §3.3；[36] 钩挂删 §2.1 |
| P4 | low | rationale.md/content.md 全文标点体例 | 直引号/弯引号体例分裂扩大：rationale 56 处 + content 64 处直引号，scheme/full_review 为弯引号（上轮仅 content 64 处） | 记录不改（豁免）：引号均成对出现、无歧义，120 处批量替换超出本轮保守修改边界；建议 writer 轮统一为弯引号 |

## 三、本轮评审团直接修复清单（5 文件 46 处编辑，恢复/新增正文角标 51 处；角标/挂钩/表格归属层面，零数值、零技术结论改动）

1. **references.md**：追加 [43] Wang（npj QM）/ [44] Prajapati（PRB）/ [45] Sumaya-Martinez（arXiv）/ [46] Raissi（JCP）四条条目（含挂钩注释）；钩挂校正 4 处（[7]/[9]/[13]/[36]）。
2. **rationale.md**（4 处）：L35 Stammer 等[27]、L49 Stammer 等[27] 与 de-la-Peña 等[28]、L65 Jiang 与 Dorfman[20]。
3. **content.md**（20 处角标）：L25 Liu[6]、L27 Iglesias[14]、L29 Gothelf[21]、L33 Even Tzur[2]、L43 双粒子方案[9]、L51 Wu[11]、L53 Wang[43]、L55 Lange[22] 与 Prajapati[44]、L61 Jabed[37]、L71 Sumaya[45]、L77 Li[10]、L85 Even Tzur[32]、L109 Even Tzur[2] 与 Gothelf[21]、L111 时域干涉反演[8] 与量子工程化框架[12]、L113 Boroumand[12] 与 Jiang-Dorfman[20]、L117 Rasputnyi[1]。
4. **scheme.md**（27 处角标）：L25 Schleich-Wheeler[16]（上轮修复回退点）、L33 Wu[11]、L47 Tyulnev[38]、L49 Iglesias[14]/Liu[6]/Gothelf[21]/Berry 曲率反演[17]/闭式解[33]、L51 Even Tzur[2]/Ehrenfest[19]、L87 Jiang-Dorfman[20]/阿秒层析[32]、L91 Li[10]、L97 Sumaya[45]、L99 Raissi[46]（内联书目括注删除）、L107 Rasputnyi[1]/阿秒重建[32]、L109 Liu[6]/Murakami[7]、L111 Wu[5]/Rivera-Dean[13]、L123 Ehrenfest[19]、L125 Prajapati[44]、L133 SBE[5]/气体原子框架[2]、L135 钨针尖干涉[10]/Boroumand[12]。
5. **full_review.md**（1 处）：r 扫描上限依据行归属改写（P3）。

## 四、已核实无问题项（非缺陷，记录备查）

- **本轮联网核验 4/4 通过**（CrossRef/arXiv 官方源）：[43] Wang Y. "Failed superconductivity in a Mott spin liquid material" npj QM 11, 68 (2026) DOI 10.1038/s41535-026-00890-8 吻合；[44] Prajapati "Terahertz harmonic generation across the Mott insulator-metal transition" PRB 113, 045118 (2026) DOI 10.1103/ydjj-xxcl 吻合（上轮已验，本轮复验）；[45] Sumaya-Martinez & Mulia-Rodriguez arXiv:2512.23538 (2025, v1) 标题作者吻合；[46] Raissi/Perdikaris/Karniadakis JCP 378, 686–707 (2019) DOI 10.1016/j.jcp.2018.10.045 吻合（作者序 Raissi 一作，与历史 CrossRef 更正记录一致）。
- params.json 两条 canonical 联动禁用旧值（5 μm FWHM 聚焦/5 nJ/2×10^10/0.1 MW/3.3×10^10/"光子数上限"表述）五文件 grep 零命中——零回退；内推链现文与 canonical 逐步一致（3 μm FWHM → 7×10⁻⁸ cm² → 0.035 MW → 1.8 nJ → 7×10⁹）。
- 引用真实性存量抽查：正文全部 46 条编号引用的书目信息均有 KB 页/历史条目/上轮联网核验三重来源支撑，未发现凭记忆杜撰条目。
- 长句终扫：正文四文件 >120 汉字句零命中（references 条目注释为书目文体不计）。
- AI 模板句扫描（值得注意的是/需要指出的是/综上所述/总而言之/不难看出/众所周知/赋能/抓手）：四正文文件零命中。
- 跨章关键数值一致：T₂∈[1,16] fs 中位 10 fs / 3.7 倍周期比（content §2.2 = scheme §3.3 = full_review 表）；R²≥0.7 + AIC≥10 门限三处一致；V=0.4→2100、V=0.3→4000、δ_q≤5%↔800 计数链一致；κ-Br T_c≈11.5 K、莫尔 126 meV/285 K 与 [11] 注释一致。
- full_review 骨架纯净：1490 中文字量级、无工作记录特征，"全文逻辑骨架"头正确。
- 05_review/params-conflicts.json：clean=true、conflicts=[]（2026-11-03T16:11:14Z，round 2），零残留。
