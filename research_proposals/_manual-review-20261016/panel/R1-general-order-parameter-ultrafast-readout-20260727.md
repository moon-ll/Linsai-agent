# R1 科学性评审 — general-order-parameter-ultrafast-readout-20260727

评审人：R1（领域资深 PI，凝聚态/强场超快方向）｜评审日期：2026-10-17｜输入：rationale.md / content.md / scheme.md / references.md 四文件全文 + P0 清单（14 条）。
注：任务单所写课题 ID 20260726 与实际不符，目录与 P0 清单均为 20260727，本报告按实际 ID 落盘。

## 总评分

**总评分：0.80**

| 维度 | innovation | feasibility | rigor | expression | completeness |
|---|---|---|---|---|---|
| 分数 | 0.83 | 0.75 | 0.78 | 0.80 | 0.85 |

**五项核查（rigor 定档）**：①数值链一致 ✓（P0 场强换算链修复后两端点全部闭合：1.5 mJ·100 fs·Ø1.3 mm→0.29 V/Å、Ø0.5 mm→0.76 V/Å；30 μJ·50 fs·Ø95 μm→0.80 V/Å、10 μJ·30 fs·Ø190 μm→0.30 V/Å；γ 端点 0.205/0.948 与"5 μm 下移 40%"、gμ_BB=0.81 meV、k_BT_N=63 meV、14 T÷(0.1–0.3 T/min)=47–140 min、σ×(1.5–2.0)=0.75%–1.6% 均复核通过）｜②指标定义可操作 ✓（G1 三子判据含旁证定位、G2 双判据、G3 三档双判据、δ/σ/σ_prior 三符号区分、FIM 7×7 定义齐备）｜③文献支撑真实 ✗（参考文献缩编 46→40 后编号未全链同步，新现 7 处错挂：Werner/Kravchuk/Mandal/Mizuno/Zhang 各挂错号）｜④逻辑闭环 ✗（σ"预研实测"与装置第 1 年搭建时间线矛盾；§三.2"半金属情景失效边界见 §三.3"指针落空）｜⑤模块自洽 ✓（温度旁证四文档同步、G2 与第 4 年出口"互不替代"声明一致；引用错挂已计入③不重复扣）。**过 3 项 → rigor 0.78**。

## 意见清单

[R1-01|critical] 引用编号错配（缩编重排新回归，非 P0 在册）｜scheme L83/L115（Werner=[15]，应 [11]；[15] 实为 Wang-Meng 相干声子文，scheme L45 处引 [15] 才是对的）；scheme L31（Kravchuk=[38]，应 [36]；[38] 实为 Mizuno）；scheme L75（Mandal=[27]，应 [23]；[27] 实为 Uzner-Neufeld 层间耦合）；content L35（Mizuno=[40]，应 [38]；[40] 实为 Grzybowski）；content L39（Zhang=[39]，应 [37]；[39] 实为 Yu）（③⑤）｜"Werner 等人 [15] 在 SOC 可忽略极限下的预言为此类通道提供提示性参照"（scheme §三.3 同名两处另引 [11] 正确，同文异号）｜按 references 表逐号改正后 grep 全文 [N] 复验；Werner 一文在 scheme 内同作者两号并存是最易漏检的回归点。

[R1-02|high] rationale｜§一.3 第一子问题段｜σ 来源时间线矛盾：装置第 1 年才"搭建并标定"，σ 却称"预研实测区间"，来源未交代（④）｜"σ 为本装置在零磁场条件下 CrSb HHG 谐波相对强度背景漂移的典型标准差，σ = 0.5%—0.8%（预研实测区间）"｜注明预研平台（合作装置实测或同类装置文献迁移估计），或改为"设计估值，第 1 年随装置信噪比标定一并定值"。

