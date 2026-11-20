# 周日深度审计 2026-11-01

## a) 全量回归
见 /tmp/weekly-selftest.log（结果已记录于日报）。

## b) cron 拓扑
实际 31 vs manifest 期望 24：差 7 = 简报域 5 条（清单外）+ paused 3 条仍在册（distill×2、self-optimize 迁移 ZCode）− weekend 动态 worker 不计。无缺失级异常，清单外条目建议下批并入。

## c) 治理减法复核
lifecycle_monitor **缺** cron exit-code 告警与 worklist 零消费告警（grep 双 0）→ 列本周期治理任务（healthcheck 降频前置条件未满足，维持现状）。

## d) 课题侧速览（重大事件）
**全部 8 课题现处 pending_review**：并行引擎会话 10-31 23:54~11-01 04:56 经「引擎亲审/评审团复核」批量晋级（v7.2.0 否决窗口已开启，7 天）。要点：
- 6 课题走引擎亲审通道（key/moire/bsv/order/houston + berry/attosecond 走评审团），晋级理由均为复核通过
- **口径冲突：berry 为 scheduler_frozen 冻结课题（10-31 设定）却被晋级**——冻结语义应先解除或否决窗口对其豁免，需人工裁决
- 主链 optimizing 池清空 → worker 转空转（log 实测 researcher 超时频发），与今日失败率 19.9% 相关
- 未销账全部清零（销账治理生效）

## e) 行动项
1. 【人工·高】8 课题 7 天否决窗口的验收排期建议（可分批：先 ssh-weyl+key）
2. 【人工·中】berry 冻结 vs 晋级冲突裁决
3. 【治理任务】monitor 补 exit-code + worklist 零消费两告警
4. 【已实施】worklist 7 天关闭抑制（v7.2.76，防滞后窗口重提刷屏）
