# 评审团 findings：研究内容视角（第二轮）

评审角色：researcher（科学正确性/引用真实性/创新增量）｜ 课题：general-ssh-weyl-20260920 ｜ 时间：2026-10-05

> 方法：通读 rationale/content/scheme/references/full_review 五章；r1 遗留靶子（R3/R5）在 knowledge/ 含 raw/pdfs/_text_cache/ 全文缓存重查；关键文献断言按 arxiv_id 在 knowledge/wiki/papers/ 逐篇核对。一切以磁盘当前文本与知识库文件为据，不调用外部 LLM/CLI。

## 一、r1 遗留靶子的本轮重查结论

### RS1 [high] R3 确证失实归属：[24] 全文不含"统计涨落 10-15%"（本轮修复）

- **位置**：content.md L33（§2.3 方向二指标段）；scheme.md L45（§2.2 Δκ 条目）；scheme.md L225（§5.2 创新点二）
- **原文摘录**：content L33"该阈值参照同类多带 SBE/TDSE 计算统计涨落基准（Avetissian 与 Mkrtchian[24]报告的多带跃迁矩阵元修正项统计涨落约为基线 10-15%）作统计依据"；scheme L45"阈值依据：Avetissian 与 Mkrtchian[24] 报告的多带跃迁矩阵元修正项统计涨落约为基线 10-15%"；scheme L225"Δκ 阈值依据来自 Avetissian 与 Mkrtchian[24] 多带跃迁矩阵元修正项统计涨落"
- **证据**：[24]（Avetissian 与 Mkrtchian, PRB 102, 245422, arXiv:2005.09449）全文缓存 `knowledge/raw/pdfs/_text_cache/2005_09449.txt`（993 行）实测：`fluctuation` 零命中、`%` 字符零命中、`10-15/10–15` 零命中——该文为解析理论框架文，不含任何统计涨落百分比报告。KB wiki 页（2005.09449.md）亦无"涨落/统计"记载。r1 因无全文缓存而"待核合规保留"，本轮全文缓存核验升级为**归属失实**。
- **severity**：high（rigor 为最弱维度 0.66；引文承载其不存在的数据属证据链硬伤）
- **修改建议**：三处解除 [24] 对"统计涨落 10-15%"的承载，Δκ ≥ 20% 的统计依据改为方向二自建的"大样本随机参数重复反演实测涨落上界"自检路径（即 r1 报告建议的重建方向）；[24] 保留在其真实贡献处（content L31 / scheme L27 的 Berry 曲率修正框架、scheme L193 原理成立性）。

### RS2 [medium] R5-② refs[14] arXiv 编号冲突确证（本轮修复）

- **位置**：references.md L31（[14] 条目）
- **原文摘录**："Phys. Rev. B 108, 214104 (2023); DOI: 10.1103/PhysRevB.108.214104; arXiv:2304.06697 [cond-mat.mes-hall]"
- **证据**：`knowledge/raw/papers/2024-2305.02025-topological-phase-detection-through-high-harmonic-spectrosco.md` 元数据 `arxiv_id: "2305.02025"`，标题与 [14] 完全一致（Topological phase detection through high-harmonic spectroscopy in extended Su-Schrieffer-Heeger chains），作者群一致（Bera, de Almeida, Bhattacharya 等）；而 `2304.06697` 在整个 knowledge/ 目录（wiki + raw）**零命中**。库内证据单向指向 2305.02025。
- **severity**：medium（编号不可反查即失去预印本定位功能；r1 遗留待核项之一）
- **修改建议**：refs[14] 改为 arXiv:2305.02025。外部 arXiv 页面为最终裁决源，但库内证据已单向闭合。

### RS3 [low] R5-① "[14] 30 fs 有效寿命窗口"仍不可核（保留原文，标待核）

- **位置**：scheme.md L49（§2.2 Δt 条目）；关联 content.md L33（"优于 SSH 边界态寿命已有定性结果给出的 30 fs 量级阈值"）
- **原文摘录**：scheme L49"Bera 等人报告的时域拟合精度对应约 30 fs 的有效寿命窗口"
- **证据**：KB [14] 页为摘要级（digest_level: abstract，has_pdf: false），无 30 fs/时域拟合精度记载；无全文缓存可查。本轮无法升级也无法证伪。
- **severity**：low（不与其它数值互斥，属"阈值依据暂不可溯源"）
- **处置建议**：保留原文，报告标"待核"；后续获取 [14] 全文后复核 30 fs 与 Δt ≤ 10 fs（取 1/3）依据链。

