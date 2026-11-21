# 评审团复核报告（第二轮）

复核员：独立复核（fresh context）｜ 课题：general-new-idea-20260822 ｜ 时间：2026-10-05

复核方式：只验清单、不做全量评审。一切以磁盘当前文本为准重新取证（grep 命中行 + 读段摘录），不采信三份 findings 与修改报告的自我声明；r1 遗留靶子（R13–R20）逐条独立取证，修改声明（锚点数、超长句、r1 回归、指标口径）全部程序化复测。引用计数、锚点-条目映射、句/段长度、模板词表均为脚本独立计量。

## 逐条判定

| # | 问题（短） | 判定 | 证据 |
|---|---|---|---|
| R13 [遗留 critical] | Osumi[13]"沿 Γ–K 约 0.3 eV 自旋轨道能隙"两轮未闭合 | 已解决（独立取证闭合，正文无需改动） | 缓存文件独立找到：`knowledge/raw/pdfs/_text_cache/2308_10117.txt`（38 KB），标题"Observation of giant band splitting in altermagnetic MnTe"，作者 9 人（T. Osumi, S. Souma, T. Aoyama, K. Yamauchi, A. Honma, K. Nakayama, T. Takahashi, K. Ohgushi, T. Sato，L2–3）与 [13] 条目逐一相符。摘要 L23–24 逐字："The magnitude of the splitting reaches 0.8 eV at non-high-symmetry momentum points, which is much larger than the spin-orbit gap of ∼0.3 eV along the ΓK high-symmetry cut"；结论 L273–274："a small (∼0.3 eV) band splitting along the high-symmetry ΓK cut, suggestive of an additional contribution from the SOC"；附录 C L321："ΓK2 cut … maximum splitting size of 0.25 eV"；L72"bulk single crystal"、L87"x-ray Laue backscattering … (0001) cleaved plane"、L19/L58/L91 TN = 307 K。正文四处表述与原文相符：rationale L29"沿 Γ–K 高对称线约 0.3 eV 的自旋轨道能隙"、L31"节点面外的一般动量点最大约 0.8 eV"、scheme L79"块体单晶解理"、scheme L99"约 0.3 eV 能隙即 SOC 诱导能隙"（摘要径称 spin-orbit gap，结论节 "suggestive of" 留有余地，采摘要口径可接受）。推理链另获 [19] 综述独立佐证：2602_13590.txt L713–716"weak altermagnetic LKSD with a ∼100 meV splitting along the Γ–K path within a nodal plane" |
| R14 [遗留 low] | 差分单谱对 SNR"约 0.5"舍入张力 | 已解决 | scheme L45 磁盘文本："单个谱对（正负磁场各一幅）的差分信噪比约 0.55"；复算 1%/(√2×1.3%)≈0.544≈0.55、0.55×√30≈3.01≥3 恰闭合；全章 grep "约 0.5。" 0 命中；10³ 档（单谱对≈1.7，需≈3 单元）、10⁴ 档（≈5.5，需 1 单元）均落入 L43"每温度点……1–6 个单元"包络 |
| R15 [遗留 low] | 口径表"非相对论劈裂为零"子句在 rationale 无逐字落点 | 已解决 | full_review L25 行现文：立项依据列"SOC 能隙约 0.3 eV（沿 Γ–K）；节点面外一般动量点最大约 0.8 eV"（= rationale L29/L31 实际持有）；研究方案列"节点面内非相对论劈裂为零，SOC 能隙约 0.3 eV；节点面外一般动量点最大约 0.8 eV"（= scheme L99 实际持有）；研究内容列"同立项依据"。虚置登记已消除 |
| R16 [遗留 R10] | Ghimire[1] 3.25 μm 驱动波长 | 已解决（有据维持） | KB 页 2025-2505_19894 L21"首个体固体 HHG 就是在纤锌矿 ZnO 中、3.25 µm 驱动下观测到的"、L107"（3.25 µm、>1 TW/cm² 驱动）"；scheme L57"ZnO（Ghimire 等[1]）在 3.25 μm 附近驱动"原文未动 |
| R17 [遗留 R10] | Amin[25] 30 nm / InP(111)A / 100 nm–10 μm | 部分解决（合规） | 已闭合部分独立取证：Dal Din 全文缓存 2401_09187.txt L340"on InP (111) A substrates using elemental Mn and Te sources"——InP(111)A 衬底有据。残留部分：scheme L75"30 nm α-MnTe(0001) 薄膜""从 100 nm 涡旋到 10 μm 图案化单畴态"两数值维持原文并登记待核（Amin 论文无 arXiv 全文在库）——符合"核实不了不改写"纪律 |
| R18 [遗留 R10] | Liu[21] 哑铃形/四叶草形细节 | 豁免（合规待核维持） | rationale L47"取向依赖的谐波产额在无 Hubbard U 时呈哑铃形，引入 Hubbard U 后……转变为四叶草形"原文未动；KB 无 PRB 112, L081105 专页与全文，登记待文献专轮，未凭记忆改写 |
| R19 [遗留 R10] | rationale L75 CDW 相变敏感性断言（无锚） | 豁免（合规待核维持） | rationale L75"HHG 光谱学在电荷密度波体系中已展示相变敏感性"原文未动、未补锚；KB 最接近证据 2404.14411 为模型计算，不足以支撑"已展示"实验口径，留文献专轮裁决 |
| N1 [high] | arXiv:2406.02238 与三处创新缺口声明潜在重叠 | 已解决（处置合规：待核登记，正文未改） | raw 条目（knowledge/raw/papers/2024-2406.02238-mnte-hhg-altermagnet-fingerprint-precision-classification.md）实测：authors: "multiple"、status: "unseen"、has_pdf: false、abstract: ""、score_deepxiv: 0.85——仅元数据级。五章节 grep "2406.02238" 0 命中，references 仍 32 条无新增条目；三处缺口声明原文未动且带时限限定（rationale L13"据现有文献检索（截至 2026 年 8 月）"、L71"（检索截至 2026 年 8 月）"、scheme L115"据目前检索（截至 2026 年 8 月）"、L121"（截至 2026 年 8 月检索）"）；修改报告 N1 行"待核｜—（正文不改）｜建议文献专轮最优先读取该文"及"遗留与风险"第 1 条在案——未据标题擅自改写，处置合规 |
| N2 [medium] | scheme L49 顺磁相点数归属错置 | 已解决 | scheme L49 磁盘文本："300–320 K 跨 T_N ≈ 310 K 加密至 5 K 步长（5 点）刻画相变邻域。320–340 K 以 5 K 步长延伸（4 点），两段合计提供 6 个顺磁相数据点（315–340 K），满足不少于 5 个的设计要求。"复算：15+5+4=24（与 scheme L51"T 为 24 点网格"闭合）；顺磁相点 315/320/325/330/335/340 共 6≥5；与 content L51"顺磁相获取不少于 5 个数据点"、scheme L137"顺磁相 ≥ 5 个数据点"设计-指标链对齐 |
| N3 [medium] | rationale L25 Reimers[10] 句漏材料名+"自旋分辨"超出证据 | 已解决（含可回滚标注） | rationale L25 磁盘文本："Reimers 等人[10]于 2024 年以软 X 射线 ARPES 在 CrSb(100) 薄膜上直接观测到 g 波带劈裂，并经 P/S 偏振依赖测量验证劈裂带的宇称选择规则，与同年体相单晶高分辨率 ARPES 给出的大带劈裂相互印证。"双证据独立核实：KB 专页（2024-s41467-024-46476-5）L35/L74"Reimers 与 Šmejkal 等人在 CrSb(100) 薄膜上用软 X 射线 ARPES"（全页无"自旋分辨"记载）；[19] 综述 2602_13590.txt L811–812"Using both P- and S-polarized light, they verified the parity selection rules of the split bands"。改写不超出 KB 可证口径；修改报告 N3 行与"遗留与风险"第 4 条载明"若文献专轮证实 [10] 确含自旋分辨探测可回滚"；材料名补齐消解指代悬置，后句"两组独立实验在体相与薄膜样品上一致指向 g 波对称性"衔接通顺 |
| N4 [low] | scheme L33 单脉冲能量 0.5–5 μJ 与 A_eff 口径 | 豁免（理由合理） | scheme L33 原文未动；下游仅"平均功率毫瓦量级"结论，任一焦斑读法（0.15–2.4 / 0.6–9.4 μJ）下均稳健、无判据依赖此区间；留预研以实测光斑定死口径后收敛 |
| N5 [low] | scheme L55 InGaAs/InSb 响应截止约 5.5 μm | 豁免（理由合理） | scheme L55 原文未动；作为探测链联合截止口径成立（5.5 μm 由 InSb 决定），是否删 InGaAs 取决于实际装置配置，KB 不可核，留预研确认 |
| CR-1 [critic] | AI 模板腔与套话 | 已解决（复测通过） | 程序化复测 11 词全 0（在此基础上/本项目拟/本项目将/值得注意/综上所述/总而言之/不仅如此/与此同时/众所周知/如前所述/如上分析）；"为…提供…支撑"跨句正则 0 命中；句首"本项目"3 处（scheme L117/L121/L125 创新点功能声明句），非滥用 |
| CR-2 [critic] | 超长句与超长段 | 已解决（复测通过） | >120 字超长句程序化全量复测 0；>400 非空白字段落仅 rationale L75（实测 401，三重瓶颈段），维持 r1"临界不动"裁决 |
| CR-3 [critic] | [N] 角标 40 超出 10–20 校准带 | 豁免（维持人工裁决） | 独立复测 rationale 22 / content 4 / scheme 14 / full_review 0 = 40 组，与 r1 完全一致、本轮零增减；10–20 校准带与仓库标准带 35–47 互斥，不擅自整体剪枝、留人工裁决，处置合规 |
| CR-4 [critic] | 跨章复述密度 | 已解决（复测通过） | r1 已收敛 3 组逐字重复 grep 复测均单章命中："弱光注入下的非平衡自旋密度"仅 rationale、"在对称性层面构成本质差异"仅 scheme、"不参与节点面对称性的轨道分量上被部分抑制"仅 scheme，未回潮 |
| CR-5 [critic] | 自引用元话语 | 已解决（通过） | 自指 3 处均为必要章节指针（scheme L17"参照 Mizuno 的自旋群选择规则与 Ly[20]…"、L115"已在立项依据 §3 交代"、L121"如创新点一所述"）；"如前所述/如上分析"0 命中 |
| CR-6 [critic] | r1 表达修复项回归 | 已解决（复测全 0） | grep 独立复测："WSe" 0、"真空加速" 0、"切线方向" 0、"经 N 次" 0、"薄膜数据下限" 0、"总线" 0、"在难点四详述（详见" 0、"持有" 0 |
| R15/V1 前置 | reviewer 遗留观察项 2（口径表虚置） | 已解决 | 同 R15 行，full_review L25 三列与各章实际持有一致 |
| V1 [reviewer] | 17 项跨章指标口径一致 | 已解决（复测一致） | 逐项独立复核全部一致：T_N 310 K（rationale L65/content L33·L51/scheme L9·L31·L49）、0.41 eV（rationale L9·L33/scheme L33）、0.3–0.8 eV（rationale L31/scheme L19·L97）、带内比值 0.375–1.0（scheme L99·L103、full_review L38；0.3/0.8=0.375、0.3/0.3=1.0 复算相符）、三档 <0.3/0.3–1.0/>1.0（scheme L103）、原子 SOC 0.4–0.5 eV（scheme L97）、κ 三档（scheme L11/L93/L173）、GR<1.2（scheme L11/L93/L139）、σ_posterior=先验 50%（content L53/scheme L11）、δ_TN ±3 K vs SQUID ±2 K（content L53/scheme L13）、SNR≥3:1（content/scheme 多处）、差分 ≥1% 暂定（content L51·L73/scheme L9）、MoS₂ 6–13 阶·0.30 eV·≤10%（content L21·L73/scheme L7·L67·L133·L147）、顺磁 <1%（content L51/scheme L7·L133·L159）、顺磁点数 6≥5（scheme L49/content L51/scheme L137）、机时 1–2 周（scheme L49/L145）、检索截止 2026 年 8 月（rationale L13·L71/scheme L115·L121） |
| V2 [reviewer] | 口径表其余行为统一设定值登记 | 豁免（理由合理） | 温度区间/波长/强度等行属全项目统一设定值登记惯例，非 r1 V2 级归属错置；不扩大化改表 |
| V3 [reviewer] | references 编号连续性与锚点对应 | 已解决（复测通过） | 程序化核点：[1]–[32] 连续无跳号；正文 40 组锚展开 25 个编号全部有登记条目、无"有锚无条目"；未引 7 条 [2][19][22][24][26][28][29] 与 r1 V6 口径一致 |
| V4 [reviewer] | 作者列表截断体例不一 | 豁免（理由合理） | 统一截断需逐条重录作者串、转录出错风险大于评审收益，全列反利于核查 |
| V5 [reviewer] | full_review 骨架语义与衔接指针 | 已解决（复测通过） | 改后实测去空白 2132 字 ≤3000（findings 所记 2105 为改前实测，r2 表行修改净增约 27 字，仍在阈值内）；衔接指针抽查全落点：content L15→scheme §6.1、content L19→§5.4、rationale L33→§5.4、content L77→§10、scheme L37→§6.1，full_review 所引 §5.4/§6.3/§7/§8/§9/§10 均存在于 scheme 实际节标题 |
| V6 [reviewer] | r1 全部修复项回归检查 | 已解决（复测通过） | grep 集同 CR-6 全 0；SNR 估算链（scheme L43/L45/L49 与 §10 L169/L171 产额/H_SF 预案）与计算量账（L23 4×10⁴ CPU·h 与 §8 L151/L153"10⁴–10⁵/10⁵ 以内"）复核无回归 |

