# Beancount记账应用 - Docker Compose 部署指南

本文档说明如何使用 Docker Compose 快速部署本项目。

## 📋 目录

- [环境要求](#环境要求)
- [快速部署](#快速部署)
- [配置说明](#配置说明)
- [常用命令](#常用命令)
- [生产环境部署](#生产环境部署)
- [故障排查](#故障排查)

---

## 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 服务器内存 1GB+

### 安装 Docker

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

**CentOS:**
```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker && sudo systemctl enable docker
```

---

## 快速部署

### 1. 上传项目代码

```bash
# 创建目录
mkdir -p ~/apps/beancount1 && cd ~/apps/beancount1

# 使用 Git 克隆或 SCP 上传代码
git clone <your_repository_url> .
```

### 2. 配置环境变量

```bash
cd backend
cp .env.example .env
nano .env
```

编辑 `.env` 文件：
```env
# VLM 配置
VLM_PROVIDER=openai
VLM_API_KEY=your_api_key_here

# OpenAI 配置
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1

# 认证配置
AUTH_ENABLED=true
AUTH_USERNAME=admin
AUTH_PASSWORD=your_secure_password
JWT_SECRET_KEY=your_jwt_secret_key

# Beancount 配置
BEANCOUNT_MAIN_PATH=/app/data/main.beancount
```

### 3. 启动服务

```bash
cd ~/apps/beancount1
docker compose up -d
```

访问 `http://your_server_ip:8000` 即可使用。

---

## 配置说明

### 项目结构

```
beancount/
├── docker-compose.yml      # 主编排文件
├── backend/
│   ├── Dockerfile
│   ├── .env
│   ├── app/
│   └── data/               # 账本数据（持久化）
└── frontend/
    ├── Dockerfile
    └── nginx.conf
```

### docker-compose.yml（完整版）

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: beancount-backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/data:/app/data
    env_file:
      - ./backend/.env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    container_name: beancount-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  # 可选：Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: beancount-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
```

### 前端 Dockerfile

在 `frontend/` 目录创建 `Dockerfile`：

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### 前端 nginx.conf

在 `frontend/` 目录创建 `nginx.conf`：

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 常用命令

```bash
# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f

# 查看后端日志
docker compose logs -f backend

# 停止服务
docker compose down

# 重新构建并启动
docker compose up -d --build

# 查看运行状态
docker compose ps

# 进入容器
docker compose exec backend bash

# 重启单个服务
docker compose restart backend
```

---

## 生产环境部署

### 1. 使用 Nginx 反向代理 + SSL

创建 `nginx/nginx.conf`：

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name your_domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name your_domain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 2. 数据备份

```bash
# 备份账本数据
docker compose exec backend tar -czf /tmp/backup.tar.gz /app/data
docker cp beancount-backend:/tmp/backup.tar.gz ./backup_$(date +%Y%m%d).tar.gz

# 定时备份（添加到 crontab）
0 2 * * * cd ~/apps/beancount1 && docker compose exec -T backend tar -czf - /app/data > backup_$(date +\%Y\%m\%d).tar.gz
```

### 3. 更新部署

```bash
cd ~/apps/beancount1
git pull
docker compose down
docker compose up -d --build
```

---

## 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker compose logs backend

# 检查配置
docker compose config
```

### 端口被占用

```bash
# 查看端口占用
sudo lsof -i :8000
sudo lsof -i :80

# 修改 docker-compose.yml 中的端口映射
ports:
  - "8080:8000"  # 改为其他端口
```

### 数据丢失

确保 volumes 配置正确：
```yaml
volumes:
  - ./backend/data:/app/data  # 本地目录:容器目录
```

### 权限问题

```bash
# 修复数据目录权限
sudo chown -R 1000:1000 ./backend/data
```
