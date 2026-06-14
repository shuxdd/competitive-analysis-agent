# 宝塔 + Docker 部署指南

> 适用环境：Ubuntu 22.04 + 宝塔免费版 + Docker

---

## 目录

1. [买服务器](#1-买服务器)
2. [装宝塔](#2-装宝塔)
3. [安装 Docker](#3-安装-docker)
4. [上传代码](#4-上传代码)
5. [配置环境变量](#5-配置环境变量)
6. [启动服务](#6-启动服务)
7. [宝塔 Nginx 配置](#7-宝塔-nginx-配置)
8. [HTTPS 证书](#8-https-证书)
9. [验证](#9-验证)
10. [常用操作](#10-常用操作)
11. [常见问题](#11-常见问题)

---

## 1. 买服务器

推荐阿里云或腾讯云 **轻量应用服务器**：

| 配置 | 价格 | 说明 |
|------|------|------|
| 2C2G | ~48元/月 | 最低配置 |
| **2C4G** | **~68元/月** | **推荐** |
| 2C4G+5Mbps | ~98元/月 | 多人使用 |

系统选 **Ubuntu 22.04**。

---

## 2. 装宝塔

SSH 登录服务器后执行：

```bash
wget -O install.sh https://download.bt.cn/install/install-ubuntu_6.0.sh
bash install.sh
```

安装完成后保存输出的面板地址 + 账号密码。

---

## 3. 安装 Docker

### 方式 A：宝塔插件安装（推荐）

宝塔 → 软件商店 → 搜索 **Docker管理器** → 安装

### 方式 B：命令行安装

```bash
curl -fsSL https://get.docker.com | bash
```

装完后验证：

```bash
docker --version
docker compose version
```

---

## 4. 上传代码

### 方式 A：git 克隆（推荐）

宝塔 → 文件 → `/www/wwwroot/` → 终端：

```bash
cd /www/wwwroot/
git clone <你的仓库地址> project
```

### 方式 B：宝塔文件上传

本地代码打包（不含 `.venv/` `node_modules/` `data/`）→ 上传 → 解压到 `/www/wwwroot/project/`

---

## 5. 配置环境变量

```bash
cd /www/wwwroot/project
cp .env.example .env
nano .env
```

必须修改的配置项：

| 变量 | 说明 | 获取方式 |
|------|------|---------|
| `OPENAI_API_KEY` | LLM API 密钥 | 你的 LLM 服务商 |
| `SERPAPI_KEY` | 搜索引擎 API 密钥 | serpapi.com |
| `SECRET_KEY` | JWT 密钥 | 自己生成一串随机字符 |
| `CORS_ORIGINS` | 前端访问域名 | 填 `https://你的域名.com` |

---

## 6. 启动服务

```bash
cd /www/wwwroot/project

# 构建并启动所有服务
docker compose up -d

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f
```

首次启动会构建镜像，需要几分钟。看到三个服务都 running 即正常：

```
NAME                   IMAGE                 STATUS
project-api            latest                Up 2 minutes
project-frontend       latest                Up 2 minutes
project-redis           redis:8-alpine       Up 2 minutes
```

### 初始化种子数据

首次部署需要初始化数据库表和数据：

```bash
# 进入后端容器执行 seed.py
docker compose exec api python seed.py
```

---

## 7. 宝塔 Nginx 配置

### 架构说明

宝塔的 Nginx 只做两件事：**HTTPS 终止** + **反向代理到前端容器**：

```
用户 → 宝塔 Nginx (443 HTTPS)
         └── 反向代理 → http://localhost:8080
                          └── 前端容器 Nginx
                               ├── 静态文件
                               └── /api/ → API 容器
                               └── /ws/  → API 容器 (WebSocket)
```

### 配置步骤

1. **宝塔 → 网站 → 添加站点**
   - 域名：你的域名
   - 根目录：任意（会被代理覆盖）
   - 创建后进入 **网站设置 → 反向代理**

2. **反向代理设置**

   | 参数 | 值 |
   |------|-----|
   | 目标 URL | `http://127.0.0.1:8080` |
   | 发送域名 | `$host` |
   | 内容替换 | 不替换 |

3. **配置文件修改**

   网站设置 → 配置文件中，在 `server` 块内增加超时设置（分析任务可能跑几分钟）：

   ```nginx
   # 在 server { ... } 内添加
   proxy_read_timeout 600s;
   proxy_send_timeout 600s;
   proxy_connect_timeout 30s;
   ```

---

## 8. HTTPS 证书

宝塔 → 网站 → 你的站点 → SSL：

1. 选择 **Let's Encrypt**
2. 勾选你的域名
3. 点击 **申请**
4. 开启 **强制 HTTPS**

宝塔会自动续签，无需手动维护。

---

## 9. 验证

按顺序检查：

### 9.1 后端健康检查

```bash
curl http://localhost:8000/health
```

应返回：`{"status": "ok"}`

### 9.2 前端页面

浏览器打开 `https://你的域名.com`，应看到登录页面。

### 9.3 全链路

1. 注册账号 → 登录
2. 添加竞品（如：Notion）
3. 提交分析任务
4. 等待完成，查看报告

---

## 10. 常用操作

### 更新代码

```bash
cd /www/wwwroot/project
git pull
docker compose up -d --build
```

### 查看日志

```bash
# 所有服务
docker compose logs -f

# 只看后端
docker compose logs -f api

# 只看前端
docker compose logs -f frontend
```

### 进入容器

```bash
docker compose exec api bash      # 后端
docker compose exec frontend sh   # 前端
```

### 重启服务

```bash
docker compose restart api        # 只重启后端
docker compose restart frontend   # 只重启前端
docker compose restart            # 重启全部
```

### 停止服务

```bash
docker compose down               # 停止并删除容器（数据卷保留）
docker compose down -v            # 停止并删除所有（含数据，慎用）
```

### 数据备份

备份 `app_data` 卷中的数据：

```bash
docker run --rm -v app_data:/data -v /www/backup:/backup alpine \
  tar czf /backup/app_data_$(date +%Y%m%d).tar.gz -C /data .
```

---

## 11. 常见问题

### Q：端口被占用

```
docker compose ps  # 检查哪个服务占用了端口
# 如果 80 端口被宝塔 Nginx 占用，修改 frontend 端口映射
# 改 docker-compose.yml 中 frontend 的 ports 为 "8080:80"
```

### Q：Chrome/Selenium 在容器里报错

```bash
# 确认容器内有 Chrome
docker compose exec api which chromium
```

### Q：数据库数据丢了

```bash
# 数据在 Docker 卷中，不会随容器删除而丢失
docker volume ls | grep app_data
# 如需手动初始化
docker compose exec api python seed.py
```

### Q：如何迁移到新服务器？

```bash
# 旧服务器备份
docker compose down
tar czf project_backup.tar.gz .env data/ docker-compose.yml

# 新服务器
# 装宝塔 → 装 Docker → 上传代码 + 备份文件 → docker compose up -d
```
