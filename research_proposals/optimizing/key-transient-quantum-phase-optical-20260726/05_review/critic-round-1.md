# 对抗评审报告（第 1 轮 / 整体一致性审查）

> 评审角色：critic（红队 / 对抗式评审专家）
> 项目类型：重点项目（key）— 5 年期 / 300 万
> 评审标准：`memory/nsfc-standards.json` → `project_types.key`
>   - min_overall_score = 0.85，max_high_issues = 0，max_medium_issues = 2
>   - 评估焦点：创新性 0.25 + 系统性 0.20 + 战略意义 0.20 + 团队实力 0.15 + 研究基础 0.10 + 可行性 0.10
>   - writing_style_rules（重点）：必须连贯叙述/论述式研究故事，禁止文献堆砌 / bullet-list 罗列 / 模板化空话
> 评审日期：2026-08-04
> **本轮聚焦**：整体一致性审查 — 三章节之间逻辑衔接、术语一致性、内容冗余/矛盾（不逐段细审）
> 申请书文件：`04_proposal/sections/{rationale.md, content.md, scheme.md, references.md, full_review.md}`
> 评级基准：v0.5 (rationale) / v0.5 (content) / v0.8 (scheme) — 经过 round-8 修复后的当前状态

---

## 0 号任务：模块完整性检查（NSFC 重点项目 7 个标准模块）

| # | 模块 | 文件 | 行数/字数 | 实质内容 | 评级 |
|---|------|------|----------|----------|------|
| 1 | （一）立项依据 | rationale.md | 226 行 / ~19794 字 | ✓ 已实质撰写（v0.5，round-7 后重写） | OK |
| 2 | （二）研究内容 | content.md | 89 行 / ~19430 字 | ✓ 已实质撰写（v0.5，round-8 后重写） | OK |
| 3 | （三）研究方案 + 特色创新 + 预期研究成果 | scheme.md | 311 行 / ~43172 字 | ✓ 已实质撰写（v0.8，round-8 后重写） | OK |
| 4 | （四）特色与创新 | （合并在 scheme.md §5） | — | ⚠️ 与（三）合并，未独立 | [medium] 归属合并 |
| 5 | （五）年度研究计划 | scheme.md §6 | — | ✓ 独立小节（5 年，每年有子课题级目标+里程碑+可证伪标准） | OK |
| 6 | （六）预期研究成果 | scheme.md §7 | — | ✓ 独立小节（理论方法学/论文专利/数据集/人才培养/国际影响 五维量化） | OK |
| 7 | （七）参考文献 | references.md | 3 行 / 50 字 | ✗ **完全空置**（仅占位"待 writer 补齐"） — 正文引用 [5][9][20][21][32][33][34] 等全部悬空 | **[high] 缺失** |
| 附 | 团队/平台 | （无独立文件） | — | ✗ **缺失** — scheme.md 中提及"申请人所在团队已有装置"但无独立章节支撑 | [high] 缺失 |
| 附 | full_review.md | （无内容） | 3 行占位 | ✗ 占位 — 整体一致性审查尚未正式完成（本轮评审输出将填充） | [medium] 缺失 |

**完整性结论**：本轮对比 round-1 至 round-8 历次评审发现的"4 个标准模块空置"问题 — round-8 后已显著改善：
- ✓ （二）研究内容已实质撰写（round-8 的 [critical] 文件级重复问题已修复）
- ✓ （五）年度研究计划已独立成节（scheme.md §6）
- ✓ （六）预期研究成果已独立成节（scheme.md §7）
- ✗ （七）参考文献仍 50 字空置 — 这是 round-5/6/7/8 连续 4 轮 P0 列表中 100% 未执行的项目
- ✗ 团队/平台无独立文件 — 是 round-3 以来 P0 列表的常驻条目

申请书**实质可评模块 5/7**（71%），**较 round-8 的 3/7（43%）有显著改善**，但参考文献缺失意味着所有编号引用不可验证 — 这是整份申请书的"硬伤"。

---

## 综合评分

**0.71 / 1.00**

**结论：本轮整体一致性审查未达重点项目输出标准（阈值 0.85，差 0.14）。**

**根本原因**：
- (a) **3 个 [high] 跨章节不一致未修复**：第 3 年"哪个材料先反演 ΔC=1 跃变"内容.md 与 scheme.md 直接矛盾；AI 代理模型"何时启动预训练"内容.md 与 scheme.md 矛盾；MoS₂ "强非绝热区"分类与 ℏω/E_g 数值不自洽 — 这些都是 round-8 优化后仍然存在的章节间不一致；
- (b) **1 个 [high] 模块空置未修复**：参考文献 references.md 50 字占位，申请书所有 [5][9][20][21][32][33][34] 等编号引用全部不可验证；
- (c) **1 个 [high] 物理概念问题未修复**：SHG 偏振旋转作为 Bi₂Se₃（中心对称 R-3m）瞬态对称破缺的实时标志 — 体相 SHG 在反演对称下禁阻，round-3 指出至今 5 轮未修复；
- (d) **未发现任何 [critical] 级问题**（ΔC 数字、章节归属错位、章节空置等 round-8 级别的硬伤已修复）。

**质量阈值判定**：
- 综合分 0.71 < min_overall_score 0.85（差 0.14）
- **critical 级问题 0 个**（达标）
- **high 级问题 5 个** > max_high_issues 0（**未达阈值**）
- medium 级问题 4 个 > max_medium_issues 2（**未达阈值**）

**分数定位**：
- 相比 round-8（聚焦 content.md，0.48）：**+0.23** — 主要来自 (a) content.md 文件级重复已修复；(b) 章节实质撰写补齐；(c) ΔC 数字内部矛盾已消除；(d) scheme.md 已更新至 v0.8 修复多个关键 high 问题。
- 相比前一轮 scheme.md 聚焦评审（0.66）：**+0.05** — 主要来自 v0.8 多项修复。
- 但**本轮首次发现的 3 个跨章节不一致是 round-1~8 历次单章评审从未触及的问题**——分章节评审只检查"章内一致性"，没有章间对照检查；这是整体一致性审查的特有价值。

---

## 维度评分

| 维度 | 权重 | 得分 | 主要短板 |
|------|------|------|----------|
| 创新性（innovation） | 0.25 | 0.80 | rationale §2.3"第三级→第四级控制对象跃迁"是逻辑清晰的范式级创新（单体/外自由度 → 多体拓扑不变量）；scheme.md §5 给出 3 项方法学定位。但"统一对象 TQP"论证虽具说服力，**反观内容.md 与 scheme.md 都未在"瞬态量子相的可全光读写"这一创新点上做对比基准**——PINN（Physics-Informed Neural Network）做瞬态反演 / DeepEuler 做含时动力学 / 已有 Floquet-Bloch 含时 Wilson 圈方法在反问题上的应用，与本项目"分层反演"的关系未在 scheme.md §5 中做差异对比 |
| 可行性（feasibility） | 0.10 | 0.68 | (a) **SHG 触发 Bi₂Se₃ 物理不可行**（见 §IV.B 问题 B-1）——[high] 残留；(b) MoS₂ "强非绝热区"分类与判据数学不自洽（见 §IV.B 问题 B-2）——[high] 残留；(c) 第 3 年"哪个材料先 ΔC=1 跃变观测"两个章节给出不同答案（见 §IV.B 问题 B-3）——[high]；(d) ATA ≤250 as vs 抖动 ≤100 as 已在 scheme.md §2.2b 物理量切分（good fix）；(e) ΔC 误差预算 √合成 ≈0.113 在 scheme.md 与 content.md 一致（good fix） |
| 严谨性（rigor） | 0.20 | 0.62 | (a) **3 个跨章节一致性违反**（见 §III 一致性表）：第 3 年材料、AI 训练时间、MoS₂ 区域分类；(b) **references.md 完全空置** ——申请书所有编号引用（content.md 引用 [5][9][20][21][32][34]，scheme.md 引用 [5][21][32][33][34]）无法验证（[high]）；(c) ℏω/E_g ≥ 2 阈值在 content.md line 89 已补充"Rabi 振荡周期"物理论证（good fix），scheme.md §2.1a line 86 同步给出 T_L ≥ 2 T_intro（good fix）；(d) E_g 取体带隙 0.3 eV 已在 scheme.md line 88 明示（good fix） |
| 完整性（completeness） | 0.45 | 0.72 | (a) **（七）参考文献仍 50 字占位**（round-5~8 连续 P0 100% 未执行）；(b) 团队/平台无独立文件（round-3 以来 P0 常驻条目）；(c) 5 个实质模块（立项依据/研究内容/研究方案/年度计划/预期成果）质量高且互不重复；(d) full_review.md 3 行占位（本轮输出后将填充） |
| **综合分** | — | **0.71** | (0.80×0.25 + 0.68×0.10 + 0.62×0.20 + 0.72×0.45) / (0.25+0.10+0.20+0.45) ≈ 0.714 ≈ 0.71 |