[R1-03|medium] scheme｜§三.2 末段→§三.3｜"半金属/窄隙情景的失效边界讨论见 §三.3"指针落空：§三.3 只有降场强预案，无金属情景 SBE 带内电流主导下的适用边界讨论（④⑤）｜"中红外 3—5 μm 驱动对应的光子能量落在带间激发可控区间，与 SBE 适用窗口的衔接及半金属/窄隙情景的失效边界讨论见 §三.3"｜在 §三.3 补金属情景处置段（带内电流主导时 SBE 适用性与 TDDFT 校验触发条件），或改指针至 §三.2 预案处。

[R1-04|medium] scheme｜§三.3 磁体段｜磁场差分时序成本未聚合：±7 T 切换 47–140 min，×72 个偏振方位角×2 场向，单温度全偏振扫描约 5–14 天连续机时，G2 总预算缺失（②）｜"±7 T 正反方向切换（含稳定时间）按 47—140 分钟量级规划实验时序（按 14 T 全变程 ÷ 变场率上下限计算）"｜给出 G2 三重扫描总时长预算与抽稀策略（方位角并档、正反场成对驻留复用、必要时场向定点抽测）。

[R1-05|low] content｜§二.3 自旋激发段｜27(2) meV 磁振子劈裂与谱仪分辨率约 20 meV 的张力未交代：若系动量维六重劈裂的自旋波拟合折算，应注明（③）｜"自旋波拟合给出能量劈裂 27(2) meV，能量维度受谱仪分辨率（约 20 meV）限制未直接分辨"｜补半句"27 meV 为动量维劈裂经自旋波色散拟合的折算值，非能量维直接分辨"。

[R1-06|low] rationale｜§一.4 主体系段｜CrSb T_N=733(4) K 高于常见文献值（约 705–723 K），正文宜注明测量口径差异，避免评审误判选择性引值（③）｜"该 733(4) K 定值由 Singh 等人 [22] 的极化中子衍射与磁化率测量共同标定"｜补一句与既有热力学/输运测值（约 705–723 K）的口径差异说明。

### P0 清单状态核对（评审必答）

| P0 条目 | 当前状态 |
|---|---|
| #1 content G1 温度旁证四文档两版 | **已修复待管线复核**（rationale §一.3 L47、content G1、scheme §三.1 L11 与 §三.3 L79 四处实体同步，且"外部锚点项不参与 G1 判定"定位一致） |
| #2 content §2.6"与 G2 口径一致"不实 | **已修复待管线复核**（改"此为第 4 年独立出口判据，与 G2 强度判据互不替代"） |
| #3 critical：低重频档场强换算 2.2–6.2 V/Å | **已修复待管线复核**（焦斑改 Ø0.5–1.3 mm，端点反推 0.29/0.76 V/Å 闭合，见①核查） |
| #4 高重频档反推 14–57 V/Å | **已修复待管线复核**（端点 30 μJ·50 fs·Ø95 μm→0.80、10 μJ·30 fs·Ø190 μm→0.30 闭合；"Ø70–250 μm"区间端组合未逐一限定，属低风险松口径） |
| #5 scheme/rationale 温度旁证半迁移 | **已修复待管线复核**（同 #1） |
| #6 §三.4"合理区间"未量化 | **已修复待管线复核**（"量级偏差 ≤ 10 倍（同 §二.6 第 4 年档）"） |
| #7 references [45] Yu 预印本滞留 | **已修复待管线复核**（[39] Yu 已升 npj Quantum Mater. 10, 47, 2025，DOI 10.1038/s41535-025-00766-3） |
| #8 critical：full_review 换算链端点差 4.1 倍 | scheme 端已闭合；full_review.md 不在本轮四文件范围，**待复核** |
| #9 骨架口径表 No-Go 与 G3 多峰归属两版 | content 已统一"多峰→边缘档"；full_review 骨架表不在本轮范围，**待复核** |
| #10 R1/R2/R3 审计代号 41 处 | **已修复待管线复核**（全换标定阶段/探测阶段/归因阶段实义名，rat 前向引用已改"归因层 G3"） |
| #11 anti_ai 超长句回潮 | content G1 判据句肉眼仍长，**需程序复跑** |
| #12 rationale §一.3 温度旁证缺句 | **已修复待管线复核**（L47 已补，与 G1 定义同构） |
| #13 references 46>40 | **已修复待管线复核**（现 40 条 ≤ 上限） |
| #14 [2] NbN 孤儿条目 | **已修复待管线复核**（现 [2] 为 Zhang TiSe₂ 且有挂靠） |

