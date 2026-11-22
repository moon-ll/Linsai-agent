# 林赛的知识库

> 本目录是 **Obsidian Vault**，可直接在 Obsidian 中打开。
> v7.0 起按 **raw / wiki / qa** 三层结构组织，三层写入权限与管理者不同。
> **v7.0.7 起**：方法学升级链接通——`literature-reading` skill（深读/蒸馏）→
> `kb_methods_backfill.py`（ZCode 零 LLM 提取，v7.0.7 改）+ `kb_methods_governance.py`
> （专题治理）+ `kb_methods_pack.py`（课题素材包）→ `update_method_manual` 消费 →
> writer/critic 写方案时直接取材方法页。知识库成为"装置/序列/参数/判据/时间预算"
> 五问素材的单一真相源。

## 三层结构总览

```
knowledge/
├── raw/                    # 源模块（原始数据，只读，用户指令才可写）
│   ├── papers/             # 文献库：论文元数据（deepxiv 流水线抓取）
│   │   ├── [year]-[arxiv_id]-[slug].md
│   │   └── (PDF 原文在 raw/pdfs/，v7.0.2 起移出 git，本地保留 + 备份覆盖)
│   ├── pdfs/               # PDF 原文 1361 个 / 6.8 GB（不入 git）
│   ├── notes/              # 用户手写笔记 / 调研报告
│   └── webclips/           # 网页剪藏（capture 管线目标位，暂空）
├── wiki/                   # 智能整理模块（AI 自动管理，可读写）
│   ├── mocs/               # 主题地图（7 张：固体HHG/强场物理/能谷电子学/表征方法/量子光学/阿秒科学/非线性光学）
│   ├── concepts/           # 核心概念（237 篇，六节模板）
│   ├── methods/            # 实验/理论方法（115 篇，方法卡四要素：
│   │                       # 原理/参数表·数值含单位与出处/适用边界/代表作）
│   ├── people/             # 学者（10 篇）
│   ├── papers/             # 论文笔记（2985 篇存活口径；地图入口 papers/MOC.md）
│   ├── projects/           # 课题 wiki 同步视图（NSFC-强场超快 / deepxiv-论文库）
│   └── reviews/            # 简报/评论汇总（126 篇）
├── templates/              # 笔记模板
├── qa/                     # 问答模块（用户讨论归档，可读写）
│   ├── paper-discussions/      # 文献讨论
│   ├── proposal-discussions/   # 课题讨论
│   └── project-discussions/    # 项目/方向讨论
└── trash/                  # 回收站（含 papers-dedup-20261030 去重暂存）
```

> **课题库位置**（2026-10-30 修正）：课题库活体与归档在**顶层** `LinSai-CoPilot/research_proposals/`
> （`optimizing/` 活跃 / `pending_review/` 待审 / `_archive/` 归档 / `_rejected-ideas/` 否决），
> 每课题目录结构 `00_research_idea.md` … `03_method/kb-methods-pack.md` … `05_review/` 等。
> 旧文档所述 `knowledge/raw/projects/` 已废弃；knowledge 侧仅在 `wiki/projects/` 保留同步视图与索引卡片。

## 写入权限规范（v7.0.1 起三库资产定位）

> **核心原则**：本目录是项目三大产出资产之一（**知识库**），与"技能库"
> `.hermes/skills/`（领域方法论/写作规范/评审标准）、"课题库"
> `research_proposals/`（核心产出）并列。三库关系：技能库驱动课题生产
> → 课题产出回流知识库（归档萃取）→ 知识库反哺新课题（文献/方法支撑）。
> 凡可复用流程优先封装成 skill，**人工处理只作兜底**——能力沉淀进 skill 让
> 自动链路自主达到质量。

| 模块 | 内容 | 写入者 | 修改方式 |
|------|------|--------|----------|
| `raw/` | 原始数据、可靠来源内容 | 原则上只读 | 仅由程序迁移/用户明确指令写入 |
| `wiki/` | AI 整理的衍生知识 | AI 自动管理 | 程序自动读写 |
| `qa/` | 用户对话/讨论归档 | AI 自动归档 | 程序自动读写 |

> **核心原则**：没有来源或不可靠的信息不进入知识库，避免污染。可靠来源包括：
> 文献原文/元数据、学术报道、用户主动提供的资料、经审核归档的课题文件、
> **v7.0.5+ 方法卡（参数表逐行带文献出处）**。

## 课题库（顶层 research_proposals/，2026-10-30 修正）

