# 编译阶段
FROM registry.cn-hongkong.aliyuncs.com/strengthening/pybase:latest
# as builder

RUN mkdir -p /tmp
RUN mkdir -p /package
COPY . /tmp

RUN cd /tmp && python3 setup.py sdist
RUN cp /tmp/dist/*.tar.gz /package
