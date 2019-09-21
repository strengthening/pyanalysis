# pyanalysis

<p align="left">
  <a href="https://github.com/strengthening/pyanalysis"><img alt="GitHub Actions status" src="https://github.com/strengthening/pyanalysis/workflows/build/badge.svg"></a>
</p>

## setup the package

python3 setup.py sdist

## build && push docker

```
# 构建docker image
sudo docker build --rm -t docker.lcgc.work/dw/pyanalysis:base .

# push docker image
sudo docker push docker.lcgc.work/dw/pyanalysis:base
```

## unittest  

python3 -m unittest test/log/log.py


## build


## release

git tag -a release-v2.0.5 -m "v2.0.5版本"
git push origin release-v2.0.5


## todo 封装邮件组件
