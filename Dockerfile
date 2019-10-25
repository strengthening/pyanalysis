FROM registry.cn-hongkong.aliyuncs.com/strengthening/pybase:latest

RUN mkdir -p /tmp
RUN mkdir -p /package
COPY . /tmp

# 编译包
RUN cd /tmp && python3 setup.py sdist
# 将编译好的包，放在指定位置。
RUN cp /tmp/dist/*.tar.gz /package
