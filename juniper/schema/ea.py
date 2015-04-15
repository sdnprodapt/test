'''
Created on Nov 18, 2014
Copyright(c) 2014, Cyan, Inc. All rights reserved.

@author: rreddy
'''
from easdk.schema import ea
from juniper.domain import oidoperation
from cymlrest.intrinsics import DeepCollection
from cymlrest.models import restapi


class Device(ea.Device):

    # https://domain.bp.cyaninc.com/oidOperation/v1
    oidOperation = DeepCollection(of=oidoperation.OidOperation, access='r')


class DeviceResourceCollection(restapi.ResourceCollection):
    of = Device
    key = 'id'
    access = 'lrp'
    operations = ea.device_operations


class Root(ea.Root):

    # https://domain.bp.cyaninc.com/device/v1
    devices = DeviceResourceCollection()

    # https://domain.bp.cyaninc.com/oidOperation/v1
    oidOperation = oidoperation.OidOperationResourceCollection()
