# 上线部署计划（宝塔 + Docker）

## 部署架构

```
一台云服务器 (2C4G, ~68元/月)
┌─────────────────────────────────────────────┐
│  宝塔面板                                    │
│  ├─ Nginx (HTTPS 终止 + 反向代理)            │
│  │   └─ https://你的域名.com                 │
│  │       └─ 反向代理 → http://127.0.0.1:8080 │
│  │                         │                 │
│  └─ Docker 容器              │                 │
│      ┌──────────────────────┘                 │
│      │                                        │
│      ├─ frontend (Nginx, :8080)              │
│      │   ├─ 静态文件 (/usr/share/nginx/html) │
│      │   └─ /api/ → api:8000                 │
│      │   └─ /ws/  → api:8000 (WebSocket)     │
│      ├─ api (uvicorn, :8000)                 │
│      │   ├─ SQLite → /data/app.db            │
│      │   ├─ Chroma → /data/chroma/           │
│      │   └─ 报告   → /data/reports/          │
│      └─ redis (缓存, :6379)                  │
└─────────────────────────────────────────────┘
```

**数据库**：SQLite（Docker 卷持久化，零配置）
**HTTPS**：宝塔一键申请 Let's Encrypt，自动续签

---

## 总览

```
第 1 天           第 2-3 天        第 4-5 天         第 6-7 天
├─ 部署准备        ├─ 安全加固       ├─ 体验完善        ├─ 上线
├─ 代码适配        ├─ 限流/校验      ├─ 报告详情页      ├─ 最终验收
├─ 宝塔配置        ├─ 日志/监控      ├─ 忘记密码        ├─ 部署文档
└─ 验证            └─ 备份          └─ 文档更新        └─ 收尾
```

---

## 第一阶段：部署准备（1-2 天）

**目标**：买服务器、装宝塔、Docker 跑起来

### 1.1 买服务器

| 配置 | 推荐 | 最低 |
|------|------|------|
| 规格 | 2C4G | 2C2G |
| 系统 | Ubuntu 22.04 | Ubuntu 22.04 |
| 带宽 | 3Mbps | 2Mbps |
| 磁盘 | 40GB | 20GB |
| 价格 | ~68元/月 | ~48元/月 |

推荐 **阿里云/腾讯云 轻量应用服务器**，2C4G 足够跑全套。

### 1.2 配置适配（无需服务器，现在就能做）

以下修改可以先在本地完成，部署时 git push 就行：

**1) CORS 配置化**

`api/app.py` 的 `allow_origins` 改为从环境变量读取。

**涉及文件**：`api/app.py`、`config/settings.py`
**预计工时**：30min

**2) 前端 API 地址配置**

`api.ts` 中 `VITE_API_URL` 默认为空，Docker 环境下走同源代理。

**涉及文件**：`frontend/src/lib/api.ts`
**预计工时**：10min

### 1.3 Dockerfile

- **后端 `Dockerfile`**：`python:3.13-slim` + Chrome（Selenium 爬虫）
- **前端 `frontend/Dockerfile`**：多阶段构建，node → nginx
- **`frontend/nginx.conf`**：托管静态文件 + 代理 API/WS
- **`.dockerignore`**：排除本地不必要的文件

**涉及文件**：`Dockerfile`、`frontend/Dockerfile`、`frontend/nginx.conf`、`.dockerignore`
**预计工时**：1h

### 1.4 docker-compose.yml

三个服务：

| 服务 | 说明 |
|------|------|
| `api` | 后端 FastAPI，挂载数据卷 |
| `frontend` | Nginx + 前端静态文件，端口 8080 |
| `redis` | 缓存 + 未来任务队列 |

**涉及文件**：`docker-compose.yml`
**预计工时**：30min

### 1.5 部署文档

编写部署文档，包含：
1. 服务器购买 + 系统安装
2. 安装宝塔
3. 宝塔软件商店安装 Docker
4. 上传代码（git 或文件上传）
5. 配置 `.env`
6. `docker compose up -d` 启动
7. 宝塔 Nginx 反向代理 + HTTPS
8. 验证访问

**涉及文件**：`deploy/README.md`
**预计工时**：1h

### 第一阶段验收标准

- [ ] 代码已适配（CORS、VITE_API_URL）
- [ ] Dockerfile 构建成功
- [ ] `docker compose up -d` 一键启动三个服务
- [ ] 前端页面可访问，API 可调用
- [ ] 健康检查 `/health` 返回 `{"status": "ok"}`

---

## 第二阶段：安全加固（1-2 天）

**目标**：不裸奔上线

### 2.1 API 限流

引入 `slowapi`：

| 规则 | 限制 |
|------|------|
| 创建分析任务 | 5次/分钟/用户 |
| 登录/注册 | 10次/分钟/IP |
| 普通 API | 60次/分钟/IP |

**涉及文件**：`api/app.py`、`requirements.txt`
**预计工时**：1.5h

### 2.2 密码强度校验

| 规则 | 说明 |
|------|------|
| 最小长度 | 8 位 |
| 组成要求 | 至少包含字母和数字 |
| 用户名限制 | 不能是纯数字、不能含特殊字符 |

**涉及文件**：`api/routers/auth.py`、`api/schemas.py`
**预计工时**：30min

### 2.3 输入校验增强

所有 Pydantic 输入模型增加约束：

