#
# Module: Makefile
#
# Copyright(c) 2014, Cyan, Inc. All rights reserved.
#

HIDE := @
VENV := env
EA_NAME := $(shell python setup.py --name)

PROJECT_DIR ?= $(shell pwd)
MODEL_DIR := $(PROJECT_DIR)/$(EA_NAME)/model
SIM_DIR := $(MODEL_DIR)/sim

PIP := $(VENV)/bin/pip
PYTHON := $(VENV)/bin/python
BPFPM ?= bpfpm

PYPI ?= 'http://pypi.cyanoptics.com/simple/'

clean: 
	rm -rf *.deb
	rm -rf blueplanet/extern
	rm -rf build
	rm -rf dist
	rm -rf *.egg

help: 
	@echo "  help         this list"
	@echo "  clean        delete temporary files"
	@echo "  test         run unit tests, model tests, and sim tests"
	@echo "  utest        run unit tests"
	@echo "  coverage     run unit tests with code coverage reporting"

test: python-unit-test test-model-validate test-model-commands test-model-error test-sim test-flake8

utest: python-unit-test

prepare-venv:
	# Workaround for pyang uninstall
	$(HIDE)rm -rf $(VENV)/lib/python2.7/site-packages/pyang*
	$(HIDE)virtualenv $(VENV)
	$(HIDE)$(VENV)/bin/pip install --upgrade -i $(PYPI) -r requirements.txt

python-unit-test:
	$(HIDE)$(VENV)/bin/nosetests -v

test-flake8:
	$(HIDE)$(VENV)/bin/flake8 $(EA_NAME)

test-model-validate:
	$(HIDE)$(VENV)/bin/bpprov-cli validate $(MODEL_DIR)

test-model-commands:
	$(HIDE)$(VENV)/bin/bpprov-cli test $(MODEL_DIR)

test-model-error:
	$(HIDE)$(VENV)/bin/bpprov-cli test-error $(MODEL_DIR)

test-sim:
	$(HIDE)$(VENV)/bin/bpprov-cli test-sim $(SIM_DIR)

coverage:
	$(HIDE)$(VENV)/bin/nosetests --with-coverage --cover-erase --cover-package $(EA_NAME)

BP_DEB_DIR := $(PROJECT_DIR)/blueplanet/extern
BP_DEB_BASE := $(BP_DEB_DIR)/python-$(EA_NAME)

bp-app:
	$(eval VERSION := $(shell python setup.py --version))
	$(eval ITERATION := $(shell python iteration.py))
# Uninstall development egg ...
	$(PYTHON) setup.py develop -u
# ... and install real one
	$(PIP) install --no-deps .
	mkdir -p $(BP_DEB_DIR)
# remove any old debians, we wouldn't want to package up old and new together
	rm -f $(BP_DEB_BASE)*.deb
# package virtualenv into debian and place in extern
	cd $(BP_DEB_DIR); \
		fpm -s dir -t deb -n python-$(EA_NAME) -v $(VERSION) --iteration $(ITERATION) \
		$(PROJECT_DIR)/$(VENV)/=/opt/cyan/$(EA_NAME)
# restore development environment
	$(PIP) uninstall -y $(EA_NAME)
	$(PIP) install --no-deps -e .
# make the blueplanet application
	$(BPFPM) -f --debian blueplanet/extern --config blueplanet/project.cfg \
		--hooks blueplanet/hooks --map blueplanet/init/=/etc/init --iteration $(ITERATION)

