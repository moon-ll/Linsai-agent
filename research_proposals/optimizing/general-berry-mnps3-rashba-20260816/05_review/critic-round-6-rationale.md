# 对抗评审报告（第 6 轮·聚焦立项依据）

元信息：general-berry-mnps3-rashba-20260816｜面上 general｜2026-09-25｜聚焦 §（一）立项依据（段落级）｜依据 nsfc-standards.json（section_standards.rationale + scoring_rubric + indicator_red_lines）、程序化 AI 检测（天花板 1.00，severe 长句 1/免赔 7 罚 0）｜模块完整性：§1.1–§1.5 五节齐备。R5 critical（12 处行内缺 [N]）已修复：rationale 角标 59 处/29 唯一编号，[31][43] 孤儿已入表，三章无幽灵编号。本轮新发现 refs 重编号后正文半迁移型错挂 4 处。

## 执行清单对照
清单1（五层递进）. 通过——§1.1 大背景→§1.2 三阶段脉络→§1.3 三瓶颈→§1.4 国内现状→§1.5 双平台定位，层层收窄
清单2（嵌入式引用非堆砌）. 不通过——嵌入格式已达标，但 L23/L67 Yarmohammadi 挂 [17]（表中 [17]=Basnet）、L7/L57 [18] 被赋予 arXiv:2609.04883 内容，具名与编号错挂（见问题 1/2）
清单3（末尾自然引出科学问题）. 通过——三问题由 §1.5 收束，无口号式开头
清单4（角标 35–47 次、文献 30–40 篇）. 通过——角标 59 处超旧口径 47 上限，按 v6.9.9 校准（范本实测 10–17）属密而不违；refs 41 条超 40 上限 1 条（表内自陈）
清单5（体量 5000–8000 字）. 通过——6385 字常规区间，冗余仅 L23 ↔ content 复述一处

## 锚点对比
申请书原文：Krempaský 等 [5] 用软 X 射线自旋分辨 ARPES 在 MnTe 体系中首次实验观测到交变磁性导致的 Kramers 自旋简并解除：节点面内 SOC 主导的弱交变劈裂量级约 100 meV，面外交换主导的强交变劈裂约 0.5 eV。
锚点原文：2011 年，Ghimire 等人 [9] 使用中红外激光驱动 ZnO 晶体，观测到了非微扰高次谐波产生现象。
差距：单句"机构+[N]+装置+动作+数值"形态已对标，两档量级并列+机制对照使数据密度反超范本。
申请书原文：Mizuno [42] 在弱 SOC 极限下建立自旋点群动力学选择规则，证明单旋圆极化驱动下自旋流谐波的 modulo-4 平移可唯一区分弱 SOC 交变磁体与磁性点群相似体系。
锚点原文：人们利用原子、分子气体高次谐波进行了大量气相原子分子的超快探测和控制研究[1-8]，包括原子价电子运动的阿秒操控、分子核运动的实时观测等。
差距：嵌入式单点论证已对标；但 [17]/[18] 编号错挂使引用嵌入的可信度受损，修复后即可全面对齐。
锚点对比结论：基本接近

## 写作风格评估
叙述骨架优良：三阶段→三瓶颈→双平台×双范式层层收束，数据驱动密度高（59 处角标、每瓶颈配实测锚点），关联词 0、模板句 1、meta 0、bullet 0。程序化检测：transition_words 1/33、template_phrases 1/8、redundant_modifiers 8/67、meta_discourse 0/2、excessive_bold 0.36/3、bullet 0、self_reference 9/10 全过；long_sentences severe 1（检索关键词句，豁免）免赔 7。残留：§1.2 P2/P3 段落 489/460 字超范本 150–300 字段长。程序化 AI 检测未发现超标模式，无需列 anti_ai 问题；天花板 1.00 不受强制限制。

