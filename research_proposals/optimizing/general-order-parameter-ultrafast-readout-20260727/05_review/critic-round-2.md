# 对抗评审报告（第 2 轮）—— 立项依据（rationale.md）段落级深审

## 元信息

- 申请书：general-order-parameter-ultrafast-readout-20260727（面上 general）
- 评审轮次：第 2 轮
- 本轮聚焦：（一）立项依据（科学意义、前人研究局限性）段落级深审；其他章节做简要一致性核对
- 项目类型：general（面上），funding ≤60 万，4 年，正文 ≤30 页，三段式
- 评审日期：2026-08-18；profile：critic
- 事实核实方式：本轮聚焦章节 rationale.md 99 行全文已读取；content.md 63 行、scheme.md 114 行、references.md 163 行已对照读取；前一轮报告 critic-round-1.md（参考文献专项检验）已全文读取。外部书目核验（DOI/arXiv 在线解析）未执行；涉及处已注明 action=verify。
- 写作风格红线扫描：对 rationale.md 全文执行程序化 AI 检测（关联词密度、模板句式、冗余修饰、句长分布、段落密度、文献编号）；数据见下文「程序化检测」段落。

## 综合评分

**0.74 / 1.00**（按 nsfc-standards.json 的 general 项目 5 维加权：创新性 0.30 × 0.85 + 可行性 0.25 × 0.80 + 科学意义 0.20 × 0.85 + 研究基础 0.15 × 0.70 + 表达质量 0.10 × 0.62 = 0.782；本轮侧重立项依据，参考立项依据贡献下调可行性权重；综合取 0.74）

评分依据：立项依据的科学问题凝练（"唯一归因 / 可辨识性边界"）与三层判据体系（复现 / 信号探测 / 可辨识性）是真实加分项；五层递进（大背景→领域脉络→核心问题→国内现状→本项目定位）结构清晰且段落密度达标（4 节、共 99 行、平均每节 25 行）。但叙事仍有"作者-期刊-年份"的段落罗列、个别物理事实不严谨（H4 未修复）、H2 年份冲突在 scheme.md 仍存、R1 的核心锚点预印本年份矛盾在 content.md 仍存在、个别文献编号缺失（rationale L5 把"序参量"教科书论述挂 [25][26]）、超长句 8 句（>120 字）违反范本红线。把综合拉到 0.74 是综合上述有利项与硬伤的折中。

## 维度评分

| 维度 | 权重 | 得分 | 问题数 | 主要依据 |
|---|---|---|---|---|
| 创新性 | 0.30 | 0.85 | 1M | 把可辨识性问题（Fisher + Bayesian）从理论概念推到实验反演判据，定位锐利（rationale §4、§3 三层判据）；与同年 Cochran/Sørensen 工作的对接是真实加分 |
| 可行性 | 0.25 | 0.80 | 2M | 装置参数阈值、备选切换判据均形式化；CrSb/MnTe 双体系与 TiSe₂ 对照三层保障完整；但核心判据（≥1% 偶次谐波差分、SNR>5）的物理论证有跳跃 |
| 严谨性 | 0.20 | 0.78 | 3H, 4M | R1 的 P0 遗留（H1/H2/H4）部分未修复；多文档年份/编号冲突；"实验确认"用语有理论文献支撑风险；材料参数引用不足 |
| 研究基础 | 0.15 | 0.70 | 1H | 申请人前期工作零自引（R1 M5 未解决）；methodology manual 4 万字是潜在支撑但申请书未引用其作为前置基础 |
| 表达质量 | 0.10 | 0.62 | 1H, 1M | >120 字超长句 8 句（占 4.5%）超过范本红线；个别段落衔接词单一；"X 等人 Y 年 [N]"式罗列在 §2 出现密度较高；理性叙述密度与范本锚点对比有差距 |

加权综合 = 0.85×0.30 + 0.80×0.25 + 0.78×0.20 + 0.70×0.15 + 0.62×0.10 = **0.78**（理论）
考虑到立项依据侧重，且 R1 遗留的 P0/H 问题在 rationale.md 上仍有 3 处显性体现（rationale L37/L43/L89），综合评分下调至 **0.74**。

## 模块完整性检查（申请书骨架）

| 标准模块 | 应有文件 | 实际状态 | 评估 |
|---|---|---|---|
| 立项依据（§1） | rationale.md | ✓ 99 行 | 完整 |
| 研究内容（§2） | content.md | ✓ 63 行 | 完整 |
| 研究方案（§3） | scheme.md | ✓ 114 行 | 完整 |
| 参考文献 | references.md | ✓ 163 行（43 条） | 完整但 R1 已发现编号体系与年份问题 |
| 研究基础 | 全申请书合并本中应包含；本目录只见 sections/ 下 4 个文件，未见独立"研究基础"章节 | ⚠ | 三段式（立项依据+研究内容+研究基础）中"研究基础"模块缺失或未单独成文——这是 2026 三段式规定的硬性模块 |
| 方法学手册 | methodology-manual.md（95251 字节） | ✓ 存在 | 完整但 rationale 全文未引用方法学手册作为前置基础 |

**模块完整性结论**：立项依据 / 研究内容 / 研究方案 / 参考文献四大模块齐备，但 2026 新版三段式（立项依据 + 研究内容 + 研究基础）所要求的**研究基础模块在当前 sections/ 目录下未独立成文**——这是结构性缺口，需在最终合并稿中补齐，否则申请书正文体例不合规。

## 历史遗留问题追踪（R1 → R2）

下表逐条核对 R1（critic-round-1.md）遗留的 P0/P1 问题在本轮 rationale.md 聚焦章节的当前状态：

| R1 编号 | 问题 | R1 严重度 | 当前状态 |
|---|---|---|---|
| H1 | [62][63][69] 预印本年份与 arXiv 编号矛盾（content.md L37 写"2025 年"） | high | **未修复** —— content.md L37 仍写 "Cochran 等人 2025 年 [62]" "Sørensen 等人 2025 年 [63]"。rationale.md L43 采用说明性表述（"2025—2026 年间"）规避，未直接复述错误年份，但 content.md 错误传播未停止 |
| H2 | Werner [24] 年份三版本并存（content.md "2024 年 [24]"，scheme.md "2026 [24]"，references.md 2026） | high | **未修复** —— scheme.md L77 仍为 "(Werner et al., 2026 [24])"；content.md L23 仍为 "Werner 等人 2024 年 [24]"。rationale.md L37 称 "Werner 等人的理论预言 [24]" 未涉及年份（避免冲突），但跨文档仍未统一 |
| H3 | 编号体系不合正式申请书规范（非连续 + 字母后缀 + 撞号 [58] vs [58a]/[58b]） | high | **未在本轮聚焦范围内**（聚焦章节为 rationale），未核查 references.md；保留 R1 判断 |
| H4 | 理论文献 [25] Šmejkal 用于支撑"d 波实验确认"论断，ARPES 实验文献缺失 | high | **部分未修复** —— rationale.md L89 仍写 "CrSb 带隙约 0.13 eV（间接）与 0.6 eV（直接），中红外 3—5 μm 驱动光对应的光子能量 0.25—0.41 eV 落在带间共振附近"（物理计算未依赖实验文献），但 L23 的"d 波形动量依赖自旋分裂打破 Kramers 自旋简并 [24][25]"用 [24][25] 两条理论文献支撑对称性框架（可接受，框架引用）；L89 写 "CrSb 满足候选信号机制前提：d 波形交错磁分裂已获实验确认 [25]"——**[25] 仍为 Šmejkal PRX 12, 040006 (2022) 理论框架论文，H4 未实质修复** |
| H5 | 预印本占比 53.5%，核心证据链未经同行评审 | high | **未修复且超出本轮范围**（聚焦 rationale）；预印本全在 references.md |
| M1 | 文献表自述统计数多处错误 | medium | **未在本轮聚焦范围** |
| M4 | CrSb/MnTe 关键材料参数无文献支撑 | medium | **未实质修复** —— rationale L89 仍用"CrSb 带隙约 0.13 eV（间接）与 0.6 eV（直接）"无引用（与 R1 完全相同表述） |
| M5 | 申请人前期工作零自引 | medium | **未修复** —— rationale 未引用任何申请人前期工作；methodology-manual.md 4 万字中若有相关产出，未在申请书引用 |

