# 林赛的知识库

> 本目录是 **Obsidian Vault**，可直接在 Obsidian 中打开。
> v6.7.11 起按 **raw / wiki / qa** 三层结构组织，三层写入权限与管理者不同。

## 三层结构总览

```
knowledge/
├── raw/                    # 源模块（原始数据，只读，用户指令才可写）
│   ├── projects/           # 课题库：一个课题一个文件夹
│   │   └── {proposal_id}/
│   │       ├── 00_research_idea.md
│   │       ├── 00_proposal-brief.md
│   │       ├── 01_direction/
│   │       ├── 02_literature/
│   │       ├── 03_question/
│   │       ├── 04_proposal/
│   │       │   ├── proposal-draft.md
│   │       │   ├── methodology-manual.md
│   │       │   └── sections/
│   │       ├── 05_review/
│   │       ├── 06_feedback/
│   │       ├── _archive-meta.json
│   │       └── _README.md
│   ├── papers/             # 文献库：论文元数据（deepxiv 流水线抓取）
│   │   ├── [year]-[arxiv_id]-[slug].md
│   │   └── pdfs/           # PDF 原文（程序维护）
│   ├── notes/              # 用户手写笔记 / 调研报告
│   └── webclips/           # 网页剪藏
├── wiki/                   # 智能整理模块（AI 自动管理，可读写）
│   ├── concepts/           # 核心概念
│   ├── methods/            # 实验/理论方法
│   ├── people/             # 学者
│   ├── papers/             # 综述/深度阅读报告
│   ├── projects/           # 课题索引卡片（由归档流程生成）
│   └── reviews/            # 简报/评论汇总
└── qa/                     # 问答模块（用户讨论归档，可读写）
    ├── paper-discussions/      # 文献讨论
    ├── proposal-discussions/   # 课题讨论
    └── project-discussions/    # 项目/方向讨论
```

## 写入权限规范

| 模块 | 内容 | 写入者 | 修改方式 |
|------|------|--------|----------|
| `raw/` | 原始数据、可靠来源内容 | 原则上只读 | 仅由程序迁移/用户明确指令写入 |
| `wiki/` | AI 整理的衍生知识 | AI 自动管理 | 程序自动读写 |
| `qa/` | 用户对话/讨论归档 | AI 自动归档 | 程序自动读写 |

> **核心原则**：没有来源或不可靠的信息不进入知识库，避免污染。可靠来源包括：文献原文/元数据、学术报道、用户主动提供的资料、经审核归档的课题文件。

## 课题库（raw/projects/）

- 每个归档课题以 `knowledge/raw/projects/{proposal_id}/` 形式保存完整源文件。
- 由 `proposal_lifecycle` 在课题审核通过归档时自动复制。
- 关键文件：
  - `00_research_idea.md` — 课题设想（初稿）
  - `04_proposal/proposal-draft.md` — 申请书
  - `04_proposal/methodology-manual.md` — 方法学手册
  - `02_literature/reading-notes.md` — 文献阅读笔记
  - `_archive-meta.json` — 归档元信息

## 文献库（raw/papers/）

- `raw/papers/*.md`：arXiv 论文结构化元数据（deepxiv 流水线抓取），共 100+ 篇 HHG 相关论文。
- `raw/pdfs/`：PDF 原文库（程序维护，见 `pdf_manager.py`）。
- 按 `project` 字段可分子库检索，如 `NSFC-强场超快`、`deepxiv-论文库`。

## project 字段与子库分类

每篇文档的 frontmatter 含 `project` 字段，标识归属子库：
- `deepxiv-论文库`：deepxiv 流水线从 arXiv 抓取的论文元数据
- `NSFC-强场超快`：NSFC 强场超快课题相关论文
- 检索时可按子库过滤：`search(query, project="NSFC-强场超快")`

## 问答模块（qa/）

- `paper-discussions/`：围绕单篇文献的讨论会话归档。
- `proposal-discussions/`：围绕单个课题的讨论会话归档。
- `project-discussions/`：方向/项目级别的讨论会话归档。

## 在 Obsidian 中使用

1. **打开 Vault**：在 Obsidian 中选择「打开本地文件夹」→ 选中 `knowledge/` 目录
2. **查看图谱**：按 `Ctrl/Cmd + G` 打开图谱视图，查看概念间的双向链接
3. **使用模板**：新建笔记时选择「概念笔记」模板，frontmatter 会自动填充
4. **添加关联**：在 frontmatter 的 `related` 字段添加概念名，保存后程序会自动注入 `[[双向链接]]`

## 与林赛系统的交互

- **raw → wiki**：将文献拖入 `raw/papers/`，林赛会自动提炼为结构化笔记
- **对话生长**：与林赛讨论新概念时，他会自动创建 seedling stub 到 `wiki/concepts/`
- **课题归档**：课题审核通过后，完整文件自动归档到 `raw/projects/`，索引卡片写入 `wiki/projects/`
- **讨论归档**：有价值的对话结束后，可归档到 `qa/` 相应子目录
- **别名映射**：修改 `aliases.json` 后，重新保存 wiki 页面即可同步到 frontmatter

## 注意事项

- 不要手动修改 `index.json`、`graph.json`、`growth-log.json`（程序自动生成）
- `.obsidian/` 文件夹存放 Obsidian 配置，可自由调整主题和插件
- `[[双向链接]]` 由程序自动维护，也可在 Obsidian 中手动添加
- `raw/` 层文件如需修改，请通过前端/对话由 agent 协助，避免直接手动编辑导致索引不一致
