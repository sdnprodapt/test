#
# Module: bp2.mk
#
# Copyright(c) 2014, Cyan, Inc. All rights reserved.
#

bp2-help:
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

# docker related commands
#
PACKAGE := $(shell python setup.py --name)
DOCKER_RUN_ARGS ?= -ti --rm
PASS_THROUGH_ENV := $(if $(EXTRA_ENV),$(shell python -c 'print "--env "," --env ".join("$(EXTRA_ENV)".split(";"))'))
DOCKER_RUN := docker run $(DOCKER_RUN_ARGS) $(PASS_THROUGH_ENV)
DOCKER_BUILD_EXTRA ?=
DOCKER_BUILD := docker build $(DOCKER_BUILD_EXTRA)
DOCKER_CMD ?= $(PACKAGE) --configpath /dev/shm
DOCKER_IMAGE ?= cyan/$(PACKAGE)
DOCKER_IMAGE_BASE := cyan/$(PACKAGE)-base
DOCKER_IMAGE_SIM := cyan/$(PACKAGE)-sim
DOCKERFILE_RA := docker/ra
DOCKERFILE_SIM := docker/sim
DOCKER_CONTAINER ?= $(PACKAGE)
DOCKER_PUBLISH ?= -p 8080:8080
DOCKER_MOUNT := --volume /dev/log:/dev/log
DOCKER_SRC := /bp2/src
DOCKER_BP2_IGNORE_ENV := \
	-e "BP2_IGNORE=True"
DOCKER_BP2_IGNORE_RUN := $(DOCKER_RUN) $(DOCKER_BP2_IGNORE_ENV)
DOCKER_APP_ENV ?=
DMODEL_DIR := $(PACKAGE)/model
DSIM_DIR := $(DMODEL_DIR)/sim
TAGS := $(shell python setup.py --version)
REGISTRY ?= artifactory.ciena.com/blueplanet

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
# NOTE: it is not possible to use BP2_IGNORE here as if we set it, it gets
#  committed to the image
	docker run $(DEV_VOLUME_MOUNT) $(NAME_MAP) $(DOCKER_IMAGE_BASE) /bin/bash -c 'touch /bp2/.dev && scripts/docker-link-src'
	docker commit $(DOCKER_CONTAINER) $(DOCKER_IMAGE_BASE):latest
	docker rm $(DOCKER_CONTAINER)

image: image-base
	$(DOCKER_BUILD) -t $(DOCKER_IMAGE) $(DOCKERFILE_RA)

image-dev: image-base-dev
	$(DOCKER_BUILD) -t $(DOCKER_IMAGE) $(DOCKERFILE_RA)

image-sim: image-base
	$(DOCKER_BUILD) -t $(DOCKER_IMAGE_SIM) $(DOCKERFILE_SIM)

image-sim-dev: image-base-dev
	$(DOCKER_BUILD) -t $(DOCKER_IMAGE_SIM) $(DOCKERFILE_SIM)

# if we have a /bp2/.dev, then this is a dev image
DEV_CHECK = /bin/bash -c 'if [ -f /bp2/.dev ]; then echo "$(DEV_VOLUME_MOUNT)"; fi'
dev-check:
	$(eval DEV_CHECK_OUT := $(shell $(DOCKER_BP2_IGNORE_RUN) $(DOCKER_IMAGE) $(DEV_CHECK)))

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

dutest: dteam-City-args dtest

ditest:

###Tagging
tag: 
	$(foreach tag, ${TAGS}, docker tag -f $(DOCKER_IMAGE):latest $(REGISTRY)/$(PACKAGE):${tag} &&) true

push: tag
	$(foreach tag, ${TAGS}, docker push $(REGISTRY)/$(PACKAGE):${tag} &&) true

dteam-City-args:
	@echo "Running Team City Setup $(DOCKER_CONTAINER)"
	$(eval DOCKER_RUN_ARGS = -i --rm)
	$(eval DOCKER_RUN = docker run $(DOCKER_RUN_ARGS) $(PASS_THROUGH_ENV))
	$(eval DOCKER_BP2_IGNORE_RUN = $(DOCKER_RUN) $(DOCKER_BP2_IGNORE_ENV))
	@echo "Docker Values Have been Set"
	@echo "Docker BP2 Ignore Run is $(DOCKER_BP2_IGNORE_RUN)"
