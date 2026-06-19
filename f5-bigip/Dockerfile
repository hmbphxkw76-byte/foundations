# BIG-IP 配置查询 Agent - Dockerfile

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动应用
# 默认不启用 Langfuse，如需启用请设置环境变量 ENABLE_LANGFUSE=true
CMD ["python", "app.py"]
