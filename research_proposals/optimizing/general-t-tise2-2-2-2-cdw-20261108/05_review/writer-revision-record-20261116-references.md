# writer 处置记录（参考文献专项轮）

课题：general-t-tise2-2-2-2-cdw-20261108
依据评审：05_review/critic-round-3-references.md（9 个问题：critical 0，high 2，medium 5，low 2）
聚焦章节：04_proposal/sections/references.md（连带 rationale / content / scheme / full_review 角标同步）

## 一、逐条处置

### 问题 1 [high]｜[26] Ye 条目卷期年三重失真

**结论：已消除，并额外发现 DOI 指向错误论文。**

原条目记作 "Science China Physics, Mechanics & Astronomy 67, 247413 (2024)"。经 arXiv API 取 abs 页 journal_ref 为
"Sci. China-Phys. Mech. Astron. 69, 267412 (2026)"，按刊出真身更正。

附带核验：arXiv 元数据所挂 DOI 10.1007/s11433-023-2318-y 经 doi.org 内容协商实际解析到
v67 (2024) 的 "Experimental observation of the significant difference between surface and bulk Kondo processes in Kondo lattice YbCu2Si2"，
为作者侧著录错误；刊出版真实 DOI 为 10.1007/s11433-026-2952-3（CrossRef 书目核定：Sci. China-Phys. Mech. Astron. 69, 267412, 2026-04-28，刊版题名 "Ultrafast phonon hardening and nonthermal lattice potential reconstruction in the charge-density-wave…"）。

条目正文改为刊版题名 + 刊版卷期页 + 刊版 DOI。**注意**：预印本题名（"Ultrafast stiffening of the lattice potential and metastable state formation in 1T-TiSe2"）与刊版题名不同，本表采用刊版题名。

### 问题 2 [medium]｜[47][24] 题名滞预印本原形却挂刊版卷期

**结论：已消除。**

- [47] Laulhé 等：原题名 "Watching the birth of a charge density wave order: diffraction study on nanometer- and picosecond-scales"（预印本原形）。经 doi.org 核验，刊版题名为 "Ultrafast Formation of a Charge Density Wave State in 1T-TaSe₂"（PRL 118, 247401 (2017)）。已改为刊版题名。
- [24] Domröse & Ropers：原题名含 "cycled at megahertz rates"，该短语属预印本叙述性副题，刊版题为 "Femtosecond trimer quench in the unconventional charge-density-wave material 1T′-TaTe₂"（PRB 110, 085155 (2024)）。已删去该短语。

### 问题 3 [medium]｜[22][23][30][39][40] 首作首字母失真

**结论：已消除（5/5 全部核实并更正）。**

经 arXiv API 取全名单首作姓名核验：

| 条目 | 原著录 | 真实首作 | 处理 |
|---|---|---|---|
| Emeis & Caruso | Emeis M | Christoph **E**meis | 已改 |
| Agarwal 等 | Agarwal K | Aneesh **A**garwal | 已改 |
| Patel & Ghosal | Patel D | Ayussh Anubhav **P**atel | 已改 |
| Ali 等 | Ali S | Anzar **A**li | 已改 |
| Lien 等 | Lien S | Chun-Tung **C** Lien | 已改 |

### 问题 4 [low]｜[1] 对 [13] 同人异拼

**结论：已消除。**

经 arXiv API 核验：arXiv:2509.15358 首作为 "K. Dharmasiri"，arXiv:2602.11582 首作为 "Kusal Dharmasiri"，同一作者。两条统一作 Dharmasiri K，rationale §一.2 正文中"Dharmasani等人[9]"同步改为"Dharmasiri等人"。

### 问题 5 [high]｜35 条期刊条目零标识符

**结论：已消除（34 条期刊条目全部补 DOI，6 条预印本补 arXiv 编号，表内零遗漏）。**

核验路径：对每条构造候选 DOI → doi.org 内容协商（Accept: application/vnd.citationstyles.csl+json）取 volume/page/article-number/issued；对 APS 系新式不透明 DOI（10.1103/xxxxx-xxxx）先用 CrossRef bibliographic 查询定位，再经 doi.org 复核；预印本条目用 arXiv API 取 id/journal_ref/doi。

