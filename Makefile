.PHONY:all run test install
all: init test

init:
	@echo "TODO init dependences"

test:
	@echo "TODO test shell"

install:
	python3 setup.py sdist && sudo pip3 install dist/pyanalysis-2.0.2.tar.gz
