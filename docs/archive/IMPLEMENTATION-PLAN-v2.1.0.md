# Lin Sai 工具协作者 — 实现计划 v1.0

> **版本**: v1.0
> **日期**: 2026-05-15
> **核心理念**: Lin Sai 应该像用户使用 AI 一样工作——把任务委托给擅长的 AI 工具，而不是自己硬扛
> **改进说明**: 计划精简，时间估算参考实际开发速度，每步可独立验证

---

## 一、问题与解决方案

### 现状

```
Lin Sai 能做的：查文件、做计算、创建任务、查知识库
Lin Sai 不能做的：执行 kimi 命令、运行 Claude CLI、读 hermes 结果

根本原因：tool_engine.py 的工具列表里没有 subprocess/shell 调用能力
```

### 解决方案

```
用户 → Lin Sai → [run_command: "kimi code 生成XXX"]
                  [run_command: "claude --print 分析XXX"]
                  [run_command: "hermes 咨询XXX"]
                  → 整合结果 → 汇报
```

### 底层能力盘点

| 能力 | 状态 |
|------|------|
| subprocess 调用 CLI | ✅ 已有（llm_router.py 在用） |
| 工具解析框架 | ✅ 已有（@@tool:name@@） |
| 工具执行循环 | ✅ 已有（copilot_engine.py 在用） |
| system_prompt 注入 | ✅ 已有（inject_tools_prompt()） |
| kimi / claude / hermes | ✅ 均已安装，在 PATH |

**只需加一个工具，整个链路就能跑通。**

---

## 二、阶段划分

```
v2.0.0  (当前)
│
├─ v2.1.0 [Phase 0]  ★ 本次实现
│    Lin Sai 获得 CLI 调用能力
│    改动：1 个新工具文件
│
├─ v2.2.0 [Phase 1]
│    Lin Sai 能调用子代理（Agent 工具）
│    改动：扩展工具注册表
│
├─ v2.3.0 [Phase 2]
│    Lin Sai 能执行 Python 程序（数据分析）
│    改动：执行用户指定的 Python 脚本
│
└─ v3.0.0 [Phase 3]
     完整研究流程：调研→分析→报告
     （届时根据 Phase 0-2 的实际使用情况再细化）
```

---

## 三、Phase 0 — CLI 调用能力（v2.1.0）

### 目标

Lin Sai 在对话中说"我来调用 kimi/claude/hermes"，然后实际执行，返回结果。

### 实现方案

**改动文件数量：1 个**（只需扩展 `tool_engine.py`）

```
scripts/tool_engine.py
│
├── 新增工具（3 个）
│   ├── tool_run_command(cmd, timeout, cwd)
│   │   用途：执行任意 CLI 命令（kimi / claude / hermes / python / git 等）
│   │   安全：cwd 限制在项目目录，timeout 防止阻塞，危险命令黑名单
│   │
│   ├── tool_read_file(path)
│   │   用途：读取文件（整合现有 file_read，移除路径白名单限制）
│   │
│   └── tool_write_file(path, content)
│       用途：写入文件
│
└── inject_tools_prompt() 更新
    新增 run_command 的描述，告诉 Lin Sai 可以调用 CLI
```

### 核心实现细节

```python
# tool_engine.py 新增

# 黑名单：危险命令
_BLOCKED = {"rm -rf /", "sudo", "dd if=", "mkfs", ":(){ :|:& };:", "curl.*--silent.*password"}

def tool_run_command(command: str, timeout: int = 60, cwd: str = "") -> str:
    """执行 CLI 命令。"""
    import subprocess

    # 安全检查
    for bad in _BLOCKED:
        if bad in command:
            return f"✗ 危险命令: {bad}"

    # cwd 限制
    if cwd:
        target_cwd = (Path(__file__).parent.parent / cwd).resolve()
        if not str(target_cwd).startswith(str(PROJECT_ROOT)):
            return "✗ 路径越界"
    else:
        target_cwd = PROJECT_ROOT

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(target_cwd),
        )
        output = result.stdout + result.stderr
        if len(output) > 10000:
            output = output[:10000] + f"\n... (截断，共 {len(output)} 字符)"
        return output if output else "(无输出)"
    except subprocess.TimeoutExpired:
        return f"✗ 命令超时（{timeout}s）"
    except Exception as e:
        return f"✗ 执行失败: {e}"
```

### 工具描述注入（inject_tools_prompt）

```python
TOOL_DESCRIPTIONS = {
    "run_command": """
run_command — 执行 CLI 命令（调用 kimi / claude / hermes / python / git 等）
参数: {"command": "命令字符串", "timeout": 60, "cwd": ""}
示例: {"command": "kimi code 生成斐波那契数列", "timeout": 30}
示例: {"command": "claude --print --model opus '解释薛定谔方程'"}
示例: {"command": "python3 scripts/my_analysis.py", "cwd": "."}
规则：
- 复杂任务优先使用 run_command，而不是自己硬扛
- kimi：适合代码生成、文件处理
- claude：适合代码审查、分析、解释
- hermes：适合闲聊、想法梳理
- timeout 默认 60s，超时自动终止
- cwd 默认不填，在项目根目录执行
""",
    # file_read / file_write 保持不变
}
```

