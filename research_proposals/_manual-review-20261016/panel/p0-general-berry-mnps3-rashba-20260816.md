# 未解决 critical/high 清单 — general-berry-mnps3-rashba-20260816

来源：_lifecycle.json open_critical_issues（round_resolved=None 且未 stale）
共 11 条（critical 2 / high 9）

## 1. [high] rationale（首见 r8）

[high] anti_ai｜全章（程序检测）｜self_reference 14 次超阈扣 0.05；"本项目"仅 1 处，余为 26 处模块自指针贡献｜模块指针一次交代后改"上述框架/该判据"回指，压至 ≤10（anti_ai_patterns）

## 2. [high] rationale（首见 r8）

[high] refs_statement｜references.md L5 ↔ 三章实测｜声明"[11]/[25]/[38] 三章均挂靠"被证伪：[11][38] 无 scheme、[25] 无 content 挂靠｜按实测计数改写声明或在缺失章补挂（references 清单3）

## 3. [high] rationale（首见 r8）

[high] citation_overload｜全章 61 处角标/65 次引用｜超章标 35-47 上限 38%，R7 立案后仅 67→61，跨轮残留｜同源成果合并引用（如 [14,17,43] 一处集中），目标 ≤47 次（rationale 清单4/citation_style v6.9.9）

## 4. [critical] content（首见 r8）

1. [critical] citation_misattribution｜rationale §1.2 L33、§1.5"理论依据"段、Mavani 句（共 5 处）｜Ghorashi-Rappe 错挂 [15]、Ogawa 压磁错挂 [18]、Mavani 错挂 [24]，真身应为 [13]/[15]/[20]｜按 refs 表全链重排对表改正，改后正则提取全文 [N] 逐号复验（indica

## 5. [high] content（首见 r8）

2. [high] orphan_refs｜references L5 ↔ 三章实测｜"43 条一一对应、每条至少挂靠一处"被证伪：[20][39] 零挂靠；"[11]/[25]/[38] 三章均挂靠 9 处"实为各 3 处且各缺一章｜[20] 错挂回正后复算声明；[39] 补挂或删除重排；L5 按实测计数改写（rubric rigor ③）

## 6. [high] content（首见 r8）

3. [high] anti_ai｜§2.2 L13（154 字）/§2.3 L23/L27/§2.6 L65/L73｜>120 字超长句反弹至 5 句（R7 为 3 句；程序检测 severe 13>7 扣 0.12）｜按分号断点各拆两句，拆后程序复跑 severe ≤7（anti_ai_patterns.remove；skill 四.5）

## 7. [critical] scheme（首见 r8）

1. [critical] citation_misattribution｜rationale L15/L17/L35/L119（跨章残留）｜Ghorashi-Rappe=[15]（实为[13]）、Mavani=[24]（实为[20]）、Rani=[28]（实为[24]）、Ogawa压磁=[18]（实为[15]）｜按 references.md 条目号全量平移，修复后 grep [13][15][

## 8. [high] scheme（首见 r8）

2. [high] citation_dangling｜scheme §3.1 口径交叉引用表 L15-24｜≥4 行"立项依据章"指针无实体：rationale 全文 grep 无 d′、30–70%、≥5×、E_thr 任何实体；E_thr 行"§3.2 末尾、§3.4"两格在本章亦零命中（实体仅在 content）｜逐格 grep 实物后改写指针，或补齐目标章实体，删失真行。违反 rubri

## 9. [high] scheme（首见 r8）

3. [high] anti_ai｜§3.1 L5（140字）、§3.2 L32 SOC 段（220字）与 Hubbard U 段（169字）｜程序 severe 9>免赔 7 罚 0.04；content L29/L57 超长句亦仍存（历史遗留）｜按分号断点各拆两句，技术参数移方法学手册。违反 anti_ai_patterns"超长句"、expression 0.80-0.89 档位描述。

## 10. [high] scheme（首见 r8）

4. [high] feasibility_gap｜§3.4 L70｜探测场强压低绝对产额 10⁻⁶ 以上，光子计数/采集时间量级论证外包"见方法学手册"，就地无锚｜补一句量级估算（X 光子/发×Y 发积分→SNR≥Z），或引用同类低压驱动实验先例。违反 indicator_red_lines.implementation_path。

## 11. [high] scheme（首见 r8）

5. [high] orphan_refs｜references L5（跨章残留）｜"43 条每条至少挂靠一处、[11]/[25]/[38] 三章均挂靠"再被实测证伪：[20][39] 三章零挂靠，[11][38] 无 scheme、[25] 无 content 挂靠｜按实测计数改写声明，或为 [20][39] 补正文挂靠点。违反 section_standards.references"正文有[

