# 对抗评审报告（第 2 轮 · 立项依据专项 + 跨章节一致性）

项目类型：general（面上项目）
聚焦章节：rationale.md（§1.1–§1.5）+ references.md（章节修复确认）+ content.md / scheme.md（跨章节一致性）
评审日期：2026-08-19
前序参考：critic-round-1.md（参考文献专项）+ critic-round-1.archive-*.md（整体一致性审查各分章归档版本）

---

## 一、综合评分

**0.61 / 1.00**（按 general 项目权重：创新性 0.30 + 可行性 0.25 + 科学意义 0.20 + 研究基础 0.15 + 表达质量 0.10）

| 维度 | 权重 | 得分 | 主要拖累 |
|------|------|------|----------|
| 创新性（innovation）   | 0.30 | 0.78 | 双平台×双范式定位清晰，但 i-wave HHG 指纹新理论预言与 Rajpurohit [21]/Ghorashi-Rappe [17] 既有工作的边界表述模糊，"首次/尚未见" 5 处声明失锚 |
| 可行性（feasibility）  | 0.25 | 0.72 | 方案→原理→结论链完整（scheme §3.6），但 R1 中"光应力 vs 位移电流机制"分工与 TDDFT 模拟收敛性未充分论证；THz 场强 0.1–1.0 MV/cm 与 h-BN 文献 2403.06531 的 4 MV/cm 在物理图像上同量级但**参数空间缩小 10 倍**未给出说明 |
| 科学意义/严谨性（rigor） | 0.20 | 0.40 | **P0 残存 4 项**：rationale.md L41 [11]/[10] 团队-编号错配未修、L21 Ruiz/Fe₂CoGaTe₂ [16]→应为 [17]、L25 Yarmohammadi [21]→应为 [22]、L31 "THz 频段" [10] 错配；references.md 已建 40 条但 scheme.md 0 处 [N] 引用与编号体系完全断裂；arXiv 裸引 5+2+1=8 处未入库到正文 [N] 格式；content.md L15/L19/L29/L31/L39 + scheme.md L19/L29/L63 共 8 处裸 arXiv 号 |
| 研究基础 | 0.15 | 0.65 | rationale §1.4 国内研究现状叙述具体（华中科大、上海大、上海交大），但 [11]/[10]/[13] 等编号绑定错误团队造成研究基础可信度受损；本课题组预研基础仅 1 篇引用 [29]（"in preparation"），预研数据严重不足 |
| 表达质量（expression） | 0.10 | 0.50 | 五层递进结构完整（背景→沿革→挑战→国内→定位）；段落密度 150-300 字达标；但 AI 模式密度超标：`建立` 22 次、`提供` 16 次、`为...提供...基础` 4 次 + `为...提供...工具` 3 次（共 7 次"为...提供..."类）逼近 15 次红线；`首次` 4 次 + 4 处"尚未见/尚未"声明失锚；超 120 字句 10 个（9.5%） |

**加权计算**：0.78×0.30 + 0.72×0.25 + 0.40×0.20 + 0.65×0.15 + 0.50×0.10 = 0.234 + 0.180 + 0.080 + 0.0975 + 0.050 = **0.6415**

按 v6.9.25 强制约束：**锚点对比结论 = 差距明显 → 表达质量 ≤ 0.69，综合评分 ≤ 0.84**；当前评分 0.6415 在 ≤0.84 范围内，表达质量 0.50 ≤ 0.69 合规。

**对照 general 阈值（min_overall_score = 0.80, max_high_issues = 0, max_medium_issues = 3）**：本轮仍 **未达输出标准**。

---

## 二、模块完整性检查

```
sections/
├── content.md          ✓ 完整（12859 字节，66 行）
├── full_review.md      ✗ 0 字节
├── rationale.md        ✓ 完整（18201 字节，81 行）
├── references.md       ✓ 已建立（5875 字节，40 条目）← R1 P0 已修
└── scheme.md           ✓ 完整（18778 字节，108 行）
```

模块完整性较 R1 显著改善：references.md 从 0 字节 → 5875 字节。**full_review.md 仍为 0 字节**——但本轮聚焦章节为 rationale，不影响本轮评审。

---

## 三、执行清单对照（逐条报告通过/不通过）

| # | 检查项 | 状态 | 证据 |
|---|--------|------|------|
| 1 | 申请书包含标准模块（立项依据+研究内容+研究方案） | ✓ 通过 | rationale.md/content.md/scheme.md 均存在 |
| 2 | 读取申请书聚焦章节 | ✓ 通过 | rationale.md 81 行完整读取 |
| 3 | 读取 nsfc-standards.json | ✓ 通过 | 已读完整 36KB |
| 4 | rationale.md 含五层递进（大背景→领域脉络→核心问题→国内现状→本项目定位） | ✓ 通过 | §1.1-§1.5 一一对应 |
| 5 | 文献引用为嵌入式论证（'某人[N]在期刊上报道了X'） | ✓ 通过 | rationale §1.2 第一阶段典型（L19"Lin 等人 [13] 的自旋分辨 ARPES 在室温 RuO₂ 中直接观测到"） |
| 6 | 末尾自然引出科学问题（不用'为回答...问题'口号） | ✓ 通过 | rationale §1.5 末尾引出"本项目的核心科学问题是：强激光能否..." |
| 7 | 正文 [N] 引用 10-20 次（v6.9.9 校准后范本标杆） | ⚠ 部分达标 | rationale.md 41 次（密集），但 scheme.md 0 次（缺失），content.md 仅 3 次（不足） |
| 8 | 参考文献 30-40 篇 | ✓ 通过 | references.md 40 条 |
| 9 | 总字数 5000-8000 字 | ✓ 通过 | rationale.md 6861 字（达标） |
| 10 | 每条研究目标至少含 1 个可检验量化指标 | ✓ 通过 | content.md §2.5 三项目标均含量化指标（10% 不确定性、≥80% 验证率、≥3σ 区分度） |
| 11 | 同一指标在不同章节数值口径一致 | ✓ 通过 | 16-40 meV/unitcell（rationale L31/L57, content L15, scheme L11/L17 一致）；0.1-1.0 MV/cm（rationale L31, content §2.5, scheme L11/L17/L37 一致） |
| 12 | 理论框架注明适用条件与失效边界 | ✓ 通过 | scheme §3.5 难点一/二明确"ALDA 在 >10% 修正区间"与"Rashba 敏感度 > 50% 区间"失效条件 |
| 13 | "首次/尚未见"有文献或检索范围支撑 | ✗ 不通过 | rationale L67/L79/L81 共 4 处"首次/尚未见"声明，但 references.md 现已含 [11] Sheng 2024 + [29] 本课题组 "in preparation" + [17] Ghorashi-Rappe 2024 等，**部分声明可能被这些 references 推翻**（详见 issue #R2-3） |
| 14 | 方案→指标实现路径 | ✓ 通过 | scheme §3.2-§3.4 各方案均给出"方案→原理→指标"链 |
| 15 | 范本叙述式行文（无条目式罗列） | ⚠ 部分达标 | rationale.md 大段连贯叙述达标，但 §1.5"研究内容将重点解决三个关键科学问题"后接 3 段 (1)/(2)/(3) 编号列举属**范本正常现象**（content_example 也用 "(1)(2)" 编号），不视为 bullet list 违规 |
| 16 | 避免 "A 做了 X，B 做了 Y，C 做了 Z" 文献堆砌 | ✓ 通过 | rationale §1.2 三阶段均按"主题→代表性体系→机制"叙事，未出现"A 做了 X [1], B 做了 Y [2]" 式罗列 |
| 17 | 研究内容围绕核心问题组织（非平行堆砌） | ✓ 通过 | content §2.1 总述段明确"驱动→读出→分离"逻辑链，§2.2-§2.4 三个分方向递进 |
| 18 | 研究方案说明"为什么选这个方法" | ✓ 通过 | scheme §3.2 "选择 TDDFT 而非纯紧束缚的理由在于..."；§3.3 "选择磁点群分析而非直接数值求解的原因在于..." |
| 19 | 特色与创新四步闭环（现有局限→方案→量化优势→定位收束） | ✓ 通过 | scheme §3.7 三个创新点均含"现有局限→本项目方案→量化优势"（定位收束略有弱化） |
| 20 | 段间过渡形成逻辑递进（不仅靠关联词） | ✓ 通过 | §1.1→§1.2 "MnPS₃ 给出器件化路径→二维实现作为下一阶段"；§1.3→§1.4 "现有局限→国内现状"逻辑递进 |
| 21 | 避免空洞概括句（"具有决定性意义""迈向新的高度"） | ✓ 通过 | rationale.md "具有决定性意义" 0 次，"迈向新的高度" 0 次 |
| 22 | 单句不超过 120 字 | ⚠ 部分达标 | 10 句超 120 字（占 9.5%），其中 L11 145 字、L25 144 字最严重；其余为多分句长句属范本正常范围 |
| 23 | 模板句式"为...提供...基础/支撑/途径" 全文 ≤ 15 次 | ✓ 通过 | rationale.md 7 次（4+3），content.md 1 次，scheme.md 2 次——全文联合约 10 次 ≤ 15 次阈值 |
| 24 | 模板主语"本项目拟/本项目将"不滥用 | ✓ 通过 | rationale.md "本项目将" 3 次（含 §1.5 L55/L77/L81）、"本项目拟" 0 次，content.md "本项目拟" 2 次（§2.1/§2.2），未滥用 |
| 25 | 冗余修饰词 ≤ 15 次 | ⚠ 边界 | "建立" 22 次（接近实现类动词上限 30）、"提供" 16 次、"系统" 7 次、"关键" 4 次——联合约 49 次 > 15 次阈值 |
| 26 | references.md 与正文编号对应 | ✗ 不通过 | references.md 已建 40 条（编号 [1]-[40] 完整），但 rationale.md 仍有 5+ 处编号-内容错配（详见 issue #R2-1）；scheme.md 0 处 [N] 引用与 references.md 完全断裂 |
| 27 | 参考文献格式统一 | ✓ 通过 | references.md 全部条目采用"作者. 标题. 期刊, 年, 卷: 页."格式，仅 [12][30][31][32][33][34][35] 等预印本以 "arXiv:XXXX.XXXXX" 形式标注 |

**执行清单统计**：27 项中 ✓ 21 项 / ⚠ 3 项 / ✗ 3 项

---

## 四、写作风格评估（程序化 AI 检测结果）

### 4.1 程序化 AI 模式检测（rationale.md）

| AI 模式 | 出现次数 | 阈值 | 状态 |
|---------|----------|------|------|
| `建立` | 22 | 实现类动词 ≤30 | ✓ 接近但未超 |
| `提供` | 16 | — | — |
| `实现` | 13 | — | — |
| `为...提供...基础` | 4 | ≤15 | ✓ |
| `为...提供...工具` | 3 | ≤15 | ✓ |
| `为...提供...基础+工具` 联合 | 7 | ≤15 | ✓ |
| `首次` | 4 | — | — |
| `尚未见` | 1 | — | — |
| `尚未` | 3 | — | — |
| `本项目将` | 3 | — | ✓ |
| `同时` | 3 | 关联词 | ⚠ 段间连续出现 2 次 |
| `然而` | 3 | 关联词 | ⚠ 段间连续出现 2 次 |
| `关键` | 4 | 冗余修饰 ≤15 | ✓ |
| `完整` | 3 | 冗余修饰 ≤15 | ✓ |
| `系统` | 7 | 冗余修饰 ≤15 | ✓ |
| `重要` | 3 | 冗余修饰 ≤15 | ✓ |
| `在此基础上` | 0 | — | ✓ |
| `基于此` | 0 | — | ✓ |
| `为回答...问题` | 0 | — | ✓ |
| `具有决定性意义` | 0 | — | ✓ |
| `迈向新的高度` | 0 | — | ✓ |

### 4.2 超长句检测

| 指标 | 数值 | 范本标杆 |
|------|------|----------|
| 总句数 | 105 | — |
| 超 80 字句 | 36 (34.3%) | 12-28%（超标） |
| 超 120 字句 | 10 (9.5%) | 应 ≤5% |

**最严重超长句（按行号定位）**：
- L11（145 字）："在更广义的二维材料体系中，铁电性驱动的二维范德华多铁方案 [10] 与滑移/莫尔铁电性 [11] 已在多层体系中普遍实现自旋劈裂的电学翻转。FeCuP₂S₆ 的研究证明..."（混合多个子论断，应拆分）
- L25（144 字）："圆偏振强场 Floquet 缀饰与谷手性选择定则的协同效应也得到理论预言：Yarmohammadi 等人 [21] 证明 Floquet 驱动结合 Rashba 耦合可在二维 d-wave 交磁体中诱导..."（应拆分）
- L23（138 字）："Ghorashi 与 Rappe [17] 的理论工作建立了'多光子吸收最低对称允许阶数→自旋劈裂角谐波'的定量关系..."（应拆分）

### 4.3 叙述式合规性评估

✓ **达标项**：
- rationale §1.1-§1.4 段落以"主题→机制→局限性"叙事，非文献堆砌
- §1.2 三阶段叙述以"研究范式转变"为主线，非平行罗列
- §1.5 "本项目定位"明确表达自己主张（双平台×双范式）
- 段间过渡以内容逻辑（"上述三个阶段的进展虽然建立了交变磁性的完整研究框架，但在二维超快操控与测量方向仍存在三个根本性瓶颈"）衔接，不仅靠关联词

⚠ **部分违规项**：
- `首次` 4 次 + 4 处"尚未见/尚未" 声明密度偏高，且**部分声明失锚**（references.md 已含相关工作）
- `建立`/`提供`/`实现` 等动词类 51 次联合，仍存在"模板句式"风险（虽未超 30 次阈值）

✗ **违规项**：
- rationale §1.5 L65-77 三段 (1)/(2)/(3) 编号列举属轻度模板化（**范本也用此格式，故仅 [medium] issue**）

**总体评估**：rationale.md 叙述式行文基本合规，**未触发 expression ≤0.6 的红线**（AI 模式密度未超 15 次"为...提供..."联合阈值）。但 `建立`/`提供` 类动词密度（51 次）与超 120 字句（10 个 9.5%）已构成**写作风格仍待优化**的标记。

---

## 五、锚点对比（申请书原文 vs 范本锚点）

### 5.1 锚点 1：rationale §1.1 开篇段（大背景）

**申请书原文（rationale L5）**：
> "自旋电子学的核心追求之一，是在无杂散场的条件下实现高速、高密度、低功耗的磁信息操控。传统铁磁材料受限于杂散场与超快磁化进动，难以满足下一代自旋器件的抗疲劳与高频需求。反铁磁体天然无净磁化，其自旋动力学上限可达 THz 乃至亚-THz 频段，被视为实现高频自旋操控的首选载体 [1,2]。然而，常规反铁磁体的自旋劈裂在动量空间呈均匀分布，器件可设计性受限。"

**范本锚点（rationale_example）**：
> "高次谐波产生是飞秒激光与物质相互作用的高阶非线性、非微扰现象。基于高次谐波光谱的超快探测技术使得在飞秒甚至阿秒尺度上实时探测物质中电子及原子核的微观动力学过程成为可能。人们利用原子、分子气体高次谐波进行了大量气相原子分子的超快探测和控制研究[1-8]，包括原子价电子运动的阿秒操控、分子核运动的实时观测等。近年来，人们在固体材料中也普遍观测到了高次谐波产生现象。2011年，Ghimire等人[9]使用中红外激光驱动ZnO晶体，观测到了非微扰高次谐波产生。"

**对比维度**：

| 维度 | 申请书 | 范本 | 差距 |
|------|--------|------|------|
| 语体（开篇） | 抽象领域意义开篇（"核心追求之一"） | 具体物理现象开篇（"高次谐波产生是飞秒激光与物质相互作用的高阶非线性、非微扰现象"） | **范本更具体**，申请书更宏观口号化 |
| 论证密度 | 4 句话建立"传统铁磁→反铁磁→交变磁性"三级跳 | 5 句话逐步从气相→固体→具体材料（ZnO）三级收窄 | **范本有具体材料锚点**，申请书仅停留在反铁磁体通论层面 |
| 数据驱动 | THz 频段（具体） | 阿秒尺度（具体） | 持平 |
| 引用嵌入 | "首选载体 [1,2]"（嵌入式） | "人们利用...研究[1-8]"（嵌入式） | 持平，**两者均合规** |
| 段落目的 | 建立"自旋-能谷多功能调控"动机 | 建立"HHG 超快探测能力"动机 | 平行对应 |

**差距定位**：申请书 §1.1 开篇**停留在"反铁磁体通论"层面未给出具体材料锚点**，而范本以 ZnO 这类具体材料作为第一层收窄。**申请书应在 §1.1 第三句或第四句插入具体材料（如 MnPS₃ 的 Néel 78 K 实验测量）作为第一层收窄**，但该具体材料出现在 §1.1 第 7 句（L9），距离开篇 4 句——收窄节奏较范本慢。

### 5.2 锚点 2：rationale §1.5 末尾"科学问题"引出段

**申请书原文（rationale L65）**：
> "本项目的核心科学问题是：强激光能否在 fs-ps 时域通过相干激发层间滑移模式与 Floquet 缀饰，实现对交变磁自旋-能谷态的超快切换——以及该过程携带何种可由 HHG 光谱指纹反演的超快动力学信息？"

**范本锚点（rationale_anchor 描述）**：
> "立项依据范本特征：以领域意义开篇，用'某人等人[N]在期刊上报道了X'式嵌入式引用，逐步收窄到核心挑战。每段150-300字，段间以内容逻辑衔接（非关联词）。末尾自然引出科学问题，**不使用'为回答...问题'式口号**。"

**对比维度**：

| 维度 | 申请书 | 范本 | 差距 |
|------|--------|------|------|
| 句式 | "本项目的核心科学问题是：X？——以及 Y？"（问题式收束） | "末尾自然引出科学问题"（嵌入式收束，无显式"科学问题是" 套语） | **范本无套语**，申请书有轻微"本项目的核心科学问题是：" 套语 |
| 物理内容 | 含具体参数（fs-ps、Floquet、HHG 指纹） | — | 申请书具体性强 |
| 收束功能 | 末尾自然引出 | 末尾自然引出 | 持平 |

**差距定位**：申请书用了"本项目的核心科学问题是："套语（虽未用"为回答...问题" 但仍属轻微模板化），**建议改为**："因此，强激光在 fs-ps 时域通过相干激发层间滑移模式与 Floquet 缀饰实现交变磁自旋-能谷态的超快切换——以及该过程携带的 HHG 光谱指纹反演——成为本项目要回答的核心物理问题。"（去掉"本项目的核心科学问题是："套语）

### 5.3 锚点 3：rationale §1.3 核心问题段

**申请书原文（rationale L31）**：
> "**瓶颈一：调控手段停留在准静态频段。** 现有二维交变磁体的自旋劈裂调控主要依赖机械滑移 [11]、热退火 [8] 或静电压缩 [16]，响应时间受限于 MHz 量级，与 THz 自旋动力学的时间窗口失配。实现 fs-ps 时域的超快切换，需要相干驱动层间滑移模式（层间声子）而非依赖热激活或静电力。NiCl₂、VS₂、CrSe₂ 等多层体系的层间滑移势垒为 16–40 meV/unitcell [11]，对应剪切声子频率在 THz 频段 [10]，与 THz 脉冲驱动场形成共振条件——这在原理上为相干驱动提供了可行性。然而，强激光场能否通过光应力或位移电流机制直接驱动层间滑移、在亚 ps 内完成自旋-能谷态切换，既无理论方案，更无实验验证。这是超快自旋-能谷器件面临的首要挑战。"

**范本锚点（content_anchor 描述）**：
> "研究内容范本特征：总述段（问题+路线+机制+产出）后接2-3个分方向，每方向有自解释标题。研究目标每条含1个可检验量化指标。关键科学问题与研究内容紧密对应，不是泛泛列举。"

**对比维度**：

| 维度 | 申请书 | 范本 | 差距 |
|------|--------|------|------|
| 段落结构 | **瓶颈一/二/三** 三个加粗子标题 + 各段论证 | 无显式子标题，渐进收窄 | 申请书**子标题化**偏离范本 |
| 论证密度 | 每段 100-200 字，密集数据（16-40 meV、138 meV、370 meV、0.93 eV、1.4 eV） | 范本段落密度相仿 | 持平，**申请书数据驱动优秀** |
| 文献嵌入 | 嵌入式引用（[11]/[8]/[16]/[10]） | — | 持平 |
| 与 content.md 对应 | §1.3 三瓶颈 ↔ §2.2-§2.4 三研究内容 强对应 | 范本要求"关键科学问题与研究内容紧密对应" | ✓ 达标 |
| "瓶颈"叙述式 | "瓶颈一" 三个加粗子标题 | 范本无加粗子标题 | **申请书偏模板化**（虽 content_example 也用"(1)(2)"编号但未用"瓶颈一/二/三"加粗） |

**差距定位**：rationale §1.3 用"瓶颈一/二/三" 加粗子标题是**轻度模板化**，虽然范本 content_example 也用"(1)(2)" 编号列举，但**范本未用"瓶颈N"加粗子标题**。建议改为流畅段落"现有二维交变磁体的研究存在三个根本性瓶颈：调控手段停留在准静态频段；HHG 谱学指纹尚未系统建立；三元耦合时域不可分离。" 然后接三个连续段落逐步论证。

### 5.4 锚点对比总结

| 维度 | 申请书现状 | 范本标杆 | 差距 |
|------|------------|----------|------|
| 语体 | 抽象动机 + 具体材料收窄 | 抽象动机 + 立即具体材料 | 范本更紧凑 |
| 论证密度 | 段均 150-300 字，含大量具体数据 | 段均 150-300 字，数据驱动 | 持平 |
| 数据驱动 | 优秀（多个 eV/meV/THz/MV/cm 数值） | 优秀 | 持平 |
| 引用嵌入 | 嵌入式（'某某[N]'） | 嵌入式（'某某[N]'） | 持平 |
| 段落目的 | 围绕核心问题逐步收窄 | 同 | 持平 |
| 套语密度 | 轻微（"本项目的核心科学问题是"、"瓶颈一"） | 极低 | 申请书略高 |

**锚点对比结论：基本接近**（范本叙述式特征 90% 达标，开篇收窄节奏略慢、轻度子标题化模板化、轻微套语）

---

## 六、跨章节一致性审查

### 6.1 关键指标跨章节口径一致性

| 指标 | rationale | content | scheme | 一致？ |
|------|-----------|---------|--------|--------|
| 16-40 meV/unitcell（层间滑移势垒） | L31/L57 | L15 | L11/L17 | ✓ 一致 |
| 0.1-1.0 MV/cm（THz 驱动场强） | L31 | §2.5 目标一 | L11/L17/L37/L65 | ✓ 一致 |
| 0.5-3.0 THz（Floquet 驱动频率） | — | — | L43 | ⚠ rationale/content 未声明，scheme 独有 |
| fs-ps 时标（切换时标） | L31/L65 | §2.5/§2.6 | L17/L65 | ✓ 一致 |
| 138 meV（Fe₂CoGaTe₂ i-wave 劈裂） | L21 | — | — | ⚠ 仅 rationale 出现，content/scheme 未引用此数据 |
| 1.4 eV（RuO₂ 自旋劈裂） | L19 | — | — | ⚠ 仅 rationale 出现 |
| i-wave HHG 指纹 5 个量 | — | §2.3/L25/§2.5 | §3.3/L25/L31 | ✓ 一致 |
| D_sep ≥ 0.80（时域分离度） | — | §2.5/§2.6 | §3.4/L43/L87 | ✓ 一致 |
| 增强倍数 ≥ 5 倍（Floquet） | — | §2.5/§2.6 | §3.4/L43/L87 | ✓ 一致 |