**R1 遗留问题在 rationale 章节的处理**：
- 已改善：用 [25] 限定语精确化（如 rationale L23、L24、L89 三处均明确写"对称性框架"或"理论框架"语义）
- 未改善：H1/H2/H4 在 rationale.md 章节内仍有 3 处直接体现（rationale L37、L43、L89）
- 严禁重复机械扣分：本轮评分已避免因 R1 问题简单重复扣分，对每条 R1 遗留按当前文本实际重新判断

## 执行清单对照（v6.9+ 评审硬性清单逐条核验）

| # | 执行项 | 通过/不通过 | 证据 / 处理 |
|---|---|---|---|
| 1 | 模块完整性检查（含研究基础模块） | **部分不通过** | 三段式所要求的"研究基础"模块在 sections/ 目录未独立成文；需补齐 |
| 2 | 读取申请书与质量标准 | ✓ | rationale.md / content.md / scheme.md / references.md / nsfc-standards.json 全部读取 |
| 3 | 逐条对照上方执行清单 | ✓ | 见本表 |
| 4 | 申请书文字与 benchmark_anchors 结构化对比 | ✓ | 见「锚点对比」段落 |
| 5 | 引用程序化 AI 检测结果 | ✓ | 见「程序化检测」段落 |
| 6 | 按项目类型标准做红队评审 | ✓ | 见「问题清单」 |
| 7 | 检查叙述式写作风格 | ✓ | 见「写作风格评估」段落 |
| 8 | 每个问题给出可执行修改建议 + rubric 条款 | ✓ | 见「问题清单」每条末尾 |
| 9 | 按严重程度分级 | ✓ | critical/high/medium/low |
| 10 | 评审报告含执行清单 / 风格 / 锚点 / 评分块 | ✓ | 见全文 |
| 11 | 多维度评分 + 引用 scoring_rubric 档位依据 | ✓ | 见「评分」块 |
| 12 | 评分块格式正确 | ✓ | 见文末 |
| 13 | 锚点回归：每条意见标注 rubric 条款 | ✓ | 见「问题清单」每条末尾 |
| 14 | 历史遗留问题核对 | ✓ | 见「历史遗留问题追踪」表 |
| 15 | 严禁因历史重复扣分 | ✓ | R1 遗留问题在评分时已按当前文本实际重新评估 |

## 程序化检测（rationale.md 全文）

检测器输出：

- 总字符数 10290；总句数 179
- 死板关联词合计 1 次（"因此" ×1），**未超阈值**（阈值：在范本反例区间，但合计 ≤ 5 即合格）
- "为 X 提供 Y 类"模板句式 4 次（"为 Werner 等人的理论预言提供了实验验证""为 HHG 偶次谐波信号所需的对称破缺条件提供原子尺度实验证据""为偏振分辨 HHG 路径提供了独立的光学实验佐证""为磁性 HHG 提供了理论参考"）—— 阈值 15，**未超**
- 冗余修饰合计 5 次（系统 ×2、关键 ×2、有效 ×1）—— 阈值 15，**未超**
- 模板主语"本项目拟/将/旨在"：0 次，**范本级水平**
- "为回答 X 问题"口号式开头：0 次
- 80-120 字长句 23 句（12.8%）—— 范本区间 12%-28%，**达标**
- **>120 字超长句 8 句（4.5%）** —— 范本要求"单句 > 120 字必拆分"，**严重超阈值**
- 段内超长句 >2 句的段落：1 段（rationale L79 "判据阈值的物理依据以四项核心可证伪阈值为骨架..."），**超标**
- "本项目"出现 6 次（rationale L25、L27、L69、L73、L97、L99），频次合理
- 正文 [N] 编号引用 69 处、38 个不同编号 —— **远超范本 10-20 次基准**（范本范围 10-17 次，超出基准 2-4 倍，但申请书内容密度高，未达反例阈值）
- 涉及编号完整列表：`['1', '2', '3', '5', '7', '9', '10', '11', '12', '13', '15', '16', '20', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '35', '39', '55', '56', '57', '58a', '58b', '62', '63', '64', '65', '66', '67', '68', '69']`

**AI 写作味结论**：模板化句式密度低、关联词单一，主体叙述密度达标；但 >120 字超长句 8 句超出范本红线，是表达质量最大的硬约束。按 anti_ai_patterns 规则："超长句单句 > 120 字标记为 high issue"——本轮标记 1 条 high issue。

## 写作风格评估（叙述式合规性）

### 通过项

- **五层递进结构完整**：rationale §1（大背景：序参量是凝聚态物理核心信息）→ §2（领域脉络：CDW/磁性 HHG/超导 HHG/多体 HHG 四条路径演进）→ §3（核心问题：唯一归因与可辨识性边界）→ §4（国内现状：孟胜、李亮兰鹏飞陆培祥等课题组积累）→ §5（略融入 §2 末段与 §3 科学问题凝练）。总体符合 nsfc-standards `general_principles.writing_style_rules.must` 第 5 条。
- **科学问题为主线**：rationale §3 把科学问题凝练为"在限定的 altermagnet 材料和多带正演模型条件下，磁场反转与偏振分辨的固体 HHG 能否在排除替代解释后区分 altermagnet 序参量相关对称性破缺与能带背景的贡献"，并在 §4 给出三个实施保障（差分设计 / 正演模型 / 独立交叉验证）。问题表述含可证伪答案 + No-Go 边界（与 trap 3 对照）。
- **可证伪判据可量化**：rationale §3 末段给出 4 项可证伪阈值（TiSe₂ 复现判据 ≤10% / CrSb 信号判据 ≥1% + SNR>5 / Fisher 条件数 κ<10² / Bayesian 后验 <50%），与 content.md §2.1、scheme.md §1 形成跨章节闭环。rubric `scoring_rubric.rigor` 0.80-0.89 档。
- **空白边界明确化**：rationale §2 末段把"超导涨落、激子凝聚"明确划入"项目完成后的自然延伸"，不消耗四年期方法学预算；rationale §3 末段再次重申；content.md §2.1 第三次重申。该处理避免面铺得太宽，与 general 项目"小切口深挖掘"定位一致。

### 不通过项

- **§2.2 国内外研究现状存在"作者-期刊-年份"式密集堆砌**（rationale L33-L51），rubric `general_principles.writing_style_rules.forbidden` 第 1 条（"A 做了... B 做了... C 做了..."）。具体表现为：rationale L33 Tyulnev→L33 Zhang→L35 Ahmed→L37 Takayoshi→L37 Werner→L39 Leeb→L39 Šmejkal→L39 Ly→L39 Jita→L41 Fuchs→L41 Schüle→L43 Rost→L43 Sankar→L43 Ren→L45 McCarter→L45 Horstmann→L45 Qiu 共 16 条连续堆叠。**虽然每条后接论证语句**（与"纯罗列"略有区别），但密度仍偏高，rubric `scoring_rubric.expression` 0.70-0.79 档（"表达一般，有一定比例的模板套话或 AI 痕迹，部分段落逻辑松散"）。
- **超长句 8 句（>120 字）违反范本红线**，rubric `general_principles.anti_ai_patterns.remove` "超长句单句 >120 字必拆分"。最高风险段：rationale L79 一段 4 个超长句 + 1 段内 >2 句——是本轮最大的表达质量硬伤。
- **rationale L5 "凝聚态物理中的相变，对应一组特定对称操作的破缺..."挂 [25][26]**（R1 L4 / L177 标记为 citation-fit 弱）：教科书级一般论述挂专题论文作支撑，rubric `scoring_rubric.rigor` 0.70-0.79 档（"论证基本成立，但存在术语不一致、指标口径模糊、或个别逻辑跳跃"）。

### 写作风格档位定级

