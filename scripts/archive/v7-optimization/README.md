# v7 优化环归档（v8.0.0，2026-11-16）

> 本目录存放 v7「全流程自动化优化环」专属脚本。v8 架构（用户裁决 2026-11-16）
> 将自动化产出定位为课题启动包，多轮优化/评审团/prompt 自优化/复盘等机制停用。
> **归档不删除**：需要回溯或部分复活时按模块拷回 scripts/ 即可。
> 归档清单与依据见 docs/WORKBENCH-ARCHITECTURE.md §7 与 CHANGELOG v8.0.0。
>
> 内容分组：
> - 自成长元环：self_optimizer / prompt_optimizer / apply_prompt_upgrades / retrospective /
>   stage_weekly_report / pilot_scorecard / strategy_optimizer 未归档（web 仍引用）
> - 旧交互式管线：pipeline_orchestrator / proposal_writer / proposal_inspector /
>   gap_analyzer / question_architect / topic_generator
> - v3.5 未启用课题管理：project_manager / project_context / project_kb /
>   project_memory / project_workflow / unit_manager
> - 一次性运维工具：rebuild_lifecycle / backfill_score_raw / backfill_manual_rereview /
>   restart_stalled_failed_job / promote_proposal_to_focus / cleanup_cron_duplicates /
>   fix_input_chain_data / import_hermes_topics / round_machine_time / apply_prompt_upgrades
> - 周末输出端：weekend_summary（输入端保留在 weekend_pipeline）
