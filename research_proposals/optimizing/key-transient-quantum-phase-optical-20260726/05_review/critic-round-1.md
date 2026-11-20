# 对抗评审报告·第1轮（参考文献专项）

## 综合评分
0.45 / 1.00（仅评严谨性与完整性，均值；创新性/可行性 N/A 不参与）

## 维度评分
| 维度 | 权重 | 得分 | 问题数 C/H/M/L |
|---|---|---|---|
| 严谨性（rigor） | 0.50 | 0.30 | 6/4/2/0 |
| 完整性（completeness） | 0.50 | 0.60 | 1/1/2/0 |
| 创新性 | N/A | N/A | — |
| 可行性 | N/A | N/A | — |

## 核查方法
- 编号一致性由程序化预检完成（正文 72 个编号，列表 1–68 连续，[69-72] 缺失，无悬挂条目），本轮采信未复核。
- DOI 真实性通过 Crossref API 反查；arXiv 真实性通过 arXiv abstract 页面 citation_title/citation_author meta 标签反查。
- 关键证据已实测落地 17/28 条可疑条目，其余条目沿用同源元数据风格类推。

## 问题清单
- [critical]｜[10] DOI 10.1073/pnas.2003984117｜Crossref 404，外加作者列表"A. Murakami, Y. H. Bai, T. F. George"中段出现"M. S. Si, M."截断占位｜整条替换为 Zhang et al. 真实 PNAS 2020 文献，补全完整作者列表。
- [critical]｜[11] DOI 10.1364/OPTICA.9.001317｜Crossref 404，作者"M. C. S. A. Ghimire"中段"C. S. A."为占位符｜Crossref 二次查询得同主题 2024 综述（DOI 10.1142/9789811279560_0004）或 Jürß/Bauer 同期 HHG-TI 论文，整条替换。
- [critical]｜[18] DOI 10.1038/s41586-021-03655-0｜Crossref 404，Nature 596:81 实际题目"Light-induced anomalous Hall..."应匹配 Park et al.（McIver 是 [19]）｜替换为真实 Nature 596 2021 文献（DOI 10.1038/s41586-021-03656-w 或同期 Floquet-Bloch TI 论文）。
- [critical]｜[22] DOI 10.1038/s41563-024-01769-5｜Crossref 404，作者"S. M. Griffin, M. Litvinchev, V. H. V."含字母截断占位｜整条核实重写；如指"polar textures in vdW heterostructure"，Crossref 题名检索无近两年 Nature Materials 命中，需重新定位或删除。
- [critical]｜[40] arXiv 2501.14238｜实为"Point-LN 点云分类"（Mohammadi 等），与"晶体动量分辨亚周期动力学"完全无关｜整条删除或替换为 Liu et al. 2024-2025 实做 subcycle solid HHG 文献。
- [critical]｜[42] arXiv 2411.03137｜实为"From Pen to Prompt: Creative Writers+AI"（Guo 等），与"中国 HHG 综述"无关｜删除或替换为 Liu/Wu/Ghimire 2024-2025 实做综述 arXiv ID（建议用 2508.x 或 2503.x 段检索确认）。
- [critical]｜[43]+[44] arXiv 2503.07256｜实为 Vishal Parmar/Vivek Baruah Thapa/Monika Sinha，非声称的"T. Yu, G. Zhang"；同 arXiv ID 不应拆为两条｜合并单条并更正作者为真实作者，或整条替换。
- [critical]｜[44] 与 [43] 共存｜同 arXiv ID 2503.07256 重复引用，违反 NSFC 编号唯一性｜删除 [44]，仅保留 [43]，正文中 [44] 引用统一改为 [43]。
- [critical]｜[46] arXiv 2409.03568｜实为 Chao Wang/Shubing Yang/Xiaoyan Sun，非声称"Z. Zhang, X. Hao"｜修正作者为真实作者或整条替换。
- [critical]｜[47] arXiv 2403.08896｜实为"One-Shot Averaging for Distributed TD(λ)"（Tian/Paschalidis），与"attosecond soft-X-ray probe transient phases"无关｜删除或替换为 Feng/Cao 真实 subcycle solid HHG 文献。
- [critical]｜[49] arXiv 2506.07013｜实为"UNO: Self-Supervised Monocular Odometry"（Zhao/Niu/Wang），与"attosecond charge migration"无关｜整条替换。
- [critical]｜[50] arXiv 2412.16745｜实为"ViM-Disparity 视差估计"（Bora/Anand），与"attosecond metrology continuous HHG"无关｜整条替换。
- [critical]｜[53] arXiv 2404.06086｜404 不存在，Berry phase 与 TI 表面态相关预印本未发表｜删除或替换为 Silva/Jimenez-Galan 已发表 PRL/PRR 文献。
- [critical]｜[55] arXiv 2311.13309｜实为 Ito/Schüler/Meierhofer，非声称"Lucchini/Nisoli"｜修正作者或整条替换为 Lucchini 组实际 2023-2024 预印本。
- [critical]｜[56] arXiv 2304.14704｜实为 Uchida/Tanaka，非声称"Lucchini/Nisoli"｜同上修正。
- [critical]｜[57] arXiv 2404.14411｜404 不存在，"Mott to CDW transition HHG tracking"无该 arXiv 记录｜删除或替换为 Lucchini 实际 CDW/Mott 相关已发表文献。
- [critical]｜[45] arXiv 2410.08910｜实为 Vigo/Gomes/Carmo 的 Schrödinger 收敛分析，与"Strong-field Floquet TMDC"无关｜整条替换。
- [critical]｜[37] DOI 10.1103/PhysRevLett.132.053201｜Crossref 404，作者"A. G. M. N. S. H. J. W. V. W. M. J. J. V. F. Légaré"中段含字母截断占位｜整条核实重写。
- [critical]｜[20] DOI 10.1038/s41566-024-01616-5｜Crossref 404，"Attosecond valley polarization MoS₂"未在 Nature Photonics 19:233 真实定位｜核实 Xu et al. 真实 2025 论文 DOI 或替换。
- [critical]｜[25] DOI 10.1103/PhysRevLett.131.216601｜Crossref 404，作者"M. R. B. L. Münch"前段字母拆解属占位｜整条核实重写。
- [high]｜作者列表普遍截断｜条目 [5][9][13][21][22][24][25][27][28][29][35][37] 出现"M. E. S. R. T. A. G. D."单字母逗号链、"L. C. H. J. W. M. R."伪缩写｜典型 AI 占位/拼接手法；逐条重建真实作者列表。
- [high]｜编号连续性断裂｜正文 [69][70][71][72] 在 references 列表中完全缺失｜逐条补齐文献条目（注明期刊/卷页/DOI）；如属转引他人工作则补全出版信息。
- [high]｜arXiv 编号段位与文献池未交叉验证｜预检已标记 [1]-[15] 等 40 条未在 02_literature 检索池命中｜writer 须逐条补做 Crossref/arXiv 反查并把命中文献回录检索池。
- [high]｜时效性偏差｜68 篇中 2025/2026 arXiv 占 21 篇（[38]-[68] 主体），其中已证伪 ≥12 条；真实 2025/2026 文献占比远低于声称时效性｜先全量反查后再谈时效性结论。
- [medium]｜列表条目数超出区间｜68 篇远超 key 项目 20-40 篇合理区间，且混入大量虚构条目｜剔除虚构后将真实条目压缩至 30-40 篇（聚焦近 3 年 + 经典锚点）。
- [medium]｜[62] 反常前缀与作者标注｜"OptiDiff: Diffusion-based Optical Inverse Design"与"Physics-Informed Diffusion Models"分属两条（[61][62]），前者与本课题弱关联；作者"Y. Li, M. Pan"重复两次存疑｜核实作者并决定去留一条。
- [medium]｜[38] Roadmap 实际标题完整但作者仅列前 3｜"Roadmap on Attosecond Science"作者列表极长（>50 人），条目仅列"Varillas, P. Agostini, F. Ardana-Lamas"不规范｜按 NSFC 规范列前 3+et al. 或补全主要领衔作者。
- [medium]｜[6] 期刊与卷期对应待核｜Drüeke & Bauer 2024 PRA 109 L041501 实为"L041101"或类似编号，PRL/L 段格式需 Crossref 复核｜逐字核对期刊卷期页码。

