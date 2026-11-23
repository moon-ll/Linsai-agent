# critic-round-1-references 处置记录（writer 轮）

- 对象：`04_proposal/sections/references.md`（49 条 → 50 条）
- 处置日期：2026-11-03
- 依据：`05_review/critic-round-1-references.md`（critical 0 / high 0 / medium 6 / low 2）
- 本轮聚焦维度：完整性（0.82 → 目标修复）

## 一、问题→处理结果对照表

| 问题 | 等级 | 处理结果 | 说明 |
|---|---|---|---|
| 1 | medium | **已修复** | 头注原声明"共 48 条、预印本 17 条"与表实不符（实为 49 条 / 18 条）。本轮按 skill 六节第 3 条（references 专属）将原核实声明式头注整体改写为正文式引文说明——按论证功能分块说明各条号区间对应的证据类别，不再出现计数句、见刊承诺或核实日志。改写后条目 50 条、预印本 12 条，头注描述与表实逐条吻合。 |
| 2 | medium | **已修复** | [42] Luttmann 已见刊版：`Phys. Rev. Applied` 15(3): 034036 (2021)，DOI 10.1103/PhysRevApplied.15.034036。核验：CrossRef `works/10.1103/PhysRevApplied.15.034036` 返回作者链（Luttmann/Bresteau/Hergott/Tcherbakoff/Ruchon）、卷期页、出版史全对；arXiv:2012.09528 的 `journal_ref` 字段本身即标注该刊版。条目去 †，改挂刊版 DOI，现编号 [44]。 |
| 3 | medium | **已修复** | [45] Zhong 已见刊版：`Ultrafast Science` 4: 0063 (2024)，DOI 10.34133/ultrafastscience.0063。核验：CrossRef 解析返回卷 4、文章号 0063、出版年 2024、作者链（Zhong/Cai/Bao/Wang/Lin/Chen/Peng/Tang/Gu/Tao/Zhang/Zhou，共 12 人）；arXiv:2510.16546 的 `journal_ref` 标注 "Ultrafast Sci. 4, 0063 (2024)"。条目去 † 改刊版，现编号 [46]；rationale §2.4"†Zhong 等[46]于 2025 年建成"同步改为"Zhong 等[46]于 2024 年建成"（刊版出版年 2024）。 |
| 4 | medium | **已修复** | rationale §2.2"2013 年又在拓扑绝缘体表面实现 Floquet-Bloch 态的实验观测"原为空挂具名论断。补原始实验文献：Wang Y.H., Steinberg H., Jarillo-Herrero P., et al. *Science*, 2013, 342: 453-457, DOI 10.1126/science.1239834（CrossRef 核验：作者链、卷期页、出版日 2013-10-25 全对）。新增为 [16]，rationale §2.2 首段改写为具名引注并补出物理内容（tr-ARPES 观测 Floquet-Bloch 带、圆偏振光子在狄拉克点打开额外能隙）；00_research_idea.md"现存研究空白或瓶颈"段同步补挂 [16]。 |
| 5 | medium | **已修复** | rationale §2.1 末"频梳级 CEP 稳定驱动技术趋于完备"原无 [N]。改写为具名引注并挂 [49] Meier 等：200 kHz、2 μm 光学参量放大器上差频被动稳定加轻量主动反馈，CEP 噪声在微秒到小时全部时间尺度压至 70 mrad（rms）以下。数值与 scheme §2.2(a) 第二级方案"75 mrad 目标在同波段已有实测先例"一致，未新增口径。 |
| 6 | medium | **已修复** | rationale §2.3 反演方法储备句原将"深度学习量子轨迹检索、双色场量子路径干涉解析、自注意力量子路径分析"三法并列为一句而仅末法挂 [36]，前两法空挂。逐法补挂：[37] Klimkin N.D. 等，Symmetry-aware deep neural networks for high harmonic spectroscopy in solids, *Optics Express*, 2023, 31(12): 20559, DOI 10.1364/oe.462692（深度网络反演谐波谱还原能带结构与入射脉冲参数）；[38] Chen Z. 等，Attosecond pulses from a solid driven by a synthesized two-color field at megahertz repetition rate, *ACS Photonics*, 2025, 12(5): 2819-2827, DOI 10.1021/acsphotonics.5c00410（固体双色场 HHG 与两色延迟扫描）。两条均经 CrossRef 核验作者链/卷期页/年份。三法各自具名引注。 |
| 7 | medium | **部分修复** | 条目总数由 49 → 50，仍高于常规 20–40 区间。已裁并 2 条可被同族条目吸收的单点引注条目：原 [28] Nayak A. 等（ELI-ALPS 高强阿秒光源）唯一引用点为 rationale §2.4"ELI-ALPS 提供装置开放"括注，改由同属 ELI-ALPS 且给出束线稳定度指标的 Csizmadia 等[40]承担；原 [44] Dubey K.A. 与 Neufeld O.（分子电荷迁移时标）唯一引用点为 rationale §2.3 列举句中的分子体系条目，与固体强场拓扑操控不同体系，删去后由 Faeyrman[12]、Jiménez-Galán[45]、†Zhao[19]三条固体侧工作承担。**未进一步压至 40 的理由**：其余 50 条经逐条核查均在正文有实语境引注且承载互不重叠的证据类（量子拓扑量、Bloch–Floquet 工程、量子几何读出、非平衡声子耦合、强场多体近似、实验装置、反演算法与误差核定、国内平台），继续裁并须删去承重引注或重写跨章论证链，将以严谨性（文献支撑真实，rigor 清单③）换取条目数，对"完整性"聚焦维度为净负。改为在头注按论证功能分块列出各条号区间的证据类别，使条目数有可核查的构成说明而非孤立数字。 |
| 8 | low | **已修复** | 预印本占比由 18/49 = 36.7% 降至 12/50 = 24.0%，低于 30% 警戒线。除问题 2/3 外另回录 3 条：[29] Tan 等（`ACS Nano`, 2026, DOI 10.1021/acsnano.6c15098；17 位作者链与 arXiv:2511.16165 完全一致，题名见刊时由 "Ultrafast μeV-Precision Bandgap Engineering in Low-Dimensional Topological Insulators" 改为现题，条目按刊版题录誊写）、[45] Jiménez-Galán 等（`Optica`, 2021, 8(3): 277, DOI 10.1364/optica.404257）、[47] Fan 等（`Comput. Mater. Sci.`, 2026, 268: 114641, DOI 10.1016/j.commatsci.2026.114641，前三位作者与 arXiv:2507.09234 一致）。 |
| 9 | low | **已修复** | 原头注"预印本条目见刊后将逐条回录刊版 DOI"为未执行承诺，随头注整体改写为正文式引文说明而删除；本轮已回录 5 条见刊版本（[29][44][45][46][47]），另 12 条为截至本轮检索未见刊版者，按 † 标注并保留 arXiv ID。 |

