import asyncio

from app.services.devices_service import DeviceData


async def run(device: DeviceData, name: str):
    while True:
        print(f"Hello {name} from {device.ip}")
        await asyncio.sleep(1)
