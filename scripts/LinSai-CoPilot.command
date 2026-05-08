#!/bin/bash
# LinSai-CoPilot macOS 快捷启动
# 将此文件放到桌面，双击即可启动

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

PORT=8080
URL="http://127.0.0.1:${PORT}"

# 检查端口占用
if lsof -Pi ":${PORT}" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "端口 ${PORT} 已有实例运行，正在打开浏览器…"
    open "$URL"
    sleep 2
    exit 0
fi

echo "🚀 启动林赛协作引擎…"
echo "   地址: ${URL}"
echo ""

python3 scripts/web_server.py --port "${PORT}" &
SERVER_PID=$!

# 等待就绪
for i in {1..15}; do
    if curl -s "$URL/api/version" >/dev/null 2>&1; then
        break
    fi
    sleep 0.3
done

open "$URL"

echo "✓ 服务器已启动，按 Ctrl+C 停止"
echo ""

# 保持终端打开
wait $SERVER_PID
