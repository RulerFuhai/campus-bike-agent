# 选择一个体积小、内置 Python 的基础镜像
FROM python:3.11-slim

# 切换到工作目录
WORKDIR /app

# 先复制依赖清单并安装 Python 包，同时安装调试工具
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && apt-get update \
    && apt-get install -y iputils-ping telnet \
    && rm -rf /var/lib/apt/lists/*

# 修改 /etc/gai.conf，让 glibc 优先使用 IPv4
RUN sed -i 's/^#precedence ::ffff:0:0\/96  100/precedence ::ffff:0:0\/96  100/' /etc/gai.conf

# 把项目代码复制进来
COPY . .

# 暴露 8000 端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
