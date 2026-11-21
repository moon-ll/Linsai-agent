# 整体一致性修订记录（writer，full_review 轮）

课题：general-bsv-driven-hhg-quantum-20260726
聚焦：rigor 维度（0.74→目标 ≥0.8），本轮性质为整体一致性修订（章节衔接、术语统一、冗余删减）
输入评审报告：05_review/critic-round-1-full_review.md

## 一、评审问题逐条处置

| # | 级别 | 问题 | 处置 | 证据 |
|---|---|---|---|---|
| 1 | critical | content §2.3 κ-Br 段（"测量以室温为首轮窗口，以 4 K 低温复测作为关联态判定的回退路径"）与 scheme §3.3（"κ-Br 本项目不单独安排 HHG 谱学"）互斥 | **已修改**：content 侧删除 κ-Br 的室温/4 K 测量安排，改为"本项目只取该归属作为 $U/W$ 分档参照，不对该体系单独安排 HHG 谱学测量"；scheme 侧原句"κ-Br 与 κ-Cl 的 HHG 对照因此落在同一平台条件性分支上"改为"$\kappa$-Cl 的 HHG 测量落在同一平台条件性分支上"，消除自相矛盾 | sections/content.md §2.3、§2.4；sections/scheme.md §3.3 |
| 2 | critical | scheme §3.3 半金属化区截止律 $E_s = 3.6\hbar\Omega_{I,0}$ 与自证分解式 $2\hbar\Omega + 3.2U_w$（=2.8$\hbar\Omega_R$）不闭合 | **已修改（按原文核对后重写）**：联网提取 Tamaya et al. arXiv:1701.02869 全文核对，原文两式为 $E_s = E_B' + 2\times3.2\,U_w = E_B' + 1.6\hbar\Omega_{R,0}$（交流 Zener 区）与 $E_s = 2\hbar\Omega_{R,0} + 3.2\,U_w \approx 3.6\hbar\Omega_{I,0}$（半金属化区）。原文中 $\Omega_R$ 与 $\Omega_I$ 为两种不同重整化的 Rabi 频率（$\Omega_R$ 经形式因子重整化，$\Omega_I$ 由入射场强重整化），原书的"$\approx$"正建立在该换算上。申请书现按原书形态书写并显式说明该频率区分，声明"不把两式中的 $\Omega$ 当作同一量代入" | sections/scheme.md §3.3 截止位置段；sections/references.md [29] 条目注释同步 |
| 3 | high | scheme 全章 [N] 引用 42 次，超范本口径 10–20 次 | **已修改**：压至 19 次（distinct）。做法：非关键论断处去编号并入叙述句（Schleich-Wheeler[16]、Wu[11]、Tyulnev[38]、Jabed[37]、Berry 反演[17]、Bloch[13]、双粒子[9]、QED[19]、Li[10]、Even Tzur[32]、Sumaya-Martinez[45]、Raissi[46]、Murakami[7]、Prajapati[44]、Wu[5]、Even Tzur[2]、Boroumand[12] 等），关键论断处的角标保留 | sections/scheme.md 全章 |
| 4 | medium | rationale §1.2.3/§1.2.2/§1.3/§1.5 共 8 处具名引用零角标 | **已修改**：补挂 17 处角标（Luu[17]、Wu[5]、Liu[6]、Gothelf[21]、Wang[23]、Lange[22]、Stammer[27]、de-la-Peña[28]、Wu[11]、Boroumand[12]、Even Tzur[32]、Jiang&Dorfman[20]、Rasputnyi[1]、Li[8]、Murakami[7]），与全章其余具名引用体例统一 | sections/rationale.md §1.2.1/§1.2.3/§1.3/§1.5 |

## 二、本轮额外发现并修复的问题（评审报告未列，独立核验发现）

