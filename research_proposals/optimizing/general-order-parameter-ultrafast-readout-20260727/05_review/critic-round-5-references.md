# 对抗评审报告（第 5 轮 · 参考文献专项）

## 元信息
- 项目类型：general（面上）；日期 2026-09-22；对象 04_proposal/sections/references.md（43 条）
- 预检采信：[N] 编号一致性由程序预检完成，本轮直接引用（43 条连续、正文引 42 个编号、[11] 未被引用、总数超区间）
- 上轮参照：round-8-references（2026-09-04 归档），其编号错挂 critical 经预检确认已修复

## 核验方法与总量结果
CrossRef 反查 30 条含 DOI 条目（全量非抽查，五件套比对）；arXiv export API（https）反查 36 条含 ID 条目并核 journal_ref/doi 字段；正文 [1]–[43] 计数以 `\[\d{1,2}\]` 裸模式程序复核。

- 43 条题名/作者/期刊/卷期/年份**全部真实，无虚构条目**；预检 7 条凭记忆条目 [2][3][14][18][22][23][37] 经 CrossRef 核验全真（R7 式虚构未复现）
- 13 条【预印本】标签经 journal_ref 核验全部准确
- 时效性：2024–2026 文献 22/43 = 51.2%，达标
- 相关性：13 分组逐条判读，均与"序参量超快读出"直接相关，无无关引用
- 元叙述：L5 自称"84 处行内引用"，实测 115（rationale 59 + content 12 + scheme 44），失实

## 锚点对比
申请书 [42]（L131）：「Sasioglu, E. et al. The magnon spectra of g-type altermagnet bulk CrSb. arXiv:2510.03759」
arXiv 2510.03759 官方记录：唯一作者 **Murat Tas**；题名/日期一致；无 journal_ref。
差距：典型"真实 ID + 虚构作者链"——Sasioglu 系该领域常见署名，凭学科记忆张冠李戴；正文 scheme L29 连带使用"Sasioglu 等人 [42]"。改写方向：条目改「Tas, M. …」，正文改「Tas 等人 [42]」。

## 问题清单
- [critical]｜references L131 + scheme L29｜[42] 作者链虚构：arXiv:2510.03759 唯一作者为 Tas, M.，非"Sasioglu, E. et al."，正文连带误称｜条目改「Tas, M. The magnon spectra…」，正文改「Tas 等人 [42]」；修复后 grep "Sasioglu" 须零残留
- [high]｜references L123｜[40] Mineev DOI 错挂：10.1103/PhysRevB.114.065130 经 doi.org/CrossRef 双查 404，真实注册 DOI 为短式 10.1103/mytl-kml2（PRB v114, 2026 存在）｜DOI 替换为 10.1103/mytl-kml2
- [high]｜references L39｜[11] Hansen & Madsen 悬置：三正文件 [11] 出现 0 次，唯一未被引用条目｜在 rationale §3 方法学警示段补引，或删除并全表重排编号
- [high]｜references L5｜元叙述计数失实："84 处行内引用"实测 115 处｜L5 改"115 处"并注明统计口径
- [medium]｜references L115｜[37] 作者名首缺失："Krempaský, J." 43 条中唯一不完整作者字段｜补全为 Krempaský, J.
- [medium]｜references 全表｜总数 43 超面上 20–40 区间 3 条（预检已标记）｜优先删 [8]（被 [9] 正式版覆盖）、[35]（辅助锚点）、[30]（结论可并入 [29]）；保留则 L3 须说明理由
- [low]｜references L73/L79｜[24][27] 截断作者列表与其余 41 条全列风格不一｜统一补全或全表改"首三作者 + et al."
- [low]｜references 7 处｜APS 短 DOI 与长式 DOI 混排｜统一长式，无法长式化注明"短式注册 DOI"
- [low]｜references 多处｜页码风格混排：文章号与页区间混用，连字符 em-dash/全角混排｜统一两种合法格式与连字符

## 对抗结论
- 本轮 9 个问题（critical:1, high:3, medium:2, low:3）
- 相比上一轮：编号错挂 critical 已修复；新增问题集中作者链与元叙述层
- 是否达标：否。1 critical + 3 high 须当轮验收：[42] 修复后 grep "Sasioglu" 四文件零残留；[40] 新 DOI CrossRef 复验；[11] 去留后预检重跑确认悬置清零
- 返工优先级：P0=[42]；P1=[40] DOI、[11] 悬置、L5 计数；P2=压回 40 以内 + 作者字段与风格统一
- 下一轮建议：writer 补充检索回录 02_literature 时同步更新 L5 计数，防旧值回灌

## 评分
创新性：N/A
可行性：N/A
严谨性：0.65
完整性：0.73
综合评分：0.69
