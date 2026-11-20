# 同类项目对标分析（2026-11-07，用户目标：吸收 GitHub 同类优点，四方向升级）

> 调研对象：AI Scientist v2（SakanaAI）/ Agent Laboratory（AMD Schmidgall）/ ChatEval + MAD 辩论评审 / SICA 自进化编码 agent / 科学写作一致性工具（Trinka 类）与长文一致性基准（ConStory 类）。
> 结论先行：本项目已在结构上**独立收敛于 SOTA 的多数机制**（skill 层≈memory/skills 资产、DGM 式三闸≈SICA 评估-修改-重评环、评审团三角色≈多智能体辩论、lifecycle_monitor+step_usage≈agent observability、口径表+AI 检测≈风格一致性工具）。真正缺口是三个**自动发现/度量层**，本轮补第一个（术语扫描器），其余分批。

## 四目标 × 现状 × 对标 × 集成批次

### 1. 自进化智能化
| 项 | 本项目现状 | SOTA 对标 | 缺口/指标 |
|---|---|---|---|
| 改进闭环 | self_optimizer 四相（摘要/基准门/提案/台账）+ ZCode 治理会话三闸（基准门→试点→台账），DGM 式 | SICA：评估→改自身→重评的**变体谱系**（每次变体带评测分） | 试点变体的**分级记分卡**（before/after 指标+谱系）尚无——台账只有 done/未 done |
| prompt 自进化 | prompt_optimizer 因 SOUL.md 污染事故停用（v6.9.68），改由 ZCode 会话受控实施 | DSPy 式自动 prompt 优化 | 保持停用；以 ZCode 治理会话+试点闸替代（有意为之） |
| **批次 B（待做）** | — | — | self_optimizer 试点记分卡：每试点记录 base/variant 指标对 + parent 谱系，晋升决策量化 |

### 2. 评审-修改对抗智能化及效率
| 项 | 本项目现状 | SOTA 对标 | 缺口/指标 |
|---|---|---|---|
| 评审结构 | 四维锚点+rigor 五项清单（v7.2.17）+锚点校准纪律+评审团三角色互不锚定 | AI Scientist v2 Automated Reviewer：**69% balanced accuracy vs 人类评审**；ChatEval 多agent辩论 | 校准账本已有（一致率健康线 0.70，事件驱动 v7.3.54）但**样本量 0/5**——需验收事件回流 |
| 对抗效率 | writer→critic 全轮（26 job/轮）+panel 核销制 | MAD 实证：辩论收益依赖角色设计/结构/成本（Meta-Review 批判） | 争议点**辩驳-仲裁**子流程（对 contested 子集单点仲裁，免全轮重评）——批次 C |
| **本轮已做** | panel 任务包并入术语扫描靶子（terminology_scanner 零 LLM 发现层） | — | 评审靶子从"台账+人工"扩到"台账+程序化扫描" |

### 3. 监管智能及效率
| 项 | 本项目现状 | SOTA 对标 | 缺口/指标 |
|---|---|---|---|
| 可观测性 | step_usage JSONL 月分片（provider/模型/时延/成败）+lifecycle_monitor 每小时+circuit breaker+failure_analyzer 8 模式 | Langfuse/LangSmith 类 trace 平台：按 stage 聚合、SLO、回归告警 | **阶段级周报与回归检测**（per-step 失败率/时延 WoW delta 自动比对）——批次 D（retrospective 已有雏形，补 stage 维度+自动比对） |
| 告警治理 | monitor 告警去重缓存+人类队列+催办分桶 | — | 已达标 |
| 校准 | 判据校准账本（预审 vs 用户裁决一致率） | AI Scientist reviewer-human agreement | 同目标 2，验收事件回流后出首个一致率读数 |

### 4. 撰写质量及风格稳定性
| 项 | 本项目现状 | SOTA 对标 | 缺口/指标 |
|---|---|---|---|
| 数值/表述一致性 | params_registry 口径表（canonical+stale_patterns，数值+机制表述 v7.2.19） | Trinka 类术语一致性检查器 | 口径表需**人工播种**，无自动发现 |
| 风格红线 | AI 模式检测 ceiling（程序化）+超长句罚分+自引用阈值+人工反馈回注 | LLM-ism 词典类风格指纹研究 | 已达标（ceiling=1.00 实测） |
| **本轮已做（批次 A）** | **terminology_scanner 上线**：CJK 变体对（滑窗+LCS+同前后缀+词缀停用+子串坍缩）与记号变体组（三形态归一同键+δ 分组+大小写敏感），phonon 实战命中交接单实证的"零泵浦产额记号四形"；panel 任务包并入 | 长文一致性基准的自动发现思路 | 指标：交接单类残留（8/20 条）从"多轮漏检"变为"每轮自动出现在评审靶子" |

## 集成批次总表

| 批次 | 内容 | 目标 | 状态 |
|---|---|---|---|
| A | terminology_scanner + panel 任务包接线（v7.3.58） | 目标 4 + 目标 2 靶子扩展 | ✅ 本轮 |
| B | self_optimizer 试点变体记分卡（base/variant 指标对 + 谱系） | 目标 1 | ✅ v7.3.59：pilot_scorecard.py（open/close/report + 默认父链=同源最近 adopted、失败变体不入父链、方向感知 verdict_hint），promote_pilot 自动开卡回写 ledger、phase_ledger 基准门红回滚同步关卡 reverted |
| C | 评审团争议点辩驳-仲裁子流程（contested 子集单点仲裁） | 目标 2 效率 | ✅ v7.3.60：skill 七节契约 + --rebuttal-scaffold/--arbitrate（裁决落账撤销清账/保持 open 附注）+ 效率纪律（辩驳率 >50% 转校准账本） |
| D | 阶段级周报：per-step 失败率/时延 WoW 回归检测入 monitor/retrospective | 目标 3 | ✅ v7.3.61：stage_weekly_report.py（R1 失败率 ≥+5pp / R2 p50 ≥+50%，噪声地板）+ run_retrospective 尾节 fail-open 接线 |
| — | 校准账本样本回流（review-verdict/adopt 已接 v7.3.54，攒 5 样本出首个一致率） | 目标 2/3 | 自然积累 |

## 边界声明
- 对标数据来源为公开论文/仓库描述（AI Scientist v2 评审准确率 ~69% balanced accuracy 为其自报口径），不做逐指标横向复现。
- 集成遵守项目纪律：零第三方依赖、skill 契约不改、LLM 直改正文不走旁路、版本号领取协议。