**结论**：核心指标跨章节口径基本一致；**Fe₂CoGaTe₂ 138 meV、RuO₂ 1.4 eV、MnTe 370 meV 等支撑性数据仅出现在 rationale**，未在 content/scheme 复述——这是合理的（content/scheme 应聚焦研究内容而非数据回顾）。

### 6.2 团队-引用对应错配（R1 P0 残存）

| 申请书原文 | 主张的团队/工作 | references.md 编号实际绑定 | 是否匹配 |
|------------|------------------|----------------------------|----------|
| rationale L41: "华中科技大学团队在滑移铁电与交变磁性结合方面做出了系统性理论贡献 [11]" | 华中科技大学（理论） | [11] Sheng et al. npj Comput Mater 2024, 10: 215（堆叠势垒 DFT） | **✗ 不匹配** |
| rationale L41: "上海大学与 TU Darmstadt 合作... [10]" | 上海大学-达姆施塔特合作（FEAFM） | [10] Zhang et al. PRL 2024, 133: 126801（FeCuP₂S₆ 单团队） | **✗ 不匹配** |
| rationale L45: "上海交通大学团队...在 RuO₂ 中观测到...自旋劈裂与 d-wave 自旋织构 [13]" | 上海交大（ARPES） | [13] Gonzalez-Hernandez et al. PRL 2024, 132: 096602（电气控制 spin splitting） | **✗ 不匹配**——rationale L19 同段把 [13] 绑定 "Lin 等人 RuO₂ 自旋分辨 ARPES"，但 references.md [13] 现为 Gonzalez-Hernandez 而非 Lin |
| rationale L19: "Lin 等人 [13] 的自旋分辨 ARPES" | Lin 等 RuO₂ ARPES | [13] Gonzalez-Hernandez et al. PRL 2024 | **✗ 不匹配**——Lin 等人应为 [5] Lin et al. Nature 2023, 614: 455-460 |
| rationale L21: "Ruiz 等人 [16] 在 Fe₂CoGaTe₂" | Ruiz 等 Fe₂CoGaTe₂ i-wave | [16] Lee et al. CoNb₄Se₈ Nat Mater 2024 | **✗ 不匹配**——Ruiz 应为 [17] Ruiz-Tijerina PRL 2025, 134: 026603 |
| rationale L25: "Yarmohammadi 等人 [21] 证明 Floquet 驱动结合 Rashba 耦合可在二维 d-wave 交磁体中诱导非平庸的各向异性磁阻与反常霍尔效应" | Yarmohammadi 各向异性磁阻 | [21] Rajpurohit et al. PRL 2025, 134: 056601（fs 切换） | **✗ 不匹配**——Yarmohammadi 应为 [22] Yarmohammadi et al. PRL 2025, 134: 096901 |
| rationale L31: "NiCl₂、VS₂、CrSe₂ 等多层体系的层间滑移势垒为 16–40 meV/unitcell [11]，对应剪切声子频率在 THz 频段 [10]" | 16-40 meV 势垒 + THz 频段 | [11] Sheng 堆叠势垒 ✓ / [10] Zhang FeCuP₂S₆ PRL | **✗ [10] 错配**——"THz 频段" 论断与 FeCuP₂S₆ 工作无关，应为单独的"剪切声子频率" 文献 |
| content L43: "Yarmohammadi 等人的理论工作 [21] 证明，Floquet 驱动结合 Rashba 耦合" | Yarmohammadi Floquet-Rashba | [21] Rajpurohit | **✗ 不匹配**——同 rationale L25 |
| content L27: "Ghorashi 与 Rappe 的理论工作 [17] 已建立'自旋劈裂对称性→角谐波最低允许阶数'的定量关系" | Ghorashi-Rappe HHG 选择定则 | [17] Ruiz-Tijerina i-wave Fe₂CoGaTe₂ | **✗ 不匹配**——Ghorashi-Rappe 应为 [18] Ghorashi-Rappe PRL 2024, 133: 116801 |
| content L31: "Lin 等人的 TDDFT 模拟 [2505.09237] 已证明滑移铁电双层中产生的圆偏振高次谐波其螺旋度能够直接映射层锁定的 Berry 曲率分布" | Lin 等 HHG-Berry | [2505.09237] 入库为 [33] Lin et al. arXiv:2505.09237 | ✓ 一致 |

**统计**：rationale + content 共 **9 处**团队-编号错配，scheme.md 0 处 [N] 引用（与编号体系完全断裂）。

### 6.3 引用密度一致性

| 章节 | [N] 引用次数 | 独立编号数 | 章节字数 | 密度（次/千字） |
|------|--------------|------------|----------|-----------------|
| rationale.md | 41 | 19 | 6861 | 6.0 |
| content.md | 3 | 3 | ~11000 | 0.27 |
| scheme.md | 0 | 0 | ~17000 | 0 |
| 联合 | 44 | 19 | ~35000 | 1.3 |

**异常**：scheme.md 完全无 [N] 引用——但 §3.2-§3.7 大量引用了 "文献 19"/"文献 21"/"文献 2403.06531"/"文献 29"/"文献 2504.18845" 等 6 处裸引——**这是 scheme.md 的引用格式与 rationale.md 不统一**（违反 section_standards.full_review "参考文献编号连续、格式统一、正文有[N]角标对应"）。

### 6.4 关键术语一致性

| 术语 | rationale | content | scheme | 一致？ |
|------|-----------|---------|--------|--------|
| i-wave | 11 | 11 | 17 | ✓ |
| d-wave | 7 | 4 | 4 | ✓ |
| g-wave | 5 | 3 | 4 | ✓ |
| Rashba | 11 | 12 | 18 | ✓ |
| Berry 曲率 | 4 | 5 | 5 | ✓ |
| Floquet | 10 | 9 | 10 | ✓ |
| HHG | 29 | 21 | 30 | ✓ |
| MnPS₃ | 8 | 4 | 3 | ✓（平台二） |
| WS₂ | 2 | 4 | 3 | ✓（平台二） |
| NiCl₂/VS₂/CrSe₂ | 2/2/3 | 2/2/2 | 4/4/4 | ✓（平台一） |
| TDDFT | 1 | 3 | 13 | ✓（scheme 集中） |

**结论**：术语一致性良好，无漂移。

---

## 七、历史 P0 问题逐条核对（R1 遗留问题清单）

### 7.1 R1 P0 #1: references.md 0 字节

**状态：✅ 已解决**

**证据**：`ls -la` 显示 references.md 5875 字节，含 40 条目（编号 [1]-[40] 连续）。

---

### 7.2 R1 P0 #2: 编号跳号 [5][6][7][22]

**状态：✅ 已解决**

**证据**：references.md 编号 [1]-[40] 连续无跳号。rationale.md 现仅引用 [8]-[29] 区间内的 19 个编号（[1]-[7]、[9]、[22]、[28] 不在 rationale 正文），但 references.md 仍完整建立这些编号作为预印本/备用文献——这是合理设计。

---

### 7.3 R1 P0 #3: 编号 [11] 一号多用绑定 5 体系

**状态：⚠ 部分解决**

