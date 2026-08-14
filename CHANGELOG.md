# 变更记录

## v6.8.51 - 2026-08-14 知识库治理落地：写入链修复 + 索引 v2 瘦身 + 每日调度

### 背景（知识库评估报告逐项落实）
评估结论：知识库处于"高速进料的文献堆场"状态，六条治理机制全部停摆——
写入器双 frontmatter 污染、简报同步断流两个月、索引膨胀 157MB、
kb_auto_sync 无调度从未运行、健康指标装饰性失真、growth_engine 从未启用。
本次按 P0（止血）→ P1（瘦身）→ P2（收敛）九项建议逐项落实。

### P0 止血：写入链修复
- `kb_wiki.py`：`save_wiki_page` 双防御——① 调用方误传整页文本时解析内层
  frontmatter 合并元数据（根治双 FM 污染）；② content 空且非 append 时保留
  原正文不清空。门面统一写生长日志（create/update 自动判定）。
  `_WIKI_TYPES` 补 `reviews`（57 个 review 文件此前对列表完全不可见）。
- `literature_service.py`：`_save_wiki_paper_note` 重写——去掉 `kw_build`
  双重构建、修复 `existing.get("content")`→`body` 的历史覆盖 bug、
  title 优先论文真实题名。
- 新增 `kb_repair_papers.py`（一次性修复工具）：双 FM 拆分合并 95→0、
  裸 arXiv ID 标题回填 68 个（从 raw/ 提取题名）、五目录 type 规范化
  131 处（消灭单复数分裂）。`--self-check` tempfile 隔离通过。

### P0 调度：lc-kb-sync 每日治理 cron
- `lifecycle/constants.py`：`DEFAULT_KB_SYNC_SCHEDULE = "40 12 * * *"`
  （上午时段结束后）+ `KB_SYNC_CRON_NAME = "lc-kb-sync"`。
- `lifecycle/framework.py`：安装流程末尾幂等挂载（cleanup_cron_duplicates +
  cron_create_no_agent）；wrapper 依次执行 `kb_auto_sync.py` 与
  `growth_engine.py --apply`（生长阶段自动晋升，此前从未运行）。
- `lifecycle_monitor.py`：`REQUIRED_CRON_PREFIXES` 追加 lc-kb-sync
  （缺失自动修复 + 告警）。

### P0 简报链：断流两个月修复
- `sync_engine.py`：`sync_research_briefings` 双命名兼容（hermes 2026-06-08
  后改产 `daily_memory_*`）+ 同日双源去重 + 改走 kb 门面写入。
  回补断流简报 26 篇。

### P1 索引 v2：157MB → 20.7MB
- `kb_index.py` 重写：格式 v2（扁平 chunk 数组 + 整型倒排 postings）；
  `kb_text.py` 中文分词 2/3/4-gram 收敛为 2-gram 滑窗；df==1 中文词条剔除
  （67310 词项中无效单现词占大头）；紧凑 JSON + 原子写入。
- 两段式检索：IDF 覆盖率预排序 → top 60 候选精确 TF-IDF 重排。
- 进程内缓存 `_INDEX_CACHE`（path+mtime_ns+size 签名校验）：长驻进程
  重复检索 240ms→6ms。
- **索引漂移修复**：v2 重建发现旧 v1 索引漏 432 个文档（mtime 增量机制
  长期漏文件）；`sync_all` 索引重建从"仅新增论文时"改为无条件
  （v2 全量 ~2s，日频可接受）；`literature_service` 入库后即时重建。
- `kb_cleanup.py`：修复 `step5_rebuild_index` 用简化格式覆写 index.json
  摧毁倒排表的关键 bug，改为委托 `build_index(force=True)`。

### P1 健康指标修正：装饰性 → 真实
- `kb_health.py`：`_compute_category_coverage` 解开双层嵌套；
  CLI 新增 `--real`（经门面注入取真实数据）。实测 wiki_count 212→305。
- `health_sensor.py`：新增知识库四类告警——kb_index_stale（索引停更>48h）、
  kb_growth_stall（生长日志断流>7d）、kb_distill_backlog（蒸馏积压>300）、
  kb_graph_disconnect（连通性<0.50）。信号采集经 facade 降级容错。

### P2 收敛：写入口径统一 + 结构清理
- `weekend_pipeline/output_jobs.py`：`_write_wiki_page` 迁移 kb 门面
  （单数 type→复数规范化，门面异常回退旧直写保可用）。
- `kb_importer.py`：hermes JSON null 字段全量防御（`_nz()`）——修复
  `tldr: null` 导致 `"\n".join` 崩溃（实测导入 19 篇新论文验证）。
- 结构清理：`knowledge/linsai-copilot-overview/` HTML 移至
  `docs/archive/html-exports/`；`docs/ARCHITECTURE.md` 新增"知识库数据
  流转（v6.8.51 重构）"章节（写入口径/每日治理/索引 v2/简报链/健康感知）。

### 实测效果
| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| index.json | 157MB（漏 432 文档） | 20.7MB（1031 文档/14981 chunk） |
| 检索耗时 | ~2-5s | 240ms 首次 / 6ms 缓存 |
| 双 frontmatter | 95 个 | 0 |
| 简报断流 | 2026-06-08 起两个月 | 回补 26 篇，链路恢复 |
| kb 每日治理 | 无调度从未运行 | lc-kb-sync 12:40 每日 |
| growth_stage 晋升 | 从未执行 | 32/32 全部 mature |
| wiki_count（真实） | 212（漏 reviews） | 305 |
| 图谱连通性 | 0.37 | 0.45（孤儿 2→0） |
| week_new | 0（生长日志停写） | 169 |

### 测试
- `self_test --module` 445/445 通过（新增 lc-kb-sync 进 monitor 必需集
  夹具；kb_repair_papers 自检通过）。
- 端到端：kb_auto_sync 完整跑通（此前 LaunchAgent 缺失 + None 崩溃双重
  失效从未成功）；growth_engine --apply 首次执行完成全部晋升。

## v6.8.50 - 2026-08-14 健康运维体系重构：双平面架构（维持+自优化共享证据层）

### 架构设计
两平面共享同一证据层（health_sensor 统一信号），维持平面保运转、优化平面促进化：
- **维持平面**（感知→防御→修复→溯源）：lifecycle_monitor + circuit_breaker + run_repair + 告警落盘
- **优化平面**（证据→干预→验证）：agent-scores + failure_analyzer + prompt_optimizer 基线 + retrospective
- 核心原则：不再依赖"success 标记可信"假设（429 空转三小时零告警的教训）

### 新增模块
- `health_sensor.py`（统一感知层，~270 行）：采集空转检测（done 但 <30s）/API 错误爆发/
  分数骤降（≥0.30）/监控心跳/熔断状态五类信号；`evaluate_risks()` 统一阈值管理。
  直接回归 2026-08-14 真实故障模式（0.81→0.18 伪分数案例）。
- `circuit_breaker.py`（配额熔断器，~230 行）：三态状态机 closed→open（连续 3 次 api_error）
  →probing（冷却 1h 后单 job 试探）→closed/open；非 API 错误不触发；fcntl 锁 + 原子写。
- 接入 `lifecycle/micro_scheduler.py`：派发前询问熔断器，job 结果回报驱动状态机，
  熔断开启即停止本轮派发（熔断器自身故障不阻塞调度——防御的防御）。

### 修改
- `lifecycle_monitor.py`：新增 3.5 感知层信号检查（`_check_health_signals`）；
  `_persist_alerts` 告警落盘独立于飞书（先落盘后通知，恢复时标 resolved_at，保留 100 条）
  ——修复 04:00 lark-cli exit=3 告警丢失问题。
- `lifecycle/orchestrator.py`：`run_repair` 新增 monitor 心跳互查（心跳 >2h 丢失由 repair 侧
  补告警），打破"谁来监控监控者"自引用。
- `profile_health.py`：接入 pipeline_jobs 一手数据源（step→profile 映射），修复日志正则
  脱节导致的 7 profile 全空数据假象；实测产出 writer 93.1%/critic 100% 真实成功率。
- `rebuild_lifecycle.py`：三重安全护栏——①周期过滤（score_history 最后一次轮次回退点为
  当前周期起点，旧周期文件排除）②漂移护栏（重算分差 >0.30 保留现状，--force 可强制）
  ③状态护栏（仅 optimizing 课题参与重算）；新增 --proposal/--force 参数。
  dry-run 实证：瞬态课题 0.81→0.48 污染被正确拦截。
- `prompt_optimizer.py`：`_record_intervention_baseline` 干预效果基线（应用时记录
  agent-scores 快照到 prompt-interventions.json），优化平面"干预→运行→对比→沉淀/回滚"
  闭环的证据锚点。
- `proposal_lifecycle/optimize.py` + `lifecycle/executor.py`：短输出防线改为
  `min_output_len` 参数（实时评审路径 300、解析落盘报告 0），修复 v6.8.46 防线
  误伤单元测试短样本问题。

### 测试（回归基线 445/445，较 v6.8.27 净增 67 个用例）
- 新增 `test_health_sensor.py`（11 用例：四类信号采集+风险评估+时间窗口+正常零告警）
- 新增 `test_circuit_breaker.py`（16 用例：三态全路径+非 API 隔离+持久化+人工复位）
- 修复 `test_optimize_dimension_scores` 3 个被 v6.8.46 防线误伤的用例
- self_test --module 445/445 全量通过；6 个核心专项测试全过

## v6.8.49 - 2026-08-14 项目结构规整与文档现代化（清理 130MB 历史备份 + CHANGELOG 瘦身 + 架构文档更新）

### 清理（结构规整）
- 删除 `_cleanup_backup/`（130MB，8-12 清理操作的临时备份，已 gitignore、系统稳定运行 2 天无回滚需求、零代码引用）。
- 清理 `projects/*/kb/` 下 20+ 空目录树（v3.5 旧 kb 布局残留，仅保留活跃的 graph.json/index.json 数据文件）。
- 保留有代码引用的空"待用槽位"目录（references/papers、research_proposals/drafts 等，代码含 mkdir 自愈）。

### CHANGELOG 瘦身（316KB → 112KB）
- v6.7.7 及更早的 20 个版本条目（3137 行）归档至 `docs/archive/CHANGELOG-archive-v6.0-v6.7.md`。
- 主文件保留 v6.8.x 全部条目 + 归档指引链接。

### 文档归档（陈旧信息清理）
- `deepxiv-knowledge-workflow.md`（5-19，v6 时代流水线，已被多源检索取代）→ archive/
- `CLAUDE-CLI-ADMIN.md`（5-12，三月前工具手册）→ archive/
- `unified-state-sync-design.md`（7-17，"待审批"设计稿）→ archive/
- 零代码引用残留（已验证）。

### 文档更新（反映 v6.8.48 架构规则）
- `README.md`：项目结构段重写（补 research_proposals/logs/backups/notes 等缺失目录，scripts 从 48 个过时清单更新为 116 脚本+8 子包核心结构）；Hermes 团队架构从 v6.6.2 更新到 v6.8（monitor 监察、五模块循环、微调度器 25 job/轮、质量天花板晋级、多源检索、韧性防线、自学闭环）；核心功能表补 6 项 v6.8 能力；开发阶段补 Phase 14-15；版本号 6.1.0→6.8.48。
- `AGENTS.md`：补 v6.8.42-48 增量（多源学术检索、API 故障防线）。
- `docs/README.md`：目录索引同步归档变化与新增维护规范。

### 验证
- 4 个核心模块（external_fetcher/literature_service/prompt_optimizer/proposal_lifecycle.optimize）导入正常。
- 生命周期状态完好（5 课题数据完整）；literature/optimize 回归测试通过。
- 磁盘从 ~2.43G 降至 2.3G（主要回收 _cleanup_backup 130MB）。

## v6.8.48 - 2026-08-14 修复 429 空转污染链：API 错误源头拦截 + 双数据层清洗

### 背景（架构评估逐项核查产出）
- 架构评估发现瞬态课题分数 0.81→0.18 异常，逐项排查定位根因：
  **MiniMax Token Plan 上午耗尽**（gap-analysis JSON 记录 HTTP 429"用量上限"），
  此后所有 hermes job 均为 13-16 秒空转（CLI returncode=0 + 错误文本输出），
  被 `_run_hermes` 记为 success=True，429 文本被解析成伪分数 0.18 污染 score_history；
  同窗口 monitor 空转又触发 R3 双 -10 误扣（v6.8.47 已修下游跳过）。

### 修改（proposal_lifecycle/optimize.py）
- 新增 `_detect_api_error()`：识别 10 种 API 错误特征（429/配额耗尽/余额不足等），
  `_run_hermes` 在 returncode=0 时进一步校验输出，命中特征返回 success=False（源头拦截）。
- `_extract_dimension_scores` 增加短输出防线：<300 字符的输出不产生维度分（纵深防御）。

### 数据清洗
- score_history：移除瞬态课题 round 4 的 3 条伪记录（0.18 等），last_score 恢复 0.81。
- agent-scores.json：回滚 R3 双 -10 误扣，writer/critic 恢复 100.0，清除无 reason 污染条目。

### 验证
- `_detect_api_error` 5 用例（含长输出不误判）通过；短输出拦截用例通过。
- test_optimize_dimension_scores / test_adversarial_governance / test_lifecycle_cron 全通过。
- hermes 探针确认配额已恢复（正常返回）。

### 评估结论修正（逐项核查后）
- rounds=0 两课题：验证为**非缺陷**（r1 进行中 25/30 job done，调度器会续跑剩余 5 个后
  自动推进轮次）；rebuild dry-run 显示直接跑会把瞬态课题 last_score 误算成 0.48
  （旧生命周期 round-8 文件混入），已规避。
- 自学闭环此前评估"数据空缺"系查看位置错误：agent-scores.json 实际活跃（46 条历史）、
  prompt 优化器 8-13 实际修改了 critic/writer SOUL.md（含备份+debug journal 审计）、
  周复盘 8-10 产物存在。自学闭环真实在运转。

## v6.8.47 - 2026-08-14 修复 monitor 解析失败被当作真实 0 分顶格误扣 agent 奖惩

### 背景（设计实现一致性验证 #4/#6 交叉发现）
- key-transient 课题 R3 轮末：monitor 独立评分 0.0（JSON+文本双解析失败，
  `last_monitor_assessment` 为空佐证），但 `apply_monitor_result` 规则层以 0.0
  为真实低分执行奖惩 → writer/critic 各被顶格扣 10 分（monitor_history R3 条目：
  `writer_delta: -10.0, critic_delta: -10.0`），污染全局 agent 分数并经
  score feedback 注入后续 writer prompt。
- 设计意图（v6.8.10）本就要求 0.0 时标记 `monitor_score_valid=false`，但该标志
  此前只用于记日志，未传入下游奖惩——设计实现不一致。

### 修改
- `adversarial/monitor.py`：返回 dict 新增 `monitor_score_valid` 字段
- `adversarial/scoring.py`：`apply_monitor_result` 检测到
  `monitor_score_valid is False` 时跳过规则层/建议混合/串通惩罚（delta=0），
  仅记录 history 与违规；旧调用无该字段时行为不变（默认有效）
- `collusion_risk` 取值移至分支外，避免无效分支引用未定义变量

### 测试（test_adversarial_governance.py 新增 3 项断言）
- `_test_invalid_monitor_score_skips_penalty`：无效分 → delta 双 0；
  兼容性控制组：无标志旧调用 → 仍按原逻辑扣分
- 全量回归 445/445 通过；py_compile 通过

## v6.8.46 - 2026-08-14 修复学习周期多源分发缺口（openalex 等新源全部落入 unknown source）

### 背景
- v6.8.42 将 `openalex` 纳入 `discover_learning_opportunities` 默认源，但
  `run_learning_cycle` 的源分发器未同步：仅处理 arxiv/web/raw，
  多源论文全部落入 `unknown source: openalex` 失败分支，学习周期内无法进入知识库。
- 顺带修复同类历史缺口：`wikipedia` 一直在默认源列表但从未被分发。

### 修改（learning_engine.py）
- 新增 `openalex/semantic_scholar/pubmed/crossref` 分发分支：
  - 含 arXiv ID → 复用 `distill_arxiv_paper`（PDF 下载 + 精读）
  - 仅 DOI → 复用 `arxiv_paper` 蒸馏 prompt（元数据驱动），
    落盘 `wiki/papers/doi-<slug>.md`，slug 约定与 literature_service v6.8.44 一致（`.`/`/` → `-`）
- `wikipedia` 词条复用 `distill_web_search`（数据结构一致）

### 测试（tests/test_learning_cycle_dispatch.py，新增 11 项断言）
- openalex 含 arXiv ID → 走 arXiv 蒸馏；仅 DOI → 落盘 doi-slug；wikipedia → web 蒸馏；
  未知 source 控制组仍正确失败
- 纳入 `self_test --module` 注册表；全量回归 442/442 通过；py_compile 通过

### 备注
- 版本号与提交内容说明：生命周期管线的 references 多源提交（7687d69，v6.8.45）在
  全量暂存时误将本修复的早期草稿一并入库（该草稿引用未定义的 `_cache_key`、
  使用不支持的 `academic_paper` 蒸馏类型）。本 v6.8.46 为净修正版：
  改用 `safe_filename` + 受支持的 `arxiv_paper` 类型 + `path=None` 初始化，
  DOI slug 约定与 literature_service 对齐。两提交并行产生，CHANGELOG 结构冲突已还原。

