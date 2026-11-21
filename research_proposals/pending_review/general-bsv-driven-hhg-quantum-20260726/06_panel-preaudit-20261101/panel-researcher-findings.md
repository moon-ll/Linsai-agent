• 我先读取相关章节文件并核查两个遗留问题。

• 检查 section_hygiene.py 的预检判据是否已改为中文字数。

• 检查当前 full_review.md 的体量，验证预检是否仍误报。

• 遗留问题 2 的判据仍有字节分支，继续抽查引用真实性与数值链。

• 抽查两条文献元数据（researcher 职责：引用真实性）。

• 发现一处引用版本注记疑似失实，再确认预检函数的调用链是否仍活跃。

• 核查完毕，写入 findings 文件。

• 定点核查完成，findings 已写入 `06_panel/panel-researcher-findings.md`。核心结论：

  **遗留问题核对**
  1. **cross_section_consistency — 已解决**。旧枚举"产额比/可见度比/噪声关联比"在申请书本体零残留；"噪声关联比"现存命中均在 `05_review/` 评审域。rationale.md:9 已按分方向三改为三指标实名，与 content.md:63、scheme.md:61 逐项一致。
  2. **precheck_misfire — 仍存在**。判据修复只落了一半：`migrate_full_review_record`（section_hygiene.py:255）已改用中文字数 + 骨架头判定，但 prompt 注入侧 `full_review_purity_text` 的告警条件（section_hygiene.py:191）还留着字节分支 `size > 4500`。实测当前干净骨架（1490 中文字、"# 全文逻辑骨架"头、零工作记录命中、6894 字节）仍触发告警，且 optimize.py:1193 活跃调用——这就是"预检误报第三连轮"的同根问题。建议删除字节分支。

  **新发现 1 条（P1 high）**
  - references.md:55 / rationale.md:39 称 [26] Wang "quantum dial" 为 "arXiv:2509.13518v3，2026-09-01 更新"，但 arXiv 官网（今日实查）该文只有 v1（2025-09-16）和 v2（2025-12-03），**无 v3**。版本注记失实，且注入侧跨章口径表同样携带这个错误锚点，需一并修正并复核 1.2 TW/cm² 的取值版本。

  其余 researcher 范围抽查全部通过：五步内推链、Rasputnyi 138×/11×/25× 折算、U_p、光子能量窗口均复算自洽；[25] Lange 元数据与摘要相符；canonical 旧值字面量全章零残留。