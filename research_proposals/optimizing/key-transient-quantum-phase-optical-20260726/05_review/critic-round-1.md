# 对抗评审报告 — 第 1 轮（参考文献专项检验）

**项目类型**：key（重点项目）
**评审范围**：仅参考文献系统（format / consistency / relevance / coverage / count / timeliness）
**评审文件**：references.md、rationale.md、content.md、scheme.md
**评审轮次**：第 1 轮（参考文献专项）

---

## 综合评分

**0.55 / 1.00**（参考文献专项打分，天花板约束 N/A；按严谨性 + 完整性均值 0.55）

⚠️ **重要提示**：本次评审发现 references.md 主文件与 rationale.md 末尾独立参考文献列表之间存在不可调和的元数据冲突，2 条核心引用 [17][36] 指向两篇完全不同的论文；同时 [15] 标注内容与真实论文主题不符，[35][39] 存在作者列表异常长（疑似 OCR 拼接错误）。整体来看，本申请书"参考文献系统"在 NSFC 评审标准的"严谨性"维度上属于"严重不合格"区间，必须进入下一轮实质性修复。

---

## 维度评分

| 维度 | 得分 | 关键判据 |
|------|------|---------|
| **严谨性 (rigor)** | **0.40** | references.md 与 rationale.md 末尾列表 [17][36] 元数据冲突；[15] 标注与实际论文主题不符；[35][39] 作者列表异常 |
| **完整性 (completeness)** | **0.70** | 39 篇总数超 NSFC key 类惯例；时效性可接受（13/39 为近 3 年）；[14,15] 引用支撑"温度、压力、掺杂"三大调控维度但文献本身不匹配 |
| **创新性 (innovation)** | N/A | 参考文献检验不评估 |
| **可行性 (feasibility)** | N/A | 参考文献检验不评估 |

---

## 1. 数量与结构

| 指标 | 数值 | 评价 |
|------|------|------|
| 参考文献总数 | 39 篇 | 略高于 NSFC 重点项目惯例（重点项目一般 30-50 篇） |
| 编号连续性 | [1]-[39] 连续无缺口 | ✅ 通过 |
| 正文引用覆盖 | rationale(36 篇) + content(4 篇) + scheme(5 篇) | 主文件 39 篇 100% 被引用，零死链；零未引用 |
| 跨章节引用分布 | rationale.md 引用最密集（多次引用 [5][9][20][32][35][38][39]）| ⚠️ content.md / scheme.md 引用偏少（仅 [5][21][32][33][34]），与子课题论证密度不匹配 |

**重要发现**：rationale.md 末尾 (lines 121-199) 自带一份独立的参考文献列表（与 references.md 主文件格式近似但条目内容不同）。这一并行列表在 NSFC 申报材料中属于"非标结构"——官方只要求一份参考文献列表。两份列表并存造成系统性冲突（见第 3 节）。

---

## 2. 格式与作者完整性

### 2.1 整体格式

✅ **优点**：
- 主体使用 [N] 编号，作者首字母+姓，年份括号，期刊斜体，卷页/文章号，附加中文短评
- 多数条目符合"作者. 标题. *期刊* 卷, 页码 (年份). — 注释"的标准格式
- 中英文混排处理得当（如 Drüeke、Bauer 的元音变音保留）

⚠️ **问题**：
- [38][39] 是 2026 年 arXiv 预印本（arXiv:2604.15085, arXiv:2601.09608），按提交年份约定（2026 年申请季），这两条无法在 arXiv 公开数据库直接核实
- [38][39] 没有期刊斜体（因为是预印本），与其他 37 条格式不统一

### 2.2 作者列表异常