---

## 一、修复确认表（跨章节追溯 → 当前 v0.5/v0.8 状态）

| 来自轮次 | 原问题 | 当前状态 | 评价 |
|---------|--------|----------|------|
| round-3 | [critical] content.md 与 scheme.md 文件级 184 行重复 | ✓ content.md 已重写为 v0.5（89 行独立"研究内容"） | ✓ 修复 |
| round-3 | [critical] ΔC ≤ 0.2 = 0.05+0.02+0.01+0.1 算术错误 | ✓ scheme.md §2.3b line 154 改为 √(0.05²+0.02²+0.01²+0.1²) ≈ 0.113；content.md line 43 同步改为 √ 合成 | ✓ 修复 |
| round-3 | [critical] 研究内容章实质空置 22 字 | ✓ content.md v0.5 已实质撰写（89 行 19K 字符） | ✓ 修复 |
| round-3 | [critical] 元数据错配（"聚焦（一）但位置在（二）"） | ✓ content.md 元数据已修正（"聚焦章节：（二）研究内容"） | ✓ 修复 |
| round-3 | [high] SHG 在 Bi₂Se₃ 上物理不可行（R-3m 中心对称） | ✗ scheme.md line 99 仍写"SHG 偏振旋转 [21] 作为瞬态对称破缺的实时标志信号"；content.md line 27 同步；rationale.md line 19/37 同样引用 [21]。**round-3 至今 5 轮未修复** | ✗ 残留 |
| round-3 | [high] ℏω/E_g ≥ 2 阈值未论证 | ✓ scheme.md §2.1a line 86 给出"T_L ≥ 2 T_intro"物理论证；content.md line 89 同步 | ✓ 修复 |
| round-3 | [high] MoS₂ 强非绝热区判据失效（4-8 μm 对 E_g≈1.8 eV 给 ℏω/E_g=0.086-0.17 ≠ 强非绝热） | ✗ scheme.md line 96 仍把"MoS₂ 等宽带隙二维材料"放在"4-8 μm 强非绝热模式"——但 MoS₂ 在 4-8 μm 下 ℏω/E_g ≈ 0.09-0.17 属于**深度准绝热**，与判据"≥2 准绝热 / ≤1 强非绝热"完全相反。**本轮首次在章间对照中浮出** | ✗ 残留 |
| round-3 | [high] ATA ≤250 as vs 抖动 ≤100 as 指标关系混乱 | ✓ scheme.md §2.2b line 123 明确切分两类物理量（脉冲时间基准不确定度 vs XUV 探测脉宽+探测器响应卷积） | ✓ 修复 |
| round-3 | [high] 圆偏振 HHG 时间分辨率"飞秒级"与 ≤100 as 指标冲突 | ✓ scheme.md §2.2b line 125 明确"不能参与 ≤100 as 项目级指标的瞬态拓扑演化时间分辨测量，而用作时间平均的 Berry 曲率投影测量" | ✓ 修复 |
| round-3 | [high] "推广"瞬态拓扑不变量—过度承诺 | ✓ scheme.md §5(1) line 218 改为"测量范式层面的扩展"；rationale.md line 215 注脚同步 | ✓ 修复 |
| round-3 | [high] "任何强场-阿秒可及体系"—绝对化 | ✓ scheme.md §5(2) line 222 改为"在测量范式层面可推广到多种强场-阿秒可及的量子材料体系" | ✓ 修复 |
| round-3 | [high] 泛函误差 ΔC~0.1 数字无来源 | ✓ scheme.md §2.3b line 152 给出"基于文献 [9, 20] 对 LDA/PBE/BEEF-vdW 泛函在 Bi₂Se₃ 平衡态 Berry 曲率计算的对比，泛函不确定性贡献量级 ~0.1" | ✓ 修复 |
| round-3 | [medium] "1–2 周"迭代周期未配 metric | ✓ scheme.md §1.2 line 60 明确"1–2 个日历周（包括数据存储、信号平均与数据分析时间）" | ✓ 修复 |
| round-3 | [medium] AI 训练样本 ~10⁵ 条来源未说明 | ✓ scheme.md §2.3a line 148 明确"100 动量点 × 1000 时间步 × 多参数扫描" | ✓ 修复 |
| round-3 | [medium] "（五）年度研究计划"未独立成文 | ✓ scheme.md §6（line 232-264）独立成节 | ✓ 修复 |
| round-3 | [medium] "（六）预期研究成果"未独立成文 | ✓ scheme.md §7（line 268-301）独立成节 | ✓ 修复 |
| round-3 | [medium] D1"数值连续性"是数学概念而非物理目标 | ✓ scheme.md §4 D1 line 188 改为"在交界处给出明确定义的转换规则" | ✓ 修复 |
| round-3 | [medium] D5 SHG/MCD 分离磁-拓扑机制未论证 | ✓ scheme.md §4 D5 line 202 补充"频段差（SHG 在 2ω，MCD 在基频）+ 对称性选择定则" | ✓ 修复 |
| round-3 | [medium] D6 VAE+扩散组合无文献支撑 | ✓ scheme.md §2.3a line 148 补充"本团队 2024 年开始在瞬态光谱反演中探索生成式架构（详见方法学手册 H 节中的技术交底路径）" | ✓ 修复 |
| round-5~8 | [high] references.md 占位符但全文引用 [5][9][20][21][32][33][34] 等 | ✗ references.md 仍 50 字空置 — **round-5/6/7/8 连续 4 轮 P0 列表 100% 未执行** | ✗ 残留 |
| round-5~8 | [high] 团队/平台章节缺失 | ✗ 仍无独立文件 — round-3 以来 P0 常驻条目 | ✗ 残留 |
| round-7 | [high] 国际竞争格局"4 家 vs 3 家"未统一 | ✓ rationale.md 已统一为 3 家（MIT Reis / MPQ Krausz / ELI-ALPS），分别在 §2.4 (line 51) 和 §4 (line 117) | ✓ 修复 |
| round-7 | [medium] ≤100 as 时序精度归属不清 | ✓ rationale.md line 75 已修复为"f-2f CEP + 反馈延迟线 + 双光梳（三重稳定）" | ✓ 修复 |
| round-7 | [medium] 强场量级从 10¹³-10¹⁵ 收窄到 10¹³-10¹⁴ | ✓ rationale.md line 3 已收窄 | ✓ 修复 |
| round-7 | [medium] §2.1/2.2 前人局限性 (a)(b)(c) 列表化 | ✓ rationale.md 已整合为叙述段（保留 3 个论点但融入论证流） | ✓ 修复 |

---

## 二、跨章节一致性审查（章间对照表 — 16 对核心要素）

