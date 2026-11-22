#!/usr/bin/env python3
"""setup_retrospective_cron.py — 注册 lc-retrospective 周复盘 cron（v7.2.32）。

背景：retrospective 8-31 后无产物（1.5 月停摆）。CHANGELOG 描述"周一 15:00
lc-retrospective"但实际从未注册到 hermes profile。本脚本：
  1. 创建 wrapper 脚本 ~/.hermes/profiles/linsai/scripts/lc_retrospective.sh
  2. 调 hermes_bridge.cron_create_no_agent 注册 "0 15 * * 1" 周一 15:00
  3. 跑一次确认手动执行无错
"""
import sys
from pathlib import Path

ROOT = Path("/Users/ll/Desktop/LinSai-CoPilot")
HERMES_SCRIPTS = Path.home() / ".hermes" / "profiles" / "linsai" / "scripts"
HERMES_SCRIPTS.mkdir(parents=True, exist_ok=True)

# 1. 写 wrapper 脚本
wrapper = HERMES_SCRIPTS / "lc_retrospective.sh"
wrapper.write_text(f"""#!/bin/bash
set -e
cd {ROOT}
python3 scripts/retrospective.py --period 7d >> logs/retrospective.log 2>&1
""", encoding="utf-8")
wrapper.chmod(0o755)
print(f"✓ Wrapper: {wrapper}")

# 2. 注册 cron
sys.path.insert(0, str(ROOT / "scripts"))
import hermes_bridge as hb
result = hb.cron_create_no_agent(
    script_name="lc_retrospective.sh",
    name="lc-retrospective",
    schedule="0 15 * * 1",  # 周一 15:00
    workdir=str(ROOT),
    profile="linsai",
)
print(f"✓ Cron 注册: {result}")
