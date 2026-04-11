import asyncio
from typing import Optional

from app.services.devices_service import DeviceData, DeviceState

WAYPOINTS = [
    (0.00, 0, 0, 255),  # green
    (0.25, 0, 255, 0),  # yellow
    (0.50, 255, 0, 0),  # red
    (0.75, 0, 255, 0),  # yellow
    (1.00, 0, 0, 255),  # green
]


def interpolate(progress: float) -> tuple[int, int, int]:
    for i in range(len(WAYPOINTS) - 1):
        t0, r0, y0, g0 = WAYPOINTS[i]
        t1, r1, y1, g1 = WAYPOINTS[i + 1]
        if t0 <= progress <= t1:
            factor = (progress - t0) / (t1 - t0)
            return (
                round(r0 + (r1 - r0) * factor),
                round(y0 + (y1 - y0) * factor),
                round(g0 + (g1 - g0) * factor),
            )
    return WAYPOINTS[-1][1], WAYPOINTS[-1][2], WAYPOINTS[-1][3]


async def run(
    device: DeviceData,
    speed: float = 0.05,
    steps: int = 100,
    loop_count: Optional[int] = None,
):
    """Fade through traffic light colors using interpolation.

    Args:
        speed: Seconds between each step.
        steps: Number of interpolation steps per full cycle (higher = smoother).
        loop_count: Number of full cycles. None means loop forever.
    """
    cycles = 0
    while True:
        for step in range(steps):
            progress = step / steps
            red, yellow, green = interpolate(progress)
            device.set_states(states=DeviceState(red=red, yellow=yellow, green=green))
            await asyncio.sleep(speed)

        if loop_count is None:
            continue

        cycles += 1
        if cycles >= loop_count:
            break

    device.set_states(states=DeviceState(red=0, yellow=0, green=0))
