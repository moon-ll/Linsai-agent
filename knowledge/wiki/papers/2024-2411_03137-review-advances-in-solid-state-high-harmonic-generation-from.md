---
title: "2024-2411_03137-review-advances-in-solid-state-high-harmonic-generation-from"
type: "papers"
created: "2026-09-27T18:50:43Z"
updated: "2026-11-15T15:09:20Z"
tags: []
related: ["key-transient-quantum-phase-optical-20260726", "强关联体系", "强场超快", "强场驱动", "瞬态量子相位", "量子几何"]
source_raw: "2024-2411.03137-review-advances-in-solid-state-high-harmonic-generation-from.md"
growth_stage: "seedling"
confidence: 0.5
digest_level: "fulltext"
---

# From Pen to Prompt: How Creative Writers Integrate AI into their Writing Practice

> ⚠️ **元数据失配提示**：frontmatter 标注本篇为"Review: Advances in solid-state high harmonic generation from Chinese research groups"（arXiv 2411.03137，强场 HHG 综述），但实际提供的全文为 HCI 论文 *"From Pen to Prompt: How Creative Writers Integrate AI into their Writing Practice"*（Guo et al., University of Washington, C&C '25, DOI: 10.1145/3698061.3726910）。两者 arXiv ID 同号但内容完全不同。frontmatter 极可能系抓取/标引串号所致。本笔记按**实际全文内容**蒸馏，不据此虚构 HHG/强场结论；同时建议在文献库中复核此条目的元数据并重新标引。
>
> ⚠️ **全文截断提示**：提供的 PDF 文本在 §4.2.1 中部中断（"...P17 described their trajectory from first using AI as pa"），第 5 节（Discussion）、第 6 节（Limitations/Future Work）等未含入。本笔记仅基于可见文本蒸馏。

---

## 林赛的理解

坦白讲：这篇是 HCI 领域访谈研究，**与本组强场超快/阿秒/HHG/交变磁/莫尔/量子几何方向没有物理接口**。它进入"NSFC-强场超快"项目文献库大概率是元数据串号，不应消耗方法学资产沉淀或课题方案写作的预算。

对课题的潜在间接价值仅在于两点（都很次要）：
1. **元数据治理**——本组知识库存在明显的"arxiv-ID 串号/标题错配"问题，需要在入库流程加一道人工或规则核验（标题 vs arxiv_id vs 摘要三角校验），否则后续 deep-read 会反复踩坑。
2. **作者写作工作流**——若课题组日常用 LLM 辅助论文/基金本子写作，这篇的"价值—关系—策略"框架可作为一个轻量参照（但这是个人写作方法论层面，非物理研究层面）。

**不进入方法卡、不进入方法页融合。**

---

## 研究问题

**RQ1**: What drives creative writers to incorporate AI? When and why do they choose to use AI?（驱动创意写作者使用 AI 的因素是什么？他们何时、因何选择用或不用？）

**RQ2**: What strategies and workflows emerge as writers develop personal practices for writing with AI?（在长期使用中，写作者发展出怎样的策略与工作流来与 AI 协作？）

中心论点：长期使用 AI 的创意写作者并非"被动接受工具"或"简单拒绝"，而是在**价值（values）—关系（relationships）—整合策略（integration strategies）**三要素的动态博弈中，刻意划定 AI 使用边界，发展出既保留自身真实性/ownership/工匠精神，又充分利用 AI 的个性化工作流。

---

## 研究背景