**证据**：
- references.md 现已明确 [11] = Sheng et al. npj Comput Mater 2024（堆叠势垒 DFT）**单一文献** ✓
- 但 rationale.md 仍以单一 [11] 绑定 5 个不同论断：
  - L11: "VSe₂ 通过 Co 掺杂可实现铁磁-反铁磁基态调控 [16]" + "CrSe₂ 在反平行堆叠下呈现 SST-4B 型对称性破缺自旋劈裂 [11]"（**CrSe₂ 应绑 [15]，非 [11]**）
  - L13: "滑移/莫尔铁电性 [11] 已在多层体系中普遍实现自旋劈裂的电学翻转" + "Sheng 等人 [11] 的系统性理论工作..."（**[11] 不能同时支撑两条独立论断**）
  - L31: "NiCl₂、VS₂、CrSe₂ 等多层体系的层间滑移势垒为 16–40 meV/unitcell [11]"（与 L13 同义重复，但物理量相同可接受）
  - L57: "滑移二维方晶格（耦合准交变磁候选）[11,30]"（[11] 此处应是平台一整体综述，[30] 是 arXiv:2408.11234 Hu 等耦合准交变磁候选——但 [30] 已支持该论断，[11] 可移除或保留作为堆叠势垒背景）

**结论**：references.md 修复了"同一 [11] 绑多篇"的问题，但 rationale.md 同一 [11] 在不同句绑不同物理机制（如 L11 CrSe₂ 绑 [11] 与 Sheng 堆叠势垒 DFT 不对应），属于**正文未配套修复 references.md**——属于 [high] rigor issue 残留。

---

### 7.4 R1 P0 #4: 编号 [16] 一号多用绑定 4 体系

**状态：⚠ 部分解决但出现新错误**

**证据**：
- references.md [16] 现已明确为 Lee et al. CoNb₄Se₈（层状交变磁体）**单一文献** ✓
- 但 rationale.md L21 "Ruiz 等人 [16] 在 Fe₂CoGaTe₂"——[16] 现指 CoNb₄Se₈ 而非 Ruiz/Fe₂CoGaTe₂，**应改为 [17]**（[17] 现为 Ruiz-Tijerina et al. PRL 2025, 134: 026603——i-wave Fe₂CoGaTe₂）✓
- rationale.md L11 "VSe₂ 通过 Co 掺杂可实现铁磁-反铁磁基态调控 [16]"——但 [16] 现指 CoNb₄Se₈ 而非 VSe₂ Co 掺杂，**应改为 [14]**（[14] 现为 Liu et al. Cobalt-doping VSe₂ Nano Lett 2024）✓
- rationale.md L11 "CrSe₂ 在反平行堆叠下呈现 SST-4B 型对称性破缺自旋劈裂 [11]"——但 [11] 现为 Sheng 堆叠势垒而非 CrSe₂，**应改为 [15]**（[15] 现为 Chen et al. CrSe₂ PRB 2024）✓
- rationale.md L19 "CoNb₄Se₈ 的层状交变磁体在 150 K 以下出现电荷-自旋密度波并展现超快光开关特性 [16]"——✓ 与 [16] 绑定一致（修复成功）

**结论**：references.md [16] 修正后**产生了新的正文本编号错位**（rationale.md L11/L21 未配套修正），仍属 [high] rigor issue。

---

### 7.5 R1 P0 #5: 编号 [20] 与 [21] 论断边界模糊

**状态：⚠ 部分解决但 rationale/content 未配套修复**

**证据**：
- references.md [20] 现为 García-Gaitán et al. NiO THz-HHG（Nat Photon 2024）单一文献
- references.md [21] 现为 Rajpurohit et al. fs 切换（PRL 2025, 134: 056601）
- references.md [22] 现为 Yarmohammadi et al. 各向异性磁阻（PRL 2025, 134: 096901）
- references.md [23] 现为 Yarmohammadi et al. 谷极化 Floquet（PRB 2025, 111: 184401）

但 rationale.md L25 / content.md L43 仍把 Yarmohammadi Floquet-Rashba 各向异性磁阻绑到 [21]——**[21] 现为 Rajpurohit fs 切换，与 Yarmohammadi 不匹配**——**应改为 [22]**（Yarmohammadi 各向异性磁阻）。

**结论**：references.md [20]/[21]/[22] 已分离，**但 rationale.md L25 + content.md L43 未配套修正**，仍属 [high] rigor issue。

---

### 7.6 R1 P0 #6: content.md 5 处 arXiv 预印本裸引

**状态：⚠ 部分解决**

**证据**：
- references.md 已将 5 个 arXiv 编号入库为 [31]-[35] ✓
- references.md 已将 scheme "文献 2403.06531" 入库为 [36]（Wang et al. PRL 2024, 133: 246901）✓
- 但 **content.md 仍有 5 处裸 arXiv 号**（L15 [2506.18439]、L19 [2503.21782]×2、L29 [2504.18845]、L31 [2505.09237]、L39 [2507.04513]×2）
- **scheme.md 仍有 3 处裸引/裸号**（L19 "文献 2403.06531"、L29 "Morimoto 等人 2504.18845"、L63 "文献 2403.06531"、L47 "Yarmohammadi 等人（文献 21）"）

**结论**：references.md 入库 ✓ 但**正文未将裸号改为 [N] 格式**，引用格式仍三制混用——属 [high] rigor issue。

---

### 7.7 R1 P0 #7: §1.4 L39 华中科技大学团队 [11] 失锚

**状态：⚠ 仍残存（且 [11] 错配未改）**

**证据**：rationale.md L41（原 L39）原文："华中科技大学团队在滑移铁电与交变磁性结合方面做出了系统性理论贡献 [11]"——但 references.md [11] 现为 Sheng et al. npj Comput Mater 2024（堆叠势垒 DFT），并非"华中科技大学系统性理论贡献"工作。该团队工作应单独引用或归入 [12] Wu et al. Prevalence of altermagnetic spin splitting in 2D van der Waals multilayers（arXiv:2406.04832——可能为华中科技大学工作）。

**结论**：rationale.md L41 团队-编号错配**完全未修复**，[11] 失锚问题**仍残存**——属 [critical] rigor issue。

---

### 7.8 R1 P1 #5: 一号多用导致新颖性表述失锚

**状态：⚠ 仍残存**

**证据**：rationale.md L67 "据目前检索（检索范围：Web of Science、arXiv、APS/IOP 期刊数据库，截止 2026-08），尚未见将层间滑移自由度引入强场超快调控的系统工作"——但 references.md 现已含：
- [11] Sheng 2024 npj Comput Mater（堆叠势垒 DFT，含层间滑移）
- [36] Wang et al. 2024 PRL（双层 h-BN THz 极化翻转——含层间滑移超快驱动）
- [31] Wang et al. 2026 arXiv 2604.27342（双层 h-BN 滑移铁电开关深度学习分子动力学——含层间滑移超快）

**这些 references 中的 [31] [36] 已涵盖"层间滑移超快驱动测量"——则 rationale L67 "尚未见"声明**部分失锚**。

**结论**：5 处"尚未见/首次"声明仍需在 references.md 建立后逐条重新核查——属 [high] rigor issue 残存。

---

## 八、本轮新发现的问题

### 8.1 本轮聚焦章节（rationale.md）新增问题

#### [critical] rigor — rationale.md L41 "华中科技大学团队 [11]" 团队-编号错配（R1 P0 残存未修）
- **位置**：rationale.md L41
- **问题**："华中科技大学团队在滑移铁电与交变磁性结合方面做出了系统性理论贡献 [11]"——但 references.md [11] = Sheng et al. npj Comput Mater 2024, 10: 215（堆叠势垒 DFT 单篇），与"华中科技大学团队系统性理论贡献"不匹配
- **违反**：section_standards.references（编号-内容对应）；indicator_red_lines.novelty_claim_cautious；R1 报告 #7 直接点名的 P0 残存问题
- **建议**：
  1. 在 references.md 中添加华中科技大学团队对应文献条目（推测为 [12] Wu et al. arXiv:2406.04832 "Prevalence of altermagnetic spin splitting in 2D van der Waals multilayers"——如核实属华中科技大学则直接绑定；或新增独立条目 [41]）
  2. rationale.md L41 [11] 改为新编号
  3. 同段 "上海大学与 TU Darmstadt 合作 [10]" 同样错配（[10] 现为 Zhang et al. FeCuP₂S₆ PRL）——需在 references.md 核实上海大学-达姆施塔特工作并独立编号
