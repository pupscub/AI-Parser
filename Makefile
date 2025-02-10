.PHONY: dev help clean setup build

help:
	@echo "make dev     - Install development dependencies"
	@echo "make setup   - Dev setup"
	@echo "make clean   - Remove virtual environment"
	@echo "make build   - Build project"

setup:
	python3 -m venv .venv
	.venv/bin/python3 -m pip install --upgrade pip
	.venv/bin/python3 -m pip install -e . 
	.venv/bin/pip install -r requirements.txt

dev: setup
	.venv/bin/pip install -r dev-requirements.txt

clean:
	rm -rf .venv

build:
	echo "Building project..."
	# Add any build commands specific to your project here