**学术脉络**（论文自述的 Related Work）：
1. **AI 对创意写作社群的冲击**：社会层面对 AI 辅助作品存在偏见（mis-bias）[29, 30]；2022 年 AI 生成艺术品获奖引发真实性和作者权争议 [55]；2023 年美国编剧工会（WGA）罢工限制 AI 使用；自助出版平台涌入 AI 作品 [4, 56]；NaNoWriMo 允许 AI 引发强烈反弹 [63]；Have I Been Trained [60] 等工具揭示数据训练未授权问题。
2. **计算支持创意写作的历史脉络**：从规则系统 [16, 31] 到聊天机器人，覆盖 ideation [27, 57, 61]、改写与反馈 [12, 68] 等环节；商业平台如 Sudowrite [1]、Novelcrafter [2] 提供风格一致的文段接续，ChatGPT [3] 等通用聊天平台亦被用于创意写作。
3. **写作者与 AI 交互研究**：现有研究多在受控实验室环境、用自定义 AI 界面、参与者多为 AI 新手 [7, 10, 11, 34, 59]；发现写作者在 8 周使用后开始分化——有人直接采纳 AI 文本，有人仅用于 ideation/改写 [34]；业余爱好者看重个人表达，专业写作者看重产能 [8]。交互范式研究把写作工具从认知辅助到协作者连续谱系定位 [15, 21, 24, 65, 66]；典型挑战包括叙事连贯性 [34, 45]、风格声音 [18, 34]、ownership 与满足感下降 [33, 40]、抄袭担忧 [25]。

**本文的动机**：填补"长期、跨平台、跨体裁、已演化出自有工作流"的创意写作者群体研究空白。论文引用 [41, 46] 指出 AI 工具价值随使用时间增长、超过新奇效应后才能发展出真正个性化用法，因此需要研究**已度过熟悉期**的写作者。

---

## 研究方法

定性 HCI 研究，方法密度对物理课题为低；按 HCI 标准展开。

### 研究设计
- **范式**：质性研究（qualitative），扎根理论（grounded theory）[51] 编码流程
- **数据采集**：半结构化访谈 + 现场写作观察（contextual inquiry）
- **时段**：2023 年 11 月 — 2024 年 7 月
- **执行**：由第一作者完成全部访谈与观察

### 受试者招募
- **样本量**：N = 18 名创意写作者
- **纳入标准**：fiction / creative non-fiction / poetry 写作者，自我认同即可，无出版/学历硬性要求；具备 AI 写作工具经验（持续使用 ≥ 1 个月或已有完成作品）
- **招募渠道**：AI 主题在线论坛与社区、大学写作/MFA 邮件列表、雪球抽样
- **筛选工具**：筛选问卷（写作背景 + AI 经验）
- **体裁分布**：fiction 最具代表性

### 受试者构成（Table 1，N=18，原文保留）

| 维度 | 分布 |
|---|---|
| 体裁 | fiction（多以小说为主，含短篇、Fanfiction、experimental）、poetry、personal essays、lyrics |
| 发表背景 | Yes（已发表）/ Self Published / Personal Blog / Literary Magazines / N/A 或 Shared Online |
| 写作年限 | 3 年 ~ > 10 年（多数 ≥ 10 年或 4–5 年） |
| AI 使用年限 | 5 个月 ~ ~2.5 年（多数 1–2.5 年） |
| AI 工具栈 | ChatGPT、Claude、Sudowrite、Novelcrafter、NovelAI、Perplexity、Write With LAIKA、Pi、Midjourney、Runway、Marlowe、Bard、Gemini、Copilot、Rexy；P5 使用经 Obsidian 插件 Loomsidian 调用的 code-davinci-002 / davinci-002 |
| 学历 | 9 名无正式写作教育 / 3 名硕士及以上 / 6 名大学或线上写作课 |
| 地域 | 美国 12 / 欧洲 5 / 加拿大 1 / 未披露 1 |
| 性别 | 女 10 / 男 6 / 非二元 1 / 未披露 1 |
| 年龄 | 18–25 至 65+ 跨多档 |

### 访谈流程
- **单次时长**：90 分钟 Zoom 半结构化访谈
- **写作观察段**：约 30 分钟嵌入访谈内（实际 range **29–45 分钟，mean 34.5 分钟**），写作者屏幕共享并在自选 AI 平台上推进真实写作项目（小说章节、诗歌、随笔）
- **观察段降扰措施**（提供三个备选以减少观察者效应）：① 访谈前预录写作过程；② 访谈前写写作日记；③ 现场观察。**实际：17 人采用现场观察、1 人（P5）选择预录**
- **干预原则**：研究者仅在写作者主动 think-aloud 之外的"接受/拒绝建议"等关键动作做 contextual 追问（如 "what made you accept this suggestion?"），其它时间最小干预
- **伦理**：经机构 IRB 审查豁免

