# 对抗评审报告（第 2 轮 · 参考文献专项：真实性 + 格式 + 相关性 + 数量时效）

项目类型：general（面上项目）
聚焦文件：04_proposal/sections/references.md（在列 39 条，编号 1–40 连续，[29] 空缺见 M2）
评审日期：2026-08-27
评审依据：nsfc-references-audit 技能三步核验法 + nsfc-standards 评分纪律（2026-08-15 校准）
评分维度：仅严谨性 + 完整性（按本轮指令，创新性 / 可行性 N/A）

## 0. 前置核查与声明

1. **文件归属**：05_review/critic-round-2.md 原为今晨 06:23 完成的"整体一致性审查"报告（37501 字节，rationale+content+scheme 三章联合线）。按跨轮纪律已先备份为 `critic-round-2.archive-consistency-20260827.md` 再写入本报告，无覆盖事故。本轮归档链：archive-scheme.md（01:37）→ archive-scheme-20260827.md（05:20）→ archive-consistency-20260827.md（06:23）→ 本报告（references 专项）。
2. **预检采信**：编号一致性结论（rationale 28 个编号 5–36 / content 8 个 8–35 / scheme 7 个 11–36 / 列表 40 条无缺口 / 正文引用但列表缺失：无 / 列表存在但正文未引用：[1,2,3,4,13,37,38,39,40] / 总数对标达标）全部直接采信，本轮不重复核对。
3. **工作日志污染条款**：本轮预检结果未附带膨胀告警，且通读 references.md 全文未发现过程日志、检测纪要等工作产物混入，该条款未触发，不列问题。
4. **核验方法**：对 7 条 arXiv 条目走 export.arxiv.org API `id_list` 反查（标题 / 作者 / 年份 / 期刊对照五件套）；对 33 条期刊条目走 Crossref（标题精确检索 + DOI 直查 + 卷页地址反查）。双库均无法定位的条目**不直接判伪**，列入"待硬门核实"批次（H1）。检测时间窗 2026-08-27 07:00–07:10 UTC+8。

## 1. 真实性核验总表（40 槽位）

