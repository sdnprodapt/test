#!/usr/bin/env python
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

import os
from rasdk import default_settings

DEFAULT_CONFIG_DIRPATH = os.path.join(os.path.dirname(__file__), 'config/dev')
DEFAULT_PORT = 8080

RA_NAME = 'rajuniper'

BPPROV_MODEL_DIRPATH = os.path.join(os.path.dirname(__file__), 'model')

RESOURCES_DIR = os.path.join(BPPROV_MODEL_DIRPATH, 'resources')
DEFINITIONS_DIR = os.path.join(RESOURCES_DIR, 'definitions')
RP_CONFIG = os.path.join(RESOURCES_DIR, 'rp_config.yaml')
RP_BIND_PORT = 9192

# DOMAIN_MANAGER_RP means this RA is for talking to systems that
# manage other elements, eg vCenter, openstack, SAM etc.
# If False, the RA will manage individual devices, eg Firefly, Cisco, etc.
DOMAIN_MANAGER_RP = False

USE_KAFKA = True

TYPE_GROUP = 'Juniper'

RESOURCE_TYPES = ['JuniperMX240',
                 'JuniperMX480',
                 'JuniperMX960',
                 'JuniperMX2010',
                 'JuniperPTX3000',
                 'JuniperEX4200_48T',
                 'JuniperQFX5100-48S-6Q',
                 'JuniperFireflyPerimeter']

VENDOR = 'cyan'

AUTHOR = 'Cyan'

STATIC_PATHS = {
        '/images/': os.path.join(os.path.dirname(__file__), 'model/graphics/images'),
            }

ENDPOINTS = (
        'netconf',
        'kafka'
        )

ROOT_CLS = 'rajuniper.schema.ra.Root'

CAPABILITIES_DOMAINS = list(default_settings.CAPABILITIES_DOMAINS) + \
    ['rajuniper.domain.oidoperation.OidOperationDomain']
