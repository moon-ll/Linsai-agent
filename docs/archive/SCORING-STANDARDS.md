# LinSai-CoPilot 提案评分标准（v6.8.9）

> 本文档是**当前有效**的评分与达标标准，是后续评审、修复、看板解读的唯一依据。
> 权威原始数据源：`memory/nsfc-standards.json`（达标阈值/权重/评分完整性规则）与
> `scripts/adversarial/constants.py`（agent 分数/质量门槛系数）、
> `scripts/proposal_lifecycle/constants.py`（逃生阀参数）。
> 修改以上文件即调整全局标准，本文档需同步更新。
> 最后更新：2026-08-07

---

## 1. 评分体系总览（4 层）

一个课题的"质量分"由 4 层机制共同决定，口径务必区分：

| 层 | 主体 | 分数区间 | 含义 |
|----|------|---------|------|
| critic 章节评分 | reviewer profile（critic） | 0-1 | 对申请书某一模块（5 模块之一）的深度评审得分 |
| agent 奖惩分 | monitor 规则层 | 0-150（初始 100） | writer/critic 两个"人格 agent"的长期信誉分，通过对抗质量增减 |
| 达标判定 | 生命周期引擎 | 布尔 | 依阈值判定是否移入 pending_review |
| 程序化天花板 | 代码检测 | 0-1（硬上限） | AI 写作味检测，critic 表达分不得超此上限 |

> 注意：critic 对申请书的评分（0-1）与 critic **agent** 的奖惩分（0-150）是两套并存的数据，勿混淆。

---

## 2. 达标阈值（三类项目）

`memory/nsfc-standards.json → project_types.{type}.quality_threshold`

| 项目 | min_overall_score | max_high_issues | max_medium_issues |
|------|:---:|:---:|:---:|
| general 面上 | **0.90** | 0 | 3 |
| key 重点 | **0.90** | 0 | 2 |
| major 重大 | **0.90** | 0 | 1 |

- 2026-08-06 起达标线统一提高至 **0.90**（原 0.80）。`scripts/adversarial/scoring.py` 中历史 rescore 记录仍写 0.80，属旧版本残影，不以为准。
- 达标线被 `nsfc-standards.json` 覆盖；`proposal_lifecycle/constants.py` 的 `DEFAULT_SCORE_THRESHOLD = 0.90` 为引擎回退默认值。

---

## 3. 维度权重（评估焦点）

`project_types.{type}.evaluation_focus`

| 维度 | general 面上 | key 重点 | major 重大 |
|------|:---:|:---:|:---:|
| 创新性 | 0.30 | 0.25 | 0.15 |
| 可行性 | 0.25 | 0.10 | 0.10 |
| 严谨性 | 0.25 | 0.20 | — |
| 表达质量 | 0.20 | 0.10 | — |
| 系统性 | — | 0.20 | — |
| 战略意义 | — | 0.15 | 0.25 |
| 顶层设计 | — | — | 0.20 |
| 多学科交叉 | — | — | 0.15 |
| 团队实力 | — | — | 0.15 |

综合分 = 各维度分 × 权重之和 / 权重之和（`optimize.py::_recalculate_score`）。

---

## 4. 评分完整性规则

`nsfc-standards.json → general_principles.scoring_integrity_rules`（程序化强制）：

1. **不准虚高**：程序化天花板 < 0.7 时综合分 ≤ 0.75；0.7-0.8 时 ≤ 0.80；0.8-0.9 时 ≤ 0.85。
2. **参考文献轮次**：创新性/可行性标记 N/A，综合分仅由严谨性+完整性等权平均；程序从权重剔除 N/A 并归一化。
3. **禁止纯机械评审**：缺"写作风格评估"与"范本对标"段落 → 评审无效，强制重审。
4. **锚点对比强制**：评审必须含"锚点对比"段落，缺失即无效。
5. **表达天花板强制**：critic 表达分超过程序化天花板则程序强制 cap。
6. **逐条清单**：critic 逐条对照 `section_standards.{section}.enforcement_checklist`，不通过条目 > 3 时该 section 分 ≤ 0.70。
7. **自引用封顶**：全文"详§X/见§X/方法学手册§X" > 10 次表达分扣 0.05，> 15 次扣 0.10。

---

## 5. 程序化表达质量天花板

`programmatic_checks`：`ceiling = 1.0`，逐项检测违规扣减，最低 0.5。

| 检测项 | 阈值 | 每超扣 |
|--------|:---:|:---:|
| AI 关联词（基础上/此外/同时/因此/然而/基于此…） | > 8 | 0.02 |
| 模板句式（为…提供…基础/支撑/途径…） | > 8 | 0.03 |
| 模板主语（本项目拟/将/计划/旨在句首） | > 5 | 0.02 |
| 冗余修饰词（显著/重要/系统/良好/成熟…） | > 12 | 0.01 |
| 超长句（单句 > 120 字） | 每千字 > 1 | 0.02 |
| 元话语（沿着…主线/我们可以辨识/值得注意的是…） | > 2 | 0.03 |
| 加粗过度 | 每千字 > 3 | 0.03 |
| 列表替代论述 | 每处 | 0.05 |

---

## 6. 进入待评审（pending_review）的 3 个条件

`completion.py::_check_done`，5 个模块（rationale/content/scheme/full_review/references）全部"对抗胜利"才算达标：

1. **条件 1（达标）**：5 模块全部通过（分数 ≥ 0.90 且各维度无短板）+ **monitor 独立评分复核通过**。
   - v6.8.9：即使 5 模块全胜，若 monitor 独立评分 < 达标线，**不予流转，继续优化**（防 writer+critic 串通虚高）。