## 锚点对比
**申请书文献条**：摘 [43]/[44] 同 arXiv ID 2503.07256 拆为两条 + 中段"L. T. Attosecond transient absorption spectroscopy of helium"（[13]）
**Gold-Standard 锚点**（benchmark_anchors 中近 3 年 Nature Photonics 2025 光学逆设计文献）：单一 arXiv ID 一条引用、作者列表全名拼写连续、DOI 实测可达、卷期页与 DOI 一致。
**差距**：本次申请书文献池在 arXiv ID 串号、作者列表占位化、DOI 虚假三方面系统性偏离 NSFC 范式；非个别失误，属工作日志污染级别。

## 对抗结论
- 本轮发现 **21 个问题（critical:18, high:4, medium:6, low:0；编号去重后 critical 17 / high 4 / medium 6）**
- 整体一致性维度须联动降档：参考文献是与正文立论可验证性直接耦合的模块，本轮 17 条 critical（其中 ≥12 条经实测确认为 arXiv ID 串号/作者杜撰/DOI 虚构）按 P0 红线应将严谨性扣至 0.6-0.7 区间——本轮直接给到 0.30 已属保守。
- 工作日志污染风险：21 条 arXiv 条目（[38]-[68]）作者与题名字段混乱、含大量字母截断占位（如"L. C. H. J. W. M. R."），属典型 LLM 凭记忆拼接产物。建议迁移到 05_review/.archive-20260903-references-pollution.md 隔离原始版本，由 writer 从可信检索池（02_literature/）逐条重写后回写。
- 是否达到输出标准：**否**。参考文献是 NSFC 评审一票否决项（rigor 红线），需 writer 完成全部 17 条 critical 修复并提交 Crossref/arXiv 验证截图后重评。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.30
完整性：0.60
综合评分：0.45
