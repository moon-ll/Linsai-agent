# 评审团任务包（引擎亲审，v7.2.97）

- **课题**：general-houston-kronig-penney-landau-zener-20261004
- **状态**：optimizing
- **发射时间**：2026-11-11T02:00:13Z
- **执行者**：任意 agent 入口（协作引擎 / CLI agent / 人工评审会话）——
  按本包与 quality-review skill 契约执行，**评审员 = 你本人**：
  亲自读文、核查、修改、复核，不调用其它 LLM、不外包内置模型。

## 核查靶子（历史遗留问题，逐条核对当前文本是否仍存在）

1. [CRITICAL] 1. [critical] indicator_conflict｜§3.2 L121 与 §7 L261 vs §3.4 L165｜MgO 缺陷档位分数两版：0.02%–0.2% 对 1.9×10⁻⁴%–1.9×10⁻²%（差 10–100 倍）｜两处统一改 1.9×10⁻⁴%–1.9×10⁻²%（对应 10¹⁷–10¹⁹ cm⁻³），ZnO 括注 0.05%–0.5% 同步改 2.4×10⁻⁴%
2. [HIGH] [high] anti_ai｜rationale L27/L49/L73｜>120 字超长句 3 处（126/146/145 字），程序计罚 23 处扣 0.32｜按分号拆 2–3 句，主语动词前断句｜违 anti_ai_patterns"超 120 字属严重超长句"
3. [HIGH] [high] narrative｜§2.2（L41–67）｜13 段中 7 段单文献汇报（L53/55/57/59/63/65/67），混淆源主线被淹没｜L59/63/65 并段压缩为支撑句，突出机制＋退相干两条混淆源｜违 rationale_anchor"逐步收窄到核心挑战"
4. [HIGH] 1. [high] indicator_conflict｜§2.2 L27 vs §2.5 L79/L81｜"两重一致性检验"与"两项一致性"同章两版且判据集合不同｜L27 改"两项一致性检验"并对齐目标一集合，无反项检验单列辅助句｜违 indicator_red_lines.consistency_check + rigor②
5. [HIGH] 2. [high] pointer｜§2.3 L51 vs scheme §3.2｜"完整分工见研究方案 §3.2"而 scheme 该处回指"分工见研究内容 §2.3"，互指环｜分工实文本在 L49-51，L51 改"三项判据的能区分工即如上"删指针；scheme 侧保留端点执行协议｜违 indicator_red_lines.implementation_path

## 程序化术语扫描靶子（terminology_scanner 零 LLM 候选，非结论——逐条人工/亲审核定真伪，真者入 findings 处置）

- CJK 候选对: 反常谐波(42) ↔ 反常电(39) @ content,method_manual
- CJK 候选对: 反常谐(44) ↔ 反常电流(37) @ content,method_manual
- CJK 候选对: 反常谐波(42) ↔ 反常电流(37) @ content,method_manual
- CJK 候选对: 象限材料(36) ↔ 跨材料(34) @ content,full_review
- CJK 候选对: 偶次谐波(37) ↔ 高次谐波(24) @ content,full_review
- CJK 候选对: 缺陷密度(37) ↔ 缺陷超(24) @ content,full_review
- 记号组 [T_2]: T_2 / T_{2 / T₂
- 记号组 [cm_2]: cm^2 / cm²
- 记号组 [n_n]: n_n / n_n^

## 课题文件
- 章节：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-houston-kronig-penney-landau-zener-20261004/04_proposal/sections/ 下 rationale.md / content.md / scheme.md / full_review.md / references.md
- 口径表：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-houston-kronig-penney-landau-zener-20261004/04_proposal/params.json（如存在 = 数值单一真相源，相关修改必须与 canonical 一致）
- 待清项：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-houston-kronig-penney-landau-zener-20261004/05_review/params-conflicts.json（如有残留，一并核查）
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
- /Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-houston-kronig-penney-landau-zener-20261004/06_panel/panel-findings.md（遗留核对表 + 新发现表）
- /Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-houston-kronig-penney-landau-zener-20261004/06_panel/panel-verify-report.md（核销表 | 条目号 | 级别 | 已解决/部分/未解决/豁免 | 文本证据 | + 末行「复核结论: 通过/需返工」）

## 红线（skill 七节，强制）
- 引用三源对照零容忍（lit-gap-*.md / candidates-*.bib / reading-notes.md），
  池中无记录的条目一律不得写入；违反按 critical 计
- 口径表一致；跨章重复按「单一出处+指针」收敛；超长句仅拆句，
  禁改技术内容/数值/公式/引用编号
- 只改本课题 04_proposal/sections/ 下 5 文件 + 06_panel/ 产物

## 执行完成后的标准收尾

    python3 scripts/panel_review.py --adopt-engine general-houston-kronig-penney-landau-zener-20261004

（解析核销表清账 → 锚集 pairwise 守卫 → optimizing 课题晋级 pending_review + 7 天否决窗口）