| 对子 | 一致性 | 备注 |
|------|--------|------|
| §1. ΔC 误差预算：rationale §3.3 (line 87 "ΔC ≤ 0.05") vs content §2.3 (line 43 "≈0.113") vs scheme §2.3b (line 154 "≈0.113") | ⚠️ 需修订 | rationale line 87 给的是"1D-TDSE ground truth 校验精度"（仅 ground truth 层面），content/scheme 给的是"总反演误差"。**两个数字是不同物理量，但 rationale 没明示这一点** — 评审专家会误以为"团队精度 0.05 vs 总误差 0.113"是矛盾 |
| §2. ≤100 as 抖动：rationale §3.2 line 75 vs content §2.2 line 33 vs scheme §2.2a line 111 | ✓ 一致 | 三处均为"≤100 as RMS 作为项目级指标"，三重稳定结构（f-2f CEP + 主动反馈延迟线 + 双光梳）一致 |
| §3. ATA 时间分辨率：rationale 无明示 vs content §2.2 line 35 "≤250 as" vs scheme §2.2b line 119 "≤250 as" | ✓ 一致 | rationale 未提及 ATA 分辨率，不算矛盾 |
| §4. 圆偏振 HHG 角色：rationale §3.2 line 75 "作为子课题 B 的探测通道" vs scheme §2.2b line 125 "不能参与 ≤100 as 瞬态拓扑反演，而用作时间平均的 Berry 曲率投影" | ⚠️ 需修订 | rationale 说 HHG 是探测通道（无量化），scheme 说 HHG 不参与瞬态反演。**rationale 没明示"时间平均"角色**，未与 scheme 一致 |
| §5. Bi₂Se₃ E_g：rationale §3.1 (line 17 隐含) vs content §2.1 line 27 "LDA/PBE 计算的体带隙" vs scheme §2.1a line 88 "体带隙 E_g ≈ 0.3 eV" | ⚠️ 需修订 | rationale §3.1 line 17 提到"驱动光子能量 ℏω 与材料带隙 E_g 的比值（即绝热参数 ℏω/E_g）"，**但未明示 E_g 取体带隙** — content/scheme 都明示了 |
| §6. 第 3 年材料：content §4 line 69 "Bi₂Se₃ + 准绝热区首批三通道信号" vs scheme §6 line 247-250 "MnBi₂Te₄ 上的瞬态陈数 ΔC = 1 跃变首次被实验反演信号观测到" | ✗ **矛盾** | **content.md 第 3 年里程碑 = Bi₂Se₃ 首批三通道信号；scheme.md 第 3 年里程碑 = MnBi₂Te₄ 首次 ΔC=1 跃变观测。同一份申请书的两个章节给出不同的"年度旗舰成果"** |
| §7. 第 3 年 AI 训练：content §4 line 69 "AI 代理模型由 L0 解析样本开始预训练" vs scheme §1.3 line 70 "AI 代理模型微调（接续第 1 年的预训练）" vs scheme §6 line 237 "完成 α-T₃ 解析模型下的 1D-TDSE 反演流水线，启动 L0 解析样本（~10⁵ 条）的 AI 预训练" | ✗ **矛盾** | **content.md 第 3 年 = AI 预训练启动；scheme.md 第 1 年 = AI 预训练启动，第 3 年 = AI 微调。content.md 的 fix 注脚 (line 89) 自称"AI 预训练在第 1 年末完成"但 §4 表格仍写第 3 年** |
| §8. MoS₂ "强非绝热"分类：content §2.1 line 27 "MoS₂ + 强非绝热区" vs scheme §2.1a line 88 "强非绝热区 ℏω/E_g ≈ 0.5–1.03" vs scheme §2.1b line 97 "4–8 μm（强非绝热模式，MoS₂ 等宽带隙二维材料）" | ✗ **物理不自洽** | MoS₂ E_g ≈ 1.8 eV（Γ-K 直接带隙），4-8 μm 驱动对应 ℏω = 0.155-0.31 eV，**ℏω/E_g ≈ 0.086-0.17**（深度准绝热区，按 scheme.md §2.1a line 86 "≥2 为准绝热"标准）。**MoS₂ 在 4-8 μm 是深度准绝热，不是强非绝热** |
| §9. MoS₂ E_g 取值：rationale §2.3 (line 47) "MoS₂ 等"无明示 vs scheme §2.1b line 97 "宽带隙二维材料"无明示 vs methodology-manual (line 150 据 round-1 报告) "4-8 μm → 准绝热" | ⚠️ 概念漂移 | rationale/scheme 不明示 MoS₂ E_g；methodology-manual 承认判据冲突。**应在正文明示"MoS₂ 取 Γ-K 直接带隙 1.8 eV 时，在 4-8 μm 下 ℏω/E_g ≈ 0.09-0.17 不构成强非绝热"** |
| §10. 5 年期 vs 4 年期：rationale line 11 + content line 9 + scheme line 5 均为"5 年" | ✓ 一致 | ✓ |
| §11. 5 个核心靶材：rationale §1 line 5 + content §1 line 9 + scheme §1.1 line 16 均为"Bi₂Se₃、MnBi₂Te₄、Co₃Sn₂S₂、MoS₂、1T-TaS₂" | ✓ 一致 | ✓ |
| §12. 三家国际同行：rationale §2.4 line 51 "MIT Reis / MPQ Krausz / ELI-ALPS" vs rationale §4 line 117 "MIT Reis / MPQ Krausz / ELI-ALPS" | ✓ 一致 | ✓ |
| §13. ΔC=1 整数假设：rationale §3.3 (line 83) "ΔC=±1 的整数跳变" vs content §2.3 (line 43) "整数跃变（ΔC=1）" vs scheme §2.3b (line 156) "ΔC=±1 的整数跃变" | ✓ 一致 | ✓ |
| §14. ΔC 实用阈值 0.2 vs 总误差 0.113：scheme §2.3b line 156 "ΔC ≤ 0.2 是闭环成立的'实用阈值'...比预期总误差 0.113 略大，作为裕度" | ✓ 自洽 | ✓ |
| §15. SHG 在 Bi₂Se₃ 上：rationale §2.2 line 19/37 + content §2.1 line 27 + scheme §2.1b line 99 三处一致用 SHG 作为瞬态对称破缺标志 | ⚠️ 物理可行性问题（但三处一致） | **一致地错**——三章一致认为 SHG 可用，但 Bi₂Se₃ 中心对称 R-3m 体相 SHG 禁阻 |
| §16. 参考文献：rationale line 121-199 列 [1]-[39] inline（v0.5 末尾被截断为 line 199 "[39]"），content/scheme 用 [5][9][20][21][32][33][34]，references.md 50 字占位 | ✗ **完全缺失** | **申请书所有编号引用无对应的参考文献章节**，评审专家无法核实 |

---

## 三、术语一致性矩阵（13 项关键缩略词 / 物理量）

| 术语 / 物理量 | rationale 位置 | content 位置 | scheme 位置 | 一致性 |
|--------------|----------------|--------------|-------------|--------|
| TQP（瞬态量子相） | §1 line 3 隐含, §2.3 line 45 | §1 line 9 | §5(2) line 218 | ✓ |
| ℏω/E_g 判据 | §3.1 line 17 "绝热参数" | §2.1 line 25 + §3 Q1 line 55 | §2.1a line 86-92 | ✓ |
| 准绝热区 / 强非绝热区分界 | §3.1 line 17 "ℏω/E_g ≫ 1 / ≲ 1" | §3 Q1 line 55 "ℏω/E_g ≳ 2 / ≲ 1" | §2.1a line 86 "≥2 准绝热 / ≤1 强非绝热" | ⚠️ 阈值口径不一致 — rationale 隐含"≫1"，content/scheme 显式"≥2/≤1"。**可统一，但 rationale 应明示阈值数字** |
| ≤100 as 项目级指标 | §3.2 line 75 | §2.2 line 33 + §3 Q2 line 57 | §1.1 line 24 + §2.2a line 111 | ✓ |
| ATA ≤250 as 信号分辨率 | （未明示） | §2.2 line 35 | §2.2b line 119 | ✓（content/scheme 一致） |
| 圆偏振 HHG 角色 | §3.2 line 75 "作为探测通道" | §2.2 line 35 "Berry 曲率时间平均投影的多通道互补信号" | §2.2b line 125 "不能参与 ≤100 as 瞬态拓扑反演，而用作时间平均的 Berry 曲率投影测量" | ⚠️ rationale 表述弱化（"作为子课题 B 的探测通道"未量化时间分辨角色） |
| RT-TDDFT（实时 TDDFT） | §1 line 5 "A 子课题 RT-TDDFT" + §3.3 line 85 "RT-TDDFT" | §2.1 line 27 + §2.3 line 43 | §1.1 line 35 + §2.3a line 148 | ✓ |
| Floquet-Bloch / 含时 Wilson 圈 | §3.1 line 17 + §3.2 line 37 | §2.1 line 25 + §3 Q1 line 55 | §2.1a line 91 + §2.3a line 148 | ✓ |
| 分层反演 L0-L3 | （未提及） | §2.3 line 43 "L0 解析 / L1 代表体系全反演 / L2 关键时间点采样" + §3 Q3 line 59 "L0 解析 → L1 代表体系全反演 → L2 关键时间点 AI 采样" | §2.3a line 141-144 "L0/L1/L2/L3 全表" | ✓ |
| 三重稳定（f-2f CEP + 反馈延迟线 + 双光梳） | §3.2 line 75 | §2.2 line 33 | §1.1 line 24 + §2.2a line 111 | ✓ |
| VAE + 扩散模型 | （未提及） | §2.3 line 43 | §2.3a line 148 + §4 D6 line 206 | ✓ |
| 三家国际同行 | §2.4 line 51 + §4 line 117 | （未明示） | §4 line 117 同步 | ✓ |
| 国际路线图/装置 | §1 line 13 [38][39] arXiv:2604.15085 / arXiv:2601.09608 | （未引用） | （未引用） | ⚠️ rationale 单独引用路线图，content/scheme 未交叉引用 — 申请书前后缺乏对国际共识的统一指向 |

