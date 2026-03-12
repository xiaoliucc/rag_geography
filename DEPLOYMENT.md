# 高中地理 RAG 系统 - 部署指南

## 📋 项目结构

```
基于增强推理的高中地理RAG系统/
├── backend/              # 后端 (FastAPI)
│   ├── api.py           # API 服务入口
│   ├── rag_system.py    # RAG 核心逻辑
│   └── requirements.txt # Python 依赖
├── frontend/            # 前端 (Vue 3 + Vite)
│   ├── src/
│   ├── package.json
│   └── .env.example     # 环境变量示例
└── materials/           # 数据和资源文件
    └── Text Materials/
        └── pdf_extracted/
            └── full_pages/ # PDF 页面图片
```

---

## 🚀 方案一：Docker 部署（推荐）

### 1. 创建 Docker Compose

在项目根目录创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./materials:/app/materials
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:80"
    depends_on:
      - backend
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    restart: unless-stopped
```

### 2. 创建后端 Dockerfile

在 `backend/Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. 创建前端 Dockerfile

在 `frontend/Dockerfile`：

```dockerfile
FROM node:20-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm install --registry=https://registry.npmmirror.com

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 4. 创建前端 Nginx 配置

在 `frontend/nginx.conf`：

```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        location / {
            try_files $uri $uri/ /index.html;
        }
    }
}
```

### 5. 启动服务

```bash
docker-compose up -d --build
```

访问：http://localhost:5173

---

## 🌐 方案二：云服务器部署（阿里云/腾讯云）

### 1. 服务器准备

- 购买云服务器（推荐配置：2核4G以上）
- 安装 Docker 和 Docker Compose
- 开放端口：80、443、8000

### 2. 上传代码

```bash
# 使用 scp 或 git 上传代码到服务器
scp -r ./ 用户名@服务器IP:/root/rag-system/
```

### 3. 配置环境变量

在服务器上创建 `frontend/.env`：

```env
VITE_API_BASE_URL=http://你的服务器IP:8000
```

### 4. 启动服务

```bash
cd /root/rag-system
docker-compose up -d --build
```

### 5. 配置域名和 HTTPS（可选）

使用 Nginx 反向代理 + Let's Encrypt 证书：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location /materials/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

---

## 💻 方案三：本地部署（开发测试）

### 1. 后端部署

```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 启动服务
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 2. 前端部署

```bash
cd frontend

# 复制环境变量
copy .env.example .env
# cp .env.example .env  # Linux/Mac

# 编辑 .env，设置 API 地址
# VITE_API_BASE_URL=http://localhost:8000

# 安装依赖
npm install --registry=https://registry.npmmirror.com

# 开发模式
npm run dev

# 生产构建
npm run build

# 预览构建结果
npm run preview
```

---

## 📦 方案四：Vercel + 阿里云函数计算

### 前端部署到 Vercel

1. 将代码推送到 GitHub
2. 在 Vercel 导入项目
3. 配置环境变量：`VITE_API_BASE_URL` 指向你的后端地址
4. 部署

### 后端部署到阿里云函数计算

1. 使用 Serverless Devs 工具
2. 配置函数计算服务
3. 配置 NAS 存储 materials 数据
4. 部署后端 API

---

## 📁 数据文件说明

确保以下文件存在：

```
materials/
├── Text Materials/
│   ├── pdf_extracted/
│   │   ├── full_pages/          # PDF 完整页面图片 (必需)
│   │   │   ├── page_1.png
│   │   │   ├── page_2.png
│   │   │   └── ...
│   │   ├── chapter_chunks.json  # 文档分块
│   │   └── ...
│   └── ...
└── textbooks/
    └── renjiao_no_watermark/
        └── 人教版地理必修第一册【高清教材】.pdf
```

---

## 🔧 常见问题

### 1. 前端无法连接后端

检查：
- 后端是否正常启动
- CORS 配置是否正确
- 防火墙是否开放端口
- `.env` 文件中的 API 地址是否正确

### 2. PDF 图片无法加载

检查：
- `materials/Text Materials/pdf_extracted/full_pages/` 目录是否存在
- 图片文件是否完整
- 后端是否正确挂载了静态文件

### 3. 内存不足

- 增加服务器内存（推荐4G以上）
- 使用更小的 embedding 模型
- 限制并发请求数

---

## 📞 技术支持

如有问题，请检查：
1. 后端日志：`docker-compose logs backend`
2. 前端日志：浏览器控制台 (F12)
3. 网络请求：浏览器 Network 面板