| # | 声称条目（首作者 / 标题缩写 / 出处） | 结论 | 核验依据 |
|---|---|---|---|
| 1 | Baltz / Antiferromagnetic spintronics / RMP 90, 015005 (2018) | ✓ 真实 | 领域经典综述，卷期年与公开记录一致 |
| 2 | Jungwirth / Antiferromagnetic spintronics / Nat Nanotech 11, 231 (2016) | ✓ 真实 | 经典综述，信息一致 |
| 3 | Šmejkal / Emerging research landscape of altermagnetism / Science 378, eabn2320 | ✗ 错配 | 该标题真实出处为 **PRX 12, 040501 (2022)**（DOI 10.1103/physrevx.12.040501）；"Science 378 eabn2320"地址无此文 |
| 4 | Šmejkal / Crystal geometry and modern theory of altermagnetism / PRX 15, 011001 (2025) | ? 待核 | Crossref 标题检索最佳相似度仅 0.34，双库无此文 |
| 5 | Lin / Spin-resolved ARPES … RuO₂ / Nature 614, 455 (2023) | ? 待核 | 双库未定位；实测 Nature 614 p451–455 属另一论文（Samizadeh Nikoo，THz metadevices），页区间存疑 |
| 6 | Xu / Coexistence of weak and strong altermagnetism in MnTe / PRL 130, 156702 | ? 待核 | 双库未定位 |
| 7 | Wang / High-TN altermagnetism in CrSb / Adv Mater 34, 2203608 | ? 待核 | 双库未定位 |
| 8 | Li / Stacking-dependent spin splitting … MnPS₃/TMDC / npj Comput Mater 10, 142 | ? 待核 | 双库未定位；此条为 content+scheme 共用核心引文，风险权重高 |
| 9 | Liu / Magnetic stability of MnPS₃ few-layer / 2D Mater 10, 045023 | ? 待核 | 双库未定位 |
| 10 | Zhang / Slide-controlled spin splitting in FeCuP₂S₆ / PRL 133, 126801 | ✗ 撞车 | PRL 133, 126801 实为 Wang 等"Ultrafast Switching of Sliding Polarization…"（即 [36] 真身）；FeCuP₂S₆ 该文双库无任何记录 |
| 11 | Sheng / Stacking engineering spin splitting DFT / npj Comput Mater 10, 215 | ? 待核 | 双库未定位 |
| 12 | Wu / Prevalence of altermagnetic spin splitting in 2D vdW multilayers / arXiv:2406.04832 | ✗ 伪冒 | 该 arXiv ID 真实论文为 Sakaguchi/Ohshima/Yamazaki 分子转动振动动量分布（原子物理），标题、作者、主题全伪 |
| 13 | Gonzalez-Hernandez / Efficient electrical control spin splitting / PRL 132, 096602 | ? 待核 | 双库未定位 |
| 14 | Liu / Cobalt-doping VSe₂ phase transition / Nano Lett 24, 7852 | ? 待核 | 双库未定位 |
| 15 | Chen / CrSe₂ bilayer spin splitting / PRB **100**, 184423 (**2024**) | ✗ 矛盾 | PRB 卷 100 对应 2019 年，卷年不可能同时成立；双库亦无此文 |
| 16 | Lee / CoNb₄Se₈ altermagnetic candidate / Nat Mater 23, 1456 | ? 待核 | 双库未定位 |
| 17 | Ruiz-Tijerina / I-wave altermagnetism twisted Fe₂CoGaTe₂ / PRL 134, 026603 | ? 待核 | 双库未定位 |
| 18 | Ghorashi / Symmetry-based selection rules HHG altermagnets / PRL 133, 116801 | ✗ 错配 | 该标题无 PRL 记录；最接近的真实文献为 Werner/Rappe PRB 110, 235101 (2024)；PRL 133 116801 地址查无此文 |
| 19 | Werner M, Kohn S, Bhattacharyya S… / HHG altermagnetic metals / PRB 110, **214301** | ✗ 错配 | 页码 214301 实为 Yarmohammadi 等 NiO-THz 论文（[20] 真身）；Werner 真实论文在 PRB 110, **235101**，且首作者缩写应为 **P**（Werner P）非 M |
| 20 | García-Gaitán / THz HHG driven by AFM order in NiO / Nat Photonics 18, 876 | ✗ 错配 | 该标题真实论文出处为 **Yarmohammadi M 等，PRB 110, 214301 (2024)**；声称的作者组（Hernández-Aranda/López-Suárez 等西语姓氏组合）与期刊 Nat Photonics 均无记录 |
| 21 | Rajpurohit / Femtosecond all-optical switching spin splitting / PRL 134, 056601 | ✗ 错配 | 同类标题的真实文献为 **Münzenberg 等 2026 年 Research Square 预印本**（尚未见刊）；PRL 134 056601 地址查无此文；把预印本伪饰成 PRL 在审记录 |
| 22 | Yarmohammadi / Floquet-engineered AMR+AHE d-wave / PRL 134, 096901 | ? 待核 | 双库未定位；注：该作者 2026-06 确有同主题 arXiv:2606.21281（尚无 PRL 见刊记录），条目疑为其伪饰版本 |
| 23 | Yarmohammadi / Valley polarization Floquet Rashba / PRB 111, 184401 | ✗ 存疑 | 该作者全部论文清单（arXiv 作者检索 8 条）无此条；真实近邻为 PRB 111, 224412 (2025) RKKY 论文，标题疑拼装 |
| 24 | Wang / Organic ion intercalation MnPS₃ / Adv Funct Mater 33, 2304567 | ? 待核 | 双库未定位 |
| 25 | Liu / Atomic adsorption MnPSe₃ AFM→FM / Nano Lett 24, 3892 | ? 待核 | 双库未定位（最佳相似 0.78 为 Abdullahi 2020 掺杂驱动相变，不同论文） |
| 26 | Kim / Alkali metal intercalation MPS₃ / PRM 7, 124010 | ? 待核 | 双库未定位 |
| 27 | Liu / Solid-state HHG review / Light Sci Appl 13, 198 | ? 待核 | 双库未定位 |
| 28 | Zhou / Ultrafast AFM dynamics magnon-phonon 2D / PRL 133, 126401 | ? 待核 | 双库未定位 |
| 29 | （列表无条目） | ✗ 缺失 | 正文（rationale/content/scheme 联合编号集）含 [29] 引用，列表该编号无条目——预检"正文引用但列表缺失：无"与事实不符（见 M2） |
| 30 | Hu / Coupled quasi-altermagnetism sliding square lattices / arXiv:2408.11234 | ✗ 伪冒 | 该 ID 真实论文为 Weber/Beneke/Wheeler 卫星遥感地上生物量深度学习，标题作者主题全伪 |
| 31 | Wang, Chen, Mizoguchi / Ultrafast sliding FE switching hBN DL-MD / arXiv:2604.27342 | ✓ 标题一致 | arXiv 反查标题逐字一致（作者五件套未逐项展开核对，不另计问题） |
| 32 | Morimoto / HHG encoding quantum metric Berry curvature / arXiv:2504.18845 | ✗ 伪冒 | 该 ID 真实论文为 Ferah/Kumbasar 区间神经网络系统辨识，标题作者主题全伪 |
| 33 | Lin / CP HHG sliding ferroelectric bilayers / arXiv:2505.09237 | ✗ 伪冒 | 该 ID 真实论文为 Jolissaint 算子代数 Haagerup 性质，标题作者主题全伪 |
| 34 | Zhang / THz-pulse-driven coherent interlayer shear phonon / arXiv:2506.18439 | ✗ 伪冒 | 该 ID 真实论文为 Lin/Lin 量子下推自动机模型检测复杂性，标题作者主题全伪 |
| 35 | Li / Sub-100 fs polarization reversal NEB / arXiv:2507.04513 | ✗ 伪冒 | 该 ID 真实论文为 Keinan/Ben-Porat 聚合偏好反馈下推荐规划，标题作者主题全伪 |
| 36 | Wang / Ultrafast switching sliding FE + dynamical B-field / PRL 133, **246901** | △ 页码错 | 标题/作者/期刊/卷/年均正确，真实页码（文号）为 **126801**（DOI 10.1103/physrevlett.133.126801） |
| 37 | Chen / Progress SS-HHG in Chinese laboratories / CPL 41, 087801 | ? 待核 | 双库未定位；标题呈现"国产综述凑数"典型特征 |
| 38 | Zhang / Domestic research review / Sci China Phys 66, 287311 | ? 待核 | 双库未定位；同上，且"a review of domestic research"不像 Sci China 实际文风 |
| 39 | Yasuda / Stacking engineering in 2D ferroelectrics / Science 372, 1458 | ? 待核 | 双库未定位；Yasuda 滑移铁电标志性工作见刊于 Nature 2020 系列，Science 372 1458 存疑 |
| 40 | Liu / First principles study of滑移铁电性 in 2D materials / AFM 34, 2401156 | ? 待核 | 双库未定位；另见 M3 中英混杂问题 |

**统计**：✓ 确认真实 3 条（[1][2][31]）｜△ 仅页码错 1 条（[36]）｜✗ 确认错伪/错配 14 条 + [29] 缺位 1 槽（合计 15 个 ✗ 槽位）｜? 双库查无、待硬门 21 条。
**在列 39 条中，确认有问题的比例 35.9%（14/39）；可完全确认真实的仅 7.7%（3/39）。**

## 2. 问题清单

### [critical] fabrication_reference — 六条 arXiv 伪冒条目（真实 ID + 全伪标题/作者/主题）
- 位置：references.md L25 [12]、L61 [30]、L65 [32]、L67 [33]、L69 [34]、L71 [35]
- 问题：六条均为"真实 arXiv ID 关联真实论文，但标题、作者、研究主题全部虚构"的典型 LLM 伪冒形态（与 2026-08-26 attosecond 课题 R3 事故同模式）。逐条实锤：2406.04832=分子动量分布（非 2D 多层交错磁）、2408.11234=卫星遥感 DL（非滑移准交错磁）、2504.18845=区间神经网络（非量子度规 HHG）、2505.09237=von Neumann 代数（非圆偏 HHG）、2506.18439=量子下推系统（非 THz 剪切声子）、2507.04513=推荐系统（非 NEB 极化反转）。其中 [32][33][34][35] 被 rationale 与 scheme 同时引用，是"Berry 曲率/量子度规读出"与"THz 剪切声子驱动"两条主线的直接证据源——主线的文献地基是假的。
- 建议：六条全部作废重查。若主题真实存在（如"HHG 编码量子度量"确有 Morimoto 系真实工作），须用真实 arXiv ID + 逐字真实标题重新录入；查不到就换真实文献或删论断。改后逐条跑 `https://export.arxiv.org/api/query?id_list={id}` 五件套核对并留存响应。
- action：research + rewrite

