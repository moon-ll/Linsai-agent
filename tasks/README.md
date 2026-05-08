# tasks/ — 工作项与项目管理

本目录存放用户与林赛协作过程中的任务追踪。

## 目录结构

```
tasks/
├── active/       # 进行中任务
├── backlog/      # 待办任务
└── completed/    # 已完成任务
```

## 任务文件格式

每个任务一个 JSON 文件：

```json
{
  "task_id": "task_001",
  "title": "设计固体HHG实验光路",
  "description": "...",
  "status": "active",
  "priority": "high",
  "created_at": "2026-05-08T09:00:00Z",
  "deadline": "2026-05-15T23:59:59Z",
  "related_sessions": ["20260508-固体HHG实验方案"],
  "subtasks": [
    {"id": "sub_001", "title": "...", "status": "completed"}
  ],
  "notes": "..."
}
```

## 状态流转

```
backlog → active → completed
     ↓
   paused
```

---

*版本：1.0*
*日期：2026-05-08*
