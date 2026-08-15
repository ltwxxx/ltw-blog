#!/usr/bin/env bash
# 仅用 Docker（无需 Docker Compose）构建并运行本项目
# 用法: ./run-docker.sh  或  HOMEPAGE_PORT=8082 ./run-docker.sh（端口被占用时）
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

IMAGE_NAME="homepage-blog"
CONTAINER_NAME="homepage-blog"
HOST_PORT="${HOMEPAGE_PORT:-8081}"

echo "=== 构建镜像: $IMAGE_NAME ==="
docker build -t "$IMAGE_NAME" .

echo ""
echo "=== 停止并删除旧容器（若存在）==="
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

echo ""
echo "=== 启动容器（端口 $HOST_PORT -> 容器 83）==="
docker run -d \
  --name "$CONTAINER_NAME" \
  -p "${HOST_PORT}:83" \
  --restart unless-stopped \
  "$IMAGE_NAME"

echo ""
echo "✅ 容器已启动。访问: http://localhost:$HOST_PORT"
echo "   查看日志: docker logs -f $CONTAINER_NAME"
echo "   停止:     docker stop $CONTAINER_NAME"
