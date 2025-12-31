# 服务器部署指南

本文档介绍如何将「来喝茶」项目部署到云服务器（阿里云/腾讯云等）上。

## 前置要求

- **服务器**：Ubuntu 20.04+ 或 Debian 10+（云服务器）
- **访问方式**：SSH 访问权限
- **域名**（可选）：如果需要 HTTPS，需要已解析的域名
- **内存要求**：至少 1GB RAM
- **磁盘空间**：至少 10GB

## 部署架构

```
┌─────────────┐
│   Nginx     │  反向代理 + 静态文件托管
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
┌──────▼──────┐  ┌──────▼──────────┐
│  用户端前端  │  │   管理端前端     │
│  (静态文件)  │  │   (静态文件)     │
└─────────────┘  └─────────────────┘
       │                 │
       └────────┬────────┘
                │
        ┌───────▼──────────┐
        │   FastAPI 后端    │
        │   (端口 8000)     │
        │   SQLite 数据库   │
        └──────────────────┘
```

## 部署步骤

### 1. 服务器环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要工具
sudo apt install -y nginx python3 python3-venv python3-pip git curl

# 安装 Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 验证安装
python3 --version  # 应显示 Python 3.10+
node --version     # 应显示 v20.x.x
nginx -v           # 应显示 nginx 版本
```

### 2. 创建部署目录

```bash
# 创建应用目录
sudo mkdir -p /opt/drinktea
sudo chown $USER:$USER /opt/drinktea
cd /opt/drinktea
```

### 3. 上传代码到服务器

**方式一：使用 Git 克隆**

```bash
git clone <你的仓库地址> .
```

**方式二：使用 SCP 上传**

```bash
# 在本地机器执行
scp -r /Users/alanyang/Desktop/workspace/drinkTea user@your-server-ip:/opt/drinktea
```

### 4. 构建前端

```bash
cd /opt/drinktea

# 构建用户端
cd apps/user-web
npm install
npm run build

# 构建管理端
cd ../admin-web
npm install
npm run build
```

### 5. 配置后端

```bash
cd /opt/drinktea/backend

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env
```

编辑 `.env` 文件：

```bash
# 生产环境配置
APP_ENV=production

# CORS 配置（如果使用 IP 访问，填服务器 IP）
APP_CORS_ORIGINS=http://your-server-ip,http://your-domain

# 管理员配置（必须修改）
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-strong-password-here
# 或者使用哈希密码（推荐）
# ADMIN_PASSWORD_HASH=$2b$12$...

# JWT 密钥（必须修改为随机字符串）
JWT_SECRET=your-random-secret-key-at-least-32-chars

# JWT 过期时间（分钟）
JWT_EXPIRE_MINUTES=720
```

**生成哈希密码（可选）：**

```bash
python3 << 'EOF'
import bcrypt
password = "your-password"
hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(f"ADMIN_PASSWORD_HASH={hash}")
EOF
```

### 6. 初始化数据库

```bash
cd /opt/drinktea/backend
source .venv/bin/activate

# 运行应用会自动创建数据库文件
python3 -c "from app.main import app; print('Database initialized')"
```

### 7. 配置 Systemd 服务

创建 systemd 服务文件：

```bash
sudo nano /etc/systemd/system/drinktea-backend.service
```

复制以下内容（见 `deploy/drinktea-backend.service`）：

```ini
[Unit]
Description=DrinkTea Backend FastAPI Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/drinktea/backend
Environment="PATH=/opt/drinktea/backend/.venv/bin"
ExecStart=/opt/drinktea/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**设置正确的权限和启动服务：**

```bash
# 创建 uploads 目录并设置权限
sudo mkdir -p /opt/drinktea/backend/data/uploads
sudo chown -R www-data:www-data /opt/drinktea/backend

# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start drinktea-backend

# 设置开机自启
sudo systemctl enable drinktea-backend

# 检查状态
sudo systemctl status drinktea-backend
```

### 8. 配置 Nginx

创建 Nginx 配置：

```bash
sudo nano /etc/nginx/sites-available/drinktea
```

复制以下内容（见 `deploy/nginx.conf`），**替换 `your_server_ip` 为实际 IP**：

