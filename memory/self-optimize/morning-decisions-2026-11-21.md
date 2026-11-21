# 晨间裁决单 2026-11-21（供你一站式处理两项待决事项）

> 由 48h 主动推进期整点轮整理（零 LLM，机械汇总 + 实测数据）；自动化不代做任何裁决。

---

## 裁决 1：ready 区 16 个启动包（法定人工节点）

**一句话**：16 包六项判据 11-20 复跑全过、A2 相似度 ≤0.19、bib 溯源 100%、120 对跨包相似全 <0.30（方向分散无簇，逐一裁决互不影响）。

**一页速览**：`research_topics/_audit/decision-brief-2026-11-19.md`（逐包指标表）

**建议审阅顺序**（按主题机械聚类，仅提速用）：

| 簇 | 包 | 指标亮点 |
|----|----|---------|
| 固体 HHG 机制分解 | houston-kronig-penney / bsv-driven-hhg-quantum / ssh-weyl / order-parameter-ultrafast-readout | bib 62/40/40/45 全溯源；A2 0.19/0.19/0.19/0.11 |
| HHG 调控工程 | chiral-hhg / phonon-hhg / moire-strong-field-probe / floquet-20261107 | A2 0.11/0.15/0.19/0.14 |
| TMD 超表面 | tmd-bic-mie-anapole | A2 0.14、bib 47 |
| 非线性输运/拓扑 | berry-berry / berry-mnps3-rashba | A2 0.15/0.15、bib 39/47 |
| 超快表征/动力学 | attosecond-streaking / t-tise2-2-2-2-cdw / key:transient-quantum-phase-optical | attosecond 笔记 22 篇最厚；key 簇 A2 0.09 全场最低 |
| 计算方法 | tdse-tddft | A2 0.12、bib 10 |
| 强场发射/纳米 | keldysh-schottky | A2 0.14、bib 5（最薄，注意） |

**操作**：
- 启动：`python3 scripts/topic_pipeline.py --activate <id>`
- 否决：`python3 scripts/topic_pipeline.py --reject <id> --reason "..."`
- 或看板点击（http://127.0.0.1:8080）

---

## 裁决 2：main 历史同步（四选一）

**现状**：本地领先 494 commits。2026-06-17 起 881 个未推送 commit 中 **400 个已分块推上**；剩余 484 个被 **4.2GB 遗留 PDF**（v7.0.2 裁决前入库的 knowledge/raw/pdfs）阻断——GitHub 端 main 更新被拒/挂死。

**恢复点已兜底**：`origin/snapshot-latest` 已实测**位级无损可恢复**（树 SHA 一致，16 ready 包俱在）——无论选哪个方案，数据零风险。

| 方案 | 说明 | 代价/收益 |
|------|------|----------|
| **① 区间重写（推荐）** | `git filter-repo --refs origin/main..main --invert-paths --path knowledge/raw/pdfs/`：只改未推 484 个 commit 的 SHA，**已推 400 个前缀不变**，随后正常快进推送 | SHA 变更限未推区间（远程已推部分不受影响）；重写前 snapshot+备份双兜底；~分钟级 |
| ② LFS 迁移 | 4.2GB PDF 转 LFS | 需 LFS 配额（另有成本）；历史同样重写 |
| ③ 仅保留快照 | main 放弃远程历史同步，恢复点用 snapshot 分支 | 零操作；丢 5 个月远程历史粒度（恢复点仍是最新全量状态） |
| ④ 远程重建 | 删 GitHub 仓库重建 + 干净树首推 | 等效①但丢失远程全部历史（含已推 400） |

**操作**：回复方案编号即可；①的话我会在重写前再打一次全量备份 + 快照，重写后跑全量测试再推送。

---

## 48h 窗口状态（2026-11-21 07:00）

- 双节奏 automation 运转正常（整点巡检 + 半点数据优化，至 11-22 23:33 自停）
- 全系统健康 ✓：无新增 incident（v8.0.46 修复后冻结首验通过）、蒸馏积压 46、成功率 100%
- 今日待核验：09:30 周末链主发射（n1/n2 夜腿已备 3 候选）、13:00 备份首含 research_topics
