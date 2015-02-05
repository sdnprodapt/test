#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

from easdk.conf import settings

from juniper.main import main
from mock import patch

import unittest


class test_main(unittest.TestCase):

    def tearDown(self):
        settings._configured = False

    @patch('juniper.main.argparse')
    @patch('juniper.main.setupDaemonLogging')
    @patch('juniper.main.setupLogging')
    @patch('juniper.main.Controller')
    @patch('juniper.main.reactor')
    def test_main(self, reactor, Controller, sL, sDL, argparse):
        main()


if __name__ == "__main__":
    unittest.main()
