#!/bin/bash

# 来喝茶项目 - 自动部署脚本
# 使用方法：
#   1. 将项目上传到服务器 /opt/drinktea
#   2. cd /opt/drinktea/deploy
#   3. chmod +x deploy.sh
#   4. sudo ./deploy.sh

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否以 root 权限运行
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要 root 权限运行"
        log_info "请使用: sudo $0"
        exit 1
    fi
}

# 检查系统环境
check_system() {
    log_info "检查系统环境..."

    # 检查操作系统
    if [[ ! -f /etc/os-release ]]; then
        log_error "无法检测操作系统"
        exit 1
    fi

    . /etc/os-release
    log_info "操作系统: $PRETTY_NAME"

    # 检查是否为 Ubuntu/Debian
    if [[ "$ID" != "ubuntu" ]] && [[ "$ID" != "debian" ]]; then
        log_warn "此脚本主要用于 Ubuntu/Debian 系统"
        log_warn "在其他系统上可能需要手动调整"
    fi
}

# 安装系统依赖
install_dependencies() {
    log_info "安装系统依赖..."

    # 更新软件包列表
    apt update

    # 安装必要软件包
    apt install -y \
        python3 \
        python3-venv \
        python3-pip \
        nginx \
        git \
        curl \
        build-essential

    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        log_info "安装 Node.js 20.x..."
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
        apt install -y nodejs
    else
        log_info "Node.js 已安装: $(node --version)"
    fi

    # 验证安装
    log_info "Python 版本: $(python3 --version)"
    log_info "Node.js 版本: $(node --version)"
    log_info "Nginx 版本: $(nginx -v 2>&1)"
}

# 配置应用目录
setup_directories() {
    log_info "配置应用目录..."

    APP_DIR="/opt/drinktea"

    # 创建必要的目录
    mkdir -p "$APP_DIR/backend/data/uploads"
    mkdir -p "$APP_DIR/backend/logs"

    # 设置权限
    chown -R www-data:www-data "$APP_DIR/backend"
    chmod -R 755 "$APP_DIR/backend"
}

# 构建前端
build_frontend() {
    log_info "构建用户端前端..."
    cd /opt/drinktea/apps/user-web
    npm install
    npm run build

    log_info "构建管理端前端..."
    cd /opt/drinktea/apps/admin-web
    npm install
    npm run build

    log_info "前端构建完成"
}

# 配置后端
setup_backend() {
    log_info "配置后端..."

    cd /opt/drinktea/backend

    # 创建虚拟环境
    if [[ ! -d .venv ]]; then
        log_info "创建 Python 虚拟环境..."
        python3 -m venv .venv
    fi

    # 激活虚拟环境并安装依赖
    log_info "安装 Python 依赖..."
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

    # 检查 .env 文件
    if [[ ! -f .env ]]; then
        log_warn ".env 文件不存在，从 .env.example 复制..."
        if [[ -f .env.example ]]; then
            cp .env.example .env
            log_error "请编辑 /opt/drinktea/backend/.env 文件，配置必要的环境变量！"
            log_error "特别是 ADMIN_PASSWORD 和 JWT_SECRET"
            read -p "按回车继续（确认已配置 .env）..."
        else
            log_error ".env.example 文件不存在"
            exit 1
        fi
    fi

    # 生成随机的 JWT_SECRET（如果未配置）
    if grep -q "change-me-in-prod" .env; then
        log_warn "检测到未修改的 JWT_SECRET"
        JWT_SECRET=$(openssl rand -hex 32)
        sed -i "s/JWT_SECRET=.*/JWT_SECRET=$JWT_SECRET/" .env
        log_info "已生成随机 JWT_SECRET"
    fi

    log_info "后端配置完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."

    cd /opt/drinktea/backend
    source .venv/bin/activate

    # 通过应用启动自动创建数据库
    python3 -c "from app.main import create_app; app = create_app(); print('Database initialized')"

    log_info "数据库初始化完成"
}

