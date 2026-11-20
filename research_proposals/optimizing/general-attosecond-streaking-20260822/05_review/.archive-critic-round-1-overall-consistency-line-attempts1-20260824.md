# 对抗评审报告（第 1 轮 · 整体一致性版本线）— general-attosecond-streaking-20260822

- **评审对象（指令指定）**：rationale.md + content.md + scheme.md 三章整体一致性（逻辑衔接、术语一致性、内容冗余/矛盾）
- **项目类型**：面上项目（general；min_overall_score=0.85，max_high_issues=0，max_medium_issues=3）
- **评审日期**：2026-08-24（本轮全部结论基于实地核实：read_file 三章全文 / stat / python 词频与口径扫描 / crossref+arXiv 外部反查，非记忆或上轮印象）
- **评审 profile**：critic（红队）
- **标准配置**：`/Users/ll/Desktop/LinSai-CoPilot/memory/nsfc-standards.json`（2026-08-20 版，474 行完整读取）
- **版本线说明**：本文件为**整体一致性版本线**第 1 轮。05_review/ 同名文件此前先后被 rationale 线、content 线、scheme 线占用，均已归档（`.archive-critic-round-1-rationale-line-…` / `-content-line-…` / `-scheme-line-attempts1-20260824.md`）。四条版本线不要混淆。

---

## 一、评审对象状态核实（先核实再下结论）

### 1.1 三章节文件状态：全部非空，本轮首次拥有完整评审对象

```
sections/rationale.md   14204 字节（6664 字） mtime 08-24 07:42
sections/content.md     10207 字节（3955 字） mtime 08-24 09:13
sections/scheme.md      17729 字节（7260 字） mtime 08-24 09:13  ← scheme 线已于本轮评审触发前兑现
sections/references.md      0 字节（08-22 20:20，从未写入）
sections/full_review.md     0 字节（08-22 20:20，从未写入）
04_proposal/proposal-draft.md 42152 字节 mtime 08-24 09:15（三章重组体）
```

历史遗留的"聚焦章节 0 字节"问题（rationale→content→scheme 连续三轮扑空）**全部解决**；但 references/full_review 两线仍零产出，模块完整性 3/5（见第五节 C6）。

### 1.2 检测报告对象归属核查：本轮一致，历史"对象错位"问题解决

- 报告称全文字符数 17883；本地三章拼接实测 **17879**（差 4 字符，属切分口径噪声），且报告三条例句（"inzani等人[12]提出了rACE""综合上述分析，阿秒条纹技术在水窗及更高能区""本课题聚焦这一空白"）**逐字命中** rationale.md 对应段落。
- 判定：本轮检测报告对象 = 三章节文件本身，前两轮复发的 detection_mismatch（报告实为 proposal-draft.md）**已解决**。以下程序化数值按本对象采信。

---

## 二、执行清单对照

| # | 清单项 | 状态 | 证据/位置 |
|---|---|---|---|
| 0 | 模块完整性检查 | **不通过** | references.md / full_review.md 均 0 字节，完整性 3/5；2026 三段式要求的"研究基础"模块无载体（C6、M5） |
| 1 | 读取申请书与标准配置 | 通过 | 三章全文 + nsfc-standards.json 474 行（含 scoring_rubric、benchmark_anchors、indicator_red_lines） |
| 2 | 逐条对照执行清单 | **部分不通过** | 叙述式细项见表下；指标红线 5 条全部不通过（C1/C2/S1/S4） |
| 3 | 锚点对比（强制） | 已执行 | 见第四节，结论：差距明显 |
| 4 | 引用程序化 AI 检测结果（强制） | 已执行 | 见第三节；检出项全部列入问题清单（S6/M1/M3），severity≥[high] 已满足 |
| 5 | 按项目类型标准红队评审 | 已执行 | 21 项问题（critical 6 / high 8 / medium 5 / low 2） |
| 6 | 写作风格重点检查 | **部分不通过** | 叙述式骨架成立（0 bullet、段落过渡真实），但程序化 AI 密度三项超标 → S6 [high] |
| 7 | 每问题给可执行建议+违反条款 | 已执行 | 问题清单逐项标注"违反条款" |
| 8 | 严重度分级 + P1/P2/P3 | 已执行 | 见问题清单与对抗结论 |

**叙述式细项判定**：
- 以科学问题为主线展开：**通过**（R1→R2→R3 单向门控逻辑贯穿三章，scheme §1 明示递进前提）。
- "A做了X，B做了Y"堆砌：**临界**（rationale §2.4 连续三个年份开头"2024年inzani…2026年zhu…2025年hutcheson…"接近编年堆砌，但各例均服务"近期进展"论证功能；且该三例中两例文献存疑，见 C3/C5）。
- 条目式/bullet 替代论证：**通过**（全文 0 处 bullet，与范本一致）。
- 段落过渡与逻辑递进：**基本通过**（段间以内容衔接为主，"同时"类粘连见 S6）。
- 研究内容围绕核心问题：**通过**。
- 方案说明"为什么选这个方法"：**部分**（TDSE 选择有专门论证段 scheme §2.1；但核心干涉项修正无适用条件论证，S1）。
- 立项依据五层递进：**通过**（大背景§1→脉络§2→核心问题§2.5→国内§3→定位§4 齐备）。
- 研究目标每条含量化指标：**通过**（G1-G3 均含 <5% 类指标）。
- 特色创新四步闭环：**形式通过、实质违规**（三点均有"局限→方案→量化→定位"四段，但量化优势句"现有方法从未达到的精度指标"为无支撑优先权主张，S4）。

**指标红线 P0 逐条**：

