import asyncio
from typing import Optional

from app.services.devices_service import DeviceData, DeviceState


async def run(
    device: DeviceData,
    delay: float,
    states: list[DeviceState],
    loop_count: int = None,
):
    while True:
        for state in states:
            device.set_states(states=state)
            await asyncio.sleep(delay)

        if loop_count is None:
            continue

        if loop_count > 0:
            loop_count -= 1
        else:
            break
