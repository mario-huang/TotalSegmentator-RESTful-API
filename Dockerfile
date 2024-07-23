FROM python:3.10.12

WORKDIR /app

ENV TZ=Asia/Shanghai
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY download_pretrained_weights.py .
RUN python download_pretrained_weights.py
COPY main.py .

ENTRYPOINT ["fastapi", "run"]
EXPOSE 8000