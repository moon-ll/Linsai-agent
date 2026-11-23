"""
checkpoint.py — 进度持久化管理
支持断点续传，记录每篇论文的 fetch 状态。
"""

import json, sys
from pathlib import Path
from datetime import datetime, timezone

class Checkpoint:
    def __init__(self, path: Path):
        self.path = path
        self.data: dict = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except Exception:
                pass
        return {"papers": {}, "meta": {"total": 0, "completed": 0, "failed": 0}}

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2))

    def set_status(self, arxiv_id: str, status: str, error: str = ""):
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        p = self.data["papers"].setdefault(arxiv_id, {})
        p["status"] = status
        p["updated_at"] = now
        if error:
            p["error"] = error
        self._refresh_stats()
        self.save()

    def _refresh_stats(self):
        papers = self.data["papers"]
        done = [v for v in papers.values() if v.get("status") in ("verified", "failed")]
        self.data["meta"]["completed"] = len([v for v in done if v.get("status") == "verified"])
        self.data["meta"]["failed"] = len([v for v in done if v.get("status") == "failed"])
        self.data["meta"]["total"] = len(papers)

    def get_status(self, arxiv_id: str) -> str:
        return self.data["papers"].get(arxiv_id, {}).get("status", "pending")

    def get_pending(self, all_ids: list) -> list:
        """返回尚未完成的论文 ID 列表（按原顺序）。"""
        return [aid for aid in all_ids if self.get_status(aid) not in ("verified", "failed")]

    def report(self) -> str:
        m = self.data["meta"]
        return (f"[Checkpoint] {m['completed']}/{m['total']} 完成 "
                f"({m['failed']} 失败) | "
                f"{m['total']-m['completed']-m['failed']} 待处理")

if __name__ == "__main__":
    import argparse
    p = Path("knowledge/raw/checkpoint.json")
    cp = Checkpoint(p)
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        print(cp.report())
    elif len(sys.argv) > 2:
        cp.set_status(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
        print(f"[{sys.argv[2]}] → {sys.argv[3]}")
