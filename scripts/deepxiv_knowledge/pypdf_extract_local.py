"""pypdf_extract_local.py — 本地 PDF 全文抽取（v6.9.75）。

用法：python3 pypdf_extract_local.py <本地PDF路径>
输出：全文文本到 stdout（失败退出码 1）。

背景：pdf_extractor.py 的 --extract-text 只支持 arXiv ID 下载模式，
本脚本补本地文件路径（优先 PyPDF2，兼容 pypdf 后继版）。
"""
import sys

try:
    from PyPDF2 import PdfReader
except ImportError:
    from pypdf import PdfReader  # type: ignore


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: pypdf_extract_local.py <pdf路径>", file=sys.stderr)
        return 1
    path = sys.argv[1]
    try:
        reader = PdfReader(path)
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        text = "\n".join(parts).strip()
        if len(text) < 100:
            print(f"PDF: {len(text)} chars, 页数: {len(reader.pages)}", file=sys.stderr)
            return 1
        sys.stdout.write(text)
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
