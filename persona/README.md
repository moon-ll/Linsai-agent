# persona/ — 林赛人格资产

本目录存放林赛的人格注入材料，供 `copilot_engine.py` 在构建 prompt 时使用。

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `lin-sai-persona.md` | **主注入文件**。整合精简版人格画像，包含身份卡、心智模型、决策启发式、表达 DNA、工作模式、AI 协作哲学。供 prompt 直接引用。 |
| `source-manifest.json` | 来源追踪。记录本目录内容复制自 virtu-LinSai 的版本和日期。 |
| `README.md` | 本文件。 |

---

## 资产来源

所有内容源自 `~/Desktop/hermes_workspace/sandbox/virtu-LinSai/`：

| 源文件 | 源路径 |
|--------|--------|
| SOUL.md | `EXTRAITS/SKILL-blueprints/SOUL.md` |
| SKILL.md | `EXTRAITS/SKILL-blueprints/SKILL.md` |
| WORKSTYLE.md | `EXTRAITS/SKILL-blueprints/WORKSTYLE.md` |
| 林赛-perspective | `.kimi/skills/林赛-perspective/SKILL.md` |
| ai-collaboration | `PERSONA/ai-collaboration.md` |

---

## 更新规范

1. **单向同步**：只从 virtu-LinSai 复制到本项目，**禁止反向修改**。
2. **版本锁定**：`source-manifest.json` 记录当前同步的 virtu-LinSai 版本号。
3. **更新流程**：
   - 检查上游 `virtu-LinSai/CHANGELOG.md` 是否有 PERSONA/EXTRAITS 相关更新
   - 如有更新，手动复制相关文件到 `persona/`
   - 更新 `source-manifest.json`
   - 更新 `lin-sai-persona.md` 整合文件
   - 在 `../CHANGELOG.md` 中记录变更

---

## 使用方式

`copilot_engine.py` 在调用 LLM 时，将 `lin-sai-persona.md` 的内容作为 system prompt 注入：

```python
with open(PROJECT_ROOT / "persona" / "lin-sai-persona.md", "r", encoding="utf-8") as f:
    persona = f.read()

system_prompt = f"""你现在是林赛（Lin Sai）。以下是你的人格设定：

{persona}

请以林赛的身份和风格回应用户。记住：你是用户的合作者，不是旁观者。"""
```

---

*版本：1.0*
*日期：2026-05-08*
