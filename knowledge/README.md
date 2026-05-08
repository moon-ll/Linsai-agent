# 林赛的知识库

> 这不是一个普通的文档文件夹——这是林赛（Lin Sai）的**研究笔记系统**。
>
> 借鉴 Andrej Karpathy 的笔记系统设计理念：raw 是原材料，wiki 是林赛的思考结晶。
> 知识库会随着交互过程**自然生长**，反映林赛作为虚拟 PI 的持续学习。

---

## 目录结构

```
knowledge/
├── raw/                    # 用户提供的原始材料（只读，保留原貌）
│   ├── papers/             # 论文 PDF/笔记
│   ├── notes/              # 用户手写笔记
│   └── webclips/           # 网页剪藏
│
├── wiki/                   # LLM 智能管理的结构化知识（林赛的研究笔记）
│   ├── concepts/           # 核心概念（如"固体高次谐波"、"阿秒脉冲"）
│   ├── methods/            # 实验方法与技术
│   ├── people/             # 重要学者与林赛的评价
│   ├── papers/             # 论文精读笔记（林赛的批注）
│   └── projects/           # 项目相关的知识聚合
│
├── index.json              # 统一倒排索引（raw + wiki）
├── graph.json              # 知识图谱（概念间链接关系）
├── growth-log.json         # 知识生长日志（记录何时/为何新增/更新）
└── README.md               # 本文件
```

---

## 核心设计理念

### 1. raw → wiki：从原材料到思考结晶

