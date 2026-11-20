# 对抗评审报告（第 5 轮·聚焦立项依据）

元信息：general-berry-mnps3-rashba-20260816｜面上 general｜2026-09-25｜聚焦 §（一）立项依据（段落级）｜依据 nsfc-standards.json（section_standards.rationale + scoring_rubric + anti_ai_patterns）、程序化 AI 检测（天花板 1.00，超长句 severe 1/免赔 6 罚 0）｜模块完整性：rationale 五节（§1.1–§1.5）齐备，研究意义含于 §1.1/§1.5，无缺模块。跨章一致性抽检通过：16.4/39.9/25.5 meV 势垒、0.1–1.0 MV/cm、τ₁≈1–9 ps / τ₂≈1–4 ns、五指纹量、cos6θ/cos2θ/cos4θ 在 rationale/content/scheme 三章数值与口径一致。

## 执行清单对照
清单1（五层递进）. 通过——§1.1 大背景→§1.2 领域脉络（三阶段）→§1.3 核心挑战（三瓶颈）→§1.4 国内现状→§1.5 定位，层层收窄
清单2（嵌入式引用非堆砌）. 不通过——R4 点名 10 处行内无[N]，R5 仅 1 处（Ogawa-Hayami）补[N]，剩 12 处复发（Misawa/Luu-Wörner 表内无条目；Werner/Yang-Liang/Ezawa×2/Rani-Juraschek/Mizuno/Ghorashi-Rappe/Mavani/Basnet/González/Gabriele 表内有条目却弃用）
清单3（末尾自然引出科学问题）. 通过——三问题由 §1.5 收束，无"为回答…"口号
清单4（正文 35–47 次角标、文献 30–40 篇）. 通过——rationale 总角标 41 处（19 个唯一编号），refs 表 38 条（编号 3–15、17–20、22–30、32–42、45 连续，缺号合规），[N] 网络对位无错位
清单5（体量 5000–8000 字）. 通过——字数未偏离（参 6281 字）

## 锚点对比
申请书原文：Krempaský 等 [5] 用软 X 射线自旋分辨 ARPES 在 MnTe 体系中首次实验观测到交变磁性导致的 Kramers 自旋简并解除：节点面内 SOC 主导的弱交变劈裂量级约 100 meV，面外交换主导的强交变劈裂约 0.5 eV。
锚点原文：2011 年，Ghimire 等人 [9] 使用中红外激光驱动 ZnO 晶体，观测到了非微扰高次谐波产生现象。
差距：单句"机构+[N]+装置+动作+数值"形态已对标，数据密度反超范本（两档量级并列+对照机制）；§1.2 P2 该句达标，拖累整体仍是同段 Misawa/González/Werner 等处仍以"作者+动词"枚举节奏。

申请书原文：Mizuno [42] 在弱 SOC 极限下建立自旋点群动力学选择规则，证明单旋圆极化驱动下自旋流谐波的 modulo-4 平移可唯一区分弱 SOC 交变磁体与磁性点群相似体系。
锚点原文：人们利用原子、分子气体高次谐波进行了大量气相原子分子的超快探测和控制研究[1-8]，包括原子价电子运动的阿秒操控、分子核运动的实时观测等。
差距：申请书 L35（91 字）单点嵌入式论证已对标"某人+[N]+对象+结果"格式；但同段 §1.3 P3 自"Werner→Yang-Liang→Ezawa→Ogawa-Hayami→Luu-Wörner"四连发仍缺[N]，对照范本"气体高次谐波…"段[1-8]聚合引用规范，本申请书行内[N]密度不均拖累锚定感。
锚点对比结论：基本接近

## 写作风格评估
叙述骨架优良：§1.3 三瓶颈、§1.5 双平台×双范式与三个科学问题层层收束，§1.5 末尾"两项空白并存"反向引出问题链，与 [25][9] 逐项划界+可行性边界由 [32][29] 双证据衔接形成论证闭环。程序化检测：关联词 0/32、模板句 1/8、冗余修饰 5/64 均过；meta 0/2、bullet 0、自指 5 合规；超长句 severe 1/免赔 6（仅 L47 = 129 字一处），相比 R4 的 10 处 severe 大幅改善；加粗 12 处合规。天花板 1.00 生效，但 anchor 结论"基本接近"封顶 0.79。残留：R4 critical #1（行内无[N]）12 处复活，扣可读性。

