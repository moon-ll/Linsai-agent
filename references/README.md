# references/ — 参考资料

本目录存放用户提供给林赛的参考资料。

## 使用规范

- 用户可将论文、笔记、代码等放入此目录
- 林赛在协作过程中可引用这些资料
- **只读原则**：脚本默认只读 references/ 下的文件，不写回
- 支持通过 `/read <文件路径>` 在对话中直接读取文档内容

## 目录结构

```
references/
├── papers/         # 论文/文献
├── notes/          # 用户笔记
├── index.json      # 文献索引（由 document_handler.py 自动生成）
└── README.md
```

## 文献索引

`index.json` 由 `scripts/document_handler.py` 自动维护，包含：

```json
[
  {
    "filename": "2024-nature-physics-solid-hhg.pdf",
    "path": "references/papers/2024-nature-physics-solid-hhg.pdf",
    "category": "paper",
    "size": 1234567,
    "last_modified": "2026-05-08T10:00:00Z"
  }
]
```

## 常用命令

```bash
# 在对话中读取文档
> /read references/papers/论文.md

# 在对话中分析代码
> /read references/notes/analysis.py

# 上传文件到参考文献库（通过 document_handler.upload_document）
```

---

*版本：1.0*  
*日期：2026-05-08*
