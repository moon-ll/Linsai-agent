# 林赛的知识库

> 本目录是 **Obsidian Vault**，可直接在 Obsidian 中打开。

## 目录结构

```
knowledge/
├── raw/                    # 原始材料（只读）
│   ├── papers/             # 论文 PDF/笔记
│   ├── notes/              # 用户手写笔记
│   └── webclips/           # 网页剪藏
├── wiki/                   # 结构化知识（LLM 智能管理）
│   ├── concepts/           # 核心概念
│   ├── methods/            # 实验方法与技术
│   ├── people/             # 重要学者
│   ├── papers/             # 论文精读笔记
│   └── projects/           # 项目知识聚合
├── templates/              # Obsidian 模板
├── index.json              # 倒排索引（程序生成）
├── graph.json              # 知识图谱（程序生成）
├── aliases.json            # 别名映射
└── growth-log.json         # 知识生长日志
```

## 在 Obsidian 中使用

1. **打开 Vault**：在 Obsidian 中选择「打开本地文件夹」→ 选中 `knowledge/` 目录
2. **查看图谱**：按 `Ctrl/Cmd + G` 打开图谱视图，查看概念间的双向链接
3. **使用模板**：新建笔记时选择「概念笔记」模板，frontmatter 会自动填充
4. **添加关联**：在 frontmatter 的 `related` 字段添加概念名，保存后程序会自动注入 `[[双向链接]]`

## 与林赛系统的交互

- **raw → wiki**：将文献拖入 `raw/papers/`，林赛会自动提炼为结构化笔记
- **对话生长**：与林赛讨论新概念时，他会自动创建 seedling stub 到 `wiki/concepts/`
- **别名映射**：修改 `aliases.json` 后，重新保存 wiki 页面即可同步到 frontmatter

## 注意事项

- 不要手动修改 `index.json`、`graph.json`、`growth-log.json`（程序自动生成）
- `.obsidian/` 文件夹存放 Obsidian 配置，可自由调整主题和插件
- `[[双向链接]]` 由程序自动维护，也可在 Obsidian 中手动添加
