# 健康检查报告 · 2026-08-10 20:00（过去 4 小时）

> 检查窗口：2026-08-10 08:00 UTC ~ 2026-08-10 12:00 UTC（本地 16:00–20:00）
> 检查工具：v6.8.21 健康检查脚本（4h 周期）
> 状态：**发现并已修复 1 个高优先级知识出口缺陷**（v6.8.21）

---

## 一、关键结论

| 维度 | 结论 | 证据 |
|------|------|------|
| 申请书格式完整性 | 5 个 optimizing 课题持续推进，1 个完成轮次 | `system-kanban.json::execution_history` |
| 任务阻塞 | 4h 内无新增失败任务；1 处已知 transient（API 429）已 natural fallback | `--module` 335/335 通过 |
| 崩溃风险路径 | v6.8.21 新发现并修复 unhashable TypeError 静默吞掉路径 | `logs/linsai.log` 18:57:18Z |
| 知识出口 | **v6.8.21 修复前**：10 篇论文静默丢失；**修复后**：可正常入库并返回真实计数 | 看板面板 + 测试 5 项新增 |
| 资源管理 | 无新发现的泄漏/无限循环 | — |

---

## 二、本轮发现的关键缺陷（已修复）

### Bug：知识库入库 unhashable 静默失败（critical）

- **位置**：
  - 根因：`scripts/kb_text.py:99` `build_frontmatter` 对 list 元素无条件 `set.add`
  - 上游触发：`scripts/literature_service.py:1013-1054` `_ingest_new_papers`
  - 上游静默：`scripts/literature_service.py:1052-1054` 内部 `except Exception` 吞掉
  - 外层虚报：`scripts/lifecycle/executor.py:601` 用 `len(new_papers)` 替代真实计数
- **触发场景**（具体、可信）：
  1. 微调度器派 `lit_search` 给 `general-bsv-driven-hhg-quantum-20260726` 第 6 轮
  2. hermes researcher agent 返回 10 个论文 JSON 数组（arxiv_id/title/authors/year/score/tldr）
  3. `LiteratureService.search()` 将每个论文封装为 `paper` dict（line 1042-1044），其中
     `status_history = [{"status": "pool", "at": ..., "by": "literature_service"}]` 是 List[Dict]
  4. `_ingest_new_papers` 调用 `build_frontmatter(fm)`，遍历到 `status_history`
     时进入 `isinstance(val, list)` 分支，执行 `seen.add(v)` —— `v` 是 dict，**不可哈希**
  5. 抛 `TypeError: unhashable type: 'dict'`，被内部 `except Exception` 吞掉
  6. **10 篇论文无一落盘**，但 `executor.py:601` 仍打印
     `lit_search 新入库 10 篇论文到知识库`（错误地使用 `len(new_papers)`）
  7. `lit_read` 因无 arxiv_id 可读而整体跳过该轮，`writing` 阶段无法基于新论文
     优化申请书引文
- **实证（4h 窗口）**：
  - `logs/linsai.log` 2026-08-10 18:57:18 连续 10 条：
    `[WARNING] [LiteratureService] 入库失败 2311.11257: unhashable type: 'dict'`
    （arxiv_id 2305.16831、2406.10443、2409.13614、2311.10390、2505.22536、
    2407.04755、2206.01042、2003.00277、2106.00372 同样失败）
  - 同一秒 `[INFO] [general-bsv-driven-hhg-quantum-20260726] lit_search 新入库 10 篇论文到知识库` —— 与上面 10 条 WARNING 同帧打印，日志与实际严重不一致
  - 后续 `lit_read 跳过: 无 arxiv_id 可读（lit_search 未返回论文）`，本轮引文校验阶段完全跳过
- **影响**：
  - **知识出口被静默阻塞**：10 篇关键论文（Even Tzur 2023/2024、Boroumand 2025、
    Lewis-Swan、Pisanty 等量子光场 HHG 奠基文献）未能进入 KB
  - `knowledge_output.process_daily_sources` 依赖 `lit-gap-*.md` 萃取可靠知识，
    所有依赖这些论文的 KB 笔记（人物/方法/概念）将持续缺失关键引用
  - **`lit_read` 阶段整体跳过**，申请书引文校验阶段无法补全
  - 直接威胁申请书高质量产出：general-bsv-driven-hhg-quantum 是 v6.8.20 后
    唯一稳定聚焦的课题（其余 4 个 optimizing 课题因 cron 残留导致轮转漂移），
    其高质量引文支撑是 0.74 → 0.80 晋级的关键

