# 林赛研究工作台（LinSai-CoPilot）

> **自动化生产课题启动包，人来启动正式研究。**

---

## 这是什么？

**林赛研究工作台**（v8.0.0）是一个研究工作台系统：
- **自动化**负责文献阅读与深度研究——发掘有价值的科学问题，产出**课题启动包**
  （课题报告 + 参考文献 + 方法素材）；
- **人**负责选题、审阅启动包、启动正式研究，并主导跨课题/跨时间的整合。

### 一句话定位

林赛不是替你写项目书的机器，而是你的**研究工作台**：
- 他每天读文献、跟踪领域动态（文献链，全天候自动）
- 他把有价值的科学问题整理成问题候选（问题收件箱）
- 他对每个问题做单遍深度研究，交出一份**课题报告**：背景调研充分、问题定位清晰、
  方案分解明确——为课题正式研究提供可以具体推进的方法和路线
- 课题报告聚焦一个具体问题（**区分于项目书**），不同课题报告之间建立关联
- **启动与否由你决定**——自动化到 ready 为止，人不批准不启动

### v8 架构裁决（2026-11-16）

放弃 v7 的全流程自动化（自动生成完整项目书 + 多轮对抗优化），三条根因：
完整项目书内容庞杂难以自动化优化好；多轮评审 token 消耗过大；上下文限制下
自动化不擅长多方信息与跨时间尺度的整合。v7 优化环机制代码已归档
（`scripts/archive/v7-optimization/`，归档不删除）。

---

## 工作流程

```
【A 文献链】简报 4次/天 → 评分 → 深读 → 蒸馏 → 聚类 → 问题候选收件箱
【B 深研链】每日 1 课题：背景调研 → 问题定位 → 方案分解 → 启动包集成（零 LLM 组装）
【C 验收自检】背景充分/问题清晰/方案明确/文献真实/篇幅/关联 六项 → 通过 → ready
【人工节点】你审阅启动包 → 一键启动（active）→ 正式研究（1v1 会话 + 任务追踪）
           → 收尾归档（关键知识萃取回知识库）
```

### 课题启动包验收标准（自动自检，零 LLM）

| 编号 | 标准 |
|------|------|
| A1 | 背景调研充分：≥8 篇文献笔记（近 24 个月 ≥3）+ 知识库关联 |
| A2 | 问题定位清晰：一句话陈述 + 新颖性对照（与既有课题相似度 <0.50） |
| A3 | 方案分解明确：≥3 个步骤、每步含判据、含首月路线、方法素材包 |
| A4 | 参考文献真实：每条引用可溯源（KB 页/raw 论文/检索池），零杜撰 |
| G1 | 篇幅约束：报告 ≤8000 字 |
| G2 | 关联明确：与相关课题/知识页建立链接 |

---

## 项目产出

| 资产 | 位置 | 定位 |
|------|------|------|
| **课题库** | `research_topics/` | 本项目的核心产出：questions → kickoff → ready → active → archive |
| **技能库** | `.hermes/skills/`（管线技能）+ `skills/`（会话技能） | 可复用能力资产 |
| **知识库** | `knowledge/` | 文献链沉淀（raw→wiki→方法卡→图谱），反哺深研链 |

`research_proposals/` 为 v7 遗留只读域（21 个课题已全部迁移至新域，原目录保留审计）。

---

## 林赛是谁？

- **31 岁**，强场超快光学独立 PI，刚拿到第一个 DFG 经费
- **核心信条**："What I cannot create, I do not understand"
- **他会什么**：实验设计、理论与实验迭代、学术写作、文献深读
- **他不会什么**：替你做启动决定、替你算数值、给标准答案式建议

完整人格画像见 [`persona/lin-sai-persona.md`](persona/lin-sai-persona.md)。

---

## 快速开始

