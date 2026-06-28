#!/usr/bin/env python3
"""
test_web_api.py — Web API 虚拟用户测试套件

用途：
    以"虚拟用户"身份通过 HTTP 请求测试 web_server 的所有 API 端点，
    覆盖会话/任务/知识库/技能/hermes协作中枢等功能的完整链路。

机制：
    - setup(): 创建隔离环境 + 启动 web_server 子进程（随机端口）
    - run_tests(): 用 ApiClient（urllib）发真实 HTTP 请求，断言状态码和响应
    - teardown(): 关闭子进程 + 清理临时目录

零依赖：仅用 urllib（标准库），不引入 requests。
"""

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from test_runner import TestSuite, REAL_ROOT, create_isolated_env

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


class ApiClient:
    """轻量 HTTP 客户端（零依赖，urllib 实现）。"""

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, body: Optional[Dict] = None) -> Tuple[int, Any]:
        # 对路径中的非 ASCII 字符做 URL 编码（session_id 可能含中文）
        from urllib.parse import quote
        encoded_path = quote(path, safe="/?&=%")
        url = self.base_url + encoded_path
        data = None
        headers = {"Accept": "application/json"}
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                try:
                    return resp.status, json.loads(raw)
                except json.JSONDecodeError:
                    return resp.status, raw
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            try:
                return e.code, json.loads(raw)
            except Exception:
                return e.code, raw

    def get(self, path: str) -> Tuple[int, Any]:
        return self._request("GET", path)

    def post(self, path: str, body: Optional[Dict] = None) -> Tuple[int, Any]:
        return self._request("POST", path, body)

    def put(self, path: str, body: Optional[Dict] = None) -> Tuple[int, Any]:
        return self._request("PUT", path, body)

    def delete(self, path: str) -> Tuple[int, Any]:
        return self._request("DELETE", path)


def _find_free_port() -> int:
    """找一个可用的空闲端口。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _copy_web_essentials(tmp_root: Path):
    """复制 web_server 启动必需的文件到隔离环境。

    create_isolated_env 只复制了 persona/skills/knowledge 索引/memory，
    但 web_server 还需要 VERSION、web/ 前端、templates 等。
    """
    # VERSION 文件（/api/version 读它）
    version_src = REAL_ROOT / "VERSION"
    if version_src.exists():
        shutil.copy(version_src, tmp_root / "VERSION")
    # web/ 前端目录（静态文件服务）
    web_src = REAL_ROOT / "web"
    if web_src.exists():
        shutil.copytree(web_src, tmp_root / "web", dirs_exist_ok=True)
    # knowledge/templates（stub 创建等可能用到）
    templates_src = REAL_ROOT / "knowledge" / "templates"
    if templates_src.exists():
        shutil.copytree(templates_src, tmp_root / "knowledge" / "templates", dirs_exist_ok=True)
    # .env（llm_router 读 API key，虽测试不发真实 LLM 请求，但 import 时可能需要）
    env_src = REAL_ROOT / ".env"
    if env_src.exists():
        shutil.copy(env_src, tmp_root / ".env")


def _wait_for_server(url: str, timeout: int = 30) -> bool:
    """等待 web_server 就绪（轮询 /api/version）。"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url + "/api/version", timeout=3) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