## v6.8.45 - 2026-08-14 多源检索接入 references 校验：期刊论文进入文献补充报告

### 背景
- v6.8.43 打通期刊论文入库后，生命周期 references 校验步骤仍只依赖 hermes researcher 单一检索途径。
- 当 hermes 超时/限流无返回时，文献补充报告为空，writer 无新文献可引用。

### 修改（proposal_lifecycle/optimize.py）
- `_run_literature_searcher` 新增多源检索补充层：在 hermes 联网检索后，叠加 `external_fetcher.search_academic`（OpenAlex + arXiv）结果。
- 去重机制：按 arxiv_id / DOI / title 三级标识与 hermes 结果对比，避免重复推荐。
- 检索报告新增「多源学术检索补充」小节，含期刊论文（DOI 标识）和预印本（arXiv 标识），显示引用数/期刊/摘要。
- 返回判断修正：hermes 无结果但多源有结果时也返回成功（`total_papers = hermes + 多源`）。
- 关键词组合取前 2 个（避免超长查询触发 OpenAlex 限制）。
- `fetch_openalex` 超时从 15s 提升到 20s + 2 次重试，SSL 握手波动时更快降级。

### 验证
- 端到端模拟（hermes 无结果场景）：多源检索成功补充 10 篇（含 Nature Communications/PRA/Nano Letters 等期刊预印本）。
- 网络波动场景（OpenAlex SSL 超时）：arXiv 源自动接管返回 10 篇，链路未中断——验证多源降级健壮性。
- `test_literature_service.py` 全量通过；py_compile 全量通过。

### 当前闭环
```
critic references 评审 → gap_identifier 识别缺口 → literature_searcher:
  ├─ hermes researcher 联网检索（主）
  └─ search_academic(arXiv + OpenAlex) 多源补充（v6.8.45 新增）
→ 文献补充报告（含期刊论文 DOI）→ writer 修订 references.md → CitationManager 入库
```

## v6.8.44 - 2026-08-14 修复 DOI 论文文件名有损命名（回归测试新失败）
### 背景
- v6.8.43 新增的 `_test_ingest_doi_paper_without_arxiv_id` 用例在回归测试中失败：
  `_safe_filename` 会剥掉 DOI 中的 `.` 与 `/`，产生有损文件名 `doi-101038s41567-018-0315-5`，
  与测试期望的点转连字符 `doi-10-1038-s41567-018-0315-5` 不符。该用例自 v6.8.43 提交起从未通过。

### 修改（literature_service.py）
- DOI 标识符生成前先将 `.` 与 `/` 转为 `-`，再经 `_safe_filename` 清洗，
  保留 DOI 结构可读性并降低不同 DOI 因剥点导致文件名碰撞的风险。

### 验证
- 全量回归 `self_test --module`：431/431 通过；py_compile 通过。

## v6.8.43 - 2026-08-14 打通期刊论文入库：无 arXiv ID 论文以 DOI 进入知识库

### 背景
- v6.8.42 新增多源检索后，发现闭环缺口：`LiteratureService._ingest_new_papers` 以 `arxiv_id` 为唯一标识，
  OpenAlex/Crossref 检索出的期刊论文（无 arXiv ID）在入口处被直接 `continue` 丢弃，多源成果进不了知识库。
- 用户确认保持无 key 配置（压力测试：OpenAlex 无 key 12/12 成功均 1.6s，PubMed 5/5；S2 429 自动降级）。

### 修改（literature_service.py）
- `_ingest_new_papers` 支持无 arXiv ID 但带 DOI 的论文：
  - 标识符回退链：`arxiv_id` → `doi-<safe-slug>`，两者皆无则跳过
  - frontmatter 新增 `doi` 字段（还原 DOI 前缀 `https://doi.org/` / `doi:`）
  - 期刊论文正文追加 DOI 链接行；`source` 保留真实来源（openalex/pubmed 等）
  - `abstract` 前 200 字符写入 frontmatter（原为空）
- 文件名规范：`{year}-doi-{safe-slug}-{title-slug}.md`，与 arXiv 论文并存于 raw/papers/

### 测试（tests/test_literature_service.py，-2 新增用例）
- `_test_ingest_doi_paper_without_arxiv_id`：DOI 期刊论文成功入库（文件落盘、frontmatter 含 doi、正文含 DOI 链接）
- `_test_ingest_paper_with_neither_id`：无标识论文不污染知识库
- 全量回归通过（隔离目录，零污染）；py_compile 全量通过

## v6.8.42 - 2026-08-14 论文检索多源化：新增 OpenAlex/Semantic Scholar/PubMed/Crossref，修复 arXiv 检索隐性故障

### 背景与验证
- 用户要求丰富论文来源。逐一验证候选途径畅通性与可靠性：
  - 畅通且高质量：**OpenAlex**（HTTP 200，期刊/作者/DOI/引用/摘要齐全）
  - 畅通但定位不同：**Crossref**（HTTP 200，但关键词搜索相关性差，定位为 DOI 元数据补全）；**PubMed**（HTTP 200，物理覆盖有限，作通用兜底）
  - 受限：**Semantic Scholar**（无 key 共享 IP 常 429，需配置免费 key）；**arXiv 官方 API**（2026-02 起 export.arxiv.org 限流加严，当前实测持续 429）
- 验证期间发现两个既有故障：
  1. `fetch_arxiv` 隐性瘫痪：deepxiv 返回的 `authors` 元素类型不一致（dict/str 混排），
     原实现 `a.get("name")` 遇 str 直接异常并被吞掉 → **arXiv 检索一直静默返回空**。
  2. 沙箱 Python SSL 证书链失效（默认 CA 指向不存在的路径）→ urllib HTTPS 请求全部失败。

### 新增（external_fetcher.py）
- 新增 4 个学术检索源：`fetch_openalex`（240M+ works，含期刊论文）/ `fetch_semantic_scholar`（可选，配置 key 后稳定）/ `fetch_pubmed`（通用兜底）/ `fetch_crossref_doi`（已知 DOI → 权威元数据补全）。
- 新增 `search_academic()` 多源聚合：按 DOI/arXiv ID/标题去重合并，任一所源失败（限流/超时）不影响其它。
- `discover_learning_opportunities` 默认源扩展为 `[arxiv, openalex, wikipedia, raw]`，`learning_engine` 近 30 天论文候选也升级为多源。
- API key 支持：`.env` 中 `OPENALEX_API_KEY` / `SEMANTIC_SCHOLAR_API_KEY`，缺失时自动匿名降级。
- `score_opportunity` 可靠性权重增加 openalex=0.85 / crossref=0.9 / pubmed=0.85 / semantic_scholar=0.85。

### 修复
- `fetch_arxiv` authors 解析兼容 dict/str 混排（恢复 arXiv 检索能力）。
- 新增 `_make_ssl_context()`：依次探测 env/系统/Homebrew CA 路径，全部失败才降级无验证（仅只读元数据抓取）。
- 自检日期断言改为相对日期，避免随日期漂移。

### 验证
- `external_fetcher.py` 全项自检通过（fetch_arxiv 10 篇 / OpenAlex 3 篇含 Nature Physics DOI / 聚合去重 / 评分 / 统一发现 12 项）。
- `test_literature_service.py` 通过；py_compile 全量通过。

## v6.8.41 - 2026-08-14 提交瞬态量子相课题自动优化产出（补记）

- 生命周期系统自动完成 key-transient-quantum-phase 第三轮优化（critic 评审/文献缺口分析/定向补研/proposal 5 模块修订/知识库同步），19 个文件 +1624/-1035。

## v6.8.40 - 2026-08-14 修复 hermes agent 子进程缺进程组清理导致孤儿 gateway 进程风险

### 问题
- 健康检查发现 key-transient r3 `lit_read` job 运行 30 分钟被 stale 检测标记失败
  （"运行超时/进程僵死"，attempts=1）。
- 追踪执行路径发现：`hermes_memory._run_hermes_agent` 使用 `subprocess.run(timeout=N)`
  未做进程组清理，与 `proposal_lifecycle/optimize.py` v6.8.3-fix9 已修复的模式不一致。
  该函数被 lit_read/lit_search/gap_identify 及 literature_service 深度阅读路径使用。
- 触发场景：hermes CLI 超时后 fork 的 gateway worker 进程成为孤儿，继续占用 CLI
  端口/管道并累积消耗资源（2026-07-26 机器冻结事故同类风险）。

### 修复
- `hermes_memory._run_hermes_agent` 改为 `Popen + start_new_session=True + os.killpg`
  进程组清理模式（与 optimize.py v6.8.3-fix9 一致），超时/异常时清理整个进程组。
- 新增 `tests/test_hermes_agent_process_group.py`（12 断言）验证 start_new_session、
  超时 killpg、返回契约，并纳入 `self_test.py --module` 回归列表。

### 验证
- py_compile 通过；self_test --module 423/423 全绿（原 411/411 + 新增 12）

## v6.8.39 - 2026-08-14 修复生命周期衍生步骤超时偏紧导致轮次卡死风险

### 问题
- 健康检查发现 key-transient r1 `update_method_manual` 实测超时(300s)（2026-08-13T19:05-19:10Z）。
- 根因：`lifecycle/executor.py` 的 `_run_update_vision_step` / `_run_update_method_manual_step`
  硬编码 `timeout=300`，与 v6.8.37 已修复的 references/critic 超时问题同源。该步骤是轮次链
  末端，300s 超时若持续触发，repair 重试 3 次耗尽后轮次无法完成、课题卡死。

### 修复
- `executor.py` 两个衍生步骤超时 300s→600s，与 v6.8.37 references/critic 修复策略一致。
- 新增 `tests/test_derived_step_timeout.py`（5 断言）验证两步骤 `_run_hermes` 调用 timeout=600，
  并纳入 `self_test.py --module` 回归列表。

### 验证
- py_compile 通过；self_test --module 411/411 全绿（原 406/406 + 新增 5）

## v6.8.38 - 2026-08-13 修复 missing_sections 初始化后不刷新导致 critic 误聚焦

### 问题
- 反馈机制核查发现：`missing_sections` 字段只在课题初始化时写入（initialization.py），
  之后 writer 补全模块也不刷新，停留在旧值。moire 标缺 innovation/plan/outcome、bsv 标缺
  innovation/plan/references，但这些模块要么不在 5 标准模块内、要么实际文件都已存在。
- 该过时列表传给 critic 供「重点检查」，让 critic 白检查已存在的模块，影响反馈精度
  （不影响评分，因 critic 实际检查会发现模块存在）。

### 修复
- `optimize.py` 在每轮 critic 评审前，基于实际 sections 文件重算 missing_sections
  （`section_exists` 内容>50字判定），并回写 prop_state。让 critic 始终聚焦真正缺失/空置
  的模块。验证：moire/bsv 重算后 missing 从过时值正确刷新为 []（5 标准模块实际都在）。

### 验证
- py_compile 通过；self_test --module 406/406 全绿

## v6.8.37 - 2026-08-13 修复 references/critic 检验超时阈值偏紧导致课题卡住

### 问题
- 晚间时段检查发现 general-quantum-geometry-inversion 的 references/critic 检验连续 3 次
  超时(300s)、重试耗尽后 stuck，本轮 references 模块缺失。
- 根因：`_run_critic` 的 references 分支用 `min(timeout, 300)` 把检验硬限在 300s
  （v6.8.3-fix10 刻意设为「轻量化」），但调用方传入 `critic_timeout=600`，且 references
  丰富的课题实际需 >300s；与 constants.py「critic 900s」的设计意图也不符。

### 修复
- `optimize.py` references 检验超时 `min(timeout, 300)` → `min(timeout, 600)`：与调用方
  critic_timeout 默认值一致，仍短于主 critic 900s（references 不评创新/可行性，较轻）。
- 运行时重置 general-quantum-geometry-inversion 卡住的 references/critic job（attempts=3/failed
  → 0/pending），其依赖 full_review-writer 已 done，下个时段将用新阈值重跑。
  （该重置为运行时状态，记于 _lifecycle.json，不入版本库。）

### 验证
- py_compile 通过；self_test --module 406/406 全绿

## v6.8.36 - 2026-08-13 历史优化报告清洗 + 测试锁隔离（补 v6.8.35 两个后续项）

### 任务1：历史脏 optimization-report 清洗
- v6.8.35 的 P3 让新生成报告「总分与四维同源」，但已生成的 10 份历史报告仍是旧脏逻辑产物
  （总分取 last_score、四维取另一条记录，如 moire r8 总分 0.81 vs 四维 0.30/0.25/0.50/0.20 错位）。
- 新增 `scripts/regenerate_optimization_reports.py`（带 `--dry-run` + rename 备份恢复 + `--self-check`）：
  rename 旧报告→.bak → 用当前逻辑重生成 → 成功删 .bak / 失败恢复，零数据丢失。
- 执行：10 份全部重生成，score_history 覆盖率 100%。moire r8 新报告总分 0.79 + 四维
  0.82/0.78/0.75/0.80 同源自一条记录（加权≈0.79），自洽。同步 KB：latest_round 与评分表同源（8）。

### 任务2：测试锁隔离缺陷修复
- 根因：`common.file_lock` 锁文件固定在 `/tmp/linsai-copilot-{name}.lock`，测试 `file_lock("proposal-lifecycle")`
  与真实 lc-micro-scheduler cron 争用同一锁文件，工作时段导致 test_round_complete_break 等挂起。
- 修复：`file_lock` 支持 `LINSAI_LOCK_DIR` 环境变量（生产不设则行为不变）；`create_isolated_env`
  设置该变量指向隔离 tmp/locks。测试锁自动隔离。
- 验证：人为持有 /tmp 锁时 test_round_complete_break 仍 30s 内通过；全量 self_test --module 406/406 全绿。

### 验证
- `py_compile` 通过；regenerate 脚本 --self-check 通过；self_test --module 406/406 全绿
- 10 份历史 report 总分四维自洽；KB reports latest_round 与评分表同源

## v6.8.35 - 2026-08-13 知识库课题同步治理与治本（事件驱动同步+反向清理+测试隔离）

### 问题
知识库课题镜像（NSFC/proposals|versions|reports）与权威源 `research_proposals/` 同步不到位：
生命周期状态变更（轮次完成/晋级/归档）这个最该同步的时刻反而不同步；归档不清理镜像产生孤儿；
report 评分表总分与四维数据源不一致；测试写穿真实 knowledge/ 产生 general-test-* 孤儿。

### 修复（P0-P4）
- **P1 堵测试源头**：`save_proposal_sync` 经 `knowledge_base/kb_wiki/kb_graph` 的模块级绝对路径常量
  此前未被测试 patch，导致写穿真实 knowledge/。修复：test_proposal_kb_sync 补 patch 整条写入链；
  4 个 micro_scheduler 测试经新增的 `patch_kb_sync_noop` 拦截 `_sync_proposal_to_kb`（测调度逻辑不测
  KB 同步）。验证：跑后真实 proposals/ mtime 不变、无 test 孤儿。
- **P2 事件驱动同步 + 反向清理**：在 4 个生命周期事件点接入 KB 同步——`optimize_cycle` 轮次完成、
  `micro_scheduler` 轮次已完成分支（补 GAP）、`transition` 流转（archived→清理 / 其他→同步）。新增
  `cleanup_kb_mirror`（归档清理 proposals/versions/reports）；`_get_all_proposals` 过滤 archived 防止
  已归档课题被 reorg 重新生成。保留周末 sync_all 作定时兜底。
- **P3 修 report 评分 bug**：① 源生成器 `_generate_round_report` 总分行改为与本轮四维同源（取自同一
  条 score_history 记录），上一轮改为按列表顺序的前一条（避免跨 epoch round 号误配）；② 显示层
  `_create_report_page` 的 latest_round 改为与评分表同源（optimization-report 最大轮次）。
- **P4 cron 持久防重复**：`_check_cron_status` 增加重复检测（每个必需前缀 >1 份→cron_duplicate 告警），
  `run_monitor` 对 cron_duplicate 自动调 `cleanup_cron_duplicates` 去重。配套：P0 阶段已把各框架 5×
  副本收敛到 1 份。
- **P0 治理**：清理 knowledge/ 里 general-test-* 孤儿（v6.8.33 已并发处理）；cron 去重各框架→1 份。

### 验证
- `py_compile` 全通过；import 链无循环
- self_test --module：P2/P3 阶段 406/406 全绿；关键测试类单独通过
  （注：最终全量 self_test 因真实 lc-micro-scheduler cron 持有 proposal-lifecycle 锁竞争未能跑完，
  系已存在的测试隔离缺陷——测试用全局锁名，非本次回归）
- 跑后真实 knowledge/ 无 test 孤儿、mtime 不变；_check_cron_status 各框架 1 份时返回 None

## v6.8.34 - 2026-08-13 修复监控 cron 陈旧检测键名不匹配（全量误报）

### 问题
- `lifecycle_monitor._check_cron_status` 读取 cron 的 `last_run_at` 键，但 `hermes_bridge.cron_list_profile` 实际返回 `last_run` 键，导致 `last_run` 恒为空 → 所有关键 cron 被误判"从未执行"，每小时产生 1 条 cron_stale 假告警（误导健康监控与飞书通知）。
- 固定 2h 陈旧阈值对每日(24h)/每6h 调度的 cron 恒误报（lc-daily-orchestrate 每日 08:55、lc-repair 每 6h，正常间隔即超 2h）。