### RS4 [low] refs[26] 注"三次与五次谐波产额增强三个数量级以上"对五次谐波量级轻度过称（本轮修复）

- **位置**：references.md L55（[26] 条目注）
- **原文摘录**："三次与五次谐波产额增强三个数量级以上"
- **证据**：KB 2025-2510_01760 深读页实测："整体三次谐波产额增强超过三个数量级"（>10³ ✓）而五阶谐波"腔体增强 > 2 个数量级"（L138/§iv）。三次达标、五次为两个数量级量级。
- **severity**：low
- **修改建议**：改为"三次谐波产额增强三个数量级以上（五次谐波增强超过两个数量级）"。正文各处（rationale L43/L63"三个数量级增强"）仅指三次谐波，无需改动。

## 二、关键文献断言抽查（本轮抽样 6 处，KB 逐篇核对）

| 文献 | 正文断言位置 | KB 核对结果 |
|------|------|------|
| [16] Pilch（2508.16166） | rationale L35/L63、content L39、scheme L87 校核窗 | 相符：0.5 THz 窄带驱动、I3f∝If³ 严格幂律（微扰区）、线偏振最强/椭圆度单调衰减/圆偏振严格为零、Boltzmann 输运、峰值场 tens–135 kV/cm；scheme 校核窗 0.3–1 THz ⊃ 实验 0.5 THz，"tens of kV/cm"与实验最低场一致 |
| [26] Duan（2510.01760） | rationale L41/L43/L63、content L41/L81、refs[26] 注 | 相符：裸膜 I₃f∝I_f^2.3（近微扰）、微腔幂指数 0.9→0.5→0.3 渐降近饱和、三次谐波增强 >10³；仅 refs 注"五次谐波三个数量级"过称（见 RS4） |
| [18] Thakur（2609.06119） | rationale L39、content L39、refs[18] 注 | 相符：偏振面须垂直 Weyl 节点分隔轴才有效耦合手性（KB ④）；频混边频随电子-空穴退相干衰减可作"退相干时钟" |
| [25] Bharti（PRB 105, 155140） | scheme L61（δ_CD/T 预标定）、L99、L207、refs[25] 注 | 相符：Berry 曲率分量宇称（奇偶性）决定反常电流方向与谐波偏振；"预估翻转点偏差归一化量在 0.3 以上"句式上为本课题自估，不越权归属文献 |
| [20] Lorenzo（2508.15631） | rationale L25/L43/L59、content L5/L17/L21/L53/L67、scheme L41/L59/L165/L197、refs[20] 注 | 维持 r1 全文级核验结论：摘要口径"上限两个数量级" + 正文拓扑半金属相 7 次谐波约 3 个数量级，两级表述在新文本全部落位正确（"拓扑半金属相"仅存于 rationale L25 与 refs[20] 注，grep 复测） |
| [9] Bauer & Hansen（PRL 120, 177401） | rationale L21、content L27、refs[9] 注 | KB 无该文页（14 个数量级断言本轮无法在库内核对）；沿用 r1 覆盖核验记录，出版信息（PRL 120, 177401, 2018）自洽，三章口径一致（"最高增强达 14 个数量级"）。标注"KB 外断言，维持原判" |

## 三、科学正确性与创新增量复检（无需修改项）

- **数值自洽**：scheme L137"激子束缚能 ~60 meV 与光子能量 ~3 eV 相差约 50 倍"算术正确（R4 修复维持）；scheme L51"$X + Y + Z = 1 - \sigma_0/\sigma_{\text{full}}$，当 σ₀/σ_full < 0.05 时 X + Y + Z ≥ 0.95"公式链自洽且与 L123 嵌套差分定义一致；scheme L87 Δt=0.1 a.u. ≈ 2.4 fs 与 fs 级动力学分辨率需求相容。
- **机制表述**：content L39"该幂律指数本身为微扰标志，而非超长散射时间的指纹"与 [16] KB 页"微扰区立方标度/低场输运型非线性"边界一致，引用未越界。
- **创新增量**（复检维持 r1 结论）：三创新点相对 [9][12][13][14][20] 的边界表述（"区别于一维 SSH 与二维 Qi-Wu-Zhang toy 模型"等）在新文本未变动，无越界宣称。
- **自洽性观察（不立项）**：scheme L41 S_edge ≥ 0.2 的"体相贡献量级约 0.1、阈值取两倍"为量级推断式自标定，文内已声明"预留文献刊本核实后的修正余量"，表述诚实，不作问题立项。
