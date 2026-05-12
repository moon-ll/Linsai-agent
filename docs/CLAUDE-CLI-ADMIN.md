# Claude CLI 人工管理指南

> 本文档说明如何使用 Claude Code CLI 手动管理林赛知识库中的 auto-grown 内容。
> Claude CLI **不集成到自动化流程**，由用户在终端手动调用。

---

## 快速开始

### 前提条件

- 已安装 [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code/overview)
- 当前目录在 `~/Desktop/LinSai-CoPilot`

### 常用命令

```bash
# 1. 进入项目目录
cd ~/Desktop/LinSai-CoPilot

# 2. 质量审查某篇 auto-grown 的 wiki
claude --print --allowed-tools "Read" --add-dir knowledge/ \
  "请审查 knowledge/wiki/papers/xxx.md，检查逻辑一致性、人格一致性和学术严谨性，列出问题清单。"

# 3. 维护审查（检测孤儿节点、重复概念）
cat docs/prompts/maintenance-audit.txt | claude --print --allowed-tools "Read" --add-dir knowledge/

# 4. 概念合并（两个相似概念）
cat docs/prompts/concept-merge.txt | claude --print --allowed-tools "Read,Edit" --add-dir knowledge/

# 5. 论文深度阅读
cat docs/prompts/paper-deep-read.txt | claude --print --allowed-tools "Read" --add-dir knowledge/
```

---

## 工作流

### 工作流 1：审查 auto-grown 内容

**触发时机**：每周一次，或发现知识库质量下降时

**步骤**：
1. 查看待审队列：`python scripts/quality_evaluator.py --pending`
2. 选择一篇 pending 的 wiki，用 Claude CLI 审查
3. 根据审查结果决定：接受 / 修改 / 拒绝

```bash
# 查看待审队列
python scripts/quality_evaluator.py --pending

# 审查单篇 wiki
claude --print --allowed-tools "Read,Edit" --add-dir knowledge/ \
  "请审查 knowledge/wiki/concepts/xxx.md，补充缺失的关键假设，修正不准确的表述，确保保持林赛的第一人称视角。"

# 审批通过
python scripts/quality_evaluator.py --approve "wiki/concepts/xxx.md"
```

### 工作流 2：维护审查

**触发时机**：每月一次，或运行 `kb_maintenance.py --health` 发现异常时

**步骤**：
1. 运行维护审计 prompt
2. 根据 Claude 的输出，手动修复问题

```bash
# 运行维护审计
cat docs/prompts/maintenance-audit.txt | claude --print --allowed-tools "Read" --add-dir knowledge/

# 根据输出手动修复
# 例如：删除孤儿节点、合并重复概念、修复 broken links
```

### 工作流 3：概念合并

**触发时机**：发现知识库中有重复或高度相似的概念时

**步骤**：
1. 确定两个要合并的概念
2. 运行概念合并 prompt
3. 将合并后的内容保存到新文件，删除旧文件

```bash
# 概念合并
cat docs/prompts/concept-merge.txt | claude --print --allowed-tools "Read,Edit" --add-dir knowledge/

# 手动保存结果并更新图谱
```

---

## 与自动化引擎的边界

```
自动化流程（scripts/learning_engine.py）
  ├── 搜索文献 ← deepxiv CLI
  ├── 生成精读笔记 ← MiniMax / kimi / claude API
  ├── 更新概念 wiki ← MiniMax / kimi / claude API
  └── 更新图谱 ← Python 脚本

人工流程（用户在终端运行 claude CLI）
  ├── 质量审查 ← quality-audit.txt prompt
  ├── 维护管理 ← maintenance-audit.txt prompt
  ├── 概念合并 ← concept-merge.txt prompt
  └── 深度阅读 ← paper-deep-read.txt prompt
```

**关键设计**：
- 自动化引擎生成的内容标记 `[auto-grown: true]`
- 用户通过 Claude CLI 审查后，运行 `quality_evaluator.py --approve` 确认
- 保留用户的最终控制权，不需要在代码中集成 Claude CLI 的自动化调用

---

## 文件清单

| 文件 | 用途 |
|------|------|
| `docs/prompts/quality-audit.txt` | 质量审查 prompt |
| `docs/prompts/maintenance-audit.txt` | 维护审查 prompt |
| `docs/prompts/concept-merge.txt` | 概念合并 prompt |
| `docs/prompts/paper-deep-read.txt` | 论文精读 prompt |

---

*版本：1.0*
*日期：2026-05-12*
