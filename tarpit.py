#!/usr/bin/env python3

import argparse
import asyncio
import random


async def handler(_reader, writer):
    try:
        while True:
            await asyncio.sleep(2)  # TODO: config
            writer.write(b'%x\r\n' % random.randrange(2**32))  # TODO: modes?
            await writer.drain() # TODO; recv() discard?
    except ConnectionResetError:
        pass  # TODO: logging


async def amain():
    server = await asyncio.start_server(handler, '0.0.0.0', 2222)  # TODO: dualstack, config
    async with server:
        await server.serve_forever()  # TODO: shutdown event

asyncio.run(amain())  # TODO: replace to python 3.5 compatible variant
