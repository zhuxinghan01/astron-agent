FROM python:3.11-slim
WORKDIR /opt/knowledge

ENV PATH=$PATH:/opt/knowledge
ENV PYTHONPATH /opt/knowledge
ENV UV_NO_CACHE=1

RUN pip install uv --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/

COPY uv.lock core/knowledge/pyproject.toml ./
COPY core/knowledge/uv.lock ./

RUN uv sync -i https://pypi.tuna.tsinghua.edu.cn/simple/

COPY core/common ./common
COPY core/knowledge ./knowledge

CMD ["uv", "run", "knowledge/main.py"]