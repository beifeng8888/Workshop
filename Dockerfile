FROM ubuntu:latest
LABEL authors="hwx"

ENTRYPOINT ["top", "-b"]

# 使用官方 Python 镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 运行 Django 开发服务器
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]