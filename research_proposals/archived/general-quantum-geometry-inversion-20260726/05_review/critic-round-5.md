# 对抗评审报告（第 5 轮·参考文献专轮）

课题：general-quantum-geometry-inversion-20260726｜类型：general（面上）｜日期：2026-09-11｜聚焦：references.md（55 条）｜上轮：R4 refs 专轮 0.74

## 核验方法与真实性结论
预检 32 条池外条目全部覆盖：24 条 arXiv 经 API 比对标题/一作/v1 日期，36 条 DOI 经 CrossRef works 反查，19 条纯 arXiv 另做 CrossRef 标题检索追发表版。结果：55/55 真实存在，标题-一作-卷期页主链一致，零虚构（R7 类风险排除）。核查产物存 05_review/.r5_refs_verify.json。

## 问题清单
[critical]｜整体｜总数 55 超 20-40 区间，R4 令裁至 ≤45 跨轮未执行｜裁[22][24][25][45][48][49][51][52][55]等至≤45并删挂点
[critical]｜[11]-[13][16]-[24][44][45][48][49][51][52][55]｜纯 arXiv 19 条占 34.5% 再超 30% 红线｜更新已发表 5 条并裁至 arXiv-only≤16
[high]｜[15][47][54]｜DOI …063111/…063107/…245147 均 404 死链｜换真 DOI d2pt-xp7x/cxff-kky6/n4gk-jxpc
[high]｜[42]｜PRR.7.043284 为 404 错构 DOI｜改 10.1103/8lhh-gq58（PRR 7, 2025）
[high]｜[19][20][23][45][48]｜已正式发表仍仅标 arXiv｜补 Adv.Phys.74,1-9/PRL135,043603/CPL43,020712/PRL135,146303/PRR 卷页 DOI
[medium]｜[13]｜标题系 v1 旧题，v2 已改 ultrafast melting of a Mott insulating state｜按 v2/发表版更新标题
[medium]｜[6][29][43]｜作者链以 et al. 截断，与他条全链风格不一｜补全或统一"前三位，等"式
[medium]｜[14]｜Nat. Mater. 无卷页且未按 R4 加 in press 标注｜补卷页或标 advance online
[low]｜整体｜期刊缩写三风格混用｜统一缩写表

注：预检"超出区间"属引用数量膨胀；references.md 无工作日志内容，不列"工作日志污染"项。

## 锚点对比
申请书：[23] Yang, B.-J. arXiv:2512.24553 (2025). "From Berry curvature to quantum metric…"
权威链：Yang, B.-J. Chin. Phys. Lett. 43, 020712 (2026). DOI 10.1088/0256-307x/43/2/020712（CrossRef 直查命中，标题/一作全同）
差距：主链准确但版本状态滞后，正式发表卷页 DOI 整体缺失——共 5 条同类。
锚点对比结论：基本接近

## 评分依据
严谨性 0.70：全量 55/55 真实性验证零虚构系首次全覆盖（R4 仅抽样 13 条）；扣分在 4 条死链 DOI（标识符事实错误，10.1103 旧式拼法未随 APS 新式 DOI 更新）、5 条已发表仍标预印本、[13] v1 旧题、[6][29][43] 作者截断，落入 0.70-0.79 档下沿。完整性 0.74：数量超区间 15 条与预印本 34.5% 两项 critical 跨轮残留；时效 32/55=58.2% 达标（≥50%）；缺失引用零——Vampa/Berry/TKNN/Xiao-Niu/Aversa-Sipe/Ghimire/Corkum/Lewenstein/Raissi 等核心链全到位；[27] 已按 R4 补 DOI（本轮 CrossRef 验证通过，唯一改善项）。

## 对抗结论
本轮 9 项（critical 2、high 3、medium 3、low 1）。较 R4：改善 1（[27] 补 DOI）、残留 5（数量/预印本占比/[23] 族/[14] 标注/缩写）、新增 3（死链 DOI×2 行、[13] 旧题、作者截断）。真实性主线全量达成；标识符可核性（4 死链）与版本新鲜度成新短板。未达输出标准（两项 critical 残留）。返工优先级：P0=换 4 条真 DOI+更新 5 条发表版（机械操作）；P1=裁量至 ≤45 且 arXiv-only≤16。下轮验收口径：references.md 内 grep '043284|063111|063107|245147' 归零、总数≤45、arXiv-only≤16、et al. 处置完毕。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.70
完整性：0.74
综合评分：0.72
