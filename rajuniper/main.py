#!/usr/bin/env python
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

from rasdk.utils.setuplogging import setupDaemonLogging, setupLogging

from rasdk.conf import settings
settings.configure('rajuniper.settings')

from rasdk.controller import Controller

from twisted.internet import reactor, defer

from twisted.web import client
client._HTTP11ClientFactory.noisy = False

from rpsdk.highlevel import RpSdkStatelessController, RpSdkHighLevelServer, declare_rp
from rpsdk.model import RpSdkSettings, RpSdkDeploymentSettings
from rpsdk.utils.cyclonehelpers import Api
from rpsdk.onboarding import onboard_types
from rasdk.ra import RaDriverFactory

import argparse
import os
import sys
import subprocess

import logging
log = logging.getLogger(__name__)


def get_assets_api(orchestrate_settings):
    if orchestrate_settings.auth_scheme:
        auth_data = {}
        auth_data["scheme"] = orchestrate_settings.auth_scheme
        auth_data.update(orchestrate_settings.auth_params)
    else:
        auth_data = None
    assets_api = Api(orchestrate_settings.assets_url, auth_data)
    return assets_api


def get_market_api(orchestrate_settings):
    if orchestrate_settings.auth_scheme:
        auth_data = {}
        auth_data["scheme"] = orchestrate_settings.auth_scheme
        auth_data.update(orchestrate_settings.auth_params)
    else:
        auth_data = None
    market_api = Api(orchestrate_settings.market_url, auth_data)
    return market_api


@defer.inlineCallbacks
def init_rp(rp_server, rp_settings, deploy_settings, market_api, assets_api, dev):
    if deploy_settings.orchestrate.onboard_types:
        hostname = None if dev else 'git-ssh'
        yield onboard_types(rp_settings.id,
                            rp_settings.definitions,
                            deploy_settings.identity,
                            market_api,
                            assets_api,
                            hostname=hostname,
                            ui_schema=rp_settings.ui_schema)

    yield declare_rp(market_api, rp_settings, deploy_settings)
    rp_server.start()


DOCKER_BRIDGE_IP_ENV = "DOCKER_BRIDGE_IP"
ASSETS_URL_ENV = "ASSETS_URL"
MARKET_URL_ENV = "MARKET_URL"


def check_env():
    REQUIRED_ENV_VARS = [
        DOCKER_BRIDGE_IP_ENV,
        MARKET_URL_ENV,
        ASSETS_URL_ENV,
    ]

    missing_envs = []

    print os.environ

    for env_var in REQUIRED_ENV_VARS:
        if env_var not in os.environ:
            missing_envs.append(env_var)

    if missing_envs:
        print("Missing required environment variables (see README.md): %s" % ", ".join(missing_envs))
        sys.exit(1)


def build_deploy_config(dev):
    container_ip = subprocess.check_output(['./scripts/docker-my-ip']).strip()
    log.info('Binding rp server to {}:{}'.format(container_ip, settings.RP_BIND_PORT))
    return {
        "orchestrate": {
            "assets_url": os.environ.get(ASSETS_URL_ENV) if dev else 'http://bpocore/bpocore/asset-manager/api/v1',
            "market_url": os.environ.get(MARKET_URL_ENV) if dev else 'http://bpocore/bpocore/market/api/v1',
        },
        "server": {
            "bind_address": os.environ.get(DOCKER_BRIDGE_IP_ENV) if dev else container_ip,
            "bind_port": settings.RP_BIND_PORT,
        },
        "identity": {
            "public_key": os.path.join(os.environ["HOME"], ".ssh", "id_rsa.pub")
        }
    }


def get_deploy_settings(dev):
    if dev:
        check_env()
    conf = build_deploy_config(dev)
    return RpSdkDeploymentSettings.from_data(conf)


def main():
    parser = argparse.ArgumentParser(description='rajuniper main entry point')
    parser.add_argument('--logfile', '-l', type=str, help='log filename for daemonlogger')
    parser.add_argument('--configpath', '-c', default=settings.DEFAULT_CONFIG_DIRPATH, type=str,
        help='main rajuniper config directory path')
    parser.add_argument('--verbose', '-v', default=1, action='count', help='increased verbosity')
    parser.add_argument('--port', '-p', type=int, default=settings.DEFAULT_PORT, help='http server port')
    parser.add_argument('--declare-rp', dest='declare_rp', action='store_true',
        help='Declare the adapter to bpocore and onbaord resource types')
    parser.add_argument('--dev', '-d', action='store_true',
        help='Start the adapter in dev mode. Get bpocore interfaces from env variables')

    args = parser.parse_args()

    if args.logfile:
        setupDaemonLogging(verbosity=args.verbose, logfile=args.logfile)
    else:
        setupLogging(verbosity=args.verbose)

    log.info('rajuniper pid %s started with %s', os.getpid(), args)

    if args.declare_rp:
        deploy_settings = get_deploy_settings(args.dev)

        market_api = get_market_api(deploy_settings.orchestrate)
        assets_api = get_assets_api(deploy_settings.orchestrate)

        rp_settings = RpSdkSettings.from_yaml_file(settings.RP_CONFIG)

        rp_controller = RpSdkStatelessController(rp_settings, deploy_settings,
                                             market_api,
                                             RaDriverFactory(market_api, settings))

        rp_server = RpSdkHighLevelServer(deploy_settings.server.bind_port, rp_controller)

    ra_controller = Controller(args.port, args.configpath)

    reactor.callWhenRunning(ra_controller.start)

    if args.declare_rp:
        reactor.callWhenRunning(init_rp, rp_server, rp_settings, deploy_settings, market_api, assets_api, args.dev)

    reactor.run()


if __name__ == '__main__':
    main()