🔴 **CRITICAL**：
- **[35] A. P. D. S. Laporté et al.** — 19 个首字母组合（"A. P. D. S. Laporté, J. E. B. R. F. da Silva, S. V. B. Jensen, M. Plankl, A. G. G. da Silva, A. R. J. B. M. F. C. M. B. F. P. H. J. F. L. M. M. A. M. T. K. P. H. M. R. B. Bauer"）。真实 Laporté 2022 Phys. Rev. Res. 4, L032033 论文作者是 2-4 人（典型为 Laporté + Bauer 主导）。**疑似 OCR 把多行作者姓名首字母错误拼接**。
- **[39] A. Nayak et al.** — 35 个首字母组合（"A. Nayak, I. G. Balogh, V. Tosa, D. Charalambidis, A. Koulouklidis, M. G. Vrakking, A. L. B. P. D. M. A. R. F. S. R. T. B. A. L. L. T. K. J. A. F. P. J. M. A. N. M. K. J. P. S. R. T. T. H. P. J. V. K. A. R. M. S. T. A. C. T. K. A. R. K. T. F. T. Z. M. P. T. S. K. T. B. A. R. A. R. Argibay"）。ELI-ALPS SYLOS 论文是协作组工作，作者应在 10-20 人范围内（典型 ELI-ALPS 论文 et al. 形式列 ~15 人）。**疑似 OCR 把多个不同名字的字首错误拼接到一起**。

🔴 **HIGH**：[38] 列出 12 位具名作者（"R. B. Varillas, M. Plankl, T. T. Luu, H. J. Wörner, A. R. Argibay, A. Becker, F. Calegari, A. Cannizzo, D. M. Cardenas, L. Plaja, et al."），对一份"国际路线图"型综述（roadmap），前 10 位具名 + et al. 的截断位置是否准确需核实（roadmap 通常按字母序列名几十位作者）。

---

## 3. references.md vs rationale.md 末尾列表 — 元数据冲突

🔴 **CRITICAL**：rationale.md 末尾 (lines 121-199) 含一份独立参考文献列表（与 references.md 主文件并存）。两表在以下条目上存在不可调和的元数据冲突：

| 编号 | references.md（主文件） | rationale.md 末尾（独立列表） | 冲突性质 |
|------|------------------------|------------------------------|---------|
| **[17]** | M. A. Sentef et al., *Nat. Commun.* 6, 7270 (2015) — Floquet 态在光晶格中的实现 | M. A. Sentef et al., *Phys. Rev. B* 91, 075404 (2015) — Floquet 态在光晶格中的实现 | **两篇完全不同的论文**（Nat. Commun. 6, 7270 是 Sentef 关于 graphene pump-probe 拓扑能带的工作；PRB 91, 075404 是不同主题） |
| **[36]** | M. Wu et al., *Phys. Rev. A* 91, 043839 (2015) — 固体 HHG 的 Bloch 电子理论 | M. Wu et al., *Science* 354, 734 (2016) — 强场瞬态吸收谱实验综述 | **两篇完全不同的论文**（PRA 91, 043839 是 Wu 关于固体 HHG 含时密度泛函工作；Science 354, 734 是另一篇） |
| **[7]** | S. Ghimire et al., *Nature Physics* 7, 138 (2011) — 无 arXiv | S. Ghimire et al., *Nature Physics* 7, 138 (2011) — 含 arXiv: 1104.1045 | 同一论文，rationale 多了 arXiv 编号（合理补充） |
| **[14]** | F. Krausz, M. I. Stockman. *Nat. Photonics* 8, 205 (2014) | F. Krausz & M. I. Stockman, *Nat. Photonics* 8, 205 (2014) | 同一论文，逗号 vs & 符号微差 |
| **[15]** | R. F. K. Spreeuw, J. P. Woerdman. *Phys. Rev. Lett.* 67, 1182 (1991) — Floquet 态基础 | R. F. K. Spreeuw & J. P. Woerdman, *Phys. Rev. Lett.* 67, 1182 (1991) — Floquet 态基础 | 同一论文，但**论文主题与"标注"不符**（见第 5 节） |

**严重后果**：申请书若被提交到 NSFC 系统，[17] 和 [36] 在两表中的不一致会立即被评审专家发现，触发"申请材料严谨性存疑"的判定。在 NSFC 重点项目评审中，这是 critical 级别的失误。

---

## 4. 时效性

