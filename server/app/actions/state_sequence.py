import asyncio

from app.services.devices_service import DeviceData, DeviceState


async def run(device: DeviceData, delay: float, states: list[DeviceState]):
    state_counter = 0
    while len(states) > 0:
        device.set_states(states[state_counter])
        state_counter = (state_counter + 1) % len(states)
        await asyncio.sleep(delay)
