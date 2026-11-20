# 林赛技能库

> 本项目的**可复用能力资产**（三大产出资产之一，2026-09-26 用户裁决）。
> 技能库服务于本项目的课题生产全链路，也可迁移到其它类似项目。

## 两类技能

| 类型 | 位置 | 加载方式 | 用途 |
|------|------|----------|------|
| **管线技能** | `.hermes/skills/<name>/SKILL.md` | hermes agent 会话自动发现（项目本地 trusted 目录）+ CoPilot 管线经 `scripts/skill_loader.py` 按节裁剪注入 | 课题生产链路（writer/critic/researcher/monitor 等 agent 的方法论与标准） |
| **会话技能** | `skills/<name>/SKILL.md` | `skill_manager.match_skills()` 关键词匹配注入对话 system prompt | 1v1 对话场景（数学推导/实验设计/文献讨论等） |

## 管线技能（v7.0.0 起，单一真相源）

| 技能 | 用途 |
|------|------|
| `nsfc-writing` | 申请书写作纪律十节：叙事主线/审计语言映射/纯净性红线/AI 模式修复/自检与检查项 |
| `research-proposal` | 课题方法学：**操作性五问**/方案六要素/设想六模块/质量递进链 |
| `literature-reading` | 结构化阅读法（五维笔记/五要素蒸馏/深读五字段）+ 数值忠实纪律 |
| `method-manual` | 方法学手册维护纪律（唯一真相源/禁追加/判据口径表） |
| `quality-review` | 评审标准：四维锚点法/串通检测/设想四维门槛 |

架构与加载机制详见 `docs/SKILL-ARCHITECTURE.md`。

## SKILL.md 格式规范（管线技能，hermes 原生格式）

```markdown
---
name: 技能名
description: "英文一句话：能力 + 适用场景（供 hermes 语义匹配）"
version: 1.0.0
author: LinSai-CoPilot
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [标签]
---

# 技能标题（中文）

## 一、节标题（CoPilot skill_loader 按 "## 前缀" 提取节注入 prompt）
正文…
```

- 节标题用 `## 中文序号、标题` 格式（加载器按前缀匹配，标题余文不敏感）
- 量化参数（字数区间/评分权重）不写死在 skill 里，引用 `memory/nsfc-standards.json`
- 正反对照样例、自检清单放在独立节，核心红线节控制篇幅（注入预算 4KB）

## SKILL.md 格式规范（会话技能）

```markdown
# 技能名称

## 触发条件
用户输入包含以下关键词任一：关键词1、关键词2

## 上下文注入
激活此技能时，追加到 system prompt 的上下文。

## 工作流
可选。标准工作流步骤。
```

## 激活机制

1. **管线技能**：代码内静态绑定（步骤→skill），`skill_loader.inject_block(name, [节名])` 注入核心节 + 完整路径供 agent 按需深读；hermes agent 启动时 skills index 自动包含
2. **会话技能**：`context_builder.py` 组装 prompt 时调用 `skill_manager.match_skills(user_input)`，命中后追加【上下文注入】文本，参与预算分配

## 扩展原则（v7.0 用户裁决）

凡可复用的流程/操作/方法论，**优先封装成 skill** 再基于 skill 优化全链路，不写一次性 prompt。人工处理（用户指令/评审团）只作兜底，能力沉淀进 skill 使自动链路自主达到质量。新增技能准入：

- [ ] 有明确的服务对象（管线步骤或对话场景）
- [ ] 内容是可复用知识（不是单次任务的操作说明）
- [ ] 量化参数引用 standards JSON，不双写
- [ ] 含验证方式（自检清单或检查项）
- [ ] 管线技能需在对应代码挂接 inject_block 并配回归测试

## 现有会话技能

| 技能 | 触发词 | 用途 |
|------|--------|------|
| `math-derivation` | 推导、证明、公式、方程、量纲 | 数学推导辅助 |
| `code-review` | 代码、review、bug、优化、重构 | 代码审查与建议 |
| `experiment-design` | 实验、方案、光路、设计、搭建 | 实验方案设计 |
| `literature-distill` | 文献、论文、精读、PRL、Nature、综述 | 文献精读与知识蒸馏（对话场景） |
| `hpc-computing` | 服务器、PBS、提交、计算、集群、qsub | HPC 计算工作流 |
| `project-planning` | 项目、计划、分解、里程碑、roadmap | 项目拆解与规划 |
| `agora-meeting` | 讨论、开会、Agora、历史人物、对话 | 多人物会议主持 |
| `self-test` | 内测、测试、回归测试、self-test、影子用户、健康检查 | 内测系统 |
| `nsfc-writing` | （已迁移指针） | 真相源在 `.hermes/skills/nsfc-writing/` |