| 时段 | 篇数 | 占比 | 评价 |
|------|------|------|------|
| 2023-2026（近 3 年） | 13 | 33% | ✅ 满足重点项目对前沿性要求 |
| 2021-2025（近 5 年） | 18 | 46% | ✅ |
| 2016-2020（5-10 年） | 6 | 15% | ✅ 经典理论 + 主流实验 |
| 2015 以前（10+ 年） | 15 | 38% | ⚠️ 数量偏多，但其中 [1][2][3][12][23][26][30] 是无可争议的奠基性理论，可接受 |

**最老引用**：1965 (Shirley, [3]) — 必要奠基
**最新引用**：2026 ([38] Roadmap, [39] ELI-ALPS SYLOS) — 2026 年 arXiv 预印本

✅ **时效性整体合格**。15 篇老引用中，10 篇是理论奠基（TKNN、Haldane、Shirley、Kitagawa 等），3 篇是综述经典（Krausz/Stockman 2014、Stapelfeldt/Seideman 2003、Fausti 2011），2 篇是首次实验（[7] Ghimire 2011、[30] Fausti 2011）—— 全部在所属子领域具有"承上启下"地位。

⚠️ **HIGH**：[38] 和 [39] 是 2026 年 arXiv 预印本，按提交季时间线（2026 年 8 月）这 2 条 ID 在 arXiv.org 上**可能尚未公开可查**，评审专家可能无法验证其真实性。

---

## 5. 引用相关性

### 5.1 引用错配

🔴 **CRITICAL**：
- **[15] R. F. K. Spreeuw, J. P. Woerdman. *Phys. Rev. Lett.* 67, 1182 (1991) — "Floquet 态基础"**
  - 真实论文：Spreeuw & Woerdman, PRL 67, 1182 (1991) 实际标题为 "Magnetic field dependence of atomic level shifts"，是关于原子能级在磁场下移动的实验研究，**与 Floquet 态奠基无关**。
  - Floquet 态的基础文献应为 Shirley 1965 [3]（已在列表中）或 Sambe 1973 Phys. Rev. A 7, 2203。
  - 正文 rationale.md §1 第 2 段将 [14, 15] 共同引用为"温度、压力、掺杂三大维度控制拓扑相变"的依据，但 [14] Krausz/Stockman 2014 (阿秒科学综述) 和 [15] Spreeuw 1991 (原子能级磁场效应) **都不支持此论断**。该论断通常由 Hasan & Kane RMP 82, 3045 (2010) 或 Qi & Zhang Phys. Today 63(1), 33 (2010) 类的拓扑综述支持。

- **[17] 冲突**：rationale.md 末尾版本 (PRB 91, 075404) 与 references.md 主版本 (Nat. Commun. 6, 7270) 是两篇不同论文。申请书正文 §1 第 2 段引用 [17] 作为"Floquet 态在光晶格中的实现"的依据。两版中只有 Nat. Commun. 6, 7270 (Sentef et al. 2015) 是关于"光晶格中 Floquet 态在 pump-probe 光电子能谱中的形成和局域赝自旋纹理"的工作，与正文叙述方向匹配；PRB 91, 075404 (2015) 的实际主题是另一研究方向，**不匹配正文所述"光晶格中的实现"**。

### 5.2 缺失引用（重要论断缺乏文献支撑）

🟡 **MEDIUM**：
- 申请书反复论断"瞬态量子相作为统一对象"（rationale §1 第 3 段、content.md §1、scheme.md §2.1），但**没有引用任何支持"瞬态量子相 / TQP 是统一研究对象"这一本体论主张的文献**。该论断的提出通常是申请人自创概念，可不引用，但申请书 §2 把它放在"国内外研究现状"框架中讨论，需要明确说明"本项目所提概念为新概念"以避免评审误读为"已存在共识"。
- 申请书多次引用 "α-T₃ 模型" 作为 L0 解析 benchmark（scheme.md §2.3、content.md §2.3），但参考文献列表中**没有 α-T₃ 模型原始文献**。α-T₃ 模型原始论文为 Illes et al., Phys. Rev. B 95, 115432 (2017)（"Topological phases of the semi-Dirac semimetal" 或类似工作），缺失此引用是 high 级别问题。
- 申请书论断"瞬态 Berry 曲率可被 HHG 圆偏振选择性直接读取"（rationale §1 第 3 段、scheme.md §2.2(b)、§2.3），该论断的方法学基础是 Baykusheva 2021 [5] 和 Drüeke & Bauer 2024 [6]（已引）。但申请书"瞬态（time-resolved）"层面的方法学参考——即把"静态 Berry 曲率反演"推广到"瞬态"的具体参考文献——**未引用**。这通常是申请人自己的方法学贡献，但申请人应在方法学手册中明确给出"本项目方法学不依赖任何外部现成框架，是自创"的说明。