### 数据分析
- **编码方法**：开放编码 → 主题聚类；初始编码由第一、三作者开发，第二作者随访谈推进迭代更新
- **多模态编码**：访谈音视频自动转写 + 人工校正 + 屏幕录像中的非言语互动（如 prompting 方式）补充编码
- **迭代机制**：每访谈数场后作者组讨论涌现主题并更新访谈提纲

### 装置/工具（写作观察对象）
- **AI 写作平台**：Sudowrite, Novelcrafter, NovelAI（商业创意专用）；ChatGPT, Claude, Bard, Gemini, Copilot, Pi, Perplexity（通用聊天）；Write With LAIKA, Marlowe, Rexy（创意专用辅助）；Midjourney, Runway（图像/视频辅助）
- **写作辅助环境**：Obsidian + Loomsidian 插件调用 davinci 系列模型（P5）

### 适用边界
- **人群边界**：仅"已主动选择并长期使用 AI"的创意写作者；不覆盖 AI 抗拒者或新手用户
- **工具边界**：观察以**商业创意写作平台与主流聊天 LLM** 为主；不覆盖开源/本地模型深度自定义场景
- **方法边界**：质性访谈——结论可迁移性受样本量与自选偏差限制；观察段受观察者效应影响（已通过备选方案部分缓解）

---

## 主要发现与核心结论

### 框架性结论

写作者与 AI 的互动由**三个相互影响的要素**构成动态系统：
1. **个人价值（values）**
2. **感知关系（relationships with AI）**
3. **具体整合策略（integration strategies）**

三者不是独立存在——例如，强 ownership 价值的写作者倾向于把 AI 看作 assistant/tool，以保留显性控制；该关系又反过来塑造他们发展出更受限、任务专属的工作流（vs. 把 AI 看作 collaborator 的写作者）。

### 核心写作者价值（4 项）
1. **Authenticity**（真实性）：保持独特的声音与表达
2. **Ownership**（所有权）：文本"是我的"，并掌控创作过程
3. **Creativity**（创造力）：以独特方式表达自我
4. **Craftsmanship**（工匠精神）：有意图、有付出、有质量

> 与 Gero et al. [23] 的 intention / authenticity / creativity、Biermann et al. [8] 的 fulfillment / ownership / integrity 等前期分类有重叠，但本文焦点在"这些价值如何塑造使用方式"而非"是否使用"。

### RQ1 回答：何时、因何使用 AI

**使用动机（4 类）：**

| 动机 | 关键机制 | 代表引述 |
|---|---|---|
| AI 重塑"创作瓶颈"的关系 | 把写作障碍从威压性壁垒变为可管理挑战；提供起点降低认知负荷 | P2: "with the AI, you don't have the mental game tripping you up anymore"；P13: "I have a very low standard/expectation for AI's generative responses... I usually can run with that" |
| 生产力提升 + 可达性工具 | 加速 ideation/编辑，缩短反馈循环；对靠写作谋生者（P2, P10, P12, P14）关乎竞争力；对健康受限者关乎能否参与 | P7（腕管炎）：曾考虑雇合著者或代笔，AI 帮助其"can actually write again"；P14（身体障碍）：AI 让"我 suddenly am competitive" |
| 聚焦喜爱的部分，发展技艺 | 战略性地让 AI 减少乏味环节摩擦；hobbyists 把困难环节视为学习机会 | P13: "this is a good learning experience for me too" |
| 新型创作实验 | 在低风险环境下探索新用法；跳出惯常风格/体裁；甚至希望用"更小、更不流畅"模型产生"更怪诞"文本 | P3: "smaller, less fluent models producing random but cooler, wackier text..."；P17: "within a lifetime, you can write more work, write more types of work..." |

**使用谨慎（3 类边界）：**

