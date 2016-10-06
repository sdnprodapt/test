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
# RP_DEPLOY_SETTINGS = os.path.join(RESOURCES_DIR, 'deploy_settings.yaml')
RP_BIND_PORT = 9191

# DOMAIN_MANAGER_RP means this RA is for talking to systems that
# manage other elements, eg vCenter, openstack, SAM etc.
# If False, the RA will manage individual devices, eg Firefly, Cisco, etc.
DOMAIN_MANAGER_RP = False

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
        'snmp',
        'kafka'
        )

ROOT_CLS = 'rajuniper.schema.ra.Root'

CAPABILITIES_DOMAINS = list(default_settings.CAPABILITIES_DOMAINS) + \
    ['rajuniper.domain.oidoperation.OidOperationDomain']

# ACCESSORS = list(default_settings.ACCESSORS) + \
#    [('rajuniper.access.oidoperation.OidOperationAccess', {})]


# Playbook settings, II-tier model is used here.

# General playbook settings
PLAYBOOK_INVENTORY = 'rasdk.playbook.inventory.RasdkInventory'
PLAYBOOK_HOME = os.path.join(BPPROV_MODEL_DIRPATH, 'playbook')
PLAYBOOK_YANG_ROOT = os.path.join(PLAYBOOK_HOME, 'yang')
PLAYBOOK_YANG_PATHS = os.path.join(PLAYBOOK_YANG_ROOT, 'common')

# Master -> service
PLAYBOOK_MASTER_CONFIGDIR = os.path.join('yang', 'service')
PLAYBOOK_MASTER_WEBPORT = 5000
PLAYBOOK_MASTER_MODULES = 'cyan-l3vpn-cfg.yang'
PLAYBOOK_MASTER_NETCONF = True

PLAYBOOK_MASTER_CLI_PORT = 7100
PLAYBOOK_MASTER_CLI_PROMPT = 'rajuniper> '
PLAYBOOK_MASTER_CLI_BANNER = 'RA Netconf Service Playbook\n'

# Slave -> device
PLAYBOOK_SLAVE_CONFIGDIR = os.path.join('yang', 'device')
PLAYBOOK_SLAVE_WEBPORT = 8088
# TBD: use juniper device yang model
PLAYBOOK_SLAVE_MODULES = 'cyan_host_juniper.yang'
PLAYBOOK_SLAVE_NETCONF = True

PLAYBOOK_SLAVE_CLI_PORT = 7001
PLAYBOOK_SLAVE_CLI_PROMPT = 'rajuniper-device> '
PLAYBOOK_SLAVE_CLI_BANNER = 'RA Netconf Device Playbook\n'
