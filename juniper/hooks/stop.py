#!/usr/bin/env python
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

# see http://confluence.cyanoptics.com/pages/viewpage.action?pageId=561069
# for details on application hooks

import os
import subprocess


def stop():
    subprocess.call('stop juniper'.split(' '))


def main():
    print 'Hook name:', os.environ.get('BP_HOOK_NAME', None)
    print 'Unit ID:', os.environ.get('BP_HOOK_UNIT', None)
    print 'Process name:', os.environ.get('BP_HOOK_PROCESS', None)
    print 'Instance ID:', os.environ.get('BP_HOOK_INSTANCE', None)
    print 'Group member:', os.environ.get('BP_HOOK_MEMBER', None)
    stop()

if __name__ == '__main__':
    main()