1. **保持真实声音、讯息与人味**：有清晰个人愿景时更愿直接写不用 AI；反思性/个人写作中"AI can't really dip into"（P13, P17 倾向让 AI 仅承担反馈）
2. **保有 ownership 与控制感**：所有权可落在"初始创意愿景"（P2："That story premise was my idea"）或"编辑控制与解读"（P13："I took that interpretation and made it my own"）；出现"AI 太会模仿自己 → 反而 ownership 下降"现象（P7：估算 30%–35% 内容可归因 AI）；许多写作者自建日志/版本控制记录创作决策（P14："creatives always need to know what the prompt is"）
3. **保留对 craft 的享受**：避免 AI "代劳"；P2："my personal satisfaction is lower when the AI does most of the work"；P10："If you weren't a good writer writing stuff by hand, you're not going to be a good writer with AI"；P6：即便是 AI 辅助，"you get to judge it on the quality... it's a story, but is it a decent story?"

> **修正前期文献 [8]**：先前认为写作者在"不自信"领域更愿与 AI 协作；本研究显示 AI 更常被用于**"不享受但熟练"**或**"乏味"**的环节，而不必然是"不擅长"。

### RQ2 回答：如何整合 AI 进写作流程

**总体机制**：动态关系指导 AI 使用；写作者在关键决策点集成 AI。

**写作者与 AI 的关系谱（按权力动力学从"显性权威"到"机械工具"排列）：**

| 关系比喻 | 权力结构 | 关键特征 | 代表引述 |
|---|---|---|---|
| **Boss / Assistant**（上司—助理） | 写作者全权决策，AI 执行任务 | 输出要高质量，写作流程中写作者随时干预 | P12: "a very good assistant... kind of like a supportive yes man" |
| **Director / Actor**（导演—演员） | 写作者引导 AI 表演特定任务 | AI 输出依愿景被"塑造" | P6: "my role... is kind of like a director, and he is the actor" |
| **Fellow writer / Collaborator**（同行写作者/协作者） | 双向贡献，迭代创作 | 写作者对 AI 创意贡献更开放；含 junior writer、ghostwriter 等子角色 | P16: "bringing its own things to the table" |
| **Editor**（编辑） | 写作者保留创意控制，欢迎反馈 | AI 用于识别强弱项、重组文本、给建议 | P13: 用 AI 模拟"the viewpoint of an editor for a writer before my essay gets published" |
| **Muse**（缪斯） | 灵感激发，非任务执行 | 偶发意外灵感；P16 描述为"interactive muse"——区别于传统被动缪斯 | P10: "a lot of times it'll spark an idea for something else" |
| **Tool**（工具） | 机械辅助，无独立创意 | 视 AI 为 Photoshop/Grammarly 类工具；不愿给予署名 | P1: "it's this tool for me... it doesn't replace what I want to do"；P12: "only responding the way it is based on what I give it" |

**动态性**：写作者与 AI 的关系**在同一写作会话中可切换**（如 P2 在一场 session 中把 AI 同时视为 tool、fellow writer、editor）；关系亦随持续使用而演化；许多写作者承认难以用单一标签描述（P7 的"strange, middle ground"张力；P11："it's my friend, it's my muse, it's my bag of tricks... a tool with a face, or a tool with a soul"）。

---

## 潜在研究方向

来自论文自陈/可推断的局限（原文在截断前未呈现完整 Limitations 节，基于方法与样本推断）：

1. **样本偏差**：N = 18 且全部为"已主动选择长期使用 AI"的写作者；不覆盖 AI 抗拒者或初次使用者；自选偏差使结论偏向"成功整合者"的经验
2. **观察者效应残余**：即便提供预录/日记替代，17/18 写作者仍在观察下写作；think-aloud 进一步改变认知过程
3. **跨文化局限**：样本 12/18 在美国，对中文/非英语创意写作社群的迁移性未验证
4. **工具代际局限**：访谈于 2023-11 至 2024-07，跨越 GPT-4 / Claude 3 / Gemini 1.5 等关键代际跃迁；论文中部分"AI 不擅长叙事连贯性/风格"已被新模型缓解
5. **未截断部分（Discussion / Future Work / Conclusion）缺失**：本笔记无法覆盖作者对 HCI 工具设计、政策建议、未来研究方向的完整论述
6. **方法论对物理课题不适用**：扎根理论访谈对自然科学研究无直接迁移价值

