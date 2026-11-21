# 存档：automation-89b6c9f1 prompt（2026-11-20 删除，供未来重建）

> automationId: automation-89b6c9f1-4ec0-4f29-80a1-918ac1cb158b
> 标题：知识库方法卡回补·每小时 :20 定时批（ZCode 直提 20 页·全库模式）
> cron: `*/30 * * * *`（实际为每 30 分钟）
> 删除原因：方法卡回补收官（3929/3929 清零 2026-11-19），空转 2425 次
> 重建方式：ZCode CronCreate 按下列 prompt 原文重建（仅在有新回补需求时）

---

在 /Users/ll/Desktop/LinSai-CoPilot 项目执行知识库方法卡回补定时批次（v7.0.7 零 LLM 架构——由你（ZCode）读页面后亲自撰写方法卡，全程禁止调用项目的 llm_gateway/llm_complete/_llm_json/hermes CLI/kimi/MiniMax 等任何外部 LLM）。

背景：课题相关优先集已于 2026-09-27 消化完毕（ok 116 页）；本任务自 now 起以 --all 全库模式消化剩余 A 级存量（约 1090 页，多为旧文献题录级页面，预计相当比例会被正确判为 no_method 或薄卡）。

执行步骤：
1. `cd /Users/ll/Desktop/LinSai-CoPilot/scripts && python3 kb_methods_backfill.py --worklist 20 --all` 发射全库待处理页面清单（memory/methods-backfill-worklist.json）。若清单为 0 页且 kb_methods_backfill.py --status 显示无 tagged/pending 遗留，说明全库 A/B 级已消化完毕，直接跳到第 4 步报告收官。
2. 逐页处理（核心工作由你完成）：
   - Read 页面 knowledge/wiki/papers/{page}.md（B 级条目有 fulltext 路径时可再读原文）
   - 按方法卡标准撰写：method_name（方法名）、principle（测什么/算什么+核心机制两三句）、params（参数表数组 {item, value, source}——数值必须来自页面原文含单位，source 写页面内出处小节名，无依据的参数不写）、boundary（适用边界）、representative（代表作）；页面确无实质方法内容则记 no_method；摘要级来源（digest_level=abstract 或正文极短，如 70-80 行的题录页）从简写卡不虚构参数，merged stub（frontmatter 含 merged_into）直接记 no_method
   - 每 5-10 页用一次 python3 库调用批量落盘+更新台账（模板，注意键名 = 页面 stem 不带 .md）：

     ```python
     import sys; sys.path.insert(0, '/Users/ll/Desktop/LinSai-CoPilot/scripts')
     from kb_methods_backfill import _append_method_card, _load_state, _save_state, PAPERS_DIR
     from common import now_utc
     st = _load_state()
     for page, card in [("stem-1", {...}), ...]:
         _append_method_card(PAPERS_DIR / f"{page}.md", card)
         st["pages"][page] = {"status": "ok", "grade": "A", "at": now_utc()}
     # no_method 页: st["pages"][page] = {"status": "no_method", "grade": "A", "at": now_utc()}
     _save_state(st)
     ```

3. 全部落盘后 `python3 kb_methods_pack.py` 刷新 10 个活跃课题的方法素材包（03_method/kb-methods-pack.md，零 LLM）。
4. `python3 kb_methods_backfill.py --status` 与 `python3 kb_health.py --real`（看 methods_card_coverage.papers_with_card）输出进度报告。

预期交付：本批约 20 页处理（方法卡或 no_method 判定）+ 素材包刷新 + 台账/指标进度报告。不需要 git 提交。

红线：
- 全程禁止调用 llm_gateway/llm_complete/_llm_json/hermes CLI——所有提取由你读文件后直接写出
- 不修改 scripts/ 下的代码文件
- 台账键名必须与 worklist 清单中的 page 名一致（stem、不带 .md），避免幽灵键
- 单次运行时间控制在合理范围：处理完当前已读页面即落盘收尾，剩余留给下次触发（台账断点安全）