### 修复
- `scripts/lifecycle_monitor.py`：`last_run = c.get("last_run") or c.get("last_run_at", "")` 兼容两键。
- 新增 `_estimate_cron_interval()` 按调度间隔估算陈旧阈值（`max(2h, 2*interval)`），消除对每日/6h cron 的误报。
- 新增 `scripts/tests/test_monitor_cron_stale.py`（7 断言）并纳入 `self_test --module` 回归。

### 验证
- 修复后 `lifecycle_monitor --dry-run` 异常数从 1（cron_stale 假告警）降为 0。
- `test_monitor_cron_stale` 7/7 通过；`self_test --module` 393/395（优于基线 392/395，唯一失败为既有偶发的 test_round_complete_break，单独运行通过）。

## v6.8.33 - 2026-08-13 优化完善 5 个课题的研究设想（申请书核心）

- **莫尔超晶格**（`optimizing/general-moire-strong-field-probe`）：剥离文件顶部 r19/r10/r18 轮次优化日志，保留纯科学内容
- **瞬态量子相**（`optimizing/key-transient-quantum-phase-optical`）：补全"来源与可靠性"小节——从仅 1 篇论文扩充为 39 篇文献六条论证链 + 检索范围声明 + DOI 核实状态如实标注
- **BSV-HHG**（`pending_review/general-bsv-driven-hhg-quantum`）：清理第 22/21/19 轮记录与第 15/16/20 轮进展、模块完整性表格等内部轮次日志，保留纯内容
- **量子几何反演 / altermagnet 序参量**：校验确认已达 NSFC 严谨性标准，无需改动
- 验证：3 个文件清理后无内部注释残留，判据数值与各课题 04_proposal 保持一致

## v6.8.32 - 2026-08-13 修复 test_literature_service 测试隔离失效（污染真实 knowledge 数据域）

### 问题
- `scripts/tests/test_literature_service.py` 的 `_test_lit_read_wiki_persistence` / `_test_link_to_proposal_after_read` 两个用例调用 `LiteratureService.read()`，发起**真实 arxiv 网络请求**并直接写入**真实 `knowledge/wiki/papers/`**：
  - 根因：`literature_service.py` 的 `WIKI_PAPERS_DIR` / `RAW_PAPERS_DIR` 是模块级常量，import 时即绑定真实 `knowledge/` 绝对路径，`patch_module_root()` 无法覆盖已绑定常量 → 隔离失效。
  - 后果：① 违背文件头「不调网络/LLM」与 AGENTS.md「测试零污染」「knowledge 为共享只读域」铁律；② 每次跑测试销毁性覆盖既有深度阅读笔记（`2502.09427.md` / `2606.22714.md` 的 hermes 产出被替换为简略网络内容）；③ 3 个测试长期不稳定（依赖网络，耗时 301s）。

### 修复
- **测试改造**：移除上述两个网络/真实 IO 用例，保留 12 个纯解析/逻辑单元测试（解析器、build_frontmatter、_ingest_new_papers 计数），文件头补充隔离原则说明与移除原因。如需回归 read()/link_to_proposal() 端到端链路，应改用注入假 fetcher + monkeypatch 路径常量方式。
- **数据恢复**：`git checkout HEAD` 逐文件还原被覆盖的 `knowledge/wiki/papers/2502.09427.md`、`2606.22714.md` 深度阅读笔记。
- **清理 `_lifecycle.json`**：移除顶层多余的 `key-transient-quantum-phase-optical-20260726` 污染键（与 `proposals` 内同名键重复，无代码读取，安全）。
- **文档/注释对齐**：AGENTS.md 的 `lifecycle_monitor.py --check` → `--dry-run`（与实际 CLI 一致）；`hermes_bridge.py` cron_list_profile 处注释 `v6.8.30` → `v6.8.31`（该 created_at 修复属 v6.8.31）。

### 验证
- `py_compile scripts/*.py scripts/tests/*.py` 通过
- `self_test.py --module`：**🟢 388/388 全量通过，4.75s**（修复前 392/395 含 3 失败、417s）
- LiteratureService 解析器测试：30/30 通过，0.048s（修复前 34/37、301s）
- 还原后的 wiki 文件 mtime 不再被后续测试触碰（隔离生效）

## v6.8.31 - 2026-08-13 修复 cron_list_profile 未暴露 created_at 导致去重排序失效

- 修复 `scripts/hermes_bridge.py`：`cron_list_profile` 返回值新增 `created_at` 字段（与 `cron_list` 保持一致）
  - 根因：v6.8.30 只给 `cron_list` 补了 `created_at`，但 `cleanup_cron_duplicates` 实际调用的是 `cron_list_profile`，导致去重排序键仍为空、无法区分"最新"副本
  - 影响：5 类框架 cron（lc-daily-orchestrate/lc-repair/lc-prompt-optimize/lc-retrospective/lc-hourly-monitor）修复后再次执行 `--setup-cron-v2` 时能正确保留最新副本
- 新增回归测试 `scripts/tests/test_cron_setup_idempotent.py::_test_cron_list_profile_exposes_created_at`，验证 cron_list_profile 透传 created_at 并可按其区分最新副本（14/14 通过）
- 验证：`py_compile` 通过

### 背景

项目经长期迭代（v1→v6.8.28），积累了大量历史备份、重复 HTML 分享产物、散落临时文件和编译缓存，总冗余约 943MB。本次按"备份迁移→验证→提交"策略，全部移入 `_cleanup_backup/` 待确认后清理。

### 整理内容

| 阶段 | 操作 | 文件数 | 体积 |
|------|------|--------|------|
| A-1 | `backups/` 旧 zip 备份（保留最近 2 个） | 7 zip + 5 lifecycle snapshot + 4 migration dir | ~920MB |
| A-2 | 5 个 HTML 分享目录 + `.trae-html-share-packages/` | 6 目录（含重复字体/JS） | ~20MB |
| A-3 | `scripts/__pycache__/`（全目录 8 个子目录） | 145 个 .pyc | ~2.8MB |
| B-1 | `healthcheck-*` 文件归入 `logs/healthchecks/` | 9 文件 | ~72KB |
| B-2 | `.DS_Store` 清理 | 5 文件 | ~50KB |
| B-3 | 废弃空目录删除（`proposals/`、`.uploads/`、`.zcode/`） | 3 目录 | ~8KB |
| B-4 | `.gitignore` 补充 healthcheck / HTML 目录 / `_cleanup_backup/` 规则 | 规则更新 | — |
| C-1 | 一次性迁移/修复脚本归入 `scripts/archive/` | 4 文件 | — |
| C-2 | `scripts/README.md` 文件统计更新（49→114 根目录 .py） | 文档更新 | — |

### 安全措施

- 所有文件**移动**到 `_cleanup_backup/`（非删除），按阶段分子目录
- `_cleanup_backup/` 已加入 `.gitignore`，不影响版本库
- 每阶段后 `py_compile` + `self_test`（375/378 同基线，无回归）
- 确认运转正常后可手动清空 `_cleanup_backup/`

### 整理前后对比

| 指标 | 整理前 | 整理后 |
|------|--------|--------|
| 根目录文件/文件夹数 | 27 文件夹 + 16 文件 | 17 文件夹 + 4 文件（.md/.gitignore/VERSION/.env） |
| backups/ 大小 | 925MB（8 zip + migration dirs） | ~820MB（仅保留最近 2 zip） |
| scripts/ __pycache__ | 2.8MB（145 .pyc） | 0（运行时自动重建） |
| .gitignore 覆盖 | 遗漏 healthcheck/HTML 目录 | 完整覆盖 |

### 修改文件

| 文件 | 改动 |
|------|------|
| `.gitignore` | 新增 healthcheck/HTML分享目录/_cleanup_backup/.uploads 规则 |
| `VERSION` | 6.8.28 → 6.8.29 |
| `scripts/README.md` | 文件数统计更新 |
| `scripts/archive/README.md` | 新建归档说明 |
| `logs/healthchecks/` | 新目录，归入 9 个 healthcheck 文件 |

## v6.8.28 - 2026-08-12 范本锚点路径修复 + stale job 清理

### 背景

v6.8.27 退回 2 个 pending_review 课题后，发现范本锚点（benchmark_anchors）存在关键路径不匹配：critic/writer prompt 引用 `reference_materials.benchmark_anchors`，但实际数据仅在 `general_principles.benchmark_anchors`，导致 agent 永远读不到实际范本内容。同时发现 order-parameter 积累了 58 个 stale jobs（rounds 7-8），需要清理。

### 修复内容

| # | 级别 | 问题 | 修复方式 |
|---|------|------|---------|
| P0 | P0 | benchmark_anchors 路径不匹配（agent 读不到范本） | 在 `reference_materials.benchmark_anchors` 下镜像数据，与 `general_principles.benchmark_anchors` 同步 |
| P1 | P1 | order-parameter 84 个 jobs 混合 rounds 1/7/8 | 清理 58 个 stale jobs（rounds 7-8），保留 round 1 的 26 个 pending jobs |

### 验证

- `reference_materials.benchmark_anchors` 4 个 example 字段均可达（rationale/content/scheme/innovation）
- 5 个 optimizing 课题状态：
  - bsv-driven-hhg: round 8 进行中（8 pending writer）
  - moire-strong-field: round 7 刚启动（27 pending）
  - order-parameter: round 1 全新链（26 pending, first=idea_review）
  - quantum-geometry: round 1 全新链（26 pending, first=idea_review）
  - key-transient: round 1 全新链（26 pending, first=idea_review）
- 模块测试 375/378 通过（同基线）
- 微调度器手动触发验证：moire-strong-field monitor job 成功执行

### 修改文件

| 文件 | 改动 |
|------|------|
| `memory/nsfc-standards.json` | `reference_materials` 下新增 `benchmark_anchors` 镜像数据 |
| `research_proposals/_lifecycle.json` | 清理 order-parameter 的 58 个 stale jobs |

## v6.8.27 - 2026-08-12 全链路审计修复：9 项问题

### 背景

v6.8.26 发布后对全系统做了三轨并行审计（执行链路 / 自检测机制 / 运行时状态），发现 10 个问题（3 个 P0 + 5 个 P1 + 2 个 P2），外加设计清查发现 1 个设计-实现偏差。本次全部修复。

### 修复列表

| # | 级别 | 问题 | 修复方式 |
|---|------|------|---------|
| P0-1 | P0 | debug-journal.json 膨胀 11.4MB（54,798 条 prompt_tuning） | 新增 `compact_journal()` 函数，重置 stats 为真实统计；已执行清理：11.42MB→9.88KB |
| P0-2 | P0 | 停滞课题检测 `done==0` 条件过严（大多数停滞课题已有部分 done） | 改为 `pending_count > 0`，检测"有 pending 但 48h 未推进"的课题 |
| P0-3 | P0 | 退回后 idea_review 无条件重触发（浪费 LLM 调用） | `need_idea_review` 增加 `not idea_review_passed` 条件 |
| P1-1 | P1 | monitor 降级路径 `round_num` 未定义（休眠 Bug） | 从 `job.get("round", 0)` 直接提取 |
| P1-2 | P1 | Writer 侧未注入人工审核反馈 | `_run_writer_optimize` 末尾增加 `_load_human_feedback_block` 注入 |
| P1-3 | P1 | `_sync_derivative_artifacts` 缺少"同步优化限制"约束 | prompt 增加"不允许新增科学目标或改变研究方向" |
| P1-4 | P1 | KB 覆盖率/趋势雷达仅 stdout 输出 | 持久化到 `system-kanban.json` 的 `kb_metrics` 字段 |
| P1-5 | P1 | 输入端熔断仅周末检测 | 在 `lifecycle_monitor.py` 每小时检查中增加 weekend input 状态检测 |
| P2-1 | P2 | optimize.py L121-124 死代码（加载但从未使用） | 已删除 |

### 修改文件

| 文件 | 改动 |
|------|------|
| `scripts/debug_journal.py` | 新增 `compact_journal()` 函数 |
| `scripts/lifecycle_monitor.py` | 停滞检测条件修复 + 输入端熔断每小时检测 |
| `scripts/lifecycle/controller.py` | idea_review 退回重触发修复 |
| `scripts/lifecycle/executor.py` | monitor 降级路径 round_num 修复 |
| `scripts/proposal_lifecycle/optimize.py` | Writer 审核反馈注入 + 同步优化限制 + 死代码清理 |
| `scripts/sync_engine.py` | KB 覆盖率/趋势雷达持久化到看板 |
| `memory/debug-journal.json` | 已执行清理（11.42MB→9.88KB） |

### 验证

- `--module`：375/378 通过（3 个失败为沙箱限制）
- debug journal 文件大小从 11.42MB 降至 9.88KB

## v6.8.26 - 2026-08-12 研究设想质量门槛（idea_review）

### 背景

当前链路中，研究设想（`00_research_idea.md`）在进入 optimizing 之前只有一次性初始化生成，之后 writer 虽然在每轮结束时"同步更新"研究设想，但这个更新是被动的、片段式的。没有独立的、前置的"研究设想质量审核"环节。key-transient 课题 8 轮优化无收敛的根因就是研究设想阶段对"研究内容 vs 研究方案"的逻辑切分未想清楚，后续优化无法弥补结构性缺陷。

### 新增功能

- **研究设想独立评审步骤**（`idea_review`）：在 round 1 的 job 链最前端，作为所有 critic 的前置依赖。使用 researcher profile 对 `00_research_idea.md` 做独立评审，聚焦科学问题清晰度、创新点可检验性、内容-方案逻辑切分、方向一致性。
- **质量门槛**：评审分数 ≥ 0.70 才允许进入优化（`IDEA_REVIEW_THRESHOLD`），与申请书的达标阈值解耦。
- **迭代修复**：未达标时 writer 根据评审意见修改研究设想，重新评审，最多 3 轮（`MAX_IDEA_REVIEW_ATTEMPTS`）。仍不达标则暂停优化，等待人工介入。
- **结构性缺陷退回机制**：monitor 步骤新增 `_detect_structural_defect` 检测 content/scheme 文件级重复或模块空置。检测到时设置 `idea_review_required` 标志，下一轮自动重新插入 `idea_review` job，形成退回闭环。
- **同步优化限制**：optimizing 阶段 writer 对 `00_research_idea.md` 的修改仅限于"同步已有内容"，不允许新增科学目标或改变研究方向——方向性变更须退回研究设想阶段。

### 修改文件

| 文件 | 改动 |
|------|------|
| `scripts/lifecycle/constants.py` | 新增 `STEP_IDEA_REVIEW`、`IDEA_REVIEW_THRESHOLD`、`MAX_IDEA_REVIEW_ATTEMPTS` 常量 |
| `scripts/lifecycle/executor.py` | 新增 `_run_idea_review_step`（评审-修复循环）、`_parse_idea_review_score`（评分解析）、`_detect_structural_defect`（缺陷检测）；`execute_job` 添加分发分支；`_run_monitor_step` 添加结构性缺陷检测和退回标志 |
| `scripts/lifecycle/controller.py` | `_build_full_round_jobs` 在 round 1 或 `idea_review_required` 时前置 idea_review job；方法绑定区添加 `_run_idea_review_step` |
| `scripts/lifecycle/micro_scheduler.py` | `_CHAIN_ORDER` 添加 `STEP_IDEA_REVIEW: -1`（最高优先级） |
| `scripts/tests/test_idea_review.py` | 新增 11 个测试用例覆盖全部功能 |
| `scripts/tests/test_lifecycle_cron.py` | 更新现有测试适配 26-job 结构 |

### 验证

- idea_review 专项测试：11/11 通过
- `--module`：375/378 通过（3 个失败为沙箱限制，与本次改动无关）

## v6.8.25 - 2026-08-12 cross-proposal 范例注入数据源修复

### 背景

v6.8.24 修复了 cross-proposal 范例注入的阈值和扫描范围，但深度审计发现函数仍完全失效：它扫描各课题目录下的独立 `_lifecycle.json` 文件，但实际所有课题状态存储在全局 `research_proposals/_lifecycle.json` 中，各课题目录无此文件。函数在 `if not lc_file.exists(): continue` 跳过所有课题，永远返回空字符串。

### 修复

- **cross-proposal 范例注入数据源（P0 死代码）**：`_load_cross_proposal_exemplar` 从扫描各课题目录下的独立 `_lifecycle.json` 改为从全局 `_lifecycle.json` 读取所有课题状态。通过 `lifecycle_obj._load_state()` 获取全局状态，遍历 `proposals` 字典筛选 optimizing/pending_review 状态的课题，用历史峰值分数选出最佳范例。

### 验证

- `--module`：373/376 通过（3 个失败均为沙箱限制，与本次改动无关）
- 修复后，`order-parameter-ultrafast-readout`（last_score=0.55 < 0.75）将从 `bsv-driven-hhg-quantum`（峰值 0.85 > 0.70）获取范例段落注入 writer prompt

## v6.8.24 - 2026-08-12 机制层审计修复：8 项失效/死代码修复

### 背景

对 writer/critic/monitor 的 prompt 反馈优化机制做深度审计，发现 4 个 P0 级系统失效和 4 个 P1 级死代码/设计缺陷。核心问题是"优化迭代提高申请书质量的关键操作"大多未按设计生效。

