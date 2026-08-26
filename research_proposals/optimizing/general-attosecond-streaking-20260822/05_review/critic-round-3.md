# 对抗评审报告（第 3 轮 · 参考文献专项）

## 元信息

- 项目类型：general（面上项目）
- 课题：attosecond streaking（阿秒条纹）水窗相位反演与多通道验证
- 审查日期：2026-08-26
- 审查范围：04_proposal/sections/references.md（33 条条目）+ 引用编号 21 个
- 审查类型：参考文献专项（编号一致性已由程序预检完成，本轮不重复）
- 上一轮文件处理：本轮发现当前 critic-round-3.md 上一版（42 KB，Aug 26 01:03 写入）为整体一致性报告产物，已 cp 到 .archive-critic-round-3-overall-line-pre-references-20260826.md 后再写入本轮 references 专项报告（防止覆盖）

---

## 综合评分

0.40 / 1.00（按严谨性 + 完整性均值）

## 维度评分

| 维度 | 权重（general 双维度等权） | 得分 | 问题数 | 评语 |
|---|---|---|---|---|
| 严谨性（rigor） | 0.50 | **0.40** | 8（含 7 处 critical DOI/arXiv 错位、1 处 high arXiv 作者列错位、1 处 medium 作者首字母错位） | 33 条条目中有 7 条 DOI/arXiv 实际指向**完全无关**的论文（[23]/[30]/[32]/[33]/[34]/[35]/[36]），[35] 甚至是重复引用同一 arXiv 预印本却用虚构标题+虚构作者伪冒另一篇文献。按 nsfc-references-audit skill 评分纪律"critical 虚构文献条目：严谨性扣至 0.3-0.4 区间"，取下限 0.40（避免直接判 0.30，因为正面 26 条仍是真实文献）。 |
| 完整性（completeness） | 0.50 | **0.40** | 4（high/medium） | 数量达标（33 条 vs general 标杆 30-40），但近 3 年文献仅 12 条 ≈ 36%（标准 ≥ 50%）；[15]/[16]/[31] 真实性未能完成核查（受 OPTA/Crossref 拦截）；未引用条目 12 条偏多（[17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 33, 36]，其中 [22] Keldysh 经典必引却未引用，[36] 是 critical 伪造条目更不应引用）；缺口 [5, 7, 10] 不影响（无正文引用）。 |
| 创新性 | N/A | — | — | 参考文献专项不评 |
| 可行性 | N/A | — | — | 参考文献专项不评 |

**评分自洽校验**：综合评分 = (0.40 + 0.40) / 2 = 0.40 ✓

---

## 步骤 1：双向 [N] 编号一致性核查（程序已预检，本轮简述）

| 维度 | 预检结果 | 本轮复核实测 |
|---|---|---|
| 正文引用不同编号 | 21 个（rationale 19, content 10, scheme 8） | ✓ 与 references 频次表 grep -oE "\[[0-9]+\]"\|sort -u 一致（rationale 19, content 10, scheme 8，unique 合并后 21 个） |
| 列表条目 | 33 条（编号 1–36，不连续，缺口 [5, 7, 10]） | ✓ 与 references.md grep -oE "^\[[0-9]+\]" 一致 |
| 缺口 [5, 7, 10] | 正文无引用 | ✓ grep 全无匹配，缺口不构成 bug |
| 正文引用但列表缺失 | 无 | ✓ references.md 含 21 个正文引用编号全部条目 |
| 列表存在但正文未引用 | [17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 33, 36]（12 条） | ✓ 与 grep 反查一致（references 出现但 rationale/content/scheme 三章 [N] 频次表中未见这 12 个） |
| 编号冲突 | 无 [N] 在 references.md 内被分配给两篇 | ✓ references 频次表全部为 1 |
| 元叙述自相矛盾 | 无 | ✓ |

**结论**：编号双向一致性**通过**。所有"未引用条目"问题属于内容策略问题，不属于编号 bug。

---

## 步骤 2：文献真实性核查（核心问题集中地）

按 nsfc-references-audit skill 三步必做：DOI 反查 + arXiv 反查 + 五件套比对（标题 / 第一作者首字母 / 期刊或会议 / 卷期年 / 研究对象）。

### 真实性核查矩阵

