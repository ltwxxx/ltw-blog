#!/bin/bash
# 免密版：一键更新个人主页（适配服务器 43.139.192.176）
# 已配置SSH密钥免密，无需输入任何密码

# ====================== 仅需修改这1处 ======================
LOCAL_CODE_DIR="/home/ltw/files/第二版个人博客"  # 改成你本地存放个人主页代码的实际目录
# 示例：如果代码在桌面，就改成 /home/ltw/Desktop/homepage
# ==========================================================
# 以下参数已适配你的服务器，无需修改
SERVER_IP="43.139.192.176"        # 你的服务器IP
SERVER_USER="root"                 # 服务器SSH用户名（默认root）
SERVER_DIR="/www/wwwroot/homepageltw"  # 服务器代码/更新脚本目录（宝塔默认）
HOME_PAGE_PORT="8080"              # 个人主页访问端口（可改成你实际用的端口）

# 定义颜色输出（方便看执行状态）
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # 重置颜色

# 日志打印函数
log() {
    local msg="$1"
    local color="$2"
    echo -e "${color}[$(date +'%Y-%m-%d %H:%M:%S')] $msg${NC}"
}

# 第一步：检查本地代码目录是否存在
log "=== 检查本地代码目录 ===" $YELLOW
if [ ! -d "$LOCAL_CODE_DIR" ]; then
    log "错误：本地代码目录 $LOCAL_CODE_DIR 不存在！请核对路径" $RED
    exit 1
fi
log "本地代码目录检查通过✅" $GREEN

# 第二步：先删除服务器上的 data 目录，确保完全同步
log "=== 删除服务器上的 data 目录 ===" $YELLOW
ssh "$SERVER_USER"@"$SERVER_IP" "rm -rf $SERVER_DIR/data"
if [ $? -eq 0 ]; then
    log "服务器 data 目录删除成功✅" $GREEN
else
    log "警告：删除服务器 data 目录失败（可能目录不存在，继续执行）" $YELLOW
fi

# 第三步：免密上传本地代码到服务器
log "=== 免密上传代码到服务器 43.139.192.176 ===" $YELLOW
scp -r "$LOCAL_CODE_DIR"/* "$SERVER_USER"@"$SERVER_IP":"$SERVER_DIR"/
if [ $? -eq 0 ]; then
    log "代码上传成功✅" $GREEN
else
    log "代码上传失败！请检查：1.本地代码路径 2.服务器22端口是否放行" $RED
    exit 1
fi

# 第四步：免密远程执行服务器更新脚本
log "=== 免密执行服务器更新脚本 ===" $YELLOW
ssh "$SERVER_USER"@"$SERVER_IP" "bash $SERVER_DIR/update_homepage.sh"
if [ $? -eq 0 ]; then
    log "=== 个人主页更新完成！===" $GREEN
    log "你的个人主页访问地址：http://$SERVER_IP:$HOME_PAGE_PORT" $YELLOW
else
    log "服务器脚本执行失败！可登录宝塔→终端，执行：cat /tmp/homepage_update.log 查看错误" $RED
    exit 1
fi