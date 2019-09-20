FROM python:3.5

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

RUN mkdir -p /tmp
COPY . /tmp

RUN cd /tmp && python3 setup.py sdist && cd dist && pip3 install pyanalysis-2.0.0.tar.gz
RUN rm /tmp -rf