### P0 修复

1. **prompt 优化器正反馈循环（灾难性）**：`_log_auto_applied` 写入 `category=prompt_tuning` → 下次 auto 运行又读回来 → 生成新 suggestion → 再次写入 → 指数膨胀。54K 条建议全是"自动修改 hermes prompt 文件，操作：append"的垃圾。**修复**：category 改为 `prompt_applied_audit`，采集时排除 `auto_applied` 标签的条目。
2. **critic/SOUL.md 严重污染（灾难性）**：原始 2.3KB → 5MB（48,094 个垃圾段落），每次 agent loop 读入 5MB 垃圾。**修复**：从原始备份恢复；清理 prompt-suggestions.json（54K→1）、debug-journal.json（55K→4）、prompt-backups/（482→2）。
3. **agent 分数奖惩 JSON 路径 bug（完全失效）**：`_load_agent_score_feedback` 读 `scores["agents"][role]` 但实际结构是 `scores[role]`，静默返回空，奖惩闭环断裂。**修复**：改为 `scores.get(role, {})`。
4. **nsfc-standards.json 幽灵引用（核心缺陷）**：`scoring_rubric`/`benchmark_anchors`/`section_standards` 被 critic/writer prompt 反复引用但**不存在**，critic 被迫虚构 rubric 档位（已实证）。**修复**：补全三个字段的完整内容。

### P1 修复

5. **cross-proposal 范例注入（从未触发）**：阈值 0.80 无课题可达 + 用 `last_score` 而非历史峰值 + 仅扫描 optimizing/。**修复**：阈值降至 0.70，用 `score_history` 峰值分数，扫描 optimizing/ + pending_review/。
6. **维度轮换（数学不可达）**：5-section 轮转 + `[-6:]` 窗口 = 同 section 最多出现 2 次 < 阈值 3。**修复**：窗口扩大到 `[-12:]`，最低 history 要求从 3 改为 6。
7. **prompt 优化器只覆盖 critic（结构性偏差）**：3 个数据源的 target profile 并集 = {writer, critic}。**修复**：`_collect_agent_score_reasons` 遍历全部 7 个 profile；`_analyze_reasons_for_prompt_hints` 新增 researcher/analyst/reviewer 模式。
8. **prompt-suggestions.json 无清理机制（无限膨胀）**：applied/failed 建议永久驻留。**修复**：新增 `_cleanup_old_suggestions()`，每次 `cmd_auto` 开头清理超过 7 天的非 pending 建议。

### 验证

- `--module`：372/376 通过（4 个失败均为沙箱限制：3 个 hermes profile 目录访问 + 1 个 wiki 页面缺失，与本次改动无关）。
- 数据清理效果：prompt-suggestions.json 54,609→1、debug-journal.json 54,802→4、prompt-backups/ 482→2、critic/SOUL.md 5MB→2.3KB。

## v6.8.23 - 2026-08-12 P0 跨轮持久化（对抗评审置换修复 5 断裂点）

### 背景

P0（critical）级问题此前**没有跨轮记忆**：critic 每轮只基于当前申请书文本评审，
历史轮次指出的"指标口径不一致""首次无文献支撑"等致命问题，若本轮聚焦章节不同，
writer 不会看到、也就不会修复，导致问题在多轮间反复出现、评分停滞。

### 修复（5 个断裂点）

1. **断裂点3（数据层）**：`_lifecycle.json` 新增 `open_critical_issues` 数组
   （registration 初始化），`optimize.py` 新增 `_update_open_critical_issues` /
   `_issue_similarity_key` / `_load_open_critical_issues` / `_build_p0_memory_text`。
   仅收录 critical/high，按（章节+严重度+相似键）跨轮去重，未复现自动标记已解决，
   超 10 轮未复现降级 stale，列表上限 40 条。执行器 `_run_writer_step` 每轮触发更新。
2. **断裂点1（critic 记忆注入）**：`_run_critic` prompt 注入历史未解决 P0，
   要求逐条核实"仍存在则再次标记 / 已解决则明确说明"，避免机械重复扣分。
3. **断裂点2（writer 修复注入）**：`_run_writer_optimize` prompt 注入
   未解决 P0 + 最近 3 条已解决（防横跳），要求列为最高优先级处理并说明结果。
4. **断裂点4（章节放宽）**：存在未解决 P0 时，writer 的聚焦章节限制放宽，
   允许一并修改 P0 涉及章节，但限定与聚焦问题直接相关，避免无关大改。
5. **断裂点5（达标把关）**：`completion._check_done` 在 5 模块全胜且 monitor 达标后，
   若仍存在未解决 critical P0，判定不予流转、继续优化，防止"带病出厂"。

### 验证

- 新增 `scripts/tests/test_cross_round_p0_memory.py`：18/18 通过（收录/去重/标记解决/
  相似键/critic 注入/writer 注入/P0 清零达标判定）。
- `python3 scripts/self_test.py --module`：373/376 通过，3 个失败均为沙箱无法访问
  `~/.hermes` profile 目录所致，与本次改动无关。

## v6.8.22 - 2026-08-11 prompt 优化器指数级膨胀修复（健康检查 4h 发现）

### Bug

`scripts/prompt_optimizer.py` 在 `auto` 模式下与 `memory/debug-journal.json`
形成**指数级增长循环**：

1. `cmd_auto` 调用 `_collect_debug_journal_entries()`，采集 journal 中**所有**
   `category=prompt_tuning` 条目作为建议输入源
2. 对每条 entry 生成一条新 suggestion（fingerprint = `md5("debug_journal:{entry_id}")`）
3. entry_id 格式 `dj-YYYYMMDD-NNN`（debug_journal.py:124-132），**每天从 001
   递增**，每次运行都生成全新 fingerprint → `existing_ids` 去重全部通过
4. `_apply_suggestion` 检查 `content_to_add in current_content` 命中后
   return True，**但仍在第 514-528 行无条件 `shutil.copy2` 创建 backup**
5. `_log_auto_applied` 把每条成功应用写入一条新 prompt_tuning journal 条目
6. 下次 run 的输入基数更大 → 再次膨胀

### 实证（2026-08-11 08:00 过去 4h 窗口）

| 文件 | 4h 增长 | 当前大小 |
|------|---------|----------|
| `memory/debug-journal.json` | +1.7 万条 prompt_tuning | 46 MB / 44,312 条 |
| `memory/prompt-suggestions.json` | +5,385 条新 applied | 34 MB / 44,185 条 |
| `memory/prompt-backups/` | +58 个新备份 | ~600 个 × 4.6 MB ≈ 2.8 GB |
| `~/.hermes/profiles/critic/SOUL.md` | 稳定在 4.6 MB（v6.8.22 修复点：内容已存在则跳过 backup） | — |

时间分布（按小时统计创建时间）：

- 2026-08-09 06:00: 3,968 条
- 2026-08-10 06:00: 12,288 条
- 2026-08-10 07:00: 7,317 条
- 2026-08-11 06:00: 7,496 条
- 2026-08-11 07:00: 3,014 条
- 2026-08-11 08:00: 2,371 条（含 58 个 prompt 备份，间隔 1 秒）

### 影响

- **磁盘占用**：prompt-backups 累积 ~2.8 GB，每天增加 ~250 MB（按 58 个 × 4.6 MB 推算）
- **链路风险**：
  - `prompt_optimizer.py` 启动需要序列化/反序列化 34 MB JSON，秒级延迟
  - 任何读 debug-journal 的脚本（`failure_analyzer`、`retrospective`、
    `debug_journal_report`）变慢
  - `retrospective.py` 每周一 15:00 触发，扫描整个 journal；
    若达到 100 MB+ 级别，`json.loads` 会触发内存峰值
  - 最坏情况：weekly `lc-retrospective` cron 持续超时失败

### 修复（最小化、定向、高置信度）

1. **`scripts/prompt_optimizer.py:127-138` — 限制采集窗口**
   - 新增常量 `DEBUG_JOURNAL_WINDOW_DAYS = 7`
   - `_collect_debug_journal_entries()` 增加时间戳过滤：
     只采集最近 7 天的 prompt_tuning 条目
   - 历史累积的 4 万多条过期条目被自动丢弃，循环基数归零
2. **`scripts/prompt_optimizer.py:521-602` — 先读后备份**
   - 调整顺序：先 `read_text` 检查 `content_to_add in current_content`，
     再决定是否备份
   - 内容已存在场景：跳过 backup 直接 return True（不再浪费磁盘）
3. **`scripts/prompt_optimizer.py:531-535` — 单 run 备份上限**
   - 新增常量 `MAX_BACKUPS_PER_FILE_PER_RUN = 1`
   - `_apply_suggestion` 接收 `backup_count_tracker` 参数，同一 run 内
     对同一文件最多备份 1 次（即便内容真的多次变化）
4. **`scripts/prompt_optimizer.py:783-799` — cmd_auto 启用 tracker**
   - `cmd_auto` 创建 `backup_tracker: Dict[str, int] = {}`
   - 传给 `_apply_suggestions` → `_apply_suggestion`
5. **零重构**：不改 fingerprint 生成逻辑（debug_journal + agent_scores
   两路仍然去重），不改 suggest entry 结构，不改应用主路径

### 回归测试（新增 3 项 / 9 断言）

| 测试 | 守护行为 |
|------|----------|
| `_test_collect_debug_journal_filters_by_window` | 窗口外条目被过滤（边界 ±1d） |
| `_test_apply_suggestion_no_backup_when_content_exists` | 内容已存在时不创建 backup |
| `_test_apply_suggestion_backup_count_tracker` | 多次写入时单文件 backup 上限生效，tracker 正确计数 |

### 副作用

- `cmd_auto` 日志格式变为
  `debug journal（prompt_tuning, 最近 7d 窗口）: N 条`，
  运维侧一眼可看出窗口裁剪生效
- 历史累积的 4.4 万条过期建议保留在 `prompt-suggestions.json`
  （已 applied 状态），新 run 不再生成重复条目；用户可手动清理
  `memory/prompt-suggestions.json` 释放 34 MB 磁盘
- 触发源不限：cron / 手动 / 调试脚本调用 `prompt_optimizer.py auto` 都不再膨胀

---

## v6.8.21 - 2026-08-10 知识库入库 unhashable 静默失败修复（健康检查 4h 发现）

### Bug
- `scripts/kb_text.py:99` `build_frontmatter` 对 `list` 元素做去重时无条件调用
  `set.add(v)`。
- 若 list 含不可哈希元素（如 `_ingest_new_papers` 传入的
  `status_history: List[Dict]`），立即抛 `TypeError: unhashable type: 'dict'`。
- `LiteratureService._ingest_new_papers`（literature_service.py:1013）的
  `except Exception` 静默吞掉所有 per-paper 异常；外层 `executor.py:601` 用
  `len(new_papers)` 虚报入库数，导致日志永远显示"新入库 N 篇"而 KB 实际零落盘。
- 实证（`logs/linsai.log` 2026-08-10 18:57:18）：
  - `general-bsv-driven-hhg-quantum-20260726` 第 6 轮 lit_search 检索到 10 篇论文
  - 10 篇论文 `_ingest_new_papers` 全部 `unhashable type: 'dict'`
  - 同时日志错误地报 `lit_search 新入库 10 篇论文到知识库`
  - 10 个 arxiv_id（2311.11257、2305.16831、2406.10443、2409.13614、
    2311.10390、2505.22536、2407.04755、2206.01042、2003.00277、2106.00372）
    全部未进入 KB。
- 影响：知识出口被静默阻塞。`knowledge_output.process_daily_sources` 依赖
  `lit-gap-*.md` 报告去萃取可靠知识，所有依赖这些论文的 KB 笔记（人物/方法/概念）
  将持续缺失关键引用；同时 `lit_read` 因无 arxiv_id 可读而整体跳过，
  申请书引文校验阶段无法补全。这是 v6.8.3 在 `_ingest_new_papers` 加入
  `status_history` 字段后埋下的回归。

### 修复
- `scripts/kb_text.py:99` — `build_frontmatter` 在列表非空时，先尝试原去重路径，
  异常时（仅 `TypeError`，含 `unhashable type`）回退为 `json.dumps` 序列化。
  字符串列表保持原 `["a","b","c"]` 输出形式，向后兼容。
- `scripts/literature_service.py:997` — `_ingest_new_papers` 返回
  `{"ingested": int, "failed": int, "skipped": int}`，让外层能看到真实入库结果。
- `scripts/lifecycle/executor.py:601` — 用真实计数 `ingested/len(new_papers)`
  替换虚报的 `len(new_papers)`，附加 `failed` / `skipped` 计数。
- **最小化、定向**：3 个文件，~30 行新增/替换，不重构 dedup 逻辑，不改其他路径。

### 回归测试
- `scripts/tests/test_literature_service.py` 新增 5 项（覆盖 15 项断言）：
  - `_test_build_frontmatter_string_list_preserves_old_behavior` — 字符串列表
    仍输出 `tags: ["a", "b", "c"]`（向后兼容）
  - `_test_build_frontmatter_dict_list_no_unhashable` — `status_history` 列表
    不抛 `TypeError`，输出合法 JSON 数组且保序
  - `_test_build_frontmatter_mixed_list_falls_back_to_json` — 混合列表保守
    走 JSON 路径（dict 元素被保留）
  - `_test_ingest_new_papers_returns_counts` — 返回 `dict` 含 `ingested/failed/skipped`
    三个计数（替换之前的 None 返回）
  - `_test_ingest_new_papers_handles_unhashable_dict_list` — 端到端验证：
    含 `status_history` 的论文能成功落盘到 `RAW_DIR/papers/`，且文件 frontmatter
    包含完整的 `"status": "pool"` 字段
- 全量基线：
  - `--module` **335/335 通过**（基线 320 → 加 15 项守护）
  - `--scenario` 16/16 通过
  - `--persona` 38/38 通过
  - `--web-ci` **403/403 通过**（基线 388 → +15 项）
  - `py_compile scripts/*.py` 全部通过

### 副作用
- 修复后 `executor.py:601` 日志格式变为 `新入库 X/N 篇论文到知识库
  （failed=Y, skipped=Z）`，运维侧一眼可分辨真实入库/失败/跳过。

---

## v6.8.20 - 2026-08-10 微调度器时段内轮转修复 + 回归测试补齐（健康检查 4h 发现）

> v6.8.19 已修复的 prompt 变量作用域问题与本次微调度器轮转修复在 git 历史中
> 都标注为 v6.8.19（修复提交时间紧邻且都用同一周期号），本次 CHANGELOG 补记
> 微调度器修复并将其登记到 v6.8.20，避免版本号复用。

### Bug
- `scripts/lifecycle/micro_scheduler.py:1070` `_focus_proposal_for_slot` 的 else
  分支（同一时段内保持当前聚焦）**不更新** `state["last_proposal_id"]` 和
  `state["last_slot_index"]`。
- 后果：下次调用进入函数顶部 `_rebalance_index` 时（908-939），用陈旧的
  `last_proposal_id` 校准 `last_proposal_index`，队列重排时指向错误课题，
  表现为**同一时段内每 5 分钟轮换一个 proposal**，永远跑不完一轮优化。
- 实证（看板 memory/lifecycle-focus.json::focus_history）：
  - `2026-08-09 23:05Z ~ 2026-08-10 00:00Z`（slot=08:30-12:30）连续 ~60 条
    5min 轮换记录，5 个 optimizing 课题反复循环，无一完成本轮。
  - 04:00Z 后焦点稳定锁定 `general-bsv-driven-hhg-quantum-20260726`，与
    修复后逻辑一致。
- 影响：5 个 optimizing 课题（其中 general-quantum-geometry 已 score=0.81 接近
  晋级，其余 0.71-0.77）的轮次优化进度被卡住，直接威胁申请书高质量产出。

### 修复
- `scripts/lifecycle/micro_scheduler.py:1073-1077` — else 分支同步写回
  `state["last_proposal_id"] = pid` 与 `state["last_slot_index"] = slot_index`。
  函数尾部 `_save_focus_state(state)`（line 1107）会统一落盘。
- **最小化、定向**：仅 2 行新增，不改其他分支逻辑。

### 回归测试
- `scripts/tests/test_micro_scheduler_rotation.py` 新增"测试 7（v6.8.19 修复守护）"：
  - 模拟 `state.last_proposal_id=""` 漂移，slot_index 不变 → 走 else 分支
  - 断言函数返回 pid_a（按 queue 选择正确）
  - 断言持久化的 `state.last_proposal_id == pid_a` 与
    `state.last_slot_index == 1`，确保下次 `_rebalance_index` 拿到正确锚点
- 全量基线：`--module` **320/320 通过**（基线 317 → 加 3 项守护）
- 单独跑：`test_micro_scheduler_rotation.py` **12/12 通过**

### 副作用
- 修复后 4 小时内 `system-kanban.json` 显示 5 个 optimizing 课题
  `stuck=false`、`failed=0`，恢复正常推进节奏。

---

## v6.8.19 - 2026-08-10 优化循环 prompt 变量作用域修复（健康检查 4h 发现）

### Bug
- `optimize.py:888` `_run_critic` 引用了 `optimize_cycle` 局部变量 `_human_feedback_block`，
  跨方法作用域不可见 → 每次 critic 评审必抛 `name '_human_feedback_block' is not defined`
