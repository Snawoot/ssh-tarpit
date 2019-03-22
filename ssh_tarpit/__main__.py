#!/usr/bin/env python3

import argparse
import asyncio
import signal
from functools import partial

from .server import TarpitServer
from .constants import LogLevel
from .utils import setup_logger, enable_uvloop


def parse_args():

    def check_port(value):
        ivalue = int(value)
        if not 0 < ivalue < 65536:
            raise argparse.ArgumentTypeError(
                "%s is not a valid port number" % value)
        return ivalue

    parser = argparse.ArgumentParser(
        description="SSH tarpit that slowly sends and endless banner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--disable-uvloop",
                        help="do not use uvloop even if it is available",
                        action="store_true")
    parser.add_argument("-v", "--verbosity",
                        help="logging verbosity",
                        type=LogLevel.__getitem__,
                        choices=list(LogLevel),
                        default=LogLevel.info)

    listen_group = parser.add_argument_group('listen options')
    listen_group.add_argument("-a", "--bind-address",
                              default="127.0.0.1",
                              help="bind address")
    listen_group.add_argument("-p", "--bind-port",
                              default=2222,
                              type=check_port,
                              help="bind port")
    listen_group.add_argument("-D", "--dualstack",
                              action="store_true",
                              help="force dualstack socket mode. Sets socket "
                              "IPV6_V6ONLY option to 0")
    return parser.parse_args()


