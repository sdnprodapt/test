#!/usr/bin/env python
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

from juniper import settings

from cymlrest import json

import sys
import subprocess
import netifaces


def get_interface_address(iface='eth0'):
    _if = netifaces.ifaddresses(iface)
    addr = _if[netifaces.AF_INET][0]['addr']
    return addr


def publish(bp_hook_process):
    interface_name = 'bpea.bp.cyan'
    my_ip = get_interface_address()
    my_port = settings.DEFAULT_PORT

    data = json.dumps(
        {'access_point_uri': 'http://{}:{}/api/v1'.format(my_ip, my_port)}
    )

    call = ['bp-interface-join', '--interface', interface_name,
            '--data', "{}".format(data), '--to', bp_hook_process]
    print ' '.join(call)
    subprocess.call(call)


def main():
    print 'interface.publish args:', str(sys.argv)
    publish(sys.argv[1])


if __name__ == '__main__':
    main()
