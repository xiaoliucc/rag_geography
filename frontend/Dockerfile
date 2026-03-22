# 构建阶段
FROM node:22-slim AS builder

WORKDIR /app

COPY package*.json ./

RUN npm config set registry https://registry.npmmirror.com && \
    npm install && \
    npm install @rollup/rollup-linux-x64-gnu --save-optional

# 复制源代码
COPY . .

# 构建（不需要 .env 也能构建）
RUN npm run build

# 运行阶段
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk add --no-cache bash curl

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]