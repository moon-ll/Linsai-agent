# 课题说明

**课题名称**：（1）莫尔超晶格的强场响应理论
**项目类型**：面上项目
**课题 ID**：`general-moire-strong-field-probe-20260726`
**当前状态**：待校验（等待人工核验）
**启动日期**：2026-07-26
**最后更新**：2026-08-03

---

## 核心问题
（待管线生成）

## 创新点
研究方案与技术路线
3.1 总体技术路线
3.2 R1：莫尔体系强场响应的有效理论模型
1. **TDDFT 参数标定（最小原胞）**。仅在均匀极限（单层原胞，~10² 原子）下用 TDDFT 计算单层能带、跃迁偶极矩与有效质量，标定下游紧束缚模型的跃迁参数 t、 onsite 能量 ε、以及 SBE 所需的偶极矩阵元 d_nm(k)。此步计算量在团队现有资源内（详见计算资源账本，方法学手册 §3B.3）。
2. **连续莫尔紧束缚模型 + SBE（莫尔尺度）**。将标定参数注入连续莫尔哈密顿量 H_Moiré(θ)（θ 为扭转角），在莫尔布里渊区用 SBE 求解强场电子动力学。该步避免了全原胞 TDDFT 的 >10⁴ 原子灾难，计算尺度为莫尔 mini-布里渊区（~10²–10³ k 点），是本项目理论计算的主力。SBE 框架已由团队在 ZnO/MgO 体系中验证（偶次谐波偏振旋转角复现偏差 < 6%，见前期工作基础），迁移到莫尔体系属增量开发。**国际方法学背书**："光场驱动 + SBE 求解"被 Zhang/Su/Wang 2024 综述 [CITE:zhang_su_wang_nat_mater_2024] 列为莫尔非线性计算的标准方法之一；SBE + Floquet 在单层 MoS₂ 的可行性已被 Xu/Zhou 2024 [CITE:xu_zhou_npj_qm_2024] 用多带紧束缚 + 周期场求解证明；HHG 反演 → SBE 正问题求解的母方法学路径已被 Hu/Meng 2024 PNAS [CITE:hu_meng_pnas_2024] 验证。三者形成"SBE 在 MoS₂ 单层 → 莫尔 + SBE + Floquet"的方法学迁移链条。

---

## 优化历史
| 轮次 | 分数 | 问题数 | high问题 | 时间 |
|------|------|--------|---------|------|
| 1 | 0.31 | 6 | 5 | 2026-07-27 |
| 2 | 0.34 | 13 | 3 | 2026-07-27 |
| 3 | 0.55 | 23 | 10 | 2026-07-27 |
| 4 | 0.52 | 19 | 8 | 2026-07-27 |
| 5 | 0.40 | 13 | 6 | 2026-07-27 |
| 6 | 0.35 | 17 | 7 | 2026-07-28 |
| 7 | 0.00 | 0 | 0 | 2026-07-30 |
| 1 | 0.54 | 40 | 27 | 2026-08-03 |
| 2 | 0.47 | 38 | 11 | 2026-08-03 |
| 3 | 0.65 | 61 | 22 | 2026-08-03 |
| 4 | 0.78 | 13 | 6 | 2026-08-03 |
| 5 | 0.72 | 1 | 0 | 2026-08-03 |

## 状态流转
- 2026-07-26: — → drafts (注册新 proposal)
- 2026-07-26: drafts → optimizing (批量确认思路可行，进入优化)
- 2026-07-29: optimizing → pending_review (连续3轮无显著提升（已通过0/4模块）)
- 2026-07-30: pending_review → archived (人工审核通过: approve)
- 2026-07-30: archived → pending_review (测试后恢复)
- 2026-07-30: pending_review → optimizing (人工审核退回(major_revision)，携带结构化意见)
- 2026-07-30: optimizing → pending_review (连续3轮无显著提升（已通过0/8模块）)
- 2026-07-30: pending_review → archived (测试通过)
- 2026-07-30: archived → pending_review (恢复测试状态)
- 2026-07-30: pending_review → optimizing (人工审核退回(major_revision)，携带结构化意见)
- 2026-07-30: optimizing → pending_review (恢复为待审核状态)
- 2026-07-30: pending_review → archived (测试归档并同步知识库)
- 2026-07-30: archived → pending_review (恢复测试状态)
- 2026-07-30: pending_review → archived (人工审核通过: approve)
- 2026-07-30: archived → pending_review (恢复为待审核状态)
- 2026-07-31: pending_review → optimizing (人工审核退回(major_revision)，携带结构化意见)
- 2026-08-03: optimizing → pending_review (达到最大轮数5（已通过0/5模块）)

## 人工审核记录
- 第1次审核: major_revision（1个问题）
- 第2次审核: major_revision（1个问题）
- 第3次审核: major_revision（1个问题）

---

## 课题产物索引
- `01_direction/` — 方向校准
- `02_literature/` — 文献调研 + 针对性检索
- `02_topic/` — 缺口分析
- `03_question/` — 科学问题框架
- `04_proposal/proposal-draft.md` — 申请书正文
- `04_proposal/methodology-manual.md` — 方法学手册（细节）
- `05_review/` — 终审 + 对抗评审（critic-round-N.md）
- `06_feedback/` — 人工反馈记录
