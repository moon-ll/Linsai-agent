# 对抗评审报告（第 6 轮 · 立项依据深审）

## 元信息与审查边界

| 项 | 内容 |
|---|---|
| 项目类型 | general（NSFC 面上项目；4 年；资助上限 60 万元；正文≤30 页） |
| 本轮聚焦 | （一）立项依据（科学意义、前人研究局限性）——段落级深审 |
| 聚焦章节文件 | `04_proposal/sections/rationale.md`（62 行，约 5,800 中文字符；4 个二级标题） |
| 跨章节简查 | `sections/content.md`、`sections/scheme.md`、`sections/references.md`、`sections/innovation.md`、`sections/plan.md`（仅做一致性） |
| 质量标准 | `memory/nsfc-standards.json` → `project_types.general`（min_overall=0.80；max_high=0；max_medium=3）+ `general_principles.writing_style_rules` + `scoring_rubric` + `benchmark_anchors` |
| 评审日期 | 2026-08-08 |
| profile | critic |
| 历史脉络 | round-1（rationale 首审 0.41）→ round-2（content 0.62）→ round-3（scheme 0.60）→ round-4（整体一致性 0.62；标 references 为 [critical] 缺失）→ round-5（references 深审 0.66，6 条 critical/high 级引文错误）→ **本轮（rationale 段落级深审）** |
| 事实核查方式 | Crossref/arXiv 关键词复核 + 行内 anti-AI 模式统计（提供...基础/首次/首次系统性/死板关联词/超长句）+ 与 round-1 修复确认 + 跨章一致性核验 |

> **本轮定位**：用户指定聚焦 §1.1–§1.4 立项依据段落级深审。round-1 对该章原始稿件打出 0.41 的低分（共 11 个问题，含 3 个 critical），随后 writer 多轮整改。本轮重新逐段对照 `nsfc-standards.json` 与范本锚点，重点检查：(a) round-1 标记的 critical/high 问题是否真修复；(b) round-5 引文错误是否在 rationale.md 文本中同步反映；(c) 当前 rationale.md 残留的 anti-AI 与 narrative 红线；(d) 物理专项检查清单（#1 BSV 增强 vs 反演精度、#2 Berry 曲率/量子度规可辨识性、#4 Q1/Q2 真假科学问题、#6 预印本依赖度、#7 驱动波长-带隙匹配）。

---

## 0. 模块完整性检查

`rationale.md` 自身结构完整，含 4 个二级标题（§1.1 / §1.2 / §1.3 / §1.4）。按 NSFC 面上三段式（立项依据 + 研究内容 + 研究基础），立项依据独立成节，模块完整性合格。其他 7 个标准模块状态详见 round-5 报告（research_plan 已独立文件，innovation 已独立文件，预期成果已扩展≥200 字，参考文献已 23 条）。

---

## 综合评分

**0.71 / 1.00**（按用户指令 4 维加权：0.30×创新性 + 0.25×可行性 + 0.20×严谨性 + 0.25×完整性）

**进展（writer 相对 round-1）**：
- §1.1 段 1 **大幅收紧修辞**：删除"新范式"措辞，删除"纠缠光子对"无关并列，把"经典光 HHG 触及单粒子/平均场层面"改为"经典光 HHG 已经触及单粒子与部分多体修正层面，但对多体关联/量子涨落仍缺乏定量灵敏度"——这正是 round-1 C-1.4 标记的**自相矛盾 critical 问题**的修复。✅
- §1.1 段 2 已增加 **No-Go 降级判据**："若 QEF 在三类对照体系上不单调上升，或独立测量（瞬态吸收、PL、tr-ARPES）与反演结果偏离超过预设阈值，则本项目将探针范式降级为'多体响应分类工具'"——修复 round-1 H-1.6「缺乏 No-Go 判据」high。✅
- §1.1 段 2 已给出 **QEF≥1.5 阈值** + 定义溯源（Fisher 信息或后验方差下降）——修复 round-1 M-1.7「额外灵敏度未量化」medium。✅
- §1.3 段 4 已澄清 "parameter dependence study ≠ coherent control / quantum optimal control" —— 修复 round-1 的术语漂移。✅
- §1.3 段 3 **关键自洽性修正**：$Q_F \to V_{\rm classical} \approx 1$（而非 $Q_F \to 0$）——这是 round-1 标记的 critical 物理错误，"该修正以"自洽性检验（修正）"明确标注，是高质量的修复动作"。✅
- §1.2.3 段 2 已精确区分 TMDC（"**属弱关联半导体而非强关联材料**"）与莫尔/Mott 的关联强度差异——修复 round-1 "TMDC 被列入强关联材料"问题。✅
- §1.4 创新点 3 已明确 Boroumand 2025 "**核心实验差异**"为"单束双色场 vs 双光路 Mach-Zehnder"，并加 "**且本项目聚焦固体体系而非气体原子**"——这是为应对 round-5 标记的 H-5.7「QSHHG 缩写归属存疑」而做的边界澄清，部分修复。✅

**本轮新增/残留（聚焦 rationale 段落级深审）**：
1. **超长句系统性反弹** [high] anti_ai：rationale.md 含 ≥6 个 >200 字符的单句（其中 §1.1 段 1 第 5 行 477 字符、§1.1 段 1 第 5 行 245 字符），违反 `anti_ai_patterns.remove.超长句：单句超过80字应拆分，超过120字属严重超长句`。这是 round-1 未深查但本轮通过分句统计发现的新维度问题。
2. **冗余修饰词密度偏高** [medium] anti_ai：rationale.md 共出现"系统/关键/显著/精准/重要/成熟/完整"等冗余修饰词 16 次（按行号：13/13/19/23/29/37/45/47/49/51/55/57/57/59/5）——其中"系统"6 次、"关键"3 次、"显著"2 次。虽然单条不超限，但密度叠加形成 AI 味纹理。
3. **Even Tzur 引文与 round-5 标记的 critical 引文错误同步出现** [high] red_line/rigor：rationale.md 第 29 行写 `[Even Tzur M. et al., Phys. Rev. Research 6, 023064 (2024); arXiv:2311.11257]`，但 round-5 联网核实该 DOI/arXiv ID 三重错误——正文与参考文献表未同步修复。这是**跨章节一致性**典型问题。
4. **Boroumand QSHHG 边界声明仍未自洽** [medium] rigor：rationale.md §1.4 创新点 3 写"Boroumand 2025 提出的 QSHHG 理论"，正文与 innovation.md/§2.8 反复使用 QSHHG 缩写，但该缩写并不出现在 round-5 联网核实的 arXiv:2505.22536 真实标题中——"概念同源但实验实现独立"的边界声明仍建立在未核实的引用之上。
5. **§1.3 问题 3 经典极限口径与 §2.5 自洽性表述完全一致** [P3 已修复跨章一致性]：rationale §1.3 与 content §2.5 均用 $V_{\rm classical} \approx 1$ 表述自洽性，cross-check 通过——这是 round-1 critical 修复后 round-4 已确认的成果，本轮未发现新矛盾。
6. **§1.1 段 1 第 5 行 Berry 曲率归因得到显式 hedging** [P3 已修复过度归因]：作者写"**对 Berry 曲率敏感**（但与量子度规、带间/带内贡献等多通道耦合，需在双色场微扰一阶近似或更精细模型下分通道解读）"——符合物理专项 #2 建议。✅
7. **国内首个声明已加检索范围与截止日期** [P3 合规化]：rationale §1.1 段 4 + §1.4 创新点 2 均写"作者于 2026-08-03 在 arXiv / Web of Science / CNKI 上以 ... 关键词检索，未发现国内团队在 BSV 驱动固体 HHG 方向发表系统性研究工作"——符合 `indicator_red_lines.novelty_claim_cautious` 要求。✅

综合评分 0.71：rationale.md 经过 round-1 → round-6 五轮整改，整体质量从"概念堆叠、有自相矛盾 critical 物理错误"提升至"以科学问题为主线展开、量化指标初步建立、跨章一致性基本对齐"。但本轮发现的"超长句系统性反弹""冗余修饰密度偏高""Even Tzur 引文未同步修复""QSHHG 边界仍存疑"四项问题将严谨性与表达质量限制在 0.7 区间。

---

## 维度评分

| 维度 | 权重 | 得分 | rubric 档位 | 主要短板 |
|---|---:|---:|---|---|
| 创新性（innovation） | 0.30 | **0.78** | `scoring_rubric.innovation.0.75-0.85` | "首次系统化""国内首个"边界声明已合规化；QEF/Q_F 双指标是命名层创新；但 §1.4 创新点 3 的 QSHHG 归属仍依赖于未核实引用 |
| 可行性（feasibility） | 0.25 | **0.72** | `scoring_rubric.feasibility.0.70-0.80` | BSV 平台参数（$10^{13}$/脉冲、<50 fs）有具体目标，Y1-Y4 里程碑已分层；可行性专门论证（"为什么能做成"）放在 scheme §3.5 而非本节，本轮不深入 |
| 严谨性（rigor） | 0.20 | **0.62** | `scoring_rubric.rigor.0.6-0.7` | **本轮主要短板**：Even Tzur 引文与 round-5 标记的 [critical] 错误未在 rationale.md 同步修复；QSHHG 缩写边界声明建立在未核实引用上；§1.3 问题 1 "显著差异"的量化口径偏弱（"误差范围内接近 1"未给出具体阈值）；§1.4 创新点 1 "首次将 ... 串成完整闭环"为强宣称 |
| 完整性（completeness） | 0.25 | **0.72** | `scoring_rubric.completeness.0.70-0.80` | 立项依据五层递进结构基本到位（科学意义 → 国内外现状 → 空白 → 科学问题 → 创新点）；§1.4 创新点 3 条结构齐全；但 §1.4 创新点 1 的"现有局限→方案→量化优势→定位收束"四步闭环中"量化优势"略空 |

**加权综合**：`0.30×0.78 + 0.25×0.72 + 0.20×0.62 + 0.25×0.72 = 0.234 + 0.180 + 0.124 + 0.180 = 0.718 ≈ 0.71`

---

## 一、立项依据段落级深度评审

> **评审原则**：每段先列**作者主张**（1-3 句摘要），再列**round-1 修复确认**，再列**本轮新增问题**（按 severity + issue_type），最后给出**action**。

### §1.1 段 1（第 5 行）— 大背景与领域脉络

**作者主张**：经典相干态激光驱动的 HHG 已经走过从光源研究到凝聚态探针的关键一步；拓扑绝缘体/TMDC/Hubbard-Mott 三大方向已建立"单粒子与部分多体修正层面"的能力基线；2024 年 Rasputnyi 首例实验后浮现根本性问题——量子光场能否突破"多体关联与量子涨落"这一边界？本段是该判断的逻辑起点。

**round-1 修复确认**：
- ✅ "新范式"措辞 → 已删；"全新"措辞 → 已收敛为"尚待开拓"
- ✅ "经典光 HHG 触及单粒子/平均场层面" vs "已建立多体基线"自相矛盾 → 已统一为"已经触及单粒子与部分多体修正层面，但对多体关联/量子涨落仍缺乏定量灵敏度"
- ✅ "纠缠光子对"与本项目无关的并列表述 → 已删除
- ✅ Berry 曲率过度归因 → 已加 hedging"（但与量子度规、带间/带内贡献等多通道耦合，需在双色场微扰一阶近似或更精细模型下分通道解读）"

**本轮新增/残留问题**：

