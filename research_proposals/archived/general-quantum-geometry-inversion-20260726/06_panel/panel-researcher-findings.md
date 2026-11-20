# 评审团定点核查（researcher·科学内容，第二轮）

课题 general-quantum-geometry-inversion-20260726 ｜ 视角：科学正确性 / 引用真实性 / 创新增量 ｜ 2026-10-05
核查方式：通读 5 章节；对 r1 复核报告（previous-20261003-r1/panel-verify-report.md）遗留靶子逐条定点核查；对关键文献断言在 `knowledge/wiki/papers/`（含全文级蒸馏页）与 `knowledge/raw/pdfs/_text_cache/` 中重新取证；不调用外部 LLM/CLI。行号以本轮修改前磁盘文本为准。

## 一、r1 遗留靶子核查（R# 编号对应修改报告处置总表）

- **R#①（r1 V4 残留）[medium] scheme.md:L99**：原文"检验单电子紧束缚框架在 $U/W \gtrsim 1$ 区间的失效点"。r1 复核已实查该处声称已改未改（3 处漏 1）。grep `gtrsim 1 区间的失效点` 全章 = 1（仅此一处；scheme:L161"外推失效点"为合法异义）。修改建议：统一为 content.md:L107/L159 既有口径"在 $U/W \approx 1.0$–1.2 区间的失效幅度"（与 §1.2 失效界 $U/W>0.5$、扩展验证区上沿 1.2 的衔接句 scheme:L3 一致，无数值冲突）。
- **R#④（r1 观察⑨）[low] content.md:L151**：原文"R4 自第 2 年二季度启动三项物理约束损失函数设计与 $\Sigma(U, T, \omega)$ 代理库预计算"与 scheme.md:L145"第 2 年一季度先完成 U 步长 0.15 eV 的粗档……第 2 年二季度完成 U 方向加密至 16 点的全档"存在季度级措辞张力（粗档先行于 R4 正式启动前一季度）。修改建议：把 content:L151 的预计算表述对齐 scheme §5.1 时间线（"按研究方案 §5.1 时间线先行：第 2 年一季度完成粗档、二季度完成全档"），损失函数设计仍自二季度启动。
- 其余 r1 靶子（②C6 残留、③V16/03_method 交接、⑤[4] 卷期）分属 critic/reviewer 视角，见 panel-critic-findings.md C2-1、panel-reviewer-findings.md V2-3/V2-4。

## 二、r1 待核清单（T1–T8）KB 重查结果

- **T2 [low，KB 有据，改] rationale.md:L11**：原文"Jiang、Holder 与 Yan 2025 年[6]综述把量子度规在非线性光学、亚阈值响应与非线性输运三类体系中的入口形式统一到同一几何张量语言下"。KB 页 `2025-2503_04943-revealing-quantum-geometry-in-nonlinear-quantum-materials.md`（全文级蒸馏）证实该综述的三区制分类为"非线性光学 / **亚带隙（subgap）响应** / 非线性输运"（该页 L23/L47/L52 三处一致），无"亚阈值"分类名。修改建议："亚阈值响应"→"亚带隙响应"。
- **T3 [medium，KB 有据，改] content.md:L41**：原文"Silva 等提出的半导体 Wannier 方程（SWE）把 1RDM 在实空间 Wannier 基下演化……"具名不精确且无 [N]。KB 全文缓存 `raw/pdfs/_text_cache/2510_22064.txt` 证实：题名 *Semiconductor Wannier equations: a real-time, real-space approach to the nonlinear optical response in crystals*，作者链 Eduardo B. **Molinero**（第一作者）, Bruno Amorim, Misha Ivanov, …, Rui E. F. **Silva**（末位通讯，†）；摘要逐字证实"deriving the equations of motion for the electronic reduced density matrix in a localized Wannier basis"（正文"把 1RDM 在实空间 Wannier 基下演化"表述准确，无需改动）。因正文 [36] 亦以"Silva 等"指代 2018 年 Mott HHG 论文，此处具名"Silva"有与 [36] 混淆的误归属风险。修改建议：改为第一作者具名"Molinero 等[51]"，references.md 末尾新增 [51] 条目（† 预印本格式，arXiv:2510.22064，2025）。
- **T8 [low，KB 有据，改] content.md:L63 / scheme.md:L75 / scheme.md:L211**：三处将 [31]（arXiv:2512.23538）称为"综述"。KB 主页 `2025-2512_23538-fisher-information-as-an-operational-metric-for-structured-o.md`（全文级蒸馏）证实该文为纯理论/数值的**方法提出文**（该页自述"本文即方法提出文"；作者定位声明为"把 Fisher 信息确立为结构光领域的操作性诊断工具"），非综述。修改建议：三处"综述"改中性"工作"（"作为参数估计的操作性度量建立"的实质表述与 KB 相符，保留）。
- **T1 [待核延续] rationale.md:L9**："始于 2019 年后 Gao、Vignale 等度规偶极理论的系统性发展"仍无 [N]。KB [6] 页仅记"量子度规偶极（QMD, 2022-24）理论上预测并随后被实验验证"，未给出 Gao-Vignale 理论文的专门页；"2019 年后"起始点无 KB 直接支撑。按"不核实不改写"保留原文，移交真实检索轮。
- **T4 [待核延续] rationale.md:L21**："BSV……RIN 在最大压缩点附近的理论上限（50–200% 区间）……经典相干态相干极限（0.1% 量级）"。KB 未检索到 BSV RIN 上限来源；检索到的 2609.01359（低噪声 MIR 光频梳，RIN 0.0026%）属不同语境，不构成支撑或证伪。保留原文。
- **T5 [待核延续] rationale.md:L25/L49**：[11] "14–300 K""约 1.5–2°"。KB 页 `2025-s43246-025-00873-5-…` 仅摘要级（该页自记"材料中未给出具体数值，需读原文"），且 raw/pdfs/_text_cache/ 无该文全文缓存。保留原文。
- **T7 [待核延续] scheme.md:L47**："同位能律"。KB 无 1907.11134（Navarrete 2019）页面与全文缓存，术语无法核对。保留原文。
- **T6/R#③**：5%→3σ 换算约定声明与手册字段数同步，涉及越权目录 03_method/，见 reviewer findings V2-4。