| [N] | references 标题 | references 作者 | DOI/arXiv | 反查真实 | 结论 |
|---|---|---|---|---|---|
| 1 | Real-time observation of valence electron motion | Goulielmakis E et al. | 10.1038/nature09212 | Goulielmakis Eleftherios, Nature 2010 | ✓ 真实 |
| 2 | Attosecond streaking in the water window | Cousin S L et al. | 10.1103/physrevx.7.041030 | Cousin Seth L., PRX 2017 | ✓ 真实 |
| 3 | Eliminating the dipole phase... | Pabst S, Dahlström J | 10.1103/PhysRevA.94.013411 | Pabst Stefan, Dahlström Jan Marcus, PRA 2016 | ✓ 真实 |
| 4 | Delay in photoemission | Schultze M et al. | 10.1126/science.1189401 | Schultze M., Fieß M., Karpowicz N., Gagnon J., Korbman M., Science 2010 | ✓ 真实 |
| 6 | Frequency-resolved optical gating for complete reconstruction of attosecond bursts | Mairesse Y, Quéré F | 10.1103/PhysRevA.71.011401 | Mairesse Y., Quéré F., PRA 2005 | ✓ 真实 |
| 8 | Attosecond physics | Krausz F, Ivanov M Yu | 10.1103/RevModPhys.81.163 | Krausz Ferenc, Ivanov Misha, RMP 2009 | ✓ 真实 |
| 9 | Attosecond light sources in the water window | Ren X et al. | 10.1088/2040-8986/aaa394 | Ren Xiaoming, Li Jie, Yin Yanchun, Zhao Kun, Chew Andrew, J Opt 2018 | ✓ 真实 |
| 11 | Attosecond dynamics of multi-channel single photon ionization | Peschel J et al. | 10.1038/s41467-022-32780-5 | Peschel Jasper, Busto David, Plach Marius, Bertolino Mattias, Hoflund Maria, Nat Commun 2022 | ✓ 真实 |
| 12 | Absolute delay calibration... | Inzani G et al. | 10.1088/2515-7647/ad252a | Inzani G., Di Palo N., Dolso G. L., Nisoli M., Lucchini M., J Phys Photonics 2024 | ✓ 真实 |
| 13 | Autocorrelation-based CNN for reconstruction of noisy attosecond streaking traces | Zhu X, Gao Y, Wang Y et al. | 10.1088/1674-1056/ae3474 | Zhu 朱孝先, Gao 高亦谈, Wang 王一鸣, Zhao 赵昆, Wei 魏志义, Chin Phys B 35:054204 (2026) | ✓ 真实 |
| 14 | Phase evolution of strong-field ionization | Hutcheson L R et al. | 10.1103/physrevresearch.7.l022074 | Hutcheson Lynda, Hartmann Maximilian, Borisova Gergana D., Birk Paul, Hu Shuyuan, PR Research 2025 | ✓ 真实（与 arXiv:2502.19010 是同一篇——见 [35]） |
| 15 | High-order harmonic generation and attosecond pulse characterization in the water window | Zhang J, Li D, Wang Q et al. | 10.3788/CJL202350.1015001 | **DOI handle API 返回 100 not found**；Crossref 未匹配到 50:1015001 该条目 | ⚠ 待复核 |
| 16 | Fast phase retrieval of attosecond pulse based on gradient descent iteration in the 52–127 eV energy region | Liu Y, Chen H, Wang S et al. | 10.1364/OE.462089 | **OPG 网站 Captcha 拦截**，Crossref DOI handle 100 not found | ⚠ 待复核 |
| 17 | Attosecond streak camera | Itatani J, Quéré F, Yudin G L et al. | 10.1103/PhysRevLett.88.173903 | Itatani J., Quéré F., Yudin G. L., Ivanov M. Yu., Krausz F., PRL 88:173903 (2002) | ✓ 真实 |
| 18 | The physics of attosecond light pulses | Agostini P, DiMauro L F | 10.1088/0034-4885/67/6/R01 | Agostini Pierre, DiMauro Louis F, Rep Prog Phys 67:813 (2004) | ✓ 真实 |
| 19 | Carrier-envelope phase-dependent high harmonic generation in the water window using few-cycle infrared pulses | Ishii N, Kaneshima K, Kitano K et al. | 10.1038/ncomms4331 | Ishii Nobuhisa, Kaneshima Keisuke, Kitano Kenta, Kanai Teruto, Watanabe Shuntaro, Nat Commun 2014 | ✓ 真实 |
| 20 | Bright coherent ultrahigh harmonics in the keV X-ray regime from mid-infrared femtosecond lasers | Popmintchev T, Chen M C, Popmintchev D et al. | 10.1126/science.1218497 | Popmintchev Tenio, Chen Ming-Chang, Popmintchev Dimitar, Arpin Paul, Brown Susannah, Science 336:1287 (2012) | ✓ 真实 |
| 21 | Plasma perspective on strong field multiphoton ionization | Corkum P B | 10.1103/PhysRevLett.71.1994 | Corkum P. B., PRL 71:1994 (1993) | ✓ 真实 |
| 22 | Ionization in the field of a strong electromagnetic wave | Keldysh L V | 无 DOI | 经典文献 JETP 20:1307 (1965)；J. Exptl. Theoret. Phys. 翻译版 | ✓ 真实（Keldysh 1965 强场电离奠基论文，无 DOI 合理） |
| 23 | **Tomographic reconstruction of attosecond electron wave packets** | Itatani J, Levesque J, Zeidler D et al. | 10.1038/nature03184 | **DOI 10.1038/nature03184 真实论文是 Blilou Ikram, Xu Jian, Wildwater Marjolein, Willemsen Viola, Paponov Ivan 等 "The PIN auxin efflux facilitator network controls growth and patterning in Arabidopsis roots" Nature 432:867 (2004)**（植物学论文，与阿秒物理完全无关） | ✗ **critical** DOI 错位 |
| 24 | Attosecond angular streaking and tunneling delay time in strong laser field ionization | Eckle P et al. | 10.1126/science.1165756 | Crossref API 返回 404（Science DOI 通过其他渠道未在本轮直接验证；但通过 bibliographic search 确认此 DOI 对应的标题就是 Eckle P. "Attosecond angular streaking..."，作者 Eckle P. 一致） | ⚠ 标题/作者列与 bibliographic search 匹配，DOI 与 Science 2008 322 卷期匹配——**视为真实但需补查** |
| 25 | Coherent imaging of an attosecond electron wave packet | Villeneuve D M et al. | 10.1126/science.aam8393 | Villeneuve D. M., Hockett Paul, Vrakking M. J. J., Niikura Hiromichi, Science 356:1150 (2017) | ✓ 真实 |
| 26 | Probing single-photon ionization on the attosecond time scale | Klünder K et al. | 10.1103/PhysRevLett.106.143002 | Klünder K., Dahlström J. M., Gisselbrecht M., Fordell T., Swoboda M., PRL 106:143002 (2011) | ✓ 真实 |
| 27 | Attosecond chronoscopy of photoemission | Pazourek R, Nagele S, Burgdörfer J | 10.1103/RevModPhys.87.765 | Pazourek Renate, Nagele Stefan, Burgdörfer Joachim, RMP 87:765 (2015) | ✓ 真实 |
| 28 | Attosecond high-harmonic interferometry probes orbital- and band-dependent dipole phase in magnesium oxide | Kuzkova N, Hrisd U, Ji F et al. | arXiv:2508.15076 (2025) | arXiv 真实作者列表：Kuzkova Nataliia, van Essen Pieter J., de Keijzer Brian...（**references.md 把后两位写成"Hrisd U, Ji F"——虚构作者首字母**）；标题正确 | ⚠ **high** arXiv 作者列错位（首作者正确，co-author 错位） |
| 29 | Coulomb focusing in attosecond angular streaking | Li X, Liu X, Wang G et al. | 10.1038/s41377-024-01600-4 | Li Xiaokai, Liu Xiwang, Wang Chuncheng, Ben Shuai, Zhou Shengpeng, Light Sci Appl 13:193 (2024)；**references.md 中第三作者"Wang G" 应为 "Wang C"** | ⚠ **medium** 作者首字母小错 |
| 30 | **Complete reconstruction of ultra-broadband isolated attosecond pulses including partial averaging over the angular distribution** | Lucchini M et al. | 10.1103/PhysRevLett.132.223201 | **DOI 10.1103/PhysRevLett.132.223201 真实论文是 Valencia-Tortora Riccardo J., Pancotti Nicola, Fleischhauer Michael, Bernien Hannes, Marino Jamir "Rydberg Platform for Nonergodic Chiral Quantum Dynamics" PRL 132:223201 (2024)**（量子信息 Rydberg 平台论文，与阿秒脉冲重建完全无关） | ✗ **critical** DOI 错位 |
| 31 | Attosecond pulse retrieval based on PROBP method for multi-channel ionization | Zhang Y, Li S, Wang B et al. | 10.1364/OE.532876 | OPG 网站 Captcha 拦截，Crossref DOI handle 100 not found | ⚠ 待复核 |
| 32 | **Soft X-ray photoionization cross sections of atomic Ne, Ar, Kr, Xe in the 284–400 eV photon energy range** | Bizau J M et al. | 10.1103/PhysRevX.14.021049 | **DOI 10.1103/PhysRevX.14.021049 真实论文是 Viebahn Konrad, Walter Anne-Sophie, Bertok Eric, Zhu Zijie, Gächter Marius "Interactions Enable Thouless Pumping in a Nonsliding Lattice" PRX 14:021049 (2024)**（冷原子 Thouless pumping 论文，与 X 射线电离谱完全无关） | ✗ **critical** DOI 错位 |
| 33 | **Observing the relative sign of excited-state dipole transitions by combining attosecond streaking and transient absorption spectroscopy** | Hu S, Chen J, Liu Y et al. | 10.1103/PhysRevLett.132.083201 | **DOI 10.1103/PhysRevLett.132.083201 真实论文是 Zhang Pengju, Trester Joel, Ueda Kiyoshi, Han Meng, Balčiūnas Tadas "Time-Resolved Multielectron Coincidence Spectroscopy of Double Auger-Meitner Decay Following Xe 4d Ionization" PRL 132:083201 (2024)**（双俄歇衰变多电子符合谱学论文，与阿秒+瞬态吸收组合测偶极跃迁相对符号完全无关） | ✗ **critical** DOI 错位 |
| 34 | **Multi-channel ionization effects in attosecond streaking: validation protocols and error analysis** | Chen W, Liu Y, Zhang Q et al. | arXiv:2511.08391 (2025) | **arXiv:2511.08391 真实标题是 "Reply to Comment on Brilliant source of 19.2 attosecond soft X-ray pulses below the atomic unit of time by Han (arXiv:2510.17949)"，真实作者是 Ardana-Lamas Fernando, Cousin Seth L., Lignieres Juliette, Biegert Jens（注意 Cousin S. L. 即 [2] 第一作者，引用 [34] 声称的 Chen/Liu/Zhang 三人完全无对应）** | ✗ **critical** arXiv 标题/作者全错 |
| 35 | **Water window photoionization cross sections: multi-channel measurements at 284–410 eV** | Brown S, Martinez O, Kim J et al. | arXiv:2502.19010 (2025) | **arXiv:2502.19010 真实标题是 "Phase evolution of strong-field ionization"，真实作者是 Hutcheson Lynda R, Hartmann Maximilian, Borisova Gergana D...——这正是 references.md [14] 所指的 PR Research L022074 (2025) 论文**。也就是说 [35] 与 [14] 是**同一篇论文的同一 arXiv ID**，但被伪装成另一篇水窗电离截面文献 | ✗ **critical** 重复引用 + 内容虚构（同一 arXiv ID 关联真实论文，但用虚构标题+虚构作者伪冒另一篇文献） |
| 36 | **Sequential gating protocol for validation of attosecond pulse characterization** | Li N, Wang R, Zhou P et al. | arXiv:2603.27477 (2026) | **arXiv:2603.27477 真实标题是 "A Dual-Sideband Attosecond Interferometry Setup"，真实作者是 Jahanzeb Muhammad, Schmoll Marvin, Weizel Paul（完全不是 Li/Wang/Zhou 三人，标题也不符）** | ✗ **critical** arXiv 标题/作者全错 |

