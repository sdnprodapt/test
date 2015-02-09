#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

from juniper.hooks.southbound_update import main

from cymlrest import json

import os

import unittest
from mock import patch


class test_southbound_update(unittest.TestCase):

    @patch('juniper.hooks.southbound_update.subprocess.call')
    def test_southbound_update(self, subprocess):
        os.environ['BP_HOOK_SOUTHBOUND_INTERFACE'] = 'rabbitmq'
        os.environ['BP_HOOK_SOUTHBOUND_DATA'] = json.dumps({
                '0.0': {
                    'amqp_uri': 'amqpc://guest:guest@localhost:5672',
                    },
                })

        main()
        self.assertTrue(subprocess.called)


if __name__ == "__main__":
    unittest.main()
