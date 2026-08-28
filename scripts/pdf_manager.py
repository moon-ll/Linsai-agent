#!/usr/bin/env python3
"""PDF 原文库管理器 — 文献 PDF 原文的存储、检索与按需调用。

v6.3.0 新增模块。实现以下能力：
- PDF 原文的本地存储与元数据管理（去重、SHA-256 校验）
- 从 arXiv 自动下载 PDF 原文（复用 deepxiv_knowledge/pdf_extractor）
- 用户手动上传 PDF（通过 Web API base64 或文件复制）
- 按需获取 PDF 全文文本（提取后缓存，避免重复解析）
- 与知识库摘要（wiki/papers/）和论文池（paper-pool.json）的关联

存储结构:
    knowledge/raw/pdfs/
    ├── {arxiv_id}.pdf           # arXiv 论文 PDF 原文
    ├── {sha256_prefix}.pdf       # 用户上传 PDF（无 arxiv_id 时）
    └── _text_cache/
        └── {arxiv_id}.txt        # 提取的全文文本缓存

元数据文件:
    memory/pdf-library.json
    {
      "papers": {
        "2403.15337": {
          "pdf_id": "2403.15337",
          "arxiv_id": "2403.15337",
          "title": "...",
          "pdf_path": "raw/pdfs/2403.15337.pdf",
          "pdf_sha256": "abc123...",
          "pdf_size_bytes": 1234567,
          "pdf_source": "arxiv_download",  # arxiv_download | user_upload | workflow
          "stored_at": "2026-07-26T...",
          "text_cached": true,
          "text_path": "raw/pdfs/_text_cache/2403.15337.txt",
          "wiki_path": "wiki/papers/2403-15337-high-harmonic.md",  # 关联的摘要
          "notes": ""
        }
      },
      "updated_at": "2026-07-26T..."
    }

用法示例:
    >>> from pdf_manager import PdfLibrary
    >>> lib = PdfLibrary()
    >>> lib.ensure_pdf("2403.15337", title="...")  # 下载 arXiv PDF
    >>> path = lib.get_pdf_path("2403.15337")       # 获取本地路径
    >>> text = lib.get_pdf_text("2403.15337")        # 提取全文文本
    >>> lib.store_upload(b"<pdf bytes>", title="自定义论文")  # 用户上传
    >>> lib.list_pdfs()                              # 列出全部 PDF
"""

from __future__ import annotations

import os
import subprocess
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import file_lock, file_sha256, load_json, now_utc, save_json, safe_filename
from paths import KNOWLEDGE_DIR, MEMORY_DIR, PDF_DIR, PDF_LIBRARY_PATH, WIKI_DIR

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

ARXIV_PDF_URL = "https://arxiv.org/pdf/{arxiv_id}.pdf"
ARXIV_PDF_URL_OLD = "https://arxiv.org/pdf/{archive}/{arxiv_id}.pdf"  # 旧格式如 physics/9906053

TEXT_CACHE_DIR = PDF_DIR / "_text_cache"

# PDF 来源标记
SOURCE_ARXIV = "arxiv_download"
SOURCE_UPLOAD = "user_upload"
SOURCE_WORKFLOW = "workflow"

# 下载超时（秒）
DOWNLOAD_TIMEOUT = 120

# 最大 PDF 大小（50MB），超过则拒绝存储
MAX_PDF_SIZE = 50 * 1024 * 1024


