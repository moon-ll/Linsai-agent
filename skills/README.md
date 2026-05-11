# 林赛技能系统

> 存放林赛的可复用能力模块。每个技能一个目录，内含 `SKILL.md`。

## SKILL.md 格式规范

```markdown
# 技能名称

## 触发条件
用户输入包含以下关键词任一：关键词1、关键词2、关键词3

## 上下文注入
激活此技能时，追加到 system prompt 的上下文。
说明林赛在此场景下应遵循的原则、方法和禁忌。

## 工作流
可选。描述此技能的标准工作流步骤。
```

## 激活机制

1. `context_builder.py` 在组装 prompt 时，调用 `skill_manager.match_skills(user_input)`
2. 命中技能后，将对应技能的【上下文注入】文本追加到 system_prompt
3. 技能上下文参与预算分配，超限时自动截断

## 现有技能

| 技能 | 触发词 | 用途 |
|------|--------|------|
| `math-derivation` | 推导、证明、公式、方程、量纲 | 数学推导辅助 |
| `code-review` | 代码、review、bug、优化、重构 | 代码审查与建议 |
| `experiment-design` | 实验、方案、光路、设计、搭建 | 实验方案设计 |
| `literature-distill` | 文献、论文、精读、PRL、Nature、综述 | 文献精读与知识蒸馏 |
| `hpc-computing` | 服务器、PBS、提交、计算、集群、qsub | HPC 计算工作流 |
| `project-planning` | 项目、计划、分解、里程碑、roadmap | 项目拆解与规划 |
| `agora-meeting` | 讨论、开会、Agora、历史人物、对话 | 多人物会议主持 |
