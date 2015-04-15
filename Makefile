HIDE ?= @
VENV := env
PACKAGE := $(shell python setup.py --name)

PROJECT_DIR ?= $(shell pwd)
MODEL_DIR := $(PROJECT_DIR)/$(PACKAGE)/model
SIM_DIR := $(MODEL_DIR)/sim

PIP := $(VENV)/bin/pip
PYTHON := $(VENV)/bin/python
BPFPM ?= $(VENV)/bin/bpfpm

PYPI ?= 'https://pypi.cyanoptics.com/simple/'
GIT_REPO_NAME ?= $(shell basename `git remote show -n origin | grep Fetch | cut -d. -f3`)
all: help

clean:
	rm -rf *.deb
	rm -rf blueplanet/extern
	rm -rf build
	rm -rf dist
	rm -rf *.egg
	rm -rf *.pyc
	rm -rf env

help:
	@echo "  help         this list"
	@echo "  clean        delete temporary files"
	@echo " --------------------------------------------------------"
	@echo "/ virtualenv backed commands                            /"
	@echo "--------------------------------------------------------"
	@echo "  prepare-venv install requirements and self into virtualenv ./env"
	@echo "  test         run unit tests, model tests, and sim tests"
	@echo "  utest        run unit tests"
	@echo "  coverage     run unit tests with code coverage reporting"
	@echo "  requirements generate new requirements.txt"
	@echo "  release      release version with bpfrelease"
	@echo " --------------------------------------------------------"
	@echo "/ docker backed commands                                /"
	@echo "--------------------------------------------------------"
	@echo "  image        build image"
	@echo "  image-dev    build image, mount src, install editable"
	@echo "  run          run container (interactive)"
	@echo "  start        start container (detached)"
	@echo "  stop         stop container (detached)"
	@echo "  restart      restart container (detached)"
	@echo "  enter        enter running container bash"
	@echo "  interact     enter new container bash"
	@echo "  dtest        run unit tests with code coverage reporting, model, sim, and flake8 tests"
	@echo "  dcoverage    run unit tests with code coverage reporting"
	@echo "  dtest-flake8 run flake8 tests"
	@echo "  dconfigure   TeamCity target, prepare for testing, runs image"
	@echo "  dutest       TeamCity target, for unittest, runs dtest"
	@echo "  ditest       TeamCity target, for integration tests"

# virtualenv related commands
#
.prepare-venv:
# Workaround for pyang uninstall
	$(HIDE)rm -rf $(VENV)/lib/python2.7/site-packages/pyang*
	$(HIDE)virtualenv $(VENV)
	$(HIDE)$(PIP) install --upgrade -i $(PYPI) -r requirements.txt --src .src
	$(HIDE)$(PIP) install -e .

prepare-venv: .prepare-venv
	$(HIDE)$(PIP) install -r requirements-src.txt --src .src --exists-action i

requirements:
	$(HIDE)$(PIP) uninstall -y $(PACKAGE)
	$(HIDE)$(PIP) freeze > requirements.txt
	$(HIDE)$(PIP) install -e .

release:
	$(HIDE)$(VENV)/bin/bpfrelease --organization ea --repository $(GIT_REPO_NAME) --project .

test: utest test-model-commands test-model-validate test-model-error test-sim test-flake8

utest:
	$(HIDE)$(VENV)/bin/nosetests -v

test-flake8:
	$(HIDE)$(VENV)/bin/flake8 $(PACKAGE)

test-model-validate:
	$(HIDE)$(VENV)/bin/bpprov-cli validate $(MODEL_DIR)

test-model-commands:
	$(HIDE)$(VENV)/bin/bpprov-cli test $(MODEL_DIR)

test-model-error:
	$(HIDE)$(VENV)/bin/bpprov-cli test-error $(MODEL_DIR)

test-sim:
	$(HIDE)$(VENV)/bin/bpprov-cli test-sim $(SIM_DIR)

coverage:
	$(HIDE)$(VENV)/bin/nosetests --with-coverage --cover-erase --cover-package $(PACKAGE)

BP_DEB_DIR := $(PROJECT_DIR)/blueplanet/extern
BP_DEB_BASE := $(BP_DEB_DIR)/python-$(PACKAGE)

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
		fpm -s dir -t deb -n python-$(PACKAGE) -v $(VERSION) --iteration $(ITERATION) \
		$(PROJECT_DIR)/$(VENV)/=/opt/cyan/$(PACKAGE)
# restore development environment
	$(PIP) uninstall -y $(PACKAGE)
	$(PIP) install --no-deps -e .
# make the blueplanet application
	$(BPFPM) -f --debian blueplanet/extern --config blueplanet/project.cfg \
		--hooks blueplanet/hooks --map blueplanet/init/=/etc/init --semantic-version $(VERSION) --iteration $(ITERATION)


# docker related commands
#
DOCKER_RUN_ARGS ?= -ti --rm
PASS_THROUGH_ENV := $(if $(EXTRA_ENV),$(shell python -c 'print "--env "," --env ".join("$(EXTRA_ENV)".split(";"))'))
DOCKER_RUN := docker run $(DOCKER_RUN_ARGS) $(PASS_THROUGH_ENV)
DOCKER_BUILD_EXTRA ?=
DOCKER_BUILD := docker build $(DOCKER_BUILD_EXTRA)
DOCKER_CMD ?= $(PACKAGE) --configpath /tmp
DOCKER_IMAGE ?= cyan/$(PACKAGE)
DOCKER_IMAGE_BASE := cyan/$(PACKAGE)-base
DOCKER_IMAGE_SIM := cyan/$(PACKAGE)-sim
DOCKERFILE_EA := docker/ea
DOCKERFILE_SIM := docker/sim
DOCKER_CONTAINER := $(PACKAGE)
DOCKER_PUBLISH ?= -p 8184:8080
DOCKER_MOUNT :=
DOCKER_SRC := /bp2/src
DOCKER_BP2_IGNORE_ENV := \
	-e "BP2_IGNORE=True"
