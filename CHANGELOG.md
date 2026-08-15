# 变更记录

## v6.9.8 - 2026-08-15 周末流水线架构加固（评估五项改进全部落地）

架构评审结论："好架构欠了三笔小债"——核心决策（checkpoint 化/四层自愈/
模板幂等）正确，扣分集中在语义一致性层面。本次逐项落地全部改进。

- **P0 dry-run 零落盘**：`run_next`/`run_stage` 在 dry_run 时不持久化
  状态（此前预览会把假 done 写入状态文件，input/reflection 无自愈兜底，
  要等 6 天跨周重置才能恢复）。配套修复 dry-run 循环终止条件（零落盘
  下每轮磁盘 reload 会无限重复 pick 同一 pending job——dry-run 改为仅
  首轮 reload、复用内存状态推进）。
- **P1a 声明式产物校验**：job 模板新增 `artifact` 字段（PROJECT_ROOT
  相对路径 + `{date}` 占位符），`_verify_artifacts` 从 output 专用硬编码
  map 通用化为三阶段统一读取声明；`{date}` 以 job 自身 `finished_at`
  格式化（旧实现取检查当日，cron 晚一天跑就误重置）。`sync_stage_jobs`
  增加字段级合并：旧 state 已有 job 自动补齐 artifact 声明（零迁移）。
  顺手修复级联重置同一下游被重复遍历（日志重复 3 次）。
- **P1b handler 二元组注册**：注册 key 统一为 `(stage, step)`，消灭
  "job_id 优先、step 回退"双命名空间（同名 step 静默错绑风险）。原
  `STEP_KB_MAINTAIN` 拆分为 `STEP_KB_DEEP_HEALTH` + `STEP_KB_MERGE`
  （现 state 未含 v6.9.6 新 job，周日 reflection cron 尚未首跑，零迁移
  成本）。
- **P2a processed_sources 滚动裁剪**：`trim_processed_sources` 保留 28 天
  （实测 291 条只增不减），与 error_history 策略对齐；旧格式（纯字符串
  无时间戳）与缺 processed_at 记录保留不误删，sync 时自动触发。
- **P2b 锁粒度细化**：① `common.file_lock` 新增 `blocking=False` 参数
  （非阻塞抢锁失败抛 TimeoutError）；② `run_stage` 从整阶段一次持锁
  （LLM 慢时段可达数小时）细化为每 job 一持一放，worker 可在间隙抢锁
  协作推进；③ `run_next` 非阻塞抢锁，锁忙温和退出（skipped=lock_busy），
  杜绝 worker cron 每 20 分钟 spawn 的进程在 flock 上堆积。
- **潜伏 bug 顺手修复 2 个**：① `JOB_STATUS_FAILED` 从未进入 pipeline
  import，run_stage 汇总段在"部分失败"路径必抛 NameError（此前因
  all()/any() 短路从未触发）；② `input_summarize` 无新论文时提前
  return 不写产物文件——实测 08-14 周六该路径真实发生，产物缺失被
  新校验正确捕获并重置，修复后无条件写空 summaries 防重置空转。
- **验证**：新增回归 `tests/test_weekend_pipeline_hardening.py`（11 用例
  35 断言，覆盖 dry-run 落盘/产物校验三阶段/finished_at 防错位/字段级
  合并/二元组完整性/裁剪/非阻塞锁/温和退出/per-job 锁等价性），注册进
  `--module` 基线 622 → **657/657** 全绿；真实环境 `--input --dry-run`
  实测：input 7 job 补齐 artifact、假 done 自愈重置、processed_sources
  裁剪无副作用。

## v6.9.7 - 2026-08-15 体检修复：kb_distill 蒸馏页 created 时间戳冻结

- **缺陷**：`kb_distill._ensure_source_raw` 硬编码 `now = "2026-08-15T00:00:00Z"`。
  蒸馏系统提示要求 LLM"直接输出 Markdown 正文（frontmatter 由系统补写）"，
  即"无 frontmatter → 构造合规头"是**主路径**而非边缘分支——lc-kb-distill
  cron（每日 12:50，5 篇/天）产出的新页 `created` 将全部冻结在 2026-08-15，
  系统性污染 KB 新鲜度指标（kb_health）与 growth_engine 晋升时序。
- **修复**：改为 `common.now_utc()` 取真实当前时间（最小化定向修复，
  `save_distilled_wiki` 门面确认不覆盖 created/updated，冻结值会原样落盘）。
- **验证**：`kb_distill.py --self-check` 新增第 5 项断言（created 与当前
  时间差 <24h）5/5 通过；新增回归测试
  `tests/test_kb_distill_created_ts.py`（5 断言）注册进 `--module` 基线，
  617 → **622/622** 全绿。