## 抽查与新问题

每处修改点看上下文衔接，未发现阻断性新问题：

- rationale L25（N3）：上承 L23 Long[8] CrSb 句、下接"两组独立实验在体相与薄膜样品上一致指向 g 波对称性"收束句，材料名补齐后指代清晰；同段无编号变动（仍 [10]），Reimers 在全部章节仅此 1 现（references 1 现），无连带口径漂移。
- scheme L45（R14）：与 L43（差分单元定义、每温度点 1–6 单元）、L49（单点 0.5–3 h）、L85/L169（10² 下限档挂 §10 产额预案）四处口径闭合；0.55 代入后 10³/10⁴ 档所需单元数（3/1）仍落在"1–6"设计包络内。
- scheme L49（N2）："延伸（4 点）"计点约定（320 K 已计入前段）与改前一致，总点数 24 不变；与 content L51、scheme L137、scheme L51（24 点网格）三点对齐。
- full_review L25（R15）：三列登记与 rationale L29/L31、scheme L99 逐一对得上；行结构与其余 21 行口径表格式一致。
- 修改范围核实：文件 mtime 实测 rationale/scheme/full_review 均为 10-05 01:41:30，content/references 停留在 10-03（未动），与"外科手术式 4 处、content/references 零改动"声明一致；r1 verify 报告与 r2 findings 所引十余处未改点（R3 [23] 句、R5 [31]、R7 三步模型、R9 GR 1.1、R12 难点指针、C2 三组改写、C3 平均语义、C5/C6 指针与方位词等）逐一与当前磁盘文本吻合。05_review/critic-round-2-rationale.md（01:07）为本轮评审步骤自身产物、早于修改步；kb-methods-pack.md（03:11）与 gap-analysis JSON（03:31）为 r2 收尾之后管线作业所改——均非修改报告越权。
- 非阻断观察 2 项（不立案）：① reviewer V1 表"差分目标"行两个次要行号引用不准（content L31 实为 L51/L73、scheme L41 实为 L9），数值本身两章一致、判定不受影响，属 findings 文档行号小瑕疵；② scheme L45"顺磁相（320–340 K）差分基线"（基线扣除取远离 T_N 的子集，r1 既有文本）与 L49 修订后"顺磁相数据点 315–340 K（6 点）"为两个不同口径（基线区间 vs 数据点集），不矛盾。

## 总结

- 原问题 24 条：已解决 16 / 部分 1（R17，合规部分闭合）/ 未解决 0 / 豁免 7（R18、R19、N4、N5、CR-3、V2、V4，均有合理理由）。
- r1 靶子消化情况：8 项（R13–R20）全部处置——闭合/修复 4（R13 两轮 critical 独立取证闭合、R14、R15、R16），部分闭合 1（R17，InP(111)A 已闭合、两数值合规待核）；合规待核转文献专轮 2（R18、R19），维持人工裁决 1（R20 引用总量 40，零增减）。
- 新引入问题：无阻断项（2 项非阻断观察见上节，均不立案）。
- 遗留 critical：无。R13（Osumi[13] 0.3 eV）已凭 arXiv:2308.10117v2 全文缓存独立取证闭合；N1（arXiv:2406.02238）已按纪律登记为文献专轮最优先待核项、正文未被擅自改写，其潜在影响被"检索截至 2026 年 8 月"时限限定兜底，不构成本轮硬伤。

复核结论: 通过
