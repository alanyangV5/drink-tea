#!/bin/bash

# 来喝茶项目 - 更新脚本
# 使用方法：
#   cd /opt/drinktea/deploy
#   sudo ./update.sh

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 检查 root 权限
if [[ $EUID -ne 0 ]]; then
    echo "此脚本需要 root 权限运行"
    echo "请使用: sudo $0"
    exit 1
fi

log_info "==================================="
log_info "来喝茶项目 - 更新脚本"
log_info "==================================="
echo ""

# 备份当前数据库
log_info "备份数据库..."
BACKUP_DIR="/opt/drinktea/backups"
mkdir -p "$BACKUP_DIR"
cp /opt/drinktea/backend/data/drinktea.db \
   "$BACKUP_DIR/drinktea.db.$(date +%Y%m%d_%H%M%S)"
log_info "数据库备份完成"

# 拉取最新代码
log_info "拉取最新代码..."
cd /opt/drinktea
# 如果是 git 仓库
if [[ -d .git ]]; then
    git pull
    log_info "代码更新完成"
else
    log_warn "不是 Git 仓库，跳过代码拉取"
    log_warn "请手动上传新代码"
fi

# 构建前端
log_info "重新构建用户端前端..."
cd /opt/drinktea/apps/user-web
npm install
npm run build

log_info "重新构建管理端前端..."
cd /opt/drinktea/apps/admin-web
npm install
npm run build

# 更新后端依赖
log_info "更新后端依赖..."
cd /opt/drinktea/backend
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 数据库迁移（如果需要）
# python3 -c "from app.db import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# 重启服务
log_info "重启服务..."
systemctl restart drinktea-backend
systemctl restart nginx

# 等待服务启动
sleep 3

# 健康检查
if systemctl is-active --quiet drinktea-backend; then
    log_info "✓ 后端服务运行正常"
else
    echo "✗ 后端服务启动失败"
    systemctl status drinktea-backend
    exit 1
fi

if systemctl is-active --quiet nginx; then
    log_info "✓ Nginx 服务运行正常"
else
    echo "✗ Nginx 服务启动失败"
    systemctl status nginx
    exit 1
fi

echo ""
log_info "==================================="
log_info "更新完成！"
log_info "==================================="
echo ""
log_info "如遇问题，可从以下位置恢复数据库："
log_info "  $BACKUP_DIR/"
echo ""