---

## 四、内容冗余与矛盾（重点）

### A. 冗余（同一信息在多处出现，需整合或交叉引用）

1. **5 年研究阶段表** 在 content §4（line 65-71）和 scheme §1.3（line 67-72）和 scheme §6（line 233-262）三处出现。content §4 强调"研究内容递进节奏"，scheme §1.3 强调"技术推进节律"，scheme §6 强调"里程碑"。**三处角度不同但内容重叠 ~70%**，评审专家读三遍同样内容会失去耐心 — [medium] 冗余。

2. **绝热分区判据** 在 rationale §3.1 line 17、content §2.1 line 25-27、content §3 Q1 line 55、scheme §2.1a line 86-93、scheme §2.3a line 148、scheme §6 line 235-243 共 6 处出现。**判定文字从 5-6 个角度重复**，且**判据数值口径不同**（rationale 隐含"≫1"，content 显式"≥2/≤1"，scheme 给"≥2 准绝热 / ≤1 强非绝热"）— [medium] 表述冗余+[medium] 阈值口径不一致。

3. **三家国际同行定位** 在 rationale §2.4 line 51 和 rationale §4 line 117 两处出现（同一份 rationale 内部），且 scheme §4 line 117 同步 — [low] 适度冗余。

4. **≤100 as 三重稳定** 在 rationale §3.2 line 75、content §2.2 line 33、scheme §1.1 line 24、scheme §2.2a line 111、scheme §4 D2 line 194 共 5 处出现 — [low] 必要冗余（不同角度论述）。

### B. 矛盾（同一信息在不同章节给出冲突表述）

**B-1 [high] SHG 在 Bi₂Se₃ 上物理不可行（残留 5 轮未修）**
- 位置：rationale §2.2 line 19 + line 37 + content §2.1 line 27 + scheme §2.1b line 99 — 三章一致地引用 [21] 主张 SHG 偏振旋转可作为瞬态对称破缺的实时标志信号
- 问题：Bi₂Se₃ 属 R-3m 空间群，具有反演对称中心（D₃d 点群），**体相 SHG 在反演对称下严格禁阻**（电偶极 SHG 选择定则）。虽然表面 SHG 因反演对称破缺可被允许，但 (a) 申请书没有区分表面 vs 体相 SHG；(b) 表面 SHG 信号量级通常比体相弱 2-3 个数量级，在 100 as 时间尺度上能否作为"实时标志"未论证；(c) [21] 的工作本身（Y. Shen et al., PRL 130, 086201, 2023）的样品体系与本项目 Bi₂Se₃ 是否一致未核实
- 修复：删除 SHG 作为"实时标志"的写法，改为"以 [21] 类似方法（适用于无反演对称的瞬态对称破缺检测）作为辅助手段"；或明示"我们仅在表面态 SHG 信号可用条件下作为标志，体相对称破缺检测改用其他手段（如 XRD 超快、瞬态反射率各向异性）"；或更换样品体系的 SHG 可行性论证（如对 MoS₂、1T-TaS₂ 是可行的，对 Bi₂Se₃ 体相需另行说明）
- action：**rewrite**

**B-2 [high] MoS₂ "强非绝热区"分类与 ℏω/E_g 数值不自洽**
- 位置：content §2.1 line 27 "MoS₂ + 强非绝热区"、scheme §2.1a line 88 "强非绝热区（ℏω/E_g ≈ 0.5–1.03）"、scheme §2.1b line 97 "4–8 μm（强非绝热模式，MoS₂ 等宽带隙二维材料）"
- 问题：MoS₂ 的直接带隙（Γ-K）E_g ≈ 1.8 eV（实验值 ~1.9 eV），间接带隙 ~1.2 eV。4-8 μm 驱动对应单光子能量 ℏω = 0.155-0.31 eV。**ℏω/E_g（用直接带隙）= 0.086-0.17，用间接带隙 = 0.13-0.26**。按 scheme §2.1a line 86 的判据（≥2 准绝热、≤1 强非绝热），MoS₂ 在 4-8 μm 下 ℏω/E_g ≈ 0.09-0.17 **位于深度准绝热区**（远小于 1，更不可能是"强非绝热"）。申请书把 MoS₂ 划入"强非绝热模式"是**与自身判据直接矛盾**
- 物理后果：MoS₂ 在 4-8 μm 下电子可在每个光场半周期内完成对本征态的多次跟随，本征态保持良好定义——按申请书自己的判据，这正是**准绝热区**的物理图像，用瞬时陈数即可。**但申请书第 2 年里程碑（scheme §6 line 241）声称要"完成 Wilson 圈反演的 ground truth 验证"——在准绝热区做 Wilson 圈反演是冗余的（瞬时陈数已足够），验证失去物理意义**
- 修复选项：
  - 选项 A：把 MoS₂ 调为准绝热区代表体系（与 Bi₂Se₃ 平行），用瞬时陈数反演；强非绝热区改用**真正宽带隙 + 短波长**的体系（如 h-BN 包封的 GaAs 双量子阱，但需重新论证）或**真正长波长**（如 12-16 μm CO₂ 激光器，团队是否具备？未说明）
  - 选项 B：明确改写判据：MoS₂ 在 4-8 μm 之所以选择 Wilson 圈不是因为物理上进入强非绝热，而是因为**二维材料的面外极化导致 Berry 曲率积分路径必须用环路相位描述**（这是几何原因，不是动力学原因）。需要重写 scheme §2.1a 的判据文字
- action：**rewrite**

**B-3 [high] 第 3 年材料里程碑两个章节矛盾**
- 位置：content §4 line 69 vs scheme §6 line 247-250
- content §4 line 69："第 3 年（读链路工程落地）... Bi₂Se₃ + 准绝热区首批三通道信号；AI 代理模型由 L0 解析样本开始预训练"
- scheme §6 line 247-250："第 3 年（代表体系验证）... 子课题 A：在 MnBi₂Te₄、Co₃Sn₂S₂ 磁性拓扑体系上验证 D5 风险层... 里程碑：MnBi₂Te₄ 上的瞬态陈数 ΔC = 1 跃变首次被实验反演信号观测到"
- 问题：同一份申请书的两个章节给出第 3 年完全不同的旗舰成果 — content 说"Bi₂Se₃ 首批三通道信号"，scheme 说"MnBi₂Te₄ 首次 ΔC=1 跃变观测"。**评审专家会问：到底是 Bi₂Se₃ 还是 MnBi₂Te₄？第 3 年到底验证哪个？**
- 物理可能性分析：两个主张可同时成立但需重写顺序 — 实际上 content 主张更合理（先 Bi₂Se₃ 建立 methodology，再用 MnBi₂Te₄ 验证磁性贡献）。但 scheme §1.3 line 70（"第 3 年: A: 磁性拓扑体系（MnBi₂Te₄、Co₃Sn₂S₂）"）已锁定 MnBi₂Te₄ 为第 3 年的子课题 A 主对象 — 这意味着 Bi₂Se₃ 在第 3 年没有 A 主导的内容（与 scheme §6 line 243 的"RT-TDDFT 前向模型在 Bi₂Se₃ 上建立并与 L0 解析样本交叉验证"是第 2 年里程碑）
- 修复：把 scheme §6 line 247-250 第 3 年里程碑改为"Bi₂Se₃ 首批三通道信号（与 content 一致）"，把"MnBi₂Te₄ 首次 ΔC=1 跃变观测"挪到第 4 年（与 scheme §1.3 line 71 "第 4 年: A: 关联相变体系" 同步的话，可以放在第 4 年的子课题 A 推进中）
- action：**rewrite**

