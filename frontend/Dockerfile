# 构建阶段
FROM node:22-slim as builder

# 设置工作目录
WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖（包括 rollup 的 Linux 版本）
RUN npm config set registry https://registry.npmmirror.com && \
    npm install && \
    npm install @rollup/rollup-linux-x64-gnu --save-optional

# 复制 .env 文件
COPY .env .env
COPY .env.docker .env.production
# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 运行阶段
FROM nginx:alpine

# 从构建阶段复制构建结果
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制源代码到容器（可选，用于调试）
COPY --from=builder /app/src /usr/src/app/src
COPY --from=builder /app/package*.json /usr/src/app/

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 安装 bash 和基本工具（用于调试）
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk add --no-cache bash curl vim

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]