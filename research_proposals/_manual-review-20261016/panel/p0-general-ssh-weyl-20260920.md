# 未解决 critical/high 清单 — general-ssh-weyl-20260920

来源：_lifecycle.json open_critical_issues（round_resolved=None 且未 stale）
共 19 条（critical 5 / high 14）

## 1. [critical] rationale（首见 r7）

1. [critical] citation_error｜§2.2 L27、§1 L5、§2.1 L19、§2.4 L55/L61/L63｜末组文献编号整组错位一格：[36][37]应[35][36]、L19/L55[38]应[37]、L61[40]应[39]、L63[39]应[38]、L5[31-35]应[31-34]｜以 refs 条目作者逐条对表改正，改正后全文重查 [N]

## 2. [high] rationale（首见 r7）

2. [high] evidence_status｜references.md 头注｜头注自证矛盾：称"[31]–[35] 五条气相奠基文献"但 [35] 实为 SSH 论文；[4] 已见刊（Nat. Commun. 2018 带 DOI）却列入预印本 10 条清单｜头注按条目实物重写，两处计数句逐条复核

## 3. [high] rationale（首见 r7）

3. [high] anti_ai｜全章（程序检测）｜超长句 9 处超免赔 7、罚 0.04；实测 L43 首句 129 字｜按分号语义边界拆为两句，L79 对照基线长句同步拆分（违 anti_ai_patterns.remove"超长句"）

## 4. [high] rationale（首见 r7）

4. [high] pointer_dangling｜L79"（详见 §2.4）"｜§2.4 全节无 ZnO/Jessen/[30]/[21] 任何论述，指针落空｜将 Jessen[30] 基线段前移入 §2.4，或改指"见本节上文"

## 5. [critical] content（首见 r7）

1. [critical] citation_error｜content L17/L49（另 rationale 4 处、scheme 4 处）｜[20]写"增强上限两个数量级（≤100倍）"，原文为"exceeding two orders of magnitude"（>100倍）及"two to three orders"，方向相反｜全文 grep"上限两个数量级｜≤100 倍"改"两至三个数

## 6. [critical] content（首见 r7）

2. [critical] indicator_mismatch（R6 残留）｜scheme §3.4.2 L173 ↔ scheme 2.2 L59/content L49｜ΔI_gap 线性版"提取…强度比，求二者之差"残留，与对数定义 ΔI_gap=log10(I_topo/I_ZnO) 互斥｜L173 整句替换为"求二者以 10 为底对数之差"（action: rewrite；违 indi

## 7. [high] content（首见 r7）

3. [high] evidence_status｜references 头注 ↔ content L15/L25/L35｜头注称"预印本结论在正文各引用处均已标明"，content 中 [12][13][15][17][18] 引用点 120 字窗内均无"预印本"标注（仅 [20][8] 有）｜五处补"（预印本）"限定（action: add；头注声明被实物证伪）

## 8. [high] content（首见 r7）

4. [high] redundancy（R6 残留，3 现改 4 现）｜方向节指标段+终止判据段 ↔ §2.6 G1-G4 ↔ §2.7 K1-K4｜十二指标数值在章内 4 现，G/K 段已有"度量定义见方向N"指针仍复述全部数值；终止判据段（L31/41/51）逐字重列刚给过的三指标｜G/K 段只留指标名删数值，终止判据段改"三项指标一并达成（见上段）"（action: remove）

## 9. [high] content（首见 r7）

5. [high] anti_ai（程序检测）｜全章超长句 9 处超免赔 7，罚 0.04；content 内实测 §2.1 首句 128 字、§2.4 首句 137 字、L39 闭合条件句 132 字｜按分号/破折号语义边界各拆为两句（action: rewrite；违 anti_ai_patterns.remove"超长句"）

## 10. [critical] scheme（首见 r6）

1. [critical] indicator_mismatch｜§2.2 L59、§3.4.2 L173 ↔ content L49/L63｜ΔI_gap 定义两章两版：scheme 线性"强度比差值"，content"对数比差值"｜统一为对数比口径，L59/L173 同步改写｜违 indicator_red_lines.consistency_check

## 11. [critical] scheme（首见 r6）

2. [critical] logic_error｜§2.2 L49 ↔ §5.2 L227｜Δt 换算链两版互斥：L49"参照阈值 30 fs…取三分之一"，L227"25 fs 驱动窗按三分之一取 10 fs"（25/3≈8.3≠10）｜统一为 30 fs 参照×1/3≈10 fs，L227 改"参照 Bera 驱动窗口尺度约束拟合时窗"｜违 programmatic 数值复算纪律

## 12. [high] scheme（首见 r6）

3. [high] evidence_mismatch｜§1 L11 ↔ references L19｜"三类已发表实验数据"首类挂 [8]（arXiv:2604.06051，refs 明标预印本）｜"已发表"改"已公开"，或改挂已刊 Bi₂Se₃ 基准（如 [5]）｜违 skill§八"已刊称预印本"反向禁则

## 13. [high] scheme（首见 r6）

4. [high] evidence_status｜L11/L49/L59/L83/L99/L167/L199/L219/L225 共 9 行｜[7][8][12][13][15][18][20] 预印本在方案章引用处零属性标注，refs L3"正文各引用处均已标明该属性"声明被 grep 证伪（rationale 已修，方案章未跟修）｜sch 首次引用处逐一加"（预印本）"｜违 indicato

## 14. [high] scheme（首见 r6）

5. [high] mechanism_identifiability｜§3.2.1 L101｜"开关 A 差分谱形作为 Y 的独立指纹"——开关 A 只控节点色散、不触曲率，所得差分为 X 指纹，主语与指纹对象错位；"曲率开关差分谱"句无开关 B 语境｜该句主语改 X，另补"开关 B 关闭前后差分为 Y 指纹"一句｜违 physics-domain #2

## 15. [high] scheme（首见 r6）

6. [high] anti_ai｜全章程序检测｜自引用 12 次超阈 10（R4→R5→R6：16→21→12），罚 0.05，连续三轮未清｜非主张句删"方向X"主语直陈对象与事实｜违 anti_ai_patterns.self_reference

## 16. [high] full_review（首见 r6）

1. [high] indicator_mismatch｜rat §4 L87 ↔ sch §2.2 L59｜ΔI_gap 残留线性版"强度比≥阈值R"，方案为对数比，两读差百倍｜rat 补"对数比"：改"强度比的对数 ΔI_gap ≥ R"

## 17. [high] full_review（首见 r6）

2. [high] logic_error｜rat §3 L79｜ZnO 激子切换基准称"下文国内研究现状一节详述"，指针悬空且方位颠倒｜改指研究内容方向四，或在 §2.4 补 Jessen[30] 一句

## 18. [high] full_review（首见 r6）

3. [high] anti_ai｜全文（程序检测）｜超长句 severe 13 处超免赔 7、罚 0.12，较 R5 的 8 处反弹｜优先拆 sch L11/L59/L125、con L39/L49、rat L19/L87

## 19. [high] references（首见 r6）

[high]｜refs L3、L89｜称"全数映射无未引用条目"，但 [31]-[35] 仅以区间 token 引用，与预检单引口径（5 条未引用）冲突｜统一口径：L89 改"36 个单引编号＋[31-35] 区间引用"，或拆为 5 个独立 [N]

