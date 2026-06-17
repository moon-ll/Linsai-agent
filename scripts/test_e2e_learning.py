#!/usr/bin/env python3
"""
端到端学习周期验证脚本

验证链路：arXiv 获取 → prompt 构建 → LLM 蒸馏 → wiki 保存 → 来源链接检查

用法：python3 scripts/test_e2e_learning.py
"""

import sys
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from external_fetcher import fetch_arxiv

WIKI_DIR = PROJECT_ROOT / "knowledge" / "wiki"
WIKI_DIR.mkdir(parents=True, exist_ok=True)


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _extract_wiki_content(raw_text: str) -> str:
    """从 LLM 输出中提取 wiki markdown 内容（处理代码块包裹）。"""
    raw_text = raw_text.strip()

    # 尝试提取 ```markdown ... ``` 代码块
    md_block = re.search(r'```markdown\s*\n(.*?)\n```', raw_text, re.DOTALL)
    if md_block:
        return md_block.group(1).strip()

    # 尝试提取 ``` ... ``` 代码块（无 markdown 标记）
    code_block = re.search(r'```\s*\n(.*?)\n```', raw_text, re.DOTALL)
    if code_block:
        content = code_block.group(1).strip()
        # 确保内容以 --- 开头（YAML frontmatter）
        if content.startswith("---"):
            return content

    # 如果全文以 --- 开头，直接返回
    if raw_text.startswith("---"):
        return raw_text

    # 否则尝试找到第一个 --- 的位置
    first_fm = raw_text.find("---")
    if first_fm >= 0:
        return raw_text[first_fm:]

    return raw_text


