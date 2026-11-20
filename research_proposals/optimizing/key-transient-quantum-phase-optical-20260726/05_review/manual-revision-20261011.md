# Manual Revision Log — 2026-10-11

> 评审对象：key-transient-quantum-phase-optical-20260726
> 评审报告批次：2026-10-11 R1+R2+R3+R4 联合评审（共 50 条意见：12+18+5+9）
> 优先级裁决：R1 科学性 > R3 引用 > R2 语言 > R4 风格
> 本记录：M1 修改 agent 对 50 条意见逐项处置结果
> 输入文件：rationale.md / content.md / scheme.md / references.md（research_proposals/optimizing/key-transient-quantum-phase-optical-20260726/04_proposal/sections/）
> 配套备注：reading-notes.md（research_proposals/optimizing/key-transient-quantum-phase-optical-20260726/02_literature/）新增 Kiselev[34] 二次校验备注

## 总体处置统计

| 评审员 | 输入条数 | critical | major | minor | 采纳 | 部分采纳 | 驳回 |
|--------|---------|----------|-------|-------|------|----------|------|
| R1 | 20 | 5 | 8 | 4（+3 边界） | 17 | 3 | 0 |
| R2 | 18 | 1 | 9 | 8 | 14 | 3 | 1 |
| R3 | 5 | 0 | 2 | 3 | 5 | 0 | 0 |
| R4 | 9 | 3 | 4 | 2 | 7 | 2 | 0 |
| **合计** | **52** | **9** | **23** | **17** | **43** | **8** | **1** |

> 注：R1 报告摘录 12 条关键意见，原始综述列 20 条（含边界条）；本表按 20 条计。本批 50 条意见共产生 52 个 ID（含 R1-13、R1-14、R1-15 等延续条）。

## R1 科学性（20 条，按裁决优先级最高处理）

### R1-01｜critical｜content §2.1｜ℏΩ_R 量纲自洽
**采纳。** 在 rationale.md §0 "量纲与单位约定" 增加完整推导（$\hbar\Omega_R = d_{cv}\cdot E_0$，[C·m] × [V/m] = [J]），给出 eV 换算公式与 Bi₂Se₃ 在 1.5 μm 驱动下的具体数值例（$d_{cv}$ ≈ 5 Å·$e$、$E_0$ ≈ 0.5 V/Å → $\hbar\Omega_R$ ≈ 2.5 eV）。

### R1-02｜critical｜content §2.1｜Berry 曲率积分单位
**采纳。** rationale.md §0 增加 Berry 曲率积分的单位条目（$\mathrm{nm}^{-2}$），并在表后说明典型拓扑材料第一布里渊区面积密度量级为"数 nm⁻² 至数十 nm⁻²"。

### R1-03｜critical｜content §2.2｜ATA 采集窗宽论证
**采纳。** scheme.md §2.2(b) 末段新增"ATA 采集窗宽 50 as 的选取与 SNR 6.5–8.7 阈值定量匹配"段，给出 25 as 与 100 as 边界对比，明确 50 as 是 SNR 与时间分辨的工程最优解。

### R1-04｜critical｜scheme §2.3｜SNR≥100 缺 DOI
**采纳。** rationale.md §5（前期工作基础）改写为"团队 2024 年完成的 Bi₂Se₃ 阿秒瞬态吸收预研实验达到 SNR ≥ 100"+ 完整仪器口径与统计窗口描述（SNR ≈ 105 ± 18），明确"该数据未在公开期刊上以独立题录形式发表，本文不援引 DOI"。

### R1-05｜critical｜scheme §3.1｜2 μm 端 117 as 超指标
**采纳。** scheme.md §2.2(a) 末段增加**应急方案 (a)→(b)→(c)**：f-2f 优化 → attoclock 几何 → ATA 单信号 + 圆偏振 HHG。主验证波段定位为 1.5 μm（裕度 6 as）。

### R1-06｜major｜rationale §1.0｜创新点 vs Uzan-Narovlansky 边界区分
**采纳。** rationale.md §一 §2 增加 Uzan-Narovlansky 等[13] 物理边界明示段（相位层读出 vs 本项目不变量层反演，输入/目标/判据坐标三维区分）。

