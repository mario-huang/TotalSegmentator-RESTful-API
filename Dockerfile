FROM ubuntu:24.04

ENV TZ=Asia/Shanghai
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

RUN apt update && \
    apt install -y python3 && \
    apt install -y python3-pip && \
    apt install -y python3-venv

RUN python3 -m venv .venv

RUN pip3 install -r requirements.txt

RUN python3 