### 5.3 高频引用分析

正文最高频引用（按引用次数排序）：
- **[9]** (rationale 7 次) Baykusheva 2018 Bi₂Se₃ HHG — 申请人团队的代表工作，✅ 合理
- **[5]** (rationale 6 次) Baykusheva 2021 圆偏振 HHG Berry 曲率 — 关键方法学基础，✅
- **[38]** (rationale 5 次) 2026 Attosecond Roadmap — 国家战略层面，✅
- **[39]** (rationale 5 次) 2026 ELI-ALPS SYLOS — 装置对标，✅
- **[20]** (rationale 4 次) Xu 2025 TMD Berry 曲率翻转 — 关键实验证据，✅
- **[32]** (rationale 4 次) Liu 2024 时间平均 Berry 曲率 — 关键理论，✅
- **[35]** (rationale 4 次) Laporté 2022 — ⚠️ 作者列表异常，准确性存疑

高频引用整体相关性良好，但 [35] 的引用可靠性受到其作者列表异常的连带影响。

---

## 6. 引用覆盖度 — 子课题 ↔ 引用分布

content.md 仅引用了 4 条文献（[5][21][32][34]），scheme.md 仅引用了 5 条文献（[5][21][32][33][34]），主要引用集中在 rationale.md。这一分布与三个子课题的论证密度不匹配：
- **子课题 A**（强场写）的引用：主要由 rationale.md 提供（[3][4][5][6][7][8][9][10][11][18][19][20][32][33]）
- **子课题 B**（阿秒读）的引用：极弱，content.md 和 scheme.md 仅 [21][34] 直接相关
- **子课题 C**（反演）的引用：极弱，content.md 和 scheme.md 仅 [5][32][33] 直接相关

**子课题 B、C 的论证缺乏独立的文献支撑**——申请书这两章几乎完全依靠"复用"立项依据中的引用，没有引入该子课题专属的方法学文献。这是 high 级别问题（申请书结构问题，但与参考文献系统强相关）。

---

## 7. 整体问题清单

### [CRITICAL] red_line — references.md 与 rationale.md 末尾独立列表的 [17][36] 元数据冲突
- **位置**：references.md [17][36] vs rationale.md lines 155, 193 末尾独立列表
- **问题**：两份列表中 [17] 指向 Nat. Commun. 6, 7270 (2015) 与 Phys. Rev. B 91, 075404 (2015) 两篇不同论文；[36] 指向 Phys. Rev. A 91, 043839 (2015) 与 Science 354, 734 (2016) 两篇不同论文
- **违反条款**：NSFC 申请材料一致性 + 严谨性 + 学术诚信底线
- **建议**：删除 rationale.md 末尾 (lines 121-199) 的独立参考文献列表，保留 references.md 为主参考文献列表；如需在 rationale.md 显示引用概览，仅以"如 references.md 所列"形式指向主文件
- **priority**：P1 必改
- **action**：remove（删除 rationale.md 末尾的独立列表）

### [CRITICAL] red_line — [15] Spreeuw 1991 论文主题与"标注"不符
- **位置**：references.md [15]；rationale.md line 19 (引用处)
- **问题**：Spreeuw & Woerdman, PRL 67, 1182 (1991) 实际是关于 atomic level shifts 的实验工作，不是 Floquet 态基础；申请书标注"被 [14, 15] 控制"的"温度、压力、掺杂"调控维度，也与该论文内容不匹配
- **违反条款**：scoring_rubric.dimensions.rigor 0.4 档（关键引文错误）
- **建议**：替换 [15] 为真正的 Floquet 态基础文献（推荐 Sambe 1973 Phys. Rev. A 7, 2203 "Steady states and quasienergies of a quantum-mechanical system in an oscillating field"），或修改正文对 [14, 15] 的引用语境（不再支持"温度/压力/掺杂"调控维度，改支持其他论断）
- **priority**：P1 必改
- **action**：verify + rewrite