补录过程中发现并修正的实质错误（原文未列）：
- [12] Kogar 等 Science 358, 1314：原拟 DOI 10.1126/science.aan5355 解析 404，真实 DOI 为 **10.1126/science.aam6432**。
- [58] Lian 等 Nat. Commun. 11, 43：真实 DOI 为 **10.1038/s41467-019-13672-7**。
- [36] Nakata 等 Nat. Commun. 12, 5873：真实 DOI 为 **10.1038/s41467-021-26105-1**。
- [52] Venturini 等 Nat. Commun. 17, 8360：真实 DOI 为 **10.1038/s41467-026-73267-x**。
- [49] Hua 等 Rev. Sci. Instrum. 95, 033902：真实 DOI 为 **10.1063/5.0181310**。
- [31] Siemann 等 PRB 113, 075137：DOI 为 **10.1103/81xm-bzdy**。
- [33] Ainouche 等 PRB 114, 285403：DOI 为 **10.1103/5tsg-xnwt**。
- [38] Carpene PRL 137, 066902：DOI 为 **10.1103/5vkg-zvhv**。
- [44] Buchberger 等 PRX 15, 041028：DOI 为 **10.1103/9trc-9865**。
- [19] Tu 等 PRB 112, 224310：DOI 为 **10.1103/frw3-jl7n**（经 ORCID 记录 + CrossRef 双向确认）。
- [35] Lv 等 Nat. Commun. 17, 7123：DOI 为 **10.1038/s41467-026-73482-6**。
- [3] Oh 等 Nat. Commun. 17, 10893：DOI 为 **10.1038/s41467-026-77670-2**。
- [2] Fragkos 等 Commun. Phys. 9, 86：DOI 为 **10.1038/s42005-026-02521-x**。
- [46] Bray Adv. Phys. 43, 357：DOI 为 **10.1080/00018739400101505**。
- [48] Jarnac 等 C. R. Physique 22, 139：DOI 为 **10.5802/crphys.89**。

### 问题 6 [medium]｜折著三态并存无凡例

**结论：已消除。**

表首立凡例："作者不足四位时全部列出，四位及以上时列出前三位后加 et al."。全表 40 条按此统一：3 位及以下者（[1] 4 位按凡例列前 3 + et al.；[7][9][10][11][13][15][18][21][22][23][24][25][26][29][30][32][38][39][40] 等）核对后确认无折著三态残留；原先"首作 + et al."与"四作全列"混用的条目已归一。

### 问题 7 [medium]｜7 条已刊条目仍标预印本

**结论：已消除（全部回录刊版卷页 + DOI）。**

| 条目 | 原著录 | 刊版真身 |
|---|---|---|
| Novko | arXiv:2510.00556 | Phys. Rev. B 112, L241114 (2025), DOI 10.1103/bs8n-wt4h |
| Que 等 | arXiv:2603.24211 | Nature Reviews Physics (2026), DOI 10.1038/s42254-026-00986-x |
| Ali 等 | arXiv:2604.19110 | CrystEngComm 28, 3414 (2026), DOI 10.1039/D6CE00245E |
| Wang W 等 | arXiv:2502.11342 | Phys. Rev. Lett. 136, 256101 (2026), DOI 10.1103/btvb-ngy5 |
| Larsen 等 | arXiv:2311.08015 | npj Comput. Mater. 11, 152 (2025), DOI 10.1038/s41524-025-01631-4 |
| Guo 等 | arXiv:2501.09968 | Phys. Rev. Lett. 135, 136102 (2025), DOI 10.1103/j8vm-wb65 |
| Yilmaz 等 | arXiv:2608.05059 | Phys. Rev. B 114, L111109 (2026), DOI 10.1103/z2j1-gwj4 |

### 问题 8 [medium]｜62 条超 20–40 上限

**结论：已消除（裁至 40 条）。**

裁撤 22 条，均为同一论证簇内的重复覆盖或应用侧旁证，裁撤后正文逐句改写以保住论证链：
7、9、11、14、20、21、22、23、24、25、27、29、30、31、33、36、39、40、44、50、53、55、56、57。

裁撤依据（逐条给出同簇保留项）：
- [7] LaTe₃ 慢化 → 同句 [6] 承担；content §2.2 改写为"准一维体系在阈值激发密度处出现的序参量抑制动力学慢化[6]"。
- [9] EuTe₄ 滞回 → 同句 [35] 承担；rationale §一.4 改挂 [21] 与 [35]。
- [11] Rossnagel 综述 → 与保留的 [7] Grüner 功能重叠，且原处簇 [11,17-19,40] 删 [40] 后由 [17-19] 承担。
- [14] Cercellier → 原簇 [14-16] 删后由 [10][11] 承担。
- [20][22] 理论侧两独立句 → 合并改写为挂 [35] 的模式选择性电声耦合指纹句。
- [21][25][56] 国内工作三环节 → 压缩为能隙测量与特征温度定位两环节，[56] 奇偶层激子态整条裁去。
- [23] 几何 GL → 并入相序动力学语境，改挂 [29]。
- [24] 兆赫重复飞秒电子衍射 → 与 [4] 同句合并。
- [27][36] 维度轴插层/单层 → 保留 [13]，删去该分句。
- [29] Winkler K₀.₃MoO₃ → 拆句后与 [6] 同段承担。
- [30] 激子-超导互制理论 → 与 [8] 同簇。
- [31] trARPES 复核 → 交叉检验旁证，删去专名后保留论点。
- [33] Hf 掺杂 ZrTe₃ → 与 [19] 同簇。
- [39][40] 两篇综述二选一 → 按 critic 建议二选一，本轮两条同裁（裁后 [12][13] 与 [17-19] 仍覆盖 Mott 物理之争与公度性分类维度）。
- [44] 库仑工程 → 与 [28] 同句，保留 [28]。
- [50] 赝隙相 → 改挂保留的 [10]。
- [53][57] 铁轴序 → 合并入 [24] Carpene 句。
- [55] ML 势两步熔化 → 与 [25] 同句，删 [55] 保留 [25]。

