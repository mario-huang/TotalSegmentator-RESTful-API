FROM python:3.12.3

WORKDIR /app

ENV TZ=Asia/Shanghai
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

COPY requirements.txt .
COPY main.py .

RUN pip install -r requirements.txt

ENTRYPOINT ["fastapi", "run"]     