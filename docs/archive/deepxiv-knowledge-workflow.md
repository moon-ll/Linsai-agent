# deepxiv 知识库流水线 — 使用文档与设计说明

> 构建者：LinSai-CoPilot | 版本：v6 | 日期：2026-05-19

---

## 1. 背景与目标

**问题**：原有 `knowledge/raw/papers/` 中论文为 AI 生成的不可靠摘要。
**目标**：用 `deepxiv` CLI 从 arXiv 实时检索真实论文，重建可靠知识库；
对重点文献进一步用 PDF 全文增强内容提取质量。

**当前规模**：61 篇论文（2026-05-19），均含 deepxiv 真实摘要 + PDF 全文内容。

---

## 2. 系统架构

```
scripts/deepxiv_knowledge/          # 论文获取流水线
├── __init__.py
├── schema.py                      # 论文标准结构（PAPER_SCHEMA）
├── checkpoint.py                   # 断点持久化（JSON）
├── fetch_core.py                   # deepxiv 封装 + section TLDR 解析
├── paper_writer.py                # 写入 raw paper Markdown
├── pdf_extractor.py               # PDF 全文提取（PyPDF2）
├── pdf_enricher.py                # PDF 增强流水线
└── run.py                        # 主入口（v6，支持 --rebuild）

scripts/wiki_regenerator/          # wiki 报告重建
├── __init__.py
├── paper_reader.py                # 读取所有 raw papers（支持 YAML 列表解析）
├── report_writer.py              # 6 篇报告生成器
└── run.py                        # 主入口

knowledge/raw/papers/              # 真实论文库（61 篇，含 PDF 增强内容）
knowledge/wiki/papers/             # wiki 报告（6 篇）
```

---

## 3. 使用方法

### 3.1 论文获取（run.py）

```bash
# 查看待处理论文列表
python scripts/deepxiv_knowledge/run.py --dry

# 全量运行（61 篇，约 10 分钟）
python scripts/deepxiv_knowledge/run.py

# 强制重建（忽略 checkpoint，重新获取所有论文）
# 用于 schema/解析逻辑变更后
python scripts/deepxiv_knowledge/run.py --rebuild

# 仅 priority=1 核心论文
python scripts/deepxiv_knowledge/run.py --priority 1

# 检查点状态
python scripts/deepxiv_knowledge/checkpoint.py report
```

### 3.2 PDF 全文增强（pdf_enricher.py）

```bash
# 对 top 20 重点文献进行 PDF 全文增强
python scripts/deepxiv_knowledge/pdf_enricher.py --all

# 对单篇论文进行 PDF 增强
python scripts/deepxiv_knowledge/pdf_enricher.py 2403.19535

# 对所有 raw papers 全量 PDF 增强
python scripts/deepxiv_knowledge/pdf_enricher.py --rebuild
```

> **依赖**：PyPDF2（macOS 内置 `~/.venv/bin/python3` 环境下可用）。
> PDF 增强后 raw paper 文件追加 `-->` 标注来源：`<!-- PDF增强于 2026-05-19 -->`。

### 3.3 wiki 报告重建

```bash
# 从所有 raw papers 重建全部 6 篇 wiki 报告
python scripts/wiki_regenerator/run.py

# hhg-methods-report.md 的 §1-4 已含公式推导（2026-05-19 已人工验证）
# → run.py 仅追加 §5（方法比较）+ 参考文献索引，不覆盖已有内容
```

---

## 4. 核心设计

### 4.1 限流策略

- `deepxiv paper --head`：每次调用后 `sleep 2s`
- `deepxiv paper --preview`：每次调用后 `sleep 5s`
- 指数退避重试：最多 3 次，`wait = 2^attempt + 2s`
- 主动识别 "not found" 错误，快速失败

### 4.2 断点续传

```python
# checkpoint.json 结构
{
  "papers": {
    "1012.3863": {"status": "verified", "updated_at": "2026-05-19T..."},
    "physics/9906053": {"status": "failed", "error": "..."}
  },
  "meta": {"total": 9, "completed": 8, "failed": 1}
}
```

### 4.3 数据源优先级（v6）

```
1. deepxiv --head sections[] TLDRs  ← 官方解析各节摘要（质量最高）
2. deepxiv --head (JSON)           ← 作者、期刊、摘要、引用数
3. deepxiv --preview (文本)         ← Introduction / Methods 关键句（降级）
4. tldr 字段                      ← 兜底（preview 解析失败时）
```

> `sections[]` 中 Acknowledgment / References / Appendix 等非实质节已过滤。

### 4.4 PDF 全文增强（pdf_extractor.py）

```
arXiv PDF → PyPDF2 全文提取 → 智能清理 → 章节解析 → 要点提取
```

**清理策略**：
- 碎片化检测：平均<30字/行 → 全文件合并（处理 PRL/Science 逐词分行）
- 去除 affiliation / URL / 页眉 / 软连字符
- 移除 "(Dated:...) 之前" 的作者块

**章节解析**：支持罗马数字标题（I. INTRODUCTION）/ 全大写节名 / 理论方法节（TDSE/Bloch/Hamiltonian）。

**内容质量对比**（61 篇平均）：

| 指标 | deepxiv head+preview | + PDF 全文增强 |
|------|---------------------|-------------------|
| 关键科学问题 | 1.0 条/篇 | **3.0 条/篇** |
| 核心发现 | 2.6 条/篇 | **6.0 条/篇** |

### 4.5 可靠性分级

| 状态 | 含义 |
|------|------|
| `verified` | head + preview 均成功 |
| `partial` | 仅 head 成功（无 preview） |
| `failed` | head 失败 |
| `pending` | 未处理 |

---

## 5. 论文 Schema

```json
{
  "arxiv_id": "1012.3863",
  "status": "verified",
  "fetched_via": "deepxiv",
  "fetched_at": "2026-05-19T...",
  "title": "Probing single-photon ionization...",
  "authors": ["K. Klünder", "J. M. Dahlström", ...],
  "year": 2010,
  "journal": "Physical review letters",
  "doi": "",
  "arxiv_url": "https://arxiv.org/abs/1012.3863",
  "pdf_url": "https://arxiv.org/pdf/1012.3863",
  "categories": ["physics.atom-ph", "physics.optics"],
  "tags": ["theory", "measurement", "RABBITT", "attosecond"],
  "abstract": "We study photoionization of argon...",
  "key_scientific_questions": [...],
  "core_findings": [...],
  "methods": [...],
  "summary_outlook": "..."
}
```

---

## 6. 调试命令

```bash
# 测试 deepxiv fetch
cd scripts/deepxiv_knowledge/
python3 -c "
from fetch_core import fetch_head, _extract_sections_from_head
d = fetch_head('2403.19535')
print(d['title'])
print('sections:', len(d.get('sections', [])))
"

# 测试 PDF 全文提取
python3 -c "
import sys; sys.path.insert(0, '.')
from pdf_extractor import extract_from_pdf
r = extract_from_pdf('2403.19535')
print('chars:', r['_pdf_chars'], 'Q:', len(r['key_scientific_questions']))
"

# 验证 wiki 报告生成
cd ../wiki_regenerator
python3 run.py
```

---

## 7. 已知限制

1. **physics/9906053 无 PDF**：1999 年旧格式，arXiv 已无存档，仅保留 abstract + tldr
2. **LaTeX 清理**：仅处理 `$math$` 上标（如 `$3s^2$` → `3s²`），复杂 LaTeX 结构简化处理
3. **作者字段**：deepxiv `--head` JSON 的作者列表更可靠
4. **PDF 提取质量**：PRL/Science 等期刊格式需合并断行，部分长段落仍有噪声
5. **PyPDF2 依赖**：`pdf_extractor.py` 依赖 PyPDF2（`~/.venv/bin/python3` 环境内置）

---

## 8. 扩展：添加新论文

### 8.1 添加到论文列表

```python
# scripts/deepxiv_knowledge/run.py 中 MASTER_LIST 追加：
("2501.XXXXX", ["your-tag"], 1),  # priority 1 = 核心
("2501.XXXXX", ["your-tag"], 2),  # priority 2 = 补充
```

### 8.2 运行流水线

```bash
python scripts/deepxiv_knowledge/run.py        # 自动断点续传
python scripts/deepxiv_knowledge/pdf_enricher.py --rebuild  # 全量 PDF 增强
python scripts/wiki_regenerator/run.py        # 重建 wiki
```

### 8.3 搜索新论文

```bash
~/.venv/bin/deepxiv search "your topic" --limit 10 --format json
```