### 修复（最小化、定向、高置信度）

1. **`scripts/kb_text.py:99` — `build_frontmatter` 容错扩展**
   - 在 list 非空分支用 try/except 包裹原去重路径
   - 仅捕获 `TypeError`（含 `unhashable type`），其他异常照常传播
   - 异常时回退为 `json.dumps(val, ensure_ascii=False)` 序列化（保留顺序）
   - 字符串列表保持 `["a","b","c"]` 原输出形式（向后兼容，Obsidian 解析不受影响）
2. **`scripts/literature_service.py:997` — `_ingest_new_papers` 返回真实计数**
   - 返回 `{"ingested": int, "failed": int, "skipped": int}`（替换之前的 `None`）
   - 在 `except` 分支增加 `failed += 1`，在 `_needs_metadata` 分支与
     `raw_path.exists()` 分支增加 `skipped += 1`，在 `write_text` 后增加
     `ingested += 1`
3. **`scripts/lifecycle/executor.py:601` — 用真实计数替代虚报**
   - 日志格式变为 `lit_search 新入库 X/N 篇论文到知识库 （failed=Y, skipped=Z）`
   - 运维侧一眼可分辨真实入库/失败/跳过
4. **零重构**：不改 dedup 逻辑主路径，不改其他调用方，不改 YAML 字符串格式约定

### 回归测试（新增 5 项 / 15 断言）

| 测试 | 守护行为 |
|------|----------|
| `_test_build_frontmatter_string_list_preserves_old_behavior` | 字符串列表走原 dedup 路径（向后兼容） |
| `_test_build_frontmatter_dict_list_no_unhashable` | `status_history` List[Dict] 不抛 TypeError，保序输出 JSON |
| `_test_build_frontmatter_mixed_list_falls_back_to_json` | 混合列表（hashable + dict）保守走 JSON |
| `_test_ingest_new_papers_returns_counts` | 返回 dict 含 `ingested/failed/skipped`（替换 None） |
| `_test_ingest_new_papers_handles_unhashable_dict_list` | 端到端：含 `status_history` 的论文能成功落盘到 `RAW_DIR/papers/` |

---

## 三、未发现缺陷的维度

- **cron / 定时任务**：v6.8.18 已修复幂等性，v6.8.19 prompt 变量已修，v6.8.20 微调度器轮转已修
  - 4h 内微调度器在 slot 内每 5 分钟启动，符合 v6.8.20 设计
  - cron 残留（jobs.json 中 32 个 vs 合理 ~13 个）仍存在但已知遗留（建议用户一次性 `--setup-cron-v2` 收敛）
- **任务阻塞**：仅 1 处 transient `超时(900s)`（bsv-driven-hhg writer 11:30Z），下个 cron 重试成功
- **资源管理**：本次未发现新内存/句柄泄漏
- **飞书通知链路**：lark-cli 未配置，告警仅写入 `monitor-alert-cache.json`（已知遗留）
- **persona 注入**：38/38 通过
- **场景剧本**：16/16 通过
- **web API**：403/403 通过

---

## 四、修复后校验

| 测试套件 | 基线 → 新结果 |
|----------|---------------|
| 新增 v6.8.21 守护测试 | 5/5（15 断言）✅ |
| `test_literature_service.py` | 7 → 12 项测试（+5）✅ |
| `--module` | 320 → **335/335**（+15 断言）✅ |
| `--scenario` | 16/16 ✅ |
| `--persona` | 38/38 ✅ |
| `--web-ci` | 388 → **403/403**（+15）✅ |
| `py_compile scripts/*.py` | 全部通过 ✅ |

---

## 五、版本变更

- 新版本：**v6.8.21**（知识库入库 unhashable 静默失败修复 + 真实入库计数回归）
- CHANGELOG 已记录（含实证证据 + 影响范围）
- git 待提交：`scripts/kb_text.py` / `scripts/literature_service.py` /
  `scripts/lifecycle/executor.py` / `scripts/tests/test_literature_service.py` /
  `VERSION` / `CHANGELOG.md`

---

## 六、用户可继续执行的操作（不阻塞，影响小）

- **建议**：一次性运行 `--setup-cron-v2` + `--setup-monitor` 收敛 cron 实例（32 → ~13）
- **可选**：配置 lark-cli 以启用飞书告警

---

*报告生成时间：2026-08-10 12:08 UTC*
*健康检查工具版本：v6.8.21*