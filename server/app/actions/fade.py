import asyncio
from typing import Optional

from app.services.devices_service import DeviceData, DeviceState


async def run(
    device: DeviceData,
    speed: float = 0.05,
    channels: list[str] = None,
    loop_count: Optional[int] = None,
):
    """Fade the specified channels (default: red, yellow, green) up then down repeatedly.

    Args:
        speed: Seconds between each brightness step (smaller = faster).
        channels: List of channels to fade. Defaults to ["red", "yellow", "green"].
        loop_count: Number of full fade cycles. None means loop forever.
    """
    if channels is None:
        channels = ["red", "yellow", "green"]

    cycles = 0
    while True:
        for value in (*range(0, 256, 5), *range(255, -1, -5)):
            state = DeviceState(**{channel: value for channel in channels})
            device.set_states(states=state)
            await asyncio.sleep(speed)

        if loop_count is None:
            continue

        cycles += 1
        if cycles >= loop_count:
            break

    device.set_states(states=DeviceState(**{channel: 0 for channel in channels}))
