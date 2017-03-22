#
# Module: Makefile
#
# Copyright(c) 2014, Cyan, Inc. All rights reserved.
#

HIDE ?= @
VENV ?= env

PIP ?= $(VENV)/bin/pip
PYTHON ?= $(VENV)/bin/python
INVOKE ?= $(VENV)/bin/dtk-invoke

PYPI ?= 'https://artifactory.ciena.com/api/pypi/blueplanet-pypi/simple'

TOOLKIT_DIR ?= '$(DEVOPS_TOOLKIT)/.devops-toolkit'
IS_DEVOPS_TOOLKIT := $(shell env | grep DEVOPS_TOOLKIT)
EMPTY = 
ifeq ($(IS_DEVOPS_TOOLKIT), $(EMPTY))
# internal user
PIP_PYPI := -i $(PYPI)
PIP_FIND_LINKS :=
else
# external user
PIP_PYPI :=
PIP_FIND_LINKS := --find-links=$(TOOLKIT_DIR)
endif

all: help

clean:
	rm -rf *.deb
	rm -rf build
	rm -rf dist
	rm -rf *.egg
	rm -rf *.egg-info
	rm -rf *.pyc
	rm -rf env

basic-help:
	@echo "  help         this list"
	@echo "  clean        delete temporary files"

env-help:
	@echo " --------------------------------------------------------"
	@echo "/ virtualenv backed commands                            /"
	@echo "--------------------------------------------------------"
	@echo "  prepare-venv install requirements and self into virtualenv $(VENV)"
	@echo "  fresh-venv   prepare a virtualenv without locked requirements"

ifneq ("$(wildcard $(INVOKE))","")
INVOKE_HELP := $(INVOKE) -h
else
INVOKE_HELP := 
endif

help: basic-help env-help
	@echo ""
	$(HIDE) $(INVOKE_HELP)

# virtualenv related commands
prepare-venv:
	$(HIDE)virtualenv $(VENV) --no-pip
	$(HIDE)$(VENV)/bin/easy_install pip==9.0.1
	$(HIDE)$(PIP) install $(PIP_FIND_LINKS) $(PIP_PYPI) -c requirements.txt dtk-invoke
	$(INVOKE) prepare-venv

fresh-venv:
	$(HIDE)rm -rf $(VENV)
	$(HIDE)virtualenv $(VENV) --no-pip
	$(HIDE)$(VENV)/bin/easy_install pip==9.0.1
	$(HIDE)$(PIP) install $(PIP_FIND_LINKS) $(PIP_PYPI) dtk-invoke
	$(INVOKE) fresh-venv


# Legacy targets provided for convenience.
# Please prefer main targets above or dtk-invoke directly

toolkit-venv:
	$(HIDE)$(MAKE) prepare-venv

test:
	$(HIDE)$(INVOKE) test

image:
	$(HIDE)$(INVOKE) image

dconfigure:
	$(HIDE)$(INVOKE) image

dtest:
	$(HIDE)$(INVOKE) dtest

dutest:
	$(HIDE)$(INVOKE) dtest

ditest:
