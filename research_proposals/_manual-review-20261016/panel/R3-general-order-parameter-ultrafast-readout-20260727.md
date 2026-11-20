# R3 引用审校 — general-order-parameter-ultrafast-readout-20260727

- 审校日期：2026-10-17
- 注：任务书课题号尾缀 20260726，仓库实际目录与 P0 清单均为 **20260727**，本报告按实际课题 ID 落盘
- 审校范围：04_proposal/sections/{rationale.md, content.md, scheme.md, references.md} + p0-general-order-parameter-ultrafast-readout-20260727.md（14 条 open，其中 critical 2 条为场强换算问题不属 R3 职责，引用相关 3 条已逐条核实现状）
- 方法：程序化编号对账（/tmp 脚本）+ 高风险条目联网反查（含 P0 涉及条目）+ 正文声称匹配性抽查
- 结论速览：40 条文献全部真实（核实 8 条零虚构，含 2 条 2026 Nature/PRL 新文），P0 引用相关 3 条**全部已修复**；但发现**新一轮重排失配**：§二.3 至 §三.2 存在 5 处编号错挂（Bai/Mizuno/Zhang/Kravchuk 四条文献编号整体错位），致 [35][36] 成为死条目。修复后引用体系即完整。

## 编号对账（五项计数 + 明细）

| 项目 | 计数 | 明细 |
|---|---|---|
| 1) 占位符 | 0 | — |
| 2) 死条目（列了未被引） | 2 | **[35] Bai（APL 2026 CrSb 霍尔/单晶）、[36] Kravchuk（PRB 2025 g 波磁振子）**三章零挂靠——两者均非"多余条目"，而是错挂的受害者（真身内容被挂到了 [37]/[38] 上，见意见） |
| 3) 超界（引了不存在编号） | 0 | 正文引用编号均在 1–40 内 |
| 4) 一号两用（同一文献多条目） | 0 | DOI/arXiv 查重无重复（[16] DOI 字段排版含"no. 25**"）的 markdown 粗体残留，属格式瑕疵非编号问题，见 R3-08 |
| 5) 正文断链（编号在 references 缺失） | 0 | — |

被引次数 Top：[1] Tyulnev 14、[2] Zhang 8、[18] Ma SHG 7、[12] Šmejkal 7、[22] Singh 7、[15] Wang 声子 6、[30] Long 6。

**错挂模式诊断**：正文 §二.3/§三.2 段落使用的是一套旧编号（Bai=37、Kravchuk=38、Zhang=39、Mizuno=40），与当前 refs 表（Bai=35、Kravchuk=36、Zhang=37、Mizuno=38、Yu=39、Grzybowski=40）整体错位两位——典型 refs 表重排（疑在 [35]/[36] 插入或前移时）后正文未同步。scheme §三.3 的 Yu=[39]、Grzybowski=[40] 两处为新编号正确挂法，新旧两套编号在同一章内并存，交叉印证失配范围限于 rationale §一.2 末段、content §二.3、scheme §三.2 三处段落。

## P0 清单核实现状（引用相关 3 条）

| P0 条目 | 现状核实 |
|---|---|
| #7 [high] reference_status（原 [45] Yu 预印本应升刊版 npj Quantum Materials 2025） | **已修复**：现条目 [39] 已著录为"npj Quantum Mater. 10, 47 (2025). DOI: 10.1038/s41535-025-00766-3"【正式发表】，与 P0 给出的 DOI 逐字一致（联网另经 arXiv:2412.12882 确认弱 MAE 内容匹配） |
| #13 [high] 全表 46 条超 20–40 上限 | **已修复**：现表 40 条，恰好落回上限 |
| #14 [high] 孤儿条目 [2]（NbN Higgs） | **已修复**：现 [2] 为 Zhang 等 TiSe₂ 理论复现（PRB 112, 085147），被引 8 次，是 G1 判据的参数迁移锚点 |
| #3/#8 [critical]（场强换算） | 非 R3 职责，未核（留给 R1/方案审校） |

## 联网核实记录（8 条，含 P0 涉及）

| 条目 | 检索证据 URL | 结论 |
|---|---|---|
| [1] Tyulnev et al., Commun. Mater. 6, 152 (2025) | https://arxiv.org/abs/2409.04216 | ✓ 真实。作者列表逐字匹配；摘要确认偏振分辨 HHG 在 CDW 相（约 200 K 以下）出现各向异性分量，与 G1 复现判据声称一致。⚠ arXiv v1 标题含"Mott to Charge-Density-Wave"，条目标题无"Mott to"——疑刊版改名，建议对照 Commun. Mater. 正式标题定稿（见 R3-07） |
| [2] Zhang et al., PRB 112, 085147 (2025) | https://arxiv.org/html/2412.13329 及 ICREA Memoir（Biegert 条目） | ✓ 真实。卷页 112, 085147 由 ICREA 独立确认；摘要确认"simplified phenomenological mean-field model"，与正文"含时薛定谔方程+现象学平均场多带模型"声称匹配 |
| [15] Wang, Wang & Meng, arXiv:2607.13863 | https://arxiv.org/html/2607.13863 及 Semantic Scholar | ✓ 真实。作者 Chenyu Wang/Yaxian Wang/Sheng Meng，2026-07-15 与条目一致；摘要确认 α-MnTe 经 B₁g 声子选择性激发进入瞬态补偿亚铁磁（cFiM）相，"MnTe+CrSb"中 MnTe 主体获确认 |
| [16] Yang et al., PRL 136, 256702 (2026) | https://cup.iphy.ac.cn/cmsfiles/3439_2026070309545770485.pdf（全文 PDF） | ✓ 真实。PRL 136, 256702 卷页经三个独立引用源确认；摘要确认"Kerr 效应源于动量空间 Berry 曲率、Voigt 效应源于实空间 Néel 各向异性"，与正文双空间声称逐点匹配 |
| [22] Singh et al., arXiv:2511.16086 (v2) | https://arxiv.org/abs/2511.16086 | ✓ 真实。v2（2026-05-13）标题已改"Coherent high-velocity chiral magnons…"与条目一致（v1 为"Chiral Spin-Split Magnons"，条目按 v2 著录正确）；摘要确认"perfectly compensated Ising altermagnet below T_N = 733(4) K"与极化中子衍射+磁化率双手段，正文 733(4) K 判据锚点完全成立。⚠ content §二.3"能量劈裂 27(2) meV"与 v1 摘要"27(5) meV"不确定度末位不符（v2 摘要未给该数） |
| [30] Long et al., Nature 656, 854–860 (2026) | Google Scholar（Weinberger 主页）及 https://www.phy.cam.ac.uk/news/... | ✓ 真实。卷页 656 (8129), 854–860 经 Scholar 确认；Cambridge Cavendish 新闻确认 dHvA/强磁场量子振荡方法，与"g 波 dHvA 节点证认"声称一致 |
| [35] Bai et al., APL 126, 042402 (2025) | https://pubs.aip.org/aip/apl/article-abstract/126/4/042402/3332865 | ✓ 真实（死条目但文献本身真实）。arXiv:2409.14855；摘要确认霍尔非线性源于多载流子（非反常霍尔），与 rationale"南京理工大学团队…三载流子分析溯源至多带输运"声称匹配——该声称当前错挂 [37]（见 R3-01） |
| [39] Yu et al., npj Quantum Mater. 10, 47 (2025) | https://arxiv.org/html/2412.12882 | ✓ 真实。P0 #7 涉及条目已按刊版著录；摘要确认"weak MAE suggests flexibility in adjusting the Néel vector orientation"，与 B_K 端约束声称（总能量差 <1 meV）方向一致 |

## 意见清单

