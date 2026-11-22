#!/usr/bin/env python3
"""setup_zcode_cron.py — 注册 lc-zcode-worker 每 2 小时（v7.2.44）。

接 P0-1 ZCode worker：scripts/zcode_worker.py 消费 distill/concepts/
methods 三个 worklist。调度沿革：
  - v7.2.32：每日 21:00（错峰保守档，每晚 15 条）
  - v7.2.34：修 CLI 参数（--consume all → consume all，argparse 子命令）
  - v7.2.43：methods 语义对齐后三通道首次全绿
  - v7.2.44（用户裁决 2026-10-24「每两小时跑吧」）：0 */2 * * *——
    每天 12 跑 × 15 条 ≈ 180 条/天，279 条积压约 2 天清完。
    夜间跑反而占优（微调度器非工作时段不派发，LLM 空闲）；
    与蒸馏 cron（12:40/12:50/18:50/02:50）整点/半点错开。
"""
import sys
from pathlib import Path

ROOT = Path("/Users/ll/Desktop/LinSai-CoPilot")
HERMES_SCRIPTS = Path.home() / ".hermes" / "profiles" / "linsai" / "scripts"
HERMES_SCRIPTS.mkdir(parents=True, exist_ok=True)

# 0. 清理旧 cron（同名重建，幂等）
sys.path.insert(0, str(ROOT / "scripts"))
import hermes_bridge as hb
for c in hb.cron_list():
    if c.get("name") == "lc-zcode-worker":
        hb.cron_delete(c.get("id"), profile="linsai")
        print(f"✓ 删除旧 cron: {c.get('id')}")

# 1. 写 wrapper
wrapper = HERMES_SCRIPTS / "lc_zcode_worker.sh"
wrapper.write_text(f"""#!/bin/bash
set -e
cd {ROOT}
python3 scripts/zcode_worker.py consume all --batch 5 >> logs/zcode-worker.log 2>&1
""", encoding="utf-8")
wrapper.chmod(0o755)
print(f"✓ Wrapper: {wrapper}")

# 2. 注册 cron（每 2 小时）
result = hb.cron_create_no_agent(
    script_name="lc_zcode_worker.sh",
    name="lc-zcode-worker",
    schedule="0 */2 * * *",
    workdir=str(ROOT),
    profile="linsai",
)
print(f"✓ Cron 注册: {result}")
