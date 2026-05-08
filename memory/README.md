# memory/ — 长期记忆与上下文

本目录存放跨会话的长期记忆数据。

## 文件说明

| 文件 | 说明 |
|------|------|
| `user-profile.json` | 用户画像：研究领域、偏好、习惯、已知技能、与林赛的互动历史 |
| `working-context.json` | 当前工作上下文：进行中的项目、关键决策、待办事项 |
| `long-term-memory.json` | 跨会话记忆索引：会话摘要、记忆片段目录 |
| `autonomy-level.json` | 自主级别配置：observe（仅记录）/ suggest（建议，默认）/ act（直接执行） |
| `snippets/` | 记忆片段目录：存储具体的 YAML Front Matter + Markdown 记忆内容 |

## user-profile.json 结构

```json
{
  "research_field": "固体高次谐波",
  "known_skills": ["Python", "MATLAB"],
  "preferences": {
    "work_time": "morning"
  },
  "communication_style": {
    "avg_input_length": 120,
    "uses_formulas": false
  },
  "interaction_history": {
    "total_sessions": 5,
    "total_messages": 42
  },
  "last_updated": "2026-05-08T10:00:00Z",
  "_confidence": {
    "research_field": 0.8,
    "known_skills": 0.9
  }
}
```

## working-context.json 结构

```json
{
  "active_projects": [
    {
      "name": "量子轨迹分析",
      "status": "active",
      "last_mentioned": "2026-05-08T10:00:00Z"
    }
  ],
  "pending_decisions": [
    {
      "topic": "用什么数值方法",
      "context": "",
      "deadline": ""
    }
  ],
  "key_insights": [],
  "last_updated": "2026-05-08T10:00:00Z"
}
```

## autonomy-level.json 结构

```json
{
  "level": "suggest",
  "set_at": "2026-05-08T10:00:00Z",
  "notes": "默认级别：检测到信号时向用户建议，不直接执行"
}
```

## 记忆更新策略

- **即时更新**：每轮对话后自动提取关键信息更新用户画像和工作上下文
- **会话摘要**：单会话 >5 条消息时触发摘要生成
- **定期清理**：记忆片段默认 90 天 TTL，超期自动清理
- **隐私边界**：所有记忆数据本地存储，不上传

---

*版本：1.0*  
*日期：2026-05-08*
