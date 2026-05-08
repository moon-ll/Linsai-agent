#!/bin/bash
"""
LinSai-CoPilot 一键启动脚本
启动 Web 服务器并自动打开浏览器

用法:
    ./scripts/launch.sh           # 默认端口 8080
    ./scripts/launch.sh 9000      # 指定端口
"""

set -e

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

PORT="${1:-8080}"
URL="http://127.0.0.1:${PORT}"

# 检查端口是否被占用
if lsof -Pi ":${PORT}" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠ 端口 ${PORT} 已被占用，尝试打开现有实例…"
    open "$URL"
    exit 0
fi

echo "🚀 启动林赛协作引擎…"
echo "   项目: ${PROJECT_ROOT}"
echo "   地址: ${URL}"
echo ""

# 启动服务器（后台）
python3 scripts/web_server.py --port "${PORT}" &
SERVER_PID=$!

# 等待服务器就绪
for i in {1..15}; do
    if curl -s "$URL/api/version" >/dev/null 2>&1; then
        echo "✓ 服务器已就绪"
        break
    fi
    sleep 0.3
done

# 打开浏览器
if command -v open >/dev/null 2>&1; then
    open "$URL"
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL"
else
    echo "请手动打开浏览器访问: ${URL}"
fi

echo ""
echo "按 Ctrl+C 停止服务器"

# 等待服务器进程
wait $SERVER_PID
