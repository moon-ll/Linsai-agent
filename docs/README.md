# docs/ — 项目文档与报告

本目录存放 LinSai-CoPilot 的项目级文档、评估报告和 prompt 模板。

## 文件清单

| 文件 | 说明 |
|------|------|
| `IMPLEMENTATION-PLAN-v2.1.0.md` | 工具型协作者实现计划（当前有效） |
| `IMPLEMENTATION-PLAN-v3.0.0.md` | 旧版计划（已废弃）：方向已重构 |
| `DEEP-AUDIT-REPORT-v1.7.2.md` | 深度评估报告（历史归档） |
| `FUNCTIONAL-TEST-REPORT-v1.7.2.md` | 功能测试报告（历史归档） |
| `CLAUDE-CLI-ADMIN.md` | Claude CLI 人工管理指南 |
| `prompts/` | LLM prompt 模板（质量审查/维护审查/概念合并/论文精读） |

## 使用规范

- 文档使用 Markdown 格式
- 报告类文档包含：测试方法、结果数据、结论建议
- prompt 模板独立存放，便于版本管理和复用
- 废弃文档请在文件名加 `(废弃)` 前缀或移入 `archived/`
