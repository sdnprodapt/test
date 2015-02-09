#!/usr/bin/env python
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

# see http://confluence.cyanoptics.com/pages/viewpage.action?pageId=561069
# for details on application hooks

import os
import subprocess
from cymlrest import json


SOUTHBOUND_FP = '/tmp/southbound.json'


def read_southbound_data():
    try:
        fd = open(SOUTHBOUND_FP)
    except IOError:
        print "no existing file", SOUTHBOUND_FP
        sb_data = {}
    else:
        sb_data = json.loads(fd.read())

    return sb_data


def write_southbound_data(sb_data):
    with open(SOUTHBOUND_FP, 'w') as fd:
        fd.write(json.dumps(sb_data))


def rabbitmq(sb_data, interface, data):
    # { '0.0': {
    #     'amqp_uri': 'amqpc://guest:guest@172.16.17.239:5672',
    # ...
    # }
    sb_data['rabbitmq'] = data.values()[0]['amqp_uri']


def southbound_update():
    interface = os.environ['BP_HOOK_SOUTHBOUND_INTERFACE']
    data = json.loads(os.environ['BP_HOOK_SOUTHBOUND_DATA'])
    sb_data = read_southbound_data()
    if interface == 'rabbitmq':
        rabbitmq(sb_data, interface, data)
    write_southbound_data(sb_data)
    subprocess.call('reload juniper')


def main():
    print 'Hook name:', os.environ.get('BP_HOOK_NAME', None)
    print 'Unit ID:', os.environ.get('BP_HOOK_UNIT', None)
    print 'Process name:', os.environ.get('BP_HOOK_PROCESS', None)
    print 'Instance ID:', os.environ.get('BP_HOOK_INSTANCE', None)
    print 'Group member:', os.environ.get('BP_HOOK_MEMBER', None)
    print 'Southbound Interface:', os.environ['BP_HOOK_SOUTHBOUND_INTERFACE']
    print 'Southbound Data:', os.environ['BP_HOOK_SOUTHBOUND_DATA']
    southbound_update()

if __name__ == '__main__':
    main()
