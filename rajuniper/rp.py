# Copyright (C) 2015 by Cyan Inc
# All rights reserved.
#
# PROPRIETARY NOTICE
# This Software consists of confidential information.
# Trade secret law and copyright law protect this Software.
# The above notice of copyright on this Software does not indicate
# any actual or intended publication of such Software.


import os
import simplejson as json
import logging
from urlparse import urlparse

from twisted.internet import defer, reactor
from twisted.internet.task import deferLater
from jinja2 import Environment, FileSystemLoader

from rasdk.controller import Controller
from rasdk.access.session import SessionAccess

from rpsdk.highlevel import RpSdkDriverFactory
from rpsdk.model import RpSdkProduct
from rpsdk.market import RpSdkMarketClient
from rpsdk.utils.cyclonehelpers import Api, RpError
from rpsdk.drivers.product import StaticProductListDriver

from rajuniper.rpdrivers import (
    RasdkBpprovCudDriver,
    RasdkBpprovListDriver,
    RasdkBpprovGetDriver,
    RasdkDeviceCudDriver,
    RasdkDeviceListDriver,
    RasdkDeviceGetDriver
    )

log = logging.getLogger(__name__)

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


def parse_url(url):
    parsed = urlparse(url)
    if ':' in parsed.netloc:
        host, port = parsed.netloc.split(':')
        return parsed.scheme, host, port
    else:
        return parsed.scheme, parsed.netloc, None

