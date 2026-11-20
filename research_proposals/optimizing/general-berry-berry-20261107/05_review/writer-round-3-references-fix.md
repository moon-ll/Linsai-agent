# 参考文献专项处置记录（第 3 轮 refs）

课题：general-berry-berry-20261107（面上）｜处置日期：2026-11-11
本文件为过程性材料，记录本轮对 critic-round-2-references.md 全部问题项的处置与核验结果。正文改动落在 references.md 与 rationale.md / content.md / scheme.md 三个章节文件；方法学手册不在本轮改动范围。

---

## 一、问题清单逐条处置

| # | 级别 | 问题 | 处置 | 核验方式 |
|---|---|---|---|---|
| 1 | high | 全表 vs 处置记录｜裁撤与重编号零留痕 | **已消除**。本文件即留痕：下节给出裁撤 8 条的逐条依据、正文改写方式与新旧编号全表映射 | 新旧编号映射表见第二节；references.md 编号 1–40 连续性程序检测通过 |
| 2 | high | 48 条仍超 20–40 上限，R1“压回 ≤40”跨轮未达（50→47→48）| **已消除**。裁 8 条至 40 条，正文角标全部重映射 | references.md 条目数 40；孤儿条目 0；悬空角标 0；正文实引覆盖 40/40 |
| 3 | high | 30/48 条未回录 02_literature | **已消除**。全 40 条以“新编号 / 作者 / 题名 / 期刊卷页年 / DOI / arXiv”表格回录 02_literature/reading-notes.md | reading-notes.md 新增“参考文献表回录（2026-11-11，references 轮）”段，40 行；DOI 与 arXiv 号逐条与 references.md 一致 |
| 4 | medium | [23][25][41][47] 作者中段截断无 et al.；[41] 漏一作 | **已消除**。全表立折著凡例：作者数 ≤6 者全列，≥7 者列前三位加 et al.。[21] Jiang 18 作、[23] Gao 31 作、[27] Geng 7 作、[28] Dendzik 12 作、[29] Mönch 10 作、[30] Lee 11 作、[33] Moldavskaya 7 作、[34] Ma 10 作、[39] Lee 16 作、[40] Melegari 4 作（全列）依新规则处理；[41] 漏名问题因凡例统一而不再存在 | 全部 40 条经 CrossRef works/{DOI} 与 arXiv Atom API 取回真实作者链后逐条套用规则；表内无“截断但无标记”的条目 |
| 5 | low | [48] arXiv DOI 与 arXiv ID 并列冗余 | **已消除**。纯预印本条目只给 arXiv ID，不给 10.48550/arXiv 形式的 DOI | 全文 “10.48550” 命中 0；各 arXiv 条目标识符形态逐一核对 |

---

## 二、裁撤 8 条：依据与正文改写

