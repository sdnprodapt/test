#!/usr/bin/env python
# Copyright(c) 2014, Cyan, Inc. All rights reserved.

from easdk.utils.setuplogging import setupDaemonLogging, setupLogging

from easdk.conf import settings
settings.configure('juniper.settings')

from easdk.controller import Controller

from twisted.internet import reactor, defer

from rpsdk.highlevel import RpSdkStatelessController, RpSdkHighLevelServer, declare_rp
from rpsdk.model import RpSdkSettings, RpSdkDeploymentSettings
from rpsdk.utils.cyclonehelpers import Api
from rpsdk.onboarding import onboard_types
from juniper.rp import GenericEaDriverFactory

import argparse
import os
import sys

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
def init_rp(rp_settings, deploy_settings, market_api, assets_api):
    if deploy_settings.orchestrate.onboard_types:
        yield onboard_types(rp_settings.id,
                            rp_settings.definitions,
                            deploy_settings.identity,
                            market_api,
                            assets_api)

    yield declare_rp(market_api, rp_settings, deploy_settings)


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

def build_deploy_config():
    return {
        "orchestrate": {
            "assets_url": os.environ[ASSETS_URL_ENV],
            "market_url": os.environ[MARKET_URL_ENV],
        },
        "server": {
            "bind_address": os.environ[DOCKER_BRIDGE_IP_ENV],
            "bind_port": settings.RP_BIND_PORT,
        },
        "identity": {
            "public_key": os.path.join(os.environ["HOME"], ".ssh", "id_rsa.pub")
        }
    }

def get_deploy_settings():
    check_env()
    return RpSdkDeploymentSettings.from_data(build_deploy_config())


def main():
    parser = argparse.ArgumentParser(description='juniper main entry point')
    # parser.add_argument('--rpconfig', '-r', type=str, help='RP configuration file')
    parser.add_argument('--logfile', '-l', type=str, help='log filename for daemonlogger')
    parser.add_argument('--configpath', '-c', default=settings.DEFAULT_CONFIG_DIRPATH, type=str,
        help='main juniper config directory path')
    parser.add_argument('--verbose', '-v', default=1, action='count', help='increased verbosity')
    parser.add_argument('--port', '-p', type=int, default=settings.DEFAULT_PORT, help='http server port')
    # parser.add_argument('--deploy-settings', '-d', type=int, default=settings.DEPLOY_SETTINGS, help='http server port')

    args = parser.parse_args()

    if args.logfile:
        setupDaemonLogging(verbosity=args.verbose, logfile=args.logfile)
    else:
        setupLogging(verbosity=args.verbose)

    log.info('juniper pid %s started with %s', os.getpid(), args)

    deploy_settings = get_deploy_settings()

    market_api = get_market_api(deploy_settings.orchestrate)
    assets_api = get_assets_api(deploy_settings.orchestrate)

    rp_settings = RpSdkSettings.from_yaml_file(settings.RP_CONFIG)

    rp_controller = RpSdkStatelessController(rp_settings, deploy_settings,
                                             market_api,
                                             GenericEaDriverFactory(market_api, settings))

    rp_server = RpSdkHighLevelServer(deploy_settings.server.bind_port, rp_controller)


    ea_controller = Controller(args.port, args.configpath)

    reactor.callWhenRunning(ea_controller.start)
    reactor.callWhenRunning(rp_server.start)
    reactor.callWhenRunning(init_rp, rp_settings, deploy_settings, market_api, assets_api)
    # reactor.callWhenRunning(_declare_rp, market_api, rp_settings, deploy_settings)

    reactor.run()


if __name__ == '__main__':
    main()