class PdfLibrary:
    """PDF 原文库管理器。

    管理文献 PDF 原文的存储、检索、文本提取与元数据维护。
    线程安全：通过 file_lock("pdf-library") 保证跨进程写入安全。
    """

    def __init__(self) -> None:
        """初始化 PDF 库，确保存储目录存在。"""
        PDF_DIR.mkdir(parents=True, exist_ok=True)
        TEXT_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 元数据读写
    # ------------------------------------------------------------------

    def _load_library(self) -> Dict[str, Any]:
        """加载 PDF 库元数据。"""
        return load_json(PDF_LIBRARY_PATH, {"papers": {}})

    def _save_library(self, data: Dict[str, Any]) -> None:
        """保存 PDF 库元数据（原子写入 + 文件锁）。"""
        data["updated_at"] = now_utc()
        with file_lock("pdf-library"):
            save_json(PDF_LIBRARY_PATH, data)

    def _get_entry(self, pdf_id: str) -> Optional[Dict[str, Any]]:
        """获取单条 PDF 记录。"""
        lib = self._load_library()
        return lib.get("papers", {}).get(pdf_id)

    def _set_entry(self, pdf_id: str, entry: Dict[str, Any]) -> None:
        """写入/更新单条 PDF 记录（加锁）。"""
        with file_lock("pdf-library"):
            lib = self._load_library()
            lib.setdefault("papers", {})[pdf_id] = entry
            lib["updated_at"] = now_utc()
            save_json(PDF_LIBRARY_PATH, lib)

    # ------------------------------------------------------------------
    # PDF 存储（核心）
    # ------------------------------------------------------------------

    def store_bytes(
        self,
        pdf_bytes: bytes,
        pdf_id: Optional[str] = None,
        title: str = "",
        source: str = SOURCE_UPLOAD,
        arxiv_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """存储 PDF 字节流到本地，返回元数据记录。

        Args:
            pdf_bytes: PDF 文件二进制内容
            pdf_id: PDF 标识符（arxiv_id 或自定义 ID），为 None 时用 SHA-256 前缀生成
            title: 论文标题（用于日志和展示）
            source: 来源标记
            arxiv_id: 关联的 arXiv ID（可选，用于跨表关联）

        Returns:
            PDF 元数据字典

        Raises:
            ValueError: PDF 内容为空或超过大小限制
        """
        if not pdf_bytes:
            raise ValueError("PDF 内容为空")
        if len(pdf_bytes) > MAX_PDF_SIZE:
            raise ValueError(f"PDF 大小 {len(pdf_bytes)} 超过限制 {MAX_PDF_SIZE}")

        # 计算 SHA-256 用于去重
        import hashlib
        sha = hashlib.sha256(pdf_bytes).hexdigest()

        # 检查是否已存在相同内容的 PDF
        existing = self._find_by_sha256(sha)
        if existing:
            # 内容相同，更新标题等元数据（不覆盖文件）
            if title and not existing.get("title"):
                existing["title"] = title
                self._set_entry(existing["pdf_id"], existing)
            return existing

        # 生成 pdf_id 和文件名
        if not pdf_id:
            if arxiv_id:
                pdf_id = arxiv_id
            else:
                pdf_id = sha[:12]  # 用 SHA-256 前 12 位作为 ID

        filename = f"{safe_filename(pdf_id)}.pdf"
        pdf_path = PDF_DIR / filename

        # 写入文件
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
            f.flush()
            os.fsync(f.fileno())

        entry = {
            "pdf_id": pdf_id,
            "arxiv_id": arxiv_id or pdf_id,
            "title": title,
            "pdf_path": f"raw/pdfs/{filename}",
            "pdf_sha256": sha,
            "pdf_size_bytes": len(pdf_bytes),
            "pdf_source": source,
            "stored_at": now_utc(),
            "text_cached": False,
            "text_path": None,
            "wiki_path": self._find_wiki_for_arxiv(arxiv_id) if arxiv_id else None,
            "notes": "",
        }
        self._set_entry(pdf_id, entry)
        return entry

    def store_file(
        self,
        src_path: Path | str,
        pdf_id: Optional[str] = None,
        title: str = "",
        source: str = SOURCE_UPLOAD,
        arxiv_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """从本地文件路径存储 PDF。

        Args:
            src_path: 源 PDF 文件路径
            pdf_id: PDF 标识符
            title: 标题
            source: 来源
            arxiv_id: 关联 arXiv ID

        Returns:
            PDF 元数据字典
        """
        src = Path(src_path)
        if not src.exists():
            raise FileNotFoundError(f"源文件不存在: {src}")
        pdf_bytes = src.read_bytes()
        return self.store_bytes(pdf_bytes, pdf_id, title, source, arxiv_id)

    # ------------------------------------------------------------------
    # arXiv PDF 下载
    # ------------------------------------------------------------------

    def ensure_pdf(
        self,
        arxiv_id: str,
        title: str = "",
        force: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """确保 arXiv 论文的 PDF 原文已存储。若已存在则直接返回，否则下载。

        Args:
            arxiv_id: arXiv 论文 ID（如 "2403.15337"）
            title: 论文标题（用于元数据）
            force: 是否强制重新下载（即使已存在）

        Returns:
            PDF 元数据字典，下载失败返回 None
        """
        arxiv_id = arxiv_id.strip()

        # 检查是否已有
        if not force:
            existing = self._get_entry(arxiv_id)
            if existing and self._pdf_file_exists(existing):
                return existing

        # 下载 PDF
        pdf_bytes = self._download_arxiv_pdf(arxiv_id)
        if not pdf_bytes:
            return None

        return self.store_bytes(
            pdf_bytes,
            pdf_id=arxiv_id,
            title=title,
            source=SOURCE_ARXIV,
            arxiv_id=arxiv_id,
        )

    def _download_arxiv_pdf(self, arxiv_id: str) -> Optional[bytes]:
        """从 arXiv 下载 PDF 原文。

        支持新旧 arXiv ID 格式：
        - 新格式：2403.15337 → https://arxiv.org/pdf/2403.15337.pdf
        - 旧格式：physics/9906053 → https://arxiv.org/pdf/physics/9906053.pdf

        下载策略（三级降级）：
        1. urllib.request（标准库，可能因 SSL 证书问题失败）
        2. curl 命令（系统命令，使用系统证书，macOS 推荐）
        3. 返回 None

        Args:
            arxiv_id: arXiv 论文 ID

        Returns:
            PDF 字节流，失败返回 None
        """
        # 构造下载 URL
        if "/" in arxiv_id:
            # 旧格式如 physics/9906053
            archive, id_part = arxiv_id.split("/", 1)
            url = ARXIV_PDF_URL_OLD.format(archive=archive, arxiv_id=id_part)
        else:
            url = ARXIV_PDF_URL.format(arxiv_id=arxiv_id)

        # 策略 1：urllib.request
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "LinSai-CoPilot/6.3 (PDF Library)"},
            )
            with urllib.request.urlopen(req, timeout=DOWNLOAD_TIMEOUT) as resp:
                pdf_bytes = resp.read()
                if len(pdf_bytes) > 1000:
                    return pdf_bytes
        except Exception:
            pass  # 降级到 curl

        # 策略 2：curl 命令（解决 macOS Python SSL 证书问题）
        try:
            result = subprocess.run(
                ["curl", "-sL", "-o", "-", "--max-time", str(DOWNLOAD_TIMEOUT),
                 "-H", "User-Agent: LinSai-CoPilot/6.3 (PDF Library)",
                 url],
                capture_output=True,
                timeout=DOWNLOAD_TIMEOUT + 10,
            )
            if result.returncode == 0 and len(result.stdout) > 1000:
                return result.stdout
        except Exception:
            pass

        return None

    # ------------------------------------------------------------------
    # PDF 检索
    # ------------------------------------------------------------------

    def get_pdf_path(self, pdf_id: str) -> Optional[Path]:
        """获取 PDF 原文的本地路径。

        Args:
            pdf_id: PDF 标识符（arxiv_id 或自定义 ID）

        Returns:
            PDF 文件的绝对路径，不存在返回 None
        """
        entry = self._get_entry(pdf_id)
        if not entry:
            return None
        if not self._pdf_file_exists(entry):
            return None
        return KNOWLEDGE_DIR / entry["pdf_path"]

    def has_pdf(self, pdf_id: str) -> bool:
        """检查是否已存储某篇论文的 PDF 原文。"""
        return self.get_pdf_path(pdf_id) is not None

    def get_info(self, pdf_id: str) -> Optional[Dict[str, Any]]:
        """获取 PDF 元数据（含关联信息）。"""
        entry = self._get_entry(pdf_id)
        if not entry:
            return None
        # 补充运行时状态
        entry = dict(entry)
        entry["file_exists"] = self._pdf_file_exists(entry)
        return entry

    def list_pdfs(
        self,
        source: Optional[str] = None,
        has_arxiv: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """列出所有 PDF 记录。

        Args:
            source: 按来源过滤（arxiv_download/user_upload/workflow）
            has_arxiv: 是否只列出有 arXiv ID 的

        Returns:
            PDF 元数据列表，按存储时间倒序
        """
        lib = self._load_library()
        papers = lib.get("papers", {})
        result = []
        for entry in papers.values():
            if source and entry.get("pdf_source") != source:
                continue
            if has_arxiv is True and not entry.get("arxiv_id"):
                continue
            if has_arxiv is False and entry.get("arxiv_id"):
                continue
            entry = dict(entry)
            entry["file_exists"] = self._pdf_file_exists(entry)
            result.append(entry)
        result.sort(key=lambda x: x.get("stored_at", ""), reverse=True)
        return result

    def list_with_paper_pool(
        self,
        paper_pool_data: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """列出 PDF 并关联论文池元数据（复用简报卡信息）。

        将 PDF 库记录与 paper-pool.json 的论文元数据（标题、方向、简报状态等）
        合并展示，实现"PDF 原文 ↔ 知识库摘要"的双向关联。

        Args:
            paper_pool_data: 论文池数据（传入避免重复加载），为 None 时自行加载

        Returns:
            合并后的记录列表，每条含 PDF 信息 + 论文池信息
        """
        if paper_pool_data is None:
            pp = load_json(MEMORY_DIR / "paper-pool.json", {})
        else:
            pp = paper_pool_data

        pdfs = self.list_pdfs()
        result = []
        for pdf in pdfs:
            arxiv_id = pdf.get("arxiv_id", "")
            pool_entry = pp.get(arxiv_id, {})
            merged = dict(pdf)
            merged["pool_title"] = pool_entry.get("title", pdf.get("title", ""))
            merged["pool_direction"] = pool_entry.get("direction", "")
            merged["pool_status"] = pool_entry.get("status", "")
            merged["pool_tldr"] = pool_entry.get("tldr", "")
            merged["pool_score"] = pool_entry.get("score", 0)
            merged["has_summary"] = bool(pdf.get("wiki_path")) or bool(pool_entry)
            result.append(merged)
        return result

    # ------------------------------------------------------------------
    # PDF 全文文本提取
    # ------------------------------------------------------------------

    def get_pdf_text(self, pdf_id: str, force: bool = False) -> Optional[str]:
        """获取 PDF 的全文文本（带缓存）。

        优先返回缓存的文本文件；若未缓存，则从 PDF 提取文本并缓存。
        文本提取策略（三级降级）：
        1. 尝试调用 deepxiv_knowledge/pdf_extractor（PyPDF2，若可用）
        2. 尝试调用系统 pdftotext 命令
        3. 回退到 document_handler 的正则方案（质量较低）

        Args:
            pdf_id: PDF 标识符
            force: 是否强制重新提取（忽略缓存）

        Returns:
            全文文本字符串，失败返回 None
        """
        entry = self._get_entry(pdf_id)
        if not entry:
            return None

        # 检查缓存
        if not force and entry.get("text_cached") and entry.get("text_path"):
            text_file = KNOWLEDGE_DIR / entry["text_path"]
            if text_file.exists():
                try:
                    return text_file.read_text(encoding="utf-8")
                except Exception:
                    pass  # 缓存损坏，重新提取

        # 获取 PDF 路径
        pdf_path = self.get_pdf_path(pdf_id)
        if not pdf_path:
            return None

        # 三级降级提取
        text = self._extract_text_deepxiv(pdf_path)
        if not text:
            text = self._extract_text_pdftotext(pdf_path)
        if not text:
            text = self._extract_text_regex(pdf_path)

        if not text:
            return None

        # 缓存文本
        text_filename = f"{safe_filename(pdf_id)}.txt"
        text_path = TEXT_CACHE_DIR / text_filename
        text_path.parent.mkdir(parents=True, exist_ok=True)
        text_path.write_text(text, encoding="utf-8")

        # 更新元数据
        entry["text_cached"] = True
        entry["text_path"] = f"raw/pdfs/_text_cache/{text_filename}"
        entry["text_extracted_at"] = now_utc()
        self._set_entry(pdf_id, entry)

        return text

    def _extract_text_deepxiv(self, pdf_path: Path) -> Optional[str]:
        """策略 1：pypdf 本地抽取（优先）/ deepxiv_knowledge/pdf_extractor。"""
        try:
            # v6.9.75: 优先 pypdf_extract_local.py（本地文件路径，venv 解释器
            # 带 pypdf；系统 python3 无 PyPDF2/pypdf，旧链路三级全败实测）
            import shutil as _shutil
            local_extractor = Path(__file__).parent / "deepxiv_knowledge" / "pypdf_extract_local.py"
            py_exe = str(Path.home() / ".venv" / "bin" / "python3")
            if local_extractor.exists() and Path(py_exe).exists():
                result = subprocess.run(
                    [py_exe, str(local_extractor), str(pdf_path)],
                    capture_output=True, text=True, timeout=60,
                )
                if result.returncode == 0 and len(result.stdout.strip()) > 200:
                    return result.stdout.strip()
            extractor_path = Path(__file__).parent / "deepxiv_knowledge" / "pdf_extractor.py"
            if not extractor_path.exists():
                return None
            # 通过 subprocess 调用，避免直接导入非标准库依赖。
            # v6.9.75: 解释器探测——系统 python3 无 PyPDF2/pypdf，优先
            # 探测带库的解释器（~/.venv/bin/python3 等）
            import shutil as _shutil
            py_candidates = [
                str(Path.home() / ".venv" / "bin" / "python3"),
                "python3",
            ]
            py_exe = next((c for c in py_candidates
                           if _shutil.which(c) or Path(c).exists()), "python3")
            result = subprocess.run(
                [py_exe, str(extractor_path), "--extract-text", str(pdf_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0 and result.stdout.strip():
                text = result.stdout.strip()
                # 过滤错误输出：deepxiv 在 PyPDF2 不可用时会输出错误信息到 stdout
                _ERROR_MARKERS = ("not available", "错误:", "Error:", "Traceback", "PDF: 0 chars")
                if len(text) > 200 and not any(m in text for m in _ERROR_MARKERS):
                    return text
            return None
        except Exception:
            return None

    def _extract_text_pdftotext(self, pdf_path: Path) -> Optional[str]:
        """策略 2：调用系统 pdftotext 命令（poppler-utils）。"""
        try:
            result = subprocess.run(
                ["pdftotext", "-q", str(pdf_path), "-"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0 and result.stdout.strip():
                text = result.stdout.strip()
                if len(text) > 100:
                    return text
            return None
        except FileNotFoundError:
            # pdftotext 未安装
            return None
        except Exception:
            return None

    def _extract_text_regex(self, pdf_path: Path) -> Optional[str]:
        """策略 3：正则提取（回退方案，质量较低）。"""
        try:
            raw = pdf_path.read_bytes()
            # 提取 PDF 文本流中的 Tj/TJ 操作符内容
            import re
            texts = []
            # 匹配 (text) Tj 模式
            for m in re.finditer(rb"\(([^)]*)\)\s*Tj", raw):
                try:
                    texts.append(m.group(1).decode("latin-1"))
                except Exception:
                    pass
            # 匹配 [(a)(b)...] TJ 模式
            for m in re.finditer(rb"\[([^\]]*)\]\s*TJ", raw):
                for part in re.finditer(rb"\(([^)]*)\)", m.group(1)):
                    try:
                        texts.append(part.group(1).decode("latin-1"))
                    except Exception:
                        pass
            text = " ".join(texts)
            return text if len(text) > 50 else None
        except Exception:
            return None

    # ------------------------------------------------------------------
    # 关联管理
    # ------------------------------------------------------------------

    def link_wiki(self, pdf_id: str, wiki_path: str) -> bool:
        """将 PDF 与知识库 wiki 摘要页面关联。

        Args:
            pdf_id: PDF 标识符
            wiki_path: wiki 页面相对路径（如 "wiki/papers/2403-15337-xxx.md"）

        Returns:
            True 表示关联成功
        """
        entry = self._get_entry(pdf_id)
        if not entry:
            return False
        entry["wiki_path"] = wiki_path
        self._set_entry(pdf_id, entry)
        return True

    def _find_wiki_for_arxiv(self, arxiv_id: str) -> Optional[str]:
        """根据 arXiv ID 查找已存在的 wiki 摘要页面。

        在 knowledge/wiki/papers/ 目录下搜索文件名含 arxiv_id 的 .md 文件。
        """
        wiki_papers = WIKI_DIR / "papers"
        if not wiki_papers.exists():
            return None
        # arxiv_id 中的点在文件名中可能被替换为连字符
        safe_id = arxiv_id.replace(".", "-").replace("/", "-")
        for f in wiki_papers.glob("*.md"):
            if arxiv_id in f.name or safe_id in f.name:
                return f"wiki/papers/{f.name}"
        return None

    def get_linked_summary(self, pdf_id: str) -> Optional[str]:
        """获取 PDF 关联的知识库摘要内容。

        Returns:
            wiki 摘要的 Markdown 文本，无关联返回 None
        """
        entry = self._get_entry(pdf_id)
        if not entry or not entry.get("wiki_path"):
            return None
        wiki_file = KNOWLEDGE_DIR / entry["wiki_path"]
        if not wiki_file.exists():
            return None
        try:
            return wiki_file.read_text(encoding="utf-8")
        except Exception:
            return None

    # ------------------------------------------------------------------
    # 删除与统计
    # ------------------------------------------------------------------

    def delete_pdf(self, pdf_id: str, delete_text: bool = True) -> bool:
        """删除 PDF 原文及其元数据。

        Args:
            pdf_id: PDF 标识符
            delete_text: 是否同时删除文本缓存

        Returns:
            True 表示删除成功
        """
        entry = self._get_entry(pdf_id)
        if not entry:
            return False

        # 删除 PDF 文件
        if entry.get("pdf_path"):
            pdf_file = KNOWLEDGE_DIR / entry["pdf_path"]
            if pdf_file.exists():
                pdf_file.unlink()

        # 删除文本缓存
        if delete_text and entry.get("text_path"):
            text_file = KNOWLEDGE_DIR / entry["text_path"]
            if text_file.exists():
                text_file.unlink()

        # 删除元数据
        with file_lock("pdf-library"):
            lib = self._load_library()
            lib.get("papers", {}).pop(pdf_id, None)
            lib["updated_at"] = now_utc()
            save_json(PDF_LIBRARY_PATH, lib)

        return True

    def stats(self) -> Dict[str, Any]:
        """返回 PDF 库统计信息。"""
        lib = self._load_library()
        papers = lib.get("papers", {})
        total_size = sum(e.get("pdf_size_bytes", 0) for e in papers.values())
        by_source: Dict[str, int] = {}
        text_cached = 0
        linked_wiki = 0
        file_exists = 0
        for e in papers.values():
            by_source[e.get("pdf_source", "unknown")] = by_source.get(e.get("pdf_source", "unknown"), 0) + 1
            if e.get("text_cached"):
                text_cached += 1
            if e.get("wiki_path"):
                linked_wiki += 1
            if self._pdf_file_exists(e):
                file_exists += 1
        return {
            "total_pdfs": len(papers),
            "file_exists": file_exists,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "by_source": by_source,
            "text_cached": text_cached,
            "linked_wiki": linked_wiki,
            "updated_at": lib.get("updated_at", ""),
        }

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------

    def _pdf_file_exists(self, entry: Dict[str, Any]) -> bool:
        """检查 PDF 文件是否实际存在于磁盘。"""
        if not entry.get("pdf_path"):
            return False
        return (KNOWLEDGE_DIR / entry["pdf_path"]).exists()

    def _find_by_sha256(self, sha: str) -> Optional[Dict[str, Any]]:
        """按 SHA-256 查找已存储的 PDF（去重）。"""
        lib = self._load_library()
        for entry in lib.get("papers", {}).values():
            if entry.get("pdf_sha256") == sha and self._pdf_file_exists(entry):
                return entry
        return None


# ---------------------------------------------------------------------------
# 便捷函数
# ---------------------------------------------------------------------------

_default_lib: Optional[PdfLibrary] = None


def get_library() -> PdfLibrary:
    """获取全局 PdfLibrary 单例。"""
    global _default_lib
    if _default_lib is None:
        _default_lib = PdfLibrary()
    return _default_lib


def ensure_pdf_for_arxiv(arxiv_id: str, title: str = "") -> Optional[Dict[str, Any]]:
    """便捷函数：确保 arXiv 论文 PDF 已下载到本地。

    Args:
        arxiv_id: arXiv 论文 ID
        title: 论文标题

    Returns:
        PDF 元数据，失败返回 None
    """
    return get_library().ensure_pdf(arxiv_id, title=title)


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_check() -> int:
    """运行模块自检。"""
    import sys

    errors = 0
    checks = 0

    def check(name: str, condition: bool, detail: str = "") -> None:
        nonlocal errors, checks
        checks += 1
        if condition:
            print(f"  ✓ {name}")
        else:
            errors += 1
            print(f"  ✗ {name}: {detail}")

    print("PDF 原文库管理器自检 (pdf_manager.py)")
    print("=" * 50)

    # 1. 路径常量
    check("PDF_DIR 定义", PDF_DIR.name == "pdfs", f"got {PDF_DIR}")
    check("PDF_LIBRARY_PATH 定义", PDF_LIBRARY_PATH.name == "pdf-library.json")

    # 2. 初始化
    lib = PdfLibrary()
    check("PdfLibrary 实例化", lib is not None)
    check("PDF_DIR 目录存在", PDF_DIR.exists())
    check("TEXT_CACHE_DIR 目录存在", TEXT_CACHE_DIR.exists())

    # 3. 空库操作
    empty_lib = load_json(PDF_LIBRARY_PATH, {"papers": {}})
    check("库元数据结构", "papers" in empty_lib, f"keys: {list(empty_lib.keys())}")

    # 4. 存储测试（用假 PDF 字节）
    fake_pdf = b"%PDF-1.4\nfake content for testing\n%%EOF"
    try:
        entry = lib.store_bytes(
            fake_pdf,
            pdf_id="test_001",
            title="测试论文",
            source="workflow",
        )
        check("store_bytes 存储", entry is not None and entry["pdf_id"] == "test_001")
        check("store_bytes SHA-256", len(entry.get("pdf_sha256", "")) == 64)
        check("store_bytes 文件大小", entry["pdf_size_bytes"] == len(fake_pdf))
        check("store_bytes 路径", entry["pdf_path"].startswith("raw/pdfs/"))
    except Exception as e:
        check("store_bytes 存储", False, str(e))
        entry = None

    # 5. 检索测试
    if entry:
        path = lib.get_pdf_path("test_001")
        check("get_pdf_path 路径", path is not None and path.exists())
        check("has_pdf", lib.has_pdf("test_001"))
        info = lib.get_info("test_001")
        check("get_info", info is not None and info["title"] == "测试论文")

    # 6. 去重测试
    try:
        dup = lib.store_bytes(
            fake_pdf,
            pdf_id="test_002",
            title="重复内容测试",
            source="workflow",
        )
        # 内容相同应返回原记录
        check("SHA-256 去重", dup["pdf_id"] == "test_001", f"got {dup['pdf_id']}")
    except Exception as e:
        check("SHA-256 去重", False, str(e))

    # 7. 列表测试
    pdfs = lib.list_pdfs()
    check("list_pdfs 非空", len(pdfs) >= 1)
    pdfs_arxiv = lib.list_pdfs(source="arxiv_download")
    check("list_pdfs 过滤", isinstance(pdfs_arxiv, list))

    # 8. 统计测试
    stats = lib.stats()
    check("stats total_pdfs", stats["total_pdfs"] >= 1)
    check("stats by_source", "workflow" in stats["by_source"])

    # 9. 文本提取测试（正则回退方案）
    if entry:
        text = lib.get_pdf_text("test_001", force=True)
        # 假 PDF 可能提取不到文本，但不应崩溃
        check("get_pdf_text 不崩溃", text is None or isinstance(text, str))

    # 10. 删除测试
    if entry:
        deleted = lib.delete_pdf("test_001")
        check("delete_pdf", deleted)
        check("删除后 has_pdf", not lib.has_pdf("test_001"))
        check("删除后文件不存在", not lib.get_pdf_path("test_001"))

    # 11. 便捷函数
    check("get_library 单例", get_library() is get_library())

    print(f"\n{'=' * 50}")
    print(f"自检完成：{checks} 项检查，{errors} 项失败")
    return errors


if __name__ == "__main__":
    import sys

    if "--self-check" in sys.argv:
        sys.exit(_self_check())

    # 演示
    print("PDF 原文库管理器 (pdf_manager.py)")
    print(f"  PDF 存储目录: {PDF_DIR}")
    print(f"  元数据文件: {PDF_LIBRARY_PATH}")
    print(f"  文本缓存: {TEXT_CACHE_DIR}")
    lib = PdfLibrary()
    stats = lib.stats()
    print(f"  已存储 PDF: {stats['total_pdfs']} 篇")
    print(f"  总大小: {stats['total_size_mb']} MB")
    print(f"\n运行 --self-check 执行自检")