def verify_arxiv_source_links():
    """验证 arXiv 论文蒸馏后的来源链接注入。"""
    print("=" * 60)
    print("端到端学习链路验证")
    print("=" * 60)

    # Step 1: 获取 arXiv 论文
    print("\n[1/5] 获取 arXiv 论文...")
    papers = fetch_arxiv("quantum optics", max_results=5)
    if not papers:
        print("  ✗ 无法获取 arXiv 论文")
        return False
    paper = papers[0]
    arxiv_id = paper.get("arxiv_id", "")
    title = paper.get("title", "")
    print(f"  ✓ 获取论文: {title[:60]}...")
    print(f"    arXiv ID: {arxiv_id}")

    # Step 2: 构建 prompt
    print("\n[2/5] 构建蒸馏 prompt...")
    abstract = paper.get("abstract", "")
    tldr = paper.get("tldr", "")
    authors = ", ".join(paper.get("authors", [])[:5])
    date = paper.get("date", "")
    pdf_url = paper.get("url", f"https://arxiv.org/pdf/{arxiv_id}")

    wiki_template = f"""---
title: "{title}"
type: papers
created: "{_now_utc()}"
updated: "{_now_utc()}"
tags: ["文献", "auto-grown"]
related: []
source_arxiv: "{arxiv_id}"
authors: "{authors}"
published: "{date}"
growth_stage: "growing"
confidence: 0.7
auto_grown: true
review_status: "pending"
---

# {title}

## 林赛的理解
（用第一人称，体现你作为强场超快光学 PI 的视角。这篇论文和你的研究有什么关联？）

## 核心发现
（论文最重要的 2-3 个发现）

## 方法亮点
（实验或理论方法上的创新点）

## 与林赛工作的关联
（这篇论文如何启发或补充你的研究？）

## 批判性思考
（论文的局限性、你怀疑的地方、想进一步验证的问题）

## 实验参数备忘
（如果有具体参数，记录下来）

## 开放问题
（这篇论文引出的你感兴趣的问题）

## 来源
- arXiv 原文：[{arxiv_id}]({pdf_url})
- 检索时间：{_now_utc()}"""

    prompt = f"""你是一位强场超快光学独立 PI（林赛），正在阅读一篇最新的 arXiv 论文。

请基于以下论文信息，撰写一篇林赛视角的精读笔记。

论文信息：
- 标题：{title}
- 作者：{authors}
- arXiv ID：{arxiv_id}
- 发表日期：{date}
- 摘要：{abstract[:2000]}
- TLDR：{tldr[:1000]}
- PDF 链接：{pdf_url}

请严格按照以下模板格式输出 wiki 页面，填充每个章节的具体内容。

【极其重要】输出要求：
1. 直接输出 markdown 原文，不要加任何代码块标记（如 ```markdown）
2. 不要添加任何解释性文字、文件路径建议或操作说明
3. 输出必须从 ---（YAML frontmatter 开始）到文件末尾的 ## 来源 章节结束
4. 保留所有 frontmatter 字段，包括 source_arxiv、auto_grown、review_status 等

模板：

{wiki_template}
"""

    # 检查 prompt 是否包含来源要求
    assert "## 来源" in prompt, "prompt 中缺少 ## 来源 章节"
    assert "source_arxiv" in prompt, "prompt 中缺少 source_arxiv frontmatter"
    assert pdf_url in prompt, "prompt 中缺少 PDF 链接"
    print("  ✓ Prompt 构建正确，包含来源链接要求")

    # Step 3: 调用 Claude CLI 蒸馏
    print("\n[3/5] 调用 Claude CLI 进行蒸馏...")
    system_prompt = (
        "你是一位强场超快光学独立 PI（林赛）。"
        "请根据用户提供的论文信息，撰写一篇林赛视角的精读 wiki 笔记。"
        "保持第一人称，体现科研品味和批判性思维。"
        "严格按照用户提供的模板格式输出。"
        "只输出纯 markdown 文本，不要加代码块包裹，不要加任何解释性文字。"
    )

    full_prompt = f"System: {system_prompt}\n\nHuman: {prompt}\n\nAssistant:"

    cmd = ["claude", "-p", "--output-format", "text", full_prompt]
    print(f"    调用: claude -p (prompt 长度 {len(full_prompt)} 字符)...")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode != 0:
            print(f"  ✗ Claude CLI 错误: {result.stderr}")
            return False
        raw_output = result.stdout.strip()
    except subprocess.TimeoutExpired:
        print("  ✗ Claude CLI 超时 (>180s)")
        return False
    except Exception as e:
        print(f"  ✗ Claude CLI 异常: {e}")
        return False

    # 提取 wiki 内容（处理代码块包裹）
    wiki_text = _extract_wiki_content(raw_output)
    wiki_lines = wiki_text.count("\n")
    print(f"  ✓ Claude 返回 {raw_output.count(chr(10))} 行原始输出")
    print(f"  ✓ 提取 wiki 内容 {wiki_lines} 行, {len(wiki_text)} 字符")

    # Step 4: 保存 wiki 文件
    print("\n[4/5] 保存 wiki 文件...")
    safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(" ", "-")[:50]
    wiki_path = WIKI_DIR / "papers" / f"{arxiv_id}-{safe_title}.md"
    wiki_path.parent.mkdir(parents=True, exist_ok=True)
    wiki_path.write_text(wiki_text, encoding="utf-8")
    print(f"  ✓ 保存到: {wiki_path.relative_to(PROJECT_ROOT)}")

    # Step 5: 验证来源链接
    print("\n[5/5] 验证来源链接注入...")
    checks = []

    # 5a: YAML frontmatter 中有 source_arxiv
    fm_match = re.search(r'^---\s*\n(.*?)\n---', wiki_text, re.DOTALL)
    if fm_match:
        frontmatter = fm_match.group(1)
        has_source_arxiv = "source_arxiv" in frontmatter
        checks.append(("frontmatter source_arxiv", has_source_arxiv))
        if has_source_arxiv:
            val = re.search(r'source_arxiv:\s*"?([^"\n]+)"?', frontmatter)
            if val:
                print(f"  ✓ frontmatter source_arxiv = {val.group(1).strip()}")
    else:
        checks.append(("frontmatter source_arxiv", False))
        print("  ✗ 未检测到 YAML frontmatter")

    # 5b: 正文中有 ## 来源 章节
    has_source_section = "## 来源" in wiki_text
    checks.append(("正文 ## 来源 章节", has_source_section))
    if has_source_section:
        print(f"  ✓ 正文包含 ## 来源 章节")
        # 检查章节内容
        section_match = re.search(r'## 来源\s*\n(.*?)(?=\n## |\Z)', wiki_text, re.DOTALL)
        if section_match:
            section_content = section_match.group(1).strip()
            print(f"    内容预览: {section_content[:120]}...")
    else:
        print(f"  ✗ 正文缺少 ## 来源 章节")

    # 5c: 有 arXiv PDF 链接
    has_pdf_link = f"arxiv.org/pdf/{arxiv_id}" in wiki_text or f"arxiv.org/abs/{arxiv_id}" in wiki_text
    checks.append(("arXiv 链接", has_pdf_link))
    if has_pdf_link:
        print(f"  ✓ 包含 arXiv 链接")
    else:
        print(f"  ✗ 缺少 arXiv 链接")

    # 5d: 有 auto_grown 标记
    has_auto_grown = "auto_grown: true" in wiki_text or "auto_grown:true" in wiki_text.replace(" ", "")
    checks.append(("auto_grown 标记", has_auto_grown))
    if has_auto_grown:
        print(f"  ✓ 包含 auto_grown: true 标记")

    # 5e: review_status 标记（容忍引号变异如 "pending"）
    has_pending = bool(re.search(r'review_status:\s*"?pending"?', wiki_text))
    checks.append(("review_status: pending", has_pending))
    if has_pending:
        print(f"  ✓ 包含 review_status: pending 标记")

    # 5f: 第一行是 ---（frontmatter 开头）
    starts_correctly = wiki_text.startswith("---")
    checks.append(("以 --- frontmatter 开头", starts_correctly))
    if starts_correctly:
        print(f"  ✓ 文件以 YAML frontmatter 开头")
    else:
        print(f"  ✗ 文件未以 YAML frontmatter 开头（首行: {wiki_text[:40]}...）")

    # 汇总
    print("\n" + "=" * 60)
    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)
    print(f"验证结果: {passed}/{total} 通过")
    for name, ok in checks:
        icon = "✓" if ok else "✗"
        print(f"  {icon} {name}")

    if passed == total:
        print("\n✓ 端到端链路验证全部通过！")
        print(f"  wiki 文件: {wiki_path.relative_to(PROJECT_ROOT)}")
        return True
    else:
        print(f"\n⚠ 部分验证失败，请检查 wiki 输出")
        return False


if __name__ == "__main__":
    ok = verify_arxiv_source_links()
    sys.exit(0 if ok else 1)
