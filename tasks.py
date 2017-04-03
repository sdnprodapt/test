#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from invoke import task
from dtk_invoke.docker import image, dtest


@task
def custom(ctx):
    '''
    example custom task
    '''
    ctx.run('echo Executing custom task')


# TeamCity tasks
@task(image)
def dconfigure(ctx):
    '''
    TeamCity task, prepare for testing, runs image
    '''
    pass


@task(dtest)
def dutest(ctx):
    '''
    TeamCity task, for unittest, runs dtest
    '''
    pass


@task
def ditest(ctx):
    '''
    TeamCity task, for integration tests
    '''
    pass
