# 评审团任务包（引擎亲审，v7.2.97）

- **课题**：general-berry-mnps3-rashba-20260816
- **状态**：optimizing
- **发射时间**：2026-11-03T16:24:30Z
- **执行者**：任意 agent 入口（协作引擎 / CLI agent / 人工评审会话）——
  按本包与 quality-review skill 契约执行，**评审员 = 你本人**：
  亲自读文、核查、修改、复核，不调用其它 LLM、不外包内置模型。

## 核查靶子（历史遗留问题，逐条核对当前文本是否仍存在）

（无历史遗留问题，本轮以主动深审为主：按角色职责发现新问题）

## 课题文件
- 章节：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-berry-mnps3-rashba-20260816/04_proposal/sections/ 下 rationale.md / content.md / scheme.md / full_review.md / references.md
- 口径表：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-berry-mnps3-rashba-20260816/04_proposal/params.json（如存在 = 数值单一真相源，相关修改必须与 canonical 一致）
- 待清项：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-berry-mnps3-rashba-20260816/05_review/params-conflicts.json（如有残留，一并核查）
- 预审参考（非结论）：06_panel-preaudit-*/（如有）

## 五步流程（契约全文见 /Users/ll/Desktop/LinSai-CoPilot/.hermes/skills/quality-review/SKILL.md 第五~七节）
1. **定点核查**：通读 5 章节，靶子逐条判定（引用行号+原文），新发现 ≤5 条
2. **深度修改**：critical/high 必修，直接编辑章节文件；数值/引用类修改
   必须有据（口径表/检索池/联网核实），禁止凭记忆；拿不准标「待核实」
3. **复核**：以修改后的磁盘文本为准逐条判定
4. **判定**：任一 critical/high 未解决 → 需返工；否则通过
5. **收尾**：运行下方标准收尾命令

## 输出契约（skill 六/七节）
- /Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-berry-mnps3-rashba-20260816/06_panel/panel-findings.md（遗留核对表 + 新发现表）
- /Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-berry-mnps3-rashba-20260816/06_panel/panel-verify-report.md（核销表 | 条目号 | 级别 | 已解决/部分/未解决/豁免 | 文本证据 | + 末行「复核结论: 通过/需返工」）

## 红线（skill 七节，强制）
- 引用三源对照零容忍（lit-gap-*.md / candidates-*.bib / reading-notes.md），
  池中无记录的条目一律不得写入；违反按 critical 计
- 口径表一致；跨章重复按「单一出处+指针」收敛；超长句仅拆句，
  禁改技术内容/数值/公式/引用编号
- 只改本课题 04_proposal/sections/ 下 5 文件 + 06_panel/ 产物

## 执行完成后的标准收尾

    python3 scripts/panel_review.py --adopt-engine general-berry-mnps3-rashba-20260816

（解析核销表清账 → 锚集 pairwise 守卫 → optimizing 课题晋级 pending_review + 7 天否决窗口）
