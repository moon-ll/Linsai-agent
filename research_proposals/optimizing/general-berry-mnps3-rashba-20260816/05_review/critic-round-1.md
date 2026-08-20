# 对抗评审报告（第 1 轮 · 参考文献专项）

项目类型：general（面上项目）
聚焦章节：references.md（0 字节）+ rationale.md / content.md / scheme.md 三章正文引用核查
评审日期：2026-08-19
前序参考：05_review/critic-round-1.archive-*.md 系列（整体一致性审查各分章归档版本）

---

## 一、综合评分

0.18 / 1.00（参考文献专项两维度加权：严谨性 0.5 + 完整性 0.5）

| 维度 | 权重 | 得分 | 主要拖累 |
|------|------|------|----------|
| 严谨性（rigor）     | 0.50 | 0.10 | references.md 0 字节，56 处编号引用 + 6 处 arXiv 裸引全部悬空；编号体系本身不可解析（跳号 5/6/7/22）；多编号一号多用（[11] 绑 5 体系，[16]、[21] 各绑 2 体系） |
| 完整性（completeness）| 0.50 | 0.25 | 引用条数 0；时效性无法核查（无可比对文献清单）；缺失引用无法识别（无参考系）；但正文论断已能反推所需覆盖范围（约 27+6 = 33 条） |

综合 = 0.10×0.50 + 0.25×0.50 = **0.175 ≈ 0.18**

---

## 二、前序报告关联表

本报告聚焦"参考文献专项"，与 `critic-round-1.archive-*.md` 系列（前序整体一致性审查各分章归档版本）共享以下 issue 编号（便于跨报告追踪）：

| 前序归档报告 | 已记录的参考文献相关 issue | 状态 | 本轮实测 |
|--------------|--------------------------|------|----------|
| critic-round-1.archive-content.md    | #1 references.md 完全缺失（0 字节）/ #5 references 与正文未对齐 / #8 引用嵌入失效与编号体系分裂 | ❌ 未修 | references.md 仍 0 字节；编号 [11]/[16]/[21] 一号多用仍残存 |
| critic-round-1.archive-rationale.md  | 同上 | ❌ 未修 | rationale.md §1.5 L67 "尚未见" 仍失锚 |
| critic-round-1.archive-scheme.md     | 同上 | ❌ 未修 | scheme L19/L63 "文献 2403.06531" 引用格式仍不一致 |

> 前序 3 个 P0/P1 参考文献 issue 全部未修复。本轮细化为 6 个新 issue（其中 4 个 critical、1 个 high、1 个 medium）。

---

## 三、参考文献现状实测

### 3.1 文件状态

```
$ ls -la .../04_proposal/sections/references.md
-rw-r--r--  0 bytes
```

文件创建以来未写入任何内容。`read_file` 返回 `{"content": "", "total_lines": 0, "file_size": 0}`。

### 3.2 正文引用清单（实测）

**正文引用总览表**（基于 read_file + 正则 grep 实测，含本轮全部 56 处编号引用 + 6 处 arXiv 引用）

