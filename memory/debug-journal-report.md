# CoPilot Debug 经验报告

> 生成时间：2026-08-05T01:29:41Z
> 总条目数：4

## 统计概览

### 按分类

- **bug_fix**: 4

### 按严重程度

- **critical**: 2
- **major**: 2

## 高频模式

- [tag] **health_check** — 出现 4 次 (关联: dj-20260804-001, dj-20260805-002, dj-20260805-003, dj-20260805-004)
- [tag] **micro_scheduler** — 出现 2 次 (关联: dj-20260805-003, dj-20260805-004)
- [cause] **文件** — 出现 3 次 (关联: dj-20260805-002, dj-20260805-003, dj-20260805-004)
- [cause] **py** — 出现 2 次 (关联: dj-20260804-001, dj-20260805-002)
- [cause] **存在** — 出现 2 次 (关联: dj-20260804-001, dj-20260805-004)
- [cause] **json** — 出现 2 次 (关联: dj-20260804-001, dj-20260805-003)
- [cause] **返回** — 出现 2 次 (关联: dj-20260805-002, dj-20260805-003)
- [cause] **健康** — 出现 2 次 (关联: dj-20260805-003, dj-20260805-004)
- [cause] **康检** — 出现 2 次 (关联: dj-20260805-003, dj-20260805-004)
- [cause] **检查** — 出现 2 次 (关联: dj-20260805-003, dj-20260805-004)
- [cause] **轮次** — 出现 2 次 (关联: dj-20260805-003, dj-20260805-004)
- [cause] **完成** — 出现 2 次 (关联: dj-20260805-003, dj-20260805-004)

## 条目详情

### dj-20260805-004: 微调度器轮转逻辑重写（产物+标签双重检查）

- **时间**: 2026-08-05T06:00:00Z
- **分类**: bug_fix
- **严重程度**: major
- **状态**: verified
- **关联提交**: v6.8.3-fix4

**发现过程**：fix3 后微调度器的时段切换仍不够精确——未验证产物实际内容是否完整，仅检查 pipeline_jobs 状态，导致空产物也视为完成。同时连续聚焦缺乏明确的上限约束。

**根因分析**：1) _is_round_complete() 仅检查 pipeline_jobs 全部 done，未验证 5 个 section 文件是否实际存在且非空；2) 时段切换条件不精确，未完成轮次也会因 stuck 逻辑触发切换；3) stuck 处理与 repair/健康检查职责重叠。

**解决方案**：重写 _is_round_complete() 增加产物+标签双重检查：pipeline_jobs 全部 done + 5 个 section 文件存在且非空（>50B）。时段切换的唯一条件为当前轮双重检查通过，未完成则继续聚焦（无连续时段上限）。stuck 不再触发时段切换，交由 repair（每6h重置 failed job）和健康检查（每1h告警）负责。

**变更文件**：scripts/lifecycle/micro_scheduler.py

**验证方法**：self_test.py --module 220/220 通过

**经验教训**：状态判断必须基于可观测的产物完整性（文件存在+非空），不能仅依赖内部状态标志。职责分离原则：stuck 检测与时段切换解耦，各自由最适合的组件负责。

**标签**：health_check, micro_scheduler, rotation, round_complete, product_check

**关联条目**：dj-20260805-003

### dj-20260805-003: 健康检查增强 + 微调度器轮转修复 + 知识库批量修复

- **时间**: 2026-08-05T04:00:00Z
- **分类**: bug_fix
- **严重程度**: major
- **状态**: verified
- **关联提交**: v6.8.3-fix3

**发现过程**：lifecycle_monitor.py 的健康检查仅检测 2 个 cron 前缀且未检查执行新鲜度；micro_scheduler.py 完成一轮后立即开始下一轮导致霸占时段；executor.py 的 gap_identify 在 researcher 返回非 JSON 时报错；knowledge 目录存在重复论文和错误标记。

**根因分析**：1) 健康检查 cron 检测覆盖不足（仅 2 个前缀，无新鲜度检测）；2) 微调度器缺乏连续聚焦上限和轮次完成判断；3) gap_identify 对非 JSON 返回值无容错；4) 知识库数据在多次迭代中积累了重复文件和错误标记。

**解决方案**：lifecycle_monitor.py 扩展到 4+1 个 cron 前缀检测，新增执行新鲜度（2h）和全链路零进展（3h）告警，cron 缺失自动修复，failed job 立即告警，同类 step 连续失败检测扩展到所有 step，系统性错误检测（429/权限）；micro_scheduler.py 新增 _count_consecutive_slots 限制连续聚焦 2 时段，修复轮次完成判断；executor.py gap_identify 增加空 gaps 兜底文件；知识库通过 kb_health_repair.py 和 kb_fill_wiki_notes.py 修复重复/标记/缺失。

