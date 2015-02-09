#!/usr/bin/env python
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

# see http://confluence.cyanoptics.com/pages/viewpage.action?pageId=561069
# for details on application hooks

import os


def main():
    print 'Hook name:', os.environ['BP_HOOK_NAME']
    print 'Unit ID:', os.environ['BP_HOOK_UNIT']
    print 'Process name:', os.environ.get('BP_HOOK_PROCESS', None)
    print 'Instance ID:', os.environ.get('BP_HOOK_INSTANCE', None)
    print 'Group member:', os.environ.get('BP_HOOK_MEMBER', None)

if __name__ == '__main__':
    main()