#### [high] anti_ai — §1.1 段 1 第 5 行：477 字符单句严重超长
- **位置**：rationale.md 第 5 行（"在能带几何响应层面... 构成本项目的原始创新空间"），是 BSV-HHG 整个引入段 + 三类对照 + Rasputnyi 触发点 + 量子相变 Y4 扩展 + 国内空白声明的**复合段**
- **问题**：用 `。` 分句后该段最长一句达 **477 字符**，第二长 245 字符。违反 `anti_ai_patterns.remove.超长句：单句超过80字应拆分，超过120字属严重超长句`。本段用 3 个 `[...]` 文献括号打断语流，复合句嵌套 5-6 个定语/状语从句。**这是 rationale.md 单段最严重的 anti-AI 红线**，且 round-1 未针对此项深查（round-1 主查概念堆砌，未做句长统计）。
- **建议改写**（直接给出可执行替换）：
  ```
  原文（477 字符单句）：
  "在能带几何响应层面，Bi₂Se₃、Bi₂Te₃ 等拓扑绝缘体的 HHG 圆偏振选择性**对 Berry 曲率敏感**
  （但与量子度规、带间/带内贡献等多通道耦合，需在双色场微扰一阶近似或更精细模型下分通道解读）；
  在能谷选择探测层面，MoS₂、WSe₂ 等过渡金属硫族化合物（TMDC）单层的 HHG 产出规律与非微扰多带
  模型一致 [Wu, Schafer, Gaarde, Phys. Rev. A 94, 063403 (2016); arXiv:1609.09852]；
  在关联体系层面，经典光 HHG 在 Hubbard/Mott 体系中的**部分多体动力学**已建立基线——但**对量子
  关联/量子涨落灵敏度有限** [Silva et al., Nat. Photon. 12, 266 (2018); arXiv:1704.08471；
  Murakami et al., PRL 121, 057405 (2018); arXiv:1712.06460；Prajapati et al., arXiv:2410.01424]。
  这一判断是本项目的逻辑基线：经典光 HHG 已经触及单粒子与部分多体修正层面，但对**多体关联与
  量子涨落**仍缺乏定量灵敏度——而这正是量子光场可能突破的边界。"

  建议改写为 3 段（每段 80-120 字符单句）：
  (1) "在能带几何响应层面，Bi₂Se₃、Bi₂Te₃ 等拓扑绝缘体的 HHG 圆偏振选择性对 Berry 曲率敏感，
      但与量子度规、带间/带内贡献等多通道耦合，需在双色场微扰一阶近似或更精细模型下分通道解读。"
  (2) "在能谷选择探测层面，MoS₂、WSe₂ 等 TMDC 单层的 HHG 产出规律与非微扰多带模型一致
      [Wu, Schafer, Gaarde, PRA 94, 063403 (2016)]；在关联体系层面，经典光 HHG 在
      Hubbard/Mott 中的部分多体动力学已建立基线，但对量子关联/量子涨落灵敏度有限
      [Silva et al., Nat. Photon. 12, 266 (2018); Murakami et al., PRL 121, 057405 (2018);
      Prajapati et al., arXiv:2410.01424]。"
  (3) "上述能力共同构成本项目的逻辑基线：经典光 HHG 已触及单粒子与部分多体修正层面，
      但对多体关联与量子涨落仍缺乏定量灵敏度——这正是量子光场可能突破的边界。"
  ```
- **违反条款**：`anti_ai_patterns.remove.超长句`；`writing_style_rules.must.使用连贯段落和过渡句`；`style_benchmark.sentence_rhythm.短句为主，单句一般不超过 60 字`
- **priority**：P1（必改，单段最长句是评审专家第一眼印象）
- **action**：rewrite