```nginx
# 后端 API 代理
server {
    listen 80;
    server_name your_server_ip;

    # 用户端前端
    location / {
        alias /opt/drinktea/apps/user-web/dist/;
        try_files $uri $uri/ /index.html;
    }

    # 管理端前端
    location /admin {
        alias /opt/drinktea/apps/admin-web/dist/;
        try_files $uri $uri/ /admin/index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 上传文件
    location /uploads {
        alias /opt/drinktea/backend/data/uploads;
    }

    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

**启用配置：**

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/drinktea /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 9. 配置防火墙

```bash
# 如果使用 UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 如果云服务商有安全组，确保开放 80 和 443 端口
```

### 10. 验证部署

```bash
# 检查后端健康状态
curl http://your-server-ip/health
# 应返回: {"ok":true}

# 访问用户端
# 浏览器打开: http://your-server-ip

# 访问管理端
# 浏览器打开: http://your-server-ip/admin
# 登录: admin / your-password

# 查看 API 文档
# 浏览器打开: http://your-server-ip/api/docs
```

## 维护操作

### 查看日志

```bash
# 后端日志
sudo journalctl -u drinktea-backend -f

# Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 重启服务

```bash
# 重启后端
sudo systemctl restart drinktea-backend

# 重启 Nginx
sudo systemctl restart nginx
```

### 更新应用

```bash
cd /opt/drinktea
git pull  # 或重新上传代码

# 重新构建前端
cd apps/user-web && npm run build
cd ../admin-web && npm run build

# 更新后端依赖
cd ../backend
source .venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl restart drinktea-backend
sudo systemctl restart nginx
```

### 备份数据

```bash
# 备份数据库
cp /opt/drinktea/backend/data/drinktea.db /opt/drinktea/backend/data/backup-$(date +%Y%m%d).db

# 备份上传的图片
tar -czf uploads-backup-$(date +%Y%m%d).tar.gz /opt/drinktea/backend/data/uploads
```

### 数据库迁移/导出

```bash
# 导出为 SQL
sqlite3 /opt/drinktea/backend/data/drinktea.db .dump > backup.sql

# 导入
sqlite3 /opt/drinktea/backend/data/drinktea.db < backup.sql
```

## HTTPS 配置（可选）

如果配置了域名，可以使用 Let's Encrypt 免费证书：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 性能优化建议

1. **启用 Gzip 压缩**（在 Nginx 配置中添加）
2. **配置静态文件缓存**
3. **使用 Supervisor 替代 Systemd**（如果需要更多功能）
4. **考虑使用 PostgreSQL 替代 SQLite**（高并发场景）
5. **配置 CDN 加速静态资源**

## 故障排查

### 后端无法启动

```bash
# 检查日志
sudo journalctl -u drinktea-backend -n 50

# 常见问题：
# - 端口 8000 被占用：sudo lsof -i:8000
# - 权限问题：sudo chown -R www-data:www-data /opt/drinktea/backend
# - Python 依赖缺失：source .venv/bin/activate && pip install -r requirements.txt
```

### 前端 404 错误

- 检查 Nginx 配置中的路径是否正确
- 确认前端已正确构建：`ls /opt/drinktea/apps/user-web/dist/`
- 检查文件权限：`sudo chown -R www-data:www-data /opt/drinktea`

### CORS 错误

- 检查后端 `.env` 中的 `APP_CORS_ORIGINS` 配置
- 确保包含正确的协议和端口

## 安全建议

1. **修改默认管理员密码**
2. **使用强 JWT_SECRET**
3. **定期更新系统和依赖**
4. **配置 fail2ban 防止暴力破解**
5. **限制数据库文件权限**：`chmod 600 /opt/drinktea/backend/data/*.db`
6. **使用防火墙限制不必要的入站连接**

## 监控

### 简单监控脚本

```bash
# 创建健康检查脚本
nano /opt/drinktea/scripts/health-check.sh
```

```bash
#!/bin/bash
if ! curl -f http://localhost/health > /dev/null 2>&1; then
    echo "Service down, restarting..."
    systemctl restart drinktea-backend
    # 可选：发送告警邮件
fi
```

添加到 crontab：

```bash
# 每 5 分钟检查一次
*/5 * * * * /opt/drinktea/scripts/health-check.sh
```
