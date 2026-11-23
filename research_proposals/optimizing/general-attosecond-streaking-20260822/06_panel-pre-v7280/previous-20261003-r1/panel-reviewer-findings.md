# 评审团定点核查 findings——整体一致性视角（reviewer）

课题：general-attosecond-streaking-20260822 ｜ 执行：engine亲审 ｜ 日期：2026-10-03
核查方式：关键指标逐章 grep 对值 + 独立复算；引用编号双向核对；full_review 语义与字数复核。

## 问题清单

### REV-1 [high] 截面数据库口径：ASD 误称复发（历史 critical，上轮仅改 rationale 侧）
- 位置：scheme.md L82、L100、L130 ↔ rationale L9/L81、content L43、scheme L49
- 原文：L82「NIST 电子电离数据库 ASD（Atomic Spectra Database）Xe 4d 与 Kr 3d 光电离子表」；L100「NIST 光电离数据库 ASD（Atomic Spectra Database）」；L130「对照 NIST 光电离数据库 ASD」
- 问题：同一标定任务两套库名并存（XCOM/FFAST vs ASD）；ASD 系原子光谱能级库、不含光电离截面，"光电离数据库 ASD/电子电离数据库 ASD"均为误称，L82"光电离子表"系病句。05_review/critic-round-2-rationale.md 问题 1（critical）曾立案，本轮 scheme 三处原样残留。
- 建议：三处统一为「NIST 光电离截面库（XCOM）、FFAST 等截面数据库」，删除 ASD 误称与病句。

### REV-2 [high] 备选路径 A 启用口径：rationale 数值错挂
- 位置：rationale.md L97 ↔ scheme §6 L130 ↔ full_review 统一定义表
- 原文：rationale「30%–50% 为失效边界验证区，对应多通道贡献（截面占比）约 30% 的通道混合度判据；若超界则启用备选路径 A。」；scheme「通道混合度大于 30%，对应多通道贡献约 40%」；full_review「40% 启用备选路径 A，40%–50% 降级运行」
- 问题：scheme 与 full_review 口径一致（混合度 30% ↔ 贡献约 40%）；rationale 把 30% 挂在"多通道贡献（截面占比）"名下，与映射表冲突（30% 是混合度值、对应贡献约 40%）。
- 建议：rationale 改为「备选路径 A 的启用判据为通道混合度大于 30%（对应多通道贡献约 40%，映射见研究方案 §6）」。

### REV-3 [medium] "通道重叠度"与"多通道贡献"同量异名残留
- 位置：scheme.md L69（"分组变量为能区与通道重叠度……通道重叠度以多通道贡献占总截面的百分比表征"）、§3.3 表头 L71「通道重叠度档位」、L86「通道重叠度超过 50%」；full_review L7「R3 以能区与通道重叠度为双变量」、L29 表行「通道重叠度 >50%」
- 问题： rationale/content 已统一"多通道贡献（截面占比）"，scheme §3.3 与 full_review 另用"通道重叠度"（虽原地定义桥接，仍属历史 critical 异名问题的残余）；"谱重叠宽度（eV）"是另一物理量，不受影响。
- 建议：上述五处统一为"多通道贡献"。

### REV-4 [low→复核不立案] rationale L85 章内指针复核
- 位置：rationale.md L85
- 原文：「其 2% 设计阈值的来源与标定计划在研究内容 §2.3 与研究方案 §4.1 分项给出」
- 复核更正：初查误录为 §2.2；现行指针实为 §2.3（R2 研究内容），该节确含"残余大于 2% 启用第二级"判据并经"见目标 G2"指针链至量化来源（§2.5）与 scheme §4.1，指针链有效。
- 处置：不改动。

### REV-5 [medium] scheme §1 "三层定义"对应关系错置（历史"术语孤岛"残余）
- 位置：scheme.md L7
- 原文：「三层的划分与研究内容 §2.2 三个研究方向对应：R1 多通道修正、R2 偶极相位解耦、R3 跨能区标定。」
- 问题：三层（算法适用 8%–50%/实验验证 15%–30%/可行性论证 8%–15%）是 R1 参数空间内的分层，与 R1/R2/R3 三个研究方向无对应关系；且 content 全章不用"三层"术语（用三亚区：线性响应/主检验/失效边界），跨章断链未真正闭合。
- 建议：改为「三层的划分以研究内容 §2.2 中 R1 工作区间（8%–50% 三亚区）为坐标」，并在各层后括注对应亚区名（主检验区/线性响应区）。

### REV-6 [medium] full_review 衔接点指针错误："三层定义由 content §2.2 给出"
- 位置：full_review.md L11
- 原文：「三层定义由 content §2.2 给出，其他章节以指代衔接。」
- 问题：content §2.2 无三层定义（只三亚区）；定义首现处为 scheme §1。
- 建议：改「三层定义由 scheme §1 给出（对应 content §2.2 三亚区），其他章节以指代衔接」。统一定义表"多通道贡献百分比"行出现章节"content §2.2/G1、scheme §2.2"同步改"方案 §1/§2.2"。