| 红线 | 状态 | 证据 |
|---|---|---|
| consistency_check（口径一致） | **不通过（critical）** | 水窗能区三种口径并存（C1）；探测器角分辨率自相矛盾（C2）；双变量两套定义（S2） |
| uncertainty_constraint（物理约束） | **不通过（critical）** | C2：±2° 角分辨率与角积分（全角向求和）需求原理性冲突 |
| theory_applicability（适用条件） | **不通过（high）** | S1：干涉项公式无相干性/重叠判据论证 |
| novelty_claim_cautious（优先权表述） | **不通过（high）** | S4："从未达到""国内尚无系统性研究报道…尚属空白"（rationale §3 末段）无检索支撑 |
| implementation_path（方案→指标路径） | 部分通过 | 主链条有路径；但 R3 触发条件两套口径未定义关系（S7）、误差度量定义模糊（M4） |

---

## 三、写作风格评估（程序化检测引用）

程序化检测报告结果（对象归属已核实为本轮三章，见 1.2）：

- **死板关联词 18 次（阈值 8，扣 0.20）**："同时"×13（本地复核 rationale 9 + content 3 + scheme 1）、"然而"×5。
- **冗余修饰词 54 次（阈值 12，扣 0.42）**："系统"×17、"关键"×16、"显著"×5、"重要"×5、"完整"×4、"有效"×4。
- **超长句 severe 22 处（扣 0.44）**：本地按句末标点对三章复核 >120 字句 **14 处**（rationale 6 / content 3 / scheme 5）；报告值 22 与本地 14 的差异属切分口径（报告按 17883 字符的 draft 切分），不影响 [high] 定级。典型例："综合上述分析，阿秒条纹技术在水窗及更高能区面临两个相互耦合的核心挑战：多电子电离通道在能谱中发生重叠，导致传统FROGCRAB的二阶非线性响应假设失效，重构误差……"（rationale §4 段1，一句压缩四个论断）。
- 通过项：template_phrases 1、template_subject 0、meta_discourse 0、excessive_bold 合规、bullet_list_substitution 0、self_reference 0。

**强制声明：程序化检测发现 AI 写作模式，表达质量被强制限制（天花板 0.50）。**

评估：三章为真实叙述式行文（无 bullet、无模板主语、引用嵌入论证链），叙述式骨架合规；但"同时"作为段间粘合剂（13 次）与"系统/关键"修饰堆叠（33 次）使行文呈现明显的机械节律，超长句密度远超范本（范本超 80 字句占 12%-28%、单句不超 120 字；本文 14 句超 120 字）。对照 scoring_rubric.expression 的 0.60-0.69 档（"表达较差，大量模板套话…可读性低"）部分命中，但因程序化天花板 0.50 强制，表达质量取天花板内档位 0.46。

---

## 四、锚点对比（强制要求）

### 对比 1：rationale.md §1 段1-2 vs benchmark_anchors.rationale_example

**申请书原文**（rationale §1 段1-2）：
> "阿秒脉冲是当前人类探测电子超快动力学最精密的时间标尺。红外条纹场与极紫外/软X射线阿秒脉冲相互作用，光电子能谱中记录下的条纹相位包含阿秒脉冲的时间结构信息——这一技术被称为阿秒条纹技术，是阿秒计量学的核心手段[1-8]。……Goulielmakis等人[1]首次证明，条纹测量所记录的并非仅仅是脉冲包络，而是光电离释放电子波包的完整量子谱相位。"

**范本锚点**（rationale_example）：
> "高次谐波产生是飞秒激光与物质相互作用的高阶非线性、非微扰现象。基于高次谐波光谱的超快探测技术使得在飞秒甚至阿秒尺度上实时探测物质中电子及原子核的微观动力学过程成为可能。人们利用原子、分子气体高次谐波进行了大量气相原子分子的超快探测和控制研究[1-8]……2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰的高次谐波产生现象。"

**差距**：①语体——开篇定义句式与范本同构（合格），但申请书第二段即用破折号插入语（"——这一技术被称为"），范本判定规则明示"不用破折号插入语"；②引用嵌入——"Goulielmakis等人[1]首次证明"符合嵌入式引用范式（合格），但 §2.2 段3 出现"nature photonics 17, 629–635（2023）的后续报道指出……[11]"，把期刊卷期写进正文再叠 [N]，引用方式与全文其余处不统一；③论证密度——范本每句推进一层（现象→技术→应用→新现象），申请书 §1 段2-4 密度相当（合格），但 §2.1-§2.4 论据密度下降，多处整句与 content.md 逐字重复（见 S8），立项依据的独特论证资产被摊薄；④数据驱动——数值密度高（285 eV、322 as、20%、30%）优于平均水准，但关键数值的文献锚点经外部反查为虚构/错位（C3/C4/C5），数据驱动的可信度被抽空。

### 对比 2：scheme.md §2.1-§2.2 vs benchmark_anchors.scheme_example

**申请书原文**（scheme §2.1 段2）：
> "本项目采用 TDSE 数值模拟作为条纹信号建模的主框架。选择 TDSE 而非解析少带模型的物理理由如下。固体 HHG 与气体 HHG 的光电离场景存在一个关键差异：多通道效应在气体靶中表现为不同电离阈的贡献叠加，而非能带结构效应。TDSE 能够在单电子近似下严格处理双通道耦合势项……"

**范本锚点**（scheme_example）：
> "在前期的工作中，我们已经熟练掌握了利用含时薛定谔方程、含时密度泛函理论研究理想晶体高次谐波的数值模拟方法。为了适应本项目的研究，需要在理想晶体的计算中引入杂质的作用，本项目将采用在周期性排布的原子结构中引入少量杂质原子来模拟掺杂半导体。首先，求解定态本征值问题……"

