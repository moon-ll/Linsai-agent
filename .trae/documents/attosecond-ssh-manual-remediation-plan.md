# 状态冲突 + A 通道校准审计 + 两册手册补齐（执行计划）

> 本文含三项：① 状态冲突事实链与回退方案（待批，不执行）；② A 通道可达性审计结论与候选改法（待批，不改 rubric）；③ attosecond / ssh-weyl 手册补齐执行计划（批准后执行）。
> 已完成且只读：三项事实核查、295 条历史评分记录统计、两册 critic 报告与 update-plan 通读。

## 一、状态冲突事实链（只读核查结论）

### 1. 当前状态

| 草案 | 当前 status | 当前目录 | `activation_decision` |
|---|---|---|---|
| chiral-hhg | optimizing | `research_proposals/optimizing/general-chiral-hhg-20261101` | `hold`，decided_at 2026-11-03T15:51:09Z |
| phonon-hhg | optimizing | `research_proposals/optimizing/general-phonon-hhg-20261101` | `hold`，同上 |
| vortex-oam-hhg | optimizing | `research_proposals/optimizing/general-vortex-oam-hhg-20261101` | `hold`，同上 |

三者 `activation_decision` 均**未被清除或改写**，仍带重评门：`all_required=true`、`recheck_after=2026-11-09T00:00:00Z`、两条 conditions 均为 `pending`——① 11-07/08 周末反思链 v7.2.107 per-job 重置验证通过；② 至少 2 个课题 last_score≥0.85 且 P0 未闭环=0。

### 2. 激活链（北京时间，UTC 加 8 小时）

| 时间 | 事件 | 证据 |
|---|---|---|
| 11-03 23:51 | 三草案统一 hold 写回 | `activation_decision.decided_at=2026-11-03T15:51:09Z`；CHANGELOG v7.3.10；`human_queue` 当时 3 条 `activate_hold` |
| 11-04 21:22:16 | phonon `drafts→optimizing` | transition_history；`_lifecycle.json.bak-20261104-adopt-settle` 已为 optimizing |
| 11-04 21:22:17 | chiral `drafts→optimizing` | 同上；理由称“用户裁决按 ZCode 尽调建议（2026-11-03）” |
| 11-04 22:00:19 | vortex `drafts→optimizing` | transition_history；理由称“用户裁决 2026-11-04「激活」，设备条件确认放行” |

时间戳均与备份序列吻合（11-03 23:50 快照尚未写 hold，23:51 写入；11-04 21:22 快照已见 chiral/phonon 激活；11-04 22:00 快照 vortex 仍 drafts，22:20 快照转 optimizing）。**不存在回填时间戳或跨会话丢写。**

