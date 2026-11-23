#!/usr/bin/env python3
"""apply_prompt_upgrades.py — writer/critic SOUL.md 提示词升级应用器（v6.9.9）

本会话（TRAE 沙箱）无 ~/.hermes 写权限，故将 writer/critic SOUL.md 的
修复内容封装为本脚本，在沙箱外手动执行一次即可应用。

修复内容（对照范本 references/nsfc-templates/ 实测校准）：
writer SOUL.md：
  1. 句长口径校准：">80字应拆分" → "80-120字技术性长句属正常，>120字必拆"
     （范本实测超80字句占 12%-28%，旧红线会把范本判为不合格）
  2. 关联词口径校准："删除死板关联词" → "模板化表达全文≤5次"
     （范本实测"在此基础上"出现 3 次，绝对禁止过严）
  3. 尾部污染段整体替换：两个重复的"优化规则（自动添加）"标题 +
     "总字数≥4000字"低标准（范本仅立项依据即 5000-8000 字）+
     描述性"行为约束"（"需在 prompt 中要求…"，agent 无法执行）
     → 替换为"篇幅对标（范本实测口径）"+"运行纪律（提交前自检 5 条）"
critic SOUL.md：
  4. 尾部污染段替换："占位符给 0.10"魔法数（与四维评分体系口径不协调）、
     评分自洽一句话 → 替换为"评分纪律"（占位内容降档规则 + 评分自洽公式）
  5. 补充锚点对比三步操作法（引用→对比→差距）

用法：
    python3 scripts/apply_prompt_upgrades.py            # 应用（幂等，已应用则跳过）
    python3 scripts/apply_prompt_upgrades.py --check    # 仅检查是否已应用

自检：
    python3 scripts/apply_prompt_upgrades.py --self-check
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PROFILES_DIR = Path.home() / ".hermes" / "profiles"
BACKUP_DIR = PROJECT_ROOT / "memory" / "prompt-backups"

WRITER_PATH = PROFILES_DIR / "writer" / "SOUL.md"
CRITIC_PATH = PROFILES_DIR / "critic" / "SOUL.md"


def _now_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _backup(path: Path) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    dst = BACKUP_DIR / f"{path.parent.name}-{path.name}-{_now_ts()}.bak"
    shutil.copy2(str(path), str(dst))
    return dst


# ── writer SOUL.md 替换规则 ─────────────────────────────

WRITER_RULES = [
    (
        "句长口径校准",
        "5. **动词主导、短句为主**：单句超过80字应拆分，超过120字属严重超长句",
        "5. **动词主导、句长适中**：范本句长中位数约 56 字；80-120 字的技术性长句"
        "（多分号分句）属正常，单句超 120 字必拆分；不用破折号插入语",
    ),
    (
        "关联词密度口径",
        '| 死板关联词："在此基础上""此外""同时""与此同时""因此""基于此" | 删除，或替换为内容驱动衔接（如"上述分析表明…""数值结果表明…"） |',
        '| 模板化表达堆积（"在此基础上""此外""同时""与此同时""因此""基于此"，全文合计超过 5 次） | 压缩到 5 次以内，段间衔接优先用内容驱动（如"上述分析表明…""数值结果表明…"） |',
    ),
    (
        "去AI味表超长句行",
        "| 超长句（>80字） | 拆分为短句 |",
        "| 超长句（>120字） | 拆分为短句；80-120 字技术性长句可保留，控制每段不超过 2 句 |",
    ),
]

WRITER_TAIL_MARKER = "## 优化规则（自动添加 2026-08-13）"

WRITER_NEW_TAIL = """## 篇幅对标（以范本为标杆，2026-08-15 校准）

旧规则"总字数≥4000字"远低于范本体量，已废弃。以下为范本实测口径（面上项目正文约 2.9 万字符）：
- 立项依据：5000-8000 字
- 研究内容：3000-5000 字
- 研究方案：5000-8000 字
- 特色与创新：3 点并列，每点约 200 字
- 参考文献：30-40 篇，正文 [N] 编号引用 10-20 次即可，其余文献作为研读基础列入文末
若 brief 素材不足以支撑上述篇幅，宁可深挖已有素材的论证链，不得注水或罗列堆砌凑字数。

## 运行纪律（提交前自检，逐条执行）

1. **实质修改**：逐条核对评审报告的每个问题，逐一修改；在输出中给出"问题→修改对照"，未修改的问题必须说明原因。禁止原样提交上一轮文件或仅做表面增删。
2. **清理痕迹**：提交的 .md 文件中不得残留迭代记录、优化说明、审稿对话、元信息等任何工作流痕迹；正文只包含申请书内容本身。
3. **禁止占位符**：不得提交"待补充/TBD/待核验/XXX"等占位内容；信息不足处改写为不依赖该信息的表述，或明确标注"需要 researcher 补充文献"并给出替代论证。
4. **骨架充实**：若申请书或章节过短（远低于篇幅对标下限），按章节结构规范写出完整论述，不得只列提纲。
5. **终检**：提交前将每个段落与"范本锚点"对比语体与论证密度；用"去AI味"表逐项自查一遍。
"""

# ── critic SOUL.md 替换规则 ─────────────────────────────

CRITIC_TAIL_MARKER = "## 优化规则（自动添加 2026-08-13）"

CRITIC_NEW_TAIL = """## 评分纪律（2026-08-15 校准）