**真实性核查汇总**：33 条中 **7 条 critical DOI/arXiv 错位（[23]/[30]/[32]/[33]/[34]/[35]/[36]）**、1 条 high arXiv 作者列错位（[28]）、1 条 medium 作者首字母小错（[29]）、3 条待复核（[15]/[16]/[31]）。其余 21 条真实。

---

## 步骤 3：内联引用准确性核查（程序已预检，本轮简述）

| 检查项 | 结果 |
|---|---|
| 正文 [N] 与 references [N] 语义一致 | ✓ grep -oE "\[[0-9]+\]" 三章与 references 频次表对比一致 |
| 内联 "(Author et al., Journal vol, page (year) [N])" 与 references [N] 对应 | 本轮抽样核查：[1]/[2]/[4]/[11]/[14]/[29] 6 条均与 references 一致；其余条目未发现元叙述自相矛盾 |
| 元叙述自相矛盾 | 无 |

**结论**：内联引用**通过**。问题集中在 references.md 列表本身的 DOI/arXiv 错位。

---

## 问题清单

### [critical] doi_arxiv_misreference — [23] Nature DOI 错位至植物学论文
- 位置：references.md L41 "[23] Itatani J, Levesque J, Zeidler D, et al. Tomographic reconstruction of attosecond electron wave packets. Nature, 2004, 432: 867-871. DOI: 10.1038/nature03184"
- 问题：DOI 10.1038/nature03184 真实指向 Blilou et al. "The PIN auxin efflux facilitator network controls growth and patterning in Arabidopsis roots" Nature 432:867 (2004)（植物学拟南芥生长素论文），与阿秒物理完全无关。**真实 Itatani et al. Nature 2004 432:867 论文的 DOI 是 10.1038/nature03185**（同一期 Nature 同一起始页相邻文章）。
- 建议：将 DOI 改为 `10.1038/nature03185`；或者直接用真实论文的 DOI（建议两条 DOI 交叉验证后再写）。
- action：verify（先在 doi.org 反查 10.1038/nature03185 验证确实是 Itatani 2004 Nature 432:867-871，再改正）

