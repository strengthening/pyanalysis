# pyanalysis

## setup the package

python3 setup.py sdist

## build && push docker

```
# 构建docker image
sudo docker build --rm -t docker.lcgc.work/dw/pyanalysis:base .

# push docker image
sudo docker push docker.lcgc.work/dw/pyanalysis:base
```
