FROM python:3.11-slim

WORKDIR /opt/rpa-server

ENV PATH=$PATH:/opt/rpa-server
ENV PYTHONPATH /opt/rpa-server

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]