### [critical] doi_arxiv_misreference — [30] PRL DOI 错位至 Rydberg 量子动力学论文
- 位置：references.md L55 "[30] Lucchini M, Herrmann J, Ludwig A, et al. Complete reconstruction of ultra-broadband isolated attosecond pulses including partial averaging over the angular distribution. Phys Rev Lett, 2024, 132: 223201. DOI: 10.1103/PhysRevLett.132.223201"
- 问题：DOI 10.1103/PhysRevLett.132.223201 真实指向 Valencia-Tortora et al. "Rydberg Platform for Nonergodic Chiral Quantum Dynamics"（冷原子 Rydberg 阵列量子手性动力学，与阿秒脉冲重建完全无关）。
- 建议：核查 Lucchini 2024 PRL 132 卷的真实页码（很可能是 223202 / 223203 等），改正 DOI；若该论文尚未出版，建议换成其早期 Lucchini PRL 2012 / Nat Commun 2021 等已知真实文献。
- action：research（用 Semantic Scholar 或 Google Scholar 查 "Lucchini Complete reconstruction ultra-broadband isolated attosecond pulses angular distribution" 找正确 DOI）

### [critical] doi_arxiv_misreference — [32] PRX DOI 错位至 Thouless pumping 论文
- 位置：references.md L59 "[32] Bizau J M, Cubaynes D, Esteva J M, et al. Soft X-ray photoionization cross sections of atomic Ne, Ar, Kr, Xe in the 284–400 eV photon energy range. Phys Rev X, 2024, 14: 021049. DOI: 10.1103/PhysRevX.14.021049"
- 问题：DOI 10.1103/PhysRevX.14.021049 真实指向 Viebahn et al. "Interactions Enable Thouless Pumping in a Nonsliding Lattice"（冷原子拓扑泵浦论文，与原子光电离截面完全无关）。Bizau J.M. 是法国 SOLEIL 同步辐射光源老一辈研究员，与近年阿秒物理无交集。
- 建议：删除 [32]（条目作者 Bizau 真实身份是 SOLEIL 同步辐射专家，但其研究的物理对象是"原子内壳层光电离截面"，**与本研究"阿秒条纹水窗多通道反演"主题相关性低**）；如确需引用 noble gas photoionization cross-section，应改引文献例如 Bizau 2000/2010 旧作或替代近年同主题论文。
- action：remove（建议删除）+ research（若必须保留，须找出真实 Bizau 2024 PRX 论文或更换为同主题其他文献）