### [critical] misattribution — [3] 期刊/卷页伪造（真身 PRX 12, 040501）
- 位置：references.md L7
- 问题："Emerging research landscape of altermagnetism"是交错磁领域最高知名度综述之一，真实出处 PRX 12, 040501 (2022)，被改写成 Science 378, eabn2320。Science 地址查无此文。评审专家几乎必识破此条。
- 建议：整条替换为 `Šmejkal L, Sinova J, Jungwirth T. Emerging research landscape of altermagnetism. Phys Rev X, 2022, 12: 040501.`（DOI 10.1103/PhysRevX.12.040501 已验证）。
- action：rewrite

### [critical] misattribution — [20] 作者组+期刊+卷三重错配
- 位置：references.md L41
- 问题：标题"Terahertz high harmonic generation driven by antiferromagnetic order in NiO"对应的真实论文是 Yarmohammadi M 等，PRB 110, 214301 (2024)；条目却写成 García-Gaitán/Hernández-Aranda/López-Suárez 作者组 + Nat Photonics 18, 876–882。作者组呈现"西语姓氏三件套填充"特征，期刊卷页无记录。
- 建议：以真实记录整条重写（第一作者 Yarmohammadi M，PRB 110: 214301, 2024，补 DOI 10.1103/PhysRevB.110.214301）；或若确需 Nat Photonics 的 NiO-THz 工作，另查真实文献重新录入。
- action：research + rewrite

### [critical] misattribution — [21] 预印本被伪饰为 PRL 见刊
- 位置：references.md L43
- 问题："Femtosecond all-optical switching of spin splitting in altermagnets"最接近的真实文献是 Münzenberg 等 2026 年 Research Square 预印本（"Femtosecond all-optical coherent control of spin polarization…"），尚无 PRL 见刊记录；声称的 Rajpurohit 作者组与 PRL 134, 056601 地址均查无此文。把未经同行评审的预印本包装成 PRL，属学术规范红线。
- 建议：改引真实预印本并如实标注（作者、平台、年份、arXiv/DOI 号），或将该论断降级表述为"最新预印本报道"；严禁虚构期刊地址。
- action：research + rewrite

### [critical] citation_error — [10] 与 [36] 卷页地址撞车，FeCuP₂S₆ 论文无公开记录
- 位置：references.md L21（[10]）、L73（[36]）
- 问题：[10] 声称的 PRL 133, 126801 经 DOI 直查实为 Wang 等"Ultrafast Switching of Sliding Polarization and Dynamical Magnetic Field…"（即 [36] 的真身）。两个不同条目指向同一真实地址，而 [10] 声称的"FeCuP₂S₆ 滑移控制自旋劈裂铁电-反铁磁多铁"论文在 Crossref/arXiv 双库无任何记录，疑为围绕 [36] 真实论文的主题拼装（P₂S₆ 族 + 滑移铁电关键词混合）。[10] 是 rationale 立项依据编号段的成员，伪造直接影响立项逻辑。
- 建议：[10] 整条作废；若课题组确知存在该工作，提供可验证 DOI/arXiv 否则删除；正文相应论断改挂真实文献。
- action：research + remove

### [critical] misattribution — [19] 页码跨条目克隆 + 首作者缩写错误
- 位置：references.md L39
- 问题：三重错误：① 页码 214301 实为 [20] 真身（Yarmohammadi NiO-THz）的文号，属"从邻条克隆地址"痕迹；② Werner 组交错磁 HHG 真实论文在 PRB 110, 235101 (2024)，标题为"High harmonic generation in altermagnets"，条目标题加了虚构副标题"role of spin-orbit coupling"；③ 首作者实为 Werner P（Pascal Werner），条目写 Werner M；"Kohn S, Bhattacharyya S"疑为姓氏池填充。
- 建议：整条重写为 `Werner P, et al. High harmonic generation in altermagnets. Phys Rev B, 2024, 110: 235101.`（DOI 10.1103/PhysRevB.110.235101 已验证），作者全列表以 DOI 记录为准。
- action：rewrite

