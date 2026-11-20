# 对抗评审报告（第 5 轮 · 参考文献专项）

【项目类型】general
【审查范围】/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-attosecond-streaking-20260822/04_proposal/sections/references.md（34 条）+ 正文（rationale/content/scheme 三章）交叉核查
【审查日期】2026-09-17

## 综合评分
0.67 / 1.00（按 general 类型严谨性+完整性双维度等权均值）

## 维度评分
| 维度 | 权重 | 得分 | 问题数 |
| --- | --- | --- | --- |
| 严谨性（rigor） | 0.50 | 0.55 | critical:2, medium:2 |
| 完整性（completeness） | 0.50 | 0.78 | high:1, medium:2 |
| 创新性 | N/A | N/A | — |
| 可行性 | N/A | N/A | — |

## 核查方法
- 30 条 DOI 经 CrossRef API（api.crossref.org/works/{doi}）反查 5 件套（标题/第一作者/期刊/卷期年/作者数）
- 4 条 arXiv ID 经 arxiv.org/abs/{id} 抽 citation_title / citation_author / citation_date / journal-ref
- 与 02_literature/supplementary-sources-2026-08-29.json 及 targeted-research/lit-gap-*.md 交叉验证

## 锚点对比（核心冲突项）
申请书 [20]："Li M, Wang H, Tahouri R, et al. Photoionization time delays probe electron correlations. Physical Review Letters, 2025, 135: 183202. DOI: 10.1103/PhysRevLett.135.183202"
CrossRef 真身："Li, Wang, Tahouri | Photoionization Time Delays Probe Electron Correlations | **DOI:10.1103/ll25-15dm**"（卷期 135 但文章号非 183202）
doi.org 反查 10.1103/PhysRevLett.135.183202 → **HTTP 404**
正文 content.md L15 / rationale.md L29 将 [20] 用作"高谱分辨 RABITT 实验证实多电子关联"——真实论文存在但 DOI/文章号整体虚构

申请书 [34]："Zhu Y, et al. Attonsecond streaking phase retrieval via deep learning methods. arXiv:2505.06275 [physics.optics], 2025 (preprint, 系统比较 CNN/ViT/CNN-ViT/Capsule Network 在阿秒条纹相位检索)"
arXiv:2505.06275 真身："SinBasis Networks: Matrix-Equivalent Feature Extraction for Wave-Like Optical Spectrograms"（Zhu Y, 2025-05-06, **AAAI 2026 已接收**）
正文 scheme.md L132 用作"CNN/ViT/CNN-ViT/Capsule Network 系统比较"——研究对象完全错位；02_literature 仅在 lit-gap 占位表登记 "2505.06275 | (需补充元数据)"，标题/作者从未验证

## 问题清单
[critical]｜[20] references.md L41｜PRL 135:183202 DOI 10.1103/PhysRevLett.135.183202 CrossRef 404，真 DOI 为 10.1103/ll25-15dm，DOI+文章号双重虚构｜action:research——按 CrossRef 真 DOI 替换并补充真文章号
[critical]｜[34] references.md L69 + scheme.md L132｜arXiv:2505.06275 真作是 AAAI 2026 SinBasis Networks，与申请书"CNN/ViT/CNN-ViT/Capsule Network 阿秒条纹相位检索"主题完全错位｜action:remove 或 research——删除该条或重换同主题 arXiv 真实综述（如 Heathcote 2024/2025 attosecond deep learning 综述），scheme L132 同步改写
[high]｜[34] scheme.md L132｜正文复述错误条目（CNN/ViT/Capsule Network），把虚构信息嵌入备选路径 A 论证链｜action:rewrite——与 [34] references 同步替换或删除引用句
[medium]｜[34] references.md L69｜arXiv:2505.06275 实已被 AAAI 2026 接收，仍标"preprint"；且 primary-class 应为 cs.CV/cs.AI 非 physics.optics｜action:rewrite——若保留须标 AAAI 2026 + cs.CV/cs.AI
[medium]｜[21] [24] [29] references.md L43/L49/L59｜3 条 arXiv 仍标"preprint"且无正式发表状态说明，其中 [24] 2018 年预印本已 8 年未刊须更新长期状态｜action:rewrite——补刊状态：[21]/[29] 仍 preprint，[24] 注明长期预印本+已被 [27] 综述替代
[medium]｜[9] references.md L19｜CPB 35(5) 054204 (2026-05) DOI ae3474 是 accepted manuscript 标记，真作者为"Zhu 朱 Xiaoxian 孝先"等 5 人，申请书只列 4 人漏 Wei Zhiyi｜action:rewrite——补 Wei Z Y 为第五作者
[low]｜[18] references.md L37｜DOI 10.1103/9jcm-8gd8 形式非传统 PRL/PRA 编号格式（短码），多数读者不熟悉，建议加注"new APS short DOI"提示｜action:verify——保留即可但建议 inline 注释

## 时效性与数量
- 总数 34 篇（general 标杆 30-40，达标）
- 2023–2026 文献 17/34 = 50%（分界达标）
- 主题覆盖：streaking 方法学、水窗、时间延迟、角条纹、ML/AI、多通道、脉冲前沿——结构完整
- 引用-列表一致性：预检通过，无幽灵编号

## 对抗结论
- 本轮发现 7 个问题（critical:2, high:1, medium:3, low:1）
- 2 条 critical 中 [20] 属"占位 DOI+虚构文章号"，[34] 属"占位 arXiv ID+完全虚构标题与主题描述"，均落入 SKILL.md 历史教训的 P0 红线模式（R7 实测：6 条凭记忆条目 CrossRef 核查为虚构/错位致评分暴跌）
- 严谨性 0.55、完整性 0.78；按 critical 条款扣分纪律（critical 虚构→严谨 0.3-0.4 区间），本次仅 2/34 故取 0.55 而非更低；如 R6 修复时未替换真 DOI/真主题，next round 应进一步降至 0.40
- 是否达到输出标准：否，须在 R6 替换 [20] [34] 两条后才能进入签字
- 下一轮建议：writer 在 R6 必须 (a) 把 [20] DOI 换为 10.1103/ll25-15dm 并补真文章号，(b) [34] 删除或替换为同主题真实综述（如 Lucchini 2024 attosecond ML 综述或 Khan 2025 streaking phase retrieval），(c) scheme.md L132 同步删改引用句；中优先级问题（[9] 补作者、[21]/[24]/[29] 标注刊状态）一并处理
- 不存在工作日志膨胀，无须迁移

## 评分
创新性：N/A
可行性：N/A
严谨性：0.55
完整性：0.78
综合评分：0.67
