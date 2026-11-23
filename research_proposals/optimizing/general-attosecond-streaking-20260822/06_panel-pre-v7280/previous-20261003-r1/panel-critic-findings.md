# 评审团定点核查 findings——表达红线视角（critic）

课题：general-attosecond-streaking-20260822 ｜ 执行：engine亲审 ｜ 日期：2026-10-03
阈值按题面校准执行（勿过严）；程序化统计：rationale 9323 字 / content 7029 字 / scheme 15275 字 / full_review 2991 字；[N] 角标 36/23/30；长句（>120 字，按。？！切分）0/1/9/3；长段（>400 字）0/0/3/0。

## 问题清单

### CRI-1 [medium] scheme 7 处 >150 字分号复句
- 位置：scheme.md L9（软 X 平台句 187 字）、L41（选通/ Keller 句 155 字）、L43（通量句 165 字）、L49（氖气句 159 字）、L57（对照实验句 154 字）、L39（HHG 判据句 154 字，随 RES-2 一并改写）、L92 区（Cousin/Peschel 句见 CRI-2 说明）
- 问题：单句超 120 字红线；多数为"；"连接的两个独立话题陈述。
- 建议：在语义独立处"；→。"拆分为两句；保留 2 处不拆——L37 γ 估算句（121 字，公式为主体、拆分无收益）与 L100 双源互证句（129 字，Cousin/Peschel 并列为 full_review 衔接点设计），理由随报告记录。

### CRI-2 [medium] scheme 3 段超 400 字且可拆
- 位置：scheme.md §2.1 TDSE 建模段（530 字，L19）、§3.1 水窗 HHG 段（405 字，L39）、§3.1 靶材梯度段（404 字，L49）
- 问题：超长段（>400 字且可拆）。
- 建议：在「建模层级分两级」/「该方案在文献中已有完整先例」/「多通道靶材选用甲烷与氮气」三处自然话题边界分段，不动句内文字。

### CRI-3 [medium] "正式 Reply"表述复发（[38] 为预印本）
- 位置：rationale.md L37；content.md L13
- 原文：「Ardana-Lamas 等[38]的正式 Reply 逐条答辩」（两处）
- 问题：[38] 在 references.md 标 †（arXiv:2511.08391，无 journal_ref），凡例明示†＝未见正式发表版；scheme 侧同句已改「以预印本形式逐条 Reply」，rationale/content 两处复发。02_literature/reading-notes.md 亦载「正文使用时应明示其预印本属性」。
- 建议：两处改「Ardana-Lamas 等[38]以预印本形式 Reply 逐条答辩」。

### CRI-4 [low] "串行衔接"句跨章逐字重复且段内义重
- 位置：scheme.md L5 ↔ rationale.md L85
- 原文：scheme「三段研究内容在执行节点上呈串行衔接，前一阶段的输出作为后一阶段的输入。」＝ rationale L85 同句；且 scheme 段首已有「三段研究内容存在递进依赖」。
- 建议：删 scheme 处该句（保留 rationale 出处），段意无损。

### CRI-5 [low] Meier[23] 句同章逐字双现
- 位置：scheme.md §3.2 L59 ↔ §5 L122
- 原文：「Meier 等[23]的机器学习重构研究表明，16 通道 TOF 构型中个别探测通道失效与高噪声可由通道间冗余信息补偿，该先例支撑（这一/本）构型……」两处仅"这一/本"之差。
- 建议：§5（难点对策处）改短引「如 §3.2 所引 Meier 等[23]的机器学习重构研究……」，保留 §3.2 全句。

### CRI-6 [low] 检索库范围三处子集表述（与 REV-7 联动）
- 位置：content.md L39、scheme.md L154（子集）；rationale.md L71（国内检索含 CNKI/IOPscience）
- 问题：references.md 表尾 canonical 集合为「Web of Science、arXiv、IEEE Xplore、Scopus 与 CrossRef」；content 缺 CrossRef、scheme 缺 IEEE Xplore 与 CrossRef，属历史 high 问题的残余。
- 建议：content/scheme 两处对齐 canonical 五库；rationale L71 为"国内未见报道"专项检索（CNKI/IOPscience 为国内文献面），保留不改。

## 不立案项（附理由）
- R1/R2/R3、G1–G3、K1–K3 代号：属结构编号体系（题面纪律要求保持既有编号体系），且每处均有实义名并注（如「研究内容 R1：多通道电离耦合的 FROG-CRAB 修正算法」），非 AI 模板腔。历史轮"改实义名"建议与编号体系纪律冲突，不立案。
- 设计值/待实测标定注记密度（scheme"设计值"6 处等）：系 4 项设计值的诚实披露与降级路径收口（scheme §4.1 集中列出），删除将伤严谨性，不立案。
- [N] 角标合计 89 次（rationale 36/content 23/scheme 30）：项目校准标准为 rationale 35–47 嵌入区间（历史两轮清单均判达标），高于题面 10–20 提示线时按项目校准执行，不立案。
- 模板腔：「在此基础上」0、「本项目拟」0、「综上所述」0；「为…提供」6 处（三章）低于"为…提供…支撑">5 全文红线且均为"提供参照/入口"实义用法，不立案。口号式开头：三章均以实质陈述开篇，通过。
- full_review 3 处 >120 字句：骨架文档的分号列举句，随 REV-4/5 修改顺带理顺，不单独立案。
