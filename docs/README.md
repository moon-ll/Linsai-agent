# docs/ — 项目文档与报告

本目录存放 LinSai-CoPilot 的项目级文档、评估报告和 prompt 模板。

## 维护约定（v6.9.29 瘦身）

- 只保留**权威/活跃**文档；已实现或已废弃的旧版计划与报告一律移入 `archive/`，避免文档堆积。
- 架构细节以 `ARCHITECTURE.md` 为准，规则以 `AGENTS.md` 为准，评分标准以 `memory/nsfc-standards.json` 为准。
- 脚本逐文件清单由 `scripts/README.md` 维护，不在 docs/ 重复。

## 文件清单

| 文件 | 说明 |
|------|------|
| `WORKBENCH-ARCHITECTURE.md` | ★ v8 设计纲领（课题启动包生产链/验收标准/迁移/清理，AGENTS.md 引用） |
| `ARCHITECTURE.md` | v8 架构说明（AGENTS.md 指向的权威架构文档，已重写为工作台架构） |
| `PROJECT-STRUCTURE.md` | 目录结构（v8：research_topics 新域 + legacy 归档） |
| `SKILL-ARCHITECTURE.md` | skill 层说明（v8 消费方：深研链 3 skill 在用） |
| `DATA-FLOW-MAP.md` | 数据流动路径图谱（v7 时代快照，文献链部分仍有效） |
| `score-distribution-20260828.html` | 历史评分分布（v7 优化环产物，存档） |
| `prompts/` | LLM prompt 模板（质量审查/维护审查/概念合并/论文精读） |
| `archive/` | 历史文档归档（已实现/已废弃的旧版计划与报告） |

## archive/ — 历史文档归档

保留已完成使命的旧版设计文档与评估报告，以便追溯项目演进轨迹。

| 文件 | 说明 |
|------|------|
| `CHANGELOG-archive-v6.0-v6.7.md` | 变更记录归档（v6.7.7 及更早） |
| `FRAMEWORK-ARCHITECTURE.md` | 框架架构总览（v6.8.9 快照，已被 ARCHITECTURE.md 取代） |
| `SCORING-STANDARDS.md` | 评分标准（v6.8.9 快照，达标线已过期，以 nsfc-standards.json 为准） |
| `FEATURE-PLAN.md` | 开发计划（P1 研究设想质量门槛已完成 v6.8.26） |
| `linsai-orchestrator-design.md` | 林赛总控设计稿（v6.7，已实现） |
| `CLAUDE-CLI-ADMIN.md` | Claude CLI 人工管理指南（2026-05，工具手册） |
| `deepxiv-knowledge-workflow.md` | deepxiv 知识库流水线设计（v6 时代，已被多源检索取代） |
| `unified-state-sync-design.md` | 论文统一状态总线设计（v4.2 设计稿，部分实现） |
| `IMPLEMENTATION-PLAN-v2.1.0.md` | 工具型协作者实现计划（已实现） |
| `IMPLEMENTATION-PLAN-v3.0.0.md` | 旧版计划（已废弃，方向已重构） |
| `DEEP-AUDIT-REPORT-v1.7.2.md` | 深度评估报告（历史归档） |
| `FUNCTIONAL-TEST-REPORT-v1.7.2.md` | 功能测试报告（历史归档） |
| `briefing-sync-design.md` | 文献简报同步设计（已实现） |
| `cognitive-loop-plan.md` | 认知闭环设计稿（v3.4，已实现） |
| `kb-smart-management-plan.md` | 知识库智能管理计划（已实现） |
| `project-assessment-v4.md` | 项目评估报告（v4，历史归档） |
| `stability-ux-plan.md` | 稳定性与 UX 优化计划（v3.3，已实现） |
| `v5-three-tier-unification-plan.md` | 三端统一架构策划书（v5，已实现） |

## 使用规范

- 文档使用 Markdown 格式
- 报告类文档包含：测试方法、结果数据、结论建议
- prompt 模板独立存放，便于版本管理和复用
- 废弃文档移入 `archive/`，避免污染主目录
- CHANGELOG 主文件只保留当前大版本（v6.9.x），旧版本切至 `archive/CHANGELOG-archive-*.md`
