#!/usr/bin/env python
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

from easdk.utils.setuplogging import setupDaemonLogging, setupLogging

from easdk.conf import settings
settings.configure('juniper.settings')

from easdk.controller import Controller

from twisted.internet import reactor

import argparse
import os

import logging
log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
                    description='juniper main entry point')
    parser.add_argument('--logfile', '-l', type=str, help='log filename for daemonlogger')
    parser.add_argument('--configpath', '-c', default=settings.DEFAULT_CONFIG_DIRPATH, type=str,
        help='main juniper config directory path')
    parser.add_argument('--verbose', '-v', default=1, action='count', help='increased verbosity')
    parser.add_argument('--port', '-p', type=int, default=settings.DEFAULT_PORT, help='http server port')

    args = parser.parse_args()

    if args.logfile:
        setupDaemonLogging(verbosity=args.verbose, logfile=args.logfile)
    else:
        setupLogging(verbosity=args.verbose)

    log.info('juniper pid %s started with %s', os.getpid(), args)

    controller = Controller(args.port, args.configpath)
    reactor.callWhenRunning(controller.start)

    reactor.run()


if __name__ == '__main__':
    main()
