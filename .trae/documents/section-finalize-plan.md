# 收尾定稿计划 v2（general-order-parameter-ultrafast-readout-20260727）

> 按用户三条硬约束重写：①不覆盖 `last_score`，先交代口径；②参考文献按硬限压到 ≤40 并重排角标；③改正文后对受影响章节重评、报告头带新 sha256。

## 一、任务范围

1. 账本刷新：让 `_lifecycle.json` 反映当前正文的五章终评分数，但**不得**悄悄覆盖 `last_score`。
2. 参考文献：按 `memory/nsfc-standards.json` 的“30–40 篇”硬性条款压到 ≤40 条，全稿角标重排并校验。
3. 定稿检查：`04_proposal/proposal-draft.md` 重组后通读——章节顺序/编号、内部标记、占位、评审口吻。
4. 不碰其他课题；不改 rubric、评分阈值、NSFC 标准数值。

## 二、当前实际状态（已核验，非假设）

| 项 | 实测 |
|---|---|
| `sections/rationale.md` | sha256 `927024e8d2960aa714ba8b48e8f44509a6d9f499cdbdd5735481f96d5c039d0e`，终评 0.85，C0/H0 |
| `sections/content.md` | sha256 `f0704871b5d8155e944d891d9070e9e93e66c546245ea94d68e0ec19a4e4c6c4`，终评 0.85，C0/H0 |
| `sections/scheme.md` | sha256 `2a97baa169f95605f2dcbba66a3f0f65da7abb63fa04a3273ee211d2b1eca0c7`，终评 0.86，C0/H0 |
| `sections/full_review.md` | sha256 `ea37d543703b433a94d2de3e25b86a3aa4b7d500c4acbbd3aaad2f6703480ad2`，终评 0.86，C0/H0 |
| `sections/references.md` | sha256 `efc6bdc8fed4de122899c5afc453d6700a8e718bf3ad6eaf52aeba3ac4e3d6ee`，终评 0.90，C0/H0 |
| `05_review/critic-20261107-final2-*.md` | 5 份均已写入，报告头 sha256 与上表逐一一致（`shasum -a 256` 已复核） |
| `04_proposal/proposal-draft.md` | 112410 B；H2 序列（一）→（五）；正文角标 1–40 全覆盖；占位/内部标记扫描 0 命中 |
| `sections/references.md` | 40 条，编号 1–40 连续，正文引用集合与文献表集合完全相等（missing=[]、uncited=[]） |
| 账本 | `last_score=0.82`、`last_monitor_score=0.81`、`optimization_rounds=0`、`current_round=null`、`pass_number=6` |
| `score_history` | 4 条：r1 rationale 0.81 / r1 content 0.82 / r1 scheme 0.82 / r3 method_manual 0.91 |
| `section_passes` | rationale/content/scheme/full_review=false；references/method_manual=true |
| `pipeline_jobs` | 全部 round=1；剩 writer full_review、critic/writer references、critic/writer method_manual、monitor、update_vision 为 pending |
| 版本 | `VERSION=7.3.62`；CHANGELOG 最新 `v7.3.62` |

## 三、硬约束①：`last_score` 口径判断（结论：不一致）

依据代码事实：

- `scripts/lifecycle/executor.py:1832`：`prop_state["last_score"] = score_after`，位于 `_run_writer_step`，写入的是**当轮单章节** critic 加权分。
- `scripts/adversarial/monitor.py` 的 monitor 步只写 `last_monitor_score` / `monitor_history`，不回写 `last_score`。
- 当前 `last_score=0.82` 与 `score_history` 的 `r1 scheme=0.82` 同值 → 确认为 round 1 scheme 章的 writer 步产物，**不是五章聚合**，也不含 monitor 加权。

结论：**口径不一致**，按用户规则走“不覆盖”分支：

- 不改 `last_score`、`last_dim_scores`、`optimization_rounds`、`section_passes`。
- 新章节分写入 `score_history`（带 `source="section_rereview_backfill"` 与报告路径）。
- 单列 `section_scores_20261107`，并在 `last_score_caliber` 写明不可比原因。
- 报告/上报中显式说明“该值不可与旧 last_score 直接比较，交 11-09 人工判门定夺”。

## 四、待执行改动

### 4.1 扩展 `scripts/backfill_manual_rereview.py`：新增 `--sections` 模式

保留原 method_manual 默认行为，新增分支：

