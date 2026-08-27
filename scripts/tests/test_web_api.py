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
import signal
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
        except (urllib.error.URLError, socket.timeout, ConnectionError, OSError) as e:
            # 网络层失败（超时/连接拒绝等）→ 返回 0 让断言判失败，
            # 不让异常炸穿 run_tests 导致整套件崩溃（v6.9.54：
            # 此前 /api/heartbeat 超时抛 socket.timeout 直接蒸发整套件）
            return 0, f"网络错误: {type(e).__name__}: {e}"

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


def _match_orphan_server(cmdline: str) -> bool:
    """判断一条 ps command 是否为泄漏的测试 web_server（纯函数，可测）。

    匹配条件（三者同时满足，正式实例无 --root 不会被误伤）：
    - 命令行含 web_server.py
    - 带有 --root 参数（仅测试这样启动）
    - --root 指向 linsai_test_* 临时隔离目录
    """
    return ("web_server.py" in cmdline and "--root" in cmdline
            and "linsai_test_" in cmdline)


def _reap_orphan_servers(exclude_pids=()) -> int:
    """清理孤儿测试 server 进程，返回清理数量（v6.9.54）。

    8 月以来历史泄漏累计 50+ 个（teardown 被跳过的年代遗留），
    每次运行本套件时自愈清扫一次，防止任何新路径的泄漏累积。
    """
    try:
        out = subprocess.run(
            ["ps", "-eo", "pid=,command="],
            capture_output=True, text=True, timeout=10,
        ).stdout
    except Exception:
        return 0
    killed = 0
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        pid_s, _, cmd = line.partition(" ")
        try:
            pid = int(pid_s)
        except ValueError:
            continue
        if pid in exclude_pids or pid == os.getpid():
            continue
        if _match_orphan_server(cmd):
            try:
                os.kill(pid, signal.SIGKILL)
                killed += 1
            except (ProcessLookupError, PermissionError):
                pass
    return killed