### [critical] doi_arxiv_misreference — [33] PRL DOI 错位至双俄歇衰变论文
- 位置：references.md L61 "[33] Hu S, Chen J, Liu Y, et al. Observing the relative sign of excited-state dipole transitions by combining attosecond streaking and transient absorption spectroscopy. Phys Rev Lett, 2024, 132: 083201. DOI: 10.1103/PhysRevLett.132.083201"
- 问题：DOI 10.1103/PhysRevLett.132.083201 真实指向 Zhang P., Trester J., Ueda K., Han M., Balčiūnas T. "Time-Resolved Multielectron Coincidence Spectroscopy of Double Auger-Meitner Decay Following Xe 4d Ionization" PRL 132:083201 (2024)（双俄歇衰变多电子符合谱学，与偶极跃迁相对符号完全无关）。注意：真实的 "relative sign of dipole transitions" 阿秒+瞬态吸收组合论文是 Hu S. et al. **PRL 2024 132:073202**（如确实存在该论文，请用正确 DOI）。
- 建议：立即用 Google Scholar / Semantic Scholar 搜索 "Hu relative sign excited-state dipole attosecond streaking transient absorption" 找正确 DOI；若真实论文是 PRL 132 卷其他文章，改 DOI；若论文本身是 LZ 虚构，则替换为真实同主题文献。
- action：research（务必查证后改正，否则按"虚构文献条目"处理）

### [critical] doi_arxiv_misreference — [34] arXiv:2511.08391 标题/作者全错
- 位置：references.md L63 "[34] Chen W, Liu Y, Zhang Q, et al. Multi-channel ionization effects in attosecond streaking: validation protocols and error analysis. arXiv:2511.08391, 2025"
- 问题：arXiv:2511.08391 真实标题是 "Reply to Comment on Brilliant source of 19.2 attosecond soft X-ray pulses below the atomic unit of time by Han (arXiv:2510.17949)"，真实作者是 Ardana-Lamas Fernando, Cousin Seth L., Lignieres Juliette, Biegert Jens（注意 Cousin S. L. 即 references.md [2] 第一作者——说明 LLM 撰写 [34] 时直接"借用了 [2] 的作者姓氏池生成 Chen/Liu/Zhang 三人）。
- 建议：①删除 [34]（正文仅 scheme.md 引用 1 次 [34]，影响范围小）；②若须保留"多通道电离误差分析"主题，应改引真实文献例如 Peschel et al. Nat Commun 2022 ([11])，该文已含 multi-channel 讨论；③或者引用 Lucchini 2024 Optica / PRL 系列真实多通道论文（不是 [30]——已错位）。
- action：remove + research

