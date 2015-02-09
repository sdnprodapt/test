#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

from juniper.hooks.interface.depart import main

import unittest
from mock import patch


class test_depart(unittest.TestCase):

    @patch('juniper.hooks.interface.depart.subprocess.call')
    @patch('juniper.hooks.interface.depart.sys')
    def test_depart(self, sys, subprocess):
        sys.argv = ['depart', 'mock.name', ]
        main()
        exp = 'bp-interface-depart --interface bpea.bp.cyan --to mock.name'
        subprocess.assert_called_with(exp.split(' '))


if __name__ == "__main__":
    unittest.main()
