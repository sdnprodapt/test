#!/usr/bin/env python
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

import os

DEFAULT_CONFIG_DIRPATH = os.path.join(os.path.dirname(__file__), 'config/dev')
DEFAULT_PORT = 8080

EA_NAME = 'juniper'

BPPROV_MODEL_DIRPATH = os.path.join(os.path.dirname(__file__), 'model')

TYPE_GROUP = 'Juniper'

ELEMENT_TYPES = ['JuniperMX240', 'JuniperMX480', 'JuniperMX960', 'JuniperMX2010', 'JuniperPTX3000', 'JuniperEX4200_48T', 'JuniperFireflyPerimeter']

VENDOR = 'cyan'

AUTHOR = 'Cyan'

STATIC_PATHS = {
        '/images/': os.path.join(os.path.dirname(__file__), 'model/graphics/images'),
            }

ENDPOINTS = (
        'netconf'
        )
