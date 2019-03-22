import asyncio
import random
import logging

class TarpitServer:
    SHUTDOWN_TIMEOUT = 5

    def __init__(self, *, address=None, port=2222, dualstack=False, loop=None):
        self._loop = loop if loop is not None else asyncio.get_event_loop()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._address = address
        self._port = port
        self._dualstack = dualstack
        #self._int_fut = self._loop.create_future()
        #self._shutdown = asyncio.ensure_future(self._int_fut, loop=self._loop)

    async def stop(self):
        try:
            self._run.cancel()
        except asyncio.InvalidStateError:
            pass
        else:
            self._server.close()
            await self._server.wait_closed()

    async def run(self):
        await self._run

#    async def _guarded_run(self, awaitable):
#        task = asyncio.ensure_future(awaitable)
#        try:
#            _, pending = await asyncio.wait((self._shutdown, task),
#                                            return_when=asyncio.FIRST_COMPLETED)
#        except asyncio.CancelledError:
#            task.cancel()
#            raise
#        if task in pending:
#            task.cancel()
#            return None
#        else:
#            return task.result()
#
    async def handler(self, _reader, writer):
        try:
            while not self._run.done():
                await asyncio.sleep(2)  # TODO: config
                writer.write(b'%x\r\n' % random.randrange(2**32))  # TODO: modes?
                await writer.drain() # TODO; recv() discard?
        except ConnectionResetError:
            pass  # TODO: logging

    async def start(self):
        self._server = await asyncio.start_server(self.handler,
                                                  self._address,
                                                  self._port)  # TODO: dualstack
        self._run = asyncio.ensure_future(self._server.serve_forever())
        self._logger.info("Server ready.")