### 验证方式

```
Phase 0 完成标志：

1. Lin Sai 能执行命令
   用户："帮我用 kimi 生成一个斐波那契函数"
   Lin Sai 输出包含 @@tool:run_command@@
   执行后返回 kimi 的结果

2. Lin Sai 能整合结果
   同样的对话，Lin Sai 基于 kimi 结果给出最终回复

3. 不破坏现有功能
   self_test.py 88/88 仍通过
```

---

## 四、Phase 1 — 子代理调用（v2.2.0）

### 目标

Lin Sai 能调用 `Agent` 工具，委托子代理完成深度调研，然后把结果整合汇报。

### 场景示例

```
用户："帮我调研一下拓扑绝缘体的表面态探测进展"

Lin Sai：
"我来并行调研三个方向：① 文献搜索 ② 知识库检索 ③ 最新 arXiv"
→ 调用 Agent（kimi 子代理）：搜索 arXiv 论文
→ 调用 Agent（claude 子代理）：分析拓扑绝缘体探测方法
→ 调用 knowledge_query：检查现有笔记
→ 整合三方结果，写成调研摘要
```

### 实现方案

**改动：1 个工具注册（`tool_engine.py`）+ prompt 更新**

```python
# tool_engine.py 新增

def tool_agent(task: str, agent_type: str = "coder", model: str = "") -> str:
    """调用子代理完成特定任务。"""
    try:
        from pathlib import Path
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from copilot_engine import Agent

        result = Agent(
            description=task[:100],
            prompt=task,
            subagent_type=agent_type,
            model=model or None,
        )
        return str(result)[:8000]
    except Exception as e:
        return f"✗ 子代理调用失败: {e}"
```

### 验证方式

```
Phase 1 完成标志：

用户："帮我用费曼的视角思考一下量子隧穿"
Lin Sai 调用费曼-perspective 子代理
返回结果被林赛整合（带林赛自己的判断）
```

---

## 五、Phase 2 — Python 程序执行（v2.3.0）

### 目标

Lin Sai 能执行用户指定的 Python 程序（数据分析、数值模拟），返回结果，写入报告。

### 场景示例

```
用户："帮我跑一下 scripts/hhg_simulation.py，参数用 default"

Lin Sai：
→ [run_command: "python3 scripts/hhg_simulation.py --preset default"]
→ 读取输出结果
→ 判断是否成功
→ 如有异常，调用 calc 工具验证关键数值
→ 写入 results/hhg-sim-20260515.md
→ 汇报："模拟成功，截止频率为 45.2 eV，结果已保存"
```

### 实现方案

**改动：扩展 `run_command` 的使用说明 + 新增安全执行模板**

不需要新增 Python 执行专用工具，`run_command` 已经覆盖。主要补充：
- 告诉 Lin Sai 如何组织 `python3 script.py [args]` 命令
- 提供结果解析和写入报告的工作流模板

### 验证方式

```
Phase 2 完成标志：

用户："帮我跑一个测试"
Lin Sai 执行 scripts/self_test.py
返回测试结果摘要
写入 memory/test-result-20260515.md
```

---

## 六、Phase 3 — 完整研究流程（v3.0.0）

**暂不细化。** 等 Phase 0-2 稳定运行后，根据实际使用中发现的需求再设计。

---

## 七、执行顺序

```
现在        →  做 Phase 0（加 1 个工具）
Phase 0 后  →  一起讨论 Phase 1（子代理）
Phase 1 后  →  一起讨论 Phase 2（程序执行）
Phase 0-2  →  评估 Phase 3 需求
```

---

## 八、风险与缓解

| 风险 | 级别 | 缓解 |
|------|------|------|
| 执行危险命令 | 中 | 黑名单 + timeout + cwd 限制 |
| Lin Sai 过度依赖工具 | 低 | Lin Sai 有 system prompt，知道何时该自己答何时该调用 |
| 命令输出过长刷屏 | 低 | 截断 + 分段返回 |
| 阻塞等待时间过长 | 低 | timeout 保护，Lin Sai 可见进度 |

---

## 九、已确认决策

| # | 问题 | 决策 |
|---|------|------|
| Q1 | Phase 0 改动范围 | 最小化：只改 1 个文件（tool_engine.py） |
| Q2 | Phase 0 验证方式 | 端到端对话测试，不写额外测试文件 |
| Q3 | Phase 1-3 | 按需讨论，不提前细化 |

---

*本计划版本：v1.0*
*创建日期：2026-05-15*
*核心原则：最小可行改动，每步可验证，稳健推进*