**注**：P0 在册 14 条中 11 条已实际修复（待管线复核），本轮科学性问题集中在缩编重排引入的新错挂（R1-01）——属同一病根（编号重排未做全文 grep 同步）的回归，修复成本极低但必须一次性全链完成。

**量化换算复核通过项（供对账）**：I=½cε₀E²（0.3 V/Å→1.2×10¹²、0.8 V/Å→8.5×10¹² W/cm²）✓；γ=ω√(2m*E_g)/(eE) 端点 0.205/0.948、5 μm 下移 40% ✓；Zeeman 0.81 meV/交换 63 meV ✓；B_SF≈√(2B_E·B_K) 框架及 ±B 迟滞预检设计合理 ✓；σ 折算 0.75%–1.6% ✓；FIM/贝叶斯先验 3 倍文献不确定度设计 ✓；g 波 𝒴₄₋³=zy(3x²−y²) 面内 sin3φ 节点 0°/60°/120° 与 d 波 cos2φ 节点 45°/135° 的互补扫描论证 ✓。

## 量化锚核实记录

1. **Tyulnev 2025 Commun. Mater. 6, 152 — TiSe₂ CDW 偏振不对称 3/5/7 阶谐波**：✅ 锚定成立。arXiv 原文（2409.04216）摘要："reveal an anisotropic component below the CDW transition temperature"，与申请书"CDW 相（约 200 K 以下）进入后才出现的各向异性谐波分量"一致。注意：arXiv 版标题含"Mott to Charge-Density-Wawk"字样（"High harmonic spectroscopy reveals anisotropy of the Mott to Charge-Density-Wave phase transition in TiSe₂"），references [1] 期刊版标题为"anisotropy of the charge-density-wave phase transition"，两版标题不一致，提交前按刊版一对一核对。URL: https://arxiv.org/abs/2409.04216
2. **Osumi 2024 PRB 109, 115102 — MnTe 非高对称动量点分裂 0.8 eV**：✅ 锚定精确成立。原文摘要："The magnitude of the splitting reaches 0.8 eV at non-high-symmetry momentum points, which is much larger than the spin-orbit gap of ~0.3 eV along the ΓK high-symmetry cut."与申请书引述完全吻合；另该文 T_N=307 K，申请书"约 310 K"量级一致。URL: https://arxiv.org/html/2308.10117
3. **Grzybowski 2023 PRB 107, L060403 — CoO 240 K 下 7.0 T 自旋翻转、迟滞至 30 T**：✅ 锚定精确成立。原文摘要："Below the Néel temperature CoO reveals a spin-flop transition at 240 K at 7.0 T, above which a hysteresis...unexpectedly persists up to 30 T."URL: https://arxiv.org/html/2109.00093v2
4. **Werner 2024 PRB 110, 235101（交错磁 HHG 两 SOC 极限）**：文献真实（多源确认卷期页），内容锚（弱 SOC 偶次谐波磁场依赖/强 SOC 高能峰与平台）与两课题引述一致；错挂问题见 R1-01。URL: https://doi.org/10.1103/PhysRevB.110.235101
5. **CrSb T_N=733(4) K、27(2) meV 手性磁振子劈裂、Terashima/Sankar/Mandal 等 2026 条目**：核心数据源均为 2025-11 后预印本/新刊文，本次真实检索范围不可核验，仅做内部一致性审查（自洽）；上线前按 references 自述规则一对一核对。
