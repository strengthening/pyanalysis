FROM python:3.5

RUN pip3 install --upgrade pip
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pymysql==0.9.3
RUN mkdir -p /tmp
COPY . /tmp

RUN cd /tmp && python3 setup.py sdist && cd dist && pip3 install pyanalysis-1.0.tar.gz
RUN rm /tmp -rf
