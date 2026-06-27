# memory/ — 长期记忆与上下文

本目录存放跨会话的长期记忆数据。

## 文件说明

| 文件 | 说明 |
|------|------|
| `user-profile.json` | 用户画像：研究领域、偏好、习惯、已知技能、与林赛的互动历史 |
| `working-context.json` | 当前工作上下文：进行中的项目、关键决策、待办事项 |
| `long-term-memory.json` | 跨会话记忆索引：会话摘要、记忆片段目录 |
| `autonomy-level.json` | 自主级别配置：observe（仅记录）/ suggest（建议，默认）/ act（直接执行） |
| `learning-config.json` | 自主学习配置：策略（保守/平衡/激进）、成本阈值、开关 |
| `learning-cost.json` | 学习成本追踪：日/月 Token 配额与累计消耗 |
| `llm-config.json` | LLM 路由配置：模型优先级与降级策略 |
| `sync-state.json` | 多端同步状态：hermes 会话/文献同步进度 |
| `reflow-state.json` | 认知回流状态：已处理会话、增量回流断点 |
| `project-dispatch.json` | 项目总控状态：意见与执行追踪持久化（v3.3.0） |
| `paper-pool.json` | 论文池：待精读/已读论文队列 |
| `paper-feedback.json` | 论文反馈：用户对论文的评价记录 |
| `nsfc-decisions.json` | NSFC 决策记录：基金申请相关关键决策 |
| `alias-candidates.json` | 别名候选：从对话学习、待审核的同义词 |
| `chat-archive-index.json` | 聊天归档索引：历史会话检索元数据 |
| `snippets/` | 记忆片段目录：存储具体的 YAML Front Matter + Markdown 记忆内容 |
| `usage/` | Token 用量统计目录：按日统计用量，含 `usage.json` |

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

*版本：3.5.0*  
*日期：2026-06-27*