def _kill_proc_group(proc: subprocess.Popen) -> None:
    """按进程组终止子进程（SIGTERM → SIGKILL），覆盖孙进程。"""
    try:
        pgid = os.getpgid(proc.pid)
    except ProcessLookupError:
        return
    try:
        os.killpg(pgid, signal.SIGTERM)
        proc.wait(timeout=5)
        return
    except (subprocess.TimeoutExpired, ProcessLookupError):
        pass
    try:
        os.killpg(pgid, signal.SIGKILL)
        proc.wait(timeout=5)
    except Exception:
        pass


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
        # 自愈清扫历史泄漏的孤儿测试 server（v6.9.54）
        reaped = _reap_orphan_servers()
        if reaped:
            print(f"○ 清理 {reaped} 个历史泄漏的测试 web_server 进程")
        self.tmp_root = create_isolated_env()
        # 补充 web_server 启动必需的文件（create_isolated_env 不含这些）
        _copy_web_essentials(self.tmp_root)
        # 关闭自主学习外呼（v6.9.54）：heartbeat 的学习机会检测内含
        # arXiv/Wikipedia 检索（实测 50s+），CI 测试不应依赖外网
        # （与"零成本不调 LLM API"原则一致）
        cfg_path = self.tmp_root / "memory" / "learning-config.json"
        if cfg_path.exists():
            try:
                cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
                cfg["auto_enabled"] = False
                cfg_path.write_text(
                    json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                pass
        self.port = _find_free_port()
        env = dict(os.environ)
        env["PYTHONPATH"] = str(_SCRIPTS_DIR)
        # 屏蔽可能的旧环境变量干扰
        env.pop("MINIMAX_MODEL", None)
        # start_new_session：子进程独立进程组，teardown 可整组回收（含孙进程）
        self.server_proc = subprocess.Popen(
            [sys.executable, str(_SCRIPTS_DIR / "web_server.py"),
             "--port", str(self.port), "--root", str(self.tmp_root)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
            start_new_session=True,
        )
        base_url = f"http://127.0.0.1:{self.port}"
        if not _wait_for_server(base_url, timeout=30):
            raise RuntimeError("web_server 启动超时")
        self.client = ApiClient(base_url, timeout=30)

    def teardown(self):
        """关闭子进程 + 清理临时目录。"""
        if self.server_proc:
            _kill_proc_group(self.server_proc)
            self.server_proc = None
        # 兜底：按 --root 匹配杀掉本套件遗留的任何 server 进程
        if self.tmp_root:
            _reap_orphan_servers()
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

        # === 路由覆盖扩展（v3.5.7）：提升路由覆盖率 18% → 25%+ ===
        for _t in [
            self.test_research_extended_routes,
            self.test_tasks_crud_routes,
            self.test_skills_routes,
            self.test_system_routes,
            self.test_kb_extended_routes,
            self.test_lifecycle_console_orchestrator_pipeline_routes,
        ]:
            try:
                _t()
            except Exception as e:
                self.results.append(
                    self._result(_t.__name__, False, f"{type(e).__name__}: {e}")
                )

    # ------------------------------------------------------------------
    # 路由覆盖扩展（v3.5.7）
    # ------------------------------------------------------------------

    def test_research_extended_routes(self):
        """research 路由扩展：单元列表/创建、课题记忆、工作流规划。

        需先创建临时课题，测试完成后在 finally 中删除，避免残留。
        """
        c = self.client
        code, data = c.post("/api/research/projects", {
            "name": "路由扩展自检课题", "goal": "验证扩展路由",
        })
        self.assert_status(code, 200, "POST research 创建课题（扩展）")
        pid = data.get("project_id", "") if isinstance(data, dict) else ""
        self.assert_true(bool(pid), "research 课题ID非空（扩展）")
        if not pid:
            return
        try:
            # GET 单元列表
            code, data = c.get(f"/api/research/projects/{pid}/units")
            self.assert_status(code, 200, "GET /api/research/projects/{id}/units")
            self.assert_json_field(data, "units", "units 列表含 units 字段")

            # POST 创建单元
            code, data = c.post(f"/api/research/projects/{pid}/units", {
                "title": "扩展测试单元",
                "acceptance_criteria": ["验证路由可达"],
            })
            self.assert_status(code, 200, "POST /api/research/projects/{id}/units")
            self.assert_json_field(data, "unit_id", "创建单元含 unit_id")

            # GET 课题记忆
            code, data = c.get(f"/api/research/projects/{pid}/memory")
            self.assert_status(code, 200, "GET /api/research/projects/{id}/memory")
            self.assert_json_field(data, "context", "memory 含 context 字段")

            # POST 工作流规划（批量规划单元）
            code, data = c.post(f"/api/research/projects/{pid}/workflow/plan", {
                "unit_specs": [
                    {"title": "规划单元A", "acceptance_criteria": ["完成调研"]},
                ],
            })
            self.assert_status(code, 200, "POST /api/research/projects/{id}/workflow/plan")
            self.assert_json_field(data, "unit_ids", "workflow/plan 含 unit_ids")
        finally:
            # 清理：删除测试课题（含其单元/知识库/记忆）
            c.delete(f"/api/research/projects/{pid}")

    def test_tasks_crud_routes(self):
        """tasks 路由扩展：创建/更新/删除。

        创建后记录 task_id，测试完成后删除；异常时尝试清理。
        """
        c = self.client
        code, data = c.post("/api/tasks", {
            "title": "WebAPI扩展自检任务", "priority": "medium",
        })
        self.assert_status(code, 200, "POST /api/tasks 创建（扩展）")
        tid = data.get("task_id", "") if isinstance(data, dict) else ""
        self.assert_true(bool(tid), "任务ID非空（扩展）")
        if not tid:
            return
        try:
            # PUT 更新任务字段
            code, data = c.put(f"/api/tasks/{tid}", {"priority": "high"})
            self.assert_status(code, 200, "PUT /api/tasks/{id} 更新")
            self.assert_json_field(data, "success", "更新返回 success")

            # DELETE 删除任务
            code, data = c.delete(f"/api/tasks/{tid}")
            self.assert_status(code, 200, "DELETE /api/tasks/{id} 删除")
            self.assert_json_field(data, "success", "删除返回 success")
        except Exception:
            # 异常时尝试清理，避免残留任务
            try:
                c.delete(f"/api/tasks/{tid}")
            except Exception:
                pass
            raise

    def test_skills_routes(self):
        """skills 路由：列表与配置。"""
        c = self.client
        code, _ = c.get("/api/skills")
        self.assert_status(code, 200, "GET /api/skills 列表（扩展）")
        code, data = c.get("/api/skills/config")
        self.assert_status(code, 200, "GET /api/skills/config 配置")
        self.assert_json_field(data, "mode", "skills config 含 mode")

    def test_system_routes(self):
        """system 路由扩展：健康检查、版本信息、工具与用量。

        /api/system/health、/api/system/version 无独立路由，
        分别映射到 /api/heartbeat、/api/version。
        """
        c = self.client
        # 健康检查（/api/system/health → /api/heartbeat）
        code, _ = c.get("/api/heartbeat")
        self.assert_status(code, 200, "GET /api/heartbeat 健康检查（扩展）")
        # 版本信息（/api/system/version → /api/version）
        code, data = c.get("/api/version")
        self.assert_status(code, 200, "GET /api/version 版本信息（扩展）")
        self.assert_json_field(data, "version", "version 含版本号（扩展）")
        # 额外系统路由覆盖
        code, _ = c.get("/api/tools")
        self.assert_status(code, 200, "GET /api/tools 工具列表")
        code, _ = c.get("/api/usage")
        self.assert_status(code, 200, "GET /api/usage 用量统计")

    def test_kb_extended_routes(self):
        """kb 路由扩展：文件列表、搜索、图谱、健康度。"""
        c = self.client
        code, _ = c.get("/api/knowledge/files")
        self.assert_status(code, 200, "GET /api/knowledge/files 文件列表")
        code, _ = c.get("/api/knowledge/search?q=test")
        self.assert_status(code, 200, "GET /api/knowledge/search?q=test 搜索（扩展）")
        code, _ = c.get("/api/knowledge/graph")
        self.assert_status(code, 200, "GET /api/knowledge/graph 图谱")
        code, _ = c.get("/api/knowledge/health")
        self.assert_status(code, 200, "GET /api/knowledge/health 健康度")

    def test_lifecycle_console_orchestrator_pipeline_routes(self):
        """生命周期 / 控制台 / 总控 / 管线路由冒烟测试。

        注册临时 proposal，验证相关端点可达且返回预期字段，
        测试完成后归档并删除临时目录（隔离环境最终也会清理）。
        """
        c = self.client
        test_pid = "webapi-lifecycle-test"

        # 注册课题
        code, data = c.post("/api/lifecycle/register", {
            "proposal_id": test_pid,
            "project_type": "general",
        })
        self.assert_status(code, 200, "POST /api/lifecycle/register 注册课题")

        try:
            # 生命周期仪表盘
            code, data = c.get("/api/lifecycle/dashboard")
            self.assert_status(code, 200, "GET /api/lifecycle/dashboard")
            self.assert_json_field(data, "status", "lifecycle dashboard 含 status", expected="ok")

            # 按状态列表
            code, data = c.get("/api/lifecycle/list/drafts")
            self.assert_status(code, 200, "GET /api/lifecycle/list/drafts")

            # 控制台
            code, data = c.get("/api/console/flow")
            self.assert_status(code, 200, "GET /api/console/flow")
            self.assert_json_field(data, "status", "console/flow 含 status", expected="ok")

            code, data = c.get("/api/console/agents")
            self.assert_status(code, 200, "GET /api/console/agents")
            self.assert_json_field(data, "status", "console/agents 含 status", expected="ok")

            code, data = c.get("/api/console/alerts")
            self.assert_status(code, 200, "GET /api/console/alerts")
            self.assert_json_field(data, "status", "console/alerts 含 status", expected="ok")

            # 总控面板
            code, data = c.get("/api/orchestrator/dashboard")
            self.assert_status(code, 200, "GET /api/orchestrator/dashboard")

            # 管线
            code, data = c.get("/api/pipeline/stages")
            self.assert_status(code, 200, "GET /api/pipeline/stages")

            code, data = c.get(f"/api/pipeline/{test_pid}/state")
            self.assert_status(code, 200, f"GET /api/pipeline/{test_pid}/state")
        finally:
            # 归档并删除临时课题，避免污染
            try:
                c.post(f"/api/lifecycle/{test_pid}/transition", {"to_stage": "archived", "reason": "webapi test cleanup"})
            except Exception:
                pass
            try:
                import shutil
                from pathlib import Path
                archive_dir = self.tmp_root / "research_proposals" / "archived" / test_pid
                if archive_dir.exists():
                    shutil.rmtree(archive_dir)
            except Exception:
                pass


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
