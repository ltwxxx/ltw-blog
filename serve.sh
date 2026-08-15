#!/usr/bin/env bash
# 用本地静态服务器打开 html 目录，方便运行 gen.py 后直接刷新看效果（类似 Live Server）
# 用法: ./serve.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PORT="${PORT:-9000}"
HTML_DIR="html"

if [ ! -d "$HTML_DIR" ]; then
    echo "❌ 目录不存在: $HTML_DIR，请先运行 gen.py 生成"
    exit 1
fi

echo "📂 正在服务: $SCRIPT_DIR/$HTML_DIR"
echo "🌐 在浏览器打开: http://localhost:$PORT/home.html"
echo "⏹️  按 Ctrl+C 停止"
echo ""

python3 -m http.server "$PORT" --directory "$HTML_DIR"