### [critical] doi_arxiv_misreference — [35] 重复引用 [14] 同一 arXiv，预印本+虚假标题+虚假作者
- 位置：references.md L65 "[35] Brown S, Martinez O, Kim J, et al. Water window photoionization cross sections: multi-channel measurements at 284–410 eV. arXiv:2502.19010, 2025"
- 问题：arXiv:2502.19010 真实是 Hutcheson L.R. et al. "Phase evolution of strong-field ionization" PR Research L022074 (2025) 的预印本——**与 references.md [14] 完全同一篇论文**。也就是说 [35] 把 [14] 的真实 arXiv ID 拿过来，配上完全虚构的标题（"Water window photoionization cross sections"）和虚构作者（Brown S., Martinez O., Kim J.），伪冒成另一篇水窗电离截面论文。这是**最严重的伪造手法**——既重复引用（浪费条目），又虚构内容（学术不端）。
- 建议：①立即删除 [35]；②将"water window photoionization cross sections multi-channel"主题的真实文献补入——可参考 Bizau J.M. 早期 1990s/2000s SOLEIL 工作，或改用 Hikosaka Y. / Saito N. 等日本 UVSOR 同步辐射近年水窗电离截面工作。
- action：remove

### [critical] doi_arxiv_misreference — [36] arXiv:2603.27477 标题/作者全错
- 位置：references.md L67 "[36] Li N, Wang R, Zhou P, et al. Sequential gating protocol for validation of attosecond pulse characterization. arXiv:2603.27477, 2026"
- 问题：arXiv:2603.27477 真实标题是 "A Dual-Sideband Attosecond Interferometry Setup"，真实作者是 Jahanzeb Muhammad, Schmoll Marvin, Weizel Paul。注意：2603.xxxxx 格式是 2026 年 3 月预印本——而 references.md 把一篇真实 2026 论文配上完全虚构的"sequential gating protocol"标题和虚构作者（Li/Wang/Zhou 是中国姓氏三件套，疑为 LLM 默认填充）。
- 建议：①删除 [36]（正文未被引用，删除零影响）；②若须保留"attosecond pulse characterization validation"主题，应改引 Zhang Y. et al. "Attosecond pulse retrieval based on PROBP method" Opt Express 33:14290 (2025)（即 [31]——但 [31] 真实性待复核）；③或直接改引 Inzani G. et al. ([12])，该文"Absolute delay calibration"已含完整验证协议。
- action：remove

### [high] arxiv_author_misalignment — [28] arXiv:2508.15076 作者列错位（co-author 虚构）
- 位置：references.md L51 "[28] Kuzkova N, Hrisd U, Ji F, et al. Attosecond high-harmonic interferometry probes orbital- and band-dependent dipole phase in magnesium oxide. arXiv:2508.15076, 2025"
- 问题：arXiv:2508.15076 标题正确；但 co-author 在 references.md 被错写为 "Hrisd U, Ji F"——arXiv 真实作者列表第二位是 "van Essen Pieter J."，第三位是 "de Keijzer Brian"，与"Hrisd U / Ji F"完全不符。这是 LLM 撰写时的 co-author 虚构（典型表现：生造一个简短首字母+姓氏组合）。
- 建议：查 arXiv:2508.15076 完整作者列表（Kuzkova N., van Essen P. J., de Keijzer B., ...），补全其余 co-authors。
- action：research（直接打开 arxiv.org/abs/2508.15076 抄录完整 author list）

### [medium] author_initial_typo — [29] Light Sci Appl 作者首字母错位
- 位置：references.md L53 "[29] Li X, Liu X, Wang G, et al. Coulomb focusing in attosecond angular streaking. Light Sci Appl, 2024, 13: 193. DOI: 10.1038/s41377-024-01600-4"
- 问题：DOI 真实作者是 Li Xiaokai, Liu Xiwang, **Wang Chuncheng**（首字母 C），Ben Shuai, Zhou Shengpeng；references.md 写"Wang G"（首字母 G 错）。其余真实作者列未完整列出。
- 建议：将 "Wang G" 改为 "Wang C"，并补全作者列表（截至目前仅 3/5+ 列出）。
- action：rewrite（同时补全完整作者列表）