1. **CLI**：`--sections`（与默认手册模式互斥）；`--proposal <pid>` 复用；`--dry-run` / `--apply` 语义不变；`--self-check` 扩一条用例。
2. **报告发现**：对 `rationale/content/scheme/full_review/references` 各在 `05_review/` 内 glob `critic-*.md`，筛 `name.endswith(f"-{section}.md")` 且 `size > 100`，取 `mtime` 最新一份。
3. **sha256 闸门**：从报告头正则 `评审时 sha256：`\``([0-9a-f]{64})`\`` 取值；对 `04_proposal/sections/<section>.md` 现算 `hashlib.sha256` 比对；不一致或缺失 → 跳过并给出双方值（严禁回填旧报告）。
4. **解析**：复用 `ProposalLifecycle._extract_score({"output": text})`、`_extract_dimension_scores`、`_extract_issues`，与 `scripts/rebuild_lifecycle.py:183-199` 同源；维度完整性用 `lifecycle.executor.judge_dims_partial(section_key, dims)`。
5. **过线判定**：`score >= lc._get_quality_threshold(project_type)["min_overall_score"]`（general=0.85）且按 `lc.DIMENSION_FLOOR` 无短板维度、且 `count_blocking_issues(text) == 0`。
6. **入史条目**（`round=1`，与当前 `pipeline_jobs` 轮次一致，避免虚构轮次）：

   ```json
   {"round":1,"score":0.85,"score_raw":0.85,"dim_scores":{...},
    "weakest_dim":"expression","focus_section":"rationale","section_passed":true,
    "issues_count":0,"high_issues":0,"caliber":"section_4d","dims_partial":false,
    "source":"section_rereview_backfill",
    "report":"optimizing/<pid>/05_review/critic-20261107-final2-rationale.md",
    "backfilled_at":"<UTC>","at":"<UTC>"}
   ```

   references 用 `caliber="references_2d"`、`score_raw=null`（2 维口径不参与 `score_raw` 判定，见 `a_gate.py:180-183`）。
7. **幂等**：`report` 相对路径已存在于 `source=="section_rereview_backfill"` 的条目中则跳过。
8. **落盘字段（apply 时）**：

   ```json
   "last_score_prev": 0.82,
   "last_score_caliber": "0.82 为 round 1 scheme 章 writer 步写入的单章加权分（executor.py:1832），非五章聚合、不含 monitor 加权；与 section_scores_20261107 不可直接比较。",
   "section_scores_20261107": {
     "review_date": "2026-11-07",
     "caliber": "章节 section_4d / 参考文献 references_2d",
     "sections": {"rationale": {"score":0.85,"dims":{...},"section_passed":true,
                                "report":"...","sha256":"..."}, "...": {...}},
     "aggregate": {"min":0.85,"mean_section_4d":0.855,"critical":0,"high":0},
     "gate_note": "section_passes 布尔未改动，保留至 11-09 人工判门；自动晋级仍被 monitor 0.81 < 0.85 阻断。"
   }
   ```

9. **不改**：`last_score`、`last_dim_scores`、`optimization_rounds`、`section_passes`、`current_round`、`pipeline_jobs`。
10. **写盘安全**：`--apply` 先 `shutil.copy2` 备份到 `_lifecycle.json.bak-sections-<ts>`，再 `common.file_lock("proposal-lifecycle")` + `common.save_json`。

### 4.2 运行与校验

```bash
python3 scripts/backfill_manual_rereview.py --self-check
python3 -m py_compile scripts/backfill_manual_rereview.py
python3 scripts/backfill_manual_rereview.py --sections --proposal general-order-parameter-ultrafast-readout-20260727 --dry-run
python3 scripts/backfill_manual_rereview.py --sections --proposal general-order-parameter-ultrafast-readout-20260727 --apply
```

dry-run 必须五章全部命中、sha 全一致、分数与上表一致才 apply；任何一章解析失败即中止，上报错误形态（不填估算值）。

### 4.3 CHANGELOG + 版本

- 领号：`grep -E '^## v' CHANGELOG.md | head -3` → 当前最新 v7.3.62，新条目取 **v7.3.63**。
- 追加 `## v7.3.63 - 2026-11-07 章节终评回流：backfill_manual_rereview 新增 --sections（sha256 闸门 + 不覆盖 last_score）`，含验证结果。
- `VERSION` 同步为 `7.3.63`；跑 `python3 -m unittest scripts.tests.test_version_monotonic`。

### 4.4 定向提交（AGENTS §自动提交规则）

只 `git add` 本次涉及文件，不用 `git add -A`（避免扫入并行 agent 的改动）：

`scripts/backfill_manual_rereview.py`、`CHANGELOG.md`、`VERSION`、本课题 `04_proposal/sections/*.md`、`04_proposal/proposal-draft.md`、`05_review/critic-20261107-final2-*.md`、`research_proposals/_lifecycle.json`。

## 五、验证清单

1. `--self-check` 全绿；`py_compile` 无错。
2. dry-run/apply 输出五章 `score / dims / passed / sha256`，与 §二 表格逐项一致。
3. apply 后复查：`last_score` 仍为 0.82；`last_score_prev=0.82`；`last_score_caliber`、`section_scores_20261107` 存在；`score_history` +5 条且 `source` 可溯源。
4. 参考文献复核：40 条、1–40 连续、正文引用/文献表集合相等、无悬空/重复（脚本已验，apply 后再跑一次）。
5. draft 复核：H2（一）→（五）、无 `待定/待补/TODO/TBD/rubric/轮次/Q 标记`、无评审口吻残留。
6. `test_version_monotonic` 通过。

## 六、边界

- 不动 `last_score`、不动 `section_passes`、不动 rubric/阈值/NSFC 标准；不碰其他课题。
- 不为了凑数删正文实际引用的文献（已压到 40，全部条目仍被正文引用）。
- 若某章重评 <0.85：如实上报（当前 final2 五章均 ≥0.85，无需回退）。