**差距**：①"为什么选这个方法"——申请书 TDSE 段有真实论证（合格且是全文亮点），但引入"固体 HHG 与气体 HHG 差异"的对比对气体靶阿秒条纹课题是游离论据（该对比源自固体 HHG 文献语境，Yue&Gaarde 的规范一致性论点亦未给 [N]，见 S5）；②范本以"前期工作已掌握…"起笔体现预研衔接，申请书全章无任何前期工作锚点（M5）；③公式呈现——范本不含公式（细节让渡给方法学手册），申请书 §2.1-§2.2 直接排入 LaTeX 行内残缺公式（`$$E_final = …$$` 双美元记号在 .md 正文中渲染异常），且公式后紧跟的干涉项展开（S(E)=S₁+S₂+2√(S₁S₂)cosΔφ）无适用条件论证（S1），违反"公式推导放方法学手册"的分工；④可行性分析——范本要求"方案→原理→结论"链式，申请书 §4.1/§4.2 大段复述研究方案内容（S3），链式结构变形。

锚点对比结论：差距明显

（绑定规则：表达质量 ≤0.69、综合评分 ≤0.84，本轮均满足。）

---

## 五、模块完整性

| 模块 | 状态 | 说明 |
|---|---|---|
| rationale.md | ✓ 6664 字 | 五层递进齐备；文献表 16 条内嵌 §5 |
| content.md | ✓ 3955 字 | 总述+R1/R2/R3+G1-G3+K1-K3 齐备 |
| scheme.md | ✓ 7260 字 | 技术路线/理论/实验/可行性/难点/替代/创新/成果/年度计划齐备 |
| references.md | ✗ 0 字节 | 独立文献模块未落盘（rationale §5 内嵌表为当前唯一载体） |
| full_review.md | ✗ 0 字节 | 整体自查模块未落盘 |

模块完整性 3/5。另：2026 三段式（立项依据+研究内容+研究基础）中"研究基础"在全部落盘文件中无载体，scheme §3.1 一句"实验室已有的阿秒条纹装置"是全文唯一预研暗示（M5）。

---

## 六、维度评分（4 维等权，依据 scoring_rubric 档位）

> 评分纪律说明：本轮指令给出 4 维（创新/可行/严谨/表达）评分块，按 2026-08-15 校准纪律第 4 条采用 4 维等权（0.25×4），general 的 6 维 evaluation_focus 权重作为评审内容参照、不进入本评分公式（历史教训：勿混入导致加权自相矛盾）。

| 维度 | 权重 | 得分 | 档位依据（scoring_rubric） | 关联问题 |
|---|---|---|---|---|
| 创新性 | 0.25 | 0.72 | 0.70-0.79 档："有一定新意，但创新点表述不够锐利，或与已有工作的差异需更充分论证"——三条主线中两条建立在既有原理推广上（[3] 角积分抑制、rACE/CNN 为备选），真正的原创核心（解析修正项）数学实质缺失且其"空白"论证依赖虚构文献坐标系，与已有工作的差异无法在可信文献系内确认 | S1/S4/C3-C5 |
| 可行性 | 0.25 | 0.66 | 0.60-0.69 档："可行性存疑，核心技术路线缺乏支撑，或关键装置/指标超出当前技术水平"——探测器指标自相矛盾（C2）、2% 压制效率无先例验证、无预研基础（M5）、scheme 全章零 [N] 支撑（S5）；但技术路线骨架（TDSE+门控+替代路径）本身自洽 | C2/S1/S3/M5 |
| 严谨性 | 0.25 | 0.35 | 低于 0.60 档："多处事实错误或逻辑矛盾"。依据 references-audit 评分纪律"critical 虚构文献条目：严谨性扣至 0.3-0.4 区间"——[2][3] 两条关键文献经外部反查确证虚构、[2505.06275] 张冠李戴、[2510.17949]/[2511.08391] 作者反转+错挂（C3/C4/C5）；叠加指标红线违规 3 类（C1/C2/S2，按纪律本应扣至 0.6-0.7，与虚构叠加取低者） | C1-C6/S2/S7 |
| 表达质量 | 0.25 | 0.46 | 程序化天花板 0.50 强制（**程序化检测发现 AI 写作模式，表达质量被强制限制**）；rubric 0.60-0.69 档部分命中（模板套话密度高、可读性受损），锚点结论"差距明显"绑定上限 0.69 不触顶 | S6/M1/M3/L1 |

**综合评分 = (0.72 + 0.66 + 0.35 + 0.46) / 4 = 0.55**

自洽复核：0.18+0.165+0.0875+0.115 = 0.5475 ≈ 0.55 ✓；维度分、问题数、综合分三者无矛盾 ✓；锚点绑定（差距明显→综合 ≤0.84）满足 ✓；表达 ≤ 天花板 0.50 ✓。

---

## 七、问题清单（P1=必改，P2=强烈建议，P3=建议）