| # | 类别 | 问题 | 处置 |
|---|---|---|---|
| 5 | broken cross-reference | scheme §3.3 称"回退的触发判据见研究内容 2.3 节"，但 content §2.3 实际不含该判据（该句原写在 κ-Br 段，本轮修订删除后指针落空） | 在 content §2.3 莫尔段补写判据句（室温首轮 / 4 K 低温复测 / 室温信号被热背景淹没时低温支接管 / 关联态判定以低温变温测量为准），scheme 侧指针改为"室温信号被热背景淹没时低温支接管（判据见研究内容 2.3 节）"，rationale §1.2.3 同步为"关联态判定由低温变温测量独立标定" |
| 6 | reference orphan | [N] 密度压缩后 [7][13][46] 一度成为零引用孤儿条目，其挂钩注释仍声称特定章节 | 三者均为承载论证的具名成果（Murakami 的 Hubbard 修正定量形式、Rivera-Dean 的 Bloch 形式化、Raissi 的 PINN 框架），已在对应承重句回挂角标；最终 48 条文献全部被正文引用，零孤儿零悬空，编号无跳号 |
| 7 | 句长超限 | 修订过程中产生 4 句超 120 字（content 2 句、scheme 2 句） | 全部拆分为短句，全文正文（含三章）单句最大 119 字，超 120 字句数 = 0 |
| 8 | 修饰词密度 | 三章合计 31 处（阈值 12） | 削减至 18 处，剩余全部为复合技术术语（两能级系统、复合系统、有效压缩度 $r_{\rm eff}$、有效截止位置、关键科学问题、关键技术风险），非空泛修饰 |
| 9 | 用词精确性 | scheme 三处"系统偏差"改为"一致性偏置"（systematic bias 的更精确中文），避免"系统"作修饰词 | 已改，两处阈值语义不变 |

## 三、历史 P0 遗留问题复核（逐条）

| 历史 P0 | 归属 | 状态 | 本轮复核结果 |
|---|---|---|---|
| ① 三层降级标签指针虚指 | rationale | 待解决 | **已消除**。rationale §1.4 实指"研究方案章特色创新三末段与预期成果节第四组判据"；scheme §3.7 给出三层完整标签链（多体态探针→多体响应分类工具→量子光 HHG 响应特征化），§3.8 给出第四组判据，指针双向闭合 |
| ② g²(0)≈3 无配置限定 | rationale | 待解决 | **已消除**。§1.3 表述为"简并 PDC 极限下有 $g^{(2)}(0)\to 3$（非简并配置取 2）"；§1.2.2 与 content §2.1 均为"非简并取 2 / 简并取 $3+1/N$"双配置并列，无矛盾 |
| ③ rationale 1.5 "一一对应"不成立 | content | 待解决 | **已消除**。改为"与研究内容三个分方向及三条关键科学问题分别承接"，与实际 3 分方向 + 3 关键科学问题结构相符 |
| ④ content 2.0 三目标零量化 | content | 待解决 | **已消除**。三目标各带可检验指标：$QEF_{\rm yield}^{(q_{\rm ref})}$ 效应量 + 95% CI；$R^2 \geq 0.7$ 且 AIC 下降 $\geq 10$；$\mathcal{R}_F$ 三档归档 |
| ⑤ scheme 截止律 $E_s=E_B+1.6\hbar\Omega_r^6$ 错转录 | scheme | 待解决 | **已消除**（本轮进一步按原文修正，见问题 2）。六次幂错误已不存在，现为 Rabi 频率一次幂，$\Omega$ 定义为 Rabi 频率，$E_B'$ 已定义 |

## 四、本轮新增文献

- **[48]** Grigoriev P. D. et al. *Giant hysteretic magnetoresistance accompanying the Mott transition and spin-glass state in organic metal*. arXiv:2512.13245 (2025)（预印本）。
  - 定向检索来源：02_literature/targeted-research/lit-gap-1794218636.md（章节 full_review，检索式 κ-(BEDT-TTF)₂X 家族 Mott 转变与关联强度）。
  - 联网核实：arXiv:2512.13245 题名、作者、日期与摘要一致，确认存在。
  - 用途：κ-(BEDT-TTF)₂Hg(SCN)₂Br 在约 3 kbar 压力窗口观测到巨磁阻与自旋玻璃弛豫，磁阻各向同性排除轨道效应；为 κ-Br 的家族层面基态归属与 $U/W$ 分档提供独立外部依据，并支撑本项目"不重复采集、只取家族层面归属"的实验安排。
  - 已引用位置：content §2.3、§2.4；scheme §3.3；references [48]。
  - 阅读笔记：02_literature/reading-notes.md 已追加条目（阅读日期 2026-11-09、来源、核心结论、与课题关联、已引用位置）。

