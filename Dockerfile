FROM python:3.12.3

WORKDIR /app

ENV TZ=Asia/Shanghai
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

COPY download_pretrained_weights.py .
COPY requirements.txt .
COPY main.py .

RUN pip install -r requirements.txt
RUN python download_pretrained_weights.py

ENTRYPOINT ["fastapi", "run"]
EXPOSE 8000