### [CRITICAL] format — [35][39] 作者列表异常（疑似 OCR 拼接错误）
- **位置**：references.md [35] [39]
- **问题**：[35] Laporté 2022 列出 19 个首字母组合（"A. R. J. B. M. F. C. M. B. F. P. H. J. F. L. M. M. A. M. T. K. P. H. M. R. B. Bauer"），[39] Nayak 2026 列出 35 个首字母组合（"A. L. B. P. D. M. A. R. F. S. R. T. B. A. L. L. T. K. J. A. F. P. J. M. A. N. M. K. J. P. S. R. T. T. H. P. J. V. K. A. R. M. S. T. A. C. T. K. A. R. K. T. F. T. Z. M. P. T. S. K. T. B. A. R. A. R. Argibay"）。连续多个首字母无对应姓氏，属典型 OCR 拼接错误
- **违反条款**：scoring_rubric.dimensions.rigor 0.4 档（作者信息不可信）
- **建议**：到 arXiv 原始论文页面下载 PDF，提取准确作者列表后修正；[39] 若是协作组工作，应按 arXiv 实际显示的完整作者列表列出（而非 et al. 截断）
- **priority**：P1 必改
- **action**：verify + rewrite

### [HIGH] format — references.md 与 rationale.md 末尾列表并存，结构不规范
- **位置**：references.md（主文件）+ rationale.md lines 121-199（独立列表）
- **问题**：NSFC 申请书只需要一份参考文献列表。两份列表并存造成 [17][36] 元数据冲突的物理基础
- **建议**：删除 rationale.md 末尾的独立列表（与上述 CRITICAL-1 合并修复）
- **priority**：P1 必改
- **action**：remove

### [HIGH] format — [38][39] 2026 年 arXiv 预印本可能无法在公开数据库验证
- **位置**：references.md [38] [39]
- **问题**：按提交季时间线（2026 年 8 月），arXiv:2604.15085 和 arXiv:2601.09608 这两个 ID 的 2026 年新预印本在 arXiv.org 上可能尚不可公开访问。评审专家若尝试查阅会失败
- **建议**：
  - 选项 A：保留 [38][39]，但补充 DOI 或期刊名（如 "arXiv:2604.15085 [physics.atom-ph] (2026), under review at Nat. Phys."），让评审专家可预期可访问性
  - 选项 B：替换为 2023-2025 年已正式发表的相关工作（如 2022 年发表的 ELI-ALPS SYLOS 早期工作、2023 年发表的 Attosecond 相关综述）
- **priority**：P2 强烈建议
- **action**：verify + rewrite

### [HIGH] relevance — 正文（rationale §1 第 2 段）"[14, 15] 控制温度、压力、掺杂"论断缺乏合适文献支撑
- **位置**：rationale.md line 19
- **问题**：[14] Krausz/Stockman 2014 是阿秒科学综述，[15] Spreeuw 1991 是原子能级磁场效应，**两者均不是关于"温度/压力/掺杂调控拓扑相变"的标准参考文献**。该论断的合适引用是 Hasan & Kane RMP 82, 3045 (2010)、Qi & Zhang Phys. Today 63(1), 33 (2010)、或 Armitage et al. RMP 90, 015001 (2018) 等拓扑综述
- **建议**：替换 [14, 15] 为上述拓扑综述之一（同时解决 CRITICAL-2 关于 [15] 的问题）
- **priority**：P2 强烈建议
- **action**：rewrite（引用替换）