- **action**：rewrite + research（核实华中科技大学与上海大学-达姆施塔特对应文献）

#### [critical] rigor — rationale.md L19/L45 [13] 团队-编号错配（Lin 等 vs Gonzalez-Hernandez）
- **位置**：rationale.md L19 + L45
- **问题**：
  - L19: "Lin 等人 [13] 的自旋分辨 ARPES 在室温 RuO₂ 中直接观测到..."——Lin 等人 RuO₂ ARPES 应为 [5] Lin et al. Nature 2023, 614: 455-460，但 [13] 现为 Gonzalez-Hernandez et al. PRL 2024, 132: 096602（电气控制 spin splitting）
  - L45: "上海交通大学团队...在 RuO₂ 中观测到...自旋劈裂与 d-wave 自旋织构 [13]"——上海交大 RuO₂ ARPES 也应为 [5]，但 [13] 现为 Gonzalez-Hernandez
- **违反**：section_standards.references；R1 已点出"§1.4 多个团队-引用错配"风险
- **建议**：
  1. rationale.md L19 [13] 改为 [5]
  2. rationale.md L45 [13] 改为 [5]，并在文字中明确"上海交通大学林志东团队"以与 [5] 对应
- **action**：rewrite

#### [critical] rigor — rationale.md L21 [16] 错配（Ruiz/Fe₂CoGaTe₂ 应为 [17]）
- **位置**：rationale.md L21
- **问题**："Ruiz 等人 [16] 在金属型范德华反铁磁体 Fe₂CoGaTe₂ 中证明..."——Ruiz 等人 Fe₂CoGaTe₂ 应为 [17] Ruiz-Tijerina et al. PRL 2025, 134: 026603（i-wave Fe₂CoGaTe₂），但 [16] 现为 Lee et al. CoNb₄Se₈ Nat Mater 2024
- **违反**：section_standards.references；indicator_red_lines.citation_system
- **建议**：rationale.md L21 [16] 改为 [17]
- **action**：rewrite

#### [critical] rigor — rationale.md L25 + content.md L43 [21] 错配（Yarmohammadi 应为 [22]）
- **位置**：rationale.md L25 + content.md L43
- **问题**：
  - rationale L25: "Yarmohammadi 等人 [21] 证明 Floquet 驱动结合 Rashba 耦合可在二维 d-wave 交磁体中诱导非平庸的各向异性磁阻与反常霍尔效应"——Yarmohammadi 应为 [22] PRL 2025, 134: 096901（各向异性磁阻），但 [21] 现为 Rajpurohit fs 切换 PRL 2025, 134: 056601
  - content L43: "Yarmohammadi 等人的理论工作 [21] 证明，Floquet 驱动结合 Rashba 耦合..."——同样错配
- **违反**：section_standards.references；indicator_red_lines.citation_system
- **建议**：rationale L25 + content L43 [21] 改为 [22]
- **action**：rewrite

#### [high] rigor — content.md L27 [17] 错配（Ghorashi-Rappe 应为 [18]）
- **位置**：content.md L27
- **问题**："Ghorashi 与 Rappe 的理论工作 [17] 已建立'自旋劈裂对称性→角谐波最低允许阶数'的定量关系"——Ghorashi-Rappe HHG 选择定则应为 [18] Ghorashi et al. PRL 2024, 133: 116801，但 [17] 现为 Ruiz-Tijerina i-wave Fe₂CoGaTe₂
- **违反**：section_standards.references；indicator_red_lines.citation_system
- **建议**：content.md L27 [17] 改为 [18]
- **action**：rewrite

#### [high] rigor — content.md L31 [17] 错配风险待核实
- **位置**：content.md L31 + rationale.md L23
- **问题**：
  - content L31: "Lin 等人的 TDDFT 模拟 [2505.09237]"——此处裸号 [2505.09237] 已入库为 [33]，✓ 一致（但未改用 [N] 格式）
  - rationale L23: "Ghorashi 与 Rappe [17] 的理论工作建立了..."——[17] 错配（应为 [18]），与 content L27 同问题
- **违反**：section_standards.references
- **建议**：rationale L23 [17] 改为 [18]；content L31 [2505.09237] 改为 [33]
- **action**：rewrite

#### [high] rigor — rationale.md L31 [10] 错配（THz 频段论断与 Zhang FeCuP₂S₆ 不对应）
- **位置**：rationale.md L31
- **问题**："NiCl₂、VS₂、CrSe₂ 等多层体系的层间滑移势垒为 16–40 meV/unitcell [11]，对应剪切声子频率在 THz 频段 [10]"——[11] Sheng 堆叠势垒 ✓ 对应；但 [10] Zhang FeCuP₂S₆ PRL 2024 与"剪切声子频率在 THz 频段"**无直接关联**（FeCuP₂S₆ 是铁电-反铁磁多铁工作，非层间剪切声子频率工作）
- **违反**：section_standards.references；R1 提到"§1.4 L39 华中科技大学团队 [11]" — L31 的 [10] 错配属同类型问题
- **建议**：
  1. rationale.md L31 [10] 移除，或独立引用剪切声子频率文献（如 scheme §3.2 L19 "文献 2403.06531"对应的 [36] Wang et al. PRL 2024）
  2. 如确实由 [10] 支撑，需在 references.md [10] 备注中说明"FeCuP₂S₆ 中反平行堆叠对应的层间声子频率"
- **action**：rewrite + verify

#### [high] rigor — scheme.md 6 处裸引/裸号与 [N] 体系完全断裂
- **位置**：scheme.md L19/L29/L47/L63 + 全章
- **问题**：scheme.md 全文 0 处 [N] 引用——所有引用以"文献 2403.06531"/"文献 19"/"文献 21"/"文献 29"/"文献 2504.18845"等裸引/裸号形式出现。**正文格式与 references.md 编号体系完全断裂**，违反 section_standards.full_review "参考文献编号连续、格式统一、正文有[N]角标对应"。
- **违反**：section_standards.references；writing_style_rules.citation_system
- **建议**：
  1. scheme.md 全文裸引改为 [N] 格式：
     - L19 "文献 2403.06531（Wang et al., 2024）" → [36]
     - L29 "Morimoto 等人 2504.18845" → [32]
     - L47 "Yarmohammadi 等人（文献 21）" → [22]（同时修正 [21]→[22] 错配）
     - L63 "文献 2403.06531" → [36]
     - L63 "文献 19" → [20]（García-Gaitán NiO THz-HHG）
     - L65 "文献 2403.06531" → [36]
     - L65 "文献 19" → [20]
     - L65 "文献 29" → [29]
- **action**：rewrite

#### [high] rigor — content.md 5 处 arXiv 裸引未改为 [N] 格式（R1 P0 残存）
- **位置**：content.md L15/L19/L29/L31/L39
- **问题**：content.md 仍有 5 处裸 arXiv 号：
  - L15 [2506.18439] → 应为 [34]
  - L19 [2503.21782] ×2 → 应为 [31]
  - L29 [2504.18845] → 应为 [32]
  - L31 [2505.09237] → 应为 [33]
  - L39 [2507.04513] ×2 → 应为 [35]
- **违反**：section_standards.references；indicator_red_lines.citation_system
- **建议**：全文 arXiv 裸号改为 [N] 格式（已入库为 [31]-[35]）
- **action**：rewrite

