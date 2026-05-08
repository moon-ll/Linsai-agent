#!/bin/bash
# LinSai-CoPilot 桌面快捷启动

PROJECT_ROOT="$HOME/Desktop/LinSai-CoPilot"

if [ ! -d "$PROJECT_ROOT" ]; then
    echo "✗ 找不到项目目录: $PROJECT_ROOT"
    echo "请确保 LinSai-CoPilot 文件夹在桌面。"
    read -p "按回车键关闭..."
    exit 1
fi

cd "$PROJECT_ROOT"
PORT=8080
URL="http://127.0.0.1:${PORT}"
LOG="/tmp/linsai-server.log"

echo "🚀 启动林赛协作引擎..."
echo "   项目: $PROJECT_ROOT"
echo ""

# 检查端口是否已有实例
if lsof -Pi ":${PORT}" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠ 端口 ${PORT} 已有实例运行"
    echo "   正在打开浏览器..."
    open "$URL"
    read -p "按回车键关闭窗口..."
    exit 0
fi

# 检查 Python3
if ! command -v python3 >/dev/null 2>&1; then
    echo "✗ 未找到 python3，请安装 Python 3"
    read -p "按回车键关闭..."
    exit 1
fi

# 启动服务器
echo "◐ 正在启动服务器..."
nohup python3 scripts/web_server.py --port "${PORT}" > "$LOG" 2>&1 &
SERVER_PID=$!

# 等待就绪
READY=false
for i in {1..20}; do
    if curl -s "$URL/api/version" >/dev/null 2>&1; then
        READY=true
        break
    fi
    sleep 0.3
done

if [ "$READY" = true ]; then
    echo "✓ 服务器已启动 (${URL})"
    echo "   PID: $SERVER_PID"
    echo "   日志: $LOG"
    echo ""
    echo "正在打开浏览器..."
    open "$URL"
    echo ""
    echo "💡 服务器在后台运行，关闭此窗口不影响使用。"
    echo "   如需停止: kill $SERVER_PID"
else
    echo "✗ 服务器启动失败"
    echo ""
    echo "--- 错误日志 ---"
    tail -20 "$LOG" 2>/dev/null || echo "(无日志输出)"
    echo ""
    echo "常见原因:"
    echo "  1. Python 3 未安装"
    echo "  2. 端口被占用"
    echo "  3. scripts/web_server.py 文件缺失"
fi

echo ""
read -p "按回车键关闭窗口..."