## 三、r1 关键改写与新文本新鲜核查

- **S1 红移口径复测（通过，不改）**：grep `5–15%` 五章 = 0；"11 阶约 50 meV（约为该阶谐波能量的 1.7%）"口径存于 rationale.md:L23/L41/L43、content.md:L105 四处，content.md:L107 以"红移量级…作为定量参照"回指，full_review.md:L33 口径表行"项目自设检测门限"落点在位。KB 主页 `2025-2508_00296-tracking-doublon-holon-dynamics-…md`（全文级）逐项对应：红移幅度随阶数增大、11 阶达 ~50 meV ✓；5 阶及以上红移、3 阶 12 MV/cm 内不变 ✓；MIR 0.263 eV 实验 + tdDMFT ✓；红移机制为 doublon-holon 复合辐射相位受瞬时电子结构调制 ✓。数值自洽：11×0.263 eV = 2.893 eV，50/2893 ≈ 1.73% ≈ 1.7% ✓。
- **S2-1 [medium，改] scheme.md:L83**：[44]（arXiv:2602.13667）句尾"对应长波驱动下计量灵敏度提升的可计算估计"与 KB 页 `2026-2602_13667-strong-field-quantum-metrology-…md`（全文级）不符：原文的**四次方波长标度是条纹可见度衰减律**（ln V ∝ −λ⁴⟨(Δn̂)²⟩，相位压缩光在 λ≳1.5 µm 处可见度断崖式下跌），而暗端口 Fisher 信息增益与可见度构成 Heisenberg 约束下的**计量学二象性/权衡**（该页"计量学二象性"条：成像保真度与量子传感灵敏度互斥），原文无"长波驱动下灵敏度提升"结论。修改建议：尾句改为"可见度衰减—暗端口增益"权衡表述。主体句"在强场光电子全息干涉下建立 Fisher 信息标度律，给出全息条纹可见度的四次方波长标度与'暗端口'Fisher 信息增益机制"与 KB 相符（r1 S11 修复维持）。
- **S2-2 复测通过（不改）**：[12]（arXiv:2605.21925）KB 页逐条对应：归一化方差随压缩参数指数衰减（e^{-2r} 形式）、方差在 r_opt ≈ 1.6 处取极小、自标定 Heisenberg 见证、对模体积不确定性稳健（该页方法卡第 147/150 行）。[8]（arXiv:2403.15337）KB 页逐条对应：同平均强度 4–7 次谐波产额高 5–15 倍、光子数分布 0–2×10¹³/脉冲、1.6 µm/25 fs/单空时模式、±1 V/Å 亚周期涨落；2×10¹³ 光子 × 0.77 eV ≈ 2.5 µJ 换算自洽（rationale.md:L19）。[9]（arXiv:2605.28236）KB 页对应"量子涨落打破驱动场动力学对称性、产生经典禁戒谐波"（rationale.md:L21）。
- **S2-3 创新增量复测（通过）**：三维交叉点定位（rationale §1.6 收束段）、三独立指标判据空间（scheme §7.2）、CDW 相图统计覆盖密度对比（scheme §7.3，121+63 点 vs 单点）与 r1 验收态一致；本轮 [31] 定性修正、[44] 权衡表述精确化均不削弱创新成立（前者反而澄清"操作性度量"的方法论文性质，与 R2 用作判据锚点的定位更自洽）。
- **S2-4 [信息] V14 国内段 KB 线索**：rationale.md:L93 陆培祥组"量子轨道分离与…阿秒能量—时间映射框架"与 KB 页 `2026-2602_03199-quantum-trajectory-separation-and-attosecond-mapping-in-liqu…` 高度吻合，可作下轮真实检索轮补挂 [N] 的首选项；本轮按 r1 豁免口径不改、不补挂，其余四组断言（孟胜组 H₃S/TDAP、北大 CRB、上海光机所 5.2 keV、河北大学 helicity-resolved）KB 无直接命中页。

## 四、待核清单汇总（本轮新增 0，延续 5）

T1（S2 节）、T4、T5、T7 原文全部保留未动；V14 按 r1 豁免延续并附 KB 线索；[4] 卷期 CrossRef 回填（见 reviewer findings V2-3）。