## 问题清单
[critical] citation_mismatch｜rationale L23、L67；scheme L73｜Yarmohammadi 具名论述挂 [17]，但 refs 表 [17]=Basnet PRR 2022、[46]=Yarmohammadi，且凡例明示两文献分开挂靠｜三处 [17]→[46]，修复后 grep "Yarmohammadi 等 \[17\]" 全文清零（indicator_red_lines.consistency_check + references #3/#4）
  论证：content L51/L55 已正确挂 [46]，scheme L73 与 rationale L23/L67 仍挂 [17]——refs 重编号（新增 [46]）后仅 content 章同步、rationale/scheme 半迁移，属"只改点名章、他章残留"典型形态。读者按 [17] 检索得到 Basnet 化学配体取代论文，Floquet 框架出处完全张冠李戴，P0。
[critical] citation_mismatch｜rationale L7、L57｜[18]（JPSJ 2025 g-wave 压磁）被赋予"154 个 SPG 活动多极矩分类、i-wave 对应 7 个 PT 破缺 SPG 的 l=6 自旋电多极"内容——该内容实为 Ogawa-Hayami 2026 新作 arXiv:2609.04883｜新增该条目并改挂，或 L7 分类句改述为 [18] 压磁实际内容；两处口径统一（references #4 无张冠李戴）
  论证：经 arXiv 全文核对，[18] 所载 JPSJ 94:063704 为压磁效应论文；154 SPG/122 collinear SPG 完整分类出自 2609.04883（Dated Sep 7, 2026）。同一编号 [18] 在 L21 承担压磁判据、在 L7/L57 承担多极分类，一号两实，且 L57"共同为非共线反铁磁体中 i-wave 判定提供群论基准"混淆两文的适用对象，P0。
[high] evidence｜rationale L21｜Werner 等 [13]"SOC 引入后带间跃迁在五次以上谐波形成平台结构"——原文摘要及正文仅称"additional higher energy peaks and plateau structures"，无"五次以上"阶数表述（正文谐波以奇数次讨论）｜删去"五次以上"或改为"高能段形成附加峰与平台结构"（indicator_red_lines.no_exaggeration）
[high] citation_mismatch｜rationale L19｜"Basnet 等 [17,20] 在轻 Cr 取代的层状反铁磁体 NiPS₃ 中证实场致自旋极化"——该成果实为 Basnet PRB 109:184405 (2024)，[17] 为非磁配体 S/Se 取代（PRR 2022）、[20] 为综述，表中均无 Cr 取代条目｜补挂 PRB 2024 条目，或将该句改述为 [17][20] 实际承载的配体取代结论（references #4）
[medium] scope｜rationale L23 ↔ content L17/L75｜[25] u-Δ 参数化"交叉校验基准"表述三处复述（R5 已点名，半修复）｜rationale 保留一处，content 两处压缩为指针一句（content_boundaries 跨章协调）
[medium] narrative｜rationale L21、L23（§1.2 P2/P3）｜段落 489/460 字超范本 150–300 字段长，段内 80–120 字技术长句密集（每段超 2 句）｜按"诊断手段/相干声子"两主题各拆为两段（writing_style_rules.anti_ai_patterns 超长句条款）
[medium] standard_compliance｜rationale L7｜"同年发表的综述整理出自旋 Laue 群分类表"即 [3] 内容却未挂角标，与 refs 凡例"[3][10][20][34] 未在正文嵌入 [N] 引用"自相矛盾｜句末补 [3] 并同步更新凡例（references #3 正文角标对应）
[low] evidence｜rationale L43｜Basnet"现任职 Morgan State University"与 ORCID 记录（2026 年 3 月 Argonne 产出）不符，隶属信息过时｜按 ORCID 现值更新或删去任职细节（no_exaggeration）

## 对抗结论
本轮 8 问题（critical 2/high 2/medium 3/low 1）。相比 R5：改善 4（行内缺 [N] 12 处清零、三问题量化指标补齐、长句 113/115 字句重写、两档量级表述修复），残留 1（[25] 划界复述半修复），新增 4（[17]→[46] 错挂、[18] 一号两实、Werner 阶数虚构、Basnet Cr 取代错挂——同根因：refs 重编号后正文内容-编号漂移）。综合 0.78＜0.85，critical 2 项＞0，未达输出标准。P1：问题 1/2；P2：问题 3/4/6。修复指令：三处 [17]→[46] 后必须 grep 全文验证，[18] 内容错挂两处须同时改，勿只改点名段。

## 评分
创新性：0.85
可行性：0.80
严谨性：0.65
表达质量：0.76
综合评分：0.78