### [critical] red_line（consistency_check）— C1：水窗能区口径跨章三说（P1）
- 位置：rationale §1 段3"碳K边~285 eV至氮K边~400 eV"；content §2.2 段3"碳K边 ~285 eV、氮K边 ~400 eV"与 §2.4 段1/§2.5 G1"284–400 eV"；scheme §1 段7"284 eV 至…400 eV"但难点一"能量 280–400 eV"。
- 问题：同一能区出现 285–400 / 284–400 / 280–400 三种口径（碳 K 边取 284 还是 285 eV、扫描下限 280 还是 284 eV），且"软 X 射线 400–543 eV"（content G3、scheme §3.3）与 rationale"水窗…至更高能区"的能区划分叙述未对齐。C K 边公认值 284 eV（N K 边 400 eV/409.9 eV 亦有口径问题）。
- 建议：全文统一为"水窗 284–400 eV（C K 边 284 eV 至 N K 边 400 eV）"；scheme 难点一参数扫描下限改 284 eV 或说明 280 eV 为预留裕量；软 X 射线区段上限 543 eV（O K 边）需在首次出现处注明定义。
- 违反条款：indicator_red_lines.consistency_check；section_standards.full_review 第 2 条。
- action：rewrite

### [critical] red_line（uncertainty_constraint）— C2：探测器指标自相矛盾，角积分与 ±2° 角分辨率原理冲突（P1）
- 位置：scheme §1 段4"位置灵敏探测器，角分辨率 ±2°"；§3.1"16 通道 TOF 阵列…角向覆盖 360°"；§3.2"事后在数据处理中做角向求和（等效于角积分）"。
- 问题：①§1 称"能量分辨率 ΔE/E ≈ 1%"，§3.1 称"单通道能量分辨率 1 eV @ 400 eV"——400 eV 处 1% 即 4 eV，与 1 eV 相差 4 倍，两处指标直接矛盾；②角积分的物理本质是对全立体角（或大acceptance）求和以平均掉角向相位结构，"±2° 角分辨率"描述的是角分辨能力——若 16 通道 TOF 以 ±2° 分辨率离散采样后再求和，只是离散角积分，其与 Zhong 方案连续角积分的等价性需论证；且 16 通道×±2° 远不能覆盖 360°（约需 90 通道），构型描述自相矛盾；③§3.2 又要求"同步采集的角分辨数据用于提取偶极相位信息"，角积分与角分辨两种互斥测量模式在同一探测器上的时分复用方案未说明。
- 建议：给出探测器最终单一规格表（通道数、每通道角向 acceptance、能量分辨 @ 参考能量）；将"±2°"改为"每通道角向 acceptance ±X°，16 通道覆盖 ±Y° 扇区，全谱角积分由机械扫描或转台实现"；说明角分辨模式与角积分模式如何切换。
- 违反条款：indicator_red_lines.consistency_check / uncertainty_constraint / no_exaggeration；section_standards.scheme 第 1 条。
- action：recalculate + rewrite

### [critical] evidence_risk（citation_integrity）— C3：核心文献 [2] 虚构——真实来源为 Cousin/Di Palo 等 PRX（P1）
- 位置：rationale §5 [2]"Bizon M D, Kienberger R, Gropper S, et al. Attosecond streaking in the water window. Science, 2017, 358: 1284-1289"；正文 §1 段3、§2.2、content §2.2、scheme §3.1/§4.1 均以"Klausen 等人[2] 2017 年 Science"引用。
- 问题（外部反查实证）：crossref 检索"Attosecond streaking in the water window"唯一匹配 **Cousin, Di Palo, Buades, Teichmann, Reduzzi, Devetta, Kheifets, Sansone, Phys. Rev. X 7, 041030 (2017)**——期刊是 PRX 而非 Science、无"Bizon/Kienberger/Gropper"作者、一作非 Klausen。Science 358 (2017) 该页码区间的水窗条纹论文不存在。正文一作（Klausen）、文献表一作（Bizon）、真实一作（Cousin）三方分裂；322 as、20% 重构误差、15%/30% 阈值等全文定量地基全部悬挂在该虚构条目上。[11]（Nat. Photonics 17, 629–635 (2023) 多通道检索误差）crossref 反查同样无法匹配，卷期存疑。
- 建议：以 PRX 7, 041030 原文为准重建 [2] 条目与全部数值引用（322 as、误差阈值须与 PRX 原文核对）；[11] 给出可验证 DOI 或替换为真实综述；全文以 references 条目为唯一真值源统一作者名。
- 违反条款：indicator_red_lines.no_exaggeration（证据地基）；section_standards.references 第 4 条"无张冠李戴"。
- action：research + rewrite

### [critical] evidence_risk（citation_integrity）— C4：核心文献 [3] 虚构——真实来源为 Pabst & Dahlström PRA（P1）
- 位置：rationale §5 [3]"Zhong S, Teng J, Zhang P. Attosecond pulse characterization with coherent Rydberg wavepacket quantum beats. Phys Rev Lett, 2016, 116: 143001"；正文 §2.3/§4、content §2.3、scheme §3.2/§4.1 以"zhong/Zhong 等人[3] 2016（PRL）"引用。
- 问题（外部反查实证）：该主题真实论文为 **Pabst & Dahlström, "Eliminating the dipole phase in attosecond pulse characterization using Rydberg wave packets", Phys. Rev. A 94 (2016)**——作者、期刊（PRA 非 PRL）、标题均与条目不符，条目为虚构。R2 整条研究线的原理基石（角积分压制 <2% 的"理论预估"）悬挂在虚构条目上。
- 建议：以 PRA 94 原文重建 [3]，核对"角积分压制偶极相位"的原始结论与定量预估是否支持 <2%；scheme §4.1"量子力学对称性的直接推论"表述需与原文核对。
- 违反条款：section_standards.references 第 4 条；nsfc-red-team-review 陷阱 1。
- action：research + rewrite

