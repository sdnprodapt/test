#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

from juniper.hooks.start import main

import unittest
from mock import patch


class test_start(unittest.TestCase):

    @patch('juniper.hooks.start.subprocess.call')
    def test_start(self, subprocess):
        main()
        self.assertTrue(subprocess.called)


if __name__ == "__main__":
    unittest.main()