#### [high] rigor — rationale.md L67/L79/L81 共 4 处"尚未见/首次"声明部分失锚
- **位置**：rationale.md L67/L79/L81
- **问题**：
  - L67 "据目前检索...尚未见将层间滑移自由度引入强场超快调控的系统工作"——但 references.md 现已含 [36] Wang et al. PRL 2024（双层 h-BN THz 极化翻转含层间滑移超快驱动）
  - L67 "利用 HHG 螺旋度/椭圆度指纹反演 i-wave 自旋劈裂对称性的理论框架尚未建立"——但 references.md 现已含 [17] Ruiz-Tijerina et al. PRL 2025（i-wave Fe₂CoGaTe₂ + 实验 HHG 预言）
  - L79 "将首次把层间滑移自由度作为独立动力学变量引入强场超快物理研究框架"——同上 [36] 残存问题
  - L81 "将首次建立 i-wave 自旋劈裂的定量 HHG 指纹对应表"——同上 [17] 残存问题
- **违反**：indicator_red_lines.novelty_claim_cautious
- **建议**：
  1. 在立项依据 §1.5 末添加"参考文献时效性说明"段落，明确"以下 4 处'尚未见/首次'声明基于检索范围 [具体范围] 截至 [核实日期]"
  2. 若 references.md 已包含相关工作（如 [36] [17]），则相应声明改为"在所考察的 [具体体系/参数空间] 中" 限定
  3. 在 references.md 添加"最近检索日志"附录，记录 4 处声明的核实过程
- **action**：research + verify

#### [medium] rigor — rationale.md §1.5 L65/L67/L77/L81 共 4 处"首次/尚未见"密度偏高
- **位置**：rationale.md §1.5
- **问题**：单章节出现 4 次"首次/尚未见"声明（密度约每 4-5 段一次），叠加上一轮 R1 已点名的失锚风险。**降低密度方式**：将"首次"声明合并为 1 段"本项目的核心创新定位"，避免散点式"首次"声明
- **违反**：anti_ai_patterns.quantitative_thresholds（虽未设"首次"上限，但密度过高易引起 reviewer 警觉）；writing_style_rules.forbidden "口号式表达"
- **建议**：rationale.md §1.5 L65/L67/L77/L81 的 4 次"首次/尚未见"合并为 §1.5 末一段"因此本项目的创新定位是：'据目前检索范围 [X] 截至 [日期]，本项目首次将层间滑移自由度作为独立动力学变量引入强场超快物理研究框架，并首次建立 i-wave 自旋劈裂的定量 HHG 指纹对应表'"
- **action**：rewrite

#### [medium] rigor — references.md [29] 本课题组 "in preparation" 预研基础不足
- **位置**：references.md L59 + rationale.md L49
- **问题**：references.md [29] = "Li M, Wang Q, Zhang J, et al. Our group's preliminary results on HHG selection rules in altermagnets. In preparation, 2025."——本课题组唯一的"预研基础" 仍是 in preparation 状态，**未发表**。面上项目评审要求"扎实预研基础"，1 篇 in preparation 预研基础**严重不足**
- **违反**：项目类型 general 评审标准 "扎实预研基础"；section_standards.references 时效性
- **建议**：
  1. 在 references.md 添加本课题组已发表的相关工作（建议 3-5 篇，包括交变磁 HHG 选择定则、强场 Floquet、固体 HHG 平台等）
  2. 如确实仅有 in preparation 状态，则在 §1.4 末增加"课题组已具备但不限于以下相关方向的实验平台积累：..."段落，将"预研基础"扩展为实验平台积累的描述
- **action**：research + rewrite

### 8.2 rationale.md 叙述式合规性新增问题

#### [medium] expression — rationale.md L11/L25/L23 三处 138-145 字超长句
- **位置**：rationale.md L11/L23/L25
- **问题**：3 句超 140 字，单句包含多个子论断且夹杂引用。范本标杆超 80 字句 12-28%，超 120 字句 ≤5%；申请书超 120 字句 9.5% 超标
- **违反**：writing_style_rules.anti_ai_patterns.remove "超长句：单句超过80字应拆分，超过120字属严重超长句"
- **建议**：
  - L11（145 字）拆为 2 句：第 1 句至"...自旋劈裂的电学翻转"；第 2 句从"FeCuP₂S₆ 的研究证明..."
  - L23（138 字）拆为 2 句：第 1 句至"...角谐波'的定量关系"；第 2 句从"d-wave 自旋劈裂在双光子过程中显现..."
  - L25（144 字）拆为 2 句：第 1 句至"...2:1——这是'全光学自旋劈裂开关'概念的理论证明"；第 2 句从"圆偏振强场 Floquet 缀饰..."
- **action**：rewrite

#### [medium] expression — rationale.md §1.3 "瓶颈一/二/三" 加粗子标题轻度模板化
- **位置**：rationale.md §1.3
- **问题**：用"瓶颈一：..."加粗子标题分割三段，属轻度模板化（范本未使用加粗子标题，而以流畅段落论证）
- **违反**：anti_ai_patterns.remove "僵硬平行结构：三个'如何'排比"（虽非完全相同，但模式类似）；范本 style_benchmark 不要求加粗子标题
- **建议**：去掉"瓶颈一/二/三"加粗子标题，改为流畅段落"现有二维交变磁体的研究存在三个根本性瓶颈：调控手段停留在准静态频段；HHG 谱学指纹尚未系统建立；三元耦合时域不可分离。" 后接三个连续段落逐步论证
- **action**：rewrite

#### [low] expression — rationale.md L65 "本项目的核心科学问题是：" 套语
- **位置**：rationale.md L65
- **问题**："本项目的核心科学问题是：强激光能否在 fs-ps 时域..."——轻微套语（范本无此套语）
- **违反**：anti_ai_patterns.remove "口号式开头：'为回答…问题'、'为实现…'"
- **建议**：改为"因此，强激光在 fs-ps 时域通过相干激发层间滑移模式与 Floquet 缀饰实现交变磁自旋-能谷态的超快切换——以及该过程携带的 HHG 光谱指纹反演——成为本项目要回答的核心物理问题。"（去掉"本项目的核心科学问题是："套语）
- **action**：rewrite

#### [low] expression — rationale.md `建立`/`提供`/`实现` 动词类联合 51 次偏高
- **位置**：rationale.md 全文
- **问题**：`建立` 22 次 + `提供` 16 次 + `实现` 13 次 = 51 次，虽单个未超 30 次阈值，但联合密度偏高
- **违反**：anti_ai_patterns.remove "动词堆砌：连续'建立…发展…实现…构建…'"
- **建议**：
  - 将部分"建立"改为具体动词（"构造"-"推导"-"证明"-"发展"）
  - 将部分"提供"改为"支撑"/"保障"/"对接"（与 anti_ai_patterns.replace_with 一致）
  - 将部分"实现"改为"完成"/"达到"/"满足"
- **action**：rewrite

---

## 九、问题清单汇总（按严重度）

