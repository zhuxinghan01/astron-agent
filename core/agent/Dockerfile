FROM python:3.11-slim

WORKDIR /opt
ENV PATH=$PATH:/opt/agent
ENV PYTHONPATH /opt/agent:/opt

# 复制 common 包和 agent 目录
COPY common/ /opt/common/
COPY agent/ /opt/agent/

WORKDIR /opt/agent
RUN uv sync
CMD ["python", "main.py"]