## 二、附加修复（超出 critic 点名范围）

1. **[42]/[45] 见刊回录引发的正文年份同步**：rationale §2.3 "†Tan 等[29]于 2025 年展示强场精确调控拓扑能隙的实验"改为"Tan 等[29]于 2026 年在 α-Bi₄Br₄ 中以低温瞬态反射谱实现微电子伏量级的能带重整"（随刊版年份与题名更新）；rationale §2.4 "†Fan 等[47]于 2025 年"改为"Fan 等[47]于 2026 年"；"†Zhong 等[46]于 2025 年"改为"Zhong 等[46]于 2024 年"。均不改动任何数值口径，仅同步出版年。

2. **AI 写作模式修复**：rationale.md 程序化检测超长句由 13 处降至 9 处（余下 9 处为表格行与公式密集技术句，属豁免类）。本轮改写的 4 处长句为 §2.2 末段、§2.3 末段、§2.4 首段、§1.3 末段，按"顺叙为主、防御性内容降权"拆分为连贯叙述式短句，未新增防御性表述。

3. **跨章重编号同步**：因新增 3 条、剔除 2 条，条目编号发生位移。对 rationale.md / content.md / scheme.md / 00_research_idea.md 全文角标做程序化重映射（LaTeX 数学区间如 `$[1, 2]$`、`$[0.3, 1]$` 已排除，避免误改物理量区间）。

## 三、文献真实性核验记录

- **全量核验方法**：CrossRef `api.crossref.org/works/{DOI}` 逐条反查（刊版条目 DOI、卷期页、作者链、出版史）；arXiv Atom API `export.arxiv.org/api/query?id_list=` 查 preprints 的题名/作者数/journal_ref/doi 字段；OpenAlex `filter=doi:10.48550/arxiv.{id}` 查 arXiv→期刊关联。
- **本轮新写入 / 回录的 8 条**（[16][29][37][38][44][45][46][47]）逐字段对照 CrossRef 记录誊写，作者顺序、姓氏缩写、年份、卷期页、DOI 全部一致。
- **被剔除的 2 条**（Nayak、Dubey）原条目本身核验为真，剔除理由为引用点可由同族条目承载，非真实性问题。
- **未写入任何池外条目**：本轮新增的 3 条均来自评审报告指定核校目标（Floquet-Bloch 2013 原始实验文献、深度学习谐波谱学反演、双色场固体 HHG），且均经当轮联网检索与 CrossRef 独立核实后誊写。

## 四、终检结果

| 项 | 结果 |
|---|---|
| 条目数 | 50 |
| 编号连续无跳号 | 是（1–50） |
| 孤儿条目（未被正文引用） | 0 |
| 空挂角标（正文引用无对应条目） | 0 |
| 正文引用覆盖 | 50/50 条目均在正文有实语境引注 |
| 预印本占比 | 12/50 = 24.0%（< 30% 警戒线） |
| 近三年（2024 年起）占比 | 36/50 = 72%（要求 ≥ 30%） |
| DOI / arXiv 二选一 | 合规（37 条刊版 DOI、12 条 arXiv、1 条刊版条目内注附 arXiv 链接） |
| 折著规则（≤3 全列，4+ 前三 + et al.） | 50/50 合规 |
| 跨章口径表 stale pattern 扫描 | 7 项全 OK（含 refs_doi_status_5_23_34 与 ref_zhao_18_vs_21_attribution） |
| 正文过程性痕迹（轮次号、内部文件名、占位符） | 0 命中 |
| sections/ 目录白名单 | 仅 rationale / content / scheme / full_review / references，无自创章节文件 |

## 五、未处理项说明

- **方法学手册（03_method/method-manual.md）未改动**：按 v6.9.60 单一真相源治理，方法学手册唯一真相源为 `03_method/method-manual.md`，由轮末专职 update_method_manual 步骤统一维护，writer 不得直接写该文件。
- **问题 7 的条目数下限**：见对照表第 7 行说明。
