# Copyright (C) 2015 by Cyan Inc
# All rights reserved.
#
# PROPRIETARY NOTICE
# This Software consists of confidential information.
# Trade secret law and copyright law protect this Software.
# The above notice of copyright on this Software does not indicate
# any actual or intended publication of such Software.


import os
import json

from twisted.internet import defer

from rpsdk.highlevel import RpSdkDriverFactory
from rpsdk.model import RpSdkProduct
from rpsdk.market import RpSdkMarketClient
from rpsdk.utils.cyclonehelpers import Api, RpError
from rpsdk.drivers.product import StaticProductListDriver
# from rpsdk.drivers.eabpprov import EaBpprovCudDriver, EaBpprovListDriver, EaBpprovGetDriver
# from rpsdk.drivers.eadevice import EaDeviceCudDriver, EaDeviceListDriver, EaDeviceGetDriver
from juniper.rpdrivers import (
    EasdkBpprovCudDriver,
    EasdkBpprovListDriver,
    EasdkBpprovGetDriver,
    EasdkDeviceCudDriver,
    EasdkDeviceListDriver,
    EasdkDeviceGetDriver
    )

# Get resource by Provider Resource ID from Market API.
# Note that this returns a resource from market as-is, i.e. without any translation
# so the product ID etc. will be the ID in market
def get_market_resource_by_prid(market_api, domain_id, provider_resource_id):
    client = RpSdkMarketClient(domain_id, market_api)
    return client.get_resource_by_prid(provider_resource_id)

# Get resource by Resource ID from Market API.
# Note that this returns a resource from market as-is, i.e. without any translation
# so the product ID etc. will be the ID in market
def get_market_resource(market_api, domain_id, resource_id):
    client = RpSdkMarketClient(domain_id, market_api)
    return client.get_resource(resource_id)

# Get product from Market API.
# Note that this returns a product from market as-is, i.e. without any translation
def get_market_product(market_api, domain_id, product_id):
    client = RpSdkMarketClient(domain_id, market_api)
    return client.get_product(product_id)

def make_product(domain_id, resource_js):
    return RpSdkProduct(
                title=resource_js['title'],
                providerProductId=resource_js['provider_product_id'],
                active=resource_js['active'],
                providerData=resource_js['provider_data'],
                resourceTypeId=resource_js['resource_type'],
                domainId=domain_id
            )


def load_json(path):
    with open(path) as fd:
        return json.load(fd)


class GenericEaDriverFactory(RpSdkDriverFactory):
    def __init__(self, market_api, ea_settings):
        self.market_api = market_api
        self.ea_settings = ea_settings

        self.resources = load_json(os.path.join(self.ea_settings.RESOURCES_DIR, 'resources.json'))
        self.commands = load_json(os.path.join(self.ea_settings.RESOURCES_DIR, 'commands.json'))

        self._cache = {}

        self.load_commands()

    def load_commands(self):
        for resource, command in self.commands.iteritems():
            self.get_file(command)

    def get_file(self, filename):
        filename = os.path.join(self.ea_settings.RESOURCES_DIR, filename)
        if filename not in self._cache:
            self._cache[filename] = load_json(filename)
        return self._cache[filename]

    # def get_driver_type_for_domain(self, domain):
    #     if domain.id in self.driver_types:
    #         return self.driver_types[domain.id]
    #     else:
    #         return None

    # def get_device_id_for_domain(self, domain):
    #     return self.device_ids.get(domain.id, None)

    def get_driver_class(self, rp_type, command):
        class_map = {
            'device': {
                'cud': EasdkDeviceCudDriver,
                'get': EasdkDeviceGetDriver,
                'list': EasdkDeviceListDriver
            },
            'bpprov': {
                'cud': EasdkBpprovCudDriver,
                'get': EasdkBpprovGetDriver,
                'list': EasdkBpprovListDriver
            }
        }
        return class_map[rp_type][command]

    def make_driver(self, api, domain, command, command_info, device_id=None, resource=None):
        driver_cls = self.get_driver_class(command_info['type'], command)
        if command_info['type'] == 'bpprov':
            rpc_commands = {cmd: val['command'] for cmd, val in command_info['commands'].iteritems()}
            if device_id:
                # GET and CUD Drivers
                driver = driver_cls(device_id,
                                    domain.tenantId,
                                    command_info['product'],
                                    rpc_commands,
                                    command_info['provider_resource_id_field'],
                                    command_info.get('device_namespace_props'),
                                    command_info.get('label_field'))
            elif driver_cls == EasdkBpprovListDriver:
                # LIST Drivers
                driver = driver_cls(domain.tenantId,
                                    command_info['product'],
                                    rpc_commands,
                                    command_info['provider_resource_id_field'],
                                    command_info.get('device_namespace_props'),
                                    command_info.get('label_field'))
            else:
                raise ValueError('The driver class {} requries a device id'.format(driver_cls.__name__))
        elif command_info['type'] == 'device':
            if driver_cls == EasdkDeviceGetDriver:
                driver = driver_cls(domain.tenantId,
                                    command_info['product'],
                                    True,
                                    resource)
            else:
                driver = driver_cls(domain.tenantId,
                                command_info['product'])
        return driver

    def get_product_list_driver(self, domain):
        api = Api(domain.accessUrl, None)
        return StaticProductListDriver([make_product(domain.id, r) for r in self.resources])

    def get_resource_cud_driver(self, domain, resource):
        api = Api(domain.accessUrl, None)
        if resource.providerResourceId:
            device_id, _, _ = resource.providerResourceId.partition('::')
        else:
            # This means all EA RPs will require the device field when creating a resource
            device_id = resource.properties.get('device')

        command_file = self.commands[resource.productId]
        commands = self.get_file(command_file)

        return self.make_driver(api, domain, 'cud', commands, device_id=device_id)

    @defer.inlineCallbacks
    def get_resource_get_driver(self, domain, provider_resource_id):
        api = Api(domain.accessUrl, None)

        # From the ID alone we don't know the resource or product type
        # Need to consult market.
        # TODO: Improve this so consulting market is not needed

        resource = yield get_market_resource_by_prid(self.market_api,
                                                     domain.id,
                                                     provider_resource_id)

        if resource:
            productId = resource.productId
        else:
            raise RpError(404, "Resource with provider resource id '%s' not found" % provider_resource_id)

        product = yield get_market_product(self.market_api, domain.id, productId)

        device_id, _, _ = provider_resource_id.partition('::')

        #device_id = resource.properties["device"]

        # TODO: Is this OK? Need to check if the device is not active
        #device_resource = yield self.get_device_and_check_active(domain, device_id)

        command_file = self.commands[product.providerProductId]
        commands = self.get_file(command_file)

        driver =  self.make_driver(api, domain, 'get', commands, device_id=device_id, resource=resource)
        defer.returnValue(driver)

    def get_resource_list_driver(self, domain, resource_type_uri):
        api = Api(domain.accessUrl, None)

        resource_map = {r['resource_type']: r['provider_product_id'] for r in self.resources}

        command_file = self.commands[resource_map[resource_type_uri]]
        commands = self.get_file(command_file)
        return self.make_driver(api, domain, 'list', commands)
