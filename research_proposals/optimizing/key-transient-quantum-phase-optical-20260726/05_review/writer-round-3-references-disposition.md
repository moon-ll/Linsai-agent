# writer 处置记录（第 3 轮 · references 焦点轮）

- 对象：04_proposal/sections/references.md（48 条 → 40 条，编号 1–40 连续）
- 聚焦维度：完整性（0.75，最弱维度）
- 触发依据：05_review/critic-round-3-references.md（8 条问题：critical 0，high 1，medium 4，low 3）

## 逐条处置

### 1. [high] 48 条超 20–40 上限第 3 轮 → 已消除
裁至 40 条并重映射编号。裁撤 8 条，每条被裁论证均由保留的**已发表**条目承载，论证强度不降：

| 裁撤（原编号） | 文献 | 论证落点 | 保留的已发表锚 |
|---|---|---|---|
| [4] | Roadmap on attosecond science（arXiv:2604.15085） | 战略定位段 | 该句并入诺贝尔奖重心句；无需文献支撑 |
| [17] | Jacobsen THz-STM（arXiv:2602.14875） | Floquet 空间分辨 | 空间维度与本项目全光时间分辨路径不重叠，整句删除；scheme §5(1) 改由 [15] Lesko 的 K/K′ 布居差异承担"锁定时间维度" |
| [24] | Mokhtari 声子退相干（arXiv:2604.07543） | 退相干时标 | [35] Herling & Neufeld（J. Phys. Chem. Lett. 2026）——已发表，同载声子抑制产额与相位相干擦除 |
| [25] | Ilin 关联张量（arXiv:2604.20388） | 第四类约束通道 | [22] Granados（跨拓扑类别共同判据）+ [40] Stammer（亚周期敏感度）；关联张量结论去引用化后并入 SSH 一维示意体系段落 |
| [37] | Kowalczyk 中红外频梳（arXiv:2609.01359） | CEP 噪声实测 | [27] Meier（Appl. Phys. B 2026）——已发表，2 μm OPCPA 端 CEP < 70 mrad |
| [42] | Srikanth 合成维度绕数（DOI 10.1364/cleo_fs.2025.ff148_2） | 整数不变量读取协议 | [23] Zhang（Chin. Phys. B 2022）——已发表，陈数可编码于 Berry 曲率或量子度规 |
| [46] | Tan 低温带隙工程（arXiv:2511.16165） | 转换区判据实验佐证 | [16] Park（ACS Nano 2024）——已发表，Bi₂Se₃ 同靶材光致应变 Z₂ 开关 |
| [47] | Dubois 量子光电子干涉（arXiv:2606.13447） | 信号解析侧参照 | [40] Stammer——同一量子光学通道的测量侧锚 |

**裁撤选择准则**：优先裁预印本与会议论文（保留条目中已发表者占 30/40），且仅裁论证可被已发表条目完整承载者。未裁任何承载唯一论证的条目（[15] Rudner Floquet 框架、[18] Zhao Z. WS₂ 数值锚、[19] Kim 1T-TaS₂ 赝能隙依据、[21] Sufyan DCD、[26] Fan 国内现状、[30] Neufeld 泛函基准、[31] Watanabe KS-多体 Berry 相位、[45]/[39] 各章基准表等均保留）。

### 2. [medium] 处置链留痕 → 已补录（本文件即留痕载体）
Tornow[7] 与 Srikanth 原条目的来源核验依据：
- Tornow：CrossRef `api.crossref.org/works/10.1038/s41566-026-02025-8` → *Nature Photonics*，2026 年上线，卷期页未编目，条目保留"在线发表"标注（与 R2#6 一致）。
- Srikanth：CrossRef `api.crossref.org/works/10.1364/cleo_fs.2025.ff148_2` → CLEO 2025 会议论文，题名逐字一致，作者序 Srikanth/Sridhar/Miller/McComb/Dutt 共 5 人，页码 FF148_2。该条目元数据本身经核验属实，但为会议论文且论证可由已发表条目承载，本轮按问题 1 裁撤。

### 3. [medium] 已核验 DOI/arXiv 未回录池 → 已回录
reading-notes.md 追加"参考文献表裁撤与全量元数据复核"一条记录，含 51 条候选（34 DOI + 17 arXiv）的复核方式、裁撤清单、论证落点对照表与结构指标。