### [critical] evidence_risk（ghost_citation）— C5：arXiv 编号引用张冠李戴 + 作者反转 + scheme 裸引无编号（P1）
- 位置：content §2.2 段4"[2505.06275]"、§2.4 段3"[2510.17949]…[2511.08391]"；scheme §2.1"Yue 与 Gaarde"、§4.2"Csizmadia 等人 2025 年（arXiv:2504.08448）""Meier 等人 2025 年（arXiv:2501.08966）"。
- 问题（外部反查实证）：①arXiv:2505.06275 真实标题为 "SinBasis Networks: Matrix-Equivalent Feature Extraction for Wave-Like Optical Spectrograms"（机器学习论文），与正文所述"19.2 as 水窗软 X 射线孤立脉冲"完全无关——编号张冠李戴；②[2510.17949] 是 Han 的 Comment、[2511.08391] 是对 Han 的 Reply，正文将"19.2 as 原始报道"归于 [2510.17949] 属作者角色反转，且原始论文（应另有正刊编号）从未被引用；③scheme 正文的 Yue&Gaarde、Ardana-Lamas、Han、Csizmadia、Meier、Inzani（§3.1 无编号）、Zhu（§3.2 无编号）共约 6 处裸提及，全部无 [N] 角标、未入任何文献表——scheme 全章 [N] 角标数为 0。
- 建议：检索"Brilliant source of 19.2 attosecond soft X-ray pulses"原始论文编号并更正三处角色；[2505.06275] 替换为真实来源；scheme 全部裸提及文献补 [N] 并入表；Yue&Gaarde 规范一致性论点给出可验证出处。
- 违反条款：indicator_red_lines.novelty_claim_cautious（证据支撑）；section_standards.full_review 第 5 条 / references 第 3 条。
- action：research + add

### [critical] missing_content（module_incomplete）— C6：references.md 与 full_review.md 仍为 0 字节，模块完整性 3/5（P1，管线侧）
- 位置：sections/references.md、sections/full_review.md（mtime 停留在 08-22 20:20）。
- 问题：五模块仅三模块落盘；文献目前唯一载体是 rationale §5 内嵌 16 条，与 content/scheme 的引用需求（含 6 处裸提及待入表）脱节；整体自查模块缺失使跨章口径问题（C1/C2/S2）无出厂拦截。
- 建议：writer 下一轮优先落盘 references.md（30-40 篇规模，见 M2）并执行 [N] 双向映射；full_review.md 按 section_standards.full_review 五条清单自查后落盘。
- 违反条款：section_standards.references 第 1 条 / full_review 全部；管线调度约定（历史 [high] pipeline_integrity 的延续形态）。
- action：add

### [high] red_line（theory_applicability）— S1：干涉项公式无适用条件与失效边界论证（P1）
- 位置：scheme §2.2 段3"设总光电子能谱为 S(E) = S₁(E) + S₂(E) + 2√(S₁S₂)cos(Δφ)，其中第三项为干涉项"。
- 问题：该干涉形式成立的前提是两通道电子波包相干叠加且谱上重叠——若通道能谱不重叠干themselves涉项为零、若电离时间差远大于相干时间则交叉项平均消失；对孤立脉冲单发测量与多脉冲累积测量，Δφ 的统计意义完全不同。正文未给出任何适用条件（重叠宽度、相干时间、单发/累积口径），而这是 R1 全部算法设计的前提公式。公式本身的呈现形式（行内残缺 LaTeX）也不符合"公式推导放方法学手册"的分工。
- 建议：在 §2.2 增加适用条件段（通道谱重叠宽度 ≥ 相干宽度的判据、单发 vs 累积测量的 Δφ 定义）；完整推导移至 methodology-manual.md，正文只留结论式与条件。
- 违反条款：indicator_red_lines.theory_applicability / indicator_measurable；methodology_manual 分工约定。
- action：rewrite + verify

### [high] red_line（consistency_check）— S2：G3 与 R3/scheme 的"双变量"是两套自变量（P1）
- 位置：content §2.5 G3"以电离通道数、光电子动能为双变量"；content §2.4 段2 与 scheme §3.3"自变量为能区宽度（光子能量区间）与通道重叠度（百分比）"。
- 问题：同一"双变量误差依赖图谱"存在两套定义——(电离通道数, 光电子动能) vs (能区宽度, 通道重叠度)，量纲、取值、实验设计完全不同；三处出现互不相同，评审无法判断图谱到底画的是什么。
- 建议：统一为一套（建议保留"光子能量区间×通道重叠度"，因 R3 靶材配置即按此设计），G3 改写并说明"电离通道数/光电子动能"仅作为图谱上的标注参量而非自变量。
- 违反条款：indicator_red_lines.consistency_check；section_standards.full_review 第 2 条。
- action：rewrite

### [high] narrative（boundary）— S3：scheme §4 可行性分析复述研究方案内容（P2）
- 位置：scheme §4.1 段1（复述多通道修正原理，与 §2.1/§2.2 重复）、§4.2 段2-3（复述探测器规格与 CNN 备选，与 §3.1/§3.2/§6 重复）、§4.3（复述三条门控逻辑，与 §1 重复）。
- 问题：content_boundaries 明示"可行性不复述研究方案做法"；§4 三小节中约六成篇幅是方案内容的重述，真正的"为什么能做成"论证（原理先例、团队能力、预研数据）占比极低，且无前期工作支撑（见 M5）。
- 建议：§4.1 压缩为"原理成立性"两段（通道干涉已被实验证实→解析修正数学上自洽）；§4.2 保留文献对标但删去装置规格复述；§4.3 门控逻辑一句话引用 §1；腾出篇幅写预研基础。
- 违反条款：content_boundaries.可行性_回答为什么能做成 / 不可越界；section_standards.scheme 第 3 条。
- action：rewrite

