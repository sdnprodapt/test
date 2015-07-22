#!/usr/bin/env python
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

import os
from easdk import default_settings

DEFAULT_CONFIG_DIRPATH = os.path.join(os.path.dirname(__file__), 'config/dev')
DEFAULT_PORT = 8080

EA_NAME = 'juniper'

BPPROV_MODEL_DIRPATH = os.path.join(os.path.dirname(__file__), 'model')

RESOURCES_DIR = os.path.join(BPPROV_MODEL_DIRPATH, 'resources')
DEFINITIONS_DIR = os.path.join(RESOURCES_DIR, 'definitions')
RP_CONFIG = os.path.join(RESOURCES_DIR, 'rp_config.yaml')
# RP_DEPLOY_SETTINGS = os.path.join(RESOURCES_DIR, 'deploy_settings.yaml')
RP_BIND_PORT = 9191

# NETWORK_MANAGER_RP means this rp is for talking to systems that
# manage other elements, eg vCenter, openstack, SAM etc.
# If False, the RP will manage individual devices, eg Firefly, Cisco, etc.
NETWORK_MANAGER_RP = False

TYPE_GROUP = 'Juniper'

ELEMENT_TYPES = ['JuniperMX240',
                 'JuniperMX480',
                 'JuniperMX960',
                 'JuniperMX2010',
                 'JuniperPTX3000',
                 'JuniperEX4200_48T',
                 'JuniperFireflyPerimeter']

VENDOR = 'cyan'

AUTHOR = 'Cyan'

STATIC_PATHS = {
        '/images/': os.path.join(os.path.dirname(__file__), 'model/graphics/images'),
            }

ENDPOINTS = (
        'netconf'
        )

ROOT_CLS = 'juniper.schema.ea.Root'

CAPABILITIES_DOMAINS = list(default_settings.CAPABILITIES_DOMAINS) + \
    ['juniper.domain.oidoperation.OidOperationDomain']

ACCESSORS = list(default_settings.ACCESSORS) + \
    [('juniper.access.oidoperation.OidOperationAccess', {})]
