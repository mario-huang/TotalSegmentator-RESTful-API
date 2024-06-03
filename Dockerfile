FROM ubuntu:24.04

ENV TZ=Asia/Shanghai
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

RUN apt update
RUN apt install -y python3
RUN apt install -y python3-pip
RUN pip install -r requirements.txt

RUN python 