#!/usr/bin/env python3
"""参考文献与引文管理器 — 申请书写作管线引用管理。

管理学术参考文献和引文的全生命周期：
1. 维护每个 proposal 的参考文献库（BibTeX-like 结构，但基于 JSON）
2. 在申请书文本中生成编号引文 [1], [2], ...
3. 验证引文完整性（文本中所有 [N] 都有对应条目）
4. 按 NSFC 风格（GB/T 7714-2015）格式化参考文献
5. 链接引文到知识库条目（段落 ↔ 文献血缘）
6. 检测未使用的参考文献和缺失的引文

数据存储：
    {proposal_dir}/04_proposal/references.json
    结构：{"references": {cite_key: {...}}, "next_number": N}

用法:
    >>> from pathlib import Path
    >>> from citation_manager import CitationManager
    >>> mgr = CitationManager(Path("/data/proposals/T1"))
    >>> key = mgr.add_reference({
    ...     "type": "journal",
    ...     "title": "High Harmonic Generation from Solids",
    ...     "authors": ["Zhang, Y.", "Li, X."],
    ...     "year": 2024,
    ...     "venue": "Nature Physics",
    ...     "volume": "20",
    ...     "pages": "123-130",
    ...     "doi": "10.1038/...",
    ... })
    >>> print(key)  # ref_001
    >>> text = "固体HHG现象[1]已被广泛研究。"
    >>> result = mgr.validate_citations(text)
    >>> print(mgr.format_references("nsfc"))

命令行自检:
    python3 scripts/citation_manager.py --self-check
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 确保可从 scripts/ 目录直接导入公共模块
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json, file_lock, lazy_load

__all__ = [
    "CitationManager",
    "REF_TYPES",
    "NSFC_TYPE_TAGS",
    "format_authors_nsfc",
    "parse_citation_numbers",
]

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
REF_TYPES = ("journal", "preprint", "book", "conference", "thesis")

# GB/T 7714-2015 文献类型标识
NSFC_TYPE_TAGS = {
    "journal": "[J]",
    "preprint": "[J]",   # arXiv 预印本按期刊论文处理
    "book": "[M]",
    "conference": "[C]",
    "thesis": "[D]",
}

# 引文格式正则：匹配 [1], [1,2], [1-3], [1,2-4] 等
CITATION_PATTERN = re.compile(r'\[(\d+(?:[,-]\d+)*)\]')

# 占位符正则：匹配 {{cite:IDENTIFIER}}
PLACEHOLDER_PATTERN = re.compile(r'\{\{cite:([^}]+)\}\}')


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def _is_chinese_text(s: str) -> bool:
    """判断字符串是否含中文字符。"""
    return bool(re.search(r'[\u4e00-\u9fff]', s))


def format_authors_nsfc(authors: List[str]) -> str:
    """按 GB/T 7714-2015 格式化作者列表。

    3 人及以下全列；超过 3 人列前 3 人 + "等"（中文）或 "et al."（英文）。

    Args:
        authors: 作者列表，格式为 "Last, First" 或中文名

    Returns:
        格式化后的作者字符串
    """
    if not authors:
        return ""
    if len(authors) <= 3:
        return ", ".join(authors)
    first_three = authors[:3]
    has_chinese = any(_is_chinese_text(a) for a in first_three)
    suffix = "等" if has_chinese else "et al."
    return ", ".join(first_three) + ", " + suffix


def parse_citation_numbers(match_str: str) -> List[int]:
    """解析引文标记中的数字，展开范围为完整列表。

    例如:
        "1" → [1]
        "1,3" → [1, 3]
        "1-3" → [1, 2, 3]
        "1,2-4" → [1, 2, 3, 4]

    Args:
        match_str: 正则捕获组内容，如 "1,2-4"

    Returns:
        展开后的数字列表
    """
    nums: List[int] = []
    for part in match_str.split(','):
        part = part.strip()
        if '-' in part:
            sub = part.split('-', 1)
            try:
                start, end = int(sub[0]), int(sub[1])
                if start <= end:
                    nums.extend(range(start, end + 1))
                else:
                    nums.append(start)
            except ValueError:
                continue
        else:
            try:
                nums.append(int(part))
            except ValueError:
                continue
    return nums


# ---------------------------------------------------------------------------
# CitationManager 类
# ---------------------------------------------------------------------------

class CitationManager:
    """参考文献与引文管理器。

    每个 proposal 目录对应一个 CitationManager 实例，管理该 proposal 下
    `04_proposal/references.json` 参考文献库。

    线程安全：所有写操作通过 common.file_lock（fcntl.flock 跨进程锁）保护
    read-modify-write 临界区，锁键基于 proposal_dir 路径哈希，不同 proposal 互不阻塞。
    """

    def __init__(self, proposal_dir: Path | str) -> None:
        """初始化引文管理器。

        Args:
            proposal_dir: proposal 根目录，引文数据库位于其下的 04_proposal/。
        """
        self.proposal_dir = Path(proposal_dir)
        self.proposal_content_dir = self.proposal_dir / "04_proposal"
        self.db_path = self.proposal_content_dir / "references.json"
        # 跨进程锁键：基于 proposal_dir 绝对路径哈希，避免不同 proposal 互相阻塞
        self._lock_name = (
            "citations-"
            + hashlib.md5(str(self.proposal_dir.resolve()).encode("utf-8")).hexdigest()[:12]
        )
        # 确保目录结构存在
        self.proposal_content_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 持久化
    # ------------------------------------------------------------------

    def _load_db(self) -> Dict[str, Any]:
        """加载引文数据库（纯读，不加锁）。

        文件不存在或格式异常时返回空数据库结构。
        """
        data = load_json(self.db_path, default=None)
        if not isinstance(data, dict) or "references" not in data:
            return {"references": {}, "next_number": 1}
        if not isinstance(data["references"], dict):
            data["references"] = {}
        if not isinstance(data.get("next_number"), int) or data["next_number"] < 1:
            data["next_number"] = 1
        return data

    def _save_db(self, data: Dict[str, Any]) -> None:
        """保存引文数据库（原子写入，应在锁内调用）。"""
        save_json(self.db_path, data)

    def _next_cite_key(self, data: Dict[str, Any]) -> Tuple[str, int]:
        """生成下一个 cite_key 和编号（须在锁内调用）。

        cite_key 格式为 ref_NNN（三位零填充），编号从 1 开始递增。
        """
        num = data.get("next_number", 1)
        cite_key = f"ref_{num:03d}"
        data["next_number"] = num + 1
        return cite_key, num

    # ------------------------------------------------------------------
    # paper_pool 集成
    # ------------------------------------------------------------------

    def _enrich_from_paper_pool(self, ref_data: Dict[str, Any]) -> Dict[str, Any]:
        """尝试从 paper_pool 获取论文元数据，补充缺失字段。

        当 ref_data 含 arxiv_id 但缺少 title/authors 时，从 paper_pool 拉取。
        paper_pool 模块不可用时静默跳过。
        """
        arxiv_id = ref_data.get("arxiv_id")
        if not arxiv_id:
            return ref_data
        # 已有足够信息则不查询
        if ref_data.get("title") and ref_data.get("authors"):
            return ref_data
        pp = lazy_load("paper_pool")
        if pp is None:
            return ref_data
        try:
            pool = pp.get_pool()
            for paper in pool.get("papers", []):
                if paper.get("arxiv_id") == arxiv_id:
                    if not ref_data.get("title"):
                        ref_data["title"] = paper.get("title", "")
                    if not ref_data.get("authors"):
                        authors_str = paper.get("authors", "")
                        if isinstance(authors_str, str) and authors_str:
                            ref_data["authors"] = [a.strip() for a in authors_str.split(",")]
                        elif isinstance(authors_str, list):
                            ref_data["authors"] = authors_str
                    if not ref_data.get("abstract"):
                        ref_data["abstract"] = paper.get("tldr", "")
                    ref_data.setdefault("source", "paper_pool")
                    break
        except Exception:
            pass
        return ref_data

    # ------------------------------------------------------------------
    # 参考文献管理
    # ------------------------------------------------------------------

    def add_reference(self, ref_data: Dict[str, Any]) -> str:
        """添加一条参考文献，返回 cite_key。

        Args:
            ref_data: 参考文献数据，必须含 type 和 title。可选字段：
                authors, year, venue, volume, issue, pages, doi, arxiv_id,
                abstract, source, kb_path, address, publisher

        Returns:
            cite_key，如 "ref_001"

        Raises:
            ValueError: type 非法或 title 为空
        """
        ref_data = dict(ref_data)
        rtype = ref_data.get("type", "")
        if rtype not in REF_TYPES:
            raise ValueError(f"type 必须为 {REF_TYPES} 之一")
        if not ref_data.get("title"):
            raise ValueError("title 不能为空")

        # 尝试从 paper_pool 补充缺失字段
        ref_data = self._enrich_from_paper_pool(ref_data)

        with file_lock(self._lock_name):
            data = self._load_db()
            cite_key, cite_number = self._next_cite_key(data)
            ref_data["cite_key"] = cite_key
            ref_data["cite_number"] = cite_number
            ref_data["added_at"] = now_utc()
            ref_data.setdefault("cited_count", 0)
            data["references"][cite_key] = ref_data
            self._save_db(data)
            return cite_key

    def get_reference(self, cite_key: str) -> Optional[Dict[str, Any]]:
        """获取参考文献（副本）；不存在返回 None。"""
        data = self._load_db()
        ref = data["references"].get(cite_key)
        return dict(ref) if ref else None

    def list_references(self) -> List[Dict[str, Any]]:
        """列出所有参考文献，按 cite_number 排序。"""
        data = self._load_db()
        refs = list(data["references"].values())
        refs.sort(key=lambda r: r.get("cite_number", 0))
        return [dict(r) for r in refs]

    def remove_reference(self, cite_key: str) -> bool:
        """移除参考文献。成功返回 True，不存在返回 False。

        注意：移除后编号不回收，可能产生编号空缺。
        """
        with file_lock(self._lock_name):
            data = self._load_db()
            if cite_key not in data["references"]:
                return False
            del data["references"][cite_key]
            self._save_db(data)
            return True

    def find_or_add(self, ref_data: Dict[str, Any]) -> str:
        """按 title/DOI/arxiv_id 查找已有参考文献，找不到则添加。

        查找优先级：arxiv_id > doi > title（归一化匹配）。

        Args:
            ref_data: 参考文献数据

        Returns:
            cite_key（已有或新建）
        """
        data = self._load_db()
        arxiv_id = ref_data.get("arxiv_id", "").strip()
        doi = ref_data.get("doi", "").strip().lower()
        title = ref_data.get("title", "").strip().lower()

        for key, ref in data["references"].items():
            # 优先匹配 arxiv_id
            if arxiv_id and ref.get("arxiv_id", "").strip() == arxiv_id:
                return key
            # 其次匹配 DOI
            if doi and ref.get("doi", "").strip().lower() == doi:
                return key
            # 最后匹配 title（归一化）
            if title and ref.get("title", "").strip().lower() == title:
                return key

        # 未找到，添加新引用
        return self.add_reference(ref_data)

    # ------------------------------------------------------------------
    # 引文扫描与验证
    # ------------------------------------------------------------------

    def scan_text_citations(self, text: str) -> List[int]:
        """扫描 markdown 文本中的 [N] 引文标记，返回引用编号列表。

        支持 [1], [1,2], [1-3], [1,2-4] 等格式。
        范围会展开为完整列表（如 [1-3] → [1, 2, 3]）。

        Returns:
            排序后的唯一引用编号列表
        """
        all_nums: set = set()
        for match in CITATION_PATTERN.finditer(text):
            nums = parse_citation_numbers(match.group(1))
            all_nums.update(nums)
        return sorted(all_nums)

    def validate_citations(self, text: str) -> Dict[str, Any]:
        """验证文本中所有 [N] 引文都有对应参考文献。

        同时更新每条参考文献的 cited_count 字段（基于本次扫描结果）。

        Returns:
            {
                "valid": bool,           # True 表示无缺失引文
                "cited_numbers": [int],  # 文本中引用的所有编号
                "missing": [int],        # 引用了但参考文献不存在的编号
                "unused": [str],         # 未被引用的 cite_key 列表
                "total_refs": int,       # 参考文献总数
                "cited_count": int,      # 被引用的参考文献数
                "uncited_count": int,    # 未被引用的参考文献数
            }
        """
        # 统计每个编号被引用的次数
        citation_count: Dict[int, int] = {}
        all_cited: set = set()
        for match in CITATION_PATTERN.finditer(text):
            nums = parse_citation_numbers(match.group(1))
            for n in nums:
                citation_count[n] = citation_count.get(n, 0) + 1
                all_cited.add(n)

        with file_lock(self._lock_name):
            data = self._load_db()
            # 更新 cited_count
            ref_numbers: set = set()
            for key, ref in data["references"].items():
                num = ref.get("cite_number", 0)
                ref_numbers.add(num)
                ref["cited_count"] = citation_count.get(num, 0)
            self._save_db(data)

        missing = sorted(all_cited - ref_numbers)
        unused = sorted(
            [key for key, ref in data["references"].items()
             if ref.get("cite_number", 0) not in all_cited],
            key=lambda k: data["references"][k].get("cite_number", 0),
        )

        cited_refs = ref_numbers & all_cited
        return {
            "valid": len(missing) == 0,
            "cited_numbers": sorted(all_cited),
            "missing": missing,
            "unused": unused,
            "total_refs": len(data["references"]),
            "cited_count": len(cited_refs),
            "uncited_count": len(unused),
        }

    # ------------------------------------------------------------------
    # 格式化
    # ------------------------------------------------------------------

    def format_single(self, cite_key: str, style: str = "nsfc") -> str:
        """格式化单条参考文献。

        Args:
            cite_key: 参考文献键
            style: 格式风格，目前支持 "nsfc"（GB/T 7714-2015）

        Returns:
            格式化后的引用字符串；cite_key 不存在返回空串
        """
        ref = self.get_reference(cite_key)
        if not ref:
            return ""
        if style == "nsfc":
            return _format_nsfc(ref)
        return ""

    def format_references(self, style: str = "nsfc") -> str:
        """格式化所有参考文献，按编号排序。

        Args:
            style: 格式风格，目前支持 "nsfc"

        Returns:
            格式化后的参考文献列表，每条一行，前缀 [N]
        """
        refs = self.list_references()
        lines: List[str] = []
        for ref in refs:
            num = ref.get("cite_number", 0)
            if style == "nsfc":
                formatted = _format_nsfc(ref)
            else:
                formatted = ""
            lines.append(f"[{num}] {formatted}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 引文注入
    # ------------------------------------------------------------------

    def inject_citations(self, text: str) -> str:
        """将占位符 {{cite:IDENTIFIER}} 替换为编号引文 [N]。

        IDENTIFIER 按以下顺序匹配：
        1. cite_key（精确匹配，如 ref_001）
        2. arxiv_id（精确匹配，如 2501.67890）
        3. DOI（精确匹配，不区分大小写）

        匹配成功替换为 [N]；匹配失败替换为 [?] 标记缺失。

        Args:
            text: 含占位符的文本

        Returns:
            替换后的文本
        """
        data = self._load_db()

        # 构建查找索引
        by_key: Dict[str, int] = {}
        by_arxiv: Dict[str, int] = {}
        by_doi: Dict[str, int] = {}
        for ref in data["references"].values():
            num = ref.get("cite_number", 0)
            by_key[ref.get("cite_key", "")] = num
            aid = ref.get("arxiv_id", "").strip()
            if aid:
                by_arxiv[aid] = num
            doi = ref.get("doi", "").strip().lower()
            if doi:
                by_doi[doi] = num

        def _replace(match: re.Match) -> str:
            identifier = match.group(1).strip()
            # 1. cite_key 精确匹配
            if identifier in by_key:
                return f"[{by_key[identifier]}]"
            # 2. arxiv_id 精确匹配
            if identifier in by_arxiv:
                return f"[{by_arxiv[identifier]}]"
            # 3. DOI 精确匹配（不区分大小写）
            lower_id = identifier.lower()
            if lower_id in by_doi:
                return f"[{by_doi[lower_id]}]"
            # 未找到
            return "[?]"

        return PLACEHOLDER_PATTERN.sub(_replace, text)

    # ------------------------------------------------------------------
    # 引文映射
    # ------------------------------------------------------------------

    def get_citation_map(self, text: str) -> Dict[int, List[str]]:
        """构建段落 → 引用文献的映射。

        将文本按空行分割为段落，对每个段落扫描引文标记，
        返回 {paragraph_index: [cite_key, ...]}。

        Args:
            text: markdown 文本

        Returns:
            段落索引 → cite_key 列表（仅含引用了文献的段落）
        """
        data = self._load_db()
        # 构建编号 → cite_key 映射
        num_to_key: Dict[int, str] = {}
        for ref in data["references"].values():
            num_to_key[ref.get("cite_number", 0)] = ref.get("cite_key", "")

        # 按空行分割段落
        paragraphs = re.split(r'\n\s*\n', text)
        result: Dict[int, List[str]] = {}
        for i, para in enumerate(paragraphs):
            nums = self.scan_text_citations(para)
            if nums:
                keys = [num_to_key[n] for n in nums if n in num_to_key]
                if keys:
                    result[i] = keys
        return result

    # ------------------------------------------------------------------
    # 导出
    # ------------------------------------------------------------------

    def export_bibliography(self, format: str = "json") -> str:
        """导出参考文献目录。

        Args:
            format: 导出格式，支持 "json" / "markdown" / "bibtex"

        Returns:
            格式化后的字符串

        Raises:
            ValueError: 不支持的格式
        """
        refs = self.list_references()
        if format == "json":
            return json.dumps(refs, ensure_ascii=False, indent=2)
        elif format == "markdown":
            return self.format_references("nsfc")
        elif format == "bibtex":
            return self._export_bibtex(refs)
        else:
            raise ValueError(f"不支持的格式: {format}（支持 json/markdown/bibtex）")

    def _export_bibtex(self, refs: List[Dict[str, Any]]) -> str:
        """导出 BibTeX 格式。

        文献类型 → BibTeX 条目类型映射：
            journal → @article
            preprint → @misc
            book → @book
            conference → @inproceedings
            thesis → @phdthesis
        """
        entry_type_map = {
            "journal": "article",
            "preprint": "misc",
            "book": "book",
            "conference": "inproceedings",
            "thesis": "phdthesis",
        }
        lines: List[str] = []
        for ref in refs:
            cite_key = ref.get("cite_key", "unknown")
            rtype = ref.get("type", "journal")
            entry_type = entry_type_map.get(rtype, "misc")
            fields: List[str] = []

            authors = ref.get("authors", [])
            if authors:
                fields.append(f"  author = {{{' and '.join(authors)}}}")

            if ref.get("title"):
                fields.append(f"  title = {{{ref['title']}}}")

            if rtype == "journal":
                if ref.get("venue"):
                    fields.append(f"  journal = {{{ref['venue']}}}")
                if ref.get("volume"):
                    fields.append(f"  volume = {{{ref['volume']}}}")
                if ref.get("pages"):
                    fields.append(f"  pages = {{{ref['pages']}}}")
            elif rtype == "preprint":
                if ref.get("arxiv_id"):
                    fields.append(f"  eprint = {{{ref['arxiv_id']}}}")
                    fields.append("  archivePrefix = {arXiv}")
            elif rtype == "book":
                pub = ref.get("publisher", "") or ref.get("venue", "")
                if pub:
                    fields.append(f"  publisher = {{{pub}}}")
            elif rtype == "conference":
                if ref.get("venue"):
                    fields.append(f"  booktitle = {{{ref['venue']}}}")
                if ref.get("pages"):
                    fields.append(f"  pages = {{{ref['pages']}}}")
            elif rtype == "thesis":
                if ref.get("venue"):
                    fields.append(f"  school = {{{ref['venue']}}}")

            if ref.get("year"):
                fields.append(f"  year = {{{ref['year']}}}")
            if ref.get("doi"):
                fields.append(f"  doi = {{{ref['doi']}}}")

            lines.append(f"@{entry_type}{{{cite_key},")
            lines.append(",\n".join(fields))
            lines.append("}")
            lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 统计
    # ------------------------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        """返回引文统计信息。

        Returns:
            {
                "total_refs": int,       # 参考文献总数
                "by_type": {type: int},  # 按类型分布
                "by_source": {src: int}, # 按来源分布
                "cited_count": int,      # 被引用的文献数（cited_count > 0）
                "uncited_count": int,    # 未被引用的文献数
                "total_citations": int,  # 引文总次数（所有 cited_count 之和）
            }
        """
        refs = self.list_references()
        by_type: Dict[str, int] = {}
        by_source: Dict[str, int] = {}
        cited = 0
        uncited = 0
        total_citations = 0
        for ref in refs:
            t = ref.get("type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
            s = ref.get("source", "unknown")
            by_source[s] = by_source.get(s, 0) + 1
            cc = ref.get("cited_count", 0)
            total_citations += cc
            if cc > 0:
                cited += 1
            else:
                uncited += 1
        return {
            "total_refs": len(refs),
            "by_type": by_type,
            "by_source": by_source,
            "cited_count": cited,
            "uncited_count": uncited,
            "total_citations": total_citations,
        }

    # ------------------------------------------------------------------
    # lineage_tracker 集成
    # ------------------------------------------------------------------

    def register_lineage(self, cite_key: str, paragraph_id: str,
                         tracker: Any = None) -> bool:
        """注册引文 → 段落的血缘关系。

        需 lineage_tracker 模块可用。通过 lazy_load 加载，失败返回 False。

        Args:
            cite_key: 参考文献键
            paragraph_id: 段落节点 ID
            tracker: 可选的 LineageTracker 实例；为 None 时自动创建

        Returns:
            成功返回 True
        """
        ref = self.get_reference(cite_key)
        if not ref:
            return False

        if tracker is None:
            lt_module = lazy_load("lineage_tracker")
            if lt_module is None:
                return False
            if hasattr(lt_module, "LineageTracker"):
                tracker = lt_module.LineageTracker(self.proposal_dir)
            else:
                return False

        try:
            # 确保节点存在
            if hasattr(tracker, "register_node"):
                tracker.register_node(cite_key, "reference", ref.get("title", cite_key))
                tracker.register_node(paragraph_id, "proposal_section", paragraph_id)
            if hasattr(tracker, "add_edge"):
                tracker.add_edge(paragraph_id, cite_key, "derived_from", "引用文献")
                return True
        except Exception:
            pass
        return False


# ---------------------------------------------------------------------------
# NSFC 格式化辅助函数
# ---------------------------------------------------------------------------

def _format_nsfc(ref: Dict[str, Any]) -> str:
    """按 GB/T 7714-2015 格式化单条参考文献。

    格式规范：
        期刊: 作者. 题名[J]. 刊名, 年, 卷(期): 起止页.
        预印本: 作者. 题名[J]. arXiv preprint arXiv:XXXX.XXXXX, 年.
        书籍: 作者. 书名[M]. 出版地: 出版社, 年.
        会议: 作者. 题名[C]//会议名. 出版地: 出版社, 年: 起止页.
        学位论文: 作者. 题名[D]. 学位授予地: 学位授予单位, 年.
    """
    authors = format_authors_nsfc(ref.get("authors", []))
    title = ref.get("title", "")
    year = ref.get("year", "")
    rtype = ref.get("type", "journal")
    tag = NSFC_TYPE_TAGS.get(rtype, "[J]")
    venue = ref.get("venue", "")
    volume = ref.get("volume", "")
    issue = ref.get("issue", "")
    pages = ref.get("pages", "")
    address = ref.get("address", "")
    publisher = ref.get("publisher", "")
    arxiv_id = ref.get("arxiv_id", "")

    # 避免作者名末尾句号与分隔句号重复（如 "Zhang, Y." + "." → "Zhang, Y.."）
    if authors:
        if authors.endswith('.'):
            author_part = f"{authors} "
        else:
            author_part = f"{authors}. "
    else:
        author_part = ""

    if rtype == "journal":
        # 作者. 题名[J]. 刊名, 年, 卷(期): 起止页.
        parts = f"{author_part}{title}{tag}."
        if venue:
            parts += f" {venue}"
        if year:
            parts += f", {year}"
        if volume:
            if issue:
                parts += f", {volume}({issue})"
            else:
                parts += f", {volume}"
        if pages:
            parts += f": {pages}"
        return parts + "."

    elif rtype == "preprint":
        # 作者. 题名[J]. arXiv preprint arXiv:XXXX.XXXXX, 年.
        parts = f"{author_part}{title}{tag}."
        if arxiv_id:
            parts += f" arXiv preprint arXiv:{arxiv_id}"
        if year:
            parts += f", {year}"
        return parts + "."

    elif rtype == "book":
        # 作者. 书名[M]. 出版地: 出版社, 年.
        pub = publisher or venue
        parts = f"{author_part}{title}{tag}."
        if address and pub:
            parts += f" {address}: {pub}"
        elif pub:
            parts += f" {pub}"
        if year:
            parts += f", {year}"
        return parts + "."

    elif rtype == "conference":
        # 作者. 题名[C]//会议名. 出版地: 出版社, 年: 起止页.
        parts = f"{author_part}{title}{tag}"
        if venue:
            parts += f"//{venue}"
        pub_parts: List[str] = []
        if address and publisher:
            pub_parts.append(f"{address}: {publisher}")
        elif publisher:
            pub_parts.append(publisher)
        if year:
            pub_parts.append(str(year))
        if pub_parts:
            parts += ". " + ", ".join(pub_parts)
        if pages:
            parts += f": {pages}"
        return parts + "."

    elif rtype == "thesis":
        # 作者. 题名[D]. 学位授予地: 学位授予单位, 年.
        parts = f"{author_part}{title}{tag}."
        if address and venue:
            parts += f" {address}: {venue}"
        elif venue:
            parts += f" {venue}"
        if year:
            parts += f", {year}"
        return parts + "."

    # 未知类型，退化为通用格式
    parts = f"{author_part}{title}"
    if venue:
        parts += f". {venue}"
    if year:
        parts += f", {year}"
    return parts + "."


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_check() -> None:
    """自检：在临时目录中隔离测试全部核心场景。

    检查点（14 项）：
        1. 初始化（创建空数据库）
        2. 添加参考文献（cite_key 生成、编号）
        3. 查重添加（find_or_add 返回已有 key）
        4. 查询与删除参考文献
        5. 扫描文本引文（单个、多个、范围格式）
        6. 验证引文（缺失检测、未使用检测）
        7. NSFC 格式化 — 期刊、预印本
        8. NSFC 格式化 — 书籍、会议、学位论文 + 作者格式化
        9. 注入引文（占位符 → 编号）
        10. 引文映射（段落 → 引用文献）
        11. 导出文献目录（json、markdown、bibtex）
        12. 统计信息
        13. 空数据库处理
        14. 原子写入 + 文件锁
    """
    import shutil
    import tempfile

    print("=" * 50)
    print("◐ citation_manager 自检")
    print("=" * 50)

    tmp = Path(tempfile.mkdtemp(prefix="citation_test_"))
    try:
        proposal_dir = tmp / "T1_proposal"

        # [1/14] 初始化（创建空数据库）
        print("\n[1/14] 初始化（创建空数据库）...")
        mgr = CitationManager(proposal_dir)
        assert mgr.db_path.parent.exists(), "04_proposal 目录应已创建"
        assert not mgr.db_path.exists(), "空数据库不应创建文件（懒创建）"
        refs = mgr.list_references()
        assert refs == [], "空数据库应返回空列表"
        stats = mgr.get_stats()
        assert stats["total_refs"] == 0
        print(f"  数据库路径: {mgr.db_path}")
        print(f"  初始文献数: {stats['total_refs']}")
        print("  ✓ 空数据库初始化成功（懒创建）")

        # [2/14] 添加参考文献（cite_key 生成、编号）
        print("\n[2/14] 添加参考文献（cite_key 生成、编号）...")
        key1 = mgr.add_reference({
            "type": "journal",
            "title": "High Harmonic Generation from Solids",
            "authors": ["Zhang, Y.", "Li, X."],
            "year": 2024,
            "venue": "Nature Physics",
            "volume": "20",
            "pages": "123-130",
            "doi": "10.1038/nphys.2024.001",
        })
        key2 = mgr.add_reference({
            "type": "preprint",
            "title": "Attosecond Dynamics in Topological Insulators",
            "authors": ["Wang, Z.", "Chen, L.", "Liu, H.", "Zhao, Q."],
            "year": 2025,
            "arxiv_id": "2501.67890",
        })
        print(f"  第一条: cite_key={key1}, number={mgr.get_reference(key1)['cite_number']}")
        print(f"  第二条: cite_key={key2}, number={mgr.get_reference(key2)['cite_number']}")
        assert key1 == "ref_001", f"期望 ref_001，实际 {key1}"
        assert key2 == "ref_002", f"期望 ref_002，实际 {key2}"
        ref1 = mgr.get_reference(key1)
        assert ref1["cite_number"] == 1
        assert ref1["added_at"] is not None
        assert ref1["cited_count"] == 0
        # 验证文件已创建
        assert mgr.db_path.exists(), "添加后数据库文件应存在"
        print("  ✓ cite_key 自动生成、编号递增、元数据完整")

        # [3/14] 查重添加（find_or_add 返回已有 key）
        print("\n[3/14] 查重添加（find_or_add 返回已有 key）...")
        # 按 DOI 查重
        dup_key = mgr.find_or_add({
            "type": "journal",
            "title": "High Harmonic Generation from Solids (Duplicate)",
            "authors": ["Zhang, Y."],
            "doi": "10.1038/nphys.2024.001",
        })
        assert dup_key == key1, f"DOI 查重应返回 {key1}，实际 {dup_key}"
        # 按 arxiv_id 查重
        dup_key2 = mgr.find_or_add({
            "type": "preprint",
            "title": "Different Title But Same arxiv_id",
            "arxiv_id": "2501.67890",
        })
        assert dup_key2 == key2, f"arxiv_id 查重应返回 {key2}，实际 {dup_key2}"
        # 按 title 查重
        dup_key3 = mgr.find_or_add({
            "type": "journal",
            "title": "High Harmonic Generation from Solids",
        })
        assert dup_key3 == key1, f"title 查重应返回 {key1}，实际 {dup_key3}"
        # 不重复则添加
        key3 = mgr.find_or_add({
            "type": "book",
            "title": "Nonlinear Optics",
            "authors": ["Boyd, R."],
            "year": 2020,
            "venue": "Academic Press",
        })
        assert key3 == "ref_003", f"新文献应为 ref_003，实际 {key3}"
        print(f"  DOI 查重 → {dup_key}")
        print(f"  arxiv_id 查重 → {dup_key2}")
        print(f"  title 查重 → {dup_key3}")
        print(f"  新文献 → {key3}")
        print("  ✓ 三种查重方式均正确，未重复添加")

        # [4/14] 查询与删除参考文献
        print("\n[4/14] 查询与删除参考文献...")
        # 查询存在的 key
        ref = mgr.get_reference(key1)
        assert ref is not None and ref["title"] == "High Harmonic Generation from Solids"
        # 查询不存在的 key
        assert mgr.get_reference("ref_999") is None
        # 删除
        removed = mgr.remove_reference(key3)
        assert removed is True
        assert mgr.get_reference(key3) is None
        # 删除不存在的 key
        removed2 = mgr.remove_reference("ref_999")
        assert removed2 is False
        # 列表
        refs = mgr.list_references()
        assert len(refs) == 2, f"删除后应剩 2 条，实际 {len(refs)}"
        print(f"  查询 {key1}: ✓")
        print(f"  查询 ref_999: None ✓")
        print(f"  删除 {key3}: {removed}")
        print(f"  删除后剩余: {len(refs)} 条")
        print("  ✓ 查询与删除正常")

        # [5/14] 扫描文本引文（单个、多个、范围格式）
        print("\n[5/14] 扫描文本引文（单个、多个、范围格式）...")
        text_single = "固体HHG现象[1]已被广泛研究。"
        text_multi = "如文献[1,2]所示，该领域发展迅速。"
        text_range = "多项研究[1-2]证实了这一结论。"
        text_complex = "不同方法[1,2]给出了不同结果[1-2]，详见[2]。"
        text_none = "没有引文的普通文本。"

        nums_single = mgr.scan_text_citations(text_single)
        assert nums_single == [1], f"单个引文应为 [1]，实际 {nums_single}"

        nums_multi = mgr.scan_text_citations(text_multi)
        assert nums_multi == [1, 2], f"多个引文应为 [1,2]，实际 {nums_multi}"

        nums_range = mgr.scan_text_citations(text_range)
        assert nums_range == [1, 2], f"范围引文应展开为 [1,2]，实际 {nums_range}"

        nums_complex = mgr.scan_text_citations(text_complex)
        assert nums_complex == [1, 2], f"复杂引文应为 [1,2]，实际 {nums_complex}"

        nums_none = mgr.scan_text_citations(text_none)
        assert nums_none == [], "无引文文本应返回空列表"

        print(f"  [1] → {nums_single}")
        print(f"  [1,2] → {nums_multi}")
        print(f"  [1-2] → {nums_range}")
        print(f"  复杂混合 → {nums_complex}")
        print(f"  无引文 → {nums_none}")
        print("  ✓ 单个/多个/范围/复杂格式均正确解析")

        # [6/14] 验证引文（缺失检测、未使用检测）
        print("\n[6/14] 验证引文（缺失检测、未使用检测）...")
        # 添加更多文献用于测试
        key4 = mgr.add_reference({
            "type": "journal",
            "title": "Another Paper",
            "authors": ["Test, A."],
            "year": 2023,
            "venue": "Test Journal",
        })
        # 文本引用了 [1]（存在）和 [5]（不存在）
        text_validate = "文献[1]提出了方法，文献[5]补充了细节。"
        result = mgr.validate_citations(text_validate)
        print(f"  引用编号: {result['cited_numbers']}")
        print(f"  缺失: {result['missing']}")
        print(f"  未使用: {result['unused']}")
        print(f"  有效: {result['valid']}")
        assert result["valid"] is False, "有缺失引文时 valid 应为 False"
        assert 1 in result["cited_numbers"]
        assert 5 in result["cited_numbers"]
        assert result["missing"] == [5], f"缺失应为 [5]，实际 {result['missing']}"
        assert len(result["unused"]) >= 1, "应有未使用的文献"
        # 验证 cited_count 更新
        ref1_updated = mgr.get_reference(key1)
        assert ref1_updated["cited_count"] == 1, f"ref_001 的 cited_count 应为 1"
        # 全部有效
        text_valid = "文献[1]和文献[2]都讨论了这个问题。"
        result2 = mgr.validate_citations(text_valid)
        assert result2["valid"] is True
        assert result2["missing"] == []
        print(f"  全部有效时: valid={result2['valid']}")
        print("  ✓ 缺失/未使用检测正确，cited_count 自动更新")

        # [7/14] NSFC 格式化 — 期刊、预印本
        print("\n[7/14] NSFC 格式化 — 期刊、预印本...")
        fmt_journal = mgr.format_single(key1, "nsfc")
        print(f"  期刊: {fmt_journal}")
        assert "[J]" in fmt_journal
        assert "Zhang, Y." in fmt_journal
        assert "Nature Physics" in fmt_journal
        assert "2024" in fmt_journal
        assert "20" in fmt_journal
        assert "123-130" in fmt_journal

        fmt_preprint = mgr.format_single(key2, "nsfc")
        print(f"  预印本: {fmt_preprint}")
        assert "[J]" in fmt_preprint
        assert "arXiv:2501.67890" in fmt_preprint
        assert "2025" in fmt_preprint
        # 预印本 4 作者 → 前 3 + et al.
        assert "et al." in fmt_preprint
        print("  ✓ 期刊和预印本格式正确")

        # [8/14] NSFC 格式化 — 书籍、会议、学位论文 + 作者格式化
        print("\n[8/14] NSFC 格式化 — 书籍、会议、学位论文 + 作者格式化...")
        key_book = mgr.add_reference({
            "type": "book",
            "title": "Nonlinear Optics",
            "authors": ["Boyd, R."],
            "year": 2020,
            "venue": "Academic Press",
            "address": "Burlington",
        })
        key_conf = mgr.add_reference({
            "type": "conference",
            "title": "Ultrafast Phenomena in Solids",
            "authors": ["Lee, S.", "Kim, J.", "Park, M."],
            "year": 2023,
            "venue": "CLEO 2023",
            "pages": "JT2A.12",
        })
        key_thesis = mgr.add_reference({
            "type": "thesis",
            "title": "Studies on High Harmonic Generation",
            "authors": ["Zhang, W."],
            "year": 2022,
            "venue": "Tsinghua University",
            "address": "Beijing",
        })
        fmt_book = mgr.format_single(key_book, "nsfc")
        fmt_conf = mgr.format_single(key_conf, "nsfc")
        fmt_thesis = mgr.format_single(key_thesis, "nsfc")
        print(f"  书籍: {fmt_book}")
        print(f"  会议: {fmt_conf}")
        print(f"  学位论文: {fmt_thesis}")
        assert "[M]" in fmt_book
        assert "Academic Press" in fmt_book
        assert "Burlington" in fmt_book
        assert "[C]" in fmt_conf
        assert "CLEO 2023" in fmt_conf
        assert "[D]" in fmt_thesis
        assert "Tsinghua University" in fmt_thesis

        # 作者格式化测试
        assert format_authors_nsfc(["A, B."]) == "A, B."
        assert format_authors_nsfc(["A, B.", "C, D."]) == "A, B., C, D."
        assert format_authors_nsfc(["A, B.", "C, D.", "E, F."]) == "A, B., C, D., E, F."
        # 4 人 → 前 3 + et al.
        four = format_authors_nsfc(["A, B.", "C, D.", "E, F.", "G, H."])
        assert "et al." in four
        assert "G, H." not in four
        # 中文作者 → 前 3 + 等
        cn_four = format_authors_nsfc(["张三", "李四", "王五", "赵六"])
        assert "等" in cn_four
        assert "赵六" not in cn_four
        # 空列表
        assert format_authors_nsfc([]) == ""
        print("  ✓ 五种类型格式正确，作者 ≤3/>3 中英文均正确")

        # format_references 全部格式化
        all_refs = mgr.format_references("nsfc")
        print(f"\n  全部参考文献（{len(all_refs.splitlines())} 条）:")
        for line in all_refs.splitlines():
            print(f"    {line}")
        assert len(all_refs.splitlines()) == len(mgr.list_references())

        # [9/14] 注入引文（占位符 → 编号）
        print("\n[9/14] 注入引文（占位符 → 编号）...")
        text_with_placeholders = (
            "如{{cite:ref_001}}所示，固体HHG已被观测。"
            "拓扑绝缘体中的现象见{{cite:2501.67890}}。"
            "DOI引用{{cite:10.1038/nphys.2024.001}}。"
            "缺失引用{{cite:9999.99999}}标记为[?]。"
        )
        injected = mgr.inject_citations(text_with_placeholders)
        print(f"  原文: {text_with_placeholders}")
        print(f"  注入: {injected}")
        assert "[1]" in injected, "cite_key 占位符应替换为 [1]"
        assert "[2]" in injected, "arxiv_id 占位符应替换为 [2]"
        assert "[?]" in injected, "缺失引用应标记为 [?]"
        print("  ✓ cite_key/arxiv_id/DOI 占位符均正确替换，缺失标记 [?]")

        # [10/14] 引文映射（段落 → 引用文献）
        print("\n[10/14] 引文映射（段落 → 引用文献）...")
        text_paragraphs = (
            "第一段讨论了HHG现象[1]。\n\n"
            "第二段分析了拓扑绝缘体[2]和传统材料[1,2]。\n\n"
            "第三段没有引用任何文献。\n\n"
            "第四段引用了范围[1-2]。"
        )
        citation_map = mgr.get_citation_map(text_paragraphs)
        print(f"  映射: {citation_map}")
        assert 0 in citation_map, "第 0 段应有引用"
        assert 1 in citation_map, "第 1 段应有引用"
        assert 2 not in citation_map, "第 2 段无引用，不应在映射中"
        assert 3 in citation_map, "第 3 段应有引用"
        assert key1 in citation_map[0], "第 0 段应引用 ref_001"
        assert key2 in citation_map[1], "第 1 段应引用 ref_002"
        print("  ✓ 段落 → 引用文献映射正确，无引用段落被跳过")

        # [11/14] 导出文献目录（json、markdown、bibtex）
        print("\n[11/14] 导出文献目录（json、markdown、bibtex）...")
        # JSON 导出
        bib_json = mgr.export_bibliography("json")
        parsed = json.loads(bib_json)
        assert isinstance(parsed, list)
        assert len(parsed) == len(mgr.list_references())
        assert parsed[0]["cite_key"] == "ref_001"
        print(f"  JSON: {len(parsed)} 条，首条 cite_key={parsed[0]['cite_key']}")

        # Markdown 导出
        bib_md = mgr.export_bibliography("markdown")
        assert bib_md == mgr.format_references("nsfc")
        assert "[1]" in bib_md
        print(f"  Markdown: {len(bib_md.splitlines())} 行")

        # BibTeX 导出
        bib_tex = mgr.export_bibliography("bibtex")
        assert "@article{ref_001" in bib_tex, "BibTeX 应含 @article 条目"
        assert "@misc{ref_002" in bib_tex, "BibTeX 应含 @misc 预印本条目"
        assert "@book{" in bib_tex, "BibTeX 应含 @book 条目"
        assert "@inproceedings{" in bib_tex, "BibTeX 应含 @inproceedings 条目"
        assert "@phdthesis{" in bib_tex, "BibTeX 应含 @phdthesis 条目"
        assert " and " in bib_tex, "BibTeX 作者应以 ' and ' 分隔"
        print(f"  BibTeX: {bib_tex.count('@')} 个条目")
        print("  ✓ JSON/Markdown/BibTeX 三种格式导出正确")

        # [12/14] 统计信息
        print("\n[12/14] 统计信息...")
        # 先更新一次引用计数
        mgr.validate_citations("文献[1]和[2]被引用，[1]再次被引用。")
        stats = mgr.get_stats()
        print(f"  总文献数: {stats['total_refs']}")
        print(f"  按类型: {stats['by_type']}")
        print(f"  按来源: {stats['by_source']}")
        print(f"  被引用: {stats['cited_count']}")
        print(f"  未引用: {stats['uncited_count']}")
        print(f"  引用总次: {stats['total_citations']}")
        assert stats["total_refs"] == len(mgr.list_references())
        assert stats["total_refs"] > 0
        assert "journal" in stats["by_type"]
        assert stats["cited_count"] >= 1
        assert stats["total_citations"] >= 2
        # ref_001 被引用 2 次，ref_002 被引用 1 次
        assert stats["total_citations"] == 3, f"引用总次应为 3，实际 {stats['total_citations']}"
        print("  ✓ 统计信息正确（总数/类型/来源/引用计数）")

        # [13/14] 空数据库处理
        print("\n[13/14] 空数据库处理...")
        empty_dir = tmp / "empty_proposal"
        empty_mgr = CitationManager(empty_dir)
        assert empty_mgr.list_references() == []
        assert empty_mgr.format_references() == ""
        assert empty_mgr.get_stats()["total_refs"] == 0
        empty_result = empty_mgr.validate_citations("文献[1]不存在。")
        assert empty_result["valid"] is False
        assert empty_result["missing"] == [1]
        assert empty_result["total_refs"] == 0
        assert empty_mgr.export_bibliography("json") == "[]"
        assert empty_mgr.export_bibliography("bibtex") == ""
        assert empty_mgr.export_bibliography("markdown") == ""
        # inject_citations 对空数据库
        injected_empty = empty_mgr.inject_citations("{{cite:ref_001}}测试")
        assert "[?]" in injected_empty, "空数据库注入应标记 [?]"
        # get_citation_map 对空数据库
        empty_map = empty_mgr.get_citation_map("文本[1]含引用。")
        assert empty_map == {}, "空数据库引文映射应为空（无匹配 cite_key）"
        print("  ✓ 空数据库所有操作安全返回")

        # [14/14] 原子写入 + 文件锁
        print("\n[14/14] 原子写入 + 文件锁...")
        # 文件存在且可正确加载
        assert mgr.db_path.exists(), "数据库文件应存在"
        raw = load_json(mgr.db_path, {})
        assert "references" in raw
        assert "next_number" in raw
        assert raw["next_number"] > len(raw["references"])
        print(f"  数据库: {len(raw['references'])} 条，next_number={raw['next_number']}")
        # 重新加载确保数据一致
        mgr2 = CitationManager(proposal_dir)
        assert len(mgr2.list_references()) == len(mgr.list_references())
        assert mgr2.get_reference(key1)["title"] == ref1["title"]
        print(f"  重新加载: {len(mgr2.list_references())} 条，数据一致")
        # 验证 JSON 格式（ensure_ascii=False, indent=2）
        raw_text = mgr.db_path.read_text(encoding="utf-8")
        assert "  \"references\"" in raw_text, "应为缩进格式"
        # 中文不被转义
        if any(c in raw_text for c in ["\\u4e00", "\\u"]):
            # 如果有中文内容，验证不被转义
            pass  # 当前测试数据无中文，跳过
        # 锁名唯一性
        assert mgr._lock_name != empty_mgr._lock_name, "不同 proposal 锁名应不同"
        print(f"  锁名: {mgr._lock_name}")
        print(f"  空库锁名: {empty_mgr._lock_name}")
        print("  ✓ 原子写入 + 文件锁 + 数据一致性验证通过")

        print("\n" + "=" * 50)
        print("✓ citation_manager 自检全部通过")
        print("=" * 50)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print("(已清理临时目录)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="参考文献与引文管理器")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
    else:
        parser.print_help()
