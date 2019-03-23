import asyncio
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
            for task in self._children:
                task.cancel()
            await asyncio.wait(self._children)

    async def handler(self, _reader, writer):
        try:
            while True:
                await asyncio.sleep(self._interval)
                writer.write(b'%x\r\n' % random.randrange(2**32))  # TODO: modes?
                await writer.drain() # TODO; recv() discard?
        except ConnectionResetError:
            pass  # TODO: logging

    async def start(self):
        def _spawn(reader, writer):
            self._children.add(
                self._loop.create_task(self.handler(reader, writer)))

        self._server = await asyncio.start_server(_spawn,
                                                  self._address,
                                                  self._port)  # TODO: dualstack
        self._run = asyncio.ensure_future(self._server.serve_forever())
        self._logger.info("Server ready.")
