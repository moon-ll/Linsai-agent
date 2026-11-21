# 评审团任务包（引擎亲审，v7.2.97）

- **课题**：general-vortex-oam-hhg-20261101
- **状态**：optimizing
- **发射时间**：2026-11-15T15:12:56Z
- **执行者**：任意 agent 入口（协作引擎 / CLI agent / 人工评审会话）——
  按本包与 quality-review skill 契约执行，**评审员 = 你本人**：
  亲自读文、核查、修改、复核，不调用其它 LLM、不外包内置模型。

## 核查靶子（历史遗留问题，逐条核对当前文本是否仍存在）

1. [CRITICAL] [critical] indicator_red_line（P0）｜§三.1 阶次集合段（L17）｜"奇阶五项、偶阶两项"与 Q_main={3,5,7,9,11,13,15} 全奇集自相矛盾，偶阶判据零数据｜改集合含偶阶（如 {3,5,7} 奇 + {4,6,8} 偶）并同步 full_review L19
2. [CRITICAL] [critical] indicator_red_line（P0）｜scheme §三.1 L17 与 content §二.1/§二.3 G2 判据｜Si 带隙 1.1 eV、3 阶光子 1.16 eV 已在其上，主网格 Si 可用阶次为空，Si 无任何 l̄_q 读数，但 G2 判据要求"中心对称材料 A_sym=0"、G1 要求"五材料基线"｜把中心对称对照材料显式改为 MgO 单材料承担
3. [HIGH] 对抗结论：本轮 8 问题（critical 0/high 2/medium 5/low 1）；R2 的 8 项中 6 项已核销（含 critical η 两版），2 项残留（否定断言限定半体、513 meV 溯源），新增 5 项基于当前文本实判（归属错乱为 R2 计数词修复引入）。未达输出标准 0.85（差 0.02），瓶颈为严谨性 0.80——§1.4 归属拆句（high）与 513 溯源（me
4. [HIGH] 历史遗留核验：①G1 判据 vs 矩阵/机时（P0 critical）已解决——scheme §三.1"材料与几何不构成全交叉，35 个单元各自绑定一种几何"，机时链 56.0+112.0+2.4+4.2=174.6 与逐块换算（93.3+16.0+2.7=112.0）脚本复算吻合；②content 束腰句/Granados 句复现（high）已解决——束腰取值 content 仅 L53 一处且
5. [HIGH] 清单6. 通过——连贯叙述式行文，无条目堆砌段落，无 [high] narrative issue
6. [HIGH] [high] numeric_chain（P1）｜§三.1 L17 与 §三.4 L49 带隙关系｜"七阶在 ZnO 全部位带隙内"实仅 {3,5,7}（9 阶 3.48 eV＞3.37 eV）；"Q_cal 全部落在 ZnO 带隙以上"反向，{3,5,7} 在带隙内｜两处按 q×0.387 eV 复算改正关系词并全链统一
7. [HIGH] [high] redundancy（P1，R2 同型残留+新增）｜§三.7 首三段 vs §三.1/§三.2；§三.1/§三.7 vs content §二.1｜"不存在未验证环节""SBE 长度规范三优点""不依赖自身数据"逐句复述；"同一套光路上共存"先例句跨章三处（content §二.1 份 R2 指令未执行）｜§三.7 压为一句指代；content 份改"光路安排见§三.1"
8. [HIGH] [high] logic_conflict（P1）｜scheme §三.1 L19 仲裁扫描段｜"仲裁扫描取 3 个材料 × 2 几何共 6 个单元……同一材料在两种几何下的对照"直接违反三章既定"材料与几何非全交叉"配对约束（rationale §1.3 L69、content §二.1 L23、scheme §三.1 L13 三处均声明 ZnO/GaSe/MgO 透射、Si/WSe₂ 反射）｜
9. [HIGH] [high] indicator_measurable（P1）｜scheme §三.1 L17 Q_ax={5,7,9} 与仲裁/层析绑定｜Q_ax 9 阶光子 3.48 eV 高于 ZnO 带隙 3.37 eV，GaSe/WSe₂ 仅 5 阶可用；仲裁扫描取 Q_ax 同集合即在多数材料上无 7/9 阶数据，而 §三.8(3) 以"角谐分量阶数等于旋转对称性"为主判据需多阶对照｜把 Q_ax 改
10. [HIGH] [high] anti_ai（P1，程序化强制）｜三章 8 处 >120 字超长句（rationale 3、scheme 1，其余密集于技术性分句段）｜按程序化检测 long_sentences 逐处拆分，使单句 ≤120 字；超长句集中在 rationale §1.4 L91 三句枚举与 §1.2 L41 对照句（违 anti_ai_patterns.remove"超长句"；skill 四·5）
11. [HIGH] [high]｜[41] Wang 及 writer 处置记录｜r2 快照后新增 2 条仅披露 Voisine，[41] 零记载｜补记 [41] 池源（reading-notes-archive）与挂钩功能说明
12. [HIGH] - 严谨性 0.86：42/42 真实性全过、折著合规、DOI 体例统一、† 零漏标；扣分项为新增条目留痕缺位（high）与首页码体例跨轮未清（low）

## 程序化术语扫描靶子（terminology_scanner 零 LLM 候选，非结论——逐条人工/亲审核定真伪，真者入 findings 处置）

- CJK 候选对: 中心对称(28) ↔ 时间不对称(18) @ content,full_review
- CJK 候选对: 角动量(41) ↔ 角谐分量(26) @ content,method_manual
- CJK 候选对: 破缺量(72) ↔ 破缺窗口(21) @ content,full_review
- CJK 候选对: 的破缺(26) ↔ 称性破缺(20) @ content,full_review
- CJK 候选对: 通道份额(22) ↔ 通道的(20) @ content,full_review
- CJK 候选对: 破缺量(72) ↔ 破缺相图(19) @ content,full_review

## 课题文件
- 章节：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-vortex-oam-hhg-20261101/04_proposal/sections/ 下 rationale.md / content.md / scheme.md / full_review.md / references.md
- 口径表：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-vortex-oam-hhg-20261101/04_proposal/params.json（如存在 = 数值单一真相源，相关修改必须与 canonical 一致）
- 待清项：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-vortex-oam-hhg-20261101/05_review/params-conflicts.json（如有残留，一并核查）
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
- /Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-vortex-oam-hhg-20261101/06_panel/panel-findings.md（遗留核对表 + 新发现表）
- /Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-vortex-oam-hhg-20261101/06_panel/panel-verify-report.md（核销表 | 条目号 | 级别 | 已解决/部分/未解决/豁免 | 文本证据 | + 末行「复核结论: 通过/需返工」）

## 红线（skill 七节，强制）
- 引用三源对照零容忍（lit-gap-*.md / candidates-*.bib / reading-notes.md），
  池中无记录的条目一律不得写入；违反按 critical 计
- 口径表一致；跨章重复按「单一出处+指针」收敛；超长句仅拆句，
  禁改技术内容/数值/公式/引用编号
- 只改本课题 04_proposal/sections/ 下 5 文件 + 06_panel/ 产物

## 执行完成后的标准收尾

    python3 scripts/panel_review.py --adopt-engine general-vortex-oam-hhg-20261101

（解析核销表清账 → 锚集 pairwise 守卫 → optimizing 课题晋级 pending_review + 7 天否决窗口）
