# 对抗评审报告：参考文献第 2 轮（general-ssh-weyl）

## 综合评分
0.62 / 1.00

## 维度评分
| 维度 | 权重 | 得分 | 问题数 |
|------|------|------|--------|
| 严谨性 (rigor) | 0.5 | 0.45 | 11 |
| 完整性 (completeness) | 0.5 | 0.80 | 5 |

（注：本轮聚焦"引文真实性/格式/数量/时效"，创新性与可行性按契约填 N/A，
故未走 NSFC general 标准加权。本表仅按"严谨性+完整性"两项等权平均报告。）

## 锚点对比

**申请书核心锚**："C. Liu, Y. Zheng, Z. Zeng, and R. Li, 'Effect of Berry curvature… in ZnO crystals,' Phys. Rev. A 97, 063412 (2018)" ([21])

**CrossRef/OSTI 实测**："C. Liu, Y. Zheng, Z. Zeng, and R. Li, **'Driving-laser ellipticity dependence of high-order harmonic generation in graphene,'** Phys. Rev. A 97, 063412 (2018)"。同一DOI同一卷页号，**对象从 ZnO 漂移为 graphene** —— 申请书 [21] 锚链整段失效。
差距项：applicant 把"Berry 曲率+反常HHG"立论挂到 ZnO，但真实锚文是 graphene；建议改为graphene版本作 [21]，ZnO 立论改挂 [50] Jessen PRB 112, 214311 (2025) 或另查 [21B] 同年 Zheng Liu ZnO PRA 98。

## 问题清单

[critical]｜references.md [21]｜材料错位 PRA 97,063412(2018)实为graphene非ZnO｜删[21]挂graphene,ZnO立论改挂Jessen[50]
[critical]｜references.md [39]｜材料错位 NatPhys 13,345(2017)实为MgO非ZnO｜删[39]挂MgO或重选ZnO各向异性HHG基线
[critical]｜references.md [43]｜标题+首作均错 PRB 113,125144(2026)实为"Attosecond pulse generation"非"Multiband effects"｜更正标题"Attosecond pulse generation from Weyl semimetals";首作改"Prachi Venkat"
[high]｜references.md [48a]｜NatCommun 12,6437(2021)条目正文未引用成孤儿｜删除或归并为[48]附注,不加[48a]重编号
[high]｜references.md 总条目｜共50条超NSFC general 20-40区间+28%预印本比例偏高｜精炼至30-35条(基础文献/锚文/对照实验),删预印本未刊条目
[high]｜references.md [1-20]｜21条孤儿(预印本+早期基础)占用名额却无引用价值｜按"基础文献必须引,顶级文献必须引"精简到≤10条
[high]｜references.md [33] Yue-Gaarde PRL 130,166903(2023)｜孤儿且arXiv未在正文锚定｜删除或新增正文一处引用使其功能化
[medium]｜references.md [26][43][44] 无独立arXiv ID｜Crossref已确认真实但本文件只挂DOI无arXiv冗余｜补arXiv ID作为hash锚防DOI重定向错位
[medium]｜references.md [22] Heide NatPhoton 16,620(2022)｜正文描述同可,但(Bi₁₋ₓInₓ)₂Se₃化学掺杂相变≠典型Weyl节点HHG｜核对正文是否把[22]正确描述为TI相变非Weyl
[medium]｜references.md [45] Duan NanoLett 26,10554(2026)｜幂律区间"2.3渐降至0.3"与R8约定口径不符｜查PDF全文复算饱和曲线,I∝E^n中n的实际取值与场强范围
[medium]｜references.md [7]标识符｜[1-10]类10条无DOI/arXiv可追溯来源｜书籍/综述可豁免,期刊文章必须挂DOI或arXiv ID
[low]｜references.md [3][4] Corkum-Krausz 2007/2009｜两条综述被列却未被正文引用,占用名额｜删除至少一条,与申请书HHG谱学定位冲突不显
[low]｜references.md [14] Guan Zhou Bian PRA 93,033852(2016)｜孤儿+作者姓氏"Guan/Bian"中文匹配度低难验证｜删除或换为可验证版本

## 反向核查总结（crossref/arXiv 验证清单）
- [24][25][29][30][34][35][36][37][38][40][45][50] arXiv ID 实测全部存在，作者/标题吻合 ✓
- [26][33][41][42][44][46][47][48] DOI 实测真实，元数据吻合 ✓
- [21][39][43] 三条 DOI 卷期页号形式真实但**对象/标题错位** ✗（见上critical）

## 关键修订指令（writer 下轮执行）
1. **P0 三连**：删除/更正 [21][39][43] 三条文献中对象/标题/作者首作缩写错位
2. **P0 残留**：删除孤儿 [48a]
3. **P1 精简**：50→30-35 条，删除全部 21 条孤儿；arXiv 预印本条目（2026 年 9+ 条）严控 ≤6 条，剩余 arXiv 条须确认至少被正文两处锚定
4. **P1 标识符**：所有期刊条目必须挂 DOI 或 arXiv ID，综述/书籍豁免须显式标注
5. **P2 验证**：剩余编号在写入前用 CrossRef/arXiv 重新核对作者顺序与首作缩写

## 工作日志污染检查
- references.md 内无 TODO/TBD/占位符；注解性"预印本，未见刊"标记9处，与申请书方法部分"理论锚定需要预印本最新版"叙述一致，无需迁 05_review。

## 对抗结论
- 本轮发现 13 个问题（critical:3, high:4, medium:4, low:2）
- 相比上一轮：新增 [21][39][43] 三条对象错位 P0（crossref实测），前轮未测这三条；半数以上 "DOI/arXiv 真实性" 通过反查核验 ✓
- 是否达到输出标准：否——三条 critical 错位会直接拉低严谨性至 0.45，须下轮严改后才能接近 0.75+ 出版水

## 评分
创新性：N/A
可行性：N/A
严谨性：0.45
完整性：0.80
综合评分：0.62