按 `scoring_rubric.expression` 档位：
- 0.80-0.89 档（"表达清晰，偶有模板化表达但不影响阅读，整体行文连贯"）：**未达**——超长句 8 句是阻断因素。
- **0.70-0.79 档**（"表达一般，有一定比例的模板套话或 AI 痕迹，部分段落逻辑松散"）：**部分命中**——模板化表达未超阈值但超长句 + 段落罗列密度偏高。
- 评分：**0.62**（在 0.60-0.69 档上沿 + 反例超长句扣减），rubric `scoring_rubric.expression` 0.60-0.69 档（"表达较差，大量模板套话或 bullet-list 式罗列，可读性低"）的反例。

## 锚点对比（申请书文字 vs benchmark_anchors）

### 锚点 1：rationale_anchor + rationale_example

范本锚点要求：
> "立项依据范本特征：以领域意义开篇，用'某人等人[N]在期刊上报道了X'式嵌入式引用，逐步收窄到核心挑战。每段150-300字，段间以内容逻辑衔接（非关联词）。末尾自然引出科学问题，不使用'为回答...问题'式口号。"

申请书 rationale 现状：

| 锚点要求 | rationale 实际表现 | 差距 |
|---|---|---|
| 以领域意义开篇 | ✓ rationale L5 凝聚态相变 + 序参量定义开篇 | 达标 |
| 嵌入式引用 '某人[N]在期刊上报道了X' | △ L33-L51 出现 "Tyulnev 等人在 TiSe₂ 中观测到 CDW 相..." "Werner 等人的理论预言了候选信号 [24]" "Rost 等人通过自旋分辨 HHG 观测到材料特异的交错磁指纹 [67]"—— 形式达标，但密度过高（16 条连续堆叠） | 部分达标 |
| 逐步收窄到核心挑战 | ✓ L7-L19 三类瓶颈 → L21 不可辨识性核心障碍 → L27 凝练科学问题 → L69 凝练 | 达标 |
| 每段 150-300 字 | △ rationale L79 一段超 600 字（L79-L79 含四项判据密集排布），L89 一段超 700 字（含 CrSb 选材四前提、MnTe 备选、T_N 带隙 SOC）—— 段长超标 | 不达标 |
| 段间以内容逻辑衔接（非关联词） | ✓ rationale §1→§2→§3→§4 各节有明确"路径-方法学-局限-切入"的递进衔接 | 达标 |
| 末尾自然引出科学问题 | ✓ rationale §3 末段 "由此凝练的科学问题是..."（非"为回答...问题"口号式） | 达标 |

**差距诊断**：段长超标（rationale §3 §4 各有 600+ 字密集段）与嵌入式引用密度偏高是主要差距。范本 anchor_example 是 158 字短段落 + 单条嵌入式引用；rationale §2 单段塞入 16 条文献。

### 锚点 2：rationale_example 文字对比

范本锚段：
> "高次谐波产生是飞秒激光与物质相互作用的高阶非线性、非微扰现象。基于高次谐波光谱的超快探测技术使得在飞秒甚至阿秒尺度上实时探测物质中电子及原子核的微观动力学过程成为可能。**人们利用原子、分子气体高次谐波进行了大量气相原子分子的超快探测和控制研究[1-8]**，包括原子价电子运动的阿秒操控、分子核运动的实时观测等。近年来，人们在固体材料中也普遍观测到了高次谐波产生现象。2011年，**Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生**。"

申请书对应段落（rationale L17-L19）：
> "固体高次谐波产生（HHG）同时具备三个属性：发射过程本身发生在驱动光场的一个光学周期之内；对晶体空间对称性与磁对称性高度敏感；具备体相穿透能力。偏振分辨的固体 HHG 已在 CDW 体系中观测到相变前后的各向异性变化 [11]。Zhang 等人以半导体布洛赫方程与现象学平均场模型的结合，精确复现了 3/5/7 阶谐波的强偏振不对称性 [12]。"

差距：
- 范本锚段：嵌入式引用 + 解释性短句（"人们利用...进行了大量...研究[1-8]"），每条引用紧跟简短描述
- 申请书段：嵌入式引用密度更集中但论证性句子更紧（"同时具备三个属性""对...敏感""具备...能力"），更接近范本风格但密度更高
- **差距评级**：中等。申请书理由事密度高于范本，但叙事主线（三个属性→已有证据→方法学价值）符合范本节奏

### 锚点 3：innovation_anchor（用于衔接创新性评估）

范本锚点要求：
> "特色创新范本特征：并列2-3点，每点约200字，遵循四步闭环：现有局限→本项目方案→量化优势/核心机理→创新定位收束。"

申请书 rationale §4 末段（rationale L97-L99）：
> "这一框架的设计哲学是把方法学可靠性置于覆盖面之上。面上项目的四年执行期只够支撑一个主攻方向——多类型序参量的同步覆盖会让方法学可靠性稀释在多个尚未独立验证的体系上。这里因此将 altermagnet HHG 的可辨识性作为唯一核心目标...项目聚焦于一个具体的、可证伪的科学命题...这一命题的验证无论结果正负都具有科学价值。"

差距：
- 范本锚段：四步闭环结构明确（现有局限 → 本项目方案 → 量化优势 → 创新定位）
- 申请书段：rationale §4 主要讲框架设计哲学（"为什么这样做"），未严格遵循四步闭环——**创新定位收束在 §4 末段有所体现，但"现有局限"已在 §2-3 阐述，此处不重复**
- **差距评级**：弱。rationale 是立项依据不是"特色创新"章节，四步闭环的"现有局限→本项目方案"两步已在 §2-3 完成，"量化优势→创新定位"两步在 §4 收束。整体架构合理但量化优势缺乏具体数字（如"反演精度比现有提升 X 倍"）

### 锚点 4：scheme_anchor（用于跨章节一致性核对）

范本锚点要求：
> "研究方案范本特征：总体方案+技术路线图→分方案（方法-装置-应用，子节以物理产出衔接）。可行性分析遵循'方案→原理→结论'链式论证，不复述方案细节。每个技术选择都有'为什么选这个方法'的论证。"

申请书 scheme.md 现状：
- ✓ 总方案（scheme §1）→ 理论方法（§2）→ 实验方案（§3）→ 可行性（§4）→ 难点（§5）→ 创新（§6）→ 预期成果（§7）
- ✓ 可行性（scheme §4）"方案→原理→结论"链式论证
- ✓ 装置/光源选择均含"为什么选这个方法"（scheme L47 中红外 vs 近红外物理理由；L49 0.3-0.8 V/Å 物理依据）
- ⚠ scheme §4 可行性 §3 实验方案有约 20% 内容重叠（场强窗口、SOC 强度先验、CrSb 带隙数据在 §3 与 §4 重复出现），属于轻微边界越界（content_boundaries：可行性不复述研究方案技术细节）

**跨章节一致性整体结论**：rationale → content → scheme 三章的判据体系一致（rationale L79 / content L5 / scheme L9-15 判据数值完全对齐）；CrSb 选材四前提在 rationale L89 与 scheme L53 重叠但表述角度不同（rationale 论证选材逻辑，scheme 论证装置匹配），不构成"内容越界"。

## 分段级深审（rationale.md 各节）

### §1. 研究意义（L1-L27，4 段）

**作者声称**：
- 序参量是凝聚态物理核心信息（L5-L7）
- 三类瓶颈：表面敏感性、时间窗口错配、多通道耦合（L9-L13）
- HHG 同时具备三属性填补空白（L15-L17）
- 不可辨识性是核心障碍（L19-L21）
- altermagnet 是直面障碍的主攻体系（L23-L25）
- 凝练科学问题（L27）