**B-4 [high] AI 代理模型训练时间两章矛盾**
- 位置：content §4 line 69 vs scheme §1.3 line 67-72 + scheme §6 line 237-238
- content §4 line 69 第 3 年："AI 代理模型由 L0 解析样本开始预训练"
- scheme §1.3 line 68 第 1 年："基于 L0 解析样本的 AI 代理模型预训练启动"
- scheme §6 line 237 第 1 年："启动 L0 解析样本（~10⁵ 条）的 AI 预训练"
- scheme §1.3 line 70 第 3 年："AI 代理模型在 RT-TDDFT 数据上的微调（接续第 1 年的预训练）"
- scheme §6 line 249 第 3 年："AI 代理模型在 L1 的 RT-TDDFT 数据上完成微调"
- 问题：content.md §4 line 69 写"第 3 年 AI 预训练启动"，与 scheme.md 三处（第 1 年启动预训练）矛盾。content.md line 89 注脚写"AI 预训练在第 1 年末完成"但 §4 表格没改。**这是 content.md v0.5 重写时遗留的内部不一致**
- 修复：把 content.md §4 line 69 第 3 年改为"AI 代理模型在 L1 RT-TDDFT 数据上微调（接续第 1 年预训练）"，与 scheme.md 同步
- action：**rewrite**

**B-5 [high] references.md 完全空置（连续 4 轮 P0 100% 未执行）**
- 位置：references.md 3 行 / 50 字 vs rationale [1]-[39]、content/scheme [5][9][20][21][32][33][34] 引用
- 问题：申请书所有编号引用无对应文献清单 — **评审专家无法核实任何引文真伪**
- 修复：把 references.md 补齐为完整文献列表（至少 30-40 条），与 rationale/content/scheme 中的所有编号引用一一对应；按 NSFC 格式要求（期刊/卷期/页码/年份）规范化
- action：**rewrite（按 round-5/6/7/8 P0 要求 ≥ 500 字）**

### C. 表述精度问题（不构成矛盾但需说明）

**C-1 [medium] rationale §3.3 line 87 "1D-TDSE ground truth 校验精度已达 ΔC ≤ 0.05" 与 content/scheme "总反演误差 √合成 ≈0.113" 数字含义未区分**
- 数字含义不同（前者是 ground truth 校验精度，后者是总反演误差），但 rationale 没明示这一点。**评审专家可能误以为"团队精度 0.05" 与"申请书总误差 0.113" 是两个矛盾的指标**
- 修复：rationale §3.3 line 87 改为"1D-TDSE ground truth 校验精度已达 ΔC ≤ 0.05（仅 ground truth 层面）；含 RT-TDDFT 泛函误差、实验噪声、抖动、温漂的总反演误差预算约为 ΔC ≈ 0.113"

**C-2 [medium] rationale §3.2 line 75 说圆偏振 HHG"作为子课题 B 的探测通道"未量化时间分辨角色，与 scheme §2.2b line 125 "不能参与 ≤100 as 瞬态拓扑反演" 不一致**
- 修复：rationale §3.2 line 75 改为"圆偏振 HHG 作为 Berry 曲率时间平均投影的互补通道（不参与 ≤100 as 瞬态拓扑演化时间分辨测量）"

**C-3 [medium] rationale §3.1 line 17 ℏω/E_g 阈值口径与 content/scheme 不一致**
- rationale 写"ℏω/E_g ≫ 1（准绝热）/ ℏω/E_g ≲ 1（强非绝热）"，content/scheme 写"≥2 / ≤1"
- 修复：rationale 改为"ℏω/E_g ≥ 2（准绝热）/ ℏω/E_g ≤ 1（强非绝热）"，或说明"≫1 是定性描述，≥2 是本项目的工程阈值"

**C-4 [medium] rationale §3.3 line 83 vs scheme §2.3b line 156 — ΔC=1 vs ΔC≤0.2 阈值的"裕度"含义在两章表述不同**
- rationale 说"SNR ≈ 5/0.113 ≈ 44"；scheme 说"SNR ≈ 1/0.113 ≈ 8.8"；两处算法不同 — rationale 把 SNR 定义为"实用阈值 / 总误差"，scheme 定义为"整数跃变 / 总误差"。这是术语定义不一致
- 修复：rationale §3.3 line 83 改为"针对 ΔC=1 整数跃变的 SNR = 1/0.113 ≈ 8.8；针对实用阈值 ΔC ≤ 0.2 的 SNR = 0.2/0.113 ≈ 1.77"。明确 SNR 的两种定义场景

---

## 五、写作风格红线审查（重点）

按 `nsfc-standards.json` 的 `writing_style_rules`，本轮重点检查：

### 5.1 是否以科学问题为主线展开（vs 架构/方法先行）

| 章节 | 是否以问题为主线 | 评价 |
|------|------------------|------|
| rationale §1-§4 | ✓ 是 | 开篇直接抛出"瞬态量子相"作为统一对象，三大问题递进展开 |
| content §1-§5 | ✓ 是 | 引子"从单一现象走向统一对象" → 总体目标 → 子课题分解（按 Q1/Q2/Q3 映射） → 关键问题 → 5 年里程碑 |
| scheme §1-§7 | ⚠️ 部分偏离 | §1 系统级架构、§2 子课题技术方案、§3 子课题协同、§4 技术难点、§5 方法学创新 — 前 4 节是"方案先行"，§5 才是"科学问题上的方法学定位"。**重点项目标准下，"为什么做"先于"怎么做"的叙事顺序在 scheme.md 中倒置** |

### 5.2 是否存在"A 做了 X，B 做了 Y，C 做了 Z"式文献堆砌

- rationale §2.1-2.3：3 节中均有较密集文献引用，但每处引用都为论证服务（如 rationale §2.2 line 39 "前人工作的根本局限在于：..." — 论证流清晰，文献是素材）
- **轻度堆砌**：rationale §2.2 line 37 "Wang 等（Nature 2021）首次在固体中实验验证 Floquet 拓扑绝缘体[18]，而 McIver 等（Nat. Phys. 2020）展示了 Floquet 工程的光学控制[19]" — "X 做了 A，Y 做了 B" 句式，但这是 NSFC 综述标准格式，**不算严重问题**
- 评级：[low] 轻度

### 5.3 是否存在条目式罗列替代论证

| 位置 | 类型 | 评价 |
|------|------|------|
| rationale §2.3 line 43 "光学参数控制 / 外自由度控制 / 单粒子内态控制 / 多体内禀拓扑自由度控制" | 4 级 bullet | **已是叙述段形式**（"可分为四级"），round-7 修复后 bullet 已融入论证 |
| content §2.1 line 25 "(a)(b)" + line 27 "(1)(2)(3)(4)" | 编号列表 | 在叙述段中作为论证要素使用，**不算严重堆砌** |
| content §4 line 65-71 表格 | 5 年里程碑表 | **必要的进度表，不是论证替代** |
| scheme §1.3 line 67-72 表格 | 5 年技术节律 | 同上 |
| scheme §4 D1-D6 表 | 6 个技术难点表 | round-8 后已加入"攻关路径+备份方案"，**实质内容已在表中**，但**段落性过渡**（"按什么优先级排"）在 §4 开头一段已有论证，**达标** |
| scheme §2.3a line 141-144 L0-L3 表 | 分层反演 | 表后有 L1 / L2 段落性论证，**达标** |

