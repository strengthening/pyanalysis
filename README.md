# pyanalysis

[![action](https://github.com/strengthening/pyanalysis/workflows/build/badge.svg)](https://github.com/strengthening/pyanalysis)
[![action](https://github.com/strengthening/pyanalysis/workflows/release/badge.svg)](https://github.com/strengthening/pyanalysis)

## feature

- mysql & mysql pool
- log & log_handle
- simple mail component
- simple date &time &datetime &timestamp component

## unittest  

python3 -m unittest test/log/log.py


## build

It will auto build when you push a branch to the origin.  


## release

Tag like `release-v2.0.1` will trigger the release process. It will push the docker to aliyun.

```

git tag -a release-$version -m "$version版本"
git push origin release-$version

```

## install
```
python setup.py sdist
pip install dist/XXXX.tar.gz
```
