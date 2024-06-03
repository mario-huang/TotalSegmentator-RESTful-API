FROM ubuntu:24.04

ENV TZ=Asia/Shanghai

RUN apt update && \
    apt install -y tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt install -y python3

RUN pip install -r requirements.txt

RUN python 