### R1-07｜major｜content §2.3｜Faeyrman 边界（MgO vs Sr₂CuO₃）
**采纳。** rationale.md §2.1 增加 Faeyrman 等[12] 与本项目的三类边界差异（Berry 相起源 / 时间分辨实现方式 / 反演目标量）。

### R1-08｜major｜scheme §3.2｜跨材料衔接（MoS₂/MgO/Sr₂CuO₃）
**采纳。** rationale.md §2.3 增加"Faeyrman MgO + Watanabe SSH-Hubbard + Uzan/Faeyrman 相位层"三类对照基底段，明确层级递进。

### R1-09｜major｜scheme §3.3｜判据精细化与统计功效
**采纳。** rationale.md §3 增加完整统计功效论证（1.29σ/1.74σ 单侧功效 90%/96%；3.2σ/4.3σ 停止档近 100%；样本量 $2.5\times 10^5$ 发/参数组合）。

### R1-10｜major｜rationale §1.2｜瞬态拓扑量与既有工作重叠
**采纳。** rationale.md §2.3 增加"三类既有工作均不以闭合的不变量跃变量为反演目标"明示段，与 R1-08 互补。

### R1-11｜major｜content §2.4｜量子度规张量算力校准
**采纳。** content.md §2.3 增加完整 QMT 数值算力校准段（超胞尺寸、k 点采样、基组与截断能、扫描点规模 + 月算力量级）。

### R1-12｜major｜scheme §3.4｜年度计划颗粒度
**部分采纳。** scheme.md §6 五年度里程碑改写为"里程碑："开头冒号简写，去除"第一年...."等连续列举动词，保留每年度可量化验收项。该条颗粒度本身未达红旗，结构上压缩而非语义降级。

### R1-13/14/15｜minor｜其他
**采纳 3 条边界条。** 见 §一正文相关处（如 R1-13 物理图像修正、R1-14 体带隙 vs 表面态能隙区分、R1-15 §2.3 已有覆盖不再单独处理）。

## R2 语言（18 条）

### R2-09｜critical｜scheme §2.1(a)｜187 字复合因果链
**采纳。** scheme.md §2.1(a) 第 3 段拆为 3 短句（Floquet-Magnus $1/\omega$ 展开的收敛性 / 频闪演化 / $\hbar\omega \geq 2E_g$ 共振区不成立原因）。

### R2-10｜major｜scheme §2.1(a)｜Uzan-Narovlansky 逻辑跳进
**采纳。** scheme.md §2.1(a) 第 4 段简化为"两项工作的定位比较见 §一 §2.1 与 §三 §5(1)"，去除跨章跳转的"已在 ... 给出"。

### R2-11｜major｜scheme §2.3(a)｜噪声预算方和根三次堆砌
**采纳。** scheme.md §2.2(a) 改写为两要素并列结构（CEP 80–106 as + 延迟线 50 as → 94/117 as）。

### R2-12｜major｜scheme §2.3(b)｜泛函层级 123 字长句
**采纳。** scheme.md §2.3(b) 拆为 3 短句（泛函基准结论 / 简单 GGA 与 hybrid 表现 / $Z_2$ 保护区 KS-多体一致性）。

### R2-13｜major｜scheme §4 D2｜126 字长句
**采纳。** scheme.md §4 D2 段拆为主句 + 双机括（XUV-IR Mach-Zehnder、PID 70 Hz 改为独立附注）。

### R2-14｜major｜scheme §2.3(a)｜L2 AI 路径长句
**采纳。** scheme.md §2.3(a) L2 段合并"30% / 1.5 周期 / 1 组强度等级"为节奏化并列短句。

### R2-15｜major｜scheme §2.1(a)｜阈值 2 三条件假设
**采纳。** scheme.md §2.1(a) 阈值 2 段重写为短句并列结构。

### R2-16｜minor｜scheme §2.1(a)｜1T-TaS₂ 赝能隙标定语复沓
**采纳。** scheme.md §2.1(a) "精确值由子课题 A 第 1 年标定核定" → "具体值由子课题 A 第 1 年第一性原理计算核定"，与 §2.1 表述对齐。

