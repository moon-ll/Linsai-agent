定点核查完成，报告已写入：

/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-houston-kronig-penney-landau-zener-20261004/06_panel/panel-researcher-findings.md

核查结论摘要：

遗留问题 18 条 —— 已解决 16 条，部分解决 2 条（#1 残留 1 处、#4 缺 5 处限定语）。

关键取证（非记忆判断，全部实时核验）：
- CrossRef 逐条比对 16 条期刊条目（作者/卷/期/页/年份/DOI 全符）
- arXiv API 核验 7 条预印本，6 条实测无 journal_ref（均未见于刊）
- 抓取 arXiv HTML 全文验证断言：#12 的 I³ 标度与 16 阶、#30 的 100 μm (100)/HH12/取向 α、#37 的七阶与动态 Stark 带隙蓝移、#9 的两条指纹与 "below approximately 1 eV" —— 申请书表述均属实
- 角标对账：三章并集覆盖 1–42，无孤儿条目；full_review 中 9 条仅出现于备注列（出处指针，非实报 scheme 引用）
- 超长句程序化重扫：43 处 → 2 处（rationale L59 为连续设问句、scheme L103 为公式行）

仍需修改（合计 6 处文本编辑 + 3 处体例补充）：
1. rationale L27 「即反常电流[3]」——[3]（Neufeld PRX）研究对象是 Kane-Mele 拓扑签名不可靠性，不支撑反常电流定义，应改挂 [11,9]。这是 9 处错挂的最后1 处。
2. #4 补 5 处「（预印本）」：[30][32][41][42] 在 rationale L19/L21/L23、content L17/L65 仍以定论口吻支撑动机链。
3. scheme L103 公式长句拆为两句（125 字）。
4. references [34] 括注用 γ、scheme L101 用 η_co，同一物理量两个符号，建议统一。
5. （可选）rationale L19/scheme L97 补注：[37] 实测强度 3.4–6.5 TW/cm²，与本方案 0.1–2 TW/cm² 差 1.5–2 个数量级，动态 Stark 结论不可直接外推。

另：遗留问题 5 的复评条件建议改为「阻断项清零」而非绝对分数 0.85 —— [3] 错挂与 citation_status 两类清零后即可解除。

未发现任何新的引用元数据错误。