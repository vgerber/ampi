import asyncio


async def run(name: str):
    while True:
        print(f"Hello {name}")
        await asyncio.sleep(1)
