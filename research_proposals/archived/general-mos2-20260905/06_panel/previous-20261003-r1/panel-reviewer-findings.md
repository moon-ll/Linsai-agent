# 评审团定点核查——整体一致性视角（reviewer）

执行者：engine 亲审 ｜ 课题：general-mos2-20260905 ｜ 时间：2026-10-03
范围：跨章指标口径逐项对账、章节衔接、参考文献编号连续性、full_review 骨架语义（≤3000 字、主线论证链 + 衔接点 + 统一口径表、不含逐项处置记录）。

## 一、跨章指标口径对账表（通过项，供复核）

| 指标 | 各章数值与出处行 | 一致？ |
|---|---|---|
| 选择定则拟合 R² | rationale L149 三档（≥0.90 / 0.85—0.90 / <0.85）＝content L73(Q1) L63(目标二) L85 ＝scheme L15(指针) L129 L137 ＝full_review L3/L12 | ✓（full_review 指针落点错，见 RV-2） |
| 累积效率 η(N) | rationale L153 ＝content L63(目标三) L77(Q3) L85 ＝scheme L19 L137 ＝full_review L3/L15，公式单点 content L25（scheme L19 完整复述公式，见 RV-3 附带项） | ✓ |
| α_syn | rationale L151/L161 ＝content L37/L39/L65(目标四) L75(Q2) ＝scheme L65 L99 L125 L131 ＝full_review L13/L14；两档 0.15/0.30 与 2.1σ 换算复算吻合 | ✓ |
| 反演空间 r≥0.8 | rationale L125/L155 ＝content L51/L67 L79(Q4) ＝scheme L91/L117/L133/L137 ＝full_review L3/L16 | ✓ |
| σ_Ω≤0.15 | rationale L125（按 Ω_max 归一化）＝scheme L83—L87（16%×1.074≈17.2% 缺口显式）＝full_review L16；content L51/L79 缺 Ω_max 限定（RE-8/RV-5） | 部分 |
| Δt≤100 as | rationale L127/L155 ＝content L53/L67 L79 L87 ＝scheme L41/L55（四档单点）/L93/L103/L121/L137 ＝full_review L3/L17 | ✓ |
| 驱动参数 | 3.2 μm/0.388 eV/T₀=10.67 fs（复算吻合）；泵浦窗口双口径 1.25—2 eV（Peterka，rationale L17）vs 1.4—2.1 eV（本项目，scheme L33）＝full_review L24 | ✓ |
| 13 阶双口径 | 3.2 μm→5.04 eV（复算吻合）vs Peterka 0.62 eV→8.06 eV（13×0.62=8.06 吻合），rationale L33 括注已声明 | ✓ |
| 莫尔周期 | 1.35/0.61/7.07 nm、δ≈4.1%、δ²≈4.6θ²（复算全部吻合）：rationale L97/L99 ＝content L27 ＝full_review L20 | ✓ |
| 失谐点/魔角/采样点 | 0、±50、±100 meV（content L19/scheme L63）；θ≈1.1°±0.2°（scheme L25）；采样 ≥30（三处一致） | ✓ |
| CEP 链 | 380→150→59 mrad ↔ 645/255/100 as（复算吻合）：scheme L43/L45/L47 ＝full_review L25 | ✓ |
| 谐波范围 | 1.9—5.8 eV / 213—640 nm（5 阶 1.94 eV≈640 nm、15 阶 5.82 eV≈213 nm 复算吻合）：scheme L59/L107 ＝full_review L18 | ✓（L107 括注语境错，见 researcher RE-3） |
| 章节衔接 | rationale §3 四问 ↔ content §2.5 Q1—Q4 ↔ 七目标 ↔ scheme 九模块 ↔ full_review ①② | ✓（full_review 目标括注错位，见 RV-1） |

## 二、问题清单

### RV-1 [high] full_review 七目标括注与 content §2.4 错位
- 位置：full_review.md L6。
- 原文："研究内容将三项缺口组织为方向一→二→三与四问 → 七条目标（目标一映射、目标二协同、目标三累积、目标四—七反演三阈值）"。
- 对照：content §2.4 实际为——目标一 ΔN_ex 激子基线、目标二选择定则映射 R²≥0.90、目标三 η(N) 累积 R²≥0.85、目标四 α_syn 协同、目标五—七反演三阈值。括注整体错一位。
- 建议：更正括注。

### RV-2 [high] full_review 口径表灰区指针落点错
- 位置：full_review.md L12。
- 原文："R² < 0.85 时按 C₃、C₃v、D₃d 逐段重拟合并报告适用边界（灰区处置细节见研究内容 §2.1）"。
- 对照：研究内容 §2.1 无三档处置；content §2.6（L85）声明"在立项依据章第三部分第一问给出"，rationale L149 为单点定义处。指针自相矛盾。
- 建议：改为"（三档处置单点定义见立项依据 §3 第一问）"。