- `optimize.py:1296` `_run_writer_optimize` 直接引用未定义变量 `section_key` →
  每次 writer 优化必抛 `name 'section_key' is not defined`
- 影响：过去 4h 健康检查看板面板（memory/system-kanban.json）execution_history 显示
  4 个 critic job + 5 个 writer job 全部失败，覆盖 4 个不同 proposal
  （general-bsv / general-order / key-transient / general-quantum）；
  5 个 optimizing 课题全部 stuck，task_progress 卡在 0%~84%；
  这是 v6.8.17 引入反馈闭环与 cross-proposal 范例注入时埋下的回归

### 修复
- `scripts/proposal_lifecycle/optimize.py` — 抽出 `_load_human_feedback_block(proposal_id)`
  私有方法，optimize_cycle 与 _run_critic 各调用一次，内部用 `proposal_id` 查 prop_state，
  消除跨方法依赖
- `scripts/proposal_lifecycle/optimize.py` — `_run_writer_optimize` 在调用
  `_load_cross_proposal_exemplar` 前从 `focus_section` / `is_full_review` 派生 section_key

### 校验结果
- 新测试 `test_optimize_v6817_prompt_vars.py`：8/8 通过（覆盖 critic 与 writer 两条路径）
- `--module`：345/345 通过（基线对齐）
- `--scenario`：16/16 通过
- `--web-ci`：413/413 通过
- `py_compile`：全部通过

---

## v6.8.18 - 2026-08-09 cron 安装幂等性修复（健康检查 4h 发现）

### Bug
- `setup_cron_framework` 和 `setup_monitor` 直接调用 `hb.cron_create_no_agent`，
  **未先清理同名旧实例**，导致每次 `--setup-cron-v2` / `--setup-monitor` 都叠加一个新 cron。
- 过去 4h 健康检查实测：
  - `lc-hourly-monitor` 注册了 2 个（id=5c89cbd77338 + 9d3177df68f0）
  - `lc-daily-orchestrate` / `lc-repair` / `lc-prompt-optimize` / `lc-retrospective`
    各注册了 5 个
  - jobs.json 总 cron 数 = 32（合理约 13）
- 影响：整点同时触发 N 次同一个 monitor，造成 CPU 浪费、看板时间戳抖动；
  同一分钟内 `lc-hourly-monitor` 双触发（16:00:36.611 + 16:00:36.735）。

### 修复
- `scripts/lifecycle/framework.py:54-60` — 清理名单新增
  `lc-daily-orchestrate` / `lc-repair` / `lc-prompt-optimize` / `lc-retrospective`
- `scripts/lifecycle/framework.py:113-128` — prompt-optimize / retrospective 创建前
  单独清理同名旧实例（这些 cron 在函数末尾才创建）
- `scripts/proposal_lifecycle/cli.py:325-330` — setup_monitor 在创建 lc-hourly-monitor
  前先清理同名旧实例，并在输出中报告 `removed_duplicates` 数量
- `scripts/tests/test_cron_setup_idempotent.py` — 新增 8 个回归断言（桩 hermes_bridge，
  不依赖真实 hermes CLI，零成本）

### 校验结果
- 新测试 `test_cron_setup_idempotent.py`：8/8 通过
- `py_compile` 全部通过

### 后续建议（需用户手动执行一次）
- `python3 scripts/proposal_lifecycle.py --setup-cron-v2`
- `python3 scripts/proposal_lifecycle.py --setup-monitor`
- 执行后 `jobs.json` 中同名 cron 应均归 1 个。

## v6.8.17 - 2026-08-09 自检测/自成长深层增强（反馈闭环 + KB健康 + 趋势雷达 + 范例注入）

### 改进1: 人工审核反馈闭环（核心）
- `feedback_archive.py` — `submit_feedback()` 新增 `session_id` 参数，退回时自动提取审核对话中的用户意见摘要写入 `06_feedback/`
- `feedback_archive.py` — 新增 `load_review_feedback_for_optimization()` 加载历史审核反馈
- `optimize.py` — critic prompt 自动注入历史人工审核反馈（"从对话中学习"）
- `web_routes_system.py` — `review-verdict` 和 `review-finalize` 传递 `session_id`
- 效果：人工审核意见不再丢失，后续优化轮次自动回避同类问题

### 改进2: 知识库健康评分
- `reflection_jobs.py` — 每周反思时自动计算 KB 健康度（覆盖率 + 新鲜度 + 连通度）
- 覆盖率 <60% 或孤立节点 >20% 时触发行动建议

### 改进3: 研究趋势雷达
- `sync_engine.py` — `sync_all()` 新增 [3.7/5] 步骤，分析最近 2 周简报的关键词频率趋势
- 领域关键词突增时在日志标记"趋势上升"

### 改进4: Cross-proposal 范例注入
- `optimize.py` — writer prompt 自动注入高分课题（≥0.80）的范例段落
- 触发条件：当前课题分数 <0.75 且存在高分范例

### 校验结果
- `--module`：345/345 通过
- `--scenario`：16/16 通过
- `--web-ci`：399/399 通过

## v6.8.16 - 2026-08-09 全链条自检测/自成长增强（5 项改进）

### 改进1: 质量天花板检测 + 自动晋级/暂停
- `completion.py::_check_done()` 新增收敛检测：连续 3 轮 ≥0.80 且每轮提升 <2% → 自动晋级到 pending_review
- 新增质量下降检测：连续 3 轮分数下降 → 暂停自动优化，附加 quality_warning
- 效果：避免高质量课题在 optimizing 阶段无限空转

### 改进2: 停滞课题自动检测
- `lifecycle_monitor.py::_check_proposals()` 新增 stalled 检测：optimizing 课题 48h 无新 done job → 告警
- 效果：0/25 job 完全停滞的课题不再被忽略

### 改进3: 知识库笔记覆盖率检测
- `sync_engine.py::sync_all()` 新增 [3.6/5] 步骤：扫描 raw/papers 无 wiki 笔记的论文，统计覆盖率
- 效果：214 篇 raw 中 137 篇无笔记的缺口可视化，为周末输出端提供补全目标

### 改进4: 对抗评审维度轮换
- `optimize.py::optimize_cycle()` 新增维度轮换逻辑：连续 3 轮在同一维度原地踏步 → 自动切换到最弱维度
- 效果：避免 critic/writer 在同一维度"鸡蛋里挑骨头"循环

### 改进5: 输入端无新设想熔断
- `reflection_jobs.py::_analyze_collected_state()` 新增 input_pipeline_broken 检测：连续 2 周 ideas=0 → 告警
- 效果：输入端管线断裂不再静默失败

### 校验结果
- `--module`：345/345 通过
- `--scenario`：16/16 通过
- `--persona`：38/38 通过
- `--web-ci`：399/399 通过

## v6.8.15 - 2026-08-08 全面校验 + 缺陷修复 + 路径清理固化

### 缺陷修复
- `kb_proposal_reorg.py` 修复 MOC 去重缺陷：capture 条件从模糊包含改为精确匹配 `## ` 标题行，修复引言行 `聚合课题相关概念` 误触发导致 MOC 内容重复追加（v6.8.5 回归缺陷）
- `kb_proposal_reorg.py` 修复标签提取缺陷：`_extract_label()` 跳过通用标题（课题说明/课题简介/提案说明/无标题），回退到 ID 推断
- `test_scenarios.py` 修复 web-ci 模式下场景测试技能匹配失败：`patch_module_root` 二次 patch（tmp→real）字符串替换失效，改为直接强制设置 `SKILLS_DIR`/`SKILLS_STATE_PATH`

### 路径清理固化
- `paths.py` 移除死路径常量：DOCS_DIR / QA_PAPER_DIR / QA_PROPOSAL_DIR / QA_PROJECT_DIR / BRIEFINGS_DIR
- `paths.py` 修复 HERMES_HOME：从 `~/.kimi` 改为 `~/.hermes`（hermes-agent 更名遗留）
- `briefing_sync.py` 废弃 paper-pool.json 写入：`sync_from_hermes()` 只更新水位标记
- `state_sync.py` 废弃 paper-pool.json 读取：`initialize_from_existing()` 跳过空 paper-pool.json
- `test_core.py` 更新 `_test_sync_from_hermes` 匹配 v6.8.14 行为

### 全面校验结果
- `--module`：340/340 通过（较 v6.8.9 基线 332→340，新增 8 项 + 修复 5 项失败）
- `--scenario`：16/16 通过
- `--persona`：38/38 通过
- `--web-ci`：394/394 通过（较 v6.8.9 基线 252→394，修复场景测试隔离 + 知识库提案整理缺陷）
- 知识库：438 索引文档 / 192 图谱节点 / 235 raw papers / 77 wiki papers / 72 PDF / 219 item-status
- cron：32 个 job 正常 / 17 个 wrapper 脚本全部含 `cd /` 前缀

## v6.8.14 - 2026-08-08 知识库架构重整（数据清理 + PDF整合 + 简报知识化 + 同步常态化 + 知识反哺 + Obsidian优化）

### WP0：数据清理
- 删除 raw/papers 17 个迁移空壳（正文 <1500 字符 + abstract 为空）
- 修复 wiki/papers 9 个双FM破损文件（从 deep_analysis JSON 重建），删除 10 个无源文件
- 回填 19 篇 wiki/papers 元数据（arxiv_id→title/链接/方向）
- 统一 45 篇 frontmatter type 字段（concepts→paper）
- 重建 index.json（438 条，清除 197 条幽灵索引）
- 重建 graph.json（192 节点 205 边）
- 归档 test 课题到 _archive/

### WP1：PDF 资产整合
- `sync_engine.py` 新增 `sync_pdf_library()`：从 hermes 同步 72 个 PDF + extracted txt
- 新建 `knowledge/raw/pdfs/_pdf-library.md` Obsidian 索引页