DOCKER_BP2_IGNORE_RUN := $(DOCKER_RUN) $(DOCKER_BP2_IGNORE_ENV)
DOCKER_APP_ENV ?=
DMODEL_DIR := $(PACKAGE)/model
DSIM_DIR := $(DMODEL_DIR)/sim

NAME_MAP := --name="$(DOCKER_CONTAINER)"

OS := $(shell uname)
ifeq ($(OS), Darwin)
# assumes here you are tunneled from a mac through the vm, and that your dev root
# is mapped to /vagrant, meaning you should see ls ../Vagrantfile from where this
# Makefile is.
DEV_HOST_BASE ?= /vagrant/$(shell pwd | xargs basename)
else
DEV_HOST_BASE ?= $(shell pwd)
endif
DEV_VOLUME_MOUNT := -v $(DEV_HOST_BASE):$(DOCKER_SRC)

image-base:
	$(DOCKER_BUILD) -t $(DOCKER_IMAGE_BASE) .

image-base-dev: image-base
	docker rm $(DOCKER_CONTAINER) 2>&1 >/dev/null || true
# create an easter egg file /bp2/.dev in the image so we know it
# is a dev image.  Then just run a script to install any libs and
# link your mounted code.
# unfortunately this line overwrites the default CMD, hence we always specify.
	docker run $(DEV_VOLUME_MOUNT) $(DOCKER_BP2_IGNORE) $(NAME_MAP) $(DOCKER_IMAGE_BASE) /bin/bash -c 'touch /bp2/.dev && scripts/docker-link-src'
	docker commit $(DOCKER_CONTAINER) $(DOCKER_IMAGE_BASE):latest
	docker rm $(DOCKER_CONTAINER)

image: image-base
	$(DOCKER_BUILD) -t $(DOCKER_IMAGE) $(DOCKERFILE_EA)

image-dev: image-base-dev
	$(DOCKER_BUILD) -t $(DOCKER_IMAGE) $(DOCKERFILE_EA)

image-sim: image-base
	$(DOCKER_BUILD) -t $(DOCKER_IMAGE_SIM) $(DOCKERFILE_SIM)

image-sim-dev: image-base-dev
	$(DOCKER_BUILD) -t $(DOCKER_IMAGE_SIM) $(DOCKERFILE_SIM)

# if we have a /bp2/.dev, then this is a dev image
DEV_CHECK = /bin/bash -c 'if [ -f /bp2/.dev ]; then echo "$(DEV_VOLUME_MOUNT)"; fi'
dev-check:
	$(eval DEV_CHECK_OUT := $(shell $(DOCKER_RUN) $(DOCKER_BP2_IGNORE) $(DOCKER_IMAGE) $(DEV_CHECK)))

finalize-mount: dev-check
	$(eval FINAL_MOUNT := $(DOCKER_MOUNT) $(DEV_CHECK_OUT))

run: finalize-mount
	$(DOCKER_RUN) $(FINAL_MOUNT) $(NAME_MAP) $(DOCKER_PUBLISH) $(DOCKER_APP_ENV) $(DOCKER_IMAGE) $(DOCKER_CMD)

start: finalize-mount
	docker run -d $(FINAL_MOUNT) $(NAME_MAP) $(DOCKER_PUBLISH) $(DOCKER_APP_ENV) $(DOCKER_IMAGE) $(DOCKER_CMD)

stop:
	docker stop $(DOCKER_CONTAINER)
	docker rm $(DOCKER_CONTAINER) || true

restart: stop start

enter:
	docker exec -ti $(DOCKER_CONTAINER) '/bin/bash'

interact: finalize-mount
	$(DOCKER_BP2_IGNORE_RUN) $(FINAL_MOUNT) $(DOCKER_IMAGE) '/bin/bash'

dtest: dcoverage dtest-model-commands dtest-model-validate dtest-model-error dtest-sim dtest-flake8

dtest-flake8: finalize-mount
	$(DOCKER_BP2_IGNORE_RUN) $(FINAL_MOUNT) $(DOCKER_IMAGE) flake8 $(PACKAGE)

dcoverage: finalize-mount
	$(DOCKER_BP2_IGNORE_RUN) $(FINAL_MOUNT) $(DOCKER_IMAGE) nosetests -v --with-coverage --cover-erase --cover-package $(PACKAGE)

dtest-model-validate: finalize-mount
	$(DOCKER_BP2_IGNORE_RUN) $(FINAL_MOUNT) $(DOCKER_IMAGE) bpprov-cli validate $(DMODEL_DIR)

dtest-model-commands: finalize-mount
	$(DOCKER_BP2_IGNORE_RUN) $(FINAL_MOUNT) $(DOCKER_IMAGE) bpprov-cli test $(DMODEL_DIR)

dtest-model-error: finalize-mount
	$(DOCKER_BP2_IGNORE_RUN) $(FINAL_MOUNT) $(DOCKER_IMAGE) bpprov-cli test-error $(DMODEL_DIR)

dtest-sim: finalize-mount
	$(DOCKER_BP2_IGNORE_RUN) $(FINAL_MOUNT) $(DOCKER_IMAGE) bpprov-cli test-sim $(DSIM_DIR)

### TeamCity Targets

dconfigure: image

dutest: dtest

ditest:
	$(HIDE)./scripts/integration-start
	$(HIDE)sleep 4
	$(HIDE)$(VENV)/bin/python $(PACKAGE)/tests/test_integration.py || true
	$(HIDE)./scripts/integration-log
	$(HIDE)./scripts/integration-stop