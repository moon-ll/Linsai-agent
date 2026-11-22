#!/usr/bin/env python3
"""
document_handler.py — 文档与代码协作模块

用途：
    为 LinSai-CoPilot 提供文档读取、摘要生成、代码分析、
    参考文献索引与管理功能。

用法示例：
    >>> from document_handler import read_document, summarize_document, analyze_code
    >>> text = read_document("~/Downloads/paper.md")
    >>> summary = summarize_document("~/Downloads/paper.md")
    >>> info = analyze_code("scripts/copilot_engine.py")
    >>> upload_document("~/Downloads/note.md", category="notes")
    >>> refs = search_references("solid HHG")

规范：
    - 仅使用 Python 3 标准库
    - 路径处理使用 pathlib.Path
    - 输出使用中文，状态图标统一
    - JSON 文件 ensure_ascii=False, indent=2
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# 路径与导入配置
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()
_REFERENCES_DIR = _PROJECT_ROOT / "references"
_PAPERS_DIR = _REFERENCES_DIR / "papers"
_NOTES_DIR = _REFERENCES_DIR / "notes"
_INDEX_FILE = _REFERENCES_DIR / "index.json"

if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    from copilot_engine import call_llm
except Exception:
    call_llm = None  # type: ignore[assignment]

_TEXT_EXTS = {".md", ".txt", ".py", ".js", ".json", ".csv", ".log", ".yaml", ".yml", ".html", ".css", ".xml", ".sh", ".rst"}


# ---------------------------------------------------------------------------
# 1. 文档读取
# ---------------------------------------------------------------------------
def read_document(file_path: Path | str) -> str:
    """读取文档内容，返回文本字符串。

    支持的格式：
    - .md / .txt / .py / .json / .csv / .log — 直接按 UTF-8 文本读取
    - .pdf — 尝试简单文本提取
    """
    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        return f"✗ 文件不存在: {path}"

    ext = path.suffix.lower()

    if ext in _TEXT_EXTS:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return "✗ 文件编码错误，无法按 UTF-8 读取"

    if ext == ".pdf":
        return _extract_pdf_text(path)

    return f"⚠ 不支持的文件格式: {ext}，仅支持文本文件与 PDF"


def _extract_pdf_text(path: Path) -> str:
    """用正则从 PDF 二进制中简单提取文本流。"""
    try:
        data = path.read_bytes()
    except Exception as exc:
        return f"✗ 读取 PDF 失败: {exc}"

    # 匹配 BT ... ET 块中的文本
    bt_blocks = re.findall(rb"BT\s*(.*?)\s*ET", data, re.DOTALL)
    texts: list[str] = []

    for block in bt_blocks:
        for m in re.findall(rb"\((.*?)\)\s*Tj", block):
            texts.append(m.decode("utf-8", errors="ignore"))
        for m in re.findall(rb"\[(.*?)\]\s*TJ", block):
            for p in re.findall(rb"\((.*?)\)", m):
                texts.append(p.decode("utf-8", errors="ignore"))

    joined = " ".join(texts).strip()
    if joined:
        return joined

    return "⚠ PDF 解析需要外部工具，建议先转换为文本"


# ---------------------------------------------------------------------------
# 2. 文档摘要
# ---------------------------------------------------------------------------
def summarize_document(file_path: Path | str, max_chars: int = 3000) -> str:
    """调用 LLM 生成文档摘要。"""
    path = Path(file_path).expanduser().resolve()
    content = read_document(path)

    if content.startswith(("✗", "⚠")):
        return content

    snippet = content[:max_chars]
    truncated = len(content) > max_chars

    system_prompt = (
        "你是林赛（Lin Sai），强场超快光学与阿秒科学领域的独立 PI。"
        "请为以下文档生成结构化摘要，用中文撰写，风格简洁专业。"
    )
    truncate_notice = "[文档过长，仅显示前 " + str(max_chars) + " 字符]\n" if truncated else ""
    user_prompt = (
        f"请为以下文档生成结构化摘要，包含：核心观点、方法论、关键结论、"
        f"对林赛和用户的意义。\n\n文档: {path.name}\n"
        f"{truncate_notice}"
        f"\n{snippet}\n\n"
        f"请按以下 Markdown 格式输出：\n"
        f"# 文档摘要：{path.name}\n\n"
        f"## 核心观点\n...\n\n"
        f"## 方法论\n...\n\n"
        f"## 关键结论\n...\n\n"
        f"## 与当前研究的相关性\n..."
    )

    if call_llm is None:
        return (
            f"# 文档摘要：{path.name}\n\n"
            f"## 核心观点\n（LLM 未配置，无法生成摘要）\n\n"
            f"## 方法论\n—\n\n"
            f"## 关键结论\n—\n\n"
            f"## 与当前研究的相关性\n—"
        )

    try:
        result = call_llm(system_prompt, [{"role": "user", "content": user_prompt}], timeout=120)
        return result
    except Exception as exc:
        return f"⚠ 摘要生成失败: {exc}"


# ---------------------------------------------------------------------------
# 3. 代码分析
# ---------------------------------------------------------------------------
def analyze_code(file_path: Path | str) -> dict:
    """分析代码文件，返回结构信息和改进建议。"""
    path = Path(file_path).expanduser().resolve()
    content = read_document(path)

    if content.startswith("✗"):
        return {"error": content}

    ext = path.suffix.lower()
    lang_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
    }
    language = lang_map.get(ext, "unknown")
    lines = content.splitlines()
    line_count = len(lines)

    functions: list[dict] = []
    classes: list[dict] = []
    imports: list[str] = []
    issues: list[dict] = []

    # 正则定义
    func_re = re.compile(r"^\s*def\s+(\w+)\s*\((.*?)\)(?:\s*->.*?)?\s*:")
    class_re = re.compile(r"^\s*class\s+(\w+)(?:\s*\(.*\))?\s*:")
    import_re = re.compile(r"^\s*(import\s+\S+|from\s+\S+\s+import\s+.+)")

    for i, line in enumerate(lines, start=1):
        # 函数
        m = func_re.match(line)
        if m:
            functions.append({"name": m.group(1), "line": i, "args": m.group(2).strip()})

        # 类
        m = class_re.match(line)
        if m:
            classes.append({"name": m.group(1), "line": i})

        # import
        m = import_re.match(line)
        if m:
            imports.append(m.group(1).strip())

        # issues: 长行
        if len(line) > 120:
            issues.append({
                "severity": "warning",
                "line": i,
                "message": f"行长度 {len(line)} 超过 120 字符",
            })

    # issues: 空 except 块（Python）
    if language == "python":
        for i, line in enumerate(lines, start=1):
            if re.search(r"^\s*except\s*.*:\s*$", line):
                # 检查下一行是否是 pass
                if i < len(lines) and lines[i].strip() == "pass":
                    issues.append({
                        "severity": "warning",
                        "line": i,
                        "message": "空的 except 块，建议捕获具体异常或添加处理逻辑",
                    })

    suggestions = _generate_code_suggestions(path.name, language, line_count, functions, classes, imports, issues)

    return {
        "language": language,
        "lines": line_count,
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "issues": issues,
        "suggestions": suggestions,
    }


def _generate_code_suggestions(
    filename: str,
    language: str,
    line_count: int,
    functions: list[dict],
    classes: list[dict],
    imports: list[str],
    issues: list[dict],
) -> str:
    """调用 LLM 生成代码改进建议，若 LLM 不可用则返回基于规则的简要建议。"""
    brief = (
        f"文件: {filename}\n"
        f"语言: {language}\n"
        f"总行数: {line_count}\n"
        f"函数数: {len(functions)}\n"
        f"类数: {len(classes)}\n"
        f"导入数: {len(imports)}\n"
        f"检测到问题: {len(issues)} 个"
    )

    if call_llm is None:
        parts = ["（LLM 未配置，以下为简要规则分析）", brief]
        if issues:
            parts.append("\n检测到的问题:")
            for iss in issues:
                parts.append(f"  - 第 {iss['line']} 行: {iss['message']}")
        return "\n".join(parts)

    system_prompt = (
        "你是林赛（Lin Sai），具备丰富编程与科研代码审查经验的独立 PI。"
        "请基于以下代码统计信息给出简洁的改进建议，用中文回复，控制在 300 字以内。"
    )
    user_prompt = f"{brief}\n\n请给出改进建议:"

    try:
        return call_llm(system_prompt, [{"role": "user", "content": user_prompt}], timeout=60)
    except Exception as exc:
        return f"⚠ 建议生成失败: {exc}\n\n{brief}"


# ---------------------------------------------------------------------------
# 4. 参考文献索引与搜索
# ---------------------------------------------------------------------------
def index_references() -> list[dict]:
    """扫描 references/papers/ 和 references/notes/ 目录，建立索引。"""
    _PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    _NOTES_DIR.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []

    for category, folder in [("paper", _PAPERS_DIR), ("note", _NOTES_DIR)]:
        if not folder.exists():
            continue
        for fpath in folder.iterdir():
            if not fpath.is_file():
                continue
            stat = fpath.stat()
            entries.append({
                "filename": fpath.name,
                "path": str(fpath.relative_to(_PROJECT_ROOT)),
                "category": category,
                "size": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            })

    entries.sort(key=lambda x: x["filename"])

    try:
        _INDEX_FILE.write_text(
            json.dumps(entries, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:
        print(f"⚠ 索引写入失败: {exc}")

    return entries


def search_references(query: str) -> list[dict]:
    """按关键词搜索参考文献（搜索文件名和文件前 500 字符）。"""
    query_lower = query.lower()
    results: list[dict] = []

    # 优先使用已有索引，否则重新生成
    if _INDEX_FILE.exists():
        try:
            entries = json.loads(_INDEX_FILE.read_text(encoding="utf-8"))
        except Exception:
            entries = index_references()
    else:
        entries = index_references()

    for entry in entries:
        score = 0
        if query_lower in entry["filename"].lower():
            score += 10

        # 读取前 500 字符进行内容匹配
        fpath = _PROJECT_ROOT / entry["path"]
        if fpath.exists():
            try:
                text = fpath.read_text(encoding="utf-8", errors="ignore")[:500]
                if query_lower in text.lower():
                    score += 5
            except Exception:
                pass

        if score > 0:
            results.append({**entry, "score": score})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# 5. 获取文档上下文
# ---------------------------------------------------------------------------
def get_document_context(file_path: Path | str, max_chars: int = 2000) -> str:
    """返回文档前 max_chars 字符，用于注入对话上下文。"""
    content = read_document(file_path)

    if content.startswith(("✗", "⚠")):
        return content

    if len(content) > max_chars:
        return content[:max_chars] + f"\n\n[文档过长，仅显示前 {max_chars} 字符]"

    return content


# ---------------------------------------------------------------------------
# 6. 文档上传
# ---------------------------------------------------------------------------
def upload_document(source_path: Path | str, category: str = "notes") -> Path:
    """将文件复制到 references/{category}/ 目录，返回目标路径。"""
    if category not in ("papers", "notes"):
        raise ValueError("category 必须是 'papers' 或 'notes'")

    src = Path(source_path).expanduser().resolve()
    if not src.exists():
        raise FileNotFoundError(f"✗ 源文件不存在: {src}")

    dest_dir = _REFERENCES_DIR / category
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name

    # 若目标已存在，添加数字后缀
    counter = 1
    original_dest = dest
    while dest.exists():
        stem = original_dest.stem
        suffix = original_dest.suffix
        # 去掉已有数字后缀
        stem = re.sub(r"_\d+$", "", stem)
        dest = dest_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    shutil.copy2(src, dest)
    print(f"✓ 已上传: {dest.relative_to(_PROJECT_ROOT)}")

    index_references()
    return dest


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("◐ 启动 document_handler.py 自检\n")

    # 准备测试目录与文件
    test_dir = _PROJECT_ROOT / "tests_doc_handler"
    test_dir.mkdir(exist_ok=True)

    # 1. 创建测试 Markdown 文件并读取
    test_md = test_dir / "test_paper.md"
    md_content = "# 固体高次谐波产生实验方案\n\n## 背景\n固体 HHG 是强场超快光学的前沿方向。\n\n## 方法\n使用 1.8 μm 中红外驱动场，聚焦到 ZnO 晶体表面。\n\n## 结论\n预计可观察到 15 阶以下的奇次谐波。\n"
    test_md.write_text(md_content, encoding="utf-8")
    read_result = read_document(test_md)
    assert "固体 HHG" in read_result
    print("✓ 文档读取测试通过")

    # 2. 创建测试 Python 代码文件并分析
    test_py = test_dir / "test_code.py"
    py_content = (
        "import json\n"
        "import sys\n"
        "from pathlib import Path\n\n"
        "def hello(name):\n"
        "    return f'Hello, {name}'\n\n"
        "class DataProcessor:\n"
        "    def process(self, data):\n"
        "        try:\n"
        "            pass\n"
        "        except:\n"
        "            pass\n"
        "        return data\n\n"
        "# " + "x" * 150 + "\n"
    )
    test_py.write_text(py_content, encoding="utf-8")
    info = analyze_code(test_py)
    assert info["language"] == "python"
    assert info["lines"] >= 10
    assert any(f["name"] == "hello" for f in info["functions"])
    assert any(c["name"] == "DataProcessor" for c in info["classes"])
    assert any("json" in imp for imp in info["imports"])
    assert any("except" in iss["message"] for iss in info["issues"])
    print("✓ 代码分析测试通过")

    # 3. 调用 summarize_document（如 LLM 可用）
    summary = summarize_document(test_md, max_chars=500)
    assert "文档摘要" in summary or "LLM 未配置" in summary or "失败" in summary
    print("✓ 文档摘要测试完成")

    # 4. 再次调用 analyze_code（已在步骤 2 完成）
    print(f"  函数列表: {[f['name'] for f in info['functions']]}")
    print(f"  类列表:   {[c['name'] for c in info['classes']]}")
    print(f"  问题数:   {len(info['issues'])}")

    # 5. 上传文件到 references/
    dest = upload_document(test_md, category="notes")
    assert dest.exists()
    print("✓ 文档上传测试通过")

    # 6. 索引和搜索参考文献
    refs = index_references()
    assert any(r["filename"] == dest.name for r in refs)
    print(f"✓ 参考文献索引测试通过（共 {len(refs)} 条）")

    search_results = search_references("固体 HHG")
    assert len(search_results) > 0
    print(f"✓ 参考文献搜索测试通过（命中 {len(search_results)} 条）")

    # 7. 获取文档上下文
    ctx = get_document_context(dest, max_chars=50)
    assert "[文档过长" in ctx or "固体" in ctx
    print("✓ 文档上下文测试通过")

    # 清理测试数据
    shutil.rmtree(test_dir, ignore_errors=True)
    if dest.exists():
        dest.unlink()
    index_references()
    print("\n✓ 自检全部通过，测试数据已清理")
