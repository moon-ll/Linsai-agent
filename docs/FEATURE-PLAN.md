# 开发计划（Feature Plan）

> 记录待开发的功能增强和架构改进，按优先级排序。
> 已完成的功能在 CHANGELOG.md 中记录。

---

## P1 -- 研究设想质量门槛（已完成 v6.8.26）

**状态**：✅ 已实现，2026-08-12 随 v6.8.26 发布

**实现摘要**：
- 新增 `idea_review` job 类型，在 round 1 的 job 链最前端作为所有 critic 的前置依赖
- researcher profile 对 `00_research_idea.md` 做独立评审，分数 ≥ 0.70 才通过
- 未达标时 writer 根据评审意见修改研究设想，重新评审，最多 3 轮
- monitor 步骤新增结构性缺陷检测（content/scheme 文件级重复或模块空置），检测到时设置 `idea_review_required` 标志，下一轮自动退回研究设想评审
- 11 个专项测试全部通过

**背景**：当前链路中，研究设想（`00_research_idea.md`）在进入 optimizing 之前只有一次性初始化生成，之后 writer 虽然在每轮结束时"同步更新"研究设想，但这个更新是被动的、片段式的——writer 修改了申请书某章节后才顺带更新对应部分。没有独立的、前置的"研究设想质量审核"环节。

**问题链**：

```
现状（有缺陷）：
研究设想（一次性生成）→ 申请书初稿 → writer-critic 对抗循环
         ↑ 缺少质量把关                ↑ 在烂地基上反复打磨

理想链路：
研究设想（生成 + 独立审核 + 迭代优化）
         ↓ 达标后
申请书初稿 → writer-critic 对抗循环
```

**实际案例**：key-transient-quantum-phase-optical 课题 8 轮优化无收敛，R8 critic 报告指出 content.md 与 scheme.md 文件级重复、4 模块空置——根因是研究设想阶段对"研究内容 vs 研究方案"的逻辑切分未想清楚，后续优化无法弥补这个结构性缺陷。

**设计方案（草案）**：

1. **研究设想独立评审步骤**：在 `initialize_for_optimization` 之后、第一轮 writer-critic 之前，插入 researcher profile 对 `00_research_idea.md` 的独立评审（聚焦科学问题清晰度、创新点可检验性、研究内容与方案的逻辑切分）
2. **质量门槛**：研究设想评审分数 ≥ 0.70 才允许进入 optimizing（与申请书的达标阈值解耦，可单独配置）
3. **迭代修复**：未达标时，由 writer 根据评审意见修改研究设想，重新评审，最多 3 轮
4. **退回机制**：optimizing 中途发现结构性问题（如 content/scheme 重复、模块空置），可由 monitor 标记"研究设想缺陷"，自动退回研究设想评审步骤（而非直接归档）
5. **同步优化限制**：optimizing 阶段 writer 对 `00_research_idea.md` 的修改仅限于"同步已有内容"，不允许新增科学目标或改变研究方向——方向性变更须退回研究设想阶段

**影响范围**：
- `proposal_lifecycle/initializer.py`：新增研究设想评审步骤
- `proposal_lifecycle/optimize.py`：monitor 增加"研究设想缺陷"检测
- `lifecycle/executor.py`：新增 job 类型 `idea_review`
- `micro_scheduler.py`：处理退回研究设想评审的逻辑
- `completion.py`：达标判定中可选的退回条件

**优先级**：P1（用户已确认纳入计划）
**预估复杂度**：中等（约 200-300 行代码，不含 prompt 调优）
