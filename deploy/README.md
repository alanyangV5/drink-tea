# 快速部署指南

本指南帮助您在 10 分钟内完成项目部署。

## 前置要求

- ✅ 服务器：Ubuntu 20.04+ 或 Debian 10+
- ✅ 内存：至少 1GB RAM
- ✅ 磁盘：至少 10GB
- ✅ SSH 访问权限
- ✅ Root 或 sudo 权限

## 一键部署（推荐）

### 1. 上传代码到服务器

**方式 A：使用 Git（推荐）**

```bash
# SSH 登录服务器
ssh user@your-server-ip

# 安装 git
sudo apt update && sudo apt install -y git

# 克隆代码
cd /opt
sudo git clone https://github.com/yourusername/drinktea.git
sudo chown -R $USER:$USER /opt/drinktea
cd /opt/drinktea
```

**方式 B：使用 SCP（本地执行）**

```bash
# 在本地机器执行（项目根目录）
scp -r . user@your-server-ip:/opt/drinktea
```

### 2. 配置环境变量

```bash
cd /opt/drinktea/backend
cp .env.production.example .env
nano .env
```

**必须修改的配置：**

```bash
# 修改为服务器 IP
APP_CORS_ORIGINS=http://YOUR_SERVER_IP

# 修改为强密码
ADMIN_PASSWORD=your-strong-password-here

# 生成新的密钥
JWT_SECRET=$(openssl rand -hex 32)
echo "JWT_SECRET=$JWT_SECRET"
```

### 3. 运行自动部署脚本

```bash
cd /opt/drinktea/deploy
chmod +x deploy.sh
sudo ./deploy.sh
```

脚本会自动完成：
- ✅ 安装系统依赖（Python、Node.js、Nginx）
- ✅ 构建前端（用户端 + 管理端）
- ✅ 配置后端（虚拟环境 + 依赖安装）
- ✅ 初始化数据库
- ✅ 配置 Systemd 服务（开机自启）
- ✅ 配置 Nginx 反向代理
- ✅ 配置防火墙规则

### 4. 验证部署

```bash
# 检查后端健康状态
curl http://localhost/health

# 检查服务状态
sudo systemctl status drinktea-backend
sudo systemctl status nginx
```

### 5. 访问应用

在浏览器中打开：

- **用户端**：`http://your-server-ip/`
- **管理端**：`http://your-server-ip/admin`
- **API 文档**：`http://your-server-ip/api/docs`

管理端登录账号（在 `.env` 文件中配置）：
- 用户名：`admin`
- 密码：你设置的密码

## 手动部署（如果自动脚本失败）

### 安装系统依赖

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx git curl

# 安装 Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### 构建前端

```bash
cd /opt/drinktea/apps/user-web
npm install
npm run build

cd ../admin-web
npm install
npm run build
```

### 配置后端

```bash
cd /opt/drinktea/backend

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.production.example .env
nano .env  # 按照上面的说明配置

# 初始化数据库
python3 -c "from app.main import create_app; create_app()"
```

### 配置 Systemd 服务

```bash
# 复制服务文件
sudo cp /opt/drinktea/deploy/drinktea-backend.service /etc/systemd/system/

# 创建上传目录并设置权限
sudo mkdir -p /opt/drinktea/backend/data/uploads
sudo chown -R www-data:www-data /opt/drinktea/backend

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable drinktea-backend
sudo systemctl start drinktea-backend
```

### 配置 Nginx

```bash
# 获取服务器 IP
SERVER_IP=$(curl -s ifconfig.me)

# 复制并修改配置
sudo sed "s/YOUR_SERVER_IP/$SERVER_IP/g" \
  /opt/drinktea/deploy/nginx.conf \
  > /etc/nginx/sites-available/drinktea

# 启用站点
sudo ln -s /etc/nginx/sites-available/drinktea /etc/nginx/sites-enabled/

# 测试并重启
sudo nginx -t
sudo systemctl restart nginx
```

### 配置防火墙

```bash
# 如果使用 UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 或在云服务商控制台配置安全组
```

## 更新应用

当有新代码时，使用更新脚本：

```bash
cd /opt/drinktea/deploy
chmod +x update.sh
sudo ./update.sh
```

或手动更新：

```bash
cd /opt/drinktea
git pull  # 或重新上传代码

# 重新构建前端
cd apps/user-web && npm run build
cd ../admin-web && npm run build

# 更新后端
cd ../backend
source .venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl restart drinktea-backend
sudo systemctl restart nginx
```

## 常见问题

### 1. 端口被占用

```bash
# 查看占用端口的进程
sudo lsof -i:8000
sudo lsof -i:80

# 杀死进程
sudo kill -9 <PID>
```

### 2. 权限错误

```bash
# 重新设置权限
sudo chown -R www-data:www-data /opt/drinktea/backend
sudo chmod -R 755 /opt/drinktea
```

### 3. 前端 404 错误

检查 Nginx 配置中的路径是否正确：

```bash
ls -la /opt/drinktea/apps/user-web/dist/
ls -la /opt/drinktea/apps/admin-web/dist/
```

### 4. 后端无法启动

查看日志：

```bash
sudo journalctl -u drinktea-backend -n 50
```

常见原因：
- `.env` 文件配置错误
- Python 依赖安装失败
- 数据库文件权限问题

### 5. CORS 错误

检查 `.env` 中的 `APP_CORS_ORIGINS` 是否包含正确的地址。

## 维护命令

```bash
# 查看后端日志
sudo journalctl -u drinktea-backend -f

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/drinktea-access.log
sudo tail -f /var/log/nginx/drinktea-error.log

# 重启服务
sudo systemctl restart drinktea-backend
sudo systemctl restart nginx

# 查看服务状态
sudo systemctl status drinktea-backend
sudo systemctl status nginx
```

## 备份数据

```bash
# 备份数据库
sudo cp /opt/drinktea/backend/data/drinktea.db \
  /opt/drinktea/backend/data/backup-$(date +%Y%m%d).db

# 备份上传的图片
sudo tar -czf /opt/drinktea/uploads-backup-$(date +%Y%m%d).tar.gz \
  /opt/drinktea/backend/data/uploads
```

## HTTPS 配置（可选）

如果配置了域名，可以使用 Let's Encrypt 免费 SSL 证书：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 安全建议

1. ✅ 修改默认管理员密码
2. ✅ 使用强 JWT_SECRET
3. ✅ 定期更新系统和依赖
4. ✅ 配置防火墙
5. ✅ 设置文件权限：`chmod 600 .env`
6. ✅ 定期备份数据

## 获取帮助

如遇到问题：

1. 查看详细部署文档：`docs/deployment.md`
2. 检查日志文件
3. 查看服务状态
4. 提交 Issue：`https://github.com/yourusername/drinktea/issues`
