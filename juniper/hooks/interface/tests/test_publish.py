#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

from juniper.hooks.interface.publish import main

import unittest
from mock import patch, Mock


class test_publish(unittest.TestCase):

    @patch('juniper.hooks.interface.publish.subprocess.call')
    @patch('juniper.hooks.interface.publish.sys')
    @patch('juniper.hooks.interface.publish.netifaces')
    @patch('juniper.hooks.interface.publish.settings', Mock(DEFAULT_PORT=8080))
    def test_publish(self, netifaces, sys, subprocess):
        netifaces.ifaddresses.return_value = {netifaces.AF_INET: [{'addr': '99.99.99.99'}, ]}
        sys.argv = ['publish', 'mock.name']
        main()
        exp = [
                'bp-interface-join', '--interface', 'bpea.bp.cyan',
                '--data', '{"access_point_uri": "http://99.99.99.99:8080/api/v1"}', '--to', 'mock.name']
        subprocess.assert_called_with(exp)
        netifaces.ifaddresses.assert_call_once_with('eth0')


if __name__ == "__main__":
    unittest.main()