## 问题清单
[critical] citation_device｜§1.1 P4/P5、§1.2 P2/P3、§1.3 P3、§1.4 P5｜R4 点名 10 处行内无[N]，R5 仅 Ogawa-Hayami 一处补[N=18]，剩 12 处复活：Werner→[13]、Yang-Liang→[12]、Ezawa×2→[14][19]、Rani-Juraschek→[28]、Misawa(arXiv:2609.01969)→表内无条目、Mizuno→[42]、Ghorashi-Rappe→[15]、Mavani→[24]、Basnet→[17][20]、González→[23]、Gabriele→[26]、Luu-Wörner→表内无条目｜行内句补[N]（含 2 条须新建条目），arXiv:2609.01969 与 Luu-Wörner 两条新建 entries 入表（section_standards.rationale #2 + references #3）
  论证：rationale 角标 19 个唯一编号，refs 表 38 条，但 19 条 references 编号在 rationale 中完全无[N] 角标（孤儿），且 12 处行内出现具名论述而无[N] 编号。Luu-Wörner 在 references 中无对应条目（critical 真孤儿），Misawa arXiv:2609.01969 同例。两形态叠加属 P0"已有才标 N、孤行不挂 N"重复违反，R4 已点名"行内句补既有编号"，R5 仅补 1 处，复发 12 处升级为 critical 新形态。
[high] anti_ai｜§1.2 P2（P=line）｜L29 (113字)、L23 (101字)、L37 (115字) 三处 100+ 字技术长句同段密集，超 80 字句同章 32 处（多在 §1.2 三阶段段内连续出现，每段超过 2 句）｜按"对象+装置+结果"三段拆分长句，每段超 80 字句保留 ≤2 句，余改短（writing_style_rules.anti_ai_patterns 超长句条款）
[high] narrative｜§1.2 P3、§1.3 P3｜§1.2 P3 自 Werner→Yang-Liang→Ezawa→Ogawa-Hayami→Luu-Wörner 五家论述全无[N]且段内缺"对本项目意义"回收句；§1.3 P3 Werner 句与"Y-L/Ezawa 椭圆二色性"句对照，段末未收束至本项目读出端判据链｜每段编号引用 ≤3，段末补一句回收至本项目指纹表或读出端瓶颈（forbidden #1）
[medium] standard_compliance｜§1.4 P5｜"Mavani 等基于自旋空间群"等行内无[N] 已与 [24] 失锚，但 Mavani 文献归属仅"国际合作组完成"未具名——核实首作/通讯机构后补挂｜行内补 [24] + 在 §1.4 备注 Mavani 第一作者机构（no_exaggeration）
[medium] evidence｜§1.5 Q2｜三个科学问题之"问题"指代含混：①"切换阈值"以"16–40 meV / 0.1–1.0 MV/cm"为势垒与场强窗口非切换阈值本身；② i-wave 指纹"具体数值关系"未给目标阈值/区间；③ 双时标 τ₁/τ₂ 已锚定但 Floquet 增强条件未给判定指标｜Q2 补目标阈值（例如"螺旋度交替幅度 ΔI≥0.3""椭圆度斜率 ≥0.1/THz"），Q1 切换阈值明写"R1 TDDFT 预言区间待定+承诺落点"（indicator_measurable + implementation_path）
[medium] scope｜§1.5 P3｜"与既有最近邻工作的边界划定如下"段重复了 [25] 与 [9] 的逐项划界——该内容与 scheme §3.2 中"Wang [29] 势垒跨越中点"段功能重叠｜rationale 仅保留一段边界划定总览，具体先例/数值移至 scheme §3.2（content_boundaries 跨章协调）
[low] expression｜§1.2 P2｜"节点面内 SOC 主导的弱交变劈裂量级约 100 meV，面外交换主导的强交变劈裂约 0.5 eV"——"量级约 100 meV"与"约 0.5 eV"两档量级差被弱化读作连续量｜改"约 100 meV 与约 0.5 eV 两档"显式分档（data_driven）

## 对抗结论
本轮 8 问题（critical 1/high 2/medium 3/low 1）。相比 R4：改善 5（[29] 归属修复、严重长句 10→1、五指纹量跨章一致、势垒-场强-时标跨章一致、§1.4 国内主线已修复），残留 1（R4 critical #1 仅 1/13 修复），新增 0。R4 critical #1 升级：12 处行内无[N] + 2 条表内真孤儿（Misawa arXiv:2609.01969、Luu-Wörner）属 critical 新形态，触发 P0 红线（indicator_red_lines.novelty_claim_cautious 间接 + consistency_check 双形态），严谨性扣入 0.6-0.7 区间下限。综合 0.75＜0.85，high 2 项＞0，未达输出标准。P1：问题 1（critical）、问题 2–3（high）。

## 评分
创新性：0.85
可行性：0.80
严谨性：0.55
表达质量：0.74
综合评分：0.75