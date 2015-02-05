#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

from juniper.hooks.stop import main

import unittest
from mock import patch


class test_stop(unittest.TestCase):

    @patch('juniper.hooks.stop.subprocess.call')
    def test_stop(self, call):
        main()
        self.assertTrue(call.called)


if __name__ == "__main__":
    unittest.main()