**变更文件**：scripts/lifecycle_monitor.py, scripts/lifecycle/micro_scheduler.py, scripts/lifecycle/executor.py, scripts/kb_health_repair.py, scripts/kb_fill_wiki_notes.py

**验证方法**：self_test.py --module 220/220 通过

**经验教训**：健康检查的覆盖范围需要随 cron 数量和告警维度同步扩展。微调度器的轮转策略需要明确的边界条件（连续上限、完成判断、卡住处理分工）。

**标签**：health_check, cron, micro_scheduler, knowledge_base, gap_identify, executor

**关联条目**：dj-20260804-001, dj-20260805-002

### dj-20260805-002: ProposalSections 路径错误导致 full_review 读不到申请书

- **时间**: 2026-08-05T02:00:00Z
- **分类**: bug_fix
- **严重程度**: critical
- **状态**: verified
- **关联提交**: v6.8.3-fix2

**发现过程**：任一 proposal 完成三章节评审后进入 full_review 步骤时触发。critic 的 files_to_read 列表为空，评审 agent 收不到任何申请书内容文件路径，在无内容基础上产出空泛评审。writer 的 section_files 列表同样为空。

**根因分析**：optimize.py 的 _run_critic（第279行）和 _run_writer（第619行）中 ProposalSections(prop_dir) 误用顶层 proposal 目录。prop_dir 为 {stage}/{proposal_id}，但 ProposalSections 期望传入 04_proposal 子目录。误传导致 sections_dir 指向顶层空的 sections/ 目录（历史残留 0 字节文件），section_exists() 对所有章节返回 False。

**解决方案**：将 ProposalSections(prop_dir) 修正为 ProposalSections(prop_dir / "04_proposal")，传入正确的 04_proposal 子目录。

**变更文件**：scripts/proposal_lifecycle/optimize.py

**验证方法**：python3 -m py_compile scripts/proposal_lifecycle/optimize.py 通过；self_test.py --module 220/220 通过（含新增 5 个章节路径正确性测试）

**经验教训**：路径构造是生命周期代码中最常见的 bug 来源。所有涉及 prop_dir 的调用必须明确是否需要传入子目录（如 04_proposal）。新增针对路径正确性的单元测试可有效防范此类问题。

**标签**：health_check, path_error, full_review, ProposalSections, optimize, proposal_lifecycle

**关联条目**：dj-20260804-001

### dj-20260804-001: 方法名拼写 + JSON解析遗漏导致降级逃生阀崩溃

- **时间**: 2026-08-04T10:00:00Z
- **分类**: bug_fix
- **严重程度**: critical
- **状态**: verified
- **关联提交**: v6.8.3-fix1

**发现过程**：v6.8.3 在 executor.py 新增了 _mark_degradation 方法及调用，但遗漏在 controller.py 绑定。lit_search/gap_identify 的 agent loop 失败降级路径调用 self._mark_degradation 时抛出 AttributeError，降级逃生阀本身崩溃。2026-08-04T01:51:38Z 的 lit_search 失败即为此触发。

**根因分析**：controller.py 补全 _mark_degradation 的导入与类绑定遗漏；executor.py 中 _mark_degradation 和 _run_monitor_step 调用不存在的 _save_proposal_state（正确方法名为 _set_proposal_state）；literature_service.py 中 _try_parse_json 无条件 break 导致 JSON 数组解析器在第一个 [ 处失败后不再尝试后续位置。

**解决方案**：controller.py 补全 _mark_degradation 的导入与类绑定；executor.py 将 _save_proposal_state 修正为 _set_proposal_state；literature_service.py 修复 _try_parse_json 中的无条件 break，允许扫描后续 [ 位置。

**变更文件**：scripts/lifecycle/controller.py, scripts/lifecycle/executor.py, scripts/literature_service.py

**验证方法**：python3 -m py_compile scripts/*.py 全部通过；self_test.py --module 215/215 通过（含新增 2 个降级追溯测试 + 7 个解析器测试）

**经验教训**：新增方法时必须同步检查所有引用该方法的模块（controller.py 绑定、executor.py 调用）。JSON 解析器的 break/return 逻辑需仔细审查，确保不会过早退出扫描循环。

**标签**：health_check, degradation, attribute_error, json_parser, literature_service
