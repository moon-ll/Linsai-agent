# 评审团 findings——researcher 视角（科学内容）

评审员：engine亲审（researcher 视角）｜ 课题：key-transient-quantum-phase-optical-20260726 ｜ 时间：2026-10-05

本轮为第二轮亲审。核查依据：五章节全文精读 + 第一轮复核报告（previous-20261003-r1/panel-verify-report.md）遗留项逐条处置 + 第一轮修改报告"遗留与风险"专项执行。文献核对来源：knowledge/wiki/papers/ 在档页 + knowledge/raw/pdfs/_text_cache/ 全文缓存（不访问外部网络，核对不了标"待核"，不下"伪造"结论）。行号为修前文件行号。

## 一、r1 遗留靶子处置（R# 编号对应 r1 修改报告 R13）

### R2-1｜Mokhtari [23] "实验标定"误标（新发现，HIGH）

- 位置：rationale.md L55
- 原文："Mokhtari 等[23]于 2026 年分析声子驱动的 HHG 退相干，给出 77–300 K 范围产率变化 15–30 倍的实验标定。"
- 证据：KB 在档页 wiki/papers/2026-2604_07543-phonon-driven-decoherence-of-high-harmonic-generation-in-the.md 明确记载：(a) 实验"于 77–500 K 宽温区系统测量……发现随温度降低谐波产额显著上升"；(b) "在 77 K 到 300 K 范围内，谐波产额随温度升高单调下降"；(c) **"由于实验最低温限制在 77 K，模型外推到液氦温度时预测高次谐波谱将有 15–30 倍的增强"**——15–30 倍是**一维链模型外推液氦温区的预测**，不是 77–300 K 实验标定值。
- 定性：与 r1 [21]（模拟误标"实验证据"）同类错标，实验量与模型外推量混写，rigor 直接受损。
- 建议：改为"实验测量 77–500 K 温区 HHG 产额随温度的显著变化（随降温显著上升），其一维链模型外推液氦温区预测产率增强 15–30 倍"；L109"低温（4–77 K）压制声子退相干"的使用逻辑不受影响（修正后反而获外推预测支撑），不改。

### R2-2｜McIver 2020 无参考文献条目（r1 R13 遗留，HIGH）

- 位置：rationale.md L35"McIver 等于 2020 年在石墨烯中观测到光致反常霍尔效应，建立固体中 Floquet 态的输运签名。"（具名无编号，表内无条目）
- 溯源（KB 定案）：wiki/papers/1811.03522.md（arXiv:1811.03522，deep-read，used_by_proposals 含本课题）记载：标题 Light-induced anomalous Hall effect in graphene；作者 J.W. McIver, B. Schulte, F.-U. Stein, T. Matsuyama, G. Jotzu, G. Meier, A. Cavalleri（MPSD）；正式发表于 Nat. Phys. 16, 38-41 (2020)，DOI: 10.1038/s41567-019-0698-y。正文断言与 KB 定性一致（"首次在真实固体中实现纯光致瞬态 Chern 绝缘体输运"——输运签名表述成立，且确为实验"观测到"）。
- 建议：补条目"McIver J.W., Schulte B., Stein F.-U., et al. Light-induced anomalous Hall effect in graphene. *Nat. Phys.*, 2020, 16: 38-41. DOI: 10.1038/s41567-019-0698-y"，正文补角标，全表按首现顺序重排（联动 V2-1）。

### R2-3｜[7] 的实验验证论文未入参考文献表（r1 R13 遗留，HIGH）

- 位置：rationale.md L21"Berry 曲率相关的圆偏振选择性由强场理论预言[7]并获实验证实"——"实验证实"悬空无条目。
- 溯源（一手定案）：(a) KB 主页 wiki/papers/2021-2109_15291-all-optical-probe-of-three-dimensional-topological-insulator.md（digest_level=fulltext）记载：Baykusheva et al., Nano Lett. 21, 8970-8978 (2021)，DOI: 10.1021/acs.nanolett.1c02145，"前期理论工作（Baykusheva et al. PR A 103, 023101 (2021)）已预言 CPL 驱动下 Bi₂Se₃ 表面态 HHG 的 unique 增强，本文是其实验验证"；(b) raw/pdfs/_text_cache/2109_15291.txt 原文引言亲证："In a recent theoretical work, we predicted a unique enhancement of high harmonics for a circularly-polarized driving laser fields from the surface state of a prototypical topological insulator system Bi2Se3 [30]. Here, we report experimental results."（其 [30] 即 PRA 103, 23101 (2021)＝本 proposal refs[7]）。
- 顺带定案（r1 修改依据复核）：[7] 理论预言定性经一手原文确认，r1 R1 修正无误。
- 建议：补条目"Baykusheva D., Chacón A., Lu J., et al. All-optical probe of three-dimensional topological insulators based on high-harmonic generation by circularly-polarized laser fields. *Nano Lett.*, 2021, 21: 8970-8978. DOI: 10.1021/acs.nanolett.1c02145"，正文 L21"并获实验证实"后补角标（联动 V2-1 重排）。

### R2-4｜Kiselev [36] 定性断言未经一手复核（r1 遗留，LOW→待核）

