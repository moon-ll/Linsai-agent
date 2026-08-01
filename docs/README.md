# docs/ — 项目文档与报告

本目录存放 LinSai-CoPilot 的项目级文档、评估报告和 prompt 模板。

## 文件清单

| 文件 | 说明 |
|------|------|
| `CLAUDE-CLI-ADMIN.md` | Claude CLI 人工管理指南 |
| `deepxiv-knowledge-workflow.md` | deepxiv 知识库流水线设计文档（v6） |
| `unified-state-sync-design.md` | 论文统一状态总线设计文档（v5） |
| `linsai-orchestrator-design.md` | 林赛总控设计文档（v6.7） |
| `prompts/` | LLM prompt 模板（质量审查/维护审查/概念合并/论文精读） |
| `archive/` | 历史版本文档归档（已实现/已废弃的旧版计划与报告） |

## archive/ — 历史文档归档

保留已完成使命的旧版设计文档与评估报告，以便追溯项目演进轨迹。

| 文件 | 说明 |
|------|------|
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
