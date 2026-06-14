# =========================================
# 智能竞品分析 Agent - 后端 Dockerfile
# =========================================

# ---- 构建阶段：只安装 Python 依赖 ----
FROM python:3.13-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# ---- 运行阶段 ----
FROM python:3.13-slim

# Chrome 暂不安装（Selenium 爬 JS 页面功能需要时再加）
# 安装方式：apt-get 在 Debian slim 上太慢，后续改用 Playwright

WORKDIR /app

# 从构建阶段复制已安装的 Python 库
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制代码
COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