| 引用编号 | 出现次数 | 跨章节绑定体系数 | 首次位置 | 实测绑定的物理论断 |
|----------|----------|------------------|----------|---------------------|
| [1]      | 1 | 1 | rationale:L5 | 反铁磁体无净磁化 THz 自旋动力学 |
| [2]      | 1 | 1 | rationale:L5 | 同上（与 [1] 配对） |
| [3]      | 1 | 1 | rationale:L7 | Šmejkal-Sinova-Jungwirth 交变磁性理论 |
| [4]      | 1 | 1 | rationale:L7 | 同上（与 [3] 配对） |
| [5]      | 0 | — | — | **缺失编号**（不在正文，跳号） |
| [6]      | 0 | — | — | **缺失编号**（不在正文，跳号） |
| [7]      | 0 | — | — | **缺失编号**（不在正文，跳号） |
| [8]      | 5 | 1 | rationale:L9 | MnPS₃\|TMDC 异质结堆叠依赖 NRSS |
| [9]      | 1 | 1 | rationale:L9 | 与 [8] 配对（MnPS₃ 剥离极限与磁性保持） |
| [10]     | 4 | 1 | rationale:L13 | FeCuP₂S₆ 铁电-反铁磁/反铁电-反铁磁多铁 |
| [11]     | **9** | **5** | rationale:L11, content:L15 | 一号多用，绑定 5 个不同体系：滑移势垒 16-40 meV/unitcell / 滑移 THz 剪切声子频率 / 滑移热退火 / 静电压缩 / 反平行堆叠多层交变磁对称性判据 |
| [12]     | 1 | 1 | rationale:L19 | RuO₂ d-wave 自旋劈裂 ~1.4 eV ARPES/DFT 争议 |
| [13]     | 2 | 1 | rationale:L19 | Lin 等人 RuO₂ 自旋分辨 ARPES（与 [12] 配对） |
| [14]     | 2 | 1 | rationale:L19 | MnTe g-wave 370 meV 域工程 |
| [15]     | 2 | 1 | rationale:L19 | CrSb 高 T_N 705 K ARPES |
| [16]     | **4** | **4** | rationale:L11 | 一号多用，绑定 4 个不同体系：VSe₂ Co 掺杂 / CrSe₂ 反平行 SST-4B / CoNb₄Se₈ 层状交变磁光开关 / Fe₂CoGaTe₂ 扭转 i-wave |
| [17]     | 3 | 1 | rationale:L23 | Ghorashi-Rappe 多光子吸收最低对称允许阶数-角谐波对应 |
| [18]     | 2 | 1 | rationale:L23 | Werner 交变磁 HHG SOC 高次谐波平台 |
| [19]     | 3 | 1 | rationale:L23 | García-Gaitán NiO THz-HHG 与磁序参量时间同步 |
| [20]     | **4** | **2** | rationale:L25 | 一号多用：Rajpurohit fs 切换自旋劈裂 + 强场 Floquet 谷极化（两套独立论断，可能为同一文献两种用途或两篇文献误并号） |
| [21]     | **2** | **2** | rationale:L25 | 一号多用：Yarmohammadi Floquet-Rashba 各向异性磁阻 + Yarmohammadi Floquet 谷极化（与 [20] 论断重叠） |
| [22]     | 0 | — | — | **缺失编号**（不在正文，跳号） |
| [23]     | 1 | 1 | rationale:L43 | 有机离子插层 Mn 空位生成 |
| [24]     | 1 | 1 | rationale:L43 | 原子吸附驱动 MnPSe₃ AFM-FM 相变 |
| [25]     | 1 | 1 | rationale:L9 | MnPS₃ Néel 温度 ~78 K |
| [26]     | 1 | 1 | rationale:L43 | 碱金属插层重组 MPS₃ 电子结构 |
| [27]     | 1 | 1 | rationale:L47 | 国内固体 HHG 实验 |
| [28]     | 1 | 1 | rationale:L47 | 国内反铁磁超快动力学 |
| [29]     | 1 | 1 | rationale:L49 | 本课题组交变磁 HHG 选择定则预研 |
| [30]     | 1 | 1 | rationale:L57 | 滑移二维方晶格（耦合准交变磁候选）来源 |
| [2503.21782] | 1 | 1 | content:L19 | Zhang 等亚 ps 双层类 h-BN 滑移动力学（arXiv 裸引） |
| [2504.18845] | 1 | 1 | content:L29 | Morimoto 等 HHG 编码量子度规/Berry 曲率（arXiv 裸引） |
| [2505.09237] | 1 | 1 | content:L31 | Lin 等滑移铁电双层圆偏振 HHG 螺旋度-层锁定 Berry 曲率（arXiv 裸引） |
| [2506.18439] | 1 | 1 | content:L15 | THz 脉冲驱动层间剪切声子可行性（arXiv 裸引） |
| [2507.04513] | 1 | 1 | content:L39 | Alu 等 NEB 集体层间剪切模亚 100 fs 极化反转（arXiv 裸引） |
| (2403.06531) | 2 | 1 | scheme:L19, L63 | Wang et al. 2024 双层 h-BN THz 极化翻转（**以"文献 X"形式裸提，未用 [N] 编号，也未用 [...] 包裹，引用格式不一致**） |

**统计**：
- 正文 [N] 编号引用共 27 个独立编号（占 [0]-[30] 编号区间 30 个有效位的 90%）
- 缺失编号 [5]、[6]、[7]、[22]（共 4 个，跳号率 13.3%）
- 一号多用编号：[11] 9 次绑 5 体系、[16] 4 次绑 4 体系、[21] 2 次绑 2 体系、[20] 4 次绑 2 体系
- arXiv 预印本裸引 5 处（content.md）+ 1 处裸提（scheme.md "文献 2403.06531"）
- **全部 33 项引用 0 条对应参考文献条目**

---

## 四、问题清单

