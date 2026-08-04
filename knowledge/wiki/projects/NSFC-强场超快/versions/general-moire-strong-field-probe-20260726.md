---
title: "莫尔超晶格强场探针 — 最新版本"
type: "proposal_version"
proposal_id: "general-moire-strong-field-probe-20260726"
project_type: "general"
latest_round: 6
last_score: 0.72
status: "optimizing"
created: "2026-08-04T08:30:27Z"
updated: "2026-08-04T08:30:27Z"
project: ["NSFC-强场超快"]
growth_stage: "growing"
confidence: 1.0
---

# 莫尔超晶格强场探针 — 最新版本

**课题 ID**：`general-moire-strong-field-probe-20260726`
**类型**：general
**最新轮次**：第 6 轮
**当前分数**：0.72
**状态**：优化中
**同步时间**：2026-08-04T08:30:27Z

---

## 章节概览

| 章节 | 标题 | 行数 |
|------|------|------|
| content | content | 95 |
| full_review | full_review | 131 |
| rationale | rationale | 56 |
| references | references | 144 |
| scheme | scheme | 54 |

## 课题简介

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
2. **连续莫尔紧束缚模型 + SBE（莫尔尺度）**。将标定参数注入连续莫尔哈密顿量 H_Moiré(θ)（θ 为扭转角），在莫尔布里渊区用 SBE 求解强场电子动力学。该步避免了全原胞 TDDFT 的 >10⁴ 原子灾难，计算尺度为莫尔 mini-布里渊区（~10²–10³ k 点），是本项目理论计算的主力。SBE 框架已由团队在 ZnO/MgO 体系中验证（偶次谐波偏振旋转角复现偏差 < 6%，见前期工作基础），迁移到莫尔体系属增量开发。**国际方法学背书**："光场驱动 + SBE 求解"被 Zhang/Su/Wang 2024 综述 [CITE:zhang_su_wang_nat_mater_2024] 列为莫尔非线性计算的标准方法之一；SBE + Floquet 在单层 MoS₂ 的可行性已被 Xu/Zhou 2024 [CITE:xu_zhou_npj_qm_2024] 用多带

（完整简介见 [源文件](research_proposals/optimizing/general-moire-strong-field-probe-20260726/04_proposal/proposal-draft-merged.md)）

## 来源

- 最新申请书：[research_proposals/optimizing/general-moire-strong-field-probe-20260726/04_proposal/proposal-draft-merged.md](research_proposals/optimizing/general-moire-strong-field-probe-20260726/04_proposal/proposal-draft-merged.md)
- 各章节文件：`research_proposals/optimizing/general-moire-strong-field-probe-20260726/04_proposal/sections/`
- 优化报告：[reports/general-moire-strong-field-probe-20260726.md](reports/general-moire-strong-field-probe-20260726.md)

> 本页由 `scripts/kb_proposal_reorg.py` 自动生成。