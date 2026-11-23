# 课题说明

**课题名称**：量子光场驱动固体高次谐波产生：BSV-HHG 作为多体态探针的理论与实验验证
**项目类型**：面上项目
**课题 ID**：`general-bsv-driven-hhg-quantum-20260726`
**当前状态**：待校验（等待人工核验）
**启动日期**：2026-07-26
**最后更新**：2026-11-16

---

## 核心问题
（待管线生成）

## 创新点
2.6 预期研究成果
2.7 关键科学问题
3.1 总体技术路线
3.2 分方案一：BSV 光源构建与同平台经典光对照
3.3 分方案二：四类对照体系谱学测量与 SBE-Q 理论建模

---

## 优化历史
| 轮次 | 分数 | 问题数 | high问题 | 时间 |
|------|------|--------|---------|------|
| 1 | 0.84 | 8 | 2 | 2026-11-05 |
| 2 | 0.89 | 0 | 0 | 2026-11-05 |
| 1 | 0.80 | 8 | 4 | 2026-11-09 |
| 1 | 0.81 | 8 | 2 | 2026-11-09 |
| 1 | 0.81 | 4 | 1 | 2026-11-09 |
| 1 | 0.75 | 9 | 1 | 2026-11-09 |
| 1 | 0.62 | 16 | 6 | 2026-11-09 |
| 2 | 0.84 | 8 | 1 | 2026-11-10 |
| 2 | 0.82 | 7 | 2 | 2026-11-10 |
| 2 | 0.83 | 8 | 3 | 2026-11-10 |
| 2 | 0.79 | 0 | 0 | 2026-11-10 |
| 2 | 0.77 | 10 | 1 | 2026-11-10 |
| 2 | 0.64 | 14 | 4 | 2026-11-10 |
| 3 | 0.84 | 8 | 0 | 2026-11-12 |
| 3 | 0.82 | 8 | 2 | 2026-11-12 |
| 3 | 0.81 | 8 | 3 | 2026-11-12 |
| 3 | 0.80 | 8 | 1 | 2026-11-12 |
| 3 | 0.79 | 5 | 1 | 2026-11-16 |
| 3 | 0.67 | 12 | 5 | 2026-11-16 |

## 状态流转
- 2026-07-26: — → drafts (注册新 proposal)
- 2026-07-26: drafts → optimizing (批量确认思路可行，进入优化)
- 2026-07-30: optimizing → pending_review (测试反馈)
- 2026-07-30: pending_review → optimizing (人工审核退回(major_revision)，携带结构化意见)
- 2026-07-30: optimizing → pending_review (连续3轮无显著提升（已通过0/8模块）)
- 2026-07-31: pending_review → optimizing (人工审核退回(major_revision)，携带结构化意见)
- 2026-08-03: optimizing → pending_review (健康检查退回优化（补充记录）)
- : pending_review → optimizing (健康检查退回优化（补充 transition 记录）)
- 2026-08-12: optimizing → pending_review (达到最大轮数8（已通过2/5模块）)
- 2026-08-15: pending_review → optimizing (人工审核退回(major_revision)，携带结构化意见)
- 2026-08-24: optimizing → pending_review (连续3轮质量下降，暂停自动优化)
- 2026-08-29: pending_review → optimizing (修复退回：08-24 误判（连续3轮质量下降暂停）由评分解析缺陷所致——critic 报告粗体得分单元格 **0.70**/**0.85** 被误读为权重列 0.50，references 真实分 0.78 被记 0.50（v6.9.78 修复；且 references 2维口径已不参与下降判定）。)
- 2026-10-05: optimizing → pending_review (达到最大轮数8（已通过1/5模块）)
- 2026-10-09: pending_review → optimizing (人工验收裁决退回（按预审 reject_lean）：R8 逃生阀晋级但仅参考文献 1/5 模块过线，rationale/content 0.75、scheme 0.73、full_review 0.77 均低于 0.85 达标线，R7→R8 四模块零提升显示旧评分锚下优化已停滞。第二遍重点：按 rigor 五项清单重定靶，检查 BSV 驱动机制的数值链与指标可操作性。)
- 2026-11-01: optimizing → pending_review (引擎亲审通过自动晋级（v7.2.0 否决窗口开启）)
- 2026-11-02: pending_review → optimizing (人工审核退回(major_revision)，携带结构化意见)
- 2026-11-03: optimizing → pending_review (引擎亲审通过自动晋级（v7.2.0 否决窗口开启）)
- 2026-11-04: pending_review → optimizing (人工审核退回(major_revision)，携带结构化意见)
- 2026-11-16: optimizing → pending_review (连续3轮质量下降，暂停自动优化)

## 人工审核记录
- 第2次审核: major_revision（6个问题）
- 第3次审核: major_revision（7个问题）
- 第4次审核: major_revision（7个问题）
- 第8次审核: major_revision（2个问题）
- 第9次审核: major_revision（1个问题）

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