**红队质询**：
1. **L5 "凝聚态物理中的相变，对应一组特定对称操作的破缺..."挂 [25][26]**：R1 L177 已标弱引用（citation-fit low）；本轮再次确认——这是教科书级一般论述（Landau 序参量定义），挂两条 altermagnet 专题论文作支撑属弱论证。建议改为综述 [39] 或删去编号。
2. **L21 不可辨识性核心障碍**：以"同一组 2/3 阶谐波强度比的变化，可能来自 altermagnet 序参量引起的 C₄ 旋转对称性破缺，也可能来自能带色散在 Γ 点附近的各向异性修正"为具体例。这是申请书**写得最锐利的物理论证**——具体、可证伪、与 Sørensen 解析结果直接呼应。**正面加分项**。
3. **L23 altermagnet 选择论证**：四条理由（零净磁矩、自旋分裂、d/g 波对称性、C₄→C₂）——但 "Altermagnet 中的磁场—序参量耦合并非简单的'翻转'关系，其自旋 flop 场强和取向依赖仍属活跃的研究课题 [58a]" 是诚实承认局限，但该段过渡到 L25 "但零净磁矩带来的背景压制效应本身是确实的"——"确实的"措辞稍带绝对化，建议改为"独立的、可定量化的"，与 §2 末段"被天然压制"语气更平衡。
4. **L27 科学问题表述**：含可证伪答案（"若可 / 若不可"）+ No-Go 边界 + 方法学起点——符合 rubric `scoring_rubric.innovation` 0.80-0.89 档（"选题有明确创新点，在已有方向上提出新视角/新方法/新机制，与前人有清晰区隔"）。

**修复确认**：
- ✅ R1 L177 弱引用问题仍存，理由书未做改动
- ✅ L21 是真实加分项

**本轮新增问题**：
- [medium] **L23-L25 "确实的"绝对化措辞**：rubric `scoring_rubric.rigor` 0.80-0.89 档（"论证较严密，偶有表述不够精确之处，但不影响核心结论"）边缘

### §2. 国内外研究现状及发展动态（L29-L65，5 段）

**作者声称**：
- 两条方法学路径（L31）
- CDW HHG：Tyulnev、Zhang、Ahmed（L33-L35）
- 磁性 HHG 理论：Takayoshi、Werner、Leeb、Šmejkal、Ly、Jita（L37-L39）
- altermagnet HHG 实验验证 2025-2026：Fuchs、Schüle、Rost、Sankar、Ren、McCarter、Horstmann、Qiu（L41-L45）
- 可辨识性正反两面：Cochran、Sørensen（L49）
- 其他体系：Ryan（kagome）、Garcia-Gaitan（NiO）、Gabriele（自旋纹理）（L51）
- 超导 HHG：Puviani、Alcalá、Matsunaga、Kawakami（L53）
- 激子 HHG：Jensen（L55）
- 多体 HHG 警示：Murakami、Dziurawiec、Granados（L57-L59）
- 国内现状：孟胜、李亮/兰鹏飞/陆培祥、Hansen/Madsen（L61）
- 文献局限 1+2（L63-L65）

**红队质询**：
1. **L33-L45 文献堆砌密度过高**：16 条文献集中在 L33-L45（约 13 行 1300 字），平均每行约一条文献——rubric `general_principles.writing_style_rules.forbidden` 第 1 条（"A 做了... B 做了... C 做了..."）虽非纯罗列（每条后接论证），但密度偏高。范本锚段（如 Ghimire 2011 [9]）是 1 段 1 文献式节奏，本申请书是 13 行 16 文献。
2. **L37 "Werner 等人的理论预言了候选信号 [24]" 与 L43 "Rost 等人...为 Werner 等人的理论预言提供了实验验证 [67]"**：L37 → L43 间隔合理（先理论后实验），但中间夹带 5 条不相关文献（Leeb/Šmejkal/Ly/Jita/Fuchs 等）。建议把"Werner→Rost"作为单线收窄，其他 altermagnet 理论文献（Leeb、Šmejkal、Ly、Jita）集中在一段对比式描述，**减少穿插**。
3. **L43 "Sankar 等人在室温 CrSb 中观测到宽带三阶非线性反常霍尔效应 [56]"**：三阶非线性反常霍尔 ≠ HHG——该工作是否构成 CrSb 非线性响应可行的支撑需谨慎措辞。Sankar 2025 [56] 是三阶霍尔效应，HHG 是高阶非线性（≥ 5 阶通常）；两个非线性阶次不同。申请书用其"间接支持非线性光学响应足够强"是合理的，但应明确"间接"语义。
4. **L53-L55 超导 HHG 与激子 HHG 边界声明**：rationale L53 写"超导体系面临的替代解释（Higgs 模式 vs. 准粒子非线性 vs. 相位模）与 altermagnet 体系不同"——这是边界声明而非论证，rubric `content_boundaries.不可越界` 适用。
5. **L59 Granados 等人警示后的设计原则**："载波包络相位与轨道角动量不纳入核心约束，仅在必要时作为辅助验证"——**这是一个真实加分项**（设计哲学前置声明，避免后续 reviewer 质问"为什么不纳入 CEP"）。**正面加分项**。
6. **L61 "国内尚未见针对 altermagnet 材料 HHG 序参量反演的实验报道"**：检索范围"altermagnet 材料 HHG 序参量反演"被精确限定——避免"国际空白"过度声明（trap 5）。**正面加分项**。
7. **L63-L65 文献局限 1+2**：rationale 把文献局限拆为"信号展示 vs 唯一归因"+"单一谐波指纹 vs 多维约束"两个递进，是真实加分项（与 §3 末段四个阈值衔接）。

**修复确认**：
- ✅ R1 M4 CrSb 材料参数无引用问题在 rationale L89 仍存（带隙、SOC、T_N 三项无引），本轮再次标记
- ✅ R1 H4 "实验确认"用语在 rationale L23/L89 仍存，本轮再次标记

**本轮新增问题**：
- [high] **L33-L45 嵌入式引用密度偏高**：rubric `general_principles.writing_style_rules.must` 第 3 条（"禁止简单罗列文献、数据、概念、技术参数；每一处引用都应为论证服务"）——虽非纯罗列但密度触发反例
- [medium] **L43 "宽带三阶非线性反常霍尔"作为 CrSb 非线性可行性的支撑**：rubric `scoring_rubric.rigor` 0.70-0.79 档（"论证基本成立，但存在术语不一致、指标口径模糊、或个别逻辑跳跃"）——三阶霍尔 ≠ HHG 应明确

### §3. 关键科学问题（L67-L81，4 段）

**作者声称**：
- 核心科学问题凝练（L69）
- 两个递进子问题：信号探测（L71）+ 排除替代解释（L73）
- 三个层次：方法学对照（TiSe₂）+ 差分实验（CrSb）+ 可辨识性分析（Fisher + Bayesian）（L75-L77）
- 四项可证伪阈值：TiSe₂ 复现、CrSb 信号、可辨识性、后验约束（L79）

**红队质询**：
1. **L69 "在限定的 altermagnet 材料和多带正演模型条件下..."**：限定语 "限定的材料" "限定的模型" 是**真实加分项**——避免无限外推到所有磁性体系，与 4 年面上项目规模匹配。**正面加分项**。
2. **L71 "Fuchs 等人在 MnTe 中 [64] 与 Rost 等人在 CrSb 中 [67] 已报道自旋极化 HHG 的观测。这里将探测变量扩展至磁场反转方向上的差分响应"**：从已有报道扩展到磁场反转差分的设计哲学明确——rubric `scoring_rubric.innovation` 0.80-0.89 档。
3. **L73 "如何区分上述信号中真正由 altermagnet 序参量相关对称性贡献的部分与能带背景的贡献？这里需要澄清'辨识'的操作定义"**：操作定义明确化是方法学进步，避免被 reviewer 质问"辨识的精确含义是什么"。**正面加分项**。
4. **L75-L77 三个层次的递进**：方法学对照（TiSe₂）→ 差分实验（CrSb）→ 可辨识性分析——结构清晰。但 L75 的"CrSb 的 Néel 温度约 720 K 远高于可达温区 4—300 K，温度跨相变差分不适用"——温度跨相变差分的不适用**是一个边界声明**，但 L77 末句"当两组不同的参数组合在现有测量精度下产生不可区分的 HHG 谱时，只报告参数的联合后验分布而不输出唯一的序参量归属"——这是 Sørensen 的非唯一性结论的应用，**方法学上正确**。
5. **L79 四项阈值**：是申请书判据体系的"母版"，与 scheme §1、content §2.1 完全对齐（已验证）。
6. **L79 一段 600+ 字 + 4 个 >120 字超长句**：rubric `general_principles.anti_ai_patterns.remove` "超长句单句 >120 字必拆分"——本段 4 项判据密度过高，建议拆为 4 段每项一段。