2. **条件 2（逃生阀）**：连续 5 轮无显著提升（`DEFAULT_NO_IMPROVEMENT_LIMIT = 5`）。
3. **条件 3（逃生阀）**：达到最大轮数 8（`DEFAULT_MAX_ROUNDS = 8`）。

> 逃生阀触发时若分数低于达标线，附 `quality_warning` 标记并建议人工审核，但**不阻断**流转（仅 monitor 复核会阻断）。

---

## 7. agent 分数机制（writer/critic，防摆烂）

持久化于 `memory/agent-scores.json`，区间 0-150，初始 100。每轮由 monitor 收尾时更新。

### 7.1 writer 分数构成

```
writer_delta = monitor_delta × 20            # monitor 独立评分变化
            + max(0, 高分问题减少数) × 3      # 实质消解问题
            + 违规扣分                        # 禁止清单
            + writer 质量门槛(monitor_score)  # v6.8.9
```

### 7.2 critic 分数构成

```
critic_delta = monitor上升奖励(×15) + 高分问题检出奖励(×2)
             - monitor回归惩罚(5)
             +_ 违规扣分
             +_ 校准奖励/惩罚（critic分与monitor分误差<0.10 奖 3；>0.20 罚）
             +_ critic 评审质量门槛              # v6.8.9
```

### 7.3 v6.8.9 质量门槛（核心防摆烂）

**writer 质量门槛**（`_writer_quality_gate`）：monitor 评分低说明申请书本身上限低，writer 的"微调式改进"未实质推进质量，不应白拿正分。

| monitor 独立评分 | 额外分 |
|:---:|:---:|
| < 0.50 | **-5**（质量过差，反向抑制） |
| 0.50-0.70 | **-2**（质量欠佳，抑制正奖励） |
| ≥ 0.70 | 0（正常） |

**critic 评审质量门槛**（`_critic_quality_gate`）：要求 critic 严格且准确，评分贴合 monitor 独立判断。

| 情形 | 额外分 |
|------|:---:|
| monitor < 0.60 且 critic 给分 ≥ 0.75（虚高/放水） | **-8** |
| monitor ≥ 0.75 且 critic 给分 < 0.55（过度苛刻/不准确） | **-4** |
| 其余 | 0 |

> 设计意图：writer 必须**实质性提升申请书质量**才能涨分；critic 必须**准确严格评审**（发现真问题、评分贴合 monitor）才能涨分。二者靠工作质量完成对抗，而非摆烂放水。

### 7.4 其他 agent 机制

- **批评家恢复**：critic 分 < 20 且近 5 轮无严重违规，每次 +3。
- **串通惩罚**：collusion_risk medium/high 时，正奖励清零并额外 -5/-10。
- **负反馈告警**：monitor 独立分连续 3 轮下降、writer/critic 连续 3 轮双降、串通连续 2 轮 ≥ medium、全局分 < 50 任一触发 → 暂停自动流转，等待人工介入。
- **低分预警**：课题分 < 0.65（`LOW_SCORE_ALERT_THRESHOLD`）且趋势恶化时标记 `low_score_alert`。

---

## 8. 违规禁止清单（扣分对照）

`constants.py::PROHIBITION_PENALTIES`（关键词兜底见 `scoring.py::_penalty_for_violations`）：

| writer | 扣分 | critic | 扣分 |
|--------|:---:|--------|:---:|
| fabrication 杜撰 | -12 | lazy_review 消极评审 | -10 |
| wrong_citation 错误引用 | -8 | rigid_scoring 僵化评分 | -8 |
| template_rigidity 僵化模板 | -6 | missed_major 遗漏重大问题 | -10 |
| unaddressed_issues 未解决 | -8 | unactionable 不可操作建议 | -6 |
| off_section 越界修改 | -5 | score_content_mismatch 评分矛盾 | -8 |
| placeholder 占位符 | -4 | | |
| surface_change 表面修改 | -5 | | |

关键词兜底：severe/critical → -10，high → -6，禁止/杜撰/伪造 → -12，错误引用 → -8，占位符/TODO → -4，表面修改/零改进 → -5，模板/套话 → -6，消极评审/过短 → -10，未解决/未修复 → -6。

---

## 9. 分数提取方式（v6.8.9 修复）

critic 报告的 markdown 表格可能含权重列：`| 创新性（innovation） | 0.30 | 0.78 |`。

- **历史 bug**：旧正则匹配到行内第一个数字（权重 0.30），导致 score_history 维度分错误地变成 {0.3, 0.25, 0.25, 0.2}（恰好等于权重）。
- **v6.8.9 修复**：`optimize.py::_extract_dimension_scores` 改为取表格行内**最后一个** 0.x 数字作为得分列；若非表格，回退到行内格式（`创新性：0.72` / `创新性 0.72`）。

---

## 10. 一页速查

- 达标线：三类项目统一 **0.90**。
- 逃生阀：连续 5 轮无提升 / 满 8 轮。
- monitor 复核：全模块胜利但 monitor 分 < 0.90 → 不流转，继续优化。
- 低分预警：< 0.65。
- agent 分区间：0-150，初始 100；writer 质量门槛 <0.50 扣 5 / <0.70 扣 2；critic 虚高扣 8 / 过苛扣 4。
- 权威数据源：`memory/nsfc-standards.json`、`scripts/adversarial/constants.py`、`scripts/proposal_lifecycle/constants.py`。