- 课题活体与归档在顶层 `LinSai-CoPilot/research_proposals/`（optimizing/ 活跃、pending_review/ 待审、_archive/ 归档），一个课题一个文件夹；knowledge 侧仅在 `wiki/projects/` 保留同步视图。
- 由 `proposal_lifecycle` 在课题审核通过归档时自动复制。
- 关键文件：
  - `00_research_idea.md` — 课题设想（初稿）
  - `00_proposal-brief.md` — 立项决策包（v6.9.0 起，含三档激活建议）
  - `04_proposal/proposal-draft.md` — 申请书
  - `04_proposal/methodology-manual.md` — 方法学手册（**手册是方案细节与文献方法素材的汇合点**）
  - `02_literature/reading-notes.md` — 文献阅读笔记
  - `03_method/kb-methods-pack.md` — v7.0.6 起按设想关键词聚合的素材包
  - `_archive-meta.json` — 归档元信息

## 文献库（raw/papers/）

- `raw/papers/*.md`：arXiv 论文结构化元数据（deepxiv 流水线抓取）。
- `raw/pdfs/`：PDF 原文库（v7.0.2 起**移出 git 跟踪**，本地保留 + `backup_manager` 每日全量 zip 覆盖备份）。
- 按 `project` 字段可分子库检索，如 `NSFC-强场超快`、`deepxiv-论文库`。
- **v7.0.7 起**：方法学升级链使 `papers` 不再只是阅读材料，方法密度高的论文在蒸馏/深读时按方法卡格式写入研究方法节（`literature-reading` skill 五节），方法页可直接取材——方法页的方法卡带 `[来源] author year` 字段。

## 知识库每日治理流水线（v7.0.7 现行口径）

> **核心变更（v7.0.7 用户裁决）**：方法学升级任务统一走 ZCode 自动化，
> 不再独立 LLM 调用——`kb_distill` 蒸馏链路本身用 LLM 属既有设计不在纠正
> 范围；被纠正的是"补方法卡 / 治理 / 课题素材包"三类知识库升级任务的执行
> 方式（提取与改写由 ZCode 任务直接读页面，零额外 LLM 消耗）。

| 任务 | 触发 | 执行者 | 产物 |
|------|------|--------|------|
| 蒸馏 raw→wiki | `lc-kb-distill` 每日 12:50 / 周日 20:00 补档 | kb_distill（LLM） | `wiki/papers/` 五要素页 |
| 蒸馏分层（v6.9.75） | 同上 | deep_read_pipeline 标记 `digest_level=fulltext/abstract` | papers frontmatter |
| 索引/图谱无条件重建 | `lc-kb-sync` 每日 12:40 | kb_auto_sync | `index.json` / `graph.json` |
| 生长阶段晋升 | `lc-kb-sync` | growth_engine --apply | seedling → developed |
| 链接补边 | 蒸馏尾部自动 | kb_linker --apply | related 边（关键词 overlap，零 LLM） |
| 论文页双世代去重 | 周日反思前置 | kb_merger --dedup-papers | slug 代为主，附录并置 |
| 重复页合并 | 周日反思 | kb_merger（LLM 融合失败降级附录并置） | stub 重定向 |
| 分类重建 | 周日反思 | kb_taxonomy --apply | tags 频率聚类 |
| **方法学升级（v7.0.7）** | `--worklist N` 发射 | **ZCode 自动化任务**（零 LLM 直接读页面撰写） | `wiki/methods/` 方法卡 |
| **专题治理（v7.0.6）** | 一次性 | kb_methods_governance | 命名纠正/合并 stub |
| **课题素材包（v7.0.6）** | 一次性 / 新课题触发 | kb_methods_pack | `03_method/kb-methods-pack.md` |

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
- **课题归档**：课题审核通过后，完整文件归档到顶层 `research_proposals/_archive/`，同步视图与索引卡片写入 `wiki/projects/`
- **讨论归档**：有价值的对话结束后，可归档到 `qa/` 相应子目录
- **别名映射**：修改 `aliases.json` 后，重新保存 wiki 页面即可同步到 frontmatter
- **方法学升级（v7.0.7）**：用户对知识库下达升级指令 → 生成 `--worklist N` → ZCode 任务消费清单 → 写方法卡到 `wiki/methods/` → 方法页被 writer/critic 写作时直接引用

## 注意事项

- 不要手动修改 `index.json`、`graph.json`、`growth-log.json`（程序自动生成）
- `.obsidian/` 文件夹存放 Obsidian 配置，可自由调整主题和插件
- `[[双向链接]]` 由程序自动维护，也可在 Obsidian 中手动添加
- `raw/` 层文件如需修改，请通过前端/对话由 agent 协助，避免直接手动编辑导致索引不一致
- **`raw/pdfs/` 在 v7.0.2 起不入 git**：本地文件全部保留，备份由 `backup_manager` 每日 knowledge 全量 zip 覆盖；如需重写 git 历史以彻底瘦身须先全量备份 + 用户明示授权（属危险操作）
- **`methods/` 方法页 v7.0.5 起按方法卡标准**：每页含原理/参数表（数值含单位与出处）/适用边界/代表作四要素；参数溯源纪律由 `method-manual` skill 一节三节约束