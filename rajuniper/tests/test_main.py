#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

from rasdk.conf import settings

from rajuniper.main import main
from mock import patch

import unittest


class test_main(unittest.TestCase):

    def tearDown(self):
        settings._configured = False

    @patch('rajuniper.main.argparse')
    @patch('rajuniper.main.setupDaemonLogging')
    @patch('rajuniper.main.setupLogging')
    @patch('rajuniper.main.Controller')
    @patch('rajuniper.main.reactor')
    def test_main(self, reactor, Controller, sL, sDL, argparse):
        main()


if __name__ == "__main__":
    unittest.main()