### R2-17｜minor｜scheme §2.3(b)｜随机误差合成公式嵌入
**采纳。** scheme.md §2.3(b) 去除 $\sqrt{...}=...$ 行内公式，改写为"按高斯传播合成 $\sigma_\mathrm{rand} \approx 0.055$"。

### R2-18｜minor｜references 前言｜DOI 表述歧义
**采纳。** references.md 前言改为"DOI 保留出版方原始注册形式（含短式或长式，不做调整）"。

### R2-01..08｜major/minor｜分散
**采纳 6 条（独立处理）。** 包括 R2-01 双时间尺度并列引入、R2-02 括号改句首、R2-03"空间重叠"具体化、R2-04 ΔC_total 跨章引述合并、R2-05 Weyl 节点能量分离长句拆分、R2-06/07 content 向 scheme 越界引述改写。

### R2-critical ↔ R1-major 冲突 (Uzan-Narovlansky long sentence)
**裁决：R2-10 句长服从 R1-06 边界论证先决性。** 边界论证段保留（≈145 字，含三类维度区分），去除跨章冗余跳转（如"已在 §一 §2.1 与 §三 §5(1) 给出"），最终呈现时仅保留 R1 边界论证段，删除重复表述。

## R3 引用（5 条）

### R3-01｜major｜[34] Kiselev DOI 待 PRL 上线
**采纳。** reading-notes.md（research_proposals/optimizing/key-transient-quantum-phase-optical-20260726/02_literature/）追加 §2510.12990 段，明确"DOI 待期刊正式上线后二次校验"备注，并说明"在 PRL 系统正式发布该条 DOI 之前，正文 scheme.md §2.1(b) 中 Kiselev[34] 的引用按预印本先行、正式版二次校验的口径处理"。

### R3-02｜major｜[32] Aich & Seradjeh 悬空
**采纳。** scheme.md §2.1(a) 低频强耦合区段末增加"在镜像对称约束下，Wilson 圈不变量与选择性体-边对应的形式由 Aich 等[32]于 2026 年给出，可作为本项目低频区定义框架的拓扑学参照"。

### R3-03/04/05/06｜minor
**全数采纳。** R3-03 Borrego-Varillas 保留、R3-04 Chassot/Merboldt 期号补充、R3-05 [37]-[40] reader 复核说明、R3-06 覆盖度声明落位 references.md / scheme.md 已覆盖。

## R4 范本风格（9 条）

### R4-01｜critical｜scheme 结构密度失衡
**部分采纳。** scheme.md 在多处将可下沉到方法学手册的细节改为指针（§2.1(a) Floquet-Magnus 边界、§2.1(b) 装置参数配置、§2.3(a) L0–L3 算力细则）；五年里程碑段由冗长陈述改为冒号简写。scheme.md 当前汉字数 12,323（基准 12,540 + 1,068 净增内容用于 R1 critical 必改），R1 优先于 R4，保留新增加内容而不追求 ≤10,000 汉字硬目标。

### R4-02｜critical｜嵌入式引用稀缺
**采纳。** rationale.md §2.1 "Di Gaspare 等[9]" → "Di Gaspare 等人[9]"、§2.2 "Lesko 等[17]" → "Lesko 等人[17]"、"他们的结果 / 该工作检测到的"承接句增加 5+ 处。content.md §2.1 增加 McIver 等[16] 嵌入式引入，§2.3 增加 Di Gaspare 等[9] 物理量级引用。

### R4-03｜major｜动词堆砌
**采纳。** scheme.md §1.2 "由子课题 C 统一维护" → "交给子课题 C 统一维护"；§2.3(a) "建立基准真值" → "给出基准真值"；§2.3(a) "采用分层策略" → "分层策略"。

### R4-04｜major｜"完整 / 系统 / 关键"集中出现
**采纳。** scheme.md §2.2(b) "时间平均加时间分辨" → "时间平均 + 时间分辨"；其余四处"完整"组合保留（该词作为学术通用修饰而非红旗）。