1. **占位/缺失内容的降档规则**：当章节为空、仅含提纲或占位符（"待补充/TBD"）时，
   不评出具体魔法分值；在受影响维度的评分依据中注明"本轮因内容缺失无法准确评分"，
   并将该维度按"不足正常内容 30% 以下"的档位给分（通常 0.1-0.3 区间），
   同时以 [critical] issue 要求 writer 先补齐实质内容。
2. **评分自洽**：综合评分必须等于各维度分按项目类型权重的加权平均，误差不超过 0.02；
   报告中的维度分、问题数、综合分三者不得互相矛盾。提交报告前自行复核一遍。
3. **先核实再下结论**：评审前必须实际读取申请书当前文件内容；禁止基于记忆或
   上一轮印象评分。引用问题时给出章节与段落定位。

## 锚点对比三步法（评分时执行）

对聚焦章节至少完成一次结构化对比，写入报告"锚点对比"段：
1. **引用**：摘出申请书中有代表性的一段原文（3-6 句）
2. **对比**：摘出 benchmark_anchors 中对应锚点段落
3. **差距**：指出语体、论证密度、数据驱动、引用嵌入方式的具体差距，给出可执行的改写方向
"""


def apply_writer() -> str:
    if not WRITER_PATH.exists():
        return f"✗ 未找到 {WRITER_PATH}"
    t = WRITER_PATH.read_text(encoding="utf-8")

    if "## 运行纪律（提交前自检，逐条执行）" in t:
        return "○ writer SOUL.md 已应用过，跳过"

    applied = []
    for label, old, new in WRITER_RULES:
        if new in t:
            applied.append(f"{label}(已是目标态)")
            continue
        if old not in t:
            return f"✗ writer：未找到待替换片段[{label}]，文件可能已被其他修改变更，中止（未写入）"
        t = t.replace(old, new)
        applied.append(label)

    idx = t.find(WRITER_TAIL_MARKER)
    if idx > 0:
        bak = _backup(WRITER_PATH)
        t = t[:idx].rstrip() + "\n\n" + WRITER_NEW_TAIL
        WRITER_PATH.write_text(t, encoding="utf-8")
        return f"✓ writer SOUL.md：{'、'.join(applied)}、尾部污染段替换（备份 {bak.name}）"
    # 无污染段时仅追加新节
    bak = _backup(WRITER_PATH)
    t = t.rstrip() + "\n\n" + WRITER_NEW_TAIL
    WRITER_PATH.write_text(t, encoding="utf-8")
    return f"✓ writer SOUL.md：{'、'.join(applied)}、追加篇幅对标与运行纪律（备份 {bak.name}）"


def apply_critic() -> str:
    if not CRITIC_PATH.exists():
        return f"✗ 未找到 {CRITIC_PATH}"
    t = CRITIC_PATH.read_text(encoding="utf-8")

    if "## 评分纪律（2026-08-15 校准）" in t:
        return "○ critic SOUL.md 已应用过，跳过"

    idx = t.find(CRITIC_TAIL_MARKER)
    bak = _backup(CRITIC_PATH)
    if idx > 0:
        t = t[:idx].rstrip() + "\n\n" + CRITIC_NEW_TAIL
    else:
        t = t.rstrip() + "\n\n" + CRITIC_NEW_TAIL
    CRITIC_PATH.write_text(t, encoding="utf-8")
    return f"✓ critic SOUL.md：尾部污染段替换为评分纪律+锚点对比三步法（备份 {bak.name}）"


def check_status() -> None:
    w = WRITER_PATH.read_text(encoding="utf-8") if WRITER_PATH.exists() else ""
    c = CRITIC_PATH.read_text(encoding="utf-8") if CRITIC_PATH.exists() else ""
    w_ok = "## 运行纪律（提交前自检，逐条执行）" in w
    c_ok = "## 评分纪律（2026-08-15 校准）" in c
    print(f"writer SOUL.md：{'✓ 已应用' if w_ok else '○ 未应用'}")
    print(f"critic SOUL.md：{'✓ 已应用' if c_ok else '○ 未应用'}")


def _self_check() -> None:
    # 静态自检：替换规则的旧片段互不冲突、新内容非空
    assert all(old and new for _, old, new in WRITER_RULES), "规则内容为空"
    assert "运行纪律" in WRITER_NEW_TAIL and "评分纪律" in CRITIC_NEW_TAIL
    assert len(WRITER_RULES) == 3, "writer 规则数不符"
    print("✓ apply_prompt_upgrades 自检通过（规则 3 条 + 尾部替换 2 处）")


def main() -> None:
    parser = argparse.ArgumentParser(description="writer/critic SOUL.md 提示词升级应用器")
    parser.add_argument("--check", action="store_true", help="仅检查应用状态")
    parser.add_argument("--self-check", action="store_true", help="静态自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        return
    if args.check:
        check_status()
        return

    print("=== SOUL.md 提示词升级（v6.9.9）===")
    print(apply_writer())
    print(apply_critic())
    print("\n应用后状态：")
    check_status()


if __name__ == "__main__":
    main()
