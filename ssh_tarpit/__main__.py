#!/usr/bin/env python3

import argparse
import asyncio
import contextlib
import signal
import logging
from functools import partial

from .server import TarpitServer
from .constants import LogLevel
from .utils import (
    raw_log_handler,
    setup_logger,
    enable_uvloop,
    AsyncLoggingHandler,
    RotateHandlers,
    is_nt,
    Heartbeat,
)


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
    parser.add_argument("-f", "--logfile",
                        nargs="*",
                        help="file(s) to log to. Empty string argument "
                        "represents stderr. Flag without arguments disables "
                        "logging completely. Default is stderr only.",
                        default=[""])

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


def rotate_sig_handler(rotate_event, signum, frame):
    logger = logging.getLogger('MAIN')
    logger.debug("Received log rotation signal.")
    rotate_event.set()


class RotateEventHandler:
    def __init__(self, event, loop=None):
        self._evt = event
        self._task = None
        self._logger = logging.getLogger('MAIN')
        self._loop = loop if loop is not None else asyncio.get_event_loop()

    async def worker(self):
        def fire_rotation():
            try:
                RotateHandlers().fire()
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                self._logger.exception("Log rotation failed: %s", str(exc))
        while True:
            await self._evt.wait()
            self._logger.debug("Log rotation scheduled via thread pool.")
            await self._loop.run_in_executor(None, fire_rotation)
            self._logger.info("Log rotated.")
            self._evt.clear()

    async def __aenter__(self):
        return await self.start()

    async def start(self):
        if self._task is None:
            self._task = asyncio.ensure_future(self.worker(), loop=self._loop)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return await self.stop()

    async def stop(self):
        self._task.cancel()
        while not self._task.done():
            try:
                await self._task
            except asyncio.CancelledError:
                pass


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

    exit_event = asyncio.Event()
    rotate_event = asyncio.Event()
    async with Heartbeat(), RotateEventHandler(rotate_event):
        sig_handler = partial(exit_handler, exit_event)
        signal.signal(signal.SIGTERM, sig_handler)
        signal.signal(signal.SIGINT, sig_handler)
        if not is_nt():
            signal.signal(signal.SIGHUP, partial(rotate_sig_handler, rotate_event))
        await exit_event.wait()
        logger.debug("Eventloop interrupted. Shutting down server...")
    await server.stop()


def main():
    args = parse_args()
    with contextlib.ExitStack() as stack:
        loghandlers = [stack.enter_context(AsyncLoggingHandler(
            raw_log_handler(args.verbosity, logfile))) for logfile in args.logfile]
        if not loghandlers:
            loghandlers.append(logging.NullHandler())

        for loghandler in loghandlers:
            logger = setup_logger('MAIN', args.verbosity, loghandler)
            setup_logger(TarpitServer.__name__, args.verbosity, loghandler)

        if not args.disable_uvloop:
            res = enable_uvloop()
        else:
            res = False
        logger.info("uvloop" + ("" if res else " NOT") + " activated.")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(amain(args, loop))
        loop.close()
        logger.info("Server stopped.")


if __name__ == '__main__':
    main()
