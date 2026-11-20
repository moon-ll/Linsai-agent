# 评审团任务包（引擎亲审，v7.2.97）

- **课题**：general-phonon-hhg-20261101
- **状态**：optimizing
- **发射时间**：2026-11-11T02:00:10Z
- **执行者**：任意 agent 入口（协作引擎 / CLI agent / 人工评审会话）——
  按本包与 quality-review skill 契约执行，**评审员 = 你本人**：
  亲自读文、核查、修改、复核，不调用其它 LLM、不外包内置模型。

## 核查靶子（历史遗留问题，逐条核对当前文本是否仍存在）

1. [CRITICAL] [critical] citation_misbinding｜rationale §2.3-§4（L41/L47/L53/L55/L57/L59/L75/L77/L81）｜具名与编号错位 13 处：Hu 2023 理论标[29]实指 Notter，Notter 标[31]实指 Yue，Li 标[32]实指 Parks 等｜按 references 表重绑 13 处并逐号 grep 具名复核，同步消
2. [CRITICAL] [critical] physics_error｜scheme L83、content L31｜E₂ 降 C₃ᵥ"阶次集合收紧"与 content"偶次转为允许"互斥，且 E₂ 面内畸变子群实为 C₂ᵥ｜统一为"偶次阶次由禁戒转为允许"并按 C₂ᵥ 重列核对表（P1）
3. [HIGH] [high] citation_order｜rationale §2 L19-L57｜首现逆序 56 对：[37][39][40][38]插入未重排、[18]全稿末现｜按全稿首现顺序重排编号并同步四章（违学术规范·顺序编码制；上轮 19 对未处置反增至 56，浮出升级）
4. [HIGH] [high] physics_check｜scheme L79（content L31/L37 指针受牵连）｜"极性模与非极性模分别对应不同的点群改变，允许的阶次集合随之不同"——wurtzite A₁(LO) 沿 c 位移保持 C₆ᵥ，不改阶次集合｜改为零/非零对照：A₁(LO) 点群不变、w_q 理论预期为零，E₂ 降点群给非零预期。
5. [HIGH] 1. [high] citation_misbinding｜scheme L209｜郑文洋等[47]被引作"偏振取向 30° 偏移"证据，实为 h-BN 取向依赖 HHG 文，缺"约 30°"原文锚｜核对原文献偏移数值后改写，或在 rationale §2.5 挂真实 30° 来源并同步 scheme｜违 rigor③、indicator_red_lines.novelty_claim_cauti
6. [HIGH] 2. [high] consistency_issue｜content L53 vs scheme L175｜UED：content 称"可回查的超快电子衍射"，scheme 明言"该项目内搭建、检索未见先例可援引、只列核对项"——既有手段与自建手段互斥｜content L53 删"可回查"，改"拟引入的超快电子衍射"｜违 indicator_red_lines.consistency_check
7. [HIGH] [high] physics_check｜scheme L47｜I_p 同名两口径：ZnO 取带隙 3.37 eV、MoS₂/1T-TaS₂ 取真空电离能 5.2/5.0 eV，档界方向随定义翻转｜统一定义并按真实带隙（或真空 IP）重算三档边界（P1）
8. [HIGH] [high] consistency_issue｜content L5 vs scheme L229/L233｜同一 novelty 声明检索关键词两版（两词/三词），L233 又缺"检索范围内"限定｜统一关键词集并补检索范围限定语，违 novelty_claim_cautious（P1）
9. [HIGH] [high] logic_contradiction｜rationale L31-33｜"2022 年以后的一组工作"组内以"随后"引出 Bionta 2021，时序倒挂｜Bionta 句前移至 Neufeld 之前或删年份限定（P2）
10. [HIGH] [high]｜全表数量｜40→51 第四轮破限回涨，无数量设计声明｜裁并单点 2026 条目至≤45 并于头注声明，目标 40
11. [HIGH] [high]｜26 条回录｜历史簇与方法链 DOI/姓氏多形态全池零命中（R5 已令）｜按头注规则回录 reading-notes 并附增量 diff

## 程序化术语扫描靶子（terminology_scanner 零 LLM 候选，非结论——逐条人工/亲审核定真伪，真者入 findings 处置）

- CJK 候选对: 调制深度(74) ↔ 调制量(42) @ content,full_review
- CJK 候选对: 通道份额(52) ↔ 的份额(42) @ content,full_review
- CJK 候选对: 调制深度(74) ↔ 调制斜(32) @ content,full_review
- CJK 候选对: 通道份额(52) ↔ 通道的(32) @ content,full_review
- CJK 候选对: 度判据(38) ↔ 度标度判(32) @ content,method_manual
- CJK 候选对: 的调制(30) ↔ 关联调制(30) @ content,method_manual
- 记号组 [w_q]: w_q / w_q^
- 记号组 [δI_q]: δI_q / δI_q^
- 记号组 [n_d]: n_d / n_d^
- 记号组 [n_g]: n_g / n_g^
- 记号组 [I_0]: I_0 / I₀
- 记号组 [n_eff]: n^{eff / n_eff

## 课题文件
- 章节：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-phonon-hhg-20261101/04_proposal/sections/ 下 rationale.md / content.md / scheme.md / full_review.md / references.md
- 口径表：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-phonon-hhg-20261101/04_proposal/params.json（如存在 = 数值单一真相源，相关修改必须与 canonical 一致）
- 待清项：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-phonon-hhg-20261101/05_review/params-conflicts.json（如有残留，一并核查）
- 预审参考（非结论）：06_panel-preaudit-*/（如有）

## 五步流程（契约全文见 /Users/ll/Desktop/LinSai-CoPilot/.hermes/skills/quality-review/SKILL.md 第五~七节）
1. **定点核查**：通读 5 章节，靶子逐条判定（引用行号+原文），新发现 ≤5 条
2. **深度修改**：critical/high 必修，直接编辑章节文件；数值/引用类修改
   必须有据（口径表/检索池/联网核实），禁止凭记忆；拿不准标「待核实」。
   对实质不同意的 finding 可走**辩驳-仲裁子流程**（v7.3.60）：
   --rebuttal-scaffold 生成脚手架 → 填反驳行 → 单点仲裁 → --arbitrate 落账
   （契约见 skill 七节；仲裁只扫 contested 子集，不触全轮重评）
3. **复核**：以修改后的磁盘文本为准逐条判定
4. **判定**：任一 critical/high 未解决 → 需返工；否则通过
5. **收尾**：运行下方标准收尾命令

## 输出契约（skill 六/七节）
- /Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-phonon-hhg-20261101/06_panel/panel-findings.md（遗留核对表 + 新发现表）
- /Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-phonon-hhg-20261101/06_panel/panel-verify-report.md（核销表 | 条目号 | 级别 | 已解决/部分/未解决/豁免 | 文本证据 | + 末行「复核结论: 通过/需返工」）

## 红线（skill 七节，强制）
- 引用三源对照零容忍（lit-gap-*.md / candidates-*.bib / reading-notes.md），
  池中无记录的条目一律不得写入；违反按 critical 计
- 口径表一致；跨章重复按「单一出处+指针」收敛；超长句仅拆句，
  禁改技术内容/数值/公式/引用编号
- 只改本课题 04_proposal/sections/ 下 5 文件 + 06_panel/ 产物

## 执行完成后的标准收尾

    python3 scripts/panel_review.py --adopt-engine general-phonon-hhg-20261101

（解析核销表清账 → 锚集 pairwise 守卫 → optimizing 课题晋级 pending_review + 7 天否决窗口）
