# ssh-weyl 开放问题快照（2026-10-03 评审团亲审输入）

## O1 [critical] rationale
1. [critical] evidence_fabrication｜§2.3 L39｜"TaP 的 2–3 个数量级增强（[16]）"原文无此数据｜删归属改"TaP THz 严格立方功率律（[16]）"

## O2 [critical] rationale
2. [critical] evidence_fabrication｜§2.2 L25 连锁 L49/55/59/67/79 及 scheme L61/L233｜Kagome"两到三个数量级"实为 up to 2 个｜全链改"至多两个数量级"并复核 R≥2 依据

## O3 [high] rationale
3. [high] rigor｜§2.2 L21｜[9] 实报"最高 14 个数量级"，正文"数个数量级"矮化失实｜改"最高达 14 个数量级（PRL 120, 177401）"

## O4 [high] rationale
4. [high] anti_ai｜L25/33/39/59/79 等 9 处｜禁用词"锚点/锚定/口径/落地"残留｜按映射改"量级基准/数值校准/判据定义/推广至材料"

## O5 [high] rationale
5. [high] anti_ai｜L25/39/57/79｜超 120 字句 4 处（全章 10 处）+元话语 L39｜L39 删"需要特别说明"并拆 3 句；L25/57/79 各拆 2 句

## O6 [critical] content
1. [critical] indicator_consistency｜content 全文 10 处（L7/11/15/19/41/43/55/67/69/83）+scheme 3 处｜"2-3 个数量级/100-1000 倍"与 rationale 已改"上限两个数量级（≤100 倍）"跨章互斥｜按 rationale L25 表述全链替换，grep 复核清零｜违 indicator_red_

## O7 [critical] content
2. [critical] evidence_fabrication｜L55/L69+scheme L61/L233｜R≥2 依据"取 2-3 个数量级增强的下界 100 倍"，[20] 实为至多两个数量级，100 倍是上限非下界，方向词错向｜改"取该增强上限 100 倍对应的对数尺度比值"并四处同步｜违 P0 连锁+no_exaggeration

## O8 [high] content
3. [high] evidence_orphan｜L41｜"比普通绝缘体高 2-3 个数量级已在多组数据中复现"无 [N] 无体系名，句后 [16] 仅报立方律无量级｜补引具体体系数据或删"多组数据复现"｜违 novelty_claim/证据充分性

## O9 [high] content
4. [high] anti_ai｜L13/25/43/51/61/67/71｜禁用词 7 处：门控 1、闭环 1、口径 3、锚点 2｜按映射改"单向依赖/递进验证/统计标准/实验基准"｜违 skill 三禁用词表

## O10 [high] content
5. [high] anti_ai｜全文｜自引用 18 次超阈值 15，程序罚 0.10｜非主张句删"本课题/立项依据的论证表明"，改直陈事实｜违 anti_ai_patterns+programmatic

## O11 [critical] scheme
1. [critical] indicator_consistency｜§2.2 L53、§3.2.2 L125、§7.1 L255 ↔ content L65/L81｜X+Y+Z 方案"≥95%"与内容"=100%"两套验收判据互斥｜content 两处改"≥95%（闭合条件 σ₀/σ_full<0.05）"与嵌套差分定义对齐｜违 indicator_red_lines.consistency_

## O12 [critical] scheme
2. [critical] evidence_fabrication（P0 残留）｜L43/L61/L233 及 references L43｜"2-3 个数量级（100-1000 倍）、取下界 100 倍"残留，content 已改"上限两个数量级（≤100 倍）"｜三处及 refs[20] 条目全改"上限两个数量级（≤100 倍）、取上限 100 倍"｜违 indicator_red_line

## O13 [high] scheme
3. [high] dead_pointer｜L35、L203｜"三条备选路径（详见 §4）"实为两条且无 TDDFT 切换；"如 §3.1 所述"处无神经网络内容｜L35 改"两条"并删 TDDFT 句或补第三条；L203 删括注｜违 section_standards.scheme 第 4 条

## O14 [high] scheme
4. [high] timeline_inversion｜§6 L237｜年度计划起于 2026.01，早于课题建档（2026-09）与最早资助起点｜整体平移至 2027.01–2020.12，论文撰写分流至第 3-4 年｜违 review_checklist 第 5 条

## O15 [high] scheme
5. [high] anti_ai（programmatic）｜全章 16 处自引用（本课题/本框架/本节/本工程）超阈 15，罚 0.10｜非主张句删自称直陈对象，"本工程"改"本节"｜违 anti_ai_patterns.self_reference

## O16 [high] scheme
6. [high] scheme_duplication｜§3.2.2 L125｜"该判据与多带引擎在 Weyl 半金属极限下的基准测试一致"同段句首句尾重复两次｜删句尾重复句｜违叙述式写作规范第 1 条