| # | severity | issue_type | 标题 | 位置 | action |
|---|----------|-----------|------|------|--------|
| 1 | [critical] | rigor | rationale.md L41 华中科技大学团队 [11] 团队-编号错配 | rationale.md L41 | rewrite + research |
| 2 | [critical] | rigor | rationale.md L19/L45 [13] Lin/Shanghai Jiao Tong 团队-编号错配 | rationale.md L19/L45 | rewrite |
| 3 | [critical] | rigor | rationale.md L21 [16] Ruiz/Fe₂CoGaTe₂ 错配应为 [17] | rationale.md L21 | rewrite |
| 4 | [critical] | rigor | rationale.md L25 + content.md L43 [21] Yarmohammadi 错配应为 [22] | rationale.md L25, content.md L43 | rewrite |
| 5 | [critical] | rigor | content.md L27 [17] Ghorashi-Rappe 错配应为 [18] | content.md L27 | rewrite |
| 6 | [critical] | rigor | references.md [10]/[11]/[12]/[29] 与 rationale §1.4 团队对应需重新核实 | references.md | research + verify |
| 7 | [high] | rigor | content.md L27 + rationale.md L23 [17] Ghorashi-Rappe 错配应为 [18] | content.md L27, rationale.md L23 | rewrite |
| 8 | [high] | rigor | rationale.md L31 [10] "THz 频段" 错配 | rationale.md L31 | rewrite + verify |
| 9 | [high] | rigor | scheme.md 6 处裸引/裸号与 [N] 体系完全断裂 | scheme.md L19/L29/L47/L63 + 全章 | rewrite |
| 10 | [high] | rigor | content.md 5 处 arXiv 裸引未改为 [N] 格式（R1 P0 残存） | content.md L15/L19/L29/L31/L39 | rewrite |
| 11 | [high] | rigor | rationale.md L67/L79/L81 共 4 处"尚未见/首次"声明部分失锚 | rationale.md L67/L79/L81 | research + verify |
| 12 | [high] | rigor | references.md [11] 一号多用正文未配套修复（rationale L11/L13/L31/L57 同 [11] 绑 5 体系） | rationale.md L11/L13/L31/L57 | rewrite |
| 13 | [high] | rigor | references.md [16] 一号多用正文未配套修复（rationale L11 VSe₂/CrSe₂ + L21 Ruiz 错位） | rationale.md L11/L21 | rewrite |
| 14 | [medium] | rigor | rationale.md §1.5 4 处"首次/尚未见" 密度偏高 | rationale.md §1.5 | rewrite |
| 15 | [medium] | rigor | references.md [29] 本课题组 "in preparation" 预研基础不足 | references.md L59 | research + rewrite |
| 16 | [medium] | expression | rationale.md L11/L25/L23 三处 138-145 字超长句 | rationale.md L11/L23/L25 | rewrite |
| 17 | [medium] | expression | rationale.md §1.3 "瓶颈一/二/三" 加粗子标题轻度模板化 | rationale.md §1.3 | rewrite |
| 18 | [low] | expression | rationale.md L65 "本项目的核心科学问题是：" 套语 | rationale.md L65 | rewrite |
| 19 | [low] | expression | rationale.md `建立`/`提供`/`实现` 动词类联合 51 次偏高 | rationale.md 全文 | rewrite |

**问题统计**：critical 6 + high 8 + medium 4 + low 2 = **共 20 个问题**

---

## 十、对抗结论

### 10.1 历史 P0 问题修复状态

| R1 P0 问题 | 状态 | 备注 |
|-----------|------|------|
| references.md 0 字节 | ✅ 已解决 | 现 5875 字节，40 条目 |
| 编号跳号 [5][6][7][22] | ✅ 已解决 | references.md [1]-[40] 连续 |
| [11] 一号多用 5 体系 | ⚠ 部分解决 | references.md 修复但正文未配套，rationale L11/L13/L31/L57 仍以单一 [11] 绑多论断；新增团队-编号错配 |
| [16] 一号多用 4 体系 | ⚠ 部分解决但新错误 | references.md 修复但 rationale L11/L21 错位（VSe₂/CrSe₂/Ruiz 错绑） |
| [20]/[21] 边界模糊 | ⚠ 部分解决但新错误 | references.md [20][21][22] 分离但 rationale L25 + content L43 错绑 |
| 5 处 arXiv 裸引 | ⚠ 部分解决 | references.md 入库但正文未改用 [N] 格式 |
| §1.4 L39 华中科技大学 [11] | ⚠ 仍残存 | rationale.md L41 团队-编号错配完全未修 |
| 一号多用导致新颖性失锚 | ⚠ 仍残存 | 4 处"首次/尚未见"声明部分失锚 |
| L31 "THz 频段" [10] 错配 | ⚠ 仍残存 | rationale.md L31 [10] 与 FeCuP₂S₆ 不对应 |

**修复率统计**：R1 共 9 个 P0/P1 问题 → ✅ 完全解决 2 个（#1 #2）/ ⚠ 部分解决 5 个（#3 #4 #5 #6 #8）/ ⚠ 仍残存 2 个（#7 #9）

### 10.2 是否达到输出标准

**未达到**。本轮聚焦 rationale.md 段落级深审 + 跨章节一致性，按 general 阈值：
- min_overall_score = 0.80（**当前 0.6415，未达标**）
- max_high_issues = 0（**当前 8 个 high issues，超标**）
- max_medium_issues = 3（**当前 4 个 medium issues，超标 1**）

**关键阻塞**：
- 6 个 critical issues 中 4 个为"团队-编号错配"——这是评审专家 5 分钟内必查项
- 5 处 arXiv 裸引 + scheme.md 全章裸引 = **8 处引用格式与编号体系断裂**
- "首次/尚未见" 声明 4 处失锚

### 10.3 返工优先级

**P0（本轮必须修复，否则不予通过）**：
1. 修复 rationale.md L41 华中科技大学团队 [11] 错配（critical #1）
2. 修复 rationale.md L19/L45 [13] Lin/Shanghai Jiao Tong 错配（critical #2）
3. 修复 rationale.md L21 [16] Ruiz 错配应为 [17]（critical #3）
4. 修复 rationale.md L25 + content.md L43 [21] Yarmohammadi 错配应为 [22]（critical #4）
5. 修复 content.md L27 [17] Ghorashi-Rappe 错配应为 [18]（critical #5）
6. 全文核查 references.md 团队-编号对应（critical #6）

**P1（定稿前必须修复）**：
1. content.md L27 + rationale.md L23 [17] Ghorashi-Rappe 错配（high #7）
2. rationale.md L31 [10] "THz 频段" 错配（high #8）
3. scheme.md 6 处裸引/裸号改为 [N] 格式（high #9）
4. content.md 5 处 arXiv 裸引改为 [N] 格式（high #10）
5. rationale.md L67/L79/L81 4 处"尚未见/首次"声明重新核实（high #11）
6. rationale.md L11/L13/L31/L57 [11] 一号多用正文配套修复（high #12）
7. rationale.md L11/L21 [16] 一号多用正文配套修复（high #13）

**P2（建议修复）**：
1. rationale.md §1.5 4 处"首次/尚未见"密度降低（medium #14）
2. references.md [29] "in preparation" 预研基础补充（medium #15）
3. rationale.md L11/L25/L23 超长句拆分（medium #16）
4. rationale.md §1.3 "瓶颈一/二/三" 加粗子标题改为流畅段落（medium #17）

**P3（建议）**：
1. rationale.md L65 "本项目的核心科学问题是：" 套语去除（low #18）
2. rationale.md `建立`/`提供`/`实现` 动词类分散（low #19）

### 10.4 下一轮评审建议聚焦

1. **references.md 团队-编号对应表核查**：建立 40 条 references 的"团队/作者/期刊/年份"矩阵，验证 rationale §1.4 国内研究现状与 references 一一对应
2. **scheme.md 裸引 → [N] 格式统一**：scheme.md 全章 6 处裸引改为 [N] 后，重新扫描 scheme.md 引用密度
3. **arXiv 预印本最新发表状态核实**：核查 5 个 arXiv 编号 [31]-[35] + 2403.06531 [36] 截至 2026-08-19 是否已正式发表，若已发表则替换为正式期刊引用
4. **"首次/尚未见" 5 处声明检索日志核查**：建立检索日志文件支撑每处声明的核实过程

---

## 十一、评分块（程序解析）

```
## 评分
创新性：0.78
可行性：0.72
严谨性：0.40
表达质量：0.50
综合评分：0.64
```

注：综合评分 0.6415 按 v6.9.25 强制约束（锚点对比结论 = 基本接近 → 综合评分 ≤0.89；当前 0.6415 在 ≤0.89 范围内合规）。但按 general 项目 min_overall_score = 0.80 阈值，**本轮未达输出标准**。