```python
from pydantic import StringConstraints
from typing import Annotated

class CreateCompetitorRequest(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    website: Annotated[str, StringConstraints(max_length=500)] = None
```

**涉及文件**：`api/schemas.py`
**预计工时**：1h

### 2.4 Secret Key 检测

启动时检测 `SECRET_KEY` 是否为默认值，是则报错退出：

```python
if settings.secret_key == "your-secret-key-change-in-production":
    raise RuntimeError("请修改 .env 中的 SECRET_KEY")
```

**涉及文件**：`config/settings.py`
**预计工时**：10min

### 2.5 宝塔安全配置

宝塔面板内完成：

| 配置 | 说明 |
|------|------|
| 修改面板默认端口 | 避免 8888 被扫 |
| 禁用面板默认用户 | 创建新管理员 |
| 开启系统防火墙 | 只放行 80/443/SSH |
| SSH 端口修改 | 避免 22 被暴力破解 |

**涉及文件**：无（宝塔操作）
**预计工时**：30min

### 第二阶段验收标准

- [ ] 限流生效，超限返回 429
- [ ] 弱密码注册被拒绝
- [ ] XSS 注入测试通过
- [ ] 服务器端口扫描无意外开放

---

## 第三阶段：运维 + 体验（1-2 天）

**目标**：出问题有感知，用户用得舒服

### 3.1 结构化日志

日志改为 JSON 格式，方便排查：

```json
{"time": "2026-06-14T10:00:00", "level": "ERROR", "module": "agent.nodes.searcher", "message": "搜索失败", "task_id": "xxx"}
```

**涉及文件**：`utils/logger.py`
**预计工时**：1h

### 3.2 健康检查增强

`/health` 返回各依赖状态：

```json
{
  "status": "ok",
  "database": "ok",
  "chroma": "ok",
  "version": "0.1.0",
  "uptime": "2h 15m"
}
```

**涉及文件**：`api/app.py`
**预计工时**：30min

### 3.3 数据备份

宝塔面板自带 "计划任务" 功能，设置每日凌晨备份：

| 备份内容 | 方式 |
|---------|------|
| `data/app.db` | SQLite 数据库文件 |
| `data/chroma/` | 向量数据库目录 |
| `data/reports/` | 报告文件 |
| `.env` | 配置文件 |

宝塔操作：计划任务 → 添加 shell 脚本 → 定时执行

**涉及文件**：新建 `scripts/backup.sh`
**预计工时**：30min

### 3.4 前端体验增强

| 任务 | 说明 |
|------|------|
| 全局 Error Boundary | 友好错误提示页 |
| 请求超时重试 | axios 自动重试 |
| 骨架屏 | 数据加载时的占位动画 |
| 空状态提示 | 没有数据时给引导文字 |

**涉及文件**：`frontend/src/App.tsx`、`frontend/src/lib/api.ts`
**预计工时**：2h

### 3.5 报告详情页

使用已安装的 `react-markdown` + `remark-gfm` 渲染报告：

| 功能 | 状态 |
|------|------|
| Markdown 渲染 | 已安装，需要写页面 |
| TOC 目录导航 | 需要实现 |
| 复制全文 | 需要实现 |
| 下载 Markdown 文件 | 需要实现 |

**涉及文件**：`frontend/src/pages/reports/[id].tsx`
**预计工时**：2h

### 3.6 README 更新

修正 README 为实际项目结构，补充宝塔部署说明。

**涉及文件**：`README.md`
**预计工时**：1h

### 第三阶段验收标准

- [ ] 日志按 JSON 格式输出
- [ ] 健康检查端点返回完整状态
- [ ] 数据备份脚本可运行
- [ ] 报告详情页正常渲染
- [ ] 前端有错误处理和加载态

---

## 上线前 Checklist

### 代码

- [ ] 所有测试通过：`pytest tests/ -v`
- [ ] `SECRET_KEY` 已修改为随机值
- [ ] `.env` 中的其他密钥已正确配置
- [ ] 前端 `npm run build` 构建成功

### 服务器

- [ ] 宝塔面板已安装
- [ ] Nginx 已配置并运行
- [ ] Docker 已安装并运行
- [ ] HTTPS 已申请（Let's Encrypt）
- [ ] SSH 端口已修改
- [ ] 防火墙已配置

### 功能

- [ ] 注册/登录正常
- [ ] 创建竞品正常
- [ ] 发起分析任务正常
- [ ] 查看报告正常
- [ ] 智能问答正常
- [ ] WebSocket 进度推送正常

### 运维

- [ ] 数据备份已配置
- [ ] 日志已配置

---

## 回滚方案

### 代码回滚

```bash
cd /www/wwwroot/project
git checkout v0.0.1           # 回到上一个标签
docker compose up -d --build  # 重新构建并启动
```

### 数据库回滚

```bash
# 从 Docker 数据卷备份恢复
# SQLite：直接替换 data/ 目录下的文件
# PostgreSQL（后续切换后）：pg_restore 恢复
```

### 前端回滚

```bash
git checkout v0.0.1
docker compose up -d --build
```

---

## 上线后迭代

| 版本 | 内容 | 时机 |
|------|------|------|
| v0.2 | SQLite → PostgreSQL 迁移 | 上线后用户量增长时 |
| v0.3 | 定时监控 + 变更预警 | 上线后按需 |
| v0.4 | 数据源扩展（社交媒体、财报） | 上线后按需 |
| v0.5 | 多用户 + 权限管理 | 多人使用时 |