```bash
cd ~/Desktop/LinSai-CoPilot

# Web 工作台（推荐）
python scripts/web_server.py            # 打开 http://localhost:8080
./scripts/launch.sh                     # 一键启动（自动开浏览器）

# CLI 课题看板
python scripts/topic_pipeline.py --list             # 课题看板
python scripts/topic_pipeline.py --daily            # 手动触发一次深研 worker
python scripts/topic_pipeline.py --check <id>       # 查看启动包自检结果
python scripts/topic_pipeline.py --activate <id>    # 启动课题（人工节点）

# CLI 协作会话（1v1 工作台助手）
python scripts/copilot_engine.py --start "固体HHG实验方案设计"
python scripts/copilot_engine.py --continue

# 备份与恢复
python scripts/backup_manager.py --list
python scripts/backup_manager.py --restore backups/<zip>
```

---

## 项目结构（v8 摘要）

```
LinSai-CoPilot/
├── AGENTS.md                  # AI 代理开发指南（v8）
├── docs/
│   ├── WORKBENCH-ARCHITECTURE.md  # v8 设计纲领（工作流程/验收标准/迁移/清理）
│   ├── ARCHITECTURE.md        # 架构说明
│   └── PROJECT-STRUCTURE.md   # 目录结构
├── research_topics/           # v8 课题库（活跃数据域）
│   ├── _topics.json           # 轻量状态索引（状态由目录位置+课题卡承载）
│   ├── questions/             # 问题候选（收件箱）
│   ├── kickoff/               # 深研中（01_background/02_problem/03_scheme/04_references）
│   ├── ready/                 # 启动包就绪（待人工启动）
│   ├── active/                # 正式研究中
│   ├── archive/               # 收尾归档
│   └── _audit/                # 迁移报告 / cron 停用审计
├── research_proposals/        # v7 legacy 只读域（已全部迁出）
├── knowledge/                 # 知识库（raw/wiki/pdfs，文献链沉淀）
├── scripts/
│   ├── topic_pipeline/        # v8 课题启动包管线（12 模块）
│   ├── topic_pipeline.py      # CLI 入口（shim）
│   ├── workbench_monitor.py   # 轻量健康检查
│   ├── copilot_engine.py      # 1v1 会话引擎
│   ├── web_server.py          # Web 工作台（Mixin 路由）
│   ├── deep_read_pipeline.py · literature_*.py · external_fetcher.py   # 文献链
│   ├── kb_*.py                # 知识库引擎
│   ├── weekend_pipeline/      # 周末输入端（文献发现）
│   ├── archive/v7-optimization/  # v7 优化环退役代码（归档不删除）
│   └── tests/                 # 自动化测试（scripts/tests/archive/ 为退役测试）
├── .hermes/skills/            # 5 个管线技能（深研链 3 个在用，2 个 legacy）
├── sessions/ memory/ tasks/   # 会话 / 记忆 / 任务（用户数据）
└── web/                       # 前端（零框架，含课题工作台看板）
```

---

## 自动化边界（人机分工）

| 自动化（无人值守） | 人工（法定节点） |
|-------------------|-----------------|
| 文献链全天候（简报/深读/蒸馏/聚类） | 问题候选**否决** |
| 每日深研 worker（1 课题/天，可配额） | 启动包**采纳启动** |
| 启动包组装 + 验收自检 | 课题**收尾归档** |
| 知识库治理（同步/蒸馏/图谱/备份） | 跨课题/跨时间整合、正式研究推进 |

深研缺口自动补齐（每缺口 2 次机会），补不过 → `needs_human` 挂起等人裁决，
不自动重试烧 token。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 运行环境 | Python 3（仅标准库，零第三方依赖） |
| 内容格式 | Markdown + JSON |
| LLM | MiniMax-M3 / GLM-5.2 / Claude CLI（hermes profile 管理，自动降级） |
| Web | `http.server` + 原生 HTML/CSS/JS（REST + SSE） |
| 定时 | hermes gateway cron（23 个活跃 job，见 AGENTS.md 清单） |

---

## 贡献与维护

- 修改前必读 `AGENTS.md`；v8 设计依据见 `docs/WORKBENCH-ARCHITECTURE.md`
- 所有变更记录在 `CHANGELOG.md`
- 测试基线：`python3 scripts/self_test.py --module`（v8.0.0 起 3576/3576）

---

*版本：8.0.0*
*日期：2026-11-17*
