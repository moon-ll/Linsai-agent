# scripts/archive/ — 一次性脚本归档

本目录存放已完成历史使命的一次性脚本。这些脚本仍可通过 `python3 scripts/archive/<name>.py` 运行，但不再在根目录中碍眼。

| 脚本 | 归档日期 | 原用途 |
|------|---------|--------|
| `migrate_literature_unified.py` | 2026-08-12 | v6.8.0 文献统一架构数据迁移（已完成） |
| `migrate_sections_v680.py` | 2026-08-12 | v6.8.0 章节结构 7→5 模块迁移（已完成） |
| `kb_health_repair.py` | 2026-08-12 | 知识库特定重复论文修复（一次性修复，已完成） |
| `repair_frontmatter.py` | 2026-08-12 | 外部工具导致的 YAML frontmatter 类型损坏修复（已完成） |

> 归档原则：数据迁移已完成、修复目标已达成、无外部代码 import 依赖的脚本。
> 如需重新使用，直接运行即可，不影响功能。