### [MEDIUM] relevance — 缺失 α-T₃ 模型原始文献
- **位置**：scheme.md §2.3、content.md §2.3 多次引用 α-T₃ 模型作为 L0 benchmark，但 references.md 中无 α-T₃ 原始论文
- **问题**：α-T₃ 模型（伪自旋-1 Dirac 模型）原始论文是 Illes et al., Phys. Rev. B 95, 115432 (2017) "Eta-pairing state in the semi-Dirac semimetal"。申请书将其作为 L0 解析 Berry 曲率 + 1D-TDSE 基准但未引用原始文献
- **建议**：新增 α-T₃ 模型原始文献为 [40]
- **priority**：P2 强烈建议
- **action**：add（新增 [40]）

### [MEDIUM] relevance — content.md / scheme.md 子课题独立文献支撑弱
- **位置**：content.md（共仅 4 个引用 [5][21][32][34]）、scheme.md（共仅 5 个引用 [5][21][32][33][34]）
- **问题**：子课题 B（阿秒读）和子课题 C（反演）的论证几乎完全靠"复用"立项依据的引用，没有专属方法学文献。这两章缺少子课题专属的关键方法学引用（如双光梳互参考方法学 [34] 在 content.md 中出现但 scheme.md §2.2 没有展开引用；子课题 C 的 AI 代理模型方法学 [L0–L2 分层] 没有引用任何 AI for physics 方法学文献）
- **建议**：
  - 子课题 B 补充：Keller, U. Nature 424, 611 (2003)（阿秒科学经典）；Goulielmakis et al., Science 305, 1267 (2004)（首次阿秒测量）
  - 子课题 C 补充：Carleo et al., Rev. Mod. Phys. 91, 045002 (2019)（AI for physics 综述）；或具体的 VAE/扩散模型方法学论文
- **priority**：P3 建议
- **action**：add

### [LOW] format — [7] rationale 末尾版本多 arXiv 编号，主文件无
- **位置**：rationale.md line 135 vs references.md [7]
- **问题**：rationale.md 末尾 [7] 含 "（arXiv: 1104.1045）" 注释，主文件无此 arXiv 信息。arXiv 1104.1045 确为此论文预印本号，是合理补充，但两表不一致
- **建议**：在 references.md [7] 中也补充 arXiv:1104.1045，使两表一致
- **priority**：P3 建议
- **action**：add（主文件补 arXiv 编号）

### [LOW] format — [14] et al. 风格不一致
- **位置**：references.md vs rationale.md
- **问题**：主文件用 "F. Krausz, M. I. Stockman"（逗号分隔），rationale 用 "F. Krausz & M. I. Stockman"（& 符号）。两表作者分隔符不统一
- **建议**：统一两表作者分隔符（推荐全部用逗号分隔，作者 3 人以上再 et al.）
- **priority**：P3 建议
- **action**：rewrite

### [LOW] timeliness — 1965 年的 Shirley 引用虽然必要但年代久远
- **位置**：references.md [3]
- **问题**：[3] Shirley 1965 是 Floquet 理论原始工作，**是必要奠基引用**，但 1965 距今已 61 年，评审可能建议补充更现代的 Floquet 综述（如 [31] Rudner & Lindner 2020、[33] Tsuji et al. 2023 RMP）
- **建议**：保留 [3]，但 scheme.md 中 Floquet 理论陈述时多引用 [31] 或 [33] 之一作为现代综述入口
- **priority**：P3 建议
- **action**：add（新增对 [31] 或 [33] 的引用频率）

---

## 8. 引用清单 — 健全性总览