**修复确认**：
- ✅ R1 H2/H4 仍存（rationale L37、L43、L89）——本段未涉及年份或"实验确认"用语

**本轮新增问题**：
- [high] **L79 一段 4 个超长句 + 段长 >600 字违反范本红线**：rubric `general_principles.anti_ai_patterns.remove` "超长句单句 >120 字必拆分"
- [medium] **L77 末句 "三个层次构成'如何回答排除替代解释'的分析框架"**——"如何回答"模板化句式，rubric `general_principles.anti_ai_patterns.remove` "动词堆砌"的边缘

### §4. 总体研究框架（L83-L99，4 段）

**作者声称**：
- 一个主体系 + 一个对照体系 + 一条可辨识性判据（L85）
- 主体系 CrSb 的四点选材论证（L87-L89）
- 对照体系 TiSe₂ 的双重证据链（L91）
- 三个实施保障：差分设计 / 正演模型 / 独立交叉验证（L93）
- 设计哲学：方法学可靠性 > 覆盖面（L97）
- 项目定位：可证伪科学命题 + 正负结果同等价值（L99）

**红队质询**：
1. **L85-L99 整体结构**："技术路线围绕'一个主体系、一个对照体系、一条可辨识性判据'展开"——三段式主轴明确，与 content §2.1、scheme §1 完全对齐。**正面加分项**。
2. **L87-L89 CrSb 四点选材论证**：
   - L87 "Rost 等人已观测到自旋极化 HHG 的材料特异指纹 [67]"——已有实验支撑 ✓
   - L87 "Néel 温度约 720 K 远高于室温，磁序在常规实验温度（4—300 K）下稳定存在"——**无引用**（R1 M4 标记问题，本轮再次确认）——rationale 把这作为选材前提之一的应补引 CrSb 磁性测量文献（Reif 1958 类或现代 CrSb 单晶磁化率测量）
   - L89 "CrSb 带隙约 0.13 eV（间接）与 0.6 eV（直接）"——**无引用**（R1 M4）——需补引（CrSb ARPES 或光学吸收谱文献）
   - L89 "中红外 3—5 μm 驱动光对应的光子能量 0.25—0.41 eV 落在带间共振附近"——计算正确（1.24/3=0.413, 1.24/5=0.248），但带隙 0.13 eV（间接）+ 0.6 eV（直接）vs 0.25-0.41 eV 共振描述：0.41 eV 与直接带隙 0.6 eV 之间仍有 0.2 eV 差距，严格说并非"共振"，而是"带间跃迁可达"——措辞"落在带间共振附近"过强，建议改为"落在带间跃迁可达区间"
   - L89 "d 波形交错磁分裂已获实验确认 [25]"——**[25] Šmejkal PRX 12, 040006 (2022) 是理论框架论文**，R1 H4 仍存，本轮再次标记。需补引 CrSb 自旋分裂 ARPES 实验文献（CrSb 单晶 ARPES 测量类工作）
3. **L91 对照体系 TiSe₂ "Tyulnev [11] 与 Zhang [12] 已在 TiSe₂ 上建立了从实验到理论的双重证据链"**：Tyulnev 实验 + Zhang 理论 = 双源证据，与内容 scheme 一致 ✓
4. **L93 三个实施保障**：
   - 第一重差分设计："磁场正反转、偏振配置切换与温度监测三者的乘积控制"——具体但"乘积控制"措辞稍带歧义（数学乘积 or 操作叠加？），建议改为"三因素的联合扫描"
   - 第二重正演模型 + 可辨识性分析："多带半导体布洛赫方程或含时密度泛函模型生成合成 HHG 谱；费舍尔信息矩阵评估参数空间的条件数（κ < 10² 可辨识、10²—10⁴ 边缘、> 10⁴ 触发 No-Go）；贝叶斯反演给出参数后验分布而非点估计"——判据数值与 §3、content §2.4、scheme §1 一致 ✓
   - 第三重独立交叉验证："与 X 射线衍射或磁输运测量的独立结果对照，确认 HHG 反演提取的磁序信息与已知方法一致"——可行性完整 ✓
5. **L97 设计哲学："方法学可靠性置于覆盖面之上"**——4 年面上项目的合理选择，与 general 项目定位一致 ✓
6. **L99 "项目聚焦于一个具体的、可证伪的科学命题...这一命题的验证无论结果正负都具有科学价值"**——可证伪 + 正负同等价值是申请书**最重要的方法学声明**，rubric `scoring_rubric.innovation` 0.80-0.89 档上沿。**正面加分项**。

**修复确认**：
- ⚠ R1 H4 "d 波形已获实验确认 [25]" 仍存（rationale L89）
- ⚠ R1 M4 CrSb 材料参数无引用仍存（rationale L89）

**本轮新增问题**：
- [high] **L89 "d 波形交错磁分裂已获实验确认 [25]"**——理论文献支撑实验确认，rubric `indicator_red_lines.novelty_claim_cautious`（"尚未见报道""实验确认"等优先权表述须有确凿文献或检索范围支撑"）
- [high] **L89 "落在带间共振附近"措辞过强**——rubric `indicator_red_lines.no_exaggeration`（"器件/装置指标须与真实技术水平一致，不得无依据地拔高"）
- [medium] **L87-L89 CrSb T_N / 带隙 / SOC 三项无文献支撑**——rubric `indicator_red_lines.evidence_fit`（"理论文献被用于支撑'实验确认'论断"），与 R1 M4 同问题未修复

## 跨章节一致性审查

| 跨章节对 | 一致性 | 证据 |
|---|---|---|
| rationale L75 复现判据 ↔ content §2.1 | ✓ | 两者均为 "方向一致、幅度偏差 ≤ 10%（±8% 实验不确定度 + 2% 工程余量）" |
| rationale L79 信号判据 ↔ content §2.1 ↔ scheme §1 | ✓ | 三处均为 "差分相对强度 ≥ 1%、SNR > 5" |
| rationale L79 条件数判据 ↔ content §2.4 ↔ scheme §1 | ✓ | 三处均为 "κ < 10² 可辨识 / 10²—10⁴ 边缘 / > 10⁴ No-Go" |
| rationale L79 后验约束判据 ↔ content §2.4 ↔ scheme §1 | ✓ | 三处均为 "后验标准差 < 先验宽度 50%" |
| rationale L89 CrSb 选材 ↔ content §2.3 ↔ scheme L53 | ⚠ | rationale L89 "CrSb 带隙 0.13/0.6 eV" content §2.3 未明说带隙 scheme L27/L47/L53 数值一致；但 rationale L89 "d 波形已获实验确认 [25]" 与 scheme L53 错误相同 |
| rationale L25 altermagnet 论证 ↔ content §2.5 ↔ scheme L95 | ✓ | 三处均称"磁场反转差分压制能带背景" |
| rationale L49 Cochran [62] / Sørensen [63] ↔ content §2.4 ↔ scheme L41 | ✗ | rationale L49 用说明性表述（"2025—2026 年间"），content §2.4 写 "Cochran 等人 2025 年 [62]" "Sørensen 等人 2025 年 [63]"（R1 H1 仍存） |
| rationale L37 Werner [24] ↔ content §2.3 ↔ scheme §2 | ✗ | rationale L37 未涉及年份（避免冲突），content §2.3 写 "Werner 等人 2024 年 [24]"，scheme L77 写 "(Werner et al., 2026 [24])"（R1 H2 仍存） |
| rationale L93 三层保障 ↔ scheme §1 总方案 ↔ scheme §5 难点 | ✓ | 三处保障措辞一致 |
| rationale L99 可证伪科学命题 ↔ content §2.1 ↔ scheme §7 | ✓ | 三处一致 |

**跨章节一致性结论**：判据数值（4 项）在 rationale / content / scheme 三章完全一致；CrSb 选材数据在 rationale 与 scheme 一致但 content §2.3 未明确；R1 H1（[62][63] 年份）、H2（Werner 年份）、H4（d 波实验确认）三处遗留问题在 rationale 章节内仍存在 3 处显性体现。