### RV-3 [high] α_syn 两基线 30% 分母切换规则循环指代、规则本体失位
- 位置：content.md L37 ↔ scheme.md L99。
- 原文：content L37"两基线相对差异超过 30% 时的分母切换与降级路径由方案章给出"；scheme L99"……以研究内容 §2.2 的定义为唯一口径；本节按该节引用，不重复展开"。
- 问题：两处互指而规则本体（几何平均 √(N_ex·N_tw)）只存在于 full_review 口径表 L13——正文两章均为悬空指针。这与上轮"§2.6 与 §3.3 指代"同类，但本次经三处对读确认构成循环。
- 建议：把规则写回声明的出处分 content §2.2（"分母切换为几何平均 √(N_ex·N_tw) 并重新报告"），scheme 指针即闭合；full_review 口径表保持。附带项：scheme L19 完整复述 η(N) 公式与 content §2.1 单点定义重复，顺笔改为按定义执行（公式只留 η(1) 代入步）。

### RV-4 [critical·已实证] references [8] 首作错挂 + 已刊称预印本（上轮问题未修）
- 位置：references.md L17；正文 rationale.md L51。
- 原文："[8] M. Taucer, arXiv:1808.09288 (2018)."；正文"Taucer[8]指出……"。
- 实证：05_review/.r2-refs-verify.json（arXiv API）作者链 Guilmot Ernotte; T. J. Hammond; Marco Taucer——首作为 Ernotte 非 Taucer；critic-round-2-references 实证已刊 Phys. Rev. B 98, 235202 (2018), doi:10.1103/PhysRevB.98.235202。本轮复核确认 **未修**（10 月 2 日 23 时修订遗漏）。
- 建议：条目改"G. Ernotte, T. J. Hammond, and M. Taucer, Phys. Rev. B 98, 235202 (2018); doi:10.1103/PhysRevB.98.235202"，正文具名联动改"Ernotte 等人[8]"。

### RV-5 [critical·已实证] references [22] DOI 死链（上轮问题未修）
- 位置：references.md L45。
- 原文："[22] C. Ma et al., Phys. Rev. Lett. 135, 166902 (2025); doi:10.1103/PhysRevLett.135.166902."
- 实证：.r2-refs-verify.json 中 [22] 长 DOI 查证记录为 "FAIL:"；critic-round-2-references 双源比对确认长式为死链、真身 10.1103/kskc-qlb3（并告诫勿按格式规则重构 APS 短 DOI）。本轮复核确认 **未修**。
- 建议：DOI 字段整串替换为 10.1103/kskc-qlb3，不改其他字段。

### RV-6 [medium] references 研读基础凡例与正文实况失真
- 位置：references.md L87。
- 原文："研读基础：[2]–[7]、[10]、[14]、[18]–[21]、[27]、[29]–[33]、[36]–[38]、[41] 等条目……不参与逐条编号引用。"
- 问题：上述编号中 [10]、[14]、[18]、[19]、[20]、[21]、[27]、[29]—[33]、[36]—[38]、[41] 现均已在正文以 [N] 引用（10 月 2 日深夜补挂 [18][36] 等后未回改凡例）；程序化核对实际未被正文引用的仅 [2]、[7]。
- 建议：凡例改为"[2]、[7] 为 HHG 早期实验背景……不参与逐条编号引用；论证主链由其余 39 条直接承担"。

### RV-7 [medium] full_review 混入逐项处置记录语（骨架语义越界）
- 位置：full_review.md L6。
- 原文："……立项依据 §2.4 与研究内容 §2.6 改指代；方案章 §5 不再复述同一规则。……正文不把研究内容中的问题表述与方案中的参数流程重复展开。"
- 问题："改指代/不再复述/不把……重复展开"是修订处置记录语，非"全文骨架"语义（骨架应为：主线论证链 + 章节衔接点 + 统一口径表）。骨架正文 2385 字 ≤3000 ✓，其余部分语义合规。
- 建议：改写为内容级衔接陈述（如"Δt 级联降级单点定义于方案章 §3.3 末段，立项依据 §2.4 与研究内容 §2.6 按该口径指代引用"；研究内容/研究方案的分工陈述句替代元话语）。

### RV-8 [medium] content σ_Ω 口径缺失（同 researcher RE-8，跨章视角立案）
- 位置：content.md L51、L79。
- 建议：两处补"（按 Ω_max 归一化）"，与 rationale L125、scheme §4 三步映射、full_review 口径表闭合。

### RV-9 [low] references 作者列体例不一
- 位置：references.md [26]（全列 4 人）、[33]（全列 4 人），其余条目均为"首作 et al."。
- 建议：统一为"首作 et al."（critic-round-2-references 问题 6 的低优先项，随本轮顺笔处理）。

## 三、参考文献编号连续性核对

- [1]—[41] 编号连续、无跳号、无重复；正文引用的全部编号（展开 37 个）均在 references.md 有条目 ✓。
- 正文引用编号与条目对应抽查：[15] Peterka、[22] Ma、[24] Zhong、[25] Liu(陆)、[28] Patra、[29] Molinero、[31] de Almeida、[34] Chiu、[35] Luu&Wörner、[37] Bondy、[38] Serov、[40] Gao、[41] Csizmadia——人名↔条目一致 ✓（round-9 重排后未漂移）。
- 格式：期刊类"作者, 期刊 卷, 页 (年); doi:…"统一 ✓（[8][22] 除外，见 RV-4/RV-5）。
