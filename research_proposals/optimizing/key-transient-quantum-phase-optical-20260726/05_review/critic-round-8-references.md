# 对抗评审报告（第 8 轮·参考文献专项）

- 项目类型：key（瞬态量子相的全光读写与时序反演）
- 审查日期：2026-09-22
- 审查范围：04_proposal/sections/references.md（41 条，编号 1-41 连续）
- 方法：41/41 全量反查（CrossRef DOI 逐条解析 22 条 + arXiv export API 20 条，三核：题名+作者链+卷期年）；编号一致性采信预检，不重复核对
- R7 修复验收：上轮 10 项全部落地——[46]Watanabe→今[36]Kiselev（arXiv:2510.12990 单作者 E. I. Kiselev 属实，正文挂点一致）；[47]DOI 错位→今[37]已改 4c01383 且卷页 15, 7254-7264 与 CrossRef 一致；[31]Ilin 顺序→今[22]已按官方顺序改写；编号缺口已消（1-41 连续）；[11][12][25]卷页已补；[4]存疑刊名已删（纯 arXiv）

## 核验统计
- 真实性：41/41 题名-作者-卷期可溯源，0 条虚构、0 条题名/ID 错配；作者链逐位一致 38/41
- arXiv 20 条 ID 全真且题名年份匹配；DOI 22 条中 21 条解析一致、1 条 404（[29]）
- 时效性：2024-2026 文献 33/41 = 80%（2026×16、2025×10、2024×7），达标（≥50%）
- 数量：41 条，超出 20-40 区间 1 条（预检已标记膨胀告警）
- 相关性：对弱相关候选 [15][26][27][29][30][38] 逐一调取正文挂点，均有实质论断支撑且论题相关（如 [29] 作 Wilson 圈体-边对应参照、[30] 作 ML 时间传播子加速 RT-TDDFT 依据），无无关引用
- 预检点名 15 条未验证条目（[1,2,3,5,6,7,10-13,15,16,18,19,24]）经全量反查全部为真，虚构风险未兑现

## 锚点对比（实锤条目逐字比对）
- 申请书 [23]：B. Lorenzo, C. Granados, D. Kim, C. Batista, J. Menotti, F. Liu, W. Gao, S. Ghimire, A. Chacón
- arXiv:2508.15631 官方作者链：Bryan Lorenzo, Carlos Batista, Milad Jangjan, Dasol Kim, Jean Menotti, Feng Liu, Wenlong Gao, Shambhu Ghimire, Camilo Granados, Alexis Chacon
- 差距：9/10 作者同池但整体错序（Granados 由第 9 位提前至第 2 位），且漏列第 3 作者 Jangjan——同池错序型失真，非虚构但歪曲署名顺序，须按官方链改写

## 问题清单
[high]｜L59 条目[29]｜DOI 10.1103/PhysRevB.114.065133 解析 404；APS 仅注册短 DOI 10.1103/vcxm-dr2g；题名较正式版多"two"｜改用短 DOI 并按 CrossRef 正式题名删"two"；action: verify+rewrite
[medium]｜L47 条目[23]｜作者链同池错序（Granados 第9→第2）且漏第 3 作者 Jangjan｜按 arXiv 官方顺序重排并补 M. Jangjan；action: rewrite
[medium]｜L51 条目[25]｜4 作者论文漏第 2 作者 Navarrete，仅列 3 人形同全列｜于 Kowalczyk 后补 F. Navarrete；action: add
[medium]｜L83 条目[41]｜arXiv+期刊+DOI 三标识并列、双年份"(2025);(2025)"，违反二选一；已见刊 Nat. Phys. 21, 1267-1274｜删 arXiv:2407.07953 与首年份，统一留 DOI；action: rewrite
[medium]｜全表｜总数 41 超出 20-40 区间 1 条（预检膨胀告警）｜删最弱单点挂点条目（候选 [26] 或 [17]）并同步正文标记与后续编号；action: remove
[low]｜L35 条目[17]｜"M. Finke" 应为 O. Finke（Ondřej）；且漏第 7 作者 M. Albrecht｜改首字母并补作者；action: rewrite
[low]｜L9/L49 条目[4][24]｜111/24 位作者以 et al. 截断，与其余全列条目制式不一｜可接受；或全表统一"前三+et al."；action: verify

## 对抗结论
- 本轮 7 个问题（critical:0, high:1, medium:4, low:2）
- 相比 R7：上轮 10 项全部修复验收通过（含编号重排全量同步）；本轮新增 1 high（[29] 短 DOI 形态，系 APS 长式拼装 404 判例，R7 未覆盖）；预检风险区 15 条经全量反查洗清，无一条虚构兑现
- 是否达到输出标准：是（有条件）——无虚构、无编号错误、时效达标；[29] 死链须当轮修复，[23][25][41] 作者链与标识清理后即收敛
- 返工优先级：[29] → [23] → [41] → [25] → 数量裁减（须最后做，重排后同步正文全部标记并 grep 复核）
- 下一轮建议：修复后对 41 条重跑 DOI/arXiv 自动比对（含短 DOI 变体）；writer 补充检索命中须回录 02_literature 检索池

## 评分
创新性：N/A
可行性：N/A
严谨性：0.84
完整性：0.86
综合评分：0.85