### [high] red_line（novelty_claim_cautious）— S4：优先权表述无支撑（P2）
- 位置：scheme §7 创新点一"这是现有方法从未达到的精度指标"；rationale §3 段2"国内尚无系统性研究报道"、段3"尚属空白"；scheme §3.1 段5"本项目首次在实验中检验通道间相位干涉项的解析形式"。
- 问题："从未达到""尚无报道""空白"均无检索范围/截止日期/文献综述支撑；且 [2][3] 两条支柱文献为虚构（C3/C4），"现有方法"的真实状态本身未经核实——若 PRX 7.041030 或其后续已含修正尝试，"首次"主张即塌方。
- 建议：全部改为限定式表述（"据 2026-08 检索（Web of Science/inspire 检索式附方法学手册），尚未见……"）；"从未达到"改为"较已报道的 >20% 重构误差，本方案以 <5% 为设计指标"。
- 违反条款：indicator_red_lines.novelty_claim_cautious；innovation_anchor"不使用国际领先/填补空白等无依据表述"。
- action：research + rewrite

### [high] evidence_risk — S5：scheme 全章 0 个 [N] 角标，6 处文献裸提及（P2）
- 位置：scheme §2.1（Yue 与 Gaarde）、§4.2（Csizmadia arXiv:2504.08448、Meier arXiv:2501.08966）、§3.1/§3.2（Klausen/Zhong 有名无号）、§4.2（Zhu）；content §2.2/§2.4 的 3 个 arXiv 编号引用（见 C5）。
- 问题：研究方案章对文献的引用全靠作者名+年份裸提及，无编号体系；两处 2025 arXiv 预印本用于支撑装置可行性，未入文献表也未标注预印本状态（陷阱 1：预印本当已发表事实）。反查已证实 2504.08448 标题为 "Active stabilization for ultralong acquisitions in an attosecond pump-probe beamline"（与"±81 as 非共线干涉仪"表述需核对细节）、2501.08966 为 "Reconstructing Time-of-Flight Detector Values of Angular Streaking Using Machine Learning"（"LCLS 真实数据验证仿真训练泛化"与标题主题吻合但"Meier"作者名待核）。
- 建议：scheme 全部文献补 [N] 并入 references.md；预印本标注"arXiv 预印本"状态；Csizmadia/Meier 两处的指标叙述与原文逐项核对。
- 违反条款：section_standards.full_review 第 5 条；nsfc-red-team-review 陷阱 1。
- action：verify + add

### [high] anti_ai — S6：程序化检测三项超标（P2）
- 位置：全文（检测报告 + 本地复核：rationale "同时"×9/"然而"×4，content "同时"×3，冗余修饰"系统"×17/"关键"×16 全文分布，>120 字句 14 处本地复核）。
- 问题：①死板关联词 18 次（阈值 8，扣 0.20），"同时"作为段间粘合剂高频出现（如 rationale §2.2 段2"同时，该工作揭示了…"）；②冗余修饰 54 次（阈值 12，扣 0.42），"系统标定/系统性工作/系统检验"与"关键技术/关键设计/关键科学问题"造成名词化膨胀；③超长句 22 处报告值（扣 0.44），典型如 rationale §4 段1（一句 120+ 字压缩四个论断）、§4 段3（一句内并列三个分号长句）。表达质量被程序化天花板强制限制在 0.50。
- 建议：①"同时，"开头的段落改内容衔接（"该工作同时揭示…"并入上句或改"这项实验的另一方面是…"）；②"系统/关键"各保留 ≤5 处实义用法，其余删除或换具体动词（标定/检验/设计）；③>120 字句全部拆为 2 句（14 处定位清单已列，优先拆 rationale §4 段1/段3、content §2.4 段3、scheme §1 段7）。
- 违反条款：anti_ai_patterns.remove（死板关联词/冗余修饰/超长句）；sentence_rhythm（单句超 120 字必拆分）。
- action：rewrite

### [high] logic_gap — S7：R1 与 R3 的修正触发条件是两套不可换算的量（P2）
- 位置：content §2.2 段3"通道重叠宽度 > 1 eV 时须触发修正"；content §2.4 段3 与 scheme §3.3"R1 修正项在通道重叠度 > 15% 时必须启用"。
- 问题：一套触发条件以谱重叠宽度（eV）为单位、一套以多通道贡献占比（%）为单位，两者关系（同一物理场景下 1 eV 宽度对应多少占比？依赖截面比与谱形）未定义；R3 图谱的"通道重叠度"轴与 R1 的"重叠宽度"判据无法衔接，门控逻辑在 R1→R3 传递时失效。
- 建议：统一以"多通道贡献占总截面百分比"为主判据（有 [2] 实验数据支撑），“>1 eV 重叠宽度”降级为 R1 模拟中的二级条件并给出两者换算关系式。
- 违反条款：indicator_red_lines.implementation_path / consistency_check。
- action：rewrite

### [high] narrative（boundary）— S8：rationale 与 content 存在整句逐字重复（P2）
- 位置：①rationale §1 段4 末句与 content §2.3 段1 末句逐字相同："现有方法通常依赖预先校准靶材相位来规避这一困难，但这使得不同靶材的测量结果不可直接比较，阻碍了阿秒条纹作为跨体系量子探针的标准化应用。"②rationale §2.3 段3"这与常规阿秒脉冲表征场景（孤立脉冲、无特定靶材制备）存在兼容性问题"与 content §2.3 段2 近逐字重复；③Klausen 阈值论述（15%/30%/20%）在 rationale §1/§2.2、content §2.2、scheme §4.3 四处重复展开；④Zhong 角积分原理（"角积分过程对不同磁量子数的偶极矩阵元做平均"）在 rationale §2.3、content §2.3、scheme §3.2 三处重复。
- 问题：跨章节大量重复（含整句 verbatim 复制），三段式 30 页限额下挤占论证空间，且暴露"每章重新论证同一论据"而非"章节间引用衔接"的结构问题。
- 建议：物理机理唯一归属——多通道失效机理详述归 rationale §2.2，content §2.2 改一句引用（"如立项依据 §2.2 所述…"），scheme 不再展开；偶极相位耦合与 Zhong 原理同理；重复句全部改写为章节功能口径。
- 违反条款：content_boundaries（跨章节重复）；style_benchmark.section_coherence（章节逻辑呼应而非重复）。
- action：rewrite

