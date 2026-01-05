# HTTPS 域名配置指南

## 前置条件

1. 拥有一个域名（如 example.com）
2. 域名 DNS 已指向服务器 IP
3. 服务器开放 80 和 443 端口

## 配置步骤

### 1. 修改配置文件

编辑 `nginx/nginx.conf`，将所有 `your-domain.com` 替换为你的实际域名：

```bash
# 使用文本编辑器替换域名
# 或使用命令（Linux/Mac）：
sed -i 's/your-domain.com/example.com/g' nginx/nginx.conf
```

### 2. 修改证书初始化脚本

编辑 `init-letsencrypt.ps1`（Windows）或 `init-letsencrypt.sh`（Linux），修改：

```powershell
# PowerShell 版本
$domains = @("example.com")  # 改为你的域名
$email = "your-email@example.com"  # 改为你的邮箱
```

```bash
# Bash 版本
domains=(example.com)  # 改为你的域名
email="your-email@example.com"  # 改为你的邮箱
```

### 3. 初始化 SSL 证书

**Windows (PowerShell):**
```powershell
.\init-letsencrypt.ps1
```

**Linux/Mac:**
```bash
chmod +x init-letsencrypt.sh
./init-letsencrypt.sh
```

### 4. 启动服务

```bash
docker compose up -d
```

## 访问应用

- HTTP: http://your-domain.com （自动跳转到 HTTPS）
- HTTPS: https://your-domain.com

## 证书自动续期

Certbot 容器会每 12 小时检查一次证书，并在到期前自动续期。

## 故障排查

### 证书申请失败

1. 确认域名 DNS 已正确指向服务器
2. 确认 80 端口可访问
3. 首次测试可以设置 `staging=1` 使用测试环境

### Nginx 启动失败

```bash
# 查看日志
docker compose logs nginx

# 测试配置
docker compose exec nginx nginx -t
```

### 手动续期证书

```bash
docker compose run --rm certbot renew
docker compose exec nginx nginx -s reload
```

## 多域名支持

如需支持多个域名（如 www.example.com），修改：

```powershell
# PowerShell
$domains = @("example.com", "www.example.com")
```

```bash
# Bash
domains=(example.com www.example.com)
```

并在 `nginx.conf` 中添加：

```nginx
server_name example.com www.example.com;
```