### 4. [medium] 括注超 ≤61 字 → 已消除
全部条目括注压至 ≤61 字（实测最大 61）。[39][40] 两条由原 87/66 字压缩，机理细节下沉至正文引用点。

### 5. [medium] †预印本 17/48＝35.4% 超 30% → 已消除
裁撤 7 条预印本后为 10/40＝25.0%。

### 6. [low] 卷(期)与"卷: 页"两式混排 → 已消除
11 条混排条目统一删期号，全部条目为"期刊, 年, 卷: 页"单式（[7] Tornow 卷期页未编目，保留"在线发表"）。

### 7. [low] [19] TaS₂ 排版形 → 已消除
按 arXiv 原式改为 `bulk 1T-TaS₂`。

### 8. [low] 孤儿预检 → 复算确认零孤儿
聚合 token（区间/逗号/空格）三章展开复算：列表 40 条全部有正文挂点，跨四章 + 00_research_idea.md 的角标集合与列表完全一致，孤儿 0、缺失引用 0。

## 元数据真实性核验（引用真实性红线）

本轮对全部 51 条候选（裁撤前 48 条 + 3 条曾被误配 DOI 的候选）逐条调用外部 API 复核：
- 34 条 DOI：`api.crossref.org/works/{DOI}` → 作者链、题名、期刊、卷期页、年份五件套逐项吻合
- 17 条 arXiv：Atom API `export.arxiv.org/api/query?id_list={id}` → 题名、作者链、提交日期吻合；全部条目 `jref`/`doi` 字段为空，† 标注全部属实，无见刊漏标
- **纠偏**：params.json `refs_doi_status_5_23_34` 条目内记 "[34] Kiselev（PRL 2026, 137(10): 106903, DOI 10.1103/lwpl-brrr）"，经 API 复核该 DOI 实为 Kiselev E.I.《Dynamical Breaking of Inversion Symmetry, Strong Second Harmonic...》PRL 137(10)，与表内第 31 条（Watanabe，arXiv:2602.22578，SSH-Hubbard 链 KS-多体 Berry 相位）并非同一篇。故第 31 条维持预印本形式，**不添加**该 DOI。该条 params.json canonical 的实质要求（刊版元数据属实、保留刊版条目、不降级为预印本）未被违反。

## 跨章一致性

- 角标重映射：rationale / content / scheme / full_review 四章 + 00_research_idea.md 全部 [N] 按新表重编，程序复检零孤儿、零缺失、零悬空作者名
- 段落改写：被裁条目所涉段落逐段重写为连贯叙述，未留悬空引用（rationale §1/§2.2/§2.3/§3、content §2.3、scheme §5(1)）
- canonical 口径：params.json 全部 stale_pattern 零命中；WS₂ 语境引 [18]（Zhao Z.）、MgO 语境引 [17]（Zhao C.）经复检一致

## 历史遗留 P0 核对

- scheme §6 Y4「17 组分批至第 5 年」：**当前文本已实现**（"当年完成 13 组" + "余下 4 组…在第 5 年完成"，L1 两组不重复入账），本轮未改动
- scheme §4 D4「机时第 3 年交叉验证后提交」：**当前文本已实现**（§2.3(a) "第 4 年峰值档的额度在第 3 年 RT-TDDFT 前向模型完成交叉验证后按实测量级正式提交"），本轮未改动
- 两条 P0 均已消除，状态维持"已解决"

## 附带处置

- 冗余指令（E₀ = 0.5 V/Å ↔ 3.3×10¹² W/cm² 在 rationale 与 scheme 双现）：保留 rationale §1 的换算推导（canonical 源头），scheme §2.1(b) 改为"换算见立项依据 §1 首段"；rationale 段内重复改为"按上式换算为"
- 重复论证：Bi₂Se₃ 光致应变约 7% 原三处复述，§2.3「反演方法储备」处改为不带数值的形式引用，数值保留在 §2.2（首次出现处）与 §3
- 句长：rationale 唯一一处 123 字长句已拆分；四章正文现无 >120 字句（表格行与文献条目不计）
- 冗余修饰：删除"显著""完整落点""系统报道"三处；余下"系统""有效""关键"均为系统误差／有效哈密顿量／关键科学问题等科研法定用法
