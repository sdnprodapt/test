#!/usr/bin/env python
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

import sys
import subprocess


def depart(bp_hook_process):
    interface_name = 'bpea.bp.cyan'
    call = 'bp-interface-depart --interface {} --to {}'.format(interface_name, bp_hook_process)
    print call
    subprocess.call(call.split(' '))


def main():
    print 'interface.depart args:', str(sys.argv)
    depart(sys.argv[1])


if __name__ == '__main__':
    main()