入口：走 `proposal_lifecycle.transition(pid, "optimizing", reason=...)`（[transitions.py#L25-L70](file:///Users/ll/Desktop/LinSai-CoPilot/scripts/proposal_lifecycle/transitions.py#L25-L70)）。该函数**只做目录移动 + 状态写入，不读取 `activation_decision`，无重评门校验、无 force 参数**，所以任何人工/并行会话调用都能直接激活。

### 3. 是否绕过重评门：是（机械口径）

- 条件①：要求 11-07/08 的反思链结果。激活发生在 11-04，**物理上不可能满足**，当前仍 pending。
- 条件②：11-03 hold 快照下满足“last_score≥0.85 且 P0=0”的 optimizing 课题数 = **0**（order 0.875 但 P0=1）；当前 = **1**（order 0.875、P0=0），仍 <2。**不满足**。
- 因此三条激活在重评门意义上均为绕过。chiral/phonon 的理由引用的是 11-03 的“尽调建议”，而 hold 裁决也在 11-03 23:51，时间上更晚或同源，记录未说明谁覆盖谁；vortex 有明确的 11-04 用户“激活”指令，属显式覆盖，但 `activation_decision` 仍未更新，审计链自相矛盾。
- 队列侧后果：`human_queue.py` 只对 `status=drafts` 生成 `activate_hold`；激活后队列只剩 2 条 `outline_review`，hold 事项在界面上消失（持久源 `memory/human-queue.json` 已核实）。

### 4. 回退方案（供批，不执行）

推荐（状态可审计、不丢产物）：

1. 冻结：确认三课题无在跑 pipeline job（`memory/pipeline-jobs.json` 按 proposal_id 过滤）；若有，等其结束或由 `--repair` 清理，不做强杀。
2. 备份：`_lifecycle.json` + 三个 proposal 目录全量快照到 `memory/backups/`。
3. 逐条回退：`python3 -c "from proposal_lifecycle import ProposalLifecycle as L; L(...).transition('<pid>','drafts',reason='回退至 hold：2026-11-04 激活未满足 recheck_after 2026-11-09 双条件（reflection pending、达标课题 0/2），activation_decision 未更新')"`。
   - 该调用会把目录从 `optimizing/` 移回 `drafts/`，保留全部产物与评审记录。
   - `activation_decision` 保持 `hold` 原样，不清空、不改写。
4. 重算队列：`human_queue.recompute()`，确认出现 3 条 `activate_hold`、`escalate=false`。
5. 只提交状态文件与目录移动；CHANGELOG 记录“回退至 hold + 原因 + 未改 rubric”。
6. vortex 单独裁决：其 11-04 用户指令明确，建议**保留激活**；若也要回退，走同一流程。

配套最小代码改动（P1，建议与回退同批）：

- 在 `transition()` 入口增加守卫：`to_stage=="optimizing"` 且 `activation_decision.decision=="hold"` 时，检查 `recheck_after` 是否已过、两条 conditions 是否均 `done`；未满足则拒绝并返回 `{"success": False, "error": "重评门未满足"}`，除非显式传 `force=True`（CLI 仅提供 `--force-hold`，要求 reason 含用户授权原文）。
- 新增 `scripts/tests/test_activation_hold_gate.py`：hold+pending 拒绝、hold+双条件达成放行、force 放行三条用例。
- 影响面：仅 `transitions.py` + 1 测试文件；不改 rubric、不改阈值。

## 二、A 通道校准审计（只读，未改 rubric/阈值）

### 1. 历史最高分（`_lifecycle.json` 全部 score_history 与 archive，595 条 section_4d 记录）

| 模块 | 历史最高 | 课题 / 轮次 | 口径 |
|---|---|---|---|
| rationale | 0.88 | attosecond r1（2026-11-02） | section_4d |
| content | 0.86 | quantum-geometry r1 | section_4d |
| scheme | 0.85 | quantum-geometry r1 | section_4d |
| full_review | 0.86 | quantum-geometry r7 | section_4d |
| references | 0.95 | ssh-weyl r7 | references_2d |
| method_manual | 0.82（入账）/ 0.91（报告） | houston r5 / order r3 | manual_2d |

结论：**5 个模块中只有 references 曾越过 0.90**；4 维模块历史最高 0.85–0.88，约 2 个月、595 条记录无一次 ≥0.90。

### 2. 结构性上限证据（rubric 原文）

- `memory/nsfc-standards.json → general_principles.scoring_rubric`：
  - 权重：创新性 0.30 / 可行性 0.25 / 严谨性 0.25 / 表达质量 0.20。
  - 表达质量：0.90–1.00 档要求“无 AI 痕迹、无模板句式、无空泛修饰”，并注明**受程序化天花板约束**。
  - 严谨性：0.90–1.00 档要求五项核查全过（数值链/指标定义/文献支撑/逻辑闭环/模块自洽），4 项只给 0.80+。
- `scripts/proposal_lifecycle/optimize.py`：
  - `expression_quality_ceiling` 由代码计数产出 0.5–1.0，critic 表达分不得超过该值；
  - 综合分再套 `overall_ceiling`：天花板 <0.9 → 综合 ≤0.85；<0.8 → ≤0.80；<0.7 → ≤0.75。
  - 595 条记录中 **39.7% 的天花板 <0.9**，即这些轮次综合分被硬压到 ≤0.85，无论内容多好。
- 加权结构：综合 = .30×创新 + .25×可行 + .25×严谨 + .20×表达。要到 0.90，四维需普遍 ~0.90；表达分被程序化天花板压制时，0.90 在结构上不可达。

### 3. 结论

**② 口径导致实质不可达**（非 ① 内容问题、非 ③ 加权/取整 bug）：权重和为 1、取整无异常；瓶颈是“表达质量程序化天花板 + overall_ceiling 0.85 硬闸 + 四维同时 0.90 的加权结构”。references 之所以能到 0.95，是因为走 `references_2d` 双维口径、不过表达天花板。

### 4. 候选改法（供批，三选一或组合；均不改当前 rubric 数值）

| 方案 | 规则 | 当前解锁数 | 影响 |
|---|---|---|---|
| C1 | A = 5 模块 ≥0.85 且无 critical/high | 0（order 最低 scheme .80；key 最低 full .77） | 与 general 质量阈值 0.85 对齐；仍要求五模块齐升，历史上无课题一次满足 |
| C2 | A = 3 核心模块（rationale/content/scheme）≥0.90，其余 ≥0.85 | 0 | 更严；核心三章恰是 4 维口径、受表达天花板约束，等于把最难的三个模块抬到 0.90 |
| C3 | A = 分位校准：各模块 ≥该模块历史 P75（rationale .83 / content .82 / scheme .80 / full .80 / refs .84）+ 综合 ≥0.85 + 无 critical/high | **1（order）** | 消除绝对 0.90 的结构性偏差；随全库进步自动抬线；需定义 P75 的滚动窗口与重算频率 |

补充：若保留 0.90，建议只对 `references_2d` 保留 0.90，4 维模块改用 0.86（历史 P90 附近）；或把 A 改为“综合 ≥0.87 且无模块 <0.80”，避免单模块绝对线。

## 三、两册手册补齐（批准后执行）

### 基线

| 册 | 字符 | 字节 | 行 | wikilink | 表格行 | [n] | 风险/失效 | 判据 |
|---|---|---|---|---|---|---|---|---|
| attosecond | 53,076 | 105,115 | 1002 | 11 | 195 | 31 | 125 | 101 |
| ssh-weyl | 63,047 | 106,377 | 990 | 16 | 201 | 135 | 73 | 95 |

### attosecond（17 项：3 critical + 6 high + 5 medium + 3 low）

- critical：伴峰 291.6 eV → Köppe 303/311 eV；Pupeikis“284–531 eV” → 2.2 μm 覆盖水窗；补 FROG/波形控制/阿秒条纹相机 3 个实存 wikilink。
- high：Ar 3s 29.2→29.24 eV；NIST→Verner–Yakovlev；5–10%→三档 <2%/2–5%/≥5%；100→100–140 eV（0.005 rad/eV×200 eV≈1 rad）；Tarrant/Shi/Zhu 引文归位；TDSE 分阶段 CPU·h 落表。
- medium/low：He ~0%→≤5%；CH₄/N₂ 设计估值；Cousin 表述；Blöchl 2.1 μm/6.9 fs；λ₁ L-curve；λ 表注；束线最坏 8–14 周；Pupeikis 2020。
- 体积：补全型，目标 55–57K，≤57K；只表格化/归并重复的场强-γ-周期换算与分档口径。

### ssh-weyl（16 项：2 critical + 6 high + 7 medium + 1 low）

- 先压缩 63,047 → ≤58,000：删 §1.4/§1.6 残留指针并入 §1.3.1；跨节重复几何量/判据合并为单一权威节+指针；版本沿革与过程记录删除；不删判据/阈值/步骤/引文。
- critical：Bi₂Se₃ 家族 HOTI（4 处）→ BHZ 推广 HOTI；I_th=7×10¹¹ W/cm² 越窗 → 通道表扩至 10¹² 并注明引擎失效边界内侧。
- high：Z 指纹改框架内强弱场区；§6.1 五行参数落值+出处；§5.1 Δt/η_SF/δ_FP 与 12 判据三行协议（拟合窗 ≥30 fs）；§8.3 35→50.3 天复算；§7.6.3 虚指删除。
- medium/low：§9 指针、§10 素材包实名、G1 双类协议、β-WP₂ 行、ZnO 通道口径、§7.6.5 核时、4 页采纳/排除登记、R_odd/even 说明。

### 复评与验收

- 新建两册 `05_review/critic-round-2-method_manual.md`：八要素 8/8（⑧“过”）、逐项核销表、分节分数前后（r1 无分节表，注明基线为按缺陷密度归因）、体积构成与信息保留、锚点对比、2 维评分与 L 级。
- 验收：字符 ≤57K/≤58K；禁用模式 grep 归零（attosecond `291.6|284–531|29.2 eV|~0%|5%–10%`；ssh `Bi₂Se₃ 家族|7×10¹¹|约 35 天|§2.6|mdd9b6dcd|Haken–Strobl–Reineker`）；wikilink 实存校验；`py_compile` + `test_version_monotonic`；CHANGELOG 先查最新号再取号；两册各自提交。
- 边界：不改 lifecycle/registration/不写人工队列/不自动 activate；遇锚集或同类守卫失败即记录并跳过。

## 四、执行顺序

1. 你批准回退方案/校准方案/手册方案（可分别批准）。
2. 若批准回退：先冻结+备份+回退 chiral/phonon（vortex 待单独裁决）+ 重算队列 + 守卫代码与测试。
3. 手册：attosecond（先）→ ssh-weyl（后），各自复评、测试、提交。
4. 最终中文汇报：状态事实链 → 校准结论 → 两册结果。
