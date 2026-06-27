# docs/ — 项目文档与报告

本目录存放 LinSai-CoPilot 的项目级文档、评估报告和 prompt 模板。

## 文件清单

| 文件 | 说明 |
|------|------|
| `CLAUDE-CLI-ADMIN.md` | Claude CLI 人工管理指南 |
| `deepxiv-knowledge-workflow.md` | deepxiv 知识库流水线设计文档（v6） |
| `cognitive-loop-plan.md` | v3.4 认知闭环设计稿 |
| `kb-smart-management-plan.md` | 知识库智能管理计划 |
| `stability-ux-plan.md` | v3.3 稳定性与用户体验优化计划 |
| `prompts/` | LLM prompt 模板（质量审查/维护审查/概念合并/论文精读） |
| `archive/` | 历史版本文档归档（见下方说明） |

## archive/ — 历史版本文档归档

本子目录存放已完成其历史使命、不再作为当前参考依据的版本计划与评估报告，保留以便追溯项目演进轨迹。

| 文件 | 说明 |
|------|------|
| `IMPLEMENTATION-PLAN-v2.1.0.md` | 工具型协作者实现计划（已实现，历史归档） |
| `IMPLEMENTATION-PLAN-v3.0.0.md` | 旧版计划（已废弃）：方向已重构 |
| `DEEP-AUDIT-REPORT-v1.7.2.md` | 深度评估报告（历史归档） |
| `FUNCTIONAL-TEST-REPORT-v1.7.2.md` | 功能测试报告（历史归档） |

## 使用规范

- 文档使用 Markdown 格式
- 报告类文档包含：测试方法、结果数据、结论建议
- prompt 模板独立存放，便于版本管理和复用
- 废弃文档请在文件名加 `(废弃)` 前缀或移入 `archive/`
- 固体 HHG 等领域调研材料归入 `knowledge/raw/notes/`，不再存放于本目录