## 术语一致性矩阵

| 术语 | 定义位置 | 使用章节 | 是否一致 |
|---|---|---|---|
| altermagnet | rationale L23 | rationale / content / scheme | ✓ |
| HHG | rationale L17 | rationale / content / scheme | ✓ |
| 序参量 | rationale L5 | rationale / content / scheme | ✓ |
| 可辨识性 / identifiability | rationale L19 | rationale / content / scheme | ✓ |
| 条件数 κ | rationale L79 | rationale / content / scheme | ✓ |
| 差分信号 | rationale L71 | rationale / content / scheme | ✓ |
| Bayesian / 贝叶斯反演 | rationale L79 | rationale / content / scheme | ✓ |
| 主体系 / 对照体系 / 备选主体系 | rationale L85 | rationale / content / scheme | ✓ |
| SBE | content §2.4 | content / scheme | ✓（rationale 仅在 §4 末段提及） |
| TDDFT | content §2.4 | content / scheme | ✓ |
| Fisher / 费舍尔信息矩阵 | rationale L79 | rationale / content / scheme | ✓ |
| Néel 温度 / T_N | rationale L71 | rationale / content / scheme | ✓ |

**术语一致性结论**：术语在 rationale / content / scheme 三章完全一致，无漂移。

## 事实核查表（关键数字与文献）

| 数字 / 论断 | 位置 | 核实结果 |
|---|---|---|
| TiSe₂ CDW 相变温度 205 K | rationale L75 | ✓ 范本 Tyulnev 报道 |
| 3/5/7 阶谐波偏振不对称 | rationale L75 | ✓ Zhang 2025 [12] |
| CrSb Néel 温度约 720 K | rationale L71 / L87 / L89 | ⚠ 全篇无引用（R1 M4）——Reif 1958 经典工作或现代 CrSb 单晶磁性测量文献应有引用 |
| CrSb 带隙 0.13 eV（间接）/ 0.6 eV（直接） | rationale L89 | ⚠ 全篇无引用（R1 M4）——CrSb ARPES / 光学吸收谱应有引用 |
| 中红外 3-5 μm 对应 0.25-0.41 eV | rationale L89 | ✓ 计算正确（1.24/3=0.413 eV, 1.24/5=0.248 eV） |
| Sb SOC 100-200 meV | rationale L37 | ⚠ 全篇无引用（R1 M4）——CrSb 第一性原理计算或原子参数表应有引用 |
| MnTe Néel 温度约 310 K | rationale L89 / L75 | ✓ Schüle [69] 引用 |
| Tyulnev ±8% 实验不确定度 | rationale L75 | ✓ Tyulnev 2025 [11] |
| 差分相对强度阈值 1% | rationale L79 | ✓ 自定义阈值，需在方法学手册给出物理依据（R2 §2.2 装置背景漂移实测） |
| SNR > 5 | rationale L79 | ✓ 自定义阈值 |
| κ < 10² / 10²-10⁴ / > 10⁴ | rationale L79 | ✓ 数值合理，但 FIM 条件数阈值在不同文献有 10³、10⁶ 等不同口径——rationale 选 10² 较激进，应论证依据 |
| 后验标准差 < 先验宽度 50% | rationale L79 | ✓ 自定义判据 |

**事实核查结论**：核心数字（相变温度、带隙、SOC、T_N、谐波阶次）有引用，但 CrSb 三项无引用（R1 M4 仍未修复）；中红外-带隙共振措辞过强；FIM 条件数阈值 10² 较激进需论证。

## 内容冗余与矛盾

| 冗余 / 矛盾 | 位置 | 严重度 | 处理 |
|---|---|---|---|
| rationale L37 / content §2.3 / scheme §2 三处都引 Werner [24]，且 rationale L37 与 content §2.3 / scheme L77 年份描述不一 | rationale L37, content L23, scheme L77 | high | R1 H2 仍存；需在 rationale / content / scheme 三处统一为 "Werner 等人 [24]（PRB 114, 035107, 2026；预印本 2024）" |
| rationale L49 / content §2.4 / scheme L41 三处都引 Cochran [62] / Sørensen [63]，且 content §2.4 写"2025 年"，scheme §2 引用风格与 rationale 不同 | rationale L49, content L37, scheme L41 | high | R1 H1 仍存；需在 rationale / content / scheme 三处统一年份 |
| rationale L89 / scheme L53 "d 波形已获实验确认 [25]" 同错误 | rationale L89, scheme L53 | high | R1 H4 仍存；需补引 CrSb ARPES 实测自旋分裂文献，或降格为"对称性框架由 [25] 给出" |
| rationale §4 与 content §2.5 / scheme §6 "创新点"在 rationale 中已部分铺垫 | rationale L97-L99, content §2.5, scheme §6 | low | 合理前置（立项依据自然引出创新点），非越界 |
| rationale §3 与 scheme §1 判据数值重复 | rationale L79, scheme L9-15 | low | 合理（立项依据给出判据体系，研究方案展开实施），非越界 |

## 问题清单

按 P1（必改）/P2（强烈建议）/P3（建议）分级。每条标注 violating rubric 条款或标准条款。

### P1（必改）

#### [high] anti_ai — L79 一段 4 个超长句 + 段长 >600 字违反范本红线
- 位置：rationale.md L79 "判据阈值的物理依据以四项核心可证伪阈值为骨架..."
- 问题：本段包含 4 项判据（TiSe₂ 复现判据 / CrSb 信号判据 / 可辨识性判据 / 后验约束判据），每项为一个 >120 字超长句，共 4 个超长句集中在同一段。程序化检测显示该段同时是"段内 >2 句超长"的唯二段落之一（另一段是 L79-L79 整体）。
- 违反：rubric `general_principles.anti_ai_patterns.remove` "超长句单句 >120 字必拆分"；rubric `general_principles.writing_style_rules.must` 第 4 条"段落之间形成逻辑递进"
- 建议：把 L79 拆为 4 段，每项判据一段（约 150-200 字），段间以"第二，""第三，""第四，"等序列词衔接但避免"在此基础上"等死板关联词。每段第 1 句建议简化为：判据一：TiSe₂ 复现判据为...；判据二：CrSb 信号判据为...；判据三：可辨识性判据为...；判据四：后验约束判据为...
- 示例改写（判据一段示例）：判据阈值的物理依据以四项核心可证伪阈值为骨架。第一，TiSe₂ 复现判据要求 CDW 相变温度 205 K 上下的 3/5/7 阶谐波偏振不对称方向与 Tyulnev [11] 报道一致，幅度偏差 ≤ 10%。10% 的物理依据是 Tyulnev 报道的 ±8% 实验不确定度加 2% 工程余量。该判据确认自建装置的偏振分辨精度与多带 SBE 模型的预测精度满足后续实验需求。
- action：rewrite

#### [high] red_line — L89 "d 波形交错磁分裂已获实验确认 [25]"理论文献支撑实验确认
- 位置：rationale.md L89 "CrSb 满足候选信号机制前提：d 波形交错磁分裂已获实验确认 [25]"
- 问题：[25] Šmejkal PRX 12, 040006 (2022) 是 altermagnet 解除 Kramers 简并的理论框架论文，不构成 CrSb d 波分裂的实验确认。d 波分裂的实验证据（CrSb 自旋劈裂 ARPES 测量类工作）未列入文献表——R1 H4 仍未实质修复。
- 违反：rubric `indicator_red_lines.novelty_claim_cautious`（"尚未见报道""实验确认"等优先权表述须有确凿文献支撑"）；rubric `indicator_red_lines.evidence_fit`（"理论文献被用于支撑'实验确认'论断"）
- 建议：方案一（推荐）：补引 CrSb 自旋分裂 ARPES 实验文献至少 1 条（如 CrSb 单晶自旋分辨 ARPES 实测劈裂幅度文献），把句改为"CrSb 满足候选信号机制前提：d 波形交错磁分裂已有自旋分辨 ARPES 实验测量 [新引文献]，其对称性分类由 [25] 锚定"。方案二（最小改动）：把句改为"d 波形对称性分类由 [25] 锚定"，删除"实验确认"措辞。
- action：research + rewrite

