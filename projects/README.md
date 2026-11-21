# projects/ — 课题指导模块数据目录

本目录存放 v3.5 课题指导模块的全部数据，由 `scripts/project_manager.py` 等模块自动管理，一般无需手动编辑。

## 目录结构

```
projects/
├── {project_id}.json          # 课题元数据（状态、标题、单元引用、时间戳）
└── {project_id}/              # 课题工作目录（每个课题一个子目录）
    ├── PROJECT-MEMORY.md      # 核心记忆（≤100 行，自动压缩）
    ├── units/                 # 单元（含验收标准数组 / 风险 / 任务引用）
    ├── kb/                    # 分层知识库（raw / parsed / summary）
    └── memory/                # 课题记忆（对话存档 / 片段 / 决策 / 风险）
```

## 说明

- **课题元数据**：`{project_id}.json` 记录课题标题、状态机状态（planning → active → paused/completed）、关联单元、创建与更新时间。
- **课题工作目录**：`{project_id}/` 存放该课题的全部工作产物。
  - `PROJECT-MEMORY.md`：核心记忆，控制在 100 行以内，超限时由 `project_manager.py` 自动压缩。
  - `units/`：单元定义，每个单元含结构化验收标准数组、风险追踪、交付物与状态机（planning → executing → review → completed）。
  - `kb/`：课题分层知识库，分为 raw（原始材料）/ parsed（解析结果）/ summary（摘要）三层，支持 TF-IDF 倒排索引与标签。
  - `memory/`：课题三级记忆——对话全文存档、记忆片段、核心记忆，以及决策记录与风险记录。
- **自动管理**：所有数据由 `project_manager.py`、`unit_manager.py`、`project_kb.py`、`project_memory.py`、`project_context.py`、`project_workflow.py` 协同维护，请勿手动修改文件结构。

## 数据安全

- 课题数据属于用户工作产物，本地存储，不上传。
- 升级或迁移前请先用 `scripts/backup_manager.py` 备份。

---
*版本：3.5.0*
*日期：2026-06-27*
