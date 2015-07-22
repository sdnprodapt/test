#!/usr/bin/env python
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

from cymlrest.objects import Object
from cymlrest.intrinsics import Str, ObjF
from cymlrest.models.restapi import ResourceCollection, RestApi

from cyml.meta import CLS

from bpramodels.schema.domain import Domain


class OidOperation(Object):
    type = Str(desc='rpc Command type to oidOperation', access='cr')
    parameters = ObjF(name='object', desc='parameters to bpprov command', access='cr')


class OidOperationResourceCollection(ResourceCollection):
    of = OidOperation
    access = 'c'
    virtual = True
    deepAccessors = (('devices', 'deviceid', 'c'),)


class OidOperationDomain(Domain):
    CLS.URI = 'https://domain.bp.cyaninc.com/oidOperation/v1'
    CLS.ID = 'OIDOPERATION'
    CLS.EXTENDS = 'https://domain.bp.cyaninc.com/device/v1'
    oidOperation = OidOperationResourceCollection()


oidOperationDomainRestApi = RestApi(resources=OidOperationDomain)