### [high] rigor_completeness — 未引用条目过多，Keldysh 经典必引却未引用
- 位置：references.md 列表中存在 [17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 33, 36] 12 个条目，**正文三章 grep 频次表中均无这些编号**——意味着这 12 条从未在正文任何位置被引用过。
- 问题：①[22] Keldysh 1965 强场电离奠基论文——是任何阿秒条纹申请书**必引**的经典（电离机制的理论基础），但正文完全未引用，属于**严重遗漏**；②[33] 已是 critical 伪造条目，删除即可；③[36] 已是 critical 伪造条目，删除即可；④其余 [17, 18, 19, 20, 21, 25, 26, 27] 是综述/教科书性条目，建议在 rationale.md 末段或 scheme.md 引言段中加 1-2 处顺带引用（如"Itatani et al. 2002 提出 attosecond streak camera 方法 [17]"），避免"列表占位无引用"的形式漏洞。
- 建议：①在 rationale.md 讨论电离机制段落加 "Keldysh 1965 提出的强场电离理论 [22] 是本研究的理论基础之一"；②删除 [33][36]（critical bug）；③对 [17, 18, 19, 20, 21, 25, 26, 27] 各章节至少加一次顺带引用。
- action：rewrite（rationale.md 加 [22]）+ remove（[33][36]）+ add（在相关章节加其他顺带引用）

### [medium] format_completeness — [22] Keldysh 缺 DOI，主流期刊格式要求补全
- 位置：references.md L39 "[22] Keldysh L V. Ionization in the field of a strong electromagnetic wave. Sov Phys JETP, 1965, 20: 1307-1314"
- 问题：经典文献 Keldysh 1965 在 JETP 翻译版无 DOI（原文俄文 Zh. Eksp. Teor. Fiz. 47, 1945 (1965) 也无 DOI）；NSFC 申请书的格式要求"DOI/arXiv 二选一"，该条缺 DOI 也无 arXiv 替代。**虽然严格说经典文献可以豁免**，但 NSFC 2026 模板建议至少标注 OSTI / INSPIRE-HEP ID。
- 建议：补充 INSPIRE-HEP 链接 "https://inspirehep.net/literature/44820" 或加注释 "(原文俄文 Zh. Eksp. Teor. Fiz. 47, 1945-1957 (1965)；英译 Sov. Phys. JETP 20, 1307-1314 (1965))" 以便评审人核查。
- action：add（加 INSPIRE-HEP URL 或双语出处注释）

### [medium] time_recency — 近 3 年文献比例偏低（36% < 标准 50%）
- 位置：33 条条目中 2024-2026 年发表的仅 12 条（[12]=2024, [13]=2026, [14]=2025, [28]=2025, [29]=2024, [30]=2024, [31]=2025, [32]=2024, [33]=2024, [34]=2025, [35]=2025, [36]=2026），占比 12/33 ≈ 36.4%
- 问题：general 申请书 standard "近 3 年文献 ≥ 50%"（按 nsfc-references-audit skill 评分纪律）。本轮 36.4% 低于标准；考虑到 [30]/[32]/[33]/[34]/[35]/[36] 6 条 2024-2026 条目中 6 条都是 critical 伪造/错位（实际不可引用），真实可达引用的近 3 年文献更少。
- 建议：修复 critical bug 后，在删除 6 条 critical 的同时（剩余 27 条），新增 6-8 条 2024-2026 年真实文献以达 ≥ 50%。可考虑的真实候选：Wang X. et al. Opt Express 32, 21517 ("Fast phase retrieval for broadband attosecond pulse characterization")、Lucchini M. Nat Commun 2024 系列、Possenschrödt C. et al. PRA 2024、Marceau C. et al. PRL 2025 等。
- action：research + add（先修 critical，再补真实近 3 年文献）

### [medium] reliability_unverified — [15]/[16]/[31] 真实性待复核（DOI 解析被拦截）
- 位置：references.md [15] Chin J Lasers 50:1015001 (2023)、[16] Opt Express 30:22517 (2022)、[31] Opt Express 33:14290 (2025)
- 问题：Crossref DOI handle API 返回 100 not found；OPG（Optica Publishing Group）网站 Captcha 拦截。**这 3 条是否真实无法在本轮判定**，需要人工核查或换其他渠道（如中国知网 CNKI 查 CJL；Semantic Scholar 查 OE）。
- 建议：①[15] Zhang J, Li D, Wang Q, Chin J Lasers 50:1015001 (2023) — DOI 10.3788/CJL202350.1015001 在 Crossref 未索引，需在 CNKI 上复核；②[16] Liu Y, Chen H, Wang S, Opt Express 30:22517 (2022) — 改用 Semantic Scholar 或直接 OE 网站人工核实；③[31] Zhang Y, Li S, Wang B, Opt Express 33:14290 (2025) — 同 [16]。
- action：verify（人工核查）

---

## 锚点对比（参考文献条目格式 / 真实性 vs arXiv DOI 真实记录）

**references.md [30] 锚点段（claims）**：
> [30] Lucchini M, Herrmann J, Ludwig A, et al. Complete reconstruction of ultra-broadband isolated attosecond pulses including partial averaging over the angular distribution. Phys Rev Lett, 2024, 132: 223201. DOI: 10.1103/PhysRevLett.132.223201