### [medium] narrative — M1：章节编号体系三制并存 + scheme 内部双指称（P3）
- 位置：rationale 用"### 1./2./3."、content 用"### §2.1/§2.2…"、scheme 用"### 1./2."；scheme §1 内"阶段一/二/三"与全文"R1/R2/R3"并行指称同一对象。
- 问题：三套编号体系（无§数字 / §2.x / 数字）不统一；scheme 读者需自行映射"阶段二=R1 实验"。
- 建议：统一为全文连续编号（推荐（一）（二）（三）内 1./2./3. + 小节 x.y）；scheme 中"阶段 N"首次出现处绑定"（=R N）"后统一用一套。
- 违反条款：section_standards.full_review 第 3 条（术语全文统一）。
- action：rewrite

### [medium] evidence_risk — M2：文献规模不足 + 内嵌表与独立模块脱节（P2）
- 位置：rationale §5（16 条）；references.md 0 字节。
- 问题：general 标杆 30-40 篇，现存 16 篇且其中 [2][3] 虚构、[11] 存疑、[4]-[8] 作者姓氏小写（"Paz J, Garcia S"应为全大写姓氏格式）、[12] 期刊名不完整（"J Phys, 2024, 16: 252301"实为 Journal of Physics: Photonics）、[13] 卷期格式异常；content/scheme 另有约 6 处引用未入表（S5）。
- 建议：references.md 落盘时扩充至 30-40 条（补 R2/R3 支撑文献：Wigner 时延类、角分辨条纹类、水窗源类近三年工作），统一 GB/T 7714 格式，逐条完成 DOI/arXiv 反查后再入表。
- 违反条款：section_standards.references 第 1/2 条；references-audit 数量纪律。
- action：add + research

### [medium] rigor — M3：术语大小写与姓名格式漂移（P3）
- 位置：rationale §2.1 段2 句首" paz 等人[4]"、" kienberger等人[5]"（小写+前导空格，明显排版事故）；"nature photonics 17, 629–635（2023）"期刊名小写且卷期写入正文；"FROGCRAB"全文统一缺连字符（规范为 FROG-CRAB）；作者姓名大小写混用（zhong/inzani/zhu 小写 vs Klausen/Goulielmakis 大写）。
- 问题：术语与姓名格式不统一，句首小写属语病级硬伤。
- 建议：句首字母大写修复；期刊名规范大写；人名统一"姓氏首字母大写"；FROG-CRAB 全文统一（或全文统一用 FROGCRAB 并在首次出现处括注）。
- 违反条款：P1 修改优先级"语病笔误"；section_standards.full_review 第 3 条。
- action：rewrite

### [medium] red_line（indicator_measurable）— M4："均方根相位误差 < 5%"量纲与口径未定义（P2）
- 位置：scheme §2.2 段4"重构脉冲与真实脉冲的均方根相位误差 < 5%"；content G1"误差定义为修正后重构脉冲相位与原始实验数据的均方根偏差"。
- 问题：相位是角量（rad/as），"相位误差 5%"除非定义为相对某归一化量的百分比，否则量纲不成立；G1 的定义（重构相位 vs 实验数据的偏差）与 scheme 的定义（重构 vs 真实脉冲）不是同一对象——"真实脉冲"在实验中不可得，只有模拟中存在，两个场合混用同一 5% 判据。
- 建议：明确定义（如"谱相位加权均方根偏差 σ_φ = [∫|Δφ(E)| w(E)dE]^(1/2)，以 as 或 rad 计，阈值 X"）；实验场合判据改为"修正后与同步重构参考的偏差"或"与模拟真值的偏差（模拟验证）+ 与 FROGCRAB 单通道基准的一致性（实验验证）"两口径分列。
- 违反条款：indicator_red_lines.indicator_measurable / consistency_check。
- action：recalculate + rewrite

### [medium] logic_gap — M5：研究基础与预研数据完全缺位（P2）
- 位置：全文（scheme §3.1"实验室已有的阿秒条纹装置"为唯一暗示；rationale §3 引 [15] SIOM/物理所平台但与申请人关系未说明，且 §3 称"中国科学院物理研究所"、[15] 标题写"at SIOM"，机构口径也冲突）。
- 问题：general 评审 checklist 第 4 条"预研基础是否支撑课题可行"无法回答；可行性分析（S3 删复述后）将无内容可写；评审专家无法判断"为什么是你做"。
- 建议：在研究基础模块（或 scheme §4 扩充）写明：现有装置参数、前期条纹测量/重构经验、TDSE 模拟代码积累、预研模拟初步结果各一段；[15] 机构口径统一并说明与本团队合作基础。
- 违反条款：project_types.general.review_checklist 第 4 条；three_why.why/how。
- action：add