**给后续 HCI 研究的方向（基于论文已暗示的 gap）**：
- 跨平台日志级（log-level）量化研究：现有 log 分析多来自众包参与者 [43, 58]，缺乏对长期写作者跨平台自然使用的纵向定量
- AI 模仿作者风格越像 → ownership 反而下降的反直觉现象（P7）值得用更大样本验证
- "hobbyists 在不擅长领域反而回避 AI"与"pros 在擅长但乏味领域使用 AI"的张力需要更精细的人群分层

---

## 与林赛研究的关联

**直接物理接口：无。** 本篇是 HCI 创意写作访谈研究，与本组核心方向（HHG、阿秒脉冲、强场驱动量子物态、交变磁超快动力学、莫尔异质结、量子几何/Berry curvature 测量）没有任何可操作的技术迁移路径。

**元数据治理建议（真正可执行）：**
1. 本条目在文献库中存在**严重元数据串号**——arxiv_id `2411.03137` 对应的实际论文是 Guo et al. 的 AI 写作 HCI 论文，而非 HHG 综述。建议立即在文献库中：
   - 将本条目移出 `project: NSFC-强场超快` 标签
   - 修正 `title`、`tags`、`direction` 至正确主题（HCI / AI-assisted creative writing）
   - 检查是否还有其他 deepxiv 条目存在相同 ID 串号问题
2. 在 `literature_service` 入库流水线增加**三角校验**：title + arxiv_id + 摘要首句之间至少两个字段一致才入库；不一致则进入人工审核队列
3. 本条目 `used_by_proposals: [key-transient-quantum-phase-optical-20260726]` 应解绑——把 HCI 论文塞进"瞬态量子相位光学"提案的文献支撑链会污染提案可信度

**对组会/学术写作工作流的次要参考（不进入方法卡）：**
- 论文 §4.2.1 中"AI 太会模仿自己 → ownership 反而下降"（P7 估算 30%–35% 内容可归 AI）以及"许多写作者自建版本控制与日志记录创作决策"（P14："creatives always need to know what the prompt is"）这两个观察，若本组用 LLM 辅助撰写论文/基金本子时可作为**自检提示**：长期依赖 LLM 可能稀释本组工作的"声音"与原创署名感，且对 prompt 与生成内容的版本溯源是必要纪律。

**结论：不进入本组方法卡/方法页融合；不引用至任何物理课题方案。** 主要价值在于暴露文献库元数据质量问题。

---

## 来源

- 蒸馏自全文（deep-read）。arXiv:2411.03137v4 [cs.HC]（实际为 Guo et al., C&C '25, DOI: 10.1145/3698061.3726910；frontmatter 标引为 HHG 综述，与实际全文不符——见正文元数据失配提示）。全文在 §4.2.1 中部截断。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：固态 HHG 最新进展综述（211 行 fulltext：带内/带间机制+拓扑/关联/Mott 体系+多维场驱动+量子光学交叉）

**原理**：固态 HHG 领域的系统综述：涵盖带内/带间机制分类、拓扑材料（Weyl/交变磁/莫尔）中的 AHHG、强关联体系（Mott/CDW/激子）、多色场波形工程、以及 HHG 与量子光学/机器学习的交叉前沿——为领域研究者提供从基础物理到实验设计的全景参考。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 综述范围 | 固态 HHG 全领域：机制/拓扑/关联/波形工程/量子交叉 | 标题/全文 |

**适用边界**：211 行 fulltext 综述但本批上下文有限未完整读取。
**代表作**：arXiv:2411.03137
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[key-transient-quantum-phase-optical-20260726]]
- [[强关联体系]]
- [[强场超快]]
- [[强场驱动]]
- [[瞬态量子相位]]
- [[量子几何]]
<!-- /linsai-wikilinks -->