class GenericRaDriverFactory(RpSdkDriverFactory):
    def __init__(self, market_api, ra_settings):
        self.market_api = market_api
        self.ra_settings = ra_settings

        self.resources = load_json(os.path.join(self.ra_settings.RESOURCES_DIR, 'resources.json'))
        self.commands = load_json(os.path.join(self.ra_settings.RESOURCES_DIR, 'commands.json'))

        # mapping from domain ids to sessions
        self.domains = {}

        self._cache = {}

        self.load_commands()

        if self.ra_settings.NETWORK_MANAGER_RP:
            self.env = Environment(loader=FileSystemLoader(os.path.join(self.ra_settings.BPPROV_MODEL_DIRPATH, 'templates')))
        else:
            self.env = None

    def load_commands(self):
        for resource, command in self.commands.iteritems():
            self.get_file(command)

    def get_file(self, filename):
        filename = os.path.join(self.ra_settings.RESOURCES_DIR, filename)
        if filename not in self._cache:
            self._cache[filename] = load_json(filename)
        return self._cache[filename]

    # def get_session_for_connection(self, root, hostname, port):
    #     def ports_for_session(session):
    #         return [session.connection[ep]['hostport']
    #                 for ep in self.ra_settings.ENDPOINTS]

    #     for session in root.sessions.itervalues():
    #         if session.connection.hostname == hostname and port in ports_for_session(session):
    #             return session
    #     return None

    @defer.inlineCallbacks
    def get_session(self, domain):
        if domain.id not in self.domains:
            root = Controller.instance().root
            session_access = SessionAccess(root)
            # TODO: Check that there isn't already a session for this hostname and port
            # If there is associate it with the domain id and return that
            # session = self.get_session_for_connection(root, hostname, port)
            # if session is not None:
            #     self.domains[domain.id] = session
            #     log.info('Found existing session %s for domain %s', session.id, domain.id)
            #     defer.returnValue(session)

            log.info('Creating session for domain %s', domain.id)
            session_create_params = self.get_file('session-templates.json')

            scheme, hostname, hostport = parse_url(domain.accessUrl)
            kwargs = {
                'hostname': hostname,
                'hostport': hostport,
                'scheme': scheme,
                'description': domain.description
            }
            kwargs.update(domain.properties)

            # For now we load a jinja template that will create the session create
            # json. I am open to other suggestions
            template_file = session_create_params[domain.domainType]['template']
            properties = self.env.get_template(template_file).render(**kwargs)
            # convert unicode to utf-8 to fix simplejson not loading the properties
            # correctly
            if isinstance(properties, unicode):
                properties = properties.encode('utf-8')
            properties = json.loads(properties)

            yield session_access.preCreate(properties, None)
            session = session_access.doCreate(properties, None, root.sessions)
            yield session_access.postCreate(session, None)

            t = 0
            while session.connectState in ['CONNECTING', 'SYNCHRONIZING']:
                yield deferLater(reactor, 0.5, lambda: None)
                t += 0.5
                if t > 30:
                    break

            self.domains[domain.id] = session
            log.info('Session %s created for domain %s', session.id, domain.id)
        defer.returnValue(self.domains[domain.id])

    def get_driver_class(self, cmd_type, command):
        class_map = {
            'device': {
                'cud': RasdkDeviceCudDriver,
                'get': RasdkDeviceGetDriver,
                'list': RasdkDeviceListDriver
            },
            'bpprov': {
                'cud': RasdkBpprovCudDriver,
                'get': RasdkBpprovGetDriver,
                'list': RasdkBpprovListDriver
            }
        }
        return class_map[cmd_type][command]

    def make_driver(self, domain, command, command_info, device_id=None, resource=None):
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
                                    device_namespace_props=command_info.get('device_namespace_props'),
                                    label_field=command_info.get('label_field'),
                                    device_id_field=command_info.get('device_id_field', None),
                                    is_domain_manager=self.ra_settings.NETWORK_MANAGER_RP)
            elif driver_cls == RasdkBpprovListDriver:
                # LIST Drivers
                driver = driver_cls(domain.tenantId,
                                    command_info['product'],
                                    rpc_commands,
                                    command_info['provider_resource_id_field'],
                                    device_namespace_props=command_info.get('device_namespace_props'),
                                    label_field=command_info.get('label_field'),
                                    device_id_field=command_info.get('device_id_field', None),
                                    is_domain_manager=self.ra_settings.NETWORK_MANAGER_RP)
            else:
                raise ValueError('The driver class {} requries a device id'.format(driver_cls.__name__))
        elif command_info['type'] == 'device':
            if driver_cls == RasdkDeviceGetDriver:
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

    @defer.inlineCallbacks
    def get_resource_cud_driver(self, domain, resource):
        if self.ra_settings.NETWORK_MANAGER_RP:
            session = yield self.get_session(domain)
            device_id = session.id
        else:
            if resource.providerResourceId:
                device_id, _, _ = resource.providerResourceId.partition('::')
            else:
                # This means all RAs will require the device field when creating a resource
                device_id = resource.properties.get('device')

        command_file = self.commands[resource.productId]
        commands = self.get_file(command_file)

        defer.returnValue(self.make_driver(domain, 'cud', commands, device_id=device_id))

    @defer.inlineCallbacks
    def get_resource_get_driver(self, domain, provider_resource_id):

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

        if self.ra_settings.NETWORK_MANAGER_RP:
            session = yield self.get_session(domain)
            device_id = session.id
        else:
            device_id, _, _ = provider_resource_id.partition('::')

        #device_id = resource.properties["device"]

        # TODO: Is this OK? Need to check if the device is not active
        #device_resource = yield self.get_device_and_check_active(domain, device_id)

        command_file = self.commands[product.providerProductId]
        commands = self.get_file(command_file)

        driver =  self.make_driver(domain, 'get', commands, device_id=device_id, resource=resource)
        defer.returnValue(driver)

    @defer.inlineCallbacks
    def get_resource_list_driver(self, domain, resource_type_uri):

        resource_map = {r['resource_type']: r['provider_product_id'] for r in self.resources}

        command_file = self.commands[resource_map[resource_type_uri]]
        commands = self.get_file(command_file)

        # If the session is None the driver will list resources from all sessions
        session = None
        if self.ra_settings.NETWORK_MANAGER_RP:
            session = yield self.get_session(domain)

        # List is a special case because it is the only driver that needs to know what session/device
        # to list resources for. Get/CUD know what their session/session is since they are given a device_id
        if commands['type'] == 'bpprov':
            rpc_commands = {cmd: val['command'] for cmd, val in commands['commands'].iteritems()}
            defer.returnValue(RasdkBpprovListDriver(domain.tenantId,
                                                 commands['product'],
                                                 rpc_commands,
                                                 commands['provider_resource_id_field'],
                                                 device_namespace_props=commands.get('device_namespace_props'),
                                                 label_field=commands.get('label_field'),
                                                 session=session,
                                                 device_id_field=commands.get('device_id_field', None),
                                                 is_domain_manager=self.ra_settings.NETWORK_MANAGER_RP))
        else:
            defer.returnValue(RasdkDeviceListDriver(domain.tenantId,
                                                    commands['product'],
                                                    session=session))