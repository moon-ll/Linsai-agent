# sessions/ — 对话会话存档

本目录存放用户与林赛的对话历史。

## 目录命名规则

每个会话一个子目录：
```
sessions/
└── YYYYMMDD-会话主题/
    ├── messages.json    # 完整消息日志
    ├── state.json       # 会话状态（主题、模式、起止时间）
    └── summary.md       # 会话摘要（自动或手动生成）
```

## 文件格式

### messages.json

```json
[
  {
    "msg_id": "msg_001",
    "role": "user",
    "content": "...",
    "timestamp": "2026-05-08T09:00:00Z",
    "mode": "co-working"
  },
  {
    "msg_id": "msg_002",
    "role": "assistant",
    "content": "...",
    "timestamp": "2026-05-08T09:01:00Z",
    "mode": "co-working"
  }
]
```

> 注：`context_builder.py` 兼容读取纯列表和字典（`{"messages": [...]}`）两种格式。

### state.json

```json
{
  "session_id": "20260508-固体HHG实验方案",
  "topic": "固体HHG实验方案设计",
  "mode": "co-working",
  "status": "active",
  "created_at": "2026-05-08T09:00:00Z",
  "last_active": "2026-05-08T10:30:00Z",
  "message_count": 15
}
```

### mode 定义

| mode | 说明 |
|------|------|
| `co-working` | 并肩工作模式（默认） |
| `deep-talk` | 深度对话模式 |
| `quick-check` | 快速验证模式 |
| `proactive` | 主动感知触发的会话 |

---

*版本：1.0*
*日期：2026-05-08*
