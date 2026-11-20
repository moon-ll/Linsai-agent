# 评审团任务包（引擎亲审，v7.2.97）

- **课题**：general-ssh-weyl-20260920
- **状态**：optimizing
- **发射时间**：2026-11-16T02:00:50Z
- **执行者**：任意 agent 入口（协作引擎 / CLI agent / 人工评审会话）——
  按本包与 quality-review skill 契约执行，**评审员 = 你本人**：
  亲自读文、核查、修改、复核，不调用其它 LLM、不外包内置模型。

## 核查靶子（历史遗留问题，逐条核对当前文本是否仍存在）

1. [CRITICAL] 1. [critical] physics｜§2.2 L35｜Haldane 模型对称性表述与原文相反：复相位次近邻跃迁破缺的是时间反演对称而非反演对称，纯 Haldane 模型反演对称保留｜改"破缺时间反演对称而保留反演与平移对称"（action: rewrite；违反 rigor 科学正确性、rubric rigor③）

## 程序化术语扫描靶子（terminology_scanner 零 LLM 候选，非结论——逐条人工/亲审核定真伪，真者入 findings 处置）

- CJK 候选对: 非拓扑(50) ↔ 高阶拓扑(37) @ content,full_review
- CJK 候选对: 拓扑相(91) ↔ 退相(91) @ content,full_review
- CJK 候选对: 极化(59) ↔ 归一化(54) @ content,method_manual
- CJK 候选对: 方程(76) ↔ 方向三(52) @ content,full_review
- CJK 候选对: 方程(76) ↔ 方向四(50) @ content,full_review
- CJK 候选对: 样本(190) ↔ 预印本(49) @ content,full_review
- 记号组 [T_2]: T_2 / T₂
- 记号组 [N_k]: N_k / N_k^
- 记号组 [R_2]: R^2 / R²
- 记号组 [I_f]: I_f / I_f^
- 记号组 [on_n]: on_n / on_{n
- 记号组 [log_10]: log_{10 / log₁₀

## 课题文件
- 章节：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-ssh-weyl-20260920/04_proposal/sections/ 下 rationale.md / content.md / scheme.md / full_review.md / references.md
- 口径表：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-ssh-weyl-20260920/04_proposal/params.json（如存在 = 数值单一真相源，相关修改必须与 canonical 一致）
- 待清项：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-ssh-weyl-20260920/05_review/params-conflicts.json（如有残留，一并核查）
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
- /Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-ssh-weyl-20260920/06_panel/panel-findings.md（遗留核对表 + 新发现表）
- /Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-ssh-weyl-20260920/06_panel/panel-verify-report.md（核销表 | 条目号 | 级别 | 已解决/部分/未解决/豁免 | 文本证据 | + 末行「复核结论: 通过/需返工」）

## 红线（skill 七节，强制）
- 引用三源对照零容忍（lit-gap-*.md / candidates-*.bib / reading-notes.md），
  池中无记录的条目一律不得写入；违反按 critical 计
- 口径表一致；跨章重复按「单一出处+指针」收敛；超长句仅拆句，
  禁改技术内容/数值/公式/引用编号
- 只改本课题 04_proposal/sections/ 下 5 文件 + 06_panel/ 产物

## 执行完成后的标准收尾

    python3 scripts/panel_review.py --adopt-engine general-ssh-weyl-20260920

（解析核销表清账 → 锚集 pairwise 守卫 → optimizing 课题晋级 pending_review + 7 天否决窗口）