#### [medium] anti_ai — §1.1 段 1：冗余修饰词密度偏高
- **位置**：rationale.md 第 13 行"**关键**交付"、第 19 行"**成熟**的能力"、第 23 行"**重要**资源"、第 29 行"**关键**物理"、第 37 行"**系统**化"、第 45/47 行"**显著**优于"/"**显著**差异"、第 49/55 行"**系统**化"、第 51 行"**精准**同步"、第 57 行"**完整**闭环"/**系统**化"、第 59 行"**系统**性开展"
- **问题**：共 16 处冗余修饰词，其中"系统"6 次、"关键"3 次、"显著"2 次、"重要/成熟/完整/精准/系统化" 各 1-2 次。虽未超 `quantitative_thresholds.冗余修饰词上限: 15`，但密度叠加形成 AI 味纹理。
- **建议**：
  - 第 13 行"关键交付"→"约定交付"（或直接删"关键"）
  - 第 19 行"成熟的能力"→"三类已成立的能力"
  - 第 23 行"重要资源"→"基础资源"
  - 第 29 行"关键物理"→删"关键"
  - 第 37/49/55 行"系统化"→保留 §1.4 创新点处的"系统化"层级描述，中间段（如 §1.2.1）改为"覆盖 / 包含"
  - 第 45/47 行"显著优于"/"显著差异"→改为"明确优于"/"可分辨差异"（"显著"在统计上有专门含义，避免统计滥用）
  - 第 51 行"精准同步"→"同步"（"精准"是常见 AI 修饰）
  - 第 57 行"完整闭环"→"闭环"或"全链条"
- **违反条款**：`anti_ai_patterns.remove.冗余修饰堆砌：显著、重要、系统、良好、成熟、完整、关键、精准、一系列`
- **priority**：P2
- **action**：rewrite（多处集中修改）

#### [low] narrative — §1.1 段 1 仍含微量文献并列堆砌
- **位置**：第 5 行末尾"但**对量子关联/量子涨落灵敏度有限** [Silva et al., ...; Murakami et al., ...; Prajapati et al., ...]"
- **问题**：3 篇文献并列一次性给出，无逐篇功能说明（Silva 是 Bi₂Se₃ 工作、Murakami 是 Mott 理论、Prajapati 是 RNiO₃ THz 实验）。属轻度文献堆砌。
- **建议**：保留文献列表但删"等" → "等三项工作分别对应拓扑绝缘体几何响应、Mott 绝缘体理论预言、RNiO₃ 莫特跃迁 THz 实验范式"（在 §2.4 内容对应处展开，rationale.md 此处只列 Silva+Murakami 两篇即可，Prajapati 移到 §2.4 Mott 段）。
- **priority**：P3
- **action**：rewrite

---

### §1.1 段 2（第 7 行）— Rasputnyi 2024 触发点 + 探针操作性定义

**作者主张**：2024 年 Rasputnyi 等首例实验后根本性问题浮现——量子光场驱动 HHG 能否触及经典光场无法揭示的多体关联/量子涨落？BSV 是宏观量子光场（$10^{13}$/脉冲），与单光子级量子光源（$\sim 10^6$/脉冲）严格区分。"探针"的操作性定义为：从 HHG 谱（产额、偏振、噪声关联、量子指纹）反演多体关联强度，QEF ≥ 1.5 阈值作可量化验收。

**round-1 修复确认**：
- ✅ 反演对象"激发寿命、量子相变"作为 Y4 示范性扩展明确出 4 年核心交付
- ✅ No-Go 降级判据已写入（独立测量偏离阈值则探针降级为"响应分类工具"）
- ✅ QEF ≥ 1.5 阈值 + Fisher 信息/后验方差量化溯源已写入

**本轮新增/残留问题**：

#### [low] rigor — §1.1 段 2 第 7 行："主要反演多体关联强度"句中的"主要"是临时补丁
- **位置**：第 7 行"**主要**反演**多体关联强度（关联长度尺度与序参量敏感性）**"
- **问题**："主要"暗示还有"次要"反演对象，但 §1.1 同段已明确"激发寿命、量子相变作为 Y4 示范性扩展（不在 4 年核心交付内）"。"主要"二字与后句"具体从 HHG 谱的产额、偏振、噪声关联、量子指纹中反演信息"形成隐含的次要反演承诺，存在被评审追问的风险。
- **建议**：删去"主要"二字 → "反演多体关联强度（关联长度尺度与序参量敏感性）；激发寿命、量子相变作为 Y4 示范性扩展，不在 4 年核心交付内。"
- **priority**：P3
- **action**：rewrite

#### [low] rigor — QEF ≥ 1.5 阈值仍缺 metric 定义溯源
- **位置**：第 7 行末尾"QEF 定义见 §1.4 创新点 2；阈值依据 Fisher 信息增益或后验方差下降的物理可观测要求"
- **问题**：跨章节引用 §1.4 的 QEF 定义是合理的，但"阈值依据 Fisher 信息增益或后验方差下降的物理可观测要求"——"物理可观测要求"过于模糊。1.5 倍信息增益或方差下降在统计物理中的常规显著性门槛是 1.0 倍（无差异），2-3 倍属于强证据，1.5 倍是惯例中"小到中等效应量"的下限。建议明确为"对应 Cohen's d ≥ 0.5 或后验方差下降 ≥ 33%"。
- **priority**：P3
- **action**：rewrite

---

### §1.1 段 3（第 9–11 行）— 探针范式的核心价值 + 双重科学价值

**作者主张**：BSV HHG 因携带高阶光子数关联与相位压缩，可能对多体关联/量子涨落呈现额外灵敏度，QEF ≥ 1.5 阈值作量化验收；项目对量子光学（拓展非经典光场应用）和凝聚态物理（多体关联新探针）有双重价值。

**round-1 修复确认**：
- ✅ "双重科学价值"由 bullet 改为连贯穿述（round-1 H-1.8 要求）
- ✅ "全新"措辞已改为"尚待开拓"

**本轮新增/残留问题**：

#### [medium] narrative — §1.1 段 3 仍是平行列举式论证，未形成递进
- **位置**：第 11 行"对量子光学而言...对凝聚态物理而言..."
- **问题**：虽然已不是 bullet，但仍以"X 而言 / Y 而言"对称并列展开，未形成"量子光学新增自由度→在固体 HHG 中如何被检验→对凝聚态物理的反馈"递进。按 `writing_style_rules.must.以科学问题为主线展开论述`，应让两个层面通过因果链相连。
- **建议改写**：
  ```
  原文："这一方向具有双重科学价值，对量子光学而言，本项目将非经典光场的应用从量子信息、
  量子测量拓展到**强场非平衡态物理**——这是量子光场作为'物质探针'的**尚待开拓**应用场景；
  对凝聚态物理而言，经典光场 HHG 已能探测 Berry 曲率、能带结构、拓扑性质等几何响应，
  但量子光场携带的相位关联、光子数关联等额外自由度，可能对**多体关联、纠缠、量子涨落**
  提供经典光场无法触及的灵敏度。"

  建议改写为单段递进：
  "这一方向连接两条研究脉络——量子光学层面，BSV 等宏观量子光场的高增益参量下转换已
  在量子成像与量子增强测量中成熟，但其在强场非平衡态物理中的应用仍是尚待开拓的应用场景；
  凝聚态物理层面，经典光场 HHG 已能探测 Berry 曲率、能带结构、拓扑性质等几何响应，但其
  携带的经典泊松光子统计无法将光场高阶关联耦合到电子响应。本项目通过 BSV 驱动把光场
  相位关联与光子数关联作为新增自由度送入固体电子动力学，使凝聚态多体关联反演获得量子
  光场提供的额外灵敏度通道——这正是量子光场'物质探针'范式的具体内涵。"
  ```
- **违反条款**：`writing_style_rules.must.以科学问题为主线展开论述`；`anti_ai_patterns.remove.僵硬平行结构：三个'如何'排比、连续'在…层面/方面'四段`
- **priority**：P2
- **action**：rewrite

#### [low] narrative — §1.1 段 3 末句"尚待开拓的应用场景"在前段已被定性为"几乎空白"
- **位置**：第 11 行末句"这是量子光场作为'物质探针'的**尚待开拓**应用场景"
- **问题**：与 §1.1 段 4 "国内空白"声明重复，但本段未引用段 4，使前后口径看似两套独立判断。
- **建议**：删去"尚待开拓"作为独立标签 → 改为"为量子光场提供 ... '物质探针'应用场景（国际同行 Rasputnyi 2024 首例实验、Even Tzur 2024 量子态理论已奠定基础；详 §1.2.2）"。
- **priority**：P3
- **action**：rewrite

---

### §1.1 段 4（第 13 行）— Rasputnyi/Even Tzur 工作 + 国内空白

**作者主张**：Rasputnyi 2024 首例实验、Even Tzur/Gorlach 2024 量子态理论已奠定基础；国内"作者于 2026-08-03 在 arXiv / WoS / CNKI 上以 ... 关键词检索，未发现国内团队在 BSV 驱动固体 HHG 方向发表系统性研究工作"——构成本项目的原始创新空间。

**round-1 修复确认**：
- ✅ "A 做了 X，B 做了 Y"文献堆砌（round-1 H-1.11 标记）→ 已用"已奠定基础"合并叙述
- ✅ "国内空白"无检索证据 → 已加"作者于 2026-08-03 在 arXiv / WoS / CNKI 上以 ... 关键词检索"溯源
- ✅ "蓝海" / "首创"等强宣称 → 已收敛为"原始创新空间"

**本轮新增/残留问题**：

#### [medium] rigor — 国内检索关键词组合的有效性需说明
- **位置**：第 13 行"作者于 2026-08-03 在 arXiv / Web of Science / CNKI 上以 'bright squeezed vacuum'、'BSV HHG'、'量子光场驱动 HHG'、'非经典光高次谐波' 等关键词检索"
- **问题**：4 个关键词的逻辑 OR 关系在 arXiv/WoS/CNKI 上对国内团队的漏检风险不同——arXiv 国际预印本对国内团队覆盖较好但 CNKI 对国际团队覆盖差；本检索是否能完全排除"国内团队用英文发 arXiv 但未在 CNKI 上检索到"的情形？
- **建议**：增加 1-2 个补充检索（如 Google Scholar 中英文混检、Chinese Physics Letters / 中国物理学会出版物检索），并写"截至检索日期，尚未见 ... 系统性研究工作（检索范围限于上述 4 数据库，可能漏检情况已标注）"——增加谦抑语。
- **priority**：P3
- **action**：rewrite

#### [low] narrative — "作者检索范围内"措辞可弱化
- **位置**：§1.4 创新点 2 第 59 行同样出现"在**作者检索范围内**（检索日期 2026-08-03，CNKI / WoS / arXiv），本项目是国内**首个**系统性开展 ... 研究的面上项目"
- **问题**：创新点 2 处的"首个系统性开展"与 §1.1 段 4 的"未发现国内团队发表系统性研究工作"互为佐证，但**两者措辞强度不同**——"未发表系统性研究工作"是文献陈述，"首个系统性开展 ... 研究"是申请主张。两者之间存在逻辑跳跃（"未发表"≠"未开展"，可能存在进行中未发表的工作）。
- **建议**：§1.4 创新点 2 改为"在作者文献检索范围内，未见国内团队在 BSV 驱动固体 HHG 方向发表系统性研究工作；本项目是首个系统性提出该方向面上项目申请的研究计划"——区分"已发表"与"已开展"，避免主张过度。
- **priority**：P3
- **action**：rewrite

---

### §1.2.1（第 17–18 行）— 经典光场 HHG 作为凝聚态探针

**作者主张**：固体 HHG 自 2011 年 Ghimire 与 Reis 在 ZnO 中首次观测以来，已经从"光源研究"发展为"能带与拓扑探针"；三类已成熟能力——拓扑绝缘体 Berry 曲率探测（**MIR 2-4 μm 驱动下最为明确**）、TMDC 多带干涉 HHG 谱对照基线、多 plateau 截止律（3-5 倍带隙 → 30-40 eV，对应 EUV 20-80 eV）。

**round-1 修复确认**：
- ✅ 物理专项 #7「驱动波长-带隙匹配」已加"MIR 2-4 μm 驱动下最为明确"——避免了 round-1 隐含的"1.5 μm 在 Bi₂Te₃ 是共振"过度归因
- ✅ 30-40 eV 与 7-9 阶口径不自洽（round-1 M-1.x）→ 已删除或整合

**本轮新增/残留问题**：

#### [low] rigor — 30-40 eV 与 EUV 20-80 eV 区间表述需自洽
- **位置**：第 19 行"3–5 倍带隙 cutoff 律 → 截止能量 30–40 eV，对应 EUV 谱段 20–80 eV"
- **问题**：30-40 eV 落在 EUV 区间是 OK 的，但 20-80 eV 跨度较大，3-5 倍带隙 cutoff 在不同带隙体系下偏移较大（如 MoS₂ 带隙 1.6 eV → 3-5 倍带隙 ≈ 4.8-8 eV，对应 VUV 而非 EUV）。
- **建议**：补一句"对应不同带隙材料的具体截止能量不同：MoS₂ 带隙 1.6 eV → 截止 5-8 eV；Bi₂Se₃ 带隙 0.3 eV → 截止 1-1.5 eV 已被中红外 MIR 驱动观测"，与 §2.2 "7-13 阶对应 8-20 eV"呼应。
- **priority**：P3
- **action**：rewrite

---

### §1.2.2 段 1（第 23 行）— BSV 物理基线（标定光子统计）

**作者主张**：BSV 单脉冲光子数可达 $2 \times 10^{13}$，$g^{(2)}(0)$ 在非简并 PDC 配置下 2、在简并 PDC 配置下 $3 + 1/N$（高 N 下趋近 3，反映超聚束 bunching）——两类独立实验体系分别复现。

**round-1 修复确认**：
- ✅ $g^{(2)}(0)$ 区间合并两个独立实验体系（round-1 M-1.x）→ 已明确"两类独立实验体系分别复现，非同一区间的两个端点"
- ✅ Iskhakov 引文卷期（Opt. Lett. 37, 1919 (2012)）→ 与 references #4 一致（虽然 references #4 标题 round-5 标 [critical] 张冠李戴，但这是参考文献表问题不是本节文本问题）

**本轮新增/残留问题**：

#### [medium] anti_ai — §1.2.2 段 1 "高光子数涨落关联、强相位敏感性"是典型 AI 列举
- **位置**：第 23 行"BSV 具有高光子数涨落关联、强相位敏感性"
- **问题**：两词并列（"高+强"），无具体物理量（涨落系数、压缩 dB、相位灵敏度阈值），是 AI 列举模板。
- **建议**："BSV 在高增益 PDC 下表现出 Mandel Q 参数 $\sim 10^{12}$ 量级（远超相干态 Q=0）和压缩度 $r \sim \mathcal{O}(1)$，使其相位灵敏度逼近散粒噪声基准以下数 dB"。
- **priority**：P2
- **action**：rewrite

---

### §1.2.2 段 2（第 25 行）— 三层论证（新物理价值）

**作者主张**：BSV-HHG 新物理价值分光源层 / 观测层 / 反演层三层论证；**不预设**产额增益必然转化为反演精度增益；QEF ≥ 1.5 阈值 + 三维度 QEF 标尺定量验证。

**round-1 修复确认**：
- ✅ "产额增益 ≠ 反演精度增益"的物理学逻辑澄清（round-1 物理专项 #1）→ 已显式写出三层分立论证 + "本项目不预设产额增益必然转化为反演精度增益"

**本轮新增/残留问题**：

#### [low] expression — "QEF 三维度" 表述与 §1.4 创新点 2 的"QEF 双指标"口径不一致
- **位置**：§1.2.2 段 2 第 25 行"以 QEF 三维度（$QEF_{\rm vis}$、$QEF_{\rm yield}^{(q_{\rm ref})}$、$QEF_{\rm yield}^{(\sum)}$）" vs §1.4 创新点 2 第 59 行"提出 QEF 双指标——$QEF_{\rm vis} = V_{\rm BSV}/V_{\rm classical}$（干涉可见度型）与 $QEF_{\rm yield} = Y_{\rm BSV-HHG}/Y_{\rm classical-HHG}$（同等平均强度下产出比）"
- **问题**：§1.2.2 称"QEF 三维度"（3 个独立指标），§1.4 称"QEF 双指标"（2 个核心）。content §2.4 又写"两个核心指标 + 一个辅助验证指标"——3 处口径不一致。round-1 已标记为 cross-chapter consistency issue (round-1 H-1.x)，但本轮仍未完全统一。
- **建议**：全文统一为"QEF 三维度"（主指标 ×2 + 辅助指标 ×1），并在 §1.4 创新点 2 处把"QEF 双指标"改为"QEF 三维度标尺（两个主指标 + 一个辅助指标）"。这是 round-4 残留问题。
- **priority**：P2
- **action**：rewrite（跨章节同步）

---

### §1.2.2 段 3（第 27 行）— Rasputnyi 2024 首例实验

**作者主张**：Rasputnyi 2024 在 CLEO 2024 报道 BSV 驱动固体 HHG 首例实验；BSV 单脉冲 $2 \times 10^{13}$、相同平均强度下报告产额增强（具体倍数与归一化见原文 §III）；**不预设**产额增益直接转化为探针优势——产额增益与反演精度增益是两个独立维度。

**本轮新增/残留问题**：

#### [high] red_line/cross_chapter — §1.2.2 段 3 引用 Iskhakov [Opt. Lett. 37, 1919 (2012)] 与 round-5 标记的 [critical] 张冠李戴
- **位置**：§1.2.2 段 1 第 23 行末尾"已在 [Iskhakov et al., Opt. Lett. 37, 1919 (2012); arXiv:1202.1682]"——卷期与 references.md #4 一致，但 round-5 联网核实该卷期（Opt. Lett. 37, 1919 (2012)）实为 "Superbunched bright squeezed vacuum state"，而 references.md #4 写的是"High-spatial-resolution retrieval..."，与正文引用意图（g^{(2)}(0) 基线）实际吻合的是 "Superbunched BSV" 工作。
- **问题**：本节文本意图是引"超聚束 BSV g^{(2)}(0) 基线"，references #4 标题错指为另一工作（"空间谱反演"）。正文与参考文献表**均需更正**：正文按真实标题改正引文标题，参考文献 #4 也改正为真实标题。这是 round-5 C-5.3 critical 的延伸。
- **建议**：
  - 正文第 23 行保持 [Iskhakov et al., Opt. Lett. 37, 1919 (2012); arXiv:1202.1682]，并明确"该工作报道 BSV 在 PDC 增益 $G \gg 1$ 下的超聚束 $g^{(2)}(0) \approx 3$"——即用真实主题呼应引用意图
  - references.md #4 标题从"High-spatial-resolution retrieval of the spatial spectrum of parametric down-converted light" 改为真实标题 "Superbunched bright squeezed vacuum state"
- **违反条款**：`indicator_red_lines.consistency_check`；`cross_chapter_consistency`；round-5 C-5.3
- **priority**：P1（引文张冠李戴是评审专家第一时间会质疑的硬伤）
- **action**：verify + rewrite（已在 round-5 列出，本轮确认 rationale.md 需同步）

#### [medium] rigor — Rasputnyi 2024 "CLEO 2024 报道" + "arXiv:2403.15337" 双归属未澄清
- **位置**：第 27 行"2024 年 Rasputnyi 等在 CLEO 2024 报道了 ... [Rasputnyi A. et al., arXiv:2403.15337 (2024)]"
- **问题**：CLEO 2024 是会议，arXiv:2403.15337 是预印本——二者关系未澄清（是否同一版本、是否正式发表、是否 conference paper）。
- **建议**：明确为"[Rasputnyi A. et al., in CLEO 2024 Technical Digest, paper ... (2024); arXiv:2403.15337]"或"[Rasputnyi A. et al., arXiv:2403.15337 (2024), also presented at CLEO 2024]"。round-5 已标注 #1 为预印本状态，本节文本应反映该状态。
- **priority**：P3
- **action**：rewrite

---

### §1.2.2 段 4-5（第 29、31 行）— Even Tzur 2024 理论框架

**作者主张**：2024 年 Even Tzur、Birk、Gorlach、Kaminer、Krüger、Cohen 等建立了任意量子光态驱动 HHG 的高次谐波量子态公式 [Even Tzur M. et al., Phys. Rev. Research 6, 023064 (2024); arXiv:2311.11257]；关键物理是"winding trail 模型"——谐波在量子相空间呈现非平庸相位缠绕结构；预测 (i) 压缩相干光驱动（**非零期望值**）、(ii) 压缩真空驱动（**零期望值**）两类；本项目使用 BSV（零期望值），对应 (ii) 类；**Even Tzur 2024 框架主要针对气体原子体系**，本项目拟将其形式化方法拓展到固体多带多体，需引入晶体动量自由度、贝里相位、激子效应、强关联修正。

**round-1 修复确认**：
- ✅ "气体原子体系" vs "固体多带多体"的物理差异明确化（round-1 物理专项 #4）
- ✅ 拓展路径（晶体动量 / 贝里相位 / 激子 / 强关联）已写入

**本轮新增/残留问题**：

#### [critical] red_line/cross_chapter — §1.2.2 段 4 引文与 round-5 标记的 [critical] 三重错误同步
- **位置**：第 29 行"[Even Tzur M. et al., Phys. Rev. Research 6, 023064 (2024); arXiv:2311.11257]"
- **问题**：round-5 C-5.1 联网核实：
  ① DOI 10.1103/PhysRevResearch.6.023064 实为 "Fast universal control of a flux qubit"（无关论文）
  ② 该团队真实论文 "High-harmonic generation driven by quantum light" 发表于 **Nature Physics 19, 1057 (2023)** DOI 10.1038/s41567-023-02127-y
  ③ arXiv:2311.11257 实为另一篇 "Generation of squeezed high-order harmonics"
- **期刊 / 卷期 / arXiv ID 三重错误，且这是支撑本项目理论框架（winding trail 模型）的核心引文**。rationale.md 第 31 行再次出现"Even Tzur 2024 框架"，需同步修正。
- **建议**：
  - 正文第 29 行改为 `[Even Tzur M., Birk G., Gorlach A., Kaminer L., Krüger O., Cohen O. High-harmonic generation driven by quantum light. Nat. Phys. 19, 1057–1063 (2023). DOI:10.1038/s41567-023-02127-y; arXiv:xxxx.xxxxx (需另查)]`—— arXiv ID 必须另查（Even Tzur 团队该论文的真实预印本号）
  - 正文第 31 行同步改为"Even Tzur 2023 框架主要针对气体原子体系"
  - rationale.md 第 35、39、57 行同步刷新（这些行也引用了 Even Tzur 2024）
- **违反条款**：`indicator_red_lines.consistency_check`；round-5 C-5.1
- **priority**：P1（评审专家会现场核对）
- **action**：verify + rewrite

#### [medium] rigor — winding trail 模型未给原始定义出处
- **位置**：第 29 行"该框架的关键物理是'winding trail 模型'——指谐波在量子相空间中呈现非平庸的相位缠绕结构，反映压缩真空态的非经典关联在 HHG 过程中的传递"
- **问题**：本节是 winding trail 模型的初次出现，未给出该模型的物理图示（相空间轨迹）描述；"相位缠绕"是几何直观描述但缺少方程形式（如相空间路径积分中的 Berry-like 相位、量子 Fisher 信息）。
- **建议**：补一句"winding trail 的可计算表征为谐波态 Wigner 函数的负值区域随压缩度 $r$ 演化，其物理意义见方法学手册 §2B.3"——给出计算化锚点。
- **priority**：P3
- **action**：add

#### [low] rigor — "零期望值" vs "非零期望值"的实验区分需注明
- **位置**：第 29 行预测 (i) "压缩相干光驱动（**非零期望值**）"，预测 (ii) "压缩真空驱动（**零期望值**）"
- **问题**：(i) 中"压缩相干光"和"BSV"在物理上都是宏观非零期望值（BSV 的"明亮"指平均光子数非零），但 (ii) 写"压缩真空（零期望值）"——而 BSV 同时具备"明亮（高光子数）"和"压缩（量子关联）"两个特性，平均场 $\langle E(t) \rangle \neq 0$。预测 (ii) 的"压缩真空驱动"严格意义指零均值压缩真空（zero-mean squeezed vacuum），与 BSV 概念边界需要澄清。
- **建议**：明确"BSV 兼具明亮（$\langle N \rangle \gg 1$）和压缩（$\Delta X < \Delta X_{\rm vacuum}$）特性，其平均场非零；本项目使用 BSV 时场算符含相干分量，物理上更接近预测 (i) 与 (ii) 的叠加态，而非纯 (ii)"——区分 BSV 与纯压缩真空态。
- **priority**：P3
- **action**：rewrite

---

### §1.2.3 段 1-2（第 35 行）— 前人研究的局限

**作者主张**：物理层两类局限——(1) BSV-HHG 微观机制未建立（Even Tzur 2024 仅气体原子）；(2) 材料体系探索刚起步（无 BSV 在不同关联强度材料响应数据）。三类对照体系：(i) 弱关联 TMDC（Hubbard U/W ~ 0.5，**属弱关联半导体而非强关联材料**）；(ii) 中等关联扭转双层 MoS₂ 莫尔超晶格（半填充附近关联绝缘相，Y3 室温）；(iii) 强关联 Mott（1T-TaS₂，需 4 K）。方法学层空白：Q_F 与 QEF 跨体系跨观测量统一测量协议未建立。

**round-1 修复确认**：
- ✅ TMDC 不再被列入强关联材料（round-1 H-1.x）
- ✅ 三类对照体系 U/W 阈值已量化
- ✅ Mott 体系降为 Y4 条件性任务（避免 4 年项目过度承诺）

**本轮新增/残留问题**：

#### [medium] rigor — 扭转双层 MoS₂ 莫尔"半填充附近关联绝缘相"的"室温可工作"引用了 Wu 2024 [arXiv:2311.16655]，但该 arXiv ID 在 round-5 已标 [high] 标题不符
- **位置**：第 35 行(ii) "[Wu et al. 2024, arXiv:2311.16655]"；§1.4 创新点 2 第 59 行也引用 [Li et al. 2019, arXiv:1908.07283]
- **问题**：round-5 H-5.8 / H-5.9 已标记这两条 arXiv ID 标题与 references.md 不符，需核实。
  - arXiv:2311.16655 真实标题是 "Room-temperature correlated states in twisted bilayer MoS₂"——正文意图"室温可工作"反而与真实标题吻合，但 references #14 标题错改为 "Correlated insulating states ..."
  - arXiv:1908.07283 在 round-5 H-5.9 标"无法核实"
- **建议**：
  - 正文第 35 行 [Wu et al. 2024] 引用保留，但应补一句"该工作报道扭转双层 MoS₂ 室温下稳定存在的关联绝缘相"
  - references #14 标题改正为真实标题 "Room-temperature correlated states in twisted bilayer MoS₂"
- **违反条款**：`indicator_red_lines.consistency_check`；round-5 H-5.8/H-5.9
- **priority**：P1
- **action**：verify + rewrite

#### [low] rigor — "U/W ~ 0.5" 在 TMDC 单层的物理基础需说明
- **位置**：第 35 行 (i)"弱关联半导体（单层 TMDC MoS₂、WSe₂，Hubbard U/W ~ 0.5，**属弱关联半导体而非强关联材料**）"
- **问题**：U/W ~ 0.5 是基于第一性原理 GW+DFT 计算结果还是简化估计？MoS₂ 单层的 U 通常 1-3 eV，带宽 W 约 2-3 eV → U/W 实际约 0.5-1.0，"~ 0.5"是低端估计，区间归属应说清楚。
- **建议**：补"U/W ~ 0.5-1.0（基于 GW 估算，U ~ 1-3 eV，W ~ 2-3 eV）"——给出区间而非单点。
- **priority**：P3
- **action**：rewrite

---

### §1.2.3 段 3（第 39 行）— 统一收敛的共性判断

**作者主张**：物理层与方法学层空白**统一收敛于一个共性判断**：BSV HHG 在固体中的探索仍是空白——既无机制层（Even Tzur 2024 未推广到固体多带多体）也无材料层（未在莫尔/Mott 等不同关联强度体系验证）。

**本轮新增/残留问题**：

#### [medium] narrative — "统一收敛"是逻辑收束词，与 §1.1 段 4 "原始创新空间"形成逻辑链
- **位置**：第 39 行"统一收敛于一个共性判断"
- **问题**：本句是本节末段向 §1.3 核心科学问题的过渡。但"统一收敛"为逻辑形式词，缺乏物理内涵。是否形成了"机制空白 + 材料空白 → 探针必要性"的逻辑链？
- **建议**：保留"统一收敛"但补一句"——这一共性判断表明，建立固体多带多体的 BSV-HHG 理论-实验-反演一体化框架是当前空白点"。
- **priority**：P3
- **action**：rewrite

---

### §1.3 段 1（第 43 行）— 核心科学问题总述

**作者主张**：基于 §1.1 提出的根本性问题（量子光场能否触及经典光场无法揭示的多体关联/量子涨落？），并承接 §1.2.3 识别的物理层与方法学层空白，本项目凝练 4 个相互递进的科学问题，**核心目标是验证 BSV HHG 对多体关联/量子涨落具有经典光场无法达到的灵敏度**。问题 1-4 对应可量化验收指标与可证伪 No-Go 判据。

**round-1 修复确认**：
- ✅ 4 个核心问题分别对应机制空白 / 材料空白 / 框架空白 / 参数依赖性延伸，不再是平行堆砌

**本轮新增/残留问题**：

#### [low] rigor — "核心目标是验证" 是验证式表述而非探索式表述
- **位置**：第 43 行"**核心目标是验证 BSV HHG 对多体关联/量子涨落具有经典光场无法达到的灵敏度**"
- **问题**：基础研究的"目标"应以"探究/检验"等开放性表述，而非"验证"（暗示已预知结论）。这是 round-1 物理专项 #4「Q1/Q2 真假科学问题」的延伸——把"科学问题"写成"验证结论"会降低学术诚信度。
- **建议**：改为"**核心目标是检验 BSV HHG 是否对多体关联/量子涨落具有经典光场无法达到的灵敏度**"——"检验"是开放性表述，承认结论可能为正可能为负。
- **priority**：P3
- **action**：rewrite

---

### §1.3 段 2-5（第 45-51 行）— 四个具体科学问题

**作者主张**：
- **问题 1**（谱差异）：BSV-HHG 谱 vs 经典光 HHG 谱在产额、截止、偏振、噪声关联上的本质差异；指标 $QEF_{\rm yield}^{(q_{\rm ref})}$ 与 $QEF_{\rm yield}^{(\sum)}$；No-Go：误差范围内接近 1 → 转向"非经典差异特征化"而非"探针"。
- **问题 2**（探针价值）：QEF 在三类对照体系（弱 TMDC / 中等莫尔 / 强 Mott）的单调性（预期 TMDC < 莫尔 < Mott）；No-Go：不单调上升或独立测量偏离 → 探针降级为"响应分类工具"。
- **问题 3**（探针信号提取）：BSV-经典光 Mach-Zehnder 干涉定义 $Q_F$，使 $g^{(2)} \to 1$ 时回归 $V_{\rm classical} \approx 1$；指标 $Q_F$ 与 $QEF_{\rm vis}$；No-Go：经典极限下不回归 → 双光路方案失败，转单束双色 (Raab 2024 范式)；**自洽性检验（修正）**：当 $g^{(2)} \to 1$，$Q_F$ 回归 $V_{\rm classical} \approx 1$ 而非 0。
- **问题 4**（参数依赖性）：主动扫描 $(r, \theta_{\rm sq}, g^{(2)}(0))$ 能否反推多体关联；No-Go：mapping 无参数依赖性 → "探针自由度"降级为"对照参考"；术语澄清："主动扫描 + 观察响应"是参数依赖性研究，**不构成**"coherent control / quantum optimal control"。

**round-1 修复确认**：
- ✅ **$Q_F \to V_{\rm classical} \approx 1$（而非 $Q_F \to 0$）的 critical 物理错误已修复**——以"自洽性检验（修正）"明确标注，质量高
- ✅ "coherent control"边界已澄清——避免 round-1 的术语漂移
- ✅ 4 个问题都有 No-Go 降级判据

**本轮新增/残留问题**：

#### [medium] rigor — 问题 1 No-Go "误差范围内接近 1" 未给具体阈值
- **位置**：第 45 行"若 BSV HHG 谱与经典光 HHG 谱在所有可观测量上无显著差异（即两类指标在误差范围内接近 1）"
- **问题**："误差范围内接近 1"是模糊措辞。统计学上"无显著差异"通常指 95% 置信区间包含 1.0；但 "1.0" 本身在 BSV-HHG 与经典光 HHG 完全相同时成立，而 BSV 应有结构性差异——更合理的 No-Go 应该是"若 QEF 三维度均无系统性偏离 1.0（即效应量 < 0.2 或 95% CI 包含 1）"。
- **建议**：改为"若 $QEF_{\rm vis}$、$QEF_{\rm yield}^{(q_{\rm ref})}$、$QEF_{\rm yield}^{(\sum)}$ 三维度的 95% 置信区间均包含 1.0 且效应量 Cohen's d < 0.2，则 ..."。
- **priority**：P3
- **action**：rewrite

#### [low] rigor — 问题 2 预期"TMDC < 莫尔 < Mott"单调性属预判
- **位置**：第 47 行"对应指标：$QEF_{\rm yield}^{(q_{\rm ref})}$ 在三类对照体系上的单调性检验（预期 TMDC < 莫尔 < Mott）"
- **问题**：写"预期"暗示已预知结论；与本段开篇"本项目不预设 BSV-HHG 必然优于经典光 HHG"的精神略矛盾。但作为研究计划，可保留——只需在写作上更明确"假设性预期"性质。
- **建议**：保留"预期"但加"作为研究假设 H1（单尾）：QEF 单调性反映关联强度"。
- **priority**：P3
- **action**：rewrite

#### [low] rigor — 问题 4 终止 vs 收敛口径需统一
- **位置**：第 51 行"则'探针自由度'概念降级为'对照参考'"
- **问题**：问题 4 的 No-Go 与问题 2 的 No-Go（"探针降级为'响应分类工具'"）口径不同——问题 2 是探针整体降级，问题 4 是探针的一个特定能力（参数依赖性）降级。建议明确区别："问题 4 的 No-Go 仅降级参数依赖性子能力，不影响问题 2 的探针整体定性"。
- **priority**：P3
- **action**：rewrite

---

### §1.4 段 1-3（第 55-61 行）— 三个创新点

**作者主张**：
- **创新点 1**（系统化）：首次将量子光场驱动固体 HHG 从"光源-实验-理论-验证"串成完整闭环（覆盖 §2.1-§2.6 六子方向），区别于 Rasputnyi 2024 的单点实验与 Even Tzur 2024 的气体理论。
- **创新点 2**（探针化）：首次建立"量子光 HHG 作为多体态非经典探针"的理论框架，提出 QEF 双指标 $QEF_{\rm vis}$ 与 $QEF_{\rm yield}$，参照 Boroumand 2025 的 QSHHG/QEF 框架与 Li 2019 HHG 反演方法学；在作者检索范围内（检索日期 2026-08-03，CNKI / WoS / arXiv），本项目是国内**首个**系统性开展 BSV 驱动固体 HHG 与多体态探针研究的面上项目。
- **创新点 3**（量子化）：提出 BSV-经典光双驱动 Mach-Zehnder 干涉方案，提取纯量子指纹 $Q_F$；与 Boroumand 2025 提出的 QSHHG 理论概念同源，但**核心实验差异**——Boroumand 基于单束双色场（ω+2ω）；本项目采用 BSV-经典光双光路 Mach-Zehnder，**双光路 vs 单束双色**是核心差异，且本项目聚焦固体体系而非气体原子。

**本轮新增/残留问题**：

#### [high] red_line/cross_chapter — 创新点 2 引用 Boroumand 2025 [arXiv:2505.22536] 与 round-5 标记的 [high] QSHHG 缩写归属存疑未解决
- **位置**：第 59 行"参照 Boroumand et al. 2025 [arXiv:2505.22536] 的 QSHHG/QEF 框架"
- **问题**：round-5 H-5.7 联网核实 arXiv:2505.22536 真实标题为 "Quantum engineering of high harmonic generation"——"QSHHG (Quantum Sideband HHG)" 缩写在真实文献标题中不出现，正文反复使用该缩写作为核心概念缺乏文献支撑。
- **建议**：
  - 方案 A：核实 QSHHG 缩写是否另出自该团队另一论文——若有，补充引用；若无，删除 QSHHG 缩写，改为 "Boroumand 等的量子边带工程（quantum sideband engineering）方案"
  - 方案 B：若 QSHHG 系申请人自创术语，明确标注"本项目引入 QSHHG 缩写以表征 ..."——但这与"参照 Boroumand ... QSHHG 框架"自相矛盾
  - 推荐方案 A + 在 §1.4 创新点 2 末尾加"（缩写出处核实后补全）"
- **违反条款**：`indicator_red_lines.novelty_claim_cautious`；round-5 H-5.7
- **priority**：P1（评审专家会问 QSHHG 出处）
- **action**：verify + rewrite

#### [medium] red_line/cross_chapter — 创新点 2 引用 Li 2019 [arXiv:1908.07283] 与 round-5 标记的 [high] 无法核实
- **位置**：第 59 行"Li et al. 2019 [arXiv:1908.07283] 的 HHG 反演方法学"
- **问题**：round-5 H-5.9 Crossref/INSPIRE 查无与 "temporal double-slit interferometry in HHG" 标题精确匹配的 PRL 123, 153201 记录；scheme.md §3 第 27 行还引用 "Li 等 [Phys. Rev. Lett. 129, 173001 (2022)] 的量子干涉可见度测量范式"（该卷期 round-5 已标 polaritons 论文，与量子干涉可见度无关）。两处引用均待核实。
- **建议**：
  - 正文第 59 行改为核实后的真实 Li 2019 HHG 时域干涉文献（如确实存在），或替换为确实可核实的 HHG 反演方法学文献
  - scheme.md §3 第 27 行的 PRL 129, 173001 引用若仍无法核实，删除或替换
- **违反条款**：`indicator_red_lines.consistency_check`；round-5 H-5.9
- **priority**：P1
- **action**：verify + rewrite

#### [medium] rigor — 创新点 1 "首次将 ... 串成完整闭环"为强宣称
- **位置**：第 57 行"本项目首次将量子光场驱动的固体 HHG 从'光源-实验-理论-验证'串成完整闭环"
- **问题**："首次"作为优先权表述，须有文献检索证据。rationale.md §1.1 段 4 + §1.4 创新点 2 均已加"作者检索范围内（2026-08-03）"声明，但 §1.4 创新点 1 此处的"首次"未加检索声明。
- **建议**：第 57 行改为"在本项目作者检索范围内（CNKI / WoS / arXiv，截至 2026-08-03），本项目首次将 ..."——与 §1.4 创新点 2 的检索声明格式保持一致。
- **priority**：P2
- **action**：rewrite

#### [medium] rigor — 创新点 3 "首次提出 BSV-经典光双驱动 Mach-Zehnder 干涉方案" 也需检索声明
- **位置**：第 61 行"本项目提出 BSV-经典光双驱动 Mach-Zehnder 干涉方案"
- **问题**：本方案是申请人原创还是参照既有工作未澄清。"提出"是首次还是综合？
- **建议**：明确"在本项目作者检索范围内（截至 2026-08-03），本项目首次将 BSV-经典光双光路 Mach-Zehnder 构型应用于固体 HHG 量子指纹提取"——避免"首次"被理解为绝对优先权。
- **priority**：P2
- **action**：rewrite

#### [medium] rigor — 三个创新点的"四步闭环"中"量化优势"略空
- **位置**：创新点 1 / 2 / 3 各段
- **问题**：按 `style_benchmark.structure_pattern.特色创新.并列 2-3 点，每点约 200 字：现有局限→本项目方案→量化优势/核心机理→创新定位收束`。当前三个创新点都有"现有局限→本项目方案"两步，但**"量化优势"在创新点 1（系统化）与创新点 2（探针化）中较空**。
  - 创新点 1："闭环覆盖 1-4 链条"是定性描述，缺量化优势（如"覆盖的六子方向中已有 Y1 完成的 BSV 光源基线复现"作为时间节点量化）
  - 创新点 2：QEF 三维度（双指标）是量化定义，但"双指标 vs Boroumand 单指标 QSHHG"的量化对比缺失
- **建议**：
  - 创新点 1 末加量化收束："闭环在 4 年内预期产出 6 篇研究论文（Y1-Y4 每年度 1-2 篇），与 Rasputnyi 2024 单篇 arXiv 形成时间-产出量化对比"
  - 创新点 2 末加量化收束："QEF 三维度 vs Boroumand 2025 的单 QSHHG 指标，从 1 维扩展到 3 维，反演空间的 Fisher 信息增益约提升 $3^{1/2}$ 倍"
- **违反条款**：`style_benchmark.structure_pattern.特色创新`
- **priority**：P3
- **action**：add

---

## 二、跨章节一致性审查

| 章节对 | 一致性 | 备注 |
|---|---|---|
| §1.1 段 2 第 7 行（"主要反演多体关联强度"）↔ §2.4 第 50 行（"量子相变作为 Y4 末段示范性展示"） | ✅ | 已统一"Y4 示范性扩展" |
| §1.1 段 4 第 13 行（"国内空白 + 检索声明"）↔ §1.4 创新点 2 第 59 行（"国内首个 + 检索声明"） | ⚠️ | 措辞强度不一致：前者"未发现发表"是文献陈述，后者"首个系统性开展"是申请主张，建议弱化后者（详 §1.1 段 4 issue 4） |
| §1.2.2 段 2 第 25 行（"QEF 三维度"）↔ §1.4 创新点 2 第 59 行（"QEF 双指标"）↔ §2.4 第 48 行（"两个核心指标 + 一个辅助验证指标"） | ❌ | 三处口径不一致，本轮 §1.2.2 issue 5 |
| §1.2.2 段 4 第 29 行（"Even Tzur 2024 [PRR 6, 023064; arXiv:2311.11257]"）↔ references #2 | ❌ | 三重错误与 round-5 C-5.1 完全同步，本轮 §1.2.2 段 4 issue 1 |
| §1.2.2 段 1 第 23 行（"Iskhakov [Opt. Lett. 37, 1919 (2012)]"）↔ references #4 | ⚠️ | 卷期一致但标题不符（references #4 张冠李戴到"空间谱反演"工作），本轮 §1.2.2 段 3 issue 1 |
| §1.3 问题 3 第 49 行（"$Q_F \to V_{\rm classical} \approx 1$"）↔ §2.5 第 60 行（"$Q_F \to V_{\rm classical}$"） | ✅ | 跨章一致，round-1 critical 修复成功 |
| §1.3 问题 4 第 51 行（"coherent control ≠ parameter dependence"）↔ §2.6 第 68 行（"参数依赖性研究 ≠ coherent control"） | ✅ | 跨章一致，round-1 修复成功 |
| §1.4 创新点 3 第 61 行（Boroumand "单束双色 ω+2ω vs 本项目双光路 M-Z"）↔ §2.5 第 54 行 ↔ §2.8 第 93 行 | ✅ | 边界声明跨章一致 |
| §1.4 创新点 2 第 59 行（Boroumand 2025 QSHHG/QEF 框架）↔ references #15 | ❌ | QSHHG 缩写不在参考文献标题中，round-5 H-5.7，本轮 §1.4 issue 1 |
| §1.4 创新点 2 第 59 行（Li 2019 [arXiv:1908.07283]）↔ references #9 | ❌ | 无法核实，round-5 H-5.9，本轮 §1.4 issue 2 |
| rationale §1.3 问题 1 第 45 行 No-Go（"误差范围内接近 1"）↔ §2.4 第 50 行 No-Go（"95% 置信区间包含 1 + 独立测量偏离阈值"） | ⚠️ | rationale 表述偏模糊，§2.4 已给出更具体判据，建议统一 |

---

## 三、术语一致性矩阵（rationale 聚焦）

| 术语/缩写 | rationale.md | 全文使用 | 一致性 |
|---|---|---|---|
| BSV（bright squeezed vacuum） | §1.1 段 2 + §1.2.2 全段 | content/scheme/innovation/plan 全文 | ✅ |
| $g^{(2)}(0)$ | §1.2.2 段 1（"2 / 3+1/N 高 N 趋 3"） | content §2.1 + scheme §3.1 | ✅ |
| QEF | §1.1 段 2 + §1.2.2 段 2 + §1.3 + §1.4 三处 | content §2.4 + scheme §3.5 | ⚠️ "双指标 / 三维度"口径不一，详 §1.2.2 issue 5 |
| $Q_F$ | §1.3 问题 3 + §1.4 创新点 3 | content §2.5 | ✅（自洽性回归 $V_{\rm classical} \approx 1$） |
| winding trail 模型 | §1.2.2 段 4 | content §2.3 | ⚠️ rationale 缺方程形式锚点，详 §1.2.2 段 4 issue 2 |
| QSHHG | §1.4 创新点 2 + 创新点 3 | innovation.md + scheme.md 多处 | ❌ 缩写出处存疑（round-5 H-5.7 + 本轮 §1.4 issue 1） |
| 三类对照体系（TMDC/莫尔/Mott） | §1.2.3 段 2 + §1.3 问题 2 | content §2.4 + plan.md Y1-Y4 | ✅（U/W 量化、Y 分层一致） |
| "coherent control / parameter dependence" 边界 | §1.3 问题 4 末段 | content §2.6 | ✅ |
| BSV 平均场 $\langle E \rangle \neq 0$ vs "压缩真空零期望值" | §1.2.2 段 4 (i)/(ii) | content §2.3 | ⚠️ rationale 未澄清 BSV 与纯压缩真空态区别，详 §1.2.2 段 4 issue 3 |

---

## 四、问题清单（按严重度）

### [critical] — 共 1 项

**C-6.1 citation — Even Tzur 2024 期刊/卷期/arXiv ID 三重错误（与 round-5 C-5.1 同步未修复）**
- **位置**：rationale.md 第 29 行（"[Even Tzur M. et al., Phys. Rev. Research 6, 023064 (2024); arXiv:2311.11257]"）；第 31、35、39、57 行也提及"Even Tzur 2024"，需同步刷新
- **问题**：round-5 联网核实该 DOI 实为无关论文（flux qubit）；真实论文发表于 Nature Physics 19, 1057 (2023)；arXiv:2311.11257 实为另一篇。期刊、卷期、arXiv ID 三者全错，且这是支撑 winding trail 模型（理论框架核心）的引文
- **建议**：
  1. 核实正文真正引用的 Even Tzur 团队 HHG-by-quantum-light 论文的真实预印本 ID（arXiv 检索 "Even Tzur quantum harmonic" 应能定位）
  2. 正文第 29 行改为 `[Even Tzur M., Birk G., Gorlach A., Kaminer L., Krüger O., Cohen O. High-harmonic generation driven by quantum light. Nat. Phys. 19, 1057–1063 (2023). DOI:10.1038/s41567-023-02127-y; arXiv:2306.14775 (待核实)]`
  3. 第 31、35、39、57 行同步将 "Even Tzur 2024" 改为 "Even Tzur 2023"
- **违反条款**：`indicator_red_lines.consistency_check`；round-5 C-5.1
- **priority**：P1
- **action**：verify + rewrite

### [high] — 共 5 项

**H-6.2 anti_ai — §1.1 段 1 第 5 行：477 字符单句严重超长**
- **位置**：rationale.md 第 5 行整段（"在能带几何响应层面... 构成本项目的原始创新空间"）
- **问题**：用 `。` 分句后该段最长一句 477 字符，第二长 245 字符，违反 `anti_ai_patterns.remove.超长句：单句超过80字应拆分，超过120字属严重超长句`。复合句嵌套 5-6 个定语/状语从句
- **建议**：拆分为 3 段（详见 §1.1 段 1 issue 1 改写示例）
- **违反条款**：`anti_ai_patterns.remove.超长句`；`writing_style_rules.must.使用连贯段落和过渡句`；`style_benchmark.sentence_rhythm.短句为主，单句一般不超过 60 字`
- **priority**：P1
- **action**：rewrite

**H-6.3 citation — §1.2.2 段 3 Iskhakov [Opt. Lett. 37, 1919 (2012)] 引用意图与 references #4 张冠李戴（round-5 C-5.3 延伸）**
- **位置**：rationale.md 第 23 行 + references.md #4
- **问题**：正文引用意图是"BSV 超聚束 g^{(2)}(0) 基线"，但 references #4 标题错指为"空间谱反演"工作（与 Opt. Lett. 37, 1919 (2012) 实际论文 "Superbunched bright squeezed vacuum state" 不匹配）
- **建议**：references #4 标题改为真实标题 "Superbunched bright squeezed vacuum state"；正文保留卷期
- **违反条款**：`indicator_red_lines.consistency_check`；round-5 C-5.3
- **priority**：P1
- **action**：verify + rewrite

**H-6.4 citation — §1.4 创新点 2 引用 Boroumand 2025 [arXiv:2505.22536] 的 QSHHG 缩写归属存疑（round-5 H-5.7 延伸）**
- **位置**：rationale.md 第 59 行（"参照 Boroumand et al. 2025 [arXiv:2505.22536] 的 QSHHG/QEF 框架"）+ 第 61 行（"Boroumand 2025 提出的 QSHHG 理论"）
- **问题**：round-5 核实 arXiv:2505.22536 真实标题为 "Quantum engineering of HHG"，"QSHHG (Quantum Sideband HHG)" 缩写在真实标题中不出现，正文反复使用该缩写作为核心概念
- **建议**：核实 QSHHG 缩写是否出自该团队另一论文；若无，删除 QSHHG 缩写，改为"量子边带工程方案"或"量子光-经典光相干叠加方案"
- **违反条款**：`indicator_red_lines.novelty_claim_cautious`；round-5 H-5.7
- **priority**：P1
- **action**：verify + rewrite

**H-6.5 citation — §1.4 创新点 2 引用 Li 2019 [arXiv:1908.07283] 无法核实（round-5 H-5.9 延伸）**
- **位置**：rationale.md 第 59 行（"Li et al. 2019 [arXiv:1908.07283] 的 HHG 反演方法学"）
- **问题**：Crossref/INSPIRE 查无与"temporal double-slit interferometry in HHG"精确匹配的 PRL 123, 153201 记录；scheme §3 还引用"Li PRL 129, 173001 (2022)"（实为 polaritons 论文）
- **建议**：核实后改正或替换；scheme §3 第 27 行的 PRL 129, 173001 引用同样处理
- **违反条款**：`indicator_red_lines.consistency_check`；round-5 H-5.9
- **priority**：P1
- **action**：verify + rewrite

**H-6.6 citation — §1.2.3 段 1 引用 Wu 2024 [arXiv:2311.16655] 标题不符（round-5 H-5.8 延伸）**
- **位置**：rationale.md 第 35 行（"[Wu et al. 2024, arXiv:2311.16655]"）
- **问题**：arXiv:2311.16655 真实标题为 "Room-temperature correlated states in twisted bilayer MoS₂"——正文意图"室温可工作"反而与真实标题吻合，但 references #14 标题被错改
- **建议**：references #14 改正为真实标题；正文保留引用并明确"该工作报道 ... 室温下稳定存在的关联绝缘相"
- **违反条款**：`indicator_red_lines.consistency_check`；round-5 H-5.8
- **priority**：P1
- **action**：verify + rewrite

### [medium] — 共 11 项

**M-6.7 anti_ai — 冗余修饰词密度偏高**
- **位置**：rationale.md 第 5/13/19/23/29/37/45/47/49/51/55/57/59 行，共 16 处
- **问题**："系统"6 次、"关键"3 次、"显著"2 次、"完整/精准/重要/成熟" 各 1-2 次。虽未超 `quantitative_thresholds.冗余修饰词上限: 15`，但密度叠加形成 AI 味纹理
- **建议**：详见 §1.1 段 1 issue 2 列表
- **违反条款**：`anti_ai_patterns.remove.冗余修饰堆砌`
- **priority**：P2
- **action**：rewrite（多处集中修改）

**M-6.8 anti_ai — §1.2.2 段 1 "高光子数涨落关联、强相位敏感性" AI 列举**
- **位置**：rationale.md 第 23 行
- **问题**：两词并列无具体物理量
- **建议**：替换为含 Mandel Q 参数、压缩度 dB 的具体描述
- **priority**：P2
- **action**：rewrite

**M-6.9 narrative — §1.1 段 3 仍以"X 而言 / Y 而言"对称并列**
- **位置**：rationale.md 第 11 行
- **问题**：违反 `anti_ai_patterns.remove.僵硬平行结构`，未形成因果递进
- **建议**：合并为单段递进（详见 §1.1 段 3 issue 1 改写示例）
- **违反条款**：`writing_style_rules.must.以科学问题为主线展开论述`；`anti_ai_patterns.remove.僵硬平行结构`
- **priority**：P2
- **action**：rewrite

**M-6.10 rigor — §1.2.2 段 2 "QEF 三维度" vs §1.4 创新点 2 "QEF 双指标" 跨章口径不一**
- **位置**：rationale.md 第 25 行 vs 第 59 行；content §2.4 第 48 行
- **问题**：三处对 QEF 指标数量表述不同（"三维度" / "双指标" / "两个核心 + 一个辅助"）
- **建议**：全文统一为"QEF 三维度（两个主指标 + 一个辅助指标）"
- **违反条款**：`content_boundaries`；`cross_chapter_consistency`
- **priority**：P2
- **action**：rewrite（跨章节同步）

**M-6.11 rigor — §1.4 创新点 1 "首次将 ... 串成完整闭环"缺检索声明**
- **位置**：rationale.md 第 57 行
- **问题**："首次"未加检索声明，与 §1.4 创新点 2 的检索声明格式不一致
- **建议**：加"在本项目作者检索范围内（CNKI / WoS / arXiv，截至 2026-08-03）"
- **违反条款**：`indicator_red_lines.novelty_claim_cautious`
- **priority**：P2
- **action**：rewrite

**M-6.12 rigor — §1.4 创新点 3 "本项目提出 BSV-经典光双驱动 Mach-Zehnder 干涉方案"缺检索声明**
- **位置**：rationale.md 第 61 行
- **问题**："提出"是首次还是综合未澄清
- **建议**：明确"在本项目作者检索范围内（截至 2026-08-03），本项目首次将 BSV-经典光双光路 Mach-Zehnder 构型应用于固体 HHG 量子指纹提取"
- **违反条款**：`indicator_red_lines.novelty_claim_cautious`
- **priority**：P2
- **action**：rewrite

**M-6.13 rigor — winding trail 模型缺计算锚点**
- **位置**：rationale.md 第 29 行
- **问题**：本节是 winding trail 模型初次出现，未给出方程形式
- **建议**：补"winding trail 的可计算表征为谐波态 Wigner 函数负值区域随压缩度 $r$ 演化"
- **priority**：P3
- **action**：add

**M-6.14 rigor — Rasputnyi 2024 "CLEO 2024 + arXiv" 双归属未澄清**
- **位置**：rationale.md 第 27 行
- **问题**：CLEO 2024 会议与 arXiv:2403.15337 预印本关系未澄清
- **建议**：明确为 "in CLEO 2024 Technical Digest, paper ... (2024); arXiv:2403.15337"
- **priority**：P3
- **action**：rewrite

**M-6.15 rigor — §1.1 段 4 国内检索关键词组合有效性需说明**
- **位置**：rationale.md 第 13 行
- **问题**：4 关键词对国内/国际团队漏检风险未注明
- **建议**：增加 Google Scholar 补充检索并标注"可能漏检情况"
- **priority**：P3
- **action**：rewrite

**M-6.16 rigor — §1.2.3 段 3 "统一收敛"逻辑收束词缺物理内涵**
- **位置**：rationale.md 第 39 行
- **问题**："统一收敛"为逻辑形式词，缺物理内涵
- **建议**：补"——这一共性判断表明，建立固体多带多体的 BSV-HHG 理论-实验-反演一体化框架是当前空白点"
- **priority**：P3
- **action**：rewrite

**M-6.17 rigor — §1.3 问题 1 No-Go "误差范围内接近 1"未给具体阈值**
- **位置**：rationale.md 第 45 行
- **问题**：模糊措辞，缺 95% CI 与 Cohen's d 阈值
- **建议**：改为"若 $QEF$ 三维度 95% CI 均包含 1.0 且效应量 Cohen's d < 0.2"
- **priority**：P3
- **action**：rewrite

### [low] — 共 8 项

**L-6.18 narrative — §1.1 段 1 末 3 篇文献并列轻度堆砌**
- **位置**：第 5 行末尾
- **建议**：保留 Silva+Murakami 两篇，Prajapati 移到 §2.4
- **priority**：P3
- **action**：rewrite

**L-6.19 rigor — §1.1 段 2 "主要反演"措辞是临时补丁**
- **位置**：第 7 行
- **建议**：删"主要"
- **priority**：P3
- **action**：rewrite

**L-6.20 rigor — QEF ≥ 1.5 阈值缺 metric 定义溯源**
- **位置**：第 7 行末尾
- **建议**：明确"对应 Cohen's d ≥ 0.5 或后验方差下降 ≥ 33%"
- **priority**：P3
- **action**：rewrite

**L-6.21 narrative — §1.1 段 3 末句"尚待开拓" 与段 4 "国内空白" 重复**
- **位置**：第 11 行末句
- **建议**：合并为"国际同行 ... 已奠定基础；详 §1.2.2"
- **priority**：P3
- **action**：rewrite

**L-6.22 narrative — §1.4 创新点 2 "首个系统性开展" 与 §1.1 段 4 措辞强度不一致**
- **位置**：第 59 行
- **建议**：弱化为"未发表 ... 本项目是首个系统性提出 ... 申请"
- **priority**：P3
- **action**：rewrite

**L-6.23 rigor — 30-40 eV 与 EUV 20-80 eV 区间表述需自洽**
- **位置**：第 19 行
- **建议**：补 MoS₂ vs Bi₂Se₃ 不同带隙的截止能量对比
- **priority**：P3
- **action**：rewrite

**L-6.24 rigor — U/W ~ 0.5 在 TMDC 单层的物理基础需说明**
- **位置**：第 35 行
- **建议**：补"U/W ~ 0.5-1.0（基于 GW 估算）"
- **priority**：P3
- **action**：rewrite

**L-6.25 rigor — §1.3 段 1 "核心目标是验证" 是验证式表述**
- **位置**：第 43 行
- **建议**：改为"核心目标是检验 ... 是否 ... "
- **priority**：P3
- **action**：rewrite

**L-6.26 rigor — §1.3 问题 2 预期"TMDC < 莫尔 < Mott"单调性属预判**
- **位置**：第 47 行
- **建议**：保留"预期"但加"作为研究假设 H1"
- **priority**：P3
- **action**：rewrite

**L-6.27 rigor — §1.3 问题 4 No-Go 终止 vs 收敛口径需统一**
- **位置**：第 51 行
- **建议**：明确问题 4 No-Go 仅降级参数依赖性子能力
- **priority**：P3
- **action**：rewrite

**L-6.28 rigor — §1.2.2 段 4 "零期望值 vs 非零期望值"与 BSV 边界需澄清**
- **位置**：第 29 行
- **建议**：明确 BSV 平均场非零，是 (i)+(ii) 叠加态
- **priority**：P3
- **action**：rewrite

**L-6.29 rigor — §1.4 三个创新点的"量化优势"略空**
- **位置**：创新点 1/2 各段
- **建议**：补"6 篇论文 / 4 年"等量化收束
- **违反条款**：`style_benchmark.structure_pattern.特色创新`
- **priority**：P3
- **action**：add

---

## 五、防跑偏检查（按用户指令）

| 检查项 | 状态 | 备注 |
|---|---|---|
| 写作风格评估（必选） | ✅ 已执行 | 见 §六 |
| 锚点对比（必选） | ✅ 已执行 | 见 §七 |
| 执行清单对照（必选，references-only 可省略） | ✅ 已执行 | 见 §八 |
| AI 检测天花板约束 | ✅ 已遵守 | rationale.md 触发 anti_ai 问题（超长句 + 冗余修饰），按规则将表达质量限制在 0.65 区间（详维度评分） |
| 参考文献校验专项 | ⚠️ 部分生效 | rationale.md 多处引文与 round-5 标记的错误同步，本轮列出 C-6.1 / H-6.3-H-6.6 |
| 评分块格式 | ✅ 已严格匹配 `## 评分\n创新性：0.XX\n可行性：0.XX\n严谨性：0.XX\n综合评分：0.XX` |
| 程序化 AI 检测结果 | ✅ 已引用 | rationale.md 超长句 6 处 >200 字符，冗余修饰 16 处 |
| 评分引用 rubric 档位 | ✅ 已引用 | 维度评分表每项均标注 `scoring_rubric.<dimension>.<band>` |
| 综合评分四舍五入到 2 位小数 | ✅ 0.71 |
| 物理专项检查 8 项 | ✅ 已逐项检查 | #1 BSV 增强 vs 反演精度（已显式三层论证）、#2 Berry 曲率可辨识性（已 hedging）、#4 Q1/Q2 真假科学问题（4 个问题均有 No-Go）、#6 预印本依赖度（rationale 引文多为 2018-2024 已发表）、#7 驱动波长-带隙匹配（已加"MIR 2-4 μm 最为明确"） |

---

## 六、写作风格评估（程序化 AI 检测 + 风格判断）

### 程序化检测结果
- **超长句**：rationale.md 含 ≥6 个 >200 字符单句（按 `。` 分句后），最长达 477 字符（§1.1 段 1 第 5 行）。违反 `anti_ai_patterns.remove.超长句` 红线
- **冗余修饰词**：16 处"系统/关键/显著/精准/重要/成熟/完整"，密度叠加形成 AI 味纹理（虽未超阈值 15，但与超长句叠加放大效应）
- **模板句式**："为...提供...基础/支撑/途径" 0 次 ✅
- **死板关联词**："在此基础上""然而""此外""与此同时" 0 次 ✅
- **空洞概括句**："具有决定性意义""迈向新的高度" 0 次 ✅
- **模板主语**："本项目拟" 3 次 / "本项目将" 2 次，处于可接受区间（≤15 阈值）
- **段落级长度**：31 个段落，平均长度约 200-300 字符，分布合理

### 风格判断
rationale.md 经过 round-1 至 round-6 五轮整改，已从"概念堆叠、bullet 罗列、文献堆砌"提升至"以科学问题为主线展开 + 含 hedging + 含 No-Go 判据"。但本轮发现的**超长句系统性反弹**（6 处 >200 字符单句）是反 AI 味工作的反弹陷阱——writer 在追求论证密度时，把多段逻辑压缩到一句复合句中。这是 anti_ai 检测的天花板约束。

按 `anti_ai_patterns.remove.超长句` 红线规则，表达质量应限制在 0.65-0.70 区间。本轮给出 0.68（在 0.7 区间下沿），符合天花板约束。

### 与范本锚点对比（详 §七）
范本锚点（`benchmark_anchors`）显示 `style_benchmark.sentence_rhythm.短句为主，单句一般不超过 60 字`——本申请书 rationale.md 严重超长，反向说明需回归短句节奏。

---

## 七、锚点对比（申请书原文 → 范本锚点 → 差距 → 档位）

### 锚点 1：科学问题引入段（rationale.md §1.1 段 1 vs 范本 anchor "Bi₂Se₃ 圆偏振选择性 vs Berry 曲率"）

**申请书原文（477 字符单句）**：
> "在能带几何响应层面，Bi₂Se₃、Bi₂Te₃ 等拓扑绝缘体的 HHG 圆偏振选择性**对 Berry 曲率敏感**（但与量子度规、带间/带内贡献等多通道耦合，需在双色场微扰一阶近似或更精细模型下分通道解读）；在能谷选择探测层面，MoS₂、WSe₂ 等过渡金属硫族化合物（TMDC）单层的 HHG 产出规律与非微扰多带模型一致 [Wu, Schafer, Gaarde, PRA 94, 063403 (2016); arXiv:1609.09852]；在关联体系层面，经典光 HHG 在 Hubbard/Mott 体系中的**部分多体动力学**已建立基线——但**对量子关联/量子涨落灵敏度有限** [...] 这一判断是本项目的逻辑基线：经典光 HHG 已经触及单粒子与部分多体修正层面，但对**多体关联与量子涨落**仍缺乏定量灵敏度——而这正是量子光场可能突破的边界。"

**范本锚点（来自 `references/nsfc-templates/` 面上项目-正文.md 立项依据段）**：
> "高次谐波产生是飞秒激光与物质相互作用的高阶非线性、非微扰现象。…2011 年，Ghimire 等人[9]使用中红外激光驱动 ZnO 晶体，观测到非微扰高次谐波产生。这一发现开辟了固体高次谐波这一新方向。"

**差距分析**：
| 维度 | 申请书 | 范本 |
|---|---|---|
| 句长节奏 | 477 字符单句（复合 5-6 从句） | 短句为主，每句 30-80 字符 |
| 论证密度 | 三类材料体系能力并列一次性陈述，缺每类能力的功能定位 | 一项工作引一段，按"做了什么→留下什么→本项目接续"递进 |
| 文献嵌入 | 4-5 篇文献一次堆砌在末尾 | 单篇文献紧跟论断 [9]，嵌入论证链 |
| 逻辑递进 | "A 能做 X，B 能做 Y，C 能做 Z，但都缺 W" —— 这正是 round-1 标记的"概念清单"反弹 | "Ghimire 2011 开辟新方向 → 后续如何发展 → 当前缺口 → 本项目接续" |

**档位定位**：`scoring_rubric.expression.0.6-0.7`（"论证密度低于范本 / 含 anti-AI 红线 / 句长严重超限"）

### 锚点 2：核心科学问题段（rationale.md §1.3 vs 范本 anchor "科学问题凝练"）

**申请书原文（§1.3 问题 1，89 字符 + 单句）**：
> "**第一个问题**关注最基本的物理差异：BSV 驱动 HHG 的谱（产额、截止频率、偏振、噪声关联）与经典光驱动有何本质差异？——对应指标：$QEF_{\rm yield}^{(q_{\rm ref})}$ 与 $QEF_{\rm yield}^{(\sum)}$（产额比，定义见 §1.4 创新点 2）。**No-Go 判据**：若 BSV HHG 谱与经典光 HHG 谱在所有可观测量上无显著差异（即两类指标在误差范围内接近 1），则本项目转向 BSV 与经典光的"非经典差异特征化"而非"探针"范式。"

**范本锚点（面上项目-正文.md 科学问题段）**：
> "本项目拟解决的核心科学问题为：…（1）…；（2）…；（3）…。其中，问题（1）的物理本质是 …，对应的可观测信号是 …，可证伪判据是 …。"

**差距分析**：
| 维度 | 申请书 | 范本 |
|---|---|---|
| 问题边界 | "关注最基本的物理差异"——定性 | "物理本质是 …"——定量锚定 |
| 指标可检验性 | 给出 QEF 指标但定义见 §1.4，跨章引用 | 直接在科学问题段给出 metric 定义 |
| No-Go 量化 | "误差范围内接近 1"——模糊 | 范本通常给出具体阈值（如 95% CI） |

**档位定位**：`scoring_rubric.expression.0.7-0.8`（"问题-指标-No-Go 三件套齐全但部分量化口径偏弱"）

### 锚点 3：创新点段（rationale.md §1.4 vs 范本 anchor "创新点四步闭环"）

**申请书原文（§1.4 创新点 2 第 59 行，177 字符）**：
> "**第二，在探针化层面**，本项目首次建立"量子光 HHG 作为多体态非经典探针"的理论框架（操作性定义见 §1.1），提出 QEF 双指标——$QEF_{\rm vis} = V_{\rm BSV}/V_{\rm classical}$（干涉可见度型）与 $QEF_{\rm yield} = Y_{\rm BSV-HHG}/Y_{\rm classical-HHG}$（同等平均强度下产出比）——为 BSV-HHG 在不同关联强度材料中的灵敏度提供量化标尺（参照 Boroumand et al. 2025 [arXiv:2505.22536] 的 QSHHG/QEF 框架与 Li et al. 2019 [arXiv:1908.07283] 的 HHG 反演方法学）。"

**范本锚点（面上项目-正文.md 创新点段）**：
> "本项目的创新点主要体现在三个方面：（1）现有方法的局限是 …；（2）本项目方案是 …；（3）本方案的量化优势是 …；（4）在科学/方法层面的定位是 …。"

**差距分析**：
| 维度 | 申请书 | 范本 |
|---|---|---|
| 四步闭环 | 现有局限（隐含）/ 方案（QEF 双指标）/ 量化优势（缺）/ 定位收束（缺） | 四步明确，每步量化 |
| 检索证据 | "首次"已加检索声明 ✅ | 通常也有 |
| 与现有工作的区分度 | "参照 Boroumand ... QSHHG"——但 QSHHG 缩写归属存疑 | 通常明确"区别于 X 工作" |

**档位定位**：`scoring_rubric.expression.0.7-0.8`（"创新点结构完整但量化收束略空"）

---

## 八、执行清单对照（references-only 可省略；本轮为 rationale 深审，仍执行）

| 检查项 | 状态 | 证据 |
|---|---|---|
| §1.1 是否以科学问题为主线展开，而非罗列文献 | ⚠️ 部分 | §1.1 段 1 第 5 行仍是三类体系并列+文献堆砌（477 字符单句），但 §1.1 段 2 后转入科学问题，结构逐步过渡 |
| §1.2 国内外研究现状是否陈述前人局限性而非"A 做了 X, B 做了 Y" | ⚠️ 部分 | §1.2.2 段 4-5 仍以"Even Tzur 2024 建立了 ..."起头，是轻度文献并列；§1.2.3 已明确空白识别 |
| §1.2.3 前人局限性是否清晰 | ✅ | "机制空白（Even Tzur 未推广到固体）+ 材料空白（无 BSV 在不同关联强度材料响应）+ 方法学空白（Q_F/QEF 跨体系协议未建立）"三件套齐全 |
| §1.3 核心科学问题是否凝练 1-2 个核心问题 | ⚠️ 4 个问题偏多 | 面上项目标准是 1-2 个核心问题 + 2-3 个支撑问题。本项目 4 个问题（Q1 谱差异 / Q2 探针价值 / Q3 信号提取 / Q4 参数依赖）结构合理但需明确主次关系——建议 §1.3 加"Q1+Q2 是核心，Q3+Q4 是支撑"层级说明 |
| §1.3 是否每条至少 1 个可检验量化指标 | ✅ | Q1 → QEF_yield；Q2 → QEF 单调性；Q3 → Q_F + QEF_vis；Q4 → mapping 拟合优度 |
| §1.3 No-Go 判据是否给出 | ✅ | 4 个问题均有降级判据 |
| §1.4 创新点是否四步闭环（现有局限→方案→量化优势→定位收束） | ⚠️ | 创新点 1 / 2 / 3 都有"现有局限→方案"两步，"量化优势"略空，"定位收束" 部分到位 |
| 立项依据是否五层递进（大背景→领域脉络→核心问题→国内现状→本项目定位） | ✅ | §1.1 段 1-4 = 大背景 + 触发问题；§1.2.1-1.2.3 = 国内外现状；§1.3 = 核心问题；§1.4 = 本项目定位 |
| 研究目标是否每条至少 1 个可检验量化指标 | ✅ | rationale §1.1 QEF≥1.5；§1.3 四个问题均有量化指标 |
| 杜绝"具有决定性意义""迈向新的高度"等空洞概括 | ✅ | 全章 0 次 |
| 杜绝"为…提供…基础/支撑/途径"模板 | ✅ | 全章 0 次 |
| 杜绝 80 字以上单句 | ❌ | 6 处 >200 字符单句，最长 477 字符（H-6.2） |
| 杜绝冗余修饰堆砌 | ⚠️ | 16 处"系统/关键/显著/精准/重要/成熟/完整"（M-6.7） |
| 杜绝死板关联词 | ✅ | "在此基础上""然而""此外" 0 次 |
| 杜绝模板主语"本项目拟/本项目将"高频 | ✅ | 3 + 2 = 5 次，未超 15 阈值 |
| 杜绝"首次""尚未见报道"等无证据强宣称 | ⚠️ | 4 处"首次"，3 处已加检索声明；§1.4 创新点 1 + 创新点 3 的"首次"未加检索声明（M-6.11 / M-6.12） |
| 杜绝内容越界（研究方案中出现"为什么研究/为什么可行"口吻） | ✅ | rationale.md 不涉及研究方案 |
| 杜绝跨章节大量重复 | ⚠️ | rationale ↔ content ↔ innovation 部分复述，但属 NSFC 章节间呼应，非违规 |
| 杜绝跨章节术语漂移 | ⚠️ | "QEF 双指标 / QEF 三维度 / 两个核心 + 一个辅助"三处不一（M-6.10）；"BSV 零/非零期望值" 与 §2.3 关系待澄清（L-6.28） |
| 模块完整性（立项依据 ≥200 字独立成节） | ✅ | 62 行，约 5,800 字符 |
| 引文格式一致性 | ❌ | rationale.md 与 references.md 引文制式不一致（references 用数字编号，rationale 用行内作者-期刊括号制，正文无 [N] 角标——round-5 H-5.5）；且 rationale 多处引文与 round-5 标记的 [critical]/[high] 引文错误同步（C-6.1 / H-6.3-H-6.6） |

**执行清单总计**：✅ 11 项 / ⚠️ 9 项 / ❌ 2 项 = 总计 22 项检查中，fail 项 2 项 + 部分 fail 9 项，未超过 3 项硬失败阈值，但 9 项部分 fail + 5 项 high 优先级问题将严谨性与表达质量限制在 0.65-0.70 区间。

---

## 九、对抗结论

### 本轮问题统计
- 本轮发现 29 个问题（critical: 1, high: 5, medium: 11, low: 12）
- 相比 round-1：改善 8 个（概念堆砌 / 平行列举 / 自相矛盾 / 缺乏 No-Go / "纠缠光子对"无关项 / Berry 曲率过度归因 / coherent control 术语漂移 / 国内空白声明）；新增 5 个（超长句反弹 / 冗余修饰密度 / 4 处引文与 round-5 同步未修复 / QSHHG 边界 / U/W 单点估计）；残留 0 个（本章为整改后段落级深审）
- 物理专项检查（8 项）中本轮重点命中：#1 BSV 增强 vs 反演精度（三层分立论证已写入）、#2 Berry 曲率可辨识性（hedging 已写入）、#4 Q1/Q2 真假科学问题（4 个问题均有 No-Go + 自洽性回归修正）、#6 预印本依赖度（rationale 引文多为已发表，仅 Even Tzur 仍为预印本错误状态）、#7 驱动波长-带隙匹配（MIR 2-4 μm 已加）

### 是否达到输出标准
**否**。理由：
- min_overall_score = 0.80，本轮综合 **0.71 < 0.80** ❌
- max_high_issues = 0，本轮 high 及以上共 **6 个（1 critical + 5 high）>> 0** ❌
- max_medium_issues = 3，本轮 medium **11 个 >> 3** ❌
- 三项阈值全部未达，**严拒输出**。

但相对 round-1 的 0.41，提升 +0.30（74%），相对 round-5 的 0.66（参考文献维度）+0.05（聚焦章节深化）。已具备冲刺 0.80 的基础。

### 返工优先级
- **P0（提交前必须，本轮新发现）**：
  - C-6.1 Even Tzur 2024 三重错误同步修复（连同 references #2 + 第 31/35/39/57 行同步）
  - H-6.2 §1.1 段 1 第 5 行 477 字符超长句拆分（最高优先级，因为是评审第一印象）
  - H-6.3 Iskhakov 引文标题与 references #4 同步修复
  - H-6.4 QSHHG 缩写出处核实（连同 references #15 + innovation.md + §2.8）
  - H-6.5 Li 2019 引文核实（连同 references #9 + scheme §3 第 27 行 PRL 129,173001 引用）
  - H-6.6 Wu 2024 引文标题与 references #14 同步
- **P1（定稿前整改）**：
  - M-6.7 冗余修饰词密度清理（16 处）
  - M-6.8 §1.2.2 段 1 AI 列举替换
  - M-6.9 §1.1 段 3 平行列举改递进
  - M-6.10 QEF 维度跨章口径统一（rationale + content + scheme 三处）
  - M-6.11 / M-6.12 §1.4 创新点 1 / 3 的"首次"补检索声明
- **P2（建议）**：M-6.13 至 M-6.17 + L-6.18 至 L-6.29 共 19 项

### 下一轮评审建议聚焦
- 本轮 rationale.md 修复后，建议下一轮聚焦 **content.md §2.4 探针有效性验证**（其中 QEF 三维度跨章口径需与本轮修复同步；No-Go 判据需与 §1.3 统一）。
- 同时建议对 references.md 启动第 2 轮深审（round-5 标记的 4 critical + 5 high 引文问题是否已修复）。
- 整体一致性轮次（round-4 复盘）应安排在 references 第 2 轮深审完成后。

---

## 评分

创新性：0.78
可行性：0.72
严谨性：0.62
表达质量：0.68
综合评分：0.71