### 5.4 段落之间是否有过渡、是否形成逻辑递进

- **rationale**：开篇 §1 → §2.1 → §2.2 → §2.3 → §2.4 → §3 → §4，每节之间有过渡句，叙事弧线完整（**优秀**）
- **content**：§1 → §2.1 → §2.2 → §2.3 → §2.4 → §3 → §4 → §5，每节有承接句（如 §2.4 line 47 "把三者割裂开来看..."），**良好**
- **scheme**：§1 → §2 → §3 → §4 → §5 → §6 → §7 — **段落间过渡较弱**：
  - §1 系统级架构 → §2 各子课题技术方案：缺乏过渡（§1 末尾是"统一的全光读写理论与实验体系"图，§2 直接进入子课题 A 详写）
  - §2 → §3：有过渡（§2 末尾"子课题间协同见 §3"）
  - §3 → §4：缺乏过渡（§3 末尾"三种协同机制"，§4 直接进入"D1 跨区衔接"）
  - §4 → §5：缺乏过渡（§4 末尾"D6 优先级安排"，§5 直接进入"瞬态拓扑不变量的全光测量范式"）
  - 评级：[medium] 部分段落缺乏过渡

### 5.5 研究内容是否围绕核心问题组织（vs 平行堆砌）

- **content §2.1-2.3** 子课题 A/B/C 严格对应 Q1/Q2/Q3（content §3 line 55-59 已建立显式映射）— **优秀**
- **content §2.4** line 49 "A → B → C 不是工程便利的分工，而是物理上的因果依赖：A 给出'瞬态相窗口在哪里、瞬态拓扑不变量应如何定义'的答案之前，B 没有合法时序扫描的目标" — **显式论证因果链**
- 评级：✓ 达标

### 5.6 研究方案是否说明"为什么选这个方法"（vs 只罗列步骤）

- **scheme §2.1a line 86-92 绝热分区判据**：先讲判据物理根据（T_L vs T_intro 关系），再讲具体驱动参数（Bi₂Se₃ 例子）— ✓ "为什么这样选"
- **scheme §2.2a line 111 ≤100 as 三重稳定**：明确说明三种稳定技术的物理含义切分（双光梳=长稳、f-2f=CEP 稳定、反馈延迟线=亚周期步进）— ✓ "为什么这样选"
- **scheme §2.3a line 139-148 分层反演策略**：明确说明"L1 全反演在算力上等价于对每个时间点做完整的贝叶斯优化...这是超算级任务" → 所以分层 — ✓ "为什么这样选"
- **scheme §4 D1-D6**：每个难点都有"攻关路径"段，说明"为什么这样攻关" — ✓ "为什么这样选"
- 评级：✓ 达标

### 5.7 综合叙事评价

| 章节 | narrative 总评 | 主要问题 |
|------|---------------|---------|
| rationale | **优秀**（4/5 分） | 全章节连贯叙事，文献服务于论证，三大问题递进清晰 |
| content | **良好**（3.5/5 分） | 子课题按问题线组织，因果链论证显式；但 §4 与 §5 之间的过渡较弱；§4 line 89 自我声称"按问题线先行"但 §4 表格本身是节奏表 |
| scheme | **中等**（3/5 分） | §1-4 偏方案先行，§5 才回到科学问题；§6-7 是项目管理层内容；段落间过渡较弱 |

---

## 六、事实核查表（跨章节数字一致性）

| 数字 / 论断 | 位置 | 一致性 | 评级 |
|------------|------|--------|------|
| 5 个核心靶材 | rationale §1 line 5 + content §1 line 9 + scheme §1.1 line 16 | ✓ 一致 | OK |
| 强场 10¹³–10¹⁴ W/cm² | rationale §1 line 3 + §3.1 line 17 + content §3 Q1 line 55 + scheme §2.1b line 97 | ✓ 一致 | OK |
| 近红外 1.5–2 μm + 中红外 4–8 μm | rationale §3.1 line 17 + content §2.1 line 27 + scheme §2.1a line 90-91 + §2.1b line 97 | ✓ 一致 | OK |
| ℏω/E_g ≥ 2 准绝热 / ≤ 1 强非绝热 | content §3 Q1 line 55 + scheme §2.1a line 86 | ✓ 一致 | OK |
| ℏω ≈ 0.6–0.8 eV (1.5–2 μm) | scheme §2.1a line 90 隐含 + line 97 | ✓ 物理正确（1.24/λ(μm) = 0.62-0.83） | OK |
| ℏω ≈ 0.15–0.31 eV (4–8 μm) | scheme §2.1a line 91 隐含 + line 97 | ✓ 物理正确（1.24/4-1.24/8 = 0.31-0.155） | OK |
| Bi₂Se₃ E_g ≈ 0.3 eV（体带隙） | content §2.1 line 27 + scheme §2.1a line 88 | ✓ 一致 | OK |
| MoS₂ E_g ≈ 1.8 eV（未明示但可推算） | （所有章节均未明示，仅说"宽带隙二维材料"） | ⚠️ 未明示 | [medium] 应补充 |
| ≤100 as RMS 项目级抖动 | rationale §3.2 line 75 + content §2.2 line 33 + scheme §2.2a line 111 | ✓ 一致 | OK |
| ATA ≤250 as 信号分辨率 | content §2.2 line 35 + scheme §2.2b line 119 | ✓ 一致 | OK |
| 阿秒条纹 ≤100 as 时间基准 | content §2.2 line 35 + scheme §2.2b line 120 | ✓ 一致 | OK |
| 圆偏振 HHG 时间分辨率 5-27 fs（光场周期级） | content §2.2 line 35 + scheme §2.2b line 121 | ✓ 一致 | OK |
| ΔC 总误差 √(0.05²+0.02²+0.01²+0.1²) ≈ 0.113 | content §2.3 line 43 + scheme §2.3b line 154 | ✓ 一致 | OK |
| ΔC 实用阈值 ≤ 0.2（闭环成立） | content §4 line 70 "分层误差 ≤ 0.2" + scheme §1.2 line 60 + §2.3b line 156 | ✓ 一致 | OK |
| SNR ≈ 8.8 针对 ΔC=1 | scheme §2.3b line 156 | ✓ 物理正确（1/0.113 ≈ 8.85） | OK |
| SNR ≈ 44 针对实用阈值 5/0.113 | content §2.3 line 43 "5/0.113 ≈ 44" | ⚠️ **算法 vs scheme 不同**：content 把 SNR 定义为"实用阈值/总误差"=5/0.113（5 = 项目级指标值），scheme 把 SNR 定义为"整数跃变/总误差"=1/0.113。两个数字都对，但定义口径不同 — 见 §IV.C-4 | [medium] |
| 团队实测抖动 ~120 as (RMS) | rationale §3.2 line 77 + scheme §2.2a line 111 | ✓ 一致 | OK |
| CEP 锁定 ≤ 200 mrad (RMS) | rationale §3.2 line 75 + content §2.2 line 35 + scheme §2.1b line 97 | ✓ 一致 | OK |
| 写脉冲 5×10¹³–10¹⁴ W/cm² + 30–50 fs | scheme §2.1b line 97 | ✓ 合理 | OK |
| AI 训练样本 ~10⁵ 条 | content §2.3 line 43 + scheme §2.3a line 148 + scheme §6 line 237 | ✓ 一致 | OK |
| 100 动量点 × 1000 时间步 | content §2.3 line 43 + scheme §2.3a line 148 + scheme §1.3 line 74 | ✓ 一致 | OK |
| L1 算力 10⁶–10⁷ CPU·h | content §2.3 line 43 + scheme §2.3a line 146 | ✓ 一致 | OK |
| 单次迭代 1–2 个日历周 | scheme §1.2 line 60 | ✓ 已给定义 | OK |
| 5 年内完成 3–5 个体系闭环 | content §4 line 71 + scheme §1.2 line 60 + §5(2) line 222 | ✓ 一致 | OK |
| MoS₂ 在 4–8 μm = 强非绝热区 | content §2.1 line 27 + scheme §2.1b line 97 | ✗ **物理不自洽**（ℏω/E_g ≈ 0.09-0.17 ≠ 强非绝热） | [high] B-2 |
| SHG 偏振旋转可作 Bi₂Se₃ 实时标志 | rationale §2.2 line 19/37 + content §2.1 line 27 + scheme §2.1b line 99 | ✗ **物理不可行**（Bi₂Se₃ R-3m 体相 SHG 禁阻） | [high] B-1 |

