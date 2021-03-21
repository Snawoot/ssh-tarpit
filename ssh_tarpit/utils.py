import asyncio
import logging
import logging.handlers
import os
import queue


class Heartbeat:
    def __init__(self, interval=.5):
        self._interval = interval
        self._beat = None

    async def heartbeat(self):
        while True:
            await asyncio.sleep(self._interval)

    async def __aenter__(self):
        return await self.start()

    async def start(self):
        if self._beat is None:
            self._beat = asyncio.ensure_future(self.heartbeat())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return await self.stop()

    async def stop(self):
        self._beat.cancel()
        while not self._beat.done():
            try:
                await self._beat
            except asyncio.CancelledError:
                pass


def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class RotateHandlers:
    def __init__(self):
        self._callbacks = []

    def add_callback(self, cb):
        self._callbacks.append(cb)

    def fire(self):
        for cb in self._callbacks:
            cb()


class OverflowingQueue(queue.Queue):
    def put(self, item, block=True, timeout=None):
        try:
            return queue.Queue.put(self, item, block, timeout)
        except queue.Full:
            # Log sink hang
            pass
        return None

    def put_nowait(self, item):
        return self.put(item, False)


class AsyncLoggingHandler:
    def __init__(self, handler, maxsize=1024):
        _queue = OverflowingQueue(maxsize)
        self._listener = logging.handlers.QueueListener(_queue, handler)
        self._async_handler = logging.handlers.QueueHandler(_queue)

    def __enter__(self):
        self._listener.start()
        return self._async_handler

    def __exit__(self, exc_type, exc_value, traceback):
        self._listener.stop()


def raw_log_handler(verbosity, logfile=None):
    if logfile:
        if is_nt():
            handler = logging.FileHandler(logfile)
        else:
            handler = logging.handlers.WatchedFileHandler(logfile)
            def rotate_cb():
                try:
                    handler.reopenIfNeeded()
                except:
                    pass
            RotateHandlers().add_callback(rotate_cb)
    else:
        handler = logging.StreamHandler()
    handler.setLevel(verbosity)
    handler.setFormatter(logging.Formatter('%(asctime)s '
                                           '%(levelname)-8s '
                                           '%(name)s: %(message)s',
                                           '%Y-%m-%d %H:%M:%S'))
    return handler


def setup_logger(name, verbosity, handler):
    logger = logging.getLogger(name)
    logger.setLevel(verbosity)
    logger.addHandler(handler)
    return logger


def enable_uvloop():
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        return False
    else:
        return True

def is_nt():
    return os.name == 'nt'