### WP2：简报知识化
- `kb_importer.py` 新增 `import_deep_analysis_all()`：批量转换 deep_analysis JSON 为 5 维笔记
- `sync_engine.py` 新增 `sync_research_briefings()`：同步每日精选简报到 wiki/reviews/
- 低质 papers/*.md 不再同步到知识库

### WP3：同步常态化
- 新建 `lc-daily-sync` cron job（每天 23:00 执行 `sync_engine.sync_all()`）
- 新增 `lc_daily_sync.sh` wrapper（含 cd / 兼容 v6.8.11）

### WP4：知识反哺（本地优先）
- `literature_service.search()` 加入 KB-first 逻辑：先查本地 raw/papers + wiki/papers，命中 ≥60% 直接返回
- `executor.py::_run_lit_search_step` 注入 `get_context()` 三层预检索作为背景知识

### WP5：Obsidian 体验优化
- 新建 `knowledge/Home.md` 顶层 Dashboard
- Graph 颜色分组：concepts 蓝 / methods 绿 / papers 橙 / reviews 紫 / projects 红
- 新建 `docs/DATA-FLOW-MAP.md` 数据流动路径图谱（7 条核心数据链 + 废弃路径清单）

## v6.8.13 - 2026-08-08 weekend-input 文献来源路径统一

- `weekend_pipeline/sources.py` 三路读取统一（raw/papers + hermes_briefings + reviews）
- `weekend_pipeline/input_jobs.py` 前置调用 `sync_engine.sync_hermes_outputs()`

## v6.8.11 - 2026-08-08 cron wrapper cd / 修复

- 所有 wrapper 脚本添加 `cd /` 前缀，解决 macOS TCC 权限导致的 `getcwd: Operation not permitted`
- `lifecycle/utils.py::_write_wrapper_script` 使用正则检测并强制升级旧 wrapper

## v6.8.10 - 2026-08-07 monitor 评分降级日志 + 聚焦软卡死让出

### monitor 评分降级
- `monitor.py::run_monitor_step`：当 `monitor_independent_score` 在 JSON 解析和文本兜底后仍为 0.0 时，记录 reviewer 原始输出前 500 字符到日志（含 proposal_id/round/section_key），方便定位是 reviewer 输出格式变化还是 LLM 挂掉。新增 `monitor_score_valid` 标记。

### 聚焦软卡死让出
- `constants.py`：新增 `MAX_SOFT_STUCK_SLOTS = 3`（连续聚焦同一 proposal 超过该时段数且轮次无推进时强制让出）。
- `micro_scheduler.py::_focus_proposal_for_slot`：在硬卡死检查（`_is_proposal_stuck`）通过后，新增软卡死检测——`_count_consecutive_slots` 统计连续 N 个时段，若 `optimization_rounds` 未增长则视同"软卡死"强制让出焦点给下一个 proposal。解决 failed job 不阻塞 pending 但又不完成（灰色地带）时永久占用焦点的问题。
- 新增 `_round_when_focused` 状态字典跟踪初始轮次，区分"轮次正常推进"和"真卡死"。

### 验证
- 语法检查通过。
- `self_test.py --module` 342/342 通过。

## v6.8.9 - 2026-08-07 评分标准存档 + 维度提取修复 + 监考者把关 + 对抗防摆烂

### 评分标准存档
- 新增 `docs/SCORING-STANDARDS.md`：完整记录当前有效评分标准（达标阈值 0.90、三类项目维度权重、评分完整性 7 规则、程序化天花板、进入待评审 3 条件、agent 分数机制、禁止清单扣分对照、分数提取方式），标注权威数据源，便于后续查看。

### 维度提取修复
- `optimize.py::_extract_dimension_scores`：修复表格含权重列时误匹配权重的问题。旧正则取行内第一个数字（权重），现改为取表格行内**最后一个**数字作为得分列；非表格回退到行内格式。修正 score_history 维度分错误等于权重的问题。
- 跟进修正（健康检查发现）：取"最后一个数字"会被表格行内档位/主要短板评语中的数字干扰（如 `U/W ~ 0.5`、`已扣 ceiling 0.05`、`17.4%`），导致严谨性误读为 0.10、表达质量误读为 0.05。改为取行内**最后一个独立纯数字单元格**（`0.xx` 独立成格）作为得分列，覆盖 `|维度|得分|`、`|维度|权重|得分|`、`|维度|权重|得分|档位|主要短板|` 各格式。

### 监考者把关
- `completion.py::_check_done`：条件 1（5 模块全胜）新增 monitor 复核——即使对抗全部胜利，若 monitor 独立评分 < 达标线，判定未达标、不予流转、继续优化，防止 writer+critic 串通虚高通过。
- 跟进修正（健康检查发现）：monitor 把关若在"全章节通过但 monitor 评分长期低于达标线"时提前返回 `done=False`，会绕过条件 3（达到最大轮数）逃生阀，导致 proposal 无限卡在 `optimizing`、永不流转到 `pending_review`。修复：仅当未达最大轮数（`rounds < DEFAULT_MAX_ROUNDS`）时才"继续优化"，已达最大轮数由逃生阀收尾流转。新增 `_test_monitor_gate_respects_max_rounds` 回归断言。

### 对抗防摆烂（质量门槛）
- `constants.py`：新增 `WRITER_QUALITY_GATE_*`、`CRITIC_INFLATION_*`、`CRITIC_OVERHARSH_*` 常量。
- `scoring.py`：
  - `compute_rule_deltas` 接入两个质量门槛。
  - 新增 `_writer_quality_gate`：monitor 评分 < 0.50 反扣 5 分、< 0.70 扣 2 分，倒逼 writer 实质提升质量。
  - 新增 `_critic_quality_gate`：monitor < 0.60 但 critic 给分 ≥ 0.75（虚高放水）扣 8 分；monitor ≥ 0.75 但 critic 给分 < 0.55（过度苛刻）扣 4 分，倒逼 critic 严格准确评审。

### 验证
- `self_test.py --module` 340/340 通过（含新增 `test_optimize_dimension_scores` 8 项断言）。
- 临时验证脚本确认：维度提取（权重列/得分列/行内各格式）、writer 质量门槛（过差反扣/欠佳抑制/高正常）、critic 质量门槛（虚高扣/过苛扣/准确不扣）行为正确。

## v6.8.8 - 2026-08-06 评审标准锚点回归 + 执行机制重构

### 问题诊断

用户反馈申请书写作有明显 AI 味、语言不连贯、内容论述不足，但评审仍给出高分。根因分析：
1. prompt 过载导致 LLM 忽略评审标准，凭感觉打分
2. 程序化天花板仅 cap 表达质量维度，综合分不受约束
3. references 评审使用固定占位分（0.85），虚高综合分
4. section checklist 未嵌入 prompt，critic 无从对照
5. 缺少强制锚点对比机制，评审无标杆参照

### 核心修复

- **nsfc-standards.json**：
  - 新增 `scoring_integrity_rules`（7 条规则）：AI 检测天花板→综合分上限联动、references 专项计分、机械评审无效、锚点对比强制、执行清单约束、自引用扣分
  - 新增 `section_standards`（4 个 section）：每个 section 含 `enforcement_checklist`（10 项检查）和 `mandatory_comparison`（锚点对比强制要求）
  - 新增 `scoring_rubric`（6 维度 × 5 档）：每档有明确判定标准，critic 必须逐条引用
  - 强化 `anti_ai_patterns`：添加量化阈值和替换指导
- **optimize.py**：
  - 嵌入 `enforcement_checklist` 到 critic prompt（`_build_enforcement_checklist_text`）
  - 综合分天花板强制 cap：AI 天花板 < 0.7 → 综合分 ≤ 0.75
  - references 评审专用计分：N/A 维度不纳入加权
  - 评审报告完整性验证：缺"锚点对比"或"写作风格评估"→评审无效
  - 自引用检测：超 10 次扣 0.05，超 15 次扣 0.10
- **writer SOUL.md**：
  - 添加 5 组改写示范（死板关联词/模板主语/加粗堆砌/元话语/空洞概括句）
  - 添加去AI味操作指南表（8 种 AI 模式 × 识别特征 × 改写方法 × 示例）
  - 添加范本锚点段落（6 个），写作时逐段对标
- **critic SOUL.md**：
  - 添加评分完整性规则（6 条强制执行）
  - 添加防跑偏规则：3 个必选节（写作风格评估/锚点对比/执行清单对照）缺一不可
  - 添加正确/错误评审示范
  - 添加输出格式模板（含必选节标注）

### 总控层锚点回归

- **lifecycle_monitor.py `_check_standard_alignment()`**：
  - 检查项从 4 项扩展到 6 项
  - 新增：scoring_integrity_rules 存在性、section_standards enforcement_checklist/mandatory_comparison 完整性
  - 新增：optimize.py 综合分天花板逻辑、评审报告完整性验证、锚点对比验证
  - 新增：critic SOUL.md 锚点对比/执行清单/写作风格评估/天花板约束引用
  - 新增：writer SOUL.md benchmark_anchors/改写示范/anti_ai_patterns 引用
- **prompt_optimizer.py `_check_anchor_regression()`**：
  - 新增检查 1b：不得移除执行机制引用（10 项：scoring_integrity_rules/enforcement_checklist/锚点对比/天花板 等）
  - 新增检查 4：不得弱化评分天花板约束
  - 新增检查 5：不得弱化评审报告完整性要求

### 验证结果
- `python3 -m py_compile`：lifecycle_monitor.py / prompt_optimizer.py / optimize.py 全部通过
- `nsfc-standards.json` JSON 格式验证通过
- `lifecycle_monitor.py --self-check`：通过（5 课题 0 异常）
- `prompt_optimizer.py --self-check`：通过（10 个 prompt 文件、2 条建议生成测试）

## v6.8.5 - 2026-08-06 知识库自动同步 + 仪表盘升级 + 微调度器优化

### 知识库自动同步（本轮新增）

- **kb_proposal_reorg.py**：全面重构
  - 动态扫描 `_lifecycle.json` 获取所有 proposal（不再硬编码 5 个 ID）
  - 动态查找 proposal 目录（覆盖 drafts/optimizing/pending_review/archived 全部阶段）
  - reports 页面新增**评分变化趋势表**（从 optimization-report-round-N.md 提取总分/innovation/feasibility/rigor/completeness 及变化量）
  - reports 页面新增**优化报告链接**区
  - 去除硬编码 `PROJECT_ROOT`，改用 `Path(__file__).resolve().parent.parent`
- **proposal_kb_sync.py**：提取函数兼容新版章节结构
  - `_extract_core_questions()`：优先从 `sections/rationale.md` 提取科学问题段落，回退到旧版 `question-framework.md`
  - `_extract_innovations()`：优先从 `sections/scheme.md` 提取创新/特色段落，回退到旧版 `proposal-draft.md`
- **micro_scheduler.py**：新增 `_sync_proposal_to_kb()` 函数
  - 轮次完成后自动调用 `proposal_kb_sync.sync_proposal()` + `kb_proposal_reorg --apply`
  - 同步失败不影响主流程（仅日志告警）
  - 不再依赖周末 output 端才刷新知识库

### 验证结果
- 知识库 proposals/ 页面：核心问题和创新点成功提取（之前显示"待提取"）
- 知识库 reports/ 页面：评分变化表正确显示（总分 0.79→0.79→0.81）

### 缺陷修复
- **kb_proposal_reorg.py `_update_moc`**：修复 MOC.md 无限膨胀缺陷。原保留逻辑按"任意行含关键词"触发捕获，而 MOC 顶部自动生成的引言行含"课题相关概念/相关方法/相关团队"子串，导致每次运行将整段旧 body 重复追加，MOC.md 随运行次数无限增长（实测 5 课题时膨胀至 367 行、引言重复 18 次）。改为仅"章节标题行（`#` 开头）"匹配关键词触发，运行幂等（连续运行行数稳定）。
- **kb_proposal_reorg.py `_extract_label`**：修复知识库索引所有课题标签雷同为「课题说明」的缺陷。brief 模板 H1 恒为"课题说明"，现跳过该通用标题，回退到 ID 推断。
- 新增回归测试 `scripts/tests/test_kb_proposal_reorg.py`（4 用例 12 断言：不重复追加、幂等、手工章节保留、标签回退），并纳入 `self_test.py --module` 清单。
- `python3 scripts/self_test.py --module`：320/320 → 332/332 通过

## v6.8.5 - 2026-08-06 仪表盘首页升级：四课题轮转进展 + 今日执行轨迹

### 改动内容

- **web/js/dashboard.js**：仪表盘首页中段重构
  - 新增 `/api/lifecycle/kanban` 数据源获取（系统看板：四课题轮次/分数/进度、执行历史）
  - `renderProposalProgress()`：四课题轮转进展板块（替代原六阶段漏斗），展示课题名、轮次标签、质量分、jobs 进度条、聚焦高亮、失败计数；点击跳转课题详情
  - `renderTodayTimeline()`：聚焦课题今日执行轨迹时间线，按本地时间分桶聚合（最多 4 段），显示时段/任务数/运行状态（正常 vs 重试）/关键步骤，末段高亮表示进行中
  - 聚焦课题今日数据不足 3 条时自动回退到当天全部记录，保证板块稳定渲染
- **web/css/style.css**：新增 `dash-prop-*`（进展行/进度条/轮次标签/分数）与 `dash-tl-*`（时间线步骤/状态点/计数）样式，复用现有 CSS 变量，自动适配深/浅色主题；补充 1100px/600px 两档响应式（时间线换行、窄屏隐藏进度条）
- **web/index.html**：`style.css` 与 `dashboard.js` 缓存版本号 `6.8.0`→`6.8.5`

### 验证结果
- `node --check web/js/dashboard.js`：语法正确
- 数据源复用既有 `GET /api/lifecycle/kanban`，无后端改动

## v6.8.4 - 2026-08-05 整体检验：辅助链路文档补全 + 数据清理 + .gitignore 加固

### 改动内容

- **AGENTS.md**：版本号 6.8.2→6.8.4，测试基线 252→320，新增辅助链路章节（健康检查/看板/定期修复/自成长），补充 `lifecycle_monitor.py`/`prompt_optimizer.py`/`retrospective.py`/`orchestrator.py` 维护命令
- **.gitignore**：补充 `/memory/prompt-backups/`、`/memory/weekend-*/`、`/memory/*.md`、`research_proposals/_lifecycle.json`、`/knowledge/qa/`、`/projects/*/kb/`、`.zcode/` 等遗漏规则
- **数据清理**：
  - `tuning-log.json`：清空 11 条 self_check 测试数据
  - `debug-journal.json`：移除 3 条无效/测试条目（重复 ID、prompt_tuning 测试、空条目），保留 4 条有效记录
  - `reflow-state.json`/`sync-state.json`：移除无效 `"sessions"` 条目
  - `background-tasks.json`：清空 6 条陈旧测试任务
  - `debug-journal-report.md`：删除过期报告
  - 删除遗留 `proposals/` 目录（已被 `research_proposals/` 替代）
  - 清理 `__pycache__/`、`.DS_Store`、`web_server.log`

### 验证结果
- `python3 scripts/self_test.py --module`：320/320 通过

## v6.8.3-fix13 - 2026-08-05 修复 derived job 优先级导致轮次无法完成

### 改动内容

- **lifecycle/micro_scheduler.py** `_CHAIN_ORDER`: 加入 `STEP_UPDATE_VISION`(7) 和 `STEP_UPDATE_METHOD_MANUAL`(8)
  - 问题：derived job 不在优先级映射中，默认优先级 99（最低），被下一轮 critic（优先级 0）抢占
- **lifecycle/micro_scheduler.py** `_job_priority_key`: 优先级键加入 `round_num` 作为第一维度
  - 问题：仅靠 `_CHAIN_ORDER` 不足以修复——下一轮 critic（chain_order=0）仍比当前轮 derived（chain_order=7）优先
  - 修复：优先级键从 `(chain_next, chain_order, scheduled_at, job_index)` 改为 `(round_num, chain_next, chain_order, scheduled_at, job_index)`
  - 确保当前轮次的 job 总是优先于下一轮，先完成当前轮再开下一轮
- **scripts/tests/test_derived_job_priority.py**: 新增 13 个回归测试
  - 覆盖：_CHAIN_ORDER 完整性、优先级值合理性、derived vs 下一轮 critic 竞争、完整轮次完成+报告生成

### 验证结果
- `python3 scripts/self_test.py --module`：320/320 通过
- Moire R8 待执行 job 正确识别为 `r8/rationale/lit_search`
- Cron 框架 14 个任务全部 active，无重复

## v6.8.3-fix12 - 2026-08-05 修复轮次完成后未 break 导致同时段启动新一轮

### 改动内容
- **lifecycle/micro_scheduler.py** `run_micro_scheduler`: 轮次完成后添加 `break`
- **scripts/tests/test_round_complete_break.py**: 新增 7 个回归测试

### 验证结果
- `python3 scripts/self_test.py --module`：307/307 通过

## v6.8.3-fix11 - 2026-08-05 references critic 轻量化优化

### 改动内容

- **proposal_lifecycle/optimize.py** `_run_critic`: 新增 references 专用轻量化 prompt 分支
  - 问题：references critic 使用与 rationale/content/scheme 完全相同的重型 prompt（叙述式检查、创新性评分、7模块完整性），对参考文献检验完全无意义，浪费 agent 算力
  - 优化后：references 只检查引文格式、编号一致性、引用相关性、缺失引用、数量/时效性，timeout 从 900s 降至 300s（5min）
  - 评分简化：只评严谨性 + 完整性，创新性/可行性固定 0.85（不影响综合评分均值）

- **lifecycle/executor.py** `_run_critic_step`: references 模块跳过 researcher 链注入
  - 参考文献检验本身就是文献检查，不需要再插入 gap_identify → lit_search → lit_read → lit_note

### 预期效果
- references critic 耗时从 ~360s 降至 ~120-180s（prompt 更短、不需要 7 模块检查）
- references 步骤总任务数从可能的 6 步（critic + 4 researcher + writer）固定为 2 步（critic + writer）

### 验证结果
- `python3 scripts/self_test.py --module`：300/300 通过

## v6.8.3-fix10 - 2026-08-05 修复 monitor 看板 updated_at_local 陈旧

### 改动内容

- **lifecycle_monitor.py** `_update_kanban`: 同步刷新 `updated_at_local` 字段
  - 根因：`lifecycle_monitor.py` 的 `_update_kanban` 在每小時监控被触发时
    只更新 `updated_at`（UTC）与 `hourly_monitor` 两个字段，**漏写了
    `updated_at_local`**。`micro_scheduler` 不在工作时隙内时不会调用
    `_update_kanban`，导致 `updated_at_local` 长时间停滞在上次
    `micro_scheduler` 执行时间（如 12:30:57），而 `updated_at` 在 monitor
    每小時执行时被刷新到当前时刻。最终 `proposal_lifecycle.py --kanban`
    CLI / 监控 UI 读取的"更新时间"呈现 1-6 小时前的陈旧值，运维误判为
    链路静默，触发不必要的告警风暴
  - 触发场景：每个非工作时隙（如 12:30-18:30、20:30-22:30）都会令
    `updated_at_local` 滞留，最多落后 `updated_at` 6 小时
  - 修复后 `_update_kanban` 同时写入 `updated_at_local`，与 `updated_at`
    保持最近一次写入时刻一致

- **tests/test_monitor_kanban_local.py**: 新增 3 个测试用例（11 个断言）
  - 测试 1：监控器更新后 `updated_at_local` 不再停留陈旧值
  - 测试 2：初始看板缺 `updated_at_local` 时也能被补上
  - 测试 3：monitor 与 scheduler 共存时保留 scheduler 写入的所有字段
    （current / execution_history / day_key / proposals / task_sync）

### 验证结果
- `python3 -m py_compile scripts/lifecycle_monitor.py scripts/tests/test_monitor_kanban_local.py` 通过
- `python3 scripts/self_test.py --module`：300/300 通过（包含 monitor 看板本地时间戳 11/11）

## v6.8.3-fix9 - 2026-08-05 修复跨时段 stale job 无法回收 + hermes 超时进程清理

### 改动内容

- **lifecycle/micro_scheduler.py** `run_micro_scheduler`: 将 stale 清理从时段检查之后移到之前
  - 根因：`run_micro_scheduler` 第一步"时段检查 → return"在 stale 清理之前，不在工作时段内时直接返回，
    `_refresh_stale_jobs` 永远不执行。references-critic 在时段末尾启动（11:35），时段结束后卡在 running
    状态超过 95 分钟无法回收，直到下一个时段（18:30）才开始处理，阻塞所有下游任务
  - 修复后 stale 清理在时段检查之前无条件执行，每 5 分钟 cron 触发时即使不在工作时段也能回收超时 job

- **lifecycle/constants.py** `STALE_RUNNING_SECONDS`: 从 3600s（60min）降低到 1800s（30min）
  - 原因：critic/writer 的 subprocess timeout 为 900s（15min），历史平均 6.3min，最长 12.2min
  - 1800s 给 hermes 足够的退出缓冲，同时将卡住检测从 60min 缩短到 30min

- **proposal_lifecycle/optimize.py** `_run_hermes`: 使用 Popen + `start_new_session=True` + `os.killpg` 替代 `subprocess.run(timeout=N)`
  - 根因：`subprocess.run(timeout=N)` 在超时后只杀死直接子进程，但 hermes CLI 连接持久化 gateway，
    gateway 内的 agent loop 在独立进程中继续运行，导致 CLI 的 stdout/stderr 管道不释放，
    Python 侧 `subprocess.run` 永远收不到子进程退出信号，timeout 实际未生效
  - 修复后使用 `start_new_session=True` 使 hermes CLI 成为新进程组 leader，
    timeout 后用 `os.killpg(SIGTERM)` → wait 5s → `os.killpg(SIGKILL)` 三级清理，
    确保整个进程组被杀死

- **tests/test_stale_cleanup_out_of_slot.py**: 新增 4 个测试用例（9 个断言）
  - 测试 1：不在时段内时 stale running job 仍被标记为 failed（核心回归）
  - 测试 2：多个 proposal 的 stale job 都被清理
  - 测试 3：正常 pending job 不受 stale 清理影响
  - 测试 4：running 但未超时的 job 不被误杀

### 验证结果
- `python3 scripts/self_test.py --module`：289/289 通过（跨时段 stale 回收 9/9）

## v6.8.3-fix8 - 2026-08-05 修复微调度器卡死 proposal 永久占用时段焦点

### 改动内容

- **lifecycle/micro_scheduler.py** `_is_proposal_stuck`: 同时检查 `attempts` 与单调递增的 `repair_attempts`
  - 根因：`orchestrator.py` `_run_repair` 在 failed→pending 重置时把 `attempts` 清零，而旧逻辑只看
    `attempts >= MAX_JOB_ATTEMPTS`，导致反复失败、已被修复系统放弃的 job 永远判不出 stuck
  - 修复后两者任一达标即视为卡死，使修复系统已放弃的 job 能被正确识别

- **lifecycle/micro_scheduler.py** `_focus_proposal_for_slot`: round_done=false 的 early-return 前增加 stuck 检查
  - 根因：进行中轮次未完成时直接 `return prev_pid`，绕过下方第 988 行 `_is_proposal_stuck` 兜底，
    导致卡死 proposal 永久占用时段焦点、饿死其余 proposal（v6.8.3-fix5 轮次连续性修复的回归风险）
  - 修复后卡死时落入 `move_to_queue_end` 让出焦点，未卡死时仍继续聚焦以保证轮次连续性

- **tests/test_micro_scheduler_rotation.py**: 新增 2 个守护测试
  - 测试 5：`attempts=0` 但 `repair_attempts>=MAX` 时 `_is_proposal_stuck` 应返回 True
  - 测试 6：进行中轮次未完成但 proposal 卡死时 `_focus_proposal_for_slot` 应让出焦点

### 验证结果
- `python3 -m py_compile scripts/lifecycle/*.py scripts/tests/test_micro_scheduler_rotation.py`：通过
- `python3 scripts/self_test.py --module`：280/280 通过（微调度器轮转测试 9/9）

## v6.8.3-fix7 - 2026-08-05 Prompt 优化器单元测试 + Cron 框架集成

### 改动内容

- **test_prompt_optimizer.py**: 新增 12 个测试用例（29 个断言），覆盖权限错误处理全链路
  - 备份/读取/写入三种 PermissionError 场景的 apply_error 标记
  - `_apply_suggestions` 失败建议标记 status=failed、成功标记 status=applied
  - `_log_auto_applied` 正确调用 debug_journal.add_entry 并写入 prompt_tuning 条目
  - debug_journal 不可用时静默失败（不抛异常）
  - auto 模式下失败建议不写入 debug journal
  - 正常应用时备份文件创建、目标文件内容修改、内容已存在跳过
  - 已纳入 `self_test.py --module` 回归（256/256 通过）

- **lifecycle/framework.py**: `setup_cron_framework` 新增 prompt 自动优化 + 复盘 cron 注册
  - `lc-prompt-optimize`：每天 14:00 执行 `prompt_optimizer.py auto`（工作日时段间隙）
  - `lc-retrospective`：每周一 15:00 执行 `retrospective.py --period 7d`（周末反思产出后）
  - 随 `--setup-cron-v2` 一并安装，随 `--teardown-cron-v2` 一并卸载

- **lifecycle/controller.py**: `_write_generic_wrappers` 新增 `lc_prompt_optimize.sh` 和 `lc_retrospective.sh` 包装脚本

- **lifecycle/constants.py**: 新增 `DEFAULT_PROMPT_OPTIMIZE_SCHEDULE` 和 `DEFAULT_RETROSPECTIVE_SCHEDULE` 常量

- **lifecycle_monitor.py**: `REQUIRED_CRON_PREFIXES` 新增 `lc-prompt-optimize` 和 `lc-retrospective`

- **self_test.py**: `--module` 过滤器新增 `test_prompt_optimizer`

### 验证结果
- `python3 scripts/self_test.py --module`：256/256 通过
- `python3 scripts/prompt_optimizer.py --self-check`：通过
- `python3 scripts/tests/test_prompt_optimizer.py`：29/29 通过

## v6.8.3-fix6 - 2026-08-05 周末反思接驳复盘 + Prompt 自动优化闭环

### 改动内容

- **retrospective.py**: 周末反思产出自动接驳到复盘报告
  - 新增 `_load_weekend_reflections()` 函数：读取 `weekend-reflection/` 下的反思报告（patterns、next_actions、健康快照）和 `weekend-input/` 下的输入端产出（ideas、decisions、directions）
  - 新增 `_analyze_weekend_reflections()` 函数：对反思产出做轻量分析，提取 top patterns 和 actionable items
  - 复盘报告新增"第 6 章：周末反思整合"，包含关键模式、健康趋势表格、输入端产出统计
  - 周末反思的 next_actions 自动合并到报告的行动建议章节
  - 报告从 6 章扩展到 7 章

- **prompt_optimizer.py**: Agent 分数到 prompt 的自动反馈闭环
  - 新增 `cmd_auto()` 函数：自动分析 + 安全过滤 + 应用 + 记录到 debug journal
  - 安全过滤：只自动应用 high/medium 级别建议，跳过 critical
  - 自动应用记录到 debug journal（category=prompt_tuning, tags=auto_applied）
  - `--apply` 改名为手动模式，保留人工介入入口
  - 新增 `_apply_suggestions()` 内部共享函数，消除重复代码

### 已完成
- prompt 自动优化 cron 已集成到 `--setup-cron-v2` 框架（fix7 完成）

## v6.8.3-fix5 - 2026-08-05 微调度器轮转 off-by-one 修复

### 改动内容

- **micro_scheduler.py**: 修复 `_focus_proposal_for_slot` 让出检查的 off-by-one bug
  - 根因：fix4 将 `current_round = completed_rounds + 1`（进行中轮次）误改为 `current_round = completed_rounds`（已完成轮次）
  - 影响：已完成 ≥1 轮的 proposal 在下一轮进行中会被误判为"本轮完成"而提前让出时段，中断连续聚焦，严重拖慢多轮优化
  - 修复：恢复为 `completed_rounds + 1`，与 `_sync_single_proposal_to_task`（L574）和调用方（L1156）的统一约定一致
  - 清理：移除 yield 检查中未使用的 `stuck` 变量（死代码，stuck 处理已交由 repair/健康检查）
- **test_micro_scheduler_rotation.py**: 新增 7 项回归测试，覆盖轮次编号选择逻辑

### 验证结果
- `self_test.py --module` 227/227 通过（含新增 7 项）
- 已验证：还原 bug 后 5/7 测试失败，修复后 7/7 通过

## v6.8.3-fix4 - 2026-08-05 微调度器轮转逻辑修正

### 改动内容

- **micro_scheduler.py**: 按设计意图重写时段轮转逻辑
  - `_is_round_complete()` 增加产物+标签双重检查：pipeline_jobs 全部 done + 5 个 section 文件存在且非空（>50B）
  - 时段切换的唯一条件：当前轮双重检查通过。未完成则继续聚焦（无连续时段上限），保证每轮优化的上下文连续性
  - 卡住（stuck）不再触发时段切换，由 repair（每6h重置 failed job）和健康检查（每1h告警）负责发现并修复

### 验证结果
- `self_test.py --module` 220/220 通过

## v6.8.3-fix3 - 2026-08-05 健康检查增强 + 微调度器修复 + 知识库修复

### 改动内容

- **lifecycle_monitor.py**: 健康检查全面增强
  - cron 完整性检测：从仅检查 2 个前缀扩展到检查 4 个核心前缀（orchestrate/repair/micro/monitor）+ weekend
  - cron 执行新鲜度检测：关键调度 cron 超过 2h 未执行则告警
  - 全链路零进展检测：done 不变且 pending>0 超过 3h 告警
  - cron 缺失自动修复：自动调用 `--setup-cron-v2` 重建框架
  - failed job 检测：从仅 `attempts>=3` 改为任何 failed 立即告警
  - 同类 step 连续失败：从仅检查 lit_search 扩展到所有 step
  - 系统性错误检测：扫描执行历史中 429 限流和权限错误模式

- **micro_scheduler.py**: 微调度器轮转修复
  - 新增 `_count_consecutive_slots()` 函数，限制单课题最多连续聚焦 2 个时段
  - 修复"完成一轮后立即开始下一轮导致霸占时段"的 bug：改为检查最近完成的一轮是否全部 done，若是则让出时段

- **executor.py**: gap_identify 容错增强
  - 当 researcher agent 返回非 JSON（自然语言分析）时，不再报错，生成空 gaps 兜底文件让流程继续

- **knowledge/**: 知识库批量修复（通过 `kb_health_repair.py` 和 `kb_fill_wiki_notes.py`）
  - 删除 3 组重复论文文件，修正 5 篇 NSFC 论文的 project 标记
  - 清除 7 篇 2607.xxx 系列错误标记，删除测试残留
  - 补齐 39 篇深度分析未落盘的 wiki 笔记（34→73 篇）

- **AGENTS.md / docs/ARCHITECTURE.md**: 更新所有 profile 模型为 MiniMax-M3

- **hermes profile researcher**: 配置 fallback 链（glm-5.2 → MiniMax-M2.7）

- **_lifecycle.json**: 修复 4 个 proposal 的 transition_history 与 status 不一致

### 验证结果
- `self_test.py --module` 220/220 通过

## v6.8.3-fix2 - 2026-08-05 健康检查修复: ProposalSections 路径错误导致 full_review 读不到申请书

### 改动内容

- **optimize.py**: 修复 `_run_critic`（第279行）和 `_run_writer`（第619行）中 `ProposalSections(prop_dir)` 误用顶层 proposal 目录
  - 根因：`prop_dir` 为 `{stage}/{proposal_id}`（如 `optimizing/general-xxx-20260726`），但 `ProposalSections` 期望传入 `04_proposal` 子目录。误传导致 `sections_dir` 指向顶层空的 `sections/` 目录（历史残留 0 字节文件），`section_exists()` 对所有章节返回 False
  - 影响：`is_full_review`（整体一致性审查）模式下，critic 的 `files_to_read` 列表为空——**评审 agent 收不到任何申请书内容文件路径**，在无内容基础上产出空泛评审。writer 的 `section_files` 列表同样为空，`assemble_draft()` 也写入错误位置
  - 触发场景：任一 proposal 完成三章节评审后进入 full_review 步骤即触发

### 验证结果
- `python3 -m py_compile scripts/proposal_lifecycle/optimize.py` 通过
- `self_test.py --module` 220/220 通过（含新增 5 个章节路径正确性测试）

## v6.8.3-fix1 - 2026-08-04 健康检查修复: 方法名拼写 + JSON解析遗漏

### 改动内容

- **controller.py**: 补全 `_mark_degradation` 的导入与类绑定（v6.8.3 在 executor.py 新增了该方法及调用，但遗漏在 controller.py 绑定）
  - 影响：lit_search/gap_identify 的 agent loop 失败降级路径调用 `self._mark_degradation(...)` 时抛出 `AttributeError: 'LifecycleCronController' object has no attribute '_mark_degradation'`，导致**降级逃生阀本身崩溃**——本应优雅降级（agent loop 失败→LiteratureService 兜底）的 job 被直接标记 FAILED。2026-08-04T01:51:38Z 的 lit_search 失败即为此触发
- **executor.py**: 修复 `_mark_degradation` 和 `_run_monitor_step` 中调用不存在的 `_save_proposal_state`（正确方法名为 `_set_proposal_state`）
  - 影响1（`_mark_degradation`，第96行）：被 try/except 静默吞掉，降级事件从未被记录——v6.8.3 的"降级追溯"功能完全失效
  - 影响2（`_run_monitor_step`，第1080行）：未受 try/except 保护，当逃生阀触发且分数低于达标线时抛出 `AttributeError`，导致 proposal 已 transition 到 pending_review 但 job 被标记 FAILED，引发状态不一致
- **literature_service.py**: 修复 `_try_parse_json` 中无条件的 `break`，允许扫描后续 `[` 位置
  - 影响：当 LLM 输出自然语言中包含 `[` 字符（如"搜索了[关键词]"）时，JSON 数组解析器在第一个 `[` 处失败后直接退出，不再尝试后续的真正 JSON 数组。论文降级为自然语言提取路径，因 `_needs_metadata` 标记被 `_import_to_kb` 跳过，导致文献未入库

### 验证结果
- `python3 -m py_compile scripts/*.py` 全部通过
- `self_test.py --module` 215/215 通过（含新增 2 个降级追溯测试 + 7 个解析器测试）

## v6.8.3 - 2026-08-04 质量保障: 逃生阀质量警告 + JSON 解析增强 + 降级追溯

### 改动内容

- **completion.py**: 逃生阀（连续无提升/达到最大轮数）触发时，若分数低于达标线，附加 quality_warning 标记写入 proposal_state 并传递至 transition 结果
- **executor.py**: 新增 `_mark_degradation()` 记录降级事件到 proposal_state（gap_identify→llm_direct、lit_search→LiteratureService）；gap_identify/lit_search prompt 改为 JSON 格式输出 + 多层兜底解析（JSON对象提取、markdown代码块剥离、空输出默认空gaps）；lit_search agent 成功执行即视为 success（0篇论文不等于失败）
- **literature_service.py**: `_parse_researcher_output` 重构为多格式兼容（JSON数组 > 管道符 > Markdown表格 > 自然语言提取）；`_dispatch_researcher` 改为 hermes CLI oneshot 优先 + LLM网关降级；`_import_to_kb` 跳过缺元数据条目防污染；`deep_read` 统一降级链
- **optimize.py**: gap_data 解析增加 try/except 兜底；DIMENSION_FLOOR 阈值提升（0.65/0.60 → 0.70/0.65）避免偏科通过
- **constants.py**: DEFAULT_MAX_ROUNDS 5→8、DEFAULT_NO_IMPROVEMENT_LIMIT 3→5，给予更多优化空间
- **lifecycle_monitor.py**: 看板更新改为读-改-写，不覆盖 scheduler 写入的详细格式
- **external_fetcher.py**: deepxiv JSON 解析增加异常捕获
- **退回残缺 proposal**: key-transient-quantum-phase-optical-20260726（5模块全false、分数0.15、3个模块为占位符<100字节）从 pending_review 退回 optimizing，轮次归零

### 验证结果
- `python3 -m py_compile scripts/*.py` 全部通过
- `self_test.py --module` 194/194 通过（含生命周期cron、对抗评审、周末任务、微调度器）

## v6.8.2 - 2026-08-03 根因防御: 健康检查新增 cron 检测 + 升级流程自动安装 cron

### 改动内容

#### 根因分析
- cron 未安装的根因是升级流程(upgrade.py)未包含 cron 安装步骤，且每日健康检查
  (daily_health_check.py) 也未检测 cron 是否存在，导致用户升级后不知需手动执行
  `--setup-cron-v2`。

#### 修复措施
- **`scripts/daily_health_check.py`**: 新增第 7 段"生命周期 cron"检测，检查
  lc-micro-scheduler 和 lc-weekend-* 是否已通过 hermes_bridge 注册（读取 profile
  cron jobs.json 而非系统 crontab）。缺失时在建议动作中提示修复命令。
- **`scripts/upgrade.py`**: 新增步骤 5，升级完成后自动通过 `_ensure_cron_installed()`
  检查生命周期 cron 是否注册，缺失则调用 `setup_cron_framework()` 自动安装。失败时
  提示人工运行 `python3 scripts/proposal_lifecycle.py --setup-cron-v2`。

#### 两项遗留处理
- 执行 `kb_maintenance.py --weekly`，知识库综合分 0.651 → 0.673
- 确认 5 个生命周期 cron 已通过 hermes_bridge 注册（lc-micro-scheduler + 4 个 weekend crons）

### 验证结果
- 194 模块测试 / 248 Web-CI 测试全部通过
- `daily_health_check.py --dry-run` 显示 cron✓ 检测正常

## v6.8.2 - 2026-08-02 Researcher Profile 混合调用与记忆回写 + 健康检查修复

### 改动内容

#### 新增模块
- **`scripts/hermes_memory.py`** — 新增 Hermes Profile 记忆回写工具模块，提供：
  - `_run_hermes_agent(profile, prompt, timeout)` — 调用 hermes agent loop（oneshot 模式）
  - `_write_memory(profile, content)` — 追加记忆条目到 profile 的 MEMORY.md（原子写入）
  - `_write_memory_batch(profile, entries)` — 批量追加多条记忆
  - `_inject_minimax_env(env)` — 自动透传 MiniMax API Key 到 hermes 子进程环境

#### 生命周期执行器改造
- **`scripts/lifecycle/executor.py`** — 三个 researcher 子步骤改为混合策略（方案A+B融合）：
  - `_run_gap_identify_step`：优先 hermes researcher agent loop → 失败降级 llm_router 直调 → 回写记忆
  - `_run_lit_search_step`：优先 hermes researcher agent loop 联网检索 → 失败降级 LiteratureService.search() → 回写记忆
  - `_run_lit_read_step`：优先 hermes researcher agent loop 深度阅读 → 失败降级 LiteratureService.read() → 回写记忆
  - 每次回写记忆包含：任务类型、课题ID、轮次、章节、结果摘要、执行方式（agent_loop / direct_fallback）

#### 缺陷修复
- **`scripts/proposal_lifecycle/cli.py`** — 修复周末模式 `--repair --dry-run` 时 KeyError: 'proposal_id'，周末修复结果返回的条目使用 `job` 键而非 `proposal_id` 键，已兼容处理两种结构。

### 验证结果
- 语法检查：171/171 脚本通过（含 `scripts/lifecycle/` 子包）
- 自检：`python3 scripts/hermes_memory.py` ✓ 通过 | `python3 scripts/hermes_bridge.py` ✓ 通过
- 回归测试：`--module` 192/192 | `--scenario` 16/16 | `--persona` 38/38 | `--web-ci` 246/246 全量通过
- Profile 健康：7 个 profile 均正常（linsai/pipeline-runner/researcher/analyst/writer/critic/reviewer）
- 生命周期修复：周末模式 dry-run 无异常，3 个周末任务均 done
- 知识库健康：226 raw / 153 wiki / 4658 chunks / 0 orphan / 0.79 图连通率
- 无未修复问题

## v6.8.1 - 2026-08-02 文献系统统一架构重构

### 改动内容

#### 文献笔记后端迁移
- **`scripts/literature_notes.py`** — 阅读笔记存储后端从 `{proposal_dir}/02_literature/reading-notes.md` 迁移到 `knowledge/wiki/papers/{arxiv_id}.md`，按 `### {proposal_id}` 分段写入。原路径改为动态生成的只读兼容视图。
- **`scripts/kb_wiki.py`** — 新增 wiki/papers/ 页面管理辅助函数，支持按 arxiv_id 查找/创建/更新论文 wiki 页面。

#### 知识库导入器增强
- **`scripts/kb_importer.py`** — 新增 `has_pdf` 自动检测（扫描 PDF_DIR）；frontmatter 扩展 `read_status`、`used_by_proposals`、`has_pdf` 字段；新增 `WIKI_PAPERS_DIR` 常量支持 wiki/papers/ 双向写入。

#### 知识库门面扩展
- **`scripts/knowledge_base.py`** — 新增 `_slugify()`、`_render_proposal_body()`、`save_extracted_knowledge()` 等函数，支持 proposal wiki 页面渲染和知识萃取统一入口。

#### 研究管线接入 LiteratureService
- **`scripts/proposal_lifecycle/optimize.py`** — `_run_lit_search()` 改为通过 `LiteratureService.search()` + `get_context()` 统一检索/入库/状态查询，替换原有直接调用 `_build_kb_context_from_gap` + `_run_hermes("researcher")` 的逻辑。

#### 提案知识库同步增强
- **`scripts/proposal_kb_sync.py`** — 重构同步逻辑，通过 `save_extracted_knowledge()` 门面写入 wiki 页面，自动构建 frontmatter 和图谱关联。

#### 知识萃取输出改造
- **`scripts/knowledge_output.py`** — `_write_wiki_page()` 委托 `knowledge_base.save_extracted_knowledge()` 处理，统一 frontmatter 构建、双向链接注入和生长日志记录。

#### 周末流水线增强
- **`scripts/weekend_pipeline/output_jobs.py`** — `run_output_generate_weekly_report()` 增强为汇总各 job 执行结果的结构化报告。
- **`scripts/weekend_pipeline/pipeline.py`** — 新增依赖链修复逻辑。
- **`scripts/weekend_pipeline/executor.py`** — 执行器增强。
- **`scripts/weekend_pipeline/reflection_jobs.py`** — 反思阶段新增健康检查任务。
- **`scripts/weekend_pipeline/jobs.py`** — Job 定义微调。
- **`scripts/tests/test_weekend_pipeline.py`** — 测试用例同步更新。

#### 生命周期增强
- **`scripts/lifecycle/executor.py`** — 执行器逻辑增强。
- **`scripts/lifecycle/orchestrator.py`** — 编排器新增方法。

#### 基础设施改进
- **`scripts/sync_engine.py`** — `_save_sync_state()` 加跨进程 `file_lock`，防止多实例并发写入丢失历史。
- **`scripts/tool_engine.py`** — 命令执行白名单和错误处理优化。
- **`scripts/web_routes_projects.py`** — 项目路由增强。
- **`scripts/hermes_pipeline.py`** — 管线派活逻辑微调。

#### 数据迁移工具
- **`scripts/migrate_literature_unified.py`**（新增）— 文献统一架构数据迁移脚本，支持 `--dry-run` 预览和 `--backup` 自动备份。迁移步骤：合并 paper-pool 状态到 KB frontmatter、合并 item-status 历史到 KB frontmatter、迁移深度解析到 wiki/papers/、迁移 per-proposal 阅读笔记到 wiki/papers/、迁移讨论记录到 qa/ 层、重建索引和图谱。含 `_self_check()` 自检。

#### 其他微调
- `scripts/state_sync.py`、`scripts/project_context.py`、`scripts/project_reader.py`、`scripts/proposal_lifecycle/constants.py` — 路径引用和常量同步更新。

### 验证结果
- `python3 -m py_compile scripts/*.py` 语法检查全部通过。
- `python3 scripts/self_test.py --module` 192/192 通过。
- `python3 scripts/self_test.py --web-ci` 246/246 通过（含人格 38/38 + 场景 16/16）。
- `python3 scripts/migrate_literature_unified.py --self-check` 自检全部通过。

---

## v6.8.1 - 2026-08-02 文献简报→知识库零拷贝通路

### 问题根因
- hermes linsai profile 每日产出的文献简报（`daily_candidates.json`）只存在于 hermes workspace，CoPilot 知识库看不到。
- `kb_auto_sync` LaunchAgent 从未安装，`sync_engine` 同步链路断裂 7 天。
- 旧的"同步搬运"方案（拷贝 JSON → 转换 .md → 写入 raw/papers/）笨重、有延迟、有冗余。

### 设计原则
- **零拷贝**：CoPilot 直接读取 hermes 产出目录，不做数据搬运。
- **惰性物化**：首次访问时自动在 `raw/papers/` 生成对应 .md，幂等。
- **显示器定位**：CoPilot 是 hermes 产出的消费者/显示器，不是数据仓库。
- **不破坏现有规则**：数据域隔离、管线只读、状态管理不变。

### 改动内容
- **hermes Job 1 prompt 更新** — `cron edit 636145dbddac`
  - 新增 Step 2：为新入池论文生成完整知识库简报（摘要+背景+发现+方法+创新+结论），写入 `briefings/papers/{arxiv_id}.md`。
  - 飞书推送的极简卡片格式不变。
- **路径常量** — `scripts/paths.py`
  - 新增 `HERMES_BRIEFINGS_DIR` 和 `HERMES_BRIEFING_PAPERS_DIR`。
- **索引引擎零拷贝扩展** — `scripts/kb_index.py`
  - `build_index()` 默认追加 `briefings/papers/` 目录，标签 `hermes-briefings`。
  - 测试隔离同步更新。
- **文献服务合并双源** — `scripts/literature_service.py`
  - `_scan_local_raw_papers()` 合并 `raw/papers/` + `briefings/papers/` 两个源。
  - 新增 `_materialize_from_briefing()`：惰性物化 hermes 简报为 CoPilot 格式 .md。
  - 新增 `_build_note_from_hermes_analysis()`：从 `deep_analysis_{aid}.json` 构建 wiki 阅读笔记。
  - `read()` 方法优先使用 hermes 深度分析 JSON（零延迟），无则降级联网检索。

### 验证结果
- `python3 -m py_compile` 语法检查全部通过。
- `python3 scripts/self_test.py --module` 192/192 通过。
- `python3 scripts/self_test.py --web-ci` 246/246 通过。
- `python3 scripts/self_test.py --scenario` 16/16 通过。
- 端到端验证：hermes 深度分析 JSON 成功转为 3276 字符阅读笔记；合并扫描 220 篇论文正常。

---

## v6.8.1 - 2026-08-01 任务系统打通 + 看板增强

### 问题根因
- 微调度器与 task_manager 任务系统完全隔离，生命周期优化进度在 Web 任务面板不可见。
- 用户无法在 Web 界面查看/触发生命周期状态同步。
- 看板（system-kanban.json）不包含任务系统统计信息，缺少 task_sync 字段。

### 新增功能
- **任务系统集成（lifecycle → task_manager）** — `scripts/lifecycle/micro_scheduler.py`
  - 新增 `_load_lifecycle_task_map` / `_save_lifecycle_task_map` / `_get_lifecycle_task_id` / `_set_lifecycle_task_id`：管理 proposal 轮次与 task_id 的映射关系。
  - 新增 `_sync_lifecycle_to_task_manager`：微调度器每次执行后自动同步所有 optimizing/pending_review/archived 的 proposal 到 task_manager，创建/更新任务并记录进度。
  - 新增 `_sync_previous_rounds_to_task_manager`：补全历史轮次（已完成但未创建 task 的轮次），支持首次启用时一键同步。
  - 新增 `_sync_single_proposal_to_task`：单个 proposal 的同步逻辑，支持创建/更新/状态流转（backlog→active→completed）。
  - 微调度器 `run_micro_scheduler` 末尾自动调用 `_sync_lifecycle_to_task_manager`。
- **看板增强** — `scripts/lifecycle/micro_scheduler.py`
  - `_update_kanban` 新增 `task_sync` 字段，包含 `enabled`、`stats`（全局统计）、`mapping_count`、`last_sync_at`。
  - 每个 proposal 的看板状态新增 `task_id`、`task_status`、`task_progress` 字段。
  - 收集 `task_manager` 全局统计（total/backlog/active/completed/lifecycle_tasks）。
- **CLI 命令** — `scripts/proposal_lifecycle/cli.py`
  - 新增 `--sync-lifecycle-tasks`：同步当前生命周期状态到任务系统。
  - 新增 `--sync-lifecycle-history`：同步历史优化轮次到任务系统。
  - 新增 `_update_kanban_task_sync` 辅助函数，同步后自动更新看板。
- **Web API 路由** — `scripts/web_routes_system.py`
  - 新增 `POST /api/lifecycle/sync-tasks`：触发生命周期任务同步。
  - 新增 `POST /api/lifecycle/sync-task-history`：触发历史轮次同步。
- **Controller 暴露** — `scripts/lifecycle/controller.py`
  - `LifecycleCronController` 绑定 `sync_lifecycle_to_task_manager` 和 `sync_lifecycle_history_tasks`。

### 修复内容
- `_sync_previous_rounds_to_task_manager` 中历史任务状态流转改为 `backlog → active → completed` 两步（原 `backlog → completed` 被状态机拒绝）。
- `_sync_lifecycle_to_task_manager` 中的 `_sync_single_proposal_to_task` 修复完成轮次未标记 completed 的问题。

### 验证结果
- `python3 -m py_compile` 语法检查全部通过。
- `python3 scripts/self_test.py --module` 192/192 通过。
- `python3 scripts/self_test.py --web-ci` 246/246 通过。
- `python3 scripts/self_test.py --scenario` 16/16 通过。
- 端到端验证：CLI 命令成功创建 39 个任务（5 个当前轮次 + 31 个历史轮次），Web API 路由正常响应。

### 设计原则
- **自动同步**：微调度器每次执行后自动同步，无需手动触发。
- **惰性加载**：`_load_lifecycle_task_map` 使用模块级缓存，仅在首次调用时加载文件。
- **并发安全**：`_save_lifecycle_task_map` 使用 `file_lock` 保护写盘操作。
- **幂等性**：`_sync_single_proposal_to_task` 先检查映射是否存在，存在则更新而非重复创建。

---

## v6.8.1 - 2026-08-01 修复 score 类型错误与跨周重新平衡机制

### 问题根因
- `literature_service.py` 中 `_get_paper_info` 返回的 score 字段可能为字符串或空字符串，排序时 `float("")` 抛出 ValueError/TypeError，导致 lit_search job 失败。
- `_parse_researcher_output` 使用 `.replace(".", "").isdigit()` 判断 score，对科学计数法、负数等格式不兼容。
- `paper_pool.py` 排序同样使用 `float(x[1].get("score", 0))`，未处理字符串 score。
- `micro_scheduler.py` 使用纯数字索引 `last_proposal_index` 追踪轮转位置，当 optimizing 列表跨周变化（新增/删除 proposal）时指向错误 proposal。

### 修复内容
- **score 类型安全转换** — `scripts/literature_service.py`
  - 新增 `_safe_float()` 静态方法，安全处理 None/空字符串/字符串数字/各类输入。
  - `_get_paper_info`、`_parse_researcher_output` 及 3 处排序（`_build_local_knowledge_context`、`_search_raw_papers`、`_search_researcher`）均使用 `_safe_float` 转换。
- **paper_pool.py 排序安全** — `scripts/paper_pool.py`
  - 排序时使用局部 `_safe_score` 函数安全转换 score。
- **跨周重新平衡机制** — `scripts/lifecycle/micro_scheduler.py`
  - 新增 `_rebalance_index()` 函数：根据 `last_proposal_id` 重新校准轮转索引，当 optimizing 列表跨周变化时自动找到正确位置。
  - `_load_focus_state` 增加 `last_proposal_id` 字段追踪。
  - `_focus_proposal_for_slot` 每次进入先调用 `_rebalance_index` 校准索引，推进时同步保存 `last_proposal_id`。

### 验证结果
- `python3 -m py_compile scripts/literature_service.py scripts/paper_pool.py scripts/lifecycle/micro_scheduler.py` 通过。
- `python3 scripts/self_test.py --module` 187/187 通过。

### 设计原则
- **防御性编程**：所有外部输入（文件读取、LLM 输出）的数值字段一律经过安全转换，避免类型错误阻塞链路。
- **内容感知索引**：轮转位置追踪从纯数字索引改为 `last_proposal_id` 内容感知，适应灵活的 proposal 列表变化。

---

## v6.8.0 - 2026-07-31 申请书五模块化 + 微调度器 + 周末任务适配

### 问题根因
- 旧版申请书按 7 模块拆分（立项依据/研究内容/研究方案/特色与创新/预期研究成果/年度研究计划/参考文献），模块过细，导致撰写与评审碎片化，一致性差。
- worker 每小时无脑挑一个 pending job 执行，不保证同一 proposal 的连贯推进，经常出现"一天跑不完一轮"的情况。
- monitor 任务 checkpoint 的 `section_key` 误用为 `references`，与 section 占位符不匹配，导致 monitor job_id 冲突。
- 周末输入/输出/反思任务与新的 proposal 目录结构（`00_proposal-brief.md`、`03_method/method-manual.md`、`02_literature/reading-notes.md`）不完全适配。

### 改造内容
- **申请书五模块化** — `scripts/proposal_sections.py` / `scripts/proposal_lifecycle/`
  - 新 5 模块：立项依据（rationale）、研究内容（content）、研究方案含特色创新与预期成果（scheme）、整篇一致性审查（full_review）、参考文献校验（references）。
  - 移除独立 `innovation` / `outcome` / `plan` 模块，将特色创新与预期成果并入 `scheme`。
  - 新增 `scripts/migrate_sections_v680.py`，自动将 5 个 optimizing proposal 的旧 7 模块目录迁移到新结构，旧文件备份到 `backups/sections-migration-20260731/`。
- **章节评审 + 整体评审 + 参考文献校验**
  - 三章节（rationale/content/scheme）先并行进行 writer-critic 对抗。
  - 全部章节达标后进入 `full_review`，只聚焦连贯性和统一性，不再重写具体章节。
  - `references` 作为独立模块放到一致性审查之后，校验引用准确性、补充遗漏文献。
- **微调度器 + 四时段轮转** — `scripts/lifecycle/micro_scheduler.py`
  - 工作日 4 个时段：00:30-03:30、04:00-08:00、08:30-12:30、18:30-22:30。
  - 每个时段只聚焦一个 proposal；若该 proposal 完成完整一轮，下一时段切换新 proposal；否则继续聚焦。
  - 通过 `lifecycle-focus.json` 记录聚焦历史，保证断点续传。
- **Monitor checkpoint 修复** — `scripts/lifecycle/controller.py`
  - monitor job 的 `section_key` 从 `references` 修正为 `"monitor"`，避免与 references 模块冲突。
  - 重新生成 5 个 optimizing proposal 的 25-job checkpoint。
- **周末任务适配** — `scripts/weekend_pipeline/`
  - `registration.py`：新课题注册时初始化 `00_proposal-brief.md`、`03_method/method-manual.md`、`02_literature/reading-notes.md`。
  - `enrich_from_idea()` 写入 draft 后自动按新 5 模块拆分。
  - `output_jobs.py`：归档 proposal 时把核心产物复制到 `knowledge/raw/projects/{proposal_id}/`，并从申请书+方法学手册萃取知识写入 wiki。
  - `reflection_jobs.py`：报告按新 5 模块统计模块状态。
  - `proposal_kb_sync.py`：同步路径适配新目录结构。

### 前端适配（v6.8.0 第二批次）
- **导航精简** — `web/index.html` / `web/js/app.js`
  - 主导航固定为 5 项：仪表盘 / 控制台 / 全链路 / 知识库 / 设置。
  - 移除 hermes / pipeline 页面入口的特殊点击处理，避免跳转失败或空白页。
  - 所有前端静态资源版本号统一为 `v=6.8.0`，防止浏览器缓存旧代码。
- **全链路页面适配 5 模块** — `web/js/lifecycle.js`
  - 课题卡片展示新 5 模块进度芯片（立项依据/研究内容/研究方案/整体一致性/参考文献）。
  - 新增 `/api/lifecycle/focus` 调用，高亮当前微调度器聚焦课题并显示下一 pending job。
  - 课题详情弹窗展示 5 模块进度、checkpoints、monitor 告警，不再依赖旧的 pipeline.js 面板。
- **对话式审核页面修复** — `web/index.html` / `web/js/session.js` / `web/js/slash_commands.js`
  - 审核操作栏（通过/退回/暂停/整理意见）集中到 `review-page`，移除 `chat-sidebar` 内重复 id，避免 DOM 冲突和按钮失效。
  - `session.js` 中旧审核按钮绑定逻辑清理，仅保留 review 会话状态；DOM 渲染由 `lifecycle.js` 接管。
  - `/proposal` 和 `/review` 快捷命令改为调用 `lcViewDetail` / `lcReview`，不再打开已废弃的 pipeline 面板。
- **仪表盘修复** — `web/js/dashboard.js`
  - 修复待办任务/任务预览仍指向已移除 `hermes` 视图的问题，统一跳转到控制台。
  - 新增当前聚焦卡片和周末任务状态卡片。
- **后端路由修复** — `scripts/web_routes_system.py`
  - `GET /api/lifecycle/focus` 改为从 `lifecycle.controller.LifecycleCronController` 调用 `get_current_focus()`，修复 `MicroScheduler` 类不存在的 500 错误。

### 验证结果
- `python3 -m py_compile scripts/*.py scripts/lifecycle/*.py scripts/web_routes_*.py` 通过。
- `node --check web/js/*.js` 全通过。
- `python3 scripts/self_test.py --web-ci` 252/252 通过。
- `python3 scripts/web_server.py --self-check` 通过。
- `LifecycleCronController.get_current_focus()` 手动调用返回当前聚焦：`general-quantum-geometry-inversion-20260726`，时段 18:30-22:30。

### 设计原则
- **结构先于文采**：先把申请书模块固定化，writer 必须补齐缺失内容，critic 将"内容缺失"作为重要评分维度。
- **一轮完整闭环**：同一时段内聚焦同一 proposal，确保一天能完成一整轮优化（章节评审 → 整体评审 → 参考文献 → monitor）。
- **周末不做对抗优化**：工作日跑对抗循环，周末做输入发现、输出萃取、链路反思与 KB 健康维护。

---

---

> 历史归档：v6.7.x 及更早版本的完整变更记录已移至 [docs/archive/CHANGELOG-archive-v6.0-v6.7.md](docs/archive/CHANGELOG-archive-v6.0-v6.7.md)（149 个版本条目中的 20 个，2026-08-14 归档）。
