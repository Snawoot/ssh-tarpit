#!/usr/bin/env python3

import argparse
import asyncio
import random

async def handler(_reader, writer):
    try:
        while True:
            await asyncio.sleep(2)
            writer.write(b'%x\r\n' % random.randrange(2**32))
            await writer.drain()
    except ConnectionResetError:
        pass

async def amain():
    server = await asyncio.start_server(handler, '0.0.0.0', 2222)
    async with server:
        await server.serve_forever()

asyncio.run(amain())
