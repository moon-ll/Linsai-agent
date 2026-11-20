# Skill 架构（v7.0.0 落地 / v7.0.4 as-built 刷新 / v8.0.0 消费方更新）

> 2026-09-25 用户裁决：项目从"prompt 驱动"迁移为"skill 驱动"运转。核心目标：产出高质量课题。
> 人工处理（用户指令/评审团）只作兜底，能力沉淀进 skill 让自动链路自主达到质量。
>
> **v8.0.0 消费方变更（2026-11-16）**：v7 优化环退役后，skill 消费方收敛为——
> ① v8 深研链 `topic_pipeline.deep_research`（B1 注入 literature-reading 节、
> B2/B3 注入 research-proposal 节、B3 注入 method-manual 参数溯源节，经 skill_loader fail-open）；
> ② 知识库链（kb_distill / method-manual 纪律）继续；
> ③ `nsfc-writing` / `quality-review` 标注 legacy（仅供人工项目书场景，hermes agent
> 会话仍可经 trusted 目录加载）。本文件其余章节描述的 v7 消费方（optimize/executor/
> hermes_pipeline/idea_generator/panel_review）已随优化环归档，历史参考。

## 一、现状诊断（侦察结论）

1. **prompt 知识散落**：~1950 行 prompt 相关代码，其中 ~45% 是知识型内容（领域方法论/写作规范/评审标准），硬编码在 optimize.py/executor.py/hermes_pipeline.py 的 f-string 里
2. **三处真相源重叠**：写作纪律同时存在于 optimize.py 内嵌 narrative_rules、skills/nsfc-writing/SKILL.md、nsfc-standards.json 的 writing_style_rules
3. **两套 skill 系统平行**：CoPilot skills/（关键词匹配，仅服务会话链路）与 hermes 原生 skill 系统（~/.hermes/profiles/*/skills/，100+ 内置技能，agent 启动自动注入 index）
4. **欠账**：idea_generator 自称注入"research-proposal 技能"但 skills/ 无此目录
5. **方案可操作性缺口**（用户直接反馈）：叙事重构后研究方案依然"读完不知怎么做"——缺少实验学家常识层（装置/序列/数据形式/时间预算）

## 二、目标架构（三层分工）

```
skill 层（单一真相源）      .hermes/skills/<name>/SKILL.md
  领域方法论 + 写作规范 + 评审标准 + 可操作性标准
      ↑ hermes agent 启动自动加载（trusted 目录，零改造）
      ↑ CoPilot 统一加载器按节裁剪注入（核心红线强制生效）
数据层                     memory/nsfc-standards.json
  量化参数（字数/引用区间/评分权重）——skill 引用，不搬家
代码层                     optimize.py / executor.py / ...
  流程编排 + 输出契约（JSON schema/评分块）+ 运行时数据注入
```

**落点**：`LinSai-CoPilot/.hermes/skills/`——hermes 项目本地 trusted 目录（优先级最高），agent 会话自动进 skills index；CoPilot 程序侧同读此目录。旧 `skills/` 会话 skill 不动（向后兼容）。

## 三、skill 清单（本轮 5 个）

| skill | 承接内容 | 来源 |
|---|---|---|
| `nsfc-writing` | 写作纪律全量：叙事主线 + 审计语言映射 + 纯净性红线 + 内容边界 + 质量纪律 + 自检/检查项 | 收敛 optimize.py narrative_rules/narrative_requirement/_purity_rules/质量纪律 + 现有 skills/nsfc-writing |
| `research-proposal` | 课题设想六模块模板 + **方案可操作性标准（操作性五问+六要素模板）** + 管线六阶段方法论 | idea_generator 六模块 + hermes_pipeline STAGE_PROMPTS + 新增可操作性标准 |
| `literature-reading` | 结构化阅读法（五维笔记/五要素/深读五字段三处同构收敛；v7.0.5 增五节方法学整理——方法卡四要素为方案写作沉淀可实施素材） | executor lit_read + kb_distill + weekend deep_digest + methods_settle（素材流） |
| `method-manual` | 方法学手册质量纪律（唯一真相源/禁追加/去重/口径表） | executor update_method_manual |
| `quality-review` | 评审标准知识：critic 四维锚点法 + monitor 串通检测 + idea_review 四维 | optimize critic 块 + monitor.py + idea_review |

## 四、代码改造

1. 新建 `scripts/skill_loader.py`：统一加载器——读 `.hermes/skills/`，按节（## 标题）提取裁剪，静态绑定表（管线步骤→skill），fail-open + 缓存
2. `optimize.py`：删除 narrative_rules/narrative_requirement/_purity_rules/质量纪律硬编码（~170 行），改 skill_loader 加载；评分契约/输出模板/运行时注入留代码
3. `executor.py`：lit_read/idea_review/update_method_manual 三步骤接 skill
4. `hermes_pipeline.py`：STAGE_PROMPTS 改为 research-proposal skill 引用 + 轻量编排壳
5. `idea_generator.py`：六模块模板改读 research-proposal skill

## 五、边界（防范围膨胀）

- 输出契约（JSON schema/评分块格式）留代码——程序解析接口
- 运行时数据（AI 检测逐词清单/P0 记忆/预算报告）留代码注入通道
- weekend_pipeline 的 `_llm_json` 通道（无文件读取能力）：本轮只收敛知识内容进 skill，注入通道下轮改造
- 旧 `skills/` 会话技能与 skill_manager 机制不动
- nsfc-standards.json 只保留量化参数，文字规范逐步迁走（本轮迁写作规范条目）

## 六、验收标准（v7.0.4 as-built 复核）

- [x] 5 个 SKILL.md 落位 `.hermes/skills/`，hermes agent 会话可自动发现
- [x] optimize/executor/hermes_pipeline/idea_generator 的知识型 prompt 改为 skill 加载，行为等价（回归测试全绿）
- [x] 三处写作纪律真相源收敛为一处——**v7.0.4 完成**：nsfc-standards.json
  `writing_style_rules` 收缩为指针 + anti_ai_patterns 量化阈值（文字规范
  唯一真相源 = nsfc-writing skill 二/四/八节）；optimize 内联重复块删除
- [x] research-proposal skill 含可操作性标准，writer 写方案时强制过"操作性五问"
- [x] 全量回归测试通过 + 新增 skill 加载测试
- [x] CHANGELOG + VERSION v7.0.0 + git 提交

## 八、v7.0.4 一致性审计修复（as-built 补记）

架构一致性审计（2026-09-26）发现并修复：

1. **绑定表归位**：阶段→skill 静态绑定表从 `hermes_pipeline.STAGE_SKILLS`
   迁至 `skill_loader.PIPELINE_STAGE_SKILLS`（本文档 §四.1 的架构声明
   成立）；hermes_pipeline 经 `get_stage_skills()` 消费。
2. **消费方扩充**（skill 有节无消费方修复）：
   - `adversarial/monitor.py` → quality-review 二/四节（串通检测+评审纪律）
   - `panel_review.py` → researcher/critic 角色注 quality-review 四+六节、
     critic 另注 nsfc-writing 十节、reviewer 角色注 quality-review
     一+一之二+四+六节、writer 阶段注七节、verify 阶段注一之二+七节
     （v7.2.77-79：role_brief/修改纪律/判定格式沉淀至 skill 六/七节，
     脚本只留流程编排；评审团与常规链路共用真相源）
   - `kb_distill.py` → literature-reading 二/四节（五要素蒸馏标准；skill
     二节措辞已与 kb_distill 实际契约对齐——审计发现收编时五要素名称走样）
3. **真相源收敛**：nsfc-standards.json `writing_style_rules` 文字条目
   （core/must/forbidden）删除，改 `_source` 指针指向 skill；anti_ai_patterns
   量化阈值保留（程序化指读）。optimize 三处指读行同步改向。
4. **冗余清理**：optimize.py 叙述式首句/references·full_review 旧全量
   规则/内容边界红线三处内联删除（skill 六节为唯一来源）；休眠的
   docs/prompts/（4 个无代码引用 txt）归档至 docs/archive/prompts/。
5. **观测补口**：/api/skills 列表附管线 5 skill 只读条目（type=pipeline）。
6. **已知边界（保留）**：weekend_pipeline `_llm_json` 通道的六模块指令
   仍内联（§五既有豁免，下轮改造）；method-manual 二/三节（判据口径/
   参数溯源）无代码注入，靠 agent 会话自读（可接受）。

## 七、执行顺序

1. 建 `.hermes/skills/` 目录 + 5 个 SKILL.md（内容核心，含新增可操作性标准）
2. `scripts/skill_loader.py` 统一加载器
3. optimize.py 改造（最重）→ executor.py → hermes_pipeline.py + idea_generator.py
4. 测试（skill 加载测试 + 全量回归）→ 文档 → 提交

---

## 九、v7.3.x 手册就绪度扩展（as-built 补记 2026-11-03）

**v7.3.0（用户裁决 2026-11-02）**：方法手册从轮末 derived 维护步升级为第六评审模块（method_manual）。skill 层落点：

- `method-manual` SKILL.md v1.1.0 新增"四、手册就绪度标准"——八要素清单（覆盖度/原理/参数可复算/实施协议/数据判据/失效模式/资源估算/溯源闭环）+ L0-L4 分级（L3=协议可执行=开工门槛）+ manual_2d 评分契约（readiness/rigor 两维）。**该节是手册评审的单一真相源**：critic 步经 `inject_block("method-manual", ["四、手册就绪度标准"])` 注入。
- `quality-review` SKILL.md 新增"九、方法手册就绪度评审"——锚点纪律沿用一之二（先数档再打分、L4=0.90+ 锚）、口径声明（2 维、语体锚点不适用）、验收预判第 5 步（手册未过线为不可豁免项）。
- `skill_loader.PIPELINE_STAGE_SKILLS` 不变（手册 critic/writer 在管线 stage 4/5 内经 inject_block 按节注入，无新 stage）。
- 消费方（v7.3.0 起）：`lifecycle/executor.py` 手册 critic 步（"四、手册就绪度标准"）与两阶段 writer（"一、更新纪律"+"四、手册就绪度标准"）；derived legacy 步保持"一、更新纪律"。
- v7.3.3/7.3.4 工程加固：退回跨遍清理（quality_warning/负反馈/monitor 边界）、KB wikilink 守卫双脱节修复（扫描集含手册）、手册两阶段超时分级（compress/merge 480s）。