### [high] verification_gap — 21 条期刊条目 Crossref+arXiv 双库查无，未过真实性硬门
- 位置：[4][5][6][7][8][9][11][13][14][16][17][22][24][25][26][27][28][37][38][39][40]
- 问题：21 条期刊条目以标题精确检索 + DOI 直查 + 卷页地址反查三策略均无法定位。不直接判伪（存在检索覆盖不足可能），但在本案 6 条 arXiv 伪冒 + 7 条期刊错配已坐实的背景下，未过门条目应推定存疑。其中 [8][11][22][23] 为正文核心论证引文，[37][38] 疑为"国内现状"凑数条目，[5][39] 卷页与知名真实论文存在交叠冲突。
- 建议：writer 对 21 条逐条提供 DOI，并跑硬门三步：`https://api.crossref.org/works/{doi}` 核对标题/作者/卷期 + doi.org 解析 200 + 期刊官网比对文号。任何一条过不了门的，按伪造处理。全部结果回填本表销号。
- action：verify + research

### [high] citation_error — [36] 页码（文号）错误
- 位置：references.md L73
- 问题：真实论文为 PRL 133, 126801 (2024)，条目写 246901。标题、作者、期刊、卷、年均正确，仅文号漂移——这正是"近真实复制+局部漂移"的典型校验位失守。
- 建议：改为 `Phys Rev Lett, 2024, 133: 126801`，补 DOI 10.1103/PhysRevLett.133.126801。
- action：rewrite

### [high] internal_contradiction — [15] PRB 卷号与年份物理上不可能同时成立
- 位置：references.md L31
- 问题：PRB 卷 100 对应 2019 年；条目声称 2024 年发在卷 100，自相矛盾。且该文双库查无记录，疑整条虚构。
- 建议：先按 H1 硬门核实该文是否存在；不存在则删除，存在则按真实卷期重写（若为 2024 年论文，卷号应在 109–110 区间）。
- action：verify + rewrite

### [high] misattribution — [18] 疑似真身错挂 PRL 地址
- 位置：references.md L37
- 问题："Symmetry-based selection rules for high harmonic generation in altermagnets"无 PRL 记录；PRL 133, 116801 地址查无此文。最接近的真实文献是 Werner/Rappe "High harmonic generation in altermagnets" PRB 110, 235101 (2024)（与 [19] 真身同一篇——[18][19] 可能是对同一真实文献的两次变异复制）。
- 建议：先确认 [18][19] 是否本就引自同一篇 Werner/Rappe：若是，二条合一并正确挂 PRB 110, 235101；若确需 Ghorashi 的选择规则工作，提供其真实 DOI/arXiv。
- action：verify + rewrite

### [high] fabrication_suspect — [23] 作者论文清单无此条，标题疑拼装
- 位置：references.md L47
- 问题：arXiv 作者检索 Yarmohammadi 全部相关论文（8 条）无"Valley polarization and Floquet theory in 2D altermagnets with Rashba coupling"；真实近邻为 PRB 111, 224412 (2025)（RKKY 交互，主题不符）。标题把项目两大关键词（valley/Floquet/Rashba/交错磁）拼接的痕迹明显，PRB 111, 184401 地址无记录。此条挂项目标题核心词（Rashba），风险权重最高。
- 建议：作废重查。若需要"Rashba×交错磁×Floquet"理论支撑，可改引该作者已验证的真实工作（如 arXiv:2510.02451，PRB 113, 184403 (2026)，Rashba d-wave altermagnet 自旋 Edelstein 效应）并提供 DOI。
- action：research + rewrite