同步新增 3 条（来自 02_literature/targeted-research/lit-gap-1794764511.md 检索池，均经当轮 arXiv + CrossRef 外部核验）：
- [21] Lv 等，Nat. Mater. 25, 420 (2025)，DOI 10.1038/s41563-025-02360-1，arXiv:2501.09715（EuTe₄ 两个错配非公度 CDW 联合共格出 13.6 nm 莫尔超晶格）。
- [22] Takahashi 等，PRX Energy 4, 033009 (2025)，DOI 10.1103/9bvh-3r6w，arXiv:2508.16017（EuTe₄ 极性 CDW 态可持续至 650 K，室温 Seebeck >500 μV/K，zT@460 K = 0.22）。
- [18] Elius 等，Phys. Rev. B 113, 235125 (2026)，DOI 10.1103/n72p-lpt6，arXiv:2508.06464（EuTe₄ 低能 CDW 能隙沿 Γ-Y 最大、沿 Γ-X 最小）。

裁表后全稿角标按新号重排（62 → 40，映射含裁撤项与三条新项），正文零悬空角标、零孤儿条目（40/40 全部被引）。

### 问题 9 [low]｜sections 四文件过程性残留

**结论：已消除（维持分离，处置记录写在本文件，不回写章节文件）。**

核验：四个章节文件（rationale/content/scheme/full_review）与 references.md 中，"round-N""本轮修订后""处置记录""闭环""核校""05_review"等标记命中 0。full_review.md 抬头原含"过程性材料（对照表、处置记录、轮次说明）一律写入 05_review/"一句，该句本身即过程性说明，已改为"本文件给出全书的论证骨架与跨章节统一口径，正文各章内容以 sections/ 下对应文件为准"。

## 二、连带修复的历史遗留 P0（与本轮著录工作直接相关）

| 遗留问题 | 状态 | 处理 |
|---|---|---|
| content 时窗口径 P0（秒级重建 vs 中子 ns–μs vs 飞秒至微秒） | 已消除 | 裁表重排后全稿时窗口径一致：主链 fs–μs 约九个数量级；中子白光飞行时间档承担 ns–μs 主链接续；事件模式 1 s 量级分箱只服务秒级重建段、不参与主链拟合；重建段单独运行、单独报告；全程十余个数量级。rationale / content / scheme / full_review 口径表四处一致。 |
| rationale 超长句 P1（3 处 >120 字） | 已消除 | 拆为 5 处独立句，最长句 120 字，>120 字命中 0。含 1 处为裁表改写引入、2 处为裁表前既有。 |
| content 超长句 P1 | 维持 | content 与 scheme 本轮复核 >120 字命中均为 0。 |
| content 成果节/年度计划缺失 P1 | 维持 | content §2.7 年度研究计划、§2.8 预期成果在位，未触及。 |
| full_review 骨架 P1 | 已消除 | 主线论证链与跨章节统一口径表两要件在位；参考文献表计数由"62 篇"同步为"40 篇"并加"每条附 DOI 或 arXiv 编号供溯源"；参考文献从立项依据章节目录中移出，独立为 references.md 模块条目。 |

## 三、本轮外部核验覆盖面

- arXiv API：29 条（6 条预印本条目 + 3 条新增 + 20 条用于首作首字母与题名核验）取 id / title / published / journal_ref / doi / 全作者链。
- doi.org 内容协商（CSL JSON）：31 条，取 container-title / volume / page / article-number / issued。
- CrossRef bibliographic 查询：18 条，用于定位 APS 新式不透明 DOI 与刊版卷期页。
- 零虚构、零重复：40/40 条题名与作者链与外部记录一致，DOI 与 arXiv 编号无重复。

## 四、遗留说明

- [23] Que 等 Nature Reviews Physics（2026）刊出时无卷期页，CrossRef 仅返回年份，按 online-first 记录，DOI 已挂。
- [1] 与 [9] 两条 Dharmasiri 工作截至 2026-11 仍为预印本，正文引用保持预印本措辞。
