import asyncio


async def run(device_ip: str, name: str):
    while True:
        print(f"Hello {name} from {device_ip}")
        await asyncio.sleep(1)