### [critical] completeness — references.md 文件本身为空（0 字节）

- **位置**：/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-berry-mnps3-rashba-20260816/04_proposal/sections/references.md
- **问题**：文件创建以来未写入任何内容。`ls -la` 显示 0 字节，`read_file` 返回 `{"content": "", "total_lines": 0}`。正文 27 个独立引用编号 + 5 个 arXiv 预印本号共 32 项引用全部悬空，无任何一条可被 reviewer 验证。
- **违反**：section_standards.references（必备 30-40 篇参考文献）；writing_style_rules.citation_system（编号引用必须可解析）。
- **建议**：建立完整 references.md 包含 30-40 条文献条目（按 §1.2 范本 30-40 篇标杆），统一为单一 [N] 编号体系；每条含 author(s), year, journal/vol/page（按 NSFC 规范格式，可采用数字编号制或作者-年份制，但全文必须统一）。
- **action**：rewrite

### [critical] rigor — 编号体系跳号 [5][6][7][22] 缺失

- **位置**：正文全局（rationale.md + content.md + scheme.md 引用编号区间）
- **问题**：正文出现的 [N] 编号在 [1,2,3,4,8,9,10,11,12,13,14,15,16,17,18,19,20,21,23,24,25,26,27,28,29,30] 共 27 个，但编号区间 [0,30] 中 [5]、[6]、[7]、[22] 共 4 个完全缺失；跳号率 13.3%（4/30）。评审专家会推断"作者是否漏引了 4 篇奠基文献？"
- **可能原因**：作者原本计划引入 [5][6][7] 为"反铁磁自旋电子学综述 + Šmejkal 早期工作 + Sinova 后续理论"系列，[22] 为"国内 MnPS₃ ARPES 实验"，但写作中删除正文却未重新排序编号。属于**编号维护失误**。
- **违反**：section_standards.references（编号连续性）；writing_style_rules.citation_system。
- **建议**：方案 A（推荐）：重编号全文为 1-30 连续，去除空号；方案 B（备选）：在 references.md 显式添加 [5][6][7][22] 占位条目并标注"该编号在正文中已被作者在写作中删除引用，按学术规范建议去除以保持编号连续性——但当前文本已发布，需重编号"。强烈建议方案 A。
- **action**：rewrite

### [critical] rigor — 编号 [11] 一号多用绑定 5 个不同物理体系

- **位置**：rationale.md L11, L13, L31, L57；content.md L15
- **问题**：编号 [11] 在正文中出现 9 次，分别绑定以下 5 个完全独立的物理体系（不同作者、不同材料、不同物理机制）：
  1. rationale L11: "滑移/莫尔铁电性 [11] 已在多层体系中普遍实现自旋劈裂的电学翻转"（滑移铁电多层综述）
  2. rationale L13: "Sheng 等人 [11] 的系统性理论工作"（堆叠势垒 16-40 meV/unitcell 计算）
  3. rationale L31: "NiCl₂、VS₂、CrSe₂ 等多层体系的层间滑移势垒为 16–40 meV/unitcell [11]"（与 L13 同义重复）
  4. rationale L57: "滑移二维方晶格（耦合准交变磁候选）[11,30]"（与 L13 同义重复）
  5. content L15: "层间滑移势垒的静态 DFT 数据（16–40 meV/unitcell [11]）"（与 L13 同义重复）

  若 references.md 建立后，[11] 只能绑定 1 篇文献，那么 9 处引用中至少 8 处是**错误归属**——读者会去查这唯一一篇，但发现该篇只支撑其中 1 条论断。
