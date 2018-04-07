#!python3

async def my_coro(name):
    await asyncio.sleep(name * 0.1)
    print(f"Hello, {name}!")


def my_opt_coro(name):
    return 

import asyncio

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*[my_coro(d) for d in range(10, -1, -1)]))
loop.close()