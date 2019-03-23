import asyncio
import socket
import weakref
import random
import logging

class TarpitServer:
    SHUTDOWN_TIMEOUT = 5

    def __init__(self, *,
                 address,
                 port,
                 dualstack=False,
                 interval=2.,
                 loop=None):
        self._loop = loop if loop is not None else asyncio.get_event_loop()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._address = address
        self._port = port
        self._dualstack = dualstack
        self._interval = interval
        self._children = weakref.WeakSet()

    async def stop(self):
        self._server.close()
        await self._server.wait_closed()
        if self._children:
            self._logger.debug("Cancelling %d client handlers...",
                               len(self._children))
            for task in self._children:
                task.cancel()
            await asyncio.wait(self._children)

    async def handler(self, reader, writer):
        writer.transport.pause_reading()
        sock = writer.transport.get_extra_info('socket')
        if sock is not None:
            sock.shutdown(socket.SHUT_RD)
        peer_addr = writer.transport.get_extra_info('peername')
        self._logger.info("Client %s connected", str(peer_addr))
        try:
            while True:
                await asyncio.sleep(self._interval)
                writer.write(b'%.8x\r\n' % random.randrange(2**32))
                await writer.drain()
        except (ConnectionResetError, RuntimeError):
            self._logger.info("Client %s disconnected", str(peer_addr))

    async def start(self):
        def _spawn(reader, writer):
            self._children.add(
                self._loop.create_task(self.handler(reader, writer)))

        if self._dualstack:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            sock.bind((self._address, self._port))
            self._server = await asyncio.start_server(_spawn, sock=sock)
        else:
            self._server = await asyncio.start_server(_spawn,
                                                      self._address,
                                                      self._port)
        self._logger.info("Server ready.")