### [low] expression — L1：排版与表述瑕疵（P3）
- 位置：scheme §2.1 行内残缺公式记号（$$…$$ 单行内未闭合渲染）；rationale §2.4"优于 24 as 的绝对延迟校准精度"（"精度 24 as"量纲表述歧义，应为"24 as 的绝对延迟确定度/分辨率"）；rationale §2.2 段3 期刊卷期内嵌正文（见 M3/锚点对比 1）。
- 建议：公式改规范块级或移方法学手册；"精度"改"确定度"；期刊卷期从正文撤回文献表。
- 违反条款：P3"统一格式细节"。
- action：rewrite

### [low] logic_gap — L2：预期成果节点与年度计划轻微错位（P3）
- 位置：scheme §8"R1 修正算法验证后投稿 1 篇（方法论）"（R1 实验验证在第二年）；§9 第一年"期间发表方法论相关论文 1 篇"（第一年仅完成模拟）。
- 问题：第一年即发"方法论论文"与"R1 验证后投稿"节点时序矛盾（第一年只有模拟结果可发，应表述为模拟方法学论文）；4-5 篇总数与各年节点加总勉强相符但口径含混。
- 建议：第一年节点改为"基于 TDSE 模拟的方法学预研论文 1 篇"，与 §8 的"R1 验证后"节点区分。
- 违反条款：style_benchmark.section_coherence（年度计划对应课题划分）。
- action：rewrite

---

## 八、历史遗留问题核对表（跨轮持久化，逐条基于当前文本判定）

| 历史问题 | 本轮状态 | 当前证据 |
|---|---|---|
| [critical] rationale.md 0 字节 | **已解决** | 6664 字，五层递进齐备（§1→§4+文献表） |
| [critical] content.md 0 字节 | **已解决** | 3955 字，R1-R3+G1-G3+K1-K3 齐备 |
| [critical] scheme.md 0 字节 | **已解决** | 7260 字，08-24 09:13 落盘，本轮首次成为可评审对象 |
| [critical] 其余模块 0 字节（完整性 0/5→1/5→2/5） | **仍存在（形态更新为 references+full_review 缺失，3/5）** | → C6 |
| [high] pipeline_integrity（writer 单线推进、评审连续扑空） | **主体已解决**（三内容线本轮全部兑现）；残余为 references/full_review 两线未兑现，并入 C6 观察 | 时间线见 1.1 |
| [critical] 检测报告对象错位（实为 proposal-draft.md） | **已解决** | 17883≈17879 字符、三例句逐字命中三章（1.2） |
| [critical] 水窗口径跨章矛盾 285/284/280 | **仍存在且确认** | → C1（scheme 难点一新增 280–400 变体） |
| [critical] [2] 一作归属 Klausen vs Bizon 分裂 | **仍存在并升级为虚构定论** | 外部反查：真实来源 Cousin et al. PRX 7, 041030 → C3 |
| [high] 文献群存疑（[2] 乱码/混改、[12][13] 卷期异常、[4]-[8] 姓氏小写） | **仍存在并扩大**（新增 [3] 虚构、arXiv 三编号错位、scheme 6 处裸引） | → C3/C4/C5/M2/M3 |
| [high] anti_ai 三项（关联词/修饰/超长句） | **仍存在** | 18/54/22（报告值）→ S6 |
| [high] content §2.2 条目化+越界预置方案 | **部分改善** | content §2.2 仍以"第一/第二/第三"层次句展开但已嵌入论证；越界问题转移至 scheme §4 → S3 |
| [high] red_line novelty（"国内尚无…尚属空白"） | **仍存在** | rationale §3 未改 → S4 |
| [P0] 占位降档规则（0 字节维度 0.1-0.3） | **本轮不再适用** | 三章有实质内容，恢复正常档位评分 |

---

## 九、对抗结论

- **本轮发现 21 个问题**（critical:6，high:8，medium:5，low:2）。
- **相比上一轮**（scheme 线，综合 0.30）：评分 0.30→0.55（+0.25）。已解决 6 项（三章 0 字节全部兑现、检测对象错位、评审扑空）；仍存在 5 项（水窗口径、[2] 归属、文献群存疑、anti_ai 三项、novelty 表述）；新增 9 项（C2 探测器矛盾、C4 [3] 虚构、C5 arXiv 错位、S1 干涉项条件、S2 双变量、S3 可行性越界、S7 触发条件两套、S8 逐字重复、M4 误差定义等）。
- **核心判断**：写作骨架与逻辑架构已是四轮以来最好状态（叙述式成立、门控递进清晰、指标量化到位），但**证据地基坍塌是本轮最严重发现**——[2][3] 两条支柱文献经 crossref/arXiv 外部反查确证虚构，3 个 arXiv 编号张冠李戴或作者反转，scheme 全章零编号引用。物理内容越写越满，文献层越查越空，这正是"AI 生成文献表"的典型指纹。在文献表重建并逐条反查通过之前，任何评分都建立在流沙上。
- **是否达到输出标准：否**。综合 0.55 ≪ min_overall_score 0.85；high 问题 8 ≫ max_high_issues 0；medium 5 > max_medium_issues 3。
- **返工优先级**：P0 = C3→C4→C5（文献表重建+逐条外部反查）→ C1→C2（口径统一）→ C6（references/full_review 落盘）；P1 = S1-S8；P2 = M1-M5；P3 = L1-L2。
- **下一轮建议**：writer 完成 references.md 落盘后，做 [N] 双向映射（正文→条目、条目→正文、僵尸条目）+ 全量文献真实性反查（arXiv title + crossref DOI 五件套比对）；同时按 S6 清单完成三项 anti_ai 降密（目标：关联词 ≤8、修饰 ≤12、>120 字句=0）。

---

## 评分
创新性：0.72
可行性：0.66
严谨性：0.35
表达质量：0.46
综合评分：0.55