#### [high] red_line — L89 "落在带间共振附近"措辞过强
- 位置：rationale.md L89 "中红外 3—5 μm 驱动光对应的光子能量 0.25—0.41 eV 落在带间共振附近"
- 问题：CrSb 带隙 0.13 eV（间接）+ 0.6 eV（直接），光子能量 0.25-0.41 eV ——0.41 eV 与直接带隙 0.6 eV 之间仍有 0.2 eV 差距，严格说并非"共振"（光子能量 ≈ 带隙）而是"带间跃迁可达"（光子能量 > 间接带隙且与直接带隙在同一量级）。措辞"共振"对物理学家 reader 会引发质疑。
- 违反：rubric `indicator_red_lines.no_exaggeration`（"器件/装置指标须与真实技术水平一致，不得无依据地拔高"）
- 建议：把句改为"中红外 3—5 μm 驱动光对应的光子能量 0.25—0.41 eV 高于 CrSb 间接带隙 0.13 eV，且与直接带隙 0.6 eV 处于同一量级，可有效激发带间跃迁"
- action：rewrite

#### [high] citation-consistency — 跨文档年份冲突 H1 / H2 在 rationale 章节内仍存
- 位置：rationale.md L37 [24]、L43 [62][63]、L49 Cochran/Sørensen、content.md L23 / L37、scheme.md L77 / L41 / L53
- 问题：rationale L37 "Werner 等人的理论预言了候选信号 [24]" 未涉及年份（避免冲突），但 content.md L23 "Werner 等人 2024 年 [24]" 与 scheme.md L77 "(Werner et al., 2026 [24])" 不一致；rationale L43 / L49 未涉及年份，但 content.md L37 写 "Cochran 等人 2025 年 [62]""Sørensen 等人 2025 年 [63]"——R1 H1/H2 仍存
- 违反：rubric `general_principles.indicator_red_lines.consistency_check`（"同一指标在不同章节出现时，数值与表述口径必须一致"）
- 建议：(a) Werner [24] 三处统一为 "Werner 等人 [24]（PRB 114, 035107, 2026；预印本 2024 年 arXiv:2407.07752）"——若预印本确实 2024 而正式发表 2026，则以正式发表为准并在脚注说明。(b) Cochran [62] / Sørensen [63] 三处先 verify arXiv 编号与年份（26xx = 2026, 25xx = 2025），统一为正确年份。
- action：verify + rewrite

### P2（强烈建议）

#### [high] narrative — L33-L45 嵌入式引用密度偏高（13 行 16 文献）
- 位置：rationale.md L33-L45
- 问题：Tyulnev、Zhang、Ahmed、Takayoshi、Werner、Leeb、Šmejkal、Ly、Jita、Fuchs、Schüle、Rost、Sankar、Ren、McCarter、Horstmann、Qiu 共 16 条文献集中在 13 行约 1300 字，平均每行约 1 条文献。范本 anchor_example 是 1 段 1-2 文献的节奏，密度显著偏高。
- 违反：rubric `general_principles.writing_style_rules.forbidden` 第 1 条（"文献堆砌式写作：A 做了... B 做了... C 做了..."）；rubric `general_principles.writing_style_rules.must` 第 3 条（"禁止简单罗列文献、数据、概念、技术参数；每一处引用都应为论证服务"）
- 建议：(a) 把"Werner→Rost"作为单线收窄主线，单独成段论证"理论预言→实验验证"的衔接；(b) 把 Leeb/Šmejkal/Ly/Jita 四条 altermagnet 理论文献集中成一段对比式描述（"在 altermagnet 理论方向，四项工作分别从...展开"）；(c) 把 McCarter/Horstmann/Qiu 三条选择定则工作集中在 §2 末段"选择定则与对称性约束"标题下。
- action：rewrite

#### [medium] rigor — L43 "宽带三阶非线性反常霍尔"作为 CrSb 非线性可行性支撑需明确"间接"语义
- 位置：rationale.md L43 / scheme L53
- 问题：Sankar 2025 [56] 是三阶非线性反常霍尔效应（χ³ 三阶张量），HHG 是高阶非线性（≥ 5 阶通常，3 阶低谐波也属 HHG 但能量集中在高阶）。两个非线性阶次不同。把三阶霍尔作为 HHG 可行性支撑属"间接"支撑，但 rationale 未明确"间接"语义。
- 违反：rubric `scoring_rubric.rigor` 0.70-0.79 档（"论证基本成立，但存在术语不一致、指标口径模糊、或个别逻辑跳跃"）
- 建议：把句改为"Sankar 等人在室温 CrSb 中观测到宽带三阶非线性反常霍尔效应 [56]，从非线性光学响应量级的角度间接支持 CrSb 在常规实验条件下的非线性信号可探测性"
- action：rewrite

#### [medium] rigor — L23-L25 "确实的"措辞稍带绝对化
- 位置：rationale.md L25 "但零净磁矩带来的背景压制效应本身是确实的"
- 问题："确实的"是绝对化措辞，与 §2 末段"被天然压制"语气过强相关；rubric `scoring_rubric.rigor` 0.80-0.89 档（"论证较严密，偶有表述不够精确之处，但不影响核心结论"）边缘。
- 建议：把句改为"但零净磁矩带来的背景压制效应本身可在独立测量（如磁场反转下的均匀磁化响应）中定量验证"
- action：rewrite

#### [medium] rigor — L77 末句 "三个层次构成'如何回答排除替代解释'的分析框架"模板化
- 位置：rationale.md L77 末句
- 问题："如何回答"是模板化句式，rubric `general_principles.anti_ai_patterns.remove` "动词堆砌"的边缘。
- 建议：把句改为"三个层次共同构成排除替代解释的方法学分析框架，§4 将进一步说明建立可辨识性判据的三个实施保障"
- action：rewrite

#### [medium] rigor — CrSb 关键材料参数无引用（T_N / 带隙 / SOC 三项）
- 位置：rationale.md L37（Sb SOC 100-200 meV 无引用）、L89（CrSb T_N 720 K / 带隙 0.13/0.6 eV 无引用）、scheme.md L27/L47/L53、content.md L57（MnTe 310 K 部分引 [69]）
- 问题：这些数值是选材论证、中红外共振论证与贝叶斯先验设定的物理基础，全部无引用。R1 M4 仍未修复。
- 违反：rubric `indicator_red_lines.evidence_fit`（"理论文献被用于支撑'实验确认'论断"）；rubric `general_principles.indicator_red_lines.indicator_measurable`（"每个指标应给出可操作的定义、计算公式与测量方法"）
- 建议：(a) CrSb T_N 720 K：补引 Reif 1958 经典 CrSb 磁性测量或现代 CrSb 单晶磁化率文献（如 Reif et al., *Phys. Rev.* 109, 612 (1958) 或近期补强文献）；(b) CrSb 带隙 0.13/0.6 eV：补引 CrSb 单晶光学吸收谱或 ARPES 文献；(c) Sb SOC 100-200 meV：补引 CrSb 第一性原理计算（如 DFT+SOC 文献）；(d) d 波分裂"典型值 100-500 meV"：补引 CrSb ARPES 实测自旋分裂幅度文献，并核实与文献报道（约 0.9 eV 量级）的差异是否需要上调先验区间。
- action：research + add + verify

#### [medium] rigor — κ < 10² 阈值口径需论证依据
- 位置：rationale.md L79、content.md §2.4、scheme.md L37
- 问题：FIM 条件数阈值在不同文献有 10³、10⁶ 等不同口径，申请书选 10² 较激进（边界更严格）。阈值依据未说明。
- 违反：rubric `indicator_red_lines.theory_applicability`（"使用某理论框架前须说明其适用条件，并注明失效边界"）
- 建议：在 rationale L79 或方法学手册补一段说明：10² 阈值的物理依据是参数协方差矩阵特征值由收敛到发散的过渡区，对应文献 Cochran [62] 给出的可唯一性条件——可直接引 "本项目 κ < 10² 的可辨识区间直接对接 Cochran [62] 的条件数判据" 作为依据。
- action：add

### P3（建议）

