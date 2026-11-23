# 对抗评审报告（第 6 轮·整体一致性审查）

课题：general-moire-strong-field-probe（面上 general）｜日期：2026-09-24｜方法：三章+full_review 全文实读、R6 三分章轮问题逐字 grep 验收、口径表逐字段比对、[27] 归属反查文献表。

## 执行清单对照

清单1（三章标准模块）. 通过
清单2（rationale 五层递进）. 通过
清单3（rationale 嵌入式引用）. 通过
清单4（末尾自然引出科学问题）. 通过
清单5（rationale 引用 35-47 次）. 不通过——实测 52 次编号引用超上限（问题 7）
清单6（rationale 体量 5000-8000）. 通过——5514 字
清单7（content 总述+分方向+目标+关键问题）. 通过——2.2.1-2.2.3 已补编号
清单8（每条目标含量化指标）. 通过
清单9（content 不出现方案细节）. 通过——假设 3 标度式以可证伪阈值为限
清单10（content 分方向递进）. 通过
清单11（content 体量 4000-7000）. 不通过——8472 字超限且程序 3 对双份未处置（问题 3）
清单12（scheme 总体+分方案+可行性）. 通过
清单13（每个技术选择有理由）. 通过
清单14（可行性"方案→原理→结论"）. 通过
清单15（难点有解决方案）. 通过
清单16（scheme 无越界口吻）. 通过
清单17（scheme 体量 6000-10000）. 通过——7642 字
清单18（full_review 骨架≤3000 字）. 通过——实测 1523 中文字，仅含主线链+衔接点+口径表+术语表；程序"8KB 超限"系 bytes 误判字数（R5 同型裁定），过程记录零残留
清单19（跨章指标口径一致）. 不通过——量级差三章三口径（问题 2）+ No-Go 不等号（问题 6）
清单20（术语统一）. 不通过——激元/激子分裂、"密度密度"损坏（问题 5）
清单21（冗余处置令执行）. 不通过——程序 3 对点名句均残留（问题 3）

指标预检裁定：6 项数值集差异经逐项核对，nm（12.8 锚点 vs 10 光斑）、μm（4.5 波段端点 vs 1.3-3 波段内值 vs 3 锚定）、K（260 tdDMFT vs 30 激子温窗）、eV/meV/百分比多数属口径差异不立案；唯百分比族中 75–360/88–352/75–300 系同指标三口径（问题 2）。相关性复核 3 段（content 第16段三路径、scheme 第1/10段）均属核心论证链（方案定位句与 MPS 柱状映射论证），保留。

## 锚点对比

对一（rationale·引用嵌入）
申请书（§1.2 L25）：Lian 等 2024 年在 *Nat. Phys.* 上实验证明 WS₂/WSe₂ 莫尔超晶格中存在谷极化激元型莫特绝缘态（ν = 1）[19]。
锚点：2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生。
差距：作者+年份+期刊+对象+观测量五要素嵌入与范本同构、密度更高；短板在同段与 content/scheme 对同一对象术语分裂（激元 vs 激子，问题 5），范本对同一对象全篇一词到底。

对二（content·总述段主语）
申请书（§2.2 L29）：围绕上述总体目标，三项研究内容构成"R1 理论建模 → R2 谱学探针 → R3 主动调控"的递进闭环。
锚点：本项目拟采用理论与实验相结合的研究方法，建立包含局域电子态效应的量子轨迹模型，揭示局域电子态对高次谐波产生过程的影响机理。
差距：递进逻辑与量化密度达标；差距在主语与自指——范本以"本项目拟…建立…揭示…"一句定位，申请书以 R1/R2/R3 令牌自指展开且全章"本项目"仅 1 次，评审阅读时回声感来自令牌而非内容主语。

锚点对比结论：基本接近

## 写作风格评估