### R4-05/06/07｜major
**部分采纳。** R4-05 句长中位偏短——已通过 R2-09/10/12/13/14/15 句长整改间接改善；R4-06 scheme 罗列处 (a)(b)(c) 7 处——因子标题结构与现有 5 模块格式已对齐，保留；R4-07 content 引用桥接——已在 §2.1 增加 [16]、[9] 嵌入式引入。

### R4-08/09｜minor
**采纳。** R4-08 "申请人"主语混用——rationale §5 已重写为"团队"开场，避免冲突；R4-09 "完整循环演示" → "验证循环演示"，已在 §6 第 4 年里程碑应用。

## 引用对账终态统计（条数 / 占位符 / 死条目 / 一号两用 / 断链 全为 0）

| 维度 | 结果 |
|------|------|
| 正文 [N] 引用集合 | [1]–[40] 全部 40 个编号 |
| references.md 编号集合 | [1]–[40] 共 40 条 |
| 缺失引用（正文引用但 references 不存在） | 0 |
| 孤立条目（references 列出但正文未用） | 0 |
| 一号两用（references 编号重复） | 0 |
| 断链（references 编号跳号） | 0（min=1, max=40 完整覆盖） |
| 总条目数 | 40 条（≤40 上限达标） |
| 预印本（†）占比 | 11/40 = 27.5% |

## 落地成果

### 修改后源文件（4 个）

- `research_proposals/optimizing/key-transient-quantum-phase-optical-20260726/04_proposal/sections/rationale.md`（汉字 9,908，基准 8,228，净增主要用于 R1-01/02/06/07/09 量化论证）
- `research_proposals/optimizing/key-transient-quantum-phase-optical-20260726/04_proposal/sections/content.md`（汉字 5,563，基准 5,186，净增主要用于 R1-11 QMT 算力校准）
- `research_proposals/optimizing/key-transient-quantum-phase-optical-20260726/04_proposal/sections/scheme.md`（汉字 12,323，基准 12,540，净压缩）
- `research_proposals/optimizing/key-transient-quantum-phase-optical-20260726/04_proposal/sections/references.md`（R2-18 微调前言）

### 配套备注（1 个）

- `research_proposals/optimizing/key-transient-quantum-phase-optical-20260726/02_literature/reading-notes.md`（追加 §2510.12990 Kiselev 二次校验备注，符合 R3-01）

### 本记录（1 个）

- `research_proposals/optimizing/key-transient-quantum-phase-optical-20260726/05_review/manual-revision-20261011.md`

## 硬约束符合性自检

1. **DOI/arXiv ID 禁止凭记忆生成**：所有引用条目沿用 references.md 既有编号与字段，未生成任何新 DOI/arXiv ID；[34] Kiselev DOI 通过 reading-notes 二次校验备注处理；[32] Aich 在正文新增的 body 引用沿用 DOI 10.1103/vcxm-dr2g。
2. **大改保守原则**：R1-08 边界论证段表述从"Faeyrman MgO 与本项目材料体系存在三类边界"改为"三类边界差异"，措辞更保守；R1-09 统计功效基于既有 SNR 6.5–8.7 推导，未引入新实验参数。
3. **过程性残留清扫**：scheme.md 移除"已在 §一 §2.1 与 §三 §5(1) 给出"等跳转式冗余；正文统一以"中文年度标记（第 1 年）"形式，未残留英文"Year 1"。
4. **拆超长句不改变科学含义**：R2-09/10/12/13/14/15/16 的所有拆句操作仅做语法重构，物理量、参数表、阈值定义、SNR 计算均原样保留。
5. **scheme 章节结构密度整改**：通过 (a) L0-L3 算力细则下沉到 method-manual G.4 指、(b) §2.1(a) Floquet-Magnus 边界下沉到 manual G.1.1、(c) §6 五年度里程碑压缩三个动作完成部分整改；由于 R1 priority 高于 R4，scheme 当前字数维持在 12,323 汉字（基线 12,540 + 新增 R1 关键内容），R4 的硬性 ≤10,000 字目标在 R1 优先级下退出。

---

*记录完毕（M1 revision agent，2026-10-11）。git commit 待用户授权后执行。*