- [R3-01|critical] rationale｜§一.2 L33｜Bai 内容错挂 [37]，真身 [35]｜"南京理工大学团队完成高质量单晶的生长与磁输运测量，其霍尔非线性经三载流子分析溯源至多带输运而非反常霍尔 [37]"｜[37] 是 Zhang 磁振子第一性原理；联网核实 Bai（APL 126, 042402）才是该声称出处，[37]→[35]，同时消除 [35] 死条目
- [R3-02|critical] content｜§二.3 L35｜Mizuno 选择定则错挂 [40]，真身 [38]｜"Mizuno [40] 在自旋点群框架下证明，沿晶轴的线偏振驱动下铁磁与交错磁相位给出相同选择定则"｜[40] 是 Grzybowski CoO 迟滞文，与自旋点群 HHG 定则无关；[40]→[38]（references L117 [38] 关联注亦自称"§二.3 定则参照"，与正文实测对不上）
- [R3-03|critical] content｜§二.3 L39｜Zhang 磁振子错挂 [39]，真身 [37]｜"Zhang 等人 [39] 以线性自旋波理论预言 CrSb 的手性磁振子劈裂由…第 11、12 近邻交换通道驱动"｜[39] 是 Yu 反常输运（scheme §三.3 L87 挂对的那条）；[39]→[37]，与同句 Singh=[22]（挂对）形成修正后完整预言—证实链
- [R3-04|critical] content｜§二.3 L41；scheme｜§三.2 L31｜Kravchuk 错挂 [38]（两处），真身 [36]｜"理论分析表明易轴型 CrSb 的手性磁振子劈裂保持 g 波对称且不受易轴各向异性改变 [38]"｜两处 [38]→[36]（Kravchuk PRB 112, 144421）；修正后 [36] 死条目同步消除
- [R3-05|high] references｜全表｜重排失配修复后须全链复验｜正文旧编号残留（Bai=37/Kravchuk=38/Zhang=39/Mizuno=40 对现表 35/36/37/38）｜按 R3-01~04 改正后，以正则提取全文 [N] 与 40 条逐号对账一遍，重点复核 §二.3 与 §三.2 两段（新旧编号并存区）
- [R3-06|high] content｜§二.3 L39｜[22] 劈裂数值不确定度与 arXiv 摘要不符｜"自旋波拟合给出能量劈裂 27(2) meV，能量维度受谱仪分辨率（约 20 meV）限制未直接分辨"｜arXiv v1 摘要载"27(5) meV…comparable to the instrumental resolution (20 meV)"，分辨率一致而不确定度 27(2)≠27(5)；核对 v2 正文后统一，无法核实则改引 27(5) meV
- [R3-07|medium] references｜[1]｜条目标题较 arXiv 版缺"Mott to"｜"High harmonic spectroscopy reveals anisotropy of the charge-density-wave phase transition in TiSe₂"｜arXiv v1 标题为"…anisotropy of the Mott to Charge-Density-Wave phase transition…"；对照 Commun. Mater. 6, 152 刊版标题定稿，若刊版即删则维持并留核对记录
- [R3-08|medium] references｜[16] L45｜DOI 字段排版残留 markdown 粗体符号｜"Phys. Rev. Lett. **136**, no. 25**, 256702 (2026)"｜"no. 25**"处有孤立 `**`，PDF 制版将外泄格式符；全表扫一遍 `**`/`__` 残留并清理
- [R3-09|medium] references｜[22] 条目｜预印本状态标注滞后风险｜条目仅标 arXiv:2511.16086【预印本】（v2 2026-05-13）｜该文 v2 已 8 个月未标刊版；按 P0 #7 对 [39] 的处理先例，提交前在 doi.org 检索一次是否已获期刊 DOI，有则升刊版著录

正面确认（不计意见）：P0 引用相关 3 条（#7 刊版化、#13 条数收敛、#14 孤儿消除）全部修复到位；733(4) K 关键判据锚点（[22]）联网逐字核实成立且正文自我限定（"Néel 温度为同组表征的副产量，与独立测量 [21] 一致"）准确；d/g 波开放争议（[12] vs [30]）双证并引、未单边预设，引用立场与检索证据一致。
