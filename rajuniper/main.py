#!/usr/bin/env python
# Copyright(c) 2016, Ciena All rights reserved.

import os
from rasdk.engine import run


def main():
    os.environ.setdefault('RASDK_SETTINGS_MODULE', 'rajuniper.settings')
    run()


if __name__ == '__main__':
    main()