# 配置 Systemd 服务
setup_systemd() {
    log_info "配置 Systemd 服务..."

    # 复制服务文件
    cp /opt/drinktea/deploy/drinktea-backend.service /etc/systemd/system/

    # 重新加载 systemd
    systemctl daemon-reload

    # 启用并启动服务
    systemctl enable drinktea-backend
    systemctl restart drinktea-backend

    # 等待服务启动
    sleep 3

    # 检查服务状态
    if systemctl is-active --quiet drinktea-backend; then
        log_info "后端服务启动成功"
    else
        log_error "后端服务启动失败"
        systemctl status drinktea-backend
        exit 1
    fi
}

# 配置 Nginx
setup_nginx() {
    log_info "配置 Nginx..."

    # 读取服务器 IP
    SERVER_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "YOUR_SERVER_IP")

    log_info "检测到服务器 IP: $SERVER_IP"

    # 复制并修改 Nginx 配置
    sed "s/YOUR_SERVER_IP/$SERVER_IP/g" /opt/drinktea/deploy/nginx.conf > /etc/nginx/sites-available/drinktea

    # 启用站点
    ln -sf /etc/nginx/sites-available/drinktea /etc/nginx/sites-enabled/

    # 删除默认站点（可选）
    # rm -f /etc/nginx/sites-enabled/default

    # 测试配置
    if nginx -t; then
        log_info "Nginx 配置测试通过"
        systemctl restart nginx
        log_info "Nginx 重启成功"
    else
        log_error "Nginx 配置测试失败"
        exit 1
    fi
}

# 配置防火墙
setup_firewall() {
    log_info "配置防火墙..."

    # 检查 UFW 是否安装
    if command -v ufw &> /dev/null; then
        log_info "配置 UFW 防火墙..."
        ufw allow 80/tcp
        ufw allow 443/tcp
        log_info "防火墙规则已添加"
    else
        log_warn "UFW 未安装，跳过防火墙配置"
        log_warn "请确保云服务商安全组已开放 80 和 443 端口"
    fi
}

# 运行健康检查
health_check() {
    log_info "运行健康检查..."

    SERVER_IP=$(curl -s ifconfig.me || curl -s icanhazip.com)

    # 检查后端健康
    if curl -sf http://localhost/health > /dev/null; then
        log_info "✓ 后端健康检查通过"
    else
        log_error "✗ 后端健康检查失败"
        return 1
    fi

    # 检查静态文件
    if [[ -f /opt/drinktea/apps/user-web/dist/index.html ]]; then
        log_info "✓ 用户端前端文件存在"
    else
        log_error "✗ 用户端前端文件不存在"
        return 1
    fi

    if [[ -f /opt/drinktea/apps/admin-web/dist/index.html ]]; then
        log_info "✓ 管理端前端文件存在"
    else
        log_error "✗ 管理端前端文件不存在"
        return 1
    fi

    echo ""
    log_info "==================================="
    log_info "部署完成！"
    log_info "==================================="
    echo ""
    log_info "访问地址："
    log_info "  用户端: http://$SERVER_IP/"
    log_info "  管理端: http://$SERVER_IP/admin"
    log_info "  API文档: http://$SERVER_IP/api/docs"
    echo ""
    log_info "默认管理员账号: admin"
    log_warn "请在 .env 文件中查看或修改管理员密码"
    echo ""
    log_info "查看日志："
    log_info "  后端: sudo journalctl -u drinktea-backend -f"
    log_info "  Nginx: sudo tail -f /var/log/nginx/drinktea-access.log"
    echo ""
}

# 主函数
main() {
    log_info "==================================="
    log_info "来喝茶项目 - 自动部署脚本"
    log_info "==================================="
    echo ""

    check_root
    check_system
    install_dependencies
    setup_directories
    build_frontend
    setup_backend
    init_database
    setup_systemd
    setup_nginx
    setup_firewall
    health_check

    log_info "部署脚本执行完成！"
}

# 运行主函数
main