---

## 七、问题清单（按严重度 + 编号 + 位置 + 详见 + action）

### [high] B-1 SHG 在 Bi₂Se₃ 上物理不可行（5 轮残留）
- 位置：rationale §2.2 line 19/37 + content §2.1 line 27 + scheme §2.1b line 99
- 问题：Bi₂Se₃ 属 R-3m（D₃d）中心对称空间群，体相 SHG 严格禁阻。申请书三章一致地引用 [21] 主张 SHG 偏振旋转作为"实时标志信号" — 物理上**体相 SHG 不存在**，表面 SHG 信号弱 2-3 数量级，在 100 as 时间尺度上能否作为"实时标志"未论证；[21] 原文样品体系与 Bi₂Se₃ 是否一致未核实。**round-3 至今 5 轮评审反复标记，未修复**
- 修复：(1) 全文删除"以 SHG 偏振旋转 [21] 作为 Bi₂Se₃ 瞬态对称破缺的实时标志信号"表述；(2) 在 scheme.md §2.1b 改为"以瞬态反射率各向异性（time-resolved reflectivity anisotropy）作为对称破缺的触发信号 — 该方法对 Bi₂Se₃ 等中心对称材料的体相/表面态均敏感，不依赖偶极 SHG 选择定则"；或 (3) 改样品选择 — 第 1/2 年用 MoS₂（无反演对称，SHG 可行）+ 1T-TaS₂（CDW 熔化伴随对称破缺，SHG 强信号）作为"SHG 标志"代表体系，Bi₂Se₃ 的瞬态对称破缺检测改用其他手段
- action：**rewrite（3 章同步修改）**

### [high] B-2 MoS₂ "强非绝热区"分类与 ℏω/E_g 数值不自洽
- 位置：content §2.1 line 27 + scheme §2.1a line 88 + scheme §2.1b line 97
- 问题：MoS₂ 直接带隙 E_g ≈ 1.8 eV，4-8 μm 驱动对应 ℏω = 0.155-0.31 eV → ℏω/E_g ≈ 0.086-0.17。按 scheme §2.1a line 86 自家判据（≥2 准绝热、≤1 强非绝热），MoS₂ 在 4-8 μm 下应属**深度准绝热区**（远小于 1），不是"强非绝热"。申请书把 MoS₂ 划入"强非绝热模式"是**与自身判据数学直接矛盾**。物理后果：在准绝热区做 Wilson 圈反演是冗余的，scheme §6 line 241 第 2 年里程碑"MoS₂ + 4 μm 强非绝热区 Wilson 圈反演 ground truth 验证"失去物理意义
- 修复（选项 A，推荐）：**MoS₂ 调为准绝热区代表体系**（与 Bi₂Se₃ 平行），第 2 年里程碑改为"MoS₂ 准绝热区瞬时陈数反演 ground truth 验证"；**强非绝热区改用真正合适的体系**（如 h-BN 包封 GaAs 双量子阱或超长波 CO₂ 激光 12-16 μm 驱动的窄带隙拓扑材料），并补充该体系的 E_g 取值与 ℏω/E_g 数值证明其落入强非绝热区
- 修复（选项 B）：**改写判据**为几何因果（"MoS₂ 在 4-8 μm 选择 Wilson 圈不是因为进入强非绝热，而是因为二维材料面外极化导致 Berry 曲率积分路径必须用环路相位描述"），需重写 scheme §2.1a 的判据物理根据段
- action：**rewrite（需补充 1 个真正的强非绝热代表体系或重写判据）**

### [high] B-3 第 3 年材料里程碑两个章节矛盾
- 位置：content §4 line 69 vs scheme §6 line 247-250
- 问题：content 说"Bi₂Se₃ + 准绝热区首批三通道信号"为第 3 年旗舰成果；scheme 说"MnBi₂Te₄ 上的瞬态陈数 ΔC = 1 跃变首次被实验反演信号观测到"为第 3 年里程碑。**同一份申请书的两个章节给出不同的"年度旗舰成果"**
- 修复：把 scheme §6 line 247-250 第 3 年里程碑改为"Bi₂Se₃ + 准绝热区首批三通道信号（与 content §4 一致）"；把"MnBi₂Te₄ 首次 ΔC=1 跃变观测"挪到第 4 年（scheme §1.3 line 71 第 4 年 A 是 1T-TaS₂，B 是全信号同步采集，C 是 L1 全反演 — 可在该年加"MnBi₂Te₄ 首次 ΔC=1 跃变观测"作为子课题 B 的拓展任务）
- action：**rewrite**

### [high] B-4 AI 代理模型训练时间两章矛盾
- 位置：content §4 line 69 vs scheme §1.3 line 67-72 + scheme §6 line 237-238
- 问题：content §4 line 69 第 3 年写"AI 代理模型由 L0 解析样本开始预训练"，scheme 三处（第 1 年启动预训练、第 3 年微调）写不同。content.md line 89 注脚虽声明"AI 预训练在第 1 年末完成"但 §4 表格没改 — **content.md v0.5 重写时遗留**
- 修复：把 content §4 line 69 第 3 年里程碑改为"AI 代理模型在 L1 RT-TDDFT 数据上微调（接续第 1 年预训练）"，与 scheme.md 同步
- action：**rewrite**

### [high] B-5 references.md 完全空置（连续 4 轮 P0 100% 未执行）
- 位置：references.md 3 行 / 50 字 vs rationale [1]-[39]、content/scheme [5][9][20][21][32][33][34] 引用
- 问题：申请书所有编号引用无对应文献清单 — 评审专家无法核实任何引文真伪。这是 NSFC 申请书基本格式要求缺失
- 修复：把 references.md 补齐为完整文献列表（≥40 条），与 rationale/content/scheme 中的所有编号引用一一对应；按 NSFC 格式要求（期刊/卷期/页码/年份/标题）规范化。**最低要求：补全 rationale 中已列出的 [1]-[39] + content/scheme 额外引用的所有编号**
- action：**rewrite（按 round-5/6/7/8 P0 要求 ≥ 500 字，建议 ≥ 3000 字）**

### [medium] C-1 rationale ΔC ≤ 0.05 与 content/scheme ≈ 0.113 数字含义未区分
- 位置：rationale §3.3 line 87
- 问题：rationale 给的是"1D-TDSE ground truth 校验精度 ΔC ≤ 0.05"，content/scheme 给的是"总反演误差 √合成 ≈ 0.113"。两者数字含义不同（前者仅 ground truth，后者含 RT-TDDFT 泛函误差），但 rationale 没明示这一点
- 修复：rationale §3.3 line 87 改为"1D-TDSE ground truth 校验精度已达 ΔC ≤ 0.05（仅 ground truth 层面）；含 RT-TDDFT 泛函误差、实验噪声、抖动、温漂的总反演误差预算约为 ΔC ≈ 0.113"
- action：**rewrite**

### [medium] C-2 rationale §3.2 圆偏振 HHG 角色表述弱化
- 位置：rationale §3.2 line 75
- 问题：rationale 写"圆偏振 HHG 与椭圆分辨谱仪已成熟，可作为子课题 B 的探测通道"，未量化时间分辨角色；scheme §2.2b line 125 明确"不能参与 ≤100 as 瞬态拓扑反演，而用作时间平均的 Berry 曲率投影测量"。**rationale 表述弱于 scheme，未对齐**
- 修复：rationale §3.2 line 75 改为"圆偏振 HHG 作为 Berry 曲率时间平均投影的互补通道（不参与 ≤100 as 瞬态拓扑演化时间分辨测量）"
- action：**rewrite**