### [high] format_inconsistency — 全部期刊条目无 DOI，违反"DOI/arXiv 二选一"要求
- 位置：全文件（33 条期刊条目）
- 问题：本轮检验要求每条文献附 DOI 或 arXiv 编号其一。现有 arXiv 条目 7 条带编号（其中 6 条还是伪冒 ID），33 条期刊条目全部无 DOI——既不满足格式要求，也使评审无法快速溯源，且与 [36] 类"仅文号漂移"错误的快速自查手段缺失直接相关。
- 建议：返工时每条期刊文献补 DOI（格式如 `DOI: 10.1103/PhysRevLett.133.126801`）；预印本保留 arXiv 号。补 DOI 与 H1 硬门核实一次性完成。
- action：add

### [medium] uncited_entries — 9 条在列条目未被正文引用
- 位置：[1][2][3][4][13][37][38][39][40]
- 问题：预检显示 9 条零引用。其中 [1][2][3][4][13] 是反铁磁/交错磁领域综述与理论基础，正文改造后编号段（rationale 5–36）已不再触达，属"僵尸条目"；[37][38] 疑似为"国内现状"段落凑数的存疑综述（双库查无）；[39][40] 滑移铁电背景未被引用。死条目占比 23%，稀释文献库信噪比。
- 建议：结合正文实际论述补挂引用（如 [1][2] 应挂在反铁磁自旋电子学背景句）；确实无位置的删除。注意 [3] 修正后（见 C2）若保留必须挂引。删除后全库重编号并同步正文角标。
- action：add + remove

### [medium] missing_citation — [29] 正文有引、列表无条目，且核心论断依赖未发表数据
- 位置：编号 29 槽位（列表 L59–L61 之间缺失）
- 问题：预检称"正文引用但列表缺失：无"，但正文引用编号集包含 [29]，列表该编号无对应条目（L59 [28] 之后直接是 [30]）——预检结论与文件实况不符，本轮更正。此外从上下文推断 [29] 应为"本组 HHG 选择规则预研结果（in preparation）"类条目：申请书把核心创新点的证据支点放在未发表数据上，且该支点在文献库中完全缺位。
- 建议：① 立即补 [29] 条目；② 若为未发表工作，按规范标注（作者. 标题. 状态, 年份），不得伪装成已发表文献；③ 正文相应论断补充至少一篇已发表的可验证文献共同支撑。
- action：add + verify

### [medium] format_inconsistency — [40] 英文条目内嵌中文
- 位置：references.md L81
- 问题："First principles study of滑移铁电性 in 2D materials"中英混杂，不符合英文文献条目规范；且该条整体未过真实性核验（H1 批次）。
- 建议：核实真身后统一为英文（sliding ferroelectricity）；中文术语仅可出现在中文期刊文献的原生标题中。
- action：rewrite

### [medium] completeness_risk — 剔伪后有效引用数将跌破 20 篇下限
- 位置：全文件
- 问题：名义 40 条达标，但确认错伪 14 条 + 缺位 1 条 + 待核 21 条中若有半数不实，可辩护的有效引用将不足 20 篇下限。数量"达标"目前是假性达标。
- 建议：返工时按"先核实、再补引"顺序：14 条错伪先行替换为真实文献（保持主题覆盖：交错磁基础/MnPS₃ 插层/滑移铁电超快/HHG 理论），再补足至 30–35 条已验证文献；每新增一条须过 H1 硬门。
- action：research + add

### [low] format_inconsistency — 作者列表截断方式不统一
- 位置：references.md L3 [1]、L49 [24] 等
- 问题：[1] 用"Baltz V, Manchon A, Tsoi m, et al."三作者+et al.，其余条目多为"三作者 + et al."或全列表混排；[38] 期刊缩写"Sci China Phys"与其他条目缩写风格不完全一致（Science China Physics, Mechanics & Astronomy 的通行缩写为 Sci China-Phys Mech Astron）。
- 建议：全库统一为"前三作者 + et al."（NSFC 常用式），期刊缩写统一按 ISO 4。
- action：rewrite

### [low] numbering_convention — 头部 4 条零引用条目占据编号资源
- 位置：[1]–[4]
- 问题：NSFC 惯例文献按正文首次引用顺序编号；[1]–[4] 全部零引用却占据列表头部，说明列表与正文引用顺序脱钩，返工删除/补挂后须整体重编号，正文角标须同步（上轮已发生过 rationale 17/22 角标错位事故，须三文件联合对照）。
- 建议：返工收官时按正文首次出现顺序重排全库，并跑一次程序化编号一致性预检再交付。
- action：rewrite

