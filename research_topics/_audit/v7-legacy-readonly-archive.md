# v7 legacy 域只读归档声明（worklist-and-prompt 任务 8 · 规则 C · 2026-11-19）

**执行依据**：worklist-and-prompt.md 第三节规则 C——"18 个 v7 课题、337 pending、
2 个 45h+ stale running。整体标只读 + 归档，不再修，也不继续消耗调度资源。"

## 归档范围与处置

- **归档对象**：`research_proposals/` 整域（v7 全流程优化环产物域）。
  - 18 个 v7 课题目录（drafts/optimizing/pending_review/archived 四段台账，见
    `research_proposals/_lifecycle.json` 与 `README-v7-LEGACY.md`）；
  - 台账内 337 个 pending job 与 2 个 45 小时以上 stale running 记录**随域冻结，
    不再清理、不再重跑**（调度资源零消耗——其宿主 cron 已于 2026-11-16
    v8.0.0 迁移时停用，审计见 `memory/v8-cron-teardown.json`）。
- **只读方式**：物理文件零改动（执行约束「不碰 research_proposals/ 下任何文件」
  逐字遵守）。本声明即只读标记：任何后续会话不得向该域写入；git 工作区中
  该域的历史未提交改动（约 20 处 kb-methods-pack.md 等）**保持原样随域冻结，
  不提交、不回滚**（改动属 v7 尾期产物，保留原貌供追溯）。
- **v8 主链**：交付主链为 `research_topics/`（v8.0.0 迁移，2026-11-17）；
  v7 域不再产出交付物，仅供审计与回滚线索。

## vortex 矛盾点原文（按规则 C 保留，供日后追溯）

> 记录原文（`memory/criteria-calibration.json` 判据校准样本 #1，2026-11-16T00:12:23Z）：
>
> ```json
> {"at": "2026-11-16T00:12:23Z", "proposal_id": "general-vortex-oam-hhg-20261101",
>  "dossier_verdict": "attention", "user_decision": "approve"}
> ```
>
> 即：vortex 课题（涡旋光束 OAM 驱动固体 HHG）的评审预判为 `attention`
> （dossier 判据口径 can_adopt=false），但以人工 approve 归档。两者口径不同、
> 均为真实记录；矛盾点不引用即不补说明，随 legacy 一起归档。

## 关联审计

- cron 停用：`memory/v8-cron-teardown.json`（2026-11-16，v8.0.0 架构迁移）
- 迁移记录：`research_topics/_audit/v8-migration-report.json`
- 事件卫生：2026-11-19 批量 ack 16 条陈旧 cron incident（9–10 月记录，
  备份 `tmp/worklist-exec-backup/executions.db.bak-before-ack`）；
  4 条当前故障（Token Plan 429 ×3、monitor exit-1 ×1）保留不 ack。
