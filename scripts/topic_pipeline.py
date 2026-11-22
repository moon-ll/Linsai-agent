#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""课题启动包管线（v8）——CLI shim（薄壳，实现在 topic_pipeline 包 cli.py）。

作为脚本直接运行时加载 scripts/topic_pipeline/ 包；import topic_pipeline
时 Python 解析到同名包（package 优先于模块，与 proposal_lifecycle 同模式）。

用法示例：
    python3 scripts/topic_pipeline.py --list
    python3 scripts/topic_pipeline.py --daily
"""
from topic_pipeline.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
