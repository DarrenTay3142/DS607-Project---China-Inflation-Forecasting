.PHONY: setup test tree
setup:
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
test:
	.venv/bin/pytest -q
tree:
	find . -maxdepth 3 -not -path './.git/*' | sort
