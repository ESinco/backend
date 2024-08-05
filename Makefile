.DEFAULT: help

SHELL := /bin/bash
PWD=$(shell pwd)

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

enter-pipenv:
	pipenv shell

run: init
	pipenv run python manage.py runserver

migrate:
	pipenv run python manage.py migrate

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache

lint:
	pipenv run pylint ./ProjetIn

pep:
	pipenv run pycodestyle ./backend
