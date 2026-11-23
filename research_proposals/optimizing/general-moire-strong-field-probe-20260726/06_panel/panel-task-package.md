# 评审团任务包（引擎亲审，v7.2.97）

- **课题**：general-moire-strong-field-probe-20260726
- **状态**：optimizing
- **发射时间**：2026-11-06T15:25:02Z
- **执行者**：任意 agent 入口（协作引擎 / CLI agent / 人工评审会话）——
  按本包与 quality-review skill 契约执行，**评审员 = 你本人**：
  亲自读文、核查、修改、复核，不调用其它 LLM、不外包内置模型。

## 核查靶子（历史遗留问题，逐条核对当前文本是否仍存在）

1. [CRITICAL] 1. [critical] self_conflict｜§1.5 L111–L113｜No-Go 余量判据(<5倍不可行)与同段"尚有2.3–9倍余量"互斥｜判据改为区间分段判定或注明 I_c 取典型带下段｜P1
2. [CRITICAL] 2. [critical] citation_integrity｜§1.4 L81｜[6] Molinero 为纯理论模拟，误称"实测谱"｜删"实测"改"数值模拟谱"｜P1
3. [CRITICAL] 1. [critical] indicator_conflict｜scheme L283 ↔ rat L117/con L23/sch L151·L194｜I_c 上端两版：L283"上端 2×10¹¹ 余量收窄至 5 倍"vs 他处 2.3×10¹¹ 且余量 4.3 倍判不可达｜L283 改 2.3×10¹¹，余量句改"4.3 倍低于 5 倍判据，该端不可达"｜violates indicato
4. [CRITICAL] 2. [critical] indicator_conflict｜scheme L153·L196 ↔ canonical 表｜1.3 μm 端三端点两版：正文 3.7×10¹⁰/4.4×10¹¹/1.2×10¹² vs canonical 2.7×10¹⁰/4.3×10¹¹/1.1×10¹²｜复算按当前 3 μm 带×5.325 得 3.7/4.3/1.2：正文 4.4 改 4.3；canoni

## 课题文件
- 章节：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-moire-strong-field-probe-20260726/04_proposal/sections/ 下 rationale.md / content.md / scheme.md / full_review.md / references.md
- 口径表：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-moire-strong-field-probe-20260726/04_proposal/params.json（如存在 = 数值单一真相源，相关修改必须与 canonical 一致）
- 待清项：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-moire-strong-field-probe-20260726/05_review/params-conflicts.json（如有残留，一并核查）
- 预审参考（非结论）：06_panel-preaudit-*/（如有）

## 五步流程（契约全文见 /Users/ll/Desktop/LinSai-CoPilot/.hermes/skills/quality-review/SKILL.md 第五~七节）
1. **定点核查**：通读 5 章节，靶子逐条判定（引用行号+原文），新发现 ≤5 条
2. **深度修改**：critical/high 必修，直接编辑章节文件；数值/引用类修改
   必须有据（口径表/检索池/联网核实），禁止凭记忆；拿不准标「待核实」
3. **复核**：以修改后的磁盘文本为准逐条判定
4. **判定**：任一 critical/high 未解决 → 需返工；否则通过
5. **收尾**：运行下方标准收尾命令

## 输出契约（skill 六/七节）
- /Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-moire-strong-field-probe-20260726/06_panel/panel-findings.md（遗留核对表 + 新发现表）
- /Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-moire-strong-field-probe-20260726/06_panel/panel-verify-report.md（核销表 | 条目号 | 级别 | 已解决/部分/未解决/豁免 | 文本证据 | + 末行「复核结论: 通过/需返工」）

## 红线（skill 七节，强制）
- 引用三源对照零容忍（lit-gap-*.md / candidates-*.bib / reading-notes.md），
  池中无记录的条目一律不得写入；违反按 critical 计
- 口径表一致；跨章重复按「单一出处+指针」收敛；超长句仅拆句，
  禁改技术内容/数值/公式/引用编号
- 只改本课题 04_proposal/sections/ 下 5 文件 + 06_panel/ 产物

## 执行完成后的标准收尾

    python3 scripts/panel_review.py --adopt-engine general-moire-strong-field-probe-20260726

（解析核销表清账 → 锚集 pairwise 守卫 → optimizing 课题晋级 pending_review + 7 天否决窗口）
