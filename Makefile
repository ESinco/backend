.DEFAULT: help

SHELL := /bin/bash
PWD=$(shell pwd)
PYLINT=/bin/pylint
PEP=/bin/pep8

help:
	@echo "Usage"
	@echo "Initialize the environment: make init"
	@echo "Run the application: make run"
	@echo "Clean up: make clean"
	@echo "Lint the code: make lint"
	@echo "Check PEP8 compliance: make pep"

default:
	@make -s run
	@make -s init

init:
	pipenv install
	pipenv shell

run:
	pipenv run python manage.py runserver

migrate:
	pipenv run python manage.py migrate

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache

lint: venv
	$(PYLINT) . --recursive=y

pep: venv
	$(PEP) -v --global-config .pep8 ./backend