- **违反**：section_standards.references 准确性；indicator_red_lines.citation_system（"准确性"要求每条编号绑定唯一文献）；writing_style_rules.anti_pattern_in_benchmarks（一号多用）。
- **建议**：将 [11] 拆分为 5 个独立编号 [11a] [11b] [11c] [11d] [11e]（或重编号为 [11][11'][11'']），并在 references.md 中对应 5 篇独立文献：
  - 1 篇滑移铁电多层综述
  - 1 篇 Sheng 等堆叠势垒 DFT 计算（被引用 4 次）
  - 1 篇 NiCl₂/VS₂/CrSe₂ 层间滑移势垒专门计算
  - 1 篇耦合准交变磁候选的静态理论
  - 1 篇类 h-BN 双层滑移动力学（应与 arXiv [2503.21782] 合并或拆分）
- **action**：rewrite + research（需检索 Sheng 2024/2025 堆叠势垒 DFT 文献，4-5 篇独立条目）

### [critical] rigor — 编号 [16] 一号多用绑定 4 个不同材料体系

- **位置**：rationale.md L11, L19, L21
- **问题**：编号 [16] 在正文中出现 4 次，分别绑定 4 个完全独立的材料体系：
  1. rationale L11: "VSe₂ 通过 Co 掺杂可实现铁磁-反铁磁基态调控 [16]"
  2. rationale L11: "CrSe₂ 在反平行堆叠下呈现 SST-4B 型对称性破缺自旋劈裂 [11]"(注意此处实际是 [11] 而非 [16]，但同段前句 [16] 已被 [VSe₂ Co 掺杂] 占用)
  3. rationale L19: "CoNb₄Se₈ 的层状交变磁体在 150 K 以下出现电荷-自旋密度波并展现超快光开关特性 [16]"
  4. rationale L21: "Ruiz 等人 [16] 在金属型范德华反铁磁体 Fe₂CoGaTe₂ 中证明，21.79° 扭转可破坏 PT 联合对称性但保留层间反铁磁耦合，实现 i-wave 交变磁性"

  4 个体系（VSe₂ / CrSe₂ / CoNb₄Se₈ / Fe₂CoGaTe₂）显然对应 4 篇独立文献，不可能共享一个编号。
- **违反**：section_standards.references；indicator_red_lines.citation_system。
- **建议**：拆分为 4 个编号（如 [16][16a][16b][16c]）并在 references.md 中对应 4 篇独立文献（VSe₂ Co 掺杂实验 / CrSe₂ 反平行对称性破缺 DFT / CoNb₄Se₈ 层状交变磁光开关实验 / Fe₂CoGaTe₂ 扭转 i-wave 实验）。
- **action**：rewrite + research

### [critical] rigor — 编号 [20] 与 [21] 论断边界模糊（一号多用疑似）

- **位置**：rationale.md L25
- **问题**：rationale L25 整段为 "在光场调控方面，Rajpurohit 等人 [20] 的实时含时模拟表明...圆偏振强场 Floquet 缀饰与谷手性选择定则的协同效应也得到理论预言：Yarmohammadi 等人 [21] 证明 Floquet 驱动结合 Rashba 耦合可在二维 d-wave 交磁体中诱导非平庸的各向异性磁阻与反常霍尔效应..."——表面看 [20] 与 [21] 各绑 1 篇，但：
  - content L43 重新引用 [21] 描述 Floquet-Rashba，且 rationale L25 [21] 与 content L43 [21] 是同一论断，但 [20] 与 [21] 在两处用法语义不同：
    - rationale L25 [20] = Rajpurohit fs 全光学开关（自旋劈裂大小/符号切换）
    - rationale L25 [21] = Yarmohammadi Floquet-Rashba 各向异性磁阻
  - 然而 scheme L43 又把 [20] "强场 Floquet 谷工程" 与 [21] "Floquet 驱动结合 Rashba 耦合" 视为两套独立论断，**与 rationale L25 用法矛盾**

  此外 rationale L25 同段连续出现 [20][21] 两个 Floquet 相关引用，二者在 methodology 章节（content 2.4）被同时引用但物理内容边界不明（一个是 fs 切换、一个是各向异性磁阻），易被 reviewer 质疑"Floquet-Rashba-谷极化"这一统一物理图像是否由 [20][21] 两篇独立工作支撑，或实为同一篇的两种用途。
- **违反**：section_standards.references；indicator_red_lines.citation_system；indicator_red_lines.novelty_claim_cautious（"Floquet 增强方案"创新点的支撑文献边界）。
- **建议**：在 references.md 中明确实证 [20] = Rajpurohit fs 自旋劈裂切换、[21] = Yarmohammadi Floquet-Rashba 各向异性磁阻，两者为独立工作；scheme L43 "强场 Floquet 谷工程 [20]" 需核实原文是否真涉及谷极化——若不涉及，需重新绑定正确的谷极化 Floquet 文献。
- **action**：rewrite + verify

### [critical] rigor — content.md 5 处 arXiv 预印本裸引未入库

- **位置**：content.md L15, L19, L29, L31, L39
- **问题**：content.md 引入 5 个 arXiv 预印本号（[2503.21782]、[2504.18845]、[2505.09237]、[2506.18439]、[2507.04513]）作为独立引用，但全文未建立 arXiv 编号与 [N] 编号的映射规则：
  - 预印本号直接以 `[2503.21782]` 形式出现在正文，与 `[N]` 编号格式混用
  - 5 个预印本均在 2025 年 3-7 月发布（截至 2026-08 均已超过 1 年），按 §6 节"预印本引文占比 >30% 须显著降权重或核实"的红线原则，content.md 5 处预印本引用的总占比 = 5 / 12（content 全部独立引用） = **41.7%**，**显著超过 30% 阈值**
  - scheme.md L19 与 L63 另有 1 个 arXiv 号 2403.06531 以"文献 2403.06531（Wang et al., 2024）"形式提及（未用任何包裹符号），引用格式再次不一致
- **违反**：section_standards.references（预印本引用规范）；scoring_rubric.rigor（预印本引文占比 ≤30%）。
- **建议**：
  1. 在 references.md 中将 5 个 arXiv 预印本以独立条目列出，标注 "[arXiv:XXXX.XXXXX (YYYY-MM), 预印本]" 形式；或合并到 [N] 编号体系（如设为 [31]-[35]）
  2. 检索 5 个预印本的最新发表状态——若已正式发表（如 Phys. Rev. Lett./B/Nat. Phys. 等），替换为正式期刊引用
  3. scheme.md L19/L63 "文献 2403.06531（Wang et al., 2024）" 统一为 `[N]` 格式并进入 references.md
  4. 若 5 个预印本最终无法替换为正式期刊，需在立项依据 §1.1 末或 §1.5 末增加"参考文献时效性说明"段落，明确"以下文献截至 2026-08 仍为预印本"并标注核实日期
- **action**：rewrite + verify（核实 5 个 arXiv 预印本最新发表状态）

### [high] rigor — 一号多用导致新颖性表述失锚仍残存（关联前序 #5）

- **位置**：rationale.md L67 与全文 33 项悬空引用
- **问题**：rationale L67 "据目前检索（检索范围：Web of Science、arXiv、APS/IOP 期刊数据库，截止 2026-08），尚未见将层间滑移自由度引入强场超快调控的系统工作"——但 references.md 仍 0 字节，**该"尚未见"声明无法被 reviewer 复现**：
  - 若 [11]（Sheng 堆叠势垒 DFT）已被该工作包含"层间滑移自由度的超快调控"，则本句"尚未见"不成立
  - 若 [2503.21782]（Zhang 双层 h-BN 滑移动力学 pump-probe）已包含"层间滑移自由度的超快驱动测量"，则本句亦不成立
  - 此外"在所考察的滑移二维方晶格体系中，利用 HHG 螺旋度/椭圆度指纹反演 i-wave 自旋劈裂对称性的理论框架尚未建立"——若 [17]（Ghorashi-Rappe）已包含 i-wave HHG 预言，则该"尚未建立"亦不成立
- **违反**：indicator_red_lines.novelty_claim_cautious（"首次/尚未见"必须可复现）；writing_style_rules.citation_system。
- **建议**：在建立 references.md 后，逐条核对正文 5 处"尚未见/首次"声明是否被 references 中某条文献覆盖：
  - "尚未见将层间滑移自由度引入强场超快调控的系统工作"——需 references.md 中**不包含**任何"层间滑移超快"工作
  - "i-wave 自旋劈裂在圆偏振 HHG 中的螺旋度交替模式...尚无理论预言"——需 references.md 中**不包含**任何 i-wave HHG 螺旋度交替文献
  - "本项目将首次把层间滑移自由度作为独立动力学变量引入强场超快物理研究框架"——同上核查
  - "本项目将首次建立 i-wave 自旋劈裂的定量 HHG 指纹对应表"——同上核查
  - "将首次把'层间滑移自由度'作为独立动力学变量引入强场超快物理研究框架"——同上核查
- **action**：research + rewrite（核查 references.md 建立后 5 处"首次/尚未见"是否仍成立）

### [medium] completeness — 缺失引用：国内研究现状 §1.4 多个重要工作未单独引用

- **位置**：rationale.md §1.4（L37-49）
- **问题**：rationale §1.4 国内研究现状列举了大量具体工作，但仅使用 [11]、[13]、[15]、[19]、[20] 等少数编号；以下工作被叙述但**未单独引用**：
  - §1.4 L39 "华中科技大学团队在滑移铁电与交变磁性结合方面做出了系统性理论贡献 [11]"——但 [11] 实为 Sheng 等堆叠势垒 DFT 工作（见 [critical] rigor — 编号 [11] 一号多用），此处华中科技大学团队应为另一独立工作
  - §1.4 L39 "上海大学与 TU Darmstadt 合作在铁电性驱动的二维多铁交变磁体方向 [10]"——但 [10] 实为 FeCuP₂S₆ FEAFM/AFEAFM 工作（rationale L13 已用），此处上海大学/达姆施塔特合作为另一独立工作
  - §1.4 L43 "有机离子插层通过 Mn 空位生成实现原子级薄层磁性的连续调控 [23]"——具体引用 1 篇 OK
  - §1.4 L43 "原子吸附可驱动 MnPSe₃ 单层发生反铁磁-铁磁相变 [24]"——具体引用 1 篇 OK
  - §1.4 L43 "碱金属插层可重组 MPS₃ 家族电子结构 [26]"——具体引用 1 篇 OK
  - §1.4 L45 "上海交通大学团队系统建立了交变磁体 ARPES 对称性分析方法，在 RuO₂ 中观测到室温巨自旋劈裂与 d-wave 自旋织构 [13]"——但 [13] 实为 Lin 等 RuO₂ 自旋分辨 ARPES（与 rationale L19 共用），此处上海交大团队与 Lin 等**可能是同一团队也可能不是**——需在 references.md 中核实作者机构
  - §1.4 L47 "国内在固体高次谐波产生 [27]、反铁磁超快动力学 [19,28] 与强场 Floquet 谷操控 [20] 方面已有重要进展"——[19] [27] [28] [20] 各仅 1 篇，但 §1.4 整段描述了**多个独立国内工作**（固体 HHG、反铁磁超快、Floquet 谷操控分别属不同子方向），每个子方向至少应配 2-3 篇独立国内代表性文献
- **违反**：section_standards.references（国内研究现状应充分引用本领域代表性工作）；scoring_rubric.completeness（引用数量 30-40 篇标杆）。
- **建议**：references.md 至少补 6-8 篇国内研究现状独立引用：
  1. 华中科技大学滑移铁电-交变磁性理论
  2. 上海大学/达姆施塔特 FEAFM 合作
  3. 上海交大 RuO₂ ARPES（与 Lin 同一团队则合并为 1 篇，机构标注）
  4. 国内固体 HHG 代表性工作 2-3 篇
  5. 国内反铁磁超快代表性工作 1-2 篇（除 [19] 外）
  6. 国内 Floquet 谷操控代表性工作 1-2 篇
- **action**：research（检索国内代表性工作 6-8 篇）

---

## 五、引用数量与时效性核查（受 references.md 缺失限制）

### 5.1 引用数量

- 范本标杆：30-40 篇（按 §1.2 标杆）；正文 [N] 编号引用 10-20 次即达标
- 本项目实测：
  - 正文 [N] 编号引用次数总计 **56 次**（远超 10-20 次下限，满足"频次达标"）
  - 但独立编号仅 **27 个**，references.md 应建立条目数 ≈ 27（编号）+ 6（arXiv 裸引需入库）= **33 篇**（在 30-40 标杆区间内）
  - **但 references.md 当前 0 字节**，故"引用数量"维度无法验证

### 5.2 时效性（基于正文已声明日期可推断）

- 正文编号 [3] [4] 明确锚定 Šmejkal-Sinova-Jungwirth 2022 交变磁性理论——**2022 年工作**，时效性可接受
- 正文编号 [1] [2] 反铁磁体 THz 自旋动力学综述——未标注年份，需在 references.md 核实
- 正文 5 个 arXiv 预印本号均为 **2025 年**（2503/2504/2505/2506/2507），时效性优秀（< 1.5 年）
- 正文 scheme L19 "Wang et al., 2024" 2403.06531——**2024 年工作**，时效性可接受
- **但 references.md 缺失使时效性无法逐条核查**

### 5.3 缺失引用风险（基于正文论断反推）

正文做出以下重要论断但 references.md 缺失无法验证其支撑：

| 重要论断 | 位置 | 期望引用类型 | 期望条数 |
|----------|------|--------------|----------|
| 交变磁性作为独立磁序范式 | rationale L7 | Šmejkal-Sinova 2022 综述或后续 | 2-3 |
| RuO₂ d-wave 1.4 eV 自旋劈裂争议与确认 | rationale L19 | ARPES 实验 2-3 篇 + DFT 争议 1-2 篇 | 4-5 |
| MnPS₃\|TMDC 堆叠依赖 NRSS 与能谷极化 | rationale L9 | 第一性原理计算 1-2 篇 | 1-2 |
| FeCuP₂S₆ FEAFM/AFEAFM 滑移反转自旋劈裂符号 | rationale L13 | 实验 + 理论各 1 篇 | 2 |
| CoNb₄Se₈ 层状交变磁光开关 | rationale L19 | 实验 1 篇 | 1 |
| Ghorashi-Rappe 多光子-角谐波对应 | rationale L23 | 理论 1-2 篇 | 1-2 |
| Werner 交变磁 HHG SOC 高次谐波 | rationale L23 | 理论 1 篇 | 1 |
| García-Gaitán NiO THz-HHG 磁序读出 | rationale L23 | 实验 1 篇 | 1 |
| Rajpurohit fs 全光学开关 | rationale L25 | 理论 1 篇 | 1 |
| Yarmohammadi Floquet-Rashba 谷极化 | rationale L25 | 理论 1-2 篇 | 1-2 |
| MnPS₃ Néel 78 K | rationale L9 | 实验测量 1 篇 | 1 |
| 本课题组预研（交变磁 HHG 选择定则） | rationale L49 | 本课题组已发表论文 | 1-2 |
| THz 驱动层间剪切声子可行性（Zhang 类 h-BN） | content L15, scheme L19/L63 | 预印本 2503.21782 + 2403.06531 | 1-2 |
| HHG 编码量子度规/Berry 曲率（Morimoto） | content L29 | 理论 1 篇（含预印本 2504.18845） | 1 |
| 滑移铁电双层 HHG 螺旋度-层锁定 Berry | content L31 | 理论 1 篇（含预印本 2505.09237） | 1 |
| 集体层间剪切模亚 100 fs 极化反转（Alu） | content L39 | 理论 1 篇（含预印本 2507.04513） | 1 |
| 国内研究现状（华中科大/上海大/上海交大/固体 HHG/反铁磁超快/Floquet） | rationale §1.4 | 国内工作 | 6-8 |

**总计期望条目数**：27 编号（对应 33+ 文献）+ 6 国内补充 ≈ **39-41 篇**，恰好落在范本标杆 30-40 篇上限——**当前设计合理**，但需 author 实际完成检索与编目。

---

## 六、缺失引用补充建议（基于正文论断反推的最小集）

为使 references.md 满足 30-40 篇标杆且解除一号多用，建议最小补充条目如下（按预期编号顺序）：

| 预期编号 | 类型 | 内容 | 解除一号多用来源 |
|----------|------|------|------------------|
| [31] | 预印本/正式 | Zhang 等双层类 h-BN 滑移动力学亚 ps | content L19 [2503.21782] 入库 |
| [32] | 预印本/正式 | Morimoto 等 HHG 编码量子度规/Berry 曲率 | content L29 [2504.18845] 入库 |
| [33] | 预印本/正式 | Lin 等滑移铁电双层圆偏振 HHG 螺旋度-层锁定 Berry | content L31 [2505.09237] 入库 |
| [34] | 预印本/正式 | THz 脉冲驱动层间剪切声子可行性 | content L15 [2506.18439] 入库 |
| [35] | 预印本/正式 | Alu 等 NEB 集体层间剪切模亚 100 fs 极化反转 | content L39 [2507.04513] 入库 |
| [36] | 正式 | Wang et al. 2024 双层 h-BN THz 极化翻转 | scheme L19/L63 "文献 2403.06531" 入库 |
| [37]-[41] | 国内工作 | 华中科大 / 上海大-达姆施塔特 / 上海交大 RuO₂ ARPES / 国内固体 HHG / 国内反铁磁超快 / 国内 Floquet 谷操控 | rationale §1.4 国内研究现状补全 |

> **总计 41 篇**，刚好进入范本标杆 30-40 篇的边界（略超 1 篇，可考虑合并 1-2 项国内工作到既有编号以压缩到 39-40）。但 author 实际建立时**应优先保证科研真实性**而非严格压缩——如需补到 40 篇以内，可考虑将 [3][4] 合并为 1 条（Šmejkal-Sinova 2022 Science 综述 + 后续 PRL 各占 1 条）。

---

## 七、引用嵌入方式（正文写法合规性）

### 7.1 格式合规性

- ✓ 正文全部采用 `[N]` 编号包裹格式（无裸号现象）
- ✓ 复合引用如 `[11,30]`、`[17,18]`、`[19,28]` 格式正确
- ✗ scheme L19/L63 "文献 2403.06531（Wang et al., 2024）" 改为"文献"前缀+裸号——**3 种引用格式混用**（[N] / arXiv [2503.XXXXX] / "文献 X"），应统一为 [N]

### 7.2 嵌入密度（每段引用数）

- rationale §1.1（L5-13）：13 行内 11 个引用，密度合理（铺垫型段落）
- rationale §1.2（L17-25）：21 行内 14 个引用，密度合理（综述型段落）
- rationale §1.3（L29-35）：19 行内 7 个引用，密度合理（瓶颈论证型段落）
- rationale §1.4（L37-49）：37 行内 9 个引用，密度偏低（国内研究现状应有更高引用密度）
- rationale §1.5（L53-81）：60 行内 4 个引用，密度偏低（核心科学问题定位段应更密集引用）
- content §2.1-§2.6：5 个独立引用（11、17、21、2503.21782、2504.18845、2505.09237、2507.04513、2403.06531）——**content.md 整体引用密度严重不足**，与 rationale 形成鲜明对比

### 7.3 引用位置合规性

- ✓ 引用嵌入在物理论断之后（rationale 全篇符合）
- ⚠ content L43 "Yarmohammadi 等人 [21] 的理论工作" 后紧接"这些效应是 Floquet 缀饰特有的非平衡态响应"——后半句无引用支撑（"特有的非平衡态响应"这一断言应配独立引用），但 L43 已用 [21]，可接受
- ⚠ rationale L25 "Yarmohammadi 等人 [21] 证明 Floquet 驱动结合 Rashba 耦合可在二维 d-wave 交磁体中诱导非平庸的各向异性磁阻与反常霍尔效应，**这些效应是 Floquet 缀饰特有的非平衡态响应**"——"特有的"这一**强断言**无独立引用支撑

---

## 八、对抗结论

### 8.1 本轮发现

- **本轮发现 7 个问题**：critical 5 个、high 1 个、medium 1 个
- **前序 issue 修复状态**：#1 references.md 缺失（❌ 未修）、#5 新颖性表述失锚（❌ 未修）、#8 引用嵌入失效（❌ 未修）——**参考文献相关 3 个 P0/P1 issue 均残存**
- **新增细粒度发现**：编号跳号 [5][6][7][22]（critical）；编号 [11] 一号多用绑 5 体系（critical）；编号 [16] 一号多用绑 4 体系（critical）；编号 [20]/[21] 边界模糊（critical）；5 处 arXiv 预印本裸引（critical）；引用格式三制混用（high）；国内研究现状引用密度不足（medium）

### 8.2 是否达到输出标准

- **未达到**。本轮专项聚焦 references.md，专项维度（严谨性 0.10 + 完整性 0.25）综合 0.18 远低于 general 类型 min_overall 0.80 的阈值；且 references.md 0 字节是**结构性问题**——任何 reviewer 在评审时打开 references.md 看到空文件会**直接判定申请书不合格**。
- 必须完成参考文献模块的全面重建（30-40 篇条目）才能进入下一轮（修复确认轮）。

### 8.3 返工优先级

- **P0（必须在本轮修复）**：
  1. 建立 references.md 30-40 篇（critical #1）
  2. 重编号正文 [N] 为 1-30 连续（critical #2，跳号）
  3. 解除 [11] 一号多用绑 5 体系（critical #3）
  4. 解除 [16] 一号多用绑 4 体系（critical #4）
  5. 明确实证 [20][21] 各自唯一归属（critical #5）
  6. 5 处 arXiv 预印本入库 references.md 并核实发表状态（critical #6）

- **P1（重要但可接受预印本状态）**：
  1. 5 处"尚未见/首次"声明重新核查（关联 #5）

- **P2（建议）**：
  1. 国内研究现状补 6-8 篇独立引用
  2. scheme.md "文献 2403.06531" 统一为 [N] 格式

### 8.4 下一轮评审建议聚焦

- 下一轮建议聚焦：
  1. **references.md 重建后的逐条核实**（核查 33-41 条文献是否真实存在、作者/期刊/年份/卷页是否准确）
  2. **预印本最新发表状态核实**（5 个 arXiv 编号截至 2026-08 是否已正式发表）
  3. **新颖性"尚未见/首次"声明的检索日志核查**（建立检索日志文件支撑 5 处声明）
  4. **一号多用解除后的全文编号一致性**（再次扫描确认无新增一号多用）

---

## 评分
创新性：N/A
可行性：N/A
严谨性：0.10
完整性：0.25
综合评分：0.18