CURRENT_DIR := $(shell pwd)

ifndef NAME
  NAME = Flaskov
endif

VIRTUALENV_DIR = env
INTERPRETER = $(CURRENT_DIR)/$(VIRTUALENV_DIR)/bin/
PATH := ${PATH}:$(INTERPRETER)

help:
	@echo "Usage: $ make <target> [NAME=Flaskproject]"
	@echo " > create    : create ${NAME}"
	@echo " > debug 	: run ${NAME} in debug mode"
	@echo " > test	 	: alias for pytest"
	@echo " > env 		: activates venv"

create:
	@echo "[RUN]: create flaskov"
	FLASK_APP="src/flaskov" flask run

debug:
	@echo "[DEBUG]: run flaskov in debug mode"
	FLASK_APP="src/flaskov" FLASK_ENV="development" flask run

test:
	@echo "[TEST]: running pytest suite"
	@coverage run --source="./src/" -m pytest

env:
	@echo "[VENV]: activate virtualenv"
	@source env/bin/activate