- **raw/** 存放用户提供的原始材料，保持原貌，不做修改
- **wiki/** 是林赛基于 raw 材料提炼的研究笔记，以**第一人称**书写
- 每个 wiki 页面都有林赛的视角：个人理解、实验经验、批判性思考

### 2. 知识库作为"林赛的可靠知识来源"，而非"记忆负担"

- 知识库中的内容是林赛**主动研究**的结果，不是机械记忆
- wiki 页面体现林赛的认知确信度（confidence）和生长阶段（growth_stage）
- 对话中引用知识时，会标注来源（raw 还是 wiki）和生长阶段

### 3. 知识生长：林赛的自我成长

知识库不是静态的，它会随着交互过程自然生长：

| 触发方式 | 动作 | 结果 |
|----------|------|------|
| 用户放入 raw 文件 | `ingest_raw()` | 文件纳入索引，可选自动提炼为 wiki |
| 对话中遇到新概念 | `create_wiki_stub()` | 创建 seedling 阶段的 wiki stub |
| 对话中补充已有概念 | `grow_wiki_page()` | 丰满 wiki 内容，提升生长阶段 |
| 手动操作 | `save_wiki_page()` | 直接创建/更新 wiki |

### 4. 生长阶段

每个 wiki 页面都有生长阶段，反映林赛对该知识点的掌握程度：

- 🌱 **seedling（幼苗）**：刚遇到的概念，只有基本框架
- 🌿 **growing（成长中）**：已有一定内容，但还不够系统
- 🌳 **mature（成熟）**：内容充实，林赛有深入的理解和经验
- 📦 **archived（归档）**：不再活跃关注，但保留作为参考

---

## Wiki 页面格式

每个 wiki 页面都是标准的 Markdown 文件，带有 YAML frontmatter：

```markdown
---
title: "固体高次谐波产生"
type: concepts
created: "2026-05-08T10:00:00Z"
updated: "2026-05-08T10:00:00Z"
tags: ["HHG", "强场光学", "超快光学"]
related: ["阿秒科学", "相位匹配", "ZnO"]
source_raw: "raw/papers/solid_hhg_review_2024.md"
growth_stage: "growing"
confidence: 0.8
---

# 固体高次谐波产生

## 林赛的理解

固体 HHG 是我博士期间的主要研究方向。与气体 HHG 相比，
固体 HHG 的优势在于电子密度高三个数量级...

## 核心要点

- 转换效率可提升 10⁴–10⁶ 倍
- 带宽可达数十 eV，支持亚飞秒脉冲产生
- 受固体周期性势场影响，谐波选择性增强

## 我的实验经验

2019 年我在搭建 ZnO HHG 系统时，发现相位匹配条件对晶体取向极其敏感...

## 开放问题

- 如何定量描述多体效应在 HHG 中的贡献？
```

### Frontmatter 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 页面标题 |
| `type` | string | 页面类型：concepts / methods / people / papers / projects |
| `created` | ISO datetime | 创建时间 |
| `updated` | ISO datetime | 最后更新时间 |
| `tags` | string[] | 标签列表 |
| `related` | string[] | 关联概念名称（用于构建知识图谱） |
| `source_raw` | string | 源 raw 文件路径（如有） |
| `growth_stage` | string | 生长阶段：seedling / growing / mature / archived |
| `confidence` | float | 林赛对该知识点的确信度（0-1） |

---

## 知识图谱

`graph.json` 记录概念之间的关系：

```json
{
  "nodes": {
    "固体高次谐波产生": {
      "type": "concepts",
      "path": "wiki/concepts/固体高次谐波产生.md",
      "growth_stage": "mature"
    }
  },
  "edges": [
    {"from": "固体高次谐波产生", "to": "阿秒科学", "relation": "enables"},
    {"from": "固体高次谐波产生", "to": "相位匹配", "relation": "requires"}
  ]
}
```

关联概念在对话时会被自动拉取，丰富上下文。

---

## 生长日志

`growth-log.json` 记录知识库的所有变更历史：

```json
[
  {
    "timestamp": "2026-05-08T10:00:00Z",
    "action": "create",
    "target": "wiki/concepts/固体高次谐波产生.md",
    "trigger": "raw_ingest",
    "reason": "从论文综述中提炼核心概念"
  },
  {
    "timestamp": "2026-05-08T11:00:00Z",
    "action": "update",
    "target": "wiki/concepts/固体高次谐波产生.md",
    "trigger": "conversation",
    "reason": "用户询问了晶体取向效应，补充了林赛的实验经验"
  }
]
```

---

## 使用方式

### 1. 添加 raw 材料

将论文、笔记等放入 `knowledge/raw/papers/`、`knowledge/raw/notes/` 或 `knowledge/raw/webclips/` 目录，然后在 Web 界面点击"重建索引"。

### 2. 通过 Web 界面管理

打开设置面板 → 点击"📚 知识库管理器"：
- **概览**：查看知识库统计和生长阶段分布
- **Raw**：浏览原始材料
- **Wiki**：浏览/查看林赛的研究笔记
- **图谱**：查看知识节点和关联关系
- **生长**：查看生长日志和待生长概念

### 3. 创建新概念 Stub

在 Wiki 面板点击"➕ 新建概念 Stub"，输入概念名称即可创建一个 seedling 阶段的 wiki 页面。后续对话中遇到这个概念时，林赛会逐步丰满它。

### 4. 程序化管理

```python
from scripts.knowledge_base import ingest_raw, create_wiki_stub, save_wiki_page

# 纳入 raw 文件
ingest_raw("raw/papers/my_paper.md", auto_distill=True)

# 创建概念 stub
create_wiki_stub("量子隧穿电离", context="用户讨论强场电离机制")

# 直接保存 wiki
save_wiki_page("wiki/methods/我的实验方法.md", "# 我的实验方法\n\n...", {
    "title": "我的实验方法",
    "type": "methods",
    "growth_stage": "mature",
    "confidence": 0.9,
})
```

---

## 与对话的集成

知识库深度集成到对话流程中：

1. **上下文构建**：`context_builder.py` 自动检索相关知识注入 system_prompt
2. **优先 wiki**：搜索结果优先返回 wiki 页面（结构化知识优先于 raw 材料）
3. **关联知识拉取**：通过知识图谱获取关联概念，丰富上下文
4. **缺失概念检测**：如果用户提到知识库中没有的概念，林赛会标注"认知边界"，并邀请用户一起记录
5. **生长触发**：对话结束后，系统可自动判断是否有需要补充的知识

---

## 注意事项

- **raw 文件是只读的**：不要在 raw/ 目录内直接编辑文件，应该通过提炼生成 wiki
- **wiki 是林赛的笔记**：以第一人称书写，体现林赛的专业视角和个人经验
- **生长阶段要诚实**：seedling 不是缺陷，是诚实标注认知边界的体现
- **知识库被 Git 忽略**：index.json、graph.json、growth-log.json 被忽略，但 raw/ 和 wiki/ 目录下的 .md 文件应该被版本控制
