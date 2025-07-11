# 选择一个体积小、内置 Python 的基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 把依赖文件复制进去，再安装依赖（利用 Docker 缓存）
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 优先使用 IPv4，避免容器内 Python 尝试 IPv6 导致无法连通
RUN sed -i \
    -e 's/^#precedence ::ffff:0:0\/96  100/precedence ::ffff:0:0\/96  100/' \
    /etc/gai.conf

# 把整个项目都复制到 /app
COPY . .

# 暴露 8000 端口
EXPOSE 8000

# 启动命令，使用 Uvicorn 运行 FastAPI 应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