- 位置：scheme.md L83"Kiselev[36]在 2026 年用参数不稳定性机制给出：反转对称中心晶体的 IR-active 声子在 Mathieu 共振条件下被驱动进入稳定的非平衡破缺态，可在原本被禁戒的二阶非线性通道产生强 SHG。"
- 复查结果：KB 无该论文在档页（grep wiki/papers 无命中）；raw/pdfs/_text_cache/ 1297 个全文缓存按标题片段（dynamical breaking of inversion / nonlinear phonon + Mathieu）与作者名（Kiselev E.）检索均无命中（含 "Kiselev" 的 5 个缓存均为引用它的他文）。
- 处置：维持原文（年份/状态已按 r1 R7 以参考文献表口径定案），定性断言标"待核"，不凭记忆改写。r1 已记录同项，本轮确认仍无法一手核。

### R2-5｜de la Torre [31] 具体数值无在档佐证（LOW→待核）

- 位置：content.md L29"de la Torre 等[31]于 2025 年在热淬火 1T-TaS₂ 中证明 H-CDW 相可由 ~120 K/s 中等速率热淬火稳定到 210 K，且 C-CDW 与 H-CDW 共存于同一块体。"
- 复查结果：KB 无该论文在档页；Kim[30]（2608.02456）KB 页侧面佐证"2025 年 de la Torre 等 [Nat. Phys. 21, 1267-1274] 通过热淬火进一步确认动态相变路径"——论文身份与主题相符，但 ~120 K/s、210 K 两个数值无在档页可对。
- 处置：维持原文，标"待核"。数值口径跨章无复现（仅此一处），不构成一致性风险。

## 二、r1 修正项一手复核定案（本轮新增证据）

### R2-6｜[21] Batista 理论/数值定性——一手确认（复核通过）

- 证据：raw/pdfs/_text_cache/2604.27750.txt 原文：方法为 time-dependent density matrix (TDDM) formalism，"spectra are simulated for each time delay""numerical simulations, we used PCBs centered at 7.5 µm"；作者均为理论机构；摘要结论"establish harmonic helicity as a field-controlled observable rather than a direct material fingerprint"。r1 将"报道了实验证据"改"从理论上证明"无误，定案。

### R2-7｜其余 KB 抽查相符（抽查记录，无问题）

| 文献 | 断言位置 | 核对结果 |
|------|---------|---------|
| Ono[3]（PRB 110, 125111） | rationale L5 | KB 2608_24984 页记载"手性反转翻转曲率而不改变能带，纵向谐波相应改变"——与正文一致；数值预言定性一致 |
| Zhao[20]（arXiv:2511.13114） | rationale L53 | KB 页记载"+2%张应变使贝里曲率从 18.24 Å⁻²增至 26.86 Å⁻²（增加约 47%）""Py 强度……近乎翻倍"——数值逐项相符；模拟定性相符 |
| Watanabe[33]（2602.22578） | rationale L113 | KB 主页记载"强耦合极限下 g_θθ ∼ (t/U)² 被压制、而 Berry 相保持量化"“Z₂ SPT 部门匹配"——相符 |
| Ilin[25]（2604.20388） | rationale L57、scheme L143 | KB 页记载"电流-电流涨落关联函数……编码量子几何与拓扑""以 SSH 模型在单侧光学腔中的对偶体系为例""本文为纯理论工作"——相符（正文"率先验证"指 SSH 模型层验证，边界句已自限） |
| Faeyrman[11]（2606.02238） | rationale L31/L53、scheme L65 | KB 页记载 MgO、强 THz 场、复数 Berry 相实部（带内）/虚部（隧穿）分辨——相符 |
| Kim[30]（2608.02456） | content L21 | KB 页记载 MLFF（NequIP）MD、CCDW→NCCDW→ICCDW 两步、SoD 重排先于畸变塌缩——相符 |
| Lesko[14]（arXiv:2407.17917） | rationale L37 | KB 页仅证论文身份与主题（Hommelhoff 组，Floquet TI）；SHG 探测/手性翻转电流调制/TDDFT 细节无在档页佐证——标"待核"（low，不影响论证结构） |

## 三、其他观察（不改，记录）

### R2-8｜rationale L21 材料类指略宽（LOW）

- "拓扑绝缘体 Bi₂Se₃/Bi₂Te₃ 中……由强场理论预言[7]并获实验证实"——[7]（PRA，标题"三维拓扑绝缘体"）与新增实验条目 [8] 的实测体系均为 Bi₂Se₃（2109_15291 原文自述）。[7] 以类指三维 TI 成立，材料列举不构成错误；附 [8] 后语义自洽，不改。

### R2-9｜创新增量复核（复核通过）

- 三项创新（全光测量范式/写-读-反演闭环/物理约束 AI 反演）与现有工作的边界陈述（Uzan/Faeyrman 相位层→不变量层、Lesko/Jacobsen 无反演环节、Zhao[20] 模拟参考点非实测证据）经本轮全文复读无让渡、无误归；con L53"读出研究把分辨对象……"归属正确（r1 R3 复核确认维持）。
