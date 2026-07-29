#!/usr/bin/env python3
"""周末任务流水线入口脚本。

等价于 python3 -m weekend_pipeline.cli，但可直接作为脚本被 hermes cron 调用。
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from weekend_pipeline.cli import main

if __name__ == "__main__":
    sys.exit(main())