### [medium] C-3 rationale §3.1 ℏω/E_g 阈值口径与 content/scheme 不一致
- 位置：rationale §3.1 line 17
- 问题：rationale 写"ℏω/E_g ≫ 1（准绝热）/ ≲ 1（强非绝热）"；content/scheme 显式"≥2 / ≤1"。**qualitative vs quantitative 表述不一致**
- 修复：rationale §3.1 line 17 改为"ℏω/E_g ≥ 2（准绝热）/ ℏω/E_g ≤ 1（强非绝热）"，与 content/scheme 同步
- action：**rewrite**

### [medium] C-4 rationale SNR 计算口径与 scheme 不同
- 位置：rationale §3.3 line 83 vs scheme §2.3b line 156
- 问题：rationale 用"5/0.113 ≈ 44"作为 SNR（5 = 项目级指标 ΔC 阈值）；scheme 用"1/0.113 ≈ 8.8"作为 SNR（针对 ΔC=1 整数跃变）。两个数字都对，但定义口径不同 — 评审专家会质疑"为什么 SNR 不一样"
- 修复：rationale §3.3 line 83 改为"针对 ΔC=1 整数跃变的 SNR = 1/0.113 ≈ 8.8；针对实用阈值 ΔC ≤ 0.2 的 SNR = 0.2/0.113 ≈ 1.77"
- action：**rewrite**

### [medium] redundancy 5 年研究阶段表 3 处出现
- 位置：content §4 line 65-71 + scheme §1.3 line 67-72 + scheme §6 line 233-262
- 问题：三处表格角度不同但内容重叠 ~70%
- 修复：保留 scheme §6（完整里程碑）+ scheme §1.3（技术节律，引用 §6），删除 content §4 重复表格；或保留 content §4 作为"研究内容递进节奏"概述，删除 scheme §1.3 重复
- action：**rewrite**

### [medium] redundancy 绝热分区判据 6 处出现
- 位置：rationale §3.1 line 17 + content §2.1 line 25-27 + §3 Q1 line 55 + scheme §2.1a line 86-93 + §2.3a line 148 + §6 line 235-243
- 问题：判据文字从 5-6 个角度重复
- 修复：在 scheme §2.1a 给出"判据物理根据 + 阈值口径"完整论证，其他位置用"判据见 scheme §2.1a，物理含义不再赘述"一句话引用
- action：**rewrite**

### [medium] （四）特色与创新未独立成节（与 scheme.md §5 合并）
- 位置：申请书缺少独立的"（四）特色与创新"小节
- 问题：NSFC 重点项目模板要求"（四）特色与创新"独立呈现 3-5 个创新点（需有范式变革或理论突破级别）；本申请书把"特色与创新"合并在 scheme.md §5 内，**章节边界不清晰**
- 修复：把 scheme.md §5 三项方法学定位提升为独立"（四）特色与创新"小节（与 scheme.md §1-§4 平行），每项创新点对应一个科学问题 Q1/Q2/Q3 的解决
- action：**rewrite（章节重排）**

### [medium] full_review.md 仍 3 行占位
- 位置：full_review.md 3 行 / 81 字
- 问题：本轮整体一致性审查的输出将填充该文件
- 修复：把本评审报告的关键一致性结论写入 full_review.md
- action：**rewrite（本轮完成）**

### [low] rationale §3.1 line 17 "瞬时本征态保持良好定义" "瞬时陈数 $C_n(t)$ 可作为瞬态拓扑不变量"
- 这是判据的物理后果，但未明确说"瞬时陈数在准绝热区等于平衡态陈数" — 评审专家可能问"那瞬时陈数与平衡态陈数有什么区别"
- 修复：补充 1 句"瞬时陈数 $C_n(t)$ 在准绝热区与平衡态陈数 $C_n^{(0)}$ 数学同构，但 $C_n(t)$ 的时间演化（瞬态陈数动力学）是瞬态物理的新对象"
- action：**rewrite**

### [low] content §1 line 11 "瞬态拓扑不变量" vs "平衡态 TKNN 陈数" 区别
- 申请书反复说"瞬态不变量是创新"但准绝热区瞬时陈数与平衡态 TKNN 数学同构 — 创新在"瞬时演化"而非"瞬时值"
- 修复：content §1 line 11 补充 1 句"本项目所指的'瞬态拓扑不变量'的创新不在'瞬时值'（准绝热区与平衡态同构），而在'瞬时演化'（亚周期尺度上的陈数动力学、含时 Wilson 圈轨迹）"
- action：**rewrite**

### [low] scheme §4 段落间过渡较弱（多处）
- §1 → §2、§3 → §4、§4 → §5 缺乏过渡句
- 修复：每节末尾加 1 句过渡句
- action：**rewrite**

### [low] rationale 5 年研究阶段表 line 13-15 国际同行仅列 3 家，未在 content/scheme 重复
- 修复：在 content §1 line 11 或 scheme §5(2) line 222 简短交叉引用 rationale §4 的"差异化定位"
- action：**add**

---

## 八、对抗结论

### 本轮发现 5 个 [high] + 4 个 [medium] + 4 个 [low] 问题

### 与上一轮（scheme.md 聚焦评审 0.66）对比
- **改善 0 个**：本轮与上一轮是不同范围评审（上一轮聚焦 scheme.md，本轮聚焦整体一致性），不直接对比
- **新增 5 个 high**：本轮首次发现的 5 个跨章节一致性违反（SHG、MoS₂ 分类、第 3 年材料、AI 时间、references）
- **未解决 5 个**：其中 1 个（SHG）是 round-3 以来 5 轮未修的常驻 critical/high；其余 4 个（references/团队平台）是 round-5~8 P0 列表的常驻 high

### 是否达到输出标准
- 综合分 0.71 < min_overall_score 0.85（差 0.14）— **未达阈值**
- high 级问题 5 个 > max_high_issues 0 — **未达阈值**
- medium 级问题 4 个 > max_medium_issues 2 — **未达阈值**

### 返工优先级

**P0（必须立即修复，申请书基础完整性）**：
1. **B-5 references.md** — 补齐为完整文献列表（≥40 条）— 评审专家无法核实任何引文
2. **B-1 SHG 在 Bi₂Se₃ 上物理不可行** — 全文删除或重写（5 轮残留）
3. **B-2 MoS₂ 强非绝热分类不自洽** — 调为准绝热区代表或补充真正强非绝热体系

**P1（重要，影响逻辑一致性）**：
4. **B-3 第 3 年材料里程碑** — 两章同步
5. **B-4 AI 训练时间** — 两章同步

**P2（次要，改善严谨性）**：
6. **C-1/C-2/C-3/C-4** — 数字含义区分、术语口径统一
7. **冗余表格** — content §4 与 scheme §1.3 整合

**P3（润色）**：
8. **特色与创新独立成节** — 章节重排
9. **方案章节过渡句** — 段落间加 1-2 句

### 下一轮评审建议聚焦

1. **段落级深审**：本轮是整体一致性，未做段落级。建议下一轮对 scheme.md §2.1a（绝热分区判据）、scheme.md §2.3b（误差预算）、content §3（关键问题 Q1/Q2/Q3）做段落级深审
2. **物理专项检查**：下一轮执行 8 项物理专项检查（BSV/反演精度区分、Berry 曲率/量子度规可辨识性、CDW/Mott/拓扑混用、Q1/Q2 真假可证伪、双色场 sin/cos 假设、预印本占比、驱动波长 vs 带隙、Sala 2025 / Ghalgaoui / Rasputnyi / Tyulnev / Verma 核实）
3. **引文事实核查**：下一轮对照补齐的 references.md，对每条引文做 (期刊名/卷期号/年份/DOI) 4 项核查

---

## 评分

创新性：0.80
可行性：0.68
严谨性：0.62
完整性：0.72
综合评分：0.71