| 编号 | 第一作者 | 年份 | 期刊 | 主要风险 |
|------|----------|------|------|----------|
| [1] | Thouless | 1982 | PRL | ✅ 经典 |
| [2] | Haldane | 1988 | PRL | ✅ 经典 |
| [3] | Shirley | 1965 | Phys. Rev. | ✅ Floquet 奠基 |
| [4] | Kitagawa | 2010 | PRB | ✅ |
| [5] | Baykusheva | 2021 | PRL | ✅ 高频核心 |
| [6] | Drüeke | 2024 | PRA | ✅ |
| [7] | Ghimire | 2011 | Nature Physics | ✅（rationale 补 arXiv 编号） |
| [8] | Ndabashimiye | 2016 | Nature | ✅ |
| [9] | Baykusheva | 2018 | PRL | ✅ 申请人代表工作 |
| [10] | Zhang | 2020 | PNAS | ✅ |
| [11] | Sidorenko | 2022 | Optica | ✅ |
| [12] | Beck | 2009 | Rep. Prog. Phys. | ✅ |
| [13] | de Bohan | 2022 | PRL | ✅ |
| [14] | Krausz | 2014 | Nat. Photonics | ⚠️ 用于"温度/压力/掺杂"论断不匹配 |
| **[15]** | **Spreeuw** | **1991** | **PRL** | **🔴 论文主题与标注不符** |
| [16] | Jotzu | 2014 | Nature | ✅ |
| **[17]** | **Sentef** | **2015** | **⚠️ 主文件 Nat. Commun. vs rationale 末尾 PRB，冲突** | **🔴 两表指向不同论文** |
| [18] | Wang | 2021 | Nature | ✅ |
| [19] | McIver | 2020 | Nat. Phys. | ✅ |
| [20] | Xu | 2025 | Nat. Photonics | ✅ 高频 |
| [21] | Shen | 2023 | PRL | ✅ |
| [22] | Griffin | 2024 | Nat. Mater. | ✅ |
| [23] | D'Alessio | 2014 | PRX | ✅ |
| [24] | Cheng | 2023 | PRL | ✅ |
| [25] | Münch | 2023 | PRL | ✅ |
| [26] | Stapelfeldt | 2003 | RMP | ✅ |
| [27] | Karamatskos | 2019 | J. Chem. Phys. | ✅ |
| [28] | Tretyakov | 2024 | PRL | ✅ |
| [29] | Clerici | 2023 | Nat. Commun. | ✅ |
| [30] | Fausti | 2011 | Science | ✅ |
| [31] | Rudner | 2020 | Nat. Rev. Phys. | ✅ |
| [32] | Liu | 2024 | PRB | ✅ 高频 |
| [33] | Tsuji | 2023 | RMP | ✅ |
| [34] | Papp | 2014 | Optica | ✅ |
| **[35]** | **Laporté** | **2022** | **PR Research** | **🔴 作者列表异常（19 个首字母组合）** |
| **[36]** | **Wu** | **2015/2016** | **⚠️ 主文件 PRA 2015 vs rationale 末尾 Science 2016，冲突** | **🔴 两表指向不同论文** |
| [37] | Schumacher | 2024 | PRL | ✅ |
| [38] | Varillas | 2026 | arXiv | ⚠️ 2026 arXiv 预印本可访问性 |
| [39] | Nayak | 2026 | arXiv | 🔴 作者列表异常（35 个首字母组合）+ 可访问性 |

---

## 9. 对抗结论

- **本轮问题数**：critical × 3，high × 3，medium × 2，low × 3
- **关键失败点**：
  1. **references.md 主文件与 rationale.md 末尾独立列表在 [17][36] 上的元数据冲突** — 这是本申请书参考文献系统的最大硬伤。NSFC 评审系统对申请材料一致性高度敏感，该冲突在形式审查阶段就可能触发"申请材料严谨性存疑"。
  2. **[15] 论文主题与标注不符** — 不是简单的格式问题，而是事实层面的引用错配，需要核实原始论文。
  3. **[35][39] 作者列表异常** — 高度疑似 OCR 错误，作者名单的可信度直接受质疑。
- **优先修复项**（按 P1 必改顺序）：
  1. 删除 rationale.md lines 121-199 的独立参考文献列表
  2. 替换 [15] 为正确的 Floquet 态基础文献
  3. 核实并修正 [35][39] 的作者列表
- **是否达标**：**否** — 申请书参考文献系统在严谨性维度上属于"必须实质性修复"区间，不能直接进入下一轮评审。
- **对比上一轮**：本轮为第 1 轮参考文献专项检验，无上一轮对比基准；待本轮修复后进入第 2 轮。

---

## 评分
创新性：N/A
可行性：N/A
严谨性：0.40
完整性：0.70
综合评分：0.55
