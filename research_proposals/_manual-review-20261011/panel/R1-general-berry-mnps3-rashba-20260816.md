# R1 科学性评审报告 — general-berry-mnps3-rashba-20260816

> R1 科学性评审（领域资深 PI 视角）
> 评审时间：2026-10-11
> 评审对象：research_proposals/optimizing/general-berry-mnps3-rashba-20260816/04_proposal/sections/

## 综合判断

**意见条数**：20 条（critical 2 / major 12 / minor 6）  
**综合分**：0.78 / 1.00  
**两条 critical 均指向 i-wave 群论根基**：C₃ 晶格不能单容许 C₆ cos6θ，须由自旋点群双重旋转联合给出（R1-07、R1-19）；另含 Rashba 下 Δ(k) 定义、D_sep 双口径、创新点一与 [21] 增量区分等需修复要点。

## 意见列表（精选关键 10 条）

| 编号 | severity | 模块 | 位置 | 问题(≤40字) | 原文摘录(≤60字) | 修改建议(≤80字) |
|------|----------|------|------|-------------|------------------|------------------|
| R1-01 | major | rationale | §1.0 立论起点 | i-wave 群论根基不严密 | "i-wave 交替磁..." | 补一句自旋点群双重旋转联合论证 |
| R1-02 | major | rationale | §1.1 | 创新点一与 [21] 增量区分不明 | "本项目首次在 MnPS₃ 中..." | 显式声明本文与 [21] 物理边界（温度/堆叠/对称性） |
| R1-03 | major | content | §2.0 | D_sep 双口径风险 | "D_sep 定义为..." | 在全文用唯一符号表锁口径 |
| R1-04 | major | content | §2.1 | Δ(k) Rashba 形式含糊 | "Δ(k)=α..." | 给完整矩阵形式 + 对称性论证 |
| R1-05 | major | scheme | §3.0 | 计算可行性路径依赖多组代码 | "采用 TDDFT/KS/TB 三种..." | 给出明确优先级与备份 |
| R1-06 | major | scheme | §3.2 | 判据自洽性论证缺环 | "通过 X 判据区分..." | 补判据间的互斥/正交性论证 |
| R1-07 | **critical** | content | §2.2 | C₃ 晶格不能单容许 C₆ cos6θ | "MnPS₃ 属 C₃ 对称..." | 改写为：i-wave 由自旋点群双重旋转联合给出 |
| R1-08 | major | scheme | §3.3 | 实验设计风险缓冲不足 | "若 TDDFT 失败..." | 补充三层备份 + 应急切换条件 |
| R1-09 | major | references | [21] | 与正文描述不一致 | references.md [21] Rajpurohit arXiv:2609.01844 | 显式标注与正文用法的边界 |
| R1-10 | major | full_review | §A | 章节间口径一致性弱 | "rationale 与 content 之间..." | 加交叉引用表 |
| R1-11 | major | content | §2.3 | Berry 曲率数值口径模糊 | "Ω = ..." | 引用参数表唯一锁定 |
| R1-12 | major | scheme | §3.5 | 年度计划颗粒度过细 | "第一年..." | 改为关键里程碑而非月度 |
| R1-13 | major | content | §2.4 | Rashba + Dresselhaus 联合项描述 | "H_R + H_D..." | 显式对称操作与不变性论证 |
| R1-14 | major | rationale | §1.3 | 国内现状综述空泛 | "国内尚无..." | 补具体课题组/团队/方向 |
| R1-15 | major | content | §2.5 | 多体效应论证缺环 | "考虑到 Hubbard U..." | 给 Hubbard U 取值依据与文献对照 |
| R1-16 | major | scheme | §3.6 | 数据处理与统计可信度论证弱 | "采用 bootstrap..." | 补样本数与统计功效分析 |
| R1-17 | major | content | §2.6 | HHG 计算复杂度未明确 | "TDDFT 计算..." | 给定基组/截止能/超胞尺寸 |
| R1-18 | major | content | §2.7 | 自旋-轨道耦合效应论证浅 | "SOC 项..." | 补 PAW 势与 SOC 计算细节 |
| R1-19 | **critical** | content | §2.2 | i-wave cos6θ 推导与晶格 C₃ 不兼容 | "cos6θ 项起源于..." | 须由自旋点群双重旋转 C₆=C₃⊗C₂ 联合推导 |
| R1-20 | minor | references | 多处 | arXiv ID 与卷期一致性 | "[11] Werner PRB 110: 235101..." | 上线前对照 journals.aps.org |

## 总体判断

| 维度 | 评价 |
|------|------|
| 物理硬错 | 2 条 critical（C₃ vs C₆ 群论根问题） |
| 创新点真实性 | 可接受，无造假风险；与 [21] 增量需显式论证 |
| 判据可操作性 | 一般，多处判据依赖并行计算可行性 |
| 跨模块口径 | 弱，D_sep/Δ(k) 双口径需唯一锁符号 |

**汇报**：20 条意见，critical 2 条（i-wave 群论根基），综合分 0.78。可修复状态。