### REV-7 [medium] full_review R2 兑现句靶材挂错
- 位置：full_review.md L13
- 原文：「R2 的 2% 压制与 5% 可比性由实验部分（氦/氖/甲烷/氮气梯度靶材、16 通道 TOF 角积分）承担」
- 问题：甲烷/氮气是 R1 主检验靶（scheme §3.1）；R2 主靶为氩/氪、对照氦/氖（scheme §3.2）。衔接点表把 R1 靶材挂到 R2 名下。
- 建议：改「（氩/氪主靶与氦/氖对照靶、16 通道 TOF 角积分）」。

### REV-8 [medium] full_review "100 eV 物理依据"出处过宽
- 位置：full_review.md L13
- 原文：「100 eV 二级修正启用阈值的物理依据（IR 半周期内光电子累积偶极相移约 1 rad 动能上限）由 content K2 与 scheme §3.2 分别给出」
- 问题：content K2 只给阈值与"压制效率拐点"语义；"约 1 rad"物理依据仅在 scheme §3.2。同句"标定路径与时间节点"中，scheme §4.1 只给标定路径与所属研究阶段，无时间节点。
- 建议：改「100 eV 二级修正启用阈值由 content K2 给出，物理依据（……）见 scheme §3.2」；「时间节点」改「所属研究阶段」。

### REV-9 [low] full_review "≥5pp/≤2pp" 与正文中文表述混用（历史 medium 复发）
- 位置：full_review.md L7、L29 表行 ↔ content G3 L65「不小于 5 个百分点 / 不大于 2 个百分点」
- 建议：骨架镜像正文中文表述（两处）。

### REV-10 [low] full_review 统一定义表两处出现章节过期
- 位置：full_review.md L31（N₂ 行「content K2、scheme §3.2」——现行 content K2 已无 N₂ 换算，N₂ 出现于 scheme §3.2/§4.2）；L28（Auger 行「content §2.1、scheme §3.3」——content §2.1 仅述 Hasan 发现、无门控处置表述，处置仅在 scheme §3.3）；同表"时域门控窗口"与 scheme"时间门控窗口"用词不一。
- 建议：N₂ 行出现章节改「scheme §3.2/§4.2」并删"（两处一致）"；Auger 行改「scheme §3.3」、"时域门控"改"时间门控"。

### REV-11 [low] 检索库范围正文子集与表尾 canonical 不齐
- 位置：content L39（缺 CrossRef）、scheme L154（缺 IEEE Xplore、CrossRef）↔ references L97 canonical
- 建议：两处对齐 canonical 五库；rationale L71 为国内文献专项检索（含 CNKI/IOPscience），保留并记录理由。

## 核查通过项（无需改动）
- 水窗能区 284/409.7/543 eV、极紫外 50–150 eV、中点能量 100/346.85/476.35 eV（复算）：全章一致。
- R1 判据：15%–50% 误差 >20%→<5%、降幅 ≥4 倍（复算 20/5=4）、8%–15% 辅助判据 <5%、K1 残差 <5%、λ 拟合 <5%（2π 归一）、G1 时间抖动 <25 as：rationale/content/scheme/full_review 一致。
- rACE 交叉验证基准点约 10%（rationale L97/content L27/scheme §3.3 表/§4.1）：一致。
- R2 判据：2% 设计阈值、0.5%–3% 残余范围、可比性 <5%、二级修正启用 100 eV（N₂ 115.6 eV、Ar 换算 116–150 eV，复算通过）：一致。
- R3 判据：合格阈值 5%、主检验差值不小于 5 个百分点、失效边界差值不大于 2 个百分点、失效边界 >409.7 eV 或贡献 >50%、备选路径 C 偏差 >10%：一致。
- 探测链：16 通道 TOF、400 eV 处 4 eV、ΔE/E≈1%、重叠宽度 0.5–2 eV 与能量差 ≥0.5 eV 适用条件、IR 场强 10⁹–10¹⁰ W/cm²（Up<1 eV，首现 scheme §1）：一致。
- 靶材-档位映射：氦（单通道）/氖-氩（XUV 8%–15%、水窗 <5% 单通道档）/甲烷-氮气（15%–30%）/氪-氙（高段）：content §2.4 与 scheme §3.1–§3.3 已收敛一致（历史 critical"氖档位三方矛盾"未复发）。
- 参考文献：编号 1–40 连续、正文 [N] 89 次全部落在条目、40/40 条目均被正文引用（无孤儿）；[38]† 标记已补；APS 长短 DOI 混排系出版方注册形态（references-critic-2 结论），不动。
- full_review 语义：仍为"主线论证链+章节衔接点+统一定义表"三段骨架、无逐项处置记录残留；字数 2991 ≤3000（修改须控增量）。
