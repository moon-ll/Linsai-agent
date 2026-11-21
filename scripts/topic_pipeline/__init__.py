# -*- coding: utf-8 -*-
"""课题启动包管线（v8 工作台核心）。

v8.0.0（用户裁决 2026-11-16）：全自动化产出的目标定位为课题启动包——
文献阅读发掘科学问题 → 单遍深度研究探索方案 → 整合参考文献与课题报告。
设计文档：docs/WORKBENCH-ARCHITECTURE.md。

子模块：
    constants     常量与路径
    similarity    零 LLM 相似度（A2 新颖性硬门）
    state         轻量状态总线 _topics.json
    card          课题卡渲染/解析
    registration  问题候选注册
    hermes_runner hermes oneshot 执行器（API 错误检测 + 计量入账）
    deep_research 单遍深度研究（B1 背景 → B2 问题 → B3 方案）
    assemble      B4 启动包集成（零 LLM）
    acceptance    验收自检（A1-A4 + G1-G2）
    migration     v7 存量迁移
    daily         每日深研调度
    cron          v8 cron 安装
    weekend_bridge 周末输入链桥接
    cli           命令行入口
"""
