.PHONY:all run test install
all: init test

init:
	@echo "TODO init dependences"

test:
	@echo "TODO test shell"

install:
	python3 -m build && pip install dist/pyanalysis-*.whl --force-reinstall
