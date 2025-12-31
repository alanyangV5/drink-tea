# 部署检查清单

使用此清单确保部署的每个步骤都正确完成。

## 部署前准备

### 服务器环境
- [ ] 服务器已购买（阿里云/腾讯云等）
- [ ] 服务器操作系统为 Ubuntu 20.04+ 或 Debian 10+
- [ ] 服务器内存至少 1GB
- [ ] 服务器磁盘空间至少 10GB
- [ ] 已获取服务器 IP 地址
- [ ] 可以通过 SSH 登录服务器
- [ ] 已拥有 root 或 sudo 权限

### 网络配置
- [ ] 服务器安全组已开放 80 端口（HTTP）
- [ ] 服务器安全组已开放 443 端口（HTTPS，如需要）
- [ ] 服务器安全组已开放 22 端口（SSH）
- [ ] （可选）域名已购买并解析到服务器 IP

## 部署步骤

### 1. 上传代码
- [ ] 代码已上传到服务器 `/opt/drinktea` 目录
- [ ] 可以使用 Git 克隆或 SCP 上传
- [ ] 文件权限正确设置

### 2. 配置环境变量
- [ ] 已复制 `.env.production.example` 到 `.env`
- [ ] 已修改 `APP_CORS_ORIGINS` 为实际服务器 IP
- [ ] 已设置强管理员密码（`ADMIN_PASSWORD`）
- [ ] 已生成并设置 `JWT_SECRET`（至少 32 个字符）
- [ ] `.env` 文件权限设置为 600（可选）

### 3. 运行部署脚本
- [ ] 已进入 `deploy` 目录
- [ ] 已给 `deploy.sh` 添加执行权限
- [ ] 已使用 `sudo` 运行部署脚本
- [ ] 脚本执行无错误

### 4. 验证服务状态

#### 后端服务
- [ ] `systemctl status drinktea-backend` 显示 `active (running)`
- [ ] 后端服务已启用开机自启（`enabled`）
- [ ] `journalctl -u drinktea-backend` 无错误日志

#### Nginx 服务
- [ ] `systemctl status nginx` 显示 `active (running)`
- [ ] `nginx -t` 配置测试通过
- [ ] Nginx 已监听 80 端口

#### 防火墙
- [ ] UFW 或云服务商安全组已开放 80 端口
- [ ] （可选）443 端口已开放（HTTPS）

## 部署后验证

### 健康检查
- [ ] `curl http://localhost/health` 返回 `{"ok":true}`
- [ ] 后端日志无异常

### 前端访问
- [ ] 用户端可以访问：`http://服务器IP/`
- [ ] 页面显示正常，样式加载正常
- [ ] 可以滑动茶叶卡片

### 管理端访问
- [ ] 管理端可以访问：`http://服务器IP/admin`
- [ ] 可以使用管理员账号登录
- [ ] 登录后可以进入仪表板

### API 测试
- [ ] API 文档可以访问：`http://服务器IP/api/docs`
- [ ] 可以在 Swagger UI 中测试 API
- [ ] 茶叶列表 API 返回数据

### 文件上传
- [ ] `/opt/drinktea/backend/data/uploads` 目录存在
- [ ] 目录权限正确（www-data:www-data）
- [ ] 可以在管理端上传茶叶图片

## 功能测试

### 用户端功能
- [ ] 浏览茶叶卡片
- [ ] 右滑喜欢茶叶
- [ ] 左滑不喜欢茶叶
- [ ] 查看茶叶详情
- [ ] 分类筛选功能

### 管理端功能
- [ ] 登录/登出
- [ ] 查看茶叶列表
- [ ] 添加新茶叶
- [ ] 编辑茶叶信息
- [ ] 上传茶叶图片
- [ ] 查看数据统计
- [ ] Excel 导入功能

## 安全检查

- [ ] 已修改默认管理员密码
- [ ] JWT_SECRET 使用强随机字符串
- [ ] `.env` 文件不包含在版本控制中
- [ ] 数据库文件权限正确（600）
- [ ] 上传目录权限正确（755）
- [ ] 防火墙规则已配置
- [ ] SSH 密钥已配置（可选）
- [ ] （可选）HTTPS 证书已配置

## 性能优化（可选）

- [ ] Nginx 已启用 Gzip 压缩
- [ ] 静态资源缓存已配置
- [ ] 后端使用多个 workers
- [ ] 日志轮转已配置
- [ ] 监控和告警已配置

## 备份策略

- [ ] 数据库定期备份
- [ ] 上传文件定期备份
- [ ] 备份文件存储在不同位置
- [ ] 测试恢复流程

## 文档和运维

- [ ] 已阅读完整部署文档（`docs/deployment.md`）
- [ ] 了解常用运维命令
- [ ] 了解日志查看方法
- [ ] 了解更新流程
- [ ] 了解数据备份和恢复方法

## 常见问题排查

如遇到问题，按以下步骤排查：

1. **检查服务状态**
   ```bash
   sudo systemctl status drinktea-backend
   sudo systemctl status nginx
   ```

2. **查看日志**
   ```bash
   sudo journalctl -u drinktea-backend -n 50
   sudo tail -f /var/log/nginx/drinktea-error.log
   ```

3. **检查端口占用**
   ```bash
   sudo lsof -i:8000
   sudo lsof -i:80
   ```

4. **检查配置文件**
   ```bash
   cat /opt/drinktea/backend/.env
   sudo nginx -t
   ```

5. **重启服务**
   ```bash
   sudo systemctl restart drinktea-backend
   sudo systemctl restart nginx
   ```

## 部署完成后

- [ ] 保存服务器登录信息
- [ ] 保存管理员账号密码
- [ ] 记录服务器 IP 和访问地址
- [ ] 设置定期备份任务
- [ ] 配置监控告警（可选）
- [ ] 通知相关人员部署完成

## 更新和维护

- [ ] 了解更新流程（`deploy/update.sh`）
- [ ] 定期检查系统更新
- [ ] 定期检查依赖更新
- [ ] 定期查看日志
- [ ] 监控服务器资源使用

---

**部署日期**：_____________

**部署人员**：_____________

**服务器 IP**：_____________

**访问地址**：_____________

**管理员账号**：_____________

**管理员密码**：_____________

**备注**：_____________
