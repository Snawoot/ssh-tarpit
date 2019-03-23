#!/usr/bin/env python3

import argparse
import asyncio
import signal
import logging
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

    def check_positive_float(value):
        fvalue = float(value)
        if fvalue <= 0:
            raise argparse.ArgumentTypeError(
                "%s is not a valid positive float" % value)
        return fvalue

    parser = argparse.ArgumentParser(
        description="SSH tarpit that slowly sends an endless banner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--disable-uvloop",
                        help="do not use uvloop even if it is available",
                        action="store_true")
    parser.add_argument("-v", "--verbosity",
                        help="logging verbosity",
                        type=LogLevel.__getitem__,
                        choices=list(LogLevel),
                        default=LogLevel.info)
    parser.add_argument("-i", "--interval",
                        help="interval between writes in seconds",
                        type=check_positive_float,
                        default=2.)

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


def exit_handler(exit_event, signum, frame):
    logger = logging.getLogger('MAIN')
    if exit_event.is_set():
        logger.warning("Got second exit signal! Terminating hard.")
        os._exit(1)
    else:
        logger.warning("Got first exit signal! Terminating gracefully.")
        exit_event.set()


async def heartbeat():
    while True:
        await asyncio.sleep(.5)


async def amain(args, loop):
    logger = logging.getLogger('MAIN')
    server = TarpitServer(address=args.bind_address,
                          port=args.bind_port,
                          dualstack=args.dualstack,
                          interval=args.interval,
                          loop=loop)
    logger.debug("Starting server...")
    await server.start()
    logger.info("Server startup completed.")

    exit_event = asyncio.Event(loop=loop)
    beat = asyncio.ensure_future(heartbeat(), loop=loop)
    sig_handler = partial(exit_handler, exit_event)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    await exit_event.wait()
    logger.debug("Eventloop interrupted. Shutting down server...")
    beat.cancel()
    await server.stop()


def main():
    args = parse_args()
    logger = setup_logger('MAIN', args.verbosity)
    setup_logger(TarpitServer.__name__, args.verbosity)

    if not args.disable_uvloop:
        res = enable_uvloop()
        logger.debug("uvloop" + ("" if res else " NOT") + " activated.")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(amain(args, loop))
    loop.close()
    logger.info("Server stopped.")


if __name__ == '__main__':
    main()
