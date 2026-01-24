import io
import re

from setuptools import setup


with io.open("pyanalysis/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name="pyanalysis",
    version=version,
    author="strengthening",
    author_email="ducg@foxmail.com",
    # url='http://www.you.com/projectname',
    packages=["pyanalysis"],
    install_requires=[
        "arrow>=1.0.0",
        "PyMySQL>=1.0.0",
    ],
    python_requires=">=3.8",
)
