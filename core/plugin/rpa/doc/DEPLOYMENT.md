# 🚀 部署指南

本文档提供了星辰 RPA 服务器的详细部署指南，包括本地开发、测试环境和生产环境部署。

## 📋 目录

- [环境要求](#环境要求)
- [本地开发部署](#本地开发部署)
- [Docker 部署](#docker-部署)
- [生产环境部署](#生产环境部署)
- [负载均衡配置](#负载均衡配置)
- [监控和日志](#监控和日志)
- [故障排除](#故障排除)

## 🛠️ 环境要求

### 系统要求
- **操作系统**: Linux (Ubuntu 20.04+, CentOS 7+), macOS, Windows 10+
- **Python**: 3.11 或更高版本
- **内存**: 最小 2GB，推荐 4GB+
- **磁盘**: 最小 1GB 可用空间
- **网络**: 需要访问外部 RPA API 服务

### 软件依赖
- Python 3.11+
- pip 或 uv 包管理器
- Git (用于代码管理)
- 可选: Docker & Docker Compose

## 💻 本地开发部署

### 1. 环境准备

```bash
# 创建项目目录
mkdir -p ~/projects/rpa-server
cd ~/projects/rpa-server

# 克隆代码
git clone <repository-url> .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 升级 pip
pip install --upgrade pip
```

### 2. 安装依赖

```bash
# 安装生产依赖
pip install -r requirements.txt

# 安装开发依赖 (可选)
pip install pytest pytest-cov pytest-asyncio black isort mypy
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env
```

**关键配置项**:
```bash
# 基础配置
LOG_LEVEL=DEBUG
LOG_PATH=./logs
UVICORN_HOST=127.0.0.1
UVICORN_PORT=19999

# RPA API 配置 (替换为实际地址)
RPA_TASK_CREATE_URL=https://your-rpa-api.com/create
RPA_TASK_QUERY_URL=https://your-rpa-api.com/query
```

### 4. 启动开发服务器

```bash
# 方式1: 使用应用入口
python main.py

# 方式2: 使用 uvicorn (推荐开发环境)
uvicorn api.app:xingchen_rap_server_app --reload --host 127.0.0.1 --port 19999

# 方式3: 使用自定义启动脚本
python -c "
import uvicorn
from api.app import xingchen_rap_server_app
uvicorn.run(
    xingchen_rap_server_app,
    host='127.0.0.1',
    port=19999,
    reload=True,
    log_level='debug'
)"
```

### 5. 验证部署

```bash
# 检查服务状态
curl http://127.0.0.1:19999/rpa/v1/docs

# 运行健康检查
curl -X POST http://127.0.0.1:19999/rpa/v1/exec \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "health-check"}'
```

## 🐳 Docker 部署

### 1. 创建 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 设置权限
RUN chmod +x main.py

# 暴露端口
EXPOSE 19999

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:19999/rpa/v1/docs || exit 1

# 启动命令
CMD ["python", "main.py"]
```

### 2. 创建 Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  rpa-server:
    build: .
    ports:
      - "19999:19999"
    environment:
      - LOG_LEVEL=INFO
      - LOG_PATH=/app/logs
      - UVICORN_HOST=0.0.0.0
      - UVICORN_PORT=19999
      - UVICORN_WORKERS=4
      - RPA_TIMEOUT=300
      - RPA_TASK_CREATE_URL=${RPA_TASK_CREATE_URL}
      - RPA_TASK_QUERY_URL=${RPA_TASK_QUERY_URL}
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:19999/rpa/v1/docs"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # 可选: 添加 Nginx 反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - rpa-server
    restart: unless-stopped
```

### 3. 构建和运行

```bash
# 构建镜像
docker build -t xingchen-rpa-server .

# 使用 Docker Compose 启动
docker-compose up -d

# 查看日志
docker-compose logs -f rpa-server

# 停止服务
docker-compose down
```

### 4. 单容器运行

```bash
# 运行单个容器
docker run -d \
  --name rpa-server \
  -p 19999:19999 \
  -e LOG_LEVEL=INFO \
  -e RPA_TASK_CREATE_URL=https://your-api.com/create \
  -e RPA_TASK_QUERY_URL=https://your-api.com/query \
  -v $(pwd)/logs:/app/logs \
  xingchen-rpa-server

# 查看容器状态
docker ps
docker logs rpa-server
```

## 🏭 生产环境部署

### 1. 使用 Gunicorn + Uvicorn Workers

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动生产服务器
gunicorn api.app:xingchen_rap_server_app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:19999 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info \
  --preload
```

### 2. 创建 Gunicorn 配置文件

```python
# gunicorn.conf.py
bind = "0.0.0.0:19999"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# 日志配置
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程管理
preload_app = True
worker_tmp_dir = "/dev/shm"

# 安全配置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
```

使用配置文件启动:
```bash
gunicorn -c gunicorn.conf.py api.app:xingchen_rap_server_app
```

### 3. Systemd 服务配置

```ini
# /etc/systemd/system/rpa-server.service
[Unit]
Description=Xingchen RPA Server
After=network.target

[Service]
Type=exec
User=rpa
Group=rpa
WorkingDirectory=/opt/rpa-server
Environment=PATH=/opt/rpa-server/venv/bin
ExecStart=/opt/rpa-server/venv/bin/gunicorn -c gunicorn.conf.py api.app:xingchen_rap_server_app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

# 安全设置
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/opt/rpa-server/logs

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
# 创建用户和目录
sudo useradd -r -s /bin/false rpa
sudo mkdir -p /opt/rpa-server
sudo chown rpa:rpa /opt/rpa-server

# 部署应用
sudo cp -r . /opt/rpa-server/
sudo chown -R rpa:rpa /opt/rpa-server/

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable rpa-server
sudo systemctl start rpa-server

# 查看状态
sudo systemctl status rpa-server
```

### 4. PM2 部署 (Node.js 环境)

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'rpa-server',
    script: '/opt/rpa-server/venv/bin/gunicorn',
    args: '-c gunicorn.conf.py api.app:xingchen_rap_server_app',
    cwd: '/opt/rpa-server',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      LOG_LEVEL: 'INFO',
      NODE_ENV: 'production'
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_file: './logs/pm2-combined.log',
    time: true
  }]
};
```

使用 PM2 部署:
```bash
# 安装 PM2
npm install -g pm2

# 启动应用
pm2 start ecosystem.config.js

# 查看状态
pm2 status
pm2 logs rpa-server

# 设置开机自启
pm2 startup
pm2 save
```

## ⚖️ 负载均衡配置

### Nginx 配置

```nginx
# /etc/nginx/sites-available/rpa-server
upstream rpa_backend {
    least_conn;
    server 127.0.0.1:19999 weight=1 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:19998 weight=1 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:19997 weight=1 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    listen [::]:80;
    server_name rpa.yourdomain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name rpa.yourdomain.com;

    # SSL 配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 客户端最大上传大小
    client_max_body_size 10M;

    # 代理配置
    location /rpa/ {
        proxy_pass http://rpa_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE 支持
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }

    # 健康检查端点
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
```

启用配置:
```bash
sudo ln -s /etc/nginx/sites-available/rpa-server /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### HAProxy 配置

```
# /etc/haproxy/haproxy.cfg
global
    daemon
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 403 /etc/haproxy/errors/403.http
    errorfile 408 /etc/haproxy/errors/408.http
    errorfile 500 /etc/haproxy/errors/500.http
    errorfile 502 /etc/haproxy/errors/502.http
    errorfile 503 /etc/haproxy/errors/503.http
    errorfile 504 /etc/haproxy/errors/504.http

frontend rpa_frontend
    bind *:80
    bind *:443 ssl crt /path/to/cert.pem
    redirect scheme https if !{ ssl_fc }
    default_backend rpa_servers

backend rpa_servers
    balance roundrobin
    option httpchk GET /rpa/v1/docs
    http-check expect status 200
    server rpa1 127.0.0.1:19999 check
    server rpa2 127.0.0.1:19998 check backup
    server rpa3 127.0.0.1:19997 check backup

listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats admin if TRUE
```

## 📊 监控和日志

### 1. 应用监控

```python
# monitoring.py
import psutil
import time
from pathlib import Path

def get_system_metrics():
    """获取系统指标"""
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'load_average': psutil.getloadavg(),
        'timestamp': time.time()
    }

def get_app_metrics():
    """获取应用指标"""
    process = psutil.Process()
    return {
        'memory_mb': process.memory_info().rss / 1024 / 1024,
        'cpu_percent': process.cpu_percent(),
        'threads': process.num_threads(),
        'connections': len(process.connections()),
        'open_files': process.num_fds() if hasattr(process, 'num_fds') else 0
    }
```

### 2. 日志聚合

```bash
# 使用 rsyslog 聚合日志
echo "*.* @@log-server:514" >> /etc/rsyslog.conf
systemctl restart rsyslog

# 使用 Logrotate 轮转日志
cat > /etc/logrotate.d/rpa-server << EOF
/opt/rpa-server/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 rpa rpa
    postrotate
        systemctl reload rpa-server
    endscript
}
EOF
```

### 3. Prometheus 指标

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

# 定义指标
REQUEST_COUNT = Counter('rpa_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('rpa_request_duration_seconds', 'Request duration')
ACTIVE_TASKS = Gauge('rpa_active_tasks', 'Active RPA tasks')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    with REQUEST_DURATION.time():
        response = await call_next(request)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path
        ).inc()
    return response

@app.get("/metrics")
async def get_metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## 🔧 故障排除

### 常见问题诊断

#### 1. 服务启动失败

```bash
# 检查端口占用
sudo netstat -tulpn | grep 19999
sudo lsof -i :19999

# 检查配置文件
python -c "
import os
from dotenv import load_dotenv
load_dotenv('.env')
print('RPA_TASK_CREATE_URL:', os.getenv('RPA_TASK_CREATE_URL'))
"

# 检查依赖
pip check
```

#### 2. 连接超时问题

```bash
# 测试网络连接
curl -v $RPA_TASK_CREATE_URL
ping $(echo $RPA_TASK_CREATE_URL | cut -d'/' -f3)

# 检查防火墙
sudo ufw status
sudo iptables -L

# 检查 DNS 解析
nslookup $(echo $RPA_TASK_CREATE_URL | cut -d'/' -f3)
```

#### 3. 内存泄漏调试

```bash
# 监控内存使用
watch -n 1 'ps aux | grep gunicorn'

# 使用 memory_profiler
pip install memory-profiler
python -m memory_profiler main.py
```

### 日志分析脚本

```bash
#!/bin/bash
# analyze_logs.sh

LOG_FILE="/opt/rpa-server/logs/rpa-server.log"

echo "=== RPA Server 日志分析 ==="
echo "日志文件: $LOG_FILE"
echo

# 错误统计
echo "❌ 错误统计:"
grep -c "ERROR" $LOG_FILE
echo

# 最近的错误
echo "🔍 最近10个错误:"
grep "ERROR" $LOG_FILE | tail -10
echo

# 请求统计
echo "📊 今日请求统计:"
grep "$(date '+%Y-%m-%d')" $LOG_FILE | grep "POST /rpa/v1/exec" | wc -l
echo

# 响应时间分析
echo "⏱️ 平均响应时间:"
grep "Process-Time" $LOG_FILE | awk '{print $NF}' | \
  awk '{sum+=$1; count++} END {print sum/count "s"}'
```

### 性能调优

```bash
# 系统级优化
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
echo 'fs.file-max = 100000' >> /etc/sysctl.conf
sysctl -p

# 应用级优化
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1

# Gunicorn 调优
gunicorn api.app:xingchen_rap_server_app \
  -w $(nproc) \
  --worker-tmp-dir /dev/shm \
  --worker-class uvicorn.workers.UvicornWorker \
  --max-requests 1000 \
  --max-requests-jitter 100
```

---

## 📞 获取帮助

- 🐛 **问题反馈**: [GitHub Issues](https://github.com/your-org/xingchen-rpa-server/issues)
- 📖 **详细文档**: [README.md](./README.md)
- 🔧 **API 示例**: [API_EXAMPLES.md](./API_EXAMPLES.md)

这个部署指南涵盖了从开发环境到生产环境的完整部署流程，您可以根据实际需求选择合适的部署方式。