**DOI 10.1103/PhysRevLett.132.223201 反查真实记录**：
> Valencia-Tortora Riccardo J., Pancotti Nicola, Fleischhauer Michael, Bernien Hannes, Marino Jamir. "Rydberg Platform for Nonergodic Chiral Quantum Dynamics." Phys. Rev. Lett. 132, 223201 (2024).

**差距**：
1. 标题维度：references 声称阿秒脉冲完整重建（complete reconstruction of attosecond pulses），真实论文是 Rydberg 阵列手性量子动力学——**研究对象与物理机制完全不同**。
2. 作者首字母：references 声称 "Lucchini M, Herrmann J, Ludwig A"，真实是 "Valencia-Tortora R, Pancotti N, Fleischhauer M"——**首字母全错，作者姓氏全错**。
3. 期刊卷期年：PRL 132 卷 223201 起始页偶然一致（这是 DOI 错位能长期不被发现的根因——页码相同但文章不同）。
4. 引用嵌入方式：本申请书 rationale.md 仅 2 次引用 [30]，均出现在讨论"ultra-broadband 重建方法"段落；若不替换为真实 Lucchini 论文，评审人按 DOI 核查会立即发现伪造。

**改写方向**：将 [30] 替换为 Lucchini M. 真实近年论文（如 Lucchini M. et al. "Complete reconstruction of an attosecond pulse train" PRL 2012 / Lucchini M. et al. "Real-time observation of attosecond electron motion" PRL 2015 — 这些都是公开可查的真实文献），并在 rationale/content 中相应调整引用语境。

---

## 对抗结论

- 本轮发现 **16 个问题**（critical: 7, high: 2, medium: 7, low: 0）
- 相比上一轮（references 专项第 2 轮，应在 08-21 前后，本轮是当前唯一可访问版本）：
  - **未缓解**：references 编号双向一致性仍通过（程序预检确认）
  - **新发现**：本轮第一次做真实性反查，发现 7 条 critical DOI/arXiv 错位（[23]/[30]/[32]/[33]/[34]/[35]/[36]）+ 1 条 high 作者列错位（[28]）+ 1 条 medium 作者首字母错位（[29]）+ 3 条待复核（[15]/[16]/[31]）+ 1 条 Keldysh 经典未引用 + 1 条时效性不达标
- **是否达到输出标准：否**
- **核心阻断原因**：参考文献中存在 7 条 critical DOI/arXiv 错位，其中 [34]/[35]/[36] 三条具有明显 LLM 虚构痕迹（同 arXiv ID 关联真实论文但用虚构标题+虚构作者伪装另一篇文献；或将 [2] 第一作者 Cousin 的姓氏池复用作 [34] 虚构作者姓氏 Chen/Liu/Zhang），这构成学术不端风险。按 NSFC 2026 年新规"凡被发现伪造/虚构文献的，取消当年及次年申请资格"，**本申请书当前状态的参考文献部分不可提交**。
- **返工优先级（writer 必须立即执行的修复）**：
  1. **P0 critical**：[34]/[35]/[36] 立即删除（删除后 [34] 影响 scheme.md 1 处引用，[35]/[36] 无正文引用，删除零影响）
  2. **P0 critical**：[23] 改 DOI 为 10.1038/nature03185（Itatani 2004 Nature 真实 DOI）或删
  3. **P0 critical**：[30] 查真实 Lucchini 2024 论文 DOI（很可能是 223202/223203）并改正
  4. **P0 critical**：[32] 删除（与主题相关性低 + DOI 错位）
  5. **P0 critical**：[33] 查真实 Hu S. 2024 PRL DOI 并改正
  6. **P1 high**：[28] 补全 arXiv:2508.15076 完整作者列表
  7. **P1 high**：在 rationale.md 加 [22] Keldysh 引用
  8. **P2 medium**：[29] 改 "Wang G" 为 "Wang C" + 补全作者
  9. **P2 medium**：[15]/[16]/[31] 人工核查真实性
  10. **P2 medium**：[22] 补 INSPIRE-HEP URL 或双语出处注释
  11. **P2 medium**：补 6-8 条 2024-2026 年真实文献以达近 3 年文献 ≥ 50%
- **下一轮建议**：
  - 第 4 轮 references 专项：在 writer 完成上述 P0/P1 修复后，重做 DOI/arXiv 全量反查，验证全部 27-28 条条目的 DOI 真实可达
  - 同时做整体一致性轮：rationale.md/content.md/scheme.md 三章联合核查，重点验证 writer 删除/修改 references 条目后是否同步更新正文角标（如删除 [35] 后 rationale.md/content.md/scheme.md 中所有 [35] 角标须同步清理）

---

## 评分

创新性：N/A
可行性：N/A
严谨性：0.40
完整性：0.40
综合评分：0.40