单段语体达标：嵌入式引用、数据密度、段间物理链条衔接不低于范本，无 bullet、无模板句。系统性缺陷收敛中但未清零：跨章双份（创新点 2/3、Lian 句、指标链数值）与令牌式自指（content 令牌自引约 118 处、跨章 §指针 70 处）构成回声主体。
程序化 AI 检测：self_reference 33 次（阈 10/15）扣 0.10；超长句 17 处（免赔 7）扣 0.20；transition_words 2/37✓、template_phrases 0✓、template_subject 0✓、redundant_modifiers 22/74✓、meta_discourse 0✓、excessive_bold✓、bullet_list✓。程序化检测发现AI写作模式，表达质量被强制限制于天花板 0.70。

## 问题清单

1. [critical] citation｜rationale §1.3 段2 末（L33）｜[27] 一号两挂：rat 作"Ortmann 与 Landsman 等综述 [27]"，scheme L127 与文献表 [27] 均为 Kumar 2026 四极激子，文献表无 Ortmann 条目｜删该句或改挂真实综述并补文献表；grep "[27]" 全量验收
论证：R6-rationale 曾令"[27] 并入 §1.3 或删"（指 Kumar 四极激子），writer 执行为在 §1.3 新增阿秒条纹综述句并挂 [27]——同一编号两章指向两个不同文献，且"Ortmann 与 Landsman"在 30 篇文献表中零命中，论述无出典。属修复令催生的虚构归属，违 section_standards"无张冠李戴"与 indicator_red_lines，同 refs 判例"真文挂假作者=critical"。

2. [critical] red_line｜rationale L59/L73 vs content L159 vs scheme L99/L127｜量级差同指标三章三口径：rat 75–360、con/sch 88–352（主锚）+75–300（旁证）；full_review 口径表 L68 仍声明"75–360 倍"三章统一，与实态脱节｜四章统一"88–352 倍（1.76 eV 主锚），旁证 75–300"，rationale 两处改值、口径表 L68 同步（action: recalculate）
论证：75–360 端点混搭（75 系 1.5 eV 旁证端、360 系 1.8 eV 主锚端），R6-content/scheme 两轮已点名，writer 只改 content/scheme 未动 rationale，修复半迁移致口径表与两章新值脱节，违 indicator_red_lines.consistency_check（P0）。

3. [high] redundancy｜content L77/L147/L151 vs scheme L99/L123/L125｜程序处置令 3 对（创新点 2/3 标题句、Lian [19] 句）content/scheme 双份完整复现，连续两轮未执行｜scheme 侧创新点标题句改一句指针，Lian 句只留 Δ_CI 锚点功能删存在性复述（action: remove）

4. [high] anti_ai｜三章（程序检测）｜self_reference 33 超阈扣 0.10、超长句 17 处扣 0.20；载体为令牌自指与 §指针｜代号句首改内容主语、超长句按分号边界拆分，压至 ≤15/免赔额（action: rewrite）

5. [high] terminology｜rationale L25 vs content L21/L77/L109、scheme L99｜同指 Lian [19] 态"谷极化激元型"（rat 孤例）vs"谷极化激子型"（5 处）分裂；scheme L21"含时密度密度泛函"字符损坏残留｜rat 改"激子型"全篇统一；"密度密度"删一（action: rewrite）

6. [medium] red_line｜rationale L55 vs content L107｜同一 No-Go 两种边界表述："SNR ≥ 30 时误差仍超过 30%"vs"SNR=30 时误差 ≥ 30%"（R6-content 点名未修）｜统一为"SNR=30 时反演误差 ≥ 30% 触发"（action: rewrite）

7. [medium] format｜rationale 全章｜编号引用 52 次超 section_standards 上限 47｜[6][8] 等低信息重复编号合并为句内复合引用（action: remove）

8. [medium] redundancy｜scheme L113｜指针句复述指标链数值"30%→18%→12%"违"指代不复述"｜删数值只留"指标链见研究内容章 R2 段"（action: remove）

## 评分
创新性：0.86
可行性：0.80
严谨性：0.65
表达质量：0.68
综合评分：0.77