class WebApiSuite(TestSuite):
    """Web API 虚拟用户测试套件。"""

    def __init__(self):
        super().__init__("Web API 虚拟用户测试")
        self.client: Optional[ApiClient] = None
        self.server_proc: Optional[subprocess.Popen] = None
        self.tmp_root: Optional[Path] = None
        self.port = 0

    def setup(self):
        """创建隔离环境 + 启动 web_server 子进程。"""
        self.tmp_root = create_isolated_env()
        # 补充 web_server 启动必需的文件（create_isolated_env 不含这些）
        _copy_web_essentials(self.tmp_root)
        self.port = _find_free_port()
        env = dict(os.environ)
        env["PYTHONPATH"] = str(_SCRIPTS_DIR)
        # 屏蔽可能的旧环境变量干扰
        env.pop("MINIMAX_MODEL", None)
        self.server_proc = subprocess.Popen(
            [sys.executable, str(_SCRIPTS_DIR / "web_server.py"),
             "--port", str(self.port), "--root", str(self.tmp_root)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )
        base_url = f"http://127.0.0.1:{self.port}"
        if not _wait_for_server(base_url, timeout=30):
            raise RuntimeError("web_server 启动超时")
        self.client = ApiClient(base_url, timeout=15)

    def teardown(self):
        """关闭子进程 + 清理临时目录。"""
        if self.server_proc:
            self.server_proc.terminate()
            try:
                self.server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_proc.kill()
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    # ---- 断言辅助 ----

    def assert_status(self, code: int, expected: int, name: str) -> bool:
        """断言 HTTP 状态码。"""
        passed = code == expected
        msg = "" if passed else f"期望 {expected}，实际 {code}"
        self.results.append(self._result(name, passed, msg))
        return passed

    def _result(self, name, passed, msg=""):
        from test_runner import TestResult
        return TestResult(name, passed, 0.0, msg)

    def assert_json_field(self, data: Any, key: str, name: str, expected: Any = None) -> bool:
        """断言 JSON 响应包含某字段（可选校验值）。"""
        if not isinstance(data, dict):
            self.results.append(self._result(name, False, "响应非 JSON 对象"))
            return False
        has = key in data
        if not has:
            self.results.append(self._result(name, False, f"缺少字段 {key}"))
            return False
        if expected is not None and data[key] != expected:
            self.results.append(self._result(name, False, f"{key}={data[key]}，期望 {expected}"))
            return False
        self.results.append(self._result(name, True))
        return True

    # ---- 测试用例 ----

    def run_tests(self):
        c = self.client
        assert c is not None

        # === 基础端点 ===
        code, data = c.get("/api/version")
        self.assert_status(code, 200, "GET /api/version")
        self.assert_json_field(data, "version", "version 含版本号")

        code, _ = c.get("/api/providers")
        self.assert_status(code, 200, "GET /api/providers")

        code, _ = c.get("/api/skills")
        self.assert_status(code, 200, "GET /api/skills")

        # === 会话管理 ===
        code, data = c.post("/api/sessions", {"topic": "测试会话", "mode": "co-working"})
        self.assert_status(code, 200, "POST /api/sessions 创建")
        sid = data.get("session_id", "") if isinstance(data, dict) else ""
        self.assert_true(bool(sid), "会话ID非空")

        code, data = c.get("/api/sessions")
        self.assert_status(code, 200, "GET /api/sessions 列表")
        self.assert_true(isinstance(data, list), "会话列表是数组")

        if sid:
            # 加载历史
            code, data = c.get(f"/api/sessions/{sid}/messages")
            self.assert_status(code, 200, "GET 会话历史消息")

        # === 任务管理 ===
        code, data = c.get("/api/tasks")
        self.assert_status(code, 200, "GET /api/tasks 列表")

        # === 知识库 ===
        code, _ = c.get("/api/knowledge/search?q=HHG")
        self.assert_status(code, 200, "GET 知识库搜索")

        code, _ = c.get("/api/knowledge/wiki")
        self.assert_status(code, 200, "GET wiki 列表")

        code, _ = c.get("/api/knowledge/aliases")
        self.assert_status(code, 200, "GET aliases")

        # === v2.7.0 项目面板 ===
        code, _ = c.get("/api/projects")
        self.assert_status(code, 200, "GET /api/projects")

        code, data = c.get("/api/projects/nsfc/dashboard")
        self.assert_status(code, 200, "GET NSFC 仪表盘")
        self.assert_json_field(data, "available", "NSFC dashboard 含 available")

        code, _ = c.get("/api/projects/nsfc/decisions?limit=3")
        self.assert_status(code, 200, "GET NSFC 决策")

        code, _ = c.get("/api/projects/nsfc/chapters")
        self.assert_status(code, 200, "GET NSFC 章节")

        code, _ = c.get("/api/projects/papers/candidates")
        self.assert_status(code, 200, "GET 文献候选")

        code, _ = c.get("/api/projects/papers/briefings")
        self.assert_status(code, 200, "GET 文献简报列表")

        # === v2.7.0 hermes 控制台 ===
        code, data = c.get("/api/hermes/cron")
        self.assert_status(code, 200, "GET hermes cron 列表")
        self.assert_json_field(data, "jobs", "cron 含 jobs 字段")

        code, _ = c.get("/api/sync/status")
        self.assert_status(code, 200, "GET 同步状态")

        # === 静态文件服务 ===
        code, _ = c.get("/web/index.html")
        self.assert_status(code, 200, "GET 首页静态文件")

        code, _ = c.get("/web/js/app.js")
        self.assert_status(code, 200, "GET app.js 静态文件")

        # === provider 切换（不改变实际值，测试 API 可用性）===
        code, _ = c.get("/api/providers/current")
        self.assert_status(code, 200, "GET 当前 provider")

        # === v3.5 课题指导路由（research）===
        code, data = c.get("/api/research/projects")
        self.assert_status(code, 200, "GET /api/research/projects 列表")
        self.assert_json_field(data, "projects", "research 列表含 projects 字段")

        code, data = c.post("/api/research/projects", {
            "name": "WebAPI自检课题", "goal": "验证课题路由",
        })
        self.assert_status(code, 200, "POST /api/research/projects 创建")
        research_pid = data.get("project_id", "") if isinstance(data, dict) else ""
        self.assert_true(bool(research_pid), "research 课题ID非空")

        if research_pid:
            code, data = c.get(f"/api/research/projects/{research_pid}")
            self.assert_status(code, 200, "GET /api/research/projects/{id} 详情")
            self.assert_json_field(data, "project_id", "research 详情含 project_id")

            # 清理：删除测试课题
            code, _ = c.delete(f"/api/research/projects/{research_pid}")
            self.assert_status(code, 200, "DELETE /api/research/projects/{id} 清理")

        # === 自主学习路由（learning）===
        code, data = c.get("/api/learning/log")
        self.assert_status(code, 200, "GET /api/learning/log")
        self.assert_json_field(data, "log", "learning log 含 log 字段")

        code, data = c.get("/api/learning/queue")
        self.assert_status(code, 200, "GET /api/learning/queue")
        self.assert_json_field(data, "queue", "learning queue 含 queue 字段")

        # === 上传路由（upload）===
        code, data = c.post("/api/upload", {
            "filename": "webapi_test.txt",
            "content": "WebAPI 自检上传测试文件",
            "category": "notes",
        })
        self.assert_status(code, 200, "POST /api/upload 文件上传")
        self.assert_json_field(data, "success", "upload 返回 success 字段")

        # === 系统路由（system）===
        code, data = c.get("/api/heartbeat")
        self.assert_status(code, 200, "GET /api/heartbeat 系统心跳")

        # === 知识库 wiki 列表（字段校验）===
        code, data = c.get("/api/knowledge/wiki")
        self.assert_status(code, 200, "GET /api/knowledge/wiki 列表（复测）")
        self.assert_json_field(data, "pages", "wiki 列表含 pages 字段")


if __name__ == "__main__":
    suite = WebApiSuite()
    import time as _time
    t0 = _time.time()
    try:
        suite.setup()
        suite.run_tests()
    except Exception as e:
        print(f"⚠ 套件运行异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        suite.teardown()
    suite.duration = _time.time() - t0

    from test_runner import print_report
    print_report([suite])
    sys.exit(0 if suite.summary()["failed"] == 0 else 1)
