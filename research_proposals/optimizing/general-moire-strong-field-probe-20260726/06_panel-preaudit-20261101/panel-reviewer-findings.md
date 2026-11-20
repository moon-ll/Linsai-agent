核查完成，findings 已写入：
/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-moire-strong-field-probe-20260726/06_panel/panel-reviewer-findings.md

结论摘要：

遗留 5 条核对
- 已解决 4 条：
  · #1 I_c/损伤阈值错挂——rationale §1.5 L85 已两量分立，数值归属与 scheme §3.3.3 参数表（L168 I_c 三档 / L164 阈值 10¹²）一致
  · #2 “方案参数表”悬空引用——scheme §3.3.3 已落地 45 行实体表（参数/取值/来源三列），原四处引用全部实指
  · #4 靶标 A 主判据互斥——content §2.1 L29 已按 scheme §3.4.1 三分支版统一
  · #5 full_review 超骨架——已重写为三段式纯骨架，中文字 1,553 ≤ 3,000（历史“超字”告警系字节误计，与既往 critic-round-5/6 裁定口径一致）
- 仍存在 1 条：#3 蒙特卡洛点数协议半修复——scheme §3.2.4 L79 已定“N=50 出误差棒 / N=30 灵敏度扫描”分工，但 content §2.2.2 L61 仍写“30/50 次采样对比曲线作 95% 置信区间估计”双档并列，未对齐分工口径

新发现 3 条（≤5 上限内）
- P1 [medium] scheme §3.4.1 L218“超出样品损伤阈值 5 倍余量（约 10¹²）”可误读为 I_c > 5×10¹²，与另两章“余量不足 5 倍”（判据线 ≈2×10¹¹）歧义
- P2 [low] rationale §1.3 L47 “OPCA” 漏字，应为 OPCPA
- P3 [low] scheme §3.4.2 L228 椭偏“180 点”未注上端档归属

程序扫描：跨章口径表 21 项禁用旧值模式全库零匹配，无 stale 值需跨章同步修正。