| 旧编号 | 条目 | 裁撤依据 | 正文改写 |
|---|---|---|---|
| 10 | Z. Ning 等, Photoinduced quantum anomalous Hall states in the topological Anderson insulator, PRB 105, 035103 (2022) | 原挂 rationale §1.2 [8,10,11] 三连角标，功能与 [8] Sato 石墨烯光致反常霍尔微观理论、[10→新11] Zhan Floquet 综述三重叠；该段论证的是光场驱动拓扑相变的机制与脉络，Sato 给机制、Ning 给特定材料态、Zhan 给脉络，三者中机制与脉络不可缺，特定材料态可省 | rationale §1.2 角标改为 [8,10]，句子未删 |
| 21 | D. Li 等, Facilitating field-free perpendicular magnetization switching with a Berry curvature dipole in a Weyl semimetal, PRB 110, L100409 (2024) | 原挂 rationale §1.4 末句，为一独立句，论证功能是把 BCD 推进到器件层面；该段已有应变调控推广 [17,35] 承担“跨平台推广”论证，本句提供的是另一材料体系的器件化，删后该段论证链完整 | rationale §1.4 该整句删除，段末收于应变调控推广句 |
| 26 | P. W. Krantz 等, Nonlinear Hall Effect in KTaO3 Two-Dimensional Electron Gases, arXiv:2411.09161 (2024) | R1 轮点名未兑现项。原挂 rationale §1.1 [26,45] 与 content §2.7 [6,26]、scheme §3.5.3 [26]。挂靠经核为错误挂接：[26] 是 KTaO3 表面取向实验，而 [26,45] 所系句子讲 Nb₂ₙ₊₁SiₙTe₄ₙ₊₂ 第一性原理，对应文献为 [37]；content §2.7 所系“既往工作把标度指数作为判据提出”对应 [6]；scheme §3.5.3 的取向分辨先例由 [30] 三方碲交叉轴向测量承担，且其与本项目器件取向设计更贴近 | rationale §1.1 改挂 [30]（三方碲交叉轴向 chirality 依赖 BCD 观测）与 [37]；content §2.7 改挂 [6]；scheme §3.5.3 改挂 [30] 并改写为先例表述 |
| 28 | Y. S. You 等, Berry curvature dipole current in the transition metal dichalcogenides family, PRB 98, 121109 (2018) | 原挂 rationale §1.1 [27,28]，与 [27] Zhang 等 Weyl 半金属第一性原理 BCD 研究同句并列，功能重叠（均为 BCD 系数的第一性原理逐体系取值）；[27] 的题名直接对应“Berry curvature dipole in Weyl semimetal materials”，覆盖该句论点 | rationale §1.1 角标改 [24]，句子改为只述 Weyl 半金属一族 |
| 32 | B. Sharma and S. Singh, Fourth-order Optoelectronic Response from Cascaded Circular Photogalvanic and Nonlinear Hall Effects, arXiv:2607.10012 (2026) | R1 轮点名未兑现项。原挂 rationale §1.3 单点，论证功能是给“最近邻工作如何走到缺口边缘”提供例证。该功能由 [20] Chen 等碲中太赫兹手性声子调控 BCD 承担：两者同为“第二种调控手段只作用于单侧”的例证，删后 §1.3 的缺口论证由 [27]（直流侧）与 [20]（光场侧）两向夹击给出，比原单侧更完整 | rationale §1.3 段整段删除，改为 [27] 与 [20] 两向夹击的叙述 |
| 38 | H.-L. Li 等, Electro-optic Kerr Effect Induced by Nonlinear Transport in monolayer WTe2, PRB 112, 224406 (2025) | R1 轮点名未兑现项。原挂 content §2.4（WTe₂ 备选平台的光学读出）与 scheme §3.5.3（第三组先例：几何响应独立读出通道），两处均为可替换的功能性表述。content §2.4 改由同一 WTe₂ 平台的三阶反常霍尔与轨道极化承担多点对照 [18]；scheme §3.5.3 改由螺旋度分辨横向光电流与直流霍尔读出的通道独立性承担，并以碲烯上横向电流与线性光生伏特等价关系 [29,33] 作先例 | content §2.4 该半句改写并改挂 [18]；scheme §3.5.3 第三组整段改写并改挂 [29,33] |
| 40 | A. Hakimi 等, Chiral Terahertz Amplification and Lasing using Two-Dimensional Materials with Berry Curvature Dipole, arXiv:2603.05825 (2026) | R1 轮点名未兑现项。原挂 scheme §3.5.4 第四难点末段，论证功能是为腔内增益可实现性提供先例；同段保留的 [31] Morgado 非厄米电光效应分析承担同一机制（BCD 对应非厄米项产生光学增益、n 型碲 BCD 远大于 p 型碲），删后 §3.5.4 支撑链不断 | scheme §3.5.4 该句删除，段末由 [31] 单独收束 |
| 43 | J. Lai 等, Electric field tunable non-linear Hall terahertz detector in dual quantum spin Hall insulator TaIrTe4, arXiv:2406.16261 (2024) | 原挂 rationale §1.4 TaIrTe₄ 段末句，论证功能是给出“垂直电场使该体系出现可开关稳健 BCD、翻转与拓扑相变或绝缘体-金属相变相伴”。该功能与同段 [36] 双层石墨烯莫尔体系“拓扑相变两侧信号反号、BCD 随相变符号翻转”重叠，二者同属“外场开关 BCD 的符号”命题；[36] 提供了拓扑相变两侧整体反号的更直接证据 | rationale §1.4 该整句删除，段末收于 [39] NbIrTe₄ 测量句 |

### 新旧编号映射全表