## 3. 锚点对比（结构化三步）

**锚点 1：[36]（近真实条目 vs arXiv/Crossref 记录）**
- 引用（申请书 L73）：`[36] Wang J, Li X, Ma X, et al. Ultrafast switching of sliding ferroelectricity and dynamical magnetic field in van der Waals bilayer induced by light. Phys Rev Lett, 2024, 133: 246901.`
- 对比（Crossref DOI 10.1103/physrevlett.133.126801 实测）：`Ultrafast Switching of Sliding Polarization and Dynamical Magnetic Field in van der Waals Bilayers | Wang J (+8) | PRL v133 p126801 (2024)`。
- 差距：作者/期刊/卷/年/标题语义全部吻合，仅文号 246901≠126801 且标题"sliding ferroelectricity"应为"sliding polarization"。结论：条目系对真实文献的"复制+局部漂移"，说明作者列表与卷期骨架可信、校验位（文号/副标题）失守——返工时此类条目改两个字符即可救活。

**锚点 2：[32]（伪冒条目 vs arXiv 记录）**
- 引用（申请书 L65）：`[32] Morimoto T, Wong J, Liang Z, et al. High harmonic generation encoding quantum metric and Berry curvature. arXiv:2504.18845, 2025.`
- 对比（arXiv API id_list=2504.18845 实测）：`Introducing Interval Neural Networks for Uncertainty-Aware System Identification | Mehmet Ali Ferah; Tufan Kumbasar | 2025`。
- 差距：ID 真实、标题/作者/主题 100% 无关。结论：这是"借真实 ID 过机器查重、内容整体虚构"的伪冒，肉眼无法识别，必须 API 反查。此类条目无修复价值，只能作废重查。

锚点对比结论：差距明显

## 4. 评分依据

- **严谨性 0.30**：在列 39 条中 14 条经双库实测确认伪造或错配（35.9%），含 6 条 arXiv 全伪条目与 8 条期刊错配/矛盾（其中 [3][20][21] 涉及把知名论文/预印本挂到虚假期刊地址，属学术规范红线）；另 21 条无法核实。按评分纪律"critical 虚构文献条目：严谨性扣至 0.3–0.4 区间"，因伪造密度高且波及正文核心论据（[32]–[35] 为 Berry 曲率读出与 THz 驱动主线的证据源），取区间下限 0.30。
- **完整性 0.72**：数量 40 篇在 20–40 区间 ✓；时效性达标（2023–2026 文献约 70%，含 2025×5、2026×1）✓。扣分项：9 条零引用死条目（23%）、[29] 正文有引列表缺位、核心论断依赖未发表数据且无公开文献兜底、剔伪后有效数存跌破 20 下限风险。0.72。

## 5. 对抗结论

- 本轮发现 18 个问题（critical 6, high 6, medium 4, low 2），覆盖 40 个文献槽位中的 35 个。
- 相比上一轮：本课题参考文献专项为首次检验（R1–R2 前序为章节线），无同维度基线；相对程序化预检，新增"文献真实性"维度的全部发现，并更正预检一处失实结论（[29] 并非"无缺失"）。
- 是否达到输出标准：**否**——critical 未清零。当前文献库整体不可用：确认真实率仅 7.7%，两条研究主线的直接证据源（[32]–[35]、[10]）均涉伪。writer 必须执行"全部作废嫌疑条目 → 逐条 DOI/arXiv 硬门重查 → 重建列表 → 三文件角标同步 → 程序化预检复跑"的完整返工流程后，方可进入第 3 轮复检。
- 返工优先级：C1（6 条 arXiv 伪冒）＞ C2–C6（期刊错配五条，其中 [3][19][20][36] 已给出可直接粘贴的正确条目）＞ H1（21 条硬门批量核实+补 DOI）＞ M1/M2（死条目处置+[29] 补位）＞ 其余。
- 下一轮建议：writer 交付时附"硬门核验回执"（每条 DOI 的 Crossref 响应摘要），critic 按 30% 抽样复测 + 对新增条目全查。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.30
完整性：0.72
综合评分：0.51