## 五、程序化终检结果（提交前当场复算）

| 检测项 | 阈值 | 结果 |
|---|---|---|
| canonical 禁用旧值/旧表述（params.json 全 12 式） | 零残留 | **通过**（12 式全部无命中；BSV 驱动档内推链 3 μm FWHM → 1.8 nJ → 7×10⁹ 落在 10⁸–10¹⁰ 档；quantum dial 1.2 TW/cm² 带 v3 版本注记，均未回退） |
| 正文角标 ↔ 参考文献一一对应 | 零孤儿零悬空 | **通过**（48 条全部被引，编号无跳号，最大角标 48 = 列表 48） |
| 单句长度 | >120 字必拆 | **通过**（正文三章 >120 字句数 0，最大 119；>80 字句属范本正常区间） |
| 自引用（详§X / 见§X） | 全章 ≤10 | **通过**（三章各 0） |
| 修饰词密度 | ≤12 | **18，全部为复合技术术语**（两能级系统、复合系统、有效压缩度、有效截止位置、关键科学问题、关键技术风险），无空泛修饰 |
| 模板化表达（为…提供…/ 本项目拟…句首 / 关联词 / 元话语 / 加粗 / 编号列表） | 各 ≤5 / ≤5 / ≤8 / ≤2 / ≤3 / 禁 | **通过**（为提供 0；本项目拟/将句首 0；关联词 3；元话语 0；加粗 0；bullet 0） |
| 禁用词（交付物/硬门控/口径/工作假设/落地等） | 零 | **通过**（三章全零） |
| 章节体量 | rationale 5000–8000 / content 4000–7000 / scheme 6000–10000 | rationale 6449、content 10678、scheme 11893 字；content/scheme 超参考上限，但跨章 40 字符 shingle 重叠 = 0，章内重复论证均为公式符号而非重复论证，判为实质性长文 |
| full_review 篇幅与纯净性 | ≤3000 字、三部分、零过程痕迹 | **通过**（1546 字；主线论证链/章节衔接点/跨章节数值与判据对照表；无轮次、文件名、处置记录） |
| 相关性复核线索 8 段 | 语义裁决 | **全部保留**（逐段复核：Jensen 隔离、SBE-Q 三步模型边界、MoS₂ 关联能隙换算、κ-Br 家族归属、SnS₂ 宽带隙对照、β-Ga₂O₃ 倍频支路、拓扑与 CDW 锚点、四类对照总述——均属核心论证链，程序因中文论证段术语密度低而误报） |

## 六、本轮修改的文件

- 04_proposal/sections/rationale.md（补角标 17 处、措辞统一、删冗余修饰、莫尔判据措辞对齐）
- 04_proposal/sections/content.md（κ-Br 口径重写、年度计划对齐、补莫尔判据句、拆分超长句、删冗余修饰）
- 04_proposal/sections/scheme.md（κ-Br 自相矛盾句修正、截止律按原文重写、角标密度压缩 42→19、拆分超长句、用词精确化）
- 04_proposal/sections/references.md（新增 [48]、同步 48 条挂钩注释至实际引用位置、修正 [29] 注释）
- 04_proposal/sections/full_review.md（骨架更新：新增 κ-Br 行、截止律行、莫尔室温窗口行；1546 字）
- 04_proposal/proposal-draft.md（由五个章节文件重新组装）
- 00_research_idea.md（补齐"拟开展研究内容和方案""拟采用技术路线""创新点""来源与可靠性"四节占位内容）
- 02_literature/reading-notes.md（追加 [48] 阅读记录）

未改动：03_method/method-manual.md（方法学手册由轮末专职 update_method_manual 步骤维护，writer 不写）。