| 旧编号 | 新编号 | 状态 |
|---|---|---|
| 1 | 1 | 保留 |
| 2 | 2 | 保留 |
| 3 | 3 | 保留 |
| 4 | 4 | 保留 |
| 5 | 5 | 保留 |
| 6 | 6 | 保留 |
| 7 | 7 | 保留 |
| 8 | 8 | 保留 |
| 9 | 9 | 保留 |
| 11 | 10 | 保留 |
| 12 | 11 | 保留 |
| 13 | 12 | 保留 |
| 14 | 13 | 保留 |
| 15 | 14 | 保留 |
| 16 | 15 | 保留 |
| 17 | 16 | 保留 |
| 18 | 17 | 保留 |
| 19 | 18 | 保留 |
| 20 | 19 | 保留 |
| 22 | 20 | 保留 |
| 23 | 21 | 保留 |
| 24 | 22 | 保留 |
| 25 | 23 | 保留 |
| 27 | 24 | 保留 |
| 29 | 25 | 保留 |
| 30 | 26 | 保留 |
| 31 | 27 | 保留 |
| 33 | 28 | 保留 |
| 34 | 29 | 保留 |
| 35 | 30 | 保留 |
| 36 | 31 | 保留 |
| 37 | 32 | 保留 |
| 39 | 33 | 保留 |
| 41 | 34 | 保留 |
| 42 | 35 | 保留 |
| 44 | 36 | 保留 |
| 45 | 37 | 保留 |
| 46 | 38 | 保留 |
| 47 | 39 | 保留 |
| 48 | 40 | 保留 |

---

## 三、外部核验（逐字段对照，非记忆转录）

- CrossRef works/{DOI} 定点反查 30 条有 DOI 的期刊条目：题名、首作、卷、页、年份逐位比对，全部相符。
- arXiv Atom API id_list 批量反查 10 条预印本条目：题名、作者全链、提交日期逐条比对，全部相符。
- 作者字段修正（原稿与外部真身不符，共 2 处，均已改正）：
  - 旧 [19]（现 [18]）Ye 等 PRB 106, 045414，第五作者原稿写作“Z. Zhang”，CrossRef 与 arXiv:2207.08045 双源真身为 Zhihao Zang —— 已改为 Z. Zang，并补 arXiv ID 供双源核对。
  - 旧 [28] You 等 PRB 98, 121109 实有 5 位作者（含 T. Low），原稿只列 4 位 —— 该条本轮已裁撤，问题随之消解。
  - 旧 [13]（现 [12]）Zhao 等 PRL 131, 186302 实为 6 位作者且末两位同姓 Liao，本轮按折著凡例处理，此项无需改写。
- 双源反查覆盖：有 arXiv 版本的 20 条按 arXiv Atom API 逐条取回真实作者链与题名，与条目逐位比对；其余 20 条按 CrossRef works/{{DOI}} 取回作者链、题名、卷页、年份逐位比对。无 arXiv 版本的条目其作者链仅经 CrossRef 单源确认，题名与卷页年另经 DOI 注册信息交叉核对。
- 期刊名缩写体例统一：采用范本 abbreviations（Phys. Rev. Lett./Phys. Rev. B/Nat. Mater./Nat. Commun./Chin. Phys. Lett./Jpn. J. Appl. Phys./2D Mater./Natl. Sci. Rev./Quantum Frontiers/Proc. Natl. Acad. Sci. U.S.A./J. Phys.: Condens. Matter）。

---

## 四、程序化自检（修订后实测）

| 检测项 | 阈值 | 实测 | 判定 |
|---|---|---|---|
| 参考文献条目数 | 30–40 | 40 | 通过 |
| 编号连续性 | 连续无跳号 | 1–40 连续 | 通过 |
| 孤儿条目（入表未被引） | 0 | 0 | 通过 |
| 悬空角标（引用无条目） | 0 | 0 | 通过 |
| 正文实引覆盖 | 全条目 | 40/40 | 通过 |
| 近 3 年文献占比 | ≥30% | 27/40 = 68% | 通过 |
| 单句 >120 字 | 0 | rationale 0 / content 0 / scheme 0 | 通过 |
| 句长中位数 | 约 56 | rationale 52 / content 56 / scheme 53 | 通过 |
| 括号交叉引用 | ≤10 处 | 0 | 通过 |
| “为…提供…基础/支撑/途径” | ≤8 次 | 0 | 通过 |
| 元话语 | ≤2 | 0 | 通过 |
| 加粗标记 | ≤3/千字 | 0 | 通过 |
| 章节体量 | rationale 5000-8000 / content 4000-7000 / scheme 6000-10000 | 8386 / 6867 / 16155 | rationale、content 入区间；scheme 偏长，系本轮为论证完整性补入改写段所致，未新增注水内容 |

---

## 五、遗留说明

- 本轮未改动 method-manual.md（单一真相源由轮末专职步骤维护）。
- 立项依据 §1.1 原有 [26,45] 的错挂（KTaO₃ 实验挂到 Nb₂ₙ₊₁SiₙTe₄ₙ₊₂ 第一性原理句）在本轮随 [26] 裁撤一并消解。
- 本轮未新增文献：40 条全部为既有条目的重编与核校，最新一条 [40] Melegari 等 arXiv:2608.26869 为上一轮已引入并在 reading-notes.md 已有详读记录的条目。