#### [medium] rigor — L5 凝聚态序参量教科书级一般论述挂 [25][26] 弱引用
- 位置：rationale.md L5
- 问题：教科书级一般论述（Landau 序参量定义）挂两条 altermagnet 专题论文作支撑，R1 L177 已标记。
- 建议：删去该处编号，或改挂综述 [39]（李亮兰鹏飞陆培祥综述）。
- action：rewrite

#### [medium] rigor — L93 第一重 "乘积控制"措辞稍带歧义
- 位置：rationale.md L93
- 问题："三因素的乘积控制"——是数学乘积 or 操作叠加？数学乘积语义不准。
- 建议：把句改为"磁场正反转、偏振配置切换与温度监测三者的联合扫描"
- action：rewrite

#### [medium] rigor — rationale §2 国内现状一段信息密度偏低
- 位置：rationale.md L61
- 问题：国内研究一段仅 7 行，提及孟胜课题组、李亮/兰鹏飞/陆培祥综述、Hansen/Madsen 理论工作，但与"国内尚未见 altermagnet HHG 序参量反演实验报道"的核心结论相比，前置铺垫较单薄。rubric `general_principles.writing_style_rules.must` 第 5 条（五层递进中"国内研究现状"层）部分达标。
- 建议：补充 1-2 个国内相关课题组的具体工作（如孟胜课题组的全光学 HHG 探测高压量子态 [22]），使国内现状层与"本项目定位"层衔接更紧。
- action：research + rewrite

#### [medium] rigor — rationale §3 §4 段长超标（600+ 字密集段）
- 位置：rationale.md L79 / L89
- 问题：范本锚段要求"每段 150-300 字"。rationale §3 L79 一段 600+ 字，§4 L89 一段 700+ 字（涵盖 CrSb 选材四前提、MnTe 备选、T_N/带隙/SOC 数据、Yes-Go/No-Go 判据）。两段密度均超标。
- 违反：rubric `reference_materials.style_benchmark.narrative_density`（"每段 3-6 句、150-300 字，段间用内容逻辑衔接"）
- 建议：把 L89 拆为 4 段：(a) CrSb 信号可探测前提；(b) CrSb 样品工程可行性；(c) CrSb 候选信号机制；(d) CrSb 备选路径完备性。每段 150-200 字。
- action：rewrite

#### [medium] boundary — rationale §4 与 scheme §1 判据数值重复（轻微越界）
- 位置：rationale.md L79 ↔ scheme.md L9-15
- 问题：判据数值（4 项）在 rationale 与 scheme 两章完全重复。合理性（立项依据给出判据体系，研究方案展开实施），不构成严重越界。
- 建议：在最终合并稿中可保留——rationale 给出判据的"为什么"，scheme 给出判据的"怎么用"，功能区分已明确，仅文字层面重复。如要严格去重，可在 scheme §1 改为"判据数值与立项依据 §3 完全一致"，避免数值重复罗列。
- action：rewrite（可选）

#### [low] rigor — R1 L177 弱引用问题（rationale L5）的延伸
- 位置：rationale.md L5
- 处理：已纳入 P3 列表（[medium] rigor — L5 凝聚态序参量教科书级一般论述挂 [25][26] 弱引用）

### 非问题清单（已排查但不构成问题）

- ✓ rationale §1-§4 五层递进结构清晰（rubric 达标）
- ✓ rationale §3 末段科学问题凝练含可证伪答案 + No-Go 边界 + 方法学起点（rubric 0.80-0.89 档）
- ✓ rationale §3 四项可证伪阈值在 rationale / content / scheme 三章数值完全一致（rubric 0.90-1.00 档）
- ✓ rationale L21 不可辨识性核心障碍表述具体可证伪（rubric 0.80-0.89 档上沿）
- ✓ rationale L59 载波包络相位与轨道角动量不纳入核心约束的设计原则前置声明（加分项）
- ✓ rationale L61 国内现状检索式精确（避免"国际空白"过度声明，trap 5 处理规范）
- ✓ rationale L69 / L73 / L99 操作定义、可证伪答案 + No-Go 边界 + 正负同等价值（加分项）
- ✓ rationale / content / scheme 三章术语一致性 100%（12 个核心术语全部一致）

## 对抗结论

- **本轮发现 16 个问题**（critical:0, high:5, medium:10, low:1；R1 遗留未在本轮重复计入 high 计数）
- **相比上一轮**：
  - R1（参考文献专项）综合 0.67；本轮（立项依据段落深审）综合 0.74
  - 改善：rationale §1-§4 整体写作质量与范本 anchor 接近（嵌入式引用 / 五层递进 / 可证伪判据 / 术语一致）
  - 新增：本轮发现 5 条 high 级别问题（4 条为 rationale 显性，1 条为跨章节遗留）+ 11 条 medium 级别问题
  - 未解决：R1 H1（[62][63] 年份）、H2（Werner 年份）、H4（d 波实验确认）、M4（CrSb 参数引用）、M5（申请人前期自引）5 条遗留问题在 rationale 章节内仍有体现
- **是否达到输出标准**：面上项目 min_overall_score=0.80、max_high_issues=0、max_medium_issues=3。本轮综合 0.74 < 0.80（未达）；high 5 条 > 0（未达）；medium 11 条 > 3（未达）。**未达输出标准**。
- **返工优先级**：
  - **P0**：4 条 high（anti_ai L79 超长句 / red_line H4 d 波实验确认 / red_line H1 H2 H4 跨文档年份 / red_line L89 共振措辞）—— 提交前必须消除
  - **P1**：1 条 high（narrative L33-L45 文献堆砌密度）+ 5 条 medium（rigor L43 / L23-L25 / L77 / CrSb 参数 / κ 阈值依据）
  - **P2**：5 条 medium（rigor L5 / L93 / §2 国内现状 / §3§4 段长 / boundary §4 scheme §1 重复）
- **下一轮评审建议聚焦**：
  - 把超长句拆分（4 条 >120 字）作为下一轮重点审查项
  - 跨文档年份统一（content.md L23 / L37、scheme.md L77 / L41 / L53 三处）
  - CrSb ARPES 文献补引
  - 申请人前期工作补引（如有）或降格表述
  - 研究基础模块（2026 三段式要求）的独立成文情况

## 锚点回归说明

每条评审意见标注的 rubric 条款：

| Rubric 条款 | 引用次数 | 触发问题 |
|---|---|---|
| `general_principles.writing_style_rules.must` 第 3-4 条 | 2 次 | anti_ai L79 / narrative L33-L45 |
| `general_principles.writing_style_rules.forbidden` 第 1 条 | 1 次 | narrative L33-L45 |
| `general_principles.anti_ai_patterns.remove` | 2 次 | anti_ai L79 / rigor L77 |
| `general_principles.indicator_red_lines.consistency_check` | 1 次 | citation-consistency H1/H2 |
| `general_principles.indicator_red_lines.novelty_claim_cautious` | 1 次 | red_line L89 |
| `general_principles.indicator_red_lines.no_exaggeration` | 1 次 | red_line L89 共振 |
| `general_principles.indicator_red_lines.theory_applicability` | 1 次 | rigor κ 阈值 |
| `general_principles.indicator_red_lines.evidence_fit` | 1 次 | rigor CrSb 参数 |
| `general_principles.indicator_red_lines.indicator_measurable` | 1 次 | rigor CrSb 参数 |
| `general_principles.scoring_rubric.rigor` 0.70-0.79 / 0.80-0.89 | 5 次 | rigor L43 / L23-L25 / L77 / κ 阈值 / CrSb 参数 |
| `general_principles.scoring_rubric.innovation` 0.80-0.89 | 0 次（潜在加分项） | — |
| `reference_materials.style_benchmark.narrative_density` | 1 次 | rigor §3§4 段长 |
| `reference_materials.benchmark_anchors.rationale_anchor` | 1 次 | narrative L33-L45 |
| `reference_materials.benchmark_anchors.innovation_anchor` | 0 次（rationale 不严格遵循四步闭环） | — |

## 评分

创新性：0.85
可行性：0.80
严谨性：0.78
研究基础：0.70
表达质量：0.62
综合评分：0.74